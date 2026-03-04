import os
import json
import random

# [2026-03-04] 난이도별 AICE 체크리스트 (Phase2 의사코드 평가)
# logicQuests.js의 프론트엔드 로컬 데이터와 동일한 패턴 매칭 기준
DESIGN_SPRINT_BY_DIFFICULTY = {
    "Basic": {
        "scenario": "CSV 파일을 읽어 결측치를 처리하고, 기초 통계를 출력하는 pandas 코드를 의사코드로 작성하세요.",
        "checklist": [
            {"id": "c1", "label": "CSV 파일 읽기 (read_csv)", "patterns": ["read_csv|csv.*읽|파일.*로드|불러오기"]},
            {"id": "c2", "label": "결측치 확인 (isnull, isna)", "patterns": ["isnull|isna|결측|null|NaN|nan"]},
            {"id": "c3", "label": "결측치 처리 (fillna 또는 dropna)", "patterns": ["fillna|dropna|결측.*처리|결측.*제거|평균.*채"]},
            {"id": "c4", "label": "기초 통계 출력 (describe, mean, std 등)", "patterns": ["describe|mean|std|통계|평균|표준편차"]},
            {"id": "c5", "label": "결과 출력 (print)", "patterns": ["print|출력|표시|보여"]},
        ]
    },
    "Associate": {
        "scenario": "데이터를 전처리하고 sklearn으로 분류 모델을 학습/평가하는 파이프라인을 의사코드로 작성하세요.",
        "checklist": [
            {"id": "c1", "label": "결측치 처리 (fillna, dropna)", "patterns": ["fillna|dropna|결측.*처리|결측.*제거"]},
            {"id": "c2", "label": "인코딩 (LabelEncoder, get_dummies)", "patterns": ["LabelEncoder|get_dummies|인코딩|label.*encod|원핫"]},
            {"id": "c3", "label": "데이터 분할 (train_test_split)", "patterns": ["train_test_split|분할|split|훈련.*테스트"]},
            {"id": "c4", "label": "모델 학습 (fit)", "patterns": ["fit|학습|train|훈련"]},
            {"id": "c5", "label": "예측 및 평가 (predict, accuracy_score)", "patterns": ["predict|accuracy|정확도|평가|score"]},
        ]
    },
    "Professional": {
        "scenario": "Keras로 딥러닝 모델을 구성하고 학습/평가하는 코드를 의사코드로 작성하세요.",
        "checklist": [
            {"id": "c1", "label": "데이터 정규화 (/ 255, normalize)", "patterns": ["255|normalize|정규화|스케일"]},
            {"id": "c2", "label": "모델 구성 (Sequential, Dense, Conv2D 등)", "patterns": ["Sequential|Dense|Conv2D|LSTM|Embedding|모델.*구성|레이어"]},
            {"id": "c3", "label": "모델 컴파일 (compile, optimizer, loss)", "patterns": ["compile|optimizer|loss|adam|sgd|컴파일"]},
            {"id": "c4", "label": "모델 학습 (model.fit, epochs)", "patterns": ["model.fit|epochs|학습|train|fit"]},
            {"id": "c5", "label": "모델 평가 (evaluate, predict)", "patterns": ["evaluate|predict|평가|예측|정확도"]},
        ]
    },
}


# [2026-03-04] 생성: AICE 문제은행 JSON에서 실전 문제 추출
async def generate_aice_quests(difficulty: str = 'Associate', count: int = 1) -> list:
    """AICE 문제은행에서 선택한 난이도에 맞는 문제를 추출 (LogicRun 4지선다형 객관식 UI용)"""

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    json_path = os.path.join(base_dir, "data", "aice_question_bank_v3.json")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            bank_data = json.load(f)

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

        speed_rounds = []
        for i, q in enumerate(selected_qs):
            speed_rounds.append({
                "round": i + 1,
                "context": q.get("q", "문제 텍스트 오류"),
                "options": q.get("opts", []),
                "answerIdx": q.get("ans", 0),
                "explanation": q.get("exp", ""),
                "codeLines": [
                    {"text": "AICE 객관식 문제", "type": "fixed"}
                ]
            })

        # [2026-03-04] 난이도별 AICE 체크리스트 적용
        design_data = DESIGN_SPRINT_BY_DIFFICULTY.get(diff_key, DESIGN_SPRINT_BY_DIFFICULTY["Basic"])

        quest = {
            "id": random.randint(1000, 9999),
            "title": f"AICE {diff_key} 실전 퀴즈",
            "difficulty": diff_key,
            "scenario": design_data["scenario"],
            "speedRounds": speed_rounds,
            "designSprint": {
                "checklist": design_data["checklist"]
            }
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
        "difficulty": "Basic",
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
            "checklist": DESIGN_SPRINT_BY_DIFFICULTY["Basic"]["checklist"]
        }
    }
