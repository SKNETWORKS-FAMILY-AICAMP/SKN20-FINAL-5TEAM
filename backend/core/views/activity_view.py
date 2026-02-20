# 수정일: 2026-02-06
# 수정내용: 아바타, 진행도, 리더보드 관련 API 뷰 구현

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import logging
logger = logging.getLogger(__name__)
from django.db.models import Sum, Count, Max
from core.models import UserActivity, UserSolvedProblem, UserProgress, UserAvatar, Practice, PracticeDetail, UserProfile
from core.services.activity_service import save_user_problem_record
from django.shortcuts import get_object_or_404
from core.nanobanana_utils import generate_nano_banana_avatar # [수정일: 2026-02-06] 추가

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

            # [2026-02-19 추가] 유닛 마스터 정보 집계 (Antigravity)
            # - UserProgress에서 각 유닛의 진행률(100%) 확인
            # - UserSolvedProblem에서 모든 문제의 최고 점수가 90점 이상인지 확인
            mastered_units = []
            user_progresses = UserProgress.objects.filter(user=activity.user).select_related('practice')
            
            for p in user_progresses:
                # 해당 유닛의 전체 문제수
                total_count = PracticeDetail.objects.filter(practice=p.practice, detail_type='PROBLEM').count()
                
                # 유저가 한 번이라도 풀어서 점수가 있는 문제수 (고유 문제 개수)
                solved_count = UserSolvedProblem.objects.filter(
                    user=activity.user, 
                    practice_detail__practice=p.practice
                ).values('practice_detail').distinct().count()

                # 해당 유닛의 모든 문제가 90점 이상인지 체크
                # 1. 유저가 푼 문제들 중 90점 미만인 문제가 하나라도 있는지 확인
                has_subpar_score = UserSolvedProblem.objects.filter(
                    user=activity.user, 
                    practice_detail__practice=p.practice
                ).values('practice_detail').annotate(max_score=Max('score')).filter(max_score__lt=90).exists()
                
                # 2. 유저가 90점 이상으로 완벽하게 풀어낸 고유 문제 개수
                perfect_count = UserSolvedProblem.objects.filter(
                    user=activity.user, 
                    practice_detail__practice=p.practice
                ).values('practice_detail').annotate(max_score=Max('score')).filter(max_score__gte=90).count()

                is_perfect_master = (not has_subpar_score) and (perfect_count == total_count) and (total_count > 0)

                # [2026-02-19] 세분화된 상태값 계산
                progress_rate = p.progress_rate
                if is_perfect_master:
                    unit_status = 'MASTERED'
                elif progress_rate >= 100:
                    unit_status = 'COMPLETED'
                elif progress_rate >= 50:
                    unit_status = 'ADVANCED'
                elif solved_count > 0:
                    unit_status = 'STARTED'
                else:
                    unit_status = 'LOCKED'

                mastered_units.append({
                    'unit_id': p.practice.id,
                    'unit_number': p.practice.unit_number,
                    'is_completed': solved_count > 0, # 0개라도 풀었으면 활성 상태로 간주
                    'is_perfect': is_perfect_master,
                    'solved_count': solved_count,
                    'total_count': total_count,
                    'perfect_count': perfect_count,
                    'unit_status': unit_status # 세분화된 상태 추가
                })

            leaderboard_data.append({
                'id': activity.user.id,
                'rank': i,
                'nickname': user_nickname,
                'points': activity.total_points,
                'current_grade': activity.current_rank,
                'avatar_url': avatar_url,
                'mastered_units': mastered_units
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
        
        # [2026-02-18 상세] 공통 서비스를 통해 문제 해결 기록 저장 및 포인트/등급/진행도 원스톱 갱신
        try:
            result = save_user_problem_record(profile, detail_id, score, submitted_data)
            
            return Response({
                'message': 'Progress updated successfully',
                'total_points': result['total_points'],
                'current_rank': result['current_rank'],
                'progress_rate': result['progress_rate']
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error saving problem record: {str(e)}")
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
                'updated_at': sp.update_date
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
