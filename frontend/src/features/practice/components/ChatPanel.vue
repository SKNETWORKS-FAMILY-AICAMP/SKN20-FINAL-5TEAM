<template>
  <div class="chat-section">
    <h3 class="section-title">💬 AI Assistant</h3>
    <div class="chat-container">
      <div class="chat-messages" ref="chatMessages">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="chat-message"
          :class="[msg.role, msg.type]"
        >
          <div class="message-header">
            <span class="message-role">{{ msg.role === 'user' ? '👤 You' : '🤖 AI' }}</span>
            <span v-if="msg.type" class="message-type-badge" :class="msg.type">
              {{ getMessageTypeLabel(msg.type) }}
            </span>
          </div>
          <p class="message-content">{{ msg.content }}</p>
        </div>
        <div v-if="isLoading" class="chat-message assistant">
          <span class="message-role">🤖 AI</span>
          <p class="message-content typing-indicator">생각 중...</p>
        </div>
      </div>
      <div class="chat-input-area">
        <input
          type="text"
          v-model="inputText"
          @keyup.enter="sendMessage"
          placeholder="아키텍처에 대해 질문하세요..."
          :disabled="isLoading"
          class="chat-input"
        />
        <button
          @click="sendMessage"
          :disabled="isLoading || !inputText.trim()"
          class="chat-send-btn"
        >
          전송
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChatPanel',
  props: {
    messages: {
      type: Array,
      default: () => []
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['send-message'],
  data() {
    return {
      inputText: ''
    };
  },
  watch: {
    messages: {
      handler() {
        this.scrollToBottom();
      },
      deep: true
    }
  },
  methods: {
    sendMessage() {
      if (!this.inputText.trim() || this.isLoading) return;
      this.$emit('send-message', this.inputText.trim());
      this.inputText = '';
    },
    scrollToBottom() {
      this.$nextTick(() => {
        if (this.$refs.chatMessages) {
          this.$refs.chatMessages.scrollTop = this.$refs.chatMessages.scrollHeight;
        }
      });
    },
    getMessageTypeLabel(type) {
      const labels = {
        'requirement': '📋 요구사항',
        'component': '🧩 컴포넌트',
        'tradeoff': '⚖️ 트레이드오프',
        'scaling': '📈 확장성',
        'general': '💬 일반',
        'followup': '🎯 꼬리질문',
        'answer': '💡 답변',
        'error': '⚠️ 오류'
      };
      return labels[type] || '';
    }
  }
};
</script>

<style scoped>
.chat-section {
  padding: 0 20px 20px;
}

.section-title {
  font-family: 'Space Mono', monospace;
  font-size: 1em;
  color: #64b5f6;
  margin: 0 0 10px 0;
}

.chat-container {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  border: 1px solid rgba(100, 181, 246, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 300px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-message {
  padding: 10px 14px;
  border-radius: 12px;
  max-width: 90%;
}

.chat-message.user {
  align-self: flex-end;
  background: linear-gradient(135deg, #64b5f6, #2196f3);
  color: #fff;
}

.chat-message.assistant {
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(100, 181, 246, 0.3);
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.message-role {
  font-size: 0.75em;
  font-weight: 700;
  opacity: 0.8;
}

.message-content {
  margin: 0;
  font-size: 0.9em;
  line-height: 1.5;
}

.typing-indicator {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Message Type Badges */
.message-type-badge {
  font-size: 0.7em;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
}

.message-type-badge.requirement {
  background: rgba(0, 255, 157, 0.2);
  color: #00ff9d;
  border: 1px solid rgba(0, 255, 157, 0.4);
}

.message-type-badge.component {
  background: rgba(171, 71, 188, 0.2);
  color: #ba68c8;
  border: 1px solid rgba(171, 71, 188, 0.4);
}

.message-type-badge.tradeoff {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
  border: 1px solid rgba(255, 193, 7, 0.4);
}

.message-type-badge.scaling {
  background: rgba(255, 71, 133, 0.2);
  color: #ff4785;
  border: 1px solid rgba(255, 71, 133, 0.4);
}

.message-type-badge.general {
  background: rgba(100, 181, 246, 0.2);
  color: #64b5f6;
  border: 1px solid rgba(100, 181, 246, 0.4);
}

.message-type-badge.followup {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
  border: 1px solid rgba(255, 152, 0, 0.4);
}

.message-type-badge.answer {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
  border: 1px solid rgba(76, 175, 80, 0.4);
}

.message-type-badge.error {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
  border: 1px solid rgba(244, 67, 54, 0.4);
}

.chat-input-area {
  display: flex;
  gap: 10px;
  padding: 12px;
  border-top: 1px solid rgba(100, 181, 246, 0.2);
  background: rgba(0, 0, 0, 0.2);
}

.chat-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(100, 181, 246, 0.3);
  border-radius: 8px;
  padding: 10px 14px;
  color: #e0e0e0;
  font-family: 'Space Mono', monospace;
  font-size: 0.9em;
}

.chat-input:focus {
  outline: none;
  border-color: #64b5f6;
}

.chat-input::placeholder {
  color: rgba(224, 224, 224, 0.5);
}

.chat-send-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #00ff9d, #00e676);
  border: none;
  border-radius: 8px;
  color: #0a0e27;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.chat-send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.chat-send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
