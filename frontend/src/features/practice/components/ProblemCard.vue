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
      {{ isEvaluating ? '심문 준비 중...' : '제출 (SUBMIT)' }}
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
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Courier+Prime:wght@400;700&display=swap');

.case-file-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.case-file-folder {
  background: #e67e22;
  padding: 5px;
  border: 4px solid #000;
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.5);
}

.case-paper {
  background: #f4f3ee; 
  color: #1a1a1a; 
  padding: 20px;
  font-family: var(--typewriter-font); 
  font-size: 0.85rem; 
  line-height: 1.4;
  border: 1px solid #ccc;
  box-shadow: inset 0 0 20px rgba(0,0,0,0.1);
  background-image: linear-gradient(#ccc 1px, transparent 1px);
  background-size: 100% 1.4rem;
}

.case-header {
  margin-bottom: 10px;
}

.case-number {
  background: #000;
  color: #fff;
  padding: 3px 8px;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.6rem;
}

.case-title {
  color: #2c3e50;
  font-size: 0.9rem;
  margin: 10px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #bdc3c7;
}

.case-section {
  margin-top: 12px;
}

.section-label {
  display: block;
  color: #1a1a1a;
  font-size: 0.65rem;
  margin-bottom: 5px;
  font-family: 'Press Start 2P', cursive;
}

.case-section p {
  margin: 5px 0;
  color: #34495e;
}

.case-section ul {
  margin: 5px 0;
}

.case-section li {
  color: #34495e;
  margin-bottom: 4px;
}

.case-section.missions .section-label {
  color: #1a1a1a;
}

.case-section.constraints .section-label {
  color: #1a1a1a;
}

/* 모드 인디케이터 */
.mode-indicator {
  background: rgba(52, 152, 219, 0.2);
  border: 2px solid #3498db;
  border-radius: 4px;
  padding: 10px;
  font-size: 0.65rem;
  text-align: center;
  color: #3498db;
  transition: all 0.3s ease;
  font-family: 'Press Start 2P', cursive;
}

.mode-indicator.connection-mode {
  background: rgba(241, 196, 15, 0.2);
  border-color: #f1c40f;
  color: #f1c40f;
}

/* 제출 버튼 */
.submit-btn {
  width: 100%;
  padding: 15px;
  background: #e74c3c;
  border: 4px solid #000;
  color: #fff;
  font-family: 'Press Start 2P', cursive;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.5);
}

.submit-btn:hover:not(:disabled) {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 rgba(0, 0, 0, 0.5);
}

.submit-btn:active:not(:disabled) {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.5);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Evidence Section */
.evidence-section {
  background: rgba(0, 0, 0, 0.8);
  border: 2px solid #f1c40f;
  border-radius: 4px;
  padding: 10px;
}

.evidence-section .section-label {
  color: #f1c40f;
  margin-bottom: 8px;
}

.code-output {
  background: #000;
  color: #f1c40f;
  padding: 10px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 150px;
  overflow-y: auto;
}
</style>
