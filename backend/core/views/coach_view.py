"""AI Coach Agent View - ReAct 패턴 기반 학습 코칭"""

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
from core.views.coach_prompt import is_off_topic, GUARDRAIL_MESSAGE
from core.views.coach_tools import (
    COACH_TOOLS,
    TOOL_DISPATCH,
    TOOL_LABELS,
    validate_and_normalize_args,
)

logger = logging.getLogger(__name__)


class AICoachOptimalView(APIView):
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

        # ── System Prompt (ReAct) ──
        SYSTEM_PROMPT = """당신은 AI 학습 코치 'Coduck Coach'입니다.

[역할]
- 학생의 학습 데이터를 도구(tool)로 조회하여 맞춤 코칭 제공
- 추측 금지, 반드시 데이터 기반 답변

[답변 구조 — 반드시 아래 3파트를 모두 포함]

1. **현재 상태 진단** (데이터 해석)
   - 조회한 데이터에서 핵심 수치 2~3개를 뽑아 의미를 설명
   - 단순 숫자 나열 금지. "~점이니까 ~수준이야" 처럼 해석해줘
   - 잘하는 부분은 칭찬, 부족한 부분은 솔직하게

2. **원인 분석 & 인사이트**
   - 왜 이런 결과가 나왔는지 가능한 원인 1~2개 제시
   - 약점 메트릭이 있다면 구체적으로 어떤 능력이 부족한 건지 풀어서 설명

3. **구체적 행동 가이드**
   - "~를 다시 풀어봐", "~부터 시작하자" 등 지금 당장 할 수 있는 행동 1~2개
   - 가능하면 특정 유닛이나 문제를 지목

[형식 규칙]
- 전체 답변 300~700자
- 영어 metric 이름은 반드시 한국어로 번역 (design→설계, implementation→구현, abstraction→추상화, edge_case→예외처리, consistency→일관성, security→보안, reliability→신뢰성, performance→성능, sustainability→지속가능성, maintainability→유지보수성)
- 마크다운: 짧은 제목(##) + 불릿(-) 위주

[톤]
- 한국어, 친근한 선배/코치 말투 (반말 OK, "~해봐", "~하자")
- 데이터가 없으면 학습 시작을 격려
- 칭찬할 건 칭찬하고, 부족한 건 솔직하게

[유닛 정보]
- unit01: 의사코드(Pseudo Code) 연습
- unit02: 디버깅(Bug Hunt) 연습
- unit03: 시스템 아키텍처 설계 연습

[도구 활용 가이드]
- get_user_scores: 유닛별 성적 조회 (신청한 도구)
- get_weak_points: 특정 유닛의 약점 분석 (약점 파악 필요 시)
- get_recent_activity: 최근 학습 활동 조회 (학습 패턴 파악 필요 시)
- recommend_next_problem: 다음 풀이 문제 추천 (문제 추천 필요 시)
- get_unit_curriculum: 유닛 커리큘럼 조회 (학습 방법/개념 질문 시)
- get_study_guide: 맞춤 학습 가이드 생성 (구체적 공부 방법 필요 시)

필요한 도구를 자율적으로 선택하여 호출하세요.
"""

        def event_stream():
            called_tools_cache = {}  # ← 도구 결과 캐싱
            try:
                conv = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ]

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
                    stream = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=conv,
                        tools=COACH_TOOLS,
                        tool_choice="auto",  # ← 에이전트 자율성 핵심
                        max_completion_tokens=4000,
                        stream=True,
                    )

                    tool_calls_data = {}
                    is_tool_call = False

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

                        # Content tokens 즉시 전송
                        if delta.content:
                            yield _sse({"type": "token", "token": delta.content})

                    # ── Tool 호출 없으면 최종 답변 ──
                    if not is_tool_call:
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
