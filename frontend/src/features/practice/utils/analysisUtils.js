/**
 * 수정일: 2026-01-29
 * 내용: 한글 주관식 채점 고도화를 위한 전처리 및 정규화 유틸리티
 */

/**
 * [수정일: 2026-01-29] 시맨틱 매칭을 위한 동의어 사전 구축
 * 핵심 개념별로 일반 용어와 기술 용어(영어 포함)를 그룹핑합니다.
 */
const SYNONYM_MAP = {
    "중복": ["중복", "duplicate", "redundant", "redundancy", "overlap"],
    "제거": ["제거", "삭제", "지우기", "clear", "remove", "delete", "erase", "cleanup", "pop", "discard"],
    "검사": ["검사", "확인", "체크", "check", "inspect", "validate", "find", "검증", "verification", "scan"],
    "비교": ["비교", "대조", "compare", "match", "대조", "상대", "대치"],
    "반복": ["반복", "순회", "loop", "iterate", "for", "while", "traverse", "mapping"],
    "하나씩": ["하나씩", "각각", "순차", "each", "stepbystep", "sequentially"],
    "순서": ["순서", "정렬", "order", "sequence", "sort", "sorting", "인덱스", "index"],
    "유지": ["유지", "보존", "keep", "preserve", "persist", "save", "store"],
    "비": ["비", "강수", "날씨", "weather", "rain", "precipitation", "강수량", "강우"],
    "미끄러움": ["미끄러움", "마찰", "slippery", "friction", "slip", "coefficient"],
    "우선": ["우선", "가중치", "중요도", "priority", "weight", "importance", "bias", "threshold"],
    "거리": ["거리", "최단", "distance", "range", "length", "path", "route"],
    "최소": ["최소", "가장작은", "min", "minimum", "smallest", "bottom"],
    "정렬": ["정렬", "순서대로", "sort", "arrange", "ordering", "indexing"],
    "최대": ["최대", "가장큰", "max", "maximum", "largest", "top"],
    "효율": ["효율", "최적", "efficiency", "optimal", "performance", "optimization"],
    "비율": ["비율", "비중", "ratio", "proportion", "scale", "percentage"],
    "가중치": ["가중치", "우선순위", "weight", "bias", "priority", "threshold", "scale"],
    "만약": ["만약", "if", "조건", "경우", "case", "when", "상태", "state", "predicate", "조건문", "분기"],
    "출력": ["출력", "반환", "print", "return", "output", "log", "display", "show"]
};

/**
 * 키워드의 동의어 그룹을 찾아 모두 포함되어 있는지 확인합니다.
 * @param {string} source 사용자 입력
 * @param {string} keyword 기준 키워드
 * @returns {boolean} 동의어 중 하나라도 매칭되면 true
 */
export const semanticMatch = (source, keyword) => {
    if (!source || !keyword) return false;

    const src = normalizeKorean(source);

    // 1. 기준 키워드 자체가 포함되어 있는지 확인
    const kw = normalizeKorean(keyword);
    if (src.includes(kw)) return true;

    // 2. 동의어 사전 검색
    for (const group in SYNONYM_MAP) {
        if (group === keyword || SYNONYM_MAP[group].includes(keyword)) {
            // 해당 그룹의 단어 중 하나라도 사용자 입력에 있는지 확인
            const matchFound = SYNONYM_MAP[group].some(synonym => {
                const normalizedSynonym = normalizeKorean(synonym);
                return src.includes(normalizedSynonym);
            });
            if (matchFound) return true;
        }
    }

    return false;
};

// [Lion's Code Snippet] [수정일: 2026-01-29] 성능 및 정확도 향상을 위한 조사 제거 로직 최적화
const PARTICLES = ['은', '는', '이', '가', '을', '를', '의', '로', '에', '서', '한', '하'];
// 파이프(|)로 연결하여 한 번에 매칭 (Performance Up)
const PARTICLE_REGEX = new RegExp(`(${PARTICLES.join('|')})$`, 'i');

/**
 * 한글 조사 및 어미를 제거/정규화하여 핵심 키워드를 추출하기 쉽게 만듭니다.
 * @param {string} text 원문 텍스트
 * @returns {string} 정규화된 텍스트
 */
export const normalizeKorean = (text) => {
    if (!text) return '';

    // 1. 기본 정제
    let normalized = text.toLowerCase().trim()
        .replace(/[\s\t\n\r]/g, '')
        .replace(/[.,!?;:()[\]{}'"]/g, '');

    // 2. 조사 제거 (단, 길이가 2글자 이상일 때만 제거하여 '사(Apple)', '비(Rain)' 같은 외자 단어 보호)
    if (normalized.length > 1) {
        normalized = normalized.replace(PARTICLE_REGEX, '');
    }

    return normalized;
};

/**
 * 유연한 키워드 매칭 (Fuzzy Match 대용)
 * @param {string} source 사용자 입력
 * @param {string} keyword 찾고자 하는 키워드
 * @returns {boolean} 일치 여부
 */
export const flexibleMatch = (source, keyword) => {
    if (!source || !keyword) return false;

    const src = source.toLowerCase().replace(/\s/g, '');
    const kw = keyword.toLowerCase().replace(/\s/g, '');

    // 1. 단순 포함 확인
    if (src.includes(kw)) return true;

    // 2. 조사 무시 매칭 (키워드가 조사 없이 입력되었을 때 사용자의 "키워드+조사" 형태를 매칭)
    // 예: keyword "중복", source "중복을" -> true
    if (src.includes(kw)) return true;

    // 3. 한글 키워드의 경우 '어근' 매칭 시도 (간단한 규칙)
    // 예: "제거" -> "제거해", "제거함" 등
    if (src.indexOf(kw) !== -1) return true;

    return false;
};
