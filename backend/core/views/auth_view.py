# 생성일: 2026-01-21
# 역할: 로그인, 로그아웃, 세션 확인 체크 등 인증 관련 API 뷰 정의
# 담당자: (User 담당자)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from core.models import UserProfile # [수정일: 2026-01-22] 프로필 정보 조회를 위해 import 추가
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from rest_framework.authentication import SessionAuthentication
from core.models import UserProfile, UserActivity # [수정일: 2026-02-06] UserActivity 추가

# [2026-01-21] CSRF 토큰을 쿠키에 설정하기 위해 ensure_csrf_cookie 데코레이터 사용
@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    # [수정일: 2026-01-22] 로그인 시에는 CSRF를 요구하지 않도록 복구 (Antigravity)
    # 로그인 성공 후 생성되는 세션에 대해 나중에 CSRF 검증이 이루어집니다.
    authentication_classes = []

    def post(self, request):
        # [2026-01-21] 이메일과 비밀번호 기반 로그인 로직 구현
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': '이메일과 비밀번호를 모두 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        # [수정일: 2026-02-04] PK 설계 원복: 이메일로 User 조회하여 기존 username 사용
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            return Response({'error': '가입되지 않은 이메일입니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Django 기본 인증 함수 호출
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user) # 세션 생성
            
            # 닉네임 기본값 (UserProfile or username)
            nickname = user.username
            user_profile = None
            try:
                # [수정일: 2026-01-22] UserProfile 모델 직접 조회 (Antigravity)
                user_profile = UserProfile.objects.get(email=user.email)
                if user_profile.user_nickname:
                     nickname = user_profile.user_nickname
            except UserProfile.DoesNotExist:
                pass 
            
            # [수정일: 2026-02-06] 활동 정보 안전하게 추출
            activity_data = {
                'total_points': 0,
                'current_rank': 'BRONZE',
                'active_avatar': None
            }
            
            if user_profile and hasattr(user_profile, 'activity'):
                activity = user_profile.activity
                activity_data['total_points'] = activity.total_points
                activity_data['current_rank'] = activity.current_rank
                if activity.active_avatar:
                    activity_data['active_avatar'] = {'image_url': activity.active_avatar.image_url}

            # [수정일: 2026-02-06] 상세 정보 및 아바타 프롬프트 추가
            user_detail_data = None
            if user_profile and hasattr(user_profile, 'user_detail'):
                detail = user_profile.user_detail
                user_detail_data = {
                    'is_developer': detail.is_developer,
                    'job_role': detail.job_role if isinstance(detail.job_role, list) else [],
                    'interests': detail.interests if isinstance(detail.interests, list) else []
                }

            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user_profile.id if user_profile else user.username,
                    'username': user.username,
                    'email': user.email,
                    'nickname': nickname,
                    'activity': activity_data,
                    'user_detail': user_detail_data,
                    'active_avatar': {
                        'image_url': activity_data['active_avatar']['image_url'] if activity_data['active_avatar'] else None,
                        'prompt': user_profile.activity.active_avatar.prompt if user_profile and hasattr(user_profile, 'activity') and user_profile.activity.active_avatar else ''
                    } if activity_data['active_avatar'] else None
                }
            })
        else:
            return Response({'error': '비밀번호가 올바르지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        # [2026-01-21] 로그아웃 및 세션 삭제
        logout(request)
        
        response = Response({'message': 'Logged out successfully'})
        
        # [수정일: 2026-01-22] 세션 쿠키만 삭제하고 CSRF 토큰은 유지하여 연속 로그인 가능하게 함 (Antigravity)
        response.delete_cookie('sessionid')
        # response.delete_cookie('csrftoken') # 이 줄은 삭제하거나 주석 처리하여 다음 로그인이 가능하게 함
        
        return response

class SessionCheckView(APIView):
    permission_classes = [permissions.AllowAny]
    # [수정일: 2026-01-22] 세션 확인을 위해 SessionAuthentication 명시
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        # [2026-01-21] 현재 로그인된 사용자 정보 반환 (새로고침 시 상태 유지용)
        if request.user.is_authenticated:
            user = request.user
            # 닉네임 기본값 (UserProfile or username)
            nickname = user.username
            profile = None
            
            # [수정일: 2026-01-22] UserProfile 닉네임 조회 로직 구현 (Antigravity)
            try:
                # auth.User의 이메일과 매칭되는 UserProfile 조회
                profile = UserProfile.objects.get(email=user.email)
                if profile.user_nickname:
                     nickname = profile.user_nickname
            except UserProfile.DoesNotExist:
                 pass
            
            # [수정일: 2026-02-06] 활동 정보 안전하게 추출 (세션 체크용)
            activity_data = {
                'total_points': 0,
                'current_rank': 'BRONZE',
                'active_avatar': None
            }
            
            if profile and hasattr(profile, 'activity'):
                activity = profile.activity
                activity_data['total_points'] = activity.total_points
                activity_data['current_rank'] = activity.current_rank
                if activity.active_avatar:
                    activity_data['active_avatar'] = {'image_url': activity.active_avatar.image_url}

            # [수정일: 2026-02-06] 상세 정보 및 아바타 프롬프트 추가 (세션 체크용)
            user_detail_data = None
            if profile and hasattr(profile, 'user_detail'):
                detail = profile.user_detail
                user_detail_data = {
                    'is_developer': detail.is_developer,
                    'job_role': detail.job_role if isinstance(detail.job_role, list) else [],
                    'interests': detail.interests if isinstance(detail.interests, list) else []
                }

            return Response({
                'isAuthenticated': True,
                'user': {
                    'id': profile.id if profile else user.username,
                    'username': user.username,
                    'email': user.email,
                    'nickname': nickname,
                    'activity': activity_data,
                    'user_detail': user_detail_data,
                    'active_avatar': {
                        'image_url': activity_data['active_avatar']['image_url'] if activity_data['active_avatar'] else None,
                        'prompt': profile.activity.active_avatar.prompt if profile and hasattr(profile, 'activity') and profile.activity.active_avatar else ''
                    } if activity_data['active_avatar'] else None
                }
            })
        else:
            return Response({'isAuthenticated': False})
