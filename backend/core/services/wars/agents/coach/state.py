"""
coach/state.py — CoachAgent LangGraph State

[노드 흐름]
  analyze_situation → decide_strategy → generate_hint → (충분한가?) → done OR escalate

[State 필드 설명]
  입력:
    - mission_required  : 이번 미션 필수 컴포넌트 목록
    - deployed_nodes    : 플레이어가 현재 배치한 컴포넌트
    - arrow_count       : 현재 화살표 수
    - hint_history      : 이전에 이미 줬던 힌트 목록 (중복 방지)

  중간:
    - situation         : analyze_situation 노드가 판단한 상황 분류
                          ("empty" | "missing_critical" | "missing_optional" |
                           "no_arrows" | "stuck_same" | "complete")
    - strategy          : decide_strategy 노드가 선택한 코칭 전략
                          ("direct" | "socratic" | "escalate" | "skip")

  출력:
    - hint              : 최종 힌트 딕셔너리 {message, missing_components, type, level}
    - done              : 루프 종료 여부
"""

from __future__ import annotations
from typing import TypedDict, Optional, List, Dict, Any


class CoachAgentState(TypedDict):
    # ── 입력 (불변) ──────────────────────────────
    mission_required: List[str]
    deployed_nodes: List[str]
    arrow_count: int
    node_count: int
    hint_history: List[Dict[str, Any]]   # [{type, message, level}, ...]

    # ── 중간 판단 ────────────────────────────────
    situation: Optional[str]             # 현재 상황 분류
    strategy: Optional[str]             # 코칭 전략

    # ── 출력 ────────────────────────────────────
    hint: Optional[Dict[str, Any]]       # 최종 힌트
    done: bool                           # 루프 종료
