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


def build_eval_graph() -> StateGraph:
    """EvalAgent LangGraph 그래프 빌드 및 컴파일"""

    builder = StateGraph(EvalAgentState)

    # 노드 등록
    builder.add_node("evaluate", evaluate)
    builder.add_node("self_critique", self_critique)
    builder.add_node("revise", revise)
    builder.add_node("finalize", finalize)

    # 엣지 정의
    builder.set_entry_point("evaluate")
    builder.add_edge("evaluate", "self_critique")

    # self_critique → 조건 분기
    builder.add_conditional_edges(
        "self_critique",
        route_after_critique,
        {
            "revise": "revise",
            "finalize": "finalize",
        },
    )

    # revise 후 다시 self_critique (루프)
    builder.add_edge("revise", "self_critique")

    # finalize → 종료
    builder.add_edge("finalize", END)

    return builder.compile()


# 싱글톤 그래프 인스턴스
_eval_graph = None


def get_eval_graph():
    global _eval_graph
    if _eval_graph is None:
        _eval_graph = build_eval_graph()
        logger.info("[EvalAgent] LangGraph 컴파일 완료")
    return _eval_graph
