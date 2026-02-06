# Database Migration Guide

이 가이드는 프로젝트의 데이터베이스 마이그레이션(Migration) 절차를 설명합니다.
현재 Docker 환경에서 실행 중이므로 Docker 명령어를 사용하는 것을 권장합니다.

## 1. Docker 환경에서 실행 (권장)

백엔드 컨테이너가 실행 중이어야 합니다 (`docker-compose up -d` 상태).

### 1.1 마이그레이션 파일 생성 (Make Migrations)
모델(`models.py`)을 수정하거나 새로 만들었을 때 실행합니다. 변경 사항을 감지하여 마이그레이션 파일을 생성합니다.

```bash
docker-compose exec backend python manage.py makemigrations
```

특정 앱(예: `core`)에 대해서만 생성하려면:
```bash
docker-compose exec backend python manage.py makemigrations core
```

### 1.2 마이그레이션 적용 (Migrate)
생성된 마이그레이션 파일을 실제 데이터베이스에 반영합니다.

```bash
docker-compose exec backend python manage.py migrate
```

### 1.3 마이그레이션 상태 확인
어떤 마이그레이션이 적용되었는지 확인합니다.

```bash
docker-compose exec backend python manage.py showmigrations
```

---

## 2. 로컬 환경에서 실행 (선택 사항)
로컬에 Python과 필요한 라이브러리가 설치되어 있고, 가상환경이 활성화된 상태에서 가능합니다.

1. 백엔드 디렉토리로 이동
   ```bash
   cd backend
   ```

2. 명령어 실행
   ```bash
   # 마이그레이션 생성
   python manage.py makemigrations

   # 마이그레이션 적용
   python manage.py migrate
   ```

---

## 3. 자주 발생하는 문제 해결

### 마이그레이션 충돌 시 (Merge conflict)
여러 브랜치에서 작업하다가 마이그레이션 파일이 꼬였을 때:
1. 로컬의 `migrations` 폴더 안의 충돌나는 파일들을 확인합니다.
2. 문제가 되는 마이그레이션 파일을 삭제하거나 수정합니다 (주의 필요).
3. 다시 `makemigrations`를 시도합니다.

### 데이터베이스 초기화가 필요한 경우
모든 데이터를 지우고 처음부터 다시 시작하고 싶을 때:
```bash
# 데이터베이스 비우기 (주의: 모든 데이터 삭제됨)
docker-compose exec backend python manage.py flush --no-input

# 다시 마이그레이션 적용
docker-compose exec backend python manage.py migrate
```
