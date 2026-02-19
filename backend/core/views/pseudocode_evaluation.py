"""
의사코드 5차원 평가 뷰
수정일: 2026-02-19

[변경 사항]
- 에러 타입별 HTTP 상태 코드 분리 (500을 200으로 숨기던 코드 제거)
  · LowEffortError  → 200 (정상 케이스, 클라이언트가 안내 표시)
  · LLMTimeoutError → 503 (클라이언트가 재시도 버튼 표시)
  · 그 외 예외      → 500 (진짜 서버 오류)
- 프론트 호환 응답 포맷 유지
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.services.pseudocode_evaluator import (
    PseudocodeEvaluator,
    EvaluationRequest,
    EvaluationMode,
    LowEffortError,
    LLMTimeoutError,
    LLMUnavailableError,
)

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def evaluate_pseudocode_5d(request):
    """
    [POST] /api/core/pseudocode/evaluate-5d/
    5차원 의사코드 평가.

    Response:
        200 OK              - 정상 평가 완료 또는 low_effort 감지
        400 Bad Request     - 필수 파라미터 누락
        503 Service Unavail - LLM 타임아웃 (재시도 권장)
        500 Server Error    - 예상치 못한 서버 오류
    """
    user_id = request.user.id
    quest_id = request.data.get('quest_id', '1')
    quest_title = request.data.get('quest_title', '데이터 전처리 미션')
    pseudocode = request.data.get('pseudocode', '').strip()

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
        mode=EvaluationMode.OPTION2_GPTONLY,
    )

    # ── 정상 평가 ────────────────────────────────────────────────
    try:
        result = evaluator.evaluate(eval_request)
        llm = result.llm_result

        return Response(_build_success_response(result, llm), status=status.HTTP_200_OK)

    # ── 무성의 입력 (정상 케이스) ─────────────────────────────────
    except LowEffortError as e:
        logger.info(f"[Evaluate] LowEffort detected for user={user_id}: {e.reason}")
        return Response(
            _build_low_effort_response(e.reason),
            status=status.HTTP_200_OK,
        )

    # ── LLM 타임아웃 (클라이언트 재시도 가능) ─────────────────────
    except LLMTimeoutError as e:
        logger.warning(f"[Evaluate] LLM timeout for user={user_id}: {e}")
        return Response(
            {
                "error": "AI_TIMEOUT",
                "error_message": "AI 응답 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.",
                "retryable": True,
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # ── LLM 사용 불가 (서버 설정 문제) ────────────────────────────
    except LLMUnavailableError as e:
        logger.error(f"[Evaluate] LLM unavailable: {e}")
        return Response(
            {
                "error": "LLM_UNAVAILABLE",
                "error_message": "AI 서비스에 연결할 수 없습니다. 관리자에게 문의해 주세요.",
                "retryable": False,
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # ── 예상치 못한 서버 오류 ─────────────────────────────────────
    except Exception as e:
        logger.error(f"[Evaluate] Unexpected error for user={user_id}: {e}", exc_info=True)
        return Response(
            {
                "error": "SERVER_ERROR",
                "error_message": "서버 내부 오류가 발생했습니다.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _build_success_response(result, llm) -> dict:
    """정상 평가 완료 응답"""
    return {
        'overall_score': result.final_score,
        'total_score_100': result.final_score,
        'grade': result.grade,
        'persona_name': result.persona,
        'one_line_review': result.feedback.get('summary', ''),
        'dimensions': result.feedback.get('dimensions', {}),
        'converted_python': (llm.converted_python if llm else '') or '# 변환 결과 없음',
        'python_feedback': (llm.python_feedback if llm else '') or '',
        'strengths': result.feedback.get('strengths', []),
        'weaknesses': result.feedback.get('improvements', []),
        'is_low_effort': False,
        'tail_question': result.tail_question,
        'deep_dive': result.deep_dive,
        'score_breakdown': result.score_breakdown,
        'metadata': result.metadata,
    }


def _build_low_effort_response(reason: str) -> dict:
    """무성의 입력 감지 응답 — 청사진은 제공, 점수는 0"""
    return {
        'overall_score': 0,
        'total_score_100': 0,
        'grade': 'POOR',
        'persona_name': '성장의 씨앗을 품은 학생',
        'one_line_review': reason,
        'dimensions': {
            dim: {'score': 0, 'max': max_val}
            for dim, max_val in {
                'design': 25, 'consistency': 25,
                'edge_case': 20, 'abstraction': 15, 'implementation': 15,
            }.items()
        },
        'converted_python': '# 설계가 부실하여 변환을 생략합니다.\n# 아래 청사진을 참고해 다시 작성해 보세요.',
        'python_feedback': '청사진을 보고 논리 흐름을 처음부터 익혀보세요.',
        'strengths': [],
        'weaknesses': [reason],
        'is_low_effort': True,
        'tail_question': None,
        'deep_dive': None,
        'score_breakdown': {},
        'metadata': {'llm_status': 'SKIPPED_LOW_EFFORT'},
    }
