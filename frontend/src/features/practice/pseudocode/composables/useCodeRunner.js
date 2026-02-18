import { ref, reactive, computed } from 'vue';
import axios from 'axios';
import { checkConsistency } from '../api/pseudocodeApi.js';

export function useCodeRunner(gameState, currentMission, addSystemLog, setPhase) {

    // --- State ---
    const runnerState = reactive({
        userCode: "",
        codeSlots: null,
        executionResult: null
    });

    // [2026-02-09] Task 1.1: ?먮윭 ???遺꾨쪟 ?⑥닔 (?명봽???먮윭 vs ?ъ슜???먮윭)
    const classifyError = (error) => {
        // ?ㅽ듃?뚰겕 ?먮윭 (?쒕쾭 ?묐떟 ?놁쓬)
        if (!error.response) {
            return {
                type: 'NETWORK_ERROR',
                shouldPenalize: false,
                userMessage: '?ㅽ듃?뚰겕 ?곌껐???뺤씤?댁＜?몄슂. ?좎떆 ???ㅼ떆 ?쒕룄?댁＜?몄슂.',
                logMessage: '?ㅽ듃?뚰겕 ?μ븷 媛먯? - ?ъ슜???⑤꼸???놁쓬'
            };
        }

        const status = error.response.status;

        // ?쒕쾭 ?대? ?ㅻ쪟 (500踰덈?)
        if (status >= 500) {
            return {
                type: 'SERVER_ERROR',
                shouldPenalize: false,
                userMessage: '?쒖뒪???ъ젒??以?.. ?좎떆 ???ㅼ떆 ?쒕룄?댁＜?몄슂.',
                logMessage: '?쒕쾭 ?명봽???ㅻ쪟 媛먯? - ?ъ슜???⑤꼸???놁쓬'
            };
        }

        // ?ъ슜???낅젰 ?ㅻ쪟 (400踰덈?)
        if (status >= 400 && status < 500) {
            return {
                type: 'USER_ERROR',
                shouldPenalize: true,
                userMessage: '肄붾뱶 寃利??ㅽ뙣',
                logMessage: '?ъ슜???낅젰 ?ㅻ쪟'
            };
        }

        // 湲고? ?먮윭
        return {
            type: 'UNKNOWN_ERROR',
            shouldPenalize: false,
            userMessage: '?????녿뒗 ?ㅻ쪟媛 諛쒖깮?덉뒿?덈떎.',
            logMessage: '誘몃텇瑜??먮윭'
        };
    };

    // --- Initialization ---
    const initPhase4Scaffolding = () => {
        console.log("[CodeRunner] initPhase4Scaffolding executed. Resetting state...");
        runnerState.codeSlots = {
            slot1: { placeholder: "::: [SYSTEM SLOT 01: READY] :::", content: null },
            slot2: { placeholder: "::: [SYSTEM SLOT 02: READY] :::", content: null },
            slot3: { placeholder: "::: [SYSTEM SLOT 03: READY] :::", content: null },
            slot4: { placeholder: "::: [SYSTEM SLOT 04: READY] :::", content: null },
        };
        runnerState.executionResult = null;

        // ?쒗뵆由?濡쒕뱶
        console.log("[CodeRunner] Current Mission:", currentMission.value?.id);
        const template = currentMission.value?.implementation?.codeFrame?.template;
        console.log("[CodeRunner] Template:", template);

        if (template) {
            runnerState.userCode = template;
            console.log("[CodeRunner] Set runnerState.userCode to template. Current value:", runnerState.userCode);
        } else {
            console.log("[CodeRunner] Template NOT FOUND. UserCode not reset.");
        }

        addSystemLog("紐⑤뱢 ?щ’ ?湲?紐⑤뱶 ?쒖꽦??, "INFO");
    };

    // --- Actions ---
    const insertSnippet = () => {
        gameState.feedbackMessage = "紐⑤뱢??留덉슦?ㅻ줈 ?뚯뼱??Drag) 諛곗튂?섏떗?쒖삤.";
        addSystemLog("?덈궡: ?대┃ ????쒕옒洹????쒕∼???ъ슜?섏꽭??", "WARN");
    };

    const handleSlotDrop = (slotKey, snippetCode) => {
        if (runnerState.codeSlots[slotKey]) {
            runnerState.codeSlots[slotKey].content = snippetCode;
            addSystemLog(`?щ’[${slotKey}] 紐⑤뱢 ?μ갑: ${snippetCode}`, "SUCCESS");
        }
    };

    const submitPythonFill = async (phase3Reasoning, handleDamage) => {
        const userCode = runnerState.userCode;

        gameState.feedbackMessage = "肄붾뱶 ?ㅽ뻾 以?..";
        gameState.feedbackMessage = "肄붾뱶 ?ㅽ뻾 以?..";
        addSystemLog(`諛깆뿏?쒕줈 肄붾뱶 ?꾩넚 以?.. (Length: ${userCode.length})`, "INFO");
        console.log("[CodeRunner] Submitting code:", userCode);

        try {
            console.log("[DEBUG] submitPythonFill: Requesting execution...");

            // [Security Update] Timeout reduced to use backend's 5s limit effectively
            const response = await axios.post('/api/core/pseudocode/execute/', {
                code: userCode,
                test_cases: currentMission.value.testCases || [],
                function_name: 'leakage_free_scaling'
            }, { timeout: 10000 }); // Frontend timeout slightly larger than backend (5s)

            runnerState.executionResult = response.data;

            // 1. ?ㅽ뻾 諛??뚯뒪???깃났
            if (response.data.success && response.data.all_passed) {
                gameState.score += 200;
                gameState.feedbackMessage = "援ы쁽 臾닿껐???뺤씤!";
                addSystemLog(`肄붾뱶 寃利??듦낵: 紐⑤뱺 ?뚯뒪???듦낵 (${response.data.passed_count}/${response.data.total_count})`, "SUCCESS");

                // ?뺥빀??泥댄겕
                try {
                    const consistency = await checkConsistency(
                        phase3Reasoning,
                        userCode,
                        'dataLeakage'
                    );

                    if (consistency.score >= 80) {
                        gameState.score += 50;
                        addSystemLog("?뺥빀??泥댄겕: ?섏궗肄붾뱶? 援ы쁽 ?쇱튂", "SUCCESS");
                    } else {
                        addSystemLog(`?뺥빀??寃쎄퀬: ${consistency.gaps.join(', ')}`, "WARN");
                    }
                } catch (err) {
                    console.error('Consistency check error:', err);
                }

                setTimeout(() => setPhase('DEEP_QUIZ'), 1500);
            }
            // 2. ?뚯뒪???ㅽ뙣 (?ㅽ뻾? ?먯쑝???뺣떟???꾨떂)
            else if (response.data.success && !response.data.all_passed) {
                handleDamage();
                const failedTest = response.data.results.find(r => !r.passed);

                if (failedTest?.message?.includes("not defined")) {
                    gameState.feedbackMessage = "蹂???뺤쓽媛 ?꾨씫?섏뿀?듬땲?? (?? scaler = ...)";
                } else {
                    gameState.feedbackMessage = `寃利??ㅽ뙣: ${failedTest?.message || '寃곌낵 遺덉씪移?}`;
                }

                if (failedTest) {
                    addSystemLog(`?뚯뒪???ㅽ뙣: ${failedTest.description}`, "ERROR");
                    addSystemLog(`硫붿떆吏: ${failedTest.message}`, "INFO");
                }
            }
            // 3. ?ㅽ뻾 ?먯껜 ?ㅽ뙣 (蹂댁븞 ?꾨컲 ??
            else {
                handleDamage();

                // 蹂댁븞 ?꾨컲 硫붿떆吏 泥섎━
                if (response.data.error && response.data.error.includes("蹂댁븞 ?꾨컲")) {
                    gameState.feedbackMessage = "蹂댁븞 ?꾨줈?좎퐳 ?꾨컲: ?덉슜?섏? ?딆? 紐⑤뱢 媛먯?";
                    addSystemLog(`CRITICAL: ${response.data.error}`, "ERROR");
                } else {
                    // Fallback using Keyword Check (Local validation)
                    fallbackValidation(userCode, handleDamage, setPhase);
                }
            }
        } catch (error) {
            console.error('[CodeRunner] Execution error:', error);

            // [2026-02-09] Task 1.1: ?먮윭 ???遺꾨쪟 ?곸슜
            const errorInfo = classifyError(error);

            gameState.feedbackMessage = errorInfo.userMessage;
            addSystemLog(errorInfo.logMessage, errorInfo.shouldPenalize ? "ERROR" : "WARN");

            // ?명봽???먮윭??HP 李④컧 ?놁쓬, ?ъ슜???먮윭留??⑤꼸??            if (errorInfo.shouldPenalize) {
                // ?ъ슜??肄붾뱶 臾몄젣 - fallback 寃利??쒕룄
                fallbackValidation(userCode, handleDamage, setPhase);
            } else {
                // ?명봽??臾몄젣 - HP 李④컧 ?놁씠 ?덈궡留?                console.warn(`[Infrastructure Error] ${errorInfo.type}:`, error);
            }
        }
    };

    const fallbackValidation = (code, handleDamage, setPhase) => {
        if (!currentMission.value || !currentMission.value.implementation) {
            gameState.feedbackMessage = "誘몄뀡 ?곗씠?곕? 遺덈윭?????놁뒿?덈떎.";
            return;
        }

        const validation = currentMission.value.implementation.codeValidation;
        const normalizedCode = code.replace(/\s+/g, '');
        const missingKeywords = validation.mustContain.filter(keyword => {
            const normalizedKeyword = keyword.replace(/\s+/g, '');
            return !normalizedCode.includes(normalizedKeyword);
        });
        const containsForbidden = validation.mustNotContain.some(keyword => {
            const normalizedKeyword = keyword.replace(/\s+/g, '');
            return normalizedCode.includes(normalizedKeyword);
        });

        if (missingKeywords.length === 0 && !containsForbidden) {
            gameState.score += 100;
            gameState.feedbackMessage = "?ㅽ듃?뚰겕 吏??- 濡쒖뺄 ?꾪궎?띿쿂 遺꾩꽍?쇰줈 ?뱀씤";
            addSystemLog("?좑툘 ?쒕쾭 ?묐떟 ?놁쓬: 濡쒖뺄 寃利?紐⑤뱶濡??꾪솚?섏뿬 ?뱀씤", "WARN");
            setTimeout(() => setPhase('DEEP_QUIZ'), 1000);
        } else {
            handleDamage();
            const reason = missingKeywords.length > 0
                ? `援ъ“??寃고븿 媛먯?: ${missingKeywords.join(", ")} 濡쒖쭅 ?꾨씫`
                : "蹂댁븞 ?꾨컲: 湲덉????⑦꽩???ы븿?섏뿀?듬땲??";
            gameState.feedbackMessage = reason + " (?ㅽ봽?쇱씤 紐⑤뱶)";
            addSystemLog(`?ㅻ쪟: ${reason}`, "ERROR");
        }
    };

    return {
        runnerState,
        initPhase4Scaffolding,
        insertSnippet,
        handleSlotDrop,
        submitPythonFill
    };
}
