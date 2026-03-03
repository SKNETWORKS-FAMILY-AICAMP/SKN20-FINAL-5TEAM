# 수정일: 2026-01-20
# 수정내용: 메인 URL 설정 및 Swagger UI 접속 경로 추가

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # [수정: 2026-02-26] core.urls가 아닌 core.views.urls로 변경하여 ModuleNotFoundError 해결
    path('api/core/', include('core.views.urls')),
]

# [수정일: 2026-02-27] 미디어 파일 서빙 설정 (DEBUG 모드 상관없이 서빙 - Nginx 설정이 없는 터널 환경 지원)
from django.urls import re_path
from django.views.static import serve
urlpatterns += [
    re_path(r'^media(?P<path>/.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
