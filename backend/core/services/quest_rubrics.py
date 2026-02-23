"""
Quest별 평가 루브릭 (Anchor Samples + Dimension Checklists)
작성일: 2026-02-21

[목적]
- LLM 평가 일관성 확보를 위한 Quest별 맞춤 루브릭
- 각 Quest마다: 앵커 샘플 (Poor/Average/Good) + 5차원 체크리스트
- pseudocode_evaluator.py의 _build_prompts()에서 참조

[채점 철학]
- 0점 시작 → 체크리스트 충족 시 가산 (Additive Scoring)
- 감점 방식 사용 금지
"""

QUEST_RUBRICS = {
    # ================================================================
    # Quest 1: 전처리 데이터 누수 방어
    # 필수 키워드: 격리(Isolation), 기준점(Anchor), 일관성(Consistency)
    # ================================================================
    1: {
        "quest_name": "전처리 데이터 누수 방어 시스템 설계",
        "core_concepts": ["격리(Isolation)", "기준점(Anchor)", "일관성(Consistency)"],

        "anchors": {
            "poor": {
                "score_range": "0~20",
                "example": "데이터를 전처리하고 모델을 학습시킨다.",
                "why": "격리·기준점·일관성 모두 누락. 구체적 절차 없음. 데이터 누수 개념 자체를 이해하지 못한 수준."
            },
            "average": {
                "score_range": "21~54",
                "example": "1. train_test_split으로 데이터를 나눈다.\n2. 스케일러로 정규화한다.\n3. 모델을 학습시킨다.",
                "why": "격리(분리)는 언급했으나, fit 대상이 학습 데이터만이어야 한다는 기준점(Anchor)이 불명확. transform 분리도 누락."
            },
            "good": {
                "score_range": "55~70",
                "example": "1. train_test_split으로 학습/테스트 데이터를 물리적으로 격리한다.\n2. StandardScaler를 생성하고 학습 데이터(X_train)에만 fit하여 기준점을 설정한다.\n3. fit된 스케일러로 X_train을 transform한다.\n4. 동일한 스케일러로 X_test도 transform한다. (fit 없이!)\n5. 학습 환경과 동일한 전처리를 운영 환경에서도 유지하여 일관성을 확보한다.",
                "why": "격리·기준점·일관성 3원칙 모두 충족. fit/transform 분리가 명확하고, 운영 환경까지 고려."
            }
        },

        "dimension_checklists": {
            "design": {
                "max": 25,
                "items": [
                    {"desc": "train_test_split 또는 데이터 분리를 첫 번째 단계로 명시", "points": 8},
                    {"desc": "fit은 학습 데이터(X_train)에만 수행한다고 명시", "points": 7},
                    {"desc": "transform을 학습/테스트 모두에 적용한다고 명시", "points": 5},
                    {"desc": "전체 흐름이 논리적 순서(분리→fit→transform)로 구성", "points": 5},
                ]
            },
            "consistency": {
                "max": 20,
                "items": [
                    {"desc": "동일한 스케일러 객체를 학습/테스트에 공유한다고 명시", "points": 7},
                    {"desc": "학습 환경과 운영(서빙) 환경의 전처리 일관성 언급", "points": 7},
                    {"desc": "fit_transform을 전체 데이터에 쓰면 안 된다는 인식 표현", "points": 6},
                ]
            },
            "abstraction": {
                "max": 15,
                "items": [
                    {"desc": "격리·기준점·일관성 3원칙을 개념적으로 구분하여 서술", "points": 6},
                    {"desc": "파이프라인/워크플로우 수준의 추상화 (단계별 모듈화)", "points": 5},
                    {"desc": "재사용 가능한 구조 언급 (함수화, 클래스화 등)", "points": 4},
                ]
            },
            "edgeCase": {
                "max": 15,
                "items": [
                    {"desc": "새로운 데이터(운영 환경) 유입 시 대응 언급", "points": 5},
                    {"desc": "결측치·이상치 등 전처리 전 데이터 품질 고려", "points": 5},
                    {"desc": "스케일러 저장/로드(직렬화) 또는 데이터 드리프트 언급", "points": 5},
                ]
            },
            "implementation": {
                "max": 10,
                "items": [
                    {"desc": "sklearn 등 구체적 라이브러리/함수명 사용", "points": 4},
                    {"desc": "변수명이 명확하고 코드로 직역 가능한 수준", "points": 3},
                    {"desc": "단계별 주석이나 설명이 충분", "points": 3},
                ]
            }
        }
    },

    # ================================================================
    # Quest 2: 과적합 방어 정규화 시스템 설계
    # 필수 키워드: 복잡도 제어, 특성 선택, 성능 모니터링
    # ================================================================
    2: {
        "quest_name": "과적합 방어 정규화 시스템 설계",
        "core_concepts": ["복잡도 제어(Complexity Control)", "특성 선택(Feature Selection)", "성능 모니터링(Performance Monitoring)"],

        "anchors": {
            "poor": {
                "score_range": "0~20",
                "example": "정규화를 적용하고 모델을 학습시킨다.",
                "why": "어떤 정규화인지, 왜 필요한지, 모니터링 방법 모두 누락. 과적합 개념 이해 부족."
            },
            "average": {
                "score_range": "21~54",
                "example": "1. Ridge 정규화를 적용한다.\n2. 불필요한 특성을 제거한다.\n3. 모델 성능을 확인한다.",
                "why": "3가지 핵심 개념을 언급했으나 각각이 피상적. alpha 조정 방법, 특성 선택 기준, 모니터링 지표가 불명확."
            },
            "good": {
                "score_range": "55~70",
                "example": "1. 학습 데이터의 R² 스코어와 검증 데이터의 R² 스코어 차이를 비교하여 과적합 정도를 진단한다.\n2. L2 정규화(Ridge, alpha=1.0)를 적용하여 가중치 크기를 제한하고 모델 복잡도를 제어한다.\n3. L1 정규화(Lasso)로 계수가 0에 가까운 불필요한 특성을 자동 제거한다.\n4. 학습 곡선(learning curve)을 그려 학습/검증 성능을 동시에 모니터링하며 최적의 alpha를 선택한다.\n5. 조기종료(Early Stopping)를 적용하여 검증 손실이 증가하면 학습을 중단한다.",
                "why": "복잡도 제어·특성 선택·모니터링 모두 구체적. 진단→처방→검증 흐름이 명확."
            }
        },

        "dimension_checklists": {
            "design": {
                "max": 25,
                "items": [
                    {"desc": "과적합 진단 단계를 먼저 수행 (학습/검증 성능 비교)", "points": 7},
                    {"desc": "L1/L2/ElasticNet 등 구체적 정규화 기법 명시", "points": 7},
                    {"desc": "정규화 강도(alpha) 조정 전략 언급", "points": 6},
                    {"desc": "진단→정규화→검증의 논리적 흐름", "points": 5},
                ]
            },
            "consistency": {
                "max": 20,
                "items": [
                    {"desc": "학습/검증 데이터 분리 후 동일 조건에서 비교", "points": 7},
                    {"desc": "정규화 적용 전후 성능을 동일 지표로 비교", "points": 7},
                    {"desc": "교차검증 등 안정적 평가 방법 사용", "points": 6},
                ]
            },
            "abstraction": {
                "max": 15,
                "items": [
                    {"desc": "복잡도 제어·특성 선택·모니터링을 개념적으로 분리하여 서술", "points": 6},
                    {"desc": "정규화를 '모델 복잡도 제한'이라는 상위 개념으로 설명", "points": 5},
                    {"desc": "Bias-Variance Tradeoff 개념 언급", "points": 4},
                ]
            },
            "edgeCase": {
                "max": 15,
                "items": [
                    {"desc": "과소적합(Underfitting) 가능성도 함께 고려", "points": 5},
                    {"desc": "alpha가 너무 크면 성능이 오히려 떨어진다는 인식", "points": 5},
                    {"desc": "조기종료(Early Stopping) 또는 드롭아웃 언급", "points": 5},
                ]
            },
            "implementation": {
                "max": 10,
                "items": [
                    {"desc": "Ridge/Lasso/ElasticNet 등 구체적 클래스명 사용", "points": 4},
                    {"desc": "GridSearchCV 등 튜닝 도구 언급", "points": 3},
                    {"desc": "코드로 직역 가능한 구체적 파라미터 명시", "points": 3},
                ]
            }
        }
    },

    # ================================================================
    # Quest 3: 불균형 데이터 처리 시스템 설계
    # 필수 키워드: 불균형 진단, 샘플링 전략, 공정한 평가
    # ================================================================
    3: {
        "quest_name": "불균형 데이터 처리 시스템 설계",
        "core_concepts": ["불균형 진단(Imbalance Detection)", "샘플링 전략(Sampling Strategy)", "공정한 평가(Fair Evaluation)"],

        "anchors": {
            "poor": {
                "score_range": "0~20",
                "example": "데이터를 오버샘플링하고 모델을 학습시킨다.",
                "why": "왜 오버샘플링이 필요한지 진단 없음. 평가 지표 선택도 누락. 불균형 문제의 본질 이해 부족."
            },
            "average": {
                "score_range": "21~54",
                "example": "1. 클래스 분포를 확인하여 불균형을 진단한다.\n2. SMOTE로 소수 클래스를 늘린다.\n3. F1-Score로 평가한다.",
                "why": "3가지 요소를 언급했으나, SMOTE 적용 시점(학습 데이터에만), 평가 지표 선택 이유가 불명확."
            },
            "good": {
                "score_range": "55~70",
                "example": "1. y_train.value_counts()로 클래스 비율을 확인하고 불균형 심각도를 수치로 진단한다.\n2. 학습 데이터에만 SMOTE를 적용하여 소수 클래스를 합성 생성한다. (테스트 데이터는 절대 리샘플링하지 않는다)\n3. 정확도 대신 Precision, Recall, F1-Score, AUC-ROC를 사용하여 소수 클래스 탐지 능력을 평가한다.\n4. class_weight='balanced'를 설정하여 비용 민감 학습도 병행한다.\n5. Stratified K-Fold로 각 폴드에서도 클래스 비율을 유지한다.",
                "why": "진단→처리→평가 흐름이 완벽. SMOTE 적용 범위(학습만), 다중 평가 지표, 계층화 분할까지 고려."
            }
        },

        "dimension_checklists": {
            "design": {
                "max": 25,
                "items": [
                    {"desc": "클래스 분포 확인/진단 단계를 먼저 수행", "points": 7},
                    {"desc": "SMOTE/오버샘플링/언더샘플링 등 구체적 기법 명시", "points": 7},
                    {"desc": "리샘플링을 학습 데이터에만 적용한다고 명시", "points": 6},
                    {"desc": "진단→샘플링→평가의 논리적 흐름", "points": 5},
                ]
            },
            "consistency": {
                "max": 20,
                "items": [
                    {"desc": "테스트 데이터는 리샘플링하지 않는다는 원칙 명시", "points": 8},
                    {"desc": "Stratified Split/K-Fold로 클래스 비율 유지 언급", "points": 7},
                    {"desc": "학습과 평가에서 동일한 평가 지표 사용", "points": 5},
                ]
            },
            "abstraction": {
                "max": 15,
                "items": [
                    {"desc": "불균형 진단·샘플링·평가를 단계별로 분리하여 서술", "points": 6},
                    {"desc": "'정확도의 함정' 또는 다수 클래스 편향 개념 설명", "points": 5},
                    {"desc": "비즈니스 관점의 비용 분석 (미탐지 vs 오탐지)", "points": 4},
                ]
            },
            "edgeCase": {
                "max": 15,
                "items": [
                    {"desc": "극단적 불균형(0.1% 미만) 시 추가 대응 언급", "points": 5},
                    {"desc": "class_weight 또는 비용 민감 학습(Cost-sensitive) 언급", "points": 5},
                    {"desc": "임계값(threshold) 조정 전략 언급", "points": 5},
                ]
            },
            "implementation": {
                "max": 10,
                "items": [
                    {"desc": "imblearn, SMOTE 등 구체적 라이브러리 사용", "points": 4},
                    {"desc": "precision_recall_fscore_support, roc_auc_score 등 함수명", "points": 3},
                    {"desc": "코드로 직역 가능한 수준의 구체성", "points": 3},
                ]
            }
        }
    },

    # ================================================================
    # Quest 4: 피처 엔지니어링 최적화 설계
    # 필수 키워드: 특성 창조, 특성 변환, 특성 선택
    # ================================================================
    4: {
        "quest_name": "피처 엔지니어링 최적화 설계",
        "core_concepts": ["특성 창조(Feature Creation)", "특성 변환(Feature Transformation)", "특성 선택(Feature Selection)"],

        "anchors": {
            "poor": {
                "score_range": "0~20",
                "example": "특성을 만들고 모델에 넣는다.",
                "why": "어떤 특성을 왜 만드는지, 변환과 선택 과정이 전혀 없음. 피처 엔지니어링 개념 부재."
            },
            "average": {
                "score_range": "21~54",
                "example": "1. 구매금액과 방문횟수를 조합하여 새 특성을 만든다.\n2. 로그 변환을 적용한다.\n3. 중요도가 낮은 특성을 제거한다.",
                "why": "3단계 흐름은 있으나 도메인 지식 기반의 구체적 파생 특성, 변환 이유, 선택 기준이 모호."
            },
            "good": {
                "score_range": "55~70",
                "example": "1. 도메인 지식을 활용하여 파생 특성을 창조한다: 구매빈도=구매횟수/가입일수, 최근활동여부=(오늘-마지막방문일)<30, 참여점수=구매금액×방문횟수.\n2. 구매금액처럼 분포가 치우친 특성에 로그 변환(log1p)을 적용하고, StandardScaler로 모든 수치형 특성을 정규화한다.\n3. RandomForest의 feature_importances_로 중요도를 분석하여 기여도 0.05 미만인 특성을 제거한다.\n4. 특성 간 상관관계를 확인하여 다중공선성이 높은 특성도 제거한다.",
                "why": "도메인 기반 창조, 분포 분석 후 변환, 중요도 기반 선택 + 다중공선성까지 고려. 구체적이고 체계적."
            }
        },

        "dimension_checklists": {
            "design": {
                "max": 25,
                "items": [
                    {"desc": "도메인 지식 기반의 구체적 파생 특성 2개 이상 제시", "points": 8},
                    {"desc": "특성 변환 방법(로그, 정규화 등)과 그 이유 명시", "points": 7},
                    {"desc": "특성 선택 기준(중요도, 상관관계 등) 명시", "points": 5},
                    {"desc": "창조→변환→선택의 논리적 순서", "points": 5},
                ]
            },
            "consistency": {
                "max": 20,
                "items": [
                    {"desc": "스케일링을 학습 데이터 기준으로 수행(fit on train)", "points": 7},
                    {"desc": "특성 변환 전후 분포 비교 또는 검증 언급", "points": 7},
                    {"desc": "학습/테스트/운영 환경에서 동일한 변환 적용", "points": 6},
                ]
            },
            "abstraction": {
                "max": 15,
                "items": [
                    {"desc": "창조·변환·선택을 독립적 단계로 분리하여 서술", "points": 6},
                    {"desc": "도메인 지식의 역할을 개념적으로 설명", "points": 5},
                    {"desc": "특성 품질이 모델 성능에 미치는 영향 설명", "points": 4},
                ]
            },
            "edgeCase": {
                "max": 15,
                "items": [
                    {"desc": "다중공선성(Multicollinearity) 처리 언급", "points": 5},
                    {"desc": "차원의 저주(Curse of Dimensionality) 인식", "points": 5},
                    {"desc": "카테고리형 변수 인코딩(OneHot, Label 등) 언급", "points": 5},
                ]
            },
            "implementation": {
                "max": 10,
                "items": [
                    {"desc": "np.log1p, StandardScaler, feature_importances_ 등 구체적 함수", "points": 4},
                    {"desc": "파생 특성의 수식을 명시 (예: freq = count / days)", "points": 3},
                    {"desc": "코드로 직역 가능한 수준", "points": 3},
                ]
            }
        }
    },

    # ================================================================
    # Quest 5: 하이퍼파라미터 튜닝 전략 설계
    # 필수 키워드: 파라미터 공간, 탐색 전략, 교차검증
    # ================================================================
    5: {
        "quest_name": "하이퍼파라미터 튜닝 전략 설계",
        "core_concepts": ["파라미터 공간(Parameter Space)", "탐색 전략(Search Strategy)", "교차검증(Cross-Validation)"],

        "anchors": {
            "poor": {
                "score_range": "0~20",
                "example": "하이퍼파라미터를 조정하고 최적의 값을 찾는다.",
                "why": "어떤 파라미터를, 어떤 범위에서, 어떤 방법으로 탐색하는지 전혀 없음."
            },
            "average": {
                "score_range": "21~54",
                "example": "1. n_estimators와 max_depth의 범위를 정한다.\n2. GridSearchCV로 탐색한다.\n3. 가장 좋은 조합을 선택한다.",
                "why": "기본 흐름은 있으나 파라미터 범위의 근거, 탐색 전략 선택 이유, K-Fold 설정이 모호."
            },
            "good": {
                "score_range": "55~70",
                "example": "1. 튜닝 대상 파라미터와 범위를 정의한다: n_estimators=[50,100,200], max_depth=[5,10,15,20], min_samples_split=[2,5,10].\n2. 파라미터 조합 수가 36개이므로 GridSearchCV를 선택한다. (100개 이상이면 RandomizedSearchCV 사용)\n3. cv=5 (5-Fold 교차검증)로 설정하여 각 조합의 안정적 성능을 평가한다.\n4. scoring='f1_weighted'로 비즈니스에 맞는 평가 지표를 지정한다.\n5. best_params_로 최적 조합을 추출하고, 테스트 데이터로 최종 검증한다.",
                "why": "파라미터 공간의 구체적 정의, 탐색 전략 선택의 논리적 근거, 교차검증 설정까지 체계적."
            }
        },

        "dimension_checklists": {
            "design": {
                "max": 25,
                "items": [
                    {"desc": "튜닝할 파라미터 2개 이상과 구체적 범위를 딕셔너리/리스트로 정의", "points": 8},
                    {"desc": "GridSearch/RandomSearch/Bayesian 중 전략 선택과 이유 명시", "points": 7},
                    {"desc": "K-Fold 교차검증 설정 (K값, scoring 지표)", "points": 5},
                    {"desc": "정의→탐색→선택→검증의 논리적 흐름", "points": 5},
                ]
            },
            "consistency": {
                "max": 20,
                "items": [
                    {"desc": "교차검증으로 과적합 없이 일관된 평가를 수행", "points": 8},
                    {"desc": "학습/검증/테스트 분리 원칙 준수", "points": 7},
                    {"desc": "동일한 scoring 지표로 모든 조합을 비교", "points": 5},
                ]
            },
            "abstraction": {
                "max": 15,
                "items": [
                    {"desc": "파라미터 공간·탐색·검증을 단계별로 분리하여 서술", "points": 6},
                    {"desc": "탐색 전략 간 트레이드오프(정확도 vs 효율) 설명", "points": 5},
                    {"desc": "파라미터 상호작용 또는 의존성 인식", "points": 4},
                ]
            },
            "edgeCase": {
                "max": 15,
                "items": [
                    {"desc": "파라미터 조합이 많을 때 효율적 탐색 전략 (Random, Bayesian)", "points": 5},
                    {"desc": "계산 비용/시간 제약 고려", "points": 5},
                    {"desc": "조기종료(HalvingGridSearch) 또는 Optuna/베이지안 언급", "points": 5},
                ]
            },
            "implementation": {
                "max": 10,
                "items": [
                    {"desc": "GridSearchCV/RandomizedSearchCV 등 구체적 클래스명", "points": 4},
                    {"desc": "param_grid 딕셔너리의 구체적 형태 제시", "points": 3},
                    {"desc": "best_params_, best_estimator_ 등 결과 추출 방법", "points": 3},
                ]
            }
        }
    },

    # ================================================================
    # Quest 6: 모델 해석성과 설명가능성 설계
    # 필수 키워드: 전역적 해석, 개별적 해석, 공정성 검증
    # ================================================================
    6: {
        "quest_name": "모델 해석성과 설명가능성 설계",
        "core_concepts": ["전역적 해석(Global Interpretation)", "개별적 해석(Local Interpretation)", "공정성 검증(Fairness Validation)"],

        "anchors": {
            "poor": {
                "score_range": "0~20",
                "example": "모델의 결과를 해석하고 설명한다.",
                "why": "어떤 방법으로 해석하는지, 전역/개별 구분 없음. 공정성 검증도 완전 누락."
            },
            "average": {
                "score_range": "21~54",
                "example": "1. 특성 중요도를 확인한다.\n2. SHAP으로 개별 예측을 해석한다.\n3. 편향이 없는지 확인한다.",
                "why": "3가지 요소를 언급했으나, 중요도 계산 방법, SHAP 적용 대상, 편향 검증의 구체적 방법이 모호."
            },
            "good": {
                "score_range": "55~70",
                "example": "1. feature_importances_로 모델 전체에서 어떤 특성이 의사결정에 가장 큰 영향을 미치는지 전역적 해석을 수행한다.\n2. SHAP TreeExplainer를 사용하여 특정 고객의 대출 거절 이유를 개별적으로 해석한다. (어떤 특성이 얼마만큼 거절에 기여했는지)\n3. 보호 속성(성별, 연령 등) 기준으로 그룹별 승인율을 비교하여 모델의 공정성을 검증한다.\n4. 대리 변수(Proxy) 편향도 체크하여 간접적 차별을 감지한다.\n5. 반사실적 설명(Counterfactual)으로 '무엇을 바꾸면 승인될 수 있는지' 제시한다.",
                "why": "전역·개별·공정성 3가지 해석을 구체적 기법과 함께 완벽하게 커버. Proxy와 Counterfactual까지 고급 개념."
            }
        },

        "dimension_checklists": {
            "design": {
                "max": 25,
                "items": [
                    {"desc": "전역적 해석 방법(feature_importances_, permutation importance 등) 명시", "points": 8},
                    {"desc": "개별적 해석 방법(SHAP, LIME 등) 명시", "points": 7},
                    {"desc": "공정성 검증 방법(그룹별 성능 비교 등) 명시", "points": 5},
                    {"desc": "전역→개별→공정성의 논리적 흐름", "points": 5},
                ]
            },
            "consistency": {
                "max": 20,
                "items": [
                    {"desc": "동일한 모델에 대해 여러 해석 기법을 일관되게 적용", "points": 7},
                    {"desc": "해석 결과를 검증 데이터에서도 확인", "points": 7},
                    {"desc": "해석 결과가 모델 성능과 일치하는지 교차 확인", "points": 6},
                ]
            },
            "abstraction": {
                "max": 15,
                "items": [
                    {"desc": "전역/개별/공정성을 서로 다른 수준의 해석으로 구분", "points": 6},
                    {"desc": "블랙박스 vs 글래스박스 트레이드오프 인식", "points": 5},
                    {"desc": "규제/윤리/비즈니스 관점의 설명가능성 필요성 언급", "points": 4},
                ]
            },
            "edgeCase": {
                "max": 15,
                "items": [
                    {"desc": "대리 변수(Proxy Bias) 또는 간접적 차별 감지 언급", "points": 5},
                    {"desc": "반사실적 설명(Counterfactual Explanation) 언급", "points": 5},
                    {"desc": "모델 업데이트 시 해석 결과도 갱신해야 한다는 인식", "points": 5},
                ]
            },
            "implementation": {
                "max": 10,
                "items": [
                    {"desc": "shap.TreeExplainer, shap.force_plot 등 구체적 함수명", "points": 4},
                    {"desc": "보호 속성 기준 그룹화 코드 수준의 구체성", "points": 3},
                    {"desc": "시각화(force_plot, summary_plot 등) 언급", "points": 3},
                ]
            }
        }
    },
}


def get_rubric_for_prompt(quest_id: int) -> str:
    """
    Quest ID에 해당하는 루브릭을 LLM 프롬프트용 텍스트로 변환.
    _build_prompts()에서 호출.
    """
    rubric = QUEST_RUBRICS.get(quest_id)
    if not rubric:
        return ""

    lines = []

    # 1. 핵심 개념
    lines.append(f"[이 미션의 핵심 개념]: {', '.join(rubric['core_concepts'])}")
    lines.append("")

    # 2. 앵커 샘플
    lines.append("[점수 앵커 — 반드시 이 기준에 맞춰 채점하십시오]")
    for level, data in rubric["anchors"].items():
        label = {"poor": "Poor", "average": "Average", "good": "Good"}[level]
        lines.append(f"  ● {label} (LLM {data['score_range']}점):")
        lines.append(f"    답변 예시: \"{data['example']}\"")
        lines.append(f"    판정 근거: {data['why']}")
        lines.append("")

    # 3. 차원별 체크리스트
    lines.append("[가산식 채점 체크리스트 — 0점에서 시작하여 충족 시 가산]")
    for dim, info in rubric["dimension_checklists"].items():
        lines.append(f"  ▸ {dim} ({info['max']}점 만점):")
        for item in info["items"]:
            lines.append(f"    □ {item['desc']} → +{item['points']}점")
        lines.append("")

    return "\n".join(lines)


def extract_quest_id_from_title(quest_title: str) -> int:
    """quest_title에서 Quest ID를 추출. 매칭 실패 시 0 반환."""
    title_map = {
        "데이터 누수": 1, "누수 방어": 1, "LEAKAGE": 1,
        "과적합": 2, "정규화": 2, "OVERFITTING": 2, "OVERFIT": 2,
        "불균형": 3, "IMBALANCE": 3, "BALANCE": 3,
        "피처": 4, "특성": 4, "FEATURE": 4,
        "하이퍼파라미터": 5, "튜닝": 5, "HYPERPARAMETER": 5, "TUNING": 5,
        "해석": 6, "설명가능": 6, "EXPLAINABILITY": 6, "EXPLAIN": 6,
    }
    upper_title = quest_title.upper()
    for keyword, qid in title_map.items():
        if keyword.upper() in upper_title:
            return qid
    return 0
