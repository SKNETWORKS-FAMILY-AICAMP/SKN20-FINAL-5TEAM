<template>
  <!-- [?섏젙?? 2026-01-30] standalone HTML?먯꽌 Vue SFC 紐⑤떖 援ъ“濡?蹂듦뎄 諛?媛?낆꽦 理쒖쟻??-->
  <div class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in" @click.self="$emit('close')">
    <div class="bg-[#0a0e17] w-full max-w-[1700px] h-[96vh] rounded-3xl border border-white/10 shadow-2xl overflow-hidden flex flex-col relative animate-scale-in">
      
      <!-- Glow Decor -->
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
          <div class="text-[9px] text-gray-500 font-bold uppercase tracking-tighter">LV_04_SECURITY_BYPASS</div>
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

        <!-- STAGE 1: Quiz -->
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
                    <span class="text-cyan-400">?ㅼ뿼??湲곗뼲</span>
                  </h2>
                </div>
              </div>
            </div>

            <div class="space-y-12">
              <p class="text-lg lg:text-[22px] text-[#8b949e] leading-relaxed font-bold">
                Lion??硫붾え由?諭낇겕媛 ?먯긽?섏뿀?듬땲?? 蹂듦뎄 ?꾨줈?몄뒪瑜??쒖옉?섍린 ?꾩뿉 媛??以묒슂???먯튃???뺤씤?댁빞 ?⑸땲??
              </p>
              
              <div class="bg-[#090c10] p-10 lg:p-12 border border-cyan-500/40 rounded-3xl relative shadow-inner">
                <h3 class="text-[#00f3ff] font-black text-2xl mb-6 flex items-center gap-3">
                  <div class="w-2.5 h-2.5 bg-cyan-400 rounded-full shadow-[0_0_10px_#00f3ff]"></div>
                  ?듭떖 媛쒕뀗: GIGO (Garbage In, Garbage Out)
                </h3>
                <p class="text-white text-[22px] font-black leading-relaxed mb-6">
                  "?곕젅湲곌? ?ㅼ뼱媛硫??곕젅湲곌? ?섏삩??"
                </p>
                <p class="text-[#8b949e] text-[18px] leading-relaxed font-bold italic border-l-2 border-cyan-500/30 pl-6">
                  紐⑤뜽???꾨Т由??곗뼱?섎룄, ?숈뒿 ?곗씠?곗쓽 ?덉쭏????쑝硫?寃곌낵臾쇰룄 ?됰쭩???⑸땲??
                </p>
              </div>
            </div>
          </div>

          <!-- Quiz Card -->
          <div class="bg-[#0d1117] border border-white/10 p-12 lg:p-16 rounded-3xl flex flex-col shadow-2xl">
            <div class="flex flex-col gap-8 mb-12">
              <div class="flex items-baseline gap-6 h-10"> <!-- Height matched with Left Cpu Icon Section -->
                <span class="text-cyan-500 font-black text-6xl italic leading-none">Q.</span>
              </div>
              <h3 class="text-3xl lg:text-4xl font-black text-white leading-[1.2]">?ㅼ쓬 以??곗씠???꾩쿂由щ? ?섑뻾?댁빞 ?섎뒗 媛????뱁븳 ?댁쑀??</h3>
            </div>

            <div class="grid grid-cols-1 gap-6 flex-1">
              <button v-for="(opt, idx) in step1Options" :key="idx"
                @click="handleStep1Submit(idx)"
                class="w-full text-left p-8 lg:p-10 bg-[#161b22] border border-white/10 rounded-2xl hover:bg-[#1c2128] hover:border-cyan-500/60 transition-all group flex items-center shadow-md hover:shadow-cyan-500/10 relative overflow-hidden">
                <div class="absolute inset-y-0 left-0 w-2.5 transition-all bg-transparent group-hover:bg-cyan-500"></div>
                <span class="flex-1 font-bold text-[#c9d1d9] text-xl lg:text-[24px] group-hover:text-white transition-colors pl-6 lg:pl-10">
                  {{ idx + 1 }}. {{ opt }}
                </span>
              </button>
            </div>
          </div>
        </div>

        <!-- STAGE 2: Pseudocode -->
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
                  由ъ뒪?몄뿉 ?닿릿 ?댁뒪 ?쒕ぉ??以?<span class="bg-cyan-500/20 text-cyan-300 px-2 rounded">"愿묎퀬"</span>, <span class="bg-cyan-500/20 text-cyan-300 px-2 rounded">"?대┃"</span>???ы븿???쒕ぉ怨? <span class="bg-pink-500/20 text-pink-300 px-2 rounded">湲몄씠媛 5??誘몃쭔</span>???곗씠?곕? ?쒓굅?섎뒗 ?꾪꽣留?濡쒖쭅???ㅺ퀎?섏떗?쒖삤.
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
              <!-- Monaco Editor Replacment -->
              <vue-monaco-editor
                v-model:value="pseudoCode"
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

        <!-- STAGE 3: Python Blocks -->
        <div v-if="currentStep === 3" class="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-14 animate-fade-in-up items-start max-w-[1600px] mx-auto w-full flex-1 min-h-0 pb-10">
          <!-- Left: Blocks -->
          <div class="bg-[#0f1219]/60 border border-white/5 p-10 hud-box-clip flex flex-col relative group min-h-0">
            <div class="absolute inset-0 bg-gradient-to-b from-cyan-500/[0.02] to-transparent pointer-events-none"></div>
            
            <div class="mb-10 relative shrink-0">
              <div class="flex items-center gap-4 mb-4">
                <div class="w-1.5 h-8 bg-cyan-500 shadow-[0_0_10px_#00f3ff]"></div>
                <h3 class="text-3xl lg:text-4xl font-black text-white italic tracking-tighter uppercase">肄붾뱶 釉붾줉 蹂닿???/h3>
              </div>
              <p class="text-gray-400 text-lg lg:text-xl leading-relaxed font-bold">
                ?꾨옒 釉붾줉???대┃?섏뿬 ?좏깮???? ?ㅻⅨ履?肄붾뱶??鍮덉뭏???대┃??梨꾩썙?ｌ쑝?몄슂.
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
                <span class="text-pink-500 not-italic font-black mr-2">Tip:</span> continue??嫄대꼫?곌린, break??硫덉텛湲곗엯?덈떎. ?곕━???앷퉴吏 ??寃?ы빐???댁슂.
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
        <span class="text-gray-500 italic"># 1. 湲몄씠 泥댄겕 諛??ㅼ썙???꾪꽣留?/span>
        if len(news) < 5 or "愿묎퀬" in news:</pre>
                
                <!-- Blank A -->
                <div class="flex items-center gap-4 pl-8 lg:pl-12 h-14">
                  <div @click="fillBlank('blankA')"
                       class="min-w-[200px] border-b-2 transition-all cursor-pointer flex items-center justify-center relative group/blank"
                       :class="pythonBlanks.blankA ? 'border-cyan-500 text-cyan-400' : 'border-gray-700 hover:border-gray-500 bg-white/[0.02]'">
                    <span class="text-sm font-bold tracking-widest">{{ pythonBlanks.blankA ? pythonBlanks.blankA.text : "__________" }}</span>
                    <div class="ml-4 text-[12px] text-gray-600 font-bold tracking-tighter">__(A)__</div>
                  </div>
                </div>

                <pre class="mt-4">
        <span class="text-gray-500 italic"># 2. ?좏슚???곗씠?????/span></pre>

                <!-- Blank B -->
                <div class="flex items-center pl-8 lg:pl-12 h-14">
                  <span>cleaned_data.</span>
                  <div @click="fillBlank('blankB')"
                       class="min-w-[200px] border-b-2 transition-all cursor-pointer flex items-center justify-center relative group/blank mx-2"
                       :class="pythonBlanks.blankB ? 'border-cyan-500 text-cyan-400' : 'border-gray-700 hover:border-gray-500 bg-white/[0.02]'">
                    <span class="text-sm font-bold tracking-widest">{{ pythonBlanks.blankB ? pythonBlanks.blankB.text : "__________" }}</span>
                  </div>
                  <div class="text-[12px] text-gray-600 font-bold tracking-tighter ml-4">__(B)__</div>
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
                    {{ isSimulating ? '?ㅽ뻾 以?..' : '肄붾뱶 ?ㅽ뻾 諛?寃利? }}
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- STAGE 4: Deep Dive -->
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
                <p class="text-2xl text-white/90">?꾩쿂由ш? 吏?섏튂寃??꾨꼍?섎㈃, ?좏슚???곗씠?곌퉴吏 '?ㅼ뿼臾?濡?遺꾨쪟???꾪뿕???덉뒿?덈떎.</p>
                
                <div class="relative pt-10">
                  <div class="absolute top-0 left-0 w-16 h-1.5 bg-pink-500 shadow-[0_0_10px_#ec4899]"></div>
                  <h3 class="text-pink-400 font-black text-xs uppercase tracking-[0.4em] mb-6">ENGINEERING ISSUE: TRADE-OFF</h3>
                  <div class="bg-pink-500/5 p-10 border border-pink-500/20 relative overflow-hidden group hud-box-clip">
                    <p class="text-2xl text-white italic mb-6 font-black tracking-tight">"False Positives vs Information Loss"</p>
                    <p class="text-lg lg:text-xl text-gray-400 leading-relaxed italic">
                      "愿묎퀬"?쇰뒗 ?ㅼ썙?쒕? 湲곌퀎?곸쑝濡???젣?쒕떎硫? <span class="text-pink-300 font-bold border-b border-pink-500/30">"愿묎퀬 ?낃퀎???숉뼢"</span>怨?媛숈? 以묒슂???댁뒪留덉? ?뚯떎?????덉뒿?덈떎.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quiz -->
          <div class="flex flex-col gap-6">
            <div class="bg-black/40 border border-white/10 p-10 lg:p-14 hud-box-clip flex-1 flex flex-col">
              <h3 class="text-2xl lg:text-3xl font-black text-white mb-12 leading-tight uppercase tracking-tight italic border-l-4 border-cyan-500 pl-6">Q. ?꾪꽣留곸쓽 遺?묒슜??理쒖냼?뷀븯怨??뺣낫??媛移섎? 蹂댁〈?섍린 ?꾪븳 理쒖쟻???붿??덉뼱留??묎렐??</h3>
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

        <!-- STAGE 5: Final Report -->
        <div v-if="currentStep === 5" class="flex-1 flex flex-col items-center justify-center animate-fade-in-up py-10 px-6 max-w-[1400px] mx-auto w-full h-full min-h-0 self-center">
          <div class="bg-black/90 border-2 border-cyan-500/30 hud-box-clip w-full p-16 lg:p-24 text-center relative overflow-hidden backdrop-blur-3xl group shadow-[0_0_150px_rgba(0,0,0,1)]">
            <!-- Cinematic background -->
            <div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:60px_60px] opacity-30"></div>
            <div class="absolute inset-0 bg-gradient-to-t from-cyan-500/10 via-transparent to-transparent"></div>
            
            <div class="relative z-10 space-y-16">
              <!-- Header -->
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

              <!-- Lion Review -->
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

              <!-- Actions -->
              <div class="flex flex-col sm:flex-row gap-8 justify-center items-center">
                <button @click="reloadApp"
                  class="group px-14 py-6 bg-white/5 hover:bg-white/10 text-gray-500 hover:text-white font-black uppercase tracking-[0.2em] text-xs border border-white/5 hover:border-white/20 hud-button-clip transition-all active:scale-95 flex items-center gap-4">
                  <RotateCcw class="w-4 h-4 group-hover:rotate-180 transition-transform duration-700" />
                  Recalibrate_System
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Feedback Modal -->
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

        <!-- Duck Helper -->
        <div v-if="currentStep !== 5" class="absolute bottom-10 right-10 z-20 pointer-events-auto">
          <Duck class-name="shadow-neon hover:scale-110 transition-transform cursor-pointer" />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
/**
 * [?섏젙?? 2026-01-30]
 * ?댁슜: standalone HTML 援ъ“瑜?Vue SFC 紐⑤떖 援ъ“濡??ъ젙由?
 * - 紐⑤떖 諛곌꼍 諛??リ린 濡쒖쭅 蹂듦뎄
 * - Lucide ?꾩씠肄??쇱씠釉뚮윭由??곕룞
 * - 媛?낆꽦 諛??고듃 ?ш린 ?곹뼢 ?좎?
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
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'
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
  "?곗씠?곗쓽 ?⑸웾??以꾩뿬?????怨듦컙???꾨겮湲??꾪빐",
  "蹂듭옟??紐⑤뜽???ъ슜?섏뿬 ?숈뒿 ?띾룄瑜???텛湲??꾪빐",
  "?몄씠利덇? ?욎씤 ?곗씠?곌? 紐⑤뜽???깅뒫????섏떆?ㅻ뒗 寃껋쓣 留됯린 ?꾪빐",
  "紐⑤뱺 ?곗씠?곕? 湲띿젙?곸씤 ?댁슜?쇰줈 諛붽씀湲??꾪빐"
]

// Step 2 Data
const pseudoCode = ref('')
const chatMessages = ref([
  { sender: 'Lion', text: '?붿??덉뼱?? 源⑥뼱?섏뀲援곗슂. ?ㅼ뿼???곗씠?곕? ?뺥솕?댁빞 ??湲곗뼲???뚯븘?듬땲?? ?ㅻⅨ履??⑤꼸???쒓?濡?濡쒖쭅???ㅺ퀎?댁＜?몄슂.' }
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
    "?쇱꽦?꾩옄 二쇨? 湲됰벑",           // ?뺤긽
    "愿묎퀬) 吏湲?諛붾줈 ?대┃?섏꽭??,    // ?ㅼ썙???꾪꽣留????    "?좎뵪",                        // 湲몄씠 誘몃쭔 ???    "AI 紐⑤뜽??誘몃옒 ?꾨쭩",          // ?뺤긽
    "珥덊듅媛 愿묎퀬 ?곹뭹 ?덈궡"         // ?ㅼ썙???꾪꽣留????];

// Step 4 Options
const step4Options = [
  "'愿묎퀬' ?⑥뼱媛 ?ы븿??紐⑤뱺 臾몄꽌瑜?臾댁“嫄???젣?쒕떎.",
  "?⑥닚 ?ㅼ썙??留ㅼ묶 ??? 臾몃㎘???댄빐?섎뒗 AI 紐⑤뜽???ъ슜?섏뿬 ?꾪꽣留곹븳??",
  "?곗씠???꾩쿂由щ? ?꾩삁 ?섏? ?딅뒗??",
  "?щ엺??紐⑤뱺 ?곗씠?곕? 吏곸젒 ?쎄퀬 吏?대떎."
]

// Monaco Editor Options
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

// Feedback Modal
const feedbackModal = reactive({
  visible: false,
  title: '',
  desc: '',
  details: '',
  isSuccess: true
})

// --- Methods ---

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

watch(pseudoCode, (newVal) => {
  if (newVal.length > 10 && !chatMessages.value.some(m => m.text.includes('?쒖옉'))) {
    chatMessages.value.push({ sender: 'Lion', text: '醫뗭뒿?덈떎. 癒쇱? ?곗씠?곕? ?섎굹??爰쇰궡??"諛섎났" 援ъ“媛 ?꾩슂??蹂댁엯?덈떎.' })
    scrollToBottom()
  }
  if (newVal.includes('留뚯빟') && !chatMessages.value.some(m => m.text.includes('議곌굔'))) {
    chatMessages.value.push({ sender: 'Lion', text: '議곌굔臾몄쓣 ???묒꽦?섍퀬 怨꾩떆援곗슂. "?쒓굅"?섍굅??"????섎뒗 ?됰룞??紐낆떆?댁＜?몄슂.' })
    scrollToBottom()
  }
})

const handleStep1Submit = (idx) => {
  const isCorrect = idx === 2
  userScore.step1 = isCorrect ? 25 : 0
  showFeedback(
    isCorrect ? "???뺣떟: GIGO ?먯튃???댄빐" : "?좑툘 ?ㅻ떟: ?ㅼ떆 ?앷컖?대낫?몄슂",
    isCorrect ? "?뚮??⑸땲?? '?곕젅湲곌? ?ㅼ뼱媛硫??곕젅湲곌? ?섏삩??Garbage In, Garbage Out)'??AI ?붿??덉뼱留곸쓽 ???먯튃?낅땲?? ?꾨Т由?醫뗭? 紐⑤뜽???곗씠?곌? ?붾윭?곕㈃ ?뚯슜?놁뒿?덈떎." : "?곗씠?곗쓽 ?묐낫?ㅻ뒗 '吏????곗꽑?낅땲?? ?몄씠利덇? ?욎씤 ?곗씠?곕뒗 紐⑤뜽???먮떒?μ쓣 ?먮━寃?留뚮벊?덈떎.",
    "?쒖슜 ?щ?: ?ㅼ젣 ?꾩뾽?먯꽌???꾩껜 ?꾨줈?앺듃 湲곌컙??80%瑜??곗씠???꾩쿂由ъ뿉 ?ъ슜?⑸땲?? 湲덉쑖 ?ш린 ?먯? 紐⑤뜽?먯꽌 ?뺤긽 嫄곕옒瑜??ш린濡??ㅽ빐?섏? ?딄쾶 ?섎젮硫??몄씠利??쒓굅媛 ?꾩닔?곸엯?덈떎.",
    isCorrect
  )
}

const submitStep2 = () => {
  const code = pseudoCode.value.trim()
  const rules = {
    loop: { pattern: /(諛섎났|?섎굹??爰쇰궡|紐⑤뱺|由ъ뒪??for|each)/, desc: "?곗씠?곕? ?섎굹???뺤씤?섎뒗 '諛섎났' 援ъ“" },
    condition: { pattern: /(留뚯빟|????寃쎌슦|?쇰㈃|if|議곌굔)/, desc: "?뱀젙 ?곗씠?곕? ?좊퀎?섎뒗 '議곌굔遺꾧린'" },
    keywordCheck: { pattern: /(愿묎퀬|?대┃|湲몄씠|5??誘몃쭔)/, desc: "臾몄젣?먯꽌 ?붽뎄??'?꾪꽣留?湲곗?' ?멸툒" },
    action: { pattern: /(?쒓굅|??젣|踰꾨┛|?쒖쇅|嫄대꼫?????異붽?|append|continue)/, desc: "議곌굔???곕Ⅸ '泥섎━ ?됰룞'" }
  }

  let score = 0
  let feedbackItems = []
  let passedCount = 0

  Object.keys(rules).forEach(key => {
    const rule = rules[key]
    if (rule.pattern.test(code)) {
      score += 6.25
      passedCount++
      feedbackItems.push(`<span class="text-green-400">??${rule.desc}媛 ?ы븿?섏뿀?듬땲??</span>`)
    } else {
      feedbackItems.push(`<span class="text-gray-500">??${rule.desc}媛 ?꾨씫?섏뿀嫄곕굹 遺덈텇紐낇빀?덈떎.</span>`)
    }
  })

  userScore.step2 = Math.floor(score)
  const listHtml = `
    <div class="space-y-4">
      <p class="font-bold border-b border-white/10 pb-2 text-xl">?뚭퀬由ъ쬁 援ъ꽦 ?붿냼 泥댄겕:</p>
      <ul class="text-lg space-y-2">${feedbackItems.map(f => `<li>${f}</li>`).join('')}</ul>
      <div class="mt-6 pt-4 border-t border-white/10 text-lg">
        <p class="mt-2 text-pink-400 font-bold italic">Lion???ъ궗?? ${passedCount >= 4 ? "?꾨꼍???ㅺ퀎?낅땲?? ?댁젣 ???쇰━瑜??뚯씠??肄붾뱶濡???만 以鍮꾧? ?섏뀲援곗슂!" : "?ㅺ퀎媛 議곌툑 異붿긽?곸엯?덈떎. '臾댁뾿?????', '?대뼸寃?諛⑸쾿)' 泥섎━?좎? 紐낇솗???곸뼱蹂댁꽭??"}</p>
      </div>
    </div>
  `
  
  showFeedback(
    score >= 20 ? "?뮕 ?쇰━ ?ㅺ퀎 ?됯?: ?곗닔?? : "?뵩 ?쇰━ ?ㅺ퀎 ?됯?: 蹂댁셿 ?꾩슂",
    "Lion???뚭퀬由ъ쬁 ?붿쭊???붿??덉뼱?섏쓽 ?섏궗肄붾뱶瑜?遺꾩꽍?덉뒿?덈떎.",
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
    simulationOutput.value = '<span class="text-pink-500">Error: 鍮덉뭏??紐⑤몢 梨꾩썙???ㅽ뻾?????덉뒿?덈떎.</span>'
    return
  }

  isSimulating.value = true
  simulationOutput.value = '<span class="text-cyan-500">Initializing cleaning_protocol.v3...</span><br>'
  
  let cleaned_data = []
  let log = '<span class="text-cyan-400 font-black tracking-widest uppercase text-[10px] italic">Checking system_integrity_protocol...</span><br>'

  for (let news of sampleData) {
    log += `<span class="text-gray-500 italic mt-2">Checking_Node: "${news}"</span><br>`
    if (news.length < 5 || news.includes("愿묎퀬")) {
      if (bA === 'continue') {
        log += `<span class="text-yellow-500 font-mono">&nbsp;&nbsp;[PROT_SKIP]: ?꾪꽣留?議곌굔 ?쇱튂.</span><br>`
        continue 
      } else if (bA === 'break') {
        log += `<span class="text-red-500 font-mono">&nbsp;&nbsp;[PROT_HALT]: 諛섎났臾?媛뺤젣 醫낅즺??</span><br>`
        break
      }
    }
    if (bB === 'append(text)') {
      cleaned_data.push(news)
      log += `<span class="text-green-500 font-mono">&nbsp;&nbsp;[DATA_SAVE]: ?곗씠?곌? cleaned_data??而ㅻ컠??</span><br>`
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
  const bA = pythonBlanks.blankA?.text === 'continue'
  const bB = pythonBlanks.blankB?.text === 'append(text)'
  let score = 0
  if (bA) score += 12
  if (bB) score += 13

  userScore.step3 = score
  showFeedback(
    score === 25 ? "?릫 ?뚯씠??援ы쁽: ?꾨꼍?? : "?릫 ?뚯씠??援ы쁽: ?쇰? ?ㅻ쪟",
    score === 25 ? "?쇰━瑜?肄붾뱶濡??꾨꼍?섍쾶 蹂?섑븯?⑥뒿?덈떎." : "?쇰? 濡쒖쭅???섎룄? ?ㅻⅤ寃??숈옉?????덉뒿?덈떎.",
    `<div class="space-y-2"><p><strong>?ㅻ챸:</strong></p><p>1. <code>continue</code>???꾩옱 諛섎났??嫄대꼫?곌퀬 ?ㅼ쓬 ?곗씠?곕줈 ?섏뼱媛묐땲??</p><p>2. ?좏슚???곗씠?곕쭔 由ъ뒪?몄뿉 <code>append</code> ?댁빞 硫붾え由щ? ?⑥쑉?곸쑝濡??ъ슜?⑸땲??</p></div>`,
    score > 15
  )
}

const handleStep4Submit = (idx) => {
  const isCorrect = idx === 1
  userScore.step4 = isCorrect ? 25 : 0
  showFeedback(
    isCorrect ? "?뽳툘 ?ы솕 遺꾩꽍: ?몃젅?대뱶?ㅽ봽" : "?쨺 ?ы솕 遺꾩꽍: ?ㅼ떆 ?앷컖?대낫?몄슂",
    isCorrect ? "?뺣떟?낅땲?? ?덈Т ?꾧꺽???꾪꽣留곸? ?좎슜???곗씠?곌퉴吏 踰꾨┫ ???덉뒿?덈떎(False Positive)." : "?꾨떃?덈떎. ?꾪꽣留곸쓣 ?덈Т 媛뺥븯寃??섎㈃ ?ㅽ엳???곗씠??遺議??꾩긽??諛쒖깮?????덉뒿?덈떎.",
    "?쒖슜 ?щ?: ?ㅽ뙵 硫붿씪 ?꾪꽣媛 ?덈Т 媛뺣젰?섎㈃, 以묒슂???낅Т 硫붿씪源뚯? ?ㅽ뙵?듭쑝濡??ㅼ뼱媛??寃껉낵 媛숈뒿?덈떎. ?붿??덉뼱????긽 '?뺥솗??? '?ы쁽?? ?ъ씠??洹좏삎??留욎떠???⑸땲??",
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
  let review = `?붿??덉뼱?섏? ?곗씠?곌? AI 紐⑤뜽??誘몄튂???곹뼢???뺥솗???댄빐?섍퀬 ?덉뒿?덈떎. `
  review += userScore.step2 >= 20 ? "?섎룄肄붾뱶瑜??듯븳 ?쇰━ 援ъ“???λ젰???곗뼱?섎ŉ, " : "?섎룄肄붾뱶 ?묒꽦??議곌툑 ???곗뒿???꾩슂??蹂댁씠吏留? "
  review += userScore.step3 >= 20 ? "?뚯씠??肄붾뱶濡쒖쓽 蹂???λ젰???뚮??⑸땲??" : "肄붾뱶 援ы쁽 ?뷀뀒?쇱쓣 議곌툑留????ㅻ벉?쇰㈃ ?뚮????붿??덉뼱媛 ??寃껋엯?덈떎."
  review += "<br/><br/>?댁젣 ?ㅼ뿼???곗씠?곌? ?쒓굅?섏뿀?쇰땲, ?ㅼ쓬 ?ㅽ뀒?댁?(RAG ?쒖뒪??援ъ텞)濡??섏븘媛?以鍮꾧? ?섏뿀?듬땲??"
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
</style>
