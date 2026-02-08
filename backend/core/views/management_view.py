# 수정일: 2026-02-08
# 수정내용: 진도 관리 및 사용자 답변 조회를 위한 관리용 API 구현

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Count, Avg, F
from core.models import UserProfile, UserProgress, UserSolvedProblem, Practice, PracticeDetail
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
            
        solved_list = query.order_by('practice_detail__display_order')
        
        answers = []
        for solved in solved_list:
            answers.append({
                'detail_id': solved.practice_detail.id,
                'title': solved.practice_detail.detail_title,
                'score': solved.score,
                'is_perfect': solved.is_perfect,
                'submitted_data': solved.submitted_data,
                'solved_date': solved.solved_date
            })
            
        return Response({
            'user': {
                'nickname': target_profile.user_nickname,
                'email': target_profile.email
            },
            'practice_id': practice_id,
            'answers': answers
        }, status=status.HTTP_200_OK)
