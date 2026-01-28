<template>
  <div class="case-file-panel">
    <!-- 오리 형사 프로필 -->
    <div class="detective-profile">
      <div class="profile-pic">
        <img src="/image/duck_det.png" alt="Detective Duck" class="detective-avatar" />
      </div>
      <p class="detective-name">DET. DUCK</p>
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
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

.case-file-panel {
  --panel-grey: #1a1a1a;
  --accent-yellow: #f1c40f;
  --danger-red: #e74c3c;
  --text-white: #ecf0f1;
  --pixel-font: 'Press Start 2P', cursive;

  width: 320px;
  min-width: 320px;
  background: var(--panel-grey);
  border-right: 4px solid #000;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  z-index: 20;
  box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5);
}

.detective-profile {
  text-align: center;
  border-bottom: 2px solid #333;
  padding-bottom: 15px;
  background: radial-gradient(circle, #333 0%, var(--panel-grey) 70%);
  border: 2px solid #555;
  padding: 15px;
}

.profile-pic {
  display: flex;
  justify-content: center;
}

.detective-avatar {
  width: 60px;
  height: 60px;
  border: 2px solid #777;
  border-radius: 50%;
  object-fit: contain;
  background: #000;
}

.detective-name {
  color: var(--accent-yellow);
  margin: 5px 0 0 0;
  font-family: var(--pixel-font);
  font-size: 0.7rem;
}

/* === 케이스 파일 폴더 === */
.case-file-folder {
  padding: 4px;
  border: 2px solid #000;
  box-shadow: 3px 3px 0 #000;
  position: relative;
}

.case-file-folder::after {
  content: 'CONFIDENTIAL';
  position: absolute;
  top: -10px;
  right: 10px;
  background: var(--danger-red);
  color: white;
  font-size: 0.5rem;
  padding: 2px 5px;
  transform: rotate(5deg);
  border: 1px solid white;
  font-family: var(--pixel-font);
}
</style>
