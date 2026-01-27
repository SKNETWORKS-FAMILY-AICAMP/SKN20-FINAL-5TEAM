<template>
  <div class="problem-section">
    <h2>🎯 CHALLENGE</h2>

    <div class="problem-card" v-if="problem">
      <h3>{{ problem.title }}</h3>

      <!-- 시나리오 -->
      <p class="scenario" v-if="problem.scenario">{{ problem.scenario }}</p>

      <!-- 미션 -->
      <div class="problem-missions" v-if="problem.missions && problem.missions.length">
        <h4>🚀 미션</h4>
        <ul>
          <li v-for="(mission, i) in problem.missions" :key="i">{{ mission }}</li>
        </ul>
      </div>

      <!-- 기술 요구사항 -->
      <div class="problem-requirements" v-if="problem.requirements && problem.requirements.length">
        <h4>📋 기술 요구사항</h4>
        <ul>
          <li v-for="(req, i) in problem.requirements" :key="i">{{ req }}</li>
        </ul>
      </div>
    </div>

    <div
      class="mode-indicator"
      :class="{ 'connection-mode': isConnectionMode }"
    >
      {{ modeIndicatorText }}
    </div>

    <button
      class="evaluate-btn"
      :disabled="!canEvaluate || isEvaluating"
      @click="$emit('start-evaluation')"
    >
      {{ isEvaluating ? '🤖 분석 중...' : '📤 아키텍처 제출' }}
      <span v-if="isEvaluating" class="loading-spinner"></span>
    </button>

    <!-- Mermaid Preview -->
    <div class="preview-section" v-if="mermaidCode">
      <h3 class="section-title">📊 Mermaid Preview</h3>
      <div class="mermaid-preview" ref="mermaidPreview"></div>
    </div>

    <!-- Generated Code -->
    <div class="code-section" v-if="mermaidCode">
      <h3 class="section-title">💻 Generated Code</h3>
      <div class="code-output">{{ mermaidCode }}</div>
    </div>
  </div>
</template>

<script>
import mermaid from 'mermaid';

export default {
  name: 'ProblemCard',
  props: {
    problem: {
      type: Object,
      default: null
    },
    isConnectionMode: {
      type: Boolean,
      default: false
    },
    canEvaluate: {
      type: Boolean,
      default: false
    },
    isEvaluating: {
      type: Boolean,
      default: false
    },
    mermaidCode: {
      type: String,
      default: ''
    }
  },
  emits: ['start-evaluation'],
  computed: {
    modeIndicatorText() {
      return this.isConnectionMode
        ? '🔗 연결 모드 - 컴포넌트를 클릭하여 연결하세요'
        : '🎯 배치 모드 - 컴포넌트를 드래그하여 배치하세요';
    }
  },
  watch: {
    mermaidCode: {
      handler(newCode) {
        if (newCode) {
          this.$nextTick(() => {
            this.renderMermaid();
          });
        }
      },
      immediate: true
    }
  },
  methods: {
    async renderMermaid() {
      const container = this.$refs.mermaidPreview;
      if (!container || !this.mermaidCode) return;

      try {
        const { svg } = await mermaid.render('mermaid-preview-' + Date.now(), this.mermaidCode);
        container.innerHTML = svg;
      } catch (error) {
        container.innerHTML = '<p class="mermaid-error">다이어그램 렌더링 중 오류가 발생했습니다.</p>';
      }
    }
  }
};
</script>

<style scoped>
.problem-section {
  padding: 20px;
}

.problem-section h2 {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.2em;
  color: #ff4785;
  margin: 0 0 15px 0;
  text-shadow: 0 0 15px rgba(255, 71, 133, 0.5);
}

.problem-card {
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 15px;
  border: 1px solid rgba(100, 181, 246, 0.3);
  position: relative;
}

.problem-card h3 {
  color: #64b5f6;
  margin: 0 0 10px 0;
  font-size: 1.1em;
}

.problem-card .scenario {
  color: #b0bec5;
  font-size: 0.9em;
  margin-bottom: 15px;
  line-height: 1.6;
  padding: 10px;
  background: rgba(100, 181, 246, 0.1);
  border-radius: 8px;
  border-left: 3px solid #64b5f6;
}

.problem-missions {
  background: rgba(255, 71, 133, 0.1);
  border-radius: 8px;
  padding: 12px;
  margin-top: 10px;
}

.problem-missions h4 {
  color: #ff4785;
  margin: 0 0 8px 0;
  font-size: 0.95em;
}

.problem-missions ul {
  margin: 0;
  padding-left: 20px;
}

.problem-missions li {
  color: #e0e0e0;
  font-size: 0.85em;
  margin-bottom: 6px;
  line-height: 1.5;
}

.problem-requirements {
  background: rgba(0, 255, 157, 0.1);
  border-radius: 8px;
  padding: 12px;
  margin-top: 10px;
}

.problem-requirements h4 {
  color: #00ff9d;
  margin: 0 0 8px 0;
  font-size: 0.95em;
}

.problem-requirements ul {
  margin: 0;
  padding-left: 20px;
}

.problem-requirements li {
  color: #e0e0e0;
  font-size: 0.85em;
  margin-bottom: 4px;
  line-height: 1.4;
}

.mode-indicator {
  background: rgba(100, 181, 246, 0.15);
  border: 1px solid rgba(100, 181, 246, 0.3);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 15px;
  font-size: 0.85em;
  text-align: center;
  color: #64b5f6;
  transition: all 0.3s ease;
}

.mode-indicator.connection-mode {
  background: rgba(0, 255, 157, 0.15);
  border-color: rgba(0, 255, 157, 0.3);
  color: #00ff9d;
}

.evaluate-btn {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #ff4785, #ff1744);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-family: 'Space Mono', monospace;
  font-size: 1em;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.evaluate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 71, 133, 0.4);
}

.evaluate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Preview & Code Sections */
.preview-section,
.code-section {
  margin-top: 15px;
}

.section-title {
  color: #64b5f6;
  margin: 0 0 10px 0;
  font-size: 0.95em;
  font-family: 'Orbitron', sans-serif;
}

.mermaid-preview {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 8px;
  border: 1px solid rgba(0, 255, 157, 0.2);
  min-height: 100px;
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

.code-output {
  background: rgba(0, 0, 0, 0.5);
  color: #00ff9d;
  padding: 15px;
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8em;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  border: 1px solid rgba(0, 255, 157, 0.2);
  max-height: 200px;
  overflow-y: auto;
}
</style>
