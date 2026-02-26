"""
constants.py — 면접 서비스 공통 상수 정의
"""

EVIDENCE_LABELS = {
    "role": "역할",
    "action": "행동",
    "result": "결과",
    "conflict": "갈등 상황",
    "reflection": "배운 점",
    "concept": "개념 이해",
    "application": "실제 적용",
    "tradeoff": "기술적 트레이드오프",
    "situation": "상황",
    "analysis": "원인 분석",
    "approach": "해결 접근법",
    "learning": "배운 점",
    "reason": "지원 이유",
    "research": "회사 리서치",
    "alignment": "직무 적합성",
    "aspiration": "성장 방향",
    "challenge": "도전 경험",
    "effort": "노력",
    "change": "변화",
}

# 슬롯별 기본 required evidence (technical_depth는 plan_generator가 동적 결정)
SLOT_REQUIRED = {
    "collaboration": ["role", "action", "result"],
    "problem_solving": ["situation", "analysis", "approach"],
    "motivation": ["reason", "alignment"],
    "growth": ["challenge", "effort", "change"],
}
