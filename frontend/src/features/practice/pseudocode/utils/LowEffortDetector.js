/**
 * LowEffortDetector.js - 클라이언트 사전 검증 (신규)
 * 작성일: 2026-02-19
 *
 * 역할: 백엔드 호출 전 빠른 실패(fast-fail)용 최소 검증.
 *       백엔드(low_effort_detector.py)와 동일한 기준을 유지합니다.
 *
 * ⚠️ 주의: 최종 판정은 항상 백엔드가 합니다.
 *           여기서 통과해도 백엔드에서 is_low_effort=true가 올 수 있습니다.
 *           컴포넌트는 백엔드 응답의 is_low_effort 필드를 최우선으로 신뢰하세요.
 */

const MIN_LENGTH = 15;
const MIN_MEANINGFUL_WORDS = 3;

const GIVEUP_PATTERNS = [
    /^\s*(모르겠|몰라|모름)\s*$/,
    /^\s*(포기|패스|pass)\s*$/i,
    /^\s*(해줘|알려줘)\s*$/,
    /귀찮/,
    /나중에 할게|다음에 할게/,
    /\?{3,}/,
    /^[ㄱ-ㅎㅏ-ㅣ\s]+$/,  // 자음/모음만 (ㅁㄴㅇㄹ 등)
];

const REPETITION_RE = /(.)\1{4,}/;

/**
 * 무성의 입력 여부를 판단합니다.
 *
 * @param {string} text
 * @returns {{ valid: boolean, reason: string|null }}
 */
export function isMeaningfulInput(text) {
    if (!text || text.trim().length < MIN_LENGTH) {
        return {
            valid: false,
            reason: `설계가 너무 짧습니다. 최소 ${MIN_LENGTH}자 이상 작성해 주세요.`,
        };
    }

    const stripped = text.trim();

    for (const pattern of GIVEUP_PATTERNS) {
        if (pattern.test(stripped)) {
            return {
                valid: false,
                reason: '설계안을 작성하는 공간입니다. 모르는 부분은 추측이라도 작성해 보세요.',
            };
        }
    }

    // 반복 문자 감지
    if (REPETITION_RE.test(stripped.replace(/\s/g, ''))) {
        return {
            valid: false,
            reason: '의미 없는 문자 반복이 감지됐습니다. 정상적인 문장으로 작성해 주세요.',
        };
    }

    // 한글 없고 짧은 영문 단어만 있는 경우
    const hasKorean = /[가-힣]/.test(stripped);
    const wordCount = stripped.split(/\s+/).filter((w) => w.length > 1).length;
    if (!hasKorean && wordCount < MIN_MEANINGFUL_WORDS) {
        return {
            valid: false,
            reason: '자연어 설명이 부족합니다. 설계 의도를 한국어로 함께 작성해 주세요.',
        };
    }

    return { valid: true, reason: null };
}
