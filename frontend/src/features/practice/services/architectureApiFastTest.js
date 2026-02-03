/**
 * Architecture Practice API Service
 *
 * 사용자의 아키텍처 + 설명을 분석하여 부족한 부분을 파악하고,
 * 해당 영역에 맞는 고품질 질문 3개를 생성
 *
 * txt 파일에서 [핵심 분석 원칙] 섹션만 파싱하여 사용
 */

import architectureProblems from '@/data/architecture.json';

// 6대 기둥 txt 파일 import (Vite ?raw 쿼리 사용)
import reliabilityTxt from '@/data/신뢰성.txt?raw';
import performanceTxt from '@/data/최적화.txt?raw';
import operationalTxt from '@/data/운영유용성.txt?raw';
import costTxt from '@/data/비용.txt?raw';
import securityTxt from '@/data/보안.txt?raw';
import sustainabilityTxt from '@/data/지속가능성.txt?raw';

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

/**
 * txt 파일에서 [핵심 분석 원칙] 섹션만 추출
 * - 질문 예시는 제외 (LLM이 복사하는 것 방지)
 * - 원칙만 제공하여 맞춤형 질문 생성 유도
 */
function extractPrinciples(txtContent) {
  // [핵심 분석 원칙 으로 시작해서 다음 ### 까지 추출
  const match = txtContent.match(/### \[핵심 분석 원칙[^\]]*\]\s*([\s\S]*?)(?=### \[|$)/);
  if (match) {
    return match[1].trim();
  }
  return '';
}

/**
 * 6대 기둥 (txt 파일에서 핵심 원칙 추출)
 */
const PILLAR_DATA = {
  reliability: {
    name: '신뢰성 (Reliability)',
    principles: extractPrinciples(reliabilityTxt)
  },
  performance: {
    name: '성능 최적화 (Performance)',
    principles: extractPrinciples(performanceTxt)
  },
  operational: {
    name: '운영 우수성 (Operational Excellence)',
    principles: extractPrinciples(operationalTxt)
  },
  cost: {
    name: '비용 최적화 (Cost)',
    principles: extractPrinciples(costTxt)
  },
  security: {
    name: '보안 (Security)',
    principles: extractPrinciples(securityTxt)
  },
  sustainability: {
    name: '지속 가능성 (Sustainability)',
    principles: extractPrinciples(sustainabilityTxt)
  }
};

/**
 * OpenAI API 호출
 */
async function callOpenAI(prompt, options = {}) {
  const {
    model = 'gpt-4o-mini',
    maxTokens = 1500,
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
 * 문제 데이터 로드
 */
export async function fetchProblems() {
  return architectureProblems;
}

/**
 * 사용자 설명 + 아키텍처 분석 → 부족한 부분 파악 → 맞춤형 질문 3개 생성
 */
export async function generateFollowUpQuestions(problem, components, connections, mermaidCode, userExplanation) {
  // 컴포넌트/연결 정보 정리
  const componentList = components.map(c => `- ${c.text} (타입: ${c.type})`).join('\n');
  const connectionList = connections.map(conn => {
    const from = components.find(c => c.id === conn.from);
    const to = components.find(c => c.id === conn.to);
    return from && to ? `- ${from.text} → ${to.text}` : null;
  }).filter(Boolean).join('\n');

  // 문제 정보
  const scenario = problem?.scenario || '';
  const constraints = problem?.constraints || [];
  const missions = problem?.missions || [];

  // 6대 기둥 원칙 텍스트 생성 (txt 파일에서 추출한 내용)
  const principlesText = Object.entries(PILLAR_DATA)
    .filter(([_, pillar]) => pillar.principles) // 원칙이 있는 것만
    .map(([key, pillar]) => `
### ${pillar.name}
${pillar.principles}
`).join('\n---\n');

  const prompt = `당신은 **시니어 클라우드 솔루션 아키텍트**입니다.

## 당신의 임무
1. 지원자의 **아키텍처 다이어그램**과 **설명**을 분석
2. **부족하거나 언급되지 않은 영역** 3가지를 파악
3. 각 부족한 영역에 대해 **구체적이고 상황 기반의 질문** 1개씩 생성

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

### 배치된 컴포넌트 (${components.length}개)
${componentList || '(없음)'}

### 연결 관계 (${connections.length}개)
${connectionList || '(없음)'}

### Mermaid 다이어그램
\`\`\`mermaid
${mermaidCode || 'graph LR'}
\`\`\`

---

## 💬 지원자의 설명
"${userExplanation || '(설명 없음)'}"

---

## 📚 6대 기둥 분석 원칙 (부족한 부분 판단 기준)

${principlesText}

---

## 📝 질문 생성 규칙

### 1. 부족한 부분 파악 방법
- 지원자의 설명에서 **언급하지 않은** 중요한 관점 찾기
- 아키텍처에서 **누락된 컴포넌트나 연결** 찾기
- 문제의 제약조건/미션과 **맞지 않는** 부분 찾기

### 2. 질문 생성 원칙
- **상황 기반**: "~한 상황이 발생하면" 형태로 질문
- **구체적**: 이 시나리오의 특정 컴포넌트/상황을 언급
- **개방형**: Yes/No가 아닌 설계 의도를 설명하게 유도
- **배치된 컴포넌트만 언급** (없는 컴포넌트 질문 금지)

### 3. 피해야 할 것
- 일반적인 교과서적 질문
- 지원자가 이미 설명한 내용 재질문
- 전문 용어 나열식 질문

---

## 출력 형식 (JSON만)

{
  "gaps_analysis": {
    "mentioned": ["지원자가 설명에서 언급한 관점들"],
    "missing": ["부족하거나 언급되지 않은 관점 3가지"]
  },
  "questions": [
    {
      "category": "부족한 영역 (예: 신뢰성, 성능, 운영 등)",
      "gap": "이 질문으로 확인하려는 부족한 부분",
      "question": "상황 기반의 구체적인 질문"
    },
    {
      "category": "부족한 영역",
      "gap": "이 질문으로 확인하려는 부족한 부분",
      "question": "상황 기반의 구체적인 질문"
    },
    {
      "category": "부족한 영역",
      "gap": "이 질문으로 확인하려는 부족한 부분",
      "question": "상황 기반의 구체적인 질문"
    }
  ]
}`;

  try {
    const response = await callOpenAI(prompt, {
      maxTokens: 1200,
      temperature: 0.7
    });

    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return {
        analysis: parsed.gaps_analysis || {},
        questions: (parsed.questions || []).slice(0, 3)
      };
    }
    throw new Error('Invalid JSON');
  } catch (error) {
    console.error('질문 생성 실패:', error);

    // Fallback
    const mainComponent = components[0]?.text || '메인 서버';
    return {
      analysis: { mentioned: [], missing: ['분석 실패'] },
      questions: [
        {
          category: '신뢰성',
          gap: '장애 대응',
          question: `${mainComponent}가 갑자기 다운된다면, 사용자들은 어떤 경험을 하게 되나요? 서비스가 완전히 중단되나요?`
        },
        {
          category: '성능',
          gap: '확장성',
          question: `동시 사용자가 평소의 10배로 급증하면, 이 아키텍처가 자동으로 처리량을 늘릴 수 있나요?`
        },
        {
          category: '운영',
          gap: '모니터링',
          question: `시스템에 문제가 생겼을 때, 운영팀이 사용자보다 먼저 알 수 있는 방법이 있나요?`
        }
      ]
    };
  }
}
