# 🎮 AI-ARCADE 프로젝트 - 완전 개요 (2026-02-20)

> **AI 엔지니어 육성 플랫폼**
> 게임처럼 배우고, 실무처럼 평가받는 대화형 학습 시스템

---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [시스템 아키텍처](#2-시스템-아키텍처)
3. [기술 스택](#3-기술-스택)
4. [데이터 모델](#4-데이터-모델)
5. [핵심 기능](#5-핵심-기능)
6. [현재 구현 상태](#6-현재-구현-상태)
7. [진행 중인 리팩토링](#7-진행-중인-리팩토링)
8. [향후 개선 방향](#8-향후-개선-방향)
9. [주요 고려사항](#9-주요-고려사항)

---

## 1. 프로젝트 개요

### 🎯 미션

```
기존 AI 교육 방식의 한계:
❌ 단순 알고리즘 반복 훈련 → ✅ 실무형 반복 훈련
❌ 강의/과제 반복 (느린 피드백) → ✅ 즉각적인 AI 피드백
❌ 느린 피드백 루프 → ✅ 실제 파이프라인 경험
❌ 일관되지 않은 평가 → ✅ 객관적인 AI 기반 평가
```

### 📊 시장 기회

- **글로벌 AI 교육 시장**: CAGR 41.4% (2025-2029)
  - 2025: 76억 달러 → 2029: 303억 달러 (약 4배 성장)
- **한국 정부 AI 인재 육성 정책**: 1.4조 원 투자
- **기업 수요**: "AI 시스템을 설계·운영·평가할 수 있는 실무 인재"

### 🎮 차별화 요소

| 구분 | 기존 방식 | AI-ARCADE |
|------|---------|----------|
| **학습 방식** | 코드 작성만 | 코드 + 설계 + 디버깅 |
| **평가** | 정답/오답 | 사고력 + 코드 품질 + 설명 능력 |
| **피드백** | 느림/일관성 부족 | 즉시/AI 기반/실무 관점 |
| **경험** | 단편적 | 통합 파이프라인 |

---

## 2. 시스템 아키텍처

### 2.1 전체 구조

```
┌─────────────────────────────────────────────────────────┐
│                   프론트엔드 (Vue 3)                     │
│  • LandingView: 홈페이지 & 실습 선택                    │
│  • 3개 Practice UI (의사코드/버그헌트/아키텍처)         │
│  • 게이미피케이션 (진행률, 레벨, 성취)                 │
└──────────────────────┬────────────────────────────────┘
                       │ REST API
┌──────────────────────┴────────────────────────────────┐
│                  백엔드 (Django REST)                 │
│  • 실습 로직 & 평가 엔진                               │
│  • 사용자 진행도 관리                                  │
│  • AI 호출 & 결과 반환                                |
└──────────────────────┬────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   ┌─────────┐  ┌──────────┐  ┌────────────┐
   │  DB     │  │ OpenAI   │  │ 외부 API   │
   │ (PG)    │  │ (LLM)    │  │           │
   └─────────┘  └──────────┘  └────────────┘
```

### 2.2 디렉토리 구조

```
프로젝트/
├── 📁 frontend/
│   ├── src/
│   │   ├── features/
│   │   │   ├── home/
│   │   │   │   └── LandingView.vue (홈페이지)
│   │   │   ├── practice/
│   │   │   │   ├── pseudocode/ (의사코드 실습)
│   │   │   │   ├── bughunt/ (버그헌트 실습)
│   │   │   │   ├── architecture/ (아키텍처 설계)
│   │   │   │   └── job-planner/ (AI 커리어 조언)
│   │   │   └── dashboard/ (관리 & 기록)
│   │   ├── components/ (공용 컴포넌트)
│   │   │   ├── LearningAnalyticsReport.vue ✨ (새 기능)
│   │   │   ├── CustomProblemSolver.vue ✨ (새 기능)
│   │   │   └── ...
│   │   ├── services/ (API 호출)
│   │   │   ├── learningAnalyticsService.js ✨ (새 기능)
│   │   │   └── ...
│   │   └── stores/ (상태 관리 - Pinia)
│   │       └── ui.js (모달 상태)
│   └── public/ (이미지, 데이터)
│
├── 📁 backend/
│   ├── core/
│   │   ├── models/ (데이터 모델)
│   │   │   └── UserSolvedProblem, UserProfile 등
│   │   ├── views/ (API 엔드포인트)
│   │   │   ├── pseudocode_evaluation.py
│   │   │   ├── architecture_view.py
│   │   │   ├── learning_analytics_view.py ✨ (새 기능)
│   │   │   └── ...
│   │   ├── services/ (비즈니스 로직)
│   │   │   ├── pseudocode_evaluator.py
│   │   │   ├── learning_analytics_adapter.py ✨ (새 기능)
│   │   │   └── ...
│   │   └── urls.py (라우팅)
│   └── settings.py (설정)
│
└── 📁 job-planner-agent/
    └── 커리어 조언 에이전트
```

---

## 3. 기술 스택

### 프론트엔드
| 기술 | 용도 | 버전 |
|------|------|------|
| **Vue 3** | UI 프레임워크 | 3.x |
| **Vite** | 번들러 & 개발 서버 | 5.x |
| **Vue Router** | 라우팅 | 4.x |
| **Pinia** | 상태 관리 | 2.x |
| **Axios** | HTTP 클라이언트 | 1.x |
| **Tailwind CSS** | 스타일링 | 3.x |
| **Lucide Vue** | 아이콘 라이브러리 | - |
| **CodeMirror** | 코드 편집기 | 5.x |
| **Mermaid** | 다이어그램 | 10.x |
| **Marked** | 마크다운 렌더러 | 11.x |

### 백엔드
| 기술 | 용도 | 버전 |
|------|------|------|
| **Django** | 웹 프레임워크 | 5.x |
| **Django REST Framework** | REST API | 3.14.x |
| **PostgreSQL** | 데이터베이스 | 14+ |
| **OpenAI API** | LLM (gpt-4o-mini) | v1 |
| **Python** | 언어 | 3.11+ |

### 배포 & 인프라
| 기술 | 용도 |
|------|------|
| **Docker** | 컨테이너화 |
| **Docker Compose** | 로컬 개발 환경 |

---

## 4. 데이터 모델

### 4.1 핵심 테이블

```sql
-- 사용자 정보
UserProfile {
  id (PK)
  email (UNIQUE)
  nickname
  avatar_url
  points (단백질 쉐이크)
  current_grade (등급)
  is_superuser
  created_at
}

-- 학습 기록
UserSolvedProblem {
  id (PK)
  user_id (FK → UserProfile)
  practice_detail_id (FK → PracticeDetail)
  score (0~100)
  submitted_data (JSON)  ← evaluation, missed_points 포함
  solved_date
  created_at
}

-- 실습 세부사항
PracticeDetail {
  id (PK)
  practice_id (FK → Practice)
  detail_id (unique)
  detail_title
  description
}

-- 실습 유닛
Practice {
  id (PK)
  name (Unit 1: Pseudo Practice, Unit 2: Bug Hunt, Unit 3: Architecture)
  description
  unit_number (1, 2, 3)
}

-- 진행도 (Phase 3에서 추가 예정)
AnalyticsSession {
  id (PK)
  user_id (FK)
  session_type
  weakness_profile (JSON)
  report (TEXT)
  custom_problems (JSON)
  created_at
}
```

### 4.2 submitted_data 구조

```json
{
  "pseudocode": "사용자 작성 의사코드",
  "evaluation": {
    "metrics": {
      "design": 20,
      "consistency": 18,
      "edge_case": 15,
      "abstraction": 12,
      "implementation": 10
    },
    "summary": "피드백 요약",
    "strengths": ["강점1", "강점2"],
    "improvements": ["개선점1"]
  },
  "missed_points": {
    "design": [],
    "consistency": ["동시성 제어 미흡"],
    "edge_case": ["null 처리 누락"],
    "abstraction": [],
    "implementation": []
  },
  "tail_question": "꼬리질문",
  "is_low_effort": false,
  "is_auto_saved": true
}
```

---

## 5. 핵심 기능

### 5.1 **Unit 1: Pseudo Practice (의사코드)**

**목표:** 데이터 처리 파이프라인 설계 & 구현 사고력

**4단계 프로토콜:**
1. **분석 (Analysis)**: 비즈니스 요구사항 이해
2. **설계 (Design)**: 데이터 흐름 설계
3. **구현 (Implementation)**: 의사코드 작성
4. **검증 (Validation)**: 예외 상황 처리

**평가 기준 (5차원):**
- 설계력 (Design): 0~25점
- 정합성 (Consistency): 0~25점 (데이터 누수 방지)
- 예외처리 (Edge Case): 0~20점
- 추상화 (Abstraction): 0~15점
- 구현력 (Implementation): 0~15점

**예시 문제:**
> "고객 이메일 목록에서 유효한 이메일만 추출하되, 악성 패턴을 필터링하고,
> 중복을 제거하고, 처리 과정을 로깅해야 한다. 의사코드를 작성하시오."

**LLM 평가:**
- 모델: **gpt-4o-mini**
- 온도: **0.2** (분석적)
- 평가 항목: 논리, 정합성, 예외 처리 품질

### 5.2 **Unit 2: Bug Hunt (디버깅)**

**목표:** 실무 버그 진단 & 수정 능력

**실습 케이스 (12가지):**

**데이터 관련:**
- Data Leakage (데이터 누수)
- Label Imbalance (라벨 불균형)
- Overfitting (과적합)

**코드 로직:**
- Off-by-one Error (범위 오류)
- Null Pointer Exception
- Type Mismatch (타입 불일치)

**ML 특화:**
- 잘못된 Metric 선택
- Feature 누락
- 하이퍼파라미터 오설정

**3단계 평가:**
1. **사고 방향**: 버그 원인을 정확히 지적했는가?
2. **코드 위험**: 수정 코드가 안전한가? (변경량, 조건문)
3. **사고 연속성**: 논리적 흐름과 근거가 충분한가?

### 5.3 **Unit 3: System Architecture (아키텍처)**

**목표:** 대규모 시스템 설계 & Trade-off 분석

**3가지 시나리오:**

1. **Image Feed (반려 식물 성장)**
   - 핵심: Low Latency, 확장성, 모니터링

2. **Real-time Chat (멘토링)**
   - 핵심: 대용량, 실시간성, 개인화

3. **Newsfeed (동아리 공지)**
   - 핵심: Feed 캐싱, 확장성, A/B Testing

**설계 프로세스:**

```
Step 1: 요구사항 이해
        ↓
Step 2: 드래그앤드롭으로 컴포넌트 배치
        (DB, Cache, Queue, API Gateway 등)
        ↓
Step 3: Mermaid 다이어그램으로 아키텍처 시각화
        ↓
Step 4: Deep Dive 면접 (설계 의도, 장애 대응)
        ↓
Step 5: AI 평가 (필수 요소, 설계 적절성)
```

**평가 항목:**
- 필수 컴포넌트 포함 여부
- 컴포넌트 간 연결 적절성
- 확장성 & 장애 허용성
- Trade-off 분석 깊이

---

## 6. 현재 구현 상태

### 6.1 완전 구현된 기능 ✅

#### 백엔드
- [x] Django REST API 기본 구조
- [x] 사용자 인증 & 세션 관리
- [x] **Unit 1 평가**: `pseudocode_evaluator.py` + `pseudocode_evaluation.py`
- [x] **Unit 2 평가**: `bughunt_evaluator.py`
- [x] **Unit 3 평가**: `architecture_evaluator.py` + `architecture_view.py`
- [x] 진행도 저장 & 조회
- [x] 리더보드 (상위 사용자)
- [x] **학습 분석 시스템** (Agent 1,2,3)
  - [x] 데이터 변환 (Adapter Pattern)
  - [x] 약점 프로필 생성
  - [x] 맞춤형 문제 생성
  - [x] 학습 리포트 작성

#### 프론트엔드
- [x] 홈페이지 & 랜딩 페이지 (게이미피케이션)
- [x] 의사코드 실습 UI (CodeMirror)
- [x] 버그헌트 실습 UI
- [x] 아키텍처 설계 UI (드래그앤드롭)
- [x] 실시간 평가 & 피드백
- [x] 진행률 표시
- [x] 사용자 기록 조회
- [x] 관리자 대시보드
- [x] **학습 분석 모달** ✨
- [x] **맞춤형 문제 풀이** ✨

### 6.2 개발 중인 기능 🔄

#### 아키텍처 리팩토링 (feat/sys-refactor)
- [x] `architecture_view.py` 생성 (백엔드 분리)
- [x] 프롬프트 생성 책임을 백엔드로 통일
- [x] Job Planner Agent 통합

#### 학습 분석 시스템
- [x] Phase 1: MVP (3-에이전트 파이프라인)
  - [x] 약점 프로필 분석
  - [x] 맞춤형 문제 생성
  - [x] 학습 리포트 작성
- [x] Phase 2: 결과 저장 (예정)
- [x] Navigation 추가 (홈페이지에서 접근 가능)

---

## 7. 진행 중인 리팩토링

### 7.1 아키텍처 시스템 백엔드 분리

**현재 문제:** LLM 호출이 프론트엔드에서 직접 수행
- 보안 위험 (API 키 노출)
- 프롬프트 관리 분산
- 캐싱 불가능

**해결 방안:**
```
Before (❌):
architectureRubricEvaluator.js (프론트엔드)
  → OpenAI API 직접 호출
  → 프롬프트 생성

After (✅):
architectureRubricEvaluator.js (프론트엔드)
  → POST /api/core/architecture/evaluate/
  → architecture_view.py (백엔드)
  → OpenAI API 호출
  → 프롬프트는 백엔드에서 관리
```

**진행 상태:**
- [x] `architecture_view.py` 생성
- [x] `ArchitectureEvaluationView` 구현
- [x] `ArchitectureQuestionGeneratorView` 구현
- [x] 프론트엔드 서비스 업데이트
- [x] 마이그레이션 완료 & 테스트

### 7.2 학습 분석 시스템 통합

**현재 상태:** Phase 1 MVP 완성
- [x] 데이터 변환 (Adapter Pattern)
- [x] 3-에이전트 파이프라인
- [x] 홈페이지 네비게이션 추가

**다음 단계 (Phase 2):**
- [ ] `AnalyticsSession` 테이블 추가
- [ ] 분석 결과 저장 (DB 캐싱)
- [ ] 재분석 시간 최적화
- [ ] 개선도 추적 (week-on-week)

---

## 8. 향후 개선 방향

### 8.1 즉시 개선 (1주)

```
Phase 2: 결과 저장 & 캐싱
├── [ ] AnalyticsSession 모델 추가
├── [ ] weakness_profile 저장
├── [ ] 재분석 시간 1초 이내로 단축
└── [ ] 분석 이력 조회

Phase 3: 세션별 분석
├── [ ] 일일/주간/월간 분석
├── [ ] 개선도 추적 (week-on-week)
└── [ ] 진행 추이 시각화
```

### 8.2 중기 개선 (1개월)

```
문제 풀이 결과 저장
├── [ ] CustomProblemSolver 답변 저장
├── [ ] 풀이 시간 기록
└── [ ] 문제별 채점 로직

자동 문제 생성 시스템
├── [ ] 3세션 완료 후 자동 생성 트리거
├── [ ] 배치 작업으로 야간 생성
└── [ ] 생성 결과 캐싱

고도화된 약점 분석
├── [ ] Clustering 기반 패턴 추출
├── [ ] 반복 실수 패턴 분류
└── [ ] 개념별 마스터리 레벨 계산
```

### 8.3 장기 개선 (3개월~)

```
엔드투엔드 학습 루프
├── [ ] 약점 분석
├── [ ] 맞춤형 문제 생성
├── [ ] 문제 풀이
├── [ ] 결과 저장
├── [ ] 재분석
└── [ ] 개선도 확인 (사이클)

인터랙티브 피드백 시스템
├── [ ] 실시간 hint 제공
├── [ ] 단계별 스캐폴딩
└── [ ] 적응형 난이도 조절

커뮤니티 & 경쟁 기능
├── [ ] 동료 비교 (안전한 방식)
├── [ ] 팀 기반 학습
└── [ ] 멘토링 연결
```

### 8.4 기술 부채 감소

```
코드 최적화
├── [ ] 컴포넌트 분할 (현재 LearningAnalyticsReport > 500줄)
├── [ ] API 응답 시간 개선 (현재 3~5초)
└── [ ] 캐싱 전략 수립

테스트 작성
├── [ ] Unit 테스트 (백엔드)
├── [ ] Component 테스트 (프론트엔드)
└── [ ] E2E 테스트

문서화
├── [ ] API 명세 (Swagger)
├── [ ] 데이터 스키마 설명서
└── [ ] 개발 가이드
```

---

## 9. 주요 고려사항

### 9.1 기술적 고려사항

#### LLM 활용

**현재 모델:**
- `gpt-4o-mini` (비용 효율적)
- 온도: 0.2 (분석), 0.5 (리포트), 0.7 (생성)

**향후 검토 항목:**
- [ ] 모델 비용 vs 품질 트레이드오프
- [ ] 응답 시간 최적화 (현재 3~5초)
- [ ] Fallback 모델 (로컬 분석)
- [ ] 응답 캐싱 (동일한 데이터에 대해)

#### 데이터 처리

**현재 방식:**
- 모든 세션 데이터를 매번 변환 (transform_to_score_history)
- 에이전트는 실시간 호출 (결과 저장 안 함)

**개선 방향:**
- [x] 변환된 데이터 캐싱
- [ ] 분석 결과 저장 (AnalyticsSession)
- [ ] 증분 업데이트 (새로운 데이터만 처리)

### 9.2 UX 고려사항

#### 학습 분석 페이지

**현재:**
- 약점 프로필 표시 (5초 대기)
- 리포트 표시
- 맞춤형 문제 생성 (클릭)
- 문제 풀이

**개선 방향:**
```
[ ] 진행률 애니메이션
[ ] 약점별 학습 경로 추천
[ ] 게이미피케이션 (배지, 마일스톤)
[ ] 진행 추이 차트
[ ] 모바일 반응형 디자인
```

#### 문제 풀이

**현재:**
- 3개 갈래 텍스트 입력
- 충족 기준 표시
- 함정 힌트

**개선 방향:**
```
[ ] 부분 점수 (갈래별 채점)
[ ] 자동 채점 피드백
[ ] 형식 검증 (마크다운, JSON 등)
[ ] 파일 업로드 지원
```

### 9.3 비즈니스 고려사항

#### 성장 지표

```
학습자:
[ ] 일일 활성 사용자 (DAU)
[ ] 평균 풀이 시간
[ ] 완료율
[ ] 재방문율

교육 효과:
[ ] 약점 개선도
[ ] 마스터리 달성률
[ ] 실무 전이 (취업률, 프로젝트 성공률)
```

#### 운영 비용

```
현재:
- LLM API 비용: ~$0.01/요청 (gpt-4o-mini)
- 일일 요청 수: ~1000개 추정
- 월 LLM 비용: ~$300

최적화:
[ ] 캐싱으로 LLM 호출 50% 감소
[ ] 로컬 분석 확대 (간단한 경우)
[ ] 배치 분석 (야간)
```

### 9.4 보안 고려사항

#### 현재 구현

```
✅ Django CSRF 보호
✅ 세션 기반 인증
✅ Axios 보안 헤더 설정
✅ HTTPS 준비 (docker-compose)
```

#### 개선 필요

```
[ ] API 레이트 리미팅
[ ] 사용자 입력 검증 강화
[ ] 감감 정보 마스킹 (로그)
[ ] 접근 제어 (관리자 전용 엔드포인트)
```

### 9.5 성능 고려사항

#### 응답 시간

```
현재:
GET /api/core/learning-analytics/report/
└─ 3~5초 (에이전트 호출)

개선 목표:
[ ] 1차 방문: 5초 이내 (캐싱 안 됨)
[ ] 2차 방문: 1초 이내 (DB 캐싱)
[ ] 계산: 100ms 이내 (로컬 분석)
```

#### 데이터베이스

```
현재:
- UserSolvedProblem 테이블에 모든 데이터 저장
- submitted_data는 JSON 필드 (인덱싱 어려움)

개선:
[ ] AnalyticsSession 테이블 추가 (정규화)
[ ] JSON 필드 인덱싱
[ ] 쿼리 최적화 (N+1 방지)
```

---

## 🔗 관련 문서

- **[LEARNING_ANALYTICS_SYSTEM.md](./LEARNING_ANALYTICS_SYSTEM.md)** - 학습 분석 시스템 상세 가이드
- **[enhancement.md](./enhancement.md)** - 고도화 방안 (3-에이전트 파이프라인)
- **[enhancement_guide.md](./enhancement_guide.md)** - Phase별 구현 로드맵
- **[submitted_data_recommendation.md](./submitted_data_recommendation.md)** - 데이터 포맷 권장사항

---

## 📈 진행 상황 요약

| 항목 | 상태 | 진행도 |
|------|------|--------|
| 기본 플랫폼 | ✅ 완성 | 100% |
| Unit 1 (의사코드) | ✅ 완성 | 100% |
| Unit 2 (버그헌트) | ✅ 완성 | 100% |
| Unit 3 (아키텍처) | ✅ 완성 | 100% |
| 학습 분석 (Phase 1) | ✅ 완성 | 100% |
| 아키텍처 리팩토링 | ✅ 완성 | 100% |
| 학습 분석 (Phase 2) | 🔄 진행 중 | 0% |
| 테스트 & 최적화 | 📋 계획 | 0% |

---

## 💡 높은 레벨의 개선 아이디어

### LLM 활용 고도화
```
[ ] Multi-turn 대화 (현재는 single-turn)
[ ] Fine-tuning (교육 도메인 특화)
[ ] 다국어 지원 (한글 → 영어 → 한글)
[ ] Prompt 버전 관리 & A/B 테스트
```

### 데이터 활용
```
[ ] 익명화된 분석 데이터 수집
[ ] 집단 약점 패턴 분석
[ ] 커리큘럼 최적화 (약한 부분 강화)
[ ] 맞춤형 학습 경로 추천
```

### 사용자 경험
```
[ ] 모바일 앱 (React Native)
[ ] 오프라인 모드
[ ] 실시간 협력 학습
[ ] VR/AR 시뮬레이션
```

### 비즈니스 확장
```
[ ] 기업 교육 (B2B)
[ ] 대학 커리큘럼 통합
[ ] 자격증 시험 대비
[ ] 라이선스 모델
```

---

**작성일:** 2026-02-20
**최종 업데이트:** feat/sys-refactor + 학습 분석 Phase 1 완성

이 문서는 여러 LLM과의 협업을 통해 고도화 방안을 구상할 수 있는 기초 자료입니다.
