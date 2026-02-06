import { ref, computed, reactive, onMounted } from 'vue';
import axios from 'axios';
import { aiQuests } from '../data/stages.js'; // [수정일: 2026-02-06] 폴더 계층화(data) 반영

export function useCoduckWars() {
    const DEBUG_MODE = true;

    // --- Game State ---
    const gameState = reactive({
        currentStageId: 1,
        // New Phases: DIAGNOSTIC_1 -> DIAGNOSTIC_2 -> PSEUDO_WRITE -> PYTHON_FILL -> DEEP_QUIZ -> EVALUATION
        phase: 'DIAGNOSTIC_1',
        playerHP: 100,
        score: 0,
        combo: 0,

        // State for Decisions
        selectedStrategyLabel: "", // Set in Phase 2

        // Phase 3 State
        phase3Reasoning: "", // User Typed Logic
        showHint: false, // Hint visibility
        missionContext: "표준 정규화 과정에서 테스트 데이터의 정보가 학습 과정에 유입되어 모델의 신뢰성이 붕괴된 사건(Data Leakage)이 감지되었습니다. 원인 파악 및 해결 설계가 시급합니다.",
        constraints: [
            "원칙 1: 스케일러(fit)는 반드시 학습 데이터(Train)만을 기준으로 생성되어야 함 (테스트 데이터 오염 방지)",
            "원칙 2: 테스트 데이터(Test)는 기생성된 스케일러로 변환(transform)만 수행하며 절대 fit에 관여해선 안 됨",
            "원칙 3: 위 두 원칙을 포함하여, 데이터의 정합성을 유지하기 위한 본인만의 해결 로직을 상세히 서술할 것"
        ],

        // Phase 4 State
        // implementing "Monaco Editor" style content replaced by Slots
        userCode: "", // The content of the code editor
        codeSlots: null, // Holds slot1, slot2, etc. after initPhase4Scaffolding

        // Interactive Messages
        coduckMessage: "경고! 접근하는 모든 데이터는 적입니다!",
        feedbackMessage: null, // "Correct!" or "Error!"

        // System Logs (Dynamic)
        systemLogs: [
            { time: "10:42:01", type: "WARN", message: "7번 구역에서 인지 부조화 감지됨." },
            { time: "10:42:05", type: "INFO", message: "아키텍트의 개입을 대기 중..." },
            { time: "10:42:09", type: "READY", message: "의사결정 입력 대기 중_" }
        ]
    });

    const getTimestamp = () => {
        const now = new Date();
        return now.toTimeString().split(' ')[0]; // HH:MM:SS
    };

    const addSystemLog = (message, type = "INFO") => {
        // Keep only last 5 logs to prevent clutter
        if (gameState.systemLogs.length > 5) {
            gameState.systemLogs.shift();
        }
        gameState.systemLogs.push({
            time: getTimestamp(),
            type,
            message
        });
    };

    // --- Hint Timer Logic ---
    let hintTimer = null;

    const startHintTimer = () => {
        if (hintTimer) clearTimeout(hintTimer);
        gameState.showHint = false;
        hintTimer = setTimeout(() => {
            gameState.showHint = true;
            addSystemLog("힌트 프로토콜 자동 활성화", "INFO");
        }, 30000); // 30 seconds
    };

    const resetHintTimer = () => {
        if (hintTimer) clearTimeout(hintTimer);
        // Only hide hint if it was shown? Or keep it? Usually typing hides it or resets it.
        // Let's hide it when typing starts to clean up interface
        gameState.showHint = false;
        hintTimer = setTimeout(() => {
            gameState.showHint = true;
            addSystemLog("힌트 프로토콜 자동 활성화", "INFO");
        }, 30000);
    };

    const handlePseudoInput = (e) => {
        gameState.phase3Reasoning = e.target.value;
        resetHintTimer();
    };

    // --- Current Mission Data ---
    const currentMission = computed(() => {
        if (!aiQuests || aiQuests.length === 0) return {};
        // Fallback to first quest if id not found
        return aiQuests.find(q => q.id === gameState.currentStageId) || aiQuests[0];
    });

    // Threat Logic
    const enemyThreat = computed(() => {
        const mission = currentMission.value;
        return {
            name: mission.category || "Unknown Anomaly",
            description: mission.missionObjective || "No Objective",
            hp: 100
        };
    });

    // --- Phase Management ---

    const setPhase = (newPhase) => {
        console.log(`[CoduckWars] Transitioning to phase: ${newPhase}`);
        gameState.phase = newPhase;
        gameState.feedbackMessage = null;

        // Clear existing timer on phase change
        if (hintTimer) {
            clearTimeout(hintTimer);
            hintTimer = null;
        }

        try {
            switch (newPhase) {
                case 'DIAGNOSTIC_1':
                    gameState.coduckMessage = "이 선택은 이후 모든 판단에 영향을 줍니다.";
                    addSystemLog("진단 프로토콜 1단계 개시", "INFO");
                    break;
                case 'DIAGNOSTIC_2':
                    gameState.coduckMessage = "무엇을 신뢰할지 결정해야 합니다.";
                    addSystemLog("진단 프로토콜 2단계 진입", "INFO");
                    break;
                case 'PSEUDO_WRITE':
                    gameState.coduckMessage = "어떤 순서로 생각하는지 보여주세요.";
                    gameState.phase3Reasoning = ""; // Reset for new entry
                    addSystemLog("자연어 처리 에디터 로드됨", "SUCCESS");
                    startHintTimer(); // Start 30s timer
                    break;
                case 'PYTHON_FILL':
                    gameState.coduckMessage = "사고와 코드가 일치하는지 확인하십시오.";
                    addSystemLog("구현 환경 동기화 완료", "SUCCESS");
                    // Initialize Scaffolding for Phase 4
                    if (typeof initPhase4Scaffolding === 'function') {
                        initPhase4Scaffolding();
                    }
                    break;
                case 'DEEP_QUIZ':
                    gameState.coduckMessage = "설명할 수 있다면, 이해한 것입니다.";
                    addSystemLog("최종 검증 프로세스 시작", "WARN");
                    break;
                case 'EVALUATION':
                    gameState.coduckMessage = "평가가 완료되었습니다.";
                    addSystemLog("미션 리포트 생성 중...", "INFO");
                    break;
            }
        } catch (e) {
            console.error("[CoduckWars] Error in setPhase:", e);
            addSystemLog("단계 전환 중 오류 발생", "ERROR");
        }
    };

    const startGame = () => {
        console.log("[CoduckWars] Game Starting...");
        gameState.currentStageId = 1;
        gameState.score = 0;
        gameState.playerHP = 100;
        gameState.feedbackMessage = null;
        gameState.systemLogs = []; // Reset logs
        addSystemLog("시스템 부팅... 초기화 완료.", "READY");
        setPhase('DIAGNOSTIC_1');
    };

    // --- 1. Diagnostic Phase 1 (Q1) ---
    const diagnosticQuestion1 = computed(() => ({
        question: "이 문제는 어디에서 시작되었습니까?",
        options: [
            {
                text: "단계적 사고 프로토콜을 재가동한다",
                bullets: ["판단 기준을 다시 정의한다", "처리 속도가 느려질 수 있다"],
                correct: true
            },
            {
                text: "외부 입력을 전면 차단한다",
                bullets: ["즉각적인 혼란을 차단한다", "중요한 정보도 함께 사라질 수 있다"],
                correct: false
            }
        ]
    }));

    const submitDiagnostic1 = (optionIndex) => {
        console.log(`[CoduckWars] submitDiagnostic1 clicked: ${optionIndex}`);
        const q = diagnosticQuestion1.value;

        if (!q || !q.options || !q.options[optionIndex]) {
            console.error("[CoduckWars] Invalid option index or question data");
            return;
        }

        if (q.options[optionIndex].correct) {
            gameState.score += 100;
            gameState.feedbackMessage = "프로토콜 확인.";
            addSystemLog("선택 승인: 프로토콜 재가동", "SUCCESS");
            setTimeout(() => setPhase('DIAGNOSTIC_2'), 800);
        } else {
            handleDamage();
            gameState.feedbackMessage = "판단 오류.";
            addSystemLog("오류: 잘못된 판단입니다", "ERROR");
        }
    };

    // --- 2. Diagnostic Phase 2 (Q2) ---
    const diagnosticQuestion2 = computed(() => ({
        question: "정상 데이터를 남기기 위한 첫 기준은 무엇입니까?",
        options: [
            {
                text: "정밀 데이터 필터링 설계",
                bullets: ["노이즈 제거", "일부 유효 신호 손실 가능"],
                correct: true
            },
            {
                text: "무작위 데이터 주입",
                bullets: ["분포 안정화 시도", "판단 기준 불명확 위험"],
                correct: false
            }
        ]
    }));

    const submitDiagnostic2 = (optionIndex) => {
        console.log(`[CoduckWars] submitDiagnostic2 clicked: ${optionIndex}`);
        const q = diagnosticQuestion2.value;
        const selected = q.options[optionIndex];

        // Save the selection for Phase 3
        gameState.selectedStrategyLabel = selected.text;

        if (selected.correct) {
            gameState.score += 100;
            gameState.feedbackMessage = "전략 수립.";
            addSystemLog(`전략 채택: ${selected.text}`, "SUCCESS");
            setTimeout(() => setPhase('PSEUDO_WRITE'), 800);
        } else {
            handleDamage();
            gameState.feedbackMessage = "전략 오류.";
            addSystemLog("경고: 유효하지 않은 전략", "WARN");
        }
    };

    // --- 3. Pseudo Write Phase ---
    const submitPseudo = () => {
        if (gameState.phase3Reasoning.length < 10) {
            gameState.feedbackMessage = "논리가 부족합니다.";
            addSystemLog("제출 거부: 논리 내용 부족", "WARN");
            return;
        }
        if (hintTimer) clearTimeout(hintTimer); // Stop timer on submit
        gameState.score += 100;
        gameState.feedbackMessage = "설계 접수.";
        addSystemLog("논리 설계 데이터 업로드 완료", "SUCCESS");
        setTimeout(() => setPhase('PYTHON_FILL'), 800);
    };

    // --- 4. Implementation Phase ---
    const initPhase4Scaffolding = () => {
        // Init slots for drag-drop interaction (Generic placeholders to not give away answers)
        gameState.codeSlots = {
            slot1: { placeholder: "::: [SYSTEM SLOT 01: READY] :::", content: null },
            slot2: { placeholder: "::: [SYSTEM SLOT 02: READY] :::", content: null },
            slot3: { placeholder: "::: [SYSTEM SLOT 03: READY] :::", content: null },
            slot4: { placeholder: "::: [SYSTEM SLOT 04: READY] :::", content: null },
        };
        addSystemLog("모듈 슬롯 대기 모드 활성화", "INFO");
    };

    const pythonSnippets = computed(() => [
        { id: 1, code: "StandardScaler()", label: "Initialize Scaler" },
        { id: 2, code: "scaler.fit(train_df)", label: "Fit Model (Train Data)" },
        { id: 3, code: "scaler.transform(train_df)", label: "Transform Train Data" },
        { id: 4, code: "scaler.transform(test_df)", label: "Transform Test Data" },
    ]);

    // Click insertion disabled as per request ("Drag Only")
    const insertSnippet = () => {
        gameState.feedbackMessage = "모듈을 마우스로 끌어서(Drag) 배치하십시오.";
        addSystemLog("안내: 클릭 대신 드래그 앤 드롭을 사용하세요.", "WARN");
    };

    const handleSlotDrop = (slotKey, snippetCode) => {
        if (gameState.codeSlots[slotKey]) {
            gameState.codeSlots[slotKey].content = snippetCode;
            addSystemLog(`슬롯[${slotKey}] 모듈 장착: ${snippetCode}`, "SUCCESS");

            // Check for match immediately? Or wait for submit? 
            // Let's just update state.
        }
    };

    const submitPythonFill = () => {
        const s = gameState.codeSlots;
        // Validate correct order
        // Correct Expected:
        // slot1: StandardScaler()
        // slot2: scaler.fit(train_df)
        // slot3: scaler.transform(train_df)
        // slot4: scaler.transform(test_df)

        const isCorrect =
            s.slot1.content === "StandardScaler()" &&
            s.slot2.content === "scaler.fit(train_df)" &&
            s.slot3.content === "scaler.transform(train_df)" &&
            s.slot4.content === "scaler.transform(test_df)";

        if (isCorrect) {
            gameState.score += 200;
            gameState.feedbackMessage = "구현 무결성 확인.";
            // Fill userCode for evaluation display later
            gameState.userCode = `def leakage_free_scaling(train_df, test_df):
    scaler = StandardScaler()
    scaler.fit(train_df)
    train_scaled = scaler.transform(train_df)
    test_scaled = scaler.transform(test_df)
    return train_scaled, test_scaled`;

            addSystemLog("코드 검증 통과: 파이프라인 정상화", "SUCCESS");
            setTimeout(() => setPhase('DEEP_QUIZ'), 800);
        } else {
            handleDamage();
            gameState.feedbackMessage = "모듈 순서 또는 종류가 잘못되었습니다.";
            addSystemLog("오류: 파이프라인 구성 결함", "ERROR");
        }
    };

    // --- 5. Deep Quiz Phase ---
    const deepQuizQuestion = computed(() => ({
        question: "다음 중 데이터 누수가 위험한 이유를 가장 정확히 설명한 것은 무엇입니까?",
        options: [
            { text: "데이터 누수는 모델이 미래 정보를 학습하게 만든다", correct: true },
            { text: "검증 데이터와 학습 데이터는 섞일수록 좋다", correct: false }
        ]
    }));

    const submitDeepQuiz = (optionIndex) => {
        const selected = deepQuizQuestion.value.options[optionIndex];
        if (selected && selected.correct) {
            gameState.score += 300;
            handleVictory();
        } else {
            handleDamage();
            gameState.feedbackMessage = "개념 오인.";
            addSystemLog("검증 실패: 개념 재확인 필요", "ERROR");
        }
    };


    // --- Common ---
    const handleDamage = () => {
        gameState.playerHP -= 15;
        addSystemLog(`시스템 손상: HP -15 (현재: ${gameState.playerHP}%)`, "WARN");
        if (gameState.playerHP <= 0) {
            gameState.phase = 'DEFEAT';
            addSystemLog("CRITICAL: 시스템 무결성 붕괴", "ERROR");
        }
    };

    const handleVictory = () => {
        generateEvaluation();
        gameState.phase = 'EVALUATION';
        gameState.score += 500 + (gameState.playerHP * 5);
        gameState.feedbackMessage = "미션 종료.";
        addSystemLog("미션 클리어: 데이터 정상화", "SUCCESS");
    };

    const nextMission = () => {
        const nextId = gameState.currentStageId + 1;
        const nextQuest = aiQuests.find(q => q.id === nextId);
        if (nextQuest) {
            gameState.currentStageId = nextId;
            setPhase('DIAGNOSTIC_1');
        } else {
            gameState.phase = 'CAMPAIGN_END';
        }
    };

    const restartMission = () => {
        addSystemLog("시스템 재부팅 시퀀스 초기화...", "WARN");
        gameState.playerHP = 100;
        setPhase('DIAGNOSTIC_1');
    };

    // --- Evaluation Logic ---
    const evaluationResult = reactive({
        finalScore: 0,
        verdict: "",
        details: [],
        aiAnalysis: "분석 중...",
        seniorAdvice: "분석 중...",
        scoreTier: "Junior",
        supplementary: [] // New: Generated problems/topics
    });

    const isEvaluating = ref(false);

    const generateEvaluation = async () => {
        isEvaluating.value = true;
        addSystemLog("AI 아키텍트가 최종 리포트를 생성 중입니다...", "INFO");

        // Basic score calculation
        const maxScore = 1300;
        const normalizedScore = Math.min(100, Math.floor((gameState.score / maxScore) * 100));
        evaluationResult.finalScore = normalizedScore;
        evaluationResult.verdict = normalizedScore >= 80 ? "시스템 복구 완료" : (normalizedScore >= 50 ? "부분적 성공" : "재건축 필요");

        // Prepare context for LLM (Enhanced for high-quality recommendations)
        const userPerformance = {
            missionObjective: "Prevent Data Leakage during Scaling",
            designPhaseReasoning: gameState.phase3Reasoning,
            implementationCode: gameState.userCode,
            finalScore: normalizedScore,
            reliabilityHP: gameState.playerHP,
            systemAuditLogs: JSON.parse(JSON.stringify(gameState.systemLogs))
        };

        try {
            // Call LLM for dynamic analysis & supplementary problems
            const response = await axios.post('/api/core/ai-evaluate/', {
                quest_title: "Data Leakage Prevention",
                user_logic: userPerformance.designPhaseReasoning,
                mode: 'final_report',
                performance: userPerformance,
                intent: "Identify knowledge gaps and suggest advanced data engineering topics"
            });

            const aiResult = response.data;
            evaluationResult.aiAnalysis = aiResult.analysis || "데이터 정제 아키텍처가 견고합니다. 누수 방지 로직이 정확히 설계되었습니다.";
            evaluationResult.seniorAdvice = aiResult.advice || "실제 환경에서는 Scikit-learn Pipeline을 사용하여 전처리를 자동화하는 것이 좋습니다.";

            // Dynamic recommendations based on OpenAI processing
            if (aiResult.supplementary && Array.isArray(aiResult.supplementary)) {
                evaluationResult.supplementary = aiResult.supplementary;
            } else {
                evaluationResult.supplementary = [
                    { title: "Pipeline & ColumnTransformer", desc: "머신러닝 워크플로우 자동화 및 데이터 오염 원천 차단" },
                    { title: "Time-Series Data Leakage", desc: "시계열 데이터에서 발생하기 쉬운 Look-ahead Bias 방지법" },
                    { title: "Target Encoding Leakage", desc: "범주형 변수 처리 시 정답 데이터가 유출되는 심각한 오류 해결" }
                ];
            }

            // Tiering
            if (normalizedScore > 80) evaluationResult.scoreTier = "시니어 아키텍트";
            else if (normalizedScore > 50) evaluationResult.scoreTier = "주니어 아키텍트";
            else evaluationResult.scoreTier = "수습 엔지니어";

        } catch (error) {
            console.error("LLM Evaluation Failed:", error);
            // Fallback to static evaluation if API fails
            evaluationResult.aiAnalysis = "통신 지연으로 간이 리포트를 생성합니다. 기본적인 패턴은 이해하고 있으나 디테일이 필요합니다.";
            evaluationResult.seniorAdvice = "성능 최적화보다는 '재현 가능한 파이프라인'을 만드는 것에 집중하세요.";
            evaluationResult.supplementary = [
                { title: "Scikit-Learn 심화", desc: "다양한 Scaler들의 특성 비교 학습" },
                { title: "커스텀 변환기", desc: "FunctionTransformer를 활용한 전처리 자동화" }
            ];
            evaluationResult.scoreTier = normalizedScore > 50 ? "주니어 아키텍트" : "수습 엔지니어";
        } finally {
            isEvaluating.value = false;
            addSystemLog("리포트 생성 완료.", "SUCCESS");
        }

        // Detailed category breakdown (Keep static for UI structure, but could be dynamic too)
        evaluationResult.details = [
            {
                category: "전략적 논리",
                score: gameState.phase3Reasoning.length > 20 ? 90 : 40,
                comment: gameState.phase3Reasoning.length > 20 ? "논리적 흐름이 명확하고 체계적입니다." : "서술이 너무 짧아 의도를 파악하기 어렵습니다.",
                improvements: ["예외 처리 로직 보강", "메모리 최적화 고려"]
            },
            {
                category: "구현 능력",
                score: gameState.userCode.includes("fit") && gameState.userCode.includes("transform") ? 100 : 50,
                comment: "표준 Scikit-learn 패턴을 정확히 준수했습니다.",
                improvements: ["변수 명명 규칙 통일", "주석 상세화"]
            }
        ];
    };


    return {
        gameState,
        enemyThreat,

        // Data
        diagnosticQuestion1,
        diagnosticQuestion2,
        deepQuizQuestion,
        pythonSnippets,
        evaluationResult,
        isEvaluating,

        // Reasoning Blocks for Phase 3
        logicBlocks: [
            { id: 1, text: "StandardScaler 객체를 생성한다." },
            { id: 2, text: "Train 데이터만을 사용하여 스케일러를 학습(fit)시킨다." },
            { id: 3, text: "학습된 스케일러로 Train 데이터를 변환(transform)한다." },
            { id: 4, text: "동일한 스케일러로 Test 데이터를 변환(transform)하여 누수를 방지한다." },
            { id: 5, text: "Test 데이터에는 절대로 fit을 사용하지 않는다." }
        ],

        // Actions
        startGame,
        submitDiagnostic1,
        submitDiagnostic2,
        submitPseudo,
        submitPythonFill,
        submitDeepQuiz,
        insertSnippet,
        handleSlotDrop,
        nextMission,
        restartMission,
        initPhase4Scaffolding,
        handlePseudoInput,
        addLogicBlock: (text) => {
            if (!gameState.phase3Reasoning.includes(text)) {
                gameState.phase3Reasoning += (gameState.phase3Reasoning ? "\n" : "") + "- " + text;
            }
        }
    };
}
