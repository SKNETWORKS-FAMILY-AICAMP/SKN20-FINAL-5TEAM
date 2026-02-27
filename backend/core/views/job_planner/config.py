# config.py
"""
전역 설정
원본 v3.1 섹션 4.1 기반
"""

# 임계값 (섹션 4.1)
SKILL_MATCH_THRESHOLD = 0.65  # MVP 기본값. 배포 전 실측으로 조정.

# 가중치 (섹션 4.2)
WEIGHT_REQUIRED_SKILLS = 0.6
WEIGHT_PREFERRED_SKILLS = 0.2
WEIGHT_EXPERIENCE = 0.2
