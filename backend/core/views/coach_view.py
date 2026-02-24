"""
AI Coach Agent View - ReAct 패턴 기반 학습 코칭 Agent
OpenAI function calling(tool use)을 사용하여 LLM이 스스로 도구를 선택하고
DB를 조회하는 Agent loop 구현.
"""

import json
import logging
import openai
from django.conf import settings
from django.db.models import Avg, Max, Count
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from core.models import (
    UserProfile, UserSolvedProblem, Practice, PracticeDetail
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 1. Tool 정의 (OpenAI function calling schema)
# ─────────────────────────────────────────────

COACH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_user_scores",
            "description": "유저의 유닛별 평균 점수, 최고 점수, 풀이 수, 완료율을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weak_points",
            "description": "특정 유닛에서 유저의 약점(70점 미만 메트릭)을 분석합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "unit_id": {
                        "type": "string",
                        "enum": ["unit01", "unit02", "unit03"],
                        "description": "분석할 유닛 ID (unit01=의사코드, unit02=디버깅, unit03=시스템아키텍처)",
                    }
                },
                "required": ["unit_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_activity",
            "description": "유저의 최근 학습 활동(풀이 기록)을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "조회할 최근 기록 수 (기본값: 10)",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_next_problem",
            "description": "아직 풀지 않았거나 점수가 낮은 문제를 추천합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "unit_id": {
                        "type": "string",
                        "enum": ["unit01", "unit02", "unit03"],
                        "description": "추천받을 유닛 ID (미지정 시 전체)",
                    }
                },
                "required": [],
            },
        },
    },
]


# ─────────────────────────────────────────────
# 2. Tool 실행 함수 (실제 DB 쿼리)
# ─────────────────────────────────────────────

def tool_get_user_scores(profile):
    """유닛별 평균점수, 최고점수, 풀이수, 완료율 조회"""
    practices = Practice.objects.filter(is_active=True).order_by('unit_number')
    result = []

    for practice in practices:
        total_problems = PracticeDetail.objects.filter(
            practice=practice, is_active=True, detail_type='PROBLEM'
        ).count()

        solved = UserSolvedProblem.objects.filter(
            user=profile,
            practice_detail__practice=practice,
            is_best_score=True,
        )
        stats = solved.aggregate(
            avg_score=Avg('score'),
            max_score=Max('score'),
            solved_count=Count('practice_detail', distinct=True),
        )

        avg_score = round(stats['avg_score'] or 0, 1)
        solved_count = stats['solved_count'] or 0
        completion_rate = min(round(solved_count / total_problems * 100, 1), 100) if total_problems > 0 else 0

        result.append({
            "unit_id": practice.id,
            "unit_title": practice.title,
            "avg_score": avg_score,
            "max_score": stats['max_score'] or 0,
            "solved_count": solved_count,
            "total_problems": total_problems,
            "completion_rate": completion_rate,
        })

    return result


def tool_get_weak_points(profile, unit_id):
    """특정 유닛의 약점 분석 - submitted_data에서 세부 메트릭 추출"""
    solved_records = UserSolvedProblem.objects.filter(
        user=profile,
        practice_detail__practice_id=unit_id,
        is_best_score=True,
    ).select_related('practice_detail')

    if not solved_records.exists():
        return {"unit_id": unit_id, "message": "풀이 기록이 없습니다.", "weak_areas": []}

    metric_scores = {}  # { metric_name: [scores] }

    for record in solved_records:
        data = record.submitted_data or {}
        _extract_metrics(data, metric_scores, unit_id)

    # 평균 70점 미만 메트릭 = weak_area
    weak_areas = []
    all_metrics = []
    for metric, scores in metric_scores.items():
        avg = round(sum(scores) / len(scores), 1) if scores else 0
        entry = {"metric": metric, "avg_score": avg, "sample_count": len(scores)}
        all_metrics.append(entry)
        if avg < 70:
            weak_areas.append(entry)

    return {
        "unit_id": unit_id,
        "total_solved": solved_records.count(),
        "weak_areas": weak_areas,
        "all_metrics": all_metrics,
    }


def _extract_metrics(data, metric_scores, unit_id):
    """submitted_data에서 유닛별 평가 메트릭 추출"""
    if unit_id == "unit01":
        # Unit 1: submitted_data.evaluation.dimensions
        evaluation = data.get("evaluation", {})
        dimensions = evaluation.get("dimensions", {})
        for dim_name, dim_data in dimensions.items():
            score = dim_data.get("score", 0) if isinstance(dim_data, dict) else 0
            metric_scores.setdefault(dim_name, []).append(score)

    elif unit_id == "unit02":
        # Unit 2: submitted_data.llm_evaluation
        llm_eval = data.get("llm_evaluation") or {}
        # step별 디버깅 점수
        for fb in llm_eval.get("step_feedbacks", []):
            step_score = fb.get("step_score")
            if isinstance(step_score, (int, float)):
                metric_scores.setdefault("디버깅_정확도", []).append(step_score)
        # 사고력 점수
        thinking = llm_eval.get("thinking_score")
        if isinstance(thinking, (int, float)):
            metric_scores.setdefault("사고력", []).append(thinking)
        # 코드 위험도 (낮을수록 좋음 → 100에서 빼서 점수화)
        risk = llm_eval.get("code_risk")
        if isinstance(risk, (int, float)):
            metric_scores.setdefault("코드_안전성", []).append(100 - risk)

    elif unit_id == "unit03":
        # Unit 3: submitted_data.evaluation_result.pillarScores
        eval_result = data.get("evaluation_result", {})
        pillar_scores = eval_result.get("pillarScores", {})
        for pillar, score in pillar_scores.items():
            if isinstance(score, (int, float)):
                metric_scores.setdefault(pillar, []).append(score)


def tool_get_recent_activity(profile, limit=10):
    """최근 학습 활동 N건 조회"""
    records = UserSolvedProblem.objects.filter(
        user=profile
    ).select_related('practice_detail__practice').order_by('-solved_date')[:limit]

    return [
        {
            "problem_id": r.practice_detail_id,
            "problem_title": r.practice_detail.detail_title,
            "unit_title": r.practice_detail.practice.title,
            "score": r.score,
            "is_perfect": r.is_perfect,
            "solved_date": r.solved_date.strftime("%Y-%m-%d %H:%M"),
            "attempt": r.attempt_number,
        }
        for r in records
    ]


def tool_recommend_next_problem(profile, unit_id=None):
    """안 풀었거나 낮은 점수 문제 추천"""
    details_qs = PracticeDetail.objects.filter(
        is_active=True, detail_type='PROBLEM'
    )
    if unit_id:
        details_qs = details_qs.filter(practice_id=unit_id)

    # 베스트 점수 70 이상인 문제 ID 집합
    mastered_ids = set(
        UserSolvedProblem.objects.filter(
            user=profile, is_best_score=True, score__gte=70
        ).values_list('practice_detail_id', flat=True)
    )

    recommendations = []
    for detail in details_qs.select_related('practice').order_by('practice__unit_number', 'display_order'):
        if detail.id in mastered_ids:
            continue

        # 기존 베스트 기록 확인
        best = UserSolvedProblem.objects.filter(
            user=profile, practice_detail=detail, is_best_score=True
        ).first()

        recommendations.append({
            "problem_id": detail.id,
            "problem_title": detail.detail_title,
            "unit_id": detail.practice_id,
            "unit_title": detail.practice.title,
            "current_best_score": best.score if best else None,
            "status": "재도전 필요" if best else "미풀이",
        })

        if len(recommendations) >= 5:
            break

    return recommendations if recommendations else [{"message": "모든 문제를 70점 이상으로 완료했습니다!"}]


# ─────────────────────────────────────────────
# 3. Tool 실행 디스패처
# ─────────────────────────────────────────────

TOOL_DISPATCH = {
    "get_user_scores": lambda profile, args: tool_get_user_scores(profile),
    "get_weak_points": lambda profile, args: tool_get_weak_points(profile, args.get("unit_id")),
    "get_recent_activity": lambda profile, args: tool_get_recent_activity(profile, args.get("limit", 10)),
    "recommend_next_problem": lambda profile, args: tool_recommend_next_problem(profile, args.get("unit_id")),
}

TOOL_LABELS = {
    "get_user_scores": "성적 데이터 조회",
    "get_weak_points": "약점 분석",
    "get_recent_activity": "최근 활동 조회",
    "recommend_next_problem": "문제 추천",
}


# ─────────────────────────────────────────────
# 4. Agent View (ReAct Loop)
# ─────────────────────────────────────────────

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
"""


class AICoachView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_message = request.data.get("message", "").strip()
        if not user_message:
            return Response(
                {"error": "메시지를 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not openai or not getattr(settings, 'OPENAI_API_KEY', None):
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

        THINKING_MESSAGES = [
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
                    # Agent 사고 과정 표시
                    yield _sse({
                        "type": "thinking",
                        "message": THINKING_MESSAGES[iteration],
                    })

                    # 스트리밍 호출 — tool_calls / content 모두 처리
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

                    for chunk in stream:
                        choice = chunk.choices[0] if chunk.choices else None
                        if not choice or not choice.delta:
                            continue
                        delta = choice.delta

                        # ── tool_calls 청크 수집 ──
                        if delta.tool_calls:
                            is_tool_call = True
                            for tc in delta.tool_calls:
                                idx = tc.index
                                if idx not in tool_calls_data:
                                    tool_calls_data[idx] = {
                                        "id": "", "name": "", "arguments": "",
                                    }
                                if tc.id:
                                    tool_calls_data[idx]["id"] = tc.id
                                if tc.function:
                                    if tc.function.name:
                                        tool_calls_data[idx]["name"] += tc.function.name
                                    if tc.function.arguments:
                                        tool_calls_data[idx]["arguments"] += tc.function.arguments

                        # ── content 토큰 → 즉시 SSE 전송 ──
                        if delta.content:
                            yield _sse({"type": "token", "token": delta.content})

                    # tool_calls 없으면 최종 답변이 스트리밍 완료된 것
                    if not is_tool_call:
                        yield "data: [DONE]\n\n"
                        return

                    # ── tool_calls 처리 ──
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
                            fn_args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                        except (json.JSONDecodeError, TypeError):
                            fn_args = {}

                        # step_start 이벤트
                        yield _sse({
                            "type": "step_start",
                            "tool": fn_name,
                            "label": TOOL_LABELS.get(fn_name, fn_name),
                            "args": fn_args,
                        })

                        # 도구 실행
                        executor = TOOL_DISPATCH.get(fn_name)
                        result_data = (
                            executor(profile, fn_args)
                            if executor
                            else {"error": f"알 수 없는 도구: {fn_name}"}
                        )
                        result_str = json.dumps(result_data, ensure_ascii=False, default=str)

                        # step_result 이벤트
                        yield _sse({
                            "type": "step_result",
                            "tool": fn_name,
                            "label": TOOL_LABELS.get(fn_name, fn_name),
                            "args": fn_args,
                            "result": result_data,
                        })

                        conv.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": result_str,
                        })

                # max_iterations 도달
                yield _sse({
                    "type": "token",
                    "token": "분석이 복잡하여 일부만 완료되었습니다. 질문을 더 구체적으로 해주세요.",
                })
                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"[AICoach] Agent loop 실패: {e}", exc_info=True)
                yield _sse({
                    "type": "error",
                    "message": "코칭 서비스에 일시적인 문제가 발생했습니다.",
                })
                yield "data: [DONE]\n\n"

        resp = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream; charset=utf-8",
        )
        resp["Cache-Control"] = "no-cache, no-transform"
        resp["X-Accel-Buffering"] = "no"
        return resp
