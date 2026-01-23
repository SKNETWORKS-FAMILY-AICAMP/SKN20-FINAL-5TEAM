# 수정일: 2026-01-22
# 수정내용: Antigravity - 모델 리팩토링 및 PK(id) 통일 반영 라우팅 설정

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    UserProfileViewSet,
    NoticeViewSet,
    DashboardLogViewSet,
    CommonViewSet,
    PracticeViewSet,
    LoginView, 
    LogoutView, 
    SessionCheckView,
    AIChatView
)

router = DefaultRouter()

# 담당자 A (User)
router.register(r'users', UserProfileViewSet)

# 담당자 D (Notice) - Post 대신 Notice 사용
router.register(r'notices', NoticeViewSet)

# 담당자 F (Dashboard)
router.register(r'dashboard', DashboardLogViewSet)

# 연습용 (Practice)
router.register(r'practices', PracticeViewSet)

# 공통 코드
router.register(r'commons', CommonViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # 인증 API
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', SessionCheckView.as_view(), name='session_check'),
    path('ai-chat/', AIChatView.as_view(), name='ai_chat'),
]
