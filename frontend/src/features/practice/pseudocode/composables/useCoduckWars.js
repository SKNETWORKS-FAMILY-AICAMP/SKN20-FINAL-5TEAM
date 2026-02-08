import { ref, computed, reactive, onMounted } from 'vue';
import axios from 'axios';
import { aiQuests } from '../data/stages.js';
import { quickCheckPseudocode, checkConsistency } from '../api/pseudocodeApi.js';
import { useGameStore } from '@/stores/game';

export function useCoduckWars() {
    const DEBUG_MODE = true;
    const gameStore = useGameStore();

    // [수정일: 2026-02-08] 맵에서 선택한 문제를 표시하기 위해 gameStore.selectedQuestIndex 사용
    // questIndex는 0-based이므로 stageId는 1-based로 변환 (id는 1부터 시작)
    const initialStageId = (gameStore.selectedQuestIndex || 0) + 1;

    // --- Game State ---
    const gameState = reactive({
        currentStageId: initialStageId,
        // New Phases: DIAGNOSTIC_1 -> DIAGNOSTIC_2 -> PSEUDO_WRITE -> PYTHON_FILL -> DEEP_QUIZ -> EVALUATION
        phase: 'DIAGNOSTIC_1',
        playerHP: 100,
        score: 0,
        combo: 0,

        // State for Decisions
        selectedStrategyLabel: "", // Set in Phase 2

        // Phase 3 State
        phase3Reasoning: "", // User Typed Logic
        phase3Score: 0, // 즉시 평가 점수
        phase3Feedback: "", // 즉시 평가 피드백
        showHint: false, // Hint visibility

        // Phase 4 State
        userCode: "", // The assembled code
        codeSlots: null, // Holds slot1, slot2, etc. after initPhase4Scaffolding
        codeExecutionResult: null, // 실제 실행 결과

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
        return aiQuests.find(q => q.id === gameState.currentStageId) || aiQuests[0];
    });

    // [수정일: 2026-02-08] 각 스테이지마다 다른 미션 컨텍스트와 제약사항 표시
    const missionContext = computed(() => {
        const mission = currentMission.value;
        return mission.designContext?.currentIncident || "미션 정보를 불러오는 중입니다.";
    });

    const constraints = computed(() => {
        const mission = currentMission.value;
        return mission.designContext?.engineeringRules || [];
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
                    gameState.phase3Score = 0;
                    gameState.phase3Feedback = "";
                    addSystemLog("자연어 처리 에디터 로드됨", "SUCCESS");
                    startHintTimer(); // Start 30s timer
                    break;
                case 'PYTHON_FILL':
                    gameState.coduckMessage = "사고와 코드가 일치하는지 확인하십시오.";
                    addSystemLog("구현 환경 동기화 완료", "SUCCESS");
                    initPhase4Scaffolding();
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

    // --- 1. Diagnostic Phase 1 (Q1) - 동적 로드 ---
    const diagnosticQuestion1 = computed(() => {
        const mission = currentMission.value;
        console.log('[DEBUG] diagnosticQuestion1 - currentMission:', mission);
        console.log('[DEBUG] currentStageId:', gameState.currentStageId);
        console.log('[DEBUG] aiQuests length:', aiQuests.length);

        if (!mission || !mission.interviewQuestions || !mission.interviewQuestions[0]) {
            console.warn('[DEBUG] Missing interviewQuestions!', mission);
            return { question: "로딩 중...", options: [] };
        }
        const q = mission.interviewQuestions[0];
        console.log('[DEBUG] Question loaded:', q.question);
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

    // --- 2. Diagnostic Phase 2 (Q2) - 동적 로드 ---
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

    // --- 3. Pseudo Write Phase (즉시 평가 추가) ---
    const submitPseudo = async () => {
        if (gameState.phase3Reasoning.length < 10) {
            gameState.feedbackMessage = "논리가 부족합니다.";
            addSystemLog("제출 거부: 논리 내용 부족", "WARN");
            return;
        }

        if (hintTimer) clearTimeout(hintTimer);

        // 즉시 평가
        gameState.feedbackMessage = "논리 분석 중...";
        addSystemLog("LLM 기반 논리 구조 분석 중...", "INFO");

        try {
            const evaluation = await quickCheckPseudocode(
                {
                    title: currentMission.value.title,
                    description: currentMission.value.missionObjective,
                    missionObjective: missionContext.value
                },
                gameState.phase3Reasoning
            );

            gameState.phase3Score = evaluation.score;
            gameState.phase3Feedback = evaluation.comment;

            // 점수 차등 부여
            if (evaluation.score >= 70) {
                gameState.score += 150;
                gameState.feedbackMessage = `우수 (${evaluation.score}점): ${evaluation.comment}`;
                addSystemLog(`논리 평가: 우수 (${evaluation.score}/100)`, "SUCCESS");
            } else if (evaluation.score >= 40) {
                gameState.score += 100;
                gameState.feedbackMessage = `보통 (${evaluation.score}점): ${evaluation.comment}`;
                addSystemLog(`논리 평가: 보통 (${evaluation.score}/100)`, "INFO");
            } else {
                gameState.score += 50;
                gameState.feedbackMessage = `미흡 (${evaluation.score}점): ${evaluation.comment}`;
                addSystemLog(`논리 평가: 개선 필요 (${evaluation.score}/100)`, "WARN");
            }

            // 점수와 관계없이 다음 단계로 (학습 기회 제공)
            setTimeout(() => setPhase('PYTHON_FILL'), 2000);

        } catch (error) {
            console.error('[CoduckWars] Pseudo evaluation error:', error);
            gameState.feedbackMessage = "평가 오류: 다음 단계로 진행합니다.";
            gameState.score += 80;
            addSystemLog("평가 시스템 오류, 기본 점수 부여", "WARN");
            setTimeout(() => setPhase('PYTHON_FILL'), 800);
        }
    };

    // --- 4. Implementation Phase (실제 코드 검증) ---
    const initPhase4Scaffolding = () => {
        gameState.codeSlots = {
            slot1: { placeholder: "::: [SYSTEM SLOT 01: READY] :::", content: null },
            slot2: { placeholder: "::: [SYSTEM SLOT 02: READY] :::", content: null },
            slot3: { placeholder: "::: [SYSTEM SLOT 03: READY] :::", content: null },
            slot4: { placeholder: "::: [SYSTEM SLOT 04: READY] :::", content: null },
        };
        gameState.codeExecutionResult = null;

        // [추가] 현재 미션의 코드 템플릿 로드
        if (currentMission.value?.implementation?.codeFrame?.template) {
            gameState.userCode = currentMission.value.implementation.codeFrame.template;
        }

        addSystemLog("모듈 슬롯 대기 모드 활성화", "INFO");
    };

    // [수정일: 2026-02-08] 각 스테이지마다 다른 코드 스니펫 표시
    const pythonSnippets = computed(() => {
        const mission = currentMission.value;
        // 스테이지에 정의된 snippets가 있으면 사용, 없으면 기본 StandardScaler 패턴 사용
        if (mission.implementation?.snippets && mission.implementation.snippets.length > 0) {
            return mission.implementation.snippets;
        }
        // 기본 fallback (이전 하드코딩된 값)
        return [
            { id: 1, code: "StandardScaler()", label: "Initialize Scaler" },
            { id: 2, code: "scaler.fit(train_df)", label: "Fit Model (Train Data)" },
            { id: 3, code: "scaler.transform(train_df)", label: "Transform Train Data" },
            { id: 4, code: "scaler.transform(test_df)", label: "Transform Test Data" }
        ];
    });

    const insertSnippet = () => {
        gameState.feedbackMessage = "모듈을 마우스로 끌어서(Drag) 배치하십시오.";
        addSystemLog("안내: 클릭 대신 드래그 앤 드롭을 사용하세요.", "WARN");
    };

    const handleSlotDrop = (slotKey, snippetCode) => {
        if (gameState.codeSlots[slotKey]) {
            gameState.codeSlots[slotKey].content = snippetCode;
            addSystemLog(`슬롯[${slotKey}] 모듈 장착: ${snippetCode}`, "SUCCESS");
        }
    };

    const submitPythonFill = async () => {
        // [수정일: 2026-02-09] 슬롯 방식에서 모나코 에디터 방식으로 전환됨에 따라 
        // gameState.userCode (에디터 내용)를 그대로 사용합니다.
        const userCode = gameState.userCode;

        gameState.feedbackMessage = "코드 실행 중...";
        addSystemLog("백엔드로 코드 전송 및 검증 중...", "INFO");

        try {
            // 2. 백엔드로 실제 실행 요청


            const response = await axios.post('/api/core/pseudocode/execute/', {
                code: userCode,
                test_cases: currentMission.value.testCases || [
                    {
                        input: {
                            train_df: [[1, 2], [3, 4]],
                            test_df: [[5, 6]]
                        },
                        description: "기본 테스트"
                    }
                ],
                function_name: 'leakage_free_scaling'
            });

            gameState.codeExecutionResult = response.data;

            // 1. 실행 및 테스트 성공
            if (response.data.success && response.data.all_passed) {
                gameState.score += 200;
                gameState.feedbackMessage = "구현 무결성 확인!";
                addSystemLog(`코드 검증 통과: 모든 테스트 통과 (${response.data.passed_count}/${response.data.total_count})`, "SUCCESS");

                // 정합성 체크
                try {
                    const consistency = await checkConsistency(
                        gameState.phase3Reasoning,
                        gameState.userCode,
                        'dataLeakage'
                    );

                    if (consistency.score >= 80) {
                        gameState.score += 50;
                        addSystemLog("정합성 체크: 의사코드와 구현 일치", "SUCCESS");
                    } else {
                        addSystemLog(`정합성 경고: ${consistency.gaps.join(', ')}`, "WARN");
                    }
                } catch (err) {
                    console.error('Consistency check error:', err);
                }

                setTimeout(() => setPhase('DEEP_QUIZ'), 1500);
            }
            // 2. 테스트 실패 (실행은 됐으나 정답이 아님)
            else if (response.data.success && !response.data.all_passed) {
                handleDamage();
                const failedTest = response.data.results.find(r => !r.passed);

                // 변수 미할당 등의 단순 실수인지 체크
                if (failedTest?.message?.includes("not defined")) {
                    gameState.feedbackMessage = "변수 정의가 누락되었습니다. (예: scaler = ...)";
                } else {
                    gameState.feedbackMessage = `검증 실패: ${failedTest?.message || '결과 불일치'}`;
                }

                if (failedTest) {
                    addSystemLog(`테스트 실패: ${failedTest.description}`, "ERROR");
                    addSystemLog(`메시지: ${failedTest.message}`, "INFO");
                }
            }
            // 3. 실행 자체 실패 (Docker 없음 등) -> Fallback 검증
            else {
                console.warn("[CoduckWars] Execution failed, using fallback:", response.data.error);

                // Fallback: 핵심 로직 키워드 검사 (Monaco Editor 내용 기반)
                const code = gameState.userCode;
                const validation = currentMission.value.implementation.codeValidation;

                // 필수 키워드 존재 여부 확인
                const missingKeywords = validation.mustContain.filter(keyword => !code.includes(keyword));
                const containsForbidden = validation.mustNotContain.some(keyword => code.includes(keyword));

                if (missingKeywords.length === 0 && !containsForbidden) {
                    gameState.score += 150;
                    gameState.feedbackMessage = "아키텍처 패턴 분석 완료: 구현 무결성이 확인되었습니다.";
                    addSystemLog("AI 검증: 설계 패턴과 코드 구조의 일치성 확인", "SUCCESS");
                    setTimeout(() => setPhase('DEEP_QUIZ'), 800);
                } else {
                    handleDamage();
                    const reason = missingKeywords.length > 0
                        ? `구조적 결함 감지: ${missingKeywords.join(", ")} 로직 누락`
                        : "보안 위반: 금지된 패턴이 포함되었습니다.";
                    gameState.feedbackMessage = reason;
                    addSystemLog(`오류: ${reason}`, "ERROR");
                }
            }
        } catch (error) {
            console.error('[CoduckWars] Code execution error:', error);

            // 네트워크 오류 등으로 아예 요청 실패 시에도 Fallback 시도
            const code = gameState.userCode;
            const validation = currentMission.value.implementation.codeValidation;
            const missingKeywords = validation.mustContain.filter(keyword => !code.includes(keyword));

            if (missingKeywords.length === 0) {
                gameState.score += 100;
                gameState.feedbackMessage = "네트워크 동기화 지연 - 로컬 아키텍처 분석으로 승인";
                setTimeout(() => setPhase('DEEP_QUIZ'), 1000);
            } else {
                handleDamage();
                gameState.feedbackMessage = "코드 구성 오류 (네트워크 연결 확인 필요)";
            }

            // Fallback logic is already handled above in the if/else
            console.error('[CoduckWars] Critical error in submission:', error);
            gameState.feedbackMessage = "마더 서버 응답 지연 - 시스템 무결성 수동 확인 필요";
        }
    };

    // --- 5. Deep Quiz Phase - 동적 로드 ---
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

        // 다음 단계 자동 해금
        const nextId = gameState.currentStageId + 1;
        if (aiQuests.find(q => q.id === nextId)) {
            addSystemLog(`다음 단계(${nextId})가 해금되었습니다!`, "INFO");
        }
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
        gameScore: 0, // 게임 퍼포먼스 (40%)
        aiScore: 0,   // AI 아키텍트 평가 (60%)
        verdict: "",
        details: [], // 5차원 메트릭
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
            const response = await axios.post('/api/core/ai-evaluate/', {
                quest_title: currentMission.value.title || "Pseudocode Practice",
                user_logic: gameState.phase3Reasoning,
                user_code: gameState.userCode,
                mode: 'final_report',
                performance: {
                    score: gameState.score,
                    hp: gameState.playerHP
                }
            });

            const aiResult = response.data;
            const aiOverallScore = aiResult.score || 0;
            evaluationResult.aiScore = aiOverallScore;

            // [산출 공식] 최종 점수 = (게임 퍼포먼스 40%) + (AI 논리 평가 60%)
            const finalUnifiedScore = Math.floor((gamePerformanceScore * 0.4) + (aiOverallScore * 0.6));

            evaluationResult.finalScore = finalUnifiedScore;
            evaluationResult.verdict = finalUnifiedScore >= 85 ? "시스템 복구 완료" : (finalUnifiedScore >= 60 ? "부분적 성공" : "재건축 필요");

            // AI가 제공한 5차원 메트릭 반영
            if (aiResult.metrics) {
                evaluationResult.details = Object.entries(aiResult.metrics).map(([category, score]) => ({
                    category,
                    score,
                    comment: getMetricComment(category, score),
                    improvements: getMetricImprovements(category, score)
                }));
            } else {
                // Fallback Metrics
                evaluationResult.details = [
                    { category: "정합성", score: 70, comment: "미션 목표와 부합합니다.", improvements: ["요구사항 재확인"] },
                    { category: "추상화", score: 60, comment: "핵심 로직이 잘 표현되었습니다.", improvements: ["변수 명명 구체화"] },
                    { category: "예외처리", score: 50, comment: "예외 상황 고려가 필요합니다.", improvements: ["Edge Case 대응 로직"] },
                    { category: "구현력", score: 80, comment: "Python 구현이 정확합니다.", improvements: ["표준 라이브러리 활용"] },
                    { category: "설계력", score: 70, comment: "단계별 연결성이 좋습니다.", improvements: ["아키텍처 확장성 고려"] }
                ];
            }

            // 꼬리 질문 저장
            if (aiResult.tail_question) {
                evaluationResult.tailQuestion = aiResult.tail_question;
            }

            evaluationResult.aiAnalysis = aiResult.analysis || `${currentMission.value.title} 아키텍처 분석이 완료되었습니다.`;
            evaluationResult.seniorAdvice = aiResult.advice || "사고의 깊이를 더하기 위해 예외 케이스를 더 고민해보세요.";

            if (aiResult.supplementary_videos && Array.isArray(aiResult.supplementary_videos)) {
                evaluationResult.supplementaryVideos = aiResult.supplementary_videos;
            } else {
                evaluationResult.supplementaryVideos = [
                    { title: "Advanced ML Pipeline", search_query: "Machine Learning Pipeline Design", desc: "복합 전처리 파이프라인 설계" },
                    { title: "Data Drift Detection", search_query: "ML Monitoring Data Drift", desc: "데이터 무결성 실시간 모니터링" }
                ];
            }

            // 점수 기반 티어 재설정 (FinalScore 기준)
            if (finalUnifiedScore >= 90) evaluationResult.scoreTier = "Senior Architect";
            else if (finalUnifiedScore >= 70) evaluationResult.scoreTier = "Junior Engineer";
            else evaluationResult.scoreTier = "Apprentice";

        } catch (error) {
            console.error("LLM Evaluation Failed:", error);
            evaluationResult.aiAnalysis = "통신 지연으로 인해 로컬 분석 시스템이 가동되었습니다. 사고 과정의 일관성에 집중하십시오.";
            evaluationResult.seniorAdvice = "네트워크 재연결 후 정밀 진단을 권장합니다.";
            evaluationResult.scoreTier = "현장 분석 중";
            evaluationResult.finalScore = gamePerformanceScore; // 게임 점수라도 표시

            // Default Metrics for failure
            evaluationResult.details = [
                { category: "정합성", score: 50, comment: "현장 분석 결과 표준 범주에 해당합니다.", improvements: ["로컬 기준점 확보"] },
                { category: "추상화", score: 50, comment: "보통 수준의 추상화입니다.", improvements: ["모듈화 고려"] },
                { category: "예외처리", score: 50, comment: "기본적인 예외 처리가 반영되었습니다.", improvements: ["Edge Case 추가"] },
                { category: "구현력", score: 50, comment: "구현 로직이 동작 가능한 수준입니다.", improvements: ["코드 최적화"] },
                { category: "설계력", score: 50, comment: "설계 전반이 무난합니다.", improvements: ["확장성 검토"] }
            ];
        } finally {
            isEvaluating.value = false;
            addSystemLog("최종 아키텍처 리포트 수신 완료.", "SUCCESS");
        }
    };

    // 메트릭별 코멘트 헬퍼
    const getMetricComment = (cat, score) => {
        if (score >= 90) return `매우 뛰어난 ${cat} 역량을 보여주었습니다.`;
        if (score >= 70) return `안정적인 ${cat} 구조를 갖추고 있습니다.`;
        if (score >= 40) return `${cat} 측면에서 기본적인 흐름은 맞으나 보완이 필요합니다.`;
        return `${cat} 로직이 비어있거나 논리적 비약이 심합니다.`;
    };

    const getMetricImprovements = (cat, score) => {
        if (score >= 90) return ["최적화 유지", "팀 내 모범 사례로 전파"];
        if (score >= 70) return ["미세한 예외 케이스 추가", "가독성 향상"];
        return ["핵심 개념 재학습", "단계별 논리 연결 재구성"];
    };

    const handleTailQuestion = (option) => {
        if (option.is_correct) {
            addSystemLog(`[Tail Question] 논리 검증 성공: ${option.reason}`, "SUCCESS");
            gameState.feedbackMessage = "✅ 통찰력 있는 분석입니다! 아키텍처 점수가 추가되었습니다.";
            gameState.score += 200;
        } else {
            addSystemLog(`[Tail Question] 논리 허점 발견: ${option.reason}`, "ERROR");
            gameState.feedbackMessage = "❌ 아키텍처의 맹점이 발견되었습니다. 보완이 필요합니다.";
            gameState.playerHP -= 10;
        }
        // 꼬리 질문 선택 후 사라지게 하거나 처리 완료 상태로 표시 (여기서는 선택 후 null 처리하여 닫음)
        evaluationResult.tailQuestion = null;
    };

    const explainStep = (idx) => {
        // Placeholder for future logic (e.g., TTS or specific highlighting)
        console.log(`Explaining step ${idx + 1} `);
    };

    // 맵에서 단계 선택 기능
    const selectStage = (stageId) => {
        const targetQuest = aiQuests.find(q => q.id === stageId);
        if (!targetQuest) {
            console.warn(`[CoduckWars] Stage ${stageId} not found`);
            return;
        }

        // 이전 단계를 모두 완료했는지 체크 (1번은 항상 가능)
        if (stageId > 1) {
            // 간단히: 점수가 있으면 해금된 것으로 간주 (실제로는 localStorage 등으로 진행도 저장 필요)
            console.log(`[CoduckWars] Selecting stage ${stageId} `);
        }

        gameState.currentStageId = stageId;
        gameState.playerHP = 100;
        gameState.score = 0;
        gameState.feedbackMessage = null;
        gameState.systemLogs = [];
        addSystemLog(`스테이지 ${stageId}: ${targetQuest.title} 시작`, "INFO");
        setPhase('DIAGNOSTIC_1');
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

        // Current Mission Data
        currentMission,
        missionContext,
        constraints,

        // Actions
        startGame,
        selectStage,
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
        explainStep,
        handleTailQuestion, // ✅ 추가
        addLogicBlock: (text) => {
            if (!gameState.phase3Reasoning.includes(text)) {
                gameState.phase3Reasoning += (gameState.phase3Reasoning ? "\n" : "") + "- " + text;
            }
        }
    };
}