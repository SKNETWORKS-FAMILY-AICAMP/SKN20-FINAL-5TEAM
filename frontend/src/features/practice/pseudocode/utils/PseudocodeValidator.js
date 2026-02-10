/**
 * PseudocodeValidator.js - 규칙 주입형 검증 엔진
 * 
 * 개선 사항:
 * 3. 검증 규칙을 외부에서 주입받음 (OCP 준수)
 * 5. 부정어 처리 로직 추가
 * 6. 코드 검증 시 주석 제거
 * 
 * [2026-02-09] Rule Engine 리팩토링 (Antigravity + Claude)
 */

export class PseudocodeValidator {
    constructor(problem) {
        this.problem = problem;
        
        // ✨ 개선: 규칙을 외부에서 주입받음
        this.rules = problem?.validation || this.getDefaultRules();
        
        // 검증 타입별 라이브러리 (필요 시)
        this.typeLibrary = problem?.validationTypeLibrary || {};
    }

    /**
     * 메인 검증 함수
     */
    validate(pseudocode) {
        const criticalErrors = this.checkCriticalErrors(pseudocode);
        const structure = this.analyzeStructure(pseudocode);
        const warnings = this.generateWarnings(pseudocode, structure);
        
        return {
            passed: criticalErrors.length === 0,
            score: structure.score,
            criticalErrors,
            warnings,
            details: {
                structure,
                concepts: this.extractConcepts(pseudocode),
                completeness: this.checkCompleteness(pseudocode)
            }
        };
    }

    /**
     * ✨ 5번 해결: 부정어를 고려한 치명적 오류 체크
     */
    checkCriticalErrors(pseudocode) {
        const errors = [];
        const normalized = this.normalize(pseudocode);

        if (!this.rules.criticalPatterns) return errors;

        for (const patternDef of this.rules.criticalPatterns) {
            // 새로운 구조: { pattern: { positive, negatives }, message, ... }
            const { pattern, message, correctExample, explanation } = patternDef;
            
            let isError = false;

            // 단순 정규식 (하위 호환)
            if (pattern instanceof RegExp) {
                isError = pattern.test(normalized);
            }
            // 부정어 포함 객체 구조
            else if (typeof pattern === 'object') {
                const { positive, negatives = [] } = pattern;
                
                // 1. 양성 패턴 체크
                if (positive.test(normalized)) {
                    // 2. 부정어가 있는지 체크
                    const hasNegative = negatives.some(neg => neg.test(normalized));
                    
                    // 부정어 없으면 오류
                    if (!hasNegative) {
                        isError = true;
                    }
                }
            }
            // 함수형 (최대 유연성)
            else if (typeof pattern === 'function') {
                isError = pattern(normalized);
            }

            if (isError) {
                errors.push({
                    severity: patternDef.severity || 'CRITICAL',
                    message,
                    example: correctExample,
                    why: explanation
                });
            }
        }

        return errors;
    }

    /**
     * ✨ 3번 해결: 외부 규칙 기반 구조 분석
     */
    analyzeStructure(pseudocode) {
        const lines = pseudocode.split('\n').filter(l => l.trim());
        
        let score = 0;
        const feedback = [];

        // 점수 구성 (규칙에서 가져옴)
        const scoring = this.rules.scoring || {
            structure: 20,
            concepts: 40,
            flow: 40
        };

        // 1. 기본 구조 (scoring.structure 점수)
        const structureScore = this.evaluateBasicStructure(lines, scoring.structure);
        score += structureScore.score;
        feedback.push(...structureScore.feedback);

        // 2. 핵심 개념 (scoring.concepts 점수)
        const concepts = this.extractConcepts(pseudocode);
        const conceptScore = this.evaluateConcepts(concepts, scoring.concepts);
        score += conceptScore.score;
        feedback.push(...conceptScore.feedback);

        // 3. 논리적 흐름 (scoring.flow 점수)
        const flow = this.analyzeLogicalFlow(pseudocode, concepts, scoring.flow);
        score += flow.score;
        feedback.push(...flow.feedback);

        return {
            score: Math.min(100, score),
            feedback,
            concepts: Array.from(concepts),
            flow
        };
    }

    /**
     * 기본 구조 평가 (외부 규칙 반영)
     */
    evaluateBasicStructure(lines, maxScore) {
        let score = 0;
        const feedback = [];
        
        const recommendations = this.rules.recommendations || {};
        const minLines = recommendations.minLines || 3;
        const maxLines = recommendations.maxLines || 20;

        // 길이 체크
        if (lines.length >= minLines && lines.length <= maxLines) {
            score += maxScore / 2;
            feedback.push('✅ 적절한 길이');
        } else if (lines.length < minLines) {
            feedback.push(`⚠️ 너무 짧음 (최소 ${minLines}줄 권장)`);
        } else {
            feedback.push(`⚠️ 너무 김 (최대 ${maxLines}줄 권장)`);
        }

        // 번호 매기기 체크
        const hasNumbering = lines.filter(l => /^\d+[\.\):]/.test(l.trim())).length > 0;
        const preferredStyle = recommendations.preferredStyle;
        
        if (hasNumbering) {
            score += maxScore / 2;
            feedback.push('✅ 번호 매기기 사용');
        } else if (preferredStyle === 'numbered') {
            feedback.push('💡 번호 매기기를 권장합니다');
        }

        return { score, feedback };
    }

    /**
     * ✨ 3번 해결: 규칙 기반 개념 추출 (가중치 반영)
     */
    extractConcepts(pseudocode) {
        const normalized = this.normalize(pseudocode);
        const concepts = new Set();

        if (!this.rules.requiredConcepts) return concepts;

        for (const concept of this.rules.requiredConcepts) {
            for (const pattern of concept.patterns) {
                if (pattern.test(normalized)) {
                    concepts.add(concept.id);
                    break;
                }
            }
        }

        return concepts;
    }

    /**
     * 개념 평가 (가중치 반영)
     */
    evaluateConcepts(concepts, maxScore) {
        const feedback = [];
        const requiredConcepts = this.rules.requiredConcepts || [];
        
        if (requiredConcepts.length === 0) {
            return { score: maxScore, feedback: ['(개념 검증 규칙 없음)'] };
        }

        // 가중치 합산
        let totalWeight = 0;
        let foundWeight = 0;
        
        for (const required of requiredConcepts) {
            const weight = required.weight || 1;
            totalWeight += weight;
            
            if (concepts.has(required.id)) {
                foundWeight += weight;
            }
        }

        const score = Math.round(maxScore * (foundWeight / totalWeight));
        
        if (foundWeight === totalWeight) {
            feedback.push('✅ 모든 핵심 개념 포함');
        } else {
            const missing = requiredConcepts
                .filter(c => !concepts.has(c.id))
                .map(c => c.name);
            feedback.push(`⚠️ 누락된 개념: ${missing.join(', ')}`);
        }

        return { score, feedback };
    }

    /**
     * 논리적 흐름 분석 (규칙 주입)
     */
    analyzeLogicalFlow(pseudocode, concepts, maxScore) {
        const lines = pseudocode.toLowerCase().split('\n');
        let score = 0;
        const feedback = [];

        if (!this.rules.dependencies) {
            return { score: maxScore, feedback: ['(흐름 검증 규칙 없음)'] };
        }

        // 총 포인트 계산
        const totalPoints = this.rules.dependencies.reduce((sum, dep) => sum + dep.points, 0);

        for (const dep of this.rules.dependencies) {
            const beforeIdx = this.findConceptLine(lines, dep.before);
            const afterIdx = this.findConceptLine(lines, dep.after);

            if (beforeIdx === -1 || afterIdx === -1) {
                continue;
            }

            if (beforeIdx < afterIdx) {
                score += (dep.points / totalPoints) * maxScore;
                feedback.push(`✅ ${dep.name} 순서 정확`);
            } else {
                // Strictness 체크
                if (dep.strictness === 'REQUIRED') {
                    feedback.push(`❌ ${dep.name}: 순서 오류 (필수)`);
                } else {
                    feedback.push(`⚠️ ${dep.name}: 순서 권장됨`);
                    score += ((dep.points / 2) / totalPoints) * maxScore;  // 부분 점수
                }
            }
        }

        return { score: Math.round(score), feedback };
    }

    /**
     * 개념이 등장하는 첫 번째 라인 찾기
     */
    findConceptLine(lines, conceptId) {
        const concept = this.rules.requiredConcepts?.find(c => c.id === conceptId);
        if (!concept) return -1;

        for (let i = 0; i < lines.length; i++) {
            for (const pattern of concept.patterns) {
                if (pattern.test(lines[i])) {
                    return i;
                }
            }
        }
        return -1;
    }

    /**
     * 정규화
     */
    normalize(text) {
        let normalized = text.toLowerCase();
        normalized = normalized.replace(/\s+/g, ' ');
        normalized = normalized.replace(/[^a-z0-9가-힣\s\.\,\(\)]/g, ' ');
        return normalized;
    }

    /**
     * 완성도 체크 (규칙 반영)
     */
    checkCompleteness(pseudocode) {
        const wordCount = pseudocode.split(/\s+/).length;
        const recommendations = this.rules.recommendations || {};
        const minWords = recommendations.minWords || 20;
        const maxWords = recommendations.maxWords || 200;
        
        return {
            wordCount,
            adequate: wordCount >= minWords && wordCount <= maxWords,
            message: wordCount < minWords
                ? `의사코드가 너무 간략합니다 (최소 ${minWords}단어 권장)`
                : wordCount > maxWords
                ? `너무 세부적입니다 (최대 ${maxWords}단어 권장)`
                : '적절한 길이입니다.'
        };
    }

    /**
     * 경고 메시지 생성
     */
    generateWarnings(pseudocode, structure) {
        const warnings = [];
        const recommendations = this.rules.recommendations || {};

        const completeness = this.checkCompleteness(pseudocode);
        if (!completeness.adequate) {
            warnings.push(completeness.message);
        }

        // 예외 처리 권장
        if (recommendations.exceptionHandling) {
            const normalized = this.normalize(pseudocode);
            const hasExceptionHandling = /예외|오류|체크|검증|확인|validation|error|check/.test(normalized);
            
            if (!hasExceptionHandling) {
                warnings.push('💡 예외 상황 처리를 추가하면 더 견고한 설계가 됩니다.');
            }
        }

        return warnings;
    }

    /**
     * 기본 규칙 (하위 호환용)
     */
    getDefaultRules() {
        return {
            criticalPatterns: [],
            requiredConcepts: [
                {
                    id: 'input',
                    name: '입력',
                    weight: 1,
                    patterns: [/입력|input|받|receive/i]
                },
                {
                    id: 'process',
                    name: '처리',
                    weight: 1,
                    patterns: [/처리|계산|process|compute/i]
                },
                {
                    id: 'output',
                    name: '출력',
                    weight: 1,
                    patterns: [/출력|반환|return|output/i]
                }
            ],
            dependencies: [],
            scoring: {
                structure: 20,
                concepts: 40,
                flow: 40
            },
            recommendations: {
                exceptionHandling: false,
                minLines: 3,
                maxLines: 20,
                minWords: 20,
                maxWords: 200
            }
        };
    }
}

/**
 * ✨ 6번 해결: 코드 검증 헬퍼 (주석 제거)
 */
export class CodeValidator {
    constructor(codeValidationRules) {
        this.rules = codeValidationRules || {};
    }

    /**
     * 주석 제거
     */
    removeComments(code) {
        let cleaned = code;
        
        const commentPatterns = this.rules.commentPatterns || [
            /#.*$/gm,           // Python #
            /"""[\s\S]*?"""/g,  // Python """
            /'''[\s\S]*?'''/g,  // Python '''
            /\/\/.*$/gm,        // JS //
            /\/\*[\s\S]*?\*\//g // JS /* */
        ];

        for (const pattern of commentPatterns) {
            cleaned = cleaned.replace(pattern, '');
        }

        return cleaned;
    }

    /**
     * 코드 검증 (주석 제외)
     */
    validate(code) {
        const cleanCode = this.removeComments(code);
        const errors = [];
        const warnings = [];

        // 필수 호출 체크
        if (this.rules.requiredCalls) {
            for (const callDef of this.rules.requiredCalls) {
                const found = callDef.pattern.test(cleanCode);
                
                if (!found) {
                    errors.push(`❌ ${callDef.name} 호출 누락`);
                }
            }
        }

        // 금지 패턴 체크
        if (this.rules.forbiddenPatterns) {
            for (const forbiddenDef of this.rules.forbiddenPatterns) {
                const codeToCheck = forbiddenDef.excludeComments 
                    ? cleanCode 
                    : code;
                
                if (forbiddenDef.pattern.test(codeToCheck)) {
                    errors.push(`🚨 ${forbiddenDef.message}`);
                }
            }
        }

        return {
            passed: errors.length === 0,
            errors,
            warnings,
            cleanCode
        };
    }
}