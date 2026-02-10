/**
 * Pseudocode Practice API Service (v2)
 * 
 * 개선 사항:
 * 1. JSON 파싱 안정성 (safeJSONParse 사용)
 * 4. AI 캐싱 (중복 호출 방지)
 * 7. 레이스 컨디션 방지 (요청 중복 차단)
 * 
 * [2026-02-09] 완전 개선 (Antigravity + Claude)
 */

import { PseudocodeValidator } from '../utils/PseudocodeValidator.js';
import { safeJSONParse } from '../utils/jsonParser.js';
import { handleAIEvaluationError } from '../utils/errorHandler.js';
import axios from 'axios';

// ✨ 4번 해결: AI 결과 캐시
const aiCache = new Map();
const MAX_CACHE_SIZE = 100;
const CACHE_TTL = 1000 * 60 * 30; // 30분

// ✨ 7번 해결: 요청 중복 방지
const ongoingRequests = new Map();

/**
 * 캐시 키 생성
 */
function getCacheKey(type, data) {
    return `${type}:${JSON.stringify(data)}`;
}

/**
 * 캐시 관리 (LRU)
 */
function setCache(key, value) {
    // 캐시 크기 제한
    if (aiCache.size >= MAX_CACHE_SIZE) {
        const firstKey = aiCache.keys().next().value;
        aiCache.delete(firstKey);
    }

    aiCache.set(key, {
        value,
        timestamp: Date.now()
    });
}

function getCache(key) {
    const cached = aiCache.get(key);
    
    if (!cached) return null;

    // TTL 체크
    if (Date.now() - cached.timestamp > CACHE_TTL) {
        aiCache.delete(key);
        return null;
    }

    return cached.value;
}

/**
 * OpenAI API 호출 (개선 버전)
 */
async function callOpenAI(prompt, options = {}) {
    const {
        model = 'gpt-4o-mini',
        maxTokens = 500,
        temperature = 0.7,
        systemMessage = null,
        maxRetries = 2
    } = options;

    const messages = [];
    if (systemMessage) {
        messages.push({ role: 'system', content: systemMessage });
    }
    messages.push({ role: 'user', content: prompt });

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            const response = await axios.post('/api/core/ai-proxy/', {
                model,
                messages,
                max_tokens: maxTokens,
                temperature
            });

            return response.data.content.trim();
        } catch (error) {
            if (attempt < maxRetries) {
                console.warn(`Retry ${attempt + 1}/${maxRetries}:`, error.message);
                await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
                continue;
            }
            throw error;
        }
    }
}

/**
 * ✨ 4번 해결: AI 튜터 피드백 (캐싱 적용)
 */
async function getTutorFeedback(problem, pseudocode, validationResult) {
    // 캐시 키 생성 (문제 ID + 점수 기반)
    const cacheKey = getCacheKey('tutor', {
        problemId: problem.id,
        score: validationResult.score,
        conceptsFound: validationResult.details.concepts.length
    });

    // 캐시 확인
    const cached = getCache(cacheKey);
    if (cached) {
        console.log('[AI Cache] Tutor feedback from cache');
        return cached;
    }

    const systemPrompt = `You are a patient, encouraging computer science tutor.

Your role:
- Help students understand WHY, not just WHAT
- Ask thought-provoking questions
- Provide specific, actionable guidance
- Be encouraging even when correcting mistakes

Never:
- Give scores or grades
- Be condescending
- Provide complete solutions
- Use phrases like "you should have" or "you forgot"`;

    const userPrompt = `Problem: ${problem.title || 'Algorithm Design'}

Student's pseudocode:
${pseudocode}

Current understanding:
- Found concepts: ${validationResult.details.concepts.join(', ') || 'none'}
- Structure score: ${validationResult.score}/100
${validationResult.criticalErrors.length > 0 ? `- Critical errors: ${validationResult.criticalErrors.map(e => e.message).join('; ')}` : ''}

Provide brief, conversational feedback (max 100 words):
1. One specific thing they did well
2. One key concept to strengthen (with a guiding question, not an answer)
3. One actionable next step

Keep it warm and encouraging.`;

    try {
        const response = await callOpenAI(userPrompt, {
            systemMessage: systemPrompt,
            maxTokens: 250,
            temperature: 0.7
        });

        const result = {
            feedback: response,
            encouragement: validationResult.score >= 70 
                ? "You're on the right track! 🎯" 
                : validationResult.score >= 40
                ? "Good foundation, let's refine it together! 💪"
                : "Let's work through this step by step! 🤝"
        };

        // 캐시 저장
        setCache(cacheKey, result);

        return result;
    } catch (error) {
        console.warn('Tutor feedback failed:', error.message);
        return {
            feedback: "Great effort on your pseudocode! Focus on the core logic flow and make sure each step builds on the previous one.",
            encouragement: "Keep going! 🚀"
        };
    }
}

/**
 * ✨ 7번 해결: Phase 3 의사코드 즉시 평가 (레이스 컨디션 방지)
 */
export async function quickCheckPseudocode(problem, pseudocode) {
    // ✨ 레이스 컨디션 방지: 동일 요청 중복 체크
    const requestKey = `quick:${problem.id}:${pseudocode.substring(0, 50)}`;
    
    if (ongoingRequests.has(requestKey)) {
        console.warn('[Race Prevention] Duplicate request blocked:', requestKey);
        // 진행 중인 요청 재사용
        return await ongoingRequests.get(requestKey);
    }

    // 요청 Promise 저장
    const evaluationPromise = (async () => {
        try {
            // 1. 규칙 기반 검증 (즉시)
            const validator = new PseudocodeValidator(problem);
            const validationResult = validator.validate(pseudocode);

            // 2. 치명적 오류가 있으면 AI 없이 즉시 반환
            if (!validationResult.passed) {
                return {
                    passed: false,
                    score: Math.min(validationResult.score, 40),
                    grade: 'needs-major-revision',
                    criticalErrors: validationResult.criticalErrors,
                    feedback: validationResult.criticalErrors[0].message,
                    why: validationResult.criticalErrors[0].why,
                    correctExample: validationResult.criticalErrors[0].example,
                    improvements: validationResult.warnings,
                    details: validationResult.details,
                    aiTutorAvailable: false
                };
            }

            // 3. 치명적 오류 없음 → AI 튜터 피드백 요청 (캐싱됨)
            let tutorFeedback = null;
            try {
                tutorFeedback = await getTutorFeedback(problem, pseudocode, validationResult);
            } catch (error) {
                console.warn('AI tutor unavailable:', error.message);
                // AI 실패해도 규칙 기반 결과는 유지
            }

            // 4. 등급 결정 (규칙 기반 점수로만)
            let grade;
            if (validationResult.score >= 85) {
                grade = 'excellent';
            } else if (validationResult.score >= 70) {
                grade = 'good';
            } else if (validationResult.score >= 50) {
                grade = 'fair';
            } else {
                grade = 'needs-improvement';
            }

            return {
                passed: true,
                score: validationResult.score,
                grade,
                criticalErrors: [],
                feedback: tutorFeedback?.feedback || validationResult.details.structure.feedback.join('\n'),
                encouragement: tutorFeedback?.encouragement || '잘하고 있습니다! 👍',
                improvements: validationResult.warnings,
                details: validationResult.details,
                aiTutorAvailable: tutorFeedback !== null
            };
        } finally {
            // 요청 완료 후 제거
            ongoingRequests.delete(requestKey);
        }
    })();

    // 진행 중인 요청 등록
    ongoingRequests.set(requestKey, evaluationPromise);

    return await evaluationPromise;
}

/**
 * ✨ 1번, 4번 해결: Pseudocode 심화 질문 생성 (JSON 파싱 개선 + 캐싱)
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
        const response = await callOpenAI(userPrompt, {
            systemMessage: systemPrompt,
            maxTokens: 400,
            temperature: 0.8
        });

        // ✨ 1번 해결: 안전한 JSON 파싱
        const questions = safeJSONParse(response, null);

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
        grade,
        summary: `의사코드: ${pseudocodeScore}/50점 | 면접 답변: ${interviewScore}/50점`,

        pseudocodeEvaluation: {
            score: pseudocodeScore,
            passed: validationResult.passed,
            criticalErrors: validationResult.criticalErrors,
            details: validationResult.details?.structure?.feedback || [],
            strengths: validationResult.score >= 70 ? ['규칙 준수 우수'] : [],
            weaknesses: validationResult.warnings
        },

        interviewEvaluation: {
            score: interviewScore,
            questionAnalysis
        },

        suggestions: [
            ...validationResult.warnings,
            '면접 답변에서는 구체적인 예시와 기술 용어를 활용하세요.'
        ],

        // ✨ 캐싱 여부 표시
        usedCache: phase3Result !== null
    };
}

/**
 * 의사코드 ↔ 실제 코드 정합성 체크
 * ✨ 6번 해결: 주석 제거 후 검증
 */
export async function checkConsistency(pseudocode, actualCode, problemType = 'dataLeakage') {
    // ✨ 주석 제거
    const cleanCode = actualCode
        .replace(/#.*$/gm, '')         // Python comments
        .replace(/"""[\s\S]*?"""/g, '') // Docstrings
        .replace(/'''[\s\S]*?'''/g, '');

    const gaps = [];

    if (problemType === 'dataLeakage') {
        // 의사코드 체크
        if (!/fit/i.test(pseudocode)) {
            gaps.push('의사코드에 "fit" 개념 누락');
        }
        if (!/transform/i.test(pseudocode)) {
            gaps.push('의사코드에 "transform" 개념 누락');
        }

        // ✨ 주석 제거된 코드에서만 체크
        if (!/\.fit\s*\(/i.test(cleanCode)) {
            gaps.push('실제 코드에 .fit() 메서드 없음');
        }
        if (!/\.transform\s*\(/i.test(cleanCode)) {
            gaps.push('실제 코드에 .transform() 메서드 없음');
        }

        // 치명적 패턴
        if (/fit\s*\(.*test/i.test(cleanCode)) {
            gaps.push('🚨 실제 코드에서 테스트 데이터로 fit 수행');
        }
    }

    const score = Math.max(0, 100 - (gaps.length * 20));
    const comment = gaps.length === 0
        ? '✅ 의사코드와 구현이 일치합니다'
        : `⚠️ ${gaps.length}개 불일치 발견`;

    return { score, comment, gaps };
}

/**
 * ✨ 캐시 관리 함수
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