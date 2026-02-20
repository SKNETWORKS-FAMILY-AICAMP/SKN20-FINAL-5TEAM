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
from core.services.quest_rubrics import get_rubric_for_prompt, extract_quest_id_from_title
from core.services.quest_resources import (
    validate_tail_question,
    validate_deep_dive,
    generate_fallback_tail_question,
    generate_fallback_deep_dive,
    get_deep_dive_pattern,
)


class MathUtils:
    @staticmethod
    def calculate_percentage(score: float, max_score: float) -> int:
        if max_score <= 0:
            return 0
        return int(round((score / max_score) * 100))


logger = logging.getLogger(__name__)


# ============================================================================
# 0. 점수 기준 상수 (프롬프트와 코드가 이 값을 공유)
# ============================================================================

SCORE_CONFIG = {
    'max_score': 100,
    'llm_max': 85,                # LLM 만점: 85점 (체크리스트 합계와 일치)
    'rule_max': 15,               # Rule 만점: 15점 (필수 개념 가산 + 치명적 오류 감점)
    'pass_threshold': 75,
    'deep_dive_threshold': 85,
    'dimension_weights': {
        'design': 25,
        'consistency': 20,
        'abstraction': 15,
        'edgeCase': 15,
        'implementation': 10,     # 합계 = 85 = LLM 만점과 정확히 일치
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
    PRIMARY_MODEL = "gpt-4o"  # 최신 플래그십 모델 (GPT-5급 성능 지향)


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
    tail_answer: str = ""
    deep_answer: str = ""

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
        tail_answer: str = "",
        deep_answer: str = "",
        model: str = ModelConfig.PRIMARY_MODEL,
        timeout: int = 40,
    ) -> LLMEvaluationResult:

        if not self.client:
            raise LLMUnavailableError("OpenAI 클라이언트를 초기화할 수 없습니다. API 키를 확인해 주세요.")

        start = time.time()
        try:
            system_prompt, user_prompt = self._build_prompts(
                pseudocode, rule_result, quest_title, tail_answer, deep_answer
            )
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
        tail_answer: str = "",
        deep_answer: str = "",
    ) -> Tuple[str, str]:
        weights = SCORE_CONFIG['dimension_weights']
        llm_max = SCORE_CONFIG['llm_max']

        # Quest별 루브릭 주입
        quest_id = extract_quest_id_from_title(quest_title)
        rubric_text = get_rubric_for_prompt(quest_id) if quest_id > 0 else ""

        system = f"""당신은 20년 경력의 전설적인 수석 아키텍트 'Coduck Wizard'입니다.
사용자의 설계(의사코드, 꼬리질문 답변, 심화 서술형 답변)를 종합적으로 분석하여 5차원 평가를 수행하고 Python 코드로 변환하십시오.

[채점 방식 - **가산식 (Additive Scoring)** / LLM 만점 {llm_max}점]
**0점에서 시작**하여 아래 체크리스트 항목을 충족할 때마다 해당 점수를 가산하십시오.
절대 "만점에서 감점"하지 마십시오. 오직 "0점에서 가산"만 허용됩니다.

각 차원의 만점:
1. **design (설계력 - {weights['design']}점)**: 전체적 논리 흐름의 효율성과 구조적 완성도.
2. **consistency (정합성 - {weights['consistency']}점)**: 요구사항 준수 및 모든 단계의 통일성.
3. **abstraction (추상화 - {weights['abstraction']}점)**: 로직의 모듈화 및 개념적 일반화 수준.
4. **edgeCase (예외처리 - {weights['edgeCase']}점)**: 비정상 데이터 및 예외 상황에 대한 대비책.
5. **implementation (구현력 - {weights['implementation']}점)**: 상세 로직의 구체성 및 파이썬 코드 변환 가능성.

합산: design + consistency + abstraction + edgeCase + implementation = overall_score (0~{llm_max})
※ 각 차원의 점수는 해당 만점을 절대 초과할 수 없습니다.

[빈틈 페널티]
- Python 변환 시 `# [생각의 빈틈]` 주석이 발생한 차원은 해당 차원 가산 점수에서 30% 차감.
- 빈틈이 3개 이상이면 overall_score 상한을 {llm_max}점의 77% ({int(llm_max * 0.77)}점)로 제한.

[점수 앵커 — 동일 수준의 답변은 반드시 동일 점수대를 부여하십시오]
- **Good (LLM 55~70점)**: 핵심 개념 3가지를 모두 구체적으로 서술. 논리 순서가 명확하고 실무적.
- **Average (LLM 21~54점)**: 핵심 개념을 언급했으나 구체성이 부족하거나 일부 누락.
- **Poor (LLM 0~20점)**: 핵심 개념 대부분 누락. 추상적이고 모호한 1~2줄 답변.

[Python 변환 지침 - **전략적 직역**]
1. 사용자의 의사코드를 **1:1로 직역(Literal Translation)**하되, 전체적인 설계 등급이 **Good 이상일 경우 보편적인 추상화(예: '데이터 전처리 수행')는 주석 없이 유효한 코드로 자연스럽게 변환**하십시오.
2. **진정으로 논리가 비어있어 구현이 불가능한 핵심 지점**에만 다음 형식으로 주석을 남기십시오:
   - 형식: `# [생각의 빈틈] {{누락된 구체적 요소}}에 대한 {{고려해야 할 공학적 판단}} 로직이 필요합니다.`
   - 예시(Generic - 금지): `# [생각의 빈틈] 이 부분의 구체적인 로직이 필요합니다`
   - 예시(Specific - 권장): `# [생각의 빈틈] 이상치(Outlier)를 판별하는 기준(상하한선)과 처리 방식(제거/대체)에 대한 구체적 설계가 누락되었습니다.`
3. 코드 내의 모든 주석은 반드시 **한국어**로 작성하십시오.

[피드백 서술 지침]
1. **절대 금지 문구**: "총점이 100점이 아닌 이유는...", "점수가 감점된 이유는...", "~가 부족하여 감점되었습니다." — 이런 표현을 절대 사용하지 마십시오.
2. **권장 오프닝**: "현재 설계의 아키텍처적 완성도를 분석한 결과, ...", "제시된 로직에서 돋보이는 설계 의도와 보완이 필요한 지점은 다음과 같습니다."
3. **심층 분석(python_feedback)**: 왜 그런 설계 방식이 실무에서 위험한지, 어떤 연쇄적인 결함을 초래하는지를 아키텍트 관점에서 전문적으로 분석하십시오.
4. 모든 응답은 반드시 **한국어**로 작성하십시오. 부드러운 격려형 어조를 유지하되, 기술적 분석은 날카로워야 합니다.

응답은 반드시 JSON 형식으로만 제공합니다."""

        # tail_answer/deep_answer 존재 여부에 따라 평가 범위 안내 동적 생성
        eval_scope_note = "\n[평가 범위 안내]"
        if tail_answer and deep_answer:
            eval_scope_note += "\n의사코드 + 꼬리질문 답변 + Deep Dive 서술형 3가지를 종합하여 최종 점수를 산출하십시오."
        elif tail_answer:
            eval_scope_note += "\n의사코드 + 꼬리질문 답변 2가지를 종합하여 점수를 산출하십시오."
        else:
            eval_scope_note += "\n현재는 의사코드만 제출된 초기 평가입니다. 의사코드를 기준으로 점수를 산출하십시오."
        eval_scope_note += "\n※ 객관식 진단 문제(2문제)는 평가 대상이 아닙니다."

        # Quest별 루브릭 블록 (앵커 + 체크리스트)
        rubric_block = ""
        if rubric_text:
            rubric_block = f"""\n\n[미션별 채점 루브릭 — 반드시 이 기준에 따라 채점하십시오]
{rubric_text}
※ 위 앵커 샘플과 유사한 수준의 답변에는 반드시 해당 점수대를 부여하십시오.
※ 체크리스트의 각 항목을 하나씩 확인하고, 충족된 항목의 점수를 합산하여 차원 점수를 결정하십시오."""

        user = f"""[미션 Context]
- 미션명: {quest_title}{eval_scope_note}{rubric_block}
- [평가 대상 1] 자연어 의사코드 (Low Effort 판단 기준):
---
{pseudocode}
---
- [평가 대상 2] 꼬리질문(4지선다) 선택 답변: {tail_answer if tail_answer else '(아직 미제출)'}
- [평가 대상 3] Deep Dive 심화 서술형 답변: {deep_answer if deep_answer else '(아직 미제출)'}

[채점 절차 — 반드시 이 순서로 수행하십시오]
1. 위 체크리스트를 차원별로 하나씩 검토하여 충족 여부를 판단하십시오.
2. 충족된 항목의 점수를 합산하여 각 차원의 점수를 결정하십시오. (0점 시작, 가산)
3. 5개 차원 점수를 합산하여 overall_score를 산출하십시오. (0~{llm_max})
4. 의사코드를 Python으로 1:1 직역하여 `converted_python`에 할당하십시오. (주석은 한국어)
5. `python_feedback`에는 현재 설계 완성도와 지표별 점수에 대한 **입체적인 심층 분석 보고서**를 한국어로 작성하십시오.
6. **[꼬리질문 생성 핵심 지침]** - 아래 순서로 반드시 따르십시오:
   a. `converted_python`에서 `# [생각의 빈틈]` 주석이 발생한 위치를 확인하십시오.
   b. 점수가 가장 낮은 차원(dimension)을 찾으십시오.
   c. 꼬리질문은 반드시 위 (a)의 빈틈 위치 또는 (b)의 취약 차원 개념을 직접 겨냥해야 합니다.
   d. 질문은 "이 상황에서 어떻게 해야 하는가?" 형태의 **실무 판단형**으로 만드십시오.
   e. 정답 선택지는 사용자가 빈틈을 채웠을 때 습득하는 핵심 원칙이어야 합니다.
   f. 오답 선택지는 실제 현업에서 흔히 하는 잘못된 판단이어야 합니다 (단순 틀린 답 금지).
7. `deep_dive`의 시나리오는 꼬리질문 정답을 알아도 더 깊이 생각해야 하는 **응용 상황**을 제시하십시오.

출력 JSON 구조:
{{
    "overall_score": 0.0,
    "dimension_scores": {{
        "design": {{"score": 0.0, "comment": "...체크리스트 충족 내역 기반 설계 분석..."}},
        "consistency": {{"score": 0.0, "comment": "...정합성 체크리스트 충족 분석..."}},
        "edgeCase": {{"score": 0.0, "comment": "...예외 대응 체크리스트 충족 분석..."}},
        "abstraction": {{"score": 0.0, "comment": "...추상화 체크리스트 충족 분석..."}},
        "implementation": {{"score": 0.0, "comment": "...구현력 체크리스트 충족 분석..."}}
    }},
    "feedback": {{ "strengths": [], "improvements": [] }},
    "weakest_dimension": "design",
    "tail_question": {{
        "context": "[사용자 코드의 [생각의 빈틈] 위치 또는 취약 차원을 한 단어로 명시]",
        "question": "[해당 빈틈이나 취약점을 실무 상황으로 제시하는 판단형 질문]",
        "options": [
            {{"text": "[핵심 원칙을 제시하는 정답]", "is_correct": true, "feedback": "[왜 이 선택이 실무에서 옳은지 설명]"}},
            {{"text": "[현업에서 흔히 하는 잘못된 판단 1]", "is_correct": false, "feedback": "[이 접근이 왜 위험한지]"}},
            {{"text": "[현업에서 흔히 하는 잘못된 판단 2]", "is_correct": false, "feedback": "[이 접근이 왜 위험한지]"}},
            {{"text": "[현업에서 흔히 하는 잘못된 판단 3]", "is_correct": false, "feedback": "[이 접근이 왜 위험한지]"}}
        ]
    }},
    "deep_dive": {{
        "title": "...",
        "scenario": "[꼬리질문 정답을 알아도 더 깊이 생각해야 하는 응용 시나리오]",
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
    """
    점수 계산 전략 (2026-02-21 개편)

    LLM (0~85점): GPT가 체크리스트 기준 가산식 채점  → 실질 점수 결정
    Rule (0~15점): 필수 개념 포함 여부 가산 + 치명적 오류 감점  → LLM 보정

    공식: LLM점수(0~85) + Rule점수(0~15) = 최종점수 (0~100)

    Rule 가산 방식:
      필수 개념 1개당 +3점 (Quest당 3개 = 최대 9점)
      논리적 순서 준수 시 +6점
      치명적 오류 감지 시 Rule 점수 반토막 + LLM 상한 50점
    """

    # Quest별 필수 개념 (Rule점수 가산용)
    REQUIRED_CONCEPTS = {
        '1': ['data_split', 'fit_train', 'transform_test'],      # 데이터 누수 방지
        '2': ['regularization', 'feature_selection', 'monitoring'],  # 과적합 방지
        '3': ['imbalance_detect', 'sampling_strategy', 'fair_eval'],  # 불균형
        '4': ['feature_create', 'feature_transform', 'feature_select'],  # 피자 엔지니어링
        '5': ['param_space', 'search_strategy', 'cross_validation'],  # 하이퍼파라미터 튀닝
        '6': ['global_interpret', 'local_interpret', 'fairness_check'],  # 해석성
    }

    def calculate(
        self,
        llm_score_85: int,
        rule_result: RuleValidationResult,
        quest_id: str = '1',
    ) -> Dict[str, Any]:
        llm_max = SCORE_CONFIG['llm_max']   # 85
        rule_max = SCORE_CONFIG['rule_max']  # 15

        # LLM 점수 클램핑 (0~85)
        llm_clamped = max(0, min(llm_max, llm_score_85))

        # Rule 점수: 0점 시작 → 필수 개념 가산
        rule_details = rule_result.details or {}
        # [2026-02-21 버그 수정] PseudocodeValidator는 details.concepts로 반환
        found_concepts = rule_details.get('concepts', rule_details.get('foundConcepts', []))
        required = self.REQUIRED_CONCEPTS.get(str(quest_id), self.REQUIRED_CONCEPTS['1'])

        # 필수 개념 가산: 개당 3점 (최대 9점)
        concept_score = sum(3 for c in required if c in found_concepts)

        # 논리적 순서 준수: +6점
        order_bonus = 6 if rule_result.passed else 0

        rule_score = min(rule_max, concept_score + order_bonus)

        # 치명적 오류 시: Rule 반토막 + LLM 상한 50점
        if rule_result.critical_error_count > 0:
            rule_score = rule_score // 2
            llm_clamped = min(llm_clamped, 50)

        # 최종 점수: LLM(0~85) + Rule(0~15) = 0~100
        final = max(0, min(100, llm_clamped + rule_score))

        if final >= 92:
            grade = 'EXCELLENT'
        elif final >= 82:
            grade = 'GOOD'
        elif final >= 62:
            grade = 'AVERAGE'
        else:
            grade = 'POOR'

        return {
            'final_score': round(final, 1),
            'llm_score_85': llm_clamped,
            'rule_score_15': rule_score,
            'rule_concept_score': concept_score,
            'rule_order_bonus': order_bonus,
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

        dimension_names = {
            'design': '설계력 (Design)',
            'consistency': '정합성 (Consistency)',
            'abstraction': '추상화 (Abstraction)',
            'edgeCase': '예외처리 (Edge Case)',
            'implementation': '구현력 (Implementation)'
        }
        
        raw_dims = llm_result.dimension_scores or {}
        dimensions = {}
        for dim, max_val in weights.items():
            raw_data = raw_dims.get(dim, {})
            # score 추출 (숫자 혹은 dict 형태 대응)
            try:
                if isinstance(raw_data, dict):
                    val = float(raw_data.get('score', 0))
                    comment = raw_data.get('comment', '')
                else:
                    val = float(raw_data)
                    comment = ''
            except (TypeError, ValueError):
                val = 0.0
                comment = ''
            
            clamped_val = min(val, max_val)  # max 초과 방지 (GPT가 가중치 초과할 경우 대비)
            percentage = MathUtils.calculate_percentage(clamped_val, max_val)
            dimensions[dim] = {
                'name': dimension_names.get(dim, dim.capitalize()),
                'score': round(clamped_val, 1),
                'max': max_val,
                'percentage': percentage,
                'comment': comment or f"{dimension_names.get(dim)} 분석 결과입니다."
            }

        # 등급 한글 변환
        GRADE_KO = {
            'EXCELLENT': '최우수',
            'GOOD':      '우수',
            'AVERAGE':   '보통',
            'POOR':      '미흡',
        }
        grade_ko = GRADE_KO.get(grade, grade)

        # 페르소나 및 summary (score 기반 고정 문구 — 등급은 한글로)
        if score >= 92:
            persona = "철옹성 설계자"
            summary = f"{grade_ko} — 실무에서도 즉시 사용 가능한 완벽한 설계입니다."
        elif score >= 82:
            persona = "원칙 중심의 이론가"
            summary = f"{grade_ko} — 핵심 설계 원칙을 잘 준수하고 있습니다. 예외 상황을 조금 더 고민하면 완벽해질 거예요."
        elif score >= 62:
            persona = "성장하는 아키텍트"
            summary = f"{grade_ko} — 방향성은 잡혔습니다. 로직을 더 구체적으로 쪼개보는 연습이 필요해요."
        else:
            persona = "견습 아키텍트"
            summary = f"{grade_ko} — 설계의 뼈대부터 다시 잡아야 합니다. 가이드를 참고해 논리 순서를 정리해보세요."

        llm_feedback = llm_result.feedback or {}

        # senior_advice: GPT 생성 맞춤 코멘트 우선,
        # 빈 값이면 python_feedback 앞 100자 사용, 그것도 없으면 summary fallback
        gpt_advice = (llm_result.senior_advice or '').strip()
        if not gpt_advice:
            python_fb = (llm_result.python_feedback or '').strip()
            gpt_advice = python_fb[:120] + ('...' if len(python_fb) > 120 else '') if python_fb else summary

        return {
            'summary': summary,
            'persona': persona,
            'dimensions': dimensions,
            'strengths': llm_feedback.get('strengths', []),
            'improvements': llm_feedback.get('improvements', []),
            'senior_advice': gpt_advice,
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
        4. LLM 결과 검증 + 폴백 (tail_question, deep_dive)
        5. 점수 계산 (Rule 페널티 적용)
        6. 피드백 생성
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
            tail_answer=request.tail_answer,
            deep_answer=request.deep_answer,
        )

        # ── Step 4: LLM 결과 검증 + 폴백 ────────────────────────────
        if llm_result.status == "SUCCESS":
            # tail_question 검증
            if llm_result.tail_question:
                is_valid, error_msg = validate_tail_question(llm_result.tail_question)
                if not is_valid:
                    logger.warning(f"[Evaluate] tail_question validation failed: {error_msg}. Using fallback.")
                    llm_result.tail_question = generate_fallback_tail_question(
                        context=request.detail_id
                    )
            else:
                logger.warning(f"[Evaluate] tail_question is None. Using fallback.")
                llm_result.tail_question = generate_fallback_tail_question(request.detail_id)

            # deep_dive 검증
            if llm_result.deep_dive:
                is_valid, error_msg = validate_deep_dive(llm_result.deep_dive)
                if not is_valid:
                    logger.warning(f"[Evaluate] deep_dive validation failed: {error_msg}. Using fallback.")
                    llm_result.deep_dive = generate_fallback_deep_dive(request.detail_id)
            else:
                logger.warning(f"[Evaluate] deep_dive is None. Using fallback.")
                llm_result.deep_dive = generate_fallback_deep_dive(request.detail_id)

        # LLM 자체가 ERROR 상태라면 rule 점수 기반으로 fallback
        llm_max = SCORE_CONFIG['llm_max']  # 85
        if llm_result.status != "SUCCESS" or llm_result.raw_score is None:
            llm_score = min(rule_result.raw_score_100, llm_max)  # fallback도 85 상한
        else:
            llm_score = max(0, min(llm_max, int(llm_result.raw_score)))

        # ── Step 5: 점수 계산 ─────────────────────────────────────
        scoring = self.scoring_engine.calculate(llm_score, rule_result)

        # ── Step 6: 피드백 생성 ───────────────────────────────────
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
