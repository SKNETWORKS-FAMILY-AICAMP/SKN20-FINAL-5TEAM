"""
STT API 엔드포인트
POST /api/core/stt/transcribe/
음성 파일 → 텍스트 변환
"""
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from core.models import UserProfile
from core.services.stt.stt_service import process_audio


def _get_user(request):
    """세션에서 UserProfile을 가져온다. 없으면 None."""
    from django.contrib.auth.models import User
    auth_user_id = request.session.get('_auth_user_id')
    if not auth_user_id:
        return None
    try:
        django_user = User.objects.get(pk=auth_user_id)
        return UserProfile.objects.get(email=django_user.email)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return None


@method_decorator(csrf_exempt, name='dispatch')
class STTTranscribeView(APIView):
    """
    POST /api/core/stt/transcribe/

    Body (multipart/form-data):
        audio: 음성 파일 (WAV, WebM, OGG, MP4 등)

    Response:
        {
            "transcript": "변환된 텍스트",
            "confidence": 0.95,
            "language": "ko",
            "has_speech": true
        }
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        user = _get_user(request)
        if not user:
            return Response(
                {'error': '로그인이 필요합니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response(
                {'error': '오디오 파일이 필요합니다. (form-data key: "audio")'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 파일 크기 제한: 25MB
        if audio_file.size > 25 * 1024 * 1024:
            return Response(
                {'error': '파일이 너무 큽니다. (최대 25MB)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        audio_bytes = audio_file.read()

        try:
            result = process_audio(audio_bytes)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'음성 변환 중 오류가 발생했습니다: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
