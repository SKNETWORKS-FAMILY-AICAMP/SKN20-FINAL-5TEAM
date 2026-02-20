/**
 * 최종 진단 리포트 생성 시스템
 * [2026-02-21] GPT 중복 호출 제거 — 백엔드 평가 데이터만 사용
 * 
 * 변경 사항:
 * - callGPT() 제거: 프론트에서 별도 GPT 호출하지 않음
 * - generateFinalReport(): 백엔드 dimensions/feedback 데이터로 직접 구성
 * - parseReport(): 정규식 파싱 제거 (GPT 마크다운 파싱 불필요)
 * - 레이더 차트, 등급 계산, YouTube 큐레이션은 그대로 유지
 */

export class ReportGenerator {
  constructor(apiKey = null) {
    // GPT 호출 제거됨 — apiKey 미사용
  }

  /**
   * [2026-02-21] 백엔드 데이터 기반 리포트 생성 (GPT 호출 없음)
   * @param {Object} metrics - 백엔드에서 온 dimensions 객체
   * @param {number} totalScore - 백엔드에서 온 최종 점수
   * @param {Object} backendFeedback - 백엔드에서 온 feedback 객체 (optional)
   */
  generateFinalReport(metrics, totalScore, backendFeedback = {}) {
    const { strongest, weakest } = this.analyzeMetrics(metrics);

    // 페르소나 결정 (백엔드 persona 우선, 없으면 점수 기반)
    let persona = backendFeedback.persona || this._getPersona(metrics, totalScore);

    // summary (백엔드 summary 우선)
    const summary = backendFeedback.summary || this._getSummary(totalScore);

    // 강점/약점 분석 (백엔드 strengths/improvements 우선)
    const strengthFeedback = backendFeedback.strengths?.length
      ? backendFeedback.strengths.join(' ')
      : `${strongest.name} 부분에서 ${strongest.percentage}%의 높은 점수를 기록하여 해당 영역의 이해도가 뛰어납니다.`;

    const weaknessFeedback = backendFeedback.improvements?.length
      ? backendFeedback.improvements.join(' ')
      : `${weakest.name} 부분에서 ${weakest.percentage}%로 보완이 필요합니다.`;

    // senior_advice → lesson
    const lesson = backendFeedback.senior_advice || 
      `${weakest.name} 향상을 위해 관련 실전 예제에 집중하세요.`;

    // scoringAnalysis: 차원별 comment 중 가장 낮은 점수의 comment 활용
    const scoringAnalysis = weakest.key && metrics[weakest.key]?.comment
      ? metrics[weakest.key].comment
      : '';

    return {
      persona,
      summary,
      strength: {
        metric: strongest.name || '',
        feedback: strengthFeedback
      },
      weakness: {
        metric: weakest.name || '',
        feedback: weaknessFeedback
      },
      scoringAnalysis,
      lesson,
      rawReport: ''
    };
  }

  _getPersona(metrics, totalScore) {
    if (totalScore >= 92) return '완벽한 방어기제의 철옹성 설계자';
    if (totalScore >= 82) return '원칙 중심의 이론가';
    if (totalScore >= 62) return '성장하는 아키텍트';
    return '기초를 다지는 성장기 분석가';
  }

  _getSummary(totalScore) {
    if (totalScore >= 92) return '실무에서도 즉시 사용 가능한 완벽한 설계입니다.';
    if (totalScore >= 82) return '핵심 설계 원칙을 잘 준수하고 있습니다. 예외 상황을 조금 더 고민하면 완벽해질 거예요.';
    if (totalScore >= 62) return '방향성은 잡혔습니다. 로직을 더 구체적으로 쪼개보는 연습이 필요해요.';
    return '설계의 뼈대부터 다시 잡아야 합니다. 가이드를 참고해 논리 순서를 정리해보세요.';
  }

  analyzeMetrics(metrics) {
    const metricsList = Object.entries(metrics).map(([key, value]) => ({
      key,
      name: value.name,
      score: value.score,
      max: value.max,
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

  calculateGrade(totalScore) {
    if (totalScore >= 92) return { grade: 'S', color: '#FFD700', description: '완벽' };
    if (totalScore >= 82) return { grade: 'A', color: '#4CAF50', description: '준수' };
    if (totalScore >= 62) return { grade: 'B', color: '#2196F3', description: '보통' };
    if (totalScore >= 40) return { grade: 'C', color: '#FF9800', description: '미흡' };
    return { grade: 'F', color: '#F44336', description: '재학습 필요' };
  }
}

/**
 * 완전한 학습 리포트 생성 (GPT 호출 없음)
 * [2026-02-21] backendFeedback 파라미터 추가
 */
export async function generateCompleteLearningReport(evaluationResults, apiKey, backendFeedback = {}) {
  const generator = new ReportGenerator();

  // 1. 최종 진단 리포트 (GPT 없이 백엔드 데이터로 직접 구성)
  const finalReport = generator.generateFinalReport(
    evaluationResults.metrics,
    evaluationResults.total,
    backendFeedback
  );

  // 2. 레이더 차트 데이터
  const radarData = generator.generateRadarChartData(evaluationResults.metrics);

  // 3. 등급
  const grade = generator.calculateGrade(evaluationResults.total);

  // 4. YouTube 큐레이션 (로컬 하드코딩 — 백엔드 큐레이션이 없을 때 폴백용)
  const { weakest } = generator.analyzeMetrics(evaluationResults.metrics);
  const { getRecommendedVideos } = await import('./learningResources.js');
  const questId = evaluationResults.questId || evaluationResults.id || 1;
  const curatedVideos = getRecommendedVideos(questId, evaluationResults.metrics, 3);
  const videos = curatedVideos.map(v => ({
    ...v,
    videoId: v.id,
    thumbnail: `https://img.youtube.com/vi/${v.id}/mqdefault.jpg`,
    url: `https://www.youtube.com/watch?v=${v.id}`
  }));

  return {
    finalReport,
    radarData,
    grade,
    recommendedContent: {
      videos,
      curationMessage: `${weakest.name || '취약 차원'} 보완을 위한 맞춤 추천 영상입니다.`
    },
    metrics: evaluationResults.metrics,
    totalScore: evaluationResults.total,
    timestamp: new Date().toISOString()
  };
}
