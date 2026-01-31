<template>
  <div class="workspace-header">
    <div class="header-title">
      <div class="rec-dot"></div>
      <span>REC | ARCHITECTURE_ROOM</span>
    </div>
    <div class="header-controls">
      <button
        class="ctrl-btn"
        :class="{ active: isConnectionMode }"
        @click="$emit('toggle-mode')"
      >
        {{ isConnectionMode ? '📦 배치 모드' : '🔗 연결 모드' }}
      </button>
      <button class="ctrl-btn danger" @click="$emit('clear-canvas')">🗑️ 초기화</button>
      <button
        class="ctrl-btn hint"
        :class="{ active: isHintActive }"
        @click="$emit('toggle-hint')"
      >
        💡 {{ isHintActive ? '힌트 OFF' : '힌트 ON' }}
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
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

.workspace-header {
  --pixel-font: 'Press Start 2P', cursive;
  --text-white: #ecf0f1;
  --accent-yellow: #f1c40f;
  --danger-red: #e74c3c;

  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: #2d3436;
  border-bottom: 4px solid #000;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
  z-index: 50;
}

.header-title {
  font-family: var(--pixel-font);
  font-size: 0.8rem;
  color: #aaa;
  letter-spacing: 2px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.rec-dot {
  width: 12px;
  height: 12px;
  background: red;
  border-radius: 50%;
  animation: blink 1s infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.header-controls {
  display: flex;
  gap: 10px;
}

/* === 3D 버튼 스타일 === */
.ctrl-btn {
  font-family: var(--pixel-font);
  background: #333;
  color: var(--text-white);
  border: 2px solid #7f8c8d;
  border-bottom: 4px solid #7f8c8d;
  padding: 8px 15px;
  font-size: 0.7rem;
  cursor: pointer;
  text-transform: uppercase;
  transition: all 0.1s;
}

.ctrl-btn:hover {
  background: #444;
  margin-top: -2px;
  border-bottom-width: 6px;
}

.ctrl-btn:active {
  margin-top: 2px;
  border-bottom-width: 2px;
}

.ctrl-btn.active {
  background: var(--accent-yellow);
  color: black;
  border-color: #f39c12;
  box-shadow: 0 0 10px var(--accent-yellow);
}

.ctrl-btn.danger {
  background: var(--danger-red);
  border-color: #c0392b;
  color: white;
}

.ctrl-btn.danger:hover {
  background: #c0392b;
}

.ctrl-btn.hint {
  background: #333;
  border-color: #7f8c8d;
}

.ctrl-btn.hint.active {
  background: var(--accent-yellow);
  color: black;
  border-color: #f39c12;
  box-shadow: 0 0 10px var(--accent-yellow);
  animation: hint-pulse 1s infinite;
}

@keyframes hint-pulse {
  0%, 100% { box-shadow: 0 0 10px rgba(241, 196, 15, 0.5); }
  50% { box-shadow: 0 0 20px rgba(241, 196, 15, 0.8), 0 0 30px rgba(241, 196, 15, 0.4); }
}
</style>
