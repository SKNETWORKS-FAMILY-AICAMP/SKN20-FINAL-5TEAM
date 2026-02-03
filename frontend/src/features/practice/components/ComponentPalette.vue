<template>
  <div class="palette" :class="{ 'hint-mode': isHintActive }">
    <!-- 힌트 안내 메시지 -->
    <!-- <div v-if="isHintActive && requiredTypes.length > 0" class="hint-guide">
      <span class="hint-guide-icon">💡</span>
      <span>필수 컴포넌트가 강조됩니다!</span>
    </div> -->

    <!-- 그룹 A. 진입 및 연산 (Compute & Entry) -->
    <div class="component-group">
      <h3>Compute & Entry</h3>
      <div
        v-for="comp in computeComponents"
        :key="comp.type"
        class="component"
        :class="[comp.type, { 'required-hint': isHintActive && isRequired(comp.type), 'dimmed': isHintActive && !isRequired(comp.type) }]"
        draggable="true"
        @dragstart="onDragStart($event, comp.type, comp.label)"
      >
        <span v-if="isHintActive && isRequired(comp.type)" class="required-badge">필수</span>
        {{ comp.label }}
      </div>
    </div>

    <!-- 그룹 B. 저장소 및 검색 (Storage & Search) -->
    <div class="component-group">
      <h3>Storage & Search</h3>
      <div
        v-for="comp in storageComponents"
        :key="comp.type"
        class="component"
        :class="[comp.type, { 'required-hint': isHintActive && isRequired(comp.type), 'dimmed': isHintActive && !isRequired(comp.type) }]"
        draggable="true"
        @dragstart="onDragStart($event, comp.type, comp.label)"
      >
        <span v-if="isHintActive && isRequired(comp.type)" class="required-badge">필수</span>
        {{ comp.label }}
      </div>
    </div>

    <!-- 그룹 C. 메시징 및 비동기 (Messaging) -->
    <div class="component-group">
      <h3>Messaging</h3>
      <div
        v-for="comp in messagingComponents"
        :key="comp.type"
        class="component"
        :class="[comp.type, { 'required-hint': isHintActive && isRequired(comp.type), 'dimmed': isHintActive && !isRequired(comp.type) }]"
        draggable="true"
        @dragstart="onDragStart($event, comp.type, comp.label)"
      >
        <span v-if="isHintActive && isRequired(comp.type)" class="required-badge">필수</span>
        {{ comp.label }}
      </div>
    </div>

    <!-- 그룹 D. 운영 및 관제 (Observability) -->
    <div class="component-group">
      <h3>Observability</h3>
      <div
        v-for="comp in observabilityComponents"
        :key="comp.type"
        class="component"
        :class="[comp.type, { 'required-hint': isHintActive && isRequired(comp.type), 'dimmed': isHintActive && !isRequired(comp.type) }]"
        draggable="true"
        @dragstart="onDragStart($event, comp.type, comp.label)"
      >
        <span v-if="isHintActive && isRequired(comp.type)" class="required-badge">필수</span>
        {{ comp.label }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ComponentPalette',
  props: {
    requiredTypes: {
      type: Array,
      default: () => []
    },
    isHintActive: {
      type: Boolean,
      default: false
    }
  },
  emits: ['drag-start'],
  data() {
    return {
      computeComponents: [
        { type: 'user', label: '👤 Client' },
        { type: 'loadbalancer', label: '⚖️ Load Balancer' },
        { type: 'gateway', label: '🚪 API Gateway' },
        { type: 'server', label: '🖥️ Server' }
      ],
      storageComponents: [
        { type: 'rdbms', label: '🗃️ RDBMS' },
        { type: 'nosql', label: '📊 NoSQL' },
        { type: 'cache', label: '⚡ Cache (Redis)' },
        { type: 'search', label: '🔍 Search Engine' },
        { type: 'storage', label: '📦 Object Storage' }
      ],
      messagingComponents: [
        { type: 'broker', label: '📬 Message Queue' },
        { type: 'eventbus', label: '📡 Pub/Sub' }
      ],
      observabilityComponents: [
        { type: 'monitoring', label: '📈 Monitoring' },
        { type: 'logging', label: '📋 Logging' },
        { type: 'cicd', label: '🔄 CI/CD' }
      ]
    };
  },
  methods: {
    onDragStart(event, type, text) {
      event.dataTransfer.setData('componentType', type);
      event.dataTransfer.setData('componentText', text);
      this.$emit('drag-start', { type, text });
    },
    isRequired(type) {
      return this.requiredTypes.includes(type);
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

.palette {
  --space-deep: #0a0a1a;
  --nebula-purple: #6b5ce7;
  --nebula-blue: #4fc3f7;
  --nebula-pink: #f06292;
  --text-primary: #e8eaed;
  --text-secondary: rgba(232, 234, 237, 0.7);
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);

  background: transparent;
  padding: 8px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 스크롤바 커스텀 */
.palette::-webkit-scrollbar {
  width: 6px;
}

.palette::-webkit-scrollbar-track {
  background: var(--space-deep);
}

.palette::-webkit-scrollbar-thumb {
  background: rgba(107, 92, 231, 0.4);
  border-radius: 10px;
}

.palette h2 {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.6rem;
  font-weight: 700;
  color: var(--nebula-blue);
  margin: 0 0 8px 0;
  text-align: center;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--glass-border);
  letter-spacing: 2px;
}

/* Hint Guide - Compact */
.hint-guide {
  background: rgba(79, 195, 247, 0.1);
  border: 1px solid rgba(79, 195, 247, 0.3);
  border-radius: 12px;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 0.6rem;
  font-weight: 600;
  color: var(--nebula-blue);
  font-family: 'Rajdhani', sans-serif;
  animation: hint-fade-in 0.3s ease;
}

.hint-guide span:last-child {
  display: none;
}

@keyframes hint-fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Component Groups - Compact */
.component-group {
  margin-bottom: 8px;
}

.component-group h3 {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.5rem;
  font-weight: 700;
  color: var(--text-secondary);
  margin: 0 0 6px 0;
  padding: 6px 8px;
  text-align: left;
  background: var(--glass-bg);
  border-left: 2px solid var(--nebula-purple);
  border-radius: 0 6px 6px 0;
  letter-spacing: 2px;
}

/* Tool Items - Space Mission Style */
.component {
  height: 50px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  margin-bottom: 6px;
  cursor: grab;
  font-size: 0.9rem;
  font-weight: 600;
  font-family: 'Rajdhani', sans-serif;
  transition: all 0.3s ease;
  position: relative;
  user-select: none;
  backdrop-filter: blur(5px);
}

.component::before {
  display: none;
}

.component:active {
  cursor: grabbing;
  transform: scale(0.96);
}

.component:hover {
  border-color: var(--nebula-purple);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(107, 92, 231, 0.3);
  background: rgba(107, 92, 231, 0.1);
}

/* Required component hint styles */
.component.required-hint {
  border-color: var(--nebula-blue) !important;
  background: rgba(79, 195, 247, 0.1);
  animation: required-glow 1.5s ease-in-out infinite;
}

@keyframes required-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(79, 195, 247, 0.3);
  }
  50% {
    box-shadow: 0 0 25px rgba(79, 195, 247, 0.6);
  }
}

.required-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: linear-gradient(135deg, #6b5ce7, #4fc3f7);
  color: white;
  font-size: 0.5rem;
  padding: 3px 8px;
  font-weight: 700;
  font-family: 'Orbitron', sans-serif;
  border-radius: 20px;
  z-index: 1;
  letter-spacing: 1px;
}

/* Dimmed styles for non-required components */
.component.dimmed {
  opacity: 0.3;
  filter: grayscale(30%);
}
</style>
