"""
state_machine.py — Wars Game State Machine
게임 상태 전환을 명시적으로 정의하고 관리한다.
LLM 없음. 순수 Python 규칙으로만 동작.

[States]
    WAITING    → 플레이어 대기 중
    PLAYING    → 실전 설계 중 (에이전트 감시 활성)
    IN_BASKET  → ChaosAgent 장애 이벤트 처리 중
    JUDGING    → 양측 제출 완료, EvalAgent 평가 중
    FINISHED   → 게임 종료

[Transitions]
    WAITING   → PLAYING   : 라운드 시작 (draw_start)
    PLAYING   → IN_BASKET : ChaosAgent 트리거
    IN_BASKET → PLAYING   : 장애 이벤트 만료 (타임아웃)
    PLAYING   → JUDGING   : 양측 모두 제출 완료
    JUDGING   → FINISHED  : EvalAgent 평가 완료
    FINISHED  → WAITING   : 다음 라운드 시작
"""

import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class GameState(str, Enum):
    WAITING   = "waiting"
    PLAYING   = "playing"
    IN_BASKET = "in_basket"
    JUDGING   = "judging"
    FINISHED  = "finished"


# 유효한 전환 테이블 — 이 외의 전환은 모두 거부
VALID_TRANSITIONS = {
    GameState.WAITING:   [GameState.PLAYING],
    GameState.PLAYING:   [GameState.IN_BASKET, GameState.JUDGING],
    GameState.IN_BASKET: [GameState.PLAYING, GameState.JUDGING],
    GameState.JUDGING:   [GameState.FINISHED],
    GameState.FINISHED:  [GameState.WAITING],
}


@dataclass
class DrawRoomState:
    """방별 ArchDrawQuiz 상태 스냅샷 — 에이전트들이 이 객체를 읽는다"""
    room_id: str
    state: GameState = GameState.WAITING
    entered_at: float = field(default_factory=time.time)

    # 현재 미션 정보
    mission_title: str = ""
    mission_required: list = field(default_factory=list)

    # 플레이어별 설계 스냅샷 {sid: {nodes, arrows, node_count, last_updated}}
    player_designs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # 에이전트 개입 이력 (중복 방지용)
    coach_triggered_at: float = 0.0    # CoachAgent 마지막 개입 시각
    chaos_triggered_at: float = 0.0    # ChaosAgent 마지막 개입 시각
    chaos_event_id: Optional[str] = None  # 진행 중인 장애 이벤트 ID

    def elapsed(self) -> float:
        """현재 상태 진입 후 경과 시간 (초)"""
        return time.time() - self.entered_at

    def update_design(self, sid: str, nodes: list, arrows: list):
        """플레이어 설계 스냅샷 갱신"""
        self.player_designs[sid] = {
            "nodes": nodes,
            "arrows": arrows,
            "node_count": len(nodes),
            "last_updated": time.time(),
        }

    def get_node_count(self, sid: str) -> int:
        return self.player_designs.get(sid, {}).get("node_count", 0)

    def seconds_since_last_update(self, sid: str) -> float:
        last = self.player_designs.get(sid, {}).get("last_updated", self.entered_at)
        return time.time() - last


class StateMachine:
    """Wars 게임 상태 머신 — 전환 유효성 검증 및 상태 변경 담당"""

    def transition(self, room_state: DrawRoomState, new_state: GameState) -> bool:
        """
        상태 전환 시도. 유효하면 전환하고 True 반환, 무효면 False 반환.
        """
        valid = VALID_TRANSITIONS.get(room_state.state, [])
        if new_state not in valid:
            print(
                f"[StateMachine] ❌ 무효 전환: {room_state.state} → {new_state} "
                f"(room: {room_state.room_id})"
            )
            return False

        print(f"[StateMachine] ✅ 상태 전환: {room_state.state} → {new_state} (room: {room_state.room_id})")
        room_state.state = new_state
        room_state.entered_at = time.time()
        return True

    def can_trigger_coach(self, room_state: DrawRoomState, sid: str) -> bool:
        """
        CoachAgent 개입 조건:
        - PLAYING 상태
        - 라운드 시작 후 30초 이상 경과
        - 마지막 CoachAgent 개입 후 60초 이상 경과 (도배 방지)
        - 노드 배치 수가 필수 컴포넌트의 절반 미만
        """
        if room_state.state != GameState.PLAYING:
            return False
        if room_state.elapsed() < 30:
            return False
        if time.time() - room_state.coach_triggered_at < 60:
            return False

        node_count = room_state.get_node_count(sid)
        required_count = len(room_state.mission_required)
        threshold = max(1, required_count // 2)

        return node_count < threshold

    def can_trigger_chaos(self, room_state: DrawRoomState) -> bool:
        """
        ChaosAgent 개입 조건:
        - PLAYING 상태
        - 라운드 시작 후 60초 이상 경과 (설계 시간 충분히 준 후)
        - 이전 장애 이벤트 없음 (라운드당 1회 제한)
        """
        if room_state.state != GameState.PLAYING:
            return False
        if room_state.elapsed() < 60:
            return False
        if room_state.chaos_triggered_at > 0:
            return False  # 이미 이번 라운드에 발동

        return True
