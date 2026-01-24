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

    <!-- [Logic Mirror 실습 모달] - Unit 1 전용 (수정일: 2026-01-24) -->
    <transition name="fade">
       <LogicMirror 
           v-if="ui.isLogicMirrorOpen" 
           :initialQuestIndex="game.selectedQuestIndex"
           @close="handleCloseLogicMirror"
           @quest-complete="(idx) => game.unlockNextStage('Pseudo Practice', idx)"
       />
    </transition>

    <!-- [Logic Mirror 가이드북 모달] - Unit 1 전용 (수정일: 2026-01-24) -->
    <LogicMirrorGuidebook 
        :isOpen="ui.isGuidebookOpen" 
        @close="ui.isGuidebookOpen = false"
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
  </div>
</template>

<script setup>
import { useUiStore } from '@/stores/ui';
import { useAuthStore } from '@/stores/auth';
import { useGameStore } from '@/stores/game';
import { useRouter } from 'vue-router';

import NoticeModal from './NoticeModal.vue';
import LoginModal from './LoginModal.vue';
import SignUpModal from './SignUpModal.vue';
import ConstructionModal from './ConstructionModal.vue';
import LogicMirror from '../features/practice/support/unit1/logic-mirror/LogicMirror.vue';
import LogicMirrorGuidebook from '../features/practice/support/unit1/logic-mirror/LogicMirrorGuidebook.vue';

/**
 * [수정일: 2026-01-24]
 * [수정내용: App.vue의 모든 모달 로직을 통합 관리하는 글로벌 모달 컨테이너 생성]
 */

const ui = useUiStore();
const auth = useAuthStore();
const game = useGameStore();
const router = useRouter();

const onLoginSuccess = (user) => {
    auth.setLoginSuccess(user);
    ui.isLoginModalOpen = false;
};

const onSignUpSuccess = (nickname) => {
    auth.isLoggedIn = true;
    auth.sessionNickname = nickname;
    ui.isSignUpModalOpen = false;
};

const handleCloseLogicMirror = () => {
    // [2026-01-24] 라우트 기반 모달이므로 닫을 때 메인으로 주소 이동
    ui.isLogicMirrorOpen = false;
    router.push('/');
    ui.isUnitModalOpen = true; // 실습 종료 후 다시 유닛 선택창 노출
};

</script>
