<template>
  <div class="ops-debug-page">
    <div class="game-container">
      <header class="header">
        <h1>DEBUG GYM</h1>
        <div class="subtitle">// ADVANCED BUG HUNTING SYSTEM v2.4</div>
      </header>

      <div class="debug-mode-switch">
        <button class="mode-btn active">🐞 Bug Hunt</button>
        <button class="mode-btn" @click="goToMode('vibe-cleanup')">✨ Vibe Code Clean Up</button>
      </div>

      <div class="main-layout-grid">
        
        <aside class="side-panel">
          <div class="panel-box scenario-box">
            <div class="panel-title">MISSION SCENARIO</div>
            <div class="scenario-content">
              <h3 class="target-name">Critical Crash: User Lookup Failure</h3>
              <p class="long-desc">
                현재 사용자 인증 모듈에서 치명적인 런타임 에러가 보고되었습니다. 
                <br><br>
                <code>main.py</code>의 12번 라인에서 존재하지 않는 ID를 조회할 때 반환되는 <code>None</code> 객체에 대한 예외 처리가 누락되어 있습니다.
                <br><br>
                <strong>[요구사항]</strong><br>
                1. <code>user</code> 변수의 <code>None</code> 여부를 체크하세요.<br>
                2. 크래시 없이 안전하게 종료되도록 로직을 수정하십시오.
              </p>
            </div>
          </div>

          <div class="panel-box explorer-box">
            <div class="panel-title">FILE SYSTEM</div>
            <div class="explorer-tree">
              <div 
                v-for="(content, filename) in files" 
                :key="filename"
                class="explorer-item"
                :class="{ active: currentFileName === filename }"
                @click="switchFile(filename)"
              >
                <span class="file-icon">{{ filename.endsWith('.json') ? '📊' : '🐍' }}</span>
                <span class="file-name">{{ filename }}</span>
              </div>
            </div>
          </div>

          <div class="side-controls">
            <button class="action-btn hint-btn" @click="showHintSystem">
              <span class="btn-glitch"></span>💡 ACCESS HINT
            </button>
            <button class="action-btn debug-btn" @click="mockDebug" :class="{ loading: isLoading }">
              <span class="btn-glitch"></span>🐞 EXECUTE DEBUG
            </button>
            <button class="action-btn submit-btn" @click="mockSubmit">
              <span class="btn-glitch"></span>🚀 DEPLOY FIX
            </button>
          </div>
        </aside>

        <main class="monitor-frame">
          <div class="screen-content">
            <transition name="slide-down">
              <div v-if="hintVisible" class="hint-guide-panel">
                <div class="hint-label">INTELLIGENCE GUIDE</div>
                <div class="hint-text">{{ currentHint }}</div>
                <button class="close-hint" @click="hintVisible = false">×</button>
              </div>
            </transition>

            <div class="editor-header">
              <div class="file-info">
                <span class="status-dot"></span>
                <span class="current-file">EDITING: {{ currentFileName }}</span>
              </div>
              <div v-if="runStatus" class="run-status-tag" :class="runStatus.toLowerCase()">
                {{ runStatus }}
              </div>
            </div>
            
            <div class="editor-container">
              <div class="line-numbers">
                <div v-for="n in lineCount" :key="n">{{ n }}</div>
              </div>
              <textarea 
                class="code-textarea" 
                v-model="files[currentFileName]" 
                spellcheck="false"
                wrap="off"
              ></textarea>
            </div>

            <div class="terminal-section">
              <div class="terminal-header">DIAGNOSTIC TERMINAL</div>
              <div class="terminal-body" :class="{ error: runStatus === 'FAILURE' }">
                <span class="prompt">></span> 
                <span class="terminal-text">{{ terminalText }}</span>
              </div>
            </div>
          </div>
        </main>
      </div>

      <div v-if="showModal" class="result-overlay">
        <div class="result-screen">
          <h2 class="result-title">{{ score === 100 ? 'MISSION CLEAR' : 'FIX REJECTED' }}</h2>
          <div class="score-display">{{ score }}%</div>
          <p class="feedback-txt">{{ feedbackText }}</p>
          <button class="confirm-btn" @click="showModal = false">RETURN TO BASE</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const goToMode = (mode) => {
  if (mode === 'vibe-cleanup') {
    router.push('/practice/vibe-cleanup');
  }
};

const files = reactive({
  'main.py': `import json\nfrom auth import login\n\ndef main():\n    with open("users.json", "r") as f:\n        users = json.load(f)\n\n    # 유저 ID 99번은 존재하지 않음\n    user = next((u for u in users if u["id"] == 99), None)\n\n    # ERROR: user가 None일 경우 여기서 크래시 발생\n    print(f"Logging in {user['username']}...")\n\n    if login(user):\n        print("SUCCESS")`,
  'auth.py': `def login(user):\n    return user.get('isActive', False)`,
  'users.json': `[{"id": 1, "username": "admin"}]`
});

const currentFileName = ref('main.py');
const terminalText = ref('SYSTEM READY...');
const isLoading = ref(false);
const runStatus = ref(null);
const score = ref(0);
const showModal = ref(false);
const feedbackText = ref('');
const hintVisible = ref(false);
const currentHint = ref("파이썬의 'if user:' 구문을 사용하여 None 여부를 먼저 체크하세요.");

const lineCount = computed(() => files[currentFileName.value].split('\n').length);
const switchFile = (name) => currentFileName.value = name;

const showHintSystem = () => { hintVisible.value = true; };
const mockDebug = () => {
  isLoading.value = true;
  terminalText.value = "ANALYZING CODE...";
  setTimeout(() => {
    isLoading.value = false;
    if (files['main.py'].includes('if user')) {
      runStatus.value = 'SUCCESS';
      terminalText.value = 'Execution finished. No errors found.';
    } else {
      runStatus.value = 'FAILURE';
      terminalText.value = 'TypeError: NoneType object is not subscriptable';
    }
  }, 1000);
};
const mockSubmit = () => {
  score.value = files['main.py'].includes('if user') ? 100 : 0;
  feedbackText.value = score.value === 100 ? "완벽한 수정입니다." : "여전히 에러가 발생합니다.";
  showModal.value = true;
};
</script>

<style scoped>
/* OpsPractice 스타일 테마 */
.ops-debug-page {
  --neon-cyan: #00f3ff;
  --neon-magenta: #ff00ff;
  --neon-yellow: #ffff00;
  --bg-dark: #0a0e17;
  --panel-bg: rgba(26, 31, 46, 0.9);
  
  background: var(--bg-dark);
  color: var(--neon-cyan);
  min-height: 100vh;
  padding: 30px;
  font-family: 'Rajdhani', sans-serif;
}

.debug-mode-switch {
  display: flex;
  gap: 12px;
  margin: 0 0 20px 0;
}

.mode-btn {
  padding: 10px 16px;
  font-family: 'Orbitron';
  font-weight: 700;
  background: transparent;
  border: 1px solid rgba(0, 243, 255, 0.4);
  color: var(--neon-cyan);
  cursor: pointer;
  border-radius: 6px;
  transition: 0.2s ease;
}

.mode-btn.active {
  background: rgba(0, 243, 255, 0.15);
  box-shadow: 0 0 12px rgba(0, 243, 255, 0.3);
}

.mode-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 16px rgba(0, 243, 255, 0.35);
}

.main-layout-grid {
  display: grid;
  grid-template-columns: 480px 1fr;
  gap: 30px;
  height: 85vh; /* 화면 높이에 맞춤 */
}

/* 사이드 패널 */
.side-panel {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.panel-box {
  background: var(--panel-bg);
  border: 1px solid rgba(0, 243, 255, 0.3);
  padding: 25px;
  margin-bottom: 20px;
  border-radius: 4px;
}

.panel-title {
  color: var(--neon-cyan);
  font-family: 'Orbitron';
  font-size: 0.9em;
  margin-bottom: 15px;
  border-left: 4px solid var(--neon-cyan);
  padding-left: 10px;
}

.long-desc { color: #a0aec0; line-height: 1.6; }

/* 버튼 디자인 (색상 강조) */
.side-controls { display: flex; flex-direction: column; gap: 15px; }

.action-btn {
  padding: 18px;
  font-family: 'Orbitron';
  font-weight: bold;
  background: transparent;
  cursor: pointer;
  transition: 0.3s;
  border-radius: 4px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hint-btn { border: 2px solid var(--neon-yellow); color: var(--neon-yellow); }
.hint-btn:hover { background: var(--neon-yellow); color: #000; box-shadow: 0 0 15px var(--neon-yellow); }

.debug-btn { border: 2px solid var(--neon-cyan); color: var(--neon-cyan); }
.debug-btn:hover { background: var(--neon-cyan); color: #000; box-shadow: 0 0 15px var(--neon-cyan); }

.submit-btn { border: 2px solid var(--neon-magenta); color: var(--neon-magenta); }
.submit-btn:hover { background: var(--neon-magenta); color: #000; box-shadow: 0 0 15px var(--neon-magenta); }

/* 에디터 모니터 프레임 (깨짐 방지 핵심) */
.monitor-frame {
  background: #000;
  border: 2px solid #2d3748;
  border-radius: 8px;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 내부 요소 탈출 방지 */
}

.screen-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-header {
  background: #1a202c;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #2d3748;
}

/* 코드 입력창 영역 */
.editor-container {
  flex: 1; /* 남은 공간 모두 차지 */
  display: flex;
  background: #0d1117;
  overflow: hidden;
}

.line-numbers {
  width: 50px;
  padding: 20px 0;
  background: #080b10;
  color: #4b5563;
  text-align: right;
  padding-right: 15px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  user-select: none;
}

.code-textarea {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #e5e7eb;
  padding: 20px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 16px;
  line-height: 1.6;
  resize: none;
  white-space: pre;
  overflow: auto; /* 내용 많을 때 스크롤 */
}

/* 터미널 섹션 */
.terminal-section {
  height: 150px;
  background: #000;
  border-top: 2px solid #2d3748;
  padding: 15px 25px;
}

.terminal-header {
  font-size: 11px;
  color: #718096;
  margin-bottom: 8px;
  letter-spacing: 2px;
}

.terminal-body { font-family: 'JetBrains Mono'; font-size: 14px; }
.terminal-body.error { color: var(--danger-red); }
.prompt { color: var(--neon-yellow); margin-right: 10px; }

/* 힌트 애니메이션 */
.hint-guide-panel {
  position: absolute;
  top: 0; left: 0; right: 0;
  background: rgba(255, 255, 0, 0.1);
  backdrop-filter: blur(8px);
  border-bottom: 2px solid var(--neon-yellow);
  padding: 25px;
  z-index: 20;
}

.result-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.85);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
}

.result-screen {
  background: var(--panel-bg);
  border: 2px solid var(--neon-cyan);
  padding: 60px;
  text-align: center;
  border-radius: 10px;
}

.score-display {
  font-size: 4em;
  font-family: 'Orbitron';
  color: var(--neon-yellow);
  margin: 20px 0;
}
</style>
