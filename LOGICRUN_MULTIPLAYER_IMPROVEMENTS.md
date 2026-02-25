# LogicRun 멀티플레이어 개선 보고서
**수정일**: 2026-02-25
**작업**: Phase 1 동기화 개선 + Phase 2 대기 상태 구현

---

## 📊 개요

### 이전 문제점
1. **Phase 1 동기화 미흡**: 상대 플레이어의 진행 상황(점수, 진도)이 실시간으로 반영되지 않음
2. **Phase 2 제출 문제**: 첫 제출 시 즉시 게임 종료 → 상대 플레이어가 답변할 기회 없음
3. **평가 부재**: 양쪽 코드에 대한 개별 평가 없음

### 해결 방안
| 문제 | 해결책 | 효과 |
|------|--------|------|
| 동기화 미흡 | `onSync` 데이터 매핑 개선 | 실시간 상대 진행도 표시 |
| 즉시 종료 | 30초 대기 상태 추가 | 양쪽 모두 제출 기회 제공 |
| 평가 부재 | 양쪽 코드 수집 후 LLM 평가 | 개별 피드백 제공 |

---

## 🔧 Phase 1: 실시간 동기화 개선

### 현재 아키텍처

```
Player 1 (정답)
    ↓
emitProgress(roomId, {
  phase: 'speedFill',
  score: 450,  ← 중요!
  sid: 'player1-sid'
})
    ↓
Backend: run_progress()
    ↓ skip_sid 제외하고 broadcast
    ↓
Player 2: onSync() 리스너
    ↓ 데이터 매핑
    ↓
scoreP2.value = data.score (실시간 업데이트!)
```

### 개선 전 코드
```javascript
// ❌ 잘못된 매핑
rs.onSync.value = (data) => {
  scoreP2.value = data.scoreP2 || 0  // scoreP2 필드는 존재하지 않음!
  checksCompletedP2.value = data.checksCompleted || 0
}
```

### 개선 후 코드
```javascript
// ✅ 올바른 매핑
rs.onSync.value = (data) => {
  if (data.sid !== rs.socket.value?.id) {
    const myIdx = rs.roomPlayers.value.findIndex(p => p.sid === rs.socket.value.id)

    // Phase 1: 빈칸 채우기 (속도전)
    if (data.phase === 'speedFill') {
      if (myIdx === 0) {
        scoreP2.value = data.score || 0  // ← 올바른 필드명
      } else {
        scoreP1.value = data.score || 0
      }
    }

    // Phase 2: 설계 스프린트
    else if (data.phase === 'designSprint') {
      if (data.state === 'submitted') {
        // 상대가 제출함!
        opponentSubmitted.value = true
        opponentCode.value = data.code || ''
        // 체크리스트 동기화
      }
    }
  }
}
```

### 동기화 흐름 다이어그램

```
┌─────────────────┐
│   Player 1      │
├─────────────────┤
│ selectBlankAnswer('정답') │
│ handleBlankCorrect()       │
│ scoreP1 += 100             │
│ emitProgress({             │
│   phase: 'speedFill',      │
│   score: 100,              │
│   combo: 1                 │
│ })                         │
└────────┬────────┘
         │
         ↓ [Socket.io]
    ┌─────────────────┐
    │ Backend Route   │
    │ run_progress()  │
    │ (broadcast)     │
    └────────┬────────┘
             │ skip_sid='player1'
             ↓
    ┌─────────────────────────┐
    │   Player 2              │
    ├─────────────────────────┤
    │ onSync() 리스너 발동     │
    │ data.score = 100        │
    │ scoreP1.value = 100     │
    │ (UI 자동 업데이트)      │
    │ ⚡ 즉시 표시됨!         │
    └─────────────────────────┘
```

### 기대 효과
- ✅ **실시간 진행도**: 상대 플레이어의 점수가 즉시 업데이트
- ✅ **경쟁 심화**: "아, 상대가 나보다 앞서나가네!" 시각적 피드백
- ✅ **긴장감**: 점수 차이가 실시간으로 보임

---

## ⏳ Phase 2: 대기 상태 & 평가 시스템

### 새 상태 머신

```
┌──────────────────────────────────────────────────┐
│ Phase 2: Design Sprint                           │
├──────────────────────────────────────────────────┤
│                                                  │
│  [EDITING] ─────SUBMIT────→ [WAITING]           │
│  (코드 작성)              (상대 대기)           │
│    ↑                           ↓                 │
│    │                    (30초 또는 상대 제출)     │
│    │                           ↓                 │
│    └──────────← [EVALUATED] ←───               │
│              (평가 완료)                         │
│                  ↓                               │
│           SHOW RESULT & SCORES                   │
└──────────────────────────────────────────────────┘
```

### 상태값 정의

```javascript
// Phase 2 상태 관리
const phase2Status = ref('editing')     // editing | waiting | evaluated
const opponentSubmitted = ref(false)    // 상대 제출 여부
const opponentCode = ref('')            // 상대가 제출한 코드
const myEvaluation = ref(null)          // 내 평가 결과
const opponentEvaluation = ref(null)    // 상대 평가 결과
const phase2WaitingTimeout = ref(30)    // 남은 대기 시간 (초)
```

### 제출 로직 상세

#### Step 1: 첫 번째 플레이어 제출
```javascript
function submitDesign() {
  if (phase2Status.value === 'waiting') return  // 이미 제출됨

  const code = designCode.value

  // ① 로컬 체크리스트 평가
  const checkedItems = []
  for (const check of checklistItems.value) {
    for (const pattern of check.patterns) {
      if (pattern.test(code)) {
        checkedItems.push(check.id)
        break
      }
    }
  }

  // ② 점수 계산
  const checkCount = checkedItems.length
  const totalPoints = (checkCount * 100) + (completionBonus) + (timeBonus)

  // ③ 내 평가 저장
  myEvaluation.value = {
    code,
    checkCount,
    totalPoints,
    checksCompleted: checkedItems
  }

  // ④ 상태 변경: waiting
  phase2Status.value = 'waiting'
  phase2WaitingTimeout.value = 30

  // ⑤ 상대에게 전송
  rs.emitProgress(roomId.value, {
    phase: 'designSprint',
    state: 'submitted',        // ← 중요: 제출됨 신호
    code: code,               // ← 상대 코드 전송
    checksCompleted: checkCount,
    totalPoints,
    sid: rs.socket.value?.id
  })

  // ⑥ 30초 타이머 시작
  startPhase2WaitingTimeout()
}
```

#### Step 2: 상대 플레이어 수신
```javascript
rs.onSync.value = (data) => {
  if (data.sid !== rs.socket.value?.id && data.phase === 'designSprint') {
    if (data.state === 'submitted') {
      // 상대가 제출했다!
      opponentSubmitted.value = true        // UI 갱신 신호
      opponentCode.value = data.code        // 상대 코드 저장
      // → UI가 즉시 상대 코드를 표시
    }
  }
}
```

#### Step 3: 타임아웃 또는 상대 제출 후 마무리
```javascript
function startPhase2WaitingTimeout() {
  let interval = setInterval(() => {
    phase2WaitingTimeout.value--

    // 조건 1: 상대가 제출했거나
    // 조건 2: 30초 타임아웃
    if (phase2WaitingTimeout.value <= 0 || opponentSubmitted.value) {
      clearInterval(interval)
      finalizePhase2()
    }
  }, 1000)
}

function finalizePhase2() {
  phase2Status.value = 'evaluated'

  // 여기서 나중에 LLM 평가 호출 가능
  // await evaluateBothCodes()

  // 2초 후 결과 화면으로
  setTimeout(() => {
    endGame('complete')
  }, 2000)
}
```

---

## 🎨 UI 상태별 표시

### 1️⃣ EDITING 상태 (코드 작성 중)
```
┌─────────────────────────────────────────────┐
│ HUD: P1 SCORE | ⏱ TIMER | P2 PROGRESS      │
├─────────────────────────────────────────────┤
│                                             │
│  [LEFT]              [RIGHT]                │
│  ┌──────────────┐   ┌──────────────┐       │
│  │ 📋 시나리오 │   │ 💻 에디터   │       │
│  │              │   │              │       │
│  │ 시나리오     │   │ function(){  │       │
│  │ 텍스트...    │   │   ...        │       │
│  │              │   │ }            │       │
│  │              │   │              │       │
│  └──────────────┘   ├──────────────┤       │
│  ┌──────────────┐   │ ✅ SUBMIT    │       │
│  │ ✓ 체크리스트 │   └──────────────┘       │
│  │ ⬜ 항목 1     │                         │
│  │ ✅ 항목 2     │                         │
│  │ ⬜ 항목 3     │                         │
│  └──────────────┘                         │
└─────────────────────────────────────────────┘
```

### 2️⃣ WAITING 상태 (상대 대기 중)
```
┌─────────────────────────────────────────────┐
│ HUD: 📤 YOU SUBMITTED | ⏳ TIMER | ⏳ WAITING │
├─────────────────────────────────────────────┤
│                                             │
│  [LEFT - 내 제출]    [RIGHT - 상대 상태]   │
│  ┌──────────────┐   ┌──────────────┐       │
│  │ 🎯 YOUR      │   │ ⏳ WAITING   │       │
│  │ SUBMISSION   │   │              │       │
│  │              │   │ 상대 플레이어 │      │
│  │ Code Preview │   │ 를 기다리는  │      │
│  │ function(){  │   │ 중...        │      │
│  │   ...        │   │              │      │
│  │ }            │   │ 남은 시간:    │      │
│  │              │   │ 23초          │      │
│  │ ✅ Checks: 2/4│  └──────────────┘       │
│  │ ⭐ Points: 450 │                       │
│  └──────────────┘                         │
└─────────────────────────────────────────────┘

상대가 제출하면:
┌─────────────────────────────────────────────┐
│ HUD: 📤 YOU SUBMITTED | ⏳ 15s | ✅ OPPONENT │
├─────────────────────────────────────────────┤
│  [LEFT - 내 제출]    [RIGHT - 상대 코드]   │
│  ┌──────────────┐   ┌──────────────┐       │
│  │ 🎯 내 코드   │   │ 📄 상대 코드 │       │
│  │ (같은 표시) │   │              │       │
│  │              │   │ function(){  │       │
│  │              │   │   other_code │       │
│  │              │   │   ...        │       │
│  │              │   │ }            │       │
│  └──────────────┘   └──────────────┘       │
└─────────────────────────────────────────────┘
```

### 3️⃣ EVALUATED 상태 (평가 완료)
```
(2초 동안 평가 상태 표시 후 자동으로 RESULT 화면으로 전환)

(향후 LLM 평가 추가 시)
┌─────────────────────────────────────────────┐
│ 🎯 PSEUDOCODE EVALUATION COMPLETE           │
├─────────────────────────────────────────────┤
│                                             │
│  [LEFT - 내 평가]    [RIGHT - 상대 평가]   │
│  ┌──────────────┐   ┌──────────────┐       │
│  │ 📊 내 평가    │   │ 📊 상대 평가 │       │
│  │              │   │              │       │
│  │ 점수: 65/100  │   │ 점수: 72/100 │       │
│  │ 등급: GOOD    │   │ 등급: GOOD   │       │
│  │              │   │              │       │
│  │ 강점:        │   │ 강점:        │       │
│  │ - 논리 명확   │   │ - 디테일 풍부│       │
│  │              │   │              │       │
│  │ 개선점:      │   │ 개선점:      │       │
│  │ - 예외처리    │   │ - 추상화 부족│       │
│  │              │   │              │       │
│  └──────────────┘   └──────────────┘       │
│                                             │
│       [← 이전]                 [다시하기 →] │
└─────────────────────────────────────────────┘
```

---

## 📊 HUD 변화

### Phase 2 HUD 비교

#### EDITING 상태
```
┌─ P1 SCORE: 450pt ─ ⏱ 87s ─ R1/1 ─ ⏱ 87s ─ P2 SCORE: 380pt ─┐
```

#### WAITING 상태
```
┌─ 📤 YOU: 3/4 checks ─ ⏳ 25s ─ ✅ OPPONENT SUBMITTED ─┐
```

#### EVALUATED 상태
```
┌─ 🎯 EVALUATING... ─────────────────────────────────────┐
```

---

## 🔌 Socket 이벤트 흐름

### Before (현재)
```
Player 1 Submit
    ↓ [run_progress]
Player 2: onSync
    ↓
endGame() ← 즉시 종료! ❌
```

### After (개선됨)
```
Player 1 Submit
    ↓ [run_progress: state='submitted']
Player 2: onSync
    ↓ opponentSubmitted = true
Player 2 대기 (30초 또는 제출 대기)
    ↓
finalizePhase2()
    ↓
endGame()
```

---

## 📋 구현 체크리스트

### Phase 1 (✅ 완료)
- [x] `onSync` 데이터 매핑 수정 (`scoreP2` → `score`)
- [x] Phase별 동기화 로직 분리

### Phase 2 (🔄 진행중)
- [x] 상태 변수 추가 (`phase2Status`, `opponentSubmitted` 등)
- [x] `evaluateDesign()` 함수 개선 (대기 상태로 전환)
- [x] `startPhase2WaitingTimeout()` 함수 구현
- [x] `finalizePhase2()` 함수 구현
- [x] UI 업데이트 (대기 상태 화면)
- [x] 스타일 추가

### 향후 (🚀 다음 단계)
- [ ] 백엔드 LLM 평가 API 추가
- [ ] `opponentEvaluation` 데이터 수신
- [ ] 평가 결과 UI 표시
- [ ] 상대 코드 분석 및 비교 기능

---

## 🚀 다음 단계: LLM 평가 통합

### 백엔드 구현 계획

```python
# backend/core/socket_server.py

run_phase2_submissions = {}  # { room_id: { p1_code, p2_code } }

@sio.event
async def run_progress(sid, data):
    room_id = data.get('room_id')

    if data.get('state') == 'submitted' and data.get('phase') == 'designSprint':
        # ① 양쪽 코드 수집
        if room_id not in run_phase2_submissions:
            run_phase2_submissions[room_id] = {}

        run_phase2_submissions[room_id][sid] = {
            'code': data.get('code'),
            'score': data.get('totalPoints')
        }

        # ② 양쪽 모두 제출되었는지 확인
        if len(run_phase2_submissions[room_id]) == 2:
            # LLM 평가 호출
            evaluations = await evaluate_both_pseudocodes(
                run_phase2_submissions[room_id]
            )

            # ③ 결과 전송
            await sio.emit('run_evaluation', evaluations, room=room_id)

            # ④ 정리
            del run_phase2_submissions[room_id]

    # 기존 forwarding 로직
    await sio.emit('run_sync', data, room=room_id, skip_sid=sid)
```

---

## 📈 기대 효과

### 사용자 경험
1. ✨ **더 공정한 경쟁**: 양쪽 모두 제출할 기회
2. 🎯 **명확한 피드백**: 상대 코드와 비교 가능
3. 📊 **학습 효과**: 다른 해결책 분석

### 시스템 안정성
1. ✅ **동기화 개선**: 실시간 진행도 표시
2. ⏳ **타임아웃 관리**: 30초 제한시간으로 무한 대기 방지
3. 🔒 **상태 관리**: 명확한 상태 전환으로 버그 감소

---

## 📝 주의사항

### 현재 제한사항
- LLM 평가는 아직 백엔드에서 구현 필요
- 간단한 체크리스트 기반 평가만 적용됨

### 개선 가능 부분
- [ ] 상대 코드 실시간 하이라이트 표시
- [ ] 두 코드의 차이점 분석
- [ ] 평가 결과 통계 그래프

---

## 📚 참고 파일

- Frontend: `frontend/src/features/wars/minigames/LogicRun.vue`
- Socket: `backend/core/socket_server.py` (line 728-732)
- Evaluator: `backend/core/services/pseudocode_evaluator.py`

---

**작성자**: Claude Code
**최종 수정**: 2026-02-25
