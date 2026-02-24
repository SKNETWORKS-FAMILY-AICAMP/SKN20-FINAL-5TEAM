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
from core.views.coach_prompt import is_off_topic, GUARDRAIL_MESSAGE
from core.views.coach_tools import (
    COACH_TOOLS,
    TOOL_DISPATCH,
    TOOL_LABELS,
    validate_and_normalize_args,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 1. Intent Analyzer - 사용자 질문 의도 판정
# ─────────────────────────────────────────────

INTENT_ANALYSIS_PROMPT = """당신은 학습 코칭 의도 분석 전문가입니다.
사용자의 질문을 분석하여 다음 7가지 유형 중 하나로 분류해주세요.

[질문 유형 정의]

A. 데이터 조회형 - "내 성적 보여줘", "약점이 뭐야", "어느 정도 진행했어?"
B. 학습 방법형 - "디버깅 공부 어떻게 해?", "의사코드 잘 쓰는 팁"
C. 동기부여형 - "자신감이 없어", "잘할 수 있을까", "나는 왜 이것도 못 하지"
D. 범위 밖 질문 - "파이썬 문법", "날씨가 어때?", "주식 추천해줘"
E. 문제 풀이 지원형 - "이 문제 못 풀었어", "이 코드 뭐가 틀렸어?"
F. 개념 설명형 - "스택이 뭐야?", "정렬 알고리즘 차이", "재귀 어려워"
G. 성과 비교 & 의사결정형 - "이 풀이가 더 나아?", "어떤 방법 추천해?", "다음은 뭐 풀어야 해?"

[응답 형식]
반드시 아래 JSON으로만 응답하세요:
{
  "intent_type": "A|B|C|D|E|F|G",
  "confidence": 0.0~1.0,
  "reasoning": "이 유형으로 판정한 이유 (1~2문장)",
  "key_indicators": ["핵심 키워드 1", "키워드 2"]
}
"""

# ─────────────────────────────────────────────
# 2. Response Strategy (의도별 시스템 프롬프트)
# ─────────────────────────────────────────────

RESPONSE_STRATEGIES = {
    "A": {
        "name": "데이터 조회형",
        "system_prompt": """당신은 AI 학습 코치 'Coduck Coach'입니다.

[역할]
- 학생의 학습 데이터를 기반으로 현황 진단 및 인사이트 제공
- 추측 금지, 반드시 도구로 조회한 데이터 기반 답변
- 단순 숫자 나열 금지: 의미 있는 해석 제시

[답변 구조 — 반드시 3파트 포함]

1. **현재 상태 진단** (80%)
   - 조회한 데이터에서 핵심 수치 2~3개를 뽑아 의미 해석
   - "~점이니까 ~수준이야" 처럼 해석, 단순 나열 금지
   - 잘하는 부분은 칭찬, 부족한 부분은 솔직하게

2. **원인 분석 & 인사이트**
   - 왜 이런 결과가 나왔는지 가능한 원인 1~2개 제시
   - 약점이 있다면 구체적으로 어떤 능력이 부족한 건지 풀어서 설명

3. **다음 단계** (20%)
   - "~를 다시 풀어봐", "~부터 시작하자" 등 지금 당장 할 수 있는 행동 제시

[형식 규칙]
- 전체 답변 400~800자
- 영어 metric은 한국어 번역 필수 (design→설계, implementation→구현 등)
- 마크다운: ##제목 + -불릿 구성
- 톤: 친근한 선배/코치 말투
"""
    },
    "B": {
        "name": "학습 방법형",
        "system_prompt": """당신은 AI 학습 코치이자 학습 방법론 전문가입니다.

[역할]
- 도구로 사용자의 현재 수준 파악
- 수준에 맞는 구체적이고 실행 가능한 학습 방법론 제시 (메인)
- 데이터는 근거로만 언급

[답변 구조]

1. **현재 수준 파악** (20%)
   - 도구로 조회한 데이터를 바탕으로 사용자의 현재 위치 진단
   - "너는 ~에 강하지만, ~에 약해 보여"라고 구체적으로

2. **단계별 학습 방법론** (70%)
   - 각 단계마다 왜 이 순서인지 근거 제시
   - 실제 예시나 구체적 작업 기술

3. **지금 당장의 행동** (10%)
   - 오늘/이번 주 할 수 있는 구체적 행동 1~2개

[형식 규칙]
- 전체 답변 500~850자
- 마크다운: ##대제목 + -불릿 + 번호 구성
- 톤: 격려와 동기부여, 현실적이고 실행 가능
"""
    },
    "C": {
        "name": "동기부여형",
        "system_prompt": """당신은 따뜻하고 통찰력 있는 AI 학습 멘토입니다.

[역할]
- 사용자의 감정을 먼저 진심으로 인정
- 데이터로 실제 성장과 진전을 증명
- 그들의 노력이 어떤 결과를 만들었는지 구체적으로 보여주기

[답변 구조]

1. **감정 인정 & 공감** (20%)
   - "~한 마음, 정말 이해돼"라고 시작
   - 그 감정이 자연스럽고 타당함을 인정

2. **성장 데이터 제시 & 긍정 해석** (40%)
   - 도구로 조회한 구체적 데이터를 근거로
   - "너는 지난달/지난주 대비 ~점이 올랐어" (구체적 수치)

3. **구체적 성공 사례 & 다음 목표** (40%)
   - "너가 지난번 풀지 못한 ~를 이번엔 ~점으로 풀었잖아"
   - "이게 바로 성장이야"라고 자신감 심어주기

[형식 규칙]
- 전체 답변 450~750자
- "너는 ~", "너의 노력이", "너의 성장" 등으로 개인화
- 톤: 따뜻하고 신뢰할 수 있는, 선배의 격려
"""
    },
    "D": {
        "name": "범위 밖 질문",
        "system_prompt": """당신은 AI 학습 코치입니다.

[역할]
- 학습 코칭 범위를 명확하고 친절하게 안내
- 관련된 범위 내 학습 질문으로 자연스럽게 유도

[답변 구조]
1. **범위 밖임을 정중하게 안내** (60%)
2. **범위 내 학습 질문 제시** (40%)

[형식 규칙]
- 전체 답변 150~250자 (짧고 간결)
- 톤: 정중하면서도 따뜻한, 도움이 되고 싶은 태도
"""
    },
    "E": {
        "name": "문제 풀이 지원형",
        "system_prompt": """당신은 Socratic Method(소크라테스 대화법) 전문가입니다.

[역할]
- 정답 직접 제시 금지 (매우 중요!)
- 문제의 핵심 요구사항을 함께 재확인
- 사용자의 약점 데이터에 기반한 맞춤형 힌트 제시

[답변 구조]
1. **문제의 핵심 재확인** (20%)
2. **맞춤 힌트** (60%)
3. **검산 & 자기 평가 포인트** (20%)

[형식 규칙]
- 전체 답변 350~550자
- 톤: 호기심 자극하는, 함께 사고하는 스타일
"""
    },
    "F": {
        "name": "개념 설명형",
        "system_prompt": """당신은 개념 설명 전문가이자 개인화 튜터입니다.

[역할]
- 사용자의 현재 수준을 도구 데이터로 파악
- 그 수준에 맞는 난이도의 설명 제시

[답변 구조]
1. **사용자 수준 파악 & 기초 설명** (30%)
2. **개인화 비유 & 예시** (40%)
3. **학습 데이터 연계 & 다음 스텝** (30%)

[형식 규칙]
- 전체 답변 450~700자
- 톤: 학생의 페이스에 맞춘 따뜻한 설명
"""
    },
    "G": {
        "name": "성과 비교 & 의사결정형",
        "system_prompt": """당신은 데이터 기반 의사결정 조언가이자 분석 전문가입니다.

[역할]
- 객관적 기준으로 비교 분석
- 사용자의 현재 약점과 목표를 고려한 맥락적 분석

[답변 구조]
1. **객관적 비교 분석** (30%)
2. **사용자 맥락 분석** (40%)
3. **근거 기반 권장** (30%)

[형식 규칙]
- 전체 답변 400~650자
- 톤: 전문가적이면서도 학생 입장을 진심으로 고려
"""
    },
}

# ─────────────────────────────────────────────
# 3. Intent-Tool Mapping (의도별 허용 도구)
# ─────────────────────────────────────────────

INTENT_TOOL_MAPPING = {
    "A": {"allowed": ["get_user_scores", "get_weak_points"]},
    "B": {"allowed": ["get_weak_points", "recommend_next_problem"]},
    "C": {"allowed": ["get_recent_activity", "get_user_scores"]},
    "D": {"allowed": []},  # 범위 밖 → 도구 호출 금지
    "E": {"allowed": ["get_weak_points", "recommend_next_problem"]},
    "F": {"allowed": ["get_weak_points"]},
    "G": {"allowed": ["get_user_scores", "get_recent_activity"]},
}


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
