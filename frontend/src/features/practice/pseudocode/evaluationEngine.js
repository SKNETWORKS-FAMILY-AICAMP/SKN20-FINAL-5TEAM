/**
 * 평가 엔진 - LLM 85% + Rule 15%
 * Stage별 점수 계산 및 종합 평가
 */

// ==================== Rule 기반 평가 (15점) ====================
export class RuleBasedEvaluator {
  constructor() {
    this.requiredKeywords = ['격리', '기준점', '일관성', 'train', 'test', 'fit', 'transform'];
    this.criticalPatterns = [
      {
        pattern: /(전체|모든|전부)\s*데이터\s*.*(fit|학습시키|학습시킴)\s*\(/i,
        penalty: -50,
        error: '🚨 치명적: 전체 데이터로 fit() 호출 감지'
      },
      {
        pattern: /(test|테스트)\s*데이터\s*.*(fit|학습시키|학습시킴)\s*\(/i,
        penalty: -50,
        error: '🚨 치명적: 테스트 데이터로 fit() 호출 감지'
      }
    ];
  }

  /**
   * Stage 2 - Rule 기반 평가 (15점)
   */
  evaluateStage2Rule(pseudocode) {
    let score = 15;
    const feedback = [];

    // 1. 치명적 패턴 검사 (-50점)
    for (const { pattern, penalty, error } of this.criticalPatterns) {
      if (pattern.test(pseudocode)) {
        score = 0;
        feedback.push({ type: 'critical', message: error });
        return { score: 0, feedback, critical: true };
      }
    }

    // 2. 필수 키워드 체크 (각 2점)
    const keywordScores = this.requiredKeywords.map(keyword => {
      const regex = new RegExp(keyword, 'i');
      const found = regex.test(pseudocode);
      return {
        keyword,
        found,
        score: found ? 2 : 0
      };
    });

    const keywordScore = Math.min(
      keywordScores.reduce((sum, k) => sum + k.score, 0),
      10  // 최대 10점
    );

    // 3. 순서 검증 (5점)
    const orderScore = this.checkOrder(pseudocode);

    score = keywordScore + orderScore;

    feedback.push({
      type: 'success',
      message: `필수 키워드: ${keywordScores.filter(k => k.found).length}/${this.requiredKeywords.length}`,
      details: keywordScores
    });

    return { score, feedback, critical: false };
  }

  /**
   * 순서 검증
   */
  checkOrder(text) {
    const splitIndex = this.findPatternIndex(text, /분리|split|격리/i);
    const fitIndex = this.findPatternIndex(text, /fit|학습시키/i);
    const transformIndex = this.findPatternIndex(text, /transform|변환/i);

    if (splitIndex === -1 || fitIndex === -1) {
      return 0;
    }

    // 분리 → Fit → Transform 순서
    if (splitIndex < fitIndex) {
      if (transformIndex === -1 || fitIndex < transformIndex) {
        return 5;
      }
      return 3;
    }

    return 0;
  }

  findPatternIndex(text, pattern) {
    const match = text.match(pattern);
    return match ? match.index : -1;
  }

  /**
   * 부족한 키워드 감지
   */
  getMissingKeywords(pseudocode) {
    const missing = [];

    if (!/(격리|분리|split|나누)/i.test(pseudocode)) {
      missing.push('isolation');
    }
    if (!/(기준점|anchor|fit|학습)/i.test(pseudocode)) {
      missing.push('anchor');
    }
    if (!/(일관성|consistency|동일|같은)/i.test(pseudocode)) {
      missing.push('consistency');
    }

    return missing;
  }
}

// ==================== LLM 평가 (85점) ====================
export class LLMEvaluator {
  constructor(apiKey = null) {
    // 백엔드 프록시를 사용하므로 클라이언트 API 키는 부차적입니다.
    this.baseUrl = '/api/core/ai-proxy/';
  }

  /**
   * GPT API 호출 (백엔드 프록시 경유)
   */
  async callGPT(prompt, maxTokens = 1000) {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 세션 인증이 필요할 경우를 대비해 기존 인증 정보를 포함할 수 있음
      },
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
      throw new Error(`Proxy AI Error: ${response.statusText}`);
    }

    const data = await response.json();
    // 백엔드 프록시는 { content: "..." } 형식으로 반환함
    return data.content;
  }

  /**
   * Stage 2 - 추상화 평가 (15점)
   */
  async evaluateAbstraction(pseudocode) {
    const prompt = `당신은 데이터 사이언스 교육 플랫폼의 평가 전문가입니다.

[학습자의 의사코드]
${pseudocode}

[평가 기준]
다음 3가지 키워드를 사용하여 논리를 구조화했는가? (각 5점)
1. 격리 (Isolation): 데이터를 나누는 시점
2. 기준점 (Anchor): 통계량(fit)을 추출할 대상
3. 일관성 (Consistency): 학습과 운영 환경의 동일한 변환 방식

[출력 형식 - JSON만]
{
  "isolation_score": 0-5,
  "anchor_score": 0-5,
  "consistency_score": 0-5,
  "total_score": 0-15,
  "one_line_comment": "논리 구조에 대한 15자 내외의 아주 짧은 총평",
  "feedback": "상세 피드백 1문장"
}`;

    const response = await this.callGPT(prompt, 500);
    return this.parseJSON(response);
  }

  /**
   * Stage 3 - 설계력 평가 (25점)
   */
  async evaluateDesign(pseudocode, pythonCode) {
    const prompt = `당신은 MLOps 시니어 엔지니어입니다.

[의사코드]
${pseudocode}

[변환된 Python 코드]
${pythonCode}

[평가 기준]
전처리 파이프라인의 논리적 흐름과 순서가 올바른가? (25점)
- 데이터 분할 시점 (8점)
- Fit/Transform 분리 (8점)
- 운영 환경 일관성 (9점)

[출력 형식 - JSON만]
{
  "split_timing": 0-8,
  "fit_transform_separation": 0-8,
  "production_consistency": 0-9,
  "total_score": 0-25,
  "one_line_comment": "설계 타당성에 대한 15자 내외의 아주 짧은 총평",
  "feedback": "상세 피드백 1문장"
}`;

    const response = await this.callGPT(prompt, 600);
    return this.parseJSON(response);
  }

  /**
   * Stage 3 - 구현력 평가 (10점)
   */
  async evaluateImplementation(pseudocode, pythonCode) {
    const prompt = `당신은 Python 코드 검수 전문가입니다.

[의사코드]
${pseudocode}

[변환된 코드]
${pythonCode}

[평가 기준]
의사코드가 실제 실행 가능한 Python으로 정확히 변환되었는가? (10점)
- 문법 정확성 (3점)
- 라이브러리 사용 (4점)
- 실행 가능성 (3점)

[출력 형식 - JSON만]
{
  "syntax_correctness": 0-3,
  "library_usage": 0-4,
  "executability": 0-3,
  "total_score": 0-10,
  "one_line_comment": "코드 품질에 대한 15자 내외의 아주 짧은 총평",
  "feedback": "상세 피드백 1문장"
}`;

    const response = await this.callGPT(prompt, 400);
    return this.parseJSON(response);
  }

  /**
   * Stage 3 - 예외처리 평가 (15점) - Deep Dive 답변 평가
   */
  async evaluateEdgeCase(deepDiveAnswer, scenario) {
    const prompt = `당신은 MLOps 실전 전문가입니다.

[질문 시나리오]
${scenario.question}

[학습자 답변]
${deepDiveAnswer}

[평가 기준]
${scenario.intent} (15점)
핵심 키워드: ${scenario.scoringKeywords?.join(', ') || '관련 키워드'}

[출력 형식 - JSON만]
{
  "keyword_match_score": 0-8,
  "practical_insight_score": 0-7,
  "total_score": 0-15,
  "one_line_comment": "위기 대응력에 대한 15자 내외의 아주 짧은 총평",
  "feedback": "상세 피드백 1문장"
}`;

    const response = await this.callGPT(prompt, 500);
    return this.parseJSON(response);
  }

  /**
   * Stage 5 - 정합성 평가 (20점)
   */
  async evaluateConsistency(allAnswers) {
    const prompt = `당신은 최종 검증 전문가입니다.

[전체 답변]
Stage 2: ${allAnswers.stage2}
Stage 3: ${allAnswers.stage3}
Deep Dive: ${allAnswers.deepdive}

[평가 기준]
전체 과정에서 '데이터 누수 방지 원칙'이 일관되게 유지되었는가? (20점)
- 원칙 일관성 (10점)
- 논리 모순 없음 (10점)

[출력 형식 - JSON만]
{
  "principle_consistency": 0-10,
  "logical_coherence": 0-10,
  "total_score": 0-20,
  "one_line_comment": "전체 조화에 대한 15자 내외의 아주 짧은 총평",
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
      // ```json 제거
      const cleaned = text.replace(/```json\n?|```\n?/g, '').trim();
      return JSON.parse(cleaned);
    } catch (err) {
      console.error('JSON 파싱 실패:', err, text);
      return { error: 'JSON 파싱 실패' };
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
      stage1: { score: 0, passed: true },  // 객관식은 점수 없음
      stage2: {},
      stage3: {},
      stage5: {},
      total: 0,
      metrics: {}
    };

    // Stage 2: 의사코드 평가 (30점)
    const [ruleResult, abstractionResult] = await Promise.all([
      this.ruleEvaluator.evaluateStage2Rule(userAnswers.pseudocode),
      this.llmEvaluator.evaluateAbstraction(userAnswers.pseudocode)
    ]);

    results.stage2 = {
      rule: ruleResult.score,           // 15점
      abstraction: abstractionResult.total_score,  // 15점
      total: ruleResult.score + abstractionResult.total_score,
      feedback: {
        rule: ruleResult.feedback,
        abstraction: abstractionResult.feedback
      },
      critical: ruleResult.critical
    };

    // 치명적 오류 시 즉시 종료 (단, 리포트 생성을 위해 기본 지표는 계산)
    if (ruleResult.critical) {
      results.total = 0;
      results.criticalError = true;
      results.stage2 = {
        rule: 0,
        abstraction: 0,
        total: 0,
        feedback: ruleResult.feedback
      };
      results.stage3 = { design: 0, implementation: 0, edgeCase: 0, total: 0 };
      results.stage5 = { consistency: 0, total: 0 };
      results.metrics = this.calculateMetrics(results);
      return results;
    }

    // Stage 3: 구현 검증 (50점)
    const [designResult, implResult, edgeCaseResult] = await Promise.all([
      this.llmEvaluator.evaluateDesign(userAnswers.pseudocode, userAnswers.pythonCode),
      this.llmEvaluator.evaluateImplementation(userAnswers.pseudocode, userAnswers.pythonCode),
      this.llmEvaluator.evaluateEdgeCase(userAnswers.deepdive, userAnswers.deepdiveScenario)
    ]);

    results.stage3 = {
      design: designResult.total_score,        // 25점
      implementation: implResult.total_score,  // 10점
      edgeCase: edgeCaseResult.total_score,    // 15점
      total: designResult.total_score + implResult.total_score + edgeCaseResult.total_score,
      feedback: {
        design: designResult.feedback,
        implementation: implResult.feedback,
        edgeCase: edgeCaseResult.feedback
      }
    };

    // Stage 5: 정합성 (20점)
    const consistencyResult = await this.llmEvaluator.evaluateConsistency({
      stage2: userAnswers.pseudocode,
      stage3: userAnswers.pythonCode,
      deepdive: userAnswers.deepdive
    });

    results.stage5 = {
      consistency: consistencyResult.total_score,  // 20점
      total: consistencyResult.total_score,
      feedback: consistencyResult.feedback
    };

    // 총점 계산
    results.total = results.stage2.total + results.stage3.total + results.stage5.total;

    // 5대 지표 계산
    results.metrics = this.calculateMetrics(results);

    return results;
  }

  /**
   * 5대 지표 계산
   */
  calculateMetrics(results) {
    return {
      abstraction: {
        name: '추상화 (Abstraction)',
        score: results.stage2.abstraction,
        max: 15,
        percentage: Math.round((results.stage2.abstraction / 15) * 100),
        comment: results.stage2.one_line_comment || results.stage2.feedback?.abstraction || '논리 구조의 명확성 분석'
      },
      implementation: {
        name: '구현력 (Implementation)',
        score: results.stage3.implementation,
        max: 10,
        percentage: Math.round((results.stage3.implementation / 10) * 100),
        comment: results.stage3.one_line_comment || results.stage3.feedback?.implementation || '파이썬 코드 변환 정확도'
      },
      design: {
        name: '설계력 (Design)',
        score: results.stage3.design,
        max: 25,
        percentage: Math.round((results.stage3.design / 25) * 100),
        comment: results.stage3.one_line_comment || results.stage3.feedback?.design || '파이프라인 흐름의 타당성'
      },
      edgeCase: {
        name: '예외처리 (Edge Case)',
        score: results.stage3.edgeCase,
        max: 15,
        percentage: Math.round((results.stage3.edgeCase / 15) * 100),
        comment: results.stage3.one_line_comment || results.stage3.feedback?.edgeCase || '심화 시나리오 대응 능력'
      },
      consistency: {
        name: '정합성 (Consistency)',
        score: results.stage5.consistency,
        max: 20,
        percentage: Math.round((results.stage5.consistency / 20) * 100),
        comment: results.stage5.one_line_comment || results.stage5.feedback || '전체 설계의 일관성 유지'
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
