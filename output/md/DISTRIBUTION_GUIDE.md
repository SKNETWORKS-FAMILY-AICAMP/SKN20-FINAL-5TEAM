# 수정일: 2026-01-20
# 수정내용: 팀원들에게 프로젝트를 배포하고 협업을 시작하기 위한 상세 가이드

# 📢 팀원 배포 및 협업 시작 가이드

현재 구축된 개발 환경을 팀원 6명에게 배포하고, 다 같이 개발을 시작하기 위한 절차입니다.

---

## 1. [팀장] 초기 배포 준비 (User)
팀장님(현재 사용자)은 로컬에 있는 코드를 원격 저장소(GitHub/GitLab)에 올려야 합니다.

### 1-1. Git 초기화 및 커밋
현재 폴더(`d:\SKN20-FINAL-5TEAM`)에서 터미널을 열고 순서대로 입력하세요.

```bash
# 1. Git 저장소 초기화
git init

# 2. 모든 파일 스테이지에 올리기 (.gitignore에 있는 파일은 자동 제외됨)
git add .

# 3. 첫 커밋 확정
git commit -m "Initial commit: Django + Vue + Docker environment via Antigravity"
```

### 1-2. GitHub 저장소 연결 및 업로드
1. **GitHub**에 로그인하여 `New Repository`를 클릭해 저장소를 만듭니다. (Public/Private 선택)
2. 생성된 저장소 주소(`https://github.com/.../repo.git`)를 복사합니다.
3. 터미널에서 아래 명령어로 업로드합니다.

```bash
# 원격 저장소 연결 (주소는 실제 주소로 변경 필요)
git remote add origin [GitHub_저장소_주소]

# 코드 업로드
git push -u origin main
```

---

## 2. [팀원] 개발 환경 세팅 가이드
팀원들에게는 **"이 파일 읽고 그대로 따라해!"**라고 아래 내용을 공유해주시면 됩니다.

### Step 1. 필수 프로그램 설치
1. **Git:** 소스 코드 다운로드용.
2. **Docker Desktop:** 개발 서버 실행용. (설치 후 반드시 실행 상태여야 함)
3. **VS Code:** 코드 편집기.
   - *주의: Python, Node.js, PostgreSQL은 따로 설치할 필요 없습니다! (Docker가 다 해줌)*

### Step 2. 소스 코드 받기
원하는 폴더에서 터미널(Git Bash 또는 PowerShell)을 열고 입력:

```bash
git clone [GitHub_저장소_주소]
cd [프로젝트_폴더명]
```

### Step 3. 서버 실행 (한 방에 끝내기)
**Docker Desktop이 켜진 상태**에서 다음 명령어 하나만 입력하세요.

```bash
docker-compose up --build
```
- 처음 실행 시 이미지를 다운로드하느라 5~10분 정도 걸릴 수 있습니다.
- 완료되면 터미널에 로그가 쭉 뜨면서 멈춥니다. (끄지 마세요!)

### Step 4. 접속 확인
- **프론트엔드 (화면):** [http://localhost:5173](http://localhost:5173)
- **백엔드 (API):** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **DB:** 자동으로 연결되어 있음.

---

## 3. 협업 시 주의사항 (필독)

### ⚠️ 내 담당 파일만 건드리기
- **A님:** `core/models/user_model.py`, `features/user/` 폴더
- **B님:** `core/models/product_model.py`, `features/product/` 폴더
- ... (각자 할당된 파일만 수정)
- 만약 `settings.py`나 `App.vue` 같은 공용 파일을 수정해야 하면 **반드시 단톡방에 공유**하세요.

### 🔄 매일 아침 업데이트 (Pull)
개발 시작 전에 남들이 수정한 코드를 받아오세요.
```bash
git pull origin main
```

### 💾 작업 내용 저장 및 공유 (Push)
```bash
git add .
git commit -m "작업내용: [기능명] 구현 완료"
git push origin main
```

---

## 4. 자주 묻는 질문 (FAQ)

**Q. "Port is already allocated" 에러가 떠요!**
A. 내 컴퓨터에 이미 PostgreSQL이나 다른 서버가 켜져 있는 겁니다. 작업 관리자에서 끄거나, 로컬 프로그램을 중지하세요.

**Q. `npm install` 해야 하나요?**
A. 아니요! `docker-compose up` 할 때 저희가 자동으로 되게 해놨습니다.

**Q. DB 테이블이 없다고 해요.**
A. 다음 명령어로 마이그레이션을 수동 실행해주세요.
```bash
docker-compose exec backend python manage.py migrate
```
