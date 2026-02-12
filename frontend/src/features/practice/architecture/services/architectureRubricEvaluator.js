/**
 * Architecture Rubric-Based Evaluation Service
 *
 * 🎯 루브릭 기반 평가 (0점부터 시작)
 * - Excellent (90-100) | Good (75-89) | Fair (60-74) | Poor (40-59) | Failing (0-39)
 * - 명확한 기준으로 공정한 평가
 * - axis_weights 가중치 반영
 *
 * 비용: 단일 호출 (경제적)
 * 효과: 높은 구분력 + 명확한 피드백
 */

import reliabilityTxt from '@/data/신뢰성.txt?raw';
import performanceTxt from '@/data/최적화.txt?raw';
import operationalTxt from '@/data/운영유용성.txt?raw';
import costTxt from '@/data/비용.txt?raw';
import securityTxt from '@/data/보안.txt?raw';
import sustainabilityTxt from '@/data/지속가능성.txt?raw';

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

/**
 * 🔥 txt 파일에서 [핵심 분석 원칙] 섹션만 추출
 */
function extractPrinciples(txtContent) {
  const match = txtContent.match(/### \[핵심 분석 원칙[^\]]*\]\s*([\s\S]*?)(?=### \[|$)/);
  return match ? match[1].trim() : '';
}

/**
 * 6대 기둥 매핑
 */
const AXIS_TO_PILLAR = {
  scalability: {
    name: '확장성 (Scalability)',
    emoji: '📈',
    principles: extractPrinciples(performanceTxt)
  },
  performance: {
    name: '성능 (Performance)',
    emoji: '⚡',
    principles: extractPrinciples(performanceTxt)
  },
  availability: {
    name: '가용성 (Availability)',
    emoji: '🔄',
    principles: extractPrinciples(reliabilityTxt)
  },
  reliability: {
    name: '신뢰성 (Reliability)',
    emoji: '🏗️',
    principles: extractPrinciples(reliabilityTxt)
  },
  consistency: {
    name: '일관성 (Consistency)',
    emoji: '🔀',
    principles: extractPrinciples(securityTxt)
  },
  security: {
    name: '보안 (Security)',
    emoji: '🔐',
    principles: extractPrinciples(securityTxt)
  }
};

/**
 * 🔥 루브릭 기준 정의 (모든 기둥 공통)
 *
 * 특징: 0점부터 시작, 명확한 5등급
 */
const RUBRIC_GRADES = {
  excellent: {
    range: [90, 100],
    label: '우수 (Excellent)',
    emoji: '✨',
    criteria: [
      '✅ 구체적인 기술/패턴 명시 (기술명, 설정값 포함)',
      '✅ 트레이드오프 깊이 있게 설명',
      '✅ 실무 기반 또는 사례 기반 답변',
      '✅ 제약조건 완벽하게 반영',
      '✅ 아키텍처 설계와 100% 일관성'
    ]
  },
  good: {
    range: [75, 89],
    label: '양호 (Good)',
    emoji: '✓',
    criteria: [
      '✅ 핵심 개념 정확',
      '✅ 구체적 기술 1-2개 언급',
      '✅ 트레이드오프 기본 수준 언급',
      '⚠️ 일부 제약조건 반영',
      '⚠️ 대부분 아키텍처와 일관성'
    ]
  },
  fair: {
    range: [60, 74],
    label: '보통 (Fair)',
    emoji: '⚠️',
    criteria: [
      '⚠️ 개념은 맞으나 구체성 부족',
      '⚠️ 일반적인 답변만 제공',
      '❌ 트레이드오프 미언급',
      '❌ 제약조건 일부만 반영',
      '❌ 아키텍처와 부분적 불일치'
    ]
  },
  poor: {
    range: [40, 59],
    label: '미흡 (Poor)',
    emoji: '❌',
    criteria: [
      '❌ 개념 이해는 있으나 부정확',
      '❌ 구체적 기술 없음',
      '❌ 문제 상황 충분히 고려 안 함',
      '❌ 제약조건 무시',
      '❌ 아키텍처와 주요 불일치'
    ]
  },
  failing: {
    range: [0, 39],
    label: '부족 (Failing)',
    emoji: '✗',
    criteria: [
      '❌ 답변 없음 또는 완전 오류',
      '❌ 문제 상황 이해 부족',
      '❌ 기술 기초 부족',
      '❌ 설계와 모순',
      '❌ 실무 불가능한 설계'
    ]
  }
};

/**
 * 축별 맞춤형 루브릭 (선택사항)
 * 문제에 따라 특정 기준을 강조
 */
const AXIS_SPECIFIC_RUBRICS = {
  scalability: {
    excellent: '캐시 샤딩, 로드 밸런싱, 동적 스케일링 전략 상세 설명',
    good: '수평 확장 전략 언급, 일부 구체적 기술 제시',
    fair: '확장성 고려 있으나 구체성 부족',
    poor: '확장성 방안 미흡',
    failing: '확장성 무시 또는 완전 오류'
  },
  performance: {
    excellent: 'latency 목표값, 캐싱 전략, 인덱싱 등 구체적 최적화 방안',
    good: '성능 고려, 캐시/인덱싱 등 1-2개 기술 언급',
    fair: '성능 최적화 인식 있으나 미흡',
    poor: '성능 방안 불충분',
    failing: '성능 무시'
  },
  availability: {
    excellent: 'RTO/RPO 정의, Failover, 다중화 전략 상세',
    good: '가용성 방안 기본 수준 설명',
    fair: '가용성 고려 있으나 구체성 부족',
    poor: '가용성 방안 미흡',
    failing: '가용성 무시'
  },
  reliability: {
    excellent: '데이터 무결성, 트랜잭션, 멱등성, 모니터링 전략 상세',
    good: '신뢰성 방안 기본 수준 설명',
    fair: '신뢰성 고려 있으나 구체성 부족',
    poor: '신뢰성 방안 미흡',
    failing: '신뢰성 무시'
  },
  consistency: {
    excellent: '강한/약한 일관성 선택 및 정당화, 조정 전략 상세',
    good: '일관성 수준 언급, 기본 방안 설명',
    fair: '일관성 고려 있으나 모호',
    poor: '일관성 방안 불명확',
    failing: '일관성 무시'
  },
  security: {
    excellent: '암호화, IAM, VPC, 감사 로깅 등 다층 보안 전략',
    good: '보안 고려, 1-2개 기술 (암호화, IAM 등) 언급',
    fair: '보안 인식 있으나 미흡',
    poor: '보안 방안 불충분',
    failing: '보안 무시'
  }
};

/**
 * OpenAI API 호출
 */
async function callOpenAI(prompt, options = {}) {
  const {
    model = 'gpt-4o-mini',
    maxTokens = 4000,
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
 * 루브릭 포맷팅 (프롬프트 용)
 */
function formatRubricForPrompt() {
  return Object.entries(RUBRIC_GRADES)
    .map(([key, rubric]) => {
      const criteriaText = rubric.criteria.map(c => `   ${c}`).join('\n');
      return `${rubric.emoji} **${rubric.label}** (${rubric.range[0]}-${rubric.range[1]}점)
${criteriaText}`;
    })
    .join('\n\n');
}

/**
 * 축별 루브릭 포맷팅 (프롬프트 용)
 */
function formatAxisRubricForPrompt() {
  return Object.entries(AXIS_SPECIFIC_RUBRICS)
    .map(([axis, rubric]) => {
      const pillar = AXIS_TO_PILLAR[axis];
      return `### ${pillar.emoji} ${pillar.name}
- 우수: ${rubric.excellent}
- 양호: ${rubric.good}
- 보통: ${rubric.fair}
- 미흡: ${rubric.poor}
- 부족: ${rubric.failing}`;
    })
    .join('\n\n');
}

/**
 * axis_weights 포맷팅
 */
function formatAxisWeights(axisWeights) {
  if (!axisWeights || Object.keys(axisWeights).length === 0) {
    return '(가중치 정보 없음 - 균등 평가)';
  }

  const sorted = Object.entries(axisWeights)
    .sort((a, b) => (b[1].weight || 0) - (a[1].weight || 0));

  const formattedWeights = sorted
    .map(([key, value], idx) => {
      const pillar = AXIS_TO_PILLAR[key];
      const weight = value.weight || 0;
      const reason = value.reason || '';

      return `${idx + 1}. ${pillar?.name || key} [가중치: ${weight}%]
   ${reason || ''}`;
    })
    .join('\n\n');

  const totalWeight = sorted.reduce((sum, [_, v]) => sum + (v.weight || 0), 0);
  const weightInfo = totalWeight !== 100 ? `(총합: ${totalWeight}%)` : '';

  return `${formattedWeights}\n\n${weightInfo}`;
}

/**
 * 🔥 루브릭 기반 평가 실행
 */
export async function evaluateWithRubric(
  problem,
  architectureContext,
  userExplanation,
  deepDiveQnA
) {
  console.log('🎯 루브릭 기반 평가 시작...');
  const startTime = Date.now();

  // Step 1: 데이터 준비
  const qnaArray = Array.isArray(deepDiveQnA) ? deepDiveQnA : [];
  const qnaText = qnaArray
    .filter(item => item.answer)
    .map((item, idx) => `
### 질문 ${idx + 1} [${item.category}]
**질문**: ${item.question}
**의도**: ${item.gap || '설계 의도 확인'}
**사용자 답변**: ${item.answer}
`).join('\n');

  // Step 2: 가중치 정보
  const weightInfo = formatAxisWeights(problem?.axis_weights);

  // Step 3: 모든 6개 기둥의 원칙
  const allPrinciples = Object.entries(AXIS_TO_PILLAR)
    .map(([_, pillar]) => `### ${pillar.emoji} ${pillar.name}\n${pillar.principles}`)
    .join('\n\n---\n\n');

  // Step 4: 루브릭 포맷팅
  const rubricGradeFormat = formatRubricForPrompt();
  const axisRubricFormat = formatAxisRubricForPrompt();

  // Step 5: 프롬프트 작성
  const prompt = `당신은 **시니어 클라우드 솔루션 아키텍트**입니다.
지원자의 시스템 아키텍처 설계와 질문 답변을 루브릭 기준으로 평가합니다.

---

## 📋 문제 정보

### 시나리오
${problem?.scenario || '시스템 아키텍처 설계'}

### 미션
${problem?.missions?.map((m, i) => `${i + 1}. ${m}`).join('\n') || '없음'}

### 제약조건
${problem?.constraints?.map((c, i) => `${i + 1}. ${c}`).join('\n') || '없음'}

---

## 🔥 평가 가중치 (문제 특성)

이 문제는 다음 측면들을 중시합니다:

${weightInfo}

---

## 🏗️ 지원자의 아키텍처

${architectureContext}

---

## 💬 지원자의 설계 설명

"${userExplanation || '(설명 없음)'}"

---

## 📝 심화 질문 및 답변

${qnaText || '(질문/답변 없음)'}

---

## 📚 평가 기준 (6대 기둥별 핵심 원칙)

${allPrinciples}

---

## ⭐ 루브릭 기준 (0점부터 시작)

### 공통 기준

${rubricGradeFormat}

### 축별 맞춤형 기준

${axisRubricFormat}

---

## ⚠️ 평가 규칙

### 1. 점수 산정 기준 (중요!)
- **0점부터 시작** - 답변이 없거나 완전 오류면 0점
- **각 기둥별로 정확히 1개 점수만 부여** (0-100)
- **루브릭 등급에 따라 점수 부여**:
  - Excellent: 90-100점
  - Good: 75-89점
  - Fair: 60-74점
  - Poor: 40-59점
  - Failing: 0-39점

### 2. 평가 방법
1. 사용자의 아키텍처 설계를 확인
2. 사용자 설명과 Q&A 답변을 검토
3. 각 기둥별로 위 루브릭 기준을 적용
4. 0-100 범위에서 점수 부여 (정수)
5. **반드시 정확히 6개 기둥 평가**

### 3. 구체적 평가 항목
각 기둥마다:
- ✅ 아키텍처에서 이 기둥을 명시적으로 다뤘는가?
- ✅ 사용자 설명/답변에서 구체적으로 언급했는가?
- ✅ 실제 기술 이름/설정값을 제시했는가?
- ✅ 트레이드오프를 이해하고 있는가?
- ✅ 제약조건을 반영했는가?

### 4. 모범답안
- 이 시나리오와 아키텍처에 맞는 구체적 답변
- 실제 기술/서비스 이름 포함
- 사용자가 배울 수 있도록 상세하게

### 5. 최종 점수 계산
\`\`\`
최종 점수 = Σ(각 기둥 점수 × 해당 기둥 가중치%) / 100
\`\`\`

예시:
- 확장성 80점 × 35% = 28점
- 성능 75점 × 25% = 18.75점
- 가용성 70점 × 15% = 10.5점
- ...
= 최종점수

---

## 출력 형식 (JSON만, 반드시 정확히 6개 기둥)

\`\`\`json
{
  "evaluations": [
    {
      "axis": "scalability",
      "axisName": "확장성",
      "weight": 35,
      "grade": "good",
      "score": 82,
      "reasoning": "아키텍처에서 Redis 캐시와 로드 밸런싱이 명시되었고, 수평 확장을 고려한 설계입니다. 다만 일관된 해싱(Consistent Hashing)과 샤딩 전략의 구체적 설명이 부족합니다.",
      "feedback": "수평 확장은 잘 설계되었으나, 새로운 캐시 노드 추가 시 기존 데이터 재분배 방법을 명시해야 합니다.",
      "modelAnswer": "확장성을 위해 Redis를 일관된 해싱으로 샤딩하여 신규 노드 추가 시 재해싱 비용을 최소화합니다. 각 서버는 CircuitBreaker 패턴으로 캐시 장애를 격리하고, 부하에 따라 자동으로 인스턴스를 증설합니다.",
      "improvements": [
        "일관된 해싱 구현 방식 명시",
        "캐시 워밍 전략 추가",
        "최대 동시 연결 수 정의"
      ]
    },
    {
      "axis": "performance",
      "axisName": "성능",
      "weight": 25,
      "grade": "good",
      "score": 78,
      ...
    },
    ...반드시 정확히 6개...
    {
      "axis": "security",
      "axisName": "보안",
      "weight": 0,
      "grade": "fair",
      "score": 65,
      ...
    }
  ],
  "weightedScores": {
    "scalability": 28.7,
    "performance": 19.5,
    ...
  },
  "overallScore": 76,
  "overallGrade": "good",
  "summary": "전반적으로 잘 설계된 아키텍처입니다. 확장성과 성능 측면에서 탁월한 설계가 보이며, 특히 Redis 기반 캐싱 전략이 효과적입니다. 다만 일관성 관리와 보안 계층(데이터 암호화, IAM)이 다소 부족한 점으로 보입니다.",
  "strengths": [
    "명확한 계층 분리와 수평 확장 가능한 설계",
    "메시지 큐를 통한 비동기 처리로 처리량 확보",
    "캐시 전략으로 응답 지연 최소화"
  ],
  "weaknesses": [
    "트랜잭션 일관성 유지 방법 설명 부족",
    "보안 계층(암호화, IAM) 고려 미흡",
    "장애 복구 시간(RTO) 명확하지 않음"
  ],
  "recommendations": [
    "분산 트랜잭션 처리를 위해 Saga 패턴 학습 추천",
    "데이터 암호화(전송/저장) 설계 추가",
    "재해 복구(RTO/RPO) 시간 목표 정의"
  ]
}
\`\`\`

**주의사항**:
- 반드시 정확히 6개 기둥 (scalability, performance, availability, reliability, consistency, security)
- 각 기둥 점수는 0-100 정수
- 각 기둥에 grade 포함 (excellent, good, fair, poor, failing)
- weightedScores = score × weight / 100
- overallScore = Σ weightedScores (정수로 반올림)
- 반드시 JSON 형식만 출력`;

  try {
    const response = await callOpenAI(prompt, {
      maxTokens: 4500,
      temperature: 0.5
    });

    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const result = JSON.parse(jsonMatch[0]);

      const endTime = Date.now();
      console.log(`✅ 루브릭 평가 완료 (${((endTime - startTime) / 1000).toFixed(1)}s)`);

      // 🔥 questionEvaluations 구성: deepDiveQnA와 evaluations 매칭
      const questionEvaluations = (result.evaluations || []).slice(0, 3).map((ev, idx) => ({
        ...ev,
        question: qnaArray[idx]?.question || '',
        userAnswer: qnaArray[idx]?.answer || '',
        category: qnaArray[idx]?.category || ev.axisName || ''
      }));

      // 결과 포맷팅 (루브릭 정보 포함)
      return {
        // 최종 점수
        score: result.overallScore,
        totalScore: result.overallScore,
        grade: result.overallGrade,
        summary: result.summary,
        strengths: result.strengths || [],
        weaknesses: result.weaknesses || [],
        suggestions: result.recommendations || [],

        // 🔥 6개 기둥별 루브릭 평가
        evaluations: result.evaluations || [],

        // 기둥별 가중치 적용 점수
        weightedScores: result.weightedScores || {},

        // 기존 호환성 유지 (question, userAnswer 포함)
        questionEvaluations,
        pillarScores: buildPillarScores(result.evaluations || []),
        nfrScores: buildNfrScores(result.evaluations || []),

        // 메타데이터
        metadata: {
          method: 'rubric',
          rubricType: 'comprehensive',
          axisWeights: problem?.axis_weights,
          evaluatedAt: new Date().toISOString()
        }
      };
    }
    throw new Error('Invalid JSON');
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
    scalability: 'scalability',
    performance: 'performanceOptimization',
    availability: 'availability',
    reliability: 'reliability',
    consistency: 'consistency',
    security: 'securityPrivacyCompliance'
  };

  const scores = {
    scalability: 0,
    performanceOptimization: 0,
    availability: 0,
    reliability: 0,
    consistency: 0,
    securityPrivacyCompliance: 0
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
    scalability: { score: 0, feedback: '', grade: 'fair' },
    availability: { score: 0, feedback: '', grade: 'fair' },
    performance: { score: 0, feedback: '', grade: 'fair' },
    consistency: { score: 0, feedback: '', grade: 'fair' },
    reliability: { score: 0, feedback: '', grade: 'fair' }
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
 * 에러 시 기본 결과 생성 (루브릭 기반)
 */
function generateFallbackResult(qnaArray, axisWeights) {
  console.warn('⚠️ 루브릭 Fallback 평가 사용');

  const baseEvaluations = Object.entries(AXIS_TO_PILLAR).map(([axis, pillar]) => {
    const weight = axisWeights?.[axis]?.weight || 0;
    // 가중치가 높을수록 더 낮은 등급 부여 (Fallback)
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
      axisName: pillar.name,
      weight,
      grade,
      score,
      feedback: '평가 중 오류가 발생했습니다.',
      modelAnswer: '',
      improvements: []
    };
  });

  // 🔥 questionEvaluations 구성: qnaArray와 매칭
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
export { extractPrinciples, formatAxisWeights, AXIS_TO_PILLAR, RUBRIC_GRADES };
