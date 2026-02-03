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
        {{ isConnectionMode ? 'CONNECT_MODE' : 'PLACE_MODE'  }}
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
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

.workspace-header {
  --space-deep: #0a0a1a;
  --space-dark: #12122a;
  --nebula-purple: #6b5ce7;
  --nebula-blue: #4fc3f7;
  --nebula-pink: #f06292;
  --text-primary: #e8eaed;
  --text-secondary: rgba(232, 234, 237, 0.7);
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);

  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--glass-border);
  z-index: 50;
}

.header-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--nebula-blue);
  letter-spacing: 2px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.rec-dot {
  width: 10px;
  height: 10px;
  background: var(--nebula-pink);
  border-radius: 50%;
  animation: pulse-glow 1.5s infinite;
  box-shadow: 0 0 8px rgba(240, 98, 146, 0.6);
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px rgba(240, 98, 146, 0.6); }
  50% { opacity: 0.4; box-shadow: 0 0 16px rgba(240, 98, 146, 0.9); }
}

.header-controls {
  display: flex;
  gap: 10px;
}

/* === Space Mission 버튼 스타일 === */
.ctrl-btn {
  font-family: 'Orbitron', sans-serif;
  background: var(--glass-bg);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
  border-radius: 30px;
  padding: 8px 18px;
  font-size: 0.65rem;
  font-weight: 700;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 2px;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.ctrl-btn:hover {
  border-color: var(--nebula-purple);
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(107, 92, 231, 0.3);
}

.ctrl-btn.active {
  background: linear-gradient(135deg, #6b5ce7, #4fc3f7);
  color: white;
  border-color: transparent;
  box-shadow: 0 0 20px rgba(107, 92, 231, 0.4);
}

.ctrl-btn.danger {
  background: var(--glass-bg);
  border-color: rgba(240, 98, 146, 0.4);
  color: var(--nebula-pink);
}

.ctrl-btn.danger:hover {
  background: rgba(240, 98, 146, 0.15);
  border-color: var(--nebula-pink);
  box-shadow: 0 0 20px rgba(240, 98, 146, 0.3);
}

.ctrl-btn.hint {
  border-color: rgba(79, 195, 247, 0.4);
  color: var(--nebula-blue);
}

.ctrl-btn.hint.active {
  background: linear-gradient(135deg, #4fc3f7, #6b5ce7);
  color: white;
  border-color: transparent;
  animation: hint-pulse 1.5s infinite;
}

@keyframes hint-pulse {
  0%, 100% { box-shadow: 0 0 15px rgba(79, 195, 247, 0.4); }
  50% { box-shadow: 0 0 30px rgba(79, 195, 247, 0.7); }
}
</style>
