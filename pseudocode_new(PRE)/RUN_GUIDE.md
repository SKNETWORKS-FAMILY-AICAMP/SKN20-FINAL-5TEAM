# 프로젝트 실행 가이드 (Running Guide)

이 문서는 프로젝트를 로컬 환경에서 설치하고 실행하는 방법을 설명합니다.

## 사전 요구 사항 (Prerequisites)

이 프로젝트를 실행하기 위해서는 컴퓨터에 **Node.js**가 설치되어 있어야 합니다.
설치되어 있지 않다면 [Node.js 공식 웹사이트](https://nodejs.org/)에서 LTS 버전을 다운로드하여 설치해주세요.

## 설치 및 실행 방법

### 1. 프로젝트 폴더로 이동
터미널(또는 명령 프롬프트/PowerShell)을 열고 프로젝트 폴더(`pseudocode_new`)로 이동합니다.

```bash
cd d:\skn_project\SKN20-FINAL-5TEAM\pseudocode_new
```

### 2. 의존성 패키지 설치
프로젝트 실행에 필요한 라이브러리들을 설치합니다.

```bash
npm install
```

### 3. 개발 서버 실행
설치가 완료되면 개발 서버를 실행합니다.

```bash
npm run dev
```

### 4. 웹 브라우저 확인
터미널에 표시된 로컬 주소(보통 `http://localhost:5173`)를 브라우저 주소창에 입력하여 접속합니다.
(Ctrl 키를 누른 채 링크를 클릭하면 바로 열립니다.)

---

## 기타 명령어

- **프로덕션 빌드 (Build):** 배포용 파일을 생성합니다.
  ```bash
  npm run build
  ```

- **미리보기 (Preview):** 빌드된 결과물을 로컬에서 미리 확인합니다.
  ```bash
  npm run preview
  ```

- **린트 (Lint):** 코드 스타일 및 에러를 검사합니다.
  ```bash
  npm run lint
  ```
