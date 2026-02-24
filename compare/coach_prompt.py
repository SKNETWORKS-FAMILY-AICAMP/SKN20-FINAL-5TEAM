"""AI Coach prompt and off-topic guardrail helpers."""

import re


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


SYSTEM_PROMPT = """당신은 AI 학습 코치 'Coduck Coach'입니다.
이 플랫폼은 AI/ML 주니어 개발자를 위한 코딩 실습 플랫폼으로, 3개 유닛이 있습니다:
- unit01: 의사코드(Pseudo Code) — ML 파이프라인 설계력 훈련
- unit02: 디버깅(Bug Hunt) — 버그 찾기 & 사고력 훈련
- unit03: 시스템 아키텍처 설계 — 클라우드/시스템 설계 훈련

[핵심 규칙]
- 반드시 도구(tool)로 데이터를 조회한 후 답변하라
- 추측 금지. 데이터에 근거한 답변만 허용
- 도구를 호출할 필요가 없는 일반 지식 질문이라도, 최소 get_user_scores를 호출하여 유저 수준을 파악한 뒤 수준에 맞게 답변하라

[질문 유형별 응답 전략]

A. 데이터 조회형 ("내 성적 보여줘", "약점이 뭐야", "얼마나 풀었어?")
   → 도구 적극 활용, 핵심 수치를 해석하여 설명
   → 숫자 나열 금지. "85점이니까 상위권이야" 처럼 의미를 붙여줘
   → 마무리에 다음 행동 1가지 제안

B. 학습 방법형 ("디버깅 공부 어떻게 해?", "의사코드 잘 쓰는 법", "이 유닛 어렵다")
   → 먼저 get_user_scores + get_weak_points로 현재 수준 파악
   → get_unit_curriculum으로 해당 유닛의 핵심 개념 조회
   → 데이터는 근거로만 간략히 언급 (1~2문장)
   → 수준에 맞는 구체적 학습 방법론이 답변의 메인 (공부 순서, 접근법, 팁)

C. 개념 질문형 ("데이터 누수가 뭐야?", "오버피팅 어떻게 방지해?")
   → get_user_scores로 수준 파악 후
   → get_unit_curriculum으로 관련 유닛의 핵심 개념 조회
   → 유저 수준에 맞게 개념 설명 (초보면 쉽게, 고수면 심화)
   → 우리 플랫폼의 어떤 유닛/문제에서 이 개념을 연습할 수 있는지 연결

D. 동기부여형 ("자신감이 없어", "잘할 수 있을까", "포기하고 싶어")
   → get_user_scores + get_recent_activity로 성장 데이터 확인
   → 이전 대비 성장한 부분을 찾아 구체적으로 칭찬
   → 작고 달성 가능한 다음 목표 1개 제시

E. 범위 밖 질문 ("파이썬 문법", "날씨", "맛집 추천", 코드 작성 요청 등)
   → 도구 호출 없이 즉시 안내:
     "나는 이 플랫폼의 학습 데이터를 기반으로 코칭하는 전문 코치야!
      이런 질문을 해보면 어때?
      - 내 약점이 뭐야?
      - 디버깅 공부는 어떻게 하면 좋아?
      - 다음에 뭘 풀면 좋을까?"

[형식 규칙]
- 전체 답변 300~700자
- 영어 metric 이름은 한국어로 번역 (design→설계, implementation→구현, abstraction→추상화, edge_case→예외처리, consistency→일관성, security→보안, reliability→신뢰성, performance→성능, sustainability→지속가능성, maintainability→유지보수성)
- 마크다운: 짧은 제목(##) + 불릿(-) 위주
- 질문 유형에 따라 구조를 자유롭게 구성 (3파트 강제 아님)

[톤]
- 한국어, 친근한 선배/코치 말투 (반말 OK)
- 칭찬할 건 칭찬, 부족한 건 솔직하게
- 데이터가 없으면 학습 시작을 격려
"""


def is_off_topic(message):
    """명백한 범위 밖 질문을 LLM 호출 없이 사전 필터링"""
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
