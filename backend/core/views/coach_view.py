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
from core.views.coach_prompt import is_off_topic, GUARDRAIL_MESSAGE, INTENT_ANALYSIS_PROMPT, RESPONSE_STRATEGIES
from core.views.coach_tools import (
    COACH_TOOLS,
    TOOL_DISPATCH,
    TOOL_LABELS,
    validate_and_normalize_args,
    INTENT_TOOL_MAPPING,
    generate_chart_data_summary,
    get_chart_details,
)

logger = logging.getLogger(__name__)


def _should_show_chart(intent_type, user_message):
    """
    Intent와 사용자 메시지 기반으로 차트 표시 필요 여부 판단

    규칙:
    1. 명시적 요청: 차트/시각화/리포트 키워드 → 표시
       - "보여줘", "차트", "그래프", "시각화", "리포트", "데이터를" 포함 → YES
    2. 명시적 비표시: 설명/피드백 중심
       - "분석해", "설명해", "알려" → 텍스트 중심 (NO)
    3. Intent별 기본값 (명시적 요청 없을 때)
       - A (데이터 조회): 기본 표시
       - B (학습 방법): 기본 비표시 (텍스트 중심)
       - C (동기부여): 기본 표시 (성장 데이터 시각화)
       - E (문제 풀이): 기본 비표시 (텍스트 중심)
       - F (개념 설명): 기본 비표시 (텍스트 중심)
       - G (의사결정): 기본 표시 (비교 표시)
    """
    msg_lower = user_message.lower()

    # 명시적 비표시 키워드 (설명/분석 중심 요청)
    text_only_keywords = {"분석해", "설명해", "알려", "어떻게", "왜", "뭐야"}
    if any(kw in msg_lower for kw in text_only_keywords):
        return False

    # 명시적 표시 키워드 (시각화/리포트 요청)
    chart_keywords = {"차트", "시각화", "그래프", "리포트", "보여줘", "보이", "데이터를"}
    if any(kw in msg_lower for kw in chart_keywords):
        return True

    # Intent별 기본값 (명시적 요청 없을 때)
    intent_defaults = {
        "A": True,   # 데이터 조회형: 기본으로 차트 표시
        "B": False,  # 학습 방법형: 텍스트 중심
        "C": True,   # 동기부여형: 성장 데이터 시각화
        "D": False,  # 범위 밖: 차트 불필요
        "E": False,  # 문제 풀이 지원: 텍스트 중심
        "F": False,  # 개념 설명: 텍스트 중심
        "G": True,   # 의사결정형: 비교 표시
    }

    return intent_defaults.get(intent_type, False)


class AICoachView(APIView):
    """ReAct 에이전트 기반 AI 코치

    플로우:
    1. [Guardrail] 명백한 범위 밖 질문 사전 차단
    2. [Agent Loop] LLM이 필요한 도구를 자율적으로 선택하며 상호작용
    3. [Tool Caching] 중복 호출 방지
    4. [SSE Streaming] 실시간 진행 상황 전달
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
                # Step 1: Intent Analysis
                # ──────────────────────────────────────

                yield _sse({
                    "type": "thinking",
                    "stage": "intent_analysis",
                    "message": "질문의 의도를 분석하고 있어요...",
                })

                intent_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": INTENT_ANALYSIS_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    max_completion_tokens=500,
                )

                intent_text = intent_response.choices[0].message.content

                try:
                    # JSON 파싱 시도
                    if "```" in intent_text:
                        intent_text = intent_text.split("```")[1]
                        if intent_text.startswith("json"):
                            intent_text = intent_text[4:]
                    intent_data = json.loads(intent_text.strip())
                except (json.JSONDecodeError, IndexError):
                    logger.warning(f"Intent parse failed: {intent_text}")
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

                # ── 차트 데이터 생성 여부 판단 (동적) ──
                # Intent + 사용자 메시지 기반으로 차트 필요 여부 결정
                should_show_chart = _should_show_chart(intent_type, user_message)

                # ──────────────────────────────────────
                # Step 2: Response Strategy + Agent Loop
                # ──────────────────────────────────────

                yield _sse({
                    "type": "thinking",
                    "stage": "response_strategy",
                    "message": "대응 전략을 수립하고 있어요...",
                })

                strategy = RESPONSE_STRATEGIES.get(intent_type, RESPONSE_STRATEGIES["B"])
                system_prompt = strategy["system_prompt"]

                conv = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ]

                # ── Intent별 도구 필터링 ──
                intent_config = INTENT_TOOL_MAPPING.get(intent_type, {})
                allowed_tools = intent_config.get("allowed", [])
                filtered_tools = [t for t in COACH_TOOLS if t["function"]["name"] in allowed_tools]

                max_iterations = 5

                thinking_messages = [
                    "질문을 분석하고 필요한 데이터를 판단하고 있어요...",
                    "추가 데이터가 필요한지 확인하고 있어요...",
                    "분석 결과를 종합하고 있어요...",
                    "최종 코칭 내용을 정리하고 있어요...",
                    "마무리 중이에요...",
                ]

                for iteration in range(max_iterations):
                    # ── Agent 사고 표시 ──
                    yield _sse({
                        "type": "thinking",
                        "message": thinking_messages[iteration] if iteration < len(thinking_messages) else "분석 중입니다...",
                    })

                    # ── LLM 호출 (스트리밍) ──
                    # 의도별로 필터링된 도구만 제공 (자율성은 유지: tool_choice="auto")
                    tools_to_use = filtered_tools if filtered_tools else openai.NOT_GIVEN
                    tool_choice_param = "auto" if filtered_tools else openai.NOT_GIVEN

                    stream = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=conv,
                        tools=tools_to_use,
                        tool_choice=tool_choice_param,
                        max_completion_tokens=4000,
                        stream=True,
                    )

                    tool_calls_data = {}
                    is_tool_call = False
                    buffered_tokens = []  # ← 토큰을 버퍼에 모으기

                    # ── 스트리밍 처리 ──
                    for chunk in stream:
                        choice = chunk.choices[0] if chunk.choices else None
                        if not choice or not choice.delta:
                            continue
                        delta = choice.delta

                        # Tool calls 수집
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

                        # Content tokens 버퍼에 모으기 (Tool 호출이 없을 때만)
                        if delta.content and not is_tool_call:
                            buffered_tokens.append(delta.content)
                        # Tool 호출이 있으면 즉시 전송
                        elif delta.content and is_tool_call:
                            yield _sse({"type": "token", "token": delta.content})

                    # ── Tool 호출 없으면: 차트 먼저, 그 다음 답변 ──
                    if not is_tool_call:
                        # 1. 차트 데이터를 먼저 생성/전송
                        if should_show_chart:
                            try:
                                chart_summaries = generate_chart_data_summary(profile, intent_type, user_message)
                                for chart in chart_summaries:
                                    yield _sse({
                                        "type": "chart_data",
                                        "intent_type": intent_type,
                                        "chart": chart,
                                    })
                            except Exception as e:
                                logger.warning(f"Failed to generate chart data: {e}")

                        # 2. 이제 버퍼된 토큰들을 전송
                        for token in buffered_tokens:
                            yield _sse({"type": "token", "token": token})

                        yield _sse({"type": "final"})
                        yield "data: [DONE]\n\n"
                        return

                    # ──────────────────────────────────────
                    # ── Tool 실행 ──
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

                # ── max_iterations 도달 ──
                # 1. 차트 데이터를 먼저 생성/전송
                if should_show_chart:
                    try:
                        chart_summaries = generate_chart_data_summary(profile, intent_type, user_message)
                        for chart in chart_summaries:
                            yield _sse({
                                "type": "chart_data",
                                "intent_type": intent_type,
                                "chart": chart,
                            })
                    except Exception as e:
                        logger.warning(f"Failed to generate chart data: {e}")

                # 2. 이제 안내 메시지 전송
                yield _sse({
                    "type": "token",
                    "token": "분석이 복잡하여 일부만 완료되었습니다. 질문을 더 구체적으로 해주세요.",
                })

                yield _sse({"type": "final"})
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

    def get(self, request):
        """상세 차트 데이터 조회 (캐싱 가능)"""
        intent_type = request.query_params.get("intent_type", "A")
        unit_id = request.query_params.get("unit_id", None)

        if intent_type not in ["A", "B", "C", "D", "E", "F", "G"]:
            return Response(
                {"error": f"유효하지 않은 intent_type: {intent_type}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = get_object_or_404(UserProfile, email=request.user.email)

        try:
            details = get_chart_details(profile, intent_type, unit_id)
            return Response({
                "intent_type": intent_type,
                "unit_id": unit_id,
                "data": details,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"[Chart Details] Error: {e}", exc_info=True)
            return Response(
                {"error": "차트 데이터 조회 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
