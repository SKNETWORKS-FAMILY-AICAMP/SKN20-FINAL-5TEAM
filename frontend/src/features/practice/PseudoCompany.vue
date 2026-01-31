<script setup>
/**
 * 수정일: 2026-01-29
 * 내용: CS 운영 시스템 리뉴얼 (Pseudo Company)
 * - 모달 구조 및 Monaco Editor 연동
 * - image/company 폴더 이미지 적용
 */
import { ref, computed, onMounted } from 'vue';
import { useGameStore } from '@/stores/game';
import { VueMonacoEditor } from '@guolao/vue-monaco-editor';

const emit = defineEmits(['close']);
const game = useGameStore();

// --- 상태 변수 (State) ---
const gameStarted = ref(false);
const gameDifficulty = ref('normal');
const currentIdx = ref(0);
const hintIdx = ref(0);
const editorContent = ref('');
const displayedDialogue = ref('');
const isStageClear = ref(false);
const isGameFinished = ref(false);

// 타이핑 효과를 위한 인터벌 저장 변수
let typingInterval = null;

// --- 상수 데이터 (Constants) ---
const CUSTOMER_TYPES = {
    hard_boss: {
        name: "감사팀 (Audit)",
        orderText: "금번 로직은 컴플라이언스 규정을 준수해야 합니다. {orderTextTemplate} 불필요한 리소스 낭비 없이 정확한 결과값만 산출하십시오.",
    }
};

const RAW_STAGES = [
    {
        title: "데이터 정합성 검사 (Validity Check)",
        fnName: "check_validity",
        params: "n",
        goal: "입력값(n)이 0을 초과하는 유효 데이터인지 검증",
        hard_order: "입력 데이터가 0을 초과하는 경우만 Valid 상태로 판별해야 합니다. 0 이하의 값은 Invalid 처리하십시오.",
        evalType: "comparison",
        testCases: {
            easy: [{ i: 5, e: true, type: 'basic' }],
            normal: [{ i: 5, e: true, type: 'basic' }, { i: 0, e: false, type: 'boundary' }],
            hard: [
                { i: 10, e: true, type: 'basic' },
                { i: 0, e: false, type: 'boundary' },
                { i: -1, e: false, type: 'negative' },
                { i: 0.0001, e: true, type: 'logic' }
            ]
        },
        hints: ["기준값(0)은 포함되지 않습니다 (Zero-exclusive).", "음수 입력 시 False 반환 정책을 준수하십시오.", "Comparison Operator를 확인하십시오."]
    },
    {
        title: "짝수 패리티 검증 (Parity Check)",
        fnName: "is_even_data",
        params: "data",
        goal: "데이터가 2의 배수(짝수) 체계인지 검증",
        hard_order: "시스템 아키텍처 상 2의 배수 단위만 허용됩니다. 음수 및 0인 경우에도 수학적 짝수 정의를 따릅니다.",
        evalType: "mod",
        testCases: {
            easy: [{ i: 4, e: true, type: 'basic' }],
            normal: [{ i: 4, e: true, type: 'basic' }, { i: 7, e: false, type: 'logic' }],
            hard: [
                { i: 100, e: true, type: 'basic' },
                { i: 1, e: false, type: 'logic' },
                { i: 0, e: true, type: 'boundary' },
                { i: -2, e: true, type: 'negative' }
            ]
        },
        hints: ["Modulo 연산자를 활용하여 잔여값을 확인하십시오.", "Zero(0)는 짝수로 분류됩니다.", "음수의 Modulo 연산 결과도 동일 규경입니다."]
    },
    {
        title: "절대값 산출 (Magnitude Check)",
        fnName: "process_magnitude",
        params: "val",
        goal: "입력값의 절대 크기(Magnitude) 산출",
        hard_order: "벡터의 방향성(부호)을 제거하고 스칼라 크기만 추출하십시오. 음수는 양수로 변환되어야 합니다.",
        evalType: "abs",
        testCases: {
            easy: [{ i: 10, e: 10, type: 'basic' }],
            normal: [{ i: 10, e: 10, type: 'basic' }, { i: -5, e: 5, type: 'negative' }],
            hard: [
                { i: 99, e: 99, type: 'basic' },
                { i: -8, e: 8, type: 'negative' },
                { i: 0, e: 0, type: 'boundary' },
                { i: -1, e: 1, type: 'negative' }
            ]
        },
        hints: ["원점(0)으로부터의 거리를 계산하십시오.", "Negative Flag를 제거해야 합니다.", "Zero값은 변환 후에도 유지가 필요합니다."]
    },
    {
        title: "임계 온도 모니터링 (Threshold)",
        fnName: "check_temperature",
        params: "temp",
        goal: "운영 안정 범위(18~26도) 준수 여부 확인",
        hard_order: "서버 랙 온도가 18.0~26.0도 사이일 경우 Normal 신호를 반환하십시오. 경계값을 포함하는 Inclusive 조건입니다.",
        evalType: "range",
        testCases: {
            easy: [{ i: 22, e: true, type: 'basic' }],
            normal: [{ i: 22, e: true, type: 'basic' }, { i: 30, e: false, type: 'logic' }],
            hard: [
                { i: 20, e: true, type: 'basic' },
                { i: 18, e: true, type: 'boundary' },
                { i: 26, e: true, type: 'boundary' },
                { i: 17.9, e: false, type: 'logic' }
            ]
        },
        hints: ["Upper/Lower Bound 조건을 모두 확인하십시오 (AND).", "경계값(Boundary Value) 포함 정책을 확인하십시오.", "부동 소수점 비교에 유의하십시오."]
    },
    {
        title: "문자열 규격 검증 (Length Validation)",
        fnName: "validate_length",
        params: "text",
        goal: "입력 텍스트가 최소 규격(5자) 이상인지 검증",
        hard_order: "입력된 String Buffer의 길이가 5 Bytes(글자) 이상이어야 유효합니다. Null 또는 Empty String은 기각하십시오.",
        evalType: "len",
        testCases: {
            easy: [{ i: "hello", e: true, type: 'basic' }],
            normal: [{ i: "hello", e: true, type: 'basic' }, { i: "abc", e: false, type: 'logic' }],
            hard: [
                { i: "python", e: true, type: 'basic' },
                { i: "abc", e: false, type: 'logic' },
                { i: "valid", e: true, type: 'boundary' },
                { i: "", e: false, type: 'missingCase' }
            ]
        },
        hints: ["String Object의 길이 속성을 확인하십시오.", "최소 길이 정책(>=5)을 준수하십시오.", "Empty String 예외 처리가 필요합니다."]
    }
];

// --- 개선된 EVALUATORS (Feedback 중심) ---
const EVALUATORS = {
    comparison: (c, val) => {
        if (!c.includes('return')) return { pass: false, msg: "[Syntax] Return 구문이 누락되었습니다." };
        if (c.includes('returnn>0') || (c.includes('ifn>0') && (c.includes('returnTrue') || c.includes('return True')))) {
            const res = val > 0;
            return { pass: res, msg: res ? "Valid" : "Boundary/Logic Error" };
        }
        return { pass: false, msg: "[Logic] 표준 비교 연산 규격을 준수하십시오. (> 0)" };
    },
    mod: (c, val) => {
        if (!c.includes('return')) return { pass: false, msg: "[Syntax] Return 구문이 누락되었습니다." };
        if (c.includes('data%2==0')) {
            const res = val % 2 === 0;
            return { pass: res, msg: res ? "Valid" : "Parity Logic Error" };
        }
        return { pass: false, msg: "[Logic] Modulo 연산자(%)를 활용하십시오." };
    },
    abs: (c, val) => {
        if (!c.includes('return')) return { pass: false, msg: "[Syntax] Return 구문이 누락되었습니다." };
        if (c.includes('abs(val)') || (c.includes('ifval<0') && c.includes('return-val'))) {
             const res = Math.abs(val) === (val < 0 ? -val : val);
             return { pass: res, msg: res ? "Valid" : "Calculation Error" };
        }
        return { pass: false, msg: "[Logic] 절대값 산출 로직을 확인하십시오." };
    },
    len: (c, val) => {
        if (!c.includes('return')) return { pass: false, msg: "[Syntax] Return 구문이 누락되었습니다." };
        if (c.includes('len(text)>=5')) {
             const res = val.length >= 5;
             return { pass: res, msg: res ? "Valid" : "Length Logic Error" };
        }
        return { pass: false, msg: "[Logic] 길이 검증 규격(len)을 확인하십시오." };
    },
    range: (c, val) => {
         if (!c.includes('return')) return { pass: false, msg: "[Syntax] Return 구문이 누락되었습니다." };
         if (c.includes('18<=temp<=26') || (c.includes('temp>=18') && c.includes('temp<=26'))) {
              const res = val >= 18 && val <= 26;
              return { pass: res, msg: res ? "Valid" : "Range Logic Error" };
         }
         return { pass: false, msg: "[Logic] 온도 임계값 범위를 확인하십시오." };
    }
};

// --- 계산된 속성 (Computed) ---
const currentStage = computed(() => RAW_STAGES[currentIdx.value] || {});

const currentHaruImage = computed(() => {
    return gameDifficulty.value === 'hard' ? '/image/company/haru_hard.png' : '/image/company/haru.png';
});

const hintButtonText = computed(() => {
    return gameDifficulty.value === 'hard' ? '💡 심화 정책 가이드 조회' : '💡 정책 레퍼런스 열람';
});

const stageBadge = computed(() => {
    return isGameFinished.value ? 'COMPLETE' : `TICKET #${202400 + currentIdx.value + 1}`;
});

const customerName = computed(() => {
    if (!gameStarted.value) return " 티켓 상세 내용";
    return `📧 발세: ${gameDifficulty.value === 'hard' ? '감사팀(Audit)' : '현업 부서'}`;
});

// 텍스트 템플릿 처리
const renderTemplate = (str, vars) => {
    return str.replace(/{(\w+)}/g, (match, key) => {
        return vars[key] !== undefined ? vars[key] : match;
    });
};

const orderBody = computed(() => {
    if (!gameStarted.value) return "할당된 티켓이 없습니다. 좌측 패널에서 업무 레벨을 설정하십시오.";
    
    const stage = currentStage.value;
    if (!stage.goal) return "";

    if (gameDifficulty.value === 'hard' && stage.hard_order) {
        return renderTemplate(CUSTOMER_TYPES.hard_boss.orderText, { orderTextTemplate: stage.hard_order });
    }
    const baseText = "{orderTextTemplate}";
    const defaultCustomerText = "안녕하세요, 운영 지원팀입니다. " + baseText + " 해당 케이스 발생 시 시스템 로그에 어떻게 기록되는지 확인 부탁드립니다.";
    return renderTemplate(defaultCustomerText, { orderTextTemplate: stage.goal + " 관련 로직을 구현하십시오." });
});

const haruSummary = computed(() => {
    if (!gameStarted.value) return "System: 대기 중...";
    const stage = currentStage.value;
    return `System: ${stage.fnName}(${stage.params}) 정책 구현 요청 수신.`;
});

// Monaco Editor 옵션 (난이도별 제어)
const editorOptions = computed(() => ({
    minimap: { enabled: false },
    fontSize: 16,
    lineHeight: 24,
    fontFamily: "'Fira Code', 'Consolas', monospace",
    theme: 'vs-dark',
    renderLineHighlight: 'all',
    scrollBeyondLastLine: false,
    automaticLayout: true,
    // [Difficulty] Easy: 자동 완성, Hard: 엄격 모드
    quickSuggestions: gameDifficulty.value === 'easy',
    suggestOnTriggerCharacters: gameDifficulty.value === 'easy',
}));

// --- 메소드 (Methods) ---
const typeHaru = (text) => {
    if (typingInterval) clearInterval(typingInterval);
    displayedDialogue.value = "";
    let i = 0;
    typingInterval = setInterval(() => {
        if (i < text.length) {
            displayedDialogue.value += text[i++];
        } else {
            clearInterval(typingInterval);
        }
    }, 15);
};

const loadStage = (idx) => {
    if (idx >= RAW_STAGES.length) {
        isGameFinished.value = true;
        typeHaru("모든 교육 과정 이수가 완료되었습니다. 인사팀에 최종 평가 리포트를 전송하겠습니다. 수고하셨습니다.");
        return;
    }

    currentIdx.value = idx;
    hintIdx.value = 0;
    isStageClear.value = false;
    
    const stage = RAW_STAGES[idx];
    
    // 에디터 초기화
    editorContent.value = `def ${stage.fnName}(${stage.params}):\n    # TODO: 운영 정책에 맞춰 로직 구현\n    `;
    
    const welcomeMsg = idx === 0 
        ? "첫 번째 티켓이 할당되었습니다. 내용을 확인하고 정책에 맞는 로직을 구현하십시오." 
        : "신규 티켓이 접수되었습니다. 처리 기한 내에 로직을 완성하십시오.";
    
    typeHaru(welcomeMsg);
};

const startGame = (difficulty) => {
    gameDifficulty.value = difficulty;
    gameStarted.value = true;
    typeHaru(`[SYSTEM] ${difficulty.toUpperCase()} MODE ACTIVATED. 인사 발령 확인되었습니다. 운영팀 리드 하루입니다.`);
    
    setTimeout(() => {
        loadStage(0);
    }, 1500);
};

const handleHint = () => {
    // [Difficulty] Hard 모드는 힌트 불가
    if (gameDifficulty.value === 'hard') {
        typeHaru("⚠️ [AUDIT WARNING] 감사(Audit) 모드에서는 힌트 접근이 제한됩니다. 정책 문서를 스스로 분석하십시오.");
        return;
    }
    // [Difficulty] Normal 모드: 3회 제한 (현재 힌트 배열 길이로 자연스럽게 제한됨)
    // 좀 더 명시적인 카운팅이 필요하다면 추가 변수 사용 가능하나, 여기서는 단계별 힌트 제공으로 대체
    
    const stage = currentStage.value;
    if (hintIdx.value < stage.hints.length) {
        typeHaru(`[HINT ${hintIdx.value + 1}/${stage.hints.length}] ${stage.hints[hintIdx.value++]}`);
    } else {
        typeHaru("추가 가이드는 제공되지 않습니다. 기존 정책 문서를 재확인하십시오.");
    }
};

const runCode = () => {
    const stage = currentStage.value;
    const userCode = editorContent.value.replace(/\s/g, ""); // 공백 제거 후 비교
    const evalFunc = EVALUATORS[stage.evalType];
    const tests = stage.testCases[gameDifficulty.value];

    // [Difficulty] Hard 모드: 세미콜론 검사 (Strict Syntax) - Python이지만 가상의 엄격함 적용
    // 혹은 특정 키워드 제한 등. 여기서는 간단히 'pass' 키워드 사용 금지 등 예시
    if (gameDifficulty.value === 'hard' && userCode.includes('pass')) {
         typeHaru("⚠️ [AUDIT WARNING] 'pass' 임시 구문은 프로덕션 코드에 허용되지 않습니다.");
         return;
    }

    let passCount = 0;
    let failedMsg = null;

    for (let i = 0; i < tests.length; i++) {
        const test = tests[i];
        const result = evalFunc(userCode, test.i); // Returns { pass: bool, msg: string }

        if (result && result.pass === test.e) {
            passCount++;
        } else {
            failedMsg = result ? result.msg : "Unknown Error";
            // Hard 모드는 첫 실패 시 즉시 중단 및 재시도 강요
            if (gameDifficulty.value === 'hard') break;
        }
    }

    const allPass = (passCount === tests.length);

    if (allPass) {
        isStageClear.value = true;
        typeHaru("✅ 검증 통과. 정책 준수 여부가 확인되었습니다. 해당 티켓을 Close 처리합니다.");
    } else {
        // [Difficulty] Fail Feedback
        if (gameDifficulty.value === 'hard') {
            typeHaru(`⛔ [CRITICAL FAILURE] ${failedMsg}\n보안 감사 기준 미달로 스테이지가 초기화됩니다.`);
            // 스테이지 리셋 (코드 초기화)
            setTimeout(() => {
                editorContent.value = `def ${stage.fnName}(${stage.params}):\n    # RE-TRY REQUIRED\n    `;
            }, 2000);
        } else {
             typeHaru(`❌ 검증 실패 (${passCount}/${tests.length} 통과).\nSystem Feedback: ${failedMsg || "데이터 처리 로직을 점검하십시오."}`);
        }
    }
};

const nextStage = () => {
    loadStage(currentIdx.value + 1);
};

// 초기 다이얼로그 설정
onMounted(() => {
    displayedDialogue.value = "인사 발령 확인되었습니다. 운영팀 리드 하루입니다. 본 시뮬레이션을 통해 귀하의 업무 적합성을 평가하겠습니다.";
});

</script>

<template>
  <div class="pseudo-company-overlay" :style="{ backgroundImage: `url('/image/company/office_bg.png')` }">
    <div class="company-container">
      <!-- 닫기 버튼 -->
      <button @click="$emit('close')" class="btn-close-company" title="사무실 나가기">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>

      <!-- 업무 강도 선택 오버레이 -->
      <transition name="fade">
          <div v-if="!gameStarted" class="difficulty-overlay">
              <h2 class="title-main">업무 투입 레벨 설정</h2>
              <p class="desc-main">
                  본 시스템은 귀하의 로직 설계 역량을 검증합니다. 적절한 운영 단계를 선택하십시오.
              </p>
              <div class="btn-group">
                <button class="difficulty-btn btn-easy" @click="startGame('easy')">LEVEL 1: 신규 입사자 교육 (OJT)</button>
                <button class="difficulty-btn btn-normal" @click="startGame('normal')">LEVEL 2: 일반 운영 업무 (Operation)</button>
                <button class="difficulty-btn btn-hard" @click="startGame('hard')">LEVEL 3: 심화 정책 검증 (QA/Audit)</button>
              </div>
          </div>
      </transition>

      <!-- 좌측 사이드바 -->
      <div class="sidebar">
          <div class="character-container">
              <img :src="currentHaruImage" class="haru-img" alt="CS Team Lead Haru">
          </div>
          <div class="dialogue-box">
              <div class="name-tag">CS운영팀장</div>
              <div class="dialogue-text">{{ displayedDialogue }}</div>
          </div>
      </div>

      <!-- 우측 콘텐츠 영역 -->
      <div class="content">
          <div class="stage-indicator">
              <span class="badge">{{ stageBadge }}</span>
              <div class="status-meta" style="display: flex; align-items: center; gap: 12px; margin-right: 50px; height: 100%;">
                  <span v-if="gameDifficulty === 'hard'" class="hard-warning" style="margin: 0;">⚠️ QA Audit: 엄격한 정책 검증 모드</span>
                  <span class="difficulty-tag" style="font-size: 0.9rem; line-height: 1; margin: 0;">{{ gameDifficulty.toUpperCase() }}</span>
              </div>
          </div>

          <div class="problem-section">
              <div class="order-card">
                  <div class="order-header">{{ customerName }}</div>
                  <div class="order-body">{{ orderBody }}</div>
              </div>
              <div class="summary-box">{{ haruSummary }}</div>
          </div>

          <!-- 에디터 영역 -->
          <div class="editor-wrapper">
            <vue-monaco-editor
              v-model:value="editorContent"
              language="python"
              :options="editorOptions"
              class="company-monaco-editor"
              :disabled="isStageClear || isGameFinished"
            />
          </div>

          <div class="footer">
              <button 
                  class="btn-hint" 
                  @click="handleHint" 
                  :disabled="!gameStarted || isStageClear || isGameFinished"
              >
                  {{ hintButtonText }}
              </button>
              
              <button 
                  v-if="isStageClear" 
                  class="btn-next" 
                  @click="nextStage"
              >
                  티켓 종료 및 다음 건 처리
              </button>
              
              <button 
                  v-else 
                  class="btn-run" 
                  @click="runCode" 
                  :disabled="!gameStarted || isGameFinished"
              >
                  코드 리뷰 요청
              </button>
          </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pseudo-company-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background-size: cover;
  background-position: center;
  display: grid;
  grid-template-columns: 0.5fr 8.5fr 1fr; /* 좌측 여백(2fr)을 대폭 줄이고 모달창(5fr -> 8.5fr) 확장 */
  align-items: center;
  backdrop-filter: blur(5px);
  padding: 0;
}

.company-container {
    grid-column: 2; /* 5fr 영역에 배치 */
    display: flex;
    width: 100%;
    height: 90vh;
    background: rgba(255, 255, 255, 0.98);
    border-radius: 16px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    position: relative;
    border: 1px solid rgba(44, 62, 80, 0.2);
}

/* 닫기 버튼 */
.btn-close-company {
  position: absolute;
  top: 35px; /* EASY 문구의 수직 중앙에 맞춤 */
  right: 25px;
  background: transparent;
  color: #2c3e50;
  cursor: pointer;
  z-index: 101;
  padding: 5px;
  border-radius: 50%;
  transition: all 0.2s;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-close-company:hover {
  background: rgba(0,0,0,0.1);
  transform: rotate(90deg);
}
.btn-close-company svg { width: 32px; height: 32px; }

/* 오버레이 효과 */
.difficulty-overlay {
    position: absolute;
    inset: 0;
    background: rgba(255, 255, 255, 0.98);
    z-index: 100;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 40px;
    text-align: center;
}

.title-main { color: #2c3e50; font-size: 2rem; margin-bottom: 10px; font-weight: 800; }
.desc-main { color: #7f8c8d; font-size: 1rem; margin-bottom: 40px; max-width: 500px; line-height: 1.6; }

.btn-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.difficulty-btn {
    width: 320px;
    padding: 20px;
    font-size: 1.1rem;
    border-radius: 12px;
    color: white;
    transition: all 0.2s;
    border: none;
    cursor: pointer;
    font-weight: 700;
}
.btn-easy { background: #27ae60; }
.btn-normal { background: #2c3e50; }
.btn-hard { background: #8e44ad; }
.difficulty-btn:hover { transform: translateY(-3px); filter: brightness(1.1); box-shadow: 0 8px 20px rgba(0,0,0,0.15); }

/* 좌측 사이드바 */
.sidebar {
    flex: 0 0 460px; /* 꼬리 공간 확보를 위해 사이드바 너비 확장 (400px -> 460px) */
    background: #f1f4f6;
    display: flex;
    flex-direction: column;
    padding: 0;
    border-right: 1px solid rgba(0,0,0,0.05);
    overflow: hidden;
    height: 100%;
}

.character-container {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    overflow: visible;
    padding-top: 40px;
}

.haru-img {
    width: 100%;
    height: auto;
    object-fit: contain;
    object-position: top center;
    filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.2));
    mask-image: linear-gradient(to bottom, black 95%, transparent 100%);
    transition: all 0.5s ease;
    transform: scale(1.2) translateX(-20px); /* 배율을 낮추고 왼쪽으로 살짝 밀어 꼬리 공간 확보 */
    transform-origin: top center;
}

.dialogue-box {
    margin: 20px 30px 30px 30px; /* 사이드바 패딩 대신 박스에 마진 추가 */
    background: white;
    border: 2px solid #2c3e50;
    border-radius: 12px;
    padding: 24px;
    min-height: 150px;
    position: relative;
    z-index: 10;
}

.name-tag {
    position: absolute;
    top: -15px;
    left: 20px;
    background: #2c3e50;
    color: white;
    padding: 4px 16px;
    border-radius: 6px;
    font-weight: 800;
    font-size: 0.9rem;
}

.dialogue-text {
    font-size: 1.05rem;
    line-height: 1.7;
    color: #2c3e50;
    word-break: keep-all;
}

/* 우측 레이아웃 */
.content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 40px;
    gap: 20px;
    background: white;
    overflow-y: auto;
}

.stage-indicator {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #f1f4f6;
    padding-bottom: 15px;
}

.badge { font-weight: 900; color: #7f8c8d; letter-spacing: 1px; }
.difficulty-tag { font-weight: 800; color: #2c3e50; }
.hard-warning { color: #c0392b; font-size: 0.8rem; background: #fff5f5; padding: 5px 12px; border-radius: 6px; border: 1px solid #ffc9c9; }

.order-card {
    background: #f8f9fa;
    padding: 24px;
    border-radius: 12px;
    border: 1px solid rgba(0,0,0,0.05);
    margin-bottom: 12px;
}

.order-header { font-size: 0.85rem; font-weight: 800; color: #2c3e50; margin-bottom: 10px; }
.order-body { font-size: 1.1rem; line-height: 1.6; color: #2f3640; border-left: 4px solid #2c3e50; padding-left: 15px; }

.summary-box {
    background: #f1f4f6;
    padding: 15px 20px;
    border-radius: 8px;
    font-size: 1rem;
    color: #2c3e50;
    font-weight: 700;
}

/* 에디터 */
.editor-wrapper {
  flex: 1;
  min-height: 350px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #282c34;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.company-monaco-editor {
  width: 100%;
  height: 100%;
}

.footer {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    margin-top: 10px;
}

button.btn-hint {
    background: white;
    color: #f39c12;
    border: 2px solid #f39c12;
    padding: 12px 24px;
}

button.btn-run { background: #2c3e50; color: white; padding: 12px 32px; font-size: 1.05rem; }
button.btn-next { background: #27ae60; color: white; padding: 12px 32px; font-size: 1.05rem; }

button:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }

/* 애니메이션 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 1200px) {
  .sidebar { flex: 0 0 350px; }
  .company-container { width: 98vw; height: 95vh; }
}
</style>