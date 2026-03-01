"""
chaos/graph.py — ChaosAgent LangGraph 그래프 정의

[흐름도]
  START
    ↓
  analyze_vulnerability   (취약점 분석 — Think)
    ↓
  generate_event          (이벤트 생성 — Act)
    ↓
  self_validate           (품질 검증 — Observe)
    ↓
  [route_after_validate]
    ├─ needs_regen & retry < 2 → regenerate → self_validate (루프)
    └─ PASS 또는 retry 초과   → finalize
                                    ↓
                                  END
"""

import logging
from langgraph.graph import StateGraph, END

from core.services.wars.agents.chaos.state import ChaosAgentState
from core.services.wars.agents.chaos.nodes import (
    analyze_vulnerability,
    generate_event,
    self_validate,
    regenerate,
    finalize,
    route_after_validate,
)

logger = logging.getLogger(__name__)


def build_chaos_graph() -> StateGraph:
    builder = StateGraph(ChaosAgentState)

    builder.add_node("analyze_vulnerability", analyze_vulnerability)
    builder.add_node("generate_event", generate_event)
    builder.add_node("self_validate", self_validate)
    builder.add_node("regenerate", regenerate)
    builder.add_node("finalize", finalize)

    builder.set_entry_point("analyze_vulnerability")
    builder.add_edge("analyze_vulnerability", "generate_event")
    builder.add_edge("generate_event", "self_validate")

    builder.add_conditional_edges(
        "self_validate",
        route_after_validate,
        {
            "regenerate": "regenerate",
            "finalize": "finalize",
        },
    )

    builder.add_edge("regenerate", "self_validate")
    builder.add_edge("finalize", END)

    return builder.compile()


_chaos_graph = None


def get_chaos_graph():
    global _chaos_graph
    if _chaos_graph is None:
        _chaos_graph = build_chaos_graph()
        logger.info("[ChaosAgent] LangGraph 컴파일 완료")
    return _chaos_graph
