/**
 * Architecture Practice API Service (Enhanced Version)
 * 질문별 모범 답안 비교, 파트별 점수 근거 명시, 종합 평가 로직 포함
 */

import architectureProblems from '@/data/architecture.json';

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

/**
 * OpenAI API 호출 기본 함수
 */
async function callOpenAI(prompt, options = {}) {
  const {
    model = 'gpt-4o-mini',
    maxTokens = 1500,
    temperature = 0.4,
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
 * 문제 데이터 로드
 */
export async function fetchProblems() {
  return architectureProblems;
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
질문만 출력하세요.`;

  try {
    return await callOpenAI(prompt, { maxTokens: 200 });
  } catch (error) {
    console.error('Deep dive question error:', error);
    return `${fromComp.text}와 ${toComp.text}의 연결에서 예상되는 데이터 흐름과 잠재적인 병목 현상에 대해 설명해주세요.`;
  }
}

/**
 * 아키텍처 분석 기반 심층 질문 3개 생성
 */
export async function generateArchitectureAnalysisQuestions(problem, components, connections, mermaidCode) {
  const componentList = components.map(c => `- ${c.text} (타입: ${c.type})`).join('\n');
  const connectionList = connections.map(conn => {
    const from = components.find(c => c.id === conn.from);
    const to = components.find(c => c.id === conn.to);
    return from && to ? `- ${from.text} → ${to.text}` : null;
  }).filter(Boolean).join('\n');

  const scenario = problem?.scenario || '';
  const rubricNfr = problem?.rubricNonFunctional || problem?.rubric_non_functional || [];
  const nfrTopics = rubricNfr.map(r => `${r.category}: ${r.question_intent}`).join('\n') || '없음';

  const prompt = `당신은 시스템 아키텍처 면접관입니다.
학생이 설계한 아키텍처를 분석하고, 심층적인 면접 질문 3개를 생성해주세요.

## 문제 정보
- 제목: ${problem?.title || '시스템 아키텍처 설계'}
- 시나리오: ${scenario}

### 평가 기준 (이 관점에서 질문할 것):
${nfrTopics}

## 학생의 아키텍처 설계
### 컴포넌트 (${components.length}개):
${componentList || '없음'}

### 연결 관계 (${connections.length}개):
${connectionList || '없음'}

## 질문 생성 기준
1. **설계 의도**: 왜 이런 구조를 선택했는지
2. **확장성/성능**: 트래픽 증가, 병목 현상, 캐싱 전략
3. **장애 대응**: 장애 시 시스템 동작, 복구 전략

## 출력 형식 (JSON만):
{
  "questions": [
    {"category": "설계 의도", "question": "질문"},
    {"category": "확장성/성능", "question": "질문"},
    {"category": "장애 대응", "question": "질문"}
  ]
}`;

  try {
    const response = await callOpenAI(prompt, { maxTokens: 600, temperature: 0.7 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return parsed.questions || [];
    }
    throw new Error('Invalid JSON');
  } catch (error) {
    console.error('Architecture analysis questions error:', error);
    return [
      { category: '설계 의도', question: `${problem?.title || '이 시스템'}에서 현재 설계한 아키텍처의 핵심 컴포넌트와 그 선택 이유를 설명해주세요.` },
      { category: '확장성/성능', question: '트래픽이 10배로 증가할 경우, 가장 먼저 병목이 발생할 곳은 어디이며 어떻게 대응하시겠습니까?' },
      { category: '장애 대응', question: '주요 컴포넌트 중 하나가 장애가 발생했을 때, 시스템은 어떻게 동작하며 복구 전략은 무엇인가요?' }
    ];
  }
}

/**
 * 평가 모달용 질문 생성
 */
export async function generateEvaluationQuestion(problem, architectureContext) {
  const scenario = problem?.scenario || '';
  const missions = problem?.missions?.join(', ') || '';
  const rubricNfr = problem?.rubricNonFunctional || problem?.rubric_non_functional || [];
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
트레이드오프, 확장성, 장애 대응 등에 대해 질문하세요.
질문만 출력하세요.`;

  try {
    return await callOpenAI(prompt, { maxTokens: 300 });
  } catch (error) {
    console.error('Question generation error:', error);
    return problem?.followUpQuestion || '설계하신 아키텍처에서 가장 중요한 트레이드오프는 무엇인가요?';
  }
}

/**
 * 아키텍처 평가 실행 (개선된 버전)
 * - 질문별 모범 답안 비교
 * - 파트별 점수 근거 명시
 * - 50(설계)/50(면접) 평가 로직
 * @param {Object} problem - 문제 데이터
 * @param {string} architectureContext - 아키텍처 컨텍스트
 * @param {string} generatedQuestion - 생성된 최종 질문
 * @param {string} userAnswer - 사용자의 최종 답변
 * @param {Array} deepDiveQnA - 심화 질문/답변 배열 [{category, question, answer}]
 */
export async function evaluateArchitecture(problem, architectureContext, generatedQuestion, userAnswer, deepDiveQnA) {
  // 기준 데이터 추출
  const keyComponents = problem?.keyComponents || [];
  const keyComponentsText = keyComponents.length > 0
    ? keyComponents.map(c => `- ${c.name} (타입: ${c.type})`).join('\n')
    : '- 명시된 핵심 컴포넌트 없음';

  const scenario = problem?.scenario || '';
  const missions = problem?.missions || [];
  const missionsText = missions.length > 0 ? missions.map(m => `- ${m}`).join('\n') : '- 없음';

  const requiredFlows = problem?.requiredFlows || [];
  const flowsText = requiredFlows.length > 0
    ? requiredFlows.map(f => `- ${f.from} → ${f.to}: ${f.reason}`).join('\n')
    : '- 없음';

  const rubricNfr = problem?.rubricNonFunctional || problem?.rubric_non_functional || [];
  const nfrText = rubricNfr.length > 0
    ? rubricNfr.map(r => `- [${r.category}] 의도: ${r.question_intent}\n  모범답안: ${r.model_answer}`).join('\n')
    : '- 없음';

  // 심화 질문/답변 배열 처리
  const deepDiveArray = Array.isArray(deepDiveQnA) ? deepDiveQnA : [];
  const deepDiveQnAText = deepDiveArray.length > 0
    ? deepDiveArray.map((item, idx) =>
        `[질문 ${idx + 1} - ${item.category || '일반'}]\nQ: ${item.question}\nA: ${item.answer || '(답변 없음)'}`
      ).join('\n\n')
    : '(심화 질문에 답변하지 않음)';

  // 각 질문을 JSON 형태로 정리 (LLM이 분석하기 쉽게)
  const deepDiveQuestionsJson = deepDiveArray.map((item, idx) => ({
    index: idx + 1,
    category: item.category || '일반',
    question: item.question,
    userAnswer: item.answer || ''
  }));

  // 답변 길이 체크
  const answerLength = (userAnswer || '').length;
  const totalDeepDiveLength = deepDiveArray.reduce((sum, item) => sum + (item.answer || '').length, 0);
  const answeredCount = deepDiveArray.filter(item => item.answer && item.answer.length > 0).length;

  const prompt = `당신은 시스템 아키텍처 전문 평가관입니다.
학생이 제출한 [아키텍처 다이어그램]과 [면접 답변]을 바탕으로 **엄격하게** 채점하세요.

## 1. 평가 기준 (출처: 문제 정의서)

### 문제 정보
- 제목: ${problem?.title || '시스템 아키텍처 설계'}
- 시나리오: ${scenario}
- 미션: ${missionsText}

### 필수 컴포넌트 (Architecture Score 기준):
${keyComponentsText}

### 필수 데이터 흐름:
${flowsText}

### 비기능적 요구사항 & 모범 답안 (Interview Score 기준):
${nfrText}

## 2. 학생 제출 자료

### 아키텍처 설계:
${architectureContext}

### 최종 질문: ${generatedQuestion || '없음'}
### 학생의 최종 답변: ${userAnswer || '(답변 없음)'}
### 최종 답변 길이: ${answerLength}자

### 심화 질문 및 답변 (${deepDiveArray.length}개 중 ${answeredCount}개 답변):
${deepDiveQnAText}

### 심화 질문 데이터 (JSON):
${JSON.stringify(deepDiveQuestionsJson, null, 2)}

### 심화 답변 총 길이: ${totalDeepDiveLength}자

## 3. 채점 규칙 (매우 엄격하게!)

### Architecture Score (50점 만점)
- 필수 컴포넌트 포함: 25점
- 연결 흐름 논리성: 25점
- 누락된 컴포넌트당 -5점
- 잘못된 연결당 -5점

### Interview Score (50점 만점)
- **답변이 없거나 30자 미만**: 최대 10점
- **답변이 짧음 (30~100자)**: 최대 25점
- **심화 질문 모두 스킵**: -15점
- **기술 용어 없이 막연한 답변**: 최대 30점
- **모범 답안 키워드 포함**: 가산점

### 모범 답안과 비교 (중요!)
위 '비기능적 요구사항'의 모범답안과 학생 답변을 비교하여:
- 일치하는 키워드/개념이 있으면 명시
- 누락된 핵심 개념이 있으면 감점 사유로 명시

### 최종 점수 계산
totalScore = architectureScore + interviewScore (100점 만점)

## 4. 출력 형식 (JSON만 출력!)
**중요: questionAnalysis에는 위에서 제공된 모든 심화 질문(${deepDiveArray.length}개)에 대해 각각 분석을 포함해야 합니다.**

{
  "totalScore": 0,
  "grade": "excellent(80+)" | "good(60-79)" | "needs-improvement(40-59)" | "poor(0-39)",
  "summary": "총평 2-3문장 (강점과 약점 명확히)",

  "architectureEvaluation": {
    "score": 0,
    "details": [
      {"item": "필수 컴포넌트", "score": 0, "basis": "포함된 것과 누락된 것"},
      {"item": "연결 흐름", "score": 0, "basis": "논리적 연결 여부"}
    ],
    "missingComponents": ["누락된 컴포넌트"],
    "incorrectFlows": ["잘못된 연결"]
  },

  "interviewEvaluation": {
    "score": 0,
    "answerAnalysis": {
      "length": ${answerLength + totalDeepDiveLength},
      "hasKeyTerms": true/false,
      "keyTermsFound": ["발견된 기술 용어"],
      "keyTermsMissing": ["누락된 핵심 키워드"]
    },
    "questionAnalysis": [
      {
        "question": "실제 질문 내용을 여기에 복사",
        "category": "질문 카테고리",
        "userAnswer": "학생이 작성한 답변 (없으면 빈 문자열)",
        "modelAnswer": "이 질문에 대한 모범 답안",
        "matchStatus": "match/partial/mismatch",
        "deductionReason": "감점 사유 (있으면)",
        "score": 0,
        "feedback": "이 답변에 대한 피드백"
      }
    ]
  },

  "strengths": ["구체적 강점1", "강점2"],
  "weaknesses": ["구체적 약점1"],
  "suggestions": ["학습 제안1", "제안2"]
}`;

  try {
    const response = await callOpenAI(prompt, { maxTokens: 2000, temperature: 0.3 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const result = JSON.parse(jsonMatch[0]);
      // 기존 호환성을 위해 score 필드도 추가
      result.score = result.totalScore;
      return result;
    }
    throw new Error('Invalid JSON response');
  } catch (error) {
    console.error('Evaluation error:', error);
    // Fallback 응답 - 질문 정보 포함
    const fallbackQuestionAnalysis = deepDiveArray.map(item => ({
      question: item.question,
      category: item.category || '일반',
      userAnswer: item.answer || '',
      modelAnswer: '평가 오류로 모범 답안을 불러올 수 없습니다.',
      matchStatus: 'mismatch',
      deductionReason: '평가 오류',
      score: 0,
      feedback: '다시 시도해주세요.'
    }));

    return {
      totalScore: 30,
      score: 30,
      grade: 'poor',
      summary: '평가 중 오류가 발생했습니다. 다시 시도해주세요.',
      architectureEvaluation: { score: 15, details: [], missingComponents: [], incorrectFlows: [] },
      interviewEvaluation: {
        score: 15,
        answerAnalysis: { length: answerLength + totalDeepDiveLength, hasKeyTerms: false, keyTermsFound: [], keyTermsMissing: [] },
        questionAnalysis: fallbackQuestionAnalysis
      },
      strengths: [],
      weaknesses: ['평가 오류'],
      suggestions: ['다시 시도해주세요']
    };
  }
}

/**
 * 채팅 메시지 전송
 */
export async function sendChatMessage(chatContext, chatHistory, userMessage) {
  const systemPrompt = `당신은 시스템 아키텍처 면접관입니다.
학생이 주어진 문제의 요구사항에 대해 질문하면 답변해주세요.

**규칙:**
1. 직접적인 정답이나 완성된 아키텍처는 알려주지 마세요.
2. 힌트와 고려사항을 제공하되, 학생이 스스로 생각하도록 유도하세요.
3. 답변은 3-5문장으로 간결하게.

**현재 문제:**
${chatContext}

한국어로 답변하세요.`;

  const messages = [
    { role: 'system', content: systemPrompt },
    ...chatHistory.map(msg => ({ role: msg.role, content: msg.content })),
    { role: 'user', content: userMessage }
  ];

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getApiKey()}`
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages,
        max_tokens: 500,
        temperature: 0.7
      })
    });

    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    const data = await response.json();
    return data.choices[0].message.content;
  } catch (error) {
    console.error('Chat error:', error);
    throw error;
  }
}
