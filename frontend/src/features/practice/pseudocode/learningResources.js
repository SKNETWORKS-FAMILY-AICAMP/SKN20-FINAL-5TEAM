/**
 * learningResources.js - 챕터 × 취약 차원 기반 유튜브 큐레이션
 * 수정일: 2026-02-20
 *
 * [설계 원칙]
 * stages.js의 각 quest별 checklist, deepDiveScenarios.scoringKeywords,
 * blueprintSteps 키워드를 직접 반영하여 큐레이션.
 *
 * 구조: QUEST_VIDEOS[questId][dimension] = [영상 배열]
 *   - questId  : stages.js의 id (1~6)
 *   - dimension: 'design' | 'consistency' | 'implementation' | 'edgeCase' | 'abstraction'
 *   - default  : 차원별 영상이 부족할 때 보완용
 *
 * 추천 로직:
 *   취약한 차원 순서대로 해당 챕터의 dimension 영상 선택
 *   → 3개 미달 시 default로 보완
 */

const QUEST_VIDEOS = {

    // ══════════════════════════════════════════════════════════════════
    // Quest 1: 전처리 데이터 누수 방어 시스템 설계
    // checklist : 격리(Isolation) / 기준점(Anchor) / 일관성(Consistency)
    // deepDive  : Pickle·Joblib·직렬화 / K-Fold·Stratified·교차검증 / 모니터링·재학습·Retraining
    // blueprint : train_test_split → scaler.fit(X_train) → scaler.transform(X_test)
    // ══════════════════════════════════════════════════════════════════
    1: {
        // 설계력 부족: 격리→fit→transform 순서 설계 자체를 모름
        design: [
            {
                id: 'fSytzGwwBVw',
                title: 'What is Data Leakage? (StatQuest)',
                desc: '데이터 누수가 왜 발생하는지, 어떤 설계 순서가 올바른지 시각적으로 설명합니다.',
                reason: '격리(Isolation) → fit → transform 순서의 설계 원칙을 처음부터 다시 확인하세요.',
            },
        ],
        // 정합성 부족: train fit / test transform-only 일관성 미준수
        consistency: [
            {
                id: 'A88rDEf-pfk',
                title: 'Standardization vs Normalization — fit/transform 순서 (StatQuest)',
                desc: 'fit()을 어느 데이터에 해야 하는지, transform은 왜 동일 기준점으로 해야 하는지 설명합니다.',
                reason: '기준점(Anchor)을 학습셋에만 고정하고 테스트셋엔 transform만 적용하는 일관성 원칙을 점검하세요.',
            },
        ],
        // 구현력 부족: sklearn Pipeline으로 누수 구조적 차단
        implementation: [
            {
                id: 'rmEa9_8GKQY',
                title: 'Sklearn Pipeline으로 Data Leakage 방지 (Krish Naik)',
                desc: 'Pipeline을 사용하면 교차검증 루프 안에서도 fit이 train에만 적용되어 구조적으로 누수를 막습니다.',
                reason: '코드 구현 수준에서 누수를 원천 차단하는 Pipeline 패턴을 학습하세요.',
            },
        ],
        // 예외처리 부족: 실시간 서빙 환경의 직렬화(Pickle/Joblib), 데이터 드리프트 대응
        edgeCase: [
            {
                id: 'BbJkCMObNsY',
                title: 'Saving & Loading ML Models — Pickle & Joblib (NeuralNine)',
                desc: '학습된 Scaler 객체를 Pickle/Joblib으로 직렬화하여 운영 환경에서 fit 없이 재사용하는 방법.',
                reason: 'deepDive "실시간 서빙 시나리오"의 핵심인 Pickle·Joblib 직렬화를 학습하세요.',
            },
        ],
        // 추상화 부족: K-Fold / StratifiedKFold — 소량 데이터 시 격리 원칙 유지
        abstraction: [
            {
                id: 'gJo0uNL-5Lw',
                title: 'K-Fold Cross Validation (StatQuest)',
                desc: '데이터가 적어도 격리 원칙을 지키면서 검증하는 K-Fold 교차검증의 원리.',
                reason: 'deepDive "데이터 부족 시나리오"의 핵심인 K-Fold·Stratified 전략을 이해하세요.',
            },
        ],
        default: [
            {
                id: 'fSytzGwwBVw',
                title: 'What is Data Leakage? (StatQuest)',
                desc: '데이터 누수의 원인과 격리·기준점·일관성 원칙을 종합적으로 설명합니다.',
                reason: '누수 방어 시스템 설계의 핵심 개념을 복습하세요.',
            },
            {
                id: 'A88rDEf-pfk',
                title: 'Standardization vs Normalization (StatQuest)',
                desc: 'fit/transform 분리 원칙과 기준점 고정의 중요성.',
                reason: 'Anchor(기준점) 설정이 왜 학습셋에만 이루어져야 하는지 확인하세요.',
            },
            {
                id: 'gJo0uNL-5Lw',
                title: 'K-Fold Cross Validation (StatQuest)',
                desc: '소량 데이터에서도 격리 원칙을 지키는 교차검증 전략.',
                reason: '데이터 부족 상황에서 올바른 검증 방법을 학습하세요.',
            },
        ],
    },

    // ══════════════════════════════════════════════════════════════════
    // Quest 2: 과적합 방어 정규화 시스템 설계
    // checklist : 복잡도제어(L1/L2/Ridge/Lasso) / 특성선택(Feature Selection) / 성능모니터링
    // deepDive  : GridSearchCV·교차검증 / 트리깊이·max_depth / 조기종료·EarlyStopping
    // blueprint : Ridge(alpha) → Lasso(alpha) → RandomForest(max_depth)
    // ══════════════════════════════════════════════════════════════════
    2: {
        // 설계력 부족: L1/L2 정규화 선택 기준과 alpha 설계 원칙
        design: [
            {
                id: 'Q81RR3yKn30',
                title: 'Regularization: Ridge & Lasso 완전 이해 (StatQuest)',
                desc: 'L1(Lasso)은 계수를 0으로 만들어 특성선택, L2(Ridge)는 가중치 크기 축소 — 언제 무엇을 쓸지 설계 기준.',
                reason: '복잡도 제어(Complexity Control) 설계 시 L1 vs L2 선택 기준을 명확히 하세요.',
            },
        ],
        // 정합성 부족: 학습/검증 성능을 함께 모니터링해야 과적합 신호 포착
        consistency: [
            {
                id: 'EuBBz3bI-aA',
                title: 'Bias and Variance Tradeoff (StatQuest)',
                desc: '학습 R²=0.98 vs 검증 R²=0.42 — 이 차이가 과적합 신호임을 이해하고 일관된 모니터링 방법.',
                reason: '성능 모니터링(Performance Monitoring) 원칙: 학습·검증 지표를 동시에 추적하는 방법을 확인하세요.',
            },
        ],
        // 구현력 부족: sklearn Ridge/Lasso 구현 + alpha GridSearchCV
        implementation: [
            {
                id: 'Q81RR3yKn30',
                title: 'Ridge & Lasso 구현 (sklearn) (StatQuest)',
                desc: 'sklearn으로 Ridge, Lasso를 실제 코드로 구현하고 GridSearchCV로 최적 alpha를 탐색하는 방법.',
                reason: '정규화 강도(alpha) 튜닝을 코드로 구현하는 방법을 학습하세요.',
            },
        ],
        // 예외처리 부족: 신경망 조기종료(EarlyStopping), 트리 깊이 제한
        edgeCase: [
            {
                id: 'CRlYPodahlE',
                title: 'Early Stopping & Dropout (DeepLearningAI)',
                desc: '검증 손실이 증가하면 조기종료 — 신경망에서 과적합이 시작되는 시점을 감지하고 멈추는 전략.',
                reason: 'deepDive "조기종료 전략 시나리오"의 핵심인 EarlyStopping 구현을 학습하세요.',
            },
        ],
        // 추상화 부족: 과적합·과소적합의 근본 원리를 모델 무관하게 일반화
        abstraction: [
            {
                id: 'EuBBz3bI-aA',
                title: 'Underfitting & Overfitting 원리 (StatQuest)',
                desc: '편향-분산 트레이드오프를 추상적으로 이해하여 어떤 모델에도 적용할 수 있는 사고 방식.',
                reason: '정규화를 특정 기법이 아닌 "복잡도 제어"의 추상 원칙으로 이해하세요.',
            },
        ],
        default: [
            {
                id: 'EuBBz3bI-aA',
                title: 'Bias and Variance (StatQuest)',
                desc: '편향-분산 트레이드오프 — 과적합의 근본 원리.',
                reason: '과적합이 발생하는 이유를 먼저 이해하세요.',
            },
            {
                id: 'Q81RR3yKn30',
                title: 'Ridge & Lasso Regularization (StatQuest)',
                desc: 'L1, L2 정규화의 동작 원리와 구현.',
                reason: '정규화 기법 선택 기준과 alpha 조정 방법을 확인하세요.',
            },
            {
                id: 'CRlYPodahlE',
                title: 'Early Stopping & Dropout (DeepLearningAI)',
                desc: '신경망에서의 조기종료와 드롭아웃 정규화.',
                reason: '다양한 정규화 기법을 비교하고 상황에 맞게 적용하는 방법을 학습하세요.',
            },
        ],
    },

    // ══════════════════════════════════════════════════════════════════
    // Quest 3: 불균형 데이터 처리 시스템 설계
    // checklist : 불균형진단(Imbalance Detection) / 샘플링전략(SMOTE) / 공정한평가(F1·AUC)
    // deepDive  : class_weight·비용함수 / 임계값·ROC곡선 / StratifiedKFold·층화분할
    // blueprint : value_counts → SMOTE.fit_resample → precision_recall_fscore + roc_auc
    // ══════════════════════════════════════════════════════════════════
    3: {
        // 설계력 부족: 불균형 감지→샘플링→평가지표 전체 흐름 설계
        design: [
            {
                id: 'JnlM4yLFNuo',
                title: 'Imbalanced Data 처리 전략 설계 (StatQuest)',
                desc: '클래스 불균형 문제의 진단부터 샘플링 선택, 평가지표 결정까지 전체 설계 흐름.',
                reason: '불균형 진단(Detection) → 샘플링 전략 → 공정한 평가의 설계 원칙을 확인하세요.',
            },
        ],
        // 정합성 부족: 정확도 대신 F1/AUC를 일관되게 사용해야 하는 이유
        consistency: [
            {
                id: 'u2WNMEbKxL8',
                title: 'ROC Curve & AUC — 불균형 평가의 표준 (StatQuest)',
                desc: '"정확도 99%"의 함정 — 불균형 데이터에서는 AUC-ROC와 F1-Score를 일관되게 사용해야 하는 이유.',
                reason: '공정한 평가(Fair Evaluation) 원칙: 정확도 대신 AUC·F1을 평가 기준으로 삼는 방법.',
            },
        ],
        // 구현력 부족: SMOTE 실제 코드 구현
        implementation: [
            {
                id: '4tAMGFpGsug',
                title: 'SMOTE 완전 구현 (imbalanced-learn)',
                desc: 'SMOTE 알고리즘 원리와 imbalanced-learn 라이브러리로 소수 클래스를 합성 생성하는 코드.',
                reason: 'SMOTE.fit_resample()을 올바르게 구현하고 결과를 검증하는 방법을 학습하세요.',
            },
        ],
        // 예외처리 부족: class_weight 비용함수, 분류 임계값 조정
        edgeCase: [
            {
                id: 'RwtP8TToimY',
                title: 'Class Weights & Cost-Sensitive Learning (Krish Naik)',
                desc: '이상 거래 1건 놓치면 $10,000 손실 — class_weight="balanced" 설정과 sample_weight로 비용 불균형 대응.',
                reason: 'deepDive "비용 민감 학습·임계값 조정 시나리오"의 핵심인 class_weight를 학습하세요.',
            },
        ],
        // 추상화 부족: StratifiedKFold — 불균형 유지하며 교차검증
        abstraction: [
            {
                id: 'gJo0uNL-5Lw',
                title: 'StratifiedKFold & 계층화 분할 (StatQuest)',
                desc: '불균형 데이터를 무작위 분할하면 한쪽에 이상 케이스가 몰릴 수 있다 — stratify=y로 해결.',
                reason: 'deepDive "계층화된 분할 시나리오"의 핵심인 StratifiedKFold를 이해하세요.',
            },
        ],
        default: [
            {
                id: 'JnlM4yLFNuo',
                title: 'Handling Imbalanced Data (StatQuest)',
                desc: '불균형 데이터 처리 전략을 종합적으로 설명합니다.',
                reason: '불균형 진단, 샘플링, 평가의 전체 흐름을 복습하세요.',
            },
            {
                id: '4tAMGFpGsug',
                title: 'SMOTE 구현 (imbalanced-learn)',
                desc: 'SMOTE 기반 오버샘플링의 원리와 구현.',
                reason: '소수 클래스를 합성 생성하는 방법을 학습하세요.',
            },
            {
                id: 'u2WNMEbKxL8',
                title: 'ROC AUC Explained (StatQuest)',
                desc: '불균형 데이터에서의 올바른 평가 지표.',
                reason: '정확도의 함정을 피하는 AUC·F1 평가 전략을 확인하세요.',
            },
        ],
    },

    // ══════════════════════════════════════════════════════════════════
    // Quest 4: 피처 엔지니어링 최적화 설계
    // checklist : 특성창조(Feature Creation) / 특성변환(로그·스케일링) / 특성선택(중요도)
    // deepDive  : PolynomialFeatures·상호작용 / StandardScaler·정규화 / PCA·차원축소
    // blueprint : 파생변수 생성 → log변환·StandardScaler → feature_importances_
    // ══════════════════════════════════════════════════════════════════
    4: {
        // 설계력 부족: 도메인 지식 기반 파생변수 창조 원칙
        design: [
            {
                id: 'md8IrSMPi6o',
                title: 'Feature Engineering 실전 (Kaggle Course)',
                desc: '구매빈도=구매횟수/가입일수처럼 도메인 지식으로 원시 특성에서 의미 있는 파생변수를 만드는 방법.',
                reason: '특성 창조(Feature Creation) 원칙 — 3개 원시 특성에서 새 특성을 설계하는 방법을 확인하세요.',
            },
        ],
        // 정합성 부족: 변환 기준(fit)을 train에만 적용해야 누수 없이 일관성 확보
        consistency: [
            {
                id: 'A88rDEf-pfk',
                title: 'StandardScaler fit/transform 분리 — 특성 변환의 일관성 (StatQuest)',
                desc: '로그 변환·StandardScaler를 train에만 fit하고 test에는 transform만 적용해야 하는 이유.',
                reason: '특성 변환(Feature Transformation) 시 누수 없는 일관된 적용 원칙을 점검하세요.',
            },
        ],
        // 구현력 부족: feature_importances_ 활용한 특성 선택 코드
        implementation: [
            {
                id: '68ABAU_V8qI',
                title: 'Feature Selection — RandomForest 중요도 분석 (StatQuest)',
                desc: 'model.feature_importances_로 기여도 낮은 특성을 제거하고 SelectKBest·RFE를 코드로 구현.',
                reason: '특성 선택(Feature Selection) 코드 구현 — 중요도 기반 필터링 방법을 학습하세요.',
            },
        ],
        // 예외처리 부족: PolynomialFeatures 상호작용, 차원의 저주
        edgeCase: [
            {
                id: 'viZrOnJclY0',
                title: 'Curse of Dimensionality & PCA (StatQuest)',
                desc: '특성 100개로 늘렸더니 성능이 하락한 이유 — 차원의 저주와 PCA·SelectKBest 해결책.',
                reason: 'deepDive "차원의 저주 시나리오"의 핵심인 PCA·차원축소를 학습하세요.',
            },
        ],
        // 추상화 부족: 선형모델 vs 트리모델의 상호작용 처리 차이
        abstraction: [
            {
                id: 'md8IrSMPi6o',
                title: 'Polynomial Features & 상호작용 특성 (Kaggle)',
                desc: '선형 모델은 PolynomialFeatures로 수동 생성, 트리 모델은 자동 학습 — 모델별 추상화 차이.',
                reason: 'deepDive "특성 상호작용 시나리오"의 핵심인 PolynomialFeatures와 비선형 모델 차이를 이해하세요.',
            },
        ],
        default: [
            {
                id: 'md8IrSMPi6o',
                title: 'Feature Engineering (Kaggle)',
                desc: '피처 엔지니어링의 전체 프로세스.',
                reason: '특성 창조, 변환, 선택의 흐름을 복습하세요.',
            },
            {
                id: '68ABAU_V8qI',
                title: 'Feature Selection (StatQuest)',
                desc: '특성 중요도 분석과 선택 방법.',
                reason: '불필요한 특성 제거로 모델을 최적화하는 방법을 확인하세요.',
            },
            {
                id: 'viZrOnJclY0',
                title: 'Curse of Dimensionality (StatQuest)',
                desc: '고차원 데이터 문제와 PCA.',
                reason: '차원의 저주와 해결 전략을 학습하세요.',
            },
        ],
    },

    // ══════════════════════════════════════════════════════════════════
    // Quest 5: 하이퍼파라미터 튜닝 전략 설계
    // checklist : 파라미터공간(param_grid) / 탐색전략(GridSearch·RandomSearch) / 교차검증(K-Fold)
    // deepDive  : HalvingGridSearch·베이지안최적화·Optuna / n_estimators↔max_depth 상호작용 / Warm-start·미세조정
    // blueprint : param_grid 정의 → GridSearchCV(cv=5) → best_params_
    // ══════════════════════════════════════════════════════════════════
    5: {
        // 설계력 부족: param_grid 정의와 GridSearch vs RandomSearch 선택 기준
        design: [
            {
                id: 'HdlDYng7g58',
                title: 'Hyperparameter Tuning — GridSearch vs RandomSearch (StatQuest)',
                desc: 'param_grid를 정의하고 GridSearchCV vs RandomizedSearchCV 중 언제 무엇을 선택할지 설계 기준.',
                reason: '파라미터 공간(Parameter Space) 설계와 탐색 전략 선택 원칙을 확인하세요.',
            },
        ],
        // 정합성 부족: 교차검증을 빼면 튜닝 결과를 신뢰할 수 없음
        consistency: [
            {
                id: 'gJo0uNL-5Lw',
                title: 'K-Fold Cross Validation — 튜닝 신뢰도 확보 (StatQuest)',
                desc: 'GridSearchCV(cv=5)로 교차검증을 함께 수행해야 파라미터 평가 결과를 신뢰할 수 있는 이유.',
                reason: '교차검증(Cross-Validation) 원칙 — cv= 파라미터가 왜 필수인지 확인하세요.',
            },
        ],
        // 구현력 부족: GridSearchCV 코드 구현 + best_params_ 추출
        implementation: [
            {
                id: 'HdlDYng7g58',
                title: 'GridSearchCV 완전 구현 (sklearn)',
                desc: 'param_grid 딕셔너리 정의 → GridSearchCV fitting → best_params_, best_estimator_ 추출 코드.',
                reason: '하이퍼파라미터 탐색을 코드로 구현하고 최적 파라미터를 적용하는 방법을 학습하세요.',
            },
        ],
        // 예외처리 부족: 탐색 시간이 너무 길 때 — HalvingGridSearch, 베이지안 최적화(Optuna)
        edgeCase: [
            {
                id: 'Np8h_U9PmFw',
                title: 'Bayesian Optimization & Optuna — 효율적 탐색 (Weights & Biases)',
                desc: '100개 조합을 그리드로 하면 하루 — HalvingGridSearch와 Optuna로 탐색 비용을 줄이는 방법.',
                reason: 'deepDive "조기종료를 통한 효율화 시나리오"의 핵심인 HalvingGridSearch·베이지안최적화를 학습하세요.',
            },
        ],
        // 추상화 부족: n_estimators ↔ max_depth 상호작용, Warm-start 전이 개념
        abstraction: [
            {
                id: 'Np8h_U9PmFw',
                title: '파라미터 상호작용 & Warm-start 이해 (W&B)',
                desc: 'n_estimators 높으면 max_depth 낮게 — 파라미터 간 상호작용과 Warm-start로 탐색 출발점 설정.',
                reason: 'deepDive "파라미터 상호작용·이전학습 시나리오"의 핵심 개념을 이해하세요.',
            },
        ],
        default: [
            {
                id: 'HdlDYng7g58',
                title: 'Hyperparameter Tuning (StatQuest)',
                desc: '파라미터 공간, 탐색 전략, 교차검증의 전체 흐름.',
                reason: '하이퍼파라미터 튜닝 전략의 핵심을 복습하세요.',
            },
            {
                id: 'gJo0uNL-5Lw',
                title: 'K-Fold Cross Validation (StatQuest)',
                desc: 'K-Fold 교차검증의 원리와 신뢰도 확보 방법.',
                reason: '교차검증이 왜 필수인지 확인하세요.',
            },
            {
                id: 'Np8h_U9PmFw',
                title: 'Bayesian Optimization (W&B)',
                desc: '계산 효율을 높이는 고급 튜닝 전략.',
                reason: '그리드 탐색의 한계를 극복하는 방법을 학습하세요.',
            },
        ],
    },

    // ══════════════════════════════════════════════════════════════════
    // Quest 6: 모델 해석성과 설명가능성 설계
    // checklist : 전역적해석(feature_importances_) / 개별적해석(SHAP·LIME) / 공정성검증(편향감지)
    // deepDive  : 대리변수·Proxy Bias·편향완화 / SHAP·LIME·대리모델 / 반사실·counterfactual·actionable
    // blueprint : feature_importances_ → shap.TreeExplainer → 보호속성 그룹별 성능비교
    // ══════════════════════════════════════════════════════════════════
    6: {
        // 설계력 부족: 전역해석 → 개별해석 → 공정성검증 전체 설계 흐름
        design: [
            {
                id: 'B-c8tIgchu0',
                title: 'SHAP Values — 전역·개별 해석 설계 (StatQuest)',
                desc: 'feature_importances_(전역) → SHAP force_plot(개별) → 편향 감지로 이어지는 해석가능성 시스템 설계.',
                reason: '전역적 해석 → 개별적 해석 → 공정성 검증의 3단계 설계 흐름을 확인하세요.',
            },
        ],
        // 정합성 부족: 모든 예측에 일관된 SHAP 기준 적용
        consistency: [
            {
                id: 'B-c8tIgchu0',
                title: 'SHAP Summary Plot — 일관된 해석 기준 (StatQuest)',
                desc: 'SHAP Summary Plot으로 전체 데이터에 일관된 feature importance 기준을 적용하는 방법.',
                reason: '개별 예측이 아닌 전체 모델에 걸쳐 일관된 해석 기준을 제공하는 방법을 확인하세요.',
            },
        ],
        // 구현력 부족: LIME 코드 구현으로 개별 예측 설명
        implementation: [
            {
                id: 'C80SQe16Rao',
                title: 'LIME 구현 — 개별 예측 설명 (Towards Data Science)',
                desc: 'LIME을 코드로 구현하여 특정 고객의 대출 거절 이유를 수치로 설명하는 방법.',
                reason: '개별적 해석(Local Interpretation) 구현 — SHAP 외에 LIME을 활용하는 방법을 학습하세요.',
            },
        ],
        // 예외처리 부족: 성별 없어도 대리변수(Proxy Bias)로 차별 발생
        edgeCase: [
            {
                id: 'GfGpXMBjOBg',
                title: 'AI Fairness & Proxy Bias 감지 (Google Developers)',
                desc: '성별이 특성에 없어도 직업·이름·거주지로 간접 차별(Proxy Bias)이 발생하는 원리와 완화 방법.',
                reason: 'deepDive "편향 감지 시나리오"의 핵심인 대리변수(Proxy) 차별과 편향 완화 전략을 학습하세요.',
            },
        ],
        // 추상화 부족: 반사실적 설명(Counterfactual) — actionable advice
        abstraction: [
            {
                id: 'GfGpXMBjOBg',
                title: 'Counterfactual Explanation & Actionable AI (Google)',
                desc: '"소득 $5,000 올리면 승인" — 반사실적 설명으로 사용자에게 실행 가능한 조언을 제공하는 방법.',
                reason: 'deepDive "반사실적 설명 시나리오"의 핵심인 counterfactual·actionable 설명 방법을 이해하세요.',
            },
        ],
        default: [
            {
                id: 'B-c8tIgchu0',
                title: 'SHAP Values Explained (StatQuest)',
                desc: 'SHAP의 원리와 전역·개별 해석 방법.',
                reason: '블랙박스 모델 해석의 핵심 기법을 복습하세요.',
            },
            {
                id: 'C80SQe16Rao',
                title: 'LIME Explained',
                desc: 'LIME으로 개별 예측을 설명하는 방법.',
                reason: 'SHAP 외의 해석 기법을 추가로 학습하세요.',
            },
            {
                id: 'GfGpXMBjOBg',
                title: 'AI Fairness and Bias (Google)',
                desc: '공정성 검증과 편향 감지 방법.',
                reason: '대리변수 차별 감지와 공정성 보장 방법을 확인하세요.',
            },
        ],
    },
};


// ── 레거시 호환 ────────────────────────────────────────────────────────────
export const LEARNING_RESOURCES = {};


// ── 외부 노출 함수 ────────────────────────────────────────────────────────

/**
 * 챕터(Quest ID) × 취약 차원 기반으로 추천 영상 3개를 반환합니다.
 *
 * @param {number|string} questId    - stages.js의 quest id (1~6)
 * @param {Object}        dimensions - 평가 결과의 dimensions 객체
 *                                    { design: {score, max, percentage}, edgeCase: {...}, ... }
 * @param {number}        maxCount   - 최대 반환 개수 (기본 3)
 * @returns {Array}                  - 추천 영상 배열
 */
export function getRecommendedVideos(questId, dimensions = {}, maxCount = 3) {
    const id = Number(questId);
    const questPool = QUEST_VIDEOS[id];

    if (!questPool) {
        console.warn(`[learningResources] Quest ID ${questId}에 대한 큐레이션이 없습니다.`);
        return [];
    }

    // 5차원 순서 (stages.js evaluationEngine 기준)
    const DIMENSION_ORDER = ['consistency', 'design', 'abstraction', 'edgeCase', 'implementation'];

    // 점수 비율 기준 취약 차원 정렬
    const sorted = DIMENSION_ORDER
        .map((dim) => {
            const d = dimensions[dim];
            if (!d) return { dim, ratio: 1 };
            const ratio = d.percentage != null
                ? d.percentage / 100
                : (d.max > 0 ? d.score / d.max : 1);
            return { dim, ratio };
        })
        .sort((a, b) => a.ratio - b.ratio);

    const result = [];
    const usedIds = new Set();

    // 취약 차원 순서대로 해당 챕터 영상 선택
    for (const { dim } of sorted) {
        if (result.length >= maxCount) break;
        const pool = questPool[dim] || [];
        for (const video of pool) {
            if (result.length >= maxCount) break;
            if (!usedIds.has(video.id)) {
                result.push(video);
                usedIds.add(video.id);
            }
        }
    }

    // 부족하면 default로 보완
    if (result.length < maxCount) {
        const defaults = questPool.default || [];
        for (const video of defaults) {
            if (result.length >= maxCount) break;
            if (!usedIds.has(video.id)) {
                result.push(video);
                usedIds.add(video.id);
            }
        }
    }

    return result;
}
