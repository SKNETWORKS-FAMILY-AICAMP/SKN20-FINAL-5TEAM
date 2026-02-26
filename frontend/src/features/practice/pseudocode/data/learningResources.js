/**
 * learningResources.js - 의사코드 학습 리소스 관리 (Backend-Driven)
 * 수정일: 2026-02-21
 *
 * [변경 사항]
 * - 수동 하드코딩 데이터를 대폭 삭제 (Source of Truth를 백엔드로 일원화)
 * - 백엔드 API 응답(evaluation-5d)의 recommended_videos를 우선하도록 설계됨
 * - 백엔드 통신 실패 시를 대비한 최소한의 폴백 데이터만 유지
 */

// 로컬 폴백용 최소 데이터 (백엔드 통신 실패 시 대비용)
const FALLBACK_VIDEOS = {
    'default': [
        {
            id: 'A88rDEf-pfk',
            videoId: 'A88rDEf-pfk',
            title: 'Machine Learning Fundamentals',
            channelTitle: 'StatQuest',
            thumbnail: 'https://img.youtube.com/vi/A88rDEf-pfk/mqdefault.jpg',
            url: 'https://www.youtube.com/watch?v=A88rDEf-pfk',
            description: '머신러닝의 기초 개념을 설명합니다.'
        }
    ]
};

/**
 * 추천 영상을 가져옵니다. 
 * 이제 백엔드 결과(evaluationResult.recommended_videos)를 우선적으로 사용해야 하므로, 
 * 이 함수는 백엔드 데이터가 없을 때의 최소 폴백 역할만 수행합니다.
 * @param {number|string} questId 
 * @param {Object} dimensions 
 * @param {number} maxCount 
 * @returns {Array} 
 */
export function getRecommendedVideos(questId, dimensions = {}, maxCount = 3) {
    console.log('[YouTube] 프론트엔드 폴백 큐레이션 호출 - Quest:', questId);
    return FALLBACK_VIDEOS.default;
}

/**
 * 학습 사유 반환 (백엔드 피드백 보조용)
 */
export function getLearningReason(questId, dimension) {
    return '해당 분야의 심화 학습이 권장됩니다.';
}
