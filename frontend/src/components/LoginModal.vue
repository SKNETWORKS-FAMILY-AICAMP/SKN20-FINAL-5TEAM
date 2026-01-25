<!--
  역할: 사용자 로그인을 처리하는 모달 컴포넌트
  기능: 이메일/비밀번호 입력, 로그인 요청(백엔드 연동 예정), 회원가입 모달 전환 이벤트(request-signup) 발생
-->
<template>
  <transition name="fade">
    <div v-if="isOpen" class="modal-overlay">
      <div class="auth-container">
        <header class="auth-header">
          <div class="auth-badge">ANTIGRAVITY LOGIN</div>
          <h2 class="auth-title">Welcome Back</h2>
          <p class="auth-subtitle">엔지니어 신원 확인을 위해 접속 보안 코드를 입력하세요.</p>
        </header>

        <div class="auth-body">
          <div class="input-group">
            <label class="input-label">ENGINEERING ID</label>
            <input type="email" v-model="email" class="auth-input" placeholder="이메일을 입력하세요" 
              @keyup.enter="handleLogin">
          </div>
          <div class="input-group">
            <label class="input-label">ACCESS SECRET</label>
            <input type="password" v-model="password" class="auth-input" placeholder="비밀번호" 
              @keyup.enter="handleLogin">
          </div>
        </div>

        <footer class="auth-footer" style="flex-direction: column; gap: 0.5rem; border-top: none; padding-top: 0; margin-top: 2rem;">
          <button class="btn btn-primary" @click="handleLogin" :disabled="isSubmitting" style="width: 100%;">
            {{ isSubmitting ? 'Verifying...' : '승인 요청' }}
          </button>
          <div style="text-align: center; margin-top: 1rem;">
            <span style="color: var(--text-muted); font-size: 0.85rem;">New here? </span>
            <a href="javascript:void(0)" @click="$emit('request-signup')"
              style="color: var(--primary); font-size: 0.85rem; font-weight: 700; text-decoration: none;">Register Now</a>
          </div>
          <button class="btn btn-secondary" @click="$emit('close')"
            style="width: 100%; border: none; background: transparent; color: #64748b;">Cancel</button>
        </footer>
      </div>
    </div>
  </transition>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LoginModal',
  props: {
    isOpen: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      email: '',
      password: '',
      isSubmitting: false
    }
  },
  watch: {
    isOpen(newVal) {
      if (newVal) {
        this.email = '';
        this.password = '';
      }
    }
  },
  methods: {
    /**
     * [로그인 처리 핸들러]
     * - [수정일: 2026-01-25] 직접적인 Axios 호출 대신 auth store의 login 액션을 사용하도록 개선.
     * - 중앙 집중화된 에러 처리 및 상태 관리를 통해 코드 안정성을 높였습니다.
     */
    async handleLogin() {
      // 1. 유효성 검사
      if (!this.email || !this.password) {
        alert('이메일과 비밀번호를 입력해주세요.');
        return;
      }
      
      this.isSubmitting = true;
      
      try {
        // 2. Pinia Store의 login 액션 호출
        const auth = useAuthStore();
        const result = await auth.login(this.email, this.password);
        
        if (result.success) {
          // 3. 성공 시 모달 닫기 요청 및 성공 이벤트 발생 (부모 컴포넌트 연동)
          this.$emit('login-success'); // 2026-01-25: 스토어 상태는 이미 반영됨
          this.$emit('close');
        } else {
          // 4. 실패 시 서버 에러 메시지 표시
          alert(result.error);
        }
      } catch (error) {
        console.error('Login Handler Error:', error);
        alert('예기치 못한 오류가 발생했습니다.');
      } finally {
        this.isSubmitting = false;
      }
    }
  }
}
</script>

<script setup>
// [2026-01-25] 스토어 접근을 위한 setup script block (또는 메서드 내 setup 패턴)
import { useAuthStore } from '@/stores/auth';
</script>

<style scoped>
/* Inherits global styles from style.css */
</style>
