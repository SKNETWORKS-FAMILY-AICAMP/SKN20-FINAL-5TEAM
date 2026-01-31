<template>
  <div class="logic-mirror-container">
    <div class="bg-overlay"></div>
    
    <div class="container">
      <div class="header">
        <h1 class="logo">Logic Mirror</h1>
        <p class="tagline">당신의 사고 구조를 비춥니다</p>
      </div>

      <!-- Screen 1: Problem Definition -->
      <div v-if="currentScreen === 1" class="screen active">
        <div class="progress-tracker">
          <div class="progress-step active">1. 문제 정의</div>
          <div class="progress-step">2. 수도코드</div>
          <div class="progress-step">3. 구현</div>
          <div class="progress-step">4. 분석</div>
        </div>

        <div class="card">
          <h2 class="card-title">📋 문제 정의 단계</h2>
          <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
            면접관과의 대화를 통해 문제를 명확히 정의하세요. 좋은 질문이 좋은 솔루션을 만듭니다.
          </p>
        </div>

        <div class="split-container">
          <div class="editor-container">
            <div class="editor-header">problem_definition.txt</div>
            <div class="editor-content">
회원가입 시스템을 설계하세요.

요구사항:
- 사용자는 이메일과 비밀번호로 가입할 수 있어야 합니다
- 이메일 중복 검사가 필요합니다
- 비밀번호는 안전하게 저장되어야 합니다
            </div>
          </div>

          <div class="chat-container">
            <div class="chat-messages">
              <div v-for="msg in chatMessages1" :key="msg.id" :class="['message', msg.type]">
                <div class="message-sender">{{ msg.type === 'user' ? '나' : '면접관' }}</div>
                <div>{{ msg.content }}</div>
              </div>
            </div>
            <div class="chat-input-container">
              <input 
                v-model="chatInput"
                type="text" 
                class="chat-input" 
                placeholder="질문을 입력하세요... (예: 이메일 형식 검증은 어떻게 하나요?)"
                @keypress.enter="sendChatMessage"
              >
            </div>
          </div>
        </div>

        <div style="text-align: center; margin-top: 2rem;">
          <button class="btn" @click="goToScreen(3)">수도코드 작성 →</button>
        </div>
      </div>

      <!-- Screen 3: Pseudocode -->
      <div v-if="currentScreen === 3" class="screen active">
        <div class="progress-tracker">
          <div class="progress-step completed">1. 문제 정의</div>
          <div class="progress-step active">2. 수도코드</div>
          <div class="progress-step">3. 구현</div>
          <div class="progress-step">4. 분석</div>
        </div>

        <div class="card">
          <h2 class="card-title">✏️ 수도코드 작성</h2>
          <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
            구현 전에 로직을 수도코드로 정리하세요. 추상화 수준을 적절히 조절하는 것이 중요합니다.
          </p>
        </div>

        <div class="editor-container">
          <div class="editor-header">solution.pseudo</div>
          <textarea 
            v-model="pseudocode"
            class="editor-content" 
            placeholder="수도코드를 작성하세요...

예시:
1. 회원가입 요청 받기
   - 이메일, 비밀번호 입력값 받기
   
2. 입력값 검증
   - 이메일 형식 검증
   - 비밀번호 복잡도 검증
   
3. 중복 확인
   - DB에서 이메일 존재 여부 확인
   - 존재하면 에러 반환
   
4. 비밀번호 암호화
   - bcrypt로 해시 생성
   
5. 사용자 정보 저장
   - DB에 저장
   - 성공 응답 반환"></textarea>
        </div>

        <div style="text-align: center; margin-top: 2rem;">
          <button class="btn" @click="submitPseudocode">수도코드 제출 →</button>
        </div>
      </div>

      <!-- Screen 4: Stress Test -->
      <div v-if="currentScreen === 4" class="screen active">
        <div class="progress-tracker">
          <div class="progress-step completed">1. 문제 정의</div>
          <div class="progress-step active">2. 수도코드</div>
          <div class="progress-step">3. 구현</div>
          <div class="progress-step">4. 분석</div>
        </div>

        <div class="card">
          <h2 class="card-title">📝 제출된 수도코드</h2>
          <div class="editor-container">
            <div class="editor-header">submitted_pseudocode.pseudo</div>
            <div class="editor-content">{{ pseudocode }}</div>
          </div>
        </div>

        <div v-if="stressAnswerSubmitted" style="text-align: center; margin-top: 2rem;">
          <button class="btn" @click="goToScreen(5)">구현 단계로 →</button>
        </div>
      </div>

      <!-- Overlay for Stress Alert -->
      <div v-if="showStressAlert" class="overlay show">
        <div class="stress-alert show">
          <h2>⚡ 꼬리질문</h2>
          <p style="color: var(--text-secondary); margin-bottom: 0.5rem; line-height: 1.8;">
            {{ currentPersona.stressQuestion }}
          </p>
          
          <textarea 
            v-model="stressAnswer"
            class="stress-answer-input" 
            placeholder="꼬리질문에 대한 답변을 작성해주세요..."></textarea>
          
          <div class="alert-actions">
            <button class="btn" @click="submitStressAnswer">답변 제출 →</button>
          </div>
        </div>
      </div>

      <!-- Screen 5: Implementation -->
      <div v-if="currentScreen === 5" class="screen active">
        <div class="progress-tracker">
          <div class="progress-step completed">1. 문제 정의</div>
          <div class="progress-step completed">2. 수도코드</div>
          <div class="progress-step active">3. 구현</div>
          <div class="progress-step">4. 분석</div>
        </div>

        <div class="card">
          <h2 class="card-title">💻 실제 코드 구현</h2>
          <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
            작성한 수도코드를 바탕으로 실제 코드를 작성하세요. 수도코드와의 일관성을 유지하는 것이 중요합니다.
          </p>
        </div>

        <div class="split-container">
          <div class="editor-container">
            <div class="editor-header">reference_pseudocode.pseudo (참고용)</div>
            <div class="editor-content" style="font-size: 0.85rem; color: var(--text-muted);">
              {{ pseudocode }}
            </div>
          </div>

          <div class="editor-container">
            <div class="editor-header">solution.js</div>
            <textarea 
              v-model="actualCode"
              class="editor-content" 
              placeholder="실제 코드를 작성하세요...

예시:
async function registerUser(email, password) {
    // 1. 입력값 검증
    if (!validateEmail(email)) {
        throw new Error('Invalid email format');
    }
    
    // 2. 중복 확인
    const existingUser = await db.findUserByEmail(email);
    if (existingUser) {
        throw new Error('Email already exists');
    }
    
    // 3. 비밀번호 암호화
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // 4. 사용자 저장
    const user = await db.createUser({
        email,
        password: hashedPassword
    });
    
    return user;
}"></textarea>
          </div>
        </div>

        <div v-if="showConsistencyWarning" class="consistency-feedback">
          <strong>⚠️ 일관성 경고</strong>
          <p style="margin-top: 0.5rem;">{{ consistencyMessage }}</p>
        </div>

        <div style="text-align: center; margin-top: 2rem;">
          <button class="btn" @click="submitCode">최종 제출 →</button>
        </div>
      </div>

      <!-- Screen 6: Report -->
      <div v-if="currentScreen === 6" class="screen active">
        <div class="progress-tracker">
          <div class="progress-step completed">1. 문제 정의</div>
          <div class="progress-step completed">2. 수도코드</div>
          <div class="progress-step completed">3. 구현</div>
          <div class="progress-step active">4. 분석</div>
        </div>

        <div class="card">
          <h2 class="card-title">📊 성과 분석</h2>
          <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
            당신의 사고 구조를 분석한 결과입니다.
          </p>
        </div>

        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-label">문제 정의 능력</div>
            <div class="metric-value">{{ metrics.problemDefinition }}%</div>
            <div class="metric-bar">
              <div class="metric-bar-fill" :style="{ width: metrics.problemDefinition + '%' }"></div>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-label">예외 처리 고려</div>
            <div class="metric-value">{{ metrics.exceptionHandling }}%</div>
            <div class="metric-bar">
              <div class="metric-bar-fill" :style="{ width: metrics.exceptionHandling + '%' }"></div>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-label">추상화 수준</div>
            <div class="metric-value">{{ metrics.abstraction }}%</div>
            <div class="metric-bar">
              <div class="metric-bar-fill" :style="{ width: metrics.abstraction + '%' }"></div>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-label">구현 일관성</div>
            <div class="metric-value">{{ metrics.consistency }}%</div>
            <div class="metric-bar">
              <div class="metric-bar-fill" :style="{ width: metrics.consistency + '%' }"></div>
            </div>
          </div>
        </div>

        <div class="feedback-section">
          <h3 class="feedback-title">💬 면접관 피드백</h3>
          <p class="feedback-text">{{ currentPersona.feedback }}</p>
        </div>

        <div class="feedback-section">
          <h3 class="feedback-title">🌱 성장 가이드</h3>
          <p class="feedback-text">{{ currentPersona.growthGuide }}</p>
        </div>

        <div class="card">
          <h3 class="card-title">⏱️ 프로세스 타임라인</h3>
          <div class="timeline">
            <div v-for="event in timeline" :key="event.id" class="timeline-item">
              <div class="timeline-time">{{ formatTime(event.time) }}</div>
              <div class="timeline-content">{{ event.action }}: {{ event.detail }}</div>
            </div>
          </div>
        </div>

        <div style="text-align: center; margin-top: 2rem;">
          <button class="btn" @click="restart">새로운 세션 시작</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CodePracticeLogicMirror',
  data() {
    return {
      currentScreen: 1,
      chatInput: '',
      pseudocode: '',
      stressAnswer: '',
      actualCode: '',
      stressAnswerSubmitted: false,
      showStressAlert: false,
      showConsistencyWarning: false,
      consistencyMessage: '',
      selectedPersona: 'balanced',
      chatMessages1: [
        {
          id: 1,
          type: 'ai',
          content: '안녕하세요! 문제를 읽어보셨나요? 궁금한 점이 있으시면 언제든지 질문해주세요.'
        }
      ],
      timeline: [],
      startTime: Date.now(),
      questions: [],
      metrics: {
        problemDefinition: 0,
        exceptionHandling: 0,
        abstraction: 0,
        consistency: 0
      },
      personas: {
        balanced: {
          name: '균형잡힌 면접관',
          icon: '⚖️',
          description: '질문의 깊이와 실용성 사이의 균형을 추구합니다',
          stressQuestion: '만약 회원가입 중 네트워크 장애가 발생한다면 어떻게 처리하시겠습니까? 데이터 일관성을 어떻게 보장하시겠습니까?',
          feedback: '문제 정의 단계에서 핵심 요구사항을 잘 파악했습니다. 수도코드의 추상화 수준도 적절했으며, 실제 구현과의 일관성도 유지되었습니다.',
          growthGuide: '다음 단계로 나아가기 위해서는 동시성 제어와 분산 시스템에서의 데이터 정합성에 대한 고민을 더해보세요.'
        }
      },
      aiResponses: {
        '이메일': '이메일 형식은 정규표현식으로 검증하면 됩니다. RFC 5322 표준을 따르는 것을 권장합니다.',
        '중복': '중복 검사는 DB의 unique constraint와 애플리케이션 레벨 체크를 모두 사용하는 것이 안전합니다.',
        '비밀번호': '비밀번호는 bcrypt나 Argon2 같은 단방향 해시 함수로 암호화해야 합니다. 절대 평문으로 저장하면 안 됩니다.',
        '인증': '이메일 인증은 토큰 기반으로 구현할 수 있습니다. 가입 시 인증 토큰을 생성하고 이메일로 발송합니다.',
        '소셜': '소셜 로그인은 OAuth 2.0 프로토콜을 사용합니다. 각 provider의 SDK를 활용하면 구현이 간편합니다.',
        '동시': '동시 요청은 DB의 트랜잭션과 락을 활용해 처리할 수 있습니다. Optimistic locking이나 Pessimistic locking을 고려해보세요.',
        'default': '좋은 질문입니다! 구체적으로 어떤 부분이 궁금하신가요?'
      },
      messageId: 1
    };
  },
  computed: {
    currentPersona() {
      return this.personas[this.selectedPersona];
    }
  },
  methods: {
    goToScreen(screenNum) {
      this.currentScreen = screenNum;
      this.trackEvent('screen_change', `Screen ${screenNum}`);
      window.scrollTo(0, 0);
    },
    sendChatMessage() {
      if (!this.chatInput.trim()) return;

      const userMsg = this.chatInput;
      this.questions.push(userMsg);
      this.trackEvent('question_asked', userMsg);

      this.chatMessages1.push({
        id: ++this.messageId,
        type: 'user',
        content: userMsg
      });

      // Calculate metric
      const goodKeywords = ['이메일', '중복', '비밀번호', '검증', '형식', '보안'];
      const score = this.questions.filter(q => 
        goodKeywords.some(kw => q.includes(kw))
      ).length * 20;
      this.metrics.problemDefinition = Math.min(score, 80);

      // Find response
      let response = this.aiResponses.default;
      for (let key in this.aiResponses) {
        if (userMsg.includes(key)) {
          response = this.aiResponses[key];
          break;
        }
      }

      setTimeout(() => {
        this.chatMessages1.push({
          id: ++this.messageId,
          type: 'ai',
          content: response
        });
        this.$nextTick(() => {
          const chatMessages = document.querySelector('.chat-messages');
          if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
          }
        });
      }, 500);

      this.chatInput = '';
    },
    submitPseudocode() {
      if (!this.pseudocode.trim()) {
        alert('수도코드를 작성해주세요!');
        return;
      }

      this.goToScreen(4);

      // Check abstraction level
      const hasAbstraction = this.pseudocode.match(/\d+\./g)?.length > 2;
      const hasDetails = this.pseudocode.includes('함수') || this.pseudocode.includes('검증') || this.pseudocode.includes('체크');
      
      if (hasAbstraction && hasDetails) {
        this.metrics.abstraction = 75;
      } else if (hasAbstraction) {
        this.metrics.abstraction = 50;
      } else {
        this.metrics.abstraction = 30;
      }

      setTimeout(() => {
        this.showStressAlert = true;
      }, 1000);
    },
    submitStressAnswer() {
      if (!this.stressAnswer.trim()) {
        alert('꼬리질문에 대한 답변을 작성해주세요!');
        return;
      }

      const goodKeywords = ['재시도', '롤백', '트랜잭션', '보상', '큐', '비동기', '타임아웃', '장애'];
      const score = goodKeywords.filter(kw => this.stressAnswer.includes(kw)).length;
      
      if (score >= 2) {
        this.metrics.exceptionHandling = 80;
      } else if (score >= 1) {
        this.metrics.exceptionHandling = 60;
      } else {
        this.metrics.exceptionHandling = 40;
      }

      this.trackEvent('stress_answer', this.stressAnswer.substring(0, 50));
      this.showStressAlert = false;
      this.stressAnswerSubmitted = true;
    },
    submitCode() {
      if (!this.actualCode.trim()) {
        alert('코드를 작성해주세요!');
        return;
      }

      const code = this.actualCode.toLowerCase();
      const pseudo = this.pseudocode.toLowerCase();
      
      const pseudoHasAuth = pseudo.includes('권한') || pseudo.includes('검증');
      const codeHasAuth = code.includes('auth') || code.includes('permission') || code.includes('validate');
      
      const pseudoHasDuplicate = pseudo.includes('중복');
      const codeHasDuplicate = code.includes('duplicate') || code.includes('exist');
      
      if ((pseudoHasAuth && !codeHasAuth) || (pseudoHasDuplicate && !codeHasDuplicate)) {
        this.showConsistencyWarning = true;
        this.consistencyMessage = '수도코드에는 있지만 실제 코드에는 없는 로직이 감지되었습니다. 일관성을 확인하세요.';
        this.metrics.consistency = 50;
      } else {
        this.showConsistencyWarning = false;
        this.metrics.consistency = 85;
      }

      this.generateReport();
      this.goToScreen(6);
    },
    generateReport() {
      this.timeline = [
        {
          id: 1,
          time: Date.now() - this.startTime,
          action: 'screen_change',
          detail: 'Screen 1'
        },
        {
          id: 2,
          time: Date.now() - this.startTime,
          action: 'question_asked',
          detail: this.questions.length + '개의 질문'
        },
        {
          id: 3,
          time: Date.now() - this.startTime,
          action: 'screen_change',
          detail: 'Screen 3'
        }
      ];
    },
    formatTime(ms) {
      const minutes = Math.floor(ms / 60000);
      const seconds = Math.floor((ms % 60000) / 1000);
      return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    },
    trackEvent(action, detail) {
      // Track events for analytics
    },
    restart() {
      this.$router.go(0);
    }
  }
};
</script>

<style scoped>
:root {
  --bg-dark: #0a0e17;
  --bg-medium: #141824;
  --bg-light: #1e2538;
  --accent-primary: #00d9ff;
  --accent-secondary: #ff3366;
  --accent-warning: #ffa726;
  --text-primary: #e8edf4;
  --text-secondary: #8b95a8;
  --text-muted: #4a5568;
  --border: #2d3748;
  --success: #4ade80;
}

.logic-mirror-container {
  font-family: 'DM Sans', sans-serif;
  background: var(--bg-dark);
  color: var(--text-primary);
  overflow-x: hidden;
  line-height: 1.6;
}

/* Animated Background */
.bg-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 50%, rgba(0, 217, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 51, 102, 0.08) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.container {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

/* Header */
.header {
  text-align: center;
  margin-bottom: 3rem;
  padding: 2rem 0;
}

.logo {
  font-family: 'Crimson Pro', serif;
  font-size: 3.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
  animation: fadeInDown 0.8s ease-out;
}

.tagline {
  font-family: 'Crimson Pro', serif;
  font-size: 1.3rem;
  color: var(--text-secondary);
  font-style: italic;
  animation: fadeInUp 0.8s ease-out 0.2s both;
}

/* Screen Container */
.screen {
  display: none;
  animation: fadeIn 0.5s ease-out;
}

.screen.active {
  display: block;
}

/* Card Styles */
.card {
  background: var(--bg-medium);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.card:hover {
  border-color: var(--accent-primary);
  box-shadow: 0 8px 16px rgba(0, 217, 255, 0.1);
}

.card-title {
  font-family: 'Crimson Pro', serif;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--accent-primary);
}

/* Split Layout */
.split-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

/* Editor */
.editor-container {
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.editor-header {
  background: var(--bg-medium);
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.editor-content {
  padding: 1.5rem;
  min-height: 400px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  line-height: 1.8;
}

textarea.editor-content {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  resize: vertical;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
}

/* Chat Interface */
.chat-container {
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 600px;
}

.chat-messages {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.message {
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 8px;
  animation: messageSlide 0.3s ease-out;
}

.message.user {
  background: rgba(0, 217, 255, 0.1);
  border-left: 3px solid var(--accent-primary);
}

.message.ai {
  background: rgba(255, 51, 102, 0.08);
  border-left: 3px solid var(--accent-secondary);
}

.message-sender {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.chat-input-container {
  padding: 1rem;
  background: var(--bg-medium);
  border-top: 1px solid var(--border);
}

.chat-input {
  width: 100%;
  padding: 0.75rem;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
}

.chat-input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

/* Button Styles */
.btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 217, 255, 0.3);
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 217, 255, 0.4);
}

.btn-secondary {
  background: var(--bg-light);
  border: 1px solid var(--border);
  box-shadow: none;
}

.btn-secondary:hover {
  border-color: var(--accent-primary);
  background: var(--bg-medium);
}

/* Alert/Overlay */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(10, 14, 23, 0.95);
  display: none;
  z-index: 999;
  backdrop-filter: blur(8px);
}

.overlay.show {
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease-out;
}

.stress-alert {
  background: linear-gradient(135deg, var(--bg-medium), var(--bg-light));
  border: 2px solid var(--accent-warning);
  border-radius: 16px;
  padding: 3rem;
  max-width: 700px;
  box-shadow: 0 20px 40px rgba(255, 167, 38, 0.3);
  animation: scaleIn 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  display: none;
}

.stress-alert.show {
  display: block;
}

.stress-alert h2 {
  color: var(--accent-warning);
  font-family: 'Crimson Pro', serif;
  font-size: 2rem;
  margin-bottom: 1rem;
}

.stress-answer-input {
  width: 100%;
  min-height: 120px;
  padding: 1rem;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  resize: vertical;
  margin-top: 1.5rem;
}

.stress-answer-input:focus {
  outline: none;
  border-color: var(--accent-warning);
}

.alert-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  justify-content: flex-end;
}

/* Progress Tracker */
.progress-tracker {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--bg-medium);
  border-radius: 8px;
}

.progress-step {
  flex: 1;
  text-align: center;
  padding: 0.5rem;
  color: var(--text-muted);
  position: relative;
}

.progress-step.active {
  color: var(--accent-primary);
  font-weight: 600;
}

.progress-step.completed {
  color: var(--success);
}

.progress-step::after {
  content: '';
  position: absolute;
  top: 50%;
  right: -50%;
  width: 100%;
  height: 2px;
  background: var(--border);
}

.progress-step:last-child::after {
  display: none;
}

.progress-step.completed::after {
  background: var(--success);
}

/* Metrics Display */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-top: 2rem;
}

.metric-card {
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
}

.metric-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent-primary);
  margin-bottom: 0.5rem;
}

.metric-bar {
  width: 100%;
  height: 8px;
  background: var(--bg-dark);
  border-radius: 4px;
  overflow: hidden;
}

.metric-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 4px;
  transition: width 0.5s ease-out;
}

/* Timeline */
.timeline {
  margin-top: 2rem;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 1rem;
  background: var(--bg-light);
  border-left: 3px solid var(--accent-primary);
  border-radius: 4px;
}

.timeline-time {
  color: var(--accent-primary);
  font-weight: 600;
  min-width: 60px;
}

.timeline-content {
  color: var(--text-secondary);
}

/* Feedback Section */
.feedback-section {
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 2rem;
  margin-top: 2rem;
}

.feedback-title {
  font-family: 'Crimson Pro', serif;
  font-size: 1.5rem;
  color: var(--accent-primary);
  margin-bottom: 1rem;
}

.feedback-text {
  line-height: 1.8;
  color: var(--text-secondary);
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
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

/* Consistency Feedback */
.consistency-feedback {
  display: none;
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(255, 167, 38, 0.1);
  border: 1px solid var(--accent-warning);
  border-radius: 8px;
  color: var(--accent-warning);
}

/* Responsive */
@media (max-width: 968px) {
  .split-container {
    grid-template-columns: 1fr;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .logo {
    font-size: 2.5rem;
  }
}
</style>
