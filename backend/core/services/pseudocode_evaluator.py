"""
의사코드 평가 엔진 - Refactored
수정일: 2026-02-19

[변경 사항]
- Rule은 "감점 게이트" 역할, LLM이 실질 점수 담당 (역할 분리)
- 점수 기준 상수화 (SCORE_CONFIG) - 프롬프트 모순 제거
- 키워드 가점 로직 제거
- LowEffortDetector 단일 진입점으로 통합
- 에러 타입별 커스텀 예외 도입
"""

import os
import json
import time
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    import openai
except ImportError:
    openai = None

from django.conf import settings
from core.utils.pseudocode_validator import PseudocodeValidator
from core.utils.mission_rules import VALIDATION_RULES
from core.utils.low_effort_detector import LowEffortDetector

logger = logging.getLogger(__name__)


# ============================================================================
# 0. 점수 기준 상수 (프롬프트와 코드가 이 값을 공유)
# ============================================================================

SCORE_CONFIG = {
    'max_score': 100,
    'pass_threshold': 70,        # 70점 이상 = 통과
    'deep_dive_threshold': 80,   # 80점 이상 = 심화 질문
    'rule_penalty_per_error': 10,  # 치명적 오류 1개당 감점
    'rule_max_penalty': 40,        # 최대 감점 한도
    'dimension_weights': {
        'design': 25,
        'consistency': 25,   # data leakage 핵심 차원
        'edge_case': 20,
        'abstraction': 15,
        'implementation': 15,
    }
}


# ============================================================================
# 1. 커스텀 예외
# ============================================================================

class LowEffortError(Exception):
    """무성의 입력 감지"""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


class LLMTimeoutError(Exception):
    """LLM API 타임아웃"""
    pass


class LLMUnavailableError(Exception):
    """LLM API 사용 불가 (키 없음, 라이브러리 없음 등)"""
    pass


# ============================================================================
# 2. 평가 모드
# ============================================================================

class EvaluationMode(Enum):
    OPTION2_GPTONLY = "option2_gptonly"


class ModelConfig:
    PRIMARY_MODEL = "gpt-4o-mini"


# ============================================================================
# 3. 데이터 클래스
# ============================================================================

@dataclass
class EvaluationRequest:
    user_id: str
    detail_id: str
    pseudocode: str
    mode: EvaluationMode = EvaluationMode.OPTION2_GPTONLY
    quest_title: str = "알 수 없는 미션"

    def __post_init__(self):
        if isinstance(self.mode, str):
            try:
                self.mode = EvaluationMode(self.mode)
            except ValueError:
                self.mode = EvaluationMode.OPTION2_GPTONLY


@dataclass
class RuleValidationResult:
    """Rule 기반 검증 결과 (감점 게이트 역할)"""
    passed: bool
    critical_error_count: int
    warnings: List[str]
    processing_time_ms: int
    details: Dict[str, Any]
    raw_score_100: int = 0   # 참고용 (실제 최종 점수에 직접 사용 안 함)


@dataclass
class LLMEvaluationResult:
    model: str
    status: str  # SUCCESS | ERROR | TIMEOUT
    raw_score: Optional[int] = None
    dimension_scores: Optional[Dict[str, float]] = None
    feedback: Optional[Dict[str, Any]] = None
    converted_python: Optional[str] = None
    python_feedback: Optional[str] = None
    tail_question: Optional[Dict[str, Any]] = None
    deep_dive: Optional[Dict[str, Any]] = None
    senior_advice: Optional[str] = None
    error_message: Optional[str] = None
    latency_ms: int = 0


@dataclass
class FinalEvaluationResult:
    user_id: str
    detail_id: str
    final_score: int
    grade: str
    persona: str
    feedback: Dict[str, Any]
    is_low_effort: bool
    tail_question: Optional[Dict[str, Any]]
    deep_dive: Optional[Dict[str, Any]]
    score_breakdown: Dict[str, Any]
    metadata: Dict[str, Any]
    rule_validation: Optional[RuleValidationResult] = None
    llm_result: Optional[LLMEvaluationResult] = None


# ============================================================================
# 4. Rule 기반 검증 (감점 게이트)
# ============================================================================

class RuleValidationEngine:
    """
    Rule 기반 검증.
    역할: 치명적 오류 감지 → LLM 점수 감점 여부 결정.
    최종 점수를 직접 산출하지 않음.
    """

    def validate(self, pseudocode: str, quest_id: str = "1") -> RuleValidationResult:
        start = time.time()
        try:
            rules = VALIDATION_RULES.get(str(quest_id), VALIDATION_RULES.get("1"))
            validator = PseudocodeValidator(rules)
            result = validator.validate(pseudocode)

            elapsed = int((time.time() - start) * 1000)

            # criticalErrors 개수 추출
            critical_errors = result.get('criticalErrors', [])
            # 심각도가 CRITICAL인 것만 카운트
            critical_count = sum(
                1 for e in critical_errors
                if isinstance(e, dict) and e.get('severity', 'CRITICAL') == 'CRITICAL'
            )

            return RuleValidationResult(
                passed=result.get('passed', False),
                critical_error_count=critical_count,
                warnings=result.get('warnings', []),
                processing_time_ms=elapsed,
                details=result,
                raw_score_100=result.get('score', 0),
            )
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            logger.warning(f"[RuleValidation] 검증 중 예외 발생: {e}")
            return RuleValidationResult(
                passed=False,
                critical_error_count=0,
                warnings=[f"로컬 검증 실패: {str(e)}"],
                processing_time_ms=elapsed,
                details={"error": str(e)},
            )


# ============================================================================
# 5. LLM 평가 엔진
# ============================================================================

class LLMEvaluationEngine:

    def __init__(self):
        if openai and getattr(settings, 'OPENAI_API_KEY', None):
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None

    def evaluate(
        self,
        pseudocode: str,
        rule_result: RuleValidationResult,
        quest_title: str,
        model: str = ModelConfig.PRIMARY_MODEL,
        timeout: int = 35,
    ) -> LLMEvaluationResult:

        if not self.client:
            raise LLMUnavailableError("OpenAI 클라이언트를 초기화할 수 없습니다. API 키를 확인해 주세요.")

        start = time.time()
        try:
            system_prompt, user_prompt = self._build_prompts(pseudocode, rule_result, quest_title)
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                timeout=timeout,
            )
            raw_text = response.choices[0].message.content
            parsed = self._safe_parse(raw_text)
            latency = int((time.time() - start) * 1000)

            return LLMEvaluationResult(
                model=model,
                status="SUCCESS",
                raw_score=parsed.get("overall_score"),
                dimension_scores=parsed.get("dimension_scores", {}),
                feedback=parsed.get("feedback", {}),
                converted_python=parsed.get("converted_python", ""),
                python_feedback=parsed.get("python_feedback", ""),
                tail_question=parsed.get("tail_question"),
                deep_dive=parsed.get("deep_dive"),
                senior_advice=parsed.get("senior_advice", ""),
                latency_ms=latency,
            )

        except Exception as e:
            latency = int((time.time() - start) * 1000)
            err_str = str(e)
            if "timeout" in err_str.lower() or "timed out" in err_str.lower():
                raise LLMTimeoutError(f"LLM 응답 시간 초과 ({timeout}s)") from e
            logger.error(f"[LLMEvaluation] 호출 실패: {e}", exc_info=True)
            return LLMEvaluationResult(
                model=model,
                status="ERROR",
                error_message=err_str,
                latency_ms=latency,
            )

    def _build_prompts(
        self,
        pseudocode: str,
        rule_result: RuleValidationResult,
        quest_title: str,
    ) -> Tuple[str, str]:
        weights = SCORE_CONFIG['dimension_weights']
        pass_t = SCORE_CONFIG['pass_threshold']
        deep_t = SCORE_CONFIG['deep_dive_threshold']

        system = f"""당신은 전설적인 아키텍트 'Coduck Wizard'입니다.
사용자의 의사코드를 5차원으로 평가하고 Python 코드로 변환하십시오.

[채점 기준 - 총합 100점]
- design (설계력): {weights['design']}점 만점
- consistency (정합성): {weights['consistency']}점 만점  ← 데이터 누수(Data Leakage) 엄격 진단
- edge_case (예외처리): {weights['edge_case']}점 만점
- abstraction (추상화): {weights['abstraction']}점 만점
- implementation (구현력): {weights['implementation']}점 만점

overall_score = 5개 차원 점수의 합계 (0~100점)

[꼬리 질문 / 심화 시나리오 기준]
- overall_score < {pass_t}: 학생이 부족한 부분을 인지하게 하는 꼬리 질문 제공
- overall_score >= {deep_t}: 심화 시나리오(deep_dive)만 제공, 꼬리 질문 생략

응답은 반드시 JSON 형식으로만 제공합니다."""

        rule_summary = f"통과={rule_result.passed}, 치명적오류={rule_result.critical_error_count}건, 경고={rule_result.warnings}"

        user = f"""미션: {quest_title}
의사코드:
---
{pseudocode}
---
Rule 검증 결과 (참고용): {rule_summary}

요청:
1. 차원별 평가 (각 차원 만점 기준으로 직접 점수 산출)
2. 의사코드를 수준 높은 Python 코드(converted_python)로 변환
3. overall_score < {pass_t} 이면 꼬리 질문(tail_question) 생성 (4지 선다형)
4. overall_score >= {deep_t} 이면 심화 챌린지(deep_dive) 생성

출력 JSON 구조:
{{
    "overall_score": 0,
    "dimension_scores": {{
        "design": 0,
        "consistency": 0,
        "edge_case": 0,
        "abstraction": 0,
        "implementation": 0
    }},
    "feedback": {{ "strengths": [], "improvements": [] }},
    "tail_question": {{
        "question": "...",
        "options": [
            {{"text": "...", "is_correct": true, "feedback": "..."}},
            {{"text": "...", "is_correct": false, "feedback": "..."}},
            {{"text": "...", "is_correct": false, "feedback": "..."}},
            {{"text": "...", "is_correct": false, "feedback": "..."}}
        ]
    }},
    "deep_dive": {{
        "title": "...",
        "scenario": "...",
        "question": "...",
        "model_answer": "..."
    }},
    "converted_python": "...",
    "python_feedback": "...",
    "senior_advice": "..."
}}
"""
        return system, user

    def _safe_parse(self, text: str) -> Dict[str, Any]:
        try:
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass
        return {}


# ============================================================================
# 6. 점수 계산 (Rule = 감점 게이트, LLM = 실질 점수)
# ============================================================================

class ScoringEngine:

    def calculate(
        self,
        llm_score_100: int,
        rule_result: RuleValidationResult,
    ) -> Dict[str, Any]:
        """
        Rule은 "통과/실패 게이트".
        - Rule 통과 → LLM 점수 그대로 사용
        - Rule 실패 → 치명적 오류 1개당 penalty 감점
        """
        penalty = 0
        if not rule_result.passed:
            penalty = min(
                SCORE_CONFIG['rule_max_penalty'],
                rule_result.critical_error_count * SCORE_CONFIG['rule_penalty_per_error'],
            )

        final = max(0, min(100, llm_score_100 - penalty))

        if final >= 80:
            grade = 'EXCELLENT'
        elif final >= 65:
            grade = 'GOOD'
        elif final >= 45:
            grade = 'AVERAGE'
        else:
            grade = 'POOR'

        return {
            'final_score': final,
            'llm_raw_score': llm_score_100,
            'rule_penalty': penalty,
            'rule_passed': rule_result.passed,
            'grade': grade,
        }


# ============================================================================
# 7. 피드백 및 페르소나 생성
# ============================================================================

class FeedbackEngine:

    def generate(
        self,
        llm_result: LLMEvaluationResult,
        scoring: Dict[str, Any],
    ) -> Dict[str, Any]:
        score = scoring['final_score']
        grade = scoring['grade']
        weights = SCORE_CONFIG['dimension_weights']

        # 차원별 점수 정규화 (만점 기준 실제 점수)
        raw_dims = llm_result.dimension_scores or {}
        dimensions = {}
        for dim, max_val in weights.items():
            raw = raw_dims.get(dim, 0)
            try:
                val = float(raw.get('score', 0) if isinstance(raw, dict) else raw)
            except (TypeError, ValueError):
                val = 0.0
            dimensions[dim] = {
                'score': round(min(val, max_val), 1),
                'max': max_val,
            }

        # 페르소나
        if score >= 80:
            persona = "철옹성 설계자"
            summary = f"{grade} 등급 — 완성도 높은 설계입니다."
        elif score >= 65:
            persona = "원칙 중심의 이론가"
            summary = f"{grade} 등급 — 우수한 설계입니다."
        elif score >= 45:
            persona = "성장하는 아키텍트"
            summary = f"{grade} 등급 — 핵심 개념을 보완해 보세요."
        else:
            persona = "견습 아키텍트"
            summary = f"{grade} 등급 — 기초 원칙부터 다시 검토해 주세요."

        llm_feedback = llm_result.feedback or {}

        return {
            'summary': summary,
            'persona': persona,
            'dimensions': dimensions,
            'strengths': llm_feedback.get('strengths', []),
            'improvements': llm_feedback.get('improvements', []),
            'senior_advice': llm_result.senior_advice or summary,
        }


# ============================================================================
# 8. 메인 오케스트레이터
# ============================================================================

class PseudocodeEvaluator:

    def __init__(self):
        self.rule_engine = RuleValidationEngine()
        self.llm_engine = LLMEvaluationEngine()
        self.scoring_engine = ScoringEngine()
        self.feedback_engine = FeedbackEngine()

    def evaluate(self, request: EvaluationRequest) -> FinalEvaluationResult:
        """
        평가 파이프라인:
        1. Low Effort 감지 → LowEffortError raise
        2. Rule 검증 (감점 게이트)
        3. LLM 평가 (실질 점수)
        4. 점수 계산 (Rule 페널티 적용)
        5. 피드백 생성
        """
        # ── Step 1: Low Effort 감지 ────────────────────────────────
        is_low, reason = LowEffortDetector.check(request.pseudocode)
        if is_low:
            raise LowEffortError(reason or "입력이 부실합니다.")

        # ── Step 2: Rule 검증 ──────────────────────────────────────
        rule_result = self.rule_engine.validate(request.pseudocode, request.detail_id)

        # ── Step 3: LLM 평가 ──────────────────────────────────────
        # LLMTimeoutError / LLMUnavailableError 는 뷰 레이어로 전파
        llm_result = self.llm_engine.evaluate(
            pseudocode=request.pseudocode,
            rule_result=rule_result,
            quest_title=request.quest_title,
        )

        # LLM 자체가 ERROR 상태라면 rule 점수 기반으로 fallback
        if llm_result.status != "SUCCESS" or llm_result.raw_score is None:
            llm_score = rule_result.raw_score_100  # rule 점수를 llm 점수 대신 사용
        else:
            llm_score = max(0, min(100, int(llm_result.raw_score)))

        # ── Step 4: 점수 계산 ─────────────────────────────────────
        scoring = self.scoring_engine.calculate(llm_score, rule_result)

        # ── Step 5: 피드백 생성 ───────────────────────────────────
        feedback = self.feedback_engine.generate(llm_result, scoring)

        return FinalEvaluationResult(
            user_id=request.user_id,
            detail_id=request.detail_id,
            final_score=scoring['final_score'],
            grade=scoring['grade'],
            persona=feedback['persona'],
            feedback=feedback,
            is_low_effort=False,
            tail_question=llm_result.tail_question,
            deep_dive=llm_result.deep_dive,
            score_breakdown=scoring,
            metadata={
                'latency_ms': llm_result.latency_ms,
                'model': llm_result.model,
                'llm_status': llm_result.status,
                'rule_passed': rule_result.passed,
                'rule_critical_errors': rule_result.critical_error_count,
            },
            rule_validation=rule_result,
            llm_result=llm_result,
        )
