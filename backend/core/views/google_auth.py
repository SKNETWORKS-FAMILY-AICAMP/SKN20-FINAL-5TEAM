import os
import requests
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import UserProfile, UserActivity, UserDetail

class GoogleLoginView(APIView):
    def get(self, request):
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        # 구글 로그인 후 다시 돌아올 우리 서버 주소
        redirect_uri = "https://okay-leisure-mitsubishi-registry.trycloudflare.com/api/core/auth/login/google/callback/"
        
        # 구글 로그인 창으로 보내버리는 주소입니다.
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope=email%20profile"
        )
        return redirect(google_auth_url)

class GoogleCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({'error': '인증 코드가 없습니다.'}, status=400)

        # 1. 구글 서버에 인증 코드를 보내서 Access Token을 받아옵니다.
        token_req_data = {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': "https://okay-leisure-mitsubishi-registry.trycloudflare.com/api/core/auth/login/google/callback/",
        }
        token_req = requests.post("https://oauth2.googleapis.com/token", data=token_req_data)
        token_req_json = token_req.json()
        error = token_req_json.get("error")

        if error:
            return Response({'error': '토큰 교환 실패'}, status=400)

        access_token = token_req_json.get('access_token')

        # 2. 받아온 Access Token으로 유저의 이메일과 프로필 정보를 가져옵니다.
        user_info_req = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_info_req.json()
        email = user_info.get('email')
        name = user_info.get('name', '구글유저')

        if not email:
            return Response({'error': '이메일을 가져올 수 없습니다.'}, status=400)

        # 3. 데이터베이스에 유저가 있는지 확인하고, 없으면 새로 만들어줍니다. (회원가입/로그인 동시 처리)
        user, created = User.objects.get_or_create(username=email, defaults={'email': email})
        
        # UserProfile 및 연관 정보 생성 (기존 회원가입 로직과 동일하게)
        profile, profile_created = UserProfile.objects.get_or_create(email=email, defaults={
            'username': email.split('@')[0][:90],
            'user_name': name,
            'user_nickname': name,
            'password': '', # OAuth2 사용자의 경우 빈 비밀번호 사용
        })

        if created or profile_created:
            UserActivity.objects.get_or_create(user=profile)
            UserDetail.objects.get_or_create(user=profile)

        # 4. 장고 세션을 이용해 서버에 "이 사람 로그인 완료" 도장을 찍어줍니다.
        login(request, user)

        # 5. 모든 처리가 끝나면 프론트엔드 메인 화면으로 리디렉션합니다.
        frontend_url = os.getenv('TUNNEL_FRONTEND_URL', 'http://localhost:5173')
        return redirect(f"{frontend_url}/")
