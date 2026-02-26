<!-- 
  역할: 시스템 공지사항 및 보안 알림을 표시하는 팝업 모달 컴포넌트
  수정일: 2026-01-20
  수정내용: 공지사항 모달 컴포넌트 분리 (App.vue에서 분리됨)
  수정일: 2026-02-26
  수정내용: Coduck Wars, AI-Coach 등 최신 업데이트 내용을 반영하여 공지 내용 및 UI 텍스트(UPDATE 테마) 변경
-->
<template>
  <transition name="fade">
    <div v-if="isOpen" class="modal-overlay notice-overlay" @click.self="closeNotice">
      <div class="notice-container" style="font-family: var(--font-main);">
        <div class="notice-badge" style="background: var(--accent); font-family: var(--font-retro); font-size: 8px;">UPDATE</div>
        <h2 class="notice-title" style="font-weight: 800; letter-spacing: -0.02em;">AI-Arcade 대규모 업데이트 안내</h2>
        <div class="notice-body">
          <p style="line-height: 1.6;">안녕하세요, 시스템 엔지니어 여러분! AI-Arcade에 새로운 훈련 모드와 강력한 기능들이 대거 업데이트 되었습니다.</p>
          <ul class="notice-list">
            <li><i data-lucide="gamepad-2" class="notice-icon"></i> <strong>Team Battle 미니게임 모드</strong> (로직 런, 아키텍처 배틀 등) 정식 오픈</li>
            <li><i data-lucide="bot" class="notice-icon"></i> <strong>AI-Coach 및 압박 면접 시뮬레이션</strong> 시스템 고도화 (비전 분석 탑재)</li>
            <li><i data-lucide="layers" class="notice-icon"></i> 실전형 <strong>시스템 아키텍처</strong> 및 의사코드 훈련 퀘스트 확장</li>
          </ul>
          <p class="notice-footer-text" style="font-weight: 600;">지금 바로 새롭게 추가된 기능들을 활용하여 <strong>최고의 엔지니어</strong>에 도전해보세요!</p>
        </div>
        <div class="notice-actions">
          <button class="btn btn-primary" @click="closeNotice" style="width: 100%; font-weight: 700;">새로운 기능 체험하기</button>
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
