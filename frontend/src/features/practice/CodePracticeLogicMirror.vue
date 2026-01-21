<template>
  <div class="logic-mirror-page">
    <div class="game-container">
      <div class="header">
        <h1>LOGIC MIRROR</h1>
        <div class="subtitle">// COGNITIVE ARCHITECTURE ANALYSIS SYSTEM v1.0</div>
      </div>

      <div class="status-bar">
        <div 
          v-for="(step, index) in ['문제 정의', '수도코드', '코드 구현', '결과 분석']" 
          :key="index"
          :class="['status-step', { active: isStepActive(index + 1) }]"
        >
          <span class="step-num">0{{ index + 1 }}</span>
          <span class="step-text">{{ step }}</span>
        </div>
      </div>

      <div v-if="currentScreen === 1" class="game-screen">
        <div class="instruction-card">
          <div class="card-header">SYSTEM_MESSAGE: PROBLEM_DEFINITION</div>
          <p>요구사항을 분석하고 면접관에게 필요한 질문을 던져 설계를 구체화하십시오.</p>
        </div>
        <div class="game-grid">
          <div class="monitor">
            <div class="screen-content">
              <div class="problem-header">ENTRY_POINT: USER_REGISTRATION_SYS</div>
              <div class="problem-content">
                회원가입 시스템을 설계하세요.<br/><br/>
                [REQUIREMENTS]<br/>
                - 사용자는 이메일과 비밀번호로 가입할 수 있어야 합니다.<br/>
                - 이메일 중복 검사가 필요합니다.<br/>
                - 비밀번호는 안전하게 저장되어야 합니다.
              </div>
            </div>
          </div>
          <div class="chat-interface">
            <div class="chat-messages">
              <div v-for="msg in chatMessages1" :key="msg.id" :class="['message-wrapper', msg.type]">
                <div class="sender-tag">{{ msg.type === 'user' ? 'USER_ID: YOU' : 'AI_INT: INTERVIEWER' }}</div>
                <div class="message-body">{{ msg.content }}</div>
              </div>
            </div>
            <div class="chat-input-area">
              <input v-model="chatInput" type="text" class="cyber-input" placeholder="질문을 입력하세요..." @keypress.enter="sendChatMessage">
              <button class="cyber-send-btn" @click="sendChatMessage">SEND</button>
            </div>
          </div>
        </div>
        <div class="bottom-actions">
          <button class="next-btn" @click="goToScreen(3)">LOGIC_PHASE_02 >></button>
        </div>
      </div>

      <div v-if="currentScreen === 3" class="game-screen">
        <div class="instruction-card">
          <div class="card-header">LOGIC_CONSTRUCTION_MODE</div>
          <p>구현 전 전체 로직을 수도코드로 설계하십시오.</p>
        </div>
        <div class="monitor full-width">
          <div class="screen-content">
            <div class="problem-header">FILE: solution.pseudo</div>
            <textarea v-model="pseudocode" class="cyber-textarea" placeholder="수도코드를 작성하십시오..."></textarea>
          </div>
        </div>
        <div class="bottom-actions">
          <button class="next-btn" @click="goToScreen(5)">IMPLEMENTATION_PHASE >></button>
        </div>
      </div>

      <div v-if="currentScreen === 5" class="game-screen">
        <div class="instruction-card">
          <div class="card-header">SYSTEM_CORE: IMPLEMENTATION</div>
          <p>작성한 수도코드를 바탕으로 실제 코드를 구현하십시오.</p>
        </div>
        <div class="game-grid">
          <div class="monitor">
            <div class="screen-content">
              <div class="problem-header">REFERENCE: solution.pseudo</div>
              <div class="pseudo-reference">{{ pseudocode || '작성된 수도코드가 없습니다.' }}</div>
            </div>
          </div>
          <div class="monitor">
            <div class="screen-content">
              <div class="problem-header">EDITOR: solution.js</div>
              <textarea v-model="actualCode" class="cyber-textarea" placeholder="실제 코드를 작성하십시오..."></textarea>
            </div>
          </div>
        </div>
        <div class="bottom-actions">
          <button class="next-btn" @click="handleFinalSubmit">SUBMIT_SYSTEM_CORE >></button>
        </div>
      </div>

      <div class="feedback-message warning" :class="{ show: showStressAlert }">
        <div class="alert-content">
          <div class="alert-header">STRESS_TEST_DETECTION</div>
          <div class="alert-body">
            <p class="stress-q">{{ currentPersona.stressQuestion }}</p>
            <textarea v-model="stressAnswer" class="cyber-textarea-small" placeholder="대응 로직을 입력하십시오..."></textarea>
            <button class="cyber-send-btn alert-btn" @click="submitStressAnswer">RECOVERY_ACTION</button>
          </div>
        </div>
      </div>

      <div v-if="currentScreen === 6" class="game-screen report-screen">
        <div class="report-grid">
          <div class="metric-box" v-for="(val, key) in metrics" :key="key">
            <div class="metric-label">{{ key.toUpperCase() }}</div>
            <div class="metric-value">{{ val }}%</div>
            <div class="metric-bar-bg"><div class="metric-bar-fill" :style="{ width: val + '%' }"></div></div>
          </div>
        </div>
        <div class="monitor full-width">
          <div class="screen-content">
            <div class="problem-header">ANALYSIS_REPORT</div>
            <h3 class="neon-text-green">// INTERVIEWER_FEEDBACK</h3>
            <p class="feedback-text">{{ currentPersona.feedback }}</p>
            <h3 class="neon-text-yellow" style="margin-top:20px;">// GROWTH_GUIDE</h3>
            <p class="feedback-text">{{ currentPersona.growthGuide }}</p>
          </div>
        </div>
        <div class="bottom-actions">
          <button class="next-btn" @click="restart">REBOOT_SYSTEM</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      currentScreen: 1,
      chatInput: '',
      pseudocode: '',
      actualCode: '',
      stressAnswer: '',
      showStressAlert: false,
      stressAnswerSubmitted: false, // 돌발 질문 답변 완료 여부
      selectedPersona: 'balanced',
      chatMessages1: [{ id: 1, type: 'ai', content: '접속을 환영합니다. 요구사항을 분석하여 질문을 입력하십시오.' }],
      metrics: { problemDefinition: 0, exceptionHandling: 0, abstraction: 0, consistency: 0 },
      personas: {
        balanced: {
          stressQuestion: '회원가입 요청이 동시에 10,000건이 발생한다면 현재 로직에서 데이터 무결성을 보장할 수 있습니까? 어떤 방식으로 동시성을 제어하시겠습니까?',
          feedback: '전반적인 사고 구조가 안정적입니다. 일관성 있는 로직 전개가 인상적입니다.',
          growthGuide: '분산 환경에서의 트랜잭션 관리와 동시성 제어(낙관적/비관적 락)에 대해 더 심화 학습하시길 권장합니다.'
        }
      },
      messageId: 1
    };
  },
  computed: {
    currentPersona() { return this.personas[this.selectedPersona]; }
  },
  methods: {
    isStepActive(step) {
      if (this.currentScreen === 1) return step === 1;
      if (this.currentScreen === 3) return step === 2;
      if (this.currentScreen === 5) return step === 3;
      if (this.currentScreen === 6) return step === 4;
      return false;
    },
    goToScreen(num) { 
      this.currentScreen = num;
      window.scrollTo(0,0);
    },
    sendChatMessage() {
      if(!this.chatInput.trim()) return;
      this.chatMessages1.push({ id: ++this.messageId, type: 'user', content: this.chatInput });
      this.metrics.problemDefinition = Math.min(this.metrics.problemDefinition + 20, 100);
      setTimeout(() => {
        this.chatMessages1.push({ id: ++this.messageId, type: 'ai', content: '데이터 정합성과 보안 측면에서 매우 중요한 포인트입니다. 해당 내용을 로직에 반영하십시오.' });
      }, 600);
      this.chatInput = '';
    },
    // 3단계 최종 제출 시 호출되는 함수
    handleFinalSubmit() {
      if(!this.actualCode.trim()) return alert('코드를 작성하십시오.');
      
      // 돌발 질문이 아직 나오지 않았다면 트리거
      if (!this.stressAnswerSubmitted) {
        this.showStressAlert = true;
      } else {
        // 이미 답변했다면 결과 화면으로
        this.goToScreen(6);
      }
    },
    // 돌발 질문 답변 제출
    submitStressAnswer() {
      if(!this.stressAnswer.trim()) return alert('대응 로직을 입력해야 시스템이 승인됩니다.');
      
      this.metrics.exceptionHandling = 95;
      this.stressAnswerSubmitted = true; // 답변 완료 체크
      this.showStressAlert = false;
      
      // 답변 직후 약간의 딜레이 후 결과 화면으로 이동
      setTimeout(() => {
        this.goToScreen(6);
      }, 500);
    },
    restart() { location.reload(); }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=JetBrains+Mono&display=swap');

:root {
  --neon-blue: #00f3ff;
  --neon-pink: #ff00ff;
  --neon-yellow: #fff200;
  --success-green: #00ff66;
  --warning-orange: #ff8800;
  --bg-black: #050505;
}

.logic-mirror-page {
  background: var(--bg-black);
  color: #fff;
  min-height: 100vh;
  padding: 40px 20px;
  font-family: 'Noto Sans KR', sans-serif;
}

.header h1 {
  font-family: 'Orbitron', sans-serif;
  font-size: 3.5em;
  color: var(--neon-blue);
  text-align: center;
  text-shadow: 0 0 15px var(--neon-blue);
  letter-spacing: 10px;
}

.subtitle {
  text-align: center;
  font-family: 'Orbitron', sans-serif;
  color: var(--neon-pink);
  margin-top: 10px;
}

.status-bar {
  display: flex;
  gap: 15px;
  margin: 40px auto;
  max-width: 1000px;
}

.status-step {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-step.active {
  border-color: var(--neon-blue);
  background: rgba(0, 243, 255, 0.1);
  box-shadow: inset 0 0 15px rgba(0, 243, 255, 0.2);
}

.step-num { font-family: 'Orbitron', sans-serif; color: var(--neon-yellow); }

/* 모니터 스타일 */
.monitor {
  background: #111;
  border: 2px solid #333;
  padding: 5px;
  position: relative;
}

.monitor::before {
  content: "";
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%);
  background-size: 100% 4px;
  pointer-events: none;
  z-index: 2;
}

.screen-content {
  background: #080a0f;
  padding: 20px;
  min-height: 350px;
}

.problem-header {
  font-family: 'Orbitron', sans-serif;
  color: var(--neon-blue);
  border-bottom: 1px solid var(--neon-blue);
  margin-bottom: 15px;
  padding-bottom: 5px;
}

/* 입력/버튼 디자인 (OpsPractice 스타일) */
.chat-input-area {
  display: flex;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--neon-blue);
  padding: 5px;
  margin-top: 10px;
}

.cyber-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  padding: 12px;
  outline: none;
  font-family: 'Orbitron', sans-serif;
}

.cyber-send-btn {
  background: var(--neon-blue);
  color: #000;
  border: none;
  padding: 0 25px;
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.cyber-send-btn:hover {
  background: #fff;
  box-shadow: 0 0 15px var(--neon-blue);
}

/* 돌발 질문 팝업 (OpsPractice 경고 스타일) */
.feedback-message.warning {
  position: fixed;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%) scale(0);
  background: var(--warning-orange);
  color: #000;
  width: 550px;
  padding: 2px;
  z-index: 2000;
  opacity: 0;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.feedback-message.show {
  transform: translate(-50%, -50%) scale(1);
  opacity: 1;
}

.alert-content { background: #111; color: #fff; padding: 30px; }

.alert-header {
  font-family: 'Orbitron', sans-serif;
  color: var(--warning-orange);
  font-size: 1.3em;
  font-weight: 700;
  margin-bottom: 20px;
  text-align: center;
  text-shadow: 0 0 10px var(--warning-orange);
}

.stress-q { color: var(--neon-yellow); line-height: 1.6; margin-bottom: 25px; font-size: 1.1em; }

.cyber-textarea-small {
  width: 100%;
  height: 120px;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--warning-orange);
  color: #fff;
  padding: 12px;
  resize: none;
  outline: none;
  margin-bottom: 20px;
  font-family: 'JetBrains Mono';
}

.alert-btn { width: 100%; background: var(--warning-orange); height: 50px; font-size: 1.1em; }

/* 레이아웃 공통 */
.game-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
.full-width { grid-column: span 2; }
.cyber-textarea {
  width: 100%; height: 350px; background: transparent; border: none;
  color: var(--success-green); font-family: 'JetBrains Mono', monospace; font-size: 1.1em; outline: none;
}
.pseudo-reference { color: var(--success-green); white-space: pre-wrap; font-family: 'JetBrains Mono'; }
.next-btn {
  background: transparent; border: 1px solid var(--neon-blue); color: var(--neon-blue);
  padding: 15px 40px; font-family: 'Orbitron', sans-serif; cursor: pointer; transition: all 0.3s;
}
.next-btn:hover { background: var(--neon-blue); color: #000; box-shadow: 0 0 20px var(--neon-blue); }
.bottom-actions { text-align: center; margin-top: 40px; }

/* 결과 화면 */
.report-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }
.metric-box { background: #111; border: 1px solid var(--neon-blue); padding: 20px; text-align: center; }
.metric-value { font-family: 'Orbitron', sans-serif; font-size: 2.2em; color: var(--neon-yellow); }
.metric-bar-bg { background: #222; height: 6px; margin-top: 10px; }
.metric-bar-fill { background: var(--neon-blue); height: 100%; transition: width 1s; }
.neon-text-green { color: var(--success-green); font-family: 'Orbitron'; }
.neon-text-yellow { color: var(--neon-yellow); font-family: 'Orbitron'; }
</style>