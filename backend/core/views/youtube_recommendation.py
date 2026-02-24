from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_youtube_recommendations(request):
    """
    취약 지표(Weak Dimensions)를 기반으로 맞춤형 유튜브 영상을 추천합니다.
    (2026-02-23: quest_resources 서비스로 로직 통합 및 라이브 검색 강화)
    """
    try:
        dimensions = request.data.get('dimensions', {})
        quest_title = request.data.get('quest_title', '머신러닝 전처리')
        
        # 1. 통합 데이터 및 라이브 검색 로직 사용
        from core.services.quest_resources import get_recommended_videos_legacy
        from core.views.pseudocode.pseudocode_evaluation import normalize_quest_id
        
        quest_id = request.data.get('quest_id')
        if not quest_id:
            from core.services.quest_rubrics import extract_quest_id_from_title
            quest_id = extract_quest_id_from_title(quest_title)
        
        qid = normalize_quest_id(quest_id)
        
        # 취약 지표 기반 큐레이션 (정적 데이터 + 실시간 라이브 검색 폴백)
        videos = get_recommended_videos_legacy(
            quest_id=qid,
            dimensions=dimensions,
            max_count=3,
            quest_title=quest_title
        )
        
        # 프론트엔드 기대 형식으로 변환 (Thumbnail, videoId 등 필드 호환성 보장)
        formatted_videos = []
        for v in videos:
            formatted_videos.append({
                'title': v.get('title'),
                'url': v.get('url'),
                'thumbnail': v.get('thumbnail'),
                'videoId': v.get('videoId') or v.get('id'),
                'channelTitle': v.get('channel') or v.get('channelTitle', ''),
                'description': v.get('desc') or v.get('description', '')
            })

        print(f"[YouTube recommendations] Unified service returned {len(formatted_videos)} videos for Quest {qid}")
        return Response({
            'query': f"Quest {qid} Context-Aware Search",
            'videos': formatted_videos
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"[YouTube recommendation Error] {e}")
        return Response({'videos': []}, status=status.HTTP_200_OK)
