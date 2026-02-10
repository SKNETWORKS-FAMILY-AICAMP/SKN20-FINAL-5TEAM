/**
 * JSON 파싱 유틸리티
 * 
 * 문제: AI가 마크다운, 서술형 텍스트, 여러 JSON 블록을 포함할 수 있음
 * 해결: 정규식으로 유효한 JSON만 추출 + 복수 시도
 * 
 * [2026-02-09] 안정성 개선 (Antigravity)
 */

/**
 * AI 응답에서 JSON 블록 안전하게 추출
 * 
 * 처리 순서:
 * 1. 마크다운 코드 블록 (```json...```) 제거
 * 2. 중괄호 기반 JSON 블록 추출
 * 3. 배열 형태 JSON 추출 (fallback)
 * 4. 모든 시도 실패 시 구조화된 에러 반환
 * 
 * @param {string} text - AI 응답 텍스트
 * @param {object} fallback - 파싱 실패 시 반환할 기본값
 * @returns {object} 파싱된 JSON 또는 fallback
 */
export function safeJSONParse(text, fallback = null) {
    if (!text || typeof text !== 'string') {
        console.warn('[safeJSONParse] Invalid input:', typeof text);
        return fallback;
    }

    // 시도 1: 마크다운 코드 블록 제거 후 파싱
    try {
        const cleanedText = text
            .replace(/```json\s*/gi, '')
            .replace(/```\s*/g, '')
            .trim();
        
        return JSON.parse(cleanedText);
    } catch (e) {
        // 계속 진행
    }

    // 시도 2: 첫 번째 {...} 블록 추출
    try {
        const objectMatch = text.match(/\{(?:[^{}]|(?:\{[^{}]*\}))*\}/);
        if (objectMatch) {
            return JSON.parse(objectMatch[0]);
        }
    } catch (e) {
        console.warn('[safeJSONParse] Object extraction failed:', e.message);
    }

    // 시도 3: 첫 번째 [...] 배열 추출
    try {
        const arrayMatch = text.match(/\[[\s\S]*?\]/);
        if (arrayMatch) {
            return JSON.parse(arrayMatch[0]);
        }
    } catch (e) {
        console.warn('[safeJSONParse] Array extraction failed:', e.message);
    }

    // 시도 4: 중첩된 JSON 추출 (더 공격적)
    try {
        // 가장 긴 {...} 블록 찾기 (중첩 지원)
        let maxLength = 0;
        let bestMatch = null;
        
        const matches = text.matchAll(/\{/g);
        for (const match of matches) {
            const startIdx = match.index;
            let depth = 1;
            let endIdx = startIdx + 1;
            
            while (depth > 0 && endIdx < text.length) {
                if (text[endIdx] === '{') depth++;
                if (text[endIdx] === '}') depth--;
                endIdx++;
            }
            
            if (depth === 0) {
                const candidate = text.substring(startIdx, endIdx);
                if (candidate.length > maxLength) {
                    try {
                        JSON.parse(candidate); // 유효성 검사
                        maxLength = candidate.length;
                        bestMatch = candidate;
                    } catch (e) {
                        // 유효하지 않으면 스킵
                    }
                }
            }
        }
        
        if (bestMatch) {
            return JSON.parse(bestMatch);
        }
    } catch (e) {
        console.warn('[safeJSONParse] Deep extraction failed:', e.message);
    }

    // 모든 시도 실패
    console.error('[safeJSONParse] All attempts failed. Original text:', text.substring(0, 200));
    return fallback;
}

/**
 * AI 응답에서 특정 필드 추출 (더 관대한 파싱)
 * 
 * @param {string} text - AI 응답
 * @param {string} field - 추출할 필드명
 * @param {any} defaultValue - 기본값
 * @returns {any} 추출된 값 또는 기본값
 */
export function extractField(text, field, defaultValue = null) {
    try {
        const parsed = safeJSONParse(text, null);
        if (parsed && typeof parsed === 'object' && field in parsed) {
            return parsed[field];
        }
    } catch (e) {
        // Fallback to regex extraction
    }

    // Fallback: 정규식으로 필드 직접 추출
    try {
        const regex = new RegExp(`"${field}"\\s*:\\s*([^,}]+)`, 'i');
        const match = text.match(regex);
        if (match) {
            const value = match[1].trim().replace(/^["']|["']$/g, '');
            // 숫자 변환 시도
            if (!isNaN(value)) return Number(value);
            return value;
        }
    } catch (e) {
        console.warn(`[extractField] Failed to extract ${field}:`, e.message);
    }

    return defaultValue;
}

/**
 * JSON 파싱 안전성 테스트
 */
export function testJSONParsing() {
    const testCases = [
        {
            name: 'Clean JSON',
            input: '{"score": 85, "feedback": "Good"}',
            expected: { score: 85, feedback: "Good" }
        },
        {
            name: 'Markdown wrapped',
            input: '```json\n{"score": 90}\n```',
            expected: { score: 90 }
        },
        {
            name: 'With preamble',
            input: 'Here is the result:\n{"score": 75, "grade": "good"}',
            expected: { score: 75, grade: "good" }
        },
        {
            name: 'Nested objects',
            input: '{"details": {"score": 88, "nested": {"deep": "value"}}}',
            expected: { details: { score: 88, nested: { deep: "value" } } }
        },
        {
            name: 'Array response',
            input: '[{"category": "A", "question": "Q1"}]',
            expected: [{ category: "A", question: "Q1" }]
        },
        {
            name: 'Multiple JSON blocks (takes first)',
            input: '{"first": 1} some text {"second": 2}',
            expected: { first: 1 }
        }
    ];

    let passed = 0;
    let failed = 0;

    testCases.forEach(test => {
        const result = safeJSONParse(test.input);
        const success = JSON.stringify(result) === JSON.stringify(test.expected);
        
        if (success) {
            console.log(`✅ ${test.name}`);
            passed++;
        } else {
            console.error(`❌ ${test.name}`);
            console.log('  Expected:', test.expected);
            console.log('  Got:', result);
            failed++;
        }
    });

    console.log(`\nTest Results: ${passed}/${testCases.length} passed`);
    return { passed, failed };
}