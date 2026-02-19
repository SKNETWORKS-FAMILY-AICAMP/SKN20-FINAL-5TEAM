from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from core.utils.youtube_helper import search_youtube_videos

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_youtube_recommendations(request):
    """
    취약 지표(Weak Dimensions)를 기반으로 맞춤형 유튜브 영상을 추천합니다.
    최종 리포트 생성 시점에 호출됩니다.
    """
    try:
        dimensions = request.data.get('dimensions', {})
        quest_title = request.data.get('quest_title', '머신러닝 전처리')
        
        # 지표별 전문 검색어 매핑 (검색 적중률 향상을 위해 키워드 중심으로 최적화)
        CURATION_MAP = {
            'design': '머신러닝 파이프라인 설계',
            'edgeCase': 'Data Drift MLOps',
            'abstraction': 'Computational Thinking Python',
            'implementation': 'Scikit-learn pipeline tutorial',
            'consistency': 'Data Leakage Machine Learning'
        }
        
        # 점수가 있는 지표 중 가장 낮은 것 추출
        # dimensions가 { design: { score: 90 }, edgeCase: { score: 70 } ... } 형태라고 가정
        valid_dims = {}
        for k, v in dimensions.items():
            if isinstance(v, dict) and 'percentage' in v:
                valid_dims[k] = v['percentage']
            elif isinstance(v, dict) and 'score' in v:
                valid_dims[k] = v['score']
        
        query = None
        if valid_dims:
            weakest = min(valid_dims.items(), key=lambda x: x[1])[0]
            query = CURATION_MAP.get(weakest)
        
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
