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
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

.case-file-panel {
  --bg-panel: #1c2128;
  --bg-card: #252c35;
  --border-color: #373e47;
  --cyan: #38ffdd;
  --yellow: #f5f557;
  --white: #d3d4d4;

  width: 320px;
  min-width: 320px;
  background: var(--bg-panel);
  border-right: 3px solid var(--border-color);
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
  background: #0d1117;
}

.case-file-panel::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 10px;
}

.detective-profile {
  text-align: center;
  padding: 15px;
  background: var(--bg-card);
  border: 2px solid var(--border-color);
  border-radius: 12px;
}

.profile-pic {
  display: flex;
  justify-content: center;
}

.detective-avatar {
  width: 70px;
  height: 70px;
  border: 3px solid var(--cyan);
  border-radius: 50%;
  object-fit: contain;
  background: #0d1117;
}

.detective-name {
  color: var(--cyan);
  margin: 12px 0 0 0;
  font-family: 'Nunito', sans-serif;
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 1px;
}

/* === 케이스 파일 폴더 === */
.case-file-folder {
  padding: 4px;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-card);
  position: relative;
}

.case-file-folder::after {
  content: 'MISSION';
  position: absolute;
  top: -10px;
  right: 15px;
  background: var(--yellow);
  color: #1c2128;
  font-size: 0.65rem;
  padding: 4px 10px;
  font-family: 'Nunito', sans-serif;
  font-weight: 800;
  letter-spacing: 1px;
  border-radius: 4px;
}
</style>
