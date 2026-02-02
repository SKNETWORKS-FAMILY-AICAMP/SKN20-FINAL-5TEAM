"""
GPT-4.0 mini 호출 래퍼
OpenAI API를 사용한 LLM 호출 기능 제공
"""

import os
import json
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_gpt(prompt: str, model: str = "gpt-4o-mini") -> str:
    print(f"  [LLM] Calling {model}...")
    """
    GPT-4.0 mini 호출

    Args:
        prompt: 사용자 프롬프트
        model: 모델 이름 (기본값: gpt-4o-mini)

    Returns:
        str: LLM 응답 텍스트
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "너는 프로그래밍 학습 문제 출제 전문가다. Python과 PyTorch를 사용한 머신러닝 버그 문제를 만들어야 한다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


def call_gpt_json(prompt: str, model: str = "gpt-4o-mini") -> dict:
    """
    JSON 형식으로 응답 요청

    Args:
        prompt: 사용자 프롬프트 (JSON 형식 요청 포함)
        model: 모델 이름 (기본값: gpt-4o-mini)

    Returns:
        dict: 파싱된 JSON 응답

    Raises:
        json.JSONDecodeError: JSON 파싱 실패 시
    """
    response = call_gpt(prompt, model)

    # JSON 파싱
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Markdown 코드 블록 제거 시도
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
            return json.loads(json_str)
        elif "```" in response:
            # 일반 코드 블록
            json_str = response.split("```")[1].split("```")[0].strip()
            return json.loads(json_str)
        raise
