# 수정일: 2026-01-25
# 수정내용: Antigravity - 라우팅 정보 최종 동기화

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    UserProfileViewSet,
    DashboardLogViewSet,
    CommonViewSet,
    PracticeViewSet,
    LoginView,
    LogoutView,
    SessionCheckView,
    AIEvaluationView,
    BugHuntEvaluationView
)

router = DefaultRouter()

# 1. 담당자 A (User)
router.register(r'users', UserProfileViewSet)

# 2. 담당자 F (Dashboard)
router.register(r'dashboard', DashboardLogViewSet)

# 3. 연습 과정 (Practice)
router.register(r'practices', PracticeViewSet)

# 4. 공통 코드
router.register(r'commons', CommonViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # 인증 관련 API
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', SessionCheckView.as_view(), name='session_check'),
    path('ai-evaluate/', AIEvaluationView.as_view(), name='ai_evaluate'),
    path('ai-bughunt-evaluate/', BugHuntEvaluationView.as_view(), name='bughunt_evaluate'),
]
