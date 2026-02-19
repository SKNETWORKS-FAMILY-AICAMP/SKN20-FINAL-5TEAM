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

    # 1차 검색 시도
    items = execute_search(query)

    # 1차 검색 결과가 없으면 쿼리 단순화 후 2차 시도 (Retry Logic)
    if not items and len(query.split()) > 1:
        simplified_query = ' '.join(query.split()[:2])  # 앞의 2단어만 추출 (예: "MLOps Data Drift..." -> "MLOps Data")
        print(f"YouTube Search: No results for '{query}'. Retrying with '{simplified_query}'...")
        items = execute_search(simplified_query)

    videos = []
    for item in items:
        snippet = item.get('snippet', {})
        thumbnails = snippet.get('thumbnails', {})
        thumbnail_url = thumbnails.get('medium', {}).get('url') or \
                       thumbnails.get('default', {}).get('url') or ""
        
        videos.append({
            'title': snippet.get('title', 'No Title'),
            'videoId': item.get('id', {}).get('videoId'),
            'thumbnail': thumbnail_url,
            'channelTitle': snippet.get('channelTitle', 'Unknown Channel'),
            'description': snippet.get('description', ''),
            'url': f"https://www.youtube.com/watch?v={item.get('id', {}).get('videoId', '')}"
        })
        
    return videos
