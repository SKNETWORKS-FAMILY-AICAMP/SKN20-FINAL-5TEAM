"""
orchestrator/graph.py — OrchestratorAgent LangGraph 그래프 정의

[흐름도]
  START
    ↓
  observe_game_state  (상황 파악 — Observe)
    ↓
  decide_action       (행동 결정 — Think / LLM)
    ↓
  [_route_after_decide]
    ├─ 모두 "none" → done (dispatch 스킵 — 불필요한 에이전트 호출 방지)
    └─ 그 외       → dispatch → done
                        ↓
                      END
"""

import logging
import threading
from langgraph.graph import StateGraph, END

from core.services.wars.agents.orchestrator.state import OrchestratorState
from core.services.wars.agents.orchestrator.nodes import (
    observe_game_state,
    decide_action,
    dispatch,
    done,
)

logger = logging.getLogger(__name__)

_orchestrator_graph = None
_orchestrator_graph_lock = threading.Lock()


def _route_after_decide(state: OrchestratorState) -> str:
    plan = state.get("action_plan", [])
    if all(a.get("agent") == "none" for a in plan):
        return "done"
    return "dispatch"


def build_orchestrator_graph() -> StateGraph:
    builder = StateGraph(OrchestratorState)

    builder.add_node("observe_game_state", observe_game_state)
    builder.add_node("decide_action", decide_action)
    builder.add_node("dispatch", dispatch)
    builder.add_node("done", done)

    builder.set_entry_point("observe_game_state")
    builder.add_edge("observe_game_state", "decide_action")

    builder.add_conditional_edges(
        "decide_action",
        _route_after_decide,
        {"done": "done", "dispatch": "dispatch"},
    )

    builder.add_edge("dispatch", "done")
    builder.add_edge("done", END)

    return builder.compile()


def get_orchestrator_graph():
    """Thread-safe 싱글톤 — DCL(Double-Checked Locking) 패턴"""
    global _orchestrator_graph
    if _orchestrator_graph is None:
        with _orchestrator_graph_lock:
            if _orchestrator_graph is None:
                _orchestrator_graph = build_orchestrator_graph()
                logger.info("[OrchestratorAgent] LangGraph 컴파일 완료")
    return _orchestrator_graph
