<template>
  <div class="modal-overlay" :class="{ active: isActive }">
    <!-- Star layers -->
    <div class="stars"></div>
    <div class="stars2"></div>
    <div class="stars3"></div>
    <div class="nebula-overlay"></div>

    <div class="modal-window">
      <div class="modal-header">
        <div class="header-icon">
          <div class="orbit-decoration"></div>
        </div>
        <h3>FINAL_QUESTION</h3>
        <div class="modal-subtitle">AI ARCHITECT BOT</div>
      </div>
      <div class="modal-body">
        <div v-if="isGenerating" class="loading-question">
          <div class="loading-orbit">
            <div class="orbit-ring"></div>
            <div class="orbit-core"></div>
          </div>
          <p>ANALYZING ARCHITECTURE...</p>
          <span class="loading-hint">질문을 생성하는 중입니다</span>
        </div>
        <template v-else>
          <div class="content-layout">
            <!-- 왼쪽: Mermaid Preview -->
            <div class="mermaid-preview-section" v-if="mermaidCode">
              <span class="preview-title">SYSTEM DIAGRAM</span>
              <div class="mermaid-preview" ref="mermaidPreview"></div>
            </div>

            <!-- 오른쪽: 질문 및 답변 -->
            <div class="question-section">
              <div class="ai-question">
                <span class="ai-question-title">QUESTION</span>
                <span class="ai-question-text">{{ question }}</span>
              </div>

              <textarea
                class="user-answer"
                v-model="answer"
                placeholder="여기에 답변을 작성해주세요... (예: CDN을 사용하여 정적 리소스를 캐싱하여 부하를 줄입니다.)"
              ></textarea>
            </div>
          </div>
        </template>
      </div>
      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">CANCEL</button>
        <button
          class="btn-submit"
          @click="submitAnswer"
          :disabled="isGenerating"
        >
          SUBMIT
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import mermaid from 'mermaid';

export default {
  name: 'EvaluationModal',
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
    components: {
      type: Array,
      default: () => []
    },
    connections: {
      type: Array,
      default: () => []
    },
    mermaidCode: {
      type: String,
      default: ''
    }
  },
  emits: ['close', 'submit'],
  data() {
    return {
      answer: ''
    };
  },
  watch: {
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
      if (!this.answer.trim()) {
        alert('답변을 입력해주세요!');
        return;
      }
      this.$emit('submit', this.answer.trim());
      this.answer = '';
    },
    async renderMermaid() {
      const container = this.$refs.mermaidPreview;
      if (!container || !this.mermaidCode) return;

      try {
        const { svg } = await mermaid.render('eval-mermaid-' + Date.now(), this.mermaidCode);
        container.innerHTML = svg;
      } catch (error) {
        container.innerHTML = '<p class="mermaid-error">다이어그램 렌더링 중 오류가 발생했습니다.</p>';
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
  z-index: 1000;
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
   MODAL WINDOW
===================== */
.modal-window {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  width: 95%;
  max-width: 1100px;
  max-height: 90vh;
  overflow-y: auto;
  backdrop-filter: blur(20px);
  box-shadow:
    0 0 40px rgba(107, 92, 231, 0.2),
    0 0 80px rgba(107, 92, 231, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transform: scale(0.9);
  transition: transform 0.4s ease;
  position: relative;
  z-index: 1;
}

.modal-window::-webkit-scrollbar {
  width: 4px;
}

.modal-window::-webkit-scrollbar-track {
  background: transparent;
}

.modal-window::-webkit-scrollbar-thumb {
  background: rgba(107, 92, 231, 0.3);
  border-radius: 10px;
}

.modal-overlay.active .modal-window {
  transform: scale(1);
}

/* =====================
   HEADER
===================== */
.modal-header {
  padding: 25px;
  border-bottom: 1px solid var(--glass-border);
  text-align: center;
  background: rgba(107, 92, 231, 0.08);
  position: relative;
}

.header-icon {
  position: relative;
  width: 30px;
  height: 30px;
  margin: 0 auto 12px;
}

.orbit-decoration {
  width: 100%;
  height: 100%;
  border: 2px solid rgba(79, 195, 247, 0.4);
  border-radius: 50%;
  animation: orbit 4s linear infinite;
  position: relative;
}

.orbit-decoration::after {
  content: '';
  position: absolute;
  top: -3px;
  left: 50%;
  width: 6px;
  height: 6px;
  background: var(--nebula-blue);
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(79, 195, 247, 0.6);
}

@keyframes orbit {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.modal-header h3 {
  margin: 0 0 8px 0;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.4rem;
  font-weight: 900;
  color: var(--nebula-blue);
  letter-spacing: 3px;
  text-shadow: 0 0 20px rgba(79, 195, 247, 0.5);
}

.modal-subtitle {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  color: var(--text-secondary);
  letter-spacing: 2px;
}

/* =====================
   BODY
===================== */
.modal-body {
  padding: 20px;
}

.content-layout {
  display: flex;
  gap: 20px;
  align-items: stretch;
}

.question-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

/* Loading */
.loading-question {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px;
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
  animation: spin 1.2s linear infinite;
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 15px rgba(107, 92, 231, 0.4); }
  50% { box-shadow: 0 0 30px rgba(79, 195, 247, 0.7); }
}

.loading-question p {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem;
  color: var(--nebula-blue);
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(79, 195, 247, 0.4);
  margin: 0 0 8px 0;
}

.loading-hint {
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

/* Question */
.ai-question {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  backdrop-filter: blur(10px);
}

.ai-question-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  color: var(--nebula-purple);
  letter-spacing: 2px;
  font-weight: 700;
}

.ai-question-text {
  font-family: 'Rajdhani', sans-serif;
  font-size: 1.05rem;
  color: var(--text-primary);
  line-height: 1.6;
}

.user-answer {
  width: 100%;
  min-height: 120px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(107, 92, 231, 0.3);
  border-radius: 12px;
  padding: 15px;
  color: var(--text-primary);
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.95rem;
  resize: vertical;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.user-answer:focus {
  outline: none;
  border-color: var(--nebula-purple);
  box-shadow: 0 0 20px rgba(107, 92, 231, 0.3);
}

.user-answer::placeholder {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

/* =====================
   MERMAID PREVIEW
===================== */
.mermaid-preview-section {
  flex: 1;
  min-width: 0;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
}

.preview-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  color: var(--text-secondary);
  letter-spacing: 2px;
  margin-bottom: 12px;
}

.mermaid-preview {
  flex: 1;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}

.mermaid-preview :deep(svg) {
  width: 100%;
  height: auto;
  max-height: 280px;
}

.mermaid-error {
  color: var(--nebula-pink);
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.85rem;
}

/* =====================
   FOOTER
===================== */
.modal-footer {
  padding: 20px 25px;
  border-top: 1px solid var(--glass-border);
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  background: rgba(107, 92, 231, 0.05);
}

.btn-cancel {
  padding: 14px 28px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 30px;
  color: var(--text-secondary);
  font-family: 'Orbitron', sans-serif;
  font-size: 0.75rem;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  border-color: rgba(107, 92, 231, 0.4);
}

.btn-submit {
  padding: 14px 28px;
  background: linear-gradient(135deg, var(--nebula-purple), var(--nebula-blue));
  border: none;
  border-radius: 30px;
  color: #fff;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(107, 92, 231, 0.4);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* =====================
   RESPONSIVE
===================== */
@media (max-width: 768px) {
  .content-layout {
    flex-direction: column;
  }

  .modal-header h3 {
    font-size: 1.1rem;
  }

  .modal-window {
    max-width: 98%;
  }
}

@media (max-width: 600px) {
  .modal-header {
    padding: 16px;
  }

  .modal-body {
    padding: 12px;
  }

  .modal-footer {
    padding: 12px 16px;
  }

  .btn-cancel,
  .btn-submit {
    padding: 10px 20px;
    font-size: 0.65rem;
  }
}
</style>
