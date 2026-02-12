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

        <!-- [수정일: 2026-02-11] AI 리뷰어 랩 (Rule Lab) 버튼. 배포 시 이 버튼만 주석 처리하면 제거 가능합니다. -->
        <button class="btn-lab-toggle" @click="toggleLab" title="AI Reviewer Rule Lab">
          <Brain :class="{ 'anim-pulse': isLabOpen }" class="w-5 h-5" />
        </button>
      </div>
    </header>

    <!-- MAIN VIEWPORT [2026-02-11] UI 레이아웃 2단 구성(Battle Grid) 복원 -->
    <main class="viewport">
        
      <!-- [2026-02-11] 사이드바 가이드 버튼 -->
      <button class="btn-guide-floating" @click="toggleGuide" :class="{ 'is-open': isGuideOpen }">
          <span class="icon">?</span>
          <span class="label">CHAPTER</span>
      </button>

      <!-- [2026-02-11] 사이드바 가이드 패널 -->
      <div class="guide-sidebar" :class="{ 'sidebar-open': isGuideOpen }">
          <div class="sidebar-header">
              <span class="sh-title">MISSION CHAPTERS</span>
              <button class="sh-close" @click="toggleGuide">×</button>
          </div>
          <div class="sidebar-content">
              <!-- [2026-02-11] 미션 엔지니어링 가이드 (의사코드 작성 원칙) -->
            <div v-if="currentMission.designContext?.writingGuide" class="guide-step-card g-active mt-4">
                <div class="gs-header-row">
                    <div class="gs-icon"><Lightbulb class="w-5 h-5 text-blue-400" /></div>
                    <div class="gs-info">
                        <span class="gs-step text-blue-400">ENGINEERING_GUIDE</span>
                        <p class="gs-text">의사코드 작성 전략</p>
                    </div>
                </div>
                <div class="gs-hint-content border-blue-500/20 bg-blue-500/5 p-2 rounded-lg overflow-hidden">
                    <p class="text-[10px] text-blue-100 leading-tight whitespace-pre-line">{{ currentMission.designContext.writingGuide }}</p>
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
                      <div class="hint-label">💡 TACTICAL ADVICE</div>
                      <p class="hint-body text-[11px] leading-tight">"{{ guide.coduckMsg }}"</p>
                  </div>
              </div>
          </div>
      </div>

      <!-- [2026-02-11] 2단 레이아웃 핵심 컨테이너 (Combat Grid) -->
      <div class="combat-grid w-full h-full">
          
          <!-- LEFT PANEL: ENTITY CARD [2026-02-11] 코덕 캐릭터 및 상태창 -->
          <aside class="entity-card">
              <div class="entity-header">
                  <span class="e-type">ANALYZE_UNIT</span>
                  <span class="e-status">SYSTEM_ACTIVE</span>
              </div>

              <div class="visual-frame">
                  <!-- [2026-02-11] 코덕 캐릭터 이미지 연결 -->
                  <img src="@/assets/image/duck_det.png" alt="Coduck Detective" class="coduck-portrait" />
                  <div class="scan-overlay"></div>
                  
                  <!-- [2026-02-11] 손상 시 표시 -->
                  <div v-if="gameState.playerHP < 40" class="disconnect-tag">INTEGRITY_COMPROMISED</div>
              </div>

              <!-- [2026-02-11] 코덕 실시간 대사창 -->
              <div class="dialogue-box">
                  <span class="speaker">CODUCK_ARCHITECT</span>
                  <p class="dialogue-text">"{{ gameState.coduckMessage || '데이터 흐름을 분석 중입니다...' }}"</p>
              </div>

              <!-- [2026-02-11] 이미지 싱크: 좌측 '작성 가이드' 전술 패널 추가 (PSEUDO_WRITE 단계 전용) -->
              <div v-if="gameState.phase === 'PSEUDO_WRITE'" class="instruction-guide-panel mt-4">
                  <div class="ig-header flex items-center gap-3 mb-4">
                      <!-- [수정일: 2026-02-11] 작성가이드 폰트 및 아이콘 크기 하향 조정 -->
                      <Lightbulb class="w-6 h-6 text-blue-400" />
                      <span class="text-blue-400 font-bold tracking-wider text-xs">작성 가이드</span>
                  </div>

                  <!-- 의사코드 형식 카드 -->
                  <div class="format-card bg-blue-500/10 border border-blue-500/20 p-3 rounded-xl mb-3">
                      <p class="text-blue-200 font-bold mb-1">의사코드 형식</p>
                      <p class="text-blue-100/80 leading-tight font-mono">IF (조건) THEN 경고 형태로 작성하세요</p>
                  </div>
 
                  <!-- 검증 항목 체크리스트 (폰트 축소) -->
                  <div class="checklist-section">
                      <p class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">검증 항목</p>
                      <div class="space-y-4">
                          <div v-for="check in ruleChecklist" :key="check.id" class="checklist-item flex items-start gap-2">
                              <div class="check-circle" :class="{ 'is-checked': check.completed }">
                                  <Check v-if="check.completed" class="w-3 h-3 text-white" />
                              </div>
                              <div class="check-info">
                                  <p class="check-label text-[11px] font-bold transition-colors" :class="check.completed ? 'text-slate-200' : 'text-slate-500'">{{ check.label }}</p>
                                  <p class="check-hint text-[9px] text-slate-600 mt-1">{{ check.hint }}</p>
                              </div>
                          </div>
                      </div>
                  </div>
              </div>

              <!-- [2026-02-11] 하단 전술 로그 (가이드 패널이 없을 때만 표시하거나 하단으로 밀림) -->
              <div v-if="gameState.phase !== 'PSEUDO_WRITE'" class="tactical-console mt-6">
                  <div class="console-header">SUBSYSTEM_LOGS</div>
                  <div class="console-body">
                      <div v-for="(log, i) in gameState.systemLogs.slice(-3)" :key="i" class="log-line">
                          <span class="t-time">[{{ log.time }}]</span>
                          <span :class="'t-' + log.type.toLowerCase()">{{ log.type }}</span>
                          <span class="t-msg">{{ log.message }}</span>
                      </div>
                  </div>
              </div>
          </aside>

          <!-- RIGHT PANEL: DECISION ENGINE [2026-02-11] 단계별 인터랙션 영역 -->
          <section class="decision-panel relative">
              

              <!-- [2026-02-12] PHASE: INTRO (미션 브리핑) -->
              <div v-if="gameState.phase === 'INTRO'" class="intro-phase-container animate-fadeIn">
                  <div class="intro-card">
                      <div class="intro-visual">
                          <img :src="currentMission.character?.image || '/assets/characters/coduck.png'" alt="Mission Lead" class="mission-lead-img" />
                          <div class="visual-glow"></div>
                      </div>
                      <div class="intro-content">
                          <div class="mission-category">{{ currentMission.category }}</div>
                          <h2 class="mission-title">{{ currentMission.title }}</h2>
                          <div class="mission-desc">{{ currentMission.desc }}</div>
                          
                          <div class="incident-report mt-6">
                              <div class="ir-header"><TriangleAlert class="w-4 h-4 text-red-500" /> <span>INCIDENT_REPORT</span></div>
                              <p class="ir-text">{{ currentMission.designContext?.currentIncident }}</p>
                          </div>

                          <div class="mission-goals mt-6">
                              <div class="mg-header"><Target class="w-4 h-4 text-cyan-400" /> <span>MISSION_GOALS</span></div>
                              <ul class="mg-list">
                                  <li v-for="(card, i) in currentMission.cards" :key="i">
                                      <span class="mg-icon">{{ card.icon }}</span>
                                      <span class="mg-text">{{ card.text }}</span>
                                  </li>
                              </ul>
                          </div>

                          <button @click="startMission" class="btn-start-mission mt-8">
                              진단 프로토콜 개시 <ArrowRight class="w-5 h-5 ml-2" />
                          </button>
                      </div>
                  </div>
              </div>

              <!-- [2026-02-12] PHASE: DIAGNOSTIC (3단계 심화 진단 시스템) -->
              <div v-if="gameState.phase.startsWith('DIAGNOSTIC')" class="space-y-6">
                  <div class="system-status-text">
                      <span v-if="gameState.phase === 'DIAGNOSTIC_1'">STEP_01: CONCEPT_IDENTIFICATION</span>
                      <span v-else-if="gameState.phase === 'DIAGNOSTIC_2'">STEP_02: ARCHITECTURE_ANALYSIS</span>
                      <span v-else>STEP_03: STRATEGY_SEQUENCE</span>
                  </div>
                  
                  <!-- 지문 내 코드 블록 렌더링 영역 [2026-02-12] 페이즈 무관하게 컨텍스트가 있으면 표시 -->
                  <div v-if="diagnosticProblemParts" class="diagnostic-code-box">
                      <div class="diagnostic-instruction">{{ diagnosticProblemParts.instruction }}</div>
                      <div class="diagnostic-code">{{ diagnosticProblemParts.code }}</div>
                  </div>

                  <h3 v-if="gameState.phase === 'DIAGNOSTIC_1' ? diagnosticQuestion1.type !== 'CHOICE' : (gameState.phase === 'DIAGNOSTIC_2' ? diagnosticQuestion2.type !== 'CHOICE' : diagnosticQuestion3.type !== 'CHOICE')" class="big-question !mb-6">
                      {{ gameState.phase === 'DIAGNOSTIC_1' ? diagnosticQuestion1.question : (gameState.phase === 'DIAGNOSTIC_2' ? diagnosticQuestion2.question : diagnosticQuestion3.question) }}
                  </h3>
                  
                  <!-- [2026-02-12] PHASE 1 전용 블록 -->
                  <div v-if="gameState.phase === 'DIAGNOSTIC_1'" class="space-y-6">
                      <!-- 서술형 UI -->
                      <div v-if="diagnosticQuestion1.type === 'DESCRIPTIVE'" class="space-y-6">
                          <div v-if="gameState.diagnosticResult && !gameState.isEvaluatingDiagnostic" class="diagnostic-result-card animate-fadeIn">
                              <div class="dr-header">
                                  <span class="dr-label">AI_ARCHITECT_VERDICT</span>
                                  <span class="dr-score" :class="gameState.diagnosticResult.score >= 70 ? 'text-green-400' : 'text-yellow-400'">{{ gameState.diagnosticResult.score }} PTS</span>
                              </div>
                              <div class="dr-analysis">"{{ gameState.diagnosticResult.analysis }}"</div>
                              <div class="dr-feedback">{{ gameState.diagnosticResult.feedback }}</div>
                              <div v-if="diagnosticQuestion1.evaluationRubric?.correctAnswer" class="model-answer-box animate-fadeIn">
                                  <div class="ma-header"><Brain class="w-4 h-4 text-purple-400" /><span class="ma-label">모범 답안</span></div>
                                  <p class="ma-content">{{ diagnosticQuestion1.evaluationRubric.correctAnswer }}</p>
                              </div>
                          </div>
                          <textarea v-model="gameState.diagnosticAnswer" class="diagnostic-textarea" placeholder="분석 내용을 입력하세요..." :disabled="gameState.isEvaluatingDiagnostic"></textarea>
                          <button @click="submitDiagnostic1()" class="btn-execute-large w-full justify-center" :disabled="(!gameState.diagnosticAnswer || gameState.diagnosticAnswer.trim().length < 5) && !gameState.diagnosticResult || gameState.isEvaluatingDiagnostic">
                              <template v-if="gameState.isEvaluatingDiagnostic">분석 중... <RotateCcw class="w-5 h-5 ml-2 animate-spin" /></template>
                              <template v-else-if="gameState.diagnosticResult">다음 단계 진행 <ArrowRight class="w-5 h-5 ml-2" /></template>
                              <template v-else>분석 완료 제출 <CheckCircle class="w-5 h-5 ml-2" /></template>
                          </button>
                      </div>
                      <!-- 객관식 UI (CHOICE) [2026-02-12] 코덕 비주얼 복구 -->
                      <div v-else-if="diagnosticQuestion1.type === 'CHOICE'" class="choice-interaction-area">
                          <div class="choice-visual-frame mb-8">
                              <div class="choice-coduck">
                                  <img :src="currentMission.character?.image || '@/assets/image/duck_det.png'" alt="Coduck Interviewer" />
                              </div>
                              <div class="choice-speech-bubble">
                                  <div class="bubble-tail"></div>
                                  <p class="bubble-text">{{ diagnosticQuestion1.question }}</p>
                              </div>
                          </div>
                          <div class="options-list">
                              <div v-for="(opt, idx) in diagnosticQuestion1.options" :key="idx" @click="submitDiagnostic1(idx)" class="option-card">
                                  <div class="opt-index">{{ idx + 1 }}</div>
                                  <div class="opt-main text-lg">{{ opt.text }}</div>
                                  <div class="opt-arrow"><ArrowRight /></div>
                              </div>
                          </div>
                      </div>
                  </div>

                  <!-- [2026-02-12] PHASE 2 전용 블록 -->
                  <div v-else-if="gameState.phase === 'DIAGNOSTIC_2'" class="space-y-6">
                      <div class="previous-answer-ref">
                          <div class="ref-header"><Info class="w-3 h-3 text-cyan-400" /><span class="ref-label">PHASE 1 CONTEXT</span></div>
                          <p class="ref-content">"{{ gameState.diagnosticAnswer || '개념 파악 완료' }}"</p>
                      </div>
                      <!-- 서술형 UI -->
                      <div v-if="diagnosticQuestion2.type === 'DESCRIPTIVE'" class="space-y-6">
                          <div v-if="gameState.diagnosticResult2 && !gameState.isEvaluatingDiagnostic" class="diagnostic-result-card animate-fadeIn">
                              <div class="dr-header">
                                  <span class="dr-label">AI_ARCHITECT_VERDICT</span>
                                  <span class="dr-score" :class="gameState.diagnosticResult2.score >= 70 ? 'text-green-400' : 'text-yellow-400'">{{ gameState.diagnosticResult2.score }} PTS</span>
                              </div>
                              <div class="dr-analysis">"{{ gameState.diagnosticResult2.analysis }}"</div>
                              <div class="dr-feedback">{{ gameState.diagnosticResult2.feedback }}</div>
                          </div>
                          <textarea v-model="gameState.diagnosticAnswer2" class="diagnostic-textarea" placeholder="상세 전술을 설계하세요..." :disabled="gameState.isEvaluatingDiagnostic"></textarea>
                          <button @click="submitDiagnostic2()" class="btn-execute-large w-full justify-center" :disabled="(!gameState.diagnosticAnswer2 || gameState.diagnosticAnswer2.trim().length < 5) && !gameState.diagnosticResult2 || gameState.isEvaluatingDiagnostic">
                              <template v-if="gameState.isEvaluatingDiagnostic">검토 중... <RotateCcw class="w-5 h-5 ml-2 animate-spin" /></template>
                              <template v-else-if="gameState.diagnosticResult2">다음 단계 진행 <ArrowRight class="w-5 h-5 ml-2" /></template>
                              <template v-else>설계 결과 제출 <CheckCircle class="w-5 h-5 ml-2" /></template>
                          </button>
                      </div>
                      <!-- 객관식 UI (CHOICE) [2026-02-12] 코덕 비주얼 복구 -->
                      <div v-else-if="diagnosticQuestion2.type === 'CHOICE'" class="choice-interaction-area">
                          <div class="choice-visual-frame mb-8">
                              <div class="choice-coduck">
                                  <img src="@/assets/image/duck_det.png" alt="Coduck Interviewer" />
                              </div>
                              <div class="choice-speech-bubble">
                                  <div class="bubble-tail"></div>
                                  <p class="bubble-text">{{ diagnosticQuestion2.question }}</p>
                              </div>
                          </div>
                          <div class="options-list">
                              <div v-for="(opt, idx) in diagnosticQuestion2.options" :key="idx" @click="submitDiagnostic2(idx)" class="option-card">
                                  <div class="opt-index">{{ idx + 1 }}</div>
                                  <div class="opt-main text-lg">{{ opt.text }}</div>
                                  <div class="opt-arrow"><ArrowRight /></div>
                              </div>
                          </div>
                      </div>
                  </div>

                  <!-- [2026-02-12] PHASE 3 전용 블록 (정렬형 위주) -->
                  <div v-else-if="gameState.phase === 'DIAGNOSTIC_3'" class="space-y-6">
                      <!-- 정렬형 UI (ORDERING) -->
                      <div v-if="diagnosticQuestion3.type === 'ORDERING'" class="space-y-6">
                          <div v-if="gameState.diagnosticResult3 && !gameState.isEvaluatingDiagnostic" class="diagnostic-result-card animate-fadeIn">
                              <div class="dr-header">
                                  <span class="dr-label">SEQUENCE_VALIDATION_RESULT</span>
                                  <span class="dr-score" :class="gameState.diagnosticResult3.score >= 70 ? 'text-green-400' : 'text-yellow-400'">{{ gameState.diagnosticResult3.score }} PTS</span>
                              </div>
                              <div class="dr-analysis">"{{ gameState.diagnosticResult3.analysis }}"</div>
                              <div class="dr-feedback">{{ gameState.diagnosticResult3.feedback }}</div>
                              <div class="model-answer-section">
                                  <button @click="showModelAnswer = !showModelAnswer" class="btn-toggle-ma">
                                      <Brain class="w-4 h-4" /> {{ showModelAnswer ? '해설 숨기기' : '모범 순서 및 해설 확인' }}
                                      <ChevronDown class="w-4 h-4 transition-transform" :class="{ 'rotate-180': showModelAnswer }" />
                                  </button>
                                  <div v-if="showModelAnswer" class="model-answer-box animate-fadeIn">
                                      <p class="ma-content">{{ diagnosticQuestion3.evaluationRubric?.correctAnswer }}</p>
                                      <div v-if="diagnosticQuestion3.evaluationRubric?.modelAnswerExplanation" class="ma-explanation-box" v-html="diagnosticQuestion3.evaluationRubric.modelAnswerExplanation"></div>
                                  </div>
                              </div>
                          </div>
                          <div class="ordering-container space-y-3">
                              <button v-for="opt in diagnosticQuestion3.options" :key="opt.id" class="ordering-item" :class="{'active': gameState.diagnosticOrder3.includes(opt.id), 'correct': gameState.diagnosticResult3?.is_correct && gameState.diagnosticOrder3.includes(opt.id), 'wrong': gameState.diagnosticResult3 && !gameState.diagnosticResult3.is_correct && gameState.diagnosticOrder3.includes(opt.id)}" @click="toggleOrderingItem(opt.id)" :disabled="gameState.isEvaluatingDiagnostic || gameState.diagnosticResult3">
                                  <div class="order-parenthesis">( <span class="order-number" v-html="gameState.diagnosticOrder3.includes(opt.id) ? gameState.diagnosticOrder3.indexOf(opt.id) + 1 : '&nbsp;&nbsp;'"></span> )</div>
                                  <span class="order-text">{{ opt.text }}</span>
                              </button>
                          </div>
                          <button @click="submitDiagnostic3" class="btn-execute-large w-full justify-center" :disabled="(gameState.diagnosticOrder3.length < 4 && !gameState.diagnosticResult3) || gameState.isEvaluatingDiagnostic">
                              <template v-if="gameState.isEvaluatingDiagnostic">시퀀스 분석 중... <RotateCcw class="w-5 h-5 ml-2 animate-spin" /></template>
                              <template v-else-if="gameState.diagnosticResult3">최종 설계 진입 <ArrowRight class="w-5 h-5 ml-2" /></template>
                              <template v-else>순서 검증 제출 <CheckCircle class="w-5 h-5 ml-2" /></template>
                          </button>
                      </div>
                      <!-- 객관식 UI (CHOICE) [2026-02-12] 코덕 비주얼 복구 -->
                      <div v-else-if="diagnosticQuestion3.type === 'CHOICE'" class="choice-interaction-area">
                          <div class="choice-visual-frame mb-8">
                              <div class="choice-coduck">
                                  <img src="@/assets/image/duck_det.png" alt="Coduck Interviewer" />
                              </div>
                              <div class="choice-speech-bubble">
                                  <div class="bubble-tail"></div>
                                  <p class="bubble-text">{{ diagnosticQuestion3.question }}</p>
                              </div>
                          </div>
                          <div class="options-list">
                              <div v-for="(opt, idx) in diagnosticQuestion3.options" :key="idx" @click="submitDiagnostic3(idx)" class="option-card">
                                  <div class="opt-index">{{ idx + 1 }}</div>
                                  <div class="opt-main text-lg">{{ opt.text }}</div>
                                  <div class="opt-arrow"><ArrowRight /></div>
                              </div>
                          </div>
                      </div>
                  </div>

                  <!-- AI 아키텍트 분석 오버레이 -->
                  <div v-if="gameState.isEvaluatingDiagnostic" class="ai-loading-overlay">
                      <LoadingDuck message="데이터 흐름 및 논리적 타당성을 정밀 분석 중입니다..." />
                  </div>
              </div>

          <!-- [2026-02-11] PHASE: PSEUDO_WRITE (Step 2: 아키텍처 설계) -->
          <div v-else-if="gameState.phase === 'PSEUDO_WRITE'" class="space-y-4 flex flex-col h-full">
              <!-- [2026-02-11] 이미지 싱크: 메인 타이틀 및 설명 개편 -->
              <div class="text-center space-y-1 mb-2">
                  <h3 class="text-xl font-black text-white">{{ currentMission.designContext?.title || 'AI 리뷰어 검증 규칙 설계' }}</h3>
                  <p class="text-slate-400 text-xs leading-tight">{{ currentMission.designContext?.description || '아래 코드에서 데이터 누수가 발생하는 부분을 찾고, 이를 자동 감지할 수 있는 의사코드 규칙을 작성하세요.' }}</p>
              </div>
              
              <!-- [2026-02-11] 이미지 싱크: 사고 코드 블록 고도화 (Header-Code-Footer 구조) -->
              <div v-if="currentMission.designContext?.incidentCode" class="incident-review-block incident-image-sync">
                  <div class="irs-header">
                      <p class="text-[10px] font-bold text-red-400 uppercase">막아야 할 패턴</p>
                  </div>
                  <div class="irs-body">
                      <pre class="text-emerald-400 text-xs font-mono leading-tight whitespace-pre-wrap">{{ currentMission.designContext.incidentCode }}</pre>
                      
                      <!-- [2026-02-11] '문제' 설명 국문 축소 -->
                      <p v-if="currentMission.designContext?.incidentProblem" class="irs-problem mt-2 text-[11px]">
                        <strong class="text-red-400">문제:</strong> {{ currentMission.designContext.incidentProblem }}
                      </p>
                  </div>
              </div>

              <div class="editor-layout">
                  <div class="editor-header">
                      <div class="tabs">
                          <button class="tab active">
                              <Code2 class="w-4 h-4 mr-2" />
                              의사코드 작성
                          </button>
                      </div>
                      <div class="actions">
                          <button 
                              :disabled="!canSubmitPseudo || isProcessing"
                              @click="submitPseudo"
                              class="btn-execute-large"
                          >
                              심화 분석 시작 <Play class="w-4 h-4" />
                          </button>
                      </div>
                  </div>
                  
                  <div class="editor-body">
                      <!-- 의사코드 입력 에디터 -->
                      <div class="monaco-wrapper flex-1 max-h-[270px]">
                          <div class="line-numbers">
                              <span v-for="n in 15" :key="n">{{ n }}</span>
                          </div>
                          <textarea 
                              v-model="gameState.phase3Reasoning"
                              @input="handlePseudoInput"
                              class="monaco-textarea w-full"
                              placeholder="예시:

IF 코드에 'scaler.fit(' 또는 'encoder.fit(' 패턴이 있음
AND 그 이전 줄에 'train_test_split' 또는 '[: 슬라이싱]'이 없음
THEN
    경고: '분할 전 통계량 산출 감지'
    설명: 'Test 데이터 통계량이 Train 학습에 영향을 줍니다'
    해결책: 'Train/Test 분할 후 scaler.fit(X_train)으로 변경하세요'"
                              spellcheck="false"
                          ></textarea>
                      </div>
                      
                      <!-- 실시간 가이드라인 체크리스트 -->
                  </div>
              </div>
          </div>

        <!-- [STEP 3] Python 시각화 및 분기 단계 -->
        <section v-else-if="gameState.phase === 'PYTHON_VISUALIZATION'" class="visualization-phase">
            <CodeFlowVisualizer
                :python-code="evaluationResult?.converted_python"
                :score="evaluationResult?.overall_score"
                :feedback="evaluationResult?.python_feedback"
                @next="handlePythonVisualizationNext"
            />
        </section>

        <!-- [STEP 3-1] Tail Question 단계 (80점 미만) -->
        <section v-else-if="gameState.phase === 'TAIL_QUESTION'" class="tail-question-phase">
            <div class="tail-question-area">
                <div class="tq-header">
                    <span class="tq-icon">💡</span>
                    <span class="tq-title">개념 보완이 필요해요 (Score: {{ evaluationResult?.overall_score }})</span>
                </div>
                
                <div class="tq-content">
                    {{ deepQuizQuestion?.question }}
                </div>
                
                <div class="tq-options">
                    <button 
                        v-for="(option, idx) in deepQuizQuestion?.options" 
                        :key="idx"
                        @click="handleTailSelection(option)"
                        class="btn-tq-option"
                    >
                        {{ option.text }}
                    </button>
                </div>
            </div>
        </section>

        <!-- [STEP 3-2] Deep Dive 단계 (80점 이상) -->
        <section v-else-if="gameState.phase === 'DEEP_QUIZ'" class="deep-dive-phase">
             <!-- 기존 Deep Dive UI 유지 또는 개선 -->
             <div class="deep-dive-container">
                <h3>🚀 심화 학습 (Deep Dive)</h3>
                <!-- Deep Dive 컴포넌트나 내용 -->
             </div>
        </section>

          <!-- [STEP 4] 최종 리포트 (EVALUATION) -->
        <section v-else-if="gameState.phase === 'EVALUATION'" class="evaluation-phase">
            <div class="report-card">
                <div class="report-header">
                    <h2>MISSION REPORT</h2>
                    <div class="total-score">
                        <span class="score-val">{{ evaluationResult?.overall_score || 0 }}</span>
                        <span class="score-label">TOTAL SCORE</span>
                    </div>
                </div>

                <div class="score-breakdown">
                    <!-- Rule-based Score (40%) -->
                    <div class="score-item rule-score">
                        <div class="si-label">RULE ADHERENCE (40%)</div>
                        <div class="progress-bar">
                            <div class="fill" :style="{ width: (evaluationResult?.rule_score || 0) + '%' }"></div>
                        </div>
                        <span class="si-val">{{ evaluationResult?.rule_score || 0 }}/40</span>
                    </div>

                    <!-- AI Metric Score (60%) -->
                    <div class="score-item ai-score">
                        <div class="metrics-grid">
                            <div v-for="(dim, key) in evaluationResult?.dimensions" :key="key" class="metric-box">
                                <span class="m-label">{{ key.toUpperCase() }}</span>
                                <span class="m-score">{{ dim.score }}/12</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mentor-feedback">
                    <h3>🤖 AI MENTOR FEEDBACK</h3>
                    <p class="feedback-text">"{{ evaluationResult?.strengths?.[0] || '분석 결과가 없습니다.' }}"</p>
                    <p class="feedback-sub" v-if="evaluationResult?.weaknesses?.[0]">
                        보완점: {{ evaluationResult?.weaknesses[0] }}
                    </p>
                </div>
                
                <div class="actions">
                    <button @click="resetFlow" class="btn-restart">
                        <RotateCcw class="w-4 h-4 mr-2" /> RESTART MISSION
                    </button>
                    <button @click="handlePracticeClose" class="btn-close">
                        MISSION COMPLETE
                    </button>
                </div>
            </div>
        </section>
          </section>
      </div>
    </main>

    <!-- [2026-02-11] FEEDBACK TOAST -->
    <div v-if="gameState.feedbackMessage && gameState.phase !== 'EVALUATION'" class="feedback-toast">
      <span class="toast-icon">!</span> {{ gameState.feedbackMessage }}
    </div>

    <!-- [수정일: 2026-02-11] AI 리뷰어 실험실 (Rule Lab) 오버레이 -->
    <!-- 나중에 기능 제거 시 아래 transition 블록 전체를 삭제하면 됩니다. -->
    <transition name="lab-slide">
      <div v-if="isLabOpen" class="ai-reviewer-lab-overlay">
        <div class="lab-window">
          <header class="lab-header">
            <div class="lh-left">
              <Brain class="text-emerald-400 w-6 h-6" />
              <h2 class="lh-title">AI REVIEWER_RULE_LAB <span class="text-[10px] opacity-40 ml-2">VERIFICATION_SANDBOX</span></h2>
            </div>
            <div class="flex items-center gap-4">
              <div class="lab-tabs">
                <button v-for="tab in ['RULES', 'GUIDE', 'TEST']" :key="tab" 
                        @click="activeLabTab = tab" 
                        :class="{ 'active': activeLabTab === tab }" class="lab-tab-btn">{{ tab }}</button>
              </div>
              <button class="lh-close" @click="toggleLab">×</button>
            </div>
          </header>

          <div class="lab-container">
            <!-- TAB 1: RULES (JSON) -->
            <div v-if="activeLabTab === 'RULES'" class="lab-full-section">
              <div class="sec-header">
                <Code2 class="w-4 h-4" /> <span>AI 정밀 평가 규칙 (JSON)</span>
              </div>
              <div class="json-editor-wrapper">
                <textarea v-model="labState.jsonRules" @input="onLabJsonInput" class="lab-json-textarea" spellcheck="false"></textarea>
                <div v-if="labState.jsonError" class="json-error-msg"><AlertOctagon class="w-3 h-3" /> {{ labState.jsonError }}</div>
              </div>
              <div class="sec-footer">
                <p class="text-[11px] text-slate-500">※ criticalPatterns 및 requiredConcepts의 정규식을 수정하여 AI의 감점/가점 기준을 제어합니다.</p>
                <button @click="applyLabData('rules')" :disabled="!!labState.jsonError" class="btn-apply-lab">규칙 즉시 적용</button>
              </div>
            </div>

            <!-- TAB 2: GUIDE (Instruction Panel) -->
            <div v-if="activeLabTab === 'GUIDE'" class="lab-full-section">
              <div class="sec-header">
                <Lightbulb class="w-4 h-4" /> <span>인스트럭션 가이드 소스 수정</span>
              </div>
              <div class="lab-guide-grid">
                <div class="guide-edit-box">
                  <label class="lab-label">의사코드 작성 원칙 (Writing Guide)</label>
                  <textarea v-model="labState.writingGuide" class="lab-guide-textarea"></textarea>
                </div>
                <div class="guide-edit-box">
                  <label class="lab-label">체크리스트 편집 (Checklist JSON)</label>
                  <textarea v-model="labState.checklistJson" @input="onChecklistJsonInput" class="lab-json-textarea text-[12px]"></textarea>
                  <div v-if="labState.checklistError" class="json-error-msg bottom-[-25px]"><AlertOctagon class="w-3 h-3" /> {{ labState.checklistError }}</div>
                </div>
              </div>
              <div class="sec-footer mt-auto">
                <p class="text-[11px] text-slate-500">※ 가이드 문구와 체크리스트 정규식을 변경하여 학습자에게 제공되는 실시간 피드백을 조정합니다.</p>
                <button @click="applyLabData('guide')" :disabled="!!labState.checklistError" class="btn-apply-lab">가이드 즉시 반영</button>
              </div>
            </div>

            <!-- TAB 3: TEST (Sandbox) -->
            <div v-if="activeLabTab === 'TEST'" class="lab-full-section flex-row gap-8">
              <div class="flex-1 flex flex-col">

                <div class="sec-header"><Play class="w-4 h-4" /> <span>테스트 로직 입력</span></div>
                <textarea v-model="labState.testInput" class="lab-test-textarea flex-1 mb-4" placeholder="검증할 의사코드를 입력하세요..."></textarea>
                <button @click="runLabTest" :disabled="labState.isTesting" class="btn-run-test w-full">
                  <Brain class="w-4 h-4" /> 샌드박스 검증 실행
                </button>
              </div>
              <div class="flex-1 flex flex-col">
                <div class="sec-header"><BarChart3 class="w-4 h-4" /> <span>실시간 분석 결과</span></div>
                <div class="test-result-group flex-1">
                   <div v-if="labState.testResult" class="result-body">
                      <div class="result-score-row">
                        <div class="rs-item"><span class="rs-label">SCORE</span><span class="rs-val" :class="getScoreColor(labState.testResult.score)">{{ labState.testResult.score }}점</span></div>
                        <div class="rs-item"><span class="rs-label">PASSED</span><span class="rs-val" :class="labState.testResult.passed ? 'text-emerald-400' : 'text-red-400'">{{ labState.testResult.passed ? 'YES' : 'NO' }}</span></div>
                      </div>
                      <div class="result-detail-list">
                        <div v-for="(err, i) in labState.testResult.criticalErrors" :key="i" class="rd-item is-error">
                          <AlertOctagon class="w-4 h-4" /> <p class="rd-msg">{{ err.message }}</p>
                        </div>
                        <div v-for="(warn, i) in labState.testResult.warnings" :key="i" class="rd-item is-warn">
                          <Info class="w-4 h-4" /> <p class="rd-msg">{{ warn }}</p>
                        </div>
                      </div>
                   </div>
                   <div v-else class="result-placeholder"><Brain class="w-12 h-12 opacity-10" /><p>로직을 입력하고 검증을 시작하세요.</p></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { computed, ref, reactive, onMounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useGameStore } from '@/stores/game';
import { useCoduckWars } from './composables/useCoduckWars.js';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import { useMonacoEditor } from './composables/useMonacoEditor.js';
import { 
  AlertOctagon, Info, ArrowRight, Lightbulb, Check, 
  Code2, Play, CheckCircle, Brain, BarChart3, RotateCcw, ChevronDown,
  TriangleAlert, Target
} from 'lucide-vue-next';
import CodeFlowVisualizer from './components/CodeFlowVisualizer.vue';
import LoadingDuck from '../components/LoadingDuck.vue';

const router = useRouter();
const gameStore = useGameStore();

const {
    gameState,
    currentMission,
    runnerState,
    evaluationResult,
    deepQuizQuestion,
    isEvaluating,
    pythonSnippets,
    ruleChecklist,
    completedChecksCount,
    allChecksPassed,
    canSubmitPseudo,
    isProcessing,
    isGuideOpen,
    selectedGuideIdx,
    showModelAnswer,

    toggleGuide,
    handleGuideClick,
    submitDiagnostic1,
    submitDiagnostic2,
    submitDiagnostic3,
    startMission, // [2026-02-12] 추가
    toggleOrderingItem,
    diagnosticQuestion1,
    diagnosticQuestion2,
    diagnosticQuestion3,
    handlePseudoInput,
    submitDeepQuiz,
    submitPseudo,
    handlePythonVisualizationNext,
    handleTailSelection, // [Import]
    resetFlow,
    handlePracticeClose
} = useCoduckWars();


// [2026-02-12] 지문(problemContext)을 설명부와 코드부로 분리하여 가독성 증대
const diagnosticProblemParts = computed(() => {
    // 모든 진단 프로퍼티가 동일한 문항을 가리키므로 diagnosticQuestion1 유지 (또는 currentDiagnosticQuestion)
    const context = diagnosticQuestion1.value.problemContext || "";
    if (!context) return null;
    
    // 이중 개행(\n\n)을 기준으로 첫 단락(설명)과 나머지(코드)를 분리
    const parts = context.split('\n\n');
    return {
        instruction: parts[0],
        code: parts.slice(1).join('\n\n')
    };
});

// --- Functions for missing refs in template ---
const restartMission = () => resetFlow();

const radarPoints = computed(() => {
    if (!evaluationResult?.details || evaluationResult.details.length === 0) return "";
    
    // Fixed Order for Radar Chart (Standardized 5-Dim)
    const fixedCategories = ['Consistency', 'Abstraction', 'Exception Handling', 'Implementation', 'Design'];
    
    const scores = fixedCategories.map(cat => {
        // Find matching category (handle potential space nuances)
        const found = evaluationResult.details.find(d => 
            d.category === cat || d.category === cat.replace(' ', '')
        );
        return found ? found.score : 0;
    });

    return scores.map((score, i) => {
        const p = calculatePoint(i, score);
        return `${p.x},${p.y}`;
    }).join(' ');
});

// Helper for Radar Chart
const calculatePoint = (index, value) => {
    const angle = (Math.PI * 2) / 5 * index - (Math.PI / 2);
    const radius = (value / 100) * 80;
    return {
        x: 100 + radius * Math.cos(angle),
        y: 100 + radius * Math.sin(angle)
    };
};

const calculatePentagonPoints = (radius) => {
    return Array.from({length: 5}).map((_, i) => {
        const p = calculatePoint(i, (radius / 80) * 100);
        return `${p.x},${p.y}`;
    }).join(' ');
};

// --- AI 리뷰어 실험실 (Rule Lab) 로직 [수정일: 2026-02-11] ---
const isLabOpen = ref(false);
const activeLabTab = ref('RULES');
const labState = reactive({
    jsonRules: '',
    jsonError: null,
    writingGuide: '',
    checklistJson: '',
    checklistError: null,
    testInput: '',
    testResult: null,
    isTesting: false
});

const toggleLab = () => {
    if (!isLabOpen.value) {
        // 미션의 현재 상태 로드
        const mission = currentMission.value;
        const validation = mission.designContext?.validation || {};
        labState.jsonRules = JSON.stringify(validation, (k, v) => v instanceof RegExp ? v.toString() : v, 2);
        labState.writingGuide = mission.designContext?.writingGuide || '';
        
        // Checklist도 JSON으로 편집 가능하게 변환
        const checklist = ruleChecklist.value || [];
        labState.checklistJson = JSON.stringify(checklist, (k, v) => v instanceof RegExp ? v.toString() : v, 2);
        
        labState.testInput = gameState.phase3Reasoning || '';
    }
    isLabOpen.value = !isLabOpen.value;
};

const onLabJsonInput = () => {
    try { JSON.parse(labState.jsonRules); labState.jsonError = null; }
    catch (e) { labState.jsonError = "JSON 형식이 올바르지 않습니다."; }
};

const onChecklistJsonInput = () => {
    try { JSON.parse(labState.checklistJson); labState.checklistError = null; }
    catch (e) { labState.checklistError = "Checklist JSON 형식이 올바르지 않습니다."; }
};

const applyLabData = (type) => {
    try {
        const reviver = (k, v) => {
            if (typeof v === 'string' && v.startsWith('/') && v.lastIndexOf('/') > 0) {
                try {
                    const parts = v.match(/\/(.*)\/(.*)/);
                    if (parts) return new RegExp(parts[1], parts[2]);
                } catch (e) {
                    console.warn('[Validator] Failed to parse regex:', v);
                    return v; // Return as string if parsing fails
                }
            }
            return v;
        };

        if (type === 'rules') {
            const parsed = JSON.parse(labState.jsonRules, reviver);
            if (currentMission.value.designContext) {
                currentMission.value.designContext.validation = parsed;
            }
        } else if (type === 'guide') {
            if (currentMission.value.designContext) {
                currentMission.value.designContext.writingGuide = labState.writingGuide;
            }
            const parsedChecklist = JSON.parse(labState.checklistJson, reviver);
            // useCoduckWars에서 관리하는 ruleChecklist에 반영
            ruleChecklist.value = parsedChecklist;
        }
        
        gameStore.addSystemLog(`실험실 데이터(${type.toUpperCase()})가 즉시 적용되었습니다.`, "SUCCESS");
        gameState.feedbackMessage = `✅ ${type.toUpperCase()} 업데이트 완료`;
    } catch (e) {
        alert("적용 중 오류 발생: " + e.message);
    }
};

const runLabTest = async () => {
    if (labState.isTesting) return;
    labState.isTesting = true;
    try {
        const { PseudocodeValidator } = await import('./utils/PseudocodeValidator.js');
        const reviver = (k, v) => {
            if (typeof v === 'string' && v.startsWith('/') && v.lastIndexOf('/') > 0) {
                const parts = v.match(/\/(.*)\/(.*)/);
                if (parts) return new RegExp(parts[1], parts[2]);
            }
            return v;
        };
        const mockMission = {
            ...currentMission.value,
            validation: JSON.parse(labState.jsonRules, reviver)
        };
        const validator = new PseudocodeValidator(mockMission);
        labState.testResult = validator.validate(labState.testInput);
    } catch (e) {
        console.error("Sandbox Test Error:", e);
    } finally { labState.isTesting = false; }
};

const getScoreColor = (s) => (s >= 80 ? 'text-emerald-400' : s >= 50 ? 'text-amber-400' : 'text-red-400');
// --- END Rule Lab Logic ---

// --- END INTEGRATION ---
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
/* [2026-02-12] 파일명 변경: monaco-styles.css -> CoduckWars.css */
@import './CoduckWars.css';

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
/* [2026-02-12] 중복 스타일 제거 함으로써 CoduckWars.css의 전술적 레이아웃 설정이 우선 적용되도록 함 */
/* .combat-grid, .entity-card, .visual-frame, .coduck-portrait 등은 CoduckWars.css에서 관리 */

.hp-bar-bg {
    width: 15vw; /* Relative width */
    max-width: 250px;
    min-width: 100px;
    height: 10px;
    background: #1f2937;
    border-radius: 4px;
    overflow: hidden;
}

/* [2026-02-12] INTRO Phase Styles */
  .intro-phase-container {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100%;
      padding: 20px;
  }

  .intro-card {
      background: rgba(15, 23, 42, 0.8);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(59, 130, 246, 0.2);
      border-radius: 32px;
      display: flex;
      max-width: 900px;
      width: 100%;
      overflow: hidden;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 50px rgba(59, 130, 246, 0.1);
  }

  .intro-visual {
      flex: 0 0 350px;
      position: relative;
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 40px;
  }

  .mission-lead-img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      z-index: 2;
      filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.3));
  }

  .visual-glow {
      position: absolute;
      width: 200px;
      height: 200px;
      background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 70%);
      border-radius: 50%;
      z-index: 1;
      animation: pulse 4s infinite;
  }

  .intro-content {
      flex: 1;
      padding: 50px;
      display: flex;
      flex-direction: column;
  }

  .mission-category {
      font-size: 11px;
      font-weight: 800;
      color: #3b82f6;
      text-transform: uppercase;
      letter-spacing: 0.2em;
      margin-bottom: 8px;
  }

  .mission-title {
      font-size: 32px;
      font-weight: 950;
      color: white;
      margin-bottom: 16px;
      line-height: 1.2;
  }

  .mission-desc {
      font-size: 15px;
      color: #94a3b8;
      line-height: 1.6;
  }

  .incident-report {
      background: rgba(239, 68, 68, 0.05);
      border-left: 3px solid #ef4444;
      padding: 16px 20px;
      border-radius: 0 12px 12px 0;
  }

  .ir-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11px;
      font-weight: 800;
      color: #ef4444;
      margin-bottom: 8px;
  }

  .ir-text {
      font-size: 13px;
      color: #f1f5f9;
      line-height: 1.5;
  }

  .mission-goals {
      background: rgba(34, 211, 238, 0.05);
      padding: 16px 20px;
      border-radius: 12px;
  }

  .mg-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11px;
      font-weight: 800;
      color: #22d3ee;
      margin-bottom: 12px;
  }

  .mg-list {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      list-style: none;
      padding: 0;
  }

  .mg-list li {
      display: flex;
      align-items: center;
      gap: 8px;
  }

  .mg-text {
      font-size: 12px;
      color: #cbd5e1;
      line-height: 1.5;
  }

  .btn-start-mission {
      background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
      color: white;
      border: none;
      padding: 18px 32px;
      border-radius: 16px;
      font-weight: 800;
      font-size: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
      box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
  }

  .btn-start-mission:hover {
      transform: translateY(-5px) scale(1.02);
      box-shadow: 0 15px 30px rgba(59, 130, 246, 0.4);
      filter: brightness(1.1);
  }

  .btn-start-mission:active {
      transform: translateY(-2px);
  }

  @keyframes pulse {
      0%, 100% { transform: scale(1); opacity: 0.2; }
      50% { transform: scale(1.5); opacity: 0.4; }
  }

  @media (max-width: 1024px) {
      .intro-card { flex-direction: column; }
      .intro-visual { flex: 0 0 250px; }
      .intro-content { padding: 30px; }
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
/* .visual-frame, .coduck-portrait, .dialogue-box 등은 monaco-styles.css에서 통합 관리 (2026-02-11) */


/* .decision-panel, .big-question, .options-list, .option-card 등은 monaco-styles.css에서 통합 관리 (2026-02-11) */
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

/* [STEP 4] Evaluation UI Styles */
.evaluation-phase {
  width: 100%;
  height: 100%;
  padding: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  position: absolute;
  top: 0;
  left: 0;
  z-index: 50;
}

.report-card {
  width: 800px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #334155;
  padding-bottom: 20px;
}

.report-header h2 {
  font-size: 2rem;
  font-weight: 900;
  color: #fff;
  letter-spacing: -0.05em;
  margin: 0;
}

.total-score {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.total-score .score-val {
  font-size: 3rem;
  font-weight: 900;
  color: #10b981;
  line-height: 1;
}

.total-score .score-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.1em;
}

.score-breakdown {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 30px;
}

.score-item {
  background: #1e293b;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #334155;
}

.si-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #94a3b8;
  margin-bottom: 15px;
  letter-spacing: 0.05em;
}

.rule-score .progress-bar {
  height: 24px;
  background: #334155;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 10px;
}

.rule-score .fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  transition: width 1s ease-out;
}

.si-val {
  font-size: 1.5rem;
  font-weight: 800;
  color: #fff;
  display: block;
  text-align: right;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.metric-box {
  background: #0f172a;
  padding: 10px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid #334155;
}

.m-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 5px;
}

.m-score {
  font-size: 1.2rem;
  font-weight: 800;
  color: #10b981;
}

.mentor-feedback {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  padding: 25px;
  border-radius: 12px;
}

.mentor-feedback h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #10b981;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.feedback-text {
  font-size: 1.1rem;
  color: #fff;
  font-style: italic;
  line-height: 1.6;
  margin: 0;
}

.feedback-sub {
  font-size: 0.9rem;
  color: #94a3b8;
  margin-top: 10px;
}

.actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
}

.btn-restart, .btn-close {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
}

.btn-restart {
  background: #334155;
  color: #fff;
  border: none;
}

.btn-restart:hover {
  background: #475569;
}

.btn-close {
  background: #10b981;
  color: #0f172a;
  border: none;
}

.btn-close:hover {
  background: #34d399;
}
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

/* .monaco-wrapper, .line-numbers, .monaco-textarea, .action-bar-bottom 등은 monaco-styles.css에서 통합 관리 (2026-02-11) */

/* [수정일: 2026-02-11] AI REVIEWER LAB STYLES (Premium Interface) */
.btn-lab-toggle {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #10b981;
  padding: 10px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 20px;
}
.btn-lab-toggle:hover {
  background: rgba(16, 185, 129, 0.2);
  transform: scale(1.1) rotate(10deg);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.ai-reviewer-lab-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(20px);
  z-index: 5000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2vw;
}

.lab-window {
  width: 95vw;
  max-width: 1400px;
  height: 90vh;
  background: #0d0d0f;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow: 0 50px 100px -20px rgba(0, 0, 0, 0.9);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.lab-header {
  padding: 25px 40px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.lh-title { font-weight: 900; letter-spacing: 3px; font-size: 1.2rem; color: #fff; text-shadow: 0 0 20px rgba(74, 222, 128, 0.3); }

.lab-tabs { display: flex; gap: 8px; background: #000; padding: 4px; border-radius: 10px; border: 1px solid #222; }
.lab-tab-btn {
  padding: 8px 20px; border: none; background: none; color: #555; font-weight: 800; font-size: 0.75rem;
  border-radius: 6px; cursor: pointer; transition: all 0.3s;
}
.lab-tab-btn.active { background: #111; color: #4ade80; box-shadow: 0 0 10px rgba(74, 222, 128, 0.1); }

.lab-container { flex: 1; overflow: hidden; display: flex; }
.lab-full-section { flex: 1; padding: 40px; display: flex; flex-direction: column; animation: lab-fade-in 0.4s ease; }

.sec-header { display: flex; align-items: center; gap: 12px; color: #64748b; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; margin-bottom: 25px; letter-spacing: 1px; }

.json-editor-wrapper { flex: 1; position: relative; margin-bottom: 25px; }
.lab-json-textarea {
  width: 100%; height: 100%; background: #050505; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px;
  padding: 25px; color: #4ade80; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; resize: none; outline: none; line-height: 1.6;
}

.lab-guide-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; flex: 1; }
.guide-edit-box { display: flex; flex-direction: column; gap: 12px; }
.lab-label { font-size: 0.75rem; font-weight: 900; color: #94a3b8; }
.lab-guide-textarea {
  flex: 1; background: #050505; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px;
  padding: 20px; color: #e2e8f0; font-size: 0.95rem; line-height: 1.7; resize: none; outline: none;
}

.btn-apply-lab {
  padding: 16px 32px; background: #4ade80; color: #000; font-weight: 900; font-size: 0.9rem;
  border-radius: 12px; cursor: pointer; border: none; transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1);
}
.btn-apply-lab:hover:not(:disabled) { transform: translateY(-4px); box-shadow: 0 15px 30px rgba(74, 222, 128, 0.3); }

.btn-run-test {
  padding: 16px; background: #111; color: #fff; font-weight: 900; border: 1px solid #333;
  border-radius: 14px; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; justify-content: center; gap: 12px;
}

.test-result-group { background: #000; border-radius: 20px; border: 1px solid #1a1a1a; overflow-y: auto; }

.anim-pulse { animation: lab-glow 2s infinite ease-in-out; }
@keyframes lab-glow { 0%, 100% { filter: brightness(1); } 50% { filter: brightness(1.5) drop-shadow(0 0 10px #4ade80); } }
@keyframes lab-fade-in { from { opacity: 0; transform: scale(0.99); } to { opacity: 1; transform: scale(1); } }

.lab-slide-enter-active, .lab-slide-leave-active { transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1); }
.lab-slide-enter-from, .lab-slide-leave-to { opacity: 0; transform: translateY(40px) scale(0.95); }


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
