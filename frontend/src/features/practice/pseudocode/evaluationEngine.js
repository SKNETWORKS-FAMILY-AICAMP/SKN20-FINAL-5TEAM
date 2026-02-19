/**
 * 평가 엔진 - LLM 85% + Rule 15%
 * Stage별 점수 계산 및 종합 평가
 * 수정일: 2026-02-19
 * 수정 내용:
 *  - one_line_comment 유실 버그 수정 (LLM 응답 필드를 results에 제대로 저장)
 *  - Critical 패턴 정규식 자연어 의사코드 대응으로 확장
 *  - 키워드 동의어 추가 (분리, 분할, 표준화 등)
 *  - callGPT credentials: 'include' 추가
 */

// ==================== Rule 기반 평가 (15점) ====================
export class RuleBasedEvaluator {
  constructor() {
    // 동의어 그룹으로 묶어서 하나라도 있으면 인정
    this.keywordGroups = [
      { label: '데이터 분리',   patterns: [/격리|분리|분할|split|나누/i] },
      { label: '기준점 설정',   patterns: [/기준점|anchor|fit|학습시키|통계량/i] },
      { label: '일관성 유지',   patterns: [/일관성|consistency|동일|같은|transform|변환/i] },
      { label: '학습 데이터',   patterns: [/train|학습\s*데이터|훈련\s*데이터/i] },
      { label: '테스트 데이터', patterns: [/test|테스트\s*데이터|검증\s*데이터/i] },
    ];

    // 자연어 의사코드에서도 치명적 패턴 감지할 수 있도록 괄호 요건 제거
    this.criticalPatterns = [
      {
        pattern: /(전체|모든|전부)\s*(데이터|data).{0,20}(fit|학습시키|학습시킴|피팅|기준점\s*설정)/i,
        error: '🚨 치명적: 전체 데이터로 fit 호출 감지 (데이터 누수 위험)'
      },
      {
        pattern: /(test|테스트|검증)\s*(데이터|data).{0,20}(fit|학습시키|학습시킴|피팅|기준점\s*설정)/i,
        error: '🚨 치명적: 테스트 데이터로 fit 호출 감지 (데이터 누수 위험)'
      }
    ];
  }

  /**
   * Stage 2 - Rule 기반 평가 (15점)
   */
  evaluateStage2Rule(pseudocode) {
    const feedback = [];

    // 1. 치명적 패턴 검사
    for (const { pattern, error } of this.criticalPatterns) {
      if (pattern.test(pseudocode)) {
        feedback.push({ type: 'critical', message: error });
        return { score: 0, feedback, critical: true };
      }
    }

    // 2. 키워드 그룹 체크 (그룹당 2점, 최대 10점)
    const keywordScores = this.keywordGroups.map(group => {
      const found = group.patterns.some(p => p.test(pseudocode));
      return { label: group.label, found, score: found ? 2 : 0 };
    });

    const keywordScore = Math.min(
      keywordScores.reduce((sum, k) => sum + k.score, 0),
      10
    );

    // 3. 순서 검증 (5점)
    const orderScore = this.checkOrder(pseudocode);

    const score = keywordScore + orderScore;

    feedback.push({
      type: 'success',
      message: `키워드 그룹: ${keywordScores.filter(k => k.found).length}/${this.keywordGroups.length}`,
      details: keywordScores
    });

    return { score, feedback, critical: false };
  }

  /**
   * 순서 검증 - 분리 → fit → transform 순서 확인
   */
  checkOrder(text) {
    const splitIndex  = this.findPatternIndex(text, /분리|분할|split|격리|나누/i);
    const fitIndex    = this.findPatternIndex(text, /fit|학습시키|기준점\s*설정|통계량\s*추출/i);
    const transformIndex = this.findPatternIndex(text, /transform|변환|적용/i);

    if (splitIndex === -1 || fitIndex === -1) return 0;

    if (splitIndex < fitIndex) {
      if (transformIndex === -1 || fitIndex < transformIndex) return 5;
      return 3;
    }

    return 0;
  }

  findPatternIndex(text, pattern) {
    const match = text.match(pattern);
    return match ? match.index : -1;
  }

  /**
   * 부족한 키워드 감지 (꼬리질문 트리거용)
   */
  getMissingKeywords(pseudocode) {
    const missing = [];
    if (!/(격리|분리|분할|split|나누)/i.test(pseudocode))       missing.push('isolation');
    if (!/(기준점|anchor|fit|학습시키|통계량)/i.test(pseudocode)) missing.push('anchor');
    if (!/(일관성|consistency|동일|같은|transform)/i.test(pseudocode)) missing.push('consistency');
    return missing;
  }
}

// ==================== LLM 평가 (85점) ====================
export class LLMEvaluator {
  constructor(apiKey = null) {
    this.baseUrl = '/api/core/ai-proxy/';
  }

  /**
   * GPT API 호출 (백엔드 프록시 경유)
   */
  async callGPT(prompt, maxTokens = 1000) {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        model: 'gpt-4o',
        messages: [
          { role: 'system', content: 'You are an expert AI Architect. Respond ONLY with valid JSON.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.2,
        max_tokens: maxTokens,
        response_format: { type: 'json_object' }
      })
    });

    if (!response.ok) {
      throw new Error(`Proxy AI Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.content;
  }

  /**
   * Stage 2 - 추상화 평가 (15점)
   */
  async evaluateAbstraction(pseudocode) {
    const prompt = `당신은 데이터 사이언스 교육 플랫폼의 멘토입니다. 학생이 작성한 의사코드를 평가합니다.

[학습자의 의사코드]
${pseudocode}

[평가 기준]
다음 3가지 핵심 개념이 논리 흐름에 반영되었는지 평가하십시오. (정확한 전문 용어가 없어도, 개념이 서술되어 있다면 점수를 부여하십시오)
1. 격리 (Isolation): 학습용 데이터와 평가용 데이터를 분리한다는 개념 (5점)
2. 기준점 (Anchor): 통계량(fit)을 학습 데이터에서만 추출한다는 개념 (5점)
3. 일관성 (Consistency): 동일한 변환 기준을 운영/테스트 데이터에도 적용한다는 개념 (5점)

* 힌트: 한국어 자연어 서술 위주라도 논리가 맞다면 점수를 넉넉히 부여하세요.

[출력 형식 - JSON만]
{
  "isolation_score": 0-5,
  "anchor_score": 0-5,
  "consistency_score": 0-5,
  "total_score": 0-15,
  "one_line_comment": "논리 구조에 대한 20자 내외의 격려하는 총평",
  "feedback": "구체적인 개선점이나 칭찬 1문장"
}`;

    const response = await this.callGPT(prompt, 500);
    return this.parseJSON(response);
  }

  /**
   * Stage 3 - 설계력 평가 (25점)
   */
  async evaluateDesign(pseudocode, pythonCode) {
    const codeSection = pythonCode
      ? `[변환된 Python 코드]\n${pythonCode}`
      : '[변환된 Python 코드]\n(코드 변환 결과 없음 - 의사코드만으로 평가)';

    const prompt = `당신은 친절한 MLOps 시니어 엔지니어입니다. 주니어의 설계를 평가하고 조언합니다.

[의사코드]
${pseudocode}

${codeSection}

[평가 기준]
전처리 파이프라인의 논리적 흐름을 관대하게 평가하십시오. 코드가 완벽하지 않아도 의도가 명확하면 부분 점수를 부여하십시오. (25점)
- 데이터 분할 시점의 적절성 (8점)
- Fit과 Transform의 명확한 분리 의도 (8점)
- 운영/테스트 환경을 고려한 로직 (9점)

[출력 형식 - JSON만]
{
  "split_timing": 0-8,
  "fit_transform_separation": 0-8,
  "production_consistency": 0-9,
  "total_score": 0-25,
  "one_line_comment": "설계 흐름에 대한 20자 내외의 피드백",
  "feedback": "상세 피드백 1문장"
}`;

    const response = await this.callGPT(prompt, 600);
    return this.parseJSON(response);
  }

  /**
   * Stage 3 - 구현력 평가 (10점)
   */
  async evaluateImplementation(pseudocode, pythonCode) {
    const codeSection = pythonCode
      ? `[변환된 코드]\n${pythonCode}`
      : '[변환된 코드]\n(코드 변환 결과 없음 - 의사코드만으로 평가)';

    const prompt = `당신은 코드 리뷰어입니다.

[의사코드]
${pseudocode}

${codeSection}

[평가 기준]
Python 코드가 실행 가능한 형태를 갖추었는지 평가하십시오. (10점)
- 문법적 완성도 (3점) - 실행만 된다면 점수 부여
- 주요 라이브러리(Pandas, Sklearn 등) 활용 여부 (4점)
- 로직의 실행 가능성 (3점)

* 코드가 없을 경우 의사코드의 구현 가능성으로 판단하세요.

[출력 형식 - JSON만]
{
  "syntax_correctness": 0-3,
  "library_usage": 0-4,
  "executability": 0-3,
  "total_score": 0-10,
  "one_line_comment": "구현 완성도에 대한 짧은 코멘트",
  "feedback": "상세 피드백 1문장"
}`;

    const response = await this.callGPT(prompt, 400);
    return this.parseJSON(response);
  }

  /**
   * Stage 3 - 예외처리 평가 (15점)
   */
  async evaluateEdgeCase(deepDiveAnswer, scenario) {
    const questionText = scenario?.question || '데이터 누수 방지 전략에 대해 서술하시오.';
    const intentText   = scenario?.intent   || '논리적 타당성과 실무 적용 가능성을 평가';

    const prompt = `당신은 MLOps 실전 전문가입니다.

[질문 시나리오]
${questionText}

[학습자 답변]
${deepDiveAnswer || '(답변 없음)'}

[평가 기준]
${intentText} (15점)
* 키워드 매칭보다는 답변의 논리적 타당성과 문제 해결 의지를 높게 평가하십시오.
* 답변이 없거나 매우 짧으면 0~3점을 부여하십시오.

[출력 형식 - JSON만]
{
  "keyword_match_score": 0-8,
  "practical_insight_score": 0-7,
  "total_score": 0-15,
  "one_line_comment": "위기 대응력에 대한 짧은 코멘트",
  "feedback": "상세 피드백 1문장"
}`;

    const response = await this.callGPT(prompt, 500);
    return this.parseJSON(response);
  }

  /**
   * Stage 5 - 정합성 평가 (20점)
   */
  async evaluateConsistency(allAnswers) {
    const prompt = `당신은 최종 검증 전문가입니다. 학생의 전체적인 학습 과정을 평가합니다.

[전체 답변]
Stage 2 (의사코드): ${allAnswers.stage2 || '(없음)'}
Stage 3 (Python 코드): ${allAnswers.stage3 || '(없음)'}
Deep Dive (심화 답변): ${allAnswers.deepdive || '(없음)'}

[평가 기준]
전체 과정에서 '데이터 누수 방지'라는 목표를 달성하기 위해 노력했는가? (20점)
- 원칙을 지키려는 의도가 보이는가? (10점)
- 앞뒤 논리가 크게 모순되지 않는가? (10점)

* 완벽함보다는 '일관된 시도'에 높은 점수를 주십시오.

[출력 형식 - JSON만]
{
  "principle_consistency": 0-10,
  "logical_coherence": 0-10,
  "total_score": 0-20,
  "one_line_comment": "전체적인 조화에 대한 격려의 코멘트",
  "feedback": "상세 피드백 1문장"
}`;

    const response = await this.callGPT(prompt, 500);
    return this.parseJSON(response);
  }

  /**
   * JSON 파싱 (안전)
   */
  parseJSON(text) {
    try {
      const cleaned = text.replace(/```json\n?|```\n?/g, '').trim();
      return JSON.parse(cleaned);
    } catch (err) {
      console.error('[EvaluationEngine] JSON 파싱 실패:', err, '\n원본:', text);
      // 파싱 실패 시 0점 fallback 반환 (필드 구조 유지)
      return {
        total_score: 0,
        one_line_comment: '평가 중 오류가 발생했습니다.',
        feedback: '잠시 후 다시 시도해 주세요.',
        error: true
      };
    }
  }
}

// ==================== 종합 평가 시스템 ====================
export class ComprehensiveEvaluator {
  constructor(apiKey) {
    this.ruleEvaluator = new RuleBasedEvaluator();
    this.llmEvaluator = new LLMEvaluator(apiKey);
  }

  /**
   * 전체 평가 실행
   */
  async evaluate(userAnswers) {
    const results = {
      stage1: { score: 0, passed: true },
      stage2: {},
      stage3: {},
      stage5: {},
      total: 0,
      metrics: {}
    };

    // Stage 2: 의사코드 평가 (30점) - rule + abstraction 병렬
    const [ruleResult, abstractionResult] = await Promise.all([
      this.ruleEvaluator.evaluateStage2Rule(userAnswers.pseudocode),
      this.llmEvaluator.evaluateAbstraction(userAnswers.pseudocode)
    ]);

    // [수정] one_line_comment, feedback 필드 누락 없이 모두 저장
    results.stage2 = {
      rule:        ruleResult.score,
      abstraction: abstractionResult.total_score ?? 0,
      total:       ruleResult.score + (abstractionResult.total_score ?? 0),
      one_line_comment: abstractionResult.one_line_comment || '',
      feedback: {
        rule:        ruleResult.feedback,
        abstraction: abstractionResult.feedback || ''
      },
      critical: ruleResult.critical
    };

    // Stage 3: 구현 검증 (50점) - 3개 병렬
    const [designResult, implResult, edgeCaseResult] = await Promise.all([
      this.llmEvaluator.evaluateDesign(userAnswers.pseudocode, userAnswers.pythonCode),
      this.llmEvaluator.evaluateImplementation(userAnswers.pseudocode, userAnswers.pythonCode),
      this.llmEvaluator.evaluateEdgeCase(userAnswers.deepdive, userAnswers.deepdiveScenario)
    ]);

    // [수정] 각 평가의 one_line_comment를 개별 필드로 저장
    results.stage3 = {
      design:         designResult.total_score ?? 0,
      implementation: implResult.total_score   ?? 0,
      edgeCase:       edgeCaseResult.total_score ?? 0,
      total: (designResult.total_score ?? 0) + (implResult.total_score ?? 0) + (edgeCaseResult.total_score ?? 0),
      one_line_comment: {
        design:         designResult.one_line_comment   || '',
        implementation: implResult.one_line_comment     || '',
        edgeCase:       edgeCaseResult.one_line_comment || ''
      },
      feedback: {
        design:         designResult.feedback   || '',
        implementation: implResult.feedback     || '',
        edgeCase:       edgeCaseResult.feedback || ''
      }
    };

    // Stage 5: 정합성 (20점)
    const consistencyResult = await this.llmEvaluator.evaluateConsistency({
      stage2:   userAnswers.pseudocode,
      stage3:   userAnswers.pythonCode,
      deepdive: userAnswers.deepdive
    });

    results.stage5 = {
      consistency:     consistencyResult.total_score ?? 0,
      total:           consistencyResult.total_score ?? 0,
      one_line_comment: consistencyResult.one_line_comment || '',
      feedback:         consistencyResult.feedback         || ''
    };

    // 총점 계산
    results.total = results.stage2.total + results.stage3.total + results.stage5.total;

    // Critical Error 페널티 (30% 감점)
    if (ruleResult.critical) {
      results.total = Math.max(0, Math.round(results.total * 0.7));
      results.stage2.feedback.rule.push({
        type: 'critical',
        message: '⚠️ 치명적 패턴이 감지되어 총점이 조정되었습니다.'
      });
    }

    // 5대 지표 계산
    results.metrics = this.calculateMetrics(results);

    return results;
  }

  /**
   * 5대 지표 계산
   * [수정] LLM이 반환한 one_line_comment를 올바른 경로에서 참조
   */
  calculateMetrics(results) {
    return {
      abstraction: {
        name:       '추상화 (Abstraction)',
        score:      results.stage2.abstraction ?? 0,
        max:        15,
        percentage: Math.round(((results.stage2.abstraction ?? 0) / 15) * 100),
        comment:    results.stage2.one_line_comment || results.stage2.feedback?.abstraction || '논리 구조의 명확성 분석'
      },
      implementation: {
        name:       '구현력 (Implementation)',
        score:      results.stage3.implementation ?? 0,
        max:        10,
        percentage: Math.round(((results.stage3.implementation ?? 0) / 10) * 100),
        comment:    results.stage3.one_line_comment?.implementation || results.stage3.feedback?.implementation || '파이썬 코드 변환 정확도'
      },
      design: {
        name:       '설계력 (Design)',
        score:      results.stage3.design ?? 0,
        max:        25,
        percentage: Math.round(((results.stage3.design ?? 0) / 25) * 100),
        comment:    results.stage3.one_line_comment?.design || results.stage3.feedback?.design || '파이프라인 흐름의 타당성'
      },
      edgeCase: {
        name:       '예외처리 (Edge Case)',
        score:      results.stage3.edgeCase ?? 0,
        max:        15,
        percentage: Math.round(((results.stage3.edgeCase ?? 0) / 15) * 100),
        comment:    results.stage3.one_line_comment?.edgeCase || results.stage3.feedback?.edgeCase || '심화 시나리오 대응 능력'
      },
      consistency: {
        name:       '정합성 (Consistency)',
        score:      results.stage5.consistency ?? 0,
        max:        20,
        percentage: Math.round(((results.stage5.consistency ?? 0) / 20) * 100),
        comment:    results.stage5.one_line_comment || results.stage5.feedback || '전체 설계의 일관성 유지'
      }
    };
  }

  /**
   * 꼬리질문 필요 여부 확인
   */
  needsFollowUp(pseudocode) {
    return this.ruleEvaluator.getMissingKeywords(pseudocode);
  }
}
