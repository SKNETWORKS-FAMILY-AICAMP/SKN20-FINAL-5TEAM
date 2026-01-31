<!--
수정일: 2026-01-31
수정내용: 
1. 캐릭터 브랜딩 전면 교체: 'Lion' 명칭을 'Coduck'으로 변경하고 픽사 스타일 캐릭터 이미지 적용.
2. 유닛 2/3 로딩 문제 해결: displayProblems 계산 시 매번 최신 데이터를 매핑하도록 수정하여 캐시 및 캐스팅 이슈 해결.
3. 유닛 매칭 유연화: 유닛 제목 비교 시 대소문자 및 공백을 무시하도록 정규화 로직 도입.
-->
<template>
  <div id="app" v-cloak>
    <!-- [메인 페이지 배경 (맵)] -->
    <LandingView
      v-if="!isPracticePage"
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

    <!-- [라우터 뷰 - Practice 페이지 (HUD 오버레이 스타일)] -->
    <router-view v-if="isPracticePage" @close="handlePracticeClose"></router-view>

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
                  <template v-else-if="game.activeUnit?.name === 'Pseudo Practice'">
                    <!-- [수정일: 2026-01-31] 유닛 1 모드 통합: AI Detective, Pseudo Forest 등의 개별 타이틀을 제거하고 통합 타이틀로 표시 -->
                    💻 Pseudo Code Practice
                  </template>
                  <template v-else>
                    {{ game.activeUnit?.unitTitle || (game.activeUnit?.problems && game.activeUnit.problems[0]?.title) || game.activeUnit?.name || 'Loading...' }}
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
                  active: problem.questIndex === currentMaxIdx,
                  unlocked: game.currentUnitProgress.includes(problem.questIndex)
                }]"
                @click="isUnlocked(problem.questIndex) && selectProblem(problem)">

                <div class="platform-glow-v3" v-if="problem.questIndex === currentMaxIdx"></div>

                <div class="platform-circle-v3">
                  <template v-if="game.currentUnitProgress.includes(problem.questIndex)">
                    <img v-if="problem.questIndex === currentMaxIdx" src="/image/unit_duck.png" class="duck-on-node-v3">
                    <div style="width: 20px; height: 20px; background: #b6ff40; border-radius: 50%; box-shadow: 0 0 10px #b6ff40;"></div>
                  </template>
                  <template v-else>
                    <i data-lucide="lock" class="lock-icon-v3"></i>
                  </template>
                </div>

                <div class="node-label-premium">
                  <template v-if="game.activeUnit?.name === 'Debug Practice' && game.currentDebugMode === 'vibe-cleanup'">
                    개발중..
                  </template>
                  <template v-else>
                    {{ problem.displayNum || problem.title }} - {{ problem.title }}
                  </template>
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
              <!-- [수정일: 2026-01-31] Unit 1(Pseudo Practice) 전용 하단 모드 전환 버튼 제거 -->
              <!-- 기존의 ai detective, pseudo forest 등 모드 전환 기능을 제거하고 통합된 연습 경험을 제공합니다. -->

              <!-- 기존 Debug Practice 모드 전환 버튼 -->
              <template v-if="game.activeUnit?.name === 'Debug Practice'">
                <button class="game-mode-btn bug-hunt" :class="{ 'active': game.currentDebugMode === 'bug-hunt' }" @click="selectGameMode('bug-hunt')">🐞 Bug Hunt</button>
                <button class="game-mode-btn vibe-cleanup" :class="{ 'active': game.currentDebugMode === 'vibe-cleanup' }" @click="selectGameMode('vibe-cleanup')">✨ Vibe Code Clean Up</button>
              </template>

              <!-- 일반 상태 표시 (진행도/잠금) -->
              <template v-else>
                <div class="stat-pill-v3 active"><i data-lucide="check-circle" style="width: 16px;"></i>{{ game.currentUnitProgress.length }}개 활성화</div>
                <div class="stat-pill-v3 locked"><i data-lucide="lock" style="width: 16px;"></i>{{ displayProblems.length - game.currentUnitProgress.length }}개 잠금</div>
              </template>
            </footer>
          </div>
        </div>
      </transition>

    <!-- [전역 모달 통합 컨테이너] -->
    <GlobalModals />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUpdated, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useGameStore } from '@/stores/game';
import { useUiStore } from '@/stores/ui';

import './style.css';
import LandingView from './features/home/LandingView.vue';
import GlobalModals from './components/GlobalModals.vue';
import progressiveData from './features/practice/progressive-problems.json';

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

// [수정일: 2026-01-31] 미사용 상태 제거 (모드 통합으로 인해 불필요)
// const detectiveLevel = ref('초급');

// Computed
const isPracticePage = computed(() => {
  // PseudoCode는 페이지/모달 하이브리드로 동작 (isPracticePage에 포함하여 배경 제어)
  const practiceRoutes = [
    'PseudoCode',
    'SystemArchitecturePractice', 
    'BugHunt', 
    'BugHuntDemo', // [수정일: 2026-01-30] BugHunt Demo 라우트 추가
    'VibeCodeCleanUp', 
    'OpsPractice'
  ];
  return practiceRoutes.includes(route?.name);
});


const displayProblems = computed(() => {
  const activeUnit = game.activeUnit;
  if (!activeUnit) return [];

  // [수정일: 2026-01-31] 모든 유닛에 대해 최신 매핑 데이터 사용 (일부 유닛의 캐시 문제 해결)
  const unitIndex = game.chapters.indexOf(activeUnit);
  const problems = game.mapDetailsToProblems(activeUnit, unitIndex + 1);
  const unitName = (activeUnit.name || '').toLowerCase().replace(/\s+/g, '');

  if (unitName === 'debugpractice' && game.currentDebugMode !== 'bug-hunt') {
    // Vibe 문제 세트가 있으면 우선 사용
    const vibeProblems = activeUnit.vibeProblems || [];
    return vibeProblems.length > 0 ? vibeProblems : problems;
  }

  return problems;
});

const displayLabelsCount = computed(() => {
  const currentCount = displayProblems.value?.length || 0;
  const targetCount = game.activeUnit?.name === 'Debug Practice' ? 7 : 10;
  return Math.max(0, targetCount - currentCount);
});

const currentMaxIdx = computed(() => {
  const progress = game.currentUnitProgress;
  const displayedIndices = displayProblems.value.map(p => p.questIndex);
  if (displayedIndices.length === 0) return 0;

  // [수정일: 2026-01-28] 현재 화면에 표시된 문제들 중 '해금된 마지막' 문제를 선택하여 오리 위치 고정
  // 이렇게 하면 항상 해금된 노드에 오리가 앉게 되어 즉시 클릭(선택)이 가능해집니다.
  const unlockedIndices = displayedIndices.filter(idx => progress.includes(idx));
  
  if (unlockedIndices.length > 0) {
    return Math.max(...unlockedIndices);
  }
  
  // 만약 현재 난이도에서 아무것도 해금되지 않았다면(이론상 불가) 첫 번째 노드 반환
  return displayedIndices[0];
});

// [수정일: 2026-01-28] 라우트 감시: 연습 페이지에서 홈으로 돌아올 때 유닛 상세 모달 자동 재개
watch(() => route.name, (newNav, oldNav) => {
  const practiceRoutes = ['PseudoCode', 'SystemArchitecturePractice', 'BugHunt', 'VibeCodeCleanUp', 'OpsPractice' /*, 'AiDetective', 'PseudoForest', 'PseudoCompany', 'PseudoEmergency' */];
  // 연습 페이지에서 홈('/')으로 돌아오는 경우
  if (newNav === 'Home' && practiceRoutes.includes(oldNav)) {
    if (game.activeUnit) {
      ui.isUnitModalOpen = true;
      nextTick(() => { if (window.lucide) window.lucide.createIcons(); });
    }
  }
});

// Methods
function syncDebugProgress() {
    try {
        const data = localStorage.getItem('bugHuntGameData');
        if (data) {
            const parsed = JSON.parse(data);
            const completed = parsed.completedProblems || [];
            // progressive-problems.json을 가져와서 미션 완료 여부 확인
            const progress = [0]; // 캠페인 1은 기본 해금
            
            progressiveData.progressiveProblems.forEach((m, idx) => {
                // 미션의 마지막 단계(step 3)가 완료되었는지 확인
                const missionCompleted = completed.includes(`progressive_${m.id}_step3`);
                if (missionCompleted) {
                    progress.push(idx + 1);
                }
            });
            
            game.unitProgress['Debug Practice'] = Array.from(new Set(progress)).sort((a, b) => a - b);
        }
    } catch (e) {
        console.warn('Failed to sync debug progress:', e);
    }
}

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
    syncDebugProgress(); // 팝업 열 때 진행도 동기화
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

  const rawName = game.activeUnit?.name || '';
  const chapterName = rawName.toLowerCase().replace(/\s+/g, '');

  if (chapterName === 'pseudopractice') {
    game.selectedQuestIndex = problem.questIndex || 0;
    // [수정일: 2026-01-31] 모든 Unit 1 문제는 HUD 스타일의 통합 연습 화면(pseudoProblem.vue)으로 연결됩니다.
    router.push('/practice/pseudo-code');
  } else if (chapterName === 'systempractice') {
    game.selectedSystemProblemIndex = problem.problemIndex || 0;
    router.push({ path: '/practice/system-architecture', query: { problem: problem.problemIndex || 0 } });
  } else if (chapterName === 'debugpractice') {
    if (game.currentDebugMode === 'bug-hunt') {
      // p1, p2, p3 미션으로 바로 이동
      router.push({
        path: '/practice/bug-hunt',
        query: { missionId: problem.id, mapMode: 'true' }
      });
    } else {
      // Vibe Code Clean Up
      router.push('/practice/vibe-cleanup');
    }
  } else if (chapterName === 'opspractice') {
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

function handlePracticeClose() {
    // [2026-01-27] 실습 페이지에서 'X' 또는 닫기 이벤트 발생 시 처리
    ui.isPseudoCodeOpen = false;
    router.push('/');
    // 닫은 후 유닛 선택 팝업을 다시 보여주어 연속성 유지
    ui.isUnitModalOpen = true;
}

// [수정일: 2026-01-31] 미사용 메서드 제거 (모드 전환 기능 제거)
// function selectUnit1Mode(mode) { ... }

function selectGameMode(mode) {
  game.currentDebugMode = mode;

  // Bug Hunt 모드로 전환 시 진행도 동기화
  if (mode === 'bug-hunt') {
    syncDebugProgress();
  }

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

// [2026-01-24] 라우트 설정을 감시하여 Unit 1 모달 강제 제어 (필요 시 URL 직접 접근 대응)
// [2026-01-27] 데이터 로드 완료 시 라우트에 따른 activeUnit 자동 복구
watch(() => game.chapters, (newChapters) => {
    if (newChapters.length > 0 && route.name === 'PseudoCode' && !game.activeUnit) {
        const pseudoUnit = newChapters.find(c => c.name === 'Pseudo Practice');
        if (pseudoUnit) game.activeUnit = pseudoUnit;
    }
}, { deep: true });

// [2026-01-24] 라우트 설정을 감시하여 Unit 1 모달 강제 제어 (필요 시 URL 직접 접근 대응)
watch(() => route.name, (newName) => {
    // 1. URL이 변경될 때마다 모달 상태를 동기화합니다.
    // [수정일: 2026-01-31] 비활성 라우트 체크 간소화
    if (newName === 'PseudoCode') {
        ui.isPseudoCodeOpen = true; // 관련 라우트 접속 시 상태 활성화
        
        // [2026-01-27] 직접 URL 접근이나 새로고침 시 activeUnit이 상실되는 문제 해결
        if (game.chapters.length > 0 && !game.activeUnit) {
            const pseudoUnit = game.chapters.find(c => c.name === 'Pseudo Practice');
            if (pseudoUnit) game.activeUnit = pseudoUnit;
        }
    } else if (!isPracticePage.value) {
        // 2. 다른 일반 페이지(Landing 드)로 이동 시 모든 실습 모달을 명시적으로 닫습니다.
        ui.isPseudoCodeOpen = false;
    }
}, { immediate: true });

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
