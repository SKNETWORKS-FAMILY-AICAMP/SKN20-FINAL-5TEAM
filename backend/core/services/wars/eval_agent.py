"""
eval_agent.py — EvalAgent (LangGraph 버전)

기존 단순 LLM 래퍼에서 진짜 Agent로 교체.
[흐름] evaluate → self_critique → (revise 루프) → finalize
"""

import logging
from typing import Dict, Any

from asgiref.sync import sync_to_async
from core.services.wars.agents.eval.graph import get_eval_graph

logger = logging.getLogger(__name__)


class EvalAgent:
    """
    LangGraph 기반 평가 에이전트.
    evaluate → self_critique → revise(최대 2회) → finalize 루프 실행.
    """

    async def evaluate(
        self,
        mission_title: str,
        p1_data: Dict[str, Any],
        p2_data: Dict[str, Any],
        rubric: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        logger.info(f"[EvalAgent] 평가 시작: {mission_title}")

        initial_state = {
            "mission_title": mission_title,
            "p1_data": p1_data,
            "p2_data": p2_data,
            "rubric": rubric,
            "raw_result": None,
            "critique": None,
            "needs_revision": False,
            "retry_count": 0,
            "revised_result": None,
            "final_result": None,
        }

        graph = get_eval_graph()

        # LangGraph는 동기 실행 → sync_to_async로 래핑
        run_graph = sync_to_async(graph.invoke)
        final_state = await run_graph(initial_state)

        result = final_state.get("final_result")
        if not result:
            logger.error("[EvalAgent] final_result 없음")
            from core.services.arch_evaluator import ArchEvaluator
            result = ArchEvaluator()._fallback_review(p1_data, p2_data)

        logger.info(f"[EvalAgent] ✅ 평가 완료 (retry={final_state.get('retry_count', 0)})")
        return result
