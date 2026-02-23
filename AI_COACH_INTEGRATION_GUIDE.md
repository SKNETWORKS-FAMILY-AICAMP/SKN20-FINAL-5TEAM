# AI 코치 고도화 버전 (v2.0) 통합 가이드

## 🚀 빠른 시작

### 백엔드 (Django)
```bash
# 1. coach_view_enhanced.py 확인
backend/core/views/coach_view_enhanced.py

# 2. 새 엔드포인트 등록됨
POST /api/core/ai-coach/chat-v2/
```

### 프론트엔드 (Vue)
```javascript
// 기존 (v1)
POST /api/core/ai-coach/chat/

// 신규 (v2 - 고도화)
POST /api/core/ai-coach/chat-v2/
```

---

## 📋 API 요청/응답 형식

### 요청 (Request)
```json
{
  "message": "내 성적 보여줘"
}
```

### 응답 (Response - SSE Streaming)

#### 1️⃣ 의도 분석 단계
```json
{
  "type": "intent_detected",
  "intent_type": "A",
  "intent_name": "데이터 조회형",
  "confidence": 0.95,
  "reasoning": "성적 데이터 조회 요청",
  "key_indicators": ["성적", "보여줘"]
}
```

#### 2️⃣ 사고 과정
```json
{
  "type": "thinking",
  "stage": "response_strategy",
  "message": "대응 전략을 수립하고 있어요..."
}
```

#### 3️⃣ 도구 호출 시작
```json
{
  "type": "step_start",
  "tool": "get_user_scores",
  "label": "성적 데이터 조회",
  "args": {}
}
```

#### 4️⃣ 도구 결과
```json
{
  "type": "step_result",
  "tool": "get_user_scores",
  "label": "성적 데이터 조회",
  "result": {
    "unit_id": "unit01",
    "unit_title": "의사코드",
    "avg_score": 75.5,
    "completion_rate": 80
  }
}
```

#### 5️⃣ 최종 응답 (토큰 단위)
```json
{
  "type": "token",
  "token": "당신의 의사코드 평균 점수는"
}
```

#### 6️⃣ 완료
```
[DONE]
```

---

## 🎯 의도별 응답 특징

| 유형 | 특징 | 데이터 비중 | 조언 비중 |
|------|------|-----------|---------|
| **A. 데이터 조회** | 숫자 + 해석 | 80% | 20% |
| **B. 학습 방법** | 구체적 방법론 | 20% | 80% |
| **C. 동기부여** | 성장 증명 + 격려 | 40% | 60% |
| **D. 범위 밖** | 범위 안내 + 유도 | 0% | 100% |
| **E. 문제 풀이** | 힌트 + 유도 | 10% | 90% |
| **F. 개념 설명** | 개인화 설명 | 30% | 70% |
| **G. 의사결정** | 객관 비교 + 권장 | 50% | 50% |

---

## 💻 프론트엔드 구현 예제 (Vue.js)

### AICoachEnhanced.vue
```vue
<template>
  <div class="ai-coach-enhanced">
    <div class="message-list">
      <!-- 의도 표시 -->
      <div v-if="intendData" class="intent-badge">
        <span class="intent-type">{{ intendData.intent_name }}</span>
        <span class="confidence">(신뢰도: {{ (intendData.confidence * 100).toFixed(0) }}%)</span>
      </div>

      <!-- 사고 과정 -->
      <div v-for="thought in thinkingMessages" :key="thought" class="thinking-bubble">
        <span class="thinking-icon">💭</span> {{ thought }}
      </div>

      <!-- 도구 호출 상황 -->
      <div v-for="step in toolSteps" :key="step.id" class="tool-step">
        <div class="tool-name">🔧 {{ step.label }}</div>
        <div class="tool-result" v-if="step.result">
          {{ formatResult(step.result) }}
        </div>
      </div>

      <!-- 최종 응답 -->
      <div class="response-text">
        {{ responseText }}
      </div>
    </div>

    <!-- 입력창 -->
    <input
      v-model="userMessage"
      @keyup.enter="sendMessage"
      placeholder="질문을 입력하세요..."
    />
  </div>
</template>

<script>
export default {
  data() {
    return {
      userMessage: '',
      intendData: null,
      thinkingMessages: [],
      toolSteps: [],
      responseText: '',
    };
  },
  methods: {
    sendMessage() {
      if (!this.userMessage.trim()) return;

      const eventSource = new EventSource(
        '/api/core/ai-coach/chat-v2/',
        {
          method: 'POST',
          body: JSON.stringify({ message: this.userMessage }),
        }
      );

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'intent_detected') {
          this.intendData = data;
        } else if (data.type === 'thinking') {
          this.thinkingMessages.push(data.message);
        } else if (data.type === 'step_start') {
          this.toolSteps.push({
            id: data.tool,
            label: data.label,
            result: null,
          });
        } else if (data.type === 'step_result') {
          const step = this.toolSteps.find(s => s.id === data.tool);
          if (step) step.result = data.result;
        } else if (data.type === 'token') {
          this.responseText += data.token;
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
      };
    },

    formatResult(result) {
      if (Array.isArray(result)) {
        return result.map(r => `${r.unit_title}: ${r.avg_score}점`).join(', ');
      }
      return JSON.stringify(result, null, 2);
    },
  },
};
</script>

<style scoped>
.intent-badge {
  background: #e3f2fd;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 14px;
}

.intent-type {
  font-weight: bold;
  color: #1976d2;
}

.confidence {
  color: #666;
  margin-left: 8px;
}

.thinking-bubble {
  background: #f5f5f5;
  padding: 8px;
  border-left: 3px solid #ffc107;
  margin: 8px 0;
}

.tool-step {
  background: #fff3e0;
  padding: 8px;
  border-radius: 4px;
  margin: 8px 0;
}

.tool-name {
  font-weight: bold;
  color: #e65100;
}

.response-text {
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
```

---

## 🔍 로컬 테스트 (Python)

### test_coach_enhanced.py
```python
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/core"
AUTH_TOKEN = "your_token_here"

def test_coach_enhanced():
    """AI 코치 고도화 버전 테스트"""

    # 테스트 질문들
    test_cases = [
        ("A", "내 성적이 어떻게 되고 있어?"),
        ("B", "디버깅을 어떻게 공부해야 해?"),
        ("C", "자신감이 없어. 잘할 수 있을까?"),
        ("F", "스택이 뭐야?"),
        ("G", "다음은 뭐 풀어야 해?"),
    ]

    for intent_type, message in test_cases:
        print(f"\n{'='*50}")
        print(f"[{intent_type}] {message}")
        print('='*50)

        headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            f"{BASE_URL}/ai-coach/chat-v2/",
            headers=headers,
            json={"message": message},
            stream=True,
        )

        detected_intent = None
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode().replace("data: ", ""))

                    if data.get("type") == "intent_detected":
                        detected_intent = data.get("intent_name")
                        print(f"✓ Intent: {detected_intent} (신뢰도: {data.get('confidence', 0):.1%})")
                        print(f"  Reasoning: {data.get('reasoning')}")

                    elif data.get("type") == "token":
                        print(data.get("token"), end="", flush=True)

                    elif data.get("type") == "step_result":
                        print(f"\n[도구] {data.get('label')}")

                except json.JSONDecodeError:
                    pass

        print("\n")
        time.sleep(1)

if __name__ == "__main__":
    test_coach_enhanced()
```

---

## 📊 구현 상태

| 컴포넌트 | 상태 | 파일 |
|---------|------|------|
| Intent Analyzer | ✅ 완료 | `coach_view_enhanced.py` |
| Response Strategy | ✅ 완료 | `coach_view_enhanced.py` |
| Tool Calling | ✅ 완료 | `coach_view_enhanced.py` |
| SSE Streaming | ✅ 완료 | `coach_view_enhanced.py` |
| 프론트엔드 | ⏳ 준비중 | - |
| 테스트 | ⏳ 준비중 | - |

---

## 🎓 핵심 학습 포인트

### Intent Analysis의 중요성
```
사용자: "의사코드 어떻게 공부하면서 성적도 높이려면?"

Old (v1): 일반적인 학습 방법 + 성적 데이터 뒤죽박죽
New (v2):
  1. [Intent] B + A 혼합 → B 우선
  2. [Strategy] 학습 방법론 70% + 성적 데이터 30%
  3. [Response] 구체적 방법론 + 근거로 성적 데이터 활용
```

### 도구 활용의 선택성
```
A형 질문: get_user_scores + get_weak_points (필수)
B형 질문: get_weak_points만 필요 (선택)
C형 질문: get_recent_activity (성장 확인용)
D형 질문: 도구 호출 금지
```

### 투명성 향상
```
사용자가 볼 수 있는 사고 과정:
"어, 이건 B형 학습 방법 질문이군요!"
→ 신뢰도 증가
→ 응답 만족도 향상
```

---

## 🔮 향후 확장 계획

### Phase 2: Multi-turn Memory
```python
# 세션별 대화 이력 저장
# 이전 질문과의 연계성 유지
conversation_history = [
    {"turn": 1, "intent": "A", "data": {...}},
    {"turn": 2, "intent": "B", "based_on_turn": 1},
]
```

### Phase 3: Intent Confidence 기반 Follow-up
```
신뢰도 < 0.7이면:
"혹시 다음 중 하나를 물어보시는 건가요?
 - 성적 확인? (A형)
 - 공부 방법? (B형)"
```

### Phase 4: 다중 의도 처리
```
의도가 두 개 이상이면:
"(1) 먼저 성적을 보여드리고, (2) 공부 방법을 제시할게요"
```

---

## 📞 문의 & 피드백

구현 중 발생하는 이슈나 개선 사항은 GitHub Issues에 등록해주세요.

**관련 파일:**
- `backend/core/views/coach_view_enhanced.py`
- `AI_COACH_RESPONSE_STRATEGY.md`
- `backend/core/urls.py`
