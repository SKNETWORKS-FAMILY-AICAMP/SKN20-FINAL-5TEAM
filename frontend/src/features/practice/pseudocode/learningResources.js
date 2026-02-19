/**
 * learningResources.js - 큐레이션 학습 리소스 (단순화)
 * 수정일: 2026-02-19
 *
 * [변경 사항]
 * - YouTube API 엔드포인트 제거 (pseudocodeApi.js의 getYouTubeRecommendations 제거됨)
 * - 하드코딩 큐레이션으로 단순화 (항상 같은 영상이 나오던 것을 솔직하게 유지)
 * - 차원별로 2~3개씩 엄선된 영상 목록 관리
 * - getRecommendedVideos() 함수 하나로 외부에 노출
 *
 * 영상 추가/교체: 이 파일의 CURATED_VIDEOS 객체만 편집하면 됩니다.
 */

// ── 차원별 큐레이션 영상 ────────────────────────────────────────────────────
// 각 차원에 2~3개 제한. 검증된 영상만 등록하세요.

const CURATED_VIDEOS = {
    consistency: [
        {
            id: 'fSytzGwwBVw',
            title: 'Cross Validation Explained (StatQuest)',
            desc: '교차 검증의 핵심 원리. 데이터 누수를 방지하는 올바른 분할 전략의 기초입니다.',
            reason: '데이터 분할과 검증 전략의 기본기를 점검해 보세요.',
        },
        {
            id: 'A88rDEf-pfk',
            title: 'Standardization vs Normalization (StatQuest)',
            desc: '데이터 표준화의 개념과 올바른 적용 시점. fit/transform 순서가 왜 중요한지 이해할 수 있습니다.',
            reason: '전처리 파이프라인에서 fit/transform 순서와 데이터 누수 방지 원리를 확인하세요.',
        },
    ],
    design: [
        {
            id: 'TMuno5RZNeE',
            title: 'SOLID Principles (Uncle Bob)',
            desc: '객체지향 설계의 5대 원칙. 컴포넌트 간 책임 분리(SoC)의 기초입니다.',
            reason: '전체적인 파이프라인 설계 구조를 개선해 보세요.',
        },
    ],
    abstraction: [
        {
            id: 'pTB0EiLXUC8',
            title: 'OOP & Abstraction (Programming with Mosh)',
            desc: '추상화 개념을 쉽고 명확하게 설명합니다.',
            reason: '하드코딩된 로직을 일반화하여 확장성을 높여 보세요.',
        },
    ],
    edge_case: [
        {
            id: 'ZUqGMDppEDs',
            title: 'Python Exception Handling (NeuralNine)',
            desc: 'try/except를 활용한 방어적 코딩 전략.',
            reason: '에지 케이스 및 비정상 데이터에 대한 방어 로직이 부족합니다.',
        },
    ],
    implementation: [
        {
            id: 'EuBBz3bI-aA',
            title: 'Bias and Variance (StatQuest)',
            desc: '편향-분산 트레이드오프. 모델 일반화와 구현 전략 이해의 기초.',
            reason: '모델 구현 수준과 일반화 성능을 함께 고려해 보세요.',
        },
    ],
};

// ── 외부 노출 함수 ────────────────────────────────────────────────────────

/**
 * 취약 차원 기반으로 추천 영상을 반환합니다.
 *
 * @param {Object} dimensions - 평가 결과의 dimensions 객체
 *                              { design: {score, max}, consistency: {score, max}, ... }
 * @param {number} maxCount   - 최대 반환 개수 (기본 2)
 * @returns {Array}           - 추천 영상 배열
 */
export function getRecommendedVideos(dimensions = {}, maxCount = 2) {
    const DIMENSION_ORDER = ['consistency', 'design', 'abstraction', 'edge_case', 'implementation'];

    // camelCase → snake_case 키 매핑 (reportGenerator의 edgeCase → edge_case)
    const ALIAS = { edgeCase: 'edge_case' };
    const normalized = {};
    for (const [k, v] of Object.entries(dimensions)) {
        normalized[ALIAS[k] || k] = v;
    }

    // 점수 비율 기준으로 취약한 차원 정렬
    const sorted = DIMENSION_ORDER
        .map((dim) => {
            const d = normalized[dim];
            if (!d) return { dim, ratio: 1 };
            // percentage가 있으면 우선 사용, 없으면 score/max 비율
            const ratio = d.percentage != null ? d.percentage / 100 : (d.max > 0 ? d.score / d.max : 1);
            return { dim, ratio };
        })
        .sort((a, b) => a.ratio - b.ratio);

    const result = [];
    const usedIds = new Set();

    for (const { dim } of sorted) {
        if (result.length >= maxCount) break;
        const pool = CURATED_VIDEOS[dim] || [];
        for (const video of pool) {
            if (result.length >= maxCount) break;
            if (!usedIds.has(video.id)) {
                result.push(video);
                usedIds.add(video.id);
            }
        }
    }

    // 추천이 없으면 consistency 기본값 반환
    if (result.length === 0) {
        return CURATED_VIDEOS.consistency.slice(0, maxCount);
    }

    return result;
}
