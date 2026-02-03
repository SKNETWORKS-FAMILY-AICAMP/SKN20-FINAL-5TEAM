<template>
  <div class="case-closed-screen">
    <div class="bg-overlay"></div>

    <div class="result-container">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner-xl"></div>
        <p>GENERATING_REPORT... 꽥!</p>
      </div>

      <!-- Result Content -->
      <div v-else-if="result" class="result-report">
        <!-- 스탬프 마크 -->
        <div class="stamp-mark" :class="[verdictClass, { stamped: showStamp }]">
          {{ verdictStamp }}
        </div>

        <!-- 헤더 -->
        <h1 class="report-title">SYSTEM_REPORT</h1>
        <div class="report-meta">
          <p><strong>DATE:</strong> {{ currentDate }}</p>
          <p><strong>OPERATOR:</strong> CODUCK_AI</p>
          <p v-if="problem"><strong>MISSION:</strong> {{ problem.title }}</p>
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
          <div class="pillar-hint-box">
            <span class="hint-icon">👆</span>
            <span class="hint-text">각 카드를 클릭하면 상세 해설을 확인할 수 있습니다</span>
          </div>
          <div class="pillar-grid">
            <div
              v-for="(pillar, idx) in evaluatedPillars"
              :key="pillar.category"
              class="pillar-item clickable"
              :class="getScoreClass(pillar.score)"
              @click="openDetailModal(idx)"
            >
              <span class="pillar-emoji">{{ pillar.emoji }}</span>
              <span class="pillar-name">{{ pillar.category }}</span>
              <span class="pillar-score">{{ pillar.score }}점</span>
              <span class="detail-hint">🔍 상세 해설 보기</span>
            </div>
          </div>
        </div>

        <!-- 상세 해설 모달 -->
        <div v-if="showDetailModal && selectedEvaluation" class="modal-overlay" @click.self="closeDetailModal">
          <div class="detail-modal" :class="getScoreClass(selectedEvaluation.score)">
            <button class="modal-close" @click="closeDetailModal">&times;</button>

            <!-- 모달 헤더 -->
            <div class="modal-header">
              <span class="modal-category">{{ selectedEvaluation.category }}</span>
              <span class="modal-score" :class="getScoreClass(selectedEvaluation.score)">{{ selectedEvaluation.score }}점</span>
            </div>

            <!-- 질문 내용 -->
            <div class="modal-section">
              <p class="modal-question">❓ {{ selectedEvaluation.question }}</p>
            </div>

            <!-- 답변 비교 -->
            <div class="modal-answers">
              <div class="modal-answer-box user-answer">
                <div class="answer-label">📝 나의 답변</div>
                <p>{{ selectedEvaluation.userAnswer || '(답변 없음)' }}</p>
              </div>
              <div class="modal-answer-box model-answer">
                <div class="answer-label">✅ 모범 답안</div>
                <p>{{ selectedEvaluation.modelAnswer || '(모범답안 없음)' }}</p>
              </div>
            </div>

            <!-- 피드백 -->
            <div class="modal-feedback">
              <div class="feedback-label">💬 피드백</div>
              <p>{{ selectedEvaluation.feedback }}</p>
            </div>

            <!-- 개선 포인트 -->
            <div v-if="selectedEvaluation.improvements && selectedEvaluation.improvements.length" class="modal-improvements">
              <div class="improvements-label">🔧 개선 포인트</div>
              <ul>
                <li v-for="(imp, i) in selectedEvaluation.improvements" :key="i">{{ imp }}</li>
              </ul>
            </div>
          </div>
        </div>

        <hr class="divider" />

        <!-- 종합 평가 -->
        <div class="summary-section">
          <h3>[ SYSTEM_ANALYSIS ]</h3>
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
            <h4>✅ STRENGTHS</h4>
            <ul>
              <li v-for="s in result.strengths" :key="s">{{ s }}</li>
            </ul>
          </div>
          <div v-if="result.weaknesses && result.weaknesses.length" class="feedback-card weaknesses">
            <h4>⚠️ IMPROVEMENTS</h4>
            <ul>
              <li v-for="w in result.weaknesses" :key="w">{{ w }}</li>
            </ul>
          </div>
        </div>

        <!-- 제안 사항 -->
        <div v-if="result.suggestions && result.suggestions.length" class="suggestions-section">
          <h4>💡 RECOMMENDATIONS</h4>
          <ul>
            <li v-for="s in result.suggestions" :key="s">{{ s }}</li>
          </ul>
        </div>

        <!-- 버튼 -->
        <div class="action-buttons">
          <button class="btn-retry" @click="$emit('retry')">
            RETRY_PROTOCOL
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
      showStamp: false,
      showDetailModal: false,
      selectedEvaluationIndex: null
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
      if (score >= 80) return 'APPROVED';
      if (score >= 50) return 'REVIEW';
      return 'REJECTED';
    },
    verdictIcon() {
      const score = this.result?.score || 0;
      if (score >= 80) return '✅';
      if (score >= 50) return '⚠️';
      return '❌';
    },
    verdictMessage() {
      const score = this.result?.score || 0;
      if (score >= 80) return '시스템 복구 성공! 아키텍처가 승인되었습니다. 꽥!';
      if (score >= 50) return '부분적 복구 완료. 추가 검토가 필요합니다. 꽥!';
      return '시스템 복구 실패. 아키텍처 재설계가 필요합니다. 꽥!';
    },
    detectiveComment() {
      return this.result?.summary || '시스템 분석 결과입니다. 꽥!';
    },
    // 평가된 기둥만 추출 (questionEvaluations 기반)
    evaluatedPillars() {
      if (!this.result?.questionEvaluations?.length) return [];
      return this.result.questionEvaluations.map(qEval => ({
        category: qEval.category,
        score: qEval.score,
        emoji: CATEGORY_EMOJI[qEval.category] || '📊'
      }));
    },
    // 선택된 평가 항목
    selectedEvaluation() {
      if (this.selectedEvaluationIndex === null || !this.result?.questionEvaluations) return null;
      return this.result.questionEvaluations[this.selectedEvaluationIndex];
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
    },
    openDetailModal(index) {
      this.selectedEvaluationIndex = index;
      this.showDetailModal = true;
      document.body.style.overflow = 'hidden';
    },
    closeDetailModal() {
      this.showDetailModal = false;
      this.selectedEvaluationIndex = null;
      document.body.style.overflow = '';
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap');

.case-closed-screen {
  --accent-green: #A3FF47;
  --accent-cyan: #00f3ff;
  --accent-pink: #ec4899;
  --bg-dark: #05070A;
  --terminal-font: 'Fira Code', monospace;

  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--bg-dark);
  z-index: 2000;
  overflow-y: auto;
  font-family: var(--terminal-font);
}

/* 스크롤바 커스텀 */
.case-closed-screen::-webkit-scrollbar {
  width: 4px;
}

.case-closed-screen::-webkit-scrollbar-track {
  background: transparent;
}

.case-closed-screen::-webkit-scrollbar-thumb {
  background: rgba(163, 255, 71, 0.2);
  border-radius: 10px;
}

.bg-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(163, 255, 71, 0.05) 0%, transparent 70%);
  pointer-events: none;
}

.result-container {
  position: relative;
  max-width: 750px;
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
  width: 70px;
  height: 70px;
  border: 3px solid rgba(163, 255, 71, 0.2);
  border-top-color: var(--accent-green);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 30px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: var(--accent-green);
  font-family: var(--terminal-font);
  font-size: 0.85rem;
  text-shadow: 0 0 10px rgba(163, 255, 71, 0.5);
}

/* Result Report */
.result-report {
  background: rgba(163, 255, 71, 0.03);
  color: #ecf0f1;
  padding: 40px;
  border: 1px solid rgba(163, 255, 71, 0.3);
  position: relative;
}

/* Stamp */
.stamp-mark {
  position: absolute;
  top: 40px;
  right: 30px;
  font-family: var(--terminal-font);
  font-size: 0.9rem;
  font-weight: 700;
  padding: 10px 15px;
  border: 2px solid;
  transform: rotate(12deg);
  opacity: 0;
  transition: all 0.3s ease;
  letter-spacing: 2px;
}

.stamp-mark.stamped {
  opacity: 1;
  transform: rotate(12deg) scale(1);
}

.stamp-mark.innocent { border-color: var(--accent-green); color: var(--accent-green); box-shadow: 0 0 15px rgba(163, 255, 71, 0.3); }
.stamp-mark.suspicious { border-color: var(--accent-cyan); color: var(--accent-cyan); box-shadow: 0 0 15px rgba(0, 243, 255, 0.3); }
.stamp-mark.guilty { border-color: var(--accent-pink); color: var(--accent-pink); box-shadow: 0 0 15px rgba(236, 72, 153, 0.3); }

/* Header */
.report-title {
  font-family: var(--terminal-font);
  font-size: 1.5rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 20px;
  color: var(--accent-green);
  letter-spacing: 4px;
  text-shadow: 0 0 20px rgba(163, 255, 71, 0.5);
}

.report-meta {
  font-size: 0.8rem;
  color: rgba(163, 255, 71, 0.6);
}

.report-meta p {
  margin: 5px 0;
}

.divider {
  border: none;
  border-top: 1px dashed rgba(163, 255, 71, 0.2);
  margin: 25px 0;
}

/* Verdict */
.verdict-section h2 {
  font-family: var(--terminal-font);
  font-size: 0.8rem;
  margin-bottom: 15px;
  color: var(--accent-green);
  letter-spacing: 2px;
}

.verdict-box {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  border: 1px solid;
  margin-bottom: 15px;
  background: rgba(0, 0, 0, 0.3);
}

.verdict-box.innocent { border-color: var(--accent-green); background: rgba(163, 255, 71, 0.05); }
.verdict-box.suspicious { border-color: var(--accent-cyan); background: rgba(0, 243, 255, 0.05); }
.verdict-box.guilty { border-color: var(--accent-pink); background: rgba(236, 72, 153, 0.05); }

.verdict-icon { font-size: 2.5rem; }
.verdict-text { font-size: 1rem; font-weight: 500; color: #ecf0f1; }

.score-display { text-align: center; }

.score-value {
  font-family: var(--terminal-font);
  font-size: 2rem;
  font-weight: 700;
}

.score-value.innocent { color: var(--accent-green); text-shadow: 0 0 15px rgba(163, 255, 71, 0.5); }
.score-value.suspicious { color: var(--accent-cyan); text-shadow: 0 0 15px rgba(0, 243, 255, 0.5); }
.score-value.guilty { color: var(--accent-pink); text-shadow: 0 0 15px rgba(236, 72, 153, 0.5); }

.score-unit { font-size: 0.9rem; color: rgba(163, 255, 71, 0.5); }

/* Section */
.eval-section h3 {
  font-family: var(--terminal-font);
  font-size: 0.7rem;
  margin-bottom: 15px;
  color: var(--accent-green);
  letter-spacing: 1px;
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
  border: 1px solid rgba(163, 255, 71, 0.2);
  background: rgba(163, 255, 71, 0.03);
  text-align: center;
}

.pillar-item.excellent { border-color: var(--accent-green); background: rgba(163, 255, 71, 0.08); }
.pillar-item.good { border-color: var(--accent-cyan); background: rgba(0, 243, 255, 0.08); }
.pillar-item.needs-improvement { border-color: #f39c12; background: rgba(243, 156, 18, 0.08); }
.pillar-item.poor { border-color: var(--accent-pink); background: rgba(236, 72, 153, 0.08); }

.pillar-emoji { font-size: 1.5rem; margin-bottom: 6px; }
.pillar-name { font-size: 0.7rem; font-weight: 500; color: rgba(236, 240, 241, 0.8); margin-bottom: 4px; }
.pillar-score { font-family: var(--terminal-font); font-size: 0.7rem; font-weight: 700; color: var(--accent-green); }

.pillar-hint-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(0, 243, 255, 0.08);
  border: 1px dashed rgba(0, 243, 255, 0.3);
  padding: 8px 12px;
  margin-bottom: 15px;
}

.hint-icon { font-size: 0.9rem; }
.hint-text { font-size: 0.7rem; color: var(--accent-cyan); }

.pillar-item.clickable {
  cursor: pointer;
  transition: all 0.2s ease;
}

.pillar-item.clickable:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 20px rgba(163, 255, 71, 0.2);
}


.detail-hint {
  font-size: 0.65rem;
  color: var(--accent-cyan);
  margin-top: 8px;
  padding: 4px 8px;
  background: rgba(0, 243, 255, 0.1);
  border: 1px solid rgba(0, 243, 255, 0.3);
  transition: all 0.2s ease;
}

.pillar-item.clickable:hover .detail-hint {
  background: rgba(0, 243, 255, 0.2);
  border-color: var(--accent-cyan);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(5, 7, 10, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  padding: 20px;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.detail-modal {
  background: rgba(10, 15, 20, 0.98);
  border: 1px solid rgba(163, 255, 71, 0.3);
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  padding: 30px;
  position: relative;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.detail-modal.excellent { border-color: var(--accent-green); box-shadow: 0 0 30px rgba(163, 255, 71, 0.2); }
.detail-modal.good { border-color: var(--accent-cyan); box-shadow: 0 0 30px rgba(0, 243, 255, 0.2); }
.detail-modal.needs-improvement { border-color: #f39c12; box-shadow: 0 0 30px rgba(243, 156, 18, 0.2); }
.detail-modal.poor { border-color: var(--accent-pink); box-shadow: 0 0 30px rgba(236, 72, 153, 0.2); }

.detail-modal::-webkit-scrollbar { width: 4px; }
.detail-modal::-webkit-scrollbar-thumb { background: rgba(163, 255, 71, 0.3); border-radius: 10px; }

.modal-close {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  color: rgba(163, 255, 71, 0.6);
  font-size: 1.5rem;
  cursor: pointer;
  transition: color 0.2s ease;
}

.modal-close:hover { color: var(--accent-green); }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px dashed rgba(163, 255, 71, 0.2);
}

.modal-category {
  background: var(--accent-green);
  color: #000;
  padding: 6px 14px;
  font-size: 0.8rem;
  font-weight: 700;
}

.modal-score {
  font-family: var(--terminal-font);
  font-size: 1.2rem;
  font-weight: 700;
}

.modal-score.excellent { color: var(--accent-green); }
.modal-score.good { color: var(--accent-cyan); }
.modal-score.needs-improvement { color: #f39c12; }
.modal-score.poor { color: var(--accent-pink); }

.modal-section { margin-bottom: 20px; }

.modal-question {
  font-size: 0.95rem;
  font-weight: 500;
  color: #ecf0f1;
  line-height: 1.6;
  margin: 0;
}

.modal-answers {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.modal-answer-box {
  background: rgba(0, 0, 0, 0.4);
  padding: 15px;
  border: 1px solid rgba(163, 255, 71, 0.1);
}

.modal-answer-box.user-answer { border-left: 3px solid var(--accent-cyan); }
.modal-answer-box.model-answer { border-left: 3px solid var(--accent-green); }

.modal-answer-box p {
  margin: 0;
  font-size: 0.85rem;
  color: rgba(236, 240, 241, 0.9);
  line-height: 1.6;
  white-space: pre-wrap;
}

.modal-feedback {
  background: rgba(163, 255, 71, 0.05);
  padding: 15px;
  border: 1px solid rgba(163, 255, 71, 0.2);
  margin-bottom: 15px;
}

.modal-feedback p {
  margin: 0;
  font-size: 0.85rem;
  color: rgba(236, 240, 241, 0.85);
  line-height: 1.6;
}

.modal-improvements {
  background: rgba(0, 243, 255, 0.05);
  padding: 15px;
  border: 1px solid rgba(0, 243, 255, 0.2);
}

.modal-improvements ul { margin: 0; padding-left: 20px; }
.modal-improvements li { font-size: 0.8rem; color: rgba(236, 240, 241, 0.8); margin-bottom: 5px; line-height: 1.5; }

@media (max-width: 600px) {
  .modal-answers { grid-template-columns: 1fr; }
}

/* Question Evaluations */
.question-eval-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-eval-card {
  background: rgba(163, 255, 71, 0.03);
  border-left: 3px solid var(--accent-cyan);
  padding: 20px;
}

.question-eval-card.excellent { border-left-color: var(--accent-green); }
.question-eval-card.good { border-left-color: var(--accent-cyan); }
.question-eval-card.needs-improvement { border-left-color: #f39c12; }
.question-eval-card.poor { border-left-color: var(--accent-pink); }

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px dashed rgba(163, 255, 71, 0.2);
}

.question-category {
  background: var(--accent-green);
  color: #000;
  padding: 4px 12px;
  font-size: 0.75rem;
  font-weight: 700;
}

.question-score {
  font-family: var(--terminal-font);
  font-size: 0.85rem;
  font-weight: 700;
}

.question-score.excellent { color: var(--accent-green); }
.question-score.good { color: var(--accent-cyan); }
.question-score.needs-improvement { color: #f39c12; }
.question-score.poor { color: var(--accent-pink); }

.question-text {
  font-size: 0.9rem;
  font-weight: 500;
  color: #ecf0f1;
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
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border: 1px solid rgba(163, 255, 71, 0.1);
}

.answer-box.user-answer { border-left: 3px solid var(--accent-cyan); }
.answer-box.model-answer { border-left: 3px solid var(--accent-green); }

.answer-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: rgba(163, 255, 71, 0.7);
  margin-bottom: 8px;
}

.answer-box p {
  margin: 0;
  font-size: 0.85rem;
  color: rgba(236, 240, 241, 0.9);
  line-height: 1.6;
  white-space: pre-wrap;
}

.feedback-box {
  background: rgba(163, 255, 71, 0.05);
  padding: 15px;
  border: 1px solid rgba(163, 255, 71, 0.2);
  margin-bottom: 15px;
}

.feedback-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--accent-green);
  margin-bottom: 8px;
}

.feedback-box p {
  margin: 0;
  font-size: 0.85rem;
  color: rgba(236, 240, 241, 0.85);
  line-height: 1.5;
}

.improvements-box {
  background: rgba(0, 243, 255, 0.05);
  padding: 15px;
  border: 1px solid rgba(0, 243, 255, 0.2);
}

.improvements-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--accent-cyan);
  margin-bottom: 8px;
}

.improvements-box ul { margin: 0; padding-left: 20px; }
.improvements-box li { font-size: 0.8rem; color: rgba(236, 240, 241, 0.8); margin-bottom: 5px; }

/* Summary */
.summary-section h3 {
  font-family: var(--terminal-font);
  font-size: 0.7rem;
  margin-bottom: 15px;
  color: var(--accent-green);
  letter-spacing: 1px;
}

.summary-box {
  background: rgba(163, 255, 71, 0.03);
  padding: 20px;
  border: 1px solid rgba(163, 255, 71, 0.1);
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
  border: 2px solid var(--accent-green);
  box-shadow: 0 0 15px rgba(163, 255, 71, 0.3);
}

.detective-comment p {
  flex: 1;
  font-size: 0.9rem;
  font-style: italic;
  margin: 0;
  line-height: 1.6;
  color: rgba(236, 240, 241, 0.9);
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
  border: 1px solid;
  background: rgba(0, 0, 0, 0.2);
}

.feedback-card.strengths { border-color: var(--accent-green); }
.feedback-card.weaknesses { border-color: var(--accent-pink); }

.feedback-card h4 { margin: 0 0 10px 0; font-size: 0.8rem; color: var(--accent-green); }
.feedback-card.weaknesses h4 { color: var(--accent-pink); }
.feedback-card ul { margin: 0; padding-left: 18px; }
.feedback-card li { font-size: 0.8rem; margin-bottom: 5px; line-height: 1.4; color: rgba(236, 240, 241, 0.8); }

/* Suggestions */
.suggestions-section {
  background: rgba(0, 243, 255, 0.05);
  border: 1px solid rgba(0, 243, 255, 0.3);
  padding: 15px;
  margin-bottom: 20px;
}

.suggestions-section h4 { margin: 0 0 10px 0; font-size: 0.8rem; color: var(--accent-cyan); }
.suggestions-section ul { margin: 0; padding-left: 18px; }
.suggestions-section li { font-size: 0.8rem; color: rgba(236, 240, 241, 0.8); margin-bottom: 5px; }

/* Button */
.action-buttons { text-align: center; margin-top: 30px; }

.btn-retry {
  font-family: var(--terminal-font);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 14px 30px;
  background: transparent;
  color: var(--accent-green);
  border: 1px solid var(--accent-green);
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 2px;
}

.btn-retry:hover {
  background: var(--accent-green);
  color: #000;
  box-shadow: 0 0 25px rgba(163, 255, 71, 0.5);
}

/* Responsive */
@media (max-width: 600px) {
  .pillar-grid { grid-template-columns: repeat(2, 1fr); }
  .answer-comparison { grid-template-columns: 1fr; }
  .feedback-grid { grid-template-columns: 1fr; }
  .stamp-mark { font-size: 0.8rem; top: 30px; right: 15px; }
}
</style>