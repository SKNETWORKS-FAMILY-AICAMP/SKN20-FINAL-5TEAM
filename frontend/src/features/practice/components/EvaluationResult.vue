<template>
  <div v-if="result" class="evaluation-result" :class="result.grade">
    <div class="score-display" :style="{ color: getGradeColor(result.grade) }">
      {{ getGradeEmoji(result.grade) }} {{ result.score }}점
    </div>

    <div class="feedback-section">
      <h4>📊 종합 평가</h4>
      <p>{{ result.summary }}</p>
    </div>

    <!-- 시스템 아키텍처 세부 점수 -->
    <div v-if="result.systemArchitectureScores" class="feedback-section scores-section">
      <h4>🏗️ 시스템 아키텍처 (60%)</h4>
      <div class="score-items">
        <div
          v-for="(value, key) in result.systemArchitectureScores"
          :key="key"
          class="score-item"
        >
          <div class="score-item-header">
            <span class="score-item-label">{{ key }}</span>
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
          <p class="score-item-feedback">{{ value.feedback }}</p>
        </div>
      </div>
    </div>

    <!-- 면접 답변 세부 점수 -->
    <div v-if="result.interviewScores" class="feedback-section scores-section">
      <h4>🎤 면접 답변 (40%)</h4>
      <div class="score-items">
        <div
          v-for="(value, key) in result.interviewScores"
          :key="key"
          class="score-item"
        >
          <div class="score-item-header">
            <span class="score-item-label">{{ key }}</span>
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
          <p class="score-item-feedback">{{ value.feedback }}</p>
        </div>
      </div>
    </div>

    <div v-if="result.strengths && result.strengths.length" class="feedback-section">
      <h4>✅ 강점</h4>
      <ul>
        <li v-for="s in result.strengths" :key="s">{{ s }}</li>
      </ul>
    </div>

    <div v-if="result.weaknesses && result.weaknesses.length" class="feedback-section">
      <h4>⚠️ 개선점</h4>
      <ul>
        <li v-for="w in result.weaknesses" :key="w">{{ w }}</li>
      </ul>
    </div>

    <div v-if="result.suggestions && result.suggestions.length" class="feedback-section">
      <h4>💡 제안</h4>
      <ul>
        <li v-for="s in result.suggestions" :key="s">{{ s }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EvaluationResult',
  props: {
    result: {
      type: Object,
      default: null
    }
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
    getScoreClass(score) {
      if (score >= 90) return 'excellent';
      if (score >= 70) return 'good';
      if (score >= 50) return 'needs-improvement';
      return 'poor';
    }
  }
};
</script>

<style scoped>
.evaluation-result {
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  padding: 20px;
  margin: 15px 20px;
  border: 2px solid;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.evaluation-result.excellent { border-color: #00ff9d; }
.evaluation-result.good { border-color: #64b5f6; }
.evaluation-result.needs-improvement { border-color: #ffc107; }
.evaluation-result.poor { border-color: #ff4785; }

.score-display {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.5em;
  text-align: center;
  margin-bottom: 20px;
  text-shadow: 0 0 20px currentColor;
}

.feedback-section {
  margin-bottom: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.feedback-section h4 {
  color: #64b5f6;
  margin: 0 0 10px 0;
  font-size: 1em;
}

.feedback-section p {
  margin: 0;
  color: #b0bec5;
  font-size: 0.9em;
  line-height: 1.6;
}

.feedback-section ul {
  margin: 0;
  padding-left: 20px;
}

.feedback-section li {
  color: #e0e0e0;
  font-size: 0.9em;
  margin-bottom: 6px;
  line-height: 1.4;
}

/* Scores Section */
.scores-section {
  background: rgba(100, 181, 246, 0.1);
}

.score-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.score-item {
  background: rgba(0, 0, 0, 0.3);
  padding: 12px;
  border-radius: 8px;
}

.score-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.score-item-label {
  font-weight: 600;
  color: #e0e0e0;
  font-size: 0.9em;
}

.score-item-value {
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  font-size: 0.95em;
}

.score-item-value.excellent { color: #00ff9d; }
.score-item-value.good { color: #64b5f6; }
.score-item-value.needs-improvement { color: #ffc107; }
.score-item-value.poor { color: #ff4785; }

.score-item-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.score-item-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.score-item-fill.excellent { background: linear-gradient(90deg, #00ff9d, #00e676); }
.score-item-fill.good { background: linear-gradient(90deg, #64b5f6, #2196f3); }
.score-item-fill.needs-improvement { background: linear-gradient(90deg, #ffc107, #ffa000); }
.score-item-fill.poor { background: linear-gradient(90deg, #ff4785, #ff1744); }

.score-item-feedback {
  font-size: 0.8em;
  color: #90a4ae;
  margin: 0;
  line-height: 1.4;
}
</style>
