# 모의면접 엔진 구현 지시서

너는 시니어 Python 백엔드 + Vue.js 프론트엔드 엔지니어다.
아래 명세를 정확히 따르는 모의면접 시스템을 구현한다.

아키텍처를 단순화하지 마라.
모듈을 합치지 마라.
역할 분리를 반드시 유지하라.

---

## 핵심 설계 원칙 (절대 깨지면 안 됨)

### 원칙 1: 결정권은 엔진에만 있다

LLM은 판단하지 않는다.
LLM은 오직 **정보 존재 여부만 태깅**한다.
평가 결과는 **규칙으로만** 나온다.

| 역할 | 담당 |
|------|------|
| 의미 해석 | LLM (Analyst) |
| 상태 판정 | Engine |
| 진행 전략 | Planner |
| 말투 | Humanizer |

> **LLM이 "좋다/나쁘다"를 말하는 순간 이 서비스는 신뢰도를 잃는다.**

### 원칙 2: 평가 단위는 개념이 아니라 증거다

- "협업 능력 있음" 같은 추상적 판단 금지
- 대신: **특정 구조의 발화가 존재했는가?** 를 본다

### 원칙 3: 대화는 자연스럽게, 평가는 기계적으로

- 내부는 상태머신
- 외부는 면접관

---

## 필수 규칙

### 기술 스택 원칙

오래된 라이브러리를 사용하지 마라.
**검증된 최신 버전**을 사용한다.
구현 전에 사용할 라이브러리의 최신 안정 버전을 확인하고 적용하라.
deprecated된 함수나 패턴을 사용하지 마라.
공식 문서 기준으로 현재 권장되는 방식만 사용하라.

### 기술 선택 가이드

아래 영역별로 선택 가능한 기술과 각각의 역할/특징을 정리한다.
구현 시 이 중에서 프로젝트에 적합한 기술을 선택하여 사용하라.
선택 근거를 코드 주석이나 README에 간단히 남겨라.

#### LLM API

| 선택지 | 역할 | 특징 |
|--------|------|------|
| **OpenAI GPT-4o** | 범용 LLM (Analyst, Interviewer, Coach) | 빠르고 비용 효율적. 한국어 성능 우수. 기존 프로젝트에서 사용 중 |
| **OpenAI GPT-4o-mini** | 경량 LLM (단순 판단 작업) | 더 빠르고 저렴. 단순 JSON 분류(Analyst의 evidence 태깅 등)에 적합 |
| **OpenAI o1 / o3** | 추론형 LLM (복잡한 분석) | 깊은 추론 필요시. 느리지만 정확 |
| **Anthropic Claude 3.5 Sonnet** | 대안 LLM | 한국어 품질 우수. OpenAI 장애 시 fallback 가능 |

- 역할별로 다른 모델을 사용할 수 있다 (예: Analyst는 GPT-4o-mini, Humanizer는 GPT-4o)
- `openai >= 1.0` 신규 SDK 문법을 사용하라 (구버전 `openai.ChatCompletion` 금지)

#### 프론트엔드 프레임워크

| 선택지 | 역할 | 특징 |
|--------|------|------|
| **Vue 3 Composition API + `<script setup>`** | 컴포넌트 작성 | 기존 프로젝트 표준. 타입 추론 우수, 코드 간결 |
| **Pinia** | 상태 관리 | Vue 3 공식 상태관리. 기존 프로젝트에서 사용 중 |
| **Vuex** | 상태 관리 (레거시) | Vue 3에서 deprecated 방향. 사용 금지 |
| **Options API** | 컴포넌트 작성 (레거시) | Vue 2 스타일. 사용 금지 |

#### SSE 클라이언트 (프론트에서 스트리밍 수신)

| 선택지 | 역할 | 특징 |
|--------|------|------|
| **fetch + ReadableStream** | SSE 수신 | 브라우저 내장 API. 별도 라이브러리 불필요. POST 요청 지원 |
| **EventSource (브라우저 내장)** | SSE 수신 | 간단하지만 GET만 지원. POST 답변 제출에는 부적합 |
| **@microsoft/fetch-event-source** | SSE 수신 | POST 지원 + 자동 재연결. fetch 기반 SSE 라이브러리 |

- 면접 답변 제출은 POST 요청이므로 EventSource(GET 전용)는 부적합

#### 백엔드 스트리밍

| 선택지 | 역할 | 특징 |
|--------|------|------|
| **Django StreamingHttpResponse** | SSE 서버 | 기존 BugHuntInterviewView에서 검증됨. 추가 설치 불필요 |
| **Django Channels (WebSocket)** | 양방향 통신 | 실시간 양방향 필요시. 현재 면접에서는 단방향이면 충분 |
| **ASGI + Starlette** | 비동기 스트리밍 | 성능 우수하지만 기존 WSGI 프로젝트와 구조가 다름 |

#### 음성 인식 (Phase 2)

| 선택지 | 역할 | 특징 |
|--------|------|------|
| **silero-vad + faster-whisper** | 로컬 VAD + STT | 네트워크 지연 없음. 비용 없음. 정확도 최우선. GPU 권장 |
| **Web Speech API (브라우저)** | 브라우저 내장 STT | 설치 불필요. 정확도 낮음. Chrome 의존. 비추천 |
| **OpenAI Whisper API** | 클라우드 STT | 설치 간편. 네트워크 필요. 비용 발생. 정확도 높음 |
| **Google Speech-to-Text** | 클라우드 STT | 실시간 스트리밍 지원. 비용 발생. 한국어 품질 우수 |

- Phase 2 기본 선택: silero-vad + faster-whisper (정확도 최우선, 로컬 실행)

#### 프론트 미디어 캡처 (Phase 2)

| 선택지 | 역할 | 특징 |
|--------|------|------|
| **MediaRecorder API (브라우저)** | 음성 녹음 | 브라우저 내장. 별도 라이브러리 불필요. WebM/Opus 출력 |
| **RecordRTC** | 음성/영상 녹음 | 크로스 브라우저 호환. WAV 출력 지원. npm 패키지 |
| **getUserMedia API (브라우저)** | 웹캠 스트림 | 브라우저 내장. 카메라 접근용 |

### 파일 구조 원칙

**모든 파일은 지정된 폴더 안에 넣는다. 흩어지게 구현하지 마라.**

```
백엔드 면접 관련 파일은 반드시 다음 구조를 따른다:

backend/core/
  models/
    interview_model.py          # 면접 관련 모델 전부 이 파일에
  views/
    interview/                  # 면접 관련 뷰는 이 폴더 안에
      __init__.py
      job_posting_view.py       # 채용공고 CRUD API
      session_view.py           # 면접 세션 API + 비전 분석 저장
      answer_view.py            # 답변 제출 + SSE 스트리밍 API
      stt_view.py               # 음성→텍스트 변환 API (Phase 2)
      tts_view.py               # 텍스트→음성 변환 API (Phase 2)
      video_view.py             # 아바타 립싱크 영상 생성 API (Phase 2)
  services/
    interview/                  # 면접 관련 서비스는 이 폴더 안에
      __init__.py
      state_engine.py           # L2: Engine — 상태 결정기 (시스템의 뇌)
      analyst.py                # L1: Analyst — 증거 추출기 (LLM)
      planner.py                # L3: Planner — intent 결정 (순수 Python rules, LLM 없음)
      interviewer.py            # L4+L5: 질문 생성 + 말투 보정 (LLM 1번)
      humanizer.py              # L5: 컨텍스트 조립 유틸 (LLM 없음)
      coach.py                  # Coach: evidence 기반 구조적 피드백 (LLM 없음, 템플릿)
      plan_generator.py         # 면접 계획 생성 (공고 + 취약점 → interview_plan)
      feedback_generator.py     # 최종 피드백 생성
      weakness_analyzer.py      # 사용자 취약점 분석
      musetalk_service.py       # 아바타 영상 생성 서비스 (Phase 2)

프론트엔드 면접 관련 파일은 반드시 다음 구조를 따른다:

frontend/src/features/interview/
  MockInterview.vue
  tts.js                       # TTS 유틸리티
  components/
    JobPostingSelector.vue
    InterviewChat.vue
    InterviewFeedback.vue
    InterviewHistory.vue       # 면접 기록
    AudioRecorder.vue          # 음성 녹음 (Phase 2)
    WebcamDisplay.vue          # 웹캠 표시 (Phase 2)
    VisionAnalysisReport.vue   # 비전 분석 보고서 (Phase 2)
  composables/
    useInterview.js            # 세션/메시지/피드백 상태 관리 (SSE 포함)
  api/
    interviewApi.js
```

면접과 무관한 기존 폴더에 면접 파일을 넣지 마라.
하나의 파일에 여러 역할을 합치지 마라.
폴더 구조가 명시되어 있으면 그대로 따르라.

---

## 프로젝트 컨텍스트

이 시스템은 기존 AI-ARCADE 교육 플랫폼에 추가되는 기능이다.

**기존 기술 스택:**
- Backend: Django + DRF (PostgreSQL)
- Frontend: Vue 3 + Vite + Pinia
- LLM: OpenAI GPT API
- 인증: Session 기반 + CSRF
- 스트리밍: SSE (Server-Sent Events) - BugHuntInterviewView에서 사용 중

**기존 코드 위치:**
- 모델: `backend/core/models/`
- 뷰: `backend/core/views/`
- URL: `backend/core/urls.py`
- 프론트 라우터: `frontend/src/main.js`
- Job Planner 뷰: `backend/core/views/job_planner/job_planner_view.py`
- 활동 모델: `backend/core/models/activity_model.py`

---

# PHASE 1: 모의면접 엔진 (텍스트 입력)

MVP 단계. 사용자는 텍스트로 답변을 입력한다.
Phase 2에서 음성 입력으로 전환한다 (면접 엔진 코드 변경 없음).

---

## 1. 프로젝트 목표

채용공고 분석 결과 + 사용자 학습 취약점 데이터를 기반으로
대화형 모의면접을 진행하는 시스템을 구현한다.

핵심 기능:
- 채용공고 기반 맞춤 면접 질문 생성
- 사용자 취약점 기반 질문 가중치 부여
- 답변 분석 → 꼬리질문 생성 → 평가 누적 → 피드백 제공
- SSE 스트리밍으로 실시간 질문/피드백 전달
- 면접 결과를 DB에 저장 (합격/불합격 점수가 아닌 정성적 피드백)

이 시스템은 챗봇이 아니다.
**결정론적 인터뷰 엔진 + 대화 인터페이스다.**

엔진이 절대 권한으로 흐름을 통제하고, LLM은 정보 존재 여부만 태깅한다.
LLM은 절대 "결정"하지 않는다. LLM이 "좋다/나쁘다"를 판단하는 순간 이 서비스의 신뢰도는 무너진다.

---

## 2. 상태 모델 (State Machine)

### 2-1. 역량 슬롯 구조

각 역량은 점수가 아니라 **증거(Evidence) 집합**이다.

Evidence는 **핵심(required)**과 **보조(optional)**로 구분한다.
CLEAR 조건은 특정 항목 하나의 유무가 아니라 **핵심 evidence 기준**으로 판단한다.

**Collaboration 역량 예시:**

| Evidence | 의미 | 구분 |
|----------|------|------|
| `role` | 본인 역할 명시 | 핵심 |
| `action` | 본인 행동 설명 | 핵심 |
| `result` | 결과 변화 | 핵심 |
| `conflict` | 갈등 상황 언급 | 보조 |
| `reflection` | 배운 점 | 보조 |

> `conflict`가 없어도 role + action + result가 확인되면 협업 역량이 충분히 드러난 것이다.
> 갈등 없이도 훌륭한 협업 답변은 존재한다.

### 2-2. 슬롯 상태 전이 규칙

| 상태 | 조건 |
|------|------|
| `UNKNOWN` | 핵심 evidence 0~1개 |
| `UNCERTAIN` | attempt 2회 이상이나 CLEAR 미달 |
| `PARTIAL` | 핵심 evidence 2개 이상 (전체 미달) |
| `CLEAR` | 핵심 evidence 전체 확인 |

**CLEAR 판단 기준:**
- 핵심 evidence 전부 True → CLEAR
- 보조 evidence는 CLEAR 판단에 포함하지 않음 (최종 피드백에는 반영)

**엔진만 상태를 변경할 수 있다.** LLM은 상태를 변경하지 않는다.

### 2-3. 사전 작업: DB 정리

다음 테이블들은 다른 에이전트 실험 중 생성된 것으로, 삭제한다:

```sql
DROP TABLE IF EXISTS job_agent_action CASCADE;
DROP TABLE IF EXISTS job_agent_goal CASCADE;
DROP TABLE IF EXISTS job_agent_state CASCADE;
```

---

## 3. 데이터베이스 모델

### 3-1. SavedJobPosting (채용공고 저장)

파일: `backend/core/models/interview_model.py` (신규 생성)

```python
class SavedJobPosting(BaseModel):
    """Job Planner에서 파싱된 채용공고 저장"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='saved_job_postings')
    company_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    job_responsibilities = models.TextField(blank=True, default='')
    required_qualifications = models.TextField(blank=True, default='')
    preferred_qualifications = models.TextField(blank=True, default='')
    required_skills = models.JSONField(default=list)       # ["Python", "Django", ...]
    preferred_skills = models.JSONField(default=list)       # ["Docker", "AWS", ...]
    experience_range = models.CharField(max_length=50, blank=True, default='')
    deadline = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=20)                # 'url', 'image', 'text'
    source_url = models.URLField(max_length=500, blank=True, default='')
    raw_text = models.TextField(blank=True, default='')
    parsed_data = models.JSONField(default=dict)

    class Meta:
        db_table = 'gym_saved_job_posting'
        ordering = ['-create_date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'source_url'],
                condition=~models.Q(source_url=''),
                name='unique_user_source_url'
            )
        ]
```

**중복 저장 방지:** 동일 사용자가 동일 URL을 다시 파싱하면 `update_or_create`로 업데이트한다.

### 3-2. InterviewSession (면접 세션)

```python
class InterviewSession(BaseModel):
    """모의면접 세션"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='interview_sessions')
    job_posting = models.ForeignKey(SavedJobPosting, on_delete=models.SET_NULL, null=True, related_name='interview_sessions')

    # 역량 슬롯 상태 (증거 기반)
    slot_states = models.JSONField(default=dict)
    # 구조:
    # {
    #   "collaboration": {
    #     "status": "PARTIAL",        # UNKNOWN | UNCERTAIN | PARTIAL | CLEAR
    #     "evidence": {
    #       "conflict": true,
    #       "role": true,
    #       "action": false,
    #       "result": false,
    #       "reflection": false
    #     },
    #     "attempt_count": 1          # 동일 슬롯 시도 횟수
    #   },
    #   ...
    # }

    # 면접 계획 (세션 시작 시 생성)
    interview_plan = models.JSONField(default=dict)

    # 상태 관리
    status = models.CharField(max_length=20, default='in_progress')
    # 'in_progress', 'completed', 'abandoned'
    current_slot = models.CharField(max_length=50, default='')
    current_turn = models.IntegerField(default=0)
    max_turns = models.IntegerField(default=20)

    # 이전 질문 기록 (Planner가 반복 방지에 사용)
    question_history = models.JSONField(default=list)
    # [{"slot": "collaboration", "intent": "행동 회상 유도", "turn": 1}, ...]

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'gym_interview_session'
        ordering = ['-started_at']
```

### 3-3. InterviewTurn (면접 턴 기록)

```python
class InterviewTurn(BaseModel):
    """면접 매 턴 기록"""
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='turns')
    turn_number = models.IntegerField()
    slot = models.CharField(max_length=50)               # 역량 슬롯명

    question = models.TextField()                         # 면접관 질문 (Humanizer 출력)
    answer = models.TextField(blank=True, default='')     # 사용자 답변

    # L1 Analyst 출력 (내부 전용, 사용자에게 미표시)
    evidence_map = models.JSONField(default=dict)
    # {"conflict": true, "role": true, "action": false, "result": false, "reflection": false}

    # L2 Engine 결정
    slot_status_before = models.CharField(max_length=20, default='UNKNOWN')
    slot_status_after = models.CharField(max_length=20, default='UNKNOWN')
    engine_action = models.CharField(max_length=30, default='')
    # 'continue', 'move_slot', 'finish'

    # L3 Planner 출력
    intent = models.CharField(max_length=100, default='')
    # 예: "행동 회상 유도", "결과 변화 확인", "가치관 탐색"

    # Coach 피드백 (LLM 없음 — evidence map 기반 구조적 메시지, 사용자에게 표시)
    coach_feedback = models.TextField(blank=True, default='')
    # 예: "말씀하신 역할과 행동은 확인됐습니다. 이후 어떻게 변화했는지 조금 더 들어볼게요."

    class Meta:
        db_table = 'gym_interview_turn'
        ordering = ['turn_number']
```

### 3-4. InterviewFeedback (최종 피드백)

```python
class InterviewFeedback(BaseModel):
    """면접 종료 후 최종 피드백 (점수 없음, 증거 기반 정성적 피드백)"""
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name='feedback')

    # 역량 슬롯별 최종 상태 요약
    slot_summary = models.JSONField(default=dict)
    # {
    #   "collaboration": {
    #     "final_status": "CLEAR",
    #     "confirmed_evidence": ["conflict", "role", "action", "result"],
    #     "missing_evidence": ["reflection"],
    #     "summary": "갈등 상황에서 본인의 역할과 행동을 구체적으로 설명함"
    #   }
    # }

    overall_summary = models.TextField()           # 전반적인 총평
    top_strengths = models.JSONField(default=list)  # 증거가 충분히 확인된 역량
    top_improvements = models.JSONField(default=list) # 증거가 부족했던 역량
    recommendation = models.TextField(blank=True, default='')
    vision_analysis = models.JSONField(null=True, blank=True)  # 비전 분석 결과 (Phase 2)

    class Meta:
        db_table = 'gym_interview_feedback'
```

### 3-5. 모델 등록

`backend/core/models/__init__.py`에 추가:
```python
from .interview_model import SavedJobPosting, InterviewSession, InterviewTurn, InterviewFeedback
```

```bash
python manage.py makemigrations core
python manage.py migrate
```

---

## 4. 에이전트 계층 구조

이 시스템의 핵심이다. 각 레이어는 단 하나의 책임만 가진다.

```
L1 Analyst     → 증거 추출 (True/False 태깅) [LLM]
L2 Engine      → 상태 결정 (시스템의 뇌) [순수 Python]
Coach          → 구조적 피드백 생성 (evidence 기반 템플릿) [LLM 없음]
L3 Planner     → 질문 의도 결정 [순수 Python rules, LLM 없음]
L4 Interviewer → 자연어 질문 생성 + 말투 보정 [LLM 1번]
L5 Humanizer   → 컨텍스트 조립 유틸 [LLM 없음]
```

**LLM 호출 횟수: 턴당 최대 2번 (L1 Analyst + L4 Interviewer)**

### L1 — Analyst (증거 추출기)

파일: `backend/core/services/interview/analyst.py`

```
입력: 사용자 답변 (str)
출력: evidence boolean map (dict)
```

**역할:**
- 문장에서 구조적 정보의 존재 여부만 판단
- True / False 만 반환

**절대 금지:**
- "잘했다" → 금지
- "부족하다" → 금지
- "괜찮다" → 금지
- 오직 True / False

```python
# 출력 예시 (Collaboration 슬롯)
{
    "conflict": True,   # 갈등 상황 언급 있음
    "role": True,       # 본인 역할 명시 있음
    "action": False,    # 본인 행동 설명 없음
    "result": False,    # 결과 변화 없음
    "reflection": False # 배운 점 없음
}
```

**프롬프트 원칙:**
- "이 발화에 [X]에 해당하는 내용이 존재하는가? True/False로만 답하라."
- 좋고 나쁨 판단 유도 문구 포함 금지

### L2 — Engine (상태 결정기)

파일: `backend/core/services/interview/state_engine.py`

```
입력: evidence map (L1 출력)
출력: 슬롯 상태 업데이트 + 다음 목표 evidence + engine_action
```

**역할:**
- 슬롯 상태(UNKNOWN → PARTIAL → CLEAR) 업데이트
- 종료 조건 판단
- 다음에 수집할 목표 evidence 결정

**여기가 시스템의 뇌다. 모든 결정은 여기서 이루어진다.**

```python
def update_slot(self, slot: str, evidence_map: dict, required: list) -> dict:
    """
    엔진이 슬롯 상태를 갱신한다.
    LLM의 판단 없이 순수 규칙으로만 동작한다.

    required: 핵심 evidence 목록 (Section 6 또는 plan_generator가 결정)
    CLEAR 기준: required evidence 전부 확인 (optional은 무시)
    """
    confirmed_required = [k for k in required if evidence_map.get(k)]
    all_confirmed = [k for k, v in evidence_map.items() if v]
    missing_required = [k for k in required if not evidence_map.get(k)]
    count_required = len(confirmed_required)

    if count_required == 0:
        new_status = "UNKNOWN"
    elif count_required < len(required):
        new_status = "PARTIAL"
    else:
        new_status = "CLEAR"  # 핵심 evidence 전부 확인

    return {
        "status": new_status,
        "confirmed": all_confirmed,          # 전체 확인 evidence (optional 포함, 피드백용)
        "confirmed_required": confirmed_required,  # 핵심 확인 evidence (상태 판정용)
        "missing_required": missing_required  # 아직 미확인 핵심 evidence
    }

def decide_action(self, session) -> str:
    """
    종료 / 슬롯 이동 / 계속 여부를 엔진이 결정한다.
    """
    # 종료 조건
    if session.current_turn >= session.max_turns:
        return "finish"

    all_clear = all(
        s["status"] == "CLEAR"
        for s in session.slot_states.values()
    )
    if all_clear:
        return "finish"

    # 현재 슬롯 상태 확인
    current = session.slot_states.get(session.current_slot, {})
    attempt_count = current.get("attempt_count", 0)

    if current.get("status") == "CLEAR":
        return "move_slot"

    # 2회 실패 → UNCERTAIN 처리 후 이동
    if attempt_count >= 2:
        return "move_slot"  # Engine이 UNCERTAIN으로 마킹 후 이동

    return "continue"
```

**가드레일 (절대 규칙):**
```
✓ 모든 슬롯 최소 1회 방문 보장
✓ max_turns 초과 금지
✓ 동일 evidence 2회 실패 → UNCERTAIN 처리 후 다음 슬롯 이동
✓ 모든 슬롯 CLEAR → 즉시 종료
```

### Coach — 구조적 피드백 생성기

파일: `backend/core/services/interview/coach.py`

```
입력: evidence_map (L1 출력), slot, required (핵심 evidence 목록)
출력: coach_feedback (str) — 사용자에게 표시되는 구조적 피드백 메시지
```

**역할: LLM 없음. evidence_map을 읽어 Python 템플릿으로 구조적 피드백 메시지를 생성한다.**

Coach는 질적 판단을 하지 않는다. "확인된 것"과 "아직 확인되지 않은 것"만 알려준다.

**절대 금지:**
- "잘 하셨습니다" → 금지 (LLM 판단 흉내)
- "부족합니다" → 금지 (부정적 평가)
- 오직 구조적 사실만 전달: "역할과 행동은 확인됐습니다. 결과를 조금 더 말씀해주세요."

```python
# coach.py — LLM 없음, 순수 Python 템플릿

EVIDENCE_LABELS = {
    "role": "역할",
    "action": "행동",
    "result": "결과",
    "conflict": "갈등 상황",
    "reflection": "배운 점",
    "concept": "개념 이해",
    "application": "실제 적용",
    "tradeoff": "기술적 트레이드오프",
    "situation": "상황",
    "analysis": "원인 분석",
    "approach": "해결 접근법",
    "learning": "배운 점",
    "reason": "지원 이유",
    "research": "회사 리서치",
    "alignment": "직무 적합성",
    "aspiration": "성장 방향",
}

# 슬롯별 기본 required evidence (technical_depth는 plan_generator가 동적 결정)
SLOT_REQUIRED = {
    "collaboration": ["role", "action", "result"],
    "problem_solving": ["situation", "analysis", "approach"],
    "motivation": ["reason", "alignment"],
    "growth": ["challenge", "effort", "change"],
}

def generate_feedback(slot: str, evidence_map: dict, required: list = None) -> str:
    """
    evidence_map 기반으로 구조적 피드백 메시지를 생성한다.
    LLM 없음. 순수 Python 템플릿.
    required가 None이면 SLOT_REQUIRED에서 가져온다.
    technical_depth는 plan_generator가 설정한 required를 인자로 전달한다.
    """
    if required is None:
        required = SLOT_REQUIRED.get(slot, list(evidence_map.keys()))

    confirmed = [k for k in required if evidence_map.get(k)]
    missing = [k for k in required if not evidence_map.get(k)]

    if not confirmed:
        return ""  # 아직 아무것도 확인되지 않았으면 피드백 없음 (첫 답변 후 표시 안 함)

    confirmed_labels = [EVIDENCE_LABELS.get(k, k) for k in confirmed]
    missing_labels = [EVIDENCE_LABELS.get(k, k) for k in missing]

    confirmed_str = "·".join(confirmed_labels)

    if not missing:
        return f"{confirmed_str}까지 잘 전달해주셨습니다."

    missing_str = "와 ".join(missing_labels)
    return f"{confirmed_str}은 확인됐습니다. {missing_str}도 조금 더 말씀해주시겠어요?"
```

**Coach 피드백 예시:**

| evidence_map 상태 | 생성되는 피드백 |
|------------------|----------------|
| role=True, action=True, result=False | "역할·행동은 확인됐습니다. 결과도 조금 더 말씀해주시겠어요?" |
| role=True, action=False, result=False | "역할은 확인됐습니다. 행동와 결과도 조금 더 말씀해주시겠어요?" |
| role=True, action=True, result=True | "역할·행동·결과까지 잘 전달해주셨습니다." |
| confirmed 없음 | "" (빈 문자열 — 표시 안 함) |

> Coach 피드백은 다음 턴 질문 **앞에** 표시된다. (SSE type: `"coach_feedback"`)
> 첫 답변 후 confirmed가 없으면 빈 문자열을 반환하며 프론트에서 표시하지 않는다.

---

### L3 — Planner (정보 획득 전략가)

파일: `backend/core/services/interview/planner.py`

```
입력:
  - 부족한 evidence 목록 (missing required evidence)
  - 이전 intent 기록 (question_history의 intent 목록)

출력:
  - 질문 의도(Intent) — 자연어 문자열
```

**역할: 무엇을 알아내야 하는지 결정한다.**

> ⚠️ Planner는 LLM을 사용하지 않는다. 순수 Python rules로 동작한다.
> Planner는 질문을 만들지 않는다. Intent(의도)만 결정한다.

**Evidence → Intent 변환 규칙 (lookup table):**

| 부족 정보 | 질문 의도 |
|----------|----------|
| `action` | 행동 회상 유도 |
| `result` | 결과 변화 확인 |
| `reflection` | 배운 점 탐색 |
| `role` | 책임 범위 확인 |
| `conflict` | 상황 배경 확인 |
| `action` + `result` | 상황 전개 확인 |
| `concept` | 개념 이해 확인 |
| `application` | 실제 적용 경험 확인 |
| `tradeoff` | 기술적 판단 근거 확인 |
| `situation` | 문제 상황 설명 요청 |
| `analysis` | 문제 원인 분석 확인 |
| `approach` | 해결 접근법 확인 |

**반복 방지 (Python rule):** `question_history`의 intent 목록과 비교, 동일 intent는 변형된 표현으로 대체.

```python
# planner.py — LLM 없음, 순수 Python
INTENT_MAP = {
    frozenset(["action"]): "행동 회상 유도",
    frozenset(["result"]): "결과 변화 확인",
    frozenset(["reflection"]): "배운 점 탐색",
    frozenset(["role"]): "책임 범위 확인",
    frozenset(["action", "result"]): "상황 전개 확인",
    frozenset(["concept"]): "개념 이해 확인",
    frozenset(["application"]): "실제 적용 경험 확인",
    frozenset(["tradeoff"]): "기술적 판단 근거 확인",
}

def decide_intent(missing: list, question_history: list) -> dict:
    key = frozenset(missing[:2])
    intent = INTENT_MAP.get(key, "구체적 설명 요청")

    # 반복 방지: 같은 intent가 직전 턴에 사용됐으면 변형
    past_intents = [h.get("intent") for h in question_history[-3:]]
    if intent in past_intents:
        intent = intent + " (다른 각도)"

    return {"missing": missing, "intent": intent}
```

### L4 — Interviewer (대화 생성기 + 말투 보정 통합)

파일: `backend/core/services/interview/interviewer.py`

```
입력:
  - intent (L3 출력)
  - humanizer_context (L5 Humanizer가 조립한 컨텍스트)

출력: 자연스러운 면접관 말투의 질문 (str)
```

**역할: intent를 받아 자연스러운 면접관 질문을 생성한다.**
**L4와 L5는 LLM 호출 1번으로 처리한다. L5 Humanizer의 규칙은 이 프롬프트에 통합된다.**

**절대 금지: 직접 evidence 요구**

| 나쁜 예 ❌ | 좋은 예 ✅ |
|------------|-----------|
| "결과를 말해주세요" | "그 이후 팀 분위기가 어떻게 바뀌었나요?" |
| "행동을 설명하세요" | "그 상황에서 어떻게 대응하셨나요?" |
| "역할이 무엇이었나요?" | "그 프로젝트에서 주로 어떤 부분을 맡으셨나요?" |

```python
# Interviewer 프롬프트 (L4 + L5 통합)
"""
당신은 자연스러운 한국어 면접관이다.

[면접 맥락]
현재 역량 슬롯: {slot}
질문 의도: {intent}
슬롯 전환 여부: {is_slot_transition}
동일 슬롯 시도 횟수: {attempt_count}

[규칙]
1. 짧은 반응구로 시작하라 (이해됐습니다 / 네 / 말씀 잘 들었습니다)
2. 슬롯 전환 시 자연스러운 브릿지 문장을 추가하라
   예: "이 경험만 봐도 일하는 방식이 보이네요. 이번에는..."
3. 동일 슬롯 2회 이상 시도 시 도입부를 변형하라
   예: "조금 더 구체적으로 말씀해 주실 수 있을까요?"
4. evidence 단어(conflict, action, result 등)를 직접 언급하지 마라
5. 질문은 반드시 하나여야 한다 (복수 질문 금지)
6. 직설적 표현을 부드럽게 완화하라
"""
```

### L5 — Humanizer (컨텍스트 조립 유틸)

파일: `backend/core/services/interview/humanizer.py`

```
입력: session 상태 정보
출력: humanizer_context dict (L4 프롬프트에 주입될 컨텍스트)
```

**역할: LLM 없음. L4 Interviewer에 전달할 컨텍스트를 조립하는 유틸 함수다.**

```python
# humanizer.py — LLM 없음, 컨텍스트 조립만
def build_context(session) -> dict:
    """
    L4 Interviewer 프롬프트에 주입할 컨텍스트를 조립한다.
    LLM 호출 없음.
    """
    current_slot_state = session.slot_states.get(session.current_slot, {})
    return {
        "slot": session.current_slot,
        "is_slot_transition": session.just_moved_slot,  # 방금 슬롯 이동했는지
        "attempt_count": current_slot_state.get("attempt_count", 1),
    }
```

---

## 5. 대화 진행 알고리즘 (한 턴 루프)

```
[사용자 답변 입력]
        ↓
[L1 Analyst]   → evidence boolean map 추출 (LLM)
        ↓
[L2 Engine]    → 슬롯 상태 갱신 + engine_action 결정 (순수 Python)
        ↓
    engine_action == "finish"    → [종료 로직 → feedback_generator → SSE]
    engine_action == "move_slot" → [다음 슬롯으로 이동 후 아래 계속]
    engine_action == "continue"  → 아래 계속
        ↓
[Coach]        → evidence_map 기반 구조적 피드백 생성 (LLM 없음, 템플릿)
               → coach_feedback (str) — SSE로 먼저 전송
        ↓
[L2 Engine]    → 다음 목표 evidence 결정 (missing required evidence)
        ↓
[L3 Planner]   → intent 생성 (순수 Python rules)
        ↓
[L5 Humanizer] → L4 Interviewer에 전달할 컨텍스트 조립 (LLM 없음)
        ↓
[L4 Interviewer] → 자연어 질문 생성 (LLM 1번)
        ↓
[출력 → SSE 스트리밍]
  1. type: "coach_feedback" — Coach 피드백 (비어있으면 전송 안 함)
  2. type: "question"       — 면접관 질문 (토큰 스트리밍)
  3. type: "meta"           — 슬롯/상태 메타 정보
```

**각 단계는 반드시 이 순서를 따른다. 순서 변경 금지.**
**Coach → Humanizer → Interviewer 순서 주의: Humanizer가 컨텍스트를 먼저 조립하고 Interviewer가 LLM 호출한다.**

---

## 6. 역량 슬롯 정의

면접에서 평가하는 역량 슬롯 목록과 각 슬롯의 evidence:

| 슬롯 | 핵심 Evidence (required) | 보조 Evidence (optional) | CLEAR 기준 |
|------|--------------------------|--------------------------|-----------|
| `collaboration` | role, action, result | conflict, reflection | 핵심 3개 전부 확인 |
| `technical_depth` | (동적 — 아래 참고) | (동적) | 핵심 전부 확인 |
| `problem_solving` | situation, analysis, approach | result, learning | 핵심 3개 전부 확인 |
| `motivation` | reason, alignment | research, aspiration | 핵심 2개 전부 확인 |
| `growth` | challenge, effort, change | reflection | 핵심 3개 전부 확인 |

**보조 evidence 규칙:**
- 보조 evidence(optional)는 CLEAR 판단에 포함하지 않는다
- 보조 evidence 확인 여부는 최종 피드백에서만 반영한다
- "conflict 없는 협업"은 충분히 가능하다. role + action + result만 확인되면 CLEAR

**technical_depth evidence — 동적 생성:**

`technical_depth` 슬롯의 evidence 항목은 채용공고 기술 스택에 따라 `plan_generator.py`가 **동적으로 결정**한다.

| 예시 토픽 | 동적 생성 required evidence |
|-----------|----------------------------|
| Python 비동기 | asyncio_개념, 실제_사용_경험, 동기방식과_차이, 한계_인식 |
| 데이터베이스 인덱스 | 인덱스_개념, 적용_경험, 성능_비교, 선택_기준 |
| REST API 설계 | 자원_설계, 상태코드_활용, 인증방식, 버저닝_경험 |

> `concept / application / tradeoff`처럼 범용 evidence 단어를 쓰지 않는다.
> 해당 기술에 맞는 구체적 evidence 키를 plan_generator가 생성한다.
> Coach와 Engine은 plan_generator가 설정한 required 목록을 그대로 사용한다.

채용공고 기반으로 슬롯 선택 및 순서를 `plan_generator.py`가 결정한다.

---

## 7. 면접 계획 생성 (plan_generator.py)

### 7-1. 입력

```python
def generate_plan(job_posting: SavedJobPosting, user_weakness: dict) -> dict:
    """
    채용공고 + 취약점 데이터 → 면접 슬롯 순서 + 각 슬롯의 첫 질문 의도 결정
    """
```

LLM 입력:
- `company_name`, `position`
- `required_skills`, `preferred_skills`
- `job_responsibilities`, `required_qualifications`
- `experience_range`
- `user_weakness` (weak_topics, weak_categories)

### 7-2. 출력

```python
{
    "slots": [
        {
            "slot": "motivation",
            "topic": "지원 동기",
            "max_attempts": 2,
            "first_intent": "지원 이유와 회사 리서치 여부 확인"
            # required evidence 없음 — SLOT_REQUIRED["motivation"] 사용
        },
        {
            "slot": "technical_depth",
            "topic": "Python 비동기",
            "max_attempts": 3,
            "first_intent": "비동기 처리 방식 이해 확인",
            "source": "required_skills + weak_topic",
            # technical_depth는 토픽에 따라 evidence를 동적으로 정의
            "required_evidence": [
                "asyncio_개념",       # asyncio/await 동작 방식 이해
                "실제_사용_경험",     # 프로젝트에서 직접 사용해봤는지
                "동기방식과_차이",    # blocking vs non-blocking 이해
                "한계_인식"           # 언제 비동기가 오히려 불리한지
            ],
            "optional_evidence": [
                "이벤트루프_이해",    # 내부 동작 원리
                "라이브러리_선택"     # aiohttp, httpx 등 선택 경험
            ]
        },
        {
            "slot": "collaboration",
            "topic": "팀 협업 경험",
            "max_attempts": 3,
            "first_intent": "갈등 상황과 대응 방식 확인"
            # required evidence 없음 — SLOT_REQUIRED["collaboration"] 사용
        }
    ],
    "total_slots": 5,
    "weakness_boost": ["비동기", "예외처리"]
}
```

**technical_depth evidence 생성 규칙:**
- `required_evidence`: 해당 기술을 실제로 이해하고 사용해봤는지 판단하는 핵심 항목 (3~4개)
- `optional_evidence`: 심화 이해를 보여주는 항목 (최종 피드백에만 반영)
- evidence 키는 한글도 허용 (Analyst 프롬프트에 그대로 전달되므로)
- Coach와 Engine은 이 `required_evidence` 목록을 직접 사용한다

### 7-3. 취약점 분석 (weakness_analyzer.py)

`gym_user_solved_problem` 테이블에서 해당 사용자의 데이터를 조회한다:

```python
def analyze_user_weakness(user: UserProfile) -> dict:
    """
    조회 기준:
      - 낮은 점수 (score < 60): 해당 문제의 주제가 취약
      - 다수 시도 (attempt_number >= 3): 반복 실패한 영역
      - is_perfect == False인 문제들의 공통 주제

    반환:
    {
        "weak_topics": ["예외처리", "비동기"],
        "weak_categories": ["기술", "문제해결"],
        "strength_topics": ["기본 문법", "함수 설계"]
    }
    """
```

---

## 8. Job Planner 수정사항

### 8-1. 파싱 시 자동 저장

`backend/core/views/job_planner/job_planner_view.py`의 `JobPlannerParseView.post()` 수정:

파싱 성공 후 결과를 `SavedJobPosting`에 저장한다.
기존 반환 구조는 유지하되, `saved_posting_id`를 응답에 추가한다.

```python
# 동일 사용자 + 동일 URL → 기존 데이터 업데이트 (중복 저장 안 함)
if source == 'url' and source_url and user:
    saved, created = SavedJobPosting.objects.update_or_create(
        user=user, source_url=source_url, defaults=defaults
    )
else:
    saved = SavedJobPosting.objects.create(user=user, source_url=source_url, **defaults)

response_data['saved_posting_id'] = saved.id
```

---

## 9. API 엔드포인트

파일 위치 (폴더 구조 준수):
```
backend/core/views/interview/
  __init__.py
  job_posting_view.py        # 채용공고 CRUD (GET/POST/DELETE)
  session_view.py            # 면접 세션 생성/조회 (GET/POST)
  answer_view.py             # 답변 제출 + SSE 스트리밍 (POST)
```

### 9-1. 채용공고

```
GET  /api/core/interview/job-postings/          → 저장된 채용공고 목록
POST /api/core/interview/job-postings/          → 새 공고 파싱 및 저장
DELETE /api/core/interview/job-postings/<id>/   → 공고 삭제
```

### 9-2. 면접 세션

```
POST /api/core/interview/sessions/
  → body: { "job_posting_id": 1 }
  → 내부 처리:
    1. SavedJobPosting 로드
    2. weakness_analyzer로 사용자 취약점 분석
    3. plan_generator로 interview_plan 생성 (슬롯 순서 결정)
    4. InterviewSession 생성, slot_states 초기화
    5. L3 Planner → L4 Interviewer → L5 Humanizer로 첫 질문 생성
    6. 첫 질문 반환
  → response: { "session_id": 1, "first_question": "..." }

POST /api/core/interview/sessions/<id>/answer/
  → body: { "answer": "사용자 답변 텍스트" }
  → 한 턴 루프 실행 (L1 → L2 → Coach → L3 → L5 → L4)
  → SSE 스트리밍 응답 (순서대로 전송):

    # 1. Coach 피드백 (비어있으면 전송 안 함)
    data: {"type": "coach_feedback", "text": "역할·행동은 확인됐습니다. 결과도 조금 더 말씀해주시겠어요?"}

    # 2. 다음 질문 (토큰 스트리밍)
    data: {"type": "question", "token": "네"}
    data: {"type": "question", "token": ", 말씀 잘 들었습니다"}
    data: {"type": "question", "token": ". 그 이후 팀 분위기는 어떻게 바뀌었나요?"}

    # 3. 메타 정보 (프론트 상태 업데이트용)
    data: {"type": "meta", "slot": "collaboration", "slot_status": "PARTIAL", "action": "continue", "turn": 3}

    data: [DONE]

  → 슬롯 이동 시 (action == "move_slot"):
    data: {"type": "coach_feedback", "text": "역할·행동·결과까지 잘 전달해주셨습니다."}
    data: {"type": "question", "token": "이 경험만 봐도 일하는 방식이 보이네요. ..."}
    data: {"type": "meta", "slot": "technical_depth", "slot_status": "UNKNOWN", "action": "move_slot", "turn": 4}
    data: [DONE]

  → 면접 종료 시 (action == "finish"):
    data: {"type": "final_feedback", "feedback": { ...InterviewFeedback 전체... }}
    data: [DONE]

**프론트 처리 규칙:**
- `coach_feedback` type 수신 시: 피드백 말풍선 UI에 표시 (질문과 별도 영역)
- `coach_feedback.text`가 빈 문자열이면 표시하지 않음
- `question` token들은 누적하여 면접관 말풍선에 스트리밍 표시
- `meta` 수신 시: 상단 슬롯 상태 UI 업데이트

GET /api/core/interview/sessions/<id>/         → 세션 상태 조회
GET /api/core/interview/sessions/              → 과거 세션 목록
```

### 9-3. SSE 스트리밍 구현 패턴

기존 `BugHuntInterviewView`와 동일한 패턴을 사용한다:

```python
from django.http import StreamingHttpResponse

def _stream_response(self, content_generator):
    def event_stream():
        try:
            for chunk_type, token in content_generator:
                payload = json.dumps({"type": chunk_type, "token": token}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            payload = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
            yield "data: [DONE]\n\n"

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream; charset=utf-8')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
```

### 9-4. URL 등록

`backend/core/urls.py`에 등록된 엔드포인트:

```python
# 면접 세션
path('interview/job-postings/', InterviewJobPostingView.as_view()),
path('interview/job-postings/<int:pk>/', InterviewJobPostingDetailView.as_view()),
path('interview/sessions/', InterviewSessionView.as_view()),
path('interview/sessions/<int:pk>/', InterviewSessionDetailView.as_view()),
path('interview/sessions/<int:pk>/answer/', InterviewAnswerView.as_view()),
path('interview/sessions/<int:pk>/vision/', InterviewVisionView.as_view()),  # 비전 분석 저장

# Phase 2 (이미 구현됨)
path('stt/transcribe/', STTTranscribeView.as_view()),    # 음성→텍스트
path('tts/synthesize/', TTSSynthesizeView.as_view()),    # 텍스트→음성
path('video/generate/', AvatarVideoView.as_view()),      # 아바타 영상 (GPU 서비스)
```

---

## 10. 종료 로직

### 면접 종료 조건

| 조건 | 처리 |
|------|------|
| 모든 슬롯 CLEAR | 즉시 종료 |
| 최대 턴(`max_turns`) 도달 | 강제 종료 |
| 사용자 종료 요청 | 즉시 종료 |

### UNCERTAIN 처리

동일 슬롯에서 2회 시도했으나 evidence 수집 실패:
- 이는 **능력 부족이 아니다**
- Engine이 해당 슬롯을 `UNCERTAIN`으로 마킹 후 다음 슬롯으로 이동
- 최종 피드백에 "충분히 확인되지 않은 역량"으로 기록

### 최종 피드백 (feedback_generator.py)

면접 종료 시 `slot_states`를 기반으로 최종 피드백 생성.

**점수나 합격/불합격 판정 금지. 증거 기반 정성적 피드백만 제공.**

```
입력: session.slot_states (전체 슬롯의 최종 evidence 상태)
출력: InterviewFeedback 모델 저장

출력 형식:
{
  "slot_summary": {
    "collaboration": {
      "final_status": "CLEAR",
      "confirmed_evidence": ["conflict", "role", "action", "result"],
      "missing_evidence": ["reflection"],
      "summary": "갈등 상황에서 본인의 역할과 행동을 구체적으로 설명함. 배운 점 언급이 없었음."
    }
  },
  "overall_summary": "전반적인 총평 (2-3 문단)",
  "top_strengths": ["협업 시 본인 역할 명확히 인식", "문제 해결 과정 논리적 서술"],
  "top_improvements": ["결과 이후 회고(reflection) 부족", "기술적 트레이드오프 설명 필요"],
  "recommendation": "이 포지션 준비를 위한 학습 추천 방향"
}
```

---

## 11. 프론트엔드

### 11-1. 라우터

```javascript
{
  path: '/interview',
  name: 'MockInterview',
  component: MockInterview
}
```

**별도 전용 페이지**로 만든다. 기존 practice 라우트를 재사용하지 않는다.

### 11-2. 페이지 구조

```
frontend/src/features/interview/
  MockInterview.vue              # 메인 페이지 (전용 레이아웃)
  tts.js                         # TTS 유틸리티
  components/
    JobPostingSelector.vue       # 저장된 기업 선택 + 새 URL 입력
    InterviewChat.vue            # 면접 채팅 인터페이스
    InterviewFeedback.vue        # 최종 피드백 표시
    InterviewHistory.vue         # 면접 기록 조회
    AudioRecorder.vue            # 음성 녹음 (Phase 2 — 구현됨)
    WebcamDisplay.vue            # 웹캠 화면 표시 (Phase 2 — 구현됨)
    VisionAnalysisReport.vue     # 비전 분석 보고서 (Phase 2 — 구현됨)
  composables/
    useInterview.js              # 면접 세션 상태 관리 (SSE 처리 포함)
  api/
    interviewApi.js              # API 호출 함수
```

### 11-3. 화면 흐름

```
[1단계: 기업 선택]
  ┌─────────────────────────────────┐
  │  모의면접 준비                    │
  │                                 │
  │  📋 저장된 기업 목록              │
  │  ┌─────────────────────────┐    │
  │  │ 삼성SDS - 백엔드 개발자   │    │
  │  │ 카카오 - AI 엔지니어      │    │
  │  └─────────────────────────┘    │
  │                                 │
  │  또는 새 공고 URL 입력:          │
  │  [________________________]     │
  │  [파싱하기]                      │
  │                                 │
  │           [면접 시작]            │
  └─────────────────────────────────┘

[2단계: 면접 진행]
  ┌─────────────────────────────────┐
  │  모의면접 - 삼성SDS 백엔드 개발자  │
  │  턴 3 | 역량: 협업 (PARTIAL)     │
  │─────────────────────────────────│
  │                                 │
  │  🤖 면접관:                      │
  │  "네, 말씀 잘 들었습니다.         │
  │   그 상황에서 본인은 실제로        │
  │   어떤 행동을 하셨나요?"          │
  │                                 │
  │  [답변 입력 영역]                │
  │  [________________________]     │
  │  [답변 제출]                     │
  └─────────────────────────────────┘

[3단계: 최종 피드백]
  ┌─────────────────────────────────┐
  │  면접 결과 피드백                 │
  │─────────────────────────────────│
  │                                 │
  │  📊 총평                        │
  │  "갈등 상황에서 본인의 역할과..."   │
  │                                 │
  │  ✅ 확인된 역량                  │
  │  • 협업 - 갈등 상황·역할·행동 확인 │
  │  • 문제해결 - 상황·분석·접근 확인  │
  │                                 │
  │  ⚠️ 보완이 필요한 부분           │
  │  • 협업 - 배운 점(reflection) 미확인│
  │  • 기술 - 트레이드오프 설명 필요  │
  │                                 │
  │  [새 면접 시작] [면접 목록으로]   │
  └─────────────────────────────────┘
```

---

## 12. 금지 사항

### LLM 권한 경계 금지 (핵심)

1. **LLM이 "좋다/나쁘다" 판단하는 것 금지** — LLM은 존재 여부(True/False)만 반환한다
2. **LLM이 슬롯 상태(UNKNOWN/PARTIAL/CLEAR)를 결정하는 것 금지** — Engine만 상태를 변경한다
3. **LLM이 다음 슬롯을 결정하는 것 금지** — Engine이 coverage 규칙으로 결정한다
4. **LLM이 종료 여부를 결정하는 것 금지** — Engine이 종료 조건을 판단한다
5. **LLM이 피드백 타이밍을 결정하는 것 금지** — 타이밍은 Engine의 고정 규칙

### 거짓 추상 판단 금지

6. "협업 능력이 뛰어납니다" 같은 추상 판단 금지
7. 증거 없는 정성 평가 금지
8. 합격/불합격 점수 부여 금지

### 구조 원칙

이 시스템은 자유 대화형 챗봇이 아니다.
**결정론적 인터뷰 엔진 + 대화 인터페이스다.**

L1~L5 각 레이어는 단 하나의 책임만 가진다. 합치지 마라.

---

## 13. 구현 순서

```
Step 1: DB 정리 (불필요 테이블 삭제)
Step 2: 모델 생성 (interview_model.py + migration)
Step 3: Job Planner 수정 (파싱 결과 저장)
Step 4: weakness_analyzer.py (취약점 분석)
Step 5: plan_generator.py (슬롯 순서 + 첫 intent 생성)
Step 6: analyst.py (L1 — evidence boolean map 추출)
Step 7: state_engine.py (L2 — 상태 전이 + action 결정)
Step 8: planner.py (L3 — intent 결정)
Step 9: interviewer.py (L4 — 자연어 질문 생성)
Step 10: humanizer.py (L5 — 말투 보정)
Step 11: feedback_generator.py (최종 피드백)
Step 12: answer_view.py (API 엔드포인트 + SSE)
Step 13: URL 등록
Step 14: 프론트엔드 구현
Step 15: 통합 테스트
```

---

## 14. 왜 이 구조가 필요한가

| 일반 LLM 면접 | 이 시스템 |
|--------------|---------|
| 매번 길이 다름 | 항상 비슷한 길이 |
| 기준 다름 | 증거 기반으로 일관된 기준 |
| 평가 불가능 | 설명 가능한 평가 |
| LLM 편향 개입 | 결정론적 규칙으로만 판정 |

**이건 챗봇이 아니라 결정론적 인터뷰 엔진 + 대화 인터페이스다.**

---

# PHASE 2: 음성/화상 전환 — 구현 완료

Phase 1의 면접 엔진 코드는 변경 없이 유지된다.
음성/화상 모듈은 면접 엔진 앞단에 독립적으로 추가되었다.

## 아키텍처

```
[Phase 1 - 텍스트]
키보드 입력 → "텍스트" → 면접 엔진 (L1 → L2 → L3 → L4 → L5)

[Phase 2 - 음성/화상 — 구현됨]
마이크 → VAD(음성감지) → STT(음성→텍스트) → "텍스트" → 면접 엔진 (변경 없음)
웹캠 → VisionAnalysis → 비전 분석 결과 저장 → VisionAnalysisReport.vue 표시
TTS → 면접관 질문을 음성으로 합성
아바타 → MuseTalk 립싱크 영상 생성 (GPU 필요)
```

## 구현된 파일

### 백엔드

```
backend/core/views/interview/
  stt_view.py           # STTTranscribeView — 음성→텍스트
  tts_view.py           # TTSSynthesizeView — 텍스트→음성
  video_view.py         # AvatarVideoView — 아바타 립싱크 영상 (MuseTalk)
  session_view.py       # InterviewVisionView 포함 — 비전 분석 결과 저장

backend/core/services/interview/
  musetalk_service.py   # MuseTalk 아바타 영상 생성 서비스
```

### STT API

```
POST /api/core/stt/transcribe/
  → 음성 데이터(WAV/WebM) → 텍스트 변환
  → Content-Type: multipart/form-data
  → body: { "audio": <binary>, "session_id": 1 }
  → response: { "transcript": "사용자가 말한 내용", "confidence": 0.95 }
```

### TTS API

```
POST /api/core/tts/synthesize/
  → 텍스트 → 음성 합성
```

### 비전 분석 저장 API

```
POST /api/core/interview/sessions/<id>/vision/
  → 비전 분석 결과를 InterviewFeedback.vision_analysis에 저장
```

### 아바타 영상 API

```
POST /api/core/video/generate/
  → AvatarVideoView — MuseTalk 립싱크 영상 생성
  → GPU 전용 서비스 (docker compose --profile gpu up)
```

### 기술 스택

```
STT: silero-vad + faster-whisper
  - silero-vad: PyTorch 기반 음성 활동 감지
  - faster-whisper: CTranslate2 기반 Whisper 최적화 버전

TTS: 텍스트→음성 합성 (tts_view.py)

아바타: MuseTalk
  - AI 립싱크 영상 생성 (GPU 필요)
  - Dockerfile.musetalk, docker-compose musetalk 서비스
  - 모델 파일: backend/GFPGANv1.4.pth, backend/models/
```

### 프론트엔드

```
frontend/src/features/interview/
  tts.js                         # TTS 유틸리티
  components/
    AudioRecorder.vue            # 마이크 녹음 + VAD 연동
    WebcamDisplay.vue            # 웹캠 화면 표시
    VisionAnalysisReport.vue     # 비전 분석 보고서
```

### Phase 2 흐름

```
1. 사용자가 "답변 시작" 버튼 클릭
2. 마이크 + 웹캠 활성화
3. 음성 녹음 시작 (MediaRecorder / AudioRecorder.vue)
4. 침묵 감지 또는 "답변 완료" 버튼으로 녹음 종료
5. 음성 파일 → /api/core/stt/transcribe/ 전송
6. 텍스트 수신 → 사용자에게 확인 표시
7. 확인 후 → /api/core/interview/sessions/<id>/answer/ 전달 (Phase 1과 동일)
8. 면접 종료 후 → 비전 분석 결과 /api/core/interview/sessions/<id>/vision/ 저장
```

### 면접 엔진(Phase 1) 수정 사항

**없음.**

`answer_view.py`의 answer 엔드포인트는 `{"answer": "텍스트"}`를 받는다.
텍스트 출처(키보드/STT)에 무관하게 면접 엔진은 동일하게 처리한다.

---

## 구현 목표

유지보수 가능한 구조와 예측 가능한 면접 흐름을 제공하는 것.
자연스러운 대화보다 **일관된 평가**가 더 중요하다.
점수보다 **설명 가능한 증거 기반 피드백**이 더 중요하다.
