<template>
  <div class="lobby-container">
    <div class="neon-bg"></div>
    
    <header class="lobby-header">
      <h1 class="neon-text">WAR ROOM LOBBY</h1>
      <div class="mission-brief">
        <span class="label">CURRENT MISSION</span>
        <h2 class="title">{{ gameStore.activeWarsMission?.mission_title || '미배정 미션' }}</h2>
      </div>
    </header>

    <main class="lobby-content">
      <!-- Left: Team List & Role Selection -->
      <div class="left-section">
        <section class="team-panel glass-panel">
          <div class="panel-header">
            <h3>TEAM STATUS</h3>
            <span class="count">{{ onlineMembers.length }}/3 READY</span>
          </div>
          <div class="member-list">
            <div v-for="member in onlineMembers" :key="member.id" class="member-card" :class="{ 'me': member.isMe }">
              <div class="avatar-box">
                <div class="avatar"></div>
                <div class="role-badge">{{ member.role }}</div>
              </div>
              <div class="info">
                <span class="name">{{ member.name }}</span>
                <span class="status">{{ member.isMe ? 'YOU (LEADER)' : 'CONNECTED' }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- [Phase 3] Role Selection Cards -->
        <section class="role-selection glass-panel">
          <div class="panel-header">
            <h3>CHOOSE YOUR SPECIALTY</h3>
          </div>
          <div class="role-grid">
            <div 
              v-for="role in roles" 
              :key="role.id" 
              class="role-card" 
              :class="{ 'active': selectedRoleId === role.id, 'taken': isRoleTaken(role.id) }"
              @click="selectRole(role.id)"
            >
              <div class="role-icon">{{ role.icon }}</div>
              <div class="role-info">
                <h4 class="role-name">{{ role.name }}</h4>
                <p class="role-desc">{{ role.description }}</p>
              </div>
              <div class="role-status" v-if="isRoleTaken(role.id)">TAKEN</div>
            </div>
          </div>
        </section>
      </div>

      <!-- Right: Chat/Console -->
      <section class="console-panel glass-panel">
        <div class="panel-header">
          <h3>TACTICAL COMMS</h3>
        </div>
        <div class="console-log" ref="consoleLog">
          <div class="log-entry system">[SYSTEM] 전술 네트워크에 연결되었습니다.</div>
          <div v-for="(msg, idx) in lobbyMessages" :key="idx" class="log-entry">
            <span class="sender">{{ msg.sender }}:</span>
            <span class="text">{{ msg.text }}</span>
          </div>
        </div>
        <div class="console-input">
          <input 
            v-model="newMsg" 
            placeholder="팀원에게 작전 지시..." 
            @keyup.enter="sendMsg"
          />
        </div>
      </section>
    </main>

    <footer class="lobby-footer">
      <!-- [P1] 3명 미만 시 경고 + 버튼 비활성화 -->
      <div class="action-hint" v-if="!selectedRoleId">
        <span class="hint-icon">👆</span>
        <span>역할을 먼저 선택해주세요</span>
      </div>
      <div class="action-hint" v-else-if="onlineMembers.length < 3">
        <span class="hint-icon">⚠️</span>
        <span v-if="onlineMembers.length === 1">팀원 2명이 더 필요합니다. ({{ 3 - onlineMembers.length }}명 대기 중)</span>
        <span v-else>팀원 1명이 더 필요합니다. ({{ 3 - onlineMembers.length }}명 대기 중)</span>
        <span class="solo-hint"> — 혼자 테스트하려면 아래 버튼 길게 클릭</span>
      </div>
      <div class="btn-group">
        <button 
          class="btn-start neon-btn"
          :class="{ 'disabled-start': onlineMembers.length < 3 || !selectedRoleId }"
          :disabled="onlineMembers.length < 3 || !selectedRoleId"
          @click="startGame"
        >
          START MISSION
          <span class="member-count-badge">{{ onlineMembers.length }}/3</span>
        </button>
        <!-- 디버그용 돌애 시작 -->
        <button class="btn-solo" @click="startGame" title="1인 테스트 모드">
          🔧 Solo Test
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useGameStore } from '@/stores/game';
import { useAuthStore } from '@/stores/auth';
import { useWarsSocket } from './composables/useWarsSocket';

const router = useRouter();
const gameStore = useGameStore();
const { 
  isConnected, 
  connectSocket, 
  changeRole, 
  socket, 
  teamMessages,
  sendTeamChat,
  disconnectSocket,
  teamMembers,
  startMission,
  onMissionStart
} = useWarsSocket();

// 전문 역할군 정의
const roles = [
  { 
    id: 'architect', 
    name: 'MAIN ARCHITECT', 
    icon: '🏗️', 
    description: '시스템의 뼈대를 잡고 전체 컴포넌트 배치를 주도합니다.' 
  },
  { 
    id: 'ops', 
    name: 'OPS/SECURITY', 
    icon: '🛡️', 
    description: '서버 부하 분산 및 방화벽 정책 등 보안 인프라를 담당합니다.' 
  },
  { 
    id: 'db', 
    name: 'DB/PERFORMANCE', 
    icon: '⚡', 
    description: '데이터 일관성 유지 및 캐시 전략을 통해 응답 속도를 최적화합니다.' 
  }
];

// [버그수정] 기본값 null → 역할을 반드시 선택해야 시작 가능
// [수정일: 2026-02-24] 저장된 역할이 있으면 초기값으로 사용
const selectedRoleId = ref(gameStore.userRole);

const lobbyMessages = computed(() => teamMessages.value.map(m => ({
  sender: m.sender_name,
  text: m.content
})));

const authStore = useAuthStore();
const currentUserName = computed(() => authStore.sessionNickname || '플레이어');

const sendMsg = () => {
  if (!newMsg.value.trim() || !gameStore.activeWarsMission) return;
  sendTeamChat(gameStore.activeWarsMission.id, currentUserName.value, newMsg.value);
  newMsg.value = '';
};

const selectRole = (roleId) => {
  if (isRoleTaken(roleId)) return; // 이미 선택된 역할 무시

  selectedRoleId.value = roleId;
  // store에 roleId(소문자) 저장
  gameStore.setUserRole(roleId);

  // [버그수정] roleName 대신 roleId를 소켓으로 전송 → 서버도 id 기준으로 저장
  if (gameStore.activeWarsMission) {
    changeRole(gameStore.activeWarsMission.id, roleId);
  }
};

// [수정일: 2026-02-23] 팀원 목록을 소켓 데이터와 결합
const onlineMembers = computed(() => {
  const members = [
    { id: 'me', name: currentUserName.value, isMe: true, role: gameStore.userRole ? gameStore.userRole.toUpperCase() : '역할 선택 중' }
  ];
  
  // 소켓에서 받은 다른 팀원들 추가
  teamMembers.value.forEach(m => {
    if (m.user_name !== currentUserName.value || m.sid !== socket.value?.id) {
       members.push({
         id: m.sid,
         name: m.user_name,
         isMe: false,
         role: m.user_role
       });
    }
  });
  
  return members;
});

// [P1] 실제 팀원 역할 중복 확인
const isRoleTaken = (roleId) => {
  // [수정일: 2026-02-24] 'pending'이나 빈 값은 점유된 것으로 보지 않음
  return teamMembers.value.some(
    m => m.user_role && m.user_role !== 'pending' && m.user_role.toLowerCase() === roleId.toLowerCase()
  );
};

const startGame = () => {
  if (gameStore.activeWarsMission) {
    // [수정일: 2026-02-24] 리더가 미션을 시작하면 방 전체에 신호 전송
    startMission(gameStore.activeWarsMission.id);
  } else {
    // 솔로 테스트 등 예외 시 로컬 이동
    const role = selectedRoleId.value || 'architect';
    gameStore.setUserRole(role);
    router.push(`/practice/coduck-wars/battle?role=${role}`);
  }
};

onMounted(async () => {
  if (!authStore.sessionNickname) {
    await authStore.checkSession();
  }

  if (!gameStore.activeWarsMission) {
    router.push('/practice/coduck-wars/briefing');
    return;
  }

  // [버그수정] 입장 시 gameStore.userRole(이미 selectRole에서 세팅됨) 사용
  // [수정일: 2026-02-24] 리더가 미션을 시작했을 때 모든 팀원 화면 전환
  onMissionStart.value = (missionId) => {
    const role = selectedRoleId.value || 'architect';
    gameStore.setUserRole(role);
    router.push(`/practice/coduck-wars/battle?role=${role}`);
  };

  const myRole = gameStore.userRole || 'pending';
  connectSocket(gameStore.activeWarsMission.id, currentUserName.value, myRole);
});

onUnmounted(() => {
  disconnectSocket();
});
</script>

<style scoped>
.lobby-container {
  min-height: 100vh;
  background: #020617;
  color: #f8fafc;
  padding: 3rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  font-family: 'Orbitron', sans-serif;
  position: relative;
  overflow: hidden;
}

.neon-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 30%, rgba(56, 189, 248, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
  z-index: 0;
}

.lobby-header {
  position: relative;
  z-index: 10;
  text-align: center;
}

.neon-text {
  font-size: 3rem;
  background: linear-gradient(to right, #38bdf8, #818cf8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.5));
}

.mission-brief {
  margin-top: 1rem;
}

.mission-brief .label {
  font-size: 0.7rem;
  color: #64748b;
  letter-spacing: 2px;
}

.mission-brief .title {
  font-size: 1.5rem;
  color: #f8fafc;
  margin-top: 0.5rem;
}

.lobby-content {
  position: relative;
  z-index: 10;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 2rem;
  flex: 1;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.left-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.glass-panel {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 1.5rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: 0.75rem;
}

.panel-header h3 {
  font-size: 0.9rem;
  color: #38bdf8;
  letter-spacing: 1px;
}

/* Role Selection Grid */
.role-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.role-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.role-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(56, 189, 248, 0.3);
  transform: translateX(10px);
}

.role-card.active {
  background: rgba(56, 189, 248, 0.1);
  border-color: #38bdf8;
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
}

.role-card.active::before {
  content: '✓';
  position: absolute;
  right: 1.5rem;
  top: 50%;
  transform: translateY(-50%);
  color: #38bdf8;
  font-weight: 900;
}

.role-icon {
  font-size: 2rem;
}

.role-name {
  font-size: 1.1rem;
  font-weight: 800;
  margin-bottom: 0.25rem;
}

.role-desc {
  font-size: 0.8rem;
  color: #94a3b8;
  line-height: 1.4;
}

/* Member list refinements */
.avatar-box {
  position: relative;
}

.role-badge {
  position: absolute;
  bottom: -5px;
  right: -5px;
  font-size: 0.6rem;
  background: #38bdf8;
  color: #020617;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 800;
}

.member-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 1rem;
}

.member-card.me {
  border-color: rgba(56, 189, 248, 0.3);
  background: rgba(56, 189, 248, 0.05);
}

.avatar {
  width: 50px;
  height: 50px;
  background: #1e293b;
  border-radius: 50%;
  border: 2px solid #38bdf8;
}

.avatar-placeholder {
  width: 50px;
  height: 50px;
  background: #0f172a;
  border-radius: 50%;
  border: 2px dashed #334155;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #334155;
}

.info .name {
  display: block;
  font-weight: 700;
  font-size: 1.1rem;
}

.info .status {
  font-size: 0.75rem;
  color: #94a3b8;
}

.member-card.empty {
  opacity: 0.5;
}

.console-panel {
  font-family: 'JetBrains Mono', monospace;
}

.console-log {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
}

.log-entry {
  font-size: 0.9rem;
  line-height: 1.5;
}

.log-entry.system {
  color: #64748b;
  font-style: italic;
}

.log-entry .sender {
  color: #38bdf8;
  margin-right: 0.75rem;
}

.console-input {
  margin-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 1rem;
}

.console-input input {
  width: 100%;
  background: transparent;
  border: none;
  color: #f8fafc;
  font-family: inherit;
  font-size: 1rem;
  outline: none;
}

.lobby-footer {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.action-hint {
  font-size: 0.9rem;
  color: #f59e0b;
}

.btn-start {
  padding: 1.5rem 6rem;
  border-radius: 4rem;
  background: #f8fafc;
  color: #020617;
  font-weight: 900;
  font-size: 1.25rem;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
}

.btn-start:hover:not(:disabled) {
  transform: translateY(-5px);
  box-shadow: 0 0 40px rgba(56, 189, 248, 0.4);
  background: #38bdf8;
}

.btn-start.disabled-start {
  background: #1e293b;
  color: #475569;
  cursor: not-allowed;
  box-shadow: none;
}

.member-count-badge {
  margin-left: 0.75rem;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  font-size: 0.8rem;
}

.disabled-start .member-count-badge {
  background: rgba(71, 85, 105, 0.2);
  color: #475569;
}

.btn-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-solo {
  padding: 0.7rem 1.2rem;
  border-radius: 2rem;
  background: transparent;
  border: 1px solid #334155;
  color: #64748b;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-solo:hover {
  border-color: #64748b;
  color: #94a3b8;
}

.action-hint {
  font-size: 0.85rem;
  color: #f59e0b;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.solo-hint { color: #475569; font-size: 0.75rem; }
</style>
