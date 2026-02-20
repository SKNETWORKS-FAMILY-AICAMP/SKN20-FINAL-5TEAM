/**
 * 최종 진단 리포트 생성 시스템
 * LLM 기반 정밀 피드백
 * 수정일: 2026-02-20
 */

export class ReportGenerator {
  constructor(apiKey = null) {
    this.baseUrl = '/api/core/ai-proxy/';
  }

  async generateFinalReport(metrics, totalScore) {
    const prompt = this.buildReportPrompt(metrics, totalScore);
    try {
      const response = await this.callGPT(prompt, 1500);
      return this.parseReport(response);
    } catch (error) {
      console.error('[ReportGenerator] 리포트 생성 실패:', error);
      return this.getFallbackReport(metrics, totalScore);
    }
  }

  buildReportPrompt(metrics, totalScore) {
    const { strongest, weakest } = this.analyzeMetrics(metrics);

    return `# [Role]
너는 데이터 사이언스 교육 플랫폼의 '최종 기술 면접관'이자 '수석 멘토'이다. 
학습자가 수행한 데이터 전처리 파이프라인 설계 결과(5개 지표 점수)를 분석하여, 객관적이고 엔지니어링 중심의 피드백을 제공하라.

# [Input Data]
총점: ${totalScore}/100점
최강 지표: ${strongest?.name || '분석 중'} (${strongest?.percentage || 0}%)
최약 지표: ${weakest?.name || '분석 중'} (${weakest?.percentage || 0}%)

5대 지표 점수 상세:
1. 설계력(Design): ${metrics.design?.score ?? 0}/${metrics.design?.max ?? 0}점 (${metrics.design?.percentage ?? 0}%)
2. 정합성(Consistency): ${metrics.consistency?.score ?? 0}/${metrics.consistency?.max ?? 0}점 (${metrics.consistency?.percentage ?? 0}%)
3. 구현력(Implementation): ${metrics.implementation?.score ?? 0}/${metrics.implementation?.max ?? 0}점 (${metrics.implementation?.percentage ?? 0}%)
4. 예외처리(Edge Case): ${metrics.edgeCase?.score ?? 0}/${metrics.edgeCase?.max ?? 0}점 (${metrics.edgeCase?.percentage ?? 0}%)
5. 추상화(Abstraction): ${metrics.abstraction?.score ?? 0}/${metrics.abstraction?.max ?? 0}점 (${metrics.abstraction?.percentage ?? 0}%)

# [Step-by-Step Logic]
1. 분석: 5개 지표 중 점수가 가장 높은 '최강 지표'와 가장 낮은 '최약 지표'를 선정한다. (동점일 경우 중요도가 높은 설계력 > 정합성 순으로 우선순위 결정)
2. 페르소나 매칭: 아래 [Persona Bank]에서 점수 분포에 맞는 명칭을 하나 선택한다.
3. 총평 작성: 학습자의 전체적인 설계 수준을 시니어 엔지니어의 시각에서 한 문장으로 요약한다.
4. 강점/약점 서술: [Keyword Bank]의 용어를 사용하여 구체적인 공학적 근거를 제시한다.

# [Persona Bank]
- (설계/정합성 높음, 예외처리 낮음): "원칙 중심의 이론가"
- (구현력/설계력 높음, 추상화 낮음): "손이 빠른 실무형 코더"
- (예외처리/추상화 높음, 구현력 낮음): "통찰력 있는 기획자"
- (전체 점수 90점 이상): "완벽한 방어기제의 철옹성 설계자"
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
* **감점 요인 및 분석:** {총점이 100점이 아닌 이유와 구체적인 감점 원인 1~2가지를 논리적으로 설명}

#### 🚀 마스터의 원포인트 레슨
{최약 지표를 개선하기 위한 학습 방향과 '사고방식'에 대한 조언 1문장}

중요: 반드시 위 형식을 정확히 지켜서 출력하라. 추가 설명이나 전처리 없이 바로 "### 최종 진단:"부터 시작하라.`;
  }

  analyzeMetrics(metrics) {
    const metricsList = Object.entries(metrics).map(([key, value]) => ({
      key,
      name:       value.name,
      score:      value.score,
      max:        value.max,
      percentage: value.percentage
    }));

    const priorities = { design: 5, consistency: 4, edgeCase: 3, abstraction: 2, implementation: 1 };

    const strongest = metricsList.length > 0
      ? metricsList.reduce((max, curr) => {
          if (curr.percentage > max.percentage) return curr;
          if (curr.percentage === max.percentage && (priorities[curr.key] ?? 0) > (priorities[max.key] ?? 0)) return curr;
          return max;
        })
      : { name: 'N/A', percentage: 0, key: 'none' };

    const weakest = metricsList.length > 0
      ? metricsList.reduce((min, curr) => {
          if (curr.percentage < min.percentage) return curr;
          if (curr.percentage === min.percentage && (priorities[curr.key] ?? 0) > (priorities[min.key] ?? 0)) return curr;
          return min;
        })
      : { name: 'N/A', percentage: 0, key: 'none' };

    return { strongest, weakest };
  }

  async callGPT(prompt, maxTokens = 1500) {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        model: 'gpt-4o',
        messages: [
          { role: 'system', content: 'You are a veteran AI architect providing final reports. Respond strictly in the requested format.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.3,
        max_tokens: maxTokens
      })
    });

    if (!response.ok) throw new Error(`API 호출 실패: ${response.status}`);
    const data = await response.json();
    return data.content;
  }

  parseReport(text) {
    if (!text || typeof text !== 'string') {
      console.warn('[ReportGenerator] parseReport: 빈 응답');
      throw new Error('빈 응답');
    }

    const startIdx = text.indexOf('### 최종 진단:');
    const content  = startIdx !== -1 ? text.slice(startIdx) : text;

    const personaMatch   = content.match(/###\s*최종\s*진단\s*:\s*(.+?)(?:\n|$)/);
    const summaryMatch   = content.match(/\*{0,2}"(.+?)"\*{0,2}/);
    const strengthMatch  = content.match(/강점\s*\[(.+?)\]\s*[:\uff1a]\s*([\s\S]+?)(?=\n[\*\-]\s*\*{0,2}보완점|\n[\*\-]\s*\*{0,2}감점|\n####|$)/);
    const weaknessMatch  = content.match(/보완점\s*\[(.+?)\]\s*[:\uff1a]\s*([\s\S]+?)(?=\n[\*\-]\s*\*{0,2}감점|\n####|$)/);
    const deductionMatch = content.match(/감점\s*요인[^:\uff1a]*[:\uff1a]\s*([\s\S]+?)(?=\n####|$)/);
    const lessonMatch    = content.match(/원포인트\s*레슨\s*\n+([\s\S]+?)(?=\n###|$)/);

    if (!personaMatch && !summaryMatch && !strengthMatch) {
      console.warn('[ReportGenerator] parseReport: 형식 오류\n원문:', text.slice(0, 300));
      throw new Error('리포트 형식 오류');
    }

    return {
      persona:  personaMatch  ? personaMatch[1].trim()  : '분석 완료',
      summary:  summaryMatch  ? summaryMatch[1].trim()  : '',
      strength: {
        metric:   strengthMatch ? strengthMatch[1].trim() : '',
        feedback: strengthMatch ? strengthMatch[2].trim() : ''
      },
      weakness: {
        metric:   weaknessMatch ? weaknessMatch[1].trim() : '',
        feedback: weaknessMatch ? weaknessMatch[2].trim() : ''
      },
      scoringAnalysis: deductionMatch ? deductionMatch[1].trim() : '',
      lesson:   lessonMatch   ? lessonMatch[1].trim()   : '',
      rawReport: content
    };
  }

  getFallbackReport(metrics, totalScore) {
    const { strongest, weakest } = this.analyzeMetrics(metrics);

    let persona = '기초를 다지는 성장기 분석가';
    if (totalScore >= 90)      persona = '완벽한 방어기제의 철옹성 설계자';
    else if (totalScore >= 60) persona = '원칙 중심의 이론가';

    return {
      persona,
      summary: `총점 ${totalScore}점으로 데이터 전처리 파이프라인에 대한 ${totalScore >= 70 ? '우수한' : '기본적인'} 이해를 보여주셨습니다.`,
      strength: {
        metric:   strongest.name || '',
        feedback: `${strongest.name} 부분에서 ${strongest.percentage}%의 높은 점수를 기록하여 해당 영역의 이해도가 뛰어납니다.`
      },
      weakness: {
        metric:   weakest.name || '',
        feedback: `${weakest.name} 부분에서 ${weakest.percentage}%로 보완이 필요합니다.`
      },
      scoringAnalysis: `현재 총점은 ${totalScore}점입니다.`,
      lesson: `${weakest.name} 향상을 위해 관련 실전 예제에 집중하세요.`,
      rawReport: ''
    };
  }

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
        borderColor:     'rgb(54, 162, 235)',
        pointBackgroundColor: 'rgb(54, 162, 235)',
        pointBorderColor:     '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor:     'rgb(54, 162, 235)'
      }]
    };
  }

  /**
   * 등급 계산
   * S / A+ / A / B+ / B / C / D / F
   */
  calculateGrade(totalScore) {
    if (totalScore >= 90) return { grade: 'S',  color: '#FFD700', description: '완벽' };
    if (totalScore >= 85) return { grade: 'A+', color: '#C8FF3E', description: '최우수' };
    if (totalScore >= 80) return { grade: 'A',  color: '#4CAF50', description: '우수' };
    if (totalScore >= 75) return { grade: 'B+', color: '#00BCD4', description: '양호+' };
    if (totalScore >= 70) return { grade: 'B',  color: '#2196F3', description: '양호' };
    if (totalScore >= 60) return { grade: 'C',  color: '#FF9800', description: '보통' };
    if (totalScore >= 50) return { grade: 'D',  color: '#FF5722', description: '미흡' };
    return                       { grade: 'F',  color: '#F44336', description: '재학습 필요' };
  }
}

/**
 * 완전한 학습 리포트 생성
 */
export async function generateCompleteLearningReport(evaluationResults, apiKey) {
  const generator = new ReportGenerator(apiKey);

  // 1. 최종 진단 리포트 (LLM)
  const finalReport = await generator.generateFinalReport(
    evaluationResults.metrics,
    evaluationResults.total
  );

  // 2. 레이더 차트 데이터
  const radarData = generator.generateRadarChartData(evaluationResults.metrics);

  // 3. 등급
  const grade = generator.calculateGrade(evaluationResults.total);

  // 4. YouTube 추천 영상 - Quest ID × 취약 차원 기반 하드코딩 큐레이션
  const { weakest } = generator.analyzeMetrics(evaluationResults.metrics);
  const { getRecommendedVideos } = await import('./learningResources.js');
  const questId = evaluationResults.questId || evaluationResults.id || 1;
  const curatedVideos = getRecommendedVideos(questId, evaluationResults.metrics, 3);
  const videos = curatedVideos.map(v => ({
    ...v,
    videoId:   v.id,
    thumbnail: `https://img.youtube.com/vi/${v.id}/mqdefault.jpg`,
    url:       `https://www.youtube.com/watch?v=${v.id}`
  }));
  console.log(`[YouTube 큐레이션] Quest ${questId} 로드:`, videos.length + '개');

  return {
    finalReport,
    radarData,
    grade,
    recommendedContent: {
      videos,
      curationMessage: `${weakest.name || '취약 차원'} 보완을 위한 맞춤 추천 영상입니다.`
    },
    metrics:    evaluationResults.metrics,
    totalScore: evaluationResults.total,
    timestamp:  new Date().toISOString()
  };
}
