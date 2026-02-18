<!--
?섏젙?? 2026-02-14
?섏젙 ?댁슜: 5? 吏???됯? ?쒖뒪???꾩쟾 ?듯빀 諛??꾨━誘몄뾼 由ы룷??UI ?곸슜
-->
<template>
  <div class="coduck-wars-container">
    <!-- BACKGROUND WATERMARK -->
    <div class="bg-watermark">CODUCK WARS</div>
    <div class="scan-line"></div>

    <!-- HEADER -->
    <header class="war-room-header">
      <div class="chapter-info">
        <span class="chapter-title">CHAPTER {{ gameState.currentStageId }}: {{ currentMission.title || '濡쒕뵫 以?..' }}</span>
        <span class="sub-info">{{ currentMission.subModuleTitle || 'LEAKAGE_GUARD' }}</span>
      </div>
      <!-- [2026-02-14 ?섏젙] ??좊━??踰꾪듉 諛??ㅼ뒿 醫낅즺 踰꾪듉 遺꾨━ -->
      <div class="header-actions">
        <!-- [2026-02-14] ?뚰듃蹂닿린 踰꾪듉 ?ㅻ뜑 - ?먯뿰???쒖닠 ?④퀎?먯꽌留??몄텧 (遺꾩꽍 ????? -->
        <button v-if="isNaturalLanguagePhase" class="btn-hint-header" @click="toggleHintDuck" :class="{ 'is-active': showHintDuck }">
           <Lightbulb class="w-4 h-4 mr-1.5" /> ?뚰듃蹂닿린
        </button>
        <button class="btn-tutorial-trigger" @click="startTutorial">
          <BookOpen class="w-4 h-4 mr-2" /> ?ъ슜踰??쒗넗由ъ뼹)
        </button>
        <button class="btn-practice-close" @click="closePractice">
          <X class="w-4 h-4 mr-2" /> ?ㅼ뒿 醫낅즺
        </button>
      </div>
    </header>

    <!-- MAIN VIEWPORT [2026-02-11] UI ?덉씠?꾩썐 2??援ъ꽦(Battle Grid) 蹂듭썝 -->
    <main class="viewport">
        
      <!-- [2026-02-14 ?섏젙] ?됯? ?④퀎?먯꽌??媛?대뱶 踰꾪듉 ?④? -->
      <button v-if="gameState.phase !== 'EVALUATION'" class="btn-guide-floating" @click="toggleGuide" :class="{ 'is-open': isGuideOpen }">
          <span class="icon">?</span>
          <span class="label">CHAPTER</span>
      </button>

      <!-- [2026-02-11] ?ъ씠?쒕컮 媛?대뱶 ?⑤꼸 -->
      <div class="guide-sidebar" :class="{ 'sidebar-open': isGuideOpen }">
          <div class="sidebar-header">
              <span class="sh-title">MISSION CHAPTERS</span>
              <button class="sh-close" @click="toggleGuide">횞</button>
          </div>
          <div class="sidebar-content">
              <!-- [2026-02-11] 誘몄뀡 ?붿??덉뼱留?媛?대뱶 (?섏궗肄붾뱶 ?묒꽦 ?먯튃) -->
            <div v-if="currentMission.designContext?.writingGuide" class="guide-step-card g-active mt-4">
                <div class="gs-header-row">
                    <div class="gs-icon"><Lightbulb class="w-5 h-5 text-blue-400" /></div>
                    <div class="gs-info">
                        <span class="gs-step text-blue-400">ENGINEERING_GUIDE</span>
                        <p class="gs-text">?섏궗肄붾뱶 ?묒꽦 ?꾨왂</p>
                    </div>
                </div>
                <div class="gs-hint-content hint-box-blue">
                    <p class="hint-text-small">{{ currentMission.designContext.writingGuide }}</p>
                </div>
            </div>

            <div v-for="(guide, idx) in currentMission.guides" 
                  :key="idx"
                  class="guide-step-card"
                  :class="{ 'g-active': idx === selectedGuideIdx }"
                  @click="handleGuideClick(idx)"
              >
                  <div class="gs-header-row">
                      <div class="gs-icon">{{ guide.icon }}</div>
                      <div class="gs-info">
                          <div class="gs-step">STEP {{ idx + 1 }}</div>
                          <div class="gs-text">{{ guide.text.split(':')[1] || guide.text }}</div>
                      </div>
                  </div>
                  <div class="gs-hint-content" v-if="idx === selectedGuideIdx">
                      <div class="hint-label">?뮕 TACTICAL ADVICE</div>
                      <p class="hint-body text-[11px] leading-tight">"{{ guide.coduckMsg }}"</p>
                  </div>
              </div>
          </div>
      </div>

      <!-- [2026-02-14 ?섏젙] 2???덉씠?꾩썐 ?듭떖 而⑦뀒?대꼫 (EVALUATION ??1?⑥쑝濡?蹂寃? -->
      <div class="combat-grid w-full h-full" :class="{ 'full-width-layout': gameState.phase === 'EVALUATION' }">
          
          <!-- LEFT PANEL: ENTITY CARD [2026-02-14 ?섏젙] ?됯? ?④퀎?먯꽌??醫뚯륫 ?⑤꼸 ???-->
          <aside v-if="gameState.phase !== 'EVALUATION'" class="entity-card">
              <div class="entity-header">
                  <span class="e-type">ANALYZE_UNIT</span>
                  <span class="e-status">SYSTEM_ACTIVE</span>
              </div>

              <div class="visual-frame">
                  <!-- [2026-02-11] 肄붾뜒 罹먮┃???대?吏 ?곌껐 [2026-02-14] ?대┃ ???ㅼ떆媛??뚰듃 ?좉? -->
                  <img src="@/assets/image/duck_det.png" alt="Coduck Detective" class="coduck-portrait cursor-pointer hover:scale-105 transition-transform" @click="toggleHintDuck" />
                  <div class="scan-overlay"></div>
                  
                  <!-- [2026-02-11] ?먯긽 ???쒖떆 -->
                  <div v-if="gameState.playerHP < 40" class="disconnect-tag">INTEGRITY_COMPROMISED</div>
              </div>

              <!-- [2026-02-11] 肄붾뜒 ?ㅼ떆媛???ъ갹 [2026-02-14 ?섏젙] ?됯? 諛?寃곌낵 ?붾㈃?먯꽌???쒕굹由ъ삤 諛뺤뒪 ???-->
              <div v-if="gameState.phase !== 'EVALUATION'" class="dialogue-box">
                  <span class="speaker">臾몄젣 ?쒕굹由ъ삤</span>
                  <p class="dialogue-text">"{{ (isInteractionPhase && currentMission.scenario) ? currentMission.scenario : (gameState.coduckMessage || '?곗씠???먮쫫??遺꾩꽍 以묒엯?덈떎...') }}"</p>
              </div>


          </aside>

          <!-- RIGHT PANEL: DECISION ENGINE [2026-02-11] ?④퀎蹂??명꽣?숈뀡 ?곸뿭 -->
          <section class="decision-panel relative" :class="{ 'visualization-p-zero': ['PYTHON_VISUALIZATION', 'TAIL_QUESTION', 'DEEP_DIVE_DESCRIPTIVE'].includes(gameState.phase) }">
              <div v-if="gameState.phase.startsWith('DIAGNOSTIC')">
                  <div class="system-status-row">
                      <span v-if="gameState.phase === 'DIAGNOSTIC_1'">STEP_01: CONCEPT_IDENTIFICATION</span>
                      <span v-else-if="gameState.phase === 'PSEUDO_WRITE'">STEP_02: PSEUDO_ARCHITECTURE</span>
                  </div>
                  
                  <!-- 吏臾???肄붾뱶 釉붾줉 ?뚮뜑留??곸뿭 [2026-02-12] ?섏씠利?臾닿??섍쾶 而⑦뀓?ㅽ듃媛 ?덉쑝硫??쒖떆 -->
                  <div v-if="diagnosticProblemParts" class="diagnostic-code-box">
                      <div class="diagnostic-instruction">{{ diagnosticProblemParts.instruction }}</div>
                      <div class="diagnostic-code">{{ diagnosticProblemParts.code }}</div>
                  </div>

                  <h3 v-if="gameState.phase === 'DIAGNOSTIC_1' && diagnosticQuestion.type !== 'CHOICE'" class="big-question">
                      {{ diagnosticQuestion.question }}
                  </h3>
                  
                  <!-- [2026-02-12] PHASE 1 ?꾩슜 釉붾줉 -->
                  <div v-if="gameState.phase === 'DIAGNOSTIC_1'" class="diagnostic-content-area">
                      <!-- ?쒖닠??UI -->
                      <div v-if="diagnosticQuestion.type === 'DESCRIPTIVE'" class="descriptive-interaction-area">
                          <div v-if="gameState.diagnosticResult && !gameState.isEvaluatingDiagnostic" class="diagnostic-result-card animate-fadeIn">
                              <div class="dr-header">
                                  <span class="dr-label">AI_ARCHITECT_VERDICT</span>
                                  <span class="dr-score" :class="gameState.diagnosticResult.score >= 70 ? 'text-green-400' : 'text-yellow-400'">{{ gameState.diagnosticResult.score }} PTS</span>
                              </div>
                              <div class="dr-analysis">"{{ gameState.diagnosticResult.analysis }}"</div>
                              <div class="dr-feedback">{{ gameState.diagnosticResult.feedback }}</div>
                              <div v-if="diagnosticQuestion.evaluationRubric?.correctAnswer" class="model-answer-box animate-fadeIn">
                                  <div class="ma-header"><Brain class="w-4 h-4 text-purple-400" /><span class="ma-label">紐⑤쾾 ?듭븞</span></div>
                                  <p class="ma-content">{{ diagnosticQuestion.evaluationRubric.correctAnswer }}</p>
                              </div>
                          </div>
                          <textarea v-model="gameState.diagnosticAnswer" class="diagnostic-textarea" placeholder="遺꾩꽍 ?댁슜???낅젰?섏꽭??.." :disabled="gameState.isEvaluatingDiagnostic"></textarea>
                          
                          <div class="actions relative mt-4">
                              <Transition name="fade-slide">
                                <div v-if="showHintDuck && isNaturalLanguagePhase" class="hint-duck-wrapper" @click="toggleHintDuck" title="?대┃?섎㈃ ?ㅼ떆 ?④퉩?덈떎">
                                    <div class="hint-bubble">
                                        <div class="hb-content">{{ dynamicHintMessage || '遺꾩꽍 以묒엯?덈떎...' }}</div>
                                        <div class="hb-tail"></div>
                                    </div>
                                    <img src="@/assets/image/unit_duck.png" alt="Hint Duck" class="hint-unit-img clickable-duck" />
                                </div>
                              </Transition>

                              <button @click="submitDiagnostic()" class="btn-execute-large w-full-btn" :disabled="(!gameState.diagnosticAnswer || gameState.diagnosticAnswer.trim().length < 5) && !gameState.diagnosticResult || gameState.isEvaluatingDiagnostic">
                                  <template v-if="gameState.isEvaluatingDiagnostic">遺꾩꽍 以?.. <RotateCcw class="w-5 h-5 ml-2 animate-spin" /></template>
                                  <template v-else-if="gameState.diagnosticResult">?ㅼ쓬 ?④퀎 吏꾪뻾 <ArrowRight class="w-5 h-5 ml-2" /></template>
                                  <template v-else>遺꾩꽍 ?꾨즺 ?쒖텧 <CheckCircle class="w-5 h-5 ml-2" /></template>
                              </button>
                          </div>
                      </div>
                      <!-- 媛앷???UI (CHOICE) [2026-02-14 ?섏젙] ?쇰뱶諛?猷⑦봽 異붽? -->
                      <div v-else-if="diagnosticQuestion.type === 'CHOICE'" class="choice-interaction-area">
                          <div class="choice-visual-frame mb-8">
                              <div class="choice-coduck">
                                  <img :src="currentMission.character?.image || '@/assets/image/duck_det.png'" alt="Coduck Interviewer" />
                              </div>
                              <div class="choice-speech-bubble" :class="{ 'correct-bubble': gameState.isDiagnosticAnswered && diagnosticQuestion.options[gameState.diagnosticAnswerIdx]?.correct, 'wrong-bubble': gameState.isDiagnosticAnswered && !diagnosticQuestion.options[gameState.diagnosticAnswerIdx]?.correct }">
                                  <div class="bubble-tail"></div>
                                  <p class="bubble-text">{{ gameState.isDiagnosticAnswered ? gameState.coduckMessage : diagnosticQuestion.question }}</p>
                              </div>
                          </div>
                          <div class="options-list">
                              <div 
                                v-for="(opt, idx) in diagnosticQuestion.options" 
                                :key="idx" 
                                @click="submitDiagnostic(idx)" 
                                class="option-card"
                                :class="{ 
                                    'is-selected': gameState.diagnosticAnswerIdx === idx,
                                    'is-correct': gameState.isDiagnosticAnswered && (opt.correct || opt.is_correct),
                                    'is-wrong': gameState.isDiagnosticAnswered && gameState.diagnosticAnswerIdx === idx && !(opt.correct || opt.is_correct),
                                    'is-disabled': gameState.isDiagnosticAnswered
                                }"
                              >
                                  <div class="opt-index">{{ idx + 1 }}</div>
                                  <div class="opt-main text-lg">{{ opt.text }}</div>
                                  <div class="opt-status-icon">
                                      <CheckCircle v-if="gameState.isDiagnosticAnswered && (opt.correct || opt.is_correct)" class="text-green-400" />
                                      <X v-else-if="gameState.isDiagnosticAnswered && gameState.diagnosticAnswerIdx === idx" class="text-red-400" />
                                      <ArrowRight v-else />
                                  </div>
                              </div>
                          </div>

                          <!-- [異붽?] ?ㅼ쓬 ?④퀎 吏꾪뻾 踰꾪듉 (?듬? ?꾩뿉留??깆옣) -->
                          <div v-if="gameState.isDiagnosticAnswered" class="mt-8 animate-fadeIn">
                              <button @click="submitDiagnostic()" class="btn-execute-large w-full-btn">
                                  ?ㅼ쓬 遺꾩꽍 ?④퀎濡?吏꾪뻾 <ArrowRight class="w-5 h-5 ml-2" />
                              </button>
                          </div>
                      </div>
                  </div>
                  <!-- AI ?꾪궎?랁듃 遺꾩꽍 ?ㅻ쾭?덉씠 (吏꾨떒 ?④퀎) -->
                  <div v-if="gameState.isEvaluatingDiagnostic" class="ai-loading-overlay">
                      <LoadingDuck message="?곗씠???먮쫫 諛??쇰━????뱀꽦???뺣? 遺꾩꽍 以묒엯?덈떎..." />
                  </div>
              </div>

              <!-- [2026-02-11] PHASE: PSEUDO_WRITE (Step 2: ?꾪궎?띿쿂 ?ㅺ퀎) -->
              <div v-else-if="gameState.phase === 'PSEUDO_WRITE'" class="space-y-4 flex flex-col h-full max-w-5xl mx-auto w-full">
                  <!-- AI ?꾪궎?랁듃 遺꾩꽍 ?ㅻ쾭?덉씠 (?섏궗肄붾뱶 ?ы솕 遺꾩꽍 ?④퀎) [異붽?: 2026-02-13] -->
                  <div v-if="isProcessing" class="ai-loading-overlay">
                      <LoadingDuck message="?묒꽦?섏떊 ?ㅺ퀎??5李⑥썝 ?꾪궎?띿쿂 ?뺣? 遺꾩꽍 諛?Python 肄붾뱶 蹂??以묒엯?덈떎..." />
                  </div>
                  <!-- [2026-02-12] ?대?吏 ?깊겕: 硫붿씤 ??댄? 諛??ㅻ챸 媛쒗렪 (誘몄뀡/?쒖빟議곌굔 ?몄텧) [?고듃 ?곹뼢 諛?以묐났 ?쒓굅] -->
                  <div class="mission-instruction-compact">
                      <div class="mi-section">
                          <h4 class="mi-title text-blue-400">[誘몄뀡]</h4>
                          <p class="mi-desc">{{ currentMission.designContext?.description }}</p>
                      </div>
                      <div class="mi-section mi-border-top">
                          <h4 class="mi-title text-amber-400">[?꾩닔 ?ы븿 議곌굔 (Constraint)]</h4>
                          <p class="mi-desc-small">{{ currentMission.designContext?.writingGuide?.replace('[?꾩닔 ?ы븿 議곌굔 (Constraint)]\n', '') }}</p>
                      </div>
                  </div>

                  <div class="editor-layout w-full flex flex-col flex-1">
                      <div class="editor-body w-full flex-1 flex flex-col">
                          <!-- ?섏궗肄붾뱶 ?낅젰 ?먮뵒??-->
                          <div class="monaco-wrapper w-full h-[320px] border border-slate-700/50 rounded-xl overflow-hidden shadow-2xl">
                              <VueMonacoEditor
                                  theme="vs-dark"
                                  language="python"
                                  :options="monacoOptions"
                                  @mount="handleMonacoMount"
                                  class="w-full h-full"
                              />
                          </div>
                      </div>

                       <div class="editor-header w-full mt-4 flex justify-between items-end">
                          <!-- [2026-02-13] ?ㅼ떆媛?洹쒖튃 泥댄겕由ъ뒪??UI: ?섎떒 諛곗튂 -->
                          <div class="rule-checklist-bar flex flex-wrap gap-2 mb-2">
                              <div 
                                  v-for="rule in ruleChecklist" 
                                  :key="rule.id"
                                  class="rule-chip"
                                  :class="{ 'is-completed': rule.completed }"
                              >
                                  <CheckCircle v-if="rule.completed" class="w-3.5 h-3.5" />
                                  <div v-else class="rule-dot"></div>
                                  <span class="rule-label">{{ rule.label }}</span>
                              </div>
                          </div>

                          <div class="actions flex items-center justify-end gap-4 relative">
                              <!-- [2026-02-14] ?ㅼ떆媛??뚰듃 ?ㅻ━ & 留먰뭾??(遺꾩꽍 以묒씪 ?뚮뒗 ??? -->
                              <Transition name="fade-slide">
                                <div v-if="showHintDuck && isNaturalLanguagePhase" class="hint-duck-wrapper" @click="toggleHintDuck" title="?대┃?섎㈃ ?ㅼ떆 ?④퉩?덈떎">
                                    <div class="hint-bubble">
                                        <div class="hb-content">{{ dynamicHintMessage || '遺꾩꽍 以묒엯?덈떎...' }}</div>
                                        <div class="hb-tail"></div>
                                    </div>
                                    <img src="@/assets/image/unit_duck.png" alt="Hint Duck" class="hint-unit-img clickable-duck" />
                                </div>
                              </Transition>

                              <button 
                                  :disabled="!canSubmitPseudo || isProcessing"
                                  @click="submitPseudo"
                                  class="btn-execute-large"
                              >
                                  ?ы솕 遺꾩꽍 ?쒖옉 <Play class="w-4 h-4 ml-1.5" />
                              </button>
                          </div>
                      </div>
                  </div>
              </div>

              <!-- [STEP 3] ?꾩닠 ?쒓컖??諛?2?④퀎 寃利?(MCQ + ?ㅻТ ?쒕굹由ъ삤) -->
              <div v-else-if="['PYTHON_VISUALIZATION', 'TAIL_QUESTION', 'DEEP_DIVE_DESCRIPTIVE'].includes(gameState.phase)" class="visualization-phase flex-1 flex flex-col min-h-0">
                  <CodeFlowVisualizer
                    :phase="gameState.phase"
                    :pseudocode="gameState.phase3Reasoning"
                    :python-code="evaluationResult.converted_python"
                    :evaluation-score="evaluationResult.overall_score"
                    :evaluation-feedback="evaluationResult.one_line_review || evaluationResult.feedback"
                    :mcq-data="evaluationResult.tail_question || evaluationResult.deep_dive"
                    :blueprint-steps="evaluationResult.blueprint_steps"
                    :assigned-scenario="gameState.assignedScenario"
                    :is-mcq-answered="gameState.isMcqAnswered"
                    @answer-mcq="handleMcqAnswer"
                    @submit-descriptive="submitDescriptiveDeepDive"
                    @next-phase="handlePythonVisualizationNext"
                  />
              </div>

              <!-- [STEP 4] 理쒖쥌 由ы룷??(EVALUATION) [2026-02-13] decision-panel ?대?濡??대룞 -->
              <div v-else-if="gameState.phase === 'EVALUATION'" class="evaluation-phase relative flex-1 flex flex-col h-full scroll-smooth">
                  <!-- [2026-02-13] 蹂듦린 ?숈뒿 紐⑤뱶 ??誘몄뀡 ?뺣낫 ?щ끂異?-->
                  <div v-if="evaluationResult?.is_low_effort || gameState.hasUsedBlueprint" class="mission-instruction-compact animate-slideDownFade mb-6">
                      <div class="mi-section">
                          <h4 class="mi-title text-blue-400">[誘몄뀡]</h4>
                          <p class="mi-desc">{{ currentMission?.designContext?.description }}</p>
                      </div>
                      <div class="mi-section mi-border-top">
                          <h4 class="mi-title text-amber-400">[?꾩닔 ?ы븿 議곌굔 (Constraint)]</h4>
                          <p class="mi-desc-small">{{ currentMission?.designContext?.writingGuide?.replace('[?꾩닔 ?ы븿 議곌굔 (Constraint)]\n', '') }}</p>
                      </div>
                  </div>
                  <!-- [2026-02-14 ?섏젙] 濡쒕뵫 ?붾㈃??1踰덉㎏ ?대?吏 ?ㅽ??쇰줈 蹂寃?(Full Width & Background Sync) -->
                  <div v-if="tutorialAnalyzing || (isProcessing && gameState.phase === 'EVALUATION')" class="ai-analysis-simulation absolute inset-0 z-[100] bg-[#050505] flex flex-col items-center justify-center rounded-2xl border border-emerald-500/30">
                      <LoadingDuck 
                        :message="tutorialAnalyzing ? '?쒗넗由ъ뼹 遺꾩꽍 以?..' : '?묒꽦?댁＜???먮쫫 諛뷀깢?쇰줈 醫낇빀?됯? 吏꾪뻾 以묒엯?덈떎...'" 
                        :duration="4000"
                      />
                  </div>

                  <!-- [2026-02-14] 理쒖쥌 ?꾪궎?띿쿂 由ы룷???ы깉 (PPT ?덉씠?꾩썐 理쒖쟻?? -->
                  <div v-if="!tutorialAnalyzing && showMetrics && finalReport" class="architect-report-portal animate-fadeIn">
                      
                      <!-- Part 1: Strategic Billboard (Score & Grade) -->
                      <div class="report-billboard-premium">
                          <div class="billboard-glass"></div>
                          <div class="billboard-content">
                              <div class="score-ring-box">
                                  <svg viewBox="0 0 100 100" class="ring-svg-neo">
                                      <circle class="ring-bg" cx="50" cy="50" r="45"></circle>
                                      <circle class="ring-fill" cx="50" cy="50" r="45" :style="{ strokeDasharray: 283, strokeDashoffset: 283 - (283 * finalReport.totalScore / 100) }"></circle>
                                  </svg>
                                  <div class="score-absolute">
                                      <span class="pts-num">{{ finalReport.totalScore }}</span>
                                      <span class="pts-unit">PTS</span>
                                  </div>
                              </div>
                              <div class="grade-badge-box">
                                  <div class="grade-symbol-neo">
                                      <span class="symbol">{{ finalReport.grade.grade }}</span>
                                      <span class="label">STATUS</span>
                                  </div>
                                  <div class="verdict-wrapper">
                                      <h3 class="persona-title">理쒖쥌 吏꾨떒: {{ finalReport.finalReport.persona }}</h3>
                                      <h2 class="verdict-headline">"{{ finalReport.finalReport.summary }}"</h2>
                                  </div>
                              </div>
                              <div class="mission-ident">
                                  <div class="ch-tag">MISSION: {{ currentMission.title }}</div>
                              </div>
                          </div>
                      </div>

                      <!-- Part 2: Analysis Center (Dual Hub) -->
                      <div class="report-hub-grid">
                          <!-- Visual Balance Scan -->
                          <div class="hub-cell visual-scan">
                              <div class="neo-glass-card">
                                  <h3 class="neo-card-title"><Activity size="14" /> Logic Balance Scan</h3>
                                  <div class="radar-container-neo">
                                      <canvas ref="radarChartCanvas"></canvas>
                                  </div>
                              </div>
                          </div>

                          <!-- Dimension Breakdowns -->
                          <div class="hub-cell metrics-matrix">
                              <div class="neo-glass-card h-full">
                                  <h3 class="neo-card-title"><Layers size="14" /> Dimension Matrix</h3>
                                  <div class="metric-progress-list">
                                      <div v-for="(metric, key) in finalReport.metrics" :key="key" class="metric-row-neo premium-feedback">
                                          <div class="m-header">
                                              <span class="m-name">{{ metric.name }}</span>
                                              <span class="m-score-tag" :style="{ color: getMetricColor(metric.percentage) }">{{ metric.percentage }}%</span>
                                          </div>
                                          <div class="m-comment-box">
                                              <p class="m-comment-text">
                                                  <span class="quote-icon">"</span>
                                                  {{ metric.comment }}
                                                  <span class="quote-icon">"</span>
                                              </p>
                                          </div>
                                      </div>
                                  </div>
                              </div>
                          </div>
                      </div>

                      <!-- Part 3: Expert Senior Verdict -->
                      <div class="expert-section-neo">
                          <div class="mentor-glass-card">
                              <div class="mentor-profile">
                                  <div class="mentor-avatar">
                                      <img src="@/assets/image/duck_det.png" alt="Architect Duck" />
                                  </div>
                                  <div class="mentor-meta">
                                      <span class="m-role">Senior Architect Monitor</span>
                                      <h4 class="m-name">Chief Duck Engineer</h4>
                                  </div>
                              </div>
                              
                              <div class="feedback-dual-grid">
                                  <div class="fb-item-neo plus">
                                      <span class="tag-neo text-emerald-400">CORE STRENGTH</span>
                                      <p class="txt-neo"><b>{{ finalReport.finalReport.strength.metric }}:</b> {{ finalReport.finalReport.strength.feedback }}</p>
                                  </div>
                                  <div class="fb-item-neo minus">
                                      <span class="tag-neo text-amber-400">EVOLVE POINT</span>
                                      <p class="txt-neo"><b>{{ finalReport.finalReport.weakness.metric }}:</b> {{ finalReport.finalReport.weakness.feedback }}</p>
                                  </div>
                              </div>

                              <div class="one-point-lesson-neo">
                                  <div class="p-icon-box"><Lightbulb size="20" class="text-amber-400" /></div>
                                  <div class="p-content">
                                      <span class="p-tag">ONE-POINT LESSON</span>
                                      <p class="p-msg">{{ finalReport.finalReport.lesson }}</p>
                                  </div>
                              </div>
                          </div>
                      </div>

                      <!-- Part 4: Continuous Learning Path (YouTube) -->
                      <div class="pathway-section-neo">
                          <div class="curation-header">
                              <h3 class="path-heading-neo"><Play size="18" class="mr-2" /> ?벟 ?ㅼ떆媛?留욎땄???숈뒿 ?먮젅?댁뀡 (YouTube API 湲곕컲)</h3>
                          </div>
                          
                          <div class="path-grid-neo">
                               <!-- [2026-02-14] API濡??ㅼ떆媛??곕룞??異붿쿇 ?곸긽 紐⑸줉 ?쒖떆 -->
                               <div v-for="video in evaluationResult.supplementaryVideos" :key="video.videoId" class="path-card-neo curation-card">
                                  <a :href="video.url" target="_blank" class="p-link-neo">
                                      <div class="p-thumbnail border-b border-white/5 overflow-hidden rounded-t-xl mb-3">
                                          <img :src="video.thumbnail" :alt="video.title" class="w-full h-auto transform hover:scale-105 transition-transform" />
                                      </div>
                                      <div class="p-index text-blue-400">{{ video.channelTitle }}</div>
                                      <h4 class="p-video-title text-sm font-bold text-white mb-2 leading-snug line-clamp-2">{{ video.title }}</h4>
                                      <p class="text-xs text-slate-400 line-clamp-3 leading-relaxed">{{ video.description }}</p>
                                      <div class="flex items-center justify-end mt-4 text-emerald-400 font-bold text-[10px]">
                                          <Play size="14" class="mr-1" /> WATCH NOW
                                      </div>
                                  </a>
                               </div>

                               <!-- API 寃곌낵媛 ?놁쓣 寃쎌슦 湲곗〈 Resource ?대갚 -->
                               <div v-if="!evaluationResult.supplementaryVideos?.length && weakestMetricKey" class="path-card-neo curation-card weakest-focus">
                                  <div class="weakest-badge">?슚 痍⑥빟 吏??吏묒쨷 蹂댁셿</div>
                                  <a :href="getMetricVideo(weakestMetricKey).url" target="_blank" class="p-link-neo">
                                      <div class="p-index">{{ LEARNING_RESOURCES[weakestMetricKey].metric }}</div>
                                      <div class="p-theme-tag">?뚮쭏: {{ LEARNING_RESOURCES[weakestMetricKey].theme }}</div>
                                      <div class="p-content-box mt-4">
                                          <div class="p-curation-msg-box">
                                              <span class="quote-icon">"</span>
                                              {{ LEARNING_RESOURCES[weakestMetricKey].curationMessage }}
                                              <span class="quote-icon">"</span>
                                          </div>
                                      </div>
                                  </a>
                               </div>
                          </div>

                          <!-- [2026-02-14] 留덉뒪???덈꺼 ?꾩슜 肄섑뀗痢?-->
                          <div v-if="evaluationResult.overall_score >= 80" class="master-next-level mt-10">
                              <div class="master-header">
                                  <h3 class="path-heading-neo master-glow"><CheckCircle size="18" class="mr-2" /> ?룇 S-CLASS ?꾪궎?랁듃 ?꾩슜 ?ы솕 ?몄뀡</h3>
                                  <p class="master-message">?대? ?ㅺ퀎 ?먯튃???꾨꼍???댄빐?섏뀲援곗슂! ?댁젣???뷀꽣?꾨씪?댁쫰 ?덈꺼???뺤옣??怨좊????뚯엯?덈떎.</p>
                              </div>
                          </div>
                      </div>

                      <!-- Part 5: Final Actions -->
                          <div class="terminal-actions-neo">
                              <button @click="resetFlow" class="btn-neo-restart" aria-label="Restart Mission">
                                  <RotateCcw size="18" class="mr-2" /> RESTART MISSION
                              </button>
                              <button @click="completeMission" class="btn-neo-complete" aria-label="Complete Mission">
                                  <CheckCircle size="18" class="mr-2" /> MISSION COMPLETE
                              </button>
                          </div>
                  </div>

                  </div>
              </section>
          </div>
      
      <!-- BugHunt ?ㅽ????ㅻ━ ?뚰듃 ?쒖뒪??[2026-02-13] - viewport ?섎떒 諛곗튂 -->
      <transition name="duck-pop">
        <div v-if="gameState.showHint" class="hint-duck-container">
            <div class="hint-speech-bubble">
                <div class="bubble-header">DUC-TIP!</div>
                <div class="bubble-content">
                    <p v-for="(hintText, hIdx) in currentMission.validation?.concepts?.flatMap(c => c.hints || [])" :key="hIdx" class="hint-li">
                        ??{{ hintText }}
                    </p>
                </div>
            </div>
            <img src="@/assets/image/duck_det.png" class="hint-duck-img" alt="Hint Duck">
        </div>
      </transition>
    </main>

    <!-- [2026-02-14 ?섏젙] ??좊━???ㅻ쾭?덉씠 異붽? (?섏씠利?蹂寃?由ъ뒪??異붽?) -->
    <PseudocodeTutorialOverlay
      v-if="showTutorial"
      @complete="onTutorialComplete"
      @skip="onTutorialComplete"
      @quit="closePractice"
      @change-phase="handleTutorialPhaseChange"
    />

    <!-- [2026-02-11] FEEDBACK TOAST -->
    <div v-if="gameState.feedbackMessage && gameState.phase !== 'EVALUATION'" class="feedback-toast">
      <span class="toast-icon">!</span> {{ gameState.feedbackMessage }}
    </div>
  </div>
</template>

<script setup>
/**
 * ?섏젙?? 2026-02-14
 * ?섏젙 ?댁슜: 5? 吏???됯? ?쒖뒪???꾩쟾 ?듯빀 諛??꾨━誘몄뾼 由ы룷??UI ?곸슜
 */
import { computed, ref, reactive, onMounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useGameStore } from '@/stores/game';
import { useCoduckWars } from './composables/useCoduckWars.js';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import { useMonacoEditor } from './composables/useMonacoEditor.js';
import { 
  AlertOctagon, Info, ArrowRight, Lightbulb, 
  RotateCcw, Play, X, Brain, CheckCircle,
  Activity, Layers, Cpu
} from 'lucide-vue-next';
import { ComprehensiveEvaluator } from './evaluationEngine.js';
import { generateCompleteLearningReport } from './reportGenerator.js';
import { filterByScore, LEARNING_RESOURCES } from './learningResources.js';
import Chart from 'chart.js/auto';

const activeYoutubeId = ref(null);
import CodeFlowVisualizer from './components/CodeFlowVisualizer.vue';
import LoadingDuck from '../components/LoadingDuck.vue';
import PseudocodeTutorialOverlay from './components/PseudocodeTutorialOverlay.vue';
import { BookOpen } from 'lucide-vue-next';

const router = useRouter();
const gameStore = useGameStore();
const emit = defineEmits(['close']);

// [2026-02-14] ?쒗넗由ъ뼹 諛?由ы룷??愿???곹깭 蹂???좎뼵 (理쒖긽???대룞)
const showTutorial = ref(false);
const originalPhase = ref(null);
const tutorialAnalyzing = ref(false);
const showMetrics = ref(false);
const finalReport = ref(null);
const radarChartCanvas = ref(null);
let radarChartInstance = null;

// [2026-02-14] useCoduckWars 遺꾨━ 諛??곗씠???좎뼵 (?곷떒 ?대룞)
const coduckWarsComposable = useCoduckWars();
const { resetHintTimer } = coduckWarsComposable;
const originalSubmitPseudo = coduckWarsComposable.submitPseudo;

const {
    gameState,
    currentMission,
    evaluationResult,
    deepQuizQuestion,
    ruleChecklist,
    canSubmitPseudo,
    isProcessing,
    isGuideOpen,
    selectedGuideIdx,
    showHintDuck,
    toggleHintDuck,
    dynamicHintMessage,
    retryDesign,

    toggleGuide,
    handleGuideClick,
    submitDiagnostic,
    diagnosticQuestion,
    submitDeepQuiz,
    handleMcqAnswer,
    submitDescriptiveDeepDive,
    handlePythonVisualizationNext,
    handleTailSelection: originalHandleTailSelection,
    resetFlow: engineResetFlow,
    toggleHint,
    handlePracticeClose,
    addSystemLog,
    handleReSubmitPseudo
} = coduckWarsComposable;

onMounted(() => {
  if (!localStorage.getItem('pseudocode-tutorial-done')) {
    startTutorial();
  }
});

const startTutorial = () => {
    // ?쒗넗由ъ뼹 ?쒖옉 ???꾩옱 ?섏씠利?諛깆뾽
    originalPhase.value = gameState.phase;
    showTutorial.value = true;
};

/**
 * [2026-02-14 ?섏젙] ?쒗넗由ъ뼹 吏꾪뻾???곕Ⅸ ?섏씠利??먮룞 ?꾪솚 諛?紐⑦궧
 */
const handleTutorialPhaseChange = (targetPhase) => {
    gameState.phase = targetPhase;

    // ?쒗넗由ъ뼹 以??붾㈃??鍮꾩뼱 蹂댁씠吏 ?딅룄濡?紐⑦겕 ?곗씠??二쇱엯
    if (targetPhase === 'DIAGNOSTIC_1') {
        // 吏꾨떒 ?④퀎?먯꽌 吏덈Ц ?곗씠?곌? ?녿뒗 寃쎌슦瑜??鍮꾪븳 紐⑦궧
    }

    if (targetPhase === 'PSEUDO_WRITE') {
        // [?섏젙] ?ъ슜?먭? 吏곸젒 ?묒꽦?????덈룄濡??먮룞 梨꾩슦湲?濡쒖쭅 ?쒓굅
    }

    if (targetPhase === 'PYTHON_VISUALIZATION') {
        // evaluationResult??reactive 媛앹껜?대?濡?.value ?놁씠 ?묎렐
        if (!evaluationResult.converted_python) {
            Object.assign(evaluationResult, {
                converted_python: "import pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.preprocessing import StandardScaler\n\n# 1. Isolation: 臾쇰━??寃⑸━\ntrain_df, test_df = train_test_split(df, test_size=0.2)\n\n# 2. Anchor: ?숈뒿 ?명듃?먯꽌留??듦퀎??異붿텧\nscaler = StandardScaler()\nscaler.fit(train_df[['age', 'income']])\n\n# 3. Consistency: ?숈씪??蹂???곸슜\ntrain_scaled = scaler.transform(train_df[['age', 'income']])\ntest_scaled = scaler.transform(test_df[['age', 'income']])",
                feedback: "?곗씠???꾩닔 諛⑹? ?먯튃???뺥솗?섍쾶 以?섑븳 ?ㅺ퀎?낅땲?? ?뱁엳 湲곗????ㅼ젙???뚮??⑸땲??",
                overall_score: 88,
                one_line_review: "?곗씠???꾩닔 李⑤떒???꾪븳 寃⑸━(Isolation)? 湲곗???Anchor) ?ㅼ젙??留ㅼ슦 ?쇰━?곸엯?덈떎."
            });
        }
        // deepQuizQuestion? computed?대?濡?吏곸젒 ?좊떦 遺덇? -> evaluationResult ?곗씠???섏젙?쇰줈 ?고쉶
        if (!evaluationResult.tail_question && !evaluationResult.deep_dive) {
           evaluationResult.tail_question = {
               should_show: true,
               question: "紐⑤뜽 諛고룷 ???곗씠??遺꾪룷媛 湲됯꺽??蹂?섎뒗 'Data Drift'媛 諛쒖깮?섎㈃, 湲곗〈??湲곗???Anchor)???대뼸寃?泥섎━?댁빞 ?좉퉴??",
               options: [
                   { id: 1, text: "?덈줈???곗씠?곗뿉 留욎떠 湲곗??먯쓣 利됱떆 ?ы븰??Re-fit)?쒕떎.", is_correct: true, feedback: "?덉젙?깆쓣 ?꾪빐 二쇨린?곸씤 湲곗????낅뜲?댄듃媛 ?꾩슂?⑸땲??" },
                   { id: 2, text: "紐⑤뜽???쇨??깆쓣 ?꾪빐 珥덇린 湲곗??먯쓣 ?덈? 諛붽씀吏 ?딅뒗??", is_correct: false, feedback: "?곗씠??遺꾪룷 蹂?붿뿉 ??묓븯吏 紐삵빐 ?깅뒫????섎맆 ???덉뒿?덈떎." }
               ]
           };
        }
    }
    
    if (targetPhase === 'EVALUATION') {
        if (!finalReport.value) {
            tutorialAnalyzing.value = true;
            // ?쒗넗由ъ뼹??鍮좊Ⅸ ?쒕??덉씠??            setTimeout(() => {
                tutorialAnalyzing.value = false;
                showMetrics.value = true;
                finalReport.value = {
                    totalScore: 88,
                    grade: { grade: 'A+', description: 'Exceptional System Integrity' },
                    metrics: {
                        design: { name: '?붿옄??, percentage: 92, score: 92, max: 100 },
                        edgeCase: { name: '?덉쇅泥섎━', percentage: 85, score: 85, max: 100 },
                        abstraction: { name: '異붿긽??, percentage: 95, score: 95, max: 100 },
                        implementation: { name: '援ы쁽??, percentage: 78, score: 78, max: 100 },
                        consistency: { name: '?뺥빀??, percentage: 90, score: 90, max: 100 }
                    },
                    finalReport: {
                        persona: 'Architect Duck',
                        summary: '???ㅺ퀎???꾨꼍??寃⑸━? 湲곗???蹂댄샇 ?꾨왂??蹂댁뿬二쇰뒗 ?쒕낯?낅땲??',
                        strength: { metric: 'Consistency', feedback: '?곗씠???뺥빀???좎?瑜??꾪빐 湲곗??먯쓣 ?숈뒿 ?곗씠?곗뿉留?怨좎젙?섍퀬 ?뚯뒪???곗씠?곗뿉 ?쇨??섍쾶 ?꾪뙆?덉뒿?덈떎.' },
                        weakness: { metric: 'Implementation', feedback: '?ㅼ젣 ?꾨줈?뺤뀡 ?섍꼍?먯꽌??湲곗????낅뜲?댄듃(Re-fitting) 二쇨린瑜??먮룞?뷀븯??肄붾뱶瑜?異붽??섎㈃ ?붿슧 寃ш퀬?댁쭏 寃껋엯?덈떎.' },
                        lesson: '?곗씠???꾩닔???ъ냼??fit() ??踰덉쑝濡??쒖옉?⑸땲?? ??긽 Anchor(湲곗???媛 ?대뵒?몄? ?먭컖?섏떗?쒖삤.'
                    },
                    recommendedContent: {
                        curationMessage: '?꾪궎?띿쿂 ?ㅺ퀎 ??웾?????④퀎 ???믪뿬以?異붿쿇 媛뺤쓽?낅땲??',
                        videos: [
                            { title: 'MLOps?먯꽌???곗씠???뺤젣 ?꾨왂', channel: 'Tech Insight', duration: '12:45', url: '#', curationPoint: '?ㅻТ ?뚯씠?꾨씪??援ъ텞', difficulty: 'expert' },
                            { title: 'Data Leakage ?꾨꼍 媛?대뱶', channel: 'AI School', duration: '18:20', url: '#', curationPoint: '?ㅼ뼇???꾩닔 ?щ? 遺꾩꽍', difficulty: 'expert' }
                        ]
                    }
                };
                nextTick(() => {
                    if (typeof renderRadarChart === 'function') renderRadarChart();
                });
            }, 1800);
        } else {
            showMetrics.value = true;
        }
    }
};

const onTutorialComplete = () => {
    showTutorial.value = false;
    // ?ㅼ젣 吏꾪뻾 以묒씠???섏씠利덈줈 蹂듦뎄
    if (originalPhase.value) {
        gameState.phase = originalPhase.value;
    }
    localStorage.setItem('pseudocode-tutorial-done', 'true');
};

const closePractice = () => {
  if (confirm('?ㅼ뒿??醫낅즺?섍퀬 紐⑸줉?쇰줈 ?뚯븘媛?쒓쿋?듬땲源?')) {
    emit('close');
  }
};

const resetFlow = () => {
    engineResetFlow();
    finalReport.value = null;
    showMetrics.value = false;
    showHintDuck.value = false;
    addSystemLog("?쒖뒪?쒖쓣 泥섏쓬遺???ㅼ떆 ?쒖옉?⑸땲??", "INFO");
};

const completeMission = () => {
    const stageIdx = (gameState.currentStageId || 1) - 1;
    gameStore.unlockNextStage('Pseudo Practice', stageIdx);
    if (stageIdx < 9) {
        gameStore.selectedQuestIndex = stageIdx + 1;
    }
    addSystemLog(`誘몄뀡 ?꾨즺: ?ㅽ뀒?댁? ${gameState.currentStageId} ?곗씠?곕쿋?댁뒪 湲곕줉??`, "SUCCESS");
    emit('close');
};

const isNaturalLanguagePhase = computed(() => {
    if (isProcessing.value || showMetrics.value || tutorialAnalyzing.value) return false;
    if (gameState.phase === 'PSEUDO_WRITE') return true;
    if (gameState.phase === 'DIAGNOSTIC_1' && diagnosticQuestion.value?.type === 'DESCRIPTIVE') return true;
    return false;
});

// [2026-02-14] 5? 吏???됯? ?쒖뒪??異붽? (?곹깭 蹂?섎뒗 ?곷떒?쇰줈 ?대룞??

async function runComprehensiveEvaluation() {
  if (finalReport.value || isProcessing.value) return;
  
  try {
    isProcessing.value = true;
    gameState.feedbackMessage = "?쒕땲???꾪궎?랁듃媛 理쒖쥌 寃??以묒엯?덈떎...";
    
    const evaluator = new ComprehensiveEvaluator(getApiKey());
    const evaluationResults = await evaluator.evaluate({
      pseudocode: gameState.phase3Reasoning,
      pythonCode: evaluationResult.converted_python || '',
      deepdive: gameState.deepDiveAnswer || gameState.deepQuizAnswer || '',
      deepdiveScenario: gameState.assignedScenario || deepQuizQuestion.value || {}
    });

    finalReport.value = await generateCompleteLearningReport(
      evaluationResults,
      getApiKey()
    );

    showMetrics.value = true;
    await nextTick();
    renderRadarChart();
  } catch (error) {
    console.error('[5D] Evaluation error:', error);
    showMetrics.value = true;
  } finally {
    isProcessing.value = false;
  }
}

async function submitPseudoEnhanced() {
  await originalSubmitPseudo();
}

function getApiKey() {
  return import.meta.env.VITE_OPENAI_API_KEY || '';
}

function renderRadarChart() {
  if (!radarChartCanvas.value || !finalReport.value) return;
  if (radarChartInstance) radarChartInstance.destroy();

  const ctx = radarChartCanvas.value.getContext('2d');
  const metrics = finalReport.value.metrics;

  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: [
        metrics.abstraction.name,
        metrics.implementation.name,
        metrics.design.name,
        metrics.edgeCase.name,
        metrics.consistency.name
      ],
      datasets: [{
        label: '?뱀떊???먯닔',
        data: [
          metrics.abstraction.percentage,
          metrics.implementation.percentage,
          metrics.design.percentage,
          metrics.edgeCase.percentage,
          metrics.consistency.percentage
        ],
        backgroundColor: 'rgba(96, 165, 250, 0.3)',
        borderColor: '#60a5fa',
        pointBackgroundColor: '#60a5fa',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#60a5fa',
        borderWidth: 3,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          ticks: { stepSize: 20, color: '#999' },
          grid: { color: '#333' },
          pointLabels: { color: '#fff', font: { size: 12 } }
        }
      },
      plugins: { 
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleColor: '#60a5fa',
            bodyColor: '#fff',
            cornerRadius: 8,
            padding: 12
          }
      },
      responsive: true,
      maintainAspectRatio: false
    }
  });
}

function getMetricColor(percentage) {
  if (percentage >= 90) return '#4ade80';
  if (percentage >= 75) return '#60a5fa';
  if (percentage >= 60) return '#fbbf24';
  return '#f87171';
}

const weakestMetricKey = computed(() => {
  if (!finalReport.value || !finalReport.value.metrics) return null;
  const metrics = finalReport.value.metrics;
  const metricKeys = ['design', 'edgeCase', 'abstraction', 'implementation', 'consistency'];
  const priorities = { design: 5, consistency: 4, edgeCase: 3, abstraction: 2, implementation: 1 };
  
  return [...metricKeys].sort((a, b) => {
    const ma = metrics[a];
    const mb = metrics[b];
    if (ma.percentage !== mb.percentage) return ma.percentage - mb.percentage;
    return (priorities[b] || 0) - (priorities[a] || 0);
  })[0];
});

function getMetricVideo(metricKey) {
  if (!metricKey || !LEARNING_RESOURCES[metricKey]) return { title: '', url: '', curationPoint: '' };
  return LEARNING_RESOURCES[metricKey].videos[0];
}

const submitPseudo = submitPseudoEnhanced;

const isInteractionPhase = computed(() => {
    const p = gameState.phase;
    return p.startsWith('DIAGNOSTIC') || 
           ['PSEUDO_WRITE', 'PYTHON_VISUALIZATION', 'EVALUATION', 'TAIL_QUESTION', 'DEEP_QUIZ'].includes(p);
});

const diagnosticProblemParts = computed(() => {
    const context = diagnosticQuestion.value.problemContext || "";
    if (!context) return null;
    const parts = context.split('\n\n');
    return { instruction: parts[0], code: parts.slice(1).join('\n\n') };
});

watch(() => gameState.phase, (newPhase) => {
    gameState.showHint = false;
    if (newPhase === 'EVALUATION' && !showTutorial.value) {
        runComprehensiveEvaluation();
    }
});

const { monacoOptions, handleMonacoMount } = useMonacoEditor(
    currentMission, 
    reactive({
        get userCode() { return gameState.phase3Reasoning; },
        set userCode(v) { gameState.phase3Reasoning = v; }
    })
);
</script>

<style scoped src="./CoduckWars.css"></style>

<style scoped>
/* [2026-02-14] 肄붾뜒 罹먮┃???대┃ ?좊룄 ?④낵 ?쒓굅 (?ъ슜???붿껌: ?섎룞 ?뚰듃留??쒓났) */
.visual-frame {
    position: relative;
    cursor: pointer;
}

@keyframes pulse-hint {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 1; }
}

@keyframes pulse-glow {
    0%, 100% { filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.3)); }
    50% { filter: drop-shadow(0 0 30px rgba(59, 130, 246, 0.7)); }
}

@keyframes loading-bar {
  0% { transform: translateX(-100%); }
  50% { transform: translateX(-20%); }
  100% { transform: translateX(0); }
}

.animate-loading-bar {
  animation: loading-bar 1.8s ease-in-out infinite;
}

.ai-analysis-simulation {
  backdrop-filter: blur(10px);
}

.visualization-p-zero {
  padding: 0 !important;
}
</style>

<style scoped>
/* 2026-02-14 ?섏젙: ?ㅻ뜑 ?좉퇋 踰꾪듉 ?ㅽ???(?쒗넗由ъ뼹, ?ㅼ뒿 醫낅즺) */
.btn-tutorial-trigger {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #f1f5f9;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.btn-tutorial-trigger:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: #3b82f6;
  color: #fff;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
}

.btn-practice-close {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f1f5f9;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.btn-practice-close:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: #ef4444;
  color: #fff;
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
}

/* [2026-02-14] ?ㅻ뜑???뚰듃 踰꾪듉 (遺됱????꾩튂) */
.btn-hint-header {
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  color: #fbbf24;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
  margin-right: 8px;
}

.btn-hint-header:hover, .btn-hint-header.is-active {
  background: rgba(251, 191, 36, 0.25);
  border-color: #f59e0b;
  color: #fff;
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.4);
}

.hint-duck-wrapper {
  position: relative !important;
  right: auto !important;
  bottom: auto !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: auto !important;
  z-index: 1000;
  cursor: pointer;
  margin-right: 15px;
  align-self: flex-end;
}

.hint-unit-img.clickable-duck {
  width: 70px;
  height: 70px;
  filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.3));
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.hint-duck-wrapper:hover .clickable-duck {
  transform: scale(1.1);
  filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.6));
}

.hint-bubble {
  position: absolute !important;
  bottom: 80px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  width: 380px !important; 
  min-width: 320px;
  margin-bottom: 0 !important;
  z-index: 1001;
  animation: bubble-bounce 0.4s ease-out;
}

.hb-tail {
  position: absolute;
  bottom: -7px;
  left: 50% !important;
  transform: translateX(-50%) rotate(45deg) !important;
  width: 14px;
  height: 14px;
  background: rgba(10, 20, 40, 0.98);
  border-right: 1.5px solid #3b82f6;
  border-bottom: 1.5px solid #3b82f6;
}

@keyframes bubble-bounce {
  0% { transform: scale(0.8) translateY(10px); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.blueprint-reference-card {
  z-index: 5;
  margin-bottom: 2rem;
}

.brc-header {
  border-bottom: none;
}

.brc-body {
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
  border-bottom-left-radius: 0.75rem;
  border-bottom-right-radius: 0.75rem;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #0f172a;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #1e293b;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #334155;
}

:deep(.btn-retry-action) {
  background: rgba(30, 41, 59, 0.6);
  border: 2px solid #3b82f6;
  color: #3b82f6;
  padding: 24px 60px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

:deep(.btn-retry-action:hover) {
  background: #3b82f6;
  color: white;
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 15px 35px rgba(59, 130, 246, 0.4);
}

.animate-slideIn {
  animation: slideInDown 0.5s ease-out;
}

@keyframes slideInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
