<template>
  <!-- [수정일: 2026-01-31] 전역 모달(z-index 1000)보다 위에 오도록 z-index를 z-[2000]으로 상향 조정 -->
  <div v-if="isOpen" class="fixed inset-0 z-[2000] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in" @click.self="$emit('close')">
    <div class="bg-[#0a0e17] w-full max-w-[1700px] h-[96vh] rounded-3xl border border-white/10 shadow-2xl overflow-hidden flex flex-col relative animate-scale-in">
      
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
      <main class="flex-1 p-8 lg:p-12 max-w-full mx-auto w-full relative flex flex-col min-h-0 overflow-y-auto custom-scrollbar z-10">
        <!-- Progress Bar -->
        <div v-if="currentStep <= 4" class="max-w-4xl mx-auto w-full mb-16 px-6 shrink-0">
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

        <!-- STAGE 1: Quiz (main 브랜치의 거대한 텍스트 스타일 복구) -->
        <div v-if="currentStep === 1" class="grid grid-cols-1 lg:grid-cols-[1fr_1.35fr] gap-10 lg:gap-14 animate-fade-in-up items-start max-w-[1600px] mx-auto w-full flex-1 min-h-0 pb-10">
          <!-- Info Card -->
          <div class="bg-[#0d1117] border border-white/10 p-12 lg:p-16 rounded-3xl flex flex-col relative overflow-hidden shadow-2xl">
            <div class="flex flex-col gap-8 mb-12">
              <div class="flex items-center gap-6">
                <div class="p-4 bg-cyan-500/5 rounded-2xl border border-cyan-500/10">
                  <Cpu class="text-cyan-400/50 w-10 h-10" />
                </div>
                <div class="space-y-1">
                  <span class="text-cyan-500/30 font-mono text-[9px] tracking-[0.3em] uppercase block">Authorized_Protocol_v4.0</span>
                  <h2 class="text-5xl lg:text-7xl font-black text-white italic tracking-tighter uppercase leading-none">
                    Stage 1:<br/>
                    <span class="text-cyan-400">오염된 기억</span>
                  </h2>
                </div>
              </div>
            </div>

            <div class="space-y-12">
              <p class="text-lg lg:text-[22px] text-[#8b949e] leading-relaxed font-bold">
                Lion의 메모리 뱅크가 손상되었습니다. 복구 프로세스를 시작하기 전에 가장 중요한 원칙을 확인해야 합니다.
              </p>
              
              <div class="bg-[#090c10] p-10 lg:p-12 border border-cyan-500/40 rounded-3xl relative shadow-inner">
                <h3 class="text-[#00f3ff] font-black text-2xl mb-6 flex items-center gap-3">
                  <div class="w-2.5 h-2.5 bg-cyan-400 rounded-full shadow-[0_0_10px_#00f3ff]"></div>
                  핵심 개념: GIGO (Garbage In, Garbage Out)
                </h3>
                <p class="text-white text-[22px] font-black leading-relaxed mb-6">
                  "쓰레기가 들어가면 쓰레기가 나온다."
                </p>
                <p class="text-[#8b949e] text-[18px] leading-relaxed font-bold italic border-l-2 border-cyan-500/30 pl-6">
                  모델이 아무리 뛰어나도, 학습 데이터의 품질이 낮으면 결과물도 엉망이 됩니다.
                </p>
              </div>
            </div>
          </div>

          <!-- Quiz Card -->
          <div class="bg-[#0d1117] border border-white/10 p-12 lg:p-16 rounded-3xl flex flex-col shadow-2xl">
            <div class="flex flex-col gap-8 mb-12">
              <div class="flex items-baseline gap-6 h-10">
                <span class="text-cyan-500 font-black text-6xl italic leading-none">Q.</span>
              </div>
              <h3 class="text-3xl lg:text-4xl font-black text-white leading-[1.2]">다음 중 데이터 전처리를 수행해야 하는 가장 타당한 이유는?</h3>
            </div>

            <div class="grid grid-cols-1 gap-6 flex-1">
              <button v-for="(opt, idx) in currentQuest.quizOptions" :key="idx"
                @click="handleStep1Submit(idx)"
                class="w-full text-left p-8 lg:p-10 bg-[#161b22] border border-white/10 rounded-2xl hover:bg-[#1c2128] hover:border-cyan-500/60 transition-all group flex items-center shadow-md hover:shadow-cyan-500/10 relative overflow-hidden">
                <div class="absolute inset-y-0 left-0 w-2.5 transition-all bg-transparent group-hover:bg-cyan-500"></div>
                <span class="flex-1 font-bold text-[#c9d1d9] text-xl lg:text-[24px] group-hover:text-white transition-colors pl-6 lg:pl-10">
                  {{ idx + 1 }}. {{ opt.text }}
                </span>
              </button>
            </div>
          </div>
        </div>

        <!-- STAGE 2: Pseudocode (main 브랜치의 문제 정의 HUD 복구) -->
        <div v-if="currentStep === 2" class="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-14 animate-fade-in-up items-start max-w-[1600px] mx-auto w-full flex-1 min-h-0 pb-10">
          <div class="flex flex-col gap-10 min-h-0 w-full">
            <!-- Problem Definition -->
            <div class="bg-black/40 border border-cyan-500/20 p-8 lg:p-12 hud-box-clip h-[350px] relative overflow-hidden group flex flex-col">
              <h3 class="text-3xl font-black text-white italic mb-8 flex items-center gap-4 shrink-0">
                <CodeIcon class="w-8 h-8 text-cyan-400" /> MISSION_OBJECTIVE
              </h3>
              <!-- Scrollable Content -->
              <div class="flex-1 overflow-y-auto custom-scrollbar pr-4 space-y-8">
                <p class="text-gray-300 leading-relaxed font-bold text-xl lg:text-2xl">
                  리스트에 담긴 뉴스 제목들 중 <span class="bg-cyan-500/20 text-cyan-300 px-2 rounded">"광고"</span>, <span class="bg-cyan-500/20 text-cyan-300 px-2 rounded">"클릭"</span>이 포함된 제목과, <span class="bg-pink-500/20 text-pink-300 px-2 rounded">길이가 5자 미만</span>인 데이터를 제거하는 필터링 로직을 설계하십시오.
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
                  class="flex flex-col" :class="msg.sender === 'User' ? 'items-end' : 'items-start'">
                  <span class="text-[8px] text-gray-500 font-black mb-2 uppercase tracking-tighter">{{ msg.sender }}_ID</span>
                  <div class="max-w-[90%] p-4 text-sm leading-relaxed hud-button-clip"
                       :class="msg.sender === 'Lion' ? 'bg-cyan-500/10 text-cyan-100 border border-cyan-500/20' : 'bg-white/5 text-white border border-white/10'">
                    {{ msg.text }}
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
              <vue-monaco-editor
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

            <button @click="submitStep2" class="mt-12 group relative transition-all active:scale-[0.98]">
              <div class="absolute -inset-1 bg-gradient-to-r from-cyan-600/50 to-blue-700/50 rounded-lg blur opacity-50 group-hover:opacity-100 transition duration-500"></div>
              <div class="relative w-full py-6 bg-black border border-cyan-500/50 text-white font-black text-xl tracking-[0.3em] uppercase hover:bg-cyan-500/10 transition-all hud-button-clip flex items-center justify-center gap-4">
                <Terminal class="w-6 h-6 text-cyan-400" />
                SUBMIT_LOGIC_NODE
              </div>
            </button>
          </div>
        </div>

        <!-- STAGE 3: Python Blocks (main 브랜치의 시네마틱 스타일 복구) -->
        <div v-if="currentStep === 3" class="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-14 animate-fade-in-up items-start max-w-[1600px] mx-auto w-full flex-1 min-h-0 pb-10">
          <!-- Left: Blocks -->
          <div class="bg-[#0f1219]/60 border border-white/5 p-10 hud-box-clip flex flex-col relative group min-h-0">
            <div class="absolute inset-0 bg-gradient-to-b from-cyan-500/[0.02] to-transparent pointer-events-none"></div>
            
            <div class="mb-10 relative shrink-0">
              <div class="flex items-center gap-4 mb-4">
                <div class="w-1.5 h-8 bg-cyan-500 shadow-[0_0_10px_#00f3ff]"></div>
                <h3 class="text-3xl lg:text-4xl font-black text-white italic tracking-tighter uppercase">코드 블록 보관함</h3>
              </div>
              <p class="text-gray-400 text-lg lg:text-xl leading-relaxed font-bold">
                아래 블록을 클릭하여 선택한 후, 오른쪽 코드의 빈칸을 클릭해 채워넣으세요.
              </p>
            </div>
            
            <div class="grid grid-cols-2 gap-4 flex-1 overflow-y-auto custom-scrollbar pr-4 min-h-0 content-start">
              <button v-for="block in blocks" :key="block.id"
                @click="selectBlock(block)"
                class="group relative h-28 transition-all active:scale-[0.98]">
                <div class="absolute inset-0 bg-black/40 border transition-all duration-300 hud-box-clip"
                     :class="selectedBlock && selectedBlock.id === block.id ? 'border-cyan-500 shadow-[0_0_20px_rgba(0,243,255,0.2)] bg-cyan-500/10' : 'border-white/10 group-hover:border-cyan-500/30'">
                </div>
                <div class="relative h-full flex items-center justify-center px-4">
                  <span class="text-base font-black tracking-widest uppercase transition-all"
                        :class="selectedBlock && selectedBlock.id === block.id ? 'text-cyan-400' : 'text-gray-400 group-hover:text-cyan-300'">
                    {{ block.text }}
                  </span>
                </div>
              </button>
            </div>

            <div class="mt-8 p-8 bg-white/[0.02] border-l-4 border-pink-500 hud-box-clip relative overflow-hidden shrink-0">
              <div class="absolute top-0 right-0 w-16 h-16 bg-pink-500/5 rotate-45 translate-x-8 -translate-y-8"></div>
              <p class="text-base lg:text-lg text-gray-300 leading-relaxed font-bold italic">
                <span class="text-pink-500 not-italic font-black mr-2">Tip:</span> continue는 건너뛰기, break는 멈추기입니다. 우리는 끝까지 다 검사해야 해요.
              </p>
            </div>
          </div>

          <!-- Right: Executor -->
          <div class="bg-[#1a1a1a] border border-white/5 hud-box-clip flex flex-col relative overflow-hidden group shadow-2xl min-h-[600px]">
            <div class="p-6 px-10 flex justify-between items-center shrink-0 border-b border-white/5 bg-black/20">
              <div class="flex items-center gap-3">
                <div class="w-2 h-2 rounded-full bg-pink-500 animate-pulse"></div>
                <span class="text-[12px] font-mono text-cyan-400/60 uppercase tracking-widest font-black">Python_Executor_v3.2</span>
              </div>
              <span class="text-[11px] font-mono text-gray-500 uppercase tracking-widest italic font-bold">data_cleaning.py</span>
            </div>

            <div class="flex-1 p-8 lg:p-12 relative overflow-y-auto custom-scrollbar min-h-0 font-mono" ref="simulationContainer">
              <!-- Code Structure -->
              <div v-if="!simulationOutput" class="text-[15px] lg:text-[17px] leading-[2.4] font-medium text-gray-300">
                <pre>def clean_news_data(news_list):
    cleaned_data = []

    for news in news_list:
        <span class="text-gray-500 italic"># 1. 길이 체크 및 키워드 필터링</span>
        if len(news) < 5 or "광고" in news:</pre>
                
                <!-- Blank A -->
                <div class="flex items-center gap-4 pl-8 lg:pl-12 h-20">
                  <div @click="fillBlank('blankA')"
                       class="min-w-[280px] border-b-2 transition-all cursor-pointer flex items-center justify-center relative group/blank"
                       :class="pythonBlanks.blankA ? 'border-cyan-500 text-cyan-400' : 'border-gray-700 hover:border-gray-500 bg-white/[0.02]'">
                    <span class="text-3xl font-black tracking-widest">{{ pythonBlanks.blankA ? pythonBlanks.blankA.text : "__________" }}</span>
                    <div class="ml-6 text-xl text-yellow-500/80 font-black tracking-tighter">__(A)__</div>
                  </div>
                </div>

                <pre class="mt-4">
        <span class="text-gray-500 italic"># 2. 유효한 데이터 저장</span></pre>

                <!-- Blank B -->
                <div class="flex items-center pl-8 lg:pl-12 h-20">
                  <span class="text-2xl">cleaned_data.</span>
                  <div @click="fillBlank('blankB')"
                       class="min-w-[280px] border-b-2 transition-all cursor-pointer flex items-center justify-center relative group/blank mx-4"
                       :class="pythonBlanks.blankB ? 'border-cyan-500 text-cyan-400' : 'border-gray-700 hover:border-gray-500 bg-white/[0.02]'">
                    <span class="text-3xl font-black tracking-widest">{{ pythonBlanks.blankB ? pythonBlanks.blankB.text : "__________" }}</span>
                  </div>
                  <div class="text-xl text-yellow-500/80 font-black tracking-tighter ml-6">__(B)__</div>
                </div>

                <pre class="mt-6">    return cleaned_data</pre>
              </div>
              
              <!-- Simulation Output Display -->
              <div v-else class="font-mono text-sm leading-relaxed" v-html="simulationOutput"></div>
              
              <div class="absolute bottom-8 right-8 z-20">
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
        <div v-if="currentStep === 4" class="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-14 animate-fade-in-up items-start max-w-[1600px] mx-auto w-full flex-1 min-h-0 pb-10">
          <!-- Info -->
          <div class="flex flex-col min-h-0">
            <div class="bg-black/40 border border-pink-500/20 p-10 relative group overflow-hidden flex-1 hud-box-clip min-h-0">
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
              <h3 class="text-2xl lg:text-3xl font-black text-white mb-12 leading-tight uppercase tracking-tight italic border-l-4 border-cyan-500 pl-6">Q. 필터링의 부작용을 최소화하고 정보의 가치를 보존하기 위한 최적의 엔지니어링 접근은?</h3>
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

              <!-- Lion Review Section -->
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
                      Lion_Integrated_Synthetic_Review
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
                <button @click="$emit('close')"
                  class="group px-14 py-6 bg-cyan-600 text-black font-black uppercase tracking-[0.2em] text-xs hud-button-clip hover:bg-cyan-400 hover:shadow-[0_0_30px_#00f3ff] transition-all active:scale-95 flex items-center gap-4">
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
                <component :is="feedbackModal.isSuccess ? CheckCircle : AlertTriangle" class="w-12 h-12" />
              </div>
              <h3 class="text-2xl lg:text-3xl font-black text-white italic tracking-tighter uppercase">{{ feedbackModal.title }}</h3>
            </div>

            <p class="text-lg lg:text-xl text-gray-200 mb-10 leading-relaxed font-bold italic border-l-4 px-6" :class="feedbackModal.isSuccess ? 'border-green-500' : 'border-pink-500'">{{ feedbackModal.desc }}</p>
            
            <div class="bg-white/[0.03] p-8 border border-white/5 text-lg font-medium text-gray-400 mb-12 leading-relaxed" v-html="feedbackModal.details"></div>
            
            <div class="flex justify-end">
              <button @click="nextStep" class="group relative h-16 transition-all active:scale-[0.98]">
                <div class="absolute -inset-1 bg-cyan-500/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition duration-300"></div>
                <div class="relative px-12 h-full bg-cyan-600 text-black font-black uppercase tracking-[0.2em] flex items-center gap-4 hud-button-clip hover:bg-cyan-400 hover:shadow-[0_0_20px_#00f3ff] transition-all">
                  {{ currentStep === 4 ? "GENERATE_REPORT" : "INITIALIZE_NEXT_PROTOCOL" }} 
                  <ChevronRight class="w-6 h-6" />
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- Duck Component 복구 -->
        <div v-if="currentStep !== 5" class="absolute bottom-10 right-10 z-20 pointer-events-auto">
          <Duck class-name="shadow-neon hover:scale-110 transition-transform cursor-pointer" />
        </div>
        <div v-else class="fixed bottom-10 right-10 scale-125 z-50">
          <Duck class-name="shadow-neon cursor-help animate-in zoom-in slide-in-from-right-20 delay-1500" />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
/**
 [수정일: 2026-01-31]
 내용: main 브랜치 UI/UX 완벽 복구 및 안정화 코드 병합
 1. UI 대형화: max-w-[1700px], 폰트 크기(text-7xl 등) main 사양으로 복구
 2. 런타임 안정성: watch가 실행되기 전에 pseudoInput(ref) 선언 위치 상향 조정 (Watcher callback error 해결)
 3. z-index 최적화: 전역 모달 대응을 위해 z-[2000] 적용
 4. 동적 데이터 연동: aiQuests(stages.js) 데이터를 사용하여 하드코딩 제거
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
import { useGameStore } from '@/stores/game'
import { useRouter } from 'vue-router'
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'
import Duck from './components/Duck.vue'
import { aiQuests } from './support/unit1/logic-mirror/data/stages.js'

const props = defineProps({
  // [수정일: 2026-01-31] 라우터를 통해 페이지로 접근 시 화면이 즉시 보이도록 기본값을 true로 설정
  isOpen: { type: Boolean, default: true }
})

const emit = defineEmits(['close'])
const gameStore = useGameStore()
const router = useRouter()

// --- Logic & Data Integration ---
const currentQuestIdx = computed(() => gameStore.selectedQuestIndex || 0)
const currentQuest = computed(() => aiQuests[currentQuestIdx.value] || aiQuests[0])

// --- State (Watcher 관련 변수를 선언부 최상단으로 배치) ---
const currentStep = ref(1)
const userScore = reactive({ step1: 0, step2: 0, step3: 0, step4: 0 })
const pseudoInput = ref('') // [수정일: 2026-01-31] Watcher 참조 순서 오류 수정을 위해 상향 배치

const chatMessages = ref([
  { sender: 'Lion', text: '엔지니어님, 깨어나셨군요. 오염된 데이터를 정화해야 제 기억이 돌아옵니다. 오른쪽 패널에 한글로 로직을 설계해주세요.' }
])
const chatContainer = ref(null)

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
  "삼성전자 주가 급등",
  "광고) 지금 바로 클릭하세요",
  "날씨",
  "AI 모델의 미래 전망",
  "초특가 광고 상품 안내"
]

const step4Options = [
  "'광고' 단어가 포함된 모든 문서를 무조건 삭제한다.",
  "단순 키워드 매칭 대신, 문맥을 이해하는 AI 모델을 사용하여 필터링한다.",
  "데이터 전처리를 아예 하지 않는다.",
  "사람이 모든 데이터를 직접 읽고 지운다."
]

const feedbackModal = reactive({
  visible: false,
  title: '',
  desc: '',
  details: '',
  isSuccess: true
})

// Monaco Editor Options (main 브랜치 사양)
const editorOptions = {
  minimap: { enabled: false },
  fontSize: 20,
  lineHeight: 32,
  theme: 'vs-dark',
  lineNumbers: 'on',
  scrollbar: {
    vertical: 'visible',
    horizontal: 'visible',
    verticalSliderSize: 6,
    horizontalSliderSize: 6
  },
  wordWrap: 'on',
  padding: { top: 20, bottom: 20 },
  fontFamily: "'Nanum Gothic Coding', monospace",
  automaticLayout: true,
  suggestOnTriggerCharacters: true,
  folding: true,
  roundedSelection: true
}

// --- Watchers ---
watch(currentQuest, (newQuest) => {
  if (newQuest && newQuest.cards) {
    currentStep.value = 1
    pythonBlanks.blankA = null
    pythonBlanks.blankB = null
    simulationOutput.value = ''
    if (pseudoInput.value !== undefined) {
      pseudoInput.value = ''
    }
  }
}, { immediate: true })

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

// --- Methods ---
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const handleStep1Submit = (idx) => {
  const isCorrect = currentQuest.value.quizOptions[idx].correct
  userScore.step1 = isCorrect ? 25 : 0
  showFeedback(
    isCorrect ? "✅ 정답: GIGO 원칙의 이해" : "⚠️ 오답: 다시 생각해보세요",
    isCorrect ? "훌륭합니다. '쓰레기가 들어가면 쓰레기가 나온다(Garbage In, Garbage Out)'는 AI 엔지니어링의 제1원칙입니다. 아무리 좋은 모델도 데이터가 더러우면 소용없습니다." : "데이터의 양보다는 '질'이 우선입니다. 노이즈가 섞인 데이터는 모델의 판단력을 흐리게 만듭니다.",
    "활용 사례: 실제 현업에서도 전체 프로젝트 기간의 80%를 데이터 전처리에 사용합니다. 금융 사기 탐지 모델에서 정상 거래를 사기로 오해하지 않게 하려면 노이즈 제거가 필수적입니다.",
    isCorrect
  )
}

const submitStep2 = () => {
  const code = pseudoInput.value.trim()
  const rules = {
    loop: { pattern: /(반복|하나씩|꺼내|모든|리스트|for|each)/, desc: "데이터를 하나씩 확인하는 '반복' 구조" },
    condition: { pattern: /(만약|일 때|경우|라면|if|조건)/, desc: "특정 데이터를 선별하는 '조건분기'" },
    keywordCheck: { pattern: /(광고|클릭|길이|5자|미만)/, desc: "문제에서 요구한 '필터링 기준' 언급" },
    action: { pattern: /(제거|삭제|버린|제외|건너뛰|저장|추가|append|continue)/, desc: "조건에 따른 '처리 행동'" }
  }

  let score = 0
  let feedbackItems = []
  let passedCount = 0

  Object.keys(rules).forEach(key => {
    const rule = rules[key]
    if (rule.pattern.test(code)) {
      score += 6.25
      passedCount++
      feedbackItems.push(`<span class="text-green-400">✔ ${rule.desc}가 포함되었습니다.</span>`)
    } else {
      feedbackItems.push(`<span class="text-gray-500">✘ ${rule.desc}가 누락되었거나 불분명합니다.</span>`)
    }
  })

  userScore.step2 = Math.floor(score)
  const listHtml = `
    <div class="space-y-4">
      <p class="font-bold border-b border-white/10 pb-2 text-xl">알고리즘 구성 요소 체크:</p>
      <ul class="text-lg space-y-2">${feedbackItems.map(f => `<li>${f}</li>`).join('')}</ul>
      <div class="mt-6 pt-4 border-t border-white/10 text-lg">
        <p class="mt-2 text-pink-400 font-bold italic">Lion의 심사평: ${passedCount >= 4 ? "완벽한 설계입니다. 이제 이 논리를 파이썬 코드로 옮길 준비가 되셨군요!" : "설계가 조금 추상적입니다. '무엇을(대상)', '어떻게(방법)' 처리할지 명확히 적어보세요."}</p>
      </div>
    </div>
  `
  
  showFeedback(
    score >= 20 ? "💡 논리 설계 평가: 우수함" : "🔧 논리 설계 평가: 보완 필요",
    "Lion의 알고리즘 엔진이 엔지니어님의 의사코드를 분석했습니다.",
    listHtml,
    score >= 15
  )
}

const selectBlock = (block) => { selectedBlock.value = block }
const fillBlank = (blankId) => {
  if (!selectedBlock.value) return
  pythonBlanks[blankId] = selectedBlock.value
  selectedBlock.value = null
}

const runSimulation = () => {
  const bA = pythonBlanks.blankA?.text 
  const bB = pythonBlanks.blankB?.text 
  
  if (!bA || !bB) {
    simulationOutput.value = '<span class="text-pink-500">Error: 빈칸을 모두 채워야 실행할 수 있습니다.</span>'
    return
  }

  isSimulating.value = true
  simulationOutput.value = '<span class="text-cyan-500">Initializing cleaning_protocol.v3...</span><br>'
  
  let cleaned_data = []
  let log = '<span class="text-cyan-400 font-black tracking-widest uppercase text-[10px] italic">Checking system_integrity_protocol...</span><br>'

  for (let news of sampleData) {
    log += `<span class="text-gray-500 italic mt-2">Checking_Node: "${news}"</span><br>`
    if (news.length < 5 || news.includes("광고")) {
      if (bA === 'continue') {
        log += `<span class="text-yellow-500 font-mono">&nbsp;&nbsp;[PROT_SKIP]: 필터링 조건 일치.</span><br>`
        continue 
      } else if (bA === 'break') {
        log += `<span class="text-red-500 font-mono">&nbsp;&nbsp;[PROT_HALT]: 반복문 강제 종료됨.</span><br>`
        break
      }
    }
    if (bB === 'append(text)') {
      cleaned_data.push(news)
      log += `<span class="text-green-500 font-mono">&nbsp;&nbsp;[DATA_SAVE]: 데이터가 cleaned_data에 커밋됨.</span><br>`
    }
  }

  log += `<br><strong class="text-white bg-cyan-700/30 px-2 py-1 italic tracking-widest uppercase text-[10px]">SYNC_COMPLETED: [${cleaned_data.join(', ')}]</strong>`
  
  setTimeout(() => {
    simulationOutput.value = log
    isSimulating.value = false
    nextTick(() => {
      if (simulationContainer.value) simulationContainer.value.scrollTop = simulationContainer.value.scrollHeight
    })
    submitStep3() 
  }, 800)
}

const submitStep3 = () => {
  const val = currentQuest.value.codeValidation
  // 퀘스트 인덱스 0번(기본)일 경우 continue와 append(text)가 정답
  const bA = pythonBlanks.blankA?.text === (currentQuestIdx.value === 0 ? 'continue' : val.fee1)
  const bB = pythonBlanks.blankB?.text === (currentQuestIdx.value === 0 ? 'append(text)' : val.fee2)
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

const finalReviewText = computed(() => {
  let review = `엔지니어님은 데이터가 AI 모델에 미치는 영향을 정확히 이해하고 있습니다. `
  review += userScore.step2 >= 20 ? "수도코드를 통한 논리 구조화 능력이 뛰어나며, " : "수도코드 작성에 조금 더 연습이 필요해 보이지만, "
  review += userScore.step3 >= 20 ? "파이썬 코드로의 변환 능력도 훌륭합니다." : "코드 구현 디테일을 조금만 더 다듬으면 훌륭한 엔지니어가 될 것입니다."
  review += "<br/><br/>이제 오염된 데이터가 제거되었으니, 다음 스테이지(RAG 시스템 구축)로 나아갈 준비가 되었습니다."
  return review
})
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