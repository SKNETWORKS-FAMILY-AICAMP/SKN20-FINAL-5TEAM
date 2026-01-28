import { ref } from 'vue';

export function useHint() {
  const isHintActive = ref(false);
  const hintTimeoutId = ref(null);

  function toggleHint(showToastFn, expectedComponents = []) {
    isHintActive.value = !isHintActive.value;

    // 이전 타이머 클리어
    if (hintTimeoutId.value) {
      clearTimeout(hintTimeoutId.value);
      hintTimeoutId.value = null;
    }

    // 힌트 활성화 시 토스트 메시지 + 5초 후 자동 해제
    if (isHintActive.value) {
      const requiredCount = expectedComponents.length || 0;
      if (showToastFn) {
        showToastFn(
          `💡 힌트 활성화! 오른쪽 팔레트에서 노란색으로 빛나는 ${requiredCount}개의 필수 컴포넌트를 확인해. 5초 후 자동 해제. 꽥!`,
          'hint'
        );
      }

      hintTimeoutId.value = setTimeout(() => {
        isHintActive.value = false;
        hintTimeoutId.value = null;
      }, 5000);
    }
  }

  function cleanup() {
    if (hintTimeoutId.value) {
      clearTimeout(hintTimeoutId.value);
      hintTimeoutId.value = null;
    }
  }

  return {
    isHintActive,
    toggleHint,
    cleanup
  };
}
