# 프로젝트 셋업 및 협업 가이드

**기술 스택:** Django REST Framework + Vue.js 3 + Vite + PostgreSQL + Docker

---

## 1. 프로젝트 구조

소스 코드 충돌을 방지하기 위해 도메인별로 파일을 분리합니다.

### 백엔드 (Django)
- **`backend/core/models/`**: 모델 파일을 기능별로 분할 (예: `user_model.py`, `practice_model.py`)
- **`backend/core/views/`**: 뷰 파일을 기능별 서브폴더로 분할 (예: `coach/`, `pseudocode/`, `bughunt/`)
- **`backend/config/`**: 전역 설정(settings.py) 및 메인 URL 관리

### 프론트엔드 (Vue.js)
- **`frontend/src/features/`**: 기능별 폴더 생성하여 작업 (예: `practice/`, `interview/`)
- **`frontend/src/App.vue`**: 기능별 컴포넌트를 조립하는 메인 레이아웃

### 모델 구조 규칙
- 모든 모델은 **`BaseModel`**을 상속하며 공통 필드를 자동으로 가짐:
  - `create_id`, `update_id` (생성/수정자 ID)
  - `create_date`, `update_date` (생성/수정 일시)
  - `use_yn` (사용 여부, 기본값 'Y')
- PK는 모든 모델에서 `id`로 통일 (예: `user.id`, `practice.id`)
- 연습 데이터 ID 규칙: 과정은 `unit01`, 상세 문제는 `unit01_01` (언더바 구분자)

---

## 2. 환경 설정

### 2.1 필수 프로그램 설치
1. **Git** — 소스 코드 관리
2. **Docker Desktop** — 개발 서버 실행 (설치 후 반드시 실행 상태)
3. **VS Code** — 코드 편집기
   - Python, Node.js, PostgreSQL은 따로 설치 불필요 (Docker가 처리)

### 2.2 소스 코드 받기
```bash
git clone [GitHub_저장소_주소]
cd [프로젝트_폴더명]
```

### 2.3 환경 변수 설정 (`.env`)

`backend/` 디렉토리 아래에 `.env` 파일을 생성합니다.

```env
# backend/.env

# Django 기본 설정
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True

# Database (Supabase IPv4 Pooler)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.bemlfemuypcejonmiyji
DB_PASSWORD=디스코드로 전달
DB_HOST=aws-1-ap-northeast-1.pooler.supabase.com
DB_PORT=5432

# AI API Keys (필요 시 입력)
OPENAI_API_KEY=
```

> **주의:** `DB_PASSWORD`는 보안상 Git에 올리지 않으며, 조장에게 전달받은 값을 사용합니다.

---

## 3. Docker 실행

### 3.1 서비스 구조

| 서비스 | 설명 | 포트 |
|--------|------|------|
| **db** (PostgreSQL) | 데이터베이스 | 5433 → 5432 |
| **backend** (Django) | API 서버 | 8000 |
| **frontend** (Vue.js/Vite) | 프론트엔드 개발 서버 | 5173 |

### 3.2 주요 명령어

```bash
# 서비스 시작 (이미지 빌드 포함)
docker-compose up -d --build

# 로그 확인 (전체 / 특정 서비스)
docker-compose logs -f
docker-compose logs -f backend

# 서비스 중지
docker-compose down

# DB 데이터까지 초기화하고 중지
docker-compose down -v
```

### 3.3 접속 확인

- **프론트엔드:** http://localhost:5173
- **백엔드 API:** http://localhost:8000
- **Swagger API 문서:** http://localhost:8000/api/docs/

### 3.4 주요 관리 명령

```bash
# Django 관리자 계정 생성
docker-compose exec backend python manage.py createsuperuser

# 마이그레이션 생성 및 적용
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# 퀘스트/연습 데이터 로드
docker-compose exec backend python manage.py loaddata practice_unit_data.json practice_detail_data.json
```

> `requirements.txt` 또는 `package.json` 변경 시 `docker-compose up -d --build`로 이미지를 재빌드합니다.

---

## 4. 외부 DB 툴 연결 (DBeaver)

DB 내부 데이터를 편하게 조회/수정하려면 DBeaver를 사용합니다.

1. **New Connection** → PostgreSQL 선택
2. **연결 설정:**
   - Host: `aws-1-ap-northeast-1.pooler.supabase.com`
   - Port: `5432` (안 될 경우 `6543`)
   - Database: `postgres`
   - User: `postgres.bemlfemuypcejonmiyji`
   - Password: 조장에게 전달받은 비밀번호
3. **스키마 위치:** `postgres > Schemas > public > Tables`

> **주의:** 공유 DB를 사용하므로 데이터 수정 시 모든 팀원에게 즉시 반영됩니다.

---

## 5. 협업 규칙

### 파일 관리
- 공통 파일(`settings.py`, `App.vue`, `__init__.py` 등)을 직접 수정할 때는 **반드시 팀에 공유**
- 각자 담당 폴더/파일 내에서 작업하고 `import`하는 방식 유지
- 수정 사항에는 상단에 수정일과 수정 내용 주석 포함
- CORS는 `CORS_ALLOW_ALL_ORIGINS = True`로 설정되어 있음

### Git 워크플로우
```bash
# 매일 아침 — 최신 코드 받기
git pull origin main

# 작업 완료 후 — 코드 공유
git add .
git commit -m "작업내용: [기능명] 구현 완료"
git push origin main
```

### 개발자별 작업 가이드

**백엔드 개발자:**
- `core/models/`에 `[기능]_model.py` 생성
- `core/views/`에 `[기능]_view.py` 생성 후 `__init__.py`에서 export
- `core/urls.py`에 라우터 등록

**프론트엔드 개발자:**
- `src/features/`에 기능 폴더 생성 (예: `login/`)
- `.vue` 컴포넌트 작성 후 `App.vue` 혹은 라우터에 등록

---

## 6. FAQ

**Q. "Port is already allocated" 에러가 떠요!**
A. 로컬에 이미 PostgreSQL이나 다른 서버가 켜져 있습니다. 작업 관리자에서 끄거나 로컬 프로그램을 중지하세요.

**Q. `npm install` 해야 하나요?**
A. 아니요! `docker-compose up` 할 때 자동으로 처리됩니다.

**Q. DB 테이블이 없다고 해요.**
A. `docker-compose exec backend python manage.py migrate`로 마이그레이션을 수동 실행하세요.

**Q. UnicodeEncodeError 인코딩 문제가 발생해요.**
A. `dumpdata` 명령어 실행 시 `-Xutf8` 옵션을 추가하세요. (예: `python -Xutf8 manage.py dumpdata ...`)
