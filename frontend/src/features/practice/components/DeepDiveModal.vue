<template>
  <div class="modal-overlay" :class="{ active: isActive }">
    <div class="interrogation-frame">
      <!-- 헤더 -->
      <div class="frame-header">
        <div class="header-left">
          <div class="header-title">INTERROGATION IN PROGRESS</div>
          <div class="header-meta">
            <span class="rec">REC</span>
            <span v-if="totalQuestions > 0">질문 {{ currentQuestion }} / {{ totalQuestions }}</span>
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
          <p>용의자의 설계도를 분석 중... 꽥!</p>
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
                <div class="det-name">DET. DUCK</div>
                <!-- <div class="det-category" v-if="category">{{ categoryIcon }} {{ category }}</div> -->
                <p class="det-question">{{ question }}</p>
              </div>
            </div>

            <!-- 용의자 진술 -->
            <div class="testimony-section">
              <div class="testimony-label">[ANSWER]</div>
              <textarea
                class="testimony-input"
                v-model="answer"
                placeholder="진술하세요... (거짓말은 금지! 꽥!)"
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
          {{ isLastQuestion ? '묵비권 행사 (평가)' : '묵비권 (건너뛰기)' }}
        </button>
        <button
          class="btn btn-submit"
          @click="submitAnswer"
          :disabled="isGenerating"
        >
          {{ isLastQuestion ? '최종 진술 (평가)' : '진술 완료' }}
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
    }
  },
  emits: ['skip', 'submit'],
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
      this.$emit('submit', this.answer.trim());
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
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Courier+Prime:wght@400;700&display=swap');

/* =====================
   OVERLAY
===================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at top, #444 0%, #000 60%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

/* CRT Noise */
.modal-overlay::after {
  content: "";
  position: fixed;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2'/%3E%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E");
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
  background: #111;
  border: 6px solid #555;
  box-shadow: 0 0 40px rgba(255, 0, 0, 0.25);
  position: relative;
  overflow-y: auto;
  transform: scale(0.9);
  transition: transform 0.3s ease;
}

.modal-overlay.active .interrogation-frame {
  transform: scale(1);
}

/* =====================
   HEADER
===================== */
.frame-header {
  padding: 16px 20px;
  border-bottom: 3px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #0a0a0a;
}

.header-title {
  font-family: 'Press Start 2P', cursive;
  font-size: 14px;
  color: #e74c3c;
  letter-spacing: 2px;
  margin-bottom: 6px;
}

.header-meta {
  font-family: 'Courier Prime', monospace;
  font-size: 12px;
  color: #aaa;
  display: flex;
  align-items: center;
  gap: 12px;
}

.rec {
  color: #ff3b3b;
  font-weight: bold;
  animation: blink 1s infinite;
}

.rec::before {
  content: "● ";
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.3; }
}

.header-right {
  min-width: 150px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #333;
  border: 2px solid #555;
}

.progress-fill {
  height: 100%;
  background: #e74c3c;
  transition: width 0.3s ease;
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
  border: 4px solid rgba(231, 76, 60, 0.3);
  border-top-color: #e74c3c;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-section p {
  color: #e74c3c;
  font-family: 'Courier Prime', monospace;
  font-size: 1rem;
}

/* =====================
   EVIDENCE (Left)
===================== */
.evidence-section {
  background: #0b0b0b;
  border: 3px solid #555;
  padding: 15px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-family: 'Press Start 2P', cursive;
  font-size: 10px;
  color: #aaa;
  margin-bottom: 12px;
}

.diagram-container {
  flex: 1;
  min-height: 220px;
  border: 2px dashed #444;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  padding: 10px;
}

.diagram-placeholder {
  color: #666;
  font-family: 'Courier Prime', monospace;
}

.diagram-container :deep(svg) {
  width: 100%;
  height: auto;
  max-height: 240px;
}

.mermaid-error {
  color: #e74c3c;
  font-size: 0.8rem;
}

/* Stamp */
.stamp {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-12deg);
  border: 6px solid #c0392b;
  color: #c0392b;
  font-family: 'Press Start 2P', cursive;
  font-size: 16px;
  padding: 12px 20px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
  background: rgba(0, 0, 0, 0.7);
}

.stamp.stamp-active {
  opacity: 0.85;
}

/* =====================
   DETECTIVE (Right)
===================== */
.detective-section {
  background: #0b0b0b;
  border: 3px solid #555;
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
  border: 3px solid #f1c40f;
  background: #222;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
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
  font-family: 'Press Start 2P', cursive;
  font-size: 10px;
  color: #f1c40f;
  margin-bottom: 6px;
}

.det-category {
  display: inline-block;
  padding: 3px 8px;
  background: rgba(231, 76, 60, 0.2);
  border: 2px solid #e74c3c;
  font-family: 'Press Start 2P', cursive;
  font-size: 8px;
  color: #e74c3c;
  margin-bottom: 8px;
}

.det-question {
  font-family: 'Courier Prime', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #eaeaea;
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
  font-family: 'Press Start 2P', cursive;
  font-size: 9px;
  color: #e74c3c;
}

.testimony-input {
  flex: 1;
  min-height: 80px;
  background: #000;
  border: 3px solid #e74c3c;
  padding: 12px;
  color: #eaeaea;
  font-family: 'Courier Prime', monospace;
  font-size: 14px;
  resize: none;
  transition: border-color 0.3s ease;
}

.testimony-input:focus {
  outline: none;
  border-color: #e74c3c;
}

.testimony-input::placeholder {
  color: rgba(234, 234, 234, 0.4);
}

/* =====================
   FOOTER
===================== */
.frame-footer {
  border-top: 3px solid #333;
  padding: 15px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  background: #0a0a0a;
}

.btn {
  flex: 1;
  max-width: 250px;
  padding: 14px 20px;
  font-family: 'Press Start 2P', cursive;
  font-size: 1.0rem;
  cursor: pointer;
  border: 3px solid #000;
  transition: all 0.2s ease;
}

.btn-submit {
  background: #f1c40f;
  color: #000;
}

.btn-submit:hover:not(:disabled) {
  background: #f39c12;
  transform: translateY(-2px);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-silent {
  background: #333;
  color: #aaa;
}

.btn-silent:hover {
  background: #444;
  color: #fff;
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
