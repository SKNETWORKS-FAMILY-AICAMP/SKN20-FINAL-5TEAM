/**
 * Architecture Question Generator v2
 *
 * 시니어 아키텍트의 관점에서 지원자 설계를 검증
 *
 * 개선사항:
 * 1. 안티패턴 탐지 기반 프롬프트 (교과서식 질문 탈피)
 * 2. 관련성 높은 기둥만 선별 주입 (정보과부하 해결)
 * 3. 컴포넌트를 Role-based로 분류 (이해도 향상)
 * 4. Chain of Thought 강제 (추론의 정확도 향상)
 */

import reliabilityTxt from '@/data/신뢰성.txt?raw';
import performanceTxt from '@/data/최적화.txt?raw';
import operationalTxt from '@/data/운영유용성.txt?raw';
import costTxt from '@/data/비용.txt?raw';
import securityTxt from '@/data/보안.txt?raw';
import sustainabilityTxt from '@/data/지속가능성.txt?raw';

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

/**
 * ============================================================================
 * PART 1: 데이터 설정 및 초기화
 * ============================================================================
 */

/**
 * txt 파일에서 [핵심 분석 원칙] 섹션 추출
 */
function extractPrinciples(txtContent) {
  const match = txtContent.match(/### \[핵심 분석 원칙[^\]]*\]\s*([\s\S]*?)(?=### \[|$)/);
  return match ? match[1].trim() : '';
}

/**
 * 6대 기둥 정보 (전체 - 나중에 필터링됨)
 */
const ALL_PILLARS = {
  reliability: {
    name: '신뢰성 (Reliability)',
    engName: 'Reliability',
    principles: extractPrinciples(reliabilityTxt),
    keywords: ['장애', '복구', '이중화', '백업', '데이터보호', 'failover', 'redundancy']
  },
  performance: {
    name: '성능 최적화 (Performance)',
    engName: 'Performance',
    principles: extractPrinciples(performanceTxt),
    keywords: ['응답속도', '처리량', '캐싱', '인덱싱', '최적화', 'latency', 'throughput']
  },
  operational: {
    name: '운영 우수성 (Operational Excellence)',
    engName: 'Operational Excellence',
    principles: extractPrinciples(operationalTxt),
    keywords: ['모니터링', '로깅', '알림', '자동화', '관리', 'monitoring', 'automation']
  },
  cost: {
    name: '비용 최적화 (Cost Optimization)',
    engName: 'Cost Optimization',
    principles: extractPrinciples(costTxt),
    keywords: ['비용', '효율', '리소스', '최소화', 'scaling', 'resource']
  },
  security: {
    name: '보안 (Security)',
    engName: 'Security',
    principles: extractPrinciples(securityTxt),
    keywords: ['보안', '암호화', '인증', '권한', '격리', 'encryption', 'authentication']
  },
  sustainability: {
    name: '지속 가능성 (Sustainability)',
    engName: 'Sustainability',
    principles: extractPrinciples(sustainabilityTxt),
    keywords: ['환경', '효율', '지속', '탄소', 'environmental', 'green']
  }
};

/**
 * ============================================================================
 * PART 2: 핵심 기둥 필터링 (정보과부하 해결)
 * ============================================================================
 */

/**
 * 문제 설명에 기반해 상위 N개의 관련성 높은 기둥만 선별
 * @param {Object} problem - 문제 객체
 * @param {number} topN - 선택할 기둥 개수 (기본값: 4)
 * @returns {Object} - { selectedPillars, relevanceScores }
 */
function selectRelevantPillars(problem, topN = 4) {
  const missions = problem?.missions || [];
  const constraints = problem?.constraints || [];
  const scenario = problem?.scenario || '';

  const allText = [
    ...missions,
    ...constraints,
    scenario
  ].join(' ').toLowerCase();

  const scores = {};

  Object.entries(ALL_PILLARS).forEach(([key, pillar]) => {
    let score = 0;

    // 키워드 매칭 (가중치: +10)
    pillar.keywords.forEach(kw => {
      if (allText.includes(kw)) score += 10;
    });

    // 기둥명 정확 매칭 (가중치: +20)
    if (allText.includes(pillar.engName.toLowerCase())) score += 20;

    scores[key] = score;
  });

  // 점수 기반 정렬 후 상위 N개 선택
  const selected = Object.entries(scores)
    .sort((a, b) => b[1] - a[1])
    .slice(0, topN)
    .map(([key]) => key);

  return {
    selectedPillars: selected,
    relevanceScores: scores,
    selectedData: selected.reduce((acc, key) => {
      acc[key] = ALL_PILLARS[key];
      return acc;
    }, {})
  };
}

/**
 * ============================================================================
 * PART 3: 컴포넌트 Role-based 분류 (구조적 이해 강화)
 * ============================================================================
 */

/**
 * 컴포넌트 타입별 역할 분류
 */
const COMPONENT_ROLES = {
  'entry': ['Client', 'User', 'API Gateway', 'Load Balancer', 'CDN'],
  'compute': ['Server', 'Lambda', 'Compute', 'EC2', 'Container', 'Function', 'Worker'],
  'storage': ['Database', 'DB', 'Cache', 'Redis', 'S3', 'Storage', 'Queue', 'Message'],
  'security': ['Auth', 'Security', 'WAF', 'Firewall', 'Vault', 'Secret'],
  'monitoring': ['Monitor', 'Log', 'Alert', 'Trace', 'CloudWatch', 'Dashboard']
};

/**
 * 컴포넌트의 역할 결정 (타입 기반)
 */
function getComponentRole(component) {
  const type = component.type.toLowerCase();
  const text = (component.text || '').toLowerCase();

  for (const [role, keywords] of Object.entries(COMPONENT_ROLES)) {
    if (keywords.some(kw => type.includes(kw.toLowerCase()) || text.includes(kw.toLowerCase()))) {
      return role;
    }
  }

  return 'other';
}

/**
 * 컴포넌트를 Role-based로 분류하여 정리
 */
function categorizeComponentsByRole(components) {
  const categorized = {
    entry: [],
    compute: [],
    storage: [],
    security: [],
    monitoring: [],
    other: []
  };

  components.forEach(comp => {
    const role = getComponentRole(comp);
    categorized[role].push(comp);
  });

  return categorized;
}

/**
 * 분류된 컴포넌트를 구조화된 형태로 표현
 */
function formatCategorizedComponents(categorized) {
  const roleLabels = {
    entry: '🚪 Entry Points (진입점)',
    compute: '⚙️ Compute (계산 계층)',
    storage: '💾 Storage (저장소)',
    security: '🔒 Security (보안 계층)',
    monitoring: '📊 Monitoring (관찰/알림)',
    other: '❓ Others'
  };

  let formatted = '';
  for (const [role, components] of Object.entries(categorized)) {
    if (components.length === 0) continue;
    formatted += `\n### ${roleLabels[role]}\n`;
    components.forEach(comp => {
      formatted += `- ${comp.text} (타입: ${comp.type})\n`;
    });
  }

  return formatted;
}

/**
 * ============================================================================
 * PART 4: 안티패턴 탐지 (설계의 모순 찾기)
 * ============================================================================
 */

/**
 * 안티패턴 체크리스트 (기둥별)
 */
const ANTIPATTERN_CHECKLIST = {
  reliability: [
    'SPOF(Single Point of Failure) 존재 여부',
    'DB가 Public Subnet에 있는지 확인',
    '단일 경로만 존재하는 구조',
    '재시도(Retry) 메커니즘 부재',
    '장애 자동 복구(Failover) 전략 부재'
  ],
  performance: [
    'DB가 모든 읽기 요청에서 병목인 구조',
    '캐시 계층 부재',
    'DB에 직접 연결된 클라이언트 (n-tier 위반)',
    '배치 처리 대신 개별 요청 처리',
    '샤딩/파티셔닝 전략 부재'
  ],
  operational: [
    '모니터링/로깅 전략 정의 부재',
    '알림 채널 부재',
    '수동 운영 구조 (자동화 부족)',
    '운영 대시보드 불명확',
    '배포 프로세스 정의 부재'
  ],
  cost: [
    '과도한 리소스 할당',
    '중복 리소스 배치',
    '스케일링 전략 없음',
    '불필요한 중복 컴포넌트',
    'Reserved Instance 또는 Spot 활용 전략 부재'
  ],
  security: [
    'Public Subnet의 민감 데이터',
    '인증/인가 계층 부재',
    '암호화 전략 정의 부재',
    '네트워크 격리 구조 불명확',
    '권한 기반 접근제어(RBAC) 구조 부재'
  ],
  sustainability: [
    '리소스 낭비 구조',
    '에너지 효율 고려 부재',
    '자동 확장 전략 부재',
    '불필요한 중복 배치'
  ]
};

/**
 * 아키텍처에서 발견 가능한 안티패턴을 체계적으로 분석
 */
function generateAntipatternsForAnalysis(pillarKey, components, connections) {
  const checklist = ANTIPATTERN_CHECKLIST[pillarKey] || [];

  // 관련 패턴만 리스트로 반환 (프롬프트에 삽입)
  return checklist.slice(0, 3).join('\n- ');
}

/**
 * ============================================================================
 * PART 5: OpenAI API 호출
 * ============================================================================
 */

async function callOpenAI(prompt, options = {}) {
  const {
    model = 'gpt-4o-mini',
    maxTokens = 1000,
    temperature = 0.7
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
 * ============================================================================
 * PART 6: 질문 생성 (CoT + 안티패턴 기반)
 * ============================================================================
 */

/**
 * 특정 기둥에 대해 고품질 질문 1개 생성
 *
 * 프롬프트 전략:
 * - Chain of Thought 강제 (내부 처리)
 * - 안티패턴 체크리스트 명시
 * - 교과서적 질문 회피 지시
 */
async function generateQuestionForPillar(
  pillarKey,
  problem,
  components,
  connections,
  mermaidCode,
  userExplanation,
  relatedPillarsData
) {
  const pillarData = relatedPillarsData[pillarKey];
  if (!pillarData) return null;

  // 데이터 전처리
  const categorized = categorizeComponentsByRole(components);
  const categorizedStr = formatCategorizedComponents(categorized);
  const connectionList = connections.map(conn => {
    const from = components.find(c => c.id === conn.from);
    const to = components.find(c => c.id === conn.to);
    return from && to ? `- ${from.text} → ${to.text}` : null;
  }).filter(Boolean).join('\n');

  const scenario = problem?.scenario || '';
  const constraints = problem?.constraints || [];
  const missions = problem?.missions || [];
  const antipatterns = generateAntipatternsForAnalysis(pillarKey, components, connections);

  const prompt = `당신은 **${pillarData.name} 전문가**입니다. Google Well-Architected Framework의 관점에서 지원자의 설계를 평가합니다.

## 당신의 임무
지원자의 아키텍처에서 **${pillarData.name} 관점의 문제점 또는 설계 선택의 의도를 파악**할 수 있는 질문을 생성하세요.

---

## 📋 문제 상황

**시나리오:** ${scenario || '시스템 아키텍처 설계'}

**미션:**
${missions.length > 0 ? missions.map((m, i) => `${i + 1}. ${m}`).join('\n') : '(없음)'}

**제약조건:**
${constraints.length > 0 ? constraints.map((c, i) => `${i + 1}. ${c}`).join('\n') : '(없음)'}

---

## 🏗️ 지원자의 아키텍처

### 컴포넌트 (역할별 분류)
${categorizedStr}

### 데이터 흐름
${connectionList || '(없음)'}

### Mermaid 다이어그램
\`\`\`mermaid
${mermaidCode || 'graph LR'}
\`\`\`

---

## 💬 지원자의 설명
"${userExplanation || '(설명 없음)'}"

---

## 🎯 ${pillarData.name} 관점에서 확인해야 할 안티패턴

- ${antipatterns}

이 체크리스트 항목들 중에서 **이 아키텍처에 실제로 존재하는 문제**를 파악하고 질문을 생성하세요.

---

## 📚 ${pillarData.name} 분석 원칙

${pillarData.principles}

---

## 🧠 질문 생성 프로세스 (내부 사고)

먼저 다음을 생각하세요 (JSON 출력 전에):
1. 이 아키텍처에서 ${pillarData.name} 관점의 강점과 약점은?
2. 위 안티패턴 중 어떤 것이 실제로 존재하는가?
3. 지원자가 이 선택을 한 **의도**는 무엇인가? (의도를 파악하는 질문)
4. 시나리오의 특정 상황에서 이 설계가 어떻게 작동하는가?

---

## 📝 질문 생성 규칙

**✅ 해야 할 것:**
- **상황 기반**: "만약 ~ 상황이 발생하면" 형태
- **구체적**: 실제 배치된 컴포넌트를 언급
- **의도 파악**: 설계자의 선택 이유를 묻기
- **설계 검증**: 안티패턴의 존재/부재를 확인
- **개방형**: 단순 Yes/No가 아닌 설명 요구

**❌ 피해야 할 것:**
- 일반적인 교과서식 질문
- 이미 설명한 내용 재질문
- 부족한 부분 나열만 하기
- 전문 용어 나열

---

## 출력 형식 (JSON만)

{
  "pillar": "${pillarKey}",
  "pillarName": "${pillarData.name}",
  "thought_process": "위에서 생각한 내용을 1-2줄로 요약",
  "assessment": "이 관점에서 아키텍처의 강점/약점 평가 (1-2줄)",
  "question": "구체적이고 상황 기반의 질문"
}`;

  try {
    const response = await callOpenAI(prompt, {
      maxTokens: 900,
      temperature: 0.7
    });

    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return {
        pillar: pillarKey,
        pillarName: pillarData.name,
        assessment: parsed.assessment || '',
        question: parsed.question || '',
        thought_process: parsed.thought_process || '',
        success: true
      };
    }
    throw new Error('Invalid JSON response');
  } catch (error) {
    console.error(`❌ 질문 생성 실패 (${pillarKey}):`, error);

    // Fallback 질문 (기본값)
    const fallbacks = {
      reliability: {
        assessment: '장애 복구 메커니즘이 명확하지 않음',
        question: `${components[0]?.text || '핵심 컴포넌트'}가 다운되면 서비스는 어떻게 되나요? 자동으로 다른 경로로 우회하거나 복구되는 구조인가요?`
      },
      performance: {
        assessment: '확장 전략이 불명확함',
        question: `동시 사용자가 10배로 늘어나면, 이 아키텍처는 자동으로 성능을 유지할 수 있나요? 어느 부분이 병목이 될 것 같나요?`
      },
      operational: {
        assessment: '모니터링 체계가 정의되지 않음',
        question: `시스템에 장애가 발생했을 때, 운영팀이 **사용자보다 먼저** 알 수 있는 구조가 있나요?`
      },
      cost: {
        assessment: '비용 효율성 고려가 부족함',
        question: `리소스 사용량을 최소화하기 위해 어떤 방식을 택했나요? 불필요한 중복이나 과도한 할당은 없나요?`
      },
      security: {
        assessment: '보안 계층이 명확하지 않음',
        question: `외부 공격자가 시스템에 접근하려고 할 때, 어떤 계층에서 차단되나요? 인증, 암호화, 데이터 격리는 어떻게 구성되나요?`
      },
      sustainability: {
        assessment: '환경/효율성 고려가 부족함',
        question: `이 아키텍처를 운영하는 데 필요한 리소스(에너지, 인프라)를 최소화하는 방법은 무엇인가요?`
      }
    };

    const fallback = fallbacks[pillarKey] || fallbacks.reliability;
    return {
      pillar: pillarKey,
      pillarName: pillarData.name,
      assessment: fallback.assessment,
      question: fallback.question,
      thought_process: '(Fallback 질문)',
      success: false
    };
  }
}

/**
 * ============================================================================
 * PART 7: 질문 품질 평가 및 선별
 * ============================================================================
 */

/**
 * 질문 품질 점수화 (0~100)
 */
function evaluateQuestionQuality(question, components, pillarKeywords) {
  let score = 0;

  // 1. 컴포넌트 언급 (최대 40점)
  const hasComponentRef = components.some(c =>
    question.question.includes(c.text)
  );
  score += hasComponentRef ? 40 : 15;

  // 2. 상황 기반 표현 (최대 35점)
  const situationalPatterns = /~하면|~한다면|만약|발생|상황|동안|될 때|된다면|경우/;
  score += situationalPatterns.test(question.question) ? 35 : 20;

  // 3. 성공 여부 (최대 25점)
  score += question.success ? 25 : 0;

  return Math.min(100, score);
}

/**
 * 여러 질문 중 점수 기반으로 상위 3개 선택
 */
function selectTopThreeQuestions(allQuestions, components) {
  const scored = allQuestions
    .filter(q => q !== null)
    .map(q => ({
      ...q,
      qualityScore: evaluateQuestionQuality(q, components, ALL_PILLARS[q.pillar]?.keywords || [])
    }))
    .sort((a, b) => b.qualityScore - a.qualityScore);

  return scored.slice(0, 3).map((q, idx) => ({
    ...q,
    rank: idx + 1
  }));
}

/**
 * ============================================================================
 * PART 8: 메인 함수
 * ============================================================================
 */

/**
 * 메인 함수: 최적화된 질문 생성 파이프라인
 */
export async function generateQuestionsFromAllPillars(
  problem,
  components,
  connections,
  mermaidCode,
  userExplanation,
  axisWeights = {}
) {
  try {
    // 🔍 Step 1: 관련성 높은 기둥만 필터링
    const { selectedPillars, selectedData } = selectRelevantPillars(problem, 4);

    // 🚀 Step 2: 선택된 기둥들에서만 병렬로 질문 생성
    const questionPromises = selectedPillars.map(pillarKey =>
      generateQuestionForPillar(
        pillarKey,
        problem,
        components,
        connections,
        mermaidCode,
        userExplanation,
        selectedData
      )
    );

    const allQuestions = await Promise.all(questionPromises);

    // ⭐ Step 3: 상위 3개 선별
    const topThree = selectTopThreeQuestions(allQuestions, components);

    // 📊 Step 4: 최종 응답 포맷팅
    return {
      success: true,
      generatedQuestions: topThree.length,
      questions: topThree.map(q => ({
        rank: q.rank,
        category: q.pillarName,
        pillar: q.pillar,
        assessment: q.assessment,
        question: q.question,
        quality: q.qualityScore
      }))
    };
  } catch (error) {
    console.error('❌ 질문 생성 전체 실패:', error);

    // Fallback: 기본 3개 질문
    return {
      success: false,
      error: error.message,
      questions: [
        {
          rank: 1,
          category: '신뢰성 (Reliability)',
          pillar: 'reliability',
          assessment: '장애 대응 전략이 불명확함',
          question: `${components[0]?.text || '핵심 컴포넌트'}가 갑자기 다운되면, 사용자는 어떤 경험을 하게 되나요?`
        },
        {
          rank: 2,
          category: '성능 최적화 (Performance)',
          pillar: 'performance',
          assessment: '확장 전략이 불명확함',
          question: `동시 사용자가 10배로 늘어나면, 이 아키텍처가 자동으로 처리량을 늘릴 수 있나요?`
        },
        {
          rank: 3,
          category: '운영 우수성 (Operational Excellence)',
          pillar: 'operational',
          assessment: '모니터링/알림 체계가 정의되지 않음',
          question: `시스템에 문제가 생겼을 때, 운영팀이 사용자보다 먼저 알 수 있는 방법이 있나요?`
        }
      ]
    };
  }
}

export { ALL_PILLARS };
