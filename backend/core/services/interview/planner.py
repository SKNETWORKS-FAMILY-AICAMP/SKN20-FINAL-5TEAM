"""
planner.py — L3 Planner (정보 획득 전략가)
LLM 없음. 순수 Python rules로 동작한다.
missing evidence → Intent 결정 (frozenset lookup table)
"""

# Evidence → Intent 변환 규칙 (lookup table)
INTENT_MAP = {
    # Collaboration
    frozenset(["action"]): "행동 회상 유도",
    frozenset(["result"]): "결과 변화 확인",
    frozenset(["reflection"]): "배운 점 탐색",
    frozenset(["role"]): "책임 범위 확인",
    frozenset(["conflict"]): "상황 배경 확인",
    frozenset(["action", "result"]): "상황 전개 확인",
    frozenset(["role", "action"]): "역할과 행동 확인",
    frozenset(["role", "result"]): "역할과 결과 연결 확인",
    frozenset(["role", "action", "result"]): "경험 전체 구조 확인",
    # Problem Solving
    frozenset(["concept"]): "개념 이해 확인",
    frozenset(["application"]): "실제 적용 경험 확인",
    frozenset(["tradeoff"]): "기술적 판단 근거 확인",
    frozenset(["situation"]): "문제 상황 설명 요청",
    frozenset(["analysis"]): "문제 원인 분석 확인",
    frozenset(["approach"]): "해결 접근법 확인",
    frozenset(["situation", "analysis"]): "문제 상황과 원인 확인",
    frozenset(["analysis", "approach"]): "분석과 해결 전략 확인",
    # Motivation
    frozenset(["reason"]): "지원 동기 확인",
    frozenset(["alignment"]): "직무 적합성 확인",
    frozenset(["research"]): "회사 리서치 여부 확인",
    frozenset(["aspiration"]): "성장 방향 탐색",
    frozenset(["reason", "alignment"]): "지원 동기와 직무 적합성 확인",
    # Growth
    frozenset(["challenge"]): "도전 경험 확인",
    frozenset(["effort"]): "극복 노력 확인",
    frozenset(["change"]): "성장 변화 확인",
    frozenset(["challenge", "effort"]): "도전과 노력 확인",
}

# 반복 시 사용하는 변형 표현 suffix
VARIATION_SUFFIXES = [
    " (다른 각도에서)",
    " (구체적 사례로)",
    " (좀 더 상세히)",
]


def decide_intent(missing: list, question_history: list) -> dict:
    """
    missing required evidence 기반으로 질문 intent를 결정한다.
    LLM 없음. 순수 Python.

    Args:
        missing: 미확인 핵심 evidence 목록
        question_history: [{"slot": ..., "intent": ..., "turn": ...}, ...]

    Returns:
        {"missing": [...], "intent": "행동 회상 유도"}
    """
    if not missing:
        return {"missing": [], "intent": "구체적 설명 요청"}

    # lookup: missing[:2]로 키 생성
    key = frozenset(missing[:2])
    intent = INTENT_MAP.get(key)

    if not intent:
        # 단일 항목으로 재시도
        key_single = frozenset([missing[0]])
        intent = INTENT_MAP.get(key_single)

    if not intent:
        # 동적 키(technical_depth 한글 키 등) — 키 이름 자체로 intent 생성
        missing_str = " 및 ".join(k.replace("_", " ") for k in missing[:2])
        intent = f"{missing_str} 확인"

    # 반복 방지: 직전 3턴의 intent와 비교
    past_intents = [h.get("intent", "") for h in question_history[-3:]]
    if intent in past_intents:
        # 동일 intent가 반복되면 variation suffix 추가
        repeat_count = sum(1 for pi in past_intents if pi == intent)
        suffix_idx = min(repeat_count - 1, len(VARIATION_SUFFIXES) - 1)
        intent = intent + VARIATION_SUFFIXES[suffix_idx]

    return {"missing": missing, "intent": intent}
