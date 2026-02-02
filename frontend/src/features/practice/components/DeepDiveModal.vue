<template>
  <div class="modal-overlay" :class="{ active: isActive }">
    <div class="interrogation-frame">
      <!-- 헤더 -->
      <div class="frame-header">
        <div class="header-left">
          <div class="header-title">{{ headerTitle }}</div>
          <div class="header-meta">
            <span class="rec">REC</span>
            <span v-if="isExplanationPhase">Step 1: 설명 작성</span>
            <span v-else-if="totalQuestions > 0">질문 {{ currentQuestion }} / {{ totalQuestions }}</span>
          </div>
        </div>
        <div class="header-right">
          <div v-if="totalQuestions > 0" class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- 메인 -->
      <div class="frame-main">
        <div v-if="isGenerating" class="loading-section">
          <div class="loading-spinner"></div>
          <p>ANALYZING_ARCHITECTURE... 꽥!</p>
        </div>

        <template v-else>
          <!-- 좌측: 증거물 (다이어그램) -->
          <div class="evidence-section">
            <div class="section-title">[EVIDENCE] SYSTEM DIAGRAM</div>
            <div class="diagram-container" ref="mermaidPreview">
              <span v-if="!mermaidCode" class="diagram-placeholder">Mermaid Diagram Here</span>
            </div>
          </div>

          <!-- 우측: 형사 & 답변 -->
          <div class="detective-section">
            <!-- 오리 형사 -->
            <div class="det-card">
              <div class="det-avatar">
                <img src="/image/duck_det.png" alt="Detective Duck" />
              </div>
              <div class="det-text">
                <div class="det-name">CODUCK_AI</div>
                <!-- <div class="det-category" v-if="category">{{ categoryIcon }} {{ category }}</div> -->
                <p class="det-question">{{ question }}</p>
              </div>
            </div>

            <!-- 용의자 진술 -->
            <div class="testimony-section">
              <div class="testimony-label">{{ isExplanationPhase ? '[EXPLANATION]' : '[ANSWER]' }}</div>
              <textarea
                class="testimony-input"
                :class="{ 'explanation-mode': isExplanationPhase }"
                v-model="answer"
                :placeholder="placeholderText"
              ></textarea>
            </div>

            <!-- 스탬프 -->
            <!-- <div class="verdict-stamp">UNDER INVESTIGATION</div> -->
          </div>
        </template>
      </div>

      <!-- 푸터 -->
      <div class="frame-footer">
        <button class="btn btn-silent" @click="$emit('skip')">
          {{ skipButtonText }}
        </button>
        <button
          class="btn btn-submit"
          :class="{ 'btn-explanation': isExplanationPhase }"
          @click="submitAnswer"
          :disabled="isGenerating || (isExplanationPhase && answer.trim().length < 10)"
        >
          {{ submitButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import mermaid from 'mermaid';

export default {
  name: 'DeepDiveModal',
  props: {
    isActive: {
      type: Boolean,
      default: false
    },
    question: {
      type: String,
      default: ''
    },
    isGenerating: {
      type: Boolean,
      default: false
    },
    currentQuestion: {
      type: Number,
      default: 1
    },
    totalQuestions: {
      type: Number,
      default: 3
    },
    category: {
      type: String,
      default: ''
    },
    mermaidCode: {
      type: String,
      default: ''
    },
    // NEW: 현재 Phase (explanation | questioning)
    phase: {
      type: String,
      default: 'questioning'
    }
  },
  emits: ['skip', 'submit', 'submit-explanation'],
  data() {
    return {
      answer: ''
    };
  },
  computed: {
    progressPercent() {
      if (this.totalQuestions === 0) return 0;
      return (this.currentQuestion / this.totalQuestions) * 100;
    },
    isLastQuestion() {
      return this.currentQuestion >= this.totalQuestions;
    },
    // NEW: Phase에 따른 UI 텍스트
    isExplanationPhase() {
      return this.phase === 'explanation';
    },
    submitButtonText() {
      if (this.isExplanationPhase) {
        return 'SUBMIT_EXPLANATION';
      }
      return this.isLastQuestion ? 'FINAL_SUBMIT' : 'NEXT_PROTOCOL';
    },
    skipButtonText() {
      if (this.isExplanationPhase) {
        return 'SKIP';
      }
      return this.isLastQuestion ? 'SKIP_TO_EVALUATE' : 'SKIP';
    },
    placeholderText() {
      if (this.isExplanationPhase) {
        return '아키텍처에 대한 설명을 입력하세요... (최소 50자 권장)';
      }
      return '답변을 입력하세요... 꽥!';
    },
    headerTitle() {
      if (this.isExplanationPhase) {
        return 'ARCHITECTURE_ANALYSIS';
      }
      return 'SYSTEM_VERIFICATION';
    }
  },
  watch: {
    question(newVal) {
      if (newVal) {
        this.answer = '';
      }
    },
    isActive(newVal) {
      if (newVal) {
        this.answer = '';
        this.$nextTick(() => {
          this.renderMermaid();
        });
      }
    },
    isGenerating(newVal) {
      if (!newVal && this.mermaidCode) {
        this.$nextTick(() => {
          this.renderMermaid();
        });
      }
    }
  },
  methods: {
    submitAnswer() {
      const trimmedAnswer = this.answer.trim();
      if (this.isExplanationPhase) {
        // 설명 Phase: 설명 제출 이벤트
        this.$emit('submit-explanation', trimmedAnswer);
      } else {
        // 질문 Phase: 기존 답변 제출 이벤트
        this.$emit('submit', trimmedAnswer);
      }
      this.answer = '';
    },
    async renderMermaid() {
      const container = this.$refs.mermaidPreview;
      if (!container || !this.mermaidCode) return;

      try {
        const { svg } = await mermaid.render('deepdive-mermaid-' + Date.now(), this.mermaidCode);
        container.innerHTML = svg;
      } catch (error) {
        container.innerHTML = '<p class="mermaid-error">다이어그램 렌더링 오류</p>';
      }
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap');

/* =====================
   OVERLAY
===================== */
.modal-overlay {
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
  background: rgba(5, 7, 10, 0.95);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.modal-overlay::after {
  content: "";
  position: fixed;
  inset: 0;
  background-image: radial-gradient(rgba(163, 255, 71, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
}

.modal-overlay.active {
  opacity: 1;
  visibility: visible;
}

/* =====================
   FRAME
===================== */
.interrogation-frame {
  width: 1100px;
  max-width: 95%;
  max-height: 90vh;
  background: var(--bg-dark);
  border: 1px solid rgba(163, 255, 71, 0.3);
  box-shadow: 0 0 60px rgba(163, 255, 71, 0.15);
  position: relative;
  overflow-y: auto;
  transform: scale(0.95);
  transition: transform 0.3s ease;
}

/* 스크롤바 커스텀 */
.interrogation-frame::-webkit-scrollbar {
  width: 4px;
}

.interrogation-frame::-webkit-scrollbar-track {
  background: transparent;
}

.interrogation-frame::-webkit-scrollbar-thumb {
  background: rgba(163, 255, 71, 0.2);
  border-radius: 10px;
}

.modal-overlay.active .interrogation-frame {
  transform: scale(1);
}

/* =====================
   HEADER
===================== */
.frame-header {
  padding: 16px 24px;
  border-bottom: 1px solid rgba(163, 255, 71, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(163, 255, 71, 0.03);
}

.header-title {
  font-family: var(--terminal-font);
  font-size: 0.85rem;
  color: var(--accent-green);
  letter-spacing: 3px;
  font-weight: 700;
  margin-bottom: 6px;
  text-shadow: 0 0 10px rgba(163, 255, 71, 0.5);
}

.header-meta {
  font-family: var(--terminal-font);
  font-size: 0.75rem;
  color: rgba(163, 255, 71, 0.6);
  display: flex;
  align-items: center;
  gap: 12px;
}

.rec {
  color: var(--accent-green);
  font-weight: bold;
  animation: pulse-opacity 1.5s infinite;
}

.rec::before {
  content: "● ";
}

@keyframes pulse-opacity {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.header-right {
  min-width: 150px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(163, 255, 71, 0.1);
  border: 1px solid rgba(163, 255, 71, 0.2);
}

.progress-fill {
  height: 100%;
  background: var(--accent-green);
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(163, 255, 71, 0.5);
}

/* =====================
   MAIN
===================== */
.frame-main {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px;
  padding: 20px;
  min-height: 350px;
}

/* Loading */
.loading-section {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(163, 255, 71, 0.2);
  border-top-color: var(--accent-green);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-section p {
  color: var(--accent-green);
  font-family: var(--terminal-font);
  font-size: 0.9rem;
}

/* =====================
   EVIDENCE (Left)
===================== */
.evidence-section {
  background: rgba(163, 255, 71, 0.03);
  border: 1px solid rgba(163, 255, 71, 0.2);
  padding: 15px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-family: var(--terminal-font);
  font-size: 0.7rem;
  color: rgba(163, 255, 71, 0.6);
  margin-bottom: 12px;
  letter-spacing: 2px;
}

.diagram-container {
  flex: 1;
  min-height: 220px;
  border: 1px dashed rgba(163, 255, 71, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  padding: 10px;
}

.diagram-placeholder {
  color: rgba(163, 255, 71, 0.3);
  font-family: var(--terminal-font);
  font-size: 0.8rem;
}

.diagram-container :deep(svg) {
  width: 100%;
  height: auto;
  max-height: 240px;
}

.mermaid-error {
  color: var(--accent-pink);
  font-size: 0.8rem;
}

/* Stamp */
.stamp {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-12deg);
  border: 2px solid var(--accent-green);
  color: var(--accent-green);
  font-family: var(--terminal-font);
  font-size: 0.9rem;
  font-weight: 700;
  padding: 12px 20px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
  background: rgba(5, 7, 10, 0.9);
  letter-spacing: 2px;
}

.stamp.stamp-active {
  opacity: 0.85;
}

/* =====================
   DETECTIVE (Right)
===================== */
.detective-section {
  background: rgba(163, 255, 71, 0.03);
  border: 1px solid rgba(163, 255, 71, 0.2);
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.det-card {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.det-avatar {
  width: 70px;
  height: 70px;
  border: 2px solid var(--accent-green);
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  box-shadow: 0 0 15px rgba(163, 255, 71, 0.3);
}

.det-avatar img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.det-text {
  flex: 1;
}

.det-name {
  font-family: var(--terminal-font);
  font-size: 0.7rem;
  color: var(--accent-green);
  margin-bottom: 6px;
  letter-spacing: 2px;
  font-weight: 700;
  text-shadow: 0 0 8px rgba(163, 255, 71, 0.5);
}

.det-category {
  display: inline-block;
  padding: 3px 8px;
  background: rgba(163, 255, 71, 0.1);
  border: 1px solid rgba(163, 255, 71, 0.3);
  font-family: var(--terminal-font);
  font-size: 0.6rem;
  color: var(--accent-green);
  margin-bottom: 8px;
}

.det-question {
  font-family: var(--terminal-font);
  font-size: 0.85rem;
  line-height: 1.6;
  color: #ecf0f1;
  margin: 0;
}

/* Testimony */
.testimony-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.testimony-label {
  font-family: var(--terminal-font);
  font-size: 0.65rem;
  color: var(--accent-green);
  letter-spacing: 1px;
}

.testimony-input {
  flex: 1;
  min-height: 80px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid var(--accent-green);
  padding: 12px;
  color: #ecf0f1;
  font-family: var(--terminal-font);
  font-size: 0.85rem;
  resize: none;
  transition: all 0.3s ease;
}

.testimony-input:focus {
  outline: none;
  box-shadow: 0 0 15px rgba(163, 255, 71, 0.3);
}

.testimony-input::placeholder {
  color: rgba(163, 255, 71, 0.3);
}

/* 설명 모드 스타일 */
.testimony-input.explanation-mode {
  min-height: 150px;
  border-color: var(--accent-cyan);
}

.testimony-input.explanation-mode:focus {
  box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
}

.btn-explanation {
  background: var(--accent-cyan) !important;
  color: #000 !important;
}

.btn-explanation:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.5) !important;
}

/* =====================
   FOOTER
===================== */
.frame-footer {
  border-top: 1px solid rgba(163, 255, 71, 0.2);
  padding: 15px 24px;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  background: rgba(163, 255, 71, 0.03);
}

.btn {
  flex: 1;
  max-width: 250px;
  padding: 12px 20px;
  font-family: var(--terminal-font);
  font-size: 0.75rem;
  cursor: pointer;
  border: 1px solid rgba(163, 255, 71, 0.3);
  transition: all 0.2s ease;
  letter-spacing: 1px;
}

.btn-submit {
  background: var(--accent-green);
  color: #000;
  font-weight: 700;
}

.btn-submit:hover:not(:disabled) {
  box-shadow: 0 0 25px rgba(163, 255, 71, 0.5);
  transform: translateY(-2px);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-silent {
  background: rgba(163, 255, 71, 0.1);
  color: rgba(163, 255, 71, 0.7);
}

.btn-silent:hover {
  background: rgba(163, 255, 71, 0.2);
  color: var(--accent-green);
}

/* =====================
   RESPONSIVE
===================== */
@media (max-width: 900px) {
  .frame-main {
    grid-template-columns: 1fr;
  }

  .evidence-section {
    min-height: 200px;
  }
}
</style>
