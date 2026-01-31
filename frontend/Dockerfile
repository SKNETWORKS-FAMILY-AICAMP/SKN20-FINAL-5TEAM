# 수정일: 2026-01-20
# 수정내용: Vue.js (Vite) 개발 환경을 위한 Dockerfile 작성

FROM node:20

WORKDIR /app

# npm install을 위해 package.json 복사 (최초 실행 시 필요)
# 소스 코드가 아직 없으면 에러가 날 수 있으므로 주의

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
