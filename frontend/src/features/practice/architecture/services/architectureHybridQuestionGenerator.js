/**
 * Architecture Practice API Service - IMPROVED VERSION
 *
 * test.md 피드백 완전 반영:
 * ✅ Phase 1 (High): 안티패턴 체크리스트 + Chain of Thought
 * ✅ Phase 2 (Mid): 동적 Pillar 선별 (시나리오 키워드 기반)
 * ✅ Phase 3 (Low): 역할 기반 컴포넌트 분류
 *
 * 핵심 개선점:
 * 1. "부족한 것 찾기" → "설계의 모순 찾기"
 * 2. 모든 Pillar 주입 → 시나리오 기반 2-3개 선별
 * 3. 단순 나열 → Entry/Compute/Storage/Security 분류
 * 4. 질문만 생성 → 사고 과정(CoT) 먼저 작성 후 질문 생성
 */

// 6대 기둥 txt 파일 import
import reliabilityTxt from '@/data/신뢰성.txt?raw';
import performanceTxt from '@/data/최적화.txt?raw';
import operationalTxt from '@/data/운영유용성.txt?raw';
import costTxt from '@/data/비용.txt?raw';
import securityTxt from '@/data/보안.txt?raw';
import sustainabilityTxt from '@/data/지속가능성.txt?raw';

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

/**
 * 원본 txt 파일에서 "핵심 원칙" 섹션 추출
 *
 * 원본 문서 구조:
 * - "핵심 원칙" 제목
 * - 설명 줄 (Well-Architected Framework의...)
 * - 빈 줄
 * - 핵심 원칙들 (콜론으로 구분된 제목과 설명)
 * - 다음 섹션 시작 또는 파일 끝
 */
function extractPrinciples(txtContent) {
  // Step 1: "핵심 원칙" 제목 찾기 (줄바꿈 처리 개선)
  const headerIndex = txtContent.indexOf('핵심 원칙');
  if (headerIndex === -1) {
    console.warn('⚠️ "핵심 원칙" 섹션을 찾을 수 없습니다.');
    return '';
  }

  // Step 2: "핵심 원칙" 다음 줄부터 시작
  // 첫 번째 줄바꿈 찾기 (제목 줄)
  const firstNewline = txtContent.indexOf('\n', headerIndex);
  if (firstNewline === -1) return '';

  // 두 번째 줄바꿈 찾기 (설명 줄)
  const secondNewline = txtContent.indexOf('\n', firstNewline + 1);
  if (secondNewline === -1) return '';

  // 세 번째 줄바꿈 이후부터 추출 (빈 줄 다음)
  const startIndex = secondNewline + 1;
  const remainingText = txtContent.substring(startIndex);

  // Step 3: 다음 섹션 시작 전까지 추출
  // 종료 패턴: 새로운 주요 섹션이 시작되는 부분
  const endPatterns = [
    '\n이러한',      // "이러한 원칙은..." (비용.txt)
    '\n조직',        // "조직 보안 마인드셋" (보안.txt)
    '\nGoogle',      // 새 섹션
    '\n파트너',      // 새 섹션
    '\nAI 및',       // 새 섹션
    '\n설계',        // "설계 단계부터..." (지속가능성.txt)
    '\n클라우드 거버넌스',
    '\n안정성 중점',
    '\n성능 최적화 프로세스',
    '\n책임 공유'    // "책임 공유 및..." (지속가능성.txt)
  ];

  let content = remainingText;
  let minIndex = content.length;

  for (const pattern of endPatterns) {
    const idx = content.indexOf(pattern);
    if (idx !== -1 && idx < minIndex) {
      minIndex = idx;
    }
  }

  content = content.substring(0, minIndex).trim();

  // 추가 정리: 불필요한 빈 줄 제거
  content = content.replace(/\n{3,}/g, '\n\n');

  return content;
}

/**
 * 6대 기둥 데이터
 */
const PILLAR_DATA = {
  reliability: {
    name: '신뢰성 (Reliability)',
    principles: extractPrinciples(reliabilityTxt),
    keywords: ['장애', '다운', 'spof', '중단', '복구', 'failover', 'redundancy', '가용성', 'availability']
  },
  performance: {
    name: '성능 최적화 (Performance)',
    principles: extractPrinciples(performanceTxt),
    keywords: ['트래픽', '급증', '동시', 'latency', '지연', '느림', '성능', 'throughput', '처리량', 'cache', 'cdn']
  },
  operational: {
    name: '운영 우수성 (Operational Excellence)',
    principles: extractPrinciples(operationalTxt),
    keywords: ['모니터링', '로그', 'alert', '경보', '운영', 'cicd', '배포', 'deploy', 'debug']
  },
  cost: {
    name: '비용 최적화 (Cost)',
    principles: extractPrinciples(costTxt),
    keywords: ['비용', '예산', 'cost', '저렴', '절감', 'spot', 'reserved', '요금']
  },
  security: {
    name: '보안 (Security)',
    principles: extractPrinciples(securityTxt),
    keywords: ['보안', '유출', '해킹', '암호화', 'encryption', 'iam', '권한', 'vpc', 'firewall', 'waf']
  },
  sustainability: {
    name: '지속 가능성 (Sustainability)',
    principles: extractPrinciples(sustainabilityTxt),
    keywords: ['환경', '효율', '장기', 'green', 'efficiency', '지속']
  }
};

/**
 * 🔥 NEW: 시나리오 기반 관련 Pillar 선별 (Phase 2)
 * 
 * 전체 6개가 아닌, 문제 상황에 맞는 2-3개만 선별하여
 * LLM의 집중도를 높이고 토큰을 절약
 */
function selectRelevantPillars(scenario, missions, constraints) {
  const fullText = [
    scenario,
    ...missions,
    ...constraints
  ].join(' ').toLowerCase();

  const scores = {};

  // 각 Pillar의 키워드 매칭 점수 계산
  Object.entries(PILLAR_DATA).forEach(([key, pillar]) => {
    scores[key] = 0;
    pillar.keywords.forEach(keyword => {
      if (fullText.includes(keyword)) {
        scores[key] += 1;
      }
    });
  });

  // 점수 높은 순으로 정렬하여 상위 2-3개 선택
  const sortedPillars = Object.entries(scores)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .filter(([_, score]) => score > 0); // 점수가 0인 것은 제외

  // 최소 2개는 보장 (점수 0이어도)
  if (sortedPillars.length < 2) {
    const allPillars = Object.keys(PILLAR_DATA);
    const selected = sortedPillars.map(([key]) => key);
    
    // 기본으로 reliability, performance 추가
    ['reliability', 'performance', 'security'].forEach(key => {
      if (!selected.includes(key) && selected.length < 2) {
        sortedPillars.push([key, 0]);
        selected.push(key);
      }
    });
  }

  return sortedPillars.map(([key]) => ({
    key,
    name: PILLAR_DATA[key].name,
    principles: PILLAR_DATA[key].principles
  }));
}

/**
 * 🔥 NEW: 컴포넌트 역할 기반 분류 (Phase 3)
 * 
 * 단순 나열 대신 Entry/Compute/Storage/Security로 분류하여
 * LLM이 아키텍처 구조를 입체적으로 이해할 수 있게 함
 */
function categorizeComponents(components) {
  const categories = {
    entry: [],
    compute: [],
    storage: [],
    security: [],
    network: [],
    other: []
  };

  const typeMap = {
    // Entry Points
    'elb': 'entry',
    'alb': 'entry',
    'nlb': 'entry',
    'cloudfront': 'entry',
    'apigateway': 'entry',
    'route53': 'entry',
    
    // Compute
    'ec2': 'compute',
    'lambda': 'compute',
    'ecs': 'compute',
    'eks': 'compute',
    'fargate': 'compute',
    'beanstalk': 'compute',
    
    // Storage
    'rds': 'storage',
    's3': 'storage',
    'dynamodb': 'storage',
    'elasticache': 'storage',
    'redis': 'storage',
    'aurora': 'storage',
    'ebs': 'storage',
    
    // Security
    'waf': 'security',
    'shield': 'security',
    'securitygroup': 'security',
    'iam': 'security',
    'cognito': 'security',
    
    // Network
    'vpc': 'network',
    'subnet': 'network',
    'natgateway': 'network',
    'internetgateway': 'network',
    'transitgateway': 'network'
  };

  components.forEach(comp => {
    const type = comp.type?.toLowerCase() || '';
    const text = comp.text?.toLowerCase() || '';
    
    let category = 'other';
    
    // 타입 기반 매칭
    for (const [keyword, cat] of Object.entries(typeMap)) {
      if (type.includes(keyword) || text.includes(keyword)) {
        category = cat;
        break;
      }
    }
    
    categories[category].push(comp);
  });

  return categories;
}

/**
 * 🔥 NEW: 연결 관계에 의미 부여
 * 
 * "A -> B" 대신 "A -> B (Traffic Flow)" 형태로
 * 데이터 흐름의 의미를 명시
 */
function analyzeConnections(connections, components) {
  return connections.map(conn => {
    const from = components.find(c => c.id === conn.from);
    const to = components.find(c => c.id === conn.to);
    
    if (!from || !to) return null;
    
    // 연결의 의미 추론
    let flowType = 'Data Flow';
    
    const fromType = from.type?.toLowerCase() || '';
    const toType = to.type?.toLowerCase() || '';
    
    if (fromType.includes('elb') || fromType.includes('alb')) {
      flowType = 'Traffic Distribution';
    } else if (toType.includes('rds') || toType.includes('dynamodb')) {
      flowType = 'Database Query';
    } else if (fromType.includes('ec2') && toType.includes('s3')) {
      flowType = 'File Storage';
    } else if (toType.includes('cache') || toType.includes('redis')) {
      flowType = 'Cache Access';
    }
    
    return `${from.text} → ${to.text} (${flowType})`;
  }).filter(Boolean);
}

/**
 * OpenAI API 호출
 */
async function callOpenAI(prompt, options = {}) {
  const {
    model = 'gpt-4o-mini',
    maxTokens = 2000,
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
 * 🔥 MAIN: 개선된 질문 생성 시스템
 * 
 * test.md 피드백 완전 반영:
 * - 안티패턴 체크리스트
 * - Chain of Thought (사고 과정)
 * - 동적 Pillar 선별
 * - 역할 기반 컴포넌트 분류
 */
export async function generateFollowUpQuestions(problem, components, connections, mermaidCode, userExplanation) {
  // 1. 컴포넌트 역할 기반 분류 (Phase 3)
  const categorized = categorizeComponents(components);
  
  // 2. 연결 관계 의미 분석
  const meaningfulConnections = analyzeConnections(connections, components);
  
  // 3. 시나리오 기반 관련 Pillar 선별 (Phase 2)
  const scenario = problem?.scenario || '';
  const constraints = problem?.constraints || [];
  const missions = problem?.missions || [];
  
  const relevantPillars = selectRelevantPillars(scenario, missions, constraints);
  
  // 4. 선별된 Pillar의 원칙만 텍스트로 생성
  const principlesText = relevantPillars.map(pillar => `
### ${pillar.name}
${pillar.principles}
`).join('\n---\n');

  // 5. 역할별 컴포넌트 리스트 생성
  const categoryTexts = {
    entry: categorized.entry.length > 0 
      ? `**🚪 진입점 (Entry Points)**\n${categorized.entry.map(c => `- ${c.text} (${c.type})`).join('\n')}`
      : '',
    compute: categorized.compute.length > 0
      ? `**⚙️ 컴퓨팅 계층 (Compute)**\n${categorized.compute.map(c => `- ${c.text} (${c.type})`).join('\n')}`
      : '',
    storage: categorized.storage.length > 0
      ? `**💾 저장소 계층 (Storage)**\n${categorized.storage.map(c => `- ${c.text} (${c.type})`).join('\n')}`
      : '',
    security: categorized.security.length > 0
      ? `**🔒 보안 계층 (Security)**\n${categorized.security.map(c => `- ${c.text} (${c.type})`).join('\n')}`
      : '',
    network: categorized.network.length > 0
      ? `**🌐 네트워크 계층 (Network)**\n${categorized.network.map(c => `- ${c.text} (${c.type})`).join('\n')}`
      : '',
    other: categorized.other.length > 0
      ? `**📦 기타 컴포넌트**\n${categorized.other.map(c => `- ${c.text} (${c.type})`).join('\n')}`
      : ''
  };
  
  const architectureOverview = Object.values(categoryTexts).filter(Boolean).join('\n\n');

  // 6. 🔥 개선된 프롬프트 (Phase 1: 안티패턴 + CoT)
  const prompt = `당신은 **시니어 클라우드 솔루션 아키텍트**입니다.

## 🎯 당신의 임무
1. 지원자의 아키텍처를 **비판적으로 분석** (안티패턴 체크)
2. **사고 과정(Chain of Thought)**을 먼저 작성
3. 부족한 영역 3가지에 대해 **날카로운 질문** 생성

---

## 📋 문제 상황

### 시나리오
${scenario || '시스템 아키텍처 설계'}

### 미션
${missions.length > 0 ? missions.map((m, i) => `${i + 1}. ${m}`).join('\n') : '없음'}

### 제약조건
${constraints.length > 0 ? constraints.map((c, i) => `${i + 1}. ${c}`).join('\n') : '없음'}

---

## 🏗️ 지원자의 아키텍처

### 역할별 컴포넌트 분류
${architectureOverview || '(컴포넌트 없음)'}

### 데이터 흐름 (${meaningfulConnections.length}개 연결)
${meaningfulConnections.length > 0 ? meaningfulConnections.join('\n') : '(연결 없음)'}

### Mermaid 다이어그램
\`\`\`mermaid
${mermaidCode || 'graph LR'}
\`\`\`

---

## 💬 지원자의 설명
"${userExplanation || '(설명 없음)'}"

---

## 📚 분석 원칙 (선별된 관점)

아래는 이 문제 시나리오와 관련성이 높은 ${relevantPillars.length}개 관점의 핵심 원칙입니다.

${principlesText}

---

## 🔍 분석 방법론

### STEP 1: 안티패턴 체크리스트 (Critical)

먼저 아래 항목들을 **반드시** 확인하세요. 이는 프로덕션에서 자주 발생하는 치명적 설계 오류입니다.

#### ⚠️ 신뢰성 안티패턴
- [ ] **SPOF (Single Point of Failure)**: 단일 컴포넌트 장애 시 전체 서비스 중단?
- [ ] **No Redundancy**: 중요 컴포넌트의 복제본이 없음?
- [ ] **단일 AZ 배치**: 모든 리소스가 1개 가용영역에만?
- [ ] **복구 계획 부재**: 장애 발생 시 복구 시나리오 언급 없음?

#### ⚡ 성능 안티패턴
- [ ] **단일 경로 병목**: 모든 트래픽이 1개 경로로만 흐름?
- [ ] **Auto Scaling 부재**: 트래픽 급증 시 수동 증설만 가능?
- [ ] **캐싱 전략 없음**: DB에 직접 쿼리만 하는 구조?
- [ ] **비동기 처리 부재**: 무거운 작업을 동기식으로만 처리?

#### 🔒 보안 안티패턴
- [ ] **Public DB**: 데이터베이스가 Public Subnet에 노출?
- [ ] **Network Segmentation 부족**: VPC/Subnet 분리 없음?
- [ ] **암호화 언급 없음**: 전송/저장 데이터 암호화 미언급?
- [ ] **IAM/권한 관리 부재**: 접근 제어 전략 없음?

#### 🛠️ 운영 안티패턴
- [ ] **모니터링 부재**: 시스템 상태 추적 방법 없음?
- [ ] **로깅 전략 없음**: 문제 발생 시 디버깅 불가?
- [ ] **수동 배포**: CI/CD 파이프라인 없음?

#### 💰 비용 안티패턴
- [ ] **Always-On 리소스**: 사용하지 않을 때도 항상 켜짐?
- [ ] **과다 프로비저닝**: 필요 이상의 리소스 할당?

### STEP 2: 누락된 관점 확인

안티패턴 체크 후, 지원자가 **언급하지 않은** 중요 관점을 찾으세요:
- 아키텍처에 배치되었지만 설명에서 빠진 컴포넌트
- 문제의 제약조건/미션과 맞지 않는 부분
- 선별된 ${relevantPillars.length}개 관점 중 다루지 않은 영역

---

## 📝 질문 생성 규칙

### 원칙
1. **안티패턴 우선**: 체크리스트에서 발견된 문제를 먼저 질문
2. **상황 기반**: "~한 상황이 발생하면" 형태 (Failure Scenario)
3. **구체적**: 이 시나리오의 특정 컴포넌트/상황을 언급
4. **개방형**: Yes/No가 아닌 설계 의도/대응 방안을 설명하게 유도
5. **배치된 컴포넌트만 언급**: 없는 컴포넌트 질문 금지

### 질문 예시 형식
- ❌ 나쁜 질문: "데이터베이스의 가용성을 어떻게 보장하나요?"
- ✅ 좋은 질문: "RDS 인스턴스가 갑자기 장애나면, 사용자는 즉시 서비스 중단을 경험하나요? 자동 Failover가 작동하나요? 어떻게 구현했나요?"

---

## 🧠 출력 형식 (JSON만)

**CRITICAL**: 반드시 아래 형식을 따라주세요.

{
  "internal_reasoning": {
    "architecture_understanding": "지원자의 아키텍처를 어떻게 이해했는지 (2-3문장)",
    "detected_antipatterns": [
      "발견한 안티패턴 1 (예: RDS 단일 AZ 배치 → SPOF)",
      "발견한 안티패턴 2",
      "발견한 안티패턴 3"
    ],
    "mentioned_aspects": ["지원자가 설명에서 언급한 관점들"],
    "missing_aspects": ["부족하거나 언급되지 않은 관점 3가지"],
    "why_these_questions": "왜 이 3가지 질문을 선택했는지 논리 (2-3문장)"
  },
  "gaps_analysis": {
    "mentioned": ["지원자가 설명에서 언급한 관점들"],
    "missing": ["부족하거나 언급되지 않은 관점 3가지"]
  },
  "questions": [
    {
      "category": "부족한 영역 (예: 신뢰성, 성능, 보안, 운영, 비용)",
      "antipattern": "발견된 안티패턴 (해당되는 경우)",
      "gap": "이 질문으로 확인하려는 부족한 부분",
      "failure_scenario": "구체적인 장애 시나리오 (예: RDS 인스턴스 다운)",
      "question": "상황 기반의 날카로운 질문 (배치된 컴포넌트 언급, 설계 의도/대응 방안 물어보기)"
    },
    {
      "category": "부족한 영역",
      "antipattern": "발견된 안티패턴",
      "gap": "이 질문으로 확인하려는 부족한 부분",
      "failure_scenario": "구체적인 장애 시나리오",
      "question": "상황 기반의 날카로운 질문"
    },
    {
      "category": "부족한 영역",
      "antipattern": "발견된 안티패턴",
      "gap": "이 질문으로 확인하려는 부족한 부분",
      "failure_scenario": "구체적인 장애 시나리오",
      "question": "상황 기반의 날카로운 질문"
    }
  ]
}

**주의사항**:
- internal_reasoning은 내부 처리용이지만, 질문 품질 향상에 필수적입니다
- 반드시 JSON 형식만 출력하세요 (마크다운 코드블록 불필요)
- 질문은 정확히 3개만 생성하세요`;

  try {
    const response = await callOpenAI(prompt, {
      maxTokens: 2000,
      temperature: 0.7
    });

    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      
      // internal_reasoning은 로깅용으로만 사용 (사용자에게 노출 X)
      console.log('🧠 AI Reasoning Process:', parsed.internal_reasoning);
      
      // 🔥 질문을 정확히 3개로 보장
      let questions = (parsed.questions || []).slice(0, 3).map(q => ({
        category: q.category,
        gap: q.gap,
        question: q.question,
        antipattern: q.antipattern || null,
        scenario: q.failure_scenario || null
      }));

      return {
        analysis: parsed.gaps_analysis || { mentioned: [], missing: [] },
        questions,
        metadata: {
          selectedPillars: relevantPillars.map(p => p.name),
          componentCategorization: {
            entry: categorized.entry.length,
            compute: categorized.compute.length,
            storage: categorized.storage.length,
            security: categorized.security.length
          },
          reasoning: parsed.internal_reasoning
        }
      };
    }
    throw new Error('Invalid JSON');
  } catch (error) {
    console.error('질문 생성 실패:', error);

    // 🔥 개선된 Fallback
    const mainComponent = components[0]?.text || '메인 서버';
    const hasDB = components.some(c => 
      c.type?.toLowerCase().includes('rds') || 
      c.type?.toLowerCase().includes('db')
    );
    const hasLB = components.some(c => 
      c.type?.toLowerCase().includes('elb') || 
      c.type?.toLowerCase().includes('alb')
    );

    return {
      analysis: { 
        mentioned: [], 
        missing: ['신뢰성', '성능', '운영']
      },
      questions: [
        {
          category: '신뢰성',
          gap: 'SPOF (Single Point of Failure)',
          antipattern: '단일 장애점',
          scenario: `${mainComponent} 장애`,
          question: `${mainComponent}가 갑자기 다운되면, 사용자는 즉시 서비스 중단을 경험하나요? 자동 장애조치(failover)가 작동하나요? 어떻게 구현했나요?`
        },
        {
          category: '성능',
          gap: 'Auto Scaling 부재',
          antipattern: '수동 확장',
          scenario: '트래픽 50배 급증',
          question: `동시 사용자가 평소의 50배로 급증하면, 이 아키텍처가 자동으로 리소스를 확장하나요? 아니면 수동 개입이 필요한가요? 확장 전략을 설명해주세요.`
        },
        {
          category: '운영',
          gap: '모니터링/경보 전략',
          antipattern: '사후 대응',
          scenario: '밤중 성능 저하',
          question: `밤중에 시스템이 느려지기 시작하면, 운영팀이 사용자보다 먼저 알아차릴 수 있는 모니터링 시스템이 있나요? 어떤 지표를 추적하고 있나요?`
        }
      ],
      metadata: {
        selectedPillars: relevantPillars.map(p => p.name),
        componentCategorization: {
          entry: categorized.entry.length,
          compute: categorized.compute.length,
          storage: categorized.storage.length,
          security: categorized.security.length
        },
        fallback: true
      }
    };
  }
}