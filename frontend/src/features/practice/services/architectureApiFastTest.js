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
    model = 'gpt-3.5-turbo',
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
 * 사용자 설명 기반 꼬리질문 생성
 * 사용자가 먼저 아키텍처 설명을 제출하면, 그 설명을 분석하여 꼬리질문 생성
 */
export async function generateFollowUpQuestions(problem, components, connections, mermaidCode, userExplanation) {
  const componentList = components.map(c => `- ${c.text} (타입: ${c.type})`).join('\n');
  const connectionList = connections.map(conn => {
    const from = components.find(c => c.id === conn.from);
    const to = components.find(c => c.id === conn.to);
    return from && to ? `- ${from.text} → ${to.text}` : null;
  }).filter(Boolean).join('\n');

  const scenario = problem?.scenario || '';
  const rubricNfr = problem?.rubricNonFunctional || problem?.rubric_non_functional || [];
  const nfrTopics = rubricNfr.map(r => `${r.category}: ${r.question_intent}`).join('\n') || '없음';

  // 컴포넌트 타입별로 정리
  const componentTypes = [...new Set(components.map(c => c.type))];
  const hasCache = components.some(c => c.type === 'cache' || c.text.toLowerCase().includes('cache') || c.text.toLowerCase().includes('redis'));
  const hasQueue = components.some(c => c.type === 'queue' || c.text.toLowerCase().includes('queue') || c.text.toLowerCase().includes('kafka'));
  const hasLoadBalancer = components.some(c => c.type === 'loadbalancer' || c.text.toLowerCase().includes('load') || c.text.toLowerCase().includes('lb'));
  const hasDatabase = components.some(c => c.type === 'database' || c.text.toLowerCase().includes('db') || c.text.toLowerCase().includes('database'));

  const prompt = `당신은 시스템 아키텍처 면접관입니다.
학생이 설계한 아키텍처와 그에 대한 설명을 분석하여, 꼬리질문 3개를 생성하세요.

## 문제 정보
- 제목: ${problem?.title || '시스템 아키텍처 설계'}
- 시나리오: ${scenario}

### 평가 기준:
${nfrTopics}

## ⚠️ 중요: 학생이 실제로 배치한 컴포넌트 목록 (이것만 기준으로 질문!)
### 컴포넌트 (${components.length}개):
${componentList || '없음'}

### 컴포넌트 타입: ${componentTypes.join(', ')}
- 캐시 포함 여부: ${hasCache ? '있음' : '없음'}
- 메시지 큐 포함 여부: ${hasQueue ? '있음' : '없음'}
- 로드밸런서 포함 여부: ${hasLoadBalancer ? '있음' : '없음'}
- 데이터베이스 포함 여부: ${hasDatabase ? '있음' : '없음'}

### 연결 관계 (${connections.length}개):
${connectionList || '없음'}

## 학생의 설명
"${userExplanation}"

---

## ⚠️ 핵심 규칙 (반드시 준수!)

### 절대 금지 사항
1. **없는 컴포넌트에 대해 질문하지 말 것**
   - 캐시가 없으면 → 캐시 관련 질문 금지
   - 메시지 큐가 없으면 → 비동기 처리 질문 금지
   - 로드밸런서가 없으면 → 부하 분산 질문 금지

2. **학생이 배치한 컴포넌트만** 기준으로 질문해야 함
   - 위 '컴포넌트 목록'에 있는 것만 언급 가능

### 질문 생성 기준
1. **실제 배치 컴포넌트 관련**: 학생이 배치한 특정 컴포넌트의 역할, 연결 이유
2. **누락 지적 (있는 것 기준)**: 배치한 컴포넌트들 간의 연결에서 부족한 부분
3. **설계 의도 확인**: 왜 이런 구조를 선택했는지

## 출력 형식 (JSON만):
{
  "student_components": ["학생이 실제로 배치한 컴포넌트 목록을 여기에 복사"],
  "explanation_analysis": {
    "key_points": ["학생이 언급한 핵심 포인트"],
    "unclear_points": ["불명확한 부분"],
    "missing_aspects": ["배치된 컴포넌트 기준으로 누락된 관점만"]
  },
  "questions": [
    {"category": "배치 컴포넌트 관련", "question": "학생이 배치한 특정 컴포넌트에 대한 질문", "intent": "이 질문으로 확인하려는 것"},
    {"category": "연결 관계", "question": "배치된 컴포넌트들의 연결에 대한 질문", "intent": "이 질문으로 확인하려는 것"},
    {"category": "설계 의도", "question": "설계 선택 이유에 대한 질문", "intent": "이 질문으로 확인하려는 것"}
  ]
}`;

  try {
    const response = await callOpenAI(prompt, { maxTokens: 800, temperature: 0.7 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return {
        analysis: parsed.explanation_analysis || {},
        questions: parsed.questions || []
      };
    }
    throw new Error('Invalid JSON');
  } catch (error) {
    console.error('Follow-up questions error:', error);
    // Fallback: 학생이 배치한 컴포넌트 기반 일반 질문
    const firstComponent = components[0]?.text || '주요 컴포넌트';
    const lastComponent = components[components.length - 1]?.text || '데이터 저장소';

    return {
      analysis: {
        key_points: ['분석 실패'],
        unclear_points: [],
        missing_aspects: []
      },
      questions: [
        {
          category: '설계 의도',
          question: `${firstComponent}를 이 위치에 배치한 이유는 무엇인가요?`,
          intent: '설계 의도 확인'
        },
        {
          category: '데이터 흐름',
          question: `${firstComponent}에서 ${lastComponent}까지 데이터가 어떻게 흐르는지 설명해주세요.`,
          intent: '데이터 흐름 이해도 확인'
        },
        {
          category: '장애 대응',
          question: '현재 설계에서 단일 장애점(SPOF)이 있다면 어디이며, 어떻게 해결하시겠습니까?',
          intent: '장애 대응 전략 확인'
        }
      ]
    };
  }
}
