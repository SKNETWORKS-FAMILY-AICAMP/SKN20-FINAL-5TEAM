import { defineStore } from 'pinia';
import axios from 'axios';

/**
 * [수정일: 2026-01-24]
 * [수정내용: App.vue의 인증 로직을 분리한 전역 인증 스토어]
 */
export const useAuthStore = defineStore('auth', {
    state: () => ({
        isLoggedIn: false,
        sessionNickname: '',
        userProteinShakes: 420 // 초기/더미 값
    }),

    actions: {
        async checkSession() {
            try {
                const response = await axios.get('/api/core/auth/me/');
                if (response.data.isAuthenticated) {
                    this.isLoggedIn = true;
                    this.sessionNickname = response.data.user.nickname || response.data.user.username;
                } else {
                    this.isLoggedIn = false;
                }
            } catch (error) {
                this.isLoggedIn = false;
            }
        },

        async logout() {
            try {
                await axios.post('/api/core/auth/logout/');
                this.isLoggedIn = false;
                this.sessionNickname = '';
            } catch (error) {
                console.error('Logout failed:', error);
                this.isLoggedIn = false;
                this.sessionNickname = '';
            }
        },

        setLoginSuccess(user) {
            this.isLoggedIn = true;
            this.sessionNickname = typeof user === 'string' ? user.split('@')[0] : (user.nickname || user.username);
        }
    }
});
