# 모델(Models) 수정 가이드

이 문서는 Django 프로젝트에서 `models.py` 파일을 수정할 때 지켜야 할 표준 절차를 안내합니다. 마이그레이션 충돌을 방지하고 팀원 간의 원활한 코드 통합을 위해 아래 절차를 반드시 준수해 주세요.

## 1. 수정자(Modifier) 절차

모델을 직접 수정하고 데이터베이스 구조를 변경하는 사람이 수행해야 할 단계입니다.

### 1단계: 최신 코드 확보
작업을 시작하기 전, `main` 브랜치나 최신 개발 브랜치의 최신 코드를 반드시 가져옵니다.
```bash
git pull origin main
```

### 2단계: 모델 수정 및 주석 작성
`models.py` 파일을 수정합니다. **반드시 수정 날짜와 내용을 주석으로 남겨주세요.**
```python
# 2026-01-22: [수정 내용 요약] - 작성자명
class MyModel(models.Model):
    ...
```

### 3단계: 마이그레이션 파일 생성 (Makemigrations)
Docker 환경에서 변경 사항을 감지하여 마이그레이션 파일을 생성합니다.
```bash
docker-compose exec backend python manage.py makemigrations
```

### 4단계: 데이터베이스 반영 및 테스트 (Migrate)
생성된 마이그레이션을 로컬 DB에 반영하고 기능이 정상적으로 작동하는지 확인합니다.
```bash
docker-compose exec backend python manage.py migrate
```

### 5단계: 코드 커밋 및 푸시
생성된 마이그레이션 파일(`backend/apps/*/migrations/*.py`)을 **반드시 포함**하여 커밋합니다.
```bash
git add .
git commit -m "2026-01-22: [모델 수정] MyModel 클래스에 필드 추가"
git push origin <your-branch>
```

---

## 2. 팀원(Collaborators) 절차

다른 팀원이 모델 수정을 완료하여 리포지토리에 푸시했을 때 수행해야 할 단계입니다.

### 1단계: 최신 코드 Pull
팀원이 올린 최신 코드를 로컬로 가져옵니다.
```bash
git pull origin main
```

### 2단계: 데이터베이스 마이그레이션 실행
팀원이 생성한 마이그레이션 파일을 자신의 로컬 데이터베이스에 반영합니다. **이 단계를 누락하면 서비스 실행 시 에러가 발생할 수 있습니다.**
```bash
docker-compose exec backend python manage.py migrate
```

### 3단계: 정상 작동 확인
서버를 실행하여 모델 변경 사항이 정상적으로 반영되었는지 확인합니다.

---

## 3. 주의 사항 (Common Pitfalls)

- **Migration 파일 삭제 금지**: 이미 푸시된 마이그레이션 파일은 절대 임의로 삭제하지 마세요. 충돌이 발생하면 팀 내 논의 후 처리합니다.
- **Docker 사용 권장**: 로컬 환경 설정 차이로 인한 오류를 방지하기 위해 가급적 Docker 명령어를 사용하여 마이그레이션을 수행하세요.
- **주석 준수**: 수정 사항 추적을 위해 파일 상단 또는 변경 지점에 날짜를 포함한 주석을 반드시 작성해 주세요.
