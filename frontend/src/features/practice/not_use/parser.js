/**
 * [수정일: 2026-01-23]
 * [수정내용: JSON 문제 데이터의 assert 구문을 파싱하는 유틸리티 구현]
 * 
 * 백엔드에서 제공된 JSON 데이터의 'examples' 필드에 포함된 Python assert 문을 분석하여,
 * 프론트엔드 UI(Input/Output 테이블)에서 직관적으로 보여줄 수 있는 객체 형태로 변환합니다.
 * 예: assert remove_Occ("hello","l") == "heo" 
 *     -> { input: 'remove_Occ("hello","l")', output: '"heo"' }
 */
export const parseExample = (assertString) => {
    if (!assertString || !assertString.startsWith('assert')) {
        return { input: assertString, output: '' };
    }

    try {
        // 'assert ' 제거 후 '==' 기준으로 분리
        const content = assertString.replace('assert ', '');
        const parts = content.split('==');

        if (parts.length === 2) {
            return {
                input: parts[0].trim(),
                output: parts[1].trim()
            };
        }
    } catch (e) {
        console.error('Parsing error:', e);
    }

    return { input: assertString, output: '' };
};

export const parseAllExamples = (examples) => {
    return examples.map(ex => ({
        ...ex,
        parsed: parseExample(ex.output)
    }));
};
