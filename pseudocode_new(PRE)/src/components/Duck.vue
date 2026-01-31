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
import { computed } from 'vue'
import { useGame } from '../composables/useGame'

const props = defineProps({
  className: String
})

const { duckStage } = useGame()

const imageSrc = '/assets/duck_nano_banana.png'

const tooltipText = computed(() => {
  if (duckStage.value === 'A') return '신입 오리 (인턴)'
  else if (duckStage.value === 'B') return '주니어 오리 (사원)'
  else return '팀장 오리 (CTO 진)'
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
