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

import { ref, computed, reactive } from 'vue';
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
    const toggleGuide = () => { isGuideOpen.value = !isGuideOpen.value; };
    const handleGuideClick = (idx) => { selectedGuideIdx.value = idx; };

    // Checklist (규칙 기반 실시간 피드백)
    const ruleChecklist = ref([
        {
            id: 'check_fit',
            label: 'fit 메서드 호출 감지',
            patterns: [/\.fit\(/i, /fit\(/i, /scaler.*fit/i, /encoder.*fit/i],
            hint: "scaler.fit( 또는 encoder.fit( 패턴 찾기",
            completed: false
        },
        {
            id: 'check_split',
            label: '분할 코드 유무 확인',
            patterns: [/train_test_split/i, /분할/i, /split/i, /\[:/i],
            hint: "train_test_split 또는 슬라이싱 체크",
            completed: false
        },
        {
            id: 'check_order',
            label: 'fit 이전에 분할 여부 검증',
            patterns: [/이전/i, /before/i, /앞/i, /먼저/i],
            hint: "fit 이전에 분할이 있는지 확인",
            completed: false
        },
        {
            id: 'check_warning',
            label: '경고 메시지 명시',
            patterns: [/경고/i, /warning/i, /알림/i, /THEN/i],
            hint: "THEN 경고: '...' 형태로 작성",
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

    const handlePseudoInput = (e) => {
        if (!e || !e.target) return;
        const val = e.target.value ?? "";
        if (typeof val !== 'string') return;

        gameState.phase3Reasoning = val;

        // 실시간 체크리스트 업데이트
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
    };

    // --- Diagnostic Logic ---
    const diagnosticQuestion1 = computed(() => {
        const mission = currentMission.value;
        if (!mission || !mission.interviewQuestions || !mission.interviewQuestions[0]) {
            return { question: "로딩 중...", options: [], type: 'CHOICE' };
        }
        return mission.interviewQuestions[0];
    });

    const submitDiagnostic1 = async (optionIndex) => {
        const q = diagnosticQuestion1.value;

        // [2026-02-12] 서술형(DESCRIPTIVE) 타입 처리 (AI 평가 연동)
        if (q.type === 'DESCRIPTIVE') {
            // 이미 평가 결과가 있는 경우: 다음 단계로 진행 (수동 진행)
            if (gameState.diagnosticResult && !gameState.isEvaluatingDiagnostic) {
                setPhase('DIAGNOSTIC_2');
                gameState.step = 1;
                return;
            }

            if (!gameState.diagnosticAnswer || gameState.diagnosticAnswer.trim().length < 5) {
                gameState.feedbackMessage = "추론 내용을 조금 더 자세히 적어주세요 (최소 5자).";
                addSystemLog("입력 부족: 분석 내용이 너무 짧습니다.", "WARN");
                return;
            }

            gameState.isEvaluatingDiagnostic = true; // 로딩 시작
            gameState.feedbackMessage = "AI 아키텍트가 분석 중입니다...";
            addSystemLog("진단 답변 AI 분석 개시...", "INFO");

            try {
                const result = await evaluateDiagnosticAnswer(q, gameState.diagnosticAnswer);

                gameState.diagnosticResult = result;
                gameState.score += Math.round(result.score * 0.2); // 점수 비례 보상

                if (result.is_correct) {
                    gameState.feedbackMessage = "분석이 완료되었습니다. 결과를 확인하고 계속 진행하세요.";
                    addSystemLog("진단 성공: 데이터 누수 원리 파악 완료", "SUCCESS");
                } else {
                    gameState.feedbackMessage = "분석이 완료되었습니다. 보완할 점을 확인해 보세요.";
                    addSystemLog("진단 미흡: 핵심 원리 파악 부족", "WARN");
                }

                // 자동 전환 제거: 사용자가 결과를 충분히 읽을 시간을 확보함
                gameState.isEvaluatingDiagnostic = false;

            } catch (error) {
                console.error("Diagnostic Evaluation Fail:", error);
                gameState.isEvaluatingDiagnostic = false;
                setPhase('DIAGNOSTIC_2');
            }
            return;
        }

        // 기존 선택형 로직
        if (optionIndex === undefined || !q.options[optionIndex]) return;

        if (q.options[optionIndex].correct) {
            gameState.score += 7.5;
            gameState.feedbackMessage = "정확합니다! 프로토콜 확인.";
            addSystemLog("선택 승인: 프로토콜 재가동", "SUCCESS");
            setTimeout(() => {
                setPhase('DIAGNOSTIC_2');
                gameState.step = 1;
            }, 1000);
        } else {
            handleDamage();
            gameState.feedbackMessage = "오답입니다. 다시 시도하세요.";
            addSystemLog("오류: 잘못된 판단입니다", "ERROR");
        }
    };

    const diagnosticQuestion2 = computed(() => {
        const mission = currentMission.value;
        if (!mission || !mission.interviewQuestions || !mission.interviewQuestions[1]) {
            return { question: "로딩 중...", options: [], type: 'CHOICE' };
        }
        return mission.interviewQuestions[1];
    });

    const submitDiagnostic2 = async (optionIndex) => {
        const q = diagnosticQuestion2.value;

        // [2026-02-12] 서술형(DESCRIPTIVE) 타입 처리 (AI 평가 연동)
        if (q.type === 'DESCRIPTIVE') {
            // 이미 평가 결과가 있는 경우: 다음 단계로 진행 (수동 진행)
            if (gameState.diagnosticResult2 && !gameState.isEvaluatingDiagnostic) {
                setPhase('PSEUDO_WRITE');
                gameState.step = 1;
                return;
            }

            if (!gameState.diagnosticAnswer2 || gameState.diagnosticAnswer2.trim().length < 5) {
                gameState.feedbackMessage = "체크리스트 내용을 조금 더 자세히 적어주세요 (최소 5자).";
                addSystemLog("입력 부족: 규칙 나열이 부족합니다.", "WARN");
                return;
            }

            gameState.isEvaluatingDiagnostic = true; // 로딩 시작
            gameState.feedbackMessage = "AI 아키텍트가 체크리스트를 검증 중입니다...";
            addSystemLog("진단 2단계 AI 검증 개시...", "INFO");

            try {
                const result = await evaluateDiagnosticAnswer(q, gameState.diagnosticAnswer2);

                gameState.diagnosticResult2 = result;
                gameState.score += Math.round(result.score * 0.2); // 점수 비례 보상

                if (result.is_correct) {
                    gameState.feedbackMessage = "검증 규칙이 논리적입니다. 결과를 확인하고 계속 진행하세요.";
                    addSystemLog("검증 성공: 논리적 체크리스트 확보", "SUCCESS");
                } else {
                    gameState.feedbackMessage = "일부 누락된 조건이 있습니다. 보완할 점을 확인해 보세요.";
                    addSystemLog("검증 미흡: 체크리스트 보완 필요", "WARN");
                }

                gameState.isEvaluatingDiagnostic = false;

            } catch (error) {
                console.error("Diagnostic 2 Evaluation Fail:", error);
                gameState.isEvaluatingDiagnostic = false;
                setPhase('PSEUDO_WRITE');
            }
            return;
        }

        // 기존 선택형 로직
        const selected = q.options[optionIndex];
        if (!selected) return;

        gameState.selectedStrategyLabel = selected.text;

        if (selected.correct) {
            gameState.score += 7.5;
            gameState.feedbackMessage = "전략 선택 완료.";
            addSystemLog("전략 채택: 아키텍처 분석 단계로 이동", "SUCCESS");
            setTimeout(() => {
                setPhase('PSEUDO_WRITE');
                gameState.step = 2;
            }, 1000);
        } else {
            handleDamage();
            gameState.feedbackMessage = "비효율적 전략입니다.";
            addSystemLog("경고: 비효율적 전략입니다", "ERROR");
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
            gameState.score += 5;
            addSystemLog("평가 시간 초과 - 기본 점수 부여", "WARN");
            setPhase('DEEP_QUIZ');
        }, 30000);

        try {
            gameState.feedbackMessage = "AI 아키텍트가 5차원 메트릭으로 분석 중...";
            addSystemLog("5차원 메트릭 평가 시작...", "INFO");

            console.log('[submitPseudo] Calling evaluatePseudocode5D...');
            console.log('[submitPseudo] Mission:', currentMission.value?.id);
            console.log('[submitPseudo] Pseudocode:', gameState.phase3Reasoning.substring(0, 100));

            // ✅ 새로운 5차원 평가 API 호출
            const evaluation = await evaluatePseudocode5D(
                currentMission.value,
                gameState.phase3Reasoning
            );

            console.log('[submitPseudo] Evaluation result:', evaluation);

            // ✅ [FIX] evaluation 유효성 검사
            if (!evaluation || typeof evaluation !== 'object') {
                console.error('[submitPseudo] Invalid evaluation result received:', evaluation);
                throw new Error('Invalid evaluation result');
            }

            // 평가 결과 저장
            gameState.phase3Score = evaluation.overall_score || 0;
            gameState.phase3EvaluationResult = evaluation;

            // ✅ Python 변환 결과 저장 (Visualizer용)
            // evaluationResult는 reactive 객체이므로 직접 속성 할당 가능
            if (evaluation.converted_python) {
                evaluationResult.converted_python = evaluation.converted_python;
            }
            if (evaluation.python_feedback) {
                evaluationResult.python_feedback = evaluation.python_feedback;
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
                    const score = Math.round(dim.score || 0);
                    const basis = dim.basis ? dim.basis.substring(0, 30) : '분석 완료';
                    addSystemLog(`${dimLabels[i]}: ${score}점 - ${basis}...`, "INFO");
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

            // ✅ 실제 점수 기반 보상 (최대 20점)
            const reward = Math.round((evaluation.overall_score || 0) * 0.2);
            gameState.score += reward;
            addSystemLog(`아키텍처 평가 보상: +${reward}점`, "SUCCESS");

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
            gameState.score += 8;

            // ✅ [FIX] 기본 evaluation 결과 생성 (EVALUATION 단계에서 사용)
            if (!gameState.phase3EvaluationResult) {
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
                    grade: 'fair'
                };
                gameState.phase3Score = 50;
            }

            addSystemLog("평가 시스템 오류, 기본 점수 부여 후 심화 검증으로 이동", "WARN");
            setTimeout(() => setPhase('DEEP_QUIZ'), 800);
        } finally {
            // ✅ [FIX] 안전 타임아웃 클리어
            clearTimeout(safetyTimeout);
            isProcessing.value = false;
        }
    };

    // --- Deep Quiz & Tail Question ---
    const deepQuizQuestion = computed(() => {
        // [2026-02-12] Tail Question 우선 처리
        if (gameState.phase === 'TAIL_QUESTION' && evaluationResult.tailQuestion) {
            const tq = evaluationResult.tailQuestion;
            return {
                question: `[추가 검증] ${tq.question}`,
                options: (tq.options || []).map(opt => ({
                    text: opt.text,
                    is_correct: opt.is_correct,
                    reason: opt.reason
                }))
            };
        }

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
        const questionData = deepQuizQuestion.value;
        const selected = questionData.options[optionIndex];

        if (!selected) return;

        // Tail Question 처리 분기
        if (gameState.phase === 'TAIL_QUESTION') {
            handleTailQuestion(selected);
            return;
        }

        // Deep Quiz 처리
        if (selected && selected.correct) {
            gameState.score += 20;
            addSystemLog("심화 검증 통과", "SUCCESS");
            handleVictory();
        } else {
            handleDamage();
            gameState.feedbackMessage = "개념 오인.";
            addSystemLog("검증 실패: 개념 재확인 필요", "ERROR");
        }
    };

    // [STEP 3] Tail Question 처리 로직 (+5점 보너스)
    const handleTailSelection = (option) => {
        if (!option) return;

        if (option.is_correct) {
            gameState.score += 5;
            gameState.feedbackMessage = "정확합니다! (+5점)";
            addSystemLog(`보완 성공: ${option.reason} (+5점)`, "SUCCESS");
        } else {
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
        const score = evaluationResult.overall_score || 0;
        const evaluation = gameState.phase3EvaluationResult;

        if (score >= 80) {
            addSystemLog("설계 우수. 심화 검증(Deep Dive) 챌린지 시작!", "SUCCESS");
            setPhase('DEEP_QUIZ');
        } else {
            // Tail Question 설정 (없으면 Fallback)
            if (evaluation && evaluation.tail_question) {
                evaluationResult.tailQuestion = evaluation.tail_question;
            } else {
                // Fallback Question
                evaluationResult.tailQuestion = {
                    question: "작성하신 코드의 실행 흐름을 다시 한 번 점검해보세요.",
                    options: [
                        { text: "네, 다시 확인하겠습니다.", is_correct: true, reason: "꼼꼼한 검증이 중요합니다." },
                        { text: "확인할 필요 없습니다.", is_correct: false, reason: "오류 가능성이 있습니다." }
                    ]
                };
            }

            addSystemLog("추가 검증이 필요합니다. (Tail Question)", "WARN");
            setPhase('TAIL_QUESTION');
        }
    };

    // [STEP 4] 최종 평가 단계로 이동
    const handleVictory = () => {
        gameState.feedbackMessage = "모든 분석이 완료되었습니다.";
        setPhase('EVALUATION');

        // 최종 점수 저장 및 리포트 생성 요청 (필요 시 백엔드 전송)
        addSystemLog("최종 리포트 생성 중...", "INFO");
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

            console.log('[generateEvaluation] Reusing Phase 3 result:', phase3Result);

            // ✅ 게임 점수 (40%)
            const maxScore = 1300;
            const gamePerformanceScore = Math.min(100, Math.floor((gameState.score / maxScore) * 100));

            // ✅ AI 5차원 점수 (60%)
            const aiScore = phase3Result.overall_score;

            // ✅ 최종 점수 = 게임 40% + AI 60%
            evaluationResult.finalScore = Math.floor((gamePerformanceScore * 0.4) + (aiScore * 0.6));
            evaluationResult.gameScore = gamePerformanceScore;
            evaluationResult.finalScore = Math.floor((gamePerformanceScore * 0.4) + (aiScore * 0.6));
            evaluationResult.gameScore = gamePerformanceScore;
            evaluationResult.aiScore = aiScore;
            evaluationResult.rule_score = phase3Result.rule_score || 0;
            evaluationResult.dimensions = phase3Result.dimensions || {};
            evaluationResult.overall_score = phase3Result.overall_score || 0;

            addSystemLog(`게임 점수: ${gamePerformanceScore}/100 (40%)`, "INFO");
            addSystemLog(`AI 점수: ${aiScore}/100 (60%)`, "INFO");
            addSystemLog(`최종 점수: ${evaluationResult.finalScore}/100`, "SUCCESS");

            // ✅ 5차원 메트릭 매핑
            const DIMENSION_NAMES = {
                coherence: 'Consistency',
                abstraction: 'Abstraction',
                exception_handling: 'Exception Handling',
                implementation: 'Implementation',
                architecture: 'Design'
            };

            evaluationResult.details = Object.entries(phase3Result.dimensions).map(([key, data]) => ({
                category: DIMENSION_NAMES[key] || key,
                score: Math.round(data.score),
                comment: data.basis || '분석 완료',
                improvement: data.improvement || ''
            }));

            console.log('[generateEvaluation] Details:', evaluationResult.details);

            // ✅ AI 멘토 코칭 생성
            try {
                const seniorAdvice = await generateSeniorAdvice(phase3Result, gameState);
                evaluationResult.seniorAdvice = seniorAdvice;
                addSystemLog("시니어 아키텍트 조언 생성 완료", "SUCCESS");
            } catch (error) {
                console.error('[Senior Advice Error]', error);
                evaluationResult.seniorAdvice = "훌륭한 시도였습니다. 실전에서 적용하며 계속 발전시켜 나가세요.";
            }

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
        handlePseudoInput,
        ruleChecklist,
        completedChecksCount,
        allChecksPassed,
        canSubmitPseudo,
        isProcessing,
        isGuideOpen,
        selectedGuideIdx,
        toggleGuide,
        handleGuideClick,
        handlePythonVisualizationNext,
        handleTailSelection,
        resetFlow: () => startGame(),
        handlePracticeClose: () => router.push('/practice'),
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
