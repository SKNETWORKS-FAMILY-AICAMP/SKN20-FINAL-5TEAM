<template>
  <div class="management-container">
    <header class="mgmt-header">
      <button class="back-btn" @click="$emit('close')">&times;</button>
      <div class="badge">ADMIN SYSTEM</div>
      <h1 class="title">Overall Training Progress</h1>
      <p class="subtitle">모든 요원들의 훈련 진척도를 실시간으로 모니터링합니다.</p>
    </header>

    <div class="stats-grid">
      <div v-for="user in overallProgress" :key="user.user_id" class="user-card">
        <div class="user-info">
          <span class="user-nickname">{{ user.nickname }}</span>
          <span class="user-email">{{ user.email }}</span>
        </div>
        
        <div class="progress-list">
          <div v-for="prog in user.progress" :key="prog.practice_id" class="prog-item" @click="showUserDetail(user, prog.practice_id)">
            <div class="prog-label">
              <span>{{ prog.practice_title }}</span>
              <span>{{ Math.round(prog.progress_rate) }}%</span>
            </div>
            <div class="prog-bar-bg">
              <div class="prog-bar-fill" :style="{ width: prog.progress_rate + '%', backgroundColor: getStatusColor(prog.progress_rate) }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 답변 상세 조회 모달 -->
    <transition name="fade">
      <div v-if="selectedUser" class="modal-overlay" @click.self="selectedUser = null">
        <div class="modal-content detail-modal">
          <header class="modal-header">
            <h3>{{ selectedUser.nickname }}'s Record ({{ selectedPracticeTitle }})</h3>
            <button class="close-btn" @click="selectedUser = null">&times;</button>
          </header>
          
          <div class="modal-body">
            <div v-if="loadingDetail" class="loading">Loading records...</div>
            <div v-else-if="userAnswers.length === 0" class="no-data">제출된 답변이 없습니다.</div>
            <div v-else class="answer-list">
              <div v-for="ans in userAnswers" :key="ans.detail_id" class="answer-card">
                <div class="card-header">
                  <span class="ans-title">{{ ans.title }}</span>
                  <span class="ans-badge" :class="{ 'perfect': ans.is_perfect }">{{ ans.score }}pts</span>
                </div>
                <div class="card-body">
                  <pre class="code-block">{{ formatAnswer(ans.submitted_data) }}</pre>
                  <div class="ans-date">{{ formatDate(ans.solved_date) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, defineEmits } from 'vue';
import axios from 'axios';

const emit = defineEmits(['close']);
const overallProgress = ref([]);
const selectedUser = ref(null);
const userAnswers = ref([]);
const selectedPracticeTitle = ref('');
const loadingDetail = ref(false);

const fetchOverallProgress = async () => {
  try {
    const res = await axios.get('/api/core/management/overall-progress/');
    overallProgress.value = res.data;
  } catch (err) {
    console.error('Failed to fetch progress:', err);
  }
};

const showUserDetail = async (user, practiceId) => {
  selectedUser.value = user;
  loadingDetail.value = true;
  userAnswers.value = [];
  
  // 제목 찾기
  const practice = user.progress.find(p => p.practice_id === practiceId);
  selectedPracticeTitle.value = practice ? practice.practice_title : '';

  try {
    const res = await axios.get(`/api/core/management/user-answers/${practiceId}/${user.user_id}/`);
    userAnswers.value = res.data.answers;
  } catch (err) {
    console.error('Failed to fetch answers:', err);
  } finally {
    loadingDetail.value = false;
  }
};

const getStatusColor = (rate) => {
  if (rate >= 90) return '#58cc02';
  if (rate >= 50) return '#1cb0f6';
  return '#ff9600';
};

const formatAnswer = (data) => {
  if (!data) return 'N/A';
  if (typeof data === 'string') return data;
  return JSON.stringify(data, null, 2);
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString();
};

onMounted(fetchOverallProgress);
</script>

<style scoped src="./ManagementView.css"></style>
