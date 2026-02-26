"""
orchestrator.py — WarsOrchestrator
StateMachine + ChaosAgent + CoachAgent + EvalAgent를 조율하는 오케스트레이터.

[역할]
socket_server.py가 직접 에이전트를 호출하지 않는다.
모든 에이전트 호출은 WarsOrchestrator를 통해서만 이루어진다.

[흐름]
소켓 이벤트 수신
    → socket_server가 orchestrator 메서드 호출
        → orchestrator가 StateMachine으로 상태 검사
            → 조건 충족 시 해당 에이전트 호출
                → 결과를 socket_server에 반환
                    → socket_server가 클라이언트에 emit
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional

from core.services.wars.state_machine import StateMachine, DrawRoomState, GameState
from core.services.wars.chaos_agent import ChaosAgent
from core.services.wars.coach_agent import CoachAgent
from core.services.wars.eval_agent import EvalAgent

logger = logging.getLogger(__name__)


class WarsOrchestrator:
    """
    ArchDrawQuiz Wars 미니게임의 에이전트 오케스트레이터.

    인스턴스는 방(room_id)별로 생성되지 않고,
    소켓 서버 전역에서 싱글톤으로 사용된다.
    상태는 DrawRoomState 객체(외부 dict)에 저장된다.
    """

    def __init__(self):
        self.state_machine = StateMachine()
        self.chaos_agent   = ChaosAgent()
        self.coach_agent   = CoachAgent()
        self.eval_agent    = EvalAgent()

    # ──────────────────────────────────────────
    # 라운드 시작
    # ──────────────────────────────────────────

    def on_round_start(
        self,
        room_state: DrawRoomState,
        mission_title: str,
        mission_required: list,
    ) -> bool:
        """
        라운드 시작 시 호출.
        WAITING → PLAYING 상태 전환.

        Returns:
            True if 전환 성공
        """
        room_state.mission_title    = mission_title
        room_state.mission_required = mission_required
        room_state.coach_triggered_at = 0.0
        room_state.chaos_triggered_at = 0.0
        room_state.chaos_event_id   = None
        room_state.player_designs   = {}

        return self.state_machine.transition(room_state, GameState.PLAYING)

    # ──────────────────────────────────────────
    # 캔버스 동기화 수신 시 — 에이전트 트리거 검사
    # ──────────────────────────────────────────

    def on_canvas_update(
        self,
        room_state: DrawRoomState,
        sid: str,
        nodes: list,
        arrows: list,
    ) -> Dict[str, Any]:
        """
        플레이어 캔버스 변경 시 호출.
        설계 스냅샷 갱신 + CoachAgent/ChaosAgent 트리거 검사.

        Returns:
            {
                "coach_hint": {...} | None,   # CoachAgent 개입 시
                "chaos_event": {...} | None,  # ChaosAgent 개입 시
            }
        """
        # 설계 스냅샷 갱신
        room_state.update_design(sid, nodes, arrows)

        result = {"coach_hint": None, "chaos_event": None}

        # CoachAgent 트리거 검사
        if self.state_machine.can_trigger_coach(room_state, sid):
            node_ids  = [n.get("compId", "") for n in nodes]
            arrow_cnt = len(arrows)
            hint = self.coach_agent.generate(
                mission_required = room_state.mission_required,
                deployed_nodes   = node_ids,
                arrow_count      = arrow_cnt,
                node_count       = len(nodes),
            )
            if hint.get("message"):  # "complete" 타입은 메시지 없음
                room_state.coach_triggered_at = time.time()
                result["coach_hint"] = hint
                logger.info(f"[Orchestrator] CoachAgent 개입: room={room_state.room_id}, sid={sid}, type={hint['type']}")

        # ChaosAgent 트리거 검사 (async이므로 별도 태스크로 실행)
        if self.state_machine.can_trigger_chaos(room_state):
            # 중복 방지를 위해 즉시 플래그 설정
            room_state.chaos_triggered_at = time.time()

            all_nodes = set()
            for design in room_state.player_designs.values():
                for n in design.get("nodes", []):
                    cid = n.get("compId", "") if isinstance(n, dict) else ""
                    if cid:
                        all_nodes.add(cid)

            chaos_event = self.chaos_agent.generate(
                mission_title  = room_state.mission_title,
                deployed_nodes = list(all_nodes),
                round_num      = 1,
            )
            room_state.chaos_event_id = chaos_event.get("event_id")

            # StateMachine: PLAYING → IN_BASKET
            self.state_machine.transition(room_state, GameState.IN_BASKET)
            result["chaos_event"] = chaos_event
            logger.info(f"[Orchestrator] ChaosAgent 개입: room={room_state.room_id}, event={chaos_event.get('event_id')}")

        return result

    # ──────────────────────────────────────────
    # IN_BASKET 만료 (타임아웃) — PLAYING 복귀
    # ──────────────────────────────────────────

    def on_incident_expired(self, room_state: DrawRoomState) -> bool:
        """
        장애 이벤트 타임아웃 시 IN_BASKET → PLAYING 복귀.

        Returns:
            True if 전환 성공
        """
        room_state.chaos_event_id = None
        return self.state_machine.transition(room_state, GameState.PLAYING)

    # ──────────────────────────────────────────
    # 양측 제출 완료 — EvalAgent 평가 실행
    # ──────────────────────────────────────────

    async def on_both_submitted(
        self,
        room_state: DrawRoomState,
        mission_title: str,
        rubric: Dict[str, Any],
        p1_data: Dict[str, Any],
        p2_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        양측 모두 제출 완료 시 호출.
        PLAYING/IN_BASKET → JUDGING → FINISHED 전환 + EvalAgent 평가 실행.

        Returns:
            EvalAgent 평가 결과 {player1: {...}, player2: {...}}
        """
        # JUDGING 상태로 전환
        self.state_machine.transition(room_state, GameState.JUDGING)

        # EvalAgent 평가 실행
        ai_reviews = await self.eval_agent.evaluate(
            mission_title = mission_title,
            p1_data       = p1_data,
            p2_data       = p2_data,
            rubric        = rubric,
        )

        # FINISHED 상태로 전환
        self.state_machine.transition(room_state, GameState.FINISHED)

        return ai_reviews

    # ──────────────────────────────────────────
    # 다음 라운드 — FINISHED → WAITING 리셋
    # ──────────────────────────────────────────

    def on_next_round(self, room_state: DrawRoomState) -> bool:
        """다음 라운드 준비 — FINISHED → WAITING"""
        return self.state_machine.transition(room_state, GameState.WAITING)
