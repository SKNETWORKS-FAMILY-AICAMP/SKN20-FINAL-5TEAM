<template>
  <!-- [수정일: 2026-01-31] 전역 모달(z-index 1000)보다 위에 오도록 z-index를 z-[2000]으로 상향 조정 -->
  <div v-if="isOpen" class="fixed inset-0 z-[2000] flex items-center justify-center md:p-4 bg-black/60 backdrop-blur-sm animate-fade-in" @click.self="$emit('close')">
    
    <!-- [수정일: 2026-02-01] Step 0: Star Wars Synopsis Crawl (모달 상자가 아닌 전체 화면을 덮도록 설정) -->
    <div v-if="currentStep === 0" class="fixed inset-0 z-[2100] flex flex-col items-center justify-center bg-black overflow-hidden select-none">
      <!-- [수정일: 2026-02-01] 배경 동영상 도입 (coduck_wars.mp4) -->
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
      <div class="relative w-full max-w-4xl h-full flex flex-col items-center text-center perspective-container">
        <!-- Prelude Text (Blue Fade) -->
        <div class="prelude-text animate-fade-out" :style="{ animationDelay: '1s' }">
          {{ synopsisText.top }}
        </div>

        <!-- Logo Zoom Stage -->
        <div class="intro-logo animate-logo-zoom" :style="{ animationDelay: '9s' }">
          PROJECT:<br/>RE-BOOT
        </div>

        <!-- Crawling Content -->
        <div class="crawl-container">
          <div class="crawl-content animate-crawl" :style="{ animationDelay: '12s' }">
            <h1 class="crawl-title">{{ synopsisText.bottom }}</h1>
            <div class="crawl-body" v-html="synopsisText.main.join('<br/><br/>')"></div>
          </div>
        </div>
      </div>
      <!-- Interaction UI -->
      <div class="absolute bottom-12 right-12 z-[100] flex gap-6 items-center">
        <div v-if="isPlayingBGM" class="flex items-center gap-3 px-4 py-2 bg-cyan-500/10 border border-cyan-500/30 rounded-full animate-pulse transition-all">
          <Volume2 class="w-4 h-4 text-cyan-400" />
          <span class="text-[10px] font-mono text-cyan-400 font-bold tracking-[0.4em] uppercase italic">Audio_Link_Synced</span>
        </div>
        <button @click="$emit('close')" class="group relative px-8 py-4 bg-red-500/5 hover:bg-red-500/10 text-red-500/60 border border-red-500/20 transition-all active:scale-95 overflow-hidden">
            <span class="relative z-10 font-black text-[10px] tracking-[0.4em] uppercase italic">ABORT_MISSION (EXIT)</span>
            <div class="absolute inset-x-0 bottom-0 h-[1px] bg-red-500 shadow-[0_0_15px_red] scale-x-0 group-hover:scale-x-100 transition-transform origin-center"></div>
        </button>
        <button @click="skipSynopsis" class="group relative px-10 py-4 bg-white/5 hover:bg-white/10 text-white border border-white/20 transition-all active:scale-95 hud-button-clip overflow-hidden">
            <span class="relative z-10 font-black text-xs tracking-[0.3em] uppercase italic">RE-BOOT_PROTOCOL (SKIP)</span>
            <div class="absolute inset-x-0 bottom-0 h-[2px] bg-cyan-500 shadow-[0_0_10px_#00f3ff] scale-x-0 group-hover:scale-x-100 transition-transform origin-center"></div>
        </button>
      </div>
    </div>

    <!-- [수정일: 2026-02-02] Platinum HUD Global Container -->
    <div class="platinum-hud-root w-full h-full relative overflow-hidden flex flex-col font-mono selection:bg-[#A3FF47]/30 selection:text-white">
      
      <!-- Layer 0: Deep Background & Technical Grid -->
      <div class="absolute inset-0 bg-[#020508] z-0">
          <div class="absolute inset-0 dot-grid opacity-20"></div>
          <div class="absolute inset-0 scanline-overlay opacity-30"></div>
          <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-black/40"></div>
      </div>

      <!-- Layer 1: Floating Navigation HUD -->
      <aside class="absolute left-8 inset-y-0 flex flex-col items-center justify-center gap-12 z-50 pointer-events-none">
          <div class="w-px h-24 bg-gradient-to-b from-transparent via-[#A3FF47]/20 to-transparent"></div>
          <div class="flex flex-col gap-10 pointer-events-auto">
              <div v-for="i in 4" :key="'nav-'+i" 
                  @click="currentStep >= i && goToStep(i)"
                  class="relative group cursor-pointer transition-all duration-500"
                  :class="[
                      currentStep === i ? 'scale-110 shadow-neon' : 'opacity-20 hover:opacity-100',
                      currentStep < i ? 'cursor-not-allowed grayscale' : ''
                  ]"
              >
                  <!-- Hexagonal Indicator Shape -->
                  <div class="w-12 h-12 flex items-center justify-center border-2 transition-all p-1"
                      :class="currentStep === i ? 'border-[#A3FF47] bg-[#A3FF47]/10' : 'border-[#A3FF47]/20 bg-black/40'"
                      style="clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);"
                  >
                      <span class="text-[10px] font-black" :class="currentStep === i ? 'text-[#A3FF47]' : 'text-white/40'">0{{ i }}</span>
                  </div>
                  <!-- Tooltip Labeled with Vertical Text -->
                  <div class="absolute left-16 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                      <span class="text-[8px] font-black text-[#A3FF47] tracking-[0.4em] uppercase">PHASE_CONNECTED_0{{ i }}</span>
                  </div>
              </div>
          </div>
          <div class="w-px h-24 bg-gradient-to-t from-transparent via-[#A3FF47]/20 to-transparent"></div>
      </aside>

      <!-- Layer 2: Main Operational View -->
      <div class="flex-1 flex flex-col z-10 relative overflow-hidden">
          
          <!-- [DEBUG_REVERT] Simplified Header -->
          <nav class="flex items-center justify-between h-20 mb-6 px-10 shrink-0 border-b border-[#A3FF47]/10 bg-black/40 backdrop-blur-md relative">
              <div class="flex items-center gap-6">
                  <div class="p-2 border border-[#A3FF47]/30 bg-[#A3FF47]/5">
                      <Cpu class="w-5 h-5 text-[#A3FF47]" />
                  </div>
                  <div class="flex flex-col">
                      <h1 class="text-2xl font-black italic text-[#A3FF47] leading-none mb-1">Chapter 1: 각성</h1>
                      <span class="text-sm font-black italic text-[#A3FF47]/60 leading-none">(Tutorial)</span>
                  </div>
              </div>

              <div class="flex items-center gap-12">
                  <div class="flex items-center gap-3 px-4 py-2 border border-[#A3FF47]/10 bg-white/5 rounded-sm">
                      <span class="text-[9px] font-bold text-[#A3FF47]/30 tracking-widest mr-3">ARCHITECT:</span>
                      <span class="text-[12px] font-black text-[#A3FF47] uppercase">{{ userNickname }}</span>
                  </div>
                  <div class="flex items-center gap-3">
                      <button @click="toggleMute" class="w-10 h-10 flex items-center justify-center rounded-full border border-[#A3FF47]/20 bg-black/40">
                          <Volume2 v-if="!isMuted" class="w-5 h-5 text-[#A3FF47]" />
                          <VolumeX v-else class="w-5 h-5 text-red-500" />
                      </button>
                      <button @click="handlePracticeClose" class="w-10 h-10 flex items-center justify-center rounded-full border border-red-500/20 bg-black/40">
                          <X class="w-5 h-5 text-red-500" />
                      </button>
                  </div>
              </div>
          </nav>

          <!-- Unified HUD Content Layout (Workspace + Sidebar) -->
          <div class="flex-1 flex min-h-0 relative px-10 pb-10 gap-8 overflow-hidden">
              
              <!-- [수정일: 2026-02-02] 중복된 Workspace Core와 가변 콘텐츠 래퍼들을 모두 제거하고 하나의 레이어로 통합 -->
              <div class="flex-1 relative flex flex-col min-h-0 bg-black/10 border border-white/[0.03] overflow-hidden rounded-sm transition-all duration-500">
                <!-- Precision Corner Brackets (Unified) -->
                <div class="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-[#A3FF47]/20 pointer-events-none z-20"></div>
                <div class="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-[#A3FF47]/20 pointer-events-none z-20"></div>
                <div class="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-[#A3FF47]/20 pointer-events-none z-20"></div>
                <div class="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-[#A3FF47]/20 pointer-events-none z-20"></div>

                <!-- STAGE 1: Neural Sync Interface -->
                <div v-if="currentStep === 1" class="flex-1 flex flex-col animate-scale-up relative">
                    <!-- Central Neural Core -->
                    <div class="flex-1 flex flex-col items-center justify-center p-12 space-y-12">
                        <!-- Floating Character HUD -->
                        <div class="relative w-80 h-80 flex items-center justify-center">
                            <!-- Tactical Orbitals -->
                            <div class="absolute inset-0 border-2 border-[#A3FF47]/5 rounded-full animate-[spin_20s_linear_infinite]"></div>
                            <div class="absolute inset-8 border border-[#A3FF47]/10 rounded-full animate-[spin_10s_linear_infinite_reverse]"></div>
                            <div class="absolute inset-0 rounded-full border-t-4 border-[#A3FF47] shadow-[0_0_30px_#A3FF47] opacity-20 animate-pulse"></div>
                            
                            <!-- Character Sphere -->
                            <div class="w-64 h-64 rounded-full border-2 border-[#A3FF47] p-2 bg-black/80 shadow-[0_0_80px_rgba(163,255,71,0.2)] overflow-hidden relative group">
                                <img :src="imageSrc" alt="Coduck" class="w-full h-full object-cover rounded-full grayscale group-hover:grayscale-0 transition-all duration-700" />
                                <div class="absolute inset-0 bg-gradient-to-t from-[#A3FF47]/20 to-transparent pointer-events-none"></div>
                            </div>

                            <!-- Data Points Around Circle -->
                            <div v-for="i in 8" :key="'dot-'+i" 
                                 class="absolute w-1.5 h-1.5 bg-[#A3FF47] rounded-full shadow-[0_0_10px_#A3FF47]"
                                 :style="{ transform: `rotate(${i * 45}deg) translateY(-160px)` }"
                            ></div>
                        </div>

                        <!-- Neural Dialog HUD -->
                        <div class="w-full max-w-2xl flex flex-col items-center space-y-8 bg-black/40 p-10 border-y border-[#A3FF47]/10 relative">
                            <div class="flex items-center gap-4">
                                <span class="text-[10px] font-black text-[#A3FF47]/40 tracking-[1em] uppercase">NEURAL_SYNC_SEQUENCE</span>
                            </div>
                            <h2 class="text-3xl lg:text-4xl font-black text-center terminal-text leading-tight px-12">
                                "{{ currentInterviewQuestion?.question || 'SYSTEM: WAITING_FOR_UPLINK...' }}"
                            </h2>
                            <div class="flex items-center gap-2">
                                <span class="w-2 h-2 bg-[#A3FF47] animate-ping rounded-full"></span>
                                <p class="text-[10px] font-bold text-[#A3FF47]/60 italic tracking-widest uppercase">Decide_Protocol_Path_Via_HUD_Selection</p>
                            </div>
                        </div>
                    </div>

                    <!-- HUD Selection Grid (Bottom Layer) -->
                    <div v-if="currentInterviewQuestion" class="px-12 pb-12 shrink-0 relative transition-all duration-700">
                        <!-- [수정일: 2026-02-02] 객관식 그리드를 중앙 HUD 너비(max-w-2xl)에 맞춤 -->
                        <div class="max-w-2xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
                            <button 
                                v-for="(opt, i) in currentInterviewQuestion?.options" 
                                :key="i" 
                                @click="handleStep1Submit(opt)"
                                class="p-8 border border-[#A3FF47]/20 bg-black/40 hover:bg-[#A3FF47]/10 hover:border-[#A3FF47] transition-all text-left group relative overflow-hidden"
                            >
                                <div class="absolute top-0 left-0 w-1 h-full bg-[#A3FF47] scale-y-0 group-hover:scale-y-100 transition-transform duration-500"></div>
                                <div class="flex justify-between items-start mb-6">
                                    <span class="text-[9px] font-black text-[#A3FF47]/30 tracking-[0.4em] uppercase font-mono">OPT.IDX_0{{ i+1 }}</span>
                                    <ChevronRight class="w-4 h-4 opacity-0 group-hover:opacity-100 group-hover:translate-x-2 transition-all" />
                                </div>
                                <span class="text-xl font-black text-[#A3FF47] group-hover:text-white transition-colors leading-tight">{{ opt.text }}</span>
                                <!-- Glow pulse on hover -->
                                <div class="absolute inset-0 bg-[#A3FF47]/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- STAGE 2: Architect Workspace (Code Logic Synthesis) -->
                <!-- [2026-02-02] Phase 1과 구성을 완전히 통일 (grid-cols-2) -->
                <div v-if="currentStep === 2" class="flex-1 grid grid-cols-2 bg-black overflow-hidden animate-fade-in relative transition-all duration-700">
                    <!-- Left column: Mission Objective and Metadata -->
                    <div class="p-8 flex flex-col items-center justify-center gap-5 overflow-y-auto custom-scrollbar relative">
                        <div class="w-full max-w-[320px] space-y-8">
                            <div class="space-y-4">
                                <div class="flex items-center gap-3">
                                  <div class="h-4 w-1 bg-[#A3FF47]"></div>
                                  <h3 class="text-xs font-black tracking-[0.4em] uppercase">Mission Objective</h3>
                                </div>
                                <p class="text-xl font-black italic terminal-glow underline decoration-[#A3FF47]/30">{{ currentQuest.briefingTitle || 'MISSION_BRIEFING' }}</p>
                                <div class="p-6 bg-[#A3FF47]/5 border-l-2 border-[#A3FF47] text-sm leading-relaxed italic text-slate-300 space-y-3">
                                  <p>{{ currentQuest.briefingText }}</p>
                                  <div class="pt-2 border-t border-[#A3FF47]/20">
                                    <span class="text-[9px] font-black uppercase tracking-[0.3em] opacity-40 italic">System_Directive: 의사코드(Pseudocode)로 작성하십시오</span>
                                  </div>
                                </div>
                            </div>

                            <div class="space-y-6">
                                <div v-for="(obj, i) in currentQuest.objectives" :key="i" class="flex items-start gap-4 p-4 bg-white/5 border border-white/5 hover:border-[#A3FF47]/30 transition-all group">
                                    <span class="text-[10px] font-mono text-[#A3FF47]/30 mt-1">0{{ i + 1 }}</span>
                                    <p class="text-[11px] font-bold text-slate-400 group-hover:text-white transition-colors uppercase tracking-wider italic leading-relaxed">{{ obj }}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Right column: Architect Terminal with Monaco Editor -->
                    <div class="bg-black/40 p-10 px-14 flex flex-col items-start justify-center gap-8 border-l border-[#A3FF47]/10 relative overflow-hidden">
                        <div class="w-full h-full flex flex-col">
                          <div class="flex items-center justify-between mb-4 opacity-50">
                              <div class="flex items-center gap-3">
                                  <Terminal class="w-4 h-4" />
                                  <span class="text-[10px] font-black uppercase tracking-[0.5em]">LOGIC_SYNTHESIZER_v4.0</span>
                              </div>
                              <div class="flex items-center gap-4">
                                  <div class="flex gap-1">
                                      <div v-for="i in 3" :key="i" class="w-1 h-1 bg-[#A3FF47] rounded-full animate-pulse"></div>
                                  </div>
                                  <span class="text-[8px] font-mono">ENCRYPTED_SIGNAL</span>
                              </div>
                          </div>
                          
                          <div class="flex-1 relative">
                            <VueMonacoEditor
                              v-model:value="pseudoInput"
                              theme="vs-dark"
                              language="markdown"
                              :options="editorOptions"
                              class="h-full"
                            />
                            <!-- Decorative Corner -->
                            <div class="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-[#A3FF47]/20 pointer-events-none"></div>
                          </div>

                          <div class="mt-8 flex gap-6 shrink-0">
                            <button @click="askCoduck" :disabled="isAsking" class="px-8 py-4 border border-[#A3FF47]/20 text-[#A3FF47] font-black uppercase text-[10px] tracking-widest hover:bg-[#A3FF47]/10 transition-all flex items-center gap-3 group relative overflow-hidden">
                                <Cpu class="w-4 h-4 group-hover:rotate-12 transition-transform" /> {{ isAsking ? 'ANALYZING...' : 'Consult_Coduck' }}
                            </button>
                            <button @click="submitStep2" class="flex-1 py-4 bg-[#A3FF47] text-black font-black uppercase text-[10px] tracking-[0.4em] shadow-[0_0_30px_rgba(163,255,71,0.3)] hover:shadow-[0_0_50px_rgba(163,255,71,0.5)] transition-all active:scale-95">Commit_Architect_Logic</button>
                          </div>
                        </div>
                    </div>
                </div>

                <!-- STAGE 3: Python Build (Project Core Uplink) -->
                <!-- [2026-02-02] Phase 1과 구성을 완전히 통일 (grid-cols-2) -->
                <div v-if="currentStep === 3" class="flex-1 grid grid-cols-2 overflow-hidden bg-black animate-fade-in relative text-[#A3FF47]">
                    <!-- Left column: Python Code Editor -->
                    <div class="flex-1 flex flex-col overflow-hidden relative border-r border-white/5">
                        <div class="h-12 border-b border-white/5 flex items-center justify-between px-10 bg-black/40">
                            <div class="flex items-center gap-4">
                                <CodeIcon class="w-4 h-4 text-[#A3FF47]/60" />
                                <span class="text-[10px] font-black tracking-[0.4em] uppercase italic">UPLINK_STREAM::REBOOT_CORE.py</span>
                            </div>
                            <div class="flex items-center gap-3">
                                <div class="w-2 h-2 rounded-full bg-[#A3FF47] animate-ping"></div>
                                <span class="text-[8px] font-black opacity-30 uppercase">ENCRYPTED_SIGNAL</span>
                            </div>
                        </div>
                        
                        <div class="flex-1 p-10 relative">
                            <VueMonacoEditor
                                v-model:value="pythonInput"
                                theme="vs-dark"
                                language="python"
                                :options="{ ...editorOptions, fontSize: 13 }"
                                class="h-full"
                            />
                        </div>

                        <div class="p-10 border-t border-white/5 bg-black/60 flex justify-end gap-6 shrink-0">
                            <button @click="goToStep(2)" class="px-8 py-4 border border-[#A3FF47]/20 text-[#A3FF47]/40 font-black uppercase text-[10px] tracking-widest hover:bg-[#A3FF47]/5 transition-all">Previous_Node</button>
                            <button @click="runSimulation" :disabled="isSimulating" class="px-14 py-4 bg-[#A3FF47] text-black font-black uppercase text-[10px] tracking-widest shadow-[0_0_30px_#A3FF47] transition-all active:scale-95">Initiate_Sandbox_Uplink</button>
                        </div>
                    </div>

                    <!-- Right column: Simulation Output -->
                    <div class="bg-black/40 flex flex-col gap-6 overflow-hidden p-10 px-14 border-l border-[#A3FF47]/10">
                        <div class="flex items-center justify-between shrink-0">
                          <div class="flex items-center gap-4">
                              <Terminal class="w-4 h-4 text-[#A3FF47]/60" />
                              <h3 class="text-[10px] font-black tracking-[0.5em] uppercase italic opacity-50">Simulation_Telemetry</h3>
                          </div>
                          <span class="text-[8px] font-mono opacity-20 italic">REALTIME_DATA_FLOW</span>
                        </div>
                        <div class="flex-1 bg-black/80 border border-white/5 p-8 font-mono text-xs overflow-y-auto custom-scrollbar leading-relaxed">
                            <div v-html="simulationOutput || 'WAITING_FOR_SIGNAL_EXECUTION...'" class="opacity-80"></div>
                        </div>
                        <div class="space-y-4">
                            <h4 class="text-[9px] font-black uppercase tracking-[0.4em] opacity-30 italic">Available_Code_Shards</h4>
                            <div class="grid grid-cols-1 gap-3">
                                <button v-for="snippet in currentQuest.codeSnippets" :key="snippet.label"
                                    @click="insertSnippet(snippet.code)"
                                    class="p-4 border border-[#A3FF47]/10 bg-white/[0.02] hover:bg-[#A3FF47]/10 transition-all text-left flex items-center justify-between group"
                                >
                                    <span class="text-[9px] font-black opacity-30 group-hover:opacity-100 uppercase tracking-widest">{{ snippet.label }}</span>
                                    <Plus class="w-3 h-3 opacity-10 group-hover:opacity-100" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- STAGE 4: Deep Analysis Hub (Tactical Briefing Grid) -->
                <!-- [2026-02-02] Phase 1과 구성을 완전히 통일 (grid-cols-2) -->
                <div v-if="currentStep === 4" class="flex-1 grid grid-cols-2 bg-black overflow-hidden relative animate-scale-up text-[#A3FF47]">
                    <!-- Left column: Question and supporting text -->
                    <div class="p-8 flex flex-col items-center justify-center gap-12 overflow-y-auto custom-scrollbar relative bg-black">
                      <div class="w-[320px] space-y-8">
                        <div class="space-y-6 text-center">
                          <h3 class="text-pink-500 font-black text-xs uppercase tracking-[0.5em] animate-pulse">Final System Clearance</h3>
                          <p class="text-2xl font-black text-white italic leading-tight uppercase terminal-glow underline decoration-[#A3FF47]/50">{{ currentQuest.quizTitle || currentQuest.step4Title }}</p>
                        </div>
                        <div class="p-10 border-l-4 border-[#A3FF47] bg-white/5 space-y-6 relative overflow-hidden">
                          <div class="absolute top-0 right-0 p-4 opacity-5">
                            <Shield class="w-20 h-20" />
                          </div>
                          <p class="text-[13px] font-bold text-slate-300 italic leading-relaxed relative z-10">
                            {{ currentQuest.step4Desc }}
                          </p>
                        </div>
                      </div>
                    </div>

                    <!-- Right column: Tactical Response Grid -->
                    <div class="bg-black/40 p-10 px-14 flex flex-col items-start justify-center gap-8 border-l border-[#A3FF47]/10 relative overflow-hidden">
                       <div class="w-full max-w-[440px] space-y-8">
                         <div class="flex items-center gap-3 opacity-50">
                            <div class="w-1.5 h-1.5 bg-pink-500"></div>
                            <span class="text-[9px] font-black uppercase tracking-[0.4em]">FINAL_ARCHITECT_VERIFICATION</span>
                         </div>
                         
                         <div class="flex flex-col gap-8 w-full">
                            <button
                              v-for="(opt, i) in step4Options"
                              :key="i"
                              @click="handleStep4Submit(i)"
                              class="group relative p-6 border-2 border-white/5 bg-black/40 hover:border-[#A3FF47] hover:bg-[#A3FF47]/5 transition-all text-left active:scale-95 w-full flex gap-6"
                            >
                              <span class="text-xl font-black text-[#A3FF47]/20 group-hover:text-[#A3FF47] transition-colors font-mono">0{{ i+1 }}</span>
                              <span class="text-[13px] font-bold text-white/70 group-hover:text-white leading-relaxed">{{ opt.text || opt }}</span>
                              <div class="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-white/5 group-hover:border-[#A3FF47]"></div>
                            </button>
                         </div>
                       </div>
                    </div>
                </div>

                <!-- STAGE 5: Final Evaluation (Sector Sanitized Report) -->
                <div v-if="currentStep === 5" class="flex-1 p-20 overflow-y-auto custom-scrollbar animate-fade-in relative text-[#A3FF47]">
                    <div class="max-w-6xl mx-auto space-y-24">
                        <!-- Success Banner -->
                        <div class="flex flex-col items-center text-center gap-12">
                            <div class="relative">
                                <div class="w-48 h-48 bg-[#A3FF47]/10 rounded-full flex items-center justify-center border-2 border-[#A3FF47]/30 shadow-[0_0_100px_rgba(163,255,71,0.2)]">
                                    <Award class="text-[#A3FF47] w-24 h-24 animate-pulse" />
                                </div>
                                <div class="absolute -top-4 -right-4 bg-[#A3FF47] text-black text-[10px] font-black px-4 py-1 skew-x-[-20deg]">RANK_PLATINUM</div>
                            </div>
                            <div class="space-y-4">
                                <h1 class="text-7xl font-black italic terminal-text tracking-tighter uppercase leading-none">Sector_Sanitized</h1>
                                <p class="text-[11px] font-black opacity-40 uppercase tracking-[0.8em]">Architectural Integrity Convergence Completed</p>
                            </div>
                        </div>

                        <!-- Data Analytics Grid -->
                        <div class="grid grid-cols-1 lg:grid-cols-[1.4fr_1fr] gap-12">
                            <div class="p-16 bg-black/60 border border-white/5 relative overflow-hidden group">
                                <h3 class="text-[10px] font-black opacity-30 uppercase tracking-[0.5em] mb-12 italic border-b border-white/5 pb-4">ArchitecturalReview.log</h3>
                                <p class="text-3xl font-black opacity-90 italic leading-snug terminal-text" v-html="finalReviewText"></p>
                                <!-- Decorative corner -->
                                <div class="absolute bottom-10 right-10 w-20 h-20 border-b-4 border-r-4 border-[#A3FF47]/20 pointer-events-none"></div>
                            </div>

                            <div class="space-y-8">
                                <div v-for="(val, key) in userScore" :key="key" class="p-12 border border-white/5 bg-white/[0.02] relative group">
                                    <div class="flex justify-between items-end mb-4">
                                        <span class="text-[10px] font-black opacity-30 uppercase tracking-[0.4em]">{{ key }}_CORE</span>
                                        <span class="text-4xl font-black terminal-text">{{ val }}%</span>
                                    </div>
                                    <div class="h-1 w-full bg-white/5 relative">
                                        <div class="h-full bg-[#A3FF47] shadow-[0_0_15px_#A3FF47] transition-all duration-1000" :style="{ width: val + '%' }"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Exit Protocol Actions -->
                        <div class="flex justify-center gap-12 pt-10">
                            <button @click="reloadApp" class="px-14 py-6 border border-[#A3FF47] text-[#A3FF47] font-black uppercase text-xs tracking-widest hover:bg-[#A3FF47]/10 transition-all">Reboot_Sector</button>
                            <button @click="goToNextQuest" v-if="currentQuestIdx < aiQuests.length - 1" class="px-20 py-6 bg-[#A3FF47] text-black font-black uppercase text-xs tracking-[0.3em] shadow-[0_0_50px_#A3FF47] transition-all active:scale-95">Next_Node_Uplink</button>
                        </div>
                    </div>
                </div>

                <!-- Platinum Feedback Modal: Cinematic Data Entry -->
                <transition name="scale">
                  <div v-if="feedbackModal.visible" class="fixed inset-0 z-[100] flex items-center justify-center p-8 bg-black/90 backdrop-blur-md">
                    <div class="w-full max-w-2xl bg-[#05070A] border-y-2 border-[#A3FF47]/30 relative overflow-hidden animate-scale-up text-[#A3FF47]">
                        <!-- Glitch line animation -->
                        <div class="absolute top-0 left-0 w-full h-[1px] bg-[#A3FF47] animate-[scan_2s_linear_infinite]"></div>
                        
                        <div class="p-16 space-y-12 text-center relative z-10">
                            <!-- Status Icon Sphere -->
                            <div class="mx-auto w-24 h-24 rounded-full flex items-center justify-center border-2 border-[#A3FF47]/20 shadow-[0_0_40px_rgba(163,255,71,0.1)]">
                                <CheckCircle v-if="feedbackModal.isSuccess" class="w-12 h-12 text-[#A3FF47] animate-pulse" />
                                <AlertTriangle v-else class="w-12 h-12 text-red-500 animate-bounce" />
                            </div>

                            <div class="space-y-4">
                                <span class="text-[9px] font-black opacity-30 uppercase tracking-[0.5em] italic">Priority_Notification::{{ feedbackModal.isSuccess ? 'PROCEED' : 'RETRY_INIT' }}</span>
                                <h3 class="text-4xl font-black italic terminal-text tracking-tighter uppercase leading-none">{{ feedbackModal.title }}</h3>
                                <p class="text-lg font-bold opacity-70 italic max-w-sm mx-auto">"{{ feedbackModal.desc }}"</p>
                            </div>

                            <div v-if="feedbackModal.details" class="p-6 bg-[#A3FF47]/2 border border-[#A3FF47]/5 text-[11px] font-bold text-left italic leading-relaxed max-h-40 overflow-y-auto custom-scrollbar" v-html="feedbackModal.details"></div>

                            <div class="pt-6">
                                <button @click="feedbackModal.isSuccess ? nextStep() : (feedbackModal.visible = false)"
                                    class="px-20 py-5 bg-[#A3FF47] text-black font-black uppercase text-xs tracking-widest shadow-[0_0_40px_rgba(163,255,71,0.2)] hover:shadow-[0_0_60px_rgba(163,255,71,0.4)] transition-all">
                                    {{ feedbackModal.isSuccess ? 'Confirm_and_Uplink' : 'Acknowledge_Error' }}
                                </button>
                            </div>
                        </div>

                        <!-- Technical Decal -->
                        <div class="absolute bottom-6 right-8 text-[40px] font-black opacity-[0.03] select-none pointer-events-none italic uppercase">SYS_LOG_v4</div>
                    </div>
                  </div>
                </transition>
              </div> <!-- workspace core end -->

          <!-- Right Status HUD (Platinum Vertical Panel) -->
          <aside class="w-80 border-l border-white/5 flex flex-col bg-black/40 hidden xl:flex shrink-0 z-30">
              <!-- [수정일: 2026-02-02] 닫기 버튼을 오른쪽 사이드바 최상단으로 이동 -->
              <button @click="$emit('close')" class="w-full py-8 bg-red-500/10 hover:bg-red-600 border-b border-white/5 transition-all group relative overflow-hidden flex flex-col items-center justify-center shrink-0">
                  <X class="w-6 h-6 text-red-500 group-hover:text-white transition-all group-hover:rotate-90 mb-2" />
                  <span class="text-xs font-black text-red-500 group-hover:text-white tracking-[0.3em] italic uppercase leading-none">Abort_Mission</span>
                  <div class="absolute bottom-0 inset-x-0 h-1 bg-red-500 scale-x-0 group-hover:scale-x-100 transition-transform origin-center"></div>
              </button>

              <div class="flex-1 flex flex-col p-10 space-y-16 overflow-y-auto custom-scrollbar">
                  <!-- Recovered Data Shards -->
                  <div class="flex items-center justify-between border-b border-white/5 pb-4">
                    <h3 class="text-[10px] font-black opacity-30 uppercase tracking-[0.4em] italic">Data_Shards</h3>
                    <span class="text-[9px] font-bold text-[#A3FF47]/60">{{ recoveredArtifacts.length }}/4</span>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                      <div v-for="i in 4" :key="'artifact-'+i" 
                        class="aspect-square border border-white/10 flex items-center justify-center bg-white/[0.02] group relative transition-all overflow-hidden"
                        :class="recoveredArtifacts.length >= i ? 'border-[#A3FF47]/40 bg-[#A3FF47]/10 shadow-[inner_0_0_20px_rgba(163,255,71,0.05)]' : ''"
                      >
                          <template v-if="recoveredArtifacts.length >= i">
                              <Database class="text-[#A3FF47] w-6 h-6 animate-pulse" />
                              <div class="absolute inset-0 bg-gradient-to-tr from-[#A3FF47]/20 to-transparent"></div>
                          </template>
                          <template v-else>
                              <Lock class="w-5 h-5 opacity-5 text-[#A3FF47]" />
                          </template>
                          
                          <!-- Kinetic Hover Reveal -->
                          <div class="absolute inset-0 bg-[#A3FF47] flex items-center justify-center p-4 translate-y-full group-hover:translate-y-0 transition-transform duration-500">
                              <span class="text-[10px] font-black text-black text-center uppercase leading-tight">{{ recoveredArtifacts[i-1] || 'LOCKED' }}</span>
                          </div>
                      </div>
                  </div>
              </div>

              <!-- Neural Bio-Status Overlay -->
              <div class="space-y-8">
                  <h3 class="text-[10px] font-black opacity-30 uppercase tracking-[0.4em] italic">Neural_Bio_Link</h3>
                  <div class="p-8 bg-black/60 border border-white/5 relative group overflow-hidden">
                      <!-- Scanning line on bio card -->
                      <div class="absolute top-0 left-0 w-full h-[1px] bg-[#A3FF47]/20 animate-[scan_3s_linear_infinite]"></div>
                      
                      <div class="flex items-center gap-6 relative z-10">
                          <div class="w-14 h-14 bg-[#A3FF47]/10 flex items-center justify-center border border-[#A3FF47]/20 relative">
                              <Zap class="text-[#A3FF47] w-6 h-6" />
                              <div class="absolute -bottom-1 -right-1 w-2 h-2 bg-cyan-400 rounded-full animate-ping"></div>
                          </div>
                          <div class="flex-1">
                              <div class="text-[10px] font-black text-[#A3FF47] uppercase tracking-tighter">{{ integrity > 75 ? 'Optimal' : (integrity > 40 ? 'Stable' : 'Unstable') }}</div>
                              <div class="mt-3 h-0.5 w-full bg-white/5 relative">
                                  <div class="h-full bg-[#A3FF47] shadow-[0_0_10px_#A3FF47] transition-all duration-1000" :style="{ width: integrity + '%' }"></div>
                              </div>
                          </div>
                      </div>
                  </div>
              </div>

              <!-- Tactical Briefing Fragment -->
              <div class="mt-auto p-8 border border-white/5 bg-black/60 relative">
                  <div class="flex items-start gap-5">
                    <AlertTriangle class="w-4 h-4 text-[#A3FF47]/30 shrink-0 mt-1" />
                    <p class="text-[10px] text-[#A3FF47]/70 leading-relaxed font-bold italic">
                      "SYSTEM: 가동률 <span class="text-[#A3FF47] font-black">{{ integrity }}%</span>. <br/>아키텍트 {{ userNickname }}, 모든 노드가 가이드라인을 준수 중입니다."
                    </p>
                  </div>
              </div>
          </aside>
        </div> <!-- unified hud layout end -->
      </div> <!-- main view end -->
    </div> <!-- platinum root end -->
  </div> <!-- isOpen root end -->
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
  VolumeX,
  Activity,
  Lock,
  Wifi
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
  isPlayingBGM,
  // [수정일: 2026-02-02] 가동률 및 아티팩트 노출
  integrity,
  recoveredArtifacts
} = usePseudoProblem(props, emit)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');

/* Platinum HUD Aesthetics */
.platinum-hud-root {
  background: radial-gradient(circle at 50% 50%, #0a0e14 0%, #020508 100%);
  color: #A3FF47;
  font-family: 'Fira Code', monospace;
}

.terminal-text {
  text-shadow: 0 0 15px rgba(163, 255, 71, 0.4);
}

.shadow-neon {
  filter: drop-shadow(0 0 10px rgba(163, 255, 71, 0.5));
}

.dot-grid {
  background-image: radial-gradient(rgba(163, 255, 71, 0.08) 1px, transparent 1px);
  background-size: 30px 30px;
}

.scanline-overlay {
  background: linear-gradient(
    rgba(18, 16, 16, 0) 50%, 
    rgba(0, 0, 0, 0.15) 50%
  ), 
  linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
  background-size: 100% 3px, 2px 100%;
  pointer-events: none;
}

/* Character HUD Effects */
.hud-ring {
    border: 1px solid rgba(163, 255, 71, 0.1);
    box-shadow: 0 0 30px rgba(163, 255, 71, 0.05);
}

/* Custom Scrollbar for Platinum HUD */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(163, 255, 71, 0.2);
  border-radius: 2px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(163, 255, 71, 0.5);
}

/* Animations */
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleUp { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }
@keyframes scan { 0% { top: -10%; } 100% { top: 110%; } }

.animate-fade-in { animation: fadeIn 0.8s ease-out forwards; }
.animate-scale-up { animation: scaleUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

/* Existing Animations Restoration */
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
@keyframes scaleIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
.animate-fade-in-up { animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.animate-scale-in { animation: scaleIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }

/* Star Wars UI Legacy */
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
}
@keyframes fadeOut { 0% { opacity: 0; } 10%, 80% { opacity: 1; } 100% { opacity: 0; } }
.animate-fade-out { animation: fadeOut 8s ease-in-out forwards; }
.crawl-container { position: relative; width: 100%; height: 100%; }
.crawl-content { position: absolute; top: 100%; width: 100%; transform-origin: 50% 100%; transform: rotateX(25deg); opacity: 1; }
.crawl-title { font-size: 72px; font-weight: 900; color: #A3FF47; text-align: center; margin-bottom: 60px; letter-spacing: 0.1em; text-transform: uppercase; font-family: 'Fira Code', monospace; }
.crawl-body { font-size: 28px; font-weight: 700; color: #A3FF47; text-align: justify; line-height: 1.6; padding: 0 15%; font-family: 'Fira Code', monospace; }
@keyframes crawl { 0% { top: 120%; } 100% { top: -3000px; } }
.animate-crawl { animation: crawl 45s linear forwards; }
.intro-logo { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) scale(10); font-size: 120px; font-weight: 900; color: #A3FF47; text-align: center; opacity: 0; white-space: nowrap; letter-spacing: -0.05em; line-height: 0.8; filter: drop-shadow(0 0 20px rgba(163, 255, 71, 0.5)); }
@keyframes logo-zoom { 0% { transform: translate(-50%, -50%) scale(8); opacity: 0; } 1% { opacity: 1; } 90% { transform: translate(-50%, -50%) scale(0.01); opacity: 1; } 100% { transform: translate(-50%, -50%) scale(0); opacity: 0; } }
.animate-logo-zoom { animation: logo-zoom 8s cubic-bezier(0.12, 0, 0.39, 0) forwards; }
</style>
