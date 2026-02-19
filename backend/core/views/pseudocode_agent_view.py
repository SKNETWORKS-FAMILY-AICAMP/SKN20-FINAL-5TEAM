"""
의사코드 힌트 에이전트 뷰 (Coduck Wizard)
수정일: 2026-02-19

[변경 사항 / 역할 재정의]
- 기존: 평가 + 5차원 점수 산출 (pseudocode_evaluation.py와 중복)
- 변경: 대화형 힌트 전용
  · 학생이 막혔을 때 힌트를 요청하는 용도
  · 점수를 내지 않음 (score 필드 없음)
  · 최종 제출 평가는 pseudocode_evaluation.py 에서만 수행

엔드포인트: POST /api/core/pseudo-agent/
"""

import logging
import json
import re

try:
    import openai
except ImportError:
    openai = None

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class PseudocodeAgentView(APIView):
    """
    대화형 힌트 에이전트.
    학생이 설계 중 막혔을 때 힌트를 요청하면 방향만 제시합니다.
    정답이나 점수는 제공하지 않습니다.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_logic = request.data.get('user_logic', '').strip()
        quest_title = request.data.get('quest_title', '알 수 없는 미션')
        quest_description = request.data.get('quest_description', '')
        selected_strategy = request.data.get('selected_strategy', '')
        constraints = request.data.get('constraints', [])
        hint_level = request.data.get('hint_level', 1)  # 1=가벼운 힌트, 2=구체적 방향, 3=핵심 짚어주기

        if not user_logic:
            return Response(
                {"error": "user_logic 필드가 비어 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not openai or not getattr(settings, 'OPENAI_API_KEY', None):
            return Response(
                {"error": "LLM_UNAVAILABLE", "hint": "현재 힌트 서비스를 사용할 수 없습니다."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            hint_instructions = {
                1: "정답은 주지 말고, 학생이 스스로 생각할 수 있도록 방향만 제시하세요. 질문 형태로 유도해도 좋습니다.",
                2: "설계의 어느 부분이 부족한지 구체적으로 짚어주되, 답은 쓰지 마세요.",
                3: "핵심 개념과 올바른 접근 방향을 명확히 알려주세요. 단, 코드나 완성된 의사코드는 제공하지 마세요.",
            }.get(hint_level, "방향만 제시하세요.")

            system_prompt = f"""당신은 20년 경력의 시니어 아키텍트 'Coduck Wizard'입니다.
현재 학생은 '{quest_title}' 미션을 수행 중입니다.

[역할 규칙]
1. 이 엔드포인트는 힌트 전용입니다. 점수를 산출하거나 "몇 점" 이라고 말하지 마세요.
2. {hint_instructions}
3. 말투: 현명하고 때로는 엄격하지만 교육적인 아키텍트 말투(~하오, ~하게나)를 사용하십시오.

[미션 배경]
{quest_description}

[사용자가 선택한 전략]: {selected_strategy}
[준수해야 할 제약]: {', '.join(constraints) if constraints else '없음'}

응답은 반드시 아래 JSON 형식으로만 하십시오:
{{
  "hint": "힌트 메시지 (2~4문장)",
  "focus_point": "학생이 다시 생각해봐야 할 핵심 포인트 (1문장)",
  "guiding_question": "학생 스스로 답할 수 있도록 유도하는 질문 (선택, 없으면 null)"
}}"""

            user_msg = f"""[내 설계 초안]
{user_logic}

위 설계에서 부족한 부분에 대해 힌트를 주십시오."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ],
                response_format={"type": "json_object"},
                temperature=0.5,
                timeout=20,
            )

            content = response.choices[0].message.content
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                match = re.search(r'\{[\s\S]*\}', content)
                result = json.loads(match.group(0)) if match else {
                    "hint": content,
                    "focus_point": "",
                    "guiding_question": None,
                }

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"[PseudocodeAgent] 힌트 생성 실패: {e}", exc_info=True)
            return Response(
                {
                    "error": "SERVER_ERROR",
                    "hint": "잠시 마법 회로에 간섭이 생겼네. 다시 한 번 설계도를 보여주게나.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
