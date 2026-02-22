# 에이전트 기반 학습 분석 시스템 - 데모 가이드

**작성일**: 2026-02-22
**상태**: Phase 1 (Orchestrator + Analysis Agent) 완성
**모델**: GPT-4o-mini (OpenAI)

---

## 🚀 빠른 시작

### 1. 백엔드 서버 실행

```bash
cd /c/Users/playdata2/Desktop/FINAL/backend
python manage.py runserver 0.0.0.0:8000
```

### 2. API 테스트

#### A. 사용자 약점 프로필 조회
```bash
curl -X GET http://localhost:8000/api/core/agents/weakness-profile/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**응답 예시**:
```json
{
  "user_id": 123,
  "summary": "Unit 1: 5회, Unit 2: 3회, Unit 3: 2회 풀이 기록 분석",
  "unit1_metrics": {
    "logic_flow": 72.0,
    "edge_case": 45.0,
    "readability": 88.0
  },
  "unit2_metrics": {
    "bug_detection": 68.0,
    "root_cause": 50.0,
    "fix_quality": 75.0
  },
  "unit3_metrics": {
    "scalability": 55.0,
    "reliability": 70.0,
    "security": 40.0,
    "performance": 65.0,
    "maintainability": 80.0,
    "cost_efficiency": 60.0
  },
  "top_weaknesses": ["edge_case", "root_cause", "security"],
  "analyzed_submission_count": 10
}
```

#### B. 종합 학습 분석 요청
```bash
curl -X POST http://localhost:8000/api/core/agents/analyze/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "내 약점을 분석하고 공부 방법을 알려줘"
  }'
```

**응답 예시**:
```json
{
  "overview": "현재 edge_case와 root_cause가 주요 약점입니다. 실무 영향도가 높아 먼저 개선하는 것을 추천합니다.",
  "action_plan": [
    {
      "step": 1,
      "title": "Defensive Programming 학습",
      "description": "null check, input validation 등 기본 방어 기법",
      "time_estimate": "60분"
    },
    {
      "step": 2,
      "title": "경계값 분석 연습",
      "description": "min, max, empty, null 케이스 직접 작성",
      "time_estimate": "30분"
    }
  ],
  "problems": [
    {
      "problem_id": "unit0103",
      "title": "데이터 파이프라인 예외 처리 설계",
      "reason": "null/empty 입력 처리를 집중 연습할 수 있습니다"
    },
    {
      "problem_id": "unit0105",
      "title": "경계값 검증 설계",
      "reason": "min, max, boundary value 처리를 다룹니다"
    }
  ],
  "motivation": "이 공부를 마치면 edge_case 점수가 70점 이상으로 올라갈 것 같습니다. 화이팅!"
}
```

---

## 🏗️ 구현된 파일 구조

```
backend/core/
├── agents/
│   ├── __init__.py
│   └── agent_runner.py          ← 모든 에이전트 실행 함수
│       ├── run_orchestrator_agent()      # 사용자 의도 파악 + 에이전트 선택
│       ├── run_analysis_agent()          # 학습 분석 + 약점 도출
│       ├── run_problem_generator_agent() # 문제 추천 (데모용)
│       ├── run_learning_guide_agent()    # 학습 경로 (데모용)
│       └── run_integration_agent()       # 결과 통합
│
├── services/
│   └── weakness_service.py      ← 약점 분석 서비스 (신규)
│       ├── get_user_solved_problems()    # 풀이 기록 조회
│       ├── parse_submitted_data()        # 메트릭 파싱
│       ├── aggregate_metrics()           # 메트릭 집계
│       ├── compute_top_weaknesses()      # 약점 도출
│       └── analyze_user_learning()       # 종합 분석
│
├── views/
│   └── agent_view.py            ← API 엔드포인트 (신규)
│       ├── UserLearningAnalysisView      # POST /agents/analyze/
│       └── WeaknessProfileView           # GET /agents/weakness-profile/
│
└── urls.py                      ← 수정됨 (엔드포인트 2개 추가)
```

---

## 📊 API 흐름도

```
POST /api/core/agents/analyze/
  ↓
UserLearningAnalysisView.post()
  ├─ Step 1: 사용자 약점 정보 조회 (analyze_user_learning)
  │
  ├─ Step 2: Orchestrator Agent 실행
  │   └─ 사용자 의도 파악 → 필요 에이전트 결정
  │
  ├─ Step 3: 필요 에이전트 병렬 실행
  │   ├─ Analysis Agent (항상 실행)
  │   │   └─ submitted_data 분석 → 약점 도출
  │   ├─ Problem Generator Agent (선택)
  │   │   └─ 약점 기반 문제 추천
  │   └─ Learning Guide Agent (선택)
  │       └─ 약점 기반 학습 경로
  │
  └─ Step 4: Integration Agent
      └─ 모든 결과 통합 → 최종 응답

Response 200 OK:
{
  "overview": "...",
  "action_plan": [...],
  "problems": [...],
  "motivation": "..."
}
```

---

## 🔧 테스트하는 법

### Python 스크립트로 테스트

```python
import requests
import json

# 설정
BASE_URL = "http://localhost:8000/api/core"
USER_TOKEN = "YOUR_JWT_TOKEN"
HEADERS = {
    "Authorization": f"Bearer {USER_TOKEN}",
    "Content-Type": "application/json"
}

# 1. 약점 프로필 조회
print("=" * 50)
print("1. 약점 프로필 조회")
print("=" * 50)
response = requests.get(
    f"{BASE_URL}/agents/weakness-profile/",
    headers=HEADERS
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# 2. 종합 분석 요청 - 분석만
print("\n" + "=" * 50)
print("2. 종합 분석 요청 (메시지: '내 약점을 분석해줘')")
print("=" * 50)
response = requests.post(
    f"{BASE_URL}/agents/analyze/",
    headers=HEADERS,
    json={"message": "내 약점을 분석해줘"}
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# 3. 종합 분석 요청 - 분석 + 가이드
print("\n" + "=" * 50)
print("3. 학습 가이드 요청 (메시지: '뭘 공부해야 하나')")
print("=" * 50)
response = requests.post(
    f"{BASE_URL}/agents/analyze/",
    headers=HEADERS,
    json={"message": "뭘 공부해야 하나"}
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# 4. 모든 기능 요청
print("\n" + "=" * 50)
print("4. 종합 분석 (분석 + 문제 + 가이드)")
print("=" * 50)
response = requests.post(
    f"{BASE_URL}/agents/analyze/",
    headers=HEADERS,
    json={"message": "종합 분석해줘"}
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

---

## 📝 로그 확인

백엔드 로그에서 에이전트 실행 과정을 확인할 수 있습니다:

```
[에이전트] 사용자 ID 123 - 요청: 내 약점을 분석해줘
[Orchestrator] 선택 에이전트: ['Analysis']
[Analysis Agent] 실행 중...
[Analysis Agent] 완료 - 약점: 3개
[Integration Agent] 실행 중...
[Integration Agent] 완료
```

---

## ⚙️ 환경 설정

### 1. OpenAI API Key 설정

`.env` 파일에 다음을 추가:

```
OPENAI_API_KEY=sk-proj-...
```

또는 Django settings.py에 설정:

```python
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
```

### 2. Python 의존성

```
openai>=1.0.0
django>=4.2
djangorestframework>=3.14
```

---

## 🎯 Phase 1 구현 완료 항목

- ✅ weakness_service.py
  - ✅ submitted_data 파싱 (Unit 1/2/3)
  - ✅ 메트릭 집계 (가중 평균)
  - ✅ 약점 도출

- ✅ agent_runner.py
  - ✅ Orchestrator Agent (OpenAI 호출)
  - ✅ Analysis Agent (OpenAI 호출)
  - ✅ Problem Generator Agent (데모)
  - ✅ Learning Guide Agent (데모)
  - ✅ Integration Agent (OpenAI 호출)

- ✅ agent_view.py
  - ✅ UserLearningAnalysisView (POST /agents/analyze/)
  - ✅ WeaknessProfileView (GET /agents/weakness-profile/)

- ✅ urls.py
  - ✅ 2개 엔드포인트 등록

---

## 📅 다음 단계 (Phase 2)

- [ ] Problem Generator Agent 실제 구현
  - [ ] 기존 문제 DB 검색
  - [ ] 새 문제 생성 (Claude 활용)

- [ ] Learning Guide Agent 실제 구현
  - [ ] 기본 이정표 DB 구축
  - [ ] Claude로 개인화 확장

- [ ] 프론트엔드 UI
  - [ ] 결과 표시 컴포넌트
  - [ ] 로딩 상태 표시

---

## 🐛 문제 해결

### 401 Unauthorized
→ JWT 토큰 확인 (로그인 필수)

### 500 Internal Server Error
→ 백엔드 로그 확인: `tail -f logs/debug.log`

### OpenAI API 오류
→ OPENAI_API_KEY 확인 및 할당량 체크

---

*데모 구현 완료: 2026-02-22*
