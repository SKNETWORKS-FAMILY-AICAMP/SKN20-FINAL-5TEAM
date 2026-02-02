<template>
  <div :class="['logic-mirror-modal-overlay', { 'animate-shake': triggerShake }]" @click.self="$emit('close')">
    <div class="logic-mirror-container">
      <!-- HUD Header -->
      <header class="h-20 border-b border-cyan-500/30 bg-black flex justify-between items-center px-8 relative overflow-hidden shrink-0">
        <!-- Background Scanline effect -->
        <div class="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%] pointer-events-none opacity-20"></div>
        
        <div class="flex items-center space-x-6 z-10">
          <div class="relative group">
            <div class="absolute -inset-1 bg-cyan-500/20 rounded-lg blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
            <div class="relative bg-black border border-cyan-500/50 p-2 rounded-lg">
              <Terminal class="text-cyan-400 w-5 h-5 animate-pulse" />
            </div>
          </div>
          <div class="space-y-0.5">
            <div class="flex items-center gap-3">
              <h1 class="font-black text-xl tracking-[0.2em] text-white italic">LOGIC_MIRROR_V3</h1>
              <span class="text-[8px] bg-cyan-500/10 text-cyan-400 px-2 py-0.5 border border-cyan-500/20 rounded font-mono">STABLE_OS</span>
            </div>
            <div class="flex items-center gap-2 text-[9px] font-mono text-cyan-500/50 uppercase tracking-widest">
              <span class="animate-pulse">●</span> SESSION_ID: 0x5CD05... | SECTOR: LOGIC_FORGE
            </div>
          </div>
        </div>

        <div class="flex items-center gap-8 z-10">
          <div class="hidden lg:flex flex-col items-end font-mono">
            <div class="text-[8px] text-gray-500 tracking-widest uppercase mb-1">Architectural Integrity</div>
            <div class="flex gap-1">
              <div v-for="i in 10" :key="i" class="w-1 h-2" :class="i < 9 ? 'bg-cyan-500/60' : 'bg-gray-800'"></div>
            </div>
          </div>
          
          <div class="h-8 w-px bg-white/10"></div>

          <button 
            @click="$emit('close')" 
            class="group relative"
          >
            <div class="absolute -inset-2 bg-red-500/20 rounded-full blur opacity-0 group-hover:opacity-100 transition duration-300"></div>
            <div class="relative flex items-center gap-2 px-3 py-1.5 border border-white/10 rounded-lg hover:border-red-500/50 hover:bg-red-500/5 transition-all text-gray-400 hover:text-red-400">
               <span class="text-[9px] font-black tracking-widest uppercase">Terminate</span>
               <X class="w-4 h-4" />
            </div>
          </button>
        </div>
        
        <!-- Bottom Neon Line -->
        <div class="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-cyan-500 to-transparent shadow-[0_0_10px_#00f3ff]"></div>
      </header>

      <div class="flex-1 flex overflow-hidden">
        <!-- Sidebar Navigation -->
        <aside class="sidebar w-80 border-r border-white/5 flex flex-col items-stretch bg-[#020408] shrink-0 relative transition-all duration-500">
          <div class="p-6 space-y-6">
            <!-- Mentor Dashboard HUD -->
            <div class="bg-white/[0.02] border border-cyan-500/20 hud-box-clip p-5 relative group overflow-hidden">
              <div class="absolute top-0 right-0 w-16 h-16 bg-cyan-500/5 rounded-full blur-xl -mr-8 -mt-8"></div>
              
              <div class="flex items-center gap-4 mb-5">
                <div class="relative">
                  <div class="w-12 h-12 bg-black border border-cyan-500/30 flex items-center justify-center p-1 hud-box-clip">
                    <img :src="mentorImage" alt="Mentor Duck" class="w-full h-full object-contain" />
                  </div>
                  <div class="absolute -bottom-1 -right-1 w-3 h-3 bg-cyan-500 rounded-full border-2 border-black animate-pulse"></div>
                </div>
                <div>
                  <div class="text-[8px] font-black text-cyan-500/50 uppercase tracking-widest mb-0.5">SYSC_MENTOR_LINK</div>
                  <h3 class="text-xs font-black text-white italic tracking-widest uppercase">{{ currentClass }}</h3>
                </div>
              </div>

              <div class="space-y-4 pt-2">
                <div class="flex justify-between items-center">
                  <span class="text-[9px] font-black text-gray-500 uppercase tracking-widest">Integrity_Core</span>
                  <div class="flex gap-1">
                    <span v-for="i in 3" :key="i" :class="['text-[10px] transition-all duration-300', i <= userStability ? 'text-cyan-400 shadow-[0_0_8px_cyan]' : 'text-gray-800']">♥</span>
                  </div>
                </div>
                
                <div class="space-y-2">
                  <div class="flex justify-between text-[8px] font-black text-cyan-500/60 uppercase tracking-widest">
                    <span>Knowledge_XP</span>
                    <span>{{ userXP }} / {{ nextLevelXP }}</span>
                  </div>
                  <div class="h-1.5 w-full bg-white/5 relative overflow-hidden group">
                    <div class="absolute inset-0 bg-cyan-500/20"></div>
                    <div 
                      class="absolute h-full bg-cyan-500 transition-all duration-1000 shadow-[0_0_10px_cyan]"
                      :style="{ width: xpProgress + '%' }"
                    >
                       <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent animate-shimmer"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

        
          <nav class="mt-4 px-6 space-y-2 shrink-0">
            <button 
                @click="activeTab = 'analyze'"
                :class="['w-full flex items-center gap-4 px-5 py-4 transition-all duration-500 group relative hud-button-clip', activeTab === 'analyze' ? 'bg-cyan-500/20 text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] border border-cyan-500/50' : 'text-gray-500 border border-white/5 hover:border-cyan-500/30 hover:bg-white/5']"
            >
              <Layers :class="['w-4 h-4 transition-all duration-500', activeTab === 'analyze' ? 'text-cyan-400 scale-110' : 'group-hover:text-cyan-400']" />
              <span class="text-xs font-black tracking-widest uppercase">SYSC_ANALYZE</span>
              <div v-if="activeTab === 'analyze'" class="absolute left-0 top-0 w-1 h-full bg-cyan-500"></div>
            </button>
            
            <button 
                @click="activeTab = 'practice'"
                :class="['w-full flex items-center gap-4 px-5 py-4 transition-all duration-500 group relative hud-button-clip', activeTab === 'practice' ? 'bg-cyan-500/20 text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] border border-cyan-500/50' : 'text-gray-500 border border-white/5 hover:border-cyan-500/30 hover:bg-white/5']"
            >
              <BookOpen :class="['w-4 h-4 transition-all duration-500', activeTab === 'practice' ? 'text-cyan-400 scale-110' : 'group-hover:text-cyan-400']" />
              <span class="text-xs font-black tracking-widest uppercase">TRAINING_CAMP</span>
              <div v-if="activeTab === 'practice'" class="absolute left-0 top-0 w-1 h-full bg-cyan-500"></div>
            </button>
          </nav>

          <!-- Chatbot Area HUD -->
          <div class="flex-1 min-h-0 px-6 mt-8 mb-4 flex flex-col overflow-hidden">
            <div class="px-2 py-2 flex items-center gap-2 border-b border-cyan-500/20 mb-3 shrink-0 uppercase italic">
              <div class="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse"></div>
              <span class="text-[9px] font-black text-cyan-400 tracking-[0.3em]">Agent_Link: DUCK</span>
            </div>

            <div id="chat-scroll" class="flex-1 overflow-y-auto space-y-4 px-2 custom-scrollbar-thin">
              <div v-for="(msg, idx) in chatMessages" :key="idx" :class="['flex flex-col', msg.role === 'user' ? 'items-end' : 'items-start']">
                <span class="text-[7px] text-gray-600 font-black mb-1 uppercase tracking-tighter">{{ msg.role === 'user' ? 'USER' : 'AGENT' }}_ID</span>
                <div :class="['max-w-[90%] p-4 text-[13px] leading-relaxed relative hud-button-clip border transition-all', 
                              msg.role === 'user' ? 'bg-white/5 text-white border-white/10' : 'bg-cyan-500/10 text-cyan-100 border-cyan-500/20']">
                  {{ msg.text }}
                </div>
              </div>
              <div v-if="isChatLoading" class="flex justify-start">
                <div class="bg-cyan-500/5 p-3 hud-button-clip animate-pulse flex gap-1 border border-cyan-500/20">
                  <span class="w-1 h-1 bg-cyan-500/40 rounded-full animate-bounce"></span>
                  <span class="w-1 h-1 bg-cyan-500/40 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                  <span class="w-1 h-1 bg-cyan-500/40 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                </div>
              </div>
            </div>

            <div class="mt-4 relative shrink-0">
              <input 
                v-model="chatInput" 
                @keyup.enter="sendChatMessage"
                placeholder="INPUT COMMAND..."
                class="w-full bg-black/40 border-2 border-white/5 hud-button-clip px-4 py-3 text-[11px] text-cyan-100 placeholder:text-gray-700 focus:outline-none focus:border-cyan-500/50 transition-all font-mono shadow-inner"
              />
              <button @click="sendChatMessage" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-cyan-400 transition-colors">
                <Send class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div class="sidebar-footer p-6 border-t border-white/5 shrink-0">
            <button 
              @click="$emit('close')"
              class="w-full flex items-center gap-4 px-6 py-4 transition-all duration-300 active:scale-95 group"
            >
              <LogOut class="w-4 h-4 text-gray-600 group-hover:text-red-400 transition-colors" />
              <span class="text-[9px] font-black tracking-[0.3em] uppercase text-gray-600 group-hover:text-red-400">DISCONNECT_SESSION</span>
            </button>
          </div>
        </aside>

        <!-- Main Content Area -->
        <main class="main-content flex-1 flex flex-col bg-[#020408] overflow-hidden relative">
          <!-- Background Grid decor -->
          <div class="absolute inset-0 opacity-[0.03] pointer-events-none" style="background-image: radial-gradient(#00f3ff 1px, transparent 1px); background-size: 32px 32px;"></div>
          
          <!-- Tabbed Content Layer -->
          <div v-if="activeTab === 'analyze'" class="flex-1 flex flex-col overflow-hidden relative z-10">
            <!-- TOP: Editor/Puzzle Workspace -->
            <section class="editor-section h-[55%] flex flex-col border-b border-white/5 bg-black/20 overflow-hidden">
              <div class="h-12 flex items-center justify-between px-8 bg-black/40 border-b border-cyan-500/20 shrink-0">
                <p class="text-[9px] font-black text-cyan-400/60 uppercase tracking-[0.3em] flex items-center gap-2 italic">
                  <Terminal class="w-3 h-3" />
                  WORKSPACE_RE_BOOT_V3
                </p>
                <div class="flex items-center gap-4">
                  <button @click="initQuestBlocks" class="flex items-center gap-2 px-3 py-1 text-[8px] font-black text-gray-500 hover:text-cyan-400 transition-colors uppercase tracking-widest border border-white/5 hover:border-cyan-500/30">
                    <History class="w-2.5 h-2.5" />
                    <span>Reset_State</span>
                  </button>
                  <button 
                    @click="analyzeCode"
                    :disabled="loading || userPuzzleSolution.length === 0"
                    class="px-6 py-1.5 bg-cyan-500 text-black font-black text-[10px] tracking-widest uppercase hover:bg-cyan-400 disabled:opacity-30 transition-all active:scale-95 shadow-[0_0_15px_rgba(0,243,255,0.4)]"
                  >
                    <span v-if="loading">Analyzing...</span>
                    <span v-else>Exec_Sync_Analysis</span>
                  </button>
                </div>
              </div>

              <div class="flex-1 flex overflow-hidden">
                <!-- Left Palette -->
                <div class="w-[360px] border-r border-white/5 bg-black/40 flex flex-col overflow-hidden shrink-0">
                  <div class="p-6 border-b border-white/5 space-y-4 shrink-0 bg-cyan-500/5">
                    <div class="flex items-center gap-4">
                      <div class="w-10 h-10 bg-black border border-cyan-500/20 flex items-center justify-center text-xl hud-box-clip">{{ currentQuest.emoji }}</div>
                      <div>
                        <h4 class="text-sm font-black text-white italic tracking-wider uppercase">{{ currentQuest.title }}</h4>
                        <p class="text-[9px] text-cyan-500/50 font-black tracking-widest uppercase italic">{{ currentQuest.logic_type }}</p>
                      </div>
                    </div>
                    <div class="p-5 bg-white/[0.02] border border-white/5 hud-box-clip">
                      <p class="text-[13px] text-gray-400 leading-relaxed font-medium">{{ currentQuest.description }}</p>
                    </div>
                  </div>
                  <div class="flex-1 flex flex-col overflow-hidden">
                    <div class="px-6 py-2 bg-black/40 border-b border-white/5"><p class="text-[9px] font-black text-gray-600 uppercase tracking-widest italic">Logic_Palette_Link</p></div>
                    <div class="flex-1 p-6 overflow-y-auto custom-scrollbar-thin bg-black/10">
                      <div class="space-y-2">
                        <div v-for="(block, index) in shuffledPalette" :key="'palette-' + index" @click="useCard(index)" class="group cursor-pointer transition-all relative">
                          <div class="absolute inset-0 bg-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity hud-button-clip"></div>
                          <div class="bg-black border border-white/5 group-hover:border-cyan-500/40 p-3 flex items-center gap-4 hud-button-clip relative z-10">
                            <div class="w-1.5 h-1.5 rounded-full bg-gray-800 group-hover:bg-cyan-500 group-hover:shadow-[0_0_8px_cyan] transition-all"></div>
                            <span class="text-[11px] font-black text-gray-500 group-hover:text-white uppercase tracking-widest italic">{{ block.text_ko }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <!-- Right Workspace -->
                <div class="flex-1 flex flex-col bg-black/20 relative">
                  <div class="flex-1 p-8 overflow-y-auto custom-scrollbar-thin relative">
                    <div v-if="userPuzzleSolution.length === 0" class="absolute inset-0 flex flex-col items-center justify-center text-gray-800 pointer-events-none uppercase italic tracking-[0.4em]">
                      <Layers class="w-10 h-10 opacity-5 mb-4" />
                      <p class="text-[8px] font-black opacity-20 italic">Place_Logic_Nodes_Here</p>
                    </div>
                    <div class="space-y-3 relative z-10">
                      <div v-for="(block, index) in userPuzzleSolution" :key="'solution-' + index" @click="unuseCard(index)" class="group cursor-pointer transition-all relative" :style="{ marginLeft: (block.indent || 0) * 24 + 'px' }">
                        <div class="absolute inset-0 bg-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity hud-button-clip"></div>
                        <div class="bg-black/60 border border-cyan-500/30 group-hover:border-cyan-400 p-4 flex items-center gap-5 hud-button-clip relative z-10 shadow-[inner_0_0_10px_rgba(0,0,0,0.5)]">
                          <div class="w-8 h-8 bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-lg hud-box-clip">{{ block.icon }}</div>
                          <div class="flex-1">
                            <p class="text-xs font-black text-cyan-400 italic uppercase tracking-wider">{{ block.text_ko }}</p>
                            <p class="text-[10px] font-mono font-black text-gray-500 mt-0.5 uppercase tracking-widest">{{ block.text_py }}</p>
                          </div>
                          <X class="w-3.5 h-3.5 text-gray-700 group-hover:text-red-400 transition-colors" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
            
            <!-- BOTTOM: AI Analysis Result -->
            <section class="spec-section flex-1 min-h-0 flex flex-col bg-black overflow-hidden">
              <div class="h-10 flex items-center px-8 bg-black border-b border-cyan-500/20 shrink-0 uppercase italic font-black text-[9px] tracking-[0.3em] text-cyan-500/40">
                <Layout class="text-cyan-500 w-3 h-3 mr-3" />
                <span>Architecture_Decomposite_Core</span>
              </div>
              <div v-if="!generatedResults && !loading" class="flex-1 flex flex-col items-center justify-center text-center">
                <div class="p-8 bg-black border border-white/5 hud-box-clip mb-6 group hover:border-cyan-500/30 transition-all duration-700">
                  <BrainCircuit class="text-gray-800 w-12 h-12 group-hover:text-cyan-500 transition-colors duration-500" />
                </div>
                <h3 class="text-lg font-black text-white italic tracking-widest uppercase">Awaiting_Input_Data...</h3>
                <p class="text-gray-600 mt-2 text-[10px] font-black font-mono uppercase tracking-[0.2em]">Synchronize logic blocks to trigger AI_ENGINE</p>
              </div>
              <div v-else-if="loading" class="flex-1 p-10 flex gap-8 items-start justify-center">
                <div v-for="i in 3" :key="i" class="w-72 h-40 bg-white/5 hud-box-clip border border-white/5 animate-pulse overflow-hidden relative">
                  <div class="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-500/10 to-transparent -translate-x-full animate-progress-stripes opacity-20"></div>
                </div>
              </div>
              <div v-else class="flex-1 flex flex-col overflow-hidden bg-black/40">
                <div class="px-8 pt-6 pb-2 flex gap-4 overflow-x-auto custom-scrollbar-none shrink-0">
                  <button v-for="level in LEVELS" :key="level.id" @click="activeLevel = level.id" :class="['px-6 py-4 transition-all duration-500 text-left min-w-[220px] relative hud-button-clip group border', activeLevel === level.id ? 'border-cyan-500/50 bg-cyan-500/10' : 'border-white/5 bg-black/40 hover:border-cyan-500/20']">
                    <p :class="['text-[8px] font-black uppercase mb-1 tracking-widest italic', activeLevel === level.id ? 'text-cyan-400' : 'text-gray-600']">DATA_LVL_0{{ level.id }}</p>
                    <h4 :class="['text-[11px] font-black tracking-[0.1em] uppercase italic', activeLevel === level.id ? 'text-white' : 'text-gray-500']">{{ level.subtitle }}</h4>
                  </button>
                </div>
                <div class="flex-1 overflow-y-auto p-10 pt-4 custom-scrollbar-thin">
                  <div class="max-w-6xl mx-auto space-y-8 pr-12">
                    <div class="bg-white/[0.01] border border-white/5 p-10 hud-box-clip relative overflow-hidden">
                      <div class="flex items-start gap-8 mb-10">
                        <div :class="['p-5 hud-box-clip border', levels[activeLevel-1].bgColor, levels[activeLevel-1].id === 3 ? 'border-purple-500/50' : 'border-cyan-500/30']">
                          <Lightbulb :class="['w-8 h-8', levels[activeLevel-1].color]" />
                        </div>
                        <div class="italic">
                          <h2 class="text-2xl font-black text-white tracking-widest uppercase italic">{{ levels[activeLevel-1].title }}</h2>
                          <p class="text-xs text-gray-500 mt-2 leading-relaxed font-black uppercase tracking-widest opacity-60">{{ levels[activeLevel-1].desc }}</p>
                        </div>
                      </div>
                      <div class="relative group/view">
                        <div v-if="activeLevel === 3" class="relative bg-black border border-purple-500/20 hud-box-clip h-[500px] overflow-y-auto overflow-x-hidden custom-scrollbar-thin">
                          <div class="p-16 flex justify-center"><div id="mermaid-renderer" class="mermaid flex justify-center text-white scale-110 origin-top mb-12"></div></div>
                        </div>
                        <pre v-else class="relative p-10 bg-black/80 border border-cyan-500/20 hud-box-clip font-mono text-[13px] leading-relaxed text-cyan-100 whitespace-pre-wrap italic">{{ generatedResults['level' + activeLevel] }}</pre>
                      </div>
                      <div class="mt-8 p-8 bg-cyan-500/5 hud-button-clip border border-cyan-500/10 flex gap-6">
                        <div class="bg-cyan-500 p-3 h-fit rounded-lg shadow-[0_0_15px_cyan]"><MessageSquare class="text-black w-4 h-4" /></div>
                        <p class="text-[13px] text-cyan-100/90 leading-relaxed italic font-black uppercase tracking-wider line-clamp-2">"{{ generatedResults.mentorTip }}"</p>
                      </div>
                      <div v-if="practiceMode !== 'none'" class="mt-10 flex flex-col sm:flex-row justify-center gap-6">
                        <button @click="handleNextQuest" class="px-10 py-5 bg-cyan-500 hover:bg-cyan-400 text-black font-black transition-all active:scale-95 text-xs uppercase tracking-widest hud-button-clip italic">Proceed_Next_Link</button>
                        <button @click="activeTab = 'practice'; practiceSubTab = 'stages';" class="px-10 py-5 bg-white/5 hover:bg-white/10 text-gray-400 font-black transition-all active:scale-95 text-xs uppercase tracking-widest border border-white/5 hud-button-clip italic">Return_To_Sector</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>
          
          <!-- Practice Tab -->
          <div v-else class="practice-tab flex-1 p-12 overflow-y-auto relative z-10 custom-scrollbar-thin">
            <div class="max-w-5xl mx-auto space-y-16">
              <div class="text-center space-y-6">
                <div class="inline-flex items-center gap-2 px-4 py-1.5 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hud-button-clip text-[9px] font-black uppercase tracking-[0.3em] italic">
                  <div class="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse"></div>SYSC_TRAINING_ACTIVE
                </div>
                <h2 class="text-5xl font-black text-white italic tracking-widest uppercase">Logic_Design_Forge</h2>
                <p class="text-gray-500 text-sm max-w-xl mx-auto font-black uppercase tracking-widest italic opacity-70">Synthesize your logic before committing to code. <br/>Architectural abstraction defines the scale of your engine.</p>
              </div>
              <div v-if="practiceSubTab === 'categories'" class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div v-for="practice in practices" :key="practice.id" @click="selectCategory(practice.id)" class="bg-black border border-white/5 p-12 hud-box-clip hover:border-cyan-500/30 transition-all duration-700 cursor-pointer group flex flex-col justify-between h-[400px] relative overflow-hidden active:scale-[0.99]">
                  <div class="absolute top-0 right-0 p-12 opacity-[0.03] group-hover:opacity-[0.08] transition-all duration-1000 rotate-12"><ArrowRight class="w-40 h-40" /></div>
                  <div class="relative z-10">
                    <div class="flex justify-between items-start mb-8">
                      <span class="px-3 py-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hud-button-clip text-[8px] font-black uppercase tracking-widest">{{ practice.badge }}</span>
                      <div class="bg-white/5 p-3 hud-box-clip text-gray-600 group-hover:text-cyan-400 group-hover:bg-cyan-500/10 transition-all duration-500"><ArrowRight class="group-hover:translate-x-1 transition-transform w-5 h-5" /></div>
                    </div>
                    <h3 class="text-2xl font-black text-white italic tracking-widest uppercase mb-2">{{ practice.title }}</h3>
                    <p class="text-cyan-500/50 font-black text-[10px] tracking-widest uppercase italic">{{ practice.subtitle }}</p>
                    <p class="text-gray-500 text-[11px] mt-8 leading-relaxed font-black uppercase tracking-widest opacity-60 group-hover:opacity-100 transition-opacity">{{ practice.description }}</p>
                  </div>
                </div>
              </div>
              <div v-else-if="practiceSubTab === 'stages'" class="space-y-10">
                <div class="flex items-center justify-between">
                  <button @click="practiceSubTab = 'categories'" class="flex items-center gap-3 text-gray-500 hover:text-cyan-400 transition-colors group italic">
                    <X class="w-4 h-4 group-hover:rotate-90 transition-transform" /><span class="text-[9px] font-black uppercase tracking-widest">Return_To_Selection</span>
                  </button>
                  <div class="px-6 py-2 bg-cyan-500/5 border border-cyan-500/20 hud-button-clip">
                    <span class="text-[8px] font-black text-cyan-500/60 uppercase tracking-widest italic">{{ selectedCategory === 'forward' ? 'Logic_Solver' : 'Architect_Analyzer' }} Sector Map</span>
                  </div>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div v-for="(quest, index) in filteredStages" :key="quest.id" @click="startStage(quest)" class="group relative bg-black/40 border border-white/5 p-8 hud-box-clip hover:border-cyan-500/40 transition-all cursor-pointer overflow-hidden">
                    <div class="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity italic"><span class="text-5xl font-black italic">{{ index + 1 }}</span></div>
                    <div class="relative z-10 space-y-4">
                      <div class="flex items-center gap-3">
                        <div class="w-8 h-8 bg-black border border-cyan-500/20 flex items-center justify-center hud-box-clip text-xl">{{ quest.emoji }}</div>
                        <span class="text-[8px] font-black text-cyan-500/50 uppercase tracking-widest italic">Node_{{ index + 1 }}</span>
                      </div>
                      <h3 class="text-base font-black text-white italic group-hover:text-cyan-300 transition-colors uppercase tracking-wider">{{ quest.title }}</h3>
                      <p class="text-[10px] text-gray-600 line-clamp-2 font-black uppercase tracking-widest opacity-60">{{ quest.description }}</p>
                      <div class="pt-4 flex items-center justify-between">
                        <span class="text-[7px] font-black text-gray-700 uppercase tracking-tighter italic">{{ quest.logic_type }}</span>
                        <div class="w-8 h-8 bg-black border border-white/10 flex items-center justify-center text-gray-600 group-hover:border-cyan-500/50 group-hover:text-cyan-400 transition-all hud-box-clip"><ArrowRight class="w-3 h-3" /></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="bg-black/60 border border-cyan-500/20 hud-box-clip p-16 relative overflow-hidden group">
                <div class="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-transparent"></div>
                <div class="flex flex-col lg:flex-row items-center gap-16 relative z-10">
                  <div class="flex-1 space-y-8 text-center lg:text-left">
                    <div class="space-y-4">
                      <div class="inline-block px-3 py-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hud-button-clip text-[8px] font-black uppercase tracking-widest italic">Anomalous_Sector_Detected</div>
                      <h3 class="text-4xl font-black text-white italic tracking-widest uppercase">Daily_Architect_Challenge</h3>
                      <p class="text-gray-500 text-lg leading-relaxed font-black uppercase tracking-widest italic opacity-70">Refine logic frameworks into <span class="text-cyan-400">Sector_02_Specs</span>.</p>
                    </div>
                    <div class="flex flex-col sm:flex-row gap-5 justify-center lg:justify-start">
                      <button @click="startChallenge" class="px-12 py-5 bg-cyan-500 hover:bg-cyan-400 text-black font-black transition-all active:scale-95 text-[10px] uppercase tracking-[0.2em] hud-button-clip italic">Initialize_Challenge</button>
                      <button @click="activeTab = 'analyze'" class="px-12 py-5 bg-white/5 hover:bg-white/10 text-gray-500 font-black transition-all text-[10px] uppercase tracking-[0.2em] border border-white/5 hud-button-clip italic">Load_Protocol_Guide</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div> <!-- Closing logic-mirror-container -->

    <!-- Red Glitch Overlay (VFX) -->
    <div v-if="triggerGlitch" class="fixed inset-0 pointer-events-none z-[30000] bg-red-600/20 mix-blend-overlay animate-glitch overflow-hidden">
      <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20"></div>
    </div>

    <!-- Validation Feedback Modal HUD -->
    <transition name="scale">
      <div v-if="showValidationModal" class="fixed inset-0 z-[20000] flex items-center justify-center p-6 bg-black/60 backdrop-blur-md">
        <div class="bg-black border border-cyan-500/40 hud-box-clip w-full max-w-md overflow-hidden shadow-[0_0_50px_rgba(0,243,255,0.2)] animate-in fade-in zoom-in duration-300 relative">
          <!-- Top Neon Bar -->
          <div :class="['h-1 shadow-[0_0_10px_currentColor]', validationResult === 'success' ? 'bg-cyan-500 text-cyan-500' : 'bg-red-500 text-red-500']"></div>
          
          <div class="p-10 text-center space-y-8 relative">
            <!-- Background Scanline effect -->
            <div class="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%)] bg-[length:100%_4px] pointer-events-none opacity-10"></div>

            <div class="flex justify-center">
              <div :class="['w-20 h-20 bg-black border-2 flex items-center justify-center text-4xl hud-box-clip shadow-2xl relative group', 
                            validationResult === 'success' ? 'border-cyan-500/50 text-cyan-400 shadow-cyan-500/20' : 'border-red-500/50 text-red-500 shadow-red-500/20']">
                <div class="absolute inset-0 bg-current opacity-5 group-hover:opacity-10 transition-opacity"></div>
                {{ validationResult === 'success' ? '⚡' : '⚠' }}
              </div>
            </div>
            
            <div class="space-y-3 italic">
              <h3 class="text-2xl font-black text-white tracking-widest uppercase italic">
                {{ validationResult === 'success' ? 'PROTOCOL_SYNC_SUCCESS' : 'LOGIC_SYNC_FAILURE' }}
              </h3>
              <p class="text-gray-500 text-[11px] font-black uppercase tracking-widest leading-relaxed opacity-80">
                {{ validationMessage }}
              </p>
            </div>

            <button 
              @click="closeValidationModal"
              :class="['w-full py-5 font-black transition-all active:scale-95 hud-button-clip italic uppercase tracking-widest text-xs', 
                       validationResult === 'success' ? 'bg-cyan-500 hover:bg-cyan-400 text-black shadow-[0_0_20px_rgba(0,243,255,0.4)]' : 'bg-white/5 hover:bg-white/10 text-gray-400 border border-white/10']"
            >
              {{ validationResult === 'success' ? 'Initialize_Analysis_Stream' : 'Re_Attempt_Calibration' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Level Up Splash UI -->
    <transition name="splash">
      <div v-if="showLevelUpSplash" class="fixed inset-0 z-[40000] flex items-center justify-center bg-indigo-950/80 backdrop-blur-3xl overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-t from-indigo-600/20 to-transparent"></div>
        <div class="relative text-center space-y-12 animate-in zoom-in-50 duration-700">
          <div class="relative inline-block">
            <div class="absolute inset-0 bg-indigo-500 blur-[120px] opacity-50 animate-pulse"></div>
            <img src="/image/mentor/duck.png" alt="Level Up" class="w-56 h-56 relative z-10 animate-bounce" />
          </div>
          <div class="space-y-4">
             <p class="text-indigo-400 font-black text-xl tracking-[0.4em] uppercase">Class Upgrade</p>
             <h2 class="text-8xl font-black text-white tracking-tighter drop-shadow-2xl">{{ currentClass }}</h2>
             <div class="h-1 w-64 bg-indigo-500 mx-auto rounded-full mt-6 shadow-[0_0_30px_rgba(99,102,241,0.8)]"></div>
          </div>
          <button @click="showLevelUpSplash = false" class="px-16 py-6 bg-white text-indigo-950 rounded-3xl font-black text-xl hover:scale-105 transition-all shadow-huge active:scale-95">NEXT STEP</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import mermaid from 'mermaid';
import { 
  BrainCircuit, Layers, BookOpen, LogOut, Terminal, Sparkles, Layout, Lightbulb, MessageSquare, ArrowRight, X, History, Send
} from 'lucide-vue-next';
import { aiQuests } from './data/stages.js';

/* 
  [수정일: 2026-01-26]
  [수정내용: 상/하 수직 분할 레이아웃으로 변경]
  - TOP: Puzzle Palette & Workspace (문제 풀이)
  - BOTTOM: AI Analysis Result (분석 결과)
  - Vertical split with borders and independent scrolling
*/

// --- 1. Constants ---
const LEVELS = [
  { id: 1, title: 'Level 1: 절차적 수도 코드', subtitle: 'Procedural Logic', desc: '구문 중심의 직역. 루프와 조건문을 명시하여 로직의 흐름을 따라갑니다.', color: 'text-blue-400', bgColor: 'bg-blue-500/10' },
  { id: 2, title: 'Level 2: 논리적 명세', subtitle: 'Logical Specification', desc: '비즈니스 규칙 중심. 처리 목적(무엇을)에 집중합니다.', color: 'text-indigo-400', bgColor: 'bg-indigo-500/10' },
  { id: 3, title: 'Level 3: 아키텍처 모델', subtitle: 'Architecture Diagram', desc: '시스템 관계 중심. Mermaid.js를 활용한 시각적 아키텍처 다이어그램입니다.', color: 'text-purple-400', bgColor: 'bg-purple-500/10' }
];

const MOCK_ANALYSIS_DB = {
  'quest_ai_01': {
    level1: "1. 입력 x와 가중치 w를 곱하여 가중 합산 시작\n2. 결과에 편향 b를 더함\n3. 최종 y를 반환",
    level2: "입력 데이터에 비중을 적용하고 모델의 오프셋(Bias)을 조절하여 뉴런의 활성화 값을 계산합니다.",
    level3: "graph TD\n  X[Input x] --> MUL[Multiply w]\n  W[Weight w] --> MUL\n  MUL --> ADD[Add Bias b]\n  B[Bias b] --> ADD\n  ADD --> Y[Output y]",
    complexity: 5,
    mentorTip: "첫 번째 인공 뉴런 구현을 축하합니다! y = wx + b는 딥러닝의 가장 기초적인 선형 결합 구조입니다."
  },
  'quest_ai_02': {
    level1: "1. 입력을 받아 0과 비교함\n2. 양수면 그대로 반환, 음수면 0으로 처리\n3. 결과값 출력",
    level2: "활성화 함수 ReLU를 통해 음수 신호를 차단하고 신경망에 비선형적 특성을 부여합니다.",
    level3: "graph TD\n  IN[Input x] --> IF{x > 0?}\n  IF -->|Yes| RET_X[Return x]\n  IF -->|No| RET_0[Return 0]",
    complexity: 8,
    mentorTip: "ReLU는 현대 딥러닝에서 가장 많이 쓰이는 활성화 함수입니다. 단순한 if문 하나가 AI의 성능을 결정하죠!"
  },
  'quest_ai_03': {
    level1: "1. 예측과 정답의 차이를 구함(diff)\n2. 차이를 스스로 곱함(Square)\n3. 최종 Loss 반환",
    level2: "평균 제곱 오차(MSE)의 핵심인 '차이의 제곱'을 통해 오차의 크기를 양수화하여 측정합니다.",
    level3: "graph TD\n  P[Predict] --> SUB[Difference]\n  T[Target] --> SUB\n  SUB --> SQ[Square diff*diff]\n  SQ --> L[Loss Value]",
    complexity: 6,
    mentorTip: "제곱을 하는 이유는 음수를 없애기 위해서이기도 하지만, 큰 오차에 더 큰 벌점을 주기 위해서이기도 합니다."
  },
  'quest_ai_04': {
    level1: "1. 기울기에 학습률을 곱해 이동량 계산\n2. 가중치에서 이동량을 빼서 갱신\n3. 업데이트된 값 저장",
    level2: "경사하강법(GD) 원리에 따라 오차가 줄어드는 방향으로 파라미터를 미세하게 조정합니다.",
    level3: "graph TD\n  G[Gradient] --> MUL[Multiply LR]\n  LR[Learning Rate] --> MUL\n  W[Weight] --> SUB[W - Step]\n  MUL --> SUB\n  SUB --> NEW[Updated W]",
    complexity: 10,
    mentorTip: "학습률(LR)은 AI의 보폭입니다. 너무 크면 길을 잃고, 너무 작으면 거북이처럼 느려지니 주의하세요!"
  }
};

// --- 2. Props & Emits ---
const props = defineProps({
  initialQuestIndex: { type: Number, default: 0 }
});
const emit = defineEmits(['close', 'quest-complete']);

// --- 3. Reactive State ---
const apiKey = import.meta.env.VITE_GEMINI_API_KEY || "";
const activeQuestIndex = ref(0);
const currentQuest = computed(() => aiQuests[activeQuestIndex.value] || aiQuests[0]);
const hasNextQuest = computed(() => activeQuestIndex.value < aiQuests.length - 1);
const activeLevel = ref(1);
const generatedResults = ref(null);
const loading = ref(false);
const activeTab = ref('analyze');
const practiceSubTab = ref('categories'); // 'categories', 'stages'
const selectedCategory = ref('forward');
const practiceMode = ref('none');
const levels = ref(LEVELS);

// Chatbot State
const chatMessages = ref([
  { role: 'assistant', text: '안녕하세요! 설계 멘토 오리입니다. 현재 스테이지에 대해 궁금한 점이 있다면 무엇이든 물어보세요! 꽥!' }
]);
const chatInput = ref('');
const isChatLoading = ref(false);

// Validation State
const showValidationModal = ref(false);
const validationResult = ref(null); // 'success', 'error'
const validationMessage = ref('');

// Gamification State
const userStability = ref(3); // HP
const userXP = ref(0);
const comboStreak = ref(0);
const showLevelUpSplash = ref(false);
const triggerShake = ref(false);
const triggerGlitch = ref(false);

const mentorImage = computed(() => {
  return userStability.value <= 1 ? "/image/mentor/duck_sad.png" : "/image/mentor/duck.png";
});

const userLevel = computed(() => {
  return Math.floor(userXP.value / 1000) + 1;
});

const nextLevelXP = computed(() => {
  return userLevel.value * 1000;
});

const xpProgress = computed(() => {
  const currentLevelBaseXP = (userLevel.value - 1) * 1000;
  const relativeXP = userXP.value - currentLevelBaseXP;
  return (relativeXP / 1000) * 100;
});

const currentClass = computed(() => {
  if (userLevel.value >= 10) return "Master Architect";
  if (userLevel.value >= 7) return "Lead Architect";
  if (userLevel.value >= 5) return "Senior Engineer";
  if (userLevel.value >= 3) return "Junior Engineer";
  return "Engineering Intern";
});

// Chatbot State
const userPuzzleSolution = ref([]);
const shuffledPalette = ref([]);

// --- 4. Helper Functions ---
const initQuestBlocks = () => {
  if (!currentQuest.value || !currentQuest.value.cards) {
    shuffledPalette.value = [];
    userPuzzleSolution.value = [];
    return;
  }
  shuffledPalette.value = [...currentQuest.value.cards]
    .sort(() => Math.random() - 0.5)
    .map(card => ({ ...card }));
  userPuzzleSolution.value = [];
  generatedResults.value = null;
};

const getInjectedCode = () => {
  if (userPuzzleSolution.value.length === 0) return "";
  const functionName = currentQuest.value?.validation?.execution?.function_name || "process_logic";
  let code = `def ${functionName}():\n`;
  userPuzzleSolution.value.forEach(block => {
    const indentLevel = block.indent || 0;
    const line = "    " + "    ".repeat(indentLevel) + (block.text_py || "# code block");
    code += line + "\n";
  });
  return code;
};

// --- 5. Logic & Methods ---
const useCard = (index) => {
  const card = shuffledPalette.value.splice(index, 1)[0];
  userPuzzleSolution.value.push(card);
};

const unuseCard = (index) => {
  const card = userPuzzleSolution.value.splice(index, 1)[0];
  shuffledPalette.value.push(card);
};

const sourceCode = computed(() => getInjectedCode());

const renderMermaid = async () => {
  if (activeLevel.value === 3 && generatedResults.value?.level3) {
    await nextTick();
    const container = document.getElementById('mermaid-renderer');
    if (container) {
      try {
        container.removeAttribute('data-processed');
        container.innerHTML = generatedResults.value.level3;
        await mermaid.run({ nodes: [container] });
      } catch (e) {
        container.innerHTML = `<div class="text-red-400 p-4 text-[10px]">Diagram Error</div>`;
      }
    }
  }
};

const analyzeCode = async () => {
  const codeToAnalyze = sourceCode.value;
  if (!codeToAnalyze.trim() || !apiKey) return;
  
  // 1. Validation Step
  const userOrder = userPuzzleSolution.value.map(b => b.id);
  const correctOrder = currentQuest.value.correctSequence;
  const isCorrect = userOrder.length === correctOrder.length && userOrder.every((id, idx) => id === correctOrder[idx]);

  if (isCorrect) {
    validationResult.value = 'success';
    validationMessage.value = currentQuest.value.validation?.feedback?.success || "알고리즘 설계가 정확합니다! 멘토 오리의 심층 분석을 확인해보세요.";
    
    // Grant Reward
    const oldLevel = userLevel.value;
    const reward = currentQuest.value.rewardXP || 100;
    const bonus = Math.floor(comboStreak.value * 10);
    userXP.value += (reward + bonus);
    comboStreak.value++;
    
    // Level Up Check & Chat
    if (userLevel.value > oldLevel) {
      showLevelUpSplash.value = true;
      chatMessages.value.push({ role: 'assistant', text: `축하하꽥! 레벨업이다꽥! 이제 당신은 당당한 ${currentClass.value}가 되었다꽥! 🎉` });
    }
    
    showValidationModal.value = true;
    startAianalysis(codeToAnalyze);
  } else {
    validationResult.value = 'error';
    userStability.value = Math.max(0, userStability.value - 1);
    comboStreak.value = 0;

    // Trigger VFX
    triggerShake.value = true;
    triggerGlitch.value = true;
    setTimeout(() => { triggerShake.value = false; triggerGlitch.value = false; }, 500);
    
    if (userStability.value === 0) {
      validationMessage.value = "시스템 과부하 발생! 설계 안정성이 바닥났다꽥. 잠시 시스템을 재부팅(세션 종료)하고 다시 훈련에 임해보는건 어떻겠냐꽥? 🐥🚨";
      showValidationModal.value = true;
      return;
    }
    
    loading.value = true;
    try {
      // Analyze WRONG order using AI for personalized hint
      const wrongSteps = userPuzzleSolution.value.map(b => b.text_ko).join(' -> ');
      const hintPrompt = `퀘스트: ${currentQuest.value.title}. 의도: ${currentQuest.value.description}. 학습자가 조립한 오답 순서: [${wrongSteps}]. 
      왜 틀렸는지 분석하고, 정답을 바로 알려주지는 말고 하나만 고치도록 유도하는 짧고 친절한 힌트를 1문장으로 주세요. 말 끝에 '꽥'을 붙여주세요.`;

      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contents: [{ parts: [{ text: hintPrompt }] }], generation_config: { temperature: 0.5, max_output_tokens: 200 } })
      });
      const data = await response.json();
      validationMessage.value = data.candidates?.[0]?.content?.parts?.[0]?.text || currentQuest.value.validation?.feedback?.failure || "순서가 조금 틀린 것 같다꽥! 다시 한 번 생각해보꽥.";
    } catch (e) {
      validationMessage.value = currentQuest.value.validation?.feedback?.failure || "로직 흐름이 어색하다꽥! 순서를 다시 조정해보꽥.";
    } finally {
      loading.value = false;
      showValidationModal.value = true;
    }
    return;
  }
};

const startAianalysis = async (codeToAnalyze) => {
  loading.value = true;
  const systemPrompt = `당신은 주니어 개발자를 위한 설계 멘토입니다. [Logic Type: ${currentQuest.value.logic_type}]
  조립된 로직을 분석하여 다음 JSON 형식으로 응답하세요.
  { "level1": "절차적 설명", "level2": "논리적 명세", "level3": "mermaid graph TD 코드", "complexity": 10, "mentorTip": "한국어 조언" }`;

  try {
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: `분석할 코드:\n${codeToAnalyze}` }] }],
        system_instruction: { parts: [{ text: systemPrompt }] },
        generation_config: { response_mime_type: "application/json", temperature: 0.2 }
      })
    });
    const data = await response.json();
    if (data.error) {
       console.error("Gemini API Error Detail:", data.error);
       // 할당량 초과(429)이거나 리소스 고갈 시 목 데이터로 자동 전환
       if ((data.error.code === 429 || data.error.status === 'RESOURCE_EXHAUSTED') && MOCK_ANALYSIS_DB[currentQuest.value?.id]) {
         generatedResults.value = { ...MOCK_ANALYSIS_DB[currentQuest.value.id] };
         console.warn("API quota exceeded, falling back to mock data for:", currentQuest.value.id);
       } else { 
         alert(`API 오류 (${data.error.code}): ${data.error.message}`); 
       }
       loading.value = false; return;
    }
    
    let rawText = data.candidates[0].content.parts[0].text;
    const jsonMatch = rawText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      generatedResults.value = JSON.parse(jsonMatch[0].trim());
    } else {
      throw new Error("Invalid JSON format from AI");
    }
  } catch (error) { 
    console.error("Analysis failed", error);
    alert("분석 결과 처리 중 오류가 발생했습니다. (잠시 후 다시 시도해주세요)"); 
  } finally { loading.value = false; }
};

const closeValidationModal = () => {
  showValidationModal.value = false;
};

const selectCategory = (id) => {
  selectedCategory.value = id;
  practiceSubTab.value = 'stages';
};

const startStage = (quest) => {
  const globalIndex = aiQuests.findIndex(q => q.id === quest.id);
  activeQuestIndex.value = globalIndex !== -1 ? globalIndex : 0;
  activeTab.value = 'analyze';
  practiceMode.value = selectedCategory.value;
  generatedResults.value = null;
  initQuestBlocks();
};

const startPractice = (type) => {
  selectedCategory.value = type;
  practiceSubTab.value = 'stages';
};

const startChallenge = () => {
  selectedCategory.value = 'reverse';
  practiceSubTab.value = 'stages';
};

const sendChatMessage = async () => {
  if (!chatInput.value.trim() || isChatLoading.value) return;

  const userText = chatInput.value;
  chatMessages.value.push({ role: 'user', text: userText });
  chatInput.value = '';
  isChatLoading.value = true;

  try {
    const contextStr = `현재 스테이지: ${currentQuest.value.title}. 로직 유형: ${currentQuest.value.logic_type}. 설명: ${currentQuest.value.description}. 힌트: ${currentQuest.value.validation?.execution?.implementation_hint?.main || ""}`;
    const systemPrompt = `당신은 주니어 개발자를 위한 설계 멘토 '오리'입니다. ${contextStr}. 사용자의 설계 질문에 친절하고 짧게 답해주세요. 말 끝마다 '꽥'을 붙여주세요.`;

    const contents = chatMessages.value.map(m => ({ 
      role: m.role === 'assistant' ? 'model' : 'user', 
      parts: [{ text: m.text }] 
    }));

    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        contents, 
        system_instruction: { parts: [{ text: systemPrompt }] },
        generation_config: { temperature: 0.7, max_output_tokens: 300 } 
      })
    });

    const data = await response.json();
    
    if (data.error) {
       console.error("Chat API Error:", data.error);
       // 할당량 초과 시 로컬 지능형 폴백
       if (data.error.code === 429 || data.error.status === 'RESOURCE_EXHAUSTED') {
         let fallbackText = `미안하꽥! 지금 질문이 너무 많아서 잠시 쉬어야겠다꽥. 하지만 이 문제의 핵심은 [${currentQuest.value.logic_type}]이라꽥! ${currentQuest.value.validation?.execution?.implementation_hint?.main || "블록 순서를 잘 고민해보꽥!"} 화이팅하꽥!`;
         
         if (userText.includes('의도') || userText.includes('이유')) {
           fallbackText = `이 문제의 의도는 [${currentQuest.value.title}]을(를) 통해 시스템의 논리 구조를 이해하는 거다꽥! ${currentQuest.value.description} 이 부분을 집중해서 조립해보꽥!`;
         } else if (userText.includes('도움') || userText.includes('힌트') || userText.includes('모르')) {
           fallbackText = `힌트를 주겠다꽥! ${currentQuest.value.validation?.execution?.implementation_hint?.sub || "블록의 색상과 아이콘을 힌트로 삼아서 순차적으로 배치해보꽥."} 포기하지 마라꽥!`;
         }
         
         chatMessages.value.push({ role: 'assistant', text: fallbackText });
         return;
       }
       throw new Error(data.error.message);
    }

    const botText = data.candidates[0].content.parts[0].text;
    chatMessages.value.push({ role: 'assistant', text: botText });
  } catch (e) {
    console.error("Chat Error:", e);
    chatMessages.value.push({ role: 'assistant', text: "미안하꽥! 일시적인 통신 오류가 발생했다꽥. 다시 말해달라꽥!" });
  } finally {
    isChatLoading.value = false;
    nextTick(() => {
      const el = document.getElementById('chat-scroll');
      if (el) el.scrollTop = el.scrollHeight;
    });
  }
};

const handleNextQuest = () => {
  if (hasNextQuest.value) {
    activeQuestIndex.value++;
    activeLevel.value = 1;
    generatedResults.value = null;
    initQuestBlocks();
  } else {
    handleCompleteQuest();
  }
};

const handleCompleteQuest = () => {
  emit('quest-complete', activeQuestIndex.value);
  emit('close');
};

// --- 6. Lifecycle & Watches ---
onMounted(() => {
  initQuestBlocks();
  mermaid.initialize({
    startOnLoad: false, theme: 'dark', securityLevel: 'loose', fontFamily: 'JetBrains Mono',
    themeVariables: { primaryColor: '#6366f1', primaryTextColor: '#fff', primaryBorderColor: '#6366f1', lineColor: '#818cf8', secondaryColor: '#1e293b', tertiaryColor: '#0f172a' }
  });
});
watch([activeLevel, generatedResults], () => { renderMermaid(); }, { immediate: false });
watch(() => currentQuest.value, initQuestBlocks);

const practices = ref([
  { id: "forward", title: "Puzzle Solve", subtitle: "로직 퍼즐 훈련", description: "블록 조립을 통해 알고리즘 설계 능력을 키웁니다.", badge: "Puzzle", badgeColor: "bg-emerald-500/10 text-emerald-400" },
  { id: "reverse", title: "Logic Analysis", subtitle: "시스템 분석", description: "설계도를 추출하여 고수준 의도를 파악합니다.", badge: "Analysis", badgeColor: "bg-blue-500/10 text-blue-400" }
]);
</script>

<style scoped>
.logic-mirror-modal-overlay { position: fixed; inset: 0; background: rgba(2, 6, 23, 0.9); backdrop-filter: blur(32px); z-index: 10000; display: flex; align-items: center; justify-content: center; padding: 2rem; animation: fadeIn 0.4s ease-out; }
.logic-mirror-container { position: relative; width: 98%; max-width: 1800px; height: 94vh; background: #0f172a; border-radius: 3rem; border: 1px solid rgba(255, 255, 255, 0.1); display: flex; overflow: hidden; box-shadow: 0 100px 200px -50px rgba(0, 0, 0, 0.9); font-family: 'Inter', system-ui, sans-serif; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.modal-close-btn { position: absolute; top: 2rem; right: 2rem; width: 44px; height: 44px; background: rgba(255, 255, 255, 0.05); border-radius: 1rem; color: #64748b; display: flex; align-items: center; justify-content: center; z-index: 1000; transition: all 0.3s; }
.modal-close-btn:hover { background: #ef4444; color: white; transform: rotate(90deg); }

/* Puzzle Blocks */
.puzzle-block { position: relative; border-radius: 12px; box-shadow: 0 4px 0 rgba(0,0,0,0.5); border-top: 1px solid rgba(255,255,255,0.2); transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); user-select: none; }
/* HUD Design System */
.logic-mirror-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background-color: rgba(0,0,0,0.6);
  backdrop-filter: blur(8px);
  animation: fadeIn 0.5s ease-out;
}

.logic-mirror-container {
  background-color: #0a0e17;
  width: 100%;
  max-width: 1400px;
  height: 95vh;
  border-radius: 0;
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  animation: scaleIn 0.3s ease-out;
}

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

@keyframes scanline {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}

@keyframes progressStripes {
  from { background-position: 0 0; }
  to { background-position: 40px 0; }
}

.animate-progress-stripes {
  background-image: linear-gradient(
    45deg, 
    rgba(255,255,255,0.1) 25%, 
    transparent 25%, 
    transparent 50%, 
    rgba(255,255,255,0.1) 50%, 
    rgba(255,255,255,0.1) 75%, 
    transparent 75%, 
    transparent
  );
  background-size: 40px 40px;
  animation: progressStripes 2s linear infinite;
}

.animate-shimmer {
  animation: shimmer 2s linear infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.shadow-neon {
  filter: drop-shadow(0 0 10px rgba(0, 243, 255, 0.3));
}

.custom-scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar-thin::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
}
.custom-scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(0, 243, 255, 0.2);
  border-radius: 2px;
}

/* Original Legacy Styles Refactoring... */
.sidebar {
  background: #020408;
}

.modal-close-btn {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 50;
  color: rgba(255,255,255,0.4);
  transition: all 0.3s;
}
.modal-close-btn:hover {
  color: #ef4444;
  transform: rotate(90deg);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
@keyframes glitch {
  0% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
  100% { transform: translate(0); }
}
.animate-glitch {
  animation: glitch 0.2s ease infinite;
}
</style>