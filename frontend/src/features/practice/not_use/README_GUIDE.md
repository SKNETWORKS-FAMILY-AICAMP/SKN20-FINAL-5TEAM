# 수정일: 2026-01-20
# 수정내용: 구현된 프로젝트 구조 및 실행 가이드 문서화

# 프로젝트 구성 및 실행 가이드 (Django + Vue.js + PostgreSQL)

이 문서는 6명의 팀원이 협업하기 위해 구축된 파일 분리 기반의 개발 환경 사용법을 설명합니다.

---

## 1. 프로젝트 구조 (파일 분리 전략)

소스 코드 충돌을 방지하기 위해 각 도메인별로 파일을 엄격히 분리했습니다.

### 백엔드 (Django)
- **`backend/core/models/`**: 모델 파일을 기능별로 분할하여 관리합니다 (예: `sample_model.py`).
- **`backend/core/views/`**: 뷰셋 파일을 기능별로 분할하여 관리합니다 (예: `sample_view.py`).
- **`backend/config/`**: 전역 설정 및 메인 URL 관리를 담당합니다.

### 프론트엔드 (Vue.js)
- **`frontend/src/features/`**: 각 개발자가 담당하는 기능별로 폴더를 생성하여 작업합니다 (예: `sample/SampleFeature.vue`).
- **`frontend/src/App.vue`**: 각 기능별 컴포넌트를 조립하는 메인 레이아웃입니다.

---

## 2. 주요 환경 정보
- **Backend:** Django Rest Framework (Port: 8000)
- **Frontend:** Vue.js 3 + Vite (Port: 5173)
- **Database:** PostgreSQL (Port: 5432)
- **API UI (Swagger):** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

---

## 3. 실행 방법 (Docker 사용)

### 최초 실행 및 빌드
```bash
docker-compose up --build
```

### 서비스 중지
```bash
docker-compose down
```

---

## 4. 협업 준수 사항
1. **파일 개별 생성:** 공통 파일(`settings.py`, `App.vue` 등)을 직접 수정하기보다는 각자의 폴더/파일을 새로 생성하여 `import` 하는 방식을 유지하세요.
2. **주석 필수:** 모든 수정 사항에는 상단에 수정일과 수정 내용을 포함한 주석을 달아주세요.
3. **CORS:** 프론트엔드 연동을 위해 백엔드에서 `CORS_ALLOW_ALL_ORIGINS = True`로 설정되어 있습니다.

---

## 5. 담당자별 작업 예시

### 백엔드 개발자
- `core/models/` 폴더에 `[기능]_model.py` 생성
- `core/views/` 폴더에 `[기능]_view.py` 생성 후 `__init__.py`에서 export
- `core/urls.py`에 라우터 등록

### 프론트엔드 개발자
- `src/features/` 폴더에 본인의 기능 폴더 생성 (예: `login/`)
- `.vue` 컴포넌트 작성 후 `App.vue` 혹은 라우터에 등록
