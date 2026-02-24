"""AI Coach tool schema and DB-backed tool executors."""

from django.db.models import Avg, Max, Count

from core.models import UserSolvedProblem, Practice, PracticeDetail


COACH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_user_scores",
            "description": "유저의 유닛별 평균 점수, 최고 점수, 풀이 수, 완료율을 조회합니다.",
            "parameters": {"type": "object", "properties": {}, "required": []},
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
    {
        "type": "function",
        "function": {
            "name": "get_unit_curriculum",
            "description": "특정 유닛의 학습 목표, 핵심 개념, 훈련 스킬, 공부 팁을 조회합니다. 학습 방법이나 개념 관련 질문에 사용하세요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "unit_id": {
                        "type": "string",
                        "enum": ["unit01", "unit02", "unit03"],
                        "description": "조회할 유닛 ID (unit01=의사코드, unit02=디버깅, unit03=시스템아키텍처)",
                    }
                },
                "required": ["unit_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_study_guide",
            "description": "유저의 약점 메트릭을 기반으로 맞춤 학습 가이드를 생성합니다. 무엇을 어떻게 공부해야 하는지 구체적 방향을 제시합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "unit_id": {
                        "type": "string",
                        "enum": ["unit01", "unit02", "unit03"],
                        "description": "학습 가이드를 생성할 유닛 ID",
                    }
                },
                "required": ["unit_id"],
            },
        },
    },
]


def tool_get_user_scores(profile):
    """유닛별 평균점수, 최고점수, 풀이수, 완료율 조회"""
    practices = Practice.objects.filter(is_active=True).order_by("unit_number")
    result = []

    for practice in practices:
        total_problems = PracticeDetail.objects.filter(
            practice=practice, is_active=True, detail_type="PROBLEM"
        ).count()

        solved = UserSolvedProblem.objects.filter(
            user=profile,
            practice_detail__practice=practice,
            is_best_score=True,
        )
        stats = solved.aggregate(
            avg_score=Avg("score"),
            max_score=Max("score"),
            solved_count=Count("practice_detail", distinct=True),
        )

        avg_score = round(stats["avg_score"] or 0, 1)
        solved_count = stats["solved_count"] or 0
        completion_rate = (
            min(round(solved_count / total_problems * 100, 1), 100)
            if total_problems > 0
            else 0
        )

        result.append(
            {
                "unit_id": practice.id,
                "unit_title": practice.title,
                "avg_score": avg_score,
                "max_score": stats["max_score"] or 0,
                "solved_count": solved_count,
                "total_problems": total_problems,
                "completion_rate": completion_rate,
            }
        )

    return result


def tool_get_weak_points(profile, unit_id):
    """특정 유닛의 약점 분석 - submitted_data에서 세부 메트릭 추출"""
    solved_records = UserSolvedProblem.objects.filter(
        user=profile,
        practice_detail__practice_id=unit_id,
        is_best_score=True,
    ).select_related("practice_detail")

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
    records = (
        UserSolvedProblem.objects.filter(user=profile)
        .select_related("practice_detail__practice")
        .order_by("-solved_date")[:limit]
    )

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


UNIT_CURRICULUM = {
    "unit01": {
        "name": "의사코드(Pseudo Code) 연습",
        "goal": "ML 파이프라인을 코드 없이 논리적으로 설계하는 능력 훈련",
        "core_concepts": [
            "데이터 전처리 파이프라인 (fit/transform 분리, 데이터 누수 방지)",
            "과적합 방어 (Ridge/Lasso 정규화, 교차검증)",
            "불균형 데이터 처리 (SMOTE, 평가지표 선택)",
            "피처 엔지니어링 (특성 생성/변환/선택)",
            "하이퍼파라미터 튜닝 (GridSearch, 교차검증)",
            "모델 해석성 (SHAP, 공정성 검증)",
        ],
        "skills_trained": ["논리적 설계력", "ML 개념 이해", "추상화 능력"],
        "difficulty": "중급",
        "study_tips": [
            "문제를 읽고 바로 코드를 쓰지 말고, 단계별 흐름을 먼저 정리해봐",
            "fit과 transform의 분리가 왜 중요한지 이해하는 게 핵심",
            "점수가 낮다면 '설계력(design)'과 '일관성(consistency)' 차원을 집중 개선해봐",
        ],
    },
    "unit02": {
        "name": "디버깅(Bug Hunt) 연습",
        "goal": "버그가 있는 코드를 읽고, 원인을 분석하고, 수정하는 디버깅 사고력 훈련",
        "core_concepts": [
            "TypeError / ValueError 등 타입 관련 버그",
            "로직 에러 (off-by-one, 조건문 실수)",
            "데이터 처리 버그 (인덱싱, 슬라이싱, NaN 처리)",
            "ML 파이프라인 버그 (데이터 누수, 스케일링 순서)",
            "딥러닝 학습 버그 (gradient, loss, optimizer 설정)",
        ],
        "skills_trained": ["디버깅 사고력", "코드 분석력", "버그 패턴 인식"],
        "difficulty": "초급~중급",
        "study_tips": [
            "코드를 한 줄씩 따라가며 변수 값이 어떻게 변하는지 추적하는 습관을 들여봐",
            "에러 메시지를 먼저 읽고 타입과 위치를 파악하는 게 첫 번째 스텝",
            "틀렸을 때 왜 틀렸는지 설명하는 연습이 사고력 향상에 핵심이야",
        ],
    },
    "unit03": {
        "name": "시스템 아키텍처 설계 연습",
        "goal": "클라우드 기반 시스템 아키텍처를 설계하고 트레이드오프를 분석하는 능력 훈련",
        "core_concepts": [
            "보안 (Security) — 인증, 암호화, 접근 제어",
            "신뢰성 (Reliability) — 장애 복구, 이중화, 백업",
            "성능 (Performance) — 캐싱, 로드밸런싱, 최적화",
            "비용 최적화 (Cost) — 리소스 효율, 스케일링 전략",
            "운영 우수성 (Operational Excellence) — 모니터링, CI/CD",
            "지속가능성 (Sustainability) — 에너지 효율, 장기 유지보수",
        ],
        "skills_trained": ["시스템 설계력", "트레이드오프 분석", "아키텍처 패턴 이해"],
        "difficulty": "중급~고급",
        "study_tips": [
            "하나의 정답이 아니라 각 설계의 트레이드오프를 설명하는 게 핵심",
            "pillar(기둥) 점수가 낮은 영역을 집중적으로 학습해봐",
            "실제 클라우드 아키텍처 사례를 읽어보면 감이 빨리 잡혀",
        ],
    },
}


STUDY_GUIDE_MAP = {
    "unit01": {
        "design": {
            "concept": "논리적 설계 순서",
            "guide": "문제를 읽고 바로 답을 쓰지 말고, '입력→처리→출력' 순서로 단계를 먼저 나눠봐. 각 단계에서 어떤 함수/도구를 쓸지 명시하면 설계력 점수가 올라가.",
        },
        "consistency": {
            "concept": "데이터 일관성 유지",
            "guide": "fit은 train에만, transform은 train+test 모두에 적용하는 원칙을 외워. 이 원칙만 지켜도 일관성 점수가 크게 올라.",
        },
        "abstraction": {
            "concept": "추상화 능력",
            "guide": "구현 디테일보다 '무엇을 하는지'를 먼저 서술해봐. '데이터를 정규화한다'가 아니라 '스케일 차이를 제거하여 모델 수렴 속도를 높인다'처럼 목적 중심으로 써봐.",
        },
        "edgeCase": {
            "concept": "예외 상황 처리",
            "guide": "결측값, 이상치, 클래스 불균형 같은 예외 상황을 항상 고려해봐. '만약 ~라면?' 질문을 스스로 던지는 습관이 중요해.",
        },
        "implementation": {
            "concept": "구현 구체성",
            "guide": "의사코드에서 구체적인 함수명이나 파라미터를 명시해봐. 'StandardScaler().fit(X_train)'처럼 실행 가능한 수준으로 적으면 구현력 점수가 올라.",
        },
    },
    "unit02": {
        "디버깅_정확도": {
            "concept": "버그 위치 정확히 짚기",
            "guide": "에러 메시지의 타입과 라인 번호를 먼저 확인하고, 해당 줄의 변수 타입을 추적해봐. print() 디버깅도 좋은 습관이야.",
        },
        "사고력": {
            "concept": "디버깅 논리적 사고",
            "guide": "버그를 찾을 때 '이 코드가 의도한 동작'과 '실제 동작'을 비교하는 습관을 들여봐. 왜 다른지를 설명할 수 있으면 사고력이 올라가.",
        },
        "코드_안전성": {
            "concept": "안전한 코드 수정",
            "guide": "버그를 고칠 때 다른 부분에 영향이 없는지 항상 확인해봐. 하나를 고치면서 다른 버그를 만들지 않는 게 핵심이야.",
        },
    },
    "unit03": {
        "security": {
            "concept": "보안 설계",
            "guide": "인증(Authentication)과 인가(Authorization)를 구분하고, 데이터 암호화(at rest / in transit)를 항상 고려해봐.",
        },
        "reliability": {
            "concept": "신뢰성 설계",
            "guide": "단일 장애 지점(SPOF)을 찾아 이중화/페일오버를 설계해봐. 장애가 나면 어떻게 복구할지 시나리오를 항상 생각해.",
        },
        "performance": {
            "concept": "성능 최적화",
            "guide": "캐싱, 로드밸런싱, 비동기 처리를 적절히 배치해봐. 병목 지점을 먼저 파악하는 게 핵심이야.",
        },
        "cost": {
            "concept": "비용 최적화",
            "guide": "오토스케일링, 예약 인스턴스, 서버리스 활용 등으로 비용을 줄이는 방법을 고려해봐.",
        },
        "operationalExcellence": {
            "concept": "운영 우수성",
            "guide": "모니터링, 로깅, CI/CD 파이프라인을 설계에 포함시켜봐. 장애를 빨리 감지하고 대응하는 구조가 중요해.",
        },
        "sustainability": {
            "concept": "지속가능성",
            "guide": "에너지 효율적인 리소스 사용과 장기 유지보수가 쉬운 구조를 고민해봐.",
        },
    },
}

UNIT_OVERALL_TIPS = {
    "unit01": "의사코드는 '생각의 설계도'야. 코드를 쓰기 전에 논리를 정리하는 습관이 핵심이야.",
    "unit02": "디버깅은 양이 중요해. 다양한 버그 패턴을 많이 접해봐야 실력이 늘어.",
    "unit03": "시스템 설계는 정답이 없어. 각 설계의 트레이드오프를 설명하는 능력이 실력이야.",
}


def tool_get_unit_curriculum(unit_id):
    curriculum = UNIT_CURRICULUM.get(unit_id)
    if not curriculum:
        return {"error": f"알 수 없는 유닛: {unit_id}"}
    return curriculum


def tool_get_study_guide(profile, unit_id):
    weak_data = tool_get_weak_points(profile, unit_id)

    guide_map = STUDY_GUIDE_MAP.get(unit_id, {})
    weak_areas = weak_data.get("weak_areas", [])

    guides = []
    for area in weak_areas:
        metric = area["metric"]
        mapping = guide_map.get(metric)
        if mapping:
            guides.append(
                {
                    "metric": metric,
                    "avg_score": area["avg_score"],
                    "concept": mapping["concept"],
                    "guide": mapping["guide"],
                }
            )
        else:
            guides.append(
                {
                    "metric": metric,
                    "avg_score": area["avg_score"],
                    "concept": metric,
                    "guide": f"{metric} 영역의 점수가 낮아. 관련 문제를 더 풀어보면서 감을 잡아보자.",
                }
            )

    guides.sort(key=lambda g: g["avg_score"])

    return {
        "unit_id": unit_id,
        "weak_metrics": [g["metric"] for g in guides],
        "priority_order": [g["metric"] for g in guides],
        "guides": guides,
        "overall_tip": UNIT_OVERALL_TIPS.get(unit_id, "꾸준히 연습하면 반드시 늘어!"),
    }


def tool_recommend_next_problem(profile, unit_id=None):
    details_qs = PracticeDetail.objects.filter(is_active=True, detail_type="PROBLEM")
    if unit_id:
        details_qs = details_qs.filter(practice_id=unit_id)

    mastered_ids = set(
        UserSolvedProblem.objects.filter(user=profile, is_best_score=True, score__gte=70).values_list(
            "practice_detail_id", flat=True
        )
    )

    recommendations = []
    for detail in details_qs.select_related("practice").order_by("practice__unit_number", "display_order"):
        if detail.id in mastered_ids:
            continue

        best = UserSolvedProblem.objects.filter(user=profile, practice_detail=detail, is_best_score=True).first()

        recommendations.append(
            {
                "problem_id": detail.id,
                "problem_title": detail.detail_title,
                "unit_id": detail.practice_id,
                "unit_title": detail.practice.title,
                "current_best_score": best.score if best else None,
                "status": "재도전 필요" if best else "미풀이",
            }
        )

        if len(recommendations) >= 5:
            break

    return recommendations if recommendations else [{"message": "모든 문제를 70점 이상으로 완료했습니다!"}]


TOOL_DISPATCH = {
    "get_user_scores": lambda profile, args: tool_get_user_scores(profile),
    "get_weak_points": lambda profile, args: tool_get_weak_points(profile, args.get("unit_id")),
    "get_recent_activity": lambda profile, args: tool_get_recent_activity(profile, args.get("limit", 10)),
    "recommend_next_problem": lambda profile, args: tool_recommend_next_problem(profile, args.get("unit_id")),
    "get_unit_curriculum": lambda profile, args: tool_get_unit_curriculum(args.get("unit_id")),
    "get_study_guide": lambda profile, args: tool_get_study_guide(profile, args.get("unit_id")),
}

TOOL_LABELS = {
    "get_user_scores": "성적 데이터 조회",
    "get_weak_points": "약점 분석",
    "get_recent_activity": "최근 활동 조회",
    "recommend_next_problem": "문제 추천",
    "get_unit_curriculum": "유닛 커리큘럼 조회",
    "get_study_guide": "맞춤 학습 가이드 생성",
}
