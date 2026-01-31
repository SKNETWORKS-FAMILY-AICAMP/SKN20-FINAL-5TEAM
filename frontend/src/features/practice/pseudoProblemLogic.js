/**
 [수정일: 2026-01-31]
 내용: pseudoProblem.vue의 로직을 Composable 패턴으로 분리
*/
import { ref, reactive, computed, watch, nextTick } from 'vue'
import {
    Terminal,
    Cpu,
    Code as CodeIcon,
    Award,
    RotateCcw,
    ChevronRight,
    AlertTriangle,
    CheckCircle,
    X
} from 'lucide-vue-next'
import { useGameStore } from '@/stores/game'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { aiQuests } from './support/unit1/logic-mirror/data/stages.js'

export function usePseudoProblem(props, emit) {
    const gameStore = useGameStore()
    const router = useRouter()

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
    const pythonBlanks = reactive({ blankA: null, blankB: null })
    const simulationOutput = ref('')
    const simulationContainer = ref(null)
    const isSimulating = ref(false)
    const isEvaluating = ref(false)

    const sampleData = [
        "삼성전자 주가 급등",
        "광고) 지금 바로 클릭하세요",
        "날씨",
        "AI 모델의 미래 전망",
        "초특가 광고 상품 안내"
    ]

    const step4Options = [
        "'광고' 단어가 포함된 모든 문서를 무조건 삭제한다.",
        "단순 키워드 매칭 대신, 문맥을 이해하는 AI 모델을 사용하여 필터링한다.",
        "데이터 전처리를 아예 하지 않는다.",
        "사람이 모든 데이터를 직접 읽고 지운다."
    ]

    const feedbackModal = reactive({
        visible: false,
        title: '',
        desc: '',
        details: '',
        isSuccess: true
    })

    // Monaco Editor Options
    const editorOptions = {
        minimap: { enabled: false },
        fontSize: 20,
        lineHeight: 32,
        theme: 'vs-dark',
        lineNumbers: 'on',
        scrollbar: {
            vertical: 'visible',
            horizontal: 'visible',
            verticalSliderSize: 6,
            horizontalSliderSize: 6
        },
        wordWrap: 'on',
        padding: { top: 20, bottom: 20 },
        fontFamily: "'Nanum Gothic Coding', monospace",
        automaticLayout: true,
        suggestOnTriggerCharacters: true,
        folding: true,
        roundedSelection: true
    }

    // --- Watchers ---
    watch(currentQuest, (newQuest) => {
        if (newQuest && newQuest.cards) {
            currentStep.value = 1
            pythonBlanks.blankA = null
            pythonBlanks.blankB = null
            simulationOutput.value = ''
            if (pseudoInput.value !== undefined) {
                pseudoInput.value = ''
            }
        }
    }, { immediate: true })

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
    const fillBlank = (blankId) => {
        if (!selectedBlock.value) return
        pythonBlanks[blankId] = selectedBlock.value
        selectedBlock.value = null
    }

    const submitStep3 = () => {
        const val = currentQuest.value.codeValidation
        const bA = pythonBlanks.blankA?.text === (currentQuestIdx.value === 0 ? 'continue' : val.fee1)
        const bB = pythonBlanks.blankB?.text === (currentQuestIdx.value === 0 ? 'append(text)' : val.fee2)
        let score = 0
        if (bA) score += 12
        if (bB) score += 13

        userScore.step3 = score
        showFeedback(
            score === 25 ? "🐍 파이썬 구현: 완벽함" : "🐍 파이썬 구현: 일부 오류",
            score === 25 ? "논리를 코드로 완벽하게 변환하셨습니다." : "일부 로직이 의도와 다르게 동작할 수 있습니다.",
            `<div class="space-y-2"><p><strong>설명:</strong></p><p>1. <code>continue</code>는 현재 반복을 건너뛰고 다음 데이터로 넘어갑니다.</p><p>2. 유효한 데이터만 리스트에 <code>append</code> 해야 메모리를 효율적으로 사용합니다.</p></div>`,
            score > 15
        )
    }

    const runSimulation = () => {
        const bA = pythonBlanks.blankA?.text
        const bB = pythonBlanks.blankB?.text

        if (!bA || !bB) {
            simulationOutput.value = '<span class="text-pink-500">Error: 빈칸을 모두 채워야 실행할 수 있습니다.</span>'
            return
        }

        isSimulating.value = true
        simulationOutput.value = '<span class="text-cyan-500">Initializing cleaning_protocol.v3...</span><br>'

        let cleaned_data = []
        let log = '<span class="text-cyan-400 font-black tracking-widest uppercase text-[10px] italic">Checking system_integrity_protocol...</span><br>'

        for (let news of sampleData) {
            log += `<span class="text-gray-500 italic mt-2">Checking_Node: "${news}"</span><br>`
            if (news.length < 5 || news.includes("광고")) {
                if (bA === 'continue') {
                    log += `<span class="text-yellow-500 font-mono">&nbsp;&nbsp;[PROT_SKIP]: 필터링 조건 일치.</span><br>`
                    continue
                } else if (bA === 'break') {
                    log += `<span class="text-red-500 font-mono">&nbsp;&nbsp;[PROT_HALT]: 반복문 강제 종료됨.</span><br>`
                    break
                }
            }
            if (bB === 'append(text)') {
                cleaned_data.push(news)
                log += `<span class="text-green-500 font-mono">&nbsp;&nbsp;[DATA_SAVE]: 데이터가 cleaned_data에 커밋됨.</span><br>`
            }
        }

        log += `<br><strong class="text-white bg-cyan-700/30 px-2 py-1 italic tracking-widest uppercase text-[10px]">SYNC_COMPLETED: [${cleaned_data.join(', ')}]</strong>`

        setTimeout(() => {
            simulationOutput.value = log
            isSimulating.value = false
            nextTick(() => {
                if (simulationContainer.value) simulationContainer.value.scrollTop = simulationContainer.value.scrollHeight
            })
            submitStep3()
        }, 800)
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
        chatMessages,
        chatContainer,
        blocks,
        selectedBlock,
        pythonBlanks,
        simulationOutput,
        simulationContainer,
        isSimulating,
        isEvaluating,
        step4Options,
        feedbackModal,
        editorOptions,
        finalReviewText,
        handleStep1Submit,
        submitStep2,
        selectBlock,
        fillBlank,
        runSimulation,
        handleStep4Submit,
        nextStep,
        reloadApp,
        // 아이콘들도 템플릿에서 component :is로 쓸 수 있게 반환
        Terminal, Cpu, CodeIcon, Award, RotateCcw, ChevronRight, AlertTriangle, CheckCircle, X
    }
}
