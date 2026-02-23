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
                "patterns": [r"정규화|규제|L1|L2|Ridge|Lasso|리지|라쏘|Elastic|penalty", r"가중치.*제한|weight.*decay|alpha|계수.*제어|패널티"]
            },
            {
                "id": "feature_selection",
                "name": "특성 선택",
                "weight": 30,
                "patterns": [r"특성|피처|변수.*(선택|제거|중요도|삭제)|feature.*selection|drop|importance", r"불필요한.*(삭제|제거)|분산.*필터|Selection"]
            },
            {
                "id": "monitoring",
                "name": "모니터링",
                "weight": 40,
                "patterns": [r"검증|val_loss|accuracy.*추적|monitoring|진단|오차|손실|지표", r"학습.*그래프|curve|점수.*비교|시각화|모니터링|early.*stopping|조기.*종료"]
            }
        ],
        "dependencies": [
            {"name": "특성 선택 → 정규화", "before": "feature_selection", "after": "regularization", "points": 20, "strictness": "RECOMMENDED"},
            {"name": "정규화 → 모니터링", "before": "regularization", "after": "monitoring", "points": 20, "strictness": "REQUIRED"}
        ],
        "scoring": {"structure": 20, "concepts": 40, "flow": 40},
        "recommendations": {"minLines": 3, "maxLines": 10}
    },
    "3": {  # Mission 3: Class Imbalance (불균형 데이터 처리)
        "type": "class_imbalance",
        "criticalPatterns": [
            {
                "pattern": r"(test|테스트|검증).*(SMOTE|오버샘플링|oversampl|리샘플링|resample)",
                "message": "🚨 테스트 데이터에 리샘플링 금지",
                "correctExample": "SMOTE는 학습 데이터(X_train)에만 적용 → 테스트 데이터는 원본 유지",
                "explanation": "테스트 데이터를 리샘플링하면 실제 운영 환경의 분포를 왜곡하여 평가가 무의미해집니다.",
                "severity": "CRITICAL"
            },
            {
                "pattern": r"(정확도|accuracy)\s*(만|만으로|으로)\s*(충분|평가|판단)",
                "message": "⚠️ 불균형 데이터에서 정확도만으로 평가 위험",
                "correctExample": "Precision, Recall, F1-Score, AUC-ROC 등 다중 지표 사용",
                "explanation": "99:1 불균형에서 모두 다수 클래스로 분류해도 정확도 99%가 나옵니다.",
                "severity": "WARNING"
            }
        ],
        "requiredConcepts": [
            {
                "id": "imbalance_detection",
                "name": "불균형 진단",
                "weight": 25,
                "patterns": [r"불균형|진단|분포.*확인|비율.*확인|value_counts|imbalance", r"클래스.*분포|class.*distribution|편향"]
            },
            {
                "id": "sampling_strategy",
                "name": "샘플링 전략",
                "weight": 35,
                "patterns": [r"SMOTE|오버샘플링|언더샘플링|oversampl|undersamp|리샘플링|resample", r"합성.*생성|synthetic|imblearn|class_weight.*balanced"]
            },
            {
                "id": "fair_evaluation",
                "name": "공정한 평가",
                "weight": 40,
                "patterns": [r"F1|AUC|ROC|Precision|Recall|재현율|정밀도|정확도.*(이외|대신|한계)", r"평가.*지표|metric|confusion.*matrix|혼동.*행렬|다양한.*지표"]
            }
        ],
        "dependencies": [
            {"name": "진단 → 샘플링", "before": "imbalance_detection", "after": "sampling_strategy", "points": 15, "strictness": "RECOMMENDED"},
            {"name": "샘플링 → 평가", "before": "sampling_strategy", "after": "fair_evaluation", "points": 20, "strictness": "REQUIRED"}
        ],
        "scoring": {"structure": 20, "concepts": 40, "flow": 40},
        "recommendations": {"minLines": 3, "maxLines": 12}
    },
    "4": {  # Mission 4: Feature Engineering (피처 엔지니어링)
        "type": "feature_engineering",
        "criticalPatterns": [
            {
                "pattern": r"(모든|전체|all)\s*(특성|feature|변수).*(그대로|바로|직접)\s*(사용|넣|입력)",
                "message": "⚠️ 원시 특성만 사용하면 모델 성능이 제한됩니다",
                "correctExample": "도메인 지식으로 파생 특성 생성 (예: 구매빈도 = 구매횟수/가입일수)",
                "explanation": "원시 특성만으로는 숨겨진 패턴을 포착하기 어렵습니다.",
                "severity": "WARNING"
            }
        ],
        "requiredConcepts": [
            {
                "id": "feature_creation",
                "name": "특성 창조",
                "weight": 35,
                "patterns": [r"생성|창조|파생|조합|만들|creation|derive|engineer", r"빈도|비율|상호작용|구매.*방문|frequency|ratio|interaction"]
            },
            {
                "id": "feature_transformation",
                "name": "특성 변환",
                "weight": 30,
                "patterns": [r"변환|로그|정규화|스케일링|transform|log|scaling|normalize", r"log1p|StandardScaler|MinMaxScaler|인코딩|encoding|OneHot"]
            },
            {
                "id": "feature_selection",
                "name": "특성 선택",
                "weight": 35,
                "patterns": [r"선택|중요도|제거|selection|importanc|drop|제거|피처.*선별", r"feature_importances|SelectKBest|RFE|상관관계|correlation|가중치.*확인"]
            }
        ],
        "dependencies": [
            {"name": "창조 → 변환", "before": "feature_creation", "after": "feature_transformation", "points": 15, "strictness": "RECOMMENDED"},
            {"name": "변환 → 선택", "before": "feature_transformation", "after": "feature_selection", "points": 15, "strictness": "RECOMMENDED"}
        ],
        "scoring": {"structure": 20, "concepts": 40, "flow": 40},
        "recommendations": {"minLines": 3, "maxLines": 12}
    },
    "5": {  # Mission 5: Hyperparameter Tuning (하이퍼파라미터 튜닝)
        "type": "hyperparameter_tuning",
        "criticalPatterns": [
            {
                "pattern": r"(기본값|default).*(그대로|충분|최적)",
                "message": "⚠️ 기본값이 항상 최적은 아닙니다",
                "correctExample": "GridSearchCV, RandomizedSearchCV 등으로 체계적 탐색",
                "explanation": "기본 파라미터는 범용적 설정일 뿐, 데이터에 맞게 튜닝해야 합니다.",
                "severity": "WARNING"
            }
        ],
        "requiredConcepts": [
            {
                "id": "param_space",
                "name": "파라미터 공간 정의",
                "weight": 30,
                "patterns": [r"파라미터.*공간|범위|param.*grid|param.*space|후보", r"n_estimators|max_depth|min_samples|learning_rate|alpha"]
            },
            {
                "id": "search_strategy",
                "name": "탐색 전략",
                "weight": 35,
                "patterns": [r"그리드.*탐색|랜덤.*탐색|GridSearch|RandomSearch|Bayesian|베이지안", r"Optuna|HalvingGrid|탐색.*전략|search.*strategy"]
            },
            {
                "id": "cross_validation",
                "name": "교차검증",
                "weight": 35,
                "patterns": [r"교차.*검증|cross.*valid|K-?Fold|cv=|k.*fold", r"검증.*폴드|fold.*split|StratifiedKFold"]
            }
        ],
        "dependencies": [
            {"name": "공간 정의 → 탐색", "before": "param_space", "after": "search_strategy", "points": 20, "strictness": "REQUIRED"},
            {"name": "탐색 → 교차검증", "before": "search_strategy", "after": "cross_validation", "points": 15, "strictness": "RECOMMENDED"}
        ],
        "scoring": {"structure": 20, "concepts": 40, "flow": 40},
        "recommendations": {"minLines": 3, "maxLines": 12}
    },
    "6": {  # Mission 6: Explainability (모델 해석성)
        "type": "explainability",
        "criticalPatterns": [
            {
                "pattern": r"(설명|해석).*(불필요|필요.*없|skip|생략)",
                "message": "⚠️ 규제 산업에서 설명가능성은 필수입니다",
                "correctExample": "SHAP, LIME 등으로 개별 예측 해석 + 공정성 검증",
                "explanation": "금융, 의료 등 규제 분야에서는 모델의 의사결정 근거를 설명해야 합니다.",
                "severity": "WARNING"
            }
        ],
        "requiredConcepts": [
            {
                "id": "global_interpretation",
                "name": "전역적 해석",
                "weight": 30,
                "patterns": [r"전역.*해석|global.*interpret|특성.*중요도|feature.*importanc", r"permutation.*importanc|순열.*중요도|전체.*영향"]
            },
            {
                "id": "local_interpretation",
                "name": "개별적 해석",
                "weight": 35,
                "patterns": [r"SHAP|LIME|개별.*해석|local.*interpret|force.*plot", r"개별.*예측|individual.*explain|기여도"]
            },
            {
                "id": "fairness_validation",
                "name": "공정성 검증",
                "weight": 35,
                "patterns": [r"공정|편향|차별|bias|fair|unfair|discriminat", r"보호.*속성|그룹별.*비교|성별|인종|대리.*변수|proxy"]
            }
        ],
        "dependencies": [
            {"name": "전역 → 개별", "before": "global_interpretation", "after": "local_interpretation", "points": 15, "strictness": "RECOMMENDED"},
            {"name": "개별 → 공정성", "before": "local_interpretation", "after": "fairness_validation", "points": 15, "strictness": "RECOMMENDED"}
        ],
        "scoring": {"structure": 20, "concepts": 40, "flow": 40},
        "recommendations": {"minLines": 3, "maxLines": 12}
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
VALIDATION_RULES["QUEST_03"] = VALIDATION_RULES["3"]
VALIDATION_RULES["QUEST_04"] = VALIDATION_RULES["4"]
VALIDATION_RULES["QUEST_05"] = VALIDATION_RULES["5"]
VALIDATION_RULES["QUEST_06"] = VALIDATION_RULES["6"]
