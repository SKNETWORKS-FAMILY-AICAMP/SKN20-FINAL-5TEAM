"""
orchestrator/graph.py — OrchestratorAgent LangGraph 그래프 정의

[흐름도]
  START
    ↓
  observe_game_state  (상황 파악 — Observe)
    ↓
  decide_action       (행동 결정 — Think / LLM)
    ↓
  dispatch            (에이전트 실행 — Act)
    ↓
  done                (결과 정리)
    ↓
  END
"""

import logging
from langgraph.graph import StateGraph, END

from core.services.wars.agents.orchestrator.state import OrchestratorState
from core.services.wars.agents.orchestrator.nodes import (
    observe_game_state,
    decide_action,
    dispatch,
    done,
)

logger = logging.getLogger(__name__)


def build_orchestrator_graph() -> StateGraph:
    builder = StateGraph(OrchestratorState)

    builder.add_node("observe_game_state", observe_game_state)
    builder.add_node("decide_action", decide_action)
    builder.add_node("dispatch", dispatch)
    builder.add_node("done", done)

    builder.set_entry_point("observe_game_state")
    builder.add_edge("observe_game_state", "decide_action")

    # [수정일: 2026-03-01] none 플램이면 dispatch 스킵 — 불필요한 AI 호출 방지
    def _route_after_decide(state):
        plan = state.get("action_plan", [])
        if all(a.get("agent") == "none" for a in plan):
            return "done"
        return "dispatch"

    builder.add_conditional_edges(
        "decide_action",
        _route_after_decide,
        {"done": "done", "dispatch": "dispatch"},
    )
    builder.add_edge("dispatch", "done")
    builder.add_edge("done", END)

    return builder.compile()


_orchestrator_graph = None


def get_orchestrator_graph():
    global _orchestrator_graph
    if _orchestrator_graph is None:
        _orchestrator_graph = build_orchestrator_graph()
        logger.info("[OrchestratorAgent] LangGraph 컴파일 완료")
    return _orchestrator_graph
