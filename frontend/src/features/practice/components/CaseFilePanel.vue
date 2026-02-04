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
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

.case-file-panel {
  --space-deep: #0a0a1a;
  --space-dark: #12122a;
  --nebula-purple: #6b5ce7;
  --nebula-blue: #4fc3f7;
  --nebula-pink: #f06292;
  --text-primary: #e8eaed;
  --text-secondary: rgba(232, 234, 237, 0.7);
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);

  width: 320px;
  min-width: 320px;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-right: 1px solid var(--glass-border);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  z-index: 20;
}

/* 스크롤바 커스텀 */
.case-file-panel::-webkit-scrollbar {
  width: 6px;
}

.case-file-panel::-webkit-scrollbar-track {
  background: var(--space-deep);
}

.case-file-panel::-webkit-scrollbar-thumb {
  background: rgba(107, 92, 231, 0.4);
  border-radius: 10px;
}

.detective-profile {
  text-align: center;
  padding: 15px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.profile-pic {
  display: flex;
  justify-content: center;
}

.detective-avatar {
  width: 70px;
  height: 70px;
  border: 2px solid var(--nebula-purple);
  border-radius: 50%;
  object-fit: contain;
  background: var(--space-deep);
  box-shadow: 0 0 15px rgba(107, 92, 231, 0.3);
}

.detective-name {
  color: var(--nebula-blue);
  margin: 12px 0 0 0;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 2px;
}

/* === 케이스 파일 폴더 === */
.case-file-folder {
  padding: 4px;
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  position: relative;
}

.case-file-folder::after {
  content: 'MISSION';
  position: absolute;
  top: -10px;
  right: 15px;
  background: linear-gradient(135deg, #6b5ce7, #4fc3f7);
  color: white;
  font-size: 0.6rem;
  padding: 4px 12px;
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  letter-spacing: 2px;
  border-radius: 20px;
  box-shadow: 0 0 12px rgba(107, 92, 231, 0.4);
}
</style>
