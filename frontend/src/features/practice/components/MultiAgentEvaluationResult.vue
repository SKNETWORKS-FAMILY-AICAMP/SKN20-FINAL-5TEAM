<template>
  <div v-if="result" class="multi-agent-result" :class="result.grade">
    <!-- 총점 및 등급 표시 -->
    <div class="score-header">
      <div class="total-score" :style="{ color: getGradeColor(result.grade) }">
        {{ getGradeEmoji(result.grade) }} {{ result.score }}점
      </div>
      <div class="grade-badge" :class="result.grade">
        {{ getGradeText(result.grade) }}
      </div>
    </div>

    <!-- 종합 평가 -->
    <div class="summary-section">
      <p>{{ result.summary }}</p>
    </div>

    <!-- 6 Pillar 레이더 차트 스타일 표시 -->
    <div v-if="result.multiAgentEvaluation" class="pillars-section">
      <h4>6 Pillars 평가 결과</h4>
      <div class="pillars-grid">
        <div
          v-for="(detail, key) in result.multiAgentEvaluation.pillarDetails"
          :key="key"
          class="pillar-card"
          :class="getScoreClass(detail.score)"
          @click="togglePillarDetail(key)"
        >
          <div class="pillar-header">
            <span class="pillar-emoji">{{ detail.emoji }}</span>
            <span class="pillar-name">{{ formatPillarName(detail.name) }}</span>
          </div>
          <div class="pillar-score">{{ detail.score }}점</div>
          <div class="pillar-bar">
            <div
              class="pillar-fill"
              :style="{ width: detail.score + '%' }"
              :class="getScoreClass(detail.score)"
            ></div>
          </div>

          <!-- 확장된 상세 정보 -->
          <transition name="expand">
            <div v-if="expandedPillars[key]" class="pillar-detail">
              <p class="pillar-summary">{{ detail.summary }}</p>

              <!-- 4가지 평가 기준 -->
              <div class="evaluation-criteria">
                <div
                  v-for="(evalItem, evalKey) in detail.evaluation"
                  :key="evalKey"
                  class="eval-item"
                >
                  <div class="eval-header">
                    <span class="eval-icon">{{ getEvalIcon(evalKey) }}</span>
                    <span class="eval-label">{{ getEvalLabel(evalKey) }}</span>
                    <span class="eval-score" :class="getScoreClass(evalItem.score)">
                      {{ evalItem.score }}점
                    </span>
                  </div>
                  <p class="eval-analysis">{{ evalItem.analysis }}</p>

                  <!-- 강점/리스크 하이라이트 -->
                  <div v-if="evalItem.highlights && evalItem.highlights.length" class="highlights">
                    <span v-for="h in evalItem.highlights" :key="h" class="highlight-tag positive">
                      {{ h }}
                    </span>
                  </div>
                  <div v-if="evalItem.concerns && evalItem.concerns.length" class="highlights">
                    <span v-for="c in evalItem.concerns" :key="c" class="highlight-tag negative">
                      {{ c }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- 권장 사항 -->
              <div v-if="detail.recommendations" class="recommendations">
                <div v-if="detail.recommendations.shortTerm?.length" class="rec-section">
                  <h6>단기 개선</h6>
                  <ul>
                    <li v-for="r in detail.recommendations.shortTerm" :key="r">{{ r }}</li>
                  </ul>
                </div>
                <div v-if="detail.recommendations.longTerm?.length" class="rec-section">
                  <h6>장기 과제</h6>
                  <ul>
                    <li v-for="r in detail.recommendations.longTerm" :key="r">{{ r }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>

    <!-- 기존 NFR 점수 (호환성) -->
    <div v-else-if="result.nfrScores" class="legacy-scores">
      <h4>NFR 평가 점수</h4>
      <div class="score-items">
        <div
          v-for="(value, key) in result.nfrScores"
          :key="key"
          class="score-item"
        >
          <div class="score-item-header">
            <span class="score-item-label">{{ formatNfrLabel(key) }}</span>
            <span class="score-item-value" :class="getScoreClass(value.score)">
              {{ value.score }}점
            </span>
          </div>
          <div class="score-item-bar">
            <div
              class="score-item-fill"
              :style="{ width: value.score + '%' }"
              :class="getScoreClass(value.score)"
            ></div>
          </div>
          <p v-if="value.feedback" class="score-item-feedback">{{ value.feedback }}</p>
        </div>
      </div>
    </div>

    <!-- 강점 -->
    <div v-if="result.strengths?.length" class="feedback-section strengths">
      <h4>강점</h4>
      <ul>
        <li v-for="s in result.strengths" :key="s">{{ s }}</li>
      </ul>
    </div>

    <!-- 개선점 -->
    <div v-if="result.weaknesses?.length" class="feedback-section weaknesses">
      <h4>개선점</h4>
      <ul>
        <li v-for="w in result.weaknesses" :key="w">{{ w }}</li>
      </ul>
    </div>

    <!-- 제안 -->
    <div v-if="result.suggestions?.length" class="feedback-section suggestions">
      <h4>단기 제안</h4>
      <ul>
        <li v-for="s in result.suggestions" :key="s">{{ s }}</li>
      </ul>
    </div>

    <!-- 장기 제안 -->
    <div v-if="result.longTermSuggestions?.length" class="feedback-section long-term">
      <h4>장기 과제</h4>
      <ul>
        <li v-for="s in result.longTermSuggestions" :key="s">{{ s }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  name: 'MultiAgentEvaluationResult',
  props: {
    result: {
      type: Object,
      default: null
    }
  },
  setup() {
    const expandedPillars = ref({});

    const togglePillarDetail = (key) => {
      expandedPillars.value[key] = !expandedPillars.value[key];
    };

    return {
      expandedPillars,
      togglePillarDetail
    };
  },
  methods: {
    getGradeColor(grade) {
      const colors = {
        'excellent': '#00ff9d',
        'good': '#64b5f6',
        'needs-improvement': '#ffc107',
        'poor': '#ff4785'
      };
      return colors[grade] || '#e0e0e0';
    },
    getGradeEmoji(grade) {
      const emojis = {
        'excellent': '🏆',
        'good': '👍',
        'needs-improvement': '💡',
        'poor': '📝'
      };
      return emojis[grade] || '❓';
    },
    getGradeText(grade) {
      const texts = {
        'excellent': '우수',
        'good': '양호',
        'needs-improvement': '개선 필요',
        'poor': '미흡'
      };
      return texts[grade] || '평가 중';
    },
    getScoreClass(score) {
      if (score >= 80) return 'excellent';
      if (score >= 60) return 'good';
      if (score >= 40) return 'needs-improvement';
      return 'poor';
    },
    formatPillarName(name) {
      return name?.replace(' Agent', '') || '';
    },
    formatNfrLabel(key) {
      const labels = {
        scalability: '확장성',
        availability: '가용성',
        performance: '성능',
        consistency: '일관성',
        reliability: '신뢰성'
      };
      return labels[key] || key;
    },
    getEvalIcon(key) {
      const icons = {
        suitability: '🎯',
        dataCollection: '📊',
        strengths: '✅',
        risks: '⚠️'
      };
      return icons[key] || '📌';
    },
    getEvalLabel(key) {
      const labels = {
        suitability: '설계 적합성',
        dataCollection: '가시성 확보',
        strengths: '강점 분석',
        risks: '리스크 분석'
      };
      return labels[key] || key;
    }
  }
};
</script>

<style scoped>
.multi-agent-result {
  background: rgba(0, 0, 0, 0.5);
  border-radius: 16px;
  padding: 24px;
  border: 2px solid;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.multi-agent-result.excellent { border-color: #00ff9d; }
.multi-agent-result.good { border-color: #64b5f6; }
.multi-agent-result.needs-improvement { border-color: #ffc107; }
.multi-agent-result.poor { border-color: #ff4785; }

/* Score Header */
.score-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

.total-score {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.5em;
  text-shadow: 0 0 20px currentColor;
}

.grade-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9em;
}

.grade-badge.excellent { background: rgba(0, 255, 157, 0.2); color: #00ff9d; }
.grade-badge.good { background: rgba(100, 181, 246, 0.2); color: #64b5f6; }
.grade-badge.needs-improvement { background: rgba(255, 193, 7, 0.2); color: #ffc107; }
.grade-badge.poor { background: rgba(255, 71, 133, 0.2); color: #ff4785; }

/* Summary */
.summary-section {
  background: rgba(255, 255, 255, 0.05);
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 24px;
}

.summary-section p {
  margin: 0;
  color: #b0bec5;
  line-height: 1.6;
  text-align: center;
}

/* Pillars Section */
.pillars-section h4 {
  color: #64b5f6;
  margin: 0 0 16px 0;
  font-size: 1.1em;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pillars-section h4::before {
  content: '🏛️';
}

.pillars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.pillar-card {
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.pillar-card:hover {
  transform: translateY(-2px);
  border-color: rgba(100, 181, 246, 0.3);
}

.pillar-card.excellent { border-left: 4px solid #00ff9d; }
.pillar-card.good { border-left: 4px solid #64b5f6; }
.pillar-card.needs-improvement { border-left: 4px solid #ffc107; }
.pillar-card.poor { border-left: 4px solid #ff4785; }

.pillar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.pillar-emoji {
  font-size: 1.5em;
}

.pillar-name {
  font-weight: 600;
  color: #e0e0e0;
  font-size: 0.95em;
}

.pillar-score {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.8em;
  margin-bottom: 8px;
}

.pillar-card.excellent .pillar-score { color: #00ff9d; }
.pillar-card.good .pillar-score { color: #64b5f6; }
.pillar-card.needs-improvement .pillar-score { color: #ffc107; }
.pillar-card.poor .pillar-score { color: #ff4785; }

.pillar-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.pillar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.pillar-fill.excellent { background: linear-gradient(90deg, #00ff9d, #00e676); }
.pillar-fill.good { background: linear-gradient(90deg, #64b5f6, #2196f3); }
.pillar-fill.needs-improvement { background: linear-gradient(90deg, #ffc107, #ffa000); }
.pillar-fill.poor { background: linear-gradient(90deg, #ff4785, #ff1744); }

/* Pillar Detail (Expanded) */
.pillar-detail {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.pillar-summary {
  color: #90a4ae;
  font-size: 0.85em;
  line-height: 1.5;
  margin-bottom: 16px;
}

.evaluation-criteria {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.eval-item {
  background: rgba(255, 255, 255, 0.03);
  padding: 12px;
  border-radius: 8px;
}

.eval-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.eval-icon {
  font-size: 1em;
}

.eval-label {
  flex: 1;
  font-weight: 500;
  color: #b0bec5;
  font-size: 0.85em;
}

.eval-score {
  font-family: 'Orbitron', sans-serif;
  font-weight: 600;
  font-size: 0.85em;
}

.eval-score.excellent { color: #00ff9d; }
.eval-score.good { color: #64b5f6; }
.eval-score.needs-improvement { color: #ffc107; }
.eval-score.poor { color: #ff4785; }

.eval-analysis {
  margin: 0;
  color: #78909c;
  font-size: 0.8em;
  line-height: 1.4;
}

.highlights {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.highlight-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75em;
}

.highlight-tag.positive {
  background: rgba(0, 255, 157, 0.15);
  color: #00ff9d;
}

.highlight-tag.negative {
  background: rgba(255, 71, 133, 0.15);
  color: #ff4785;
}

/* Recommendations */
.recommendations {
  margin-top: 16px;
}

.rec-section {
  margin-bottom: 12px;
}

.rec-section h6 {
  color: #64b5f6;
  font-size: 0.8em;
  margin: 0 0 8px 0;
}

.rec-section ul {
  margin: 0;
  padding-left: 16px;
}

.rec-section li {
  color: #90a4ae;
  font-size: 0.8em;
  line-height: 1.4;
  margin-bottom: 4px;
}

/* Expand Animation */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 1000px;
}

/* Feedback Sections */
.feedback-section {
  margin-top: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.feedback-section h4 {
  margin: 0 0 12px 0;
  font-size: 1em;
}

.feedback-section.strengths h4 { color: #00ff9d; }
.feedback-section.strengths h4::before { content: '✅ '; }

.feedback-section.weaknesses h4 { color: #ffc107; }
.feedback-section.weaknesses h4::before { content: '⚠️ '; }

.feedback-section.suggestions h4 { color: #64b5f6; }
.feedback-section.suggestions h4::before { content: '💡 '; }

.feedback-section.long-term h4 { color: #ab47bc; }
.feedback-section.long-term h4::before { content: '🎯 '; }

.feedback-section ul {
  margin: 0;
  padding-left: 20px;
}

.feedback-section li {
  color: #b0bec5;
  font-size: 0.9em;
  line-height: 1.5;
  margin-bottom: 6px;
}

/* Legacy Scores (기존 호환) */
.legacy-scores {
  margin-top: 20px;
}

.legacy-scores h4 {
  color: #64b5f6;
  margin: 0 0 16px 0;
}

.score-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.score-item {
  background: rgba(0, 0, 0, 0.3);
  padding: 12px;
  border-radius: 8px;
}

.score-item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.score-item-label {
  color: #e0e0e0;
  font-weight: 500;
}

.score-item-value {
  font-family: 'Orbitron', sans-serif;
  font-weight: 600;
}

.score-item-value.excellent { color: #00ff9d; }
.score-item-value.good { color: #64b5f6; }
.score-item-value.needs-improvement { color: #ffc107; }
.score-item-value.poor { color: #ff4785; }

.score-item-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  margin-bottom: 8px;
}

.score-item-fill {
  height: 100%;
  border-radius: 3px;
}

.score-item-fill.excellent { background: #00ff9d; }
.score-item-fill.good { background: #64b5f6; }
.score-item-fill.needs-improvement { background: #ffc107; }
.score-item-fill.poor { background: #ff4785; }

.score-item-feedback {
  margin: 0;
  color: #78909c;
  font-size: 0.85em;
}
</style>
