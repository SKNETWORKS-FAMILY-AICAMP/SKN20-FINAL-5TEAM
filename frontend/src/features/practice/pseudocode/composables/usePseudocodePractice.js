/**
 * usePseudocodePractice.js - Refactored (Restored and Fixed)
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
import { useStageEngine } from './useStageEngine.js';
import { useCodeRunner } from './useCodeRunner.js';

export function usePseudocodePractice() {
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
    } = useStageEngine();

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

    const fallbackChecklistPatterns = {
        check_isolation: [/격리|분리|isolation|split/i],
        check_anchor: [/기준점|기준|fit|anchor/i],
        check_consistency: [/일관성|동일|변환|consistency|transform/i],
        check_control: [/복잡도|제어|정규화|l1|l2|ridge|lasso|depth/i],
        check_selection: [/특성|선택|제거|selection|feature/i],
        check_monitoring: [/성능|모니터링|추적|accuracy|score|monitoring/i],
        check_diagnosis: [/불균형|진단|분포|detect|imbalance/i],
        check_sampling: [/샘플링|smote|오버|언더|sampling|balance/i],
        check_evaluation: [/평가|지표|f1|auc|precision|recall|metric|fair/i],
        check_creation: [/창조|생성|파생|creation/i],
        check_transformation: [/변환|스케일링|정규화|transformation|scaling/i],
        check_feature_selection: [/선택|중요도|제거|selection/i],
        check_space: [/공간|범위|정의|param|space/i],
        check_search: [/탐색|전략|그리드|랜덤|search|strategy/i],
        check_cv: [/교차검증|k-fold|cv|valid/i],
        check_global: [/전역|해석|global/i],
        check_local: [/개별|해석|shap|lime|local/i],
        check_fairness: [/공정|검증|편향|fair|bias/i]
    };

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

    // [수정일: 2026-02-24] DB에서 로드된 checklist.patterns가 JSON 직렬화 시 RegExp가 {} 로 변환되어 TypeError를 발생시키는 문제 해결
    // fallbackChecklistPatterns 로컬 패턴을 우선 사용하고, RegExp 인스턴스 또는 문자열 패턴만 안전하게 처리하도록 복구
    watch(() => gameState.phase3Reasoning, (newCode) => {
        try {
            ruleChecklist.value.forEach(check => {
                // fallbackChecklistPatterns에 정의된 패턴이 있으면 우선 사용
                const patternsToUse = fallbackChecklistPatterns[check.id] || check.patterns;

                if (!Array.isArray(patternsToUse) || patternsToUse.length === 0) {
                    return; // patterns가 없으면 completed 상태 유지
                }

                check.completed = patternsToUse.some(p => {
                    if (p instanceof RegExp) return p.test(newCode);
                    if (typeof p === 'string' && p.length > 0) return new RegExp(p, 'i').test(newCode);
                    return false; // {} 등 잘못된 형식은 무시
                });
            });
        } catch (e) {
            console.warn('[usePseudocodePractice] ruleChecklist watcher error:', e);
        }
        if (showHintDuck.value) updateDynamicHint();
    });

    watch(() => gameState.phase, (newPhase) => {
        showHintDuck.value = false;
        gameState.showHint = false;
        if (newPhase === 'PYTHON_VISUALIZATION' || newPhase === 'PSEUDO_WRITE') {
            initPhase4Scaffolding();
        }
    });

    // [2026-02-22] 복구 성공 여부 추적 (재평가 시 오염 방지용 마스터 키)
    const isRecovered = ref(false);

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
        senior_advice: "",   // AI ARCHITECT ADVICE에 표시할 GPT 맞춤 코멘트
        persona_name: "Senior Architect",
        details: [],
        supplementaryVideos: []
    });

    const submitPseudo = async () => {
        if (isProcessing.value || !canSubmitPseudo.value) return;
        isProcessing.value = true;
        await runEvaluationProcess();
    };

    // [2026-02-19] 무성의 입력 경고 후 강제 진행 처리
    const confirmLowEffortProceed = async (choice) => {
        showLowEffortModal.value = false;

        if (choice === 'RECONSTRUCT') {
            // [2026-02-22 Fix] '기초부터 배우기' 선택 시 백엔드 재호출 없이 즉시 시각화(복구 작전) 단계로 진입
            // 이미 evaluationResult에 blueprintSteps가 포함되어 내려왔으므로 바로 전환 가능
            setPhase('PYTHON_VISUALIZATION'); // Changed from currentPhase.value = GAME_PHASES.PYTHON_VISUALIZATION;
            return;
        }

        // '직접 보완하기'는 기존 로직 유지 (재평가 프로세스 실행)
        // isProcessing.value는 runEvaluationProcess 내부에서 처리
        await runEvaluationProcess(); // Removed currentPseudocode.value as it's not a valid argument for the first position
    };

    // 공통 평가 프로세스 분리
    // tailAnswer, deepAnswer: 최초 제출 시엔 빈 문자열, Deep Dive 제출 후 재평가 시엔 실제 답변 전달
    const runEvaluationProcess = async (tailAnswer = '', deepAnswer = '') => {
        try {
            isProcessing.value = true; // Moved here from confirmLowEffortProceed
            gameState.feedbackMessage = "분석 중...";

            const result = await evaluate(
                currentMission.value,
                gameState.phase3Reasoning,
                tailAnswer,
                deepAnswer,
            );

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
                finalScore: result.score,
                overall_score: result.score,
                total_score_100: result.score,
                dimensions: result.dimensions,
                feedback: result.oneLineReview,
                strengths: result.strengths,
                weaknesses: result.weaknesses,
                tail_question: result.tailQuestion,
                deep_dive: result.deepDive,
                converted_python: result.convertedPython,
                one_line_review: result.oneLineReview,
                senior_advice: result.seniorAdvice,
                persona_name: result.persona,
                is_low_effort: result.isLowEffort,
                recommended_videos: result.recommendedVideos || [],  // 백엔드 큐레이션 (2026-02-23 확인)
                blueprint_steps: result.blueprintSteps || [],       // [2026-02-22] 청사진 복구용
                supplementaryVideos: [],  // EVALUATION 단계에서 세팅
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

    // [2026-02-22] 복구 모드 결과 반영 통합 함수
    // 점수만 60점을 주는 것이 아니라, 청사진 학습자가 '실제로 부족한 부분'을 오각형에 정직하게 반영
    const applyRecoveryResult = (score, isCorrect = true, isFinal = false) => {
        isRecovered.value = true;

        evaluationResult.strengths = [];
        evaluationResult.weaknesses = [];
        evaluationResult.details = [];
        evaluationResult.overall_score = score;
        evaluationResult.total_score_100 = score;
        evaluationResult.finalScore = score;
        evaluationResult.is_low_effort = false;

        // 점수대별 페르소나 (청사진 의존도 반영)
        if (score >= 80) {
            evaluationResult.persona_name = "미래를 설계하는 아키텍트";
        } else if (score >= 70) {
            evaluationResult.persona_name = "준비된 설계 전략가";
        } else {
            evaluationResult.persona_name = "성장하는 주니어 아키텍트";
        }

        if (!isFinal) {
            evaluationResult.one_line_review = "청사진을 통해 아키텍처의 핵심 구조를 복원했습니다.";
            evaluationResult.senior_advice = "구조는 잡혔습니다. 이제 꼬리 질문을 통해 세부 원리를 증명해 보세요.";
        } else {
            evaluationResult.one_line_review = isCorrect
                ? "축하합니다! 이해도 테스트까지 통과하며 시스템 아키텍처를 재건했습니다."
                : "아키텍처 구조는 복구했으나, 세부 원칙에 대한 보완이 조금 더 필요합니다.";
            evaluationResult.senior_advice = isCorrect
                ? "훌륭한 복구 능력입니다. 이제 청사진 없이도 스스로 설계할 수 있도록 연습해 보세요!"
                : "설계 뼈대는 복원했지만, 복잡한 예외 상황에 대한 스스로의 고민이 더 필요합니다.";
        }

        const ratio = score / 100;
        const metrics = {
            abstraction: Math.round(85 * ratio),
            consistency: Math.round(80 * ratio),
            implementation: Math.round(70 * ratio),
            design: Math.round(50 * ratio),
            edgeCase: Math.round(45 * ratio),
        };

        evaluationResult.dimensions = {
            design: { score: Math.round(metrics.design * 0.25), max: 25, percentage: metrics.design, comment: "청사진 의존도가 높아 독창적 설계 의도가 부족합니다." },
            consistency: { score: Math.round(metrics.consistency * 0.20), max: 20, percentage: metrics.consistency, comment: "청사진의 논리적 일관성을 잘 수용했습니다." },
            abstraction: { score: Math.round(metrics.abstraction * 0.15), max: 15, percentage: metrics.abstraction, comment: "아키텍처의 핵심 추상화 구조를 복원했습니다." },
            edgeCase: { score: Math.round(metrics.edgeCase * 0.15), max: 15, percentage: metrics.edgeCase, comment: "다양한 예외 상황에 대한 자가 대응력이 부족합니다." },
            implementation: { score: Math.round(metrics.implementation * 0.10), max: 10, percentage: metrics.implementation, comment: "제공된 가이드를 충실히 구현에 반영했습니다." }
        };
    };

    // [2026-02-22] 청사진 복구 완료 처리 (기본 점수 부여)
    const handleBlueprintComplete = (mode) => {
        // [2026-02-23 수정] 60점 고정 탈피: 60~64점 사이의 변동성 부여
        const variance = Math.floor(Math.random() * 5);
        const baseScore = mode === 'keyword' ? (70 + variance) : (60 + variance);
        applyRecoveryResult(baseScore, true, false); // <--- isFinal: false (중간 단계)

        // senior_advice만 잠시 꼬리질문 유도형으로 변경
        evaluationResult.senior_advice = "청사진 학습을 완료하셨습니다. 이제 아래의 꼬리 질문을 통해 이해도를 최종 점검해 보세요!";
        evaluationResult.is_low_effort = true;

        handlePythonVisualizationNext();
        addSystemLog(`청사진 복구 성공! 이해도 확인을 위한 꼬리 질문 단계로 진입합니다.`, "SUCCESS");
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
        gameState.isMcqAnswered = true;
        // 꼬리질문 선택 텍스트 저장 → Deep Dive 제출 후 재평가 시 백엔드에 전달됨
        gameState.tailAnswer = selected.text || '';

        if (selected.is_correct || selected.correct) {
            // [2026-02-22] 청사진 모드(Recovery)에서 정답 시 점수 추가 가산
            if (evaluationResult.is_low_effort) {
                const bonusScore = (evaluationResult.overall_score || 0) + 10;
                applyRecoveryResult(bonusScore, true, true); // <--- isFinal: true
                addSystemLog(`이해도 테스트 통과! 최종 점수 ${bonusScore}점이 확정되었습니다.`, "SUCCESS");
                setTimeout(() => setPhase('EVALUATION'), 1500);
                return;
            }

            gameState.score += 150;
            gameState.coduckMessage = selected.feedback || '설계 결함이 성공적으로 보완되었습니다.';
            addSystemLog("탁월한 판단입니다! 설계 결함이 성공적으로 보완되었습니다.", "SUCCESS");
        } else {
            handleDamage(15);
            gameState.coduckMessage = `오답입니다: ${selected.feedback || '아키텍처 무결성이 손상되었습니다.'}`;
            addSystemLog("판단 오류입니다. 아키텍처 무결성이 손상되었습니다.", "WARN");

            // [2026-02-22] 청사진 모드에서 오답 시에도 리포트 이동 (점수 가산 없음)
            if (evaluationResult.is_low_effort) {
                applyRecoveryResult(evaluationResult.overall_score, false, true); // <--- isFinal: true
                setTimeout(() => setPhase('EVALUATION'), 1500);
            }
        }
    };

    /**
     * Deep Dive 서술형 제출 → 백엔드 종합 재평가 → EVALUATION 페이즈 전환
     * pseudocode + tail_answer(꼬리질문 선택) + deep_answer(서술형) 3개 모두 전달
     * [2026-02-22 Fix] 재평가 완료 후 setPhase('EVALUATION') 추가
     * [2026-02-22 Fix] tail_question/deep_dive 필드 보존 (덮어쓰지 않음)
     */
    const submitDescriptiveDeepDive = async (userAnswer) => {
        if (!userAnswer.trim() || isProcessing.value) return;

        try {
            isProcessing.value = true;
            gameState.deepDiveAnswer = userAnswer;
            addSystemLog("서술형 답변 포함 종합 재평가 중...", "INFO");

            const tailAnswer = gameState.tailAnswer || '';

            const result = await evaluate(
                currentMission.value,
                gameState.phase3Reasoning,
                tailAnswer,
                userAnswer,
            );

            if (!result) {
                addSystemLog("재평가 실패. 최종 리포트로 이동합니다.", "WARN");
                // 재평가 실패해도 EVALUATION으로 전환 (기존 점수 유지)
                setPhase('EVALUATION');
                return;
            }

            // [2026-02-22 Fix] MASTER GUARD: 복구 완료 상태(isRecovered)이면 백엔드 오염 원천 차단
            if (isRecovered.value || (result.isLowEffort && (evaluationResult.overall_score || 0) >= 60)) {
                console.log('[MASTER GUARD] 복구된 데이터를 감지했습니다. 백엔드의 저의도 응답에 의한 오염을 차단하고 리포트로 직행합니다.');
                setPhase('EVALUATION');
                return;
            }

            // [2026-02-21] 점수 하락 방지: max(기존 복구 점수, 새 평가 점수)
            const previousScore = evaluationResult.overall_score || 0;
            const finalScore = Math.max(previousScore, result.score || 0);

            Object.assign(evaluationResult, {
                finalScore: finalScore,
                overall_score: finalScore,
                total_score_100: finalScore,
                dimensions: result.dimensions || evaluationResult.dimensions,
                persona_name: result.persona || evaluationResult.persona_name,
                one_line_review: result.oneLineReview || evaluationResult.one_line_review,
                senior_advice: result.seniorAdvice || evaluationResult.senior_advice,
                strengths: result.strengths || evaluationResult.strengths,
                weaknesses: result.weaknesses || evaluationResult.weaknesses,
                converted_python: result.convertedPython || evaluationResult.converted_python,
                is_low_effort: false,
                recommended_videos: result.recommendedVideos || evaluationResult.recommended_videos || [],
            });

            addSystemLog(`종합 재평가 완료: ${finalScore}점`, "SUCCESS");

            // [2026-02-22 Fix] 반드시 EVALUATION으로 전환
            setPhase('EVALUATION');
        } catch (error) {
            console.error('[submitDescriptiveDeepDive] Error:', error);
            addSystemLog("재평가 중 오류가 발생했습니다. 최종 리포트로 이동합니다.", "ERROR");
            // 에러가 나도 EVALUATION으로 전환
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
        handleBlueprintComplete,
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
