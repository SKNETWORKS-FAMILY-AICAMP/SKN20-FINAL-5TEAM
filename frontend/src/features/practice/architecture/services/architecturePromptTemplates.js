/**
 * Architecture Rubric Evaluation - Prompt Templates
 *
 * [작성일: 2026-02-20]
 * 루브릭 기반 평가용 프롬프트 생성 함수들
 * 프론트엔드에서 프롬프트를 생성한 후 백엔드로 전송
 */

// JSON 파일에서 핵심 원칙 import
import reliabilityJson from '../data/Reliability.json';
import performanceJson from '../data/Performance_Optimization.json';
import operationalJson from '../data/Operational_Excellence.json';
import costJson from '../data/Cost_Optimization.json';
import securityJson from '../data/Security.json';
import sustainabilityJson from '../data/Sustainability.json';

/**
 * JSON 파일에서 "핵심 원칙" 섹션 추출
 */
function extractPrinciples(jsonData) {
  try {
    const sections = jsonData?.content?.sections || [];
    const principleSection = sections.find(section => section.heading === '핵심 원칙');

    if (!principleSection) {
      console.warn('⚠️ "핵심 원칙" 섹션을 찾을 수 없습니다.');
      return '';
    }

    const listContent = principleSection.content.find(c => c.type === 'list');

    if (!listContent || !listContent.items) {
      console.warn('⚠️ 핵심 원칙 목록을 찾을 수 없습니다.');
      return '';
    }

    return listContent.items
      .map(item => `- ${item}`)
      .join('\n\n');
  } catch (error) {
    console.error('❌ 핵심 원칙 추출 실패:', error);
    return '';
  }
}

/**
 * 6대 기둥 매핑
 */
const AXIS_TO_PILLAR = {
  performance_optimization: {
    name: '성능 최적화 (Performance Optimization)',
    emoji: '⚡',
    principles: extractPrinciples(performanceJson)
  },
  reliability: {
    name: '신뢰성 (Reliability)',
    emoji: '🏗️',
    principles: extractPrinciples(reliabilityJson)
  },
  operational_excellence: {
    name: '운영 우수성 (Operational Excellence)',
    emoji: '⚙️',
    principles: extractPrinciples(operationalJson)
  },
  cost_optimization: {
    name: '비용 최적화 (Cost Optimization)',
    emoji: '💰',
    principles: extractPrinciples(costJson)
  },
  security: {
    name: '보안 (Security)',
    emoji: '🔐',
    principles: extractPrinciples(securityJson)
  },
  sustainability: {
    name: '지속가능성 (Sustainability)',
    emoji: '🌱',
    principles: extractPrinciples(sustainabilityJson)
  }
};

/**
 * 루브릭 기준 정의
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
 * 축별 맞춤형 루브릭
 */
const AXIS_SPECIFIC_RUBRICS = {
  performance_optimization: {
    excellent: 'latency 목표값, 캐싱 전략, 인덱싱, 샤딩 등 구체적 최적화 방안과 트레이드오프 설명',
    good: '성능 최적화 고려, 캐시/인덱싱 등 1-2개 기술 언급',
    fair: '성능 최적화 인식 있으나 구체성 부족',
    poor: '성능 최적화 방안 불충분',
    failing: '성능 최적화 무시'
  },
  reliability: {
    excellent: '데이터 무결성, 트랜잭션, 멱등성, RTO/RPO, Failover, 모니터링 전략 상세',
    good: '신뢰성 방안 기본 수준 설명 (복제, 백업 등)',
    fair: '신뢰성 고려 있으나 구체성 부족',
    poor: '신뢰성 방안 미흡',
    failing: '신뢰성 무시'
  },
  operational_excellence: {
    excellent: '자동화, 모니터링, 로깅, 배포 전략, IaC, 장애 대응 프로세스 상세',
    good: '운영 측면 고려, 모니터링/로깅 등 기본 방안 언급',
    fair: '운영 고려 있으나 구체성 부족',
    poor: '운영 방안 미흡',
    failing: '운영 측면 무시'
  },
  cost_optimization: {
    excellent: '리소스 최적화, 예약 인스턴스, 스팟 인스턴스, 스토리지 계층화, 비용 모니터링 상세',
    good: '비용 고려, 리소스 효율화 등 1-2개 방안 언급',
    fair: '비용 인식 있으나 구체성 부족',
    poor: '비용 최적화 방안 미흡',
    failing: '비용 측면 무시'
  },
  security: {
    excellent: '암호화(전송/저장), IAM, VPC, 최소 권한, 감사 로깅, 규정 준수 등 다층 보안 전략',
    good: '보안 고려, 1-2개 기술 (암호화, IAM 등) 언급',
    fair: '보안 인식 있으나 미흡',
    poor: '보안 방안 불충분',
    failing: '보안 무시'
  },
  sustainability: {
    excellent: '에너지 효율, 리소스 활용 최적화, 탄소 배출 최소화, 지역 선택 전략 상세',
    good: '지속가능성 고려, 리소스 효율화 등 기본 방안 언급',
    fair: '지속가능성 인식 있으나 구체성 부족',
    poor: '지속가능성 방안 미흡',
    failing: '지속가능성 무시'
  }
};

/**
 * 루브릭 포맷팅
 */
function formatRubricForPrompt() {
  return Object.entries(RUBRIC_GRADES)
    .map(([key, rubric]) => {
      const criteriaText = rubric.criteria.map(c => `   ${c}`).join('\n');
      return `${rubric.emoji} **${rubric.label}** (${rubric.range[0]}-${rubric.range[1]}점)\n${criteriaText}`;
    })
    .join('\n\n');
}

/**
 * 축별 루브릭 포맷팅
 */
function formatAxisRubricForPrompt() {
  return Object.entries(AXIS_SPECIFIC_RUBRICS)
    .map(([axis, rubric]) => {
      const pillar = AXIS_TO_PILLAR[axis];
      return `### ${pillar.emoji} ${pillar.name}\n- 우수: ${rubric.excellent}\n- 양호: ${rubric.good}\n- 보통: ${rubric.fair}\n- 미흡: ${rubric.poor}\n- 부족: ${rubric.failing}`;
    })
    .join('\n\n');
}

/**
 * axis_weights 포맷팅
 */
export function formatAxisWeights(axisWeights) {
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

      return `${idx + 1}. ${pillar?.name || key} [가중치: ${weight}%]\n   ${reason || ''}`;
    })
    .join('\n\n');

  const totalWeight = sorted.reduce((sum, [_, v]) => sum + (v.weight || 0), 0);
  const weightInfo = totalWeight !== 100 ? `(총합: ${totalWeight}%)` : '';

  return `${formattedWeights}\n\n${weightInfo}`;
}

/**
 * 🔥 루브릭 평가 프롬프트 생성
 */
export function generateRubricPrompt(problem, architectureContext, userExplanation, deepDiveQnA) {
  // 데이터 준비
  const qnaArray = Array.isArray(deepDiveQnA) ? deepDiveQnA : [];
  const qnaText = qnaArray
    .filter(item => item.answer)
    .map((item, idx) => `
### 질문 ${idx + 1} [${item.category}]
**질문**: ${item.question}
**의도**: ${item.gap || '설계 의도 확인'}
**사용자 답변**: ${item.answer}
`).join('\n');

  // 가중치 정보
  const weightInfo = formatAxisWeights(problem?.axis_weights);

  // 모든 6개 기둥의 원칙
  const allPrinciples = Object.entries(AXIS_TO_PILLAR)
    .map(([_, pillar]) => `### ${pillar.emoji} ${pillar.name}\n${pillar.principles}`)
    .join('\n\n---\n\n');

  // 루브릭 포맷팅
  const rubricGradeFormat = formatRubricForPrompt();
  const axisRubricFormat = formatAxisRubricForPrompt();

  // 프롬프트 작성
  return `당신은 **시니어 클라우드 솔루션 아키텍트**입니다.
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
5. **각 기둥마다 정확히 5-7문장의 modelAnswer 작성**
6. **반드시 정확히 6개 기둥 평가**

### 3. 구체적 평가 항목
각 기둥마다:
- ✅ 아키텍처에서 이 기둥을 명시적으로 다뤘는가?
- ✅ 사용자 설명/답변에서 구체적으로 언급했는가?
- ✅ 실제 기술 이름/설정값을 제시했는가?
- ✅ 트레이드오프를 이해하고 있는가?
- ✅ 제약조건을 반영했는가?

### 4. 모범답안 (필수: 정확히 5-7문장)
- 이 시나리오와 아키텍처에 맞는 구체적 답변
- 실제 기술/서비스 이름과 설정값 포함 (예: Redis 일관된 해싱, 100ms latency 목표)
- 트레이드오프와 선택 이유를 명시적으로 설명
- 사용자가 배울 수 있도록 상세하게
- **반드시 정확히 5-7문장으로 작성** (너무 짧으면 안됨, 예: 2-3문장 X)

### 5. 최종 점수 계산
\`\`\`
최종 점수 = Σ(각 기둥 점수 × 해당 기둥 가중치%) / 100
\`\`\`

---

## 출력 형식 (JSON만, 반드시 정확히 6개 기둥)

반드시 다음 JSON 형식으로 응답하세요:

\`\`\`json
{
  "evaluations": [
    {
      "axis": "performance_optimization",
      "axisName": "성능 최적화",
      "weight": 30,
      "grade": "good",
      "score": 82,
      "feedback": "구체적인 피드백",
      "improvements": ["개선점 1", "개선점 2"]
    },
    ...정확히 6개...
  ],
  "overallScore": 76,
  "overallGrade": "good",
  "summary": "전반적인 평가 요약",
  "strengths": ["강점 1", "강점 2"],
  "weaknesses": ["약점 1"],
  "recommendations": ["추천사항 1"]
}
\`\`\`

**주의사항**:
- 반드시 정확히 6개 기둥 (performance_optimization, reliability, operational_excellence, cost_optimization, security, sustainability)
- 각 기둥 점수는 0-100 정수
- 반드시 JSON 형식만 출력`;
}
