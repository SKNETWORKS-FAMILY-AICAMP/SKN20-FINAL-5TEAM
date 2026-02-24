"""AI Coach Agent View - Intent Analysis + ReAct 패턴 기반 학습 코칭

플로우:
1. [Intent Analysis] 사용자 질문 → A-G 중 분류
2. [Response Strategy] 의도별 프롬프트로 도구 호출 & 응답 생성 (자율성 유지)
3. [SSE 스트리밍] 의도 분석 + 도구 호출 + 최종 응답 전달
"""

import json
import logging
import openai
from django.conf import settings
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import UserProfile
# from core.views.coach_prompt import is_off_topic, GUARDRAIL_MESSAGE, INTENT_ANALYSIS_PROMPT, RESPONSE_STRATEGIES
# from core.views.coach_tools import (
#     COACH_TOOLS,
#     TOOL_DISPATCH,
#     TOOL_LABELS,
#     validate_and_normalize_args,
#     INTENT_TOOL_MAPPING,
# )

logger = logging.getLogger(__name__)


class AICoachView(APIView):
    """ReAct 에이전트 기반 AI 코치 (임시 비활성화됨)
    [수정일: 2026-02-24] 누락된 모듈 오류로 인해 임시 비활성화 조치
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response(
            {"error": "AI Coach 서비스는 현재 점검 중입니다."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
