<template>
  <transition name="fade">
    <div v-if="ui.isMockInterviewModalOpen" class="modal-overlay z-50 fixed inset-0 flex items-center justify-center bg-black/80 backdrop-blur-md" @click.self="handleCloseModal">
      
      <div class="mock-interview-modal bg-[#161618] text-gray-100 flex flex-col lg:flex-row rounded-2xl shadow-2xl overflow-hidden w-full max-w-6xl h-[90vh] lg:h-[85vh] m-4 border border-gray-700/50">
        
        <!-- Left Panel: Video Conference Area -->
        <div class="flex-1 bg-[#0a0a0a] relative flex flex-col items-center justify-center overflow-hidden shrink-0">
          
          <!-- Top Left Indicators -->
          <div class="absolute top-6 left-6 flex flex-col gap-3 z-40 w-full md:w-auto pr-6 sm:pr-0">
            <div class="flex items-center gap-3">
              <div class="flex items-center gap-2 bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 shadow-lg">
                 <span class="w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(239,68,68,0.8)]" :class="isInterviewActive ? 'bg-red-500 animate-pulse' : 'bg-gray-500'"></span>
                 <span class="text-xs font-bold tracking-wider" :class="isInterviewActive ? 'text-red-100' : 'text-gray-400'">REC</span>
              </div>
              <div class="bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 text-xs font-mono font-medium text-gray-300 hidden sm:block">
                 Live Video Interview Session
              </div>
              
              <!-- [수정일: 2026-02-22] Job Planner 데이터 요약 보기 버튼 스타일 상향 -->
              <button 
                v-if="interviewStore.jobPlannerData"
                @click="showJobPlannerSummary = !showJobPlannerSummary"
                class="group relative flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-bold text-indigo-100 shadow-lg transition-all ml-auto sm:ml-0 overflow-hidden"
              >
                <!-- Glowing Background -->
                <div class="absolute inset-0 bg-gradient-to-r from-indigo-600/60 to-purple-600/60 backdrop-blur-md group-hover:from-indigo-500/80 group-hover:to-purple-500/80 transition-colors"></div>
                <!-- Glass Border -->
                <div class="absolute inset-0 rounded-full border border-white/20 group-hover:border-white/40 transition-colors"></div>
                <!-- Content -->
                <svg class="w-4 h-4 text-indigo-200 relative z-10 drop-shadow-md group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                <span class="relative z-10 tracking-wide drop-shadow-md">지원 정보 보기</span>
              </button>
            </div>
            
            <!-- Job Planner Summary Popup Panel -->
            <transition name="job-panel">
              <div v-if="showJobPlannerSummary && interviewStore.jobPlannerData" class="bg-gray-900/90 backdrop-blur-xl border border-indigo-500/30 rounded-xl p-4 shadow-2xl w-full sm:w-80">
                <div class="flex justify-between items-center mb-3 border-b border-gray-700/50 pb-2">
                   <h4 class="text-sm font-bold text-indigo-300 flex items-center gap-1.5">
                     <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                     제출된 Job Planner 요약
                   </h4>
                   <button @click="showJobPlannerSummary = false" class="text-gray-400 hover:text-white">
                     <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path></svg>
                   </button>
                </div>
                <!-- Data Display -->
                <div class="space-y-3 text-[13px]">
                   <div>
                     <span class="block text-gray-500 font-bold mb-0.5 uppercase tracking-wide text-[10px]">목표 기업 (Target Company)</span>
                     <span class="text-gray-100 font-medium break-words">{{ interviewStore.jobPlannerData?.jobData?.company_name || '미설정' }}</span>
                   </div>
                   <div>
                     <span class="block text-gray-500 font-bold mb-0.5 uppercase tracking-wide text-[10px]">지원 직무 (Position)</span>
                     <span class="text-gray-100 font-medium break-words">{{ interviewStore.jobPlannerData?.jobData?.position || '미설정' }}</span>
                   </div>
                   <div>
                     <span class="block text-gray-500 font-bold mb-1 uppercase tracking-wide text-[10px]">요구 기술 (Required Skills)</span>
                     <div class="flex flex-wrap gap-1.5">
                       <span 
                         v-for="skill in (interviewStore.jobPlannerData?.jobData?.required_skills || []).slice(0, 5)" 
                         :key="skill"
                         class="px-2 py-0.5 bg-gray-800 border border-gray-600 rounded text-xs text-indigo-200"
                       >
                         {{ skill }}
                       </span>
                       <span v-if="(interviewStore.jobPlannerData?.jobData?.required_skills?.length || 0) > 5" class="px-2 py-0.5 text-xs text-gray-500">...</span>
                     </div>
                   </div>
                </div>
              </div>
            </transition>
          </div>

          <!-- Main Camera Feed (Interviewer) -->
          <div class="relative flex flex-col items-center justify-center w-full h-full pb-20">
            <!-- Glow effect behind avatar when speaking/typing -->
            <div :class="['absolute rounded-full blur-[80px] w-64 h-64 transition-opacity duration-1000', interviewStore.isTyping ? 'bg-indigo-500/40 opacity-100' : 'opacity-0']"></div>
            
            <div :class="[
              'relative w-48 h-48 sm:w-64 sm:h-64 rounded-full overflow-hidden shadow-2xl transition-all duration-700 object-cover bg-gray-800 z-10',
              interviewStore.isTyping ? 'ring-4 ring-indigo-500 ring-offset-8 ring-offset-[#0a0a0a] scale-105' : 'border border-gray-700 opacity-90'
            ]">
              <img src="../assets/images/interviewer_duck.png" alt="Duck Interviewer" class="w-full h-full object-cover" />
            </div>
            
            <!-- Avatar Name Tag -->
            <div class="mt-8 text-center z-10">
              <h2 class="text-2xl font-black tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-gray-100 to-gray-400">도덕 (Coduck)</h2>
              <p class="text-sm text-indigo-400 mt-1.5 font-semibold tracking-wide uppercase">Senior AI-ARCADE Interviewer</p>
            </div>
          </div>

          <!-- Interviwer Name Tag (Bottom Left of Video) -->
          <div class="absolute bottom-24 left-6 bg-black/50 backdrop-blur-md px-4 py-2.5 rounded-xl border border-white/10 hidden md:block z-10 shadow-lg">
             <span class="text-sm font-semibold text-white tracking-wide">도덕 (Interviewer)</span>
          </div>

          <!-- PIP (User Camera Placeholder) -->
          <div class="absolute top-6 right-6 w-36 h-48 bg-gray-900 rounded-xl border border-gray-700 shadow-2xl overflow-hidden flex flex-col items-center justify-center z-30 group cursor-default hidden sm:flex">
             <div class="w-full h-full flex items-center justify-center bg-gray-800 group-hover:bg-gray-700 transition-colors">
               <svg class="w-16 h-16 text-gray-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path></svg>
             </div>
             <div class="absolute bottom-2 left-2 bg-black/70 px-2 py-1 rounded text-[11px] font-bold text-white tracking-wide">지원자 (Me)</div>
             <!-- Camera Off Indicator -->
             <div class="absolute top-2 right-2 bg-red-500/90 rounded-full p-1 shadow">
                <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3l18 18"></path></svg>
             </div>
          </div>

          <!-- Live Subtitle Display (Like Teams/Zoom Captions) -->
          <transition name="fade">
            <div v-if="interviewStore.isTyping" class="absolute bottom-40 left-0 right-0 flex justify-center px-10 z-20 pointer-events-none">
               <div class="bg-black/70 backdrop-blur-xl border border-white/10 px-6 py-4 rounded-2xl max-w-3xl w-full text-center shadow-2xl">
                  <p class="text-[16px] leading-[1.6] font-medium text-white drop-shadow-md">
                     "{{ interviewStore.currentTypingMessage }}"
                     <span class="inline-block animate-pulse ml-1 text-indigo-400 font-bold">...</span>
                  </p>
               </div>
            </div>
            <div v-else-if="interviewStore.messages.length > 0 && interviewStore.messages[interviewStore.messages.length-1].role === 'interviewer'" class="absolute bottom-40 left-0 right-0 flex justify-center px-10 z-20 pointer-events-none opacity-80 transition-opacity hover:opacity-100">
               <div class="bg-black/50 backdrop-blur-md border border-white/5 px-6 py-4 rounded-2xl max-w-3xl w-full text-center">
                  <p class="text-[15px] leading-[1.6] font-medium text-gray-300 drop-shadow-md line-clamp-3">
                     "{{ interviewStore.messages[interviewStore.messages.length-1].content }}"
                  </p>
               </div>
            </div>
          </transition>

          <!-- Bottom Control Bar -->
          <div class="absolute bottom-6 left-0 right-0 flex justify-center gap-4 z-20">
             <!-- Start Interview Button (Replaces typical 'Start Video/Mic' call to action) -->
             <button @click="startMockInterview" :disabled="isInterviewActive" class="group flex items-center justify-center px-6 h-14 rounded-full bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-800 disabled:opacity-50 transition-all shadow-lg border border-white/10 font-bold tracking-wide">
                <svg v-if="!isInterviewActive" class="w-5 h-5 mr-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <svg v-else class="w-5 h-5 mr-2 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>
                <span :class="isInterviewActive ? 'text-emerald-100' : 'text-white'">{{ isInterviewActive ? '면접 진행 중' : '모의 면접 시작' }}</span>
             </button>
             
             <!-- Mock Mic / Video buttons -->
             <div class="flex gap-3 hidden sm:flex">
               <button disabled class="w-14 h-14 rounded-full bg-gray-800/80 backdrop-blur-md border border-white/10 flex items-center justify-center opacity-70 cursor-not-allowed hidden md:flex">
                  <!-- Mic Off -->
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3l18 18"></path></svg>
               </button>
               <button disabled class="w-14 h-14 rounded-full bg-gray-800/80 backdrop-blur-md border border-white/10 flex items-center justify-center opacity-70 cursor-not-allowed">
                  <!-- Video Off -->
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3l18 18"></path></svg>
               </button>
             </div>

             <!-- Leave / Close Button -->
             <button @click="handleCloseModal" class="w-14 h-14 rounded-full bg-red-600 hover:bg-red-500 shadow-[0_0_15px_rgba(239,68,68,0.5)] flex items-center justify-center transition-transform hover:scale-105 border border-red-500 group">
                <svg class="w-6 h-6 text-white group-hover:rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M5 3a2 2 0 00-2 2v1c0 8.284 6.716 15 15 15h1a2 2 0 002-2v-3.28a1 1 0 00-.684-.948l-4.493-1.498a1 1 0 00-1.21.502l-1.13 2.257a11.042 11.042 0 01-5.516-5.517l2.257-1.128a1 1 0 00.502-1.21L9.228 3.683A1 1 0 008.279 3H5z"></path></svg>
             </button>
          </div>
        </div>

        <!-- Right Panel: Interview Transcript & Input -->
        <div class="w-full lg:w-[420px] bg-[#1a1a1c] border-t lg:border-t-0 lg:border-l border-gray-800 flex flex-col shrink-0 flex-1 lg:flex-none">
           <!-- Panel Header -->
           <div class="h-[72px] flex flex-col justify-center px-6 border-b border-gray-800/80 bg-[#161618] shrink-0 shadow-sm relative z-10">
              <h3 class="font-bold text-gray-100 tracking-wide flex items-center gap-2 text-[15px]">
                 <svg class="w-4.5 h-4.5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                 Interview Transcript
              </h3>
              <p class="text-[11px] text-gray-500 font-medium tracking-wide mt-0.5 ml-6">실시간 질의응답 텍스트 기록</p>
           </div>

           <!-- Q&A Log -->
           <div class="flex-1 overflow-y-auto px-5 py-6 space-y-7 custom-scrollbar bg-[#1a1a1c]">
              <!-- Setup state msg -->
              <div v-if="!isInterviewActive" class="flex flex-col items-center justify-center h-full opacity-60">
                 <svg class="w-12 h-12 text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                 <p class="text-center text-[13px] text-gray-400 font-medium">면접을 시작하면<br/>대화 기록이 이곳에 표시됩니다.</p>
              </div>

              <!-- Iterating messages -->
              <div 
                 v-for="(msg, index) in interviewStore.messages" 
                 :key="index"
                 class="flex flex-col space-y-2 group"
              >
                 <!-- Name and Avatar -->
                 <div class="flex items-center gap-2.5">
                    <span v-if="msg.role === 'interviewer'" class="w-7 h-7 rounded bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center text-[10px] font-black text-white shadow-md border border-indigo-400/50">AI</span>
                    <span v-else class="w-7 h-7 rounded bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center text-[10px] font-black text-white shadow-md border border-gray-500/50">ME</span>
                    <span class="text-[13px] font-bold tracking-wide" :class="msg.role === 'interviewer' ? 'text-indigo-300' : 'text-gray-300'">
                      {{ msg.role === 'interviewer' ? '도덕 (Interviewer)' : '지원자 (Candidate)' }}
                    </span>
                 </div>
                 <!-- Content Block -->
                 <div :class="[
                   'text-[14px] leading-relaxed p-4 rounded-xl border',
                   msg.role === 'interviewer' 
                    ? 'bg-indigo-950/20 text-gray-200 border-indigo-900/50' 
                    : 'bg-gray-800/40 text-gray-300 border-gray-700/50'
                 ]">
                   <span class="whitespace-pre-wrap">{{ msg.content }}</span>
                 </div>
              </div>
           </div>

           <!-- Input Area -->
           <div class="p-5 bg-[#161618] border-t border-gray-800 shadow-[0_-10px_30px_rgba(0,0,0,0.5)] z-20 shrink-0">
              <label class="block text-[11px] font-bold text-gray-400 mb-2 uppercase tracking-wide ml-1">Your Response</label>
              <div class="relative bg-[#0d0d0f] rounded-xl border border-gray-700 focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 transition-all shadow-inner overflow-hidden flex flex-col">
                 <textarea 
                   v-model="userInput"
                   @keydown.enter.prevent="sendMessage"
                   :disabled="!isInterviewActive || interviewStore.isTyping"
                   :placeholder="isInterviewActive ? (interviewStore.isTyping ? '면접관의 질문을 듣는 중...' : '답변을 타이핑하세요...') : '대기 중...'"
                   class="w-full bg-transparent p-4 text-[14px] leading-relaxed text-gray-100 placeholder-gray-600 resize-none h-[110px] focus:outline-none custom-scrollbar"
                 ></textarea>
                 
                 <!-- Bottom actions of input -->
                 <div class="bg-[#121214] px-3 py-2 flex justify-between items-center border-t border-gray-800">
                   <div class="flex items-center text-[11px] text-gray-500 font-medium ml-1 gap-1">
                     <kbd class="bg-gray-800 px-1.5 py-0.5 rounded border border-gray-700 text-gray-400">Enter</kbd> <span>to submit</span>
                   </div>
                   <button 
                     @click="sendMessage"
                     :disabled="!isInterviewActive || interviewStore.isTyping || !userInput.trim()"
                     class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-[12px] font-bold tracking-wide rounded border border-indigo-500 transition-all shadow-md disabled:opacity-50 disabled:bg-gray-800 disabled:text-gray-500 disabled:shadow-none disabled:border-gray-700"
                   >
                     답변 제출
                   </button>
                 </div>
              </div>
           </div>
        </div>

      </div>
    </div>
  </transition>
</template>

<script setup>
/**
 * 작성일: 2026-02-21
 * 작성자: 개발자
 * 작성내용:
 * - 모의 면접 UI Mockup 페이지 컴포넌트 구현
 * - 브라우저 내장 API인 `EventSource`를 생성하여 백엔드의 `/api/v1/mock-interview/stream` (SSE API)에 직접 연결을 맺음.
 * - 수신된 이벤트 데이터를 파싱하여 Pinia 스토어(interviewStore)를 업데이트하고 실시간 글자 타이핑 애니메이션(UX)과 '...' 깜빡임 효과를 제공함.
 * - "done" 상태 수신 시 연결을 안전하게 종료하도록 생명주기 OnUnmounted 훅 방어 처리 등 포함.
 *
 * 수정일: 2026-02-21
 * 수정내용: 기존 SVG 아바타 대신 생성한 '나노바나나를 활용한 픽사 감성의 오리 면접관' 이미지를 화면의 면접관 영역에 삽입 및 상태별 메세지 갱신. Antigravity 주석 삭제.
 * 
 * 추가수정 (2026-02-21): 모의 면접 화면을 모달 모드로 변경하고, 모달 닫기 로직 및 타이핑 방어 로직 구현.
 */
import { ref, computed, onUnmounted, nextTick } from 'vue';
import { useInterviewStore } from '../stores/interview';
import { useUiStore } from '../stores/ui';

const interviewStore = useInterviewStore();
const ui = useUiStore();
const isInterviewActive = ref(false);
const userInput = ref('');
const showLog = ref(false); // [수정일: 2026-02-22] 로그 필터 상태
const showJobPlannerSummary = ref(false); // [수정일: 2026-02-22] Job Planner 정보 토글 상태
let eventSource = null;

const toggleLog = () => {
  showLog.value = !showLog.value;
};

// 최신 대화만 보여주는 로직 (마지막 2개 메시지 혹은 타이핑 내용)
const latestMessages = computed(() => {
  const msgs = interviewStore.messages;
  if (msgs.length === 0) return [];
  // 마지막 2개의 메세지만 (사용자 응답 -> 면접관 질문 형태)을 가져옵니다.
  return msgs.slice(-2);
});

const startMockInterview = () => {
  if (isInterviewActive.value) return;

  interviewStore.clearMessages();
  isInterviewActive.value = true;
  interviewStore.setTypingStatus(true);

  // [수정일: 2026-02-22] Job Planner 데이터가 존재하면 SSE 스트림(POST) 호출 시 전송
  let bodyData = null;
  if (interviewStore.jobPlannerData) {
    bodyData = { job_planner: interviewStore.jobPlannerData };
  }

  connectSSEFetch('/api/v1/mock-interview/stream', bodyData);
};

const sendMessage = () => {
  const msg = userInput.value.trim();
  if (!msg || !isInterviewActive.value || interviewStore.isTyping) return;

  // 1. Add user message to store
  interviewStore.addUserMessage(msg);

  // 2. Clear input & show typing indicator for AI
  userInput.value = '';
  interviewStore.setTypingStatus(true);

  // 3. Request AI reply via new SSE endpoint (POST with fetch)
  const history = interviewStore.messages.map(m => ({
    role: m.role === 'interviewer' ? 'assistant' : 'user',
    content: m.content
  }));

  // [수정일: 2026-02-22] 꼬리 질문 답변 시에도 Job Planner 정보(Context) 유지
  const bodyData = { history };
  if (interviewStore.jobPlannerData) {
    bodyData.job_planner = interviewStore.jobPlannerData;
  }

  connectSSEFetch('/api/v1/mock-interview/reply', bodyData);
};

// [수정일: 2026-02-22] EventSource 대신 Fetch 기반의 스트림 리더 구현 (POST 지원 유지 및 이전 대화 내역 전송)
const connectSSEFetch = async (endpoint, bodyData = null) => {
  closeConnection(false);

  // CORS(fetch failed) 에러 방지:
  // VITE_API_URL로 절대 경로(http://localhost:8000)를 강제하면 credentials: 'include' 옵션 시
  // 브라우저가 strict CORS 위반으로 막아버립니다. vite proxy('/api')를 활용하도록 상대 경로를 씁니다.
  const url = endpoint;

  try {
    const response = await fetch(url, {
      method: bodyData ? 'POST' : 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // 세션 쿠키 포함하여 사용자를 식별 (DB 연동 위함)
      body: bodyData ? JSON.stringify(bodyData) : null
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      if (!isInterviewActive.value) {
        reader.cancel();
        break;
      }

      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop(); // 남아있는 불완전한 덩어리 유지

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6);
          if (!dataStr.trim()) continue;

          try {
            const data = JSON.parse(dataStr);
            if (data.status === 'typing') {
              interviewStore.appendChunk(data.chunk);
            } else if (data.status === 'done') {
              interviewStore.finalizeMessage();
              closeConnection(false);

              nextTick(() => {
                const container = document.querySelector('.custom-scrollbar');
                if (container) container.scrollTop = container.scrollHeight;
              });
            }
          } catch (e) {
            console.error('SSE JSON 파싱 오류', e, dataStr);
          }
        }
      }
    }
  } catch (error) {
    console.error('SSE 스트림 에러 발생', error);
    interviewStore.finalizeMessage();
    closeConnection(false);
  }
};

const connectSSE = (endpoint) => {
  connectSSEFetch(endpoint);
};

const closeConnection = (deactivate = true) => {
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  if (deactivate) {
    isInterviewActive.value = false;
    interviewStore.setTypingStatus(false);
  }
};

const handleCloseModal = () => {
  if (isInterviewActive.value && interviewStore.isTyping) {
    if (!confirm('AI 면접관이 답변을 고민 중입니다. 현재 진행 상황을 종료하시겠습니까?')) return;
  } else if (isInterviewActive.value && interviewStore.messages.length > 0) {
    if (!confirm('현재 진행 중인 모의 면접을 종료 시 대화 기록이 유실될 수 있습니다. 닫으시겠습니까?')) return;
  }

  closeConnection();
  interviewStore.clearMessages();
  ui.isMockInterviewModalOpen = false;
};

onUnmounted(() => {
  closeConnection();
});
</script>

<style scoped>
/* Fade Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Job Panel Slide Transition */
.job-panel-enter-active,
.job-panel-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: top left;
}
.job-panel-enter-from,
.job-panel-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* Custom Scrollbar for Chat */
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
