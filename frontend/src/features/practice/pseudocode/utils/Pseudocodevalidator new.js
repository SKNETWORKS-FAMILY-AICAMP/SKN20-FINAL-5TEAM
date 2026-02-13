/**
 * Pseudocode Validator v2.0
 * validationRules.js 기반 동적 검증
 * 
 * [2026-02-14] 긴급 재작성 - 실제 작동 버전
 */

export class PseudocodeValidator {
  constructor(validationRules) {
    if (!validationRules) {
      throw new Error('Validation rules required');
    }
    this.rules = validationRules;
  }

  /**
   * 1단계: 치명적 패턴 검증 (블로킹)
   */
  validateCriticalPatterns(text) {
    if (!this.rules.criticalPatterns) {
      return { isValid: true, errors: [] };
    }

    const errors = [];

    for (const rule of this.rules.criticalPatterns) {
      const matched = this._matchPattern(text, rule.pattern);
      
      if (matched) {
        errors.push({
          type: 'CRITICAL',
          message: rule.message,
          correctExample: rule.correctExample,
          explanation: rule.explanation,
          severity: rule.severity || 'CRITICAL'
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * 2단계: 필수 개념 점수 계산
   */
  calculateConceptScore(text) {
    if (!this.rules.requiredConcepts) {
      return { score: 0, matched: [], missing: [] };
    }

    const matched = [];
    const missing = [];
    let totalScore = 0;
    const maxScore = this.rules.requiredConcepts.reduce((sum, c) => sum + c.weight, 0);

    for (const concept of this.rules.requiredConcepts) {
      const isPresent = concept.patterns.some(pattern => {
        return this._testPattern(text, pattern);
      });

      if (isPresent) {
        matched.push({
          id: concept.id,
          name: concept.name,
          weight: concept.weight
        });
        totalScore += concept.weight;
      } else {
        missing.push({
          id: concept.id,
          name: concept.name,
          hints: concept.hints || []
        });
      }
    }

    return {
      score: totalScore,
      maxScore,
      percentage: maxScore > 0 ? (totalScore / maxScore) * 100 : 0,
      matched,
      missing
    };
  }

  /**
   * 3단계: 논리적 순서 검증
   */
  validateFlow(text) {
    if (!this.rules.dependencies) {
      return { isValid: true, violations: [], score: 100 };
    }

    const violations = [];
    let totalPoints = 0;
    let earnedPoints = 0;

    // 각 개념의 위치 찾기
    const conceptPositions = this._findConceptPositions(text);

    for (const dep of this.rules.dependencies) {
      totalPoints += dep.points || 10;

      const beforePos = conceptPositions[dep.before];
      const afterPos = conceptPositions[dep.after];

      if (beforePos === -1 || afterPos === -1) {
        // 개념이 누락됨 (이미 개념 점수에서 감점)
        continue;
      }

      if (beforePos < afterPos) {
        // 순서 정상
        earnedPoints += dep.points || 10;
      } else {
        // 순서 위반
        violations.push({
          name: dep.name,
          expected: `${dep.before} → ${dep.after}`,
          actual: `${dep.after} → ${dep.before}`,
          points: dep.points || 10,
          strictness: dep.strictness || 'RECOMMENDED'
        });
      }
    }

    return {
      isValid: violations.filter(v => v.strictness === 'REQUIRED').length === 0,
      violations,
      score: totalPoints > 0 ? (earnedPoints / totalPoints) * 100 : 100
    };
  }

  /**
   * 종합 평가
   */
  evaluate(text) {
    // 1. 기본 구조 검증
    const structure = this._validateStructure(text);
    
    // 2. 치명적 패턴
    const critical = this.validateCriticalPatterns(text);
    
    if (!critical.isValid) {
      return {
        isValid: false,
        score: 0,
        breakdown: {
          structure: 0,
          concepts: 0,
          flow: 0
        },
        errors: critical.errors,
        feedback: this._generateErrorFeedback(critical.errors)
      };
    }

    // 3. 개념 점수
    const concepts = this.calculateConceptScore(text);
    
    // 4. 논리 흐름
    const flow = this.validateFlow(text);

    // 5. 최종 점수 계산
    const scoring = this.rules.scoring || { structure: 20, concepts: 40, flow: 40 };
    
    const breakdown = {
      structure: (structure.score / 100) * scoring.structure,
      concepts: (concepts.percentage / 100) * scoring.concepts,
      flow: (flow.score / 100) * scoring.flow
    };

    const totalScore = Math.round(
      breakdown.structure + breakdown.concepts + breakdown.flow
    );

    return {
      isValid: totalScore >= 60,
      score: totalScore,
      breakdown,
      concepts: {
        matched: concepts.matched,
        missing: concepts.missing
      },
      flow: {
        violations: flow.violations
      },
      feedback: this._generateFeedback(totalScore, concepts, flow)
    };
  }

  // ==================== 내부 헬퍼 메서드 ====================

  /**
   * 패턴 매칭 (부정어 고려)
   */
  _matchPattern(text, patternRule) {
    if (!patternRule) return false;

    // 단순 정규식인 경우
    if (patternRule instanceof RegExp) {
      return patternRule.test(text);
    }

    // positive/negatives 구조
    const { positive, negatives } = patternRule;
    
    if (!positive.test(text)) {
      return false; // positive 패턴 불일치
    }

    // 부정어 검사
    if (negatives && negatives.length > 0) {
      const positiveMatch = text.match(positive);
      if (!positiveMatch) return false;

      const positiveIndex = positiveMatch.index;

      // 부정어가 positive 앞에 있으면 안전
      for (const negPattern of negatives) {
        const negMatch = text.match(negPattern);
        if (negMatch && negMatch.index < positiveIndex) {
          return false; // 부정어로 무효화됨
        }
      }
    }

    return true; // 실제 오류
  }

  _testPattern(text, pattern) {
    if (pattern instanceof RegExp) {
      return pattern.test(text);
    }
    return false;
  }

  /**
   * 개념 위치 찾기
   */
  _findConceptPositions(text) {
    const positions = {};
    
    if (!this.rules.requiredConcepts) return positions;

    for (const concept of this.rules.requiredConcepts) {
      positions[concept.id] = -1; // 기본값: 없음

      for (const pattern of concept.patterns) {
        const match = text.match(pattern);
        if (match) {
          positions[concept.id] = match.index;
          break;
        }
      }
    }

    return positions;
  }

  /**
   * 기본 구조 검증
   */
  _validateStructure(text) {
    const lines = text.split('\n').filter(line => line.trim().length > 0);
    const recommendations = this.rules.recommendations || {};

    let score = 100;
    const issues = [];

    // 최소 줄 수
    if (recommendations.minLines && lines.length < recommendations.minLines) {
      score -= 30;
      issues.push(`최소 ${recommendations.minLines}줄 이상 작성하세요`);
    }

    // 최대 줄 수
    if (recommendations.maxLines && lines.length > recommendations.maxLines) {
      score -= 20;
      issues.push(`${recommendations.maxLines}줄 이하로 간결하게 작성하세요`);
    }

    // 번호 매기기 권장
    if (recommendations.preferredStyle === 'numbered') {
      const numberedLines = lines.filter(line => /^\s*\d+[\.)]\s/.test(line));
      if (numberedLines.length < lines.length * 0.5) {
        score -= 10;
        issues.push('단계별 번호를 붙이면 더 명확합니다');
      }
    }

    return { score: Math.max(0, score), issues };
  }

  /**
   * 피드백 생성
   */
  _generateFeedback(score, concepts, flow) {
    const parts = [];

    if (score >= 90) {
      parts.push('🎉 완벽합니다!');
    } else if (score >= 70) {
      parts.push('✅ 좋은 답변입니다!');
    } else if (score >= 50) {
      parts.push('⚠️ 개선이 필요합니다.');
    } else {
      parts.push('❌ 다시 시도해보세요.');
    }

    // 누락된 개념
    if (concepts.missing.length > 0) {
      parts.push('\n\n📝 누락된 개념:');
      concepts.missing.forEach(m => {
        parts.push(`\n  • ${m.name}`);
        if (m.hints && m.hints.length > 0) {
          parts.push(`\n    💡 ${m.hints[0]}`);
        }
      });
    }

    // 순서 위반
    if (flow.violations.length > 0) {
      parts.push('\n\n🔄 순서 개선 필요:');
      flow.violations.forEach(v => {
        parts.push(`\n  • ${v.name}: ${v.expected}`);
      });
    }

    return parts.join('');
  }

  _generateErrorFeedback(errors) {
    return errors.map(err => {
      return `${err.message}\n💡 올바른 방법: ${err.correctExample}\n📖 ${err.explanation}`;
    }).join('\n\n');
  }
}

/**
 * 코드 검증 (Phase 4용)
 */
export class CodeValidator {
  constructor(codeValidationRules) {
    this.rules = codeValidationRules || {};
  }

  validate(code) {
    const cleanCode = this._removeComments(code);
    
    // 필수 호출 검사
    const missingCalls = [];
    if (this.rules.requiredCalls) {
      for (const call of this.rules.requiredCalls) {
        if (!call.pattern.test(cleanCode)) {
          missingCalls.push(call.name);
        }
      }
    }

    // 금지 패턴 검사
    const violations = [];
    if (this.rules.forbiddenPatterns) {
      for (const pattern of this.rules.forbiddenPatterns) {
        if (pattern.pattern.test(cleanCode)) {
          violations.push(pattern.message);
        }
      }
    }

    return {
      isValid: missingCalls.length === 0 && violations.length === 0,
      missingCalls,
      violations
    };
  }

  _removeComments(code) {
    let cleaned = code;
    
    if (this.rules.commentPatterns) {
      for (const pattern of this.rules.commentPatterns) {
        cleaned = cleaned.replace(pattern, '');
      }
    }

    return cleaned;
  }
}