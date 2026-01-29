<template>
  <div class="pseudo-company-container">
    <div class="header">
      <div class="unit-tag">UNIT 1 SPECIAL</div>
      <h1>🏢 Pseudo Company</h1>
      <p>실제 기업의 로직을 체험해보는 비즈니스 시뮬레이션입니다.</p>
    </div>

    <div class="content-placeholder">
      <div class="card">
        <div class="icon">🏗️</div>
        <h3>Coming Soon</h3>
        <p>Pseudo Company 모드가 준비 중입니다.<br>기업용 복잡한 비즈니스 로직을 설계하고 검증해보는 공간이 될 것입니다.</p>
      </div>
    </div>

    <div class="footer">
      <button @click="$emit('close')" class="back-btn">돌아가기</button>
    </div>
  </div>
</template>

<script setup>
/**
 * [수정일: 2026-01-29]
 * [내용: Pseudo Company 메뉴 추가 및 기초 프레임워크 구축]
 */
defineEmits(['close']);
</script>

<style scoped>
.pseudo-company-container {
  position: fixed;
  inset: 0;
  background: #0f172a;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  z-index: 150;
  font-family: 'Jua', sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 3rem;
}

.unit-tag {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  background: #334155;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: #94a3b8;
}

h1 {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #38bdf8;
}

p {
  color: #94a3b8;
  font-size: 1.2rem;
}

.content-placeholder {
  max-width: 600px;
  width: 100%;
}

.card {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  padding: 3rem;
  border-radius: 3rem;
  text-align: center;
  backdrop-filter: blur(10px);
}

.icon {
  font-size: 5rem;
  margin-bottom: 1rem;
}

h3 {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: white;
}

.footer {
  margin-top: 4rem;
}

.back-btn {
  padding: 1rem 3rem;
  background: #38bdf8;
  color: #0f172a;
  border: none;
  border-radius: 1rem;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  transform: scale(1.05);
  filter: brightness(1.1);
}
</style>
