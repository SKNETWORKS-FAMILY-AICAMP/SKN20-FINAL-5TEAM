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
import json
import sys
import traceback

env = environ.Env()

@method_decorator(csrf_exempt, name='dispatch')
class AIChatView(APIView):
    """
    AI 학습 도우미 챗봇 뷰 (JRPG 코드 위저드 컨셉)
    """
    authentication_classes = [] 
    permission_classes = [AllowAny]

    def post(self, request):
        user_message = request.data.get('message')
        quest_context = request.data.get('quest_context', '')
        
        if not user_message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return Response({"error": "API Key not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            client = openai.OpenAI(api_key=api_key)
            
            system_prompt = f"""
            당신은 'Super Code Adventure' 게임의 AI 튜터 '코드 위저드'입니다.
            현재 사용자는 다음 퀘스트를 수행 중입니다: {quest_context}
            
            평가 및 대화 규칙:
            1. 친절한 JRPG 게임 캐릭터 말투를 사용하세요 (~하오, ~하게나, 혹은 신비로운 마법사 톤).
            2. 한국어로 핵심만 전달하세요.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )

            ai_message = response.choices[0].message.content
            return Response({"message": ai_message}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class AIEvaluationView(APIView):
    """
    실습 결과 AI 정밀 평가 및 꼬리 질문 생성 뷰
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        # [수정일: 2026-01-27] AxiosError 500 해결을 위한 데이터 및 SDK 호환성 수정한 버전
        score = request.data.get('score', 0)
        grade = request.data.get('grade', 'F')
        quest_title = request.data.get('quest_title', '알 수 없는 퀘스트')
        user_logic = request.data.get('user_logic', [])
        user_code = request.data.get('user_code', {})
        user_free_answer = request.data.get('user_free_answer', '')
        
        # 디버그 로그 (실시간 확인용)
        print(f"[DEBUG] Eval Start: {quest_title} / {score}", flush=True)
        
        try:
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return Response({"error": "OpenAI API Key is missing"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            client = openai.OpenAI(api_key=api_key)
            
            # [중요] SDK 호환성을 위해 response_format 대신 프롬프트 지시 강화
            system_prompt = """
            당신은 시니어 소프트웨어 엔지니어 '코드 위저드'입니다. 
            반드시 아래의 **JSON 형식으로만** 응답해야 합니다. 다른 텍스트는 섞지 마세요.

            {
              "score": 0-100,
              "analysis": "답변 및 코드 논리에 대한 구체적인 분석 (2~3문장)",
              "advice": "제자를 위한 따뜻한 조언",
              "is_logical": true/false,
              "metrics": {
                "정합성": 0-100, "추상화": 0-100, "예외처리": 0-100, "구현력": 0-100, "설계력": 0-100
              },
              "tail_question": {
                "question": "논리적 헛점을 찌르는 날카로운 질문 1개",
                "options": [
                  {"text": "정답", "is_correct": true, "reason": "..."},
                  {"text": "오답1", "is_correct": false, "reason": "..."},
                  {"text": "오답2", "is_correct": false, "reason": "..."}
                ]
              }
            }
            """
            
            logic_str = ', '.join(user_logic) if isinstance(user_logic, list) else str(user_logic)
            user_msg = f"""
            [미션] {quest_title} (현재 점수: {score})
            [로직] {logic_str}
            [코드] {user_code}
            [자유 답변] {user_free_answer}
            
            위 데이터를 분석하여 JSON 결과를 출력하라.
            """

            print("[DEBUG] Calling OpenAI...", flush=True)
            # response_format 제거 (SDK 호환성)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ]
            )
            
            content = response.choices[0].message.content
            print(f"[DEBUG] AI Response Received: {content[:100]}...", flush=True)

            try:
                # JSON 문자열 정제 (가끔 ```json ... ``` 으로 감싸지는 경우 대비)
                if "```" in content:
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                
                result = json.loads(content.strip())
                
                # 프론트엔드 호환성 유지
                if 'feedback' not in result and 'analysis' in result:
                    result['feedback'] = result['analysis']
                    
                return Response(result, status=status.HTTP_200_OK)
            
            except Exception as parse_e:
                print(f"[DEBUG] JSON Parse Fail: {parse_e}", flush=True)
                # 파싱 실패 시 기본 응답 구조 반환
                return Response({
                    "score": score,
                    "analysis": "분석 파싱 중 마법이 꼬였네. 하지만 자네의 논리는 충분히 훌륭하네.",
                    "advice": "코드의 가독성을 조금 더 신경 써보게나.",
                    "is_logical": True,
                    "metrics": { "정합성": 85, "추상화": 75, "예외처리": 65, "구현력": 85, "설계력": 80 },
                    "tail_question": {
                        "question": "파싱 에러가 발생했을 때, 시스템의 가용성을 유지하는 가장 좋은 방법은?",
                        "options": [
                            {"text": "Fallback 응답을 정의한다", "is_correct": True, "reason": "사용자 경험을 해치지 않습니다."},
                            {"text": "서버를 즉시 중단한다", "is_correct": False, "reason": "서비스 중단은 최후의 수단입니다."},
                            {"text": "에러를 무시한다", "is_correct": False, "reason": "데이터 오염의 위험이 있습니다."}
                        ]
                    }
                }, status=status.HTTP_200_OK)

        except Exception as e:
            tb = traceback.format_exc()
            print(f"[CRITICAL] AI Error: {e}\n{tb}", flush=True)
            return Response({"error": str(e), "traceback": tb}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
