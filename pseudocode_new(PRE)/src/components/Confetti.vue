<template>
  <div
    ref="canvas"
    :style="{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      pointerEvents: 'none',
      zIndex: 2147483647
    }"
  ></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import confetti from 'canvas-confetti'

const props = defineProps({
  numberOfPieces: {
    type: Number,
    default: 200
  }
})

const canvas = ref(null)

onMounted(() => {
  if (canvas.value) {
    confetti({
      particleCount: props.numberOfPieces,
      spread: 70,
      origin: { y: 0.6 }
    })
  }
})
</script>
