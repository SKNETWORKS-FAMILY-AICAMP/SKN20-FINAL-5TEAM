# llm/gateway.py
"""
LLM Gateway
원본 v3.1 기반
"""
from openai import OpenAI
import os
import json

class LLMGateway:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def call(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def call_json(self, prompt: str, model: str = "gpt-4o-mini") -> dict:
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
