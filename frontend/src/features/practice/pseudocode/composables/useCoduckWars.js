/**
 * useCoduckWars.js - Refactored (Restored and Fixed)
 * 
 * 개선 사항:
 * - 5차원 메트릭 기반 평가 적용
 * - Tail Question 분기 로직 추가
 * - 진단 단계 연동 (diagnosticQuestion, submitDiagnostic)
 * - 자동 힌트 타이머 수동화 (사용자 요청)
 * 
 * [2026-02-14] 머지 이슈 및 런타임 에러(TypeError) 완전 해결
 */

import { ref, computed, reactive, watch } from 'vue';
import { useRouter } from 'vue-router';
import { evaluateDiagnosticAnswer } from '../api/pseudocodeApi.js';
import { useEvaluationOrchestrator, EvaluationErrorType } from './useEvaluationOrchestrator.js';
import { useGameEngine } from './useGameEngine.js';
import { useCodeRunner } from './useCodeRunner.js';

export function useCoduckWars() {
    const router = useRouter();

    // Game Engine
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
        selectStage,
        restartMission: engineResetFlow
    } = useGameEngine();

    // Code Runner
    const {
        runnerState,
        initPhase4Scaffolding,
        insertSnippet,
        handleSlotDrop,
        submitPythonFill
    } = useCodeRunner(gameState, currentMission, addSystemLog, setPhase);

    // 중복 요청 차단
    const isProcessing = ref(false);

    // 평가 오케스트레이터
    const { evaluate, errorType, errorMessage } = useEvaluationOrchestrator();

    // UI State
    const isGuideOpen = ref(false);
    const selectedGuideIdx = ref(0);
    const showModelAnswer = ref(false);
    const isEvaluating = ref(false); // [NEW] 평가 중 상태

    // [2026-02-19] 커스텀 모달 상태 (무성의 입력 경고용)
    const showLowEffortModal = ref(false);
    const lowEffortReason = ref("");

    const toggleGuide = () => { isGuideOpen.value = !isGuideOpen.value; };
    const handleGuideClick = (idx) => { selectedGuideIdx.value = idx; };

    // --- Diagnostic Phase Logic ---
    const diagnosticQuestion = computed(() => {
        const stage = currentMission.value;
        if (!stage || !stage.interviewQuestions) return null;
        return stage.interviewQuestions[gameState.diagnosticStep] || null;
    });

    const submitDiagnostic = async (answer) => {
        if (!diagnosticQuestion.value || isProcessing.value) return;

        // 이미 답변 완료된 상태에서 호출되면 다음 단계로 진행
        if (gameState.isDiagnosticAnswered) {
            moveNextDiagnosticStep();
            return;
        }

        try {
            // [객관식 처리]
            if (diagnosticQuestion.value.type === 'CHOICE') {
                const idx = answer;
                const opt = diagnosticQuestion.value.options[idx];

                gameState.diagnosticAnswerIdx = idx;
                gameState.isDiagnosticAnswered = true;

                if (opt.correct || opt.is_correct) {
                    gameState.score += 100;
                    gameState.coduckMessage = opt.feedback || '정확한 개념 이해입니다.';
                    addSystemLog("정확한 분석입니다! 설계 능력이 증명되었습니다.", "SUCCESS");
                } else {
                    handleDamage(15);
                    gameState.coduckMessage = `오답입니다: ${opt.feedback || '논리적 허점이 발견되었습니다.'}`;
                    addSystemLog(`분석 오류가 감지되었습니다.`, "WARN");
                }
                return;
            }

            // [서술형 처리 - 기존 로직 유지하되 피드백 루프 추가 필요시 수정 예정]
            isProcessing.value = true;
            addSystemLog("주관식 답변 분석 중...", "INFO");

            const result = await evaluateDiagnosticAnswer(diagnosticQuestion.value, answer.text || answer);

            gameState.diagnosticAnswer = answer.text || answer;
            gameState.diagnosticScores.push(result.score || 0);

            if (result.is_correct) {
                gameState.coduckMessage = `훌륭합니다! ${result.feedback || '설계 능력이 증명되었습니다.'}`;
                addSystemLog("정확한 분석입니다!", "SUCCESS");
            } else {
                handleDamage(10);
                gameState.coduckMessage = `보충이 필요합니다: ${result.feedback || '논리적 허점이 발견되었습니다.'}`;
                addSystemLog(`분석 오류: ${result.feedback}`, "WARN");
            }

            gameState.isDiagnosticAnswered = true;
        } catch (error) {
            console.error("Diagnostic Evaluation Error:", error);
            addSystemLog("진단 평가 중 오류", "ERROR");
            moveNextDiagnosticStep();
        } finally {
            isProcessing.value = false;
        }
    };

    const moveNextDiagnosticStep = () => {
        gameState.isDiagnosticAnswered = false;
        gameState.diagnosticAnswerIdx = null;
        gameState.coduckMessage = "다음 데이터 분석을 시작합니다.";

        const totalQuestions = currentMission.value?.interviewQuestions?.length || 0;
        if (gameState.diagnosticStep < totalQuestions - 1) {
            gameState.diagnosticStep++;
        } else {
            setPhase('PSEUDO_WRITE');
        }
    };

    // --- Checklist (규칙 기반 실시간 피드백) ---
    // [2026-02-19 수정] 하드코딩 제거 및 미션별 동적 로드
    const ruleChecklist = ref([]);

    // 미션이 변경될 때 체크리스트 초기화
    watch(currentMission, (newMission) => {
        if (newMission && newMission.checklist) {
            ruleChecklist.value = newMission.checklist.map(c => ({
                ...c,
                completed: false,
                hint: c.hint || `${c.label} 개념이 포함되어야 합니다.`
            }));
        }
    }, { immediate: true });

    const completedChecksCount = computed(() =>
        ruleChecklist.value.filter(c => c.completed).length
    );

    const allChecksPassed = computed(() =>
        completedChecksCount.value === ruleChecklist.value.length
    );

    const canSubmitPseudo = computed(() =>
        gameState.phase3Reasoning.trim().length > 0
    );

    // [2026-02-14 수정] 수동 힌트 전환으로 인한 타이머 비활성화
    const startHintTimer = () => { };
    const resetHintTimer = () => { };

    // 실시간 힌트 오리 관련 상태
    const showHintDuck = ref(false);
    const dynamicHintMessage = ref("");

    const toggleHintDuck = () => {
        showHintDuck.value = !showHintDuck.value;
        if (showHintDuck.value) {
            updateDynamicHint();
        }
    };

    const toggleHint = () => {
        toggleHintDuck();
    };

    const updateDynamicHint = () => {
        const code = gameState.phase3Reasoning || "";

        // [2026-02-19 수정] 미션별 동적 힌트 로직
        // 1. 포기/의지 부족 감지
        const surrenderKeywords = /잘\s*모르겠다|모름|몰라|어렵다|어려워|포기|힘들어/i;
        if (surrenderKeywords.test(code) || (code.trim().length > 0 && code.trim().length < 5)) {
            dynamicHintMessage.value = "🐣 [복기 학습 제안]\n\n설계가 막막하신가요? [심화 분석 시작]을 눌러 청사진을 확인해보세요.";
            return;
        }

        // 2. 미완료된 규칙 기반 힌트 제공
        const pendingRule = ruleChecklist.value.find(r => !r.completed);
        if (pendingRule) {
            dynamicHintMessage.value = `🐣 [설계 가이드]\n\n'${pendingRule.label}' 개념이 누락된 것 같아요. ${pendingRule.hint}`;
            return;
        }

        // 3. 분량 부족
        if (code.replace(/\s/g, '').length < 30) {
            dynamicHintMessage.value = "🐣 [구조화 독려]\n\n설계의 인과관계가 잘 드러나도록 문장을 조금 더 다듬어보세요.";
            return;
        }

        dynamicHintMessage.value = "🐣 [설계 완료]\n\n훌륭한 설계입니다! 아키텍트의 승인을 요청해 보세요.";
    };

    watch(() => gameState.phase3Reasoning, (newCode) => {
        ruleChecklist.value.forEach(check => {
            check.completed = check.patterns.some(p => p.test(newCode));
        });
        if (showHintDuck.value) updateDynamicHint();
    });

    watch(() => gameState.phase, (newPhase) => {
        showHintDuck.value = false;
        gameState.showHint = false;
        if (newPhase === 'PYTHON_VISUALIZATION' || newPhase === 'PSEUDO_WRITE') {
            initPhase4Scaffolding();
        }
    });

    const evaluationResult = reactive({
        finalScore: 0,
        overall_score: 0,
        dimensions: {},
        feedback: "",
        strengths: [],
        weaknesses: [],
        tail_question: null,
        converted_python: "",
        one_line_review: "",
        persona_name: "Senior Architect",
        details: [],
        supplementaryVideos: [] // CoduckWars.vue UI 연동용
    });

    const submitPseudo = async () => {
        if (isProcessing.value || !canSubmitPseudo.value) return;
        isProcessing.value = true;
        await runEvaluationProcess();
    };

    // [2026-02-19] 무성의 입력 경고 후 강제 진행 처리
    const confirmLowEffortProceed = async () => {
        showLowEffortModal.value = false;
        isProcessing.value = true;
        await runEvaluationProcess();
    };

    // 공통 평가 프로세스 분리
    const runEvaluationProcess = async () => {
        try {
            gameState.feedbackMessage = "분석 중...";

            const result = await evaluate(currentMission.value, gameState.phase3Reasoning);

            // 네트워크 에러 / LLM 장애로 null 반환 시
            if (!result) {
                if (errorType.value === EvaluationErrorType.AI_TIMEOUT) {
                    addSystemLog("AI 응답 시간 초과. 잠시 후 다시 시도해 주세요.", "WARN");
                } else {
                    addSystemLog("평가 시스템 일시 장애. 관리자에게 문의해 주세요.", "ERROR");
                }
                return;
            }

            // 평가 결과 반영
            Object.assign(evaluationResult, {
                finalScore:          result.score,
                overall_score:       result.score,
                total_score_100:     result.score,
                dimensions:          result.dimensions,
                feedback:            result.oneLineReview,
                strengths:           result.strengths,
                weaknesses:          result.weaknesses,
                tail_question:       result.tailQuestion,
                deep_dive:           result.deepDive,
                converted_python:    result.convertedPython,
                one_line_review:     result.oneLineReview,
                persona_name:        result.persona,
                is_low_effort:       result.isLowEffort,
                supplementaryVideos: [],
            });

            // low_effort → 모달 띄우고 멈춤 (confirmLowEffortProceed에서 재개)
            if (result.isLowEffort) {
                lowEffortReason.value = result.oneLineReview;
                showLowEffortModal.value = true;
                return;
            }

            setPhase('PYTHON_VISUALIZATION');
        } catch (error) {
            console.error(error);
            addSystemLog("평가 시스템 일시 장애", "ERROR");
        } finally {
            isProcessing.value = false;
        }
    };

    const handleReSubmitPseudo = submitPseudo;

    const retryDesign = () => {
        setPhase('PSEUDO_WRITE');
        addSystemLog("설계 보완 모드 활성화", "INFO");
    };

    /**
     * Python 시각화 단계에서 '다음(DEEP DIVE 진입)' 클릭 시
     */
    const handlePythonVisualizationNext = () => {
        // [2026-02-14 수정] 무성의 입력 복구 모드(is_low_effort)인 경우 MCQ 답변 체크 우회
        if (!gameState.isMcqAnswered && !evaluationResult.is_low_effort) {
            addSystemLog("아키텍처 결함 보완 문제를 먼저 완료해주세요.", "WARN");
            return;
        }

        // 현재 서술형 Deep Dive 단계라면 최종 리포트로 이동
        if (gameState.phase === 'DEEP_DIVE_DESCRIPTIVE') {
            setPhase('EVALUATION');
            addSystemLog("모든 설계 검증이 완료되었습니다. 리포트를 생성합니다.", "SUCCESS");
            return;
        }

        // 3대 실무 시나리오 중 하나 랜덤 할당 (이미 할당되지 않은 경우)
        if (!gameState.assignedScenario) {
            const scenarios = currentMission.value?.deepDiveScenarios || [];
            if (scenarios.length > 0) {
                // 무작위 추출
                gameState.assignedScenario = scenarios[Math.floor(Math.random() * scenarios.length)];
            }
        }

        // 서술형 Deep Dive 페이즈로 전환
        setPhase('DEEP_DIVE_DESCRIPTIVE');
        addSystemLog(`[실무 챌린지] ${gameState.assignedScenario?.title} 시나리오가 제시되었습니다.`, "INFO");
    };

    /**
     * MCQ 답변 처리 (Tail Question / Deep Quiz 공용)
     */
    const handleMcqAnswer = async (idx) => {
        const question = deepQuizQuestion.value;
        if (!question || !question.options) {
            console.error("MCQ Question data is missing.");
            return;
        }

        const selected = question.options[idx];
        gameState.isMcqAnswered = true; // 답변 완료 기록

        if (selected.is_correct || selected.correct) {
            gameState.score += 150;
            gameState.coduckMessage = selected.feedback || '설계 결함이 성공적으로 보완되었습니다.';
            addSystemLog("탁월한 판단입니다! 설계 결함이 성공적으로 보완되었습니다.", "SUCCESS");
        } else {
            handleDamage(15);
            gameState.coduckMessage = `오답입니다: ${selected.feedback || '아키텍처 무결성이 손상되었습니다.'}`;
            addSystemLog("판단 오류입니다. 아키텍처 무결성이 손상되었습니다.", "WARN");
        }
    };

    /**
     * 최종 실무 시나리오(서술형) 제출 처리
     */
    const submitDescriptiveDeepDive = async (userAnswer) => {
        if (!userAnswer.trim() || isProcessing.value) return;

        try {
            isProcessing.value = true;
            gameState.deepDiveAnswer = userAnswer;

            addSystemLog("최종 실무 시나리오 설계 분석 중...", "INFO");

            // [2026-02-14 추가] 무성의 입력(Low Effort) 복구 수련 완료 시 점수 대폭 보정
            if (evaluationResult.is_low_effort) {
                evaluationResult.overall_score = 75; // 0점 -> 75점으로 복구
                evaluationResult.total_score_100 = 75;
                evaluationResult.persona_name = "각성한 설계 지망생";
                evaluationResult.one_line_review = "부족함을 인정하고 끝까지 아키텍처를 복구해낸 끈기가 돋보입니다.";

                // 각 차원 점수도 '복구됨'으로 업데이트 (방사형 차트 반영용)
                const dims = evaluationResult.dimensions;
                Object.keys(dims).forEach(key => {
                    dims[key].score = 7; // 10점 만점에 7점 수준으로 복구
                    dims[key].basis = "학습을 통한 설계 복구 성공";
                    dims[key].improvement = "앞으로도 이 설계 원칙을 잊지 마세요.";
                });
            }

            // [2026-02-19] 즉시 평가로 넘어가지 않고 UI에서 모범 답안을 보여주도록 변경
            addSystemLog("서술형 설계가 기록되었습니다. 모범 답안을 확인해 보세요.", "INFO");
        } catch (error) {
            console.error(error);
        } finally {
            isProcessing.value = false;
        }
    }

    const submitDeepQuiz = async (answer) => {
        if (answer.is_correct) {
            gameState.score += 150;
            addSystemLog("심화 퀴즈 정답! 시스템 코어가 강화되었습니다.", "SUCCESS");
        } else {
            handleDamage(15);
            addSystemLog("오답입니다. 아키텍처 결함이 탐지되었습니다.", "WARN");
        }
        setPhase('EVALUATION');
    };

    const handleTailSelection = (option) => {
        if (option.is_correct) {
            gameState.score += 100;
            addSystemLog("약점 보완 완료!", "SUCCESS");
            setPhase('DEEP_QUIZ');
        } else {
            handleDamage(10);
            addSystemLog("추가 질문 오답 - 재적응 훈련이 필요합니다.", "WARN");
            retryDesign();
        }
    };

    /**
     * MCQ 오답 시 재시도
     */
    const retryMcq = () => {
        gameState.isMcqAnswered = false;
        addSystemLog("설계 결함 보완 재시도 모드 활성화", "INFO");
    };

    const deepQuizQuestion = computed(() => {
        const aiTq = evaluationResult.tail_question;
        const aiDq = evaluationResult.deep_dive;

        // 시각화 단계(PYTHON_VISUALIZATION)나 꼬리 질문 단계에서 데이터 반환
        if (['PYTHON_VISUALIZATION', 'TAIL_QUESTION', 'DEEP_DIVE_DESCRIPTIVE'].includes(gameState.phase)) {
            return aiTq || aiDq || null;
        }
        if (gameState.phase === 'DEEP_QUIZ' && aiDq) return aiDq;
        return null;
    });

    return {
        gameState,
        enemyThreat,
        currentMission,
        evaluationResult,
        addSystemLog,
        missionContext,
        constraints,
        diagnosticQuestion,
        deepQuizQuestion,
        isEvaluating,
        startGame,
        selectStage,
        submitPseudo,
        submitDiagnostic,
        submitDeepQuiz,
        retryDesign,
        nextMission,
        restartMission,
        userCode: computed(() => runnerState.userCode),
        runnerState,
        codeSlots: computed(() => runnerState.codeSlots),
        codeExecutionResult: computed(() => runnerState.executionResult),
        insertSnippet,
        handleSlotDrop,
        submitPythonFill: () => submitPythonFill(gameState.phase3Reasoning, handleDamage),
        initPhase4Scaffolding,
        ruleChecklist,
        completedChecksCount,
        allChecksPassed,
        canSubmitPseudo,
        isProcessing,
        isGuideOpen,
        selectedGuideIdx,
        showModelAnswer,
        toggleGuide,
        handleGuideClick,
        showHintDuck,
        dynamicHintMessage,
        toggleHintDuck,
        toggleHint,
        handlePythonVisualizationNext,
        showLowEffortModal,
        lowEffortReason,
        confirmLowEffortProceed,
        handleTailSelection,
        handleMcqAnswer,
        submitDescriptiveDeepDive,
        handleReSubmitPseudo,
        retryMcq,
        resetFlow: engineResetFlow,
        resetHintTimer,
        handlePracticeClose: () => router.push('/practice')
    };
}
