/**
 * Architecture Rubric-Based Evaluation Service
 *
 * 🎯 루브릭 기반 평가 (0점부터 시작)
 * [수정일: 2026-02-20] 완전 리팩토링 - 책임분리 완료
 * - 프롬프트 생성: architecturePromptTemplates.js
 * - LLM 호출: 백엔드 API
 * - 프론트엔드: 데이터 → 프롬프트 생성 → 백엔드 API 호출 → 결과 처리
 */

import { generateRubricPrompt, formatAxisWeights } from './architecturePromptTemplates.js';

/**
 * 🔥 루브릭 기반 평가 실행
 *
 * 프로세스:
 * 1. 프롬프트 생성 (architecturePromptTemplates.js)
 * 2. 백엔드 API 호출 (/api/core/architecture/evaluate/)
 * 3. 결과 처리 및 변환
 */
export async function evaluateWithRubric(
  problem,
  architectureContext,
  userExplanation,
  deepDiveQnA
) {
  console.log('🎯 루브릭 기반 평가 시작...');
  const startTime = Date.now();

  const qnaArray = Array.isArray(deepDiveQnA) ? deepDiveQnA : [];

  try {
    // Step 1: 프롬프트 생성
    const prompt = generateRubricPrompt(
      problem,
      architectureContext,
      userExplanation,
      qnaArray
    );

    // Step 2: 백엔드 API 호출
    const response = await fetch('/api/core/architecture/evaluate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        problem,
        architectureContext,
        userExplanation,
        deepDiveQnA: qnaArray,
        prompt  // 프롬프트를 백엔드로 전송
      })
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    const result = await response.json();

    const endTime = Date.now();
    console.log(`✅ 루브릭 평가 완료 (${((endTime - startTime) / 1000).toFixed(1)}s)`);

    // Step 3: 응답 결과 처리
    const questionEvaluations = (result.evaluations || []).slice(0, 3).map((ev, idx) => ({
      ...ev,
      question: qnaArray[idx]?.question || '',
      userAnswer: qnaArray[idx]?.answer || '',
      category: qnaArray[idx]?.category || ev.axisName || ''
    }));

    return {
      score: result.overallScore,
      totalScore: result.overallScore,
      grade: result.overallGrade,
      summary: result.summary,
      strengths: result.strengths || [],
      weaknesses: result.weaknesses || [],
      suggestions: result.recommendations || [],
      evaluations: result.evaluations || [],
      weightedScores: result.weightedScores || {},
      questionEvaluations,
      pillarScores: buildPillarScores(result.evaluations || []),
      nfrScores: buildNfrScores(result.evaluations || []),
      metadata: {
        method: 'rubric',
        rubricType: 'comprehensive',
        axisWeights: problem?.axis_weights,
        evaluatedAt: new Date().toISOString()
      }
    };
  } catch (error) {
    console.error('루브릭 평가 실패:', error);
    return generateFallbackResult(qnaArray, problem?.axis_weights);
  }
}

/**
 * 평가 결과를 pillarScores 형식으로 변환
 */
function buildPillarScores(evaluations) {
  const axisToPillar = {
    performance_optimization: 'performanceOptimization',
    reliability: 'reliability',
    operational_excellence: 'operationalExcellence',
    cost_optimization: 'costOptimization',
    security: 'security',
    sustainability: 'sustainability'
  };

  const scores = {
    performanceOptimization: 0,
    reliability: 0,
    operationalExcellence: 0,
    costOptimization: 0,
    security: 0,
    sustainability: 0
  };

  evaluations.forEach(ev => {
    const key = axisToPillar[ev.axis];
    if (key) {
      scores[key] = ev.score;
    }
  });

  return scores;
}

/**
 * 평가 결과를 nfrScores 형식으로 변환
 */
function buildNfrScores(evaluations) {
  const scores = {
    performance_optimization: { score: 0, feedback: '', grade: 'fair' },
    reliability: { score: 0, feedback: '', grade: 'fair' },
    operational_excellence: { score: 0, feedback: '', grade: 'fair' },
    cost_optimization: { score: 0, feedback: '', grade: 'fair' },
    security: { score: 0, feedback: '', grade: 'fair' },
    sustainability: { score: 0, feedback: '', grade: 'fair' }
  };

  evaluations.forEach(ev => {
    const axis = ev.axis;
    if (scores[axis]) {
      scores[axis] = {
        score: ev.score,
        feedback: ev.feedback,
        grade: ev.grade
      };
    }
  });

  return scores;
}

/**
 * 에러 시 기본 결과 생성 (Fallback)
 */
function generateFallbackResult(qnaArray, axisWeights) {
  console.warn('⚠️ 루브릭 Fallback 평가 사용');

  const PILLAR_NAMES = {
    performance_optimization: '성능 최적화',
    reliability: '신뢰성',
    operational_excellence: '운영 우수성',
    cost_optimization: '비용 최적화',
    security: '보안',
    sustainability: '지속가능성'
  };

  const baseEvaluations = Object.entries(PILLAR_NAMES).map(([axis, name]) => {
    const weight = axisWeights?.[axis]?.weight || 0;
    let grade, score;

    if (weight === 0) {
      grade = 'fair';
      score = 65;
    } else if (weight >= 30) {
      grade = 'poor';
      score = 48;
    } else {
      grade = 'fair';
      score = 62;
    }

    return {
      axis,
      axisName: name,
      weight,
      grade,
      score,
      feedback: '평가 중 오류가 발생했습니다.',
      improvements: []
    };
  });

  const questionEvaluations = baseEvaluations.slice(0, 3).map((ev, idx) => ({
    ...ev,
    question: qnaArray[idx]?.question || '',
    userAnswer: qnaArray[idx]?.answer || '',
    category: qnaArray[idx]?.category || ev.axisName || ''
  }));

  const weightedScores = {};
  let totalWeightedScore = 0;
  let totalWeight = 0;

  baseEvaluations.forEach(ev => {
    const weighted = ev.score * ev.weight / 100;
    weightedScores[ev.axis] = weighted;
    totalWeightedScore += weighted;
    totalWeight += ev.weight;
  });

  const overallScore = totalWeight > 0 ? Math.round(totalWeightedScore / (totalWeight / 100)) : 50;

  return {
    score: overallScore,
    totalScore: overallScore,
    grade: 'poor',
    summary: '평가 중 오류가 발생했습니다. 다시 시도해주세요.',
    strengths: [],
    weaknesses: [],
    suggestions: ['다시 시도해주세요'],
    evaluations: baseEvaluations,
    questionEvaluations,
    weightedScores,
    metadata: {
      method: 'fallback',
      rubricType: 'fallback',
      error: true
    }
  };
}

/**
 * 내보내기
 */
export { formatAxisWeights };
