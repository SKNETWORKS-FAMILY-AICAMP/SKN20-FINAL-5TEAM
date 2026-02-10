<template>
  <div class="analyzing-duck-container">
    <!-- Cyberpunk Decorative Elements -->
    <div class="glow-bg"></div>
    <div class="scanline"></div>

    <div class="video-wrapper">
      <video
        autoplay
        loop
        muted
        playsinline
        class="duck-video"
      >
        <source src="/lp_duck.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <!-- Circular Progress Ring (Optional decoration) -->
      <div class="circular-glow"></div>
    </div>

    <div class="loading-content">
      <div class="status-msg">
        <span class="pulse-icon">📡</span>
        {{ message }}
        <span class="blinking-cursor">_</span>
      </div>

      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: displayPercent + '%' }"></div>
          <div class="progress-glitch"></div>
        </div>
        <div class="progress-stats">
          <span class="percent-text">{{ displayPercent }}%</span>
          <span class="loading-tag">ANALYZING_CORE_LOGIC</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  message: {
    type: String,
    default: 'AI 아키텍트가 분석 중입니다...'
  },
  duration: {
    type: Number,
    default: 5000 // Default visualization duration in ms
  }
});

const displayPercent = ref(0);
let interval = null;

onMounted(() => {
  // Simulate progress for visual appeal
  const step = 100; // updates every 100ms
  const increment = 100 / (props.duration / step);
  
  interval = setInterval(() => {
    if (displayPercent.value < 99) {
      displayPercent.value = Math.min(99, Math.floor(displayPercent.value + increment + Math.random() * 2));
    }
  }, step);
});

onUnmounted(() => {
  if (interval) clearInterval(interval);
});
</script>

<style scoped>
.analyzing-duck-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: rgba(5, 5, 5, 0.9);
  border: 1px solid rgba(0, 255, 157, 0.3);
  border-radius: 16px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 30px rgba(0, 255, 157, 0.1);
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

.glow-bg {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(0, 255, 157, 0.05) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
  pointer-events: none;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.scanline {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: rgba(0, 255, 157, 0.2);
  box-shadow: 0 0 10px rgba(0, 255, 157, 0.5);
  animation: scan 3s linear infinite;
  z-index: 10;
  pointer-events: none;
}

@keyframes scan {
  from { top: -2%; }
  to { top: 102%; }
}

.video-wrapper {
  position: relative;
  width: 200px;
  height: 200px;
  margin-bottom: 30px;
  border-radius: 50%;
  padding: 10px;
  background: rgba(0, 255, 157, 0.1);
  box-shadow: 0 0 20px rgba(0, 255, 157, 0.2);
}

.duck-video {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(0, 255, 157, 0.5);
}

.circular-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px dashed rgba(0, 255, 157, 0.3);
  animation: spin 10s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-content {
  width: 100%;
  text-align: center;
  z-index: 5;
}

.status-msg {
  font-family: 'JetBrains Mono', monospace;
  color: #00ff9d;
  font-size: 1.1rem;
  margin-bottom: 20px;
  text-shadow: 0 0 8px rgba(0, 255, 157, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.pulse-icon {
  animation: pulse 1s infinite alternate;
}

@keyframes pulse {
  from { opacity: 0.5; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1.1); }
}

.blinking-cursor {
  animation: blink 0.8s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.progress-container {
  width: 100%;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  border: 1px solid rgba(0, 255, 157, 0.2);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00ff9d, #00d4ff);
  box-shadow: 0 0 15px rgba(0, 255, 157, 0.6);
  transition: width 0.3s ease-out;
}

.progress-glitch {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: move-glitch 2s infinite linear;
}

@keyframes move-glitch {
  from { transform: translateX(-100%); }
  to { transform: translateX(100%); }
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  color: rgba(0, 255, 157, 0.7);
}

.loading-tag {
  letter-spacing: 1px;
}
</style>
