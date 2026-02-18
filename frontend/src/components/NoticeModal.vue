<!-- 
  역할: 시스템 공지사항 및 보안 알림을 표시하는 팝업 모달 컴포넌트
  수정일: 2026-01-20
  수정내용: 공지사항 모달 컴포넌트 분리 (App.vue에서 분리됨)
-->
<template>
  <transition name="fade">
    <div v-if="isOpen" class="modal-overlay notice-overlay" @click.self="closeNotice">
      <div class="notice-container" style="font-family: var(--font-main);">
        <div class="notice-badge" style="background: var(--accent); font-family: var(--font-retro); font-size: 8px;">SECURITY</div>
        <h2 class="notice-title" style="font-weight: 800; letter-spacing: -0.02em;">AI-Arcade 보안 고도화 안내</h2>
        <div class="notice-body">
          <p style="line-height: 1.6;">안녕하세요, 엔지니어 여러분! 여러분의 훈련 데이터를 보호하기 위해 <strong>시스템 보안 체계</strong>가 강화되었습니다.</p>
          <ul class="notice-list">
            <li><i data-lucide="shield-check" class="notice-icon"></i> 미인증 사용자 콘텐츠 접근 제한 시스템 도입</li>
            <li><i data-lucide="lock" class="notice-icon"></i> 로그인 및 세션 관리 보안 프로토콜 강화</li>
            <li><i data-lucide="bell" class="notice-icon"></i> 부적절한 접근 시도시 실시간 보안 알림 가동</li>
          </ul>
          <p class="notice-footer-text" style="font-weight: 600;">더욱 안전하고 쾌적한 환경에서 <strong>최고의 아키텍처</strong>를 설계해 보세요!</p>
        </div>
        <div class="notice-actions">
          <button class="btn btn-primary" @click="closeNotice" style="width: 100%; font-weight: 700;">보안 지침 확인 및 훈련하기</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: "NoticeModal",
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
  },
  emits: ["close"],
  methods: {
    closeNotice() {
      this.$emit("close");
    },
  },
  // [수정: 2026-01-20]
  // 컴포넌트가 DOM에 마운트된 직후 실행됩니다.
  // 페이지 로드 시점에 모달이 이미 열려있는 경우(isOpen=true), Lucide 아이콘을 즉시 변환하여 렌더링합니다.
  mounted() {
    if (this.isOpen) {
        this.$nextTick(() => {
            if (window.lucide) window.lucide.createIcons();
        });
    }
  },
  watch: {
    // [수정: 2026-01-20]
    // isOpen 속성의 변화를 감지합니다.
    // 모달이 닫혀있다가 열리는 순간(newVal=true)을 포착하여,
    // DOM이 업데이트된 후($nextTick) 아이콘을 다시 그려(createIcons) 화면에 표시되게 합니다.
    isOpen(newVal) {
      if (newVal) {
        this.$nextTick(() => {
            if (window.lucide) window.lucide.createIcons();
        });
      }
    }
  }
};
</script>

<style scoped>
/* Notice Popup Styles copied from style.css for scoping or assumed global */
/* Assuming global style.css handles the classes, but we can verify dependencies */
</style>
