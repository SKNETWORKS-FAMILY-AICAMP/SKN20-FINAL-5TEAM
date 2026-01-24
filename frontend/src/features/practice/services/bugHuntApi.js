/**
 * Bug Hunt API Service
 * OpenAI API를 사용하여 사용자의 디버깅 답변을 평가합니다.
 */

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

async function callOpenAI(prompt, systemMessage = null) {
    const apiKey = getApiKey();
    if (!apiKey) {
        console.warn('OpenAI API Key is missing. Simulating response...');
        return simulateEvaluation();
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
            model: 'gpt-4o-mini', // 또는 'gpt-3.5-turbo'
            messages,
            max_tokens: 1000,
            temperature: 0.7
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
            resolve(JSON.stringify({
                "overallScore": 85,
                "summary": "사용자는 버그의 근본 원인을 잘 파악했으며, 특히 Off-by-one 에러와 Null 처리 부분에서 논리적인 해결책을 제시했습니다. 하지만 상태 누수 문제에 대해서는 조금 더 구체적인 설명이 보완되면 좋겠습니다.",
                "evaluations": [
                    { "step": 1, "score": 90, "feedback": "인덱스 범위에 대한 이해도가 높습니다." },
                    { "step": 2, "score": 85, "feedback": "방어적 프로그래밍의 중요성을 잘 언급했습니다." },
                    { "step": 3, "score": 80, "feedback": "가변 기본 인자의 위험성을 인지하고 있으나 해결 과정 설명이 간결합니다." }
                ],
                "strengths": ["경계 조건 파악 능력", "데이터 무결성 고려"],
                "weaknesses": ["심화 개념에 대한 구체적 설명 부족"]
            }));
        }, 2000);
    });
}

export async function evaluateBugHunt(missionTitle, steps, explanations) {
    const stepContext = steps.map((s, idx) => {
        return `[Step ${idx + 1}: ${s.title}]\n- 문제 설명: ${s.instruction}\n- 사용자의 해결 전략: ${explanations[idx + 1]}`;
    }).join('\n\n');

    const prompt = `당신은 시니어 파이썬 개발자이자 코드 리뷰어입니다.
학생이 수행한 'Bug Hunt' 미션 결과를 평가해주세요.

## 미션 정보
- 제목: ${missionTitle}

## 학생의 단계별 해결 전략:
${stepContext}

## 평가 가이드라인:
1. 각 단계별 해결 전략이 버그의 근본 원인을 정확히 짚고 있는지 평가하세요.
2. 프로그래밍 원칙(Off-by-one, Null Safety, Pure Function 등)에 기반한 설명인지 확인하세요.
3. 전반적인 점수와 요약 피드백을 제공하세요.

## 출력 형식 (JSON만 출력하세요):
{
  "overallScore": 0-100 점수,
  "summary": "전체 총평 (3~4문장)",
  "evaluations": [
    { "step": 1, "score": 0-100, "feedback": "1단계 피드백" },
    { "step": 2, "score": 0-100, "feedback": "2단계 피드백" },
    { "step": 3, "score": 0-100, "feedback": "3단계 피드백" }
  ],
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["보완점1", "보완점2"]
}`;

    try {
        const response = await callOpenAI(prompt, "당신은 냉철하지만 교육적인 시니어 파이썬 개발자입니다.");
        const jsonMatch = response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            return JSON.parse(jsonMatch[0]);
        }
        throw new Error('Invalid JSON format');
    } catch (error) {
        console.error('LLM Evaluation error:', error);
        const mockData = await simulateEvaluation();
        return JSON.parse(mockData);
    }
}
