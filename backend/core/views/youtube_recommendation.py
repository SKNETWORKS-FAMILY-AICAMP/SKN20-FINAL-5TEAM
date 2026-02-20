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
        # [2026-02-21] core.utils.curated_videos 삭제에 따른 통합 리소스(QUEST_VIDEOS)로 변경
        from core.services.quest_resources import QUEST_VIDEOS
        from core.views.pseudocode_evaluation import normalize_quest_id
        
        # quest_id가 있으면 우선 사용, 없으면 타이틀에서 추출 시도
        quest_id = request.data.get('quest_id')
        if not quest_id:
            from core.services.quest_rubrics import extract_quest_id_from_title
            quest_id = extract_quest_id_from_title(quest_title)
        
        qid = int(normalize_quest_id(quest_id))
        
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

        # 큐레이션된 영상이 있는지 확인 (Quest ID 기반)
        if qid in QUEST_VIDEOS:
            target_video = QUEST_VIDEOS[qid].get(str(weakest_dim))
            if not target_video:
                # 해당 차원 영상 없으면 default의 첫 번째 영상 사용
                defaults = QUEST_VIDEOS[qid].get('default', [])
                if defaults:
                    target_video = defaults[0]

            if target_video:
                curated_video = {
                    'title': target_video['title'],
                    'url': f"https://www.youtube.com/watch?v={target_video['id']}",
                    'thumbnail': f"https://img.youtube.com/vi/{target_video['id']}/hqdefault.jpg",
                    'videoId': target_video['id'],
                    'channelTitle': target_video.get('channel', ''),
                    'description': target_video.get('desc', '')
                }
                
                print(f"[YouTube recommendations] Found curated video for Quest {qid} -> {weakest_dim}")
                return Response({
                    'query': f"Curated: Quest {qid} - {weakest_dim}",
                    'videos': [curated_video]
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
