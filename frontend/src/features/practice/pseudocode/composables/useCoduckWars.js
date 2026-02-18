/**
 * useCoduckWars.js - Refactored (Restored and Fixed)
 * 
 * 媛쒖꽑 ?ы빆:
 * - 5李⑥썝 硫뷀듃由?湲곕컲 ?됯? ?곸슜
 * - Tail Question 遺꾧린 濡쒖쭅 異붽?
 * - 吏꾨떒 ?④퀎 ?곕룞 (diagnosticQuestion, submitDiagnostic)
 * - ?먮룞 ?뚰듃 ??대㉧ ?섎룞??(?ъ슜???붿껌)
 * 
 * [2026-02-14] 癒몄? ?댁뒋 諛??고????먮윭(TypeError) ?꾩쟾 ?닿껐
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

    // 以묐났 ?붿껌 李⑤떒
    const isProcessing = ref(false);

    // UI State
    const isGuideOpen = ref(false);
    const selectedGuideIdx = ref(0);
    const showModelAnswer = ref(false);
    const isEvaluating = ref(false); // [NEW] ?됯? 以??곹깭

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

        // ?대? ?듬? ?꾨즺???곹깭?먯꽌 ?몄텧?섎㈃ ?ㅼ쓬 ?④퀎濡?吏꾪뻾
        if (gameState.isDiagnosticAnswered) {
            moveNextDiagnosticStep();
            return;
        }

        try {
            // [媛앷???泥섎━]
            if (diagnosticQuestion.value.type === 'CHOICE') {
                const idx = answer;
                const opt = diagnosticQuestion.value.options[idx];

                gameState.diagnosticAnswerIdx = idx;
                gameState.isDiagnosticAnswered = true;

                if (opt.correct || opt.is_correct) {
                    gameState.score += 100;
                    gameState.coduckMessage = opt.feedback || '?뺥솗??媛쒕뀗 ?댄빐?낅땲??';
                    addSystemLog("?뺥솗??遺꾩꽍?낅땲?? ?ㅺ퀎 ?λ젰??利앸챸?섏뿀?듬땲??", "SUCCESS");
                } else {
                    handleDamage(15);
                    gameState.coduckMessage = `?ㅻ떟?낅땲?? ${opt.feedback || '?쇰━???덉젏??諛쒓껄?섏뿀?듬땲??'}`;
                    addSystemLog(`遺꾩꽍 ?ㅻ쪟媛 媛먯??섏뿀?듬땲??`, "WARN");
                }
                return;
            }

            // [?쒖닠??泥섎━ - 湲곗〈 濡쒖쭅 ?좎??섎릺 ?쇰뱶諛?猷⑦봽 異붽? ?꾩슂???섏젙 ?덉젙]
            isProcessing.value = true;
            addSystemLog("二쇨????듬? 遺꾩꽍 以?..", "INFO");

            const result = await evaluateDiagnosticAnswer(diagnosticQuestion.value, answer.text || answer);

            gameState.diagnosticAnswer = answer.text || answer;
            gameState.diagnosticScores.push(result.score || 0);

            if (result.is_correct) {
                gameState.coduckMessage = `?뚮??⑸땲?? ${result.feedback || '?ㅺ퀎 ?λ젰??利앸챸?섏뿀?듬땲??'}`;
                addSystemLog("?뺥솗??遺꾩꽍?낅땲??", "SUCCESS");
            } else {
                handleDamage(10);
                gameState.coduckMessage = `蹂댁땐???꾩슂?⑸땲?? ${result.feedback || '?쇰━???덉젏??諛쒓껄?섏뿀?듬땲??'}`;
                addSystemLog(`遺꾩꽍 ?ㅻ쪟: ${result.feedback}`, "WARN");
            }

            gameState.isDiagnosticAnswered = true;
        } catch (error) {
            console.error("Diagnostic Evaluation Error:", error);
            addSystemLog("吏꾨떒 ?됯? 以??ㅻ쪟", "ERROR");
            moveNextDiagnosticStep();
        } finally {
            isProcessing.value = false;
        }
    };

    const moveNextDiagnosticStep = () => {
        gameState.isDiagnosticAnswered = false;
        gameState.diagnosticAnswerIdx = null;
        gameState.coduckMessage = "?ㅼ쓬 ?곗씠??遺꾩꽍???쒖옉?⑸땲??";

        const totalQuestions = currentMission.value?.interviewQuestions?.length || 0;
        if (gameState.diagnosticStep < totalQuestions - 1) {
            gameState.diagnosticStep++;
        } else {
            setPhase('PSEUDO_WRITE');
        }
    };

    // --- Checklist (洹쒖튃 湲곕컲 ?ㅼ떆媛??쇰뱶諛? ---
    const ruleChecklist = ref([
        {
            id: 'check_isolation',
            label: '寃⑸━ (Isolation) ?ы븿',
            patterns: [/寃⑸━|遺꾨━|?섎늻|?섎닎|isolation|split/i],
            hint: "?곗씠?곕? ?섎늻??'寃⑸━' 媛쒕뀗???ы븿?섏뼱???⑸땲??",
            completed: false
        },
        {
            id: 'check_anchor',
            label: '湲곗???(Anchor) ?뺤쓽',
            patterns: [/湲곗???湲곗?|?듦퀎??fit|anchor|?숈뒿/i],
            hint: "?듦퀎?됱쓣 異붿텧????곸씤 '湲곗?????紐낆떆?섏뼱???⑸땲??",
            completed: false
        },
        {
            id: 'check_consistency',
            label: '?쇨???(Consistency) ?뺣낫',
            patterns: [/?쇨????숈씪|蹂??consistency|transform/i],
            hint: "?숈뒿怨??댁쁺 ?섍꼍??'?쇨??? ?덈뒗 蹂??諛⑹떇???ы븿?섏뼱???⑸땲??",
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

    // [2026-02-14 ?섏젙] ?섎룞 ?뚰듃 ?꾪솚?쇰줈 ?명븳 ??대㉧ 鍮꾪솢?깊솕
    const startHintTimer = () => { };
    const resetHintTimer = () => { };

    // ?ㅼ떆媛??뚰듃 ?ㅻ━ 愿???곹깭
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
                title: "?맋 [蹂듦린 ?숈뒿 ?쒖븞]",
                pool: ["?ㅺ퀎媛 留됰쭑?섏떊媛?? [?ы솕 遺꾩꽍 ?쒖옉]???뚮윭 泥?궗吏꾩쓣 ?뺤씤?대낫?몄슂."]
            },
            isolation: {
                title: "?맋 [寃⑸━ ?좊룄]",
                pool: ["?곗씠??遺꾪븷 ?쒖젏???곸젅?쒖? ?ㅼ떆 ?쒕쾲 ?앷컖?대낫?몄슂."]
            },
            anchor: {
                title: "?맋 [湲곗???援먯젙 ?뚰듃]",
                pool: ["?뺣떟吏(Test)媛 湲곗????ㅼ젙???ы븿?섏????딆븯?섏슂?"]
            },
            consistency: {
                title: "?맋 [?쇨???媛뺤“ ?뚰듃]",
                pool: ["?숈뒿 ???쇰뜕 ?숈씪??蹂??諛⑹떇???뚯뒪?몄뿉???곸슜?덈굹??"]
            },
            abstraction: {
                title: "?맋 [援ъ“???낅젮 ?뚰듃]",
                pool: ["?ㅺ퀎???멸낵愿怨꾧? ???쒕윭?섎룄濡?臾몄옣???ㅻ벉?대낫?몄슂."]
            }
        };

        const setHint = (typeKey) => {
            const entry = HINT_DATA[typeKey];
            if (!entry) return;
            const randomSentence = entry.pool[Math.floor(Math.random() * entry.pool.length)];
            dynamicHintMessage.value = `${entry.title}\n\n${randomSentence}`;
        };

        const surrenderKeywords = /??s*紐⑤Ⅴ寃좊떎|紐⑤쫫|紐곕씪|?대졄???대젮???ш린|?섎뱾??i;
        if (surrenderKeywords.test(code) || (code.trim().length > 0 && code.trim().length < 5)) {
            setHint('surrender');
            return;
        }

        const isolationKeywords = /split|遺꾪븷|?섎늻湲?履쇨컻湲?寃⑸━/i;
        if (!isolationKeywords.test(code)) {
            setHint('isolation');
            return;
        }

        const anchorError = /fit\s*\(\s*(total|all|df|?꾩껜|?뚯뒪??test)/i.test(code);
        if (anchorError) {
            setHint('anchor');
            return;
        }

        const consistencyKeywords = /transform|蹂???곸슜|?숈씪?섍쾶|?묎컳??i;
        if (!consistencyKeywords.test(code)) {
            setHint('consistency');
            return;
        }

        if (code.replace(/\s/g, '').length < 40) {
            setHint('abstraction');
            return;
        }

        dynamicHintMessage.value = "?맋 [?ㅺ퀎 ?꾨즺]\n\n?꾨꼍??媛源뚯슫 ?ㅺ퀎?낅땲?? ?뱀씤???붿껌??蹂댁꽭??";
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
        supplementaryVideos: [] // CoduckWars.vue UI ?곕룞??    });

    const submitPseudo = async () => {
        if (isProcessing.value || !canSubmitPseudo.value) return;
        isProcessing.value = true;

        try {
            gameState.feedbackMessage = "遺꾩꽍 以?..";
            const diagnosticContext = {
                answers: [gameState.diagnosticAnswer],
                scores: gameState.diagnosticScores
            };

            const evaluation = await evaluatePseudocode5D(currentMission.value, gameState.phase3Reasoning, diagnosticContext);
            Object.assign(evaluationResult, evaluation);
            evaluationResult.finalScore = evaluation.overall_score;
            // [2026-02-14] UI ?명솚?깆쓣 ?꾪빐 異붿쿇 ?곸긽 留ㅽ븨
            evaluationResult.supplementaryVideos = evaluation.recommended_videos || [];

            setPhase('PYTHON_VISUALIZATION');
        } catch (error) {
            console.error(error);
            addSystemLog("?됯? ?쒖뒪???쇱떆 ?μ븷", "ERROR");
        } finally {
            isProcessing.value = false;
        }
    };

    const handleReSubmitPseudo = submitPseudo;

    const retryDesign = () => {
        setPhase('PSEUDO_WRITE');
        addSystemLog("?ㅺ퀎 蹂댁셿 紐⑤뱶 ?쒖꽦??, "INFO");
    };

    /**
     * Python ?쒓컖???④퀎?먯꽌 '?ㅼ쓬(DEEP DIVE 吏꾩엯)' ?대┃ ??     */
    const handlePythonVisualizationNext = () => {
        // [2026-02-14 ?섏젙] 臾댁꽦???낅젰 蹂듦뎄 紐⑤뱶(is_low_effort)??寃쎌슦 MCQ ?듬? 泥댄겕 ?고쉶
        if (!gameState.isMcqAnswered && !evaluationResult.is_low_effort) {
            addSystemLog("?꾪궎?띿쿂 寃고븿 蹂댁셿 臾몄젣瑜?癒쇱? ?꾨즺?댁＜?몄슂.", "WARN");
            return;
        }

        // 3? ?ㅻТ ?쒕굹由ъ삤 以??섎굹 ?쒕뜡 ?좊떦 (?대? ?좊떦?섏? ?딆? 寃쎌슦)
        if (!gameState.assignedScenario) {
            const scenarios = currentMission.value?.deepDiveScenarios || [];
            if (scenarios.length > 0) {
                // 臾댁옉??異붿텧
                gameState.assignedScenario = scenarios[Math.floor(Math.random() * scenarios.length)];
            }
        }

        // ?쒖닠??Deep Dive ?섏씠利덈줈 ?꾪솚
        setPhase('DEEP_DIVE_DESCRIPTIVE');
        addSystemLog(`[?ㅻТ 梨뚮┛吏] ${gameState.assignedScenario?.title} ?쒕굹由ъ삤媛 ?쒖떆?섏뿀?듬땲??`, "INFO");
    };

    /**
     * MCQ ?듬? 泥섎━ (Tail Question / Deep Quiz 怨듭슜)
     */
    const handleMcqAnswer = async (idx) => {
        const question = deepQuizQuestion.value;
        if (!question || !question.options) {
            console.error("MCQ Question data is missing.");
            return;
        }

        const selected = question.options[idx];
        gameState.isMcqAnswered = true; // ?듬? ?꾨즺 湲곕줉

        if (selected.is_correct || selected.correct) {
            gameState.score += 150;
            gameState.coduckMessage = selected.feedback || '?ㅺ퀎 寃고븿???깃났?곸쑝濡?蹂댁셿?섏뿀?듬땲??';
            addSystemLog("?곸썡???먮떒?낅땲?? ?ㅺ퀎 寃고븿???깃났?곸쑝濡?蹂댁셿?섏뿀?듬땲??", "SUCCESS");
        } else {
            handleDamage(15);
            gameState.coduckMessage = `?ㅻ떟?낅땲?? ${selected.feedback || '?꾪궎?띿쿂 臾닿껐?깆씠 ?먯긽?섏뿀?듬땲??'}`;
            addSystemLog("?먮떒 ?ㅻ쪟?낅땲?? ?꾪궎?띿쿂 臾닿껐?깆씠 ?먯긽?섏뿀?듬땲??", "WARN");
        }
    };

    /**
     * 理쒖쥌 ?ㅻТ ?쒕굹由ъ삤(?쒖닠?? ?쒖텧 泥섎━
     */
    const submitDescriptiveDeepDive = async (userAnswer) => {
        if (!userAnswer.trim() || isProcessing.value) return;

        try {
            isProcessing.value = true;
            gameState.deepDiveAnswer = userAnswer;

            addSystemLog("理쒖쥌 ?ㅻТ ?쒕굹由ъ삤 ?ㅺ퀎 遺꾩꽍 以?..", "INFO");

            // [2026-02-14 異붽?] 臾댁꽦???낅젰(Low Effort) 蹂듦뎄 ?섎젴 ?꾨즺 ???먯닔 ???蹂댁젙
            if (evaluationResult.is_low_effort) {
                evaluationResult.overall_score = 75; // 0??-> 75?먯쑝濡?蹂듦뎄
                evaluationResult.total_score_100 = 75;
                evaluationResult.persona_name = "媛곸꽦???ㅺ퀎 吏留앹깮";
                evaluationResult.one_line_review = "遺議깊븿???몄젙?섍퀬 ?앷퉴吏 ?꾪궎?띿쿂瑜?蹂듦뎄?대궦 ?덇린媛 ?뗫낫?낅땲??";

                // 媛?李⑥썝 ?먯닔??'蹂듦뎄???쇰줈 ?낅뜲?댄듃 (諛⑹궗??李⑦듃 諛섏쁺??
                const dims = evaluationResult.dimensions;
                Object.keys(dims).forEach(key => {
                    dims[key].score = 7; // 10??留뚯젏??7???섏??쇰줈 蹂듦뎄
                    dims[key].basis = "?숈뒿???듯븳 ?ㅺ퀎 蹂듦뎄 ?깃났";
                    dims[key].improvement = "?욎쑝濡쒕룄 ???ㅺ퀎 ?먯튃???딆? 留덉꽭??";
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
            addSystemLog("?ы솕 ?댁쫰 ?뺣떟! ?쒖뒪??肄붿뼱媛 媛뺥솕?섏뿀?듬땲??", "SUCCESS");
        } else {
            handleDamage(15);
            addSystemLog("?ㅻ떟?낅땲?? ?꾪궎?띿쿂 寃고븿???먯??섏뿀?듬땲??", "WARN");
        }
        setPhase('EVALUATION');
    };

    const handleTailSelection = (option) => {
        if (option.is_correct) {
            gameState.score += 100;
            addSystemLog("?쎌젏 蹂댁셿 ?꾨즺!", "SUCCESS");
            setPhase('DEEP_QUIZ');
        } else {
            handleDamage(10);
            addSystemLog("異붽? 吏덈Ц ?ㅻ떟 - ?ъ쟻???덈젴???꾩슂?⑸땲??", "WARN");
            retryDesign();
        }
    };

    const deepQuizQuestion = computed(() => {
        const aiTq = evaluationResult.tail_question;
        const aiDq = evaluationResult.deep_dive;

        // ?쒓컖???④퀎(PYTHON_VISUALIZATION)??瑗щ━ 吏덈Ц ?④퀎?먯꽌 ?곗씠??諛섑솚
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
