<template>
  <div class="min-h-screen w-full flex flex-col relative overflow-hidden boot-screen glitch-bg bg-[#05070A] text-[#A3FF47]" :class="{'shake-effect': isDamaged, 'damage-flash': isDamaged}">

    <!-- [수정일: 2026-02-03] REPAIR EFFECT OVERLAY -->
    <div v-if="isRepaired" class="fixed inset-0 z-[60] pointer-events-none flex items-center justify-center bg-[#A3FF47]/10 animate-fade-in-out">
        <div class="text-center relative">
             <h1 class="text-6xl md:text-8xl font-black italic text-[#A3FF47] tracking-tighter drop-shadow-[0_0_30px_rgba(163,255,71,0.8)] scale-up-center">SYSTEM REPAIRED</h1>
             <div class="h-1 w-full bg-[#A3FF47] mt-4 animate-width-expand"></div>
             <p class="text-xl md:text-2xl mt-4 font-mono text-[#A3FF47]/80 tracking-[0.5em] uppercase">Architecture Integrity Restored</p>
        </div>
    </div>

    <!-- 0. 시놉시스 레이어 (Star Wars Cinematic) -->
    <div v-if="currentStep === 0" class="fixed inset-0 z-[100] bg-black flex flex-col items-center justify-center overflow-hidden select-none">
      <!-- 배경 동영상 도입 (coduck_wars.mp4) -->
      <video 
        class="absolute inset-0 w-full h-full object-cover z-0 opacity-40" 
        autoplay 
        muted 
        loop 
        playsinline
      >
        <source src="/assets/audio/coduck_wars.mp4" type="video/mp4">
      </video>
      
      <!-- Perspective Container -->
      <div class="relative w-full max-w-4xl h-full flex flex-col items-center text-center perspective-container py-10 md:py-20">
        <!-- Prelude Text (Blue Fade) -->
        <div class="prelude-text animate-fade-out" :style="{ animationDelay: '1s' }">
          PROGRAM: INITIALIZING_REBOOT_PROTOCOL<br/>
          YEAR: 2077<br/>
          LOCATION: MOTHER_SERVER_CORE
        </div>

        <!-- Crawling Content -->
        <div class="crawl-container relative w-full h-full">
          <div class="crawl-content animate-crawl" :style="{ animationDelay: '4.5s' }">
            <h1 class="crawl-title italic">WELCOME BACK, ARCHITECT: {{ userNickname }}</h1>
            <div class="crawl-body italic space-y-12">
              <p>서기 2077년, 인류를 관리하던 '마더 서버'가 오염되었습니다.</p>
              <p>AI들은 현실을 왜곡하는 '환각(Hallucination)'과 '오버피팅'에 빠져 통제를 벗어났습니다.</p>
              <p>대부분의 엔지니어는 기술을 잃었지만, 당신은 유일한 '아키텍처 복구자(Architect)'입니다.</p>
              <p>파트너 'Coduck'과 함께 붕괴된 데이터 구역을 하나씩 정화하고 시스템을 재부팅해야 합니다.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Interaction UI -->
      <div class="absolute bottom-12 right-12 z-[110] flex gap-6 items-center">
        <!-- Audio Status -->
        <div v-if="isPlayingBGM" class="flex items-center gap-3 px-4 py-2 bg-cyan-500/10 border border-cyan-500/30 rounded-full animate-pulse transition-all">
          <Volume2 class="w-4 h-4 text-cyan-400" />
          <span class="text-[10px] font-mono text-cyan-400 font-bold tracking-[0.4em] uppercase italic">Audio_Link_Synced</span>
        </div>

        <button @click="$emit('close')" class="group relative px-8 py-4 bg-red-500/5 hover:bg-red-500/10 text-red-500/60 border border-red-500/20 transition-all active:scale-95 overflow-hidden">
            <span class="relative z-10 font-black text-[10px] tracking-[0.4em] uppercase italic">ABORT_MISSION (EXIT)</span>
            <div class="absolute inset-x-0 bottom-0 h-[1px] bg-red-500 shadow-[0_0_15px_red] scale-y-100 group-hover:scale-y-[2px] transition-all origin-center"></div>
        </button>
        <button @click="skipSynopsis" class="group relative px-10 py-4 bg-[#A3FF47]/10 hover:bg-[#A3FF47]/20 text-[#A3FF47] border border-[#A3FF47]/20 transition-all active:scale-95 overflow-hidden">
            <span class="relative z-10 font-black text-xs tracking-[0.3em] uppercase italic">RE-BOOT_PROTOCOL (SKIP)</span>
            <div class="absolute inset-x-0 bottom-0 h-[2px] bg-[#A3FF47] shadow-[0_0_10px_#00f3ff] scale-x-0 group-hover:scale-x-100 transition-transform origin-center"></div>
        </button>
      </div>
    </div>

    <!-- OS 상단 헤더 -->
    <nav class="h-16 border-b border-[#A3FF47]/20 bg-black/90 backdrop-blur-xl px-4 md:px-8 flex items-center z-50 shrink-0">
      <div class="flex items-center gap-4 md:gap-8 overflow-x-auto no-scrollbar">
        <div class="flex items-center gap-3 shrink-0">
          <div class="w-8 h-8 md:w-10 md:h-10 bg-[#A3FF47] rounded-sm flex items-center justify-center shadow-[0_0_15px_#A3FF47]">
            <Cpu class="text-black w-5 h-5 md:w-6 md:h-6" />
          </div>
          <span class="orbitron-font text-lg md:text-2xl font-black tracking-widest uppercase italic terminal-glow">Architect OS</span>
        </div>
        <div class="h-8 w-px bg-[#A3FF47]/20 hidden sm:block"></div>
        <div class="hidden lg:flex items-center gap-6 text-sm font-bold tracking-widest">
          <span class="flex items-center gap-2 opacity-50">
            <Wifi class="w-5 h-5" /> SECTOR: {{ currentQuest.category }}
          </span>
          <span class="flex items-center gap-2 text-cyan-400 animate-pulse">
            <Activity class="w-5 h-5" /> VOICE_LINK_SYNCED
          </span>
        </div>
        <div class="h-8 w-px bg-[#A3FF47]/20 hidden sm:block"></div>
        <div class="flex items-center gap-3 bg-[#A3FF47]/10 px-3 md:px-5 py-2 rounded-sm border border-[#A3FF47]/30 shrink-0">
          <span class="text-[10px] md:text-xs opacity-50 uppercase">User:</span>
          <span class="text-xs md:text-sm font-black tracking-tighter">{{ userNickname }}</span>
        </div>
        <button @click="toggleMute" class="p-1.5 md:p-2 btn-neon rounded-full shrink-0">
          <VolumeX v-if="isMuted" class="text-red-500 w-5 h-5 md:w-6 md:h-6" />
          <Volume2 v-else class="w-5 h-5 md:w-6 md:h-6" />
        </button>
        <button @click="$emit('close')" class="p-1.5 md:p-2 btn-neon rounded-full shrink-0">
          <X class="text-red-500 w-5 h-5 md:w-6 md:h-6" />
        </button>
      </div>
    </nav>

    <!-- Phase 사이드바 (왼쪽 고정) -->
    <!-- Phase 사이드바 (왼쪽 고정: 평소에는 숨김, 마우스 오버 시 확장) -->
    <div v-if="currentStep > 0" class="fixed left-0 top-16 bottom-0 w-3 hover:w-24 border-r border-[#A3FF47]/10 flex flex-col items-center py-10 gap-8 bg-black/90 z-20 shrink-0 transition-all duration-300 overflow-hidden group">
      <!-- 힌트 바 (평소에 보이는 부분) -->
      <div class="absolute left-0 top-0 bottom-0 w-1 bg-[#A3FF47]/20 group-hover:bg-[#A3FF47] transition-colors"></div>
      
      <div v-for="i in 4" :key="i"
        class="w-20 h-20 rounded-sm flex flex-col items-center justify-center transition-all duration-500 shrink-0 opacity-0 group-hover:opacity-100 translate-x-[-20px] group-hover:translate-x-0"
        :class="currentStep === i ? 'bg-[#A3FF47] text-black shadow-[0_0_30px_#A3FF47]' : 'border border-[#A3FF47]/30 text-[#A3FF47]/40 bg-black/80'"
      >
        <span class="text-[9px] font-black leading-none mb-1 opacity-60">PHASE</span>
        <span class="text-2xl font-black leading-none tracking-tighter">0{{ i }}</span>
      </div>
    </div>

    <!-- 메인 터미널 영역 -->
    <!-- [2026-02-02] 해상도에 따라 사이드바 여백 조절 (사이드바 숨김으로 인한 여백 축소) -->
    <main class="flex-1 flex overflow-hidden relative" :class="currentStep > 0 ? 'ml-4' : ''">
      <div class="flex-1 flex flex-col min-w-0 relative">
        <!-- 상단 미션 브리핑 바 -->
        <div class="border-b border-[#A3FF47]/10 flex flex-col md:grid md:grid-cols-2 bg-[#A3FF47]/5 shrink-0">
          <div class="p-4 flex items-center justify-center border-b md:border-b-0 md:border-r border-[#A3FF47]/10">
            <div class="w-full max-w-[320px] flex items-center justify-between">
              <div>
                <h2 class="text-base md:text-lg font-black italic tracking-tighter uppercase terminal-glow">{{ currentQuest.title }}</h2>
                <p class="text-[8px] opacity-60 uppercase tracking-[0.3em] font-bold">Protocol: {{ currentQuest.subModuleTitle }}</p>
              </div>
              <div class="p-1.5 bg-[#A3FF47]/10 rounded border border-[#A3FF47]/30 opacity-40">
                <Terminal class="w-3.5 h-3.5" />
              </div>
            </div>
          </div>
          <div class="p-4 px-10 flex items-center justify-end">
            <div class="text-right">
              <span class="text-[8px] font-bold opacity-40 block uppercase tracking-widest mb-1">Purification Integrity</span>
              <div class="flex items-center gap-3">
                <div class="w-32 h-1.5 bg-black rounded-full overflow-hidden border border-[#A3FF47]/20">
                  <div class="h-full bg-[#A3FF47] shadow-[0_0_10px_#A3FF47] transition-all duration-1000" :style="{ width: integrity + '%' }"></div>
                </div>
                <span class="text-xl font-black text-[#A3FF47] tracking-tighter">{{ integrity }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="flex-1 flex overflow-hidden">
          <!-- Step 1: Coduck 각성 및 사고 회로 복구 인터뷰 -->
          <!-- [2026-02-03] 모바일/태블릿(lg)까지는 스택형(1열), 데스크탑(xl)부터 2열 그리드 (사이드바 공간 확보) -->
          <div v-if="currentStep === 1" class="flex-1 grid grid-cols-1 xl:grid-cols-2 bg-black overflow-hidden group">
            <!--
              왼쪽 영역: 이미지 및 텍스트
              [수정사항]
              - pl-24 제거 (이미 상위 div에서 ml-24로 전체 콘텐츠 영역을 띄웠으므로 중복 제거)
            -->
            <div id="tutorial-target-partner" class="p-4 md:p-8 flex flex-col items-center justify-center gap-5 overflow-y-auto custom-scrollbar relative border-b lg:border-b-0 border-[#A3FF47]/10">
              <div class="w-full max-w-[320px] flex flex-col gap-5">
                <!-- Coduck 캐릭터 이미지 영역 -->
                <div class="w-full aspect-square rounded-sm border-2 border-[#A3FF47] p-2.5 relative bg-black shadow-[0_0_60px_rgba(163,255,71,0.1)] overflow-hidden">
                    <img :src="imageSrc" alt="Coduck" class="w-full h-full object-cover grayscale brightness-75 group-hover:grayscale-0 group-hover:brightness-100 transition-all duration-1000" />
                    <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                    <!-- 텍스트 주사선 효과 -->
                    <div class="absolute inset-0 scanline pointer-events-none opacity-20"></div>
                </div>

                <div class="space-y-2.5">
                    <p class="text-lg font-black leading-[1.4] text-[#A3FF47] italic terminal-text tracking-tight animate-pulse">
                    "아키텍처님! 제 음성 모듈이 연결되었습니다.<br/>
                    먼저 제 <span class="bg-[#A3FF47] text-black px-1.5 not-italic">사고 회로</span>를 고쳐주세요."
                    </p>
                </div>
              </div>
            </div>

            <div id="tutorial-target-workspace" class="bg-black/40 p-6 md:p-10 lg:px-14 flex flex-col items-start justify-center gap-8 md:gap-12 border-l-0 xl:border-l border-[#A3FF47]/10 relative overflow-hidden">
              <!-- [2026-02-02] 문제(질문) 폰트 확대 및 최상단 배치 (반응형 폰트 적용) -->
              <div class="w-full space-y-4">
                <div class="flex items-center gap-3 opacity-50">
                   <div class="w-1.5 h-1.5 bg-[#A3FF47]"></div>
                   <span class="text-[9px] font-black uppercase tracking-[0.4em]">INQUIRY_PROTOCOL_v2.0</span>
                </div>
                <h3 class="text-xl md:text-3xl font-black italic text-[#A3FF47] leading-tight terminal-glow">
                  [{{ currentInterviewIdx + 1 }}/{{ currentQuest.interviewQuestions.length }}] {{ currentInterviewQuestion?.question }}
                </h3>
              </div>

              <!-- 2026-02-02: 문제(답변 버튼) 간의 가독성 유지 -->
              <div class="w-full max-w-[500px] flex flex-col gap-8">
              <button
                v-for="(opt, i) in currentQuest.interviewQuestions[currentInterviewIdx]?.options"
                :key="i"
                @click="handleStep1Submit(opt)"
                class="group relative p-6 border-2 border-[#A3FF47]/20 bg-black hover:border-[#A3FF47] hover:bg-[#A3FF47]/5 transition-all text-left active:scale-95 w-full"
              >
                <!-- 장식용 코너 -->
                <div class="absolute top-0 right-0 w-2.5 h-2.5 border-t-2 border-r-2 border-[#A3FF47]/30 group-hover:border-[#A3FF47]"></div>
                <div class="absolute bottom-0 left-0 w-2.5 h-2.5 border-b-2 border-l-2 border-[#A3FF47]/30 group-hover:border-[#A3FF47]"></div>
                
                <div class="flex items-center gap-2 mb-2 opacity-40 group-hover:opacity-100">
                  <span class="text-[8px] font-black uppercase tracking-[0.2em]">REPAIR_SEQUENCE_0{{ i+1 }}</span>
                  <Zap class="w-2 h-2 text-[#A3FF47]" />
                </div>
                <span class="text-lg md:text-xl font-black tracking-tight leading-snug text-white group-hover:text-[#A3FF47] transition-colors">{{ opt.text }}</span>
              </button>
              </div>
            </div>
          </div>

          <!-- Step 2: 수도코드 설계 (Logic Restoration) -->
          <!-- [2026-02-04] 레이아웃 비율 조정: 왼쪽(미션/HUD) 6 vs 오른쪽(터미널) 4 (xl:grid-cols-10 기반) -->
          <div v-else-if="currentStep === 2" class="flex-1 grid grid-cols-1 xl:grid-cols-10 bg-black overflow-hidden relative">
            <!-- [2026-02-02] Phase 1과 구성을 완전히 통일 (p-8, items-center, justify-center) -->
            <!-- [수정일: 2026-02-04] 왼쪽 영역 비중 확대 (60%) -->
            <div class="p-0 flex flex-col border-b lg:border-b-0 border-[#A3FF47]/10 h-[500px] lg:h-full overflow-hidden shrink-0 xl:col-span-6">

              <!-- 상단: Mission Objective (Compact Left-Aligned) -->
              <!-- 상단: Mission Objective (높이 30% 배정 및 스크롤 허용) -->
              <div class="basis-[40%] lg:basis-[30%] grow shrink min-h-0 overflow-y-auto custom-scrollbar p-4 flex flex-col items-center justify-start space-y-6">
                <div class="w-full max-w-[850px] space-y-4 md:space-y-6 flex flex-col items-start">
                  <div class="flex items-center gap-2">
                    <div class="h-4 w-1 bg-[#A3FF47]"></div>
                    <h3 class="text-[9px] font-black tracking-[0.4em] uppercase text-[#A3FF47]/50">Mission Objective</h3>
                  </div>
                  <p class="text-base md:text-xl font-black italic terminal-glow border-l-4 border-[#A3FF47] px-6 py-2 leading-relaxed text-[#A3FF47] whitespace-pre-wrap">{{ currentQuest.missionObjective }}</p>
                  <div class="p-6 md:p-8 bg-[#A3FF47]/5 border-l-4 border-[#A3FF47]/30 text-sm md:text-base leading-relaxed italic text-slate-300 space-y-4 text-left w-full">
                    <p class="text-sm md:text-base whitespace-pre-wrap">"Coduck의 기본 기능을 활성화하기 위해, 데이터 리스트를 순회하며 유효한 패킷(정상 데이터)만

필터링하는 아키텍처 논리를 설계하십시오."</p>
                    <div class="pt-4 border-t border-[#A3FF47]/20 flex justify-start">
                      <p class="text-[10px] md:text-[12px] font-black text-[#A3FF47] not-italic uppercase tracking-widest flex items-center gap-2">
                         <MessageSquare class="w-3 h-3" /> System_Directive: 의사코드 작성
                      </p>
                    </div>
                  </div>

                  <!-- [수정일: 2026-02-04] 필수 설계 지침 폰트 확대 -->
                  <div v-if="currentQuest.id > 1 && activeRequirements.length > 0" class="w-full space-y-4 animate-fade-in-up">
                    <div class="flex items-center gap-2">
                      <div class="h-5 w-1.5 bg-pink-500 shadow-[0_0_15px_#ec4899]"></div>
                      <h3 class="text-[11px] font-black tracking-[0.4em] uppercase text-pink-500">Mandatory Design Requirements</h3>
                    </div>
                    <div class="p-5 bg-pink-500/5 border border-pink-500/20 rounded-sm space-y-4">
                      <div v-for="(req, idx) in activeRequirements" :key="idx" class="flex items-start gap-4">
                        <div class="mt-1.5 w-2 h-2 bg-pink-500 rotate-45 shrink-0 shadow-[0_0_8px_#ec4899]"></div>
                        <p class="text-[14px] font-bold text-white leading-relaxed">{{ req }}</p>
                      </div>
                      <div class="pt-3 mt-3 border-t border-pink-500/10">
                        <p class="text-[10px] font-black text-pink-500/60 uppercase tracking-widest italic animate-pulse">
                          * 위 지침을 준수하지 않을 경우 아키텍처 승인이 반려될 수 있습니다.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 하단: [수정일: 2026-02-04] AI HUD (높이 70%Basis 고정하여 절대 확장 방지) -->
              <div class="basis-[60%] lg:basis-[70%] max-h-[60%] lg:max-h-[70%] flex flex-col items-center bg-black/60 border-t border-[#A3FF47]/10 relative shrink-0 overflow-hidden">
                <div class="h-12 border-b border-[#A3FF47]/20 flex items-center px-4 justify-between bg-[#A3FF47]/5 w-full max-w-[850px] shrink-0">
                  <div class="flex items-center gap-3">
                    <Brain class="w-4 h-4 text-[#A3FF47] animate-pulse" />
                    <span class="text-[12px] font-black uppercase tracking-widest text-[#A3FF47]">AI Architecture Consultant</span>
                  </div>
                  <div class="flex items-center gap-3">
                     <div v-if="isApproved" class="flex items-center gap-2 px-4 py-1.5 bg-[#A3FF47] text-black rounded-sm shadow-[0_0_20px_#A3FF47]">
                        <CheckCircle class="w-3.5 h-3.5" />
                        <span class="text-[11px] font-black uppercase tracking-widest">APPROVED</span>
                     </div>
                     <span v-else class="text-[10px] font-black text-pink-500 uppercase animate-pulse">○ Awaiting_Approval</span>
                  </div>
                </div>
                
                <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar w-full max-w-[850px]">
                  <div v-for="(msg, idx) in chatMessages" :key="idx" 
                    class="flex flex-col gap-1.5"
                    :class="msg.sender === 'User' ? 'items-end' : 'items-start'"
                  >
                    <span class="text-[10px] font-black opacity-30 uppercase tracking-tighter">{{ msg.sender }}</span>
                    <div :class="[
                      'max-w-[90%] px-4 py-3 text-[13px] md:text-[14px] font-bold leading-relaxed',

                      msg.sender === 'User' 
                        ? 'bg-[#A3FF47]/10 text-[#A3FF47] border-r-2 border-[#A3FF47]' 
                        : 'bg-white/5 text-slate-100 border-l-2 border-white/20'
                    ]">
                      {{ msg.text }}
                    </div>
                  </div>
                  <div v-if="isAsking" class="flex items-center gap-2 text-[#A3FF47]">
                     <span class="animate-bounce">●</span><span class="animate-bounce delay-75">●</span><span class="animate-bounce delay-150">●</span>
                  </div>
                </div>

                <div class="p-4 border-t border-[#A3FF47]/10 bg-black/40 flex items-center gap-3 w-full max-w-[850px]">
                  <button 
                    @click="askCoduck"
                    :disabled="isAsking || pseudoInput.length < 5"
                    class="flex-1 py-4 bg-[#A3FF47]/10 border border-[#A3FF47]/30 text-[#A3FF47] text-[12px] font-black uppercase tracking-widest hover:bg-[#A3FF47]/20 transition-all disabled:opacity-30"
                  >
                    {{ isAsking ? 'Consulting...' : 'Request_Logic_Audit' }}
                  </button>
                  <div class="w-10 h-10 border border-[#A3FF47]/20 flex items-center justify-center p-2">
                      <MessageSquare class="w-4 h-4 opacity-30" />
                  </div>
                </div>
              </div>
            </div>
            <!-- [수정일: 2026-02-04] 오른쪽 터미널 영역 비중 축소 (40%) -->
            <div class="bg-black/40 p-0 lg:p-0 flex flex-col items-start justify-center border-l-0 xl:border-l border-[#A3FF47]/10 relative overflow-hidden h-[400px] xl:h-full xl:col-span-4">
              <div class="w-full h-full flex flex-col">
                <div class="h-20 border-b border-[#A3FF47]/10 flex items-center px-10 gap-4 text-xs font-black bg-black/40 shrink-0">
                  <Terminal class="w-5 h-5 opacity-50 text-[#A3FF47]" />
                  <span class="opacity-50 tracking-widest text-[#A3FF47]">ARCHITECT_TERMINAL:</span> LOGIC_RESTORE_v1.pseudo
                </div>
                <div class="flex-1 relative">
                  <VueMonacoEditor
                    v-model:value="pseudoInput"
                    theme="vs-dark"
                    language="markdown"
                    :options="editorOptions"
                    class="h-full"
                  />
                </div>

                <div class="p-10 md:p-16 border-t border-[#A3FF47]/20 flex justify-end shrink-0 bg-black/80">
                  <button 
                    @click="submitStep2" 
                    :disabled="!isApproved"
                    class="w-full md:w-auto px-12 py-4 font-black uppercase text-xs transition-all active:scale-95 border-2 relative overflow-hidden group"
                    :class="isApproved 
                      ? 'bg-[#A3FF47] text-black border-black hover:shadow-[0_0_50px_#A3FF47] scale-105' 
                      : 'bg-black text-[#A3FF47]/30 border-[#A3FF47]/10 cursor-not-allowed opacity-50'"
                  >
                    <div v-if="isApproved" class="absolute inset-0 bg-white/20 animate-pulse pointer-events-none"></div>
                    {{ isApproved ? 'LOGIC VERIFIED - PROCEED TO SIMULATION >>' : 'Analyze Logic Engine' }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 3: 파이썬 구현 (Code Pulse) -->
          <!-- [2026-02-03] 사이드바 공간 확보를 위해 xl 브레이크포인트 사용 -->
          <div v-else-if="currentStep === 3" class="flex-1 grid grid-cols-1 xl:grid-cols-2 overflow-hidden bg-black">
            <!-- [2026-02-02] Phase 1과 구성을 통일 -->
            <div class="flex-1 flex flex-col overflow-hidden relative border-b xl:border-b-0 xl:border-r border-[#A3FF47]/10 h-[400px] xl:h-full">
              <div class="h-12 border-b border-[#A3FF47]/10 flex items-center px-6 justify-between bg-black/60 shrink-0">
                <div class="flex items-center gap-3">
                  <span class="w-2 h-2 rounded-full bg-[#A3FF47] animate-ping"></span>
                  <span class="text-[10px] opacity-60 uppercase tracking-widest font-bold">Python_Restoration_Core</span>
                </div>
                <div class="flex gap-2">
                  <button
                    v-for="(s, i) in currentQuest.pythonSnippets"
                    :key="i"
                    @click="insertSnippet(s.code)"
                    class="text-[9px] font-bold border border-[#A3FF47]/30 px-3 py-1 rounded-sm hover:bg-[#A3FF47]/20 transition-all uppercase"
                  >{{ s.label }}</button>
                </div>
              </div>
              <div class="flex-1 relative">
                <VueMonacoEditor
                  v-model:value="pythonInput"
                  theme="vs-dark"
                  language="python"
                  :options="{ ...editorOptions, fontSize: 16 }"
                  class="h-full"
                />
              </div>
              <div class="p-4 md:p-8 border-t border-[#A3FF47]/10 flex flex-col md:flex-row justify-end gap-3 md:gap-6 shrink-0 bg-black/40">
                <button @click="currentStep = 2" class="px-8 py-3 md:py-4 border border-[#A3FF47]/20 text-[#A3FF47]/40 font-black uppercase text-[10px] tracking-widest hover:bg-[#A3FF47]/5 transition-all">Back_to_Logic</button>
                <button @click="runSimulation" :disabled="isSimulating" class="px-10 md:px-14 py-3 md:py-4 bg-[#A3FF47] text-black font-black uppercase text-xs tracking-widest shadow-[0_0_30px_#A3FF47] transition-all border-2 border-black">
                  {{ isSimulating ? 'DEPLOYING...' : 'RE-BOOT SYSTEM' }}
                </button>
              </div>
            </div>

            <!-- Simulation & Result HUD (Phase 1 비율에 맞춰 조절) -->
            <div class="bg-black/40 flex flex-col gap-4 md:gap-6 overflow-hidden p-6 md:p-10 lg:px-14 border-l-0 xl:border-l border-[#A3FF47]/10">
               <div class="flex-1 flex flex-col gap-4 min-h-0">
                 <div class="flex items-center justify-between border-b border-[#A3FF47]/10 pb-4">
                   <h3 class="text-[10px] font-black opacity-30 uppercase tracking-[0.5em] italic">Simulation_Terminal</h3>
                   <Terminal class="w-4 h-4 text-[#A3FF47]/20" />
                 </div>
                 <div ref="simulationContainer" class="flex-1 bg-black/80 border border-[#A3FF47]/20 rounded p-4 md:p-8 font-mono text-xs overflow-y-auto custom-scrollbar leading-relaxed text-cyan-400 h-full min-h-[500px]">
                    <div v-if="isSimulating" class="animate-pulse text-xs md:text-sm">RUNNING SYNC SIMULATION... [PLEASE WAIT]</div>
                    <div v-else class="whitespace-pre-wrap text-xs md:text-sm">{{ simulationOutput || 'READY FOR DATA UPLINK...' }}</div>
                 </div>
               </div>
            </div>
          </div>

          <!-- Step 4: 심화 분석 (Architecture Review) -->
          <!-- [2026-02-03] 사이드바 공간 확보를 위해 xl 브레이크포인트 사용 -->
          <div v-else-if="currentStep === 4" class="flex-1 grid grid-cols-1 xl:grid-cols-2 bg-black overflow-hidden relative">
            <!-- [2026-02-02] Phase 1과 구성을 완전히 통일 (p-8, items-center, justify-center) -->
            <div class="p-6 md:p-8 flex flex-col items-center justify-center gap-8 md:gap-12 overflow-y-auto custom-scrollbar relative bg-black border-b xl:border-b-0 border-[#A3FF47]/10">
              <div class="w-full max-w-[320px] space-y-6 md:space-y-8">
                <div class="space-y-4 md:space-y-6 text-center">
                  <h3 class="text-pink-500 font-black text-[10px] md:text-xs uppercase tracking-[0.5em] animate-pulse">Final System Clearance</h3>
                  <!-- [2026-02-02] 반응형 폰트 크기 적용 -->
                  <p class="text-xl md:text-2xl font-black text-white italic leading-tight uppercase terminal-glow underline decoration-[#A3FF47]/50">오늘 수행한 각성 프로토콜의 <br/>핵심 가치는 무엇입니까?</p>
                </div>
                <div class="p-6 md:p-10 border-l-4 border-[#A3FF47] bg-white/5 space-y-4 md:space-y-6 relative overflow-hidden">
                  <div class="absolute top-0 right-0 p-4 opacity-5">
                    <Shield class="w-16 h-16 md:w-20 md:h-20" />
                  </div>
                  <!-- [2026-02-02] 반응형 폰트 크기 적용 -->
                  <p class="text-[12px] md:text-[13px] font-bold text-slate-300 italic leading-relaxed relative z-10">
                    "Architect는 단순히 버그를 고치는 사람이 아닙니다. 무너진 인공지능 세계의 기초 설계도를 다시 그리는 사람임을 잊지 마십시오."
                  </p>
                </div>
              </div>
            </div>

            <div class="bg-black/40 p-6 md:p-10 lg:px-14 flex flex-col items-start justify-center gap-8 border-l-0 xl:border-l border-[#A3FF47]/10 relative overflow-hidden">
               <div class="w-full max-w-[440px] space-y-6 md:space-y-8">
                 <div class="flex items-center gap-3 opacity-50">
                    <div class="w-1.5 h-1.5 bg-pink-500"></div>
                    <span class="text-[9px] font-black uppercase tracking-[0.4em]">FINAL_ARCHITECT_VERIFICATION</span>
                 </div>
                 
                 <div class="flex flex-col gap-4 md:gap-8 w-full">
                    <button
                    v-for="(opt, i) in step4Options"
                    :key="i"
                    @click="handleStep4Submit(i)"
                      class="group relative p-4 md:p-6 border-2 border-white/5 bg-black/40 hover:border-[#A3FF47] hover:bg-[#A3FF47]/5 transition-all text-left active:scale-95 w-full flex gap-4 md:gap-6"
                    >
                      <!-- [2026-02-02] 반응형 폰트 크기 적용 -->
                      <span class="text-lg md:text-xl font-black text-[#A3FF47]/20 group-hover:text-[#A3FF47] transition-colors font-mono">0{{ i+1 }}</span>
                      <!-- [2026-02-02] 반응형 폰트 크기 적용 -->
                      <span class="text-[12px] md:text-[13px] font-bold text-white/70 group-hover:text-white leading-relaxed">{{ opt }}</span>
                      <div class="absolute bottom-0 right-0 w-3 h-3 md:w-4 md:h-4 border-b-2 border-r-2 border-white/5 group-hover:border-[#A3FF47]"></div>
                    </button>
                 </div>
               </div>
            </div>
          </div>

          <!-- Step 5: 최종 각성 리포트 (Re-Booted) -->
          <!-- [2026-02-02] 패딩 및 콘텐츠 크기 반응형 조절 -->
          <div v-else-if="currentStep === 5" class="flex-1 flex flex-col items-center justify-center p-6 md:p-12 lg:p-20 bg-gradient-to-t from-[#A3FF47]/10 to-transparent overflow-y-auto custom-scrollbar relative">
            <div class="absolute inset-0 opacity-10 pointer-events-none" style="background-image: url('https://www.transparenttextures.com/patterns/carbon-fibre.png');"></div>
            <div class="relative mb-8 md:mb-16 scale-75 md:scale-100">
              <div class="absolute -inset-16 bg-[#A3FF47]/20 blur-[100px] animate-pulse"></div>
              <Award class="w-48 h-48 md:w-64 md:h-64 text-[#A3FF47] drop-shadow-[0_0_50px_rgba(163,255,71,0.8)] relative z-10" />
            </div>
            <h2 class="orbitron-font text-3xl md:text-5xl lg:text-7xl font-black italic tracking-tighter uppercase mb-4 terminal-glow text-center">SECTOR: REBOOTED</h2>
            <div class="h-1 md:h-2 w-48 md:w-96 bg-[#A3FF47] mb-8 md:mb-12 shadow-[0_0_30px_#A3FF47]"></div>
            <p class="text-lg md:text-2xl text-slate-300 max-w-2xl text-center leading-relaxed mb-10 md:mb-16 font-bold italic">
              "축하합니다, {{ userNickname }}님. [{{ currentQuest.title }}] 구역의 정화가 완료되었습니다. Coduck이 다시 세상을 올바르게 보기 시작했습니다."
            </p>
            <div class="grid grid-cols-2 xl:grid-cols-4 gap-4 md:gap-6 w-full max-w-5xl">
              <div v-for="(v, k) in userScore" :key="k" class="p-4 md:p-8 bg-black/60 border-2 border-[#A3FF47]/30 text-center rounded-sm hover:border-[#A3FF47] transition-all">
                <div class="text-[8px] md:text-xs opacity-50 uppercase font-black mb-2 md:mb-3 tracking-widest">{{ k }}_ENGINE</div>
                <div class="text-3xl md:text-5xl font-black text-[#A3FF47] tracking-tighter">{{ v }}</div>
              </div>
            </div>
            <div class="mt-10 md:mt-20 flex flex-wrap justify-center gap-4 md:gap-8 relative z-10 w-full px-4">
              <!-- [수정일: 2026-02-04] 미션 재시작 버튼 -->
              <button @click="reloadApp" class="px-8 md:px-12 py-3 md:py-5 border-2 border-white/20 text-white/60 font-black uppercase text-[10px] md:text-xs hover:border-[#A3FF47] hover:text-[#A3FF47] transition-all tracking-[0.3em] active:scale-95 bg-black/40">
                RETRY MISSION
              </button>

              <!-- [수정일: 2026-02-04] 다음 미션 진행 버튼 (존재할 때만 표시) -->
              <button v-if="hasNextQuest" @click="goToNextQuest" class="px-10 md:px-20 py-4 md:py-6 border-2 border-[#A3FF47] bg-[#A3FF47] text-black font-black uppercase text-xs md:text-sm hover:brightness-110 transition-all tracking-[0.5em] active:scale-95 shadow-[0_0_50px_rgba(163,255,71,0.4)]">
                NEXT MISSION >>
              </button>

              <!-- [수정일: 2026-02-04] 허브(메뉴)로 나가기 버튼 -->
              <button @click="emit('close')" class="px-8 md:px-12 py-3 md:py-5 border-2 border-pink-500/30 text-pink-500/60 font-black uppercase text-[10px] md:text-xs hover:border-pink-500 hover:text-pink-500 transition-all tracking-[0.3em] active:scale-95 bg-black/40">
                EXIT TO HUB
              </button>
            </div>
          </div>

          <!-- 우측 사이드바: 아카이브 & 상태 (2077 스타일) -->
          <!-- [2026-02-03] UX 개선: Layout Fixed & Always Visible on Desktop (lg+) -->
          <div class="hidden lg:flex w-80 border-l border-[#A3FF47]/10 flex-col p-6 space-y-8 bg-black/80 shrink-0 backdrop-blur-sm z-20">
            <div>
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-[10px] font-black opacity-30 uppercase tracking-[0.4em] italic">Recovered Artifacts</h3>
                <Database class="w-4 h-4 opacity-20" />
              </div>
              <div id="tutorial-target-inventory" class="grid grid-cols-2 gap-3">
                <div 
                  v-for="(item, i) in recoveredArtifacts" 
                  :key="i" 
                  @click="currentStep === 3 && insertSnippet(item.code)"
                  class="aspect-square rounded-sm border-2 border-[#A3FF47]/20 flex flex-col items-center justify-center bg-black/40 overflow-hidden relative transition-all duration-300"
                  :class="(currentStep === 3 || tutorialState.isActive) ? 'brightness-100 grayscale-0 shadow-inner' : 'opacity-40 grayscale cursor-not-allowed'"
                >
                  <component :is="icons[item.icon] || icons.Database" class="text-[#A3FF47] w-6 h-6 mb-2 transition-transform" :class="{'group-hover:scale-110': currentStep === 3}" />
                  <span class="text-[8px] font-black uppercase tracking-tighter text-[#A3FF47] text-center px-1">{{ item.label }}</span>
                  
                  <!-- 활성 상태 효과 (Step 3에서만) -->
                  <div v-if="currentStep === 3" class="absolute inset-0 bg-[#A3FF47]/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  
                  <!-- 비활성 상태 잠금 표시 (Step 3도 아니고 튜토리얼도 아닐 때) -->
                  <div v-if="currentStep !== 3 && !tutorialState.isActive" class="absolute inset-0 bg-black/50 flex items-center justify-center backdrop-blur-[1px]">
                     <Lock class="w-4 h-4 text-white/30" />
                  </div>
                </div>
                <!-- Empty Slots Filler -->
                <div v-for="j in (4 - recoveredArtifacts.length)" :key="'empty-'+j" class="aspect-square rounded-sm border-2 border-white/5 flex items-center justify-center bg-white/5 opacity-30">
                   <Lock class="w-5 h-5 opacity-20" />
                </div>
              </div>
            </div>


            <div class="h-px bg-gradient-to-r from-transparent via-[#A3FF47]/20 to-transparent"></div>



            <div class="space-y-6" :class="{'animate-shake': isDamaged}">
              <h3 class="text-[10px] font-black opacity-30 uppercase tracking-[0.4em] italic">Navi-Duck Analysis</h3>
              <div id="tutorial-target-status" class="p-6 bg-[#A3FF47]/5 border-2 rounded-sm flex flex-col gap-6 shadow-xl transition-colors duration-300" :class="[hpState.borderColor, {'bg-red-500/10': isDamaged}]">
                <div class="flex items-center gap-4">
                  <div class="w-16 h-16 bg-[#A3FF47]/10 rounded-full flex items-center justify-center border-2 shadow-[0_0_20px_rgba(163,255,71,0.4)] animate-pulse transition-all duration-500" :class="[hpState.borderColor, hpState.color, {'scale-110 shadow-[0_0_50px_red]': isDamaged}]">
                    <Zap class="w-8 h-8 transition-colors duration-300" :class="hpState.color" />
                  </div>
                  <div>
                    <div class="text-[9px] opacity-40 uppercase font-black tracking-widest leading-none mb-1">NEURAL_SYNC_RATE</div>
                    <div class="text-2xl font-black uppercase tracking-tighter terminal-glow transition-all duration-300" :class="[hpState.color, {'text-shadow-neon': hpState.isCritical, 'text-red-500 scale-110': isDamaged, 'text-[#A3FF47] scale-110': isRepaired}]">{{ hpState.status }} ({{ systemHP }}%)</div>
                  </div>
                </div>
                <div class="bg-black/60 p-4 rounded-sm border border-white/5 relative overflow-hidden">
                  <div v-if="isRepaired" class="absolute inset-0 bg-[#A3FF47]/20 animate-pulse"></div>
                  <p class="text-[10px] font-bold text-slate-400 italic leading-relaxed relative z-10" :class="{'text-red-400': isDamaged}">
                     <span v-if="isDamaged">"경고! 노이즈 발생! 동기화율이 떨어집니다!"</span>
                     <span v-else-if="isRepaired">"신호 증폭! 동기화율이 상승합니다."</span>
                     <span v-else>"현재 동기화율이 {{ systemHP }}%입니다. 100%까지 연결하세요."</span>
                  </p>
                </div>
              </div>
            </div>

            <div class="mt-auto p-5 border-2 border-red-500/20 bg-red-500/5 rounded-sm relative overflow-hidden group transition-all duration-300" :class="{'border-red-500 bg-red-500/20 shadow-[0_0_30px_rgba(239,68,68,0.5)]': isDamaged || hpState.isCritical}">
              <div class="flex items-center gap-3 mb-3 text-red-500">
                <ShieldAlert class="w-4 h-4" :class="{'animate-ping': isDamaged || hpState.isCritical}" />
                <span class="text-[10px] font-black tracking-[0.2em] uppercase">Security Alert</span>
              </div>
              <p class="text-[10px] text-red-400 font-bold leading-normal group-hover:text-red-300 transition-colors">
                데이터 드리프트 현상 감지. 튜토리얼 이후 섹터의 오염도가 임계치를 상회하고 있습니다.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 피드백 모달 (2077 테크니컬 디자인) -->
    <!-- [2026-02-02] 모바일 대응 모달 너비 및 패딩 조절 -->
    <div v-if="feedbackModal.visible" class="fixed inset-0 z-[200] bg-black/95 backdrop-blur-md flex items-center justify-center p-4 md:p-8 transition-all duration-300">
      <div class="max-w-2xl w-full p-8 md:p-16 border-2 bg-[#020406] relative shadow-[0_0_100px_rgba(0,0,0,1)] animate-scale-up" :class="feedbackModal.isSuccess ? 'border-[#A3FF47] shadow-[#A3FF47]/10' : 'border-pink-600 shadow-pink-600/10'">
        <div class="absolute top-0 right-0 p-4 md:p-6 opacity-10">
          <div class="flex gap-2">
            <div v-for="i in 5" :key="i" class="w-1 h-1 bg-white"></div>
          </div>
        </div>
        <div class="flex items-center gap-4 md:gap-8 mb-6 md:mb-10">
          <div :class="feedbackModal.isSuccess ? 'bg-[#A3FF47]/10 border-[#A3FF47]' : 'bg-pink-600/10 border-pink-600'" class="p-3 md:p-5 border-2 rounded-sm shadow-lg">
            <CheckCircle v-if="feedbackModal.isSuccess" class="w-10 h-10 md:w-14 md:h-14 text-[#A3FF47]" />
            <AlertTriangle v-else class="w-10 h-10 md:w-14 md:h-14 text-pink-500" />
          </div>
          <div>
            <h3 class="text-xl md:text-3xl font-black italic tracking-tighter uppercase terminal-text mb-2">{{ feedbackModal.title }}</h3>
            <p class="text-[8px] md:text-[10px] opacity-40 uppercase tracking-[0.5em] font-bold">{{ feedbackModal.isSuccess ? 'ACCESS_GRANTED' : 'ACCESS_DENIED' }}</p>
          </div>
        </div>
        <p class="text-sm md:text-lg font-bold text-slate-200 leading-relaxed mb-8 md:mb-12 italic border-l-4 md:border-l-8 pl-4 md:pl-8 border-white/10">
          {{ feedbackModal.desc }}
        </p>
        <div v-if="feedbackModal.details" class="mb-8 p-4 bg-black/40 border border-[#A3FF47]/20 text-xs text-white/70 overflow-y-auto max-h-[200px] custom-scrollbar" v-html="feedbackModal.details"></div>
        <div class="flex flex-col md:flex-row justify-end gap-4 md:gap-6">
          <button v-if="!feedbackModal.isSuccess" @click="feedbackModal.visible = false" class="px-8 md:px-10 py-3 md:py-4 font-black uppercase text-[10px] md:text-xs tracking-widest btn-neon text-white">RE-TRY SEQUENCE</button>
          <!-- [수정일: 2026-02-04] 단계에 따라 버튼 텍스트 동적 변경 (Step 4 완료 시에는 리포트 확인 안내) -->
          <button @click="nextStep" class="px-10 md:px-12 py-4 md:py-5 font-black uppercase text-[10px] md:text-xs tracking-widest transition-all active:scale-95 shadow-2xl" :class="feedbackModal.isSuccess ? 'bg-[#A3FF47] text-black hover:brightness-110' : 'hidden'">
            {{ currentStep === 4 ? 'VIEW FINAL REPORT >>' : 'EXECUTE NEXT PHASE >>' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 배경 장식 (그리드 & 라이트) -->
    <div class="fixed inset-0 pointer-events-none -z-10">
      <div class="absolute inset-0" style="background-image: radial-gradient(rgba(163, 255, 71, 0.1) 1px, transparent 1px); background-size: 50px 50px; opacity: 0.3;"></div>
      <div class="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[180px] animate-pulse"></div>
      <div class="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-[#A3FF47]/10 rounded-full blur-[150px]"></div>
    </div>
    <!-- [수정일: 2026-02-03] 인게임 튜토리얼 (Spotlight Effect 적용) -->
    <div v-if="tutorialState.isActive" class="fixed inset-0 z-[300] transition-all duration-500">
        <!-- 하이라이트 박스 (스포트라이트 효과: box-shadow를 이용해 주변을 어둡게 처리) -->
        <div 
          class="absolute border-4 border-[#A3FF47] transition-all duration-500 ease-out z-[310] pointer-events-none rounded-sm"
          :style="{
              ...highlightStyle,
              boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.85)'
          }"
        >
             <!-- 코너 장식 -->
             <div class="absolute -top-3 -left-3 w-6 h-6 border-t-4 border-l-4 border-[#A3FF47] bg-transparent shadow-[0_0_15px_#A3FF47]"></div>
             <div class="absolute -bottom-3 -right-3 w-6 h-6 border-b-4 border-r-4 border-[#A3FF47] bg-transparent shadow-[0_0_15px_#A3FF47]"></div>
             <div class="absolute inset-0 shadow-[inset_0_0_50px_rgba(163,255,71,0.2)]"></div>
        </div>

        <!-- 설명 모달 (하이라이트 근처 또는 중앙 하단 고정) -->
        <div class="absolute bottom-10 left-1/2 -translate-x-1/2 w-full max-w-3xl p-6 z-[320]">
             <div class="bg-black/95 border-2 border-[#A3FF47] p-8 relative shadow-[0_0_100px_rgba(0,0,0,0.8)] animate-fade-in-up">
                 <div class="flex items-start gap-6">
                     <!-- 튜토리얼 단계 표시 -->
                     <div class="flex flex-col items-center gap-2">
                         <div class="w-16 h-16 rounded-full border-2 border-[#A3FF47] flex items-center justify-center bg-[#A3FF47]/10 shadow-[0_0_20px_#A3FF47]">
                             <span class="text-2xl font-black text-[#A3FF47]">{{ tutorialState.currentStep + 1 }}</span>
                             <span class="text-xs text-[#A3FF47]/50">/{{ tutorialSteps.length }}</span>
                         </div>
                     </div>
                     
                     <div class="flex-1 space-y-4">
                         <h3 class="text-xl font-black text-[#A3FF47] uppercase tracking-widest italic terminal-glow border-b border-[#A3FF47]/30 pb-2">
                             {{ tutorialSteps[tutorialState.currentStep].stage }}
                         </h3>
                         <p class="text-lg text-white/90 leading-relaxed font-bold whitespace-pre-wrap">
                             {{ tutorialSteps[tutorialState.currentStep].desc }}
                         </p>
                     </div>
                 </div>

                 <!-- 컨트롤 버튼 -->
                 <div class="mt-8 flex justify-end gap-4">
                     <button @click="skipTutorial" class="px-6 py-3 text-xs font-bold text-gray-500 hover:text-white uppercase tracking-widest transition-colors">
                         SKIP TUTORIAL
                     </button>
                     <button @click="nextTutorialStep" class="px-10 py-3 bg-[#A3FF47] text-black font-black uppercase text-sm tracking-widest hover:bg-[#b4ff6a] transition-all shadow-[0_0_20px_rgba(163,255,71,0.4)] active:scale-95">
                         {{ tutorialState.currentStep === tutorialSteps.length - 1 ? 'Start Mission' : 'Next Step >>' }}
                     </button>
                 </div>
             </div>
        </div>
    </div>
  </div>
</template>

<script setup>
/**
 * [수정일: 2026-02-03]
 * [수정내용:
 * 1. 하드코딩된 questData 제거 및 stages.js 데이터 단일화
 * 2. 모든 상태(ref, reactive)와 비즈니스 로직을 pseudoProblemLogic.js(usePseudoProblem)로 이관
 * 3. 컴포넌트는 UI 렌더링과 composable 호출에만 집중하도록 리팩토링]
 */
import { ref, reactive, onMounted, watch, onUnmounted, nextTick, computed } from 'vue'
import {
  X, Send, Layout, Cpu, Database, Binary, Shield, 
  ChevronRight, RefreshCw, BarChart3, HelpCircle, 
  Terminal, Play, CheckCircle2, AlertCircle, 
  ChevronLeft, ArrowRight, Code, MessageSquare, 
  Zap, Brain, Lock, Volume2, VolumeX, SkipForward,
  PlayCircle, MoreHorizontal, Info, ShieldAlert, Award, CheckCircle, AlertTriangle,
  Wifi, Activity, ArrowUp, Target, Plus, Square, Compass, Scissors, Shuffle, Repeat, Download, Pause, RotateCcw,
  Check as CheckIcon, Filter, PlusCircle // Cleaned up distinct imports
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { usePseudoProblem } from './pseudoProblemLogic'
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'


// [수정일: 2026-02-03] 동적 아이콘 매핑을 위한 객체
const icons = {
  ArrowUp,
  Target,
  Plus,
  Stop: Square,
  Compass,
  Scissors,
  Check: CheckIcon,
  Filter,
  Zap,
  Shuffle,
  Repeat,
  Download,
  SkipForward,
  PlusCircle,
  Database,
  Lock,
  Terminal,
  Play,
  Pause,
  RotateCcw,
  Cpu,
  Shield,
  ShieldAlert,
  Activity,
  Code
}

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])

const authStore = useAuthStore()
const userNickname = computed(() => authStore.sessionNickname || 'ENGINEER')

// [수정일: 2026-02-03] 모든 로직과 상태를 Composable에서 가져옴
const {
  currentQuest,
  currentStep,
  userScore,
  pseudoInput,
  pythonInput,
  chatMessages,
  chatContainer,
  simulationContainer,
  isSimulating,
  // isEvaluating, // [수정일: 2026-02-04] 현재 템플릿 미사용
  isAsking,
  currentInterviewIdx,
  currentInterviewQuestion,
  // interviewResults, // [수정일: 2026-02-04] 현재 템플릿 미사용
  step4Options,
  feedbackModal,
  editorOptions,
  // finalReviewText, // [수정일: 2026-02-04] 현재 템플릿 미사용
  handleStep1Submit,
  submitStep2,
  // selectBlock, // [수정일: 2026-02-04] 구 버전(블록코딩) 잔재
  runSimulation,
  handleStep4Submit,
  nextStep,
  // goToStep, // [수정일: 2026-02-04] 내부 로직으로 대체
  reloadApp,
  goToNextQuest,
  hasNextQuest,
  insertSnippet,
  askCoduck,
  // aiQuests, // [수정일: 2026-02-04] 현재 템플릿 미사용
  // currentQuestIdx, // [수정일: 2026-02-04] 현재 템플릿 미사용
  imageSrc,
  // currentDuckImage, // [수정일: 2026-02-04] imageSrc 내부 사용으로 대체
  isMuted,
  toggleMute,
  // synopsisText, // [수정일: 2026-02-04] Logic 내부 사용으로 충분
  skipSynopsis,
  isPlayingBGM,
  initAudio,
  cleanupAudio,
  integrity,
  recoveredArtifacts,
  // [수정일: 2026-02-04] 게이트키퍼 필수 상태 (미사용 항목 주석)
  // isConsulted, 
  // [수정일: 2026-02-04] 인터뷰 기반 설계 요구사항(activeRequirements) 추가
  activeRequirements,
  isApproved,
  hpState,
  // pseudoChecklist, // [수정일: 2026-02-04] 현재 템플릿 미사용
  systemHP,
  isDamaged,
  isRepaired,
  // [수정일: 2026-02-03] 튜토리얼
  tutorialState,
  tutorialSteps,
  nextTutorialStep,
  skipTutorial
} = usePseudoProblem(props, emit)

// [수정일: 2026-02-03] 튜토리얼 하이라이트 위치 계산 로직
const highlightStyle = reactive({ top: '0px', left: '0px', width: '0px', height: '0px' })

const updateHighlightPosition = () => {
    if (!tutorialState.isActive) return
    
    // [수정일: 2026-02-04] 튜토리얼 비활성화 시(ID 2+) 에러 방지를 위해 요소 존재 여부 체크
    if (!tutorialSteps.value || tutorialSteps.value.length === 0 || !tutorialSteps.value[tutorialState.currentStep]) return
    
    const targetId = tutorialSteps.value[tutorialState.currentStep].targetId
    const el = document.getElementById(targetId)
    
    if (el) {
        const rect = el.getBoundingClientRect()
        // 약간의 여백(padding)을 주어 박스를 그림
        const padding = 10
        highlightStyle.top = `${rect.top - padding}px`
        highlightStyle.left = `${rect.left - padding}px`
        highlightStyle.width = `${rect.width + (padding * 2)}px`
        highlightStyle.height = `${rect.height + (padding * 2)}px`
    }
}

// 튜토리얼 스텝이 바뀌거나 활성화될 때 위치 재계산
watch(() => [tutorialState.currentStep, tutorialState.isActive], async () => {
    if (tutorialState.isActive) {
        await nextTick()
        // 애니메이션 효과를 위해 약간 지연 후 계산
        setTimeout(updateHighlightPosition, 100)
    }
}, { immediate: true })

// 창 크기가 바뀔 때도 재계산
onMounted(() => {
    window.addEventListener('resize', updateHighlightPosition)
    if (currentStep.value === 0) {
      initAudio()
    }
})

onUnmounted(() => {
    window.removeEventListener('resize', updateHighlightPosition)
    cleanupAudio()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;900&display=swap');

body {
  font-family: 'Fira Code', monospace;
  background-color: #05070A;
  color: #A3FF47;
  margin: 0;
  overflow: hidden;
}

.orbitron-font {
  font-family: 'Orbitron', sans-serif;
}

/* Glitch & CRT Effects */
.glitch-bg {
  position: relative;
  overflow: hidden;
}
.glitch-bg::before {
  content: " ";
  display: block;
  position: absolute;
  top: 0; left: 0; bottom: 0; right: 0;
  background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
  z-index: 100;
  background-size: 100% 2px, 3px 100%;
  pointer-events: none;
}

/* Star Wars Crawl Styles */
.perspective-container {
  perspective: 400px;
  height: 100%;
  overflow: hidden;
  position: relative;
}
.crawl-content {
  transform: rotateX(25deg);
  position: absolute;
  top: 100%;
  width: 100%;
  text-align: center;
  transform-origin: 50% 0%;
}
/* [2026-02-02] 반응형 폰트 크기 및 레이아웃 조절 */
.crawl-title {
  font-family: 'Orbitron', sans-serif;
  font-size: clamp(2rem, 8vw, 4.5rem);
  font-weight: 900;
  margin-bottom: 2rem;
  text-transform: uppercase;
  letter-spacing: -0.05em;
}
.crawl-body {
  font-size: clamp(1rem, 4vw, 1.875rem);
  font-weight: 700;
  line-height: 1.5;
  padding: 0 2rem;
  text-align: justify;
  font-style: italic;
}
.crawl-body p {
  margin-bottom: 3rem;
}
@keyframes crawl {
  0% { top: 120%; }
  100% { top: -3000px; }
}
.animate-crawl {
  animation: crawl 45s linear forwards;
}

/* Star Wars UI Legacy Effects */
.perspective-container {
  perspective: 300px;
  overflow: hidden;
  mask-image: linear-gradient(to bottom, transparent, black 30%, black 80%, transparent);
}
.prelude-text {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'Fira Code', monospace;
  font-size: 24px;
  font-weight: 700;
  color: #A3FF47;
  opacity: 0;
  white-space: nowrap;
  text-align: center;
  line-height: 1.6;
}
@keyframes fadeOut { 0% { opacity: 0; } 10%, 80% { opacity: 1; } 100% { opacity: 0; } }
.animate-fade-out { animation: fadeOut 4s ease-in-out forwards; }

.crawl-container { position: relative; width: 100%; height: 100%; }
.crawl-content { position: absolute; top: 100%; width: 100%; transform-origin: 50% 100%; transform: rotateX(25deg); opacity: 1; }
/* [2026-02-02] 반응형 폰트 크기 적용 */
.crawl-title { font-size: clamp(32px, 8vw, 72px); font-weight: 900; color: #A3FF47; text-align: center; margin-bottom: 40px; letter-spacing: 0.1em; text-transform: uppercase; font-family: 'Fira Code', monospace; }
.crawl-body { font-size: clamp(16px, 3vw, 28px); font-weight: 700; color: #A3FF47; text-align: justify; line-height: 1.6; padding: 0 10%; font-family: 'Fira Code', monospace; }

/* Terminal Glow */
.terminal-glow {
  text-shadow: 0 0 10px rgba(163, 255, 71, 0.7);
}

.terminal-text {
  text-shadow: 0 0 20px rgba(163,255,71,0.8), 0 0 5px rgba(163,255,71,0.4);
}

.scanline {
  background: linear-gradient(to bottom, transparent 50%, rgba(163,255,71,0.1) 50%);
  background-size: 100% 4px;
}

/* HUD & OS Aesthetic */
.btn-neon {
  background: rgba(163, 255, 71, 0.05);
  border: 1px solid rgba(163, 255, 71, 0.3);
  transition: all 0.3s ease;
}
.btn-neon:hover {
  background: rgba(163, 255, 71, 0.2);
  box-shadow: 0 0 20px rgba(163, 255, 71, 0.4);
  transform: translateY(-2px);
}

/* Scrollbar Custom */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(163, 255, 71, 0.2);
  border-radius: 10px;
}

/* Boot Sequence Animation */
@keyframes flicker {
  0% { opacity: 0.1; }
  5% { opacity: 0.7; }
  10% { opacity: 0.3; }
  15% { opacity: 0.9; }
  100% { opacity: 1; }
}
.boot-screen {
  animation: flicker 0.5s ease-in;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes scaleUp {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}
.animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
}
.animate-scale-up {
  animation: scaleUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.animate-shake {
  animation: shake 0.2s cubic-bezier(.36,.07,.19,.97) both infinite;
}

.damage-flash {
  animation: damageFlash 0.5s ease-out;
}

@keyframes damageFlash {
  0% { box-shadow: inset 0 0 100px rgba(239, 68, 68, 0.8); }
  100% { box-shadow: none; }
}

.scale-up-center {
    animation: scale-up-center 0.4s cubic-bezier(0.390, 0.575, 0.565, 1.000) both;
}

@keyframes scale-up-center {
  0% { transform: scale(0.5); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.animate-width-expand {
    animation: width-expand 0.6s ease-out forwards;
}

@keyframes width-expand {
    0% { width: 0; opacity: 0; }
    100% { width: 100%; opacity: 1; }
}
</style>