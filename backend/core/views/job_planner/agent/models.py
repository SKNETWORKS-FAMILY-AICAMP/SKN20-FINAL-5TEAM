# agent/models.py
"""
데이터 모델
원본 v3.1 섹션 2.3 기반
"""
from dataclasses import dataclass

@dataclass
class JobPosting:
    source: str                  # "text" | "image" | "url" | "api"
    raw_text: str
    company_name: str
    position: str
    required_skills: list[str]
    preferred_skills: list[str]
    experience_range: str
    job_description: str
    tech_stack: list[str]
    domain: str
    deadline: str | None         # "2025-03-15" | "상시" | None
    deadline_days: int | None    # 자동 계산

@dataclass
class UserProfile:
    name: str
    current_role: str
    experience_years: int
    skills: list[str]
    skill_levels: dict[str, int]  # {"Python": 4} — 1~5
    education: str
    certifications: list[str]
    career_goals: str
    available_prep_days: int
