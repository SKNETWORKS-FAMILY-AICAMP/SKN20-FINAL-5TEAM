/**
 * useCoduckWars.js - Refactored (Restored and Fixed)
 * 
 * [2026-02-18] pseudo_tts 브랜치와 프론트엔드 UI 및 로직 완전 동기화 (한글 인코딩 복구 포함)
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
import { evaluatePseudocode5D, evaluateDiagnosticAnswer } from '../api/pseudocodeApi.js';
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

    // UI State
    const isGuideOpen = ref(false);
    const selectedGuideIdx = ref(0);
    const showModelAnswer = ref(false);
    const isEvaluating = ref(false); // [NEW] 평가 중 상태

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
    const ruleChecklist = ref([
        {
            id: 'check_isolation',
            label: '격리 (Isolation) 포함',
            patterns: [/격리|분리|나누|나눔|isolation|split/i],
            hint: "데이터를 나누는 '격리' 개념이 포함되어야 합니다.",
            completed: false
        },
        {
            id: 'check_anchor',
            label: '기준점 (Anchor) 정의',
            patterns: [/기준점|기준|통계량|fit|anchor|학습/i],
            hint: "통계량을 추출할 대상인 '기준점'이 명시되어야 합니다.",
            completed: false
        },
        {
            id: 'check_consistency',
            label: '일관성 (Consistency) 확보',
            patterns: [/일관성|동일|변환|consistency|transform/i],
            hint: "학습과 운영 환경의 '일관성' 있는 변환 방식이 포함되어야 합니다.",
            completed: false
        }
    ]);

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
        const HINT_DATA = {
            surrender: {
                title: "🐣 [복기 학습 제안]",
                pool: ["설계가 막막하신가요? [심화 분석 시작]을 눌러 청사진을 확인해보세요."]
            },
            isolation: {
                title: "🐣 [격리 유도]",
                pool: ["데이터 분할 시점이 적절한지 다시 한번 생각해보세요."]
            },
            anchor: {
                title: "🐣 [기준점 교정 힌트]",
                pool: ["정답지(Test)가 기준점 설정에 포함되지는 않았나요?"]
            },
            consistency: {
                title: "🐣 [일관성 강조 힌트]",
                pool: ["학습 때 썼던 동일한 변환 방식을 테스트에도 적용했나요?"]
            },
            abstraction: {
                title: "🐣 [구조화 독려 힌트]",
                pool: ["설계의 인과관계가 잘 드러나도록 문장을 다듬어보세요."]
            }
        };

        const setHint = (typeKey) => {
            const entry = HINT_DATA[typeKey];
            if (!entry) return;
            const randomSentence = entry.pool[Math.floor(Math.random() * entry.pool.length)];
            dynamicHintMessage.value = `${entry.title}\n\n${randomSentence}`;
        };

        const surrenderKeywords = /잘\s*모르겠다|모름|몰라|어렵다|어려워|포기|힘들어/i;
        if (surrenderKeywords.test(code) || (code.trim().length > 0 && code.trim().length < 5)) {
            setHint('surrender');
            return;
        }

        const isolationKeywords = /split|분할|나누기|쪼개기|격리/i;
        if (!isolationKeywords.test(code)) {
            setHint('isolation');
            return;
        }

        const anchorError = /fit\s*\(\s*(total|all|df|전체|테스트|test)/i.test(code);
        if (anchorError) {
            setHint('anchor');
            return;
        }

        const consistencyKeywords = /transform|변환|적용|동일하게|똑같이/i;
        if (!consistencyKeywords.test(code)) {
            setHint('consistency');
            return;
        }

        if (code.replace(/\s/g, '').length < 40) {
            setHint('abstraction');
            return;
        }

        dynamicHintMessage.value = "🐣 [설계 완료]\n\n완벽에 가까운 설계입니다! 승인을 요청해 보세요.";
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

        try {
            gameState.feedbackMessage = "분석 중...";
            const diagnosticContext = {
                answers: [gameState.diagnosticAnswer],
                scores: gameState.diagnosticScores
            };

            const evaluation = await evaluatePseudocode5D(currentMission.value, gameState.phase3Reasoning, diagnosticContext);
            Object.assign(evaluationResult, evaluation);
            evaluationResult.finalScore = evaluation.overall_score;
            // [2026-02-14] UI 호환성을 위해 추천 영상 매핑
            evaluationResult.supplementaryVideos = evaluation.recommended_videos || [];

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

            setPhase('EVALUATION');
        } catch (error) {
            console.error(error);
            setPhase('EVALUATION');
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
        handleTailSelection,
        handleMcqAnswer,
        submitDescriptiveDeepDive,
        handleReSubmitPseudo,
        resetFlow: engineResetFlow,
        resetHintTimer,
        handlePracticeClose: () => router.push('/practice')
    };
}
