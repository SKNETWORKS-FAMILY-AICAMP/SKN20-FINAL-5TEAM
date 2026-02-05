
import { ref, computed, reactive, onMounted } from 'vue';
import { aiQuests } from './stages.js';

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

        // Phase 4 State
        // implementing "Monaco Editor" style content
        userCode: "", // The content of the code editor

        // Interactive Messages
        coduckMessage: "경고! 접근하는 모든 데이터는 적입니다!",
        feedbackMessage: null, // "Correct!" or "Error!"
    });

    // --- Hint Timer Logic ---
    let hintTimer = null;

    const startHintTimer = () => {
        if (hintTimer) clearTimeout(hintTimer);
        gameState.showHint = false;
        hintTimer = setTimeout(() => {
            gameState.showHint = true;
        }, 30000); // 30 seconds
    };

    const resetHintTimer = () => {
        if (hintTimer) clearTimeout(hintTimer);
        // Only hide hint if it was shown? Or keep it? Usually typing hides it or resets it.
        // Let's hide it when typing starts to clean up interface
        gameState.showHint = false;
        hintTimer = setTimeout(() => {
            gameState.showHint = true;
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
                    break;
                case 'DIAGNOSTIC_2':
                    gameState.coduckMessage = "무엇을 신뢰할지 결정해야 합니다.";
                    break;
                case 'PSEUDO_WRITE':
                    gameState.coduckMessage = "어떤 순서로 생각하는지 보여주세요.";
                    gameState.phase3Reasoning = ""; // Reset for new entry
                    startHintTimer(); // Start 30s timer
                    break;
                case 'PYTHON_FILL':
                    gameState.coduckMessage = "사고와 코드가 일치하는지 확인하십시오.";
                    // Initialize Scaffolding for Phase 4
                    if (typeof initPhase4Scaffolding === 'function') {
                        initPhase4Scaffolding();
                    }
                    break;
                case 'DEEP_QUIZ':
                    gameState.coduckMessage = "설명할 수 있다면, 이해한 것입니다.";
                    break;
                case 'EVALUATION':
                    gameState.coduckMessage = "평가가 완료되었습니다.";
                    break;
            }
        } catch (e) {
            console.error("[CoduckWars] Error in setPhase:", e);
        }
    };

    const startGame = () => {
        console.log("[CoduckWars] Game Starting...");
        gameState.currentStageId = 1;
        gameState.score = 0;
        gameState.playerHP = 100;
        gameState.feedbackMessage = null;
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
            setTimeout(() => setPhase('DIAGNOSTIC_2'), 800);
        } else {
            handleDamage();
            gameState.feedbackMessage = "판단 오류.";
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
            setTimeout(() => setPhase('PSEUDO_WRITE'), 800);
        } else {
            handleDamage();
            gameState.feedbackMessage = "전략 오류.";
        }
    };

    // --- 3. Pseudo Write Phase ---
    const submitPseudo = () => {
        if (gameState.phase3Reasoning.length < 10) {
            gameState.feedbackMessage = "논리가 부족합니다.";
            return;
        }
        if (hintTimer) clearTimeout(hintTimer); // Stop timer on submit
        gameState.score += 100;
        gameState.feedbackMessage = "설계 접수.";
        setTimeout(() => setPhase('PYTHON_FILL'), 800);
    };

    // --- 4. Implementation Phase ---
    const initPhase4Scaffolding = () => {
        // Scaffolding Text
        const strategy = gameState.selectedStrategyLabel || "전략 미수립";
        let summary = gameState.phase3Reasoning || "(사고 내용 없음)";
        // Simple summary format
        if (summary.length > 300) summary = summary.substring(0, 300) + "...";

        gameState.userCode = `def leakage_free_scaling(train_df, test_df):
    
    # 1. 학습 데이터(train) 기준으로 스케일러 생성
    # TODO: 여기에 코드를 작성하세요

    # 2. 학습 데이터로만 기준 학습 (fit)
    # TODO: 여기에 코드를 작성하세요

    # 3. 동일한 기준을 학습 데이터에 적용 (transform)
    # TODO: 여기에 코드를 작성하세요

    # 4. 동일한 기준을 테스트 데이터에 적용 (transform)
    # TODO: 여기에 코드를 작성하세요

    return train_scaled, test_scaled`;
    };

    const pythonSnippets = computed(() => [
        { code: "StandardScaler()", label: "스케일러 생성" },
        { code: "scaler.fit(train_df)", label: "학습 데이터 기준 학습" },
        { code: "scaler.transform(train_df)", label: "학습 데이터 변환" },
        { code: "scaler.transform(test_df)", label: "테스트 데이터 변환" },
    ]);

    const insertSnippet = (snippetCode) => {
        if (gameState.userCode.includes("# TODO: 여기에 코드를 작성하세요")) {
            gameState.userCode = gameState.userCode.replace("# TODO: 여기에 코드를 작성하세요", snippetCode);
        } else {
            gameState.userCode += "\n    " + snippetCode;
        }
    };

    const submitPythonFill = () => {
        // Basic check: did they use correct methods?
        const code = gameState.userCode;
        const required = ["StandardScaler()", "scaler.fit(train_df)", "scaler.transform(train_df)", "scaler.transform(test_df)"];

        const missing = required.filter(r => !code.includes(r));

        if (missing.length === 0) {
            gameState.score += 200;
            gameState.feedbackMessage = "구현 완료.";
            setTimeout(() => setPhase('DEEP_QUIZ'), 800);
        } else {
            handleDamage();
            gameState.feedbackMessage = "사고 불일치: 사고 요약과 코드 적용 순서를 비교하십시오.";
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
        }
    };


    // --- Common ---
    const handleDamage = () => {
        gameState.playerHP -= 15;
        if (gameState.playerHP <= 0) {
            gameState.phase = 'DEFEAT';
        }
    };

    const handleVictory = () => {
        generateEvaluation();
        gameState.phase = 'EVALUATION';
        gameState.score += 500 + (gameState.playerHP * 5);
        gameState.feedbackMessage = "미션 종료.";
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
        gameState.playerHP = 100;
        setPhase('DIAGNOSTIC_1');
    };

    // --- Evaluation Logic ---
    const evaluationResult = reactive({
        pseudoLength: 0,
        requirementsMet: "",
        aiAnalysis: "",
        tailQuestionResult: "",
        seniorAdvice: "",
        scoreTier: "Junior"
    });

    const generateEvaluation = () => {
        // Calculate a 0-100 scale score based on Game Score (Max approx 1200)
        // Diagnostic(200) + Pseudo(100) + Code(200) + Quiz(300) + HP bonus(500) = ~1300
        const maxScore = 1300;
        const normalizedScore = Math.min(100, Math.floor((gameState.score / maxScore) * 100));

        evaluationResult.finalScore = normalizedScore;
        evaluationResult.verdict = normalizedScore >= 80 ? "시스템 복구 완료" : (normalizedScore >= 50 ? "부분적 성공" : "재건축 필요");

        // Detailed category breakdown
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
            },
            {
                category: "개념적 깊이",
                score: gameState.score >= 500 ? 95 : 60,
                comment: "데이터 누수(Leakage)의 위험성을 정확히 인지하고 있습니다.",
                improvements: ["고급 스케일링 기법 학습", "파이프라인 구축 연습"]
            }
        ];

        // Overall Analysis
        if (normalizedScore > 80) {
            evaluationResult.aiAnalysis = "뛰어난 아키텍트의 자질이 보입니다. 전체적인 설계와 구현이 조화를 이루고 있습니다.";
            evaluationResult.scoreTier = "시니어 아키텍트";
        } else if (normalizedScore > 50) {
            evaluationResult.aiAnalysis = "기본적인 패턴은 이해하고 있으나, 디테일한 부분에서 아쉬움이 남습니다. 특히 '단계적 사고'를 끝까지 유지하는 것에 집중하세요.";
            evaluationResult.scoreTier = "주니어 아키텍트";
        } else {
            evaluationResult.aiAnalysis = "시스템 복구에 실패했습니다. 데이터 흐름을 처음부터 다시 설계해야 합니다.";
            evaluationResult.scoreTier = "수습 엔지니어";
        }

        evaluationResult.seniorAdvice = "성능 최적화보다는 '재현 가능한 파이프라인'을 만드는 것이 데이터 엔지니어링의 핵심입니다.";
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

        // Actions
        startGame,
        submitDiagnostic1,
        submitDiagnostic2,
        submitPseudo,
        submitPythonFill,
        submitDeepQuiz,
        insertSnippet,
        nextMission,
        restartMission,
        handlePseudoInput // Export this new action
    };
}
