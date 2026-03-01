"""
orchestrator/nodes.py — OrchestratorAgent LangGraph 노드 정의

[노드 목록]
  observe_game_state : 전체 게임 맥락 수집 및 상황 요약 (Observe)
  decide_action      : 상황 요약 기반 최적 행동 결정 (Think / LLM)
  dispatch           : 결정된 에이전트들 실행 (Act)
  done               : 결과 정리 및 종료

[기존 Orchestrator와의 차이]
  기존: can_trigger_coach() and can_trigger_chaos() → 단순 조건 분기
  신규: 전체 게임 맥락(양쪽 플레이어 상태, 이력, 경과시간)을 LLM이 보고
        "지금 Coach만 개입할지, Chaos만 발동할지, 둘 다 할지, 아무것도 안 할지"를 판단
        + StateMachine 조건은 하드 가드로 유지 (무결성 보장)
"""

import json
import logging
import time
from typing import Dict, Any, List

from django.conf import settings

try:
    import openai
except ImportError:
    openai = None

from core.services.wars.agents.orchestrator.state import OrchestratorState

logger = logging.getLogger(__name__)


def _get_client():
    if openai and getattr(settings, "OPENAI_API_KEY", None):
        return openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Node 1: observe_game_state
# ─────────────────────────────────────────────────────────────────────────────

def observe_game_state(state: OrchestratorState) -> OrchestratorState:
    """
    [Observe] 현재 게임 상태를 인간이 읽기 쉬운 상황 요약으로 변환.
    LLM 없음 — 룰 기반으로 빠르게 요약 생성.
    """
    logger.info(f"[Orchestrator] ▶ observe_game_state (room={state['room_id']}, elapsed={state['elapsed_seconds']:.0f}s)")

    snapshots = state.get("player_snapshots", {})
    required = set(state.get("mission_required", []))
    hint_history = state.get("hint_history", {})

    lines = [
        f"미션: {state['mission_title']}",
        f"게임 상태: {state['game_state_name']}",
        f"경과 시간: {state['elapsed_seconds']:.0f}초",
        f"ChaosAgent 발동 여부: {'발동됨' if state.get('chaos_triggered') else '미발동'}",
    ]

    for sid, snap in snapshots.items():
        deployed = set(snap.get("deployed_nodes", []))
        missing = list(required - deployed)
        history = hint_history.get(sid, [])
        last_hint_level = history[-1].get("level", 0) if history else 0
        inactive = snap.get("seconds_inactive", 0)

        lines.append(
            f"플레이어 {sid[:8]}: "
            f"노드={snap.get('node_count', 0)}, "
            f"화살표={snap.get('arrow_count', 0)}, "
            f"누락={missing[:3]}, "
            f"무조작={inactive:.0f}s, "
            f"힌트횟수={len(history)}, 마지막힌트레벨={last_hint_level}"
        )

    summary = "\n".join(lines)
    logger.info(f"[Orchestrator] 상황 요약:\n{summary}")
    return {**state, "situation_summary": summary}


# ─────────────────────────────────────────────────────────────────────────────
# Node 2: decide_action
# ─────────────────────────────────────────────────────────────────────────────

def decide_action(state: OrchestratorState) -> OrchestratorState:
    """
    [Think] 상황 요약을 보고 최적 행동 결정.

    LLM 있을 때: 전체 맥락 분석 후 행동 계획 JSON 반환
    LLM 없을 때: 룰 기반 하드코딩 로직 (기존 can_trigger 조건)
    """
    logger.info("[Orchestrator] ▶ decide_action 노드 실행")

    client = _get_client()

    # ── 하드 가드 조건 (StateMachine 규칙 — LLM이 무시할 수 없음) ──────────────
    if state["game_state_name"] != "playing":
        logger.info(f"[Orchestrator] 게임 상태 {state['game_state_name']} → 행동 없음")
        return {**state, "action_plan": [{"agent": "none", "sid": None, "reason": "게임 상태가 playing이 아님"}]}

    if state["elapsed_seconds"] < 10:
        logger.info("[Orchestrator] 10초 미경과 → 행동 없음")
        return {**state, "action_plan": [{"agent": "none", "sid": None, "reason": "라운드 시작 직후"}]}

    if not client:
        plan = _rule_based_action_plan(state)
        return {**state, "action_plan": plan}

    try:
        plan = _llm_decide(state)
    except Exception as e:
        logger.error(f"[Orchestrator] decide_action LLM 실패: {e} → 룰 기반 폴백")
        plan = _rule_based_action_plan(state)

    logger.info(f"[Orchestrator] 행동 계획: {plan}")
    return {**state, "action_plan": plan}


def _llm_decide(state: OrchestratorState) -> List[Dict[str, Any]]:
    """LLM 기반 행동 결정"""
    client = _get_client()
    snapshots = state.get("player_snapshots", {})
    hint_history = state.get("hint_history", {})

    # 각 플레이어별 힌트 쿨다운 계산
    player_info = []
    for sid, snap in snapshots.items():
        history = hint_history.get(sid, [])
        hint_count = len(history)
        last_level = history[-1].get("level", 0) if history else 0
        # [수정일: 2026-03-01] 히늨트 시간 정보 추가 — LLM이 쿨다운 판단 가능하도록
        last_hint_time = history[-1].get("_time", 0) if history else 0
        seconds_since_hint = round(time.time() - last_hint_time) if last_hint_time else 9999
        player_info.append({
            "sid": sid[:8],
            "full_sid": sid,
            "node_count": snap.get("node_count", 0),
            "arrow_count": snap.get("arrow_count", 0),
            "seconds_inactive": snap.get("seconds_inactive", 0),
            "hint_count": hint_count,
            "last_hint_level": last_level,
            "seconds_since_last_hint": seconds_since_hint,  # [수정일: 2026-03-01] 추가
        })

    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """당신은 아키텍처 교육 게임의 Orchestrator AI입니다.
현재 게임 상황을 분석하고 어떤 에이전트를 발동할지 결정합니다.

규칙:
- coach: 특정 플레이어에게 힌트 (sid 필수). 힌트를 너무 자주 주면 학습 효과가 떨어짐.
- chaos: 장애 이벤트 발동 (sid 불필요). chaos_triggered가 True면 절대 선택 불가.
- none: 아무 행동도 하지 않음.
- coach와 chaos를 동시에 선택할 수 있음.

JSON 배열로만 응답합니다.""",
            },
            {
                "role": "user",
                "content": f"""[현재 상황]
{state.get('situation_summary', '')}

[플레이어 상세]
{json.dumps(player_info, ensure_ascii=False, indent=2)}

[제약]
- chaos_triggered: {state.get('chaos_triggered')} (True면 chaos 선택 불가)
- 경과 시간: {state['elapsed_seconds']:.0f}초
- chaos 최소 발동 시간: 25초 이상
- 이번 canvas_update 발신자: {state.get('trigger_sid', '')[:8]}

위 상황에서 최적의 행동을 결정하세요.

출력 형식 (JSON 배열만):
[
  {{"agent": "coach", "sid": "full_sid_here", "reason": "판단 이유"}},
  {{"agent": "chaos", "sid": null, "reason": "판단 이유"}}
]

아무것도 안 할 경우:
[{{"agent": "none", "sid": null, "reason": "이유"}}]""",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
        timeout=8,
    )

    content = response.choices[0].message.content
    parsed = json.loads(content)

    # LLM이 {"actions": [...]} 형태로 반환하는 경우 대응
    if isinstance(parsed, dict):
        plan = parsed.get("actions", parsed.get("plan", [parsed]))
    else:
        plan = parsed

    # chaos_triggered 하드 가드 재적용
    if state.get("chaos_triggered"):
        plan = [a for a in plan if a.get("agent") != "chaos"]
        if not plan:
            plan = [{"agent": "none", "sid": None, "reason": "chaos 이미 발동됨"}]

    # elapsed < 25 chaos 가드
    if state["elapsed_seconds"] < 25:
        plan = [a for a in plan if a.get("agent") != "chaos"]
        if not plan:
            plan = [{"agent": "none", "sid": None, "reason": "chaos 최소 시간 미충족"}]

    return plan


def _rule_based_action_plan(state: OrchestratorState) -> List[Dict[str, Any]]:
    """LLM 없을 때 StateMachine.can_trigger_* 사용 — [수정일: 2026-03-01] 중복 로직 제거"""
    from core.services.wars.state_machine import StateMachine, DrawRoomState as _DrawRoomState

    plan = []
    trigger_sid = state.get("trigger_sid", "")
    snapshots = state.get("player_snapshots", {})
    hint_history = state.get("hint_history", {})
    elapsed = state["elapsed_seconds"]

    # [수정일: 2026-03-01] 인라인 조건 중복 작성 대신 StateMachine 이용
    # OrchestratorState에서 다시 DrawRoomState-유사 객체를 임시 생성해서 can_trigger_* 호출
    sm = StateMachine()

    # 임시 DrawRoomState 스냅샷 생성 (StateMachine 메서드 인자 포맷 일치)
    tmp_room = _DrawRoomState(room_id=state.get("room_id", ""))
    tmp_room.state = __import__('core.services.wars.state_machine', fromlist=['GameState']).GameState(state["game_state_name"])
    tmp_room.entered_at = time.time() - elapsed
    tmp_room.mission_required = state.get("mission_required", [])
    tmp_room.player_designs = {
        sid: {"node_count": snap.get("node_count", 0), "last_updated": time.time() - snap.get("seconds_inactive", 0)}
        for sid, snap in snapshots.items()
    }
    tmp_room.hint_history = hint_history
    tmp_room.coach_triggered_at = 0.0  # can_trigger_coach는 room_state의 coach_triggered_at를 사용
    # 힙트 이력에서 최근 코치 개입 시각 복원
    all_hints = [h for hs in hint_history.values() for h in hs]
    if all_hints:
        tmp_room.coach_triggered_at = max(h.get("_time", 0) for h in all_hints)
    tmp_room.chaos_triggered_at = 1.0 if state.get("chaos_triggered") else 0.0

    # Coach 조건 — StateMachine에 위임
    if sm.can_trigger_coach(tmp_room, trigger_sid):
        plan.append({"agent": "coach", "sid": trigger_sid, "reason": "룰 기반(StateMachine): 정체 감지"})

    # Chaos 조건 — StateMachine에 위임
    if sm.can_trigger_chaos(tmp_room):
        plan.append({"agent": "chaos", "sid": None, "reason": "룰 기반(StateMachine): chaos 발동 조건 충족"})

    if not plan:
        plan.append({"agent": "none", "sid": None, "reason": "룰 기반: 조건 미충족"})

    return plan


# ─────────────────────────────────────────────────────────────────────────────
# Node 3: dispatch
# ─────────────────────────────────────────────────────────────────────────────

def dispatch(state: OrchestratorState) -> OrchestratorState:
    """
    [Act] action_plan에 따라 실제 에이전트를 호출한다.
    CoachAgent와 ChaosAgent를 직접 임포트해서 실행.
    """
    logger.info("[Orchestrator] ▶ dispatch 노드 실행")

    from core.services.wars.coach_agent import CoachAgent
    from core.services.wars.chaos_agent import ChaosAgent

    coach_agent = CoachAgent()
    chaos_agent = ChaosAgent()

    plan = state.get("action_plan", [])
    snapshots = state.get("player_snapshots", {})
    hint_history = state.get("hint_history", {})

    coach_hint = None
    chaos_event = None
    actions_taken = []

    for action in plan:
        agent_type = action.get("agent")

        if agent_type == "coach":
            sid = action.get("sid") or state.get("trigger_sid", "")
            snap = snapshots.get(sid, {})
            history = hint_history.get(sid, [])

            hint = coach_agent.generate(
                mission_required=state["mission_required"],
                deployed_nodes=snap.get("deployed_nodes", []),
                arrow_count=snap.get("arrow_count", 0),
                node_count=snap.get("node_count", 0),
                hint_history=history,
            )
            if hint.get("message"):
                coach_hint = {**hint, "_target_sid": sid}
                actions_taken.append(f"coach→{sid[:8]} (level={hint.get('level')})")
                logger.info(f"[Orchestrator] CoachAgent 실행: sid={sid[:8]}, level={hint.get('level')}")

        elif agent_type == "chaos":
            all_nodes = set()
            for snap in snapshots.values():
                all_nodes.update(snap.get("deployed_nodes", []))

            event = chaos_agent.generate(
                mission_title=state["mission_title"],
                deployed_nodes=list(all_nodes),
                round_num=1,
                past_event_ids=state.get("past_event_ids", []),
            )
            chaos_event = event
            actions_taken.append(f"chaos: {event.get('event_id')} (severity={event.get('severity')})")
            logger.info(f"[Orchestrator] ChaosAgent 실행: {event.get('event_id')}")

        elif agent_type == "none":
            logger.info(f"[Orchestrator] 행동 없음: {action.get('reason', '')}")

    return {
        **state,
        "coach_hint": coach_hint,
        "chaos_event": chaos_event,
        "actions_taken": actions_taken,
        "dispatched": True,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 4: done
# ─────────────────────────────────────────────────────────────────────────────

def done(state: OrchestratorState) -> OrchestratorState:
    """결과 정리 및 로깅"""
    logger.info(
        f"[Orchestrator] ✅ 완료: room={state['room_id']}, "
        f"actions={state.get('actions_taken', [])}"
    )
    return state
