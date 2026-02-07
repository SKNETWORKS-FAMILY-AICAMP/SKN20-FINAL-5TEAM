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
    
    # 각 앱의 URL 연결 (협업 시 담당 앱을 추가)
    path('api/core/', include('core.urls')),
]

# [수정일: 2026-02-06] 미디어 파일 서빙 설정 추가 (Antigravity)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
