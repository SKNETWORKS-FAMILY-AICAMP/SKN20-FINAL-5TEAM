<!-- 
  수정일: 2026-01-28 
  내용: 3단계 퀘스트 시스템 구축 (Stage 7개 x Step 3개)
  - 스테이지별 심화/꼬리 질문 흐름 적용
  - 객관식(Objective) 및 주관식(Subjective) 입력 방식 지원
  - AI 단계별 피드백 및 3단계 완료 시 다각도 종합 평가 리포트 구현
-->
<template>
  <div class="pseudo-forest-overlay" :style="{ backgroundImage: `url('/image/forest/village_bg.png')` }">
    <div id="game-container" class="forest-glass">
      <!-- 닫기 버튼 -->
      <button @click="$emit('close')" class="btn-close-forest" title="마을 나가기">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>

      <!-- Main Layer -->
      <div id="content-layer">
        <!-- Header: 상태 바 및 프로그레스 -->
        <div id="status-bar">
          <div class="status-item">🏆 점수: <span>{{ totalScore }}</span></div>
          <div class="status-item">🌳 Stage: <span>{{ currentStageIndex + 1 }}/7</span></div>
          <div class="step-indicator">
            <span v-for="s in currentStage.steps.length" :key="s" :class="['step-dot', { active: currentStepIndex + 1 >= s, current: currentStepIndex + 1 === s }]"></span>
          </div>
        </div>

        <!-- 실습 영역 -->
        <div id="game-area">
          <!-- 왼쪽: 주민 인터랙션 -->
          <div id="left-panel">
            <div id="character-container" :class="{ 'talking': isAnalyzing }">
              <img :src="currentStage.character.image" :alt="currentStage.character.name">
            </div>
            <div id="dialogue-box">
              <div id="speaker-name">{{ currentStage.character.name }}</div>
              <p id="dialogue-text">{{ currentStage.dialogue }}</p>
              <!-- 단계별 질문 텍스트 -->
              <div class="step-question animate-fade-in" :key="currentStepIndex">
                <strong>질문 {{ currentStepIndex + 1 }}:</strong> {{ currentStep.question }}
              </div>
            </div>
          </div>

          <!-- 오른쪽: 응답 및 결과 -->
          <div id="right-panel">
            <!-- 퀘스트 설명 (도움말) [수정일: 2026-01-28] 가시성 보정 -->
            <div id="quest-info" v-if="currentStep.type === 'subjective'">
              <p id="quest-desc" class="dark-text">주민의 질문에 적절한 **의사코드(Pseudo-code)**나 논리를 자유롭게 작성해보세요.</p>
            </div>

            <!-- 입력 영역: 주관식 -->
            <div id="code-section" v-if="currentStep.type === 'subjective'">
              <textarea 
                v-model="userResponse" 
                placeholder="여기에 답변을 작성하세요..."
                id="code-input"
                :disabled="isStepFeedbackOpen"
              ></textarea>
            </div>

            <!-- 입력 영역: 파이썬 빈칸 채우기 (4단계) [수정일: 2026-01-28] -->
            <div id="python-fill-input" v-if="currentStep.type === 'python-fill'">
              <p id="quest-desc" class="dark-text">의사코드를 파이썬으로 변환해봅시다. 빈칸을 채워 완성하세요!</p>
              <div class="python-code-block">
                <div class="python-code-content"><template v-for="(part, pIdx) in codeParts" :key="pIdx"><span v-if="part.type === 'text'" class="code-text-part">{{ part.content }}</span><input v-else type="text" class="code-blank-input" v-model="pythonBlanks[part.blankIndex]" :style="{ width: Math.max(40, (pythonBlanks[part.blankIndex] || '').length * 12) + 'px' }" :disabled="isStepFeedbackOpen" /></template></div>
              </div>
            </div>

            <!-- 입력 영역: 객관식 -->
            <div id="objective-section" v-else-if="currentStep.type === 'objective'">
              <div class="options-grid">
                <button 
                  v-for="(opt, idx) in currentStep.options" 
                  :key="idx"
                  class="option-btn"
                  @click="submitObjective(idx)"
                  :disabled="isStepFeedbackOpen"
                >
                  <span class="opt-num">{{ idx + 1 }}</span> {{ opt }}
                </button>
              </div>
            </div>

            <!-- 컨트롤 버튼 (주관식/파이썬 빈칸용) -->
            <div id="controls" v-if="currentStep.type === 'subjective' || currentStep.type === 'python-fill'">
              <!-- [수정일: 2026-01-28] 실시간 AI 오리 가이드 영역 (상시 노출로 변경하여 초기 안내 제공) -->
              <div class="ai-duck-guide animate-fade-in">
                <div class="duck-speech-bubble">
                  <p>{{ duckHint }}</p>
                </div>
                <img src="/image/forest/i_duck_guide.png" alt="AI Duck" class="duck-img">
              </div>

              <button 
                @click="currentStep.type === 'subjective' ? submitSubjective() : submitPythonFill()" 
                class="btn primary"
                :disabled="isAnalyzing || isStepFeedbackOpen"
              >
                {{ isAnalyzing ? 'AI 분석 중...' : '답변 제출하기' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 단계별 AI 피드백 모달 -->
        <transition name="pop">
          <div v-if="isStepFeedbackOpen" id="step-feedback-overlay">
            <div class="step-feedback-card">
              <div class="feedback-header">
                <span class="icon">{{ stepResult.success ? '✅' : '💡' }}</span>
                <h3>{{ stepResult.success ? '훌륭해요!' : '조금 더 생각해볼까요?' }}</h3>
              </div>
              <p class="feedback-msg" v-html="stepResult.message"></p>
              <button @click="proceedNext" class="btn next-btn">
                {{ currentStepIndex < 2 ? '다음 단계로' : '종합 평가 보기' }}
              </button>
            </div>
          </div>
        </transition>

        <!-- 스테이지 완료 AI 종합 평가 모달 -->
        <transition name="pop">
          <div v-if="isFinalEvalOpen" id="final-eval-overlay">
            <div class="final-eval-card">
              <div class="eval-header">
                <h2>🌳 Stage {{ currentStageIndex + 1 }} 완료 보고서</h2>
                <div class="resident-seal">마을 주민 인증 완료</div>
              </div>
              
              <div class="eval-body">
                <div class="eval-scores">
                  <div class="score-item">통찰력: <span class="val">{{ finalEval.insight }}</span></div>
                  <div class="score-item">구성력: <span class="val">{{ finalEval.structure }}</span></div>
                  <div class="score-item">정밀도: <span class="val">{{ finalEval.precision }}</span></div>
                </div>
                <div class="eval-report-box">
                  <h4>🤖 AI 분석관 리포트</h4>
                  <p v-html="finalEval.report"></p>
                </div>
              </div>

              <div class="eval-footer">
                <button @click="finishStage" class="btn primary">수련 마치고 마을로 (Stage 완료)</button>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import { useGameStore } from '@/stores/game';

const emit = defineEmits(['close']);
const game = useGameStore();

// --- 4단계 퀘스트 데이터 (Stage 7개 x Step 4개) [수정일: 2026-01-28] ---
const gameData = [
  {
    stageId: 1,
    character: { name: "감자쥬 (카피바라)", image: "/image/forest/char_gamjaju.png" },
    dialogue: "뭐~ 되면 됐쥬. 마을 입구 공지판이 너무 복잡해유. 똑같은 글은 한 번만 보이게 정리해주면 고맙겠쥬~",
    steps: [
      {
        type: "subjective",
        question: "중복된 게시글을 어떻게 찾아내고 제거할지 기본적인 아이디어를 말해보세요!",
        evalCriteria: { insightKeywords: ["중복", "제거", "비교"], structureKeywords: ["순회", "반복", "리스트"], precisionKeywords: ["삭제", "하나만"] },
        duckEncouragement: "이장님, 중복 제거는 마을 정비의 기본이쥬! 어떻게 걸러낼지 생각나는 대로 적어보슈."
      },
      {
        type: "objective",
        question: "수만 개의 게시글이 있을 때, 가장 빠르게 중복을 체크할 수 있는 자료구조는 무엇일까요?",
        options: ["배열 (Array)", "집합 (Set)", "연결 리스트", "스택 (Stack)"],
        correctIndex: 1,
        explanation: "Set은 데이터 존재 여부를 O(1) 시간에 확인하여 가장 효율적입니다."
      },
      {
        type: "subjective",
        question: "만약 '글을 쓴 순서'를 그대로 유지하면서 중복만 제거해야 한다면, 로직에 무엇을 추가해야 할까요?",
        evalCriteria: { insightKeywords: ["순서", "유지", "정렬"], structureKeywords: ["새로운", "배열", "담기"], precisionKeywords: ["기존", "그대로"] },
        duckEncouragement: "순서가 뒤섞이면 마을 사람들이 헷갈려해유. '순서 유지'가 핵심이구먼유!"
      },
      {
        type: "python-fill",
        question: "순서를 유지하며 중복을 제거하는 파이썬 코드를 완성해보세요! (Set 활용)",
        codeSnippet: "def clean_board(posts):\n    seen = set()\n    result = []\n    for p in posts:\n        if p {{blank}} seen:\n            result.append(p)\n            seen.{{blank}}(p)\n    return result",
        blanks: ["not in", "add"],
        duckEncouragement: "오호, 이제 파이썬으로 옮겨볼 차례구먼유! 'not in'과 'add'를 적절히 써보슈."
      }
    ],
    finalAppraisal: {
      insightMentions: { high: "중복된 데이터의 본질을 아주 명확하게 꿰뚫어 보셨구먼유!", low: "데이터가 겹치는 부분을 찾는 게 조금 헷갈리셨나 보네유." },
      structureMentions: { high: "Set을 활용한 논리 구성이 마을 입구만큼이나 깔끔하네유!", low: "순서 유지 로직을 짤 때 조금 더 차근차근 생각해보셔유." },
      precisionMentions: { high: "파이썬 문법 실력은 이미 이 동네 최고인 것 같구먼유!", low: "코드 작성 시 문법적인 부분을 조금 더 정교하게 다듬어보셔유." },
      overallSummary: { high: "이장님 덕분에 마을 입구가 다시 환해졌슈! 천재 설계사네유.", mid: "실력이 일취월장하고 계셔유. 아주 훌륭한 정비사네유!", low: "천천히 가도 괜찮슈. 새마을 정신으로 하면 다 되게 되어 있어유!" }
    }
  },
  {
    stageId: 2,
    character: { name: "두부 (곰)", image: "/image/forest/char_dubu.png" },
    dialogue: "이장님! 날씨에 따라 배달 경로를 다르게 짜야 해요. 맑을 땐 빠른 길, 비 올 땐 안 미끄러운 길!",
    steps: [
      {
        type: "subjective",
        question: "맑은 날씨일 때, 단순히 '거리'만 고려하여 최단 경로를 찾는 로직을 어떻게 설계할까요?",
        evalCriteria: { insightKeywords: ["맑음", "거리", "최단"], structureKeywords: ["비교", "가장 짧은"], precisionKeywords: ["ID", "선택"] },
        duckEncouragement: "맑은 날엔 역시 지름길이 최고쥬! 가장 짧은 길을 어떻게 찾을지 적어보슈."
      },
      {
        type: "subjective",
        question: "비 오는 날에는 '미끄러움' 수치를 1순위로 고려해야 합니다. 어떤 조건문이 추가되어야 할까요?",
        evalCriteria: { insightKeywords: ["비", "미끄러움", "우선"], structureKeywords: ["만약", "if", "조건"], precisionKeywords: ["판단", "기준"] },
        duckEncouragement: "비 올 땐 안전이 제일이쥬! 미끄러운 길을 피하는 조건을 넣어보슈."
      },
      {
        type: "objective",
        question: "상황에 따라 다른 알고리즘을 선택하여 실행하는 패턴을 무엇이라고 부를까요?",
        options: ["싱글톤 패턴", "전략 패턴 (Strategy Pattern)", "팩토리 패턴", "어댑터 패턴"],
        correctIndex: 1,
        explanation: "전략 패턴은 실행 중에 알고리즘을 선택할 수 있게 해주는 유용한 패턴입니다."
      },
      {
        type: "python-fill",
        question: "날씨에 따라 정렬 기준을 바꾸는 파이썬 코드를 완성해보슈!",
        codeSnippet: "def get_best_path(paths, weather):\n    if weather == 'sunny':\n        return sorted(paths, key=lambda x: x.{{blank}})\n    else:\n        return sorted(paths, key=lambda x: x.{{blank}})",
        blanks: ["distance", "slip"],
        duckEncouragement: "람다(lambda) 함수를 써서 기준(key)을 정해주는 거구먼유! 거리와 미끄러움을 잘 넣어보슈."
      }
    ],
    finalAppraisal: {
      insightMentions: { high: "날씨와 지형에 따른 최적화 조건을 완벽하게 이해하셨네유!", low: "상황별 조건 분기가 조금 엉키신 것 같아유. 다시 살펴봐유." },
      structureMentions: { high: "전략 패턴을 적용하는 설계 능력이 곰처럼 듬직하구먼유!", low: "람다 함수와 정렬 기준 설정을 조금 더 연습해보면 좋겠슈." },
      precisionMentions: { high: "파이썬으로 구현한 경로 로직이 아주 정밀하고 군더더기 없슈!", low: "코드 실전 구현에서 작은 실수들을 조심하면 완벽하겠슈." },
      overallSummary: { high: "두부가 정말 고마워해유! 이제 비가 와도 배달 걱정은 없겠구먼유.", mid: "배달부로서의 자질이 충분해유. 로직이 탄탄해지고 있어유!", low: "안전이 제일이쥬. 논리를 조금만 더 다듬어보면 금방 좋아질 거예유." }
    }
  },
  {
    stageId: 3,
    character: { name: "유리 (토끼)", image: "/image/forest/char_yuri.png" },
    dialogue: "우편물이 너무 많아요! 긴급도가 높은 것부터, 같으면 카테고리 순으로 정렬해야 해요!",
    steps: [
      {
        type: "subjective",
        question: "1순위(긴급도)가 같을 때 2순위(카테고리)를 비교하는 의사코드를 한 줄로 표현한다면?",
        evalCriteria: { insightKeywords: ["긴급도", "동일", "같으면"], structureKeywords: ["카테고리", "비교", "다음"], precisionKeywords: ["사전순", "정렬"] },
        duckEncouragement: "긴급한 게 똑같으면 다음 기준을 봐야쥬. 차근차근 비교해보슈!"
      },
      {
        type: "subjective",
        question: "카테고리도 같다면 3순위(이름)를 확인해야 합니다. 이 전체적인 흐름을 최적화할 방법이 있을까요?",
        evalCriteria: { insightKeywords: ["이름", "삼단계", "마지막"], structureKeywords: ["정렬", "함수", "Comparator"], precisionKeywords: ["조건", "우선"] },
        duckEncouragement: "기준이 세 개나 되네유! 이걸 한 번에 처리하는 멋진 방법이 있을까유!"
      },
      {
        type: "objective",
        question: "여러 정렬 기준을 적용할 때, 정렬 결과가 뒤바뀌지 않는 성질을 무엇이라 할까요?",
        options: ["안정 정렬 (Stable Sort)", "불안정 정렬", "병합 정렬", "힙 정렬"],
        correctIndex: 0,
        explanation: "안정 정렬은 동일한 키값을 가진 요소들의 상대적 순서를 유지해줍니다."
      },
      {
        type: "python-fill",
        question: "다중 조건 정렬을 수행하는 파이썬 코드를 완성해보슈! (튜플 활용)",
        codeSnippet: "def sort_mail(mails):\n    # priority는 오름차순, 나머지는 사전순\n    mails.sort(key=lambda x: (x.{{blank}}, x.{{blank}}, x.{{blank}}))\n    return mails",
        blanks: ["priority", "category", "name"],
        duckEncouragement: "파이썬에선 튜플을 반환하면 알아서 순서대로 비교해줘유! 아주 편하쥬?"
      }
    ],
    finalAppraisal: {
      insightMentions: { high: "다중 조건 정렬의 핵심 원리를 완벽하게 간파하셨구먼유!", low: "정렬 순서가 꼬이면 우편함도 꼬여유. 우선순위를 다시 생각해봐유." },
      structureMentions: { high: "튜플을 활용한 다층적 구조 설계가 토끼처럼 아주 기발해유!", low: "안정 정렬의 특성을 조금 더 깊이 고민해보면 도움이 될 거예유." },
      precisionMentions: { high: "정교한 파이썬 정렬 문법 구사가 아주 인상적이고 깔끔해유!", low: "복합적인 기준을 코드로 옮길 때 괄호나 콤마 실수를 조심하셔유." },
      overallSummary: { high: "유리가 춤을 추고 있어유! 우편물이 착착 정리되는 소리가 들리네유.", mid: "체계적인 정리 능력이 돋보여유. 실력이 아주 일취월장해유!", low: "처음엔 다 복잡한 법이쥬. 하나씩 정리하다 보면 길이 보일 거예유." }
    }
  },
  {
    stageId: 4,
    character: { name: "모래 (두더지)", image: "/image/forest/char_morae.png" },
    dialogue: "마을 축제 부스를 배치해야 하는데, 사이가 안 좋은 이웃끼리는 옆에 두면 안 돼요!",
    steps: [
      {
        type: "subjective",
        question: "부스를 하나씩 놓아보다가 규칙에 어긋나는(앙숙 인접) 상황이 발생하면 어떻게 해야 할까요?",
        evalCriteria: { insightKeywords: ["어긋남", "위반", "취소"], structureKeywords: ["되돌리기", "back", "이전"], precisionKeywords: ["자리", "변경"] },
        duckEncouragement: "싸움 나면 축제 망쳐유! 안 되겠다 싶을 때 되돌아가는 법을 써보슈."
      },
      {
        type: "objective",
        question: "가능한 모든 경우를 탐색하다가 유망하지 않으면 되돌아가는 알고리즘 기법은?",
        options: ["백트래킹 (Backtracking)", "플로이드-워셜", "다익스트라", "프림 알고리즘"],
        correctIndex: 0,
        explanation: "백트래킹은 해를 찾는 과정에서 막히면 되돌아가서 다시 탐색하는 기법입니다."
      },
      {
        type: "subjective",
        question: "앙숙 관계를 미리 리스트(forbiddenPairs)로 만들어두면 어떤 점이 좋아질까요?",
        evalCriteria: { insightKeywords: ["리스트", "미리", "앙숙"], structureKeywords: ["검사", "빠름", "조회"], precisionKeywords: ["시간", "단축"] },
        duckEncouragement: "미리 명단을 뽑아두면 일 처리가 훨씬 빠르겠쥬? 장점을 적어보슈."
      },
      {
        type: "python-fill",
        question: "부스 배치가 유효한지 검사하는 파이썬 함수를 완성해보슈!",
        codeSnippet: "def is_valid(booths, forbidden):\n    for i in range(len(booths) - 1):\n        pair = (booths[i], booths[i+1])\n        if pair {{blank}} forbidden:\n            return {{blank}}\n    return True",
        blanks: ["in", "False"],
        duckEncouragement: "앙숙 쌍이 명단에 있는지 확인하고, 있으면 안 된다고(False) 알려줘야쥬!"
      }
    ],
    finalAppraisal: {
      insightMentions: { high: "갈등을 미연에 방지하는 위기 관리 능력이 탁월하시네유!", low: "앙숙 관계를 미리 파악하는 통찰력이 조금 더 필요해 보여유." },
      structureMentions: { high: "백트래킹 기법을 자유자재로 다루시는 모습이 두더지처럼 영리해유!", low: "되돌아가는 지점을 찾는 논리가 조금 복잡하셨나 보네유." },
      precisionMentions: { high: "불가능한 경우를 빠르게 쳐내는 코드 구현이 아주 날카로워유!", low: "파이썬 조건문 검사 로직을 조금 더 세밀하게 짜보셔유." },
      overallSummary: { high: "모래가 축제 준비 걱정을 덜었슈! 평화로운 마을 축제가 되겠구먼유.", mid: "위기 대응 능력이 훌륭해유. 논리적인 안전 장치가 돋보여유!", low: "평화는 멀고도 험하네유. 조금 더 정교한 검역 로직을 응원해유!" }
    }
  },
  {
    stageId: 5,
    character: { name: "밤송 (고슴도치)", image: "/image/forest/char_bamsong.png" },
    dialogue: "고민 상담 예약이 꽉 찼어요! 가장 많은 사람을 상담해주려면 어떻게 일정을 짜야 할까요?",
    steps: [
      {
        type: "subjective",
        question: "가장 많은 상담을 수락하기 위해, '상담 시간'과 '마감 기한' 중 무엇을 먼저 정렬하는 게 좋을까요?",
        evalCriteria: { insightKeywords: ["마감", "기한", "정렬"], structureKeywords: ["가장 빠른", "먼저"], precisionKeywords: ["순서", "Greedy"] },
        duckEncouragement: "시간은 금이쥬! 어떤 걸 먼저 처리해야 상담을 많이 할 수 있을까유?"
      },
      {
        type: "objective",
        question: "매 순간 가장 최선의 선택을 하는 알고리즘 설계 패러다임은?",
        options: ["그리디 (Greedy)", "동적 계획법", "분할 정복", "브루트 포스"],
        correctIndex: 0,
        explanation: "그리디 알고리즘은 탐욕적으로 현재의 최선책을 선택해 나가는 방식입니다."
      },
      {
        type: "subjective",
        question: "만약 상담 시간이 겹칠 때, 어떤 상담을 취소하고 어떤 상담을 유지할지 판단 근거를 말해보세요.",
        evalCriteria: { insightKeywords: ["겹침", "취소", "선택"], structureKeywords: ["마감", "빠른", "유지"], precisionKeywords: ["효율", "최적"] },
        duckEncouragement: "몸이 열 개라도 모자라유! 겹쳤을 때 누굴 먼저 봐줄지 기준을 세워보슈."
      },
      {
        type: "python-fill",
        question: "마감 시간이 빠른 순으로 정렬하는 파이썬 코드를 완성해보슈!",
        codeSnippet: "def schedule_counsel(tasks):\n    # end_time(마감 시간) 기준으로 정렬\n    tasks.{{blank}}(key=lambda x: x.{{blank}})\n    return tasks",
        blanks: ["sort", "end_time"],
        duckEncouragement: "정렬(sort) 함수와 람다를 쓰면 아주 간단하쥬! 마감 시간을 기준으로 해보슈."
      }
    ],
    finalAppraisal: {
      insightMentions: { high: "매 순간 최선의 선택을 찾는 눈썰미가 고슴도치 가시처럼 예리해유!", low: "마감 기한의 중요성을 놓친 것 같아유. 어떤 게 더 급한지 봐유." },
      structureMentions: { high: "그리디 알고리즘의 정수를 마을 일정표에 아주 잘 녹여내셨구먼유!", low: "효율적인 정렬 기준을 정하는 게 이번 퀘스트의 핵심이었슈." },
      precisionMentions: { high: "시간순 정렬 코드가 아주 명료하고 실수가 전혀 없으시네유!", low: "코드에서 인덱스나 변수명을 조금 더 꼼꼼히 챙겨보셔유." },
      overallSummary: { high: "밤송이가 상담 왕이 됐슈! 덕분에 마을 주민들이 속 시원해해유.", mid: "효율적인 시간 관리 능력이 일품이셔유. 아주 똑똑한 이장님이셔유!", low: "시간 관리가 참 어렵쥬. 우선순위를 다시 세우는 법을 같이 고민해봐유." }
    }
  },
  {
    stageId: 6,
    character: { name: "바나나 (원숭이)", image: "/image/forest/char_banana.png" },
    dialogue: "우유 배달을 해야 하는데 마을이 너무 넓어요! 적당히 효율적인 경로를 빨리 찾아야 해요!",
    steps: [
      {
        type: "objective",
        question: "모든 경로를 다 확인하는 대신, '적당한 수준의 해'를 빠르게 찾는 방식을 무엇이라 할까요?",
        options: ["브루트 포스", "휴리스틱 (Heuristic)", "완전 탐색", "이진 탐색"],
        correctIndex: 1,
        explanation: "휴리스틱은 완벽한 정답 대신 실행 가능한 수준의 결과를 빠르게 얻는 방법입니다."
      },
      {
        type: "subjective",
        question: "마을이 너무 커서 모든 경로를 다 계산하기 힘들 때, '가장 가까운 집부터 가기'라는 전략은 어떤가요?",
        evalCriteria: { insightKeywords: ["가까운", "전략", "휴리스틱"], structureKeywords: ["반복", "이동"], precisionKeywords: ["효율", "빠름"] },
        duckEncouragement: "다 계산하다간 해 떨어져유! 그냥 눈앞의 가까운 곳부터 가는 건 어때유?"
      },
      {
        type: "subjective",
        question: "이 배달 로직에서 '복잡도'를 줄이기 위해 어떤 타협을 할 수 있을지 의견을 주세요.",
        evalCriteria: { insightKeywords: ["복잡도", "타협", "적당한"], structureKeywords: ["근사치", "Heuristic", "포기"], precisionKeywords: ["시간", "단축"] },
        duckEncouragement: "완벽보단 적당히 빠른 게 실속 있쥬! 어떤 점을 포기하면 빨라질까유?"
      },
      {
        type: "python-fill",
        question: "현재 위치에서 가장 가까운 이웃을 찾는 파이썬 코드를 완성해보슈!",
        codeSnippet: "def find_nearest(current, neighbors):\n    nearest = min(neighbors, key=lambda n: {{blank}}(current, n))\n    return {{blank}}",
        blanks: ["distance", "nearest"],
        duckEncouragement: "거리(distance)가 최소(min)인 이웃을 찾는 거구먼유! 힌트를 잘 보슈."
      }
    ],
    finalAppraisal: {
      insightMentions: { high: "휴리스틱의 가치를 완벽히 이해하고 빠른 판단을 내리셨구먼유!", low: "완벽함에 너무 집착하다가 해가 다 졌슈! 적당한 타협이 필요해유." },
      structureMentions: { high: "근사치를 찾는 논리가 바나나처럼 아주 유연하고 실용적이에유!", low: "가까운 곳을 찾는 기준(min-key) 설정을 다시 한 번 검토해봐유." },
      precisionMentions: { high: "복잡한 계산을 최소화하는 파이썬 코드 구현 능력이 훌륭해유!", low: "입력값의 변동에 따른 예외 처리를 조금 더 정교하게 해보셔유." },
      overallSummary: { high: "바나나가 바나나 우유를 쐈슈! 아주 신속하고 정확한 배달이었슈.", mid: "융통성 있는 문제 해결 능력이 돋보여유. 아주 실전적인 실력이셔유!", low: "때로는 '적당히'가 최고일 때가 있어유. 휴리스틱을 다시 새겨봐유." }
    }
  },
  {
    stageId: 7,
    character: { name: "라임 (앵무새)", image: "/image/forest/char_lime.png" },
    dialogue: "알림 시스템을 만들 거예요! 필터링하고, 정렬하고, 그룹화해서 보내야 해요! 정신 똑바로 차리세요!",
    steps: [
      {
        type: "subjective",
        question: "데이터를 가공할 때 '필터링 -> 정렬 -> 그룹화' 순서를 지켜야 하는 이유는 무엇일까요?",
        evalCriteria: { insightKeywords: ["순서", "이유", "데이터"], structureKeywords: ["효율", "먼저", "줄이기"], precisionKeywords: ["단계", "정확"] },
        duckEncouragement: "일에도 순서가 있쥬! 왜 이 순서로 해야 효율적인지 생각해보슈."
      },
      {
        type: "objective",
        question: "여러 연산(Filter, Map, Sort)을 한 줄로 엮어 처리하는 데이터 가공 방식을 무엇이라 할까요?",
        options: ["데이터 마이닝", "파이프라인 (Pipeline)", "데이터 복제", "더미 데이터"],
        correctIndex: 1,
        explanation: "여러 단계를 체인처럼 엮어 처리하는 방식을 파이프라인 또는 스트림 처리라고 합니다."
      },
      {
        type: "subjective",
        question: "만약 긴급 알림이 발생했다면, 이 파이프라인의 어떤 단계에서 예외로 가로채야 할까요?",
        evalCriteria: { insightKeywords: ["긴급", "예외", "가로채기"], structureKeywords: ["필터링", "시작", "먼저"], precisionKeywords: ["우선", "전송"] },
        duckEncouragement: "불나면 만사 제치고 달려가야쥬! 긴급 데이터는 어디서 빼돌릴까유?"
      },
      {
        type: "python-fill",
        question: "데이터를 필터링하고 정렬하는 파이썬 파이프라인을 완성해보슈!",
        codeSnippet: "def process_data(data):\n    # 유효한 것만 거르고(Filter), 시간순 정렬\n    filtered = [d for d in data if d.{{blank}}]\n    return sorted(filtered, key=lambda x: x.{{blank}})",
        blanks: ["is_valid", "timestamp"],
        duckEncouragement: "유효성(is_valid) 검사를 먼저 하고, 시간(timestamp)대로 줄 세우는 거구먼유!"
      }
    ],
    finalAppraisal: {
      insightMentions: { high: "데이터 파이프라인의 복잡한 흐름을 완전히 장악하셨구먼유!", low: "필터링과 정렬의 순서가 뒤섞이면 일이 두 배로 힘들어져유." },
      structureMentions: { high: "연쇄적인 연산을 체계적으로 엮어내는 설계가 앵무새처럼 똑부러져유!", low: "긴급 상황 가로채기 지점을 찾는 논리를 조금 더 보완해봐유." },
      precisionMentions: { high: "리스팅과 소팅을 한 줄에 담는 고난도 구현력이 최상급이셔유!", low: "파이썬 리스트 컴프리헨션 문법을 조금 더 익혀보면 좋겠슈." },
      overallSummary: { high: "라임이 할 말이 없대유! 완벽한 자동화 시스템이 구축됐슈. 최고유!", mid: "체계적인 데이터 처리 능력이 뛰어나유. 마을 알림장이 아주 든든해유.", low: "복잡한 시스템도 결국 한 줄부터 시작이쥬. 차근차근 다시 지어봐유." }
    }
  }
];

// --- 상태 관리 ---
// [수정일: 2026-01-28] 상태 관리 변수 선언 (순서 최적화)
const currentStageIndex = ref(0);
const currentStepIndex = ref(0);
const totalScore = ref(0);
const userResponse = ref('');
const pythonBlanks = ref([]);

const currentStage = computed(() => gameData[currentStageIndex.value]);
const currentStep = computed(() => {
  if (!currentStage.value || !currentStage.value.steps) return null;
  return currentStage.value.steps[currentStepIndex.value] || null;
});

// [수정일: 2026-01-28] 파이썬 코드를 텍스트와 빈칸(input)으로 조각내기
const codeParts = computed(() => {
  if (!currentStep.value || currentStep.value.type !== 'python-fill') return [];
  const snippet = currentStep.value.codeSnippet || '';
  const parts = [];
  const splitPattern = /{{blank}}/;
  const splitTexts = snippet.split(splitPattern);
  
  splitTexts.forEach((text, i) => {
    // 텍스트 추가
    parts.push({ type: 'text', content: text });
    // 마지막 텍스트가 아니면 빈칸 추가
    if (i < splitTexts.length - 1) {
      parts.push({ type: 'blank', blankIndex: i });
    }
  });
  return parts;
});

// [수정일: 2026-01-28] 다음 단계로 넘어갈 때 빈칸 모델 초기화 (방어 코드 추가)
watch(() => currentStepIndex.value, (newIdx) => {
  if (!currentStep.value || currentStep.value.type !== 'python-fill') return;
  
  // 이미 값이 있으면 유지, 없으면 빈 문자열로 초기화
  const snippet = currentStep.value.codeSnippet || '';
  const blankCount = (snippet.match(/{{blank}}/g) || []).length;
  if (pythonBlanks.value.length !== blankCount) {
    pythonBlanks.value = new Array(blankCount).fill('');
  }
}, { immediate: true });

// [수정일: 2026-01-28] 실시간 오리 힌트 상태 관리 (데이터 주도형으로 개편)
const duckHint = computed(() => {
  const step = currentStep.value;
  if (!step) return "새마을 정신으로 일하면 못할 게 없슈! 논리적으로 차근차근 써보세유.";

  if (step.type === 'subjective') {
    const resp = userResponse.value.trim().toLowerCase();
    if (resp.length === 0) return "이장님, 뭐라도 적어보슈! 내가 옆에서 도와줄게유~";
    
    // 핵심 키워드가 포함되었을 때 (데이터 기반 리액션)
    const hits = step.evalCriteria.insightKeywords.filter(kw => resp.includes(kw));
    if (hits.length > 0) return `오! '${hits[0]}' 같은 핵심을 잘 짚으셨구먼유. 계속 가보슈!`;
    
    // 입력이 길어지는데 키워드가 없을 때 보조 힌트
    if (resp.length > 20) return "오호, 말이 길어지는 걸 보니 뭔가 생각 중이시구먼유? 키워드를 좀 더 섞어보슈!";
    
    return step.duckEncouragement || "새마을 정신으로 일하면 못할 게 없슈! 논리적으로 차근차근 써보세유.";
  }

  if (step.type === 'python-fill') {
    const filledCount = pythonBlanks.value.filter(b => b && b.trim()).length;
    if (filledCount === 0) return step.duckEncouragement || "파이썬으로 빈칸을 채워보슈! 실력이 아주 일취월장 하셨구먼유.";
    if (filledCount < step.blanks.length) return "그렇쥬! 빈칸을 마저 채우면 완벽한 코드가 되겠구먼유. 힘내슈!";
    return "오오, 다 채우셨구먼유! 이제 '답변 제출하기'를 눌러 검사를 받아보슈.";
  }
  
  return "새마을 정신으로 일하면 못할 게 없슈! 논리적으로 차근차근 써보세유.";
});

const isAnalyzing = ref(false);
const isStepFeedbackOpen = ref(false);
const isFinalEvalOpen = ref(false);

const stepResult = ref({ success: false, message: '' });
const finalEval = ref({ insight: 0, structure: 0, precision: 0, report: '' });
const stageLogs = ref([]); // 현재 스테이지의 3단계 답변 및 평가 로그


// --- 핸들러: 주관식 제출 ---
const submitSubjective = () => {
  // [수정일: 2026-01-28] 빈 입력값에 대한 예외 처리 및 사용자 안내 추가 (무반응 현상 해결)
  if (!userResponse.value.trim()) {
    stepResult.value = { 
      success: false, 
      message: "이장님, 뭐라도 적어주셔야 마을 정비를 할 수 있어유! 빈 칸으론 안 돼유~" 
    };
    isStepFeedbackOpen.value = true;
    return;
  }
  isAnalyzing.value = true;

  // AI 분석 시뮬레이션
  setTimeout(() => {
    const code = userResponse.value.toLowerCase();
    const criteria = currentStep.value.evalCriteria;
    
    let score = 0;
    if (criteria.insightKeywords.some(kw => code.includes(kw))) score += 40;
    if (criteria.structureKeywords.some(kw => code.includes(kw))) score += 40;
    if (criteria.precisionKeywords.some(kw => code.includes(kw))) score += 20;

    const success = score >= 60;
    const msg = success 
      ? `<strong>AI 통찰:</strong> 논리적 키워드가 정확합니다! 단계별 요구사항을 완벽히 이해하셨네요.`
      : `<strong>AI 조언:</strong> 핵심 개념인 '${criteria.insightKeywords[0]}' 등에 대해 조금 더 명확히 서술해보세요.`;

    stepResult.value = { success, message: msg, rawScore: score, response: userResponse.value };
    stageLogs.value.push(stepResult.value);
    
    isAnalyzing.value = false;
    isStepFeedbackOpen.value = true;
    totalScore.value += score;
  }, 1000);
};

// --- 핸들러: 객관식 제출 ---
const submitObjective = (idx) => {
  const isCorrect = idx === currentStep.value.correctIndex;
  const score = isCorrect ? 100 : 20;
  
  stepResult.value = { 
    success: isCorrect, 
    message: isCorrect 
      ? `정답입니다! 🎯<br>${currentStep.value.explanation}`
      : `아쉽습니다. 정답은 <strong>'${currentStep.value.options[currentStep.value.correctIndex]}'</strong>입니다.<br>${currentStep.value.explanation}`,
    rawScore: score,
    response: currentStep.value.options[idx]
  };
  
  stageLogs.value.push(stepResult.value);
  isStepFeedbackOpen.value = true;
  totalScore.value += score;
};

// --- 핸들러: 파이썬 빈칸 제출 [수정일: 2026-01-28] ---
const submitPythonFill = () => {
  const blanks = currentStep.value.blanks;
  if (pythonBlanks.value.length < blanks.length || pythonBlanks.value.some(b => !b?.trim())) {
    stepResult.value = { success: false, message: "빈칸을 모두 채워주셔야 마을 정비가 끝나유!" };
    isStepFeedbackOpen.value = true;
    return;
  }

  isAnalyzing.value = true;
  setTimeout(() => {
    let correctCount = 0;
    pythonBlanks.value.forEach((val, idx) => {
      if (val.trim() === blanks[idx]) correctCount++;
    });

    const success = correctCount === blanks.length;
    const score = Math.round((correctCount / blanks.length) * 100);
    
    stepResult.value = {
      success,
      message: success 
        ? "<strong>AI 통찰:</strong> 완벽한 파이썬 코드구먼유! 의사코드의 논리를 정확히 이해하셨네유."
        : `<strong>AI 조언:</strong> 조금 아깝구먼유! ${blanks.length - correctCount}개가 틀려슈. 문법을 다시 한 번 확인해보슈!`,
      rawScore: score,
      response: pythonBlanks.value.join(', ')
    };

    stageLogs.value.push(stepResult.value);
    isAnalyzing.value = false;
    isStepFeedbackOpen.value = true;
    totalScore.value += score;
  }, 1000);
};

// --- 다음 단계 또는 종합 평가로 이동 ---
const proceedNext = () => {
  isStepFeedbackOpen.value = false;
  userResponse.value = '';
  
  const stepCount = currentStage.value.steps.length;
  if (currentStepIndex.value < stepCount - 1) {
    currentStepIndex.value++;
  } else {
    // 현재 스테이지 모든 단계 완료 -> 종합 평가 생성
    generateFinalEvaluation();
  }
};

/**
 * [수정일: 2026-01-28] 3단계 답변 로그를 기반으로 다각도 AI 최종 리포트 생성
 */
const generateFinalEvaluation = () => {
  const totalRaw = stageLogs.value.reduce((acc, log) => acc + log.rawScore, 0);
  const stepCount = currentStage.value.steps.length;
  
  // [수정일: 2026-01-28] 단계별 성취도 정밀 분석 로직
  // Step 1: 통찰력 (Insight)
  const step1 = stageLogs.value[0] || { rawScore: 0 };
  const insight = Math.min(Math.round(step1.rawScore * 1.1), 100);
  
  // Step 2 & 3: 구성력 (Structure)
  const step2 = stageLogs.value[1] || { rawScore: 0 };
  const step3 = stageLogs.value[2] || { rawScore: 0 };
  const structure = Math.min(Math.round(((step2.rawScore + step3.rawScore) / 2) * 1.05), 100);
  
  // Step 4: 정밀도 (Precision) - 파이썬 코딩
  const step4 = stageLogs.value[3] || { rawScore: 0 };
  const precision = step4.rawScore;

  const avg = (insight + structure + precision) / 3;
  const appraisal = currentStage.value.finalAppraisal;

  // 개인화된 분석 리포트 생성 (데이터 기반)
  let comment = "";
  if (avg >= 90) comment = appraisal.overallSummary.high;
  else if (avg >= 70) comment = appraisal.overallSummary.mid;
  else comment = appraisal.overallSummary.low;

  finalEval.value = {
    insight,
    structure,
    precision,
    report: `<strong>[${currentStage.value.character.name} 스테이지 분석]</strong><br><br>` +
            `• <strong>통찰 분석:</strong> ${insight >= 80 ? appraisal.insightMentions.high : appraisal.insightMentions.low}<br>` +
            `• <strong>논리 구성:</strong> ${structure >= 80 ? appraisal.structureMentions.high : appraisal.structureMentions.low}<br>` +
            `• <strong>실전 구현:</strong> ${precision >= 80 ? appraisal.precisionMentions.high : appraisal.precisionMentions.low}<br><br>` +
            `<strong>🤖 총평:</strong> ${comment}`
  };
  
  isFinalEvalOpen.value = true;
};

// --- 스테이지 완료 및 다음 해금 ---
const finishStage = () => {
  isFinalEvalOpen.value = false;
  
  // gameStore 연동: 현재 스테이지 완료 처리 및 다음 해금
  game.unlockNextStage('Pseudo Forest', currentStageIndex.value);
  
  if (currentStageIndex.value < gameData.length - 1) {
    currentStageIndex.value++;
    currentStepIndex.value = 0;
    stageLogs.value = [];
    userResponse.value = '';
  } else {
    emit('close');
  }
};

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Gaegu:wght@400;700&family=Nanum+Gothic+Coding:wght@400;700&display=swap');

.pseudo-forest-overlay {
  position: fixed; inset: 0; background-size: cover; background-position: center; z-index: 2000;
  display: flex; align-items: center; justify-content: center; padding: 20px; font-family: 'Gaegu', cursive;
}
.pseudo-forest-overlay::before { content: ''; position: absolute; inset: 0; background: rgba(0, 0, 0, 0.45); backdrop-filter: blur(8px); }

#game-container {
  position: relative; width: 100%; max-width: 1100px; height: 90vh;
  background: rgba(255, 255, 255, 0.88); backdrop-filter: blur(20px);
  border-radius: 40px; border: 8px solid #5d4037; box-shadow: 0 40px 100px rgba(0,0,0,0.5);
  overflow: hidden; display: flex; flex-direction: column;
}

.btn-close-forest {
  position: absolute; top: 20px; right: 20px; background: #8b4513; color: white;
  width: 44px; height: 44px; border-radius: 12px; border: none; cursor: pointer;
  z-index: 10; display: flex; align-items: center; justify-content: center; transition: 0.3s;
}
.btn-close-forest:hover { transform: scale(1.1) rotate(90deg); background: #d32f2f; }

#content-layer { flex: 1; display: flex; flex-direction: column; padding: 30px; }

#status-bar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 30px; background: #795548; color: white; border-radius: 20px; margin-bottom: 20px;
}
.status-item span { font-weight: 800; color: #ffeb3b; }

.step-indicator { display: flex; gap: 10px; }
.step-dot { width: 12px; height: 12px; border-radius: 50%; background: rgba(255,255,255,0.3); transition: 0.4s; }
.step-dot.active { background: #ffeb3b; }
.step-dot.current { box-shadow: 0 0 15px #ffeb3b; transform: scale(1.3); }

#game-area { flex: 1; display: grid; grid-template-columns: 1fr 1.2fr; gap: 30px; min-height: 0; }

#left-panel { display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
#character-container { flex: 1; display: flex; align-items: center; justify-content: center; transition: 0.3s; }
#character-container img { max-height: 250px; filter: drop-shadow(0 10px 20px rgba(0,0,0,0.2)); }
#character-container.talking { animation: bounce 0.5s infinite alternate; }

#dialogue-box {
  background: #fff9c4; border: 4px solid #fbc02d; border-radius: 20px; padding: 20px; position: relative;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
#speaker-name { position: absolute; top: -15px; left: 20px; background: #f9a825; color: white; padding: 3px 15px; border-radius: 10px; font-weight: 800; }
#dialogue-text { font-size: 1.3rem; margin-bottom: 10px; color: #5d4037; }
.step-question { font-size: 1.4rem; color: #2e7d32; border-top: 2px dashed #fbc02d; padding-top: 10px; line-height: 1.4; }

#right-panel { display: flex; flex-direction: column; gap: 20px; }
#code-section { flex: 1; display: flex; flex-direction: column; }
#code-input {
  flex: 1; width: 100%; font-family: 'Nanum Gothic Coding', monospace; font-size: 1.3rem;
  padding: 20px; border: 4px solid #ced4da; border-radius: 20px; background: white;
  color: #1a1a1a; resize: none; transition: 0.3s;
}
.dark-text { color: #5d4037 !important; font-weight: 700; } /* [수정일: 2026-01-28] 가시성 보정용 스타일 */

#code-input:focus { border-color: #8b4513; outline: none; box-shadow: 0 0 20px rgba(139,69,19,0.1); }

/* [수정일: 2026-01-28] 실시간 AI 오리 가이드 스타일 */
.ai-duck-guide {
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  gap: 10px;
  margin-top: -10px;
  margin-bottom: 5px;
}
.duck-speech-bubble {
  background: #fff9c4;
  border: 3px solid #fbc02d;
  padding: 10px 15px;
  border-radius: 20px 20px 0 20px;
  max-width: 250px;
  font-size: 1.1rem;
  color: #5d4037;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.duck-img {
  width: 70px;
  height: 70px;
  object-fit: contain;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
}

/* 객관식 스타일 */
.options-grid { display: flex; flex-direction: column; gap: 15px; }
.option-btn {
  background: white; border: 3px solid #e0e0e0; border-radius: 15px; padding: 15px 25px;
  font-family: inherit; font-size: 1.4rem; color: #5d4037; cursor: pointer; text-align: left;
  display: flex; align-items: center; gap: 15px; transition: 0.2s;
}
.option-btn:hover:not(:disabled) { transform: translateX(10px); background: #fffde7; border-color: #fbc02d; }
.opt-num { background: #f5f5f5; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: 800; }

.btn {
  width: 100%; padding: 15px; border-radius: 20px; font-family: inherit; font-size: 1.5rem; font-weight: 800;
  cursor: pointer; border: none; box-shadow: 0 8px 0 rgba(0,0,0,0.1); transition: 0.2s;
}
.btn.primary { background: #fbc02d; color: #5d4037; }
.btn.primary:hover { transform: translateY(-3px); box-shadow: 0 11px 0 rgba(0,0,0,0.1); background: #fdd835; }
.btn:active { transform: translateY(5px); box-shadow: 0 3px 0 rgba(0,0,0,0.1); }

/* 모달 및 피드백 */
#step-feedback-overlay, #final-eval-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 100;
  padding: 40px;
}
.step-feedback-card, .final-eval-card {
  background: white; border-radius: 30px; padding: 40px; max-width: 600px; width: 100%;
  border: 6px solid #8b4513; animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.feedback-header { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
.feedback-header .icon { font-size: 3rem; }
.feedback-msg { font-size: 1.3rem; line-height: 1.6; color: #5d4037; margin-bottom: 30px; }

.final-eval-card { max-width: 750px; }
.eval-header h2 { color: #5d4037; font-size: 2rem; margin: 0; }
.resident-seal { padding: 5px 15px; border: 3px double #d32f2f; color: #d32f2f; font-weight: 900; transform: rotate(-5deg); border-radius: 10px; background: rgba(211, 47, 47, 0.05); }
.eval-scores { display: flex; justify-content: space-around; margin-bottom: 30px; background: #fdf5e6; padding: 20px; border-radius: 20px; border: 2px solid #deb887; }
.score-item { text-align: center; font-size: 1.3rem; display: flex; flex-direction: column; color: #5d4037; font-weight: 700; }
.score-item .val { font-size: 3rem; font-weight: 900; color: #2e7d32; text-shadow: 2px 2px 0 white; }
.eval-report-box { background: white; padding: 25px; border-radius: 20px; border: 3px solid #e0e0e0; box-shadow: inset 0 2px 10px rgba(0,0,0,0.05); }
.eval-report-box h4 { margin-bottom: 15px; color: #5d4037; font-size: 1.4rem; display: flex; align-items: center; gap: 10px; }
.eval-report-box p { line-height: 1.8; font-size: 1.25rem; color: #4e342e; text-align: left; }

@keyframes popIn { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }
@keyframes bounce { from { transform: translateY(0); } to { transform: translateY(-10px); } }

/* [수정일: 2026-01-28] 파이썬 빈칸 채우기 스타일 */
.python-code-block {
  background: #23241f; color: #f8f8f2; padding: 25px; border-radius: 20px;
  font-family: 'Nanum Gothic Coding', monospace; font-size: 1.1rem; line-height: 1.6;
  overflow-x: auto; border: 4px solid #5d4037; box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
}
.python-code-content {
  white-space: pre; word-break: normal; margin: 0;
  display: block; font-family: 'Nanum Gothic Coding', monospace;
  font-size: 1.1rem; line-height: 1.8;
}
.code-text-part {
  display: inline; white-space: pre;
}
.code-blank-input {
  background: #3e3e3e; border: 2px solid #fbc02d; color: #ffeb3b;
  padding: 1px 8px; border-radius: 6px; font-family: inherit; font-size: 1.1rem;
  transition: 0.3s; margin: 0 4px; outline: none;
  vertical-align: middle; display: inline-block;
  box-sizing: border-box; position: relative; top: -1px;
}
.code-blank-input:focus { background: #4e4e4e; box-shadow: 0 0 10px #fbc02d; border-color: #fdd835; }

.animate-fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
