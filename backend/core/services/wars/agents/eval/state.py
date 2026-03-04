"""
eval/state.py — EvalAgent LangGraph State

[노드 흐름]
  evaluate → self_critique → (재평가 필요?) → revise OR finalize

[State 필드 설명]
  - mission_title, p1_data, p2_data, rubric : 입력값 (불변)
  - raw_result      : evaluate 노드가 생성한 1차 평가
  - critique        : self_critique 노드가 생성한 자기비판
  - revised_result  : revise 노드가 생성한 수정 평가
  - final_result    : finalize 노드가 확정한 최종 결과
  - retry_count     : 재평가 횟수 (무한루프 방지용, 최대 2회)
  - needs_revision  : self_critique 결과 판단 (True면 revise로 분기)
"""

from __future__ import annotations
from typing import TypedDict, Optional, Dict, Any


class EvalAgentState(TypedDict):
    # ── 입력 (불변) ──────────────────────────────
    mission_title: str
    p1_data: Dict[str, Any]
    p2_data: Dict[str, Any]
    rubric: Optional[Dict[str, Any]]

    # ── 중간 상태 ────────────────────────────────
    raw_result: Optional[Dict[str, Any]]       # 1차 평가 결과
    critique: Optional[str]                    # 자기비판 텍스트
    needs_revision: bool                       # 재평가 필요 여부
    retry_count: int                           # 재평가 시도 횟수

    # ── 최종 출력 ────────────────────────────────
    revised_result: Optional[Dict[str, Any]]   # 수정된 평가
    final_result: Optional[Dict[str, Any]]     # 확정 결과
