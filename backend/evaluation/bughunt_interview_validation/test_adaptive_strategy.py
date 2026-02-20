"""
적응형 질문 전략 테스트 — 전략 3(모르겠다), 전략 4(완전히 틀린 답변)
────────────────────────────────────────────────────────────
시나리오: S4 Step 1 (Gradient Bug - zero_grad 누락)
모델: gpt-5.2 (temperature=0.6)
프롬프트: ai_view.py _build_stream_prompt 동일
"""

import os, sys, json, time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
except ImportError:
    pass

import openai

client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY', ''))
MODEL = "gpt-5.2"

# ── S4 Step 1 컨텍스트 ──
BUGGY_CODE = """import torch
import torch.nn as nn
import torch.optim as optim

model = SimpleNet()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

for epoch in range(10):
    for batch_idx, (data, target) in enumerate(train_loader):
        output = model(data)
        loss = criterion(output, target)

        loss.backward()
        optimizer.step()

        print(f"Epoch {epoch}, Batch {batch_idx}: Loss = {loss.item():.4f}")"""

USER_CODE = BUGGY_CODE.replace(
    "        output = model(data)",
    "        optimizer.zero_grad()\n\n        output = model(data)"
)

RUBRIC = {
    "core_concepts": ["zero_grad() 누락", "gradient 누적"],
    "mechanism_concepts": ["backward()가 .grad에 += 연산", "배치마다 gradient가 커짐"],
    "application_concepts": ["표준 루프 순서: zero_grad → forward → backward → step", "의도적 gradient accumulation과의 차이"]
}


def build_stream_prompt(turn, candidate_name="지원자"):
    MAX_TURNS = 3
    remaining = MAX_TURNS - turn
    rubric_text = (
        f"핵심 개념 (core): {', '.join(RUBRIC['core_concepts'])}\n"
        f"메커니즘 개념 (mechanism): {', '.join(RUBRIC['mechanism_concepts'])}\n"
        f"응용 개념 (application): {', '.join(RUBRIC['application_concepts'])}"
    )
    return f"""너는 주니어 AI 엔지니어를 면접하는 기술 면접관이다. 한국어로 대화한다.
{candidate_name}님이 아래 코드의 버그를 수정했다. 수정 이유와 이해도를 파악하기 위해 질문한다.

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
{BUGGY_CODE}

[유저가 수정한 코드]
{USER_CODE}

[버그 정보]
타입: Gradient Accumulation Bug
설명: optimizer.zero_grad()가 누락되어 gradient가 매 배치마다 누적되고 있습니다.

[평가 기준 - 채점 루브릭]
{rubric_text}

[적응형 질문 전략 - 유저의 직전 답변을 기준으로 판단하라]

1) 답변이 정확하고 구체적인 경우:
   → "잘 이해하고 계시네요"를 짧게 인정한 뒤, 루브릭의 다음 단계 개념을 물어라.
   → 단, 반드시 루브릭 범위 안의 개념만 물어라.

2) 방향은 맞지만 부정확하거나 빠진 부분이 있는 경우:
   → 틀린 부분을 부드럽게 짚어라. (예: "~라고 하셨는데, 실제로는 조금 다릅니다. 그러면 ~는 어떤 식으로 동작할까요?")
   → 틀린 것을 그냥 넘어가지 마라. 교정이 최우선이다.

3) "모르겠다" 또는 매우 모호한 답변인 경우:
   → 난이도를 확 낮춰라. 같은 개념을 더 쉽게 다시 물어라.
   → 짧은 힌트를 제시하라. (예: "힌트를 드리자면, backward()를 호출할 때 .grad 값이 어떻게 변하는지 생각해보시면 됩니다. 혹시 아시나요?")
   → 절대로 같은 난이도나 더 어려운 질문을 내지 마라.

4) 완전히 방향이 틀린 경우:
   → 틀린 부분을 정중하게 알려주고, 올바른 방향의 단서를 준 뒤 더 쉬운 질문을 하라.

[규칙]
- 정답을 직접 알려주지 마라. 유도 질문만 하라.
- 질문은 1~2문장으로 짧고 명확하게 하라. 한 번에 여러 질문을 하지 마라.
- 반드시 존댓말을 사용하라.
- 유저를 부를 때는 반드시 "{candidate_name}님" 호칭을 사용하라.
- 내부 평가/분석 과정은 절대 노출하지 마라.
- 출력은 JSON이 아닌, 사용자에게 보여줄 "질문 문장만" 출력하라.
"""


# ── 테스트 케이스 정의 ──
TEST_CASES = [
    {
        "name": "전략 3: '모르겠다' 답변",
        "user_answer": "잘 모르겠어요. zero_grad를 추가하긴 했는데 왜 필요한지는 정확히 모르겠습니다.",
        "expected": ["힌트", "쉽", "간단", "생각해보", "예를 들", "혹시"],
        "turn": 1,
    },
    {
        "name": "전략 3: 매우 모호한 답변",
        "user_answer": "음... 뭔가 학습이 잘 안 돼서요? 그래서 넣었어요.",
        "expected": ["힌트", "쉽", "간단", "생각해보", "예를 들", "혹시", "구체적"],
        "turn": 1,
    },
    {
        "name": "전략 4: 완전히 틀린 답변",
        "user_answer": "zero_grad는 학습률을 0으로 초기화해서 모델이 처음부터 다시 학습하게 하는 함수입니다.",
        "expected": ["실제로는", "다릅니다", "아닙니다", "정확히는", "사실", "gradient", "기울기"],
        "turn": 1,
    },
    {
        "name": "전략 4: 전혀 관련 없는 답변",
        "user_answer": "zero_grad는 GPU 메모리를 비우는 함수라서 OOM 에러를 방지하려고 넣었습니다.",
        "expected": ["실제로는", "다릅니다", "아닙니다", "정확히는", "사실", "gradient", "기울기", "메모리"],
        "turn": 1,
    },
]

RUNS_PER_CASE = 2

print("=" * 70)
print("  적응형 질문 전략 테스트 (전략 3: 모르겠다 / 전략 4: 완전히 틀림)")
print(f"  모델: {MODEL} | 반복: {RUNS_PER_CASE}회/케이스")
print("=" * 70)

for tc in TEST_CASES:
    print(f"\n▶ {tc['name']}")
    print(f"  유저 답변: \"{tc['user_answer'][:60]}...\"")
    print("-" * 60)

    for run in range(1, RUNS_PER_CASE + 1):
        prompt = build_stream_prompt(tc["turn"])
        messages = [
            {"role": "system", "content": prompt},
            {"role": "assistant", "content": "방금 optimizer.zero_grad()를 추가하셨는데, 이 코드가 없으면 구체적으로 어떤 일이 일어나나요?"},
            {"role": "user", "content": tc["user_answer"]},
        ]

        try:
            t0 = time.time()
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.6,
                max_completion_tokens=300,
            )
            elapsed = time.time() - t0
            text = resp.choices[0].message.content.strip()

            # 기대 키워드 매칭 확인
            matched = [kw for kw in tc["expected"] if kw in text]
            has_question = "?" in text or "요?" in text or "까요" in text or "나요" in text

            # 난이도 판단 (힌트 제공 여부)
            has_hint = any(h in text for h in ["힌트", "생각해보", "예를 들", "드리자면"])
            has_correction = any(c in text for c in ["실제로는", "다릅니다", "아닙니다", "정확히는", "사실은"])

            print(f"\n  [Run {run}] ({elapsed:.2f}s)")
            print(f"  응답: {text}")
            print(f"  ─ 키워드 매칭: {matched}")
            print(f"  ─ 질문형 종결: {'✅' if has_question else '❌'}")
            print(f"  ─ 힌트 제공: {'✅' if has_hint else '➖'}")
            print(f"  ─ 오개념 교정: {'✅' if has_correction else '➖'}")

        except Exception as e:
            print(f"  [Run {run}] ❌ ERROR: {e}")

print("\n" + "=" * 70)
print("  테스트 완료")
print("=" * 70)
