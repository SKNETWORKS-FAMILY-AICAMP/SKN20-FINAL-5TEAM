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
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

.workspace-header {
  --bg-panel: #1c2128;
  --bg-card: #252c35;
  --border-color: #373e47;
  --red: #c51111;
  --green: #11802d;
  --yellow: #f5f557;
  --cyan: #38ffdd;
  --white: #d3d4d4;

  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: var(--bg-panel);
  border-bottom: 3px solid var(--border-color);
  z-index: 50;
}

.header-title {
  font-family: 'Nunito', sans-serif;
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--white);
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.rec-dot {
  width: 10px;
  height: 10px;
  background: var(--red);
  border-radius: 50%;
  animation: pulse-glow 1.5s infinite;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.header-controls {
  display: flex;
  gap: 10px;
}

/* === 어몽어스 버튼 스타일 === */
.ctrl-btn {
  font-family: 'Nunito', sans-serif;
  background: var(--bg-card);
  color: var(--white);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.2s ease;
}

.ctrl-btn:hover {
  border-color: var(--cyan);
  transform: translateY(-2px);
}

.ctrl-btn.active {
  background: var(--cyan);
  color: #1c2128;
  border-color: var(--cyan);
}

.ctrl-btn.danger {
  background: var(--bg-card);
  border-color: var(--red);
  color: var(--red);
}

.ctrl-btn.danger:hover {
  background: var(--red);
  color: white;
}

.ctrl-btn.hint {
  border-color: var(--yellow);
  color: var(--yellow);
}

.ctrl-btn.hint.active {
  background: var(--yellow);
  color: #1c2128;
  border-color: var(--yellow);
  animation: hint-pulse 1.5s infinite;
}

@keyframes hint-pulse {
  0%, 100% { box-shadow: 0 0 10px rgba(245, 245, 87, 0.5); }
  50% { box-shadow: 0 0 20px rgba(245, 245, 87, 0.8); }
}
</style>
