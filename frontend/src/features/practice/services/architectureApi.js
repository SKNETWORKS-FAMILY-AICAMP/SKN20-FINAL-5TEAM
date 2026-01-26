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
  const prompt = `당신은 시스템 아키텍처 면접관입니다.

문제: ${problem?.title || '시스템 아키텍처 설계'}
요구사항: ${problem?.requirements?.join(', ') || '없음'}

학생이 "${fromComp.text}"와 "${toComp.text}"를 연결했습니다.
이 연결에 대해 깊이 있는 면접 질문 1개를 생성해주세요.

예시 질문 유형:
- 이 연결에서 발생할 수 있는 문제점은?
- 왜 이 두 컴포넌트를 연결했나요?
- 이 연결의 데이터 흐름을 설명해주세요.
- 장애 상황에서 이 연결은 어떻게 처리되나요?

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
 * Mermaid 다이어그램과 컴포넌트/연결 정보를 분석하여 면접 질문 생성
 */
export async function generateArchitectureAnalysisQuestions(problem, components, connections, mermaidCode) {
  // 컴포넌트 정보 정리
  const componentList = components.map(c => `- ${c.text} (타입: ${c.type})`).join('\n');

  // 연결 정보 정리
  const connectionList = connections.map(conn => {
    const from = components.find(c => c.id === conn.from);
    const to = components.find(c => c.id === conn.to);
    return from && to ? `- ${from.text} → ${to.text}` : null;
  }).filter(Boolean).join('\n');

  const prompt = `당신은 시스템 아키텍처 면접관입니다.
학생이 설계한 아키텍처를 분석하고, 심층적인 면접 질문 3개를 생성해주세요.

## 문제 정보
- 제목: ${problem?.title || '시스템 아키텍처 설계'}
- 요구사항: ${problem?.requirements?.join(', ') || '없음'}
- 주요 토픽: ${problem?.questionTopics?.map(t => t.topic).join(', ') || '없음'}

## 학생의 아키텍처 설계

### 배치된 컴포넌트 (${components.length}개):
${componentList || '없음'}

### 연결 관계 (${connections.length}개):
${connectionList || '없음'}

### Mermaid 다이어그램:
\`\`\`
${mermaidCode}
\`\`\`

## 질문 생성 기준
1. **설계 의도 질문**: 왜 이런 구조를 선택했는지, 트레이드오프는 무엇인지
2. **확장성/성능 질문**: 트래픽 증가, 병목 현상, 캐싱 전략 등
3. **장애 대응 질문**: 특정 컴포넌트 장애 시 시스템 동작, 복구 전략 등

각 질문은 학생의 실제 설계를 기반으로 구체적이어야 합니다.
질문은 서로 다른 관점(설계 의도, 확장성, 장애 대응)에서 출제하세요.

## 출력 형식 (JSON만 출력, 다른 텍스트 없이):
{
  "questions": [
    {
      "category": "설계 의도",
      "question": "질문 내용"
    },
    {
      "category": "확장성/성능",
      "question": "질문 내용"
    },
    {
      "category": "장애 대응",
      "question": "질문 내용"
    }
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
    // Fallback 질문 생성
    return [
      {
        category: '설계 의도',
        question: `${problem?.title || '이 시스템'}에서 현재 설계한 아키텍처의 핵심 컴포넌트와 그 선택 이유를 설명해주세요.`
      },
      {
        category: '확장성/성능',
        question: '트래픽이 10배로 증가할 경우, 현재 아키텍처에서 가장 먼저 병목이 발생할 곳은 어디이며 어떻게 대응하시겠습니까?'
      },
      {
        category: '장애 대응',
        question: '주요 컴포넌트 중 하나가 장애가 발생했을 때, 시스템은 어떻게 동작하며 복구 전략은 무엇인가요?'
      }
    ];
  }
}

/**
 * 평가 모달용 질문 생성
 */
export async function generateEvaluationQuestion(problem, architectureContext) {
  const prompt = `당신은 시스템 아키텍처 면접관입니다.

문제: ${problem?.title || '시스템 아키텍처 설계'}
요구사항: ${problem?.requirements?.join(', ') || '없음'}
주제 힌트: ${problem?.evaluationRubric ? Object.keys(problem.evaluationRubric).join(', ') : ''}

학생의 아키텍처:
${architectureContext}

이 아키텍처에 대해 심층적인 면접 질문 1개를 생성하세요.
학생이 설계한 내용을 바탕으로 트레이드오프, 확장성, 장애 대응 등에 대해 질문하세요.
질문만 출력하세요.`;

  try {
    return await callOpenAI(prompt, { maxTokens: 300 });
  } catch (error) {
    console.error('Question generation error:', error);
    return problem?.followUpQuestion || '설계하신 아키텍처에서 가장 중요한 트레이드오프는 무엇인가요?';
  }
}

/**
 * 아키텍처 평가 실행
 * JSON의 모든 평가 정보를 활용하여 LLM 기반 평가 수행
 */
export async function evaluateArchitecture(problem, architectureContext, generatedQuestion, userAnswer, deepDiveAnswers) {
  const rubric = problem?.evaluationRubric;
  const systemArchRubric = rubric?.system_architecture || [];
  const interviewRubric = rubric?.interview_score || [];

  // 핵심 컴포넌트 목록 (학생이 포함해야 하는 것들 - 이름과 타입 포함)
  const keyComponents = problem?.keyComponents || [];
  const keyComponentsText = keyComponents.length > 0
    ? keyComponents.map(c => `- ${c.name} (타입: ${c.type})`).join('\n')
    : '- 명시된 핵심 컴포넌트 없음';

  // 참조 개념 (학생이 이해해야 하는 핵심 설계 개념)
  const referenceConcept = problem?.referenceConcept || {};
  const conceptsText = Object.keys(referenceConcept).length > 0
    ? Object.entries(referenceConcept).map(([key, val]) => `- ${key}: ${val}`).join('\n')
    : '- 명시된 참조 개념 없음';

  // 평가 토픽 및 키워드
  const questionTopics = problem?.questionTopics || [];
  const topicsText = questionTopics.length > 0
    ? questionTopics.map(t => `- ${t.topic}: [${t.keywords.join(', ')}]`).join('\n')
    : '- 명시된 토픽 없음';

  // 참조 Mermaid 다이어그램 (정답 예시)
  const referenceMermaid = problem?.referenceMermaid || '';

  const prompt = `당신은 시스템 아키텍처 면접관입니다.
다음 평가 기준과 참조 정보를 바탕으로 학생의 아키텍처를 **세부 항목별로** 평가해주세요.

## 문제 정보
- 제목: ${problem?.title || '시스템 아키텍처 설계'}
- 난이도: ${problem?.difficulty || 'medium'}
- 요구사항: ${problem?.requirements?.join(', ') || '없음'}

## 참조 정보 (평가 기준으로 활용)

### 필수 포함 컴포넌트:
${keyComponentsText}

### 핵심 설계 개념 (학생이 반드시 고려해야 할 것들):
${conceptsText}

### 평가 토픽 및 필수 키워드:
${topicsText}

${referenceMermaid ? `### 참조 아키텍처 (정답 예시):
\`\`\`
${referenceMermaid}
\`\`\`` : ''}

## 평가 기준 (각 항목 0-100점)

### 1. 시스템 아키텍처 평가 (60%)
${systemArchRubric.map(r => `- **${r.metric}**: ${r.description}`).join('\n') || '- 구조적 완성도\n- 확장성\n- 가용성/복원력'}

### 2. 면접 답변 평가 (40%)
${interviewRubric.map(r => `- **${r.metric}**: ${r.description}`).join('\n') || '- 논리적 일관성\n- 근거의 타당성\n- 전달력'}

## 학생의 제출물

### 아키텍처 설계:
${architectureContext}

### 심층 질문: ${generatedQuestion || problem?.followUpQuestion || ''}
### 학생의 답변: ${userAnswer}

${deepDiveAnswers ? `### 심화 질문 답변들:\n${deepDiveAnswers}` : ''}

## 평가 지침
1. **컴포넌트 검증**: 학생이 필수 컴포넌트를 포함했는지 확인하세요.
2. **개념 이해도**: 핵심 설계 개념(${Object.keys(referenceConcept).join(', ') || '확장성, 가용성'})을 올바르게 적용했는지 평가하세요.
3. **키워드 사용**: 평가 토픽의 필수 키워드를 답변에서 적절히 사용했는지 확인하세요.
4. **참조 비교**: 참조 아키텍처와 비교하여 누락된 흐름이나 컴포넌트를 식별하세요.
5. **실용성**: 실제 구현 가능성과 트레이드오프 이해도를 평가하세요.

## 출력 형식 (JSON만 출력, 다른 텍스트 없이):
{
  "score": 0-100,
  "grade": "excellent" | "good" | "needs-improvement" | "poor",
  "componentCoverage": {
    "included": ["포함된 필수 컴포넌트"],
    "missing": ["누락된 필수 컴포넌트"],
    "extra": ["추가로 포함한 좋은 컴포넌트"]
  },
  "systemArchitectureScores": {
    "${systemArchRubric[0]?.metric || '구조적 완성도'}": { "score": 0-100, "feedback": "구체적 피드백" },
    "${systemArchRubric[1]?.metric || '확장성'}": { "score": 0-100, "feedback": "구체적 피드백" },
    "${systemArchRubric[2]?.metric || '가용성/복원력'}": { "score": 0-100, "feedback": "구체적 피드백" }
  },
  "interviewScores": {
    "${interviewRubric[0]?.metric || '논리적 일관성'}": { "score": 0-100, "feedback": "구체적 피드백" },
    "${interviewRubric[1]?.metric || '근거의 타당성'}": { "score": 0-100, "feedback": "구체적 피드백" },
    "${interviewRubric[2]?.metric || '전달력'}": { "score": 0-100, "feedback": "구체적 피드백" }
  },
  "conceptUnderstanding": {
    "demonstrated": ["이해를 보여준 핵심 개념"],
    "needsImprovement": ["더 학습이 필요한 개념"]
  },
  "summary": "종합 평가 2-3문장 (구체적인 강점과 개선점 포함)",
  "strengths": ["구체적인 강점1", "구체적인 강점2"],
  "weaknesses": ["구체적인 약점1"],
  "suggestions": ["구체적인 개선 제안1", "구체적인 개선 제안2"]
}`;

  const response = await callOpenAI(prompt, { maxTokens: 1200, temperature: 0.5 });

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
4. 요구사항의 의미, 우선순위, 트레이드오프에 대해서는 명확히 설명해주세요.
5. 학생의 질문이 요구사항 관련이면 아래 정보를 기반으로, 그 외의 일반적인 아키텍처 질문은 기본 지식으로 답변하세요.

**답변 형식:**
- 핵심 내용을 먼저 간결하게 답변
- 필요시 추가 고려사항이나 꼬리 질문 제시
- 답변은 3-5문장으로 간결하게

**현재 문제:**
${chatContext}

친절하지만 교육적인 태도로 답변해주세요. 한국어로 답변하세요.`;

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
 * @returns {Promise<Array>} 아키텍처 문제 데이터
 */
export async function fetchProblems() {
  // src/data/architecture.json에서 import된 데이터 반환
  return architectureProblems;
}
