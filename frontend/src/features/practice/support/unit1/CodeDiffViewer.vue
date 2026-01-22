<template>
  <div class="diff-viewer-container h-[500px] bg-[#1e1e1e] rounded-2xl overflow-hidden border border-slate-700 shadow-2xl animate-in fade-in zoom-in-95 duration-500">
    <!-- 
      [수정일: 2026-01-23]
      [수정내용: Monaco Diff Editor를 활용한 코드 비교 컴포넌트 구현]
    -->
    <div class="diff-header px-6 py-3 bg-[#252526] border-b border-slate-700 flex justify-between items-center font-mono text-[10px] tracking-widest text-slate-500">
      <div class="flex items-center gap-10">
        <span class="flex items-center gap-2"><div class="w-1.5 h-1.5 bg-rose-500 rounded-full"></div> ORIGINAL_LOGIC</span>
        <span class="flex items-center gap-2"><div class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></div> YOUR_IMPLEMENTATION</span>
      </div>
      <button @click="$emit('close')" class="hover:text-white transition-colors">CLOSE_DIFF [X]</button>
    </div>

    <div class="flex-1 h-full">
      <vue-monaco-diff-editor
        theme="vs-dark"
        :language="language"
        :original="originalCode"
        :modified="modifiedCode"
        :options="diffOptions"
        class="h-full"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  originalCode: { type: String, required: true },
  modifiedCode: { type: String, required: true },
  language: { type: String, default: 'python' }
});

defineEmits(['close']);

const diffOptions = {
  automaticLayout: true,
  readOnly: true,
  renderSideBySide: true,
  fontSize: 13,
  fontFamily: "'JetBrains Mono', monospace",
  minimap: { enabled: false },
  originalEditable: false,
  scrollBeyondLastLine: false,
  theme: 'vs-dark'
};
</script>

<style scoped>
.diff-viewer-container {
  display: flex;
  flex-direction: column;
}
</style>
