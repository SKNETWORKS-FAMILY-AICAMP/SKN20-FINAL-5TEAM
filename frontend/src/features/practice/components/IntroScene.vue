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
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap');

/* === INTRO SCENE (Terminal 2077 스타일) === */
.scene-intro {
  --accent-green: #A3FF47;
  --accent-cyan: #00f3ff;
  --bg-dark: #05070A;
  --text-white: #ecf0f1;
  --terminal-font: 'Fira Code', monospace;

  width: 100%;
  height: 100%;
  background: var(--bg-dark);
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
  top: -100px;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 100%;
  background: radial-gradient(ellipse at top, rgba(163, 255, 71, 0.1) 0%, transparent 70%);
  pointer-events: none;
  z-index: 1;
}

/* 오리 형사 (거대 사이즈) */
.intro-duck {
  width: 350px;
  height: 350px;
  z-index: 2;
  filter: drop-shadow(0 0 30px rgba(163, 255, 71, 0.3));
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
}

/* 인트로 대화창 (하단 고정) */
.intro-dialog-box {
  position: absolute;
  bottom: 40px;
  width: 90%;
  max-width: 800px;
  background: rgba(163, 255, 71, 0.05);
  border: 1px solid rgba(163, 255, 71, 0.3);
  backdrop-filter: blur(10px);
  padding: 30px;
  z-index: 10;
}

.intro-dialog-inner {
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: 100%;
}

.speaker-name {
  color: var(--accent-green);
  font-family: var(--terminal-font);
  font-size: 0.9rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 3px;
  text-shadow: 0 0 10px rgba(163, 255, 71, 0.5);
}

.intro-text {
  font-family: var(--terminal-font);
  font-size: 1.2rem;
  line-height: 1.8;
  color: var(--text-white);
  flex: 1;
}

.next-indicator {
  align-self: flex-end;
  color: rgba(163, 255, 71, 0.6);
  font-family: var(--terminal-font);
  font-size: 0.75rem;
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
  background: var(--accent-green);
  color: #000;
  border: none;
  padding: 16px 32px;
  font-family: var(--terminal-font);
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  z-index: 20;
  box-shadow: 0 0 30px rgba(163, 255, 71, 0.4);
  transition: all 0.3s ease;
}

.start-btn:hover {
  transform: translate(-50%, -55%);
  box-shadow: 0 0 50px rgba(163, 255, 71, 0.6);
}
</style>
