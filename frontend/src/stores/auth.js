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
        userProteinShakes: 420, // 초기/더미 값
        userAvatarUrl: null,    // [수정일: 2026-02-06] 나노바나나 아바타 URL
        userRank: 'BRONZE',     // [수정일: 2026-02-06] 현재 등급
        user: null              // [수정일: 2026-02-06] 전체 유저 데이터 (프로필 수정용)
    }),

    actions: {
        /**
         * [세션 체크]
         * - 앱 초기화 시 백엔드(/api/core/auth/me/)를 호출하여 현재 유효한 로그인 세션이 있는지 확인합니다.
         */
        async checkSession() {
            try {
                // [2026-01-25] 서버로부터 인증 여부와 유저 정보 조회
                const response = await axios.get('/api/core/auth/me/');
                if (response.data.isAuthenticated && response.data.user) {
                    this.isLoggedIn = true;
                    this.sessionNickname = response.data.user.nickname || response.data.user.username;

                    // [수정일: 2026-02-07] 새 사용자 정보로 완전히 갱신 (이전 상태 잔류 방지)
                    this.userProteinShakes = 0;
                    this.userRank = 'BRONZE';
                    this.userAvatarUrl = null;

                    // [수정일: 2026-02-06] 활동 및 아바타 정보 동기화
                    if (response.data.user.activity) {
                        this.userProteinShakes = response.data.user.activity.total_points || 0;
                        this.userRank = response.data.user.activity.current_rank || 'BRONZE';
                        if (response.data.user.activity.active_avatar) {
                            this.userAvatarUrl = response.data.user.activity.active_avatar.image_url;
                        }
                    }
                    // [수정일: 2026-02-07] active_avatar 최상위 필드에서도 확인 (LoginView 응답 호환)
                    if (!this.userAvatarUrl && response.data.user.active_avatar?.image_url) {
                        this.userAvatarUrl = response.data.user.active_avatar.image_url;
                    }
                    // [수정일: 2026-02-06] 전체 유저 객체 보관 (수정 페이지용)
                    this.user = response.data.user;
                } else {
                    this.isLoggedIn = false;
                    this.sessionNickname = '';
                    this.userAvatarUrl = null;
                    this.user = null;
                }
            } catch (error) {
                console.error("Session check failed:", error);
                this.isLoggedIn = false;
                this.sessionNickname = '';
                this.userAvatarUrl = null;
            }
        },

        /**
         * [로그인 요청]
         * - 사용자로부터 입력받은 이메일/비밀번호로 백엔드 인증을 요청합니다.
         */
        async login(email, password) {
            try {
                // [2026-01-25] CSRF 토큰이 헤더에 포함되어 전송됨 (main.js 설정 덕분)
                const response = await axios.post('/api/core/auth/login/', {
                    email,
                    password
                });

                if (response.status === 200 && response.data.user) {
                    this.setLoginSuccess(response.data.user);
                    return { success: true };
                }
                return { success: false, error: '응답 형식이 올바르지 않습니다.' };
            } catch (error) {
                // 서버 에러 메시지가 있으면 반환, 없으면 기본 메시지
                const msg = error.response?.data?.error || '로그인 서버와 통신 중 오류가 발생했습니다.';
                return { success: false, error: msg };
            }
        },

        /**
         * [로그아웃]
         * - 서버 세션을 종료하고 클라이언트의 인증 상태를 초기화합니다.
         */
        async logout() {
            try {
                await axios.post('/api/core/auth/logout/');
                this.isLoggedIn = false;
                this.sessionNickname = '';
            } catch (error) {
                console.error('Logout failed:', error);
                // 네트워크 오류 등으로 실패하더라도 클라이언트 상태는 초기화하여 보안 유지
                this.isLoggedIn = false;
                this.sessionNickname = '';
            }
        },

        /**
         * [로그인/가입 성공 상태 반영]
         * - 전달받은 유저 객체에서 화면에 표시할 닉네임을 추출하여 저장합니다.
         */
        setLoginSuccess(user) {
            if (!user) return;
            this.isLoggedIn = true;
            // [2026-01-25] 유연한 닉네임 추출 로직 (객체인 경우와 이메일 문자열인 경우 모두 대응)
            if (typeof user === 'string') {
                this.sessionNickname = user.split('@')[0];
                this.userAvatarUrl = null;
            } else {
                this.sessionNickname = user.nickname || user.username || user.user_nickname || 'ENGINEER';
                // [수정일: 2026-02-07] 아바타 정보 동기화
                this.userAvatarUrl = user.activity?.active_avatar?.image_url
                    || user.active_avatar?.image_url
                    || null;
                this.userProteinShakes = user.activity?.total_points || 0;
                this.userRank = user.activity?.current_rank || 'BRONZE';
            }
            // [수정일: 2026-02-06] 유저 객체 저장
            this.user = user;
        }
    }
});
