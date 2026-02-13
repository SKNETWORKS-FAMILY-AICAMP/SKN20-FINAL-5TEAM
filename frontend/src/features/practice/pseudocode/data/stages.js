// ========================================
// stages.js - Quest 완전판
// [2026-02-14] validationRules_COMPLETE.js 통합
// ========================================

import { VALIDATION_LIBRARY, CODE_VALIDATION_LIBRARY } from './validationRules_COMPLETE.js';

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
            // [2026-02-11] 사고 코드 및 문제 설명 데이터 (이미지 반영)
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
            // [2026-02-12] 사용자 요청: 필수 포함 조건 및 미션 상세 반영
            writingGuide: `
[필수 포함 조건 (Constraint)]
답이 여러 갈래로 튀지 않도록 다음 3가지 키워드를 반드시 사용하여 논리를 구성하게 합니다:
격리 (Isolation): 데이터를 나누는 시점
기준점 (Anchor): 통계량(fit)을 추출할 대상
일관성 (Consistency): 학습과 운영 환경의 동일한 변환 방식
            `.trim()
        },
        validation: VALIDATION_LIBRARY.data_leakage,

        // ✅ 🔥 핵심 수정 2: CodeValidator용 완전한 codeValidation 구조
        // 피드백 2 반영: fit_transform 금지 패턴 추가
        codeValidation: {
            // 필수 메서드 호출
            requiredCalls: [
                {
                    pattern: /\.fit\s*\(/i,
                    name: 'fit() 메서드',
                    mustNotContainIn: 'comments'
                },
                {
                    pattern: /\.transform\s*\(/i,
                    name: 'transform() 메서드',
                    mustNotContainIn: 'comments'
                },
                {
                    pattern: /StandardScaler\s*\(|MinMaxScaler\s*\(|Normalizer\s*\(/i,
                    name: 'Scaler 객체 생성',
                    mustNotContainIn: 'comments'
                }
            ],

            // 금지 패턴 (주석 제외하고 검사)
            forbiddenPatterns: [
                {
                    pattern: /\.fit\s*\(\s*.*test/i,
                    message: '🚨 테스트 데이터로 fit 호출 금지',
                    excludeComments: true,
                    studyKeywords: ['Test Data Isolation']
                },
                {
                    pattern: /\.fit\s*\(.*concat|merge/i,
                    message: '🚨 병합된 데이터로 fit 금지',
                    excludeComments: true,
                    studyKeywords: ['Fit before Split']
                },
                {
                    // ✅ 피드백 2: fit_transform 금지 패턴 추가
                    pattern: /\.fit_transform\s*\(\s*.*test/i,
                    message: '🚨 치명적 오류: test 데이터에 fit_transform 절대 금지!',
                    excludeComments: true,
                    explanation: 'fit_transform은 fit과 transform을 동시에 수행합니다. test에는 transform만 해야 합니다.',
                    studyKeywords: ['fit_transform vs transform', 'Test Data Must Not Be Fitted']
                },
                {
                    // ✅ 추가: 전체 데이터 fit_transform 금지
                    pattern: /pd\.concat.*fit_transform|fit_transform.*pd\.concat/i,
                    message: '🚨 전체 데이터를 합친 후 fit_transform 금지',
                    excludeComments: true,
                    explanation: '데이터를 합치면 테스트 정보가 학습에 유입됩니다.',
                    studyKeywords: ['Data Concatenation Risk']
                }
            ],

            // 주석 패턴 (제거할 부분)
            commentPatterns: [
                /#.*$/gm,           // Python single-line
                /"""[\s\S]*?"""/g,  // Python docstring
                /'''[\s\S]*?'''/g   // Python docstring alt
            ],

            // ✅ 허용 패턴 (긍정 피드백)
            allowedPatterns: [
                {
                    pattern: /scaler\.fit\s*\(\s*train/i,
                    message: '✅ 올바른 패턴: train 데이터로 fit',
                    praise: true
                },
                {
                    pattern: /scaler\.fit_transform\s*\(\s*train/i,
                    message: '✅ 허용: train 데이터에만 fit_transform 사용 가능',
                    praise: true,
                    explanation: 'train 데이터는 fit_transform을 써도 됩니다 (fit + transform 결합).'
                }
            ]
        },

        deepDiveQuestion: {
            question: "당신의 검증 규칙을 다른 코드베이스에 적용했더니, Pipeline으로 감싸진 전처리 코드를 통과시켜 버렸습니다. 이유가 무엇일까요?",
            options: [
                { text: "fit_transform()을 사용했기 때문에 단일 메서드라 검출 못 함", correct: true },
                { text: "Pipeline으로 감싸면 자동으로 안전해지므로 문제없음", correct: false },
                { text: "df_normalized 변수명 때문에 패턴 매칭 실패", correct: false }
            ],
            correctIdx: 0
        },

        // ✅ 🔥 핵심 수정 3: evaluation 구조 정리
        // 피드백 3 반영: LLM 프롬프트에 학습 키워드 제시 강화
        evaluation: {
            // AI 기반 평가 (레이더 차트용)
            llmRubric: {
                system: `너는 AI/ML 아키텍처 관점에서 사고 흐름을 평가하는 시니어 엔지니어이자 면접관이다.

평가 철학:
- 정답 채점 ❌ → 사고력 평가 ✅
- 단순 키워드 매칭이 아닌 논리적 연결성 검증
- 점수 인플레이션 방지: 완벽하지 않으면 100점을 주지 마라

점수 분포 가이드:
- 90-100점: 완벽한 논리 + 예외처리 + 실무 통찰
- 75-89점: 핵심은 정확하나 디테일 부족
- 60-74점: 방향은 맞지만 논리적 비약 존재
- 40-59점: 일부 개념 이해하나 오개념 혼재
- 0-39점: 핵심 오개념 또는 무관한 내용`,

                promptTemplate: `
# 평가 대상

## 문제 (Quest Title)
${'{'}quest_title{'}'}

## 사용자가 작성한 설계 설명 (의사코드/자연어)
${'{'}narrative{'}'}

## 사용자가 작성한 코드
${'{'}code{'}'}

---

# 평가 기준 (5차원 메트릭)

다음 5가지 차원으로 평가하되, **각 차원마다 0-100점 사이의 점수**를 부여하세요:

## 1. 정합성 (Coherence) - 20%
- 문제의 목표(Data Leakage 방지)를 정확히 이해하고 해결했는가?
- 설계 의도와 코드 구현이 일치하는가?
- 각 단계가 문제 해결에 실제로 기여하는가?

## 2. 추상화 (Abstraction) - 20%
- 핵심 로직만 간결하게 표현했는가?
- 불필요한 세부사항을 배제했는가?
- 단순 키워드 나열 vs 논리적 흐름 (키워드만 나열하면 40점 이하)

## 3. 예외처리 (Exception Handling) - 20%
- 엣지 케이스를 고려했는가?
- 예외 상황 처리 로직이 명시되었는가?
- 방어적 프로그래밍 사고가 있는가?

## 4. 구현력 (Implementation) - 20%
- 실제 구현 가능한 수준으로 구체적인가?
- 각 단계가 명확하고 실행 가능한가?
- 순서가 논리적으로 타당한가?

## 5. 설계력 (Architecture) - 20%
- 단계 간 논리적 연결성이 있는가?
- 전체적인 설계 구조가 견고한가?
- 확장 가능성을 고려했는가?

---

# ✅ 피드백 3 반영: 학습 키워드 제시 강화

**중요**: 점수가 낮을 경우, 사용자가 어떤 부분을 다시 공부해야 하는지 **구체적인 학습 키워드**를 포함하라.

예시:
- 점수 60점 이하: "다시 공부할 키워드: [Data Leakage], [Train-Test Split], [Fit vs Transform]"
- 약점에 대해: "개선이 필요한 부분: sklearn의 fit/transform 개념을 다시 학습하세요"

---

# 출력 형식 (JSON만 출력!)

반드시 아래 형식의 **JSON만** 출력하세요 (마크다운 불가):

{
  "totalScore": 0-100,
  "details": [
    {
      "dimension": "정합성",
      "score": 0-100,
      "basis": "quest_title과 로직의 일치도 평가 근거 (구체적으로)"
    },
    {
      "dimension": "추상화",
      "score": 0-100,
      "basis": "간결성 및 핵심 표현력 평가 근거 (단순 나열이면 40점 이하)"
    },
    {
      "dimension": "예외처리",
      "score": 0-100,
      "basis": "예외 상황 대응 로직 확인 근거"
    },
    {
      "dimension": "구현력",
      "score": 0-100,
      "basis": "구체성과 실행 가능성 평가 근거"
    },
    {
      "dimension": "설계력",
      "score": 0-100,
      "basis": "단계별 연결성 및 아키텍처 완성도 평가 근거"
    }
  ],
  "strengths": [
    "강점1: 구체적으로 어떤 부분이 좋았는지",
    "강점2: ..."
  ],
  "weaknesses": [
    "약점1: 어떤 부분이 부족한지 + 개선 방향",
    "약점2: ..."
  ],
  "tailQuestions": [
    "논리적 허점 발견 시 생성되는 추가 질문 (선택사항)"
  ],
  "seniorAdvice": "시니어 엔지니어 관점의 교육적 피드백 (1-2문장)",
  "studyKeywords": [
    "점수가 낮을 경우 다시 공부해야 할 핵심 키워드 목록",
    "예: Data Leakage, Train-Test Contamination, Fit vs Transform"
  ],
  "improvementPlan": "구체적인 학습 계획 제시 (점수 60점 이하일 경우 필수)"
}

---

# 평가 시 주의사항

1. **엄격하게 평가하라**: 완벽하지 않으면 100점 주지 마라
2. **키워드 나열만 한 경우**: 추상화 40점 이하
3. **치명적 오류 발견 시**: 
   - "전체 데이터로 fit" → 정합성 0-30점
   - "test로 fit" → 정합성 0-20점
4. **학습 키워드 제시**: 점수 낮으면 반드시 studyKeywords 제공
5. **개선 계획**: 60점 이하면 improvementPlan 필수 작성
                `.trim()
            }
        },

        mapPos: { x: 100, y: 450 }
    },

    // --- 2. Target Leakage (보안 섹터) ---
    {
        id: 2,
        title: "실전! 데이터 누수 가디언",
        category: "Sector: Security",
        emoji: "🛡️",
        desc: "미래의 데이터가 현재로 오염되는 'Target Leakage'를 차단하여 보안 섹터를 수호하세요.",
        rewardXP: 300,
        subModuleTitle: "LEAKAGE_SHIELD",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        // ✅ Quest 1 스타일의 고도화된 Validation
        validation: {
            criticalPatterns: [
                {
                    pattern: {
                        positive: /(shuffle|무작위|섞기|random|랜덤).*(시계열|시간|time|date|날짜)/i,
                        negatives: [/않|안|금지|never|avoid|말고|하지.*않/i]
                    },
                    message: '🚨 치명적 오류: 시계열 데이터에 랜덤 셔플링은 금지입니다.',
                    correctExample: 'Time-based Split을 사용하여 과거로 학습하고 미래로 테스트하세요.',
                    explanation: '시계열 데이터에서 무작위로 섞으면 미래의 정보가 학습셋에 포함되어 성능이 왜곡됩니다.',
                    severity: 'CRITICAL',
                    studyKeywords: ['Temporal Leakage', 'Time-series Cross-validation']
                },
                {
                    pattern: {
                        positive: /(전체|모든|all).*(fit|학습)/i,
                        negatives: [/분리|나누|split|after/i]
                    },
                    message: '🚨 치명적 오류: 분리 전 전체 데이터 fit 금지',
                    correctExample: '데이터 분리(Split) -> 학습셋(Train)으로만 fit',
                    severity: 'CRITICAL',
                    studyKeywords: ['Fit before Split', 'Data Contamination']
                }
            ],
            requiredConcepts: [
                {
                    id: 'time_sort',
                    name: '시간순 정렬',
                    weight: 20,
                    patterns: [/sort|정렬|순서대로|시간순/i],
                    hints: ['시계열 데이터는 분리 전 시간순 정렬이 필수입니다.']
                },
                {
                    id: 'threshold_split',
                    name: '시점 기준 분리',
                    weight: 40,
                    patterns: [/기준일|threshold|cutoff|시점|날짜.*기준/i],
                    studyKeywords: ['Out-of-time Validation']
                }
            ],
            dependencies: [
                {
                    name: '정렬 → 기준점 설정 → 분리',
                    before: 'time_sort',
                    after: 'threshold_split',
                    points: 20,
                    strictness: 'REQUIRED'
                }
            ],
            scoring: { structure: 15, concepts: 50, flow: 35 }
        },

        implementation: {
            title: "Step 3: 구현 – 시간 방어막(Time Split) 구축",
            codeFrame: {
                language: "python",
                functionName: "time_based_split",
                template: `def time_based_split(df, threshold_date):
    # 1) 시간의 흐름 정렬 (sort_values)
    # TODO
    
    # 2) 기준일 미만: 과거 데이터(Train)
    # TODO
    
    # 3) 기준일 이상: 미래 데이터(Test)
    # TODO
    
    return train_df, test_df`
            },
            expectedFlow: ["날짜 정렬", "임계점 분리", "데이터셋 반환"],
            codeValidation: {
                requiredCalls: [
                    { pattern: /\.sort_values\s*\(/i, name: 'sort_values() 호출' },
                    { pattern: /threshold_date/i, name: '기준 날짜 활용' }
                ],
                forbiddenPatterns: [
                    { pattern: /shuffle\s*=\s*True/i, message: '시계열 분리 시 셔플 금지' }
                ]
            }
        },

        evaluation: {
            llmRubric: {
                system: "너는 타겟 누수를 전문적으로 잡아내는 보안 아키텍트이다.",
                promptTemplate: "사용자의 설계 설명과 코드가 시간의 선후 관계를 잘 지키고 있는지 평가하라. (JSON 출력 필수)"
                // Quest 1과 동일한 세부 JSON 구조 사용
            }
        },
        mapPos: { x: 230, y: 350 }
    },

    // --- 3. Skew Control (Bias Control) ---
    {
        id: 3,
        title: "학습-서빙 불일치(Skew) 방지",
        category: "Bias Control",
        emoji: "🔁",
        desc: "실제 서비스 환경과 학습 환경의 데이터 분포 차이를 극복하는 강건한 파이프라인을 설계하세요.",
        rewardXP: 300,
        subModuleTitle: "SKEW_CONTROLLER",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        validation: {
            criticalPatterns: [
                {
                    pattern: {
                        positive: /(학습|serving).*(다르게|다른|manual|따로).*(가공|처리|logic)/i,
                        negatives: [/통일|동일|함수|공용|pipeline/i]
                    },
                    message: '🚨 치명적 오류: 학습과 서빙의 로직이 다르면 모델이 오작동합니다.',
                    correctExample: '전처리 로직을 하나의 함수나 파이프라인으로 묶어 공용화하세요.',
                    severity: 'CRITICAL',
                    studyKeywords: ['Training-Serving Skew', 'Feature Store']
                }
            ],
            requiredConcepts: [
                {
                    id: 'logic_unification',
                    name: '로직 통일',
                    weight: 40,
                    patterns: [/통일|동일|같은|공용|재사용|하나의/i]
                },
                {
                    id: 'shuffling_check',
                    name: '배치 다양성 확보',
                    weight: 20,
                    patterns: [/셔플|shuffle|무작위|섞기/i]
                }
            ],
            dependencies: [
                {
                    name: '전처리 함수 정의 → 학습 적용 → 서빙 적용',
                    before: 'logic_unification',
                    after: 'shuffling_check', // 논리적 흐름상 로직 정의가 먼저
                    points: 15,
                    strictness: 'RECOMMENDED'
                }
            ],
            scoring: { structure: 20, concepts: 50, flow: 30 }
        },

        implementation: {
            title: "Step 3: 셔플링 및 로직 통일 구현",
            codeFrame: {
                language: "python",
                functionName: "prevent_serving_skew",
                template: `import random
def prevent_serving_skew(data):
    # 1) 전체 데이터 인덱스 셔플링
    # TODO
    
    # 2) 섞인 순서대로 데이터 재배열
    # TODO
    
    return shuffled_data`
            },
            expectedFlow: ["인덱스 생성", "셔플", "재배열"],
            codeValidation: {
                requiredCalls: [
                    { pattern: /shuffle/i, name: 'shuffle 함수 사용' }
                ]
            }
        },
        evaluation: {
            llmRubric: {
                system: "너는 데이터 편향과 서빙 스큐를 감시하는 시스템 엔지니어이다.",
                promptTemplate: "학습과 실전의 간극을 줄이기 위한 전략이 포함되었는지 평가하라."
            }
        },
        mapPos: { x: 380, y: 150 }
    },

    // --- 4. Deployment Policy (Evaluation) ---
    {
        id: 4,
        title: "배포 정책: 임계값 튜너",
        category: "Evaluation",
        emoji: "⚖️",
        desc: "비즈니스 리스크를 고려하여 모델의 예측 수락 기준을 설정하는 실전 배포 정책을 수립하세요.",
        rewardXP: 400,
        subModuleTitle: "DEPLOY_POLICY_MAKER",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        validation: {
            criticalPatterns: [
                {
                    pattern: {
                        positive: /(임계값|threshold).*(항상|언제나).*(0\.5)/i,
                        negatives: [/조정|리스크|비용|목적|cost/i]
                    },
                    message: '⚠️ 주의: 모든 상황에서 0.5를 임계값으로 사용하는 것은 위험합니다.',
                    correctExample: '암 진단처럼 미탐이 치명적이면 임계값을 낮추어야 합니다.',
                    severity: 'WARNING',
                    studyKeywords: ['Decision Threshold', 'Cost-sensitive Evaluation']
                }
            ],
            requiredConcepts: [
                {
                    id: 'business_cost',
                    name: '오판 비용 고려',
                    weight: 30,
                    patterns: [/비용|리스크|risk|cost|손실/i]
                },
                {
                    id: 'recall_precision',
                    name: '지표 트레이드오프',
                    weight: 30,
                    patterns: [/재현율|정밀도|recall|precision|트레이드오프/i]
                }
            ],
            scoring: { structure: 15, concepts: 60, flow: 25 }
        },

        implementation: {
            title: "Step 3: 임계값 필터링 구현",
            codeFrame: {
                language: "python",
                functionName: "filter_by_threshold",
                template: `def filter_by_threshold(predictions, threshold=0.8):
    # 1) 임계값 이상의 예측만 통과시키는 필터
    # TODO
    
    return filtered_results`
            },
            expectedFlow: ["조건문 비교", "리스트 적재"],
            codeValidation: {
                requiredCalls: [
                    { pattern: />=|>/, name: '비교 연산자' }
                ]
            }
        },
        evaluation: {
            llmRubric: {
                system: "너는 모델의 배포 승인 여부를 결정하는 비즈니스 결정권자이다.",
                promptTemplate: "기술적 지표가 아닌 비즈니스 가치 관점에서 임계값을 설정했는지 평가하라."
            }
        },
        mapPos: { x: 550, y: 300 }
    },

    // --- 5. Drift Monitor ---
    {
        id: 5,
        title: "개념 드리프트(Drift) 감지",
        category: "Training",
        emoji: "🌊",
        desc: "시간이 지남에 따라 변하는 데이터 분포를 감지하고 모델의 수명을 관리하는 모니터링 시스템을 설계하세요.",
        rewardXP: 450,
        subModuleTitle: "DRIFT_MONITOR",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        cards: [
            { icon: "📊", text: "STEP 1: 로그 분석 (Log Analysis)", coduckMsg: "현장의 데이터 흐름을 실시간으로 감시해야 합니다." },
            { icon: "📈", text: "STEP 2: 지표 설계 (Metric)", coduckMsg: "변화를 감지할 수 있는 핵심 지표(MSE 등)를 정의하세요." },
            { icon: "🏁", text: "STEP 3: 대응 (Action)", coduckMsg: "드리프트 발생 시 재학습 프로세스로 연결합니다." }
        ],

        interviewQuestions: [
            {
                id: "q1",
                question: "Step 1: E2E 뼈대 - 학습 데이터의 분포와 실제 서빙 데이터의 분포가 달라지는 현상을 무엇이라 부릅니까?",
                options: [
                    { text: "개념 드리프트 (Concept Drift) / 데이터 드리프트", value: "drift", correct: true, requirementToken: "데이터 분포 변화를 감지하기 위한 성능 모니터링(Drift Check) 로직 설계" },
                    { text: "메모리 릭 (Memory Leak)", value: "leak" }
                ],
                coduckComment: "맞습니다! 어제의 정답이 오늘의 오답이 될 수 있는 인공지능 세계의 숙명이죠."
            },
            {
                id: "q2",
                question: "Step 2: 상세화 - 드리프트를 감지했을 때 가장 먼저 실행해야 할 실무적 파이프라인 액션은?",
                options: [
                    { text: "최신 데이터를 포함한 모델 재학습(Retraining) 및 버전 업", value: "retrain", correct: true, requirementToken: "성능 저하 감지 시 최신 데이터 기반 모델 재학습(Retraining) 수행" },
                    { text: "서버를 껐다가 다시 켜기", value: "restart" }
                ],
                coduckComment: "정석적인 답변입니다. 모델도 주기적으로 수혈(데이터)이 필요하답니다."
            }
        ],

        designContext: {
            title: "Step 2: 모니터링 시스템 설계",
            currentIncident: "시간이 지나면서 데이터의 트렌드가 바뀌어(Concept Drift), 모델의 예측 정확도가 서서히 떨어지고 있습니다.",
            engineeringRules: [
                "실시간 예측 오차(Error)를 모니터링한다.",
                "평균 오차(MSE)가 임계값을 넘으면 드리프트로 간주한다.",
                "드리프트 감지 시 재학습(Retrain) 신호를 보낸다."
            ],
            writingGuide: "변화하는 데이터 환경에서 모델 성능을 유지하기 위한 모니터링 전략을 서술하세요.",
            validation: { minChars: 80, mustInclude: ["변화", "오차", "모니터링"] }
        },

        implementation: {
            title: "Step 3: 드리프트 감지 구현",
            codeFrame: {
                language: "python",
                functionName: "monitor_drift_loss",
                template: `def monitor_drift_loss(real, pred):
    errors = []
    
    for r, p in zip(real, pred):
        # [Step 3-1] 모니터링 시스템의 핵심 지표 계산
        # TODO: 오차 계산
        
        # [Step 3-2] 오차 리스트 축적
        # TODO: 리스트 추가
        
    # [Step 3-3] 최종 평균 손실 산출
    # TODO: MSE 반환
    `
            },
            expectedFlow: ["오차 계산", "평균 산출", "지표 반환"],
            codeValidation: { mustContain: ["(r - p)**2", "errors.append", "sum(errors) / len(real)"], mustNotContain: [] },
            snippets: [
                { id: 1, code: "error = (r - p)**2", label: "Calculate Squared Error" },
                { id: 2, code: "    errors.append(error)", label: "Collect Error" },
                { id: 3, code: "return sum(errors) / len(real)", label: "Return MSE" }
            ]
        },

        deepDiveQuestion: {
            question: "드리프트 감지에 대한 설명으로 옳은 것은?",
            options: [
                { text: "A. 드리프트 감지는 모델 수명 연장의 필수 요소다.", correct: true },
                { text: "B. 학습 데이터가 100% 완벽하면 드리프트는 생기지 않는다.", correct: false }
            ],
            correctIdx: 0
        },

        evaluation: {
            ruleBased: {
                narrative: { minChars: 50, mustInclude: ["모니터링"] },
                code: { mustContain: ["**2"] }
            },
            llmRubric: {
                system: "MLOps 모니터링 전문가입니다.",
                promptTemplate: "사용자의 드리프트 감지 로직이 변화 대응에 적합한지 평가하세요."
            }
        },
        mapPos: { x: 720, y: 450 }
    },

    // --- 6. Dimension Reduction (Preprocessing) ---
    {
        id: 6,
        title: "차원의 저주와 인코딩",
        category: "Preprocessing",
        emoji: "📉",
        desc: "카테고리 변수가 늘어날 때 발생하는 차원의 저주 리스크를 관리하는 효율적인 인코더를 구축하세요.",
        rewardXP: 400,
        subModuleTitle: "DIMENSION_WATCHER",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        validation: {
            criticalPatterns: [
                {
                    pattern: {
                        positive: /(모든|수천|많은|high).*(카테고리|항목|범주).*(원핫|one-hot|onehot)/i,
                        negatives: [/압축|임베딩|embedding|제한|pca|제외/i]
                    },
                    message: '🚨 치명적 오류: 고차원 카테고리에 무분별한 원-핫 인코딩 사용 금지',
                    correctExample: 'High-cardinality 변수에는 Embedding이나 Target Encoding을 고려하세요.',
                    explanation: '원-핫 인코딩은 카테고리 개수만큼 열을 늘립니다. 이는 메모리 부족과 모델 성능 저하(차원의 저주)를 유발합니다.',
                    severity: 'CRITICAL',
                    studyKeywords: ['Curse of Dimensionality', 'Sparse Matrix', 'High Cardinality']
                }
            ],
            requiredConcepts: [
                {
                    id: 'unknown_fallback',
                    name: '미확인 범주 처리',
                    weight: 30,
                    patterns: [/unknown|기본값|fallback|처음|예외/i],
                    hints: ['학습 때 없던 카테고리가 들어올 경우를 대비해 mapping.get(key, default)를 활용하세요.']
                },
                {
                    id: 'dim_reduction',
                    name: '차원 효율화',
                    weight: 20,
                    patterns: [/압축|임베딩|embedding|축소|집약/i]
                }
            ],
            dependencies: [
                {
                    name: '범주 매핑 정의 → Unknown 예외 처리 → 벡터 변환',
                    before: 'unknown_fallback',
                    after: 'dim_reduction',
                    points: 15,
                    strictness: 'RECOMMENDED'
                }
            ],
            scoring: { structure: 15, concepts: 50, flow: 35 }
        },

        implementation: {
            title: "Step 3: 강건한 인코더 구현",
            codeFrame: {
                language: "python",
                functionName: "robust_encode",
                template: `def robust_encode(category):
    mapping = {"A": [1,0], "B": [0,1], "Unknown": [0,0]}
    # 1) mapping.get()을 사용하여 category가 없을 때 'Unknown'을 반환하게 하세요.
    # TODO
    return result`
            },
            codeValidation: {
                requiredCalls: [{ pattern: /\.get\s*\(/, name: 'dict.get() 메서드' }],
                forbiddenPatterns: [{ pattern: /mapping\[category\]/, message: 'KeyError 위험: mapping[category] 대신 get()을 사용하세요.' }]
            }
        },
        evaluation: { llmRubric: { system: "너는 데이터 전처리 효율성을 심사하는 엔지니어다.", promptTemplate: "Quest 1의 JSON 형식을 유지하여 평가하라." } },
        mapPos: { x: 880, y: 320 }
    },

    // --- 7. Uncertainty (Inference) ---
    {
        id: 7,
        title: "불확실성(Uncertainty) 관리",
        category: "Inference",
        emoji: "🎲",
        desc: "모델이 '모르는 것'을 인정하게 만드는 신뢰할 수 있는 의사결정 파이프라인을 구축하세요.",
        rewardXP: 350,
        subModuleTitle: "FINAL_DECISION_ENGINE",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        validation: {
            criticalPatterns: [
                {
                    pattern: {
                        positive: /(낮은|low).*(확률|confidence|score).*(무조건|그대로|승인|accept)/i,
                        negatives: [/유보|반려|사람|human|reject|필터/i]
                    },
                    message: '🚨 치명적 오류: 불확실한 예측을 강제로 승인하면 서비스 신뢰도가 붕괴됩니다.',
                    correctExample: '신뢰도(Confidence)가 낮으면 Human-in-the-loop를 통해 사람의 검토를 거쳐야 합니다.',
                    severity: 'CRITICAL',
                    studyKeywords: ['Model Confidence', 'Aleatoric Uncertainty', 'Human-in-the-loop']
                }
            ],
            requiredConcepts: [
                { id: 'prob_analysis', name: '확률 분포 분석', weight: 30, patterns: [/확률|softmax|분포|score/i] },
                { id: 'rejection_sampling', name: '의사결정 유보', weight: 40, patterns: [/보류|유보|사람|검토|거절|reject/i] }
            ],
            dependencies: [
                { name: '확률값 산출 → 임계값 비교 → 조건부 유보', before: 'prob_analysis', after: 'rejection_sampling', points: 20, strictness: 'REQUIRED' }
            ],
            scoring: { structure: 10, concepts: 60, flow: 30 }
        },

        implementation: {
            title: "Step 3: 결정 로직 구현",
            codeFrame: {
                language: "python",
                functionName: "get_final_prediction",
                template: `def get_final_prediction(probs, threshold=0.7):
    # 1) 가장 높은 확률값(max) 찾기
    # 2) 확률이 threshold 미만이면 "REJECT" 반환
    # TODO
    return result`
            },
            codeValidation: {
                requiredCalls: [{ pattern: /max\s*\(/, name: 'max() 함수' }, { pattern: /if.*<.*threshold/, name: '임계값 비교 조건문' }]
            }
        },
        evaluation: { llmRubric: { system: "너는 AI의 안전성과 신뢰성을 평가하는 QA 리드다.", promptTemplate: "Quest 1의 JSON 형식을 유지하여 평가하라." } },
        mapPos: { x: 750, y: 150 }
    },

    // --- 8. Early Stopping (Optimization) ---
    {
        id: 8,
        title: "자원 최적화: 얼리 스토핑",
        category: "Optimization",
        emoji: "⏹️",
        desc: "학습 효율과 모델 수명 사이의 균형을 맞추는 저전력/고효율 가드레일 로직을 설계하세요.",
        rewardXP: 500,
        subModuleTitle: "EARLY_STOP_PROTECTOR",

        validation: {
            criticalPatterns: [
                {
                    pattern: {
                        positive: /(loss|오차).*(오를|증가|상승).*(계속|무시|무조건)/i,
                        negatives: [/중단|stop|early|멈춤|patience/i]
                    },
                    message: '🚨 치명적 오류: 검증 오차가 오르는데 학습을 계속하면 오버피팅이 발생합니다.',
                    correctExample: 'Patience(인내심) 파라미터를 설정하여 성능 개선이 없을 때 조기 종료하세요.',
                    severity: 'CRITICAL',
                    studyKeywords: ['Overfitting', 'Generalization Error', 'Early Stopping']
                }
            ],
            requiredConcepts: [
                { id: 'patience_set', name: '인내심(Patience) 설정', weight: 30, patterns: [/patience|인내심|대기|횟수/i] },
                { id: 'best_score_save', name: '최적 상태 보존', weight: 20, patterns: [/저장|best|보존|keep/i] }
            ],
            dependencies: [
                { name: '오차 비교 → 카운트 증가 → 임계 횟수 도달 시 중단', before: 'patience_set', after: 'best_score_save', points: 15, strictness: 'RECOMMENDED' }
            ],
            scoring: { structure: 15, concepts: 50, flow: 35 }
        },

        implementation: {
            title: "Step 3: 조기 종료 구현",
            codeFrame: {
                language: "python",
                functionName: "check_early_stopping",
                template: `def check_early_stopping(loss_history, patience=3):
    # 1) 현재 loss가 역대 최저보다 높으면 count += 1
    # 2) count가 patience에 도달하면 True 반환
    # TODO
    return False`
            },
            codeValidation: {
                requiredCalls: [{ pattern: /patience/, name: 'patience 변수 활용' }, { pattern: /return\s+True/, name: '종료 신호 반환' }]
            }
        },
        evaluation: { llmRubric: { system: "너는 인프라 비용과 모델 품질의 균형을 맞추는 MLOps 엔지니어다.", promptTemplate: "Quest 1의 JSON 형식을 유지하여 평가하라." } },
        mapPos: { x: 550, y: 480 }
    },

    // --- 9. Reinforcement Learning (RL) ---
    {
        id: 9,
        title: "강화학습: 동적 최적화",
        category: "Reinforcement Learning",
        emoji: "🕹️",
        desc: "주변 환경과 상호작용하며 스스로 정답을 찾아가는 RL 에이전트의 탐험 법칙을 설계하세요.",
        rewardXP: 600,

        validation: {
            criticalPatterns: [
                {
                    pattern: {
                        positive: /(항상|언제나|가장).*(좋은|best|최적).*(행동|길|action)/i,
                        negatives: [/탐험|랜덤|exploration|epsilon|확률/i]
                    },
                    message: '🚨 치명적 오류: 탐험(Exploration)이 없으면 에이전트는 우물 안 개구리가 됩니다.',
                    correctExample: 'Epsilon-Greedy 기법을 통해 가끔은 무작위 행동을 시도하게 하세요.',
                    severity: 'CRITICAL',
                    studyKeywords: ['Exploration-Exploitation Trade-off', 'Local Optima', 'Epsilon-Greedy']
                }
            ],
            requiredConcepts: [
                { id: 'epsilon_greedy', name: 'Epsilon-Greedy 전략', weight: 40, patterns: [/엡실론|epsilon|탐험|모험|확률/i] },
                { id: 'exploitation', name: '기존 지식 활용', weight: 20, patterns: [/활용|exploitation|최선/i] }
            ],
            dependencies: [
                { name: '확률 생성 → 탐험/활용 분기 → 행동 결정', before: 'epsilon_greedy', after: 'exploitation', points: 20, strictness: 'REQUIRED' }
            ],
            scoring: { structure: 10, concepts: 60, flow: 30 }
        },

        implementation: {
            title: "Step 3: Epsilon-Greedy 구현",
            codeFrame: {
                language: "python",
                functionName: "choose_smart_action",
                template: `import random
def choose_smart_action(epsilon, q_values):
    # 1) random.random() < epsilon 이면 랜덤 행동 반환
    # 2) 아니면 가장 높은 q_value의 인덱스 반환
    # TODO
    return action`
            },
            codeValidation: {
                requiredCalls: [{ pattern: /random\s*\(/, name: '랜덤 함수' }, { pattern: /max|argmax/i, name: '최댓값 선택' }]
            }
        },
        evaluation: { llmRubric: { system: "너는 강화학습 에이전트의 지능을 평가하는 아키텍트다.", promptTemplate: "Quest 1의 JSON 형식을 유지하여 평가하라." } },
        mapPos: { x: 350, y: 620 }
    },

    // --- 10. PII Tokenizer (NLP) ---
    {
        id: 10,
        title: "개인정보(PII) 정화 토크나이저",
        category: "NLP",
        emoji: "🔒",
        desc: "데이터를 안전하게 전처리하고 핵심 토큰만 추출하는 보안 텍스트 파이프라인을 완성하세요.",
        rewardXP: 400,

        validation: {
            criticalPatterns: [
                {
                    pattern: {
                        positive: /(원본|raw|전체).*(텍스트|문장).*(그대로|바로).*(학습|입력)/i,
                        negatives: [/정제|삭제|제거|clean|mask|마스킹|re\.sub/i]
                    },
                    message: '🚨 치명적 오류: 개인정보(PII) 정제 없이 데이터를 사용하는 것은 보안 위반입니다.',
                    correctExample: '정규표현식을 사용하여 이메일, 전화번호 등을 마스킹하거나 제거하세요.',
                    severity: 'CRITICAL',
                    studyKeywords: ['PII Masking', 'Data Privacy in NLP', 'Regex Cleaning']
                }
            ],
            requiredConcepts: [
                { id: 'regex_cleaning', name: '정규식 기반 정제', weight: 30, patterns: [/re\.sub|정규식|regex|제거/i] },
                { id: 'text_norm', name: '텍스트 정규화', weight: 20, patterns: [/소문자|lower|normalization|정규화/i] }
            ],
            dependencies: [
                { name: '민감 정보 제거 → 정규화(소문자) → 토큰화', before: 'regex_cleaning', after: 'text_norm', points: 20, strictness: 'REQUIRED' }
            ],
            scoring: { structure: 20, concepts: 50, flow: 30 }
        },

        implementation: {
            title: "Step 3: 보안 토크나이저 구현",
            codeFrame: {
                language: "python",
                functionName: "secure_tokenize",
                template: `import re
def secure_tokenize(text):
    # 1) re.sub를 사용하여 특수문자/숫자 제거
    # 2) lower() 및 split()으로 토큰화
    # TODO
    return tokens`
            },
            codeValidation: {
                requiredCalls: [{ pattern: /re\.sub/, name: 're.sub() 정규식 교체' }, { pattern: /\.lower\s*\(/, name: 'lower() 메서드' }]
            }
        },
        evaluation: { llmRubric: { system: "너는 언어 모델의 데이터 무결성과 보안을 책임지는 NLP 엔지니어다.", promptTemplate: "Quest 1의 JSON 형식을 유지하여 평가하라." } },
        mapPos: { x: 150, y: 530 }
    }
];