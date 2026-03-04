import os
import json
import random

# [2026-03-04] 생성: AICE 문제은행 JSON에서 실전 문제 추출
async def generate_aice_quests(difficulty: str = 'Associate', count: int = 1) -> list:
    """AICE 문제은행에서 선택한 난이도에 맞는 문제를 추출 (LogicRun 4지선다형 객관식 UI용)"""
    
    # JSON 파일 경로
    # __file__ 위치: backend/core/services/wars/aice_question_generator.py
    # backend 디렉토리를 찾기 위해 4번 상위로 올라감
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    json_path = os.path.join(base_dir, "data", "aice_question_bank_v3.json")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            bank_data = json.load(f)
            
        # 프론트엔드에서 넘어오는 difficulty 값이 소문자일 수 있으므로 대문자화하여 매칭
        # e.g., 'basic' -> 'Basic'
        diff_key = difficulty.capitalize()
        if diff_key not in bank_data:
            print(f"⚠️ [AICEGen] Invalid difficulty '{difficulty}', falling back to 'Basic'")
            diff_key = 'Basic'
            
        questions_pool = bank_data.get(diff_key, [])
        if len(questions_pool) < 5:
            print(f"⚠️ [AICEGen] Not enough questions in '{diff_key}', using all available")
            selected_qs = questions_pool
        else:
            selected_qs = random.sample(questions_pool, 5)
            
        # LogicRun 프론트엔드의 4지선다 구조에 맞게 변환
        # LogicRun은 기본적으로 1개의 'Quest' 안의 여러 'speedRounds'를 기대함.
        # 따라서 뽑은 5개의 문제를 1개의 Quest 객체 안에 넣어서 반환.
        
        speed_rounds = []
        for i, q in enumerate(selected_qs):
            speed_rounds.append({
                "round": i + 1,
                "context": q.get("q", "문제 텍스트 오류"), # AICE 문제 텍스트
                # 기존처럼 배열이 아니라 새로운 4지선다 전용 필드로 전달
                "options": q.get("opts", []),
                "answerIdx": q.get("ans", 0),
                "explanation": q.get("exp", ""),
                
                # 프론트엔드 호환성을 위해 기존 codeLines 자리에도 일부 남김
                "codeLines": [
                    {"text": "AICE 객관식 문제", "type": "fixed"}
                ]
            })
            
        quest = {
            "id": random.randint(1000, 9999),
            "title": f"AICE {diff_key} 실전 퀴즈",
            "scenario": f"AICE {diff_key} 자격증 취득을 위한 5문제 실전 트레이닝입니다.",
            "speedRounds": speed_rounds,
            "designSprint": _get_fallback_quest()["designSprint"] # Phase 2 구조는 기본 폴백 사용
        }
        
        return [quest]
        
    except Exception as e:
        print(f"⚠️ [AICEGen] Failed to load AICE JSON: {e}")
        return [_get_fallback_quest()]


def _get_fallback_quest() -> dict:
    """폴백 퀘스트 (에러 시 기본 문제 제공)"""
    return {
        "id": 9999,
        "title": "AICE 백업 문제",
        "scenario": "문제를 불러오지 못했습니다. 기본 문제로 진행합니다.",
        "speedRounds": [
            {
                "round": 1,
                "context": "AI(인공지능), 머신러닝, 딥러닝의 포함 관계로 올바른 것은?",
                "options": ["딥러닝 ⊃ 머신러닝 ⊃ AI", "AI ⊃ 머신러닝 ⊃ 딥러닝", "머신러닝 ⊃ AI ⊃ 딥러닝", "세 개념은 모두 동일"],
                "answerIdx": 1,
                "explanation": "AI가 가장 넓은 개념이고, 그 안에 머신러닝, 그 안에 딥러닝이 포함되는 계층 구조입니다.",
                "codeLines": [{"text": "백업 문제", "type": "fixed"}]
            }
        ],
        "designSprint": {
            "checklist": [
                {"id": "c1", "label": "데이터 전처리 루틴 추가", "patterns": ["전처리|결측치|이상치"]},
                {"id": "c2", "label": "모델 학습 코드 작성", "patterns": ["학습|fit|train"]},
                {"id": "c3", "label": "평가 지표 계산", "patterns": ["평가|score|정확도"]},
                {"id": "c4", "label": "결과 시각화", "patterns": ["시각|plot|그래프"]},
                {"id": "c5", "label": "최종 배포 함수", "patterns": ["배포|deploy|반환"]}
            ]
        }
    }
