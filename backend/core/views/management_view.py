# 수정일: 2026-02-08
# 수정내용: 진도 관리 및 사용자 답변 조회를 위한 관리용 API 구현

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Count, Avg, F
from core.models import UserProfile, UserProgress, UserSolvedProblem, Practice
from django.shortcuts import get_object_or_404

class IsAdminUser(permissions.BasePermission):
    """관리자 권한 확인"""
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsOwnerOrAdmin(permissions.BasePermission):
    """본인 또는 관리자 권한 확인"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        # UserSolvedProblem이나 UserProgress의 경우 user 필드를 통해 확인
        user_profile = getattr(obj, 'user', None)
        if user_profile and user_profile.email == request.user.email:
            return True
        return False

class OverallProgressView(APIView):
    """
    [관리자 전용] 모든 사용자의 연습 과정별 진행률 조회
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        profiles = UserProfile.objects.all().prefetch_related('progresses__practice')
        
        results = []
        for profile in profiles:
            user_progress = []
            for prog in profile.progresses.all():
                user_progress.append({
                    'practice_id': prog.practice.id,
                    'practice_title': prog.practice.title,
                    'progress_rate': prog.progress_rate,
                    'last_update': prog.update_date
                })
            
            results.append({
                'user_id': profile.id,
                'username': profile.username,
                'nickname': profile.user_nickname,
                'email': profile.email,
                'progress': user_progress
            })
            
        return Response(results, status=status.HTTP_200_OK)

class UserAnswersView(APIView):
    """
    사용자 본인 또는 관리자가 특정 연습 과정의 상세 답변 내역 조회
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, practice_id=None, user_id=None):
        print(f"DEBUG: UserAnswersView - practice_id: {practice_id}, user_id: {user_id}, user: {request.user}", flush=True)
        # 1. 대상 유저 결정 (user_id가 없으면 본인)
        if user_id and request.user.is_superuser:
            target_profile = get_object_or_404(UserProfile, id=user_id)
        else:
            # [수정일: 2026-02-08] 이메일 대신 더 확실한 username으로 매칭 (404 방지)
            target_profile = get_object_or_404(UserProfile, username=request.user.username)
        
        print(f"DEBUG: Found target_profile: {target_profile.email}", flush=True)
        
        # 2. 특정 연습 과정(Practice)의 모든 문제 해결 기록 조회
        query = UserSolvedProblem.objects.filter(user=target_profile).select_related('practice_detail')
        
        if practice_id:
            query = query.filter(practice_detail__practice_id=practice_id)
            # [2026-02-20] 버그헌트 튜토리얼 단계 (S1, S2, S3) 제외
            # - 데이터는 DB에 저장되지만 마이 히스토리에는 S4 이상만 표시
            if practice_id == 'unit02':
                query = query.exclude(
                    practice_detail__content_data__id__in=['S1', 'S2', 'S3']
                )

        # [2026-02-19 수정] 문제별 시도 내역 그룹화 (Antigravity)
        # - 최신 기록부터 먼저 정렬하여 그룹화 처리
        solved_list = query.order_by('-solved_date')
        
        group_map = {}
        for solved in solved_list:
            detail_id = solved.practice_detail.id
            if detail_id not in group_map:
                # content_data에 title이 있으면 사용, 없으면 detail_title 사용
                problem_title = solved.practice_detail.detail_title
                if solved.practice_detail.content_data and isinstance(solved.practice_detail.content_data, dict):
                    problem_title = solved.practice_detail.content_data.get('title', solved.practice_detail.detail_title)

                group_map[detail_id] = {
                    'detail_id': detail_id,
                    'title': problem_title,
                    'display_order': solved.practice_detail.display_order,
                    'attempts': []
                }
            
            # 각 시도 기록을 attempts 리스트에 추가
            group_map[detail_id]['attempts'].append({
                'score': solved.score,
                'is_perfect': solved.is_perfect,
                'submitted_data': solved.submitted_data,
                'solved_date': solved.solved_date
            })
            
        # 3. display_order 기준 정렬 및 최종 포맷팅
        grouped_answers = sorted(
            group_map.values(),
            key=lambda x: x['display_order']
        )

        # 반환용 리스트에서 display_order 필드 제거
        for group in grouped_answers:
            group.pop('display_order', None)
            
        return Response({
            'user': {
                'nickname': target_profile.user_nickname,
                'email': target_profile.email
            },
            'practice_id': practice_id,
            'answers': grouped_answers
        }, status=status.HTTP_200_OK)
