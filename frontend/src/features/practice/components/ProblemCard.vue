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
    <!-- <div class="evidence-section" v-if="mermaidCode && mermaidCode.includes('comp_')">
      <strong class="section-label">[EVIDENCE]</strong>
      <div class="code-output">{{ mermaidCode }}</div>
    </div> -->
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
        ? '연결 모드 - 컴포넌트를 클릭하여 연결'
        : '배치 모드 - 컴포넌트를 드래그하여 배치';
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

.case-file-section {
  --nebula-purple: #6b5ce7;
  --nebula-blue: #4fc3f7;
  --nebula-pink: #f06292;
  --text-primary: #e8eaed;
  --text-secondary: rgba(232, 234, 237, 0.7);
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);
  --space-deep: #0a0a1a;

  display: flex;
  flex-direction: column;
  gap: 15px;
}

.case-file-folder {
  background: var(--glass-bg);
  padding: 2px;
  border: 1px solid var(--glass-border);
  border-radius: 12px;
}

.case-paper {
  background: rgba(10, 10, 26, 0.8);
  color: var(--text-primary);
  padding: 16px;
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.85rem;
  line-height: 1.5;
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  backdrop-filter: blur(10px);
}

.case-header {
  margin-bottom: 12px;
}

.case-number {
  background: linear-gradient(135deg, #6b5ce7, #4fc3f7);
  color: white;
  padding: 3px 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 2px;
  border-radius: 20px;
}

.case-title {
  color: var(--nebula-blue);
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  margin: 12px 0 10px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(79, 195, 247, 0.2);
  text-shadow: 0 0 10px rgba(79, 195, 247, 0.3);
  letter-spacing: 1px;
}

.case-section {
  margin-top: 12px;
}

.section-label {
  display: block;
  color: var(--nebula-purple);
  font-size: 0.6rem;
  margin-bottom: 6px;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 2px;
}

.case-section p {
  margin: 5px 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-family: 'Rajdhani', sans-serif;
}

.case-section ul {
  margin: 5px 0;
}

.case-section li {
  color: var(--text-secondary);
  margin-bottom: 4px;
  font-size: 0.82rem;
  font-family: 'Rajdhani', sans-serif;
}

.case-section.missions .section-label {
  color: var(--nebula-blue);
}

.case-section.constraints .section-label {
  color: var(--nebula-pink);
}

/* 모드 인디케이터 */
.mode-indicator {
  background: rgba(107, 92, 231, 0.1);
  border: 1px solid rgba(107, 92, 231, 0.3);
  border-radius: 12px;
  padding: 10px;
  font-size: 0.65rem;
  text-align: center;
  color: var(--nebula-purple);
  transition: all 0.3s ease;
  font-family: 'Rajdhani', sans-serif;
  font-weight: 600;
}

.mode-indicator.connection-mode {
  background: rgba(79, 195, 247, 0.1);
  border-color: rgba(79, 195, 247, 0.3);
  color: var(--nebula-blue);
}

/* 제출 버튼 */
.submit-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #6b5ce7, #4fc3f7);
  border: none;
  color: white;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-radius: 30px;
}

.submit-btn:hover:not(:disabled) {
  box-shadow: 0 10px 30px rgba(107, 92, 231, 0.4);
  transform: translateY(-3px);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  filter: grayscale(0.3);
}

.loading-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Evidence Section */
/* .evidence-section {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 12px;
  backdrop-filter: blur(10px);
}

.evidence-section .section-label {
  color: var(--nebula-purple);
  margin-bottom: 8px;
} */

.code-output {
  background: rgba(10, 10, 26, 0.8);
  color: var(--nebula-blue);
  padding: 10px;
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.75rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 150px;
  overflow-y: auto;
  border-radius: 8px;
  border: 1px solid var(--glass-border);
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
  background: rgba(107, 92, 231, 0.3);
  border-radius: 10px;
}
</style>
