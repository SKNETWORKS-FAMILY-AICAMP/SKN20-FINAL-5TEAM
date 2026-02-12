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
                  <span class="speaker">문제 시나리오</span>
                  <p class="dialogue-text">"{{ ((gameState.phase.startsWith('DIAGNOSTIC') || gameState.phase === 'PSEUDO_WRITE') && currentMission.scenario) ? currentMission.scenario : (gameState.coduckMessage || '데이터 흐름을 분석 중입니다...') }}"</p>
              </div>


          </aside>

          <!-- RIGHT PANEL: DECISION ENGINE [2026-02-11] 단계별 인터랙션 영역 -->
          <section class="decision-panel relative">
              <!-- [2026-02-12] PHASE: DIAGNOSTIC (3단계 심화 진단 시스템) -->
              <div v-if="gameState.phase.startsWith('DIAGNOSTIC')" class="space-y-6">
                  <div class="system-status-text">
                      <span v-if="gameState.phase === 'DIAGNOSTIC_1'">STEP_01: CONCEPT_IDENTIFICATION</span>
                      <span v-else-if="gameState.phase === 'PSEUDO_WRITE'">STEP_02: PSEUDO_ARCHITECTURE</span>
                  </div>
                  
                  <!-- 지문 내 코드 블록 렌더링 영역 [2026-02-12] 페이즈 무관하게 컨텍스트가 있으면 표시 -->
                  <div v-if="diagnosticProblemParts" class="diagnostic-code-box">
                      <div class="diagnostic-instruction">{{ diagnosticProblemParts.instruction }}</div>
                      <div class="diagnostic-code">{{ diagnosticProblemParts.code }}</div>
                  </div>

                  <h3 v-if="gameState.phase === 'DIAGNOSTIC_1' && diagnosticQuestion1.type !== 'CHOICE'" class="big-question !mb-6">
                      {{ diagnosticQuestion1.question }}
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
                   <!-- AI 아키텍트 분석 오버레이 -->
                  <div v-if="gameState.isEvaluatingDiagnostic" class="ai-loading-overlay">
                      <LoadingDuck message="데이터 흐름 및 논리적 타당성을 정밀 분석 중입니다..." />
                  </div>
              </div>

          <!-- [2026-02-11] PHASE: PSEUDO_WRITE (Step 2: 아키텍처 설계) [2026-02-12] 폭 맞춤 및 중앙 정렬 -->
          <div v-else-if="gameState.phase === 'PSEUDO_WRITE'" class="space-y-4 flex flex-col h-full max-w-5xl mx-auto w-full">
              <!-- [2026-02-12] 이미지 싱크: 메인 타이틀 및 설명 개편 (미션/제약조건 노출) [폰트 상향 및 중복 제거] -->
              <div class="mission-instruction-compact w-full space-y-3 p-5 bg-slate-900/60 border border-slate-700/50 rounded-2xl shadow-xl">
                  <div class="mi-section">
                      <h4 class="text-blue-400 font-black text-sm tracking-widest mb-2">[미션]</h4>
                      <p class="text-slate-200 text-sm leading-relaxed">{{ currentMission.designContext?.description }}</p>
                  </div>
                  <div class="mi-section border-t border-slate-700/30 pt-4">
                      <h4 class="text-amber-400 font-black text-sm tracking-widest mb-2">[필수 포함 조건 (Constraint)]</h4>
                      <p class="text-slate-300 text-[13px] leading-relaxed whitespace-pre-line">{{ currentMission.designContext?.writingGuide?.replace('[필수 포함 조건 (Constraint)]\n', '') }}</p>
                  </div>
              </div>

              <div class="editor-layout w-full flex flex-col flex-1">
                  <div class="editor-body w-full flex-1">
                      <!-- 의사코드 입력 에디터 [2026-02-12] :value 제거하여 완전 수동 동기화로 전환 (삭제/입력 프리징 근본 해결) -->
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

                  <div class="editor-header w-full mt-4 flex justify-end">
                      <div class="tabs">
                        
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
  </div>
</template>

<script setup>
import { computed, ref, reactive, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useGameStore } from '@/stores/game';
import { useCoduckWars } from './composables/useCoduckWars.js';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';
import { useMonacoEditor } from './composables/useMonacoEditor.js';
import { 
  AlertOctagon, Info, ArrowRight, Lightbulb, 
  Code2, Play, CheckCircle, RotateCcw, Brain
} from 'lucide-vue-next';
import CodeFlowVisualizer from './components/CodeFlowVisualizer.vue';
import LoadingDuck from '../components/LoadingDuck.vue';

const router = useRouter();
const gameStore = useGameStore();

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

    toggleGuide,
    handleGuideClick,
    submitDiagnostic1,
    diagnosticQuestion1,
    submitPseudo,
    handlePythonVisualizationNext,
    handleTailSelection,
    resetFlow,
    handlePracticeClose
} = useCoduckWars();


// [2026-02-12] 지문(problemContext)을 설명부와 코드부로 분리하여 가독성 증대
const diagnosticProblemParts = computed(() => {
    const context = diagnosticQuestion1.value.problemContext || "";
    if (!context) return null;
    
    // 이중 개행(\n\n)을 기준으로 첫 단락(설명)과 나머지(코드)를 분리
    const parts = context.split('\n\n');
    return {
        instruction: parts[0],
        code: parts.slice(1).join('\n\n')
    };
});

// [2026-02-12] Monaco Editor 연동
const { monacoOptions, handleMonacoMount } = useMonacoEditor(
    currentMission, 
    reactive({
        get userCode() { return gameState.phase3Reasoning; },
        set userCode(v) { gameState.phase3Reasoning = v; }
    })
);

// --- END INTEGRATION ---


// --- END INTEGRATION ---
</script>

<style scoped src="./CoduckWars.css"></style>
