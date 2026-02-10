<!-- 
  [2026-02-10] 공통 아바타 프레임 컴포넌트
  - 역할: 이미지 로드 실패 대응, 전역 등급 스타일 적용, 호버 확대 기능 통합
-->
<template>
  <div 
    class="avatar-frame-container avatar-ranked" 
    :class="[rankClass, { 'allow-hover': hoverZoom }]"
    :style="containerStyle"
  >
    <img 
      :src="computedSrc" 
      @error="handleImageError" 
      :alt="alt"
      class="avatar-img"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  src: {
    type: String,
    default: null
  },
  rank: {
    type: String,
    default: 'BRONZE'
  },
  size: {
    type: String,
    default: '50px'
  },
  hoverZoom: {
    type: Boolean,
    default: false
  },
  alt: {
    type: String,
    default: 'User Avatar'
  }
});

const isError = ref(false);
const defaultAvatar = '/image/unit_duck.png';

// [중요] 백엔드 미디어 서버 주소 보정
const computedSrc = computed(() => {
  if (isError.value || !props.src) return defaultAvatar;
  
  // 이미 전체 URL(http://...)인 경우 그대로 사용
  if (props.src.startsWith('http')) return props.src;
  
  // 상대 경로(/media/...)인 경우 그대로 반환
  // Vite proxy(vite.config.js)가 /media를 백엔드로 전달하므로 상대 경로가 더 안전함
  if (props.src.startsWith('/media/')) {
    return props.src;
  }
  
  return props.src;
});

const rankClass = computed(() => `avatar-rank-${props.rank || 'BRONZE'}`);

const containerStyle = computed(() => ({
  width: props.size,
  height: props.size,
  minWidth: props.size,
  minHeight: props.size
}));

const handleImageError = () => {
  console.warn('Avatar image load failed, falling back to default:', props.src);
  isError.value = true;
};
</script>

<style scoped>
.avatar-frame-container {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #000;
  cursor: pointer;
  /* ranking.css의 .avatar-ranked 스타일을 상속받음 */
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

/* 호버 시 확대 효과 (호버 허용된 경우만) */
.avatar-frame-container.allow-hover:hover .avatar-img {
  /* LandingView 등에서 정의한 scale 효과와 조화되도록 설정 */
  transform: scale(1.1);
}

/* ranking.css가 전역에 임포트되어 있으므로 border-radius 등은 거기서 제어 */
</style>
