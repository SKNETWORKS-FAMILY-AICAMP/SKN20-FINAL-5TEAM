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
# Quest × 취약 차원 기반 YouTube 큐레이션 (통합 리소스 서비스 사용)
# [2026-02-21 개편] 구조 통일 + 차원별 우선순위 적용
# ============================================================================
from core.services.quest_resources import (
    QUEST_VIDEOS,
    get_dimension_priority,
    get_quest_videos,
)


def _get_recommended_videos(quest_id: str, dimensions: dict, max_count: int = 3) -> list:
    """Quest ID × 취약 차원 기반 YouTube 영상 추천 목록 반환 (프론트 호환 포맷).
    
    [2026-02-21] 개선사항:
    1. 퀘스트별 차원 우선순위 반영
    2. 구조 통일 (모든 차원이 [list])
    3. YouTube Data API 검증 + 폴백 검색
    """
    try:
        qid = int(quest_id)
    except (ValueError, TypeError):
        qid = 1
    
    # 퀘스트별 영상 풀 가져오기
    pool = get_quest_videos(quest_id)
    
    # 퀘스트별 차원 우선순위 가져오기
    priority = get_dimension_priority(quest_id)

    # 취약 차원 순 정렬 (낮은 percentage 우선)
    dim_ratios = []
    for dim in priority:
        d = dimensions.get(dim, {})
        pct = d.get('percentage', 100) if isinstance(d, dict) else 100
        dim_ratios.append((dim, pct))
    dim_ratios.sort(key=lambda x: x[1])

    candidates = []
    used_ids = set()

    # 취약 차원 순으로 선택 (이제 모든 차원이 [list] 구조)
    for dim, _ in dim_ratios:
        if len(candidates) >= max_count:
            break
        videos = pool.get(dim, [])
        if not isinstance(videos, list):
            videos = [videos]
        for video in videos:
            if len(candidates) >= max_count:
                break
            if video['id'] not in used_ids:
                candidates.append({**video, '_dim': dim})
                used_ids.add(video['id'])

    # default로 보완
    default_videos = pool.get('default', [])
    if not isinstance(default_videos, list):
        default_videos = [default_videos]
    for video in default_videos:
        if len(candidates) >= max_count:
            break
        if video['id'] not in used_ids:
            candidates.append({**video, '_dim': 'default'})
            used_ids.add(video['id'])

    # YouTube Data API로 영상 존재 검증 + 폴백 검색
    result = _verify_and_fallback(candidates)

    return [
        {
            'id': v['id'],
            'videoId': v['id'],
            'title': v['title'],
            'channelTitle': v.get('channel', v.get('channelTitle', '')),
            'thumbnail': f"https://img.youtube.com/vi/{v['id']}/mqdefault.jpg",
            'url': f"https://www.youtube.com/watch?v={v['id']}",
            'description': v.get('desc', v.get('description', '')),
        }
        for v in result
    ]


def _verify_and_fallback(candidates: list) -> list:
    """YouTube Data API로 영상 ID 검증. 죽은 링크는 검색으로 대체.
    
    API 키가 없으면 검증 없이 그대로 반환.
    """
    from django.conf import settings
    api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    if not api_key:
        # API 키 없으면 검증 불가 → 하드코딩 그대로
        return candidates

    import requests as http_requests
    
    # 일괄 검증: videos.list API (1회 호출로 여러 개 검증)
    video_ids = [c['id'] for c in candidates]
    try:
        resp = http_requests.get(
            'https://www.googleapis.com/youtube/v3/videos',
            params={
                'part': 'id,snippet',
                'id': ','.join(video_ids),
                'key': api_key,
            },
            timeout=5,
        )
        if resp.status_code != 200:
            logger.warning(f"[YouTube API] 검증 실패 (HTTP {resp.status_code})")
            return candidates
        
        data = resp.json()
        valid_ids = {item['id'] for item in data.get('items', [])}
    except Exception as e:
        logger.warning(f"[YouTube API] 검증 중 예외: {e}")
        return candidates

    # 죽은 링크 대체
    result = []
    from core.utils.youtube_helper import search_youtube_videos
    
    for candidate in candidates:
        if candidate['id'] in valid_ids:
            # 존재 확인됨 → 실제 제목으로 업데이트
            api_item = next((item for item in data['items'] if item['id'] == candidate['id']), None)
            if api_item:
                candidate['title'] = api_item['snippet'].get('title', candidate['title'])
                candidate['channel'] = api_item['snippet'].get('channelTitle', candidate.get('channel', ''))
            result.append(candidate)
        else:
            # 죽은 링크 → 검색으로 대체
            logger.info(f"[YouTube] 죽은 링크 감지: {candidate['id']} ({candidate['title']})")
            search_query = candidate['title'].split('(')[0].strip()  # "Ridge & Lasso (StatQuest)" → "Ridge & Lasso"
            replacements = search_youtube_videos(search_query, max_results=1)
            if replacements:
                r = replacements[0]
                result.append({
                    'id': r['videoId'],
                    'title': r['title'],
                    'channel': r.get('channelTitle', ''),
                    'desc': r.get('description', ''),
                })
                logger.info(f"[YouTube] 대체 영상 찾음: {r['videoId']} ({r['title']})")
            else:
                # 검색도 실패 → 제외 (죽은 링크 제공하지 않음)
                logger.warning(f"[YouTube] 대체 영상도 없음: {search_query}")
    
    return result


# ============================================================================
# Quest ID 정규화
# ============================================================================
def normalize_quest_id(quest_id):
    if not quest_id:
        return "1"
    q_str = str(quest_id).upper()
    if q_str.startswith('UNIT01'):
        try:
            return str(int(q_str[6:]))
        except Exception:
            pass
    elif q_str.startswith('QUEST_'):
        try:
            return str(int(q_str[6:]))
        except Exception:
            pass
    nums = re.findall(r'\d+', q_str)
    return nums[0] if nums else q_str


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
                profile, target_detail_id, 0,
                {'pseudocode': pseudocode, 'reason': e.reason, 'is_low_effort': True, 'is_auto_saved': True},
            )
        except Exception as save_error:
            logger.error(f"[Evaluate] Failed to save low-effort: {save_error}")
        return Response(_build_low_effort_response(e.reason), status=status.HTTP_200_OK)

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
    is_llm_success = result.metadata.get('llm_status') == 'SUCCESS'

    return {
        'overall_score': result.final_score,
        'total_score_100': result.final_score,
        'grade': result.grade,
        'persona_name': result.persona,
        'one_line_review': result.feedback.get('summary', ''),
        'senior_advice': result.feedback.get('senior_advice', ''),
        'dimensions': dimensions,
        'converted_python': (llm.converted_python if llm else '') or '# 변환 결과 없음',
        'python_feedback': (llm.python_feedback if llm else '') or '',
        'strengths': result.feedback.get('strengths', []),
        'weaknesses': result.feedback.get('improvements', []),
        'is_low_effort': False,
        'tail_question': result.tail_question,
        'deep_dive': result.deep_dive,
        'score_breakdown': result.score_breakdown,
        'metadata': result.metadata,
        # ── 영상 큐레이션: 백엔드에서 항상 제공 ──────────────────────
        # 프론트는 이 값이 있으면 사용, 없으면 learningResources.js 폴백
        'recommended_videos': _get_recommended_videos(quest_id, dimensions),
        'llm_available': is_llm_success,
    }


def _build_low_effort_response(reason: str) -> dict:
    return {
        'overall_score': 0,
        'total_score_100': 0,
        'grade': 'POOR',
        'persona_name': '성장의 씨앗을 품은 학생',
        'one_line_review': reason,
        'senior_advice': '',
        'dimensions': {
            dim: {'score': 0, 'max': max_val, 'percentage': 0, 'comment': '설명이 부족하여 분석할 수 없습니다.'}
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
        'tail_question': None,
        'deep_dive': None,
        'score_breakdown': {},
        'metadata': {'llm_status': 'SKIPPED_LOW_EFFORT'},
        'recommended_videos': [],
        'llm_available': False,
    }
