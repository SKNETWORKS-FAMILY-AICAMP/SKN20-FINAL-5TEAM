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
import { useIntro } from '../composables/useIntro';
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

/* === INTRO SCENE (sa_panic_room.html 스타일) === */
.scene-intro {
  --accent-yellow: #f1c40f;
  --danger-red: #e74c3c;
  --text-white: #ecf0f1;
  --pixel-font: 'Press Start 2P', cursive;
  --typewriter-font: 'Courier Prime', monospace;

  width: 100%;
  height: 100%;
  background: #111;
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
  background: radial-gradient(ellipse at top, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
  pointer-events: none;
  z-index: 1;
}

/* 오리 형사 (거대 사이즈) */
.intro-duck {
  width: 400px;
  height: 400px;
  z-index: 2;
  filter: drop-shadow(0 0 20px rgba(0, 0, 0, 0.5));
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
  height: 200px;
  background: rgba(0, 0, 0, 0.9);
  border: 4px solid white;
  border-radius: 10px;
  padding: 30px;
  z-index: 10;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 1);
}

.intro-dialog-inner {
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: 100%;
}

.speaker-name {
  color: var(--accent-yellow);
  font-family: var(--pixel-font);
  font-size: 1.2rem;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.intro-text {
  font-family: var(--typewriter-font);
  font-size: 1.5rem;
  line-height: 1.6;
  color: white;
  flex: 1;
}

.next-indicator {
  align-self: flex-end;
  color: var(--accent-yellow);
  font-family: var(--pixel-font);
  font-size: 0.8rem;
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

/* 시작 버튼 (인트로 끝날 때 등장) */
.start-btn {
  position: absolute;
  top: 83%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--danger-red);
  color: white;
  border: 4px solid white;
  padding: 20px 40px;
  font-family: var(--pixel-font);
  font-size: 1.5rem;
  cursor: pointer;
  z-index: 20;
  box-shadow: 10px 10px 0 black;
  animation: sway 2s ease-in-out infinite;
}

@keyframes sway {
  0%, 100% { transform: translate(-50%, -50%) translateX(-10px); }
  50% { transform: translate(-50%, -50%) translateX(10px); }
}

.start-btn:hover {
  animation: none;
  transform: translate(-50%, -55%);
}
</style>
