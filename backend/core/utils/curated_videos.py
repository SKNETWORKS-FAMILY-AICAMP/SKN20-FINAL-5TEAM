QUEST_VIDEO_MAP = {
    # Quest 1: Data Leakage
    "Data Leakage": {
        "abstraction": {
            "title": "Data Leakage in Machine Learning: detailed explanation (StatQuest)",
            "url": "https://www.youtube.com/watch?v=MInqE1H7JbU",
            "thumbnail": "https://img.youtube.com/vi/MInqE1H7JbU/0.jpg",
            "description": "데이터 누수의 개념과 왜 발생하는지에 대한 이론적 설명입니다."
        },
        "design": {
            "title": "How to Prevent Data Leakage in ML Design",
            "url": "https://www.youtube.com/watch?v=xM_26L6vG1g",
            "thumbnail": "https://img.youtube.com/vi/xM_26L6vG1g/0.jpg",
            "description": "데이터 파이프라인 설계 단계에서 누수를 방지하는 전략입니다."
        },
        "implementation": {
            "title": "Scikit-Learn Pipelines to Prevent Data Leakage",
            "url": "https://www.youtube.com/watch?v=QF2b2n6J9a4",
            "thumbnail": "https://img.youtube.com/vi/QF2b2n6J9a4/0.jpg",
            "description": "Sklearn Pipeline을 사용하여 구현 단계에서 누수를 원천 차단하는 방법입니다."
        },
        "edgeCase": {
            "title": "Data Leakage Pitfalls: Time Series & Group Split",
            "url": "https://www.youtube.com/watch?v=8p6XAQYYXpI",
            "thumbnail": "https://img.youtube.com/vi/8p6XAQYYXpI/0.jpg",
            "description": "시계열 데이터나 그룹 데이터 분할 시 자주 발생하는 실수와 예외 케이스입니다."
        },
        "consistency": {
            "title": "Reliable Validation: Cross-Validation Done Right",
            "url": "https://www.youtube.com/watch?v=fSytzGwwBVw",
            "thumbnail": "https://img.youtube.com/vi/fSytzGwwBVw/0.jpg",
            "description": "일관된 모델 성능 평가를 위한 올바른 교차 검증 방법입니다."
        }
    },

    # Quest 2: Overfitting
    "Overfitting": {
        "abstraction": {
            "title": "Bias-Variance Tradeoff Explained (StatQuest)",
            "url": "https://www.youtube.com/watch?v=EuBBz3bI-aA",
            "thumbnail": "https://img.youtube.com/vi/EuBBz3bI-aA/0.jpg",
            "description": "과적합과 과소적합, 편향과 분산의 관계를 시각적으로 이해합니다."
        },
        "design": {
            "title": "Strategies to Handle Overfitting",
            "url": "https://www.youtube.com/watch?v=2f-851r5I98",
            "thumbnail": "https://img.youtube.com/vi/2f-851r5I98/0.jpg",
            "description": "모델 설계를 통해 과적합을 제어하는 다양한 전략입니다."
        },
        "implementation": {
            "title": "Regularization in Python (L1 & L2)",
            "url": "https://www.youtube.com/watch?v=Nm532d1fOaU",
            "thumbnail": "https://img.youtube.com/vi/Nm532d1fOaU/0.jpg",
            "description": "Lasso, Ridge 규제를 파이썬으로 직접 구현하여 과적합을 막는 방법입니다."
        },
        "edgeCase": {
            "title": "Early Stopping: When to Stop Training?",
            "url": "https://www.youtube.com/watch?v=wKzJ5eN2iX0",
            "thumbnail": "https://img.youtube.com/vi/wKzJ5eN2iX0/0.jpg",
            "description": "학습 조기 종료(Early Stopping) 시점 결정과 예외 상황 처리입니다."
        },
        "consistency": {
            "title": "Learning Curves for Model Diagnostics",
            "url": "https://www.youtube.com/watch?v=RmP7h25M8Hk",
            "thumbnail": "https://img.youtube.com/vi/RmP7h25M8Hk/0.jpg",
            "description": "학습 곡선을 통해 모델의 일관성과 성능 상태를 진단하는 방법입니다."
        }
    },

    # Quest 3: Imbalanced Data
    "Imbalanced Data": {
        "abstraction": {
            "title": "The Problem with Imbalanced Classes",
            "url": "https://www.youtube.com/watch?v=-Z178gGPjkE",
            "thumbnail": "https://img.youtube.com/vi/-Z178gGPjkE/0.jpg",
            "description": "불균형 데이터가 왜 문제인지, 정확도의 함정에 대해 알아봅니다."
        },
        "design": {
            "title": "Choosing Valid Metrics: AUC-ROC vs F1-Score",
            "url": "https://www.youtube.com/watch?v=4jRBRDbJemM",
            "thumbnail": "https://img.youtube.com/vi/4jRBRDbJemM/0.jpg",
            "description": "불균형 데이터 상황에서 올바른 평가지표를 설계/선택하는 방법입니다."
        },
        "implementation": {
            "title": "SMOTE for Imbalanced Classification in Python",
            "url": "https://www.youtube.com/watch?v=U3X98xZ4_no",
            "thumbnail": "https://img.youtube.com/vi/U3X98xZ4_no/0.jpg",
            "description": "SMOTE 등 오버샘플링 기법을 파이썬 코드로 구현해봅니다."
        },
        "edgeCase": {
            "title": "When SMOTE Goes Wrong: Oversampling Pitfalls",
            "url": "https://www.youtube.com/watch?v=DGLlnBN17Xk",
            "thumbnail": "https://img.youtube.com/vi/DGLlnBN17Xk/0.jpg",
            "description": "오버샘플링을 잘못 적용했을 때 발생하는 문제(소음 증폭 등)와 해결책입니다."
        },
        "consistency": {
            "title": "Stratified K-Fold for Imbalanced Data",
            "url": "https://www.youtube.com/watch?v=1d5o-hJgQyE",
            "thumbnail": "https://img.youtube.com/vi/1d5o-hJgQyE/0.jpg",
            "description": "데이터 비율을 유지하며 일관되게 검증하는 Stratified K-Fold 기법입니다."
        }
    },

    # Quest 4: Feature Engineering
    "Feature Engineering": {
        "abstraction": {
            "title": "Feature Engineering Concepts & Intuition",
            "url": "https://www.youtube.com/watch?v=d11chG7Z-ms",
            "thumbnail": "https://img.youtube.com/vi/d11chG7Z-ms/0.jpg",
            "description": "피처 엔지니어링이 모델 성능에 미치는 영향과 핵심 개념입니다."
        },
        "design": {
            "title": "Feature Selection Strategies",
            "url": "https://www.youtube.com/watch?v=EqLmLGEdF_k",
            "thumbnail": "https://img.youtube.com/vi/EqLmLGEdF_k/0.jpg",
            "description": "어떤 피처를 선택하고 어떤 피처를 버릴지 설계하는 전략입니다."
        },
        "implementation": {
            "title": "Feature Engineering with Pandas & Sklearn",
            "url": "https://www.youtube.com/watch?v=8p6XAQYYXpI", # Placeholder - replace with specific
            "thumbnail": "https://img.youtube.com/vi/8p6XAQYYXpI/0.jpg",
            "description": "Categorical Encoding, Scaling 등 실제 코드 구현 방법입니다."
        },
        "edgeCase": {
            "title": "Handling Outliers & Missing Values",
            "url": "https://www.youtube.com/watch?v=5U9B2d4Xg-E",
            "thumbnail": "https://img.youtube.com/vi/5U9B2d4Xg-E/0.jpg",
            "description": "이상치와 결측치 처리 시 주의할 점과 예외 상황 대처법입니다."
        },
        "consistency": {
            "title": "Feature Scaling: Standardization vs Normalization",
            "url": "https://www.youtube.com/watch?v=mnKm3YP56PY",
            "thumbnail": "https://img.youtube.com/vi/mnKm3YP56PY/0.jpg",
            "description": "데이터 분포의 일관성을 유지하기 위한 스케일링 기법 비교입니다."
        }
    },

    # Quest 5: Hyperparameter Tuning
    "Hyperparameter Tuning": {
        "abstraction": {
            "title": "Hyperparameters vs Parameters: What's the difference?",
            "url": "https://www.youtube.com/watch?v=VteS7C6fGpw",
            "thumbnail": "https://img.youtube.com/vi/VteS7C6fGpw/0.jpg",
            "description": "모델 파라미터와 하이퍼파라미터의 개념적 차이와 중요성입니다."
        },
        "design": {
            "title": "Grid Search vs Random Search vs Bayesian Optimization",
            "url": "https://www.youtube.com/watch?v=5nYqK-HaoKY",
            "thumbnail": "https://img.youtube.com/vi/5nYqK-HaoKY/0.jpg",
            "description": "튜닝 전략 설계: 그리드, 랜덤, 베이지안 최적화의 장단점 비교입니다."
        },
        "implementation": {
            "title": "Optuna Tutorial: Efficient Hyperparameter Tuning",
            "url": "https://www.youtube.com/watch?v=J_XdNk80k6g",
            "thumbnail": "https://img.youtube.com/vi/J_XdNk80k6g/0.jpg",
            "description": "최신 튜닝 라이브러리인 Optuna를 사용한 효율적인 구현 방법입니다."
        },
        "edgeCase": {
            "title": "Overfitting the Validation Set via Tuning",
            "url": "https://www.youtube.com/watch?v=F1ka6a13S9I",
            "thumbnail": "https://img.youtube.com/vi/F1ka6a13S9I/0.jpg",
            "description": "과도한 튜닝으로 인해 검증 세트에 과적합되는 문제를 방지하는 법입니다."
        },
        "consistency": {
            "title": "Reproducible ML: Random Seeds & Tuning",
            "url": "https://www.youtube.com/watch?v=2pWv7GOvuf0",
            "thumbnail": "https://img.youtube.com/vi/2pWv7GOvuf0/0.jpg",
            "description": "튜닝 결과의 재현성을 보장하기 위한 시드 설정과 일관성 유지법입니다."
        }
    },

    # Quest 6: Explainable AI
    "Explainable AI": {
        "abstraction": {
            "title": "Explainable AI (XAI) Concepts: SHAP & LIME",
            "url": "https://www.youtube.com/watch?v=9haIOplEIGM",
            "thumbnail": "https://img.youtube.com/vi/9haIOplEIGM/0.jpg",
            "description": "XAI의 필요성과 SHAP, LIME의 핵심 원리를 설명합니다."
        },
        "design": {
            "title": "Designing Interpretable Machine Learning Systems",
            "url": "https://www.youtube.com/watch?v=w6a8d6f5q4g",
            "thumbnail": "https://img.youtube.com/vi/w6a8d6f5q4g/0.jpg",
            "description": "해석 가능한 모델을 설계하기 위한 고려사항과 접근법입니다."
        },
        "implementation": {
            "title": "SHAP in Python: Visualizing Model Decisions",
            "url": "https://www.youtube.com/watch?v=VB9uV-x0o44",
            "thumbnail": "https://img.youtube.com/vi/VB9uV-x0o44/0.jpg",
            "description": "SHAP 라이브러리를 사용하여 모델의 예측을 시각화하고 해석하는 코드입니다."
        },
        "edgeCase": {
            "title": "Pitfalls of Interpretation Methods (LIME/SHAP)",
            "url": "https://www.youtube.com/watch?v=hUnRCxnydCc",
            "thumbnail": "https://img.youtube.com/vi/hUnRCxnydCc/0.jpg",
            "description": "해석 기법이 가질 수 있는 편향과 오류, 주의해야 할 예외 상황입니다."
        },
        "consistency": {
            "title": "Global vs Local Interpretability",
            "url": "https://www.youtube.com/watch?v=ZO5sK8y73lY",
            "thumbnail": "https://img.youtube.com/vi/ZO5sK8y73lY/0.jpg",
            "description": "모델 전체의 일관된 설명(Global)과 개별 예측 설명(Local)의 균형입니다."
        }
    }
}
