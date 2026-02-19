"""
의사코드 평가 엔진 - Hybrid Mode (Improved v2)
수정일: 2026-02-18
수정내용: 무성의 입력 감지, 꼬리 질문(tail_question), 심화 시나리오(deep_dive) 데이터 클래스 필드 추가 및 프롬프트 고도화
"""

import os
import json
import time
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
try:
    import openai
except ImportError:
    openai = None
from django.conf import settings
from core.models import UserProfile, PracticeDetail, UserSolvedProblem
from core.utils.pseudocode_validator import PseudocodeValidator
from core.utils.mission_rules import VALIDATION_RULES


# ============================================================================
# 1. 평가 모드 및 설정
# ============================================================================

class EvaluationMode(Enum):
    """평가 모드 (3가지 옵션)"""
    OPTION1_ALWAYS_MULTIMODEL = "option1_always_multimodel"  # 옵션1: 항상 3개 모델 사용
    OPTION2_GPTONLY = "option2_gptonly"                      # 옵션2: GPT-4o-mini만 사용
    OPTION3_HYBRID = "option3_hybrid"                        # 옵션3: 하이브리드 (로컬 성공→GPT, 실패→3모델)


class ModelConfig:
    """모델 설정"""
    PRIMARY_MODEL = "gpt-4o-mini"
    ALL_MODELS = [PRIMARY_MODEL]


# ============================================================================
# 2. 데이터 클래스
# ============================================================================

@dataclass
class EvaluationRequest:
    """평가 요청"""
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
class LocalValidationResult:
    """로컬 검증 결과"""
    passed: bool
    score: int
    feedback: List[str]
    warnings: List[str]
    processing_time_ms: int
    details: Dict[str, Any]
    is_low_effort: bool = False
    low_effort_reason: Optional[str] = None


@dataclass
class LLMEvaluationResult:
    """LLM 평가 결과"""
    model: str
    status: str  # SUCCESS, ERROR, TIMEOUT
    raw_score: Optional[int] = None
    dimension_scores: Optional[Dict[str, int]] = None
    feedback: Optional[Dict[str, Any]] = None
    converted_python: Optional[str] = None
    python_feedback: Optional[str] = None
    is_low_effort: bool = False
    low_effort_reason: Optional[str] = None  # [2026-02-18 추가] AttributeError 방지
    tail_question: Optional[Dict[str, Any]] = None
    deep_dive: Optional[Dict[str, Any]] = None
    senior_advice: Optional[str] = None
    error_message: Optional[str] = None
    latency_ms: int = 0
    confidence: float = 0.0


@dataclass
class FinalEvaluationResult:
    """최종 평가 결과"""
    user_id: str
    detail_id: str
    mode: EvaluationMode
    local_validation: LocalValidationResult
    llm_evaluations: Dict[str, LLMEvaluationResult]
    final_score: int
    grade: str
    persona: str
    feedback: Dict[str, Any]
    is_low_effort: bool
    tail_question: Optional[Dict[str, Any]]
    deep_dive: Optional[Dict[str, Any]]
    score_breakdown: Dict[str, Any]
    metadata: Dict[str, Any]


# ============================================================================
# 3. 로컬 검증 엔진
# ============================================================================

class LocalValidationEngine:
    """로컬 검증 (Rule 기반)"""
    
    def validate(self, pseudocode: str, quest_id: str = "1") -> LocalValidationResult:
        """의사코드 로컬 검증"""
        start_time = time.time()
        
        try:
            # 실효성 있는 규칙 로드 (mission_rules.py 활용)
            rules = VALIDATION_RULES.get(str(quest_id), VALIDATION_RULES.get("1"))
            validator = PseudocodeValidator(rules)
            result = validator.validate(pseudocode)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return LocalValidationResult(
                passed=result['passed'],
                score=result['score'],
                feedback=result.get('details', {}).get('structure', []),
                warnings=result.get('warnings', []),
                processing_time_ms=processing_time,
                details=result,
                is_low_effort=result.get('is_low_effort', False),
                low_effort_reason=result.get('low_effort_reason')
            )
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return LocalValidationResult(
                passed=False, score=0, feedback=[f"검증 오류: {str(e)}"],
                warnings=["로컬 검증 실패"], processing_time_ms=processing_time,
                details={"error": str(e)}
            )


# ============================================================================
# 4. LLM 평가 엔진 (OpenAI v1.0+ 호환)
# ============================================================================

class LLMEvaluationEngine:
    """LLM 기반 평가 및 코드 생성"""
    
    def __init__(self):
        if openai:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
    
    def evaluate_with_single_model(
        self, 
        pseudocode: str, 
        local_validation: LocalValidationResult,
        quest_title: str = "데이터 전처리 미션",
        model: str = ModelConfig.PRIMARY_MODEL,
        timeout: int = 30  # [2026-02-18] 프론트 45초 타임아웃과 여유 확보
    ) -> LLMEvaluationResult:
        """단일 모델 평가 및 Python 변환"""
        
        start_time = time.time()
        
        try:
            system_prompt, user_prompt = self._create_prompts(pseudocode, local_validation, quest_title)
            
            # API 호출 (OpenAI 전용)
            response_text = self._call_openai(system_prompt, user_prompt, model, timeout)
            
            # 응답 파싱
            parsed = self._parse_json_response(response_text)
            latency = int((time.time() - start_time) * 1000)
            
            return LLMEvaluationResult(
                model=model,
                status='SUCCESS',
                raw_score=parsed.get('overall_score', 0),
                dimension_scores=parsed.get('dimension_scores', {}),
                feedback=parsed.get('feedback', {}),
                converted_python=parsed.get('converted_python', ""),
                python_feedback=parsed.get('python_feedback', ""),
                is_low_effort=parsed.get('is_low_effort', False),
                tail_question=parsed.get('tail_question'),
                deep_dive=parsed.get('deep_dive'),
                senior_advice=parsed.get('senior_advice', ""),
                latency_ms=latency,
                confidence=parsed.get('confidence', 0.8)
            )
        
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            return LLMEvaluationResult(
                model=model, status='ERROR', error_message=str(e), latency_ms=latency
            )
    
    def evaluate_with_multiple_models(
        self, pseudocode: str, local_validation: LocalValidationResult, quest_title: str
    ) -> Dict[str, LLMEvaluationResult]:
        """다중 모델 호환성 유지 (단일 모델만 수행)"""
        results = {}
        for model in ModelConfig.ALL_MODELS:
            results[model] = self.evaluate_with_single_model(pseudocode, local_validation, quest_title, model=model)
        return results

    def _create_prompts(self, pseudocode, local_result, quest_title):
        system = """당신은 전설적인 아키텍트 'Coduck Wizard'입니다.
사용자의 의사코드를 5차원으로 정밀 평가하고 파이썬 코드로 변환하십시오.

[채점 기준 - 각 차원의 만점은 아래와 같습니다 (총합 85점)]
- design (설계력): 만점 25점
- consistency (정합성): 만점 20점  ← 데이터 누수(Data Leakage) 여부를 매우 엄격하게 진단
- edge_case (예외처리): 만점 15점
- abstraction (추상화): 만점 15점
- implementation (구현력): 만점 10점

⚠️ 중요: dimension_scores의 각 값은 반드시 해당 차원의 만점 기준 실제 점수로 응답하십시오.
예) design이 우수하면 20~25, 보통이면 12~18, 미흡하면 0~10 (100점 환산 아님)
overall_score는 5개 차원 점수의 합계 (0~85점 범위)로 산출하십시오.

응답은 반드시 JSON 형식으로 제공합니다."""

        user = f"""미션: {quest_title}
의사코드:
---
{pseudocode}
---
로컬 룰 검증 결과: {local_result.score}점 (100점 만점), 누락 개념: {local_result.warnings}

요청:
1. **차원별 평가** (각 차원의 만점 기준으로 직접 점수 산출):
   - design: 0~25점
   - consistency: 0~20점 (데이터 누수/fit-transform 순서 엄격 검증)
   - edge_case: 0~15점
   - abstraction: 0~15점
   - implementation: 0~10점
   - overall_score = 위 5개 합계 (0~85)

2. **청사진(Blueprint)**: 의사코드를 수준 높은 파이썬 코드(converted_python)로 변환

3. **꼬리 질문(tail_question)** - 4지 선다형:
   - overall_score < 68 (80점 만점 기준 미달)이면: 사용자가 틀리거나 부족한 부분을 인지하게 하는 질문
   - overall_score >= 68이면: 심화 사고확장 문제

4. **심화 챌린지(deep_dive)**:
   - overall_score >= 68 (80점 만점 환산 기준)인 경우에만 생성
   - 실무 아키텍처 서술형 시나리오 질문

5. **가점 원칙 (Keyword Scoring)**:
   - 핵심 키워드(Isolation/격리, Anchor/기준점, Consistency/일관성)를 포함하면
     이해도 높음으로 판단하여 overall_score를 68~85점 수준으로 적극 가점

출력 JSON 구조:
{{
    "overall_score": 0,
    "is_low_effort": false,
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
        "model_answer": "전문 아키텍트의 관점에서의 1~2줄 핵심 모범 답안",
        "ideal_answer_concept": "..."
    }},
    "converted_python": "...",
    "python_feedback": "...",
    "senior_advice": "...",
    "confidence": 0.9
}}
is_low_effort가 true인 경우에도 학습을 위해 converted_python에는 반드시 모범 답안(Blueprint)을 넣으십시오.
"""
        return system, user

    def _call_openai(self, system, user, model, timeout):
        if not self.client:
            raise Exception("OpenAI 라이브러리가 설치되지 않았거나 클라이언트 초기화에 실패했습니다.")
            
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={"type": "json_object"},
            temperature=0.3,
            timeout=timeout
        )
        return response.choices[0].message.content

    def _parse_json_response(self, text):
        try:
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                return json.loads(json_match.group(0))
            return {}
        except: return {}


# ============================================================================
# 5. 점수 및 피드백 엔진
# ============================================================================

class ScoringEngine:
    def calculate_hybrid_score(self, llm_response: Dict[str, Any], local_score_100: int, has_critical: bool = False) -> Dict[str, Any]:
        """
        [2026-02-18] 85:85 하이브리드 점수 산출
        - Rule: local_score_100 (0~100) -> 0~85점 환산
        - LLM: dimension_scores (각 차원의 만점 기준으로 직접 응답) -> 합계 0~85점
        - Total: Rule + LLM = 0~170점 -> /1.7 = 0~100점
        """
        # 1. 룰 기반 점수 (100점 만점 -> 85점 만점 환산)
        rule_score_85 = (local_score_100 / 100.0) * 85.0

        # 2. LLM 차원별 점수 (LLM이 이미 각 만점 기준으로 반환)
        #    만점: design=25, consistency=20, edge_case=15, abstraction=15, implementation=10
        DIMENSION_MAX = {
            'design': 25.0,
            'consistency': 20.0,
            'edge_case': 15.0,
            'abstraction': 15.0,
            'implementation': 10.0
        }

        dimension_scores = llm_response.get('dimension_scores')
        if not isinstance(dimension_scores, dict):
            dimension_scores = {}

        scaled_dimensions = {}  # 프론트 표시용 (각 만점 기준 실제 점수)
        ai_score_85 = 0.0

        for dim, max_score in DIMENSION_MAX.items():
            score_data = dimension_scores.get(dim, 0)
            try:
                if isinstance(score_data, dict):
                    val = float(score_data.get('score', 0))
                else:
                    val = float(score_data)
            except (ValueError, TypeError):
                val = 0.0

            # 만점 초과 방지 클리핑
            val = min(val, max_score)
            scaled_dimensions[dim] = round(val, 1)
            ai_score_85 += val

        # overall_score도 참고용으로 저장 (LLM이 합계로 준 경우)
        llm_overall = llm_response.get('overall_score', 0)

        # 3. 합산 및 정규화 (170점 만점 -> 100점)
        total_170 = rule_score_85 + ai_score_85
        final_score_100 = round(total_170 / 1.7)

        # 4. 등급 결정
        if final_score_100 >= 80:   grade = 'EXCELLENT'
        elif final_score_100 >= 65: grade = 'GOOD'
        elif final_score_100 >= 45: grade = 'AVERAGE'
        else:                       grade = 'POOR'

        return {
            'total_score_100': final_score_100,
            'rule_raw_100': local_score_100,
            'rule_score_85': round(rule_score_85, 1),
            'ai_raw_85': round(ai_score_85, 1),     # LLM 실제 합계 (0~85)
            'ai_llm_overall': llm_overall,           # LLM이 직접 준 overall 참고값
            'ai_dimensions_custom': scaled_dimensions,
            'grade': grade,
            'total_170': round(total_170, 1)
        }

    def aggregate_multiple_scores(self, results: Dict[str, LLMEvaluationResult]) -> Dict[str, Any]:
        succs = [r.raw_score for r in results.values() if r.status == 'SUCCESS' and r.raw_score is not None]
        if not succs: return {'final_score': 0, 'confidence': 0.0, 'consistency_std_dev': 0}
        avg = sum(succs) / len(succs)
        return {'final_score': int(avg), 'confidence': 0.9, 'consistency_std_dev': 0.0}


class FeedbackEngine:
    def generate_feedback(self, llm_response: Dict[str, Any], scoring_result: Dict[str, Any], is_low_effort=False, low_effort_reason=None) -> Dict[str, Any]:
        raw_dimensions = llm_response.get('dimension_scores') or {}
        scaled_map = scoring_result.get('ai_dimensions_custom', {})
        
        dimensions = {}
        for dim, data in raw_dimensions.items():
            if not isinstance(data, dict):
                data = {'score': data, 'basis': '평가 완료', 'improvement': ''}
            
            # 사용자 지정 가중치(Design 25, etc.)가 적용된 점수 주입
            dimensions[dim] = {
                'score': scaled_map.get(dim, 0),
                'original_score': data.get('score', 0),
                'basis': data.get('basis', '평가 기준에 따른 분석입니다.'),
                'improvement': data.get('improvement', '현재 설계를 유지하거나 조금 더 상세화해 보세요.'),
                'specific_issue': data.get('specific_issue', '')
            }

        # [2026-02-18 수정] dict/int 모두 안전하게 design 점수 읽기
        raw_design = raw_dimensions.get('design', 0)
        if isinstance(raw_design, dict):
            design = raw_design.get('score', 0)
        elif isinstance(raw_design, (int, float)):
            design = raw_design
        else:
            design = 0
        
        # 최종 점수 기준으로 등급 문구 결정 (design 단일 지표보다 종합점수 우선)
        final_score = scoring_result.get('total_score_100', 0)
        
        if is_low_effort:
            persona = "성장의 씨앗을 품은 학생"
            summary = "설계 초안 분석 단계입니다. 청사진(Blueprint)을 통해 핵심 원리를 익힌 후 다시 도전해 보세요!"
        elif final_score >= 80 or design > 80:
            persona = "철옹성 설계자"
            summary = f"{scoring_result['grade']} 등급의 완벽한 설계입니다."
        elif final_score >= 65 or design > 60:
            persona = "원칙 중심의 이론가"
            summary = f"{scoring_result['grade']} 등급의 우수한 설계입니다."
        elif final_score >= 45:
            persona = "성장하는 아키텍트"
            summary = f"{scoring_result['grade']} 등급의 설계입니다."
        else:
            persona = "견습 아키텍트"
            summary = f"{scoring_result['grade']} 등급입니다. 핵심 원칙을 다시 검토해 보세요."
        
        feedback_data = llm_response.get('feedback') or {}
        
        return {
            'summary': summary,
            'persona': persona,
            'dimensions': dimensions,
            'strengths': feedback_data.get('strengths', []),
            'improvements': feedback_data.get('improvements', []),
            'senior_advice': llm_response.get('senior_advice', summary)
        }


# ============================================================================
# 6. 메인 오케스트레이터
# ============================================================================

class PseudocodeEvaluator:
    def __init__(self):
        self.local_validator = LocalValidationEngine()
        self.llm_engine = LLMEvaluationEngine()
        self.scoring_engine = ScoringEngine()
        self.feedback_engine = FeedbackEngine()

    def evaluate(self, request: EvaluationRequest) -> FinalEvaluationResult:
        try:
            # 1. 로컬 검증
            local_result = self.local_validator.validate(request.pseudocode, request.detail_id)
            
            llm_evaluations = {}
            final_score = 0
            
            # 2. LLM 평가 (옵션에 따름)
            try:
                if request.mode == EvaluationMode.OPTION2_GPTONLY:
                    res = self.llm_engine.evaluate_with_single_model(request.pseudocode, local_result, request.quest_title)
                    llm_evaluations[ModelConfig.PRIMARY_MODEL] = res
                else:
                    llm_evaluations = self.llm_engine.evaluate_with_multiple_models(request.pseudocode, local_result, request.quest_title)
            except Exception as llm_err:
                print(f"[LLM Engine Crash] {llm_err}")
                # AI 호출 자체가 실패한 경우 에러 객체 생성
                err_res = LLMEvaluationResult(model=ModelConfig.PRIMARY_MODEL, status='ERROR', error_message=str(llm_err))
                llm_evaluations[ModelConfig.PRIMARY_MODEL] = err_res

            # 3. 정규화 및 피드백
            if not llm_evaluations:
                # LLM 결과가 아예 없는 경우 방어용 더미 데이터 생성
                err_res = LLMEvaluationResult(model=ModelConfig.PRIMARY_MODEL, status='ERROR', error_message="LLM 호출 결과 없음")
                llm_evaluations[ModelConfig.PRIMARY_MODEL] = err_res

            primary_res = llm_evaluations.get(ModelConfig.PRIMARY_MODEL) or next(iter(llm_evaluations.values()))
            
            # [2026-02-18] 무성의 입력 판정 (사용자 경험 보호용 최소 제한)
            # LLM 결과가 오기 전, 명시적 포기 의사만 로컬에서 0차 필터링
            is_low_effort_by_logic = False
            low_effort_reason_by_logic = None
            
            surrender_keywords = ["모르겠", "모름", "몰라", "어려워", "포기", "잘 안됨", "힘들"]
            if any(sk in request.pseudocode for sk in surrender_keywords):
                is_low_effort_by_logic = True
                low_effort_reason_by_logic = "원리를 아직 파악 중이시군요. 청사진을 통해 핵심을 짚어보세요!"
            
            # 짧은 문장에 대한 "무조건 낙제" 로직 제거 
            # -> 대신 LLM이 문맥을 보고 판단하도록 위임 (신뢰성 회복)
            llm_data = {
                'overall_score': primary_res.raw_score or 0,
                'dimension_scores': primary_res.dimension_scores or {},
                'feedback': primary_res.feedback or {},
                'senior_advice': primary_res.senior_advice or ""
            }
            has_critical = not local_result.passed
            scoring = self.scoring_engine.calculate_hybrid_score(llm_data, local_result.score, has_critical=has_critical)
            
            final_low_effort = local_result.is_low_effort or primary_res.is_low_effort or is_low_effort_by_logic
            final_low_effort_reason = low_effort_reason_by_logic or local_result.low_effort_reason or primary_res.low_effort_reason

            feedback = self.feedback_engine.generate_feedback(
                llm_data, 
                scoring, 
                is_low_effort=final_low_effort,
                low_effort_reason=final_low_effort_reason
            )
            
            return FinalEvaluationResult(
                user_id=request.user_id,
                detail_id=request.detail_id,
                mode=request.mode,
                local_validation=local_result,
                llm_evaluations=llm_evaluations,
                final_score=scoring['total_score_100'],
                grade=scoring['grade'],
                persona=feedback['persona'],
                feedback=feedback,
                is_low_effort=final_low_effort,
                tail_question=primary_res.tail_question,
                deep_dive=primary_res.deep_dive,
                score_breakdown=scoring,
                metadata={
                    'latency': sum(r.latency_ms for r in llm_evaluations.values() if r),
                    'model': primary_res.model,
                    'status': primary_res.status
                }
            )
        except Exception as e:
            # [최후의 보루] 엔진 전체 크래시 시 안전한 Fallback 결과 반환
            print(f"[Critical Evaluator Error] {e}")
            import traceback
            print(traceback.format_exc())
            
            # 최소한의 데이터로 복구 결과 생성 (local_result가 없을 수도 있음)
            _local_result = locals().get('local_result') or LocalValidationResult(
                passed=False, score=0, feedback=['엔진 에러'], warnings=[], processing_time_ms=0, details={}
            )
            dummy_scoring = self.scoring_engine.calculate_hybrid_score({'overall_score': 0}, _local_result.score)
            return FinalEvaluationResult(
                user_id=request.user_id, detail_id=request.detail_id, mode=request.mode,
                local_validation=_local_result,
                llm_evaluations={ModelConfig.PRIMARY_MODEL: LLMEvaluationResult(model=ModelConfig.PRIMARY_MODEL, status='ERROR', error_message=str(e))},
                final_score=dummy_scoring['total_score_100'],
                grade=dummy_scoring['grade'],
                persona="시스템 안전 모드",
                feedback={'summary': '엔진 재시작 중입니다. 로컬 진단 결과로 우선 학습을 진행하세요.', 'dimensions': {}},
                is_low_effort=True,
                tail_question=None, deep_dive=None,
                score_breakdown=dummy_scoring,
                metadata={'status': 'CRASH_RECOVERED'}
            )
