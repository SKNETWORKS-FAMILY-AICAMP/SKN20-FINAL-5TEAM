"""AI Coach Agent view (streaming ReAct loop orchestrator)."""

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
from core.views.coach_prompt import GUARDRAIL_MESSAGE, SYSTEM_PROMPT, is_off_topic
from core.views.coach_tools import COACH_TOOLS, TOOL_DISPATCH, TOOL_LABELS

logger = logging.getLogger(__name__)


class AICoachView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_message = request.data.get("message", "").strip()
        if not user_message:
            return Response(
                {"error": "메시지를 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if is_off_topic(user_message):
            def guardrail_stream():
                yield f"data: {json.dumps({'type': 'status', 'message': '학습 코칭 범위 밖의 질문이에요', 'variant': 'blocked'}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'type': 'token', 'token': GUARDRAIL_MESSAGE}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"

            resp = StreamingHttpResponse(
                guardrail_stream(),
                content_type="text/event-stream; charset=utf-8",
            )
            resp["Cache-Control"] = "no-cache, no-transform"
            resp["X-Accel-Buffering"] = "no"
            return resp

        if not openai or not getattr(settings, "OPENAI_API_KEY", None):
            return Response(
                {"error": "LLM 서비스를 사용할 수 없습니다."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        profile = get_object_or_404(UserProfile, email=request.user.email)
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        conv = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        def _sse(data):
            return f"data: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"

        thinking_messages = [
            "질문을 분석하고 필요한 데이터를 판단하고 있어요...",
            "추가 데이터가 필요한지 확인하고 있어요...",
            "분석 결과를 종합하고 있어요...",
            "최종 코칭 내용을 정리하고 있어요...",
            "마무리 중이에요...",
        ]

        def event_stream():
            max_iterations = 5
            try:
                for iteration in range(max_iterations):
                    yield _sse({"type": "thinking", "message": thinking_messages[iteration]})

                    stream = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=conv,
                        tools=COACH_TOOLS,
                        tool_choice="auto",
                        max_completion_tokens=4000,
                        stream=True,
                    )

                    tool_calls_data = {}
                    is_tool_call = False
                    content_started = False

                    for chunk in stream:
                        choice = chunk.choices[0] if chunk.choices else None
                        if not choice or not choice.delta:
                            continue
                        delta = choice.delta

                        if delta.tool_calls:
                            is_tool_call = True
                            for tc in delta.tool_calls:
                                idx = tc.index
                                if idx not in tool_calls_data:
                                    tool_calls_data[idx] = {"id": "", "name": "", "arguments": ""}
                                if tc.id:
                                    tool_calls_data[idx]["id"] = tc.id
                                if tc.function:
                                    if tc.function.name:
                                        tool_calls_data[idx]["name"] += tc.function.name
                                    if tc.function.arguments:
                                        tool_calls_data[idx]["arguments"] += tc.function.arguments

                        if delta.content:
                            if not content_started and iteration > 0:
                                content_started = True
                                yield _sse(
                                    {
                                        "type": "status",
                                        "message": "조회한 데이터로 답변을 작성하고 있어요!",
                                        "variant": "ready",
                                    }
                                )
                            yield _sse({"type": "token", "token": delta.content})

                    if not is_tool_call:
                        yield "data: [DONE]\n\n"
                        return

                    if iteration > 0:
                        yield _sse(
                            {
                                "type": "status",
                                "message": "추가 데이터를 가져오고 있어요!",
                                "variant": "fetching",
                            }
                        )

                    tc_list = [tool_calls_data[i] for i in sorted(tool_calls_data.keys())]
                    conv.append(
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": tc["id"],
                                    "type": "function",
                                    "function": {
                                        "name": tc["name"],
                                        "arguments": tc["arguments"],
                                    },
                                }
                                for tc in tc_list
                            ],
                        }
                    )

                    for tc in tc_list:
                        fn_name = tc["name"]
                        try:
                            fn_args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                        except (json.JSONDecodeError, TypeError):
                            fn_args = {}

                        yield _sse(
                            {
                                "type": "step_start",
                                "tool": fn_name,
                                "label": TOOL_LABELS.get(fn_name, fn_name),
                                "args": fn_args,
                            }
                        )

                        executor = TOOL_DISPATCH.get(fn_name)
                        result_data = executor(profile, fn_args) if executor else {"error": f"알 수 없는 도구: {fn_name}"}
                        result_str = json.dumps(result_data, ensure_ascii=False, default=str)

                        yield _sse(
                            {
                                "type": "step_result",
                                "tool": fn_name,
                                "label": TOOL_LABELS.get(fn_name, fn_name),
                                "args": fn_args,
                                "result": result_data,
                            }
                        )

                        conv.append(
                            {
                                "role": "tool",
                                "tool_call_id": tc["id"],
                                "content": result_str,
                            }
                        )

                yield _sse(
                    {
                        "type": "token",
                        "token": "분석이 복잡하여 일부만 완료되었습니다. 질문을 더 구체적으로 해주세요.",
                    }
                )
                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error("[AICoach] Agent loop 실패: %s", e, exc_info=True)
                yield _sse(
                    {
                        "type": "error",
                        "message": "코칭 서비스에 일시적인 문제가 발생했습니다.",
                    }
                )
                yield "data: [DONE]\n\n"

        resp = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream; charset=utf-8",
        )
        resp["Cache-Control"] = "no-cache, no-transform"
        resp["X-Accel-Buffering"] = "no"
        return resp
