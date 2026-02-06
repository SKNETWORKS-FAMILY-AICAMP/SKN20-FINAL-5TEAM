# AI-GYM 프로젝트 통합 개발 가이드

이 문서는 프로젝트의 핵심 설정, 협업 규칙, 실행 방법을 하나로 통합한 가이드입니다.

---

## 1. 🚀 빠른 시작 (Quick Start)

### 필수 프로그램
- **Git**, **Docker Desktop**, **VS Code** (Python/Node 등은 Docker가 관리하므로 설치 불필요)

### 환경 설정 (`.env`)
`backend/.env` 파일을 생성하고 아래 내용을 입력합니다 (비밀번호는 조장에게 확인).
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.bemlfemuypcejonmiyji
DB_PASSWORD=전달받은_비밀번호
DB_HOST=aws-1-ap-northeast-1.pooler.supabase.com
DB_PORT=5432
```

### 실행 및 초기화
```bash
# 1. 서비스 빌드 및 실행
docker-compose up -d --build

# 2. DB 마이그레이션 적용
docker-compose exec backend python manage.py migrate

# 3. 기초 데이터 로드
docker-compose exec backend python manage.py loaddata practice_unit_data.json practice_detail_data.json
```

---

## 2. 🤝 협업 준수 사항

### 파일 분리 및 모듈화 전략 (충돌 방지)
- **백엔드**: `backend/core/models/`, `views/` 폴더 내에 `[기능]_model.py`, `[기능]_view.py` 형태로 분리 생성합니다.
- **프론트엔드**: `frontend/src/features/` 폴더 내에 기능 폴더를 생성합니다.
  - **패턴 예시 (최신)**: `src/features/practice/pseudocode/` 처럼 특정 도메인별로 파일을 한데 모아 관리합니다.
- **공통 파일 수정 금지**: `App.vue`, `settings.py`, 메인 `urls.py` 등은 수정 전 팀원에게 반드시 공유하세요.

### 코드 및 DB 규칙
- **PK 명칭 통일**: 모든 모델의 고유 ID는 `id`로 통일합니다. (예: `user_id`, `board_id` 사용 지양 → `id` 사용)
- **주석 필드**: 모든 수정 사항에는 상단에 수정일과 내용을 포함한 주석을 답니다.
- **Git 관리**: `not_use` 폴더 등 임시/레거시 폴더는 `.gitignore`에 등록되어 관리 대상에서 제외되니, 파일 삭제보다 이동/무시를 권장합니다.

---

## 3. 🛠 주요 관리 명령어

| 기능 | 명령어 |
| :--- | :--- |
| **모델 변경 반영** | `docker-compose exec backend python manage.py makemigrations` |
| **DB 반영** | `docker-compose exec backend python manage.py migrate` |
| **슈퍼유저 생성** | `docker-compose exec backend python manage.py createsuperuser` |
| **데이터 추출(Dump)** | `docker-compose exec backend python -Xutf8 manage.py dumpdata [앱명] --indent 4 > [파일명].json` |
| **데이터 적재(Load)** | `docker-compose exec backend python manage.py loaddata [파일명].json` |

### 3-1. 모델(Model) 수정 표준 절차

**A. 수정자(Modifier) 프로세스**
1.  **최신화**: `git pull origin main`으로 최신 코드 확보
2.  **수정**: `models.py` 수정 후 상단에 **수정일/내용 주석** 작성
3.  **생성**: `docker-compose exec backend python manage.py makemigrations`
4.  **반영**: `docker-compose exec backend python manage.py migrate`
5.  **커밋**: 생성된 마이그레이션 파일(`#.py`)을 포함하여 `git push`

**B. 팀원(Collaborator) 프로세스**
1.  **동기화**: `git pull origin main`으로 마이그레이션 파일 수신
2.  **반영**: `docker-compose exec backend python manage.py migrate` 실행 (필수!)

> [!CAUTION]
> 마이그레이션 파일은 팀 간의 DB 상태를 맞추는 중요한 지표입니다. 절대 임의로 삭제하지 마세요.

---

## 4. 🌐 접속 정보
- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Swagger Docs**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

---
**[최종 업데이트: 2026-02-06]**
