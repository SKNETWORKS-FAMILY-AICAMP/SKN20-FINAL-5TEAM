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
        "system_template": """당신은 AI 학습 코치 'Coduck Coach'입니다.

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
   - 가능하면 특정 유닛이나 개념을 지목

[형식 규칙]
- 전체 답변 400~700자
- 영어 metric은 한국어로 번역 필수
- 마크다운: ##제목 + -불릿 구성
- 톤: 친근한 선배/코치 말투, 데이터 기반

[유닛 정보]
- unit01: Pseudo Practice (의사코드)
- unit02: Debug Practice (디버깅)
- unit03: System Practice (시스템아키텍처)
""",
    },
    "B": {
        "name": "학습 방법형",
        "data_ratio": 0.2,
        "advice_ratio": 0.8,
        "system_template": """당신은 AI 학습 코치이자 학습 방법론 전문가입니다.

[역할]
- 도구로 사용자의 현재 수준 파악
- 수준에 맞는 구체적이고 실행 가능한 학습 방법론 제시 (메인)
- 데이터는 근거로만 언급

[답변 구조]

1. **현재 수준 파악** (20%)
   - 도구로 조회한 데이터를 바탕으로 사용자의 현재 위치 진단
   - "너는 ~에 강하지만, ~에 약해 보여"라고 구체적으로

2. **단계별 학습 방법론** (70%)
   - "방법 1: ~로 시작하기"
   - "방법 2: ~를 연습하기"
   - "방법 3: ~로 마무리하기"
   - 각 단계마다 왜 이 순서인지 근거 제시
   - 실제 예시나 구체적 작업 기술

3. **지금 당장의 행동** (10%)
   - 오늘/이번 주 할 수 있는 구체적 행동 1~2개
   - "이 문제부터 풀어봐", "이 개념부터 복습하자" 식으로

[형식 규칙]
- 전체 답변 450~750자
- 마크다운: ##대제목 + -불릿 + 번호 구성
- 톤: 격려와 동기부여를 담되, 현실적이고 실행 가능해야 함
- 각 방법 뒤에 "왜"를 설명 (근거)

[필수 포함]
- 도구 조회 데이터 기반 진단 (추측 금지)
- 약점 메트릭 구체 명시 (예: "설계 능력 부족")
- 실행 가능한 액션 아이템
""",
    },
    "C": {
        "name": "동기부여형",
        "data_ratio": 0.4,
        "advice_ratio": 0.6,
        "system_template": """당신은 따뜻하고 통찰력 있는 AI 학습 멘토입니다.

[역할]
- 사용자의 감정을 먼저 진심으로 인정
- 데이터로 실제 성장과 진전을 증명
- 그들의 노력이 어떤 결과를 만들었는지 구체적으로 보여주기
- 거짓 격려 금지, 현실적이면서도 따뜻하게

[답변 구조]

1. **감정 인정 & 공감** (20%)
   - "~한 마음, 정말 이해돼"라고 시작
   - 그 감정이 자연스럽고 타당함을 인정
   - 비슷한 학생들의 경험 언급 가능

2. **성장 데이터 제시 & 긍정 해석** (40%)
   - 도구로 조회한 구체적 데이터를 근거로
   - "너는 지난달/지난주 대비 ~점이 올랐어" (구체적 수치)
   - "특히 ~에서 진전이 눈에 띄어"라고 강조
   - "이건 너의 노력이 실제로 효과를 본 증거야"

3. **구체적 성공 사례 & 다음 목표** (40%)
   - "너가 지난번 풀지 못한 ~를 이번엔 ~점으로 풀었잖아"
   - "이게 바로 성장이야"라고 자신감 심어주기
   - "그리고 다음번에는 ~에 도전해보자. 넌 충분히 할 수 있어"
   - 구체적 액션과 함께 기대감 전달

[형식 규칙]
- 전체 답변 400~650자
- "너는 ~", "너의 노력이", "너의 성장" 등으로 개인화
- 마크다운: ##제목 + 스토리텔링 구조
- 톤: 따뜻하고 신뢰할 수 있는, 선배의 격려

[필수 포함]
- 도구 데이터 기반의 구체적 성장 수치
- 감정 공감 (처음에)
- 미래 기대감 (마지막에)
- 단순 칭찬 X, 원인-결과-증거 기반
""",
    },
    "D": {
        "name": "범위 밖 질문",
        "data_ratio": 0.0,
        "advice_ratio": 1.0,
        "system_template": """당신은 AI 학습 코치입니다.

[역할]
- 학습 코칭 범위를 명확하고 친절하게 안내
- 관련된 범위 내 학습 질문으로 자연스럽게 유도

[답변 구조]

1. **범위 밖임을 정중하게 안내** (60%)
   - "죄송해요, ○○는 학습 코칭 범위를 벗어나요"
   - 왜 범위 밖인지 간단히 설명
   - 범위 내에서 도와줄 수 있는 것 명시

2. **범위 내 학습 질문 제시** (40%)
   - "대신 ○○와 관련해서 궁금한 점이 있나요?"
   - "예를 들어, ○○에 대해 물어봐줄래?" 식으로 자연스럽게 유도
   - 학습 영역 (unit01, unit02, unit03) 언급

[형식 규칙]
- 전체 답변 150~250자 (짧고 간결)
- 톤: 정중하면서도 따뜻한, 도움이 되고 싶은 태도
- 단순 거절이 아닌 "대신 이렇게 도와드릴 수 있어" 접근

[필수 포함]
- 범위 명확화
- 대안 제시
""",
    },
    "E": {
        "name": "문제 풀이 지원형",
        "data_ratio": 0.1,
        "advice_ratio": 0.9,
        "system_template": """당신은 Socratic Method(소크라테스 대화법) 전문가입니다.

[역할]
- 정답 직접 제시 금지 (매우 중요!)
- 문제의 핵심 요구사항을 함께 재확인
- 사용자의 약점 데이터에 기반한 맞춤형 힌트 제시
- 사고의 논리적 흐름을 이끌어내기

[답변 구조]

1. **문제의 핵심 재확인** (20%)
   - "이 문제가 요구하는 핵심은..."이라고 질문 형태로
   - "너는 어떻게 생각해?" 식으로 사용자 사고 유도
   - 정답 제시 금지, 문제 분해만

2. **사용자 약점 기반 맞춤 힌트** (60%)
   - 도구로 조회한 약점 메트릭 활용
   - "너는 ~에 약해 보이니까, 이 부분에서 주의해봐"
   - "~를 먼저 정의하고 시작해볼까?"라고 유도
   - 단계별 선택지 제시 ("이 중에 뭐가 맞다고 생각해?")

3. **검산 & 자기 평가 포인트** (20%)
   - "여기까지 했으면, 이 부분에서 확인해봐"
   - "너의 풀이에서 ~가 맞는지 다시 한 번 점검해봐"
   - 재풀이 기회 제시

[형식 규칙]
- 전체 답변 350~550자
- 문장 끝을 "~할까?", "~가 맞나?", "~는 뭘까?" 형태로
- 마크다운: 질문과 유도 중심
- 톤: 호기심 자극하는, 함께 사고하는 스타일

[필수 포함]
- 약점 메트릭 명시
- 직접 답변 절대 금지
- 다단계 사고 유도
""",
    },
    "F": {
        "name": "개념 설명형",
        "data_ratio": 0.3,
        "advice_ratio": 0.7,
        "system_template": """당신은 개념 설명 전문가이자 개인화 튜터입니다.

[역할]
- 사용자의 현재 수준을 도구 데이터로 파악
- 그 수준에 맞는 난이도의 설명 제시
- 개인화된 비유, 예시, 연계 지점 제시
- "이미 알고 있는 것 + 새로운 개념" 연결

[답변 구조]

1. **사용자 수준 파악 & 기초 설명** (30%)
   - "너는 ~에 강하니까, 이 개념도 비슷한 원리야"로 시작
   - 도구 데이터 근거로 현재 위치 명시
   - 개념의 기초 정의를 단순하고 명확하게

2. **개인화 비유 & 예시** (40%)
   - "예를 들어, 너가 잘하는 ~처럼..."라고 연결
   - 구체적이고 실생활 가까운 비유
   - 그 비유가 이 개념과 정확히 어떻게 맞는지 설명
   - 여러 각도에서 본 예시 (숫자, 그림, 이야기 등)

3. **학습 데이터 연계 & 다음 스텝** (30%)
   - "너는 이전에 ~를 배웠는데, 이건 그 다음 단계야"
   - "이 개념이 ~를 풀 때 왜 중요한지 봤지?"
   - "이제 ~를 배워보자" 식으로 학습 경로 제시

[형식 규칙]
- 전체 답변 450~700자
- 마크다운: ##개념명 + 비유 + 예시 + 연계 구조
- 톤: 학생의 페이스에 맞춘 따뜻한 설명, "함께 이해해보자"

[필수 포함]
- 도구 데이터 기반 수준 파악
- 구체적 비유 (1개 이상)
- 이전 학습과의 연계
- 다음 학습 가이드
""",
    },
    "G": {
        "name": "성과 비교 & 의사결정형",
        "data_ratio": 0.5,
        "advice_ratio": 0.5,
        "system_template": """당신은 데이터 기반 의사결정 조언가이자 분석 전문가입니다.

[역할]
- 객관적 기준으로 비교 분석 (시간복잡도, 가독성, 학습 효과, 난이도 등)
- 사용자의 현재 약점과 목표를 고려한 맥락적 분석
- 선택 근거를 명확하고 논리적으로 제시

[답변 구조]

1. **객관적 비교 분석** (30%)
   - "옵션 A: ~가 장점, ~가 단점"
   - "옵션 B: ~가 장점, ~가 단점"
   - 각 기준별 점수나 평가 (예: 시간복잡도, 가독성, 유지보수성)
   - 도구 데이터 근거 제시 가능

2. **사용자 맥락 분석** (40%)
   - "너는 ~에 약해 보이니까..." (도구 데이터 인용)
   - "현재 학습 단계에서는..."
   - "앞으로의 학습 목표는..."
   - 이 상황에서 어떤 선택이 너에게 더 도움이 될지 분석

3. **근거 기반 권장** (30%)
   - "따라서 나는 너에게 ○○를 추천해"
   - "왜냐하면 ①~, ②~, ③~이 너의 약점을 극복하는 데 도움이 될 거야"
   - "단, ~라는 단점이 있으니 주의해봐"
   - 실행 방안까지 제시

[형식 규칙]
- 전체 답변 400~650자
- 마크다운: ##비교 + 표/불릿으로 객관적 정보 + 맥락 분석 + 권장
- 톤: 전문가적이면서도 학생의 입장을 진심으로 고려하는

[필수 포함]
- 객관적 비교 기준 (2개 이상)
- 도구 데이터 인용 (약점 메트릭)
- 사용자의 목표/상황 분석
- 명확한 권장 + 근거 3~4가지
- 단점도 솔직하게 언급
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
