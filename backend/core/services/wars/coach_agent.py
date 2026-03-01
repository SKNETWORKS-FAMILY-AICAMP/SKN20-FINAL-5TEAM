"""
coach_agent.py — CoachAgent (LangGraph 버전)

기존 if/else 룰 기반에서 진짜 Agent로 교체.
[흐름] analyze_situation → decide_strategy → generate_hint(or skip)
힌트 이력(hint_history)을 받아 단계적 코칭 전략을 동적으로 결정한다.
"""

import logging
from typing import Dict, Any, List

from core.services.wars.agents.coach.graph import get_coach_graph

logger = logging.getLogger(__name__)


class CoachAgent:
    """
    LangGraph 기반 코칭 에이전트.
    상황 분석 → 전략 결정 → 힌트 생성 루프 실행.
    hint_history를 받아 이전 힌트를 고려한 단계적 코칭을 수행한다.
    """

    def generate(
        self,
        mission_required: list,
        deployed_nodes: list,
        arrow_count: int = 0,
        node_count: int = 0,
        hint_history: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Args:
            mission_required : 이번 미션의 필수 컴포넌트 ID 목록
            deployed_nodes   : 플레이어가 현재 배치한 컴포넌트 ID 목록
            arrow_count      : 현재 화살표 수
            node_count       : 현재 배치 노드 수
            hint_history     : 이전 힌트 목록 [{message, type, level}, ...]

        Returns:
            {message, missing_components, type, level}
        """
        initial_state = {
            "mission_required": mission_required,
            "deployed_nodes": deployed_nodes,
            "arrow_count": arrow_count,
            "node_count": node_count,
            "hint_history": hint_history or [],
            "situation": None,
            "strategy": None,
            "hint": None,
            "done": False,
        }

        graph = get_coach_graph()
        final_state = graph.invoke(initial_state)

        hint = final_state.get("hint") or {
            "message": "", "missing_components": [], "type": "complete", "level": 0
        }

        logger.info(
            f"[CoachAgent] ✅ 힌트 생성 완료: "
            f"situation={final_state.get('situation')}, "
            f"strategy={final_state.get('strategy')}, "
            f"type={hint.get('type')}, level={hint.get('level')}"
        )
        return hint
