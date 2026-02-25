# LogicRun 멀티플레이어 구현 완료 체크리스트

**작성일**: 2026-02-25
**상태**: ✅ Phase 1, 2 구현 완료

---

## ✅ 완료된 작업

### 🎮 Frontend (LogicRun.vue)

#### Phase 1: 실시간 동기화
- [x] `onSync` 데이터 매핑 개선
  - ❌ `data.scoreP2` → ✅ `data.score`
  - Phase별 데이터 구분 처리

- [x] `emitProgress` 이벤트 최적화
  - Phase 정보 포함 (`speedFill`, `designSprint`)
  - 점수 및 진행도 실시간 전송

**코드 위치**: Line 308-330
```javascript
rs.onSync.value = (data) => {
  if (data.phase === 'speedFill') {
    scoreP2.value = data.score || 0
  } else if (data.phase === 'designSprint') {
    if (data.state === 'submitted') {
      opponentSubmitted.value = true
      opponentCode.value = data.code || ''
    }
  }
}
```

#### Phase 2: 대기 상태 & 평가 시스템
- [x] 상태 변수 추가
  - `phase2Status` (editing | waiting | evaluated)
  - `opponentSubmitted`, `opponentCode`
  - `myEvaluation`, `opponentEvaluation`
  - `phase2WaitingTimeout` (30초)

**코드 위치**: Line 363-372
```javascript
const phase2Status = ref('editing')
const opponentSubmitted = ref(false)
const opponentCode = ref('')
const myEvaluation = ref(null)
const opponentEvaluation = ref(null)
const phase2WaitingTimeout = ref(30)
```

- [x] 제출 로직 개선
  - 첫 제출 후 "waiting" 상태로 전환
  - 체크리스트 기반 로컬 평가
  - 점수 계산 및 저장

**코드 위치**: Line 786-850
```javascript
function evaluateDesign() {
  phase2Status.value = 'waiting'
  myEvaluation.value = { code, checkCount, totalPoints }
  rs.emitProgress(roomId.value, {
    phase: 'designSprint',
    state: 'submitted',
    code: code,
    checksCompleted: checkCount,
    score: totalPoints,
    sid: rs.socket.value?.id
  })
  startPhase2WaitingTimeout()
}
```

- [x] 타이머 관리
  - 30초 대기 타이머 시작
  - 상대 제출 또는 타임아웃 감지
  - 타이머 자동 정리 (메모리 누수 방지)

**코드 위치**: Line 852-876
```javascript
function startPhase2WaitingTimeout() {
  if (phase2WaitingInterval) clearInterval(phase2WaitingInterval)

  phase2WaitingInterval = setInterval(() => {
    phase2WaitingTimeout.value--

    if (phase2WaitingTimeout.value <= 0 || opponentSubmitted.value) {
      clearInterval(phase2WaitingInterval)
      phase2WaitingInterval = null
      finalizePhase2()
    }
  }, 1000)
}
```

- [x] UI 상태별 표시
  - EDITING: 기존 시나리오 + 체크리스트 + 에디터
  - WAITING: 내 제출 + 상대 대기 (또는 상대 코드 표시)
  - EVALUATED: 평가 완료 → 자동으로 결과 화면

**코드 위치**: Line 149-225, 230-310

- [x] 스타일 추가
  - `.waiting-hud` - 대기 상태 HUD
  - `.code-preview` - 코드 미리보기
  - `.waiting-panel` - 대기 패널
  - `.waitingPulse` 애니메이션

**코드 위치**: Line 1063-1117

- [x] 타이머 정리 개선
  - `endGame()` 함수에서 `phase2WaitingInterval` 정리
  - `onUnmounted` 훅에서 모든 interval 정리
  - 메모리 누수 방지

**코드 위치**: Line 360, 903-904, 925-929

- [x] 게임 시작 시 상태 초기화
  - Phase 2 관련 변수 모두 초기화
  - 매 게임마다 깨끗한 상태에서 시작

**코드 위치**: Line 542-566

---

### 🔧 Backend (socket_server.py)

#### Phase 2 코드 수집 구조
- [x] Phase 2 제출 데이터 저장소 추가
  - `run_phase2_submissions` 딕셔너리
  - 방별 양쪽 코드 수집

**코드 위치**: Line 677-678
```python
run_phase2_submissions = {}  # { room_id: { sid: { code, checks, points }, ... } }
```

- [x] `run_progress` 함수 개선
  - Phase 2 제출 감지 (`state == 'submitted'`)
  - 양쪽 코드 수집
  - 로그 출력 (디버깅용)
  - 향후 LLM 평가 호출 준비

**코드 위치**: Line 730-761
```python
@sio.event
async def run_progress(sid, data):
    if data.get('phase') == 'designSprint' and data.get('state') == 'submitted':
        if room_id not in run_phase2_submissions:
            run_phase2_submissions[room_id] = {}

        run_phase2_submissions[room_id][sid] = {
            'code': data.get('code', ''),
            'checksCompleted': data.get('checksCompleted', 0),
            'totalPoints': data.get('score', 0)
        }

        if len(run_phase2_submissions[room_id]) >= 2:
            print(f"✅ Both players submitted in room {room_id}")

    await sio.emit('run_sync', data, room=room_id, skip_sid=sid)
```

---

## 📊 동작 흐름 검증

### Phase 1: Speed Fill (속도전)
```
Player 1: selectBlankAnswer('정답')
    ↓
handleBlankCorrect()
    ↓
scoreP1 += 100
    ↓
emitProgress({
  phase: 'speedFill',
  score: 100,
  sid: 'p1-sid'
})
    ↓ [Socket.io]
Backend: run_progress()
    ↓ broadcast (skip_sid='p1-sid')
    ↓
Player 2: onSync()
    ↓
scoreP1.value = 100 ✅ 즉시 업데이트!
```

### Phase 2: Design Sprint (설계 스프린트)
```
Player 1: submitDesign()
    ↓
evaluateDesign()
    ↓ Phase 2 상태: editing → waiting
    ↓
emitProgress({
  phase: 'designSprint',
  state: 'submitted',  ← 제출 신호
  code: '...',
  checksCompleted: 3,
  score: 500,
  sid: 'p1-sid'
})
    ↓ [Socket.io]
Backend: run_progress()
    ↓ 코드 저장 + 로그
    ↓ broadcast to Player 2
    ↓
Player 2: onSync()
    ↓
opponentSubmitted = true
opponentCode = '...'
    ↓
UI: 상대 코드 표시 + 30초 타이머 진행 중

Player 2 (옵션): submitDesign() or 30초 타임아웃
    ↓
finalizePhase2()
    ↓ phase2Status: waiting → evaluated
    ↓ 2초 후 자동으로 result 화면으로
```

---

## 🔌 Socket 이벤트 시퀀스

### Before (이전)
```
┌─────────────────────────────────────┐
│ Player 1 (SUBMIT)                   │
└────────────┬────────────────────────┘
             │
             ↓ run_progress

┌─────────────────────────────────────┐
│ Backend                             │
│ broadcast to room                   │
└────────────┬────────────────────────┘
             │
             ↓ run_sync

┌─────────────────────────────────────┐
│ Player 2 (onSync)                   │
│ ❌ 즉시 게임 종료                     │
└─────────────────────────────────────┘
```

### After (개선됨)
```
┌─────────────────────────────────────┐
│ Player 1 (SUBMIT)                   │
└────────────┬────────────────────────┘
             │
             ↓ run_progress (state='submitted')

┌─────────────────────────────────────┐
│ Backend                             │
│ ✅ 코드 저장                         │
│ 👀 상태 감지: 2/2 플레이어 제출됨    │
│ broadcast to room                   │
└────────────┬────────────────────────┘
             │
             ↓ run_sync

┌─────────────────────────────────────┐
│ Player 2 (onSync)                   │
│ ✅ opponentSubmitted = true         │
│ ✅ opponentCode 저장                 │
│ ✅ UI: "상대 코드 보여줌"            │
│ ⏳ 30초 또는 제출 대기                │
│ ✅ 조건 충족 시 평가 완료            │
└─────────────────────────────────────┘
```

---

## 🧪 테스트 시나리오

### Scenario 1: 양쪽 모두 제출 (정상 케이스)
```
1. Player 1 코드 작성 → SUBMIT
   → phase2Status: editing → waiting
   → HUD: "📤 YOU SUBMITTED | ⏳ 30s"
   → UI: 내 코드 표시

2. Player 2가 run_sync 수신
   → opponentSubmitted = true
   → opponentCode 저장
   → HUD: "✅ OPPONENT SUBMITTED"
   → UI: 상대 코드 표시

3. Player 2 코드 작성 → SUBMIT
   → phase2Status: waiting → evaluated
   → finalizePhase2() 즉시 호출
   → 2초 후 result 화면

✅ 결과: 양쪽 모두 점수 + 평가 표시
```

### Scenario 2: 상대 미제출 (타임아웃)
```
1. Player 1 SUBMIT
   → phase2Status: editing → waiting
   → 30초 타이머 시작

2. Player 2가 제출하지 않음
   → 30초 경과
   → phase2WaitingTimeout.value = 0
   → finalizePhase2() 호출
   → 2초 후 result 화면

✅ 결과: 한쪽만 제출했어도 게임 완료
```

### Scenario 3: 빠른 연속 제출
```
1. Player 1 SUBMIT (t=0s)
   → opponentSubmitted = false
   → 타이머: 30s → 29s → 28s...

2. Player 2 즉시 SUBMIT (t=1s)
   → opponentSubmitted = true
   → clearInterval() 호출
   → finalizePhase2() 즉시 호출
   → 2초 후 result 화면

✅ 결과: 타이머 상관없이 양쪽 제출 시 즉시 완료
```

---

## 📋 코드 위치 요약

| 기능 | 파일 | 라인 |
|------|------|------|
| Phase 2 상태 변수 | LogicRun.vue | 363-372 |
| onSync 리스너 | LogicRun.vue | 308-330 |
| evaluateDesign | LogicRun.vue | 786-850 |
| startPhase2WaitingTimeout | LogicRun.vue | 852-876 |
| finalizePhase2 | LogicRun.vue | 870-876 |
| WAITING UI | LogicRun.vue | 149-225 |
| 대기 상태 스타일 | LogicRun.vue | 1063-1117 |
| 타이머 정리 | LogicRun.vue | 360, 903-904, 925-929 |
| 상태 초기화 | LogicRun.vue | 542-566 |
| 백엔드 코드 수집 | socket_server.py | 677-678 |
| run_progress 개선 | socket_server.py | 730-761 |

---

## 🚀 다음 단계 (선택사항)

### 즉시 구현 가능
- [ ] LLM 평가 API 호출 (`finalizePhase2()` 함수에서)
- [ ] 평가 결과 UI 표시
- [ ] 두 코드의 차이점 시각화

### 향후 개선
- [ ] 상대 코드 문법 하이라이팅
- [ ] 평가 결과 비교 차트
- [ ] 전체 게임 통계 분석

---

## ⚠️ 알려진 제한사항

### 현재 구현
- ✅ 실시간 동기화
- ✅ 30초 대기 타이머
- ✅ 상대 코드 표시
- ⏳ LLM 평가 (준비만 됨, 아직 미구현)

### 주의사항
1. **네트워크 지연**: 소켓 통신이 느리면 타이머가 정확하지 않을 수 있음
2. **동시 제출**: 거의 동시에 제출하면 race condition 발생 가능
3. **메모리**: 장시간 플레이 시 interval 정리 필수 (이미 구현됨)

---

## ✨ 기대 효과

### 사용자 경험 개선
1. 🎮 **공정한 경쟁**: 양쪽 모두 제출할 기회
2. 📚 **학습 효과**: 상대 코드 분석 가능
3. ⚡ **실시간 피드백**: 상대 진행도 즉시 확인

### 개발 안정성
1. 🔒 **상태 관리**: 명확한 상태 전환
2. 🛡️ **메모리 관리**: 타이머 자동 정리
3. 📊 **디버깅**: 백엔드 로그로 추적 가능

---

## 📝 변경 이력

### 2026-02-25
- Phase 1 동기화 개선 (데이터 매핑 수정)
- Phase 2 대기 상태 구현
- 상태 머신 추가
- 30초 타이머 구현
- 타이머 메모리 정리
- 백엔드 코드 수집 구조 추가

---

**작성자**: Claude Code
**최종 수정**: 2026-02-25
**상태**: ✅ 준비 완료 (테스트 대기)
