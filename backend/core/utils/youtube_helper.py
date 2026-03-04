"""
youtube_helper.py
수정일: 2026-03-04

[변경 사항]
- generate_llm_search_queries(): LLM으로 취약 지표 + 퀘스트 맥락 기반 검색어 3개 생성
- search_youtube_videos(): 기존 유지
- filter_valid_videos(): 기존 유지
"""

import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


# ============================================================================
# LLM 기반 검색어 생성
# ============================================================================

def generate_llm_search_queries(quest_title: str, weak_dimensions: list, pseudocode: str = "") -> list:
    """
    LLM(GPT)에게 취약 지표 + 퀘스트 맥락을 주고
    YouTube 검색어 3개를 생성하게 합니다.

    Args:
        quest_title: 퀘스트 제목 (예: "데이터 누수 방어 시스템 설계")
        weak_dimensions: 취약한 차원 리스트 (예: ["consistency", "edgeCase"])
        pseudocode: 사용자가 작성한 의사코드 (맥락 보강용, 선택)

    Returns:
        검색어 리스트 (예: ["Data Leakage sklearn pipeline tutorial", ...])
    """
    try:
        import openai
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key:
            logger.warning("[LLM Search] OPENAI_API_KEY 없음 → 폴백 쿼리 사용")
            return _fallback_queries(quest_title, weak_dimensions)

        client = openai.OpenAI(api_key=api_key)

        dim_labels = {
            'design':         '설계력 (ML 파이프라인 구조화)',
            'consistency':    '정합성 (fit/transform 분리, 데이터 누수 방지)',
            'abstraction':    '추상화 (모듈화, 재사용 구조)',
            'edgeCase':       '예외처리 (결측치, 이상치, 데이터 드리프트)',
            'implementation': '구현력 (sklearn, pandas 실무 코드)',
        }
        weak_labels = [dim_labels.get(d, d) for d in weak_dimensions[:2]]  # 상위 2개만

        pseudo_snippet = pseudocode[:300] if pseudocode else "(미제공)"

        prompt = f"""당신은 ML 교육 전문가입니다.
학생이 아래 퀘스트에서 취약한 부분을 보완할 수 있는 YouTube 검색어 3개를 생성하세요.

[퀘스트]: {quest_title}
[취약 지표]: {', '.join(weak_labels) if weak_labels else '전반적인 ML 개념'}
[학생 의사코드 요약]: {pseudo_snippet}

규칙:
- 각 검색어는 실제 YouTube에서 좋은 교육 영상이 나올 법한 영어 또는 한국어 키워드
- 너무 추상적이지 않게, 구체적인 라이브러리/기법 이름 포함
- JSON 배열만 반환 (다른 텍스트 금지)

예시 출력:
["Data Leakage sklearn pipeline tutorial", "fit transform train test split python", "StandardScaler cross validation explained"]
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=200,
            timeout=10,
        )

        raw = response.choices[0].message.content.strip()

        # JSON 파싱
        import json, re
        match = re.search(r'\[.*?\]', raw, re.DOTALL)
        if match:
            queries = json.loads(match.group(0))
            if isinstance(queries, list) and len(queries) > 0:
                logger.info(f"[LLM Search] 생성된 쿼리: {queries}")
                return [str(q) for q in queries[:3]]

    except Exception as e:
        logger.warning(f"[LLM Search] 쿼리 생성 실패: {e}")

    return _fallback_queries(quest_title, weak_dimensions)


def _fallback_queries(quest_title: str, weak_dimensions: list) -> list:
    """LLM 실패 시 규칙 기반 폴백 쿼리"""
    base_map = {
        'consistency':    'fit transform data leakage prevention sklearn',
        'design':         'machine learning pipeline design best practices',
        'edgeCase':       'handling missing values outliers machine learning',
        'abstraction':    'clean code machine learning modular design',
        'implementation': 'sklearn pandas machine learning tutorial step by step',
    }
    queries = []
    for dim in weak_dimensions[:2]:
        q = base_map.get(dim)
        if q:
            queries.append(q)

    # 퀘스트 타이틀 기반 보완
    title_lower = quest_title.lower()
    if '누수' in title_lower or 'leakage' in title_lower:
        queries.append('data leakage machine learning explained')
    elif '과적합' in title_lower or 'regularization' in title_lower:
        queries.append('ridge lasso regularization overfitting python')
    elif '불균형' in title_lower or 'imbalanced' in title_lower:
        queries.append('imbalanced dataset SMOTE classification python')
    elif '피처' in title_lower or 'feature' in title_lower:
        queries.append('feature engineering selection importance python')
    elif '하이퍼' in title_lower or 'hyperparameter' in title_lower:
        queries.append('hyperparameter tuning GridSearchCV optuna python')
    elif '해석' in title_lower or 'explainability' in title_lower:
        queries.append('SHAP LIME explainable AI model interpretation')
    else:
        queries.append('machine learning tutorial python scikit-learn')

    return list(dict.fromkeys(queries))[:3]  # 중복 제거 후 최대 3개


# ============================================================================
# YouTube Data API v3 검색
# ============================================================================

def search_youtube_videos(query, max_results=3):
    """
    YouTube Data API v3를 사용하여 영상을 검색합니다.
    """
    api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    if not api_key:
        logger.warning("[YouTube] YOUTUBE_API_KEY 없음")
        return []

    url = "https://www.googleapis.com/youtube/v3/search"

    def execute_search(search_query):
        params = {
            'part': 'snippet',
            'q': search_query,
            'key': api_key,
            'maxResults': max_results,
            'type': 'video',
            'videoEmbeddable': 'true',
            'relevanceLanguage': 'ko',   # 한국어/영어 혼합 결과
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('items', [])
        except Exception as e:
            logger.warning(f"[YouTube] 검색 실패 '{search_query}': {e}")
            return []

    # 1차: 교육 키워드 보강
    items = execute_search(f"{query} tutorial explained")
    # 2차: 원본 쿼리로 재시도
    if not items:
        items = execute_search(query)
    # 3차: 쿼리 축소
    if not items and len(query.split()) > 2:
        items = execute_search(' '.join(query.split()[:3]))

    videos = []
    for item in items:
        snippet = item.get('snippet', {})
        video_id = item.get('id', {}).get('videoId', '')
        thumbnails = snippet.get('thumbnails', {})

        thumbnail_url = (
            thumbnails.get('medium', {}).get('url')
            or thumbnails.get('default', {}).get('url')
            or (f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg' if video_id else '')
        )

        videos.append({
            'videoId':      video_id,
            'id':           video_id,
            'title':        snippet.get('title', ''),
            'channelTitle': snippet.get('channelTitle', ''),
            'description':  snippet.get('description', ''),
            'thumbnail':    thumbnail_url,
            'url':          f'https://www.youtube.com/watch?v={video_id}' if video_id else '#',
        })

    return videos


def search_youtube_multi_query(queries: list, max_per_query: int = 2) -> list:
    """
    여러 검색어로 YouTube를 검색하여 중복 없이 합칩니다.

    Args:
        queries: 검색어 리스트 (최대 3개 권장)
        max_per_query: 쿼리당 최대 결과 수

    Returns:
        중복 제거된 영상 리스트
    """
    seen_ids = set()
    results = []

    for query in queries:
        if len(results) >= 3:
            break
        videos = search_youtube_videos(query, max_results=max_per_query)
        for v in videos:
            vid_id = v.get('videoId') or v.get('id', '')
            if vid_id and vid_id not in seen_ids:
                seen_ids.add(vid_id)
                results.append(v)

    logger.info(f"[YouTube Multi-Query] {len(queries)}개 쿼리 → {len(results)}개 영상 수집")
    return results


# ============================================================================
# 영상 유효성 검증 (캐시 적용)
# ============================================================================

def filter_valid_videos(videos: list) -> list:
    """
    YouTube Videos API로 실제 공개된 영상만 필터링합니다.
    API 실패 시 원본 리스트를 그대로 반환합니다.
    """
    api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    if not api_key or not videos:
        return videos

    video_ids = [v.get('videoId') or v.get('id', '') for v in videos]
    video_ids = [vid for vid in video_ids if vid]
    if not video_ids:
        return videos

    cache_key = f"yt_valid_{'_'.join(sorted(video_ids))}"
    cached = cache.get(cache_key)

    if cached is not None:
        valid_ids = cached
    else:
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {'part': 'id,status', 'id': ','.join(video_ids), 'key': api_key}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            valid_ids = {
                item['id'] for item in data.get('items', [])
                if item.get('status', {}).get('privacyStatus') == 'public'
            }
            cache.set(cache_key, valid_ids, timeout=60 * 60 * 24)
            logger.info(f"[YouTube Validation] {len(valid_ids)}/{len(video_ids)} 공개 영상")
        except Exception as e:
            logger.warning(f"[YouTube Validation] API 실패, 원본 반환: {e}")
            return videos  # 실패 시 원본 그대로

    result = [v for v in videos if (v.get('videoId') or v.get('id', '')) in valid_ids]

    # 필터 후 아무것도 없으면 원본 반환 (전체 제거 방지)
    return result if result else videos
