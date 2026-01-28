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

        <!-- 아키텍처 평가 -->
        <div v-if="result.architectureEvaluation" class="eval-section">
          <h3>[ 설계도 분석 결과 ] ({{ result.architectureEvaluation.score || 0 }}/50점)</h3>

          <div v-if="result.architectureEvaluation.details && result.architectureEvaluation.details.length" class="eval-details">
            <div v-for="(detail, idx) in result.architectureEvaluation.details" :key="idx" class="eval-item">
              <div class="eval-item-header">
                <span class="eval-item-name">{{ detail.item }}</span>
                <span class="eval-item-score" :class="getScoreClass(detail.score * 4)">{{ detail.score }}점</span>
              </div>
              <p class="eval-item-basis">{{ detail.basis }}</p>
            </div>
          </div>

          <!-- 누락된 컴포넌트 -->
          <div v-if="result.architectureEvaluation.missingComponents && result.architectureEvaluation.missingComponents.length" class="missing-section">
            <strong>❌ 누락된 증거:</strong>
            <div class="tag-list">
              <span v-for="comp in result.architectureEvaluation.missingComponents" :key="comp" class="tag missing">
                {{ comp }}
              </span>
            </div>
          </div>

          <!-- 잘못된 연결 -->
          <div v-if="result.architectureEvaluation.incorrectFlows && result.architectureEvaluation.incorrectFlows.length" class="incorrect-section">
            <strong>⚠️ 의심스러운 연결:</strong>
            <div class="tag-list">
              <span v-for="flow in result.architectureEvaluation.incorrectFlows" :key="flow" class="tag incorrect">
                {{ flow }}
              </span>
            </div>
          </div>
        </div>

        <hr class="divider" />

        <!-- 심문 평가 -->
        <div v-if="result.interviewEvaluation" class="eval-section">
          <h3>[ 심문 기록 분석 ] ({{ result.interviewEvaluation.score || 0 }}/50점)</h3>

          <div v-if="result.interviewEvaluation.questionAnalysis && result.interviewEvaluation.questionAnalysis.length" class="question-list">
            <div v-for="(qa, idx) in result.interviewEvaluation.questionAnalysis" :key="idx" class="question-item" :class="qa.matchStatus">
              <div class="question-header">
                <span class="question-number">Q{{ idx + 1 }}</span>
                <span v-if="qa.category" class="question-category">{{ qa.category }}</span>
                <span class="match-badge" :class="qa.matchStatus">
                  {{ matchStatusText(qa.matchStatus) }}
                </span>
                <span class="question-score">{{ qa.score }}점</span>
              </div>
              <p class="question-text">{{ qa.question }}</p>
              <div class="answer-comparison">
                <div class="user-answer-box">
                  <span class="box-label">[용의자 진술]</span>
                  <p>{{ qa.userAnswer || '(묵비권 행사)' }}</p>
                </div>
                <div class="model-answer-box">
                  <span class="box-label">[모범 답안]</span>
                  <p>{{ qa.modelAnswer }}</p>
                </div>
              </div>
              <div v-if="qa.deductionReason" class="deduction-reason">
                <strong>감점 사유:</strong> {{ qa.deductionReason }}
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
      const now = new Date();
      return now.toISOString().split('T')[0];
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
      if (score >= 90) return 'excellent';
      if (score >= 70) return 'good';
      if (score >= 50) return 'needs-improvement';
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

/* Result Report (종이 스타일) */
.result-report {
  background: #f4f3ee;
  color: #1a1a1a;
  padding: 40px;
  border: 4px solid black;
  box-shadow: 20px 20px 0 black;
  position: relative;
}

/* 스탬프 */
.stamp-mark {
  position: absolute;
  top: 60px;
  right: 30px;
  border: 8px solid;
  font-family: 'Press Start 2P', cursive;
  font-size: 1.5rem;
  padding: 10px 15px;
  transform: rotate(-15deg) scale(0);
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  text-align: center;
}

.stamp-mark.stamped {
  transform: rotate(-15deg) scale(1);
  opacity: 1;
}

.stamp-mark.innocent {
  border-color: #27ae60;
  color: #27ae60;
}

.stamp-mark.suspicious {
  border-color: #f39c12;
  color: #f39c12;
}

.stamp-mark.guilty {
  border-color: #e74c3c;
  color: #e74c3c;
}

.report-title {
  text-align: center;
  font-family: 'Press Start 2P', cursive;
  font-size: 1.5rem;
  margin: 0 0 20px 0;
  border-bottom: 4px double #000;
  padding-bottom: 15px;
}

.report-meta {
  margin-bottom: 20px;
}

.report-meta p {
  margin: 5px 0;
  font-size: 0.9rem;
}

.divider {
  border: none;
  border-top: 2px dashed #bdc3c7;
  margin: 25px 0;
}

/* 판결 섹션 */
.verdict-section {
  text-align: center;
}

.verdict-section h2 {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.9rem;
  margin-bottom: 20px;
}

.verdict-box {
  padding: 20px;
  border: 4px solid;
  margin-bottom: 15px;
}

.verdict-box.innocent {
  background: rgba(39, 174, 96, 0.1);
  border-color: #27ae60;
}

.verdict-box.suspicious {
  background: rgba(243, 156, 18, 0.1);
  border-color: #f39c12;
}

.verdict-box.guilty {
  background: rgba(231, 76, 60, 0.1);
  border-color: #e74c3c;
}

.verdict-icon {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.verdict-text {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.7rem;
  line-height: 1.8;
}

.score-display {
  margin-top: 15px;
}

.score-value {
  font-family: 'Press Start 2P', cursive;
  font-size: 2rem;
}

.score-value.innocent { color: #27ae60; }
.score-value.suspicious { color: #f39c12; }
.score-value.guilty { color: #e74c3c; }

.score-unit {
  font-size: 1rem;
  color: #7f8c8d;
}

/* 평가 섹션 */
.eval-section {
  margin: 20px 0;
}

.eval-section h3 {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.7rem;
  margin-bottom: 15px;
  color: #2c3e50;
}

.eval-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.eval-item {
  background: rgba(0, 0, 0, 0.05);
  padding: 12px;
  border-left: 4px solid #3498db;
}

.eval-item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.eval-item-name {
  font-weight: bold;
}

.eval-item-score {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.7rem;
}

.eval-item-score.excellent { color: #27ae60; }
.eval-item-score.good { color: #3498db; }
.eval-item-score.needs-improvement { color: #f39c12; }
.eval-item-score.poor { color: #e74c3c; }

.eval-item-basis {
  font-size: 0.85rem;
  color: #555;
  margin: 0;
}

/* 태그 리스트 */
.missing-section,
.incorrect-section {
  margin-top: 15px;
  font-size: 0.9rem;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.tag {
  padding: 4px 10px;
  font-size: 0.8rem;
  border: 2px solid;
}

.tag.missing {
  background: rgba(231, 76, 60, 0.1);
  border-color: #e74c3c;
  color: #e74c3c;
}

.tag.incorrect {
  background: rgba(243, 156, 18, 0.1);
  border-color: #f39c12;
  color: #f39c12;
}

/* 질문 리스트 */
.question-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.question-item {
  background: rgba(0, 0, 0, 0.05);
  padding: 15px;
  border-left: 4px solid #3498db;
}

.question-item.match { border-left-color: #27ae60; }
.question-item.partial { border-left-color: #f39c12; }
.question-item.mismatch { border-left-color: #e74c3c; }

.question-header {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.question-number {
  background: #2c3e50;
  color: white;
  padding: 2px 8px;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.5rem;
}

.question-category {
  background: rgba(241, 196, 15, 0.2);
  color: #f39c12;
  padding: 2px 8px;
  font-size: 0.75rem;
}

.match-badge {
  padding: 2px 8px;
  font-size: 0.75rem;
  border: 1px solid;
}

.match-badge.match {
  background: rgba(39, 174, 96, 0.1);
  border-color: #27ae60;
  color: #27ae60;
}

.match-badge.partial {
  background: rgba(243, 156, 18, 0.1);
  border-color: #f39c12;
  color: #f39c12;
}

.match-badge.mismatch {
  background: rgba(231, 76, 60, 0.1);
  border-color: #e74c3c;
  color: #e74c3c;
}

.question-score {
  margin-left: auto;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.6rem;
}

.question-text {
  margin: 0 0 10px 0;
  font-size: 0.9rem;
}

.answer-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.user-answer-box,
.model-answer-box {
  padding: 10px;
  background: white;
  border: 2px solid #bdc3c7;
}

.box-label {
  display: block;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.5rem;
  margin-bottom: 5px;
}

.user-answer-box .box-label { color: #3498db; }
.model-answer-box .box-label { color: #27ae60; }

.user-answer-box p,
.model-answer-box p {
  margin: 0;
  font-size: 0.85rem;
  color: #555;
}

.deduction-reason {
  margin-top: 10px;
  padding: 8px;
  background: rgba(231, 76, 60, 0.1);
  font-size: 0.85rem;
  color: #e74c3c;
}

/* 종합 평가 */
.summary-section h3 {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.7rem;
  margin-bottom: 15px;
}

.summary-box {
  background: #000;
  padding: 15px;
}

.detective-comment {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.comment-avatar {
  width: 60px;
  height: 60px;
  border: 3px solid #f1c40f;
  background: #81ecec;
  flex-shrink: 0;
}

.detective-comment p {
  color: #f1c40f;
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0;
}

/* 피드백 그리드 */
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

.feedback-card.strengths {
  background: rgba(39, 174, 96, 0.05);
  border-color: #27ae60;
}

.feedback-card.weaknesses {
  background: rgba(231, 76, 60, 0.05);
  border-color: #e74c3c;
}

.feedback-card h4 {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.6rem;
  margin: 0 0 10px 0;
}

.feedback-card.strengths h4 { color: #27ae60; }
.feedback-card.weaknesses h4 { color: #e74c3c; }

.feedback-card ul {
  margin: 0;
  padding-left: 18px;
}

.feedback-card li {
  font-size: 0.85rem;
  margin-bottom: 5px;
  color: #555;
}

/* 제안 섹션 */
.suggestions-section {
  margin: 20px 0;
  padding: 15px;
  background: rgba(52, 152, 219, 0.05);
  border: 2px solid #3498db;
}

.suggestions-section h4 {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.6rem;
  color: #3498db;
  margin: 0 0 10px 0;
}

.suggestions-section ul {
  margin: 0;
  padding-left: 18px;
}

.suggestions-section li {
  font-size: 0.85rem;
  margin-bottom: 5px;
  color: #555;
}

/* 버튼 */
.action-buttons {
  text-align: center;
  margin-top: 30px;
}

.btn-retry {
  padding: 15px 30px;
  background: #f1c40f;
  border: 4px solid #000;
  color: #000;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.7rem;
  cursor: pointer;
  box-shadow: 6px 6px 0 rgba(0, 0, 0, 0.8);
  transition: all 0.2s;
}

.btn-retry:hover {
  transform: translate(-2px, -2px);
  box-shadow: 8px 8px 0 rgba(0, 0, 0, 0.8);
}

.btn-retry:active {
  transform: translate(2px, 2px);
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.8);
}

@media (max-width: 600px) {
  .answer-comparison {
    grid-template-columns: 1fr;
  }

  .feedback-grid {
    grid-template-columns: 1fr;
  }

  .stamp-mark {
    font-size: 1rem;
    top: 30px;
    right: 15px;
  }
}
</style>
