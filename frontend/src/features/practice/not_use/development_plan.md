# 개발 환경 구축 및 협업 플랜 (Django + Vue.js + PostgreSQL)

이 문서는 6명의 개발자가 Django, Vue.js, PostgreSQL을 사용하여 충돌 없이 효율적으로 협업하기 위한 개발 환경 구성 계획을 담고 있습니다.

## 1. 기술 스택 요약
- **Backend:** Django (Django REST Framework)
- **Frontend:** Vue.js 3 (Vite, Pinia/Vuex)
- **Database:** PostgreSQL
- **Infrastructure:** Docker, Docker Compose
- **Version Control:** Git (GitHub/GitLab)

---

## 2. 프로젝트 구조 (Monorepo 권장)
프론트엔드와 백엔드를 하나의 저장소에서 관리하여 API 명세 변경 등에 유연하게 대응합니다.

```text
/
├── .github/              # PR 템플릿, CI/CD 워크플로우
├── backend/              # Django 프로젝트 폴더
│   ├── manage.py
│   ├── requirements.txt
│   └── ...
├── frontend/             # Vue.js 프로젝트 폴더
│   ├── package.json
│   ├── src/
│   └── ...
├── docker-compose.yml    # 전체 서비스 오케스트레이션
├── .gitignore
└── README.md
```

---

## 3. 파일 분리(모듈화) 중심의 협업 전략

브랜치 전환의 복잡함을 줄이고, 작업 영역을 물리적으로 나누어 코드 충돌을 원천 차단하는 방식입니다.

### 3.1 Django (Backend) 모듈화 전략
하나의 `views.py`나 `models.py`에 코드를 몰아넣지 않고, 기능별로 파일을 쪼개서 `import` 하는 방식을 사용합니다.

- **App 단위 분리:** `users`, `posts`, `payments` 등 도메인별로 Django App을 생성합니다.
- **파일 디렉토리화:** 
  - `views.py` → `views/` 폴더 내에 `login_view.py`, `profile_view.py` 등으로 분리.
  - `models.py` → `models/` 폴더 내에 `user_model.py`, `order_model.py` 등으로 분리.
- **URL 분리:** 각 App마다 `urls.py`를 두고 메인 `urls.py`에서 `include()`하여 관리합니다.

### 3.2 Vue.js (Frontend) 컴포넌트 분리 전략
Vue의 장점인 컴포넌트 기반 아키텍처를 극대화합니다.

- **Feature 위주 폴더 구성:** `src/features/login/`, `src/features/dashboard/` 등 작업자별로 폴더를 엄격히 분리합니다.
- **Atomic Design:** 공통 UI(버튼, 입력창 등)만 공통 폴더(`src/components/common`)에 두고, 나머지 로직은 각자의 폴더에서 독립적으로 작성합니다.
- **라우터 자동화:** 라우터 설정을 하나의 파일에 다 적지 않고, 각 모듈에서 정의한 라우터를 가져와서 합치는 방식을 사용합니다.

### 3.3 충돌 방지 핵심 규칙
1. **Shared File(공공 파일) 수정 예고:** `settings.py`, `App.vue`, 메인 `urls.py` 등 공통으로 사용하는 파일을 수정할 때는 반드시 팀원들에게 미리 알립니다.
2. **독립적 DB 마이그레이션:** 데이터베이스 모델 수정 시, 서로 다른 파일을 수정하게 하여 마이그레이션 충돌을 방지합니다.
3. **Index 관리:** 각 폴더의 `__init__.py`나 `index.js`에서 각자 만든 파일을 `export`/`import` 하도록 설정하여 외부 접근 경로를 단일화합니다.

---

## 4. 환경 일관성을 위한 Docker 구성
6명의 개발 환경(Windows, Mac 등)이 달라도 동일하게 동작하도록 Docker를 사용합니다.

- **db 서비스:** PostgreSQL 공식 이미지 사용.
- **backend 서비스:** Python 이미지 기반, Django 실행.
- **frontend 서비스:** Node 이미지 기반, Vue 개발 서버 실행.

---

## 5. 코드 스타일 통일 (Auto-formatting)
서로 다른 코딩 스타일로 인한 불필요한 Git 충돌을 방지합니다.

- **Python (Backend):** `Black` 또는 `Flake8` 사용.
- **JavaScript/Vue (Frontend):** `ESLint` 및 `Prettier` 사용.
- **Pre-commit Hook:** 커밋 전 자동으로 포맷팅을 확인하도록 설정합니다.

---

## 6. 단계별 구축 계획 (Plan)

### [Phase 1] 기초 인프라 구축 (1~2일차)
- GitHub 저장소 생성 및 초기 세팅.
- Docker Compose 설정 (DB, Backend, Frontend 깡통 세팅).
- DB 스키마 설계 및 기초 마이그레이션.

### [Phase 2] 프레임워크 초기화 및 API 규격 정의 (3~4일차)
- Django REST Framework (DRF) 설정.
- Vue.js 초기 프로젝트 생성 및 Axios 연동.
- Swagger(drf-spectacular 등)를 이용한 API 문서화 자동화 (프론트-백엔드 소통 원활화).

### [Phase 3] 기능 개발 시작 (5일차~)
- 정의된 브랜치 전략에 따라 각자 기능 개발.
- 주기적인 코드 리뷰 및 `develop` 통합.

---

## 7. 주석 규칙 (User Custom Rule 반영)
모든 수정 사항에는 다음과 같은 형식으로 주석을 추가합니다.
```python
# 수정일: 2026-01-20
# 수정내용: [기능명] 작업 완료
```
