/**
 * Bug Hunt API Service
 * OpenAI API를 사용하여 사용자의 디버깅 사고를 평가합니다.
 */

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

async function callOpenAI(prompt, systemMessage = null) {
    const apiKey = getApiKey();
    if (!apiKey) {
        console.warn('OpenAI API Key is missing. Simulating response...');
        return null;
    }

    const messages = [];
    if (systemMessage) {
        messages.push({ role: 'system', content: systemMessage });
    }
    messages.push({ role: 'user', content: prompt });

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            model: 'gpt-4o-mini',
            messages,
            max_tokens: 1500,
            temperature: 0.3
        })
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }

    const data = await response.json();
    return data.choices[0].message.content.trim();
}

function simulateEvaluation() {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                thinking_pass: true,
                code_risk: 25,
                thinking_score: 78,
                총평: "버그의 원인을 정확히 파악하고 적절한 범위 내에서 수정했으나, 일부 설명에서 논리적 근거가 부족합니다."
            });
        }, 2000);
    });
}

/**
 * 디버깅 사고 평가 함수
 * @param {string} missionTitle - 미션 제목
 * @param {Array} steps - 각 단계 정보 (buggy_code, instruction 등)
 * @param {Object} explanations - 각 단계별 사용자 설명 {1: '...', 2: '...', 3: '...'}
 * @param {Object} userCodes - 각 단계별 사용자 수정 코드 {1: '...', 2: '...', 3: '...'}
 * @returns {Object} 평가 결과 {thinking_pass, code_risk, thinking_score, 총평}
 */
export async function evaluateBugHunt(missionTitle, steps, explanations, userCodes) {
    // 각 단계별 데이터 구성
    const stepContext = steps.map((s, idx) => {
        const stepNum = idx + 1;
        const originalCode = s.buggy_code || '';
        const modifiedCode = userCodes[stepNum] || '';
        const explanation = explanations[stepNum] || '설명 없음';

        return `### Step ${stepNum}: ${s.title || s.bug_type}
- 문제 설명: ${s.instruction}

- 원본 버그 코드:
\`\`\`python
${originalCode}
\`\`\`

- 사용자 수정 코드:
\`\`\`python
${modifiedCode}
\`\`\`

- 사용자 설명: ${explanation}`;
    }).join('\n\n');

    const systemMessage = `너는 디버깅 사고를 평가하는 시스템이다.
정오답이 아니라 "디버깅 사고의 질"을 평가한다.
냉철하고 객관적으로 평가하되, 교육적인 관점을 유지한다.`;

    const prompt = `## 평가 대상 데이터

미션: ${missionTitle}

${stepContext}

## 평가 단계

1. 사고 방향 평가 (모델 A 관점)
   다음 항목들을 검토한다:
   - 원인 언급 여부: 사용자가 버그의 근본 원인을 언급했는가?
   - 원인-수정 일치 여부: 언급한 원인과 실제 코드 수정이 일치하는가?
   - 부작용 고려 여부: 수정으로 인한 부작용을 고려했는가?
   - 수정 범위 적절성: 필요한 부분만 수정했는가, 과도하게 수정했는가?
   - 설명-코드 일관성: 설명 내용과 실제 코드 변경이 일관되는가?
   → 주요 항목(원인 언급, 원인-수정 일치, 설명-코드 일관성) 충족 시 통과

2. 코드 위험 평가 (모델 B 관점)
   다음 요소를 분석한다:
   - 변경 라인 수: 얼마나 많은 코드를 변경했는가?
   - 조건문/예외 처리 변화: 로직 흐름에 영향을 주는 변경이 있는가?
   - 기존 로직 훼손 여부: 원래 동작해야 할 부분을 망가뜨렸는가?
   → 위험 점수 0~100 (0: 매우 안전, 100: 매우 위험)

3. 사고 연속 점수 평가 (모델 C 관점)
   좋은 디버깅 답변의 특성과 비교한다:
   - 논리적 흐름: 문제 인식 → 원인 분석 → 해결책 제시 순서
   - 근거 제시: 왜 그렇게 수정했는지 이유를 설명했는가?
   - 명확성: 설명이 명확하고 이해하기 쉬운가?
   - 기술적 정확성: 사용한 용어와 개념이 정확한가?
   → 사고 점수 0~100

## 출력 형식
반드시 아래 JSON 형식만 출력하라. 다른 텍스트는 포함하지 마라.

{
  "thinking_pass": true 또는 false,
  "code_risk": 0에서 100 사이의 숫자,
  "thinking_score": 0에서 100 사이의 숫자,
  "총평": "전체 평가를 요약한 한 문장"
}`;

    try {
        const response = await callOpenAI(prompt, systemMessage);

        if (!response) {
            // API 키가 없는 경우 시뮬레이션
            return await simulateEvaluation();
        }

        const jsonMatch = response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            const result = JSON.parse(jsonMatch[0]);
            // 필수 필드 검증
            return {
                thinking_pass: Boolean(result.thinking_pass),
                code_risk: Number(result.code_risk) || 50,
                thinking_score: Number(result.thinking_score) || 50,
                총평: result.총평 || result.summary || '평가를 완료했습니다.'
            };
        }
        throw new Error('Invalid JSON format');
    } catch (error) {
        console.error('LLM Evaluation error:', error);
        return await simulateEvaluation();
    }
}
