"""
약점 분석 및 사용자 약점 프로필 관리 서비스
"""
import json
from typing import List, Dict, Any
from core.models import UserSolvedProblem, UserProfile
from django.db.models import Max, Q


def get_user_solved_problems(user_id: int, limit: int = 5) -> List[UserSolvedProblem]:
    """
    사용자의 최근 풀이 기록 조회

    Args:
        user_id: 사용자 ID
        limit: 조회 개수

    Returns:
        UserSolvedProblem 쿼리셋 (최신 순)
    """
    try:
        user = UserProfile.objects.get(id=user_id)
        return list(
            UserSolvedProblem.objects.filter(
                user=user,
                submitted_data__isnull=False
            ).select_related('practice_detail__practice').order_by('-solved_date')[:limit]
        )
    except UserProfile.DoesNotExist:
        return []


def parse_submitted_data(submitted_data: dict, unit_id: str) -> Dict[str, Any]:
    """
    submitted_data JSONField 파싱 → 메트릭 추출

    Unit별로 다른 구조를 처리:
    - Unit 1 (unit01): metrics (logic_flow, edge_case, readability)
    - Unit 2 (unit02): metrics (bug_detection, root_cause, fix_quality)
    - Unit 3 (unit03): pillarScores (scalability, reliability, security, ...)

    Args:
        submitted_data: UserSolvedProblem.submitted_data JSONField
        unit_id: 유닛 ID (unit01, unit02, unit03)

    Returns:
        표준화된 메트릭 dict
    """
    if not submitted_data or not isinstance(submitted_data, dict):
        return {}

    ai_eval = submitted_data.get('ai_evaluation', {})

    if unit_id == 'unit01':
        # Unit 1: logic_flow, edge_case, readability
        metrics = ai_eval.get('metrics', {})
        return {
            'unit': 'unit01',
            'logic_flow': metrics.get('logic_flow', 0),
            'edge_case': metrics.get('edge_case', 0),
            'readability': metrics.get('readability', 0),
        }

    elif unit_id == 'unit02':
        # Unit 2: bug_detection, root_cause, fix_quality
        metrics = ai_eval.get('metrics', {})
        return {
            'unit': 'unit02',
            'bug_detection': metrics.get('bug_detection', 0),
            'root_cause': metrics.get('root_cause', 0),
            'fix_quality': metrics.get('fix_quality', 0),
        }

    elif unit_id == 'unit03':
        # Unit 3: pillarScores (6개)
        pillar = ai_eval.get('pillarScores', {})
        return {
            'unit': 'unit03',
            'scalability': pillar.get('scalability', 0),
            'reliability': pillar.get('reliability', 0),
            'security': pillar.get('security', 0),
            'performance': pillar.get('performance', 0),
            'maintainability': pillar.get('maintainability', 0),
            'cost_efficiency': pillar.get('cost_efficiency', 0),
        }

    return {}


def aggregate_metrics(metrics_list: List[Dict]) -> Dict[str, float]:
    """
    여러 제출의 메트릭을 평균으로 집계
    최근 3회에 가중치 2배 적용

    Args:
        metrics_list: [{"logic_flow": 80, ...}, ...]

    Returns:
        {"logic_flow": 72.5, ...}
    """
    if not metrics_list:
        return {}

    all_keys = set()
    for m in metrics_list:
        if isinstance(m, dict):
            all_keys.update(k for k in m.keys() if k != 'unit')

    result = {}
    n = len(metrics_list)

    for key in all_keys:
        values = [m.get(key, 0) for m in metrics_list if isinstance(m, dict)]

        if not values:
            continue

        # 최근 3회에 가중치 2배
        recent = values[-3:] if n >= 3 else values
        older = values[:-3] if n > 3 else []

        if recent:
            weighted = (sum(recent) * 2 + sum(older)) / (len(recent) * 2 + len(older))
        else:
            weighted = sum(recent) / len(recent)

        result[key] = round(weighted, 1)

    return result


def compute_top_weaknesses(aggregated_metrics: Dict[str, float], threshold: int = 65) -> List[str]:
    """
    전체 메트릭 중 threshold 미만인 항목을 낮은 순으로 반환

    Args:
        aggregated_metrics: {"logic_flow": 72, "edge_case": 45, ...}
        threshold: 약점 판정 기준 (기본: 65점)

    Returns:
        ["edge_case", "root_cause", "security"]
    """
    weak = {k: v for k, v in aggregated_metrics.items() if v < threshold and v > 0}
    sorted_weak = sorted(weak.items(), key=lambda x: x[1])
    return [k for k, _ in sorted_weak[:5]]  # 상위 5개


def analyze_user_learning(user_id: int) -> Dict[str, Any]:
    """
    사용자 학습 종합 분석

    1. submitted_data 조회
    2. 메트릭 파싱 및 집계
    3. 약점 도출
    4. 약점 진단 정보 추가

    Args:
        user_id: 사용자 ID

    Returns:
        {
            "user_id": 123,
            "summary": "종합 분석 요약",
            "unit1_metrics": {...},
            "unit2_metrics": {...},
            "unit3_metrics": {...},
            "top_weaknesses": ["edge_case", "root_cause"],
            "analyzed_submission_count": 5
        }
    """
    solved_list = get_user_solved_problems(user_id, limit=10)

    if not solved_list:
        return {
            "user_id": user_id,
            "summary": "아직 풀이 기록이 없습니다",
            "unit1_metrics": {},
            "unit2_metrics": {},
            "unit3_metrics": {},
            "top_weaknesses": [],
            "analyzed_submission_count": 0
        }

    # 유닛별 메트릭 분리
    unit_records = {'unit01': [], 'unit02': [], 'unit03': []}

    for sp in solved_list:
        unit_id = sp.practice_detail.practice_id
        metrics = parse_submitted_data(sp.submitted_data, unit_id)

        if metrics and any(v > 0 for v in metrics.values() if k != 'unit' for k, v in metrics.items()):
            unit_records[unit_id].append(metrics)

    # 유닛별 평균 계산
    unit1_avg = aggregate_metrics(unit_records['unit01'])
    unit2_avg = aggregate_metrics(unit_records['unit02'])
    unit3_avg = aggregate_metrics(unit_records['unit03'])

    # 전체 약점 도출
    all_metrics = {**unit1_avg, **unit2_avg, **unit3_avg}
    top_weak = compute_top_weaknesses(all_metrics)

    return {
        "user_id": user_id,
        "summary": f"Unit 1: {len(unit_records['unit01'])}회, Unit 2: {len(unit_records['unit02'])}회, Unit 3: {len(unit_records['unit03'])}회 풀이 기록 분석",
        "unit1_metrics": unit1_avg,
        "unit2_metrics": unit2_avg,
        "unit3_metrics": unit3_avg,
        "top_weaknesses": top_weak,
        "analyzed_submission_count": sum(
            len(unit_records['unit01']) + len(unit_records['unit02']) + len(unit_records['unit03'])
        )
    }


def get_focus_weakness(top_weaknesses: List[str]) -> str:
    """
    상위 약점 중 가장 긴급한 것을 선택 (첫 번째)

    Args:
        top_weaknesses: ["edge_case", "root_cause", ...]

    Returns:
        "edge_case" 또는 ""
    """
    return top_weaknesses[0] if top_weaknesses else ""
