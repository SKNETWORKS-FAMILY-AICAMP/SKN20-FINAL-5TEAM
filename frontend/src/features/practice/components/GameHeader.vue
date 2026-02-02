<template>
  <div class="workspace-header">
    <div class="header-title">
      <div class="rec-dot"></div>
      <span>LIVE | ARCHITECT_TERMINAL</span>
    </div>
    <div class="header-controls">
      <button
        class="ctrl-btn"
        :class="{ active: isConnectionMode }"
        @click="$emit('toggle-mode')"
      >
        {{ isConnectionMode ? 'PLACE_MODE' : 'CONNECT_MODE' }}
      </button>
      <button class="ctrl-btn danger" @click="$emit('clear-canvas')">RESET</button>
      <button
        class="ctrl-btn hint"
        :class="{ active: isHintActive }"
        @click="$emit('toggle-hint')"
      >
        {{ isHintActive ? 'HINT_OFF' : 'HINT_ON' }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GameHeader',
  props: {
    isConnectionMode: {
      type: Boolean,
      default: false
    },
    isHintActive: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle-mode', 'clear-canvas', 'toggle-hint']
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap');

.workspace-header {
  --terminal-font: 'Fira Code', monospace;
  --text-white: #ecf0f1;
  --accent-green: #A3FF47;
  --accent-pink: #ec4899;
  --bg-dark: #05070A;

  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: rgba(5, 7, 10, 0.9);
  border-bottom: 1px solid rgba(163, 255, 71, 0.2);
  backdrop-filter: blur(10px);
  z-index: 50;
}

.header-title {
  font-family: var(--terminal-font);
  font-size: 0.75rem;
  color: rgba(163, 255, 71, 0.6);
  letter-spacing: 2px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.rec-dot {
  width: 8px;
  height: 8px;
  background: var(--accent-green);
  border-radius: 50%;
  animation: pulse-glow 1.5s infinite;
  box-shadow: 0 0 8px var(--accent-green);
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--accent-green); }
  50% { opacity: 0.5; box-shadow: 0 0 4px var(--accent-green); }
}

.header-controls {
  display: flex;
  gap: 10px;
}

/* === 터미널 버튼 스타일 === */
.ctrl-btn {
  font-family: var(--terminal-font);
  background: rgba(163, 255, 71, 0.1);
  color: var(--accent-green);
  border: 1px solid rgba(163, 255, 71, 0.3);
  padding: 8px 16px;
  font-size: 0.7rem;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.2s ease;
}

.ctrl-btn:hover {
  background: rgba(163, 255, 71, 0.2);
  box-shadow: 0 0 15px rgba(163, 255, 71, 0.2);
}

.ctrl-btn.active {
  background: var(--accent-green);
  color: #000;
  border-color: var(--accent-green);
  box-shadow: 0 0 20px rgba(163, 255, 71, 0.5);
}

.ctrl-btn.danger {
  background: rgba(236, 72, 153, 0.1);
  border-color: rgba(236, 72, 153, 0.3);
  color: var(--accent-pink);
}

.ctrl-btn.danger:hover {
  background: rgba(236, 72, 153, 0.2);
  box-shadow: 0 0 15px rgba(236, 72, 153, 0.3);
}

.ctrl-btn.hint {
  background: rgba(163, 255, 71, 0.1);
  border-color: rgba(163, 255, 71, 0.3);
}

.ctrl-btn.hint.active {
  background: var(--accent-green);
  color: #000;
  border-color: var(--accent-green);
  box-shadow: 0 0 20px rgba(163, 255, 71, 0.5);
  animation: hint-pulse 1.5s infinite;
}

@keyframes hint-pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(163, 255, 71, 0.5); }
  50% { box-shadow: 0 0 35px rgba(163, 255, 71, 0.8); }
}
</style>
