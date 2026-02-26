import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import socketio
from core.socket_server import sio

# [수정일: 2026-02-23] Django ASGI 설정 및 Socket.io 미들웨어 연동
# HTTP 요청은 Django가 처리하고, /socket.io/ 경로는 Socket.io 서버가 처리합니다.

django_app = get_asgi_application()
application = socketio.ASGIApp(sio, django_app)
