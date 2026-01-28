import { ref } from 'vue';

export function useToast() {
  const showToast = ref(false);
  const toastMessage = ref('');
  const toastType = ref('guide'); // 'guide', 'connect', 'place', 'hint'
  const toastTimeoutId = ref(null);

  function showToastMessage(message, type = 'guide', duration = 0) {
    // 이전 타이머 클리어
    if (toastTimeoutId.value) {
      clearTimeout(toastTimeoutId.value);
      toastTimeoutId.value = null;
    }

    toastMessage.value = message;
    toastType.value = type;
    showToast.value = true;

    // duration이 지정되면 자동 해제
    if (duration > 0) {
      toastTimeoutId.value = setTimeout(() => {
        dismissToast();
      }, duration);
    }
  }

  function dismissToast() {
    showToast.value = false;
    if (toastTimeoutId.value) {
      clearTimeout(toastTimeoutId.value);
      toastTimeoutId.value = null;
    }
  }

  function cleanup() {
    if (toastTimeoutId.value) {
      clearTimeout(toastTimeoutId.value);
      toastTimeoutId.value = null;
    }
  }

  return {
    showToast,
    toastMessage,
    toastType,
    showToastMessage,
    dismissToast,
    cleanup
  };
}
