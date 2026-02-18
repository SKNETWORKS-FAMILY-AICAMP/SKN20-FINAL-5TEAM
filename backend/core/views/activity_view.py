# 수정일: 2026-02-06
# 수정내용: 아바타, 진행도, 리더보드 관련 API 뷰 구현

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum, Count, Max
from core.models import UserActivity, UserSolvedProblem, UserProgress, UserAvatar, Practice, PracticeDetail
from django.shortcuts import get_object_or_404
from core.nanobanana_utils import generate_nano_banana_avatar 
# [2026-02-18 상세] Unit 1/Unit 3 기록 저장 로직을 공통화하여 관리하는 서비스 추가
from core.services.activity_service import save_user_problem_record

from django.core.paginator import Paginator

class LeaderboardView(APIView):
    """
    상위 랭커 목록 및 현재 사용자의 순위 정보 반환 (페이징 지원)
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # 전체 랭킹 조회
        all_activities = UserActivity.objects.select_related('user', 'active_avatar').order_by('-total_points')
        
        # [수정일: 2026-02-09] 페이징 처리 (페이지당 5명)
        page_number = request.query_params.get('page', 1)
        page_size = 5
        paginator = Paginator(all_activities, page_size)
        
        try:
            page_obj = paginator.get_page(page_number)
        except Exception:
            return Response({"error": "Invalid page number"}, status=status.HTTP_400_BAD_REQUEST)

        leaderboard_data = []
        # 페이징 시작 번호를 기반으로 절대 순위 계산
        start_rank = (page_obj.number - 1) * page_size + 1
        
        for i, activity in enumerate(page_obj, start_rank):
            # [수정일: 2026-02-09] 닉네임 폴백 로직 강화
            user_nickname = getattr(activity.user, 'user_nickname', None) or str(activity.user.username)
            
            avatar_url = None
            if activity.active_avatar and activity.active_avatar.image_url:
                avatar_url = activity.active_avatar.image_url

            leaderboard_data.append({
                'id': activity.user.id,
                'rank': i,
                'nickname': user_nickname,
                'points': activity.total_points,
                'current_grade': activity.current_rank,
                'avatar_url': avatar_url
            })
            
        return Response({
            'leaderboard': leaderboard_data,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }, status=status.HTTP_200_OK)

class UserProgressView(APIView):
    """
    사용자의 전체 학습 진행도 및 특정 유닛 진행 상태 조회
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # UserProfile 조회 (email 매칭)
        from core.models import UserProfile
        profile = get_object_or_404(UserProfile, email=user.email)
        
        progresses = UserProgress.objects.filter(user=profile).select_related('practice')
        
        data = []
        for p in progresses:
            data.append({
                'unit_id': p.practice.id,
                'unit_title': p.practice.title,
                'progress_rate': p.progress_rate,
                'unlocked_nodes': p.unlocked_nodes
            })
            
        return Response(data, status=status.HTTP_200_OK)

class SubmitProblemView(APIView):
    """
    문제 해결 시 점수 저장 및 활동 상태 업데이트
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        from core.models import UserProfile
        profile = get_object_or_404(UserProfile, email=user.email)
        
        detail_id = request.data.get('detail_id')
        score = request.data.get('score', 0)
        submitted_data = request.data.get('submitted_data', {})
        
        detail = get_object_or_404(PracticeDetail, id=detail_id)
        
        detail_id = request.data.get('detail_id')
        score = request.data.get('score', 0)
        submitted_data = request.data.get('submitted_data', {})
        
        try:
            # [2026-02-18 상세] 비즈니스 로직(DB 저장, 포인트 정계산, 진도 업데이트)을 
            # 전용 서비스(activity_service.py)로 이관하여 코드 중복을 제거하고 
            # 향후 Unit 1 등 신규 컨텐츠 확장을 용이하게 함 (기존 API 규격은 완벽히 유지)
            result = save_user_problem_record(profile, detail_id, score, submitted_data)
            
            # [2026-02-18 상세] 서비스 실행 후 업데이트된 최신 정보(포인트, 등급, 진행률)를 프론트엔드에 반환함
            return Response({
                'message': 'Progress updated successfully',
                'total_points': result['total_points'],
                'current_rank': result['current_rank'],
                'progress_rate': result['progress_rate']
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserSolvedProblemView(APIView):
    """
    사용자가 해결한 문제 목록 및 제출 데이터 조회
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        from core.models import UserProfile
        profile = get_object_or_404(UserProfile, email=user.email)
        
        # 사용자의 모든 해결 기록 조회 (최신순)
        solved_problems = UserSolvedProblem.objects.filter(user=profile).select_related('practice_detail').order_by('-updated_at')
        
        data = []
        for sp in solved_problems:
            data.append({
                'id': sp.id,
                'practice_detail': sp.practice_detail.id,
                'score': sp.score,
                'submitted_data': sp.submitted_data,
                'is_perfect': sp.is_perfect,
                'updated_at': sp.updated_at
            })
            
        return Response(data, status=status.HTTP_200_OK)

class AvatarPreviewView(APIView):
    """
    회원가입 전 아바타 미리보기 생성
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        prompt = request.data.get('prompt', 'default duck')
        seed = request.data.get('seed')
        
        # 미리보기는 로컬의 고정된 파일(preview_temp.png)에 저장하여 파일 누적 방지
        import os
        from django.conf import settings
        
        avatar_data = generate_nano_banana_avatar(prompt, seed=seed, save_local=False)
        
        if avatar_data and 'image_data' in avatar_data:
            # [수정일: 2026-02-10] 미리보기 시에는 로컬에만 저장 (비용/용량 절감)
            # 확정 시(UserProfileSerializer.update)에만 S3로 업로드됨
            import uuid
            filename = f"preview_{uuid.uuid4().hex}.png"
            media_path = os.path.join('avatars', filename)
            abs_path = os.path.join(settings.MEDIA_ROOT, media_path)
            
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, 'wb') as f:
                f.write(avatar_data['image_data'])
            
            # 최종 응답 데이터 구성 (로컬 URL 반환)
            response_data = {
                'url': f"{settings.MEDIA_URL}{media_path}",
                'seed': avatar_data['seed'],
                'ai_generated': True
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        elif avatar_data and 'url' in avatar_data:
            # 폴백 이미지 등이 반환된 경우 그대로 사용
            return Response(avatar_data, status=status.HTTP_200_OK)
            
        return Response({'error': 'Failed to generate preview'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
