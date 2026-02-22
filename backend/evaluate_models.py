import os
import time
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenAI 클라이언트 초기화 (환경 변수 또는 직접 입력)
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("❌ 환경 변수 'OPENAI_API_KEY'가 설정되지 않았습니다.")
    exit(1)

client = OpenAI(api_key=api_key)

# 테스트할 모델 목록
# 참고: o1-preview, o1-mini 등은 OpenAI의 최신 추론(Reasoning) 특화 모델로 소위 'GPT-5급' 지능을 가집니다.
# 단, o1 계열 모델은 현재 streaming 파라미터 제약이 있거나 시스템 프롬프트 지원 방식이 다를 수 있어
# 일반적인 ChatCompletion 스트리밍 테스트에는 gpt-4o 계열을 우선 사용하고,
# o1 계열은 지원 여부에 따라 별도 처리가 필요할 수 있습니다.
MODELS_TO_TEST = [
    "gpt-4o-mini",       # 현재 저희가 쓰는 초고속/가성비 모델
    "gpt-4o",            # 높은 지능과 준수한 속도를 가진 플래그십 모델
    "gpt-5-mini",           # GPT-5급 추론 모델 (심층 사고, 경량)
    "gpt-5.2",        # GPT-5급 추론 모델 (최고 수준 지능)
]

# 테스트용 더미 프롬프트 (가혹한 조건)
SYSTEM_PROMPT = """당신은 수석 기술 면접관 '도덕'입니다. 
단 한 개의 꼬리 질문만 예리하게 생략 없이 던지세요.
[지원자 과거 코드]: 파이썬으로 BFS 탐색 알고리즘을 짰으나, 방문 처리(visited) 로직이 완전 누락되어 무한 루프 위험이 있음.
[지원 회사 요건]: 대규모 트래픽 처리 경험과 메모리 최적화 역량.

위 코드를 바탕으로 면접 질문을 만드세요."""

USER_PROMPT = "지원자가 방금 입장했습니다. 가볍게 인사하고 즉시 과거 코드의 약점을 지적하는 질문을 던지세요."

def run_benchmark():
    print("=" * 60)
    print("🚀 실시간 음성 면접 타당성 모델 벤치마크 테스트 🚀")
    print("=" * 60)
    print("측정 지표:")
    print("1. TTFT (Time To First Token): 첫 번째 단어가 나오기까지 걸린 시간 (가장 중요!)")
    print("2. Total Time: 전체 답변이 완성되기까지 걸린 시간")
    print("3. Response Quality: 반환된 실제 텍스트 내용\n")

    for model_name in MODELS_TO_TEST:
        print(f"▶ 테스트 시작: [{model_name}]")
        try:
            start_time = time.time()
            first_token_time = None
            full_response = ""

            is_o1 = model_name.startswith("o1") or model_name.startswith("gpt-5")

            # o1/gpt-5 계열 모델은 system prompt 대신 user를 사용해야 하며, temperature 파라미터를 지원하지 않습니다.
            # 또한 공식적으로 실시간 streaming 성능 측정 지표가 무의미하므로(내부적으로 긴 시간 사고함) 분기 처리합니다.
            kwargs = {
                "model": model_name,
                "messages": [
                    {"role": "user" if is_o1 else "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT}
                ]
            }
            if not is_o1:
                kwargs["stream"] = True
                kwargs["temperature"] = 0.7

            # API 호출
            response = client.chat.completions.create(**kwargs)

            if is_o1:
                # o1 모델들은 내부 "Thinking" 프로세스 때문에 사실상 스트리밍 체감이 안 됩니다.
                first_token_time = time.time()  # 대답이 반환된 시점을 첫 토큰으로 간주
                if hasattr(response.choices[0].message, 'content'):
                    full_response = response.choices[0].message.content or ""
            else:
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content is not None:
                        # 첫 토큰이 도달한 시간 기록
                        if first_token_time is None:
                            first_token_time = time.time()
                        full_response += content

            end_time = time.time()

            # 시간 계산
            if first_token_time:
                ttft = first_token_time - start_time
                total_duration = end_time - start_time
                chars_per_sec = len(full_response) / total_duration if total_duration > 0 else 0

                print(f"   ⏱️ TTFT (응답 시작 속도): {ttft:.3f} 초")
                print(f"   ⏳ 전체 소요 시간: {total_duration:.3f} 초")
                print(f"   ⚡ 생성 속도: 약 {chars_per_sec:.1f} 글자/초")
                print(f"   📄 생성된 답변 (일부): {full_response.strip()[:100]}...\n")
            else:
                print("   ❌ 응답 토큰을 받지 못했습니다.\n")

        except Exception as e:
            print(f"   ❌ {model_name} 호출 실패: {e}\n")

if __name__ == "__main__":
    run_benchmark()
