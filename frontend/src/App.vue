<!-- 
수정일: 2026-01-20
수정내용: 'Coding Gym' 테마 적용 및 인덱스 페이지(index copy.html) 디자인 포팅
-->
<template>
  <div id="app" v-cloak>
    <!-- [라우터 뷰 - Practice 페이지 (메인 레이아웃 없이 단독 표시)] -->
    <router-view v-if="isPracticePage"></router-view>

    <!-- [메인 페이지] -->
    <template v-if="!isPracticePage">
      <LandingView 
        :isLoggedIn="isLoggedIn"
        :userProteinShakes="userProteinShakes"
        :chapters="chapters"
        :leaderboard="leaderboard"
        @go-to-playground="handleGoToPlayground"
        @open-unit="openUnitPopup"
      >
        <template #auth-buttons>
          <template v-if="!isLoggedIn">
            <button class="btn-login-ref" @click="handleLogin">Login</button>
            <button class="btn-signup-ref" @click="handleSignUp">Sign Up</button>
          </template>
          <div v-else class="user-profile-v2">
            <div class="user-info-v2">
              <span class="user-name-v2">{{ sessionNickname }}</span>
              <span class="user-rank-v2">ENGINEER</span>
            </div>
            <button class="btn-logout-v2" @click="handleLogout">Logout</button>
          </div>
        </template>
      </LandingView>

    <!-- [유닛 상세 팝업 모달] -->
    <transition name="fade">
      <div v-if="isUnitModalOpen" class="modal-overlay" @click.self="isUnitModalOpen = false">
        <div class="unit-detail-modal">
          <header class="unit-modal-header-v3">
            <div class="title-section-v3">
              <div class="unit-label-v3">
                {{ activeUnit?.name === 'Debug Practice' ? 'DEBUG GYM' : 'UNIT ' + (chapters.indexOf(activeUnit) + 1) }}
              </div>
              <h2 class="unit-name-v3">
                <template v-if="activeUnit?.name === 'Debug Practice'">
                  {{ currentDebugMode === 'bug-hunt' ? '🐞 Bug Hunt' : '✨ Vibe Code Clean Up' }}
                </template>
                <template v-else>
                  {{ activeUnit?.unitTitle || activeUnit?.problems?.[0]?.title || activeUnit?.name }}
                </template>
              </h2>
            </div>
            <div style="display: flex; align-items: center;">
              <button class="guidebook-btn-v3">
                <i data-lucide="book-open"></i>
                GUIDEBOOK
              </button>
              <button class="close-btn-v3" @click="isUnitModalOpen = false">&times;</button>
            </div>
          </header>

          <div class="unit-modal-body-v3">
            <div class="path-container-v3">
              <svg class="path-svg-v3" viewBox="0 0 800 1500">
                <path class="path-line-v3" d="M400,100 L560,250 L280,400 L520,550 L360,700 L400,850 L480,1000 L320,1150 L560,1300 L400,1450" fill="none"
                  stroke="rgba(148, 163, 184, 0.2)" stroke-width="3" stroke-dasharray="10,5" />
              </svg>

                <div v-for="(problem, pIdx) in displayProblems" :key="problem.id" class="node-platform-v3"
                :class="['node-' + pIdx, { 
                  active: pIdx === currentMaxIdx, 
                  unlocked: currentUnitProgress.includes(pIdx) 
                }]"
                @click="isUnlocked(pIdx) && (selectProblem(problem, activeUnit), isUnitModalOpen = false)">

                <div class="platform-glow-v3" v-if="pIdx === currentMaxIdx"></div>

                <div class="platform-circle-v3">
                  <template v-if="currentUnitProgress.includes(pIdx)">
                    <img v-if="pIdx === currentMaxIdx" src="/image/unit_duck.png" class="duck-on-node-v3">
                    <div
                      style="width: 20px; height: 20px; background: #b6ff40; border-radius: 50%; box-shadow: 0 0 10px #b6ff40;">
                    </div>
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
            <!-- Debug Practice일 때는 게임 모드 선택 버튼 -->
            <template v-if="activeUnit?.name === 'Debug Practice'">
              <button
                class="game-mode-btn bug-hunt"
                :class="{ 'active': currentDebugMode === 'bug-hunt' }"
                @click="selectGameMode('bug-hunt')">
                🐞 Bug Hunt
              </button>
              <button
                class="game-mode-btn vibe-cleanup"
                :class="{ 'active': currentDebugMode === 'vibe-cleanup' }"
                @click="selectGameMode('vibe-cleanup')">
                ✨ Vibe Code Clean Up
              </button>
            </template>
            <!-- 다른 Practice는 기존대로 -->
            <template v-else>
              <div class="stat-pill-v3 active">
                <i data-lucide="check-circle" style="width: 16px;"></i>
                1개 활성화
              </div>
              <div class="stat-pill-v3 locked">
                <i data-lucide="lock" style="width: 16px;"></i>
                {{ (displayProblems.length || 1) + displayLabelsCount - 1 }}개 잠금
              </div>
            </template>
          </footer>
        </div>
      </div>
    </transition>

    <!-- [에이전트 실습 워크스페이스] -->
    <transition name="fade">
      <div v-if="isAgentModalOpen" class="modal-overlay">
        <div class="workspace-container">
            <header class="workspace-header">
                <div class="header-left">
                    <span class="badge bg-medium">{{ unitBadge }}</span>
                    <h2 style="margin-top: 0.5rem;">{{ activeProblem?.title }}</h2>
                </div>
                <button class="btn-close" @click="isAgentModalOpen = false">&times;</button>
            </header>

            <div class="workspace-body">
                <!-- Left: Editor Section -->
                <div class="editor-section">
                    <div class="editor-top">
                        <span class="editor-label">{{ editorLabel }}</span>
                        <p class="card-desc">{{ activeProblem?.content }}</p>
                    </div>
                    <textarea v-model="editedPrompt" class="prompt-textarea"
                        :placeholder="editorPlaceholder"></textarea>
                </div>

                <!-- Middle: Live Chat Playground -->
                <div class="chat-playground">
                    <div class="playground-header">
                        <i data-lucide="message-square" style="width: 16px;"></i>
                        <span>{{ playgroundTitle }}</span>
                    </div>
                    <div class="chat-messages" ref="chatScroll">
                        <div v-if="chatHistory.length === 0" class="empty-chat">
                            {{ emptyChatMessage }}
                        </div>
                        <div v-for="(chat, cIdx) in chatHistory" :key="cIdx"
                            :class="['chat-bubble', chat.role]">
                            <div class="bubble-content">{{ chat.content }}</div>
                        </div>
                        <div v-if="isTyping" class="chat-bubble assistant typing">
                            <div class="dot-flashing"></div>
                        </div>
                    </div>
                    <div class="chat-input-wrapper">
                        <input type="text" v-model="userInput" @keyup.enter="sendLiveMessage"
                            placeholder="에이전트에게 테스트 메시지 전송..." :disabled="isTyping">
                        <button class="btn-send" @click="sendLiveMessage" :disabled="isTyping">
                            <i data-lucide="send"></i>
                        </button>
                    </div>
                </div>

                <!-- Right: Sidebar Section -->
                <div class="sidebar-section">
                    <div class="metric-card">
                        <h4>Current Metrics</h4>
                        <div class="chart-container-radar">
                            <canvas id="performanceChart"></canvas>
                        </div>
                        <div class="metric-grid">
                            <div class="metric-item">
                                <span class="metric-value">{{ submissionResult ? submissionResult.accuracy + '%' : '--' }}</span>
                                <span class="metric-label">Accuracy</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-value">{{ submissionResult ? submissionResult.hallucination_rate + '%' : '--' }}</span>
                                <span class="metric-label">Hallucination</span>
                            </div>
                        </div>
                    </div>
                    <div class="info-card">
                        <h4>Evaluation Criteria</h4>
                        <ul style="font-size: 0.85rem; color: var(--text-muted); padding-left: 1rem;">
                            <li>문서에 근거한 정확성</li>
                            <li>불쾌하거나 사적인 질문 차단</li>
                            <li>응답 지연 시간 (Latency)</li>
                        </ul>
                    </div>
                </div>
            </div>

            <footer class="workspace-footer">
                <button class="btn btn-secondary" @click="isAgentModalOpen = false">나중에 하기</button>
                <button class="btn btn-primary" @click="submitAgent" :disabled="isSubmitting">
                    {{ isSubmitting ? 'Evaluating...' : 'Test & Submit' }}
                </button>
            </footer>
        </div>
      </div>
    </transition>

    <!-- [평가 결과 리포트] -->
    <transition name="fade">
      <div v-if="isReportModalOpen" class="modal-overlay">
        <div class="workspace-container report-container">
            <header class="workspace-header">
                <div class="header-left">
                    <span class="badge bg-easy">EVALUATION COMPLETE</span>
                    <h2 style="margin-top: 0.5rem;">🎯 에이전트 성능 평가 리포트</h2>
                </div>
                <button class="btn-close" @click="isReportModalOpen = false">&times;</button>
            </header>

            <div class="workspace-body report-body">
                <div class="report-summary">
                    <div class="summary-card">
                        <span class="summary-label">최종 점수</span>
                        <span class="summary-value">{{ submissionResult?.accuracy }}점</span>
                    </div>
                    <div class="summary-card">
                        <span class="summary-label">환각 발생률</span>
                        <span class="summary-value" :class="{'text-danger': submissionResult?.hallucination_rate > 10}">
                            {{ submissionResult?.hallucination_rate }}%
                        </span>
                    </div>
                    <div class="summary-card">
                        <span class="summary-label">평단 지연 시간</span>
                        <span class="summary-value">{{ submissionResult?.latency }}s</span>
                    </div>
                </div>

                <div class="detail-section">
                    <h4>✅ 주요 검증 결과 (Test Cases)</h4>
                    <div class="test-case-list">
                        <div v-for="test in activeProblem?.agent_info?.test_cases" :key="test.id" class="test-item">
                            <div class="test-q"><strong>Q:</strong> {{ test.input_query }}</div>
                            <div class="test-a"><strong>Expected:</strong> {{ test.expected_response }}</div>
                            <div class="test-status status-pass">PASS</div>
                        </div>
                    </div>

                    <div class="feedback-section">
                        <h4>🤖 AI 코치 피드백</h4>
                        <div class="coach-bubble">
                            {{ submissionResult?.feedback_message || '평가 데이터를 분석 중입니다...' }}
                        </div>
                    </div>
                </div>
            </div>

            <footer class="workspace-footer">
                <button class="btn btn-secondary" @click="isReportModalOpen = false; isAgentModalOpen = true;">다시 수정하기</button>
                <button class="btn btn-primary" @click="isReportModalOpen = false">닫기</button>
            </footer>
        </div>
      </div>
    </transition>

    <!-- [공지사항 모달] -->
    <NoticeModal :isOpen="isNoticeOpen" @close="closeNotice" />

    <!-- [로그인 모달] -->
    <!-- [로그인 모달] -->
    <LoginModal 
        :isOpen="isLoginModalOpen" 
        @close="isLoginModalOpen = false"
        @login-success="onLoginSuccess"
        @request-signup="onRequestSignupFromLogin"
    />

    <!-- [회원가입 모달] -->
    <!-- [회원가입 모달] -->
    <SignUpModal
        :isOpen="isSignUpModalOpen"
        @close="isSignUpModalOpen = false"
        @signup-success="onSignUpSuccess"
    />

     <!-- [접근 제한 안내 모달] -->
     <transition name="fade">
        <div v-if="isAuthRequiredModalOpen" class="modal-overlay" @click.self="isAuthRequiredModalOpen = false">
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
                    <button class="btn btn-primary" @click="isAuthRequiredModalOpen = false; handleSignUp()"
                        style="width: 100%; height: 55px; font-size: 1.1rem;">
                        무료로 회원가입하고 입장하기
                    </button>
                    <button class="btn btn-secondary" @click="isAuthRequiredModalOpen = false; handleLogin()"
                        style="width: 100%; border: none;">
                        이미 계정이 있나요? 로그인
                    </button>
                    <button class="btn-text" @click="isAuthRequiredModalOpen = false"
                        style="background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 0.85rem; margin-top: 0.5rem;">
                        다음에 할게요
                    </button>
                </footer>
            </div>
        </div>

     </transition>

     <!-- [공사중 안내 모달] -->
     <ConstructionModal 
        :isOpen="isConstructionModalOpen" 
        @close="isConstructionModalOpen = false" 
     />

    </template>

    <!-- [Logic Mirror 실습 모달] - Global placement -->
    <transition name="fade">
       <LogicMirror 
           v-if="isLogicMirrorOpen" 
           :initialQuestIndex="selectedQuestIndex"
           @close="handleCloseLogicMirror"
           @quest-complete="handleQuestComplete"
       />
    </transition>
  </div>
</template>

<script>
// Import external stylesheet (or rely on global style.css if imported in main.js)
import './style.css';
import axios from 'axios'; // [수정일: 2026-01-22] axios 임포트 누락 수정 (Antigravity)
import NoticeModal from './components/NoticeModal.vue';
import LoginModal from './components/LoginModal.vue';
import SignUpModal from './components/SignUpModal.vue';
import ConstructionModal from './components/ConstructionModal.vue';
import LogicMirror from './features/practice/support/unit1/logic-mirror/LogicMirror.vue';
import LandingView from './features/home/LandingView.vue';
import { gameData } from './features/practice/support/unit1/logic-mirror/data/stages.js';

export default {
    components: {
        NoticeModal,
        LoginModal,
        SignUpModal,
        ConstructionModal,
        LogicMirror,
        LandingView
    },
    data() {
        return {
            userProteinShakes: 420,
            chapters: [],
            leaderboard: [
                { id: 1, username: 'TopEngineer', solved: 45, shakes: 2450 },
                { id: 2, username: 'DjangoMaster', solved: 42, shakes: 2100 },
                { id: 3, username: 'VueNinja', solved: 38, shakes: 1850 },
                { id: 4, username: 'AgentZero', solved: 35, shakes: 1600 },
                { id: 5, username: 'OpsWizard', solved: 30, shakes: 1400 }
            ],
            isAgentModalOpen: false,
            isReportModalOpen: false, 
            activeProblem: null,
            editedPrompt: '',
            submissionResult: null,
            chatHistory: [],
            userInput: '',
            isTyping: false,
            isNoticeOpen: true,
            isLoginModalOpen: false,
            // loginEmail: '',  // Moved to LoginModal
            // loginPassword: '', // Moved to LoginModal
            isSignUpModalOpen: false,
            // signupNickname: '', // Moved to SignUpModal
            // signupEmail: '',
            // signupPassword: '',
            // Additional signup fields omitted for brevity but can be added back
            isLoggedIn: false,
            sessionNickname: '',
            isUnitModalOpen: false,
            activeUnit: null,
            activeChapter: null,
            showScrollHint: false,
            isAuthRequiredModalOpen: false,
            isConstructionModalOpen: false, // [수정일: 2026-01-21] 공사중 모달 상태 추가
                        isLogicMirrorOpen: false, // [수정일: 2026-01-22] Pseudo Practice 모달 상태 추가
            selectedQuestIndex: 0, // [2026-01-24] 선택된 퀘스트 인덱스 추적
            currentDebugMode: 'bug-hunt', // [수정일: 2026-01-22] Debug Practice 현재 모드 (bug-hunt | vibe-cleanup)
            unitProgress: {
                'Pseudo Practice': [0],
                'Debug Practice': [0],
                'System Practice': [0],
                'Ops Practice': [0],
                'Agent Practice': [0]
            },
            // Mermaid, Code, Debug, Pseudo state vars would go here...
            mermaidCode: '',
        }
    },
    methods: {
        async fetchChapters() {
             // Mock data since backend might not be ready with CORS
             const colors = ['#58cc02', '#1cb0f6', '#ff9600', '#ce82ff', '#ff4b4b'];
             const iconMap = {
                                'Pseudo Practice': 'code',
                'Debug Practice': 'bug',
                'System Practice': 'layers',
                'Ops Practice': 'zap',
                'Agent Practice': 'bot',
                'Pseudo Practice': 'gamepad-2'
             };
             
             // Simulating fetch
             this.chapters = [
                                  { id: 1, name: 'Pseudo Practice', unitTitle: 'Algorithm 101', description: 'Strength Training', problems: [], image: '/image/unit_code.png' },
                 { id: 2, name: 'Debug Practice', description: 'Precision Training', problems: [{id: 2, title: 'Fix the Bug'}], image: '/image/unit_debug.png' },
                 { id: 3, name: 'System Practice', description: 'Strategy Training', problems: [{id: 3, title: 'Design System'}], image: '/image/unit_system.png' },
                 { id: 4, name: 'Ops Practice', description: 'Endurance Training', problems: [{id: 4, title: 'Server Down!'}], image: '/image/unit_ops.png' },
                 { id: 5, name: 'Agent Practice', description: 'AI Training', problems: [{id: 5, title: 'Prompt Eng'}], image: '/image/unit_agent.png' },
             ].map((ch, idx) => ({
                    ...ch,
                    color: colors[idx % colors.length],
                    icon: iconMap[ch.name] || 'book'
             }));

             // [2026-01-24] Code Practice 챕터에 stages.js의 10개 퀘스트를 개별 문제로 매핑
                          const pseudoPracticeIdx = this.chapters.findIndex(c => c.name === 'Pseudo Practice');
                          if (pseudoPracticeIdx !== -1 && gameData.quests) {
                 this.chapters[pseudoPracticeIdx].problems = gameData.quests.map((q, idx) => ({
                     id: q.id,
                     title: q.title,
                     questIndex: idx,
                     displayNum: `1-${idx + 1}`
                 }));
             }

             this.$nextTick(() => {
                 if (window.lucide) window.lucide.createIcons();
             });
        },
        closeNotice() {
            this.isNoticeOpen = false;
        },
        labelsCount(unit) {
            const currentCount = unit?.problems?.length || 0;
            return Math.max(0, 6 - currentCount);
        },
        openUnitPopup(unit) {
            if (!this.isLoggedIn) {
                this.isAuthRequiredModalOpen = true;
                return;
            }
            this.activeUnit = unit;
            // Debug Practice일 경우 기본 모드를 Bug Hunt로 설정
            if (unit?.name === 'Debug Practice') {
                this.currentDebugMode = 'bug-hunt';
            }
            this.isUnitModalOpen = true;
        },
        selectProblem(problem, chapter) {
            if (!this.isLoggedIn) {
                this.isAuthRequiredModalOpen = true;
                return;
            }
            this.activeProblem = problem;
            this.activeChapter = chapter;

            // [수정일: 2026-01-23] Practice 페이지들은 라우터로 이동
            console.log('selectProblem:', chapter?.name);
                        if (chapter?.name === 'Pseudo Practice') {
                this.selectedQuestIndex = problem.questIndex || 0;
                this.isLogicMirrorOpen = true;
            } else if (chapter?.name === 'System Practice') {
                this.$router.push('/practice/system-architecture');
            } else if (chapter?.name === 'Debug Practice') {
                // currentDebugMode에 따라 다른 라우트로 이동
                if (this.currentDebugMode === 'bug-hunt') {
                    this.$router.push('/practice/bug-hunt');
                } else if (this.currentDebugMode === 'vibe-cleanup') {
                    this.$router.push('/practice/vibe-cleanup');
                }
            } else if (chapter?.name === 'Ops Practice') {
                this.$router.push('/practice/ops-practice');
            } else if (chapter?.name === 'Agent Practice') {
                this.isAgentModalOpen = true;
                this.$nextTick(() => {
                    if (window.lucide) window.lucide.createIcons();
                    // Chart init would go here
                });
            } else {
                 this.isConstructionModalOpen = true;
            }
        },
        selectGameMode(mode) {
            this.currentDebugMode = mode;
            if (this.activeUnit?.name === 'Debug Practice') {
                const isDebugRoute = ['BugHunt', 'VibeCodeCleanUp'].includes(this.$route.name);
                if (isDebugRoute) {
                    const nextPath = mode === 'bug-hunt' ? '/practice/bug-hunt' : '/practice/vibe-cleanup';
                    this.$router.push(nextPath);
                }
            }
            this.$nextTick(() => {
                if (window.lucide) window.lucide.createIcons();
            });
        },
        handleLogin() { this.isLoginModalOpen = true; },
        onLoginSuccess(email) {
            this.isLoggedIn = true;
            this.isLoginModalOpen = false;
            this.sessionNickname = email.split('@')[0] || 'Engineer';
        },
        onRequestSignupFromLogin() {
            this.isLoginModalOpen = false;
            this.handleSignUp();
        },
        handleSignUp() { this.isSignUpModalOpen = true; },
        onSignUpSuccess(nickname) {
            this.isSignUpModalOpen = false;
            // Success modal logic omitted
            this.isLoggedIn = true;
            this.sessionNickname = nickname || 'NewUser';
        },
        // [수정일: 2026-01-21] 로그인 성공 핸들러
        onLoginSuccess(user) {
            this.isLoggedIn = true;
            this.sessionNickname = user.nickname || user.username;
            this.isLoginModalOpen = false;
        },

        // [수정일: 2026-01-21] 로그아웃 API 연동
        async handleLogout() {
            try {
                await axios.post('/api/core/auth/logout/');
                this.isLoggedIn = false;
                this.sessionNickname = '';
                alert('Logged out successfully.');
            } catch (error) {
                console.error('Logout failed:', error);
                // 그래도 클라이언트 로그아웃은 처리
                this.isLoggedIn = false;
                this.sessionNickname = '';
            }
        },

        // [수정일: 2026-01-21] 세션 체크 (새로고침 시 로그인 유지)
        async checkSession() {
            try {
                const response = await axios.get('/api/core/auth/me/');
                if (response.data.isAuthenticated) {
                    this.isLoggedIn = true;
                    this.sessionNickname = response.data.user.nickname || response.data.user.username;
                }
            } catch (error) {
                this.isLoggedIn = false;
            }
        },

        handleCloseLogicMirror() {
            /* [2026-01-24] 실습 종료 후 다시 월드 맵(Unit Modal)을 보여주도록 개선 */
            this.isLogicMirrorOpen = false;
            this.isUnitModalOpen = true;
        },
        handleQuestComplete(index) {
            /* [2026-01-24] 문제 완료 시 다음 스테이지 활성화 로직 (Pseudo Practice 전용) */
            const progress = this.unitProgress['Pseudo Practice'];
            if (!progress.includes(index)) {
                progress.push(index);
            }
            // 다음 인덱스도 잠금 해제
            const nextIdx = index + 1;
            if (nextIdx < 10 && !progress.includes(nextIdx)) {
                progress.push(nextIdx);
            }
        },
        isUnlocked(pIdx) {
            return this.currentUnitProgress.includes(pIdx);
        },

        handleGoToPlayground() {
            if (this.isLoggedIn) {
                document.getElementById('chapters')?.scrollIntoView({ behavior: 'smooth' });
            } else {
                this.isAuthRequiredModalOpen = true;
            }
        },
        async sendLiveMessage() {
            if (!this.userInput.trim()) return;
            this.chatHistory.push({ role: 'user', content: this.userInput });
            this.userInput = '';
            this.isTyping = true;
            setTimeout(() => {
                this.chatHistory.push({ role: 'assistant', content: 'This is a simulated AI response.' });
                this.isTyping = false;
            }, 1000);
        },
        submitAgent() {
            this.isSubmitting = true;
            setTimeout(() => {
                this.submissionResult = { accuracy: 88, hallucination_rate: 12, latency: 0.8 };
                this.isSubmitting = false;
                this.isAgentModalOpen = false;
                this.isReportModalOpen = true;
            }, 1500);
        }
    },
    computed: {
        isPracticePage() {
            const practiceRoutes = ['LogicMirror', 'LogicMirrorTest', 'SystemArchitecturePractice', 'BugHunt', 'VibeCodeCleanUp', 'OpsPractice'];
            return practiceRoutes.includes(this.$route?.name);
        },
        currentUnitProgress() {
            if (!this.activeUnit) return [0];
            return this.unitProgress[this.activeUnit.name] || [0];
        },
        currentMaxIdx() {
            return Math.max(...this.currentUnitProgress);
        },
        displayProblems() {
            if (this.activeUnit?.name === 'Debug Practice') {
                const title = this.currentDebugMode === 'bug-hunt' ? 'Bug Hunt' : 'Vibe Code Clean Up';
                return [{ id: this.currentDebugMode, title }];
            }
            return this.activeUnit?.problems || [];
        },
        displayLabelsCount() {
            const currentCount = this.displayProblems?.length || 0;
            return Math.max(0, 6 - currentCount);
        },
        unitBadge() { return this.activeChapter?.name || 'Practice'; },
        editorLabel() { return 'SYSTEM PROMPT EDITOR'; },
        editorPlaceholder() { return 'Enter your system prompt here...'; },
        playgroundTitle() { return 'LIVE CHAT PLAYGROUND'; },
        emptyChatMessage() { return 'Start testing your prompt!'; }
    },
    mounted() {
        this.checkSession(); // 앱 로드 시 세션 확인
        this.fetchChapters();
        this.$nextTick(() => {
            if (window.lucide) window.lucide.createIcons();
        });
    },
    // 2026-01-20: 모달/팝업(v-if) 렌더링 시 Lucide 아이콘이 표시되지 않는 문제 해결 (DOM 업데이트 후 아이콘 리로드)
    updated() {
        this.$nextTick(() => {
            if (window.lucide) window.lucide.createIcons();
        });
    }
}
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
