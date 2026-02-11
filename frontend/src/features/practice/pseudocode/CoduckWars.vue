<!--
수정일: 2026-02-10
수정 내용: 이전 작업 버전(SKN20-FINAL-5TEAM_before)으로 pseudocode 프론트엔드 코드 복구
-->
<template>
  <div class="coduck-wars-container">
    <!-- BACKGROUND WATERMARK -->
    <div class="bg-watermark">CODUCK WARS</div>
    <div class="scan-line"></div>

    <!-- HEADER -->
    <header class="war-room-header">
      <div class="chapter-info">
        <span class="chapter-title">CHAPTER {{ gameState.currentStageId }}: {{ currentMission.title || '로딩 중...' }}</span>
        <span class="sub-info">{{ currentMission.subModuleTitle || 'BOOT_PROTOCOL' }}</span>
      </div>
      <div class="integrity-monitor">
        <span class="integrity-label">정화 무결성</span>
        <div class="hp-bar-bg">
             <div class="hp-bar-fill" :style="{ width: Math.max(0, gameState.playerHP) + '%' }"></div>
        </div>
        <span class="integrity-val">{{ Math.max(0, gameState.playerHP) }}%</span>
      </div>
    </header>

    <!-- MAIN VIEWPORT -->
    <main class="viewport">
        
      <!-- GUIDE FLOATING BUTTON (Toggle) -->
      <button class="btn-guide-floating" @click="toggleGuide" :class="{ 'is-open': isGuideOpen }">
          <span class="icon">?</span>
          <span class="label">CHAPTER</span>
      </button>

      <!-- GUIDE SLIDE PANEL -->
      <div class="guide-sidebar" :class="{ 'sidebar-open': isGuideOpen }">
          <div class="sidebar-header">
              <span class="sh-title">MISSION CHAPTERS</span>
              <button class="sh-close" @click="toggleGuide">×</button>
          </div>
          <div class="sidebar-content">
              <div 
                  v-for="(card, idx) in currentMission.cards" 
                  :key="idx"
                  class="guide-step-card"
                  :class="{ 'g-active': idx === selectedGuideIdx }"
                  @click="handleGuideClick(idx)"
              >
                  <div class="gs-header-row">
                      <div class="gs-icon">{{ card.icon }}</div>
                      <div class="gs-info">
                          <div class="gs-step">STEP {{ idx + 1 }}</div>
                          <div class="gs-text">{{ card.text.split(':')[1] || card.text }}</div>
                      </div>
                  </div>
                  
                  <!-- EXPANDED HINT AREA -->
                  <div class="gs-hint-content" v-if="idx === selectedGuideIdx">
                      <div class="hint-label">💡 TACTICAL ADVICE</div>
                      <p class="hint-body">"{{ card.coduckMsg }}"</p>
                  </div>
              </div>
          </div>
      </div>


      <!-- PHASE: STEP 0 (INTRO) -->
      <section v-if="gameState.phase === 'INTRO' || gameState.phase === 'DIAGNOSTIC_1' && gameState.step === 0" class="w-full h-full overflow-y-auto p-12">
          <div class="max-w-3xl mx-auto space-y-8">
                <div class="bg-slate-900/50 p-10 rounded-[2.5rem] border border-slate-800 shadow-2xl">
                    <div class="w-16 h-16 text-red-500 mb-8"><AlertOctagon class="w-full h-full" /></div>
                    <h2 class="text-3xl font-black mb-6 leading-tight">
                        Quest 01:<br/>
                        전처리 데이터 누수 방어 시스템 설계
                    </h2>
                    
                    <!-- 사고 보고서 -->
                    <div class="bg-red-500/5 border border-red-500/20 p-6 rounded-2xl mb-6">
                        <p class="text-sm text-red-400 font-bold mb-2">🚨 긴급 사고 보고</p>
                        <p class="text-slate-300 text-base leading-relaxed mb-3">
                            주니어 개발자가 작성한 전처리 코드가 Production에 배포되었습니다.
                        </p>
                        <div class="bg-slate-900/50 p-4 rounded-xl border border-slate-800 mb-3">
                            <pre class="text-emerald-400 text-xs code-line">scaler = StandardScaler()
scaler.fit(df)  # 전체 데이터로 학습
X_train = scaler.transform(df[:800])
X_test = scaler.transform(df[800:])</pre>
                        </div>
                        <p class="text-slate-400 text-sm">
                            <strong class="text-red-400">결과:</strong> 
                            Train 정확도 95% → Test 정확도 68% <span class="text-red-400 font-bold">(27%p 폭락)</span>
                        </p>
                    </div>

                    <p class="text-slate-400 text-lg leading-relaxed mb-6">
                        당신은 <strong class="text-blue-400">AI 코드 리뷰어 시스템 설계자</strong>입니다.<br/>
                        이런 전처리 누수 코드가 다시 작성되지 않도록 <strong>자동 검증 규칙</strong>을 만드세요.
                    </p>

                    <div class="flex items-start gap-4 p-5 bg-blue-500/10 rounded-2xl border border-blue-500/20 mb-8">
                        <Info class="text-blue-400 mt-1 shrink-0 w-5 h-5" />
                        <div class="text-sm text-blue-100">
                            <p class="font-bold mb-2">학습 목표</p>
                            <p class="text-blue-200 leading-relaxed">
                                코드를 직접 고치는 것이 아닌, <strong>AI가 자동으로 문제를 찾게 만드는 프롬프트</strong>를 개발합니다.
                            </p>
                        </div>
                    </div>

                    <button @click="submitDiagnostic1(0)" 
                            class="w-full md:w-auto px-10 py-5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-2xl transition-all flex items-center justify-center gap-3 shadow-xl active:scale-95">
                        개념 학습 시작하기 <ArrowRight class="w-5 h-5" />
                    </button>
                </div>
          </div>
      </section>

      <!-- PHASE: STEP 1 (CONCEPTS) -->
      <section v-if="gameState.phase.startsWith('DIAGNOSTIC') && gameState.step !== 0" class="w-full h-full overflow-y-auto p-12">
            <div class="max-w-3xl mx-auto space-y-8">
                <div class="text-center space-y-4 mb-10">
                    <span class="text-xs font-bold text-blue-500 uppercase tracking-[0.2em]">
                        Step 01: Concept Foundation
                    </span>
                    <h3 class="text-3xl font-black">전처리 누수 개념 이해</h3>
                    <p class="text-slate-400">
                        규칙을 설계하기 전, 먼저 <strong>왜 문제인지</strong> 명확히 이해해야 합니다.
                    </p>
                </div>

                <!-- 진행 상태 -->
                <div class="flex justify-center gap-3 mb-8">
                    <div v-for="s in 2" :key="s"
                         :class="['w-3 h-3 rounded-full transition-all',
                                  (gameState.phase === 'DIAGNOSTIC_2' && s===1) || gameState.phase === 'DIAGNOSTIC_2' ? 'bg-blue-500 scale-110' : 'bg-slate-700']">
                    </div>
                </div>

                <!-- 현재 문제 -->
                <div class="bg-slate-900/50 p-10 rounded-[2.5rem] border border-slate-800 space-y-8">
                    <!-- 카테고리 -->
                    <div class="inline-block px-3 py-1 bg-indigo-500/20 text-indigo-400 rounded-lg text-xs font-bold uppercase">
                        {{ gameState.phase === 'DIAGNOSTIC_1' ? "데이터 누수 정의" : "올바른 해결 방법" }}
                    </div>

                    <!-- 질문 -->
                    <div class="space-y-4">
                        <h4 class="text-2xl font-bold leading-snug">
                            {{ gameState.phase === 'DIAGNOSTIC_1' ? diagnosticQuestion1.question : diagnosticQuestion2.question }}
                        </h4>
                    </div>

                    <!-- 선택지 -->
                    <div class="space-y-4">
                        <button
                            v-for="(opt, idx) in (gameState.phase === 'DIAGNOSTIC_1' ? diagnosticQuestion1.options : diagnosticQuestion2.options)"
                            :key="idx"
                            @click="gameState.phase === 'DIAGNOSTIC_1' ? submitDiagnostic1(idx) : submitDiagnostic2(idx)"
                            class="w-full text-left p-6 rounded-2xl border-2 border-slate-800 bg-slate-900/50 hover:border-slate-700 transition-all group"
                        >
                            <div class="flex items-start gap-4">
                                <span class="w-10 h-10 rounded-xl bg-slate-800 text-slate-500 group-hover:bg-slate-700 flex items-center justify-center text-sm font-black shrink-0">
                                    {{ String.fromCharCode(65 + idx) }}
                                </span>
                                <div class="flex-1">
                                    <p class="text-base leading-relaxed text-slate-400 group-hover:text-slate-200">
                                        {{ opt.text }}
                                    </p>
                                </div>
                            </div>
                        </button>
                    </div>
                </div>
            </div>
      </section>

      <!-- PHASE: STEP 2 (RULE DESIGN) -->
      <section v-if="gameState.phase === 'PSEUDO_WRITE'" class="w-full h-full overflow-y-auto p-12">
        <div class="max-w-6xl mx-auto space-y-8">
            <div class="text-center space-y-4 mb-10">
                <span class="text-xs font-bold text-blue-500 uppercase tracking-[0.2em]">
                    Step 02: Rule Design
                </span>
                <h3 class="text-3xl font-black">AI 리뷰어 검증 규칙 설계</h3>
                <p class="text-slate-400 max-w-2xl mx-auto leading-relaxed">
                    이제 개념을 이해했으니, <strong class="text-blue-400">AI가 자동으로 전처리 누수를 찾게 만드는 규칙</strong>을 의사코드로 작성하세요.
                </p>
            </div>

            <!-- 사고 코드 복습 -->
            <div class="bg-red-500/5 border border-red-500/20 rounded-2xl overflow-hidden mb-8">
                <div class="bg-red-500/10 px-6 py-4 border-b border-red-500/20">
                    <p class="text-xs font-bold text-red-400 uppercase">막아야 할 패턴</p>
                </div>
                <div class="p-6">
                    <pre class="text-emerald-400 text-sm code-line mb-4">scaler = StandardScaler()
scaler.fit(df)  # ⚠️ 전체 데이터로 fit
X_train = scaler.transform(df[:800])
X_test = scaler.transform(df[800:])</pre>
                    <p class="text-xs text-slate-500">
                        <strong class="text-red-400">문제:</strong> fit() 실행 시점에 Train/Test 분할이 되지 않아 Test 통계량이 Train에 영향
                    </p>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
                <!-- 왼쪽: 가이드 -->
                <div class="lg:col-span-4 space-y-6">
                    <div class="p-6 bg-slate-900/80 rounded-[2rem] border border-slate-800 sticky top-28">
                        <h4 class="text-xs font-bold uppercase tracking-widest mb-6 text-blue-500 flex items-center gap-2">
                            <Lightbulb class="w-4 h-4" /> 작성 가이드
                        </h4>
                        
                        <div class="space-y-4 mb-6">
                            <div class="p-4 bg-blue-500/5 rounded-xl border border-blue-500/10">
                                <p class="text-xs text-blue-300 font-bold mb-2">의사코드 형식</p>
                                <p class="text-xs text-slate-400 leading-relaxed">
                                    IF (조건) THEN 경고 형태로 작성하세요
                                </p>
                            </div>
                        </div>

                        <!-- 체크리스트 -->
                        <div class="space-y-4">
                            <h5 class="text-[10px] font-black text-slate-500 uppercase tracking-widest">검증 항목</h5>
                            <div v-for="check in ruleChecklist" :key="check.id" class="space-y-2">
                                <div class="flex items-start gap-3">
                                    <div :class="['w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5',
                                                    check.completed ? 'bg-emerald-500' : 'bg-slate-700']">
                                        <Check class="w-3 h-3 text-white" />
                                    </div>
                                    <span :class="['text-xs font-bold',
                                                    check.completed ? 'text-emerald-400' : 'text-slate-500']">
                                        {{ check.label }}
                                    </span>
                                </div>
                                <div v-if="!check.completed" class="ml-8 text-[10px] text-slate-600 italic">
                                    {{ check.hint }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 오른쪽: 입력창 -->
                <div class="lg:col-span-8 space-y-6">
                    <div class="space-y-2">
                        <label class="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                            <Code2 class="w-4 h-4" /> 검증 규칙 (의사코드)
                        </label>
                        <p class="text-xs text-slate-600 leading-relaxed">
                            AI가 코드를 스캔할 때 사용할 규칙을 작성하세요. 
                            <strong>어떤 패턴을 찾고, 어떤 경고를 낼지</strong> 명시하세요.
                        </p>
                    </div>
                    
                    <textarea 
                        v-model="gameState.phase3Reasoning"
                        @input="handlePseudoInput"
                        placeholder="예시:

IF 코드에 'scaler.fit(' 또는 'encoder.fit(' 패턴이 있음
AND 그 이전 줄에 'train_test_split' 또는 '[: 슬라이싱]'이 없음
THEN 
    경고: '분할 전 통계량 산출 감지'
    설명: 'Test 데이터 통계량이 Train 학습에 영향을 줍니다'
    해결책: 'Train/Test 분할 후 scaler.fit(X_train)으로 변경하세요'"
                        class="w-full h-[500px] bg-slate-900 border-2 border-slate-800 rounded-[2.5rem] 
                                p-10 text-slate-200 focus:border-blue-600 outline-none transition-all 
                                resize-none leading-relaxed shadow-2xl text-sm font-mono"
                    ></textarea>
                    
                    <div class="flex items-center justify-between text-xs text-slate-600">
                        <span>{{ gameState.phase3Reasoning.length }} characters</span>
                        <span :class="allChecksPassed ? 'text-emerald-400 font-bold' : 'text-slate-500'">
                            {{ completedChecksCount }}/{{ ruleChecklist.length }} 검증 항목 완료
                        </span>
                    </div>

                    <button 
                        :disabled="!allChecksPassed"
                        @click="submitPseudo"
                        :class="['w-full py-6 rounded-3xl font-black flex justify-center items-center gap-3 text-lg transition-all',
                                    allChecksPassed
                                    ? 'bg-blue-600 text-white hover:bg-blue-500 shadow-xl active:scale-95' 
                                    : 'bg-slate-800 text-slate-600 cursor-not-allowed']"
                    >
                        <span v-if="!allChecksPassed">
                            모든 검증 항목 완료 필요 ({{ completedChecksCount }}/{{ ruleChecklist.length }})
                        </span>
                        <span v-else>
                            파이썬 코드 생성 <Play class="w-5 h-5" />
                        </span>
                    </button>
                    <!-- Progress / Feedback Message -->
                    <div v-if="gameState.feedbackMessage" class="text-center text-sm font-bold text-blue-400 mt-2">
                        {{ gameState.feedbackMessage }}
                    </div>
                </div>
            </div>
        </div>
      </section>


                <!-- 3. 모듈 (드래그 가능) -->
                <div class="modules-col">
                    <div class="panel-subheader">
                        <span class="sub-icon">📦</span>
                        <span class="sub-title">모듈 (Drag)</span>
                    </div>
                    <div class="snippet-list-scroll">
                        <div 
                            v-for="(snip, idx) in pythonSnippets" 
                            :key="idx" 
                            class="snippet-block-draggable"
                            draggable="true"
                            @dragstart="onDragStart($event, snip.code)"
                        >
                            <span class="s-icon">::</span>
                            <span class="s-label">{{ snip.label }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Bottom Action Bar -->
            <div class="action-bar-bottom">
                 <div class="error-console" v-if="gameState.feedbackMessage">
                      <span class="bad-signal">시스템 경고 >></span> {{ gameState.feedbackMessage }}
                 </div>
                 <div v-else style="flex:1"></div>

                 <div class="btn-group">
                      <button class="btn-reset-large" @click="initPhase4Scaffolding">
                          <span class="btn-text">다시 하기</span>
                      </button>
                      <button class="btn-execute-large" @click="submitPythonFill">
                          <span class="btn-text">코드 배포</span>
                          <span class="btn-icon">→</span>
                      </button>
                 </div>
            </div>
         </div>
      </section>

      <!-- PHASE: STEP 4 (DEEP DIVE / TAIL QUESTION) -->
      <section v-if="gameState.phase === 'DEEP_QUIZ' || gameState.phase === 'TAIL_QUESTION'" class="w-full h-full overflow-y-auto p-12">
        <div class="max-w-3xl mx-auto space-y-8">
            <div class="text-center space-y-4 mb-10">
                <span class="text-xs font-bold text-blue-500 uppercase tracking-[0.2em]">
                    Step 04: {{ gameState.phase === 'DEEP_QUIZ' ? 'Deep Dive' : 'Analysis' }}
                </span>
                <h3 class="text-3xl font-black">
                    {{ gameState.phase === 'DEEP_QUIZ' ? '심화 시나리오 검증' : '누락된 로직 진단' }}
                </h3>
                <p class="text-slate-400">
                    {{ gameState.phase === 'DEEP_QUIZ' ? 'AI가 생성한 엣지 케이스 시나리오에 대응해보세요.' : '작성한 코드에서 놓친 부분을 점검합니다.' }}
                </p>
            </div>

            <div class="bg-slate-900/50 p-10 rounded-[2.5rem] border border-slate-800 space-y-8 shadow-2xl">
                <!-- 질문 -->
                <div class="space-y-4">
                    <div class="inline-block px-3 py-1 bg-indigo-500/20 text-indigo-400 rounded-lg text-xs font-bold uppercase">
                        Question
                    </div>
                    <h4 class="text-xl font-bold leading-relaxed whitespace-pre-line">
                        {{ deepQuizQuestion.question }}
                    </h4>
                </div>

                <!-- 선택지 -->
                <div class="space-y-4">
                    <button
                        v-for="(opt, idx) in deepQuizQuestion.options"
                        :key="idx"
                        @click="submitDeepQuiz(idx)"
                        class="w-full text-left p-6 rounded-2xl border-2 border-slate-800 bg-slate-900/50 hover:border-slate-700 transition-all group"
                    >
                        <div class="flex items-start gap-4">
                            <span class="w-8 h-8 rounded-lg bg-slate-800 text-slate-500 group-hover:bg-slate-700 flex items-center justify-center text-sm font-black shrink-0">
                                {{ idx + 1 }}
                            </span>
                            <div class="flex-1">
                                <p class="text-sm leading-relaxed text-slate-400 group-hover:text-slate-200">
                                    {{ opt.text }}
                                </p>
                            </div>
                        </div>
                    </button>
                </div>
            </div>
        </div>
      </section>

      <!-- PHASE: EVALUATION (FINAL REPORT) -->
      <section v-if="gameState.phase === 'EVALUATION'" class="w-full h-full overflow-y-auto p-12">
        <div class="max-w-5xl mx-auto space-y-8">
            <div class="text-center space-y-4 mb-10">
                <span class="text-xs font-bold text-emerald-500 uppercase tracking-[0.2em]">
                    Final Report
                </span>
                <h3 class="text-3xl font-black">AI 아키텍트 평가 리포트</h3>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- 왼쪽: 방사형 차트 -->
                <div class="bg-slate-900/50 rounded-[2.5rem] border border-slate-800 p-8 flex flex-col items-center justify-center relative overflow-hidden">
                    <div class="absolute inset-0 bg-blue-500/5 blur-3xl rounded-full"></div>
                    
                    <div class="relative w-full aspect-square max-w-[400px]">
                        <svg viewBox="0 0 200 200" class="w-full h-full">
                            <!-- Grid -->
                            <polygon v-for="level in 5" :key="level"
                                     :points="calculatePentagonPoints(level * 20)"
                                     class="fill-none stroke-slate-800"
                                     stroke-width="1" />
                            
                            <!-- Axis -->
                            <line v-for="i in 5" :key="'line-'+i"
                                  x1="100" y1="100"
                                  :x2="calculatePoint(i-1, 100).x"
                                  :y2="calculatePoint(i-1, 100).y"
                                  class="stroke-slate-800"
                                  stroke-width="1" />

                            <!-- Data -->
                            <polygon :points="radarPoints" 
                                     class="fill-blue-500/20 stroke-blue-500"
                                     stroke-width="2" />
                                     
                            <!-- Labels -->
                             <text v-for="(metric, i) in evaluationResult.details" :key="'label-'+i"
                                   :x="calculatePoint(i, 115).x"
                                   :y="calculatePoint(i, 115).y"
                                   class="text-[8px] fill-slate-400 font-bold"
                                   text-anchor="middle"
                                   dominant-baseline="middle">
                                 {{ metric.dimension || metric.category }}
                             </text>
                        </svg>
                    </div>
                </div>

                <!-- 오른쪽: 점수 및 피드백 -->
                <div class="space-y-6">
                    <!-- 종합 점수 -->
                    <div class="bg-slate-900/80 p-8 rounded-[2rem] border border-slate-800 flex items-center justify-between">
                        <div>
                            <p class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Total Score</p>
                            <h2 class="text-5xl font-black text-white">{{ evaluationResult.finalScore || evaluationResult.totalScore }}</h2>
                        </div>
                        <div class="text-right">
                             <div :class="['px-4 py-2 rounded-xl text-lg font-bold',
                                          (evaluationResult.finalScore || evaluationResult.totalScore) >= 80 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400']">
                                {{ (evaluationResult.finalScore || evaluationResult.totalScore) >= 80 ? 'EXCELLENT' : 'NEEDS IMPROVEMENT' }}
                             </div>
                        </div>
                    </div>

                    <!-- 피드백 카드 -->
                    <div class="bg-slate-900/50 p-8 rounded-[2rem] border border-slate-800 space-y-6">
                        <div class="space-y-2">
                             <div class="flex items-center gap-2 text-blue-400 font-bold mb-2">
                                <Info class="w-4 h-4" /> AI 피드백
                             </div>
                             <p class="text-sm text-slate-300 leading-relaxed">
                                {{ evaluationResult.seniorAdvice }}
                             </p>
                        </div>
                        
                        <div v-if="evaluationResult.improvementPlan" class="space-y-2 pt-4 border-t border-slate-800">
                             <div class="flex items-center gap-2 text-amber-400 font-bold mb-2">
                                <Lightbulb class="w-4 h-4" /> 개선 가이드
                             </div>
                             <p class="text-sm text-slate-300 leading-relaxed">
                                {{ evaluationResult.improvementPlan }}
                             </p>
                        </div>
                    </div>

                    <button @click="resetFlow" class="w-full py-4 bg-slate-800 hover:bg-slate-700 rounded-2xl font-bold text-slate-300 transition-all">
                        처음으로 돌아가기
                    </button>
                </div>
            </div>
        </div>
      </section>

       <!-- PHASE: DEFEAT -->
      <section v-if="gameState.phase === 'DEFEAT'" class="panel defeat-view">
            <h1 class="glitch-text">시스템 실패</h1>
            <p>치명적인 무결성 손실</p>
            <button class="btn-retry" @click="restartMission">시스템 재부팅</button>
      </section>

       <!-- PHASE: CAMPAIGN END -->
      <section v-if="gameState.phase === 'CAMPAIGN_END'" class="panel victory-view">
            <h1 class="gold-text">모든 섹터 확보됨</h1>
            <p>최종 점수: {{ gameState.score }}</p>
      </section>

    </main>
    
    <!-- FEEDBACK TOAST -->
    <div v-if="gameState.feedbackMessage && gameState.phase !== 'PYTHON_FILL' && gameState.phase !== 'EVALUATION' && gameState.phase !== 'DEFEAT' && gameState.phase !== 'CAMPAIGN_END'" class="feedback-toast">
      <span class="toast-icon">!</span> {{ gameState.feedbackMessage }}
    </div>

  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useGameStore } from '@/stores/game';
import { useCoduckWars } from './composables/useCoduckWars.js';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import { useMonacoEditor } from './composables/useMonacoEditor.js';
import { 
  AlertOctagon, Info, ArrowRight, Lightbulb, Check, 
  Code2, Play, CheckCircle, Brain, BarChart3, RotateCcw 
} from 'lucide-vue-next';

const router = useRouter();
const gameStore = useGameStore();

// --- MOCK STATE for Debugging ---
const gameState = ref({phase: 'DIAGNOSTIC_1', systemLogs: []});
const currentMission = ref({});
const runnerState = ref({});
const evaluationResult = ref({});
const deepQuizQuestion = ref({});
const isEvaluating = ref(false);
const logicBlocks = ref([]);
const pythonSnippets = ref([]);
const activeDetail = ref(null);
const isGuideOpen = ref(false);
const isWritingGuideOpen = ref(false);
const selectedGuideIdx = ref(0);

// --- New State for Pseudocode2 UI ---
const ruleChecklist = ref([
    {
        id: 'check_fit',
        label: 'fit 메서드 호출 감지',
        patterns: [
            /\.fit\(/i,
            /fit\(/i,
            /scaler.*fit/i,
            /encoder.*fit/i
        ],
        hint: "scaler.fit( 또는 encoder.fit( 패턴 찾기",
        completed: false
    },
    {
        id: 'check_split',
        label: '분할 코드 유무 확인',
        patterns: [
            /train_test_split/i,
            /분할/i,
            /split/i,
            /\[:/i
        ],
        hint: "train_test_split 또는 슬라이싱 체크",
        completed: false
    },
    {
        id: 'check_order',
        label: 'fit 이전에 분할 여부 검증',
        patterns: [
            /이전/i,
            /before/i,
            /앞/i,
            /먼저/i
        ],
        hint: "fit 이전에 분할이 있는지 확인",
        completed: false
    },
    {
        id: 'check_warning',
        label: '경고 메시지 명시',
        patterns: [
            /경고/i,
            /warning/i,
            /알림/i,
            /THEN/i
        ],
        hint: "THEN 경고: '...' 형태로 작성",
        completed: false
    }
]);

const completedChecksCount = computed(() => 
    ruleChecklist.value.filter(c => c.completed).length
);

const allChecksPassed = computed(() => 
    completedChecksCount.value === ruleChecklist.value.length
);

// Watch for pseudocode input to update checklist
watch(() => gameState.value.phase3Reasoning, (newRules) => {
    if (!newRules) return;
    ruleChecklist.value.forEach(check => {
        check.completed = check.patterns.some(pattern => pattern.test(newRules));
    });
});

// --- MOCK FUNCTIONS ---
const toggleGuide = () => {};
const toggleWritingGuide = () => {};
const handleGuideClick = () => {};
const handleDiagnosticSubmit = () => {};
const submitPseudo = () => {};
const submitPythonFill = () => {};
const submitDeepQuiz = () => {};
const initPhase4Scaffolding = () => {};
const handlePseudoInput = () => {};
const handleEditorDrop = () => {};
const onDragStart = () => {};
const onDrop = () => {};
const handleMonacoMount = () => {};
const monacoOptions = {};
const getLogTypeClass = () => {};
const getLogLabel = () => {};
const insertCodeSnippet = () => {};
const handleTailQuestion = () => {};
const selectStage = () => {};
const explainStep = () => {};
const addLogicBlock = () => {};
const submitDiagnostic1 = () => {};
const submitDiagnostic2 = () => {};
const activeStepIndex = computed(() => 0);
const radarPoints = computed(() => "");
const currentDiagnosticQuestion = computed(() => ({}));
const commentedLogicLines = computed(() => []);
const exitToHub = () => { router.push('/'); };
const restartMission = () => {};

// --- END MOCK ---
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
@import './monaco-styles.css';

/* GLOBAL CONTAINER */
.coduck-wars-container {
  width: 100%; /* [2026-02-09] 100vw → 100%로 변경하여 스크롤바 너비 고려 */
  height: 100vh;
  background-color: #050505; /* Pitch Black */
  color: #E5E7EB;
  font-family: 'Inter', sans-serif;
  overflow: hidden; /* Prevent scroll */
  display: flex;
  flex-direction: column;
  position: relative;
}

/* [2026-02-09] 반응형 레이아웃 강제 적용 - 모든 요소가 화면 너비를 초과하지 않도록 */
.coduck-wars-container *,
.coduck-wars-container *::before,
.coduck-wars-container *::after {
  box-sizing: border-box;
  max-width: 100%;
}

/* BACKGROUND WATERMARK */
.bg-watermark {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-15deg);
    font-size: 15rem; /* Huge */
    font-weight: 900;
    color: rgba(255, 255, 255, 0.03); /* Subtle */
    white-space: nowrap;
    z-index: 0;
    pointer-events: none;
    user-select: none;
}
.scan-line {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 5px;
  background: rgba(74, 222, 128, 0.05);
  animation: scan 4s linear infinite;
  z-index: 10;
  pointer-events: none;
}
@keyframes scan {
  0% { top: -10%; }
  100% { top: 110%; }
}

/* HEADER - TERMINAL STYLE */
.war-room-header {
  height: 80px; /* Slightly taller */
  background: transparent;
  display: flex;
  justify-content: space-between;
  align-items: center; /* Center vertically */
  padding: 0 40px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  z-index: 100;
  position: relative;
}
.chapter-info { display: flex; flex-direction: column; }
.chapter-title {
    color: #4ade80; /* Neon Green */
    font-weight: 900;
    font-size: 1.4rem;
    font-style: italic;
    letter-spacing: 1px;
}
.sub-info {
    color: #6b7280;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    margin-top: 5px;
}
.integrity-monitor {
    display: flex;
    align-items: center;
    gap: 20px; /* LAYOUT GRID */
}
.viewport { flex: 1; position: relative; z-index: 50; padding: 0; display: flex; }
.combat-grid {
    display: flex;
    flex-wrap: nowrap; /* CRITICAL: Force side-by-side */
    width: 100%;
    height: 100%;
    overflow: hidden; /* Prevent scroll */
}

/* LEFT PANEL - ENTITY CARD */
.entity-card {
    /* Fixed width to preserve "Coduck" card ratio */
    flex: 0 0 450px; 
    max-width: 450px;
    height: 100%; /* Fill Text/Image Logic Height */
    background: #0a0a0a;
    border-right: 1px solid #333;
    padding: 30px; /* Fixed padding for consistent look */
    display: flex;
    flex-direction: column;
}

/* ... existing styles ... */

.hp-bar-bg {
    width: 15vw; /* Relative width */
    max-width: 250px;
    min-width: 100px;
    height: 10px;
    background: #1f2937;
    border-radius: 4px;
    overflow: hidden;
}

/* ... existing styles ... */

.snippet-panel { 
    flex: 0 0 25%; /* Replaces fixed 350px */
    min-width: 280px;
    background:#111; 
    padding:30px; 
    display:flex; 
    flex-direction:column; 
}
.entity-header {
    display: flex;
    justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    color: #fbbf24; /* Amber Warning */
    margin-bottom: 30px;
    border-bottom: 2px solid #fbbf24;
    padding-bottom: 10px;
}
.visual-frame {
    position: relative;
    border: 2px solid #333;
    flex: 1; /* Fill vertical space */
    max-height: 500px;
    background: #000;
    margin-bottom: 30px;
    overflow: hidden;
}
.coduck-portrait { width: 100%; height: 100%; object-fit: cover; filter: grayscale(100%) sepia(20%) hue-rotate(50deg) saturate(300%) contrast(1.2); opacity: 0.9; }
.scan-overlay {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.2),
        rgba(0, 0, 0, 0.2) 2px,
        transparent 2px,
        transparent 4px
    );
    pointer-events: none;
}
.disconnect-tag {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #ef4444; /* Red */
    color: #000;
    font-weight: 900;
    padding: 10px;
    text-align: center;
    font-size: 1rem;
    letter-spacing: 2px;
}
.dialogue-box {
    background: #111;
    border: 1px solid #333;
    padding: 25px;
    border-left: 4px solid #3b82f6; /* Blue Accent */
}
.speaker { color: #3b82f6; font-size: 0.9rem; font-weight: bold; display: block; margin-bottom: 10px; text-transform: uppercase; }
.dialogue-text { color: #e5e7eb; font-style: italic; line-height: 1.6; font-size: 1.1rem; }


/* RIGHT PANEL - DECISION ENGINE */
.decision-panel {
    flex: 1;
    min-width: 0; /* CRITICAL: Allow shrinking */
    padding: 4vw 6vw; /* Responsive padding (was 60px 100px) */
    display: flex;
    flex-direction: column;
    justify-content: center; /* Center Vertically */
    background: rgba(10, 10, 10, 0.3); /* Slight tint */
    overflow-y: auto;
}
.system-status-text {
    color: #6b7280;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem;
    margin-bottom: 30px;
    letter-spacing: 1px;
}
.big-question {
    font-size: 3.5rem; /* Massive Font */
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1.2;
    color: #fff;
    margin-bottom: 60px;
    text-shadow: 0 0 50px rgba(0,0,0,0.8); /* Shadow for readability */
}

/* Stretched Options to Fill Space */
.options-list { 
    display: flex; 
    flex-direction: column; 
    gap: 30px; /* Big Gap */
    width: 100%; 
}

.option-card {
    background: rgba(20, 20, 20, 0.6);
    border: 1px solid rgba(255,255,255,0.1);
    display: flex;
    align-items: stretch;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    height: 140px; /* Taller Cards */
    text-align: left;
    padding: 0;
    position: relative;
    z-index: 60;
    pointer-events: auto;
    overflow: hidden;
}
.option-card:hover {
    background: rgba(74, 222, 128, 0.05);
    border-color: #4ade80;
    transform: translateX(10px); /* Slide effect */
}
.opt-index {
    width: 100px;
    background: #1f2937; /* Default Dark Grey */
    color: #9ca3af;
    font-weight: 900;
    font-size: 2.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s, color 0.2s;
}
.option-card:hover .opt-index {
    background: #4ade80; /* Neon Green on Hover */
    color: #000;
}
/* --- GUIDE FLOATING BUTTON & SIDEBAR --- */
.btn-guide-floating {
    position: fixed;
    left: 0;
    top: 20%;
    z-index: 2000;
    background: #000;
    border: 1px solid #333;
    border-left: none;
    border-radius: 0 8px 8px 0;
    padding: 15px 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    box-shadow: 4px 0 15px rgba(0,0,0,0.5);
    transition: all 0.3s;
}
.btn-guide-floating:hover {
    background: #111;
    border-color: #4ade80;
    transform: translateX(5px);
}
.btn-guide-floating .icon {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #222;
    color: #4ade80;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.1rem;
    border: 1px solid #333;
}
.btn-guide-floating .label {
    writing-mode: vertical-rl;
    text-orientation: mixed;
    color: #fff;
    font-weight: 900;
    font-size: 0.8rem;
    letter-spacing: 2px;
}
.btn-guide-floating.is-open {
    transform: translateX(320px); /* Move button with sidebar */
    border-color: #4ade80;
    background: #000;
}

.guide-sidebar {
    position: fixed;
    top: 0;
    left: -320px; /* Hidden */
    width: 320px;
    height: 100%;
    background: rgba(10, 10, 10, 0.95);
    backdrop-filter: blur(10px);
    border-right: 1px solid #333;
    z-index: 1999;
    padding: 30px 20px;
    transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1);
    display: flex;
    flex-direction: column;
    box-shadow: 10px 0 30px rgba(0,0,0,0.8);
}
.guide-sidebar.sidebar-open {
    transform: translateX(320px); /* Slide in */
}

.sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    border-bottom: 1px solid #333;
    padding-bottom: 15px;
}
.sh-title {
    font-size: 1.2rem;
    font-weight: 900;
    color: #4ade80;
    letter-spacing: 2px;
}
.sh-close {
    background: none;
    border: none;
    color: #666;
    font-size: 1.5rem;
    cursor: pointer;
}
.sh-close:hover { color: #fff; }

.sidebar-content {
    display: flex;
    flex-direction: column;
    gap: 15px;
    overflow-y: auto;
}

.guide-step-card {
    background: #18181b;
    border: 1px solid #27272a;
    border-radius: 8px;
    padding: 15px;
    display: flex;
    gap: 15px;
    cursor: pointer;
    transition: all 0.2s;
    align-items: flex-start; /* Align top */
    flex-direction: column; /* Changed to column for expansion */
    gap: 0;
}
.gs-header-row {
    display: flex;
    gap: 15px;
    align-items: center;
    width: 100%;
}
.guide-step-card:hover {
    background: #27272a;
    border-color: #52525b;
}
.guide-step-card.g-active {
    background: rgba(74, 222, 128, 0.05);
    border-color: #4ade80;
}
.gs-icon {
    font-size: 1.5rem;
    background: #222;
    width: 40px;
    height: 40px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.gs-info {
    display: flex;
    flex-direction: column;
    gap: 5px;
}
.gs-step {
    font-size: 0.75rem;
    color: #4ade80;
    font-weight: 900;
    letter-spacing: 1px;
}
.gs-text {
    font-size: 0.9rem;
    color: #d4d4d4;
    line-height: 1.4;
}
/* Expanded Hint Styles */
.gs-hint-content {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px dashed #333;
    width: 100%;
    animation: fadeIn 0.3s ease;
}
.hint-label {
    font-size: 0.7rem;
    color: #4ade80;
    font-weight: 900;
    margin-bottom: 5px;
    display: block;
}
.hint-body {
    font-size: 0.9rem;
    color: #a1a1aa;
    line-height: 1.6;
    font-style: italic;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-5px); }
    to { opacity: 1; transform: translateY(0); }
}

.opt-content {
    flex: 1;
    padding: 0 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.opt-main { font-size: 1.6rem; font-weight: 800; color: #fff; margin-bottom: 10px; letter-spacing: -0.5px; }
.opt-desc { color: #9ca3af; font-size: 1rem; font-family: 'JetBrains Mono', monospace; }
.opt-arrow {
    width: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    color: #4ade80;
    opacity: 0;
    transition: opacity 0.2s, transform 0.2s;
    transform: translateX(-20px);
}
.option-card:hover .opt-arrow { opacity: 1; transform: translateX(0); }

.terminal-footer { margin-top: auto; font-family: 'JetBrains Mono', monospace; color: #4b5563; font-size: 0.9rem; padding-top: 40px; }

/* SYSTEM LOG STYLES */
.tactical-console {
    margin-top: auto;
    background: rgba(0,0,0,0.4);
    border-top: 1px solid rgba(255,255,255,0.1);
    padding: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    height: 150px; /* Fixed height for scrolling */
    display: flex;
    flex-direction: column;
}
.console-header { color: #4b5563; font-size: 0.8rem; margin-bottom: 10px; font-weight: bold; }
.console-body { 
    flex: 1; 
    overflow-y: auto; 
    display: flex; 
    flex-direction: column; 
    justify-content: flex-end; /* Keep bottom */
}
.log-line { margin-bottom: 5px; color: #aaa; }
.active-line { color: #fff; text-shadow: 0 0 5px rgba(255,255,255,0.5); }
.t-time { color: #555; margin-right: 10px; }
.t-info { color: #3b82f6; font-weight: bold; }
.t-warn { color: #fbbf24; font-weight: bold; }
.t-error { color: #ef4444; font-weight: bold; }
.t-success { color: #4ade80; font-weight: bold; }
.t-ready { color: #4ade80; font-weight: bold; animation: pulse 2s infinite; }
.cursor-blink { animation: blink 1s step-end infinite; color: #4ade80; margin-left: 5px; }

@keyframes blink { 50% { opacity: 0; } }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

/* FADE TRANSITION FOR LOGS */
.log-fade-enter-active,
.log-fade-leave-active {
  transition: all 0.3s ease;
}
.log-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.log-fade-leave-to {
  opacity: 0;
}


/* PHASE 3 REVISED CSS */
.mission-problem-box {
    margin-top: 20px;
    background: #111;
    border: 1px solid #333;
    border-left: 4px solid #4ade80;
    padding: 20px;
}
.mp-title { color: #6b7280; font-size: 0.8rem; font-weight: bold; margin-bottom: 15px; letter-spacing: 1px; }
.selected-strat-tag { 
    color: #4ade80; 
    font-weight: 900; 
    font-size: 1.4rem; /* Larger font for visibility */
    margin-bottom: 15px; 
    line-height: 1.3;
    border-bottom: 1px solid #333;
    padding-bottom: 15px;
}
.mp-desc { color: #d1d5db; font-size: 1rem; line-height: 1.6; }

/* HINT BUBBLE */
.coduck-speech-bubble {
    margin-top: 15px;
    background: #050505; /* Dark background */
    border: 2px solid #4ade80; /* Neon Green Border */
    color: #fff; /* High contrast text */
    padding: 20px;
    border-radius: 8px;
    position: relative;
    font-weight: bold;
    animation: fadeIn 0.5s;
    box-shadow: 0 0 15px rgba(74, 222, 128, 0.15); /* Green Glow */
}
.coduck-speech-bubble::before {
    content: '';
    position: absolute;
    top: -12px;
    left: 40px;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-bottom: 10px solid #4ade80;
}
.coduck-speech-bubble::after {
    content: '';
    position: absolute;
    top: -9px;
    left: 40px;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-bottom: 10px solid #050505;
}
.hint-content { display: flex; align-items: flex-start; gap: 10px; }
.h-icon { font-size: 1.5rem; }
.h-text { font-size: 1rem; line-height: 1.4; }
.h-highlight { color: #4ade80; font-weight: 900; } /* Text Highlight instead of background */

/* MONACO STYLE EDITOR WRAPPER */
.monaco-wrapper {
    flex: 1;
    background: #1e1e1e; /* VS Code Logic Background */
    border: 1px solid #333;
    display: flex;
    position: relative;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    overflow: hidden;
    margin-bottom: 20px;
}
.line-numbers {
    width: 50px; /* Slightly wider */
    background: #1e1e1e;
    border-right: 1px solid #333;
    color: #858585;
    text-align: right;
    padding: 20px 10px;
    font-size: 14px;
    line-height: 1.5;
    user-select: none;
    display: flex; /* Flex column for vertical numbers */
    flex-direction: column;
}
.monaco-textarea {
    flex: 1;
    background: transparent;
    border: none;
    color: #d4d4d4;
    padding: 20px;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.5;
    resize: none;
    outline: none;
    white-space: pre;
}

.editor-action-bar {
    display: flex;
    justify-content: space-between; /* Changed to space-between to align notice left, button right */
    align-items: center;
    padding-top: 10px;
}

.btn-execute-large {
    background: #4ade80; /* Neon Green */
    color: #000;
    font-weight: 900;
    padding: 10px 30px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all 0.2s;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.btn-execute-large:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(74, 222, 128, 0.5);
    background: #22c55e;
}


/* PHASE 4, 5, etc preserved */
/* PHASE 4, 5, etc preserved */
.code-panel { flex:2; background:#000; display:flex; flex-direction:column; padding:30px; border-right:1px solid #333; }
.code-editor-monaco-style { 
    flex:1; 
    background:#1E1E1E; /* Distinct VS Code Dark */
    color:#d4d4d4; 
    border:none; 
    border-top: 2px solid #3776AB; /* Python Blue Accent */
    padding:20px; 
    font-family:'JetBrains Mono'; 
    font-size:14px; 
    resize:none; 
    outline:none; 
    z-index:60; 
    position:relative; 
    box-shadow: inset 0 0 20px rgba(0,0,0,0.5); /* Inner Depth */
}
.error-console { background:#300; color:#f88; padding:10px; font-family:'JetBrains Mono'; margin-top:10px; }
.snippet-panel { width:350px; background:#111; padding:30px; display:flex; flex-direction:column; }
.snippet-list { flex:1; display:flex; flex-direction:column; gap:10px; overflow-y:auto; margin-bottom:20px; }
.snippet-btn { background:#222; border:1px solid #333; color:#eee; padding:15px; text-align:left; cursor:pointer; display:flex; align-items:center; gap:10px; z-index:60; position:relative; }
.snippet-btn:hover { border-color:#4ade80; color:#4ade80; }
/* Button Group Spacing */
.btn-group { 
    display: flex; 
    gap: 15px; 
    align-items: center; 
    z-index: 500; 
    position: relative;
}

.action-bar-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 15px;
    border-top: 1px solid #333;
    margin-top: auto;
}

.btn-reset-large {
    background: transparent;
    color: #ef4444; /* Red Text */
    font-weight: 900;
    padding: 10px 30px;
    border: 2px solid #ef4444; /* Red Border */
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all 0.2s;
    text-transform: uppercase;
    letter-spacing: 1px;
    height: 44px; /* Fixed Height matching execute */
}

.btn-reset-large:hover {
    background: rgba(239, 68, 68, 0.1);
    box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
    transform: translateY(-2px);
}

/* PHASE 5 & RESULT */
.centered-layout { justify-content:center; align-items:center; height:100%; width: 100%; position: relative; z-index: 100; pointer-events: auto; }
.center-panel { width:100%; max-width:1000px; text-align:center; position: relative; z-index: 110; } /* Wider */
.big-question-center { font-size:3rem; font-weight:900; margin-bottom:60px; color:#fff; }
.gold-hover { cursor: pointer !important; pointer-events: auto !important; }
.gold-hover:hover { background:rgba(251, 191, 36, 0.15) !important; border-color:#fbbf24 !important; }
.gold-idx { background:#fbbf24; color: black; }
.phase-header-gold { color:#fbbf24; font-weight:900; font-size:1.4rem; margin-bottom:40px; text-align:center; display:block;}
.options-wide { gap: 20px; display:flex; flex-direction:column; width: 100%; } /* Ensure gap */


.evaluation-view { 
    display: flex; 
    justify-content: center; 
    align-items: center; 
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    background: rgba(0,0,0,0.85); 
    z-index: 80; 
    backdrop-filter: blur(10px);
    overflow-y: auto; /* Enable vertical scrolling */
}
.report-card { 
    width: 650px; 
    background: #080808; 
    border: 1px solid #333; 
    border-radius: 12px;
    padding: 40px; 
    text-align: center; 
    box-shadow: 0 0 50px rgba(0,0,0,0.8);
    position: relative;
    overflow: hidden;
}
/* Report Header */
.report-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    position: relative;
}
.report-title {
    font-family: 'Inter', sans-serif;
    font-weight: 900;
    font-size: 2rem;
    letter-spacing: 2px;
    color: #fff;
    text-transform: uppercase;
    background: linear-gradient(90deg, #4ade80, #22c55e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stamp-box {
    border: 3px solid;
    padding: 5px 15px;
    font-weight: 900;
    font-size: 1rem;
    text-transform: uppercase;
    transform: rotate(-10deg);
    opacity: 0.8;
}
.stamp-success { color: #4ade80; border-color: #4ade80; box-shadow: 0 0 10px #4ade80; }
.stamp-fail { color: #ef4444; border-color: #ef4444; box-shadow: 0 0 10px #ef4444; }

.report-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #666;
    display: flex;
    flex-direction: column;
    gap: 5px;
    margin-bottom: 30px;
    border-bottom: 1px solid #222;
    padding-bottom: 20px;
}

/* Score Circle */
.score-section { margin-bottom: 40px; }
.score-circle {
    width: 120px;
    height: 120px;
    margin: 0 auto 15px;
    position: relative;
}
.circular-chart { display: block; margin: 0 auto; max-width: 100%; max-height: 100%; }
.circle-bg { fill: none; stroke: #222; stroke-width: 2.5; }
.circle { fill: none; stroke-width: 2.5; stroke-linecap: round; animation: progress 1s ease-out forwards; stroke: #4ade80; }
.percentage { fill: #fff; font-family: 'Inter', sans-serif; font-weight: 900; font-size: 0.8em; text-anchor: middle; dominant-baseline: middle; }
.score-label { font-weight: bold; color: #4ade80; font-size: 1.1rem; }

/* Philosophy Banner */
.philosophy-banner {
    background: linear-gradient(90deg, #111 0%, #0a1f12 50%, #111 100%);
    border: 1px solid rgba(74, 222, 128, 0.3);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 30px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
}
.p-badge { background: #4ade80; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: 900; font-size: 0.75rem; }
.p-text { color: #4ade80; font-weight: bold; font-size: 0.9rem; letter-spacing: 0.5px; }

/* Metrics Grid */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 15px;
    margin-bottom: 30px;
}
.metric-card {
    background: #111;
    border: 1px solid #333;
    padding: 15px 10px;
    border-radius: 8px;
    text-align: center;
    transition: all 0.3s;
}
.metric-card:hover { border-color: #4ade80; transform: translateY(-3px); }
.m-label { display: block; font-size: 0.75rem; color: #888; margin-bottom: 8px; }
.m-value { display: block; font-family: 'JetBrains Mono'; font-size: 1.4rem; font-weight: 900; color: #4ade80; }
/* Radar Chart Styles */
.radar-chart-section {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 40px;
    background: #0d1117;
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 40px;
    border: 1px solid #30363d;
}
.chart-container { width: 220px; height: 220px; }
.radar-svg { width: 100%; height: 100%; overflow: visible; }
.radar-grid { fill: none; stroke: #30363d; stroke-width: 1; }
.radar-axis { stroke: #30363d; stroke-width: 1; stroke-dasharray: 2,2; }
.radar-label-text { fill: #8b949e; font-size: 10px; text-anchor: middle; font-weight: bold; }
.radar-data-poly { fill: rgba(74, 222, 128, 0.2); stroke: #4ade80; stroke-width: 2; filter: drop-shadow(0 0 5px rgba(74, 222, 128, 0.4)); }
.score-summary { display: flex; flex-direction: column; align-items: flex-start; }
.score-main { font-size: 4.5rem; font-weight: 900; color: #4ade80; line-height: 1; font-family: 'JetBrains Mono'; }
.score-tier { font-size: 1rem; color: #8b949e; margin-top: 8px; border-left: 3px solid #4ade80; padding-left: 10px; }

/* YouTube Study Cards */
.youtube-card {
    display: flex !important;
    gap: 15px;
    text-decoration: none;
    transition: all 0.3s;
    border: 1px solid #30363d !important;
    background: #161b22 !important;
    padding: 15px;
    border-radius: 8px;
}
.youtube-card:hover { 
    transform: scale(1.02); 
    border-color: #ff0000 !important; 
    box-shadow: 0 0 15px rgba(255, 0, 0, 0.1);
}
.yt-thumb {
    width: 110px;
    height: 70px;
    background: #000;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    position: relative;
}
.yt-play { color: #ff0000; font-size: 1.8rem; }
.yt-search-tag { 
    font-size: 0.75rem; 
    color: #ff0000; 
    margin-top: 8px; 
    font-family: 'JetBrains Mono';
    font-weight: bold;
}
.s-card-title { color: #f0f6fc; font-weight: bold; margin-bottom: 5px; }
.s-card-desc { color: #8b949e; font-size: 0.85rem; line-height: 1.4; }


/* Metrics Grid */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 15px;
    margin-bottom: 30px;
}
.metric-card {
    background: #111;
    border: 1px solid #333;
    padding: 15px 10px;
    border-radius: 8px;
    text-align: center;
    transition: all 0.3s;
    cursor: pointer;
    position: relative;
}
.metric-card:hover { border-color: #4ade80; transform: translateY(-3px); }
.metric-card.card-active { border-color: #4ade80; background: #0a1f12; }
.m-label { display: block; font-size: 0.75rem; color: #888; margin-bottom: 8px; }
.m-value { display: block; font-family: 'JetBrains Mono'; font-size: 1.4rem; font-weight: 900; color: #4ade80; }
.m-arrow { font-size: 0.6rem; color: #4ade80; margin-top: 5px; opacity: 0.6; }

/* Metric Detail Box */
.metric-detail-box {
    background: #0a1f12;
    border: 1px solid #4ade80;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 30px;
    text-align: left;
    animation: slideDown 0.3s ease-out;
}
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.detail-row { margin-bottom: 15px; }
.detail-label { display: block; font-size: 0.7rem; color: #4ade80; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; font-weight: bold; }
.detail-text { color: #c9d1d9; font-size: 0.95rem; line-height: 1.5; margin: 0; }
.detail-list { list-style: none; padding: 0; margin: 0; }
.detail-list li { color: #888; font-size: 0.9rem; margin-bottom: 4px; }

/* Tail Question Area */
.tail-question-area {
    margin-top: 30px;
    background: #0d1117;
    border: 1px solid #3b82f6;
    border-radius: 12px;
    padding: 25px;
    text-align: left;
    margin-bottom: 30px;
}
.tq-header { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
.tq-icon { font-size: 1.5rem; }
.tq-title { color: #60a5fa; font-weight: bold; font-size: 1.1rem; }
.tq-content { font-size: 1rem; color: #c9d1d9; line-height: 1.6; margin-bottom: 25px; border-left: 3px solid #3b82f6; padding-left: 15px; }
.tq-options { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.btn-tq-option {
    background: #161b22;
    border: 1px solid #30363d;
    color: #c9d1d9;
    padding: 15px;
    border-radius: 8px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
}
.btn-tq-option:hover { border-color: #3b82f6; background: #1c2128; }

@keyframes progress { 0% { stroke-dasharray: 0 100; } }

/* Accordion */
.evaluation-areas { text-align: left; margin-bottom: 30px; }
.area-header { color: #888; font-size: 0.85rem; letter-spacing: 2px; margin-bottom: 10px; font-weight: bold; text-align: center; }
.area-list { display: flex; flex-direction: column; gap: 10px; }
.area-item {
    background: #111;
    border: 1px solid #333;
    border-radius: 6px;
    overflow: hidden;
    transition: all 0.3s;
    cursor: pointer;
}
.area-item:hover { border-color: #4ade80; }
.area-expanded { border-color: #4ade80; background: #1a1a1a; }

.area-summary {
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.area-name { font-weight: bold; font-size: 1rem; color: #ddd; }
.area-score { font-family: 'JetBrains Mono'; color: #4ade80; font-weight: bold; }
.area-arrow { font-size: 0.8rem; color: #555; transition: transform 0.3s; }
.area-expanded .area-arrow { transform: rotate(180deg); }

.area-detail-content {
    background: #0f1510; /* Very dark green hint */
    border-top: 1px solid #333;
    padding: 20px;
    font-size: 0.9rem;
    animation: slideDown 0.3s ease-out;
}
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

.detail-row { margin-bottom: 15px; }
.detail-row:last-child { margin-bottom: 0; }
.detail-label { display: block; font-size: 0.75rem; color: #4ade80; margin-bottom: 5px; font-weight: bold; letter-spacing: 1px; }
.detail-text { color: #ccc; line-height: 1.5; }
.detail-list { list-style: none; padding: 0; margin: 0; color: #aaa; }

/* Analysis Box */
.analysis-box {
    background: rgba(74, 222, 128, 0.05);
    border: 1px solid rgba(74, 222, 128, 0.2);
    border-radius: 8px;
    padding: 20px;
    display: flex;
    align-items: flex-start;
    gap: 15px;
    text-align: left;
    margin-bottom: 25px;
}
.coduck-avatar-small img { width: 50px; height: 50px; border-radius: 50%; border: 2px solid #4ade80; object-fit: cover; }
.analysis-text-wrapper { flex: 1; }
.ai-comment { font-style: italic; color: #fff; margin-bottom: 8px; font-size: 0.95rem; }
.senior-tip { font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #4ade80; }

.btn-next-report {
    width: 100%;
    padding: 18px;
    font-weight: 900;
    background: #4ade80;
    color: #000;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: transform 0.2s, box-shadow 0.2s;
}
.btn-next-report:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(74, 222, 128, 0.4);
}

/* FEEDBACK */
.feedback-toast {
    position: fixed;
    bottom: 40px;
    left: 50%;
    transform: translateX(-50%);
    background: #000;
    color: #4ade80;
    border: 2px solid #4ade80;
    padding: 15px 40px;
    font-weight: 900;
    z-index: 200;
    box-shadow: 0 0 20px rgba(74, 222, 128, 0.2);
}

/* --- PYTHON FILL REVISED STYLES --- */
.implementation-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: rgba(10, 10, 10, 0.5);
    padding: 30px;
    overflow: hidden;
}
.split-view {
    flex: 1;
    display: flex;
    gap: 15px;
    overflow: hidden;
    margin-bottom: 20px;
    margin-top: 10px;
}

/* Logic Viewer (Left Col) */
/* Logic Viewer (Left Col - 40%) */
.logic-viewer {
    flex: 4;
    width: auto; /* Remove fixed width */
    background: #0d0d0d;
    border: 1px solid #333;
    display: flex;
    flex-direction: column;
}
.viewer-header {
    background: #222;
    color: #999;
    font-size: 0.75rem;
    font-weight: bold;
    padding: 8px 12px;
    letter-spacing: 1px;
}
.commented-content {
    flex: 1;
    padding: 15px;
    overflow-y: auto;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.85rem;
    line-height: 1.5;
    color: #6a9955; /* Comment Green */
    white-space: pre-wrap;
}

/* Code Editor (Middle Col - 60%) */
/* Code Editor (Middle Col - Flexible) */
/* Code Editor (Middle Col - Flexible) */
.code-editor-area {
    flex: 6; /* Ratio 4:6 with logic-viewer */
    min-width: 0; /* Prevent overflow */
    background: #1e1e1e;
    border: 1px solid #444;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow-x: hidden; /* Prevent horizontal scrolling logic */
}

/* Modules Sidebar (Right Col - Fixed Width -> Fluid) */
.modules-sidebar {
    flex: 0 0 20%; /* Replaces fixed 280px */
    min-width: 200px;
    max-width: 300px;
    flex-shrink: 0;
    background: #0a0a0a;
    border: 1px solid #333;
    display: flex;
    flex-direction: column;
    padding: 10px;
}
.phase-header-green-small {
    color: #4ade80;
    font-weight: 900;
    font-size: 1rem;
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1px solid #333;
}
.snippet-list-scroll {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.snippet-block {
    background: #1f1f1f;
    color: #cecece;
    padding: 12px;
    border-radius: 4px;
    cursor: grab;
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    border: 1px solid #333;
    transition: all 0.2s;
}
.snippet-block:hover {
    border-color: #4ade80;
    background: #2a2a2a;
    transform: translateX(-2px);
}
.snippet-block:active {
    cursor: grabbing;
}
.s-icon { color: #555; font-weight: bold; }

/* Bottom Action Bar */
.action-bar-bottom {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.btn-group { display: flex; gap: 10px; }

/* DEFEAT & VICTORY SCREENS */
.defeat-view, .victory-view {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0, 0, 0, 0.95);
    z-index: 200;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    backdrop-filter: blur(5px);
}

.glitch-text {
    font-size: 5rem;
    font-weight: 900;
    color: #ef4444;
    text-transform: uppercase;
    letter-spacing: 8px;
    margin-bottom: 20px;
    text-shadow: 2px 2px 0px #000;
    animation: glitch-anim 0.3s infinite;
}

.btn-retry {
    margin-top: 40px;
    background: transparent;
    border: 2px solid #ef4444;
    color: #ef4444;
    padding: 15px 50px;
    font-size: 1.2rem;
    font-weight: 900;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 2px;
    transition: all 0.2s;
}
.btn-retry:hover {
    background: #ef4444;
    color: #000;
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
}

.gold-text {
    font-size: 4rem;
    font-weight: 900;
    color: #fbbf24;
    text-shadow: 0 0 20px rgba(251, 191, 36, 0.5);
    margin-bottom: 20px;
}

@keyframes glitch-anim {
    0% { transform: translate(0); text-shadow: 2px 2px 0px #000; }
    25% { transform: translate(-2px, 2px); text-shadow: -2px -2px 0px #000; }
    50% { transform: translate(2px, -2px); text-shadow: 2px -2px 0px #000; }
    75% { transform: translate(-2px, -2px); text-shadow: -2px 2px 0px #000; }
    100% { transform: translate(0); text-shadow: 2px 2px 0px #000; }
}

/* NEW DROP ZONE STYLES */
.code-editor-area {
    padding: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    overflow-y: auto;
    gap: 15px; /* Spacing between blocks */
}
.code-header, .code-footer {
    color: #569cd6; /* Python Blue Keyword */
    font-weight: bold;
}
.code-block {
    display: flex;
    flex-direction: column;
    gap: 5px;
}
.comment-line {
    color: #6a9955;
    font-size: 0.9rem;
    margin-bottom: 2px;
}
.drop-zone {
    background: #252526;
    border: 1px dashed #555;
    padding: 12px;
    color: #888;
    cursor: default;
    transition: all 0.2s;
    border-radius: 4px;
    text-align: center;
    min-height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.drop-zone:hover {
    border-color: #4ade80;
    background: rgba(74, 222, 128, 0.05);
    color: #4ade80;
}
.drop-zone.filled {
    border: 1px solid #3776AB; /* Python Blue */
    background: #0d1117;
    color: #fff;
    font-weight: bold;
    justify-content: flex-start; /* Align text left */
    padding-left: 15px;
}

/* Added for Row Layout */
.code-row {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
}
.var-name {
    color: #9cdcfe; /* Light Blue Variable Color */
    font-weight: bold;
    min-width: 60px;
    text-align: right;
}
.code-row .drop-zone {
    flex: 1; /* Take remaining space */
}


/* LLM SUPPLEMENT SECTION */
.supplement-section {
    margin-top: 24px;
    padding: 16px;
    background: rgba(59, 130, 246, 0.05);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 12px;
}
.s-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
}
.s-title {
    font-weight: bold;
    color: #60a5fa;
    font-size: 0.9rem;
    text-transform: uppercase;
}
.s-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}
.s-card {
    background: rgba(0, 0, 0, 0.3);
    padding: 12px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.s-card-title {
    font-weight: bold;
    font-size: 0.85rem;
    color: #fbbf24;
    margin-bottom: 4px;
}
.s-card-desc {
    font-size: 0.75rem;
    color: #9ca3af;
    line-height: 1.4;
}

/* MISSION BRIEFING BOX STYLES */
.full-width-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.top-briefing-zone {
    background: rgba(15, 23, 42, 0.6);
    border-bottom: 1px solid rgba(59, 130, 246, 0.2);
    padding: 15px 20px;
}

.briefing-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.05);
    margin: 12px 0;
}

.incident-text {
    font-size: 1.15rem; /* Slightly larger */
    color: #cbd5e1; /* Changed from reddish to soft light grey/blue */
    font-weight: 500;
    line-height: 1.6;
}

.briefing-sub {
    font-size: 0.95rem; /* Scaled up */
    color: #94a3b8;
    margin-bottom: 12px;
}

.briefing-section {
    margin-bottom: 0;
}

.briefing-label {
    font-size: 0.95rem; /* Scaled up */
    font-weight: bold;
    color: #4ade80; /* Text Emerald */
    margin-bottom: 10px;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.b-icon {
    font-size: 1.25rem;
}

.briefing-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.briefing-list li {
    font-size: 1.1rem; /* Scaled up */
    color: #cbd5e1;
    margin-bottom: 8px;
    padding-left: 22px;
    position: relative;
    line-height: 1.6;
}

.briefing-list li::before {
    content: '▪';
    position: absolute;
    left: 0;
    color: #3b82f6;
}

.badge-natural {
    background: #ef4444;
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: bold;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}

.writing-notice {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-right: auto;
}

/* WRITING GUIDE BUTTON & PANEL */
.header-controls {
    display: flex;
    align-items: center;
    gap: 10px;
}
.btn-writing-guide {
    background: #27272a;
    border: 1px solid #4ade80;
    color: #4ade80;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 5px;
    transition: all 0.2s;
}
.btn-writing-guide:hover {
    background: #4ade80;
    color: #000;
}

.writing-guide-overlay {
    position: absolute;
    top: 50px;
    right: 20px;
    width: 300px;
    background: #18181b;
    border: 1px solid #3f3f46;
    border-radius: 8px;
    padding: 15px;
    z-index: 100;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    animation: fadeIn 0.2s ease-out;
}
.wg-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    border-bottom: 1px solid #27272a;
    padding-bottom: 10px;
}
.wg-title { font-weight: bold; color: #fff; }
.wg-close { background: none; border: none; color: #71717a; cursor: pointer; font-size: 1.2rem; }
.wg-close:hover { color: #fff; }

.wg-section { margin-bottom: 15px; }
.wg-label { font-size: 0.8rem; color: #4ade80; font-weight: bold; margin-bottom: 5px; }
.wg-list { padding-left: 20px; font-size: 0.85rem; color: #d4d4d8; line-height: 1.5; }
.wg-list li { margin-bottom: 5px; }
.wg-example {
    background: #111;
    border: 1px dashed #3f3f46;
    padding: 10px;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #a1a1aa;
    line-height: 1.5;
    font-style: italic;
}

</style>
