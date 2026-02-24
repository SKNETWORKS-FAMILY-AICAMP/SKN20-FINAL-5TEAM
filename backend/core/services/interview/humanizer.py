"""
humanizer.py — L5 Humanizer (컨텍스트 조립 유틸)
LLM 없음. L4 Interviewer에 전달할 컨텍스트를 조립하는 유틸 함수다.
"""


def build_context(session, plan_slot: dict = None) -> dict:
    """
    L4 Interviewer 프롬프트에 주입할 컨텍스트를 조립한다.
    LLM 호출 없음.

    Args:
        session: InterviewSession 인스턴스
        plan_slot: 현재 슬롯의 interview_plan 항목

    Returns:
        {
            "slot": "collaboration",
            "topic": "팀 협업 경험",
            "is_slot_transition": False,
            "attempt_count": 1,
            "is_first_question": False,
            "company_name": "삼성SDS",
            "position": "백엔드 개발자",
        }
    """
    if plan_slot is None:
        plan_slot = session.get_current_slot_plan()

    current_slot_state = session.slot_states.get(session.current_slot, {})
    attempt_count = current_slot_state.get("attempt_count", 1)

    # 채용공고 정보
    company_name = ""
    position = ""
    job_responsibilities = ""
    required_qualifications = ""
    preferred_qualifications = ""

    if session.job_posting:
        company_name = session.job_posting.company_name or ""
        position = session.job_posting.position or ""
        job_responsibilities = (session.job_posting.job_responsibilities or "")[:400]
        required_qualifications = (session.job_posting.required_qualifications or "")[:300]
        preferred_qualifications = (session.job_posting.preferred_qualifications or "")[:200]

    weakness_boost = session.interview_plan.get("weakness_boost", [])

    return {
        "slot": session.current_slot,
        "topic": plan_slot.get("topic", session.current_slot),
        "is_slot_transition": session.just_moved_slot,
        "attempt_count": attempt_count,
        "is_first_question": (session.current_turn == 0),
        "company_name": company_name,
        "position": position,
        "job_responsibilities": job_responsibilities,
        "required_qualifications": required_qualifications,
        "preferred_qualifications": preferred_qualifications,
        "weakness_boost": weakness_boost,
    }
