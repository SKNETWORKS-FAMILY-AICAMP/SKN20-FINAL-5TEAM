/**
 * Architecture Evaluation Service (Simplified)
 *
 * 핵심 기둥 3개만 평가 (Option C)
 * - 질문 생성 시 파악된 부족한 3개 영역만 평가
 * - 각 영역 33% 비중으로 점수 산출
 * - 모범답안 제공으로 학습 효과 증대
 */

// txt 파일에서 핵심 원칙 추출 (architectureApiFastTest.js와 동일한 방식)
import reliabilityTxt from '@/data/신뢰성.txt?raw';
import performanceTxt from '@/data/최적화.txt?raw';
import operationalTxt from '@/data/운영유용성.txt?raw';
import costTxt from '@/data/비용.txt?raw';
import securityTxt from '@/data/보안.txt?raw';
import sustainabilityTxt from '@/data/지속가능성.txt?raw';

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

/**
 * txt 파일에서 [핵심 분석 원칙] 섹션만 추출
 */
function extractPrinciples(txtContent) {
  const match = txtContent.match(/### \[핵심 분석 원칙[^\]]*\]\s*([\s\S]*?)(?=### \[|$)/);
  return match ? match[1].trim() : '';
}

/**
 * 6대 기둥 데이터 (txt 파일에서 원칙 추출)
 */
const PILLAR_DATA = {
  '신뢰성': {
    id: 'reliability',
    name: '신뢰성 (Reliability)',
    emoji: '🏗️',
    principles: extractPrinciples(reliabilityTxt)
  },
  '성능': {
    id: 'performance',
    name: '성능 최적화 (Performance)',
    emoji: '⚡',
    principles: extractPrinciples(performanceTxt)
  },
  '운영': {
    id: 'operational',
    name: '운영 우수성 (Operational Excellence)',
    emoji: '🤖',
    principles: extractPrinciples(operationalTxt)
  },
  '비용': {
    id: 'cost',
    name: '비용 최적화 (Cost)',
    emoji: '💰',
    principles: extractPrinciples(costTxt)
  },
  '보안': {
    id: 'security',
    name: '보안 (Security)',
    emoji: '🔐',
    principles: extractPrinciples(securityTxt)
  },
  '지속가능성': {
    id: 'sustainability',
    name: '지속 가능성 (Sustainability)',
    emoji: '🌱',
    principles: extractPrinciples(sustainabilityTxt)
  }
};

/**
 * OpenAI API 호출
 */
async function callOpenAI(prompt, options = {}) {
  const {
    model = 'gpt-4o-mini',
    maxTokens = 2000,
    temperature = 0.5
  } = options;

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getApiKey()}`
    },
    body: JSON.stringify({
      model,
      messages: [{ role: 'user', content: prompt }],
      max_tokens: maxTokens,
      temperature
    })
  });

  if (!response.ok) throw new Error(`API Error: ${response.status}`);
  const data = await response.json();
  return data.choices[0].message.content.trim();
}

/**
 * 메인 평가 함수
 *
 * @param {Object} problem - 문제 정보
 * @param {string} architectureContext - 아키텍처 컨텍스트 (컴포넌트, 연결, mermaid)
 * @param {string} generatedQuestion - (사용 안 함)
 * @param {string} userExplanation - 사용자의 아키텍처 설명
 * @param {Array} deepDiveQnA - 질문과 답변 배열 [{category, question, answer, gap}, ...]
 */
export async function evaluateWithMasterAgent(
  problem,
  architectureContext,
  generatedQuestion,
  userExplanation,
  deepDiveQnA
) {
  console.log('🎯 평가 시작...');
  const startTime = Date.now();

  // Q&A 정리
  const qnaArray = Array.isArray(deepDiveQnA) ? deepDiveQnA : [];
  const qnaText = qnaArray
    .filter(item => item.answer)
    .map((item, idx) => `
### 질문 ${idx + 1} [${item.category}]
**질문**: ${item.question}
**의도**: ${item.gap || '설계 의도 확인'}
**사용자 답변**: ${item.answer}
`).join('\n');

  // 평가할 기둥 카테고리 추출 (질문에서 파악된 3개)
  const categories = qnaArray
    .map(item => item.category)
    .filter(Boolean);

  // 각 카테고리에 해당하는 원칙 가져오기
  const relevantPrinciples = categories
    .map(cat => {
      const pillar = PILLAR_DATA[cat];
      if (pillar) {
        return `### ${pillar.emoji} ${pillar.name}\n${pillar.principles}`;
      }
      return null;
    })
    .filter(Boolean)
    .join('\n\n---\n\n');

  const prompt = `당신은 **시니어 클라우드 솔루션 아키텍트**입니다.
지원자의 시스템 아키텍처 설계와 질문 답변을 평가합니다.

---

## 📋 문제 정보

### 시나리오
${problem?.scenario || '시스템 아키텍처 설계'}

### 미션
${problem?.missions?.map((m, i) => `${i + 1}. ${m}`).join('\n') || '없음'}

### 제약조건
${problem?.constraints?.map((c, i) => `${i + 1}. ${c}`).join('\n') || '없음'}

---

## 🏗️ 지원자의 아키텍처

${architectureContext}

---

## 💬 지원자의 설계 설명

"${userExplanation || '(설명 없음)'}"

---

## 📝 질문 및 답변

${qnaText || '(질문/답변 없음)'}

---

## 📚 평가 기준 (해당 영역의 핵심 원칙)

${relevantPrinciples || '(원칙 없음)'}

---

## ⚠️ 평가 규칙

### 1. 점수 산정 기준
- 각 질문 영역별로 0-100점 부여
- **기본 점수 40점에서 시작**
- 답변이 구체적이고 기술적 근거가 있으면 +점수
- 답변이 모호하거나 핵심을 벗어나면 -점수
- 아키텍처에 반영되지 않은 답변은 감점

### 2. 모범답안 작성 규칙
- 해당 시나리오와 아키텍처에 맞는 구체적인 답변
- 실제 기술/서비스 이름 포함
- 사용자가 배울 수 있도록 상세하게

### 3. 최종 점수
- **반드시 정확히 3개** 영역만 평가 (evaluations 배열 길이 = 3)
- 3개 영역 점수의 평균 (각 33.3%)

---

## 출력 형식 (JSON만)

{
  "evaluations": [
    {
      "category": "질문 카테고리 (예: 신뢰성)",
      "question": "질문 내용",
      "userAnswer": "사용자 답변 요약",
      "score": 0-100,
      "feedback": "사용자 답변에 대한 구체적 피드백 (2-3문장)",
      "modelAnswer": "이 시나리오/아키텍처에 맞는 모범답안 (5-7문장, 구체적 기술 포함)",
      "improvements": ["개선 포인트 1", "개선 포인트 2"]
    }
  ],
  "overallScore": 0-100,
  "grade": "excellent/good/needs-improvement/poor",
  "summary": "전체 평가 요약 (3-4문장)",
  "strengths": ["강점 1", "강점 2"],
  "weaknesses": ["약점 1", "약점 2"],
  "recommendations": ["추천 학습/개선 사항 1", "추천 2"]
}`;

  try {
    const response = await callOpenAI(prompt, {
      maxTokens: 2500,
      temperature: 0.5
    });

    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const result = JSON.parse(jsonMatch[0]);

      const endTime = Date.now();
      console.log(`✅ 평가 완료 (${((endTime - startTime) / 1000).toFixed(1)}s)`);

      // 정확히 3개만 유지
      const evaluations = (result.evaluations || []).slice(0, 3);

      // 결과 포맷팅
      return {
        score: result.overallScore,
        totalScore: result.overallScore,
        grade: result.grade,
        summary: result.summary,
        strengths: result.strengths || [],
        weaknesses: result.weaknesses || [],
        suggestions: result.recommendations || [],

        // 질문별 평가 (모범답안 포함) - 3개 고정
        questionEvaluations: evaluations,

        // 기존 호환용
        nfrScores: buildNfrScores(evaluations),
        pillarScores: buildPillarScores(evaluations)
      };
    }
    throw new Error('Invalid JSON');
  } catch (error) {
    console.error('평가 실패:', error);
    return generateFallbackResult(qnaArray);
  }
}

/**
 * 평가 결과를 nfrScores 형식으로 변환 (기존 호환)
 */
function buildNfrScores(evaluations) {
  const scores = {
    scalability: { score: 50, feedback: '' },
    availability: { score: 50, feedback: '' },
    performance: { score: 50, feedback: '' },
    consistency: { score: 50, feedback: '' },
    reliability: { score: 50, feedback: '' }
  };

  evaluations.forEach(ev => {
    const cat = ev.category?.toLowerCase();
    if (cat?.includes('신뢰') || cat?.includes('reliability')) {
      scores.reliability = { score: ev.score, feedback: ev.feedback };
      scores.availability = { score: ev.score, feedback: ev.feedback };
    } else if (cat?.includes('성능') || cat?.includes('performance')) {
      scores.performance = { score: ev.score, feedback: ev.feedback };
      scores.scalability = { score: ev.score, feedback: ev.feedback };
    } else if (cat?.includes('보안') || cat?.includes('security')) {
      scores.consistency = { score: ev.score, feedback: ev.feedback };
    }
  });

  return scores;
}

/**
 * 평가 결과를 pillarScores 형식으로 변환
 * Vue 컴포넌트의 키 이름과 일치시킴
 */
function buildPillarScores(evaluations) {
  // Vue 컴포넌트에서 사용하는 키 이름으로 매핑
  const categoryToKey = {
    '신뢰성': 'reliability',
    '성능': 'performanceOptimization',
    '운영': 'operationalExcellence',
    '비용': 'costOptimization',
    '보안': 'securityPrivacyCompliance',
    '지속가능성': 'sustainability'
  };

  const scores = {
    reliability: 0,
    performanceOptimization: 0,
    operationalExcellence: 0,
    costOptimization: 0,
    securityPrivacyCompliance: 0,
    sustainability: 0
  };

  evaluations.forEach(ev => {
    const key = categoryToKey[ev.category];
    if (key) {
      scores[key] = ev.score;
    }
  });

  return scores;
}

/**
 * 에러 시 기본 결과 생성
 */
function generateFallbackResult(qnaArray) {
  return {
    score: 50,
    totalScore: 50,
    grade: 'needs-improvement',
    summary: '평가 중 오류가 발생했습니다. 다시 시도해주세요.',
    strengths: ['평가 오류'],
    weaknesses: ['평가 오류'],
    suggestions: ['다시 시도해주세요'],
    questionEvaluations: qnaArray.map(q => ({
      category: q.category,
      question: q.question,
      userAnswer: q.answer,
      score: 50,
      feedback: '평가 오류',
      modelAnswer: '평가 오류로 모범답안을 생성할 수 없습니다.',
      improvements: []
    })),
    nfrScores: {
      scalability: { score: 50, feedback: '평가 오류' },
      availability: { score: 50, feedback: '평가 오류' },
      performance: { score: 50, feedback: '평가 오류' },
      consistency: { score: 50, feedback: '평가 오류' },
      reliability: { score: 50, feedback: '평가 오류' }
    },
    pillarScores: {}
  };
}

// ============================================================================
// Export 함수들 (기존 호환)
// ============================================================================

export function getAvailableSubAgents() {
  return Object.entries(PILLAR_DATA).map(([key, pillar]) => ({
    id: pillar.id,
    name: pillar.name,
    emoji: pillar.emoji,
    category: key
  }));
}

export function getAllQuestionStrategies() {
  return [];  // 더 이상 사용하지 않음
}

export { fetchProblems } from './architectureApiFastTest.js';