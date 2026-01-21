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
          
          <div class="auth-body">
            <div class="input-group">
              <label class="input-label">ENGINEER CALLSIGN</label>
              <input type="text" v-model="nickname" class="auth-input" placeholder="당신의 호출명을 입력하세요 (Ex. Nova)">
            </div>
            <div class="input-group">
              <label class="input-label">ENGINEERING ID (EMAIL)</label>
              <input type="email" v-model="email" class="auth-input" placeholder="이메일을 입력하세요">
            </div>
            <div class="input-group">
              <label class="input-label">ACCESS SECRET</label>
              <input type="password" v-model="password" class="auth-input" placeholder="비밀번호 (8자 이상)">
            </div>

            <!-- 추가 정보 섹션 -->
            <div class="input-row" style="display: flex; gap: 1rem; margin-bottom: 1rem;">
              <div class="input-group" style="flex: 1;">
                <label class="input-label">BIRTH DATE</label>
                <input type="date" v-model="birthDate" class="auth-input date-input">
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

                <!-- IT INTERESTS 추가 -->
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
            <button class="btn btn-secondary" @click="$emit('close')" style="flex: 1;">Cancel</button>
            <button class="btn btn-primary" @click="completeSignUp" :disabled="isSubmitting" style="flex: 2;">
              {{ isSubmitting ? 'Registering...' : '훈련 참가하기' }}
            </button>
          </footer>
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

export default {
  name: 'SignUpModal',
  props: {
    isOpen: {
      type: Boolean,
      required: true
    }
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
      isSuccess: false
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
        user_id: this.email,      // 이메일을 ID로 사용
        email: this.email,
        password: this.password,
        birth_date: this.birthDate || null,
        user_detail: {
          is_developer: this.isDeveloper,
          job_role: this.jobRole || null,
          interests: this.interests || null // 관심사 추가
        }
      };

      // [수정일: 2026-01-20] axios를 사용한 백엔드 API 연동
      try {
        // 2. API 전송 (POST 요청)
        // 백엔드의 UserProfileViewSet.create 메서드 호출
        const response = await axios.post('/api/core/users/', formData);
        
        // 3. 성공 처리 (HTTP 201 Created)
        if (response.status === 201) {
          // alert('회원가입이 완료되었습니다! 로그인해주세요.'); // 기존 alert 제거
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

<style scoped>
/* Inherits global styles from style.css */
</style>
