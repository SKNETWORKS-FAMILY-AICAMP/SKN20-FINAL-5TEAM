<template>
  <div class="modal-overlay" :class="{ active: isActive }">
    <div class="modal-window">
      <div class="modal-header">
        <h3>🧐 최종 질문</h3>
        <div class="modal-subtitle">AI Architect Bot</div>
      </div>
      <div class="modal-body">
        <div v-if="isGenerating" class="loading-question">
          <div class="loading-spinner-large"></div>
          <p>아키텍처를 분석하여 질문을 생성하는 중...</p>
        </div>
        <template v-else>
          <!-- Mermaid Preview -->
          <div class="mermaid-preview-section" v-if="mermaidCode">
            <span class="preview-title">📊 아키텍처 다이어그램</span>
            <div class="mermaid-preview" ref="mermaidPreview"></div>
          </div>

          <!-- 질문 -->
          <div class="ai-question">
            <span class="ai-question-title">QUESTION</span>
            <span>{{ question }}</span>
          </div>

          <!-- 답변 입력 -->
          <textarea
            class="user-answer"
            v-model="answer"
            placeholder="여기에 답변을 작성해주세요... (예: CDN을 사용하여 정적 리소스를 캐싱하여 부하를 줄입니다.)"
          ></textarea>
        </template>
      </div>
      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">취소</button>
        <button
          class="btn-submit"
          @click="submitAnswer"
          :disabled="isGenerating"
        >
          제출 완료
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
  computed: {
    formattedConnections() {
      return this.connections.map(conn => {
        const from = this.components.find(c => c.id === conn.from);
        const to = this.components.find(c => c.id === conn.to);
        if (from && to) {
          return `${from.text} → ${to.text}`;
        }
        return '';
      }).filter(Boolean);
    }
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
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.modal-overlay.active {
  opacity: 1;
  visibility: visible;
}

.modal-window {
  background: linear-gradient(145deg, #0a0e27, #111827);
  border: 2px solid #64b5f6;
  border-radius: 20px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(100, 181, 246, 0.3);
  transform: scale(0.9);
  transition: transform 0.3s ease;
}

.modal-overlay.active .modal-window {
  transform: scale(1);
}

.modal-header {
  padding: 25px;
  border-bottom: 1px solid rgba(100, 181, 246, 0.3);
  text-align: center;
}

.modal-header h3 {
  margin: 0 0 5px 0;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.5em;
  color: #64b5f6;
  text-shadow: 0 0 15px rgba(100, 181, 246, 0.5);
}

.modal-subtitle {
  color: #64b5f6;
  font-size: 0.9em;
}

.modal-body {
  padding: 25px;
}

.loading-question {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.loading-spinner-large {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(100, 181, 246, 0.3);
  border-top-color: #64b5f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-question p {
  color: #b0bec5;
  font-size: 1em;
}

/* Architecture Summary */
.architecture-summary {
  background: rgba(0, 255, 157, 0.1);
  border: 1px solid rgba(0, 255, 157, 0.3);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.summary-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.85em;
  color: #00ff9d;
  letter-spacing: 1px;
  display: block;
  margin-bottom: 12px;
}

.architecture-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.components-list,
.connections-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.list-label {
  font-size: 0.8em;
  color: #90a4ae;
  font-weight: 600;
}

.component-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.component-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75em;
  font-weight: 600;
}

/* Component tag colors */
.component-tag.user { background: #ff4785; color: #fff; }
.component-tag.loadbalancer { background: #26c6da; color: #0a0e27; }
.component-tag.gateway { background: #64b5f6; color: #fff; }
.component-tag.server { background: #ab47bc; color: #fff; }
.component-tag.rdbms { background: #00ff9d; color: #0a0e27; }
.component-tag.nosql { background: #4db6ac; color: #0a0e27; }
.component-tag.cache { background: #ffc107; color: #0a0e27; }
.component-tag.search { background: #7c4dff; color: #fff; }
.component-tag.storage { background: #ff7043; color: #fff; }
.component-tag.broker { background: #ff8a65; color: #fff; }
.component-tag.eventbus { background: #ba68c8; color: #fff; }
.component-tag.monitoring { background: #66bb6a; color: #fff; }
.component-tag.logging { background: #78909c; color: #fff; }
.component-tag.cicd { background: #42a5f5; color: #fff; }

.connection-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.connection-item {
  font-size: 0.8em;
  color: #b0bec5;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
}

/* Question */
.ai-question {
  background: rgba(100, 181, 246, 0.1);
  border: 1px solid rgba(100, 181, 246, 0.3);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-question-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8em;
  color: #64b5f6;
  letter-spacing: 2px;
}

.ai-question > span:last-child {
  font-size: 1.1em;
  color: #e0e0e0;
  line-height: 1.6;
}

.user-answer {
  width: 100%;
  min-height: 120px;
  background: rgba(0, 0, 0, 0.4);
  border: 2px solid rgba(100, 181, 246, 0.3);
  border-radius: 12px;
  padding: 15px;
  color: #e0e0e0;
  font-family: 'Space Mono', monospace;
  font-size: 0.95em;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.user-answer:focus {
  outline: none;
  border-color: #00ff9d;
}

.user-answer::placeholder {
  color: rgba(224, 224, 224, 0.4);
}

.modal-footer {
  padding: 20px 25px;
  border-top: 1px solid rgba(100, 181, 246, 0.3);
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.btn-cancel {
  padding: 12px 25px;
  background: transparent;
  border: 2px solid #78909c;
  border-radius: 8px;
  color: #78909c;
  font-family: 'Space Mono', monospace;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  background: #78909c;
  color: #0a0e27;
}

.btn-submit {
  padding: 12px 25px;
  background: linear-gradient(135deg, #00ff9d, #00e676);
  border: none;
  border-radius: 8px;
  color: #0a0e27;
  font-family: 'Space Mono', monospace;
  font-size: 0.9em;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 255, 157, 0.4);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Mermaid Preview */
.mermaid-preview-section {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 255, 157, 0.2);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.preview-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.85em;
  color: #64b5f6;
  letter-spacing: 1px;
  display: block;
  margin-bottom: 12px;
}

.mermaid-preview {
  background: rgba(0, 0, 0, 0.2);
  padding: 15px;
  border-radius: 8px;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}

.mermaid-preview :deep(svg) {
  max-width: 100%;
  height: auto;
}

.mermaid-error {
  color: #ff4785;
  font-size: 0.85em;
}
</style>
