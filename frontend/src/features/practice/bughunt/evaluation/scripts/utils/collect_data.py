"""
MBPP 데이터셋 수집 및 번역 스크립트

Google Research의 MBPP(Mostly Basic Python Problems) 데이터셋에서
코딩 문제를 수집하고 영어를 한글로 번역하여 JSON 파일로 저장합니다.

작성일: 2026-01-22
작성자: SKN20 5팀
"""

import json
import os
import time
from datasets import load_dataset
from deep_translator import GoogleTranslator

# Hugging Face Hub 경고 메시지 비활성화
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

def translate_to_korean(text, delay=0.5):
    """
    영어 텍스트를 한글로 번역합니다.
    
    Google Translator API를 사용하여 영어 텍스트를 한글로 번역합니다.
    API 호출 제한을 방지하기 위해 번역 후 지연 시간을 추가합니다.
    
    Args:
        text (str): 번역할 영어 텍스트
        delay (float): API 호출 간 지연 시간 (초), 기본값 0.5초
    
    Returns:
        str: 번역된 한글 텍스트. 번역 실패 시 원본 텍스트 반환
    
    Example:
        >>> translate_to_korean("Hello World")
        "안녕하세요 세계"
    """
    try:
        # 빈 텍스트나 특수 케이스는 번역하지 않고 그대로 반환
        if not text or text == "N/A" or text == "No description available":
            return text
        
        # Google Translator 인스턴스 생성 (영어 -> 한글)
        translator = GoogleTranslator(source='en', target='ko')
        translated = translator.translate(text)
        
        # API 호출 제한 방지를 위한 지연
        time.sleep(delay)
        return translated
    except Exception as e:
        # 번역 실패 시 경고 메시지 출력 후 원본 텍스트 반환
        print(f"⚠️ 번역 실패: {e}")
        return text

def collect_problems(save_filename="problems.json", limit=10):
    """
    MBPP 데이터셋에서 코딩 문제를 수집하고 한글로 번역하여 저장합니다.
    
    Google Research의 MBPP 데이터셋에서 Python 코딩 문제를 가져와
    영어 원문과 한글 번역을 포함한 JSON 파일로 저장합니다.
    
    Args:
        save_filename (str): 저장할 JSON 파일명, 기본값 "problems.json"
        limit (int): 수집할 문제 개수, 기본값 10개
    
    Returns:
        None
    
    Output Format (JSON):
        [
            {
                "id": 문제 ID,
                "difficulty": 난이도 (영문),
                "difficulty_ko": 난이도 (한글),
                "title": 제목 (영문),
                "title_ko": 제목 (한글),
                "description": 설명 (영문),
                "description_ko": 설명 (한글),
                "examples": 예제 입출력,
                "solution_code": 정답 코드
            },
            ...
        ]
    """
    print("🚀 데이터 수집 시작 (MBPP 데이터셋)...")
    
    try:
        # MBPP 데이터셋 로드 (full 버전, test split, 스트리밍 모드)
        # 스트리밍 모드: 전체 데이터를 다운로드하지 않고 순차적으로 읽기
        dataset = load_dataset("google-research-datasets/mbpp", "full", split="test", streaming=True)
        
        # 수집된 문제를 저장할 리스트
        collected_data = []
        
        # 데이터셋을 순회하며 문제 수집
        for item in dataset:
            # 지정된 개수만큼 수집했으면 종료
            if len(collected_data) >= limit:
                break
            
            # 데이터셋 필드명이 버전에 따라 다를 수 있어 유연하게 처리
            # 'text' 또는 'prompt' 필드에서 문제 설명 추출
            description = item.get('text') or item.get('prompt') or "No description available"
            
            # 영어 문제 데이터 구조 생성
            problem = {
                "id": item.get('task_id'),  # 문제 고유 ID
                "difficulty": "introductory",  # 난이도 (MBPP는 기본적으로 입문 수준)
                "title": f"Logic Practice {item.get('task_id')}",  # 문제 제목
                "description": description,  # 문제 설명
                "examples": [
                    {
                        "input": "Sample test",
                        "output": item.get('test_list', ["N/A"])[0] if item.get('test_list') else "N/A"
                    }
                ],
                "solution_code": item.get('code', "")  # 정답 코드
            }
            
            # 한글 번역 수행
            print(f"🔄 [{len(collected_data) + 1}] 번역 중...")
            problem["title_ko"] = translate_to_korean(problem["title"])  # 제목 번역
            problem["description_ko"] = translate_to_korean(problem["description"])  # 설명 번역
            problem["difficulty_ko"] = "입문" if problem["difficulty"] == "introductory" else problem["difficulty"]  # 난이도 번역
            
            # 번역된 문제를 리스트에 추가
            collected_data.append(problem)
            print(f"✅ [{len(collected_data)}] 수집 및 번역 완료: Task {item.get('task_id')}")
            
        # JSON 파일로 저장 (UTF-8 인코딩, 들여쓰기 2칸)
        with open(save_filename, "w", encoding="utf-8") as f:
            json.dump(collected_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 총 {len(collected_data)}개의 문제가 '{save_filename}'에 저장되었습니다.")

    except Exception as e:
        # 오류 발생 시 메시지 출력
        print(f"❌ 에러 발생: {e}")

# 스크립트 직접 실행 시 동작
if __name__ == "__main__":
    # 10개의 문제를 수집하고 번역하여 problems.json에 저장
    collect_problems(limit=10)