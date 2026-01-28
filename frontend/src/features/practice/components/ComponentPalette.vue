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
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

.palette {
  background: #34495e;
  padding: 8px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.palette h2 {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.5rem;
  color: #f1c40f;
  margin: 0 0 8px 0;
  text-align: center;
  padding-bottom: 8px;
  border-bottom: 2px solid #2c3e50;
}

/* Hint Guide - Compact */
.hint-guide {
  background: rgba(241, 196, 15, 0.2);
  border: 2px solid #f1c40f;
  border-radius: 4px;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 0.5rem;
  color: #f1c40f;
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
  margin-bottom: 4px;
}

.component-group h3 {
  font-family: 'Press Start 2P', cursive;
  font-size: 0.4rem;
  color: #95a5a6;
  margin: 0 0 4px 0;
  padding: 4px 0;
  text-align: center;
  background: #2c3e50;
  border-radius: 2px;
}

/* Tool Items - Evidence Tag Style */
.component {
  height: 60px;
  background: #ecf0f1;
  border: 2px solid #bdc3c7;
  border-bottom: 4px solid #95a5a6;
  color: #2c3e50;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  margin-bottom: 6px;
  cursor: grab;
  font-size: 0.55rem;
  font-weight: 600;
  font-family: 'Press Start 2P', cursive;
  transition: all 0.15s ease;
  position: relative;
  user-select: none;
}

/* Tape look on top */
.component::before {
  content: '';
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 30%;
  height: 8px;
  background: rgba(0, 0, 0, 0.2);
}

.component:active {
  cursor: grabbing;
  border-bottom-width: 2px;
  transform: translateY(2px);
}

.component:hover {
  transform: scale(1.05);
}

/* Required component hint styles */
.component.required-hint {
  border-color: #f1c40f !important;
  box-shadow: 0 0 10px rgba(241, 196, 15, 0.8);
  animation: required-glow 1s ease-in-out infinite;
}

@keyframes required-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(241, 196, 15, 0.8);
  }
  50% {
    box-shadow: 0 0 20px rgba(241, 196, 15, 1);
  }
}

.required-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #f1c40f;
  color: #000;
  font-size: 0.35rem;
  padding: 2px 4px;
  border-radius: 2px;
  font-weight: 700;
  border: 2px solid #000;
  z-index: 1;
}

/* Dimmed styles for non-required components */
.component.dimmed {
  opacity: 0.35;
  filter: grayscale(70%);
}
</style>
