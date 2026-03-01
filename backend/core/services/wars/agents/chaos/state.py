"""
chaos/state.py — ChaosAgent LangGraph State

[노드 흐름]
  analyze_vulnerability → generate_event → self_validate → finalize
                                                  ↑              │ needs_regen & retry < 2
                                                  └── regenerate ←┘

[State 필드]
  입력:
    - mission_title    : 현재 미션 제목
    - deployed_nodes   : 양쪽 플레이어 합산 배치 컴포넌트 목록
    - round_num        : 현재 라운드 번호
    - past_event_ids   : 이번 게임에서 이미 발동된 이벤트 ID 목록 (중복 방지)

  중간:
    - vulnerability    : analyze_vulnerability가 찾은 핵심 취약점
                         {"component": "db", "reason": "단일 장애점", "severity_suggestion": "CRITICAL"}
    - raw_event        : generate_event가 만든 1차 이벤트
    - validation       : self_validate 결과 ("PASS" or "REGEN: <이유>")
    - needs_regen      : 재생성 필요 여부
    - retry_count      : 재생성 횟수 (최대 2회)

  출력:
    - final_event      : 확정된 장애 이벤트 {event_id, title, description, severity, target_components, hint}
"""

from __future__ import annotations
from typing import TypedDict, Optional, List, Dict, Any


class ChaosAgentState(TypedDict):
    # ── 입력 ────────────────────────────────────
    mission_title: str
    deployed_nodes: List[str]
    round_num: int
    past_event_ids: List[str]          # 중복 이벤트 방지

    # ── 중간 ────────────────────────────────────
    vulnerability: Optional[Dict[str, Any]]   # 취약점 분석 결과
    raw_event: Optional[Dict[str, Any]]        # 1차 생성 이벤트
    validation: Optional[str]                  # PASS or REGEN: <이유>
    needs_regen: bool
    retry_count: int

    # ── 출력 ────────────────────────────────────
    final_event: Optional[Dict[str, Any]]
