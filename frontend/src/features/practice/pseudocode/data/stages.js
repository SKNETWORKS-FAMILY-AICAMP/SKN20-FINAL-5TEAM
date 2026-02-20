// stages.js - Quest 완전판
// [2026-02-21] 외부 하드코딩 검증 규칙(VALIDATION_LIBRARY) 제거 — 백엔드 기반으로 일원화

export const aiQuests = [
    {
        id: 1,
        title: "전처리 데이터 누수 방어 시스템 설계",
        category: "System Reboot",
        emoji: "🚨",
        desc: "AI 모델의 신뢰성을 파괴하는 전처리 데이터 누수를 차단하고 견고한 검증 규칙을 설계합니다.",
        rewardXP: 500,
        subModuleTitle: "LEAKAGE_GUARD",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },
        scenario: "신입 개발자가 작성한 이탈 예측 모델이 검증(Validation) 정확도 95%를 기록하며 배포되었으나, 실제 고객 데이터가 들어오는 운영(Serving) 환경에서는 68%의 성능을 보이며 비즈니스에 큰 손실을 입혔습니다. 조사 결과, 데이터 전처리 단계에서 '정보 유출(Leakage)'이 발생한 것으로 파악되었습니다.",

        cards: [
            { icon: "🚑", text: "STEP 1: 위험 진단", coduckMsg: "주니어 개발자의 치명적인 실수가 발견되었습니다. 무엇이 문제인지 먼저 파악합시다." },
            { icon: "📝", text: "STEP 2: 규칙 설계", coduckMsg: "이런 실수가 재발하지 않도록 AI가 자동으로 감지할 수 있는 검증 규칙을 만드세요." },
            { icon: "💻", text: "STEP 3: 심화 검증", coduckMsg: "단순한 규칙을 넘어, 더 교묘한 누수 패턴도 잡아낼 수 있는지 확인해 봅시다." },
            { icon: "⚖️", text: "STEP 4: 최종 평가", coduckMsg: "당신의 아키텍처 설계 능력을 AI 아키텍트가 정밀 평가합니다." }
        ],

        blueprint: `
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. Isolation: 전처리 전 물리적 분리 (최우선 방어선)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 2. Anchor: 오직 학습 데이터로만 통계량(fit) 추출
scaler = StandardScaler()
scaler.fit(X_train)

# 3. Consistency: 학습셋의 기준점으로 테스트셋까지 변환
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)
        `.trim(),

        blueprintSteps: [
            { id: "s1", python: "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)", pseudo: "먼저 데이터를 학습용과 검증용으로 물리적 격리(Isolation)한다.", keywords: ["격리", "분리", "학습/검증", "Isolation"] },
            { id: "s2", python: "scaler.fit(X_train)", pseudo: "학습 데이터(train)에서만 통계량을 추출하여 기준점(Anchor)을 설정한다.", keywords: ["기준점", "학습데이터", "통계량", "fit"] },
            { id: "s3", python: "scaler.transform(X_test)", pseudo: "테스트 데이터(test)에는 fit 없이 transform만 적용하여 일관성(Consistency)을 유지한다.", keywords: ["일관성", "테스트데이터", "transform", "동일변환"] }
        ],

        interviewQuestions: [
            {
                id: "concept_1_choice",
                type: "CHOICE",
                question: "Q1. [격리의 시점] 데이터 오염을 막는 첫 번째 방어선\n신입 개발자가 범한 가장 큰 실수는 scaler.fit(df)를 통해 전체 데이터의 정보를 섞어버린 것입니다. 이를 방지하기 위한 가장 우선적인 조치는 무엇인가요?",
                options: [
                    { text: "더 많은 데이터를 수집하여 모델을 복잡하게 만든다.", correct: false, feedback: "데이터 양을 늘리는 것과 정보 유출 방지는 무관합니다." },
                    { text: "전처리(Scaling)를 모두 마친 후 데이터를 나눈다.", correct: false, feedback: "이것이 바로 신입 개발자가 범한 실수(누수 발생)입니다." },
                    { text: "데이터 전처리 프로세스가 시작되기 전, 학습(Train)과 테스트(Test) 데이터를 물리적으로 분리(격리)한다.", correct: true, feedback: "정답입니다! 전처리 전 분리가 가장 확실한 방어선입니다." },
                    { text: "운영 환경에서는 전처리를 생략한다.", correct: false, feedback: "학습 때와 동일한 전처리가 운영 환경에서도 반드시 필요합니다." }
                ],
                context: "데이터 전처리 누수(Leakage) 원천 차단 전략"
            },
            {
                id: "concept_2_choice",
                type: "CHOICE",
                question: "Q2. [기준점의 설정] '저울'은 무엇으로 만들어야 하는가?\n데이터를 분리한 후, 표준화(Standardization)를 위한 평균과 표준편차 값은 어느 데이터셋에서 추출해야 하나요?",
                options: [
                    { text: "전체 데이터셋: 데이터가 많을수록 통계량이 정확하기 때문이다.", correct: false, feedback: "전체 데이터를 사용하면 테스트 데이터의 정보가 스며들어 '데이터 누수'가 발생합니다." },
                    { text: "테스트 데이터셋: 실제 운영 환경과 유사한 분포를 가져야 하기 때문이다.", correct: false, feedback: "테스트 데이터는 미래의 데이터 역할을 해야 하며, 이를 기준으로 삼아서는 안 됩니다." },
                    { text: "학습 데이터셋: 모델이 '이미 알고 있는 과거의 정보'만을 기준으로 삼아야 하기 때문이다.", correct: true, feedback: "정답입니다! 학습 데이터에서 얻은 '저울(평균/표준편차)'로 모든 데이터를 측정해야 정보 유출이 없습니다." },
                    { text: "무작위 추출: 편향을 방지하기 위해 매번 새로 계산해야 한다.", correct: false, feedback: "기준점(저울)이 매번 바뀌면 모델의 판단 기준이 흔들리게 됩니다." }
                ],
                context: "신뢰할 수 있는 모델 평가 기준 확립"
            },
        ],

        designContext: {
            title: "[미션] 데이터 오염 원천 차단 설계",
            description: "실제 운영 환경에서 이 모델이 '바보'가 되지 않도록, 데이터 오염을 원천 차단하는 전처리 파이프라인의 설계 원칙과 그 순서를 '의사코드(Pseudo Code)' 형태로 서술하세요.",
            incidentCode: `
scaler = StandardScaler()
scaler.fit(df)  # ⚠️ 전체 데이터로 fit
X_train = scaler.transform(df[:800])
X_test = scaler.transform(df[800:])
            `.trim(),
            incidentProblem: "fit() 실행 시점에 Train/Test 분할이 되지 않아 Test 통계량이 Train에 영향",
            currentIncident: `
🚨 긴급 사고 보고: 전처리 데이터 누수 감지
주니어 개발자가 작성한 전처리 코드가 Production에 배포되었습니다.
fit() 실행 시점에 Train/Test 분할이 되지 않아 Test 통계량이 Train에 영향을 주었습니다.

결과: Train 정확도 95% → Test 정확도 68% (27%p 폭락)
            `.trim(),
            engineeringRules: [
                "Train 데이터로만 fit 한다.",
                "Test 데이터는 transform만 수행한다.",
                "미래 데이터의 정보는 사용하지 않는다.",
                "학습과 서빙은 동일한 전처리 흐름을 사용한다."
            ],
            writingGuide: `
[필수 포함 조건 (Constraint)]
답이 여러 갈래로 튀지 않도록 다음 3가지 키워드를 반드시 사용하여 논리를 구성하게 합니다:
격리 (Isolation): 데이터를 나누는 시점
기준점 (Anchor): 통계량(fit)을 추출할 대상
일관성 (Consistency): 학습과 운영 환경의 동일한 변환 방식
            `.trim()
        },

        // [2026-02-14] 실무 3대 심화 시나리오 (서술형 세션)
        deepDiveScenarios: [
            {
                id: "drift",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "시간",
                title: "데이터 드리프트 시나리오",
                question: "1년 뒤 고객층 변화로 데이터 분포가 바뀌었습니다. 기존 기준점(Anchor)을 고수하면 성능이 떨어질 텐데, '일관성' 원칙을 깨고 기준을 실시간으로 바꿀 것인가요? 아니면 다른 대안이 있나요?",
                intent: "모델의 노후화를 인지하고 주기적인 재학습 파이프라인 설계 역량 확인.",
                scoringKeywords: ["모니터링", "재학습", "기준점 갱신", "Retraining"],
                modelAnswer: "실시간으로 기준을 바꾸면 판단 근거가 흔들립니다. 대신 '모니터링'을 통해 성능 저하를 감지하고, 새로운 데이터로 '주기적인 재학습'을 진행하여 기준점(Anchor)을 공식적으로 갱신해야 합니다."
            },
            {
                id: "realtime",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "환경",
                title: "실시간 서빙 시나리오",
                question: "0.1초 내 응답이 필요한 시스템입니다. 매번 격리와 기준점(fit) 계산을 반복할 순 없는데, 정확도를 지키며 속도를 확보할 엔지니어링적 방법은 무엇인가요?",
                intent: "학습 시의 상태를 서빙 환경으로 전이하는 직렬화 기술 확인.",
                scoringKeywords: ["Pickle", "Joblib", "직렬화", "객체화", "Serialization"],
                modelAnswer: "학습 단계에서 생성된 Scaler 객체를 'Pickle'이나 'Joblib'으로 직렬화(Serialization)하여 저장합니다. 운영 환경에서는 이를 로드하여 fit 과정 없이 transform만 수행함으로써 정확도와 속도를 동시에 잡습니다."
            },
            {
                id: "scarcity",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "한계",
                title: "데이터 부족 및 불균형 시나리오",
                question: "데이터가 100건뿐이라 격리를 하면 학습이 안 되고, 안 하자니 오염이 걱정됩니다. 원칙을 지키면서도 모델을 제대로 검증할 전략은?",
                intent: "소량 데이터셋에서의 통계적 유의성 확보 능력 확인.",
                scoringKeywords: ["K-Fold", "Stratified", "교차 검증", "층화"],
                modelAnswer: "단순 분할 대신 'K-Fold 교차 검증'이나 'Stratified Sampling(층화 추출)'을 사용합니다. 데이터를 여러 조각으로 나누어 모든 데이터가 한 번씩은 검증용으로 쓰이게 하되, 매 루프마다 격리 원칙은 엄격히 지킵니다."
            }
        ],

        // [2026-02-14] ✅ COMPLETE 버전 검증 규칙 적용
        checklist: [
            { id: 'check_isolation', label: '격리 (Isolation) 포함', patterns: [/격리|분리|나누|나눔|isolation|split/i] },
            { id: 'check_anchor', label: '기준점 (Anchor) 정의', patterns: [/기준점|기준|통계량|fit|anchor|학습/i] },
            { id: 'check_consistency', label: '일관성 (Consistency) 확보', patterns: [/일관성|동일|변환|consistency|transform/i] }
        ],
        placeholder: "격리, 기준점, 일관성 원칙을 바탕으로 당신만의 데이터 전처리 설계를 서술하세요...\n예: 1. train_test_split으로 데이터를 분리한다.",

        mapPos: { x: 100, y: 350 }
    },
    {
        id: 2,
        title: "과적합 방어 정규화 시스템 설계",
        category: "Overfit Shield",
        emoji: "🛡️",
        desc: "모델이 학습 데이터에만 과도하게 최적화되어 일반화 능력을 잃는 과적합을 방지하고, 정규화 기법으로 강건한 모델을 설계합니다.",
        rewardXP: 600,
        subModuleTitle: "OVERFITTING_GUARD",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },
        scenario: "강화학습 기반 가격 예측 모델이 학습 때는 R² 스코어 0.98을 달성했으나, 새로운 시간대 데이터로 테스트하니 0.42로 급락했습니다. 모델이 학습 노이즈까지 학습해버린 '과적합(Overfitting)'이 의심됩니다.",

        cards: [
            { icon: "🔍", text: "STEP 1: 과적합 진단", coduckMsg: "학습과 검증의 성능 차이를 분석해 과적합 정도를 파악합시다." },
            { icon: "⚙️", text: "STEP 2: 정규화 설계", coduckMsg: "L1/L2 정규화, 드롭아웃, 조기종료 등의 기법으로 모델의 복잡도를 제어하세요." },
            { icon: "🎯", text: "STEP 3: 파라미터 최적화", coduckMsg: "정규화 강도를 조정하여 최적의 성능 균형점을 찾아봅시다." },
            { icon: "✅", text: "STEP 4: 최종 검증", coduckMsg: "일반화된 모델이 새로운 데이터에도 안정적인지 확인합니다." }
        ],

        blueprint: `
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor

# 1. Complexity Control: 모델 복잡도 제어 (L2 정규화)
model_l2 = Ridge(alpha=1.0)
model_l2.fit(X_train, y_train)

# 2. Feature Selection: 불필요한 특성 제거 (L1 정규화)
model_l1 = Lasso(alpha=0.01)
model_l1.fit(X_train, y_train)

# 3. Ensemble Stabilization: 앙상블 기법으로 일반화 강화
model_ensemble = RandomForestRegressor(n_estimators=100, max_depth=5)
model_ensemble.fit(X_train, y_train)
        `.trim(),

        blueprintSteps: [
            { id: "s1", python: "model = Ridge(alpha=1.0)", pseudo: "L2 정규화를 통해 모델의 계수 크기를 제어하여 과도한 가중치를 억제한다.", keywords: ["정규화", "L2", "복잡도제어", "Ridge"] },
            { id: "s2", python: "model.fit(X_train, y_train)", pseudo: "학습 데이터에서 정규화된 모델을 적합시켜 일반화 성능을 높인다.", keywords: ["적합", "학습", "정규화"] },
            { id: "s3", python: "score_train vs score_test", pseudo: "학습 데이터와 검증 데이터의 성능 차이를 모니터링하여 과적합 정도를 진단한다.", keywords: ["모니터링", "성능차이", "과적합진단"] }
        ],

        interviewQuestions: [
            {
                id: "overfitting_1_choice",
                type: "CHOICE",
                question: "Q1. [과적합의 신호] 학습 R²=0.98, 검증 R²=0.42가 의미하는 것은?\n모델의 어떤 병증을 시사하나요?",
                options: [
                    { text: "모델이 충분히 복잡하지 않아 데이터를 제대로 학습하지 못했다.", correct: false, feedback: "학습 정확도가 높으므로 이 설명은 맞지 않습니다." },
                    { text: "모델이 학습 데이터의 노이즈까지 함께 학습하여 새로운 데이터에 적응하지 못했다.", correct: true, feedback: "정답입니다! 높은 학습 정확도와 낮은 검증 정확도는 과적합의 명확한 신호입니다." },
                    { text: "검증 데이터의 품질이 좋지 않아 테스트 결과가 신뢰할 수 없다.", correct: false, feedback: "56%의 성능 격차는 데이터 품질 문제가 아닌 모델의 과적합을 의미합니다." },
                    { text: "더 많은 데이터를 추가하면 자동으로 해결된다.", correct: false, feedback: "데이터 추가는 도움이 될 수 있지만, 정규화 같은 직접적인 개입이 필요합니다." }
                ],
                context: "과적합의 원인 파악 및 진단"
            },
            {
                id: "overfitting_2_choice",
                type: "CHOICE",
                question: "Q2. [정규화의 역할] Ridge 정규화(L2)와 Lasso 정규화(L1)의 차이점은?\n어느 상황에서 어느 것을 사용해야 하나요?",
                options: [
                    { text: "L2는 계수를 0으로 만들고, L1은 계수 크기를 축소한다.", correct: false, feedback: "반대입니다. L1이 체계적으로 계수를 0으로 만듭니다." },
                    { text: "L1은 계수를 0으로 만들어 '특성 선택'을 수행하고, L2는 계수 크기를 축소해 '가중치 분산'을 제어한다.", correct: true, feedback: "정답입니다! L1은 피처 선택에, L2는 가중치 제어에 더 효과적입니다." },
                    { text: "L1과 L2는 동일한 역할을 하므로 어느 것을 선택해도 상관없다.", correct: false, feedback: "L1과 L2는 서로 다른 메커니즘으로 작동하며, 데이터 특성에 따라 선택해야 합니다." },
                    { text: "L1은 느리고 L2는 빨라서 항상 L2를 사용해야 한다.", correct: false, feedback: "속도 차이는 미미하며, 문제 특성에 맞는 방식을 선택해야 합니다." }
                ],
                context: "정규화 기법의 선택과 적용"
            }
        ],

        designContext: {
            title: "[미션] 과적합 방어 정규화 설계",
            description: "학습 데이터의 노이즈까지 학습한 과적합 모델을 개선하기 위해, 정규화 기법을 설계하고 적절한 정규화 강도(alpha)를 결정하는 엔지니어링 전략을 의사코드로 서술하세요.",
            incidentCode: `
# 과적합 상황
model = LinearRegression()
model.fit(X_train, y_train)
train_score = 0.98  # 매우 높음
test_score = 0.42   # 매우 낮음 → 과적합!
            `.trim(),
            incidentProblem: "모델이 학습 데이터의 노이즈까지 학습하여 새로운 데이터에 일반화하지 못함",
            currentIncident: `
🛡️ 알림: 과적합 탐지
가격 예측 모델이 학습 데이터에서는 뛰어난 성능(R²=0.98)을 보이지만,
새로운 시간대 데이터에서는 급격히 성능이 떨어집니다(R²=0.42).

이는 모델이 학습 데이터의 특수한 패턴과 노이즈를 암기했다는 증거입니다.
            `.trim(),
            engineeringRules: [
                "정규화 강도(alpha)를 점진적으로 조정한다.",
                "학습과 검증 성능을 동시에 모니터링한다.",
                "과적합과 과소적합 사이의 최적점을 찾는다.",
                "새로운 데이터에 대한 일반화 능력을 검증한다."
            ],
            writingGuide: `
[필수 포함 조건 (Constraint)]
다음 3가지 개념을 반드시 포함하여 논리를 구성합니다:
복잡도 제어 (Complexity Control): 모델의 학습 능력 제한
특성 선택 (Feature Selection): 불필요한 특성 제거
성능 모니터링 (Performance Monitoring): 학습/검증 성능 함께 추적
            `.trim()
        },

        deepDiveScenarios: [
            {
                id: "alpha_tuning",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "성능",
                title: "정규화 강도 튜닝 시나리오",
                question: "alpha 값이 0에 가까우면 과적합이 생기고, 크면 과소적합(언더핏)이 발생합니다. 최적의 alpha를 찾는 체계적인 방법은?",
                intent: "하이퍼파라미터 튜닝을 위한 검색 전략 이해도 확인.",
                scoringKeywords: ["교차검증", "그리드서치", "정규화곡선", "GridSearchCV"],
                modelAnswer: "K-Fold 교차검증과 GridSearchCV를 사용하여 여러 alpha 값을 자동으로 시도하고, 검증 성능이 최고인 alpha를 선택합니다."
            },
            {
                id: "model_complexity",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "모델",
                title: "모델 복잡도 선택 시나리오",
                question: "선형 모델 vs 트리 기반 모델(Random Forest, XGBoost) 중 어떤 것이 과적합에 더 취약한가요?",
                intent: "모델 아키텍처와 과적합 위험의 관계 이해도 확인.",
                scoringKeywords: ["트리깊이", "모델표현력", "정규화메커니즘", "복잡도"],
                modelAnswer: "트리 기반 모델은 깊이가 깊을수록 과적합되기 쉽습니다. 따라서 max_depth, min_samples_split 등으로 트리의 깊이를 제한하고, 앙상블 개수도 적절히 조정해야 합니다."
            },
            {
                id: "early_stopping",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "학습",
                title: "조기종료 전략 시나리오",
                question: "신경망 학습 중 검증 손실이 증가하기 시작했습니다. 계속 학습해야 할까요, 멈춰야 할까요?",
                intent: "조기종료(Early Stopping)를 통한 과적합 방지 방법 이해도 확인.",
                scoringKeywords: ["조기종료", "검증손실", "성능저하감지", "모니터링"],
                modelAnswer: "검증 손실이 증가하면 과적합이 시작되었다는 신호입니다. '조기종료(Early Stopping)'를 사용하여 검증 성능이 떨어지면 학습을 멈추는 것이 정답입니다."
            }
        ],

        checklist: [
            { id: 'check_control', label: '복잡도 제어 (Complexity Control)', patterns: [/복잡도|제어|정규화|L1|L2|Ridge|Lasso|depth|제한/i] },
            { id: 'check_selection', label: '특성 선택 (Feature Selection)', patterns: [/특성|선택|제거|가중치|분산|selection|feature/i] },
            { id: 'check_monitoring', label: '성능 모니터링 (Performance Monitoring)', patterns: [/성능|모니터링|추적|진단|accuracy|score|monitoring/i] }
        ],
        placeholder: "복잡도 제어, 특성 선택, 성능 모니터링 원칙을 바탕으로 과적합 방어 전략을 서술하세요...\n예: 1. Ridge 정규화를 적용하여 가중치를 제어한다.",

        mapPos: { x: 300, y: 350 }
    },
    {
        id: 3,
        title: "불균형 데이터 처리 시스템 설계",
        category: "Balance Keeper",
        emoji: "⚖️",
        desc: "클래스 불균형(정상 99% vs 이상 1%)으로 인한 모델 편향을 해결하고, 공정한 분류기를 설계합니다.",
        rewardXP: 650,
        subModuleTitle: "IMBALANCE_GUARD",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },
        scenario: "이상 거래 탐지 시스템에서 정상 거래는 99%, 이상 거래는 1%입니다. 모델을 학습시키니 모든 거래를 '정상'으로 분류하면 정확도가 99%가 나옵니다. 그런데 실제 이상 거래는 하나도 찾지 못했습니다.",

        cards: [
            { icon: "📊", text: "STEP 1: 불균형 분석", coduckMsg: "클래스 분포의 불균형이 모델 성능에 어떤 영향을 미치는지 파악합시다." },
            { icon: "🔄", text: "STEP 2: 샘플링 전략", coduckMsg: "오버샘플링, 언더샘플링, SMOTE 등으로 클래스 분포를 조정하세요." },
            { icon: "⚖️", text: "STEP 3: 평가지표 설정", coduckMsg: "정확도 대신 Precision, Recall, F1-Score, AUC-ROC를 사용하여 공정한 평가를 하세요." },
            { icon: "✔️", text: "STEP 4: 모니터링", coduckMsg: "소수 클래스의 성능도 함께 모니터링하여 공정성을 보장합니다." }
        ],

        blueprint: `
from imblearn.over_sampling import SMOTE
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score

# 1. Imbalance Detection: 클래스 분포 확인
print(y_train.value_counts())  # 1:99의 불균형 확인

# 2. Sampling Strategy: SMOTE로 소수 클래스 오버샘플링
smote = SMOTE(random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# 3. Metric Selection: 정확도 대신 F1-Score와 AUC-ROC 사용
precision, recall, f1, _ = precision_recall_fscore_support(y_test, predictions, average='weighted')
auc = roc_auc_score(y_test, pred_proba)
        `.trim(),

        blueprintSteps: [
            { id: "s1", python: "print(y_train.value_counts())", pseudo: "클래스 분포의 불균형을 진단하여 얼마나 심각한 문제인지 파악한다.", keywords: ["진단", "분포확인", "불균형", "DetectImbalance"] },
            { id: "s2", python: "smote = SMOTE(); X_balanced, y_balanced = smote.fit_resample(X_train, y_train)", pseudo: "SMOTE 기법을 사용하여 소수 클래스를 합성적으로 생성하고 균형을 맞춘다.", keywords: ["샘플링", "SMOTE", "오버샘플링", "BalanceClass"] },
            { id: "s3", python: "roc_auc_score(y_test, pred_proba)", pseudo: "정확도 대신 Precision, Recall, F1-Score, AUC-ROC 등 다중 평가 지표를 사용하여 공정한 성능 평가를 수행한다.", keywords: ["평가지표", "F1", "AUC", "Precision"] }
        ],

        interviewQuestions: [
            {
                id: "imbalance_1_choice",
                type: "CHOICE",
                question: "Q1. [불균형의 함정] 정확도 99%인 모델이 모든 거래를 '정상'으로 분류한 이유는?\n이 현상을 무엇이라고 부르나요?",
                options: [
                    { text: "모델이 제대로 학습되었고, 높은 정확도는 모델의 성능이 우수하다는 증거다.", correct: false, feedback: "정상 거래를 찾는 것이 아니라 이상 거래를 찾아야 하는데, 모든 것을 정상으로만 분류하는 것은 문제입니다." },
                    { text: "클래스 불균형 때문에 모델이 다수 클래스(정상)로만 편향된 예측을 한다. 이를 '다수 클래스 편향'이라고 한다.", correct: true, feedback: "정답입니다! 소수 클래스를 무시하는 현상을 '클래스 불균형(Class Imbalance)'이라 하며, 높은 정확도는 착각입니다." },
                    { text: "모델의 과소적합(Underfitting)으로 인한 문제다.", correct: false, feedback: "과소적합은 학습 성능부터 낮습니다. 이 경우는 명백히 다수 클래스에 대한 과적합입니다." },
                    { text: "더 많은 데이터를 수집하면 자동으로 해결된다.", correct: false, feedback: "불균형이 심한 상황에서 데이터만 추가하면 불균형이 더 심해집니다." }
                ],
                context: "불균형 데이터의 함정과 다수 클래스 편향"
            },
            {
                id: "imbalance_2_choice",
                type: "CHOICE",
                question: "Q2. [정확한 평가지표] 불균형 데이터에서 모델 성능을 평가할 때 정확도 대신 무엇을 사용해야 하나요?",
                options: [
                    { text: "정확도: 가장 직관적이고 이해하기 쉽기 때문이다.", correct: false, feedback: "불균형 데이터에서 정확도는 매우 호도적인 지표입니다." },
                    { text: "Precision, Recall, F1-Score, AUC-ROC: 소수 클래스 성능을 정확히 반영한다.", correct: true, feedback: "정답입니다! 이 지표들은 소수 클래스의 성능을 명시적으로 평가합니다." },
                    { text: "손실 함수(Loss)만 모니터링하면 된다.", correct: false, feedback: "손실 함수도 중요하지만, 최종적으로는 비즈니스 관점의 평가 지표가 필요합니다." },
                    { text: "정확도와 Recall을 더하면 충분하다.", correct: false, feedback: "두 지표를 더하는 것은 의미가 없습니다. F1-Score 같은 조화평균을 사용해야 합니다." }
                ],
                context: "불균형 데이터의 올바른 평가 방법"
            }
        ],

        designContext: {
            title: "[미션] 불균형 데이터 처리 설계",
            description: "1% 이상 거래를 정확히 탐지하면서도 정상 거래와의 균형을 맞추는 공정한 분류 시스템을 의사코드로 설계하세요. 단순한 정확도 개선을 넘어, 비즈니스 손실을 최소화하는 관점에서 접근하세요.",
            incidentCode: `
# 불균형의 함정
model = LogisticRegression()
model.fit(X_train, y_train)  # 99% 정상, 1% 이상
accuracy = 0.99  # 모든 거래를 정상으로 분류해도 99%!
anomaly_detected = 0  # 그런데 이상 거래는 하나도 찾지 못함
            `.trim(),
            incidentProblem: "모델이 다수 클래스(정상)에만 편향되어 소수 클래스(이상)를 거의 찾지 못함",
            currentIncident: `
⚖️ 경고: 분류 편향 감지
이상 거래 탐지 모델이 정확도가 높지만, 실제로는 모든 거래를 '정상'으로 분류하고 있습니다.
다수 클래스(정상 99%)에는 편향되었지만, 소수 클래스(이상 1%)는 거의 탐지하지 못합니다.

비즈니스 관점에서는 '정확도 99%'가 아닌 '이상 거래 탐지율 0%'이 더 중요합니다.
            `.trim(),
            engineeringRules: [
                "클래스 불균형을 먼저 진단하고 정량화한다.",
                "SMOTE, 오버샘플링, 언더샘플링 중 적절한 기법을 선택한다.",
                "정확도 대신 Precision, Recall, F1, AUC-ROC를 평가 지표로 사용한다.",
                "비즈니스 손실을 고려한 비용 함수(Cost Function)를 설계한다."
            ],
            writingGuide: `
[필수 포함 조건 (Constraint)]
다음 3가지 요소를 모두 포함하여 설계합니다:
불균형 진단 (Imbalance Detection): 클래스 분포 분석
샘플링 전략 (Sampling Strategy): SMOTE, 오버/언더샘플링 등
공정한 평가 (Fair Evaluation): Precision, Recall, F1, AUC-ROC
            `.trim()
        },

        deepDiveScenarios: [
            {
                id: "cost_sensitive",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "비용",
                title: "비용 민감 학습 시나리오",
                question: "이상 거래 1건을 놓치면 $10,000 손실이 발생하지만, 정상 거래를 잘못 거르면 $100 손실입니다. 이 비용 불균형을 모델에 어떻게 반영할까요?",
                intent: "비즈니스 가치를 고려한 머신러닝 설계 능력 확인.",
                scoringKeywords: ["클래스가중치", "비용함수", "class_weight", "sample_weight"],
                modelAnswer: "LogisticRegression이나 RandomForest의 class_weight='balanced'를 설정하거나, 명시적으로 class_weight 딕셔너리를 지정하여 이상 클래스에 더 높은 가중치를 부여합니다."
            },
            {
                id: "threshold_tuning",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "임계값",
                title: "분류 임계값 조정 시나리오",
                question: "로지스틱 회귀의 기본 임계값은 0.5입니다. 허위 경보가 많다면, 재정 거래를 더 엄격하게 판단하려면 임계값을 어떻게 조정해야 할까요?",
                intent: "Precision-Recall 트레이드오프를 이해하고 비즈니스 요구에 맞게 최적화하는 능력 확인.",
                scoringKeywords: ["임계값", "정밀도", "재현율", "ROC곡선"],
                modelAnswer: "임계값을 0.5에서 높여서(예: 0.7) 이상 판정을 더 보수적으로 만듭니다. 이렇게 하면 정밀도(Precision)가 높아지지만 재현율(Recall)이 낮아집니다. ROC 곡선을 분석하여 비즈니스 요구에 맞는 최적의 임계값을 찾습니다."
            },
            {
                id: "stratified_split",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "검증",
                title: "계층화된 분할 시나리오",
                question: "Train/Test 분할 시 불균형이 심한 데이터에서 무작위 분할을 하면 한쪽에 모든 이상 케이스가 몰릴 수 있습니다. 이를 방지하려면?",
                intent: "데이터 분할 시 통계적 대표성을 보장하는 기법 이해도 확인.",
                scoringKeywords: ["계층화분할", "StratifiedKFold", "대표성", "동등분포"],
                modelAnswer: "stratify 매개변수를 사용하여 '계층화된 분할(Stratified Split)'을 수행합니다. train_test_split(X, y, test_size=0.2, stratify=y)로 각 분할에서 클래스 비율을 동등하게 유지합니다."
            }
        ],

        checklist: [
            { id: 'check_diagnosis', label: '불균형 진단 (Imbalance Detection)', patterns: [/불균형|진단|분포|확인|detect|imbalance/i] },
            { id: 'check_sampling', label: '샘플링 전략 (Sampling Strategy)', patterns: [/샘플링|SMOTE|오버|언더|sampling|balance/i] },
            { id: 'check_evaluation', label: '공정한 평가 (Fair Evaluation)', patterns: [/평가|지표|F1|AUC|Precision|Recall|metric|fair/i] }
        ],
        placeholder: "불균형 진단, 샘플링 전략, 공정한 평가 원칙을 바탕으로 불균형 데이터 처리 설계를 서술하세요...\n예: 1. SMOTE를 사용하여 소수 클래스를 오버샘플링한다.",

        mapPos: { x: 500, y: 350 }
    },
    {
        id: 4,
        title: "피처 엔지니어링 최적화 설계",
        category: "Feature Master",
        emoji: "⚡",
        desc: "원본 데이터로부터 의미 있는 특성(Feature)을 창조하고, 불필요한 특성을 제거하여 모델 성능을 극대화합니다.",
        rewardXP: 700,
        subModuleTitle: "FEATURE_ENGINEERING",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },
        scenario: "온라인 쇼핑몰 고객 이탈 예측 모델이 구현되어야 합니다. 원본 데이터는 '구매금액', '방문횟수', '마지막방문일'뿐입니다. 이 3개의 원시 특성으로는 예측 성능이 68%에 불과합니다. 어떻게 의미 있는 특성들을 만들어낼까요?",

        cards: [
            { icon: "🔨", text: "STEP 1: 특성 생성", coduckMsg: "도메인 지식을 바탕으로 원본 데이터에서 새로운 특성을 창조하세요." },
            { icon: "📈", text: "STEP 2: 특성 변환", coduckMsg: "로그 변환, 정규화, 카테고리 인코딩으로 특성의 표현력을 강화합니다." },
            { icon: "🎯", text: "STEP 3: 특성 선택", coduckMsg: "중요도 분석으로 불필요한 특성을 제거하고 모델을 단순화하세요." },
            { icon: "🚀", text: "STEP 4: 성능 검증", coduckMsg: "특성 엔지니어링 후 모델 성능이 실제로 향상되었는지 검증합니다." }
        ],

        blueprint: `
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# 1. Feature Creation: 새로운 특성 창조
df['purchase_frequency'] = df['purchase_count'] / df['days_since_signup']
df['days_since_last_visit'] = (today - df['last_visit_date']).dt.days
df['engagement_score'] = df['purchase_amount'] * df['visit_count']

# 2. Feature Transformation: 특성 변환
df['log_purchase_amount'] = np.log1p(df['purchase_amount'])
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df[['purchase_frequency', 'engagement_score']])

# 3. Feature Selection: 중요도 기반 선택
model = RandomForestClassifier()
model.fit(X, y)
important_features = X.columns[model.feature_importances_ > 0.05]
        `.trim(),

        blueprintSteps: [
            { id: "s1", python: "df['purchase_frequency'] = df['purchase_count'] / df['days_since_signup']", pseudo: "원본 특성들을 조합하여 의미 있는 새로운 특성을 엔지니어링한다. (예: 구매빈도 = 구매횟수/가입일수)", keywords: ["생성", "조합", "도메인지식", "FeatureCreation"] },
            { id: "s2", python: "df['log_amount'] = np.log1p(df['amount'])", pseudo: "로그 변환, 정규화, 인코딩 등을 통해 특성의 분포를 개선하고 모델 학습을 촉진한다.", keywords: ["변환", "정규화", "스케일링", "FeatureTransformation"] },
            { id: "s3", python: "model.feature_importances_", pseudo: "모델 학습 후 특성 중요도를 분석하여 기여도가 낮은 특성을 제거함으로써 모델을 단순화한다.", keywords: ["선택", "중요도", "제거", "FeatureSelection"] }
        ],

        interviewQuestions: [
            {
                id: "feature_eng_1_choice",
                type: "CHOICE",
                question: "Q1. [특성 생성의 핵심] 왜 3개의 원시 특성이 아닌, 새롭게 만든 특성들이 더 효과적일까요?\n그 이유는?",
                options: [
                    { text: "더 많은 특성이 있으면 무조건 모델 성능이 좋아진다.", correct: false, feedback: "특성의 개수가 아니라 품질과 의미가 중요합니다." },
                    { text: "원시 특성들이 이미 모든 정보를 담고 있으므로 조합할 필요가 없다.", correct: false, feedback: "각 특성 간의 상호작용과 파생된 의미를 포착하는 것이 머신러닝의 핵심입니다." },
                    { text: "새 특성은 데이터가 담은 숨은 패턴과 도메인 지식을 모델이 쉽게 학습할 수 있도록 정보를 '압축'하고 '강조'한다.", correct: true, feedback: "정답입니다! 좋은 피처 엔지니어링은 도메인 지식으로 모델의 학습 난제를 사전에 해결합니다." },
                    { text: "단순히 계산량을 늘려서 모델을 더 복잡하게 만든다.", correct: false, feedback: "피처 엔지니어링의 목표는 복잡함이 아니라 명확한 신호 강화입니다." }
                ],
                context: "피처 엔지니어링의 목적과 가치"
            },
            {
                id: "feature_eng_2_choice",
                type: "CHOICE",
                question: "Q2. [특성 선택의 중요성] 많은 특성이 항상 좋은 성능을 보장할까요?\n왜 일부 특성을 제거해야 할까요?",
                options: [
                    { text: "더 많은 특성이 있을수록 모델이 더 정교하고 강력해진다.", correct: false, feedback: "오히려 불필요한 특성이 많으면 노이즈가 증가하여 성능이 떨어집니다." },
                    { text: "불필요한 특성은 모델의 성능을 해치며(과적합 유발), 계산 비용을 증가시킨다.", correct: true, feedback: "정답입니다! 특성 선택은 모델의 생산성과 성능, 해석성을 모두 개선합니다." },
                    { text: "웹 기반 모델에서는 특성 수가 적을수록 빨라지지만, 학습에는 영향이 없다.", correct: false, feedback: "불필요한 특성은 학습 성능까지 악영향을 미칩니다." },
                    { text: "모든 특성은 동등한 영향을 미치므로 선택할 필요가 없다.", correct: false, feedback: "실제로는 특성마다 모델에 미치는 영향이 크게 다릅니다." }
                ],
                context: "특성 선택을 통한 모델 최적화"
            }
        ],

        designContext: {
            title: "[미션] 피처 엔지니어링 최적화 설계",
            description: "3개의 원시 특성(구매금액, 방문횟수, 마지막방문일)으로부터 시작하여, 의미 있는 파생 특성을 창조하고, 특성 변환과 선택을 통해 모델 성능을 68%에서 85% 이상으로 끌어올리는 엔지니어링 전략을 의사코드로 설계하세요.",
            incidentCode: `
# 원시 특성만 사용
X = df[['purchase_amount', 'visit_count', 'last_visit_date']]
model = LogisticRegression()
model.fit(X, y)
accuracy = 0.68  # 낮은 성능
            `.trim(),
            incidentProblem: "원시 특성만으로는 고객 이탈 패턴을 충분히 포착하지 못함",
            currentIncident: `
⚡ 알림: 저조한 예측 성능
고객 이탈 예측 모델의 정확도가 68%로 매우 낮습니다.
현재 사용하는 특성(구매금액, 방문횟수, 마지막방문일)은 너무 원시적이어서
고객의 진정한 이탈 신호를 포착하지 못하고 있습니다.

도메인 지식을 활용한 피처 엔지니어링이 시급합니다.
            `.trim(),
            engineeringRules: [
                "도메인 지식에 기반하여 비즈니스적으로 의미 있는 특성을 창조한다.",
                "특성의 분포를 분석하고 필요시 변환(로그, 정규화 등)을 수행한다.",
                "특성 간 상관성을 제거하여 모델의 안정성을 높인다.",
                "특성 중요도 분석을 통해 불필요한 특성을 제거한다."
            ],
            writingGuide: `
[필수 포함 조건 (Constraint)]
다음 3가지 작업을 순서대로 수행하고 설명합니다:
특성 창조 (Feature Creation): 도메인 지식으로 새로운 특성 정의
특성 변환 (Feature Transformation): 분포 개선 및 스케일링
특성 선택 (Feature Selection): 중요도 기반 최적화
            `.trim()
        },

        deepDiveScenarios: [
            {
                id: "feature_interaction",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "상호작용",
                title: "특성 상호작용 시나리오",
                question: "단일 특성으로는 패턴을 못 찾지만, 두 특성의 곱이나 비율은 강한 신호를 보입니다. 모델이 자동으로 상호작용을 학습할까요, 아니면 수동으로 생성해야 할까요?",
                intent: "선형 모델과 비선형 모델의 특성 상호작용 처리 방식 이해도 확인.",
                scoringKeywords: ["상호작용", "선형", "비선형", "다항특성", "PolynomialFeatures"],
                modelAnswer: "선형 모델(로지스틱 회귀, SVM)은 상호작용 특성을 수동으로 만들어야 합니다. 반면 트리 기반 모델(Random Forest, XGBoost)은 상호작용을 자동으로 학습합니다. PolynomialFeatures를 사용하여 자동으로 상호작용 특성을 생성할 수도 있습니다."
            },
            {
                id: "feature_scaling",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "스케일",
                title: "특성 스케일링 시나리오",
                question: "구매금액은 0-1000만 원, 방문횟수는 0-500입니다. 스케일 차이가 큰데, 정규화를 하지 않으면 어떻게 될까요?",
                intent: "특성 정규화의 중요성과 효과 이해도 확인.",
                scoringKeywords: ["정규화", "표준화", "스케일링", "StandardScaler"],
                modelAnswer: "스케일이 큰 특성(구매금액)이 모델의 학습을 지배하게 되어 작은 스케일의 중요한 신호(방문횟수)가 무시됩니다. StandardScaler나 MinMaxScaler로 정규화하여 모든 특성을 동등한 스케일로 맞춰야 합니다."
            },
            {
                id: "feature_curse",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "차원",
                title: "차원의 저주 시나리오",
                question: "특성을 100개로 늘렸는데, 성능이 더 나빠졌습니다. 왜 이런 현상이 발생할까요? 그리고 해결책은?",
                intent: "차원의 저주를 이해하고 고차원 데이터 처리 능력 확인.",
                scoringKeywords: ["차원축소", "PCA", "과적합", "희소성"],
                modelAnswer: "특성이 너무 많으면 모델이 노이즈까지 학습하는 과적합이 발생하고, 필요한 샘플 수가 기하급수적으로 증가합니다. PCA, SelectKBest, RFE 등의 차원 축소 기법을 사용하여 의미 있는 특성만 선택합니다."
            }
        ],

        checklist: [
            { id: 'check_creation', label: '특성 창조 (Feature Creation)', patterns: [/창조|생성|파생|조합|creation/i] },
            { id: 'check_transformation', label: '특성 변환 (Feature Transformation)', patterns: [/변환|스케일링|정규화|로그|transformation|scaling/i] },
            { id: 'check_feature_selection', label: '특성 선택 (Feature Selection)', patterns: [/선택|중요도|제거|selection/i] }
        ],
        placeholder: "특성 창조, 변환, 선택 원칙을 바탕으로 피처 엔지니어링 전략을 서술하세요...\n예: 1. 도메인 지식을 활용해 파생 특성을 생성한다.",

        mapPos: { x: 700, y: 350 }
    },
    {
        id: 5,
        title: "하이퍼파라미터 튜닝 전략 설계",
        category: "Tuning Master",
        emoji: "🎛️",
        desc: "모델의 동작 방식을 결정하는 하이퍼파라미터를 체계적으로 최적화하여 모델의 성능을 극대화합니다.",
        rewardXP: 750,
        subModuleTitle: "HYPERPARAMETER_TUNING",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },
        scenario: "Random Forest로 이미지 분류를 구현하려 합니다. n_estimators, max_depth, min_samples_split 등 수십 개의 파라미터가 있는데, 각각의 기본값을 그대로 사용한 모델의 성능은 78%입니다. 이 모델을 88% 이상으로 개선할 수 있을까요?",

        cards: [
            { icon: "🔍", text: "STEP 1: 파라미터 공간 정의", coduckMsg: "튜닝할 하이퍼파라미터와 그 범위를 정의하세요." },
            { icon: "🔎", text: "STEP 2: 탐색 전략 선택", coduckMsg: "그리드 탐색(Grid Search), 랜덤 탐색(Random Search), 베이지안 최적화 중 적절한 전략을 선택합니다." },
            { icon: "📊", text: "STEP 3: 교차검증 수행", coduckMsg: "K-Fold 교차검증으로 과적합 없이 신뢰할 수 있는 성능을 평가합니다." },
            { icon: "🏆", text: "STEP 4: 최적 파라미터 확정", coduckMsg: "가장 좋은 성능을 보인 파라미터 조합을 선택하고 최종 검증합니다." }
        ],

        blueprint: `
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score

# 1. Parameter Space: 파라미터 공간 정의
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15, 20],
    'min_samples_split': [2, 5, 10]
}

# 2. Search Strategy: 그리드 탐색 수행
grid_search = GridSearchCV(
    RandomForestClassifier(),
    param_grid,
    cv=5,  # 5-Fold 교차검증
    scoring='accuracy'
)

# 3. Model Fitting: 최적 파라미터 찾기
grid_search.fit(X_train, y_train)

# 4. Best Parameters: 최적 파라미터 확인
best_params = grid_search.best_params_
best_model = grid_search.best_estimator_
        `.trim(),

        blueprintSteps: [
            { id: "s1", python: "param_grid = {'n_estimators': [50, 100, 200], ...}", pseudo: "튜닝할 하이퍼파라미터와 그 값의 범위를 딕셔너리 형태로 정의한다.", keywords: ["정의", "범위", "파라미터", "ParamSpace"] },
            { id: "s2", python: "GridSearchCV(..., cv=5)", pseudo: "K-Fold 교차검증과 함께 그리드 탐색을 수행하여 모든 파라미터 조합의 성능을 평가한다.", keywords: ["탐색", "교차검증", "조합", "GridSearch"] },
            { id: "s3", python: "best_params = grid_search.best_params_", pseudo: "가장 좋은 검증 성능을 보인 파라미터 조합을 추출하고 이를 최종 모델에 적용한다.", keywords: ["선택", "최적화", "확정", "BestParams"] }
        ],

        interviewQuestions: [
            {
                id: "tuning_1_choice",
                type: "CHOICE",
                question: "Q1. [튜닝의 목표] 하이퍼파라미터 튜닝을 통해 얻을 수 있는 가장 큰 이점은 무엇인가요?",
                options: [
                    { text: "알고리즘을 더 복잡하게 만들어서 모델의 능력을 향상시킨다.", correct: false, feedback: "더 복잡하다고 성능이 좋아지는 것은 아닙니다." },
                    { text: "기본값(default)의 파라미터는 모든 데이터셋에 최적이므로 튜닝의 필요가 없다.", correct: false, feedback: "기본값은 범용적인 설정일 뿐, 특정 데이터셋에는 최적이 아닙니다." },
                    { text: "각 데이터셋과 문제의 특성에 맞게 모델의 동작을 미세 조정하여 성능을 극대화한다.", correct: true, feedback: "정답입니다! 하이퍼파라미터 튜닝은 데이터와 문제에 맞춘 모델 최적화의 핵심입니다." },
                    { text: "더 강력한 컴퓨터를 사용하는 것과 같은 효과를 낸다.", correct: false, feedback: "튜닝은 소프트웨어 최적화이지, 하드웨어 문제가 아닙니다." }
                ],
                context: "하이퍼파라미터 튜닝의 목적과 가치"
            },
            {
                id: "tuning_2_choice",
                type: "CHOICE",
                question: "Q2. [탐색 전략의 선택] 그리드 탐색(Grid Search) vs 랜덤 탐색(Random Search)?\n언제 어떤 것을 사용해야 하나요?",
                options: [
                    { text: "그리드 탐색은 모든 조합을 시도하므로 항상 더 나은 결과를 낸다.", correct: false, feedback: "더 나은 결과를 낸다는 것이 항상 참은 아니며, 계산량이 매우 많아집니다." },
                    { text: "랜덤 탐색은 빠르지만 최적값을 놓칠 가능성이 높다.", correct: false, feedback: "오히려 랜덤 탐색이 더 효율적일 때가 많으며, 놓칠 가능성도 낮습니다." },
                    { text: "파라미터가 적고 계산 시간이 충분하면 그리드 탐색, 파라미터가 많고 시간이 제한적이면 랜덤 탐색을 사용한다.", correct: true, feedback: "정답입니다! 문제의 규모와 제약 조건에 따라 적절한 전략을 선택해야 합니다." },
                    { text: "항상 랜덤 탐색을 사용해야 최신 머신러닝 기법이다.", correct: false, feedback: "기법의 신구가 아니라, 문제에 맞는 선택이 중요합니다." }
                ],
                context: "탐색 전략의 선택과 트레이드오프"
            }
        ],

        designContext: {
            title: "[미션] 하이퍼파라미터 튜닝 전략 설계",
            description: "78%의 기본 성능을 88% 이상으로 끌어올리기 위해, Random Forest의 주요 하이퍼파라미터(n_estimators, max_depth, min_samples_split 등)를 체계적으로 튜닝하는 전략을 의사코드로 설계하세요. 계산 효율성도 고려하여 작성하세요.",
            incidentCode: `
# 기본값으로 설정한 모델
model = RandomForestClassifier()  # 기본값 사용
model.fit(X_train, y_train)
accuracy = 0.78  # 충분하지 않은 성능
            `.trim(),
            incidentProblem: "기본 하이퍼파라미터로는 특정 데이터셋의 특성을 활용하지 못함",
            currentIncident: `
🎛️ 알림: 튜닝 필요
Random Forest 모델의 기본값 사용 시 정확도가 78%로 목표(88%)에 미치지 못합니다.
주요 하이퍼파라미터의 체계적인 최적화가 필요합니다.
            `.trim(),
            engineeringRules: [
                "튜닝할 주요 파라미터를 선정한다 (예: n_estimators, max_depth, min_samples_split).",
                "각 파라미터의 탐색 범위를 정렬한다.",
                "계산 효율성을 고려하여 그리드 탐색 또는 랜덤 탐색을 선택한다.",
                "K-Fold 교차검증으로 안정적인 성능을 평가한다."
            ],
            writingGuide: `
[필수 포함 조건 (Constraint)]
다음 3가지 요소를 포함하여 설계합니다:
파라미터 공간 (Parameter Space): 튜닝 대상과 범위
탐색 전략 (Search Strategy): 그리드/랜덤/베이지안
교차검증 (Cross-Validation): K-Fold를 통한 신뢰도 확보
            `.trim()
        },

        deepDiveScenarios: [
            {
                id: "early_stopping",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "효율성",
                title: "조기종료를 통한 효율화 시나리오",
                question: "그리드 탐색으로 100개의 파라미터 조합을 시도하려 하는데, 계산 시간이 하루 이상입니다. 시간을 줄이면서도 좋은 파라미터를 찾을 방법은?",
                intent: "계산 효율성과 결과 품질의 균형을 고려한 실무 능력 확인.",
                scoringKeywords: ["HalvingGridSearch", "조기종료", "베이지안최적화", "효율성"],
                modelAnswer: "HalvingGridSearch를 사용하여 처음에는 모든 조합을 빠르게 평가한 후, 성능이 좋은 조합들만 반복적으로 정밀 평가합니다. 또는 Optuna 같은 베이지안 최적화 라이브러리로 효율적으로 탐색합니다."
            },
            {
                id: "param_interaction",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "상호작용",
                title: "파라미터 상호작용 시나리오",
                question: "n_estimators가 높으면 max_depth는 낮게, n_estimators가 낮으면 max_depth는 높게 설정해야 한다는 말이 있습니다. 이는 사실일까요?",
                intent: "파라미터 간의 상호작용 효과를 이해하고 활용하는 능력 확인.",
                scoringKeywords: ["상호작용", "트레이드오프", "균형", "앙상블"],
                modelAnswer: "부분적으로 사실입니다. 트리 개수가 많으면(n_estimators 높음) 각 트리의 복잡도를 낮추어(max_depth 낮춤) 다양성을 유지합니다. 반대로 트리 개수가 적으면 각 트리를 더 깊게 학습시킵니다. GridSearch는 이런 상호작용도 자동으로 고려합니다."
            },
            {
                id: "transfer_learning",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "전이",
                title: "파라미터 이전학습 시나리오",
                question: "A 회사의 유사한 분류 문제에서 찾은 최적 하이퍼파라미터를 B 회사의 같은 종류의 문제에 직접 적용할 수 있을까요?",
                intent: "파라미터의 일반화 가능성과 문제 특성의 중요성 이해도 확인.",
                scoringKeywords: ["전이학습", "도메인차이", "미세조정", "Warm-start"],
                modelAnswer: "직접 적용보다는 '시작점(Warm-start)'으로 사용하는 것이 좋습니다. A 회사의 최적 파라미터를 초기값으로 설정한 후, B 회사의 데이터로 미세 조정(Fine-tuning)하면 학습 시간을 크게 단축할 수 있습니다."
            }
        ],

        checklist: [
            { id: 'check_space', label: '파라미터 공간 (Parameter Space)', patterns: [/공간|범위|정의|param|space/i] },
            { id: 'check_search', label: '탐색 전략 (Search Strategy)', patterns: [/탐색|전략|그리드|랜덤|그리드서치|search|strategy/i] },
            { id: 'check_cv', label: '교차검증 (Cross-Validation)', patterns: [/교차검증|신뢰|K-Fold|cv|valid/i] }
        ],
        placeholder: "파라미터 공간, 탐색 전략, 교차검증 원칙을 바탕으로 하이퍼파라미터 튜닝 전략을 서술하세요...\n예: 1. GridSearchCV로 최적의 파라미터를 탐색한다.",

        mapPos: { x: 900, y: 350 }
    },
    {
        id: 6,
        title: "모델 해석성과 설명가능성 설계",
        category: "Explainability",
        emoji: "🔬",
        desc: "블랙박스 모델의 의사결정 원리를 해석하여 모델의 신뢰성을 확보하고, 이해 가능한 AI 시스템을 설계합니다.",
        rewardXP: 800,
        subModuleTitle: "EXPLAINABILITY_SYSTEM",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },
        scenario: "신용 대출 심사 AI 모델이 성공적으로 구축되어 성능도 92%입니다. 하지만 고객이 '왜 내 대출이 거절되었는가'를 물어봤을 때, 모델은 답할 수 없습니다. 규제 당국도 '차별 없는 공정한 의사결정'의 증거를 요구합니다. 이 블랙박스를 어떻게 투명하게 열어낼까요?",

        cards: [
            { icon: "🎯", text: "STEP 1: 중요도 분석", coduckMsg: "어떤 특성이 모델의 결정에 가장 큰 영향을 미쳤는지 파악하세요." },
            { icon: "📍", text: "STEP 2: 개별 예측 해석", coduckMsg: "SHAP, LIME 등의 기법으로 특정 고객의 대출 거절 이유를 설명합니다." },
            { icon: "⚖️", text: "STEP 3: 차별 감지", coduckMsg: "모델이 특정 집단에 대해 편향되지 않았는지 검증하세요." },
            { icon: "📢", text: "STEP 4: 투명성 보고", coduckMsg: "고객과 규제당국에 설명 가능한 형태로 의사결정 근거를 제시합니다." }
        ],

        blueprint: `
import shap
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# 1. Global Importance: 특성 중요도 분석
model = RandomForestClassifier()
model.fit(X_train, y_train)
importances = model.feature_importances_
important_features = X.columns[np.argsort(importances)[::-1][:5]]

# 2. Local Explanation: 개별 예측 해석
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
shap.force_plot(explainer.expected_value[1], shap_values[1], X_test.iloc[0])

# 3. Bias Detection: 차별 감지
protected_attr = X['gender']
model_predictions = model.predict(X_test)
# 성별로 그룹화하여 성능 비교
        `.trim(),

        blueprintSteps: [
            { id: "s1", python: "model.feature_importances_", pseudo: "학습된 모델에서 각 특성이 전체 의사결정에 미치는 영향도를 계산하는 전역적 해석을 수행한다.", keywords: ["해석", "중요도", "특성", "GlobalExplanation"] },
            { id: "s2", python: "shap_values = explainer.shap_values(X_test)", pseudo: "SHAP이나 LIME 같은 기법을 사용하여 특정 사례의 모델 예측을 개별적으로 해석한다.", keywords: ["설명", "SHAP", "개별", "LocalExplanation"] },
            { id: "s3", python: "# 성별로 그룹화하여 성능 비교", pseudo: "보호되는 속성(성별, 나이 등)에 대해 모델의 성능 및 결정에 편향이 있는지 검증한다.", keywords: ["검증", "편향", "공정성", "BiasDetection"] }
        ],

        interviewQuestions: [
            {
                id: "explain_1_choice",
                type: "CHOICE",
                question: "Q1. [설명가능성의 필요성] 92% 정확도의 모델이 있는데, 왜 '왜?'라는 질문에 답해야 할까요?\n설명가능성이 중요한 이유는?",
                options: [
                    { text: "성능이 좋으면 설명할 필요가 없다. 높은 정확도가 신뢰성의 증거다.", correct: false, feedback: "성능과 신뢰성은 다른 개념입니다. 규제, 윤리, 사용자 신뢰 등이 중요합니다." },
                    { text: "금융, 의료, 법률 같은 규제 산업에서는 의사결정의 근거를 반드시 설명할 수 있어야 한다. 또한 고객 신뢰와 편향 감시도 필수적이다.", correct: true, feedback: "정답입니다! 설명가능성은 법이 요구하고, 신뢰를 구축하며, 편향을 감시합니다." },
                    { text: "모델이 복잡할수록 성능이 좋으므로, 단순히 이해 가능한 모델로는 안 된다.", correct: false, feedback: "복잡성과 해석가능성의 트레이드오프가 있지만, 설명가능한 기법들로 해결할 수 있습니다." },
                    { text: "사용자가 모델의 결정에 의문하지 않으면 설명할 필요가 없다.", correct: false, feedback: "능동적 투명성이 핵심입니다. 사용자의 의문 여부와 관계없이 설명 가능해야 합니다." }
                ],
                context: "모델 설명가능성의 중요성과 필요성"
            },
            {
                id: "explain_2_choice",
                type: "CHOICE",
                question: "Q2. [해석 방법의 선택] 특정 고객의 대출 거절 이유를 설명할 때 사용하는 '전역적 해석(특성 중요도)'과 '개별적 해석(SHAP, LIME)'의 차이는?\n어떤 상황에서 어떤 것을 사용해야 하나요?",
                options: [
                    { text: "특성 중요도만 있으면 충분하며, 개별적 해석은 불필요하다.", correct: false, feedback: "두 가지는 서로 다른 관점을 제공합니다." },
                    { text: "특성 중요도(전역적)는 모델 전체의 의사결정 기준을, SHAP/LIME(개별적)은 특정 고객의 거절 이유를 설명한다.", correct: true, feedback: "정답입니다! 둘 다 필요하며, 다른 수준의 통찰을 제공합니다." },
                    { text: "SHAP과 LIME은 동일한 기법이므로 어느 것을 사용해도 상관없다.", correct: false, feedback: "기본 원리는 비슷하지만, 작동 방식과 효율성이 다릅니다." },
                    { text: "성능이 좋으면 특성 중요도도 반드시 높다.", correct: false, feedback: "성능과 해석성은 독립적일 수 있습니다." }
                ],
                context: "해석 방법의 선택과 적용"
            }
        ],

        designContext: {
            title: "[미션] 모델 설명가능성 및 투명성 설계",
            description: "92% 정확도의 대출 심사 AI가 거절 고객에게 '왜 거절되었는가'를 명확히 설명할 수 있도록, 그리고 규제당국에 '공정하고 편향 없는 의사결정'임을 증명할 수 있도록 하는 해석가능성 시스템을 의사코드로 설계하세요.",
            incidentCode: `
# 성능은 좋지만 설명할 수 없는 블랙박스
model = GradientBoostingClassifier()
model.fit(X_train, y_train)
accuracy = 0.92  # 높은 성능
predictions = model.predict(X_test)
# 하지만 '왜 거절되었는가'에 답할 수 없음
            `.trim(),
            incidentProblem: "높은 성능에도 불구하고 모델의 의사결정 근거를 설명할 수 없음",
            currentIncident: `
🔬 경고: 투명성 부족
대출 심사 모델의 성능은 92%로 매우 우수합니다.
하지만 거절된 고객에게 '왜 거절되었는가'를 설명할 수 없습니다.
규제당국도 '공정한 의사결정의 증거'를 요구하고 있습니다.

모델의 블랙박스를 투명하게 개방해야 합니다.
            `.trim(),
            engineeringRules: [
                "모델 전체의 의사결정 기준을 '특성 중요도'로 파악한다.",
                "개별 예측별로 '정확한 기여도'를 계산하는 SHAP/LIME을 적용한다.",
                "보호되는 속성(성별, 인종 등)에 대한 편향을 체계적으로 감지한다.",
                "고객과 규제당국에 이해 가능한 형태로 설명을 제시한다."
            ],
            writingGuide: `
[필수 포함 조건 (Constraint)]
다음 3가지 해석 수준을 포함하여 설계합니다:
전역적 해석 (Global Interpretation): 특성 중요도 분석
개별적 해석 (Local Interpretation): SHAP/LIME을 통한 개별 예측 해석
공정성 검증 (Fairness Validation): 보호 속성에 대한 편향 감시
            `.trim()
        },

        deepDiveScenarios: [
            {
                id: "fairness_bias",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "공정성",
                title: "편향 감지 및 완화 시나리오",
                question: "모델이 여성 지원자에게는 거의 대출을 승인하지 않습니다. 성별이 특성에 없는데도 이런 일이 가능할까요? 이를 어떻게 해결할까요?",
                intent: "간접적 차별(Proxy Bias)과 인과성 추론의 중요성 이해도 확인.",
                scoringKeywords: ["대리변수", "프록시", "인과성", "편향완화"],
                modelAnswer: "성별이 명시적 특성이 아니어도, 직업, 이름, 거주지역 같은 다른 특성과 연관되어 있을 수 있습니다(대리 변수/Proxy). 편향을 완화하려면 불공정한 대리 변수를 제거하거나, 대리 특성을 중립화하거나, 공정성 제약을 학습에 추가해야 합니다."
            },
            {
                id: "model_transparency",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "투명성",
                title: "블랙박스 vs 글래스박스 시나리오",
                question: "신경망(블랙박스)의 성능이 92%이고, 의사결정나무(설명 가능)의 성능이 84%입니다. 설명가능성을 위해 8%의 성능을 포기해야 할까요?",
                intent: "성능과 해석가능성의 트레이드오프에 대한 실무적 판단 능력 확인.",
                scoringKeywords: ["SHAP", "LIME", "대리모델", "설명가능성"],
                modelAnswer: "성능을 완전히 포기할 필요는 없습니다. SHAP이나 LIME 같은 '해석 가능하게 하는 기법(Post-hoc Explanations)'을 신경망에 적용하거나, 신경망을 학습시킨 후 그 결과로 설명 가능한 대리 모델을 만들 수 있습니다."
            },
            {
                id: "counterfactual_explain",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "행동",
                title: "반사실적 설명 시나리오",
                question: "고객이 '내가 뭘 바꾸면 대출이 승인될까?'를 묻습니다. 어떤 최소한의 변화가 필요한지 데이터로 제시할 수 있을까요?",
                intent: "사용자 중심의 실행 가능한(Actionable) 설명 설계 능력 확인.",
                scoringKeywords: ["반사실", "actionable", "최소변화", "counterfactual"],
                modelAnswer: "반사실적 설명(Counterfactual Explanation)을 사용합니다. 모델의 의사결정을 바꿀 수 있는 최소한의 특성 변화를 계산하여, '소득을 $5,000 올리고 신용 점수를 50점 올리면 승인 가능'처럼 실행 가능한 조언을 제시합니다."
            }
        ],

        checklist: [
            { id: 'check_global', label: '전역적 해석 (Global Interpretation)', patterns: [/전역|해석|중요도|global/i] },
            { id: 'check_local', label: '개별적 해석 (Local Interpretation)', patterns: [/개별|해석|SHAP|LIME|local/i] },
            { id: 'check_fairness', label: '공정성 검증 (Fairness Validation)', patterns: [/공정|검증|편향|차별|fair|bias/i] }
        ],
        placeholder: "전역적 해석, 개별적 해석, 공정성 검증 원칙을 바탕으로 모델 해석 시스템을 설계하세요...\n예: 1. SHAP 값을 계산하여 개별 예측의 기여도를 분석한다.",

        mapPos: { x: 1100, y: 350 }
    }
];