/**
 * Pseudocode Practice API Service
 * 
 * 평가 철학:
 * 1. 규칙 기반: 치명적 오류 검증 + 구조 점수 (객관적, 일관적)
 * 2. AI 튜터: 교육적 대화형 피드백 (주관적, 개인화)
 * 3. 최종 점수: 규칙 기반만 사용 (공정성)
 * 
 * [2026-02-09] 완전 재설계 - 규칙 기반 + AI 튜터 하이브리드 (Antigravity + Claude)
 */

import { PseudocodeValidator } from '../utils/PseudocodeValidator.js';
import axios from 'axios';

/**
 * OpenAI API 호출 기본 함수
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
 * AI 통합 분석 (피드백 + 심층 질문 + 5차원 평가)
 * Single-Pass로 처리하여 토큰 비용 절감 및 속도 향상
 */
async function getUnifiedFeedback(problem, pseudocode, validationResult) {
  const systemPrompt = `You are a computer science tutor and technical interviewer.
Analyze the student's pseudocode and provide output in JSON format.
CRITICAL: All output text (feedback, questions, advice) MUST be in Korean.

Role:
1. Tutor: Provide encouraging, actionable feedback in Korean.
2. Interviewer: Generate 3 deep-dive technical questions based on their code in Korean.
3. Evaluator: Rate the code on 5 dimensions (0-100).

Output structure:
{
  "feedback": "string (warm, educational feedback in Korean, max 100 words)",
  "questions": [
    { "category": "Logic", "question": "..." },
    { "category": "Edge Cases", "question": "..." },
    { "category": "Optimization", "question": "..." }
  ],
  "metrics": {
    "completeness": number,
    "logic_flow": number,
    "abstraction": number,
    "syntax_consistency": number,
    "edge_cases": number
  }
}`;

  const userPrompt = `Problem: ${problem.title || 'Algorithm Problem'}
Description: ${problem.description || ''}

Student's Pseudocode:
${pseudocode}

Validation Result (Reference):
- Structure Score: ${validationResult.score}
- Key Concepts Found: ${(Array.isArray(validationResult.details.concepts) ? validationResult.details.concepts.join(', ') : 'None')}
- Warnings: ${(Array.isArray(validationResult.warnings) ? validationResult.warnings.join('; ') : 'None')}

Generate the JSON response.`;

  try {
    const response = await callOpenAI(userPrompt, {
      systemMessage: systemPrompt,
      maxTokens: 800,
      temperature: 0.7,
      jsonMode: true // If supported by proxy, otherwise instructed in prompt
    });

    // Clean and parse JSON
    const jsonStr = response.replace(/```json/g, '').replace(/```/g, '').trim();
    return JSON.parse(jsonStr);

  } catch (error) {
    console.warn('Unified AI analysis failed:', error);
    return null; // Fallback handled by caller
  }
}

/**
 * Phase 3: 의사코드 즉시 평가 (Unified)
 * 
 * 흐름:
 * 1. 규칙 기반 검증 (즉시, 무료)
 * 2. 치명적 오류 있으면 즉시 반환
 * 3. 오류 없으면 AI 통합 분석 요청 (비동기, 선택적)
 * 
 * @returns {
 *   passed: boolean,
 *   score: number (규칙 기반),
 *   grade: string,
 *   criticalErrors: array,
 *   feedback: string,
 *   questions: array,
 *   metrics: object,
 *   improvements: array,
 *   details: object
 * }
 */
export async function quickCheckPseudocode(problem, pseudocode) {
  try {
    // 1. 규칙 기반 검증 (즉시)
    const validator = new PseudocodeValidator(problem);
    const validationResult = validator.validate(pseudocode);

    // 2. 치명적 오류 확인
    if (!validationResult.passed) {
      return {
        passed: false,
        score: Math.min(validationResult.score, 40), // 치명적 오류 있으면 최대 40점
        grade: 'needs-major-revision',
        criticalErrors: validationResult.criticalErrors,
        feedback: validationResult.criticalErrors[0].message,
        why: validationResult.criticalErrors[0].why,
        correctExample: validationResult.criticalErrors[0].example,
        questions: [],
        metrics: null,
        improvements: validationResult.warnings,
        details: validationResult.details
      };
    }

    // 3. AI 통합 분석 요청 (Single-Pass)
    const aiResult = await getUnifiedFeedback(problem, pseudocode, validationResult);

    // 4. 결과 병합
    // 규칙 기반 점수와 AI 메트릭 점수를 50:50으로 혼합하거나, AI 점수를 보조로 사용
    // 여기서는 규칙 점수를 기본으로 하고, AI 메트릭을 상세 리포트에 포함

    const finalScore = validationResult.score;

    let grade;
    if (finalScore >= 85) {
      grade = 'excellent';
    } else if (finalScore >= 70) {
      grade = 'good';
    } else if (finalScore >= 50) {
      grade = 'fair';
    } else {
      grade = 'needs-improvement';
    }

    return {
      passed: true,
      score: finalScore,
      grade,
      criticalErrors: [],
      // AI 피드백이 있으면 우선 사용, 없으면 규칙 기반 피드백 Fallback
      feedback: aiResult?.feedback || validationResult.details.structure.feedback.join('\n'),
      questions: aiResult?.questions || [],
      metrics: aiResult?.metrics || {},
      improvements: validationResult.warnings,
      details: validationResult.details
    };

  } catch (error) {
    console.error('Quick check error:', error);
    return {
      passed: false,
      score: 0,
      grade: 'system-error',
      feedback: '시스템 오류가 발생했습니다.',
      criticalErrors: [{ message: error.message }],
      questions: [],
      metrics: null,
      details: {}
    };
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
 */
export async function evaluatePseudocode(problem, pseudocode, deepDiveQnA) {
  // 1. 의사코드 평가 (규칙 기반)
  const validator = new PseudocodeValidator(problem);
  const validationResult = validator.validate(pseudocode);

  // 의사코드 점수: 50점 만점으로 환산
  const pseudocodeScore = Math.round(validationResult.score * 0.5);

  // 2. 면접 답변 평가 (AI)
  const deepDiveArray = Array.isArray(deepDiveQnA) ? deepDiveQnA : [];

  let interviewScore = 0;
  const questionAnalysis = [];

  // 간단한 휴리스틱 평가 (AI 비용 절감)
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
      // 기술 용어 확인
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

  // 면접 답변 점수: 최대 50점
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
      details: validationResult.details.structure.feedback,
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
    ]
  };
}

/**
 * 의사코드 ↔ 실제 코드 정합성 체크
 * (기존 로직 유지)
 */
export async function checkConsistency(pseudocode, actualCode, problemType = 'dataLeakage') {
  // 간단한 키워드 기반 검증
  const gaps = [];

  if (problemType === 'dataLeakage') {
    // 의사코드 체크
    if (!/fit/i.test(pseudocode)) {
      gaps.push('의사코드에 "fit" 개념 누락');
    }
    if (!/transform/i.test(pseudocode)) {
      gaps.push('의사코드에 "transform" 개념 누락');
    }

    // 코드 체크
    if (!/\.fit\(/i.test(actualCode)) {
      gaps.push('실제 코드에 .fit() 메서드 없음');
    }
    if (!/\.transform\(/i.test(actualCode)) {
      gaps.push('실제 코드에 .transform() 메서드 없음');
    }

    // 치명적 패턴
    if (/fit\(.*test/i.test(actualCode)) {
      gaps.push('🚨 실제 코드에서 테스트 데이터로 fit 수행');
    }
  }

  const score = Math.max(0, 100 - (gaps.length * 20));
  const comment = gaps.length === 0
    ? '✅ 의사코드와 구현이 일치합니다'
    : `⚠️ ${gaps.length}개 불일치 발견`;

  return { score, comment, gaps };
}
