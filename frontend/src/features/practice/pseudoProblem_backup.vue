<template>
  <!-- [수정일: 2026-01-31] 전역 모달(z-index 1000)보다 위에 오도록 z-index를 z-[2000]으로 상향 조정 -->
  <div v-if="isOpen" class="fixed inset-0 z-[2000] flex items-center justify-center md:p-4 bg-black/60 backdrop-blur-sm animate-fade-in" @click.self="$emit('close')">
    <div class="bg-[#0a0e17] w-full max-w-[1700px] h-full md:h-[96vh] md:max-h-[1000px] md:rounded-3xl border border-white/10 shadow-2xl overflow-hidden flex flex-col relative animate-scale-in">
      
      <!-- Glow Decor (main 브랜치의 화려한 배경 효과 복구) -->
      <div class="absolute top-0 left-1/4 w-[600px] h-[600px] bg-cyan-500/[0.03] rounded-full blur-[120px] pointer-events-none"></div>
      <div class="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-pink-500/[0.03] rounded-full blur-[120px] pointer-events-none"></div>

      <!-- HUD Header -->
      <header class="h-24 border-b border-white/5 bg-[#07090e] grid grid-cols-3 items-center px-10 relative shrink-0 z-30">
        <!-- Left: Logo & Project Title -->
        <div class="flex items-center gap-6">
          <div class="w-10 h-10 bg-[#117e96] rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(0,243,255,0.3)] border border-cyan-400/20">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 8L11 12L7 16M13 16H17" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="space-y-0.5">
            <div class="flex items-center gap-3">
              <h1 class="font-black text-xl tracking-tight text-white uppercase italic leading-none">PROJECT: RE-BOOT</h1>
              <span class="px-1.5 py-0.5 bg-pink-500/20 border border-pink-500/30 text-[9px] font-bold text-pink-400 rounded">VER 2.1</span>
            </div>
            <div class="text-[10px] font-bold text-cyan-400/40 uppercase tracking-widest">Data Cleaning Protocol</div>
          </div>
        </div>

        <!-- Center: System Status -->
        <div class="flex justify-center items-center gap-8 font-mono">
          <div class="flex items-center gap-3">
            <span class="text-gray-600 text-[10px] uppercase font-bold tracking-widest">UPLINK_STATUS:</span>
            <span class="text-[#4ade80] text-[11px] font-black animate-pulse">ACTIVE</span>
          </div>
          <div class="h-4 w-[1px] bg-white/10"></div>
          <div class="text-[9px] text-gray-500 font-bold uppercase tracking-tighter">{{ currentQuest.category || 'LV_04_SECURITY_BYPASS' }}</div>
          
          <!-- [수정일: 2026-02-01] TTS 음소거 토글 버튼 추가 -->
          <div class="h-4 w-[1px] bg-white/10"></div>
          <button @click="toggleMute" class="p-2 hover:bg-white/5 rounded-lg transition-colors group relative" :title="isMuted ? '음소거 해제' : '음소거'">
            <VolumeX v-if="isMuted" class="w-4 h-4 text-pink-500 animate-pulse" />
            <Volume2 v-else class="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform" />
          </button>
        </div>

        <!-- Right: Close Button -->
        <div class="flex justify-end pr-2">
          <button 
            @click="$emit('close')" 
            class="flex items-center justify-center w-12 h-12 rounded-xl border border-white/10 hover:bg-pink-500/20 hover:border-pink-500/60 transition-all text-gray-500 hover:text-pink-400 group relative"
          >
            <X class="w-7 h-7 group-hover:rotate-180 transition-transform duration-500 relative z-10" />
            <div class="absolute -top-1 -right-1 w-3 h-3 bg-pink-500 rounded-full border-2 border-[#0a0e17] shadow-[0_0_10px_#ec4899] animate-bounce"></div>
          </button>
        </div>
        
        <!-- Decoration Line -->
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-48 h-[2px] bg-cyan-500 shadow-[0_0_15px_#00f3ff]"></div>
      </header>

      <!-- Main Content Area -->
      <main class="flex-1 p-4 md:p-8 lg:p-12 max-w-full mx-auto w-full relative flex flex-col min-h-0 overflow-y-auto custom-scrollbar z-10">
        <!-- [수정일: 2026-02-01] Step 0: Star Wars Synopsis Crawl -->
        <div v-if="currentStep === 0" class="absolute inset-0 z-50 flex flex-col items-center justify-center bg-black overflow-hidden select-none">
          <!-- Starfield Background -->
          <div class="absolute inset-0 star-field"></div>
          
          <!-- Perspective Container -->
          <div class="relative w-full max-w-4xl h-full flex flex-col items-center text-center perspective-container">
            <!-- Prelude Text (Blue Fade) -->
            <div class="prelude-text animate-fade-out" :style="{ animationDelay: '1s' }">
              {{ synopsisText.prelude }}
            </div>

            <!-- Crawling Content -->
            <div class="crawl-container">
              <div class="crawl-content animate-crawl">
                <h1 class="crawl-title">{{ synopsisText.title }}</h1>
                <div class="crawl-body" v-html="synopsisText.content.replace(/\n/g, '<br/>')"></div>
              </div>
            </div>
          </div>

          <!-- Interaction UI -->
          <div class="absolute bottom-12 right-12 z-[100] flex gap-6 items-center">
            <div v-if="isPlayingBGM" class="flex items-center gap-3 px-4 py-2 bg-cyan-500/10 border border-cyan-500/30 rounded-full animate-pulse">
              <Volume2 class="w-4 h-4 text-cyan-400" />
              <span class="text-[10px] font-mono text-cyan-400 font-bold tracking-widest uppercase italic">Audio_Link_Synced</span>
            </div>
            <button @click="skipSynopsis" class="group relative px-10 py-4 bg-white/5 hover:bg-white/10 text-white border border-white/20 transition-all active:scale-95 hud-button-clip overflow-hidden">
                <span class="relative z-10 font-black text-xs tracking-[0.3em] uppercase italic">Initialize_Protocol_X</span>
                <div class="absolute inset-x-0 bottom-0 h-[2px] bg-cyan-500 shadow-[0_0_10px_#00f3ff] scale-x-0 group-hover:scale-x-100 transition-transform origin-center"></div>
            </button>
          </div>
        </div>

        <!-- Progress Bar -->
        <div v-if="currentStep >= 1 && currentStep <= 4" class="max-w-4xl mx-auto w-full mb-16 px-6 shrink-0">
          <div class="flex justify-between mb-4 px-1">
            <span v-for="i in 4" :key="'label-'+i" 
                  class="text-[11px] font-black tracking-[0.3em] transition-colors duration-500 italic"
                  :class="i <= currentStep ? 'text-cyan-400' : 'text-gray-600'">
              PHASE_0{{ i }}
            </span>
          </div>
          <div class="grid grid-cols-4 gap-8 h-1">
            <div v-for="i in 4" :key="'bar-'+i"
                 class="relative h-full transition-all duration-700 rounded-full bg-gray-800/40"
                 :class="i <= currentStep ? 'bg-cyan-500/20' : 'bg-gray-800/40'">
              <div v-if="i <= currentStep" class="absolute inset-0 bg-cyan-500 rounded-full shadow-[0_0_10px_rgba(0,243,255,0.4)]"></div>
              <div v-if="i === currentStep" class="absolute -top-1 -right-1 w-3 h-3 bg-cyan-500 rounded-full border border-[#0a0e17] shadow-[0_0_10px_#00f3ff]"></div>
            </div>
          </div>
        </div>

        <!-- STAGE 1: Discovery Interview (인터랙티브 개편 [수정일: 2026-01-31]) -->
        <div v-if="currentStep === 1" class="grid grid-cols-1 lg:grid-cols-[1fr_1.35fr] gap-10 lg:gap-14 animate-fade-in-up items-start max-w-[1600px] mx-auto w-full flex-1 min-h-0 pb-10">
          <!-- Info Card (Coduck's Briefing) -->
          <div class="bg-[#0d1117] border border-white/10 p-12 lg:p-16 rounded-3xl flex flex-col relative overflow-hidden shadow-2xl">
            <div class="flex flex-col gap-8 mb-12">
              <div class="flex items-center gap-6">
                <div class="p-4 bg-cyan-500/5 rounded-2xl border border-cyan-500/10">
                  <MessageSquare class="text-cyan-400/50 w-10 h-10" />
                </div>
                <div class="space-y-1">
                  <span class="text-cyan-500/30 font-mono text-[9px] tracking-[0.3em] uppercase block">Discovery_Phase_v1.0</span>
                  <h2 class="text-5xl lg:text-7xl font-black text-white italic tracking-tighter uppercase leading-none">
                    Stage 1:<br/>
                    <span class="text-cyan-400">요구사항 인터뷰</span>
                  </h2>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-8 p-10 bg-cyan-500/5 rounded-3xl border border-cyan-500/20 mb-8 relative overflow-hidden group/brief">
              <div class="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rotate-45 translate-x-16 -translate-y-16 group-hover/brief:bg-cyan-500/20 transition-all"></div>
              <div class="relative w-24 h-24 shrink-0 rounded-2xl overflow-hidden border-2 border-cyan-400/40 shadow-[0_0_20px_rgba(34,211,238,0.2)]">
                <img :src="imageSrc" alt="Coduck" class="w-full h-full object-cover" />
              </div>
              <div class="relative flex-1">
                 <h4 class="text-[10px] font-mono text-cyan-500 uppercase tracking-[0.3em] mb-2 font-black italic">Coduck_Briefing</h4>
                 <p class="text-lg text-gray-200 font-bold leading-relaxed">
                   "엔지니어님, 시스템 설계 전 저와 인터뷰를 통해 세부 규격을 확정하시죠. 저의 질문에 신중히 답해주세요!"
                 </p>
              </div>
            </div>

            <div class="space-y-8 mt-auto">
              <div class="bg-[#090c10] p-8 lg:p-10 border border-cyan-500/40 rounded-3xl relative shadow-inner">
                <h3 class="text-[#00f3ff] font-black text-2xl mb-4 flex items-center gap-3">
                  <div class="w-2.5 h-2.5 bg-cyan-400 rounded-full shadow-[0_0_10px_#00f3ff]"></div>
                  현재 진행 상황: {{ currentInterviewIdx + 1 }} / {{ currentQuest.interviewQuestions?.length || 1 }}
                </h3>
                <p class="text-white text-[18px] font-bold leading-relaxed opacity-60">
                  인터뷰를 통해 획득한 수치는 설계 단계에서 중요한 기준이 됩니다. 
                </p>
              </div>
            </div>
          </div>

          <!-- Interview Card (Questions) -->
          <div class="bg-[#0d1117] border border-white/10 p-12 lg:p-16 rounded-3xl flex flex-col shadow-2xl h-full">
            <div v-if="currentInterviewQuestion" class="flex flex-col h-full gap-8">
              <div class="flex flex-col gap-8">
                <div class="flex items-baseline gap-6 h-10">
                  <span class="text-cyan-500 font-black text-4xl italic leading-none uppercase">Question {{ currentInterviewIdx + 1 }}</span>
                </div>
                <h3 class="text-3xl lg:text-4xl font-black text-white leading-[1.2] min-h-[100px]">
                  {{ currentInterviewQuestion.question }}
                </h3>
              </div>

              <div class="grid grid-cols-1 gap-6 mt-8">
                <button v-for="(opt, idx) in currentInterviewQuestion.options" :key="idx"
                  @click="handleStep1Submit(opt)"
                  class="w-full text-left p-8 lg:p-10 bg-[#161b22] border border-white/10 rounded-2xl hover:bg-[#1c2128] hover:border-cyan-500/60 transition-all group flex items-center shadow-md hover:shadow-cyan-500/10 relative overflow-hidden">
                  <div class="absolute inset-y-0 left-0 w-2.5 transition-all bg-transparent group-hover:bg-cyan-500"></div>
                  <span class="flex-1 font-bold text-[#c9d1d9] text-xl lg:text-[24px] group-hover:text-white transition-colors pl-6 lg:pl-10">
                    {{ opt.text }}
                  </span>
                </button>
              </div>
            </div>
            <!-- Backup for old quiz format -->
            <div v-else class="flex flex-col h-full gap-8">
                <div class="flex flex-col gap-8 mb-12">
                  <div class="flex items-baseline gap-6 h-10">
                    <span class="text-cyan-500 font-black text-6xl italic leading-none">Q.</span>
                  </div>
                  <h3 class="text-3xl lg:text-4xl font-black text-white leading-[1.2]">{{ currentQuest.quizTitle || '정답을 고르세요.' }}</h3>
                </div>
                <div class="grid grid-cols-1 gap-6">
                  <button v-for="(opt, idx) in currentQuest.quizOptions" :key="idx"
                    @click="handleStep1Submit(opt)"
                    class="w-full text-left p-8 lg:p-10 bg-[#161b22] border border-white/10 rounded-2xl hover:bg-[#1c2128] hover:border-cyan-500/60 transition-all group flex items-center shadow-md">
                    <span class="flex-1 font-bold text-[#c9d1d9] text-xl lg:text-[24px]">
                      {{ idx + 1 }}. {{ opt?.text }}
                    </span>
                  </button>
                </div>
            </div>
          </div>
        </div>

        <!-- STAGE 2: Pseudocode (main 브랜치의 문제 정의 HUD 복구) -->
        <div v-if="currentStep === 2" class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-14 animate-fade-in-up items-stretch max-w-[1600px] mx-auto w-full flex-1 min-h-0 pb-6 md:pb-10">
          <div class="flex flex-col gap-6 lg:gap-10 min-h-0 w-full">
            <!-- Problem Definition -->
            <div class="bg-black/40 border border-cyan-500/20 p-6 lg:p-12 hud-box-clip flex-1 md:h-[350px] relative overflow-hidden group flex flex-col">
              <h3 class="text-3xl font-black text-white italic mb-8 flex items-center gap-4 shrink-0">
                <CodeIcon class="w-8 h-8 text-cyan-400" /> MISSION_OBJECTIVE
              </h3>
              <!-- Scrollable Content -->
              <div class="flex-1 overflow-y-auto custom-scrollbar pr-4 space-y-8">
                <p class="text-gray-300 leading-relaxed font-bold text-xl lg:text-2xl">
                  {{ currentQuest.missionObjective || '해당 단계의 매뉴얼이 업로드되지 않았습니다.' }}
                </p>
                <div class="h-px bg-gradient-to-r from-cyan-500/50 to-transparent"></div>
                <div class="space-y-4">
                  <span class="text-cyan-500/40 font-mono text-[10px] tracking-[0.2em] uppercase font-bold">Metadata_Tags</span>
                  <div class="flex flex-wrap gap-3 uppercase font-mono text-[11px]">
                    <div v-for="tag in ['iteration', 'conditional', 'filtering', 'data_cleaning']" :key="tag" class="px-3 py-1.5 bg-white/5 border border-white/10 text-gray-400 font-bold">{{ tag }}</div>
                  </div>
                </div>
              </div>
              <div class="absolute bottom-4 right-4 text-[60px] font-black text-white/[0.02] select-none pointer-events-none font-mono">CODE_PROTOCOL_X</div>
            </div>

            <!-- Chat -->
            <div class="bg-black/60 border border-white/5 hud-box-clip h-[350px] flex flex-col overflow-hidden relative">
              <div class="bg-white/5 p-3 text-[10px] font-mono text-cyan-400/50 border-b border-white/5 flex justify-between items-center tracking-widest px-6 italic uppercase">
                <span>Agent_Link_Active</span>
                <span class="flex items-center gap-2"><div class="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse"></div> ENCRYPTED</span>
              </div>
              <div ref="chatContainer" class="flex-1 overflow-y-auto p-8 space-y-6 custom-scrollbar">
                <div v-for="(msg, idx) in chatMessages" :key="idx"
                  class="flex gap-4 mb-6" :class="msg.sender === 'User' ? 'flex-row-reverse items-start' : 'flex-row items-start'">
                  
                  <!-- [수정일: 2026-01-31] 캐릭터 아바타 노출 로직 보강 -->
                  <div v-if="msg.sender === 'Coduck'" class="w-12 h-12 shrink-0 rounded-xl overflow-hidden border-2 border-cyan-500/30 shadow-[0_0_15px_rgba(34,211,238,0.2)] bg-black/40">
                    <img :src="imageSrc" alt="Coduck" class="w-full h-full object-cover" />
                  </div>
                  <div v-else class="w-12 h-12 shrink-0 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center shadow-inner">
                    <Terminal class="w-6 h-6 text-cyan-500/50" />
                  </div>

                  <div class="flex flex-col flex-1" :class="msg.sender === 'User' ? 'items-end' : 'items-start'">
                    <span class="text-[9px] text-gray-500 font-black mb-1.5 uppercase tracking-widest">{{ msg.sender }}_ID</span>
                    <div class="max-w-[100%] p-5 text-base leading-relaxed hud-button-clip shadow-xl"
                         :class="msg.sender === 'Coduck' ? 'bg-cyan-500/15 text-cyan-50 text-[15px] border border-cyan-500/30' : 'bg-white/5 text-gray-200 border border-white/10'">
                      {{ msg.text }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Input Area (Monaco Editor Integration) -->
          <div class="bg-white/[0.02] border border-white/10 p-10 lg:p-12 hud-box-clip flex flex-col items-stretch relative overflow-hidden">
            <div class="flex items-center justify-between mb-10">
              <div class="space-y-1">
                <h3 class="text-2xl font-black text-white tracking-[0.2em] italic uppercase">PSEUDO_COMPILER</h3>
                <div class="text-[10px] font-mono text-cyan-400/40 uppercase tracking-widest">Logic_Validation_Engine v4.0</div>
              </div>
              <div class="text-[10px] font-mono text-gray-500 flex items-center gap-3 bg-white/5 px-4 py-2 rounded-lg border border-white/5">
                <span class="w-2 h-2 rounded-full bg-yellow-500 animate-pulse shadow-[0_0_8px_#eab308]"></span> 
                <span class="font-bold tracking-tighter uppercase">WAITING_FOR_INPUT</span>
              </div>
            </div>
            
            <div class="relative flex-1 flex flex-col group/editor min-h-[400px]">
              <VueMonacoEditor
                v-model:value="pseudoInput"
                theme="vs-dark"
                language="markdown"
                :options="editorOptions"
                class="flex-1"
              />
              
              <!-- Corner Accents -->
              <div class="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-cyan-500/20 pointer-events-none transition-colors"></div>
              <div class="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-cyan-500/20 pointer-events-none transition-colors"></div>
            </div>

            <div class="grid grid-cols-2 gap-4 mt-12">
              <!-- AI에게 질문하기 (상담 모드) -->
              <button @click="askCoduck" :disabled="isAsking || isEvaluating" class="group relative transition-all active:scale-[0.98]">
                <div class="absolute -inset-1 bg-gradient-to-r from-cyan-600/30 to-blue-700/30 rounded-lg blur opacity-30 group-hover:opacity-100 transition duration-500"></div>
                <div class="relative w-full py-5 bg-black/40 border border-cyan-500/30 text-cyan-400 font-bold text-lg tracking-widest uppercase hover:bg-cyan-500/10 transition-all hud-button-clip flex items-center justify-center gap-4">
                  <div v-if="isAsking" class="w-4 h-4 border-2 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin"></div>
                  <Cpu v-else class="w-5 h-5" />
                  {{ isAsking ? 'ANALYZING...' : 'Coduck에게 질문하기' }}
                </div>
              </button>

              <!-- 최종 로직 제출 (평가 모드) -->
              <button @click="submitStep2" :disabled="isAsking || isEvaluating" class="group relative transition-all active:scale-[0.98]">
                <div class="absolute -inset-1 bg-gradient-to-r from-pink-600/40 to-cyan-700/40 rounded-lg blur opacity-50 group-hover:opacity-100 transition duration-500"></div>
                <div class="relative w-full py-5 bg-black border border-cyan-500/50 text-white font-black text-lg tracking-[0.2em] uppercase hover:bg-cyan-500/10 transition-all hud-button-clip flex items-center justify-center gap-4">
                  <div v-if="isEvaluating" class="w-5 h-5 border-2 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin"></div>
                  <Terminal v-else class="w-5 h-5 text-cyan-400" />
                  {{ isEvaluating ? 'EVALUATING...' : '최종 로직 제출' }}
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- STAGE 3: Python Build (중요: 블록/빈칸에서 Monaco Editor 직접 입력으로 개편) -->
        <div v-if="currentStep === 3" class="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-14 animate-fade-in-up items-start max-w-[1600px] mx-auto w-full flex-1 min-h-0">
          <!-- Left: Code Editor -->
          <div class="flex flex-col min-h-0 h-full">
            <div class="bg-black/40 border border-white/10 p-8 hud-box-clip flex-1 flex flex-col min-h-[500px]">
              <div class="flex items-center justify-between mb-8">
              <div class="flex items-center gap-6">
                  <div class="p-4 bg-cyan-500/10 rounded-xl border-2 border-cyan-500/30">
                    <CodeIcon class="text-cyan-400 w-8 h-8" />
                  </div>
                  <div>
                    <h3 class="text-3xl font-black text-white italic tracking-tighter uppercase">{{ currentQuest.title }}</h3>
                    <p class="text-xs text-cyan-500 font-mono tracking-[0.3em] font-bold">MODULE: {{ currentQuest.subModuleTitle || 'SYSTEM_CORE' }}</p>
                  </div>
                </div>
              </div>
              
              <!-- [추가] Mission Briefing (상시 노출 문제 설명) -->
              <div class="mb-10 p-6 bg-cyan-500/5 border border-cyan-500/20 rounded-2xl relative overflow-hidden">
                <div class="flex items-start gap-5">
                  <div class="p-3 bg-cyan-500/10 rounded-lg">
                    <Terminal class="w-5 h-5 text-cyan-400" />
                  </div>
                  <div class="flex-1">
                    <h4 class="text-[10px] font-mono text-cyan-500/40 uppercase tracking-[0.3em] mb-2 font-black italic">MISSION_BRIEFING</h4>
                    <p class="text-lg text-gray-200 font-bold leading-relaxed italic">
                      {{ currentQuest.missionObjective || '현재 단계의 규칙 분석 중...' }}
                    </p>
                  </div>
                </div>
                <!-- Decoration dots -->
                <div class="absolute top-2 right-4 flex gap-1">
                  <div v-for="i in 3" :key="i" class="w-0.5 h-0.5 bg-cyan-500/40"></div>
                </div>
              </div>
              
              <!-- Python Monaco Editor Helper Chips (디자인 및 가독성 고도화) -->
              <div class="mb-4">
                <div class="flex items-center gap-3 mb-4">
                  <div class="h-[1px] flex-1 bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent"></div>
                  <span class="text-[10px] font-mono text-cyan-500/50 tracking-[0.4em] uppercase font-black italic">Assist_Interface</span>
                  <div class="h-[1px] flex-1 bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent"></div>
                </div>
                <div class="flex flex-wrap gap-4 justify-center">
                  <button 
                    v-for="token in (currentQuest.pythonSnippets || [])" 
                    :key="token.code"
                    @click="insertSnippet(token.code)"
                    class="flex items-center gap-3 px-5 py-2.5 bg-[#1a1a1a] hover:bg-white/[0.05] border border-white/10 hover:border-cyan-500/50 rounded-lg transition-all active:scale-[0.97] group/chip shadow-lg hover:shadow-cyan-500/5"
                  >
                    <div :class="['p-1.5 rounded-md transition-all group-hover/chip:scale-110 shadow-inner bg-cyan-500/10']">
                      <!-- 아이콘을 토큰 데이터에 따라 동적으로 v-if로 렌더링 -->
                      <RotateCcw v-if="token.icon === 'RotateCcw'" class="w-4 h-4 text-cyan-400" />
                      <CodeIcon v-else-if="token.icon === 'CodeIcon'" class="w-4 h-4 text-cyan-400" />
                      <X v-else-if="token.icon === 'X'" class="w-4 h-4 text-cyan-400" />
                      <Cpu v-else-if="token.icon === 'Cpu'" class="w-4 h-4 text-cyan-400" />
                      <Award v-else-if="token.icon === 'Award'" class="w-4 h-4 text-cyan-400" />
                      <Terminal v-else class="w-4 h-4 text-cyan-400" />
                    </div>
                    <div class="flex flex-col items-start gap-0.5">
                      <span class="text-[11px] font-black text-gray-500 group-hover/chip:text-cyan-400 transition-colors uppercase tracking-tighter">{{ token.label }}</span>
                      <span class="text-[12px] font-mono font-bold text-gray-300">{{ token.code.split('(')[0] }}</span>
                    </div>
                  </button>
                </div>
              </div>

              <!-- Python Monaco Editor -->
              <div class="flex-1 border border-white/10 relative group bg-[#111] rounded-xl overflow-hidden min-h-0 shadow-[inset_0_0_30px_rgba(0,0,0,0.5)]">
                <VueMonacoEditor
                  v-model:value="pythonInput"
                  language="python"
                  :options="editorOptions"
                  class="h-full"
                />
              </div>

              <div class="mt-8 p-8 bg-cyan-500/[0.03] border border-cyan-500/10 rounded-2xl relative overflow-hidden shrink-0 group/tip">
                <div class="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rotate-45 translate-x-12 -translate-y-12"></div>
                <div class="flex gap-6 items-center">
                  <div class="w-12 h-12 bg-cyan-400/10 rounded-xl flex items-center justify-center shrink-0 border border-cyan-400/20 group-hover/tip:border-cyan-400/40 transition-colors">
                    <AlertTriangle class="text-cyan-400 w-6 h-6 animate-pulse" />
                  </div>
                  <div class="flex-1">
                    <h4 class="text-[11px] font-mono text-cyan-500 uppercase tracking-[0.2em] mb-1 font-black">CODUCK_SYSTEM_GUIDE</h4>
                    <p class="text-base lg:text-lg text-gray-400 font-bold leading-relaxed">
                      작성하신 논리를 <span class="text-cyan-400 italic font-black uppercase tracking-tighter">Python 코드로 구현</span>할 차례입니다.
                      에디터 내의 <span class="text-white bg-cyan-500/20 px-2 py-0.5 rounded text-sm mx-1"># TODO</span> 주석 위치에 적절한 제어문과 행동을 배치해 정화 모듈을 완성하세요.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: Executor (Simulation) -->
          <div class="bg-[#1a1a1a] border border-white/5 hud-box-clip flex flex-col relative overflow-hidden group shadow-2xl min-h-[500px]">
            <div class="p-6 px-10 flex justify-between items-center shrink-0 border-b border-white/5 bg-black/20">
              <div class="flex items-center gap-3">
                <div class="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></div>
                <span class="text-[12px] font-mono text-cyan-400/60 uppercase tracking-widest font-black">AI_GYM_SANDBOX_v1.0</span>
              </div>
              <span class="text-[11px] font-mono text-gray-500 uppercase tracking-widest italic font-bold">execution_log.v3</span>
            </div>

            <div class="flex-1 p-8 lg:p-12 relative overflow-y-auto custom-scrollbar min-h-0 font-mono" ref="simulationContainer">
              <div v-if="!simulationOutput" class="h-full flex flex-col items-center justify-center text-gray-600 gap-6 opacity-40">
                <Cpu class="w-20 h-20" />
                <p class="text-lg font-black tracking-widest">AWAITING_CODE_COMMIT</p>
              </div>
              <div v-else class="font-mono text-sm leading-relaxed" v-html="simulationOutput"></div>
              
              <div class="absolute bottom-8 right-8 z-20 flex gap-4">
                <!-- [수정일: 2026-01-31] 로직 수정하기 (Feedback Loop) 버튼 추가 -->
                <button @click="goToStep(2)" 
                  class="group relative h-12 transition-all active:scale-[0.98]"
                >
                  <div class="relative px-6 h-full bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white font-bold text-sm tracking-wide transition-all flex items-center justify-center rounded-sm border border-white/10">
                    로직 수정하기 (Back to Design)
                  </div>
                </button>

                <button @click="runSimulation" 
                  class="group relative h-12 transition-all active:scale-[0.98]"
                  :disabled="isSimulating"
                >
                  <div class="relative px-8 h-full bg-[#117e96] hover:bg-[#1491ad] text-white font-bold text-sm tracking-wide transition-all flex items-center justify-center rounded-sm">
                    <div v-if="isSimulating" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-3"></div>
                    {{ isSimulating ? '실행 중...' : '코드 실행 및 검증' }}
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- STAGE 4: Deep Dive (main 브랜치의 트레이드오프 설명 HUD 복구) -->
        <div v-if="currentStep === 4" class="grid grid-cols-1 xl:grid-cols-2 gap-8 lg:gap-14 animate-fade-in-up items-stretch max-w-[1800px] mx-auto w-full flex-1 min-h-0 pb-6 md:pb-10">
          <!-- Left: Coding Editor Area -->
          <div class="flex flex-col min-h-[500px] md:min-h-0 w-full">
            <div class="bg-black/40 border border-white/5 p-6 lg:p-12 relative group overflow-hidden flex-1 flex flex-col hud-box-clip min-h-0">
              <div class="absolute top-0 right-0 w-32 h-32 bg-pink-500/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-pink-500/10 transition-all duration-1000"></div>
              
              <div class="flex items-center gap-6 mb-10">
                <div class="p-4 bg-pink-500/10 rounded-xl border-2 border-pink-500/30">
                  <Award class="text-pink-400 w-10 h-10" />
                </div>
                <div>
                  <h2 class="text-4xl lg:text-5xl font-black text-white italic tracking-tighter uppercase">ANOMALY_DETECTION</h2>
                  <p class="text-xs text-pink-500 font-mono tracking-[0.3em] font-bold">SUB_MODULE: DATA_LOSS_PREVENTION</p>
                </div>
              </div>

              <div class="space-y-10 text-gray-300 leading-relaxed font-bold">
                <p class="text-2xl text-white/90">전처리가 지나치게 완벽하면, 유효한 데이터까지 '오염물'로 분류될 위험이 있습니다.</p>
                
                <div class="relative pt-10">
                  <div class="absolute top-0 left-0 w-16 h-1.5 bg-pink-500 shadow-[0_0_10px_#ec4899]"></div>
                  <h3 class="text-pink-400 font-black text-xs uppercase tracking-[0.4em] mb-6">ENGINEERING ISSUE: TRADE-OFF</h3>
                  <div class="bg-pink-500/5 p-10 border border-pink-500/20 relative overflow-hidden group hud-box-clip">
                    <p class="text-2xl text-white italic mb-6 font-black tracking-tight">"False Positives vs Information Loss"</p>
                    <p class="text-lg lg:text-xl text-gray-400 leading-relaxed italic">
                      "광고"라는 키워드를 기계적으로 삭제한다면, <span class="text-pink-300 font-bold border-b border-pink-500/30">"광고 업계의 동향"</span>과 같은 중요한 뉴스마저 소실될 수 있습니다.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quiz -->
          <div class="flex flex-col gap-6">
            <div class="bg-black/40 border border-white/10 p-10 lg:p-14 hud-box-clip flex-1 flex flex-col">
              <h3 class="text-2xl lg:text-3xl font-black text-white mb-12 leading-tight uppercase tracking-tight italic border-l-4 border-cyan-500 pl-6">Q. {{ currentQuest.quizTitle || '최적의 엔지니어링 접근은?' }}</h3>
              <div class="space-y-6">
                <button v-for="(opt, idx) in step4Options" :key="idx"
                  @click="handleStep4Submit(idx)"
                  class="w-full text-left p-8 bg-white/[0.02] hover:bg-pink-500/10 border border-white/5 hover:border-pink-500/30 transition-all group relative overflow-hidden hud-button-clip"
                >
                  <div class="flex items-center">
                    <div class="w-14 h-14 bg-white/5 border border-white/10 flex items-center justify-center mr-8 text-sm font-mono text-pink-400 group-hover:bg-pink-500 group-hover:text-black transition-all font-black">
                      0{{ idx + 1 }}
                    </div>
                    <span class="flex-1 font-black text-lg lg:text-xl text-gray-400 group-hover:text-white transition-colors tracking-tight">{{ opt }}</span>
                  </div>
                </button>
              </div>

              <!-- [수정일: 2026-01-31] 순환 구조(Feedback Loop) 구현: 실구현 결과에 따라 설계를 수정할 수 있도록 이전 단계로 돌아가는 버튼 추가 -->
              <div class="mt-8 flex justify-center">
                <button @click="goToStep(2)"
                  class="px-8 py-4 bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white font-black text-xs tracking-widest transition-all rounded-sm border border-white/10 uppercase italic"
                >
                  <span class="mr-2">←</span> 로직 수정하러 돌아가기 (Back to Design)
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- STAGE 5: Final Report (main 브랜치의 화려한 결과 화면 복구) -->
        <div v-if="currentStep === 5" class="flex-1 flex flex-col items-center justify-center animate-fade-in-up py-10 px-6 max-w-[1400px] mx-auto w-full h-full min-h-0 self-center">
          <div class="bg-black/90 border-2 border-cyan-500/30 hud-box-clip w-full p-16 lg:p-24 text-center relative overflow-hidden backdrop-blur-3xl group shadow-[0_0_150px_rgba(0,0,0,1)]">
            <div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:60px_60px] opacity-30"></div>
            <div class="absolute inset-0 bg-gradient-to-t from-cyan-500/10 via-transparent to-transparent"></div>
            
            <div class="relative z-10 space-y-16">
              <div class="space-y-8">
                <div class="inline-block relative">
                  <div class="absolute -inset-12 bg-cyan-500/10 blur-3xl rounded-full scale-110 animate-pulse"></div>
                  <Award class="w-40 h-40 text-cyan-400 mx-auto drop-shadow-[0_0_40px_#00f3ff] relative z-10" />
                </div>
                
                <div class="space-y-4">
                  <h2 class="text-6xl lg:text-7xl font-black text-white italic tracking-tighter uppercase scale-y-110 drop-shadow-[4px_4px_0px_#00f3ff44]">Restore_Success</h2>
                  <div class="h-2 w-64 bg-cyan-500 mx-auto shadow-[0_0_30px_#00f3ff]"></div>
                  <div class="text-xs text-cyan-500 font-mono tracking-[0.6em] uppercase mt-6 italic font-bold">Protocol_Resolution_Integrity_Confirmed</div>
                </div>
              </div>

              <!-- Score Grid -->
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                <div v-for="(val, key, index) in { 'CONCEPT': userScore.step1, 'LOGIC': userScore.step2, 'CODE': userScore.step3, 'DEEP_DIVE': userScore.step4 }" :key="key" 
                  class="bg-white/[0.03] border border-white/5 p-8 hud-box-clip hover:bg-cyan-500/10 transition-all text-left group/card relative animate-fade-in-up"
                  :style="{ animationDelay: (400 + index * 100) + 'ms' }">
                  <div class="absolute top-0 right-0 p-3 opacity-10 group-hover/card:opacity-30 transition-opacity">
                    <div class="text-[8px] font-mono text-cyan-500 flex flex-col items-end">
                      <span>SEC_{{ index + 1 }}</span>
                      <span>UID_0x{{ (index * 123 + 456).toString(16).toUpperCase() }}</span>
                    </div>
                  </div>
                  <div class="text-xs font-black text-cyan-500/40 uppercase tracking-widest mb-4 italic group-hover/card:text-cyan-400 transition-colors">{{ key }}_CORE</div>
                  <div class="flex items-baseline gap-3 mb-8">
                    <span class="text-5xl lg:text-6xl font-black text-white italic group-hover/card:scale-110 transition-transform origin-left">{{ val }}</span>
                    <span class="text-sm text-gray-700 font-mono font-bold">/ 25</span>
                  </div>
                  <div class="h-1 bg-white/5 w-full relative overflow-hidden">
                    <div class="absolute inset-y-0 left-0 bg-cyan-500 transition-all duration-1000" :style="{ width: (val / 25 * 100) + '%' }"></div>
                  </div>
                </div>
              </div>

              <!-- Coduck Review Section -->
              <div class="bg-black/40 border border-cyan-500/20 p-10 hud-box-clip text-left relative overflow-hidden">
                <div class="flex items-start gap-10">
                  <div class="shrink-0 hidden lg:block">
                    <div class="w-24 h-24 bg-cyan-500/5 border border-cyan-500/20 hud-box-clip flex items-center justify-center relative">
                      <Terminal class="w-10 h-10 text-cyan-400 opacity-40" />
                      <div class="absolute -top-1 -right-1 w-3 h-3 bg-cyan-500 rounded-full animate-pulse shadow-[0_0_10px_#00f3ff]"></div>
                    </div>
                  </div>
                  <div class="flex-1 space-y-8">
                    <h3 class="text-cyan-400 font-black text-sm uppercase tracking-[0.5em] italic flex items-center gap-4">
                      <span class="w-3 h-3 bg-cyan-500 rounded-full animate-ping"></span>
                      Coduck_Integrated_Synthetic_Review
                    </h3>
                    <p class="text-2xl lg:text-3xl text-gray-100 leading-relaxed font-black italic border-l-8 border-cyan-500/40 pl-10" v-html="finalReviewText"></p>
                  </div>
                </div>
              </div>

              <div class="flex flex-col sm:flex-row gap-8 justify-center items-center">
                <button @click="reloadApp"
                  class="group px-14 py-6 bg-white/5 hover:bg-white/10 text-gray-500 hover:text-white font-black uppercase tracking-[0.2em] text-xs border border-white/5 hover:border-white/20 hud-button-clip transition-all active:scale-95 flex items-center gap-4">
                  <RotateCcw class="w-4 h-4 group-hover:rotate-180 transition-transform duration-700" />
                  Recalibrate_System
                </button>
                
                <!-- [수정일: 2026-01-31] 다음 미션으로 바로 가기 버튼 추가 (조건부 노출) -->
                <button v-if="currentQuestIdx < aiQuests.length - 1" @click="goToNextQuest"
                  class="group px-14 py-6 bg-cyan-600 text-black font-black uppercase tracking-[0.2em] text-xs hud-button-clip hover:bg-cyan-400 hover:shadow-[0_0_30px_#00f3ff] transition-all active:scale-95 flex items-center gap-4">
                  <Terminal class="w-5 h-5 group-hover:scale-110 transition-transform" />
                  Initialize_Next_Mission_Protocol
                </button>

                <button @click="$emit('close')"
                  class="group px-14 py-6 bg-white/10 hover:bg-white/20 text-white font-black uppercase tracking-[0.2em] text-xs border border-white/10 hud-button-clip transition-all active:scale-95 flex items-center gap-4">
                  <ChevronRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  Return_To_Hub_Command
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Feedback Modal (main 브랜치의 거대한 모달 스타일 복구) -->
        <div v-if="feedbackModal.visible" class="fixed inset-0 bg-black/95 flex items-center justify-center z-[110] p-6 backdrop-blur-xl">
          <div class="bg-[#020408] border-2 border-white/10 hud-box-clip p-8 lg:p-12 max-w-2xl w-full shadow-[0_0_100px_rgba(0,0,0,1)] relative animate-fade-in-up">
            <div class="absolute top-0 right-0 p-4 opacity-10">
              <div class="flex gap-2">
                <div v-for="i in 5" :key="i" class="w-1 h-1 bg-white"></div>
              </div>
            </div>

            <div class="flex items-center space-x-6 mb-10">
              <div :class="feedbackModal.isSuccess ? 'bg-green-500/20 text-green-400' : 'bg-pink-500/20 text-pink-400'" class="p-4 border border-current rounded-xl">
                <CheckCircle v-if="feedbackModal.isSuccess" class="w-12 h-12" />
                <AlertTriangle v-else class="w-12 h-12" />
              </div>
              <h3 class="text-2xl lg:text-3xl font-black text-white italic tracking-tighter uppercase">{{ feedbackModal.title }}</h3>
            </div>

            <p class="text-lg lg:text-xl text-gray-200 mb-10 leading-relaxed font-bold italic border-l-4 px-6" :class="feedbackModal.isSuccess ? 'border-green-500' : 'border-pink-500'">{{ feedbackModal.desc }}</p>
            
            <div class="bg-white/[0.03] p-8 border border-white/5 text-lg font-medium text-gray-400 mb-12 leading-relaxed" v-html="feedbackModal.details"></div>
            
            <div class="flex justify-end gap-4">
              <!-- [수정일: 2026-01-31] 순환 구조(Feedback Loop) 반영: 실패 시에는 다음 단계로 넘어가지 않고 수정을 유도하거나 재시도함 -->
              <template v-if="!feedbackModal.isSuccess">
                <button @click="feedbackModal.visible = false" class="group relative h-16 transition-all active:scale-[0.98]">
                  <div class="relative px-12 h-full bg-white/10 text-white font-black uppercase tracking-[0.2em] flex items-center gap-4 hud-button-clip hover:bg-white/20 transition-all">
                    닫기 (Close)
                  </div>
                </button>
                <button v-if="currentStep >= 3" @click="goToStep(2)" class="group relative h-16 transition-all active:scale-[0.98]">
                  <div class="relative px-12 h-full bg-pink-600 text-white font-black uppercase tracking-[0.2em] flex items-center gap-4 hud-button-clip hover:bg-pink-500 transition-all">
                    로직 수정하기 (Back to Design)
                  </div>
                </button>
              </template>
              
              <button v-else @click="nextStep" class="group relative h-16 transition-all active:scale-[0.98]">
                <div class="absolute -inset-1 bg-cyan-500/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition duration-300"></div>
                <div class="relative px-12 h-full bg-cyan-600 text-black font-black uppercase tracking-[0.2em] flex items-center gap-4 hud-button-clip hover:bg-cyan-400 hover:shadow-[0_0_20px_#00f3ff] transition-all">
                  {{ currentStep === 4 ? "GENERATE_REPORT" : "INITIALIZE_NEXT_PROTOCOL" }} 
                  <ChevronRight class="w-6 h-6" />
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- [수정일: 2026-01-31] 하단 고정 오리 제거 (채팅 UI로 통합) -->
      </main>
    </div>
  </div>
</template>

<script setup>
/**
 [수정일: 2026-01-31]
 내용: 스크립트 로직을 별도 파일(pseudoProblemLogic.js)로 분리하여 유지보수성 향상
*/
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'
import {
  Terminal,
  Cpu,
  Code as CodeIcon,
  Award,
  RotateCcw,
  ChevronRight,
  AlertTriangle,
  CheckCircle,
  MessageSquare,
  X,
  Volume2,
  VolumeX
} from 'lucide-vue-next'
import Duck from './components/Duck.vue'
import { usePseudoProblem } from './pseudoProblemLogic'

const props = defineProps({
  // 라우터를 통해 페이지로 접근 시 화면이 즉시 보이도록 기본값을 true로 설정
  isOpen: { type: Boolean, default: true }
})

const emit = defineEmits(['close'])

// Composable을 통해 모든 상태와 메서드를 가져옵니다.
const {
  currentQuest,
  currentStep,
  userScore,
  pseudoInput,
  pythonInput, // 추가
  chatMessages,
  chatContainer,
  blocks,
  selectedBlock,
  simulationOutput,
  simulationContainer,
  isSimulating,
  isEvaluating,
  isAsking, // 추가
  currentInterviewIdx,
  currentInterviewQuestion,
  interviewResults,
  step4Options,
  feedbackModal,
  editorOptions,
  finalReviewText,
  handleStep1Submit,
  submitStep2,
  selectBlock,
  runSimulation,
  handleStep4Submit,
  nextStep,
  goToStep,
  reloadApp,
  goToNextQuest, // [수정일: 2026-01-31] 추가
  insertSnippet,
  askCoduck,
  aiQuests,      // [수정일: 2026-01-31] 추가
  currentQuestIdx, // [수정일: 2026-01-31] 추가
  imageSrc,
  // [수정일: 2026-02-01] TTS 제어 추가
  isMuted,
  toggleMute,
  // [수정일: 2026-02-01] 시놉시스 추가
  synopsisText,
  skipSynopsis,
  isPlayingBGM
} = usePseudoProblem(props, emit)
</script>

<style scoped>
/* HUD Aesthetics */
.hud-box-clip {
  clip-path: polygon(
    0 0, 
    calc(100% - 20px) 0, 
    100% 20px, 
    100% 100%, 
    20px 100%, 
    0 calc(100% - 20px)
  );
}

.hud-button-clip {
  clip-path: polygon(
    0 0, 
    calc(100% - 10px) 0, 
    100% 10px, 
    100% 100%, 
    10px 100%, 
    0 calc(100% - 10px)
  );
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 243, 255, 0.3);
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-up {
  animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
.animate-scale-in {
  animation: scaleIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

.shadow-neon {
  filter: drop-shadow(0 0 15px rgba(0, 243, 255, 0.4));
}
</style>