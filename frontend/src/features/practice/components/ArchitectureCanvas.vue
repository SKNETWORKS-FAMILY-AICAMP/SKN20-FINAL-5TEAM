<template>
  <div class="canvas">
    <div class="canvas-header">
      <h2>⚡ ARCHITECTURE CANVAS</h2>
      <div class="btn-group">
        <button
          class="btn btn-mode"
          :class="{ active: isConnectionMode }"
          @click="toggleMode"
        >
          {{ isConnectionMode ? '🎯 배치' : '🔗 연결' }}
        </button>
        <button class="btn btn-clear" @click="clearCanvas">🗑️ 초기화</button>
      </div>
    </div>

    <div
      class="canvas-area"
      ref="canvasArea"
      @dragover.prevent
      @drop="onDrop"
      @mousemove="onMouseMove"
      @mouseup="stopDragging"
      @mouseleave="stopDragging"
    >
      <!-- Connection Lines -->
      <template v-for="(conn, index) in renderedConnections" :key="'conn-'+index">
        <div class="connection-line" :style="conn.lineStyle"></div>
        <div class="connection-arrow" :style="conn.arrowStyle"></div>
      </template>

      <!-- Dropped Components -->
      <div
        v-for="comp in components"
        :key="comp.id"
        :id="comp.id"
        class="dropped-component"
        :class="[comp.type, { selected: selectedComponentId === comp.id }]"
        :style="{ left: comp.x + 'px', top: comp.y + 'px' }"
        @mousedown.stop="onComponentMouseDown($event, comp)"
        @dblclick.stop="startEditingComponent(comp.id)"
      >
        <input
          v-if="editingComponentId === comp.id"
          v-model="editingComponentText"
          class="component-name-input"
          @blur="finishEditingComponent"
          @keyup.enter="finishEditingComponent"
          @keyup.escape="cancelEditingComponent"
          @click.stop
          @mousedown.stop
          ref="componentNameInput"
        />
        <span v-else>{{ comp.text }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ArchitectureCanvas',
  props: {
    components: {
      type: Array,
      default: () => []
    },
    connections: {
      type: Array,
      default: () => []
    },
    isConnectionMode: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'toggle-mode',
    'clear-canvas',
    'component-dropped',
    'component-moved',
    'component-renamed',
    'connection-created',
    'component-selected'
  ],
  data() {
    return {
      selectedComponentId: null,
      editingComponentId: null,
      editingComponentText: '',
      draggingComponentId: null,
      dragStartPos: { mouseX: 0, mouseY: 0, compX: 0, compY: 0 }
    };
  },
  computed: {
    renderedConnections() {
      return this.connections.map(conn => {
        const fromComp = this.components.find(c => c.id === conn.from);
        const toComp = this.components.find(c => c.id === conn.to);

        if (!fromComp || !toComp) return null;

        const width = 140;
        const height = 50;

        const x1 = fromComp.x + width / 2;
        const y1 = fromComp.y + height / 2;
        const x2 = toComp.x + width / 2;
        const y2 = toComp.y + height / 2;

        const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
        const angle = Math.atan2(y2 - y1, x2 - x1) * (180 / Math.PI);

        return {
          lineStyle: {
            width: `${length}px`,
            left: `${x1}px`,
            top: `${y1}px`,
            transform: `rotate(${angle}deg)`
          },
          arrowStyle: {
            left: `${x2}px`,
            top: `${y2 - 6}px`,
            transform: `rotate(${angle}deg)`
          }
        };
      }).filter(Boolean);
    }
  },
  methods: {
    toggleMode() {
      this.selectedComponentId = null;
      this.$emit('toggle-mode');
    },
    clearCanvas() {
      if (confirm('모든 컴포넌트와 연결을 삭제하시겠습니까?')) {
        this.selectedComponentId = null;
        this.$emit('clear-canvas');
      }
    },
    onDrop(event) {
      if (this.isConnectionMode) return;

      const type = event.dataTransfer.getData('componentType');
      const text = event.dataTransfer.getData('componentText');
      if (!type) return;

      const rect = this.$refs.canvasArea.getBoundingClientRect();
      const x = event.clientX - rect.left - 70;
      const y = event.clientY - rect.top - 25;

      this.$emit('component-dropped', { type, text, x, y });
    },
    onComponentMouseDown(event, comp) {
      if (this.isConnectionMode) {
        this.handleConnectionClick(comp);
        return;
      }

      this.draggingComponentId = comp.id;
      this.dragStartPos = {
        mouseX: event.clientX,
        mouseY: event.clientY,
        compX: comp.x,
        compY: comp.y
      };
    },
    onMouseMove(event) {
      if (!this.draggingComponentId) return;

      const comp = this.components.find(c => c.id === this.draggingComponentId);
      if (comp) {
        const deltaX = event.clientX - this.dragStartPos.mouseX;
        const deltaY = event.clientY - this.dragStartPos.mouseY;

        const newX = this.dragStartPos.compX + deltaX;
        const newY = this.dragStartPos.compY + deltaY;

        this.$emit('component-moved', { id: comp.id, x: newX, y: newY });
      }
    },
    stopDragging() {
      if (this.draggingComponentId) {
        this.draggingComponentId = null;
      }
    },
    handleConnectionClick(comp) {
      if (this.selectedComponentId === comp.id) {
        this.selectedComponentId = null;
        return;
      }

      if (!this.selectedComponentId) {
        this.selectedComponentId = comp.id;
        this.$emit('component-selected', comp);
      } else {
        const fromComp = this.components.find(c => c.id === this.selectedComponentId);
        this.$emit('connection-created', {
          from: this.selectedComponentId,
          to: comp.id,
          fromType: fromComp.type,
          toType: comp.type
        });
        this.selectedComponentId = null;
      }
    },
    startEditingComponent(compId) {
      if (this.isConnectionMode) return;
      const comp = this.components.find(c => c.id === compId);
      if (!comp) return;

      this.editingComponentId = compId;
      this.editingComponentText = comp.text;

      this.$nextTick(() => {
        const input = this.$refs.componentNameInput;
        if (input && input[0]) {
          input[0].focus();
          input[0].select();
        }
      });
    },
    finishEditingComponent() {
      if (!this.editingComponentId) return;

      if (this.editingComponentText.trim()) {
        this.$emit('component-renamed', {
          id: this.editingComponentId,
          text: this.editingComponentText.trim()
        });
      }

      this.editingComponentId = null;
      this.editingComponentText = '';
    },
    cancelEditingComponent() {
      this.editingComponentId = null;
      this.editingComponentText = '';
    }
  }
};
</script>

<style scoped>
.canvas {
  background: linear-gradient(145deg, rgba(10, 14, 39, 0.95), rgba(17, 24, 39, 0.98));
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(100, 181, 246, 0.3);
}

.canvas-header {
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(0, 255, 157, 0.3);
  background: rgba(0, 0, 0, 0.3);
}

.canvas-header h2 {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.3em;
  color: #00ff9d;
  margin: 0;
  text-shadow: 0 0 15px rgba(0, 255, 157, 0.5);
}

.btn-group {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-family: 'Space Mono', monospace;
  font-size: 0.85em;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-mode {
  background: rgba(100, 181, 246, 0.2);
  color: #64b5f6;
  border: 1px solid #64b5f6;
}

.btn-mode.active {
  background: #64b5f6;
  color: #0a0e27;
}

.btn-clear {
  background: rgba(255, 71, 133, 0.2);
  color: #ff4785;
  border: 1px solid #ff4785;
}

.btn-clear:hover {
  background: #ff4785;
  color: #fff;
}

.canvas-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(rgba(100, 181, 246, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(100, 181, 246, 0.05) 1px, transparent 1px);
  background-size: 30px 30px;
}

.dropped-component {
  position: absolute;
  padding: 12px 18px;
  border-radius: 10px;
  cursor: move;
  font-size: 0.9em;
  font-weight: 600;
  min-width: 140px;
  text-align: center;
  transition: box-shadow 0.2s ease, transform 0.1s ease;
  border: 2px solid transparent;
  user-select: none;
}

.dropped-component:hover {
  transform: scale(1.02);
}

.dropped-component.selected {
  border-color: #00ff9d;
  box-shadow: 0 0 20px rgba(0, 255, 157, 0.6);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(0, 255, 157, 0.6); }
  50% { box-shadow: 0 0 30px rgba(0, 255, 157, 0.9); }
}

/* Component type styles */
.dropped-component.user { background: linear-gradient(135deg, #ff4785, #ff1744); color: #fff; }
.dropped-component.loadbalancer { background: linear-gradient(135deg, #26c6da, #00acc1); color: #0a0e27; }
.dropped-component.gateway { background: linear-gradient(135deg, #64b5f6, #2196f3); color: #fff; }
.dropped-component.server { background: linear-gradient(135deg, #ab47bc, #8e24aa); color: #fff; }
.dropped-component.rdbms { background: linear-gradient(135deg, #00ff9d, #00e676); color: #0a0e27; }
.dropped-component.nosql { background: linear-gradient(135deg, #4db6ac, #26a69a); color: #0a0e27; }
.dropped-component.cache { background: linear-gradient(135deg, #ffc107, #ffa000); color: #0a0e27; }
.dropped-component.search { background: linear-gradient(135deg, #7c4dff, #651fff); color: #fff; }
.dropped-component.storage { background: linear-gradient(135deg, #ff7043, #f4511e); color: #fff; }
.dropped-component.broker { background: linear-gradient(135deg, #ff8a65, #ff5722); color: #fff; }
.dropped-component.eventbus { background: linear-gradient(135deg, #ba68c8, #ab47bc); color: #fff; }
.dropped-component.monitoring { background: linear-gradient(135deg, #66bb6a, #43a047); color: #fff; }
.dropped-component.logging { background: linear-gradient(135deg, #78909c, #607d8b); color: #fff; }
.dropped-component.cicd { background: linear-gradient(135deg, #42a5f5, #1e88e5); color: #fff; }

.component-name-input {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid #00ff9d;
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'Space Mono', monospace;
  font-size: 0.9em;
  width: 100%;
  text-align: center;
}

/* Connection lines */
.connection-line {
  position: absolute;
  height: 3px;
  background: linear-gradient(90deg, #64b5f6, #00ff9d);
  transform-origin: left center;
  pointer-events: none;
  box-shadow: 0 0 8px rgba(100, 181, 246, 0.5);
}

.connection-arrow {
  position: absolute;
  width: 0;
  height: 0;
  border-left: 10px solid #00ff9d;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  transform-origin: left center;
  pointer-events: none;
  filter: drop-shadow(0 0 4px rgba(0, 255, 157, 0.8));
}
</style>
