"""유튜브 추천 큐레이션 기능을 테스트하는 스크립트 (1회성 유틸리티)."""
import sys
import os

# Add the backend root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Mock django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from core.services.quest_resources import get_recommended_videos_legacy

def test_youtube_curation():
    print("Testing YouTube Curation with Live Search Fallback...")
    
    # Use a quest and dimension that might not have enough static videos
    # Or just test if the live search is triggered by looking at the _dim field
    
    quest_id = "99" # Non-existent quest to force fallback/live search
    quest_title = "과적합 방어 정규화 시스템 설계"
    dimensions = {
        'design': {'percentage': 30}, # Very low score to prioritize this
        'consistency': {'percentage': 80},
        'abstraction': {'percentage': 90},
        'edgeCase': {'percentage': 90},
        'implementation': {'percentage': 90}
    }
    
    print(f"Requesting videos for Quest {quest_id} with weakest dim 'design'...")
    videos = get_recommended_videos_legacy(quest_id, dimensions, max_count=3, quest_title=quest_title)
    
    print(f"Retrieved {len(videos)} videos:")
    for v in videos:
        print(f"- [{v.get('_dim')}] {v.get('title')} (ID: {v.get('id') or v.get('videoId')})")
        # Check if any video has 'live_' prefix in _dim
        if str(v.get('_dim')).startswith('live_'):
            print("  ✅ Live search fallback was triggered!")
    
    if len(videos) > 0:
        print("\nCuration Test Passed!")
    else:
        print("\nCuration Test Failed: No videos returned.")

if __name__ == "__main__":
    test_youtube_curation()
