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
    coherence: 'Consistency',
    abstraction: 'Abstraction',
    exception_handling: 'Exception Handling',
    implementation: 'Implementation',
    architecture: 'Design'
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
export async function evaluatePseudocode5D(problem, pseudocode) {
    console.log('[5D Evaluation] Starting evaluation...');

    // 레이스 컨디션 방지
    const requestKey = `5d:${problem.id}:${pseudocode.substring(0, 50)}`;
    if (ongoingRequests.has(requestKey)) {
        console.warn('[Race Prevention] Duplicate request blocked');
        return await ongoingRequests.get(requestKey);
    }

    const evaluationPromise = (async () => {
        try {
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
                    // [STEP 3] Python 변환 요청 플래그 추가
                    request_python_conversion: true
                }, { timeout: 35000 }); // 타임아웃 35초로 연장 (변환 시간 고려)

                aiResult = response.data;
                console.log('[5D Evaluation] AI response received:', aiResult.overall_score);

            } catch (error) {
                console.error('[AI Evaluation Error]', error.message);

                // Fallback: 규칙 기반으로 5차원 생성
                console.log('[5D Evaluation] Fallback to rule-based dimensions');
                aiResult = {
                    overall_score: ruleResult.score, // 0-100
                    dimensions: generateRuleBasedDimensions(ruleResult, pseudocode),
                    strengths: ruleResult.details.structure?.feedback?.filter(f => f.includes('✅')) || [],
                    weaknesses: ruleResult.warnings,
                    tail_question: null
                };
            }

            // STEP 3: 점수 통합 및 스케일링
            // 요구사항: AI 5지표 각 12점씩 총 60점 + Rule 40점 = 100점

            // 1. Rule 점수 (0-100) -> 40점 만점으로 변환
            const ruleScoreScaled = Math.round(ruleResult.score * 0.4);

            // 2. AI 점수 (0-100) -> 60점 만점으로 변환
            let aiScoreScaled = 0;

            // AI Dimensions 스케일링 (100점 -> 12점)
            if (aiResult.dimensions) {
                Object.keys(aiResult.dimensions).forEach(key => {
                    const dim = aiResult.dimensions[key];
                    // 원본 점수(100만점)를 12점으로 변환
                    dim.original_score = dim.score; // 백업
                    dim.score = (dim.score / 100) * 12;

                    // 소수점 1자리까지 (UI 표시용)
                    dim.score = Math.round(dim.score * 10) / 10;

                    aiScoreScaled += dim.score;
                });
            } else {
                // Dimensions가 없는 경우 overall_score 기반으로 배분
                aiScoreScaled = (aiResult.overall_score / 100) * 60;
            }

            aiScoreScaled = Math.round(aiScoreScaled);

            // 3. 최종 점수 합산
            const combinedScore = ruleScoreScaled + aiScoreScaled;

            console.log('[5D Evaluation] Final Scores:', {
                rule_raw: ruleResult.score,
                rule_scaled_40: ruleScoreScaled,
                ai_raw: aiResult.overall_score,
                ai_scaled_60: aiScoreScaled,
                total: combinedScore,
                hasCriticalErrors
            });

            // STEP 4: Tail Question 생성 (80점 미만 시)
            const tailQuestion = generateTailQuestion(aiResult.dimensions, combinedScore);

            // STEP 5: 다음 단계 결정
            // 80점 이상 -> DEEP_QUIZ
            // 80점 미만 -> TAIL_QUESTION
            const nextPhase = combinedScore >= 80 ? 'DEEP_QUIZ' : 'TAIL_QUESTION';

            // 치명적 오류가 있었다면 강제로 TAIL_QUESTION 및 안내
            let finalTailQuestion = tailQuestion;
            if (hasCriticalErrors) {
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

            // [STEP 4-1] Python 피드백이 있다면 이를 우선 반영 (규칙 오류가 없을 때)
            if (!hasCriticalErrors && combinedScore < 80 && aiResult.python_feedback) {
                finalTailQuestion = {
                    should_show: true,
                    reason: "Python 변환 중 논리 허점 발견",
                    question: `작성하신 의사코드를 Python으로 변환하는 과정에서 다음 이슈가 발견되었습니다: "${aiResult.python_feedback}". 이를 보완하시겠습니까?`,
                    hint: "구체적인 로직(예: fit 호출 전 데이터 분리 등)을 명시하세요.",
                    options: [
                        { text: "네, 보완하겠습니다.", is_correct: true, reason: "논리적 완성도 향상" },
                        { text: "현재 로직으로 충분합니다.", is_correct: false, reason: "잠재적 오류 위험" }
                    ]
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
                python_feedback: aiResult.python_feedback || ""
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
function generateRuleBasedDimensions(ruleResult, pseudocode) {
    const baseScore = ruleResult.score;
    const concepts = Array.from(ruleResult.details.concepts || []);

    return {
        coherence: {
            score: concepts.length >= 4 ? Math.min(baseScore + 10, 100) : baseScore * 0.7,
            basis: `필수 개념 ${concepts.length}개 포함 (규칙 기반 추정)`,
            specific_issue: concepts.length < 4 ? '핵심 개념 일부 누락' : null,
            improvement: concepts.length < 4 ? '데이터 분리, fit, transform 개념을 모두 포함하세요' : null
        },
        abstraction: {
            score: /IF.*THEN/i.test(pseudocode) ? baseScore : baseScore * 0.6,
            basis: /IF.*THEN/i.test(pseudocode) ?
                '조건-행동 구조 사용 (규칙 기반 추정)' :
                '단순 나열 형태 (규칙 기반 추정)',
            specific_issue: /IF.*THEN/i.test(pseudocode) ? null : '단순 키워드 나열',
            improvement: /IF.*THEN/i.test(pseudocode) ? null :
                'IF-THEN 구조로 조건과 행동을 분리하세요'
        },
        exception_handling: {
            score: /예외|검증|체크|확인|validation|check|error/i.test(pseudocode) ? 60 : 30,
            basis: /예외|검증|체크/i.test(pseudocode) ?
                '예외 처리 키워드 포함 (규칙 기반 추정)' :
                '예외 처리 누락 (규칙 기반 추정)',
            specific_issue: /예외|검증|체크/i.test(pseudocode) ? null : '엣지 케이스 처리 누락',
            improvement: /예외|검증|체크/i.test(pseudocode) ? null :
                '데이터 검증 단계를 추가하세요 (예: IF 데이터가 None THEN 예외 발생)'
        },
        implementation: {
            score: baseScore,
            basis: '구조 점수 기반 (규칙 기반 추정)',
            specific_issue: baseScore < 70 ? '실행 가능성 낮음' : null,
            improvement: baseScore < 70 ? '각 단계를 더 구체화하세요' : null
        },
        architecture: {
            score: ruleResult.details.flow?.score || baseScore * 0.9,
            basis: '논리적 순서 분석 (규칙 기반 추정)',
            specific_issue: (ruleResult.details.flow?.score || 0) < 70 ? '단계 간 연결성 부족' : null,
            improvement: (ruleResult.details.flow?.score || 0) < 70 ?
                '순서를 번호로 명시하세요 (예: 1. 분할 → 2. fit → 3. transform)' : null
        }
    };
}

/**
 * Tail Question 생성
 */
function generateTailQuestion(dimensions, overallScore) {
    if (overallScore >= 80) {
        return {
            should_show: false,
            reason: "점수가 충분히 높아 tail question 불필요"
        };
    }

    // 가장 약한 차원 찾기
    const dimEntries = Object.entries(dimensions);
    const weakestDim = dimEntries.sort((a, b) => a[1].score - b[1].score)[0];

    if (!weakestDim) {
        return {
            should_show: true,
            reason: "논리 검증 필요",
            question: "작성하신 의사코드의 논리적 흐름을 재점검해보세요.",
            hint: "핵심 개념을 더 구체적으로 표현하세요",
            options: [
                { text: "논리 흐름을 보완하겠습니다.", is_correct: true, reason: "구체적인 흐름 정의가 필요합니다." },
                { text: "현재 로직이 완벽합니다.", is_correct: false, reason: "개선할 여지가 있습니다." }
            ]
        };
    }

    const [dimKey, dimData] = weakestDim;
    const dimName = DIMENSION_NAMES[dimKey] || dimKey;

    return {
        should_show: true,
        reason: `${dimName} 점수 낮음 (${Math.round(dimData.score)}점)`,
        question: `${dimName} 영역에서 문제가 발견되었습니다: ${dimData.specific_issue || '개선 필요'}`,
        hint: dimData.improvement || '핵심 개념을 더 명확히 표현하세요',
        options: [
            {
                text: dimData.improvement || '현재 로직을 개선하겠습니다',
                is_correct: true,
                reason: "AI가 제시한 개선 방안"
            },
            {
                text: "현재 로직이 완벽합니다",
                is_correct: false,
                reason: `${dimName} 영역 개선이 필요합니다`
            },
            {
                text: "이 부분은 중요하지 않습니다",
                is_correct: false,
                reason: `${dimName}은 설계의 핵심 요소입니다`
            }
        ]
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
- 100자 이내로 간결하게
- 구체적인 개선점 제시
- 격려와 조언의 균형
- "~한 부분은 훌륭합니다. 다만 ~를 개선하면 더욱 견고한 설계가 될 것입니다." 형식`;

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
            "훌륭한 시도였습니다. 실전에서 적용하며 계속 발전시켜 나가세요.";

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

    const systemPrompt = `당신은 데이터 과학 교육 전문가입니다.
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

    try {
        const response = await axios.post('/api/core/ai-proxy/', {
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: `학생의 답변: "${userAnswer}"` }
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