<template>
  <div class="coach-container">
    <header class="coach-header">
      <button class="back-btn" @click="$emit('close')">&times;</button>
      <div class="badge">AI COACH</div>
      <h1 class="title">Coduck Coach</h1>
      <p class="subtitle">AI 학습 코치가 당신의 성장을 도와드립니다</p>
    </header>

    <div class="chat-area" ref="chatArea">
      <!-- 프리셋 버튼 (대화 없을 때) -->
      <div v-if="messages.length === 0" class="preset-section">
        <p class="preset-label">무엇을 도와드릴까요?</p>
        <div class="preset-buttons">
          <button class="preset-btn" @click="sendPreset('내 약점을 분석해줘')">
            <span class="preset-icon">&#127919;</span>
            <span>내 약점 분석</span>
          </button>
          <button class="preset-btn" @click="sendPreset('다음에 어떤 문제를 풀면 좋을지 추천해줘')">
            <span class="preset-icon">&#128218;</span>
            <span>다음 학습 추천</span>
          </button>
          <button class="preset-btn" @click="sendPreset('내 전체 학습 현황을 리포트해줘')">
            <span class="preset-icon">&#128202;</span>
            <span>성장 리포트</span>
          </button>
          <button class="preset-btn" @click="sendPreset('유닛별 성적을 보여줘')">
            <span class="preset-icon">&#127942;</span>
            <span>유닛별 성적</span>
          </button>
        </div>
      </div>

      <!-- 채팅 메시지 -->
      <div v-for="(msg, idx) in messages" :key="idx" class="message-block">
        <!-- 의도 분석 결과 배지 (v2) [2026-02-23] -->
        <div v-if="msg.intentData" class="intent-badge">
          <span class="intent-type">{{ msg.intentData.intent_name }}</span>
          <span class="intent-confidence">(신뢰도: {{ (msg.intentData.confidence * 100).toFixed(0) }}%)</span>
          <span class="intent-reasoning">{{ msg.intentData.reasoning }}</span>
        </div>

        <!-- 유저 메시지 -->
        <div v-if="msg.role === 'user'" class="chat-bubble user">
          {{ msg.content }}
        </div>

        <!-- Agent Steps (실시간 스트리밍) -->
        <template v-if="msg.role === 'assistant'">
          <!-- Agent 사고 과정 + Tool 사용 -->
          <template v-for="(item, iIdx) in msg.timeline" :key="'t-' + iIdx">
            <!-- thinking -->
            <div v-if="item.type === 'thinking'" class="thinking-block">
              <span class="thinking-icon">&#129504;</span>
              <span class="thinking-text">{{ item.message }}</span>
              <span v-if="item.active" class="step-spinner"></span>
            </div>
            <!-- tool step -->
            <div v-if="item.type === 'step'" class="step-block">
              <div class="step-header" :class="{ 'no-result': !item.showResult }">
                <span class="step-icon">&#128295;</span>
                <span class="step-label">{{ item.label }}</span>
                <span v-if="Object.keys(item.args || {}).length" class="step-args">
                  ({{ formatArgs(item.args) }})
                </span>
                <span v-if="item.loading" class="step-spinner"></span>
              </div>
              <div v-if="item.showResult" class="step-result">
                <span class="result-icon">&#128202;</span>
                <pre class="result-json">{{ formatResult(item.result) }}</pre>
              </div>
            </div>
          </template>

          <!-- 최종 답변 (스트리밍) -->
          <div v-if="msg.showAnswer" class="chat-bubble assistant" v-html="renderMarkdown(msg.displayedContent || '')">
          </div>
        </template>
      </div>

      <!-- 로딩 (첫 이벤트 도착 전까지만 표시) -->
      <div v-if="loading && !streaming" class="loading-indicator">
        <div class="loading-dots">
          <span></span><span></span><span></span>
        </div>
        <span class="loading-text">코치가 분석 중입니다...</span>
      </div>
    </div>

    <div class="input-area">
      <input
        v-model="inputText"
        class="chat-input"
        placeholder="학습에 대해 물어보세요..."
        @keyup.enter="sendMessage"
        :disabled="loading"
      />
      <button class="send-btn" @click="sendMessage" :disabled="loading || !inputText.trim()">
        전송
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';

const emit = defineEmits(['close']);

const messages = ref([]);
const inputText = ref('');
const loading = ref(false);
const streaming = ref(false);
const chatArea = ref(null);

function getCsrfToken() {
  const m = document.cookie.match(/csrftoken=([^;]+)/);
  return m ? m[1] : '';
}

// 토큰 디스플레이 큐 — 네트워크 버퍼링과 무관하게 부드러운 출력
let tokenBuffer = '';
let displayPos = 0;
let displayTimer = null;

function startTokenDisplay(msg) {
  if (displayTimer) return;
  displayTimer = setInterval(() => {
    if (displayPos >= tokenBuffer.length) return; // 버퍼 따라잡음 — 대기
    const end = Math.min(displayPos + 3, tokenBuffer.length);
    msg.displayedContent += tokenBuffer.slice(displayPos, end);
    displayPos = end;
    scrollToBottom();
  }, 20);
}

function flushTokenDisplay(msg) {
  if (displayTimer) { clearInterval(displayTimer); displayTimer = null; }
  // 남은 토큰 즉시 표시
  if (displayPos < tokenBuffer.length) {
    msg.displayedContent += tokenBuffer.slice(displayPos);
    displayPos = tokenBuffer.length;
  }
  tokenBuffer = '';
  displayPos = 0;
}

function formatArgs(args) {
  return Object.entries(args).map(([k, v]) => `${k}: ${v}`).join(', ');
}

function formatResult(result) {
  if (!result) return '(데이터 없음)';
  if (result.message) return result.message;

  if (Array.isArray(result)) {
    if (result.length === 0) return '(데이터 없음)';
    if (result.length === 1 && result[0].message) return result[0].message;
    if (result[0].avg_score !== undefined) {
      return result.map(r =>
        `${r.unit_title}: 평균 ${r.avg_score}점, 최고 ${r.max_score}점, ${r.solved_count}/${r.total_problems}문제 (${r.completion_rate}%)`
      ).join('\n');
    }
    if (result[0].solved_date !== undefined) {
      return result.map(r =>
        `${r.problem_title} — ${r.score}점 (${r.solved_date})`
      ).join('\n');
    }
    if (result[0].status !== undefined) {
      return result.map(r =>
        `${r.problem_title} [${r.status}]${r.current_best_score != null ? ` 현재 ${r.current_best_score}점` : ''}`
      ).join('\n');
    }
    return result.map(r => r.message || JSON.stringify(r)).join('\n');
  }

  if (result.weak_areas !== undefined) {
    if (result.weak_areas.length === 0) return `풀이 ${result.total_solved}건 — 약점 없음 (모두 70점 이상)`;
    const weakList = result.weak_areas.map(w => `${w.metric} ${w.avg_score}점`).join(', ');
    return `풀이 ${result.total_solved}건 — 약점: ${weakList}`;
  }

  return String(result);
}

function renderMarkdown(text) {
  if (!text) return '';
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`);
  html = html.replace(/\n/g, '<br>');
  return html;
}

function scrollToBottom() {
  nextTick(() => {
    if (chatArea.value) {
      chatArea.value.scrollTop = chatArea.value.scrollHeight;
    }
  });
}

function sendPreset(text) {
  inputText.value = text;
  sendMessage();
}

async function sendMessage() {
  const text = inputText.value.trim();
  if (!text || loading.value) return;

  messages.value.push({ role: 'user', content: text });
  inputText.value = '';
  loading.value = true;
  streaming.value = false;
  scrollToBottom();

  messages.value.push({
    role: 'assistant',
    content: '',
    timeline: [],
    showAnswer: false,
    displayedContent: '',
    intentData: null, // [2026-02-23] 의도 분석 데이터
  });
  const assistantMsg = messages.value[messages.value.length - 1];

  try {
    // AI Coach 엔드포인트
    const endpoint = '/api/core/ai-coach/chat/';

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ message: text }),
    });

    if (!response.ok || !response.body) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || `HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let done = false;

    while (!done) {
      const chunk = await reader.read();
      if (chunk.done) break;
      buffer += decoder.decode(chunk.value, { stream: true });

      let boundary = buffer.indexOf('\n\n');
      while (boundary !== -1) {
        const eventChunk = buffer.slice(0, boundary).trim();
        buffer = buffer.slice(boundary + 2);

        if (eventChunk.startsWith('data:')) {
          const payload = eventChunk
            .split('\n')
            .filter(l => l.startsWith('data:'))
            .map(l => l.slice(5).trim())
            .join('');

          if (payload === '[DONE]') {
            done = true;
            break;
          }

          try {
            const data = JSON.parse(payload);
            streaming.value = true;

            // [2026-02-24] Intent Detected (v2, v3)
            if (data.type === 'intent_detected') {
              assistantMsg.intentData = {
                intent_name: data.intent_name,
                confidence: data.confidence,
                reasoning: data.reasoning,
              };
              scrollToBottom();
            }
            else if (data.type === 'thinking') {
              // 이전 thinking 비활성화
              const prevThinking = [...assistantMsg.timeline].reverse().find(i => i.type === 'thinking');
              if (prevThinking) prevThinking.active = false;
              // 새 thinking 추가
              assistantMsg.timeline.push({
                type: 'thinking',
                message: data.message,
                active: true,
              });
              scrollToBottom();
            }
            else if (data.type === 'step_start') {
              // thinking 비활성화
              const curThinking = [...assistantMsg.timeline].reverse().find(i => i.type === 'thinking');
              if (curThinking) curThinking.active = false;
              // step 추가
              assistantMsg.timeline.push({
                type: 'step',
                tool: data.tool,
                label: data.label,
                args: data.args || {},
                result: null,
                showResult: false,
                loading: true,
              });
              scrollToBottom();
            }
            else if (data.type === 'step_result') {
              const lastStep = [...assistantMsg.timeline].reverse().find(i => i.type === 'step');
              if (lastStep) {
                lastStep.result = data.result;
                lastStep.showResult = true;
                lastStep.loading = false;
              }
              scrollToBottom();
            }
            else if (data.type === 'token') {
              if (!assistantMsg.showAnswer) {
                // thinking 비활성화 + 답변 생성 대기 해제
                const curThinking = [...assistantMsg.timeline].reverse().find(i => i.type === 'thinking');
                if (curThinking) curThinking.active = false;
                assistantMsg.showAnswer = true;
              }
              assistantMsg.content += data.token;
              tokenBuffer += data.token;
              startTokenDisplay(assistantMsg);
            }
            else if (data.type === 'error') {
              assistantMsg.content = data.message;
              assistantMsg.displayedContent = data.message;
              assistantMsg.showAnswer = true;
              scrollToBottom();
            }
          } catch (e) { /* JSON parse error — skip */ }
        }

        boundary = buffer.indexOf('\n\n');
      }
    }

    // 스트림 종료 — 남은 토큰을 부드럽게 마저 출력
    await new Promise(resolve => {
      const check = setInterval(() => {
        if (displayPos >= tokenBuffer.length) {
          clearInterval(check);
          flushTokenDisplay(assistantMsg);
          resolve();
        }
      }, 50);
    });

  } catch (err) {
    const errorMsg = err.message || '오류가 발생했습니다. 다시 시도해주세요.';
    flushTokenDisplay(assistantMsg);
    if (!assistantMsg.displayedContent) {
      assistantMsg.content = errorMsg;
      assistantMsg.displayedContent = errorMsg;
      assistantMsg.showAnswer = true;
    }
    scrollToBottom();
  } finally {
    loading.value = false;
    streaming.value = false;
  }
}
</script>

<style scoped>
.coach-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: var(--dark);
  display: flex;
  flex-direction: column;
  color: var(--text);
  font-family: 'Outfit', sans-serif;
  z-index: 1000;
}

/* ===== Header (MyHistoryView 패턴) ===== */
.coach-header {
  text-align: center;
  padding: 2rem 2rem 1.5rem;
  position: relative;
  flex-shrink: 0;
}

.back-btn {
  position: absolute;
  top: 1rem;
  right: 0;
  background: none;
  border: none;
  color: #64748b;
  font-size: 2.5rem;
  cursor: pointer;
  line-height: 1;
  transition: color 0.2s;
}
.back-btn:hover {
  color: #f8fafc;
}

.badge {
  background: var(--primary);
  color: #fff;
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: 800;
  font-size: 0.75rem;
  margin-bottom: 0.5rem;
  letter-spacing: 1px;
}

.title {
  font-size: 2.5rem;
  font-weight: 900;
  color: #f8fafc;
  margin: 0;
}

.subtitle {
  color: var(--text-muted);
  font-size: 1.1rem;
  margin: 0;
}

/* ===== Chat Area ===== */
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-area::-webkit-scrollbar {
  width: 6px;
}
.chat-area::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}
.chat-area::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* ===== Preset Buttons ===== */
.preset-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 1.5rem;
}

.preset-label {
  font-size: 1.1rem;
  color: var(--text-muted);
  margin: 0;
  font-weight: 500;
}

.preset-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  max-width: 480px;
  width: 100%;
}

.preset-btn {
  background: var(--glass);
  border: 1px solid var(--glass-border);
  color: var(--text);
  padding: 1rem 1.25rem;
  border-radius: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.95rem;
  font-weight: 600;
  font-family: 'Outfit', sans-serif;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.preset-btn:hover {
  background: rgba(99, 102, 241, 0.1);
  border-color: var(--primary);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
}

.preset-icon {
  font-size: 1.25rem;
}

/* ===== Chat Bubbles (style.css 패턴) ===== */
.message-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.chat-bubble {
  max-width: 85%;
  padding: 0.8rem 1.2rem;
  border-radius: 12px;
  font-size: 0.95rem;
  line-height: 1.6;
  word-break: break-word;
}

.chat-bubble.user {
  align-self: flex-end;
  background: var(--primary);
  color: white;
  border-bottom-right-radius: 2px;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

.chat-bubble.assistant {
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
  border-bottom-left-radius: 2px;
  border: 1px solid var(--glass-border);
}

.chat-bubble.assistant :deep(h3),
.chat-bubble.assistant :deep(h4) {
  color: var(--secondary);
  margin: 0.5rem 0 0.25rem;
  font-family: 'Outfit', sans-serif;
}
.chat-bubble.assistant :deep(strong) {
  color: #fff;
}
.chat-bubble.assistant :deep(ul) {
  padding-left: 1.25rem;
  margin: 0.25rem 0;
}
.chat-bubble.assistant :deep(li) {
  margin: 0.15rem 0;
}

/* ===== Agent Thinking ===== */
.thinking-block {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  align-self: flex-start;
  padding: 0.45rem 0.85rem;
  background: rgba(255, 255, 255, 0.03);
  border-left: 3px solid rgba(99, 102, 241, 0.4);
  border-radius: 0 8px 8px 0;
  animation: stepSlideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.thinking-icon {
  font-size: 0.9rem;
}

.thinking-text {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-style: italic;
}

/* ===== Agent Steps ===== */
.step-block {
  align-self: flex-start;
  max-width: 85%;
  animation: stepSlideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes stepSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.step-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.75rem;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 8px 8px 0 0;
  font-size: 0.8rem;
  color: var(--primary);
}
.step-header.no-result {
  border-radius: 8px;
}

.step-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(99, 102, 241, 0.3);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-left: auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.step-icon {
  font-size: 0.85rem;
}

.step-label {
  font-weight: 700;
  letter-spacing: 0.3px;
}

.step-args {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.step-result {
  display: flex;
  gap: 0.4rem;
  padding: 0.5rem 0.75rem;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--glass-border);
  border-top: none;
  border-radius: 0 0 8px 8px;
  font-size: 0.75rem;
  animation: resultExpand 0.3s ease-out;
}

@keyframes resultExpand {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 500px;
  }
}

.result-icon {
  font-size: 0.8rem;
  flex-shrink: 0;
  margin-top: 1px;
}

.result-json {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.7rem;
  max-height: 200px;
  overflow-y: auto;
}

/* ===== Loading ===== */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  align-self: flex-start;
  padding: 0.6rem 1rem;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
}

.loading-dots {
  display: flex;
  gap: 4px;
}
.loading-dots span {
  width: 6px;
  height: 6px;
  background: var(--primary);
  border-radius: 50%;
  animation: dotPulse 1.2s infinite;
}
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotPulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1.2); }
}

.loading-text {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* ===== Input Area (style.css chat-input-wrapper 패턴) ===== */
.input-area {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 2rem;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid var(--glass-border);
  flex-shrink: 0;
}

.chat-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: white;
  font-size: 0.9rem;
  font-family: 'Outfit', sans-serif;
  outline: none;
  transition: border-color 0.3s;
}
.chat-input:focus {
  border-color: var(--primary);
}
.chat-input::placeholder {
  color: var(--text-muted);
}
.chat-input:disabled {
  opacity: 0.5;
}

.send-btn {
  background: var(--primary);
  color: #fff;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  font-family: 'Outfit', sans-serif;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}
.send-btn:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}
.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===== Intent Badge [2026-02-23] ===== */
.intent-badge {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
  border-left: 3px solid var(--primary);
  border-radius: 8px;
  align-self: flex-start;
  max-width: 85%;
  animation: intentSlideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes intentSlideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.intent-type {
  font-weight: 700;
  color: var(--primary);
  font-size: 0.9rem;
}

.intent-confidence {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.intent-reasoning {
  font-size: 0.85rem;
  color: var(--text);
  font-style: italic;
}
</style>
