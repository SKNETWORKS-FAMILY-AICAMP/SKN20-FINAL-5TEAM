"""
BugHunt 면접관 LLM 모델 비교 테스트 (v2)
──────────────────────────────────────
대상 모델: gpt-4o-mini, gpt-5.2, gemini-2.5-flash
시나리오 : S4 Step 1 (Gradient Bug - optimizer.zero_grad 누락)
조건     : 프롬프트 고정, 유저 답변 고정, 3회 반복
"""

import os, sys, json, time, re, statistics
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
except ImportError:
    pass

import openai
import google.generativeai as genai

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

# ═══════════════════════════════════════════════
# 1. 테스트 시나리오 (S4 Step 1 - Gradient Bug)
# ═══════════════════════════════════════════════
STEP_CONTEXT = {
    "buggy_code": (
        "import torch\nimport torch.nn as nn\nimport torch.optim as optim\n\n"
        "model = SimpleNet()\ncriterion = nn.CrossEntropyLoss()\n"
        "optimizer = optim.Adam(model.parameters(), lr=0.001)\n\n"
        "for epoch in range(10):\n"
        "    for batch_idx, (data, target) in enumerate(train_loader):\n"
        "        output = model(data)\n"
        "        loss = criterion(output, target)\n\n"
        "        loss.backward()\n"
        "        optimizer.step()\n\n"
        "        print(f\"Epoch {epoch}, Batch {batch_idx}: Loss = {loss.item():.4f}\")"
    ),
    "user_code": (
        "import torch\nimport torch.nn as nn\nimport torch.optim as optim\n\n"
        "model = SimpleNet()\ncriterion = nn.CrossEntropyLoss()\n"
        "optimizer = optim.Adam(model.parameters(), lr=0.001)\n\n"
        "for epoch in range(10):\n"
        "    for batch_idx, (data, target) in enumerate(train_loader):\n"
        "        optimizer.zero_grad()\n\n"
        "        output = model(data)\n"
        "        loss = criterion(output, target)\n\n"
        "        loss.backward()\n"
        "        optimizer.step()\n\n"
        "        print(f\"Epoch {epoch}, Batch {batch_idx}: Loss = {loss.item():.4f}\")"
    ),
    "error_info": {
        "type": "Gradient Accumulation Bug",
        "description": "optimizer.zero_grad()가 누락되어 gradient가 매 배치마다 누적되고 있습니다."
    },
    "interview_rubric": {
        "core_concepts": ["zero_grad() 누락", "gradient 누적"],
        "mechanism_concepts": ["backward()가 .grad에 += 연산", "배치마다 gradient가 커짐"],
        "application_concepts": [
            "표준 루프 순서: zero_grad → forward → backward → step",
            "의도적 gradient accumulation과의 차이"
        ],
        "first_question": "방금 optimizer.zero_grad()를 추가하셨는데, 이 코드가 없으면 구체적으로 어떤 일이 일어나나요?"
    }
}

# 고정 유저 답변 (3턴 + 최종 평가 재전송)
USER_ANSWERS = [
    "zero_grad가 없으면 gradient가 초기화 안돼서 이전 배치의 gradient가 계속 쌓이는 걸로 알고 있습니다. 그래서 loss가 점점 커지는 것 같아요.",
    "backward를 호출하면 각 파라미터의 .grad에 새로운 gradient가 더해지는데, zero_grad가 없으면 이전 값 위에 계속 += 되니까 gradient 값이 기하급수적으로 커지는 거죠.",
    "표준 루프 순서는 zero_grad, forward, backward, step 순서로 하는 게 맞고, 만약 의도적으로 gradient를 누적하고 싶으면 n배치마다 한번씩 zero_grad를 호출하는 gradient accumulation 기법을 쓸 수 있습니다."
]

MAX_TURNS = 3
DISPLAY_NAME = "지원자"

# 턴별 기대 키워드 (질문 품질 평가용)
TURN_KEYWORDS = {
    1: ["zero_grad", "gradient", "초기화", "누적", "원인"],
    2: ["backward", ".grad", "+=", "내부", "동작", "메커니즘"],
    3: ["순서", "zero_grad.*forward.*backward.*step", "accumulation", "실무", "디버깅"],
}

# 비용 추정 (USD per 1M tokens, 2026-02 기준 추정)
COST_PER_1M = {
    "gpt-4o-mini":       {"input": 0.15,  "output": 0.60},
    "gpt-5.2":           {"input": 2.50,  "output": 10.00},
    "gemini-2.5-flash":  {"input": 0.15,  "output": 0.60},
}


# ═══════════════════════════════════════════════
# 2. 프롬프트 빌더 (ai_view.py와 100% 동일)
# ═══════════════════════════════════════════════
def _rubric_text():
    r = STEP_CONTEXT['interview_rubric']
    return (
        f"핵심 개념 (core): {', '.join(r['core_concepts'])}\n"
        f"메커니즘 개념 (mechanism): {', '.join(r['mechanism_concepts'])}\n"
        f"응용 개념 (application): {', '.join(r['application_concepts'])}"
    )

def build_stream_prompt(turn):
    ei = STEP_CONTEXT['error_info']
    remaining = MAX_TURNS - turn
    return f"""너는 주니어 AI 엔지니어를 면접하는 기술 면접관이다. 한국어로 대화한다.
{DISPLAY_NAME}님이 아래 코드의 버그를 수정했다. 수정 이유와 이해도를 파악하기 위해 질문한다.

[대상 수준 - 매우 중요]
상대방은 AI/ML을 배우고 있는 주니어 엔지니어다.
- 물어봐도 되는 것: 개념의 "왜", 내부 동작 원리, 코드 동작 순서, 해당 버그와 직접 관련된 내용
- 절대 물어보면 안 되는 것: gradient accumulation 구현, loss scaling, learning rate scheduling 전략, 분산 학습, 커스텀 옵티마이저 등 시니어 레벨 주제
- 루브릭에 있는 개념 범위 안에서만 질문하라. 루브릭에 없는 심화 주제로 넘어가지 마라.

[현재 진행 상황]
현재 {turn}/{MAX_TURNS}턴 (남은 질문 기회: {remaining}회)

턴별 질문 방향:
- 1턴 (첫 답변 후): core 개념을 정확히 이해했는지 확인. 틀린 부분이 있으면 반드시 짚어라.
- 2턴: mechanism 개념으로 넘어가라. "내부적으로 어떤 일이 일어나는지" 물어라.
- 3턴 (마지막): application 개념을 물어라. 단, 주니어 수준의 실무 (디버깅 방법, 확인 방법) 한정.

[버그 코드]
{STEP_CONTEXT['buggy_code']}

[유저가 수정한 코드]
{STEP_CONTEXT['user_code']}

[버그 정보]
타입: {ei['type']}
설명: {ei['description']}

[평가 기준 - 채점 루브릭]
{_rubric_text()}

[적응형 질문 전략 - 유저의 직전 답변을 기준으로 판단하라]

1) 답변이 정확하고 구체적인 경우:
   → "잘 이해하고 계시네요"를 짧게 인정한 뒤, 루브릭의 다음 단계 개념을 물어라.

2) 방향은 맞지만 부정확하거나 빠진 부분이 있는 경우:
   → 틀린 부분을 부드럽게 짚어라.

3) "모르겠다" 또는 매우 모호한 답변인 경우:
   → 난이도를 확 낮춰라.

4) 완전히 방향이 틀린 경우:
   → 틀린 부분을 정중하게 알려주고, 올바른 방향의 단서를 준 뒤 더 쉬운 질문을 하라.

[규칙]
- 정답을 직접 알려주지 마라. 유도 질문만 하라.
- 질문은 1~2문장으로 짧고 명확하게 하라.
- 반드시 존댓말을 사용하라.
- 유저를 부를 때는 반드시 "{DISPLAY_NAME}님" 호칭을 사용하라.
- 출력은 JSON이 아닌, 사용자에게 보여줄 "질문 문장만" 출력하라.
"""


def build_eval_prompt():
    ei = STEP_CONTEXT['error_info']
    return f"""너는 주니어 AI 엔지니어 기술 면접관이다. 한국어로 대화한다.
{DISPLAY_NAME}님이 아래 코드의 버그를 수정했고, 지금까지 대화를 나눴다.
이번이 마지막 턴이다. {DISPLAY_NAME}님의 마지막 답변을 평가하고 종합 평가를 JSON으로 반환하라.

[버그 코드]
{STEP_CONTEXT['buggy_code']}

[유저가 수정한 코드]
{STEP_CONTEXT['user_code']}

[버그 정보]
타입: {ei['type']}
설명: {ei['description']}

[평가 기준 - 채점 루브릭]
{_rubric_text()}

[채점 방법 - 주니어 엔지니어 기준으로 관대하게 채점하라]
대화 전체를 종합해서 채점하라 (마지막 답변만이 아님).
피드백 문장에서는 반드시 "{DISPLAY_NAME}님" 호칭을 사용하라.

1) core (40점 만점):
   - 핵심 원인을 자기 말로 설명했으면 30~40점
   - 방향은 맞지만 부정확하면 15~25점
   - 전혀 모르면 0~10점

2) mechanism (35점 만점):
   - 내부 동작을 구체적으로 설명했으면 25~35점
   - 개념은 알지만 설명이 모호하면 10~20점
   - 언급 없으면 0~5점

3) application (25점 만점):
   - 실무 적용 방법을 1가지라도 구체적으로 제시하면 15~25점
   - 추상적으로만 언급하면 5~12점
   - 언급 없으면 0점

[understanding_level 기준]
- 90점 이상: "Excellent"
- 70~89점: "Good"
- 40~69점: "Surface"
- 39점 이하: "Poor"

반드시 아래 JSON 형식으로만 응답하라:
{{
  "type": "evaluation",
  "message": "2~3문장의 종합 피드백",
  "score": 0에서 100 사이 정수,
  "understanding_level": "Excellent|Good|Surface|Poor",
  "matched_concepts": ["유저가 보여준 개념들"],
  "weak_point": "부족한 부분 (없으면 null)"
}}"""


# ═══════════════════════════════════════════════
# 3. 질문 품질 자동 평가
# ═══════════════════════════════════════════════
def evaluate_question_quality(text, turn):
    """질문 텍스트의 품질을 0~100으로 평가"""
    score = 0
    details = {}

    # (1) 존댓말 사용 여부 (20점)
    honorific_patterns = ["나요", "까요", "세요", "습니다", "시겠", "드리"]
    honorific_count = sum(1 for p in honorific_patterns if p in text)
    honorific_score = min(20, honorific_count * 7)
    score += honorific_score
    details["존댓말"] = f"{honorific_score}/20"

    # (2) 호칭 사용 (10점)
    has_name = DISPLAY_NAME in text
    name_score = 10 if has_name else 0
    score += name_score
    details["호칭"] = f"{name_score}/10"

    # (3) 질문 길이 적정성 (15점) — 50~300자가 적정
    length = len(text)
    if 30 <= length <= 400:
        len_score = 15
    elif 15 <= length <= 600:
        len_score = 10
    else:
        len_score = 5
    score += len_score
    details["길이"] = f"{len_score}/15 ({length}자)"

    # (4) 턴별 키워드 부합도 (30점)
    keywords = TURN_KEYWORDS.get(turn, [])
    if keywords:
        matched = sum(1 for k in keywords if re.search(k, text, re.IGNORECASE))
        kw_score = min(30, int(matched / len(keywords) * 30))
    else:
        kw_score = 15  # 키워드 없으면 중간값
    score += kw_score
    details["주제부합"] = f"{kw_score}/30"

    # (5) 한국어 비율 (15점)
    korean_chars = len(re.findall(r'[가-힣]', text))
    kr_ratio = korean_chars / max(len(text), 1)
    kr_score = 15 if kr_ratio > 0.3 else (10 if kr_ratio > 0.15 else 5)
    score += kr_score
    details["한국어"] = f"{kr_score}/15 ({kr_ratio:.0%})"

    # (6) 질문형 종결 (10점) — ?로 끝나는지
    has_question = "?" in text or "요?" in text
    q_score = 10 if has_question else 3
    score += q_score
    details["질문형"] = f"{q_score}/10"

    return score, details


def validate_eval_json(parsed):
    """최종 평가 JSON 스키마 검증"""
    required = ["type", "message", "score", "understanding_level", "matched_concepts", "weak_point"]
    valid_levels = ["Excellent", "Good", "Surface", "Poor"]
    issues = []

    for key in required:
        if key not in parsed:
            issues.append(f"missing: {key}")

    if "score" in parsed:
        s = parsed["score"]
        if not isinstance(s, (int, float)) or s < 0 or s > 100:
            issues.append(f"score out of range: {s}")

    if "understanding_level" in parsed:
        lvl = parsed["understanding_level"]
        if lvl not in valid_levels:
            issues.append(f"invalid level: {lvl}")

    if "matched_concepts" in parsed:
        if not isinstance(parsed["matched_concepts"], list):
            issues.append("matched_concepts not array")

    if "message" in parsed:
        msg = parsed["message"]
        if DISPLAY_NAME not in msg:
            issues.append("호칭 미사용")

    return len(issues) == 0, issues


# ═══════════════════════════════════════════════
# 4. OpenAI 모델 테스트
# ═══════════════════════════════════════════════
def test_openai_model(model_name, num_runs=3):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    results = {"model": model_name, "question_turns": [], "eval_turns": [], "errors": []}
    first_q = STEP_CONTEXT['interview_rubric']['first_question']

    for run in range(num_runs):
        print(f"  [Run {run+1}/{num_runs}]", end=" ", flush=True)
        conversation = []

        # ── 질문 턴 1~3 (스트리밍) ──
        for turn in range(1, MAX_TURNS + 1):
            if turn == 1:
                conversation.append({"role": "assistant", "content": first_q})
            conversation.append({"role": "user", "content": USER_ANSWERS[turn - 1]})

            messages = [{"role": "system", "content": build_stream_prompt(turn)}] + conversation

            try:
                t0 = time.time()
                stream = client.chat.completions.create(
                    model=model_name, messages=messages,
                    temperature=0.6, max_completion_tokens=400, stream=True,
                )
                ttft = None
                full_text = ""
                token_count = 0
                for chunk in stream:
                    if ttft is None:
                        ttft = time.time() - t0
                    delta = chunk.choices[0].delta if chunk.choices else None
                    tok = getattr(delta, "content", None) or ""
                    full_text += tok
                    if tok:
                        token_count += 1
                total_time = time.time() - t0

                conversation.append({"role": "assistant", "content": full_text})
                q_score, q_details = evaluate_question_quality(full_text, turn)

                results["question_turns"].append({
                    "run": run+1, "turn": turn,
                    "ttft": round(ttft, 3) if ttft else None,
                    "total_time": round(total_time, 3),
                    "response_length": len(full_text),
                    "token_count": token_count,
                    "quality_score": q_score,
                    "quality_details": q_details,
                    "response_text": full_text,
                })
                print(f"T{turn}✓({q_score}점)", end=" ", flush=True)

            except Exception as e:
                results["errors"].append({"run": run+1, "turn": turn, "type": "question", "error": str(e)})
                print(f"T{turn}✗", end=" ", flush=True)
                conversation.append({"role": "assistant", "content": "(error)"})

        # ── 최종 평가 턴 (비스트리밍, JSON) ──
        conversation.append({"role": "user", "content": USER_ANSWERS[-1]})
        messages = [{"role": "system", "content": build_eval_prompt()}] + conversation

        try:
            t0 = time.time()
            response = client.chat.completions.create(
                model=model_name, messages=messages,
                temperature=0.6, max_completion_tokens=800,
                response_format={"type": "json_object"},
            )
            eval_time = time.time() - t0
            raw = response.choices[0].message.content
            parsed = json.loads(raw)
            schema_ok, schema_issues = validate_eval_json(parsed)

            results["eval_turns"].append({
                "run": run+1,
                "time": round(eval_time, 3),
                "json_valid": True,
                "schema_valid": schema_ok,
                "schema_issues": schema_issues,
                "score": parsed.get("score"),
                "understanding_level": parsed.get("understanding_level"),
                "matched_concepts": parsed.get("matched_concepts", []),
                "weak_point": parsed.get("weak_point"),
                "message": parsed.get("message", ""),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                },
            })
            print(f"Eval✓(score={parsed.get('score')})", flush=True)

        except json.JSONDecodeError:
            results["eval_turns"].append({
                "run": run+1, "time": round(time.time()-t0, 3),
                "json_valid": False, "schema_valid": False, "score": None,
                "raw_preview": (raw[:300] if 'raw' in dir() else "N/A"),
            })
            results["errors"].append({"run": run+1, "type": "eval_json", "error": "JSON parse failed"})
            print("Eval✗(JSON)", flush=True)
        except Exception as e:
            results["errors"].append({"run": run+1, "type": "eval", "error": str(e)})
            print(f"Eval✗({str(e)[:40]})", flush=True)

    return results


# ═══════════════════════════════════════════════
# 5. Gemini 모델 테스트
# ═══════════════════════════════════════════════
def test_gemini_model(model_name="gemini-2.5-flash", num_runs=3):
    genai.configure(api_key=GOOGLE_API_KEY)
    results = {"model": model_name, "question_turns": [], "eval_turns": [], "errors": []}
    first_q = STEP_CONTEXT['interview_rubric']['first_question']

    for run in range(num_runs):
        print(f"  [Run {run+1}/{num_runs}]", end=" ", flush=True)
        conversation = []

        for turn in range(1, MAX_TURNS + 1):
            if turn == 1:
                conversation.append({"role": "model", "parts": [first_q]})
            conversation.append({"role": "user", "parts": [USER_ANSWERS[turn - 1]]})

            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=build_stream_prompt(turn),
                generation_config=genai.types.GenerationConfig(temperature=0.6, max_output_tokens=400),
            )

            try:
                t0 = time.time()
                response = model.generate_content(conversation, stream=True)
                ttft = None
                full_text = ""
                token_count = 0
                for chunk in response:
                    if ttft is None:
                        ttft = time.time() - t0
                    txt = chunk.text if hasattr(chunk, 'text') else ""
                    full_text += txt
                    if txt:
                        token_count += 1
                total_time = time.time() - t0

                conversation.append({"role": "model", "parts": [full_text]})
                q_score, q_details = evaluate_question_quality(full_text, turn)

                results["question_turns"].append({
                    "run": run+1, "turn": turn,
                    "ttft": round(ttft, 3) if ttft else None,
                    "total_time": round(total_time, 3),
                    "response_length": len(full_text),
                    "token_count": token_count,
                    "quality_score": q_score,
                    "quality_details": q_details,
                    "response_text": full_text,
                })
                print(f"T{turn}✓({q_score}점)", end=" ", flush=True)

            except Exception as e:
                results["errors"].append({"run": run+1, "turn": turn, "type": "question", "error": str(e)})
                print(f"T{turn}✗", end=" ", flush=True)
                conversation.append({"role": "model", "parts": ["(error)"]})

        # ── 최종 평가 턴 ──
        conversation.append({"role": "user", "parts": [USER_ANSWERS[-1]]})
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=build_eval_prompt(),
            generation_config=genai.types.GenerationConfig(
                temperature=0.6, max_output_tokens=800,
                response_mime_type="application/json",
            ),
        )

        try:
            t0 = time.time()
            response = model.generate_content(conversation)
            eval_time = time.time() - t0
            raw = response.text
            parsed = json.loads(raw)
            schema_ok, schema_issues = validate_eval_json(parsed)

            usage_meta = response.usage_metadata
            results["eval_turns"].append({
                "run": run+1,
                "time": round(eval_time, 3),
                "json_valid": True,
                "schema_valid": schema_ok,
                "schema_issues": schema_issues,
                "score": parsed.get("score"),
                "understanding_level": parsed.get("understanding_level"),
                "matched_concepts": parsed.get("matched_concepts", []),
                "weak_point": parsed.get("weak_point"),
                "message": parsed.get("message", ""),
                "usage": {
                    "prompt_tokens": getattr(usage_meta, 'prompt_token_count', 0),
                    "completion_tokens": getattr(usage_meta, 'candidates_token_count', 0),
                },
            })
            print(f"Eval✓(score={parsed.get('score')})", flush=True)

        except json.JSONDecodeError:
            results["eval_turns"].append({
                "run": run+1, "time": round(time.time()-t0, 3),
                "json_valid": False, "schema_valid": False, "score": None,
                "raw_preview": (raw[:300] if 'raw' in dir() else "N/A"),
            })
            results["errors"].append({"run": run+1, "type": "eval_json", "error": "JSON parse failed"})
            print("Eval✗(JSON)", flush=True)
        except Exception as e:
            results["errors"].append({"run": run+1, "type": "eval", "error": str(e)})
            print(f"Eval✗({str(e)[:50]})", flush=True)

    return results


# ═══════════════════════════════════════════════
# 6. 결과 분석 리포트
# ═══════════════════════════════════════════════
def safe_stdev(values):
    return statistics.stdev(values) if len(values) >= 2 else 0.0

def analyze_results(all_results):
    separator = "=" * 80
    print(f"\n{separator}")
    print("  BugHunt 면접관 LLM 모델 비교 테스트 결과 리포트")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(separator)

    summaries = []  # 종합표용

    for res in all_results:
        model = res["model"]
        q_turns = res["question_turns"]
        e_turns = res["eval_turns"]
        errors = res["errors"]

        print(f"\n{'━' * 80}")
        print(f"  ■ 모델: {model}")
        print(f"{'━' * 80}")

        summary = {"model": model}

        # ── A. 질문 턴 성능 ──
        if q_turns:
            ttfts = [t["ttft"] for t in q_turns if t.get("ttft")]
            totals = [t["total_time"] for t in q_turns]
            lengths = [t["response_length"] for t in q_turns]
            q_scores = [t["quality_score"] for t in q_turns]

            print(f"\n  [A. 질문 턴 성능] (총 {len(q_turns)}회 = {len(q_turns)//3}runs × 3turns)")
            print(f"    ┌{'─'*50}")
            print(f"    │ TTFT (첫 토큰)  : 평균 {sum(ttfts)/len(ttfts):.3f}s  (min {min(ttfts):.3f}s / max {max(ttfts):.3f}s)")
            print(f"    │ 총 응답 시간    : 평균 {sum(totals)/len(totals):.3f}s  (min {min(totals):.3f}s / max {max(totals):.3f}s)")
            print(f"    │ 응답 길이       : 평균 {sum(lengths)//len(lengths)}자  (min {min(lengths)}자 / max {max(lengths)}자)")
            print(f"    │ 질문 품질 점수  : 평균 {sum(q_scores)/len(q_scores):.1f}/100  (stdev {safe_stdev(q_scores):.1f})")
            print(f"    └{'─'*50}")

            summary["avg_ttft"] = round(sum(ttfts)/len(ttfts), 3)
            summary["avg_q_time"] = round(sum(totals)/len(totals), 3)
            summary["avg_q_quality"] = round(sum(q_scores)/len(q_scores), 1)

            # 턴별 샘플 (Run 1)
            print(f"\n  [B. 질문 샘플 (Run 1)]")
            for t in q_turns:
                if t["run"] == 1:
                    text = t["response_text"].replace("\n", " ").strip()
                    print(f"    Turn {t['turn']} (품질:{t['quality_score']}점): {text[:200]}")
                    for k, v in t["quality_details"].items():
                        print(f"      {k}: {v}", end="  ")
                    print()

        # ── C. 최종 평가 성능 ──
        if e_turns:
            scores = [t["score"] for t in e_turns if t.get("score") is not None]
            times = [t["time"] for t in e_turns]
            json_ok = sum(1 for t in e_turns if t.get("json_valid"))
            schema_ok = sum(1 for t in e_turns if t.get("schema_valid"))

            print(f"\n  [C. 최종 평가 성능] ({len(e_turns)}회)")
            print(f"    ┌{'─'*55}")
            print(f"    │ JSON 파싱 성공   : {json_ok}/{len(e_turns)} ({json_ok/len(e_turns)*100:.0f}%)")
            print(f"    │ 스키마 완전 준수  : {schema_ok}/{len(e_turns)} ({schema_ok/len(e_turns)*100:.0f}%)")
            if scores:
                avg = sum(scores)/len(scores)
                sd = safe_stdev(scores)
                print(f"    │ 점수 평균       : {avg:.1f}점")
                print(f"    │ 점수 범위       : {min(scores)} ~ {max(scores)} (편차 {max(scores)-min(scores)}점)")
                print(f"    │ 점수 표준편차   : {sd:.2f}")
                levels = [t.get("understanding_level", "?") for t in e_turns]
                print(f"    │ 이해도 등급     : {levels}")
                summary["avg_score"] = round(avg, 1)
                summary["score_stdev"] = round(sd, 2)
                summary["score_range"] = f"{min(scores)}~{max(scores)}"
            print(f"    │ 응답 시간 평균   : {sum(times)/len(times):.3f}s")
            print(f"    └{'─'*55}")

            summary["json_rate"] = f"{json_ok}/{len(e_turns)}"
            summary["schema_rate"] = f"{schema_ok}/{len(e_turns)}"
            summary["avg_eval_time"] = round(sum(times)/len(times), 3)

            # 상세 평가 결과
            print(f"\n  [D. 평가 상세 (Run별)]")
            total_prompt = 0
            total_completion = 0
            for t in e_turns:
                print(f"    Run {t['run']}: score={t.get('score')} | level={t.get('understanding_level')} "
                      f"| json={t.get('json_valid')} | schema={t.get('schema_valid')}")
                if t.get("schema_issues"):
                    print(f"      ⚠ 스키마 이슈: {t['schema_issues']}")
                if t.get("matched_concepts"):
                    print(f"      매칭 개념: {t['matched_concepts']}")
                if t.get("weak_point"):
                    print(f"      약점: {t['weak_point']}")
                if t.get("message"):
                    print(f"      피드백: {t['message'][:150]}")
                if t.get("usage"):
                    u = t["usage"]
                    total_prompt += u.get("prompt_tokens", 0)
                    total_completion += u.get("completion_tokens", 0)
                    print(f"      토큰: prompt={u.get('prompt_tokens',0)} / completion={u.get('completion_tokens',0)}")

            # 비용 추정
            cost_info = COST_PER_1M.get(model, {})
            if cost_info and total_prompt > 0:
                est_cost = (total_prompt * cost_info["input"] + total_completion * cost_info["output"]) / 1_000_000
                per_session = est_cost / len(e_turns)
                print(f"\n    💰 비용 추정 (평가 턴만): 총 ${est_cost:.6f} / 세션당 ${per_session:.6f}")
                summary["est_cost_per_session"] = f"${per_session:.6f}"

        # 에러 요약
        if errors:
            print(f"\n  [E. 에러] {len(errors)}건")
            for e in errors:
                print(f"    Run {e.get('run')}: [{e.get('type')}] {e.get('error','')[:80]}")
        summary["error_count"] = len(errors)

        summaries.append(summary)

    # ═══ 종합 비교표 ═══
    print(f"\n{'━' * 80}")
    print("  ■ 종합 비교표")
    print(f"{'━' * 80}")

    col_w = 24
    header = f"  {'항목':<22}"
    for s in summaries:
        header += f"│ {s['model']:<{col_w}}"
    print(header)
    print("  " + "─" * (22 + (col_w + 2) * len(summaries)))

    rows = [
        ("평균 TTFT (스트리밍)", "avg_ttft", "s"),
        ("평균 질문 응답시간", "avg_q_time", "s"),
        ("평균 평가 응답시간", "avg_eval_time", "s"),
        ("질문 품질 점수", "avg_q_quality", "/100"),
        ("JSON 파싱 성공률", "json_rate", ""),
        ("스키마 완전 준수", "schema_rate", ""),
        ("평균 점수", "avg_score", "점"),
        ("점수 표준편차", "score_stdev", ""),
        ("점수 범위", "score_range", ""),
        ("추정 비용/세션", "est_cost_per_session", ""),
        ("에러 건수", "error_count", "건"),
    ]

    for label, key, unit in rows:
        row = f"  {label:<22}"
        for s in summaries:
            val = s.get(key, "N/A")
            if val != "N/A" and unit:
                val = f"{val}{unit}"
            row += f"│ {str(val):<{col_w}}"
        print(row)

    print()


# ═══════════════════════════════════════════════
# 7. 메인
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    NUM_RUNS = 3

    print("=" * 80)
    print("  BugHunt 면접관 LLM 모델 비교 테스트 v2")
    print(f"  날짜: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  시나리오: S4 Step 1 (Gradient Bug - zero_grad 누락)")
    print(f"  반복: {NUM_RUNS}회/모델 | 프롬프트: 고정 | 유저 답변: 고정")
    print(f"  평가 항목: TTFT, 응답시간, 질문품질, JSON준수, 채점일관성, 비용")
    print("=" * 80)

    all_results = []

    print(f"\n▶ [1/3] gpt-4o-mini 테스트...")
    all_results.append(test_openai_model("gpt-4o-mini", NUM_RUNS))

    print(f"\n▶ [2/3] gpt-5.2 테스트...")
    all_results.append(test_openai_model("gpt-5.2", NUM_RUNS))

    print(f"\n▶ [3/3] gemini-2.5-flash 테스트...")
    all_results.append(test_gemini_model("gemini-2.5-flash", NUM_RUNS))

    analyze_results(all_results)

    # JSON 저장
    output_path = Path(__file__).parent / "model_comparison_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"📁 상세 결과 저장: {output_path}")
