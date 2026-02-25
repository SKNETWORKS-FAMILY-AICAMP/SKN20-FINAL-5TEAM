import os
import sys
import django
import json
import time
import openai

# Django 환경 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from core.models import PracticeDetail
from core.services.arch_evaluator import ArchEvaluator

def test_consistency(iterations=3):
    print(f"🤖 [gpt-4o-mini] 아키텍처 평가 일관성 테스트 시작 (총 {iterations}회)")
    
    # 1. 문제 가져오기 (unit03_27: 결제 파이프라인 설계)
    try:
        pd = PracticeDetail.objects.get(id='unit03_27')
        q_data = pd.content_data
    except Exception as e:
        print(f"❌ 문제를 불러오는 중 오류 발생: {e}")
        return

    title = q_data.get('title', 'Unknown Mission')
    
    # 루브릭 데이터 준비
    rubric = q_data.get('rubric_functional', {})
    axis_weights = q_data.get('axis_weights', {})
    if axis_weights:
        rubric['axis_weights'] = axis_weights

    # 2. 플레이어 모의(Mock) 데이터 준비
    # Player 1: 요구사항 대부분 충족 (MQ를 사용한 비동기/안정적 설계)
    p1_data = {
        'name': '우수설계_유저',
        'pts': 90,
        'checks': [
            {'label': '권리 관리(A) 배치', 'ok': True},
            {'label': 'Message Queue 배치', 'ok': True},
            {'label': '회계/결제(B,C) 배치', 'ok': True},
        ],
        'nodes': [{'name': 'Auth System'}, {'name': 'Message Queue'}, {'name': 'Payment System'}],
        'arrows': [{'fc': 'Auth System', 'tc': 'Message Queue'}, {'fc': 'Message Queue', 'tc': 'Payment System'}]
    }

    # Player 2: 요구사항 누락 (MQ 없이 직접 결합하여 결함 발생 가능성)
    p2_data = {
        'name': '부족설계_유저',
        'pts': 40,
        'checks': [
            {'label': '권리 관리(A) 배치', 'ok': True},
            {'label': 'Message Queue 배치', 'ok': False},
            {'label': '회계/결제(B,C) 배치', 'ok': True},
        ],
        'nodes': [{'name': 'Auth System'}, {'name': 'Payment System'}],
        'arrows': [{'fc': 'Auth System', 'tc': 'Payment System'}]
    }

    print(f"\n📝 문제 제목: {title}")
    print(f"⚖️ 루브릭 로드 성공: 필수 컴포넌트 {len(rubric.get('required_components', []))}개")

    # 3. 프롬프트 생성 (ArchEvaluator 로직 재사용)
    evaluator = ArchEvaluator()
    system_prompt = evaluator._build_system_prompt(rubric)
    user_prompt = evaluator._build_user_prompt(title, p1_data, p2_data)
    
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    results = []
    
    for i in range(iterations):
        print(f"\n🔄 --- [ 테스트 {i+1}회차 ] ---")
        start_time = time.time()
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # 사용자 요청에 따라 gpt-4o-mini 사용
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            parsed = json.loads(response.choices[0].message.content)
            elapsed = time.time() - start_time
            print(f"⏱️ 소요 시간: {elapsed:.2f}초")
            
            # 요약된 리뷰 결과만 출력
            print(f"🗣️ 우수 유저(P1) 분석 요약: {parsed.get('player1', {}).get('my_analysis')[:70]}...")
            print(f"🗣️ 우수 유저(P1) 비교 요약: {parsed.get('player1', {}).get('versus')[:70]}...")
            
            print(f"🗣️ 부족 유저(P2) 분석 요약: {parsed.get('player2', {}).get('my_analysis')[:70]}...")
            print(f"🗣️ 부족 유저(P2) 비교 요약: {parsed.get('player2', {}).get('versus')[:70]}...")
            results.append(parsed)
        except Exception as e:
            print(f"❌ API 호출 중 오류: {e}")

    # 결과를 json 파일로 저장
    output_path = os.path.join(BASE_DIR, 'scripts', 'consistency_results.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 전체 JSON 결과가 파일로 저장되었습니다: {output_path}")

if __name__ == '__main__':
    # 5번 정도 반복하여 답변의 일관성을 체크
    test_consistency(5)
