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

        <!-- Architecture Evaluation (50점 만점) -->
        <div v-if="result.architectureEvaluation" class="architecture-eval-section">
          <h2>🏗️ 아키텍처 설계 평가 (50점)</h2>
          <div class="eval-score-header">
            <span class="eval-score-value" :class="getScoreClass50(result.architectureEvaluation.score)">
              {{ result.architectureEvaluation.score || 0 }}점
            </span>
            <span class="eval-score-max">/ 50점</span>
          </div>
          <div class="eval-bar">
            <div
              class="eval-bar-fill"
              :style="{ width: ((result.architectureEvaluation.score || 0) / 50 * 100) + '%' }"
              :class="getScoreClass50(result.architectureEvaluation.score)"
            ></div>
          </div>

          <!-- Details -->
          <div v-if="result.architectureEvaluation.details && result.architectureEvaluation.details.length" class="eval-details">
            <div v-for="(detail, idx) in result.architectureEvaluation.details" :key="idx" class="eval-detail-item">
              <div class="detail-header">
                <span class="detail-item">{{ detail.item }}</span>
                <span class="detail-score" :class="getScoreClass(detail.score * 4)">{{ detail.score }}점</span>
              </div>
              <p class="detail-basis">{{ detail.basis }}</p>
            </div>
          </div>

          <!-- Missing Components -->
          <div v-if="result.architectureEvaluation.missingComponents && result.architectureEvaluation.missingComponents.length" class="missing-section">
            <h4>❌ 누락된 컴포넌트</h4>
            <div class="tag-list">
              <span v-for="comp in result.architectureEvaluation.missingComponents" :key="comp" class="tag missing">
                {{ comp }}
              </span>
            </div>
          </div>

          <!-- Incorrect Flows -->
          <div v-if="result.architectureEvaluation.incorrectFlows && result.architectureEvaluation.incorrectFlows.length" class="incorrect-section">
            <h4>⚠️ 잘못된 연결</h4>
            <div class="tag-list">
              <span v-for="flow in result.architectureEvaluation.incorrectFlows" :key="flow" class="tag incorrect">
                {{ flow }}
              </span>
            </div>
          </div>
        </div>

        <!-- Interview Evaluation (50점 만점) -->
        <div v-if="result.interviewEvaluation" class="interview-eval-section">
          <h2>🎤 면접 답변 평가 (50점)</h2>
          <div class="eval-score-header">
            <span class="eval-score-value" :class="getScoreClass50(result.interviewEvaluation.score)">
              {{ result.interviewEvaluation.score || 0 }}점
            </span>
            <span class="eval-score-max">/ 50점</span>
          </div>
          <div class="eval-bar">
            <div
              class="eval-bar-fill"
              :style="{ width: ((result.interviewEvaluation.score || 0) / 50 * 100) + '%' }"
              :class="getScoreClass50(result.interviewEvaluation.score)"
            ></div>
          </div>

          <!-- Answer Analysis -->
          <div v-if="result.interviewEvaluation.answerAnalysis" class="answer-analysis">
            <h4>📝 답변 분석</h4>
            <div class="analysis-grid">
              <div class="analysis-item">
                <span class="analysis-label">답변 길이</span>
                <span class="analysis-value">{{ result.interviewEvaluation.answerAnalysis.length || 0 }}자</span>
              </div>
              <div class="analysis-item">
                <span class="analysis-label">기술 용어 사용</span>
                <span class="analysis-value" :class="result.interviewEvaluation.answerAnalysis.hasKeyTerms ? 'positive' : 'negative'">
                  {{ result.interviewEvaluation.answerAnalysis.hasKeyTerms ? '✅ 사용함' : '❌ 부족' }}
                </span>
              </div>
            </div>

            <!-- Key Terms Found -->
            <div v-if="result.interviewEvaluation.answerAnalysis.keyTermsFound && result.interviewEvaluation.answerAnalysis.keyTermsFound.length" class="keyterms-section">
              <h5>✅ 발견된 기술 용어</h5>
              <div class="tag-list">
                <span v-for="term in result.interviewEvaluation.answerAnalysis.keyTermsFound" :key="term" class="tag found">
                  {{ term }}
                </span>
              </div>
            </div>

            <!-- Key Terms Missing -->
            <div v-if="result.interviewEvaluation.answerAnalysis.keyTermsMissing && result.interviewEvaluation.answerAnalysis.keyTermsMissing.length" class="keyterms-section">
              <h5>❌ 누락된 핵심 키워드</h5>
              <div class="tag-list">
                <span v-for="term in result.interviewEvaluation.answerAnalysis.keyTermsMissing" :key="term" class="tag missing">
                  {{ term }}
                </span>
              </div>
            </div>
          </div>

          <!-- Question Analysis -->
          <div v-if="result.interviewEvaluation.questionAnalysis && result.interviewEvaluation.questionAnalysis.length" class="question-analysis">
            <h4>💬 질문별 분석</h4>
            <div class="question-list">
              <div v-for="(qa, idx) in result.interviewEvaluation.questionAnalysis" :key="idx" class="question-item" :class="qa.matchStatus">
                <div class="question-header">
                  <span class="question-number">Q{{ idx + 1 }}</span>
                  <span class="match-badge" :class="qa.matchStatus">
                    {{ matchStatusText(qa.matchStatus) }}
                  </span>
                  <span class="question-score">{{ qa.score }}점</span>
                </div>
                <div class="question-content">
                  <p class="question-text">{{ qa.question }}</p>
                </div>
                <div class="answer-comparison">
                  <div class="user-answer-box">
                    <span class="box-label">내 답변</span>
                    <p>{{ qa.userAnswer || '(답변 없음)' }}</p>
                  </div>
                  <div class="model-answer-box">
                    <span class="box-label">모범 답안</span>
                    <p>{{ qa.modelAnswer }}</p>
                  </div>
                </div>
                <div v-if="qa.deductionReason" class="deduction-reason">
                  <span class="deduction-label">감점 사유:</span> {{ qa.deductionReason }}
                </div>
                <div v-if="qa.feedback" class="question-feedback">
                  <span class="feedback-label">피드백:</span> {{ qa.feedback }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Legacy: Interview Score (기존 형식 지원) -->
        <div v-else-if="result.interviewScore" class="interview-score-section">
          <h3>🎤 면접 답변 평가</h3>
          <div class="interview-score-card">
            <div class="interview-score-header">
              <span class="interview-score-value" :class="getScoreClass(result.interviewScore.score)">
                {{ result.interviewScore.score }}점
              </span>
            </div>
            <div class="interview-score-bar">
              <div
                class="interview-score-fill"
                :style="{ width: result.interviewScore.score + '%' }"
                :class="getScoreClass(result.interviewScore.score)"
              ></div>
            </div>
            <p class="interview-score-feedback">{{ result.interviewScore.feedback }}</p>
          </div>
        </div>

        <!-- Legacy Support: Old format scores -->
        <div v-else-if="result.systemArchitectureScores || result.interviewScores" class="scores-grid">
          <!-- System Architecture (Legacy) -->
          <div v-if="result.systemArchitectureScores" class="score-section">
            <h3>🏗️ 시스템 아키텍처</h3>
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

          <!-- Interview Score (Legacy) -->
          <div v-if="result.interviewScores" class="score-section">
            <h3>🎤 면접 답변</h3>
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
    },
    getScoreClass50(score) {
      // 50점 만점 기준
      if (score >= 45) return 'excellent';
      if (score >= 35) return 'good';
      if (score >= 25) return 'needs-improvement';
      return 'poor';
    },
    matchStatusText(status) {
      const texts = {
        'match': '✅ 일치',
        'partial': '🔶 부분 일치',
        'mismatch': '❌ 불일치'
      };
      return texts[status] || status;
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

/* NFR Scores Section */
.nfr-scores-section {
  margin-bottom: 30px;
}

.nfr-scores-section h2 {
  color: #64b5f6;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.3em;
  margin: 0 0 20px 0;
  text-align: center;
}

.nfr-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 15px;
}

.nfr-card {
  background: rgba(17, 24, 39, 0.95);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(100, 181, 246, 0.3);
  transition: all 0.3s ease;
}

.nfr-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}

.nfr-card.excellent { border-color: rgba(0, 255, 157, 0.5); }
.nfr-card.good { border-color: rgba(100, 181, 246, 0.5); }
.nfr-card.needs-improvement { border-color: rgba(255, 193, 7, 0.5); }
.nfr-card.poor { border-color: rgba(255, 71, 133, 0.5); }

.nfr-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.nfr-icon {
  font-size: 1.3em;
}

.nfr-title {
  flex: 1;
  font-weight: 600;
  color: #e0e0e0;
  font-size: 0.95em;
}

.nfr-score {
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  font-size: 1.1em;
}

.nfr-score.excellent { color: #00ff9d; }
.nfr-score.good { color: #64b5f6; }
.nfr-score.needs-improvement { color: #ffc107; }
.nfr-score.poor { color: #ff4785; }

.nfr-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.nfr-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.8s ease;
}

.nfr-bar-fill.excellent { background: linear-gradient(90deg, #00ff9d, #00e676); }
.nfr-bar-fill.good { background: linear-gradient(90deg, #64b5f6, #2196f3); }
.nfr-bar-fill.needs-improvement { background: linear-gradient(90deg, #ffc107, #ffa000); }
.nfr-bar-fill.poor { background: linear-gradient(90deg, #ff4785, #ff1744); }

.nfr-feedback {
  font-size: 0.85em;
  color: #90a4ae;
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.nfr-checklist {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.nfr-checklist span {
  font-size: 0.8em;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  color: #90a4ae;
}

.nfr-checklist span.checked {
  color: #00ff9d;
  background: rgba(0, 255, 157, 0.1);
}

/* Interview Score Section */
.interview-score-section {
  background: rgba(17, 24, 39, 0.95);
  border-radius: 16px;
  padding: 25px;
  margin-bottom: 30px;
  border: 1px solid rgba(100, 181, 246, 0.3);
}

.interview-score-section h3 {
  color: #64b5f6;
  margin: 0 0 20px 0;
  font-size: 1.1em;
}

.interview-score-card {
  background: rgba(0, 0, 0, 0.3);
  padding: 20px;
  border-radius: 10px;
}

.interview-score-header {
  text-align: center;
  margin-bottom: 15px;
}

.interview-score-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 2em;
  font-weight: 700;
}

.interview-score-value.excellent { color: #00ff9d; }
.interview-score-value.good { color: #64b5f6; }
.interview-score-value.needs-improvement { color: #ffc107; }
.interview-score-value.poor { color: #ff4785; }

.interview-score-bar {
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 15px;
}

.interview-score-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.8s ease;
}

.interview-score-fill.excellent { background: linear-gradient(90deg, #00ff9d, #00e676); }
.interview-score-fill.good { background: linear-gradient(90deg, #64b5f6, #2196f3); }
.interview-score-fill.needs-improvement { background: linear-gradient(90deg, #ffc107, #ffa000); }
.interview-score-fill.poor { background: linear-gradient(90deg, #ff4785, #ff1744); }

.interview-score-feedback {
  font-size: 0.95em;
  color: #e0e0e0;
  margin: 0;
  line-height: 1.6;
  text-align: center;
}

/* Architecture & Interview Evaluation Sections */
.architecture-eval-section,
.interview-eval-section {
  background: rgba(17, 24, 39, 0.95);
  border-radius: 16px;
  padding: 25px;
  margin-bottom: 30px;
  border: 1px solid rgba(100, 181, 246, 0.3);
}

.architecture-eval-section h2,
.interview-eval-section h2 {
  color: #64b5f6;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.2em;
  margin: 0 0 20px 0;
}

.eval-score-header {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
  margin-bottom: 15px;
}

.eval-score-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.5em;
  font-weight: 700;
}

.eval-score-value.excellent { color: #00ff9d; }
.eval-score-value.good { color: #64b5f6; }
.eval-score-value.needs-improvement { color: #ffc107; }
.eval-score-value.poor { color: #ff4785; }

.eval-score-max {
  color: #90a4ae;
  font-size: 1.2em;
}

.eval-bar {
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 25px;
}

.eval-bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.8s ease;
}

.eval-bar-fill.excellent { background: linear-gradient(90deg, #00ff9d, #00e676); }
.eval-bar-fill.good { background: linear-gradient(90deg, #64b5f6, #2196f3); }
.eval-bar-fill.needs-improvement { background: linear-gradient(90deg, #ffc107, #ffa000); }
.eval-bar-fill.poor { background: linear-gradient(90deg, #ff4785, #ff1744); }

/* Eval Details */
.eval-details {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.eval-detail-item {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 10px;
  border-left: 3px solid #64b5f6;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.detail-item {
  font-weight: 600;
  color: #e0e0e0;
}

.detail-score {
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
}

.detail-score.excellent { color: #00ff9d; }
.detail-score.good { color: #64b5f6; }
.detail-score.needs-improvement { color: #ffc107; }
.detail-score.poor { color: #ff4785; }

.detail-basis {
  font-size: 0.9em;
  color: #90a4ae;
  margin: 0;
  line-height: 1.5;
}

/* Missing & Incorrect Sections */
.missing-section,
.incorrect-section {
  margin-top: 20px;
  padding: 15px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
}

.missing-section h4,
.incorrect-section h4 {
  color: #ff4785;
  margin: 0 0 12px 0;
  font-size: 0.95em;
}

.incorrect-section h4 {
  color: #ffc107;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 500;
}

.tag.missing {
  background: rgba(255, 71, 133, 0.2);
  color: #ff4785;
  border: 1px solid rgba(255, 71, 133, 0.4);
}

.tag.incorrect {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
  border: 1px solid rgba(255, 193, 7, 0.4);
}

.tag.found {
  background: rgba(0, 255, 157, 0.2);
  color: #00ff9d;
  border: 1px solid rgba(0, 255, 157, 0.4);
}

/* Answer Analysis */
.answer-analysis {
  margin-top: 20px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
}

.answer-analysis h4 {
  color: #64b5f6;
  margin: 0 0 15px 0;
  font-size: 1em;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.analysis-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
}

.analysis-label {
  color: #90a4ae;
  font-size: 0.9em;
}

.analysis-value {
  font-weight: 600;
  color: #e0e0e0;
}

.analysis-value.positive { color: #00ff9d; }
.analysis-value.negative { color: #ff4785; }

.keyterms-section {
  margin-top: 15px;
}

.keyterms-section h5 {
  color: #b0bec5;
  margin: 0 0 10px 0;
  font-size: 0.9em;
}

/* Question Analysis */
.question-analysis {
  margin-top: 25px;
}

.question-analysis h4 {
  color: #64b5f6;
  margin: 0 0 20px 0;
  font-size: 1em;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-item {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 20px;
  border-left: 4px solid #64b5f6;
}

.question-item.match { border-left-color: #00ff9d; }
.question-item.partial { border-left-color: #ffc107; }
.question-item.mismatch { border-left-color: #ff4785; }

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
}

.question-number {
  background: rgba(100, 181, 246, 0.2);
  color: #64b5f6;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 700;
}

.match-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8em;
  font-weight: 600;
}

.match-badge.match {
  background: rgba(0, 255, 157, 0.2);
  color: #00ff9d;
}

.match-badge.partial {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.match-badge.mismatch {
  background: rgba(255, 71, 133, 0.2);
  color: #ff4785;
}

.question-score {
  margin-left: auto;
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  color: #e0e0e0;
}

.question-content {
  margin-bottom: 15px;
}

.question-text {
  color: #e0e0e0;
  margin: 0;
  line-height: 1.6;
  font-size: 0.95em;
}

.answer-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
}

.user-answer-box,
.model-answer-box {
  padding: 15px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.3);
}

.user-answer-box {
  border: 1px solid rgba(100, 181, 246, 0.3);
}

.model-answer-box {
  border: 1px solid rgba(0, 255, 157, 0.3);
}

.box-label {
  display: block;
  font-size: 0.8em;
  font-weight: 600;
  margin-bottom: 8px;
}

.user-answer-box .box-label { color: #64b5f6; }
.model-answer-box .box-label { color: #00ff9d; }

.user-answer-box p,
.model-answer-box p {
  color: #b0bec5;
  margin: 0;
  font-size: 0.9em;
  line-height: 1.5;
}

.deduction-reason {
  background: rgba(255, 71, 133, 0.1);
  padding: 10px 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  font-size: 0.9em;
  color: #ff4785;
}

.deduction-label {
  font-weight: 600;
}

.question-feedback {
  background: rgba(100, 181, 246, 0.1);
  padding: 10px 15px;
  border-radius: 8px;
  font-size: 0.9em;
  color: #64b5f6;
}

.feedback-label {
  font-weight: 600;
}

@media (max-width: 768px) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }

  .answer-comparison {
    grid-template-columns: 1fr;
  }
}
</style>
