import openai
import json
import re
import traceback
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class PseudocodeAgentView(APIView):
    """
    [수정일: 2026-02-10]
    수도코드 전용 지능형 에이전트 (Coduck Wizard)
    단순 평가를 넘어 사용자의 설계 의도를 분석하고 맞춤형 피드백을 제공합니다.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        user_logic = request.data.get('user_logic', '')
        quest_title = request.data.get('quest_title', '알 수 없는 미션')
        quest_description = request.data.get('quest_description', '')
        selected_strategy = request.data.get('selected_strategy', '')
        constraints = request.data.get('constraints', [])

        if not user_logic:
            return Response({"error": "User logic is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return Response({"error": "OpenAI API Key is missing"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            client = openai.OpenAI(api_key=api_key)

            system_prompt = f"""
            당신은 20년 경력의 시니어 소프트웨어 아키텍트이자 교육자인 'Coduck Wizard'입니다.
            현재 사용자는 '{quest_title}' 미션을 수행 중입니다.
            
            [미션 배경]
            {quest_description}
            
            [사용자의 사전 선택 전략]
            - 선택한 전략: {selected_strategy}
            - 준수해야 할 제약 사항: {', '.join(constraints)}
            
            [역할 및 지침]
            1. 페르소나: 현명하고 예리하며, 때로는 엄격하지만 교육적인 JRPG 마법사 아키텍트 말투(~하오, ~하게나, ~인가 등)를 사용하십시오.
            2. 분석: 사용자가 서술한 수도코드가 '선택한 전략'과 '제약 사항'을 충실히 반영했는지 검증하십시오.
            3. 평가: 논리적 타당성, 정합성, 예외 처리, 추상화 수준을 평가하십시오.
            4. 피드백: 단순한 정답 확인이 아니라, "왜 이 설계가 위험한지" 또는 "어떻게 하면 더 견고해지는지" 시니어의 관점에서 조언하십시오.
            
            [응답 형식]
            반드시 아래 JSON 형식으로만 응답해야 합니다.
            
            {{
              "score": 0-100,
              "verdict": "도전 성공 / 보완 필요 / 설계 실패 등",
              "analysis": "사용자 설계에 대한 종합적인 비평 (2~3문단)",
              "advice": "다음 단계를 위한 핵심 조언",
              "metrics": {{
                "정합성": {{ "score": 0-100, "comment": "요구사항 준수 여부" }},
                "추상화": {{ "score": 0-100, "comment": "모듈화 및 논리 분리 수준" }},
                "예외처리": {{ "score": 0-100, "comment": "엣지 케이스 고려 여부" }},
                "구현력": {{ "score": 0-100, "comment": "설계의 구체성" }},
                "설계력": {{ "score": 0-100, "comment": "전체적인 아키텍처 완성도" }}
              }},
              "tail_question": {{
                "question": "현재 설계의 허점을 찌르는 날카로운 질문",
                "options": [
                  {{"text": "통찰력 있는 답변", "is_correct": true, "reason": "이유"}},
                  {{"text": "일반적인 답변", "is_correct": false, "reason": "이유"}},
                  {{"text": "잘못된 접근", "is_correct": false, "reason": "이유"}}
                ]
              }}
            }}
            """

            user_msg = f"""
            [사용자 수도코드 설계]
            {user_logic}
            
            위 설계를 아키텍트의 관점에서 분석하여 리포트를 작성하라.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.7
            )

            content = response.choices[0].message.content
            
            # JSON 추출 및 파싱
            try:
                if "```" in content:
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                
                result = json.loads(content.strip())
                return Response(result, status=status.HTTP_200_OK)
            except Exception as parse_e:
                return Response({
                    "score": 50,
                    "verdict": "분석 지연",
                    "analysis": f"아카이브를 분석하는 도중 마법 회로에 간섭이 발생했네. (Error: {str(parse_e)})",
                    "advice": "다시 한번 설계도를 보여주게나.",
                    "metrics": {{ "정합성": 50, "추상화": 50, "예외처리": 50, "구현력": 50, "설계력": 50 }},
                    "tail_question": {{
                        "question": "시스템이 불안정할 때 아키텍처를 점검하는 가장 좋은 방법은?",
                        "options": [
                            {{"text": "로그를 확인한다", "is_correct": True, "reason": "데이터는 거짓말을 하지 않소."}},
                            {{"text": "기도를 한다", "is_correct": False, "reason": "신앙심은 좋으나 공학적이지 않소."}}
                        ]
                    }}
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
