<template>
  <div class="progressive-problems-container">
    <!-- Header -->
    <header class="problem-header">
      <h1>🎯 Progressive Debugging Challenge</h1>
      <p class="subtitle">AI 엔지니어를 위한 단계별 디버깅 미션</p>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${(currentStep / 3) * 100}%` }"></div>
      </div>
      <div class="step-indicator">
        Step {{ currentStep }} / 3
      </div>
    </header>

    <!-- Main Content Grid -->
    <div class="main-content">
      
      <!-- Left Panel: Problem Info + Logs -->
      <div class="left-panel">
        <!-- Problem Info Card -->
        <div class="problem-info-card">
          <div class="problem-header-bar">
            <h2>{{ currentProblem.title }}</h2>
            <span class="difficulty-badge">{{ currentProblem.difficulty }}</span>
          </div>
          
          <div class="problem-scroll-area">
            <div class="problem-description">
              <h3>📝 문제 설명</h3>
              <p>{{ currentProblem.description }}</p>
            </div>

            <div class="learning-objective">
              <h3>🎓 학습 목표</h3>
              <ul>
                <li v-for="(objective, index) in currentProblem.objectives" :key="index">
                  {{ objective }}
                </li>
              </ul>
            </div>

            <div class="hint-section">
              <button @click="toggleHint" class="btn-hint">
                {{ showHint ? '힌트 숨기기' : '💡 힌트 보기' }}
              </button>
              <transition name="fade">
                <div v-if="showHint" class="hint-content">
                  <p><strong>힌트:</strong></p>
                  <ul>
                    <li v-for="(hint, index) in currentProblem.hints" :key="index">
                      {{ hint }}
                    </li>
                  </ul>
                </div>
              </transition>
            </div>

            <!-- Feedback Display -->
            <transition name="slide-up">
              <div v-if="feedback" class="feedback" :class="feedback.type">
                <h4>{{ feedback.title }}</h4>
                <p>{{ feedback.message }}</p>
              </div>
            </transition>
          </div>
        </div>

        <!-- Log Card -->
        <div class="log-info-card">
          <div class="log-header">
            <h3>📋 실행 로그</h3>
            <button @click="clearLog" class="btn-clear-log">Clear</button>
          </div>
          <div class="log-content" ref="logContent">
            <div v-if="logs.length === 0" class="log-empty">
              코드를 실행하면 로그가 여기에 표시됩니다.
            </div>
            <div v-for="(log, index) in logs" :key="index" class="log-entry" :class="log.type">
              <span class="log-timestamp">{{ log.timestamp }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
          
          <!-- Error Analysis Helper in Log Card -->
          <div class="error-helper" v-if="lastError">
            <div class="error-helper-header">🔍 에러 분석</div>
            <div class="error-body">
              <div class="error-type"><strong>{{ lastError.type }}</strong></div>
              <div class="error-desc">{{ lastError.suggestion }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Code Editor -->
      <div class="right-panel">
        <div class="code-editor-card">
          <div class="editor-header">
            <span class="file-name">📄 {{ currentProblem.fileName }}</span>
            <button @click="resetCode" class="btn-reset">↺ 초기화</button>
          </div>
          
          <textarea 
            v-model="userCode" 
            class="code-input"
            spellcheck="false"
            @input="clearFeedback"
          ></textarea>

          <div class="action-buttons">
            <button @click="runCode" class="btn-run" :disabled="isRunning">
              {{ isRunning ? '⚙️ 실행 중...' : '▶️ 코드 실행' }}
            </button>
            <button @click="submitCode" class="btn-submit">
              ✅ 정답 제출
            </button>
            <button v-if="currentStep < 3" @click="skipProblem" class="btn-skip">
              ⏭️ Skip
            </button>
          </div>
        </div>
      </div>

    </div>

    <!-- Completion Modal (Same) -->
    <transition name="modal">
      <div v-if="showCompletionModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <div class="completion-animation">🎉</div>
          <h2>축하합니다!</h2>
          <p>모든 문제를 성공적으로 해결했습니다!</p>
          <div class="stats">
            <div class="stat-item">
              <span class="stat-label">해결한 문제:</span>
              <span class="stat-value">{{ solvedProblems.length }} / 3</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">총 실행 횟수:</span>
              <span class="stat-value">{{ totalRuns }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">힌트 사용:</span>
              <span class="stat-value">{{ hintUsageCount }}회</span>
            </div>
          </div>
          <button @click="resetAllProblems" class="btn-restart">처음부터 다시 시작</button>
          <button @click="closeModal" class="btn-close-modal">닫기</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import problemData from './progressive-problems.json'

export default {
  name: 'ProgressiveProblems',
  data() {
    return {
      currentStep: 1,
      userCode: '',
      logs: [],
      showHint: false,
      isRunning: false,
      feedback: null,
      lastError: null,
      showCompletionModal: false,
      solvedProblems: [],
      totalRuns: 0,
      hintUsageCount: 0,
      problems: []
    }
  },
  
  created() {
    this.loadProblems()
  },
  
  computed: {
    currentProblem() {
      return this.problems[this.currentStep - 1]
    }
  },
  
  mounted() {
    if (this.currentProblem) {
      this.userCode = this.currentProblem.buggyCode
    }
  },
  
  methods: {
    loadProblems() {
      // Find the P1 problem set from the JSON
      const problemSetId = 'P1' 
      const selectedProblemSet = problemData.progressiveProblems.find(p => p.id === problemSetId)
      
      if (selectedProblemSet) {
        this.problems = selectedProblemSet.steps.map(step => ({
          id: step.step,
          title: `Step ${step.step}: ${step.title}`,
          difficulty: 'Lv.' + step.step,
          fileName: step.file_name,
          description: step.description,
          objectives: step.objectives,
          buggyCode: step.buggy_code,
          correctCode: step.correct_code,
          hints: step.hints,
          errorLog: step.error_log,
          successLog: step.success_log,
          solutionCheck: step.solution_check,
          errorInfo: step.error_info
        }))
        
        // Initialize user code if problems exist
        if (this.problems.length > 0) {
          this.userCode = this.problems[0].buggyCode
        }
      } else {
        console.error(`Problem set ${problemSetId} not found in JSON data.`)
      }
    },

    addLog(message, type = 'info') {
      const timestamp = new Date().toLocaleTimeString()
      this.logs.push({ timestamp, message, type })
      this.$nextTick(() => {
        this.scrollToBottom()
      })
    },
    
    scrollToBottom() {
      if (this.$refs.logContent) {
        this.$refs.logContent.scrollTop = this.$refs.logContent.scrollHeight
      }
    },
    
    clearLog() {
      this.logs = []
    },
    
    clearFeedback() {
      this.feedback = null
    },
    
    resetCode() {
      this.userCode = this.currentProblem.buggyCode
      this.clearLog()
      this.clearFeedback()
      this.lastError = null
      this.addLog('코드가 초기화되었습니다.', 'info')
    },
    
    toggleHint() {
      this.showHint = !this.showHint
      if (this.showHint) {
        this.hintUsageCount++
        this.addLog('힌트를 확인했습니다.', 'warning')
      }
    },
    
    async runCode() {
      this.isRunning = true
      this.clearFeedback()
      this.totalRuns++
      
      this.addLog('=== 코드 실행 시작 ===', 'info')
      this.addLog('코드 컴파일 중...', 'info')
      
      await this.delay(500)
      
      // Check if code still has bugs
      const hasBugs = this.checkForBugs()
      
      if (hasBugs) {
        this.addLog('', 'info')
        const errorLines = this.currentProblem.errorLog.split('\n')
        for (const line of errorLines) {
          this.addLog(line, 'error')
          await this.delay(50)
        }
        
        this.setErrorHelper()
      } else {
        await this.delay(300)
        const successLines = this.currentProblem.successLog.split('\n')
        for (const line of successLines) {
          this.addLog(line, 'success')
          await this.delay(100)
        }
        this.lastError = null
      }
      
      this.addLog('=== 실행 완료 ===', 'info')
      this.isRunning = false
    },
    
    checkForBugs() {
      const code = this.userCode.trim()
      const rules = this.currentProblem.solutionCheck
      
      if (!rules) return false
      
      if (rules.type === 'multi_condition') {
        if (rules.required_any && rules.required_any.length > 0) {
          const hasAny = rules.required_any.some(keyword => code.includes(keyword))
          if (!hasAny) return true
        }
        
        if (rules.required_all && rules.required_all.length > 0) {
          const hasAll = rules.required_all.every(keyword => code.includes(keyword))
          if (!hasAll) return true 
        }
        
        if (rules.forbidden && rules.forbidden.length > 0) {
          const hasForbidden = rules.forbidden.some(keyword => code.includes(keyword))
          if (hasForbidden) return true // Bug exists
        }
      } 
      else if (rules.type === 'regex') {
        const regex = new RegExp(rules.value, rules.flags)
        if (!regex.test(code)) return true
      }
      
      return false 
    },
    
    setErrorHelper() {
      if (this.currentProblem.errorInfo) {
        this.lastError = this.currentProblem.errorInfo
      }
    },
    
    submitCode() {
      const isCorrect = !this.checkForBugs()
      
      if (isCorrect) {
        this.feedback = {
          type: 'success',
          title: '✅ 정답입니다!',
          message: '축하합니다! 코드가 올바르게 수정되었습니다.'
        }
        
        this.addLog(`문제 ${this.currentStep} 해결 완료!`, 'success')
        this.solvedProblems.push(this.currentStep)
        
        setTimeout(() => {
          if (this.currentStep < 3) {
            this.moveToNextProblem()
          } else {
            this.showCompletionModal = true
          }
        }, 2000)
      } else {
        this.feedback = {
          type: 'error',
          title: '❌ 아직 버그가 남아있습니다',
          message: '코드를 다시 확인하고 로그를 참고하여 수정해보세요.'
        }
        
        this.addLog('제출 실패: 버그가 남아있습니다.', 'error')
      }
    },
    
    skipProblem() {
      if (confirm('이 문제를 건너뛰시겠습니까?')) {
        this.addLog(`문제 ${this.currentStep}을 건너뛰었습니다.`, 'warning')
        this.moveToNextProblem()
      }
    },
    
    moveToNextProblem() {
      this.currentStep++
      this.userCode = this.currentProblem.buggyCode
      this.clearLog()
      this.clearFeedback()
      this.showHint = false
      this.lastError = null
      
      this.addLog(`=== 문제 ${this.currentStep} 시작 ===`, 'info')
    },
    
    resetAllProblems() {
      this.currentStep = 1
      this.userCode = this.problems[0].buggyCode
      this.clearLog()
      this.clearFeedback()
      this.showHint = false
      this.lastError = null
      this.showCompletionModal = false
      this.solvedProblems = []
      this.totalRuns = 0
      this.hintUsageCount = 0
      
      this.addLog('=== 새로운 도전 시작 ===', 'info')
    },
    
    closeModal() {
      this.showCompletionModal = false
    },
    
    delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
    }
  }
}
</script>

<style scoped>
.progressive-problems-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #111827; /* Darker background for code vibe */
  padding: 1rem 2rem;
  font-family: 'Inter', sans-serif;
  color: #e5e7eb;
}

.problem-header {
  text-align: center;
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.problem-header h1 {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(to right, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #9ca3af;
  font-size: 0.9rem;
}

/* Progress Bar */
.progress-bar {
  width: 300px;
  height: 6px;
  background: #374151;
  border-radius: 3px;
  margin: 1rem auto 0.5rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #60a5fa;
  box-shadow: 0 0 10px rgba(96, 165, 250, 0.6);
  transition: width 0.3s ease;
}

.step-indicator {
  font-size: 0.9rem;
  color: #d1d5db;
  margin-top: 0.5rem;
}

/* Main Content Grid */
.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: 4fr 5fr; /* 4:5 ratio for Problem:Code */
  gap: 1.5rem;
  min-height: 0; /* Important for scroll */
  padding-bottom: 1rem;
}

/* Left Panel */
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-height: 0;
}

/* Problem Info Card */
.problem-info-card {
  background: #1f2937;
  border-radius: 12px;
  border: 1px solid #374151;
  display: flex;
  flex-direction: column;
  flex: 1; /* Grow to fill space */
  min-height: 0; /* Allow shrink */
  overflow: hidden;
}

.problem-header-bar {
  padding: 1.2rem;
  border-bottom: 1px solid #374151;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0,0,0,0.2);
}

.problem-header-bar h2 {
  font-size: 1.25rem;
  color: #f3f4f6;
  margin: 0;
}

.difficulty-badge {
  background: #374151;
  color: #60a5fa;
  padding: 0.2rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid #4b5563;
}

.problem-scroll-area {
  padding: 1.2rem;
  overflow-y: auto;
  flex: 1;
}

.problem-scroll-area::-webkit-scrollbar {
  width: 6px;
}
.problem-scroll-area::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 3px;
}

.problem-description h3, 
.learning-objective h3 {
  color: #9ca3af;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.problem-description p {
  line-height: 1.6;
  color: #e5e7eb;
  margin-bottom: 1.5rem;
}

.learning-objective ul {
  list-style: none;
  padding: 0;
  margin-bottom: 1.5rem;
}

.learning-objective li {
  padding-left: 1.2rem;
  position: relative;
  color: #d1d5db;
  margin-bottom: 0.5rem;
}
.learning-objective li::before {
  content: '▹';
  position: absolute;
  left: 0;
  color: #60a5fa;
}

/* Hint */
.btn-hint {
  width: 100%;
  background: #374151;
  border: 1px dashed #6b7280;
  color: #d1d5db;
  padding: 0.8rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-hint:hover {
  background: #4b5563;
  border-color: #9ca3af;
}

.hint-content {
  background: #422006;
  border: 1px solid #a16207;
  color: #fca5a5;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}
.hint-content p { color: #fdba74; margin-bottom: 0.5rem; }
.hint-content li { color: #fed7aa; }

/* Log Card */
.log-info-card {
  background: #000000;
  border-radius: 12px;
  border: 1px solid #374151;
  display: flex;
  flex-direction: column;
  height: 30%; /* Reduced for better problem visibility */
  min-height: 150px;
}

.log-header {
  padding: 0.8rem 1rem;
  background: #111827;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-header h3 {
  font-size: 0.9rem;
  color: #9ca3af;
  margin: 0;
}

.btn-clear-log {
  background: transparent;
  border: 1px solid #4b5563;
  color: #9ca3af;
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}
.btn-clear-log:hover { background: #374151; color: white; }

.log-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  font-family: 'Consolas', monospace;
  font-size: 0.9rem;
}

.log-content::-webkit-scrollbar { width: 8px; }
.log-content::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }

.log-entry { margin-bottom: 0.4rem; display: flex; gap: 0.8rem;}
.log-timestamp { color: #569cd6; font-size: 0.8rem; min-width: 70px; }
.log-message { word-break: break-all; white-space: pre-wrap; }

.log-entry.info .log-message { color: #e5e7eb; }
.log-entry.error .log-message { color: #f87171; }
.log-entry.success .log-message { color: #4ade80; }
.log-entry.warning .log-message { color: #fbbf24; }

.log-empty { color: #4b5563; text-align: center; margin-top: 2rem; font-style: italic; }

/* Error Helper in Log */
.error-helper {
  background: #3f1111;
  border-top: 1px solid #7f1d1d;
  padding: 0.8rem 1rem;
}
.error-helper-header { color: #f87171; font-weight: bold; font-size: 0.85rem; margin-bottom: 0.3rem;}
.error-body { display: flex; flex-direction: column; gap: 0.2rem;}
.error-type { color: #fca5a5; font-size: 0.85rem;}
.error-desc { color: #fee2e2; font-size: 0.85rem;}

/* Right Panel: Code Editor */
.right-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.code-editor-card {
  background: #1f2937;
  border-radius: 12px;
  border: 1px solid #374151;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.editor-header {
  background: #111827;
  padding: 0.4rem 1rem; /* Compact header */
  border-bottom: 1px solid #374151;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-name {
  font-family: 'Consolas', monospace;
  color: #e5e7eb;
  font-size: 0.9rem;
}

.btn-reset {
  background: #374151;
  color: #d1d5db;
  border: none;
  font-size: 0.8rem;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  cursor: pointer;
}
.btn-reset:hover { background: #4b5563; color: white; }

.code-input {
  flex: 1;
  background: #0d1117; /* GitHub Dark Dimmed code bg */
  color: #c9d1d9;
  border: none;
  padding: 1rem; /* Reduced padding */
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 1rem;
  line-height: 1.6;
  resize: none;
  outline: none;
}

.action-buttons {
  padding: 0.8rem;
  background: #1f2937;
  border-top: 1px solid #374151;
  display: flex;
  gap: 0.8rem;
}

.btn-run, .btn-submit, .btn-skip {
  padding: 0.8rem 1.2rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  flex: 1;
  transition: all 0.2s;
}

.btn-run { background: #2563eb; color: white; }
.btn-run:hover:not(:disabled) { background: #3b82f6; }
.btn-run:disabled { opacity: 0.6; cursor: wait; }

.btn-submit { background: #059669; color: white; }
.btn-submit:hover { background: #10b981; }

.btn-skip { background: #4b5563; color: white; }
.btn-skip:hover { background: #6b7280; }

/* Feedback */
.feedback {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 8px;
  animation: slideUp 0.3s ease;
}
.feedback.success { background: #064e3b; border: 1px solid #059669; color: #a7f3d0; }
.feedback.error { background: #450a0a; border: 1px solid #dc2626; color: #fecaca; }

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #1f2937;
  padding: 3rem;
  border-radius: 20px;
  text-align: center;
  border: 1px solid #374151;
  max-width: 500px;
  width: 90%;
}

.completion-animation { font-size: 4rem; margin-bottom: 1rem; animation: bounce 1s infinite; }
.stats { margin: 2rem 0; display: flex; justify-content: space-around; background: #111827; padding: 1rem; border-radius: 10px; }
.stat-item { display: flex; flex-direction: column; gap: 0.5rem; }
.stat-label { color: #9ca3af; font-size: 0.9rem; }
.stat-value { color: #e5e7eb; font-weight: bold; font-size: 1.2rem; }

h2 { margin-bottom: 10px; color: #fff;}
p { color: #9ca3af;}

.btn-restart { background: #2563eb; color: white; padding: 1rem 2rem; border-radius: 8px; border:none; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 1rem; }
.btn-close-modal { background: transparent; color: #9ca3af; border: none; cursor: pointer; }

@keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }

/* Transition Helpers */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-up-enter-active { transition: all 0.3s ease; }
.slide-up-enter-from { opacity: 0; transform: translateY(20px); }
</style>
