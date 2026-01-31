import { ref, computed, watch, inject, provide } from 'vue'
import { levels as gameLevels } from '../data/game_levels'

// Create a symbol for provide/inject
const GameContextSymbol = Symbol('GameContext')

export const createGameContext = () => {
  const levelsList = gameLevels || []

  const getInitialCompleted = () => {
    try {
      const saved = localStorage.getItem('pseudo_completed_v3')
      return saved ? JSON.parse(saved) : []
    } catch (e) {
      return []
    }
  }

  const getInitialUnlocked = () => {
    try {
      const saved = localStorage.getItem('pseudo_unlocked_v3')
      const parsed = saved ? JSON.parse(saved) : [1]
      if (!parsed.includes(1)) parsed.push(1)
      return parsed
    } catch (e) {
      return [1]
    }
  }

  const completedLevels = ref(getInitialCompleted())
  const currentLevelId = ref(null)
  const unlockedLevels = ref(getInitialUnlocked())

  const duckStage = computed(() => {
    const maxUnlocked = Math.max(...unlockedLevels.value)
    if (maxUnlocked >= 10) return 'C'
    else if (maxUnlocked >= 5) return 'B'
    else return 'A'
  })

  // Watch for changes and sync to localStorage
  watch(
    [completedLevels, unlockedLevels],
    ([newCompleted, newUnlocked]) => {
      localStorage.setItem('pseudo_completed_v3', JSON.stringify(newCompleted))
      localStorage.setItem('pseudo_unlocked_v3', JSON.stringify(newUnlocked))
    },
    { deep: true }
  )

  const completeLevel = (id) => {
    if (!completedLevels.value.includes(id)) {
      completedLevels.value.push(id)

      const nextId = id + 1
      if (nextId <= levelsList.length && !unlockedLevels.value.includes(nextId)) {
        unlockedLevels.value.push(nextId)
      }
    }
  }

  const getLevelStatus = (id) => {
    const intId = parseInt(id)
    if (completedLevels.value.includes(intId)) return 'completed'
    if (unlockedLevels.value.includes(intId)) return 'unlocked'
    return 'locked'
  }

  const context = {
    levels: levelsList,
    currentLevelId,
    setCurrentLevelId: (id) => {
      currentLevelId.value = id
    },
    completeLevel,
    getLevelStatus,
    duckStage,
    completedLevels,
    unlockedLevels
  }

  return context
}

export const useGameProvider = (context) => {
  provide(GameContextSymbol, context)
}

export const useGame = () => {
  const context = inject(GameContextSymbol)
  if (!context) {
    throw new Error('useGame() called without GameProvider')
  }
  return context
}
