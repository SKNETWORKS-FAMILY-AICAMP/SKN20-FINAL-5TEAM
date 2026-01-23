<!-- 
수정일: 2026-01-23
수정내용: AI 엔지니어들을 위한 'Architecture Playground' 테마의 랜딩 페이지 구현.
          sports_gym.mp4 배경, 운동하는 오리 GIF 및 플로팅 애니메이션 적용.
-->
<template>
  <div class="landing-container">
    <!-- [Hero Section] -->
    <header class="hero-playground-premium">
      <video id="hero-video" src="/image/sports_gym.mp4" autoplay muted loop playsinline></video>
      <div class="hero-overlay-refined"></div>
      <div class="hero-scanline"></div>
      
      <div class="hero-content-premium">
        <div class="playground-badge-v2">
          <span class="badge-dot"></span>
          OPEN BETA v1.2
        </div>
        <h1 class="playground-title-v2">
          <span class="text-glow-premium">Architecture</span><br>
          <span class="text-neon-ultimate">Playground!</span>
        </h1>
        <p class="playground-subtitle-v2">
          단순한 실습을 넘어선 **압도적 아키텍처 경험.**<br>
          이제 오리들과 함께 당신의 한계를 돌파하세요. 🦆✨
        </p>
        
        <div class="hero-action-group-v2">
          <button @click="$emit('go-to-playground')" class="btn-play-premium">
            <div class="btn-glow-layer"></div>
            <span class="btn-text">입장하기!</span>
            <i data-lucide="arrow-right" class="btn-arrow"></i>
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
    <nav class="navbar-v2">
      <div class="logo-playground">AI-GYM</div>
      <div class="nav-links-v2">
        <a href="#chapters">Stages</a>
        <a href="#leaderboard">Hall of Fame</a>
        <div class="protein-status">
          <i data-lucide="milk" class="icon-protein"></i>
          <span>{{ userProteinShakes }}</span>
        </div>
        <slot name="auth-buttons"></slot>
      </div>
    </nav>

    <!-- [Chapters Section] -->
    <section id="chapters" class="playground-section-premium">
      <div class="background-grid-pattern"></div>
      <div class="section-header">
        <h2 class="title-with-mascot">
          Engineer's Gym 🎮 
        </h2>
        <p>원하는 훈련 기구를 선택하고 당신의 실력을 증명하세요!</p>
      </div>

      <div class="playground-grid">
        <div v-for="(chapter, idx) in chapters" :key="chapter.id" 
             class="gym-card-premium" 
             :class="'card-color-' + (idx % 5)"
             @click="$emit('open-unit', chapter)">
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
              <div class="unit-badge-row">
                <span class="unit-tag-v2">UNIT 0{{ idx + 1 }}</span>
                <span class="level-indicator">LV.{{ (idx + 1) * 10 }}</span>
              </div>
              <h3>{{ chapter.name }}</h3>
              <p>{{ chapter.description }}</p>
              <div class="card-footer-v2">
                <span class="engineer-count"><i data-lucide="users"></i> 80+ Training</span>
                <button class="btn-enter-mini">START</button>
              </div>
            </div>
          </div>
          <div class="card-border-glow"></div>
        </div>
      </div>
    </section>

    <!-- [Leaderboard Section Premium] -->
    <section id="leaderboard" class="lb-section-premium">
      <div class="lb-energy-pulse"></div>
      <div class="lb-wrapper-v2">
        <div class="lb-header-v2">
          <div class="lb-title-wrap">
            <span class="lb-subtitle">ENGINEER RANKING</span>
            <h2>오늘의 득근 전당 🏆</h2>
          </div>
          <p>상위 5명의 아키텍처 마스터들이 훈련장을 빛내고 있습니다.</p>
        </div>
        
        <div class="lb-glass-table-v2">
          <div class="lb-table-head">
            <span class="col-rank">Rank</span>
            <span class="col-user">Engineer</span>
            <span class="col-solved">Stages Mastered</span>
            <span class="col-shakes">Protein Points</span>
          </div>
          <div v-for="(user, index) in leaderboard" :key="user.id" 
               class="lb-row-v2" :class="'row-rank-' + (index + 1)">
            <div class="col-rank">
              <div class="rank-box">
                <span class="rank-num">#{{ index + 1 }}</span>
                <i v-if="index === 0" data-lucide="crown" class="crown-icon"></i>
              </div>
            </div>
            <div class="col-user">
              <div class="user-avatar-mini">
                <img src="/image/unit_duck.png" alt="avatar">
              </div>
              <span class="username-premium">{{ user.username }}</span>
            </div>
            <div class="col-solved">
              <span class="solved-count-v2">{{ user.solved }}</span>
              <span class="label-v2">UNITS</span>
            </div>
            <div class="col-shakes">
              <div class="shake-badge-v2">
                <i data-lucide="milk" class="milk-icon-v2"></i>
                <span>{{ user.shakes.toLocaleString() }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <footer class="playground-footer">
      <p>&copy; 2026 ARCH-GYM. Crafted with ❤️ by Antigravity AI.</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'LandingView',
  props: {
    isLoggedIn: Boolean,
    userProteinShakes: Number,
    chapters: Array,
    leaderboard: Array
  },
  methods: {
    scrollToLeaderboard() {
      document.getElementById('leaderboard')?.scrollIntoView({ behavior: 'smooth' });
    }
  },
  mounted() {
    if (window.lucide) window.lucide.createIcons();
  },
  updated() {
    this.$nextTick(() => {
      if (window.lucide) window.lucide.createIcons();
    });
  }
}
</script>

<style scoped>
.landing-container {
  background-color: #0c0e14;
  color: #fff;
  font-family: 'Outfit', sans-serif;
  overflow-x: hidden;
}

/* [Hero Playground Premium] */
.hero-playground-premium {
  position: relative;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: hidden;
  background-color: #0c0e14;
}

.hero-overlay-refined {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(12, 14, 20, 0.2) 0%, #0c0e14 100%);
  z-index: 1;
}

.hero-scanline {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, transparent, rgba(182, 255, 64, 0.05) 50%, transparent);
  background-size: 100% 4px;
  z-index: 2;
  pointer-events: none;
  animation: scan 10s linear infinite;
}

@keyframes scan {
  from { transform: translateY(-100%); }
  to { transform: translateY(100%); }
}

.hero-content-premium {
  position: relative;
  z-index: 10;
  padding: 2rem;
  animation: content-drift 5s ease-in-out infinite;
}

@keyframes content-drift {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.playground-badge-v2 {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  padding: 0.6rem 1.5rem;
  border-radius: 99px;
  font-weight: 800;
  font-size: 0.85rem;
  letter-spacing: 2px;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.badge-dot {
  width: 8px;
  height: 8px;
  background: #b6ff40;
  border-radius: 50%;
  box-shadow: 0 0 10px #b6ff40;
  animation: pulse-dot 1s infinite;
}

@keyframes pulse-dot {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.5); opacity: 0.5; }
}

.playground-title-v2 {
  font-size: 6.5rem;
  font-weight: 950;
  line-height: 0.85;
  margin-bottom: 2.5rem;
  letter-spacing: -2px;
}

.text-glow-premium {
  color: #fff;
  text-shadow: 0 0 30px rgba(255, 255, 255, 0.5), 0 0 60px rgba(255, 255, 255, 0.2);
}

.text-neon-ultimate {
  background: linear-gradient(90deg, #b6ff40, #34d399, #b6ff40);
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 20px rgba(182, 255, 64, 0.4));
  animation: shine 3s linear infinite;
}

@keyframes shine {
  to { background-position: 200% center; }
}

.playground-subtitle-v2 {
  font-size: 1.6rem;
  color: #cbd5e1;
  margin-bottom: 4rem;
  font-weight: 300;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.5;
}

.hero-action-group-v2 {
  display: flex;
  gap: 2rem;
  justify-content: center;
}

.btn-play-premium {
  position: relative;
  background: #b6ff40;
  color: #000;
  padding: 1.4rem 4rem;
  border-radius: 16px;
  font-weight: 950;
  font-size: 1.4rem;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 10px 40px rgba(182, 255, 64, 0.4);
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  overflow: hidden;
}

.btn-play-premium:hover {
  transform: scale(1.05) translateY(-5px);
  box-shadow: 0 20px 60px rgba(182, 255, 64, 0.6);
}

.btn-arrow {
  transition: transform 0.3s;
}

.btn-play-premium:hover .btn-arrow {
  transform: translateX(10px);
}

.btn-social-v2 {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  color: #fff;
  padding: 1.4rem 3rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 1.1rem;
}

.btn-social-v2:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-5px);
}

/* [Floating Decor] */
.hero-decor {
  position: absolute;
  background: rgba(182, 255, 64, 0.1);
  border: 1px solid rgba(182, 255, 64, 0.2);
  border-radius: 50%;
  z-index: 5;
  filter: blur(40px);
}

.decor-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  left: -100px;
  animation: float-decor 20s infinite alternate;
}

.decor-2 {
  width: 300px;
  height: 300px;
  bottom: 0px;
  right: -50px;
  animation: float-decor 25s infinite alternate-reverse;
}

@keyframes float-decor {
  from { transform: translate(0, 0); }
  to { transform: translate(100px, 100px); }
}

.duck-1-premium {
  top: 15%;
  right: 12%;
  width: 180px;
  animation: float1 5s ease-in-out infinite;
}

.duck-2-premium {
  bottom: 12%;
  left: 8%;
  width: 150px;
  animation: float2 6s ease-in-out infinite;
}

@keyframes float1 {
  0%, 100% { transform: translateY(0) rotate(5deg); }
  50% { transform: translateY(-30px) rotate(-5deg); }
}

@keyframes float2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(20px, -20px) scale(1.1); }
}

/* [Navbar] */
.navbar-v2 {
  position: fixed;
  top: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 1200px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  padding: 1rem 2rem;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1000;
}

.logo-playground {
  font-weight: 900;
  font-size: 1.5rem;
  letter-spacing: 2px;
  color: #b6ff40;
}

.nav-links-v2 {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.nav-links-v2 a {
  text-decoration: none;
  color: #94a3b8;
  font-weight: 600;
  transition: color 0.3s;
}

.nav-links-v2 a:hover {
  color: #fff;
}

.protein-status {
  background: rgba(56, 189, 248, 0.1);
  color: #38bdf8;
  padding: 0.5rem 1rem;
  border-radius: 99px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(56, 189, 248, 0.2);
}

/* [Premium Playground Section] */
.playground-section-premium {
  position: relative;
  padding: 10rem 2rem;
  max-width: 1400px;
  margin: 0 auto;
  overflow: hidden;
}

.background-grid-pattern {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(182, 255, 64, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(182, 255, 64, 0.05) 1px, transparent 1px);
  background-size: 50px 50px;
  mask-image: radial-gradient(circle at center, black, transparent 80%);
  pointer-events: none;
  z-index: 0;
  animation: bg-shift 20s linear infinite;
}

@keyframes bg-shift {
  from { transform: translateY(0); }
  to { transform: translateY(50px); }
}

.section-header {
  position: relative;
  z-index: 10;
  text-align: center;
  margin-bottom: 6rem;
}

.title-with-mascot {
  font-size: 3.5rem;
  font-weight: 950;
  color: #fff;
  text-shadow: 0 0 30px rgba(182, 255, 64, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.playground-grid {
  position: relative;
  z-index: 10;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 3rem;
  perspective: 1000px;
}

.gym-card-premium {
  position: relative;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border-radius: 32px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
  cursor: pointer;
  transform-style: preserve-3d;
}

.gym-card-premium:hover {
  transform: translateY(-20px) rotateX(10deg) rotateY(-5deg);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(182, 255, 64, 0.4);
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.4),
    0 0 50px rgba(182, 255, 64, 0.1);
}

.card-inner-v2 {
  padding: 3rem;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card-image-wrap-v2 {
  position: relative;
  width: 220px; /* 기존 180px에서 확대 */
  height: 220px;
  margin: 0 auto 2.5rem auto;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(60px); /* 3D 효과 강화 */
}

.premium-icon {
  width: 100%; /* 이미지를 꽉 차게 변경 */
  height: 100%;
  object-fit: contain;
  z-index: 5;
  filter: drop-shadow(0 15px 30px rgba(0, 0, 0, 0.6));
  transition: transform 0.4s ease;
}

.gym-card-premium:hover .premium-icon {
  transform: scale(1.15) translateY(-5px);
}

/* Energy Rings Animation */
.energy-rings span {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border: 2px solid rgba(182, 255, 64, 0.4);
  border-radius: 50%;
  pointer-events: none;
}

.ring-1 { width: 110%; height: 110%; animation: spin-ring 4s linear infinite; border-style: dashed !important; }
.ring-2 { width: 140%; height: 140%; animation: spin-ring 6s linear reverse infinite; opacity: 0.4; }
.ring-3 { width: 90%; height: 90%; animation: pulse-ring 2s ease-in-out infinite; border-color: #b6ff40 !important; border-width: 3px !important; }

@keyframes spin-ring {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes pulse-ring {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
  50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.7; }
}

.card-aura-premium {
  position: absolute;
  inset: -20px;
  background: radial-gradient(circle, rgba(182, 255, 64, 0.15) 0%, transparent 70%);
  z-index: 0;
  filter: blur(10px);
}

.unit-badge-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.unit-tag-v2 {
  font-weight: 900;
  font-size: 0.75rem;
  letter-spacing: 1.5px;
  color: #b6ff40;
  background: rgba(182, 255, 64, 0.1);
  padding: 4px 12px;
  border-radius: 6px;
}

.level-indicator {
  font-family: 'Orbitron', sans-serif;
  font-weight: 800;
  font-size: 0.8rem;
  color: #ccc;
}

.card-text-v2 h3 {
  font-size: 2.2rem;
  font-weight: 950;
  margin-bottom: 0.8rem;
  background: linear-gradient(to right, #fff, #94a3b8);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.card-text-v2 p {
  color: #94a3b8;
  font-size: 1.05rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.card-footer-v2 {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.engineer-count {
  font-size: 0.85rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-enter-mini {
  background: #fff;
  color: #000;
  border: none;
  padding: 8px 20px;
  border-radius: 8px;
  font-weight: 900;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s;
}

.gym-card-premium:hover .btn-enter-mini {
  background: #b6ff40;
  transform: scale(1.1);
}

.card-border-glow {
  position: absolute;
  inset: -1px;
  border-radius: 32px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(182, 255, 64, 0.4), transparent, rgba(99, 102, 241, 0.4));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.4s;
}

.gym-card-premium:hover .card-border-glow {
  opacity: 1;
}

/* [Leaderboard Premium] */
.lb-section-premium {
  position: relative;
  padding: 12rem 2rem;
  background: #06070a;
  overflow: hidden;
}

.lb-energy-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.05) 0%, transparent 60%);
  pointer-events: none;
  animation: lb-pulse 10s ease-in-out infinite;
}

@keyframes lb-pulse {
  0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.1); }
}

.lb-wrapper-v2 {
  max-width: 1100px;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

.lb-header-v2 {
  text-align: center;
  margin-bottom: 5rem;
}

.lb-subtitle {
  color: #6366f1;
  font-weight: 900;
  letter-spacing: 4px;
  font-size: 0.9rem;
  display: block;
  margin-bottom: 1rem;
}

.lb-header-v2 h2 {
  font-size: 3.5rem;
  font-weight: 950;
  color: #fff;
  margin-bottom: 1.5rem;
}

.lb-header-v2 p {
  color: #94a3b8;
  font-size: 1.1rem;
}

.lb-glass-table-v2 {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(40px);
  border-radius: 40px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 1.5rem;
  box-shadow: 
    0 40px 100px rgba(0, 0, 0, 0.6),
    inset 0 0 20px rgba(255, 255, 255, 0.02);
}

.lb-table-head {
  display: grid;
  grid-template-columns: 120px 1fr 200px 200px;
  padding: 1.5rem 2.5rem;
  color: #64748b;
  font-weight: 800;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.lb-row-v2 {
  display: grid;
  grid-template-columns: 120px 1fr 200px 200px;
  padding: 1.8rem 2.5rem;
  align-items: center;
  margin-bottom: 0.8rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.015);
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  border: 1px solid transparent;
}

.lb-row-v2:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: scale(1.02) translateX(10px);
  border-color: rgba(99, 102, 241, 0.3);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
}

.rank-box {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rank-num {
  font-family: 'Orbitron', sans-serif;
  font-weight: 900;
  font-size: 1.4rem;
  color: #475569;
}

.row-rank-1 .rank-num { color: #facc15; text-shadow: 0 0 15px rgba(250, 204, 21, 0.5); font-size: 1.8rem; }
.row-rank-2 .rank-num { color: #cbd5e1; }
.row-rank-3 .rank-num { color: #94a3b8; }

.crown-icon {
  width: 24px;
  height: 24px;
  color: #facc15;
  filter: drop-shadow(0 0 8px rgba(250, 204, 21, 0.6));
  animation: crown-float 2s ease-in-out infinite;
}

@keyframes crown-float {
  0%, 100% { transform: translateY(0) rotate(-10deg); }
  50% { transform: translateY(-5px) rotate(10deg); }
}

.col-user {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-avatar-mini {
  width: 45px;
  height: 45px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 5px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.user-avatar-mini img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.username-premium {
  font-size: 1.25rem;
  font-weight: 800;
  color: #fff;
}

.solved-count-v2 {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.5rem;
  font-weight: 950;
  color: #fff;
  margin-right: 8px;
}

.label-v2 {
  font-size: 0.75rem;
  font-weight: 900;
  color: #64748b;
  letter-spacing: 1px;
}

.shake-badge-v2 {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: rgba(56, 189, 248, 0.1);
  padding: 8px 18px;
  border-radius: 100px;
  color: #38bdf8;
  font-weight: 900;
  font-size: 1.1rem;
  border: 1px solid rgba(56, 189, 248, 0.2);
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.1);
}

.milk-icon-v2 {
  width: 18px;
  height: 18px;
}

.row-rank-1 {
  background: linear-gradient(90deg, rgba(250, 204, 21, 0.08), rgba(250, 204, 21, 0.02)) !important;
  border-left: 4px solid #facc15 !important;
}

.playground-footer {
  text-align: center;
  padding: 4rem;
  color: #475569;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}
</style>
