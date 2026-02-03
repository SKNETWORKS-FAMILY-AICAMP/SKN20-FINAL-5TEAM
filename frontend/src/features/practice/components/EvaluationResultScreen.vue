<template>
  <div class="space-screen">
    <!-- 별 배경 -->
    <div class="stars-container">
      <div class="stars"></div>
      <div class="stars2"></div>
      <div class="stars3"></div>
    </div>

    <!-- 성운 오버레이 -->
    <div class="nebula-overlay"></div>

    <div class="result-container">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="orbit-loader">
          <div class="planet"></div>
          <div class="orbit"></div>
        </div>
        <p class="loading-text">ANALYZING SYSTEM...</p>
      </div>

      <!-- Result Content -->
      <div v-else-if="result" class="result-report">
        <!-- 스탬프 마크 -->
        <div class="stamp-mark" :class="[verdictClass, { stamped: showStamp }]">
          {{ verdictStamp }}
        </div>

        <!-- 헤더 -->
        <h1 class="report-title">SYSTEM REPORT</h1>
        <div class="report-meta">
          <p><span class="label">DATE</span> {{ currentDate }}</p>
          <p><span class="label">OPERATOR</span> CODUCK_AI</p>
          <p v-if="problem"><span class="label">MISSION</span> {{ problem.title }}</p>
        </div>

        <div class="divider"></div>

        <!-- 판결 결과 -->
        <div class="verdict-section">
          <h2 class="section-title">VERDICT</h2>
          <div class="verdict-box" :class="verdictClass">
            <div class="verdict-text">{{ verdictMessage }}</div>
          </div>
          <div class="score-display">
            <div class="score-ring" :class="verdictClass">
              <svg viewBox="0 0 100 100">
                <circle class="score-bg" cx="50" cy="50" r="45"/>
                <circle class="score-progress" cx="50" cy="50" r="45"
                  :style="{ strokeDashoffset: scoreOffset }"/>
              </svg>
              <span class="score-value">{{ result.score }}</span>
            </div>
          </div>
        </div>

        <div class="divider"></div>

        <!-- 평가된 기둥 점수 (아코디언) -->
        <div v-if="evaluatedPillars.length" class="eval-section">
          <h3 class="section-title">EVALUATION AREAS</h3>
          <p class="hint-text">각 영역을 클릭하면 상세 해설을 확인할 수 있습니다</p>
          <div class="accordion-list">
            <div
              v-for="(pillar, idx) in evaluatedPillars"
              :key="pillar.category"
              class="accordion-item"
              :class="[getScoreClass(pillar.score), { expanded: expandedIndex === idx }]"
            >
              <!-- 아코디언 헤더 -->
              <div class="accordion-header" @click="toggleAccordion(idx)">
                <div class="accordion-header-left">
                  <span class="accordion-category">{{ pillar.category }}</span>
                </div>
                <div class="accordion-header-right">
                  <span class="accordion-score">{{ pillar.score }}</span>
                  <span class="accordion-arrow" :class="{ rotated: expandedIndex === idx }">&#9662;</span>
                </div>
              </div>

              <!-- 아코디언 본문 -->
              <div class="accordion-body" v-if="expandedIndex === idx && result.questionEvaluations[idx]">
                <div class="accordion-question">
                  <p>{{ result.questionEvaluations[idx].question }}</p>
                </div>

                <div class="accordion-answers">
                  <div class="accordion-answer-box user-answer">
                    <div class="answer-label">MY ANSWER</div>
                    <p>{{ result.questionEvaluations[idx].userAnswer || '(답변 없음)' }}</p>
                  </div>
                  <div class="accordion-answer-box model-answer">
                    <div class="answer-label">MODEL ANSWER</div>
                    <p>{{ result.questionEvaluations[idx].modelAnswer || '(모범답안 없음)' }}</p>
                  </div>
                </div>

                <div class="accordion-feedback">
                  <div class="feedback-label">FEEDBACK</div>
                  <p>{{ result.questionEvaluations[idx].feedback }}</p>
                </div>

                <div v-if="result.questionEvaluations[idx].improvements && result.questionEvaluations[idx].improvements.length" class="accordion-improvements">
                  <div class="improvements-label">IMPROVEMENTS</div>
                  <ul>
                    <li v-for="(imp, i) in result.questionEvaluations[idx].improvements" :key="i">{{ imp }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="divider"></div>

        <!-- 종합 평가 -->
        <div class="summary-section">
          <h3 class="section-title">ANALYSIS</h3>
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
            <h4>STRENGTHS</h4>
            <ul>
              <li v-for="s in result.strengths" :key="s">{{ s }}</li>
            </ul>
          </div>
          <div v-if="result.weaknesses && result.weaknesses.length" class="feedback-card weaknesses">
            <h4>IMPROVEMENTS</h4>
            <ul>
              <li v-for="w in result.weaknesses" :key="w">{{ w }}</li>
            </ul>
          </div>
        </div>

        <!-- 제안 사항 -->
        <div v-if="result.suggestions && result.suggestions.length" class="suggestions-section">
          <h4>RECOMMENDATIONS</h4>
          <ul>
            <li v-for="s in result.suggestions" :key="s">{{ s }}</li>
          </ul>
        </div>

        <!-- 버튼 -->
        <div class="action-buttons">
          <button class="btn-retry" @click="$emit('retry')">
            <span class="btn-text">TRY AGAIN</span>
            <span class="btn-glow"></span>
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
      showStamp: false,
      expandedIndex: null
    };
  },
  computed: {
    currentDate() {
      return new Date().toISOString().split('T')[0];
    },
    verdictClass() {
      const score = this.result?.score || 0;
      if (score >= 80) return 'excellent';
      if (score >= 50) return 'good';
      return 'poor';
    },
    verdictStamp() {
      const score = this.result?.score || 0;
      if (score >= 80) return 'APPROVED';
      if (score >= 50) return 'REVIEW';
      return 'REJECTED';
    },
    verdictMessage() {
      const score = this.result?.score || 0;
      if (score >= 80) return '시스템 복구 성공. 아키텍처가 승인되었습니다.';
      if (score >= 50) return '부분적 복구 완료. 추가 검토가 필요합니다.';
      return '시스템 복구 실패. 아키텍처 재설계가 필요합니다.';
    },
    detectiveComment() {
      return this.result?.summary || '시스템 분석 결과입니다.';
    },
    scoreOffset() {
      const score = this.result?.score || 0;
      const circumference = 2 * Math.PI * 45;
      return circumference - (score / 100) * circumference;
    },
    evaluatedPillars() {
      if (!this.result?.questionEvaluations?.length) return [];
      return this.result.questionEvaluations.map(qEval => ({
        category: qEval.category,
        score: qEval.score
      }));
    },
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
      if (score >= 40) return 'moderate';
      return 'poor';
    },
    toggleAccordion(index) {
      this.expandedIndex = this.expandedIndex === index ? null : index;
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

.space-screen {
  --space-deep: #0a0a1a;
  --space-dark: #12122a;
  --nebula-purple: #6b5ce7;
  --nebula-blue: #4fc3f7;
  --nebula-pink: #f06292;
  --star-white: #ffffff;
  --text-primary: #e8eaed;
  --text-secondary: rgba(232, 234, 237, 0.7);
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);

  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--space-deep) 0%, var(--space-dark) 50%, #1a1a3a 100%);
  z-index: 2000;
  overflow-y: auto;
  font-family: 'Rajdhani', sans-serif;
}

/* 별 배경 애니메이션 */
.stars-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
}

.stars, .stars2, .stars3 {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: transparent;
}

.stars {
  background-image:
    radial-gradient(2px 2px at 20px 30px, var(--star-white), transparent),
    radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.8), transparent),
    radial-gradient(1px 1px at 90px 40px, var(--star-white), transparent),
    radial-gradient(2px 2px at 160px 120px, rgba(255,255,255,0.9), transparent),
    radial-gradient(1px 1px at 230px 80px, var(--star-white), transparent),
    radial-gradient(2px 2px at 300px 150px, rgba(255,255,255,0.7), transparent),
    radial-gradient(1px 1px at 350px 200px, var(--star-white), transparent),
    radial-gradient(2px 2px at 420px 50px, rgba(255,255,255,0.8), transparent),
    radial-gradient(1px 1px at 500px 180px, var(--star-white), transparent),
    radial-gradient(2px 2px at 580px 100px, rgba(255,255,255,0.9), transparent);
  background-size: 600px 300px;
  animation: twinkle 4s ease-in-out infinite;
}

.stars2 {
  background-image:
    radial-gradient(1px 1px at 100px 150px, var(--nebula-blue), transparent),
    radial-gradient(2px 2px at 200px 250px, rgba(79, 195, 247, 0.6), transparent),
    radial-gradient(1px 1px at 350px 100px, var(--nebula-blue), transparent),
    radial-gradient(2px 2px at 450px 300px, rgba(79, 195, 247, 0.7), transparent),
    radial-gradient(1px 1px at 550px 200px, var(--nebula-blue), transparent);
  background-size: 600px 400px;
  animation: twinkle 6s ease-in-out infinite 1s;
}

.stars3 {
  background-image:
    radial-gradient(1px 1px at 50px 200px, var(--nebula-purple), transparent),
    radial-gradient(2px 2px at 150px 50px, rgba(107, 92, 231, 0.6), transparent),
    radial-gradient(1px 1px at 280px 180px, var(--nebula-purple), transparent),
    radial-gradient(2px 2px at 400px 120px, rgba(107, 92, 231, 0.7), transparent),
    radial-gradient(1px 1px at 520px 280px, var(--nebula-purple), transparent);
  background-size: 600px 400px;
  animation: twinkle 5s ease-in-out infinite 2s;
}

@keyframes twinkle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 성운 오버레이 */
.nebula-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(ellipse at 20% 20%, rgba(107, 92, 231, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(240, 98, 146, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(79, 195, 247, 0.08) 0%, transparent 60%);
  pointer-events: none;
  animation: nebulaPulse 10s ease-in-out infinite;
}

@keyframes nebulaPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* 스크롤바 */
.space-screen::-webkit-scrollbar { width: 6px; }
.space-screen::-webkit-scrollbar-track { background: transparent; }
.space-screen::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--nebula-purple), var(--nebula-blue));
  border-radius: 10px;
}

.result-container {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 150px 0;
}

.orbit-loader {
  position: relative;
  width: 100px;
  height: 100px;
  margin-bottom: 30px;
}

.planet {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 30px;
  height: 30px;
  margin: -15px 0 0 -15px;
  background: linear-gradient(135deg, var(--nebula-purple), var(--nebula-blue));
  border-radius: 50%;
  box-shadow: 0 0 30px rgba(107, 92, 231, 0.5);
}

.orbit {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 2px solid transparent;
  border-top-color: var(--nebula-blue);
  border-radius: 50%;
  animation: orbit 1.5s linear infinite;
}

.orbit::before {
  content: '';
  position: absolute;
  top: -4px;
  left: 50%;
  width: 8px;
  height: 8px;
  margin-left: -4px;
  background: var(--nebula-blue);
  border-radius: 50%;
  box-shadow: 0 0 15px var(--nebula-blue);
}

@keyframes orbit {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.9rem;
  color: var(--nebula-blue);
  letter-spacing: 3px;
  text-shadow: 0 0 20px rgba(79, 195, 247, 0.5);
}

/* Result Report */
.result-report {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 40px;
  position: relative;
  box-shadow:
    0 0 40px rgba(107, 92, 231, 0.1),
    inset 0 0 60px rgba(255, 255, 255, 0.02);
}

/* Stamp */
.stamp-mark {
  position: absolute;
  top: 30px;
  right: 30px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 8px 16px;
  border: 2px solid;
  border-radius: 4px;
  transform: rotate(12deg);
  opacity: 0;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  letter-spacing: 2px;
}

.stamp-mark.stamped {
  opacity: 1;
  transform: rotate(12deg) scale(1);
}

.stamp-mark.excellent {
  border-color: var(--nebula-blue);
  color: var(--nebula-blue);
  box-shadow: 0 0 20px rgba(79, 195, 247, 0.4);
}
.stamp-mark.good {
  border-color: var(--nebula-purple);
  color: var(--nebula-purple);
  box-shadow: 0 0 20px rgba(107, 92, 231, 0.4);
}
.stamp-mark.poor {
  border-color: var(--nebula-pink);
  color: var(--nebula-pink);
  box-shadow: 0 0 20px rgba(240, 98, 146, 0.4);
}

/* Header */
.report-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.8rem;
  font-weight: 900;
  text-align: center;
  margin-bottom: 20px;
  background: linear-gradient(135deg, var(--nebula-blue), var(--nebula-purple), var(--nebula-pink));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 4px;
}

.report-meta {
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.report-meta p { margin: 6px 0; }
.report-meta .label {
  color: var(--nebula-blue);
  font-weight: 600;
  margin-right: 8px;
}

.divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
  margin: 30px 0;
}

/* Section Title */
.section-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--nebula-purple);
  letter-spacing: 3px;
  text-align: center;
}

/* Verdict */
.verdict-box {
  padding: 20px;
  border-radius: 12px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  margin-bottom: 25px;
  text-align: center;
}

.verdict-box.excellent {
  border-color: rgba(79, 195, 247, 0.3);
  box-shadow: 0 0 30px rgba(79, 195, 247, 0.1);
}
.verdict-box.good {
  border-color: rgba(107, 92, 231, 0.3);
  box-shadow: 0 0 30px rgba(107, 92, 231, 0.1);
}
.verdict-box.poor {
  border-color: rgba(240, 98, 146, 0.3);
  box-shadow: 0 0 30px rgba(240, 98, 146, 0.1);
}

.verdict-text {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
}

/* Score Ring */
.score-display {
  display: flex;
  justify-content: center;
}

.score-ring {
  position: relative;
  width: 120px;
  height: 120px;
}

.score-ring svg {
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
}

.score-bg {
  fill: none;
  stroke: var(--glass-border);
  stroke-width: 6;
}

.score-progress {
  fill: none;
  stroke-width: 6;
  stroke-linecap: round;
  stroke-dasharray: 283;
  transition: stroke-dashoffset 1s ease;
}

.score-ring.excellent .score-progress { stroke: var(--nebula-blue); filter: drop-shadow(0 0 10px var(--nebula-blue)); }
.score-ring.good .score-progress { stroke: var(--nebula-purple); filter: drop-shadow(0 0 10px var(--nebula-purple)); }
.score-ring.moderate .score-progress { stroke: #ffc107; filter: drop-shadow(0 0 10px #ffc107); }
.score-ring.poor .score-progress { stroke: var(--nebula-pink); filter: drop-shadow(0 0 10px var(--nebula-pink)); }

.score-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: 'Orbitron', sans-serif;
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--text-primary);
}

/* Accordion */
.hint-text {
  text-align: center;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.accordion-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.accordion-item {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.accordion-item.expanded {
  border-color: rgba(255, 255, 255, 0.2);
}

.accordion-item.excellent.expanded { box-shadow: 0 0 25px rgba(79, 195, 247, 0.15); border-color: rgba(79, 195, 247, 0.3); }
.accordion-item.good.expanded { box-shadow: 0 0 25px rgba(107, 92, 231, 0.15); border-color: rgba(107, 92, 231, 0.3); }
.accordion-item.moderate.expanded { box-shadow: 0 0 25px rgba(255, 193, 7, 0.15); border-color: rgba(255, 193, 7, 0.3); }
.accordion-item.poor.expanded { box-shadow: 0 0 25px rgba(240, 98, 146, 0.15); border-color: rgba(240, 98, 146, 0.3); }

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.accordion-header:hover {
  background: rgba(255, 255, 255, 0.03);
}

.accordion-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.accordion-category {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.accordion-header-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.accordion-score {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.3rem;
  font-weight: 700;
}

.accordion-item.excellent .accordion-score { color: var(--nebula-blue); }
.accordion-item.good .accordion-score { color: var(--nebula-purple); }
.accordion-item.moderate .accordion-score { color: #ffc107; }
.accordion-item.poor .accordion-score { color: var(--nebula-pink); }

.accordion-arrow {
  font-size: 0.9rem;
  color: var(--text-secondary);
  transition: transform 0.3s ease;
  display: inline-block;
}

.accordion-arrow.rotated {
  transform: rotate(180deg);
}

/* Accordion Body */
.accordion-body {
  padding: 0 20px 20px;
  border-top: 1px solid var(--glass-border);
  animation: accordionOpen 0.3s ease;
}

@keyframes accordionOpen {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.accordion-question {
  padding: 15px 0;
}

.accordion-question p {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.6;
}

.accordion-answers {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 15px;
}

.accordion-answer-box {
  background: rgba(0, 0, 0, 0.2);
  padding: 14px;
  border-radius: 10px;
  border: 1px solid var(--glass-border);
}

.accordion-answer-box.user-answer { border-left: 3px solid var(--nebula-purple); }
.accordion-answer-box.model-answer { border-left: 3px solid var(--nebula-blue); }

.answer-label {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.accordion-answer-box p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-primary);
  line-height: 1.6;
  white-space: pre-wrap;
}

.accordion-feedback {
  background: rgba(107, 92, 231, 0.1);
  padding: 14px;
  border-radius: 10px;
  border: 1px solid rgba(107, 92, 231, 0.2);
  margin-bottom: 12px;
}

.feedback-label, .improvements-label {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--nebula-purple);
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.accordion-feedback p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-primary);
  line-height: 1.6;
}

.accordion-improvements {
  background: rgba(79, 195, 247, 0.1);
  padding: 14px;
  border-radius: 10px;
  border: 1px solid rgba(79, 195, 247, 0.2);
}

.improvements-label { color: var(--nebula-blue); }

.accordion-improvements ul { margin: 0; padding-left: 20px; }
.accordion-improvements li {
  font-size: 0.85rem;
  color: var(--text-primary);
  margin-bottom: 6px;
  line-height: 1.5;
}

@media (max-width: 600px) {
  .accordion-answers { grid-template-columns: 1fr; }
}

/* Summary */
.summary-box {
  background: var(--glass-bg);
  padding: 25px;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
}

.detective-comment {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.comment-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 2px solid var(--nebula-purple);
  box-shadow: 0 0 20px rgba(107, 92, 231, 0.3);
}

.detective-comment p {
  flex: 1;
  font-size: 0.95rem;
  font-style: italic;
  margin: 0;
  line-height: 1.7;
  color: var(--text-primary);
}

.feedback-card {
  padding: 20px;
  border-radius: 12px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
}

.feedback-card.strengths { border-color: rgba(79, 195, 247, 0.3); }
.feedback-card.weaknesses { border-color: rgba(240, 98, 146, 0.3); }

.feedback-card h4 {
  font-family: 'Orbitron', sans-serif;
  margin: 0 0 15px 0;
  font-size: 0.75rem;
  letter-spacing: 2px;
}

.feedback-card.strengths h4 { color: var(--nebula-blue); }
.feedback-card.weaknesses h4 { color: var(--nebula-pink); }

.feedback-card ul { margin: 0; padding-left: 18px; }
.feedback-card li {
  font-size: 0.85rem;
  margin-bottom: 8px;
  line-height: 1.5;
  color: var(--text-primary);
}

/* Suggestions */
.suggestions-section {
  background: var(--glass-bg);
  border: 1px solid rgba(107, 92, 231, 0.3);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
}

.suggestions-section h4 {
  font-family: 'Orbitron', sans-serif;
  margin: 0 0 15px 0;
  font-size: 0.75rem;
  color: var(--nebula-purple);
  letter-spacing: 2px;
}

.suggestions-section ul { margin: 0; padding-left: 18px; }
.suggestions-section li {
  font-size: 0.85rem;
  color: var(--text-primary);
  margin-bottom: 8px;
  line-height: 1.5;
}

/* Button */
.action-buttons {
  text-align: center;
  margin-top: 30px;
}

.btn-retry {
  position: relative;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 16px 40px;
  background: linear-gradient(135deg, var(--nebula-purple), var(--nebula-blue));
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 2px;
  overflow: hidden;
}

.btn-text {
  position: relative;
  z-index: 1;
}

.btn-glow {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s ease;
}

.btn-retry:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(107, 92, 231, 0.4);
}

.btn-retry:hover .btn-glow {
  left: 100%;
}

/* Responsive */
@media (max-width: 600px) {
  .feedback-grid { grid-template-columns: 1fr; }
  .stamp-mark { font-size: 0.7rem; top: 20px; right: 20px; padding: 6px 12px; }
  .report-title { font-size: 1.4rem; }
  .result-report { padding: 25px; }
}
</style>
