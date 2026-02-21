import { defineStore } from 'pinia';

export const useInterviewStore = defineStore('interview', {
    state: () => ({
        messages: [], // Message objects: { role: 'interviewer' | 'user', content: string }
        isTyping: false,
        currentTypingMessage: '' // 임시로 타이핑 중인 메시지
    }),
    actions: {
        setTypingStatus(status) {
            this.isTyping = status;
        },
        appendChunk(chunk) {
            this.currentTypingMessage += chunk;
        },
        finalizeMessage() {
            if (this.currentTypingMessage.trim()) {
                this.messages.push({
                    role: 'interviewer',
                    content: this.currentTypingMessage
                });
                this.currentTypingMessage = '';
            }
            this.isTyping = false;
        },
        addUserMessage(content) {
            this.messages.push({
                role: 'user',
                content: content
            });
        },
        clearMessages() {
            this.messages = [];
            this.currentTypingMessage = '';
            this.isTyping = false;
        }
    }
});
