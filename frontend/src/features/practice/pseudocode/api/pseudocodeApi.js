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
    coherence: '정합성',
    abstraction: '추상화',
    exception_handling: '예외처리',
    implementation: '구현력',
    architecture: '설계력'
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
            const tailQuestion = generateTailQuestion(aiResult.dimensions, combinedScore, problem);

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
                python_feedback: aiResult.python_feedback || "",
                // ✅ 백엔드에서 생성된 조언 우선 사용
                senior_advice: aiResult.senior_advice || "",
                // ✅ [2026-02-13] 유튜브 추천 영상 포함
                recommended_videos: getRecommendedVideos(aiResult.dimensions, problem)
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
            basis: concepts.length > 0 ? `필수 개념 ${concepts.length}개 포함` : '핵심 로직이 명시되지 않음',
            specific_issue: concepts.length < 4 ? '핵심 개념 일부 누락' : null,
            improvement: concepts.length < 4 ? '데이터 분리, fit, transform 개념을 모두 포함하세요' : '적절한 논리 흐름이 필요합니다'
        },
        abstraction: {
            score: /IF.*THEN/i.test(pseudocode) ? baseScore : baseScore * 0.6,
            basis: /IF.*THEN/i.test(pseudocode) ?
                '조건-행동 구조 사용' :
                '단순 나열 또는 미완성 구조',
            specific_issue: /IF.*THEN/i.test(pseudocode) ? null : '단순 키워드 나열',
            improvement: /IF.*THEN/i.test(pseudocode) ? null :
                'IF-THEN 구조로 조건과 행동을 분리하세요'
        },
        exception_handling: {
            score: /예외|검증|체크|확인|validation|check|error/i.test(pseudocode) ? 60 : 30,
            basis: /예외|검증|체크/i.test(pseudocode) ?
                '예외 처리 키워드 포함' :
                '예외 처리 로직 부재',
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
        { id: 'w_A5M9In9I0', title: 'Data Leakage in Machine Learning', desc: '데이터 누수의 정의와 실전 방지 전략을 배웁니다.', reason: '데이터 분할 전 통계량 산출 로직 보완이 필요합니다.' },
        { id: 'nBaL9nTrkr4', title: 'ML Pipelines Simplified', desc: 'Pipeline으로 데이터 누수를 원천 차단하는 방법을 확인하세요.', reason: '전처리 파이프라인의 구조적 설계 교육용입니다.' }
    ],
    skew: [
        { id: 'uF_fS65B_j4', title: 'Training-Serving Skew & Bias', desc: '학습과 서빙 환경의 데이터 불일치를 잡는 노하우.', reason: '수집 환경과 실제 추론 환경의 정합성을 검토해보세요.' }
    ],
    exception_handling: [
        { id: '94_MhWqj1vM', title: 'Robust Python Error Handling', desc: 'Try-Except를 넘어서는 견고한 에러 핸들링 설계.', reason: '에지 케이스 및 비정상 데이터에 대한 방어 로직이 부족합니다.' }
    ],
    architecture: [
        { id: 'H0S_995S_jA', title: 'System Design: Separation of Concerns', desc: '복잡한 비즈니스 로직을 구조화하는 아키텍트의 시선.', reason: '전체적인 컴포넌트 간의 책임 분리(Separation of Concerns)를 연구해보세요.' }
    ],
    abstraction: [
        { id: '3fA2E4I_m88', title: 'Clean Code: Logic vs Implementation', desc: '더 유연한 시스템을 위한 추상화 도입 타이밍.', reason: '하드코딩된 로직을 일반화하여 확장성을 높여보세요.' }
    ]
};

/**
 * 약점 기반 유튜브 영상 추천 로직
 */
function getRecommendedVideos(dimensions, problem = null) {
    const dimEntries = Object.entries(dimensions);
    // 가장 점수가 낮은 차원 찾기 (80점 미만 대상)
    const weakDims = dimEntries
        .filter(([_, d]) => d.score < 80)
        .sort((a, b) => a[1].score - b[1].score);

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
- 말투: 시니어 아키텍트다운 전문적이고 신뢰감 있는 어조 (무조건적인 비난 금지)`; ㅉㅉㅉ

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