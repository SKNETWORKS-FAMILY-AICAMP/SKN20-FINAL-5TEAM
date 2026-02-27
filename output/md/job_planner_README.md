# Job Planner Agent v3.1

> AI 기반 채용공고 분석 및 취업 전략 수립 시스템 — AI-ARCADE 통합 버전

---

## 목차

1. [개요](#1-개요)
2. [설계 원칙](#2-설계-원칙)
3. [시스템 아키텍처](#3-시스템-아키텍처)
4. [주요 기능](#4-주요-기능)
5. [API 엔드포인트](#5-api-엔드포인트)
6. [핵심 알고리즘](#6-핵심-알고리즘)
7. [화면 구성 (4단계 Flow)](#7-화면-구성-4단계-flow)
8. [파일 구조](#8-파일-구조)
9. [설치 및 실행](#9-설치-및-실행)
10. [트러블슈팅](#10-트러블슈팅)

---

## 1. 개요

**Job Planner Agent**는 채용공고를 분석하여 사용자 역량과 매칭하고, 맞춤형 취업 전략을 제공하는 대화형 AI 시스템이다.

### 핵심 가치

- **정확한 스킬 매칭**: Sentence Transformers 임베딩으로 한영 통합 스킬 매칭 (Python ↔ 파이썬)
- **멀티 입력 지원**: URL 크롤링, 이미지 OCR(GPT-4o Vision), 텍스트 직접 입력
- **동적 에이전트**: 정보 부족 시 자동으로 추가 질문 생성, 답변에 따라 점수 재계산
- **종합 보고서**: SWOT 분석, 면접 예상 질문, 단계별 실행 전략
- **공고 추천**: 사람인/잡코리아/원티드 실시간 크롤링으로 맞춤 공고 추천

### 이 시스템이 하지 않는 것

- 합격 확률 예측
- 자동 지원/이력서 제출
- 학습 기간/효과 수치 예측
- 정확한 시장 경쟁률 측정

---

## 2. 설계 원칙

### "측정은 알고리즘, 해석은 LLM"

| 영역 | 담당 | 이유 |
|------|------|------|
| 스킬 매칭 점수 | Embedding Cosine Similarity | 일관성, 재현성 |
| skill_gap, readiness | Deterministic 함수 | 같은 입력 → 같은 결과 |
| 스킬 카테고리 분류 | 딕셔너리 → Embedding → LLM fallback | 텍스트 분류 (점수 산출 아님) |
| 전략 해석 / 행동 추론 | LLM (GPT-4o-mini) | 자연어 판단 |
| 이미지 OCR | LLM (GPT-4o Vision) | 이미지 처리 |
| 최종 보고서 | LLM (GPT-4o) | 자연어 요약 |

**LLM이 하지 않는 것**: 점수 산출, 학습 기간 예측, 경쟁 강도 수치화

### 신뢰할 수 있는 것만 출력한다

- "공고에 Redis가 필수인데 당신은 경험이 없습니다" (사실)
- "매칭 스킬이 요구사항의 60%입니다" (측정)
- "마감까지 7일이고 부족 스킬이 3개입니다" (계산)
- ~~"7일이면 Redis를 배울 수 있습니다"~~ (근거 없음 — 하지 않음)

---

## 3. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vue 3)                          │
│  JobPlannerModal.vue                                         │
│  - 4-Step Flow: 공고입력 → 내정보 → 추가질문 → 최종결과     │
│  - Multi-Input: URL / Image / Text                           │
│  - 정보 완성도 자동 평가 + 데이터 병합                       │
│  - 백그라운드 병렬 API 호출                                  │
└───────────────────────┬─────────────────────────────────────┘
                        ↕ HTTP API
┌───────────────────────┴─────────────────────────────────────┐
│                 Backend (Django REST)                        │
│  backend/core/views/job_planner/job_planner_view.py          │
│                                                              │
│  1. JobPlannerParseView          채용공고 파싱               │
│     └ URL 크롤링 (BeautifulSoup + Playwright fallback)       │
│     └ 이미지 OCR (GPT-4o Vision)                            │
│     └ 텍스트 파싱 (GPT-4o-mini)                             │
│                                                              │
│  2. JobPlannerAnalyzeView        스킬 매칭 분석              │
│     └ 텍스트 전체 스킬 추출 (Regex, 60+ 키워드)             │
│     └ 한영 스킬 정규화 (SKILL_SYNONYMS 사전)                │
│     └ 임베딩 매칭 (Sentence Transformers)                   │
│     └ 준비도 점수 계산 (deterministic)                      │
│                                                              │
│  3. JobPlannerCompanyAnalyzeView 기업 분석                   │
│     └ 회사 페이지 크롤링                                     │
│     └ LLM 분석 (GPT-4o): 기술력/성장성/복지 점수            │
│                                                              │
│  4. JobPlannerAgentQuestionsView 동적 질문 생성              │
│     └ 부족 스킬 기반 맞춤 질문 (GPT-4o-mini)                │
│                                                              │
│  5. JobPlannerAgentReportView    최종 보고서                 │
│     └ SWOT 분석 + 면접 질문 + 전략 (GPT-4o)                 │
│                                                              │
│  6. JobPlannerRecommendView      공고 추천                   │
│     └ 사람인/잡코리아 크롤링 (각 최대 15개)                 │
│     └ 중복 제거 + 스킬 매칭 순 정렬                         │
└───────────────────────┬─────────────────────────────────────┘
                        ↕
┌───────────────────────┴─────────────────────────────────────┐
│  job-planner-agent/ (독립 모듈)                              │
│  ├── agent/          orchestrator, planner, state, models    │
│  ├── collectors/     saramin, jobkorea, wanted, static,      │
│  │                   browser (Playwright)                    │
│  ├── scoring/        engine (deterministic 점수 계산)        │
│  ├── llm/            gateway (GPT-4o / GPT-4o-mini)         │
│  └── config.py       임계값, 가중치                          │
└───────────────────────┬─────────────────────────────────────┘
                        ↕
┌───────────────────────┴─────────────────────────────────────┐
│                 External Services                            │
│  OpenAI GPT-4o (Vision + Report)                            │
│  OpenAI GPT-4o-mini (Parsing + Questions + Strategy)        │
│  Sentence Transformers (paraphrase-multilingual-MiniLM-L12)  │
│  사람인 (saramin.co.kr)                                      │
│  잡코리아 (jobkorea.co.kr)                                   │
│  원티드 (wanted.co.kr)                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 주요 기능

### 4.1 채용공고 파싱 (Multi-Input)

세 가지 입력 방식을 지원하며, 조합 시 자동 병합한다.

| 방식 | 처리 | 특이사항 |
|------|------|----------|
| URL | BeautifulSoup → Playwright fallback | JS 렌더링 사이트 대응 |
| 이미지 | GPT-4o Vision OCR | 다중 이미지, 긴 이미지 자동 분할 |
| 텍스트 | GPT-4o-mini 파싱 | 자유 형식 텍스트 |

**파싱 결과 스키마:**

```json
{
  "company_name": "카카오",
  "position": "백엔드 개발자",
  "required_skills": ["Python", "Django", "PostgreSQL"],
  "preferred_skills": ["Docker", "Kubernetes"],
  "experience_range": "2-4년",
  "job_responsibilities": "대규모 트래픽 처리 서버 개발...",
  "required_qualifications": "Python 3년 이상, Django 경험...",
  "preferred_qualifications": "AWS 경험자 우대...",
  "deadline": "2026-03-15"
}
```

**정보 완성도 자동 평가 (7점 척도):**

```
company_name        +1
position            +1
required_skills     +2  (가중치 2배)
job_responsibilities +1
required_qualifications +1
preferred_qualifications +1
─────────────────────
합계 7점 → 70% 미만이면 추가 입력 요청
```

---

### 4.2 스킬 매칭 & 역량 분석

#### 한영 통합 스킬 정규화

60+ 기술 스택 동의어 사전으로 언어 무관 매칭:

```python
'파이썬' → 'python'
'리액트' → 'react'
'장고'   → 'django'
```

#### 분석 결과 구조

- **준비도 점수** (0.0 ~ 1.0): 매칭률(50%) + 경력적합도(20%) + 숙련도(30%)
  - 숙련도 정보 없을 시: 매칭률(70%) + 경력적합도(30%)
- **스킬 갭**: 1.0 - 매칭률
- **경력 적합도**: 요구 경력 범위와 사용자 경력 비교
- **인사이트**: 자격증, 학력, 커리어 목표 기반 조언

#### 준비도 색상 기준

| 범위 | 등급 | 의미 |
|------|------|------|
| 80% 이상 | Excellent | 즉시 지원 가능 |
| 60-80% | Good | 일부 보완 후 지원 |
| 40-60% | Fair | 2주 준비 후 지원 |
| 40% 미만 | Poor | 1개월 집중 학습 권장 |

---

### 4.3 기업 분석

회사 URL 또는 텍스트 기반으로 GPT-4o가 분석:

| 항목 | 내용 |
|------|------|
| 회사 개요 | 비전/미션, 산업 분야, 설립 연도, 규모 |
| 기술 스택 & 개발 문화 | 사용 언어/프레임워크, 애자일/코드리뷰, 기술 블로그 |
| 성장성 & 안정성 | 투자 유치, 시장 포지션, 성장 가능성 |
| 복지 & 근무환경 | 연봉 수준, 복지 혜택, 워라밸/재택 |
| 종합 점수 | 기술력(0-1) / 성장성(0-1) / 복지(0-1) |

---

### 4.4 동적 에이전트 질문

GPT-4o-mini가 부족 스킬과 사용자 프로필을 바탕으로 맞춤 질문 생성:

```json
[
  {
    "question": "Django를 사용한 프로젝트 경험이 있으신가요?",
    "type": "experience",
    "related_skill": "Django"
  },
  {
    "question": "AWS 클라우드 환경에서 배포 경험이 있으신가요?",
    "type": "skill_depth",
    "related_skill": "AWS"
  }
]
```

사용자 답변 → 상태 보정 → 점수 재계산 (에이전트의 핵심)

건너뛰기 가능: 질문 없이 바로 최종 결과로 이동

---

### 4.5 종합 보고서 (SWOT + 면접 + 전략)

GPT-4o가 생성하는 3-part 보고서:

**① SWOT 분석**

```
Strengths    현재 보유한 강점 스킬, 경력
Weaknesses   부족한 스킬, 경험 공백
Opportunities 학습 가능한 영역, 자격증 취득 기회
Threats      경쟁자 대비 약점, 트렌드 변화
```

**② 면접 예상 질문 (10개)**
- 기술 질문 5개
- 경험 질문 3개
- 상황 질문 2개

**③ 실행 전략**
- 단기 (즉시~1개월): 즉시 착수 가능한 학습 항목
- 중기 (1~3개월): 포트폴리오/자격증 취득
- 지원 타이밍: 준비도 기반 권장 시점

---

### 4.6 공고 추천

사람인 + 잡코리아 각 최대 15개(총 30개)를 크롤링 후:

1. 현재 분석 중인 공고 제외
2. URL 중복 제거
3. 회사명+제목 유사도 기반 중복 제거
4. 사용자 스킬과 임베딩 매칭 → 준비도보다 높은 공고 우선 추천
5. 추천 이유 자동 생성

---

## 5. API 엔드포인트

모든 엔드포인트: `POST /api/core/job-planner/<path>/`

### 5.1 채용공고 파싱

```
POST /api/core/job-planner/parse/
```

```json
// 요청
{
  "type": "url",           // "url" | "image" | "text"
  "url": "https://...",
  "images": ["data:image/jpeg;base64,..."],
  "text": "채용공고 텍스트"
}

// 응답
{
  "company_name": "카카오",
  "position": "백엔드 개발자",
  "required_skills": ["Python", "Django"],
  "preferred_skills": ["Docker"],
  "experience_range": "2-4년",
  "job_responsibilities": "...",
  "required_qualifications": "...",
  "preferred_qualifications": "...",
  "deadline": "2026-03-15"
}
```

### 5.2 스킬 매칭 분석

```
POST /api/core/job-planner/analyze/
```

```json
// 요청
{
  "user_skills": ["Python", "Django", "React"],
  "skill_levels": {"Python": 4, "Django": 3},
  "experience_years": 3,
  "required_skills": ["Python", "Django", "AWS"],
  "required_qualifications": "Python 3년 이상...",
  "experience_range": "2-4년"
}

// 응답
{
  "readiness_score": 0.685,
  "skill_gap_score": 0.315,
  "experience_fit": 0.850,
  "matched_skills": [
    {"required": "Python", "user_skill": "Python", "similarity": 1.0}
  ],
  "missing_skills": [
    {"required": "AWS", "closest_match": "Docker", "similarity": 0.42}
  ],
  "insights": ["자격증 AWS SAA 취득을 권장합니다."]
}
```

### 5.3 기업 분석

```
POST /api/core/job-planner/company-analyze/
```

```json
// 요청
{
  "company_name": "카카오",
  "method": "url",
  "url": "https://www.kakaocorp.com"
}

// 응답
{
  "company_name": "카카오",
  "overview": {"vision": "...", "industry": "IT", "size": "대기업"},
  "tech_stack": {"languages": ["Kotlin", "Python"], "culture": "애자일"},
  "growth": {"investment": "상장", "market_position": "국내 1위"},
  "welfare": {"salary_level": "상위권", "remote": true},
  "overall_score": {"tech": 0.85, "growth": 0.78, "welfare": 0.82}
}
```

### 5.4 동적 질문 생성

```
POST /api/core/job-planner/agent-questions/
```

```json
// 요청
{
  "missing_skills": [{"required": "AWS", "similarity": 0.42}],
  "user_profile": {"skills": ["Python", "Django"], "experience_years": 3},
  "job_info": {"position": "백엔드 개발자", "company_name": "카카오"}
}

// 응답
{
  "questions": [
    {
      "question": "AWS 사용 경험이 있으신가요?",
      "type": "skill_depth",
      "related_skill": "AWS"
    }
  ]
}
```

### 5.5 최종 보고서

```
POST /api/core/job-planner/agent-report/
```

```json
// 요청
{
  "user_profile": {...},
  "job_info": {...},
  "analysis_result": {...},
  "agent_answers": {"AWS 사용 경험이 있으신가요?": "프리티어로 EC2만 써봤습니다."}
}

// 응답
{
  "swot": {
    "strengths": ["Python/Django 3년 경력"],
    "weaknesses": ["AWS 경험 부족"],
    "opportunities": ["AWS SAA 자격증 취득 가능"],
    "threats": ["클라우드 경험자와 경쟁"]
  },
  "interview_questions": ["Django ORM N+1 문제 해결 경험은?", ...],
  "strategy": {
    "short_term": ["Docker 공식 문서 학습", "AWS 프리티어 실습"],
    "mid_term": ["Kubernetes 자격증 취득"],
    "apply_timing": "2주 준비 후 지원 권장"
  },
  "final_message": "현재 준비도 68.5%입니다..."
}
```

### 5.6 공고 추천

```
POST /api/core/job-planner/recommend/
```

```json
// 요청
{
  "user_skills": ["Python", "Django"],
  "skill_levels": {"Python": 4},
  "readiness_score": 0.65,
  "job_position": "백엔드 개발자",
  "current_job_url": "https://...",
  "current_job_company": "카카오",
  "current_job_title": "백엔드 개발자"
}

// 응답
{
  "recommendations": [
    {
      "source": "사람인",
      "company_name": "네이버",
      "title": "Python 백엔드 개발자",
      "url": "https://...",
      "match_rate": 0.82,
      "matched_count": 8,
      "total_skills": 10,
      "reason": "보유 스킬과 잘 맞고, 8/10개 스킬이 일치합니다."
    }
  ],
  "total_found": 30,
  "total_recommendations": 10
}
```

---

## 6. 핵심 알고리즘

### 6.1 스킬 정규화

```python
SKILL_SYNONYMS = {
    '파이썬': 'python', 'python': 'python',
    '자바': 'java', 'java': 'java',
    '리액트': 'react', 'react': 'react',
    '장고': 'django', 'django': 'django',
    # 60+ 키워드
}

def normalize_skill(skill: str) -> str:
    return SKILL_SYNONYMS.get(skill.lower().strip(), skill.lower().strip())
```

### 6.2 임베딩 기반 스킬 매칭

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
threshold = 0.50  # config.py: SKILL_MATCH_THRESHOLD

# 정규화
user_norm = [normalize_skill(s) for s in user_skills]
req_norm  = [normalize_skill(s) for s in required_skills]

# 임베딩 → 코사인 유사도
user_emb = model.encode(user_norm, normalize_embeddings=True)
req_emb  = model.encode(req_norm,  normalize_embeddings=True)
sim_matrix = user_emb @ req_emb.T  # shape: (|user|, |required|)

# 매칭
for i, req in enumerate(required_skills):
    best_idx = sim_matrix[:, i].argmax()
    score = float(sim_matrix[best_idx, i])
    if score >= threshold:
        matched.append({"required": req, "user_skill": user_skills[best_idx], "similarity": score})
    else:
        missing.append({"required": req, "closest_match": user_skills[best_idx], "similarity": score})
```

### 6.3 준비도 점수 계산

```python
# config.py 가중치
WEIGHT_REQUIRED_SKILLS  = 0.6
WEIGHT_PREFERRED_SKILLS = 0.2
WEIGHT_EXPERIENCE       = 0.2

match_rate = len(matched) / len(required_skills)
exp_fit    = calculate_exp_fit(user_years, experience_range)

if proficiency_score > 0:
    readiness = match_rate * 0.5 + exp_fit * 0.2 + proficiency_score * 0.3
else:
    readiness = match_rate * 0.7 + exp_fit * 0.3

skill_gap = 1.0 - match_rate
```

### 6.4 경력 적합도

```python
def calculate_exp_fit(years: int, req_range: str) -> float:
    nums = re.findall(r'\d+', req_range)
    lo, hi = int(nums[0]), int(nums[-1])

    if lo <= years <= hi:
        return 1.0              # 범위 내: 완벽 매칭
    elif years < lo:
        return max(0.0, years / lo)  # 경력 부족
    else:
        return max(0.7, 1.0 - (years - hi) * 0.05)  # 경력 초과
```

### 6.5 비동기 병렬 처리

```javascript
// 에이전트 질문 단계로 이동하면서 백그라운드에서 병렬 처리
this.currentStep = 'agent';          // 즉시 UI 전환
this.fetchAgentQuestions();          // 백그라운드
this.fetchRecommendations();         // 백그라운드
this.generateFinalReport();          // 백그라운드
// 결과 탭 진입 시 이미 완료되어 있음
```

---

## 7. 화면 구성 (4단계 Flow)

```
┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
│ 1. 공고   │ → │ 2. 내정보 │ → │ 3. 추가   │ → │ 4. 최종   │
│   입력    │   │           │   │   질문    │   │   결과    │
└───────────┘   └───────────┘   └───────────┘   └───────────┘
  URL/이미지/    스킬/경력/      AI 생성 질문/    분석차트/
  텍스트 입력    숙련도/자격증   답변 or 건너뛰기  SWOT/추천공고
```

### 단계별 상세

**Step 1 — 공고 입력**
- URL, 이미지 업로드(다중), 텍스트 입력 탭
- 입력 후 파싱 API 호출 → 정보 완성도 자동 체크
- 70% 미만이면 추가 입력 유도

**Step 2 — 내 정보**
- 보유 스킬 + 숙련도 슬라이더 (1~5단계)
- 경력 연수, 학력, 자격증 (선택)
- 커리어 목표, 준비 가능 기간 (선택)
- "분석 시작" → 스킬 매칭 API 호출

**Step 3 — 추가 질문 (에이전트)**
- AI 생성 맞춤 질문 카드
- 답변 입력 or 건너뛰기 가능
- 답변 제출 → 보정된 분석 결과로 보고서 생성

**Step 4 — 최종 결과**
- 준비도 차트 + 스킬 갭 바
- 매칭/부족 스킬 목록
- 기업 분석 카드 (기술력/성장성/복지)
- SWOT 테이블
- 면접 예상 질문 10개
- 추천 공고 카드 (매칭률 순)

---

## 8. 파일 구조

```
project-root/
├── job-planner-agent/              # 독립 AI 엔진 모듈
│   ├── agent/
│   │   ├── models.py               # JobPosting, UserProfile 데이터 모델
│   │   ├── orchestrator.py         # 전체 흐름 조율
│   │   ├── planner.py              # GPT-4o-mini 맥락 분석/재계획
│   │   └── state.py                # 세션 상태 관리
│   ├── collectors/
│   │   ├── router.py               # 입력 타입 감지 및 라우팅
│   │   ├── static_collector.py     # BeautifulSoup 정적 크롤링
│   │   ├── browser_collector.py    # Playwright 동적 크롤링
│   │   ├── saramin_collector.py    # 사람인 공고 수집
│   │   ├── jobkorea_collector.py   # 잡코리아 공고 수집
│   │   └── wanted_collector.py     # 원티드 공고 수집
│   ├── scoring/
│   │   └── engine.py               # Deterministic 점수 계산
│   ├── llm/
│   │   └── gateway.py              # OpenAI API 래퍼 (GPT-4o / 4o-mini)
│   ├── config.py                   # SKILL_MATCH_THRESHOLD, 가중치
│   ├── main.py                     # CLI 진입점
│   └── requirements.txt
│
├── backend/
│   └── core/
│       ├── views/
│       │   └── job_planner/
│       │       └── job_planner_view.py  # 6개 API 뷰 (1200+ lines)
│       └── urls.py                      # URL 라우팅
│
└── frontend/
    └── src/
        ├── components/
        │   ├── JobPlannerModal.vue       # 메인 UI 컴포넌트 (2800+ lines)
        │   └── GlobalModals.vue          # 모달 마운트
        ├── features/home/
        │   └── LandingView.vue           # Hero 섹션 "Job Planner" 버튼
        └── stores/
            └── ui.js                     # isJobPlannerModalOpen 상태
```

---

## 9. 설치 및 실행

### 사전 요구사항

```bash
# Python 의존성
pip install openai>=1.0.0
pip install sentence-transformers>=2.2.0
pip install torch>=2.0.0
pip install beautifulsoup4>=4.12.0
pip install requests>=2.31.0

# 동적 크롤링 (선택)
pip install playwright
playwright install chromium
```

### 환경변수

```bash
# .env (필수)
OPENAI_API_KEY=sk-...
```

OpenAI API 키 없이도 스킬 매칭 분석은 동작하나, 파싱/보고서/질문 생성 기능은 사용 불가.

### 서버 실행

```bash
# Backend
cd backend
python manage.py runserver

# Frontend
cd frontend
npm run dev
```

### Docker

```bash
docker-compose restart backend
```

### URL 라우팅 확인

```python
# backend/core/urls.py
urlpatterns = [
    path('job-planner/parse/',            JobPlannerParseView.as_view()),
    path('job-planner/analyze/',          JobPlannerAnalyzeView.as_view()),
    path('job-planner/company-analyze/',  JobPlannerCompanyAnalyzeView.as_view()),
    path('job-planner/agent-questions/',  JobPlannerAgentQuestionsView.as_view()),
    path('job-planner/agent-report/',     JobPlannerAgentReportView.as_view()),
    path('job-planner/recommend/',        JobPlannerRecommendView.as_view()),
]
```

---

## 10. 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `ImportError: No module named 'sentence_transformers'` | 의존성 미설치 | `pip install -r job-planner-agent/requirements.txt` |
| API 500 "Job Planner 모듈이 설치되지 않았습니다" | sys.path 문제 | `job-planner-agent/` 경로 확인, 의존성 재설치 |
| `strategy: null` 또는 보고서 미생성 | OPENAI_API_KEY 미설정 | `.env`에 키 추가 |
| URL 파싱 실패 | JS 렌더링 사이트 | Playwright 설치 (`pip install playwright && playwright install chromium`) |
| 임베딩 모델 로드 느림 | 첫 실행 시 모델 다운로드 | 정상 동작 — 이후 캐시에서 로드됨 |

---

## 기술 스택 요약

| 영역 | 기술 |
|------|------|
| Frontend | Vue 3 (Composition API), Pinia, Axios |
| Backend | Django 5.0, Django REST Framework |
| AI / LLM | OpenAI GPT-4o (Vision + Report), GPT-4o-mini (Parsing + Questions) |
| 스킬 매칭 | Sentence Transformers (paraphrase-multilingual-MiniLM-L12-v2), PyTorch |
| 크롤링 | BeautifulSoup4, Playwright (동적), Requests |
| 공고 소스 | 사람인, 잡코리아, 원티드 |

---

**버전:** v3.1 | **최종 업데이트:** 2026-02-25 | **팀:** SKN20-FINAL-5TEAM
