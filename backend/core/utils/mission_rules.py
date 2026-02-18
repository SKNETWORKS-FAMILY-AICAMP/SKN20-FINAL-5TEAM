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
                    "positive": r"(test|테스트|검증).*(fit|학습시키|fitting)",
                    "negatives": [r"않|안|금지|never|not|don't", r"transform"]
                },
                "message": "🚨 테스트 데이터로 fit 금지",
                "correctExample": "학습 데이터로만 fit → 테스트는 transform만",
                "explanation": "테스트 데이터는 미래의 보이지 않는 데이터를 시뮬레이션합니다.",
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
    "QUEST_01": None, # Will be mapped to "1"
}

VALIDATION_RULES["QUEST_01"] = VALIDATION_RULES["1"]
