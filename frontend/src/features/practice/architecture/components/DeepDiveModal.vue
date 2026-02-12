<template>
  <div class="modal-overlay" :class="{ active: isActive }">
    <!-- Star layers -->
    <div class="stars"></div>
    <div class="stars2"></div>
    <div class="stars3"></div>
    <div class="nebula-overlay"></div>

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
          <div class="loading-orbit">
            <div class="orbit-ring"></div>
            <div class="orbit-core"></div>
          </div>
          <p>ANALYZING_ARCHITECTURE...</p>
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
                <p class="det-question">{{ question }}</p>
              </div>
            </div>

            <!-- 용의자 진술 -->
            <div class="testimony-section">
              <div class="testimony-label">{{ isExplanationPhase ? '[EXPLANATION]' : '[ANSWER]' }}</div>
              <textarea
                class="testimony-input"
                :class="{ 'explanation-mode': isExplanationPhase, 'error': validationError }"
                v-model="answer"
                :placeholder="placeholderText"
              ></textarea>
              <!-- 🔥 NEW: 검증 실패 메시지 표시 -->
              <div v-if="validationError" class="validation-error-message">
                <span class="error-icon">⚠️</span>
                {{ validationError }}
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 푸터 -->
      <div class="frame-footer">
        <button
          class="btn btn-submit"
          :class="{ 'btn-explanation': isExplanationPhase }"
          @click="submitAnswer"
          :disabled="isGenerating || !answer.trim()"
        >
          {{ submitButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#6b5ce7',
    primaryTextColor: '#e8eaed',
    primaryBorderColor: '#6b5ce7',
    lineColor: '#4fc3f7',
    secondaryColor: '#f06292',
    tertiaryColor: '#4fc3f7',
    background: '#12122a',
    mainBkg: 'rgba(255, 255, 255, 0.05)',
    textColor: '#e8eaed'
  },
  securityLevel: 'loose'
});

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
    },
    // 🔥 NEW: 검증 에러 메시지
    validationError: {
      type: String,
      default: ''
    }
  },
  emits: ['submit', 'submit-explanation'],
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
    placeholderText() {
      if (this.isExplanationPhase) {
        return '아키텍처에 대한 설명을 입력하세요... (최소 50자 권장)';
      }
      return '답변을 입력하세요...';
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
    },
    mermaidCode(newVal) {
      if (newVal && this.isActive && !this.isGenerating) {
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
        // 🔥 검증 통과 시에만 답변 초기화 (부모에서 성공 확인 후)
      } else {
        // 질문 Phase: 기존 답변 제출 이벤트
        this.$emit('submit', trimmedAnswer);
      }
    },
    async renderMermaid() {
      const container = this.$refs.mermaidPreview;
      if (!container || !this.mermaidCode) return;

      try {
        const { svg } = await mermaid.render('deepdive-mermaid-' + Date.now(), this.mermaidCode);
        container.innerHTML = svg;
      } catch (error) {
        console.error('Mermaid rendering error:', error);
        container.innerHTML = '<p class="mermaid-error">다이어그램 렌더링 오류</p>';
      }
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;700&display=swap');

/* =====================
   CSS VARIABLES
===================== */
.modal-overlay {
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
}

/* =====================
   OVERLAY
===================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--space-deep) 0%, var(--space-dark) 50%, #1a1a3a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.4s ease;
  overflow: hidden;
}

.modal-overlay.active {
  opacity: 1;
  visibility: visible;
}

/* =====================
   STAR LAYERS
===================== */
.stars, .stars2, .stars3 {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.stars {
  background-image: radial-gradient(1px 1px at 20px 30px, rgba(255,255,255,0.5) 50%, transparent 50%),
    radial-gradient(1px 1px at 40px 70px, rgba(255,255,255,0.4) 50%, transparent 50%),
    radial-gradient(1px 1px at 50px 160px, rgba(255,255,255,0.5) 50%, transparent 50%),
    radial-gradient(1px 1px at 90px 40px, rgba(255,255,255,0.4) 50%, transparent 50%),
    radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.5) 50%, transparent 50%),
    radial-gradient(1px 1px at 160px 120px, rgba(255,255,255,0.3) 50%, transparent 50%);
  background-size: 200px 200px;
  animation: twinkle 50s linear infinite;
  opacity: 0.5;
}

.stars2 {
  background-image: radial-gradient(2px 2px at 100px 50px, rgba(255,255,255,0.3) 50%, transparent 50%),
    radial-gradient(2px 2px at 200px 150px, rgba(255,255,255,0.2) 50%, transparent 50%),
    radial-gradient(2px 2px at 300px 250px, rgba(255,255,255,0.3) 50%, transparent 50%);
  background-size: 400px 400px;
  animation: twinkle 100s linear infinite;
  opacity: 0.3;
}

.stars3 {
  background-image: radial-gradient(3px 3px at 150px 100px, rgba(255,255,255,0.2) 50%, transparent 50%),
    radial-gradient(3px 3px at 350px 300px, rgba(255,255,255,0.15) 50%, transparent 50%);
  background-size: 600px 600px;
  animation: twinkle 150s linear infinite;
  opacity: 0.2;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; transform: translateY(0); }
  50% { opacity: 0.8; transform: translateY(-5px); }
}

/* =====================
   NEBULA OVERLAY
===================== */
.nebula-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(ellipse at 20% 80%, rgba(107, 92, 231, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(79, 195, 247, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(240, 98, 146, 0.05) 0%, transparent 70%);
  pointer-events: none;
}

/* =====================
   FRAME
===================== */
.interrogation-frame {
  width: 1100px;
  max-width: 95%;
  max-height: 90vh;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  backdrop-filter: blur(20px);
  box-shadow:
    0 0 40px rgba(107, 92, 231, 0.2),
    0 0 80px rgba(107, 92, 231, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  position: relative;
  overflow-y: auto;
  transform: scale(0.95);
  transition: transform 0.4s ease;
  z-index: 1;
}

/* 스크롤바 커스텀 */
.interrogation-frame::-webkit-scrollbar {
  width: 4px;
}

.interrogation-frame::-webkit-scrollbar-track {
  background: transparent;
}

.interrogation-frame::-webkit-scrollbar-thumb {
  background: rgba(107, 92, 231, 0.3);
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
  border-bottom: 1px solid var(--glass-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(107, 92, 231, 0.08);
}

.header-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.85rem;
  color: var(--nebula-blue);
  letter-spacing: 3px;
  font-weight: 700;
  margin-bottom: 6px;
  text-shadow: 0 0 15px rgba(79, 195, 247, 0.5);
}

.header-meta {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 12px;
}

.rec {
  color: var(--nebula-pink);
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
  background: rgba(107, 92, 231, 0.15);
  border: 1px solid rgba(107, 92, 231, 0.3);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--nebula-purple), var(--nebula-blue));
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(79, 195, 247, 0.5);
  border-radius: 3px;
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

.loading-orbit {
  position: relative;
  width: 60px;
  height: 60px;
  margin-bottom: 24px;
}

.orbit-ring {
  position: absolute;
  inset: 0;
  border: 3px solid rgba(107, 92, 231, 0.2);
  border-top-color: var(--nebula-blue);
  border-right-color: var(--nebula-purple);
  border-radius: 50%;
  animation: orbit 1.2s linear infinite;
}

.orbit-core {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 12px;
  height: 12px;
  background: linear-gradient(135deg, var(--nebula-purple), var(--nebula-blue));
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 20px rgba(107, 92, 231, 0.6);
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes orbit {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 15px rgba(107, 92, 231, 0.4); }
  50% { box-shadow: 0 0 30px rgba(79, 195, 247, 0.7); }
}

.loading-section p {
  color: var(--nebula-blue);
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(79, 195, 247, 0.4);
}

/* =====================
   EVIDENCE (Left)
===================== */
.evidence-section {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 15px;
  position: relative;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
}

.section-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  color: var(--text-secondary);
  margin-bottom: 12px;
  letter-spacing: 2px;
}

.diagram-container {
  flex: 1;
  min-height: 220px;
  border: 1px dashed rgba(107, 92, 231, 0.25);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.2);
  padding: 10px;
}

.diagram-placeholder {
  color: var(--text-secondary);
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.9rem;
}

.diagram-container :deep(svg) {
  width: 100%;
  height: auto;
  max-height: 240px;
}

.mermaid-error {
  color: var(--nebula-pink);
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.85rem;
}

/* =====================
   DETECTIVE (Right)
===================== */
.detective-section {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  backdrop-filter: blur(10px);
}

.det-card {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.det-avatar {
  width: 70px;
  height: 70px;
  border: 2px solid var(--nebula-purple);
  border-radius: 50%;
  background: rgba(107, 92, 231, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(107, 92, 231, 0.3);
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
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  color: var(--nebula-blue);
  margin-bottom: 6px;
  letter-spacing: 2px;
  font-weight: 700;
  text-shadow: 0 0 8px rgba(79, 195, 247, 0.5);
}

.det-question {
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text-primary);
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
  font-family: 'Orbitron', sans-serif;
  font-size: 0.65rem;
  color: var(--nebula-purple);
  letter-spacing: 2px;
}

.testimony-input {
  flex: 1;
  min-height: 80px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(107, 92, 231, 0.3);
  border-radius: 12px;
  padding: 12px;
  color: var(--text-primary);
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.95rem;
  resize: none;
  transition: all 0.3s ease;
}

.testimony-input:focus {
  outline: none;
  border-color: var(--nebula-purple);
  box-shadow: 0 0 20px rgba(107, 92, 231, 0.3);
}

.testimony-input::placeholder {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

/* 설명 모드 스타일 */
.testimony-input.explanation-mode {
  min-height: 150px;
  border-color: rgba(79, 195, 247, 0.4);
}

.testimony-input.explanation-mode:focus {
  border-color: var(--nebula-blue);
  box-shadow: 0 0 20px rgba(79, 195, 247, 0.3);
}

/* 🔥 NEW: 검증 에러 상태 */
.testimony-input.error {
  border-color: #ff6b6b !important;
  background: rgba(255, 107, 107, 0.08);
}

.testimony-input.error:focus {
  box-shadow: 0 0 20px rgba(255, 107, 107, 0.4);
}

.validation-error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(255, 107, 107, 0.12);
  border: 1px solid #ff6b6b;
  border-radius: 8px;
  color: #ff6b6b;
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.85rem;
  line-height: 1.4;
  animation: shake 0.4s ease;
}

.error-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-8px); }
  75% { transform: translateX(8px); }
}

.btn-explanation {
  background: linear-gradient(135deg, var(--nebula-blue), #81d4fa) !important;
  color: var(--space-deep) !important;
}

.btn-explanation:hover:not(:disabled) {
  box-shadow: 0 10px 30px rgba(79, 195, 247, 0.4) !important;
}

/* =====================
   FOOTER
===================== */
.frame-footer {
  border-top: 1px solid var(--glass-border);
  padding: 15px 24px;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  background: rgba(107, 92, 231, 0.05);
}

.btn {
  flex: 1;
  max-width: 250px;
  padding: 14px 28px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.75rem;
  cursor: pointer;
  border: 1px solid rgba(107, 92, 231, 0.3);
  border-radius: 30px;
  transition: all 0.3s ease;
  letter-spacing: 2px;
}

.btn-submit {
  background: linear-gradient(135deg, var(--nebula-purple), var(--nebula-blue));
  color: #fff;
  font-weight: 700;
  border: none;
}

.btn-submit:hover:not(:disabled) {
  box-shadow: 0 10px 30px rgba(107, 92, 231, 0.4);
  transform: translateY(-3px);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

  .header-title {
    font-size: 0.7rem;
    letter-spacing: 2px;
  }
}

@media (max-width: 600px) {
  .interrogation-frame {
    max-width: 98%;
  }

  .frame-header {
    padding: 12px 16px;
  }

  .frame-main {
    padding: 12px;
    gap: 12px;
  }

  .frame-footer {
    padding: 12px 16px;
  }

  .btn {
    padding: 10px 16px;
    font-size: 0.65rem;
  }
}
</style>
