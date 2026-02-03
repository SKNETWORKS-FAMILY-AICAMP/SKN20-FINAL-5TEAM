/**
 * [수정일: 2026-01-31]
 * [수정내용:
 * 1. 캐릭터 명칭 및 아이콘 변경 (Lion 🦁 -> Coduck 🦆)
 * 2. 챗봇 가이드 및 피드백 텍스트의 캐릭터 브랜딩 고도화
 * 3. AI 상담 모드(askCoduck) 도입 및 통합]
 */
import { ref, reactive, computed, watch, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import axios from 'axios'
import { tts } from '@/utils/tts'
import { useAuthStore } from '@/stores/auth'
import { aiQuests } from './support/unit1/logic-mirror/data/stages.js'

export function usePseudoProblem(props, emit) {
    const gameStore = useGameStore()
    const authStore = useAuthStore()
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

    // [수정일: 2026-02-02] 선언 순서 조정: 의존성 있는 변수들을 최상단으로 이동
    const userNickname = computed(() => authStore.sessionNickname || 'ENGINEER')

    const replaceUsername = (text) => {
        if (!text) return text
        return text.replace(/{username}/g, userNickname.value)
    }

    const currentQuest = computed(() => {
        const stage = aiQuests.find(q => q.id === (currentQuestIdx.value + 1))
        if (!stage) return aiQuests[0]

        // 데이터 내의 {username}을 실제 닉네임으로 치환하여 반환
        const processedStage = JSON.parse(JSON.stringify(stage))

        const deepReplace = (obj) => {
            for (let key in obj) {
                if (typeof obj[key] === 'string') {
                    obj[key] = replaceUsername(obj[key])
                } else if (typeof obj[key] === 'object' && obj[key] !== null) {
                    deepReplace(obj[key])
                }
            }
        }

        deepReplace(processedStage)
        return processedStage
    })

    const synopsisText = computed(() => ({
        top: `PROGRAM: INITIALIZING_REBOOT_PROTOCOL\nYEAR: 2077\nLOCATION: MOTHER_SERVER_CORE`,
        main: [
            "서기 2077년, 인류를 관리하던 '마더 서버'가 오염되었습니다.",
            "AI들은 현실을 왜곡하는 '환각(Hallucination)'과 '오버피팅'에 빠져 통제를 벗어났습니다.",
            "대부분의 엔지니어는 기술을 잃었지만, 당신은 유일한 '아키텍처 복구자(Architect)'입니다.",
            "파트너 'Coduck'과 함께 붕괴된 데이터 구역을 하나씩 정화하고 시스템을 재부팅해야 합니다."
        ],
        bottom: `WELCOME BACK, ARCHITECT: ${userNickname.value}`
    }))

    // --- State ---
    const currentStep = ref(0) // [수정일: 2026-02-01] 0단계(시놉시스)부터 시작
    // [수정일: 2026-02-03] 점수 키 명칭을 UI와 일관되게 CONCEPT, LOGIC, CODE, ARCH로 통일
    const userScore = reactive({ CONCEPT: 0, LOGIC: 0, CODE: 0, ARCH: 0 })
    const pseudoInput = ref('')

    // [수정일: 2026-01-31] 캐릭터 명칭 동적 참조
    const charName = computed(() => currentQuest.value.character?.name || 'Coduck')

    const chatMessages = ref([
        { sender: 'Coduck', text: `...지...지지직... 아키텍처님? 제 음성 모듈이... 드디어 연결되었습니다. Architect ${userNickname.value}님, 절 깨워주셔서 감사합니다.` }
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
    const isAsking = ref(false) // AI에게 질문 중인지 여부
    // [수정일: 2026-02-03] 게이트키퍼 강화를 위한 상태 변수 추가
    const isConsulted = ref(false) // 최소 1회 상담 여부
    const isApproved = ref(false)  // AI 논리 승인 여부
    const isSuccess = ref(false) // 단계 성공 여부 추적

    // [수정일: 2026-02-02] UI 고도화를 위한 새로운 상태 추가
    const integrity = ref(0) // 시스템 가동률
    const recoveredArtifacts = ref([]) // 복구된 아티팩트 목록

    // [수정일: 2026-02-03] 캐릭터 표정 상태 관리 통합
    const currentDuckImage = ref(currentQuest.value.character?.image || '/assets/characters/coduck.png')

    const isMuted = ref(false)
    const isPlayingBGM = ref(false)
    const synopsisAudio = ref(null)
    let synopsisTimer = null // [수정일: 2026-02-03] 누락된 타이머 변수 선언 추가

    const toggleMute = () => {
        isMuted.value = !isMuted.value
        // [수정일: 2026-02-01] BGM에도 음소거 적용
        if (synopsisAudio.value) {
            synopsisAudio.value.muted = isMuted.value
        }
        tts.toggleMute()
    }

    // [수정일: 2026-01-31] 인터랙티브 인터뷰(Stage 1) 상태 변수 추가
    const currentInterviewIdx = ref(0)
    const interviewResults = ref([])
    const currentInterviewQuestion = computed(() => {
        const questions = currentQuest.value.interviewQuestions || []
        return questions[currentInterviewIdx.value] || null
    })


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


    const skipSynopsis = () => {
        if (synopsisAudio.value) {
            synopsisAudio.value.pause()
            synopsisAudio.value.currentTime = 0
        }
        isPlayingBGM.value = false
        tts.stop()
        currentStep.value = 1
    }



    // [수정일: 2026-01-31] Coduck Agent: 지능형 휴면 감지 및 능동적 가이드 로직
    const inactivityTimer = ref(null)
    const resetInactivityTimer = () => {
        if (inactivityTimer.value) clearTimeout(inactivityTimer.value)
        // [수정일: 2026-01-31] 사용자 피드백 반영: 넛지 딜레이 단축 (30초 -> 15초)
        inactivityTimer.value = setTimeout(nudgeUser, 15000)
    }

    // [수정일: 2026-01-31] nudgeUser 고도화: 사용자가 이미 구현한 논리를 인식하여 중복 가이드를 방지하고 칭찬과 다른 힌트를 제공
    const nudgeUser = () => {
        const questions = currentQuest.value.interviewQuestions || []
        if (currentStep.value === 1 && questions.length > 0) return

        let nudgeText = ""
        const code = (currentStep.value === 2) ? pseudoInput.value : pythonInput.value

        // [수정일: 2026-01-31] 상세 논리 상태 분석
        const getCompleteness = (txt, type) => {
            if (!txt) return { score: 0, hasLoop: false, hasCondition: false, hasAction: false }
            let s = 0
            const state = {
                hasLoop: type === 'pseudo' ? /(반복|하나씩|for|each)/.test(txt) : /for\s+\w+\s+in\s+/.test(txt),
                hasCondition: type === 'pseudo' ? /(만약|일 때|if|경우)/.test(txt) : /if\s+/.test(txt),
                hasAction: type === 'pseudo' ? /(제거|삭제|추가|저장|기록|append|remove|continue|clean)/.test(txt) : (/\.append\(/.test(txt) || /continue/.test(txt))
            }
            if (state.hasLoop) s += 30
            if (state.hasCondition) s += 30
            if (state.hasAction) s += 30
            if (txt.length > (type === 'pseudo' ? 50 : 100)) s += 10
            return { score: s, ...state }
        }

        const stats = getCompleteness(code, currentStep.value === 2 ? 'pseudo' : 'python')

        if (stats.score >= 90) {
            const compliments = [
                "캬! 논리 구조가 완벽합니다. 이제 제출해서 결과를 확인해볼까요?",
                "굉장히 훌륭한 로직이네요! 제가 더 가이드할 게 없어서 심심할 정도예요. 꽥!",
                "엔지니어님의 설계 능력이 대단합니다. 바로 실행 엔진으로 돌려보고 싶어요."
            ]
            nudgeText = compliments[Math.floor(Math.random() * compliments.length)]
        } else if (currentStep.value === 2) {
            if (!stats.hasLoop) {
                nudgeText = "데이터를 하나씩 살펴봐야 해요. '반복'해서 확인하는 구조를 먼저 잡아보면 어떨까요?"
            } else if (!stats.hasCondition) {
                nudgeText = "반복문은 아주 좋습니다! 이제 오염된 데이터를 판별할 '조건(만약~)'을 넣어볼까요?"
            } else if (!stats.hasAction) {
                nudgeText = "논리가 거의 완성됐어요. 조건을 만족했을 때 '삭제'하거나 '건너뛰는' 행동을 명시해주세요."
            }
        } else if (currentStep.value === 3) {
            if (!stats.hasLoop) {
                nudgeText = "파이썬의 'for'문을 사용해 리스트를 순회해보세요. 상단의 스니펫이 도움이 될 거예요."
            } else if (!stats.hasCondition) {
                nudgeText = "코드 뼈대가 튼튼하네요! 'if'문을 사용해 필터링 조건을 채워주시면 됩니다."
            } else if (!stats.hasAction) {
                nudgeText = "마지막 단계예요! 'continue'로 넘기거나 'append'로 저장하는 로직을 마무리해주세요. 꽥!"
            }
        }

        // 중복 답변 방지 및 상태 기반 출력
        if (nudgeText && !chatMessages.value.some(m => m.text === nudgeText)) {
            // "이미 ~하셨네요!" 식의 보강 (사용자가 이미 했다면 nudgeText를 위에서 다른 걸로 바꿨을 것이므로 여기서는 출력만)
            chatMessages.value.push({ sender: charName.value, text: nudgeText, isNudge: true })

            // [수정일: 2026-02-01] 오리가 참견할(Nudge) 때 음성 출력
            tts.speak(nudgeText);

            scrollToBottom()
        }
    }


    onUnmounted(() => {
        if (inactivityTimer.value) clearTimeout(inactivityTimer.value)
        if (pythonWorker) pythonWorker.terminate()
        cleanupAudio() // [수정일: 2026-02-03] 시놉시스 사운드 정리 통합
        if (synopsisTimer) clearTimeout(synopsisTimer)
    })

    // [수정일: 2026-01-31] 단순 키워드 와처는 지능형 넛지 시스템(nudgeUser)으로 통합하여 중복 방지

    // --- Methods ---
    const scrollToBottom = () => {
        nextTick(() => {
            if (chatContainer.value) {
                chatContainer.value.scrollTop = chatContainer.value.scrollHeight
            }
        })
    }

    // [수정일: 2026-01-31] handleStep1Submit 개편: 다단계 인터뷰 지원
    const handleStep1Submit = (option) => {
        const questions = currentQuest.value.interviewQuestions || []

        // 인터뷰 데이터가 없는 경우 기존 퀴즈 방식 호환
        if (questions.length === 0) {
            const isCorrect = option.correct
            userScore.CONCEPT = isCorrect ? 25 : 0
            showFeedback(
                isCorrect ? "✅ 정답: GIGO 원칙의 이해" : "⚠️ 오답: 다시 생각해보세요",
                isCorrect ? "훌륭합니다. '쓰레기가 들어가면 쓰레기가 나온다'는 AI 엔지니어링의 제1원칙입니다." : "데이터의 질이 모델의 성능을 결정합니다.",
                "전처리 과정의 중요성을 잊지 마세요.",
                isCorrect
            )
            return
        }

        // 인터뷰 진행
        const currentQ = questions[currentInterviewIdx.value]
        const isCorrect = option.correct

        if (isCorrect) {
            // [수정일: 2026-02-03] 캐릭터 표정 초기화 및 점수 반영
            currentDuckImage.value = currentQuest.value.character?.image
            integrity.value = Math.min(integrity.value + 15, 100)

            interviewResults.value.push({ questionId: currentQ.id, answer: option.text, isCorrect: true })
            chatMessages.value.push({ sender: 'User', text: option.text })
            chatMessages.value.push({ sender: 'Coduck', text: currentQ.coduckComment })
        } else {
            // [수정일: 2026-02-03] 오답 시 '나노바나나' Coduck 슬픈 표정 적용
            currentDuckImage.value = '/assets/characters/coduck_sad.png'
            interviewResults.value.push({ questionId: currentQ.id, answer: option.text, isCorrect: false })
            chatMessages.value.push({ sender: 'User', text: option.text })
            chatMessages.value.push({ sender: 'Coduck', text: currentQ.coduckComment })
        }

        // [수정일: 2026-02-01] 인터뷰 응답 낭독
        if (currentQ.coduckComment) {
            tts.speak(currentQ.coduckComment);
        }

        scrollToBottom()

        // 다음 질문 또는 단계로 이동
        if (currentInterviewIdx.value < questions.length - 1) {
            currentInterviewIdx.value++
        } else {
            // 인터뷰 종료: 합산 점수 계산 (만점 25)
            const correctCount = interviewResults.value.filter(r => r.isCorrect).length
            userScore.CONCEPT = Math.round((correctCount / questions.length) * 25)

            setTimeout(() => {
                // [수정일: 2026-02-02] 가동률 업데이트
                integrity.value = Math.min(integrity.value + 25, 100)

                showFeedback(
                    "📊 요구사항 분석 완료",
                    "Coduck과의 인터뷰를 통해 시스템 규격을 성공적으로 정의했습니다.",
                    "이제 정의된 규격을 바탕으로 의사코드를 설계해봅시다. (점수: " + userScore.CONCEPT + " / 25)",
                    true
                )
            }, 1000)
        }
    }

    // [수정일: 2026-02-03] Coduck에게 질문하기 (게이트키퍼 필수 관문)
    const askCoduck = async () => {
        const code = pseudoInput.value.trim()
        if (code.length < 5) {
            chatMessages.value.push({ sender: charName.value, text: '질문하시려면 먼저 로직을 조금 작성해주세요!' })
            scrollToBottom()
            return
        }

        isAsking.value = true
        isConsulted.value = true // [수정일: 2026-02-03] 상담 시도 기록
        chatMessages.value.push({ sender: 'User', text: '이 로직에 대해 피드백을 줄 수 있어?' })
        chatMessages.value.push({ sender: 'Coduck', text: '엔지니어님의 로직을 검토 중입니다... 잠시만요.' })
        scrollToBottom()

        try {
            const response = await axios.post('/api/core/ai-evaluate/', {
                quest_title: currentQuest.value.title,
                user_logic: code,
                mode: 'consult', // 단순 상담 모드 (점수 미반영)
            }, { withCredentials: true })

            const result = response.data

            // [수정일: 2026-02-03] AI의 논리적 타당성 판단에 따른 승인 처리
            // 백엔드에서 is_logical 또는 유사한 승인 플래그를 내려준다고 가정
            if (result.is_logical || (result.score && result.score >= 15)) {
                isApproved.value = true
            } else {
                isApproved.value = false
            }

            chatMessages.value.push({
                sender: 'Coduck',
                text: result.analysis || result.feedback || "논리적인 흐름이 좋습니다. 규칙을 빼먹지는 않았는지 다시 한번 확인해보세요!"
            })
        } catch (error) {
            chatMessages.value.push({ sender: 'Coduck', text: '통신 상태가 좋지 않아 지금은 상담이 어렵습니다. 하지만 계속 진행하실 수 있어요!' })
            // 통신 장애 시에는 학습 편의를 위해 임시 승인 처리
            isApproved.value = true
        } finally {
            isAsking.value = false
            scrollToBottom()
        }
    }

    const submitStep2 = async () => {
        const code = pseudoInput.value.trim()

        // [수정일: 2026-02-03] 게이트키퍼: AI 승인이 없는 경우 진행 차단
        if (!isApproved.value) {
            showFeedback(
                "⚠️ 아키텍처 승인 필요",
                "먼저 Coduck 컨설턴트에게 논리 검토를 받아야 합니다.",
                "우측 하단의 AI 컨설팅 HUD를 통해 '승인'을 획득하십시오.",
                false
            )
            return
        }

        if (code.length < 5) {
            showFeedback("⚠️ 입력 부족", "의사코드를 조금 더 상세히 작성해주세요.", "최소 5자 이상 작성해야 분석이 가능합니다.", false)
            return
        }

        const hasLoop = /(반복|하나씩|꺼내|for|each)/.test(code)
        const hasCondition = /(만약|일 때|if|경우)/.test(code)
        const hasAction = /(제거|삭제|추가|저장|append|remove|continue)/.test(code)

        // [수정일: 2026-01-31] 하드코딩된 순서 체크 제거 (자연어 표현의 다양성 존중)
        // 기존에는 '제거' 등의 키워드가 앞에 나오면 오류를 냈으나, 이제는 AI가 전체 맥락을 파악하도록 넘깁니다.

        isEvaluating.value = true;
        const analyzingText = `${charName.value === 'Coduck' ? '꽥! ' : ''}잠시만 기다려주세요. 엔지니어님의 논리 엔진을 정밀 분석 중입니다...`;
        chatMessages.value.push({ sender: charName.value, text: analyzingText })

        // [수정일: 2026-02-01] 분석 시작 안내 낭독
        tts.speak(analyzingText);

        scrollToBottom()

        try {
            const response = await axios.post('/api/core/ai-evaluate/', {
                quest_title: currentQuest.value.title,
                user_logic: code,
                score: 0,
            }, { withCredentials: true })

            const result = response.data || {}
            userScore.LOGIC = result.score || 10 // 기본 점수 보장

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
            <p class="text-cyan-400 font-bold italic">${charName.value}의 조언: ${result.advice || "훌륭한 접근입니다!"}</p>
          </div>
        </div>
      `

            showFeedback(
                result.is_logical ? "💡 AI 논리 분석 완료" : "🔧 논리 보완 필요",
                result.is_logical ? "복구 엔진이 의사코드를 정밀 분석했습니다." : "논리 구조를 조금 더 보강해야 할 것 같아요.",
                feedbackHtml,
                result.is_logical ?? (userScore.LOGIC >= 15) // is_logical이 없으면 점수 기반으로 결정
            )

            // [수정일: 2026-02-02] 가동률 업데이트
            if (result.is_logical || userScore.LOGIC >= 15) {
                // [수정일: 2026-02-03] 점수 키 변경 반영
                userScore.LOGIC = 25
                integrity.value = Math.max(integrity.value, 50)
                showFeedback("💡 논리 아키텍처 승인", "입력하신 의사코드가 정화 알고리즘으로 채택되었습니다. 이제 실제 코드로 변환하여 주입하십시오.", null, true)
            }
        } catch (error) {
            console.error("AI Evaluation Failed:", error)
            // [수정일: 2026-01-31] stats가 미정의된 상태에서 참조되는 오류 수정 (hasLoop 등 기존 정의된 변수 사용)
            const oldScore = (hasLoop ? 6 : 0) + (hasCondition ? 6 : 0) + (hasAction ? 6 : 0) + 7
            userScore.LOGIC = oldScore
            // [수정일: 2026-01-31] Quest 1(튜토리얼)의 경우 실습 편의를 위해 무조건 통과 허용
            const tutorialPass = currentQuest.value.id === 1 && (hasLoop || hasCondition || hasAction)
            showFeedback(
                `${charName.value}의 간이 평가`,
                "통신 장애로 인해 간이 분석기로 대체합니다.",
                "논리 키워드 기반으로 분석되었습니다.",
                tutorialPass || oldScore >= 15
            )
        } finally {
            isEvaluating.value = false
        }
    }

    const selectBlock = (block) => { selectedBlock.value = block }

    // fillBlank 및 pythonBlanks 는 Monaco Editor 도입으로 더 이상 사용하지 않으므로 제거합니다.

    // [수정일: 2026-02-03] 주석 제거 로직 (Comment Stripper)
    // 초보자가 주석에 키워드를 넣어 통과하는 것을 방지합니다.
    const stripComments = (code) => {
        if (!code) return ''
        // # 주석 제거
        let stripped = code.replace(/#.*$/gm, '')
        // """ 또는 ''' 독스트링 제거
        stripped = stripped.replace(/("""[\s\S]*?"""|'''[\s\S]*?''')/g, '')
        return stripped.trim()
    }

    const submitStep3 = (executionResult = null) => {
        // [수정일: 2026-02-03] 게이트키퍼: 최종 구현 제출 시에도 아키텍처 승인 여부 재검증
        if (!isApproved.value) {
            showFeedback(
                "⚠️ 아키텍처 권한 소실",
                "설계도(Step 2)가 수정되었거나 승인되지 않았습니다.",
                "이전 단계로 돌아가 아키텍처 컨설턴트의 승인을 다시 받으십시오.",
                false
            )
            return
        }

        const rawCode = pythonInput.value
        const strippedCode = stripComments(rawCode)
        const quest = currentQuest.value
        const v = quest.codeValidation || {}

        // [수정일: 2026-02-03] 초보자를 위한 상세 평가 로직
        let score = 0
        let details = '<div class="space-y-3">'

        // 1. 코드 존재 여부 체크
        if (strippedCode.length < 10) {
            details += `<p class="text-pink-400">✗ 유효한 코드가 너무 적습니다. 주석이 아닌 실제 실행 로직을 작성해주세요.</p>`
            showFeedback("⚠️ 코드 부족", "시스템을 복구하기 위한 유효한 코드가 부족합니다.", details + "</div>", false)
            return
        }

        // 2. 키워드 매칭 (주석 제외된 코드에서만 수행)
        const mainVar = v.price || 'data'
        const key1 = v.fee1 || 'continue'
        const key2 = v.fee2 || 'append'

        const hasKey1 = strippedCode.includes(key1)
        const hasKey2 = strippedCode.includes(key2)

        if (hasKey1) score += 5
        if (hasKey2) score += 5

        // 3. 실행 결과 검증 (I/O Matching)
        if (executionResult !== null) {
            const expected = JSON.stringify(quest.expectedOutput)
            const actual = JSON.stringify(executionResult)

            // 공백 제거 후 비교 (배열 내의 공백 등 미세 차이 무시)
            const isMatch = expected.replace(/\s/g, '') === actual.replace(/\s/g, '')

            if (isMatch) {
                score += 15
                details += `<p class="text-[#A3FF47]">✓ [SUCCESS] 실행 결과가 설계 아키텍처와 정확히 일치합니다.</p>`
                details += `<div class="p-2 bg-black/40 border border-[#A3FF47]/20 text-[10px] font-mono">
                                <span class="opacity-50">INPUT:</span> ${JSON.stringify(quest.sampleData)}<br/>
                                <span class="opacity-50">OUTPUT:</span> ${actual}
                            </div>`
            } else {
                const hint = quest.failHints?.logic_error || "결과값이 예상과 다릅니다."
                details += `<p class="text-pink-400">✗ [MISMATCH] ${hint}</p>`
                details += `<div class="p-2 bg-black/40 border border-pink-500/20 text-[10px] font-mono">
                                <span class="opacity-50">EXPECTED:</span> ${expected}<br/>
                                <span class="opacity-50">ACTUAL:</span> ${actual}
                            </div>`
            }
        } else {
            details += `<p class="text-amber-400">! 시뮬레이션 실행 결과가 없습니다. 'RE-BOOT SYSTEM'을 먼저 눌러주세요.</p>`
        }

        details += '</div>'
        userScore.CODE = score

        const isFullySuccess = score >= 20
        showFeedback(
            isFullySuccess ? "🐍 파이썬 구현: 아키텍처 정합성 승인" : "🐍 파이썬 구현: 설계 위반 감지",
            isFullySuccess ? "축하합니다! 코드가 논리적으로 무결하며 승인된 설계도와 완벽히 일치합니다." : "작성하신 로직이 Step 2에서 승인받은 아키텍처 설계 의도를 충분히 반영하지 못하고 있습니다.",
            details + `<p class="mt-4 text-[10px] opacity-40 italic">Architecture_Policy: 승인된 설계도와 구현체가 80% 이상 일치해야 최종 가동률이 보장됩니다.</p></div>`,
            isFullySuccess
        )

        if (isFullySuccess) {
            integrity.value = Math.min(integrity.value + 25, 100)
        }
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
        // [수정일: 2026-01-31] 하드코딩된 함수명 대신 stages.js의 functionName 사용
        const funcName = currentQuest.value.functionName || 'clean_news_data'
        // [수정일: 2026-02-03] 다중 인자 대응 로직 추가 (* spread)
        const wrappedCode = `
${code}

try:
    func = ${funcName}
    # 리스트의 리스트 형태이면서 인자가 여러 개인 특정 함수들 처리
    multi_arg_funcs = ["leakage_free_scaling", "monitor_drift_loss", "choose_smart_action"]
    if isinstance(target_data, list) and len(target_data) > 0 and isinstance(target_data[0], list) and "${funcName}" in multi_arg_funcs:
        result = func(*target_data)
    else:
        result = func(target_data)
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
                    // [수정일: 2026-02-03] 실제 결과값(output 내 SYSTEM_RESULT 이후의 값) 파싱
                    const resultMatch = output.match(/\[SYSTEM_RESULT\]:\s*([\s\S]*)$/)
                    let finalResult = null
                    if (resultMatch) {
                        try {
                            // Python의 리스트/딕셔너리 표현을 JSON처럼 파싱 시도 (단순 배열 형태 우선)
                            const resultStr = resultMatch[1].trim().replace(/'/g, '"')
                            finalResult = JSON.parse(resultStr)
                        } catch (e) {
                            console.error("Result parsing failed:", e)
                            finalResult = resultMatch[1].trim()
                        }
                    }
                    submitStep3(finalResult)
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
        // [수정일: 2026-01-31] 하드코딩된 정답 인덱스(idx === 1) 대신 데이터 기반(step4CorrectIdx) 사용
        const correctIdx = currentQuest.value.step4CorrectIdx ?? 0
        const isCorrect = idx === correctIdx
        userScore.ARCH = isCorrect ? 25 : 0

        // [수정일: 2026-01-31] 정답 시 다음 스테이지 자동 해금
        if (isCorrect) {
            gameStore.unlockNextStage('Pseudo Practice', currentQuestIdx.value)
        }

        // [수정일: 2026-01-31] 하드코딩된 피드백 텍스트 대신 stages.js의 데이터 사용
        const success = currentQuest.value.step4SuccessFeedback || {}
        const failure = currentQuest.value.step4FailFeedback || {}

        showFeedback(
            isCorrect ? (success.title || "⚖️ 심화 분석: 성공") : (failure.title || "🤔 심화 분석: 다시 생각해보세요"),
            isCorrect ? (success.desc || "정답입니다.") : (failure.desc || "다시 한번 고민해보세요."),
            isCorrect ? (success.details || "훌륭한 통찰입니다.") : (failure.details || "엔지니어링 사고방식으로 접근해 보세요."),
            isCorrect
        )

        if (idx === currentQuest.value.step4CorrectIdx) {
            // [수정일: 2026-02-03] 점수 키 변경 및 가동률 최대치 반영
            userScore.ARCH = 25
            integrity.value = 100

            const successText = (currentQuest.value.step4SuccessFeedback?.desc || "축하합니다! 해당 구역의 데이터 무결성이 확보되었습니다.").replace(/{username}/g, userNickname.value)
            const successDetails = currentQuest.value.step4SuccessFeedback?.details || "훌륭한 설계입니다. 마더 서버는 인류의 논리적인 접근에 반응하기 시작했습니다."

            showFeedback(currentQuest.value.step4SuccessFeedback?.title || "🔐 시스템 권한 회복", successText, successDetails, true)
        } else {
            // [수정일: 2026-02-03] 실패 시 캐릭터 표정 변경
            currentDuckImage.value = '/assets/characters/coduck_sad.png'
            showFeedback(currentQuest.value.step4FailFeedback?.title || "⚠️ 시스템 거부", currentQuest.value.step4FailFeedback?.desc || "결정적인 가치 정의 오류로 인해 최종 승인이 반려되었습니다.", currentQuest.value.step4FailFeedback?.details, false)
        }
    }

    const showFeedback = (title, desc, details, isSuccess) => {
        feedbackModal.title = title
        feedbackModal.desc = desc
        feedbackModal.details = details
        feedbackModal.isSuccess = isSuccess
        feedbackModal.visible = true

        // [수정일: 2026-02-01] 피드백 발생 시 설명(desc) 낭독
        if (desc) {
            tts.speak(desc);
        }
    }


    // [수정일: 2026-01-31] 단계 이동 함수 (Feedback Loop 지원)
    const goToStep = (step) => {
        if (step >= 1 && step <= 5) {
            currentStep.value = step
            feedbackModal.visible = false
        }
    }

    // [수정일: 2026-01-31] SPA 환경에 최적화된 미션 초기화 (새로고침 없이 상태만 리셋)
    const reloadApp = () => {
        currentStep.value = 1
        // [수정일: 2026-02-03] 점수 키 통일
        userScore.CONCEPT = 0
        userScore.LOGIC = 0
        userScore.CODE = 0
        userScore.ARCH = 0
        pseudoInput.value = ''
        pythonInput.value = currentQuest.value.pythonTemplate || ''
        simulationOutput.value = ''
        isSuccess.value = false
        currentInterviewIdx.value = 0
        interviewResults.value = []
        isEvaluating.value = false
        isAsking.value = false
        isSimulating.value = false
        integrity.value = 0 // [수정일: 2026-02-02] 가동률 초기화
        currentDuckImage.value = currentQuest.value.character?.image // [2026-02-03] 이미지 초기화

        chatMessages.value = [
            { sender: charName.value, text: `미션을 처음부터 다시 시작합니다.${charName.value === 'Coduck' ? ' 꽥!' : ''} 데이터 바다를 다시 정화해볼까요?` }
        ]

        feedbackModal.visible = false
        resetInactivityTimer()
        nextTick(() => {
            scrollToBottom()
        })
    }

    // [수정일: 2026-01-31] 다음 퀘스트로 직접 이동
    const goToNextQuest = () => {
        if (currentQuestIdx.value < aiQuests.length - 1) {
            gameStore.selectedQuestIndex++
            reloadApp() // 상태 초기화 후 새 퀘스트 로드
        }
    }

    const finalReviewText = computed(() => {
        let review = `엔지니어님은 데이터가 AI 모델에 미치는 영향을 정확히 이해하고 있습니다. `
        review += userScore.LOGIC >= 20 ? "수도코드를 통한 논리 구조화 능력이 뛰어나며, " : "수도코드 작성에 조금 더 연습이 필요해 보이지만, "
        review += userScore.CODE >= 20 ? "파이썬 코드로의 변환 능력도 훌륭합니다." : "코드 구현 디테일을 조금만 더 다듬으면 훌륭한 엔지니어가 될 것입니다."
        review += "<br/><br/>이제 오염된 데이터가 제거되었으니, 다음 스테이지(RAG 시스템 구축)로 나아갈 준비가 되었습니다."
        return review
    })


    // [수정일: 2026-02-03] 라이프사이클 및 오디오 관리 추가
    const nextStep = () => {
        feedbackModal.visible = false
        currentDuckImage.value = currentQuest.value.character?.image // 단계 전환 시 표정 초기화
        if (currentStep.value < 5) currentStep.value++
    }

    const initAudio = () => {
        if (!synopsisAudio.value) {
            synopsisAudio.value = new Audio('/assets/audio/synopsis_bgm.mp3')
            synopsisAudio.value.loop = true
            synopsisAudio.value.volume = 0.4
            synopsisAudio.value.muted = isMuted.value
        }

        synopsisAudio.value.play().then(() => {
            isPlayingBGM.value = true
        }).catch(err => console.log('BGM Autoplay blocked:', err))

        // [수정일: 2026-02-02] 로고 줌(9s) 이후 크롤링 시작(12s)에 맞춰 TTS 낭독 시작
        setTimeout(() => {
            if (currentStep.value === 0) {
                const fullText = synopsisText.value.main.join(' ');
                tts.speak(`${synopsisText.value.top}. ${fullText}. ${synopsisText.value.bottom}`);
            }
        }, 12000);

        if (synopsisTimer) clearTimeout(synopsisTimer);
        synopsisTimer = setTimeout(skipSynopsis, 80000);
    }

    const cleanupAudio = () => {
        if (synopsisAudio.value) {
            synopsisAudio.value.pause()
            synopsisAudio.value = null
        }
        tts.stop()
    }

    // --- Watchers & Lifecycle Hooks (Bottom for Hoisting Safety) ---

    watch(currentInterviewQuestion, (newQ) => {
        tts.stop();
        if (newQ && newQ.question) {
            tts.speak(newQ.question);
        }
    })

    watch(currentQuest, (newQuest) => {
        if (newQuest) {
            currentStep.value = 0
            pythonInput.value = ''
            simulationOutput.value = ''
            isSuccess.value = false
            currentInterviewIdx.value = 0
            interviewResults.value = []
            currentDuckImage.value = newQuest.character?.image || '/assets/characters/coduck.png'
            chatMessages.value = [
                { sender: 'Coduck', text: replaceUsername(`지..지직.. Architect님! [${newQuest.title}] 프로토콜을 감지했습니다. ${newQuest.desc}`) }
            ]
            if (currentStep.value === 1) {
                tts.speak(replaceUsername(`오늘의 미션은 ${newQuest.title}입니다. ${newQuest.desc}`));
            }
        }
    }, { immediate: true })

    watch(currentStep, (newStep) => {
        tts.stop();
        if (newStep === 1) {
            if (currentInterviewQuestion.value && currentInterviewQuestion.value.question) {
                tts.speak(currentInterviewQuestion.value.question);
            }
        }
        if (newStep === 0) {
            setTimeout(initAudio, 500);
        }
        if (newStep !== 0 && synopsisAudio.value) {
            synopsisAudio.value.pause()
            isPlayingBGM.value = false
        }
        if (newStep >= 2 && newStep <= 4) {
            const objective = currentQuest.value.missionObjective;
            if (objective) {
                tts.speak(objective);
            }
        }
        if (newStep === 3) {
            const userLogicHeader = pseudoInput.value
                ? `\"\"\"\n[엔지니어의 설계 가이드]\n${pseudoInput.value}\n\"\"\"\n\n`
                : ''
            if (!pythonInput.value || pythonInput.value === currentQuest.value.pythonTemplate) {
                pythonInput.value = userLogicHeader + (currentQuest.value.pythonTemplate || '')
            }
        }
        isSuccess.value = false
    }, { immediate: true })

    watch([pseudoInput, pythonInput, currentStep], () => {
        resetInactivityTimer()
    }, { immediate: true })

    // [수정일: 2026-02-03] 수도코드 변경 시 AI 승인 상태 리셋 (Gatekeeper)
    watch(pseudoInput, () => {
        if (isApproved.value) {
            isApproved.value = false
            // [참고] 사용자가 내용을 수정하면 다시 승인을 받아야 함을 알림
        }
    })

    return {
        currentQuest,
        currentStep,
        currentQuestIdx,
        userScore,
        pseudoInput,
        pythonInput,
        chatMessages,
        chatContainer,
        blocks,
        selectedBlock,
        simulationOutput,
        simulationContainer,
        isSimulating,
        isEvaluating,
        isAsking,
        isSuccess,
        currentInterviewIdx,
        currentInterviewQuestion,
        interviewResults,
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
        goToStep,
        reloadApp,
        goToNextQuest,
        insertSnippet,
        askCoduck,
        aiQuests,
        imageSrc: computed(() => currentDuckImage.value || currentQuest.value.character?.image || '/assets/characters/coduck.png'),
        isMuted,
        toggleMute,
        synopsisText,
        skipSynopsis,
        isPlayingBGM,
        recoveredArtifacts,
        currentDuckImage,
        initAudio,
        cleanupAudio,
        integrity,
        // [수정일: 2026-02-03] 게이트키퍼 상태 반환 추가
        isConsulted,
        isApproved
    }
}
