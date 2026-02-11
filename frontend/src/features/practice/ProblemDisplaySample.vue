<!--
수정일: 2026-02-11
수정내용: PracticeDetail(ID: bughunt01) 데이터를 동적으로 가져와 표시하는 샘플 구현
-->
<template>
  <div class="sample-container">
    <div v-if="loading" class="loading">데이터 로딩 중...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="problemData" class="problem-card">
      <header class="problem-header">
        <span class="badge">{{ problemData.detail_type }}</span>
        <h1 class="title">{{ problemData.detail_title }}</h1>
      </header>

      <section class="content-section" v-if="problemData.content_data">
        <div class="scenario-box">
          <h2>시나리오</h2>
          <p>{{ problemData.content_data.scenario || problemData.content_data.description }}</p>
        </div>

        <div class="details-grid">
          <div class="detail-item">
            <span class="label">난이도:</span>
            <span class="value">{{ problemData.content_data.difficulty || problemData.content_data.level }}</span>
          </div>
          <div class="detail-item" v-if="problemData.content_data.logic_type">
            <span class="label">로직 유형:</span>
            <span class="value">{{ problemData.content_data.logic_type }}</span>
          </div>
        </div>

        <!-- 카드 목록 (예제) -->
        <div class="cards-section" v-if="problemData.content_data.cards">
          <h2>관련 카드</h2>
          <div class="cards-list">
            <div v-for="card in problemData.content_data.cards" :key="card.id" class="data-card" :style="{ borderLeft: `4px solid ${card.color || '#ccc'}` }">
              <span class="card-icon">{{ card.icon }}</span>
              <div class="card-text">
                <div class="ko">{{ card.text_ko }}</div>
                <div class="py"><code>{{ card.text_py }}</code></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 가이드라인 (예제) -->
        <div class="rules-section" v-if="problemData.content_data.designContext?.engineeringRules">
          <h2>엔지니어링 규칙</h2>
          <ul>
            <li v-for="(rule, idx) in problemData.content_data.designContext.engineeringRules" :key="idx">
              {{ rule }}
            </li>
          </ul>
        </div>
      </section>

      <footer class="problem-footer">
        <p>ID: {{ problemData.id }} | 표시 순서: {{ problemData.display_order }}</p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const problemData = ref(null);
const loading = ref(true);
const error = ref(null);

// 특정 ID(bughunt01) 데이터를 가져오는 함수
const fetchProblemDetail = async (id) => {
  try {
    loading.value = true;
    // 백엔드에 새로 추가한 동적 API 엔드포인트 호출
    const response = await axios.get(`/api/core/practice-details/${id}/`);
    problemData.value = response.data;
    console.log('Fetched data:', problemData.value);
  } catch (err) {
    console.error('Error fetching problem detail:', err);
    error.value = '데이터를 불러오는 중 오류가 발생했습니다.';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchProblemDetail('bughunt01'); // 원하는 ID를 넣어서 호출 가능
});
</script>

<style scoped>
.sample-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
  font-family: 'Inter', sans-serif;
  color: #333;
}

.problem-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  overflow: hidden;
  border: 1px solid #eee;
}

.problem-header {
  background: #f8f9fa;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #007bff;
  color: #fff;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.title {
  margin: 0;
  font-size: 1.5rem;
  color: #222;
}

.content-section {
  padding: 1.5rem;
}

.scenario-box {
  background: #fff9db;
  padding: 1rem;
  border-left: 4px solid #fab005;
  margin-bottom: 1.5rem;
}

.scenario-box h2 {
  margin-top: 0;
  font-size: 1.1rem;
  color: #862e1e;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-item .label {
  font-weight: bold;
  margin-right: 0.5rem;
  color: #666;
}

.cards-section, .rules-section {
  margin-top: 2rem;
}

.cards-section h2, .rules-section h2 {
  font-size: 1.2rem;
  border-bottom: 2px solid #eee;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.cards-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.data-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f1f3f5;
  border-radius: 8px;
}

.card-icon {
  font-size: 1.5rem;
}

.py code {
  background: #e9ecef;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  color: #d6336c;
}

.rules-section ul {
  padding-left: 1.25rem;
}

.rules-section li {
  margin-bottom: 0.5rem;
  color: #444;
}

.problem-footer {
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  font-size: 0.85rem;
  color: #888;
  text-align: right;
  border-top: 1px solid #eee;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
}

.error {
  color: #fa5252;
}
</style>
