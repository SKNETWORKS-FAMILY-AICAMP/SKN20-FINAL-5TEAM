<template>
  <div class="global-modals">
    <!-- [공지사항 모달] -->
    <NoticeModal :isOpen="ui.isNoticeOpen" @close="ui.isNoticeOpen = false" />

    <!-- [로그인 모달] -->
    <LoginModal 
        :isOpen="ui.isLoginModalOpen" 
        @close="ui.isLoginModalOpen = false"
        @login-success="onLoginSuccess"
        @request-signup="ui.isLoginModalOpen = false; ui.isSignUpModalOpen = true"
    />

    <!-- [회원가입 모달] -->
    <SignUpModal
        :isOpen="ui.isSignUpModalOpen"
        @close="ui.isSignUpModalOpen = false"
        @signup-success="onSignUpSuccess"
    />

    <!-- [회원 정보 수정 모달] -->
    <ProfileSettingsModal
        :isOpen="ui.isProfileSettingsModalOpen"
        @close="ui.isProfileSettingsModalOpen = false"
    />

     <!-- [접근 제한 안내 모달] -->
     <transition name="fade">
        <div v-if="ui.isAuthRequiredModalOpen" class="modal-overlay" @click.self="ui.isAuthRequiredModalOpen = false">
            <div class="auth-container playground-auth-card">
                <div class="playground-header-icon">
                    <i data-lucide="party-popper" class="bounce-icon"></i>
                </div>
                <header class="auth-header">
                    <div class="auth-badge warning">STOP! ACCESS RESTRICTED</div>
                    <h2 class="auth-title">놀이터 입장 전 확인! 🚧</h2>
                    <p class="auth-subtitle">
                        아키텍처 놀이터의 모든 시설을 이용하시려면<br>
                        엔지니어 신원 확인(로그인)이 필요합니다.
                    </p>
                </header>

                <div class="playground-perks">
                    <div class="perk-item">
                        <i data-lucide="check-circle" class="perk-icon"></i>
                        <span>모든 훈련 스테이지 오픈</span>
                    </div>
                    <div class="perk-item">
                        <i data-lucide="check-circle" class="perk-icon"></i>
                        <span>단백질 쉐이크 보상 획득</span>
                    </div>
                    <div class="perk-item">
                        <i data-lucide="check-circle" class="perk-icon"></i>
                        <span>실시간 랭킹 시스템 반영</span>
                    </div>
                </div>

                <footer class="auth-footer" style="flex-direction: column; gap: 0.8rem; margin-top: 1.5rem;">
                    <button class="btn btn-primary" @click="ui.isAuthRequiredModalOpen = false; ui.isSignUpModalOpen = true"
                        style="width: 100%; height: 55px; font-size: 1.1rem;">
                        무료로 회원가입하고 입장하기
                    </button>
                    <button class="btn btn-secondary" @click="ui.isAuthRequiredModalOpen = false; ui.isLoginModalOpen = true"
                        style="width: 100%; border: none;">
                        이미 계정이 있나요? 로그인
                    </button>
                    <button class="btn-text" @click="ui.isAuthRequiredModalOpen = false"
                        style="background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 0.85rem; margin-top: 0.5rem;">
                        다음에 할게요
                    </button>
                </footer>
            </div>
        </div>
     </transition>

     <!-- [공사중 안내 모달] -->
     <ConstructionModal 
        :isOpen="ui.isConstructionModalOpen" 
        @close="ui.isConstructionModalOpen = false" 
     />

    <!-- [에이전트 실습 워크스페이스] -->
    <transition name="fade">
      <div v-if="ui.isAgentModalOpen" class="modal-overlay">
        <div class="workspace-container">
            <!-- 에이전트 실습 UI 내용 (생략 가능하나 기능 유지를 위해 App.vue에서 이전) -->
            <header class="workspace-header">
                <div class="header-left">
                    <span class="badge bg-medium">{{ game.activeChapter?.name }}</span>
                    <h2 style="margin-top: 0.5rem;">{{ game.activeProblem?.title }}</h2>
                </div>
                <button class="btn-close" @click="ui.isAgentModalOpen = false">&times;</button>
            </header>
            <!-- ... 나머지 Agent 실습 바디 ... -->
            <div class="workspace-body" style="padding: 2rem; color: white;">
                Agent Practice Workspace (Refactored)
            </div>
            <footer class="workspace-footer">
                <button class="btn btn-secondary" @click="ui.isAgentModalOpen = false">닫기</button>
            </footer>
        </div>
      </div>
    </transition>
    <!-- [전역 토스트 알림] -->
    <GlobalToast />

    <!-- [Job Planner 모달] -->
    <JobPlannerModal
        :isOpen="ui.isJobPlannerModalOpen"
        @close="ui.isJobPlannerModalOpen = false"
    />
  </div>
</template>

<script setup>
// [2026-02-12] Global Modals Container
import { useUiStore } from '@/stores/ui';
import { useAuthStore } from '@/stores/auth';
import { useGameStore } from '@/stores/game';
import { useRouter } from 'vue-router';

import NoticeModal from './NoticeModal.vue';
import LoginModal from './LoginModal.vue';
import SignUpModal from './SignUpModal.vue';
import ConstructionModal from './ConstructionModal.vue';
import ProfileSettingsModal from './ProfileSettingsModal.vue';
import GlobalToast from './GlobalToast.vue'; // [수정일: 2026-02-16] 전역 토스트 추가
import JobPlannerModal from '../features/job_planner/components/JobPlannerModal.vue';

/**
 * [수정일: 2026-01-24] 
 * [수정내용: App.vue의 모든 모달 로직을 통합 관리하는 글로벌 모달 컨테이너 생성]
 */

const ui = useUiStore();
const auth = useAuthStore();
const game = useGameStore();
const router = useRouter();

const onLoginSuccess = async (user) => {
    auth.setLoginSuccess(user);
    ui.isLoginModalOpen = false;

    // [수정일: 2026-02-27] 로그인 성공 시 새 사용자의 진행도 로드
    const { useProgressStore } = await import('@/stores/progress');
    const progressStore = useProgressStore();
    await progressStore.fetchAllProgress();

    // [수정일: 2026-02-16] 로그인 성공 시 사용자 환영 메시지 표시 (Toast 적용)
    const nickname = (user && (user.nickname || user.username)) || auth.sessionNickname || '엔지니어';
    ui.showToast(`${nickname}님, 환영합니다! AI-Arcade 보안 시스템에 접속되었습니다.`, 'success');
};

const onSignUpSuccess = async (nickname) => {
    auth.isLoggedIn = true;
    auth.sessionNickname = nickname;
    ui.isSignUpModalOpen = false;

    // [수정일: 2026-02-27] 회원가입 성공 시 진행도 로드
    const { useProgressStore } = await import('@/stores/progress');
    await useProgressStore().fetchAllProgress();
};

const handleClosePseudoCode = () => {
    // [2026-01-27] Pseudo Code 페이지 종료 시 메인으로 이동
    ui.isPseudoCodeOpen = false;
    router.push('/');
    ui.isUnitModalOpen = true; 
};

</script>
