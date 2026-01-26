<!--
수정일: 2026-01-26
수정내용: Composition API + Pinia stores로 리팩토링
-->
<template>
  <div id="app" v-cloak>
    <!-- [라우터 뷰 - Practice 페이지 (메인 레이아웃 없이 단독 표시)] -->
    <router-view v-if="isPracticePage"></router-view>

    <!-- [메인 페이지] -->
    <template v-else>
      <LandingView
        :isLoggedIn="auth.isLoggedIn"
        :userProteinShakes="auth.userProteinShakes"
        :chapters="game.chapters"
        :leaderboard="leaderboard"
        @go-to-playground="handleGoToPlayground"
        @open-unit="openUnitPopup"
      >
        <template #auth-buttons>
          <template v-if="!auth.isLoggedIn">
            <button class="btn-login-ref" @click="ui.openLogin">Login</button>
            <button class="btn-signup-ref" @click="ui.openSignUp">Sign Up</button>
          </template>
          <div v-else class="user-profile-v2">
            <div class="user-info-v2">
              <span class="user-name-v2">{{ auth.sessionNickname }}</span>
              <span class="user-rank-v2">ENGINEER</span>
            </div>
            <button class="btn-logout-v2" @click="auth.logout">Logout</button>
          </div>
        </template>
      </LandingView>

      <!-- [유닛 상세 팝업 모달] -->
      <transition name="fade">
        <div v-if="ui.isUnitModalOpen" class="modal-overlay" @click.self="ui.isUnitModalOpen = false">
          <div class="unit-detail-modal">
            <header class="unit-modal-header-v3">
              <div class="title-section-v3">
                <div class="unit-label-v3">
                  {{ game.activeUnit?.name === 'Debug Practice' ? 'DEBUG GYM' : 'UNIT ' + (game.chapters.indexOf(game.activeUnit) + 1) }}
                </div>
                <h2 class="unit-name-v3">
                  <template v-if="game.activeUnit?.name === 'Debug Practice'">
                    {{ game.currentDebugMode === 'bug-hunt' ? '🐞 Bug Hunt' : '✨ Vibe Code Clean Up' }}
                  </template>
                  <template v-else>
                    {{ game.activeUnit?.unitTitle || game.activeUnit?.problems?.[0]?.title || game.activeUnit?.name }}
                  </template>
                </h2>
              </div>
              <div style="display: flex; align-items: center;">
                <button class="guidebook-btn-v3" @click="handleGuidebookClick">
                  <span class="btn-icon-wrapper"><i data-lucide="book-open"></i></span>
                  GUIDEBOOK
                </button>
                <button class="close-btn-v3" @click="ui.isUnitModalOpen = false">&times;</button>
              </div>
            </header>

            <div class="unit-modal-body-v3">
              <div class="path-container-v3">
                <svg class="path-svg-v3" viewBox="0 0 800 1500">
                  <path class="path-line-v3" d="M400,100 L560,250 L280,400 L520,550 L360,700 L400,850 L480,1000 L320,1150 L560,1300 L400,1450" fill="none" stroke="rgba(148, 163, 184, 0.2)" stroke-width="3" stroke-dasharray="10,5" />
                </svg>

                <div v-for="(problem, pIdx) in displayProblems" :key="problem.id" class="node-platform-v3"
                :class="['node-' + pIdx, {
                  active: pIdx === currentMaxIdx,
                  unlocked: game.currentUnitProgress.includes(pIdx)
                }]"
                @click="isUnlocked(pIdx) && selectProblem(problem)">

                <div class="platform-glow-v3" v-if="pIdx === currentMaxIdx"></div>

                <div class="platform-circle-v3">
                  <template v-if="game.currentUnitProgress.includes(pIdx)">
                    <img v-if="pIdx === currentMaxIdx" src="/image/unit_duck.png" class="duck-on-node-v3">
                    <div style="width: 20px; height: 20px; background: #b6ff40; border-radius: 50%; box-shadow: 0 0 10px #b6ff40;"></div>
                  </template>
                  <template v-else>
                    <i data-lucide="lock" class="lock-icon-v3"></i>
                  </template>
                </div>

                <div class="node-label-premium">
                  {{ problem.displayNum || problem.title }} - {{ problem.title }}
                </div>
              </div>

              <!-- Decorative Locked Nodes -->
              <div v-for="i in displayLabelsCount" :key="'extra-' + i" class="node-platform-v3 locked"
                :class="'node-' + (displayProblems.length + i - 1)">
                <div class="platform-circle-v3">
                  <i data-lucide="lock" class="lock-icon-v3"></i>
                </div>
              </div>
            </div>
          </div>

            <footer class="unit-stats-bar-v3">
              <template v-if="game.activeUnit?.name === 'Debug Practice'">
                <button class="game-mode-btn bug-hunt" :class="{ 'active': game.currentDebugMode === 'bug-hunt' }" @click="selectGameMode('bug-hunt')">🐞 Bug Hunt</button>
                <button class="game-mode-btn vibe-cleanup" :class="{ 'active': game.currentDebugMode === 'vibe-cleanup' }" @click="selectGameMode('vibe-cleanup')">✨ Vibe Code Clean Up</button>
              </template>
              <template v-else>
                <div class="stat-pill-v3 active"><i data-lucide="check-circle" style="width: 16px;"></i>1개 활성화</div>
                <div class="stat-pill-v3 locked"><i data-lucide="lock" style="width: 16px;"></i>{{ (displayProblems.length || 1) + displayLabelsCount - 1 }}개 잠금</div>
              </template>
            </footer>
          </div>
        </div>
      </transition>
    </template>

    <!-- [전역 모달 통합 컨테이너] -->
    <GlobalModals />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUpdated, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useGameStore } from '@/stores/game';
import { useUiStore } from '@/stores/ui';

import './style.css';
import LandingView from './features/home/LandingView.vue';
import GlobalModals from './components/GlobalModals.vue';

// Stores
const auth = useAuthStore();
const game = useGameStore();
const ui = useUiStore();

// Router
const route = useRoute();
const router = useRouter();

// Local State
const leaderboard = ref([
  { id: 1, username: 'TopEngineer', solved: 45, shakes: 2450 },
  { id: 2, username: 'DjangoMaster', solved: 42, shakes: 2100 },
  { id: 3, username: 'VueNinja', solved: 38, shakes: 1850 },
  { id: 4, username: 'AgentZero', solved: 35, shakes: 1600 },
  { id: 5, username: 'OpsWizard', solved: 30, shakes: 1400 }
]);

// Computed
const isPracticePage = computed(() => {
  const practiceRoutes = ['LogicMirror', 'LogicMirrorTest', 'SystemArchitecturePractice', 'BugHunt', 'VibeCodeCleanUp', 'OpsPractice'];
  return practiceRoutes.includes(route?.name);
});

const displayProblems = computed(() => {
  if (game.activeUnit?.name === 'Debug Practice') {
    const title = game.currentDebugMode === 'bug-hunt' ? 'Bug Hunt' : 'Vibe Code Clean Up';
    return [{ id: game.currentDebugMode, title }];
  }
  return game.activeUnit?.problems || [];
});

const displayLabelsCount = computed(() => {
  const currentCount = displayProblems.value?.length || 0;
  return Math.max(0, 6 - currentCount);
});

const currentMaxIdx = computed(() => {
  return Math.max(...game.currentUnitProgress);
});

// Methods
function isUnlocked(pIdx) {
  return game.currentUnitProgress.includes(pIdx);
}

function openUnitPopup(unit) {
  if (!auth.isLoggedIn) {
    ui.isAuthRequiredModalOpen = true;
    return;
  }
  game.setActiveUnit(unit);
  if (unit?.name === 'Debug Practice') {
    game.currentDebugMode = 'bug-hunt';
  }
  ui.isUnitModalOpen = true;
  nextTick(() => {
    if (window.lucide) window.lucide.createIcons();
  });
}

function selectProblem(problem) {
  if (!auth.isLoggedIn) {
    ui.isAuthRequiredModalOpen = true;
    return;
  }

  game.activeProblem = problem;
  game.activeChapter = game.activeUnit;
  ui.isUnitModalOpen = false;

  const chapterName = game.activeUnit?.name;

  if (chapterName === 'Pseudo Practice') {
    game.selectedQuestIndex = problem.questIndex || 0;
    ui.isLogicMirrorOpen = true;
  } else if (chapterName === 'System Practice') {
    router.push('/practice/system-architecture');
  } else if (chapterName === 'Debug Practice') {
    if (game.currentDebugMode === 'bug-hunt') {
      router.push('/practice/bug-hunt');
    } else {
      router.push('/practice/vibe-cleanup');
    }
  } else if (chapterName === 'Ops Practice') {
    router.push('/practice/ops-practice');
  } else if (chapterName === 'Agent Practice') {
    ui.isAgentModalOpen = true;
    nextTick(() => {
      if (window.lucide) window.lucide.createIcons();
    });
  } else {
    ui.isConstructionModalOpen = true;
  }
}

function selectGameMode(mode) {
  game.currentDebugMode = mode;
  if (game.activeUnit?.name === 'Debug Practice') {
    const isDebugRoute = ['BugHunt', 'VibeCodeCleanUp'].includes(route.name);
    if (isDebugRoute) {
      const nextPath = mode === 'bug-hunt' ? '/practice/bug-hunt' : '/practice/vibe-cleanup';
      router.push(nextPath);
    }
  }
  nextTick(() => {
    if (window.lucide) window.lucide.createIcons();
  });
}

function handleGoToPlayground() {
  if (auth.isLoggedIn) {
    document.getElementById('chapters')?.scrollIntoView({ behavior: 'smooth' });
  } else {
    ui.isAuthRequiredModalOpen = true;
  }
}

function handleGuidebookClick() {
  ui.isGuidebookOpen = true;
}

// Lifecycle
onMounted(() => {
  auth.checkSession();
  game.initGame();
  nextTick(() => {
    if (window.lucide) window.lucide.createIcons();
  });
});

onUpdated(() => {
  nextTick(() => {
    if (window.lucide) window.lucide.createIcons();
  });
});
</script>

<style scoped>
/* 게임 모드 선택 버튼 스타일 */
.game-mode-btn {
  flex: 1;
  padding: 18px 30px;
  font-family: 'Orbitron', sans-serif;
  font-weight: bold;
  font-size: 1.1em;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.game-mode-btn.bug-hunt {
  background: linear-gradient(135deg, #ff00ff, #ff4db8);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 0, 255, 0.3);
}

.game-mode-btn.bug-hunt:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(255, 0, 255, 0.5);
}

.game-mode-btn.vibe-cleanup {
  background: linear-gradient(135deg, #ffff00, #ffd700);
  color: #1a1f2e;
  box-shadow: 0 4px 15px rgba(255, 255, 0, 0.3);
}

.game-mode-btn.vibe-cleanup:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(255, 255, 0, 0.5);
}

/* Auth Buttons for LandingView Slot */
.btn-login-ref, .btn-signup-ref {
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.btn-login-ref {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.btn-signup-ref {
  background: #6366f1;
  color: #fff;
  margin-left: 0.5rem;
}

.btn-login-ref:hover, .btn-signup-ref:hover {
  transform: translateY(-2px);
  filter: brightness(1.2);
}

.user-profile-v2 {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info-v2 {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.user-name-v2 {
  font-weight: 800;
  color: #fff;
  font-size: 0.9rem;
}

.user-rank-v2 {
  font-size: 0.7rem;
  color: #b6ff40;
  font-weight: 900;
}

.btn-logout-v2 {
  background: rgba(255, 75, 75, 0.1);
  color: #ff4b4b;
  border: 1px solid rgba(255, 75, 75, 0.2);
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
}
</style>
