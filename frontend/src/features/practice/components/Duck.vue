<template>
  <div
    class="duck-container"
    :class="className"
    :style="{
      position: 'relative',
      pointerEvents: 'none',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }"
  >
    <!-- Tooltip -->
    <div
      :style="{
        backgroundColor: '#1e293b',
        color: 'white',
        fontSize: '11px',
        fontWeight: 'bold',
        padding: '4px 8px',
        borderRadius: '6px',
        marginBottom: '4px',
        whiteSpace: 'nowrap',
        border: '1px solid #475569',
        boxShadow: '0 4px 6px rgba(0,0,0,0.3)'
      }"
    >
      {{ tooltipText }}
    </div>

    <!-- Duck Image -->
    <img
      :src="imageSrc"
      alt="Nano Banana"
      :style="{
        width: '70px',
        height: '70px',
        objectFit: 'contain',
        filter: 'drop-shadow(0 5px 5px rgba(0,0,0,0.5))',
        animation: 'bounce 2s infinite'
      }"
    />
  </div>
</template>

<script setup>
/**
 * 수정일: 2026-01-30
 * 수정내용: 오리 도우미 캐릭터 컴포넌트 추가 (진행도에 따른 칭호 변경)
 */
import { computed } from 'vue'
import { useGameStore } from '@/stores/game'

const props = defineProps({
  className: String
})

const gameStore = useGameStore()

const imageSrc = '/image/unit_duck.png' // 기존 프로젝트의 이미지 경로 사용

const tooltipText = computed(() => {
  const unlockedCount = gameStore.currentUnitProgress.length
  if (unlockedCount >= 6) return '팀장 오리 (CTO 진)'
  else if (unlockedCount >= 3) return '주니어 오리 (사원)'
  else return '신입 오리 (인턴)'
})
</script>

<style scoped>
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
</style>
