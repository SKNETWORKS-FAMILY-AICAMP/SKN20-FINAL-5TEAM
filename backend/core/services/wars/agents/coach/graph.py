"""
coach/graph.py — CoachAgent LangGraph 그래프 정의

[흐름도]
  START
    ↓
  analyze_situation   (상황 파악)
    ↓
  decide_strategy     (전략 결정)
    ↓
  [route_after_strategy]
    ├─ strategy == "skip"  → skip → END
    └─ 그 외               → generate_hint → END
"""

import logging
import threading
from langgraph.graph import StateGraph, END

from core.services.wars.agents.coach.state import CoachAgentState
from core.services.wars.agents.coach.nodes import (
    analyze_situation,
    decide_strategy,
    generate_hint,
    skip,
    route_after_strategy,
)

logger = logging.getLogger(__name__)

_coach_graph = None
_coach_graph_lock = threading.Lock()


def build_coach_graph() -> StateGraph:
    builder = StateGraph(CoachAgentState)

    builder.add_node("analyze_situation", analyze_situation)
    builder.add_node("decide_strategy", decide_strategy)
    builder.add_node("generate_hint", generate_hint)
    builder.add_node("skip", skip)

    builder.set_entry_point("analyze_situation")
    builder.add_edge("analyze_situation", "decide_strategy")

    builder.add_conditional_edges(
        "decide_strategy",
        route_after_strategy,
        {
            "skip": "skip",
            "generate_hint": "generate_hint",
        },
    )

    builder.add_edge("generate_hint", END)
    builder.add_edge("skip", END)

    return builder.compile()


def get_coach_graph():
    """Thread-safe 싱글톤 — DCL(Double-Checked Locking) 패턴"""
    global _coach_graph
    if _coach_graph is None:
        with _coach_graph_lock:
            if _coach_graph is None:
                _coach_graph = build_coach_graph()
                logger.info("[CoachAgent] LangGraph 컴파일 완료")
    return _coach_graph
