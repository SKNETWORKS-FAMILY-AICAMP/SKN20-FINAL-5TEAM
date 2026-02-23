"""
[2026-02-21 대폭 개편]
의사코드 퀘스트별 추천 영상, 차원 우선순위, Deep Dive 패턴 통합 관리 서비스

[2026-02-22 추가]
- QUEST_BLUEPRINTS: 기초부터 배우기(청사진 모드)를 위한 정답 데이터
"""

import logging
import re

logger = logging.getLogger(__name__)


# ============================================================================
# 0. 기초부터 배우기 (청사진 모드) 데이터
# ============================================================================

QUEST_BLUEPRINTS = {
    '1': [
        { "id": "s1", "python": "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)", "pseudo": "먼저 데이터를 학습용과 검증용으로 물리적 격리(Isolation)한다.", "keywords": ["격리", "분리", "학습/검증", "Isolation"] },
        { "id": "s2", "python": "scaler.fit(X_train)", "pseudo": "학습 데이터(train)에서만 통계량을 추출하여 기준점(Anchor)을 설정한다.", "keywords": ["기준점", "학습데이터", "통계량", "fit"] },
        { "id": "s3", "python": "scaler.transform(X_test)", "pseudo": "테스트 데이터(test)에는 fit 없이 transform만 적용하여 일관성(Consistency)을 유지한다.", "keywords": ["일관성", "테스트데이터", "transform", "동일변환"] }
    ],
    '2': [
        { "id": "s1", "python": "model = Ridge(alpha=1.0)", "pseudo": "L2 정규화를 통해 모델의 계수 크기를 제어하여 과도한 가중치를 억제한다.", "keywords": ["정규화", "L2", "복잡도제어", "Ridge"] },
        { "id": "s2", "python": "model.fit(X_train, y_train)", "pseudo": "학습 데이터에서 정규화된 모델을 적합시켜 일반화 성능을 높인다.", "keywords": ["적합", "학습", "정규화"] },
        { "id": "s3", "python": "score_train vs score_test", "pseudo": "학습 데이터와 검증 데이터의 성능 차이를 모니터링하여 과적합 정도를 진단한다.", "keywords": ["모니터링", "성능차이", "과적합진단"] }
    ],
    '3': [
        { "id": "s1", "python": "print(y_train.value_counts())", "pseudo": "클래스 분포의 불균형을 진단하여 얼마나 심각한 문제인지 파악한다.", "keywords": ["진단", "분포확인", "불균형", "DetectImbalance"] },
        { "id": "s2", "python": "smote = SMOTE(); X_balanced, y_balanced = smote.fit_resample(X_train, y_train)", "pseudo": "SMOTE 기법을 사용하여 소수 클래스를 합성적으로 생성하고 균형을 맞춘다.", "keywords": ["샘플링", "SMOTE", "오버샘플링", "BalanceClass"] },
        { "id": "s3", "python": "roc_auc_score(y_test, pred_proba)", "pseudo": "정확도 대신 F1-Score, AUC-ROC 등 다중 평가 지표를 사용하여 공정한 성능 평가를 수행한다.", "keywords": ["평가지표", "F1", "AUC", "Precision"] }
    ],
    '4': [
        { "id": "s1", "python": "df['freq'] = df['count'] / df['days']", "pseudo": "원본 특성들을 조합하여 의미 있는 새로운 특성을 생성한다.", "keywords": ["생성", "조합", "도메인", "FeatureCreation"] },
        { "id": "s2", "python": "df['log_val'] = np.log1p(df['val'])", "pseudo": "로그 변환 등을 통해 특성의 분포를 개선하고 모델 학습을 촉진한다.", "keywords": ["변환", "정규화", "스케일링", "Transformation"] },
        { "id": "s3", "python": "model.feature_importances_", "pseudo": "특성 중요도를 분석하여 기여도가 낮은 특성을 제거하여 모델을 단순화한다.", "keywords": ["선택", "중요도", "제거", "Selection"] }
    ],
    '5': [
        { "id": "s1", "python": "param_grid = {'n_estimators': [50, 100], ...}", "pseudo": "튜닝할 하이퍼파라미터와 그 값의 범위를 정의한다.", "keywords": ["정의", "범위", "파라미터", "Space"] },
        { "id": "s2", "python": "GridSearchCV(..., cv=5)", "pseudo": "K-Fold 교차검증과 함께 그리드 탐색을 수행하여 성능을 평가한다.", "keywords": ["탐색", "교차검증", "조합", "Search"] },
        { "id": "s3", "python": "best_params = grid.best_params_", "pseudo": "가장 좋은 검증 성능을 보인 파라미터 조합을 추출하여 최종 모델에 적용한다.", "keywords": ["선택", "최적화", "확정", "Best"] }
    ],
    '6': [
        { "id": "s1", "python": "model.feature_importances_", "pseudo": "각 특성이 전체 의사결정에 미치는 영향도를 계산하는 전역적 해석을 수행한다.", "keywords": ["해석", "중요도", "특성", "Global"] },
        { "id": "s2", "python": "shap_values = explainer.shap_values(X_test)", "pseudo": "SHAP 같은 기법을 사용하여 특정 사례의 모델 예측을 개별적으로 해석한다.", "keywords": ["설명", "SHAP", "개별", "Local"] },
        { "id": "s3", "python": "performance_by_group", "pseudo": "보호되는 속성에 대해 모델의 성능 및 결정에 편향이 있는지 검증한다.", "keywords": ["검증", "편향", "공정성", "Bias"] }
    ]
}

QUEST_RECOVERY_QUESTIONS = {
    '1': {
        'question': '데이터 누수 방지를 위해 fit과 transform을 분리하는 이유 중 가장 적절한 것은?',
        'options': [
            {'text': '테스트 데이터의 통계량이 학습 데이터에 영향을 주지 않도록 하기 위해', 'is_correct': True, 'reason': '이것이 데이터 격리(Isolation)의 핵심 원칙입니다.'},
            {'text': '연산 속도를 더 빠르게 높이기 위해', 'is_correct': False, 'reason': '속도보다는 논리적 무결성이 우선입니다.'},
            {'text': '전체 데이터의 평균값을 더 정확하게 구하기 위해', 'is_correct': False, 'reason': '전체 데이터를 한꺼번에 계산하면 나중에 올 실제 데이터 예측 시 문제가 생깁니다.'}
        ]
    },
    '2': {
        'question': '릿지(Ridge) 회귀에서 알파(Alpha) 값이 커질 때 발생하는 현상은?',
        'options': [
            {'text': '계수(Weight)의 크기가 작아지며 모델이 더 단순해진다', 'is_correct': True, 'reason': '알파는 규제의 강도를 조절하여 과적합을 방지합니다.'},
            {'text': '모델이 학습 데이터에 더 완벽하게 밀착된다', 'is_correct': False, 'reason': '그것은 알파가 0에 가까울 때의 현상입니다.'},
            {'text': '계수들의 합이 항상 0이 된다', 'is_correct': False, 'reason': '계수를 줄이는 것이지 무조건 0으로 만드는 것은 아닙니다.'}
        ]
    },
    '3': {
        'question': '불균형 데이터를 다룰 때 정확도(Accuracy) 지표만 신뢰하면 안 되는 이유는?',
        'options': [
            {'text': '다수 클래스만 잘 맞추고 소수 클래스를 놓쳐도 높게 나올 수 있어서', 'is_correct': True, 'reason': '그래서 F1-Score나 AUC-ROC 같은 지표가 필수적입니다.'},
            {'text': '정확도는 계산 시간이 오래 걸려서', 'is_correct': False, 'reason': '정확도 계산은 매우 빠릅니다.'},
            {'text': '데이터가 적을 때는 정확도가 항상 0이 되어서', 'is_correct': False, 'reason': '데이터 양과 정확도의 관계는 상황에 따라 다릅니다.'}
        ]
    },
    '4': {
        'question': '특성 중요도(Feature Importance) 분석의 주된 목적은?',
        'options': [
            {'text': '모델의 의사결정에 가장 큰 영향을 준 변수를 파악하기 위해', 'is_correct': True, 'reason': '이를 통해 불필요한 변수를 제거하거나 도메인 인사이트를 얻습니다.'},
            {'text': '데이터의 결측치를 자동으로 채우기 위해', 'is_correct': False, 'reason': '결측치 처리는 전처리 단계에서 별도로 수행해야 합니다.'},
            {'text': '전체 학습 속도를 10배 이상 높이기 위해', 'is_correct': False, 'reason': '가독성과 해석력 향상이 주목적입니다.'}
        ]
    },
    '5': {
        'question': '그리드 탐색(Grid Search) 시 교차 검증(CV)을 함께 사용하는 이유는?',
        'options': [
            {'text': '특정 데이터 분할에만 운 좋게 잘 맞는 "우연"을 방지하기 위해', 'is_correct': True, 'reason': '데이터를 여러 개로 쪼개어 평균 성능을 보는 것이 더 강건합니다.'},
            {'text': '하이퍼파라미터의 범위를 자동으로 무한 확장하기 위해', 'is_correct': False, 'reason': '범위는 사용자가 직접 지정해야 합니다.'},
            {'text': '모델의 파이썬 코드를 더 짧게 만들기 위해', 'is_correct': False, 'reason': '코딩 스타일과는 무관한 성능 검증 기법입니다.'}
        ]
    },
    '6': {
        'question': 'SHAP 값(SHAP Value)이 우리에게 알려주는 핵심 정보는?',
        'options': [
            {'text': '특정 입력값이 모델의 예측 결과를 정답 대비 얼마나 변화시켰는가', 'is_correct': True, 'reason': '개별 사례에 대한 기여도를 정밀하게 분석할 수 있습니다.'},
            {'text': '모델이 사용하는 메모리 점유율', 'is_correct': False, 'reason': 'SHAP은 해석용 지표이지 하드웨어 지표가 아닙니다.'},
            {'text': '학습 데이터에 포함된 욕설이나 비속어 비율', 'is_correct': False, 'reason': '데이터 정제와는 다른 영역입니다.'}
        ]
    }
}


def get_quest_blueprint(quest_id: str) -> list:
    """Quest ID에 맞는 청사진 단계를 반환합니다."""
    return QUEST_BLUEPRINTS.get(str(quest_id), [])


import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 1. 차원별 우선순위 (퀘스트별로 다름 - 한 번에 하나씩 점검)
# ============================================================================

DIMENSION_PRIORITY_BY_QUEST = {
    '1': ['consistency', 'design', 'implementation', 'abstraction', 'edgeCase'],
    '2': ['design', 'consistency', 'implementation', 'edgeCase', 'abstraction'],
    '3': ['consistency', 'design', 'edgeCase', 'abstraction', 'implementation'],
    '4': ['design', 'implementation', 'consistency', 'abstraction', 'edgeCase'],
    '5': ['design', 'consistency', 'implementation', 'abstraction', 'edgeCase'],
    '6': ['abstraction', 'consistency', 'design', 'implementation', 'edgeCase'],
}

# 폴백 (Quest ID를 모를 때)
DEFAULT_DIMENSION_PRIORITY = ['consistency', 'design', 'implementation', 'abstraction', 'edgeCase']


# ============================================================================
# 2. YouTube 추천 영상 맵 (모든 차원이 [list] 구조로 통일)
# ============================================================================

QUEST_VIDEOS = {
    # ──────────────────────────────────────────────────────────
    # Quest 1: 데이터 누수 방어 시스템 설계
    # 우선순위: consistency > design > implementation > abstraction > edgeCase
    # ──────────────────────────────────────────────────────────
    1: {
        'consistency': [
            {'id': 'A88rDEf-pfk', 'title': 'Standardization vs Normalization — fit/transform (StatQuest)', 'channel': 'StatQuest'},
            {'id': 'fSytzGwwBVw', 'title': 'What is Data Leakage? (StatQuest)', 'channel': 'StatQuest'},
        ],
        'design': [
            {'id': 'fSytzGwwBVw', 'title': 'What is Data Leakage? (StatQuest)', 'channel': 'StatQuest'},
        ],
        'implementation': [
            {'id': 'rmEa9_8GKQY', 'title': 'Sklearn Pipeline으로 Data Leakage 방지 (Krish Naik)', 'channel': 'Krish Naik'},
        ],
        'abstraction': [
            {'id': 'gJo0uNL-5Lw', 'title': 'K-Fold Cross Validation (StatQuest)', 'channel': 'StatQuest'},
        ],
        'edgeCase': [
            {'id': 'Gmq7mXv6M-c', 'title': 'Saving & Loading ML Models — Pickle & Joblib (NeuralNine)', 'channel': 'NeuralNine'},
        ],
        'default': [
            {'id': 'fSytzGwwBVw', 'title': 'What is Data Leakage?', 'channel': 'StatQuest'},
            {'id': 'A88rDEf-pfk', 'title': 'Standardization vs Normalization', 'channel': 'StatQuest'},
            {'id': 'rmEa9_8GKQY', 'title': 'Sklearn Pipeline', 'channel': 'Krish Naik'},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # Quest 2: 과적합 방어 정규화 시스템 설계
    # 우선순위: design > consistency > implementation > edgeCase > abstraction
    # ──────────────────────────────────────────────────────────
    2: {
        'design': [
            {'id': 'Q81RR3yKn30', 'title': 'Ridge & Lasso Regularization 완전 이해 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'consistency': [
            {'id': 'EuBBz3bI-aA', 'title': 'Bias and Variance Tradeoff (StatQuest)', 'channel': 'StatQuest'},
        ],
        'implementation': [
            {'id': 'Q81RR3yKn30', 'title': 'Ridge & Lasso 구현 (sklearn) (StatQuest)', 'channel': 'StatQuest'},
        ],
        'edgeCase': [
            {'id': 'CRlYPodahlE', 'title': 'Early Stopping & Dropout (DeepLearningAI)', 'channel': 'DeepLearningAI'},
        ],
        'abstraction': [
            {'id': 'EuBBz3bI-aA', 'title': 'Underfitting & Overfitting 원리 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'default': [
            {'id': 'EuBBz3bI-aA', 'title': 'Bias and Variance', 'channel': 'StatQuest'},
            {'id': 'Q81RR3yKn30', 'title': 'Ridge & Lasso', 'channel': 'StatQuest'},
            {'id': 'CRlYPodahlE', 'title': 'Early Stopping & Dropout', 'channel': 'DeepLearningAI'},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # Quest 3: 불균형 데이터 처리 시스템 설계
    # 우선순위: consistency > design > edgeCase > abstraction > implementation
    # ──────────────────────────────────────────────────────────
    3: {
        'consistency': [
            {'id': '4jRBRDbJemM', 'title': 'ROC Curve & AUC — 불균형 평가의 표준 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'design': [
            {'id': 'geZDkTfGT-I', 'title': 'Imbalanced Data 처리 전략 설계 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'edgeCase': [
            {'id': 'pDw_JHHvj-0', 'title': 'Class Weights & Cost-Sensitive Learning (Krish Naik)', 'channel': 'Krish Naik'},
        ],
        'abstraction': [
            {'id': 'gJo0uNL-5Lw', 'title': 'StratifiedKFold & 계층화 분할 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'implementation': [
            {'id': 'U3X98xZ4_no', 'title': 'SMOTE 완전 구현 (imbalanced-learn)', 'channel': 'imbalanced-learn'},
        ],
        'default': [
            {'id': 'geZDkTfGT-I', 'title': 'Handling Imbalanced Data', 'channel': 'StatQuest'},
            {'id': '4jRBRDbJemM', 'title': 'ROC AUC', 'channel': 'StatQuest'},
            {'id': 'U3X98xZ4_no', 'title': 'SMOTE', 'channel': 'imbalanced-learn'},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # Quest 4: 피처 엔지니어링 최적화 설계
    # 우선순위: design > implementation > consistency > abstraction > edgeCase
    # ──────────────────────────────────────────────────────────
    4: {
        'design': [
            {'id': 'md8IrSMPi6o', 'title': 'Feature Engineering 실전 (Kaggle Course)', 'channel': 'Kaggle'},
        ],
        'implementation': [
            {'id': '68ABAU_V8qI', 'title': 'Feature Selection — RandomForest 중요도 분석 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'consistency': [
            {'id': 'A88rDEf-pfk', 'title': 'StandardScaler fit/transform 분리 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'abstraction': [
            {'id': 'viZrOnJclY0', 'title': 'Polynomial Features & 상호작용 특성 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'edgeCase': [
            {'id': 'FgakZw6K1QQ', 'title': 'Curse of Dimensionality & PCA (StatQuest)', 'channel': 'StatQuest'},
        ],
        'default': [
            {'id': 'md8IrSMPi6o', 'title': 'Feature Engineering', 'channel': 'Kaggle'},
            {'id': '68ABAU_V8qI', 'title': 'Feature Selection', 'channel': 'StatQuest'},
            {'id': 'FgakZw6K1QQ', 'title': 'Curse of Dimensionality', 'channel': 'StatQuest'},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # Quest 5: 하이퍼파라미터 튜닝 전략 설계
    # 우선순위: design > consistency > implementation > abstraction > edgeCase
    # ──────────────────────────────────────────────────────────
    5: {
        'design': [
            {'id': 'HdlDYng7g58', 'title': 'Hyperparameter Tuning — GridSearch vs RandomSearch (StatQuest)', 'channel': 'StatQuest'},
        ],
        'consistency': [
            {'id': 'gJo0uNL-5Lw', 'title': 'K-Fold Cross Validation — 튜닝 신뢰도 확보 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'implementation': [
            {'id': 'HdlDYng7g58', 'title': 'GridSearchCV 완전 구현 (sklearn)', 'channel': 'StatQuest'},
        ],
        'abstraction': [
            {'id': 'Np8h_U9PmFw', 'title': '파라미터 상호작용 & Warm-start (W&B)', 'channel': 'W&B'},
        ],
        'edgeCase': [
            {'id': 'Np8h_U9PmFw', 'title': 'Bayesian Optimization & Optuna — 효율적 탐색 (W&B)', 'channel': 'W&B'},
        ],
        'default': [
            {'id': 'HdlDYng7g58', 'title': 'Hyperparameter Tuning', 'channel': 'StatQuest'},
            {'id': 'gJo0uNL-5Lw', 'title': 'K-Fold Cross Validation', 'channel': 'StatQuest'},
            {'id': 'Np8h_U9PmFw', 'title': 'Bayesian Optimization', 'channel': 'W&B'},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # Quest 6: 모델 해석성과 설명가능성 설계
    # 우선순위: abstraction > consistency > design > implementation > edgeCase
    # ──────────────────────────────────────────────────────────
    6: {
        'abstraction': [
            {'id': 'B-c8tIgchu0', 'title': 'SHAP Values — 전역·개별 해석 설계 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'consistency': [
            {'id': 'B-c8tIgchu0', 'title': 'SHAP Summary Plot — 일관된 해석 기준 (StatQuest)', 'channel': 'StatQuest'},
        ],
        'design': [
            {'id': 'GfGpXMBjOBg', 'title': 'Counterfactual Explanation & Actionable AI (Google)', 'channel': 'Google'},
        ],
        'implementation': [
            {'id': 'C80SQe16Rao', 'title': 'LIME 구현 — 개별 예측 설명 (Towards Data Science)', 'channel': 'Towards Data Science'},
        ],
        'edgeCase': [
            {'id': 'GfGpXMBjOBg', 'title': 'AI Fairness & Proxy Bias 감지 (Google Developers)', 'channel': 'Google'},
        ],
        'default': [
            {'id': 'B-c8tIgchu0', 'title': 'SHAP Values', 'channel': 'StatQuest'},
            {'id': 'C80SQe16Rao', 'title': 'LIME', 'channel': 'Towards Data Science'},
            {'id': 'GfGpXMBjOBg', 'title': 'AI Fairness', 'channel': 'Google'},
        ],
    },
}

# ============================================================================
# 3. Deep Dive 시나리오 패턴 (꼬리질문 정답을 알아도 더 깊이 생각해야 함)
# ============================================================================

DEEP_DIVE_PATTERNS = {
    '1': {
        'title': '대규모 실시간 서빙 환경의 누수 대응',
        'pattern': '[대규모 실시간 서빙] {데이터 볼륨}, {시간 제약}의 환경에서 {역할}을 수행해야 할 때, 누수를 방지하려면?',
        'example_scenario': '[대규모 실시간 서빙] 매초 10만 건의 거래 데이터가 들어오는데, 모델 서빙 중 매주 재학습을 해야 합니다. 이전 주 데이터로 만든 Scaler를 새 주 데이터에 그대로 사용하면 문제가 생길까?',
        'model_answer': '예, 심각한 누수가 발생합니다. 새 주 데이터(분포가 변했을 수 있음)의 통계량을 학습 중에 포함하므로, Scaler를 주 단위로 재학습해야 합니다. 또는 데이터 드리프트를 모니터링하여 임계값을 넘으면 경고합니다.',
    },
    '2': {
        'title': '제약된 데이터에서의 과적합 대응 설계',
        'pattern': '[제약된 학습 데이터] {샘플 수}건, {특성 수}개의 데이터로 {요구 정확도}를 달성해야 할 때, 과적합 없이 신뢰도 높은 모델을 만들려면?',
        'example_scenario': '[제약된 학습 데이터] 학습셋 100건뿐인데, 검증 정확도 85% 이상을 달성해야 합니다. 정규화, K-Fold, 조기종료 중 어떤 조합이 가장 효과적일까?',
        'model_answer': 'K-Fold(cv=5)로 신뢰도 확보, L2 정규화(Ridge)는 약하게, 조기종료(EarlyStopping)로 과적합 시점 감지. 단, 데이터 부족 시 augmentation 고려. 최종 평가는 테스트셋이 아닌 k-fold 평균으로 신뢰성 판단.',
    },
    '3': {
        'title': '불균형 환경에서의 비용 민감 문제',
        'pattern': '[비용 불균형] 양성(거짓음성 cost={비용} 손실) vs 음성(거짓양성 cost={비용} 손실)의 불균형에서 {제약}을 만족하려면?',
        'example_scenario': '[비용 불균형] 이상 거래 1건 놓치면 $10,000 손실인데, 오탐지 1건은 $100 비용. 정확도 90%인 모델(불균형 고려 없음)은 신뢰할 수 있을까?',
        'model_answer': '아니요. class_weight="balanced"를 사용하거나 sample_weight로 비용을 반영. 임계값을 기본 0.5에서 더 높게 조정(0.7~0.8)하여 양성 예측을 보수적으로. ROC AUC로 평가해야 정확도의 함정을 피합니다.',
    },
    '4': {
        'title': '고차원 피처 공간에서의 차원의 저주',
        'pattern': '[차원 증가] {원시 특성 개수}에서 {파생 방식}으로 {결과 차원}까지 늘렸을 때, 성능이 {저하 패턴}이면 어떻게 대응할까?',
        'example_scenario': '[차원 증가] 원래 특성 5개에서 PolynomialFeatures(degree=2)로 20개로 늘렸더니 모델 성능이 하락했습니다. 원인은 무엇이고 해결책은?',
        'model_answer': '차원의 저주(동일 샘플 수로 공간 희소성 증가)와 과적합 위험 상승. 해결책: (1) PCA로 10개로 축소, (2) SelectKBest(f_classif, k=10)로 중요도 기반 선택, (3) L1 정규화(Lasso)로 자동 특성제거.',
    },
    '5': {
        'title': '하이퍼파라미터 상호작용과 효율적 탐색',
        'pattern': '[탐색 효율성] {파라미터 조합 수}개를 {예산 제약} 초과 없이 탐색할 때, n_estimators와 max_depth의 상호작용을 고려하려면?',
        'example_scenario': '[탐색 효율성] GridSearchCV(cv=5)로 100개 조합을 탐색하면 12시간이 걸립니다. Optuna를 쓰면 빠를까? n_estimators=1000은 max_depth를 낮게 해야 할까?',
        'model_answer': '예, Optuna(베이지안 최적화)로 40% 시간 단축 가능. n_estimators ↑ → max_depth는 ↓ (과적합 위험 완화). Warm-start 사용하여 이전 학습 상태 계승 가능.',
    },
    '6': {
        'title': '대리변수 차별(Proxy Bias)과 공정성 검증',
        'pattern': '[공정성 검증] {보호속성}이 모델 특성에 없는데도 {간접 차별}이 의심될 때, 편향을 감지하고 완화하려면?',
        'example_scenario': '[공정성 검증] 대출 승인 모델에서 성별은 특성에 없지만, 직업과 거주지로 간접 차별이 발생할 수 있습니다. 이를 감지하고 개선하려면?',
        'model_answer': 'SHAP로 각 속성의 기여도 시각화. 성별별 정확도 비교하여 disparity 추출. Proxy Bias 제거: (1) 의심 특성 제거(직업/거주지), (2) adversarial debiasing, (3) 보호속성별 모델 분리.',
    },
}


# ============================================================================
# 4. 검증 함수들
# ============================================================================

def get_dimension_priority(quest_id: str) -> list:
    """
    퀘스트별 차원 우선순위를 반환합니다.
    
    Args:
        quest_id: 퀘스트 ID (1~6, 또는 '1'~'6')
    
    Returns:
        차원을 우선순위 순으로 정렬한 리스트
    """
    quest_str = str(quest_id)
    return DIMENSION_PRIORITY_BY_QUEST.get(quest_str, DEFAULT_DIMENSION_PRIORITY)


def _enrich_video(video: dict) -> dict:
    """YouTube 영상 데이터에 thumbnail/url/videoId 필드를 자동 보충합니다."""
    vid = video.copy()
    video_id = vid.get('id', '') or vid.get('videoId', '')
    
    # [수정 2026-02-23] 섬네일 누락 방지 및 폴백 이미지 적용
    # mqdefault.jpg (320x180) 사용
    if video_id:
        vid['videoId'] = video_id
        vid['url'] = f'https://www.youtube.com/watch?v={video_id}'
        # 기존 thumbnail이 없거나 가짜(placeholder)인 경우에만 생성
        if not vid.get('thumbnail') or 'placeholder' in vid.get('thumbnail', ''):
            vid['thumbnail'] = f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
        
        # 정적 데이터의 'id' 필드를 'videoId'와 동기화
        if 'id' in vid:
            vid['id'] = video_id
    else:
        # 비디오 ID조차 없는 경우 (데이터 오류)
        vid['thumbnail'] = "https://coduck-assets.s3.ap-northeast-2.amazonaws.com/images/video_fallback.png"
        vid['url'] = "#"
        
    return vid


def get_quest_videos(quest_id: str) -> dict:
    """
    특정 퀘스트의 모든 영상 데이터를 반환합니다.
    
    Args:
        quest_id: 퀘스트 ID
    
    Returns:
        영상 맵 (차원명 -> [영상 리스트])
    """
    quest_int = int(quest_id) if isinstance(quest_id, str) else quest_id
    raw = QUEST_VIDEOS.get(quest_int, QUEST_VIDEOS[1])  # 기본값: Quest 1
    # 리스트의 각 영상에 thumbnail/url/videoId 자동 보추
    enriched = {}
    for key, videos in raw.items():
        if isinstance(videos, list):
            enriched[key] = [_enrich_video(v) for v in videos]
        else:
            enriched[key] = videos
    return enriched


def get_deep_dive_pattern(quest_id: str) -> dict:
    """
    특정 퀘스트의 Deep Dive 시나리오 패턴을 반환합니다.
    
    Args:
        quest_id: 퀘스트 ID
    
    Returns:
        패턴 데이터 (title, pattern, example_scenario, model_answer)
    """
    quest_str = str(quest_id)
    pattern = DEEP_DIVE_PATTERNS.get(quest_str)
    if not pattern:
        logger.warning(f"[quest_resources] Deep Dive Pattern for Quest {quest_id} not found")
        return {
            'title': '추가 학습 시나리오',
            'pattern': '[상황] 이전 문제의 핵심을 알고 있어도 더 복잡한 제약에서는 어떻게 대응하실 건가요?',
            'example_scenario': '실무 상황을 더 깊이 있게 분석하는 연습입니다.',
            'model_answer': '제시된 제약을 고려하여 설계 원칙을 응용하세요.',
        }
    return pattern


def validate_tail_question(tail_q: dict) -> tuple:
    """
    꼬리질문 데이터 구조를 검증합니다.
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    required_fields = ['context', 'question', 'options']
    for field in required_fields:
        if field not in tail_q:
            return False, f"Required field missing: {field}"
    
    # context: 단어 수 ≤ 5
    context_words = tail_q['context'].split()
    if len(context_words) > 5:
        logger.warning(f"[validate_tail_question] context 단어 수 초과: {len(context_words)}")
    
    # question: [상황] 또는 [사례] 시작 권장
    if not any(tail_q['question'].startswith(prefix) for prefix in ['[상황]', '[사례]', '[문제]']):
        logger.warning(f"[validate_tail_question] question이 '[상황]' 등으로 시작하지 않음")
    
    # options: 정확히 1개 is_correct
    correct_count = sum(1 for opt in tail_q['options'] if opt.get('is_correct', False))
    if correct_count != 1:
        return False, f"Expected exactly 1 correct option, found {correct_count}"
    
    # 모든 옵션에 reason 필드 필수
    for i, opt in enumerate(tail_q['options']):
        if 'reason' not in opt:
            return False, f"Option {i} missing 'reason' field"
    
    return True, None


def validate_deep_dive(deep_dive: dict) -> tuple:
    """
    Deep Dive 데이터 구조를 검증합니다.
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    required_fields = ['title', 'scenario', 'question', 'model_answer']
    for field in required_fields:
        if field not in deep_dive:
            return False, f"Required field missing: {field}"
    
    # scenario: 구체적/비추상적 확인
    if len(deep_dive['scenario']) < 20:
        logger.warning(f"[validate_deep_dive] scenario가 너무 짧음: {len(deep_dive['scenario'])} chars")
    
    return True, None


# ============================================================================
# 5. 폴백 데이터 생성 함수들
# ============================================================================

def generate_fallback_tail_question(context: str = "설계 원칙 확인") -> dict:
    """
    LLM이 tail_question을 생성하지 못할 때의 폴백 구조."""
    return {
        'context': context,
        'question': '[상황] 이전 설계에서 놓친 핵심 요소가 있다면 무엇일까요?',
        'options': [
            {
                'text': '설계 원칙의 실무 응용 및 제약 조건 고려',
                'is_correct': True,
                'reason': '설계만으로는 부족하며, 현업 환경(규모, 비용, 시간)의 제약을 반영해야 합니다.',
            },
            {
                'text': '코드 최적화 및 성능 튜닝',
                'is_correct': False,
                'reason': '성능은 부차적 고려사항입니다. 먼저 논리적 정확성과 일관성이 우선입니다.',
            },
            {
                'text': '학습 데이터 양 대폭 증가',
                'is_correct': False,
                'reason': '데이터 양의 증가만으로는 설계 오류를 보정할 수 없습니다.',
            },
            {
                'text': '더 복잡한 모델 아키텍처 도입',
                'is_correct': False,
                'reason': '복잡도가 높아지면 오히려 과적합과 유지보수 어려움이 증가합니다.',
            }
        ]
    }


def generate_fallback_deep_dive(quest_id: str) -> dict:
    """
    LLM이 deep_dive를 생성하지 못할 때의 폴백 구조."""
    pattern = get_deep_dive_pattern(quest_id)
    return {
        'title': pattern['title'],
        'scenario': pattern['example_scenario'],
        'question': pattern['pattern'],
        'model_answer': pattern['model_answer'],
    }


# ============================================================================
# 6. 하위호환성 유지 (learningResources.js 폴백 호출용)
# ============================================================================

def get_recommended_videos_legacy(
    quest_id: str, 
    dimensions: dict, 
    max_count: int = 3,
    quest_title: str = ""
) -> list:
    """
    [2026-02-23 업그레이드] 
    1. 정적 큐레이션 데이터(QUEST_VIDEOS) 매핑
    2. 데이터 부족 시 YouTube Search API를 통한 실시간 검색 폴백 수행
    """
    try:
        # quest_id 정규화: 'unit01_02' 같은 형태는 숫자 부분만 추출
        if isinstance(quest_id, str):
            # '언더스코어' 형태 (e.g., 'unit01_02' -> '2', 'unit01_04' -> '4')
            if '_' in quest_id:
                parts = quest_id.split('_')
                last_nums = re.findall(r'\d+', parts[-1])
                if last_nums:
                    n = int(last_nums[-1])
                    quest_id_normalized = str(n) if 1 <= n <= 6 else '1'
                else:
                    quest_id_normalized = '1'
            else:
                # 순수 숫자 (e.g., '2', '3')
                nums = re.findall(r'\d+', quest_id)
                quest_id_normalized = '1'
                for n_str in nums:
                    n = int(n_str)
                    if 1 <= n <= 6:
                        quest_id_normalized = str(n)
                        break
        else:
            n = int(quest_id) if quest_id else 1
            quest_id_normalized = str(n) if 1 <= n <= 6 else '1'
        
        quest_videos = get_quest_videos(quest_id_normalized)
        quest_int = int(quest_id_normalized)
        priority = get_dimension_priority(quest_id_normalized)
        
        # 취약 차원 정렬
        dim_ratios = []
        for dim in priority:
            d = dimensions.get(dim, {})
            pct = d.get('percentage', 100) if isinstance(d, dict) else 100
            dim_ratios.append((dim, pct))
        dim_ratios.sort(key=lambda x: x[1])
        
        # [수정일: 2026-02-23] 유튜브 큐레이션 동적화: 하이브리드 방식 (정적 1개 + 동적 2개)
        candidates = []
        used_ids = set()
        
        # 1. 정적 큐레이션 데이터에서 가장 취약한 차원의 영상을 1개만 무작위로 선택
        import random
        for dim, _ in dim_ratios:
            videos = quest_videos.get(dim, [])
            if videos and isinstance(videos, list):
                # 셔플하여 '하드코딩된 느낌' 방지
                random_video = random.choice(videos)
                candidates.append({**random_video, '_dim': dim, '_source': 'curated'})
                used_ids.add(random_video['id'])
                break # 1개만 뽑고 종료
        
        # 2. 부족한 부분(나머지 2개 이상)은 실시간 라이브 검색으로 채움
        from core.utils.youtube_helper import search_youtube_videos
        
        # 취약 지표(가장 점수 낮은 것) 추출
        weakest_dim = dim_ratios[0][0] if dim_ratios else 'default'
        
        # 검색 쿼리 정교화
        search_keywords = {
            'design': ['ML System Design', '머신러닝 파이프라인 설계'],
            'consistency': ['Data Leakage prevention', 'ML train test split fit transform'],
            'abstraction': ['Clean Code Machine Learning', 'ML Architecture Patterns'],
            'implementation': ['Scikit-learn tutorial', 'ML implementation step by step'],
            'edgeCase': ['MLOps Monitoring Data Drift', 'Handling ML outliers missing values']
        }
        
        quest_keyword = ""
        if "누수" in quest_title or quest_id_normalized == "1": quest_keyword = "Data Leakage"
        elif "과적합" in quest_title or "정규화" in quest_title or quest_id_normalized == "2": quest_keyword = "Regularization Ridge Lasso"
        elif "불균형" in quest_title or quest_id_normalized == "3": quest_keyword = "Imbalanced Data SMOTE"
        elif "피처" in quest_title or quest_id_normalized == "4": quest_keyword = "Feature Engineering Selection"
        elif "하이퍼" in quest_title or quest_id_normalized == "5": quest_keyword = "Hyperparameter Tuning GridSearch"
        elif "해석" in quest_title or quest_id_normalized == "6": quest_keyword = "Explainable AI SHAP LIME"

        base_keywords = search_keywords.get(weakest_dim, ["Machine Learning Tutorial"])
        search_query = f"{quest_keyword} {base_keywords[0]}"
        
        print(f"[QuestResources] 실시간 하이브리드 검색 수행: {search_query}")
        
        # 부족한 개수만큼 라이브 검색 수행 (기본 2개 이상)
        needed = max_count - len(candidates)
        if needed > 0:
            live_videos = search_youtube_videos(search_query, max_results=needed + 2) # 여유있게 검색
            for lv in live_videos:
                if len(candidates) >= max_count:
                    break
                vid_id = lv.get('videoId')
                if vid_id and vid_id not in used_ids:
                    candidates.append({
                        'id': vid_id,
                        'title': lv.get('title'),
                        'channel': lv.get('channelTitle'),
                        'desc': lv.get('description'),
                        'videoId': vid_id,
                        'url': lv.get('url'),
                        'thumbnail': lv.get('thumbnail'),
                        '_dim': f"live_{weakest_dim}",
                        '_source': 'live'
                    })
                    used_ids.add(vid_id)

        # 3. 그래도 부족하면 마지막으로 default 정적 데이터로 보완 (셔플 적용)
        if len(candidates) < max_count:
            default_videos = list(quest_videos.get('default', []))
            random.shuffle(default_videos)
            for video in default_videos:
                if len(candidates) >= max_count:
                    break
                if video['id'] not in used_ids:
                    candidates.append({**video, '_dim': 'default', '_source': 'fallback'})
                    used_ids.add(video['id'])
        
        # [2026-02-23] 최종 반환 전 존재하지 않는 영상 필터링
        from core.utils.youtube_helper import filter_valid_videos
        valid_candidates = filter_valid_videos(candidates)
        
        # 필터 후 부족한 경우 default로 보완
        if len(valid_candidates) < max_count:
            default_videos = list(quest_videos.get('default', []))
            random.shuffle(default_videos)
            for video in default_videos:
                if len(valid_candidates) >= max_count:
                    break
                vid = video.get('id') or video.get('videoId')
                if vid and vid not in {v.get('id') or v.get('videoId') for v in valid_candidates}:
                    valid_candidates.append({**video, '_dim': 'default', '_source': 'fallback_recheck'})
            # 보완된 것도 다시 검증
            valid_candidates = filter_valid_videos(valid_candidates)
        
        return valid_candidates
    except Exception as e:
        logger.error(f"[get_recommended_videos_legacy] Error: {e}")
        return []