# 생성일: 2026-01-21
# 역할: 로그인, 로그아웃, 세션 확인 체크 등 인증 관련 API 뷰 정의
# 담당자: (User 담당자)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from rest_framework.authentication import SessionAuthentication # [수정일: 2026-01-22] 세션 인증 명시 (Antigravity)

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

        # 이메일로 User 조회 (auth.User의 username을 모르므로)
        try:
            # 우리 시스템은 이메일을 유니크하게 사용한다고 가정
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            return Response({'error': '가입되지 않은 이메일입니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Django 기본 인증 함수 호출
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user) # 세션 생성
            
            # 닉네임 가져오기 (UserProfile or username)
            nickname = user.username
            if hasattr(user, 'userprofile'):
                nickname = user.userprofile.user_nickname or user.username
            
            return Response({
                'message': 'Login successful',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'nickname': nickname
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
            nickname = user.username
            
            # UserProfile 연결되어 있는 경우 닉네임 우선 사용
            # (주의: UserProfile 모델과 1:1 연결이 어떻게 되어있는지 확인 필요. 
            #  현재 UserProfile.user_id(문자열) 필드와 auth.User가 연결된 게 아니라, 
            #  별도의 UserProfile 테이블만 있는데... auth.User와 UserProfile의 관계 정립 필요)
            
            # 현재 우리 시스템: auth.User (Admin/Login용) vs UserProfile (서비스용)
            # SignUpModal에서 가입 시 UserProfile만 만들었음 -> auth.User는 안 만듦?
            # 잠깐! SignUpModal의 API는 UserProfileViewSet.create인데, 여기서 auth.User를 만드는 로직이 있었나?
            
            # 확인 결과: UserProfileViewSet은 UserProfile 모델만 다룸. 
            # Django 기본 auth.User 테이블에는 데이터가 없을 수 있음!
            # 그렇다면 authenticate()가 작동하지 않습니다. 이 부분을 해결해야 합니다.
            
            return Response({
                'isAuthenticated': True,
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'nickname': nickname
                }
            })
        else:
            return Response({'isAuthenticated': False})
