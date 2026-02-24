"""
coach.py — Coach (구조적 피드백 생성기)
LLM 없음. evidence_map을 읽어 Python 템플릿으로 구조적 피드백 메시지를 생성한다.
Coach는 질적 판단을 하지 않는다. "확인된 것"과 "아직 확인되지 않은 것"만 알려준다.

절대 금지:
- "잘 하셨습니다" → 금지 (LLM 판단 흉내)
- "부족합니다" → 금지 (부정적 평가)
- 오직 구조적 사실만 전달
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


def generate_feedback(slot: str, evidence_map: dict, required: list = None) -> str:
    """
    evidence_map 기반으로 구조적 피드백 메시지를 생성한다.
    LLM 없음. 순수 Python 템플릿.

    Args:
        slot: 역량 슬롯명
        evidence_map: {evidence_key: bool, ...}
        required: 핵심 evidence 목록 (None이면 SLOT_REQUIRED에서 가져옴)

    Returns:
        피드백 문자열 (confirmed 없으면 빈 문자열)
    """
    if required is None:
        required = SLOT_REQUIRED.get(slot, list(evidence_map.keys()))

    confirmed = [k for k in required if evidence_map.get(k)]
    missing = [k for k in required if not evidence_map.get(k)]

    # 아직 아무것도 확인되지 않았으면 피드백 없음 (첫 답변 후 표시 안 함)
    if not confirmed:
        return ""

    confirmed_labels = [_get_label(k) for k in confirmed]
    missing_labels = [_get_label(k) for k in missing]

    confirmed_str = "·".join(confirmed_labels)

    if not missing:
        return f"{confirmed_str}까지 잘 전달해주셨습니다."

    missing_str = "와 ".join(missing_labels)
    return f"{confirmed_str}은 확인됐습니다. {missing_str}도 조금 더 말씀해주시겠어요?"


def _get_label(key: str) -> str:
    """evidence 키를 한글 레이블로 변환. 동적 키(한글)는 그대로 사용."""
    if key in EVIDENCE_LABELS:
        return EVIDENCE_LABELS[key]
    # 동적으로 생성된 technical_depth evidence 키는 한글 그대로 사용
    # 예: "asyncio_개념" → "asyncio 개념"
    return key.replace("_", " ")
