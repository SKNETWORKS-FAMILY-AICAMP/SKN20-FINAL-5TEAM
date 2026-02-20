# agent/state.py
"""
에이전트 상태 관리
원본 v3.1 섹션 6 기반
"""
from dataclasses import dataclass

@dataclass
class State:
    skill_gap_score: float
    readiness_score: float
    readiness_band: str
    deadline: str | None
    deadline_days: int | None
    time_pressure: str             # "없음"|"여유"|"보통"|"촉박"|"긴급"
    missing_skills: list[str]
    matched_skills: list[str]
    skill_priorities: list[dict]
    current_skills: list[str]
    current_levels: dict[str, int]
    loop_count: int
    action_history: list[dict]
    needs_replan: bool
    replan_reason: str | None

def compute_time_pressure(days: int | None) -> str:
    if days is None: return "없음"
    if days > 30: return "여유"
    if days > 14: return "보통"
    if days > 5: return "촉박"
    return "긴급"

# 섹션 7: 행동 공간
from enum import Enum

class ActionType(Enum):
    APPLY_NOW = "apply_now"
    LEARN_SKILL = "learn_skill"
    CURATE_LEARNING_PATH = "curate_learning_path"
    SEARCH_JOBS = "search_jobs"
    PIVOT_ROLE = "pivot_role"
    WAIT_AND_PREPARE = "wait_and_prepare"
    ASK_USER = "ask_user"

@dataclass
class Action:
    type: ActionType
    params: dict
    reasoning: str
    alternatives_rejected: list[dict]
    requires_confirmation: bool = False

@dataclass
class Observation:
    message: str = ""
    triggers_replan: bool = False
    user_skill_update: dict | None = None
