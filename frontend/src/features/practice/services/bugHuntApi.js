/**
 * Bug Hunt API Service
 * 백엔드를 통해 OpenAI API로 사용자의 디버깅 사고를 평가합니다.
 *
 * [수정일: 2026-01-27]
 * [수정내용: 프론트엔드 직접 API 호출 → 백엔드 API 호출로 변경 (보안 강화)]
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/core';

/**
 * 디버깅 사고 평가 함수
 * @param {string} missionTitle - 미션 제목
 * @param {Array} steps - 각 단계 정보 (buggy_code, instruction 등)
 * @param {Object} explanations - 각 단계별 사용자 설명 {1: '...', 2: '...', 3: '...'}
 * @param {Object} userCodes - 각 단계별 사용자 수정 코드 {1: '...', 2: '...', 3: '...'}
 * @returns {Object} 평가 결과 {thinking_pass, code_risk, thinking_score, 총평}
 */
export async function evaluateBugHunt(missionTitle, steps, explanations, userCodes) {
    try {
        const response = await fetch(`${API_BASE_URL}/ai-bughunt-evaluate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                missionTitle,
                steps,
                explanations,
                userCodes
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `API Error: ${response.status}`);
        }

        const result = await response.json();

        return {
            thinking_pass: Boolean(result.thinking_pass),
            code_risk: Number(result.code_risk) || 50,
            thinking_score: Number(result.thinking_score) || 50,
            총평: result.총평 || result.summary || '평가를 완료했습니다.'
        };

    } catch (error) {
        console.error('Bug Hunt Evaluation error:', error);

        // 에러 시 시뮬레이션 결과 반환
        return {
            thinking_pass: false,
            code_risk: 50,
            thinking_score: 50,
            총평: "서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요."
        };
    }
}
