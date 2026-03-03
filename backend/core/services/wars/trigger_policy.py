"""
trigger_policy.py — Wars Agent 개입 조건 판단 서비스

StateMachine에서 분리된 비즈니스 정책 레이어.
StateMachine은 상태 전환만 담당하고,
"언제 에이전트를 개입시킬지"에 대한 판단은 이 모듈이 담당한다.

사용처:
  - orchestrator/nodes.py (_rule_based_action_plan 폴백)
  - orchestrator.py (직접 호출 없음 — nodes.py 를 통해 간접 사용)
"""

import time
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.services.wars.state_machine import DrawRoomState

logger = logging.getLogger(__name__)

# ── 공통 상수 ─────────────────────────────────────────────────────────────────
_ROUND_START_GRACE     = 10   # 라운드 시작 후 자유 탐색 보장 시간 (초) (20 -> 10 하향)
_COACH_COOLDOWN        = 40   # Coach 개입 후 재개입 최소 간격 (초) (45 -> 40 하향)
_COACH_INACTIVITY      = 15   # 무조작 시간 기준 (초) (25 -> 15 하향)
_COACH_NO_NODE_ELAPSED = 20   # 이 시간이 지나도 노드 1개 이하면 개입 (30 -> 20 하향)
_COACH_MISSING_ELAPSED = 25   # 이 시간이 지나도 필수 컴포넌트 50% 이상 누락이면 개입 (35 -> 25 하향)
_CHAOS_MIN_NODES       = 2    # Chaos 발동 최소 배치 노드 수 (3 -> 2 하향)


def can_trigger_coach(room_state: "DrawRoomState", sid: str) -> bool:
    """
    CoachAgent 개입 가능 여부 판단.

    핵심 원칙: 플레이어가 '실제로 헤매는 상황'일 때만 개입한다.
    게임 시작 직후나 이제 막 배치를 시작한 상황에서는 개입하지 않는다.

    조건 (모두 통과해야 함):
      1. PLAYING 상태
      2. 라운드 시작 후 10초 이상 경과 (초반 자유 탐색 보장)
      3. 해당 플레이어 본인의 마지막 Coach 개입 후 40초 이상 경과 (도배 방지)

    + 아래 '헤매는 상황' 중 하나 이상 해당:
      A. 15초 이상 아무 조작 없음 (멈춰있음)
      B. 20초 지났는데 노드가 1개 이하 (조작 미비)
      C. 25초 지났는데 필수 컴포넌트 50% 이상 누락
    """
    from core.services.wars.state_machine import GameState

    if room_state.state != GameState.PLAYING:
        return False

    elapsed = room_state.elapsed()

    if elapsed < _ROUND_START_GRACE:
        return False

    # [수정일: 2026-03-03] 플레이어별 개별 쿨다운 적용 (hint_history 참조)
    history = room_state.hint_history.get(sid, [])
    last_hint_time = history[-1].get("_time", 0) if history else 0
    if time.time() - last_hint_time < _COACH_COOLDOWN:
        return False

    node_count = room_state.get_node_count(sid)
    required_count = len(room_state.mission_required)
    missing_ratio = 1.0
    if required_count > 0:
        deployed_ids = set()
        for n in room_state.player_designs.get(sid, {}).get('nodes', []):
            if isinstance(n, dict):
                deployed_ids.add(n.get('compId', ''))
        missing_count = len(set(room_state.mission_required) - deployed_ids)
        missing_ratio = missing_count / required_count

    # 헤매는 상황 A: 25초 이상 무조작
    inactivity = room_state.seconds_since_last_update(sid)
    if inactivity > _COACH_INACTIVITY:
        logger.debug(f"[TriggerPolicy] Coach 트리거 — 무조작 {inactivity:.0f}s (sid={sid[:8]})")
        return True

    # 헤매는 상황 B: 30초 지났는데 노드 1개 이하
    if elapsed > _COACH_NO_NODE_ELAPSED and node_count <= 1:
        logger.debug(f"[TriggerPolicy] Coach 트리거 — {elapsed:.0f}s 경과, 노드={node_count}개")
        return True

    # 헤매는 상황 C: 35초 지났는데 필수 컴포넌트 50% 이상 누락
    if elapsed > _COACH_MISSING_ELAPSED and missing_ratio >= 0.5:
        logger.debug(f"[TriggerPolicy] Coach 트리거 — {elapsed:.0f}s 경과, 누락={missing_ratio:.0%}")
        return True

    return False


def can_trigger_chaos(room_state: "DrawRoomState") -> bool:
    """
    ChaosAgent 개입 가능 여부 판단.

    핵심 원칙: 플레이어가 어느 정도 설계를 한 상태에서만 발동한다.
    아무것도 없는 캔버스에 장애를 내보내는 건 교육적 의미가 없다.

    조건 (모두 통과해야 함):
      1. PLAYING 상태
      2. 라운드 시작 후 20초 이상 경과
      3. 라운드당 1회 제한 (chaos_triggered_at == 0)
      4. 양측 합산 배치 노드가 최소 3개 이상
    """
    from core.services.wars.state_machine import GameState

    if room_state.state != GameState.PLAYING:
        return False

    if room_state.elapsed() < _ROUND_START_GRACE:
        return False

    if room_state.chaos_triggered_at > 0:
        return False

    total_nodes = sum(
        d.get('node_count', 0)
        for d in room_state.player_designs.values()
    )
    if total_nodes < _CHAOS_MIN_NODES:
        logger.debug(
            f"[TriggerPolicy] Chaos 대기 — 총 노드={total_nodes}개 (최소 {_CHAOS_MIN_NODES}개 필요)"
        )
        return False

    logger.debug(
        f"[TriggerPolicy] Chaos 조건 충족 — 총 노드={total_nodes}개, "
        f"elapsed={room_state.elapsed():.0f}s"
    )
    return True
