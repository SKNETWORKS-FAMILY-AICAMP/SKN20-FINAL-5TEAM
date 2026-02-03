<template>
  <div class="scene-intro" @click="handleClick">
    <div class="spotlight"></div>

    <div class="intro-duck" :class="{ appear: duckAppeared }">
      <img src="/image/duck_det.png" alt="Detective Duck" />
    </div>

    <div class="intro-dialog-box" v-if="!showStartBtn">
      <div class="intro-dialog-inner">
        <div class="speaker-name">CODUCK_AI</div>
        <div class="intro-text">{{ displayedIntroText }}</div>
        <div class="next-indicator">▼ Click to continue</div>
      </div>
    </div>
    <button v-if="showStartBtn" class="start-btn" @click.stop="handleEnterGame">
      <span>INITIALIZE_PROTOCOL</span>
    </button>

  </div>
</template>

<script>
import { useIntro } from '../composables/useIntro';
import { onMounted, onUnmounted, watch } from 'vue';

export default {
  name: 'IntroScene',
  props: {
    introLines: {
      type: Array,
      default: () => [
        "[SYSTEM ALERT] 아키텍트님, 마더 서버에 이상 징후가 감지되었습니다. 꽥!",
        "오염된 AI들이 환각(Hallucination)에 빠져 시스템을 붕괴시키고 있습니다.",
        "당신만이 이 상황을 복구할 수 있습니다.",
        "올바른 시스템 아키텍처를 설계하여 데이터 무결성을 확보하세요!",
        "[PROTOCOL READY] 복구 터미널에 접속합니다..."
      ]
    }
  },
  emits: ['enter-game'],
  setup(props, { emit }) {
    const {
      displayedIntroText,
      duckAppeared,
      showStartBtn,
      introLines,
      nextIntroLine,
      enterGame,
      startIntroAnimation,
      cleanup
    } = useIntro(props.introLines);

    // Watch for prop changes
    watch(() => props.introLines, (newLines) => {
      introLines.value = newLines;
    });

    onMounted(() => {
      startIntroAnimation();
    });

    onUnmounted(() => {
      cleanup();
    });

    function handleClick() {
      nextIntroLine();
    }

    function handleEnterGame() {
      enterGame();
      emit('enter-game');
    }

    return {
      displayedIntroText,
      duckAppeared,
      showStartBtn,
      handleClick,
      handleEnterGame
    };
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

/* === INTRO SCENE (Among Us 스타일) === */
.scene-intro {
  --bg-space: #0d1117;
  --bg-panel: #1c2128;
  --bg-card: #252c35;
  --border-color: #373e47;
  --red: #c51111;
  --cyan: #38ffdd;
  --yellow: #f5f557;
  --white: #d3d4d4;

  width: 100%;
  height: 100%;
  background: var(--bg-space);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  cursor: pointer;
}

/* 스포트라이트 효과 */
.spotlight {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 800px;
  height: 100%;
  background: radial-gradient(ellipse at top, rgba(56, 255, 221, 0.08) 0%, transparent 60%);
  pointer-events: none;
  z-index: 1;
}

/* 오리 형사 (거대 사이즈) */
.intro-duck {
  width: 300px;
  height: 300px;
  z-index: 2;
  transform: translateY(50px);
  transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.intro-duck.appear {
  transform: translateY(0);
}

.intro-duck img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 0 30px rgba(56, 255, 221, 0.3));
}

/* 인트로 대화창 (하단 고정) */
.intro-dialog-box {
  position: absolute;
  bottom: 40px;
  width: 90%;
  max-width: 800px;
  background: var(--bg-panel);
  border: 4px solid var(--border-color);
  border-radius: 16px;
  padding: 25px 30px;
  z-index: 10;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.intro-dialog-inner {
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: 100%;
}

.speaker-name {
  color: var(--cyan);
  font-family: 'Nunito', sans-serif;
  font-size: 1rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.intro-text {
  font-family: 'Nunito', sans-serif;
  font-size: 1.15rem;
  font-weight: 600;
  line-height: 1.8;
  color: var(--white);
  flex: 1;
}

.next-indicator {
  align-self: flex-end;
  color: var(--yellow);
  font-family: 'Nunito', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 1px;
  animation: pulse-opacity 1.5s ease-in-out infinite;
}

@keyframes pulse-opacity {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* 시작 버튼 (인트로 끝날 때 등장) */
.start-btn {
  position: absolute;
  top: 83%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--red);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 18px 40px;
  font-family: 'Nunito', sans-serif;
  font-size: 1rem;
  font-weight: 800;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  z-index: 20;
  box-shadow: 0 6px 0 #8b0000;
  transition: all 0.2s ease;
}

.start-btn:hover {
  transform: translate(-50%, -55%);
  box-shadow: 0 8px 0 #8b0000;
}

.start-btn:active {
  transform: translate(-50%, -48%);
  box-shadow: 0 3px 0 #8b0000;
}
</style>
