# 🌐 Localtunnel 멀티플레이어 접속 가이드

## 개요
localtunnel을 사용하여 같은 네트워크가 아닌 외부 사용자도 Socket.io 게임에 동시 접속할 수 있게 합니다.

---

## 사전 준비

```bash
# localtunnel 글로벌 설치 (한 번만)
npm install -g localtunnel
```

---

## 실행 순서 (터미널 4개 필요)

### 터미널 1: 백엔드 서버 실행
```bash
cd backend
uvicorn config.asgi:application --host 0.0.0.0 --port 8000
```

### 터미널 2: 백엔드 터널 열기
```bash
lt --port 8000 --subdomain coduck-backend
```
> 결과: `https://coduck-backend.loca.lt` (subdomain이 이미 사용중이면 다른 이름 사용)
> 
> ⚠️ localtunnel 첫 접속 시 "Friendly Reminder" 페이지가 뜹니다.
> "Click to Continue" 버튼을 눌러야 합니다.

### 터미널 3: 프론트엔드 서버 실행 (tunnel 모드)
```bash
cd frontend
npx vite --mode tunnel
```
> `--mode tunnel`을 사용하면 `.env.tunnel`의 환경변수가 자동 로딩됩니다.

### 터미널 4: 프론트엔드 터널 열기
```bash
lt --port 5173 --subdomain coduck-wars
```
> 결과: `https://coduck-wars.loca.lt`

---

## .env.tunnel 설정

`frontend/.env.tunnel` 파일에서 백엔드 터널 URL을 맞춰주세요:

```env
VITE_API_BASE_URL=https://coduck-backend.loca.lt/api/core
VITE_SOCKET_URL=https://coduck-backend.loca.lt
```

> subdomain을 변경했다면 여기도 맞춰서 수정!

---

## 접속 방법

1. **모든 플레이어**가 `https://coduck-wars.loca.lt`로 접속
2. localtunnel "Friendly Reminder" 페이지에서 **Continue** 클릭
3. 게임 로비에서 같은 방에 입장하면 Socket.io로 실시간 동기화!

---

## 주의사항

### localtunnel이 불안정할 때 (자주 끊김)
**ngrok 사용 추천** (무료 플랜으로 충분):

```bash
# ngrok 설치 후
ngrok http 8000   # 백엔드
ngrok http 5173   # 프론트엔드 (별도 터미널)
```

ngrok은 더 안정적이며, 발급된 URL을 `.env.tunnel`에 넣으면 됩니다:
```env
VITE_API_BASE_URL=https://abc123.ngrok-free.app/api/core
VITE_SOCKET_URL=https://abc123.ngrok-free.app
```

### WebSocket 연결이 안 될 때
- 브라우저 콘솔에서 소켓 연결 URL 확인
- `transports: ['polling', 'websocket']`이 이미 설정되어 있으므로 polling fallback 가능
- localtunnel은 WebSocket을 지원하지만 간헐적으로 끊길 수 있음

### CORS 에러가 날 때
백엔드 `socket_server.py`의 `cors_allowed_origins='*'`가 이미 모든 도메인을 허용하고 있으므로 정상적으로 동작해야 합니다.

---

## 빠른 테스트 (혼자서 2개 브라우저)

1. 위 4개 터미널을 모두 실행
2. **Chrome 브라우저**: `https://coduck-wars.loca.lt` 접속
3. **시크릿 모드 또는 다른 브라우저**: 같은 URL 접속
4. 둘 다 같은 미션 방에 입장 → 실시간 동기화 확인!
