<template>
  <div class="disaster-ops-container">
    <!-- Main Menu Overlay -->
    <div v-if="state.showMenu" class="main-menu">
      <div class="menu-content">
        <h1 class="menu-title">DISASTER RESPONSE<br>CONTROL CENTER</h1>
        <p class="menu-subtitle">재난 대응 관제 센터 시뮬레이션</p>
        <div class="menu-buttons">
          <button @click="startGame" class="menu-btn primary">게임 시작하기 (START OPERATION)</button>
          <button @click="startTutorial" class="menu-btn secondary">게임 방법 (OPERATOR GUIDE)</button>
        </div>
        <div class="menu-footer">SYSTEM V.1.0.2 // SKN-ACT</div>
      </div>
    </div>

    <!-- Guide Modal -->
    <div v-if="state.showGuide" class="modal-overlay">
      <div class="modal-content">
        <h2 class="modal-title">OPERATOR MANUAL (대응 매뉴얼)</h2>
        <div class="manual-steps">
          <div class="manual-step">
            <span class="step-num">01</span>
            <div class="step-desc">
              <strong>상황 파악 (ANALYZE)</strong>
              <p>좌측 <em>상황 보고서(Situation Report)</em>를 정독하여 현재 현장의 위험 요소(화재, 부상자 등)를 파악하십시오.</p>
            </div>
          </div>
          <div class="manual-step">
            <span class="step-num">02</span>
            <div class="step-desc">
              <strong>규칙 수립 (PROTOCOL)</strong>
              <p>우측 패널에서 <em>조건(IF)</em>과 <em>대응(THEN)</em> 블록을 조립하여 자동 대응 규칙을 만드십시오.</p>
            </div>
          </div>
          <div class="manual-step">
            <span class="step-num">03</span>
            <div class="step-desc">
              <strong>시뮬레이션 (SIMULATE)</strong>
              <p><em>규칙 검증(EVALUATE)</em> 버튼을 눌러 테스트 케이스를 실행하고, 모든 결과가 <span style="color:#22c55e">PASS</span>될 때까지 규칙을 수정하십시오.</p>
            </div>
          </div>
        </div>
        <button @click="state.showGuide = false" class="menu-btn secondary full-width">매뉴얼 닫기 (CLOSE)</button>
      </div>
    </div>

    <!-- Visual Effects -->
    <div class="alert-overlay" :class="{ active: state.isCritical }"></div>
    <div class="scan-line" :class="{ active: state.isCritical }"></div>

    <!-- Tutorial Elements -->
    <div ref="tutorialSpotlight" class="tutorial-spotlight" :class="{ active: state.tutorialActive }"></div>
    <div ref="tutorialPopover" class="tutorial-popover" :class="{ active: state.tutorialActive }">
      <div class="t-header">
        <span class="t-title"><span class="t-step-badge">{{ state.tutorialStep + 1 }}/{{ TUTORIAL_STEPS.length }}</span> 가이드 (GUIDE)</span>
      </div>
      <div class="t-desc" v-html="currentTutorialStepDesc"></div>
      <div class="t-footer">
        <button @click="endTutorial" class="t-btn t-btn-skip">닫기 (SKIP)</button>
        <button @click="nextTutorialStep" class="t-btn t-btn-next">
          {{ state.tutorialStep === TUTORIAL_STEPS.length - 1 ? "확인 (FINISH)" : "다음 (NEXT) →" }}
        </button>
      </div>
    </div>

    <!-- Hint Overlay -->
    <div class="hint-overlay" :class="{ active: state.showHintOverlay }">
        <div class="hint-content">
            <h3>담당자 가이드 (GUIDE)</h3>
            <div v-text="state.hintText"></div>
            <button @click="state.showHintOverlay = false" class="close-btn">확인 (ACKNOWLEDGE)</button>
        </div>
    </div>

    <!-- Game UI -->
    <div v-if="!state.showMenu" id="app-container" class="app-container">
      <!-- Header -->
      <header>
        <div class="brand">재난 대응 관제센터 (INCIDENT TRIAGE)</div>
        <div class="pressure-gauge" :class="pressureClass">
          <span class="pressure-label">INCIDENT PRESSURE:</span>
          <span class="pressure-val" :class="pressureClass">{{ pressureLabel }}</span>
        </div>
        <div class="stage-info">스테이지: {{ state.currentStage.id }} - {{ state.currentStage.title }}</div>
        <div class="controls">
          <span class="badge">{{ state.currentStage.difficulty }}</span>
          <button @click="showHint" class="hint-btn" :class="`hint-level-${hintCount}`" title="힌트 보기">
            ⚠️ 힌트 (HINT)
          </button>
        </div>
      </header>

      <!-- Main Content Grid -->
      <main>
        <!-- Left Panel: Situation Report -->
        <section class="panel left-panel">
          <div class="panel-header">상황 보고서 (SITUATION REPORT)</div>
          <div class="panel-body">
            <div class="scenario-box">
              <div style="margin-bottom:8px;">
                <span v-for="tag in state.currentStage.scenarioTags" :key="tag.text" class="system-tag" :class="`tag-${tag.type}`">[{{ tag.text }}]</span>
              </div>
              <div v-for="(line, idx) in state.currentStage.scenario" :key="idx" v-html="line"></div>
            </div>

            <div class="field-data">
              <div class="field-header">수신된 현장 데이터 (INCOMING DATA)</div>
              <div class="field-grid">
                <div v-for="(type, key) in state.currentStage.fields" :key="key" class="field-item">
                  <span class="field-key">{{ key }}</span>
                  <span class="field-val">{{ Array.isArray(type) ? "Select" : type }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Right Panel: Rule Builder -->
        <section class="panel right-panel">
          <div class="panel-header">대응 수칙 조립 (PROTOCOL ASSEMBLER)</div>
          <div class="panel-body rule-builder-container">
            <div class="rule-list">
              <div v-for="(rule, rIdx) in state.rules" :key="rule.id" class="rule-block" :class="{ 'rule-else': rule.type === 'else', complex: isComplex(rule) }">
                
                <!-- IF Rule Header -->
                <div v-if="rule.type === 'if'" class="rule-header">
                  <span class="rule-label">조건 (IF ANY/ALL TRUE):</span>
                  <button class="logic-toggle" @click="toggleLogic(rIdx)">{{ rule.logic.toUpperCase() }}</button>
                  <button class="btn-icon" @click="removeRule(rIdx)" title="Remove Rule">×</button>
                </div>

                <!-- ELSE Rule Header -->
                <div v-else class="rule-header">
                    <span class="rule-else-label">그 외 (ELSE Unmatched):</span>
                </div>

                <!-- Conditions (only for IF) -->
                <div v-if="rule.type === 'if'" class="conditions-container">
                  <div v-for="(cond, cIdx) in rule.conditions" :key="cIdx" class="condition-row">
                    <select v-model="cond.field">
                      <option v-for="(type, field) in state.currentStage.fields" :key="field" :value="field">{{ field }}</option>
                    </select>
                    <select v-model="cond.op">
                      <option value="eq">==</option>
                      <option value="gte">>=</option>
                      <option value="lte">&lt;=</option>
                    </select>
                    <input type="text" v-model="cond.value" style="width: 60px;">
                    <button class="btn-icon" @click="removeCondition(rIdx, cIdx)">-</button>
                  </div>
                  <button class="btn-icon" style="color:#38bdf8; text-align:left;" @click="addCondition(rIdx)">+ 조건 추가</button>
                </div>

                <!-- Action Row -->
                <div class="action-row">
                  <span class="then-label">대응 (THEN):</span>
                  <select v-model="rule.then.genre">
                    <option v-for="g in state.currentStage.allowedOutputs.genres" :key="g" :value="g">{{ g }}</option>
                  </select>
                  <select v-model="rule.then.action">
                    <option v-for="a in state.currentStage.allowedOutputs.actions" :key="a" :value="a">{{ a }}</option>
                  </select>
                </div>

              </div>
            </div>

            <div class="rule-actions">
              <button @click="addNewRule" id="add-rule-btn" class="action-btn">+ 규칙 추가</button>
              <div class="spacer"></div>
              <button @click="runSimulation" id="run-btn" class="run-btn">▶ 규칙 검증 (EVALUATE)</button>
            </div>
          </div>
        </section>
      </main>

      <!-- Bottom Panel: Logs -->
      <section class="panel bottom-panel">
        <div class="panel-header">
          시뮬레이션 로그 (LOGS)
          <span class="status-indicator" :class="statusClass">{{ statusText }}</span>
        </div>
        <div ref="logContainer" class="log-console">
            <div v-for="(log, idx) in state.logs" :key="idx" class="log-entry" :class="log.cls" v-html="log.html"></div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { reactive, computed, nextTick, ref, onMounted } from 'vue';
import { useUiStore } from '@/stores/ui';

export default {
  name: 'PseudoEmergency',
  setup() {
    const ui = useUiStore();
    
    onMounted(() => {
        ui.isNoticeOpen = false;
    });
    // Stage Data
    const STAGES = [
        {
            id: "E1",
            difficulty: "EASY",
            title: "연기 감지 + 부상자 신고",
            initialPressureCalc: { injured: 1, fire: true, structuralDamage: 'unverified' }, 
            scenarioTags: [
                { text: "SMOKE DETECTED", type: "warn" },
                { text: "INJURY CONFIRMED", type: "danger" },
                { text: "STRUCTURAL: UNVERIFIED", type: "unknown" }
            ],
            scenario: [
                "<p>• 상황 접수: 지하 주차장에서 <span class='hl-warn'>연기(Smoke)</span>가 피어오르고 있다는 신고.</p>",
                "<p>• 넘어져서 다친 <span class='hl-danger'>부상자(Injured) 1명</span>이 발생했다고 함.</p>",
                "<p>• 건물 구조 손상 여부는 <b>미확인(Unverified)</b> 상태.</p>"
            ],
            fields: {
                injured: "number",
                fire: "boolean",
                structuralDamage: ["none", "minor", "major"],
                crowd: ["low", "med", "high"]
            },
            allowedOutputs: {
                genres: ["DISASTER", "EXPERIMENT", "SURVIVAL"],
                actions: ["EVACUATE", "ISOLATE", "CONTAIN", "RATION", "ASSESS"]
            },
            tests: [
                {
                    name: "테스트 1: 부상자 발생",
                    input: { injured: 1, fire: false, structuralDamage: "none", crowd: "low" },
                    expect: { genre: "DISASTER", action: "EVACUATE" }
                },
                {
                    name: "테스트 2: 화재 발생",
                    input: { injured: 0, fire: true, structuralDamage: "none", crowd: "med" },
                    expect: { genre: "DISASTER", action: "EVACUATE" }
                },
                {
                    name: "테스트 3: 구조물 붕괴 위험",
                    input: { injured: 0, fire: false, structuralDamage: "major", crowd: "low" },
                    expect: { genre: "DISASTER", action: "EVACUATE" }
                },
                {
                    name: "테스트 4: 위험 요소 없음",
                    input: { injured: 0, fire: false, structuralDamage: "none", crowd: "low" },
                    expect: { genre: "SURVIVAL", action: "ASSESS" }
                }
            ],
            hints: {
                localRestate: "요구사항: (1) 부상자가 1명 이상이거나, (2) 화재가 있거나, (3) 구조물 손상이 심각(major)하면 '재난(DISASTER)'으로 분류하고 '대피(EVACUATE)'를 지시하라.",
                localFailureTypes: "힌트: '하나라도 해당되면(OR)' 조건인지 확인하세요. 모든 위험 요소를 체크하고 있나요?",
                llmHint: "LLM 힌트: 경계값(0 vs 1)을 확인하고, 우선순위가 맞는지 점검하십시오."
            }
        }
    ];

    const TUTORIAL_STEPS = [
        {
            targetSelector: '#app-container',
            title: '관제 센터에 오신 것을 환영합니다',
            desc: '이곳은 <b>재난 대응 관제 센터(Control Center)</b>입니다.<br>귀하의 목표는 현장 상황에 맞춰 <b>자동 대응 수칙(Protocol)</b>을 설계하여, 모든 시나리오를 안전하게 해결하는 것입니다.'
        },
        {
            targetSelector: '.left-panel',
            title: '1. 상황 보고서 (Situation Report)',
            desc: '<b>이 창은 현장 데이터를 보여줍니다.</b><br>현재 발생한 재난의 종류(화재, 붕괴 등)와 수치 데이터(부상자 수)가 실시간으로 표시됩니다. 이곳의 정보를 바탕으로 판단해야 합니다.'
        },
        {
            targetSelector: '.right-panel',
            title: '2. 대응 수칙 조립 (Rule Builder)',
            desc: '<b>이 창은 명령을 입력하는 곳입니다.</b><br>좌측의 상황 데이터에 따라 어떤 행동을 할지 결정합니다. <i>"만약(IF) 불이 나면, 대피(THEN)시킨다"</i>와 같은 규칙을 블록처럼 조립하세요.'
        },
        {
            targetSelector: '.rule-block',
            title: '3. 조건 및 행동 설정',
            desc: '<b>각 규칙의 세부 내용을 수정할 수 있습니다.</b><br>드롭다운을 눌러 변수(부상자, 화재여부)와 기준값(1명 이상 등)을 변경하여 정교한 규칙을 만드세요.'
        },
        {
            targetId: 'run-btn',
            title: '4. 검증 및 실행 (Evaluate)',
            desc: '<b>규칙이 올바른지 테스트하는 버튼입니다.</b><br>이 버튼을 누르면 4가지 시뮬레이션 케이스가 실행됩니다. 모두 <b>PASS</b>가 나와야 승리합니다.'
        }
    ];

    // Reactive State
    const state = reactive({
        showMenu: true,
        showGuide: false,
        isCritical: false,
        currentStage: STAGES[0],
        rules: [
            {
                id: 'rule-1', type: 'if', logic: 'any',
                conditions: [{ field: 'injured', op: 'gte', value: 1 }],
                then: { genre: 'DISASTER', action: 'EVACUATE' }
            },
            {
                id: 'rule-else', type: 'else',
                then: { genre: 'SURVIVAL', action: 'ASSESS' }
            }
        ],
        logs: [
            { cls: 'system', html: 'STATUS: Awaiting protocol evaluation...' },
            { cls: 'system', html: '<span style="opacity:0.7">> No scenarios executed yet.</span>' }
        ],
        tutorialActive: false,
        tutorialStep: 0,
        hintState: {}, // stageId -> count
        showHintOverlay: false,
        hintText: "",
        statusMode: 'idle', // idle, running, pass, fail
    });

    const logContainer = ref(null);
    const tutorialSpotlight = ref(null);
    const tutorialPopover = ref(null);

    // Hints
    const hintCount = computed(() => state.hintState[state.currentStage.id] || 0);

    // Pressure
    const pressureInfo = computed(() => {
        let score = 0;
        const data = state.currentStage.initialPressureCalc || {};
        if (state.isCritical) return { label: "CRITICAL / ESCALATING", class: "press-critical" }; // Override

        if (data.injured >= 1) score += 1;
        if (data.fire === true) score += 1;
        if (data.structuralDamage === 'major') score += 1;
        if (data.structuralDamage === 'unverified') score += 0.5;

        if (score >= 3) return { label: "CRITICAL", class: "press-critical" };
        if (score >= 2) return { label: "HIGH", class: "press-high" };
        if (score >= 1) return { label: "ELEVATED", class: "press-elevated" };
        return { label: "STABLE", class: "press-stable" };
    });

    const pressureLabel = computed(() => pressureInfo.value.label);
    const pressureClass = computed(() => pressureInfo.value.class);

    // Status
    const statusText = computed(() => {
        if (state.statusMode === 'running') return '실행 중...';
        if (state.statusMode === 'pass') return 'APPROVED';
        if (state.statusMode === 'fail') return 'ALERT';
        return '대기';
    });

    const statusClass = computed(() => {
        if (state.statusMode === 'running') return 'running';
        if (state.statusMode === 'pass') return 'pass';
        if (state.statusMode === 'fail') return 'fail';
        return '';
    });

    const currentTutorialStepDesc = computed(() => {
        const step = TUTORIAL_STEPS[state.tutorialStep];
        if (!step) return '';
        return `<strong>${step.title}</strong><br/>${step.desc}`;
    });

    // Methods
    const isComplex = (rule) => rule.type === 'if' && rule.conditions.length >= 3;

    const startGame = () => {
        state.showMenu = false;
        state.isCritical = false;
    };

    const addNewRule = () => {
        const newRule = {
            id: `rule-${Date.now()}`,
            type: 'if', logic: 'any',
            conditions: [{ field: 'injured', op: 'gte', value: 1 }],
            then: { genre: 'DISASTER', action: 'EVACUATE' }
        };
        state.rules.splice(state.rules.length - 1, 0, newRule);
    };

    const removeRule = (idx) => {
        state.rules.splice(idx, 1);
    };

    const toggleLogic = (idx) => {
        const r = state.rules[idx];
        r.logic = r.logic === 'any' ? 'all' : 'any';
    };

    const addCondition = (rIdx) => {
        state.rules[rIdx].conditions.push({ field: 'fire', op: 'eq', value: true });
    };

    const removeCondition = (rIdx, cIdx) => {
        state.rules[rIdx].conditions.splice(cIdx, 1);
    };

    const showHint = () => {
        const stage = state.currentStage;
        const c = (state.hintState[stage.id] ?? 0) + 1;
        state.hintState[stage.id] = Math.min(c, 3);
        
        let txt = "";
        if (c === 1) txt = stage.hints.localRestate;
        else if (c === 2) txt = stage.hints.localFailureTypes;
        else txt = stage.hints.llmHint;
        
        state.hintText = txt;
        state.showHintOverlay = true;
    };

    // Engine Logic
    function opEval(cond, input) {
        const [op, ...args] = cond;
        const val = (k) => input[k];
        const cmp = (a) => (typeof a === "string" && a.startsWith("$")) ? val(a.slice(1)) : a;
        switch (op) {
            case "eq": return cmp(args[0]) == cmp(args[1]); // loose eq for form inputs (string vs number)
            case "gte": return Number(cmp(args[0])) >= Number(cmp(args[1]));
            case "lte": return Number(cmp(args[0])) <= Number(cmp(args[1]));
            case "any": return args.some(c => opEval(c, input));
            case "all": return args.every(c => opEval(c, input));
            default: throw new Error("Unknown op: " + op);
        }
    }

    function runPolicyAST(ast, input) {
        for (const rule of ast) {
            if (rule.if) {
                if (opEval(rule.if, input)) return rule.then;
            } else if (rule.else) {
                return rule.else;
            }
        }
        return null;
    }

    function sameDecision(a, b) {
        return a && b && a.genre === b.genre && a.action === b.action;
    }

    const runSimulation = () => {
        state.logs = [];
        state.statusMode = 'running';
        state.isCritical = false;
        document.body.classList.remove('critical-mode');
        
        // AST Conversion
        const ast = state.rules.map(r => {
            if (r.type === 'else') return { else: r.then };
            const conds = r.conditions.map(c => [c.op, `$${c.field}`, c.value]);
            return { if: [r.logic, ...conds], then: r.then };
        });

        // Simulate Async
        setTimeout(() => {
            let passAll = true;
            const results = [];
            const delay = 200;

            state.currentStage.tests.forEach((t, i) => {
                let got = null;
                try { got = runPolicyAST(ast, t.input); } 
                catch (e) { got = { genre: "ERROR", action: e.message }; }
                
                const safeGot = got ?? { genre: "NONE", action: "NONE" };
                const ok = sameDecision(safeGot, t.expect);
                if (!ok) passAll = false;

                const statusHtml = ok ? '<span class="log-pass">PASS</span>' : '<span class="log-fail">FAIL</span>';
                const inputStr = Object.entries(t.input).map(([k, v]) => `${k}=${v}`).join(', ');

                setTimeout(() => {
                    state.logs.push({
                        cls: 'log-entry',
                        html: `<span style="color:#666">[테스트 ${i + 1}]</span> ${t.name}<br/>
                               &nbsp;&nbsp;입력: { ${inputStr} }<br/>
                               &nbsp;&nbsp;기대값: ${t.expect.genre}/${t.expect.action} → 결과: ${safeGot.genre}/${safeGot.action} ${statusHtml}`
                    });
                    scrollLog();
                }, i * delay);
                
                results.push({ ok });
            });

            // Final Result
            setTimeout(() => {
                if (passAll) {
                    document.body.classList.remove('critical-mode');
                    state.isCritical = false;
                    state.statusMode = 'pass';
                    state.logs.push({
                         cls: 'log-entry',
                         html: `<span style="color:#22c55e; font-weight:bold;">[SUCCESS] PROTOCOL VERIFIED.</span><br><span style="color:#86efac; font-size:0.9em;">All scenarios handled within safety parameters. Deployment authorized. 💰</span>`
                    });
                } else {
                    document.body.classList.add('critical-mode');
                    state.isCritical = true;
                    state.statusMode = 'fail';
                    state.logs.push({
                        cls: 'log-escalation',
                        html: `<strong>⚠ PROTOCOL FAILURE: 상황 악화 (Incident Escalating)</strong><br>
                               진단: 대응 로직이 위협을 억제하지 못했습니다.<br>
                               상태: 사상자가 증가하고 있습니다. 즉각적인 수정이 필요합니다.`
                    });
                }
                scrollLog();
            }, state.currentStage.tests.length * delay + 100);

        }, 300);
    };

    const scrollLog = () => {
        nextTick(() => {
            if (logContainer.value) {
                logContainer.value.scrollTop = logContainer.value.scrollHeight;
            }
        });
    };

    // Tutorial Logic
    const startTutorial = () => {
        startGame();
        state.tutorialStep = 0;
        state.tutorialActive = true;
        renderTutorialStep();
    };

    const renderTutorialStep = () => {
        nextTick(() => {
            const step = TUTORIAL_STEPS[state.tutorialStep];
            if (!step) { endTutorial(); return; }

            const target = step.targetId ? document.getElementById(step.targetId) : document.querySelector(step.targetSelector);
            if (!target || !tutorialSpotlight.value || !tutorialPopover.value) return;

            target.scrollIntoView({ behavior: 'smooth', block: 'center' });

            const rect = target.getBoundingClientRect();
            const pad = 8;
            
            const spot = tutorialSpotlight.value;
            spot.style.top = (rect.top - pad) + 'px';
            spot.style.left = (rect.left - pad) + 'px';
            spot.style.width = (rect.width + pad * 2) + 'px';
            spot.style.height = (rect.height + pad * 2) + 'px';

            const pop = tutorialPopover.value;
            const popWidth = 320;
            let popLeft = rect.right + 20;
            let popTop = rect.top;

            if (rect.width > window.innerWidth * 0.8) {
                popLeft = window.innerWidth / 2 - (popWidth / 2);
                popTop = window.innerHeight / 3;
            } else {
                if (popLeft + popWidth + 20 > window.innerWidth) {
                    popLeft = rect.left - popWidth - 20;
                }
            }

            if (popLeft < 20) popLeft = 20;
            if (popLeft + popWidth > window.innerWidth) popLeft = window.innerWidth - popWidth - 20;
            if (popTop + 200 > window.innerHeight) popTop = window.innerHeight - 250;
            if (popTop < 20) popTop = 20;

            pop.style.top = popTop + 'px';
            pop.style.left = popLeft + 'px';
        });
    };

    const nextTutorialStep = () => {
        state.tutorialStep++;
        if (state.tutorialStep >= TUTORIAL_STEPS.length) endTutorial();
        else renderTutorialStep();
    };

    const endTutorial = () => {
        state.tutorialActive = false;
    };

    return {
        state,
        STAGES,
        TUTORIAL_STEPS,
        hintCount,
        pressureLabel,
        pressureClass,
        statusText,
        statusClass,
        currentTutorialStepDesc,
        isComplex,
        startGame,
        addNewRule,
        removeRule,
        toggleLogic,
        addCondition,
        removeCondition,
        startTutorial,
        nextTutorialStep,
        endTutorial,
        runSimulation,
        showHint,
        logContainer,
        tutorialSpotlight,
        tutorialPopover
    };
  }
};
</script>

<style scoped>
:root {
    --bg-dark: #0b0f14;
    --bg-panel: #111827;
    --border-color: #1f2937;
    --text-primary: #e5e7eb;
    --text-muted: #9ca3af;
    --accent-blue: #38bdf8;
    --accent-red: #f87171;
    --accent-green: #22c55e;
    --accent-yellow: #facc15;
    --font-mono: 'JetBrains Mono', monospace;
}

.disaster-ops-container {
    height: 100vh;
    background-color: #0b0f14;
    background-image:
        radial-gradient(1200px circle at 20% 10%, #1b2430 0%, transparent 40%),
        linear-gradient(180deg, #0b0f14, #0e141b);
    color: #e5e7eb;
    font-family: 'JetBrains Mono', monospace;
    overflow: hidden;
}

* {
    box-sizing: border-box;
}

/* =========================================
   Main Menu Overlay
   ========================================= */
.main-menu {
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: url('/image/emergency/bg_main.png') no-repeat center center/cover;
    display: flex;
    align-items: center;
    justify-content: center;
}

.main-menu::before {
    content: "";
    position: absolute;
    inset: 0;
    background: rgba(0, 5, 10, 0.7);
    backdrop-filter: blur(2px);
}

.menu-content {
    position: relative;
    z-index: 2;
    text-align: center;
    max-width: 800px;
    padding: 40px;
    background: rgba(11, 15, 20, 0.85);
    border: 1px solid #1f2937;
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.8);
    border-radius: 4px;
}

.menu-title {
    font-size: 3rem;
    line-height: 1.1;
    margin-bottom: 12px;
    color: #38bdf8;
    text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    letter-spacing: -1px;
}

.menu-subtitle {
    font-size: 1.2rem;
    color: #9ca3af;
    margin-bottom: 40px;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.menu-buttons {
    display: flex;
    gap: 20px;
    justify-content: center;
    margin-bottom: 30px;
}

.menu-btn {
    padding: 16px 32px;
    font-size: 1.1rem;
    border-radius: 2px;
    cursor: pointer;
    font-family: inherit;
    font-weight: bold;
    text-transform: uppercase;
    transition: all 0.2s;
}

.menu-btn.primary {
    background: #38bdf8;
    border: 1px solid #38bdf8;
    color: #0b0f14;
}

.menu-btn.primary:hover {
    background: #7dd3fc;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.6);
}

.menu-btn.secondary {
    background: transparent;
    border: 1px solid #9ca3af;
    color: #9ca3af;
}

.menu-btn.secondary:hover {
    border-color: #e5e7eb;
    color: #e5e7eb;
    background: rgba(255, 255, 255, 0.05);
}

.menu-footer {
    font-size: 0.8rem;
    color: #4b5563;
    margin-top: 20px;
    border-top: 1px solid #1f2937;
    padding-top: 10px;
}

/* =========================================
   App Container & Header Components
   ========================================= */
.app-container {
    display: flex;
    flex-direction: column;
    height: 100%;
}

header {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    border-bottom: 1px solid #1f2937;
    background: rgba(11, 15, 20, 0.8);
    backdrop-filter: blur(4px);
}

.brand {
    font-weight: 700;
    letter-spacing: 0.05em;
    color: #38bdf8;
}

.pressure-gauge {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #111827;
    padding: 6px 16px;
    border-radius: 4px;
    border: 1px solid #1f2937;
}

.pressure-label {
    font-size: 0.8rem;
    color: #9ca3af;
    font-weight: bold;
}

.pressure-val {
    font-weight: bold;
    font-size: 0.95rem;
}

.press-stable { color: #38bdf8; }
.press-elevated { color: #facc15; }
.press-high { color: #f87171; text-shadow: 0 0 5px rgba(248, 113, 113, 0.3); }
.press-critical { 
    color: #fb7185; 
    text-shadow: 0 0 8px rgba(251, 113, 133, 0.6); 
    animation: pulse 1.5s infinite; 
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

.stage-info {
    font-size: 1.1rem;
    font-weight: 500;
}

.controls {
    display: flex;
    gap: 16px;
    align-items: center;
}

.badge {
    padding: 4px 8px;
    background: #1f2937;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #9ca3af;
}

.hint-btn {
    background: transparent;
    border: 1px solid #1f2937;
    color: #facc15;
    padding: 6px 12px;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
}

.hint-btn:hover {
    background: rgba(250, 204, 21, 0.1);
    border-color: #facc15;
}

.hint-level-1 { border-color: #6b7280; color: #9ca3af; }
.hint-level-2 { border-color: #facc15; color: #facc15; box-shadow: 0 0 5px rgba(250, 204, 21, 0.2); }
.hint-level-3 { border-color: #38bdf8; color: #38bdf8; box-shadow: 0 0 8px rgba(56, 189, 248, 0.4); }

/* Main Layout */
main {
    flex: 1;
    display: flex;
    overflow: hidden;
}

.panel {
    display: flex;
    flex-direction: column;
    border-right: 1px solid #1f2937;
    transition: background 0.3s;
}

.panel-header {
    background: #0f172a;
    padding: 8px 16px;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    color: #9ca3af;
    border-bottom: 1px solid #1f2937;
    text-transform: uppercase;
    display: flex;
    justify-content: space-between;
}

.panel-body {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
}

.left-panel {
    width: 35%;
    max-width: 450px;
}

.right-panel {
    flex: 1;
    border-right: none;
    background: rgba(2, 6, 23, 0.4);
}

.scenario-box {
    margin-bottom: 24px;
    line-height: 1.6;
}

.system-tag {
    display: inline-block;
    padding: 2px 6px;
    margin: 2px 0;
    font-size: 0.75rem;
    font-weight: bold;
    border-radius: 2px;
    letter-spacing: 0.05em;
}

.tag-danger { border: 1px solid #f87171; color: #f87171; background: rgba(248, 113, 113, 0.1); }
.tag-unknown { border: 1px dashed #64748b; color: #94a3b8; background: rgba(100, 116, 139, 0.1); }
.tag-warn { border: 1px solid #facc15; color: #facc15; background: rgba(250, 204, 21, 0.1); }

.hl-danger { color: #f87171; font-weight: 700; }
.hl-warn { color: #facc15; font-weight: 700; }
.hl-info { color: #38bdf8; font-weight: 700; }

.field-header {
    font-size: 0.8rem;
    color: #9ca3af;
    margin-bottom: 8px;
    border-bottom: 1px solid #1f2937;
    padding-bottom: 4px;
}

.field-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}

.field-item {
    background: #1f2937;
    padding: 8px;
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
}

.field-key { color: #9ca3af; font-size: 0.8rem; }
.field-val { font-weight: bold; }

/* Rule Builder */
.rule-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-bottom: 24px;
}

.rule-block {
    background: #020617;
    border: 1px solid #334155;
    padding: 12px;
    position: relative;
    transition: all 0.2s;
}

.rule-block:hover {
    border-color: #38bdf8;
    box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.2);
}

.rule-block.complex {
    box-shadow: inset 0 0 0 1px rgba(248, 113, 113, 0.3);
    border-color: #475569;
}

.rule-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    align-items: center;
}

.rule-label { font-weight: bold; color: #38bdf8; }
.rule-else-label { font-weight: bold; color: #9ca3af; }

.logic-toggle {
    background: #1e293b;
    border: 1px solid #1f2937;
    color: #9ca3af;
    padding: 2px 8px;
    cursor: pointer;
    font-size: 0.8rem;
}

.logic-toggle:hover { background: #334155; }

.conditions-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding-left: 12px;
    border-left: 2px solid #334155;
    margin-bottom: 12px;
}

.condition-row {
    display: flex;
    gap: 8px;
    align-items: center;
}

.condition-row select, .condition-row input {
    background: #0f172a;
    border: 1px solid #334155;
    color: #e5e7eb;
    padding: 4px;
    font-family: inherit;
}

.btn-icon {
    background: transparent;
    border: none;
    color: #ef4444;
    cursor: pointer;
    font-weight: bold;
    padding: 0 4px;
}

.action-row {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed #334155;
    display: flex;
    align-items: center;
    gap: 12px;
}

.then-label { font-size: 0.8rem; color: #9ca3af; }

.rule-actions {
    display: flex;
    gap: 12px;
    padding-top: 16px;
    border-top: 1px solid #1f2937;
}

.spacer { flex: 1; }

.action-btn {
    background: #1f2937;
    border: 1px solid #1f2937;
    color: #e5e7eb;
    padding: 8px 16px;
    cursor: pointer;
    font-family: inherit;
}

.action-btn:hover { background: #374151; }

.run-btn {
    background: #020617;
    border: 1px solid #475569;
    color: #22c55e;
    font-weight: bold;
    padding: 8px 20px;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
    position: relative;
}

.run-btn:hover {
    background: #052e16;
    border-color: #22c55e;
    box-shadow: 0 0 10px rgba(34, 197, 94, 0.2);
}

.bottom-panel {
    height: 30%;
    min-height: 200px;
    border-top: 1px solid #1f2937;
}

.log-console {
    background: #000;
    padding: 12px;
    font-size: 0.9rem;
    overflow-y: auto;
    height: 100%;
}

.log-entry { margin-bottom: 4px; opacity: 1; }
.log-pass { color: #22c55e; }
.log-fail { color: #f87171; margin-left: 8px; }
.system { color: #38bdf8; }

.status-indicator {
    font-size: 0.7rem;
    padding: 2px 6px;
    background: #333;
    border-radius: 2px;
    margin-left: auto;
}
.status-indicator.running { color: #facc15; }
.status-indicator.pass { background: #22c55e; color: #000; }
.status-indicator.fail { background: #f87171; color: #fff; }

.hint-overlay {
    position: fixed;
    bottom: 20px;
    right: -400px;
    width: 350px;
    background: #1e293b;
    border: 1px solid #facc15;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    transition: right 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    z-index: 100;
}
.hint-overlay.active { right: 20px; }
.hint-content { padding: 16px; }
.hint-content h3 {
    margin: 0 0 12px 0;
    font-size: 1rem;
    color: #facc15;
    border-bottom: 1px solid #475569;
    padding-bottom: 8px;
}
.close-btn {
    width: 100%;
    margin-top: 16px;
    padding: 8px;
    background: #0f172a;
    border: 1px solid #334155;
    color: #9ca3af;
    cursor: pointer;
}
.close-btn:hover { background: #1e293b; color: #e5e7eb; }

/* Modal */
.modal-overlay {
    position: fixed;
    inset: 0;
    z-index: 10000;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
}
.modal-content {
    background: #111827;
    border: 1px solid #38bdf8;
    width: 600px;
    max-width: 90%;
    padding: 32px;
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.5);
    border-radius: 4px;
    position: relative;
}
.modal-title {
    font-size: 1.5rem;
    color: #38bdf8;
    margin: 0 0 24px 0;
    border-bottom: 1px solid #1f2937;
    padding-bottom: 16px;
    letter-spacing: -0.5px;
}
.manual-steps {
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-bottom: 32px;
}
.manual-step { display: flex; gap: 16px; align-items: flex-start; }
.step-num { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: bold; color: #9ca3af; opacity: 0.3; line-height: 1; }
.step-desc { flex: 1; }
.step-desc strong { display: block; color: #e5e7eb; margin-bottom: 6px; font-size: 1.1rem; }
.step-desc p { margin: 0; font-size: 0.95rem; color: #94a3b8; line-height: 1.5; }
.full-width { width: 100%; text-align: center; margin-top: 10px; }

/* Tutorial */
.tutorial-spotlight {
    position: absolute;
    z-index: 10000;
    border: 3px solid #22c55e;
    box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.85);
    border-radius: 4px;
    transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1);
    pointer-events: none;
    display: none;
}
.tutorial-spotlight.active { display: block; animation: breathe 2s infinite; }
@keyframes breathe {
    0%, 100% { border-color: #22c55e; box-shadow: 0 0 20px rgba(34, 197, 94, 0.2), 0 0 0 9999px rgba(0, 0, 0, 0.85); }
    50% { border-color: #86efac; box-shadow: 0 0 40px rgba(34, 197, 94, 0.4), 0 0 0 9999px rgba(0, 0, 0, 0.85); }
}
.tutorial-popover {
    position: absolute;
    z-index: 10001;
    width: 320px;
    background: #1e293b;
    border: 1px solid #22c55e;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    transition: all 0.4s ease;
    opacity: 0;
    pointer-events: auto;
    display: none;
}
.tutorial-popover.active { display: block; opacity: 1; }
.t-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    border-bottom: 1px solid #334155;
    padding-bottom: 8px;
}
.t-title { color: #22c55e; font-weight: bold; font-size: 1.1rem; display: flex; align-items: center; gap: 8px; }
.t-step-badge { background: #22c55e; color: #000; font-size: 0.7rem; padding: 2px 6px; border-radius: 10px; }
.t-desc { font-size: 0.95rem; color: #cbd5e1; line-height: 1.6; margin-bottom: 20px; }
.t-footer { display: flex; justify-content: flex-end; gap: 10px; }
.t-btn { padding: 8px 16px; border-radius: 2px; cursor: pointer; font-weight: bold; font-family: inherit; font-size: 0.85rem; transition: all 0.2s; }
.t-btn-next { background: #22c55e; border: 1px solid #22c55e; color: #020617; }
.t-btn-next:hover { background: #4ade80; }
.t-btn-skip { background: transparent; border: 1px solid #475569; color: #94a3b8; }
.t-btn-skip:hover { border-color: #cbd5e1; color: #cbd5e1; }

/* Alert */
.alert-overlay {
    position: fixed;
    inset: 0;
    background: radial-gradient(circle, transparent 40%, rgba(220, 38, 38, 0.4) 100%);
    box-shadow: inset 0 0 150px rgba(220, 38, 38, 0.6);
    z-index: 9000;
    pointer-events: none;
    opacity: 0;
    transition: opacity 1s ease-out;
    mix-blend-mode: overlay;
}
.alert-overlay.active { animation: alertPulse 4s cubic-bezier(0.22, 1, 0.36, 1) forwards; }
@keyframes alertPulse {
    0% { opacity: 0; transform: scale(1); }
    10% { opacity: 0.8; transform: scale(1.02); }
    30% { opacity: 0.4; } 
    100% { opacity: 0.2; transform: scale(1); }
}
.scan-line {
    position: fixed;
    top: 0;
    left: -100%;
    width: 200%;
    height: 100%;
    background: linear-gradient(90deg, transparent 0%, rgba(220, 38, 38, 0.1) 45%, rgba(220, 38, 38, 0.3) 50%, rgba(220, 38, 38, 0.1) 55%, transparent 100%);
    z-index: 9001;
    pointer-events: none;
    opacity: 0;
    transform: skewX(-20deg);
}
.scan-line.active { opacity: 1; animation: scanSweep 3s ease-in-out forwards; }
@keyframes scanSweep {
    0% { left: -100%; }
    100% { left: 100%; }
}
.log-escalation {
    color: #fca5a5;
    font-family: 'JetBrains Mono', monospace;
    border-left: 2px solid #ef4444;
    padding-left: 8px;
    margin-top: 8px;
    background: rgba(127, 29, 29, 0.1);
}
.log-escalation strong { color: #ef4444; text-transform: uppercase; letter-spacing: 1px; }

/* Critical Mode Overrides for Body */
/* In Vue scoped styles, we can't easily target body, but since this is a full-page component, we style the container based on critical state */
.alert-overlay.active ~ .disaster-ops-container header { /* This selection relies on structure */ }
</style>
