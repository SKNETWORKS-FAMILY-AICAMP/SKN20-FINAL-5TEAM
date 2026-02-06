# Docker 실행 가이드

이 문서는 프로젝트를 Docker 환경에서 실행하고 관리하는 방법을 설명합니다.

## 전제 조건 (Prerequisites)

*   [Docker](https://www.docker.com/products/docker-desktop/)가 설치되어 있어야 합니다.
*   [Docker Compose](https://docs.docker.com/compose/install/)가 설치되어 있어야 합니다 (Docker Desktop에 포함됨).

## 서비스 구조

이 프로젝트는 Docker Compose를 사용하여 다음 세 가지 서비스를 실행합니다:

1.  **db (PostgreSQL)**: 데이터베이스 서비스
    *   Host Port: `5433`
    *   Container Port: `5432`
    *   Database: `mygym`
    *   User: `myuser`
    *   Password: `mypassword`
2.  **backend (Django)**: 백엔드 API 서버
    *   Port: `8000`
    *   Build Context: `./backend`
    *   Command: `python manage.py runserver 0.0.0.0:8000`
3.  **frontend (Vue.js/Vite)**: 프론트엔드 개발 서버
    *   Port: `5173`
    *   Build Context: `./frontend`
    *   Command: `npm install && npm run dev`

## 실행 방법 (Usage)

### 1. 서비스 시작

백그라운드에서 모든 서비스를 시작하려면 다음 명령어를 실행하세요. 변경 사항이 있을 경우 이미지를 다시 빌드하기 위해 `--build` 옵션을 사용하는 것이 좋습니다.

```bash
docker-compose up -d --build
```

### 2. 로그 확인

실행 중인 컨테이너의 로그를 실시간으로 확인하려면:

```bash
docker-compose logs -f
```

특정 서비스의 로그만 확인하려면 (예: backend):

```bash
docker-compose logs -f backend
```

### 3. 접속 정보

서비스가 정상적으로 시작되면 다음 주소로 접속할 수 있습니다:

*   **Frontend**: [http://localhost:5173](http://localhost:5173)
*   **Backend API**: [http://localhost:8000](http://localhost:8000)
    *   Admin 페이지: [http://localhost:8000/admin](http://localhost:8000/admin) (superuser 생성 필요)

### 4. 서비스 중지

모든 서비스를 중지하고 컨테이너를 삭제하려면:

```bash
docker-compose down
```

데이터 볼륨까지 삭제하고 싶다면 (DB 데이터 초기화):

```bash
docker-compose down -v
```

## 주요 관리 명령 (Maintenance)

### Django 관리자(Superuser) 생성

백엔드 컨테이너 내부에서 명령어를 실행하여 관리자 계정을 생성합니다.

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 마이그레이션 적용 (Migrations)

DB 모델 변경 사항을 적용하려면:

```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### 새로운 패키지 설치 후

`requirements.txt` (Backend) 또는 `package.json` (Frontend)이 변경된 경우, 이미지를 다시 빌드해야 합니다.

```bash
docker-compose up -d --build
```
