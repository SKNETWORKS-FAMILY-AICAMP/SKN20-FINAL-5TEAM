<template>
  <div class="path-container" @click="() => console.log('Container clicked')">
    <div class="path-line"></div>

    <div v-if="safeLevels.length === 0" style="color: white; text-align: center; margin-top: 100px">
      Loading...
    </div>

    <template v-else>
      <div v-for="(level, index) in safeLevels" :key="level.id" class="level-row">
        <div class="node-container" :style="offsetStyle(index)">
          <!-- Duck Avatar -->
          <div v-if="isDuckHere(level.id)" class="duck-wrapper">
            <Duck />
          </div>

          <button
            @click.stop="handleNodeClick(level)"
            :disabled="getLevelStatus(level.id) === 'locked'"
            :class="`level-node ${getLevelStatus(level.id)}`"
          >
            {{ getLevelStatus(level.id) === 'completed' ? '★' : level.id }}
          </button>

          <div class="level-label">
            {{ level.title }}
          </div>
        </div>
      </div>
    </template>

    <div style="height: 100px"></div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useGame } from '../composables/useGame'
import Duck from './Duck.vue'

const { levels, getLevelStatus, setCurrentLevelId, unlockedLevels } = useGame()

const safeLevels = computed(() => levels || [])

const currentMaxLevel = computed(() => {
  const unlocked = unlockedLevels.value || [1]
  return Math.max(...unlocked)
})

onMounted(() => {
  console.log('PathMap Mounted. Unlocked:', unlockedLevels.value)
})

const isDuckHere = (levelId) => {
  return levelId === currentMaxLevel.value
}

const offsetStyle = (index) => {
  const isLeft = index % 2 === 0
  return isLeft ? { marginRight: '100px' } : { marginLeft: '100px' }
}

const handleNodeClick = (level) => {
  if (getLevelStatus(level.id) === 'locked') {
    console.warn('User clicked locked level:', level.id)
    return
  }
  console.log('Opening Level:', level.id)
  setCurrentLevelId(level.id)
}
</script>

<style scoped>
@import '../styles/PathMap.css';
</style>
