# 학습분석 에이전트 동작 방식 분석

## 📊 시스템 분류

**프로젝트의 학습분석 에이전트는 "LLM 기반 에이전트 오케스트레이션" 또는 "프롬프트 기반 멀티-에이전트 시스템"입니다.**

### 에이전트 vs LLM 체인 비교

| 특성 | 에이전트 | LLM 체인 | 학습분석 시스템 |
|------|---------|---------|----------------|
| **제어 흐름** | 동적 (의도 기반) | 고정 (순차 구조) | 동적 + 규칙 기반 혼합 |
| **메모리** | 유지 (컨텍스트 누적) | 없음 | 없음 (단일 요청) |
| **에이전트 선택** | LLM이 자율 결정 | 미리 정의된 순서 | Orchestrator가 결정 |
| **피드백 루프** | 있음 (재계획) | 없음 | 없음 (일회성) |
| **복잡도** | 높음 (동적 계획) | 낮음 (정해진 단계) | 중간 (의도 기반 선택) |

---

## 🏗️ 현재 아키텍처

### 5가지 에이전트 구성

```
사용자 요청
    ↓
┌─────────────────────────────────────────────┐
│ Data Analyzer Agent (항상 실행)              │
│ - submitted_data 직접 분석                   │
│ - 약점/강점 도출                              │
│ - OpenAI gpt-4o-mini 호출                   │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ Orchestrator Agent                          │
│ - 사용자 의도 분석                           │
│ - 필요 에이전트 결정                         │
│ - 실행 모드 선택 (PARALLEL/SEQUENTIAL)      │
└──────────────┬──────────────────────────────┘
               ↓
    ┌─────────────────────────────┐
    │ 필요 에이전트 병렬 실행      │
    │ (Orchestrator 결과 기반)    │
    │                            │
    ├─ Problem Generator         │
    │  └ 문제 추천               │
    │                            │
    └─ Learning Guide            │
       └ 학습 경로 생성           │

               ↓
┌─────────────────────────────────────────────┐
│ Integration Agent                           │
│ - 모든 에이전트 결과 통합                    │
│ - 최종 응답 생성                            │
│ - OpenAI gpt-4o-mini 호출                   │
└──────────────┬──────────────────────────────┘
               ↓
          최종 응답
        (overview, action_plan, motivation)
```

---

## 🔄 단계별 실행 흐름

### Step 1: Data Analyzer Agent 실행

**목적**: submitted_data 직접 분석 → 자연스러운 약점 표현

**입력**:
- 사용자의 최근 풀이 기록 (최대 10개)
- 각 풀이의 제출 데이터 (코드, 설계, 답안)
- 점수 정보

**프롬프트 구조**:
```python
# 파일: backend/core/agents/agent_runner.py (196-307줄)

prompt = f"""
당신은 AI 엔지니어의 학습을 깊이 있게 분석하는 전문가입니다.

사용자의 최근 풀이 기록을 분석해서:
1. 실제로 부족한 부분이 무엇인지
2. 강점이 무엇인지
자연스러운 표현으로 파악하세요.

데이터 형식: {풀이 데이터 JSON}

분석 시 고려사항:
- 제출된 코드/설계의 질
- 점수 추이
- 반복되는 패턴 (부족한 부분)
- 잘하는 부분
"""
```

**출력**:
```json
{
  "analysis_summary": "전체 분석 요약",
  "weaknesses": [
    {
      "description": "구체적으로 부족한 부분",
      "severity": "HIGH/MEDIUM/LOW",
      "affected_areas": ["Unit1", "Unit2"],
      "recommendation": "학습/개선 방법"
    }
  ],
  "strengths": [
    {
      "description": "잘하는 부분",
      "evidence": "근거"
    }
  ]
}
```

---

### Step 2: Orchestrator Agent 실행

**목적**: Data Analyzer 결과 + 사용자 의도 분석 → 필요 에이전트 결정

**입력**:
- 사용자 요청 메시지
- Data Analyzer 결과 (약점/강점)
- 사용자 컨텍스트 (과거 약점 기록, 풀이 수)

**의도 판단 규칙**:
```python
# 파일: backend/core/agents/agent_runner.py (50-71줄)

"나 약점 뭔지 보여줘", "분석해줘"
  → ["Analysis"]

"이 약점 해결할 문제 줘", "문제 만들어줘"
  → ["Analysis", "ProblemGenerator"]

"뭘 공부해야 하나", "학습 경로"
  → ["Analysis", "LearningGuide"]

"종합 분석해줘", "전체적으로"
  → ["Analysis", "ProblemGenerator", "LearningGuide"]
```

**출력**:
```json
{
  "intent": "사용자의 의도",
  "agents": ["Analysis", "ProblemGenerator"],
  "execution_mode": "PARALLEL"
}
```

---

### Step 3: 필요 에이전트 병렬 실행

#### 3-1. Problem Generator Agent

**목적**: 약점별 문제 추천

**입력**:
- 분석된 약점 설명
- 사용자 프로필

**의미 기반 매칭** (`_match_weakness_to_category` 함수):
```python
# 약점 설명 → 카테고리 자동 매칭

"null/empty 입력" → "edge_case"
"원인 분석" → "root_cause"
"보안 고려" → "security"
"논리 설계" → "logic_design"
"성능 최적화" → "performance"
"코드 가독성" → "readability"
```

**출력**:
```json
{
  "method": "RECOMMEND",
  "problems": [
    {
      "problem_id": "unit0103",
      "title": "데이터 파이프라인 예외 처리 설계",
      "reason": "null/empty 입력 처리를 집중 연습할 수 있습니다"
    }
  ],
  "matched_category": "edge_case"
}
```

#### 3-2. Learning Guide Agent

**목적**: 약점별 학습 경로 생성

**입력**:
- 분석된 약점 설명
- 사용자 프로필

**출력**:
```json
{
  "personalized_message": "null/empty 입력 처리를...",
  "learning_path": [
    {
      "order": 1,
      "concept": "Defensive Programming",
      "duration_minutes": 60,
      "why_important": "실무에서 처리하지 않은 예외는...",
      "resources": [
        {
          "type": "article",
          "title": "Defensive Programming Wikipedia",
          "url": "..."
        }
      ]
    }
  ],
  "estimated_total_hours": 1.5,
  "matched_category": "edge_case"
}
```

---

### Step 4: Integration Agent 실행

**목적**: 모든 에이전트 결과 통합 → 최종 응답 생성

**입력**:
- Data Analyzer 결과
- Problem Generator 결과
- Learning Guide 결과
- 사용자 원본 메시지
- Orchestrator가 파악한 의도

**프롬프트**:
```python
당신은 학습 결과를 종합해서 사용자에게 명확하게 전달하는 커뮤니케이터입니다.
사용자의 실제 의도를 반영하여 실용적인 조언을 제공하세요.

분석 결과: {...}
추천 문제: {...}
학습 가이드: {...}
사용자 요청: {user_message}
```

**최종 출력**:
```json
{
  "overview": "종합 분석 요약",
  "action_plan": [
    {
      "step": 1,
      "title": "학습할 개념",
      "description": "설명",
      "time_estimate": "60분"
    }
  ],
  "problems": [
    {
      "problem_id": "unit0103",
      "title": "문제 제목",
      "reason": "왜 이 문제를 풀어야 하는가"
    }
  ],
  "motivation": "격려 메시지"
}
```

---

## 🔌 API 엔드포인트

### POST `/api/core/agents/analyze/`

**요청**:
```json
{
  "message": "내 약점을 분석하고 공부 방법을 알려줘",
  "context": {
    "top_weaknesses": ["edge_case", "root_cause"],
    "analyzed_submission_count": 5,
    "unit_metrics": {
      "unit1": {"edge_case": 45, "logic_design": 75},
      "unit2": {"root_cause": 50},
      "unit3": {}
    }
  }
}
```

**응답**: Integration Agent의 최종 결과

### GET `/api/core/agents/weakness-profile/`

**응답**: 사용자의 약점 프로필
```json
{
  "unit1_metrics": {...},
  "unit2_metrics": {...},
  "unit3_metrics": {...},
  "top_weaknesses": ["edge_case", "root_cause"],
  "analyzed_submission_count": 5
}
```

---

## 🎯 핵심 특징

### ✅ 에이전트 특징 (있는 것)

1. **의도 기반 제어**
   - Orchestrator가 사용자 의도 분석 → 필요 에이전트 결정
   - 고정된 흐름이 아니라 동적 선택

2. **독립적 에이전트**
   - 각 에이전트는 독립적인 OpenAI API 호출
   - 자신의 역할에만 집중 (단일 책임 원칙)

3. **다단계 추론**
   - Data Analyzer → Orchestrator → {ProblemGenerator, LearningGuide} → Integration
   - 각 단계에서 LLM 호출로 깊이 있는 분석

### ❌ 에이전트 특징 (없는 것)

1. **메모리 없음**
   - 각 요청마다 새로 실행
   - 이전 분석 이력 미반영

2. **피드백 루프 없음**
   - 재계획이나 재시도 로직 없음
   - 일회성 분석

3. **도구 사용 없음**
   - 외부 API나 도구 호출 불가
   - LLM 호출만 가능

4. **에이전트 간 협업 미흡**
   - 에이전트들이 서로 통신하지 않음
   - Integration Agent가 일방적으로 결과 종합

---

## 📚 Code 구조

### 파일 맵핑

| 파일 | 역할 |
|-----|------|
| `backend/core/agents/agent_runner.py` | 5가지 에이전트 함수 구현 |
| `backend/core/views/agent_view.py` | API 엔드포인트 + 실행 오케스트레이션 |
| `backend/core/urls.py` | 라우팅 등록 |
| `backend/core/services/weakness_service.py` | 데이터 전처리 (분석 기초 제공) |

### agent_view.py의 실행 흐름

```python
# POST /api/core/agents/analyze/

1. UserProfile 조회 (request.user.email 기반)
2. 사용자 메시지 + 컨텍스트 받기
3. run_data_analyzer_agent() 실행
   ├─ UserSolvedProblem 조회 (최근 10개)
   ├─ OpenAI API 호출
   └─ 약점/강점 반환
4. run_orchestrator_agent() 실행
   ├─ Data Analyzer 결과 + 사용자 메시지 분석
   ├─ OpenAI API 호출
   └─ 필요 에이전트 결정
5. 조건부 에이전트 실행
   ├─ if "ProblemGenerator" in agents → run_problem_generator_agent()
   └─ if "LearningGuide" in agents → run_learning_guide_agent()
6. run_integration_agent() 실행
   ├─ 모든 결과 수집
   ├─ OpenAI API 호출
   └─ 최종 응답 생성
7. Response 반환
```

---

## 🤔 분류 최종 결론

### 이 시스템은 **"프롬프트 기반 멀티-에이전트 오케스트레이션"**

**근거**:
1. ✅ 각 함수가 "에이전트"처럼 독립적으로 동작
2. ✅ 의도 기반 라우팅 (Orchestrator 역할)
3. ✅ 다단계 추론 (Data → Orchestrator → {Generators} → Integration)
4. ❌ 하지만 메모리/피드백 루프 없음
5. ❌ 도구 사용 불가 (순수 LLM 호출만)

**더 정확한 분류**:
- **초기 버전**: LLM 체인 (순차 프롬프트 호출)
- **현재 버전**: 의도 기반 에이전트 라우팅 + 병렬 처리
- **발전 방향**: 메모리 추가 → 진정한 에이전트 시스템

---

## 💡 개선 가능 방향

### 현재의 한계

1. **메모리 부재**
   - 해결: 분석 이력 DB 저장 → 다음 요청에 참고

2. **고정된 문제/경로**
   - 해결: 카테고리별 문제 DB 확장 → 동적 생성

3. **피드백 루프 없음**
   - 해결: 사용자 만족도 → 다음 분석에 반영

4. **에이전트 간 협업 미흡**
   - 해결: 에이전트가 중간 결과 쿼리 가능하게 구현

### 추천 다음 단계

```
1단계 (현재): 프롬프트 기반 다중 에이전트
2단계: 분석 이력 메모리 추가 (DB 저장)
3단계: 에이전트 간 도구 사용 추가 (API 호출, 검색 등)
4단계: ReAct 패턴 도입 (자율적 재계획)
5단계: 다중 턴 대화 지원 (Agentic Loop)
```

---

## 📝 요약

| 항목 | 답변 |
|------|------|
| **에이전트인가?** | 부분적. 의도 기반 라우팅은 있지만 메모리/피드백 루프는 없음 |
| **LLM 체인인가?** | 아니다. 고정된 순차 구조가 아니라 동적 선택 |
| **정확한 분류** | "의도 기반 멀티-에이전트 오케스트레이션 시스템" |
| **에이전트 개수** | 5개 (Data Analyzer, Orchestrator, Problem Generator, Learning Guide, Integration) |
| **LLM 모델** | OpenAI gpt-4o-mini |
| **실행 방식** | Data Analyzer (순차) → Orchestrator (순차) → {ProblemGenerator, LearningGuide} (병렬) → Integration (순차) |
