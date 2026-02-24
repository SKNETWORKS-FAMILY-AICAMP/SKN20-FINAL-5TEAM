# AI Coach 개선사항 (2026-02-24)

**Branch:** feat/coach-dev
**기준 커밋:** bdb68a8 (feat: 챗봇 그래프화)
**최종 변경:** coach_view.py, AICoach.vue 2개 파일

---

## 🎯 문제점

### 1. SSE 스트리밍 순서 문제
- **이전:** 최종 답변 토큰이 먼저 스트리밍 → 그 다음 차트 표시
- **현상:** 차트가 화면 아래 어딘가에 나타나서 스크롤 필요

### 2. max_iterations 문제
- Intent A (데이터 조회형)가 `max_iterations=2`로 제한됨
- 약점 분석 같은 복잡한 요청은 여러 도구 호출 필요 → 불충분
- 결과: "분석이 복잡하여 일부만 완료되었습니다" 메시지 발생

### 3. 모델 오류
- `gpt-5-mini` (존재하지 않는 모델) 사용

---

## ✅ 해결 방안

### Backend (coach_view.py)

#### 1️⃣ 모델명 수정
```python
# Before
stream = client.chat.completions.create(
    model="gpt-5-mini",  # ❌ 존재하지 않음
    ...
)

# After
stream = client.chat.completions.create(
    model="gpt-4o-mini",  # ✅ 올바른 모델
    ...
)
```

#### 2️⃣ 토큰 버퍼링 (SSE 순서 개선)
```python
# Before: 토큰을 즉시 전송
if delta.content:
    yield _sse({"type": "token", "token": delta.content})

# After: 토큰을 버퍼에 모으기
buffered_tokens = []

if delta.content and not is_tool_call:
    buffered_tokens.append(delta.content)  # 버퍼에 저장
elif delta.content and is_tool_call:
    yield _sse({"type": "token", "token": delta.content})  # 즉시 전송
```

#### 3️⃣ 차트 우선 렌더링 (Tool 호출 없을 때)
```python
# Before: 토큰 → 차트
if delta.content:
    yield _sse({"type": "token", ...})
# ... 이후 차트 생성

# After: 차트 → 토큰
if not is_tool_call:
    # 1. 차트 먼저 생성/전송
    if should_show_chart:
        chart_summaries = generate_chart_data_summary(profile, intent_type)
        for chart in chart_summaries:
            yield _sse({"type": "chart_data", ...})

    # 2. 버퍼된 토큰들 전송
    for token in buffered_tokens:
        yield _sse({"type": "token", "token": token})
```

#### 4️⃣ max_iterations 복원 (고정값)
```python
# Before: Intent별로 다르게 설정
intent_max_iterations = {
    "A": 2,   # 데이터 조회: 2회 ← 부족!
    "B": 4,
    "C": 2,
    ...
}
max_iterations = intent_max_iterations.get(intent_type, 3)

# After: 모든 Intent 동일하게 5회
max_iterations = 5
```

#### 5️⃣ max_iterations 도달 시에도 차트 먼저 전송
```python
# Before: 메시지 → 차트
yield _sse({"type": "token", "token": "분석이 복잡하여..."})
# ... 이후 차트 생성

# After: 차트 → 메시지
if should_show_chart:
    # 차트 먼저 생성/전송
    chart_summaries = generate_chart_data_summary(...)
    ...

# 메시지 전송
yield _sse({"type": "token", "token": "분석이 복잡하여..."})
yield _sse({"type": "final"})
```

---

### Frontend (AICoach.vue)

#### 렌더링 순서 변경
```html
<!-- Before -->
<div v-for="(msg, idx) in messages" :key="idx" class="message-block">
  <!-- 의도분석 배지 -->
  <div v-if="msg.intentData" class="intent-badge">...</div>

  <!-- 차트 (의도분석 바로 아래) --> ❌
  <div v-if="msg.charts && msg.charts.length > 0" class="charts-section">...</div>

  <!-- 유저메시지 -->

  <!-- Timeline (thinking, steps) -->

  <!-- 최종답변 -->
</div>

<!-- After -->
<div v-for="(msg, idx) in messages" :key="idx" class="message-block">
  <!-- 의도분석 배지 -->
  <div v-if="msg.intentData" class="intent-badge">...</div>

  <!-- 유저메시지 -->

  <!-- Timeline (thinking, steps) -->

  <!-- 차트 (Timeline 다음, 최종답변 바로 위) --> ✅
  <div v-if="msg.charts && msg.charts.length > 0" class="charts-section">...</div>

  <!-- 최종답변 -->
</div>
```

**결과:** 스크롤할 필요 없이 자연스러운 순서로 표시

---

## 📊 개선 결과

### 사용자 경험 플로우

**Before (문제 상황):**
```
의도분석 배지
  ↓
차트 (의도분석 아래, 화면 상단)
  ↓
Timeline (thinking, steps - 분석 진행) ← 스크롤 아래로 밀림
  ↓
최종답변 (스크롤 아래)
  ↓
차트 (또 다시 스크롤 아래) ← 다시 스크롤 올려야 함
```

**After (개선 후):**
```
의도분석 배지 (화면 상단)
  ↓
유저메시지
  ↓
Timeline (thinking, steps - 분석 진행)
  ↓
차트 (Timeline 다음, 화면에 바로 보임) ← 스크롤 불필요
  ↓
최종답변 (차트 바로 아래)
```

### 기술적 개선

| 항목 | Before | After |
|------|--------|-------|
| **모델** | gpt-5-mini ❌ | gpt-4o-mini ✅ |
| **max_iterations** | Intent별 (A:2, B:4, ...) | 고정 5 |
| **토큰 전송** | 즉시 전송 | 버퍼링 → 차트 후 전송 |
| **차트 위치** | 의도분석 아래 | Timeline 아래 (최종답변 위) |
| **max_iterations 초과 시** | 메시지만 전송 | 차트 먼저 → 메시지 |

---

## 📝 요약

총 5가지 개선:
1. ✅ 모델명 수정 (gpt-5-mini → gpt-4o-mini)
2. ✅ 토큰 버퍼링으로 SSE 순서 제어
3. ✅ 차트를 최종답변 바로 위에 배치
4. ✅ max_iterations를 5로 통일 (Intent A도 충분한 반복)
5. ✅ max_iterations 초과 시에도 차트 우선 렌더링

**결과:** 사용자가 스크롤하지 않고도 자연스럽게 분석 과정 → 차트 → 답변을 볼 수 있음

---

**파일 변경:**
- `backend/core/views/coach_view.py`: ~70줄 수정
- `frontend/src/features/dashboard/AICoach.vue`: ~50줄 이동 (순서 변경)
