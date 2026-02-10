<!--
  역할: 신규 회원가입을 처리하는 모달 컴포넌트
  기능: 닉네임, 이메일, 비밀번호, 직군(다중선택), 관심사(다중선택) 수집 및 백엔드 API 전송. 가입 성공 시 축하 메시지 표시.
-->
<template>
  <transition name="fade">
    <div v-if="isOpen" class="modal-overlay">
      <div class="auth-container">
        <template v-if="!isSuccess">
          <header class="auth-header">
            <div class="auth-badge">ANTIGRAVITY SYSTEM</div>
            <h2 class="auth-title">Become an Engineer</h2>
            <p class="auth-subtitle">아키텍처 훈련센터의 정식 요원으로 등록하세요.</p>
          </header>
          
          <form @submit.prevent="completeSignUp">
            <div class="auth-body">
              <div class="input-group">
                <label class="input-label">ENGINEER CALLSIGN <span class="required-mark">*</span></label>
                <input type="text" v-model="nickname" class="auth-input" placeholder="당신의 호출명을 입력하세요 (Ex. Nova)">
              </div>
              <div class="input-group">
                <label class="input-label">ENGINEERING ID (EMAIL) <span class="required-mark">*</span></label>
                <input type="email" v-model="email" class="auth-input" placeholder="이메일을 입력하세요">
              </div>
              <div class="input-group">
                <label class="input-label">ACCESS SECRET <span class="required-mark">*</span></label>
                <input type="password" v-model="password" class="auth-input" placeholder="비밀번호 (8자 이상)">
              </div>

              <!-- [NEW] 아바타 선택 및 미리보기 섹션 -->
              <div class="input-group avatar-custom-section" style="margin-top: 1.5rem; padding: 1rem; background: rgba(182, 255, 64, 0.05); border-radius: 12px; border: 1px dashed rgba(182, 255, 64, 0.3);">
                <label class="input-label" style="color: #b6ff40; display: flex; align-items: center; gap: 8px;">
                   <i data-lucide="sparkles" style="width: 16px;"></i> NANO-BANANA AVATAR DESIGN
                </label>
                <div style="display: flex; gap: 1rem; margin-top: 0.8rem;">
                  <div style="flex: 2;">
                    <input type="text" v-model="avatarStyle" class="auth-input" placeholder="원하는 스타일 입력 (Ex. Cyberpunk Duck)" @keydown.enter.prevent="previewAvatar" style="border-color: rgba(182, 255, 64, 0.4);">
                    <p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.4rem;">💡 스타일 입력 후 <b>엔터(Enter)</b>를 치거나 우측 버튼을 누르세요.</p>
                  </div>
                  <button type="button" class="btn btn-primary" @click="previewAvatar" :disabled="isPreviewing" style="width: 100px; height: 48px; min-height: 48px; font-weight: 800; letter-spacing: 0.5px; box-shadow: 0 0 10px rgba(182, 255, 64, 0.2); font-size: 0.85rem; border-radius: 8px !important; flex: none; display: flex; align-items: center; justify-content: center; padding: 0 !important;">
                    {{ isPreviewing ? '...' : 'CREATE' }}
                  </button>
                </div>
                
                <div class="avatar-preview-display" style="margin-top: 1rem; display: flex; justify-content: center;">
                  <AvatarFrame 
                    v-if="avatarPreviewUrl" 
                    :src="avatarPreviewUrl" 
                    rank="BRONZE" 
                    size="220px" 
                    class="preview-card"
                  />
                  <div v-else class="preview-placeholder" style="width: 220px; height: 220px; background: rgba(255,255,255,0.05); border-radius: 20px; border: 2px dashed rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 0.9rem; text-align: center; padding: 10px;">
                    스타일을 입력하고<br>미리보기 해보세요!
                  </div>
                </div>
              </div>

              <!-- 추가 정보 섹션 -->
              <div class="input-row" style="display: flex; gap: 1rem; margin-bottom: 1rem;">
                <!-- ... 생략 (기존 내용 유지) ... -->
                <div class="input-group" style="flex: 1;">
                  <label class="input-label">BIRTH DATE</label>
                  <input type="date" v-model="birthDate" class="auth-input date-input" :max="today">
                </div>
                <div class="input-group" style="flex: 1;">
                  <label class="input-label">DEVELOPER STATUS</label>
                  <div class="toggle-group" style="display: flex; background: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 4px;">
                    <label class="toggle-choice" style="flex: 1; text-align: center; cursor: pointer; padding: 6px; border-radius: 6px;" :style="isDeveloper ? 'background: var(--primary); color: white;' : 'color: var(--text-muted);'">
                      <input type="radio" :value="true" v-model="isDeveloper" style="display: none;">
                      <span>Yes</span>
                    </label>
                    <label class="toggle-choice" style="flex: 1; text-align: center; cursor: pointer; padding: 6px; border-radius: 6px;" :style="!isDeveloper ? 'background: var(--primary); color: white;' : 'color: var(--text-muted);'">
                      <input type="radio" :value="false" v-model="isDeveloper" style="display: none;">
                      <span>No</span>
                    </label>
                  </div>
                </div>
              </div>

              <transition name="fade">
                <div class="input-group" v-if="isDeveloper">
                  <label class="input-label">JOB ROLE (Multiple Select)</label>
                  <div class="checkbox-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;">
                    <label v-for="role in jobRolesOptions" :key="role.value" class="checkbox-item" style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                      <input type="checkbox" :value="role.value" v-model="jobRole" style="accent-color: var(--primary);">
                      <span style="font-size: 0.9rem; color: #cbd5e1;">{{ role.label }}</span>
                    </label>
                  </div>

                  <div class="input-group" style="margin-top: 1rem;">
                      <label class="input-label">IT INTERESTS</label>
                      <div class="interest-chips" style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                          <label v-for="tag in interestsOptions" :key="tag.value" class="chip" style="cursor: pointer; padding: 5px 10px; border-radius: 20px; background: rgba(255,255,255,0.1); display: flex; align-items: center; gap: 5px; transition: all 0.2s;" :style="interests.includes(tag.value) ? 'background: var(--primary); color: #000;' : ''">
                              <input type="checkbox" :value="tag.value" v-model="interests" style="display: none;">
                              <span>{{ tag.label }}</span>
                          </label>
                          <div class="custom-interest-input-wrapper">
                              <input type="text" v-model="customInterest" @keyup.enter="addCustomInterest"
                                  placeholder="+ 직접 입력" class="auth-input custom-interest-input" style="padding: 5px 10px; border-radius: 20px; font-size: 0.9rem; width: 100px;">
                          </div>
                      </div>
                  </div>
                </div>
              </transition>
            </div>
            
            <footer class="auth-footer">
              <button type="button" class="btn btn-secondary" @click="$emit('close')" style="flex: 1;">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="isSubmitting" style="flex: 2;">
                {{ isSubmitting ? 'Registering...' : '훈련 참가하기' }}
              </button>
            </footer>
          </form>
        </template>

        <!-- 성공 화면 (v-else) -->
        <template v-else>
          <div class="auth-body" style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem; animation: bounce 1s infinite;">🎉</div>
            <h2 class="auth-title" style="margin-bottom: 1rem; color: #b6ff40;">Welcome aboard!</h2>
            <p class="auth-subtitle" style="margin-bottom: 2rem;">
              축하합니다, <strong>{{ nickname }}</strong> 엔지니어님!<br>
              아키텍처 훈련센터 등록이 완료되었습니다.
            </p>
            <button class="btn btn-primary" @click="closeAndLogin" style="width: 100%; padding: 1rem;">
              로그인하러 가기
            </button>
          </div>
        </template>
      </div>
    </div>
  </transition>
</template>

<script>
import axios from 'axios'; // 2024-05-23: 서버와 데이터를 주고받기 위한 Promise 기반의 HTTP 클라이언트 라이브러리입니다.
import { useAuthStore } from '@/stores/auth'; // [수정일: 2026-02-07] 자동 로그인 상태 갱신용
import AvatarFrame from '@/components/AvatarFrame.vue';

export default {
  name: 'SignUpModal',
  components: { AvatarFrame },
  props: {
    isOpen: {
      type: Boolean,
      required: true
    }
  },
  setup() {
    const authStore = useAuthStore();
    return { authStore };
  },
  data() {
    return {
      nickname: '',
      email: '',
      password: '',
      birthDate: '',
      isDeveloper: true,
      jobRole: [], 
      jobRolesOptions: [],
      interests: [], // 선택된 관심사
      interestsOptions: [], // API로 로드된 관심사 목록
      customInterest: '', // 직접 입력 텍스트
      isSubmitting: false,
      isSuccess: false,
      // [수정일: 2026-02-06] 아바타 커스텀 상태
      avatarStyle: 'default duck',
      avatarPreviewUrl: null,
      isPreviewing: false,
      avatarSeed: Math.floor(Math.random() * 100000),
      // [수정일: 2026-02-07] 오늘 날짜 (미래 날짜 선택 방지용)
      today: new Date().toISOString().split('T')[0]
    }
  },
  watch: {
    isOpen(newVal) {
      if (newVal) {
        // [수정일: 2026-01-20] 모달 열릴 때 상태 초기화 및 공통 코드 조회
        this.nickname = '';
        this.email = '';
        this.password = '';
        this.birthDate = '';
        this.isDeveloper = true;
        this.jobRole = [];
        this.interests = [];
        this.customInterest = '';
        this.isSuccess = false;
        // [수정일: 2026-02-06] 아바타 상태 초기화
        this.avatarStyle = 'default duck';
        this.avatarPreviewUrl = null;
        this.avatarSeed = Math.floor(Math.random() * 100000);
        
        this.fetchCommonCodes();
      }
    }
  },
  methods: {
    async fetchCommonCodes() {
      try {
        // 병렬로 API 호출
        const [jobRoleRes, interestRes] = await Promise.all([
          axios.get('/api/core/commons/?top_code=JOB_ROLE'),
          axios.get('/api/core/commons/?top_code=IT_INTEREST')
        ]);
        
        this.jobRolesOptions = jobRoleRes.data.map(item => ({
          value: item.code_id,
          label: item.code_name
        }));
        
        this.interestsOptions = interestRes.data.map(item => ({
          value: item.code_id,
          label: item.code_name
        }));
        
      } catch (error) {
        console.error('Failed to fetch common codes:', error);
      }
    },
    
    // 관심사 직접 입력 추가
    addCustomInterest() {
        if(this.customInterest.trim()) {
            // 이미 있는지 확인 (선택적)
            const val = this.customInterest.trim();
            // 임시로 value와 label을 동일하게 추가 (저장은 텍스트로 되거나 백엔드 처리에 따라 다름)
            // 여기서는 선택된 배열에 단순 문자열로 추가하는 방식을 씁니다.
            // 하지만 UI가 value/label 객체 기반이므로, options에 없는 값이 들어오면 처리가 복잡할 수 있습니다.
            // index copy.html 처럼 단순히 문자열 태그라면 쉽습니다.
            // 여기서는 interestsOptions에 없는 값도 interests 배열에 넣을 수 있다고 가정합니다.
            // 다만 Checkbox UI이므로 options에 추가해줘야 체크된 상태로 보입니다.
            
            // 중복 체크
            if (!this.interestsOptions.find(opt => opt.value === val)) {
                this.interestsOptions.push({ value: val, label: val });
            }
            if (!this.interests.includes(val)) {
                this.interests.push(val);
            }
            this.customInterest = '';
        }
    },
    
    async previewAvatar() {
      if (!this.avatarStyle.trim()) return;
      this.isPreviewing = true;
      try {
        const response = await axios.post('/api/core/activity/preview/', {
          prompt: this.avatarStyle,
          seed: this.avatarSeed
        });
        if (response.data.fallback) {
          console.warn('AI Avatar Generation Fallback:', response.data.error_msg);
          alert('💡 현재 AI 아바타 생성 서버가 혼잡하여 기본 오리로 대체되었습니다. 나중에 다시 시도해 주세요!');
        }
        this.avatarPreviewUrl = response.data.url + '?t=' + new Date().getTime();
      } catch (error) {
        console.error('Failed to preview avatar:', error);
        alert('아바타 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.');
      } finally {
        this.isPreviewing = false;
      }
    },

    // [수정일: 2026-01-20] 성공 화면에서 '로그인하러 가기' 클릭 시 처리
    closeAndLogin() {
      this.$emit('signup-success', this.nickname); // 부모 컴포넌트에 알림
      this.$emit('close'); // 모달 닫기
    },

    async completeSignUp() {
      // Basic validation
      if (!this.nickname || !this.email || !this.password) {
        alert('닉네임, 이메일, 비밀번호는 필수 입력 항목입니다.');
        return;
      }
      
      this.isSubmitting = true;
      
      // 1. 데이터 구성
      const formData = {
        user_nickname: this.nickname,
        user_name: this.nickname, // 이름은 닉네임으로 대체 (필요 시 별도 입력 필드 추가)
        username: this.email.split('@')[0], // [수정일: 2026-02-07] id 대신 username 필드 사용
        email: this.email,
        password: this.password,
        birth_date: this.birthDate || null,
        user_detail: {
          is_developer: this.isDeveloper,
          job_role: this.jobRole || null,
          interests: this.interests || null, // 관심사 추가
          avatar_style: this.avatarStyle,    // [수정일: 2026-02-06] 아바타 스타일 추가
          avatar_seed: this.avatarSeed,      // [수정일: 2026-02-06] 아바타 시드 추가
          avatar_preview_url: this.avatarPreviewUrl // [수정일: 2026-02-08] 미리보기 URL 추가하여 저장 시 일관성 유지 (Antigravity)
        }
      };

      // [수정일: 2026-01-20] axios를 사용한 백엔드 API 연동
      try {
        // 2. API 전송 (POST 요청)
        // 백엔드의 UserProfileViewSet.create 메서드 호출
        const response = await axios.post('/api/core/users/', formData);
        
        // 3. 성공 처리 (HTTP 201 Created)
        if (response.status === 201) {
          // [수정일: 2026-02-07] 회원가입 후 자동 로그인 세션 갱신
          await this.authStore.checkSession();
          this.isSuccess = true; // 성공 화면으로 전환
        }
      } catch (error) {
        // 4. 에러 처리
        console.error('Signup Error:', error);
        
        // 서버에서 반환한 구체적인 에러 메시지가 있는 경우 (예: 아이디 중복 등)
        if (error.response && error.response.data) {
          // [수정일: 2026-01-21] 에러 메시지를 alert 대신 UI에 표시하거나 더 예쁘게 처리
          // 특히 "email" 필드에 대한 에러(중복 등)를 체크
          const errorData = error.response.data;
          
          if (errorData.email || errorData.detail) {
             const msg = (errorData.email && errorData.email[0]) || errorData.detail;
             alert('⚠️ ' + msg); // 일단 alert로 하되 이모지 추가 (요청: 이미 존재한다는 메시지를 예쁘게)
             // 추후 토스트 메시지나 인라인 에러 텍스트로 고도화 가능
          } else {
             alert('회원가입 실패: ' + JSON.stringify(errorData));
          }
        } else {
          alert('서버 통신 중 오류가 발생했습니다.');
        }
      } finally {
        // 성공/실패 여부와 상관없이 로딩 상태 해제
        this.isSubmitting = false;
      }
    }
  }
}
</script>

<style scoped src="./SignUpModal.css"></style>
