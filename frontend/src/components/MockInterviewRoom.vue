<template>
  <div class="mock-interview-room min-h-screen bg-gray-900 text-white flex flex-col font-sans">
    <!-- Header -->
    <header class="p-4 bg-gray-800 border-b border-gray-700 flex justify-between items-center shadow-md">
      <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500">
        AI-GYM 모의 면접 (PoC)
      </h1>
      <button 
        @click="startMockInterview" 
        :disabled="isInterviewActive"
        class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-semibold rounded transition"
      >
        면접 시작
      </button>
    </header>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col p-4 max-w-4xl w-full mx-auto">
      
      <!-- Video / Avatar area placeholder -->
      <div class="mb-4 bg-gray-800 rounded-lg h-48 flex items-center justify-center border border-gray-700 shadow-inner relative overflow-hidden">
        <div class="text-center">
          <div class="w-20 h-20 bg-gray-700 rounded-full mx-auto mb-2 flex items-center justify-center">
            <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
          </div>
          <p class="text-gray-400 text-sm">대기 중...</p>
        </div>
      </div>

      <!-- Chat Interface -->
      <div class="flex-1 overflow-y-auto space-y-4 mb-4 pr-2 custom-scrollbar">
        <!-- Render Finished Messages -->
        <div 
          v-for="(msg, index) in interviewStore.messages" 
          :key="index"
          :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
        >
          <div 
            :class="[
              'p-3 max-w-2xl rounded-lg text-sm leading-relaxed shadow', 
              msg.role === 'user' ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-gray-800 text-gray-200 border border-gray-700 rounded-bl-none'
            ]"
          >
            {{ msg.content }}
          </div>
        </div>

        <!-- Render Currently Typing Message -->
        <div v-if="interviewStore.isTyping" class="flex justify-start">
          <div class="p-3 max-w-2xl bg-gray-800 text-gray-200 border border-gray-700 rounded-lg rounded-bl-none text-sm leading-relaxed shadow">
            <span>{{ interviewStore.currentTypingMessage }}</span>
            <span class="inline-block animate-pulse font-bold ml-1">...</span>
          </div>
        </div>
      </div>

      <!-- Chat input (Mock) -->
      <div class="mt-auto flex gap-2">
        <input 
          type="text" 
          disabled
          placeholder="PoC 버전에서는 AI 면접관의 발언만 시연됩니다." 
          class="flex-1 bg-gray-800 border border-gray-700 rounded p-3 text-sm text-gray-400 cursor-not-allowed focus:outline-none"
        />
        <button disabled class="px-6 py-3 bg-gray-700 text-gray-400 font-semibold rounded cursor-not-allowed transition">
          전송
        </button>
      </div>

    </main>
  </div>
</template>

<script setup>
/**
 * 작성일: 2026-02-21
 * 작성자: Antigravity (프론트엔드 에이전트)
 * 작성내용:
 * - 모의 면접 UI Mockup 페이지 컴포넌트 구현
 * - 브라우저 내장 API인 `EventSource`를 생성하여 백엔드의 `/api/v1/mock-interview/stream` (SSE API)에 직접 연결을 맺음.
 * - 수신된 이벤트 데이터를 파싱하여 Pinia 스토어(interviewStore)를 업데이트하고 실시간 글자 타이핑 애니메이션(UX)과 '...' 깜빡임 효과를 제공함.
 * - "done" 상태 수신 시 연결을 안전하게 종료하도록 생명주기 OnUnmounted 훅 방어 처리 등 포함.
 */
import { ref, onUnmounted } from 'vue';
import { useInterviewStore } from '../stores/interview';

const interviewStore = useInterviewStore();
const isInterviewActive = ref(false);
let eventSource = null;

const startMockInterview = () => {
  if (isInterviewActive.value) return;
  
  // 상태 초기화
  interviewStore.clearMessages();
  isInterviewActive.value = true;
  interviewStore.setTypingStatus(true);
  
  // SSE 연결
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  eventSource = new EventSource(`${apiUrl}/api/v1/mock-interview/stream`);
  // Note: EventSource는 기본적으로 GET 및 credentials 설정이 제한적이나, PoC 용도로는 로컬/Same Origin 등으로 충분히 우회 또는 설정 가능
  // 필요 시 withCredentials 옵션 추가(백엔드 CORS 확인 필요): new EventSource(..., { withCredentials: true })

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      
      if (data.status === 'typing') {
        interviewStore.appendChunk(data.chunk);
      } else if (data.status === 'done') {
        interviewStore.finalizeMessage();
        closeConnection();
      }
    } catch (e) {
      console.error('SSE JSON 파싱 오류', e);
    }
  };

  eventSource.onerror = (error) => {
    console.error('SSE 스트림 에러 발생', error);
    interviewStore.finalizeMessage(); // 에러 발생 시 진행 중이던 메시지 확정
    closeConnection();
  };
};

const closeConnection = () => {
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  isInterviewActive.value = false;
  interviewStore.setTypingStatus(false);
};

onUnmounted(() => {
  closeConnection();
});
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #1f2937; /* gray-800 */
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #374151; /* gray-700 */
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #4b5563; /* gray-600 */
}
</style>
