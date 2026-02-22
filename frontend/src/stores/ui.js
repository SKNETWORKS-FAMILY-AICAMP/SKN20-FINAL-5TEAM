import { defineStore } from 'pinia';

/**
 * [수정일: 2026-01-24]
 * [수정내용: App.vue의 모달 제어 상태를 분리한 UI 스토어]
 */
export const useUiStore = defineStore('ui', {
    state: () => ({
        isNoticeOpen: true,
        isLoginModalOpen: false,
        isSignUpModalOpen: false,
        isAuthRequiredModalOpen: false,
        isUnitModalOpen: false,
        isConstructionModalOpen: false,
        isPseudoCodeOpen: false,
        isGuidebookOpen: false,
        isAgentModalOpen: false,
        isReportModalOpen: false,
        isProfileSettingsModalOpen: false,
        isJobPlannerModalOpen: false,
        isLearningAnalyticsOpen: false,

        // [수정일: 2026-02-16] 전역 토스트 알림 상태
        toast: {
            show: false,
            message: '',
            type: 'success', // 'success', 'error', 'info', 'warning'
            duration: 3000
        }
    }),

    actions: {
        /**
         * [전역 토스트 표시]
         * @param {string} message 표시할 메시지
         * @param {string} type 토스트 타입 (success, error, info, warning)
         */
        showToast(message, type = 'success') {
            this.toast.message = message;
            this.toast.type = type;
            this.toast.show = true;

            setTimeout(() => {
                this.toast.show = false;
            }, this.toast.duration);
        },

        closeAllModals() {
            this.isLoginModalOpen = false;
            this.isSignUpModalOpen = false;
            this.isAuthRequiredModalOpen = false;
            this.isUnitModalOpen = false;
            this.isConstructionModalOpen = false;
            this.isPseudoCodeOpen = false;
            this.isGuidebookOpen = false;
            this.isAgentModalOpen = false;
            this.isReportModalOpen = false;
            this.isJobPlannerModalOpen = false;
            this.isLearningAnalyticsOpen = false;
        },

        openLogin() { this.isLoginModalOpen = true; },
        openSignUp() { this.isSignUpModalOpen = true; },
        openUnit() { this.isUnitModalOpen = true; }
    }
});
