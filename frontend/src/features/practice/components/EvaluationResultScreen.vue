<template>
  <div class="evaluation-screen">
    <div class="bg-animation"></div>

    <div class="result-container">
      <div class="result-header">
        <h1>📊 평가 결과</h1>
        <p class="problem-title" v-if="problem">{{ problem.title }}</p>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner-xl"></div>
        <p>아키텍처를 평가하고 있습니다...</p>
      </div>

      <!-- Result Content -->
      <div v-else-if="result" class="result-content">
        <!-- Score Card -->
        <div class="score-card" :class="result.grade">
          <div class="score-circle">
            <svg viewBox="0 0 100 100">
              <circle class="score-bg" cx="50" cy="50" r="45"/>
              <circle
                class="score-progress"
                cx="50" cy="50" r="45"
                :style="{ strokeDashoffset: scoreOffset }"
              />
            </svg>
            <div class="score-value">
              <span class="score-number">{{ result.score }}</span>
              <span class="score-unit">점</span>
            </div>
          </div>
          <div class="grade-badge" :class="result.grade">
            {{ gradeText }}
          </div>
        </div>

        <!-- Summary -->
        <div class="summary-card">
          <h3>📝 종합 평가</h3>
          <p>{{ result.summary }}</p>
        </div>

        <!-- Detailed Scores -->
        <div class="scores-grid">
          <!-- System Architecture -->
          <div v-if="result.systemArchitectureScores" class="score-section">
            <h3>🏗️ 시스템 아키텍처 (60%)</h3>
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

          <!-- Interview Score -->
          <div v-if="result.interviewScores" class="score-section">
            <h3>🎤 면접 답변 (40%)</h3>
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
        </div>

        <!-- Strengths & Weaknesses -->
        <div class="feedback-grid">
          <div v-if="result.strengths && result.strengths.length" class="feedback-card strengths">
            <h3>✅ 강점</h3>
            <ul>
              <li v-for="s in result.strengths" :key="s">{{ s }}</li>
            </ul>
          </div>

          <div v-if="result.weaknesses && result.weaknesses.length" class="feedback-card weaknesses">
            <h3>⚠️ 개선점</h3>
            <ul>
              <li v-for="w in result.weaknesses" :key="w">{{ w }}</li>
            </ul>
          </div>
        </div>

        <!-- Suggestions -->
        <div v-if="result.suggestions && result.suggestions.length" class="suggestions-card">
          <h3>💡 제안</h3>
          <ul>
            <li v-for="s in result.suggestions" :key="s">{{ s }}</li>
          </ul>
        </div>

        <!-- Action Button -->
        <div class="action-buttons">
          <button class="btn-retry" @click="$emit('retry')">
            🔄 다시 도전하기
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EvaluationResultScreen',
  props: {
    result: {
      type: Object,
      default: null
    },
    problem: {
      type: Object,
      default: null
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['retry'],
  computed: {
    scoreOffset() {
      const circumference = 2 * Math.PI * 45;
      const score = this.result?.score || 0;
      return circumference - (score / 100) * circumference;
    },
    gradeText() {
      const grades = {
        'excellent': '🏆 Excellent',
        'good': '👍 Good',
        'needs-improvement': '💪 Keep Going',
        'poor': '📝 Try Again'
      };
      return grades[this.result?.grade] || '';
    }
  },
  methods: {
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
.evaluation-screen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #0a0e27;
  z-index: 2000;
  overflow-y: auto;
  font-family: 'Space Mono', monospace;
}

.bg-animation {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.3;
  background:
    radial-gradient(ellipse at 20% 30%, rgba(0, 255, 157, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 70%, rgba(255, 71, 133, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(100, 181, 246, 0.1) 0%, transparent 50%);
}

.result-container {
  position: relative;
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.result-header {
  text-align: center;
  margin-bottom: 40px;
}

.result-header h1 {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.5em;
  color: #00ff9d;
  margin: 0 0 10px 0;
  text-shadow: 0 0 30px rgba(0, 255, 157, 0.5);
}

.problem-title {
  color: #64b5f6;
  font-size: 1.2em;
  margin: 0;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
}

.loading-spinner-xl {
  width: 80px;
  height: 80px;
  border: 4px solid rgba(0, 255, 157, 0.2);
  border-top-color: #00ff9d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 30px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: #b0bec5;
  font-size: 1.2em;
}

/* Score Card */
.score-card {
  background: rgba(17, 24, 39, 0.95);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  margin-bottom: 30px;
  border: 2px solid;
}

.score-card.excellent { border-color: #00ff9d; }
.score-card.good { border-color: #64b5f6; }
.score-card.needs-improvement { border-color: #ffc107; }
.score-card.poor { border-color: #ff4785; }

.score-circle {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto 20px;
}

.score-circle svg {
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
}

.score-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 8;
}

.score-progress {
  fill: none;
  stroke: #00ff9d;
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 283;
  transition: stroke-dashoffset 1s ease;
}

.score-card.excellent .score-progress { stroke: #00ff9d; }
.score-card.good .score-progress { stroke: #64b5f6; }
.score-card.needs-improvement .score-progress { stroke: #ffc107; }
.score-card.poor .score-progress { stroke: #ff4785; }

.score-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-number {
  font-family: 'Orbitron', sans-serif;
  font-size: 3.5em;
  font-weight: 900;
  color: #fff;
  display: block;
}

.score-unit {
  font-size: 1.2em;
  color: #90a4ae;
}

.grade-badge {
  display: inline-block;
  padding: 10px 30px;
  border-radius: 30px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.2em;
  font-weight: 700;
}

.grade-badge.excellent { background: linear-gradient(135deg, #00ff9d, #00e676); color: #0a0e27; }
.grade-badge.good { background: linear-gradient(135deg, #64b5f6, #2196f3); color: #fff; }
.grade-badge.needs-improvement { background: linear-gradient(135deg, #ffc107, #ffa000); color: #0a0e27; }
.grade-badge.poor { background: linear-gradient(135deg, #ff4785, #ff1744); color: #fff; }

/* Summary Card */
.summary-card {
  background: rgba(17, 24, 39, 0.95);
  border-radius: 16px;
  padding: 25px;
  margin-bottom: 30px;
  border: 1px solid rgba(100, 181, 246, 0.3);
}

.summary-card h3 {
  color: #64b5f6;
  margin: 0 0 15px 0;
  font-size: 1.1em;
}

.summary-card p {
  color: #e0e0e0;
  margin: 0;
  line-height: 1.7;
  font-size: 1em;
}

/* Scores Grid */
.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.score-section {
  background: rgba(17, 24, 39, 0.95);
  border-radius: 16px;
  padding: 25px;
  border: 1px solid rgba(100, 181, 246, 0.3);
}

.score-section h3 {
  color: #64b5f6;
  margin: 0 0 20px 0;
  font-size: 1.1em;
}

.score-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.score-item {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 10px;
}

.score-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.score-item-label {
  font-weight: 600;
  color: #e0e0e0;
}

.score-item-value {
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
}

.score-item-value.excellent { color: #00ff9d; }
.score-item-value.good { color: #64b5f6; }
.score-item-value.needs-improvement { color: #ffc107; }
.score-item-value.poor { color: #ff4785; }

.score-item-bar {
  height: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 10px;
}

.score-item-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.8s ease;
}

.score-item-fill.excellent { background: linear-gradient(90deg, #00ff9d, #00e676); }
.score-item-fill.good { background: linear-gradient(90deg, #64b5f6, #2196f3); }
.score-item-fill.needs-improvement { background: linear-gradient(90deg, #ffc107, #ffa000); }
.score-item-fill.poor { background: linear-gradient(90deg, #ff4785, #ff1744); }

.score-item-feedback {
  font-size: 0.85em;
  color: #90a4ae;
  margin: 0;
  line-height: 1.5;
}

/* Feedback Grid */
.feedback-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.feedback-card {
  background: rgba(17, 24, 39, 0.95);
  border-radius: 16px;
  padding: 25px;
  border: 1px solid;
}

.feedback-card.strengths {
  border-color: rgba(0, 255, 157, 0.3);
}

.feedback-card.weaknesses {
  border-color: rgba(255, 193, 7, 0.3);
}

.feedback-card h3 {
  margin: 0 0 15px 0;
  font-size: 1.1em;
}

.feedback-card.strengths h3 { color: #00ff9d; }
.feedback-card.weaknesses h3 { color: #ffc107; }

.feedback-card ul {
  margin: 0;
  padding-left: 20px;
}

.feedback-card li {
  color: #e0e0e0;
  margin-bottom: 8px;
  line-height: 1.5;
}

/* Suggestions */
.suggestions-card {
  background: rgba(17, 24, 39, 0.95);
  border-radius: 16px;
  padding: 25px;
  margin-bottom: 30px;
  border: 1px solid rgba(100, 181, 246, 0.3);
}

.suggestions-card h3 {
  color: #64b5f6;
  margin: 0 0 15px 0;
  font-size: 1.1em;
}

.suggestions-card ul {
  margin: 0;
  padding-left: 20px;
}

.suggestions-card li {
  color: #e0e0e0;
  margin-bottom: 8px;
  line-height: 1.5;
}

/* Action Buttons */
.action-buttons {
  text-align: center;
  padding: 20px 0;
}

.btn-retry {
  padding: 18px 50px;
  background: linear-gradient(135deg, #00ff9d, #00e676);
  border: none;
  border-radius: 12px;
  color: #0a0e27;
  font-family: 'Space Mono', monospace;
  font-size: 1.1em;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-retry:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 255, 157, 0.4);
}
</style>
