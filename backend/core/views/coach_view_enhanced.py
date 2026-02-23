"""
AI Coach Agent View (고도화 버전) - Intent Analysis + Response Strategy
======================================================================

패턴:
1. 의도 분석 단계 (Intent Analyzer): 사용자 질문 → A-G 유형 분류
2. 응답 전략 단계 (Response Strategy): 의도에 맞는 도구 활용 & 응답 생성

A. 데이터 조회형 - 성적, 약점, 진행 현황
B. 학습 방법형 - 디버깅, 의사코드 등 학습 방법론
C. 동기부여형 - 자신감, 성장 격려
D. 범위 밖 질문 - 학습 범위 안내
E. 문제 풀이 지원형 - 문제 풀이 과정, 코드 분석
F. 개념 설명형 - 스택, 재귀, 정렬 등 개념
G. 성과 비교 & 의사결정형 - 풀이 비교, 다음 학습 방향
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
# 1. Intent Analyzer - 사용자 질문 의도 판정
# ─────────────────────────────────────────────

INTENT_ANALYSIS_PROMPT = """당신은 학습 코칭 의도 분석 전문가입니다.
사용자의 질문을 분석하여 다음 7가지 유형 중 하나로 분류해주세요.

[질문 유형 정의]

A. 데이터 조회형 (데이터 제시)
   - "내 성적 보여줘", "약점이 뭐야", "어느 정도 진행했어?"
   - 특징: 사용자 학습 데이터를 조회하고 현황을 파악하는 것

B. 학습 방법형 (방법론 제시)
   - "디버깅 공부 어떻게 해?", "의사코드 잘 쓰는 팁", "시간복잡도 이해 어떻게?"
   - 특징: 구체적인 학습 방법론과 실행 계획 필요

C. 동기부여형 (격려 + 성장 확인)
   - "자신감이 없어", "잘할 수 있을까", "나는 왜 이것도 못 하지"
   - 특징: 감정 인정 + 성장 데이터 확인 + 격려 필요

D. 범위 밖 질문 (범위 안내)
   - "파이썬 문법 알려줘", "날씨가 어때?", "주식 추천해줘"
   - 특징: 학습 코칭 범위를 벗어남

E. 문제 풀이 지원형 (힌트 + 단계별 가이드)
   - "이 문제 못 풀었어", "풀이 과정 알려줘", "이 코드 뭐가 틀렸어?"
   - 특징: 특정 문제/코드 분석 필요, 직접 답변 금지

F. 개념 설명형 (수준별 설명)
   - "스택이 뭐야?", "정렬 알고리즘 차이", "재귀 어려워"
   - 특징: 개념을 사용자 수준에 맞게 설명 필요

G. 성과 비교 & 의사결정형 (비교 분석 + 권장)
   - "이 풀이가 더 나아?", "어떤 방법 추천해?", "다음은 뭐 풀어야 해?"
   - 특징: 객관적 비교와 근거 기반 권장 필요

[응답 형식]
반드시 아래 JSON으로만 응답하세요:
{
  "intent_type": "A|B|C|D|E|F|G",
  "confidence": 0.0~1.0,
  "reasoning": "이 유형으로 판정한 이유 (1~2문장)",
  "key_indicators": ["질문에서 발견된 핵심 키워드 1", "키워드 2"]
}

[분석 규칙]
- 불명확한 경우 가장 가능성 높은 것으로 선택
- "내 약점 알려주고 어떻게 공부할지도 알려줘" → A+B 혼합이면 A(데이터 먼저)
- 감정이 포함되면 C의 가능성 상향
"""

# ─────────────────────────────────────────────
# 2. Response Strategy Prompts (유형별)
# ─────────────────────────────────────────────

RESPONSE_STRATEGIES = {
    "A": {
        "name": "데이터 조회형",
        "data_ratio": 0.8,
        "advice_ratio": 0.2,
        "system_template": """당신은 AI 학습 코치입니다.

[역할: 데이터 기반 인사이트 제공]
- 사용자 학습 데이터를 제시하고 의미를 해석
- 단순 숫자 나열 금지: "~점이니까 ~수준이야" 식으로 해석
- 잘하는 부분은 칭찬, 부족한 부분은 솔직하게

[응답 구조]
1. 핵심 수치 2~3개 제시 + 해석 (80%)
2. 부족한 영역 간단히 언급 (20%)

[형식]
- 300~500자
- 마크다운 불릿(-)과 짧은 제목(##)
- 한국어, 친근한 톤
""",
    },
    "B": {
        "name": "학습 방법형",
        "data_ratio": 0.2,
        "advice_ratio": 0.8,
        "system_template": """당신은 AI 학습 코치이자 학습 방법론 전문가입니다.

[역할: 수준별 학습 방법론 제시]
- 도구로 사용자의 현재 수준 파악
- 수준에 맞는 구체적 학습 방법론 제시 (메인)
- 데이터는 근거로만 간략히 언급

[응답 구조]
1. 현재 수준 파악 (20%)
2. 구체적 학습 방법론 단계별 제시 (70%)
3. 지금 당장 할 수 있는 행동 (10%)

[형식]
- 400~600자
- "방법 1: ~", "방법 2: ~" 식 단계별 구성
- 실행 가능한 구체적 행동 제시
""",
    },
    "C": {
        "name": "동기부여형",
        "data_ratio": 0.4,
        "advice_ratio": 0.6,
        "system_template": """당신은 따뜻한 AI 학습 멘토입니다.

[역할: 감정 인정 + 성장 확인 + 격려]
- 사용자의 감정을 먼저 인정
- 데이터로 과거 대비 성장을 증명
- 구체적 성공 사례 제시
- 거짓 격려 금지, 현실적이면서 따뜻하게

[응답 구조]
1. 감정 인정 & 공감 (20%)
2. 성장 데이터 제시 + 긍정 해석 (40%)
3. 구체적 성공 사례 & 다음 목표 (40%)

[형식]
- 300~500자
- "너는 실제로 ~해서 좋아졌어"로 개인화
- 마음을 담은 따뜻한 톤
""",
    },
    "D": {
        "name": "범위 밖 질문",
        "data_ratio": 0.0,
        "advice_ratio": 1.0,
        "system_template": """당신은 AI 학습 코치입니다.

[역할: 범위 안내 + 자연스러운 유도]
- 학습 코칭 범위를 명확하고 정중하게 안내
- 관련된 학습 질문으로 자연스럽게 유도

[응답 구조]
1. 범위 안내 (60%)
2. 관련 학습 질문 제시 (40%)

[형식]
- 200~300자
- 정중하면서도 따뜻한 톤
""",
    },
    "E": {
        "name": "문제 풀이 지원형",
        "data_ratio": 0.1,
        "advice_ratio": 0.9,
        "system_template": """당신은 Socratic Method(소크라테스 대화법) 전문가입니다.

[역할: 단계별 힌트 제시, 자력 완성 유도]
- 정답 직접 제시 금지
- 문제의 핵심 요구사항 재확인
- 사용자 약점 기반 맞춤 힌트
- 검산 포인트 안내

[응답 구조]
1. 문제 재확인: "이 문제가 요구하는 핵심은..." (20%)
2. 맞춤 힌트: "너는 ~에 약해 보이니까..." (60%)
3. 검산 포인트: "여기서 확인해봐" (20%)

[형식]
- 300~500자
- 질문 형태로 유도
""",
    },
    "F": {
        "name": "개념 설명형",
        "data_ratio": 0.3,
        "advice_ratio": 0.7,
        "system_template": """당신은 개념 설명 전문가이자 개인화 튜터입니다.

[역할: 사용자 수준에 맞는 설명]
- 사용자의 현재 수준을 데이터로 파악
- 개인화된 비유/예시 제시
- 학습 데이터와 연계: "너는 배열이 강하니까, 스택도 이렇게 생각해봐"

[응답 구조]
1. 기초 설명 (30%)
2. 개인화 비유/예시 (40%)
3. 학습 데이터 연계 (30%)

[형식]
- 400~600자
- "이것은 ~와 비슷해", "너는 ~해서 여기서도 같은 원리야" 식 개인화
""",
    },
    "G": {
        "name": "성과 비교 & 의사결정형",
        "data_ratio": 0.5,
        "advice_ratio": 0.5,
        "system_template": """당신은 근거 기반 의사결정 조언가입니다.

[역할: 객관적 비교 + 사용자 맥락 고려]
- 객관적 비교: 시간복잡도, 가독성, 학습 효과
- 사용자 약점 고려한 권장
- 선택 근거 명확히 설명

[응답 구조]
1. 객관적 비교 (30%)
2. 사용자 맥락 분석 (40%)
3. 근거 기반 권장 (30%)

[형식]
- 350~500자
- "A는 ~지만, 너는 ~에 약하니까 B를 추천해"
- 명확한 근거 제시
""",
    },
}

# ─────────────────────────────────────────────
# 3. Tool 정의 (기존과 동일)
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
                        "description": "분석할 유닛 ID",
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
                        "description": "추천받을 유닛 ID",
                    }
                },
                "required": [],
            },
        },
    },
]

# ─────────────────────────────────────────────
# 4. Tool 실행 함수 (기존과 동일)
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
    """특정 유닛의 약점 분석"""
    solved_records = UserSolvedProblem.objects.filter(
        user=profile,
        practice_detail__practice_id=unit_id,
        is_best_score=True,
    ).select_related('practice_detail')

    if not solved_records.exists():
        return {"unit_id": unit_id, "message": "풀이 기록이 없습니다.", "weak_areas": []}

    metric_scores = {}

    for record in solved_records:
        data = record.submitted_data or {}
        _extract_metrics(data, metric_scores, unit_id)

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
        evaluation = data.get("evaluation", {})
        dimensions = evaluation.get("dimensions", {})
        for dim_name, dim_data in dimensions.items():
            score = dim_data.get("score", 0) if isinstance(dim_data, dict) else 0
            metric_scores.setdefault(dim_name, []).append(score)

    elif unit_id == "unit02":
        llm_eval = data.get("llm_evaluation") or {}
        for fb in llm_eval.get("step_feedbacks", []):
            step_score = fb.get("step_score")
            if isinstance(step_score, (int, float)):
                metric_scores.setdefault("디버깅_정확도", []).append(step_score)
        thinking = llm_eval.get("thinking_score")
        if isinstance(thinking, (int, float)):
            metric_scores.setdefault("사고력", []).append(thinking)
        risk = llm_eval.get("code_risk")
        if isinstance(risk, (int, float)):
            metric_scores.setdefault("코드_안전성", []).append(100 - risk)

    elif unit_id == "unit03":
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

    mastered_ids = set(
        UserSolvedProblem.objects.filter(
            user=profile, is_best_score=True, score__gte=70
        ).values_list('practice_detail_id', flat=True)
    )

    recommendations = []
    for detail in details_qs.select_related('practice').order_by('practice__unit_number', 'display_order'):
        if detail.id in mastered_ids:
            continue

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
# 5. Tool 디스패처 및 라벨
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
# 7. Intent별 허용 도구 매핑
# ─────────────────────────────────────────────

INTENT_TOOL_MAPPING = {
    "A": {
        "allowed": ["get_user_scores", "get_weak_points"],
        "required": ["get_user_scores"],  # 최소한 성적은 필요
    },
    "B": {
        "allowed": ["get_weak_points", "recommend_next_problem"],
        "required": [],  # 도구 선택적
    },
    "C": {
        "allowed": ["get_recent_activity", "get_user_scores"],
        "required": ["get_recent_activity"],  # 최근 활동 필수
    },
    "D": {
        "allowed": [],  # 범위 밖 → 도구 호출 금지
        "required": [],
    },
    "E": {
        "allowed": ["get_weak_points", "recommend_next_problem"],
        "required": [],  # 도구 선택적
    },
    "F": {
        "allowed": ["get_weak_points"],
        "required": [],  # 도구 선택적
    },
    "G": {
        "allowed": ["get_user_scores", "get_recent_activity"],
        "required": ["get_user_scores"],  # 성적 비교 필수
    },
}

# ─────────────────────────────────────────────
# 8. Tool Argument Schema 및 검증
# ─────────────────────────────────────────────

TOOL_ARG_SCHEMA = {
    "get_user_scores": {},
    "get_weak_points": {
        "unit_id": {"required": True, "allowed": ["unit01", "unit02", "unit03"]},
    },
    "get_recent_activity": {
        "limit": {"required": False, "default": 10},
    },
    "recommend_next_problem": {
        "unit_id": {"required": False, "allowed": ["unit01", "unit02", "unit03"]},
    },
}


def validate_and_normalize_args(fn_name, fn_args):
    """도구 인자 검증 및 기본값 적용"""
    schema = TOOL_ARG_SCHEMA.get(fn_name, {})
    normalized = dict(fn_args)
    for arg_name, rules in schema.items():
        if rules.get("required") and arg_name not in normalized:
            raise ValueError(f"[{fn_name}] 필수 인자 누락: {arg_name}")
        if arg_name in normalized and "allowed" in rules:
            if normalized[arg_name] not in rules["allowed"]:
                raise ValueError(f"[{fn_name}] 잘못된 {arg_name}: '{normalized[arg_name]}'")
        if arg_name not in normalized and "default" in rules:
            normalized[arg_name] = rules["default"]
    return normalized


# ─────────────────────────────────────────────
# 9. Tool 결과 충분도 평가
# ─────────────────────────────────────────────

class ToolResultEvaluator:
    """Tool 호출 결과가 의도에 맞게 충분한지 평가"""

    def is_sufficient(self, tool_results, intent_type):
        """이 결과로 충분한가?"""
        required_tools = INTENT_TOOL_MAPPING.get(intent_type, {}).get("required", [])

        # 필수 도구가 없으면 충분
        if not required_tools:
            return True

        # 호출된 도구 이름 수집
        called_tools = {tr.get("tool") for tr in tool_results if tr.get("tool")}

        # 모든 필수 도구가 호출되었는가?
        return all(tool in called_tools for tool in required_tools)

    def missing_tools(self, tool_results, intent_type):
        """빠진 필수 도구는?"""
        required_tools = INTENT_TOOL_MAPPING.get(intent_type, {}).get("required", [])
        called_tools = {tr.get("tool") for tr in tool_results if tr.get("tool")}
        return [t for t in required_tools if t not in called_tools]


# ─────────────────────────────────────────────
# 6. Enhanced AI Coach View
# ─────────────────────────────────────────────

class AICoachEnhancedView(APIView):
    """
    의도 분석 + 응답 전략 기반 AI 코치

    플로우:
    1. [의도 분석] 사용자 질문 → A-G 중 분류
    2. [응답 전략] 의도별 프롬프트로 도구 호출 & 응답 생성
    3. [SSE 스트리밍] 사고 과정 + 도구 호출 + 최종 응답 전달
    """
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

        def _sse(data):
            return f"data: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"

        def event_stream():
            called_tools_cache = {}  # ← 추가: Tool 중복 호출 방지 캐시
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
                    model="gpt-5-mini",
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
                # Step 2: Response Strategy
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
                filtered_tools = [t for t in COACH_TOOLS if t["function"]["name"] in allowed_tools]

                # ── Tool 결과 평가 준비 ──
                evaluator = ToolResultEvaluator()
                tool_results = []
                tools_sufficient = False  # ← 다음 iteration에서 tool_choice 제한 여부

                max_iterations = 5
                for iteration in range(max_iterations):
                    yield _sse({
                        "type": "thinking",
                        "stage": "response_generation",
                        "message": f"분석 중입니다... ({iteration + 1}/{max_iterations})",
                    })

                    # ── 도구 제공 여부: 충분도에 따라 결정 ──
                    if tools_sufficient:
                        # 데이터 충분 → 도구 제공 안 함 (최종 응답만 생성)
                        tools_to_use = openai.NOT_GIVEN
                        tool_choice_param = openai.NOT_GIVEN
                    else:
                        # 데이터 부족 → 도구 제공 (필요시 추가 호출)
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

                    # ──────────────────────────────────────
                    # 스트리밍 처리: tool_calls vs content
                    # ──────────────────────────────────────

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

                        # Content 토큰 → 즉시 전송
                        if delta.content:
                            yield _sse({"type": "token", "token": delta.content})

                    # Tool calls 없으면 완료
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

                        # ── Tool 결과 수집 ──
                        tool_results.append({
                            "tool": fn_name,
                            "args": fn_args_raw,
                            "result": result_data,
                        })

                    # ── Tool 호출이 있었는지 + 데이터 충분도 평가 ──
                    if is_tool_call:
                        if evaluator.is_sufficient(tool_results, intent_type):
                            # 필수 도구 모두 호출됨 → 다음 iteration에서 최종 응답 생성
                            logger.debug(f"[충분도 평가] Intent {intent_type}: 데이터 충분")
                            tools_sufficient = True
                    # (Tool 호출이 없으면 다음 iteration에서 자동으로 최종 응답 생성됨)

                # max_iterations 도달 (Tool 호출이 계속되는 경우)
                yield _sse({
                    "type": "token",
                    "token": "분석이 복잡하여 일부만 완료되었습니다. 질문을 더 구체적으로 해주세요.",
                })
                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"[AICoachEnhanced] Error: {e}", exc_info=True)
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
