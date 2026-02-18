/**
 * Pseudocode Practice API Service (v3)
 * 
 * 媛쒖꽑 ?ы빆:
 * - LLM 60% + Rule 40% ?섏씠釉뚮━???됯?
 * - 5李⑥썝 硫뷀듃由??ㅼ젣 怨꾩궛
 * - Tail Question ?먮룞 ?앹꽦
 * 
 * [2026-02-12] ?꾨㈃ 媛쒗렪
 */

import { PseudocodeValidator } from '../utils/PseudocodeValidator.js';
import { safeJSONParse } from '../utils/jsonParser.js';
import axios from 'axios';

// 罹먯떆
const aiCache = new Map();
const MAX_CACHE_SIZE = 100;
const CACHE_TTL = 1000 * 60 * 30; // 30遺?
// ?붿껌 以묐났 諛⑹?
const ongoingRequests = new Map();

/**
 * 李⑥썝 ?대쫫 留ㅽ븨
 */
const DIMENSION_NAMES = {
    design: '?ㅺ퀎??,
    consistency: '?뺥빀??,
    implementation: '援ы쁽??,
    edge_case: '?덉쇅泥섎━',
    abstraction: '異붿긽??
};

/**
 * 罹먯떆 愿由? */
function getCacheKey(type, data) {
    return `${type}:${JSON.stringify(data)}`;
}

function setCache(key, value) {
    if (aiCache.size >= MAX_CACHE_SIZE) {
        const firstKey = aiCache.keys().next().value;
        aiCache.delete(firstKey);
    }
    aiCache.set(key, { value, timestamp: Date.now() });
}

function getCache(key) {
    const cached = aiCache.get(key);
    if (!cached) return null;
    if (Date.now() - cached.timestamp > CACHE_TTL) {
        aiCache.delete(key);
        return null;
    }
    return cached.value;
}

/**
 * ???듭떖 ?⑥닔: 5李⑥썝 硫뷀듃由?湲곕컲 ?섏궗肄붾뱶 ?됯?
 * LLM 60% + Rule 40% ?섏씠釉뚮━?? */
export async function evaluatePseudocode5D(problem, pseudocode, userContext = null) {
    console.log('[5D Evaluation] Starting evaluation...');

    // ?덉씠??而⑤뵒??諛⑹?
    const requestKey = `5d:${problem.id}:${pseudocode.substring(0, 50)}`;
    if (ongoingRequests.has(requestKey)) {
        console.warn('[Race Prevention] Duplicate request blocked');
        return await ongoingRequests.get(requestKey);
    }

    const evaluationPromise = (async () => {
        try {
            // [2026-02-14 異붽?] STEP 0: 臾댁꽦?섑븳 ?낅젰 ?먯쿇 李⑤떒 (鍮꾩떬 AI ?몄텧 諛⑹?)
            const inputCheck = PseudocodeValidator.isMeaningfulInput(pseudocode);
            if (!inputCheck.valid) {
                console.warn('[Validation] High-Reject: Low effort input detected');

                // [2026-02-14 異붽?] ?고????먮윭 諛⑹?瑜??꾪븳 ?붾? 吏덈Ц 諛??ㅼ젣 泥?궗吏??곗씠???곕룞
                return {
                    overall_score: 0,
                    total_score_100: 0,
                    is_low_effort: true,
                    one_line_review: inputCheck.reason || "?ㅺ퀎媛 遺議깊빀?덈떎.",
                    persona_name: "?숈젣??寃ъ뒿??,
                    dimensions: {
                        design: { score: 0, basis: "痢≪젙 遺덇?", improvement: "?ㅺ퀎 ?섎룄媛 ?꾪? 蹂댁씠吏 ?딆뒿?덈떎." },
                        consistency: { score: 0, basis: "?먯튃 臾댁떆", improvement: "寃⑸━ 諛??쇨????먯튃???숈뒿?섏꽭??" },
                        implementation: { score: 0, basis: "援ы쁽 遺덇?", improvement: "?④퀎蹂??됰룞??援ъ껜?뷀븯?몄슂." },
                        edge_case: { score: 0, basis: "怨좊젮 遺議?, improvement: "?덉쇅 ?곹솴???앷컖?대낫?몄슂." },
                        abstraction: { score: 0, basis: "援ъ“ 寃곗뿬", improvement: "?쇰━??援ъ“瑜?媛뽰텛?댁빞 ?⑸땲??" }
                    },
                    converted_python: "# [李⑤떒] ?ㅺ퀎瑜??ш린?덇굅???낅젰???덈Т 遺?ㅽ븯??遺꾩꽍??以묐떒?덉뒿?덈떎.",
                    python_feedback: "?쒓났??泥?궗吏?Blueprint)??蹂듦뎄?섎ŉ ?쇰━ ?먮쫫??泥섏쓬遺???ㅼ떆 ?듯?蹂댁떆湲?諛붾엻?덈떎.",
                    tail_question: {
                        should_show: true,
                        context: "?꾪궎?띿쿂 蹂듦린 ?숈뒿",
                        question: "?ㅺ퀎 ?댁슜???덈Т 遺?ㅽ븯嫄곕굹 ?ш린?섏뀲?듬땲?? '泥?궗吏?蹂듦뎄 ?ㅼ뒿'?쇰줈 ?꾪솚?섏떆寃좎뒿?덇퉴?",
                        options: [
                            { text: "?? 湲곗큹遺???ㅼ떆 諛곗슦寃좎뒿?덈떎.", is_correct: true, reason: "蹂듦뎄 ?숈뒿 紐⑤뱶 ?쒖옉" },
                            { text: "?꾨땲?? ?ㅼ떆 ?묒꽦??蹂닿쿋?듬땲??", is_correct: false, reason: "?ъ옉??紐⑤뱶" }
                        ]
                    },
                    blueprint_steps: problem.blueprintSteps || [], // stages.js?먯꽌 異붽????④퀎蹂??ㅼ뒿 ?곗씠??                    next_phase: 'TAIL_QUESTION',
                    hybrid: true
                };
            }

            // STEP 1: 洹쒖튃 湲곕컲 ?ъ쟾 寃利?(40??留뚯젏)
            console.log('[5D Evaluation] Step 1: Rule-based validation...');
            const validator = new PseudocodeValidator(problem);
            const ruleResult = validator.validate(pseudocode);

            // 移섎챸???ㅻ쪟媛 ?덉뼱??AI ?됯???吏꾪뻾?섎릺, ?뚮옒洹??ㅼ젙 諛?媛먯젏
            let hasCriticalErrors = false;
            if (ruleResult && typeof ruleResult.passed === 'boolean') {
                hasCriticalErrors = !ruleResult.passed;
            }

            if (hasCriticalErrors) {
                console.warn('[5D Evaluation] Critical errors found, but proceeding to AI for feedback');
                // 媛먯젏 濡쒖쭅? ?꾩닠
            }

            // STEP 2: AI 5李⑥썝 ?됯? (60??留뚯젏)
            console.log('[5D Evaluation] Step 2: AI 5D metrics evaluation...');

            // 罹먯떆 ?뺤씤
            const cacheKey = getCacheKey('5d', {
                problemId: problem.id,
                pseudocodeHash: hashString(pseudocode)
            });

            const cached = getCache(cacheKey);
            if (cached) {
                console.log('[AI Cache] 5D evaluation from cache');
                return cached;
            }

            let aiResult;

            try {
                // 諛깆뿏?쒖뿉 5李⑥썝 ?됯? 諛?Python 蹂???붿껌
                // 二쇱쓽: 諛깆뿏?쒕뒗 0-100???ㅼ??쇰줈 諛섑솚?쒕떎怨?媛??                const response = await axios.post('/api/core/pseudocode/evaluate-5d', {
                    quest_id: problem.id,
                    quest_title: problem.title || problem.missionObjective,
                    pseudocode,
                    validation_rules: problem.validation,
                    rule_result: {
                        score: ruleResult.score,
                        concepts: Array.from(ruleResult.details.concepts || []),
                        warnings: ruleResult.warnings
                    },
                    // [2026-02-12] 吏꾨떒 ?④퀎 ?듬? ?곗씠??異붽? ?≪떊
                    user_diagnostic: userContext,
                    // [STEP 3] Python 蹂???붿껌 ?뚮옒洹?異붽?
                    request_python_conversion: true
                }, { timeout: 45000 }); // ??꾩븘??45珥덈줈 ?곗옣 (蹂???쒓컙 怨좊젮)

                aiResult = response.data;
                console.log('[5D Evaluation] AI response received:', aiResult.overall_score);

            } catch (error) {
                console.error('[AI Evaluation Error]', error.message);

                // Fallback: 洹쒖튃 湲곕컲?쇰줈 5李⑥썝 ?앹꽦
                console.log('[5D Evaluation] Fallback to rule-based dimensions');
                aiResult = {
                    overall_score: Math.round(ruleResult.score * 0.85),
                    dimensions: generateRuleBasedDimensions(ruleResult, pseudocode),
                    strengths: ruleResult.details.structure?.feedback?.filter(f => f.includes('??)) || [],
                    weaknesses: ruleResult.warnings,
                    tail_question: null,
                    converted_python: "# [?ㅻ쪟] AI 遺꾩꽍 以??쒓컙 珥덇낵媛 諛쒖깮?덉뒿?덈떎.\n# 猷?湲곕컲 ?먯닔濡??곗꽑 ?됯?瑜?吏꾪뻾?⑸땲??",
                    python_feedback: "?섏궗肄붾뱶???듭떖 ?ㅼ썙??寃⑸━, 湲곗??? ?쇨???瑜??ы븿?덈뒗吏 ?뺤씤??二쇱꽭??"
                };
            }

            // STEP 3: ?먯닔 ?듯빀 (2026-02-14 ?섏젙: 紐⑤뱺 沅뚰븳 ?쒕쾭 ?뚯닔)
            // ?쒕쾭?먯꽌 怨꾩궛???꾧껐???먯닔瑜??ъ슜?⑸땲??
            const combinedScore = aiResult.total_score_100 || 0;
            const ruleScoreScaled = aiResult.score_breakdown?.rule_score_15 || 0;
            const aiScoreScaled = aiResult.score_breakdown?.ai_score_85 || 0;

            console.log('[5D Evaluation] Server calculated scores:', {
                rule_raw: aiResult.score_breakdown?.rule_raw_100,
                rule_scaled_15: ruleScoreScaled,
                ai_scaled_85: aiScoreScaled,
                total: combinedScore,
                hasCriticalErrors
            });

            // STEP 4: Tail Question ?앹꽦 (80??誘몃쭔 ??
            const tailQuestion = generateTailQuestion(aiResult.dimensions, combinedScore, problem);

            // STEP 5: ?ㅼ쓬 ?④퀎 寃곗젙
            // 80???댁긽 -> DEEP_QUIZ
            // 80??誘몃쭔 -> TAIL_QUESTION
            const nextPhase = combinedScore >= 80 ? 'DEEP_QUIZ' : 'TAIL_QUESTION';

            // 移섎챸???ㅻ쪟媛 ?덉뿀?ㅻ㈃ 湲곕낯?곸쑝濡?TAIL_QUESTION 沅뚯옣
            // ?? ?ъ슜?먭? ?낅젰???ш린??'is_low_effort' ?곹깭?쇰㈃ 蹂듦린 吏덈Ц?????곗꽑??            let finalTailQuestion = tailQuestion;
            if (hasCriticalErrors && !aiResult.is_low_effort) {
                const firstError = ruleResult.criticalErrors[0]?.message || "?꾩닔 媛쒕뀗 ?꾨씫";
                finalTailQuestion = {
                    should_show: true,
                    reason: "洹쒖튃 ?꾨컲 (Rule Critical Error)",
                    question: `?ㅺ퀎?먯꽌 移섎챸?곸씤 臾몄젣媛 諛쒓껄?섏뿀?듬땲?? "${firstError}". ?대? ?닿껐?섍린 ?꾪빐 ?대뼡 ?섏젙???꾩슂?좉퉴??`,
                    hint: "臾몄젣 議곌굔???ㅼ떆 ??踰?瑗쇨세???쎌뼱蹂댁꽭??",
                    options: [
                        { text: "?? ?섏젙?섍쿋?듬땲??", is_correct: true, reason: "洹쒖튃 以???꾩슂" },
                        { text: "?꾨땲?? ?대?濡?吏꾪뻾?⑸땲??", is_correct: false, reason: "洹쒖튃 ?꾨컲 ??媛먯젏 ?붿씤" }
                    ]
                };
            }

            // [STEP 4-1] AI媛 吏곸젒 ?앹꽦??吏덈Ц(tail_question ?먮뒗 deep_dive)???덈떎硫??곗꽑 ?몄텧
            // 諛깆뿏?쒖쓽 is_low_effort 紐⑤뱶 ??묒슜
            if (aiResult.tail_question && aiResult.tail_question.question) {
                finalTailQuestion = {
                    ...aiResult.tail_question,
                    should_show: true,
                    // 諛깆뿏?쒖뿉?????뺤떇???ㅻ? ???덉쑝誘濡?留ㅽ븨 蹂댁셿
                    options: (aiResult.tail_question.options || []).map(opt => ({
                        text: opt.text,
                        is_correct: opt.is_correct ?? opt.correct ?? false,
                        reason: opt.reason ?? opt.feedback ?? (opt.is_correct ? '?뺣떟?낅땲??' : '?ㅻ떟?낅땲??')
                    }))
                };
            } else if ((!hasCriticalErrors || aiResult.deep_dive?.question) && aiResult.deep_dive && aiResult.deep_dive.question) {
                finalTailQuestion = {
                    should_show: true,
                    reason: aiResult.is_low_effort ? "?꾪궎?띿쿂 蹂듦린 ?숈뒿" : "?꾪궎?띿쿂 ?ы솕 寃利?,
                    question: aiResult.deep_dive.question,
                    hint: aiResult.python_feedback || "?쒓났??紐⑤쾾 ?듭븞(泥?궗吏???蹂닿퀬 ?쇰━瑜?遺꾩꽍??蹂댁꽭??",
                    options: (aiResult.deep_dive.options || []).map(opt => ({
                        text: opt.text,
                        is_correct: opt.is_correct ?? opt.correct ?? false,
                        reason: opt.reason ?? opt.feedback ?? (opt.is_correct ? '?뺣떟?낅땲??' : '?ㅻ떟?낅땲??')
                    }))
                };
            }

            const result = {
                overall_score: combinedScore,
                rule_score: ruleScoreScaled,
                ai_score: aiScoreScaled,
                dimensions: aiResult.dimensions, // ?댁젣 12???ㅼ???                grade: getGrade(combinedScore),
                strengths: aiResult.strengths || [],
                weaknesses: [...(aiResult.weaknesses || []), ...(ruleResult.criticalErrors.map(e => e.message))],
                tail_question: finalTailQuestion,
                next_phase: hasCriticalErrors ? 'TAIL_QUESTION' : nextPhase,
                hybrid: true,
                fallback: false,
                // ??Python 蹂??寃곌낵 ?ы븿
                converted_python: aiResult.converted_python || "",
                python_feedback: aiResult.python_feedback || "",
                // ???ш린/臾댁꽦???묐떟 ?뚮옒洹?                is_low_effort: aiResult.is_low_effort || false,
                // ??諛깆뿏?쒖뿉???앹꽦??議곗뼵 留ㅽ븨
                senior_advice: aiResult.senior_advice || "",
                // ??[2026-02-14] 諛깆뿏?쒖뿉???앹꽦???섎Ⅴ?뚮굹, 珥앺룊, ?좏뒠釉?異붿쿇 ?곸긽 留ㅽ븨
                persona_name: aiResult.persona_name || "遺꾩꽍 以묒씤 ?꾪궎?랁듃",
                one_line_review: aiResult.one_line_review || "?꾨컲?곸쑝濡??묓샇???ㅺ퀎?낅땲??",
                one_point_lesson: aiResult.one_point_lesson || "寃⑸━ ?섏??????믪뿬蹂댁꽭??",
                // ???숈쟻 Deep Dive ?ы븿
                deep_dive: aiResult.deep_dive || null,
                recommended_videos: aiResult.recommended_videos || getRecommendedVideos(aiResult.dimensions, problem)
            };

            // 罹먯떆 ???            setCache(cacheKey, result);

            return result;

        } finally {
            ongoingRequests.delete(requestKey);
        }
    })();

    ongoingRequests.set(requestKey, evaluationPromise);
    return await evaluationPromise;
}

/**
 * Fallback: 洹쒖튃 湲곕컲?쇰줈 5李⑥썝 ?먯닔 ?앹꽦
 */
export async function generatePseudocodeDeepDiveQuestions(problem, pseudocode) {
    // 罹먯떆 ?뺤씤
    const cacheKey = getCacheKey('questions', {
        problemId: problem.id,
        pseudocodeHash: pseudocode.substring(0, 100)
    });

    const cached = getCache(cacheKey);
    if (cached) {
        console.log('[AI Cache] Questions from cache');
        return cached;
    }

    const systemPrompt = `You are an experienced technical interviewer.
Generate 3 insightful follow-up questions to assess deeper understanding.

Categories:
1. Logic Understanding - why they chose this approach
2. Edge Cases - how they handle exceptions
3. Optimization - time/space complexity awareness`;

    const userPrompt = `Problem: ${problem?.title || 'Algorithm Problem'}
Student's pseudocode:
${pseudocode}

Generate 3 questions (one per category).
Format as JSON array:
[
  {"category": "Logic Understanding", "question": "..."},
  {"category": "Edge Cases", "question": "..."},
  {"category": "Optimization", "question": "..."}
]`;

    try {
        const response = await axios.post('/api/core/ai-proxy/', {
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userPrompt }
            ],
            max_tokens: 400,
            temperature: 0.8
        });

        // ??1踰??닿껐: ?덉쟾??JSON ?뚯떛
        const responseData = response.data.content || response.data;
        const questions = typeof responseData === 'string' ? safeJSONParse(responseData, null) : responseData;

        if (Array.isArray(questions) && questions.length > 0) {
            // 罹먯떆 ???            setCache(cacheKey, questions);
            return questions;
        }

        throw new Error('Invalid JSON response');

    } catch (error) {
        console.error('Question generation failed:', error.message);

        // Fallback 吏덈Ц
        const fallback = [
            {
                category: 'Logic Understanding',
                question: '???뚭퀬由ъ쬁???듭떖 ?꾩씠?붿뼱瑜???臾몄옣?쇰줈 ?ㅻ챸?댁＜?몄슂.'
            },
            {
                category: 'Edge Cases',
                question: '?낅젰 ?곗씠?곌? 鍮꾩뼱?덇굅???덉긽怨??ㅻⅨ ?뺤떇?????대뼸寃?泥섎━?섎굹??'
            },
            {
                category: 'Optimization',
                question: '???뚭퀬由ъ쬁???쒓컙 蹂듭옟?꾨뒗 ?대뼸寃??섎ŉ, 媛쒖꽑?????덈뒗 遺遺꾩씠 ?덈굹??'
            }
        ];

        return fallback;
    }
}

/**
 * [NEW] 諛깆뿏??吏?ν삎 ?먯씠?꾪듃 ?몄텧 (Coduck Wizard)
 * ?ъ슜?먯쓽 ?꾨왂怨??쒖빟?ы빆???ы븿?섏뿬 ?뺣? 遺꾩꽍???섑뻾?⑸땲??
 */
export async function runPseudocodeAgent(params) {
    const {
        user_logic,
        quest_title,
        quest_description,
        selected_strategy,
        constraints
    } = params;

    try {
        const response = await axios.post('/api/core/pseudo-agent/', {
            user_logic,
            quest_title,
            quest_description,
            selected_strategy,
            constraints
        });
        return response.data;
    } catch (error) {
        console.error('Pseudocode Agent Error:', error);
        throw error;
    }
}

/**
 * 理쒖쥌 醫낇빀 ?됯? (?섏궗肄붾뱶 + 硫댁젒 ?듬?)
 * ??4踰??닿껐: Phase 3 寃곌낵 ?ъ궗??(罹먯떛)
 */
export async function evaluatePseudocode(problem, pseudocode, deepDiveQnA, phase3Result = null) {
    // ??Phase 3 寃곌낵 ?ъ궗??(以묐났 AI ?몄텧 諛⑹?)
    let validationResult;

    if (phase3Result) {
        console.log('[Cache] Reusing Phase 3 validation result');
        validationResult = {
            score: phase3Result.score,
            passed: phase3Result.passed,
            criticalErrors: phase3Result.criticalErrors,
            details: phase3Result.details,
            warnings: phase3Result.improvements
        };
    } else {
        // Phase 3 ?놁씠 吏곸젒 ?몄텧??寃쎌슦
        const validator = new PseudocodeValidator(problem);
        validationResult = validator.validate(pseudocode);
    }

    // ?섏궗肄붾뱶 ?먯닔: 50??留뚯젏?쇰줈 ?섏궛
    const pseudocodeScore = Math.round(validationResult.score * 0.5);

    // 2. 硫댁젒 ?듬? ?됯? (媛꾨떒???대━?ㅽ떛)
    const deepDiveArray = Array.isArray(deepDiveQnA) ? deepDiveQnA : [];

    let interviewScore = 0;
    const questionAnalysis = [];

    for (const qa of deepDiveArray) {
        const answer = qa.answer || '';
        const wordCount = answer.split(/\s+/).length;

        let qScore = 0;
        let feedback = '';

        if (wordCount === 0) {
            qScore = 0;
            feedback = '?듬????놁뒿?덈떎.';
        } else if (wordCount < 10) {
            qScore = 5;
            feedback = '?덈Т 吏㏃뒿?덈떎. ??援ъ껜?곸쑝濡??ㅻ챸?대낫?몄슂.';
        } else if (wordCount < 30) {
            qScore = 10;
            feedback = '湲곕낯 媛쒕뀗? ?덉?留????먯꽭???ㅻ챸???꾩슂?⑸땲??';
        } else {
            const hasTechTerms = /(?뚭퀬由ъ쬁|蹂듭옟??理쒖쟻???곗씠?곌뎄議??쒓컙|怨듦컙|?⑥쑉|?깅뒫)/i.test(answer);
            qScore = hasTechTerms ? 15 : 12;
            feedback = hasTechTerms
                ? '援ъ껜?곸씠怨?湲곗닠?곸씤 ?듬??낅땲??'
                : '醫뗭? ?듬??낅땲?? 湲곗닠 ?⑹뼱瑜?異붽??섎㈃ ??醫뗪쿋?듬땲??';
        }

        interviewScore += qScore;
        questionAnalysis.push({
            question: qa.question,
            category: qa.category,
            userAnswer: answer,
            score: qScore,
            feedback
        });
    }

    interviewScore = Math.min(50, interviewScore);

    // 3. 理쒖쥌 ?듯빀
    const totalScore = pseudocodeScore + interviewScore;

    let grade;
    if (totalScore >= 85) {
        grade = 'excellent';
    } else if (totalScore >= 70) {
        grade = 'good';
    } else if (totalScore >= 50) {
        grade = 'needs-improvement';
    } else {
        grade = 'poor';
    }

    return {
        totalScore,
        pseudocodeScore,
        interviewScore,
        grade,
        questionAnalysis,
        isPassed: totalScore >= 70
    };
}

function generateRuleBasedDimensions(ruleResult, pseudocode) {
    const baseScore = ruleResult.score; // 0-100
    const concepts = Array.from(ruleResult.details.concepts || []);

    // 85??留뚯젏 湲곗? 媛?媛以묒튂
    const scale = 0.85;

    return {
        design: {
            score: Math.round((concepts.length >= 4 ? 25 : 15) * scale),
            basis: concepts.length >= 4 ? '?듭떖 ?④퀎 援ъ꽦 ?붿냼 ?ы븿' : '?ㅺ퀎 援ъ꽦 ?붿냼 ?쇰? ?꾨씫',
            improvement: '?꾩쿂由?諛??숈뒿 ?먮쫫??紐낇솗???섏꽭??'
        },
        consistency: {
            score: Math.round((ruleResult.passed ? 20 : 10) * scale),
            basis: ruleResult.passed ? '?곗씠???꾩닔 諛⑹? ?먯튃 以?? : '援먯감 ?ㅼ뿼 媛?μ꽦 諛쒓껄',
            improvement: '遺꾪븷怨?蹂?섏쓽 ?쒖꽌瑜??ㅼ떆 ?뺤씤?섏꽭??'
        },
        implementation: {
            score: Math.round((baseScore >= 70 ? 10 : 5) * scale),
            basis: '媛?낆꽦 諛??쇰━ ?꾧컻 ?섏? 湲곕컲',
            improvement: '??援ъ껜?곸씤 ?숈옉???묒꽦?섏꽭??'
        },
        edge_case: {
            score: Math.round((/?덉쇅|寃利?泥댄겕|?뺤씤|validation|check|error/i.test(pseudocode) ? 15 : 5) * scale),
            basis: /?덉쇅|寃利?泥댄겕/i.test(pseudocode) ? '?덉쇅 泥섎━ ?ㅼ썙???ы븿' : '?덉쇅 泥섎━ 濡쒖쭅 遺??,
            improvement: '?곗씠??寃利??④퀎瑜?異붽??섏꽭??(?? IF ?곗씠?곌? None THEN ?덉쇅 諛쒖깮)'
        },
        abstraction: {
            score: Math.round((/IF.*THEN/i.test(pseudocode) ? 15 : 8) * scale),
            basis: /IF.*THEN/i.test(pseudocode) ? '議곌굔-?됰룞 援ъ“ ?ъ슜' : '?⑥닚 ?섏뿴??援ъ“',
            improvement: 'IF-THEN 援ъ“濡??쒖뒪???꾪궎?띿쿂瑜??쒗쁽??蹂댁꽭??'
        }
    };
}

const CONCEPTUAL_FALLBACKS = {
    // ?슜 誘몄뀡 1 & 2: Data Leakage / Security
    leakage: [
        {
            question: "?묒꽦?섏떊 濡쒖쭅?먯꽌 '?곗씠???꾩닔(Data Leakage)'瑜?諛⑹??섍린 ?꾪빐 媛??二쇱쓽?댁빞 ???④퀎??臾댁뾿?멸???",
            options: [
                { text: "Train ?곗씠?곗뿉留?fit???곸슜?섍퀬 Test ?곗씠?곗뿉???곸슜?섏? ?딅뒗??", is_correct: true, reason: "Test ?곗씠???뺣낫媛 ?숈뒿???ы븿?섎㈃ ?깅뒫??怨쇰??됯??⑸땲??" },
                { text: "紐⑤뱺 ?곗씠??Train+Test)瑜??⑹퀜????踰덉뿉 fit ?쒗궓??", is_correct: false, reason: "?닿쾬???꾪삎?곸씤 ?곗씠???꾩닔 ?곹솴?낅땲??" }
            ]
        },
        {
            question: "?쒓퀎??Time-series) ?곗씠??蹂댁븞 ?뱁꽣?먯꽌 誘몃옒 ?뺣낫瑜?蹂댄샇?섍린 ?꾪븳 媛???щ컮瑜?遺꾪븷 諛⑹떇??",
            options: [
                { text: "怨쇨굅? 誘몃옒瑜??쒖젏 湲곗??쇰줈 ?섎늻??Time-based Split???ъ슜?쒕떎.", is_correct: true, reason: "怨쇨굅 ?뺣낫濡??숈뒿?섍퀬 誘몃옒瑜??덉륫?섎뒗 寃껋씠 ?ㅼ젣 ?곹솴怨??쇱튂?⑸땲??" },
                { text: "?곗씠?곗쓽 ?쒖꽌瑜?臾댁옉?꾨줈 ?욎? ???쒕뜡?섍쾶 ?섎늿??Shuffle).", is_correct: false, reason: "誘몃옒???뺣낫媛 怨쇨굅 ?숈뒿???ы븿?섏뼱 '?寃??꾩닔'媛 諛쒖깮?⑸땲??" }
            ]
        }
    ],
    // ?슜 誘몄뀡 3: Bias Control / Skew
    skew: [
        {
            question: "?숈뒿 ?섍꼍(Training)怨??꾩닠 ?섍꼍(Serving)???곗씠??遺꾪룷 李⑥씠(Skew)瑜?諛⑹??섍린 ?꾪븳 ?듭떖 ?꾨왂??",
            options: [
                { text: "?숈뒿怨??쒕튃 ???숈씪???꾩쿂由??뚯씠?꾨씪??Function)??怨듭슜?쇰줈 ?ъ슜?쒕떎.", is_correct: true, reason: "濡쒖쭅????1%留??щ씪???덉륫 ?깅뒫??移섎챸?곸씤 ?쒓끝??諛쒖깮?⑸땲??" },
                { text: "?쒕튃 ?섍꼍???뱀꽦??留욎떠 ?ㅼ떆媛꾩쑝濡??꾩쿂由?濡쒖쭅???곕줈 ?쒖옉?쒕떎.", is_correct: false, reason: "?닿쾬??諛붾줈 '?숈뒿-?쒕튃 遺덉씪移?Skew)'瑜??좊컻?섎뒗 二쇱썝?몄엯?덈떎." }
            ]
        }
    ],
    // ?슜 誘몄뀡 4: Evaluation / Policy
    policy: [
        {
            question: "鍮꾩쫰?덉뒪 由ъ뒪?ш? ???곹솴(?? 吏덈퀝 吏꾨떒)?먯꽌 紐⑤뜽???꾧퀎媛?Threshold)???ㅼ젙?섎뒗 ?щ컮瑜??꾪궎?띿쿂???먮떒??",
            options: [
                { text: "誘명깘吏(False Negative) 由ъ뒪?щ? 以꾩씠湲??꾪빐 ?꾧퀎媛믪쓣 ??텛???ы쁽??Recall)???믪씤??", is_correct: true, reason: "?꾪뿕 媛먯?媛 ?곗꽑???쒖뒪?쒖뿉?쒕뒗 ?뺣??꾨낫???ы쁽?⑥씠 ?꾨왂?곸쑝濡???以묒슂?⑸땲??" },
                { text: "?쒖뒪???좊ː?꾨? ?꾪빐 ??긽 ?꾧퀎媛?0.5瑜??좎??쒕떎.", is_correct: false, reason: "鍮꾩쫰?덉뒪 鍮꾩슜(?ㅽ뙋 鍮꾩슜)??怨좊젮?섏? ?딆? 湲곌퀎???먮떒?낅땲??" }
            ]
        }
    ],
    // ?슜 湲고? 湲곕낯 李⑥썝蹂??댁쫰 (Fallback of fallback)
    abstraction: [
        {
            question: "?섏궗肄붾뱶??異붿긽???섏????믪씠湲??꾪빐, ?곸꽭 援ы쁽 肄붾뱶瑜??섏뿴?섎뒗 寃껊낫????沅뚯옣?섎뒗 諛⑹떇??",
            options: [
                { text: "?쇰━???좏썑 愿怨꾨? ?섑??대뒗 ?ㅼ썙??IF-THEN, STEP)瑜?湲곕컲?쇰줈 ?묒꽦?쒕떎.", is_correct: true, reason: "?섏궗肄붾뱶??援ъ껜?곸씤 肄붾뱶蹂대떎 ?쒖뒪?쒖쓽 '?ㅺ퀎 ?섎룄'瑜?蹂댁뿬以섏빞 ?⑸땲??" },
                { text: "?뚯씠??臾몃쾿??理쒕????욎뼱??援ъ껜?곸쑝濡??묒꽦?쒕떎.", is_correct: false, reason: "洹멸쾬? ?⑥닚??肄붾뱶 珥덉븞?댁? ?ㅺ퀎?꾧? ?꾨떃?덈떎." }
            ]
        }
    ]
};

function generateTailQuestion(dimensions, overallScore, problem = null) {
    if (overallScore >= 80) {
        return {
            should_show: false,
            reason: "?먯닔媛 異⑸텇???믪븘 tail question 遺덊븘??
        };
    }

    // 誘몄뀡 移댄뀒怨좊━ ?앸퀎 (二쇱젣蹂?吏덈Ц 留ㅼ묶??
    const category = problem?.category?.toLowerCase() || '';
    const missionId = problem?.id || 0;

    // 媛???쏀븳 李⑥썝 李얘린
    const dimEntries = Object.entries(dimensions);
    const weakestDim = dimEntries.sort((a, b) => a[1].score - b[1].score)[0];

    // 硫뷀? ?쇰뱶諛??꾪꽣留?(?섎? ?녿뒗 ?쇰뱶諛??쒓굅)
    const isGenericIssue = (issue) => {
        if (!issue) return true;
        const metaKeywords = ['吏㏃뒿?덈떎', '遺議깊빀?덈떎', '湲몄씠', '鍮꾩뼱', '?낅젰', '?섏궗肄붾뱶'];
        return metaKeywords.some(k => issue.includes(k)) || issue.length < 5;
    };

    if (weakestDim) {
        const [dimKey, dimData] = weakestDim;
        const dimName = DIMENSION_NAMES[dimKey] || dimKey;

        // ?ㅼ젣 媛쒕뀗 吏덈Ц???꾩슂???곹솴?몄? 泥댄겕
        if (isGenericIssue(dimData.specific_issue)) {
            // 1?쒖쐞: 誘몄뀡 二쇱젣??留욌뒗 ? ?좏깮
            let pool = null;
            if (missionId === 1 || missionId === 2 || category.includes('leakage') || category.includes('security')) pool = CONCEPTUAL_FALLBACKS.leakage;
            else if (missionId === 3 || category.includes('skew') || category.includes('bias')) pool = CONCEPTUAL_FALLBACKS.skew;
            else if (missionId === 4 || category.includes('policy') || category.includes('evaluation')) pool = CONCEPTUAL_FALLBACKS.policy;

            // 2?쒖쐞: 李⑥썝蹂??대갚
            if (!pool) pool = CONCEPTUAL_FALLBACKS[dimKey] || CONCEPTUAL_FALLBACKS.leakage;

            const fallback = pool[Math.floor(Math.random() * pool.length)];

            return {
                should_show: true,
                reason: `${dimName} ?곸뿭 媛쒕뀗 蹂댁븞 ?꾩슂`,
                question: fallback.question,
                hint: "?대떦 ?꾨찓?몄쓽 ?듭떖 ?ㅺ퀎 ?먯튃?낅땲??",
                options: fallback.options
            };
        }

        // AI 吏덈Ц??議댁옱??寃쎌슦 媛怨?        return {
            should_show: true,
            reason: `${dimName} ?먯닔 ??쓬 (${Math.round(dimData.score)}??`,
            question: dimData.specific_issue,
            hint: dimData.improvement || '湲곗닠???뺣??⑥쓣 ?뺣낫?섏꽭??',
            options: [
                { text: dimData.improvement || '濡쒖쭅??蹂댁셿?섍쿋?듬땲??', is_correct: true, reason: "?곴레?곸씤 媛?대뱶 ?섏슜" },
                { text: "?꾩옱 ?ㅺ퀎瑜??좎??섍쿋?듬땲??", is_correct: false, reason: "蹂댁셿???꾩슂???ㅺ퀎 ?덉젏?낅땲??" }
            ]
        };
    }

    // ?뺣낫 ?꾨Т ??理쒖쥌 ?대갚
    const finalFallback = CONCEPTUAL_FALLBACKS.leakage[0];
    return {
        should_show: true,
        reason: "?쇰━ 寃利??꾩슂",
        question: finalFallback.question,
        hint: "?꾪궎?띿쿂??湲곕낯 臾닿껐??寃利앹엯?덈떎.",
        options: finalFallback.options
    };
}

/**
 * ?깃툒 寃곗젙
 */
function getGrade(score) {
    if (score >= 85) return 'excellent';
    if (score >= 70) return 'good';
    if (score >= 50) return 'fair';
    return 'needs-improvement';
}

/**
 * ?벟 [2026-02-13] ?꾪궎?랁듃 ?숈뒿 ?쇱씠釉뚮윭由?(YouTube)
 * 媛쒕뀗蹂??꾩꽑??媛뺤쓽 ?곸긽 ?곗씠?곕쿋?댁뒪
 */
const YOUTUBE_LIBRARY = {
    leakage: [
        { id: 'fSytzGwwBVw', title: 'Cross Validation (StatQuest)', desc: '援먯감 寃利앹쓽 ?듭떖 ?먮━瑜??쎄퀬 ?щ??덇쾶 諛곗썙遊낅땲?? ?곗씠???꾩닔瑜?諛⑹??섎뒗 ?щ컮瑜?遺꾪븷 ?꾨왂??湲곗큹?낅땲??', reason: '?곗씠??遺꾪븷怨?寃利??꾨왂??湲곕낯湲곕? ?먭??대낫?몄슂.' },
        { id: 'A88rDEf-pfk', title: 'Standardization (StatQuest)', desc: '?곗씠???쒖??붿쓽 媛쒕뀗怨??щ컮瑜??곸슜 ?쒖젏???뚯븘遊낅땲?? fit/transform ?쒖꽌媛 ??以묒슂?쒖? ?댄빐?????덉뒿?덈떎.', reason: '?꾩쿂由??뚯씠?꾨씪?몄뿉??fit/transform ?쒖꽌? ?곗씠???꾩닔 諛⑹? ?먮━瑜??뺤씤?섏꽭??' }
    ],
    skew: [
        { id: 'EuBBz3bI-aA', title: 'Bias and Variance (StatQuest)', desc: '?명뼢-遺꾩궛 ?몃젅?대뱶?ㅽ봽???듭떖??吏곴??곸쑝濡??ㅻ챸?⑸땲?? 紐⑤뜽 ?쇰컲?붿? ?섍꼍 李⑥씠瑜??댄빐?섎뒗 湲곗큹?낅땲??', reason: '紐⑤뜽 ?쇰컲???깅뒫怨??숈뒿-?쒕튃 ?섍꼍 李⑥씠瑜??댄빐?섎뒗 湲곕낯湲곗엯?덈떎.' }
    ],
    exception_handling: [
        { id: 'ZUqGMDppEDs', title: 'Python Exception Handling (NeuralNine)', desc: 'Python?먯꽌 寃ш퀬???먮윭 ?몃뱾留??⑦꽩???ㅼ뒿?⑸땲?? try/except瑜??쒖슜??諛⑹뼱??肄붾뵫 ?꾨왂??諛곗썙蹂댁꽭??', reason: '?먯? 耳?댁뒪 諛?鍮꾩젙???곗씠?곗뿉 ???諛⑹뼱 濡쒖쭅??遺議깊빀?덈떎.' }
    ],
    architecture: [
        { id: 'TMuno5RZNeE', title: 'SOLID Principles (Uncle Bob)', desc: '媛앹껜吏???ㅺ퀎??5? ?먯튃(SOLID)??李쎌떆??Robert C. Martin??吏곸젒 ?ㅻ챸?⑸땲??', reason: '?꾩껜?곸씤 而댄룷?뚰듃 媛꾩쓽 梨낆엫 遺꾨━(Separation of Concerns)瑜??곌뎄?대낫?몄슂.' }
    ],
    abstraction: [
        { id: 'pTB0EiLXUC8', title: 'OOP Simplified (Programming with Mosh)', desc: '媛앹껜吏???꾨줈洹몃옒諛띿쓽 異붿긽??媛쒕뀗???쎄퀬 紐낇솗?섍쾶 ?ㅻ챸?⑸땲??', reason: '?섎뱶肄붾뵫??濡쒖쭅???쇰컲?뷀븯???뺤옣?깆쓣 ?믪뿬蹂댁꽭??' }
    ]
};

/**
 * ?쎌젏 湲곕컲 ?좏뒠釉??곸긽 異붿쿇 濡쒖쭅
 */
function getRecommendedVideos(dimensions, problem = null) {
    const dimEntries = Object.entries(dimensions);
    // 媛???먯닔媛 ??? 李⑥썝 李얘린 (?먮낯 100??湲곗? 80??誘몃쭔 ???
    // 二쇱쓽: ???쒖젏?먯꽌 d.score??12??留뚯젏?쇰줈 ?ㅼ??쇰쭅???곹깭?대?濡?original_score ?ъ슜
    const weakDims = dimEntries
        .filter(([_, d]) => (d.original_score ?? d.score) < 80)
        .sort((a, b) => (a[1].original_score ?? a[1].score) - (b[1].original_score ?? b[1].score));

    const recommendations = [];
    const usedIds = new Set();

    // 1. 誘몄뀡蹂??뱀닔 ?쎌젏 (Leakage ?? ?곗꽑 泥댄겕
    const category = problem?.category?.toLowerCase() || '';
    if (category.includes('leakage') || category.includes('security')) {
        YOUTUBE_LIBRARY.leakage.forEach(v => {
            if (!usedIds.has(v.id)) { recommendations.push(v); usedIds.add(v.id); }
        });
    }

    // 2. 媛???쏀븳 李⑥썝 1~2媛?異붽?
    weakDims.slice(0, 2).forEach(([key, _]) => {
        const pool = YOUTUBE_LIBRARY[key] || [];
        pool.forEach(v => {
            if (recommendations.length < 3 && !usedIds.has(v.id)) {
                recommendations.push(v);
                usedIds.add(v.id);
            }
        });
    });

    // 3. 留뚯빟 異붿쿇???덈Т ?곸쑝硫?湲곕낯 ?꾪궎?띿쿂 ?곸긽 異붽?
    if (recommendations.length < 1) {
        recommendations.push(YOUTUBE_LIBRARY.architecture[0]);
    }

    return recommendations.slice(0, 2); // 理쒕? 2媛?異붿쿇
}

/**
 * 媛꾨떒???댁떆 ?⑥닔 (罹먯떆 ?ㅼ슜)
 */
function hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return Math.abs(hash).toString(36);
}

/**
 * AI 硫섑넗 肄붿묶 ?앹꽦
 */
export async function generateSeniorAdvice(evaluation, gameState) {
    console.log('[Senior Advice] Generating...');

    // 罹먯떆 ?뺤씤
    const cacheKey = getCacheKey('advice', {
        score: evaluation.overall_score,
        hp: gameState.playerHP
    });

    const cached = getCache(cacheKey);
    if (cached) {
        console.log('[AI Cache] Senior advice from cache');
        return cached;
    }

    const dimEntries = Object.entries(evaluation.dimensions);
    const weakestDim = dimEntries.sort((a, b) => a[1].score - b[1].score)[0];
    const strongestDim = dimEntries.sort((a, b) => b[1].score - a[1].score)[0];

    const systemPrompt = `?뱀떊? 20??寃쎈젰???쒕땲???꾪궎?랁듃?낅땲??
?꾨같?먭쾶 ?곕쑜?섏?留??뺥솗???쇰뱶諛깆쓣 ?쒓났?섏꽭??

洹쒖튃:
- 100???대궡濡?媛꾧껐?섍쾶 ?묒꽦
- 援ъ껜?곸씤 媛쒖꽑???쒖떆
- 醫낇빀 ?먯닔媛 50??誘몃쭔?대㈃ '?꾧꺽??寃쎄퀬? 洹쇰낯?곸씤 ?ъ옉??沅뚭퀬' ?꾩＜濡??묒꽦
- 醫낇빀 ?먯닔媛 50???댁긽 70??誘몃쭔?대㈃ '寃⑸젮? 援ъ껜?곸씤 蹂댁셿???쒖떆' ?꾩＜濡??묒꽦
- 醫낇빀 ?먯닔媛 80???댁긽?대㈃ '寃⑸젮? ?ы솕 議곗뼵' ?꾩＜濡??묒꽦
- 留먰닾: ?쒕땲???꾪궎?랁듃?ㅼ슫 ?꾨Ц?곸씠怨??좊ː媛??덈뒗 ?댁“ (臾댁“嫄댁쟻??鍮꾨궃 湲덉?)`;

    const userPrompt = `?숈깮 ?됯? 寃곌낵:
- 醫낇빀 ?먯닔: ${evaluation.overall_score}/100
- 媛뺤젏: ${DIMENSION_NAMES[strongestDim[0]]} (${Math.round(strongestDim[1].score)}??
  ??${strongestDim[1].basis}
- ?쎌젏: ${DIMENSION_NAMES[weakestDim[0]]} (${Math.round(weakestDim[1].score)}??
  ??${weakestDim[1].specific_issue || '媛쒖꽑 ?꾩슂'}

?쒕땲??愿?먯쓽 議곗뼵???묒꽦?섏꽭??`;

    try {
        const response = await axios.post('/api/core/ai-proxy/', {
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userPrompt }
            ],
            max_tokens: 200,
            temperature: 0.7
        }, { timeout: 10000 });

        const advice = response.data.content?.trim() ||
            (evaluation.overall_score >= 50
                ? "?뚮????쒕룄??듬땲?? ?ㅼ쟾?먯꽌 ?곸슜?섎ŉ 怨꾩냽 諛쒖쟾?쒖폒 ?섍??몄슂."
                : "濡쒖쭅???ㅺ퀎 ?섎룄媛 紐낇솗?섏? ?딆뒿?덈떎. 援ъ꽦 ?붿냼瑜??ㅼ떆 寃?좏븯怨?堉덈?遺???ㅼ떆 ?묒꽦?대낫?몄슂.");

        // 罹먯떆 ???        setCache(cacheKey, advice);

        return advice;

    } catch (error) {
        console.error('[Senior Advice Error]', error.message);

        // Fallback
        if (evaluation.overall_score >= 80) {
            return `${DIMENSION_NAMES[strongestDim[0]]} ?곸뿭???뱁엳 ?곗닔?⑸땲?? ${DIMENSION_NAMES[weakestDim[0]]} 遺遺꾩쓣 蹂댁셿?섎㈃ ?꾨꼍???ㅺ퀎媛 ??寃껋엯?덈떎.`;
        } else {
            return `湲곕낯湲곕뒗 媛뽰텛?덉뒿?덈떎. ${DIMENSION_NAMES[weakestDim[0]]} ?곸뿭??吏묒쨷?곸쑝濡?蹂닿컯?섏꽭??`;
        }
    }
}

/**
 * 罹먯떆 愿由? */
export function clearAICache() {
    aiCache.clear();
    console.log('[AI Cache] Cleared');
}

export function getAICacheStats() {
    return {
        size: aiCache.size,
        maxSize: MAX_CACHE_SIZE,
        ttl: CACHE_TTL
    };
}

/**
 * ??[2026-02-12] ?좉퇋: ?쒖닠??吏꾨떒 臾몄젣 AI ?됯?
 */
export async function evaluateDiagnosticAnswer(question, userAnswer) {
    const rubric = question.evaluationRubric || {};
    const isOrdering = question.type === 'ORDERING';

    let systemPrompt = `?뱀떊? ?곗씠??怨쇳븰 援먯쑁 ?꾨Ц媛?낅땲??
?숈깮??吏꾨떒 臾몄젣 ?듬????됯??섍퀬 JSON?쇰줈 ?묐떟?섏꽭??

# ?뺣떟 ?쇰━
${rubric.correctAnswer || "?곗씠???꾩닔 李⑥씠 ?ㅻ챸"}

# 猷⑤툕由?- ?ㅼ썙?? ${rubric.keyKeywords?.join(', ') || "leakage, fit"}
- 梨꾩젏 湲곗?: ${JSON.stringify(rubric.gradingCriteria || [])}

# 異쒕젰 ?뺤떇 (JSON)
{
  "score": 0-100,
  "is_correct": boolean,
  "feedback": "?꾨Ц?곸씠怨?移쒖젅???쇰뱶諛?(?쒓?, 150???대궡)",
  "analysis": "?대뼡 遺遺꾩씠 留욊퀬 ??몃뒗吏?????媛꾨왂??遺꾩꽍"
}`;

    if (isOrdering) {
        systemPrompt = `?뱀떊? ?곗씠??怨쇳븰 援먯쑁 ?꾨Ц媛?낅땲??
?숈깮???쒖텧??'?뺣젹 ?쒖꽌'???쇰━????뱀꽦???됯??섍퀬 JSON?쇰줈 ?묐떟?섏꽭??

# ?뺣떟 ?쒖꽌 ?ㅻ챸
${rubric.correctAnswer || ""}
${rubric.modelAnswerExplanation || ""}

# 梨꾩젏 媛?대뱶
- ?숈깮? ?щ윭 媛쒖쓽 ?④퀎(options)瑜??뱀젙 ?쒖꽌濡??뺣젹?덉뒿?덈떎.
- ?⑥닚???쒖꽌媛 ??몃떎怨?媛먯젏?섍린蹂대떎, 洹??쒖꽌媛 媛吏????덈뒗 ?꾪뿕???? ?곗씠???꾩닔 ?먯? ?ㅽ뙣)??吏?곹빐 二쇱꽭??
- 紐⑤뱺 ?쒖꽌媛 ?꾨꼍?섎㈃ 100?? ?쇰━???덉젏???덈떎硫?洹몄뿉 鍮꾨???媛먯젏?섏꽭??

# 異쒕젰 ?뺤떇 (JSON)
{
  "score": 0-100,
  "is_correct": boolean,
  "feedback": "?쒖꽌??????쇰━???쇰뱶諛?(?쒓?, 150???대궡)",
  "analysis": "?????쒖꽌媛 ?꾪뿕?섍굅??鍮꾪슚?⑥쟻?몄???????④퀎蹂?遺꾩꽍"
}`;
    }

    try {
        const response = await axios.post('/api/core/ai-proxy/', {
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: systemPrompt },
                {
                    role: 'user', content: isOrdering
                        ? `?숈깮???쒖텧???뺣젹 寃곌낵: ${userAnswer}\n\n???쒖꽌媛 ?쇰━?곸씤吏 遺꾩꽍??二쇱꽭??`
                        : `?숈깮???듬?: "${userAnswer}"`
                }
            ],
            response_format: { type: "json_object" }
        }, { timeout: 15000 });

        let result = response.data.content;
        if (typeof result === 'string') {
            result = safeJSONParse(result);
        }
        return result || { score: 50, is_correct: false, feedback: "遺꾩꽍???꾨즺?섏? 紐삵뻽?듬땲??" };

    } catch (error) {
        console.error('[Diagnostic Evaluation Error]', error);
        return {
            score: 70,
            is_correct: true,
            feedback: "吏꾩???異붾줎 ?쒕룄??媛먯궗?쒕┰?덈떎. (?쒕쾭 ?곌껐 吏?곗쑝濡?湲곕낯 ?듦낵 泥섎━)"
        };
    }
}

/**
 * ?뺥빀??泥댄겕 (Reasoning vs Implementation)
 * [2026-02-12] Added to support useCodeRunner.js
 */
export async function checkConsistency(reasoning, implementation, type = 'general') {
    console.log('[Consistency Check] Starting...', { type });

    // 罹먯떆 ?뺤씤
    const cacheKey = getCacheKey('consistency', {
        reasoningHash: hashString(reasoning),
        implHash: hashString(implementation),
        type
    });

    const cached = getCache(cacheKey);
    if (cached) {
        console.log('[AI Cache] Consistency check from cache');
        return cached;
    }

    try {
        const response = await axios.post('/api/core/ai-proxy/', {
            model: 'gpt-4o-mini',
            messages: [
                {
                    role: 'system',
                    content: `You are a code consistency checker.
Analyze if the implementation matches the reasoning.
Type: ${type}
Return JSON:
{
  "score": 0-100,
  "gaps": ["list of specific inconsistencies"]
}`
                },
                {
                    role: 'user',
                    content: `Reasoning: ${reasoning}\n\nImplementation:\n${implementation}`
                }
            ],
            response_format: { type: "json_object" }
        }, { timeout: 10000 });

        let result = response.data.content;
        if (typeof result === 'string') {
            result = safeJSONParse(result);
        }

        if (!result) result = { score: 50, gaps: ["AI ?묐떟 ?뚯떛 ?ㅽ뙣"] };

        // 罹먯떆 ???        setCache(cacheKey, result);

        return result;

    } catch (error) {
        console.error('[Consistency Check Error]', error);
        // Fail-safe: ?듦낵 泥섎━ (?ъ슜???먮쫫 諛⑺빐 諛⑹?)
        return {
            score: 100,
            gaps: []
        };
    }
}
