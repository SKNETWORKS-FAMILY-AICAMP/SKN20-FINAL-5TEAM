import requests
import json
import time

def check_wanted_api():
    # 1. AI 엔지니어 직군(650) API 호출
    url = "https://www.wanted.co.kr/api/v4/jobs"
    params = {
        "country": "kr",
        "tag_type_ids": "650",
        "locations": "all",
        "years": "-1",
        "limit": 5,
        "job_sort": "job.latest_order"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    print("API 요청 시작...")
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        jobs = data.get('data', [])
        
        if not jobs:
            print("가져온 공고가 없습니다. 파라미터를 확인하세요.")
            return
            
        # 2. 결과 저장 테스트
        filename = "wanted_ai_list.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)
            
        print(f"성공! {len(jobs)}개의 공고 목록이 '{filename}'에 저장되었습니다.")
        
        # 샘플 ID 하나 출력 (상세 페이지 크롤링용)
        print(f"첫 번째 공고 ID: {jobs[0]['id']}")
    else:
        print(f"에러 발생: {response.status_code}")

check_wanted_api()