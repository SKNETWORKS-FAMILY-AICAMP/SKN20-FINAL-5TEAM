# AI-GYM 프로젝트 팀 셋팅 가이드 (공유 DB 버전)

모든 조원이 동일한 데이터베이스(Supabase)를 공유하여 실시간으로 데이터를 동기화하며 개발하기 위한 가이드입니다.

## 1. 환경 변수 설정 (`.env`)

`backend/` 디렉토리 아래에 `.env` 파일을 생성하고 아래 내용을 복사하여 넣으세요.  
(이미 파일이 있다면 내용을 수정하세요.)

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

> [!IMPORTANT]
> `DB_PASSWORD`는 보안상 Git에 올리지 않으며, 조장님께 전달받은 값을 사용하세요.

---

## 2. 프로젝트 실행 (Docker)

터미널(PowerShell 또는 Bash)에서 프로젝트 루트 폴더로 이동한 후 아래 명령어를 실행합니다.

```bash
# 1. 설정 반영 및 컨테이너 재시작
docker compose up -d --build

# 2. (선택사항) 서버 로그 확인
docker compose logs -f backend
```

---

## 3. 데이터베이스 동기화 (최초 1회만 권장)

이미 조장님이 테이블 생성과 기초 데이터 업로드를 완료했습니다. 하지만 본인의 로컬 환경에서 DB 연결 상태를 확인하고 싶다면 아래 명령어를 수행해 보세요.

```bash
# 테이블 마이그레이션 확인
docker compose exec backend python manage.py migrate

# 퀘스트/연습 데이터 로드 (최신 unit01_01 패턴 적용본)
docker compose exec backend python manage.py loaddata practice_unit_data.json practice_detail_data.json
```

---

## 4. 주의 사항

1. **ID 규칙 준수**: 연습 과정은 `unit01`, 상세 문제는 `unit01_01`과 같이 언더바(_) 구분자 패턴을 사용합니다. 새로운 데이터를 추가할 때 이 규칙을 꼭 지켜주세요.
2. **CORS 설정**: 프론트엔드는 기본적으로 `http://localhost:5173`에서 실행되어야 백엔드와 정상적으로 통신됩니다.
3. **DB 공유**: 내가 DB에서 데이터를 수정하면 모든 팀원에게 즉시 반영되므로, 중요한 데이터를 삭제할 때는 주의하세요!

---

## 5. 외부 DB 툴 연결 (DBeaver 등)

DB 내부 데이터를 엑셀처럼 편하게 보고 수정하고 싶다면 DBeaver 설치를 권장합니다.

1. **New Connection**: PostgreSQL 선택
2. **Main 설정**:
   - **Host**: `aws-1-ap-northeast-1.pooler.supabase.com`
   - **Port**: `5432` (안 될 경우 `6543`)
   - **Database**: `postgres`
   - **User**: `postgres.bemlfemuypcejonmiyji`
   - **Password**: 조장님께 받은 비밀번호
3. **스키마 위치**: `postgres > Schemas > public > Tables`에서 확인 가능합니다.

---

**즐거운 개발 되세요! 🚀✨**
