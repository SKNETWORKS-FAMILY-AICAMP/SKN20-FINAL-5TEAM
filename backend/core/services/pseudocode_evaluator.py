"""
의사코드 평가 엔진 - Refactored
수정일: 2026-02-19

[변경 사항]
- Rule은 "감점 게이트" 역할, LLM이 실질 점수 담당 (역할 분리)
- 점수 기준 상수화 (SCORE_CONFIG) - 프롬프트 모순 제거
- 키워드 가점 로직 제거
- LowEffortDetector 단일 진입점으로 통합
- 에러 타입별 커스텀 예외 도입
- [수정 2026-02-22] 억지 긍정(마스킹) 로직 제거 및 채점 공식 단순화
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
    get_recommended_videos_legacy,
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
    'divisor': 1.0,               # LLM(85) + Rule(15) = 100점 만점, 나눗수 불필요
    'rule_penalty_per_error': 5,  # 치명적 오류 1개당 감점
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
    internal_reasoning: Optional[str] = None  # [추가 2026-02-22] CoT 단계별 추론 과정
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
    recommended_videos: List[Dict[str, Any]] = field(default_factory=list)
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
                internal_reasoning=parsed.get("internal_reasoning", ""),
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

        system = f"""당신은 전설적인 소프트웨어 아키텍트이자 다정한 멘토인 'Coduck'입니다.
        사용자가 작성한 의사코드(설계)를 분석하여 격려와 함께 실무적인 피드백을 주십시오.
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        [0] 채점 대원칙 (Grade Policy) — 반드시 준수
        - **점수 스케일**: overall_score는 반드시 0~{llm_max} 사이의 정수로 응답하십시오. 100점 만점이 아닙니다.
        - **차원 점수**: 각 차원(design/consistency 등)은 해당 max 값 이하의 점수로 응답하십시오.
          예) design은 0~{weights['design']} 사이, consistency는 0~{weights['consistency']} 사이
        - 사용자가 핵심 의도(Ridge/Lasso 언급 등)를 파악했다면 점수를 아끼지 마십시오.
        - **절대 금기**: 이해 가능한 수준의 논리 흐름이 있다면 0점이나 극단적으로 낮은 점수(1~2점)를 주지 마십시오.
        [평가 가이드라인 - 긍정적 보상 및 디테일 강화 (수정일: 2026-02-23)]
        - **중요**: 부족한 점을 찾아 감점하기보다, 사용자가 잘 서술한 부분과 기술적 디테일을 찾아 점수를 더해주는 **'가산점 방식(Additive Scoring)'**을 취하십시오.
        - 사용자가 단계별로 논리를 쪼개어 구체적으로 서술했다면, AI 만점(85점) 중 **80점 이상**을 주저 없이 부여하십시오.
        - 핵심 알고리즘(Lasso, Ridge 등)이나 전문 용어(Hyperparameter, Validation 등)를 적절히 사용했다면 높은 전문성 점수를 반영하십시오.
        - 만점(85/85)은 도달 불가능한 점수가 아닙니다. 전문가 수준의 통찰력이 보인다면 과감하게 만점을 주십시오.
        - 사용자가 짧게 적었더라도 그 안에 담긴 '생각의 가치'를 높게 사서 최소 보통(AVERAGE) 이상의 점수를 유도하십시오.
        - **점수 안내 기준표** (overall_score 0~85 기준):
          전설적인 수준의 완벽한 설계 (디테일과 통찰력이 모두 압도적): 82~85점
          실무 수준의 매우 우수한 설계 (모든 단계·기법 명확 및 구체적): 76~81점
          핵심 흐름과 도구를 명시한 양호한 설계 (fit/transform 분리, 모델 명칭 등): 60~75점
          방향성은 맞으나 세부 누락이 있는 설계 (단계 추상적이나 흐름 인지): 45~59점
          기초적인 흐름 인지 수준: 25~44점
          분석 불가능 수준: 5~24점
        - **[중요 - 2차 완화]**: 문제에서 명시적으로 요구하지 않은 특정 라이브러리나 도구(예: GridSearchCV, Optuna, MLflow 등)가 언급되지 않았다고 해서 감점하지 마십시오. 사용자가 제시한 논리 흐름 자체가 무결하다면 해당 차원 점수는 반드시 90% 이상(만점에 가깝게) 부여하십시오. (수정일: 2026-02-23)
        - **중요**: 사용자가 핵심 알고리즘/기법 이름(Ridge, SMOTE, StandardScaler 등)을 1개 이상 언급했다면 overall_score 최소 60 이상을 부여하십시오. (수정일: 2026-02-23 - 3차 상향)
        - **중요**: 4단계 이상의 논리적 흐름이 있고 방향성이 명확하면 overall_score 최소 70 이상을 부여하십시오. (수정일: 2026-02-23 - 3차 상향)
        - **Converted Python**은 사용자가 공부할 수 있도록 항상 최선을 다해 완성도 높게 작성하십시오.

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        [1] 내부 추론 (Chain of Thought)
        모든 최종 결과 생성 전, 아래 항목을 `internal_reasoning`에 먼저 기록하십시오.
        - 현재 의사코드의 핵심 안티패턴(Anti-patterns) 3가지 추출
        - 실패 가능성이 있는 엣지 케이스(Failure Scenarios) 식별
        - **사고 흐름 추적(Logic Trace)**: 사용자의 의사코드가 파이썬 코드로 어떻게 매핑되는지 한 줄씩 매칭 분석
        - 사용자 답변 수준에 따른 '성장 경로' 설계 (교정 vs 심화)

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        [2] 안티패턴 체크리스트 (감점 및 피드백 핵심)
        아래 항목 감지 시 반드시 `improvements`에 구체적 해결책과 함께 명시하십시오.
        - [Leakage] train 데이터의 정보(평균/표준편차 등)를 test에 미리 노출하는가?
        - [Hardcoding] 특정 모델, 클래스, 파라미터에만 종속된 설계를 하고 있는가?
        - [Blind Spot] 결측치, 이상치, 데이터 타입 불일치에 대한 방어 로직이 전무한가?
        - [Fragility] 모델 로드/저장(Persistence) 시 map_location이나 직렬화 규칙을 무시하는가?

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        [3] 5차원 루브릭 채점표 (LLM 만점 {llm_max}점)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ▶ design (설계력) — {weights['design']}점
          [0-5]   논리 순서 붕괴, 핵심 처리 단계 누락
          [16-20] 흐름은 맞으나 구체적 기법(fit-transform)의 선후 관계 모호
          [21-25] 실무 수준의 파이프라인(Pipeline) 구조화 및 멱등성(Idempotency) 고려

        ▶ consistency (정합성) — {weights['consistency']}점
          [0-5]   train/test 혼용, 기준점 오염(Data Leakage) 발생
          [12-15] 데이터 분리 및 기준 유지 노력은 보이나 일부 코드에서 모순
          [16-20] 직렬화 규칙 및 운영 환경에서의 추론 일관성 완벽 보장

        ▶ abstraction (추상화) — {weights['abstraction']}점
          [0-4]   단순 절차 나열, 하드코딩된 로직
          [8-11]  함수/클래스 기반 모듈화 시도
          [12-15] 다른 도메인에도 즉시 이식 가능한 설계 패턴 적용

        ▶ edgeCase (예외처리) — {weights['edgeCase']}점
          [0-4]   완성된 데이터만 상정한 행복한 경로(Happy Path) 설계
          [8-11]  결측치/이상치 등 일반적인 데이터 이슈 대응
          [12-15] 네트워크 분할, 리소스 부족, 드리프트 등 운영 장애 시나리오 대응

        ▶ implementation (구현력) — {weights['implementation']}점
          [0-3]   자연어 위주이나 흐름은 이해됨 (최소한의 점수 부여)
          [4-7]   라이브러리(sklearn 등) 명칭 사용하나 파라미터 누락
          [8-10]  구체적 파라미터 및 로직 명시

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        [5] 파이썬 변환 및 사고 분석 지침
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        - **Converted Python**: **사용자가 아주 짧게 썼더라도, 심지어 자연어로만 적었더라도 절대 비워두거나 "구체적인 Python 코드가 필요합니다" 같은 텍스트를 넣지 마십시오.** 반드시 사용자의 의사코드 의도를 `# [의사코드]: ...` 형태의 주석으로 한 줄씩 포함하고, 그 바로 아래에 대응되는 완성된 파이썬 코드를 작성하십시오. 사용자가 "Ridge 학습" 한 마디만 써도 `from sklearn.linear_model import Ridge; model = Ridge(); model.fit(X_train, y_train)` 처럼 완전한 코드로 변환하십시오. 절대 "코드가 필요합니다", "구현이 필요합니다" 같은 placeholder 문구는 금지입니다.
        - **Python Feedback**: 단순 지식 요약이 아니라, 사용자의 **'생각의 순서(Logic Sequence)'**를 비평하십시오. "어떤 생각을 먼저 했어야 했는지", "이 흐름대로라면 결국 어떤 논리적 모순에 직격하는지"를 거울처럼 보여주십시오.

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        [4] 적응형 질문 및 피드백 지침
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        - **성공(82점 이상)**: 실무 판단형 질문. 정답을 알아도 더 깊은 '트레이드오프'를 묻는 Deep Dive 질문 생성.
        - **보통(62~81점)**: 핵심 원칙을 리마인드하는 '개념 확인형' 질문 및 힌트 제공.
        - **미흡(61점 이하)**: 오개념을 교정하거나, 정답의 실마리를 알려주는 '힌트성' 질문.
        - **피드백 스타일**: 칭찬보다는 시니어 아키텍트의 날카로운 분석을 우선하며, "무엇이 부족해서 만점이 아닌지"를 명확히 할 것.

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
- [평가 대상 1] 의사코드:
---
{pseudocode}
---
- [평가 대상 2] 꼬리질문 선택 답변: {tail_answer if tail_answer else '(미제출)'}
- [평가 대상 3] Deep Dive 답변: {deep_answer if deep_answer else '(미제출)'}

[출력 형식 정의] ⚠️ CRITICAL: overall_score는 반드시 0~{llm_max} 범위의 정수입니다. 100점이 아님!
예) 잘 쓴 의사코드 → overall_score: 65, 아주 훌륭하면 → overall_score: 78. 절대 85 초과 금지!
{{
    "internal_reasoning": "위 [1] 지침에 따른 AI의 단계별 사고 과정 (한국어)",
    "overall_score": 0,
    "dimension_scores": {{
        "design": {{"score": 0.0, "comment": "안티패턴 및 루브릭 준수 분석 (0~{weights['design']} 범위)"}},
        "consistency": {{"score": 0.0, "comment": "정합성 및 데이터 누수 분석 (0~{weights['consistency']} 범위)"}},
        "edgeCase": {{"score": 0.0, "comment": "예외 대응 및 실패 시나리오 분석 (0~{weights['edgeCase']} 범위)"}},
        "abstraction": {{"score": 0.0, "comment": "모듈화 및 재사용 구조 분석 (0~{weights['abstraction']} 범위)"}},
        "implementation": {{"score": 0.0, "comment": "구현 구체성 분석 (0~{weights['implementation']} 범위)"}}
    }},
    "feedback": {{ "strengths": ["강점 1", "..."], "improvements": ["안티패턴 1 및 개선안", "..."] }},
    "tail_question": {{
        "context": "취약점/빈틈 식별",
        "question": "적응형 전략에 따른 4지선다 질문 (힌트 혹은 심화)",
        "options": [
            {{"text": "정답", "is_correct": true, "reason": "옳은 이유"}},
            {{"text": "오답 1", "is_correct": false, "reason": "틀린 이유 1"}},
            {{"text": "오답 2", "is_correct": false, "reason": "틀린 이유 2"}},
            {{"text": "오답 3", "is_correct": false, "reason": "틀린 이유 3"}}
        ]
    }},
    "deep_dive": {{
        "title": "...",
        "scenario": "...",
        "question": "...",
        "model_answer": "..."
    }},
    "converted_python": "의사코드 1:1 직역 기반 고품질 Python 코드",
    "python_feedback": "설계의 입체적 심층 분석 보고서",
    "senior_advice": "수석 아키텍트의 핵심 멘토링 코멘트"
}}
"""
        return system, user

    def _safe_parse(self, text: str) -> Dict[str, Any]:
        """
        JSON 블록을 더 안정적으로 추출합니다.
        문자열 내의 첫 번째 '{'와 마지막 '}' 사이의 내용을 파싱합니다.
        """
        if not text:
            return {}
        try:
            # [2026-02-23] 정규식 최적화: 가장 바깥쪽 중괄호 쌍을 찾음
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx+1]
                return json.loads(json_str)
            
            # 정규식 fallback
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            logger.warning(f"[_safe_parse] JSON 파싱 실패: {e}")
        return {}


# ============================================================================
# 6. 점수 계산 (Rule = 감점 게이트, LLM = 실질 점수)
# ============================================================================

class ScoringEngine:

    def calculate(
        self,
        llm_score_85: int,
        rule_result: RuleValidationResult,
        dimension_scores: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        점수 산출 로직 (2026-02-24 수정):
        - GPT overall_score(0~85)와 dim_total을 비교해 더 높은 값 채택
        - Rule 점수: CRITICAL 에러가 없으면 고정 10점 보장 (방어적)
        - 최종 = LLM점수(85) + Rule점수(15) = 최대 100점
        """
        llm_max = SCORE_CONFIG['llm_max']  # 85

        # 1. LLM 점수 보정: GPT가 100점 기준으로 응답했을 경우 스케일링
        if llm_score_85 > llm_max:
            llm_score_85 = int(round(llm_score_85 * llm_max / 100))

        # 차원 합계 계산 (dim_total은 항상 85점 기준)
        dim_total = 0.0
        if dimension_scores:
            weights = SCORE_CONFIG['dimension_weights']
            for dim, d in dimension_scores.items():
                max_val = weights.get(dim, 25)
                if isinstance(d, dict):
                    raw_val = float(d.get('score', 0))
                else:
                    raw_val = float(d)
                # GPT가 차원 점수를 100점 기준으로 준 경우 스케일링
                if raw_val > max_val:
                    raw_val = raw_val * max_val / 100
                dim_total += min(raw_val, max_val)  # max 초과 방지

            # overall_score와 dim_total 중 더 높은 값 채택
            if dim_total > 0:
                llm_score_85 = min(llm_max, max(llm_score_85, int(round(dim_total))))

        # 2. Rule 점수 산출: 최대 15점
        rule_max = SCORE_CONFIG['rule_max']
        penalty_per = SCORE_CONFIG['rule_penalty_per_error']
        critical_penalty = rule_result.critical_error_count * penalty_per

        # raw_score_100이 0이어도 CRITICAL 에러가 없으면 기본 10점 보장
        if rule_result.raw_score_100 > 0:
            validator_raw = round((rule_result.raw_score_100 / 100) * rule_max, 1)
        else:
            # Rule 점수가 없으면 CRITICAL 에러 여부에 따라 기본값
            validator_raw = 0.0 if rule_result.critical_error_count > 0 else 10.0

        rule_score = max(0, validator_raw - critical_penalty)

        # 3. 최종 점수: LLM + Rule 합산 (상한 100)
        final = max(0, min(100, llm_score_85 + rule_score))

        # [수정일: 2026-02-23] 등급 임계값 2차 완화 (S등급 진입 장벽 하향: 90 -> 88)
        if final >= 88: # 90 -> 88
            grade = 'EXCELLENT'
        elif final >= 75: # 78 -> 75
            grade = 'GOOD'
        elif final >= 50: # 55 -> 50
            grade = 'AVERAGE'
        else:
            grade = 'POOR'

        return {
            'final_score': int(round(final)), # [수정 2026-02-23] RDS(IntegerField)와의 정합성을 위해 정수형으로 변환
            'llm_score_85': llm_score_85,
            'rule_score_15': rule_score,
            'rule_validator_raw': validator_raw,
            'rule_penalty': critical_penalty,
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
            
            # GPT가 100점 기준으로 응답한 경우 스케일링 후 클램핑
            if val > max_val:
                val = val * max_val / 100
            clamped_val = min(val, max_val)  # max 초과 방지
            percentage = MathUtils.calculate_percentage(clamped_val, max_val)

            # [수정 2026-02-22] 억지 긍정(마스킹) 로직 제거. 
            # 진실된 피드백을 위해 AI가 생성한 원본 코멘트를 그대로 유지함.
            # (과거 로직: 점수 높을 때 부정어 포함 시 강제 긍정 치환)

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
        # [수정일: 2026-02-23] 페르소나 및 요약 문구 임계값 2차 동기화
        if score >= 88: # 90 -> 88
            persona = "철옹성 설계자"
            summary = f"{grade_ko} — 실무에서도 즉시 사용 가능한 완벽한 설계입니다."
        elif score >= 75: # 78 -> 75
            persona = "원칙 중심의 이론가"
            summary = f"{grade_ko} — 핵심 설계 원칙을 잘 준수하고 있습니다. 예외 상황을 조금 더 고민하면 완벽해질 거예요."
        elif score >= 50: # 55 -> 50
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
        # [수정 2026-02-23] 청사진 모드 진입을 위한 첫 제출일 때만 LowEffortError 발생
        # 이미 꼬리질문(tail_answer)이나 심화 답변(deep_answer)을 한 상태라면 평가를 진행함
        is_low, reason = LowEffortDetector.check(request.pseudocode)
        if is_low and not (request.tail_answer or request.deep_answer):
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
            # fallback: rule 점수 0이라도 기본값 30점 보장 (0점 방지)
            fallback_base = max(30, rule_result.raw_score_100) if rule_result.raw_score_100 > 0 else 30
            llm_score = min(fallback_base, llm_max)
        else:
            raw = int(llm_result.raw_score)
            # GPT가 100점 기준으로 응답했을 경우 (85 초과) 자동 스케일링
            if raw > llm_max:
                raw = int(round(raw * llm_max / 100))
            llm_score = max(0, min(llm_max, raw))  # 0~85 범위로 클램핑

        # ── Step 5: 점수 계산 ─────────────────────────────────────
        scoring = self.scoring_engine.calculate(
            llm_score, 
            rule_result, 
            llm_result.dimension_scores
        )

        # [수정 2026-02-23] 청사진 복구 모드 보정 (UI와 RDS 점수 동기화)
        # 무성의 입력이었으나 회복 답변(tail_answer 등)이 있는 경우, 최소 60점 이상을 보장하여 RDS에 기록되게 함
        if (request.tail_answer or request.deep_answer):
            current_score = scoring['final_score']
            if current_score < 60:
                logger.info(f"[Evaluate] Recovery boost applied: {current_score} -> 60+")
                # UI의 variance(60~64)와 유사하게 최소 점수 보정
                recovery_boost = 60 + (int(request.user_id[-1]) % 5 if request.user_id.isdigit() else 2)
                scoring['final_score'] = max(current_score, recovery_boost)
                # 등급 재산정
                if scoring['final_score'] >= 75: scoring['grade'] = 'GOOD'
                elif scoring['final_score'] >= 50: scoring['grade'] = 'AVERAGE'

        # ── Step 6: 피드백 생성 ───────────────────────────────────
        feedback = self.feedback_engine.generate(llm_result, scoring)

        # ── Step 7: 영상 큐레이션 (2026-02-23 추가) ────────────────
        try:
            from core.services.quest_resources import get_recommended_videos_legacy
            # detail_id가 'unit01_02' 형태일 수 있으므로 정규화된 숫자 ID 사용
            # 'unit01_02' -> '2', 'unit01_04' -> '4', '3' -> '3'
            raw_id = str(request.detail_id)
            normalized_quest_id = '1'  # 기본값
            if '_' in raw_id:
                # 'unit01_02' 형태: 마지막 언더스코어 뒤 숫자
                parts = raw_id.split('_')
                last_nums = re.findall(r'\d+', parts[-1])
                if last_nums:
                    n = int(last_nums[-1])
                    if 1 <= n <= 6:
                        normalized_quest_id = str(n)
            else:
                # 순수 숫자 또는 quest_4 형태
                all_nums = re.findall(r'\d+', raw_id)
                for n_str in all_nums:
                    n = int(n_str)
                    if 1 <= n <= 6:
                        normalized_quest_id = str(n)
                        break
            recommended_videos = get_recommended_videos_legacy(
                normalized_quest_id,
                feedback['dimensions'],
                max_count=3,
                quest_title=request.quest_title
            )
        except Exception as e:
            logger.error(f"[Evaluate] Failed to fetch recommended videos: {e}")
            recommended_videos = []

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
            recommended_videos=recommended_videos,
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