# AI Coach 하이브리드 차트 시스템 통합 가이드

## 📋 개요

**SSE (Server-Sent Events) + REST API 하이브리드 방식**
- SSE: 실시간 답변 스트리밍 + 기본 차트 데이터
- REST API: 상세 차트 데이터 (캐싱 가능, 필요시 호출)

---

## 🔄 API 플로우

### 1️⃣ 실시간 코칭 (SSE - POST)

**요청:**
```bash
POST /api/core/ai-coach/chat/
Content-Type: application/json

{
  "message": "내 성적 보여줘"
}
```

**응답 (SSE 스트림):**
```javascript
// Event 1: 분석 중
event: thinking
data: {"type": "thinking", "stage": "intent_analysis", "message": "질문의 의도를 분석하고 있어요..."}

// Event 2: 의도 분류 완료
event: intent_detected
data: {
  "type": "intent_detected",
  "intent_type": "A",
  "intent_name": "데이터 조회형",
  "confidence": 0.95,
  "reasoning": "사용자가 자신의 학습 상태 조회를 요청했습니다."
}

// Event 3: 차트 데이터 (요약) ✨ NEW
event: chart_summary
data: {
  "type": "chart_summary",
  "intent_type": "A",
  "chart": {
    "chart_type": "bar",
    "title": "유닛별 평균 점수",
    "data": {
      "labels": ["의사코드", "디버깅", "아키텍처"],
      "datasets": [{
        "label": "평균 점수",
        "data": [75.5, 82.3, 68.9],
        "backgroundColor": ["#FF6B6B", "#4ECDC4", "#95E1D3"]
      }]
    }
  }
}

// Event 4: 도구 호출
event: step_start
data: {"type": "step_start", "tool": "get_user_scores", "label": "성적 데이터 조회"}

// Event 5: 도구 결과
event: step_result
data: {"type": "step_result", "tool": "get_user_scores", "result": {...}}

// Event 6: 텍스트 응답 (스트리밍)
event: token
data: {"type": "token", "token": "지난주 대비..."}

// Event 7: 완료
event: final
data: [DONE]
```

---

### 2️⃣ 상세 차트 데이터 조회 (REST - GET)

**요청 (선택적, 필요시에만):**
```bash
GET /api/core/ai-coach/chart-details/?intent_type=A&unit_id=unit01
Authorization: Bearer <token>
```

**응답:**
```json
{
  "intent_type": "A",
  "unit_id": "unit01",
  "data": {
    "weak_areas": [
      {
        "metric": "design",
        "avg_score": 65.0,
        "sample_count": 5,
        "feedback_samples": [
          "설계 단계에서 더 체계적인 접근이 필요해",
          "각 단계의 목적을 명확히 하면 좋겠어"
        ]
      }
    ],
    "all_metrics": [
      {"metric": "design", "avg_score": 65.0},
      {"metric": "consistency", "avg_score": 78.5},
      ...
    ]
  }
}
```

---

## 💻 프론트엔드 구현

### Vue.js 예시

#### 1️⃣ Coach Chat Service (기존 + 확장)

**`frontend/src/services/CoachChatService.js`**

```javascript
import axios from 'axios';

export class CoachChatService {
  constructor(apiBaseUrl = '/api/core') {
    this.apiBaseUrl = apiBaseUrl;
  }

  /**
   * SSE 기반 실시간 코칭 (스트리밍)
   */
  async *streamCoachChat(message, token) {
    const response = await fetch(`${this.apiBaseUrl}/ai-coach/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            yield {
              type: data.type,
              payload: data,
            };
          } catch (e) {
            console.warn('Failed to parse SSE data:', line);
          }
        }
      }
    }
  }

  /**
   * 상세 차트 데이터 조회 (캐싱 가능)
   */
  async getChartDetails(intentType, unitId = null, token) {
    const params = new URLSearchParams();
    params.append('intent_type', intentType);
    if (unitId) params.append('unit_id', unitId);

    const response = await axios.get(
      `${this.apiBaseUrl}/ai-coach/chart-details/?${params}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    return response.data;
  }
}

export default new CoachChatService();
```

---

#### 2️⃣ Chart Renderer 컴포넌트

**`frontend/src/components/CoachChartRenderer.vue`**

```vue
<template>
  <div class="chart-container">
    <!-- Bar Chart -->
    <div v-if="chart.chart_type === 'bar'" class="chart-wrapper">
      <h3>{{ chart.title }}</h3>
      <canvas :ref="`chart-${chartId}`"></canvas>
    </div>

    <!-- Line Chart -->
    <div v-else-if="chart.chart_type === 'line'" class="chart-wrapper">
      <h3>{{ chart.title }}</h3>
      <canvas :ref="`chart-${chartId}`"></canvas>
    </div>

    <!-- Radar Chart -->
    <div v-else-if="chart.chart_type === 'radar'" class="chart-wrapper">
      <h3>{{ chart.title }}</h3>
      <canvas :ref="`chart-${chartId}`"></canvas>
    </div>

    <!-- Progress Bars -->
    <div v-else-if="chart.chart_type === 'progress'" class="progress-wrapper">
      <h3>{{ chart.title }}</h3>
      <div v-for="(rate, idx) in chart.data.completion_rates" :key="idx" class="progress-item">
        <span class="label">{{ chart.data.units[idx] }}</span>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${rate}%` }"></div>
        </div>
        <span class="percentage">{{ rate.toFixed(1) }}%</span>
      </div>
    </div>

    <!-- Table -->
    <div v-else-if="chart.chart_type === 'table'" class="table-wrapper">
      <h3>{{ chart.title }}</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="col in chart.data.columns" :key="col">{{ col }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in chart.data.rows" :key="idx">
            <td v-for="(cell, cidx) in row" :key="cidx">{{ cell }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  name: 'CoachChartRenderer',
  props: {
    chart: {
      type: Object,
      required: true,
    },
    chartId: {
      type: String,
      default: () => `chart-${Math.random().toString(36).substr(2, 9)}`,
    },
  },
  data() {
    return {
      chartInstance: null,
    };
  },
  watch: {
    chart: {
      handler() {
        this.$nextTick(() => {
          this.renderChart();
        });
      },
      deep: true,
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.renderChart();
    });
  },
  beforeUnmount() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }
  },
  methods: {
    async renderChart() {
      if (!this.chart || !this.chart.data) return;

      const canvas = this.$refs[`chart-${this.chartId}`];
      if (!canvas) return;

      // 기존 차트 제거
      if (this.chartInstance) {
        this.chartInstance.destroy();
      }

      const ctx = canvas.getContext('2d');
      const config = this.getChartConfig();

      this.chartInstance = new Chart(ctx, config);
    },

    getChartConfig() {
      const { chart_type, data } = this.chart;

      switch (chart_type) {
        case 'bar':
          return {
            type: 'bar',
            data: {
              labels: data.labels,
              datasets: data.datasets,
            },
            options: {
              responsive: true,
              plugins: {
                legend: { display: true },
              },
              scales: {
                y: { max: data.options?.max_value || 100 },
              },
            },
          };

        case 'line':
          return {
            type: 'line',
            data: {
              labels: data.labels,
              datasets: data.datasets,
            },
            options: {
              responsive: true,
              plugins: { legend: { display: true } },
            },
          };

        case 'radar':
          return {
            type: 'radar',
            data: {
              labels: data.labels,
              datasets: data.datasets,
            },
            options: {
              responsive: true,
              scales: { r: { max: 100 } },
            },
          };

        default:
          return null;
      }
    },
  },
};
</script>

<style scoped>
.chart-container {
  margin: 20px 0;
}

.chart-wrapper {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-wrapper h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
}

.progress-wrapper {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.progress-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  gap: 10px;
}

.label {
  min-width: 100px;
  font-weight: 500;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ecdc4, #44b0a3);
  transition: width 0.3s ease;
}

.percentage {
  min-width: 50px;
  text-align: right;
  font-size: 12px;
  color: #666;
}

.table-wrapper {
  background: white;
  border-radius: 8px;
  padding: 20px;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f5f5f5;
  padding: 10px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #e0e0e0;
}

.data-table td {
  padding: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.data-table tbody tr:hover {
  background: #fafafa;
}
</style>
```

---

#### 3️⃣ Coach Chat 페이지 (통합)

**`frontend/src/pages/CoachChatPage.vue`**

```vue
<template>
  <div class="coach-chat-page">
    <div class="chat-area">
      <!-- 챗 메시지 -->
      <div v-for="msg in messages" :key="msg.id" class="message" :class="msg.role">
        <div class="message-content">
          {{ msg.content }}
        </div>
      </div>

      <!-- 차트 영역 ✨ NEW -->
      <div v-for="(chart, idx) in charts" :key="`chart-${idx}`" class="chart-section">
        <CoachChartRenderer :chart="chart" />
      </div>

      <!-- 상세 데이터 버튼 -->
      <div v-if="currentIntentType && showDetailButton" class="detail-button-area">
        <button @click="loadChartDetails" class="detail-btn">
          📊 상세 분석 보기
        </button>
      </div>

      <!-- 상세 데이터 표시 -->
      <div v-if="detailData" class="detail-section">
        <h3>📈 상세 분석</h3>
        <pre>{{ JSON.stringify(detailData, null, 2) }}</pre>
      </div>
    </div>

    <!-- 입력 창 -->
    <div class="input-area">
      <input
        v-model="userMessage"
        @keyup.enter="sendMessage"
        type="text"
        placeholder="질문을 입력해주세요..."
        class="message-input"
      />
      <button @click="sendMessage" class="send-btn">전송</button>
    </div>
  </div>
</template>

<script>
import CoachChartRenderer from '@/components/CoachChartRenderer.vue';
import CoachChatService from '@/services/CoachChatService';

export default {
  name: 'CoachChatPage',
  components: { CoachChartRenderer },
  data() {
    return {
      userMessage: '',
      messages: [],
      charts: [],
      currentIntentType: null,
      detailData: null,
      showDetailButton: false,
      token: null,
    };
  },
  async mounted() {
    this.token = localStorage.getItem('auth_token');
  },
  methods: {
    async sendMessage() {
      if (!this.userMessage.trim()) return;

      // 사용자 메시지 추가
      this.messages.push({
        id: Date.now(),
        role: 'user',
        content: this.userMessage,
      });

      const userMsg = this.userMessage;
      this.userMessage = '';
      this.charts = [];
      this.detailData = null;
      this.showDetailButton = false;

      try {
        // SSE 스트림 처리
        for await (const event of CoachChatService.streamCoachChat(userMsg, this.token)) {
          switch (event.type) {
            case 'thinking':
              this.addAssistantMessage(`💭 ${event.payload.message}`);
              break;

            case 'intent_detected':
              this.currentIntentType = event.payload.intent_type;
              this.addAssistantMessage(
                `✓ 의도 인식: ${event.payload.intent_name} (확률: ${(event.payload.confidence * 100).toFixed(0)}%)`
              );
              break;

            case 'chart_summary':
              // ✨ 차트 데이터 처리
              this.charts.push(event.payload.chart);
              this.showDetailButton = true; // 상세 버튼 표시
              break;

            case 'step_start':
              this.addAssistantMessage(`🔧 ${event.payload.label}...`);
              break;

            case 'step_result':
              this.addAssistantMessage(`✅ ${event.payload.label} 완료`);
              break;

            case 'token':
              // 텍스트 스트리밍
              const lastMsg = this.messages[this.messages.length - 1];
              if (lastMsg && lastMsg.role === 'assistant') {
                lastMsg.content += event.payload.token;
              }
              break;

            case 'final':
              this.addAssistantMessage('✨ 코칭이 완료되었습니다!');
              break;

            case 'error':
              this.addAssistantMessage(`❌ 오류: ${event.payload.message}`);
              break;
          }
        }
      } catch (error) {
        this.addAssistantMessage(`❌ 오류가 발생했습니다: ${error.message}`);
      }
    },

    addAssistantMessage(content) {
      this.messages.push({
        id: Date.now() + Math.random(),
        role: 'assistant',
        content,
      });
    },

    async loadChartDetails() {
      try {
        const details = await CoachChatService.getChartDetails(
          this.currentIntentType,
          null,
          this.token
        );
        this.detailData = details;
      } catch (error) {
        alert('상세 데이터 조회 중 오류가 발생했습니다.');
      }
    },
  },
};
</script>

<style scoped>
.coach-chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 70%;
  word-wrap: break-word;
}

.message.user {
  align-self: flex-end;
  background: #4ecdc4;
  color: white;
}

.message.assistant {
  align-self: flex-start;
  background: white;
  border: 1px solid #e0e0e0;
}

.chart-section {
  align-self: center;
  width: 100%;
  max-width: 600px;
}

.detail-button-area {
  text-align: center;
  margin: 20px 0;
}

.detail-btn {
  padding: 10px 20px;
  background: #4ecdc4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.detail-btn:hover {
  background: #3db8ae;
}

.detail-section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  margin: 20px auto;
  max-width: 600px;
  width: 100%;
}

.input-area {
  display: flex;
  gap: 10px;
  padding: 20px;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.message-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
}

.send-btn {
  padding: 12px 20px;
  background: #4ecdc4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.send-btn:hover {
  background: #3db8ae;
}
</style>
```

---

## 📊 차트 타입별 설정

| 타입 | 사용 케이스 | Chart.js Type |
|------|----------|---------------|
| `bar` | 유닛별 성적 비교 | `bar` |
| `line` | 시간별 성적 추이 | `line` |
| `radar` | 메트릭별 다각형 비교 | `radar` |
| `progress` | 완료율 진행도 | 커스텀 |
| `table` | 상세 통계 데이터 | HTML 테이블 |

---

## 🚀 배포 체크리스트

- [ ] `coach_tools.py`: `generate_chart_data_summary()`, `get_chart_details()` 함수 추가
- [ ] `coach_view.py`: SSE `chart_summary` 이벤트 + `get()` 메서드 추가
- [ ] `urls.py`: `/ai-coach/chart-details/` 엔드포인트 등록
- [ ] 프론트엔드: `CoachChatService.js`, `CoachChartRenderer.vue`, `CoachChatPage.vue` 구현
- [ ] 테스트: 각 Intent별 차트 렌더링 확인

---

## 💡 주요 특징

✅ **하이브리드 아키텍처**
- 빠른 응답: SSE로 요약 차트 즉시 전달
- 확장성: REST API로 상세 데이터 필요시 조회

✅ **캐싱 가능**
- GET 요청이므로 브라우저/CDN 캐싱 가능
- 반복 조회 시 성능 향상

✅ **Intent별 최적화**
- A (데이터): Bar + Progress
- B (학습): Radar (메트릭 비교)
- C (동기): Line (추이)
- G (의사결정): Table

✅ **사용자 경험**
- 텍스트 + 시각화 함께 제시
- 상세 분석은 필요시만 로드
- 모바일 반응형 디자인
