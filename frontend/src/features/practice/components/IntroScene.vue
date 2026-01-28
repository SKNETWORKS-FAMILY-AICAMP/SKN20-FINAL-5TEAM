<template>
  <div class="scene-intro" @click="handleClick">
    <div class="spotlight"></div>

    <div class="intro-duck" :class="{ appear: duckAppeared }">
      <img src="/image/duck_det.png" alt="Detective Duck" />
    </div>

    <div class="intro-dialog-box" v-if="!showStartBtn">
      <div class="intro-dialog-inner">
        <div class="speaker-name">DET. DUCK</div>
        <div class="intro-text">{{ displayedIntroText }}</div>
        <div class="next-indicator">▼ Click to continue</div>
      </div>
    </div>

    <button v-if="showStartBtn" class="start-btn" @click.stop="handleEnterGame">
      <span>취조실 입장 (ENTER)</span>
    </button>
  </div>
</template>

<script>
import { useIntro } from '@/composables/useIntro';
import { onMounted, onUnmounted, watch } from 'vue';

export default {
  name: 'IntroScene',
  props: {
    introLines: {
      type: Array,
      default: () => [
        "거기 서! 도망갈 생각 마라. 꽥!",
        "네가 오늘 발생한 대규모 서버 폭파 사건의 가장 유력한 용의자로 지목되었다.",
        "억울하다고? 그렇다면 취조실로 들어와서 직접 증명해 봐.",
        "올바른 시스템 아키텍처를 설계해서 네 결백을 입증하는 거다!",
        "(철창 문이 열린다...)"
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
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Courier+Prime:wght@400;700&display=swap');

/* === INTRO SCENE === */
.scene-intro {
  --accent-yellow: #f1c40f;
  --danger-red: #e74c3c;
  --pixel-font: 'Press Start 2P', cursive;
  --typewriter-font: 'Courier Prime', monospace;

  width: 100%;
  height: 100%;
  background: #000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  position: relative;
  cursor: pointer;
}

.spotlight {
  position: absolute;
  top: -150px;
  left: 50%;
  transform: translateX(-50%);
  width: 800px;
  height: 120%;
  background: radial-gradient(ellipse at top, rgba(255, 255, 255, 0.1) 0%, transparent 60%);
  pointer-events: none;
  z-index: 1;
  animation: flickerLight 4s infinite alternate;
}

@keyframes flickerLight {
  0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% { opacity: 1; }
  20%, 24%, 55% { opacity: 0.8; }
}

.intro-duck {
  width: 400px;
  height: 400px;
  z-index: 2;
  filter: drop-shadow(0 0 30px rgba(0, 0, 0, 0.8)) sepia(0.3) contrast(1.2);
  transform: translateY(100px);
  opacity: 0;
  transition: all 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.intro-duck.appear {
  transform: translateY(0);
  opacity: 1;
}

.intro-duck img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.intro-dialog-box {
  width: 80%;
  height: 220px;
  background: rgba(10, 10, 10, 0.95);
  border: 2px solid #fff;
  box-shadow: 0 0 0 4px #000, 0 10px 40px rgba(0, 0, 0, 1);
  margin-bottom: 50px;
  padding: 25px;
  z-index: 10;
  position: relative;
}

.intro-dialog-box::before {
  content: '';
  position: absolute;
  top: 5px;
  left: 5px;
  right: 5px;
  bottom: 5px;
  border: 1px dashed #555;
  pointer-events: none;
}

.intro-dialog-inner {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
}

.speaker-name {
  color: var(--accent-yellow);
  font-family: var(--pixel-font);
  font-size: 1rem;
  text-shadow: 2px 2px 0 #000;
  background: #222;
  display: inline-block;
  padding: 5px 10px;
  border-left: 4px solid var(--accent-yellow);
}

.intro-text {
  font-family: var(--typewriter-font);
  font-size: 1.3rem;
  line-height: 1.6;
  color: #ddd;
  flex: 1;
}

.next-indicator {
  align-self: flex-end;
  color: var(--danger-red);
  font-family: var(--pixel-font);
  font-size: 0.7rem;
  animation: blink 1s infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.start-btn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: repeating-linear-gradient(45deg, #000, #000 10px, #e74c3c 10px, #e74c3c 20px);
  color: white;
  border: 4px solid white;
  padding: 20px 50px;
  font-family: var(--pixel-font);
  font-size: 1.2rem;
  text-shadow: 2px 2px 0 black;
  cursor: pointer;
  z-index: 20;
  box-shadow: 10px 10px 0 rgba(0, 0, 0, 0.8);
  transition: transform 0.1s;
}

.start-btn span {
  border-bottom: 2px solid white;
}

.start-btn:hover {
  transform: translate(-50%, -55%);
  filter: brightness(1.2);
}
</style>
