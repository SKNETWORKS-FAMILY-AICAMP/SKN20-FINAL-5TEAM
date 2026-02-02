<template>
  <div class="case-file-section">
    <!-- 케이스 파일 폴더 -->
    <div class="case-file-folder" v-if="problem">
      <div class="case-paper">
        <div class="case-header">
          <span class="case-number">CASE #{{ problem.id || '2026-Q' }}</span>
        </div>

        <h3 class="case-title">{{ problem.title }}</h3>

        <!-- 시나리오 (SITUATION) -->
        <div class="case-section" v-if="problem.scenario">
          <strong class="section-label">[SITUATION]</strong>
          <p>{{ problem.scenario }}</p>
        </div>

        <!-- 미션 (MISSION) -->
        <div class="case-section missions" v-if="problem.missions && problem.missions.length">
          <strong class="section-label">[MISSION]</strong>
          <ul>
            <li v-for="(mission, i) in problem.missions" :key="i">{{ mission }}</li>
          </ul>
        </div>

        <!-- 제약조건 (CONSTRAINTS) -->
        <div class="case-section constraints" v-if="problem.requirements && problem.requirements.length">
          <strong class="section-label">[CONSTRAINTS]</strong>
          <ul>
            <li v-for="(req, i) in problem.requirements" :key="i">{{ req }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 모드 인디케이터 -->
    <!-- <div
      class="mode-indicator"
      :class="{ 'connection-mode': isConnectionMode }"
    >
      {{ modeIndicatorText }}
    </div> -->

    <!-- 제출 버튼 -->
    <button
      class="submit-btn"
      :disabled="!canEvaluate || isEvaluating"
      @click="$emit('start-evaluation')"
    >
      {{ isEvaluating ? 'INITIALIZING...' : 'EXECUTE_EVALUATION' }}
      <span v-if="isEvaluating" class="loading-spinner"></span>
    </button>

    <!-- Generated Code (Optional) -->
    <div class="evidence-section" v-if="mermaidCode && mermaidCode.includes('comp_')">
      <strong class="section-label">[EVIDENCE]</strong>
      <div class="code-output">{{ mermaidCode }}</div>
    </div>
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
        ? '⚡ 연결 모드 - 컴포넌트를 클릭하여 연결'
        : '📦 배치 모드 - 컴포넌트를 드래그하여 배치';
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap');

.case-file-section {
  --accent-green: #A3FF47;
  --accent-cyan: #00f3ff;
  --accent-pink: #ec4899;
  --terminal-font: 'Fira Code', monospace;

  display: flex;
  flex-direction: column;
  gap: 15px;
}

.case-file-folder {
  background: rgba(163, 255, 71, 0.05);
  padding: 2px;
  border: 1px solid rgba(163, 255, 71, 0.3);
}

.case-paper {
  background: rgba(5, 7, 10, 0.9);
  color: #ecf0f1;
  padding: 16px;
  font-family: var(--terminal-font);
  font-size: 0.8rem;
  line-height: 1.5;
  border: 1px solid rgba(163, 255, 71, 0.1);
}

.case-header {
  margin-bottom: 12px;
}

.case-number {
  background: var(--accent-green);
  color: #000;
  padding: 3px 10px;
  font-family: var(--terminal-font);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 1px;
}

.case-title {
  color: var(--accent-green);
  font-size: 0.85rem;
  font-weight: 700;
  margin: 12px 0 10px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(163, 255, 71, 0.2);
  text-shadow: 0 0 8px rgba(163, 255, 71, 0.3);
}

.case-section {
  margin-top: 12px;
}

.section-label {
  display: block;
  color: rgba(163, 255, 71, 0.7);
  font-size: 0.6rem;
  margin-bottom: 6px;
  font-family: var(--terminal-font);
  letter-spacing: 1px;
}

.case-section p {
  margin: 5px 0;
  color: rgba(236, 240, 241, 0.9);
  font-size: 0.8rem;
}

.case-section ul {
  margin: 5px 0;
  padding-left: 16px;
}

.case-section li {
  color: rgba(236, 240, 241, 0.8);
  margin-bottom: 4px;
  font-size: 0.78rem;
}

.case-section.missions .section-label {
  color: rgba(163, 255, 71, 0.7);
}

.case-section.constraints .section-label {
  color: rgba(163, 255, 71, 0.7);
}

/* 모드 인디케이터 */
.mode-indicator {
  background: rgba(163, 255, 71, 0.1);
  border: 1px solid rgba(163, 255, 71, 0.3);
  padding: 10px;
  font-size: 0.65rem;
  text-align: center;
  color: var(--accent-green);
  transition: all 0.3s ease;
  font-family: var(--terminal-font);
}

.mode-indicator.connection-mode {
  background: rgba(0, 243, 255, 0.1);
  border-color: rgba(0, 243, 255, 0.3);
  color: var(--accent-cyan);
}

/* 제출 버튼 */
.submit-btn {
  width: 100%;
  padding: 14px;
  background: var(--accent-green);
  border: none;
  color: #000;
  font-family: var(--terminal-font);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.submit-btn:hover:not(:disabled) {
  box-shadow: 0 0 30px rgba(163, 255, 71, 0.5);
  transform: translateY(-2px);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Evidence Section */
.evidence-section {
  background: rgba(163, 255, 71, 0.05);
  border: 1px solid rgba(163, 255, 71, 0.3);
  padding: 10px;
}

.evidence-section .section-label {
  color: var(--accent-green);
  margin-bottom: 8px;
}

.code-output {
  background: rgba(0, 0, 0, 0.5);
  color: var(--accent-green);
  padding: 10px;
  font-family: var(--terminal-font);
  font-size: 0.7rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 150px;
  overflow-y: auto;
}

/* 스크롤바 커스텀 */
.code-output::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}

.code-output::-webkit-scrollbar-track {
  background: transparent;
}

.code-output::-webkit-scrollbar-thumb {
  background: rgba(163, 255, 71, 0.2);
  border-radius: 10px;
}
</style>
