"""AI Coach Agent View (최적화 버전) - Modular + Two-Stage + Guardrails + Caching"""

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
from core.views.coach_prompt_optimal import (
    INTENT_ANALYSIS_PROMPT,
    RESPONSE_STRATEGIES,
    is_off_topic,
    GUARDRAIL_MESSAGE,
)
from core.views.coach_tools_optimal import (
    COACH_TOOLS,
    TOOL_DISPATCH,
    TOOL_LABELS,
    INTENT_TOOL_MAPPING,
    validate_and_normalize_args,
    ToolResultEvaluator,
)

logger = logging.getLogger(__name__)


class AICoachOptimalView(APIView):
    """최적화된 AI 코치 (Modular + Two-Stage + Guardrail + Caching)

    플로우:
    1. [Guardrail] 명백한 범위 밖 질문 사전 차단 (규칙 기반)
    2. [Intent Analysis] LLM이 사용자 질문을 A-G로 분류
    3. [Response Strategy] 의도별 프롬프트로 도구 호출 & 응답 생성
    4. [Caching & Validation] 중복 호출 방지, 인자 검증
    5. [SSE Streaming] 의도 + 도구 + 응답을 실시간 전달
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_message = request.data.get("message", "").strip()
        if not user_message:
            return Response(
                {"error": "메시지를 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Guardrail: 범위 밖 질문 사전 차단 ──
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

        def _sse(data):
            return f"data: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"

        def event_stream():
            called_tools_cache = {}  # ← 도구 결과 캐싱
            try:
                # ──────────────────────────────────────
                # Step 1: Intent Analysis (LLM 호출 1차)
                # ──────────────────────────────────────

                yield _sse({
                    "type": "thinking",
                    "stage": "intent_analysis",
                    "message": "질문의 의도를 분석하고 있어요...",
                })

                intent_response = client.chat.completions.create(
                    model="gpt-4-mini",  # 더 빠른 모델
                    messages=[
                        {"role": "system", "content": INTENT_ANALYSIS_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    max_completion_tokens=500,
                )

                intent_text = intent_response.choices[0].message.content

                try:
                    if "```" in intent_text:
                        intent_text = intent_text.split("```")[1]
                        if intent_text.startswith("json"):
                            intent_text = intent_text[4:]
                    intent_data = json.loads(intent_text.strip())
                except (json.JSONDecodeError, IndexError):
                    logger.warning(f"[Intent Parse] 파싱 실패: {intent_text}")
                    intent_data = {
                        "intent_type": "B",
                        "confidence": 0.5,
                        "reasoning": "의도 분석 실패, 학습 방법형으로 가정",
                        "key_indicators": []
                    }

                intent_type = intent_data.get("intent_type", "B")
                confidence = intent_data.get("confidence", 0.5)

                yield _sse({
                    "type": "intent_detected",
                    "intent_type": intent_type,
                    "intent_name": RESPONSE_STRATEGIES.get(intent_type, {}).get("name", "미분류"),
                    "confidence": confidence,
                    "reasoning": intent_data.get("reasoning", ""),
                    "key_indicators": intent_data.get("key_indicators", []),
                })

                # ──────────────────────────────────────
                # Step 2: Response Strategy (LLM 호출 2차부터)
                # ──────────────────────────────────────

                yield _sse({
                    "type": "thinking",
                    "stage": "response_strategy",
                    "message": "대응 전략을 수립하고 있어요...",
                })

                strategy = RESPONSE_STRATEGIES.get(intent_type, RESPONSE_STRATEGIES["B"])
                system_prompt = strategy["system_template"]

                conv = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ]

                # ── Intent별 도구 필터링 ──
                intent_config = INTENT_TOOL_MAPPING.get(intent_type, {})
                allowed_tools = intent_config.get("allowed", [])
                required_tools = intent_config.get("required", [])
                filtered_tools = [t for t in COACH_TOOLS if t["function"]["name"] in allowed_tools]

                # ── Tool 결과 평가 준비 ──
                evaluator = ToolResultEvaluator()
                tool_results = []
                tools_sufficient = False

                required_tools_called = set()
                required_tools_missing = set(required_tools) if required_tools else set()

                max_iterations = 8  # B의 5 + A의 10 중간값
                for iteration in range(max_iterations):
                    yield _sse({
                        "type": "thinking",
                        "stage": "response_generation",
                        "message": f"분석 중입니다... ({iteration + 1}/{max_iterations})",
                    })

                    # ── 도구 제공 여부 결정 ──
                    if tools_sufficient:
                        tools_to_use = openai.NOT_GIVEN
                        tool_choice_param = openai.NOT_GIVEN
                    else:
                        if filtered_tools:
                            tools_to_use = filtered_tools
                            if required_tools_missing:
                                tool_choice_param = "required"  # ← 필수 도구 강제 호출
                                logger.info(f"[필수 도구 호출] {required_tools_missing}")
                            else:
                                tool_choice_param = "auto"
                        else:
                            tools_to_use = openai.NOT_GIVEN
                            tool_choice_param = openai.NOT_GIVEN

                    stream = client.chat.completions.create(
                        model="gpt-4-mini",
                        messages=conv,
                        tools=tools_to_use,
                        tool_choice=tool_choice_param,
                        max_completion_tokens=4000,
                        stream=True,
                    )

                    tool_calls_data = {}
                    is_tool_call = False

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
                            yield _sse({"type": "token", "token": delta.content})

                    # Tool 호출 없으면 최종 답변 완료
                    if not is_tool_call:
                        yield _sse({
                            "type": "final",
                            "intent_type": intent_type,
                            "strategy": strategy["name"],
                        })
                        yield "data: [DONE]\n\n"
                        return

                    # ──────────────────────────────────────
                    # Tool Calling & Execution
                    # ──────────────────────────────────────

                    tc_list = [tool_calls_data[i] for i in sorted(tool_calls_data.keys())]
                    conv.append({
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
                    })

                    for tc in tc_list:
                        fn_name = tc["name"]

                        # ← 필수 도구 호출 추적
                        if fn_name in required_tools:
                            required_tools_called.add(fn_name)
                            required_tools_missing.discard(fn_name)
                            logger.info(f"[필수 도구 호출] {fn_name}")

                        try:
                            fn_args_raw = json.loads(tc["arguments"]) if tc["arguments"] else {}
                        except (json.JSONDecodeError, TypeError):
                            fn_args_raw = {}

                        yield _sse({
                            "type": "step_start",
                            "tool": fn_name,
                            "label": TOOL_LABELS.get(fn_name, fn_name),
                            "args": fn_args_raw,
                        })

                        # ── 캐시 확인 ──
                        cache_key = f"{fn_name}:{json.dumps(fn_args_raw, sort_keys=True, ensure_ascii=False)}"
                        if cache_key in called_tools_cache:
                            result_data = called_tools_cache[cache_key]
                            logger.debug(f"[캐시 히트] {fn_name}")
                        else:
                            executor = TOOL_DISPATCH.get(fn_name)
                            if not executor:
                                result_data = {"error": True, "message": f"알 수 없는 도구: {fn_name}"}
                            else:
                                try:
                                    fn_args = validate_and_normalize_args(fn_name, fn_args_raw)
                                    result_data = executor(profile, fn_args)
                                    called_tools_cache[cache_key] = result_data
                                except ValueError as ve:
                                    logger.warning(f"[인자 검증 실패] {fn_name}: {ve}")
                                    result_data = {"error": True, "message": str(ve)}
                                except Exception as e:
                                    logger.error(f"[도구 실행 오류] {fn_name}", exc_info=True)
                                    result_data = {"error": True, "message": f"'{fn_name}' 도구 실행 중 오류가 발생했습니다."}

                        result_str = json.dumps(result_data, ensure_ascii=False, default=str)
                        yield _sse({
                            "type": "step_result",
                            "tool": fn_name,
                            "label": TOOL_LABELS.get(fn_name, fn_name),
                            "args": fn_args_raw,
                            "result": result_data,
                        })

                        conv.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": result_str,
                        })

                        tool_results.append({
                            "tool": fn_name,
                            "args": fn_args_raw,
                            "result": result_data,
                        })

                    # ── 데이터 충분도 평가 ──
                    if is_tool_call:
                        if not required_tools_missing:
                            logger.info(f"[충분도 평가] Intent {intent_type}: 필수 도구 모두 호출됨")
                            tools_sufficient = True
                        elif evaluator.is_sufficient(tool_results, intent_type):
                            logger.info(f"[충분도 평가] Intent {intent_type}: 데이터 충분")
                            tools_sufficient = True
                        else:
                            logger.warning(f"[충분도 미달] Intent {intent_type}, iteration {iteration + 1}/{max_iterations}")

                # max_iterations 도달
                if required_tools_missing:
                    warning_msg = f"주의: 필수 데이터를 완전히 수집하지 못했습니다. 다시 시도하거나 더 구체적인 질문을 해주세요."
                    logger.warning(f"[Max Iterations] {warning_msg}")
                    yield _sse({
                        "type": "warning",
                        "message": warning_msg,
                        "missing_tools": list(required_tools_missing),
                    })
                else:
                    yield _sse({
                        "type": "token",
                        "token": "분석이 복잡하여 일부만 완료되었습니다. 질문을 더 구체적으로 해주세요.",
                    })
                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"[AICoachOptimal] Error: {e}", exc_info=True)
                yield _sse({
                    "type": "error",
                    "message": f"코칭 서비스에 일시적인 문제가 발생했습니다. ({str(e)})",
                })
                yield "data: [DONE]\n\n"

        resp = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream; charset=utf-8",
        )
        resp["Cache-Control"] = "no-cache, no-transform"
        resp["X-Accel-Buffering"] = "no"
        return resp
