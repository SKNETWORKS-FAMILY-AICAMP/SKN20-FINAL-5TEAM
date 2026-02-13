/**
 * 최종 진단 리포트 생성 시스템
 * LLM 기반 정밀 피드백
 */

export class ReportGenerator {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://api.anthropic.com/v1/messages';
  }

  /**
   * 최종 리포트 생성
   */
  async generateFinalReport(metrics, totalScore) {
    const prompt = this.buildReportPrompt(metrics, totalScore);
    
    try {
      const response = await this.callClaude(prompt, 1500);
      return this.parseReport(response);
    } catch (error) {
      console.error('리포트 생성 실패:', error);
      return this.getFallbackReport(metrics, totalScore);
    }
  }

  /**
   * 리포트 생성 프롬프트
   */
  buildReportPrompt(metrics, totalScore) {
    const { strongest, weakest } = this.analyzeMetrics(metrics);

    return `# [Role]
너는 데이터 사이언스 교육 플랫폼의 '최종 기술 면접관'이자 '수석 멘토'이다. 
학습자가 수행한 데이터 전처리 파이프라인 설계 결과(5개 지표 점수)를 분석하여, 객관적이고 엔지니어링 중심의 피드백을 제공하라.

# [Input Data]
총점: ${totalScore}/100점

5대 지표 점수:
1. 설계력(Design): ${metrics.design.score}/${metrics.design.max}점 (${metrics.design.percentage}%)
2. 정합성(Consistency): ${metrics.consistency.score}/${metrics.consistency.max}점 (${metrics.consistency.percentage}%)
3. 구현력(Implementation): ${metrics.implementation.score}/${metrics.implementation.max}점 (${metrics.implementation.percentage}%)
4. 예외처리(Edge Case): ${metrics.edgeCase.score}/${metrics.edgeCase.max}점 (${metrics.edgeCase.percentage}%)
5. 추상화(Abstraction): ${metrics.abstraction.score}/${metrics.abstraction.max}점 (${metrics.abstraction.percentage}%)

최강 지표: ${strongest.name} (${strongest.percentage}%)
최약 지표: ${weakest.name} (${weakest.percentage}%)

# [Step-by-Step Logic]
1. 분석: 5개 지표 중 점수가 가장 높은 '최강 지표'와 가장 낮은 '최약 지표'를 선정한다. (동점일 경우 중요도가 높은 설계력 > 정합성 순으로 우선순위 결정)
2. 페르소나 매칭: 아래 [Persona Bank]에서 점수 분포에 맞는 명칭을 하나 선택한다.
3. 총평 작성: 학습자의 전체적인 설계 수준을 시니어 엔지니어의 시각에서 한 문장으로 요약한다.
4. 강점/약점 서술: [Keyword Bank]의 용어를 사용하여 구체적인 공학적 근거를 제시한다.

# [Persona Bank]
- (설계/정합성 높음, 예외처리 낮음): "원칙 중심의 이론가"
- (구현력/설계력 높음, 추상화 낮음): "손이 빠른 실무형 코더"
- (예외처리/추상화 높음, 구현력 낮음): "통찰력 있는 기획자"
- (전체 점수 80점 이상): "완벽한 방어기제의 철옹성 설계자"
- (전체 점수 50점 미만): "기초를 다지는 성장기 분석가"

# [Keyword Bank (반드시 활용)]
- 긍정: 데이터 격리 완벽, 정보 유출 차단, 파이프라인 정석, 기준점 고정, 일관된 변환
- 부정: 데이터 누수(Leakage) 위험, 통계적 오염, 훈련/테스트 혼동, 운영 환경 병목, 설계의 경직성

# [Output Format - 반드시 이 양식을 준수할 것]
### 최종 진단: {Persona 명칭}
**"{한 줄 총평}"**

---

#### 🧐 지표별 정밀 분석
* **강점 [{최강 지표}]:** {해당 점수가 높은 이유를 'Keyword Bank'를 써서 2문장으로 서술}
* **보완점 [{최약 지표}]:** {해당 점수가 낮은 이유와 실무에서 발생할 위험을 2문장으로 서술}

#### 🚀 마스터의 원포인트 레슨
{최약 지표를 개선하기 위한 학습 방향과 '사고방식'에 대한 조언 1문장}

중요: 반드시 위 형식을 정확히 지켜서 출력하라. 추가 설명이나 전처리 없이 바로 "### 최종 진단:"부터 시작하라.`;
  }

  /**
   * 최강/최약 지표 분석
   */
  analyzeMetrics(metrics) {
    const metricsList = Object.entries(metrics).map(([key, value]) => ({
      key,
      name: value.name,
      score: value.score,
      max: value.max,
      percentage: value.percentage
    }));

    // 중요도 가중치
    const priorities = {
      design: 5,
      consistency: 4,
      edgeCase: 3,
      abstraction: 2,
      implementation: 1
    };

    // 최강 지표
    const strongest = metricsList.reduce((max, curr) => {
      if (curr.percentage > max.percentage) return curr;
      if (curr.percentage === max.percentage && priorities[curr.key] > priorities[max.key]) {
        return curr;
      }
      return max;
    });

    // 최약 지표
    const weakest = metricsList.reduce((min, curr) => {
      if (curr.percentage < min.percentage) return curr;
      if (curr.percentage === min.percentage && priorities[curr.key] > priorities[min.key]) {
        return curr;
      }
      return min;
    });

    return { strongest, weakest };
  }

  /**
   * Claude API 호출
   */
  async callClaude(prompt, maxTokens = 1500) {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: maxTokens,
        temperature: 0.3,  // 일관성 향상
        messages: [{
          role: 'user',
          content: prompt
        }]
      })
    });

    if (!response.ok) {
      throw new Error(`API 호출 실패: ${response.status}`);
    }

    const data = await response.json();
    return data.content[0].text;
  }

  /**
   * 리포트 파싱
   */
  parseReport(text) {
    // ### 최종 진단: 부터 추출
    const match = text.match(/### 최종 진단:(.+)/s);
    if (!match) {
      throw new Error('리포트 형식 오류');
    }

    const content = match[0];

    // 섹션 파싱
    const personaMatch = content.match(/### 최종 진단:\s*(.+?)\n/);
    const summaryMatch = content.match(/\*\*"(.+?)"\*\*/);
    const strengthMatch = content.match(/\* \*\*강점 \[(.+?)\]:\*\* (.+?)(?=\n\* \*\*보완점|\n####)/s);
    const weaknessMatch = content.match(/\* \*\*보완점 \[(.+?)\]:\*\* (.+?)(?=\n####)/s);
    const lessonMatch = content.match(/#### 🚀 마스터의 원포인트 레슨\n(.+?)$/s);

    return {
      persona: personaMatch ? personaMatch[1].trim() : '분석 중',
      summary: summaryMatch ? summaryMatch[1].trim() : '',
      strength: {
        metric: strengthMatch ? strengthMatch[1].trim() : '',
        feedback: strengthMatch ? strengthMatch[2].trim() : ''
      },
      weakness: {
        metric: weaknessMatch ? weaknessMatch[1].trim() : '',
        feedback: weaknessMatch ? weaknessMatch[2].trim() : ''
      },
      lesson: lessonMatch ? lessonMatch[1].trim() : '',
      rawReport: content
    };
  }

  /**
   * Fallback 리포트 (API 실패 시)
   */
  getFallbackReport(metrics, totalScore) {
    const { strongest, weakest } = this.analyzeMetrics(metrics);
    
    let persona = '기초를 다지는 성장기 분석가';
    if (totalScore >= 80) {
      persona = '완벽한 방어기제의 철옹성 설계자';
    } else if (totalScore >= 60) {
      persona = '원칙 중심의 이론가';
    }

    return {
      persona,
      summary: `총점 ${totalScore}점으로 데이터 전처리 파이프라인에 대한 ${totalScore >= 70 ? '우수한' : '기본적인'} 이해를 보여주셨습니다.`,
      strength: {
        metric: strongest.name,
        feedback: `${strongest.name} 부분에서 ${strongest.percentage}%의 높은 점수를 기록하여 해당 영역의 이해도가 뛰어납니다. 파이프라인 정석을 잘 이해하고 계십니다.`
      },
      weakness: {
        metric: weakest.name,
        feedback: `${weakest.name} 부분에서 ${weakest.percentage}%로 보완이 필요합니다. 실무 환경에서 이 부분의 약점은 데이터 누수 위험으로 이어질 수 있습니다.`
      },
      lesson: `${weakest.name} 향상을 위해 관련 실전 예제와 사례 연구에 집중하세요.`,
      rawReport: ''
    };
  }

  /**
   * 레이더 차트 데이터 생성
   */
  generateRadarChartData(metrics) {
    return {
      labels: [
        metrics.abstraction.name,
        metrics.implementation.name,
        metrics.design.name,
        metrics.edgeCase.name,
        metrics.consistency.name
      ],
      datasets: [{
        label: '당신의 점수',
        data: [
          metrics.abstraction.percentage,
          metrics.implementation.percentage,
          metrics.design.percentage,
          metrics.edgeCase.percentage,
          metrics.consistency.percentage
        ],
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgb(54, 162, 235)',
        pointBackgroundColor: 'rgb(54, 162, 235)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(54, 162, 235)'
      }]
    };
  }

  /**
   * 등급 계산
   */
  calculateGrade(totalScore) {
    if (totalScore >= 90) return { grade: 'S', color: '#FFD700', description: '완벽' };
    if (totalScore >= 80) return { grade: 'A', color: '#4CAF50', description: '우수' };
    if (totalScore >= 70) return { grade: 'B', color: '#2196F3', description: '양호' };
    if (totalScore >= 60) return { grade: 'C', color: '#FF9800', description: '보통' };
    if (totalScore >= 50) return { grade: 'D', color: '#FF5722', description: '미흡' };
    return { grade: 'F', color: '#F44336', description: '재학습 필요' };
  }
}

/**
 * 완전한 학습 리포트 생성
 */
export async function generateCompleteLearningReport(evaluationResults, apiKey) {
  const generator = new ReportGenerator(apiKey);
  
  // 1. 최종 진단 리포트
  const finalReport = await generator.generateFinalReport(
    evaluationResults.metrics,
    evaluationResults.total
  );

  // 2. 레이더 차트 데이터
  const radarData = generator.generateRadarChartData(evaluationResults.metrics);

  // 3. 등급
  const grade = generator.calculateGrade(evaluationResults.total);

  // 4. 추천 콘텐츠
  const { weakest } = generator.analyzeMetrics(evaluationResults.metrics);
  const { recommendContent } = await import('./learningResources.js');
  const recommendedContent = recommendContent(weakest.key, evaluationResults.total);

  return {
    finalReport,
    radarData,
    grade,
    recommendedContent,
    metrics: evaluationResults.metrics,
    totalScore: evaluationResults.total,
    timestamp: new Date().toISOString()
  };
}
