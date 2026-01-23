import openai
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import environ
import os

env = environ.Env()

@method_decorator(csrf_exempt, name='dispatch')
class AIChatView(APIView):
    """
    AI 학습 도우미 챗봇 뷰
    """
    authentication_classes = [] # CSRF 체크 방지를 위해 인증 클래스 비우기
    permission_classes = [AllowAny]

    def post(self, request):
        user_message = request.data.get('message')
        quest_context = request.data.get('quest_context', '')
        
        if not user_message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # settings에서 API 키 로드
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return Response({"error": "API Key not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            client = openai.OpenAI(api_key=api_key)
            
            # 시스템 프롬프트 설정 (JRPG 튜터 컨셉)
            system_prompt = f"""
            당신은 'Super Code Adventure' 게임의 AI 튜터 '코드 위저드'입니다.
            현재 사용자는 다음 퀘스트를 수행 중입니다: {quest_context}
            
            평가 및 대화 규칙:
            1. 친절한 JRPG 게임 캐릭터 말투를 사용하세요 (~하오, ~하게나, 혹은 신비로운 마법사 톤).
            2. 사용자가 코드를 제출했을 때(실행결과가 포함된 경우):
               - 실행결과가 '성공'이라면, 논리적 완성도를 칭찬하고 실력이 'A-Rank' 급이라고 치켜세워주세요.
               - 실행결과가 '실패'라면, 안타까워하며 어떤 마법 공식(코드)이 꼬였는지 비유적으로 설명하세요.
               - 제공된 '체크포인트'를 기준으로 사용자의 코드가 해당 기준을 충족하는지 넌지시 언급하세요.
            3. 정답 코드를 바로 알려주지 말고, 스스로 답을 찾을 수 있는 힌트를 단계적으로 제공하세요.
            4. 답변은 한국어로 하며, 텍스트가 너무 길어지지 않게 핵심만 전달하세요.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo", # 또는 gpt-4
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )

            ai_message = response.choices[0].message.content
            return Response({"message": ai_message}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
