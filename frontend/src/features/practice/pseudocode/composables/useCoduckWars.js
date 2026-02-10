import { ref, computed, reactive, onMounted } from 'vue';
import axios from 'axios';
import { quickCheckPseudocode, runPseudocodeAgent } from '../api/pseudocodeApi.js';
import { useGameEngine } from './useGameEngine.js';
import { useCodeRunner } from './useCodeRunner.js';

export function useCoduckWars() {
    const DEBUG_MODE = true;

    // --- 1. Game Logic Core ---
    const {
        gameState,
        currentMission,
        missionContext,
        constraints,
        enemyThreat,
        addSystemLog,
        setPhase,
        handleDamage,
        nextMission,
        restartMission,
        startGame,
        selectStage
    } = useGameEngine();

    // --- 2. Code Runner Logic ---
    const {
        runnerState,
        initPhase4Scaffolding,
        insertSnippet,
        handleSlotDrop,
        submitPythonFill
    } = useCodeRunner(gameState, currentMission, addSystemLog, setPhase);

    // [2026-02-09] Task 1.2: 레이스 컨디션 방지 - 중복 요청 차단
    const isProcessing = ref(false);

    // --- 3. Additional State specific to Composable ---
    // Hint Timer Logic (Could be in GameEngine, but kept here for now)
    let hintTimer = null;

    const startHintTimer = () => {
        if (hintTimer) clearTimeout(hintTimer);
        gameState.showHint = false;
        hintTimer = setTimeout(() => {
            gameState.showHint = true;
            addSystemLog("힌트 프로토콜 자동 활성화", "INFO");
        }, 30000);
    };

    const resetHintTimer = () => {
        if (hintTimer) clearTimeout(hintTimer);
        gameState.showHint = false;
        hintTimer = setTimeout(() => {
            gameState.showHint = true;
            addSystemLog("힌트 프로토콜 자동 활성화", "INFO");
        }, 30000);
    };

    // Watch for phase changes to trigger side effects
    // (In a fuller refactor, use watch() on gameState.phase)
    const originalSetPhase = setPhase;
    // Override setPhase to add local side effects if needed (like timers)
    // For now, we manually handle it or rely on the UI to call startHintTimer

    const handlePseudoInput = (e) => {
        gameState.phase3Reasoning = e.target.value;
        resetHintTimer();
    };

    // --- Diagnostic Logic (Phase 1 & 2) ---
    const diagnosticQuestion1 = computed(() => {
        const mission = currentMission.value;
        if (!mission || !mission.interviewQuestions || !mission.interviewQuestions[0]) {
            return { question: "로딩 중...", options: [] };
        }
        const q = mission.interviewQuestions[0];
        return {
            question: q.question,
            options: q.options.map(opt => ({
                text: opt.text,
                bullets: opt.bullets || [],
                correct: opt.correct
            }))
        };
    });

    const submitDiagnostic1 = (optionIndex) => {
        const q = diagnosticQuestion1.value;
        if (!q.options[optionIndex]) return;

        if (q.options[optionIndex].correct) {
            gameState.score += 7.5;
            gameState.feedbackMessage = "프로토콜 확인.";
            addSystemLog("선택 승인: 프로토콜 재가동", "SUCCESS");
            setTimeout(() => setPhase('DIAGNOSTIC_2'), 800);
        } else {
            handleDamage();
            gameState.feedbackMessage = "판단 오류.";
            addSystemLog("오류: 잘못된 판단입니다", "ERROR");
        }
    };

    const diagnosticQuestion2 = computed(() => {
        const mission = currentMission.value;
        if (!mission || !mission.interviewQuestions || !mission.interviewQuestions[1]) {
            return { question: "로딩 중...", options: [] };
        }
        const q = mission.interviewQuestions[1];
        return {
            question: q.question,
            options: q.options.map(opt => ({
                text: opt.text,
                bullets: opt.bullets || [],
                correct: opt.correct
            }))
        };
    });

    const submitDiagnostic2 = (optionIndex) => {
        const q = diagnosticQuestion2.value;
        const selected = q.options[optionIndex];

        gameState.selectedStrategyLabel = selected.text;

        if (selected.correct) {
            gameState.score += 7.5;
            gameState.feedbackMessage = "전략 수립.";
            addSystemLog(`전략 채택: ${selected.text}`, "SUCCESS");
            setTimeout(() => {
                setPhase('PSEUDO_WRITE');
                startHintTimer(); // Start timer for Phase 3
            }, 800);
        } else {
            handleDamage();
            gameState.feedbackMessage = "전략 오류.";
            addSystemLog("경고: 유효하지 않은 전략", "WARN");
        }
    };

    // --- Pseudo Write Phase (Phase 3) ---
    const submitPseudo = async () => {
        // [2026-02-09] Task 1.2: 중복 클릭 방지
        if (isProcessing.value) {
            addSystemLog("이미 처리 중입니다. 잠시만 기다려주세요.", "WARN");
            return;
        }

        if (!gameState.phase3Reasoning.trim()) {
            alert("아키텍처 설계를 입력해주세요.");
            return;
        }

        if (hintTimer) clearTimeout(hintTimer);

        // 즉시 평가
        isProcessing.value = true;
        gameState.feedbackMessage = "논리 분석 중...";
        addSystemLog("LLM 기반 논리 구조 분석 중...", "INFO");

        try {
            // [수정일: 2026-02-10] 백엔드 지능형 에이전트(Coduck Wizard) 호출로 변경
            // 단순 룰 베이스 + AI를 넘어, 사용자의 전략과 제약사항을 심층 분석
            const evaluation = await runPseudocodeAgent({
                user_logic: gameState.phase3Reasoning,
                quest_title: currentMission.value.title,
                quest_description: currentMission.value.missionObjective,
                selected_strategy: gameState.selectedStrategyLabel,
                constraints: constraints.value
            });

            gameState.phase3Score = evaluation.score;
            gameState.phase3Feedback = evaluation.advice; // 핵심 조언을 우선 표시

            // 상세 리포트 항목 업데이트
            evaluationResult.verdict = evaluation.verdict;
            evaluationResult.aiAnalysis = evaluation.analysis;
            evaluationResult.seniorAdvice = evaluation.advice;
            evaluationResult.tailQuestion = evaluation.tail_question;

            if (evaluation.metrics) {
                evaluationResult.details = Object.entries(evaluation.metrics).map(([category, data]) => ({
                    category,
                    score: data.score,
                    comment: data.comment,
                    improvements: data.improvements || []
                }));
            }

            // 점수 차등 부여
            if (evaluation.score >= 85) {
                gameState.score += 20;
                gameState.feedbackMessage = `우수 (${evaluation.score}점): ${evaluation.advice}`;
                addSystemLog(`논리 평가: 우수 (${evaluation.score}/100) +20점`, "SUCCESS");
            } else if (evaluation.score >= 70) {
                gameState.score += 15;
                gameState.feedbackMessage = `양호 (${evaluation.score}점): ${evaluation.advice}`;
                addSystemLog(`논리 평가: 양호 (${evaluation.score}/100) +15점`, "SUCCESS");
            } else if (evaluation.score >= 50) {
                gameState.score += 10;
                gameState.feedbackMessage = `보통 (${evaluation.score}점): ${evaluation.advice}`;
                addSystemLog(`논리 평가: 보통 (${evaluation.score}/100) +10점`, "INFO");
            } else {
                gameState.score += 0;
                gameState.feedbackMessage = `미흡 (${evaluation.score}점): ${evaluation.advice}`;
                addSystemLog(`논리 평가: 미흡 (${evaluation.score}/100) +0점`, "WARN");
            }
            // Save AI questions for later use (e.g. review) or logs
            if (evaluation.questions && evaluation.questions.length > 0) {
                console.log("[Deep Dive Candidates]", evaluation.questions);
            }

            // 점수와 관계없이 다음 단계로 (학습 기회 제공)
            setTimeout(() => {
                setPhase('PYTHON_FILL');
                initPhase4Scaffolding();
            }, 2000);

        } catch (error) {
            console.error('[CoduckWars] Pseudo evaluation error:', error);
            gameState.feedbackMessage = "평가 오류: 다음 단계로 진행합니다.";
            gameState.score += 8;
            addSystemLog("평가 시스템 오류, 기본 점수 부여", "WARN");
            setTimeout(() => {
                setPhase('PYTHON_FILL');
                initPhase4Scaffolding();
            }, 800);
        } finally {
            isProcessing.value = false;
        }
    };

    // --- Deep Quiz Phase (Phase 5) ---
    const deepQuizQuestion = computed(() => {
        const mission = currentMission.value;
        if (!mission || !mission.deepDiveQuestion) {
            return { question: "로딩 중...", options: [] };
        }
        return {
            question: mission.deepDiveQuestion.question,
            options: mission.deepDiveQuestion.options
        };
    });

    const submitDeepQuiz = (optionIndex) => {
        const selected = deepQuizQuestion.value.options[optionIndex];
        if (selected && selected.correct) {
            gameState.score += 20;
            handleVictory();
        } else {
            handleDamage();
            gameState.feedbackMessage = "개념 오인.";
            addSystemLog("검증 실패: 개념 재확인 필요", "ERROR");
        }
    };

    const handleVictory = () => {
        gameState.phase = 'EVALUATION';
        const hpBonus = Math.min(10, Math.round(gameState.playerHP * 0.2 * 10) / 10);
        gameState.score += 15 + hpBonus;
        gameState.score = Math.round(gameState.score * 10) / 10; // 소수점 1자리
        gameState.feedbackMessage = "미션 종료.";
        addSystemLog(`미션 클리어 +15점, HP 보너스 +${hpBonus}점 (총점: ${gameState.score}/100)`, "SUCCESS");
        // Generate Final Report Logic (Using AI Single Pass for Final Report if needed, or re-using existing logic)
        // For now, we trigger the existing generation logic which handles the 5-dimension score
        // Ideally, this should also be refactored to use `evaluatePseudocode` or similar
        generateEvaluation();

        // Unlock next stage
        const nextId = gameState.currentStageId + 1;
        // Logic to update global unlocked state would go here
    };

    // --- Final Evaluation Logic ---
    // (This part is still heavy, but kept here as it orchestrates the final report)
    const evaluationResult = reactive({
        finalScore: 0,
        gameScore: 0,
        aiScore: 0,
        verdict: "",
        details: [],
        aiAnalysis: "분석 중...",
        seniorAdvice: "분석 중...",
        scoreTier: "Junior",
        supplementaryVideos: [],
        tailQuestion: null
    });
    const isEvaluating = ref(false);

    const generateEvaluation = async () => {
        isEvaluating.value = true;
        addSystemLog("AI 아키텍트가 최종 리포트를 생성 중입니다...", "INFO");

        const maxScore = 1300;
        const gamePerformanceScore = Math.min(100, Math.floor((gameState.score / maxScore) * 100));
        evaluationResult.gameScore = gamePerformanceScore;

        try {
            // Re-using the unified feedback or calling a dedicated endpoint
            // For the final report, we might want a comprehensive summary.
            // Since we already have `quickCheck` result, we could reuse it, or call `evaluatePseudocode`.
            // Here we keep the axios call to `ai-evaluate` for the full report generation
            // BUT we should ensure it uses the Optimized logic if possible.

            // For now, we keep the existing endpoint call but structure it to be efficient
            const response = await axios.post('/api/core/ai-evaluate/', {
                quest_title: currentMission.value.title,
                user_logic: gameState.phase3Reasoning,
                user_code: runnerState.userCode,
                mode: 'final_report',
                performance: { score: gameState.score, hp: gameState.playerHP }
                // ... other params
            });

            // Populate evaluationResult from response...
            // (省略: Existing parsing logic kept for continuity)
            const aiResult = response.data;
            evaluationResult.aiScore = aiResult.score || 80;
            evaluationResult.finalScore = Math.floor((gamePerformanceScore * 0.4) + (evaluationResult.aiScore * 0.6));
            // ... mapping metrics ...
            if (aiResult.metrics) {
                evaluationResult.details = Object.entries(aiResult.metrics).map(([category, data]) => ({
                    category,
                    score: typeof data === 'number' ? data : data.score,
                    comment: typeof data === 'number' ? '' : data.comment,
                    improvements: typeof data === 'number' ? [] : [data.improvement]
                }));
            }
            evaluationResult.aiAnalysis = aiResult.analysis || "분석 완료";
            evaluationResult.seniorAdvice = aiResult.advice || "수고하셨습니다.";

        } catch (error) {
            console.error("Final Eval Error", error);
            evaluationResult.finalScore = gamePerformanceScore;
            evaluationResult.aiAnalysis = "통신 지연으로 로컬 리포트로 대체합니다.";
        } finally {
            isEvaluating.value = false;
        }
    };

    // --- Snippets Helpers ---
    const pythonSnippets = computed(() => {
        const mission = currentMission.value;
        if (mission.implementation?.snippets && mission.implementation.snippets.length > 0) {
            return mission.implementation.snippets;
        }
        return [
            { id: 1, code: "StandardScaler()", label: "Initialize Scaler" },
            { id: 2, code: "scaler.fit(train_df)", label: "Fit Model (Train Data)" },
            { id: 3, code: "scaler.transform(train_df)", label: "Transform Train Data" },
            { id: 4, code: "scaler.transform(test_df)", label: "Transform Test Data" }
        ];
    });

    const handleTailQuestion = (option) => {
        if (option.is_correct) {
            addSystemLog(`[Tail Question] 논리 검증 성공: ${option.reason}`, "SUCCESS");
            gameState.feedbackMessage = "✅ 통찰력 있는 분석입니다! 아키텍처 점수가 추가되었습니다.";
        } else {
            addSystemLog(`[Tail Question] 논리 허점 발견: ${option.reason}`, "ERROR");
            gameState.feedbackMessage = "❌ 아키텍처의 맹점이 발견되었습니다. 보완이 필요합니다.";
            gameState.playerHP -= 10;
        }
        evaluationResult.tailQuestion = null;
    };


    return {
        // From GameEngine
        gameState,
        enemyThreat,
        diagnosticQuestion1,
        diagnosticQuestion2,
        deepQuizQuestion,
        evaluationResult,
        isEvaluating,
        currentMission,
        missionContext,
        constraints,

        // Methods
        startGame,
        selectStage,
        submitDiagnostic1,
        submitDiagnostic2,
        submitPseudo,
        submitDeepQuiz,
        handleTailQuestion,
        nextMission,
        restartMission,

        // Code Runner
        userCode: computed(() => runnerState.userCode), // Expose mostly for reading? Or write?
        // Actually we need to make userCode writable in the editor.
        // Let's expose the state object or a specific setter
        runnerState,

        codeSlots: computed(() => runnerState.codeSlots),
        codeExecutionResult: computed(() => runnerState.executionResult),

        insertSnippet,
        handleSlotDrop,
        submitPythonFill: () => submitPythonFill(gameState.phase3Reasoning, handleDamage),
        initPhase4Scaffolding,

        // Data
        pythonSnippets,

        // Misc
        handlePseudoInput,
        logicBlocks: [
            { id: 1, text: "StandardScaler 객체를 생성한다." },
            { id: 2, text: "Train 데이터만을 사용하여 스케일러를 학습(fit)시킨다." },
            { id: 3, text: "학습된 스케일러로 Train 데이터를 변환(transform)한다." },
            { id: 4, text: "동일한 스케일러로 Test 데이터를 변환(transform)하여 누수를 방지한다." },
            { id: 5, text: "Test 데이터에는 절대로 fit을 사용하지 않는다." }
        ],
        addLogicBlock: (text) => {
            if (!gameState.phase3Reasoning.includes(text)) {
                gameState.phase3Reasoning += (gameState.phase3Reasoning ? "\n" : "") + "- " + text;
            }
        },
        explainStep: (idx) => console.log(`Step ${idx}`)
    };
}