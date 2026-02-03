import { ref, computed } from 'vue';
import { generateMermaidCode } from '../utils/architectureUtils';

export function useCanvasState() {
  const isConnectionMode = ref(false);
  const droppedComponents = ref([]);
  const connections = ref([]);
  const componentCounter = ref(0);

  const mermaidCode = computed(() => {
    return generateMermaidCode(droppedComponents.value, connections.value);
  });

  function toggleMode(showToastFn) {
    isConnectionMode.value = !isConnectionMode.value;

    if (showToastFn) {
      if (isConnectionMode.value) {
        showToastFn(
          '연결 모드! 컴포넌트를 클릭해서 연결해. 두 개를 순서대로 클릭하면 화살표가 생겨. 꽥!',
          'connect'
        );
      } else {
        showToastFn(
          '배치 모드! 오른쪽 팔레트에서 컴포넌트를 드래그해서 캔버스에 놓아. 꽥!',
          'place'
        );
      }
    }
  }

  function clearCanvas() {
    droppedComponents.value = [];
    connections.value = [];
    componentCounter.value = 0;
  }

  function onComponentDropped({ type, text, x, y }) {
    droppedComponents.value.push({
      id: `comp_${componentCounter.value++}`,
      type,
      text,
      x,
      y
    });
  }

  function onComponentMoved({ id, x, y }) {
    const comp = droppedComponents.value.find(c => c.id === id);
    if (comp) {
      comp.x = x;
      comp.y = y;
    }
  }

  function onComponentRenamed({ id, text }) {
    const comp = droppedComponents.value.find(c => c.id === id);
    if (comp) {
      comp.text = text;
    }
  }

  function onComponentDeleted(compId) {
    droppedComponents.value = droppedComponents.value.filter(c => c.id !== compId);
    connections.value = connections.value.filter(
      conn => conn.from !== compId && conn.to !== compId
    );
  }

  function onConnectionCreated({ from, to, fromType, toType }) {
    const exists = connections.value.some(c =>
      (c.from === from && c.to === to) ||
      (c.from === to && c.to === from)
    );

    if (!exists) {
      connections.value.push({ from, to, fromType, toType });
      return true;
    }
    return false;
  }

  return {
    isConnectionMode,
    droppedComponents,
    connections,
    componentCounter,
    mermaidCode,
    toggleMode,
    clearCanvas,
    onComponentDropped,
    onComponentMoved,
    onComponentRenamed,
    onComponentDeleted,
    onConnectionCreated
  };
}
