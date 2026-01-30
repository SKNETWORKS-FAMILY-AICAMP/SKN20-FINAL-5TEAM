<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in" @click.self="$emit('close')">
    <div class="bg-[#0a0e17] w-full max-w-7xl h-[90vh] rounded-3xl border border-white/10 shadow-2xl overflow-hidden flex flex-col relative animate-scale-in">
      
    <!-- HUD Header -->
    <header class="h-20 border-b border-white/5 bg-[#07090e] flex justify-between items-center px-10 relative overflow-hidden shrink-0">
      <div class="flex items-center space-x-6 z-10">
        <!-- Exact Logo Match -->
        <div class="w-10 h-10 bg-[#117e96] rounded flex items-center justify-center">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 8L11 12L7 16M13 16H17" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="space-y-0">
          <h1 class="font-black text-2xl tracking-tighter text-white uppercase italic leading-none">PROJECT: RE-BOOT</h1>
          <div class="text-[12px] font-bold text-cyan-400/60 uppercase tracking-widest mt-1">
            Stage {{ currentStep }}: Data Cleaning Protocol
          </div>
        </div>
      </div>

      <div class="flex items-center gap-8 z-10">
        <div class="flex items-center gap-2 font-mono text-xs">
          <span class="text-gray-500 uppercase tracking-widest">SYS_STATUS:</span>
          <span class="text-[#4ade80] font-black animate-pulse">STABLE</span>
        </div>
        
        <button 
          @click="$emit('close')" 
          class="flex items-center justify-center w-10 h-10 rounded hover:bg-white/5 transition-all text-gray-500 hover:text-white"
        >
          <X class="w-6 h-6" />
        </button>
      </div>
      
      <!-- Top Neon Line -->
      <div class="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent"></div>
    </header>



    <!-- Main Content -->
    <main class="flex-1 p-6 lg:p-12 max-w-7xl mx-auto w-full relative flex flex-col min-h-0 overflow-y-auto custom-scrollbar bg-[#07090e]">
      <!-- Glow Decor -->
      <div class="absolute top-0 left-1/4 w-[600px] h-[600px] bg-cyan-500/[0.03] rounded-full blur-[120px] pointer-events-none"></div>
      <div class="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-pink-500/[0.03] rounded-full blur-[120px] pointer-events-none"></div>


      <!-- HUD Progress (Pill Style Match) -->
      <div v-if="currentStep <= 4" class="max-w-6xl mx-auto w-full mb-12 px-4 shrink-0">
        <div class="grid grid-cols-4 gap-6 h-3">
           <div 
             v-for="i in 4" 
             :key="i"
             class="relative h-full transition-all duration-700 rounded-full bg-white/10"
           >
             <div 
               v-if="i <= currentStep" 
               class="absolute inset-0 bg-cyan-400 rounded-full shadow-[0_0_20px_rgba(0,243,255,0.6)]"
               :class="i === currentStep ? 'animate-pulse' : ''"
             ></div>
           </div>
        </div>
      </div>


      <!-- STAGE 1: Quiz (Refined Clean Aesthetic) -->
      <div v-if="currentStep === 1" class="grid grid-cols-1 lg:grid-cols-[1fr_1.2fr] gap-8 animate-fade-in-up items-stretch max-w-6xl mx-auto w-full flex-1 min-h-0">
        <!-- Info Card -->
        <div class="bg-[#0b0e14] border border-white/5 p-10 rounded-2xl flex flex-col relative overflow-hidden group shadow-2xl">
          <div class="flex items-center gap-4 mb-4">
            <div class="p-3 bg-cyan-500/10 rounded-xl border border-cyan-500/20">
              <Cpu class="text-cyan-400 w-8 h-8" />
            </div>
            <h2 class="text-3xl font-black text-[#00f3ff] italic tracking-tighter uppercase">Stage 1: 오염된 기억</h2>
          </div>

          <div class="space-y-8 text-gray-400 leading-relaxed font-medium">
            <p class="text-[17px] text-[#8b949e]">Lion의 메모리 뱅크가 손상되었습니다. 복구 프로세스를 시작하기 전에 가장 중요한 원칙을 확인해야 합니다.</p>
            
            <div class="bg-[#0d1117] p-8 border border-white/5 rounded-xl relative overflow-hidden group/gigo mt-auto">
               <h3 class="text-cyan-400 font-bold text-lg mb-4 flex items-center gap-2">
                 핵심 개념: GIGO (Garbage In, Garbage Out)
               </h3>
               <p class="text-lg text-white font-medium leading-relaxed">
                 "쓰레기가 들어가면 쓰레기가 나온다."
               </p>
               <p class="text-sm text-[#8b949e] mt-2">
                 모델이 아무리 뛰어나도, 학습 데이터의 품질이 낮으면 결과물도 엉망이 됩니다.
               </p>
            </div>
          </div>
        </div>

        <!-- Quiz Card -->
        <div class="bg-[#0b0e14] border border-white/5 p-10 rounded-2xl flex flex-col shadow-2xl">
          <h3 class="text-2xl font-black text-white mb-10 leading-tight">Q. 다음 중 데이터 전처리를 수행해야 하는 가장 타당한 이유는?</h3>

          <div class="space-y-4 flex-1">
            <button
              v-for="(opt, idx) in step1Options"
              :key="idx"
              @click="handleStep1Submit(idx)"
              class="w-full text-left p-6 bg-[#161b22] hover:bg-cyan-500/10 border border-transparent hover:border-cyan-500/30 transition-all group flex items-center rounded-xl"
            >
              <span class="flex-1 font-bold text-[#c9d1d9] group-hover:text-white transition-colors">
                {{ idx + 1 }}. {{ opt }}
              </span>
            </button>
          </div>
        </div>
      </div>


      <!-- STAGE 2: Pseudocode -->
      <div v-if="currentStep === 2" class="grid grid-cols-1 lg:grid-cols-2 gap-10 animate-fade-in-up items-stretch max-w-7xl mx-auto w-full flex-1 min-h-0">
        <div class="flex flex-col gap-10 min-h-0">
          <!-- Problem Definition HUD -->
          <div class="bg-black/40 border border-cyan-500/20 p-10 hud-box-clip flex-1 relative overflow-hidden group min-h-[200px]">
            <h3 class="text-2xl font-black text-white italic mb-6 flex items-center gap-3">
              <CodeIcon class="w-6 h-6 text-cyan-400" /> MISSION_OBJECTIVE
            </h3>
            <div class="space-y-6">
              <p class="text-gray-300 leading-relaxed font-bold text-lg">
                리스트에 담긴 뉴스 제목들 중 <span class="bg-cyan-500/20 text-cyan-300 px-2 rounded">"광고"</span>, <span class="bg-cyan-500/20 text-cyan-300 px-2 rounded">"클릭"</span>이 포함된 제목과, <span class="bg-pink-500/20 text-pink-300 px-2 rounded">길이가 5자 미만</span>인 데이터를 제거하는 필터링 로직을 설계하십시오.
              </p>
              
              <div class="h-px bg-gradient-to-r from-cyan-500/50 to-transparent"></div>
              
              <div class="flex flex-wrap gap-2 uppercase font-mono text-[9px]">
                <div v-for="tag in ['iteration', 'conditional', 'filtering', 'data_cleaning']" :key="tag" class="px-2 py-1 bg-white/5 border border-white/10 text-gray-500">{{ tag }}</div>
              </div>
            </div>
            
            <!-- Matrix background effect -->
            <div class="absolute bottom-4 right-4 text-[40px] font-black text-white/[0.02] select-none pointer-events-none">0101101</div>
          </div>

          <!-- Lion Chat HUD -->
          <div class="bg-black/60 border border-white/5 hud-box-clip flex-[0.8] flex flex-col overflow-hidden relative max-h-[400px]">
            <div class="bg-white/5 p-3 text-[10px] font-mono text-cyan-400/50 border-b border-white/5 flex justify-between items-center tracking-widest px-6 italic uppercase">
              <span>Agent_Link_Active</span>
              <span class="flex items-center gap-2"><div class="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse"></div> ENCRYPTED</span>
            </div>
            <div ref="chatContainer" class="flex-1 overflow-y-auto p-8 space-y-6 custom-scrollbar">
              <div
                v-for="(msg, idx) in chatMessages"
                :key="idx"
                class="flex flex-col"
                :class="msg.sender === 'User' ? 'items-end' : 'items-start'"
              >
                <span class="text-[8px] text-gray-500 font-black mb-2 uppercase tracking-tighter">{{ msg.sender }}_ID</span>
                <div
                  class="max-w-[90%] p-4 text-sm leading-relaxed hud-button-clip"
                  :class="msg.sender === 'Lion' ? 'bg-cyan-500/10 text-cyan-100 border border-cyan-500/20' : 'bg-white/5 text-white border border-white/10'"
                >
                  {{ msg.text }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area HUD -->
        <div class="bg-white/[0.02] border border-white/10 p-10 hud-box-clip flex flex-col items-stretch relative">
          <div class="flex items-center justify-between mb-8">
            <h3 class="text-xl font-black text-white tracking-widest">PSEUDO_COMPILER</h3>
            <div class="text-[9px] font-mono text-gray-500 flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></span> WAITING_FOR_INPUT
            </div>
          </div>
          
          <div class="relative flex-1 flex flex-col">
            <textarea
              v-model="pseudoInput"
              class="flex-1 bg-black/40 text-cyan-100 p-8 font-mono text-sm border-2 border-white/5 focus:border-cyan-500/50 focus:outline-none resize-none leading-relaxed placeholder-gray-700 transition-all custom-scrollbar shadow-inner"
              placeholder="[SYSTEM]: Input logic sequence here...&#10;> 1. Fetch news data...&#10;> 2. Validate keywords..."
            ></textarea>
            
            <!-- Corner Accents -->
            <div class="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-cyan-500/30"></div>
            <div class="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-cyan-500/30"></div>
          </div>

          <button
            @click="submitStep2"
            class="mt-10 group relative transition-all active:scale-[0.98]"
          >
            <div class="absolute -inset-1 bg-gradient-to-r from-cyan-600 to-blue-700 rounded-lg blur opacity-25 group-hover:opacity-100 transition duration-1000"></div>
            <div class="relative w-full py-5 bg-black border border-cyan-500/50 text-white font-black text-lg tracking-widest uppercase hover:bg-cyan-500/10 transition-all hud-button-clip">
              Submit_Logic_Node
            </div>
          </button>
        </div>
      </div>



      <!-- STAGE 3: Python Blocks Refined -->
      <div v-if="currentStep === 3" class="grid grid-cols-1 lg:grid-cols-[1fr_1.2fr] gap-10 animate-fade-in-up items-stretch max-w-7xl mx-auto w-full flex-1 min-h-0">
        <!-- Left: Code Block Storage -->
        <div class="bg-[#0f1219]/60 border border-white/5 p-10 hud-box-clip flex flex-col relative group min-h-0">
          <div class="absolute inset-0 bg-gradient-to-b from-cyan-500/[0.02] to-transparent pointer-events-none"></div>
          
          <div class="mb-10 relative shrink-0">
            <h3 class="text-2xl font-black text-cyan-400 italic tracking-tighter uppercase mb-2">코드 블록 보관함</h3>
            <p class="text-gray-400 text-sm leading-relaxed font-bold">
              아래 블록을 클릭하여 선택한 후, 오른쪽 코드의 빈칸을 클릭해 채워넣으세요.
            </p>
            <div class="absolute -left-10 top-0 w-1 h-full bg-cyan-500/50"></div>
          </div>
          
          <!-- Blocks Grid - Fixed Height Scrollable -->
          <div class="grid grid-cols-2 gap-4 flex-1 overflow-y-auto custom-scrollbar pr-4 min-h-0">
            <button
              v-for="block in blocks"
              :key="block.id"
              @click="selectedBlock = block"
              class="group relative h-28 transition-all active:scale-[0.98]"
            >
              <div 
                class="absolute inset-0 bg-black/40 border transition-all duration-300 hud-box-clip"
                :class="selectedBlock && selectedBlock.id === block.id ? 'border-cyan-500 shadow-[0_0_20px_rgba(0,243,255,0.2)] bg-cyan-500/10' : 'border-white/10 group-hover:border-cyan-500/30'"
              ></div>
              <div class="relative h-full flex items-center justify-center px-4">
                <span 
                  class="text-base font-black tracking-widest uppercase transition-all"
                  :class="selectedBlock && selectedBlock.id === block.id ? 'text-cyan-400' : 'text-gray-400 group-hover:text-cyan-300'"
                >
                  {{ block.text }}
                </span>
              </div>
            </button>
          </div>

          <!-- Tip Box -->
          <div class="mt-8 p-6 bg-white/[0.02] border-l-2 border-pink-500 hud-box-clip relative overflow-hidden shrink-0">
             <div class="absolute top-0 right-0 w-16 h-16 bg-pink-500/5 rotate-45 translate-x-8 -translate-y-8"></div>
             <p class="text-[13px] text-gray-400 leading-relaxed font-bold italic">
               <span class="text-pink-500 not-italic font-black mr-2">Tip:</span> continue는 건너뛰기, break는 멈추기입니다. 우리는 끝까지 다 검사해야 해요.
             </p>
          </div>
        </div>

        <!-- Right: Python Executor -->
        <div class="bg-[#1a1a1a] border border-white/5 hud-box-clip flex flex-col relative overflow-hidden group shadow-2xl min-h-0">
          <!-- source header -->
          <div class="p-4 px-8 flex justify-end items-center shrink-0">
             <span class="text-[11px] font-mono text-gray-600 uppercase tracking-widest italic">data_cleaning.py</span>
          </div>

          <div class="flex-1 p-12 relative overflow-y-auto custom-scrollbar min-h-0" style="font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;">
            <!-- Code Structure -->
            <div class="text-[17px] leading-[2.4] font-medium text-gray-300">
              <pre>def clean_news_data(news_list):
    cleaned_data = []

    for news in news_list:
        <span class="text-gray-500 italic"># 1. 길이 체크 및 키워드 필터링</span>
        if len(news) < 5 or "광고" in news:</pre>
              
              <!-- Blank A -->
              <div class="flex items-center gap-4 pl-12 h-14">
                 <div 
                   @click="fillBlank('blankA')"
                   class="min-w-[200px] border-b-2 transition-all cursor-pointer flex items-center justify-center relative group/blank"
                   :class="pythonBlanks.blankA ? 'border-cyan-500 text-cyan-400' : 'border-gray-700 hover:border-gray-500 bg-white/[0.02]'"
                 >
                   <span class="text-sm font-bold tracking-widest">{{ pythonBlanks.blankA ? pythonBlanks.blankA.text : "__________" }}</span>
                   <div class="ml-4 text-[12px] text-gray-600 font-bold tracking-tighter">__(A)__</div>
                 </div>
              </div>

              <pre class="mt-4">
        <span class="text-gray-500 italic"># 2. 유효한 데이터 저장</span></pre>

              <!-- Blank B -->
              <div class="flex items-center pl-12 h-14">
                <span>cleaned_data.</span>
                <div 
                  @click="fillBlank('blankB')"
                  class="min-w-[200px] border-b-2 transition-all cursor-pointer flex items-center justify-center relative group/blank mx-2"
                  :class="pythonBlanks.blankB ? 'border-cyan-500 text-cyan-400' : 'border-gray-700 hover:border-gray-500 bg-white/[0.02]'"
                >
                  <span class="text-sm font-bold tracking-widest">{{ pythonBlanks.blankB ? pythonBlanks.blankB.text : "__________" }}</span>
                </div>
                <div class="text-[12px] text-gray-600 font-bold tracking-tighter ml-4">__(B)__</div>
              </div>

              <pre class="mt-6">    return cleaned_data</pre>
            </div>

            <!-- Execution Button (Bottom Right) -->
            <div class="absolute bottom-8 right-8">
              <button 
                @click="runSimulation" 
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


      <!-- STAGE 4: Deep Dive HUD -->
      <div v-if="currentStep === 4" class="grid grid-cols-1 lg:grid-cols-2 gap-12 animate-fade-in-up items-stretch max-w-6xl mx-auto w-full flex-1 min-h-0">
        <div class="flex flex-col min-h-0">
          <div class="bg-black/40 border border-pink-500/20 p-10 relative group overflow-hidden flex-1 hud-box-clip min-h-0">
            <div class="absolute top-0 right-0 w-32 h-32 bg-pink-500/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-pink-500/10 transition-all duration-1000"></div>
            
            <div class="flex items-center gap-4 mb-8">
              <div class="p-3 bg-pink-500/10 rounded-xl border border-pink-500/30">
                <Award class="text-pink-400 w-8 h-8" />
              </div>
              <div>
                <h2 class="text-3xl font-black text-white italic tracking-tighter uppercase">ANOMALY_DETECTION</h2>
                <p class="text-[10px] text-pink-500 font-mono tracking-widest">SUB_MODULE: DATA_LOSS_PREVENTION</p>
              </div>
            </div>

            <div class="space-y-8 text-gray-400 leading-relaxed font-medium">
              <p class="text-lg text-white/90">전처리가 지나치게 완벽하면, 유효한 데이터까지 '오염물'로 분류될 위험이 있습니다.</p>
              
              <div class="relative pt-6">
                <div class="absolute top-0 left-0 w-8 h-1 bg-pink-500"></div>
                <h3 class="text-pink-300 font-black text-xs uppercase tracking-[0.3em] mb-4">ENGINEERING ISSUE: TRADE-OFF</h3>
                <div class="bg-pink-500/5 p-8 border border-pink-500/10 relative overflow-hidden group">
                   <p class="text-xl text-white italic mb-4 font-black">"False Positives vs Information Loss"</p>
                   <p class="text-sm text-gray-500 leading-relaxed italic">
                     "광고"라는 키워드를 기계적으로 삭제한다면, <span class="text-pink-300">"광고 업계의 동향"</span>과 같은 중요한 뉴스마저 소실될 수 있습니다.
                   </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-6">
          <div class="bg-black/40 border border-white/10 p-10 hud-box-clip flex-1 flex flex-col">
            <h3 class="text-xl font-black text-white mb-8 leading-tight uppercase tracking-tight">Q. 필터링의 부작용을 최소화하고 정보의 가치를 보존하기 위한 최적의 엔지니어링 접근은?</h3>

            <div class="space-y-4">
              <button
                v-for="(opt, idx) in step4Options"
                :key="idx"
                @click="handleStep4Submit(idx)"
                class="w-full text-left p-6 bg-white/[0.02] hover:bg-pink-500/10 border border-white/5 hover:border-pink-500/30 transition-all group relative overflow-hidden hud-button-clip"
              >
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-white/5 border border-white/10 flex items-center justify-center mr-5 text-xs font-mono text-pink-400 group-hover:bg-pink-500 group-hover:text-black transition-all">
                    0{{ idx + 1 }}
                  </div>
                  <span class="flex-1 font-bold text-gray-300 group-hover:text-white transition-colors">{{ opt }}</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>



      <!-- STAGE 5: Final Report HUD Refined -->
      <div v-if="currentStep === 5" class="flex flex-col items-center justify-center animate-fade-in-up py-6 max-w-6xl mx-auto w-full h-full">
        <div class="bg-black/80 border border-cyan-500/20 hud-box-clip w-full p-16 text-center relative overflow-hidden backdrop-blur-3xl group shadow-[0_0_100px_rgba(0,0,0,1)]">
          <!-- Cinematic background grids -->
          <div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:60px_60px] opacity-30"></div>
          <div class="absolute inset-0 bg-gradient-to-t from-cyan-500/10 via-transparent to-transparent"></div>
          
          <div class="relative z-10 space-y-16">
            <!-- Header Section -->
            <div class="space-y-6">
              <div class="inline-block relative">
                 <div class="absolute -inset-8 bg-cyan-500/20 blur-2xl rounded-full scale-110 animate-pulse"></div>
                 <Award class="w-32 h-32 text-cyan-400 mx-auto drop-shadow-[0_0_30px_#00f3ff] relative z-10" />
                 <!-- Decorative Rings -->
                 <div class="absolute inset-0 border-4 border-cyan-500/20 rounded-full animate-ping scale-150 opacity-20"></div>
              </div>
              
              <div class="space-y-2">
                <h2 class="text-6xl font-black text-white italic tracking-tighter uppercase scale-y-110 drop-shadow-[2px_2px_0px_#00f3ff44]">Mission_Restore_Success</h2>
                <div class="h-1.5 w-48 bg-cyan-500 mx-auto shadow-[0_0_20px_#00f3ff]"></div>
                <div class="text-[10px] text-cyan-500/60 font-mono tracking-[0.5em] uppercase mt-4 italic">Final_System_Integrity_Confirmed</div>
              </div>
            </div>

            <!-- Score Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              <div v-for="(val, key, index) in { 'CONCEPT': userScore.step1, 'LOGIC': userScore.step2, 'CODE': userScore.step3, 'DEEP_DIVE': userScore.step4 }" :key="key" 
                   class="bg-white/[0.03] border border-white/5 p-8 hud-box-clip hover:bg-cyan-500/10 transition-all text-left group/card relative animate-in fade-in slide-in-from-bottom-5"
                   :style="{ animationDelay: (400 + index * 100) + 'ms' }">
                <div class="absolute top-0 right-0 p-3 opacity-10 group-hover/card:opacity-30 transition-opacity">
                   <div class="text-[8px] font-mono text-cyan-500 flex flex-col items-end">
                      <span>SEC_{{ index + 1 }}</span>
                      <span>UID_0x{{ (index * 123 + 456).toString(16).toUpperCase() }}</span>
                   </div>
                </div>
                <div class="text-[10px] font-black text-cyan-500/40 uppercase tracking-widest mb-4 italic group-hover/card:text-cyan-400 transition-colors">{{ key }}_CORE</div>
                <div class="flex items-baseline gap-2 mb-6">
                  <span class="text-4xl font-black text-white italic group-hover/card:scale-110 transition-transform origin-left">{{ val }}</span>
                  <span class="text-xs text-gray-700 font-mono">/ 25</span>
                </div>
                <!-- Mini Progress Bar -->
                <div class="h-1 bg-white/5 w-full relative overflow-hidden">
                  <div class="absolute inset-y-0 left-0 bg-cyan-500 transition-all duration-1000" :style="{ width: (val / 25 * 100) + '%' }"></div>
                </div>
              </div>
            </div>

            <!-- Intelligence Review Hardware Module -->
            <div class="bg-black/40 border border-cyan-500/20 p-10 hud-box-clip text-left relative overflow-hidden animate-in fade-in slide-in-from-bottom-10 delay-1000">
               <!-- Scanline effect for this box -->
               <div class="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%)] bg-[length:100%_4px] pointer-events-none opacity-10"></div>
               
               <div class="flex items-start gap-10">
                 <!-- Mascot Placeholder or Icon -->
                 <div class="shrink-0 hidden lg:block">
                    <div class="w-24 h-24 bg-cyan-500/5 border border-cyan-500/20 hud-box-clip flex items-center justify-center relative">
                       <Terminal class="w-10 h-10 text-cyan-400 opacity-40" />
                       <div class="absolute -top-1 -right-1 w-3 h-3 bg-cyan-500 rounded-full animate-pulse shadow-[0_0_10px_#00f3ff]"></div>
                    </div>
                 </div>

                 <div class="flex-1 space-y-6">
                   <h3 class="text-cyan-400 font-black text-xs uppercase tracking-[0.4em] italic flex items-center gap-4">
                     <span class="w-2 h-2 bg-cyan-500 rounded-full animate-ping"></span>
                     Lion_Artificial_Intelligence_Review
                   </h3>
                   <p class="text-[19px] text-gray-200 leading-relaxed font-bold italic border-l-4 border-cyan-500/30 pl-8" v-html="finalReviewText"></p>
                   
                   <div class="flex gap-4 opacity-30 text-[9px] font-mono text-cyan-500 uppercase tracking-tighter">
                      <span>STATUS: ANALYZED</span>
                      <span>COMPLETION: 100%</span>
                      <span>DATA_SYNC: VERIFIED</span>
                   </div>
                 </div>
               </div>
            </div>

            <!-- Final Actions -->
            <div class="flex flex-col sm:flex-row gap-8 justify-center items-center">
              <button
                @click="reloadApp"
                class="group px-14 py-6 bg-white/5 hover:bg-white/10 text-gray-500 hover:text-white font-black uppercase tracking-[0.2em] text-xs border border-white/5 hover:border-white/20 hud-button-clip transition-all active:scale-95 flex items-center gap-4"
              >
                 <RotateCcw class="w-4 h-4 group-hover:rotate-180 transition-transform duration-700" />
                 Recalibrate_System
              </button>
              <button
                @click="$emit('close')"
                class="group px-14 py-6 bg-cyan-600 text-black font-black uppercase tracking-[0.2em] text-xs hud-button-clip hover:bg-cyan-400 hover:shadow-[0_0_30px_#00f3ff] transition-all active:scale-95 flex items-center gap-4"
              >
                 <ChevronRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                 Return_To_Hub_Command
              </button>
            </div>
          </div>
        </div>

        <!-- Duck Component - Repositioned for Step 5 -->
        <div class="fixed bottom-10 right-10 scale-125 z-50">
          <div class="bg-black/60 border border-cyan-500 px-6 py-3 hud-box-clip text-cyan-400 font-black text-[10px] tracking-widest italic mb-2 text-center animate-bounce">
            주니어 오리 (사원)
          </div>
          <Duck class-name="shadow-neon cursor-help animate-in zoom-in slide-in-from-right-20 delay-1500" />
        </div>
      </div>


      <!-- Feedback HUD Modal -->
      <div v-if="feedbackModal.visible" class="fixed inset-0 bg-black/95 flex items-center justify-center z-[110] p-6 backdrop-blur-xl">
        <div class="bg-[#020408] border-2 border-white/10 hud-box-clip p-12 max-w-2xl w-full shadow-[0_0_100px_rgba(0,0,0,1)] relative animate-scale-in">
          <div class="absolute top-0 right-0 p-4 opacity-10">
             <div class="flex gap-2">
                <div v-for="i in 5" :key="i" class="w-1 h-1 bg-white"></div>
             </div>
          </div>

          <div class="flex items-center space-x-6 mb-10">
            <div :class="feedbackModal.isSuccess ? 'bg-green-500/20 text-green-400' : 'bg-pink-500/20 text-pink-400'" class="p-4 border border-current rounded-xl">
              <component
                :is="feedbackModal.isSuccess ? CheckCircle : AlertTriangle"
                class="w-12 h-12"
              />
            </div>
            <h3 class="text-3xl font-black text-white italic tracking-tighter uppercase">{{ feedbackModal.title }}</h3>
          </div>

          <p class="text-xl text-gray-200 mb-10 leading-relaxed font-bold italic border-l-4 px-6" :class="feedbackModal.isSuccess ? 'border-green-500' : 'border-pink-500'">{{ feedbackModal.desc }}</p>
          
          <div class="bg-white/[0.03] p-8 border border-white/5 text-sm font-medium text-gray-400 mb-12 leading-relaxed" v-html="feedbackModal.details"></div>
          
          <div class="flex justify-end">
            <button
              @click="nextStep"
              class="group relative h-16 transition-all active:scale-[0.98]"
            >
               <div class="absolute -inset-1 bg-cyan-500/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition duration-300"></div>
               <div class="relative px-12 h-full bg-cyan-600 text-black font-black uppercase tracking-[0.2em] flex items-center gap-4 hud-button-clip hover:bg-cyan-400 hover:shadow-[0_0_20px_#00f3ff] transition-all">
                  {{ currentStep === 4 ? "GENERATE_REPORT" : "INITIALIZE_NEXT_PROTOCOL" }} 
                  <ChevronRight class="w-6 h-6" />
               </div>
            </button>
          </div>
        </div>
      </div>


      <!-- Duck Helper - Integrated Absolute Positioning (Hidden on Final Report) -->
      <div v-if="currentStep !== 5" class="absolute bottom-10 right-10 z-20 pointer-events-auto">
        <Duck class-name="shadow-neon hover:scale-110 transition-transform cursor-pointer" />
      </div>
    </main>
    </div>
  </div>
</template>

<script setup>
/**
 * 수정일: 2026-01-30
 * 수정내용: HTML 하이브리드 코드를 정식 Vue SFC 구조로 리팩토링 및 Lucide 아이콘 적용
 */
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { 
  Terminal, 
  Cpu, 
  Code as CodeIcon, 
  Award, 
  RotateCcw, 
  ChevronRight, 
  AlertTriangle, 
  CheckCircle,
  X 
} from 'lucide-vue-next'
import Duck from './components/Duck.vue'

const props = defineProps({
  isOpen: { type: Boolean, default: false }
})

const emit = defineEmits(['close'])


// --- State ---
const currentStep = ref(1)
const userScore = reactive({ step1: 0, step2: 0, step3: 0, step4: 0 })

// Step 1 Options
const step1Options = [
  "데이터의 용량을 줄여서 저장 공간을 아끼기 위해",
  "복잡한 모델을 사용하여 학습 속도를 늦추기 위해",
  "노이즈가 섞인 데이터가 모델의 성능을 저하시키는 것을 막기 위해",
  "모든 데이터를 긍정적인 내용으로 바꾸기 위해"
]

// Step 2 Data
const pseudoInput = ref('')
const chatMessages = ref([
  { sender: 'Lion', text: '엔지니어님, 깨어나셨군요. 오염된 데이터를 정화해야 제 기억이 돌아옵니다. 오른쪽 패널에 한글로 로직을 설계해주세요.' }
])
const chatContainer = ref(null)

// Step 3 Data
const blocks = [
  { id: 'b1', text: 'continue' },
  { id: 'b2', text: 'break' },
  { id: 'b3', text: 'append(text)' },
  { id: 'b4', text: 'remove(text)' }
]
const selectedBlock = ref(null)
const pythonBlanks = reactive({ blankA: null, blankB: null })
const simulationOutput = ref('')
const simulationContainer = ref(null)
const isSimulating = ref(false)

const sampleData = [
    "삼성전자 주가 급등",           // 정상
    "광고) 지금 바로 클릭하세요",    // 키워드 필터링 대상
    "날씨",                        // 길이 미만 대상
    "AI 모델의 미래 전망",          // 정상
    "초특가 광고 상품 안내"         // 키워드 필터링 대상
];

// Step 4 Options
const step4Options = [
  "'광고' 단어가 포함된 모든 문서를 무조건 삭제한다.",
  "단순 키워드 매칭 대신, 문맥을 이해하는 AI 모델을 사용하여 필터링한다.",
  "데이터 전처리를 아예 하지 않는다.",
  "사람이 모든 데이터를 직접 읽고 지운다."
]

// Feedback Modal
const feedbackModal = reactive({
  visible: false,
  title: '',
  desc: '',
  details: '',
  isSuccess: true
})

// --- Methods & Logic ---

// Helper: Scroll Chat
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// Watch pseudoInput for hints
watch(pseudoInput, (newVal) => {
  if (newVal.length > 10 && !chatMessages.value.some(m => m.text.includes('시작'))) {
    chatMessages.value.push({ sender: 'Lion', text: '좋습니다. 먼저 데이터를 하나씩 꺼내는 "반복" 구조가 필요해 보입니다.' })
    scrollToBottom()
  }
  if (newVal.includes('만약') && !chatMessages.value.some(m => m.text.includes('조건'))) {
    chatMessages.value.push({ sender: 'Lion', text: '조건문을 잘 작성하고 계시군요. "제거"하거나 "저장"하는 행동도 명시해주세요.' })
    scrollToBottom()
  }
})

// Step 1 Submit
const handleStep1Submit = (idx) => {
  const isCorrect = idx === 2
  userScore.step1 = isCorrect ? 25 : 0
  showFeedback(
    isCorrect ? "✅ 정답: GIGO 원칙의 이해" : "⚠️ 오답: 다시 생각해보세요",
    isCorrect ? "훌륭합니다. '쓰레기가 들어가면 쓰레기가 나온다(Garbage In, Garbage Out)'는 AI 엔지니어링의 제1원칙입니다. 아무리 좋은 모델도 데이터가 더러우면 소용없습니다." : "데이터의 양보다는 '질'이 우선입니다. 노이즈가 섞인 데이터는 모델의 판단력을 흐리게 만듭니다.",
    "활용 사례: 실제 현업에서도 전체 프로젝트 기간의 80%를 데이터 전처리에 사용합니다. 금융 사기 탐지 모델에서 정상 거래를 사기로 오해하지 않게 하려면 노이즈 제거가 필수적입니다.",
    isCorrect
  )
}

// Step 2 Submit
function submitStep2() {
    const code = pseudoInput.value.trim();
    
    // 1. 분석을 위한 규칙 정의 (정규표현식 활용)
    const rules = {
        loop: {
            pattern: /(반복|하나씩|꺼내|모든|리스트|for|each)/,
            desc: "데이터를 하나씩 확인하는 '반복' 구조"
        },
        condition: {
            pattern: /(만약|일 때|경우|라면|if|조건)/,
            desc: "특정 데이터를 선별하는 '조건분기'"
        },
        keywordCheck: {
            pattern: /(광고|클릭|길이|5자|미만)/,
            desc: "문제에서 요구한 '필터링 기준' 언급"
        },
        action: {
            pattern: /(제거|삭제|버린|제외|건너뛰|저장|추가|append|continue)/,
            desc: "조건에 따른 '처리 행동'"
        }
    };

    let score = 0;
    let feedbackItems = [];
    let passedCount = 0;

    // 2. 각 규칙별 검증 진행
    Object.keys(rules).forEach(key => {
        const rule = rules[key];
        if (rule.pattern.test(code)) {
            score += 6.25; // 25점 만점 기준 (4가지 항목)
            passedCount++;
            feedbackItems.push(`<span class="text-green-400">✔ ${rule.desc}가 포함되었습니다.</span>`);
        } else {
            feedbackItems.push(`<span class="text-gray-500">✘ ${rule.desc}가 누락되었거나 불분명합니다.</span>`);
        }
    });

    // 3. 논리적 순서 추가 검증 (보너스 점수 또는 정교화)
    const loopPos = code.search(rules.loop.pattern);
    const condPos = code.search(rules.condition.pattern);
    
    let logicBonusText = "";
    if (loopPos !== -1 && condPos !== -1 && loopPos < condPos) {
        score = Math.min(25, score + 2.5); // 순서가 맞으면 가산점
        logicBonusText = "<li class='text-cyan-400'>✨ 훌륭합니다! 데이터를 먼저 꺼내고 조건을 검사하는 논리적 순서가 명확합니다.</li>";
    }

    userScore.step2 = Math.floor(score);

    // 4. 피드백 구성
    const listHtml = `
        <div class="space-y-2">
            <p class="font-bold border-b border-white/10 pb-1">알고리즘 구성 요소 체크:</p>
            <ul class="text-xs space-y-1">${feedbackItems.map(f => `<li>${f}</li>`).join('')}</ul>
            <div class="mt-4 pt-2 border-t border-white/10 text-sm">
                ${logicBonusText}
                <p class="mt-2 text-pink-400">Lion의 심사평: ${
                    passedCount >= 4 
                    ? "완벽한 설계입니다. 이제 이 논리를 파이썬 코드로 옮길 준비가 되셨군요!" 
                    : "설계가 조금 추상적입니다. '무엇을(대상)', '어떻게(방법)' 처리할지 명확히 적어보세요."
                }</p>
            </div>
        </div>
    `;

    showFeedback(
        score >= 20 ? "💡 논리 설계 평가: 우수함" : "🔧 논리 설계 평가: 보완 필요",
        "Lion의 알고리즘 엔진이 엔지니어님의 의사코드를 분석했습니다.",
        listHtml,
        score >= 15
    );
}

// Step 3 Logic
const selectBlock = (block) => {
  selectedBlock.value = block
}

const fillBlank = (blankId) => {
  if (!selectedBlock.value) return
  pythonBlanks[blankId] = selectedBlock.value
  selectedBlock.value = null
}

// Step 3 Simulation
const runSimulation = () => {
    const bA = pythonBlanks.blankA?.text; // continue, break 등
    const bB = pythonBlanks.blankB?.text; // append(text) 등
    
    if (!bA || !bB) {
        simulationOutput.value = '<span class="text-pink-500">Error: 빈칸을 모두 채워야 실행할 수 있습니다.</span>';
        return;
    }

    isSimulating.value = true;
    simulationOutput.value = '<span class="text-cyan-500">Initializing cleaning_protocol.v3...</span><br>';
    
    let cleaned_data = [];
    let log = '<span class="text-cyan-400 font-black tracking-widest uppercase text-[10px] italic">Checking system_integrity_protocol...</span><br>';

    for (let news of sampleData) {
        log += `<span class="text-gray-500 italic mt-2">Checking_Node: "${news}"</span><br>`;
        
        if (news.length < 5 || news.includes("광고")) {
            if (bA === 'continue') {
                log += `<span class="text-yellow-500 font-mono">&nbsp;&nbsp;[PROT_SKIP]: 필터링 조건 일치.</span><br>`;
                continue; 
            } else if (bA === 'break') {
                log += `<span class="text-red-500 font-mono">&nbsp;&nbsp;[PROT_HALT]: 반복문 강제 종료됨.</span><br>`;
                break;
            }
        }

        if (bB === 'append(text)') {
            cleaned_data.push(news);
            log += `<span class="text-green-500 font-mono">&nbsp;&nbsp;[DATA_SAVE]: 데이터가 cleaned_data에 커밋됨.</span><br>`;
        } else if (bB === 'remove(text)') {
            log += `<span class="text-pink-500 font-mono">&nbsp;&nbsp;[DATA_ERROR]: 삭제 명령이 유효하지 않음.</span><br>`;
        }
    }

    log += `<br><strong class="text-white bg-cyan-700/30 px-2 py-1 italic tracking-widest uppercase text-[10px]">SYNC_COMPLETED: [${cleaned_data.join(', ')}]</strong>`;
    
    // Simulate a bit of delay for effect
    setTimeout(() => {
        simulationOutput.value = log;
        isSimulating.value = false;
        nextTick(() => {
            if (simulationContainer.value) {
                simulationContainer.value.scrollTop = simulationContainer.value.scrollHeight;
            }
        });
        
        // 점수 및 최종 제출 로직 연동
        submitStep3(); 
    }, 800);
}

const submitStep3 = () => {
  const bA = pythonBlanks.blankA?.text === 'continue'
  const bB = pythonBlanks.blankB?.text === 'append(text)'

  let score = 0
  if (bA) score += 12
  if (bB) score += 13

  userScore.step3 = score
  showFeedback(
    score === 25 ? "🐍 파이썬 구현: 완벽함" : "🐍 파이썬 구현: 일부 오류",
    score === 25 ? "논리를 코드로 완벽하게 변환하셨습니다." : "일부 로직이 의도와 다르게 동작할 수 있습니다.",
    `<div class="space-y-2"><p><strong>설명:</strong></p><p>1. <code>continue</code>는 현재 반복을 건너뛰고 다음 데이터로 넘어갑니다.</p><p>2. 유효한 데이터만 리스트에 <code>append</code> 해야 메모리를 효율적으로 사용합니다.</p></div>`,
    score > 15
  )
}

// Step 4 Submit
const handleStep4Submit = (idx) => {
  const isCorrect = idx === 1
  userScore.step4 = isCorrect ? 25 : 0
  showFeedback(
    isCorrect ? "⚖️ 심화 분석: 트레이드오프" : "🤔 심화 분석: 다시 생각해보세요",
    isCorrect ? "정답입니다. 너무 엄격한 필터링은 유용한 데이터까지 버릴 수 있습니다(False Positive)." : "아닙니다. 필터링을 너무 강하게 하면 오히려 데이터 부족 현상이 발생할 수 있습니다.",
    "활용 사례: 스팸 메일 필터가 너무 강력하면, 중요한 업무 메일까지 스팸통으로 들어가는 것과 같습니다. 엔지니어는 항상 '정확도'와 '재현율' 사이의 균형을 맞춰야 합니다.",
    isCorrect
  )
}

// Feedback Control
const showFeedback = (title, desc, details, isSuccess) => {
  feedbackModal.title = title
  feedbackModal.desc = desc
  feedbackModal.details = details
  feedbackModal.isSuccess = isSuccess
  feedbackModal.visible = true
}

const nextStep = () => {
  feedbackModal.visible = false
  if (currentStep.value < 5) currentStep.value++
}

const reloadApp = () => location.reload()

// Final Review Computed
const finalReviewText = computed(() => {
  let review = `엔지니어님은 데이터가 AI 모델에 미치는 영향을 정확히 이해하고 있습니다. `
  review += userScore.step2 >= 20 ? "수도코드를 통한 논리 구조화 능력이 뛰어나며, " : "수도코드 작성에 조금 더 연습이 필요해 보이지만, "
  review += userScore.step3 >= 20 ? "파이썬 코드로의 변환 능력도 훌륭합니다." : "코드 구현 디테일을 조금만 더 다듬으면 훌륭한 엔지니어가 될 것입니다."
  review += "<br/><br/>이제 오염된 데이터가 제거되었으니, 다음 스테이지(RAG 시스템 구축)로 나아갈 준비가 되었습니다."
  return review
})
</script>

<style scoped>
:root {
  --bg-dark: #0a0e17;
  --neon-cyan: #00f3ff;
  --neon-pink: #ff00ff;
}

.selection-cyan::selection {
  background-color: var(--neon-cyan);
  color: black;
}

/* Animation Classes */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

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

@keyframes scanline {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}

.shadow-neon {
  filter: drop-shadow(0 0 15px rgba(0, 243, 255, 0.4));
}

</style>