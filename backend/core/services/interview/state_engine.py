"""
state_engine.py — L2 Engine (상태 결정기)
시스템의 뇌. 모든 결정은 여기서 이루어진다.
LLM 없음. 순수 Python 규칙으로만 동작한다.
"""


class StateEngine:
    """
    증거 기반 슬롯 상태 관리 + 면접 흐름 결정 엔진.
    LLM이 개입하지 않는다. 모든 판단은 규칙으로만.
    """

    def update_slot(self, slot: str, evidence_map: dict, required: list) -> dict:
        """
        슬롯 상태를 갱신한다.
        CLEAR 기준: required evidence 전부 확인 (optional은 무시)

        Args:
            slot: 슬롯명
            evidence_map: {evidence_key: bool, ...}
            required: 핵심 evidence 목록

        Returns:
            {
                "status": "UNKNOWN" | "PARTIAL" | "CLEAR",
                "confirmed": [...],          # 전체 확인 evidence (optional 포함)
                "confirmed_required": [...], # 핵심 확인 evidence
                "missing_required": [...]    # 미확인 핵심 evidence
            }
        """
        confirmed_required = [k for k in required if evidence_map.get(k)]
        all_confirmed = [k for k, v in evidence_map.items() if v]
        missing_required = [k for k in required if not evidence_map.get(k)]
        count_required = len(confirmed_required)

        if count_required == 0:
            new_status = "UNKNOWN"
        elif count_required < len(required):
            new_status = "PARTIAL"
        else:
            new_status = "CLEAR"  # 핵심 evidence 전부 확인

        return {
            "status": new_status,
            "confirmed": all_confirmed,
            "confirmed_required": confirmed_required,
            "missing_required": missing_required,
        }

    def decide_action(self, session) -> str:
        """
        종료 / 슬롯 이동 / 계속 여부를 결정한다.

        Returns:
            "finish" | "move_slot" | "continue"
        """
        # 종료 조건 1: 최대 턴 초과
        if session.current_turn >= session.max_turns:
            return "finish"

        # 종료 조건 2: 모든 슬롯 CLEAR 또는 UNCERTAIN (완료 처리)
        slot_states = session.slot_states
        if slot_states:
            all_done = all(
                s.get("status") in ("CLEAR", "UNCERTAIN")
                for s in slot_states.values()
            )
            if all_done:
                return "finish"

        # 현재 슬롯 상태 확인
        current_state = slot_states.get(session.current_slot, {})
        attempt_count = current_state.get("attempt_count", 0)

        # 현재 슬롯이 CLEAR 또는 UNCERTAIN → 다음 슬롯으로 이동
        if current_state.get("status") in ("CLEAR", "UNCERTAIN"):
            return "move_slot"

        # 최대 시도 횟수 초과 → UNCERTAIN 처리 후 이동
        plan_slot = session.get_current_slot_plan()
        max_attempts = plan_slot.get("max_attempts", 3)
        if attempt_count >= max_attempts:
            return "move_slot"

        # 연속 2회 이상 새 evidence 없음 → 조기 이동
        consecutive_no_gain = current_state.get("consecutive_no_gain", 0)
        if consecutive_no_gain >= 2:
            return "move_slot"

        return "continue"

    def move_to_next_slot(self, session) -> str:
        """
        다음 방문할 슬롯을 결정하고 session을 업데이트한다.
        모든 슬롯을 최소 1회 방문 보장.

        Returns:
            다음 슬롯명 (없으면 "")
        """
        plan_slots = session.interview_plan.get("slots", [])
        slot_names = [s["slot"] for s in plan_slots]

        current_idx = -1
        for i, name in enumerate(slot_names):
            if name == session.current_slot:
                current_idx = i
                break

        # 아직 완료되지 않은 슬롯 우선 (CLEAR, UNCERTAIN은 완료로 간주)
        for i, name in enumerate(slot_names):
            if i > current_idx:
                state = session.slot_states.get(name, {})
                if state.get("status") not in ("CLEAR", "UNCERTAIN"):
                    return name

        # 모든 슬롯 방문 완료
        return ""

    def initialize_slot_states(self, interview_plan: dict) -> dict:
        """
        interview_plan 기반으로 slot_states 초기화

        Returns:
            초기화된 slot_states dict
        """
        from core.services.interview.coach import SLOT_REQUIRED

        slot_states = {}
        for slot_plan in interview_plan.get("slots", []):
            slot_name = slot_plan["slot"]

            # required evidence: plan에 있으면 우선, 없으면 SLOT_REQUIRED 기본값
            required = slot_plan.get("required_evidence") or SLOT_REQUIRED.get(slot_name, [])

            # evidence_map 초기화 (required + optional 모두 False)
            all_keys = list(required) + list(slot_plan.get("optional_evidence", []))
            evidence = {k: False for k in all_keys}

            slot_states[slot_name] = {
                "status": "UNKNOWN",
                "evidence": evidence,
                "confirmed_required": [],
                "missing_required": list(required),
                "attempt_count": 0,
                "required": list(required),
            }

        return slot_states

    def mark_uncertain(self, session, slot_name: str) -> None:
        """슬롯을 UNCERTAIN으로 마킹 (2회 이상 시도 실패)"""
        slot_states = session.slot_states
        if slot_name in slot_states:
            slot_states[slot_name]["status"] = "UNCERTAIN"
            session.slot_states = slot_states
