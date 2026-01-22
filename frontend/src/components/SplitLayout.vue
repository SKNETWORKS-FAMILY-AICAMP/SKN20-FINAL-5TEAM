<template>
  <!-- 
    [수정일: 2026-01-23]
    [수정내용: 문제 풀이용 좌우 분할 레이아웃 컴포넌트 구현]
    
    이 컴포넌트는 화면을 가로로 두 영역으로 나누어 배치합니다.
    - 왼쪽(left slot): 지문, 문제 설명, 제약 사항 등 정적인 정보 표시
    - 오른쪽(right slot): 코드 에디터, 드래그 앤 드롭 퍼즐 등 동적인 작업 공간 표시
  -->
  <div class="split-layout flex h-screen overflow-hidden bg-slate-900 text-slate-100">
    <!-- 왼쪽 패널: 문제 설명 -->
    <div class="left-panel border-r border-slate-700 overflow-y-auto" :style="{ width: leftPercent + '%' }">
      <div class="p-6">
        <slot name="left"></slot>
      </div>
    </div>

    <!-- 구분선 (조절 가능 피드백 반영용 공간) -->
    <div class="resizer w-1 bg-slate-700 cursor-col-resize hover:bg-neon-blue transition-colors"></div>

    <!-- 오른쪽 패널: 작업 영역 (코드 에디터, 퍼즐 등) -->
    <div class="right-panel flex-1 overflow-y-auto bg-slate-800">
      <div class="h-full">
        <slot name="right"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  initialLeftWidth: {
    type: Number,
    default: 45
  }
});

const leftPercent = ref(props.initialLeftWidth);
</script>

<style scoped>
.left-panel {
  min-width: 300px;
}
.right-panel {
  min-width: 400px;
}
.bg-neon-blue {
  background-color: #00f3ff;
  box-shadow: 0 0 10px #00f3ff;
}
</style>
