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
    <!-- [상단 네비게이션 바] -->
    <nav class="navbar">
      <div class="logo">
        <span class="logo-text">ARCH-GYM 🚀</span>
      </div>
      <div class="nav-links">
        <a href="#chapters">Chapters</a>
        <a href="#leaderboard">Leaderboard</a>
        <div class="user-stats">
          <i data-lucide="milk" class="icon-token"></i>
          <span>{{ userProteinShakes }}</span>
        </div>
        <template v-if="!isLoggedIn">
          <button class="btn btn-login" @click="handleLogin">Login</button>
          <button class="btn btn-signup" @click="handleSignUp">Sign Up</button>
        </template>
        <div v-else class="user-profile">
          <div class="user-info">
            <span class="user-status-dot"></span>
            <span class="user-name">{{ sessionNickname }}</span>
            <span class="user-rank">ENGINEER</span>
          </div>
          <button class="btn btn-secondary btn-sm" @click="handleLogout"
            style="padding: 0.4rem 0.8rem; font-size: 0.75rem; min-width: auto;">
            Logout
          </button>
        </div>
      </div>
    </nav>

    <!-- [히어로 섹션] -->
    <header class="hero">
      <!-- Video Path needs to be correct. Assuming handled by backend static serving or copied to public -->
<video
  id="hero-video"
  src="/image/sports_gym.mp4"
  autoplay
  muted
  loop
  playsinline
></video>
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <h1 class="main-title bounce-in">Engineer Playground!</h1>
        <p class="subtitle">아키텍처 근성장(?) 보장! 엔지니어들을 위한 아키텍처 놀이터 <i data-lucide="party-popper"></i></p>
        <div class="hero-btns">
          <button @click="handleGoToPlayground" class="btn btn-primary">놀러 가기!</button>
          <a href="#leaderboard" class="btn btn-secondary">랭킹 파티 확인</a>
        </div>
      </div>
    </header>

    <!-- [챕터/스테이지 섹션] -->
    <section id="chapters" class="section" :class="{ 'locked-content': !isLoggedIn }"
      @click="!isLoggedIn && (isAuthRequiredModalOpen = true)">
      <div class="hub-wrapper">
        <div class="learning-path-sidebar left">
          <div class="mascot-container">
            <div class="mascot-bubble">훈련 준비됐어? 가보자고!</div>
            <img src="/image/mascot.png" alt="Mascot" class="path-mascot">
          </div>
        </div>

        <div class="hub-main-content">
          <h2 class="section-title" style="text-align: left; margin-bottom: 2.5rem; margin-top: 0;">재밌는 아키텍처 스테이지</h2>

          <div class="unit-parallel-grid">
            <div v-for="(chapter, idx) in chapters.slice(0, 6)" :key="chapter.id" class="unit-card-parallel"
              @click="openUnitPopup(chapter)">
              <div class="unit-card-icon" :style="{ background: chapter.color || 'var(--primary)' }">
                <i :data-lucide="chapter.icon || 'shield'"></i>
              </div>
              <div class="unit-card-info">
                <span class="unit-card-number">UNIT {{ idx + 1 }}</span>
                <h4 class="unit-card-name">{{ chapter.name }}</h4>
              </div>
              <div class="unit-card-arrow">
                <i data-lucide="chevron-right"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- [리더보드 섹션] -->
    <section id="leaderboard" class="section" :class="{ 'locked-content': !isLoggedIn }"
      @click="!isLoggedIn && (isAuthRequiredModalOpen = true)">
      <div class="hub-wrapper">
        <div class="learning-path-sidebar left">
          <!-- Space filler -->
        </div>
        <div class="hub-main-content">
          <h2 class="section-title" style="text-align: left; margin-bottom: 2.5rem; margin-top: 0;">오늘의 득근 전당</h2>
          <div class="leaderboard-container">
            <table class="leaderboard-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Engineer</th>
                  <th>Problems Solved</th>
                  <th>Protein Shakes</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(user, index) in leaderboard" :key="user.id">
                  <td>#{{ index + 1 }}</td>
                  <td style="font-weight: 700;">{{ user.username }}</td>
                  <td>{{ user.solved }}</td>
                  <td class="td-token">
                    <i data-lucide="milk" class="small-icon"></i>
                    {{ user.shakes }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer>
      <p>&copy; 2026 Architecture Gym. Built with ⚡ by Antigravity AI.</p>
    </footer>

    <!-- [유닛 상세 팝업 모달] -->
    <transition name="fade">
      <div v-if="isUnitModalOpen" class="modal-overlay" @click.self="isUnitModalOpen = false">
        <div class="unit-detail-modal">
          <header class="unit-modal-header-v3">
            <div class="title-section-v3">
              <div class="unit-label-v3">UNIT {{ chapters.indexOf(activeUnit) + 1 }}</div>
              <h2 class="unit-name-v3">{{ activeUnit?.problems?.[0]?.title || activeUnit?.name }}</h2>
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
              <svg class="path-svg-v3" viewBox="0 0 800 1000">
                <path class="path-line-v3" d="M400,100 L560,250 L280,400 L520,550 L360,700 L400,850" fill="none"
                  stroke="rgba(148, 163, 184, 0.2)" stroke-width="3" stroke-dasharray="10,5" />
              </svg>

              <div v-for="(problem, pIdx) in activeUnit?.problems" :key="problem.id" class="node-platform-v3"
                :class="['node-' + pIdx, { active: pIdx === 0 }]"
                @click="selectProblem(problem, activeUnit); isUnitModalOpen = false">

                <div class="platform-glow-v3" v-if="pIdx === 0"></div>

                <div class="platform-circle-v3">
                  <template v-if="pIdx === 0">
                    <img src="/image/unit_duck.png" class="duck-on-node-v3">
                    <div
                      style="width: 20px; height: 20px; background: #b6ff40; border-radius: 50%; box-shadow: 0 0 10px #b6ff40;">
                    </div>
                  </template>
                  <template v-else>
                    <i data-lucide="lock" class="lock-icon-v3"></i>
                  </template>
                </div>

                <div class="node-label-premium">
                  {{ problem.title }}
                </div>
              </div>

              <!-- Decorative Locked Nodes -->
              <div v-for="i in labelsCount(activeUnit)" :key="'extra-' + i" class="node-platform-v3 locked"
                :class="'node-' + (activeUnit?.problems?.length + i - 1)">
                <div class="platform-circle-v3">
                  <i data-lucide="lock" class="lock-icon-v3"></i>
                </div>
              </div>
            </div>
          </div>

          <footer class="unit-stats-bar-v3">
            <div class="stat-pill-v3 active">
              <i data-lucide="check-circle" style="width: 16px;"></i>
              1개 활성화
            </div>
            <div class="stat-pill-v3 locked">
              <i data-lucide="lock" style="width: 16px;"></i>
              {{ (activeUnit?.problems?.length || 1) + labelsCount(activeUnit) - 1 }}개 잠금
            </div>
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

     <!-- Scroll Attempt Warning Toast -->
    <div v-if="!isLoggedIn" class="scroll-warning-toast" :class="{ show: showScrollHint }">
        <i data-lucide="lock" style="width: 18px; color: #1e293b;"></i>
        <span>잠깐! 🚧 로그인이 필요해요</span>
        <button @click="handleLogin" style="background: #1e293b; color: white; border: none; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; cursor: pointer; margin-left: 5px; font-weight: 700;">로그인하기</button>
    </div>
    </template>
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

export default {
    components: {
        NoticeModal,
        LoginModal,
        SignUpModal,
        ConstructionModal
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
            isUnitModalOpen: false,
            activeUnit: null,
            activeChapter: null,
            showScrollHint: false,
            isAuthRequiredModalOpen: false,
            isConstructionModalOpen: false, // [수정일: 2026-01-21] 공사중 모달 상태 추가
            // Mermaid, Code, Debug, Pseudo state vars would go here...
            mermaidCode: '',
        }
    },
    methods: {
        async fetchChapters() {
             // Mock data since backend might not be ready with CORS
             const colors = ['#58cc02', '#1cb0f6', '#ff9600', '#ce82ff', '#ff4b4b'];
             const iconMap = {
                'Code Practice': 'code',
                'Debug Practice': 'bug',
                'System Practice': 'layers',
                'Ops Practice': 'zap',
                'Agent Practice': 'bot',
                'Pseudo Practice': 'gamepad-2'
             };
             
             // Simulating fetch
             this.chapters = [
                 { id: 1, name: 'Code Practice', description: 'Strength Training', problems: [{id: 1, title: 'Algorithm 101'}] },
                 { id: 2, name: 'Debug Practice', description: 'Precision Training', problems: [{id: 2, title: 'Fix the Bug'}] },
                 { id: 3, name: 'System Practice', description: 'Strategy Training', problems: [{id: 3, title: 'Design System'}] },
                 { id: 4, name: 'Ops Practice', description: 'Endurance Training', problems: [{id: 4, title: 'Server Down!'}] },
                 { id: 5, name: 'Agent Practice', description: 'AI Training', problems: [{id: 5, title: 'Prompt Eng'}] },
             ].map((ch, idx) => ({
                    ...ch,
                    color: colors[idx % colors.length],
                    icon: iconMap[ch.name] || 'book'
             }));

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
            this.isUnitModalOpen = true;
        },
        selectProblem(problem, chapter) {
            if (!this.isLoggedIn) {
                this.isAuthRequiredModalOpen = true;
                return;
            }
            this.activeProblem = problem;
            this.activeChapter = chapter;

            // [수정일: 2026-01-21] Practice 페이지들은 메인 레이아웃 없이 단독 표시
            if (chapter?.name === 'Code Practice') {
                this.$router.push('/practice/logic-mirror');
            } else if (chapter?.name === 'System Practice') {
                this.$router.push('/practice/system-architecture');
            } else if (chapter?.name === 'Debug Practice') {
                this.$router.push('/practice/debug-practice');
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
            const practiceRoutes = ['CodePracticeLogicMirror', 'SystemArchitecturePractice', 'DebugPractice', 'OpsPractice'];
            return practiceRoutes.includes(this.$route.name);
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
/* Scoped styles if needed, but we rely on global style.css */
</style>
