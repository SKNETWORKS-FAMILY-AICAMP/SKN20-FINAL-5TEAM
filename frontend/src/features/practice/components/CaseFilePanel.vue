<template>
  <div class="case-file-panel">
    <!-- 오리 형사 프로필 -->
    <div class="detective-profile">
      <div class="profile-pic">
        <img src="/image/duck_det.png" alt="Detective Duck" class="detective-avatar" />
      </div>
      <p class="detective-name">CODUCK_AI</p>
    </div>

    <!-- 케이스 파일 폴더 -->
    <div class="case-file-folder">
      <!-- 문제 카드 -->
      <ProblemCard
        :problem="problem"
        :is-connection-mode="isConnectionMode"
        :can-evaluate="canEvaluate"
        :is-evaluating="isEvaluating"
        :mermaid-code="mermaidCode"
        @start-evaluation="$emit('start-evaluation')"
      />
    </div>

  </div>
</template>

<script>
import ProblemCard from './ProblemCard.vue';

export default {
  name: 'CaseFilePanel',
  components: {
    ProblemCard
  },
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
  emits: ['start-evaluation']
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap');

.case-file-panel {
  --bg-panel: rgba(163, 255, 71, 0.05);
  --panel-border: rgba(163, 255, 71, 0.2);
  --accent-green: #A3FF47;
  --accent-cyan: #00f3ff;
  --text-white: #ecf0f1;
  --terminal-font: 'Fira Code', monospace;

  width: 320px;
  min-width: 320px;
  background: var(--bg-panel);
  border-right: 1px solid var(--panel-border);
  backdrop-filter: blur(10px);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  z-index: 20;
}

/* 스크롤바 커스텀 */
.case-file-panel::-webkit-scrollbar {
  width: 4px;
}

.case-file-panel::-webkit-scrollbar-track {
  background: transparent;
}

.case-file-panel::-webkit-scrollbar-thumb {
  background: rgba(163, 255, 71, 0.2);
  border-radius: 10px;
}

.detective-profile {
  text-align: center;
  padding: 15px;
  background: rgba(163, 255, 71, 0.03);
  border: 1px solid var(--panel-border);
}

.profile-pic {
  display: flex;
  justify-content: center;
}

.detective-avatar {
  width: 60px;
  height: 60px;
  border: 2px solid var(--accent-green);
  border-radius: 50%;
  object-fit: contain;
  background: #000;
  box-shadow: 0 0 15px rgba(163, 255, 71, 0.3);
}

.detective-name {
  color: var(--accent-green);
  margin: 10px 0 0 0;
  font-family: var(--terminal-font);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 2px;
  text-shadow: 0 0 8px rgba(163, 255, 71, 0.5);
}

/* === 케이스 파일 폴더 === */
.case-file-folder {
  padding: 4px;
  border: 1px solid var(--panel-border);
  background: rgba(163, 255, 71, 0.02);
  position: relative;
}

.case-file-folder::after {
  content: 'CLASSIFIED';
  position: absolute;
  top: -10px;
  right: 10px;
  background: var(--accent-green);
  color: #000;
  font-size: 0.55rem;
  padding: 3px 8px;
  font-family: var(--terminal-font);
  font-weight: 700;
  letter-spacing: 1px;
}
</style>
