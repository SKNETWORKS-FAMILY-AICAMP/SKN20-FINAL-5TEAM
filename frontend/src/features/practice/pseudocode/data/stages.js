export const aiQuests = [
    {
        id: 1,
        title: "[튜토리얼] 사고 회로 복구: Data Leakage",
        category: "System Reboot",
        emoji: "💡",
        desc: "AI 문제를 만났을 때, 코드를 치기 전 무엇을 먼저 생각해야 하는지 훈련합니다.",
        rewardXP: 500,
        subModuleTitle: "BOOT_PROTOCOL",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        cards: [
            { icon: "🚨", text: "STEP 1: 위험 감지 (Diagnosis)", coduckMsg: "데이터 파이프라인에서 비정상 신호가 감지되었습니다. 현재 상황을 정확히 진단하는 것이 급선무입니다." },
            { icon: "📝", text: "STEP 2: 설계 (Architecture)", coduckMsg: "문제를 해결하기 위한 논리적 설계를 수립하세요. 코드를 짜기 전에 글로 먼저 정리해야 합니다." },
            { icon: "💻", text: "STEP 3: 구현 (Implementation)", coduckMsg: "설계한 논리를 바탕으로 실제 복구 코드를 작성하세요. 빈 칸을 채워 시스템을 정상화하십시오." },
            { icon: "⚖️", text: "STEP 4: 검증 (Validation)", coduckMsg: "수정된 시스템이 올바르게 작동하는지 테스트 케이스를 통해 검증합니다." }
        ],

        interviewQuestions: [
            {
                id: "q1",
                question: "Step 1-1: 사고 회로 복구를 위한 첫 번째 행동은?",
                options: [
                    { text: "전체 데이터 흐름(E2E Pipeline)을 먼저 파악한다", value: "flow", correct: true },
                    { text: "바로 모델과 코드를 수정한다", value: "code" }
                ],
                coduckComment: "좋아요. 문제를 고치기 전에, 먼저 전체 흐름을 봐야 해요."
            },
            {
                id: "q2",
                question: "Step 1-2: AI가 환각(Hallucination)에 빠지는 가장 흔한 원인은?",
                options: [
                    { text: "잘못된 학습 기준으로 데이터를 처리했기 때문", value: "leakage", correct: true },
                    { text: "모델이 충분히 똑똑하지 않아서", value: "model" }
                ],
                coduckComment: "정확해요. 기준이 무너지면 모델도 흔들려요."
            }
        ],

        designContext: {
            title: "Step 2: 아키텍처 설계 (자연어 서술)",
            currentIncident: `
    모델 학습 과정에서 테스트 데이터의 통계 정보가
    학습 기준 생성에 사용되는 데이터 누수(Data Leakage)가 발생했습니다.

    검증 성능은 높게 나왔지만,
    실제 서비스 환경에서는 성능이 재현되지 않는 문제가 확인되었습니다.
        `.trim(),
            engineeringRules: [
                "Train 데이터로만 fit 한다.",
                "Test 데이터는 transform만 수행한다.",
                "미래 데이터의 정보는 사용하지 않는다.",
                "학습과 서빙은 동일한 전처리 흐름을 사용한다."
            ],
            writingGuide: `
    다음 내용을 포함해 사고 과정을 서술하세요.

    - 데이터 누수가 무엇이며 왜 발생했는가
    - 이 문제가 실전 환경에서 왜 위험한가
    - 전처리 파이프라인을 어떤 순서로 설계해야 하는가

    ※ 코드는 작성하지 말고, 사고 흐름만 서술하세요.
        `.trim(),
            validation: {
                minChars: 120,
                mustInclude: ["train", "test", "fit", "transform"],
            }
        },

        implementation: {
            title: "Step 3: 구현 – 사고 흐름을 코드로 증명하세요",
            codeFrame: {
                language: "python",
                functionName: "leakage_free_scaling",
                template: `def leakage_free_scaling(train_df, test_df):
        from sklearn.preprocessing import StandardScaler
        # 1) 스케일러 초기화
        # TODO

        # 2) Train 데이터로 기준 생성 (fit)
        # TODO

        # 3) Train 데이터 변환 (transform)
        # TODO

        # 4) Test 데이터 변환 (transform)
        # TODO

        return train_scaled, test_scaled`
            },
            expectedFlow: [
                "Train 데이터로만 fit 수행",
                "Train 데이터 transform",
                "Test 데이터 transform"
            ],
            codeValidation: {
                mustContain: [
                    "scaler.fit(train_df)",
                    "scaler.transform(train_df)",
                    "scaler.transform(test_df)"
                ],
                mustNotContain: [
                    "scaler.fit(test_df)"
                ]
            },
            snippets: [
                { id: 1, code: "scaler = StandardScaler()", label: "Initialize Scaler" },
                { id: 2, code: "scaler.fit(train_df)", label: "Fit Model (Train Data)" },
                { id: 3, code: "train_scaled = scaler.transform(train_df)", label: "Transform Train Data" },
                { id: 4, code: "test_scaled = scaler.transform(test_df)", label: "Transform Test Data" }
            ]
        },

        deepDiveQuestion: {
            question: "다음 중 데이터 누수가 특히 위험한 이유는 무엇입니까?",
            options: [
                { text: "모델이 미래 정보를 미리 학습해 실전 성능이 붕괴된다", correct: true },
                { text: "학습 속도가 느려진다", correct: false },
                { text: "GPU 메모리를 더 많이 사용한다", correct: false },
                { text: "코드가 복잡해진다", correct: false }
            ],
            correctIdx: 0
        },

        evaluation: {
            ruleBased: {
                narrative: {
                    minChars: 120,
                    mustInclude: ["train", "test", "fit", "transform"],
                    mustNotInclude: ["test로 fit", "fit(test)"]
                },
                code: {
                    mustContain: [
                        "scaler.fit(train_df)",
                        "scaler.transform(train_df)",
                        "scaler.transform(test_df)"
                    ],
                    mustNotContain: ["scaler.fit(test_df)"]
                }
            },
            llmRubric: {
                system: "너는 AI 아키텍처 관점에서 사고 흐름을 평가하는 면접관이다.",
                promptTemplate: `
    사용자 설계 설명:
    {{narrative}}

    사용자 코드:
    {{code}}

    다음 기준으로 평가하라:
    - 데이터 누수의 원인을 정확히 이해했는가
    - 왜 실전에서 위험한지 설명했는가
    - 설계와 코드가 일관되는가

    JSON 형식으로 출력:
    { "score": number, "feedback": string }
        `.trim()
            }
        },
        mapPos: { x: 100, y: 450 }
    },

    // --- 2. Target Leakage ---
    {
        id: 2,
        title: "실전! 데이터 누수 가디언",
        category: "Sector: Security",
        emoji: "🛡️",
        desc: "미래의 데이터가 현재로 오염되는 'Target Leakage'를 차단하여 보안 섹터를 수호하세요.",
        rewardXP: 300,
        subModuleTitle: "LEAKAGE_SHIELD",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        cards: [
            { icon: "⏳", text: "STEP 1: 위험 감지 (Diagnosis)", coduckMsg: "시간선이 꼬였습니다. 미래의 정보가 과거로 흘러들어오고 있습니다." },
            { icon: "🔧", text: "STEP 2: 설계 (Architecture)", coduckMsg: "시간의 흐름을 지키는 방어막을 설계하세요. 미래를 보지 않고 과거만으로 학습해야 합니다." },
            { icon: "✨", text: "STEP 3: 구현 (Implementation)", coduckMsg: "설계된 시간 방어막(Time Split)을 코드로 구현하여 누수를 막으십시오." },
            { icon: "🏁", text: "STEP 4: 검증 (Validation)", coduckMsg: "보안이 강화된 파이프라인이 정상 작동하는지 확인합니다." }
        ],

        interviewQuestions: [
            {
                id: "q1",
                question: "Step 1: 뼈대 설계 - 미래의 정보가 현재의 학습에 스며들어 시간선이 꼬이는 'Data Leakage'를 막기 위한 분리 방식은?",
                options: [
                    { text: "시간의 흐름대로 데이터를 분리 (Time-based Split)", value: "time", correct: true, requirementToken: "데이터를 무작위로 섞지 않고 '시간 흐름(Time-series)'에 따라 순차적으로 분리" },
                    { text: "과거와 미래를 무작위로 섞어서 분리 (Random Split)", value: "random" }
                ],
                coduckComment: "옳은 선택입니다, {username}님! 시간선이 뒤섞이면 마더 서버는 환각을 보게 됩니다."
            },
            {
                id: "q2",
                question: "Step 2: 상세화 - 마더 서버가 검증 데이터의 통계량을 미리 훔쳐보는 것을 막기 위한 핵심 조치는?",
                options: [
                    { text: "오직 학습용 데이터셋으로만 전처리 기준(fit)을 수립하기", value: "leak", correct: true, requirementToken: "전처리 기준(fit)은 반드시 '학습용 데이터(train_df)'로만 수립하여 미래 정보 유출 차단" },
                    { text: "모든 데이터를 한 번에 정규화하기", value: "lack" }
                ],
                coduckComment: "정확한 방어 전략입니다. 'Fit before Split'은 Architect가 절대 범해서는 안 되는 실수죠."
            }
        ],

        designContext: {
            title: "Step 2: 아키텍처 설계 (자연어 서술)",
            currentIncident: "미래 시점의 데이터가 과거 학습 데이터에 섞여 들어가는 타겟 누수(Target Leakage)가 발생했습니다. 이로 인해 모델이 실제보다 과도하게 낙관적인 성능을 보이고 있습니다.",
            engineeringRules: [
                "데이터는 시간 순서대로 분리한다 (Time Series Split).",
                "검증 데이터(Test)는 학습 과정에 절대 개입하지 않는다.",
                "전처리 기준(Scaler fit)은 오직 과거 데이터(Train)로만 수립한다."
            ],
            writingGuide: "타겟 누수가 왜 위험한지, 그리고 이를 방지하기 위해 어떤 순서로 데이터를 분리하고 전처리해야 하는지 서술하세요.",
            validation: {
                minChars: 100,
                mustInclude: ["시간", "분리", "fit", "train"],
            }
        },

        implementation: {
            title: "Step 3: 구현 – 시간 방어막(Time Split) 구축",
            codeFrame: {
                language: "python",
                functionName: "time_based_split",
                template: `def time_based_split(df, threshold_date):
    # [Step 3-1] 시간의 흐름 파악
    # TODO
    
    # [Step 3-2] 과거 데이터(Train) 격리
    # TODO
    
    # [Step 3-3] 미래 데이터(Test) 보호
    # TODO
    
    return train_df, test_df`
            },
            expectedFlow: ["날짜 정렬", "임계점 분리", "데이터셋 반환"],
            codeValidation: {
                mustContain: ["sort_values", "df['date'] < threshold_date", "df['date'] >= threshold_date"],
                mustNotContain: ["shuffle=True", "random_state"]
            },
            snippets: [
                { id: 1, code: "df = df.sort_values('date')", label: "Sort by Time" },
                { id: 2, code: "train_df = df[df['date'] < threshold_date]", label: "Extract Train (Past)" },
                { id: 3, code: "test_df = df[df['date'] >= threshold_date]", label: "Extract Test (Future)" }
            ]
        },

        deepDiveQuestion: {
            question: "학습 시 테스트 데이터의 정보를 사용하면 검증 성능은 높지만 실전 성능은 낮은 현상이 발생합니다. 이러한 문제가 위험한 핵심 이유는?",
            options: [
                { text: "A. 모델이 실제로 접하지 못한 미래 정보를 미리 학습하여 과적합된다.", correct: true },
                { text: "B. 검증 데이터와 학습 데이터는 섞일수록 좋다.", correct: false }
            ],
            correctIdx: 0
        },

        evaluation: {
            ruleBased: {
                narrative: { minChars: 50, mustInclude: ["시간", "분리"] },
                code: { mustContain: ["fit(train_df)"], mustNotContain: ["fit(test_df)"] }
            },
            llmRubric: {
                system: "타겟 누수 방지 전략을 평가하는 보안관입니다.",
                promptTemplate: "사용자의 시간 분리 전략과 코드 구현의 일치성을 평가하세요. JSON 포맷 필수."
            }
        },
        mapPos: { x: 230, y: 350 }
    },

    // --- 3. Skew Control ---
    {
        id: 3,
        title: "학습-서빙 불일치(Skew) 방지",
        category: "Bias Control",
        emoji: "🔁",
        desc: "실제 서비스 환경과 학습 환경의 데이터 분포 차이를 극복하는 강건한 파이프라인을 설계하세요.",
        rewardXP: 300,
        subModuleTitle: "SKEW_CONTROLLER",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        cards: [
            { icon: "📏", text: "STEP 1: 규격 확인 (Diagnosis)", coduckMsg: "학습 환경과 실전 환경이 다릅니다. 이대로면 모델이 현장에서 고장납니다." },
            { icon: "🎲", text: "STEP 2: 설계 (Architecture)", coduckMsg: "편향을 막기 위해 데이터를 어떻게 섞어야 할지 설계하세요." },
            { icon: "📝", text: "STEP 3: 구현 (Implementation)", coduckMsg: "일관된 전처리 파이프라인을 구축하여 불일치를 해소하십시오." },
            { icon: "🏁", text: "STEP 4: 검증 (Validation)", coduckMsg: "환경 동기화가 성공했는지 검증합니다." }
        ],

        interviewQuestions: [
            {
                id: "q1",
                question: "Step 1: E2E 뼈대 - 학습된 모델이 현장에 배포되었을 때 성능이 급락하는 'Train/Serving Skew'의 주요 원인은?",
                options: [
                    { text: "학습 시 사용한 피처 가공 로직과 실시간 환경의 로직이 다르기 때문", value: "skew", correct: true, requirementToken: "학습(Train)과 운영(Serving) 환경 간의 전처리 파이프라인 로직 통일" },
                    { text: "서버 사양이 부족해서", value: "server" }
                ],
                coduckComment: "날카롭군요! '전처리 코드 형상 관리'가 안 되면 발생하는 비극이죠."
            },
            {
                id: "q2",
                question: "Step 2: 상세화 - 데이터 편향을 막기 위한 셔플링(Shuffling)이 역효과를 내는 경우는?",
                options: [
                    { text: "시계열적 특성이 중요한 금융/로그 데이터일 때", value: "time", correct: true, requirementToken: "시계열적 특성 보존을 위해 문맥에 맞지 않는 불필요한 셔플링 지양" },
                    { text: "데이터가 너무 많을 때", value: "volume" }
                ],
                coduckComment: "정확합니다. 도메인의 특성에 맞춰 셔플링 여부를 결정하는 것이 의사결정의 핵심입니다."
            }
        ],

        designContext: {
            title: "Step 2: 편향 방지 설계",
            currentIncident: "특정 클래스의 데이터가 뭉쳐서 입력되어, 모델이 편향된 학습을 하고 있습니다. 배치(Batch) 단위의 다양성이 부족합니다.",
            engineeringRules: [
                "학습 전 데이터를 무작위로 섞는다 (Shuffle).",
                "단, 시계열 데이터인 경우 셔플링을 주의한다.",
                "학습과 서빙의 전처리 로직을 동일하게 유지한다."
            ],
            writingGuide: "데이터 편향(Bias)이 학습에 미치는 악영향과, 셔플링이 필요한 이유를 서술하세요.",
            validation: { minChars: 80, mustInclude: ["셔플", "순서", "편향"] }
        },

        implementation: {
            title: "Step 3: 셔플링 구현",
            codeFrame: {
                language: "python",
                functionName: "prevent_serving_skew",
                template: `import random
def prevent_serving_skew(data):
    # 1) 전체 데이터의 인덱스 생성
    # TODO
    
    # 2) [Step 3-1] 무작위 셔플링으로 배치 편향 제거
    # TODO
    
    # 3) 섞인 인덱스 순서대로 데이터 재배열
    # TODO
    
    return shuffled_data`
            },
            expectedFlow: ["인덱스 생성", "인덱스 셔플", "데이터 재배열"],
            codeValidation: { mustContain: ["random.shuffle(indices)", "list(range(len(data)))"], mustNotContain: [] },
            snippets: [
                { id: 1, code: "indices = list(range(len(data)))", label: "Create Index List" },
                { id: 2, code: "random.shuffle(indices)", label: "Shuffle Indices" },
                { id: 3, code: "shuffled_data = [data[i] for i in indices]", label: "Reorder Data" }
            ]
        },

        deepDiveQuestion: {
            question: "스큐 방지에 대한 설명으로 옳은 것은?",
            options: [
                { text: "A. 스큐를 막으려면 전처리 코드의 공용화가 필요하다.", correct: true },
                { text: "B. 서빙용 데이터는 학습용보다 더 복잡해야 한다.", correct: false }
            ],
            correctIdx: 0
        },

        evaluation: {
            ruleBased: {
                narrative: { minChars: 50, mustInclude: ["셔플"] },
                code: { mustContain: ["shuffle"] }
            },
            llmRubric: {
                system: "데이터 편향 제어 전문가입니다.",
                promptTemplate: "사용자의 셔플링 전략이 편향 해소에 적합한지 평가하세요."
            }
        },
        mapPos: { x: 380, y: 150 }
    },

    // --- 4. Deployment Policy ---
    {
        id: 4,
        title: "배포 정책: 임계값 튜너",
        category: "Evaluation",
        emoji: "⚖️",
        desc: "비즈니스 리스크를 고려하여 모델의 예측 수락 기준을 설정하는 실전 배포 정책을 수립하세요.",
        rewardXP: 400,
        subModuleTitle: "DEPLOY_POLICY_MAKER",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        cards: [
            { icon: "💰", text: "STEP 1: 비용 산정 (Cost Analysis)", coduckMsg: "틀렸을 때의 비용을 계산하세요. 모든 에러가 똑같이 나쁜 건 아닙니다." },
            { icon: "🔢", text: "STEP 2: 임계값 설계 (Threshold)", coduckMsg: "비즈니스 목표에 맞는 최적의 합격 기준점(Threshold)을 정해야 합니다." },
            { icon: "⚖️", text: "STEP 3: 정책 구현 (Implementation)", coduckMsg: "기준 미달인 예측을 과감히 걸러내는 필터를 만드세요." },
            { icon: "🏁", text: "STEP 4: 배포 승인 (Approval)", coduckMsg: "안전하게 정제된 예측 결과만 배포합니다." }
        ],

        interviewQuestions: [
            {
                id: "q1",
                question: "Step 1: E2E 뼈대 - 긴급 재난 알림 시스템처럼 '놓치면 치명적인' 문제에서 가장 중요한 메트릭은?",
                options: [
                    { text: "재현율 (Recall: 실제 양성을 얼마나 잘 찾아내는가)", value: "recall", correct: true, requirementToken: "미탐(False Negative) 리스크가 큰 경우 재현율(Recall) 최적화 전략 수립" },
                    { text: "정밀도 (Precision: 모델이 맞다고 한 것 중 실제는 얼마인가)", value: "precision" }
                ],
                coduckComment: "훌륭한 비즈니스 감각입니다! 하나라도 놓치는 것이 더 위험한 상황이니까요."
            },
            {
                id: "q2",
                question: "Step 2: 상세화 - 암 진단 모델에서 임계값을 0.9로 높게 잡는 '보수적 전략'의 리스크는?",
                options: [
                    { text: "실제 환자를 정상으로 오판(False Negative)하여 골든타임을 놓칠 수 있음", value: "fn", correct: true, requirementToken: "임계값(Threshold) 설정 시 비즈니스 오판 비용(Cost of Error)을 고려" },
                    { text: "학습 시간이 길어짐", value: "slow" }
                ],
                coduckComment: "정답입니다. 기술적 지표 뒤에 숨겨진 '사람의 생명'이나 '비용'을 보는 것이 시니어의 눈이죠."
            }
        ],

        designContext: {
            title: "Step 2: 배포 정책 수립",
            currentIncident: "예측 점수가 낮은 불안정한 결과까지 사용자에게 노출되고 있어 클레임이 발생하고 있습니다.",
            engineeringRules: [
                "비즈니스 리스크(Cost)에 따라 임계값(Threshold)을 조정한다.",
                "신뢰도가 낮은 예측은 필터링(Reject)한다."
            ],
            writingGuide: "임계값 설정이 비즈니스에 미치는 영향과, 낮은 점수의 예측을 걸러내야 하는 이유를 서술하세요.",
            validation: { minChars: 80, mustInclude: ["임계값", "필터", "신뢰도"] }
        },

        implementation: {
            title: "Step 3: 임계값 필터링 구현",
            codeFrame: {
                language: "python",
                functionName: "filter_by_threshold",
                template: `def filter_by_threshold(predictions, threshold=0.8):
    filtered_results = []
    
    for p in predictions:
        # [Step 3-1] 실무 대응: 비즈니스 하한선 필터링
        # TODO: 조건 확인
        # TODO: 결과 추가
        
    return filtered_results`
            },
            expectedFlow: ["점수 확인", "임계값 비교", "필터링"],
            codeValidation: { mustContain: ["if p['score'] >= threshold:", "filtered_results.append(p)"], mustNotContain: [] },
            snippets: [
                { id: 1, code: "if p['score'] >= threshold:", label: "Filter Condition" },
                { id: 2, code: "    filtered_results.append(p)", label: "Add to Results" }
            ]
        },

        deepDiveQuestion: {
            question: "임계값(Threshold) 결정에 대한 설명으로 옳은 것은?",
            options: [
                { text: "A. 임계값 결정은 모델링만큼 중요한 의사결정이다.", correct: true },
                { text: "B. 모든 서비스에는 임계값 0.9가 가장 안전하다.", correct: false }
            ],
            correctIdx: 0
        },

        evaluation: {
            ruleBased: {
                narrative: { minChars: 50, mustInclude: ["임계값"] },
                code: { mustContain: [">="] }
            },
            llmRubric: {
                system: "비즈니스 배포 정책 담당자입니다.",
                promptTemplate: "사용자의 임계값 필터링 전략이 비즈니스 리스크 관리에 적합한지 평가하세요."
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
            { icon: "⚖️", text: "STEP 3: 구현 (Monitor)", coduckMsg: "오차가 기준치를 넘으면 경보를 울리는 로직을 작성합니다." },
            { icon: "🏁", text: "STEP 4: 대응 (Action)", coduckMsg: "드리프트 발생 시 재학습 프로세스로 연결합니다." }
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

    // --- 6. Dimension Reduction ---
    {
        id: 6,
        title: "차원의 저주와 인코딩",
        category: "Preprocessing",
        emoji: "📉",
        desc: "카테고리 변수가 늘어날 때 발생하는 차원의 저주 리스크를 관리하는 효율적인 인코더를 구축하세요.",
        rewardXP: 400,
        subModuleTitle: "DIMENSION_WATCHER",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        cards: [
            { icon: "📑", text: "STEP 1: 현황 파악 (Analysis)", coduckMsg: "카테고리가 너무 많아 모델이 혼란스러워합니다. 차원의 저주를 막아야 합니다." },
            { icon: "⚠️", text: "STEP 2: 설계 (Architecture)", coduckMsg: "정보를 잃지 않으면서도 효율적으로 압축할 인코딩 전략을 세우세요." },
            { icon: "🎯", text: "STEP 3: 구현 (Encoding)", coduckMsg: "예외 상황(처음 보는 값)까지 처리할 수 있는 강건한 인코더를 만드세요." },
            { icon: "🏁", text: "STEP 4: 검증 (Validation)", coduckMsg: "인코딩 결과가 안전한지 확인합니다." }
        ],

        interviewQuestions: [
            {
                id: "q1",
                question: "Step 1: E2E 뼈대 - 카테고리 종류가 수백 개일 때 원-핫 인코딩(One-hot)을 남발하면 파이프라인에 생기는 비극은?",
                options: [
                    { text: "메모리 부족 및 연산 속도 급락 (차원의 저주)", value: "curse", correct: true, requirementToken: "고차원 카테고리 데이터 처리 시 Sparse Matrix 및 메모리 부족 리스크 관리" },
                    { text: "모델 가중치가 모두 0이 됨", value: "zero" }
                ],
                coduckComment: "정확합니다. 불필요하게 늘어난 0(Sparse)이 모델을 멍청하게 만들 수 있죠."
            },
            {
                id: "q2",
                question: "Step 2: 상세화 - 수백 개의 카테고리를 숫자로 안전하게 바꾸기 위해 실무에서 고려하는 대안은?",
                options: [
                    { text: "차원을 축소하여 정보를 집약하는 임베딩(Embedding) 기법", value: "embed", correct: true, requirementToken: "정보 손실을 줄이면서 차원을 효율적으로 축약하는 인코딩/임베딩 전략 수립" },
                    { text: "모두 무시하고 삭제하기", value: "delete" }
                ],
                coduckComment: "훌륭해요. 복잡도를 제어하면서도 정보를 유지하는 것이 실력입니다."
            }
        ],

        designContext: {
            title: "Step 2: 인코딩 전략 수립",
            currentIncident: "카테고리 수가 폭발적으로 증가하여 메모리가 부족해지고 학습 속도가 느려지고 있습니다. 게다가 학습 때 못 본 새로운 카테고리가 등장하면 에러가 납니다.",
            engineeringRules: [
                "고차원 데이터는 효율적인 인코딩 방식을 선택한다.",
                "미확인 카테고리(Unknown)에 대한 예외 처리(Fallback)를 반드시 구현한다."
            ],
            writingGuide: "차원의 저주를 피하기 위한 인코딩 전략과, 새로운 데이터에 대응하는 방어 코드를 어떻게 짤지 서술하세요.",
            validation: { minChars: 80, mustInclude: ["차원", "예외", "인코딩"] }
        },

        implementation: {
            title: "Step 3: 강건한 인코더 구현",
            codeFrame: {
                language: "python",
                functionName: "robust_encode",
                template: `def robust_encode(category):
    # [Step 3-1] 전략적 매핑 정의 (Unknown 대응 포함)
    mapping = {
        "NLP": [1, 0, 0],
        "Vision": [0, 1, 0],
        "Unknown": [0, 0, 1]
    }
    
    # [Step 3-2] 실무 리스크 대응: 처음 보는 값은 예외 처리
    # TODO: mapping.get을 사용하여 category에 대한 벡터를 반환하세요. 없을 경우 mapping['Unknown'] 반환
    return result`
            },
            expectedFlow: ["매핑 정의", "안전한 조회(get)", "기본값 반환"],
            codeValidation: { mustContain: ["mapping.get", "mapping['Unknown']"], mustNotContain: [] },
            snippets: [
                { id: 1, code: "result = mapping.get(category, mapping['Unknown'])", label: "Safe Mapping Lookup" }
            ]
        },

        deepDiveQuestion: {
            question: "인코딩 전략에 대한 설명으로 옳은 것은?",
            options: [
                { text: "A. 원-핫 인코딩은 범주 간의 서열을 만들지 않는다.", correct: true },
                { text: "B. 카테고리가 많을수록 0이 많아지는 희소 행렬이 생긴다.", correct: true }
            ],
            correctIdx: 0
        },

        evaluation: {
            ruleBased: {
                narrative: { minChars: 50, mustInclude: ["예외"] },
                code: { mustContain: ["get"] }
            },
            llmRubric: {
                system: "데이터 전처리 전문가입니다.",
                promptTemplate: "사용자의 인코딩 전략이 차원의 저주와 예외 처리를 잘 다루고 있는지 평가하세요."
            }
        },
        mapPos: { x: 880, y: 320 }
    },

    // --- 7. Uncertainty ---
    {
        id: 7,
        title: "불확실성(Uncertainty) 관리",
        category: "Inference",
        emoji: "🎲",
        desc: "모델이 '모르는 것'을 인정하게 만드는 신뢰할 수 있는 의사결정 파이프라인을 구축하세요.",
        rewardXP: 350,
        subModuleTitle: "FINAL_DECISION_ENGINE",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        cards: [
            { icon: "📊", text: "STEP 1: 확률 분석 (Probability)", coduckMsg: "모델이 내놓은 확률값들을 분석하세요. 확신이 있는지 없는지 봐야 합니다." },
            { icon: "🔍", text: "STEP 2: 설계 (Design)", coduckMsg: "확률이 애매할 때는 결정을 유보하거나 사람에게 넘기는 로직이 필요합니다." },
            { icon: "🧑‍💻", text: "STEP 3: 구현 (Implementation)", coduckMsg: "가장 높은 확률을 선택하되, 신뢰도를 검증하는 코드를 작성하세요." },
            { icon: "🏁", text: "STEP 4: 검증 (Verification)", coduckMsg: "결정 엔진이 합리적인 선택을 하는지 확인합니다." }
        ],

        interviewQuestions: [
            {
                id: "q1",
                question: "Step 1: E2E 뼈대 - 확률 [0.35, 0.3, 0.35]처럼 모델이 갈팡질팡할 때 '자동 배포'를 강행하면 생기는 실무 리스크는?",
                options: [
                    { text: "오판 확률이 매우 높아져 서비스 신뢰도 붕괴", value: "fail", correct: true, requirementToken: "모델 예측의 불확실성이 높을 경우 자동 승인을 반려하는 안전 장치 설계" },
                    { text: "모델 용량이 커짐", value: "size" }
                ],
                coduckComment: "빙고! 이때는 '모름'이라고 인정하고 사람에게 검토를 맡기는 것이 진짜 실력이죠."
            },
            {
                id: "q2",
                question: "Step 2: 상세화 - 1등 확률만 뽑는 것보다, 2등과의 차이(Margin)를 계산해야 하는 이유는?",
                options: [
                    { text: "모델이 얼마나 압도적으로 확신하는지 측정하기 위해", value: "margin", correct: true, requirementToken: "신뢰도 임계값(Margin/Confidence) 미달 시 수동 검토 프로세스 유도" },
                    { text: "수학을 좋아하는 면접관에게 잘 보이려고", value: "show" }
                ],
                coduckComment: "정확합니다. 압도적인 1위가 아니면 의사결정을 유보하는 전략이 필요하죠."
            }
        ],

        designContext: {
            title: "Step 2: 의사결정 엔진 설계",
            currentIncident: "모델이 확신하지 못하는 상황에서도 무조건 답변을 내놓아, 엉뚱한 결과를 초래하고 있습니다.",
            engineeringRules: [
                "모델의 예측 확률(Softmax output)을 분석한다.",
                "가장 높은 확률(Confidence)을 가진 클래스를 선택한다.",
                "단, 신뢰도가 너무 낮으면 결정을 보류한다 (Human-in-the-loop)."
            ],
            writingGuide: "AI의 불확실성을 관리하기 위한 의사결정 로직과 안전장치에 대해 서술하세요.",
            validation: { minChars: 80, mustInclude: ["확률", "비교", "신뢰"] }
        },

        implementation: {
            title: "Step 3: 결정 로직 구현",
            codeFrame: {
                language: "python",
                functionName: "get_final_prediction",
                template: `def get_final_prediction(probs):
    # [Step 3-1] 실무 대응: 확률적 최대값 산출
    # TODO: 최댓값 찾기
    
    # [Step 3-2] 최종 라벨 인덱스 반환
    # TODO: 인덱스 추출
    `
            },
            expectedFlow: ["최댓값 찾기", "인덱스 반환"],
            codeValidation: { mustContain: ["max(probs)", "probs.index"], mustNotContain: [] },
            snippets: [
                { id: 1, code: "max_val = max(probs)", label: "Find Max Probability" },
                { id: 2, code: "return probs.index(max_val)", label: "Return Label Index" }
            ]
        },

        deepDiveQuestion: {
            question: "다중 클래스 분류에서 Argmax의 의미는?",
            options: [
                { text: "A. Argmax는 가장 높은 확률을 가진 클래스의 위치를 찾는다.", correct: true },
                { text: "B. 모든 확률의 합이 1보다 크면 오버피팅된 것이다.", correct: false }
            ],
            correctIdx: 0
        },

        evaluation: {
            ruleBased: {
                narrative: { minChars: 50, mustInclude: ["신뢰"] },
                code: { mustContain: ["max"] }
            },
            llmRubric: {
                system: "인공지능 의사결정 전문가입니다.",
                promptTemplate: "사용자의 불확실성 처리 방식이 합리적인지 평가하세요."
            }
        },
        mapPos: { x: 750, y: 150 }
    },

    // --- 8. Early Stopping ---
    {
        id: 8,
        title: "자원 최적화: 얼리 스토핑",
        category: "Optimization",
        emoji: "⏹️",
        desc: "학습 효율과 모델 수명 사이의 균형을 맞추는 저전력/고효율 가드레일 로직을 설계하세요.",
        rewardXP: 500,
        subModuleTitle: "EARLY_STOP_PROTECTOR",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        cards: [
            { icon: "📝", text: "STEP 1: 손실 기록 (History)", coduckMsg: "학습 과정을 지켜보세요. 성적이 오르고 있나요, 제자리걸음인가요?" },
            { icon: "⚖️", text: "STEP 2: 기준 설정 (Patience)", coduckMsg: "언제까지 기다려줄지 인내심(Patience)의 한계를 정하세요." },
            { icon: "⏳", text: "STEP 3: 구현 (Logic)", coduckMsg: "개선이 없으면 과감하게 학습을 중단시키는 코드를 짭니다." },
            { icon: "🏁", text: "STEP 4: 검증 (Test)", coduckMsg: "자원 낭비 없이 적절한 시점에 멈추는지 확인합니다." }
        ],

        interviewQuestions: [
            {
                id: "q1",
                question: "Step 1: E2E 뼈대 - 학습 세션이 너무 길어져 그래픽 카드(GPU) 자원이 낭비되고 비용이 폭증할 때 필요한 시스템은?",
                options: [
                    { text: "개선 없을 시 자동 종료하는 얼리 스토핑 (Early Stopping)", value: "stop", correct: true, requirementToken: "자원 낭비 및 오버피팅 전조 현상 발생 시 조기 종료(Early Stopping) 기법 적용" },
                    { text: "컴퓨터 전원 강제로 끄기", value: "power" }
                ],
                coduckComment: "합리적이네요. 에너지와 비용을 아끼는 것도 훌륭한 엔지니어링의 일환입니다."
            },
            {
                id: "q2",
                question: "Step 2: 상세화 - 얼리 스토핑 기준 손실값이 0.1, 0.11, 0.12처럼 조금씩 '오를 때' 바로 멈추지 않고 좀 더 기다려야 하는 이유는?",
                options: [
                    { text: "모델이 로컬 미니마(Local Minima)를 벗어날 기회를 주기 위해 (인내심)", value: "local", correct: true, requirementToken: "일시적 정체 구간(Patience)을 감안한 유연한 종료 기준 수립" },
                    { text: "내가 코딩을 덜 하고 싶어서", value: "lazy" }
                ],
                coduckComment: "맞습니다. 일시적인 정체를 넘어 진정한 '수렴'인지 판단할 시간을 줘야 하죠."
            }
        ],

        designContext: {
            title: "Step 2: 자원 최적화 설계",
            currentIncident: "이미 다 배운 모델을 계속 학습시키느라 GPU 비용이 낭비되고, 오히려 성능이 떨어지는 오버피팅이 발생하고 있습니다.",
            engineeringRules: [
                "검증 손실(Val Loss)이 개선되지 않으면 카운트를 센다.",
                "지정된 횟수(Patience)만큼 참아도 개선이 없으면 중단한다.",
                "최적의 모델 상태를 저장한다."
            ],
            writingGuide: "효율적인 학습 종료 시점을 결정하는 알고리즘과 인내심(Patience)의 필요성을 서술하세요.",
            validation: { minChars: 80, mustInclude: ["중단", "개선", "비용"] }
        },

        implementation: {
            title: "Step 3: 조기 종료 구현",
            codeFrame: {
                language: "python",
                functionName: "check_early_stopping",
                template: `def check_early_stopping(loss_history, patience=3):
    best_loss = float('inf')
    no_improve_count = 0
    
    for loss in loss_history:
        if loss < best_loss:
            best_loss = loss
            no_improve_count = 0
        else:
            # [Step 3-1] 실무 대응: 정체 구간 카운트 개시
            # TODO
            
        # [Step 3-2] 파이프라인 중단 신호 조건
        # TODO
            
    return False`
            },
            expectedFlow: ["손실 비교", "카운트 증가", "중단 조건 확인"],
            codeValidation: { mustContain: ["no_improve_count += 1", "if no_improve_count >= patience:", "return True"], mustNotContain: [] },
            snippets: [
                { id: 1, code: "no_improve_count += 1", label: "Increment Counter" },
                { id: 2, code: "if no_improve_count >= patience:\n    return True", label: "Early Stop Trigger" }
            ]
        },

        deepDiveQuestion: {
            question: "얼리 스토핑에 대한 설명으로 옳은 것은?",
            options: [
                { text: "A. 얼리 스토핑은 규제화(Regularization) 기법 중 하나다.", correct: true },
                { text: "B. 손실 함수가 0이 될 때까지 돌리는 게 기본이다.", correct: false }
            ],
            correctIdx: 0
        },

        evaluation: {
            ruleBased: {
                narrative: { minChars: 50, mustInclude: ["중단"] },
                code: { mustContain: ["patience"] }
            },
            llmRubric: {
                system: "모델 최적화 전문가입니다.",
                promptTemplate: "사용자의 조기 종료 전략이 자원 낭비를 막을 수 있는지 평가하세요."
            }
        },
        mapPos: { x: 550, y: 480 }
    },

    // --- 9. Reinforcement Learning ---
    {
        id: 9,
        title: "강화학습: 동적 최적화",
        category: "Reinforcement Learning",
        emoji: "🕹️",
        desc: "주변 환경과 상호작용하며 스스로 정답을 찾아가는 RL 에이전트의 모험과 활용의 법칙을 설계하세요.",
        rewardXP: 600,
        subModuleTitle: "RL_EXPLORATION_UNIT",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        cards: [
            { icon: "👀", text: "STEP 1: 관찰 (Observation)", coduckMsg: "환경을 탐색하세요. 가보지 않은 길에 보물이 있을지도 모릅니다." },
            { icon: "🗺️", text: "STEP 2: 설계 (Strategy)", coduckMsg: "언제 모험을 하고 언제 안전한 길을 갈지 전략을 세우세요 (Epsilon-Greedy)." },
            { icon: "🌀", text: "STEP 3: 구현 (Action)", coduckMsg: "확률에 따라 모험과 활용을 결정하는 에이전트의 뇌를 만드세요." },
            { icon: "🏁", text: "STEP 4: 검증 (Review)", coduckMsg: "에이전트가 균형 잡힌 성장을 하는지 확인합니다." }
        ],

        interviewQuestions: [
            {
                id: "q1",
                question: "Step 1: E2E 뼈대 - 정해진 라벨 없이 로봇이 행동하고 '보상(Reward)'을 받는 파이프라인을 무엇이라 합니까?",
                options: [
                    { text: "강화 학습 (Reinforcement Learning)", value: "rl", correct: true, requirementToken: "환경과의 상호작용 및 보상(Reward) 시스템 기반의 최적 정책 학습 엔진 설계" },
                    { text: "지도 학습 (Supervised Learning)", value: "supervised" }
                ],
                coduckComment: "훌륭한 정의입니다. 스스로 시행착오를 겪으며 성장하는 엔진이죠."
            },
            {
                id: "q2",
                question: "Step 2: 상세화 - 에이전트가 항상 '최선'이라고 판단한 길로만 가지 않고 가끔 랜덤한 길을 가야 하는 이유는?",
                options: [
                    { text: "현재 모르는 더 큰 보석(Global Optimum)이 숨어있을 수 있기 때문에", value: "explore", correct: true, requirementToken: "탐색(Exploration)과 활용(Exploitation)의 균형을 맞추는 메커니즘 구축" },
                    { text: "인공지능도 가끔은 쉬고 싶기 때문", value: "rest" }
                ],
                coduckComment: "멋집니다! 이 '탐험' 없이는 영원히 지역적인 최선(Local Optima)에 갇히게 됩니다."
            }
        ],

        designContext: {
            title: "Step 2: 강화학습 전략 설계",
            currentIncident: "에이전트가 아는 길로만 다니느라 새로운 최적 경로를 찾지 못하고 정체되어 있습니다 (`Local Optima`).",
            engineeringRules: [
                "일정 확률(Epsilon)로 무작위 탐험(Exploration)을 시도한다.",
                "나머지 확률로 현재까지의 최선(Exploitation)을 선택한다.",
                "시행착오를 통해 학습한다."
            ],
            writingGuide: "탐험(Exploration)과 활용(Exploitation)의 균형이 왜 중요한지, 그리고 이를 어떻게 구현할지 서술하세요.",
            validation: { minChars: 80, mustInclude: ["탐험", "활용", "균형"] }
        },

        implementation: {
            title: "Step 3: Epsilon-Greedy 구현",
            codeFrame: {
                language: "python",
                functionName: "choose_smart_action",
                template: `import random
def choose_smart_action(epsilon, q_values):
    # [Step 3-1] 실무 대응: 확률적 모험(Exploration) 가동
    # TODO: 조건 확인
    # TODO: 랜덤 행동
    
    # [Step 3-2] 축적된 지식 기반 활용(Exploitation)
    # TODO: 최선 행동
    `
            },
            expectedFlow: ["확률 난수 생성", "랜덤 인덱스 반환", "최댓값 인덱스 반환"],
            codeValidation: { mustContain: ["if random.random() < epsilon:", "random.randint", "max(q_values)"], mustNotContain: [] },
            snippets: [
                { id: 1, code: "if random.random() < epsilon:", label: "Check Exploration Prob" },
                { id: 2, code: "    return random.randint(0, len(q_values)-1)", label: "Explore (Random)" },
                { id: 3, code: "return q_values.index(max(q_values))", label: "Exploit (Best Knowledge)" }
            ]
        },

        deepDiveQuestion: {
            question: "강화학습에 대한 설명으로 옳은 것은?",
            options: [
                { text: "A. RL은 경험을 통해 직접 정책을 학습한다.", correct: true },
                { text: "B. 강화학습은 항상 정답 데이터셋이 필요하다.", correct: false }
            ],
            correctIdx: 0
        },

        evaluation: {
            ruleBased: {
                narrative: { minChars: 50, mustInclude: ["탐험", "활용"] },
                code: { mustContain: ["epsilon"] }
            },
            llmRubric: {
                system: "강화학습 아키텍트입니다.",
                promptTemplate: "사용자의 탐험 전략이 최적해를 찾는데 기여하는지 평가하세요."
            }
        },
        mapPos: { x: 350, y: 620 }
    },

    // --- 10. PII Tokenizer ---
    {
        id: 10,
        title: "개인정보(PII) 정화 토크나이저",
        category: "NLP",
        emoji: "🔒",
        desc: "실습 데이터를 안전하게 전처리하고 핵심 토큰만 추출하는 고성능 텍스트 파이프라인을 완성하세요.",
        rewardXP: 400,
        subModuleTitle: "SECURE_TEXT_PURIFIER",
        character: { name: "Coduck", image: "/assets/characters/coduck.png" },

        cards: [
            { icon: "📝", text: "STEP 1: 식별 (Identify)", coduckMsg: "문장 속에 숨어있는 개인정보나 노이즈를 찾아내야 합니다." },
            { icon: "🧹", text: "STEP 2: 정화 (Cleanse)", coduckMsg: "특수문자나 기밀 정보를 제거하여 안전한 텍스트로 만드세요." },
            { icon: "✂️", text: "STEP 3: 토큰화 (Tokenize)", coduckMsg: "정제된 텍스트를 AI가 이해할 수 있는 단위(토큰)로 쪼갭니다." },
            { icon: "🏁", text: "STEP 4: 배포 (Deploy)", coduckMsg: "보안이 확보된 깨끗한 데이터셋을 파이프라인에 공급합니다." }
        ],

        interviewQuestions: [
            {
                id: "q1",
                question: "Step 1: E2E 뼈대 - 언어 모델 학습 전, 이메일이나 전화번호 같은 기밀 정보를 처리하는 필수 전처리 단계는?",
                options: [
                    { text: "개인정보 식별 및 마스킹 (De-identification)", value: "masking", correct: true, requirementToken: "민감 정보(PII) 유출 방지를 위한 강력한 데이터 마스킹 전략 수립" },
                    { text: "크게 읽고 암기하기", value: "read" }
                ],
                coduckComment: "훌륭한 보안 의식입니다! 신뢰할 수 있는 데이터 수집이 모델의 토대니까요."
            },
            {
                id: "q2",
                question: "Step 2: 상세화 - 정규표현식으로 기호를 지울 때 '공백'만 남기고 소문자로 통일하는 이유는?",
                options: [
                    { text: "Apple, apple, APPLE!? 을 하나의 동일한 의미 단위로 묶기 위해", value: "normalize", correct: true, requirementToken: "의미적 일관성 확보를 위한 텍스트 정규화(Normalization) 전처리 수행" },
                    { text: "소문자가 더 귀여워서", value: "cute" }
                ],
                coduckComment: "정확합니다. 의미적 정규화를 통해 모델의 어휘집(Vocabulary) 효율을 극대화하는 것이죠."
            }
        ],

        designContext: {
            title: "Step 2: 텍스트 정화 설계",
            currentIncident: "수집된 텍스트 데이터에 특수문자와 노이즈가 너무 많아 모델이 학습을 못하고 있고, 개인정보 유출 위험도 있습니다.",
            engineeringRules: [
                "정규표현식(Regex)을 사용하여 불필요한 기호를 제거한다.",
                "모든 텍스트는 소문자로 정규화(Normalization)한다.",
                "빈 토큰(Empty token)은 필터링한다."
            ],
            writingGuide: "NLP 파이프라인의 보안성과 효율성을 높이기 위한 전처리 전략을 서술하세요.",
            validation: { minChars: 80, mustInclude: ["정규화", "제거", "토큰"] }
        },

        implementation: {
            title: "Step 3: 보안 토크나이저 구현",
            codeFrame: {
                language: "python",
                functionName: "secure_tokenize",
                template: `import re
def secure_tokenize(text):
    # [Step 3-1] 서비스 노이즈 및 특수기호 일괄 소거
    # TODO: 정규표현식 정화
    
    # [Step 3-2] 언어적 정규화(소문자화)
    # TODO: 토큰화 및 정규화
    
    # [Step 3-3] 최종 무결성 토큰 리스트 반환
    # TODO: 필터링 및 반환
    `
            },
            expectedFlow: ["특수문자 제거", "소문자 변환", "토큰 리스트 반환"],
            codeValidation: { mustContain: ["re.sub", "lower()", "split()", "t.strip()"], mustNotContain: [] },
            snippets: [
                { id: 1, code: "clean_text = re.sub(r'[^\\w\\s]', '', text)", label: "Cleanse Text (Regex)" },
                { id: 2, code: "tokens = clean_text.lower().split()", label: "Tokenize & Lowercase" },
                { id: 3, code: "return [t for t in tokens if t.strip()]", label: "Filter & Return Tokens" }
            ]
        },

        deepDiveQuestion: {
            question: "NLP 전처리에 대한 설명으로 옳은 것은?",
            options: [
                { text: "A. NLP 전처리는 모델의 언어 이해력을 결정한다.", correct: true },
                { text: "B. 특수문자가 많을수록 감성 분석이 무조건 쉬워진다.", correct: false }
            ],
            correctIdx: 0
        },

        evaluation: {
            ruleBased: {
                narrative: { minChars: 50, mustInclude: ["정규화"] },
                code: { mustContain: ["re.sub"] }
            },
            llmRubric: {
                system: "NLP 보안 엔지니어입니다.",
                promptTemplate: "사용자의 텍스트 정화 전략이 데이터 품질과 보안을 보장하는지 평가하세요."
            }
        },
        mapPos: { x: 150, y: 530 }
    }
];
