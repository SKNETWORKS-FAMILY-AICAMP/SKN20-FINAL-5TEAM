"""
architecture_advanced_gcp.json을 백엔드 fixture 형식으로 변환하는 스크립트
"""
import json
from datetime import datetime

# 입력 파일 읽기
with open('frontend/src/data/architecture_advanced_gcp.json', 'r', encoding='utf-8') as f:
    problems = json.load(f)

# 기존 fixture 읽기
with open('backend/core/fixtures/practice_detail_data.json', 'r', encoding='utf-8') as f:
    existing_fixtures = json.load(f)

# unit03용 fixture 생성
new_fixtures = []
timestamp = "2026-02-12T10:00:00Z"

for idx, problem in enumerate(problems, start=1):
    # engineering_spec을 constraints 배열로 변환 (프론트엔드 호환)
    constraints = problem.get('engineering_spec', [])
    if isinstance(constraints, dict):
        # dict인 경우 배열로 변환
        constraints = [f"{key}: {value}" for key, value in constraints.items()]

    # missions도 배열로 변환
    missions = problem.get('mission', [])

    fixture = {
        "model": "core.practicedetail",
        "pk": f"unit03_{idx:02d}",
        "fields": {
            "practice": "unit03",
            "detail_title": problem['title'],
            "detail_type": "PROBLEM",
            "content_data": {
                "problem_id": problem['problem_id'],
                "title": problem['title'],
                "scenario": problem['scenario'],
                "constraints": constraints,
                "missions": missions,
                "rubric_functional": problem.get('rubric_functional', {}),
                "rubric_non_functional": problem.get('rubric_non_functional', []),
                "axis_weights": problem.get('axis_weights', {}),
                "decision_points": problem.get('decision_points', [])
            },
            "display_order": idx,
            "is_active": True,
            "create_date": timestamp,
            "update_date": timestamp,
            "use_yn": "Y"
        }
    }
    new_fixtures.append(fixture)

# 기존 fixture에서 unit03 제거하고 새로운 거 추가
filtered_fixtures = [f for f in existing_fixtures if not f['pk'].startswith('unit03_')]
all_fixtures = filtered_fixtures + new_fixtures

# 저장
with open('backend/core/fixtures/practice_detail_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_fixtures, f, ensure_ascii=False, indent=4)

print(f"[OK] {len(new_fixtures)}개의 아키텍처 문제를 fixture에 추가했습니다.")
print(f"   총 fixture 수: {len(all_fixtures)}개")
