/**
 * useEvaluationOrchestrator.js - 평가 흐름 제어 (신규)
 * 작성일: 2026-02-19
 *
 * 역할: pseudocodeApi.js(HTTP) + 에러 처리 + 응답 정규화를 조합해
 *       컴포넌트에서 사용하기 쉬운 단일 evaluate() 함수를 제공합니다.
 *
 * 컴포넌트에서 사용법:
 *   import { useEvaluationOrchestrator } from './useEvaluationOrchestrator.js';
 *   const { evaluate, isLoading, errorType } = useEvaluationOrchestrator();
 *   const result = await evaluate(problem, pseudocode);
 */

import { ref } from 'vue';
import { requestEvaluation } from '../api/pseudocodeApi.js';

// ── 에러 타입 상수 ────────────────────────────────────────────────
export const EvaluationErrorType = {
    LOW_EFFORT: 'LOW_EFFORT',      // 무성의 입력 (백엔드 판정)
    AI_TIMEOUT: 'AI_TIMEOUT',      // LLM 타임아웃
    SERVER_ERROR: 'SERVER_ERROR',  // 서버 오류
    NETWORK_ERROR: 'NETWORK_ERROR',// 네트워크 단절
};

export function useEvaluationOrchestrator() {
    const isLoading = ref(false);
    const errorType = ref(null);
    const errorMessage = ref('');

    /**
     * 의사코드 평가 실행.
     */
    async function evaluate(problem, pseudocode, tailAnswer = '', deepAnswer = '') {
        errorType.value = null;
        errorMessage.value = '';
        isLoading.value = true;

        try {
            // [2026-02-21] 클라이언트 사전 검증 제거 -> 백엔드에서 통합 처리

            // ── Step 2: 백엔드 평가 요청 ────────────────
            const response = await requestEvaluation(
                problem.id,
                problem.title || problem.missionObjective || '미션',
                pseudocode,
                tailAnswer,
                deepAnswer,
            );
            const data = response.data;

            // ── Step 3: 서버가 low_effort로 판정한 경우 ───────────────
            if (data.is_low_effort) {
                errorType.value = EvaluationErrorType.LOW_EFFORT;
                errorMessage.value = data.one_line_review || '설계가 부실합니다.';
                return _normalizeResult(data);
            }

            // ── Step 4: 정상 결과 정규화 ──────────────────────────────
            return _normalizeResult(data);

        } catch (err) {
            return _handleError(err);
        } finally {
            isLoading.value = false;
        }
    }

    /**
     * 에러 처리 — HTTP 상태 코드 기반으로 errorType 설정
     */
    function _handleError(err) {
        const httpStatus = err?.response?.status;
        const serverError = err?.response?.data?.error;

        if (!httpStatus) {
            // 네트워크 연결 안 됨
            errorType.value = EvaluationErrorType.NETWORK_ERROR;
            errorMessage.value = '네트워크 연결을 확인해 주세요.';
            return null;
        }

        if (httpStatus === 503) {
            if (serverError === 'AI_TIMEOUT') {
                errorType.value = EvaluationErrorType.AI_TIMEOUT;
                errorMessage.value = 'AI 응답 시간이 초과됐습니다. 잠시 후 다시 시도해 주세요.';
            } else {
                errorType.value = EvaluationErrorType.SERVER_ERROR;
                errorMessage.value = 'AI 서비스에 일시적인 문제가 있습니다.';
            }
            return null;
        }

        // 500 or 기타
        errorType.value = EvaluationErrorType.SERVER_ERROR;
        errorMessage.value = '서버 오류가 발생했습니다. 문제가 지속되면 관리자에게 문의해 주세요.';
        console.error('[EvaluationOrchestrator] Server error:', err?.response?.data);
        return null;
    }

    return {
        evaluate,
        isLoading,
        errorType,
        errorMessage,
    };
}

// ── 응답 정규화 ───────────────────────────────────────────────────────────

/**
 * 백엔드 응답 → UI 모델로 변환.
 * 컴포넌트는 이 형태만 사용하면 됩니다.
 */
function _normalizeResult(data) {
    // senior_advice: GPT가 생성한 맞춤 코멘트 — 빈 값이면 one_line_review fallback
    const seniorAdvice = (data.senior_advice || data.one_line_review || '').trim();
    return {
        score: data.total_score_100 ?? data.overall_score ?? 0,
        grade: data.grade ?? 'POOR',
        persona: data.persona_name ?? '아키텍트',
        oneLineReview: data.one_line_review ?? '',
        seniorAdvice,
        dimensions: data.dimensions ?? {},
        convertedPython: data.converted_python ?? '',
        pythonFeedback: data.python_feedback ?? '',
        strengths: data.strengths ?? [],
        weaknesses: data.weaknesses ?? [],
        isLowEffort: data.is_low_effort ?? false,
        tailQuestion: data.tail_question ?? null,
        deepDive: data.deep_dive ?? null,
        scoreBreakdown: data.score_breakdown ?? {},
        metadata: data.metadata ?? {},
        // 백엔드에서 제공한 영상 큐레이션 (없으면 프론트 폴백)
        recommendedVideos: data.recommended_videos ?? [],
        llmAvailable: data.llm_available ?? true,
    };
}

function _buildLowEffortResult(reason) {
    return _normalizeResult({
        total_score_100: 0,
        grade: 'POOR',
        persona_name: '성장의 씨앗을 품은 학생',
        one_line_review: reason,
        is_low_effort: true,
        dimensions: {},
        strengths: [],
        weaknesses: [reason],
    });
}
