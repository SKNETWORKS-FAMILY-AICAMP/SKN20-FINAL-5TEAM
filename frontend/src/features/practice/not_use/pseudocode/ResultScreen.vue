<template>
  <div class="result-screen">
    <!-- 로딩 중 -->
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">평가 중입니다... 잠시만 기다려주세요!</p>
    </div>

    <!-- 평가 결과 -->
    <template v-else-if="result">
      <!-- 헤더 -->
      <div class="result-header">
        <div class="result-title">평가 결과</div>
        <div class="result-score" :class="getGradeClass(result.grade)">
          {{ result.totalScore }}점
        </div>
        <div class="result-grade" :class="getGradeClass(result.grade)">
          {{ getGradeText(result.grade) }}
        </div>
      </div>

      <!-- 종합 요약 -->
      <div class="result-summary">
        <h3>📝 종합 평가</h3>
        <p>{{ result.summary }}</p>
      </div>

      <!-- 점수 세부사항 -->
      <div class="score-details">
        <!-- Pseudocode 평가 -->
        <div class="score-section">
          <h3>💻 의사코드 평가 ({{ result.pseudocodeEvaluation?.score || 0 }}/50점)</h3>
          <div class="score-items">
            <div
              v-for="(detail, idx) in result.pseudocodeEvaluation?.details || []"
              :key="idx"
              class="score-item"
            >
              <div class="item-header">
                <span class="item-name">{{ detail.item }}</span>
                <span class="item-score">{{ detail.score }}점</span>
              </div>
              <p class="item-basis">{{ detail.basis }}</p>
            </div>
          </div>

          <!-- 강점/약점 -->
          <div class="feedback-lists">
            <div v-if="result.pseudocodeEvaluation?.strengths?.length" class="feedback-positive">
              <strong>✅ 강점:</strong>
              <ul>
                <li v-for="(item, idx) in result.pseudocodeEvaluation.strengths" :key="idx">
                  {{ item }}
                </li>
              </ul>
            </div>
            <div v-if="result.pseudocodeEvaluation?.weaknesses?.length" class="feedback-negative">
              <strong>⚠️ 약점:</strong>
              <ul>
                <li v-for="(item, idx) in result.pseudocodeEvaluation.weaknesses" :key="idx">
                  {{ item }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Interview 평가 -->
        <div class="score-section">
          <h3>🎤 면접 답변 평가 ({{ result.interviewEvaluation?.score || 0 }}/50점)</h3>
          
          <!-- 답변 분석 -->
          <div v-if="result.interviewEvaluation?.answerAnalysis" class="answer-analysis">
            <p>
              <strong>답변 길이:</strong> {{ result.interviewEvaluation.answerAnalysis.length }}자
            </p>
            <p v-if="result.interviewEvaluation.answerAnalysis.keyTermsFound?.length">
              <strong>발견된 키워드:</strong>
              {{ result.interviewEvaluation.answerAnalysis.keyTermsFound.join(', ') }}
            </p>
            <p v-if="result.interviewEvaluation.answerAnalysis.keyTermsMissing?.length">
              <strong>누락된 키워드:</strong>
              {{ result.interviewEvaluation.answerAnalysis.keyTermsMissing.join(', ') }}
            </p>
          </div>

          <!-- 질문별 분석 -->
          <div class="question-analysis">
            <div
              v-for="(qa, idx) in result.interviewEvaluation?.questionAnalysis || []"
              :key="idx"
              class="qa-item"
            >
              <div class="qa-header">
                <span class="qa-category">{{ qa.category }}</span>
                <span class="qa-score" :class="getMatchClass(qa.matchStatus)">
                  {{ qa.score }}점
                </span>
              </div>
              <p class="qa-question"><strong>Q:</strong> {{ qa.question }}</p>
              <p class="qa-user-answer"><strong>학생 답변:</strong> {{ qa.userAnswer || '(답변 없음)' }}</p>
              <p class="qa-model-answer"><strong>모범 답안:</strong> {{ qa.modelAnswer }}</p>
              <p class="qa-feedback" :class="getMatchClass(qa.matchStatus)">
                {{ qa.feedback }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 학습 제안 -->
      <div v-if="result.suggestions?.length" class="suggestions">
        <h3>💡 학습 제안</h3>
        <ul>
          <li v-for="(suggestion, idx) in result.suggestions" :key="idx">
            {{ suggestion }}
          </li>
        </ul>
      </div>

      <!-- 액션 버튼 -->
      <div class="action-buttons">
        <button @click="$emit('retry')" class="btn btn-retry">
          다시 도전하기
        </button>
        <button @click="$emit('close')" class="btn btn-close">
          닫기
        </button>
      </div>
    </template>
  </div>
</template>

<script>
export default {
  name: 'PseudocodeResultScreen',
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
  emits: ['retry', 'close'],
  methods: {
    getGradeClass(grade) {
      const gradeMap = {
        'excellent': 'grade-excellent',
        'good': 'grade-good',
        'needs-improvement': 'grade-needs-improvement',
        'poor': 'grade-poor'
      };
      return gradeMap[grade] || 'grade-poor';
    },
    getGradeText(grade) {
      const textMap = {
        'excellent': '🏆 Excellent',
        'good': '👍 Good',
        'needs-improvement': '📚 Needs Improvement',
        'poor': '💪 Keep Trying'
      };
      return textMap[grade] || 'Keep Trying';
    },
    getMatchClass(matchStatus) {
      const classMap = {
        'match': 'match-full',
        'partial': 'match-partial',
        'mismatch': 'match-none'
      };
      return classMap[matchStatus] || 'match-none';
    }
  }
};
</script>

<style scoped>
.result-screen {
  padding: 40px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  min-height: 100vh;
  color: #eaeaea;
}

/* =====================
   LOADING
===================== */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(241, 196, 15, 0.3);
  border-top-color: #f1c40f;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 1.2rem;
  color: #f1c40f;
}

/* =====================
   HEADER
===================== */
.result-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.result-title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 20px;
  color: #f1c40f;
}

.result-score {
  font-size: 4rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.result-grade {
  font-size: 1.5rem;
  font-weight: bold;
}

.grade-excellent { color: #2ecc71; }
.grade-good { color: #3498db; }
.grade-needs-improvement { color: #f39c12; }
.grade-poor { color: #e74c3c; }

/* =====================
   SUMMARY
===================== */
.result-summary {
  background: rgba(255, 255, 255, 0.05);
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 30px;
  border-left: 4px solid #f1c40f;
}

.result-summary h3 {
  margin-bottom: 15px;
  font-size: 1.3rem;
}

.result-summary p {
  line-height: 1.8;
  font-size: 1.1rem;
}

/* =====================
   SCORE DETAILS
===================== */
.score-details {
  display: grid;
  gap: 30px;
}

.score-section {
  background: rgba(255, 255, 255, 0.05);
  padding: 25px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.score-section h3 {
  margin-bottom: 20px;
  font-size: 1.3rem;
  color: #f1c40f;
}

.score-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.score-item {
  background: rgba(0, 0, 0, 0.2);
  padding: 15px;
  border-radius: 8px;
  border-left: 3px solid #3498db;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.item-name {
  font-weight: bold;
  color: #f1c40f;
}

.item-score {
  color: #2ecc71;
  font-weight: bold;
}

.item-basis {
  color: #bbb;
  font-size: 0.95rem;
  line-height: 1.6;
}

/* =====================
   FEEDBACK LISTS
===================== */
.feedback-lists {
  display: grid;
  gap: 15px;
  margin-top: 20px;
}

.feedback-positive,
.feedback-negative {
  padding: 15px;
  border-radius: 8px;
}

.feedback-positive {
  background: rgba(46, 204, 113, 0.1);
  border-left: 3px solid #2ecc71;
}

.feedback-negative {
  background: rgba(231, 76, 60, 0.1);
  border-left: 3px solid #e74c3c;
}

.feedback-positive ul,
.feedback-negative ul {
  margin-top: 10px;
  padding-left: 20px;
}

.feedback-positive li,
.feedback-negative li {
  margin-bottom: 5px;
  line-height: 1.6;
}

/* =====================
   ANSWER ANALYSIS
===================== */
.answer-analysis {
  background: rgba(0, 0, 0, 0.2);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.answer-analysis p {
  margin-bottom: 8px;
  line-height: 1.6;
}

/* =====================
   QUESTION ANALYSIS
===================== */
.question-analysis {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.qa-item {
  background: rgba(0, 0, 0, 0.2);
  padding: 20px;
  border-radius: 8px;
  border-left: 3px solid #3498db;
}

.qa-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.qa-category {
  background: rgba(52, 152, 219, 0.2);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #3498db;
  font-weight: bold;
}

.qa-score {
  font-weight: bold;
  padding: 5px 12px;
  border-radius: 20px;
}

.match-full { background: rgba(46, 204, 113, 0.2); color: #2ecc71; }
.match-partial { background: rgba(243, 156, 18, 0.2); color: #f39c12; }
.match-none { background: rgba(231, 76, 60, 0.2); color: #e74c3c; }

.qa-question,
.qa-user-answer,
.qa-model-answer,
.qa-feedback {
  margin-bottom: 12px;
  line-height: 1.6;
}

.qa-question strong,
.qa-user-answer strong,
.qa-model-answer strong {
  color: #f1c40f;
}

.qa-user-answer {
  background: rgba(52, 152, 219, 0.1);
  padding: 10px;
  border-radius: 6px;
}

.qa-model-answer {
  background: rgba(46, 204, 113, 0.1);
  padding: 10px;
  border-radius: 6px;
}

.qa-feedback {
  font-style: italic;
  padding: 10px;
  border-radius: 6px;
}

/* =====================
   SUGGESTIONS
===================== */
.suggestions {
  background: rgba(241, 196, 15, 0.1);
  padding: 25px;
  border-radius: 12px;
  border-left: 4px solid #f1c40f;
  margin-top: 30px;
}

.suggestions h3 {
  margin-bottom: 15px;
  color: #f1c40f;
}

.suggestions ul {
  padding-left: 20px;
}

.suggestions li {
  margin-bottom: 10px;
  line-height: 1.6;
}

/* =====================
   ACTION BUTTONS
===================== */
.action-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 40px;
}

.btn {
  padding: 15px 40px;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-retry {
  background: #3498db;
  color: white;
}

.btn-retry:hover {
  background: #2980b9;
  transform: translateY(-2px);
}

.btn-close {
  background: #7f8c8d;
  color: white;
}

.btn-close:hover {
  background: #6c7a7b;
  transform: translateY(-2px);
}
</style>
