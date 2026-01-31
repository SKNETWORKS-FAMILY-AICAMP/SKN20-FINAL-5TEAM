<template>
  <div :style="{ minHeight: '100vh', backgroundColor: '#131f24', color: 'white' }">
    <PathMap />
    <ProblemSolver />
  </div>
</template>

<script setup>
import { createGameContext, useGameProvider } from './composables/useGame'
import PathMap from './components/PathMap.vue'
import ProblemSolver from './components/ProblemSolver.vue'

// Initialize game context and provide it
const gameContext = createGameContext()
useGameProvider(gameContext)
</script>

<style scoped>
</style>
