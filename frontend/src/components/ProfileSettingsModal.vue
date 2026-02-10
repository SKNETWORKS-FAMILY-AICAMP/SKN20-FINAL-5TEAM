<!--
  역할: 가입된 회원 정보를 수정하는 모달 컴포넌트
  기능: 현재 사용자 정보 로드, 정보 수정(PATCH), 아바타 실시간 재생성 지원
-->
<template>
  <transition name="fade">
    <div v-if="isOpen" class="modal-overlay">
      <div class="auth-container">
        <header class="auth-header">
          <div class="auth-badge">ANTIGRAVITY PROFILE</div>
          <h2 class="auth-title">Update Your Gear</h2>
          <p class="auth-subtitle">엔지니어의 정보를 최신 상태로 유지하세요.</p>
        </header>
        
        <form @submit.prevent="updateProfile">
          <div class="auth-body">
            <div class="input-group">
              <label class="input-label">ENGINEER CALLSIGN</label>
              <input type="text" v-model="nickname" class="auth-input" placeholder="호출명 수정">
            </div>
            <div class="input-group">
              <label class="input-label">ENGINEERING ID (READ-ONLY)</label>
              <input type="email" :value="email" class="auth-input" disabled style="opacity: 0.6; cursor: not-allowed;">
            </div>
            <div class="input-group">
              <label class="input-label">NEW ACCESS SECRET (OPTIONAL)</label>
              <input type="password" v-model="password" class="auth-input" placeholder="비어두면 기존 비밀번호 유지">
            </div>

            <!-- 아바타 수정 섹션 -->
            <div class="input-group avatar-custom-section" style="margin-top: 1.5rem; padding: 1rem; background: rgba(182, 255, 64, 0.05); border-radius: 12px; border: 1px dashed rgba(182, 255, 64, 0.3);">
              <label class="input-label" style="color: #b6ff40; display: flex; align-items: center; gap: 8px;">
                 <i data-lucide="sparkles" style="width: 16px;"></i> NANO-BANANA AVATAR UPDATE
              </label>
              <div style="display: flex; gap: 1rem; margin-top: 0.8rem;">
                <div style="flex: 2;">
                  <input type="text" v-model="avatarStyle" class="auth-input" placeholder="새로운 스타일 (Ex. Space Wizard Duck)" @keydown.enter.prevent="previewAvatar" style="border-color: rgba(182, 255, 64, 0.4);">
                </div>
                <button type="button" class="btn btn-primary" @click="previewAvatar" :disabled="isPreviewing" style="width: 100px; height: 48px; min-height: 48px; font-weight: 800; font-size: 0.85rem; border-radius: 8px !important; flex: none; display: flex; align-items: center; justify-content: center; padding: 0 !important;">
                  {{ isPreviewing ? '...' : 'RE-GEN' }}
                </button>
              </div>
              
              <div class="avatar-preview-display" style="margin-top: 1.5rem; display: flex; justify-content: center; width: 100%;">
                <AvatarFrame 
                  v-if="avatarPreviewUrl" 
                  :src="avatarPreviewUrl" 
                  :rank="authStore.user?.current_rank || 'BRONZE'" 
                  size="220px" 
                  class="preview-card avatar-preview-box"
                />
              </div>
            </div>

            <!-- 직무 및 관심사 (개발자 전용) -->
            <div class="input-group" style="margin-top: 1rem;">
                <label class="input-label">JOB ROLE</label>
                <div class="checkbox-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;">
                  <label v-for="role in jobRolesOptions" :key="role.value" class="checkbox-item" style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                    <input type="checkbox" :value="role.value" v-model="jobRole" style="accent-color: var(--primary);">
                    <span style="font-size: 0.9rem; color: #cbd5e1;">{{ role.label }}</span>
                  </label>
                </div>
            </div>

            <div class="input-group" style="margin-top: 1rem;">
                <label class="input-label">INTERESTS</label>
                <div class="checkbox-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;">
                  <label v-for="opt in interestsOptions" :key="opt.value" class="checkbox-item" style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                    <input type="checkbox" :value="opt.value" v-model="interests" style="accent-color: var(--primary);">
                    <span style="font-size: 0.9rem; color: #cbd5e1;">{{ opt.label }}</span>
                  </label>
                </div>
            </div>
          </div>
          
          <footer class="auth-footer">
            <button type="button" class="btn btn-secondary" @click="$emit('close')" style="flex: 1;">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting" style="flex: 2;">
              {{ isSubmitting ? 'UPDATING...' : '저장하기' }}
            </button>
          </footer>
        </form>
      </div>
    </div>
  </transition>
</template>

<script>
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import AvatarFrame from '@/components/AvatarFrame.vue';

export default {
  name: 'ProfileSettingsModal',
  components: { AvatarFrame },
  props: {
    isOpen: { type: Boolean, required: true }
  },
  data() {
    return {
      nickname: '',
      email: '',
      password: '',
      jobRole: [],
      jobRolesOptions: [],
      interests: [],
      interestsOptions: [],
      avatarStyle: '',
      avatarPreviewUrl: '',
      isPreviewing: false,
      isSubmitting: false,
      avatarSeed: Math.floor(Math.random() * 100000)
    }
  },
  setup() {
    const authStore = useAuthStore();
    return { authStore };
  },
  watch: {
    async isOpen(newVal) {
      if (newVal) {
        await this.loadCurrentProfile();
      }
    }
  },
  methods: {
    async loadCurrentProfile() {
      try {
        const user = this.authStore.user;
        if (!user) return;

        // 1. 공통 코드 로드
        const jobRoleRes = await axios.get('/api/core/commons/?top_code=JOB_ROLE');
        this.jobRolesOptions = jobRoleRes.data.map(item => ({
          value: item.code_id,
          label: item.code_name
        }));

        const interestsRes = await axios.get('/api/core/commons/?top_code=IT_INTEREST');
        this.interestsOptions = interestsRes.data.map(item => ({
          value: item.code_id,
          label: item.code_name
        }));

        // 2. 현재 프로필 정보 매핑
        this.nickname = user.nickname || user.user_nickname;
        this.email = user.email;
        this.avatarPreviewUrl = user.active_avatar?.image_url;
        this.avatarStyle = user.active_avatar?.prompt || '';
        // [수정일: 2026-02-07] 기존 시드 로드 (Antigravity)
        if (user.active_avatar?.seed) {
           this.avatarSeed = user.active_avatar.seed;
        }
        
        if (user.user_detail) {
           this.jobRole = user.user_detail.job_role || [];
           this.interests = user.user_detail.interests || [];
        }
      } catch (error) {
        console.error('Failed to load profile:', error);
      }
    },

    async previewAvatar() {
      if (!this.avatarStyle.trim()) return;
      this.isPreviewing = true;
      try {
        // [수정일: 2026-02-07] 새로운 변형을 위해 시드 갱신 (Antigravity)
        this.avatarSeed = Math.floor(Math.random() * 1000000);
        
        const response = await axios.post('/api/core/activity/preview/', {
          prompt: this.avatarStyle,
          seed: this.avatarSeed
        });
        if (response.data.fallback) {
          console.warn('AI Avatar Generation Fallback:', response.data.error_msg);
          alert('💡 현재 AI 아바타 생성 서버가 혼잡하여 기본 오리로 대체되었습니다. 잠시 후 다시 시도해 주세요!');
        }
        this.avatarPreviewUrl = response.data.url + '?t=' + new Date().getTime();
      } catch (error) {
        console.error('Failed to preview avatar:', error);
      } finally {
        this.isPreviewing = false;
      }
    },

    async updateProfile() {
      this.isSubmitting = true;
      try {
        const formData = {
          user_nickname: this.nickname,
          user_detail: {
            job_role: this.jobRole,
            interests: this.interests,
            avatar_style: this.avatarStyle,
            avatar_seed: this.avatarSeed,
            avatar_preview_url: this.avatarPreviewUrl // [수정일: 2026-02-07] 미리보기 이미지 확정 채택 (Antigravity)
          }
        };
        
        if (this.password) {
          formData.password = this.password;
        }

        const response = await axios.patch(`/api/core/users/${this.authStore.user.id}/`, formData);
        
        if (response.status === 200) {
          alert('정보가 성공적으로 수정되었습니다! ✨');
          await this.authStore.checkSession(); // 스토어 정보 갱신
          this.$emit('close');
        }
      } catch (error) {
        console.error('Update Failed:', error);
        const errorMsg = error.response?.data?.detail || 
                        JSON.stringify(error.response?.data) || 
                        '정보 수정 중 오류가 발생했습니다.';
        alert(`❌ 수정 실패: ${errorMsg}`);
      } finally {
        this.isSubmitting = false;
      }
    }
  }
}
</script>

<style scoped src="./ProfileSettingsModal.css"></style>
