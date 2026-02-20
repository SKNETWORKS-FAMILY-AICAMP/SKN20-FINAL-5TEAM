from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from core.utils.youtube_helper import search_youtube_videos

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_youtube_recommendations(request):
    """
    취약 지표(Weak Dimensions)를 기반으로 맞춤형 유튜브 영상을 추천합니다.
    최종 리포트 생성 시점에 호출됩니다.
    """
    try:
        dimensions = request.data.get('dimensions', {})
        quest_title = request.data.get('quest_title', '머신러닝 전처리')
        
        # 1. 큐레이션 매핑 확인 (Prioritized)
        from core.utils.curated_videos import QUEST_VIDEO_MAP
        
        # 점수가 있는 지표 중 가장 낮은 것 추출
        valid_dims = {}
        for k, v in dimensions.items():
            if isinstance(v, dict) and 'percentage' in v:
                valid_dims[k] = v['percentage']
            elif isinstance(v, dict) and 'score' in v:
                valid_dims[k] = v['score']
        
        weakest_dim = None
        if valid_dims:
            weakest_dim = min(valid_dims.items(), key=lambda x: x[1])[0]

        # 큐레이션된 영상이 있는지 확인
        if quest_title in QUEST_VIDEO_MAP and weakest_dim in QUEST_VIDEO_MAP[quest_title]:
            curated_video = QUEST_VIDEO_MAP[quest_title][weakest_dim]
            print(f"[YouTube recommendations] Found curated video for {quest_title} -> {weakest_dim}")
            return Response({
                'query': f"Curated: {quest_title} - {weakest_dim}",
                'videos': [curated_video] # 리스트 형태로 반환
            }, status=status.HTTP_200_OK)

        # 2. 폴백: 기존 검색 로직
        # 지표별 전문 검색어 매핑 (검색 적중률 향상을 위해 키워드 중심으로 최적화)
        CURATION_MAP = {
            'design': '머신러닝 파이프라인 설계',
            'edgeCase': 'Data Drift MLOps',
            'abstraction': 'Computational Thinking Python',
            'implementation': 'Scikit-learn pipeline tutorial',
            'consistency': 'Data Leakage Machine Learning'
        }
        
        query = None
        if weakest_dim:
            query = CURATION_MAP.get(weakest_dim)
        
        # 폴백 쿼리
        if not query:
            query = f"머신러닝 {quest_title} 설계 방법"
            
        print(f"[YouTube recommendations] Fetching for query: {query}")
        videos = search_youtube_videos(query, max_results=3)
        
        return Response({
            'query': query,
            'videos': videos
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"[YouTube recommendation Error] {e}")
        return Response({'videos': []}, status=status.HTTP_200_OK)
