# AI 코치 내부 동작 원리 (2026-02-24)

**파일:** `backend/core/views/coach_view.py`
**API Endpoint:** `/api/core/ai-coach/chat/` (POST)

---

## 🏗️ 전체 아키텍처

```
사용자 질문
  ↓
[1] Guardrail (범위 밖 질문 차단)
  ↓
[2] Intent Analysis (의도 분석: A-G 7가지 타입)
  ↓
[3] Response Strategy (의도별 프롬프트 선택)
  ↓
[4] Agent Loop (도구 자율 호출, 최대 5회 반복)
  ↓
[5] Tool Execution (도구 호출 + 캐싱)
  ↓
[6] Chart Generation (차트 데이터 생성)
  ↓
[7] SSE Streaming (클라이언트에 실시간 전달)
```

---

## 1️⃣ Guardrail 단계 (범위 밖 질문 차단)

### 목적
학습 코칭 범위 밖의 질문 사전 차단

### 동작
```python
if is_off_topic(user_message):
    # 범위 밖 감지 → 즉시 응답 & 종료
    yield _sse({
        "type": "status",
        "message": "학습 코칭 범위 밖의 질문이에요",
        "variant": "blocked"
    })
    yield _sse({
        "type": "token",
        "token": GUARDRAIL_MESSAGE  # 사전 정의 메시지
    })
    return  # 다른 단계 스킵
```

### 예시
- ❌ "오늘 날씨는?" → 차단
- ❌ "피자 레시피 알려줘" → 차단
- ✅ "내 약점을 분석해줘" → 통과

---

## 2️⃣ Intent Analysis 단계 (의도 분석)

### 목적
사용자의 실제 의도를 7가지 타입 중 하나로 분류

### 의도 타입 (A-G)
| 타입 | 이름 | 설명 | 예시 |
|------|------|------|------|
| **A** | 데이터 조회형 | 자신의 학습 상태/약점 조회 | "내 약점을 분석해줘" |
| **B** | 학습 방법형 | 학습 방법/전략 문의 | "약점을 극복하는 방법은?" |
| **C** | 동기부여형 | 성장/성취 관련 | "내가 얼마나 성장했어?" |
| **D** | 범위 밖 | 학습과 무관 | (이미 Guardrail에서 차단) |
| **E** | 문제 풀이형 | 특정 문제 풀이 지원 | "이 문제 어떻게 풀어?" |
| **F** | 개념 설명형 | 프로그래밍 개념 설명 | "클래스가 뭐야?" |
| **G** | 의사결정형 | 문제 선택/경로 결정 | "어떤 문제를 풀어야 해?" |

### 동작 (LLM 호출)
```python
intent_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": INTENT_ANALYSIS_PROMPT  # 의도 분류 프롬프트
        },
        {
            "role": "user",
            "content": user_message
        }
    ],
    max_completion_tokens=500,
)

# 응답: JSON 형식
{
    "intent_type": "A",           # A-G 중 하나
    "confidence": 0.90,            # 신뢰도 (0-1)
    "reasoning": "...",            # 판단 근거
    "key_indicators": [...]        # 핵심 키워드
}
```

### SSE 이벤트
```python
yield _sse({
    "type": "intent_detected",
    "intent_type": "A",
    "intent_name": "데이터 조회형",
    "confidence": 0.90,
    "reasoning": "사용자가 자신의 학습 상태와 약점을 조회하고자 하는 의도...",
    "key_indicators": ["약점", "분석"]
})
```

---

## 3️⃣ Chart 표시 여부 판단

### 목적
Intent + 사용자 메시지 기반으로 **차트 필요 여부** 동적 결정

### 판단 규칙 (3단계)

#### 1단계: 명시적 요청 확인
```python
# 명시적 비표시 키워드 → 무조건 차트 NO
text_only_keywords = {"분석해", "설명해", "알려", "어떻게", "왜", "뭐야"}
→ 차트 표시하지 않음

# 명시적 표시 키워드 → 무조건 차트 YES
chart_keywords = {"차트", "시각화", "그래프", "리포트", "보여줘", "데이터를"}
→ 차트 표시
```

#### 2단계: Intent별 기본값
```python
intent_defaults = {
    "A": True,   # 데이터 조회: 기본 표시
    "B": False,  # 학습 방법: 텍스트만
    "C": True,   # 동기부여: 기본 표시
    "D": False,  # 범위 밖: 불필요
    "E": False,  # 문제 풀이: 텍스트만
    "F": False,  # 개념 설명: 텍스트만
    "G": True,   # 의사결정: 기본 표시 (비교)
}
```

### 예시
```
요청: "내 약점을 분석해줘"
1. "분석해" 키워드 → text_only_keywords 포함 → NO
   (선택: 답변 → 차트)

요청: "유닛별 성적을 보여줘"
1. "보여줘" 키워드 → chart_keywords 포함 → YES
   (선택: 답변 + 차트)

요청: "내가 얼마나 성장했어?"
1. 명시적 요청 없음
2. Intent C (동기부여) → intent_defaults["C"] = True
   (선택: 답변 + 차트)
```

---

## 4️⃣ Response Strategy 단계

### 목적
Intent별 **최적화된 프롬프트** 선택

### 동작
```python
strategy = RESPONSE_STRATEGIES.get(intent_type, RESPONSE_STRATEGIES["B"])
system_prompt = strategy["system_prompt"]  # Intent A용 프롬프트 선택

# 예: Intent A (데이터 조회형) 프롬프트
# "사용자의 학습 데이터를 분석하여 구체적인 약점과 개선 방안을 제시하세요..."
```

### Intent별 프롬프트 예시
```
A (데이터 조회):
→ "학습 데이터 분석 → 약점 도출 → 개선 방안 제시"

B (학습 방법):
→ "약점 원인 분석 → 학습 전략 제안 → 실행 계획 수립"

C (동기부여):
→ "성장 인식 → 성취 강조 → 미래 목표 제시"

E (문제 풀이):
→ "문제 이해 → 풀이 과정 설명 → 핵심 개념 강조"
```

---

## 5️⃣ Agent Loop (도구 자율 호출)

### 목적
LLM이 필요한 도구를 **스스로 판단**하며 최대 5회 반복

### 동작 흐름

```
반복 1:
  ├─ thinking 이벤트 ("질문을 분석하고 있어요...")
  ├─ LLM 호출 (Tool 제공)
  ├─ Tool 호출 여부 판단
  │   ├─ Tool 호출 있음 → Tool 실행 (Step 6로)
  │   └─ Tool 호출 없음 → 최종 응답 (Step 7로)

반복 2 (Tool이 실행된 경우만):
  ├─ 도구 결과를 메시지에 추가
  ├─ LLM 호출 (다시)
  └─ ...

반복 3-5:
  └─ 필요시 반복
```

### max_iterations = 5
```python
# 각 반복에서 다른 thinking 메시지 출력
thinking_messages = [
    "질문을 분석하고 필요한 데이터를 판단하고 있어요...",
    "추가 데이터가 필요한지 확인하고 있어요...",
    "분석 결과를 종합하고 있어요...",
    "최종 코칭 내용을 정리하고 있어요...",
    "마무리 중이에요...",
]

# 5회 반복 후에도 최종 응답이 없으면
→ "분석이 복잡하여 일부만 완료되었습니다." 메시지
```

### Tool Filtering
```python
# Intent별로 **사용 가능한 도구만 제공** (자율성은 유지)
intent_config = INTENT_TOOL_MAPPING.get(intent_type, {})
allowed_tools = intent_config.get("allowed", [])
filtered_tools = [t for t in COACH_TOOLS if t["function"]["name"] in allowed_tools]

# 예: Intent A는 [성적 조회, 약점 분석] 만 제공
#     Intent B는 [성적 조회, 약점 분석, 학습 자료 추천] 제공
```

---

## 6️⃣ Tool Execution & Caching

### 목적
필요한 도구를 실행하고 **중복 호출 방지**

### 동작

#### 1단계: Tool 호출 탐지
```python
for chunk in stream:
    if delta.tool_calls:  # LLM이 도구 호출 결정
        is_tool_call = True
        # tool_calls_data에 저장
        # 예: {
        #   "id": "call_123",
        #   "name": "get_student_scores",
        #   "arguments": "{\"unit_id\": \"unit01\"}"
        # }
```

#### 2단계: Token 버퍼링 (Tool 호출 없을 때만)
```python
# Tool 호출이 없으면: 토큰을 버퍼에 모으기 (아직 전송 X)
if delta.content and not is_tool_call:
    buffered_tokens.append(delta.content)

# Tool 호출이 있으면: 즉시 전송
elif delta.content and is_tool_call:
    yield _sse({"type": "token", "token": delta.content})
```

#### 3단계: Tool 캐싱
```python
cache_key = f"{fn_name}:{json.dumps(fn_args_raw, sort_keys=True)}"
# 예: "get_student_scores:{"unit_id": "unit01"}"

if cache_key in called_tools_cache:
    # 이전에 실행한 결과 재사용
    result_data = called_tools_cache[cache_key]
else:
    # 처음 실행
    result_data = executor(profile, fn_args)
    called_tools_cache[cache_key] = result_data
```

#### 4단계: Tool 결과 전송
```python
yield _sse({
    "type": "step_result",
    "tool": "get_student_scores",
    "result": {
        # 성적 데이터
        # Pseudo Practice: 평균 65점, 최고 65점, 1/8문제 (12.5%)
        # Debug Practice: 평균 91.5점, 최고 100점, 4/7문제 (57.1%)
    }
})
```

### 사용 가능한 도구들
```python
COACH_TOOLS = [
    {
        "function": {
            "name": "get_student_scores",
            "description": "사용자의 전체 성적 조회"
        }
    },
    {
        "function": {
            "name": "get_weak_areas",
            "description": "약점 분석 (특정 유닛)"
        }
    },
    # ... 기타 도구들
]
```

---

## 7️⃣ 차트 데이터 생성 & SSE 순서

### 목적
분석 결과를 시각화하여 더 쉽게 이해할 수 있도록 함

### 동작 (Tool 호출 없을 때)

```python
if not is_tool_call:
    # Step 1: 차트를 먼저 생성/전송
    if should_show_chart:
        chart_summaries = generate_chart_data_summary(profile, intent_type)
        for chart in chart_summaries:
            yield _sse({
                "type": "chart_data",
                "intent_type": "A",
                "chart": {
                    "title": "유닛별 성적",
                    "chart_type": "bar",
                    "data": {
                        "labels": ["Pseudo", "Debug", "System"],
                        "datasets": [...]
                    }
                }
            })

    # Step 2: 버퍼된 토큰들을 전송 (최종 답변)
    for token in buffered_tokens:
        yield _sse({"type": "token", "token": token})

    # Step 3: 완료 이벤트
    yield _sse({"type": "final"})
    yield "data: [DONE]\n\n"
    return
```

### 차트 타입
```
1. bar: 막대 그래프 (단위별 성적 비교)
2. line: 선 그래프 (시간 경과에 따른 성적)
3. radar: 레이더 차트 (약점 분포)
4. progress: 진행률 바 (완성도)
5. table: 표 (상세 데이터)
```

---

## 8️⃣ SSE 이벤트 순서 (최종)

### 완전한 흐름

```
[클라이언트 → 서버: 질문 전송]

↓ [1] Guardrail 통과
  → type: "thinking", stage: "intent_analysis"

↓ [2] Intent 분석 완료
  → type: "intent_detected" (A/B/C 등)

↓ [3] 응답 전략 수립
  → type: "thinking", stage: "response_strategy"

↓ [4] Agent Loop 시작
  ├─ Iteration 1
  │  ├─ → type: "thinking" (분석 중)
  │  ├─ → type: "step_start" (도구 호출)
  │  └─ → type: "step_result" (결과)
  │
  ├─ Iteration 2 (필요시)
  │  └─ ...
  │
  └─ Tool 호출 없음 → [5]로

↓ [5] 차트 생성 (필요 시)
  → type: "chart_data" ✅ (먼저)

↓ [6] 최종 답변 스트리밍
  → type: "token" (한 글자씩 실시간)
  → type: "token"
  → type: "token"
  → ...

↓ [7] 완료
  → type: "final"
  → [DONE]

[클라이언트: 모든 이벤트 수신 완료]
```

### 각 이벤트 타입
```javascript
{
    type: "thinking"         // 사고 중 표시
    type: "intent_detected"  // 의도 분석 완료
    type: "step_start"       // 도구 호출 시작
    type: "step_result"      // 도구 결과
    type: "token"            // 답변 토큰 (스트리밍)
    type: "chart_data"       // 차트 데이터
    type: "error"            // 에러
    type: "final"            // 완료
}
```

---

## 🔄 예시: "내 약점을 분석해줘"

### 1단계: Guardrail 통과 ✅

### 2단계: Intent Analysis
```
입력: "내 약점을 분석해줘"
↓
LLM 분석
↓
결과: Intent A (데이터 조회형, 신뢰도 90%)
```

### 3단계: Chart 표시 여부
```
사용자 메시지: "내 약점을 분석해줘"
키워드 "분석해" 포함 → text_only_keywords 매칭
→ should_show_chart = False
```

### 4단계: Response Strategy
```
Intent A 선택 → 데이터 조회 최적화 프롬프트 사용
```

### 5단계: Agent Loop
```
Iteration 1:
├─ thinking: "질문을 분석하고 필요한 데이터를 판단하고 있어요..."
├─ LLM 호출
├─ Tool 호출 결정: "get_weak_areas" 호출
├─ step_start: "약점 분석" (unit_id: unit01)
├─ Tool 실행: 약점 데이터 추출
└─ step_result: 분석 결과 표시

Iteration 2:
├─ thinking: "추가 데이터가 필요한지 확인하고 있어요..."
├─ LLM 호출
├─ Tool 호출 결정: "get_weak_areas" 호출 (unit03)
├─ step_start: "약점 분석" (unit_id: unit03)
├─ Tool 실행
└─ step_result: 분석 결과 표시

Iteration 3:
├─ thinking: "분석 결과를 종합하고 있어요..."
├─ LLM 호출
└─ Tool 호출 없음 → [6단계]로
```

### 6단계: 차트 생성 (이 경우 NO)
```
should_show_chart = False
→ 차트 스킵
```

### 7단계: 최종 답변 스트리밍
```
토큰: "당신의 약점은 다음과 같습니다..."
토큰: "1. Design Pattern (점수: 15점)"
토큰: "2. Edge Case Handling (점수: 10점)"
토큰: "..."
```

### 8단계: 완료
```
→ type: "final"
→ [DONE]
```

---

## 📊 동작 최적화

### 1. Tool Caching
```
요청: "내 성적을 보여줘"
요청: "성적 기반으로 추천해줘"

첫 번째 요청:
└─ get_student_scores 실행 → 캐시 저장

두 번째 요청:
└─ get_student_scores (캐시 히트) → 즉시 반환 ✅
```

### 2. 토큰 버퍼링
```
문제: Tool 없을 때 토큰이 즉시 나가면
      LLM 처리 전에 화면에 답변이 보임

해결: 토큰을 버퍼에 모아뒀다가
      차트 생성 완료 후 일괄 전송
```

### 3. Intent별 Tool 필터링
```
Intent A에 불필요한 도구(학습자료추천)는
제공하지 않음 → 토큰 절감 ✅
```

---

## 🎯 핵심 포인트

1. **2-Stage LLM**
   - Stage 1: Intent Analysis (의도만 분석)
   - Stage 2: Response Strategy + Agent Loop (답변 생성)

2. **자율적 도구 호출**
   - LLM이 필요한 도구를 직접 선택
   - Intent별 도구 필터링으로 범위 제한

3. **실시간 스트리밍**
   - SSE로 각 단계 진행 상황 실시간 전달
   - 사용자 경험 향상

4. **성능 최적화**
   - Tool 캐싱 (중복 호출 방지)
   - Token 버퍼링 (SSE 순서 제어)
   - Intent별 Tool 필터링 (토큰 절감)

5. **UX 개선**
   - 차트를 최종답변 바로 위에 배치
   - 스크롤 불필요
   - 자연스러운 정보 흐름
