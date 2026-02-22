/**
 * 작성일: 2026-02-21
 * 작성자: 프론트엔드 에이전트
 * 작성내용: 
 * - 모의 면접 시스템 전용 상태 관리 스토어 (Pinia)
 * - 백엔드 SSE 스트림에서 수신되는 청크(chunk) 단위 텍스트를 `currentTypingMessage`에 누적하여 상태를 업데이트함.
 * - 메시지 배열(`messages`) 및 현재 타이핑 상태(`isTyping`)를 분리 관리하여 기존 파일과 충돌 없이 독립적으로 동작하게 함.
 */
import { defineStore } from 'pinia';

export const useInterviewStore = defineStore('interview', {
    state: () => ({
        messages: [], // Message objects: { role: 'interviewer' | 'user', content: string }
        isTyping: false,
        currentTypingMessage: '', // 임시로 타이핑 중인 메시지

        // [수정일: 2026-02-21] 상태 고도화 플랜 적용
        status: 'idle', // 'idle' | 'running' | 'error' | 'finished'
        errorMessage: '',
        summary: null,

        // [수정일: 2026-02-22] Job Planner 파싱/분석 연동 데이터
        jobPlannerData: null
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
        setStatus(status, errorMsg = '') {
            this.status = status;
            this.errorMessage = errorMsg;
        },
        setSummary(summaryData) {
            this.summary = summaryData;
            this.status = 'finished';
        },
        clearMessages() {
            this.messages = [];
            this.currentTypingMessage = '';
            this.isTyping = false;
            this.status = 'idle';
            this.errorMessage = '';
            this.summary = null;
        },
        setJobPlannerData(data) {
            this.jobPlannerData = data;
        }
    }
});
