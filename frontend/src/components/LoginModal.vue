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
    async handleLogin() {
      // Basic validation
      if (!this.email || !this.password) {
        alert('이메일과 비밀번호를 입력해주세요.');
        return;
      }
      
      this.isSubmitting = true;
      
      try {
        // [수정일: 2026-01-21] 백엔드 로그인 API 호출
        const response = await axios.post('/api/core/auth/login/', {
          email: this.email,
          password: this.password
        });
        
        if (response.status === 200) {
          // 로그인 성공 시 사용자 정보와 함께 이벤트 발생
          this.$emit('login-success', response.data.user);
        }
      } catch (error) {
        console.error('Login Error:', error);
        if (error.response && error.response.data && error.response.data.error) {
           alert(error.response.data.error);
        } else {
           alert('로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.');
        }
      } finally {
        this.isSubmitting = false;
      }
    }
  }
}
</script>

<style scoped>
/* Inherits global styles from style.css */
</style>
