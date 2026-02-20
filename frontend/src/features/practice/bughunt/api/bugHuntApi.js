/**
 * Bug Hunt API Service
 * 백엔드를 통해 OpenAI API로 사용자의 디버깅 사고를 평가합니다.
 *
 * [수정일: 2026-02-06]
 * [수정내용: 행동 기반 검증 API 추가 (Docker 샌드박스)]
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/core';

/**
 * 행동 기반 코드 검증 함수
 * Docker 샌드박스에서 실제 코드를 실행하여 검증합니다.
 *
 * @param {string} userCode - 사용자가 수정한 코드
 * @param {string} verificationCode - 검증용 코드 (문제에서 제공)
 * @param {string} problemId - 문제 ID (로깅용)
 * @returns {Object} 검증 결과 {verified, message, details, execution_time}
 */
export async function verifyCodeBehavior(userCode, verificationCode, problemId = '') {
    try {
        console.log('🔬 행동 기반 검증 시작:', problemId);

        const response = await fetch(`${API_BASE_URL}/verify-behavior/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_code: userCode,
                verification_code: verificationCode,
                problem_id: problemId,
                image: 'pytorch'  // PyTorch 이미지 사용
            })
        });

        console.log('📡 검증 응답 상태:', response.status);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Verification Error: ${response.status}`);
        }

        const result = await response.json();
        console.log('🔬 검증 결과:', result);

        return {
            verified: Boolean(result.verified),
            message: result.message || '',
            details: result.details || {},
            execution_time: result.execution_time || 0
        };

    } catch (error) {
        console.error('❌ 행동 기반 검증 실패:', error);

        // Docker 미설치 등의 경우 문자열 검증으로 폴백
        return {
            verified: null,  // null = 검증 불가 (폴백 필요)
            message: error.message,
            details: { fallback: true },
            execution_time: 0
        };
    }
}

/**
 * 디버깅 사고 평가 함수
 * Step별 딥다이브 면접 결과를 종합하여 최종 평가를 생성합니다.
 *
 * @param {string} missionTitle - 미션 제목
 * @param {Array} steps - 각 단계 정보 (buggy_code, instruction 등)
 * @param {Object} explanations - 각 단계별 사용자 설명 {1: '...', 2: '...', 3: '...'}
 * @param {Object} userCodes - 각 단계별 사용자 수정 코드 {1: '...', 2: '...', 3: '...'}
 * @param {Object} performance - 풀이 성과 지표 (오답 횟수 등)
 * @param {Object} interviewResults - 각 단계별 면접 결과 {1: {score, understanding_level, ...}, ...}
 * @returns {Object} 평가 결과 {thinking_pass, code_risk, thinking_score, 총평, step_feedbacks}
 */
export async function evaluateBugHunt(missionTitle, steps, explanations, userCodes, performance = {}, interviewResults = {}) {
    try {
        console.log('🚀 API 호출 시작:', API_BASE_URL);
        const response = await fetch(`${API_BASE_URL}/ai-bughunt-evaluate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                missionTitle,
                steps,
                explanations,
                userCodes,
                performance,
                interviewResults
            })
        });

        console.log('📡 응답 상태:', response.status);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `API Error: ${response.status}`);
        }

        const result = await response.json();
        console.log('📦 API 응답 데이터:', result);
        console.log('📋 Step Feedbacks 있음?', result.step_feedbacks);

        return {
            thinking_pass: Boolean(result.thinking_pass),
            code_risk: Number(result.code_risk) || 50,
            thinking_score: Number(result.thinking_score) || 50,
            총평: result.총평 || result.summary || '평가를 완료했습니다.',
            step_feedbacks: result.step_feedbacks || []  // ✅ 추가!
        };

    } catch (error) {
        console.error('❌ Bug Hunt Evaluation error:', error);

        // 에러 시 시뮬레이션 결과 반환
        return {
            thinking_pass: false,
            code_risk: 50,
            thinking_score: 50,
            총평: "서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.",
            step_feedbacks: []  // ✅ 추가!
        };
    }
}

/**
 * 딥다이브 면접 API 호출
 * Step별로 LLM 면접관과 대화한다.
 *
 * @param {Object} stepContext - 현재 Step 정보 (buggy_code, user_code, error_info, coaching, interview_rubric)
 * @param {Array} conversation - 대화 내역 [{role, content}, ...]
 * @param {number} turn - 현재 턴 번호 (1부터 시작)
 * @param {string} candidateName - 유저 호출명
 * @returns {Object} {type: 'question'|'evaluation', message, ...}
 */
export async function interviewBugHunt(stepContext, conversation, turn, candidateName = '') {
    try {
        const response = await fetch(`${API_BASE_URL}/ai-bughunt-interview/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                step_context: stepContext,
                conversation,
                turn,
                candidate_name: candidateName
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Interview API Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Interview API error:', error);
        return {
            type: 'evaluation',
            message: '면접 서버 연결에 실패했습니다. 점수는 코드 수정 결과로 대체됩니다.',
            score: 50,
            understanding_level: 'Unknown',
            matched_concepts: [],
            weak_point: null
        };
    }
}

/**
 * 딥다이브 면접 스트리밍 API 호출
 * 질문 턴에서 LLM 응답을 토큰 단위로 수신합니다.
 *
 * @param {Object} stepContext
 * @param {Array} conversation
 * @param {number} turn
 * @param {string} candidateName
 * @param {(token: string) => void} onToken
 */
export async function interviewBugHuntStream(stepContext, conversation, turn, candidateName = '', onToken = () => {}) {
    const response = await fetch(`${API_BASE_URL}/ai-bughunt-interview/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            step_context: stepContext,
            conversation,
            turn,
            candidate_name: candidateName,
            stream: true
        })
    });

    if (!response.ok || !response.body) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Interview Stream Error: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        let boundary = buffer.indexOf('\n\n');
        while (boundary !== -1) {
            const eventChunk = buffer.slice(0, boundary).trim();
            buffer = buffer.slice(boundary + 2);

            if (eventChunk.startsWith('data:')) {
                const payload = eventChunk
                    .split('\n')
                    .filter((line) => line.startsWith('data:'))
                    .map((line) => line.slice(5).trim())
                    .join('');

                if (payload === '[DONE]') {
                    return;
                }

                try {
                    const parsed = JSON.parse(payload);
                    if (parsed.token) {
                        onToken(parsed.token);
                    } else if (parsed.error) {
                        throw new Error(parsed.error);
                    }
                } catch (e) {
                    // JSON 파싱 실패 시 무시
                }
            }
            boundary = buffer.indexOf('\n\n');
        }
    }
}
