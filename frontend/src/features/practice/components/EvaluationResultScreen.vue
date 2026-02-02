<template>
  <div class="case-closed-screen">
    <div class="bg-overlay"></div>

    <div class="result-container">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner-xl"></div>
        <p>판결을 내리는 중... 꽥!</p>
      </div>

      <!-- Result Content -->
      <div v-else-if="result" class="result-report">
        <!-- 스탬프 마크 -->
        <div class="stamp-mark" :class="[verdictClass, { stamped: showStamp }]">
          {{ verdictStamp }}
        </div>

        <!-- 헤더 -->
        <h1 class="report-title">CASE CLOSED</h1>
        <div class="report-meta">
          <p><strong>DATE:</strong> {{ currentDate }}</p>
          <p><strong>OFFICER:</strong> DET. DUCK</p>
          <p v-if="problem"><strong>CASE:</strong> {{ problem.title }}</p>
        </div>

        <hr class="divider" />

        <!-- 판결 결과 -->
        <div class="verdict-section">
          <h2>[ VERDICT ]</h2>
          <div class="verdict-box" :class="verdictClass">
            <div class="verdict-icon">{{ verdictIcon }}</div>
            <div class="verdict-text">{{ verdictMessage }}</div>
          </div>
          <div class="score-display">
            <span class="score-value" :class="verdictClass">{{ result.score }}</span>
            <span class="score-unit">/ 100점</span>
          </div>
        </div>

        <hr class="divider" />

        <!-- 평가된 기둥 점수 (동적) -->
        <div v-if="evaluatedPillars.length" class="eval-section pillar-scores-section">
          <h3>[ 평가 영역별 점수 ]</h3>
          <div class="pillar-grid">
            <div
              v-for="pillar in evaluatedPillars"
              :key="pillar.category"
              class="pillar-item"
              :class="getScoreClass(pillar.score)"
            >
              <span class="pillar-emoji">{{ pillar.emoji }}</span>
              <span class="pillar-name">{{ pillar.category }}</span>
              <span class="pillar-score">{{ pillar.score }}점</span>
            </div>
          </div>
        </div>

        <hr class="divider" />

        <!-- 질문별 평가 결과 (모범답안 포함) -->
        <div v-if="result.questionEvaluations && result.questionEvaluations.length" class="eval-section question-evaluations-section">
          <h3>[ 질문별 상세 평가 ]</h3>
          <div class="question-eval-list">
            <div
              v-for="(qEval, idx) in result.questionEvaluations"
              :key="idx"
              class="question-eval-card"
              :class="getScoreClass(qEval.score)"
            >
              <!-- 질문 헤더 -->
              <div class="question-header">
                <span class="question-category">{{ qEval.category }}</span>
                <span class="question-score" :class="getScoreClass(qEval.score)">{{ qEval.score }}점</span>
              </div>

              <!-- 질문 내용 -->
              <div class="question-content">
                <p class="question-text">❓ {{ qEval.question }}</p>
              </div>

              <!-- 답변 비교 -->
              <div class="answer-comparison">
                <div class="answer-box user-answer">
                  <div class="answer-label">📝 나의 답변</div>
                  <p>{{ qEval.userAnswer || '(답변 없음)' }}</p>
                </div>
                <div class="answer-box model-answer">
                  <div class="answer-label">✅ 모범 답안</div>
                  <p>{{ qEval.modelAnswer || '(모범답안 없음)' }}</p>
                </div>
              </div>

              <!-- 피드백 -->
              <div class="feedback-box">
                <div class="feedback-label">💬 피드백</div>
                <p>{{ qEval.feedback }}</p>
              </div>

              <!-- 개선 포인트 -->
              <div v-if="qEval.improvements && qEval.improvements.length" class="improvements-box">
                <div class="improvements-label">🔧 개선 포인트</div>
                <ul>
                  <li v-for="(imp, i) in qEval.improvements" :key="i">{{ imp }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <hr class="divider" />

        <!-- 종합 평가 -->
        <div class="summary-section">
          <h3>[ 수사관 소견 ]</h3>
          <div class="summary-box">
            <div class="detective-comment">
              <img src="/image/duck_det.png" alt="Detective Duck" class="comment-avatar" />
              <p>"{{ detectiveComment }}"</p>
            </div>
          </div>
        </div>

        <!-- 강점 & 개선점 -->
        <div class="feedback-grid">
          <div v-if="result.strengths && result.strengths.length" class="feedback-card strengths">
            <h4>✅ 유리한 증거</h4>
            <ul>
              <li v-for="s in result.strengths" :key="s">{{ s }}</li>
            </ul>
          </div>
          <div v-if="result.weaknesses && result.weaknesses.length" class="feedback-card weaknesses">
            <h4>⚠️ 불리한 증거</h4>
            <ul>
              <li v-for="w in result.weaknesses" :key="w">{{ w }}</li>
            </ul>
          </div>
        </div>

        <!-- 제안 사항 -->
        <div v-if="result.suggestions && result.suggestions.length" class="suggestions-section">
          <h4>💡 수사관 조언</h4>
          <ul>
            <li v-for="s in result.suggestions" :key="s">{{ s }}</li>
          </ul>
        </div>

        <!-- 버튼 -->
        <div class="action-buttons">
          <button class="btn-retry" @click="$emit('retry')">
            재수사 요청 (RETRY)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// 카테고리별 이모지 매핑
const CATEGORY_EMOJI = {
  '신뢰성': '🏗️',
  '성능': '⚡',
  '운영': '🤖',
  '비용': '💰',
  '보안': '🔐',
  '지속가능성': '🌱'
};

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
  data() {
    return {
      showStamp: false
    };
  },
  computed: {
    currentDate() {
      return new Date().toISOString().split('T')[0];
    },
    verdictClass() {
      const score = this.result?.score || 0;
      if (score >= 80) return 'innocent';
      if (score >= 50) return 'suspicious';
      return 'guilty';
    },
    verdictStamp() {
      const score = this.result?.score || 0;
      if (score >= 80) return 'INNOCENT';
      if (score >= 50) return 'SUSPICIOUS';
      return 'GUILTY';
    },
    verdictIcon() {
      const score = this.result?.score || 0;
      if (score >= 80) return '🎉';
      if (score >= 50) return '🤔';
      return '🚨';
    },
    verdictMessage() {
      const score = this.result?.score || 0;
      if (score >= 80) return 'ㅇㅋ 결백하군. 집으로 보내줄게. 꽥!';
      if (score >= 50) return '흐음... 좀 의심스러운데 일단 보류다. 꽥!';
      return '뭐야 이자식! 범인이다! 당장 체포해! 꽥!';
    },
    detectiveComment() {
      return this.result?.summary || '수사 기록을 분석한 결과입니다. 꽥!';
    },
    // 평가된 기둥만 추출 (questionEvaluations 기반)
    evaluatedPillars() {
      if (!this.result?.questionEvaluations?.length) return [];
      return this.result.questionEvaluations.map(qEval => ({
        category: qEval.category,
        score: qEval.score,
        emoji: CATEGORY_EMOJI[qEval.category] || '📊'
      }));
    }
  },
  watch: {
    result: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.showStamp = false;
          setTimeout(() => {
            this.showStamp = true;
          }, 500);
        }
      }
    }
  },
  methods: {
    getScoreClass(score) {
      if (score >= 80) return 'excellent';
      if (score >= 60) return 'good';
      if (score >= 40) return 'needs-improvement';
      return 'poor';
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Courier+Prime:wght@400;700&display=swap');

.case-closed-screen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #1a1a1a;
  z-index: 2000;
  overflow-y: auto;
  font-family: 'Courier Prime', monospace;
}

.bg-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(241, 196, 15, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.result-container {
  position: relative;
  max-width: 700px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* Loading */
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
  border: 4px solid rgba(241, 196, 15, 0.2);
  border-top-color: #f1c40f;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 30px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: #f1c40f;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.8rem;
}

/* Result Report */
.result-report {
  background: #f4f3ee;
  color: #1a1a1a;
  padding: 40px;
  border: 4px solid black;
  box-shadow: 20px 20px 0 black;
  position: relative;
}

/* Stamp */
.stamp-mark {
  position: absolute;
  top: 40px;
  right: 30px;
  font-family: 'Press Start 2P', cursive;
  font-size: 1.2rem;
  padding: 10px 15px;
  border: 4px solid;
  transform: rotate(12deg);
  opacity: 0;
  transition: all 0.3s ease;
}

.stamp-mark.stamped {
  opacity: 1;
  transform: rotate(12deg) scale(1);
}

.stamp-mark.innocent { border-color: #27ae60; color: #27ae60; }
.stamp-mark.suspicious { border-color: #f39c12; color: #f39c12; }
.stamp-mark.guilty { border-color: #e74c3c; color: #e74c3c; }

/* Header */
.report-title {
  font-family: 'Press Start 2P', cursive;
  font-size: 1.5rem;
  text-align: center;
  margin-bottom: 20px;
  color: #1a1a1a;
}

.report-meta {
  font-size: 0.9rem;
  color: #555;
}

.report-meta p {
  margin: 5px 0;
}

.divider {
  border: none;
  border-top: 2px dashed #999;
  margin: 25px 0;
}

/* Verdict */
.verdict-section h2 {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.9rem;
  margin-bottom: 15px;
}

.verdict-box {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  border: 3px solid;
  margin-bottom: 15px;
}

.verdict-box.innocent { border-color: #27ae60; background: rgba(39, 174, 96, 0.1); }
.verdict-box.suspicious { border-color: #f39c12; background: rgba(243, 156, 18, 0.1); }
.verdict-box.guilty { border-color: #e74c3c; background: rgba(231, 76, 60, 0.1); }

.verdict-icon { font-size: 2.5rem; }
.verdict-text { font-size: 1.1rem; font-weight: bold; }

.score-display { text-align: center; }

.score-value {
  font-family: 'Press Start 2P', cursive;
  font-size: 2rem;
}

.score-value.innocent { color: #27ae60; }
.score-value.suspicious { color: #f39c12; }
.score-value.guilty { color: #e74c3c; }

.score-unit { font-size: 1rem; color: #777; }

/* Section */
.eval-section h3 {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.75rem;
  margin-bottom: 15px;
  color: #333;
}

/* Pillar Grid */
.pillar-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.pillar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 10px;
  border: 2px solid #ddd;
  background: white;
  text-align: center;
}

.pillar-item.excellent { border-color: #27ae60; background: rgba(39, 174, 96, 0.08); }
.pillar-item.good { border-color: #3498db; background: rgba(52, 152, 219, 0.08); }
.pillar-item.needs-improvement { border-color: #f39c12; background: rgba(243, 156, 18, 0.08); }
.pillar-item.poor { border-color: #e74c3c; background: rgba(231, 76, 60, 0.08); }

.pillar-emoji { font-size: 1.5rem; margin-bottom: 6px; }
.pillar-name { font-size: 0.75rem; font-weight: bold; color: #333; margin-bottom: 4px; }
.pillar-score { font-family: 'Press Start 2P', cursive; font-size: 0.65rem; }

/* Question Evaluations */
.question-eval-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-eval-card {
  background: rgba(255, 255, 255, 0.9);
  border-left: 5px solid #3498db;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.question-eval-card.excellent { border-left-color: #27ae60; }
.question-eval-card.good { border-left-color: #3498db; }
.question-eval-card.needs-improvement { border-left-color: #f39c12; }
.question-eval-card.poor { border-left-color: #e74c3c; }

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #ddd;
}

.question-category {
  background: #34495e;
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: bold;
}

.question-score {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.9rem;
}

.question-score.excellent { color: #27ae60; }
.question-score.good { color: #3498db; }
.question-score.needs-improvement { color: #f39c12; }
.question-score.poor { color: #e74c3c; }

.question-text {
  font-size: 1rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 15px 0;
  line-height: 1.5;
}

.answer-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
}

.answer-box {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.answer-box.user-answer { border-left: 3px solid #9b59b6; }
.answer-box.model-answer { border-left: 3px solid #27ae60; background: #f0fff4; }

.answer-label {
  font-size: 0.8rem;
  font-weight: bold;
  color: #555;
  margin-bottom: 8px;
}

.answer-box p {
  margin: 0;
  font-size: 0.9rem;
  color: #333;
  line-height: 1.6;
  white-space: pre-wrap;
}

.feedback-box {
  background: #fff8e1;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #ffecb3;
  margin-bottom: 15px;
}

.feedback-label {
  font-size: 0.8rem;
  font-weight: bold;
  color: #f57c00;
  margin-bottom: 8px;
}

.feedback-box p {
  margin: 0;
  font-size: 0.9rem;
  color: #5d4037;
  line-height: 1.5;
}

.improvements-box {
  background: #e3f2fd;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #bbdefb;
}

.improvements-label {
  font-size: 0.8rem;
  font-weight: bold;
  color: #1565c0;
  margin-bottom: 8px;
}

.improvements-box ul { margin: 0; padding-left: 20px; }
.improvements-box li { font-size: 0.85rem; color: #1976d2; margin-bottom: 5px; }

/* Summary */
.summary-section h3 {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.75rem;
  margin-bottom: 15px;
}

.summary-box {
  background: rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.detective-comment {
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.comment-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 3px solid #f1c40f;
}

.detective-comment p {
  flex: 1;
  font-size: 1rem;
  font-style: italic;
  margin: 0;
  line-height: 1.6;
}

/* Feedback Grid */
.feedback-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin: 20px 0;
}

.feedback-card {
  padding: 15px;
  border: 2px solid;
}

.feedback-card.strengths { border-color: #27ae60; background: rgba(39, 174, 96, 0.05); }
.feedback-card.weaknesses { border-color: #e74c3c; background: rgba(231, 76, 60, 0.05); }

.feedback-card h4 { margin: 0 0 10px 0; font-size: 0.9rem; }
.feedback-card ul { margin: 0; padding-left: 18px; }
.feedback-card li { font-size: 0.85rem; margin-bottom: 5px; line-height: 1.4; }

/* Suggestions */
.suggestions-section {
  background: rgba(52, 152, 219, 0.1);
  border: 2px solid #3498db;
  padding: 15px;
  margin-bottom: 20px;
}

.suggestions-section h4 { margin: 0 0 10px 0; font-size: 0.9rem; color: #2980b9; }
.suggestions-section ul { margin: 0; padding-left: 18px; }
.suggestions-section li { font-size: 0.85rem; color: #2c3e50; margin-bottom: 5px; }

/* Button */
.action-buttons { text-align: center; margin-top: 30px; }

.btn-retry {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.7rem;
  padding: 15px 30px;
  background: #1a1a1a;
  color: #f1c40f;
  border: 3px solid #f1c40f;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-retry:hover {
  background: #f1c40f;
  color: #1a1a1a;
}

/* Responsive */
@media (max-width: 600px) {
  .pillar-grid { grid-template-columns: repeat(2, 1fr); }
  .answer-comparison { grid-template-columns: 1fr; }
  .feedback-grid { grid-template-columns: 1fr; }
  .stamp-mark { font-size: 1rem; top: 30px; right: 15px; }
}
</style>