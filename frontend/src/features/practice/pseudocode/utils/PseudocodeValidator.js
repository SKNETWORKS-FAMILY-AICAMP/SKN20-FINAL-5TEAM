/**
 * PseudocodeValidator.js - Rule 기반 검증 엔진 (클라이언트)
 * 수정일: 2026-02-19
 *
 * [변경 사항]
 * - isMeaningfulInput 제거 → LowEffortDetector.js로 이동
 * - 이 클래스는 Rule 기반 구조/개념/흐름 검증만 담당합니다.
 */

export class PseudocodeValidator {
    constructor(problem) {
        this.problem = problem;
        this.rules = problem?.validation || this._defaultRules();
    }

    // ── 메인 검증 ───────────────────────────────────────────────

    validate(pseudocode) {
        const criticalErrors = this._checkCriticalErrors(pseudocode);
        const structure = this._analyzeStructure(pseudocode);
        const warnings = this._generateWarnings(pseudocode, structure);

        return {
            passed: criticalErrors.length === 0,
            score: structure.score,
            criticalErrors,
            warnings,
            details: {
                structure,
                concepts: this._extractConcepts(pseudocode),
                completeness: this._checkCompleteness(pseudocode),
            },
        };
    }

    // ── 치명적 오류 체크 ─────────────────────────────────────────

    _checkCriticalErrors(pseudocode) {
        const errors = [];
        const normalized = this._normalize(pseudocode);
        if (!this.rules.criticalPatterns) return errors;

        for (const p of this.rules.criticalPatterns) {
            if (p.severity === 'PRAISE' || p.severity === 'INFO') continue;

            let isError = false;
            const { pattern } = p;

            if (pattern instanceof RegExp) {
                isError = pattern.test(normalized);
            } else if (pattern && typeof pattern === 'object') {
                const { positive, negatives = [] } = pattern;
                if (positive?.test?.(normalized)) {
                    const hasNeg = negatives.some((n) => n?.test?.(normalized));
                    if (!hasNeg) isError = true;
                }
            } else if (typeof pattern === 'function') {
                try { isError = pattern(normalized); } catch { isError = false; }
            }

            if (isError) {
                errors.push({
                    severity: p.severity || 'CRITICAL',
                    message: p.message,
                    example: p.correctExample,
                    why: p.explanation,
                });
            }
        }
        return errors;
    }

    // ── 구조 분석 ────────────────────────────────────────────────

    _analyzeStructure(pseudocode) {
        const lines = pseudocode.split('\n').filter((l) => l.trim());
        const scoring = this.rules.scoring || { structure: 20, concepts: 40, flow: 40 };

        let score = 0;
        const feedback = [];

        const structureScore = this._evalBasicStructure(lines, scoring.structure);
        score += structureScore.score;
        feedback.push(...structureScore.feedback);

        const concepts = this._extractConcepts(pseudocode);
        const conceptScore = this._evalConcepts(concepts, scoring.concepts);
        score += conceptScore.score;
        feedback.push(...conceptScore.feedback);

        const flow = this._analyzeFlow(pseudocode, concepts, scoring.flow);
        score += flow.score;
        feedback.push(...flow.feedback);

        return { score: Math.min(100, score), feedback, concepts: Array.from(concepts), flow };
    }

    _evalBasicStructure(lines, maxScore) {
        let score = 0;
        const feedback = [];
        const rec = this.rules.recommendations || {};
        const min = rec.minLines || 3;
        const max = rec.maxLines || 20;

        if (lines.length >= min && lines.length <= max) {
            score += maxScore / 2;
            feedback.push('✅ 적절한 길이');
        } else {
            feedback.push(`⚠️ ${lines.length < min ? '너무 짧음' : '너무 김'}`);
        }

        if (lines.some((l) => /^\d+[\.\):]/.test(l.trim()))) {
            score += maxScore / 2;
            feedback.push('✅ 번호 매기기 사용');
        }
        return { score, feedback };
    }

    _extractConcepts(pseudocode) {
        const normalized = this._softNormalize(pseudocode);
        const found = new Set();
        for (const concept of this.rules.requiredConcepts || []) {
            for (const pattern of concept.patterns || []) {
                try {
                    if (pattern?.test?.(normalized)) { found.add(concept.id); break; }
                } catch { /* skip */ }
            }
        }
        return found;
    }

    _evalConcepts(concepts, maxScore) {
        const required = this.rules.requiredConcepts || [];
        if (!required.length) return { score: maxScore, feedback: [] };

        const totalW = required.reduce((s, c) => s + (c.weight || 1), 0);
        const foundW = required.filter((c) => concepts.has(c.id)).reduce((s, c) => s + (c.weight || 1), 0);
        const score = totalW > 0 ? Math.round(maxScore * (foundW / totalW)) : 0;

        const missing = required.filter((c) => !concepts.has(c.id)).map((c) => c.name);
        const feedback = missing.length === 0
            ? ['✅ 모든 핵심 개념 포함']
            : [`⚠️ 누락된 개념: ${missing.join(', ')}`];

        return { score, feedback };
    }

    _analyzeFlow(pseudocode, concepts, maxScore) {
        const lines = this._softNormalize(pseudocode).split('\n');
        const deps = this.rules.dependencies || [];
        if (!deps.length) return { score: maxScore, feedback: [] };

        const totalPts = deps.reduce((s, d) => s + (d.points || 0), 0);
        if (!totalPts) return { score: maxScore, feedback: [] };

        let score = 0;
        const feedback = [];
        for (const dep of deps) {
            const bi = this._findConceptLine(lines, dep.before);
            const ai = this._findConceptLine(lines, dep.after);
            if (bi === -1 || ai === -1) continue;
            const pts = dep.points || 0;
            if (bi < ai) {
                score += (pts / totalPts) * maxScore;
                feedback.push(`✅ ${dep.name} 순서 정확`);
            } else if (dep.strictness === 'REQUIRED') {
                feedback.push(`❌ ${dep.name}: 순서 오류 (필수)`);
            } else {
                score += (pts / 2 / totalPts) * maxScore;
                feedback.push(`⚠️ ${dep.name}: 순서 권장됨`);
            }
        }
        return { score: Math.round(score), feedback };
    }

    _findConceptLine(lines, conceptId) {
        const concept = (this.rules.requiredConcepts || []).find((c) => c.id === conceptId);
        if (!concept) return -1;
        for (let i = 0; i < lines.length; i++) {
            for (const p of concept.patterns || []) {
                try { if (p?.test?.(lines[i])) return i; } catch { /* skip */ }
            }
        }
        return -1;
    }

    // ── 정규화 ────────────────────────────────────────────────────

    _normalize(text) {
        if (!text) return '';
        return text
            .toLowerCase()
            .replace(/\s+/g, ' ')
            .replace(/[^a-z0-9가-힣\s\.\,\(\)\_\-\:\;\=\>\<\!\?\/]/g, ' ')
            .trim();
    }

    _softNormalize(text) {
        if (!text) return '';
        return text.toLowerCase().replace(/\s+/g, ' ').trim();
    }

    // ── 완성도 / 경고 ─────────────────────────────────────────────

    _checkCompleteness(pseudocode) {
        const wordCount = pseudocode.split(/\s+/).filter((w) => w.length > 0).length;
        const rec = this.rules.recommendations || {};
        const minW = rec.minWords || 20;
        const maxW = rec.maxWords || 200;
        return {
            wordCount,
            adequate: wordCount >= minW && wordCount <= maxW,
            message: wordCount < minW
                ? `의사코드가 너무 간략합니다 (최소 ${minW}단어 권장)`
                : wordCount > maxW
                    ? `너무 세부적입니다 (최대 ${maxW}단어 권장)`
                    : '적절한 길이입니다.',
        };
    }

    _generateWarnings(pseudocode, structure) {
        const warnings = [];
        const completeness = this._checkCompleteness(pseudocode);
        if (!completeness.adequate) warnings.push(completeness.message);

        if (this.rules.recommendations?.exceptionHandling) {
            const soft = this._softNormalize(pseudocode);
            if (!/예외|오류|체크|검증|validation|error|check/i.test(soft)) {
                warnings.push('💡 예외 상황 처리를 추가하면 더 견고한 설계가 됩니다.');
            }
        }
        return warnings;
    }

    _defaultRules() {
        return {
            criticalPatterns: [],
            requiredConcepts: [
                { id: 'input',   name: '입력', weight: 1, patterns: [/입력|input|받|receive/i] },
                { id: 'process', name: '처리', weight: 1, patterns: [/처리|계산|process|compute/i] },
                { id: 'output',  name: '출력', weight: 1, patterns: [/출력|반환|return|output/i] },
            ],
            dependencies: [],
            scoring: { structure: 20, concepts: 40, flow: 40 },
            recommendations: { exceptionHandling: false, minLines: 3, maxLines: 20, minWords: 20, maxWords: 200 },
        };
    }
}

/**
 * 코드 검증 헬퍼 (주석 제거 후 검증)
 */
export class CodeValidator {
    constructor(rules) {
        this.rules = rules || {};
    }

    removeComments(code) {
        const patterns = this.rules.commentPatterns || [
            /#.*$/gm, /"""[\s\S]*?"""/g, /'''[\s\S]*?'''/g,
            /\/\/.*$/gm, /\/\*[\s\S]*?\*\//g,
        ];
        return patterns.reduce((c, p) => c.replace(p, ''), code);
    }

    validate(code) {
        const clean = this.removeComments(code);
        const errors = [];
        const warnings = [];

        for (const call of this.rules.requiredCalls || []) {
            if (!call.pattern.test(clean)) errors.push(`❌ ${call.name} 호출 누락`);
        }
        for (const f of this.rules.forbiddenPatterns || []) {
            const src = f.excludeComments ? clean : code;
            if (f.pattern.test(src)) errors.push(`🚨 ${f.message}`);
        }
        return { passed: errors.length === 0, errors, warnings, cleanCode: clean };
    }
}
