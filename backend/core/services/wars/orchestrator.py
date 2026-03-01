"""
orchestrator.py — WarsOrchestrator (LangGraph 버전)

기존 단순 조건 분기 Orchestrator에서 LangGraph Agent로 전면 교체.

[기존]
  on_canvas_update → can_trigger_coach? → CoachAgent.generate()
                   → can_trigger_chaos? → ChaosAgent.generate()

[신규]
  on_canvas_update → OrchestratorAgent(LangGraph) →
    observe_game_state → decide_action(LLM) → dispatch → done

  LLM이 전체 맥락을 보고 "지금 무엇을 해야 하는가"를 직접 판단.
  StateMachine은 하드 가드로만 유지 (무효 전환 차단).

[EvalAgent 호출은 on_both_submitted에서 직접 실행 — Orchestrator 외부]
"""

import logging
import time
from typing import Dict, Any, Optional

from core.services.wars.state_machine import StateMachine, DrawRoomState, GameState
from core.services.wars.eval_agent import EvalAgent
from core.services.wars.agents.orchestrator.graph import get_orchestrator_graph

logger = logging.getLogger(__name__)


class WarsOrchestrator:
    """
    ArchDrawQuiz Wars 미니게임 Orchestrator.
    canvas_update 이벤트마다 OrchestratorAgent(LangGraph)를 실행하여
    CoachAgent / ChaosAgent 개입 여부와 타이밍을 AI가 결정한다.
    """

    def __init__(self):
        self.state_machine = StateMachine()
        self.eval_agent    = EvalAgent()

    # ──────────────────────────────────────────────────────────
    # 라운드 시작
    # ──────────────────────────────────────────────────────────

    def on_round_start(
        self,
        room_state: DrawRoomState,
        mission_title: str,
        mission_required: list,
    ) -> bool:
        """WAITING → PLAYING 전환 + 라운드 상태 초기화"""
        room_state.mission_title      = mission_title
        room_state.mission_required   = mission_required
        room_state.coach_triggered_at = 0.0
        room_state.chaos_triggered_at = 0.0
        room_state.chaos_event_id     = None
        room_state.player_designs     = {}
        room_state.hint_history       = {}
        # 이번 라운드 발동된 이벤트 ID 초기화
        if not hasattr(room_state, "past_event_ids"):
            room_state.past_event_ids = []
        else:
            room_state.past_event_ids = []

        return self.state_machine.transition(room_state, GameState.PLAYING)

    # ──────────────────────────────────────────────────────────
    # 캔버스 업데이트 → OrchestratorAgent 실행
    # ──────────────────────────────────────────────────────────

    # [수정일: 2026-03-01] 캔버스 업데이트마다 AI 호출 방지용 쿨다운 (초)
    AGENT_CALL_COOLDOWN = 3.0

    def on_canvas_update(
        self,
        room_state: DrawRoomState,
        sid: str,
        nodes: list,
        arrows: list,
    ) -> Dict[str, Any]:
        """
        플레이어 캔버스 변경 시 호출.
        OrchestratorAgent(LangGraph)가 전체 맥락을 보고 행동을 결정한다.

        Returns:
            {
                "coach_hint": {...} | None,
                "chaos_event": {...} | None,
            }
        """
        # 1. 설계 스냅샷 갱신
        room_state.update_design(sid, nodes, arrows)

        # [수정일: 2026-03-01] 쿨다운 체크 — 너무 자주 AI 호출하지 않도록 방지
        now = time.time()
        last_called = getattr(room_state, '_last_agent_call', 0)
        if now - last_called < self.AGENT_CALL_COOLDOWN:
            return {"coach_hint": None, "chaos_event": None}
        room_state._last_agent_call = now

        # 2. OrchestratorAgent에 넘길 player_snapshots 빌드
        player_snapshots = {}
        for player_sid, design in room_state.player_designs.items():
            player_snapshots[player_sid] = {
                "node_count": design.get("node_count", 0),
                "arrow_count": len(design.get("arrows", [])),
                "deployed_nodes": [
                    n.get("compId", "") for n in design.get("nodes", [])
                    if isinstance(n, dict) and n.get("compId")
                ],
                "seconds_inactive": room_state.seconds_since_last_update(player_sid),
            }

        # 3. OrchestratorAgent 실행
        graph = get_orchestrator_graph()
        initial_state = {
            "room_id": room_state.room_id,
            "game_state_name": room_state.state.value,
            "mission_title": room_state.mission_title,
            "mission_required": room_state.mission_required,
            "elapsed_seconds": room_state.elapsed(),
            "player_snapshots": player_snapshots,
            "hint_history": room_state.hint_history,
            "chaos_triggered": room_state.chaos_triggered_at > 0,
            "past_event_ids": getattr(room_state, "past_event_ids", []),
            "trigger_sid": sid,
            "situation_summary": None,
            "action_plan": None,
            "dispatched": False,
            "coach_hint": None,
            "chaos_event": None,
            "actions_taken": [],
        }

        final_state = graph.invoke(initial_state)

        result = {"coach_hint": None, "chaos_event": None}

        # 4. CoachAgent 결과 처리
        coach_hint = final_state.get("coach_hint")
        if coach_hint and coach_hint.get("message"):
            target_sid = coach_hint.pop("_target_sid", sid)
            room_state.coach_triggered_at = time.time()

            # 힌트 이력 저장
            if target_sid not in room_state.hint_history:
                room_state.hint_history[target_sid] = []
            room_state.hint_history[target_sid].append({
                "message": coach_hint["message"],
                "type": coach_hint.get("type"),
                "level": coach_hint.get("level", 1),
                "_time": time.time(),
            })
            if len(room_state.hint_history[target_sid]) > 5:
                room_state.hint_history[target_sid].pop(0)

            result["coach_hint"] = coach_hint
            logger.info(
                f"[Orchestrator] CoachAgent 개입: room={room_state.room_id}, "
                f"sid={target_sid[:8]}, level={coach_hint.get('level')}"
            )

        # 5. ChaosAgent 결과 처리
        chaos_event = final_state.get("chaos_event")
        if chaos_event and chaos_event.get("event_id"):
            room_state.chaos_triggered_at = time.time()
            room_state.chaos_event_id = chaos_event.get("event_id")

            # 이벤트 ID 이력 저장
            if not hasattr(room_state, "past_event_ids"):
                room_state.past_event_ids = []
            room_state.past_event_ids.append(chaos_event["event_id"])

            # StateMachine: PLAYING → IN_BASKET
            self.state_machine.transition(room_state, GameState.IN_BASKET)
            result["chaos_event"] = chaos_event
            logger.info(
                f"[Orchestrator] ChaosAgent 개입: room={room_state.room_id}, "
                f"event={chaos_event.get('event_id')}, severity={chaos_event.get('severity')}"
            )

        return result

    # ──────────────────────────────────────────────────────────
    # 장애 이벤트 만료 — IN_BASKET → PLAYING 복귀
    # ──────────────────────────────────────────────────────────

    def on_incident_expired(self, room_state: DrawRoomState) -> bool:
        """IN_BASKET → PLAYING 복귀"""
        room_state.chaos_event_id = None
        return self.state_machine.transition(room_state, GameState.PLAYING)

    # ──────────────────────────────────────────────────────────
    # 양측 제출 완료 — EvalAgent 평가
    # ──────────────────────────────────────────────────────────

    async def on_both_submitted(
        self,
        room_state: DrawRoomState,
        mission_title: str,
        rubric: Dict[str, Any],
        p1_data: Dict[str, Any],
        p2_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """PLAYING/IN_BASKET → JUDGING → FINISHED + EvalAgent 평가"""
        self.state_machine.transition(room_state, GameState.JUDGING)

        ai_reviews = await self.eval_agent.evaluate(
            mission_title=mission_title,
            p1_data=p1_data,
            p2_data=p2_data,
            rubric=rubric,
        )

        self.state_machine.transition(room_state, GameState.FINISHED)
        return ai_reviews

    # ──────────────────────────────────────────────────────────
    # 다음 라운드
    # ──────────────────────────────────────────────────────────

    def on_next_round(self, room_state: DrawRoomState) -> bool:
        """FINISHED → WAITING"""
        return self.state_machine.transition(room_state, GameState.WAITING)
