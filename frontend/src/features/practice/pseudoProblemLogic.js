/**
 [수정일: 2026-01-31]
 내용: pseudoProblem.vue의 로직을 Composable 패턴으로 분리
*/
import { ref, reactive, computed, watch, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import axios from 'axios'
import { aiQuests } from './support/unit1/logic-mirror/data/stages.js'

export function usePseudoProblem(props, emit) {
    const gameStore = useGameStore()
    const router = useRouter()

    // [수정일: 2026-01-31] Web Worker 초기화 (Pyodide 엔진) - 안전한 초기화
    let pythonWorker = null
    try {
        pythonWorker = new Worker('/scripts/pyodideWorker.js')
    } catch (e) {
        console.error("Worker initialization failed:", e)
    }

    // --- Logic & Data Integration ---
    const currentQuestIdx = computed(() => gameStore.selectedQuestIndex || 0)
    const currentQuest = computed(() => aiQuests[currentQuestIdx.value] || aiQuests[0])

    // --- State ---
    const currentStep = ref(1)
    const userScore = reactive({ step1: 0, step2: 0, step3: 0, step4: 0 })
    const pseudoInput = ref('')

    const chatMessages = ref([
        { sender: 'Lion', text: '엔지니어님, 깨어나셨군요. 오염된 데이터를 정화해야 제 기억이 돌아옵니다. 오른쪽 패널에 한글로 로직을 설계해주세요.' }
    ])
    const chatContainer = ref(null)

    const blocks = [
        { id: 'b1', text: 'continue' },
        { id: 'b2', text: 'break' },
        { id: 'b3', text: 'append(text)' },
        { id: 'b4', text: 'remove(text)' }
    ]
    const selectedBlock = ref(null)
    const pythonInput = ref('') // Step 3 직접 코드 입력을 위한 변수
    const simulationOutput = ref('')
    const simulationContainer = ref(null)
    const isSimulating = ref(false)
    const isEvaluating = ref(false)
    const isSuccess = ref(false) // 단계 성공 여부 추적
    const step4Options = computed(() => currentQuest.value.step4Options || [])

    // 코드 스니펫 삽입 기능 (초보자 지원) - 주석(# TODO)을 감지하여 스마트하게 삽입
    const insertSnippet = (snippet) => {
        const lines = pythonInput.value.split('\n')
        let targetIndex = -1

        // 첫 번째 만나는 # TODO 주석을 찾음
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].includes('# TODO')) {
                targetIndex = i
                break
            }
        }

        if (targetIndex !== -1) {
            // 해당 라인의 인덴트(공백)를 유지하며 코드 삽입
            const indent = lines[targetIndex].match(/^\s*/)[0]
            lines[targetIndex] = `${indent}${snippet}`
            pythonInput.value = lines.join('\n')
        } else {
            // 주석이 없으면 맨 뒤에 추가
            pythonInput.value += `\n${snippet}`
        }
    }

    const feedbackModal = reactive({
        visible: false,
        title: '',
        desc: '',
        details: '',
        isSuccess: true
    })

    // Monaco Editor Options - 가독성 향상을 위해 폰트 크기 및 줄 간격 최적화
    const editorOptions = {
        minimap: { enabled: false },
        fontSize: 22,
        lineHeight: 36,
        theme: 'vs-dark',
        lineNumbers: 'on',
        renderLineHighlight: 'all',
        scrollbar: {
            vertical: 'visible',
            horizontal: 'visible',
            verticalSliderSize: 6,
            horizontalSliderSize: 6
        },
        wordWrap: 'on',
        padding: { top: 24, bottom: 24 },
        fontFamily: "'Fira Code', 'Nanum Gothic Coding', monospace",
        fontLigatures: true,
        automaticLayout: true,
        suggestOnTriggerCharacters: true,
        folding: true,
        roundedSelection: true
    }

    // 퀘스트 변경 시 상태 초기화
    watch(currentQuest, (newQuest) => {
        if (newQuest) {
            currentStep.value = 1
            pythonInput.value = '' // 퀘스트 변경 시 코드 비우기 (3단계 진입 시 템플릿 로드 유도)
            simulationOutput.value = ''
            isSuccess.value = false

            // 챗봇용 퀘스트 정보 업데이트
            chatMessages.value = [
                { sender: 'Lion', text: `안녕하세요! 오늘의 미션은 [${newQuest.title}]입니다. ${newQuest.desc}` }
            ]
        }
    }, { immediate: true })

    // 단계(Step) 변경 시 로직
    watch(currentStep, (newStep) => {
        // 3단계(Python 코딩) 진입 시 템플릿 로드
        if (newStep === 3 && !pythonInput.value) {
            pythonInput.value = currentQuest.value.pythonTemplate || ''
        }

        // 단계 정답 여부 초기화
        isSuccess.value = false
    }, { immediate: true })

    // [수정일: 2026-01-31] Lion Agent: 지능형 휴면 감지 및 능동적 가이드 로직
    const inactivityTimer = ref(null)
    const resetInactivityTimer = () => {
        if (inactivityTimer.value) clearTimeout(inactivityTimer.value)
        inactivityTimer.value = setTimeout(nudgeUser, 30000) // 30초 휴면 시 발동
    }

    const nudgeUser = () => {
        let nudgeText = ""
        const code = (currentStep.value === 2) ? pseudoInput.value : pythonInput.value

        if (currentStep.value === 2) {
            if (!code.includes('만약')) nudgeText = "엔지니어님, 광고를 걸러내기 위한 '만약(if)' 조건문이 필요해 보입니다."
            else if (!code.includes('반복')) nudgeText = "데이터가 여러 개이니 '반복' 구조를 먼저 설계해보는 건 어떨까요?"
            else nudgeText = "설계가 막히셨나요? '제거'하거나 '저장'하는 로직을 구체화해보세요!"
        } else if (currentStep.value === 3) {
            if (!code.includes('for')) nudgeText = "파이썬의 'for news in news_list:' 문법을 활용해 데이터를 하나씩 꺼내보세요."
            else if (!code.includes('if')) nudgeText = "필터링의 핵심은 'if' 조건문입니다. 5자 미만이나 '광고' 단어를 체크해보세요."
            else if (!code.includes('append')) nudgeText = "정화된 데이터를 'cleaned_data.append(news)'로 저장하는 것을 잊지 마세요!"
            else nudgeText = "코드가 거의 완성된 것 같습니다. 상단의 '코드 실행 및 검증' 버튼을 눌러보시겠어요?"
        }

        if (nudgeText && !chatMessages.value.some(m => m.text === nudgeText)) {
            chatMessages.value.push({
                sender: 'Lion',
                text: nudgeText,
                isNudge: true
            })
            scrollToBottom()
        }
    }

    watch([pseudoInput, pythonInput, currentStep], () => {
        resetInactivityTimer()
    }, { immediate: true })

    onUnmounted(() => {
        if (inactivityTimer.value) clearTimeout(inactivityTimer.value)
        if (pythonWorker) pythonWorker.terminate()
    })

    watch(pseudoInput, (newVal) => {
        if (newVal.length > 10 && !chatMessages.value.some(m => m.text.includes('시작'))) {
            chatMessages.value.push({ sender: 'Lion', text: '좋습니다. 먼저 데이터를 하나씩 꺼내는 "반복" 구조가 필요해 보입니다.' })
            scrollToBottom()
        }
        if (newVal.includes('만약') && !chatMessages.value.some(m => m.text.includes('조건'))) {
            chatMessages.value.push({ sender: 'Lion', text: '조건문을 잘 작성하고 계시군요. "제거"하거나 "저장"하는 행동도 명시해주세요.' })
            scrollToBottom()
        }
    })

    // --- Methods ---
    const scrollToBottom = () => {
        nextTick(() => {
            if (chatContainer.value) {
                chatContainer.value.scrollTop = chatContainer.value.scrollHeight
            }
        })
    }

    const handleStep1Submit = (idx) => {
        const isCorrect = currentQuest.value.quizOptions[idx].correct
        userScore.step1 = isCorrect ? 25 : 0
        showFeedback(
            isCorrect ? "✅ 정답: GIGO 원칙의 이해" : "⚠️ 오답: 다시 생각해보세요",
            isCorrect ? "훌륭합니다. '쓰레기가 들어가면 쓰레기가 나온다(Garbage In, Garbage Out)'는 AI 엔지니어링의 제1원칙입니다. 아무리 좋은 모델도 데이터가 더러우면 소용없습니다." : "데이터의 양보다는 '질'이 우선입니다. 노이즈가 섞인 데이터는 모델의 판단력을 흐리게 만듭니다.",
            "활용 사례: 실제 현업에서도 전체 프로젝트 기간의 80%를 데이터 전처리에 사용합니다. 금융 사기 탐지 모델에서 정상 거래를 사기로 오해하지 않게 하려면 노이즈 제거가 필수적입니다.",
            isCorrect
        )
    }

    const submitStep2 = async () => {
        const code = pseudoInput.value.trim()
        if (code.length < 5) {
            showFeedback("⚠️ 입력 부족", "의사코드를 조금 더 상세히 작성해주세요.", "최소 5자 이상 작성해야 분석이 가능합니다.", false)
            return
        }

        const hasLoop = /(반복|하나씩|꺼내|for|each)/.test(code)
        const hasCondition = /(만약|일 때|if|경우)/.test(code)
        const hasAction = /(제거|삭제|추가|저장|append|remove|continue)/.test(code)

        const loopIdx = code.search(/(반복|하나씩|for|each)/)
        const condIdx = code.search(/(만약|if|경우)/)
        const actionIdx = code.search(/(제거|삭제|추가|저장|append|remove|continue)/)

        if (hasLoop && hasCondition && hasAction) {
            if (actionIdx < loopIdx && actionIdx < condIdx) {
                showFeedback("🤔 논리 순서 불분명", "행동(제거/저장)이 조건보다 앞에 나옵니다.", "실제 실행 순서에 맞춰 의사코드를 작성해보세요.", false)
                return
            }
        }

        isEvaluating.value = true
        chatMessages.value.push({ sender: 'Lion', text: '흐음... 잠시만 기다려주세요. 엔지니어님의 논리 엔진을 정밀 분석 중입니다...' })
        scrollToBottom()

        try {
            const response = await axios.post('/api/core/ai-evaluate/', {
                quest_title: currentQuest.value.title,
                user_logic: code,
                score: 0,
            }, { withCredentials: true })

            const result = response.data
            userScore.step2 = result.score || 0

            const metricsHtml = result.metrics ? `
        <div class="grid grid-cols-5 gap-2 my-4">
          ${Object.entries(result.metrics).map(([key, val]) => `
            <div class="text-center p-2 bg-white/5 border border-white/10 rounded">
              <div class="text-[8px] text-gray-500 uppercase font-black">${key}</div>
              <div class="text-xs font-bold ${val > 70 ? 'text-cyan-400' : 'text-pink-400'}">${val}</div>
            </div>
          `).join('')}
        </div>
      ` : ''

            const feedbackHtml = `
        <div class="space-y-4">
          <div class="p-4 bg-cyan-500/10 border border-cyan-500/20 rounded-xl italic text-gray-200">
            "${result.analysis || result.feedback}"
          </div>
          ${metricsHtml}
          <div class="mt-4 pt-4 border-t border-white/10 text-lg">
            <p class="text-cyan-400 font-bold italic">Lion의 조언: ${result.advice || "훌륭한 접근입니다!"}</p>
          </div>
        </div>
      `

            showFeedback(
                result.is_logical ? "💡 AI 논리 분석 완료" : "🔧 논리 보완 필요",
                "복구 엔진이 의사코드를 정밀 분석했습니다.",
                feedbackHtml,
                result.is_logical
            )
        } catch (error) {
            console.error("AI Evaluation Failed:", error)
            const oldScore = (hasLoop ? 6 : 0) + (hasCondition ? 6 : 0) + (hasAction ? 6 : 0) + 7
            userScore.step2 = oldScore
            showFeedback("🦁 Lion의 간이 평가", "통신 장애로 인해 간이 분석기로 대체합니다.", "논리 키워드 기반으로 분석되었습니다.", true)
        } finally {
            isEvaluating.value = false
        }
    }

    const selectBlock = (block) => { selectedBlock.value = block }

    // fillBlank 및 pythonBlanks 는 Monaco Editor 도입으로 더 이상 사용하지 않으므로 제거합니다.

    const submitStep3 = () => {
        const code = pythonInput.value
        const hasContinue = code.includes('continue')
        const hasAppend = code.includes('append(news)')
        const hasPass = code.includes('pass')
        const hasBreak = code.includes('break')

        let score = 0
        let details = '<div class="space-y-2"><p><strong>분석 결과:</strong></p>'

        // 논리적 정확성 체크
        if (hasContinue) {
            score += 12
            details += '<p class="text-green-400">✓ 필터링 조건 시 continue를 사용하여 효율적으로 데이터를 건너뛰었습니다.</p>'
        } else if (hasPass) {
            score += 8
            details += '<p class="text-yellow-400">! pass를 사용했습니다. 로직은 작동하지만 continue가 더 명확할 수 있습니다.</p>'
        } else if (hasBreak) {
            score += 5
            details += '<p class="text-pink-400">✗ break는 반복문을 완전히 멈춥니다. 남은 데이터를 검사하지 못하게 됩니다.</p>'
        }

        if (hasAppend) {
            score += 13
            details += '<p class="text-green-400">✓ valid한 데이터를 cleaned_data에 성공적으로 저장했습니다.</p>'
        }

        details += '</div>'

        userScore.step3 = score
        showFeedback(
            score >= 20 ? "🐍 파이썬 구현: 완벽함" : "🐍 파이썬 구현: 로직 보완 필요",
            score >= 20 ? "논리를 코드로 완벽하게 변환하셨습니다." : "일부 로직이 의도와 다르게 동작할 수 있습니다.",
            details,
            score >= 20
        )
    }

    const runSimulation = () => {
        const code = pythonInput.value

        if (code.length < 50) {
            simulationOutput.value = '<span class="text-pink-500">Error: 코드가 너무 짧습니다. 템플릿의 형식을 유지해주세요.</span>'
            return
        }

        isSimulating.value = true
        simulationOutput.value = '<span class="text-cyan-500 font-black animate-pulse">AI-GYM Sandbox Environment Initializing...</span><br>'

        // 실제 파이썬 코드 실행을 위한 래핑
        // 1. 유저의 함수 정의 
        // 2. target_data(worker에서 주입됨)를 인자로 함수 호출 및 결과 출력
        const wrappedCode = `
${code}

try:
    result = clean_news_data(target_data)
    print(f"[SYSTEM_RESULT]: {result}")
except Exception as e:
    print(f"[SYSTEM_ERROR]: {str(e)}")
`

        if (!pythonWorker) {
            simulationOutput.value = '<span class="text-pink-500">Error: Python 엔진 초기화에 실패했습니다. 관리자에게 문의하세요.</span>'
            isSimulating.value = false
            return
        }

        pythonWorker.postMessage({
            code: wrappedCode,
            data: currentQuest.value.sampleData || []
        })

        pythonWorker.onmessage = (event) => {
            const { success, output, error } = event.data
            let log = '<span class="text-cyan-400 font-black tracking-widest uppercase text-[10px] italic">Executing cleaner_module.py on Pyodide_Runtime...</span><br><br>'

            if (success) {
                // 특정 색상 입히기
                const formattedOutput = output
                    .replace(/\[SYSTEM_RESULT\]:/g, '<strong class="text-white bg-cyan-700/30 px-2 py-1 italic tracking-widest uppercase text-[10px]">EXEC_COMPLETED:</strong>')
                    .replace(/\n/g, '<br>')

                log += `<div class="font-mono text-gray-300 leading-relaxed">${formattedOutput}</div>`

                // 성공 시 자동으로 다음 단계 평가 진행 (실제로 결과가 나왔으므로)
                setTimeout(() => {
                    submitStep3()
                }, 1000)
            } else {
                log += `<div class="text-pink-500 font-mono p-4 bg-pink-500/10 border border-pink-500/20 rounded-lg">
                    <p class="font-black mb-2 uppercase text-xs">Runtime_Execution_Error</p>
                    <p class="text-sm">${error}</p>
                </div>`
            }

            simulationOutput.value = log
            isSimulating.value = false

            nextTick(() => {
                if (simulationContainer.value) {
                    simulationContainer.value.scrollTop = simulationContainer.value.scrollHeight
                }
            })
        }
    }

    const handleStep4Submit = (idx) => {
        const isCorrect = idx === 1
        userScore.step4 = isCorrect ? 25 : 0
        showFeedback(
            isCorrect ? "⚖️ 심화 분석: 트레이드오프" : "🤔 심화 분석: 다시 생각해보세요",
            isCorrect ? "정답입니다. 너무 엄격한 필터링은 유용한 데이터까지 버릴 수 있습니다(False Positive)." : "아닙니다. 필터링을 너무 강하게 하면 오히려 데이터 부족 현상이 발생할 수 있습니다.",
            "활용 사례: 스팸 메일 필터가 너무 강력하면, 중요한 업무 메일까지 스팸통으로 들어가는 것과 같습니다. 엔지니어는 항상 '정확도'와 '재현율' 사이의 균형을 맞춰야 합니다.",
            isCorrect
        )
    }

    const showFeedback = (title, desc, details, isSuccess) => {
        feedbackModal.title = title
        feedbackModal.desc = desc
        feedbackModal.details = details
        feedbackModal.isSuccess = isSuccess
        feedbackModal.visible = true
    }

    const nextStep = () => {
        feedbackModal.visible = false
        if (currentStep.value < 5) currentStep.value++
    }

    const reloadApp = () => location.reload()

    const finalReviewText = computed(() => {
        let review = `엔지니어님은 데이터가 AI 모델에 미치는 영향을 정확히 이해하고 있습니다. `
        review += userScore.step2 >= 20 ? "수도코드를 통한 논리 구조화 능력이 뛰어나며, " : "수도코드 작성에 조금 더 연습이 연습이 필요해 보이지만, "
        review += userScore.step3 >= 20 ? "파이썬 코드로의 변환 능력도 훌륭합니다." : "코드 구현 디테일을 조금만 더 다듬으면 훌륭한 엔지니어가 될 것입니다."
        review += "<br/><br/>이제 오염된 데이터가 제거되었으니, 다음 스테이지(RAG 시스템 구축)로 나아갈 준비가 되었습니다."
        return review
    })


    return {
        currentQuest,
        currentStep,
        userScore,
        pseudoInput,
        pythonInput, // 추가
        chatMessages,
        chatContainer,
        blocks,
        selectedBlock,
        simulationOutput,
        simulationContainer,
        isSimulating,
        isEvaluating,
        isSuccess,
        step4Options,
        feedbackModal,
        editorOptions,
        finalReviewText,
        handleStep1Submit,
        submitStep2,
        selectBlock,
        runSimulation,
        handleStep4Submit,
        nextStep,
        reloadApp,
        insertSnippet // 추가
    }
}
