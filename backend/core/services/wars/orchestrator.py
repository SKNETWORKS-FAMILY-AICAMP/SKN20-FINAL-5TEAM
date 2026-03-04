"""
orchestrator.py — WarsOrchestrator (LangGraph 버전)

[흐름]
  on_canvas_update → OrchestratorAgent(LangGraph, 비동기 실행) →
    observe_game_state → decide_action(LLM) → dispatch → done

  EvalAgent 호출은 on_both_submitted 에서 직접 실행 — Orchestrator 외부.

[수정 이력]
  2026-03-02  on_canvas_update → asyncio.to_thread 래핑으로 이벤트 루프 블로킹 해결
              StateMachine에서 can_trigger_* 제거 → trigger_policy 모듈로 이전 반영
"""

import asyncio
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
        room_state.past_event_ids     = []

        return self.state_machine.transition(room_state, GameState.PLAYING)

    # ──────────────────────────────────────────────────────────
    # 캔버스 업데이트 → OrchestratorAgent 실행
    # ──────────────────────────────────────────────────────────

    # AI 호출 과부하 방지용 쿨다운 (초)
    AGENT_CALL_COOLDOWN = 2.0

    # [수정일: 2026-03-02] LLM 직렬 호출 경고 임계값 (초)
    # dispatch 노드는 Orchestrator LLM + Coach LLM + Chaos LLM을 직렬로 호출할 수 있어
    # 최악의 경우 수실 30초 대기가 발생할 수 있다. 이 시간을 초과하면 주의를 로깅한다.
    DISPATCH_SLOW_WARN_SEC = 10.0

    async def on_canvas_update(
        self,
        room_state: DrawRoomState,
        sid: str,
        nodes: list,
        arrows: list,
        is_poll: bool = False,
    ) -> Dict[str, Any]:
        """
        플레이어 캔버스 변경 시 호출 (is_poll=False)
        또는 백그라운드에서 무조작/장애 여부 체크를 위해 주기적으로 호출 (is_poll=True).

        is_poll=True일 경우 설계 스냅샷 갱신을 건너뛰어 Inactivity 타이머 유효성을 유지한다.
        """
        # 1. 설계 스냅샷 갱신 (폴링 시에는 스킵)
        if not is_poll:
            room_state.update_design(sid, nodes or [], arrows or [])

        # 2. 쿨다운 체크 — 너무 자주 AI 호출하지 않도록 방지 (플레이어별 분리)
        now = time.time()
        if not hasattr(room_state, '_last_agent_call_per_sid'):
            room_state._last_agent_call_per_sid = {}
        
        last_called = room_state._last_agent_call_per_sid.get(sid, 0)
        cooldown = self.AGENT_CALL_COOLDOWN if not is_poll else 1.0 # 폴링 시에는 조금 더 유연하게(1s)
        
        if now - last_called < cooldown:
            return {"coach_hint": None, "chaos_event": None}
        room_state._last_agent_call_per_sid[sid] = now

        # 3. OrchestratorAgent에 넘길 player_snapshots 빌드
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

        # 4. LangGraph graph.invoke() — 동기 함수 → asyncio.to_thread 로 실행
        #    이벤트 루프 블로킹 없이 백그라운드 스레드에서 처리됨
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

        graph = get_orchestrator_graph()
        # [수정일: 2026-03-02] LLM 직렬 호출 시간 측정
        # dispatch가 Orchestrator + Coach + Chaos LLM을 직렬로 호출하면 최대 30초 소요 가능
        _invoke_start = time.time()
        final_state = await asyncio.to_thread(graph.invoke, initial_state)
        _invoke_elapsed = time.time() - _invoke_start
        if _invoke_elapsed > self.DISPATCH_SLOW_WARN_SEC:
            logger.warning(
                f"[Orchestrator] ⚠️ LLM 직렬 호출 지연 감지: {_invoke_elapsed:.1f}s "
                f"(room={room_state.room_id}) "
                f"— actions={final_state.get('actions_taken', [])}"
            )

        result = {"coach_hint": None, "chaos_event": None}

        # 5. CoachAgent 결과 처리
        coach_hint = final_state.get("coach_hint")
        if coach_hint and coach_hint.get("message"):
            # [수정일: 2026-03-03] pop() 전에 target_sid 먼저 보존
            # 기존: pop() 후 result에 담기면 socket_server에서 _target_sid 꼽아도 None 반환 → 나한테 전송
            target_sid = coach_hint.get("_target_sid") or sid
            coach_hint = {k: v for k, v in coach_hint.items() if k != "_target_sid"}
            coach_hint["_target_sid"] = target_sid  # socket_server가 읽을 수 있도록 유지
            room_state.coach_triggered_at = time.time()

            if target_sid not in room_state.hint_history:
                room_state.hint_history[target_sid] = []
            room_state.hint_history[target_sid].append({
                "message": coach_hint["message"],
                "type": coach_hint.get("type"),
                "level": coach_hint.get("level", 1),
                "_time": time.time(),
            })
            # 힌트 이력 최대 5개 유지
            if len(room_state.hint_history[target_sid]) > 5:
                room_state.hint_history[target_sid].pop(0)

            result["coach_hint"] = coach_hint
            logger.info(
                f"[Orchestrator] CoachAgent 개입: room={room_state.room_id}, "
                f"sid={target_sid[:8]}, level={coach_hint.get('level')}"
            )

        # 6. ChaosAgent 결과 처리
        chaos_event = final_state.get("chaos_event")
        if chaos_event and chaos_event.get("event_id"):
            room_state.chaos_triggered_at = time.time()
            room_state.chaos_event_id = chaos_event.get("event_id")

            if not hasattr(room_state, "past_event_ids"):
                room_state.past_event_ids = []
            room_state.past_event_ids.append(chaos_event["event_id"])

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
