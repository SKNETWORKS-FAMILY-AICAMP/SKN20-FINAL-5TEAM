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

    // [2026-02-13] 실시간 힌트 오리 관련 상태
    const showHintDuck = ref(false);
    const dynamicHintMessage = ref("");

    const toggleHintDuck = () => {
        showHintDuck.value = !showHintDuck.value;
        if (showHintDuck.value) {
            updateDynamicHint();
        }
    };

    /**
     * [2026-02-14 수정] 실시간 의사코드 분석 및 풍부한 유동적 힌트 생성
     */
    const updateDynamicHint = () => {
        const code = gameState.phase3Reasoning || "";

        // 힌트 데이터 뱅크
        const HINT_POOLS = {
            isolation: [
                "단어들은 잘 나열하셨네요! 하지만 이 단계들이 어떤 순서로 배치되어야 미래의 시험 문제가 학습 데이터로 새어나가지 않을까요?",
                "모델이 학습하는 동안 미래의 정답지(Test)를 한 번이라도 훔쳐본다면, 그 성능을 신뢰할 수 있을까요? 물리적인 벽을 세우는 시점을 고민해 보세요.",
                "현실 세계에서는 미래 데이터를 미리 알 수 없습니다. 현재 설계에서 '과거'와 '미래'를 가르는 명확한 선은 어디에 있나요?",
                "전처리 도구가 전체 데이터의 특성(평균, 편차 등)을 미리 학습해버린다면, 이미 정보 유출이 시작된 것 아닐까요? 분할의 선후 관계를 다시 보세요."
            ],
            anchor: [
                "만약 테스트 데이터로 기준을 새로 잡는다면, 학습 때 고생해서 만든 '기준점'이 흔들리지 않을까요? 모델이 배포된 후에도 이 기준을 유지할 방법을 고민해보세요.",
                "우리가 가진 유일한 **'믿을 수 있는 과거'**는 어떤 데이터셋인가요? 그 데이터셋만이 기준점(fit)이 될 자격이 있습니다.",
                "운영(Serving) 환경에서는 데이터가 한 건씩 들어옵니다. 그때마다 기준점을 새로 잡는다면, 모델이 배운 '원래의 잣대'가 유지될 수 있을까요?",
                "테스트 데이터의 통계량을 기준점 설정에 포함하는 순간, 그것은 더 이상 공정한 테스트가 아닌 '답안지 유출'이 됩니다."
            ],
            abstraction: [
                "키워드는 완벽해요! 이제 이 재료들을 연결해볼까요? '격리'가 된 상태에서 '기준점'을 잡아야 하는 공학적인 이유는 무엇일까요?",
                "학습할 때는 섭씨(°C)로 가르치고, 시험 볼 때는 화씨(°F)로 물어본다면 모델이 정답을 맞출 수 있을까요? 변환의 기준을 똑같이 맞추는 방법은 무엇일까요?",
                "운영 환경에서 들어오는 '쌩쌩한' 데이터에 학습 때 썼던'동일한 저울'을 적용하는 구체적인 로직이 포함되었나요?",
                "모델이 배포된 후에도 '과거의 기준'에 자신을 맞추게 만드는 장치가 무엇인지 설계에 반영해 보세요."
            ],
            consistency: [
                "학습할 때는 섭씨(°C)로 가르치고, 시험 볼 때는 화씨(°F)로 물어본다면 모델이 정답을 맞출 수 있을까요? 변환의 기준을 똑같이 맞추는 방법은 무엇일까요?",
                "운영 환경에서 들어오는 '쌩쌩한' 데이터에 학습 때 썼던 **'동일한 저울'**을 적용하는 구체적인 로직이 포함되었나요?",
                "모델이 배포된 후에도 '과거의 기준'에 자신을 맞추게 만드는 장치가 무엇인지 설계에 반영해 보세요."
            ]
        };

        const getRandomHint = (pool) => pool[Math.floor(Math.random() * pool.length)];

        // 유형 1: [격리 Isolation] 개념 부족 (순서 오류/분리 미흡)
        const hasSplit = /split|분할|나누|분리/i.test(code);
        const fitPos = code.search(/fit|기준|학습/i);
        const splitPos = code.search(/split|분할|나누|분리/i);

        if (!hasSplit || (fitPos !== -1 && splitPos !== -1 && fitPos < splitPos)) {
            dynamicHintMessage.value = getRandomHint(HINT_POOLS.isolation);
            return;
        }

        // 유형 2: [기준점 Anchor] 개념 부족 (Train/Test 혼동)
        if (/(fit|학습|기준)\s*.*\s*(all|전체|test|테스트|전체데이터|모든|test_df|test_data)/i.test(code)) {
            dynamicHintMessage.value = getRandomHint(HINT_POOLS.anchor);
            return;
        }

        // 유형 4: [일관성 (Consistency)] 관련: 운영 환경 적용 오류
        const hasTransform = /transform|변환|적용/i.test(code);
        if (!hasTransform) {
            dynamicHintMessage.value = getRandomHint(HINT_POOLS.consistency);
            return;
        }

        // 유형 3: [추상화 Abstraction] 논리적 연결 부족 (단순 나열)
        const hasConnections = /->|>|다음으로|그 후|순서|단계|이후|과정/i.test(code);
        if (code.length < 60 || !hasConnections) {
            dynamicHintMessage.value = getRandomHint(HINT_POOLS.abstraction);
            return;
        }

        dynamicHintMessage.value = "완벽한 설계입니다! 이제 [심화 분석 시작]을 통해 아키텍처의 완성도를 검증받아보세요.";
    };

    // [2026-02-12] 에디터 내용 변경 시 실시간 체크리스트 및 힌트 업데이트
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
        if (showHintDuck.value) {
            updateDynamicHint();
        }
    });

    // [2026-02-13] 설계 단계 진입 시 초기화
    watch(() => gameState.phase, (newPhase) => {
        if (newPhase === 'PSEUDO_WRITE') {
            showHintDuck.value = false;
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

        // ✅ [FIX] 안전 타임아웃 - 45초 후 강제 해제 (API 타임아웃 35초보다 길게 설정)
        const safetyTimeout = setTimeout(() => {
            console.error('[submitPseudo] Safety timeout triggered - forcing phase transition');
            isProcessing.value = false;
            gameState.feedbackMessage = "평가 시간 초과. 다음 단계로 진행합니다.";
            addSystemLog("평가 시간 초과 - 기본 점수 부여", "WARN");
            setPhase('DEEP_QUIZ');
        }, 45000);

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
            gameState.phase3Score = evaluation.overall_score || 0;

            // [2026-02-13] 청사전(Blueprint) 사용 추적: 무성의 답변으로 복기 모드 진입 시 마킹
            evaluationResult.is_low_effort = evaluation.is_low_effort;
            if (evaluation.is_low_effort) {
                gameState.hasUsedBlueprint = true;
                addSystemLog("복기 학습 모드 진입: 청사진 참고 기록됨", "WARN");
            }

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
            if (evaluation.deep_dive) {
                evaluationResult.deepDive = evaluation.deep_dive;
            }
            evaluationResult.overall_score = evaluation.overall_score || 0;
            evaluationResult.is_low_effort = evaluation.is_low_effort || false;
            // 2026-02-14 수정: 페르소나 및 총평 데이터 매핑 추가
            evaluationResult.persona_name = evaluation.persona_name || "";
            evaluationResult.one_line_review = evaluation.one_line_review || "";

            // ✅ [FIX] dimensions null-safe 접근
            const dims = evaluation.dimensions || {};

            // 5차원 점수별 로그 출력 (null-safe)
            const dimKeys = ['design', 'consistency', 'implementation', 'edge_case', 'abstraction'];
            const dimLabels = ['설계력', '정합성', '구현력', '예외처리', '추상화'];

            dimKeys.forEach((key, i) => {
                const dim = dims[key];
                if (dim) {
                    // [2026-02-13] 백엔드에서 이미 85점 만점 기준 가중치 점수로 옴. 
                    // displayScore를 위해 역산하거나 그냥 보여줌.
                    // 원본 100점 만점이 필요하면 (score / maxWeight) * 100
                    const weights = { design: 25, consistency: 20, implementation: 10, edge_case: 15, abstraction: 15 };
                    const displayScore = Math.round((dim.score / weights[key]) * 100);
                    addSystemLog(`${dimLabels[i]}: ${displayScore}점 - ${dim.basis || '분석 완료'}`, "INFO");
                }
            });

            // ✅ [2026-02-13] 차원 점수 합계로 종합 점수 재계산 (백엔드 불일치 방지)
            const sumOfDimensions = Object.values(dims)
                .filter(d => d && typeof d.score === 'number')
                .reduce((sum, d) => sum + d.score, 0);

            // 종합 점수 보정 (최대 85점)
            evaluationResult.overall_score = sumOfDimensions;
            gameState.phase3EvaluationResult.overall_score = sumOfDimensions;
            gameState.phase3Score = sumOfDimensions + (evaluationResult.rule_score || 0);

            // 평균 점수 계산 (각 항목의 원래 점수 기준 평균이 아님. 백분위 평균으로 보여줄 것)
            let sumPercentage = 0;
            let countDimensions = 0;
            const SCORE_WEIGHTS = { design: 25, consistency: 20, implementation: 10, edge_case: 15, abstraction: 15 };

            Object.keys(dims).forEach(k => {
                if (dims[k] && typeof dims[k].score === 'number') {
                    const maxW = SCORE_WEIGHTS[k] || 20;
                    sumPercentage += (dims[k].score / maxW) * 100;
                    countDimensions++;
                }
            });

            const avgPercentage = countDimensions > 0 ? Math.round(sumPercentage / countDimensions) : 0;

            // [2026-02-13] 피드백 메시지에 점수 노출 방지 (유저 요청: 로딩 중/직후 점수 팝업 숨김)
            gameState.feedbackMessage = null;

            // [2026-02-13] gameState.score 직접 가산 제거 (Phase 3 점수는 gameState.phase3Score에 보관)
            addSystemLog(`아키텍처 평가 완료: ${sumOfDimensions}점 (${avgPercentage}%)`, "SUCCESS");

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
                        design: { score: 10, basis: '평가 오류로 기본 점수', improvement: null },
                        consistency: { score: 10, basis: '평가 오류로 기본 점수', improvement: null },
                        implementation: { score: 5, basis: '평가 오류로 기본 점수', improvement: null },
                        edge_case: { score: 5, basis: '평가 오류로 기본 점수', improvement: null },
                        abstraction: { score: 5, basis: '평가 오류로 기본 점수', improvement: null }
                    },
                    strengths: [],
                    weaknesses: ['평가 시스템 오류'],
                    deep_dive: null,
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
    // --- Deep Quiz & Tail Question ---
    const deepQuizQuestion = computed(() => {
        const isVisualization = gameState.phase === 'PYTHON_VISUALIZATION';
        const isTailQuestion = gameState.phase === 'TAIL_QUESTION';
        const isDeepQuiz = gameState.phase === 'DEEP_QUIZ';
        const rawScore = evaluationResult.overall_score || gameState.phase3Score || 0;
        const score = Number(rawScore);

        // [2026-02-13] AI가 생성한 질문(tailQuestion)이 있다면 점수와 상관없이 최우선 표시
        // 특히 '복기 모드'나 '심화 시나리오'가 여기 담겨 있음
        const aiTq = evaluationResult.tailQuestion;
        const aiDq = evaluationResult.deepDive;

        if (aiTq && aiTq.should_show) {
            return {
                question: aiTq.reason ? `[${aiTq.reason}] ${aiTq.question}` : aiTq.question,
                options: (aiTq.options || []).map(opt => ({
                    text: opt.text,
                    is_correct: opt.is_correct || opt.correct,
                    reason: opt.reason || '개념 확인이 필요합니다.'
                }))
            };
        }

        // 1. 저득점 보완 질문 (폴백)
        if ((isVisualization || isTailQuestion) && score < 80) {
            return {
                question: "[기초 보완] 작성하신 의사코드의 선후 관계를 다시 한 번 검토해볼까요?",
                options: [
                    { text: "네, 로직의 선후 관계를 명확히 다듬겠습니다.", is_correct: true, reason: "안정적인 코드 구현을 위해 구조적 탄탄함은 필수입니다." },
                    { text: "현재 로직으로도 충분해 보입니다.", is_correct: false, reason: "보이지 않는 에지 케이스가 있을 수 있습니다." }
                ]
            };
        }

        // 2. 고득점 또는 AI 심화 질문
        if ((isVisualization || isDeepQuiz || isTailQuestion)) {
            const dq = aiDq || currentMission.value?.deepDiveQuestion;
            if (!dq) return null;

            return {
                question: dq.title ? `[${dq.title}] ${dq.question}` : `[심화 챌린지] ${dq.question}`,
                options: (dq.options || []).map(opt => ({
                    text: opt.text,
                    is_correct: opt.is_correct || opt.correct,
                    reason: opt.reason || opt.feedback || '심화 개념 확인이 필요합니다.'
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
     * [2026-02-13] 아키텍처 복기 후 재설계 시도 (Retry)
     */
    const retryDesign = () => {
        addSystemLog("청사진을 참고하여 설계를 보완해 보세요.", "INFO");
        setPhase('PSEUDO_WRITE');
    };

    /**
     * [2026-02-13] 실시간 및 최종 가중 점수 계산 로직 일원화
     * Diagnostic (20%) + Design (70%) + Iterative (10%)
     */
    const updateFinalScore = () => {
        // [2026-02-13] 유저 요청: 객관식 퀴즈(Diagnostic) 및 부가 점수는 최종 합산에서 제외
        // 오직 실전 설계(Phase 3: Rule 15% + AI 85% = 100%) 성적만 반영합니다.
        let weighted = gameState.phase3Score || 0;

        // [2026-02-13] Blueprint Exploitation 방지 로직: 
        // 청사진을 한 번이라도 참고하여 재설계한 경우, 최종 점수를 80점으로 캡(Cap) 적용
        if (gameState.hasUsedBlueprint && weighted > 80) {
            weighted = 80;
            addSystemLog("청사진 참고로 인해 최종 평가가 80점으로 조정되었습니다.", "INFO");
        }

        gameState.score = weighted;
        gameState.finalWeightedScore = weighted;
    };
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
        deepDive: null, // [2026-02-13] 4지선다형 심화 질문
        recommendedLecture: null, // [2026-02-13] 추천 강의
        converted_python: "",
        python_feedback: "",
        overall_score: 0,
        rule_score: 0,
        dimensions: {},
        is_low_effort: false
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

            // [2026-02-13] 통합 가중 점수 계산 함수 (Diagnostic 제외 반영)
            updateFinalScore();
            const finalScore = gameState.finalWeightedScore;

            evaluationResult.finalScore = finalScore;

            // [2026-02-13] 5차원 지표 매핑 최적화
            const diagAvg = gameState.diagnosticScores.length > 0
                ? gameState.diagnosticScores.reduce((a, b) => a + b, 0) / gameState.diagnosticScores.length
                : 0;

            const aiScore = phase3Result.ai_score || 0;
            const ruleScore = phase3Result.rule_score || 0;

            evaluationResult.diagnosticScoreWeighted = 0; // 이제 0
            evaluationResult.designScoreWeighted = Math.round((aiScore / 85) * 85 * 10) / 10;
            evaluationResult.iterativeScoreWeighted = ruleScore; // Rule 점수(15)를 여기에 매핑

            evaluationResult.gameScore = Math.round(diagAvg);
            evaluationResult.aiScore = Math.round(aiScore);
            evaluationResult.rule_score = ruleScore;

            evaluationResult.dimensions = {};
            const MAX_WEIGHTS = {
                design: 25,
                consistency: 20,
                implementation: 10,
                edge_case: 15,
                abstraction: 15
            };

            Object.keys(phase3Result.dimensions || {}).forEach(key => {
                const d = phase3Result.dimensions[key];
                // [2026-02-13] 167% 버그 수정: 백엔드 개별 배점(Max Weight)을 기준으로 백분율 계산
                const maxW = MAX_WEIGHTS[key] || 15;
                const rawScore = d.original_score || (d.score * 100 / maxW) || 0;
                evaluationResult.dimensions[key] = {
                    ...d,
                    score: Math.min(100, Math.round(rawScore))
                };
            });

            evaluationResult.overall_score = evaluationResult.designScoreWeighted;

            // addSystemLog(`진단 점수: ${evaluationResult.diagnosticScoreWeighted}/20`, "INFO");
            // addSystemLog(`설계 점수: ${evaluationResult.designScoreWeighted}/70`, "INFO");
            // addSystemLog(`최종 검증: ${evaluationResult.iterativeScoreWeighted}/10`, "INFO");
            // addSystemLog(`최종 미션 스코어: ${finalScore}/100`, "SUCCESS");

            // ✅ 5차원 메트릭 매핑 (백엔드 키와 정합성 시급 패치)
            const DIMENSION_NAMES = {
                design: '설계력',
                consistency: '정합성',
                edge_case: '예외처리',
                implementation: '구현력',
                abstraction: '추상화'
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

            // [2026-02-13] 추천 강의 데이터 연동
            if (phase3Result.recommended_lecture) {
                evaluationResult.recommendedLecture = phase3Result.recommended_lecture;
            }

            console.log('[generateEvaluation] Details:', evaluationResult.details);

            // ✅ AI 멘토 코칭 생성
            try {
                const seniorAdvice = await generateSeniorAdvice(phase3Result, gameState);
                evaluationResult.seniorAdvice = seniorAdvice;
                addSystemLog("시니어 아키텍트 조언 생성 완료", "SUCCESS");
            } catch (error) {
                console.error('[Senior Advice Error]', error);
                evaluationResult.seniorAdvice = evaluationResult.finalScore >= 50
                    ? "훌륭한 시도였습니다. 실전에서 적용하며 계속 발전시켜 나가세요."
                    : "로직의 기초를 더 탄탄히 다져야 합니다. 가이드라인을 참고하여 다시 설계해보세요.";
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
        // [2026-02-13] 하드코딩 탈피: 게임 점수와 미션 성격을 결합한 동적 리포트 생성
        const baseScore = Math.min(100, Math.floor((gameState.score / 100) * 80));
        const missionName = currentMission.value?.subModuleTitle || "ARCH";

        const DIM_NAMES = {
            design: '설계력',
            consistency: '정합성',
            implementation: '구현력',
            edge_case: '예외처리',
            abstraction: '추상화'
        };

        return Object.keys(DIM_NAMES).map(key => ({
            id: key,
            category: DIM_NAMES[key],
            score: Math.max(40, baseScore - Math.floor(Math.random() * 10)),
            comment: `${missionName}의 주요 원칙이 반영된 설계입니다.`,
            improvement: '시니어의 청사진을 참고하여 세부 로직을 보완하세요.'
        }));
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

    /**
     * [2026-02-13] AI 엔진 장애 시 동적 분석 기반 대체 피드백 생성 (하드코딩 방지)
     */
    function getDynamicFallbackAdvice(result) {
        const sortedDetails = result.details?.length > 0
            ? [...result.details].sort((a, b) => a.score - b.score)
            : [];
        const weakest = sortedDetails[0] || { category: '설계' };
        const missionName = currentMission.value?.subModuleTitle || "아키텍처 미션";

        if (result.finalScore >= 80) {
            return `[S-CLASS] ${missionName}의 핵심 원칙을 매우 우수하게 구현했습니다. 특히 ${weakest.category} 설계가 조금 더 보강된다면 실전에서도 즉시 통용될 수준의 완벽한 아키텍처가 될 것입니다.`;
        } else if (result.finalScore >= 50) {
            return `[STANDARD] 전반적인 논리 흐름은 준수하나 ${weakest.category} 관점에서의 정합성이 다소 불안정합니다. 시니어의 청사진을 참고하여 본인의 설계와 대조해 보며 복기해 보시길 권장합니다.`;
        } else {
            return `[RE-DESIGN] ${missionName} 수행을 위한 기초적인 설계 보완이 시급합니다. ${weakest.category}를 포함한 필수 제약조건을 다시 한번 점검하고, 아키텍트의 가이드라인에 따라 뼈대부터 재구축해 주십시오.`;
        }
    }

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
        retryDesign,

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
        handlePracticeClose: () => router.push('/practice')
    };

}
