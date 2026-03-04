"""
bug_problem_generator.py — BugBubble 문제 동적 생성 서비스

openai 직접 호출 → JSON 파싱 → 검증 → 반환
사용처: socket_server.py > bubble_start 이벤트
"""

import json
import os
import random
import logging
from typing import List, Dict, Any

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

_client: AsyncOpenAI = None

def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


PROMPT_TEMPLATE = """당신은 AI 부트캠프의 실무 디버깅 문제 출제자입니다.
주니어 AI 개발자가 실무에서 맞닥뜨리는 버그 상황을 {count}개 만들어주세요.

## 난이도
{difficulty_desc}

## 카테고리 (골고루 섞어서)
- Python 기초: TypeError, IndexError, KeyError 등
- 데이터 분석: pandas, numpy 관련 에러
- 모델 학습: PyTorch/sklearn shape 불일치, NaN 등
- API/서버: Django, FastAPI 엔드포인트, JSON 파싱 에러
- 배포/환경: import 실패, 경로, 환경변수 누락

## 출력 형식 (JSON 배열, 마크다운 없이 순수 JSON만)
[
  {{
    "title": "한줄 제목 (한국어)",
    "bug_type_name": "에러이름 (예: TypeError)",
    "file_name": "파일명.py",
    "bug_line": 버그줄번호(정수),
    "buggy_code": "버그 포함 코드 (5~10줄, \\n으로 줄구분)",
    "error_log": "에러 로그 (File, Line 포함)",
    "hint": "디버깅 힌트 (1문장)",
    "choices": [
      {{"label": "수정 코드 한 줄", "correct": true}},
      {{"label": "그럴듯한 오답", "correct": false}},
      {{"label": "그럴듯한 오답", "correct": false}},
      {{"label": "그럴듯한 오답", "correct": false}}
    ]
  }}
]

## 규칙
1. choices 정확히 4개, correct=true 반드시 1개만
2. 오답은 그럴듯하지만 다른 에러를 유발하거나 해결 못하는 코드
3. buggy_code는 실제로 해당 에러가 발생하는 코드
4. 시나리오가 "주니어 AI 개발자 업무" 느낌
5. 같은 에러 타입 반복 금지"""

DIFFICULTY_DESC = {
    1: "기초 — Python 문법, 타입 에러 (부트캠프 1개월차)",
    2: "중급 — 라이브러리 에러, 데이터 처리 (부트캠프 3개월차)",
    3: "실무 — 모델 학습, API 연동, 배포 (실무 투입 직전)",
}

FALLBACK_PROBLEMS = [
    {
        "title": "서버 응답 점수 합산 에러", "bug_type_name": "TypeError",
        "file_name": "score_api.py", "bug_line": 4,
        "buggy_code": 'import json\nresponse = \'{"score": "100", "bonus": 50}\'\ndata = json.loads(response)\ntotal = data["score"] + data["bonus"]\nprint(total)',
        "error_log": 'TypeError: can only concatenate str (not "int") to str\nFile "score_api.py", line 4',
        "hint": "JSON에서 파싱한 score의 타입을 확인해보세요.",
        "choices": [
            {"label": 'total = int(data["score"]) + data["bonus"]', "correct": True},
            {"label": 'total = data["score"] + str(data["bonus"])', "correct": False},
            {"label": 'total = str(data["score"] + data["bonus"])', "correct": False},
            {"label": 'total = data["score"].add(data["bonus"])', "correct": False},
        ],
    },
    {
        "title": "리스트 마지막 원소 접근 실패", "bug_type_name": "IndexError",
        "file_name": "data_loader.py", "bug_line": 2,
        "buggy_code": 'batch = ["img1.png", "img2.png", "img3.png"]\nlast = batch[3]\nprint(f"마지막 배치: {last}")',
        "error_log": 'IndexError: list index out of range\nFile "data_loader.py", line 2',
        "hint": "리스트 인덱스는 0부터 시작합니다.",
        "choices": [
            {"label": "last = batch[2]", "correct": True},
            {"label": "last = batch[4]", "correct": False},
            {"label": "last = batch.last()", "correct": False},
            {"label": "last = batch[-0]", "correct": False},
        ],
    },
    {
        "title": "딕셔너리 키 누락 처리", "bug_type_name": "KeyError",
        "file_name": "config.py", "bug_line": 3,
        "buggy_code": 'config = {"host": "localhost", "port": 8080}\nhost = config["host"]\ndb = config["database"]',
        "error_log": "KeyError: 'database'\nFile \"config.py\", line 3",
        "hint": "존재하지 않는 키에 안전하게 접근하는 방법은?",
        "choices": [
            {"label": 'db = config.get("database", "default_db")', "correct": True},
            {"label": 'db = config["db"]', "correct": False},
            {"label": "db = config.database", "correct": False},
            {"label": 'db = config or "default_db"', "correct": False},
        ],
    },
    {
        "title": "None 반환값 속성 접근", "bug_type_name": "AttributeError",
        "file_name": "user_service.py", "bug_line": 7,
        "buggy_code": 'def find_user(users, name):\n    for u in users:\n        if u["name"] == name:\n            return u\n\nresult = find_user([], "Alice")\nprint(result["email"])',
        "error_log": "TypeError: 'NoneType' object is not subscriptable\nFile \"user_service.py\", line 7",
        "hint": "함수가 아무것도 못 찾으면 무엇을 반환하나요?",
        "choices": [
            {"label": 'if result: print(result["email"])', "correct": True},
            {"label": "print(result.email)", "correct": False},
            {"label": 'print(str(result["email"]))', "correct": False},
            {"label": "result = find_user([], 'Alice') or []", "correct": False},
        ],
    },
    {
        "title": "무한 루프 탈출 실패", "bug_type_name": "LogicError",
        "file_name": "trainer.py", "bug_line": 4,
        "buggy_code": 'epoch = 0\nmax_epochs = 5\nwhile epoch < max_epochs:\n    print(f"Epoch {epoch}")\n    epoch = epoch',
        "error_log": "Program hangs (infinite loop)\nLine 5: epoch never increments",
        "hint": "epoch 값이 루프 안에서 변하고 있나요?",
        "choices": [
            {"label": "epoch = epoch + 1", "correct": True},
            {"label": "epoch = epoch - 1", "correct": False},
            {"label": "epoch == epoch + 1", "correct": False},
            {"label": "break", "correct": False},
        ],
    },
]


def _validate_problem(p: Dict[str, Any]) -> bool:
    for field in ["title", "bug_type_name", "buggy_code", "choices", "bug_line"]:
        if not p.get(field):
            return False
    choices = p.get("choices", [])
    if len(choices) != 4:
        return False
    if sum(1 for c in choices if c.get("correct")) != 1:
        return False
    if any(not c.get("label") for c in choices):
        return False
    lines = p.get("buggy_code", "").split("\n")
    if p["bug_line"] < 1 or p["bug_line"] > len(lines):
        return False
    return True


def _clean_problem(p: Dict[str, Any], step: int) -> Dict[str, Any]:
    p["fix_mode"] = "choice"
    p["step"] = step
    if not p.get("file_name"):
        p["file_name"] = "debug_me.py"
    if not p.get("error_log"):
        p["error_log"] = f'{p.get("bug_type_name", "Error")}: see line {p.get("bug_line", "?")}'
    if not p.get("hint"):
        p["hint"] = "에러 로그를 자세히 읽어보세요."
    random.shuffle(p["choices"])
    return p


async def generate_bug_problems(count: int = 10, difficulty: int = 1) -> List[Dict[str, Any]]:
    difficulty_desc = DIFFICULTY_DESC.get(difficulty, DIFFICULTY_DESC[1])
    prompt = PROMPT_TEMPLATE.format(count=count, difficulty_desc=difficulty_desc)
    problems = []

    try:
        client = _get_client()
        response = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0.85, max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()

        raw = json.loads(content)
        if not isinstance(raw, list):
            raw = [raw]

        logger.info(f"[BugGen] GPT가 {len(raw)}개 문제 생성")
        step = 1
        for p in raw:
            if _validate_problem(p):
                problems.append(_clean_problem(p, step))
                step += 1

    except json.JSONDecodeError as e:
        logger.error(f"[BugGen] JSON 파싱 실패: {e}")
    except Exception as e:
        logger.error(f"[BugGen] GPT 호출 실패: {e}")

    if len(problems) < 5:
        fallback = [_clean_problem(dict(p), len(problems) + i + 1)
                    for i, p in enumerate(FALLBACK_PROBLEMS)]
        random.shuffle(fallback)
        problems.extend(fallback[:max(0, 5 - len(problems))])

    random.shuffle(problems)
    return problems
