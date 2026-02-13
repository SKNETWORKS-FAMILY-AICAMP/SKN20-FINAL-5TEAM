/**
 * useCoduckWars.js - Refactored
 * 
 * 개선 사항:
 * - 5차원 메트릭 기반 평가 적용
 * - Tail Question 분기 로직 추가
 * - AI 멘토 코칭 생성
 * 
 * [2026-02-12] 전면 개편
 */

import { ref, computed, reactive, watch } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { evaluatePseudocode5D, generateSeniorAdvice, evaluateDiagnosticAnswer } from '../api/pseudocodeApi.js';
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
        selectStage
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
    const showModelAnswer = ref(false); // [NEW] 모범 답안 노출 여부
    const toggleGuide = () => { isGuideOpen.value = !isGuideOpen.value; };
    const handleGuideClick = (idx) => { selectedGuideIdx.value = idx; };

    // [2026-02-12] INTRO 단계 제거로 인한 startMission 삭제

    // Checklist (규칙 기반 실시간 피드백)
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

    // Hint Timer
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

    // [2026-02-12] 에디터 내용 변경 시 실시간 체크리스트 업데이트 (Monaco 전용)
    watch(() => gameState.phase3Reasoning, (val) => {
        if (!val) return;
        if (ruleChecklist.value && Array.isArray(ruleChecklist.value)) {
            ruleChecklist.value.forEach(check => {
                if (check && Array.isArray(check.patterns)) {
                    check.completed = check.patterns.some(pattern => {
                        if (pattern instanceof RegExp) {
                            return pattern.test(val);
                        }
                        return false;
                    });
                }
            });
        }
        resetHintTimer();
    });

    // [2026-02-13] 설계 단계 진입 시 힌트 타이머 즉시 기동
    watch(() => gameState.phase, (newPhase) => {
        if (newPhase === 'PSEUDO_WRITE') {
            startHintTimer();
        }
    });

    // --- Diagnostic Logic ---
    // [2026-02-12] 현재 진행 중인 진담 문항 통합 접근
    const diagnosticQuestion = computed(() => {
        const q = currentMission.value.interviewQuestions?.[gameState.diagnosticStep || 0];
        return q || { type: 'CHOICE', question: '로딩 중...', options: [] };
    });

    const submitDiagnostic = async (optionIndex) => {
        const q = diagnosticQuestion.value;

        // [2026-02-12] 서술형(DESCRIPTIVE) 타입 처리
        if (q.type === 'DESCRIPTIVE') {
            if (gameState.diagnosticResult && !gameState.isEvaluatingDiagnostic) {
                setPhase('PSEUDO_WRITE');
                gameState.step = 2; // Step 2 is Pseudocode
                return;
            }

            if (!gameState.diagnosticAnswer || gameState.diagnosticAnswer.trim().length < 5) {
                gameState.feedbackMessage = "분석 내용을 조금 더 자세히 적어주세요 (최소 5자).";
                addSystemLog("입력 부족: 분석 내용이 너무 짧습니다.", "WARN");
                return;
            }

            gameState.isEvaluatingDiagnostic = true;
            gameState.feedbackMessage = "AI 아키텍트가 분석 내용을 검토하고 있습니다...";
            addSystemLog("진단 1단계 AI 정밀 분석 개시...", "INFO");

            try {
                const result = await evaluateDiagnosticAnswer(q, gameState.diagnosticAnswer);
                gameState.diagnosticResult = result;
                gameState.diagnosticScores.push(result.score);
                // [2026-02-13] gameState.score 직접 가산 제거 (가중치 기반 자동 계산)
                updateFinalScore();

                if (result.is_correct) {
                    gameState.feedbackMessage = "분석이 완료되었습니다. 다음 단계로 진행하세요.";
                    addSystemLog("진단 성공: 핵심 패턴 파악 완료", "SUCCESS");
                } else {
                    gameState.feedbackMessage = "일부 누락된 관점이 있습니다. 분석을 확인해 보세요.";
                    addSystemLog("진단 미흡: 추론 보완 필요", "WARN");
                }
                gameState.isEvaluatingDiagnostic = false;
            } catch (error) {
                console.error("Diagnostic 1 Evaluation Fail:", error);
                gameState.isEvaluatingDiagnostic = false;
                setPhase('PSEUDO_WRITE');
                gameState.step = 2;
            }
            return;
        }

        // [2026-02-12] 선택형(CHOICE) 타입 처리
        if (q.type === 'CHOICE') {
            if (optionIndex === undefined || !q.options[optionIndex]) return;
            const selected = q.options[optionIndex];
            if (selected.correct) {
                gameState.diagnosticScores.push(100);
                // [2026-02-13] gameState.score 직접 가산 제거
                updateFinalScore();
                gameState.feedbackMessage = "진단 완료! 설계 단계로 진입합니다.";
                addSystemLog("진단 완료: 설계 단계 이동", "SUCCESS");
                setTimeout(() => {
                    // [2026-02-13] 다음 문항이 있는지 확인
                    const nextStep = gameState.diagnosticStep + 1;
                    if (currentMission.value.interviewQuestions?.[nextStep]) {
                        gameState.diagnosticStep = nextStep;
                        gameState.feedbackMessage = null;
                        addSystemLog(`다음 문항 진행: ${nextStep + 1}번`, "INFO");
                    } else {
                        setPhase('PSEUDO_WRITE');
                        gameState.step = 2;
                    }
                }, 1000);
            } else {
                handleDamage();
                gameState.feedbackMessage = selected.feedback || "잘못된 분석입니다. 다시 시도하세요.";
                addSystemLog("오류: 잘못된 판단입니다", "ERROR");
            }
            return;
        }
    };

    /**
     * ✅ 핵심 개선: 5차원 메트릭 기반 평가
     * [2026-02-12] Bug Fix: 모든 경로에서 phase 전환 보장
     */
    const submitPseudo = async () => {
        if (isProcessing.value) {
            console.warn('[submitPseudo] Request already in progress');
            return;
        }

        if (!gameState.phase3Reasoning.trim()) {
            gameState.feedbackMessage = "의사코드를 작성해주세요.";
            return;
        }

        isProcessing.value = true;

        // ✅ [FIX] 안전 타임아웃 - 30초 후 강제 해제
        const safetyTimeout = setTimeout(() => {
            console.error('[submitPseudo] Safety timeout triggered - forcing phase transition');
            isProcessing.value = false;
            gameState.feedbackMessage = "평가 시간 초과. 다음 단계로 진행합니다.";
            // [2026-02-13] gameState.score 직접 가산 제거
            addSystemLog("평가 시간 초과 - 기본 점수 부여", "WARN");
            setPhase('DEEP_QUIZ');
        }, 30000);

        try {
            gameState.feedbackMessage = "AI 아키텍트가 5차원 메트릭으로 분석 중...";
            addSystemLog("5차원 메트릭 평가 시작...", "INFO");

            console.log('[submitPseudo] Calling evaluatePseudocode5D...');
            console.log('[submitPseudo] Mission:', currentMission.value?.id);
            console.log('[submitPseudo] Pseudocode:', gameState.phase3Reasoning.substring(0, 100));

            // ✅ [2026-02-13] 통합된 진단 데이터 기반으로 컨텍스트 구성 (레거시 변수 제거)
            const diagnosticContext = {
                answers: [gameState.diagnosticAnswer],
                scores: gameState.diagnosticScores
            };

            // ✅ 새로운 5차원 평가 API 호출
            const evaluation = await evaluatePseudocode5D(
                currentMission.value,
                gameState.phase3Reasoning,
                diagnosticContext
            );

            console.log('[submitPseudo] Evaluation result:', evaluation);

            // ✅ [FIX] evaluation 유효성 검사
            if (!evaluation || typeof evaluation !== 'object') {
                console.error('[submitPseudo] Invalid evaluation result received:', evaluation);
                throw new Error('Invalid evaluation result');
            }

            // 평가 결과 저장
            gameState.phase3EvaluationResult = evaluation;
            gameState.phase3Score = evaluation.overall_score || 0; // [2026-02-13] 총점 합산을 위해 필수 저장
            updateFinalScore();

            // ✅ Python 변환 결과 저장 (Visualizer용)
            // evaluationResult는 reactive 객체이므로 직접 속성 할당 가능
            if (evaluation.converted_python) {
                evaluationResult.converted_python = evaluation.converted_python;
            }
            if (evaluation.python_feedback) {
                evaluationResult.python_feedback = evaluation.python_feedback;
            }
            if (evaluation.tail_question) {
                evaluationResult.tailQuestion = evaluation.tail_question;
            }
            evaluationResult.overall_score = evaluation.overall_score || 0;

            // ✅ [FIX] dimensions null-safe 접근
            const dims = evaluation.dimensions || {};

            // 5차원 점수별 로그 출력 (null-safe)
            const dimKeys = ['coherence', 'abstraction', 'exception_handling', 'implementation', 'architecture'];
            const dimLabels = ['정합성', '추상화', '예외처리', '구현력', '설계력'];

            dimKeys.forEach((key, i) => {
                const dim = dims[key];
                if (dim) {
                    // [2026-02-13] API에서 이미 12점 스케일링이 되었을 수 있으므로 100점으로 복구하여 저장
                    // api.js에서 dim.score = (dim.score / 100) * 12 를 수행함.
                    // UI와 일관성을 위해 여기서는 100점 만점 원본 점수를 사용하거나 역산함.
                    const displayScore = dim.original_score || (dim.score * 100 / 12);
                    addSystemLog(`${dimLabels[i]}: ${Math.round(displayScore)}점 - ${dim.basis || '분석 완료'}`, "INFO");
                }
            });

            // ✅ 5차원 평균 점수 기반 피드백
            const dimScores = Object.values(dims)
                .filter(d => d && typeof d.score === 'number')
                .map(d => d.score);

            const avgDimScore = dimScores.length > 0
                ? dimScores.reduce((sum, s) => sum + s, 0) / dimScores.length
                : evaluation.overall_score || 0;

            gameState.feedbackMessage = `5차원 평균: ${Math.round(avgDimScore)}점 | 종합: ${evaluation.overall_score || 0}점`;

            // [2026-02-13] gameState.score 직접 가산 제거 (Phase 3 점수는 gameState.phase3Score에 보관)
            addSystemLog(`아키텍처 평가 완료: ${evaluation.overall_score || 0}점`, "SUCCESS");

            // ✅ 강점/약점 요약
            if (evaluation.strengths && evaluation.strengths.length > 0) {
                addSystemLog(`강점: ${evaluation.strengths[0]}`, "SUCCESS");
            }
            if (evaluation.weaknesses && evaluation.weaknesses.length > 0) {
                addSystemLog(`약점: ${evaluation.weaknesses[0]}`, "WARN");
            }

            // ✅ AI 결정에 따라 다음 단계 분기
            addSystemLog("분석 완료. 2초 후 다음 단계로 이동합니다.", "INFO");
            await new Promise(resolve => setTimeout(resolve, 2000));

            // [STEP 3] Python 시각화 단계로 이동
            addSystemLog("분석 완료. Python 변환 결과를 확인하세요.", "SUCCESS");
            setPhase('PYTHON_VISUALIZATION');



        } catch (error) {
            console.error('[submitPseudo] Error:', error);
            console.error('[submitPseudo] Error stack:', error.stack);

            // ✅ [FIX] 에러 발생해도 반드시 다음 단계로 전환
            gameState.feedbackMessage = "평가 중 오류 발생. 다음 단계로 진행합니다.";
            // [2026-02-13] gameState.score 직접 가산 제거

            // ✅ [FIX] 기본 evaluation 결과 생성 (EVALUATION 단계에서 사용)
            if (!gameState.phase3EvaluationResult) {
                const fallbackTail = {
                    question: "작성하신 로직이 설계 요구사항을 충족하는지 다시 한 번 점검이 필요합니다.",
                    options: [
                        { text: "아키텍처를 다시 살펴보겠습니다.", is_correct: true, reason: "꼼꼼한 검증은 필수입니다." },
                        { text: "이대로 결과를 확인하겠습니다.", is_correct: false, reason: "보완이 필요한 부분이 있을 수 있습니다." }
                    ]
                };

                gameState.phase3EvaluationResult = {
                    overall_score: 50,
                    dimensions: {
                        coherence: { score: 50, basis: '평가 오류로 기본 점수', specific_issue: null, improvement: null },
                        abstraction: { score: 45, basis: '평가 오류로 기본 점수', specific_issue: null, improvement: null },
                        exception_handling: { score: 40, basis: '평가 오류로 기본 점수', specific_issue: null, improvement: null },
                        implementation: { score: 55, basis: '평가 오류로 기본 점수', specific_issue: null, improvement: null },
                        architecture: { score: 45, basis: '평가 오류로 기본 점수', specific_issue: null, improvement: null }
                    },
                    strengths: [],
                    weaknesses: ['평가 시스템 오류'],
                    grade: 'fair',
                    tail_question: fallbackTail
                };
                gameState.phase3Score = 50;
                evaluationResult.tailQuestion = fallbackTail;
                evaluationResult.overall_score = 50;
            }

            addSystemLog("평가 시스템 오류, 기본 점수 부여 후 심화 검증으로 이동", "WARN");
            // ✅ 기존: setTimeout(() => setPhase('DEEP_QUIZ'), 800);
            // ✅ 개선: 화면 전환을 막고 듀얼 뷰에서 질문을 보여주기 위해 setPhase 제거
        } finally {
            // ✅ [FIX] 안전 타임아웃 클리어
            clearTimeout(safetyTimeout);
            isProcessing.value = false;
        }
    };

    // --- Deep Quiz & Tail Question ---
    const deepQuizQuestion = computed(() => {
        const isVisualization = gameState.phase === 'PYTHON_VISUALIZATION';
        const isTailQuestion = gameState.phase === 'TAIL_QUESTION';
        const isDeepQuiz = gameState.phase === 'DEEP_QUIZ';
        const rawScore = evaluationResult.overall_score || gameState.phase3Score || 0;
        const score = Number(rawScore);

        // 로깅 추가
        console.log('[deepQuizQuestion DEBUG]', {
            phase: gameState.phase,
            score,
            hasTail: !!evaluationResult.tailQuestion,
            hasDeep: !!currentMission.value?.deepDiveQuestion
        });

        // 1. PYTHON_VISUALIZATION 또는 TAIL_QUESTION 단계 (저득점 보완)
        if ((isVisualization || isTailQuestion) && score < 80) {
            const tq = evaluationResult.tailQuestion;

            // 데이터가 없거나 형식이 잘못된 경우 하드코딩된 폴백 제공
            if (!tq || !tq.question) {
                return {
                    question: "작성하신 의사코드의 전체적인 논리 구조를 다시 한 번 검토해볼까요?",
                    options: [
                        { text: "네, 로직의 선후 관계를 명확히 다듬겠습니다.", is_correct: true, reason: "안정적인 코드 구현을 위해 구조적 탄탄함은 필수입니다." },
                        { text: "현재 로직으로도 충분해 보입니다.", is_correct: false, reason: "보이지 않는 에지 케이스가 있을 수 있습니다." }
                    ]
                };
            }

            return {
                question: tq.question.startsWith('[') ? tq.question : `[추가 보완] ${tq.question}`,
                options: (tq.options || []).map(opt => ({
                    text: opt.text,
                    is_correct: opt.is_correct || opt.correct,
                    reason: opt.reason || '개선이 필요한 지점입니다.'
                }))
            };
        }

        // 2. PYTHON_VISUALIZATION 또는 DEEP_QUIZ 단계 (고득점 심화)
        if ((isVisualization || isDeepQuiz) && score >= 80) {
            const mission = currentMission.value;
            const dq = mission?.deepDiveQuestion;

            if (!dq || !dq.question) {
                // 심화 퀴즈가 없는 미션일 경우의 폴백
                return {
                    question: "완벽한 설계입니다! 이 로직을 더 확장한다면 어떤 점을 고려할까요?",
                    options: [
                        { text: "더 효율적인 시간 복잡도를 고민하겠습니다.", is_correct: true, reason: "최적화는 아키텍트의 다음 목표입니다." },
                        { text: "현재 성능으로 충분히 만족합니다.", is_correct: false, reason: "성능 한계에 부딪힐 수 있습니다." }
                    ]
                };
            }

            return {
                question: dq.question.startsWith('[') ? dq.question : `[심화 챌린지] ${dq.question}`,
                options: dq.options.map(opt => ({
                    text: opt.text,
                    is_correct: opt.is_correct || opt.correct,
                    reason: opt.reason || '심화 개념 확인이 필요합니다.'
                }))
            };
        }

        return null;
    });

    const submitDeepQuiz = (optionIndex) => {
        const questionData = deepQuizQuestion.value;
        const selected = questionData.options[optionIndex];

        if (!selected) return;

        // Tail Question 처리 분기
        if (gameState.phase === 'TAIL_QUESTION') {
            handleTailSelection(selected);
            return;
        }

        // Deep Quiz 처리
        if (selected && selected.is_correct) {
            gameState.iterativeScore = 100;
            // [2026-02-13] gameState.score 직접 가산 제거
            updateFinalScore();
            addSystemLog("심화 검증 통과", "SUCCESS");
            handleVictory();
        } else {
            gameState.iterativeScore = 0;
            handleDamage();
            gameState.feedbackMessage = "개념 오인.";
            addSystemLog("검증 실패: 개념 재확인 필요", "ERROR");
            setTimeout(() => handleVictory(), 1500); // 실패해도 종료
        }
    };

    // [STEP 3] Tail Question 처리 로직 (+5점 보너스)
    const handleTailSelection = (option) => {
        if (!option) return;

        if (option.is_correct) {
            gameState.iterativeScore = 100;
            // [2026-02-13] gameState.score 직접 가산 제거
            updateFinalScore();
            gameState.feedbackMessage = "정확합니다!";
            addSystemLog(`보완 성공: ${option.reason} (+5점)`, "SUCCESS");
        } else {
            gameState.iterativeScore = 0;
            gameState.feedbackMessage = "아쉽습니다. 다음에는 더 꼼꼼히 확인해보세요.";
            addSystemLog(`보완 실패: ${option.reason}`, "WARN");
        }

        // 보너스 문제라 실패해도 데미지 없음. 바로 최종 평가로 이동
        setTimeout(() => {
            handleVictory(); // STEP 4 (EVALUATION)으로 이동
        }, 1500);
    };

    /**
     * [STEP 3] Python 시각화 완료 후 분기 (Deep Dive or Tail Question)
     */
    const handlePythonVisualizationNext = () => {
        // 2026-02-13: 이 함수는 이제 CodeFlowVisualizer 내에서 질문이 없을 때만 호출되거나, 
        // 최종 버튼 클릭 시 handleVictory로 바로 연결되도록 CoduckWars.vue에서 직접 호출합니다.
        handleVictory();
    };

    // [STEP 4] 최종 평가 단계로 이동
    const handleVictory = () => {
        gameState.feedbackMessage = "모든 분석이 완료되었습니다.";
        setPhase('EVALUATION');

        // [2026-02-13] 최종 점수 동적 계산 및 동기화
        updateFinalScore();

        // [2026-02-13] 최종 리포트 데이터 생성 자동 호출 (빈 화면 방지)
        generateEvaluation();

        addSystemLog("최종 리포트 생성 중...", "INFO");
    };

    /**
     * [2026-02-13] 실시간 및 최종 가중 점수 계산 로직 일원화
     * Diagnostic (20%) + Design (70%) + Iterative (10%)
     */
    const updateFinalScore = () => {
        const diagAvg = gameState.diagnosticScores.length > 0
            ? gameState.diagnosticScores.reduce((a, b) => a + b, 0) / gameState.diagnosticScores.length
            : 0;

        const designScore = gameState.phase3Score || 0;
        const iterativeScore = gameState.iterativeScore || 0;

        const weighted = Math.round(
            (diagAvg / 100) * 20 +
            (designScore / 100) * 70 +
            (iterativeScore / 100) * 10
        );

        gameState.score = weighted;
        gameState.finalWeightedScore = weighted;
    };


    // --- Final Evaluation ---
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
        tailQuestion: null,
        converted_python: "",
        python_feedback: "",
        overall_score: 0,
        rule_score: 0,
        dimensions: {}
    });
    const isEvaluating = ref(false);

    /**
     * ✅ 개선: Phase 3 결과 재사용 + AI 멘토 코칭
     */
    const generateEvaluation = async () => {
        isEvaluating.value = true;
        addSystemLog("AI 아키텍트가 최종 리포트를 생성 중입니다...", "INFO");

        try {
            // ✅ Phase 3 평가 결과 재사용 (캐싱)
            const phase3Result = gameState.phase3EvaluationResult;

            if (!phase3Result || !phase3Result.dimensions) {
                throw new Error('Phase 3 evaluation not found');
            }

            // [2026-02-13] 통합 가중 점수 계산 함수 재사용
            updateFinalScore();
            const finalScore = gameState.finalWeightedScore;

            evaluationResult.finalScore = finalScore;

            // 상세 비중 리포트용 개별 가중치 재계산 (표시용)
            const diagAvg = gameState.diagnosticScores.length > 0
                ? gameState.diagnosticScores.reduce((a, b) => a + b, 0) / gameState.diagnosticScores.length
                : 0;
            const designScore = phase3Result.overall_score || 0;
            const iterativeScore = gameState.iterativeScore || 0;

            evaluationResult.diagnosticScoreWeighted = Math.round((diagAvg / 100) * 20 * 10) / 10;
            evaluationResult.designScoreWeighted = Math.round((designScore / 100) * 70 * 10) / 10;
            evaluationResult.iterativeScoreWeighted = Math.round((iterativeScore / 100) * 10 * 10) / 10;

            evaluationResult.gameScore = Math.round(diagAvg);
            evaluationResult.aiScore = Math.round(designScore);
            evaluationResult.rule_score = phase3Result.rule_score || 0;

            evaluationResult.dimensions = {};
            Object.keys(phase3Result.dimensions || {}).forEach(key => {
                const d = phase3Result.dimensions[key];
                // [2026-02-13] API에서 12점 스케일링(60%비중)된 것을 다시 100% 비율로 변환하여 표시
                const rawScore = d.original_score || (d.score * 100 / 12) || 0;
                evaluationResult.dimensions[key] = {
                    ...d,
                    score: Math.round(rawScore)
                };
            });

            evaluationResult.overall_score = designScore;

            addSystemLog(`진단 점수: ${evaluationResult.diagnosticScoreWeighted}/20`, "INFO");
            addSystemLog(`설계 점수: ${evaluationResult.designScoreWeighted}/70`, "INFO");
            addSystemLog(`최종 검증: ${evaluationResult.iterativeScoreWeighted}/10`, "INFO");
            addSystemLog(`최종 미션 스코어: ${finalScore}/100`, "SUCCESS");

            // ✅ 5차원 메트릭 매핑 (한글화)
            const DIMENSION_NAMES = {
                coherence: '정합성',
                abstraction: '추상화',
                exception_handling: '예외처리',
                implementation: '구현력',
                architecture: '설계력'
            };

            evaluationResult.details = Object.entries(evaluationResult.dimensions).map(([key, data]) => ({
                id: key,
                category: DIMENSION_NAMES[key] || key,
                score: data.score,
                comment: data.basis || '적절한 논리 전개입니다.',
                improvement: data.improvement || '특별한 보완 사항이 없습니다.'
            }));

            // ✅ [2026-02-13] 연동 최적화: 백엔드 통합 조언 우선 사용
            evaluationResult.seniorAdvice = phase3Result.senior_advice || "탁월한 설계 역량을 보여주셨습니다.";

            addSystemLog("최종 리포트 생성 완료", "SUCCESS");

            // [2026-02-13] 코드 블루프린트 데이터 복사
            evaluationResult.converted_python = phase3Result.converted_python || "";
            evaluationResult.python_feedback = phase3Result.python_feedback || "";

            console.log('[generateEvaluation] Details:', evaluationResult.details);

            // ✅ [2026-02-13] 유튜브 추천 영상 연동
            evaluationResult.supplementaryVideos = phase3Result.recommended_videos || [];

            // ✅ [2026-02-13] 연동 최적화: 백엔드 통합 조언을 최종적으로 확정 (중복 호출 제거)
            evaluationResult.seniorAdvice = phase3Result.senior_advice || "탁월한 설계 역량을 보여주셨습니다.";

            addSystemLog("최종 리포트 데이터 바인딩 완료", "SUCCESS");

            // ✅ 등급 결정
            if (evaluationResult.finalScore >= 90) {
                evaluationResult.scoreTier = "Architect";
            } else if (evaluationResult.finalScore >= 80) {
                evaluationResult.scoreTier = "Senior";
            } else if (evaluationResult.finalScore >= 70) {
                evaluationResult.scoreTier = "Mid-Level";
            } else {
                evaluationResult.scoreTier = "Junior";
            }

            // ✅ [2026-02-13] 유튜브 추천 영상 매핑
            if (phase3Result.recommended_videos) {
                evaluationResult.supplementaryVideos = phase3Result.recommended_videos;
                addSystemLog(`추천 강의 ${evaluationResult.supplementaryVideos.length}건 준비 완료`, "INFO");
            }

        } catch (error) {
            console.error("Final Eval Error", error);

            // Fallback
            const gamePerformanceScore = Math.min(100, Math.floor((gameState.score / 1300) * 100));
            evaluationResult.finalScore = gamePerformanceScore;
            evaluationResult.aiAnalysis = "통신 지연으로 로컬 리포트로 대체합니다.";
            evaluationResult.details = generateFallbackDetails();
            evaluationResult.seniorAdvice = "평가 오류가 발생했습니다. 다시 시도해주세요.";

        } finally {
            isEvaluating.value = false;
        }
    };

    /**
     * Fallback: 규칙 기반 5차원 점수
     */
    function generateFallbackDetails() {
        return [
            {
                category: 'Consistency',
                score: 70,
                comment: '기본 개념은 이해했으나 세부사항 부족',
                improvement: '문제 요구사항과 로직의 일치도를 높이세요'
            },
            {
                category: 'Abstraction',
                score: 65,
                comment: '키워드 나열 수준',
                improvement: 'IF-THEN 구조로 조건과 행동을 명확히 분리하세요'
            },
            {
                category: 'Exception Handling',
                score: 50,
                comment: '예외 처리 누락',
                improvement: '엣지 케이스(빈 데이터, None 값) 처리를 추가하세요'
            },
            {
                category: 'Implementation',
                score: 75,
                comment: '실행 가능한 수준',
                improvement: '각 단계를 더 구체화하세요'
            },
            {
                category: 'Design',
                score: 70,
                comment: '기본 구조는 양호',
                improvement: '단계 간 연결성을 명시하세요'
            }
        ];
    }

    // --- Snippets ---
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

    return {
        // From GameEngine
        gameState,
        enemyThreat,
        diagnosticQuestion,
        submitDiagnostic,
        isEvaluating,
        currentMission,
        evaluationResult,
        deepQuizQuestion,
        missionContext,
        constraints,

        // Methods
        startGame,
        selectStage,
        submitPseudo,
        submitDeepQuiz,

        nextMission,
        restartMission,

        // Code Runner
        userCode: computed(() => runnerState.userCode),
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
        handlePythonVisualizationNext,
        handleTailSelection,
        resetFlow: () => startGame(),
        toggleHint: () => { gameState.showHint = !gameState.showHint; },
        handlePracticeClose: () => router.push('/')
    };
}
