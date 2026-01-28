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
        isReportModalOpen: false
    }),

    actions: {
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
        },

        openLogin() { this.isLoginModalOpen = true; },
        openSignUp() { this.isSignUpModalOpen = true; },
        openUnit() { this.isUnitModalOpen = true; }
    }
});
