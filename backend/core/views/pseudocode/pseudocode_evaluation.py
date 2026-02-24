"""
의사코드 5차원 평가 뷰
수정일: 2026-02-21

[변경 사항]
- _build_success_response에 senior_advice 추가
- 영상 큐레이션: 백엔드에서 Quest ID × 취약 차원 기반으로 직접 제공
  · LLM 성공 여부와 관계없이 항상 recommended_videos 반환
  · 프론트는 이 값을 우선 사용, 없으면 로컬 learningResources.js 폴백
- 꼬리질문 context 필드 프론트 전달 추가
"""

import logging
import re
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.services.activity_service import save_user_problem_record
from core.models import UserProfile

from core.services.pseudocode_evaluator import (
    PseudocodeEvaluator,
    EvaluationRequest,
    EvaluationMode,
    LowEffortError,
    LLMTimeoutError,
    LLMUnavailableError,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Quest ID 정규화
# ============================================================================
def normalize_quest_id(quest_id):
    """quest_id를 1~6 사이의 Quest 번호로 정규화.
    
    입력 예시: 'unit01_02', 'UNIT01_03', '2', 'quest_4', 'QUEST_5'
    출력 예시: '2', '3', '2', '4', '5'
    
    핵심 로직:
    - 'unit01_XX' 형태: 언더스코어 뒤 숫자가 Quest 번호
    - 숫자만 있는 경우: 그대로 사용
    - 1~6 범위 벗어나면 '1' 폴백
    """
    if not quest_id:
        return "1"
    q_str = str(quest_id).strip()
    
    # 'unit01_02' 형태 처리: 언더스코어 뒤 숫자 추출
    if '_' in q_str:
        parts = q_str.split('_')
        try:
            # 마지막 부분에서 숫자 추출 (e.g., '02' -> 2)
            last_part = re.findall(r'\d+', parts[-1])
            if last_part:
                n = int(last_part[-1])
                if 1 <= n <= 6:
                    return str(n)
        except Exception:
            pass
    
    # 'quest_4' 또는 순수 숫자 처리
    nums = re.findall(r'\d+', q_str)
    for n_str in nums:
        try:
            n = int(n_str)
            if 1 <= n <= 6:
                return str(n)
        except Exception:
            continue
    
    return "1"


# ============================================================================
# 뷰
# ============================================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def evaluate_pseudocode_5d(request):
    """
    [POST] /api/core/pseudocode/evaluate-5d/
    5차원 의사코드 평가.
    """
    user_id = request.user.id
    quest_id = request.data.get('quest_id', '1')
    quest_title = request.data.get('quest_title', '데이터 전처리 미션')
    pseudocode = request.data.get('pseudocode', '').strip()
    tail_answer = request.data.get('tail_answer', '').strip()
    deep_answer = request.data.get('deep_answer', '').strip()

    if not pseudocode:
        return Response(
            {"error": "pseudocode 필드가 비어 있습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    evaluator = PseudocodeEvaluator()
    eval_request = EvaluationRequest(
        user_id=str(user_id),
        detail_id=str(quest_id),
        pseudocode=pseudocode,
        quest_title=quest_title,
        tail_answer=tail_answer,
        deep_answer=deep_answer,
        mode=EvaluationMode.OPTION2_GPTONLY,
    )

    try:
        result = evaluator.evaluate(eval_request)
        llm = result.llm_result

        # DB 자동 기록
        try:
            profile = UserProfile.objects.get(email=request.user.email)
            normalized_id = normalize_quest_id(quest_id)
            str_quest_id = str(quest_id)
            target_detail_id = (
                str_quest_id
                if (str_quest_id.startswith('unit') and '_' in str_quest_id)
                else f"unit01_{normalized_id.zfill(2)}"
            )
            save_user_problem_record(
                profile,
                target_detail_id,
                result.final_score,
                {'pseudocode': pseudocode, 'evaluation': result.feedback, 'is_auto_saved': True},
            )
        except Exception as save_error:
            logger.error(f"[Evaluate] Failed to auto-save: {save_error}")

        return Response(_build_success_response(result, llm, quest_id), status=status.HTTP_200_OK)

    except LowEffortError as e:
        logger.info(f"[Evaluate] LowEffort user={user_id}: {e.reason}")
        # [수정 2026-02-23] 무성의 입력(잘모르겠다 등)은 청사진 모드 진입용이므로 RDS에 0점 기록을 남기지 않음
        return Response(_build_low_effort_response(quest_id, e.reason), status=status.HTTP_200_OK)

    except LLMTimeoutError as e:
        logger.warning(f"[Evaluate] LLM timeout user={user_id}: {e}")
        return Response(
            {"error": "AI_TIMEOUT", "error_message": "AI 응답 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.", "retryable": True},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    except LLMUnavailableError as e:
        logger.error(f"[Evaluate] LLM unavailable: {e}")
        return Response(
            {"error": "LLM_UNAVAILABLE", "error_message": "AI 서비스에 연결할 수 없습니다.", "retryable": False},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    except Exception as e:
        logger.error(f"[Evaluate] Unexpected error user={user_id}: {e}", exc_info=True)
        return Response(
            {"error": "SERVER_ERROR", "error_message": "서버 내부 오류가 발생했습니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _build_success_response(result, llm, quest_id='1') -> dict:
    """정상 평가 완료 응답 — 영상 큐레이션 포함."""
    dimensions = result.feedback.get('dimensions', {})
    
    # [수정 2026-02-23] 모든 점수 필드 소수점 제거 및 정수화
    processed_dimensions = {}
    for dim, data in dimensions.items():
        processed_dimensions[dim] = {
            **data,
            'score': int(round(float(data.get('score', 0)))),
            'percentage': int(round(float(data.get('percentage', 0))))
        }

    return {
        'overall_score': int(result.final_score),
        'total_score_100': int(result.final_score),
        'grade': result.grade,
        'persona_name': result.persona,
        'one_line_review': result.feedback.get('summary', ''),
        'senior_advice': result.feedback.get('senior_advice', ''),
        'dimensions': processed_dimensions,
        'converted_python': (llm.converted_python if llm else '') or '# 변환 결과 없음',
        'python_feedback': (llm.python_feedback if llm else '') or '',
        'strengths': result.feedback.get('strengths', []),
        'weaknesses': result.feedback.get('improvements', []),
        'is_low_effort': False,
        'tail_question': result.tail_question,
        'deep_dive': result.deep_dive,
        'score_breakdown': result.score_breakdown,
        'metadata': {
            **result.metadata,
            'internal_reasoning': llm.internal_reasoning if llm else ''
        },
        'llm_available': result.metadata.get('llm_status') == 'SUCCESS',
        'recommended_videos': result.recommended_videos,
    }


def _build_low_effort_response(quest_id: str, reason: str) -> dict:
    from core.services.quest_resources import (
        get_quest_blueprint, 
        QUEST_RECOVERY_QUESTIONS,
        get_quest_videos
    )
    
    normalized_id = normalize_quest_id(quest_id)
    blueprint = get_quest_blueprint(normalized_id)
    recovery_q = QUEST_RECOVERY_QUESTIONS.get(normalized_id)

    return {
        'overall_score': 0,
        'total_score_100': 0,
        'grade': 'POOR',
        'persona_name': '성장의 씨앗을 품은 학생',
        'one_line_review': reason,
        'senior_advice': '설계 내용이 분석하기엔 너무 짧습니다. 아키텍처의 기초부터 차근차근 배워볼까요?',
        'dimensions': {
            dim: {'score': 0, 'max': max_val, 'percentage': 0, 'comment': '데이터 부족으로 분석이 생략되었습니다.'}
            for dim, max_val in {
                'design': 25, 'consistency': 20,
                'edgeCase': 15, 'abstraction': 15, 'implementation': 10,
            }.items()
        },
        'converted_python': '# 설계가 부실하여 변환을 생략합니다.\n# 아래 청사진을 참고해 다시 작성해 보세요.',
        'python_feedback': '청사진을 보고 논리 흐름을 처음부터 익혀보세요.',
        'strengths': [],
        'weaknesses': [reason],
        'is_low_effort': True,
        'blueprint_steps': blueprint,
        'tail_question': recovery_q,
        'deep_dive': None,
        'score_breakdown': {},
        'metadata': {'llm_status': 'SKIPPED_LOW_EFFORT'},
        'llm_available': False,
        'recommended_videos': get_quest_videos(quest_id).get('default', []),
    }
