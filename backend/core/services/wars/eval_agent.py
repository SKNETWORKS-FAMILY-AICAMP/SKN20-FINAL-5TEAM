"""
eval_agent.py — EvalAgent
기존 ArchEvaluator를 에이전트 역할로 분리한 래퍼.
WarsOrchestrator가 이 에이전트를 호출하여 평가를 수행한다.

[기존 방식 — socket_server.py 안에 직접 호출]
    eval_func = sync_to_async(arch_evaluator.evaluate_comparison)
    ai_reviews = await eval_func(mission_title, p1_data, p2_data, rubric=rubric_data)

[에이전트 방식 — WarsOrchestrator를 통해 호출]
    orchestrator = WarsOrchestrator(room_id)
    results = await orchestrator.run_evaluation(room)
    # 내부적으로 EvalAgent → ArchEvaluator 호출

역할 분리 이유:
    socket_server는 네트워크 I/O만 담당
    평가 로직은 EvalAgent가 캡슐화
    테스트/교체가 용이한 구조
"""

import logging
from typing import Dict, Any

from asgiref.sync import sync_to_async
from core.services.arch_evaluator import ArchEvaluator

logger = logging.getLogger(__name__)


class EvalAgent:
    """
    ArchDrawQuiz 라운드 평가 에이전트.
    기존 ArchEvaluator를 래핑하여 에이전트 인터페이스로 제공.

    역할:
        - 양측 플레이어 설계 데이터를 입력받아 AI 평가 수행
        - 평가 결과를 표준 포맷으로 반환
        - 실패 시 폴백 리뷰 자동 반환 (게임 중단 방지)
    """

    def __init__(self):
        self._evaluator = ArchEvaluator()

    async def evaluate(
        self,
        mission_title: str,
        p1_data: Dict[str, Any],
        p2_data: Dict[str, Any],
        rubric: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        두 플레이어 설계를 비교 평가한다.

        Args:
            mission_title: 미션 제목
            p1_data: {name, pts, checks, nodes, arrows}
            p2_data: {name, pts, checks, nodes, arrows}
            rubric: DB에서 로드한 평가 기준표

        Returns:
            {
                "player1": {"my_analysis": "...", "versus": "..."},
                "player2": {"my_analysis": "...", "versus": "..."}
            }
        """
        logger.info(f"[EvalAgent] 평가 시작: {mission_title} | {p1_data.get('name')} vs {p2_data.get('name')}")

        eval_func = sync_to_async(self._evaluator.evaluate_comparison)

        try:
            result = await eval_func(mission_title, p1_data, p2_data, rubric=rubric)
            logger.info(f"[EvalAgent] ✅ 평가 완료: {list(result.keys())}")
            return result
        except Exception as e:
            logger.error(f"[EvalAgent] ❌ 평가 실패: {e} → 폴백 반환")
            return self._evaluator._fallback_review(p1_data, p2_data)
