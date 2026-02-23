import requests
from django.conf import settings
from django.core.cache import cache

def search_youtube_videos(query, max_results=3):
    """
    YouTube Data API v3를 사용하여 영상을 검색합니다.
    (2026-02-14 수정: 실시간 영상 큐레이션 기능 추가)
    """
    api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    if not api_key:
        print("YouTube API Error: YOUTUBE_API_KEY not found. Please check your .env or settings.")
        return []

    url = "https://www.googleapis.com/youtube/v3/search"
    
    def execute_search(search_query):
        params = {
            'part': 'snippet',
            'q': search_query,
            'key': api_key,
            'maxResults': max_results,
            'type': 'video',
            'videoEmbeddable': 'true'
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('items', [])
        except Exception as e:
            print(f"YouTube API Request Failed for query '{search_query}': {e}")
            return []

    # [2026-02-23] 검색 품질 최적화: 교육용 영상 위주로 검색되도록 키워드 보강
    educational_keywords = "tutorial theory explained 실무 강의"
    optimized_query = f"{query} {educational_keywords}"
    
    # 1차 검색 시도
    items = execute_search(optimized_query)

    # 1차 검색 결과가 없으면 쿼리 단순화 후 2차 시도 (Retry Logic)
    if not items:
        # 교육용 키워드 제거하고 원본 쿼리만으로 시도
        items = execute_search(query)
        
    if not items and len(query.split()) > 1:
        simplified_query = ' '.join(query.split()[:2])
        print(f"YouTube Search: No results for '{query}'. Retrying with '{simplified_query}'...")
        items = execute_search(simplified_query)

    videos = []
    for item in items:
        snippet = item.get('snippet', {})
        thumbnails = snippet.get('thumbnails', {})
        thumbnail_url = thumbnails.get('medium', {}).get('url') or \
                       thumbnails.get('default', {}).get('url') or ""
        
        # [2026-02-23] 섬네일 폴백 강화
        fallback_thumb = "https://coduck-assets.s3.ap-northeast-2.amazonaws.com/images/video_fallback.png"
        final_thumbnail = thumbnail_url if thumbnail_url and "hqdefault_live.jpg" not in thumbnail_url else (
            f"https://img.youtube.com/vi/{item.get('id', {}).get('videoId')}/mqdefault.jpg" if item.get('id', {}).get('videoId') else fallback_thumb
        )

        videos.append({
            'title': snippet.get('title', 'No Title'),
            'videoId': item.get('id', {}).get('videoId'),
            'thumbnail': final_thumbnail,
            'channelTitle': snippet.get('channelTitle', 'Unknown Channel'),
            'description': snippet.get('description', ''),
            'url': f"https://www.youtube.com/watch?v={item.get('id', {}).get('videoId', '')}"
        })
        
    return videos


def filter_valid_videos(videos: list) -> list:
    """
    YouTube Videos API를 사용하여 실제로 존재하는(공개된) 영상만 반환합니다.
    존재하지 않거나 삭제/비공개된 영상은 제거됩니다.
    결과는 캐싱하여 API 쿼터 절약.
    """
    api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    if not api_key or not videos:
        return videos

    # videoId 목록 추출
    video_ids = [v.get('videoId') or v.get('id', '') for v in videos]
    video_ids = [vid for vid in video_ids if vid]

    if not video_ids:
        return videos

    # 캐시 확인 (24시간 유지)
    cache_key = f"yt_valid_{'_'.join(sorted(video_ids))}"
    cached = cache.get(cache_key)
    if cached is not None:
        valid_ids = cached
    else:
        # YouTube Videos API 호출 (한 번에 최대 50개)
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'id,status',
            'id': ','.join(video_ids),
            'key': api_key,
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            # 실제로 API 응답에 포함된 id = 공개 영상
            valid_ids = {
                item['id'] for item in data.get('items', [])
                if item.get('status', {}).get('privacyStatus') == 'public'
            }
            # 응답에 아예 없는 id = 삭제된 영상
            cache.set(cache_key, valid_ids, timeout=60 * 60 * 24)  # 24시간
            print(f"[YouTube Validation] {len(valid_ids)}/{len(video_ids)} videos are valid")
        except Exception as e:
            print(f"[YouTube Validation Error] {e}")
            # 검증 실패 시 그냥 통과 (API 에러로 멀쩡한 영상 제거 방지)
            return videos

    # 유효한 영상만 필터링
    result = []
    for v in videos:
        vid_id = v.get('videoId') or v.get('id', '')
        if vid_id in valid_ids:
            result.append(v)
        else:
            print(f"[YouTube Validation] Removed invalid video: {vid_id} — '{v.get('title', '?')}'")

    return result
