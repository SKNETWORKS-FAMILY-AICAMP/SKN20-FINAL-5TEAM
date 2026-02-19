/**
 * pseudocodeApi.js - HTTP 호출 전용
 * 수정일: 2026-02-19
 *
 * [변경 사항]
 * - 이 파일은 백엔드 API 호출만 담당합니다.
 * - 평가 흐름 제어, 점수 통합, tail question 생성 로직은 모두 제거됐습니다.
 *   → useEvaluationOrchestrator.js 참조
 * - YouTube 추천 API 호출도 제거됐습니다.
 *   → 하드코딩 큐레이션으로 단순화 (learningResources.js 참조)
 */

import axios from 'axios';

// ── 5차원 평가 요청 ────────────────────────────────────────────────────────
/**
 * 의사코드 5차원 평가를 백엔드에 요청합니다.
 *
 * @param {string|number} questId
 * @param {string} questTitle
 * @param {string} pseudocode
 * @returns {Promise<AxiosResponse>}
 */
export async function requestEvaluation(questId, questTitle, pseudocode) {
    return axios.post(
        '/api/core/pseudocode/evaluate-5d',
        { quest_id: questId, quest_title: questTitle, pseudocode },
        { timeout: 45000 },
    );
}

// ── 힌트 에이전트 요청 ─────────────────────────────────────────────────────
/**
 * 학생이 막혔을 때 힌트를 요청합니다. 점수를 반환하지 않습니다.
 *
 * @param {Object} params
 * @param {string} params.user_logic        - 학생의 현재 설계 초안
 * @param {string} params.quest_title
 * @param {string} params.quest_description
 * @param {string} params.selected_strategy
 * @param {string[]} params.constraints
 * @param {number} params.hint_level        - 1(방향만) | 2(구체적) | 3(핵심)
 * @returns {Promise<{hint: string, focus_point: string, guiding_question: string|null}>}
 */
export async function requestHint(params) {
    const response = await axios.post('/api/core/pseudo-agent/', params, { timeout: 25000 });
    return response.data;
}

// ── 진단 문제 평가 ──────────────────────────────────────────────────────────
/**
 * 서술형/순서형 진단 문제의 답변을 AI로 평가합니다.
 */
export async function evaluateDiagnosticAnswer(question, userAnswer) {
    const rubric = question.evaluationRubric || {};
    const isOrdering = question.type === 'ORDERING';

    const response = await axios.post(
        '/api/core/ai-proxy/',
        {
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: _buildDiagnosticSystemPrompt(rubric, isOrdering) },
                {
                    role: 'user',
                    content: isOrdering
                        ? `학생이 제출한 정렬 결과: ${userAnswer}`
                        : `학생의 답변: "${userAnswer}"`,
                },
            ],
            response_format: { type: 'json_object' },
        },
        { timeout: 15000 },
    );

    let result = response.data?.content ?? response.data;
    if (typeof result === 'string') {
        try { result = JSON.parse(result); } catch { /* ignore */ }
    }
    return result || { score: 50, is_correct: false, feedback: '분석을 완료하지 못했습니다.' };
}

// ── Python 코드 실행 ────────────────────────────────────────────────────────
/**
 * Docker 샌드박스에서 Python 코드를 실행합니다.
 */
export async function executePythonCode(code, functionName, testCases) {
    const response = await axios.post(
        '/api/core/pseudocode/execute/',
        { code, function_name: functionName, test_cases: testCases },
        { timeout: 20000 },
    );
    return response.data;
}

// ── 심화 질문 생성 ──────────────────────────────────────────────────────────
/**
 * 의사코드 기반으로 deep-dive 질문 3개를 생성합니다.
 */
export async function generateDeepDiveQuestions(problem, pseudocode) {
    const response = await axios.post(
        '/api/core/ai-proxy/',
        {
            model: 'gpt-4o-mini',
            messages: [
                {
                    role: 'system',
                    content: `You are an experienced technical interviewer.
Generate 3 insightful follow-up questions to assess deeper understanding.
Categories: 1. Logic Understanding  2. Edge Cases  3. Optimization
Return JSON array: [{"category":"...","question":"..."}, ...]`,
                },
                {
                    role: 'user',
                    content: `Problem: ${problem?.title || ''}\nPseudocode:\n${pseudocode}`,
                },
            ],
            max_tokens: 400,
            temperature: 0.8,
        },
        { timeout: 15000 },
    );

    const raw = response.data?.content ?? response.data;
    const parsed = typeof raw === 'string' ? _safeParseJSON(raw) : raw;

    if (Array.isArray(parsed) && parsed.length > 0) return parsed;

    // fallback
    return [
        { category: 'Logic Understanding', question: '이 알고리즘의 핵심 아이디어를 한 문장으로 설명해 주세요.' },
        { category: 'Edge Cases', question: '입력 데이터가 비어있거나 예상과 다른 형식일 때 어떻게 처리하나요?' },
        { category: 'Optimization', question: '이 알고리즘의 시간 복잡도는 어떻게 되며, 개선할 수 있는 부분이 있나요?' },
    ];
}

// ── 정합성 체크 ───────────────────────────────────────────────────────────
/**
 * 의사코드와 실제 구현 코드 간의 정합성을 확인합니다.
 *
 * @param {string} pseudocode
 * @param {string} implementationCode
 * @param {string} checkType - 'dataLeakage' 등
 * @returns {Promise<{score: number, gaps: string[], feedback: string}>}
 */
export async function checkConsistency(pseudocode, implementationCode, checkType = 'dataLeakage') {
    const response = await axios.post(
        '/api/core/ai-proxy/',
        {
            model: 'gpt-4o-mini',
            messages: [
                {
                    role: 'system',
                    content: `당신은 코드 정합성 검토 전문가입니다.
의사코드(설계)와 실제 구현 코드가 일치하는지 평가하고 JSON으로 응답하세요.
체크 유형: ${checkType}
출력 형식: {"score":0-100, "gaps":["불일치 항목1","불일치 항목2"], "feedback":"한 줄 요약"}`,
                },
                {
                    role: 'user',
                    content: `[의사코드]\n${pseudocode}\n\n[구현 코드]\n${implementationCode}`,
                },
            ],
            response_format: { type: 'json_object' },
        },
        { timeout: 15000 },
    );

    let result = response.data?.content ?? response.data;
    if (typeof result === 'string') {
        try { result = JSON.parse(result); } catch { /* ignore */ }
    }
    return result || { score: 0, gaps: ['정합성 분석 실패'], feedback: '분석을 완료하지 못했습니다.' };
}

// ── 내부 유틸 ─────────────────────────────────────────────────────────────

function _safeParseJSON(text) {
    try {
        const cleaned = text.replace(/```json|```/g, '').trim();
        return JSON.parse(cleaned);
    } catch {
        return null;
    }
}

function _buildDiagnosticSystemPrompt(rubric, isOrdering) {
    if (isOrdering) {
        return `당신은 데이터 과학 교육 전문가입니다.
학생이 제출한 '정렬 순서'의 논리적 타당성을 평가하고 JSON으로 응답하세요.
정답 설명: ${rubric.correctAnswer || ''}
출력 형식: {"score":0-100,"is_correct":bool,"feedback":"한글 150자 이내","analysis":"단계별 분석"}`;
    }
    return `당신은 데이터 과학 교육 전문가입니다.
학생의 답변을 평가하고 JSON으로 응답하세요.
키워드: ${rubric.keyKeywords?.join(', ') || ''}
출력 형식: {"score":0-100,"is_correct":bool,"feedback":"한글 150자 이내","analysis":"간략 분석"}`;
}
