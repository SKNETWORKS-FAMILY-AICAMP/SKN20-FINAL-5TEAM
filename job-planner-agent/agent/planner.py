# agent/planner.py
"""
Planner - 전략 추천
원본 v3.1 섹션 9 기반
"""
from agent.state import State, Action, ActionType
from agent.models import JobPosting, UserProfile
from llm.gateway import LLMGateway

class Planner:
    def __init__(self, llm: LLMGateway):
        self.llm = llm
        self.core_challenge: str | None = None

    def analyze_core_challenge(self, job: JobPosting) -> str:
        """1단계: 직무 핵심 과제 분석 (최초 1회만)"""
        prompt = f"""
        이 채용공고의 핵심 과제를 1~2문장으로 요약하라.
        "어떤 스킬이 필요한가"가 아니라 "이 직무가 해결해야 하는 비즈니스 문제"를 파악하라.
        
        회사: {job.company_name} | 포지션: {job.position}
        직무 설명: {job.job_description}
        필수 스킬: {job.required_skills}
        """
        self.core_challenge = self.llm.call(prompt, model="gpt-4o-mini")
        return self.core_challenge

    def select_action(self, state: State, job: JobPosting, user: UserProfile) -> Action:
        # 재계획 시 규칙 필터 건너뜀
        if state.needs_replan:
            state.needs_replan = False
            state.replan_reason = None
            return self._llm_select(state, job, user)

        rule = self._apply_rules(state)
        return rule if rule else self._llm_select(state, job, user)

    def _apply_rules(self, state: State) -> Action | None:
        """명백한 상황만 규칙으로 처리"""
        if state.time_pressure == "긴급" and state.readiness_score < 0.3:
            return Action(
                ActionType.PIVOT_ROLE, 
                {"reason": "마감임박+준비도낮음"},
                "마감 5일 이내, readiness 0.3 미만. 대안 검토.", 
                [{"action":"learn_skill","reason":"시간부족"}],
                requires_confirmation=True
            )
        if state.time_pressure == "긴급" and state.readiness_score >= 0.5:
            return Action(
                ActionType.APPLY_NOW, 
                {"reason": "마감임박+준비도충분"},
                f"마감 {state.deadline_days}일, readiness {state.readiness_score}. 지원 권장.",
                [{"action":"learn_skill","reason":"시간부족"}]
            )
        return None

    def _llm_select(self, state: State, job: JobPosting, user: UserProfile) -> Action:
        """2단계: 행동 선택"""
        prompt = f"""
        채용공고 공략 전략 에이전트. 다음 행동 하나를 선택하라.

        [핵심 과제] {self.core_challenge or "미분석"}

        [현재 상태]
        readiness: {state.readiness_score} ({state.readiness_band})
        skill_gap: {state.skill_gap_score}
        마감: {state.deadline_days}일 ({state.time_pressure})
        부족: {state.missing_skills} | 매칭: {state.matched_skills}

        [행동]
        1. "learn_skill" — 스킬 학습 추천
        2. "ask_user" — 사용자에게 질문
        3. "apply_now" — 지원
        4. "wait_and_prepare" — 면접 준비
        5. "pivot_role" — 대안 검토

        JSON: {{"reasoning":"2문장","action":"타입","params":{{}},"alternatives_rejected":[]}}
        """
        resp = self.llm.call_json(prompt, model="gpt-4o-mini")
        return Action(
            ActionType(resp["action"]), 
            resp.get("params", {}),
            resp.get("reasoning", ""), 
            resp.get("alternatives_rejected", []),
            requires_confirmation=(resp["action"]=="pivot_role")
        )
