# AI 챗봇 동작 방식 (How It Works)
**간단하고 명확한 설명서**

---

## 📍 1줄 요약

**사용자 질문 → 의도 파악(7가지) → Intent별 맞춤형 도구 자동 호출 → 실시간 답변 전달**

---

## 🎯 핵심 플로우

```
┌─────────────────┐
│ 사용자 질문     │  "내 약점이 뭐야?"
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ [1] 범위 확인 (가드레일) │ ❌ "날씨 어때?" → 차단
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ [2] 의도 분석 (Intent)       │ 7가지 타입 중 분류
│    (LLM 호출 1)              │ A, B, C, E, F, G
└────────┬─────────────────────┘
         │
         ▼
┌────────────────────────────┐
│ [3] 도구 선택 & 자동 호출  │ Intent별로 필요한 도구만
│    (LLM 호출 2+)           │ (최대 5회 반복)
│    - get_user_scores       │
│    - get_weak_points       │
│    - get_recent_activity   │
│    - recommend_next_problem│
└────────┬───────────────────┘
         │
         ▼
┌──────────────────────────┐
│ [4] 차트 생성 (필요시)   │ 사용자 요청 키워드 기반
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ [5] 답변 전달 (SSE)      │ 실시간 스트리밍
│    - 의도 분석 결과      │
│    - 도구 호출 진행도    │
│    - 차트 데이터        │
│    - 최종 답변           │
└──────────────────────────┘
```

---

## 📋 5단계 상세 분석

### [Step 1] 범위 확인 (Guardrail)

**목적:** LLM 호출 전에 명백한 범위 밖 질문 사전 차단

**판단 기준**
```python
✅ 학습 관련 키워드 포함
   - "성적", "약점", "공부", "학습", "추천", "문제", "풀이"
   - "디버깅", "설계", "버그", "코드", "분석"
   - "자신감", "포기", "어렵", "잘할" (감정 포함)

❌ 범위 밖 (2가지 타입)
   - 욕설/비난: "바보", "멍청", "시발"
   - 잡담: "날씨", "맛집", "영화", "주식", "축구"
   - 무의미: "ㅋㅋㅋ", "???" (3자 이하)
```

**응답**
```
범위 밖 감지 → 즉시 메시지 반환
"나는 이 플랫폼의 학습 데이터를 기반으로 코칭하는 전문 코치야!
다음과 같이 질문해보세요:
- 내 약점이 뭐야?
- 디버깅 공부는 어떻게 하면 좋아?
- 다음에 뭘 풀면 좋을까?"
```

---

### [Step 2] 의도 분석 (Intent Analysis)

**목적:** 사용자의 실제 의도를 7가지 타입으로 분류

**7가지 Intent 타입**

| 타입 | 이름 | 설명 | 예시 | 특징 |
|------|------|------|------|------|
| **A** | 데이터 조회형 | 성적/약점 조회 | "내 성적 보여줘" | 수치, 기록 조회 |
| **B** | 학습 방법형 | 학습 전략/로드맵 | "약점을 극복하려면?" | HOW, 단계, 전략 |
| **C** | 동기부여형 | 감정/자신감 | "정말 잘할 수 있을까?" | 감정어, 부정표현 |
| **D** | 범위 밖 | 학습과 무관 | "날씨 어때?" | [Step 1에서 차단] |
| **E** | 문제 풀이형 | 특정 문제 도움 | "이 문제 못 풀었어" | 구체적 문제 언급 |
| **F** | 개념 설명형 | 개념 이해 요청 | "DFS가 뭐야?" | 개념명, "뭐야?" |
| **G** | 의사결정형 | 비교/추천 | "어떤 문제를 풀어야 해?" | 선택지 제시, 비교 |

**Intent 판정 기준**

```
명확한 구분:
  A vs B: A는 "지금 내 성적이 몇 점?" (결과), B는 "어떻게 올릴래?" (방법)
  A vs F: A는 "약점이 뭐?" (리스트), F는 "약점이 왜 생겨?" (설명)
  E vs F: E는 "이 문제 뭐가 틀렸나?" (구체적), F는 "재귀가 뭐야?" (개념)
```

**LLM 호출**
```python
model: "gpt-4o-mini"
prompt: INTENT_ANALYSIS_PROMPT (100줄 규칙)
input: user_message
output: JSON 형식
{
    "intent_type": "A",           # A-G 중 하나
    "confidence": 0.95,           # 신뢰도 0-1
    "reasoning": "사용자가...",   # 판단 근거
    "key_indicators": ["약점", "분석"]  # 핵심 키워드
}
```

**응답 (SSE 이벤트)**
```javascript
{
  type: "intent_detected",
  intent_type: "A",
  intent_name: "데이터 조회형",
  confidence: 0.95,
  reasoning: "사용자가 자신의 약점을 조회하려는 의도...",
  key_indicators: ["약점", "분석"]
}
```

---

### [Step 3] 도구 선택 & 자동 호출 (Agent Loop)

**목적:** LLM이 필요한 도구를 자율적으로 선택하며 상호작용

**사용 가능한 도구 (6개)**

| 도구명 | 설명 | Intent별 사용 |
|--------|------|----------|
| `get_user_scores` | 유닛별 평균점수, 최고점수, 풀이수, 완료율 | A, B, G |
| `get_weak_points` | 특정 유닛의 약점(70점 미만 메트릭) | A, B |
| `get_recent_activity` | 최근 풀이 기록 | A, C |
| `recommend_next_problem` | 추천 문제 | B, G |
| `get_unit_curriculum` | 유닛 학습 목표, 개념, 팁 | B, F |
| `get_problem_explanation` | 특정 문제 설명 | E, F |

**Intent별 도구 필터링**
```python
INTENT_TOOL_MAPPING = {
    "A": ["get_user_scores", "get_weak_points"],
    "B": ["get_user_scores", "get_weak_points", "get_unit_curriculum", "recommend_next_problem"],
    "C": ["get_user_scores", "get_recent_activity"],
    "E": ["get_problem_explanation"],
    "F": ["get_unit_curriculum"],
    "G": ["get_user_scores", "recommend_next_problem"],
}

# 효과:
# - Intent A는 불필요한 도구 제공 안 함 (토큰 절감)
# - Intent B는 충분한 도구 제공 (깊이 있는 분석)
# - LLM의 자율성은 유지 (tool_choice="auto")
```

**반복 프로세스 (Max Iterations = 5)**

```
반복 1:
  ├─ thinking: "질문을 분석하고 필요한 데이터를 판단 중..."
  ├─ LLM 호출: 답변 + 도구 선택 (스트리밍)
  ├─ 도구 호출?
  │  ├─ Yes: Step 실행
  │  └─ No: 최종 답변으로 이동
  │
  반복 2:
  ├─ thinking: "추가 데이터가 필요한지 확인 중..."
  ├─ LLM 호출 (이전 결과 포함)
  ├─ 도구 호출?
  │  ├─ Yes: 추가 Step 실행
  │  └─ No: 최종 답변으로 이동
  │
  반복 3-5: (필요시 반복)
  │
  Max 도달: "분석이 복잡합니다. 더 구체적으로 질문해주세요."
```

**도구 호출 & 캐싱**

```python
# 도구 호출 감지
if delta.tool_calls:
    is_tool_call = True
    tool_calls_data[id] = {
        "name": "get_weak_points",
        "arguments": {"unit_id": "unit01"}
    }

# 캐싱 (중복 호출 방지)
cache_key = "get_weak_points:{'unit_id': 'unit01'}"

if cache_key in called_tools_cache:
    result = called_tools_cache[cache_key]  # 캐시 사용
else:
    result = execute_tool(...)
    called_tools_cache[cache_key] = result  # 캐시 저장
```

**도구 실행 응답 (SSE 이벤트)**
```javascript
// 도구 호출 시작
{
  type: "step_start",
  tool: "get_weak_points",
  arguments: {unit_id: "unit01"}
}

// 도구 결과
{
  type: "step_result",
  tool: "get_weak_points",
  result: {
    "unit01": {
      "weak_metrics": [
        {metric: "Edge Case", score: 45},
        {metric: "Security", score: 30},
        ...
      ]
    }
  }
}
```

---

### [Step 4] 차트 생성 (선택사항)

**목적:** 데이터를 시각화하여 더 쉽게 이해할 수 있도록 함

**차트 표시 결정 로직 (3단계)**

```
1단계: 명시적 요청 확인
  ├─ "보여줘", "차트", "그래프", "데이터를" 포함
  │  → 차트 표시 (YES)
  │
  ├─ "분석해", "설명해", "알려", "왜" 포함
  │  → 차트 비표시 (NO)
  │
  └─ 명시적 요청 없음 → 2단계로

2단계: Intent별 기본값
  ├─ A (데이터 조회): 표시 (YES)
  ├─ B (학습 방법): 비표시 (NO)
  ├─ C (동기부여): 표시 (YES)
  ├─ E (문제 풀이): 비표시 (NO)
  ├─ F (개념 설명): 비표시 (NO)
  └─ G (의사결정): 표시 (YES)

3단계: 결정
  → should_show_chart = True/False
```

**차트 데이터 선택**

```python
# 사용자 메시지 분석
user_message = "내 약점을 분석해줘"

# 데이터 타입 결정
data_type = _determine_data_type(user_message)
# "약점" 키워드 → "metric"

# 해당 차트 생성 함수 호출
if data_type == "metric":
    chart = _generate_metric_chart(profile)  # Radar 차트
elif data_type == "chronological":
    chart = _generate_chronological_chart(profile)  # Line 차트
else:
    chart = _generate_unit_chart(profile)  # Bar 차트 (기본)
```

**차트 타입**

| 타입 | 설명 | 사용 케이스 |
|------|------|------------|
| **Bar** | 막대 그래프 | 유닛별/메트릭별 수치 비교 |
| **Line** | 선 그래프 | 시간 경과에 따른 추이 |
| **Radar** | 레이더 차트 | 약점 분포 (다각형) |
| **Progress** | 진행률 바 | 완료율, 진행도 |
| **Table** | 표 | 상세 데이터 |

---

### [Step 5] 답변 전달 (SSE 스트리밍)

**목적:** 실시간으로 진행 상황을 클라이언트에 전달

**이벤트 타입**

```javascript
// 1. 사고 중 표시
{type: "thinking", message: "분석 중입니다..."}

// 2. 의도 분석 완료
{
  type: "intent_detected",
  intent_type: "A",
  confidence: 0.95,
  ...
}

// 3. 도구 호출 시작
{type: "step_start", tool: "get_weak_points", arguments: {...}}

// 4. 도구 결과
{type: "step_result", tool: "get_weak_points", result: {...}}

// 5. 차트 데이터
{
  type: "chart_data",
  chart: {
    chart_type: "radar",
    title: "메트릭 분석",
    data: {...}
  }
}

// 6. 최종 답변 (토큰 단위 스트리밍)
{type: "token", token: "당신의"}
{type: "token", token: " 약점은"}
{type: "token", token: " ..."}

// 7. 완료
{type: "final"}
[DONE]
```

**SSE 이벤트 순서 (최종)**

```
의도분석 배지 표시
  ↓
사용자 질문 메시지
  ↓
Timeline (thinking 메시지들)
  ↓
도구 호출 진행도 (step_start, step_result)
  ↓
차트 데이터 (필요시)  ← 토큰 이전에 먼저 전송
  ↓
최종 답변 토큰 (글자 단위 실시간)
  ↓
완료
```

**토큰 버퍼링**

```python
# Tool 호출이 없을 때만 토큰을 버퍼에 모음
buffered_tokens = []

if delta.content and not is_tool_call:
    buffered_tokens.append(delta.content)  # 버퍼 저장 (아직 전송 X)

# Tool 호출이 있으면 즉시 전송
elif delta.content and is_tool_call:
    yield _sse({"type": "token", "token": delta.content})

# 최종 처리
if not is_tool_call:
    # 1. 차트 먼저 전송 (있으면)
    if should_show_chart:
        yield chart_data

    # 2. 버퍼된 토큰 일괄 전송
    for token in buffered_tokens:
        yield token
```

---

## 🔄 실제 예시: "내 약점을 분석해줘"

### 전체 흐름

```
사용자: "내 약점을 분석해줘"

┌─ Step 1: 가드레일 확인
│  └─ "약점", "분석" → 학습 관련 키워드 ✅ 통과

┌─ Step 2: 의도 분석 (LLM 호출 1)
│  ├─ Input: "내 약점을 분석해줘"
│  ├─ Output:
│  │  {
│  │    "intent_type": "A",
│  │    "confidence": 0.95,
│  │    "reasoning": "사용자가 자신의 약점(metrics)을 조회...",
│  │    "key_indicators": ["약점", "분석"]
│  │  }
│  └─ SSE: intent_detected 이벤트 전송

┌─ Step 3: 차트 표시 여부 판단
│  ├─ "분석해" 키워드 포함
│  ├─ text_only_keywords 매칭
│  └─ should_show_chart = False

┌─ Step 4: Agent Loop (LLM 호출 2+)
│  ├─ Intent A 선택 → 필터링된 도구 제공
│  │  - get_user_scores (O)
│  │  - get_weak_points (O)
│  │  - (다른 도구는 제공 X)
│  │
│  ├─ Iteration 1:
│  │  ├─ thinking: "질문을 분석하고 데이터 판단 중..."
│  │  ├─ LLM: "약점을 분석하겠습니다" → get_weak_points 호출 결정
│  │  ├─ step_start: get_weak_points (unit01)
│  │  ├─ 도구 실행: DB 조회
│  │  │  └─ Design (60), EdgeCase (35), Security (25), ...
│  │  └─ step_result: 약점 데이터 전송
│  │
│  ├─ Iteration 2:
│  │  ├─ thinking: "추가 데이터 확인 중..."
│  │  ├─ LLM: (unit02, unit03도 확인하려면) → get_weak_points 호출
│  │  ├─ step_start: get_weak_points (unit02)
│  │  ├─ 도구 실행: unit02 약점 조회
│  │  └─ step_result: unit02 약점 전송
│  │
│  └─ Iteration 3:
│     ├─ thinking: "분석 결과 종합 중..."
│     ├─ LLM: "도구 호출 결정 없음" → 최종 응답 생성으로 이동
│     └─ (반복 종료)

┌─ Step 5: 차트 생성
│  └─ should_show_chart = False → 스킵

┌─ Step 6: 최종 답변 전송
│  ├─ 토큰 버퍼에서 꺼내기
│  ├─ SSE token 이벤트로 실시간 전송
│  ├─ "당신의 약점은 다음과 같습니다:\n"
│  ├─ "1. Design Pattern (점수: 60점)\n"
│  ├─ "2. Edge Case Handling (점수: 35점)\n"
│  └─ ...

┌─ Step 7: 완료
│  ├─ SSE final 이벤트
│  └─ [DONE]

클라이언트에서:
  ├─ 의도분석 배지: "데이터 조회형 (신뢰도 95%)"
  ├─ 타임라인: 분석 과정 시각화
  ├─ 최종 답변: "당신의 약점은 다음과 같습니다..."
  └─ (차트 없음 - text_only_keywords 매칭)
```

---

## 📊 성능 최적화

### 1. Tool Caching
```
문제: "내 성적을 보여줘" → "성적 기반 추천해줘"
      같은 get_user_scores 중복 호출

해결:
cache_key = "get_user_scores:{}"
첫 호출: 실행 → 캐시 저장
두 번째: 캐시 사용 → 즉시 반환 ✅
```

### 2. Intent별 도구 필터링
```
문제: 모든 도구를 LLM에 제공 → 토큰 낭비

해결:
Intent A: 2개 도구만 제공 (조회 전용)
Intent B: 4개 도구 제공 (깊이 있는 분석)
Intent E: 1개 도구만 제공 (문제 설명)
→ 필요한 도구만 제공 ✅
```

### 3. Token Buffering
```
문제: 토큰이 즉시 나감 → 차트 준비 전에 답변 보임

해결:
Tool 없을 때: 토큰을 버퍼에 모으기
차트 생성 후: 버퍼된 토큰 일괄 전송 ✅
```

### 4. Guardrail 필터링
```
문제: LLM을 호출해야 범위 밖 질문 구분

해결:
키워드 기반 사전 필터링 (LLM 호출 전)
→ 불필요한 LLM 호출 방지 ✅
```

---

## 🔌 API 엔드포인트

```
POST /api/core/ai-coach/chat/

Request:
{
  "message": "내 약점을 분석해줘"
}

Response: SSE (Server-Sent Events)
- Content-Type: text/event-stream
- 실시간 스트리밍
```

---

## 🎓 주요 개념

### ReAct 패턴
```
Reasoning (추론) + Acting (행동) + Observation (관찰)

1. Reasoning: LLM이 상황 분석
2. Acting: 필요한 도구 선택 & 호출
3. Observation: 도구 결과 수집
4. (반복) → Reasoning 2, Acting 2, ...
```

### Two-Stage LLM
```
Stage 1: Intent Analysis (빠름)
  - 사용자 의도만 파악 (7가지 분류)
  - 간단한 프롬프트
  - 비용 적음

Stage 2: Response Generation (깊음)
  - Intent 맞춤 프롬프트로 도구 호출 & 답변
  - 복잡한 상호작용
  - 비용 많음
```

### Tool Filtering
```
LLM의 자율성 + 범위 제한의 조합

tool_choice = "auto"  ← 도구 선택 자율성 유지
filtered_tools = [...]  ← Intent별로 필요한 도구만 제공
→ 예측 가능하면서 유연함
```

---

## 🚀 다음 단계 (개선 예정)

### 단기
- [ ] 동적 차트 형식 확대 (Metric, Chronological, Problem-wise)
- [ ] Tool 결과 캐싱 확대

### 중기
- [ ] Verification Agent (약점 극복 확인)
- [ ] 적응형 학습 경로 제안

### 장기
- [ ] AI 기반 문제 생성
- [ ] 멀티턴 대화 개선

---

## 📚 참고 문서

- `RELEASE_NOTES_2026-02-24.md` - 최근 변경사항 (20KB)
- `AI_COACH_INTERNAL_FLOW.md` - 아키텍처 상세분석 (15KB)
- `CHART_DYNAMIC_STRATEGY.md` - 동적 차트 전략 (8.8KB)

---

## 💭 Q&A

**Q1: 왜 Intent를 먼저 분석하나요?**
A: Intent를 알면 도구와 프롬프트를 최적화할 수 있습니다.
- Intent A는 빠른 응답 필요 (2개 도구만)
- Intent B는 깊이 있는 분석 필요 (4개 도구 제공)

**Q2: 도구 호출을 LLM이 결정하는 이유는?**
A: 유연성과 예측 가능성의 균형입니다.
- LLM 자율성: 상황에 따라 필요한 도구를 판단
- 범위 제한: Intent별로 필요한 도구만 제공

**Q3: 왜 토큰을 버퍼에 모나요?**
A: 차트를 먼저 보여주기 위함입니다.
- 토큰이 즉시 나가면 차트 준비 전에 답변이 보임
- 버퍼링으로 순서 제어

**Q4: 캐싱은 얼마나 효과적인가요?**
A: 같은 사용자의 중복 질문 시 매우 효과적입니다.
- 첫 호출: 실행 (1-2초)
- 캐시 히트: 즉시 반환 (< 100ms)

---

**문서 작성:** 2026-02-24
**대상:** 전체 팀원
**읽기 시간:** 15분
**업데이트:** 기능 변경시
