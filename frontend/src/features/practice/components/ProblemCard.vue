<template>
  <div class="problem-section">
    <h2>🎯 CHALLENGE</h2>

    <div class="problem-card" v-if="problem">
      <h3>{{ problem.title }}</h3>
      <p>{{ problem.description }}</p>
      <div class="problem-requirements">
        <h4>📋 요구사항</h4>
        <ul>
          <li v-for="(req, i) in problem.requirements" :key="i">{{ req }}</li>
        </ul>
      </div>
      <span
        class="difficulty-badge"
        :class="`difficulty-${problem.difficulty}`"
      >
        {{ problem.difficulty.toUpperCase() }}
      </span>
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
      {{ isEvaluating ? '🤖 분석 중...' : '🤖 AI 평가 시작' }}
      <span v-if="isEvaluating" class="loading-spinner"></span>
    </button>
  </div>
</template>

<script>
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
    }
  },
  emits: ['start-evaluation'],
  computed: {
    modeIndicatorText() {
      return this.isConnectionMode
        ? '🔗 연결 모드 - 컴포넌트를 클릭하여 연결하세요'
        : '🎯 배치 모드 - 컴포넌트를 드래그하여 배치하세요';
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
  padding-right: 60px;
}

.problem-card > p {
  color: #b0bec5;
  font-size: 0.9em;
  margin-bottom: 15px;
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

.difficulty-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75em;
  font-weight: 700;
}

.difficulty-easy {
  background: linear-gradient(135deg, #00ff9d, #00e676);
  color: #0a0e27;
}

.difficulty-medium {
  background: linear-gradient(135deg, #ffc107, #ffa000);
  color: #0a0e27;
}

.difficulty-hard {
  background: linear-gradient(135deg, #ff4785, #ff1744);
  color: #fff;
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
</style>
