"""
AI를 활용하여 Python 코드의 수도코드(pseudo-code)를 생성하는 스크립트
problems.json의 solution_code를 읽어서 각 문제에 대한 모범 수도코드를 생성합니다.
"""

import json
import os
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def generate_pseudocode(solution_code, description, title):
    """
    AI를 사용하여 주어진 Python 코드의 수도코드를 생성합니다.
    
    Args:
        solution_code (str): Python 솔루션 코드
        description (str): 문제 설명
        title (str): 문제 제목
        
    Returns:
        str: 생성된 수도코드
    """
    prompt = f"""
다음은 프로그래밍 문제와 그 해결 코드입니다.

문제 제목: {title}
문제 설명: {description}

Python 코드:
```python
{solution_code}
```

위 Python 코드의 논리를 설명하는 명확하고 이해하기 쉬운 수도코드(pseudo-code)를 작성해주세요.
수도코드는 다음 규칙을 따라주세요:

1. 한국어로 작성
2. 들여쓰기를 사용하여 구조를 명확히 표현
3. 알고리즘의 핵심 로직과 각 단계를 명확히 설명
4. 복잡한 구현 세부사항보다는 논리적 흐름에 집중
5. 변수명과 함수명은 의미를 명확히 전달할 수 있도록 표현

수도코드만 작성하고, 추가 설명은 포함하지 마세요.
"""

    try:
        # OpenAI 클라이언트 초기화 (함수 내부에서 수행)
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 또는 "gpt-4o", "gpt-3.5-turbo" 등
            messages=[
                {"role": "system", "content": "당신은 프로그래밍 교육 전문가입니다. 코드를 분석하여 명확하고 이해하기 쉬운 수도코드를 작성하는 것이 전문입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # 일관성을 위해 낮은 temperature 사용
            max_tokens=1000
        )
        
        pseudocode = response.choices[0].message.content.strip()
        return pseudocode
    
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return None


def process_problems(input_file='problems.json', output_file='problems_with_pseudocode.json'):
    """
    problems.json 파일을 읽어서 각 문제에 대한 수도코드를 생성하고 저장합니다.
    
    Args:
        input_file (str): 입력 JSON 파일 경로
        output_file (str): 출력 JSON 파일 경로
    """
    script_dir = Path(__file__).parent
    input_path = script_dir / input_file
    output_path = script_dir / output_file
    
    # problems.json 파일 읽기
    with open(input_path, 'r', encoding='utf-8') as f:
        problems = json.load(f)
    
    print(f"총 {len(problems)}개의 문제를 처리합니다.\n")
    
    # 각 문제에 대해 수도코드 생성
    for idx, problem in enumerate(problems, 1):
        problem_id = problem.get('id')
        title = problem.get('title_ko', problem.get('title'))
        description = problem.get('description_ko', problem.get('description'))
        solution_code = problem.get('solution_code')
        
        print(f"[{idx}/{len(problems)}] 처리 중: {title} (ID: {problem_id})")
        
        if solution_code:
            pseudocode = generate_pseudocode(solution_code, description, title)
            
            if pseudocode:
                problem['pseudocode'] = pseudocode
                print(f"✓ 수도코드 생성 완료\n")
            else:
                print(f"✗ 수도코드 생성 실패\n")
        else:
            print(f"✗ solution_code가 없습니다.\n")
    
    # 결과를 새 파일로 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)
    
    print(f"\n완료! 결과가 {output_file}에 저장되었습니다.")
    
    # 통계 출력
    problems_with_pseudocode = sum(1 for p in problems if 'pseudocode' in p)
    print(f"\n통계:")
    print(f"- 전체 문제: {len(problems)}개")
    print(f"- 수도코드 생성 성공: {problems_with_pseudocode}개")
    print(f"- 수도코드 생성 실패: {len(problems) - problems_with_pseudocode}개")


def main():
    """
    메인 함수
    """
    # API 키 확인
    if not os.getenv('OPENAI_API_KEY'):
        print("경고: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("다음과 같이 설정해주세요:")
        print("  Windows: $env:OPENAI_API_KEY='your-api-key'")
        print("  Linux/Mac: export OPENAI_API_KEY='your-api-key'")
        return
    
    print("=" * 60)
    print("수도코드 생성 스크립트")
    print("=" * 60)
    print()
    
    process_problems()


if __name__ == "__main__":
    main()
