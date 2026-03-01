"""
chaos_agent.py — ChaosAgent (LangGraph 버전)

기존 단순 LLM 1회 호출에서 진짜 Agent로 교체.
[흐름] analyze_vulnerability → generate_event → self_validate → (regenerate 루프) → finalize

past_event_ids를 받아 라운드 내 중복 이벤트를 자동으로 방지한다.
"""

import logging
from typing import Dict, Any, List

from core.services.wars.agents.chaos.graph import get_chaos_graph

logger = logging.getLogger(__name__)


class ChaosAgent:
    """
    LangGraph 기반 장애 이벤트 생성 에이전트.
    취약점 분석(Think) → 이벤트 생성(Act) → 품질 검증(Observe) 루프.
    """

    def generate(
        self,
        mission_title: str,
        deployed_nodes: List[str],
        round_num: int = 1,
        past_event_ids: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Args:
            mission_title    : 현재 미션 제목
            deployed_nodes   : 양측 플레이어 합산 배치 컴포넌트 목록
            round_num        : 현재 라운드 번호
            past_event_ids   : 이미 발동된 이벤트 ID 목록 (중복 방지)

        Returns:
            {event_id, title, description, severity, target_components, hint}
        """
        initial_state = {
            "mission_title": mission_title,
            "deployed_nodes": deployed_nodes,
            "round_num": round_num,
            "past_event_ids": past_event_ids or [],
            "vulnerability": None,
            "raw_event": None,
            "validation": None,
            "needs_regen": False,
            "retry_count": 0,
            "final_event": None,
        }

        graph = get_chaos_graph()
        final_state = graph.invoke(initial_state)

        event = final_state.get("final_event")
        if not event:
            logger.error("[ChaosAgent] final_event 없음 — 긴급 폴백")
            from core.services.wars.agents.chaos.nodes import _fallback_by_nodes
            event = _fallback_by_nodes(deployed_nodes)

        logger.info(
            f"[ChaosAgent] ✅ 완료: event_id={event.get('event_id')}, "
            f"severity={event.get('severity')}, retry={final_state.get('retry_count', 0)}"
        )
        return event
