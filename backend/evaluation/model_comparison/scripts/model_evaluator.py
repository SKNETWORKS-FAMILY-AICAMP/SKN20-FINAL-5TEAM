"""
다중 모델 평가 지원 모듈

OpenAI와 Hugging Face 모델을 평가할 수 있는 통합 인터페이스 제공
"""
import os
import re
import json
import time
import requests
from openai import OpenAI
from django.conf import settings


class ModelEvaluator:
    """모델별 평가를 실행하는 기본 클래스"""

    def __init__(self, model_name):
        self.model_name = model_name
        self.total_cost = 0
        self.total_tokens = 0
        self.evaluation_times = []

    def evaluate(self, system_message, prompt):
        """평가 실행 (서브클래스에서 구현)"""
        raise NotImplementedError

    def get_stats(self):
        """통계 반환"""
        return {
            'model': self.model_name,
            'total_cost': self.total_cost,
            'total_tokens': self.total_tokens,
            'avg_time': sum(self.evaluation_times) / len(self.evaluation_times) if self.evaluation_times else 0,
            'total_evaluations': len(self.evaluation_times)
        }


class OpenAIEvaluator(ModelEvaluator):
    """OpenAI 모델 평가기"""

    # 모델별 가격 (1M 토큰당 USD)
    PRICING = {
        # GPT-4 계열
        'gpt-4o': {'input': 2.50, 'output': 10.00},
        'gpt-4o-mini': {'input': 0.150, 'output': 0.600},
        'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50},
        'gpt-4-turbo': {'input': 10.00, 'output': 30.00},

        # GPT-5 계열
        'gpt-5-nano': {'input': 0.05, 'output': 0.40},
        'gpt-5-mini': {'input': 0.25, 'output': 2.00},
        'gpt-5': {'input': 1.25, 'output': 10.00},
        'gpt-5.1': {'input': 1.25, 'output': 10.00},
        'gpt-5.2': {'input': 1.75, 'output': 14.00},
        'gpt-5-codex': {'input': 1.25, 'output': 10.00},
        'gpt-5.2-codex': {'input': 1.75, 'output': 14.00}
    }

    def __init__(self, model_name, api_key=None):
        super().__init__(model_name)
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)

    def evaluate(self, system_message, prompt):
        """OpenAI API를 사용한 평가"""
        start_time = time.time()

        try:
            # GPT-5 모델은 max_completion_tokens 사용, GPT-4 이하는 max_tokens 사용
            if self.model_name.startswith('gpt-5'):
                # GPT-5는 더 긴 reasoning이 필요하므로 8000 토큰 할당
                token_params = {'max_completion_tokens': 8000}
            else:
                token_params = {'max_tokens': 2500}

            # GPT-5-mini와 GPT-5는 temperature 기본값만 지원
            if self.model_name in ['gpt-5-mini', 'gpt-5']:
                temperature = 1  # 기본값
            else:
                temperature = 0.3

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                **token_params,
                temperature=temperature
            )

            elapsed_time = time.time() - start_time
            self.evaluation_times.append(elapsed_time)

            # 토큰 및 비용 계산
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            self.total_tokens += (input_tokens + output_tokens)

            if self.model_name in self.PRICING:
                pricing = self.PRICING[self.model_name]
                cost = (input_tokens * pricing['input'] / 1_000_000) + \
                       (output_tokens * pricing['output'] / 1_000_000)
                self.total_cost += cost

            response_text = response.choices[0].message.content.strip()

            # JSON 파싱
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group(0))
                return {
                    'success': True,
                    'result': result,
                    'tokens': {
                        'input': input_tokens,
                        'output': output_tokens,
                        'total': input_tokens + output_tokens
                    },
                    'cost': cost if self.model_name in self.PRICING else 0,
                    'time': elapsed_time
                }
            else:
                return {
                    'success': False,
                    'error': 'JSON parsing failed',
                    'raw_response': response_text,
                    'time': elapsed_time
                }

        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'time': elapsed_time
            }


class GeminiEvaluator(ModelEvaluator):
    """Google Gemini 모델 평가기"""

    PRICING = {
        'gemini-2.5-flash': {'input': 0, 'output': 0},  # 무료
        'gemini-2.5-pro': {'input': 1.25, 'output': 5.00},
        'gemini-2.0-flash-exp': {'input': 0, 'output': 0},  # 무료
        'gemini-2.0-flash': {'input': 0.075, 'output': 0.30},
        'gemini-1.5-flash': {'input': 0.075, 'output': 0.30},
        'gemini-1.5-pro': {'input': 1.25, 'output': 5.00}
    }

    def __init__(self, model_name, api_key=None):
        super().__init__(model_name)
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)
        except ImportError:
            raise ImportError("google-generativeai package not installed")

    def evaluate(self, system_message, prompt):
        """Gemini API를 사용한 평가"""
        start_time = time.time()

        try:
            full_prompt = f"{system_message}\n\n{prompt}"
            response = self.model.generate_content(full_prompt)

            elapsed_time = time.time() - start_time
            self.evaluation_times.append(elapsed_time)

            response_text = response.text.strip()

            # JSON 파싱
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group(0))

                # 비용 계산 (토큰 정보가 없으면 추정)
                cost = 0
                if self.model_name in self.PRICING:
                    pricing = self.PRICING[self.model_name]
                    # 추정: 입력 ~2000 tokens, 출력 ~500 tokens
                    cost = (2000 * pricing['input'] / 1_000_000) + (500 * pricing['output'] / 1_000_000)
                    self.total_cost += cost

                return {
                    'success': True,
                    'result': result,
                    'tokens': {'total': 'N/A'},
                    'cost': cost,
                    'time': elapsed_time
                }
            else:
                return {
                    'success': False,
                    'error': 'JSON parsing failed',
                    'raw_response': response_text[:500],
                    'time': elapsed_time
                }

        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'time': elapsed_time
            }


class GroqEvaluator(ModelEvaluator):
    """Groq 모델 평가기 (초고속 Llama)"""

    def __init__(self, model_name, api_key=None):
        super().__init__(model_name)
        self.api_key = api_key or os.getenv('GROQ_API_KEY')

        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            raise ImportError("groq package not installed")

    def evaluate(self, system_message, prompt):
        """Groq API를 사용한 평가"""
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.3
            )

            elapsed_time = time.time() - start_time
            self.evaluation_times.append(elapsed_time)

            response_text = response.choices[0].message.content.strip()

            # JSON 파싱
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group(0))
                return {
                    'success': True,
                    'result': result,
                    'tokens': {'total': 'N/A'},
                    'cost': 0,  # 무료
                    'time': elapsed_time
                }
            else:
                return {
                    'success': False,
                    'error': 'JSON parsing failed',
                    'raw_response': response_text[:500],
                    'time': elapsed_time
                }

        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'time': elapsed_time
            }


def get_evaluator(model_name):
    """모델 이름으로 적절한 Evaluator 반환"""

    # OpenAI 모델 (GPT-4, GPT-5)
    openai_models = [
        'gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-4-turbo',
        'gpt-5-nano', 'gpt-5-mini', 'gpt-5', 'gpt-5.1', 'gpt-5.2',
        'gpt-5-codex', 'gpt-5.2-codex'
    ]
    if model_name in openai_models:
        return OpenAIEvaluator(model_name)

    # Google Gemini 모델
    gemini_models = [
        'gemini-2.5-flash', 'gemini-2.5-pro',  # 최신
        'gemini-2.0-flash-exp', 'gemini-2.0-flash',
        'gemini-1.5-flash', 'gemini-1.5-pro'
    ]
    if model_name in gemini_models:
        return GeminiEvaluator(model_name)

    # Groq 모델 (Llama, Mixtral)
    groq_models = ['llama-3.3-70b-versatile', 'mixtral-8x7b-32768']
    if model_name in groq_models:
        return GroqEvaluator(model_name)


    raise ValueError(f"Unknown model: {model_name}")
