import { ref } from 'vue';

export function useIntro(defaultLines = []) {
  const showIntro = ref(true);
  const introLines = ref(defaultLines);
  const introIndex = ref(0);
  const displayedIntroText = ref('');
  const duckAppeared = ref(false);
  const showStartBtn = ref(false);
  const introTypingInterval = ref(null);
  const introIsTyping = ref(false);
  const currentIntroFullText = ref('');

  function typeIntroText(text) {
    displayedIntroText.value = '';
    currentIntroFullText.value = text;
    introIsTyping.value = true;
    let i = 0;

    clearInterval(introTypingInterval.value);
    introTypingInterval.value = setInterval(() => {
      if (i < text.length) {
        displayedIntroText.value += text.charAt(i);
        i++;
      } else {
        finishIntroTyping();
      }
    }, 30);
  }

  function finishIntroTyping() {
    clearInterval(introTypingInterval.value);
    displayedIntroText.value = currentIntroFullText.value;
    introIsTyping.value = false;
  }

  function nextIntroLine() {
    if (introIsTyping.value) {
      finishIntroTyping();
      return;
    }

    introIndex.value++;
    if (introIndex.value < introLines.value.length) {
      typeIntroText(introLines.value[introIndex.value]);
    } else {
      showStartBtn.value = true;
    }
  }

  function enterGame() {
    showIntro.value = false;
  }

  function startIntroAnimation() {
    setTimeout(() => {
      duckAppeared.value = true;
      if (introLines.value.length > 0) {
        typeIntroText(introLines.value[0]);
      }
    }, 500);
  }

  function cleanup() {
    if (introTypingInterval.value) {
      clearInterval(introTypingInterval.value);
      introTypingInterval.value = null;
    }
  }

  return {
    showIntro,
    introLines,
    introIndex,
    displayedIntroText,
    duckAppeared,
    showStartBtn,
    introIsTyping,
    typeIntroText,
    finishIntroTyping,
    nextIntroLine,
    enterGame,
    startIntroAnimation,
    cleanup
  };
}
