#!/bin/bash
# ============================================================
# Localtunnel로 팀 대전 게임 외부 접속 설정
# 사용법: bash start-tunnel.sh
# ============================================================
#
# 사전 준비:
#   npm install -g localtunnel
#
# subdomain은 다른 사람이 이미 사용 중이면 변경 필요
# 원하는 이름으로 바꿔도 됩니다
BACKEND_SUBDOMAIN="coduck-backend"
FRONTEND_SUBDOMAIN="coduck-frontend"

BACKEND_URL="https://${BACKEND_SUBDOMAIN}.loca.lt"
FRONTEND_URL="https://${FRONTEND_SUBDOMAIN}.loca.lt"

echo "============================================"
echo "  Coduck Wars - Localtunnel 시작"
echo "============================================"
echo ""
echo "Backend URL:  ${BACKEND_URL}"
echo "Frontend URL: ${FRONTEND_URL}"
echo ""
echo "팀원에게 Frontend URL을 공유하세요!"
echo ""
echo "[주의] 팀원이 처음 접속하면 localtunnel 확인 페이지가 뜹니다."
echo "       자신의 공인 IP를 입력하면 됩니다. (https://whatismyip.com)"
echo ""
echo "============================================"
echo ""

# .env에 터널 URL 설정 (Django가 읽을 수 있도록)
export TUNNEL_FRONTEND_URL="${FRONTEND_URL}"
export TUNNEL_BACKEND_URL="${BACKEND_URL}"

# 백엔드 터널 시작 (백그라운드)
echo "[1/2] 백엔드 터널 시작 (port 8000)..."
lt --port 8000 --subdomain ${BACKEND_SUBDOMAIN} &
LT_BACKEND_PID=$!

# 프론트엔드 터널 시작 (백그라운드)
echo "[2/2] 프론트엔드 터널 시작 (port 5173)..."
lt --port 5173 --subdomain ${FRONTEND_SUBDOMAIN} &
LT_FRONTEND_PID=$!

echo ""
echo "터널이 실행 중입니다. Ctrl+C로 종료하세요."
echo ""

# Ctrl+C로 종료 시 두 프로세스 모두 종료
trap "echo '터널 종료 중...'; kill $LT_BACKEND_PID $LT_FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

wait
