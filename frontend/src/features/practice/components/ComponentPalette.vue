<template>
  <div class="palette" :class="{ 'hint-mode': isHintActive }">
    <h2>⚡ Components</h2>

    <!-- 힌트 안내 메시지 -->
    <div v-if="isHintActive && requiredTypes.length > 0" class="hint-guide">
      <span class="hint-guide-icon">💡</span>
      <span>필수 컴포넌트가 강조됩니다!</span>
    </div>

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
        { type: 'user', label: '👤 USER' },
        { type: 'loadbalancer', label: '⚖️ L7 LB' },
        { type: 'gateway', label: '🚪 GATEWAY' },
        { type: 'server', label: '🖥️ SERVER' }
      ],
      storageComponents: [
        { type: 'rdbms', label: '🗃️ RDBMS' },
        { type: 'nosql', label: '📊 NoSQL' },
        { type: 'cache', label: '⚡ CACHE' },
        { type: 'search', label: '🔍 SEARCH' },
        { type: 'storage', label: '📦 STORAGE' }
      ],
      messagingComponents: [
        { type: 'broker', label: '📬 MQ' },
        { type: 'eventbus', label: '📡 EVENT' }
      ],
      observabilityComponents: [
        { type: 'monitoring', label: '📈 MONITOR' },
        { type: 'logging', label: '📋 LOG' },
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

.hint-guide-icon {
  font-size: 0.8rem;
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

/* Tool Items - Compact Blocks */
.component {
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  margin-bottom: 4px;
  border-radius: 4px;
  cursor: grab;
  font-size: 0.5rem;
  font-weight: 600;
  font-family: 'Press Start 2P', cursive;
  transition: all 0.2s ease;
  border: 3px solid #000;
  position: relative;
  user-select: none;
  box-shadow: 3px 3px 0 rgba(0,0,0,0.5);
}

.component:active {
  cursor: grabbing;
  transform: translate(2px, 2px);
  box-shadow: 1px 1px 0 rgba(0,0,0,0.5);
}

.component:hover {
  transform: translateY(-2px);
  box-shadow: 5px 5px 0 rgba(0,0,0,0.5);
}

/* Required component hint styles */
.component.required-hint {
  border-color: #f1c40f !important;
  box-shadow: 0 0 10px rgba(241, 196, 15, 0.8), 3px 3px 0 rgba(0,0,0,0.5);
  animation: required-glow 1s ease-in-out infinite;
}

@keyframes required-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(241, 196, 15, 0.8), 3px 3px 0 rgba(0,0,0,0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(241, 196, 15, 1), 3px 3px 0 rgba(0,0,0,0.5);
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
}

/* Dimmed styles for non-required components */
.component.dimmed {
  opacity: 0.35;
  filter: grayscale(70%);
}

/* Compute & Entry */
.component.user { background: linear-gradient(135deg, #ff4785, #ff1744); color: #fff; }
.component.loadbalancer { background: linear-gradient(135deg, #26c6da, #00acc1); color: #0a0e27; }
.component.gateway { background: linear-gradient(135deg, #64b5f6, #2196f3); color: #fff; }
.component.server { background: linear-gradient(135deg, #ab47bc, #8e24aa); color: #fff; }

/* Storage & Search */
.component.rdbms { background: linear-gradient(135deg, #00ff9d, #00e676); color: #0a0e27; }
.component.nosql { background: linear-gradient(135deg, #4db6ac, #26a69a); color: #0a0e27; }
.component.cache { background: linear-gradient(135deg, #ffc107, #ffa000); color: #0a0e27; }
.component.search { background: linear-gradient(135deg, #7c4dff, #651fff); color: #fff; }
.component.storage { background: linear-gradient(135deg, #ff7043, #f4511e); color: #fff; }

/* Messaging */
.component.broker { background: linear-gradient(135deg, #ff8a65, #ff5722); color: #fff; }
.component.eventbus { background: linear-gradient(135deg, #ba68c8, #ab47bc); color: #fff; }

/* Observability */
.component.monitoring { background: linear-gradient(135deg, #66bb6a, #43a047); color: #fff; }
.component.logging { background: linear-gradient(135deg, #78909c, #607d8b); color: #fff; }
.component.cicd { background: linear-gradient(135deg, #42a5f5, #1e88e5); color: #fff; }
</style>
