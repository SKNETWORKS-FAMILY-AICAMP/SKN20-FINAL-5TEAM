<template>
  <div class="webcam-display">

    <!-- 웹캠 활성화 전 -->
    <div v-if="!isActive && !error" class="webcam-placeholder">
      <div class="placeholder-icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor" opacity="0.4">
          <path d="M17 10.5V7a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-3.5l4 4v-11l-4 4z"/>
        </svg>
      </div>
      <p class="placeholder-text">카메라 준비 중...</p>
    </div>

    <!-- 카메라 오류 -->
    <div v-else-if="error" class="webcam-error">
      <div class="error-icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor" opacity="0.5">
          <path d="M18.364 5.636a9 9 0 1 1-12.728 12.728A9 9 0 0 1 18.364 5.636zM12 7v6m0 2v2"/>
        </svg>
      </div>
      <p class="error-text">{{ error }}</p>
    </div>

    <!-- 웹캠 피드 -->
    <video
      v-show="isActive"
      ref="videoRef"
      class="webcam-video"
      autoplay
      muted
      playsinline
    ></video>

    <!-- 활성 표시 -->
    <div v-if="isActive" class="webcam-badge">
      <span class="live-dot"></span> LIVE
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

// [수정일: 2026-02-23] [vision] 비디오 준비 완료 이벤트 정의
const emit = defineEmits(['ready']);

const videoRef = ref(null);
const isActive = ref(false);
const error = ref('');

// [수정일: 2026-02-23] [vision] 부모 컴포넌트에서 비디오 DOM에 접근할 수 있도록 노출
defineExpose({
  videoRef
});

let stream = null;

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
      audio: false,
    });

    if (videoRef.value) {
      videoRef.value.srcObject = stream;
      
      // [수정일: 2026-02-23] [vision] 메타데이터가 로드되어 실제로 플레이 가능한 시점에 ready 이벤트 발생
      videoRef.value.onloadedmetadata = () => {
        isActive.value = true;
        emit('ready', videoRef.value);
      };
    }
  } catch (err) {
    if (err.name === 'NotAllowedError') {
      error.value = '카메라 권한이 없습니다';
    } else if (err.name === 'NotFoundError') {
      error.value = '카메라를 찾을 수 없습니다';
    } else {
      error.value = '카메라 연결 실패';
    }
  }
}

onMounted(() => {
  startCamera();
});

onUnmounted(() => {
  if (stream) {
    stream.getTracks().forEach(t => t.stop());
  }
});
</script>

<style scoped>
.webcam-display {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  background: #0a0c14;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 플레이스홀더 */
.webcam-placeholder,
.webcam-error {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.placeholder-icon,
.error-icon {
  color: rgba(255, 255, 255, 0.4);
}

.placeholder-text,
.error-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.35);
  margin: 0;
  text-align: center;
}

/* 웹캠 비디오 */
.webcam-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1); /* 거울 효과 */
}

/* LIVE 배지 */
.webcam-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: 5px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 3px 8px;
  border-radius: 99px;
  backdrop-filter: blur(4px);
}

.live-dot {
  width: 7px;
  height: 7px;
  background: #ef4444;
  border-radius: 50%;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
