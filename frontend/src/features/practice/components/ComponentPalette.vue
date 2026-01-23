<template>
  <div class="palette">
    <h2>⚡ Components</h2>

    <!-- 그룹 A. 진입 및 연산 (Compute & Entry) -->
    <div class="component-group">
      <h3>Compute & Entry</h3>
      <div
        v-for="comp in computeComponents"
        :key="comp.type"
        class="component"
        :class="comp.type"
        draggable="true"
        @dragstart="onDragStart($event, comp.type, comp.label)"
      >
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
        :class="comp.type"
        draggable="true"
        @dragstart="onDragStart($event, comp.type, comp.label)"
      >
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
        :class="comp.type"
        draggable="true"
        @dragstart="onDragStart($event, comp.type, comp.label)"
      >
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
        :class="comp.type"
        draggable="true"
        @dragstart="onDragStart($event, comp.type, comp.label)"
      >
        {{ comp.label }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ComponentPalette',
  emits: ['drag-start'],
  data() {
    return {
      computeComponents: [
        { type: 'user', label: '👤 User/Client' },
        { type: 'loadbalancer', label: '⚖️ Load Balancer' },
        { type: 'gateway', label: '🚪 API Gateway' },
        { type: 'server', label: '🖥️ Compute Service' }
      ],
      storageComponents: [
        { type: 'rdbms', label: '🗃️ Relational DB' },
        { type: 'nosql', label: '📊 NoSQL DB' },
        { type: 'cache', label: '⚡ In-Memory Cache' },
        { type: 'search', label: '🔍 Search Engine' },
        { type: 'storage', label: '📦 Object Storage' }
      ],
      messagingComponents: [
        { type: 'broker', label: '📬 Message Broker' },
        { type: 'eventbus', label: '📡 Event Bus' }
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
    }
  }
};
</script>

<style scoped>
.palette {
  background: rgba(17, 24, 39, 0.98);
  padding: 20px;
  overflow-y: auto;
  border-right: 1px solid rgba(100, 181, 246, 0.3);
}

.palette h2 {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.3em;
  color: #00ff9d;
  margin: 0 0 20px 0;
  text-shadow: 0 0 15px rgba(0, 255, 157, 0.5);
}

.component-group {
  margin-bottom: 20px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  border: 1px solid rgba(100, 181, 246, 0.2);
}

.component-group h3 {
  font-family: 'Space Mono', monospace;
  font-size: 0.85em;
  color: #64b5f6;
  margin: 0 0 10px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(100, 181, 246, 0.3);
}

.component {
  padding: 12px 15px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: grab;
  font-size: 0.9em;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.component:active {
  cursor: grabbing;
}

.component:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
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
