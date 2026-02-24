"""AI Coach 프롬프트 - 가드레일 필터링"""

import re

# ─────────────────────────────────────────────
# 1. 가드레일: 규칙 기반 범위 밖 질문 필터링
# ─────────────────────────────────────────────

_LEARNING_KEYWORDS = {
    "성적", "점수", "약점", "강점", "공부", "학습", "추천", "문제", "풀이", "풀어",
    "디버깅", "의사코드", "아키텍처", "설계", "버그", "코드", "유닛",
    "리포트", "분석", "방법", "팁", "개선", "향상", "연습",
    "데이터", "모델", "머신러닝", "딥러닝", "파이프라인",
    "오버피팅", "과적합", "전처리", "피처", "하이퍼파라미터",
    "보안", "성능", "신뢰성", "스케일링", "캐싱",
    "자신감", "포기", "어렵", "힘들", "못하겠", "잘할",
    "알려", "도와", "코치", "시작", "수준", "실력",
    "unit", "score", "weak", "bug", "debug", "hunt",
    "정확도", "사고력", "안전성", "추상화", "일관성",
}

_OFF_TOPIC_KEYWORDS = {
    "날씨", "맛집", "영화", "노래", "게임하자", "연애",
    "주식", "비트코인", "로또", "운세", "축구", "야구",
    "요리", "레시피", "여행", "호텔", "드라마",
}

_ABUSIVE_KEYWORDS = {
    "바보", "멍청", "꺼져", "시발", "씨발", "병신", "지랄",
    "닥쳐", "ㅅㅂ", "ㅂㅅ", "ㅄ",
}

_NONSENSE_RE = re.compile(r"^[ㄱ-ㅎㅏ-ㅣ\s!?.,~ㅋㅎㅠㅜ]+$")

GUARDRAIL_MESSAGE = (
    "나는 이 플랫폼의 학습 데이터를 기반으로 코칭하는 전문 코치야!\n\n"
    "이런 질문을 해보면 어때?\n"
    "- **내 약점이 뭐야?**\n"
    "- **디버깅 공부는 어떻게 하면 좋아?**\n"
    "- **다음에 뭘 풀면 좋을까?**"
)


def is_off_topic(message):
    """명백한 범위 밖 질문을 LLM 호출 전 차단"""
    msg = message.strip()
    msg_lower = msg.lower()

    if _NONSENSE_RE.match(msg):
        return True
    if any(kw in msg_lower for kw in _ABUSIVE_KEYWORDS):
        return True
    if len(msg) <= 3 and not any(kw in msg_lower for kw in _LEARNING_KEYWORDS):
        return True
    if any(kw in msg_lower for kw in _OFF_TOPIC_KEYWORDS):
        if not any(kw in msg_lower for kw in _LEARNING_KEYWORDS):
            return True

    return False
