"""
orchestrator/state.py — OrchestratorAgent LangGraph State

[노드 흐름]
  observe_game_state → decide_action → dispatch → observe_result → done

[역할]
  기존 Orchestrator: 소켓 이벤트마다 단순히 조건 체크 후 에이전트 호출
  신규 Orchestrator: 게임 전체 맥락을 보고 최적의 에이전트 조합과 타이밍을 AI가 결정

[State 필드]
  입력:
    - room_id            : 방 ID
    - game_state_name    : 현재 StateMachine 상태 (playing/in_basket/...)
    - mission_title      : 현재 미션
    - mission_required   : 필수 컴포넌트 목록
    - elapsed_seconds    : 라운드 시작 후 경과 시간
    - player_snapshots   : {sid: {node_count, arrow_count, deployed_nodes, seconds_inactive}}
    - hint_history       : {sid: [{type, level}, ...]}
    - chaos_triggered    : 이번 라운드 ChaosAgent 이미 발동 여부
    - past_event_ids     : 이미 발동된 이벤트 ID 목록
    - trigger_sid        : 이번 canvas_update를 보낸 플레이어 sid

  중간:
    - situation_summary  : observe_game_state가 정리한 전체 상황 요약
    - action_plan        : decide_action이 결정한 행동 목록
                           예: [{"agent": "coach", "sid": "xxx"}, {"agent": "chaos"}]
    - dispatched         : dispatch 완료 여부

  출력:
    - coach_hint         : CoachAgent 결과 (없으면 None)
    - chaos_event        : ChaosAgent 결과 (없으면 None)
    - actions_taken      : 실제 실행된 액션 목록 (로깅용)
"""

from __future__ import annotations
from typing import TypedDict, Optional, List, Dict, Any


class OrchestratorState(TypedDict):
    # ── 입력 ────────────────────────────────────
    room_id: str
    game_state_name: str
    mission_title: str
    mission_required: List[str]
    elapsed_seconds: float
    player_snapshots: Dict[str, Dict[str, Any]]   # {sid: {node_count, arrow_count, deployed_nodes, seconds_inactive}}
    hint_history: Dict[str, List[Dict[str, Any]]]  # {sid: [{type, level, message},...]}
    chaos_triggered: bool
    past_event_ids: List[str]
    trigger_sid: str                               # 이번 canvas_update 발신자

    # ── 중간 ────────────────────────────────────
    situation_summary: Optional[str]
    action_plan: Optional[List[Dict[str, Any]]]    # [{"agent": "coach"|"chaos"|"none", "sid": str|None, "reason": str}]
    dispatched: bool

    # ── 출력 ────────────────────────────────────
    coach_hint: Optional[Dict[str, Any]]
    chaos_event: Optional[Dict[str, Any]]
    actions_taken: List[str]
