"""
weakness_analyzer.py — 사용자 취약점 분석기
gym_user_solved_problem 테이블 기반 순수 Python 분석
"""
from collections import Counter
from core.models import UserSolvedProblem, UserProfile


def analyze_user_weakness(user: UserProfile) -> dict:
    """
    사용자의 문제 풀이 이력을 분석하여 취약점을 추출한다.

    조회 기준:
      - 낮은 점수 (score < 60)
      - 다수 시도 (attempt_number >= 3)
      - is_perfect == False인 문제들의 공통 주제

    반환:
    {
        "weak_topics": ["예외처리", "비동기"],
        "weak_categories": ["기술", "문제해결"],
        "strength_topics": ["기본 문법", "함수 설계"]
    }
    """
    try:
        solved_problems = UserSolvedProblem.objects.filter(
            user=user
        ).select_related('practice_detail').order_by('-solved_date')[:200]

        weak_topic_counter = Counter()
        strong_topic_counter = Counter()
        weak_categories = set()

        for sp in solved_problems:
            content_data = {}
            if sp.practice_detail:
                content_data = sp.practice_detail.content_data or {}

            topic = _extract_topic(content_data, sp.practice_detail)
            category = _extract_category(content_data, sp.practice_detail)

            is_weak = (
                sp.score < 60 or
                sp.attempt_number >= 3 or
                not sp.is_perfect
            )

            if topic:
                if is_weak:
                    weak_topic_counter[topic] += 1
                    if category:
                        weak_categories.add(category)
                elif sp.is_perfect and sp.score >= 80:
                    strong_topic_counter[topic] += 1

        # 상위 취약 토픽 (3회 이상 실패 또는 상위 5개)
        weak_topics = [
            topic for topic, count in weak_topic_counter.most_common(10)
            if count >= 1
        ][:5]

        # 강점 토픽 (완벽 풀이 2회 이상)
        strength_topics = [
            topic for topic, count in strong_topic_counter.most_common(5)
            if count >= 2
        ][:3]

        return {
            "weak_topics": weak_topics,
            "weak_categories": list(weak_categories)[:3],
            "strength_topics": strength_topics
        }

    except Exception as e:
        print(f"[WeaknessAnalyzer] 분석 오류: {e}")
        return {
            "weak_topics": [],
            "weak_categories": [],
            "strength_topics": []
        }


def _extract_topic(content_data: dict, practice_detail) -> str:
    """content_data에서 토픽 추출"""
    if not content_data:
        return ""

    # pseudocode 문제: title이나 topic 필드 사용
    for key in ('topic', 'category', 'title', 'quest_title', 'subject'):
        val = content_data.get(key, '')
        if val and isinstance(val, str) and len(val) < 50:
            return val.strip()

    # practice_detail의 detail_title 사용
    if practice_detail and practice_detail.detail_title:
        title = practice_detail.detail_title
        # 너무 긴 제목은 앞부분만
        return title[:30].strip() if len(title) > 30 else title.strip()

    return ""


def _extract_category(content_data: dict, practice_detail) -> str:
    """content_data에서 카테고리 추출"""
    if not content_data:
        return ""

    for key in ('category', 'type', 'unit_type', 'practice_type'):
        val = content_data.get(key, '')
        if val and isinstance(val, str):
            return val.strip()

    if practice_detail:
        return practice_detail.detail_type or ""

    return ""
