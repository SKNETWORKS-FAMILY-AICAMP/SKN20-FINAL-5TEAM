import os
import tempfile
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from core.services.interview.musetalk_service import musetalk_service


class AvatarVideoView(APIView):
    """
    POST /api/core/video/generate/

    Body (multipart/form-data):
        audio: WAV 파일 (프론트엔드 TTS에서 가져온 것)
        avatar_type: "woman"  // 선택 (기본값: woman)
        session_id: "abc123"  // 선택

    Response:
        Content-Type: video/mp4
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        avatar_type = request.data.get('avatar_type', 'woman')
        audio_file = request.FILES.get('audio')

        if not audio_file:
            return Response(
                {"error": "audio 파일이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 아바타 이미지 경로
        avatar_file = f"interviewer_{avatar_type}.png"
        image_path = os.path.join(settings.BASE_DIR, "media", "avatars", avatar_file)
        if not os.path.exists(image_path):
            image_path = os.path.join(settings.BASE_DIR, "media", "avatars", "interviewer_woman.png")

        if not os.path.exists(image_path):
            return Response(
                {"error": f"아바타 이미지를 찾을 수 없습니다: {avatar_file}"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                audio_path = os.path.join(tmpdir, "tts.wav")
                with open(audio_path, 'wb') as f:
                    for chunk in audio_file.chunks():
                        f.write(chunk)

                output_path = os.path.join(tmpdir, f"avatar_{avatar_type}.mp4")

                result_path = musetalk_service.generate_video(
                    image_path=image_path,
                    audio_path=audio_path,
                    output_path=output_path,
                    fps=25
                )

                if not result_path or not os.path.exists(result_path):
                    return Response(
                        {"error": "비디오 생성에 실패했습니다."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                with open(result_path, 'rb') as f:
                    video_data = f.read()

            return HttpResponse(video_data, content_type='video/mp4')

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
