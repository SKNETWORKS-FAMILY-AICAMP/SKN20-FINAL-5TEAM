# AI-ARCADE 에이전트 기반 학습 분석 시스템 구현 계획
> 작성일: 2026-02-22
> 핵심 원칙: LLM 단일 호출이 아닌 멀티 에이전트 자율 협력 시스템
> 목표: 여러 전문 에이전트가 사용자 학습을 분석하고 문제 생성 + 가이드 제시

---

## 0. 에이전트 기반 아키텍처란

```
[기존 구조]
사용자 요청 → LLM 단순 호출 → 응답

[에이전트 구조]
사용자 요청
    ↓
Orchestrator Agent (OpenAI)
"사용자가 뭘 원하나? 어떤 에이전트가 필요한가?"
    ↓
병렬 실행:
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│ Analysis Agent     │ │ Problem Generator  │ │ Learning Guide     │
│ (학습 분석)        │ │ Agent (문제 생성)  │ │ Agent (가이드)     │
│                    │ │                    │ │                    │
│ 실행 흐름:         │ │ 실행 흐름:         │ │ 실행 흐름:         │
│ 1. DB 조회         │ │ 1. 약점 확인       │ │ 1. 약점 받기       │
│ 2. 메트릭 계산     │ │ 2. 문제 검색       │ │ 2. 이정표 조회     │
│ 3. 분석 (OpenAI)   │ │ 3. 생성/추천       │ │ 3. 상세 설명 추가  │
│ 4. 결과 저장       │ │ 4. 결과 저장       │ │ 4. 결과 저장       │
└────────────────────┘ └────────────────────┘ └────────────────────┘
    ↓                       ↓                       ↓
  결과 1                  결과 2                  결과 3
    ↓
Integration Agent (OpenAI)
"세 결과를 통합해서 사용자에게 전달"
    ↓
최종 응답 (분석 + 문제 + 가이드)
```

---

## 1. 에이전트 정의

### 1-1. Orchestrator Agent (오케스트레이터)

**역할**: 사용자 요청 해석 → 필요한 에이전트 결정

**프롬프트**:
```
당신은 AI 엔지니어 학습 시스템의 오케스트레이터입니다.
사용자의 요청을 분석해서 필요한 에이전트를 결정하세요.

사용자 요청: {user_message}
사용자 컨텍스트: {weaknesses: {...}, recent_problems: [...]}

요청 분석:
- "나 약점 뭔지 보여줘" → ["Analysis"]
- "이 약점 해결할 문제 줘" → ["ProblemGenerator"]
- "뭘 공부해야 하나" → ["LearningGuide"]
- "종합 분석해줘" → ["Analysis", "ProblemGenerator", "LearningGuide"]

JSON 응답:
{
  "intent": "사용자가 원하는 것 (1줄)",
  "agents": ["Analysis", "ProblemGenerator", ...],
  "execution_mode": "PARALLEL" 또는 "SEQUENTIAL"
}
```

**실행 방식**:
1. 백엔드에서 이 프롬프트로 OpenAI 호출
2. 응답 파싱 → agents 배열과 execution_mode 추출
3. 선택된 에이전트들을 병렬/순차 실행

---

### 1-2. Analysis Agent (분석 에이전트)

**역할**: `submitted_data` 분석 → 약점 도출 + 근본 원인 분석

**실행 흐름**:
```
1. 백엔드: Django 함수로 사용자 풀이 기록 조회
   → UserSolvedProblem.objects.filter(user=user)

2. 백엔드: submitted_data 파싱 + 메트릭 추출
   → weakness_service.parse_unit1/2/3_metrics()
   → weakness_service.aggregate_metrics()

3. 백엔드: 메트릭 데이터를 OpenAI에 전달

4. OpenAI (분석): 메트릭 분석 + 근본 원인 파악

5. 백엔드: 결과를 UserWeaknessProfile DB에 저장
```

**OpenAI 분석 프롬프트**:
```
당신은 AI 엔지니어 학습 분석가입니다.
아래 사용자의 풀이 메트릭을 분석해서 약점을 파악하세요.

사용자 제출 기록 (최근 5개):
{
  "submissions": [
    {
      "problem_id": "unit0101",
      "score": 75,
      "submitted_data": {
        "metrics": {
          "logic_flow": 80,
          "edge_case": 50,
          "readability": 90
        },
        "analysis": "예외 처리가 부족합니다"
      }
    },
    ...
  ]
}

분석 과제:
1. 각 메트릭의 평균과 추이 분석
2. 반복되는 약점 3~5개 도출 (낮은 점수 순)
3. 각 약점의 근본 원인 (2~3줄)
   - "왜 이 약점이 반복되나"
   - "사용자 풀이 패턴에서 보이는 문제"
4. 약점별 심각도 (HIGH/MEDIUM/LOW)

JSON 응답:
{
  "summary": "전체 분석 요약 (1문장)",
  "analyzed_submission_count": 5,
  "weaknesses": [
    {
      "name": "edge_case",
      "score": 48.0,
      "trend": "down",
      "diagnosis": "null/empty 입력 처리 누락",
      "root_cause": "설계 단계에서 정상 케이스만 고려하는 습관",
      "impact": "HIGH",
      "evidence": ["제출1: null check 없음", "제출3: empty array 미처리"]
    },
    ...
  ]
}
```

---

### 1-3. Problem Generator Agent (문제 생성 에이전트)

**역할**: 약점 기반 새 문제 생성 또는 기존 문제 재추천

**실행 흐름**:
```
1. 백엔드: Analysis 결과 받기
   → 약점: edge_case, 점수: 45

2. 백엔드: 기존 문제 풀에서 약점 관련 문제 검색
   → PracticeDetail.objects.filter(content_data__contains="edge_case")

3. Option A) 기존 문제 재추천
   → 상위 3개 문제 선택

4. Option B) 새 문제 생성
   → OpenAI로 새 문제 생성
   → 품질 평가
   → DRAFT 상태로 DB 저장 (관리자 검토 필요)

5. 결과 반환
```

**문제 검색 프롬프트** (Option A):
```
약점: edge_case (현재 점수: 45/100)
진단: null/empty 입력 처리 미흡

기존 문제 풀:
{
  "problems": [
    {
      "id": "unit0103",
      "title": "예외 처리 집중",
      "keywords": ["null", "edge_case", "defensive"]
    },
    ...
  ]
}

이 약점을 집중 연습할 상위 3개 문제를 추천하세요.
각 문제가 왜 효과적인지 1문장 설명.

JSON 응답:
{
  "method": "RECOMMEND",
  "problems": [
    {
      "problem_id": "unit0103",
      "title": "예외 처리 집중",
      "reason": "null check와 boundary value를 다루는 문제"
    },
    ...
  ]
}
```

**문제 생성 프롬프트** (Option B):
```
약점: edge_case (현재 점수: 45/100)
진단: null/empty 입력 처리 미흡
사용자 레벨: 초급~중급

이 약점을 집중 연습할 새로운 문제를 설계하세요.
단, 설명과 예시만 명시적으로, 풀이는 제시하지 마세요.

JSON 응답:
{
  "method": "GENERATE",
  "problem": {
    "title": "데이터 파이프라인 예외 처리 설계",
    "description": "...",
    "context": "실제 상황 설정",
    "requirements": [
      "null 입력 감지 및 처리",
      "빈 배열 경계값 처리",
      "타입 검증"
    ],
    "difficulty": "INTERMEDIATE",
    "time_estimate_minutes": 30,
    "learning_objectives": [
      "방어적 코딩 이해",
      "경계값 테스트"
    ]
  }
}
```

---

### 1-4. Learning Guide Agent (학습 가이드 에이전트)

**역할**: 약점별 상세 학습 경로 + 개념 확장 설명

**실행 흐름**:
```
1. 백엔드: Analysis 결과 받기
   → 약점: edge_case

2. 백엔드: WEAKNESS_LEARNING_ROADMAP에서 기본 이정표 조회
   → 이정표는 이미 정의됨 (수정 안 함)

3. OpenAI: 사용자의 구체적인 상황을 반영해 이정표 확장
   → "너는 구체적으로..."
   → "실제 풀이에서 보이는 패턴"
   → 학습 자료 추천 강화

4. 결과 반환
```

**학습 가이드 프롬프트**:
```
당신은 AI 엔지니어 초년생 교육 멘토입니다.

약점 분석 결과:
- 약점: edge_case
- 현재 점수: 45/100
- 진단: null/empty 입력을 처리하지 않음
- 근본 원인: 설계 단계에서 정상 케이스만 고려하는 습관

기본 학습 이정표:
{
  "learning_path": [
    {
      "order": 1,
      "concept": "Defensive Programming",
      "duration_minutes": 60,
      "keywords": ["null check", "input validation"],
      "resources": ["wiki URL", "video URL"]
    },
    ...
  ]
}

위 이정표를 바탕으로:

1. 사용자의 구체적인 상황 반영
   - "너는 {근본원인}이 문제라서..."
   - 사용자 풀이 패턴 언급

2. 각 학습 단계별 추가 설명
   - 개념 상세 (실무 사례 포함)
   - 흔한 실수와 해결책
   - 학습 자료 순서 조정

3. 마일스톤 수립
   - 각 단계 완료 기준
   - 검증 방법

JSON 응답:
{
  "personalized_message": "너는 {...}이 문제라서, Defensive Programming부터 시작하는 게 효과적할 거야",
  "expanded_learning_path": [
    {
      "order": 1,
      "concept": "Defensive Programming",
      "duration_minutes": 60,
      "why_important": "실무에서 처리하지 않은 예외는 장애로 이어진다",
      "real_world_case": "우버의 null pointer exception 장애",
      "common_mistake": "모든 입력을 검증하려다 과한 검증",
      "resources": [
        {
          "type": "article",
          "title": "Defensive Programming",
          "url": "https://..."
        },
        {
          "type": "video",
          "title": "Null Safety in Python"
        }
      ]
    },
    ...
  ],
  "milestones": [
    {
      "step": 1,
      "goal": "Defensive Programming 기본 개념 이해",
      "validation_method": "null check, empty array 처리를 직접 작성해보기"
    },
    ...
  ],
  "estimated_total_hours": 2.25,
  "motivation": "이 공부를 마치면 edge_case 점수가 70점 이상 올라갈 거야"
}
```

---

### 1-5. Integration Agent (통합 에이전트)

**역할**: 각 에이전트 결과를 통합 → 사용자 친화적 최종 응답

**실행 흐름**:
```
1. 각 에이전트 결과 수집
   - Analysis: 약점 분석
   - ProblemGenerator: 문제 (추천 또는 생성)
   - LearningGuide: 학습 경로

2. OpenAI: 결과 통합 및 우선순위 정렬

3. 사용자 친화적 포맷으로 변환

4. 격려/동기부여 메시지 추가
```

**통합 프롬프트**:
```
당신은 학습 결과를 종합해서 사용자에게 명확하게 전달하는 커뮤니케이터입니다.

여러 에이전트의 결과:

[Analysis 결과]
{analysis_json}

[Problem Generator 결과]
{problem_json}

[Learning Guide 결과]
{learning_guide_json}

위 결과들을 통합해서:

1. 사용자가 "오, 이렇게 하면 되겠다!"라고 느낄 수 있도록 정리
2. 우선순위 명시 (어떤 걸 먼저 해야 하는가)
3. 실행 가능한 단계별 계획 수립
4. 희망 메시지 추가

JSON 응답:
{
  "overview": "종합 분석 요약 (2~3문장)",
  "top_priority": {
    "weakness": "edge_case",
    "reason": "왜 이것부터 해야 하는가"
  },
  "action_plan": [
    {
      "step": 1,
      "title": "Defensive Programming 학습",
      "description": "...",
      "time_estimate": "60분",
      "resources": [...]
    },
    ...
  ],
  "problems": [
    {
      "problem_id": "unit0103",
      "title": "...",
      "why": "이 문제를 풀어야 하는 이유"
    },
    ...
  ],
  "motivation": "종합 평가 + 격려의 말 (1문장)"
}
```

---

## 2. 필요한 Django 함수/서비스

각 에이전트가 호출할 기존/신규 Django 함수들:

### 2-1. Analysis Agent가 사용할 함수

```python
# backend/core/services/weakness_service.py에서 import

from core.services.weakness_service import (
    get_user_solved_problems,      # UserSolvedProblem 조회
    parse_submitted_data,          # submitted_data 파싱
    aggregate_metrics,             # 메트릭 집계
    save_weakness_profile,         # 분석 결과 저장
)

# 예시 호출
submitted_list = get_user_solved_problems(user_id=user.id, limit=5)
metrics_list = [parse_submitted_data(sp.submitted_data, sp.practice_detail.practice_id)
                for sp in submitted_list]
aggregated = aggregate_metrics(metrics_list)
save_weakness_profile(user, aggregated)
```

### 2-2. Problem Generator Agent가 사용할 함수

```python
# backend/core/services/problem_service.py (신규)

def query_existing_problems(weakness: str, difficulty: str = None, limit: int = 5):
    """약점 관련 기존 문제 검색"""
    # PracticeDetail 쿼리
    # content_data에서 weakness 관련 문제 찾기
    pass

def generate_new_problem(weakness: str, user_level: str, context: dict):
    """새로운 문제 생성 (OpenAI 사용)"""
    # Problem Generator Agent의 프롬프트 실행
    # 새 문제 JSON 반환
    pass

def save_generated_problem(problem_json: dict, status: str = "DRAFT"):
    """생성된 문제 DB 저장"""
    # PracticeDetail 생성 (또는 임시 테이블)
    pass
```

### 2-3. Learning Guide Agent가 사용할 함수

```python
# 기존 파일 이용
from AI_ARCADE_개인맞춤형학습_구현계획 import WEAKNESS_LEARNING_ROADMAP

def get_learning_roadmap(weakness: str):
    """기본 이정표 조회"""
    return WEAKNESS_LEARNING_ROADMAP.get(weakness, {})
```

---

## 3. 에이전트 실행 흐름

### 3-1. API 엔드포인트

**파일**: `backend/core/views/agent_view.py` (신규)

```python
from openai import OpenAI

class UserLearningAnalysisView(APIView):
    """
    POST /api/core/agents/analyze/

    사용자 요청 → Orchestrator → 필요 에이전트 실행 → Integration
    """
    def post(self, request):
        user_profile = request.user.userprofile
        user_message = request.data.get('message', '내 학습 분석해줘')

        # 1. Orchestrator Agent 실행
        orchestrator_result = run_orchestrator_agent(
            user_message=user_message,
            user_weaknesses=get_user_weaknesses(user_profile)
        )
        # 응답: {"intent": "...", "agents": ["Analysis", ...], "execution_mode": "PARALLEL"}

        # 2. 선택된 에이전트 실행
        agent_results = {}

        if "Analysis" in orchestrator_result['agents']:
            agent_results['analysis'] = run_analysis_agent(user_profile)

        if "ProblemGenerator" in orchestrator_result['agents']:
            agent_results['problems'] = run_problem_generator_agent(
                user_profile,
                orchestrator_result.get('focus_weakness')  # Analysis 결과의 약점
            )

        if "LearningGuide" in orchestrator_result['agents']:
            agent_results['guide'] = run_learning_guide_agent(
                user_profile,
                orchestrator_result.get('focus_weakness')
            )

        # 3. Integration Agent (결과 통합)
        final_response = run_integration_agent(
            agent_results=agent_results,
            user_message=user_message
        )

        return Response(final_response)
```

### 3-2. 각 에이전트 실행 함수

**파일**: `backend/core/agents/agent_runner.py` (신규)

```python
from openai import OpenAI

client = OpenAI()

def run_orchestrator_agent(user_message: str, user_weaknesses: dict) -> dict:
    """Orchestrator: 사용자 의도 파악 + 에이전트 선택"""

    prompt = f"""
당신은 오케스트레이터입니다.

사용자 요청: {user_message}
사용자 현재 약점: {user_weaknesses}

JSON 응답:
{{
  "intent": "...",
  "agents": ["Analysis", "ProblemGenerator", "LearningGuide"],
  "execution_mode": "PARALLEL"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    # JSON 파싱
    import json
    return json.loads(response.choices[0].message.content)


def run_analysis_agent(user_profile) -> dict:
    """Analysis Agent: submitted_data 분석"""

    # 1. Django 함수로 데이터 준비
    from core.services.weakness_service import (
        get_user_solved_problems,
        parse_submitted_data,
        aggregate_metrics,
        save_weakness_profile,
    )

    submitted_list = get_user_solved_problems(user_profile.id, limit=5)
    metrics_list = [
        parse_submitted_data(sp.submitted_data, sp.practice_detail.practice_id)
        for sp in submitted_list
    ]

    # 2. OpenAI에 분석 요청
    prompt = f"""
당신은 학습 분석가입니다.

사용자 최근 5개 제출 메트릭:
{json.dumps(metrics_list, indent=2)}

분석해서 약점 도출.
JSON 응답: {{"summary": "...", "weaknesses": [...]}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    analysis_result = json.loads(response.choices[0].message.content)

    # 3. DB 저장
    save_weakness_profile(user_profile, analysis_result)

    return analysis_result


def run_problem_generator_agent(user_profile, weakness: str) -> dict:
    """Problem Generator Agent: 문제 추천 또는 생성"""

    from core.services.problem_service import (
        query_existing_problems,
        generate_new_problem,
        save_generated_problem,
    )

    # 1. 기존 문제 검색 시도
    existing = query_existing_problems(weakness, limit=3)

    if existing:
        # 옵션 A: 기존 문제 재추천
        prompt = f"""
약점 관련 기존 문제들:
{json.dumps([p.to_dict() for p in existing])}

상위 3개를 순서대로 추천.
JSON: {{"method": "RECOMMEND", "problems": [...]}}
"""
    else:
        # 옵션 B: 새 문제 생성
        prompt = f"""
약점: {weakness}
사용자 레벨: 초급~중급

새로운 문제 설계.
JSON: {{"method": "GENERATE", "problem": {{...}}}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    problem_result = json.loads(response.choices[0].message.content)

    # DB 저장 (필요시)
    if problem_result['method'] == 'GENERATE':
        save_generated_problem(problem_result['problem'], status='DRAFT')

    return problem_result


def run_learning_guide_agent(user_profile, weakness: str) -> dict:
    """Learning Guide Agent: 학습 경로 + 자료"""

    from AI_ARCADE_개인맞춤형학습_구현계획 import WEAKNESS_LEARNING_ROADMAP

    # 1. 기본 이정표 조회
    basic_roadmap = WEAKNESS_LEARNING_ROADMAP.get(weakness, {})

    # 2. OpenAI로 확장 + 개인화
    prompt = f"""
기본 학습 이정표:
{json.dumps(basic_roadmap, ensure_ascii=False, indent=2)}

사용자: {user_profile.name}
약점: {weakness}

이 이정표를 확장하고 개인화.
JSON: {{"personalized_message": "...", "expanded_path": [...], "milestones": [...]}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    guide_result = json.loads(response.choices[0].message.content)
    return guide_result


def run_integration_agent(agent_results: dict, user_message: str) -> dict:
    """Integration Agent: 결과 통합 + 최종 응답"""

    prompt = f"""
여러 에이전트의 결과:

분석:
{json.dumps(agent_results.get('analysis'), indent=2)}

문제:
{json.dumps(agent_results.get('problems'), indent=2)}

학습 가이드:
{json.dumps(agent_results.get('guide'), indent=2)}

이들을 통합해서 사용자 친화적 응답 구성.
JSON: {{"overview": "...", "action_plan": [...], "motivation": "..."}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.choices[0].message.content)
```

---

## 4. 구현 아키텍처

### 4-1. 폴더 구조

```
backend/
├── core/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agent_runner.py  (NEW: 모든 에이전트 실행 함수)
│   │
│   ├── services/
│   │   ├── weakness_service.py      (수정: 분석 함수 추가/강화)
│   │   └── problem_service.py       (NEW: 문제 관련 함수)
│   │
│   ├── views/
│   │   └── agent_view.py             (NEW: 에이전트 API)
│   │
│   └── urls.py                       (수정: 에이전트 엔드포인트 추가)
```

### 4-2. 간단한 구조의 장점

```
MCP 방식 (복잡):
OpenAI ← MCP 도구 정의 → Django 함수
↓
도구 선택 → 호출 → 결과 파싱 → 다시 OpenAI로

간단한 방식 (지금):
Django (데이터 준비) → OpenAI (분석/판단) → Django (저장)
↓
명확한 흐름, 디버깅 쉬움, 빠른 개발
```

---

## 5. API 호출 흐름

### 5-1. 사용자 요청 (프론트)

```javascript
// POST /api/core/agents/analyze/
const response = await fetch('/api/core/agents/analyze/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: "내 약점을 분석하고 공부 방법을 알려줘",
    // 또는: message: "edge_case 약점을 해결할 문제를 만들어줘"
    // 또는: message: "보안 공부 로드맵을 만들어줘"
  })
})

const data = await response.json();
console.log(data.overview);    // "종합 분석"
console.log(data.action_plan); // 단계별 계획
```

### 5-2. 백엔드 응답 (최종)

```json
{
  "overview": "지금 edge_case와 root_cause가 주요 약점입니다. edge_case부터 개선하면 실무 장애 예방에 도움이 될 거예요.",

  "top_priority": {
    "weakness": "edge_case",
    "reason": "실무에서 처리하지 않은 예외가 장애로 이어지기 때문"
  },

  "action_plan": [
    {
      "step": 1,
      "title": "Defensive Programming 학습",
      "description": "null check, input validation 등 기본 방어 기법",
      "time_estimate": "60분",
      "resources": [
        {
          "type": "article",
          "title": "Defensive Programming",
          "url": "https://..."
        }
      ]
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
      "title": "예외 처리 집중 문제",
      "why": "null check와 boundary value를 다루는 문제로 edge_case 약점을 직접 연습할 수 있습니다"
    }
  ],

  "motivation": "이 공부를 마치면 edge_case 점수가 70점 이상으로 올라갈 것 같습니다. 화이팅!"
}
```

---

## 6. 실행 패턴

### 6-1. Sequential (순차 실행)

```
Orchestrator 분석 결과: 문제 생성이 필요
    ↓
1단계: Analysis Agent
  - Django: submitted_data 조회 + 파싱
  - OpenAI: 분석 (약점 도출)
  - Django: 결과 저장
  - 결과 반환: {weakness: "edge_case", score: 45, ...}
    ↓
2단계: Problem Generator Agent
  (분석 결과 받아서)
  - Django: 기존 문제 검색
  - OpenAI: 문제 추천/생성
  - Django: 결과 저장 (선택)
  - 결과 반환: {method: "RECOMMEND", problems: [...]}
    ↓
3단계: Integration Agent
  - OpenAI: 모든 결과 통합
  - 최종 응답 반환
```

### 6-2. Parallel (병렬 실행)

```
Orchestrator 분석 결과: 종합 분석 필요

[동시 실행] (각각 독립적으로)
┌─────────────────────────┐
│ 1. Analysis Agent       │
│    - submitted_data     │
│    - OpenAI 분석        │
│    - 결과 반환          │
└─────────────────────────┘

┌─────────────────────────┐
│ 2. Problem Generator    │
│    - 기존 문제 검색     │
│    - OpenAI 추천/생성   │
│    - 결과 반환          │
└─────────────────────────┘

┌─────────────────────────┐
│ 3. Learning Guide       │
│    - 기본 이정표 조회   │
│    - OpenAI 확장/개인화 │
│    - 결과 반환          │
└─────────────────────────┘
    ↓ (모두 완료 대기)
Integration Agent (결과 통합)
```

---

## 7. 구현 우선순위

### Phase 1: Orchestrator + Analysis Agent (Day 1~2)

```
□ weakness_service.py 함수들 강화
  └─ get_user_solved_problems()
  └─ parse_submitted_data()
  └─ aggregate_metrics()
  └─ save_weakness_profile()

□ agent_runner.py 생성
  └─ run_orchestrator_agent()
  └─ run_analysis_agent()

□ agent_view.py 생성
  └─ UserLearningAnalysisView (POST /api/core/agents/analyze/)

□ urls.py 수정
  └─ 에이전트 엔드포인트 등록

□ 테스트
  └─ Orchestrator: "내 약점 보여줘" → 에이전트 선택 확인
  └─ Analysis: submitted_data 파싱 → 분석 결과 확인
```

### Phase 2: Problem Generator + Learning Guide (Day 3~4)

```
□ problem_service.py 생성
  └─ query_existing_problems()
  └─ generate_new_problem()
  └─ save_generated_problem()

□ agent_runner.py 확장
  └─ run_problem_generator_agent()
  └─ run_learning_guide_agent()

□ 기본 이정표 데이터
  └─ WEAKNESS_LEARNING_ROADMAP import

□ 테스트
  └─ "edge_case 해결 문제 줘" → 문제 추천/생성
  └─ "뭘 공부해야 하나" → 학습 경로
```

### Phase 3: Integration Agent + UI (Day 5~6)

```
□ agent_runner.py 최종 함수
  └─ run_integration_agent()

□ UserLearningAnalysisView 완성
  └─ 병렬/순차 실행 처리
  └─ 결과 통합

□ 프론트엔드 UI
  └─ AgentAnalysisService.js
  └─ AgentAnalysisPanel.vue
  └─ 로딩 상태 표시

□ 통합 테스트
  └─ "종합 분석해줘" → 모든 에이전트 실행 → 결과 통합 확인
```

---

## 8. 주요 특징

### 8-1. MCP 없이도 에이전트의 이점을 살림

| 특징 | 설명 |
|------|------|
| **명확한 흐름** | Django 함수 → OpenAI → Django 저장 (이해하기 쉬움) |
| **빠른 개발** | MCP 정의 없으므로 1주일 내 완성 가능 |
| **디버깅 용이** | 각 에이전트의 입출력이 명확 |
| **확장 가능** | 새 에이전트 추가 시 함수만 준비하면 됨 |
| **비용 효율** | 불필요한 LLM 호출 없음 (OpenAI는 필요한 곳에만) |

### 8-2. 에이전트의 역할 분리

```
Orchestrator → 사용자 의도 파악 (1번의 OpenAI 호출)
Analysis → 데이터 분석 (1번의 OpenAI 호출)
ProblemGenerator → 문제 추천/생성 (1번의 OpenAI 호출)
LearningGuide → 경로 개인화 (1번의 OpenAI 호출)
Integration → 결과 통합 (1번의 OpenAI 호출)

총 5번의 OpenAI 호출로 완전한 학습 분석 완성
```

---

## 9. 기술 스택

```
백엔드:
- Framework: Django REST Framework
- LLM: OpenAI GPT-4o-mini
- 데이터: PostgreSQL (existing)
- 언어: Python

프론트엔드:
- Framework: Vue 3
- 통신: HTTP (비동기 요청)
  또는 Websocket (진행도 실시간 표시, 선택)
```

---

## 10. 간단한 구현 흐름도

```
프론트: POST /api/core/agents/analyze/
  ↓
백엔드: UserLearningAnalysisView
  ├─ 1단계: Orchestrator 실행
  │        └─ OpenAI: 사용자 의도 파악
  │        └─ 필요 에이전트 결정
  │
  ├─ 2단계: 병렬 실행 (필요에 따라)
  │        ├─ Analysis: Django (조회) → OpenAI (분석) → Django (저장)
  │        ├─ ProblemGenerator: Django (검색) → OpenAI (추천/생성) → Django (저장)
  │        └─ LearningGuide: Django (조회) → OpenAI (개인화) → Django (저장)
  │
  └─ 3단계: Integration 실행
           └─ OpenAI: 결과 통합
           └─ JSON 응답
  ↓
프론트: 결과 표시
```

---

## 11. 구현 시 주의사항

### JSON 파싱
```python
# OpenAI 응답은 항상 JSON으로 받기
response = client.chat.completions.create(...)
result = json.loads(response.choices[0].message.content)  # 파싱 필수
```

### 에러 처리
```python
try:
    result = json.loads(response.choices[0].message.content)
except json.JSONDecodeError:
    # OpenAI가 JSON이 아닌 텍스트 반환한 경우
    # 재시도 또는 폴백
    pass
```

### 토큰 관리
```
- Orchestrator: ~300 토큰 (짧음)
- Analysis: ~1500 토큰 (submitted_data 포함)
- ProblemGenerator: ~1000 토큰
- LearningGuide: ~1200 토큰
- Integration: ~800 토큰

총: ~5000 토큰 (약 $0.02 비용)
```

---

## 12. 다음 단계

1. **Phase 1** (Day 1~2)
   - Orchestrator + Analysis 구현
   - 기본 동작 확인

2. **Phase 2** (Day 3~4)
   - ProblemGenerator + LearningGuide
   - 에이전트 간 데이터 전달 확인

3. **Phase 3** (Day 5~6)
   - Integration + 프론트엔드 UI
   - 통합 테스트

---

*작성일: 2026-02-22*
*상태: MCP 없는 간단한 에이전트 기반 설계 완료*
*핵심 원칙: "Django + OpenAI" 조합으로 간단하고 효율적으로*
