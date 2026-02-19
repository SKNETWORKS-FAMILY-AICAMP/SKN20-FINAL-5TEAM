# 📋 Job Planner Agent v3.1

> AI 기반 채용공고 분석 및 취업 전략 수립 시스템

## 📖 목차

1. [개요](#-개요)
2. [주요 기능](#-주요-기능)
3. [시스템 아키텍처](#-시스템-아키텍처)
4. [기술 스택](#-기술-스택)
5. [사용 방법](#-사용-방법)
6. [API 엔드포인트](#-api-엔드포인트)
7. [핵심 알고리즘](#-핵심-알고리즘)
8. [화면 구성](#-화면-구성)
9. [설치 및 설정](#-설치-및-설정)
10. [구현 세부사항](#-구현-세부사항)

---

## 🎯 개요

**Job Planner Agent**는 AI를 활용하여 채용공고를 분석하고, 사용자의 역량과 매칭하여 맞춤형 취업 전략을 제공하는 지능형 시스템입니다.

### 핵심 가치

- 🔍 **정확한 분석**: OpenAI GPT-4o Vision으로 이미지 채용공고도 정확하게 파싱
- 🎯 **스킬 매칭**: Sentence Transformers로 한영 통합 스킬 매칭 (Python ↔ 파이썬)
- 🤖 **동적 에이전트**: 정보 부족 시 자동으로 추가 질문 생성
- 📊 **종합 보고서**: SWOT 분석, 면접 예상 질문, 실행 전략 제공
- 🎁 **공고 추천**: 사람인/잡코리아 실시간 크롤링으로 맞춤 공고 추천

---

## ✨ 주요 기능

### 1. 📄 채용공고 파싱 (Multi-Input)

**지원 입력 방식:**
- **URL 입력**: 채용공고 URL 크롤링 (BeautifulSoup)
- **이미지 업로드**: GPT-4o Vision API로 OCR 파싱 (복수 이미지 지원)
- **텍스트 입력**: 직접 복사/붙여넣기

**추출 정보:**
```json
{
  "company_name": "회사명",
  "position": "포지션",
  "job_responsibilities": "담당 업무 (원문)",
  "required_qualifications": "필수 요건 (원문)",
  "preferred_qualifications": "우대 조건 (원문)",
  "required_skills": ["Python", "Django", "React"],
  "preferred_skills": ["Docker", "AWS"],
  "experience_range": "2-4년",
  "deadline": "2026-03-15"
}
```

**데이터 병합 기능:**
- URL + 이미지 조합 시 자동 병합
- 중복 제거 및 정보 보완
- 정보 완성도 자동 평가 (7점 척도, 70% 기준)

---

### 2. 🎯 스킬 매칭 & 역량 분석

#### 한영 통합 스킬 정규화
```python
# 60+ 기술 스택 동의어 사전
'파이썬' → 'python'
'리액트' → 'react'
'장고' → 'django'
```

#### 텍스트 전체 분석
- **기존**: `required_skills` 배열만 비교
- **개선**: `required_qualifications` 텍스트 전체에서 60+ 키워드 추출
- 정규식 패턴 매칭으로 숨어있는 스킬도 발견

#### 매칭 알고리즘
```python
# Sentence Transformers
model = 'paraphrase-multilingual-MiniLM-L12-v2'
threshold = 0.50  # 임계값 완화

# Cosine Similarity
similarity = user_embedding @ job_embedding.T
```

#### 분석 결과
- **준비도 점수**: 매칭률(50%) + 경력적합도(20%) + 숙련도(30%)
- **스킬 갭**: 부족한 스킬 목록 + 유사도
- **경력 적합도**: 요구 경력 범위와 사용자 경력 비교
- **인사이트**: 자격증, 학력, 커리어 목표 기반 조언

---

### 3. 🏢 기업 분석

**정보 수집:**
- URL 크롤링 또는 텍스트 입력
- 회사 홈페이지, 채용페이지, 뉴스 기사 등

**분석 항목:**

#### 1) 회사 개요
- 비전 및 미션
- 산업 분야
- 설립 연도 및 규모

#### 2) 기술 스택 & 개발 문화
- 사용 언어/프레임워크
- 개발 문화 (애자일, 코드 리뷰 등)
- 기술 블로그 여부

#### 3) 성장성 & 안정성
- 투자 유치 현황
- 시장 포지션
- 성장 가능성

#### 4) 복지 & 근무환경
- 연봉 수준
- 복지 혜택
- 워라밸 & 재택근무

#### 5) 종합 점수
- 기술력 점수 (0-1)
- 성장성 점수 (0-1)
- 복지 점수 (0-1)
- **총점** 및 추천 의견

---

### 4. 🤖 동적 에이전트 시스템

#### 정보 완성도 자동 평가
```javascript
// 7점 척도
score = (
  company_name ? 1 : 0 +
  position ? 1 : 0 +
  required_skills.length > 0 ? 2 : 0 +  // 가중치 2배
  job_responsibilities ? 1 : 0 +
  required_qualifications ? 1 : 0 +
  preferred_qualifications ? 1 : 0
) / 7

// 70% 미만이면 추가 정보 요청
if (score < 0.7) {
  alert("정보가 부족합니다. 이미지를 추가로 업로드하시겠습니까?");
}
```

#### 맞춤형 질문 생성
**GPT-4o-mini**가 동적으로 생성:
- 부족한 스킬 관련 경험 질문
- 프로젝트 경험 질문
- 학습 계획 질문
- 커리어 목표 질문

**예시:**
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

---

### 5. 📊 종합 보고서 (SWOT + 면접 + 전략)

**GPT-4o**가 생성하는 상세 보고서:

#### 1) SWOT 분석
```yaml
Strengths:
  - Python/Django 5년 경력
  - 대규모 트래픽 처리 경험

Weaknesses:
  - AWS 클라우드 경험 부족
  - Docker/Kubernetes 미흡

Opportunities:
  - AI/ML 역량 추가 학습 가능
  - 클라우드 자격증 취득 기회

Threats:
  - 경쟁자 대비 클라우드 경험 부족
  - 신기술 트렌드 따라가기 필요
```

#### 2) 면접 예상 질문 (10개)
- 기술 질문 (5개)
- 경험 질문 (3개)
- 상황 질문 (2개)

#### 3) 실행 전략
**단기 (즉시~1개월):**
- Docker 공식 문서 학습
- AWS 프리티어로 실습

**중기 (1~3개월):**
- Kubernetes 자격증 취득
- 포트폴리오에 클라우드 프로젝트 추가

**지원 타이밍:**
- 준비도 60% 이상: 즉시 지원 가능
- 준비도 40-60%: 2주 준비 후 지원
- 준비도 40% 미만: 1개월 집중 학습 후 지원

---

### 6. 🎁 공고 추천 시스템

#### 실시간 크롤링
**사람인 + 잡코리아** 각 최대 15개 (총 30개)

```python
# 사람인
search_url = f"https://www.saramin.co.kr/zf_user/search?searchword={position}"

# 잡코리아
search_url = f"https://www.jobkorea.co.kr/Search/?stext={position}"
```

#### 중복 제거
- URL 정확 일치 제거
- 회사명 + 제목 유사도 제거
- 사용자가 분석 중인 공고 제외

#### 스킬 매칭 (threshold: 0.50)
- 사용자 스킬과 공고 스킬 임베딩 비교
- 준비도보다 높은 매칭률만 추천
- 또는 준비도 90% 이상이면서 새로운 스킬 학습 가능한 공고

#### 추천 이유 자동 생성
```python
if match_rate > readiness + 0.2:
    "현재보다 25% 높은 매칭률로 더 적합한 공고입니다."
elif match_rate > readiness + 0.1:
    "보유 스킬과 잘 맞고, 8/10개 스킬이 일치합니다."
else:
    "현재 수준과 비슷하면서 새로운 기술을 배울 수 있는 기회입니다."
```

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vue 3)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  JobPlannerModal.vue (2800+ lines)                   │  │
│  │  - 4-Step Flow (채용공고 → 내정보 → 에이전트 → 결과) │  │
│  │  - Multi-Input Support (URL/Image/Text)              │  │
│  │  - Data Merging & Validation                         │  │
│  │  - Async Background Loading                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             ↕ HTTP API
┌─────────────────────────────────────────────────────────────┐
│                 Backend (Django REST)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  job_planner_view.py (1200+ lines)                   │  │
│  │                                                        │  │
│  │  1. JobPlannerParseView                              │  │
│  │     - URL Crawling (BeautifulSoup)                   │  │
│  │     - Image OCR (GPT-4o Vision)                      │  │
│  │     - Text Parsing (GPT-4o-mini)                     │  │
│  │                                                        │  │
│  │  2. JobPlannerAnalyzeView                            │  │
│  │     - Text Skill Extraction (Regex)                  │  │
│  │     - Skill Normalization (한영 통합)                 │  │
│  │     - Embedding Matching (Sentence Transformers)     │  │
│  │     - Readiness Score Calculation                    │  │
│  │                                                        │  │
│  │  3. JobPlannerCompanyAnalyzeView                     │  │
│  │     - Company Info Crawling                          │  │
│  │     - LLM Analysis (GPT-4o)                          │  │
│  │                                                        │  │
│  │  4. JobPlannerAgentQuestionsView                     │  │
│  │     - Dynamic Question Generation (GPT-4o-mini)      │  │
│  │                                                        │  │
│  │  5. JobPlannerAgentReportView                        │  │
│  │     - SWOT Analysis (GPT-4o)                         │  │
│  │     - Interview Questions (GPT-4o)                   │  │
│  │     - Strategy Planning (GPT-4o)                     │  │
│  │                                                        │  │
│  │  6. JobPlannerRecommendView                          │  │
│  │     - 사람인/잡코리아 Crawling                         │  │
│  │     - Duplicate Filtering                            │  │
│  │     - Skill Matching & Ranking                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             ↕
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  - OpenAI GPT-4o, GPT-4o-mini                               │
│  - Sentence Transformers (paraphrase-multilingual)          │
│  - 사람인 (www.saramin.co.kr)                                │
│  - 잡코리아 (www.jobkorea.co.kr)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 기술 스택

### Frontend
- **Vue 3** (Composition API)
- **Axios** (HTTP Client)
- **Pinia** (State Management)

### Backend
- **Django 5.0**
- **Django REST Framework**
- **OpenAI API** (GPT-4o, GPT-4o-mini)
- **Sentence Transformers** (paraphrase-multilingual-MiniLM-L12-v2)
- **PyTorch** (ML Framework)
- **BeautifulSoup4** (Web Scraping)
- **Requests** (HTTP Library)

### Key Dependencies
```txt
openai>=1.0.0
sentence-transformers>=2.2.0
torch>=2.0.0
beautifulsoup4>=4.12.0
requests>=2.31.0
```

---

## 📱 사용 방법

### 1단계: 채용공고 입력

**방법 1: URL 입력**
```
https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=12345
```

**방법 2: 이미지 업로드**
- 여러 이미지 동시 업로드 가능
- GPT-4o Vision이 자동 파싱

**방법 3: 텍스트 입력**
```
[회사명] 카카오
[포지션] 백엔드 개발자
[필수요건] Python, Django, 3년 이상 경력
...
```

### 2단계: 내 정보 입력

**필수 정보:**
- 보유 스킬 (예: Python, Django, React)
- 스킬 숙련도 (1~5단계)
- 경력 연수

**선택 정보:**
- 이름
- 현재 역할
- 학력
- 자격증
- 커리어 목표
- 준비 가능 기간

### 3단계: 에이전트 질문

AI가 자동 생성한 맞춤 질문에 답변:
- 경험 관련 질문
- 프로젝트 질문
- 학습 계획 질문

**건너뛰기 가능** → 자동으로 다음 단계 진행

### 4단계: 결과 확인

#### 📊 분석 결과
- 준비도: 68.5%
- 스킬 갭: 31.5%
- 경력 적합도: 85.0%

#### 🎯 매칭된 스킬 (8개)
- Python → 파이썬 (100%)
- Django → 장고 (100%)
- React → 리액트 (98%)

#### ❌ 부족한 스킬 (3개)
- AWS → 클라우드 (45%)
- Docker → 도커 (42%)
- Kubernetes (0%)

#### 🏢 기업 분석
- 기술력: 8.5/10
- 성장성: 7.8/10
- 복지: 8.2/10

#### 📋 SWOT 분석
- 강점/약점/기회/위협

#### 💼 면접 예상 질문 (10개)
- 기술 질문
- 경험 질문
- 상황 질문

#### 🎁 추천 공고 (10개)
- 매칭률 순 정렬
- 사람인/잡코리아 실시간

---

## 🔌 API 엔드포인트

### 1. 채용공고 파싱
```http
POST /api/core/job-planner/parse/
Content-Type: application/json

{
  "method": "url",  // "url" | "image" | "text"
  "url": "https://...",
  "images": ["data:image/jpeg;base64,..."],
  "text": "채용공고 텍스트"
}

Response 200:
{
  "company_name": "카카오",
  "position": "백엔드 개발자",
  "required_skills": ["Python", "Django"],
  ...
}
```

### 2. 스킬 매칭 분석
```http
POST /api/core/job-planner/analyze/
Content-Type: application/json

{
  "user_skills": ["Python", "Django", "React"],
  "skill_levels": {"Python": 4, "Django": 3, "React": 4},
  "experience_years": 3,
  "required_skills": ["Python", "Django", "AWS"],
  "required_qualifications": "Python 3년 이상...",
  ...
}

Response 200:
{
  "readiness_score": 0.685,
  "skill_gap_score": 0.315,
  "experience_fit": 0.850,
  "matched_skills": [...],
  "missing_skills": [...],
  "insights": [...]
}
```

### 3. 기업 분석
```http
POST /api/core/job-planner/company-analyze/
Content-Type: application/json

{
  "company_name": "카카오",
  "method": "url",
  "url": "https://www.kakaocorp.com"
}

Response 200:
{
  "company_name": "카카오",
  "overview": {...},
  "tech_stack": {...},
  "growth": {...},
  "welfare": {...},
  "overall_score": {...}
}
```

### 4. 동적 질문 생성
```http
POST /api/core/job-planner/agent-questions/
Content-Type: application/json

{
  "missing_skills": [...],
  "user_profile": {...},
  "job_info": {...}
}

Response 200:
{
  "questions": [
    {
      "question": "Django를 사용한 프로젝트 경험이 있으신가요?",
      "type": "experience",
      "related_skill": "Django"
    }
  ]
}
```

### 5. 최종 보고서 생성
```http
POST /api/core/job-planner/agent-report/
Content-Type: application/json

{
  "user_profile": {...},
  "job_info": {...},
  "analysis_result": {...},
  "agent_answers": {...}
}

Response 200:
{
  "swot": {...},
  "interview_questions": [...],
  "strategy": {...},
  "final_message": "..."
}
```

### 6. 공고 추천
```http
POST /api/core/job-planner/recommend/
Content-Type: application/json

{
  "user_skills": ["Python", "Django"],
  "skill_levels": {...},
  "readiness_score": 0.65,
  "job_position": "백엔드 개발자",
  "current_job_url": "https://...",  // 제외할 공고
  "current_job_company": "카카오",
  "current_job_title": "백엔드 개발자"
}

Response 200:
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
  "total_recommendations": 12
}
```

---

## 🔬 핵심 알고리즘

### 1. 스킬 정규화 (Skill Normalization)

```python
SKILL_SYNONYMS = {
    '파이썬': 'python', 'python': 'python',
    '자바': 'java', 'java': 'java',
    '리액트': 'react', 'react': 'react',
    '장고': 'django', 'django': 'django',
    # ... 60+ 키워드
}

def _normalize_skill(skill):
    skill_lower = skill.lower().strip()
    return SKILL_SYNONYMS.get(skill_lower, skill_lower)
```

### 2. 텍스트에서 스킬 추출

```python
def _extract_skills_from_text(required_text, preferred_text, responsibilities_text):
    import re

    tech_keywords = [
        'Python', 'Java', 'JavaScript', 'React', 'Django',
        'AWS', 'Docker', 'Kubernetes', ...
    ]

    found_skills = []
    for keyword in tech_keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, full_text, re.IGNORECASE):
            found_skills.append(keyword)

    return {'required': required_found, 'preferred': preferred_found}
```

### 3. 임베딩 기반 스킬 매칭

```python
from sentence_transformers import SentenceTransformer

# 모델 로드
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
threshold = 0.50

# 정규화
user_skills_normalized = [normalize_skill(s) for s in user_skills]
required_skills_normalized = [normalize_skill(s) for s in required_skills]

# 임베딩 생성
user_emb = model.encode(user_skills_normalized, normalize_embeddings=True)
req_emb = model.encode(required_skills_normalized, normalize_embeddings=True)

# 코사인 유사도 계산
sim_matrix = user_emb @ req_emb.T

# 매칭
for i, req in enumerate(required_skills):
    best_idx = sim_matrix[:, i].argmax()
    best_score = float(sim_matrix[best_idx, i])

    if best_score >= threshold:
        matched_skills.append({
            "required": req,
            "user_skill": user_skills[best_idx],
            "similarity": round(best_score, 3)
        })
```

### 4. 준비도 점수 계산

```python
# 기본 공식
match_rate = len(matched_skills) / len(required_skills)
exp_fit = calculate_exp_fit(user_years, required_range)

# 숙련도가 있으면 반영
if proficiency_score > 0:
    readiness = match_rate * 0.5 + exp_fit * 0.2 + proficiency_score * 0.3
else:
    readiness = match_rate * 0.7 + exp_fit * 0.3

skill_gap = 1.0 - match_rate
```

### 5. 경력 적합도 계산

```python
def _calculate_exp_fit(years, req_range):
    # "2-4년" → [2, 4] 추출
    nums = re.findall(r'\d+', req_range)
    lo, hi = int(nums[0]), int(nums[-1])

    if lo <= years <= hi:
        return 1.0  # 완벽한 매칭
    elif years < lo:
        return max(0.0, years / lo)  # 경력 부족
    else:
        return max(0.7, 1.0 - (years - hi) * 0.05)  # 경력 초과
```

---

## 🖥️ 화면 구성

### 4단계 Flow

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ 1. 채용공고  │ → │  2. 내정보  │ → │ 3. 에이전트 │ → │  4. 결과    │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
  URL/이미지/      스킬/경력/        동적 질문/        분석/SWOT/
  텍스트 입력      자격증 입력       답변 수집         추천공고
```

### 주요 컴포넌트

**JobPlannerModal.vue** (2800+ lines)
- **Input Methods**: URL/Image/Text 탭
- **Profile Form**: 스킬 입력 + 레벨 슬라이더
- **Agent Q&A**: 동적 질문 카드
- **Results Dashboard**:
  - 분석 차트
  - 스킬 갭 바
  - 기업 분석 카드
  - SWOT 테이블
  - 면접 질문 리스트
  - 추천 공고 카드

---

## 🛠️ 설치 및 설정

### 1. Backend 설정

```bash
# 의존성 설치
pip install -r requirements.txt

# 필수 라이브러리 확인
pip install openai>=1.0.0
pip install sentence-transformers>=2.2.0
pip install torch>=2.0.0
pip install beautifulsoup4>=4.12.0
pip install requests>=2.31.0
```

### 2. 환경 변수 설정

```bash
# .env
OPENAI_API_KEY=sk-...
```

### 3. URL 라우팅 등록

**backend/core/urls.py**
```python
from core.views import (
    JobPlannerParseView,
    JobPlannerAnalyzeView,
    JobPlannerCompanyAnalyzeView,
    JobPlannerAgentQuestionsView,
    JobPlannerAgentReportView,
    JobPlannerRecommendView
)

urlpatterns = [
    path('job-planner/parse/', JobPlannerParseView.as_view()),
    path('job-planner/analyze/', JobPlannerAnalyzeView.as_view()),
    path('job-planner/company-analyze/', JobPlannerCompanyAnalyzeView.as_view()),
    path('job-planner/agent-questions/', JobPlannerAgentQuestionsView.as_view()),
    path('job-planner/agent-report/', JobPlannerAgentReportView.as_view()),
    path('job-planner/recommend/', JobPlannerRecommendView.as_view()),
]
```

### 4. Frontend 통합

**stores/ui.js**
```javascript
export const useUiStore = defineStore('ui', {
  state: () => ({
    isJobPlannerModalOpen: false
  })
});
```

**GlobalModals.vue**
```vue
<JobPlannerModal
  :isOpen="ui.isJobPlannerModalOpen"
  @close="ui.isJobPlannerModalOpen = false"
/>
```

### 5. Docker 재시작

```bash
docker-compose restart backend
```

---

## 📝 구현 세부사항

### 비동기 처리 최적화

**문제:** 에이전트 질문 + 추천 공고 + 최종 보고서를 순차 실행하면 8-10초 소요

**해결:** 백그라운드 병렬 처리

```javascript
// ❌ 기존 (순차 처리)
await this.fetchAgentQuestions();     // 3초
await this.fetchRecommendations();    // 5초
await this.generateFinalReport();     // 2초
// 총 10초

// ✅ 개선 (병렬 처리)
this.currentStep = 'agent';  // 즉시 이동
this.fetchAgentQuestions();       // 백그라운드 (await 제거)
this.fetchRecommendations();      // 백그라운드
this.generateFinalReport();       // 백그라운드
// 총 0.2초 (체감)
```

### 데이터 병합 로직

```javascript
const mergeText = (oldText, newText) => {
  // 타입 체크
  if (typeof oldText !== 'string') oldText = String(oldText || '');
  if (typeof newText !== 'string') newText = String(newText || '');

  // 중복 방지
  if (oldText.trim() === newText.trim()) return oldText;
  if (oldText.includes(newText.trim())) return oldText;
  if (newText.includes(oldText.trim())) return newText;

  // 병합
  return oldText + '\n\n' + newText;
};

const mergeArray = (oldArr, newArr) => {
  return [...new Set([...oldArr, ...newArr])];
};
```

### 정보 완성도 체크

```javascript
checkDataCompleteness() {
  let score = 0;
  const maxScore = 7;
  const missing = [];

  if (this.jobData.company_name) score++;
  else missing.push('회사명');

  if (this.jobData.position) score++;
  else missing.push('포지션');

  if (this.jobData.required_skills?.length > 0) score += 2;  // 가중치 2배
  else missing.push('필수 스킬');

  if (this.jobData.job_responsibilities) score++;
  else missing.push('담당 업무');

  if (this.jobData.required_qualifications) score++;
  else missing.push('필수 요건');

  if (this.jobData.preferred_qualifications) score++;
  else missing.push('우대 조건');

  const completenessRate = score / maxScore;
  this.needsMoreInfo = completenessRate < 0.7;

  if (this.needsMoreInfo) {
    alert(`정보가 부족합니다 (${Math.round(completenessRate * 100)}%)\n\n부족한 정보: ${missing.join(', ')}\n\n이미지를 추가로 업로드하시겠습니까?`);
  }
}
```

---

## 🚀 성능 최적화

### 1. 임베딩 모델 캐싱
- 첫 요청 시 한 번만 로드
- 메모리에 유지 (재사용)

### 2. 웹 크롤링 병렬화
```python
# 사람인 + 잡코리아 동시 실행
saramin_jobs = self._crawl_saramin(position)
jobkorea_jobs = self._crawl_jobkorea(position)
job_listings.extend(saramin_jobs)
job_listings.extend(jobkorea_jobs)
```

### 3. API 타임아웃 설정
```python
response = requests.get(url, timeout=15)  # 15초 제한
```

### 4. 결과 제한
- 추천 공고: 최대 10개
- 크롤링: 각 사이트 최대 15개
- 면접 질문: 10개

---

## 📈 향후 개선사항

### 단기 (1개월)
- [ ] 공고 북마크 기능
- [ ] 지원 이력 추적
- [ ] PDF 이력서 자동 생성

### 중기 (3개월)
- [ ] 링크드인 연동
- [ ] 자동 지원 시스템
- [ ] 면접 연습 챗봇

### 장기 (6개월)
- [ ] 채용 트렌드 분석
- [ ] 연봉 예측 모델
- [ ] 네트워킹 추천

---

## 🤝 기여 방법

1. 이 저장소를 Fork
2. 새 브랜치 생성 (`git checkout -b feature/amazing`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing`)
5. Pull Request 생성

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

---

## 👥 팀

**SKN20-FINAL-5TEAM**

- Backend: Django REST + AI Integration
- Frontend: Vue 3 + Composition API
- AI: OpenAI GPT-4o + Sentence Transformers

---

## 📞 문의

프로젝트 관련 문의사항은 이슈로 남겨주세요.

---

**마지막 업데이트:** 2026-02-16
**버전:** v3.1
