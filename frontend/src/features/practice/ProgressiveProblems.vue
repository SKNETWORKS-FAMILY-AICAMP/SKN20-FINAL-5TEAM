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

    <!-- Problem Display -->
    <div class="main-content">
      <div class="problem-section">
        <div class="problem-card">
          <div class="problem-header-bar">
            <h2>{{ currentProblem.title }}</h2>
            <span class="difficulty-badge">{{ currentProblem.difficulty }}</span>
          </div>
          
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

          <div class="code-section">
            <h3>💻 버그가 있는 코드</h3>
            <div class="code-editor">
              <div class="editor-header">
                <span class="file-name">{{ currentProblem.fileName }}</span>
                <button @click="resetCode" class="btn-reset">초기화</button>
              </div>
              <textarea 
                v-model="userCode" 
                class="code-input"
                spellcheck="false"
                @input="clearFeedback"
              ></textarea>
            </div>
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

          <div class="action-buttons">
            <button @click="runCode" class="btn-run" :disabled="isRunning">
              {{ isRunning ? '실행 중...' : '▶️ 코드 실행' }}
            </button>
            <button @click="submitCode" class="btn-submit">
              ✅ 정답 제출
            </button>
            <button v-if="currentStep < 3" @click="skipProblem" class="btn-skip">
              ⏭️ 건너뛰기
            </button>
          </div>

          <!-- Feedback -->
          <transition name="slide-up">
            <div v-if="feedback" class="feedback" :class="feedback.type">
              <h4>{{ feedback.title }}</h4>
              <p>{{ feedback.message }}</p>
            </div>
          </transition>
        </div>
      </div>

      <!-- Log Display -->
      <div class="log-section">
        <div class="log-card">
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
        </div>

        <!-- Error Analysis Helper -->
        <div class="error-helper" v-if="lastError">
          <h3>🔍 에러 분석 도움말</h3>
          <div class="error-type">
            <strong>에러 타입:</strong> {{ lastError.type }}
          </div>
          <div class="error-description">
            <strong>설명:</strong> {{ lastError.description }}
          </div>
          <div class="error-suggestion">
            <strong>해결 방향:</strong> {{ lastError.suggestion }}
          </div>
        </div>
      </div>
    </div>

    <!-- Completion Modal -->
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
    this.userCode = this.currentProblem.buggyCode
  },
  
  methods: {
    loadProblems() {
      // Find the P1 problem set from the JSON
      // Note: The user swapped IDs in the JSON, so 'P1' is now the AI Engineering set.
      const problemSetId = 'P1' 
      const selectedProblemSet = problemData.progressiveProblems.find(p => p.id === problemSetId)
      
      if (selectedProblemSet) {
        this.problems = selectedProblemSet.steps.map(step => ({
          id: step.step,
          title: `Step ${step.step}: ${step.title}`,
          difficulty: 'Junior',
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
      
      if (!rules) return false // No rules, pass? Or fail? Better fail if we expect validation
      
      if (rules.type === 'multi_condition') {
        // Check required_any (at least one must be present)
        if (rules.required_any && rules.required_any.length > 0) {
          const hasAny = rules.required_any.some(keyword => code.includes(keyword))
          if (!hasAny) return true // Bug exists
        }
        
        // Check required_all (all must be present)
        if (rules.required_all && rules.required_all.length > 0) {
          const hasAll = rules.required_all.every(keyword => code.includes(keyword))
          if (!hasAll) return true // Bug exists
        }
        
        // Check forbidden (none should be present)
        if (rules.forbidden && rules.forbidden.length > 0) {
          const hasForbidden = rules.forbidden.some(keyword => code.includes(keyword))
          if (hasForbidden) return true // Bug exists
        }
      } 
      else if (rules.type === 'regex') {
        const regex = new RegExp(rules.value, rules.flags)
        if (!regex.test(code)) return true // Bug exists
      }
      
      return false // No bugs detected
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
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.problem-header {
  text-align: center;
  color: white;
  margin-bottom: 2rem;
}

.problem-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 1.5rem;
}

.progress-bar {
  width: 100%;
  max-width: 600px;
  height: 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  margin: 0 auto 1rem;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ade80, #22c55e);
  border-radius: 10px;
  transition: width 0.5s ease;
  box-shadow: 0 0 10px rgba(74, 222, 128, 0.5);
}

.step-indicator {
  font-size: 1.2rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
  display: inline-block;
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 2rem;
}

.problem-card,
.log-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.5s ease;
}

/* Terminal Style for Log Card */
.log-card {
  background: #1e1e1e; /* Dark terminal background */
  color: #d4d4d4; /* Light text for readability */
  border: 1px solid #333;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.log-header {
  border-bottom: 1px solid #333;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-header h3 {
  color: #fff;
  margin: 0;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.log-header h3::before {
  content: '>';
  color: #22c55e;
  font-weight: bold;
}

.btn-clear-log {
  background: #333;
  color: white;
  border: 1px solid #444;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.btn-clear-log:hover {
  background: #444;
  border-color: #666;
}

.log-content {
  height: 300px; /* Fixed height for terminal feel */
  overflow-y: auto;
  padding: 0.5rem;
  background: #1e1e1e;
}

/* Custom Scrollbar for Log */
.log-content::-webkit-scrollbar {
  width: 10px;
}

.log-content::-webkit-scrollbar-track {
  background: #1e1e1e;
}

.log-content::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 5px;
}

.log-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.log-entry {
  padding: 4px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  gap: 1rem;
  font-size: 0.95rem;
  line-height: 1.4;
}

.log-timestamp {
  color: #569cd6; /* VS Code Blue like timestamp */
  font-size: 0.85rem;
  min-width: 80px;
  user-select: none;
}

.log-message {
  white-space: pre-wrap; /* Maintain formatting for errors */
  word-break: break-word;
}

/* Log Types */
.log-entry.info .log-message { color: #d4d4d4; }
.log-entry.success .log-message { color: #4ade80; } /* Green */
.log-entry.warning .log-message { color: #fcd34d; } /* Yellow */
.log-entry.error .log-message { color: #f87171; } /* Red */

.log-empty {
  color: #666;
  text-align: center;
  padding-top: 2rem;
  font-style: italic;
}

/* Animations */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Remove old difficulty badge style to avoid conflict if I don't use it, 
   but keeping generic layout styles below */

.problem-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.problem-header-bar h2 {
  font-size: 1.8rem;
  color: #1f2937;
  margin: 0;
}

.difficulty-badge {
  padding: 0.4rem 1rem;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  color: white;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.problem-description,
.learning-objective {
  margin-bottom: 1.5rem;
}

.problem-description h3,
.learning-objective h3 {
  color: #374151;
  font-size: 1.2rem;
  margin-bottom: 0.75rem;
}

.problem-description p {
  color: #6b7280;
  line-height: 1.6;
  font-size: 1rem;
}

.learning-objective ul {
  list-style: none;
  padding: 0;
}

.learning-objective li {
  color: #6b7280;
  padding: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
}

.learning-objective li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #10b981;
  font-weight: bold;
}

.code-section {
  margin: 1.5rem 0;
}

.code-section h3 {
  color: #374151;
  font-size: 1.2rem;
  margin-bottom: 0.75rem;
}

.code-editor {
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.editor-header {
  background: #1f2937;
  color: white;
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-name {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.btn-reset {
  background: #374151;
  color: white;
  border: none;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
}

.btn-reset:hover {
  background: #4b5563;
}

.code-input {
  width: 100%;
  min-height: 300px;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  font-size: 0.95rem;
  line-height: 1.6;
  border: none;
  resize: vertical;
  background: #f9fafb;
  color: #1f2937;
}

.code-input:focus {
  outline: none;
  background: #f3f4f6;
}

.hint-section {
  margin: 1.5rem 0;
}

.btn-hint {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-hint:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(251, 191, 36, 0.4);
}

.hint-content {
  margin-top: 1rem;
  padding: 1rem;
  background: #fffbeb;
  border-left: 4px solid #fbbf24;
  border-radius: 8px;
}

.hint-content ul {
  margin-top: 0.5rem;
  padding-left: 1.5rem;
}

.hint-content li {
  color: #78350f;
  padding: 0.3rem 0;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-run,
.btn-submit,
.btn-skip {
  flex: 1;
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-run {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.btn-run:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-run:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-submit {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.btn-skip {
  background: #e5e7eb;
  color: #6b7280;
}

.btn-skip:hover {
  background: #d1d5db;
}

.feedback {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 8px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.feedback.success {
  background: #d1fae5;
  border-left: 4px solid #10b981;
}

.feedback.error {
  background: #fee2e2;
  border-left: 4px solid #ef4444;
}

.feedback h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.feedback.success h4 {
  color: #065f46;
}

.feedback.error h4 {
  color: #991b1b;
}

.feedback p {
  margin: 0;
  color: #374151;
}

/* Log Section */
.log-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.log-card {
  flex: 1;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
}

.log-header h3 {
  color: #1f2937;
  font-size: 1.3rem;
  margin: 0;
}

.btn-clear-log {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.btn-clear-log:hover {
  background: #dc2626;
}

.log-content {
  background: #1f2937;
  border-radius: 8px;
  padding: 1rem;
  min-height: 400px;
  max-height: 500px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.log-content::-webkit-scrollbar {
  width: 8px;
}

.log-content::-webkit-scrollbar-track {
  background: #374151;
  border-radius: 4px;
}

.log-content::-webkit-scrollbar-thumb {
  background: #6b7280;
  border-radius: 4px;
}

.log-content::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.log-empty {
  color: #9ca3af;
  text-align: center;
  padding: 2rem;
  font-style: italic;
}

.log-entry {
  padding: 0.4rem 0;
  display: flex;
  gap: 1rem;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.log-timestamp {
  color: #9ca3af;
  flex-shrink: 0;
}

.log-message {
  flex: 1;
  word-break: break-word;
}

.log-entry.info .log-message {
  color: #93c5fd;
}

.log-entry.success .log-message {
  color: #86efac;
}

.log-entry.error .log-message {
  color: #fca5a5;
}

.log-entry.warning .log-message {
  color: #fcd34d;
}

/* Error Helper */
.error-helper {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  border-left: 4px solid #ef4444;
}

.error-helper h3 {
  color: #1f2937;
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.error-type,
.error-description,
.error-suggestion {
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.error-type strong,
.error-description strong,
.error-suggestion strong {
  color: #374151;
}

.error-type {
  color: #ef4444;
  font-weight: 600;
}

.error-description {
  color: #6b7280;
}

.error-suggestion {
  color: #059669;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 3rem;
  max-width: 500px;
  width: 90%;
  text-align: center;
  animation: scaleIn 0.3s ease;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.completion-animation {
  font-size: 5rem;
  animation: bounce 0.5s ease infinite alternate;
}

@keyframes bounce {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(-20px);
  }
}

.modal-content h2 {
  color: #1f2937;
  font-size: 2rem;
  margin: 1rem 0;
}

.modal-content p {
  color: #6b7280;
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.stats {
  background: #f9fafb;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  color: #1f2937;
  font-weight: 700;
}

.btn-restart,
.btn-close-modal {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 0.5rem;
}

.btn-restart {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-restart:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-close-modal {
  background: #e5e7eb;
  color: #6b7280;
}

.btn-close-modal:hover {
  background: #d1d5db;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .log-content {
    max-height: 400px;
  }
}

@media (max-width: 768px) {
  .progressive-problems-container {
    padding: 1rem;
  }
  
  .problem-header h1 {
    font-size: 1.8rem;
  }
  
  .problem-card,
  .log-card {
    padding: 1.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .modal-content {
    padding: 2rem;
  }
}
</style>
