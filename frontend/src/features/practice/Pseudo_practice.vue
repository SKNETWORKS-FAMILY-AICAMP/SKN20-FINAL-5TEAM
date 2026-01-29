<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <!-- [로딩 화면 또는 AI 평가 대기 화면] -->
    <div v-if="isLoading || isEvaluating" class="fixed inset-0 z-[200] flex flex-col items-center justify-center bg-slate-900 text-white p-6 text-center animate-in fade-in duration-700">
      <div class="relative w-48 h-48 bg-slate-800 rounded-full flex items-center justify-center p-8 shadow-inner overflow-hidden border-4 border-slate-700 mb-8">
        <img :src="duckAssets.idle" class="w-full h-full object-contain animate-pixar-fly">
        <div class="absolute inset-0 bg-indigo-500/10 animate-pulse"></div>
      </div>
      <div class="space-y-3">
        <h2 class="text-4xl font-black text-white font-jua">{{ isEvaluating ? '코드 위저드가 분석 중...' : '퀘스트 준비 중...' }}</h2>
        <p class="text-slate-400 font-bold animate-pulse text-lg">{{ isEvaluating ? '당신의 아키텍처 통찰력을 정교하게 분석하고 있습니다.' : '잠시만 기다려주세요!' }}</p>
      </div>
    </div>

    <!-- 메인 컨테이너 -->
    <div class="max-w-6xl w-full bg-white rounded-[3.5rem] shadow-2xl overflow-hidden border-[12px] border-slate-900 relative flex flex-col h-[750px]">
      <!-- 헤더: 여백 최적화 (라운딩 56px + 테두리 12px 고려하여 80px 설정) -->
      <div class="bg-slate-900 text-white flex justify-between items-center font-jua border-b-4 border-slate-800" 
           style="padding: 40px 80px 20px 80px;">
        <div class="flex items-center gap-6">
          <h1 class="text-4xl font-black text-yellow-400 drop-shadow-md">PseudoPractice</h1>
          <span class="bg-white/10 px-6 py-1.5 rounded-full text-lg border border-white/20">{{ currentStep }}층 진행 중</span>
        </div>
        <div class="flex items-center gap-8">
          <div class="bg-yellow-400 text-slate-900 px-8 py-2.5 rounded-2xl font-black text-xl shadow-lg">
            점수: {{ score }}
          </div>
          <!-- 닫기 버튼: 헤더 영역 내로 통합 및 위치 조정 -->
          <button @click="$emit('close')" class="text-slate-400 hover:text-yellow-500 text-5xl transition-colors font-bold leading-none">&times;</button>
        </div>
      </div>

      <div class="flex flex-col md:flex-row flex-grow overflow-hidden min-h-0">
        <!-- 왼쪽 영역: 계단 및 오리 (비율 조정: 48%) -->
        <div class="w-full md:w-[48%] bg-sky-100 p-6 border-r-4 border-slate-900 relative overflow-hidden flex items-end h-full">
          <!-- 말풍선 -->
          <div class="absolute top-8 left-6 right-6 z-[110]">
            <div class="duck-bubble transition-opacity duration-300 min-h-[50px] flex items-center justify-center shadow-lg" :style="{ opacity: showBubble ? 1 : 0 }">
              <p class="text-slate-800 font-bold text-sm text-center leading-tight whitespace-pre-line">{{ bubbleMsg }}</p>
            </div>
          </div>

          <!-- 계단 컨테이너 -->
          <div class="relative w-full h-[550px] flex items-end">
            <!-- START 플랫폼 -->
            <div class="stair-start absolute" 
                 :style="{ 
                    width: '180px', 
                    height: '60px', 
                    left: '20px', 
                    bottom: '40px',
                    zIndex: 0
                 }">
              <div class="platform-top">START</div>
              <div class="platform-side"></div>
            </div>

            <!-- 대각선 계단 (동적 생성) -->
            <div v-for="i in currentQuest.solution.length" :key="i" 
                 class="stair-pill group transition-all duration-300" 
                 :class="{ 'active-target': (currentStep === i-1) }"
                 :style="{ 
                    width: '260px', 
                    height: '55px', 
                    left: (i * 30 + (i % 2 === 0 ? 120 : 0)) + 'px', 
                    bottom: (i * 80 + 30) + 'px',
                    zIndex: i 
                 }"
                 @dragover.prevent
                 @drop="onDrop($event, i-1)">
                 
                 <!-- 배치된 블록 -->
                 <div v-if="droppedBlocks[i-1]" 
                      class="placed-block-refined"
                      :class="droppedBlocks[i-1].color">
                   <span class="text-2xl">{{ droppedBlocks[i-1].icon }}</span>
                   <span class="block-text">{{ droppedBlocks[i-1].text }}</span>
                   <button @click.stop="removeBlock(i-1)" class="remove-btn-refined">✕</button>
                 </div>

                 <!-- 현재 채워야 할 타겟 표시 (점선 알약) -->
                 <div v-else class="empty-stair-pill">
                    <div v-if="currentStep === i-1" class="text-slate-300 text-3xl animate-pulse">📥</div>
                 </div>
            </div>

            <!-- 골 지점 -->
            <div class="absolute w-[80px] h-[80px] flex items-center justify-center transition-all duration-500" 
                 :style="{ 
                    left: (currentQuest.solution.length * 30 + (currentQuest.solution.length % 2 === 0 ? 160 : 40)) + 'px', 
                    bottom: (currentQuest.solution.length * 80 + 30) + 'px' 
                 }">
                <div class="text-5xl animate-bounce">👑</div>
            </div>
          </div>

          <!-- 오리 캐릭터: 포지셔닝 보정 -->
          <div id="duck-actor" 
               class="absolute transition-all duration-700 z-[100]" 
               :class="{ 'animate-fall': isFalling, 'animate-pixar-fly': isFlying }" 
               :style="{ ...duckPosition, width: '110px', height: '110px' }" 
               @mouseenter="handleDuckHover(true)" 
               @mouseleave="handleDuckHover(false)">
             <div v-if="isFlying" class="fixed inset-0 bg-white/30 backdrop-blur-sm z-[200] flex flex-col items-center justify-center pointer-events-none animate-in fade-in duration-1000">
               <div class="text-7xl font-black text-amber-500 animate-bounce mb-4 font-jua text-shadow-lg">AWESOME! 🐥</div>
               <div class="text-4xl text-slate-700 font-bold opacity-80">파닥파닥! 다음 단계로 날아가요! ✨</div>
             </div>

             <div class="w-full h-full relative" :style="{ transform: isHovering ? 'scale(1.15) rotate(5deg)' : 'scale(1)' }">
               <img class="duck-frame" :src="duckAssets.idle" :style="{ opacity: (currentEmotion === 'idle' && !isFlying) ? 1 : 0 }" alt="idle">
               <img class="duck-frame" :src="duckAssets.happy" :style="{ opacity: (currentEmotion === 'happy' || isFlying) ? 1 : 0 }" alt="happy">
               <img class="duck-frame" :src="duckAssets.sad" :style="{ opacity: currentEmotion === 'sad' ? 1 : 0 }" alt="sad">
               <img class="duck-frame" :src="duckAssets.hover" :style="{ opacity: currentEmotion === 'hover' ? 1 : 0 }" alt="hover">
               
               <!-- 비행 깃털/구름 효과 -->
               <div v-if="isFlying" class="absolute -bottom-10 left-1/2 -translate-x-1/2 flex gap-2 pointer-events-none">
                 <div class="text-4xl animate-ping opacity-60">🪶</div>
                 <div class="text-4xl animate-ping opacity-40 delay-300">✨</div>
               </div>
            </div>
          </div>
        </div>

        <!-- 오른쪽 영역: 문제 풀이 (비율 조정: 52%) -->
        <div class="w-full md:w-[52%] p-10 flex flex-col bg-white overflow-y-auto h-full">
          
          <!-- 1단계: 퍼즐 -->
          <div v-if="stage === 1" class="space-y-10 h-full flex flex-col">
            <div class="border-l-8 border-yellow-400 pl-6 py-2">
              <span class="px-4 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-black mb-2 inline-block">QUEST {{ currentQuestIdx + 1 }}</span>
              <h2 class="text-3xl font-black text-slate-800 font-jua mb-2">{{ currentQuest.title }}</h2>
              <p class="text-slate-500 font-bold text-lg">{{ currentQuest.desc }}</p>
            </div>
            
            <div class="flex flex-col gap-6 flex-grow">
               <!-- 힌트 영역 -->
               <div v-if="showHint" class="bg-rose-50 border-2 border-rose-100 p-6 rounded-[2rem] animate-in fade-in slide-in-from-top-4 duration-500">
                 <p class="text-rose-600 font-black flex items-center gap-2">
                   <span>💡 힌트</span>
                   <span class="text-sm font-bold text-rose-500">{{ currentQuest.hint || "블록의 순서가 중요해요!" }}</span>
                 </p>
               </div>

               <!-- 선택 가능한 블록: 콤팩트 디자인 -->
               <div class="bg-white p-6 rounded-[2.5rem] border-2 border-slate-200 shadow-sm">
                <h3 class="text-slate-400 font-black text-xs mb-3 tracking-widest uppercase flex items-center gap-2">
                   <span class="w-3 h-3 bg-yellow-400 rounded-full"></span>
                   코딩 블록 보관함
                </h3>
                <div class="flex flex-wrap gap-2">
                  <div v-for="block in availableBlocks" 
                       :key="block.id" 
                       draggable="true" 
                       @dragstart="onDragStart($event, block)" 
                       class="block-item group px-4 py-2.5 rounded-2xl text-xs font-black shadow-sm text-slate-800 transform hover:-translate-y-1 hover:scale-105 active:scale-95 transition-all flex items-center gap-2 bg-slate-50 border-b-4 border-slate-200" 
                       :class="[block.color, { 'opacity-30 grayscale cursor-not-allowed': isBlockUsed(block.id) }]">
                    <span class="bg-white/50 w-6 h-6 rounded-lg flex items-center justify-center text-sm">{{ block.icon }}</span>
                    {{ block.text }}
                  </div>
                </div>
              </div>

              <!-- 안내 메시지 (복구) -->
              <div v-if="droppedBlocks.every(b => !b)" class="mt-4 p-8 border-4 border-dashed border-slate-200 rounded-[2.5rem] flex flex-col items-center justify-center text-slate-400 gap-3 bg-white/50 animate-pulse">
                <div class="text-4xl">🖱️</div>
                <p class="font-black text-sm text-center leading-relaxed">왼쪽의 비어있는 계단으로<br>블록을 드래그해서 올려주세요!</p>
              </div>
            </div>
          </div>

          <div v-else-if="stage === 2" class="space-y-10 h-full flex flex-col">
            <div class="space-y-2">
              <span class="px-5 py-1.5 bg-indigo-100 text-indigo-600 rounded-full text-sm font-black tracking-tighter">PHASE 02</span>
              <h2 class="text-4xl font-black text-slate-800 tracking-tight">실전 코드 구현</h2>
              <div class="mt-4 p-6 bg-slate-50 border-2 border-slate-100 rounded-2xl">
                <p class="text-slate-600 font-bold leading-relaxed">
                  <span class="text-indigo-500">Q.</span> {{ currentQuest.title }} 로직을 파이썬으로 구현해 보세요!
                </p>
              </div>
            </div>

            <!-- 코드 에디터: 테마 보강 -->
            <div class="bg-slate-900 rounded-[2.5rem] p-10 text-emerald-400 font-mono text-xl leading-relaxed shadow-2xl relative border-t-8 border-slate-800">
              <div class="absolute top-4 right-8 bg-slate-800 px-3 py-1 rounded-full text-slate-500 text-[10px] uppercase tracking-widest font-bold border border-slate-700">Python v3.11</div>
              <div><span class="text-pink-500">def</span> <span class="text-blue-400">{{ currentQuest.id === 5 ? 'check_fee' : 'process_logic' }}</span>(input_data):</div>
              <div class="pl-8 flex items-center gap-2"><span class="text-pink-500">if</span> value == <input v-model="codeInputs.price" type="text" :placeholder="currentQuest.codeValidation.price" class="bg-slate-800 border-b-4 border-emerald-500 w-32 text-center outline-none focus:bg-slate-700 transition-colors">:</div>
              <div class="pl-16 flex items-center gap-2">result = <input v-model="codeInputs.fee1" type="text" :placeholder="currentQuest.codeValidation.fee1" class="bg-slate-800 border-b-4 border-emerald-500 w-32 text-center outline-none focus:bg-slate-700 transition-colors"></div>
              <div class="pl-8"><span class="text-pink-500">else</span>:</div>
              <div class="pl-16 flex items-center gap-2">result = <input v-model="codeInputs.fee2" type="text" :placeholder="currentQuest.codeValidation.fee2" class="bg-slate-800 border-b-4 border-emerald-500 w-32 text-center outline-none focus:bg-slate-700 transition-colors"></div>
              <div class="pl-8"><span class="text-pink-500">return</span> result</div>
            </div>
            <!-- 코드 실행 버튼: Pixar 스타일 고도화 -->
            <button @click="checkStage2" class="run-code-btn group">
              <span class="flex items-center justify-center gap-3">
                <span class="btn-icon">▶</span>
                <span class="btn-text">로직 검증 및 코드 실행</span>
              </span>
              <div class="btn-glow"></div>
            </button>
          </div>

          <div v-else-if="stage === 3" class="space-y-8 h-full">
            <h2 class="text-2xl font-black text-slate-800 font-jua mb-2">3단계: 비즈니스 설계</h2>
            <div class="bg-blue-50 p-8 rounded-[2.5rem] border-4 border-blue-200 space-y-6">
              <p class="text-slate-700 font-bold text-lg italic">"이 로직을 더 고도화하려면?"</p>
              <div class="grid grid-cols-1 gap-4">
                <button v-for="(opt, i) in currentQuest.quizOptions" :key="i" @click="verifyStage3(opt.correct)" class="p-4 bg-white border-2 border-slate-200 rounded-2xl hover:border-blue-500 font-bold text-slate-600 shadow-sm text-left transition-all hover:scale-[1.02]">
                  {{ opt.text }}
                </button>
              </div>
            </div>
          </div>

          <!-- [2026-01-27] Stage 3.5: The Thinking Bridge (꼬리 질문 스테이지) -->
          <div v-else-if="stage === 3.5" class="h-full flex flex-col justify-center items-center p-8 relative overflow-hidden bg-slate-900 rounded-[3rem] text-white">
            <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-500/10 via-transparent to-transparent"></div>
            
            <div class="z-10 text-center space-y-8 w-full max-w-xl">
              <div class="inline-block px-4 py-1.5 bg-amber-500 text-slate-900 rounded-full text-xs font-black uppercase tracking-[0.2em] mb-4">The Wizard's Meditation</div>
              
              <div class="space-y-4">
                <h3 class="text-3xl font-black text-white leading-tight">잠시만요, 라이언님!</h3>
                <p class="text-indigo-300 font-bold text-lg">최종 분석 전에 대현자님이 궁금한 게 있대요.</p>
              </div>

              <!-- 질문 타이핑 영역 -->
              <div class="bg-white/5 border border-white/10 p-8 rounded-[2rem] backdrop-blur-xl min-h-[140px] flex items-center justify-center">
                <p class="text-xl font-bold leading-relaxed text-amber-200 italic">
                  "{{ typedQuestion || '분석 중...' }}"
                </p>
              </div>

              <!-- 답변 입력창 (Min 10 chars) -->
              <div class="space-y-4">
                <textarea 
                  v-model="userFreeAnswer" 
                  placeholder="대현자님께 라이언님의 생각을 들려주세요 (최소 10자)..."
                  class="w-full bg-slate-800 border-2 border-white/10 rounded-2xl p-6 text-white font-bold outline-none focus:border-indigo-500 transition-all resize-none h-32"
                ></textarea>
                <div class="flex justify-between items-center text-xs font-bold px-2">
                  <span :class="userFreeAnswer.length >= 10 ? 'text-emerald-400' : 'text-slate-500'">글자수: {{ userFreeAnswer.length }} / 최소 10자</span>
                  <span class="text-slate-500 italic">"진정한 엔지니어는 자신의 논리를 설명할 수 있어야 하네."</span>
                </div>
              </div>

              <button 
                @click="submitFinalAnswer" 
                :disabled="userFreeAnswer.length < 10 || isSubmittingAnswer"
                class="w-full py-5 rounded-2xl font-black text-xl transition-all flex items-center justify-center gap-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:opacity-50 shadow-xl shadow-indigo-500/20"
              >
                {{ isSubmittingAnswer ? '대현자의 최종 분석을 기다리는 중...' : '생각 전달하기' }}
              </button>
            </div>
          </div>

          <div v-else-if="stage === 4" class="h-full flex flex-col items-center justify-start space-y-4 py-6 overflow-y-auto px-10">
            <!-- 트로피 제거 및 상단 정제 (마진 축소) -->
            <div class="text-center space-y-1 mb-2">
              <h2 class="text-3xl font-black text-slate-900 font-jua tracking-tight">{{ finalGrade === 'A+' ? '완벽한 엔지니어의 탄생!' : '미션을 완료했습니다!' }}</h2>
              <p class="text-slate-400 font-bold text-[10px] uppercase tracking-[0.4em]">Integrated Performance Report v7.5</p>
            </div>

            <!-- 성과 보드 (2컬럼 프리미엄 리포트) -->
            <div class="w-full max-w-5xl bg-slate-50 border-4 border-slate-900 rounded-[3rem] p-10 shadow-2xl flex flex-col md:flex-row gap-12 animate-in zoom-in duration-700 relative overflow-hidden">
              <!-- 배경 장식 -->
              <div class="absolute -top-24 -left-24 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl"></div>
              <div class="absolute -bottom-24 -right-24 w-64 h-64 bg-amber-500/5 rounded-full blur-3xl"></div>

              <!-- 왼쪽: 레이더 차트 시각화 (AI 전용 - 영역 축소: 32%) -->
              <div class="w-full md:w-[32%] flex flex-col items-center justify-center p-6 bg-white rounded-[2.5rem] shadow-[0_20px_50px_rgba(0,0,0,0.05)] border-2 border-slate-100 relative z-10 min-h-[350px]">
                <div class="text-center mb-6">
                  <p class="text-slate-400 text-[9px] font-bold uppercase tracking-[0.3em] mb-1">AI-Powered Analysis</p>
                  <h3 class="text-slate-900 font-extrabold text-sm tracking-tight">PERFORMANCE SPECTRUM</h3>
                </div>
                
                <div class="relative w-48 h-48 flex items-center justify-center">
                  <svg viewBox="0 0 200 200" class="w-full h-full filter drop-shadow-[0_10px_10px_rgba(0,0,0,0.05)]">
                    <!-- 배경 그리드 (정오각형, Top에서 시작하도록 좌표 재계산) -->
                    <polygon points="100,10 185.6,72.2 152.9,172.8 47.1,172.8 14.4,72.2" fill="none" stroke="#f1f5f9" stroke-width="2" />
                    <polygon points="100,40 157.1,81.5 135.3,148.5 64.7,148.5 42.9,81.5" fill="none" stroke="#f8fafc" stroke-width="1.5" />
                    <polygon points="100,70 128.5,90.7 117.6,124.3 82.4,124.3 71.5,90.7" fill="none" stroke="#fbfcfd" stroke-width="1" />
                    
                    <!-- 축 표시 -->
                    <line v-for="i in 5" :key="i" x1="100" y1="100" 
                          :x2="100 + 90 * Math.sin((i-1) * (Math.PI * 2) / 5)" 
                          :y2="100 - 90 * Math.cos((i-1) * (Math.PI * 2) / 5)" 
                          stroke="#f1f5f9" stroke-width="1.5" />

                    <!-- 데이터 영역 (AI 로딩 전후 처리) -->
                    <g v-if="aiMetrics">
                      <polygon :points="radarPointsPath" fill="rgba(99, 102, 241, 0.2)" stroke="#6366f1" stroke-width="4" stroke-linejoin="round" class="transition-all duration-1000" />
                      <circle v-for="p in radarCirclePoints" :key="p.x + p.y" :cx="p.x" :cy="p.y" r="5" fill="white" stroke="#6366f1" stroke-width="3" />
                    </g>
                    <!-- 로딩 상태 가이드 차트 (중점만 표시) -->
                    <circle v-else cx="100" cy="100" r="3" fill="#e2e8f0" />
                  </svg>
                  
                  <!-- 지표 라벨 (축소된 차트에 맞춰 위치/크기 보정) -->
                  <div class="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] font-black text-slate-500 bg-slate-50 px-2 py-0.5 rounded-full border border-slate-200">정합성</div>
                  <div class="absolute top-[28%] -right-12 -translate-y-1/2 text-[10px] font-black text-slate-500 bg-slate-50 px-2 py-0.5 rounded-full border border-slate-200">추상화</div>
                  <div class="absolute bottom-4 -right-6 text-[10px] font-black text-slate-500 bg-slate-50 px-2 py-0.5 rounded-full border border-slate-200">예외처리</div>
                  <div class="absolute bottom-4 -left-6 text-[10px] font-black text-slate-500 bg-slate-50 px-2 py-0.5 rounded-full border border-slate-200">구현력</div>
                  <div class="absolute top-[28%] -left-12 -translate-y-1/2 text-[10px] font-black text-slate-500 bg-slate-50 px-2 py-0.5 rounded-full border border-slate-200">설계력</div>
                </div>
              </div>

              <!-- 오른쪽: 상세 지표 및 AI 피드백 (영역 확장: 68%) -->
              <div class="w-full md:w-[68%] space-y-6 text-left relative z-10">
                <div class="bg-white p-6 rounded-[2.5rem] shadow-sm border border-slate-200 space-y-4">
                  <div class="flex justify-between items-start">
                    <div>
                      <p class="text-slate-400 text-[9px] font-black uppercase tracking-widest">Assessment Profile</p>
                      <h4 class="text-2xl font-black text-slate-900 leading-tight">Training Performance</h4>
                    </div>
                    <div class="bg-indigo-600 text-white px-5 py-3 rounded-2xl flex flex-col items-center justify-center shadow-xl shadow-indigo-100 gap-1 shrink-0">
                      <span class="text-[9px] font-bold opacity-70 uppercase tracking-tighter leading-none">TOTAL SCORE</span>
                      <div class="flex items-baseline gap-0.5">
                        <span class="text-3xl font-black leading-none">{{ score }}</span>
                        <span class="text-[10px] font-bold opacity-80">pts</span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 상세 지표 리스트 (하드코딩 제거: AI 지표만 사용) -->
                  <div class="grid grid-cols-2 gap-4">
                    <div v-for="(val, key) in radarPoints" :key="key" 
                         class="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex flex-col justify-between group overflow-hidden relative">
                      <div class="relative z-10">
                        <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{{ key }}</p>
                        <p class="text-2xl font-black text-slate-800 transition-transform group-hover:scale-110 origin-left">{{ val }}<span class="text-sm font-bold ml-0.5 opacity-50">%</span></p>
                      </div>
                      <!-- 미니 막대 프로그레스 -->
                      <div class="w-full h-1.5 bg-slate-200 rounded-full mt-3 overflow-hidden">
                        <div class="h-full bg-indigo-500 transition-all duration-1000" :style="{ width: val + '%' }"></div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- AI 위저드 인사이트 (내부 스크롤 가능하게 수정) -->
                <div class="relative pt-4 flex-grow min-h-0">
                  <!-- 말풍선 꼬리 -->
                  <div class="absolute top-1 left-10 w-6 h-6 bg-amber-50 rotate-45 border-l-2 border-t-2 border-amber-100 -z-0"></div>
                  
                  <div class="bg-amber-50 p-6 rounded-[2.5rem] border-2 border-amber-100 relative shadow-sm group h-full flex flex-col">
                    <div class="flex items-center gap-3 mb-3 shrink-0">
                      <div class="w-10 h-10 bg-amber-400 rounded-2xl flex items-center justify-center text-xl shadow-md animate-bounce-slow">🧙‍♂️</div>
                      <div>
                        <h4 class="text-amber-900 font-extrabold text-xs"> 대현자 '코드 위저드'의 분석</h4>
                      </div>
                      <div v-if="!isLogical" class="bg-rose-100 text-rose-600 px-2 py-0.5 rounded text-[8px] font-black animate-pulse">LOGIC WARNING</div>
                    </div>
                    <div class="overflow-y-auto pr-2 max-h-[160px]">
                      <p class="text-amber-900/80 font-bold text-[14px] leading-relaxed relative z-10 whitespace-pre-line">
                        {{ mentorAnalysis || evaluationMessage }}
                      </p>
                      
                      <!-- [2026-01-27] 추가 조언(Advice) 섹션 -->
                      <div v-if="mentorAdvice" class="mt-4 p-4 bg-white/50 rounded-2xl border border-amber-200/50">
                        <p class="text-[9px] font-black text-amber-500 uppercase tracking-widest mb-1">Mentor's Advice</p>
                        <p class="text-amber-800 text-xs font-black italic">"{{ mentorAdvice }}"</p>
                      </div>
                    </div>
                    <!-- AI 로딩 스피너 -->
                    <div v-if="!mentorAnalysis" class="mt-2 flex items-center gap-2">
                      <div class="w-1.5 h-1.5 bg-amber-400 rounded-full animate-pulse"></div>
                      <div class="w-1.5 h-1.5 bg-amber-400 rounded-full animate-pulse delay-150"></div>
                      <div class="w-1.5 h-1.5 bg-amber-400 rounded-full animate-pulse delay-300"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex gap-4">
              <button @click="resetGame" class="bg-indigo-600 text-white px-8 py-4 rounded-[2rem] font-black shadow-xl hover:scale-105 transition-all text-lg">다시 시작하기</button>
              <button @click="$emit('close')" class="bg-slate-800 text-white px-8 py-4 rounded-[2rem] font-black shadow-xl hover:scale-105 transition-all text-lg">나가기</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * [수정일: 2026-01-27]
 * [수정내용: 워처(watcher) 실행 시 초기화 순서로 인한 오류 수정 및 로딩 상태 제어 로직 보강]
 */
import { ref, reactive, computed, onMounted } from 'vue';
import axios from 'axios';
import { aiQuests } from './support/unit1/logic-mirror/data/stages.js';

const props = defineProps({
  initialQuestIndex: { type: Number, default: 0 }
});
const emit = defineEmits(['close', 'quest-complete']);

// --- State ---
const currentQuestIdx = ref(props.initialQuestIndex);
const currentQuest = computed(() => aiQuests[currentQuestIdx.value] || aiQuests[0]);
const isLoading = ref(true);
const isEvaluating = ref(false); // [2026-01-27] AI 평가 대기 상태 추가
const loadingStep = ref("캐릭터 준비 중...");
const stage = ref(1);
const score = ref(0);
const currentStep = ref(0);
const duckAssets = reactive({ 
  idle: '/image/duck_idle.png', 
  happy: '/image/duck_happy.png', 
  sad: '/image/duck_sad.png', 
  hover: '/image/duck_hover.png' 
});
const currentEmotion = ref('idle');
const bubbleMsg = ref("");
const showBubble = ref(false);
const isFalling = ref(false);
const isFlying = ref(false);
const isHovering = ref(false);

// [수정일: 2026-01-27] Gemini 제안 다차원 평가 데이터 구조
const evaluationResults = reactive({
  logicScore: 0,      // 1단계: 논리 구조화
  codingScore: 0,     // 2단계: 코드 구현
  designScore: 0,     // 3단계: 아키텍처 설계
  penaltyCount: 0,    // 틀린 횟수
  hintsUsed: 0,       // 사용한 힌트 수
  timeSpent: 0,       // 총 소요 시간 (초)
  stageTimestamps: {
    start: null,
    stage2Start: null,
    stage3Start: null,
    end: null
  },
  perkFlags: {
    oneShotCoding: true, // 2단계 한 번에 성공 여부
    perfectDesign: false // 3단계 성공 여부
  }
});

const personaTitle = ref("평범한 개발자");

// Quiz State
const availableBlocks = ref([]);
const droppedBlocks = ref([]);
const showHint = ref(false);
const hintMessage = ref("");
const aiFeedback = ref(""); // This seems to be an older variable, replaced by mentorAnalysis/Advice
const aiMetrics = ref(null);

const isBlockUsed = (id) => droppedBlocks.value.some(b => b && b.id === id);
const codeInputs = reactive({ price: '', fee1: '', fee2: '' });
const stage3Options = computed(() => currentQuest.value.quizOptions);

const initQuestData = () => {
    if (!currentQuest.value) return;
    
    availableBlocks.value = [...currentQuest.value.cards];
    droppedBlocks.value = new Array(currentQuest.value.cards.length).fill(null);
    hintMessage.value = currentQuest.value.hint || "블록을 순서대로 드래그하세요!";
    currentStep.value = 0;
    stage.value = 1;
    score.value = 0;
    
    // 평가 초기화
    Object.assign(evaluationResults, {
      logicScore: 0, codingScore: 0, designScore: 0,
      penaltyCount: 0, hintsUsed: 0, timeSpent: 0,
      stageTimestamps: { start: Date.now(), stage2Start: null, stage3Start: null, end: null },
      perkFlags: { oneShotCoding: true, perfectDesign: false }
    });
    
    codeInputs.price = '';
    codeInputs.fee1 = '';
    codeInputs.fee2 = '';
    
    setTimeout(() => { isLoading.value = false; }, 800);
};

import { watch } from 'vue';
watch(currentQuest, initQuestData, { immediate: true });

onMounted(() => {
    // 필요한 초기화 작업이 있다면 여기에 추가
});

const duckPosition = computed(() => {
    // 1. START 위치 초기값 (축소된 가로 너비에 맞춰 보정)
    let x = 40;
    let y = 80;

    // 2. 현재 단계 계단 위치로 이동 (지그재그 보정)
    if (currentStep.value > 0) {
        const stairIndex = Math.min(currentStep.value, currentQuest.value.solution.length);
        const i = stairIndex; 
        x = (i * 30 + (i % 2 === 0 ? 120 : 0)) + 40; 
        y = (i * 80 + 30) + 55; 
    }
    
    return {
        bottom: y + 'px',
        left: x + 'px'
    };
});

// [2026-01-27] 생각하는 힘 강화용 상태 추가
const tailQuestion = ref(null);
const userFreeAnswer = ref("");
const typedQuestion = ref(""); // 질문 타이핑 효과용
const mentorAnalysis = ref(""); // AI 최종 분석 결과
const mentorAdvice = ref(""); // AI 최종 조언
const isLogical = ref(true); // AI가 판단한 논리적 일관성
const isSubmittingAnswer = ref(false); // 답변 제출 중 로딩 상태

const finalGrade = computed(() => {
    if (score.value >= 90) return 'S';
    if (score.value >= 75) return 'A';
    if (score.value >= 60) return 'B';
    return 'C';
});

const evaluationMessage = computed(() => {
    if (mentorAnalysis.value) return mentorAnalysis.value; // Use mentorAnalysis if available
    
    // AI 피드백이 없을 때의 기본 대화 (등급 기반)
    if (finalGrade.value === 'S') return "완벽한 설계와 구현 능력입니다!\n라이언님은 이미 훌륭한 엔지니어예요!";
    if (finalGrade.value === 'A') return "매우 훌륭합니다!\n조금만 더 연습하면 마스터가 될 수 있어요.";
    if (finalGrade.value === 'B') return "고생하셨습니다!\n프로그래밍의 기초를 착실히 다졌네요.";
    return "수고하셨습니다!\n한 번 더 도전하여 높은 등급을 받아보세요!";
});

// --- Radar Chart Logic ---
const radarPoints = computed(() => {
    // [2026-01-27] 하드코딩 완전 제거: AI 분석 데이터가 있는 경우에만 유의미한 수치 반환
    if (aiMetrics.value) {
        return {
            "정합성": aiMetrics.value["정합성"] || 0,
            "추상화": aiMetrics.value["추상화"] || 0,
            "예외처리": aiMetrics.value["예외처리"] || 0,
            "구현력": aiMetrics.value["구현력"] || 0,
            "설계력": aiMetrics.value["설계력"] || 0
        };
    }
    // AI 데이터 로딩 전에는 0으로 초기화하여 시각적 정합성 유지 (하드코딩 Fallback 제거)
    return {
        "정합성": 0,
        "추상화": 0,
        "예외처리": 0,
        "구현력": 0,
        "설계력": 0
    };
});

const radarCirclePoints = computed(() => {
    const points = Object.values(radarPoints.value);
    const center = 100;
    const radius = 90;
    const angleStep = (Math.PI * 2) / 5;

    return points.map((val, i) => {
        const r = (val / 100) * radius;
        // [2026-01-27] Geometry 보정: Math.sin/cos 사용하여 Top(-90deg) 위치에서 정오각형 산출
        const angle = i * angleStep - Math.PI / 2; // Start from top (-90 degrees)
        return {
            x: center + r * Math.cos(angle),
            y: center + r * Math.sin(angle)
        };
    });
});

const radarPointsPath = computed(() => {
    return radarCirclePoints.value.map(p => `${p.x},${p.y}`).join(' ');
});

// --- Methods ---
const displayMessage = (msg) => {
    bubbleMsg.value = msg;
    showBubble.value = true;
    // 이전 타이머 제거 로직이 필요할 수 있으나 여기선 단순화
    setTimeout(() => {
      if (bubbleMsg.value === msg) showBubble.value = false;
    }, 3000);
};

const onDragStart = (e, block) => {
    e.dataTransfer.setData("blockId", block.id);
};

const onDrop = (e, stairIdx) => {
    if (stairIdx !== currentStep.value) {
        displayMessage("순서대로 계단을 올라가야 해요!");
        return;
    }

    const id = e.dataTransfer.getData("blockId");
    const block = availableBlocks.value.find(b => b.id === id);
    const correctId = currentQuest.value.solution[stairIdx];
    
    if (id === correctId) {
        droppedBlocks.value[stairIdx] = block;
        currentStep.value++;
        
        currentEmotion.value = 'happy';
        showHint.value = false;
        displayMessage("정답이에요! 껑충!");
        
        if (currentStep.value === currentQuest.value.solution.length) {
            isFlying.value = true;
            displayMessage("파닥파닥! 날아올라요! 🐥");
            setTimeout(() => { 
                stage.value = 2; 
                evaluationResults.stageTimestamps.stage2Start = Date.now();
                isFlying.value = false;
                currentEmotion.value = 'idle'; 
            }, 2500);
        } else {
            setTimeout(() => currentEmotion.value = 'idle', 1000);
        }
    } else {
        handleFailure();
    }
};

const removeBlock = (idx) => {
    if (idx < currentStep.value) {
        // [2026-01-27] 중간 블록 삭제 시 그 위로 배치된 모든 블록을 함께 취소하여 논리적 순차성 유지
        for (let i = currentStep.value - 1; i >= idx; i--) {
            droppedBlocks.value[i] = null;
            currentStep.value--;
            score.value = Math.max(0, score.value - 20);
        }
        displayMessage("로직을 재구성합니다! 🔧");
    }
};

const handleFailure = () => {
    evaluationResults.penaltyCount++; // [2026-01-27] 패널티 카운트 증가
    currentEmotion.value = 'sad';
    displayMessage("으아앙! 틀렸어요!");
    showHint.value = true;
    if (stage.value === 1) evaluationResults.hintsUsed++; // 1단계 힌트 사용 체크
    if (stage.value === 2) evaluationResults.perkFlags.oneShotCoding = false; // 2단계 오답 시 깃발 종료
    
    // 오리가 계단에서 미끄러지는 연출
    isFalling.value = true;
    setTimeout(() => {
        isFalling.value = false;
        currentEmotion.value = 'idle';
    }, 1000);
};

const checkStage2 = () => {
    const val = currentQuest.value.codeValidation;
    if (codeInputs.price === val.price && codeInputs.fee1 === val.fee1 && codeInputs.fee2 === val.fee2) {
        currentEmotion.value = 'happy';
        displayMessage("코드 구현 성공!");
        setTimeout(() => { 
            stage.value = 3; 
            evaluationResults.stageTimestamps.stage3Start = Date.now();
            currentEmotion.value = 'idle'; 
        }, 1500);
    } else {
        handleFailure();
    }
};

const verifyStage3 = async (isCorrect) => {
    if (isCorrect) {
        score.value += 20; // Adjusted score as per instruction
        currentEmotion.value = 'happy';
        displayMessage("완벽한 설계군요! 대현자님이 이제 라이언님의 깊은 생각을 묻고자 하십니다.");
        
        // [2026-01-27] Stage 3.5 (Bridge) 진입 및 꼬리 질문 1차 페치
        stage.value = 3.5;
        fetchInitialTailQuestion();
        emit('quest-complete', currentQuestIdx.value);
    } else {
        handleFailure();
    }
};
const fetchInitialTailQuestion = async () => {
    typedQuestion.value = "";
    try {
        const response = await axios.post('/api/core/ai-evaluate/', {
            score: score.value,
            grade: finalGrade.value,
            quest_title: currentQuest.value.title,
            user_logic: droppedBlocks.value.filter(b => b).map(b => b.text),
            user_code: codeInputs,
            user_free_answer: ""
        });
        
        if (response.data.tail_question) {
            tailQuestion.value = response.data.tail_question;
            startTypingEffect(tailQuestion.value.question);
        }
    } catch (e) {
        console.error("Tail question fetch failed:", e);
        startTypingEffect("자네의 로직이 어떤 예외 상황에서 멈출 수 있을지 말해주겠나?");
    }
};

const startTypingEffect = (text) => {
    let i = 0;
    typedQuestion.value = "";
    const interval = setInterval(() => {
        typedQuestion.value += text[i];
        i++;
        if (i === text.length) clearInterval(interval);
    }, 40);
};

const submitFinalAnswer = async () => {
    isSubmittingAnswer.value = true;
    try {
        const response = await axios.post('/api/core/ai-evaluate/', {
            score: score.value,
            grade: finalGrade.value,
            quest_title: currentQuest.value.title,
            user_logic: droppedBlocks.value.filter(b => b).map(b => b.text),
            user_code: codeInputs,
            user_free_answer: userFreeAnswer.value
        });
        
        if (response.data.metrics) aiMetrics.value = response.data.metrics;
        mentorAnalysis.value = response.data.analysis || response.data.feedback;
        mentorAdvice.value = response.data.advice;
        isLogical.value = response.data.is_logical !== false;
        
        if (isLogical.value) score.value += 10;
        
        stage.value = 4;
    } catch (e) {
        console.error("Final analysis failed:", e);
        stage.value = 4;
    } finally {
        isSubmittingAnswer.value = false;
    }
};

const calculateFinalResults = async () => {
    const res = evaluationResults;
    const ts = res.stageTimestamps;
    res.timeSpent = (ts.end - ts.start) / 1000;

    try {
        // [2026-01-27] 백엔드 AI 평가 API 호출
        const response = await axios.post('/api/core/ai-evaluate/', {
            quest: currentQuest.value,
            performance: {
                timeSpent: res.timeSpent,
                penaltyCount: res.penaltyCount,
                hintsUsed: res.hintsUsed,
                perkFlags: res.perkFlags
            }
        });

        const data = response.data;
        res.logicScore = data.logicScore || 0;
        res.codingScore = data.codingScore || 0;
        res.designScore = data.designScore || 0;
        personaTitle.value = data.personaTitle || "분석 실패";
        evaluationMessageOverride.value = data.feedbackMessage || "AI가 분석한 당신의 학습 성과를 확인해보세요!";
        score.value = data.totalScore || 0;

    } catch (error) {
        console.error("AI Evaluation failed, falling back to local logic:", error);
        evaluationMessageOverride.value = "AI 위저드와 일시적으로 연결이 원활하지 않아,\n표준 결과 시스템으로 평가를 진행했습니다.";
        // 폴백 로직 (기존 로직 유지)
        res.logicScore = Math.max(0, 100 - (res.penaltyCount * 5) - (res.hintsUsed * 10));
        const stage2Duration = (ts.stage3Start - ts.stage2Start) / 1000;
        let codeBase = res.perkFlags.oneShotCoding ? 100 : 70;
        if (stage2Duration > 60) codeBase -= 10;
        res.codingScore = Math.max(0, codeBase);
        res.designScore = res.perkFlags.perfectDesign ? 100 : 0;
        const finalScore = (res.logicScore * 0.3) + (res.codingScore * 0.3) + (res.designScore * 0.4) - (res.penaltyCount * 2);
        score.value = Math.max(0, finalScore);
        personaTitle.value = "꼼꼼한 탐험가";
    }
};

const handleDuckHover = (state) => {
    if (isFalling.value) return;
    isHovering.value = state;
    if (state) {
        currentEmotion.value = 'hover';
        displayMessage("헤헤, 간지러워요!");
    } else {
        currentEmotion.value = 'idle';
    }
};

const resetGame = () => {
    stage.value = 1;
    score.value = 0;
    currentStep.value = 0;
    droppedBlocks.value = new Array(currentQuest.value.cards.length).fill(null);
    showHint.value = false;
    codeInputs.price = '';
    codeInputs.fee1 = '';
    codeInputs.fee2 = '';
    aiMetrics.value = null;
    mentorAnalysis.value = '';
    mentorAdvice.value = '';
    isLogical.value = true;
    userFreeAnswer.value = '';
    typedQuestion.value = '';
    tailQuestion.value = null;
    currentEmotion.value = 'idle';
};

onMounted(() => {
    setTimeout(() => {
      isLoading.value = false;
    }, 1000);
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Nanum+Gothic:wght@400;700;800&display=swap');

.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 2rem;
}

.font-jua { font-family: 'Jua', sans-serif; }

.block-item { 
    cursor: grab; 
    transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 6px 0 rgba(0,0,0,0.1), inset 0 -2px 5px rgba(255,255,255,0.3);
}
.block-item:active { cursor: grabbing; transform: translateY(2px); }

/* --- START 플랫폼 (3D 회색 디자인) --- */
.stair-start {
    position: absolute;
}
.platform-top {
    height: 45px;
    background: #cccccc;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: 900;
    color: #444;
    position: relative;
    z-index: 2;
}
.platform-side {
    height: 20px;
    background: #999999;
    border-radius: 0 0 20px 20px;
    margin-top: -10px;
    position: relative;
    z-index: 1;
}

/* --- 알약 형태 계단 타겟 --- */
.stair-pill {
    position: absolute;
    background: transparent;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.empty-stair-pill {
    width: 100%;
    height: 100%;
    background: white;
    border: 3px dashed #cbd5e1;
    border-radius: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.active-target .empty-stair-pill {
    border-color: #fbbf24;
    background: rgba(255, 251, 235, 0.5);
    box-shadow: 0 0 20px rgba(251, 191, 36, 0.2);
}

/* --- 배치된 블록 (이미지 참고 고도화) --- */
.placed-block-refined {
    width: 100%;
    height: 100%;
    background: white;
    border-radius: 100px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    gap: 15px;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
    position: relative;
    border-bottom: 6px solid transparent; /* 동적 색상 적용을 위해 */
    animation: bounceIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* 하단 테두리 색상 클래스 */
.placed-block-refined.border-indigo-500 { border-color: #6366f1; }
.placed-block-refined.border-emerald-500 { border-color: #22c55e; }
.placed-block-refined.border-amber-500 { border-color: #f59e0b; }

.block-text {
    font-size: 0.85rem;
    font-weight: 800;
    color: #1e293b;
    flex-grow: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 170px;
}

.remove-btn-refined {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #f1f5f9;
    color: #64748b;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    transition: all 0.2s;
    cursor: pointer;
    position: relative;
    z-index: 50;
}

.remove-btn-refined:hover {
    background: #fb7185;
    color: white;
}

@keyframes bounceIn {
    0% { transform: scale(0.8) translateY(10px); opacity: 0; }
    100% { transform: scale(1) translateY(0); opacity: 1; }
}

/* --- 디즈니 픽사 스타일 비행 애니메이션 --- */
@keyframes pixarFly {
    0% { transform: translateY(0) scale(1) rotate(0deg); }
    15% { transform: translateY(20px) scale(1.3, 0.7) rotate(-5deg); filter: brightness(1.2); } /* 웅크리기(Anticipation) */
    40% { transform: translateY(-300px) scale(0.8, 1.4) rotate(15deg); filter: contrast(1.2); } /* 급상승 */
    55% { transform: translateY(-350px) scale(1.1) rotate(-10deg); }
    70% { transform: translateY(-500px) scale(0.9) rotate(20deg); opacity: 0.8; }
    100% { transform: translateY(-1000px) rotate(360deg); opacity: 0; } /* 화면 밖으로 슝! */
}
.animate-pixar-fly { 
    animation: pixarFly 2.2s forwards cubic-bezier(0.45, 0.05, 0.55, 0.95); 
    z-index: 999;
}

.duck-frame {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: contain;
    transition: opacity 0.3s;
    filter: drop-shadow(0 10px 15px rgba(0,0,0,0.1));
}

@keyframes fall {
    0% { transform: translateY(0) rotate(0deg); }
    20% { transform: translateY(-30px) rotate(15deg); }
    100% { transform: translateY(600px) rotate(1080deg); opacity: 0; }
}
.animate-fall { animation: fall 1s forwards cubic-bezier(0.55, 0.055, 0.675, 0.19); }

@keyframes bounceSlow {
    0%, 100% { transform: translateY(-5%); animation-timing-function: cubic-bezier(0.8, 0, 1, 1); }
    50% { transform: translateY(0); animation-timing-function: cubic-bezier(0, 0, 0.2, 1); }
}
.feedback-paragraph {
    position: relative;
    padding-left: 1.5rem;
}

.feedback-paragraph::before {
    content: "•";
    position: absolute;
    left: 0;
    color: #6366f1;
    font-weight: 900;
}

.animate-bounce-slow { animation: bounceSlow 3s infinite; }

.duck-bubble {
    position: relative;
    background: white;
    border: 3px solid #fbbf24;
    border-radius: 20px;
    padding: 12px;
    box-shadow: 0 10px 15px rgba(0,0,0,0.1);
}
.duck-bubble::after {
    content: '';
    position: absolute;
    bottom: -15px;
    left: 20px;
    border-width: 15px 15px 0 0;
    border-style: solid;
    border-color: #fbbf24 transparent transparent transparent;
}

/* --- 코드 실행 버튼 고도화 디자인 --- */
.run-code-btn {
    display: block;
    width: 100%;
    margin-top: 2rem;
    background-color: #1e293b !important;
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
    color: #ffffff !important;
    font-weight: 900;
    padding: 1.5rem !important;
    border-radius: 2rem !important;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    border: none !important;
    border-bottom: 6px solid #000000 !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25) !important;
    cursor: pointer;
    z-index: 10;
}

.run-code-btn:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
    background: linear-gradient(135deg, #334155 0%, #1e293b 100%) !important;
}

.run-code-btn:active {
    transform: translateY(2px);
    border-bottom-width: 2px;
}

.btn-icon {
    background-color: #22c55e !important;
    width: 44px !important;
    height: 44px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: 50% !important;
    font-size: 1.2rem !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(34, 197, 94, 0.5) !important;
}

.btn-text {
    font-size: 1.25rem;
    letter-spacing: -0.025em;
    font-family: 'Jua', sans-serif;
}

.btn-glow {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
}

.run-code-btn:hover .btn-glow {
    opacity: 1;
}
</style>