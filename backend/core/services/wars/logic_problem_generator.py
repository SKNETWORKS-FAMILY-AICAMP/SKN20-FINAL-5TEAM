"""
[생성일: 2026-03-04] LogicRun AI 문제 생성기
- Phase1: speedRounds (빈칸 채우기 5라운드)
- Phase2: designSprint (설계 체크리스트 5항목)
- openai AsyncOpenAI 직접 호출 (langchain 미사용)
"""
import os
import json
import asyncio
from openai import AsyncOpenAI

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

# ── 주제 풀 (랜덤 다양성 확보) ──────────────────────────
TOPIC_POOL = [
    "배열에서 중복 제거 후 정렬",
    "로그인 인증 및 세션 관리",
    "파일 업로드 및 용량 검증",
    "장바구니 총액 계산 및 할인 적용",
    "이진 탐색 알고리즘",
    "스택을 이용한 괄호 유효성 검사",
    "REST API 페이지네이션 처리",
    "비밀번호 해싱 및 검증",
    "캐시 만료 및 갱신 로직",
    "WebSocket 채팅 메시지 브로드캐스트",
    "데이터베이스 트랜잭션 롤백 처리",
    "이미지 리사이즈 및 썸네일 생성",
    "JWT 토큰 발급 및 검증",
    "큐를 이용한 작업 스케줄링",
    "재귀적 디렉토리 탐색",
    "CSV 파일 파싱 및 데이터 변환",
    "Rate Limiter 구현",
    "Observer 패턴으로 이벤트 처리",
    "LRU 캐시 구현",
    "병합 정렬 알고리즘",
]

SYSTEM_PROMPT = """너는 소프트웨어 엔지니어 교육용 의사코드 문제 생성기야.
주어진 주제로 **한국어 의사코드** 빈칸 채우기 문제를 만들어.

반드시 아래 JSON 포맷으로만 응답해. 다른 텍스트 없이 JSON만 출력해.

{
  "title": "문제 제목 (한국어, 영문 병기)",
  "scenario": "상황 설명 2~3문장",
  "speedRounds": [
    {
      "round": 1,
      "context": "1. 이 단계 설명",
      "codeLines": [
        { "text": "코드 한 줄", "type": "fixed" },
        { "text": "빈칸이 있는 줄 ________", "type": "blank", "answer": "정답", "options": ["정답", "오답1", "오답2", "오답3"] }
      ]
    }
  ],
  "designSprint": {
    "checklist": [
      { "id": "c1", "label": "체크 항목 설명", "patterns": ["매칭키워드1|매칭키워드2"] }
    ]
  }
}

규칙:
1. speedRounds는 정확히 5개 라운드
2. 각 라운드에 blank는 1~2개, fixed는 1~3개
3. blank의 options는 정확히 4개 (정답 포함, 순서 랜덤)
4. 답이 너무 뻔하면 안 됨 — 오답도 그럴듯하게 만들어 (예: "반복" 정답이면 오답에 "순회", "탐색", "매핑" 같은 유사 용어)
5. 의사코드는 한국어로 작성 (함수, 변수명 한국어)
6. 난이도: 초급~중급 개발자가 15초 안에 풀 수 있는 수준
7. designSprint.checklist는 정확히 5개 항목
8. checklist의 patterns는 정규식 OR(|) 패턴으로, 핵심 키워드 3~5개
9. 각 라운드 codeLines 합계: 2~4줄
10. ________는 빈칸 표시 (blank 타입에만)"""


async def generate_logic_quest(topic: str = None) -> dict:
    """LogicRun용 퀘스트 1개 생성"""
    import random
    if not topic:
        topic = random.choice(TOPIC_POOL)

    client = _get_client()

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.9,
            max_tokens=3000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"주제: {topic}"}
            ]
        )

        content = resp.choices[0].message.content.strip()

        # 마크다운 코드블록 제거
        if "```" in content:
            parts = content.split("```")
            for part in parts:
                stripped = part.strip()
                if stripped.startswith("json"):
                    stripped = stripped[4:].strip()
                if stripped.startswith("{"):
                    content = stripped
                    break

        quest = json.loads(content)

        # 검증
        if not _validate_quest(quest):
            print(f"⚠️ [LogicGen] Validation failed, using fallback")
            return _get_fallback_quest()

        # ID 부여
        quest["id"] = hash(topic) % 10000

        print(f"✅ [LogicGen] Generated quest: {quest['title']}")
        return quest

    except Exception as e:
        print(f"⚠️ [LogicGen] Generation failed: {e}")
        return _get_fallback_quest()


async def generate_logic_quests(count: int = 3) -> list:
    """여러 퀘스트 동시 생성"""
    import random
    topics = random.sample(TOPIC_POOL, min(count, len(TOPIC_POOL)))
    tasks = [generate_logic_quest(t) for t in topics]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    quests = []
    for r in results:
        if isinstance(r, dict) and "speedRounds" in r:
            quests.append(r)

    # 부족하면 폴백으로 채우기
    while len(quests) < count:
        quests.append(_get_fallback_quest())

    return quests[:count]


def _validate_quest(quest: dict) -> bool:
    """퀘스트 구조 검증"""
    try:
        if not quest.get("title") or not quest.get("scenario"):
            return False

        rounds = quest.get("speedRounds", [])
        if len(rounds) != 5:
            return False

        for r in rounds:
            if "codeLines" not in r:
                return False
            blanks = [l for l in r["codeLines"] if l.get("type") == "blank"]
            if len(blanks) == 0:
                return False
            for b in blanks:
                if len(b.get("options", [])) != 4:
                    return False
                if b.get("answer") not in b["options"]:
                    return False

        checklist = quest.get("designSprint", {}).get("checklist", [])
        if len(checklist) < 3:
            return False

        return True
    except Exception:
        return False


def _get_fallback_quest() -> dict:
    """폴백 퀘스트"""
    return {
        "id": 9999,
        "title": "해시맵 기반 빈도수 카운터 (Frequency Counter)",
        "scenario": "주어진 문자열 배열에서 각 단어의 등장 빈도를 해시맵(딕셔너리)으로 집계하고, 가장 많이 등장한 단어를 반환하는 로직을 작성하세요.",
        "speedRounds": [
            {
                "round": 1,
                "context": "1. 함수 선언 및 빈도 저장소 준비",
                "codeLines": [
                    {"text": "함수 최빈단어_찾기(단어_배열):", "type": "fixed"},
                    {"text": "  빈도맵 = ________", "type": "blank", "answer": "{}", "options": ["{}", "[]", "0", "None"]}
                ]
            },
            {
                "round": 2,
                "context": "2. 배열 순회하며 빈도 집계",
                "codeLines": [
                    {"text": "  각각 단어 in 단어_배열 ________:", "type": "blank", "answer": "반복", "options": ["반복", "조건", "예외", "대기"]},
                    {"text": "    만약 단어 in 빈도맵 이면:", "type": "fixed"},
                    {"text": "      빈도맵[단어] = 빈도맵[단어] + 1", "type": "fixed"}
                ]
            },
            {
                "round": 3,
                "context": "3. 새 단어 등록",
                "codeLines": [
                    {"text": "    ________:", "type": "blank", "answer": "아니면", "options": ["아니면", "만약", "시도", "종료"]},
                    {"text": "      빈도맵[단어] = ________", "type": "blank", "answer": "1", "options": ["1", "0", "단어", "참"]}
                ]
            },
            {
                "round": 4,
                "context": "4. 최대 빈도 단어 탐색",
                "codeLines": [
                    {"text": "  최대빈도 = 0", "type": "fixed"},
                    {"text": "  결과단어 = ''", "type": "fixed"},
                    {"text": "  각각 (키, 값) in 빈도맵.________ 반복:", "type": "blank", "answer": "항목들", "options": ["항목들", "키들", "값들", "길이"]}
                ]
            },
            {
                "round": 5,
                "context": "5. 비교 후 결과 반환",
                "codeLines": [
                    {"text": "    만약 값 ________ 최대빈도 이면:", "type": "blank", "answer": ">", "options": [">", "==", "<", "!="]},
                    {"text": "      최대빈도 = 값", "type": "fixed"},
                    {"text": "      결과단어 = 키", "type": "fixed"},
                    {"text": "  반환 결과단어", "type": "fixed"}
                ]
            }
        ],
        "designSprint": {
            "checklist": [
                {"id": "c1", "label": "해시맵(딕셔너리) 자료구조 초기화", "patterns": ["해시|딕셔너리|맵|{}|빈도"]},
                {"id": "c2", "label": "배열 전체를 순회하는 반복문", "patterns": ["반복|순회|each|for|루프"]},
                {"id": "c3", "label": "키 존재 여부에 따른 분기 처리", "patterns": ["만약|조건|존재|in|아니면|else"]},
                {"id": "c4", "label": "최대값 비교를 통한 결과 갱신", "patterns": ["최대|비교|>|갱신|크"]},
                {"id": "c5", "label": "최종 결과 반환", "patterns": ["반환|return|결과"]}
            ]
        }
    }
