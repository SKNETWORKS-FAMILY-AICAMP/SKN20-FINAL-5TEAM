/**
 * Architecture Practice API Service
 * OpenAI API와의 통신을 담당하는 서비스
 */

import architectureProblems from '@/data/architecture.json';

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

/**
 * OpenAI API 호출 기본 함수
 */
async function callOpenAI(prompt, options = {}) {
  const {
    model = 'gpt-3.5-turbo',
    maxTokens = 500,
    temperature = 0.7,
    systemMessage = null
  } = options;

  const messages = [];
  if (systemMessage) {
    messages.push({ role: 'system', content: systemMessage });
  }
  messages.push({ role: 'user', content: prompt });

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getApiKey()}`
    },
    body: JSON.stringify({
      model,
      messages,
      max_tokens: maxTokens,
      temperature
    })
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  const data = await response.json();
  return data.choices[0].message.content.trim();
}

/**
 * 심층 질문 생성 (레거시 - 단일 연결용)
 */
export async function generateDeepDiveQuestion(problem, fromComp, toComp) {
  const scenario = problem?.scenario || '';
  const missions = problem?.missions?.join('\n') || '';

  const prompt = `당신은 시스템 아키텍처 면접관입니다.

문제: ${problem?.title || '시스템 아키텍처 설계'}
시나리오: ${scenario}
미션: ${missions}

학생이 "${fromComp.text}"와 "${toComp.text}"를 연결했습니다.
이 연결에 대해 깊이 있는 면접 질문 1개를 생성해주세요.

질문만 출력하세요. 다른 설명은 포함하지 마세요.`;

  try {
    return await callOpenAI(prompt, { maxTokens: 200 });
  } catch (error) {
    console.error('Deep dive question error:', error);
    return `${fromComp.text}와 ${toComp.text}의 연결에서 예상되는 데이터 흐름과 잠재적인 병목 현상에 대해 설명해주세요.`;
  }
}

/**
 * 아키텍처 분석 기반 심층 질문 3개 생성 (최종 제출용)
 */
export async function generateArchitectureAnalysisQuestions(problem, components, connections, mermaidCode) {
  const componentList = components.map(c => `- ${c.text} (타입: ${c.type})`).join('\n');
  const connectionList = connections.map(conn => {
    const from = components.find(c => c.id === conn.from);
    const to = components.find(c => c.id === conn.to);
    return from && to ? `- ${from.text} → ${to.text}` : null;
  }).filter(Boolean).join('\n');

  const scenario = problem?.scenario || '';
  const missions = problem?.missions?.join('\n- ') || '';
  const specText = Object.entries(problem?.engineeringSpec || {}).map(([k, v]) => `- ${k}: ${v}`).join('\n');
  const rubricNfr = problem?.rubricNonFunctional || [];
  
  // 평가해야 할 핵심 토픽 추출
  const nfrTopics = rubricNfr.map(r => `${r.category} (${r.question_intent})`).join(', ') || '전반적인 아키텍처 설계';

  const prompt = `당신은 시스템 아키텍처 면접관입니다.
학생이 설계한 아키텍처를 분석하고, 심층적인 면접 질문 3개를 생성해주세요.

## 문제 정보
- 제목: ${problem?.title}
- 시나리오: ${scenario}
- 미션:
${missions}
- 기술 요구사항:
${specText}

## 평가 핵심 토픽 (이 부분을 중점적으로 질문):
${nfrTopics}

## 학생의 아키텍처 설계
### 컴포넌트:
${componentList}
### 연결 관계:
${connectionList}
### Mermaid 다이어그램:
\`\`\`
${mermaidCode}
\`\`\`

## 질문 생성 기준
1. **핵심 토픽 질문**: 위 '평가 핵심 토픽'과 관련된 설계 의도를 물어보세요. (가장 중요)
2. **트레이드오프 질문**: 왜 다른 대안 대신 이 구조를 선택했는지 물어보세요.
3. **확장성/장애대응 질문**: 트래픽 증가나 장애 상황 시의 대처를 물어보세요.

출력 형식 (JSON만 출력):
{
  "questions": [
    { "category": "핵심 설계 의도", "question": "..." },
    { "category": "트레이드오프", "question": "..." },
    { "category": "확장성/운영", "question": "..." }
  ]
}`;

  try {
    const response = await callOpenAI(prompt, { maxTokens: 600, temperature: 0.7 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return parsed.questions || [];
    }
    throw new Error('Invalid JSON response');
  } catch (error) {
    console.error('Architecture analysis questions error:', error);
    return [
      { category: '핵심 설계', question: '이 아키텍처에서 가장 중요하게 고려한 부분은 무엇인가요?' },
      { category: '성능', question: '트래픽이 급증할 때 병목이 예상되는 구간은 어디인가요?' },
      { category: '확장성', question: '데이터 양이 10배로 늘어난다면 어떤 구조 변경이 필요한가요?' }
    ];
  }
}

/**
 * 평가 모달용 질문 생성
 */
export async function generateEvaluationQuestion(problem, architectureContext) {
  const scenario = problem?.scenario || '';
  const rubricNfr = problem?.rubricNonFunctional || [];
  // 질문의 초점을 문제의 핵심 의도(NFR)에 맞춤
  const nfrHints = rubricNfr.map(r => `핵심 평가 항목: ${r.category} - ${r.question_intent}`).join('\n');

  const prompt = `당신은 시스템 아키텍처 면접관입니다.
문제: ${problem?.title}
시나리오: ${scenario}

${nfrHints}

학생의 아키텍처:
${architectureContext}

위 '핵심 평가 항목'을 검증할 수 있는 날카로운 면접 질문 1개를 생성하세요.
질문만 출력하세요.`;

  try {
    return await callOpenAI(prompt, { maxTokens: 300 });
  } catch (error) {
    return '설계하신 아키텍처에서 가장 중요한 트레이드오프는 무엇인가요?';
  }
}

/**
 * 아키텍처 및 면접 답변 평가 실행 (개선된 로직)
 * * 평가 점수 배분 (총 100점):
 * 1. 아키텍처 설계 (Architecture Design): 50점
 * - 필수 컴포넌트 포함 여부 (25점)
 * - 필수 연결 흐름 구현 여부 (25점)
 * * 2. 면접/NFR 답변 (Interview Quality): 50점
 * - 핵심 NFR(문제 출제 의도) 이해도 (30점)
 * - 일반 아키텍처 지식 및 논리성 (20점)
 */
export async function evaluateArchitecture(problem, architectureContext, generatedQuestion, userAnswer, deepDiveAnswers) {
  
  // 1. 아키텍처 정답 기준 (Functional Rubric)
  const rubricFunc = problem?.rubric_functional || problem?.rubricFunctional || {};
  const requiredComponents = rubricFunc.required_components || [];
  const requiredFlows = rubricFunc.required_flows || [];

  const reqCompText = requiredComponents.length > 0 
    ? requiredComponents.join(', ') 
    : '별도 지정 없음';
    
  const reqFlowText = requiredFlows.length > 0
    ? requiredFlows.map(f => `${f.from} -> ${f.to} (${f.reason})`).join('\n')
    : '별도 지정 없음';

  // 2. 면접 평가 기준 (Non-Functional Rubric - Key NFR)
  const rubricNfr = problem?.rubric_non_functional || problem?.rubricNonFunctional || [];
  
  // 핵심 평가 요소 텍스트화
  const keyNfrText = rubricNfr.length > 0
    ? rubricNfr.map(r => `[Category: ${r.category}]\n   - 의도: ${r.question_intent}\n   - 모범답안 키워드: ${r.model_answer}`).join('\n\n')
    : '일반적인 시스템 설계 원칙(확장성, 가용성 등)을 기준으로 평가';

  const prompt = `당신은 시스템 아키텍처 면접관입니다.
학생의 설계와 면접 답변을 분석하여 점수를 매겨주세요.

## 문제 정보
- 제목: ${problem?.title}
- 시나리오: ${problem?.scenario}

## 학생 제출 데이터
### 1. 아키텍처 설계
${architectureContext}

### 2. 면접 답변
- 질문: ${generatedQuestion || '설계에 대한 설명'}
- 답변: ${userAnswer || '(답변 없음)'}
- 심화 질문 답변들: ${deepDiveAnswers || '(없음)'}

---

## [평가 기준 및 배점 가이드] (총 100점)

### PART 1: 아키텍처 설계 평가 (50점 만점)
학생의 다이어그램이 아래 **정답 기준**을 얼마나 충족했는지 평가합니다.

1. **필수 컴포넌트 (25점)**:
   - 기준 목록: [${reqCompText}]
   - 평가: 위 목록에 있는 컴포넌트가 포함되어 있으면 점수 부여. (부분 점수 가능)

2. **필수 연결 흐름 (25점)**:
   - 기준 목록: 
${reqFlowText}
   - 평가: 위 데이터 흐름이 논리적으로 연결되어 있으면 점수 부여. (부분 점수 가능)

### PART 2: 면접 및 핵심 의도 평가 (50점 만점)
학생이 **이 문제의 핵심 출제 의도(Key NFR)**를 파악했는지 평가합니다.

1. **핵심 NFR 이해도 (30점)**:
   - **평가 기준(가장 중요):**
${keyNfrText}
   - 채점: 학생의 답변이 위 '의도'와 '모범답안 키워드'를 정확히 포함하고 설명했다면 만점(30점). 
   - 언급은 했으나 설명이 부족하면 10~20점. 전혀 언급 없으면 0점.

2. **기술적 깊이 및 일반 지식 (20점)**:
   - 채점: 
     - 적절한 기술 용어(Cache, LB, Sharding, Async 등) 사용 여부.
     - 설계의 트레이드오프나 제한사항을 인지하고 있는지.
     - 답변이 논리적이고 구체적인지.
   - 답변이 없거나 너무 짧으면(20자 미만) 0점 처리.

---

## 출력 형식 (JSON Only)
반드시 아래 포맷으로 JSON만 출력하세요.

{
  "score": (PART 1 + PART 2 합계, 0~100),
  "grade": "excellent"(80+) | "good"(60-79) | "needs-improvement"(40-59) | "poor"(0-39),
  
  "breakdown": {
    "architectureScore": 0~50,
    "interviewScore": 0~50,
    "details": {
      "componentScore": 0~25,
      "flowScore": 0~25,
      "keyNfrScore": 0~30,
      "generalKnowledgeScore": 0~20
    }
  },

  "componentCoverage": {
    "included": ["학생이 포함한 필수 컴포넌트들"],
    "missing": ["놓친 필수 컴포넌트들"]
  },

  "nfrScores": { 
    // UI 표시용 (점수는 위 로직에 따라 계산된 결과를 반영하되, 각 항목별 상태 표시)
    "scalability": { "score": 0~100, "feedback": "한줄 평" },
    "availability": { "score": 0~100, "feedback": "한줄 평" },
    "performance": { "score": 0~100, "feedback": "한줄 평" },
    "consistency": { "score": 0~100, "feedback": "한줄 평" },
    "reliability": { "score": 0~100, "feedback": "한줄 평" }
  },

  "summary": "전체적인 총평 (강점과 약점 위주로 2~3문장)",
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["보완점1", "보완점2"],
  "suggestions": ["구체적인 개선 제안1", "구체적인 개선 제안2"]
}`;

  const response = await callOpenAI(prompt, { maxTokens: 1500, temperature: 0.4 });

  const jsonMatch = response.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    return JSON.parse(jsonMatch[0]);
  }
  throw new Error('Invalid JSON response');
}

/**
 * 채팅 메시지 전송
 */
export async function sendChatMessage(chatContext, chatHistory, userMessage) {
  const systemPrompt = `당신은 시스템 아키텍처 면접관입니다.
학생이 주어진 문제의 기능적/비기능적 요구사항에 대해 질문하면 답변해주세요.

**중요 규칙:**
1. 학생이 요구사항에 대해 질문하면 아래 "현재 문제" 정보를 참고하여 구체적으로 설명해주세요.
2. 직접적인 정답이나 완성된 아키텍처 설계는 알려주지 마세요.
3. 힌트와 고려사항을 제공하되, 학생이 스스로 생각할 수 있도록 유도 질문을 하세요.

**현재 문제:**
${chatContext}

친절하지만 교육적인 태도로 한국어로 답변하세요.`;

  const messages = [
    { role: 'system', content: systemPrompt },
    ...chatHistory.map(msg => ({ role: msg.role, content: msg.content })),
    { role: 'user', content: userMessage }
  ];

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getApiKey()}`
    },
    body: JSON.stringify({
      model: 'gpt-3.5-turbo',
      messages,
      max_tokens: 500,
      temperature: 0.7
    })
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

/**
 * 문제 데이터 로드
 */
export async function fetchProblems() {
  return architectureProblems;
}