"""
GPT-5.2 temperature 실제 적용 여부 확인 테스트
─────────────────────────────────────────────
테스트 1: temperature 파라미터가 에러 없이 수락되는지
테스트 2: temperature=0.6 vs 1.0 출력 다양성 비교 (각 5회)
테스트 3: reasoning_effort="none" 명시 시 차이 확인
"""

import os, sys, json, time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
except ImportError:
    pass

import openai

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY not found")
    sys.exit(1)

client = openai.OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-5.2"
RUNS = 5

# 짧고 단순한 프롬프트 (다양성 측정이 쉽도록)
PROMPT = "PyTorch에서 optimizer.zero_grad()의 역할을 한 문장으로 설명하세요."

def call_model(temp, reasoning_effort=None):
    """모델 호출. 성공 시 (응답텍스트, 시간) 반환, 실패 시 (에러메시지, 0) 반환"""
    kwargs = {
        "model": MODEL,
        "messages": [{"role": "user", "content": PROMPT}],
        "max_completion_tokens": 100,
        "temperature": temp,
    }
    if reasoning_effort is not None:
        kwargs["reasoning"] = {"effort": reasoning_effort}

    try:
        t0 = time.time()
        resp = client.chat.completions.create(**kwargs)
        elapsed = time.time() - t0
        text = resp.choices[0].message.content.strip()
        return text, elapsed
    except Exception as e:
        return f"ERROR: {e}", 0


def jaccard_similarity(s1, s2):
    """두 문자열의 단어 단위 자카드 유사도"""
    w1 = set(s1.split())
    w2 = set(s2.split())
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)


def avg_pairwise_similarity(texts):
    """텍스트 리스트의 평균 쌍별 유사도"""
    n = len(texts)
    if n < 2:
        return 0.0
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += jaccard_similarity(texts[i], texts[j])
            count += 1
    return total / count


print("=" * 70)
print(f"  GPT-5.2 temperature 적용 여부 테스트")
print(f"  모델: {MODEL} | 반복: {RUNS}회 | SDK: openai {openai.__version__}")
print("=" * 70)

# ──────────────────────────────────────────
# 테스트 1: temperature 파라미터 수락 여부
# ──────────────────────────────────────────
print("\n▶ 테스트 1: temperature 파라미터 수락 여부")
print("-" * 50)

for temp in [0.0, 0.6, 1.0]:
    text, elapsed = call_model(temp)
    is_error = text.startswith("ERROR:")
    status = "❌ 거부" if is_error else "✅ 수락"
    print(f"  temperature={temp}: {status} ({elapsed:.2f}s)")
    if is_error:
        print(f"    → {text}")

# ──────────────────────────────────────────
# 테스트 2: temperature=0.6 vs 1.0 다양성 비교
# ──────────────────────────────────────────
print(f"\n▶ 테스트 2: 출력 다양성 비교 (각 {RUNS}회)")
print("-" * 50)

results = {}

for temp in [0.6, 1.0]:
    print(f"\n  [temperature={temp}]")
    texts = []
    for i in range(RUNS):
        text, elapsed = call_model(temp)
        if text.startswith("ERROR:"):
            print(f"    Run {i+1}: ❌ {text}")
            continue
        texts.append(text)
        # 앞 40자만 표시
        preview = text[:60].replace('\n', ' ')
        print(f"    Run {i+1} ({elapsed:.2f}s): {preview}...")

    results[temp] = texts

# 유사도 분석
print(f"\n▶ 유사도 분석")
print("-" * 50)

for temp, texts in results.items():
    if len(texts) < 2:
        print(f"  temperature={temp}: 데이터 부족 (수집 {len(texts)}건)")
        continue

    sim = avg_pairwise_similarity(texts)
    # 고유 응답 수
    unique = len(set(texts))
    # 평균 길이
    avg_len = sum(len(t) for t in texts) / len(texts)

    print(f"  temperature={temp}:")
    print(f"    평균 쌍별 유사도: {sim:.4f} (1.0=동일, 0.0=완전상이)")
    print(f"    고유 응답 수: {unique}/{len(texts)}")
    print(f"    평균 응답 길이: {avg_len:.0f}자")

# 판정
if 0.6 in results and 1.0 in results:
    sim_06 = avg_pairwise_similarity(results[0.6])
    sim_10 = avg_pairwise_similarity(results[1.0])

    print(f"\n▶ 판정")
    print("-" * 50)
    print(f"  temperature=0.6 유사도: {sim_06:.4f}")
    print(f"  temperature=1.0 유사도: {sim_10:.4f}")
    diff = sim_06 - sim_10

    if diff > 0.05:
        print(f"  차이: +{diff:.4f}")
        print(f"  → ✅ temperature가 실제 적용됨 (0.6이 더 일관적)")
    elif diff < -0.05:
        print(f"  차이: {diff:.4f}")
        print(f"  → ⚠️ 역전 현상 (1.0이 더 일관적) — 샘플 부족 가능")
    else:
        print(f"  차이: {diff:+.4f} (거의 없음)")
        print(f"  → ❌ temperature가 무시되고 있을 가능성 높음")

# ──────────────────────────────────────────
# 테스트 3: reasoning_effort="none" 명시 시
# ──────────────────────────────────────────
print(f"\n▶ 테스트 3: reasoning_effort='none' 명시 + temperature")
print("-" * 50)

for effort in ["none", "low", "medium"]:
    text, elapsed = call_model(0.6, reasoning_effort=effort)
    is_error = text.startswith("ERROR:")
    status = "❌ 거부" if is_error else "✅ 수락"
    print(f"  reasoning_effort='{effort}' + temp=0.6: {status} ({elapsed:.2f}s)")
    if is_error:
        print(f"    → {text[:120]}")

print("\n" + "=" * 70)
print("  테스트 완료")
print("=" * 70)
