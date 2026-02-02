/**
 * Architecture Practice API Service (Enhanced Version)
 * run_all_tests.mjs의 Elite/Basic 로직을 통합한 지능형 아키텍처 평가 서비스
 */

import architectureProblems from '@/data/architecture.json';

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

/**
 * OpenAI API 호출 기본 함수
 */
async function callOpenAI(prompt, options = {}) {
  const {
    model = 'gpt-4o-mini', // 성능과 비용을 고려해 4o-mini 권장
    maxTokens = 1500,
    temperature = 0.6,
    systemMessage = null
  } = options;

  const messages = [];
  if (systemMessage) {
    messages.push({ role: 'system', content: systemMessage });
  }
  messages.push({ role: 'user', content: prompt });

  try {
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

    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    const data = await response.json();
    return data.choices[0].message.content.trim();
  } catch (error) {
    console.error('OpenAI Call Error:', error);
    throw error;
  }
}

/**
 * 아키텍처 데이터를 프롬프트용 텍스트로 변환
 */
function formatArchitectureContext(components, connections) {
  const componentList = components.map(c => `- ${c.text} (타입: ${c.type})`).join('\n');
  const connectionList = connections.map(conn => {
    const from = components.find(c => c.id === conn.from);
    const to = components.find(c => c.id === conn.to);
    return from && to ? `- ${from.text} → ${to.text}` : null;
  }).filter(Boolean).join('\n');
  return { componentList, connectionList };
}

/**
 * 학생의 설계 수준을 판단하여 적절한 질문 세트 생성 (Elite vs Basic)
 */
export async function generateArchitectureAnalysisQuestions(problem, components, connections) {
  const { componentList, connectionList } = formatArchitectureContext(components, connections);
  
  // 설계 수준 판단 로직 (컴포넌트 3개 이하이거나 연결이 너무 적으면 Basic)
  const isPoorDesign = components.length <= 3 || connections.length < components.length - 1;
  
  let prompt = '';
  
  if (isPoorDesign) {
    // Basic 모드: 생존 가능성 및 누락 로직 점검
    prompt = `당신은 아키텍처 멘토입니다. 학생의 설계는 핵심 로직이 누락되었거나 운영이 불가능한 구조적 결함이 있습니다. 스스로 '생존 가능성'을 점검하게 유도하세요.

## 문제 정보
- 제목: ${problem.title}
- 시나리오: ${problem.scenario}

## 학생의 아키텍처 설계
### 컴포넌트:
${componentList}
### 연결 관계:
${connectionList}

## 질문 생성 가이드 (Basic - Viability & Integrity)
1. **데이터의 행방**: 데이터가 최종적으로 어디에 어떻게 저장되는지 흐름 추적.
2. **생존 가능성**: 단일 장애 지점(SPOF)이나 가용성 문제 지적.
3. **보안/무결성**: 치명적인 보안 구멍이나 데이터 유실 가능성 유도.

## 출력 형식 (JSON만):
{
  "questions": [
    {"category": "데이터 흐름", "question": "질문"},
    {"category": "가용성", "question": "질문"},
    {"category": "설계 결함", "question": "질문"}
  ]
}`;
  } else {
    // Elite 모드: 최적화 및 트레이드오프 압박 면접
    prompt = `당신은 시니어 시스템 아키텍트 면접관입니다. 학생의 설계는 수준급이므로, '한계점'과 '트레이드오프'를 시험하는 압박 면접을 진행하세요.

## 문제 정보
- 제목: ${problem.title}
- 시나리오: ${problem.scenario}

## 학생의 아키텍처 설계
### 컴포넌트:
${componentList}
### 연결 관계:
${connectionList}

## 질문 생성 가이드 (Elite - Optimization & Trade-off)
1. **최적화와 비용**: 성능 유지 및 비용 절감 등 비즈니스 관점의 트레이드오프.
2. **고도화된 장애**: Cache Stampede, 메시지 순서, DB 병목 등 기술적 엣지 케이스.
3. **기술적 방어**: 대안 기술과의 비교를 통한 논리적 근거 압박.

## 출력 형식 (JSON만):
{
  "questions": [
    {"category": "최적화/비용", "question": "질문"},
    {"category": "장애 시나리오", "question": "질문"},
    {"category": "트레이드오프", "question": "질문"}
  ]
}`;
  }

  try {
    const response = await callOpenAI(prompt, { temperature: isPoorDesign ? 0.6 : 0.7 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    return jsonMatch ? JSON.parse(jsonMatch[0]).questions : [];
  } catch (error) {
    console.error('Question generation error:', error);
    return [
      { category: '공통', question: '현재 설계에서 가장 트래픽이 몰릴 것으로 예상되는 지점은 어디인가요?' },
      { category: '공통', question: '데이터의 일관성을 보장하기 위해 어떤 전략을 사용하셨나요?' },
      { category: '공통', question: '특정 컴포넌트 장애 시 전체 시스템에 미치는 영향은 무엇인가요?' }
    ];
  }
}

/**
 * 아키텍처 평가 실행 (엄격한 채점 로직)
 */
export async function evaluateArchitecture(problem, architectureContext, generatedQuestion, userAnswer, deepDiveQnA) {
  const keyComponentsText = (problem?.keyComponents || []).map(c => `- ${c.name} (${c.type})`).join('\n');
  const rubricNfr = problem?.rubricNonFunctional || problem?.rubric_non_functional || [];
  const nfrText = rubricNfr.map(r => `- [${r.category}] 의도: ${r.question_intent}\n  모범답안: ${r.model_answer}`).join('\n');
  
  const deepDiveArray = Array.isArray(deepDiveQnA) ? deepDiveQnA : [];
  const deepDiveQnAText = deepDiveArray.map((item, idx) => 
    `[질문 ${idx + 1}] Q: ${item.question}\nA: ${item.answer || '(미응답)'}`
  ).join('\n\n');

  const prompt = `당신은 시스템 아키텍처 전문 평가관입니다. 학생의 설계와 면접 답변을 엄격하게 채점하세요.

## 1. 평가 기준
- 문제: ${problem?.title}
- 필수 컴포넌트:
${keyComponentsText}
- 비기능 요구사항 및 모범답안:
${nfrText}

## 2. 학생 제출 자료
- 아키텍처 요약: ${architectureContext}
- 심화 인터뷰 답변:
${deepDiveQnAText}
- 최종 종합 답변: ${userAnswer}

## 3. 채점 규칙
- Architecture Score (50점): 필수 컴포넌트 및 흐름의 논리적 정합성.
- Interview Score (50점): 답변의 구체성, 기술 용어 활용, 트레이드오프 이해도.
- **주의**: 모범 답안과 표현이 다르더라도 핵심 개념이 일치하면 정답으로 인정합니다.

## 출력 형식 (JSON만):
{
  "totalScore": 0,
  "grade": "excellent/good/needs-improvement/poor",
  "summary": "총평",
  "architectureEvaluation": { "score": 0, "details": [], "missingComponents": [], "incorrectFlows": [] },
  "interviewEvaluation": {
    "score": 0,
    "questionAnalysis": [
      { "question": "", "category": "", "userAnswer": "", "modelAnswer": "", "matchStatus": "match/partial/mismatch", "feedback": "" }
    ]
  },
  "strengths": [], "weaknesses": [], "suggestions": []
}`;

  try {
    const response = await callOpenAI(prompt, { temperature: 0.3 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const result = JSON.parse(jsonMatch[0]);
      result.score = result.totalScore;
      return result;
    }
    throw new Error('Invalid JSON');
  } catch (error) {
    return { totalScore: 0, summary: '평가 처리 중 오류 발생' };
  }
}

// 나머지 헬퍼 함수들 (fetchProblems, sendChatMessage 등)은 기존 구조 유지
export async function fetchProblems() { return architectureProblems; }
export async function sendChatMessage(chatContext, chatHistory, userMessage) { 
  /* 기존 유지 또는 필요시 위 callOpenAI 활용 구조로 변경 */ 
}