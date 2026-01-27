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
  // 시나리오와 미션 정보 활용
  const scenario = problem?.scenario || '';
  const missions = problem?.missions?.join('\n') || '';

  const prompt = `당신은 시스템 아키텍처 면접관입니다.

문제: ${problem?.title || '시스템 아키텍처 설계'}
시나리오: ${scenario}
미션: ${missions}

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

  // 새 데이터 구조에서 정보 추출
  const scenario = problem?.scenario || '';
  const missions = problem?.missions?.join('\n- ') || '';
  const engineeringSpec = problem?.engineeringSpec || {};
  const specText = Object.entries(engineeringSpec).map(([k, v]) => `- ${k}: ${v}`).join('\n');
  const rubricNfr = problem?.rubricNonFunctional || [];
  const nfrTopics = rubricNfr.map(r => r.category).join(', ') || '없음';

  const prompt = `당신은 시스템 아키텍처 면접관입니다.
학생이 설계한 아키텍처를 분석하고, 심층적인 면접 질문 3개를 생성해주세요.

## 문제 정보
- 제목: ${problem?.title || '시스템 아키텍처 설계'}
- 시나리오: ${scenario}
- 미션:
- ${missions || '없음'}

### 기술 요구사항:
${specText || '없음'}

### 평가 주요 토픽: ${nfrTopics}

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
  // 새 데이터 구조에서 정보 추출
  const scenario = problem?.scenario || '';
  const missions = problem?.missions?.join(', ') || '';
  const rubricNfr = problem?.rubricNonFunctional || [];
  const nfrHints = rubricNfr.map(r => `${r.category}: ${r.question_intent}`).join('\n') || '';

  const prompt = `당신은 시스템 아키텍처 면접관입니다.

문제: ${problem?.title || '시스템 아키텍처 설계'}
시나리오: ${scenario}
미션: ${missions}

평가 힌트:
${nfrHints}

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
 * 5가지 비기능적 요소(NFR) 기반 LLM 평가 수행
 * - Scalability (확장성)
 * - Availability (가용성)
 * - Performance (성능/지연시간)
 * - Consistency (데이터 일관성)
 * - Reliability & Data Integrity (신뢰성 및 무결성)
 */
export async function evaluateArchitecture(problem, architectureContext, generatedQuestion, userAnswer, deepDiveAnswers) {
  // 핵심 컴포넌트 목록 (학생이 포함해야 하는 것들 - 이름과 타입 포함)
  const keyComponents = problem?.keyComponents || [];
  const keyComponentsText = keyComponents.length > 0
    ? keyComponents.map(c => `- ${c.name} (타입: ${c.type})`).join('\n')
    : '- 명시된 핵심 컴포넌트 없음';

  // 새 데이터 구조에서 정보 추출
  const scenario = problem?.scenario || '';
  const missions = problem?.missions || [];
  const missionsText = missions.length > 0
    ? missions.map(m => `- ${m}`).join('\n')
    : '- 없음';

  // 기술 요구사항 (engineering_spec)
  const engineeringSpec = problem?.engineeringSpec || {};
  const specText = Object.keys(engineeringSpec).length > 0
    ? Object.entries(engineeringSpec).map(([key, val]) => `- ${key}: ${val}`).join('\n')
    : '- 없음';

  // 필수 연결 관계 (rubric_functional.required_flows)
  const requiredFlows = problem?.requiredFlows || [];
  const flowsText = requiredFlows.length > 0
    ? requiredFlows.map(f => `- ${f.from} → ${f.to}: ${f.reason}`).join('\n')
    : '- 없음';

  // 비기능적 평가 기준 (rubric_non_functional)
  const rubricNfr = problem?.rubricNonFunctional || [];
  const nfrText = rubricNfr.length > 0
    ? rubricNfr.map(r => `- [${r.category}] ${r.question_intent}\n  모범답안: ${r.model_answer}`).join('\n')
    : '- 없음';

  // 평가 토픽 (기존 호환성)
  const questionTopics = problem?.questionTopics || [];
  const topicsText = questionTopics.length > 0
    ? questionTopics.map(t => `- ${t.topic}: ${t.keywords?.join(', ') || t.modelAnswer || ''}`).join('\n')
    : '- 없음';

  const prompt = `당신은 시스템 아키텍처 면접관입니다.
다음 **5가지 비기능적 요소(NFR)** 평가 기준을 바탕으로 학생의 아키텍처를 평가해주세요.

## 문제 정보
- 제목: ${problem?.title || '시스템 아키텍처 설계'}
- 시나리오: ${scenario}

### 미션:
${missionsText}

### 기술 요구사항:
${specText}

## 참조 정보 (평가 기준으로 활용)

### 필수 포함 컴포넌트:
${keyComponentsText}

### 필수 연결 관계:
${flowsText}

### 비기능적 평가 기준:
${nfrText}

### 평가 토픽:
${topicsText}

## 5가지 비기능적 요소(NFR) 평가 기준

### 1. Scalability (확장성) - 20%
- 정의: 사용자 수나 데이터 양이 급격히 늘어날 때 시스템이 버틸 수 있는가?
- 평가 포인트:
  1. Scale-up vs Scale-out: 단일 장비 업그레이드보다 수평적 확장을 선호하는가?
  2. Load Balancing: 트래픽을 여러 서버로 분산시키는가?
  3. Database Sharding: 데이터가 많을 때 파티셔닝 전략을 사용하는가?

### 2. Availability (가용성) - 20%
- 정의: 특정 서버나 컴포넌트에 장애가 발생해도 서비스가 계속되는가?
- 평가 포인트:
  1. SPOF (Single Point of Failure) 제거: 하나가 죽으면 다 죽는 구간이 없는가?
  2. Replication (복제): DB나 서버를 다중화(Master-Slave)해두었는가?
  3. Failover: 장애 발생 시 자동으로 예비 장비로 전환되는가?

### 3. Performance (성능/지연시간) - 20%
- 정의: 사용자의 요청에 대해 얼마나 빠르게 응답하는가?
- 평가 포인트:
  1. Caching: 자주 쓰는 데이터를 메모리(Redis)나 CDN에 저장했는가?
  2. Asynchronous Processing: 오래 걸리는 작업은 큐(Message Queue)로 비동기 처리하는가?
  3. Indexing: DB 조회 속도를 높이기 위해 인덱스를 적절히 사용했는가?

### 4. Consistency (데이터 일관성) - 20%
- 정의: 모든 사용자가 동시에 같은 데이터를 보는가?
- 평가 포인트:
  1. ACID 트랜잭션: 결제, 재고 등 중요한 데이터에 트랜잭션을 적용했는가?
  2. Locking Strategy: 동시 접속 시 충돌 방지(Lock) 대책이 있는가?
  3. Eventual Consistency: 실시간성이 덜 중요한 데이터는 최종 일관성을 택했는가?

### 5. Reliability & Data Integrity (신뢰성 및 무결성) - 20%
- 정의: 데이터가 유실되거나 훼손되지 않는가?
- 평가 포인트:
  1. Data Persistence: 데이터를 메모리에만 두지 않고 디스크(DB/Storage)에 영구 저장하는가?
  2. Idempotency (멱등성): 같은 요청을 두 번 보내도 결과가 한 번만 처리되는가?

## 학생의 제출물

### 아키텍처 설계:
${architectureContext}

### 심층 질문: ${generatedQuestion || problem?.followUpQuestion || ''}
### 학생의 최종 답변: ${userAnswer || '(답변 없음)'}
### 최종 답변 길이: ${userAnswer ? userAnswer.length : 0}자

### 심화 질문 답변들:
${deepDiveAnswers || '(심화 질문에 답변하지 않음 - interviewScore 최대 20점 제한)'}

### 답변 분석 요청:
- 학생 답변이 비어있거나 매우 짧으면(30자 미만) interviewScore는 0~20점으로 제한
- 심화 질문에 모두 스킵하거나 답변이 없으면 interviewScore에서 -30점
- 구체적인 기술 용어 없이 막연한 답변이면 interviewScore 최대 40점

## 평가 지침 (엄격하게 평가할 것!)

### 점수 배분 (총 100점)
- **아키텍처 설계 (40점)**: NFR 5개 영역 평균 * 0.4
- **답변 품질 (60점)**: 심층 질문 + 심화 질문 답변 품질 * 0.6

### 답변 품질 평가 기준 (매우 중요!)
1. **답변이 없거나 10자 미만**: interviewScore = 0~10점
2. **답변이 짧거나 피상적 (10~50자)**: interviewScore = 10~30점
3. **답변이 있지만 기술 용어 없음**: interviewScore = 30~50점
4. **답변이 구체적이고 기술 용어 포함**: interviewScore = 50~80점
5. **완벽한 답변 (구체적 + 트레이드오프 언급)**: interviewScore = 80~100점

### 컴포넌트 검증
1. 필수 컴포넌트 누락 시: NFR 점수에서 컴포넌트당 -10점
2. 연결 관계가 논리적이지 않으면: NFR 점수에서 -15점

### 엄격한 채점 원칙
- **기본 점수는 0점에서 시작** (관대한 채점 금지)
- 답변을 거의 안 쓰면 총점 40점을 넘을 수 없음
- 심화 질문에 모두 스킵하면 interviewScore 최대 20점
- 기술 용어(Load Balancer, Replication, Cache, Queue, Sharding, Failover 등) 사용 여부 반드시 체크

### 최종 점수 계산
score = (NFR 5개 평균점수 * 0.4) + (interviewScore * 0.6)

예시:
- NFR 평균 80점 + 답변 0점 = 80*0.4 + 0*0.6 = 32점
- NFR 평균 60점 + 답변 50점 = 60*0.4 + 50*0.6 = 54점
- NFR 평균 80점 + 답변 80점 = 80*0.4 + 80*0.6 = 80점

## 출력 형식 (JSON만 출력, 다른 텍스트 없이):
{
  "score": 0-100 (위의 점수 계산 공식 반드시 적용),
  "grade": "excellent"(80+) | "good"(60-79) | "needs-improvement"(40-59) | "poor"(0-39),
  "componentCoverage": {
    "included": ["포함된 필수 컴포넌트"],
    "missing": ["누락된 필수 컴포넌트"],
    "extra": ["추가로 포함한 좋은 컴포넌트"]
  },
  "nfrScores": {
    "scalability": {
      "score": 0-100,
      "feedback": "확장성 관련 구체적 피드백 (Scale-out, Load Balancing, Sharding 고려 여부)",
      "checklist": {
        "scaleOut": true/false,
        "loadBalancing": true/false,
        "sharding": true/false
      }
    },
    "availability": {
      "score": 0-100,
      "feedback": "가용성 관련 구체적 피드백 (SPOF 제거, Replication, Failover 고려 여부)",
      "checklist": {
        "noSPOF": true/false,
        "replication": true/false,
        "failover": true/false
      }
    },
    "performance": {
      "score": 0-100,
      "feedback": "성능 관련 구체적 피드백 (Caching, Async Processing, Indexing 고려 여부)",
      "checklist": {
        "caching": true/false,
        "asyncProcessing": true/false,
        "indexing": true/false
      }
    },
    "consistency": {
      "score": 0-100,
      "feedback": "일관성 관련 구체적 피드백 (ACID, Locking, Eventual Consistency 고려 여부)",
      "checklist": {
        "acidTransaction": true/false,
        "lockingStrategy": true/false,
        "eventualConsistency": true/false
      }
    },
    "reliability": {
      "score": 0-100,
      "feedback": "신뢰성 관련 구체적 피드백 (Data Persistence, Idempotency 고려 여부)",
      "checklist": {
        "dataPersistence": true/false,
        "idempotency": true/false
      }
    }
  },
  "interviewScore": {
    "score": 0-100,
    "answerLength": "답변 총 글자수",
    "hasKeyTerms": true/false,
    "keyTermsUsed": ["사용된 기술 용어들"],
    "feedback": "면접 답변에 대한 종합 피드백 (답변이 없으면 '답변이 제출되지 않았습니다' 명시)"
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
