"""gpt-4o-mini TTFT 이상치(381초) 재현 테스트 — 5회 반복"""
import os, sys, time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
except ImportError:
    pass

import openai

client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY', ''))

PROMPT = [{"role": "user", "content": "optimizer.zero_grad()가 없으면 어떤 일이 일어나나요?"}]

print("gpt-4o-mini TTFT 재현 테스트 (5회)")
print("-" * 40)

for i in range(5):
    t0 = time.time()
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=PROMPT,
        max_completion_tokens=100,
        temperature=0.6,
        stream=True,
    )
    ttft = None
    for chunk in stream:
        if ttft is None:
            ttft = time.time() - t0
        delta = chunk.choices[0].delta if chunk.choices else None
        # consume stream
    total = time.time() - t0
    print(f"  Run {i+1}: TTFT={ttft:.3f}s / Total={total:.3f}s")

print("-" * 40)
print("완료")
