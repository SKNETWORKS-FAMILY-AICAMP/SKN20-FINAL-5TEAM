<script setup>
/**
 * 수정일: 2026-01-29
 * 내용: 비상 대응 시스템 (Pseudo Emergency) 한국어 번역 및 데이터 보강
 */
import { ref, computed, onMounted } from 'vue';
import { useGameStore } from '@/stores/game';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';

const emit = defineEmits(['close']);
const game = useGameStore();

// --- 상태 변수 (State) ---
const gameStarted = ref(false);
const currentIdx = ref(0);
const editorContent = ref('');
const displayedDialogue = ref('');
const isStageClear = ref(false);
const isGameFinished = ref(false);

// 타이핑 효과를 위한 인터벌 저장 변수
let typingInterval = null;

// --- 상수 데이터 (Constants) ---
const RAW_STAGES = [
    {
        title: "긴급 차단 스위치 (Emergency Kill-switch)",
        fnName: "emergency_stop",
        params: "status",
        goal: "시스템 상태(status)가 'CRITICAL'일 때 즉시 중단(True) 신호를 반환하십시오.",
        evalType: "killswitch",
        testCases: [
            { i: "CRITICAL", e: true },
            { i: "NORMAL", e: false },
            { i: "WARNING", e: false }
        ],
        hints: ["문자열 'CRITICAL'과 정확히 일치해야 합니다.", "비교 연산자(==)를 사용하여 상태를 확인하십시오."]
    }
];

const EVALUATORS = {
    killswitch: (c, val) => {
        // 공백 제거 후 핵심 로직 포함 여부 확인
        const code = c.replace(/\s/g, "");
        if (code.includes("status=='CRITICAL'") || code.includes('status=="CRITICAL"')) {
            return val === "CRITICAL";
        }
        return null;
    }
};

// --- 계산된 속성 (Computed) ---
const currentStage = computed(() => RAW_STAGES[currentIdx.value] || {});

const stageBadge = computed(() => {
    return isGameFinished.value ? '완료' : `비상 대응 #${currentIdx.value + 1}`;
});

// Monaco Editor 옵션
const editorOptions = {
    minimap: { enabled: false },
    fontSize: 16,
    lineHeight: 24,
    fontFamily: "'Fira Code', 'Consolas', monospace",
    theme: 'vs-dark',
    renderLineHighlight: 'all',
    scrollBeyondLastLine: false,
    automaticLayout: true,
};

// --- 메소드 (Methods) ---
const typeDialogue = (text) => {
    if (typingInterval) clearInterval(typingInterval);
    displayedDialogue.value = "";
    let i = 0;
    typingInterval = setInterval(() => {
        if (i < text.length) {
            displayedDialogue.value += text[i++];
        } else {
            clearInterval(typingInterval);
        }
    }, 20);
};

const loadStage = (idx) => {
    if (idx >= RAW_STAGES.length) {
        isGameFinished.value = true;
        typeDialogue("모든 비상 대응 훈련 세션을 성공적으로 마쳤습니다. 시스템이 이제 안전한 상태입니다.");
        return;
    }

    currentIdx.value = idx;
    isStageClear.value = false;
    
    const stage = RAW_STAGES[idx];
    editorContent.value = `def ${stage.fnName}(${stage.params}):\n    # TODO: 비상 대응 로직을 여기에 구현하십시오\n    `;
    typeDialogue("긴급 상황 발생! 즉시 대응 로직을 작성하여 시스템 셧다운을 방지해야 합니다.");
};

const startGame = () => {
    gameStarted.value = true;
    loadStage(0);
};

const runCode = () => {
    const stage = currentStage.value;
    const userCode = editorContent.value;
    const evalFunc = EVALUATORS[stage.evalType];
    const tests = stage.testCases;

    let passCount = 0;
    for (let i = 0; i < tests.length; i++) {
        const test = tests[i];
        if (evalFunc(userCode, test.i) === test.e) passCount++;
    }

    if (passCount === tests.length) {
        isStageClear.value = true;
        typeDialogue("축하합니다! 비상 상황이 해제되었고 시스템이 정상화되었습니다.");
        // 진행도 업데이트 (game store 연동 시 구현 가능)
        // game.unlockNextStage('Pseudo Emergency', currentIdx.value);
    } else {
        typeDialogue("검증 실패! 작성하신 로직에 오류가 있습니다. 시스템이 여전히 위험 상태입니다.");
    }
};

onMounted(() => {
    typeDialogue("의사 비상 대응(Pseudo Emergency) 훈련 센터에 오신 것을 환영합니다. 준비가 되셨다면 시작 버튼을 눌러주십시오.");
});

</script>

<template>
  <div class="pseudo-emergency-overlay">
    <div class="emergency-container">
      <!-- 닫기 버튼 -->
      <button @click="$emit('close')" class="btn-close" title="훈련 종료">
        &times;
      </button>

      <!-- 시작 화면 -->
      <div v-if="!gameStarted" class="start-overlay">
          <h1 class="title">의사 비상 대응</h1>
          <p class="subtitle">Pseudo Emergency</p>
          <p class="desc">시스템 긴급 장애 상황에서의 전술적 논리 대응 역량을 강화하십시오.</p>
          <button class="start-btn" @click="startGame">훈련 시작</button>
      </div>

      <!-- 메인 콘텐츠 -->
      <div v-else class="main-layout">
          <div class="sidebar">
              <div class="char-area">
                  <img src="/image/unit_duck.png" class="duck-img" alt="훈련 교관">
              </div>
              <div class="msg-box">
                  <div class="name-tag">훈련 교관 (Instructor)</div>
                  <div class="msg-text">{{ displayedDialogue }}</div>
              </div>
          </div>

          <div class="content">
              <div class="header">
                  <span class="badge">{{ stageBadge }}</span>
                  <h2 class="stage-title">{{ currentStage.title }}</h2>
              </div>

              <div class="problem-card">
                  <div class="goal-label">미션 목표:</div>
                  <div class="goal-text">{{ currentStage.goal }}</div>
                  
                  <div v-if="currentStage.hints" class="hint-section">
                      <div class="hint-label">힌트:</div>
                      <ul class="hint-list">
                          <li v-for="(hint, hIdx) in currentStage.hints" :key="hIdx">{{ hint }}</li>
                      </ul>
                  </div>
              </div>

              <div class="editor-area">
                  <vue-monaco-editor
                    v-model:value="editorContent"
                    language="python"
                    :options="editorOptions"
                    class="monaco-editor"
                  />
              </div>

              <div class="footer-actions">
                  <button v-if="isStageClear" class="btn-finish" @click="$emit('close')">훈련 세션 종료</button>
                  <button v-else class="btn-verify" @click="runCode">코드 검증 요청</button>
              </div>
          </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pseudo-emergency-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(15px);
}

.emergency-container {
  width: 95vw;
  height: 90vh;
  background: #121212;
  border: 3px solid #ff3e3e;
  border-radius: 24px;
  position: relative;
  overflow: hidden;
  display: flex;
  box-shadow: 0 0 50px rgba(255, 62, 62, 0.3);
}

.btn-close {
  position: absolute;
  top: 25px;
  right: 25px;
  background: none;
  border: none;
  color: #666;
  font-size: 2.5rem;
  cursor: pointer;
  z-index: 100;
  transition: all 0.2s;
}
.btn-close:hover { color: #ff3e3e; transform: rotate(90deg); }

.start-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #121212;
  z-index: 50;
  text-align: center;
}

.title { 
    color: #ff3e3e; 
    font-size: 4rem; 
    margin-bottom: 5px; 
    font-family: 'Orbitron', sans-serif;
    text-shadow: 0 0 20px rgba(255, 62, 62, 0.5);
}
.subtitle { color: #888; font-size: 1.5rem; margin-bottom: 30px; letter-spacing: 5px; text-transform: uppercase; }
.desc { color: #aaa; margin-bottom: 50px; font-size: 1.2rem; max-width: 600px; line-height: 1.6; }
.start-btn { 
    padding: 18px 50px; 
    background: linear-gradient(135deg, #ff3e3e, #b31d1d);
    color: white; 
    border: none; 
    border-radius: 12px; 
    font-size: 1.4rem; 
    cursor: pointer;
    font-weight: 900;
    transition: all 0.3s;
    box-shadow: 0 10px 30px rgba(179, 29, 29, 0.5);
}
.start-btn:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(179, 29, 29, 0.7); }

.main-layout { display: flex; width: 100%; height: 100%; }

.sidebar { 
    width: 380px; 
    background: #1a1a1a; 
    border-right: 1px solid #333; 
    display: flex; 
    flex-direction: column;
    padding: 60px 30px;
}

.char-area { flex: 1; display: flex; justify-content: center; align-items: center; }
.duck-img { width: 240px; filter: drop-shadow(0 0 30px rgba(255, 62, 62, 0.4)); }

.msg-box { 
    background: #000; 
    padding: 25px; 
    border-radius: 16px; 
    border: 1px solid #ff3e3e; 
    min-height: 160px;
    position: relative;
    margin-top: 40px;
}
.name-tag {
    position: absolute;
    top: -15px;
    left: 20px;
    background: #ff3e3e;
    color: white;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 800;
}
.msg-text { color: #fff; line-height: 1.8; font-size: 1.05rem; word-break: keep-all; }

.content { flex: 1; display: flex; flex-direction: column; padding: 60px; gap: 30px; }

.header { display: flex; align-items: center; gap: 20px; border-bottom: 2px solid #222; padding-bottom: 25px; }
.badge { background: #ff3e3e; color: white; padding: 6px 18px; border-radius: 8px; font-weight: 900; font-size: 0.9rem; }
.stage-title { font-size: 1.8rem; margin: 0; color: white; font-weight: 800; }

.problem-card { background: #1a1a1a; padding: 30px; border-radius: 16px; border: 1px solid #333; }
.goal-label { color: #888; font-size: 0.9rem; margin-bottom: 10px; font-weight: 700; }
.goal-text { color: #ff3e3e; font-size: 1.3rem; font-weight: 800; line-height: 1.5; margin-bottom: 20px; }

.hint-section { border-top: 1px solid #333; padding-top: 15px; }
.hint-label { color: #666; font-size: 0.85rem; margin-bottom: 8px; font-weight: 700; }
.hint-list { list-style: none; padding: 0; margin: 0; }
.hint-list li { color: #888; font-size: 0.95rem; margin-bottom: 5px; position: relative; padding-left: 15px; }
.hint-list li::before { content: '•'; position: absolute; left: 0; color: #ff3e3e; }

.editor-area { flex: 1; border-radius: 16px; overflow: hidden; border: 1px solid #333; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
.monaco-editor { width: 100%; height: 100%; }

.footer-actions { display: flex; justify-content: flex-end; }
.btn-verify, .btn-finish { 
    padding: 16px 40px; 
    background: #ff3e3e; 
    color: white; 
    border: none; 
    border-radius: 12px; 
    cursor: pointer;
    font-weight: 900;
    font-size: 1.15rem;
    transition: all 0.3s;
}
.btn-finish { background: #27ae60; }

.btn-verify:hover, .btn-finish:hover { filter: brightness(1.2); transform: translateY(-3px); }
</style>
