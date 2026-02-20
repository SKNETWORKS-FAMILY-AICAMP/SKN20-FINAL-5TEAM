# agent/orchestrator.py
"""
Agent Orchestrator - 메인 루프
원본 v3.1 섹션 12 기반 (간소화)
"""
from agent.state import State, Action, ActionType, compute_time_pressure
from agent.models import JobPosting, UserProfile
from agent.planner import Planner
from scoring.engine import ScoringEngine

class AgentOrchestrator:
    def __init__(self, planner: Planner, scoring: ScoringEngine, target_readiness: float = 0.7):
        self.planner = planner
        self.scoring = scoring
        self.target = target_readiness
        self.max_loops = 10

    def run(self, user: UserProfile, job: JobPosting) -> dict:
        """에이전트 실행"""
        
        # 핵심 과제 분석
        print("\n[1단계] 핵심 과제 분석...")
        self.planner.analyze_core_challenge(job)
        print(f"핵심 과제: {self.planner.core_challenge}\n")

        # 초기 상태
        state = self._init_state(user, job)
        self._print_state(state)

        # 메인 루프
        while state.loop_count < self.max_loops:
            # 종료 조건
            if state.readiness_score >= self.target:
                print(f"\n✅ 목표 달성! readiness={state.readiness_score:.3f}")
                break

            if state.time_pressure == "긴급" and state.readiness_score >= 0.5:
                print(f"\n✅ 마감 임박. 현재 상태로 지원 권장.")
                break

            # 행동 선택
            action = self.planner.select_action(state, job, user)
            
            print(f"\n--- Loop {state.loop_count + 1} ---")
            print(f"[행동] {action.type.value}")
            print(f"[이유] {action.reasoning}")

            # 간단한 행동 처리
            if action.type == ActionType.APPLY_NOW:
                print("[결과] 지원 결정!")
                break
            elif action.type == ActionType.ASK_USER:
                question = action.params.get("question", "추가 정보가 필요합니다.")
                print(f"[질문] {question}")
                answer = input("> 답변: ").strip()
                print(f"[결과] 답변 수신: {answer}")
            else:
                print(f"[결과] {action.type.value} 수행")

            # 상태 업데이트
            state.loop_count += 1
            state.action_history.append({
                "action": action.type.value,
                "reasoning": action.reasoning
            })

        # 최종 보고서
        print("\n" + "="*60)
        print("최종 결과")
        print("="*60)
        print(f"최종 readiness: {state.readiness_score:.3f}")
        print(f"루프 횟수: {state.loop_count}")
        print(f"실행 행동: {[a['action'] for a in state.action_history]}")

        return {
            "final_readiness": state.readiness_score,
            "loop_count": state.loop_count,
            "actions": state.action_history
        }

    def _init_state(self, user: UserProfile, job: JobPosting) -> State:
        """초기 상태 생성"""
        report = self.scoring.generate_match_report(user, job)

        return State(
            skill_gap_score=report["skill_gap_score"],
            readiness_score=report["readiness_score"],
            readiness_band=self._interpret_readiness(report["readiness_score"]),
            deadline=job.deadline,
            deadline_days=job.deadline_days,
            time_pressure=compute_time_pressure(job.deadline_days),
            missing_skills=[m["required_skill"] for m in report["missing"]],
            matched_skills=[m["required_skill"] for m in report["matched"]],
            skill_priorities=[],
            current_skills=list(user.skills),
            current_levels=dict(user.skill_levels),
            loop_count=0,
            action_history=[],
            needs_replan=False,
            replan_reason=None
        )

    def _interpret_readiness(self, score: float) -> str:
        """readiness 해석"""
        if score >= 0.8: return "준비 완료"
        if score >= 0.6: return "지원 고려"
        if score >= 0.4: return "기초 준비"
        return "준비 필요"

    def _print_state(self, state: State):
        """상태 출력"""
        print("\n" + "="*60)
        print("[초기 분석]")
        print(f"  readiness: {state.readiness_score:.3f} ({state.readiness_band})")
        print(f"  skill_gap: {state.skill_gap_score:.3f}")
        print(f"  마감: {state.deadline_days}일 ({state.time_pressure})")
        print(f"  매칭: {state.matched_skills}")
        print(f"  부족: {state.missing_skills}")
        print("="*60)
