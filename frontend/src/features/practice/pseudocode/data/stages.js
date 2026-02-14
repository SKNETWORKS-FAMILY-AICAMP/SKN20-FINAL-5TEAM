// ========================================
// stages.js - Quest 완전판
// [2026-02-14] 5차원 메트릭 및 2단계 검증(Trigger MCQ -> 3대 시나리오 Deep Dive) 통합
// ========================================

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
                scoringKeywords: ["모니터링", "재학습", "기준점 갱신", "Retraining"]
            },
            {
                id: "realtime",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "환경",
                title: "실시간 서빙 시나리오",
                question: "0.1초 내 응답이 필요한 시스템입니다. 매번 격리와 기준점(fit) 계산을 반복할 순 없는데, 정확도를 지키며 속도를 확보할 엔지니어링적 방법은 무엇인가요?",
                intent: "학습 시의 상태를 서빙 환경으로 전이하는 직렬화 기술 확인.",
                scoringKeywords: ["Pickle", "Joblib", "직렬화", "객체화", "Serialization"]
            },
            {
                id: "scarcity",
                type: "SCENARIO_DESCRIPTIVE",
                axis: "한계",
                title: "데이터 부족 및 불균형 시나리오",
                question: "데이터가 100건뿐이라 격리를 하면 학습이 안 되고, 안 하자니 오염이 걱정됩니다. 원칙을 지키면서도 모델을 제대로 검증할 전략은?",
                intent: "소량 데이터셋에서의 통계적 유의성 확보 능력 확인.",
                scoringKeywords: ["K-Fold", "Stratified", "교차 검증", "층화"]
            }
        ],

        mapPos: { x: 100, y: 450 }
    }
    // ... 추가 스테이지는 Quest 1과 동일한 구조로 확장 가능
];