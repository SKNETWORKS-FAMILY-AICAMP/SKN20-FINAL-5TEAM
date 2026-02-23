import requests
from django.conf import settings

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
