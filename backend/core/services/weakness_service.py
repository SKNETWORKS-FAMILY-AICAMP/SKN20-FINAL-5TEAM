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


def parse_submitted_data(submitted_data: dict, unit_id: str, score: int = 0) -> Dict[str, Any]:
    """
    submitted_data + score 기반 메트릭 추출

    현재 submitted_data에 ai_evaluation이 없으므로, 점수를 기반으로 메트릭 생성
    점수를 0~100 범위로 정규화하여 메트릭으로 사용

    Args:
        submitted_data: UserSolvedProblem.submitted_data JSONField
        unit_id: 유닛 ID (unit01, unit02, unit03)
        score: 풀이 점수 (기반이 될 점수)

    Returns:
        표준화된 메트릭 dict
    """
    if not submitted_data or not isinstance(submitted_data, dict):
        return {}

    # 점수를 0~100 범위로 정규화 (최대 점수를 100으로 가정)
    # 실제 점수는 보통 100점을 만점으로 함
    normalized_score = min(score, 100) if score > 0 else 0

    if unit_id == 'unit01':
        # Unit 1 (Pseudo Practice): logic_flow, edge_case, readability
        # 점수를 3개 항목으로 분산
        return {
            'unit': 'unit01',
            'logic_flow': normalized_score,
            'edge_case': normalized_score,
            'readability': normalized_score,
        }

    elif unit_id == 'unit02':
        # Unit 2 (Debug Practice): bug_detection, root_cause, fix_quality
        return {
            'unit': 'unit02',
            'bug_detection': normalized_score,
            'root_cause': normalized_score,
            'fix_quality': normalized_score,
        }

    elif unit_id == 'unit03':
        # Unit 3 (System Practice): 6개 아키텍처 기둥
        return {
            'unit': 'unit03',
            'scalability': normalized_score,
            'reliability': normalized_score,
            'security': normalized_score,
            'performance': normalized_score,
            'maintainability': normalized_score,
            'cost_efficiency': normalized_score,
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

    # [DEBUG] 조회된 풀이 기록 수
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[약점분석] 사용자 {user_id} - 조회된 풀이 기록: {len(solved_list)}개")

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
        # score를 메트릭 파싱에 전달
        metrics = parse_submitted_data(sp.submitted_data, unit_id, sp.score)
        logger.info(f"[약점분석] {unit_id} - 점수: {sp.score}, 파싱된 메트릭: {metrics}")

        if metrics and any(v > 0 for k, v in metrics.items() if k != 'unit'):
            unit_records[unit_id].append(metrics)

    logger.info(f"[약점분석] 유닛별 기록 - Unit1: {len(unit_records['unit01'])}, Unit2: {len(unit_records['unit02'])}, Unit3: {len(unit_records['unit03'])}")

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
        "analyzed_submission_count": len(unit_records['unit01']) + len(unit_records['unit02']) + len(unit_records['unit03'])
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
