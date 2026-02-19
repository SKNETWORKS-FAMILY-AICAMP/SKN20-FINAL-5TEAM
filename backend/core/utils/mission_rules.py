# Mission Validation Rules for Backend
import re

VALIDATION_RULES = {
    "1": {  # Mission 1: Data Leakage
        "type": "data_leakage",
        "criticalPatterns": [
            {
                "pattern": {
                    "positive": r"(전체|모든|all|whole|entire).*(데이터|data).*(fit|학습|fitting)",
                    "negatives": [r"않|안|금지|말|never|not|don't|avoid|prevent"]
                },
                "message": "🚨 데이터 누수: 전체 데이터로 fit 금지",
                "correctExample": "scaler.fit(X_train) → scaler.transform(X_train), scaler.transform(X_test)",
                "explanation": "스케일러는 학습 데이터의 통계만 학습해야 합니다. 테스트 데이터 정보가 유입되면 과적합됩니다.",
                "severity": "CRITICAL"
            },
            {
                "pattern": {
                    # [2026-02-18] 수정: train_test_split과 fit이 단순히 공존하는 경우의 오탐 방지 (더 구체적으로 매칭)
                    "positive": r"(test|테스트|검증)\s*(데이터|data)?\s*(에|을|를|에 대해|에대해)\s*(fit|학습|fitting|학습시키)",
                    "negatives": [r"않|안|금지|never|not|don't", r"transform", r"train_test_split"]
                },
                "message": "🚨 테스트 데이터로 fit 금지",
                "correctExample": "학습 데이터(train)로만 fit → 테스트(test)는 transform만 적용",
                "explanation": "테스트 데이터는 미래의 보이지 않는 데이터를 시뮬레이션하므로 학습 과정에 유입되면 안 됩니다.",
                "severity": "CRITICAL"
            }
        ],
        "requiredConcepts": [
            {
                "id": "data_split",
                "name": "데이터 분리",
                "weight": 15,
                "patterns": [r"분리|나누|나눔|split|separate|divide", r"train.*test|학습.*테스트|training.*testing", r"train_test_split"]
            },
            {
                "id": "scaler_create",
                "name": "스케일러 생성",
                "weight": 15,
                "patterns": [r"scaler|스케일러|standardscaler|minmaxscaler", r"정규화.*도구|normalization.*tool|scaling.*object", r"StandardScaler\(\)|MinMaxScaler\(\)"]
            },
            {
                "id": "fit_train",
                "name": "학습 데이터로 fit",
                "weight": 20,
                "patterns": [r"(train|학습|training).*(fit|학습시|fitting)", r"fit.*train|학습시.*train", r"scaler\.fit\(.*train"]
            },
            {
                "id": "transform_train",
                "name": "학습 데이터 변환",
                "weight": 15,
                "patterns": [r"(train|학습).*(transform|변환|transforming)", r"transform.*train|변환.*train", r"scaler\.transform\(.*train"]
            },
            {
                "id": "transform_test",
                "name": "테스트 데이터 변환",
                "weight": 15,
                "patterns": [r"(test|테스트|testing).*(transform|변환|transforming)", r"transform.*test|변환.*test", r"scaler\.transform\(.*test"]
            },
            {
                "id": "same_scaler",
                "name": "동일 스케일러 사용",
                "weight": 10,
                "patterns": [r"같은.*scaler|동일.*scaler|same.*scaler", r"하나의.*scaler|한.*scaler|one.*scaler"]
            }
        ],
        "dependencies": [
            {"name": "분리 → 스케일러 생성", "before": "data_split", "after": "scaler_create", "points": 8, "strictness": "RECOMMENDED"},
            {"name": "fit → transform(train)", "before": "fit_train", "after": "transform_train", "points": 15, "strictness": "REQUIRED"},
            {"name": "fit → transform(test)", "before": "fit_train", "after": "transform_test", "points": 15, "strictness": "REQUIRED"},
            {"name": "transform(train) → transform(test)", "before": "transform_train", "after": "transform_test", "points": 12, "strictness": "RECOMMENDED"}
        ],
        "scoring": {"structure": 20, "concepts": 40, "flow": 40},
        "recommendations": {"minLines": 4, "maxLines": 12, "preferredStyle": "numbered"}
    },
    "2": {  # Mission 2: Overfitting Control (복잡도 제어)
        "type": "overfitting_control",
        "criticalPatterns": [
            {
                "pattern": r"(계속|무한|infinite).*(학습|training)",
                "message": "🚨 과적합 위험: 무한 학습 금지",
                "correctExample": "epochs=100 + early_stopping → 학습 조기 종료",
                "explanation": "너무 오래 학습하면 훈련 데이터에만 특화되어 일반화 성능이 떨어집니다.",
                "severity": "CRITICAL"
            },
            {
                "pattern": r"모든.*특성.*사용|제거.*없음",
                "message": "🚨 복잡도 경고: 불필요한 특성 제거 권장",
                "correctExample": "중요도가 낮은 특성 제거(Feature Selection)",
                "explanation": "모든 특성을 다 쓰면 모델이 너무 복잡해져 과적합될 가능성이 높습니다.",
                "severity": "WARNING"
            }
        ],
        "requiredConcepts": [
            {
                "id": "regularization",
                "name": "정규화(Regularization)",
                "weight": 30,
                "patterns": [r"정규화|L1|L2|Ridge|Lasso|Elastic|penalty", r"가중치.*제한|weight.*decay|alpha"]
            },
            {
                "id": "feature_selection",
                "name": "특성 선택",
                "weight": 30,
                "patterns": [r"특성.*선택|제거|중요도|feature.*selection|drop|importance", r"불필요한.*삭제|분산.*필터"]
            },
            {
                "id": "monitoring",
                "name": "모니터링",
                "weight": 40,
                "patterns": [r"검증.*분석|val_loss|accuracy.*추적|monitoring|진단", r"학습.*그래프|curve|점수.*비교"]
            }
        ],
        "dependencies": [
            {"name": "특성 선택 → 정규화", "before": "feature_selection", "after": "regularization", "points": 20, "strictness": "RECOMMENDED"},
            {"name": "정규화 → 모니터링", "before": "regularization", "after": "monitoring", "points": 20, "strictness": "REQUIRED"}
        ],
        "scoring": {"structure": 20, "concepts": 40, "flow": 40},
        "recommendations": {"minLines": 3, "maxLines": 10}
    },
    "QUEST_01": None,
    "QUEST_02": None,
    "QUEST_03": None,
    "QUEST_04": None,
    "QUEST_05": None,
    "QUEST_06": None,
}

VALIDATION_RULES["QUEST_01"] = VALIDATION_RULES["1"]
VALIDATION_RULES["QUEST_02"] = VALIDATION_RULES["2"]
# 추가 미션들은 기본적으로 1번이나 2번의 구조를 재사용하거나 확장 가능
VALIDATION_RULES["QUEST_03"] = VALIDATION_RULES["1"] 
VALIDATION_RULES["QUEST_04"] = VALIDATION_RULES["2"]
VALIDATION_RULES["QUEST_05"] = VALIDATION_RULES["1"]
VALIDATION_RULES["QUEST_06"] = VALIDATION_RULES["2"]
