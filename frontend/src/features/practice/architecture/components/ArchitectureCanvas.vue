<template>
  <div class="canvas">
    <div v-if="!hideHeader" class="canvas-header">
      <h2>⚡ ARCHITECTURE CANVAS</h2>
      <div class="btn-group">
        <button
          class="btn btn-mode"
          :class="{ active: isConnectionMode }"
          @click="toggleMode"
        >
          {{ isConnectionMode ? '배치 모드' : '연결 모드' }}
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
        <!-- Delete Button -->
        <button
          class="delete-btn"
          @click.stop="deleteComponent(comp.id)"
          @mousedown.stop
          title="컴포넌트 삭제"
        >
          ✕
        </button>
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
    },
    hideHeader: {
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
    'component-deleted',
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

        const dx = x2 - x1;
        const dy = y2 - y1;
        const length = Math.sqrt(dx * dx + dy * dy);
        const angle = Math.atan2(dy, dx) * (180 / Math.PI);

        // 화살표를 컴포넌트 경계 바깥에 위치시키기 위해 오프셋 계산
        const arrowOffset = 55; // 컴포넌트 반폭
        const ratio = (length - arrowOffset) / length;
        const arrowX = x1 + dx * ratio;
        const arrowY = y1 + dy * ratio;

        return {
          lineStyle: {
            width: `${length - arrowOffset}px`,
            left: `${x1}px`,
            top: `${y1}px`,
            transform: `rotate(${angle}deg)`
          },
          arrowStyle: {
            left: `${arrowX}px`,
            top: `${arrowY - 10}px`,
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
    },
    deleteComponent(compId) {
      this.$emit('component-deleted', compId);
      if (this.selectedComponentId === compId) {
        this.selectedComponentId = null;
      }
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap');

.canvas {
  --accent-neon: #4fc3f7;
  --accent-cyan: #00f3ff;
  --accent-pink: #ec4899;
  --terminal-font: 'Fira Code', monospace;

  background: transparent;
  display: flex;
  flex-direction: column;
  flex: 1;
  position: relative;
}

.canvas-header {
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(79, 195, 247, 0.2);
  background: rgba(5, 7, 10, 0.8);
  backdrop-filter: blur(10px);
}

.canvas-header h2 {
  font-family: var(--terminal-font);
  font-size: 0.9rem;
  color: var(--accent-neon);
  margin: 0;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(79, 195, 247, 0.5);
}

.btn-group {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: 1px solid rgba(79, 195, 247, 0.3);
  background: rgba(79, 195, 247, 0.1);
  font-family: var(--terminal-font);
  font-size: 0.75rem;
  color: var(--accent-neon);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-mode {
  background: rgba(79, 195, 247, 0.1);
  color: var(--accent-neon);
  border: 1px solid rgba(79, 195, 247, 0.3);
}

.btn-mode.active {
  background: var(--accent-neon);
  color: #000;
  box-shadow: 0 0 15px rgba(79, 195, 247, 0.4);
}

.btn-clear {
  background: rgba(236, 72, 153, 0.1);
  color: var(--accent-pink);
  border: 1px solid rgba(236, 72, 153, 0.3);
}

.btn-clear:hover {
  background: rgba(236, 72, 153, 0.2);
  box-shadow: 0 0 15px rgba(236, 72, 153, 0.3);
}

.canvas-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  background-size: 25px 25px;
}

.dropped-component {
  position: absolute;
  padding: 10px 16px;
  cursor: move;
  font-size: 0.8rem;
  font-weight: 500;
  font-family: var(--terminal-font);
  min-width: 130px;
  text-align: center;
  transition: box-shadow 0.2s ease, transform 0.1s ease;
  border: 1px solid rgba(79, 195, 247, 0.4);
  user-select: none;
}

.dropped-component:hover {
  transform: scale(1.02);
  box-shadow: 0 0 20px rgba(79, 195, 247, 0.3);
}

.dropped-component:hover .delete-btn {
  opacity: 1;
}

.delete-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  background: var(--accent-pink);
  border: none;
  color: #fff;
  font-size: 10px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.2s ease;
  z-index: 10;
}

.delete-btn:hover {
  background: #f43f8e;
  transform: scale(1.1);
  box-shadow: 0 0 10px rgba(236, 72, 153, 0.5);
}

.dropped-component.selected {
  border-color: var(--accent-neon);
  box-shadow: 0 0 25px rgba(79, 195, 247, 0.6);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 25px rgba(79, 195, 247, 0.6); }
  50% { box-shadow: 0 0 40px rgba(79, 195, 247, 0.9); }
}

/* Component type styles - Terminal 2077 Theme */
.dropped-component.user { background: rgba(236, 72, 153, 0.9); color: #fff; border-color: #ec4899; }
.dropped-component.loadbalancer { background: rgba(0, 243, 255, 0.9); color: #000; border-color: #00f3ff; }
.dropped-component.gateway { background: rgba(100, 181, 246, 0.9); color: #000; border-color: #64b5f6; }
.dropped-component.server { background: rgba(171, 71, 188, 0.9); color: #fff; border-color: #ab47bc; }
.dropped-component.rdbms { background: rgba(79, 195, 247, 0.9); color: #000; border-color: #4fc3f7; }
.dropped-component.nosql { background: rgba(77, 182, 172, 0.9); color: #000; border-color: #4db6ac; }
.dropped-component.cache { background: rgba(255, 193, 7, 0.9); color: #000; border-color: #ffc107; }
.dropped-component.search { background: rgba(124, 77, 255, 0.9); color: #fff; border-color: #7c4dff; }
.dropped-component.storage { background: rgba(255, 112, 67, 0.9); color: #fff; border-color: #ff7043; }
.dropped-component.broker { background: rgba(255, 138, 101, 0.9); color: #000; border-color: #ff8a65; }
.dropped-component.eventbus { background: rgba(186, 104, 200, 0.9); color: #fff; border-color: #ba68c8; }
.dropped-component.monitoring { background: rgba(102, 187, 106, 0.9); color: #000; border-color: #66bb6a; }
.dropped-component.logging { background: rgba(120, 144, 156, 0.9); color: #fff; border-color: #78909c; }
.dropped-component.cicd { background: rgba(66, 165, 245, 0.9); color: #000; border-color: #42a5f5; }

.component-name-input {
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid var(--accent-neon);
  color: var(--accent-neon);
  padding: 4px 8px;
  font-family: var(--terminal-font);
  font-size: 0.8rem;
  width: 100%;
  text-align: center;
}

/* Connection lines - 네온 그린 스타일 */
.connection-line {
  position: absolute;
  height: 3px;
  background: var(--accent-neon);
  transform-origin: left center;
  pointer-events: none;
  box-shadow: 0 0 10px rgba(79, 195, 247, 0.6);
  z-index: 5;
}

.connection-arrow {
  position: absolute;
  width: 0;
  height: 0;
  border-left: 14px solid var(--accent-neon);
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  transform-origin: left center;
  pointer-events: none;
  filter: drop-shadow(0 0 6px rgba(79, 195, 247, 0.8));
  z-index: 6;
}
</style>
