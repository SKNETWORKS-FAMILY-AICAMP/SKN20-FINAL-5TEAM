import requests
from django.conf import settings

def search_youtube_videos(query, max_results=3):
    """
    YouTube Data API v3를 사용하여 영상을 검색합니다.
    (2026-02-14 수정: 실시간 영상 큐레이션 기능 추가)
    """
    api_key = getattr(settings, 'GOOGLE_API_KEY', None)
    if not api_key:
        print("YouTube API Error: GOOGLE_API_KEY not found in settings")
        return []

    url = "https://www.googleapis.com/youtube/v3/search"
    
    params = {
        'part': 'snippet',
        'q': query,
        'key': api_key,
        'maxResults': max_results,
        'type': 'video',
        'relevanceLanguage': 'ko',
        'videoEmbeddable': 'true'
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        videos = []
        for item in data.get('items', []):
            videos.append({
                'title': item['snippet']['title'],
                'videoId': item['id']['videoId'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'channelTitle': item['snippet']['channelTitle'],
                'description': item['snippet']['description'],
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            })
        return videos
    except Exception as e:
        print(f"YouTube API Error: {e}")
        return []
