import { ref, computed, reactive, onMounted, watch } from 'vue';
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
        missionContext: "", // Loaded from stages.js
        constraints: [],    // Loaded from stages.js

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

    // --- Idle Monitor & Real-time Feedback ---
    let idleInterval = null;
    let lastInputTime = Date.now();

    const startIdleMonitor = () => {
        lastInputTime = Date.now();
        if (idleInterval) clearInterval(idleInterval);

        idleInterval = setInterval(() => {
            if (gameState.phase !== 'PSEUDO_WRITE') return;

            const now = Date.now();
            const diff = now - lastInputTime;

            // 25 seconds idle: Specific hint based on blank state
            if (diff > 25000 && diff < 26000) {
                if (gameState.phase3Reasoning.length < 10) {
                    gameState.coduckMessage = "시작이 어렵다면 '1. 먼저 학습 데이터의 분포를 파악한다' 라고 적어보세요.";
                } else {
                    gameState.coduckMessage = "잘 하고 계십니다. '테스트 데이터'를 어떻게 다룰지도 꼭 포함해주세요.";
                }
            }
        }, 1000);
    };

    const stopIdleMonitor = () => {
        if (idleInterval) clearInterval(idleInterval);
        idleInterval = null;
    };

    const handlePseudoInput = (e) => {
        const prevLen = gameState.phase3Reasoning.length;
        gameState.phase3Reasoning = e.target.value;
        const newLen = gameState.phase3Reasoning.length;

        lastInputTime = Date.now();
        resetHintTimer();

        // Real-time flow feedback (Throttled random praise)
        // Trigger only on significant typing chunks or randomly
        if (newLen > prevLen && newLen % 30 === 0) {
            const praises = [
                "좋습니다! 논리가 구체화되고 있어요.",
                "계속 하세요! 시스템 동기화율이 상승 중입니다.",
                "훌륭한 접근입니다. 키워드를 놓치지 마세요.",
                "그렇죠! 바로 그겁니다."
            ];
            gameState.coduckMessage = praises[Math.floor(Math.random() * praises.length)];
        }
    };

    // --- Current Mission Data ---
    const currentMission = computed(() => {
        if (!aiQuests || aiQuests.length === 0) return {};
        // Fallback to first quest if id not found
        return aiQuests.find(q => q.id === gameState.currentStageId) || aiQuests[0];
    });

    // --- Sync Game State with Mission Data ---
    watch(currentMission, (newMission) => {
        if (newMission) {
            // Support new data structure (Phase 3)
            if (newMission.designContext) {
                gameState.missionContext = newMission.designContext.currentIncident || "";
                gameState.constraints = newMission.designContext.engineeringRules || [];
            } else {
                // Fallback to old structure
                gameState.missionContext = newMission.incidentContext || "";
                gameState.constraints = newMission.constraints || [];
            }
        }
    }, { immediate: true });

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
        stopIdleMonitor(); // Stop idle checks on phase switch

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
                    startIdleMonitor(); // Start real-time feedback
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
    const diagnosticQuestion1 = computed(() => {
        const q = currentMission.value.interviewQuestions?.[0];
        return q || { question: "데이터 로딩 실패", options: [] };
    });

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

            // Show Coduck's specific comment
            if (q.coduckComment) {
                gameState.coduckMessage = q.coduckComment.replace('{username}', 'Architect');
            }

            setTimeout(() => setPhase('DIAGNOSTIC_2'), 1500); // 1.5s delay to read message
        } else {
            handleDamage();
            gameState.feedbackMessage = "판단 오류.";
            addSystemLog("오류: 잘못된 판단입니다", "ERROR");
        }
    };

    // --- 2. Diagnostic Phase 2 (Q2) ---
    const diagnosticQuestion2 = computed(() => {
        const q = currentMission.value.interviewQuestions?.[1];
        return q || { question: "데이터 로딩 실패", options: [] };
    });

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

            // Show Coduck's specific comment
            if (q.coduckComment) {
                gameState.coduckMessage = q.coduckComment.replace('{username}', 'Architect');
            }

            setTimeout(() => setPhase('PSEUDO_WRITE'), 1500); // 1.5s delay to read message
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
        // Reduced to 3 slots for Data Leakage logic
        gameState.codeSlots = {
            slot1: { placeholder: "::: [SYSTEM SLOT 01: READY] :::", content: null },
            slot2: { placeholder: "::: [SYSTEM SLOT 02: READY] :::", content: null },
            slot3: { placeholder: "::: [SYSTEM SLOT 03: READY] :::", content: null }
        };
        gameState.feedbackMessage = null; // Clear previous errors
        addSystemLog("모듈 슬롯 대기 모드 활성화", "INFO");
    };

    const pythonSnippets = computed(() => {
        const m = currentMission.value;

        // 1. explicit snippets (Old structure)
        if (m.pythonSnippets) {
            return m.pythonSnippets.map((s, idx) => ({
                id: idx + 1,
                code: s.code,
                label: s.label || s.code
            }));
        }

        // 2. Implicit snippets from implementation.codeValidation.mustContain (New structure)
        // We generate snippets based on the required code lines AND correct/incorrect options
        if (m.implementation?.codeValidation?.mustContain) {
            const goods = m.implementation.codeValidation.mustContain;
            const bads = m.implementation.codeValidation.mustNotContain || [];

            // Combine and map to snippet objects
            // We can add a simple shuffle or just list them. For stability, just listing.
            const allSnippets = [...goods, ...bads];

            return allSnippets.map((codeStr, idx) => ({
                id: idx + 1,
                code: codeStr,
                label: codeStr // Use code as label for now
            }));
        }

        return [];
    });

    // Click insertion disabled as per request ("Drag Only")
    const insertSnippet = () => {
        gameState.feedbackMessage = "모듈을 마우스로 끌어서(Drag) 배치하십시오.";
        addSystemLog("안내: 클릭 대신 드래그 앤 드롭을 사용하세요.", "WARN");
    };

    const handleSlotDrop = (slotKey, snippetCode) => {
        if (gameState.codeSlots[slotKey]) {
            gameState.codeSlots[slotKey].content = snippetCode;
            addSystemLog(`슬롯[${slotKey}] 모듈 장착`, "SUCCESS"); // Don't show full code to keep log clean
        }
    };

    const submitPythonFill = () => {
        const s = gameState.codeSlots;
        const m = currentMission.value;

        // Validation Logic
        let isCorrect = false;
        let feedback = "";

        // 1. New Structure (implementation.codeValidation)
        // We simulate "ordered" check by seeing if slot 1..N match mustContain 0..N
        if (m.implementation?.codeValidation?.mustContain) {
            const required = m.implementation.codeValidation.mustContain;
            // Check order: slot1 == required[0], slot2 == required[1], etc.
            const slots = [
                s.slot1.content?.trim(),
                s.slot2.content?.trim(),
                s.slot3.content?.trim()
            ];

            // Check if all matched
            isCorrect = required.every((req, idx) => {
                const userVal = slots[idx];
                const cleanReq = req.trim();
                const match = userVal === cleanReq;
                if (!match) {
                    console.log(`Mismatch at ${idx}: User[${userVal}] vs Req[${cleanReq}]`);
                }
                return match;
            });

            // Also check 'mustNotContain'
            if (isCorrect && m.implementation.codeValidation.mustNotContain) {
                const hasForbidden = m.implementation.codeValidation.mustNotContain.some(forbid =>
                    slots.includes(forbid.trim())
                );
                if (hasForbidden) {
                    isCorrect = false;
                    feedback = "금지된 코드(오답)가 포함되어 있습니다.";
                }
            }

            if (!isCorrect && !feedback) {
                feedback = "모듈 순서가 틀렸거나 잘못된 모듈입니다.";
                // Debug: specific error log
                addSystemLog(`검증 실패: 순서 또는 값 불일치`, "WARN");
            }

        } else if (m.id === 1 || !m.expectedSlots) {
            // Hardcoded Fallback for Chapter 1 (Data Leakage)
            const required = [
                "scaler.fit(train_df)",
                "scaler.transform(train_df)",
                "scaler.transform(test_df)"
            ];

            isCorrect =
                s.slot1.content?.trim() === required[0] &&
                s.slot2.content?.trim() === required[1] &&
                s.slot3.content?.trim() === required[2];

            // Check negative rule
            const allSlots = [s.slot1.content, s.slot2.content, s.slot3.content];
            if (allSlots.some(c => c?.trim() === "scaler.fit(test_df)")) {
                isCorrect = false;
                feedback = "금지된 코드(오답)가 포함되어 있습니다. (Test Data Leakage)";
            }

            if (!isCorrect && !feedback) {
                feedback = "모듈 순서가 틀렸거나 올바른 모듈이 아닙니다.";
                addSystemLog(`검증 실패: 로직 불일치`, "WARN");
            }

        } else if (m.expectedSlots) {
            // 2. Old Structure (expectedSlots)
            const expected = m.expectedSlots;
            isCorrect =
                s.slot1.content === expected[0] &&
                s.slot2.content === expected[1] &&
                s.slot3.content === expected[2] &&
                s.slot4.content === expected[3];
            if (!isCorrect) feedback = "모듈 순서 또는 종류가 잘못되었습니다.";
        } else {
            // 3. Fallback / Error
            console.warn("No validation rules found for this stage.");
            isCorrect = false;
        }


        if (isCorrect) {
            gameState.score += 200;
            gameState.feedbackMessage = "구현 무결성 확인.";
            // Fill userCode for evaluation display later
            // Prefer template from new structure
            gameState.userCode = m.implementation?.codeFrame?.template || m.pythonTemplate || "코드 생성 완료";

            addSystemLog("코드 검증 통과: 파이프라인 정상화", "SUCCESS");
            setTimeout(() => setPhase('DEEP_QUIZ'), 800);
        } else {
            handleDamage();
            gameState.feedbackMessage = feedback || "구현 오류.";
            addSystemLog("오류: 파이프라인 구성 결함", "ERROR");
        }
    };

    // --- 5. Deep Quiz Phase ---
    const deepQuizQuestion = computed(() => {
        const m = currentMission.value;
        // Support new structure (deepDiveQuestion) or old (deepQuiz)
        return m.deepDiveQuestion || m.deepQuiz || { question: "데이터 로딩 실패", options: [] };
    });

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
        },
        currentMission, // Expose for UI
        explainStep: (stepIdx) => {
            const steps = currentMission.value.cards;
            if (!steps || !steps[stepIdx]) return;

            const step = steps[stepIdx];
            const explanations = [
                "제 분석 모듈을 가동하여 시스템 전체의 데이터 흐름을 시각화합니다. 어디가 막혔는지 찾아낼게요!", // Step 1
                "오염된 데이터를 걸러내기 위한 정밀 필터를 설계합니다. 제 알고리즘 회로를 동기화해주세요.", // Step 2
                "파이썬 코드로 실제 정화 장치를 가동합니다. 구문 오류가 없도록 제가 실시간 감시할게요.", // Step 3
                "모든 시스템이 정상인지 최종 점검하고 재부팅 승인 도장을 찍습니다. 준비되셨나요?" // Step 4
            ];

            gameState.coduckMessage = step.coduckMsg || explanations[stepIdx] || "이 단계에서 필요한 작업을 수행하세요.";
            addSystemLog(`가이드 요청: ${step.text.split(':')[0]}`, "INFO");
        }
    };
}
