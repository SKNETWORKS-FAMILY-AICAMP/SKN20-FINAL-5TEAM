<!-- 
수정일: 2026-01-23
수정내용: AI 엔지니어들을 위한 'Architecture Playground' 테마의 랜딩 페이지 구현.
          game_duck.mp4 배경, 운동하는 오리 GIF 및 플로팅 애니메이션 적용.
-->
<template>
  <div class="landing-container" ref="landingContainer" @scroll="handleScroll">
    <!-- [Hero Section] -->
    <header class="hero-playground-premium">
      <video id="hero-video" src="/image/game_duck.mp4" autoplay muted loop playsinline></video>
      <div class="hero-overlay-refined"></div>
      <div class="hero-scanline"></div>
      
      <div class="hero-content-premium">
        <div class="playground-badge-v2">
          <span class="badge-dot"></span>
          OPEN BETA v1.2
        </div>
        <h1 class="playground-title-v2">
          <span class="text-glow-premium">AI-Engineer</span><br>
          <span class="text-neon-ultimate">Playground!</span>
        </h1>
        <p class="playground-subtitle-v2">
          단순한 실습을 넘어선 압도적 AI 엔지니어링 경험.<br>
          이제 오리들과 함께 당신의 한계를 돌파하세요.
        </p>
        
        <div class="hero-action-group-v2">
          <button @click="$emit('go-to-playground')" class="btn-play-premium">
            <span>입장하기!</span>
            <ArrowRight class="btn-arrow" />
          </button>
          <button @click="scrollToLeaderboard" class="btn-social-v2">
            전당 확인
          </button>
        </div>
      </div>

      <!-- [Decorative Elements] -->
      <div class="hero-decor decor-1"></div>
      <div class="hero-decor decor-2"></div>
    </header>

    <!-- [Navigation Bar - Glassmorphism] -->
    <nav class="navbar-v2" :class="{ 'is-hidden': isScrolled }">
      <div class="logo-playground">
        <Gamepad2 class="logo-icon" />
        <span class="logo-text">AI-Arcade</span>
      </div>
      <div class="nav-links-v2">
        <a href="#chapters" class="nav-item" @click.prevent="scrollToSection('chapters')">
          <LayoutGrid class="nav-icon" />
          <span class="nav-label">Stages</span>
        </a>
        <a href="#leaderboard" class="nav-item" @click.prevent="scrollToSection('leaderboard')">
          <Trophy class="nav-icon" />
          <span class="nav-label">Hall of Fame</span>
        </a>
        <div class="protein-status">
          <Zap class="icon-protein" />
          <span class="protein-count">{{ userProteinShakes }}</span>
        </div>
        <slot name="auth-buttons"></slot>
      </div>
    </nav>

    <nav class="navbar-v2 bookmark-mode" :class="{ 'is-visible': isScrolled }">
      <div class="logo-playground">
        <Gamepad2 class="logo-icon" />
      </div>
      <div class="nav-links-v2">
        <a href="#chapters" class="nav-item" @click.prevent="scrollToSection('chapters')">
          <LayoutGrid class="nav-icon" />
          <span class="nav-label">Stages</span>
        </a>
        <a href="#leaderboard" class="nav-item" @click.prevent="scrollToSection('leaderboard')">
          <Trophy class="nav-icon" />
          <span class="nav-label">Hall of Fame</span>
        </a>
        <div class="protein-status">
          <Zap class="icon-protein" />
          <span class="protein-count">{{ userProteinShakes }}</span>
        </div>
        <slot name="auth-buttons"></slot>
      </div>
    </nav>

    <!-- [Chapters Section] -->
    <section id="chapters" class="playground-section-premium">
      <div class="background-grid-pattern"></div>
      <div class="section-header">
        <h2 class="title-with-mascot">
          Engineer's Arcade <Gamepad2 />
        </h2>
        <p>원하는 게임을 선택하고 당신의 실력을 증명하세요!</p>
      </div>

      <div class="playground-slider-container">
        <button class="slider-nav prev" @click="prevSlide">
          <ChevronLeft />
        </button>

        <div
          class="slider-wrapper"
          :class="{ dragging: isDragging }"
          @pointerdown="onDragStart"
          @pointermove="onDragMove"
          @pointerup="onDragEnd"
          @pointerleave="onDragEnd"
        >
          <div class="slider-track" :style="trackStyle">
            <div v-for="(chapter, idx) in chapters" :key="chapter.id" 
                 class="gym-card-premium" 
                 :style="{ '--unit-color': chapter.color }"
                 :class="[
                   'card-color-' + (idx % 5),
                   { 'active': idx === currentIdx, 
                     'prev': idx === getPrevIdx, 
                     'next': idx === getNextIdx,
                     'hidden': !isIndexVisible(idx)
                   }
                 ]">
              <div class="card-inner-v2">
                <div class="card-image-wrap-v2">
                  <div class="energy-rings">
                    <span class="ring-1"></span>
                    <span class="ring-2"></span>
                    <span class="ring-3"></span>
                  </div>
                  <img :src="chapter.image" :alt="chapter.name" class="premium-icon">
                  <div class="card-aura-premium"></div>
                </div>
                <div class="card-text-v2">
                  <!-- [2026-01-25] 유닛 정보 영역: DB(PracticeUnit) 필드 연동 -->
                  <div class="unit-badge-row">
                    <!-- 1. 유닛 번호 표시 (최소 2자리 숫자로 포맷팅, 예: UNIT 01) -->
                    <span class="unit-tag-v2">
                      <component :is="chapter.icon" style="width: 14px; height: 14px; margin-right: 4px;" />
                      UNIT {{ String(chapter.unit_number).padStart(2, '0') }}
                    </span>
                    <!-- 2. 권장 레벨 표시 (예: LV.10) -->
                    <span class="level-indicator">LV.{{ chapter.level }}</span>
                  </div>
                  <!-- 3. 유닛 제목 및 부제목(설명) 표시 -->
                  <h3>{{ chapter.name }}</h3>
                  <p>{{ chapter.description }}</p>
                  
                  <div class="card-footer-v2">
                    <!-- 4. 참여 인원 데이터 표시 (예: 85+ Training) -->
                    <span class="engineer-count">
                      <Users style="width: 14px; height: 14px; display: inline-block; vertical-align: middle; margin-right: 4px;" /> 
                      {{ chapter.participant_count }}+ Played
                    </span>
                    <button class="btn-enter-mini" @click="handleCardClick(chapter, idx)">START</button>
                  </div>
                </div>
              </div>
              <div class="card-border-glow"></div>
            </div>
          </div>
        </div>
        <button class="slider-nav next" @click="nextSlide">
          <ChevronRight />
        </button>

        <!-- Pagination Dots -->
        <div class="slider-pagination">
          <span v-for="(_, idx) in chapters" :key="'dot-'+idx"
                class="dot" :class="{ 'active': idx === currentIdx }"
                @click="goToSlide(idx)"></span>
        </div>
      </div>
    </section>

    <!-- [Leaderboard Section Premium] -->
    <section id="leaderboard" class="lb-section-premium">
      <div class="background-grid-pattern"></div>
      <div class="lb-energy-pulse"></div>
      <div class="lb-header-v2">
        <span class="lb-subtitle">ENGINEER RANKING</span>
        <h2>오늘의 명예 전당 🏆</h2>
        <p>아키텍처 마스터들이 아케이드를 빛내고 있습니다. (Page {{ leaderboardCurrentPage }} / {{ leaderboardTotalPages }})</p>
      </div>
      
      <div class="lb-glass-table-v2">
          <div class="lb-table-head">
            <span class="col-rank">Rank</span>
            <span class="col-user">Engineer</span>
            <span class="col-solved">Stages Mastered</span>
            <span class="col-shakes">Arcade Points</span>
          </div>
          <div v-for="(user, index) in leaderboard" :key="user.id" 
               class="lb-row-v2" :class="'row-rank-' + user.rank">
            <div class="col-rank">
              <div class="rank-box">
                <span class="rank-num">#{{ user.rank }}</span>
                <Crown v-if="user.rank === 1" class="crown-icon" />
              </div>
            </div>
            <div class="col-user">
              <AvatarFrame 
                :src="user.avatar_url" 
                :rank="user.current_grade || 'BRONZE'" 
                size="50px" 
                hoverZoom 
                class="user-avatar-mini"
              />
              <span class="username-premium">{{ user.nickname }}</span>
            </div>
            <div class="col-solved">
              <span class="solved-count-v2">{{ user.solved }}</span>
              <span class="label-v2">UNITS</span>
            </div>
            <div class="col-shakes">
              <div class="shake-badge-v2">
                <Zap class="milk-icon-v2" />
                <span>{{ user.points.toLocaleString() }}</span>
              </div>
            </div>
          </div>

          <!-- [수정일: 2026-02-09] 페이징 컨트롤 UI 추가 -->
          <div class="lb-pagination" v-if="leaderboardTotalPages > 1">
            <button 
              class="btn-pg prev" 
              :disabled="leaderboardCurrentPage === 1"
              @click="$emit('change-page', leaderboardCurrentPage - 1)"
            >
              <ChevronLeft style="width: 20px;" />
            </button>
            
            <div class="pg-numbers">
              <span 
                v-for="p in leaderboardTotalPages" 
                :key="'pg-'+p"
                class="pg-num"
                :class="{ active: p === leaderboardCurrentPage }"
                @click="$emit('change-page', p)"
              >
                {{ p }}
              </span>
            </div>

            <button 
              class="btn-pg next" 
              :disabled="leaderboardCurrentPage === leaderboardTotalPages"
              @click="$emit('change-page', leaderboardCurrentPage + 1)"
            >
              <ChevronRight style="width: 20px;" />
            </button>
          </div>
      </div>
    </section>

    <footer class="playground-footer">
      <p>&copy; 2026 AI-ARCADE. Crafted with ❤️ by Final 5 Team</p>
    </footer>

    <!-- [2026-01-24] 최상단 복귀용 프리미엄 Home 버튼 추가 -->
    <transition name="home-pop">
      <button v-if="isScrolled" @click="scrollToTop" class="btn-floating-home" aria-label="Scroll to top">
        <Home class="home-icon" />
        <div class="home-glow"></div>
      </button>
    </transition>
  </div>
</template>

<script>
import { 
  Gamepad2, 
  LayoutGrid, 
  Trophy, 
  Zap, 
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  Users,
  Crown,
  Home,
  Play,
  Settings,
  History,
  LogOut
} from 'lucide-vue-next';
import AvatarFrame from '@/components/AvatarFrame.vue';

export default {
  name: 'LandingView',
  components: {
    AvatarFrame,
    Users, 
    Crown, 
    Zap, 
    ChevronLeft, 
    ChevronRight,
    Play,
    Settings,
    History,
    LogOut,
    Home,
    Gamepad2,
    LayoutGrid,
    Trophy,
    ArrowRight
  },
  props: {
    isLoggedIn: Boolean,
    userProteinShakes: Number,
    chapters: Array,
    leaderboard: Array,
    leaderboardCurrentPage: Number,
    leaderboardTotalPages: Number
  },
  data() {
    return {
      currentIdx: 0,
      isScrolled: false,
      scrollTicking: false,
      hoverTimer: null,
      isDragging: false,
      dragMoved: false,
      dragStartX: 0,
      dragThreshold: 120
    };
  },
  computed: {
    // 1. 이전 카드 인덱스 계산 (방어 로직 포함)
    getPrevIdx() {
      if (!this.chapters || this.chapters.length === 0) return 0;
      return (this.currentIdx - 1 + this.chapters.length) % this.chapters.length;
    },
    // 2. 다음 카드 인덱스 계산 (방어 로직 포함)
    getNextIdx() {
      if (!this.chapters || this.chapters.length === 0) return 0;
      return (this.currentIdx + 1) % this.chapters.length;
    },
    trackStyle() {
      // 슬라이더 트랙 커스텀 스타일 (필요 시 확장)
      return {};
    }
  },
  methods: {
    /**
     * [아이콘 새로고침]
     * - Lucide 라이브러리를 사용하여 DOM 내의 data-lucide 아이콘들을 렌더링합니다.
     */
    refreshIcons() {
      this.$nextTick(() => {
        if (window.lucide) {
          window.lucide.createIcons();
        }
      });
    },
    /**
     * [스크롤 이벤트 핸들러]
     * - 일정 높이 이상 스크롤 시 상단 바의 디자인을 변경(isScrolled)합니다.
     */
    handleScroll() {
      if (this.scrollTicking) return;
      this.scrollTicking = true;
      requestAnimationFrame(() => {
        const container = this.$refs.landingContainer;
        if (container) {
          this.isScrolled = container.scrollTop > 100;
        }
        this.scrollTicking = false;
      });
    },
    scrollToSection(sectionId) {
      const container = this.$refs.landingContainer;
      const section = document.getElementById(sectionId);
      if (!container || !section) return;
      container.scrollTo({ top: section.offsetTop, behavior: 'smooth' });
    },
    scrollToLeaderboard() {
      this.scrollToSection('leaderboard');
    },
    /**
     * [최상단 복귀]
     * - 버튼 클릭 시 히어로 영역으로 부드럽게 스크롤합니다.
     */
    scrollToTop() {
      const container = this.$refs.landingContainer;
      if (container) {
        container.scrollTo({ top: 0, behavior: 'smooth' });
      }
    },
    nextSlide() {
      if (this.chapters.length > 0) {
        this.currentIdx = (this.currentIdx + 1) % this.chapters.length;
      }
    },
    prevSlide() {
      if (this.chapters.length > 0) {
        this.currentIdx = (this.currentIdx - 1 + this.chapters.length) % this.chapters.length;
      }
    },
    goToSlide(idx) {
      this.currentIdx = idx;
    },
    /**
     * [카드가 화면에 보이는지 여부]
     * - 현재 인덱스와 인접한 카드만 보여주어 3D 넘김 효과를 구현합니다.
     */
    isIndexVisible(idx) {
      if (!this.chapters || this.chapters.length === 0) return false;
      const diff = Math.abs(idx - this.currentIdx);
      return diff <= 1 || diff === this.chapters.length - 1;
    },
    /**
     * [카드 호버 핸들러]
     * - 마우스가 근처 카드에 상주할 때만 전환되도록 지연(250ms)을 둡니다.
     * - 빠른 마우스 이동으로 인한 오작동을 방지합니다.
     */
    handleCardHover(idx) {
      if (this.currentIdx === idx) return;
      
      clearTimeout(this.hoverTimer);
      this.hoverTimer = setTimeout(() => {
        this.currentIdx = idx;
      }, 250); // 0.25초 이상 머물렀을 때만 전환
    },
    /**
     * [호버 타이머 초기화]
     * - 마우스가 카드를 벗어나면 전환 예약을 취소합니다.
     */
    clearHoverTimer() {
      clearTimeout(this.hoverTimer);
    },
    onDragStart(event) {
      if (event.button !== 0) return;
      if (event.target.closest('button') || event.target.closest('a')) return;
      this.isDragging = true;
      this.dragMoved = false;
      this.dragStartX = event.clientX;
      event.currentTarget.setPointerCapture?.(event.pointerId);
    },
    onDragMove(event) {
      if (!this.isDragging) return;
      const deltaX = event.clientX - this.dragStartX;
      if (Math.abs(deltaX) < this.dragThreshold) return;
      this.dragMoved = true;
      const direction = deltaX > 0 ? -1 : 1;
      if (this.chapters.length > 0) {
        this.currentIdx = (this.currentIdx + direction + this.chapters.length) % this.chapters.length;
      }
      this.dragStartX = event.clientX;
    },
    onDragEnd(event) {
      if (!this.isDragging) return;
      this.isDragging = false;
      event.currentTarget.releasePointerCapture?.(event.pointerId);
    },
    /**
     * [카드 클릭 핸들러]
     * - 이미 선택된 카드 클릭 시 상세 팝업을 열고, 아니면 해당 카드를 중앙으로 이동시킵니다.
     */
    handleCardClick(chapter, idx) {
      if (this.dragMoved) {
        this.dragMoved = false;
        return;
      }
      if (idx === this.currentIdx) {
        this.$emit('open-unit', chapter);
      } else {
        this.currentIdx = idx;
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.refreshIcons();
    });
    window.addEventListener('scroll', this.handleScroll);
  },
  unmounted() {
    window.removeEventListener('scroll', this.handleScroll);
    clearTimeout(this.hoverTimer);
  },
  updated() {
    this.$nextTick(() => {
      this.refreshIcons();
    });
  }
}
</script>

<style scoped src="./LandingView.css"></style>
