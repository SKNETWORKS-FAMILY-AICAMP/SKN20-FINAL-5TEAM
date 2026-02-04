# 공통 데이터 공유 및 적재 가이드 (Data Sharing Guide)

팀원 간에 데이터베이스의 기초 데이터(공통 코드, 카테고리 등)를 동일하게 맞추기 위한 가이드입니다.
Django의 `dumpdata`와 `loaddata` 기능을 사용하여 데이터를 JSON 파일로 추출하고 공유합니다.

> **💡 참고**: 모든 명령어는 `backend` 컨테이너 내부에서 실행하거나, `docker-compose`를 통해 실행해야 합니다.

---

## 1. 데이터 추출하기 (작업자)

데이터를 생성한 팀원이 자신의 DB에서 데이터를 추출하여 파일로 만듭니다.

# Docker 환경에서 실행 시
docker-compose exec backend python -Xutf8 manage.py dumpdata core.Common --indent 4 > backend/core/fixtures/common_data.json

# (Windows Powershell에서 리다이렉션 이슈가 있을 경우, 컨테이너 접속 후 실행 권장)
# 1. 컨테이너 접속
docker-compose exec backend /bin/bash
# 2. 명령어 실행
python -Xutf8 manage.py dumpdata core.Common --indent 4 > core/fixtures/common_data.json
# 3. 종료
exit
```

### 1-2. `core` 앱 전체 데이터 추출하기
`core` 앱의 모든 모델 데이터를 추출합니다.
```bash
docker-compose exec backend python -Xutf8 manage.py dumpdata core --indent 4 > backend/core/fixtures/core_data.json
```

---

## 2. 데이터 공유하기 (Git)

1. 위에서 생성된 `json` 파일이 `backend/core/fixtures/` 경로에 있는지 확인합니다.
   - (폴더가 없다면 `backend/core/fixtures` 폴더를 생성하세요)
2. `git add`, `git commit`, `git push`를 통해 원격 저장소에 올립니다.

---

## 3. 데이터 적재하기 (다른 팀원)

다른 팀원은 `git pull`을 통해 최신 코드를 받은 후, 공유된 데이터 파일을 자신의 로컬 DB에 적재합니다.

### 3-1. 공통 데이터 적재 (Load)
```bash
docker-compose exec backend python manage.py loaddata core/fixtures/common_data.json
```

### 3-2. 전체 데이터 적재
```bash
docker-compose exec backend python manage.py loaddata core/fixtures/core_data.json
```

---

## 4. 자주 묻는 질문 (FAQ)

**Q. `loaddata`를 하면 기존 데이터는 어떻게 되나요?**
A. PK(기본키)가 같은 데이터는 덮어씌워지고, 없는 데이터는 새로 추가됩니다. PK가 다른데 논리적으로 중복된 데이터가 있다면 에러가 날 수 있으므로, 초기화된 DB에서 실행하는 것이 가장 안전합니다.

**Q. `UnicodeEncodeError` 등 인코딩 문제가 발생해요.**
A. `dumpdata` 명령어를 실행할 때 `-Xutf8` 옵션을 python 명령어 뒤에 붙여주세요. (예: `python -Xutf8 manage.py ...`)

**Q. FK(Foreign Key) 관련 에러가 발생해요.**
A. 데이터 간의 의존성이 있는 경우, 참조되는 데이터(부모 데이터)가 먼저 DB에 있어야 합니다. 필요한 경우 전체 데이터를 덤프받거나, 순서대로 로드해야 합니다.
