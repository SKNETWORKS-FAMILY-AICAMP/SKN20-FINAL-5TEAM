# Job Planner Agent - AI-ARCADE 통합 가이드

## 📋 개요
Job Planner Agent가 AI-ARCADE의 메인 페이지에 통합되었습니다.

## 🎯 통합된 기능
1. **메인 페이지 버튼**: Hero 섹션에 "Job Planner" 버튼 추가
2. **백엔드 API**: Django REST Framework 엔드포인트 생성
3. **프론트엔드 모달**: Vue 3 기반 채용공고 분석 UI

## 🔧 백엔드 구성

### API 엔드포인트
```
POST /api/core/job-planner/analyze/
POST /api/core/job-planner/quick-match/
```

### 파일 구조
```
backend/
  core/
    views/
      job_planner_view.py  # 메인 API 뷰
    urls.py                # URL 라우팅 설정
```

### 요청 형식 (analyze)
```json
{
  "user": {
    "name": "홍길동",
    "current_role": "주니어 개발자",
    "experience_years": 2,
    "skills": ["Python", "Django", "MySQL"],
    "skill_levels": {"Python": 4, "Django": 3},
    "career_goals": "백엔드 개발자",
    "available_prep_days": 30
  },
  "job": {
    "company_name": "테크 회사",
    "position": "백엔드 개발자",
    "required_skills": ["Python", "Django", "PostgreSQL"],
    "preferred_skills": ["Docker", "Kubernetes"],
    "experience_range": "2-4년",
    "job_description": "대규모 트래픽 처리"
  }
}
```

### 응답 형식
```json
{
  "readiness_score": 0.75,
  "skill_gap_score": 0.25,
  "experience_fit": 1.0,
  "matched_skills": [
    {
      "required": "Python",
      "user_skill": "Python",
      "similarity": 1.0
    }
  ],
  "missing_skills": [
    {
      "required": "PostgreSQL",
      "closest_match": "MySQL",
      "similarity": 0.62
    }
  ],
  "strategy": null  // OPENAI_API_KEY 설정 시 전략 추천
}
```

## 🎨 프론트엔드 구성

### 파일 구조
```
frontend/
  src/
    components/
      JobPlannerModal.vue      # Job Planner 모달 컴포넌트
      GlobalModals.vue         # 모달 통합 (업데이트됨)
    features/
      home/
        LandingView.vue        # 메인 페이지 (버튼 추가됨)
        LandingView.css        # 버튼 스타일 추가
    stores/
      ui.js                    # 모달 상태 관리 (업데이트됨)
    App.vue                    # 이벤트 핸들러 추가
```

### 사용 방법
1. 메인 페이지 Hero 섹션의 "Job Planner" 버튼 클릭
2. 모달에서 "내 프로필" 정보 입력
3. "채용공고" 정보 입력
4. "분석 시작" 버튼 클릭
5. "분석 결과" 탭에서 결과 확인

## 🚀 실행 방법

### 1. Job Planner 의존성 설치
```bash
cd job-planner-agent
pip install -r requirements.txt
```

필수 패키지:
- sentence-transformers>=2.2.0
- torch>=2.0.0
- openai>=1.0.0 (선택적, 전략 추천용)

### 2. 환경변수 설정 (선택적)
```bash
# LLM 기반 전략 추천을 사용하려면
export OPENAI_API_KEY=your-api-key-here
```

### 3. Django 서버 실행
```bash
cd backend
python manage.py runserver
```

### 4. Vue 개발 서버 실행
```bash
cd frontend
npm run dev
```

### 5. 브라우저에서 확인
```
http://localhost:5173  # 또는 Vue 개발 서버 포트
```

## 📊 기능 상세

### 스킬 매칭
- **Sentence Transformers** 사용
- 다국어 지원 (paraphrase-multilingual-MiniLM-L12-v2)
- 유사도 임계값: 0.65 (config.py에서 조정 가능)

### 점수 계산
- **Readiness Score**: 준비도 (0.0 ~ 1.0)
- **Skill Gap Score**: 스킬 갭 (0.0 ~ 1.0)
- **Experience Fit**: 경력 적합도 (0.0 ~ 1.0)

### AI 전략 추천 (선택적)
- OpenAI API 키가 설정된 경우에만 활성화
- GPT-4o-mini 모델 사용
- 맞춤형 학습 전략 및 우선순위 추천

## 🎨 UI 특징

### 디자인 테마
- Dark mode gradient background
- Glassmorphism 효과
- 실시간 점수 시각화
- 색상 코딩:
  - 🟢 Excellent: 80% 이상
  - 🔵 Good: 60-80%
  - 🟠 Fair: 40-60%
  - 🔴 Poor: 40% 미만

### 탭 구조
1. **공고 입력**: 사용자 프로필 + 채용공고 입력
2. **분석 결과**: 점수 overview + 매칭/부족 스킬 + AI 전략

## 🔍 트러블슈팅

### 모듈을 찾을 수 없음
```
ImportError: No module named 'sentence_transformers'
```
→ `pip install -r job-planner-agent/requirements.txt` 실행

### API 500 에러
```
Job Planner 모듈이 설치되지 않았습니다.
```
→ job-planner-agent 경로 확인 및 의존성 설치

### 전략 추천이 null
→ OPENAI_API_KEY 환경변수 설정 필요 (선택적 기능)

## 📝 향후 개선 사항
- [ ] 채용공고 URL 크롤링 기능 추가
- [ ] 학습 계획 시각화 (타임라인)
- [ ] 사용자 히스토리 저장 기능
- [ ] PDF 이력서 업로드 및 파싱
- [ ] 공고 북마크 및 비교 기능

## 👥 개발자
- Backend: Django REST Framework + Job Planner Engine
- Frontend: Vue 3 Composition API + Tailwind-like CSS
- AI: Sentence Transformers + OpenAI GPT-4o-mini
