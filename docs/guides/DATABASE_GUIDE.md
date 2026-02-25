# 데이터베이스 운영 가이드

모든 명령어는 `backend` 컨테이너 내부에서 실행하거나, `docker-compose`를 통해 실행합니다.

---

## 1. 마이그레이션 (Migration)

모델(`models.py`)을 수정하거나 새로 만들었을 때 사용합니다.

### 1.1 마이그레이션 파일 생성
```bash
docker-compose exec backend python manage.py makemigrations

# 특정 앱만 생성
docker-compose exec backend python manage.py makemigrations core
```

### 1.2 마이그레이션 적용
```bash
docker-compose exec backend python manage.py migrate
```

### 1.3 마이그레이션 상태 확인
```bash
docker-compose exec backend python manage.py showmigrations
```

### 1.4 로컬 환경에서 실행 (Docker 없이)
로컬에 Python과 가상환경이 설정되어 있는 경우:
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

---

## 2. 데이터 공유 (Fixtures)

팀원 간 기초 데이터(공통 코드, 카테고리 등)를 동일하게 맞추기 위해 Django의 `dumpdata`/`loaddata`를 사용합니다.

### 2.1 데이터 추출 (작업자)

```bash
# 특정 모델 데이터 추출
docker-compose exec backend python -Xutf8 manage.py dumpdata core.Common --indent 4 > backend/core/fixtures/common_data.json

# core 앱 전체 데이터 추출
docker-compose exec backend python -Xutf8 manage.py dumpdata core --indent 4 > backend/core/fixtures/core_data.json
```

> Windows PowerShell에서 리다이렉션 이슈가 있을 경우, 컨테이너에 직접 접속하여 실행합니다:
> ```bash
> docker-compose exec backend /bin/bash
> python -Xutf8 manage.py dumpdata core.Common --indent 4 > core/fixtures/common_data.json
> exit
> ```

### 2.2 데이터 공유 (Git)
1. JSON 파일이 `backend/core/fixtures/` 경로에 있는지 확인 (폴더 없으면 생성)
2. `git add` → `git commit` → `git push`로 원격 저장소에 업로드

### 2.3 데이터 적재 (다른 팀원)
`git pull` 후 공유된 데이터 파일을 로컬 DB에 적재합니다.

```bash
# 공통 데이터 적재
docker-compose exec backend python manage.py loaddata core/fixtures/common_data.json

# 전체 데이터 적재
docker-compose exec backend python manage.py loaddata core/fixtures/core_data.json
```

---

## 3. 데이터베이스 초기화

모든 데이터를 지우고 처음부터 다시 시작해야 할 때:

```bash
# 방법 1: flush (테이블 구조 유지, 데이터만 삭제)
docker-compose exec backend python manage.py flush --no-input
docker-compose exec backend python manage.py migrate

# 방법 2: 볼륨 삭제 (DB 완전 초기화)
docker-compose down -v
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
```

---

## 4. FAQ

**Q. `loaddata` 하면 기존 데이터는 어떻게 되나요?**
A. PK가 같은 데이터는 덮어씌워지고, 없는 데이터는 새로 추가됩니다. PK가 다른데 논리적으로 중복된 데이터가 있으면 에러가 날 수 있으므로, 초기화된 DB에서 실행하는 것이 안전합니다.

**Q. `UnicodeEncodeError` 인코딩 문제가 발생해요.**
A. `dumpdata` 명령어 실행 시 `-Xutf8` 옵션을 추가하세요. (예: `python -Xutf8 manage.py ...`)

**Q. FK(Foreign Key) 관련 에러가 발생해요.**
A. 참조되는 데이터(부모 데이터)가 먼저 DB에 있어야 합니다. 전체 데이터를 덤프받거나, 의존성 순서대로 로드하세요.

**Q. 마이그레이션 충돌이 발생했어요.**
A. `migrations/` 폴더에서 충돌나는 파일을 확인하고, 문제가 되는 파일을 삭제 또는 수정한 뒤 다시 `makemigrations`를 시도합니다.
