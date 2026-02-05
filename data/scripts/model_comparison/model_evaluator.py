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
        'gpt-4o': {'input': 2.50, 'output': 10.00},
        'gpt-4o-mini': {'input': 0.150, 'output': 0.600},
        'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50},
        'gpt-4-turbo': {'input': 10.00, 'output': 30.00}
    }

    def __init__(self, model_name, api_key=None):
        super().__init__(model_name)
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)

    def evaluate(self, system_message, prompt):
        """OpenAI API를 사용한 평가"""
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


class HuggingFaceEvaluator(ModelEvaluator):
    """Hugging Face Inference API 평가기"""

    HF_MODELS = {
        'meta-llama/Llama-3.1-70B-Instruct': 'Llama-3.1-70B',
        'mistralai/Mixtral-8x7B-Instruct-v0.1': 'Mixtral-8x7B'
    }

    def __init__(self, model_id, hf_token=None):
        # Display name 설정
        display_name = self.HF_MODELS.get(model_id, model_id.split('/')[-1])
        super().__init__(display_name)

        self.model_id = model_id
        self.hf_token = hf_token or os.getenv('HF_TOKEN')
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"

    def evaluate(self, system_message, prompt):
        """Hugging Face Inference API를 사용한 평가"""
        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }

        # 메시지 포맷팅 (Llama/Mixtral 형식)
        full_prompt = f"""<|system|>
{system_message}
<|user|>
{prompt}
<|assistant|>
"""

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 2500,
                "temperature": 0.3,
                "top_p": 0.9,
                "return_full_text": False
            }
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120
            )

            elapsed_time = time.time() - start_time
            self.evaluation_times.append(elapsed_time)

            if response.status_code == 200:
                result_data = response.json()

                # 응답 형식 확인
                if isinstance(result_data, list) and len(result_data) > 0:
                    response_text = result_data[0].get('generated_text', '')
                elif isinstance(result_data, dict):
                    response_text = result_data.get('generated_text', '')
                else:
                    return {
                        'success': False,
                        'error': 'Unexpected response format',
                        'raw_response': result_data,
                        'time': elapsed_time
                    }

                # JSON 파싱
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    result = json.loads(json_match.group(0))
                    return {
                        'success': True,
                        'result': result,
                        'tokens': {'total': 'N/A'},  # HF API doesn't return token count
                        'cost': 0,  # Free tier
                        'time': elapsed_time
                    }
                else:
                    return {
                        'success': False,
                        'error': 'JSON parsing failed',
                        'raw_response': response_text[:500],
                        'time': elapsed_time
                    }

            elif response.status_code == 503:
                # Model is loading
                return {
                    'success': False,
                    'error': 'Model is loading, please retry in a few seconds',
                    'time': elapsed_time
                }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'details': response.text[:200],
                    'time': elapsed_time
                }

        except requests.Timeout:
            elapsed_time = time.time() - start_time
            return {
                'success': False,
                'error': 'Request timeout (120s)',
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

    # OpenAI 모델
    openai_models = ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-4-turbo']
    if model_name in openai_models:
        return OpenAIEvaluator(model_name)

    # Hugging Face 모델
    hf_model_map = {
        'Llama-3.1-70B': 'meta-llama/Llama-3.1-70B-Instruct',
        'Mixtral-8x7B': 'mistralai/Mixtral-8x7B-Instruct-v0.1'
    }

    if model_name in hf_model_map:
        return HuggingFaceEvaluator(hf_model_map[model_name])

    raise ValueError(f"Unknown model: {model_name}")
