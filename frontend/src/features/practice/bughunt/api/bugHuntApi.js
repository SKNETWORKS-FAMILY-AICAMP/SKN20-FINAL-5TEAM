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
 * @param {string} missionTitle - 미션 제목
 * @param {Array} steps - 각 단계 정보 (buggy_code, instruction 등)
 * @param {Object} explanations - 각 단계별 사용자 설명 {1: '...', 2: '...', 3: '...'}
 * @param {Object} userCodes - 각 단계별 사용자 수정 코드 {1: '...', 2: '...', 3: '...'}
 * @param {Object} performance - 풀이 성과 지표 (오답 횟수 등)
 * @returns {Object} 평가 결과 {thinking_pass, code_risk, thinking_score, 총평, step_feedbacks}
 */
export async function evaluateBugHunt(missionTitle, steps, explanations, userCodes, performance = {}) {
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
                performance
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
