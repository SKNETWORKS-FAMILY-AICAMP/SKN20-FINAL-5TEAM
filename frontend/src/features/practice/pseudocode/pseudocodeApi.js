/**
 * Pseudocode Practice API Service (Deep Dive Evaluation)
 * SystemArchitecture 스타일의 면접관 페르소나 평가 방식 적용
 */

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
 * Pseudocode 심층 질문 3개 생성
 * - 의사코드를 기반으로 면접관이 추가로 확인할 내용 질문
 */
export async function generatePseudocodeDeepDiveQuestions(problem, pseudocode) {
  const prompt = `당신은 알고리즘 및 의사코드 작성 능력을 평가하는 면접관입니다.

## 문제 정보
- 제목: ${problem?.title || '알고리즘 문제'}
- 설명: ${problem?.description || ''}

## 학생이 작성한 의사코드
${pseudocode}

## 질문 생성 기준
학생의 의사코드를 보고 다음 3가지 관점에서 심화 질문을 생성해주세요:

1. **논리 이해도**: 학생이 이 알고리즘을 제대로 이해하고 작성했는지 확인
   - 예: "왜 이런 순서로 처리하도록 설계했나요?"
   - 예: "이 부분에서 다른 접근 방법은 고려해보셨나요?"

2. **예외 처리**: 엣지 케이스나 예외 상황에 대한 이해도
   - 예: "입력값이 비어있거나 음수일 때는 어떻게 처리하나요?"
   - 예: "이 로직에서 무한루프가 발생할 가능성은 없나요?"

3. **최적화**: 시간/공간 복잡도 및 개선 가능성
   - 예: "이 알고리즘의 시간 복잡도는 어떻게 되나요?"
   - 예: "더 효율적인 자료구조를 사용할 수 있을까요?"

## 출력 형식 (JSON만):
{
  "questions": [
    {"category": "논리 이해도", "question": "질문1"},
    {"category": "예외 처리", "question": "질문2"},
    {"category": "최적화", "question": "질문3"}
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
    console.error('Deep dive questions generation error:', error);
    // Fallback 질문
    return [
      { category: '논리 이해도', question: '작성하신 의사코드의 핵심 로직과 그렇게 설계한 이유를 설명해주세요.' },
      { category: '예외 처리', question: '입력값이 예상과 다르거나 엣지 케이스가 발생할 때 어떻게 처리하나요?' },
      { category: '최적화', question: '이 알고리즘의 시간 복잡도는 어떻게 되며, 더 개선할 방법이 있을까요?' }
    ];
  }
}

/**
 * Pseudocode 종합 평가
 * - 의사코드 자체 평가 (50점) + 면접 답변 평가 (50점)
 * 
 * @param {Object} problem - 문제 데이터
 * @param {string} pseudocode - 학생이 작성한 의사코드
 * @param {Array} deepDiveQnA - 심화 질문/답변 [{category, question, answer}]
 */
export async function evaluatePseudocode(problem, pseudocode, deepDiveQnA) {
  const deepDiveArray = Array.isArray(deepDiveQnA) ? deepDiveQnA : [];
  const deepDiveQnAText = deepDiveArray.length > 0
    ? deepDiveArray.map((item, idx) =>
        `[질문 ${idx + 1} - ${item.category || '일반'}]\nQ: ${item.question}\nA: ${item.answer || '(답변 없음)'}`
      ).join('\n\n')
    : '(심화 질문에 답변하지 않음)';

  const answeredCount = deepDiveArray.filter(item => item.answer && item.answer.length > 0).length;
  const totalAnswerLength = deepDiveArray.reduce((sum, item) => sum + (item.answer || '').length, 0);

  // 모범 답안 (있다면)
  const modelPseudocode = problem?.pseudocode || problem?.model_pseudocode || '';
  const solutionCode = problem?.solution_code || '';

  const prompt = `당신은 알고리즘 및 의사코드 평가 전문가입니다.

## 문제 정보
- 제목: ${problem?.title || '알고리즘 문제'}
- 설명: ${problem?.description || ''}
${modelPseudocode ? `\n### 모범 의사코드 (참고용)\n${modelPseudocode}` : ''}
${solutionCode ? `\n### 정답 코드 (참고용)\n\`\`\`python\n${solutionCode}\n\`\`\`\n` : ''}

## 학생이 작성한 의사코드
${pseudocode}

## 심화 질문 및 답변 (${deepDiveArray.length}개 중 ${answeredCount}개 답변)
${deepDiveQnAText}

## 채점 규칙

### Pseudocode Score (50점 만점)
- **논리 정확성 (25점)**: 알고리즘이 문제를 올바르게 해결하는가?
- **구조 명확성 (15점)**: 단계별 흐름이 명확하고 이해하기 쉬운가?
- **완성도 (10점)**: 필요한 단계들이 모두 포함되어 있는가?

### Interview Score (50점 만점)
- **답변이 없거나 의미 없음**: 최대 10점
- **답변이 짧지만 개념적으로 타당 (30~100자)**: 최대 30점
- **핵심 개념은 맞으나 설명 부족**: 30~40점
- **구체적 설명 + 기술 용어 포함**: 40~45점
- **구체적 설명 + 트레이드오프/최적화 명시**: 45~50점

### 총점 계산
totalScore = pseudocodeScore + interviewScore (100점 만점)

## 출력 형식 (JSON만 출력!)
{
  "totalScore": 0,
  "grade": "excellent(80+)" | "good(60-79)" | "needs-improvement(40-59)" | "poor(0-39)",
  "summary": "총평 2-3문장",

  "pseudocodeEvaluation": {
    "score": 0,
    "details": [
      {"item": "논리 정확성", "score": 0, "basis": "평가 근거"},
      {"item": "구조 명확성", "score": 0, "basis": "평가 근거"},
      {"item": "완성도", "score": 0, "basis": "평가 근거"}
    ],
    "strengths": ["강점1", "강점2"],
    "weaknesses": ["약점1"]
  },

  "interviewEvaluation": {
    "score": 0,
    "answerAnalysis": {
      "length": ${totalAnswerLength},
      "hasKeyTerms": true/false,
      "keyTermsFound": ["발견된 기술 용어"],
      "keyTermsMissing": ["누락된 핵심 키워드"]
    },
    "questionAnalysis": [
      {
        "question": "실제 질문 내용",
        "category": "질문 카테고리",
        "userAnswer": "학생 답변",
        "modelAnswer": "모범 답안",
        "matchStatus": "match/partial/mismatch",
        "deductionReason": "감점 사유 (있으면)",
        "score": 0,
        "feedback": "피드백"
      }
    ]
  },

  "suggestions": ["학습 제안1", "제안2"]
}`;

  try {
    const response = await callOpenAI(prompt, { maxTokens: 2000, temperature: 0.3 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const result = JSON.parse(jsonMatch[0]);
      result.score = result.totalScore; // 호환성
      return result;
    }
    throw new Error('Invalid JSON response');
  } catch (error) {
    console.error('Evaluation error:', error);
    // Fallback 응답
    const fallbackQuestionAnalysis = deepDiveArray.map(item => ({
      question: item.question,
      category: item.category || '일반',
      userAnswer: item.answer || '',
      modelAnswer: '평가 오류',
      matchStatus: 'mismatch',
      deductionReason: '평가 오류',
      score: 0,
      feedback: '다시 시도해주세요.'
    }));

    return {
      totalScore: 30,
      score: 30,
      grade: 'poor',
      summary: '평가 중 오류가 발생했습니다.',
      pseudocodeEvaluation: {
        score: 15,
        details: [],
        strengths: [],
        weaknesses: ['평가 오류']
      },
      interviewEvaluation: {
        score: 15,
        answerAnalysis: { length: totalAnswerLength, hasKeyTerms: false, keyTermsFound: [], keyTermsMissing: [] },
        questionAnalysis: fallbackQuestionAnalysis
      },
      suggestions: ['다시 시도해주세요']
    };
  }
}
