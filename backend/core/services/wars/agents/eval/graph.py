"""
eval/graph.py — EvalAgent LangGraph 그래프 정의

[흐름도]
  START
    ↓
  evaluate          (1차 평가)
    ↓
  self_critique     (품질 자기비판)
    ↓
  [route_after_critique]
    ├─ needs_revision & retry < 2 → revise → self_critique (루프)
    └─ PASS 또는 retry 초과      → finalize
                                      ↓
                                    END
"""

import logging
import threading
from langgraph.graph import StateGraph, END

from core.services.wars.agents.eval.state import EvalAgentState
from core.services.wars.agents.eval.nodes import (
    evaluate,
    self_critique,
    revise,
    finalize,
    route_after_critique,
)

logger = logging.getLogger(__name__)

_eval_graph = None
_eval_graph_lock = threading.Lock()


def build_eval_graph() -> StateGraph:
    """EvalAgent LangGraph 그래프 빌드 및 컴파일"""
    builder = StateGraph(EvalAgentState)

    builder.add_node("evaluate", evaluate)
    builder.add_node("self_critique", self_critique)
    builder.add_node("revise", revise)
    builder.add_node("finalize", finalize)

    builder.set_entry_point("evaluate")
    builder.add_edge("evaluate", "self_critique")

    builder.add_conditional_edges(
        "self_critique",
        route_after_critique,
        {
            "revise": "revise",
            "finalize": "finalize",
        },
    )

    builder.add_edge("revise", "self_critique")
    builder.add_edge("finalize", END)

    return builder.compile()


def get_eval_graph():
    """Thread-safe 싱글톤 — DCL(Double-Checked Locking) 패턴"""
    global _eval_graph
    if _eval_graph is None:
        with _eval_graph_lock:
            if _eval_graph is None:
                _eval_graph = build_eval_graph()
                logger.info("[EvalAgent] LangGraph 컴파일 완료")
    return _eval_graph
