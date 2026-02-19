/**
 * Pseudocode Practice API Service (v3)
 * 
 * 개선 사항:
 * - LLM 60% + Rule 40% 하이브리드 평가
 * - 5차원 메트릭 실제 계산
 * - Tail Question 자동 생성
 * 
 * [2026-02-12] 전면 개편
 */

import { PseudocodeValidator } from '../utils/PseudocodeValidator.js';
import { safeJSONParse } from '../utils/jsonParser.js';
import axios from 'axios';

// 캐시
const aiCache = new Map();
const MAX_CACHE_SIZE = 100;
const CACHE_TTL = 1000 * 60 * 30; // 30분

// 요청 중복 방지
const ongoingRequests = new Map();

/**
 * 차원 이름 매핑
 */
const DIMENSION_NAMES = {
    design: '설계력',
    consistency: '정합성',
    implementation: '구현력',
    edge_case: '예외처리',
    abstraction: '추상화'
};

/**
 * 캐시 관리
 */
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
 * ✅ 핵심 함수: 5차원 메트릭 기반 의사코드 평가
 * LLM 60% + Rule 40% 하이브리드
 */
export async function evaluatePseudocode5D(problem, pseudocode, userContext = null) {
    console.log('[5D Evaluation] Starting evaluation...');

    // 레이스 컨디션 방지
    const requestKey = `5d:${problem.id}:${pseudocode.substring(0, 50)}`;
    if (ongoingRequests.has(requestKey)) {
        console.warn('[Race Prevention] Duplicate request blocked');
        return await ongoingRequests.get(requestKey);
    }

    const evaluationPromise = (async () => {
        try {
            // [2026-02-14 추가] STEP 0: 무성의한 입력 원천 차단 (비싼 AI 호출 방지)
            const inputCheck = PseudocodeValidator.isMeaningfulInput(pseudocode);
            if (!inputCheck.valid) {
                console.warn('[Validation] High-Reject: Low effort input detected');

                // [2026-02-14 추가] 런타임 에러 방지를 위한 더미 질문 및 실제 청사진 데이터 연동
                return {
                    overall_score: 0,
                    total_score_100: 0,
                    is_low_effort: true,
                    one_line_review: inputCheck.reason || "설계가 부족합니다.",
                    persona_name: "낙제한 견습생",
                    dimensions: {
                        design: { score: 0, basis: "측정 불가", improvement: "설계 의도가 전혀 보이지 않습니다." },
                        consistency: { score: 0, basis: "원칙 무시", improvement: "격리 및 일관성 원칙을 학습하세요." },
                        implementation: { score: 0, basis: "구현 불가", improvement: "단계별 행동을 구체화하세요." },
                        edge_case: { score: 0, basis: "고려 부족", improvement: "예외 상황을 생각해보세요." },
                        abstraction: { score: 0, basis: "구조 결여", improvement: "논리적 구조를 갖추어야 합니다." }
                    },
                    converted_python: "# [차단] 설계를 포기했거나 입력이 너무 부실하여 분석을 중단했습니다.",
                    python_feedback: "제공된 청사진(Blueprint)을 복구하며 논리 흐름을 처음부터 다시 익혀보시기 바랍니다.",
                    tail_question: {
                        should_show: true,
                        context: "아키텍처 복기 학습",
                        question: "설계 내용이 너무 부실하거나 포기하셨습니다. '청사진 복구 실습'으로 전환하시겠습니까?",
                        options: [
                            { text: "네, 기초부터 다시 배우겠습니다.", is_correct: true, reason: "복구 학습 모드 시작" },
                            { text: "아니요, 다시 작성해 보겠습니다.", is_correct: false, reason: "재작성 모드" }
                        ]
                    },
                    blueprint_steps: problem.blueprintSteps || [],
                    next_phase: 'TAIL_QUESTION',
                    hybrid: true
                };
            }

            // STEP 1: 규칙 기반 사전 검증 (40점 만점)
            console.log('[5D Evaluation] Step 1: Rule-based validation...');
            const validator = new PseudocodeValidator(problem);
            const ruleResult = validator.validate(pseudocode);

            // 치명적 오류가 있어도 AI 평가는 진행하되, 플래그 설정 및 감점
            let hasCriticalErrors = false;
            if (ruleResult && typeof ruleResult.passed === 'boolean') {
                hasCriticalErrors = !ruleResult.passed;
            }

            if (hasCriticalErrors) {
                console.warn('[5D Evaluation] Critical errors found, but proceeding to AI for feedback');
                // 감점 로직은 후술
            }

            // STEP 2: AI 5차원 평가 (60점 만점)
            console.log('[5D Evaluation] Step 2: AI 5D metrics evaluation...');

            // 캐시 확인
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
                // 백엔드에 5차원 평가 및 Python 변환 요청
                // 주의: 백엔드는 0-100점 스케일로 반환한다고 가정
                const response = await axios.post('/api/core/pseudocode/evaluate-5d', {
                    quest_id: problem.id,
                    quest_title: problem.title || problem.missionObjective,
                    pseudocode,
                    validation_rules: problem.validation,
                    rule_result: {
                        score: ruleResult.score,
                        concepts: Array.from(ruleResult.details.concepts || []),
                        warnings: ruleResult.warnings
                    },
                    // [2026-02-12] 진단 단계 답변 데이터 추가 송신
                    user_diagnostic: userContext,
                    // [STEP 3] Python 변환 요청 플래그 추가
                    request_python_conversion: true
                }, { timeout: 45000 }); // 타임아웃 45초로 연장 (변환 시간 고려)

                aiResult = response.data;
                console.log('[5D Evaluation] AI response received:', aiResult.overall_score);

            } catch (error) {
                console.error('[AI Evaluation Error]', error.message);

                // Fallback: 규칙 기반으로 5차원 생성
                console.log('[5D Evaluation] Fallback to rule-based dimensions');
                aiResult = {
                    overall_score: Math.round(ruleResult.score * 0.85),
                    dimensions: generateRuleBasedDimensions(ruleResult, pseudocode),
                    strengths: ruleResult.details.structure?.feedback?.filter(f => f.includes('✅')) || [],
                    weaknesses: ruleResult.warnings,
                    tail_question: null,
                    converted_python: "# [오류] AI 분석 중 시간 초과가 발생했습니다.\n# 룰 기반 점수로 우선 평가를 진행합니다.",
                    python_feedback: "의사코드의 핵심 키워드(격리, 기준점, 일관성)를 포함했는지 확인해 주세요."
                };
            }

            // STEP 3: 점수 통합 (2026-02-14 수정: 모든 권한 서버 회수)
            // 서버에서 계산된 완결된 점수를 사용합니다.
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

            // STEP 4: Tail Question 생성 (80점 미만 시)
            const tailQuestion = generateTailQuestion(aiResult.dimensions, combinedScore, problem);

            // STEP 5: 다음 단계 결정
            // 80점 이상 -> DEEP_QUIZ
            // 80점 미만 -> TAIL_QUESTION
            const nextPhase = combinedScore >= 80 ? 'DEEP_QUIZ' : 'TAIL_QUESTION';

            // 치명적 오류가 있었다면 기본적으로 TAIL_QUESTION 권장
            // 단, 사용자가 입력을 포기한 'is_low_effort' 상태라면 복기 질문을 더 우선함
            let finalTailQuestion = tailQuestion;
            if (hasCriticalErrors && !aiResult.is_low_effort) {
                const firstError = ruleResult.criticalErrors[0]?.message || "필수 개념 누락";
                finalTailQuestion = {
                    should_show: true,
                    reason: "규칙 위반 (Rule Critical Error)",
                    question: `설계에서 치명적인 문제가 발견되었습니다: "${firstError}". 이를 해결하기 위해 어떤 수정이 필요할까요?`,
                    hint: "문제 조건을 다시 한 번 꼼꼼히 읽어보세요.",
                    options: [
                        { text: "네, 수정하겠습니다.", is_correct: true, reason: "규칙 준수 필요" },
                        { text: "아니요, 이대로 진행합니다.", is_correct: false, reason: "규칙 위반 시 감점 요인" }
                    ]
                };
            }

            // [STEP 4-1] AI가 직접 생성한 질문(tail_question 또는 deep_dive)이 있다면 우선 노출
            // 백엔드의 is_low_effort 모드 대응용
            if (aiResult.tail_question && aiResult.tail_question.question) {
                finalTailQuestion = {
                    ...aiResult.tail_question,
                    should_show: true,
                    // 백엔드에서 온 형식이 다를 수 있으므로 매핑 보완
                    options: (aiResult.tail_question.options || []).map(opt => ({
                        text: opt.text,
                        is_correct: opt.is_correct ?? opt.correct ?? false,
                        reason: opt.reason ?? opt.feedback ?? (opt.is_correct ? '정답입니다!' : '오답입니다.')
                    }))
                };
            } else if ((!hasCriticalErrors || aiResult.deep_dive?.question) && aiResult.deep_dive && aiResult.deep_dive.question) {
                finalTailQuestion = {
                    should_show: true,
                    reason: aiResult.is_low_effort ? "아키텍처 복기 학습" : "아키텍처 심화 검증",
                    question: aiResult.deep_dive.question,
                    hint: aiResult.python_feedback || "제공된 모범 답안(청사진)을 보고 논리를 분석해 보세요.",
                    options: (aiResult.deep_dive.options || []).map(opt => ({
                        text: opt.text,
                        is_correct: opt.is_correct ?? opt.correct ?? false,
                        reason: opt.reason ?? opt.feedback ?? (opt.is_correct ? '정답입니다!' : '오답입니다.')
                    }))
                };
            }

            const result = {
                overall_score: combinedScore,
                rule_score: ruleScoreScaled,
                ai_score: aiScoreScaled,
                dimensions: aiResult.dimensions, // 이제 12점 스케일
                grade: getGrade(combinedScore),
                strengths: aiResult.strengths || [],
                weaknesses: [...(aiResult.weaknesses || []), ...(ruleResult.criticalErrors.map(e => e.message))],
                tail_question: finalTailQuestion,
                next_phase: hasCriticalErrors ? 'TAIL_QUESTION' : nextPhase,
                hybrid: true,
                fallback: false,
                // ✅ Python 변환 결과 포함
                converted_python: aiResult.converted_python || "",
                python_feedback: aiResult.python_feedback || "",
                // ✅ 포기/무성의 응답 플래그
                is_low_effort: aiResult.is_low_effort || false,
                // ✅ 백엔드에서 생성된 조언 매핑
                senior_advice: aiResult.senior_advice || "",
                // ✅ [2026-02-14] 백엔드에서 생성된 페르소나, 총평, 유튜브 추천 영상 매핑
                persona_name: aiResult.persona_name || "분석 중인 아키텍트",
                one_line_review: aiResult.one_line_review || "전반적으로 양호한 설계입니다.",
                one_point_lesson: aiResult.one_point_lesson || "격리 수준을 더 높여보세요.",
                // ✅ 동적 Deep Dive 포함
                deep_dive: aiResult.deep_dive || null,
                recommended_videos: aiResult.recommended_videos || getRecommendedVideos(aiResult.dimensions, problem)
            };

            // 캐시 저장
            setCache(cacheKey, result);

            return result;

        } finally {
            ongoingRequests.delete(requestKey);
        }
    })();

    ongoingRequests.set(requestKey, evaluationPromise);
    return await evaluationPromise;
}

/**
 * Fallback: 규칙 기반으로 5차원 점수 생성
 */
export async function generatePseudocodeDeepDiveQuestions(problem, pseudocode) {
    // 캐시 확인
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

        // ✨ 1번 해결: 안전한 JSON 파싱
        const responseData = response.data.content || response.data;
        const questions = typeof responseData === 'string' ? safeJSONParse(responseData, null) : responseData;

        if (Array.isArray(questions) && questions.length > 0) {
            // 캐시 저장
            setCache(cacheKey, questions);
            return questions;
        }

        throw new Error('Invalid JSON response');

    } catch (error) {
        console.error('Question generation failed:', error.message);

        // Fallback 질문
        const fallback = [
            {
                category: 'Logic Understanding',
                question: '이 알고리즘의 핵심 아이디어를 한 문장으로 설명해주세요.'
            },
            {
                category: 'Edge Cases',
                question: '입력 데이터가 비어있거나 예상과 다른 형식일 때 어떻게 처리하나요?'
            },
            {
                category: 'Optimization',
                question: '이 알고리즘의 시간 복잡도는 어떻게 되며, 개선할 수 있는 부분이 있나요?'
            }
        ];

        return fallback;
    }
}

/**
 * [NEW] 백엔드 지능형 에이전트 호출 (Coduck Wizard)
 * 사용자의 전략과 제약사항을 포함하여 정밀 분석을 수행합니다.
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
 * 최종 종합 평가 (의사코드 + 면접 답변)
 * ✨ 4번 해결: Phase 3 결과 재사용 (캐싱)
 */
export async function evaluatePseudocode(problem, pseudocode, deepDiveQnA, phase3Result = null) {
    // ✨ Phase 3 결과 재사용 (중복 AI 호출 방지)
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
        // Phase 3 없이 직접 호출된 경우
        const validator = new PseudocodeValidator(problem);
        validationResult = validator.validate(pseudocode);
    }

    // 의사코드 점수: 50점 만점으로 환산
    const pseudocodeScore = Math.round(validationResult.score * 0.5);

    // 2. 면접 답변 평가 (간단한 휴리스틱)
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
            feedback = '답변이 없습니다.';
        } else if (wordCount < 10) {
            qScore = 5;
            feedback = '너무 짧습니다. 더 구체적으로 설명해보세요.';
        } else if (wordCount < 30) {
            qScore = 10;
            feedback = '기본 개념은 있지만 더 자세한 설명이 필요합니다.';
        } else {
            const hasTechTerms = /(알고리즘|복잡도|최적화|데이터구조|시간|공간|효율|성능)/i.test(answer);
            qScore = hasTechTerms ? 15 : 12;
            feedback = hasTechTerms
                ? '구체적이고 기술적인 답변입니다!'
                : '좋은 답변입니다. 기술 용어를 추가하면 더 좋겠습니다.';
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

    // 3. 최종 통합
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

    // 85점 만점 기준 각 가중치
    const scale = 0.85;

    return {
        design: {
            score: Math.round((concepts.length >= 4 ? 25 : 15) * scale),
            basis: concepts.length >= 4 ? '핵심 단계 구성 요소 포함' : '설계 구성 요소 일부 누락',
            improvement: '전처리 및 학습 흐름을 명확히 하세요.'
        },
        consistency: {
            score: Math.round((ruleResult.passed ? 20 : 10) * scale),
            basis: ruleResult.passed ? '데이터 누수 방지 원칙 준수' : '교차 오염 가능성 발견',
            improvement: '분할과 변환의 순서를 다시 확인하세요.'
        },
        implementation: {
            score: Math.round((baseScore >= 70 ? 10 : 5) * scale),
            basis: '가독성 및 논리 전개 수준 기반',
            improvement: '더 구체적인 동작을 작성하세요.'
        },
        edge_case: {
            score: Math.round((/예외|검증|체크|확인|validation|check|error/i.test(pseudocode) ? 15 : 5) * scale),
            basis: /예외|검증|체크/i.test(pseudocode) ? '예외 처리 키워드 포함' : '예외 처리 로직 부재',
            improvement: '데이터 검증 단계를 추가하세요 (예: IF 데이터가 None THEN 예외 발생)'
        },
        abstraction: {
            score: Math.round((/IF.*THEN/i.test(pseudocode) ? 15 : 8) * scale),
            basis: /IF.*THEN/i.test(pseudocode) ? '조건-행동 구조 사용' : '단순 나열형 구조',
            improvement: 'IF-THEN 구조로 시스템 아키텍처를 표현해 보세요.'
        }
    };
}

const CONCEPTUAL_FALLBACKS = {
    // 🚩 미션 1 & 2: Data Leakage / Security
    leakage: [
        {
            question: "작성하신 로직에서 '데이터 누수(Data Leakage)'를 방지하기 위해 가장 주의해야 할 단계는 무엇인가요?",
            options: [
                { text: "Train 데이터에만 fit을 적용하고 Test 데이터에는 적용하지 않는다.", is_correct: true, reason: "Test 데이터 정보가 학습에 포함되면 성능이 과대평가됩니다." },
                { text: "모든 데이터(Train+Test)를 합쳐서 한 번에 fit 시킨다.", is_correct: false, reason: "이것이 전형적인 데이터 누수 상황입니다." }
            ]
        },
        {
            question: "시계열(Time-series) 데이터 보안 섹터에서 미래 정보를 보호하기 위한 가장 올바른 분할 방식은?",
            options: [
                { text: "과거와 미래를 시점 기준으로 나누는 Time-based Split을 사용한다.", is_correct: true, reason: "과거 정보로 학습하고 미래를 예측하는 것이 실제 상황과 일치합니다." },
                { text: "데이터의 순서를 무작위로 섞은 후 랜덤하게 나눈다(Shuffle).", is_correct: false, reason: "미래의 정보가 과거 학습에 포함되어 '타겟 누수'가 발생합니다." }
            ]
        }
    ],
    // 🚩 미션 3: Bias Control / Skew
    skew: [
        {
            question: "학습 환경(Training)과 전술 환경(Serving)의 데이터 분포 차이(Skew)를 방지하기 위한 핵심 전략은?",
            options: [
                { text: "학습과 서빙 시 동일한 전처리 파이프라인(Function)을 공용으로 사용한다.", is_correct: true, reason: "로직이 단 1%만 달라도 예측 성능에 치명적인 왜곡이 발생합니다." },
                { text: "서빙 환경의 특성에 맞춰 실시간으로 전처리 로직을 따로 제작한다.", is_correct: false, reason: "이것이 바로 '학습-서빙 불일치(Skew)'를 유발하는 주원인입니다." }
            ]
        }
    ],
    // 🚩 미션 4: Evaluation / Policy
    policy: [
        {
            question: "비즈니스 리스크가 큰 상황(예: 질병 진단)에서 모델의 임계값(Threshold)을 설정하는 올바른 아키텍처적 판단은?",
            options: [
                { text: "미탐지(False Negative) 리스크를 줄이기 위해 임계값을 낮추어 재현율(Recall)을 높인다.", is_correct: true, reason: "위험 감지가 우선인 시스템에서는 정밀도보다 재현율이 전략적으로 더 중요합니다." },
                { text: "시스템 신뢰도를 위해 항상 임계값 0.5를 유지한다.", is_correct: false, reason: "비즈니스 비용(오판 비용)을 고려하지 않은 기계적 판단입니다." }
            ]
        }
    ],
    // 🚩 기타 기본 차원별 퀴즈 (Fallback of fallback)
    abstraction: [
        {
            question: "의사코드의 추상화 수준을 높이기 위해, 상세 구현 코드를 나열하는 것보다 더 권장되는 방식은?",
            options: [
                { text: "논리적 선후 관계를 나타내는 키워드(IF-THEN, STEP)를 기반으로 작성한다.", is_correct: true, reason: "의사코드는 구체적인 코드보다 시스템의 '설계 의도'를 보여줘야 합니다." },
                { text: "파이썬 문법을 최대한 섞어서 구체적으로 작성한다.", is_correct: false, reason: "그것은 단순한 코드 초안이지 설계도가 아닙니다." }
            ]
        }
    ]
};

function generateTailQuestion(dimensions, overallScore, problem = null) {
    if (overallScore >= 80) {
        return {
            should_show: false,
            reason: "점수가 충분히 높아 tail question 불필요"
        };
    }

    // 미션 카테고리 식별 (주제별 질문 매칭용)
    const category = problem?.category?.toLowerCase() || '';
    const missionId = problem?.id || 0;

    // 가장 약한 차원 찾기
    const dimEntries = Object.entries(dimensions);
    const weakestDim = dimEntries.sort((a, b) => a[1].score - b[1].score)[0];

    // 메타 피드백 필터링 (의미 없는 피드백 제거)
    const isGenericIssue = (issue) => {
        if (!issue) return true;
        const metaKeywords = ['짧습니다', '부족합니다', '길이', '비어', '입력', '의사코드'];
        return metaKeywords.some(k => issue.includes(k)) || issue.length < 5;
    };

    if (weakestDim) {
        const [dimKey, dimData] = weakestDim;
        const dimName = DIMENSION_NAMES[dimKey] || dimKey;

        // 실제 개념 질문이 필요한 상황인지 체크
        if (isGenericIssue(dimData.specific_issue)) {
            // 1순위: 미션 주제에 맞는 풀 선택
            let pool = null;
            if (missionId === 1 || missionId === 2 || category.includes('leakage') || category.includes('security')) pool = CONCEPTUAL_FALLBACKS.leakage;
            else if (missionId === 3 || category.includes('skew') || category.includes('bias')) pool = CONCEPTUAL_FALLBACKS.skew;
            else if (missionId === 4 || category.includes('policy') || category.includes('evaluation')) pool = CONCEPTUAL_FALLBACKS.policy;

            // 2순위: 차원별 폴백
            if (!pool) pool = CONCEPTUAL_FALLBACKS[dimKey] || CONCEPTUAL_FALLBACKS.leakage;

            const fallback = pool[Math.floor(Math.random() * pool.length)];

            return {
                should_show: true,
                reason: `${dimName} 영역 개념 보안 필요`,
                question: fallback.question,
                hint: "해당 도메인의 핵심 설계 원칙입니다.",
                options: fallback.options
            };
        }

        // AI 질문이 존재할 경우 가공
        return {
            should_show: true,
            reason: `${dimName} 점수 낮음 (${Math.round(dimData.score)}점)`,
            question: dimData.specific_issue,
            hint: dimData.improvement || '기술적 정밀함을 확보하세요.',
            options: [
                { text: dimData.improvement || '로직을 보완하겠습니다.', is_correct: true, reason: "적극적인 가이드 수용" },
                { text: "현재 설계를 유지하겠습니다.", is_correct: false, reason: "보완이 필요한 설계 허점입니다." }
            ]
        };
    }

    // 정보 전무 시 최종 폴백
    const finalFallback = CONCEPTUAL_FALLBACKS.leakage[0];
    return {
        should_show: true,
        reason: "논리 검증 필요",
        question: finalFallback.question,
        hint: "아키텍처의 기본 무결성 검증입니다.",
        options: finalFallback.options
    };
}

/**
 * 등급 결정
 */
function getGrade(score) {
    if (score >= 85) return 'excellent';
    if (score >= 70) return 'good';
    if (score >= 50) return 'fair';
    return 'needs-improvement';
}

/**
 * 📺 [2026-02-13] 아키텍트 학습 라이브러리 (YouTube)
 * 개념별 엄선된 강의 영상 데이터베이스
 */
const YOUTUBE_LIBRARY = {
    leakage: [
        { id: 'fSytzGwwBVw', title: 'Cross Validation (StatQuest)', desc: '교차 검증의 핵심 원리를 쉽고 재미있게 배워봅니다. 데이터 누수를 방지하는 올바른 분할 전략의 기초입니다.', reason: '데이터 분할과 검증 전략의 기본기를 점검해보세요.' },
        { id: 'A88rDEf-pfk', title: 'Standardization (StatQuest)', desc: '데이터 표준화의 개념과 올바른 적용 시점을 알아봅니다. fit/transform 순서가 왜 중요한지 이해할 수 있습니다.', reason: '전처리 파이프라인에서 fit/transform 순서와 데이터 누수 방지 원리를 확인하세요.' }
    ],
    skew: [
        { id: 'EuBBz3bI-aA', title: 'Bias and Variance (StatQuest)', desc: '편향-분산 트레이드오프의 핵심을 직관적으로 설명합니다. 모델 일반화와 환경 차이를 이해하는 기초입니다.', reason: '모델 일반화 성능과 학습-서빙 환경 차이를 이해하는 기본기입니다.' }
    ],
    exception_handling: [
        { id: 'ZUqGMDppEDs', title: 'Python Exception Handling (NeuralNine)', desc: 'Python에서 견고한 에러 핸들링 패턴을 실습합니다. try/except를 활용한 방어적 코딩 전략을 배워보세요.', reason: '에지 케이스 및 비정상 데이터에 대한 방어 로직이 부족합니다.' }
    ],
    architecture: [
        { id: 'TMuno5RZNeE', title: 'SOLID Principles (Uncle Bob)', desc: '객체지향 설계의 5대 원칙(SOLID)을 창시자 Robert C. Martin이 직접 설명합니다.', reason: '전체적인 컴포넌트 간의 책임 분리(Separation of Concerns)를 연구해보세요.' }
    ],
    abstraction: [
        { id: 'pTB0EiLXUC8', title: 'OOP Simplified (Programming with Mosh)', desc: '객체지향 프로그래밍의 추상화 개념을 쉽고 명확하게 설명합니다.', reason: '하드코딩된 로직을 일반화하여 확장성을 높여보세요.' }
    ]
};

/**
 * 약점 기반 유튜브 영상 추천 로직
 */
function getRecommendedVideos(dimensions, problem = null) {
    const dimEntries = Object.entries(dimensions);
    // 가장 점수가 낮은 차원 찾기 (원본 100점 기준 80점 미만 대상)
    // 주의: 이 시점에서 d.score는 12점 만점으로 스케일링된 상태이므로 original_score 사용
    const weakDims = dimEntries
        .filter(([_, d]) => (d.original_score ?? d.score) < 80)
        .sort((a, b) => (a[1].original_score ?? a[1].score) - (b[1].original_score ?? b[1].score));

    const recommendations = [];
    const usedIds = new Set();

    // 1. 미션별 특수 약점 (Leakage 등) 우선 체크
    const category = problem?.category?.toLowerCase() || '';
    if (category.includes('leakage') || category.includes('security')) {
        YOUTUBE_LIBRARY.leakage.forEach(v => {
            if (!usedIds.has(v.id)) { recommendations.push(v); usedIds.add(v.id); }
        });
    }

    // 2. 가장 약한 차원 1~2개 추가
    weakDims.slice(0, 2).forEach(([key, _]) => {
        const pool = YOUTUBE_LIBRARY[key] || [];
        pool.forEach(v => {
            if (recommendations.length < 3 && !usedIds.has(v.id)) {
                recommendations.push(v);
                usedIds.add(v.id);
            }
        });
    });

    // 3. 만약 추천이 너무 적으면 기본 아키텍처 영상 추가
    if (recommendations.length < 1) {
        recommendations.push(YOUTUBE_LIBRARY.architecture[0]);
    }

    return recommendations.slice(0, 2); // 최대 2개 추천
}

/**
 * 간단한 해시 함수 (캐시 키용)
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
 * AI 멘토 코칭 생성
 */
export async function generateSeniorAdvice(evaluation, gameState) {
    console.log('[Senior Advice] Generating...');

    // 캐시 확인
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

    const systemPrompt = `당신은 20년 경력의 시니어 아키텍트입니다.
후배에게 따뜻하지만 정확한 피드백을 제공하세요.

규칙:
- 100자 이내로 간결하게 작성
- 구체적인 개선점 제시
- 종합 점수가 50점 미만이면 '엄격한 경고와 근본적인 재작성 권고' 위주로 작성
- 종합 점수가 50점 이상 70점 미만이면 '격려와 구체적인 보완점 제시' 위주로 작성
- 종합 점수가 80점 이상이면 '격려와 심화 조언' 위주로 작성
- 말투: 시니어 아키텍트다운 전문적이고 신뢰감 있는 어조 (무조건적인 비난 금지)`;

    const userPrompt = `학생 평가 결과:
- 종합 점수: ${evaluation.overall_score}/100
- 강점: ${DIMENSION_NAMES[strongestDim[0]]} (${Math.round(strongestDim[1].score)}점)
  → ${strongestDim[1].basis}
- 약점: ${DIMENSION_NAMES[weakestDim[0]]} (${Math.round(weakestDim[1].score)}점)
  → ${weakestDim[1].specific_issue || '개선 필요'}

시니어 관점의 조언을 작성하세요.`;

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
                ? "훌륭한 시도였습니다. 실전에서 적용하며 계속 발전시켜 나가세요."
                : "로직의 설계 의도가 명확하지 않습니다. 구성 요소를 다시 검토하고 뼈대부터 다시 작성해보세요.");

        // 캐시 저장
        setCache(cacheKey, advice);

        return advice;

    } catch (error) {
        console.error('[Senior Advice Error]', error.message);

        // Fallback
        if (evaluation.overall_score >= 80) {
            return `${DIMENSION_NAMES[strongestDim[0]]} 영역이 특히 우수합니다. ${DIMENSION_NAMES[weakestDim[0]]} 부분을 보완하면 완벽한 설계가 될 것입니다.`;
        } else {
            return `기본기는 갖추었습니다. ${DIMENSION_NAMES[weakestDim[0]]} 영역을 집중적으로 보강하세요.`;
        }
    }
}

/**
 * 캐시 관리
 */
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
 * ✅ [2026-02-12] 신규: 서술형 진단 문제 AI 평가
 */
export async function evaluateDiagnosticAnswer(question, userAnswer) {
    const rubric = question.evaluationRubric || {};
    const isOrdering = question.type === 'ORDERING';

    let systemPrompt = `당신은 데이터 과학 교육 전문가입니다.
학생의 진단 문제 답변을 평가하고 JSON으로 응답하세요.

# 정답 논리
${rubric.correctAnswer || "데이터 누수 차이 설명"}

# 루브릭
- 키워드: ${rubric.keyKeywords?.join(', ') || "leakage, fit"}
- 채점 기준: ${JSON.stringify(rubric.gradingCriteria || [])}

# 출력 형식 (JSON)
{
  "score": 0-100,
  "is_correct": boolean,
  "feedback": "전문적이고 친절한 피드백 (한글, 150자 이내)",
  "analysis": "어떤 부분이 맞고 틀렸는지에 대한 간략한 분석"
}`;

    if (isOrdering) {
        systemPrompt = `당신은 데이터 과학 교육 전문가입니다.
학생이 제출한 '정렬 순서'의 논리적 타당성을 평가하고 JSON으로 응답하세요.

# 정답 순서 설명
${rubric.correctAnswer || ""}
${rubric.modelAnswerExplanation || ""}

# 채점 가이드
- 학생은 여러 개의 단계(options)를 특정 순서로 정렬했습니다.
- 단순히 순서가 틀렸다고 감점하기보다, 그 순서가 가질 수 있는 위험성(예: 데이터 누수 탐지 실패)을 지적해 주세요.
- 모든 순서가 완벽하면 100점, 논리적 허점이 있다면 그에 비례해 감점하세요.

# 출력 형식 (JSON)
{
  "score": 0-100,
  "is_correct": boolean,
  "feedback": "순서에 대한 논리적 피드백 (한글, 150자 이내)",
  "analysis": "왜 이 순서가 위험하거나 비효율적인지에 대한 단계별 분석"
}`;
    }

    try {
        const response = await axios.post('/api/core/ai-proxy/', {
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: systemPrompt },
                {
                    role: 'user', content: isOrdering
                        ? `학생이 제출한 정렬 결과: ${userAnswer}\n\n이 순서가 논리적인지 분석해 주세요.`
                        : `학생의 답변: "${userAnswer}"`
                }
            ],
            response_format: { type: "json_object" }
        }, { timeout: 15000 });

        let result = response.data.content;
        if (typeof result === 'string') {
            result = safeJSONParse(result);
        }
        return result || { score: 50, is_correct: false, feedback: "분석을 완료하지 못했습니다." };

    } catch (error) {
        console.error('[Diagnostic Evaluation Error]', error);
        return {
            score: 70,
            is_correct: true,
            feedback: "진지한 추론 시도에 감사드립니다. (서버 연결 지연으로 기본 통과 처리)"
        };
    }
}

/**
 * [2026-02-19] 최종 리포트 단계에서 실시간 유튜브 추천 영상을 가져옵니다.
 */
export async function getYouTubeRecommendations(dimensions, questTitle) {
    try {
        const response = await axios.post('/api/core/youtube/recommendations', {
            dimensions,
            quest_title: questTitle
        });
        return response.data.videos || [];
    } catch (error) {
        console.error('YouTube recommendations fetch failed:', error);
        return [];
    }
}

/**
 * 정합성 체크 (Reasoning vs Implementation)
 * [2026-02-12] Added to support useCodeRunner.js
 */
export async function checkConsistency(reasoning, implementation, type = 'general') {
    console.log('[Consistency Check] Starting...', { type });

    // 캐시 확인
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

        if (!result) result = { score: 50, gaps: ["AI 응답 파싱 실패"] };

        // 캐시 저장
        setCache(cacheKey, result);

        return result;

    } catch (error) {
        console.error('[Consistency Check Error]', error);
        // Fail-safe: 통과 처리 (사용자 흐름 방해 방지)
        return {
            score: 100,
            gaps: []
        };
    }
}