# 수정내용: 코드 실행 샌드박스 및 라우팅 설정 정합성 수정 (Antigravity)

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
    AIProxyView,
    BugHuntEvaluationView,
    CodeExecutionView,
    BehaviorVerificationView,
    OverallProgressView,
    UserAnswersView,
    activity_view
)
from core.views.pseudocode_execution import execute_python_code

router = DefaultRouter()
router.register(r'users', UserProfileViewSet, basename='users')
router.register(r'dashboard-logs', DashboardLogViewSet)
router.register(r'commons', CommonViewSet)
router.register(r'practices', PracticeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # 인증 및 사용자 관리 API
    path('user/profile/', UserProfileViewSet.as_view({'get': 'list', 'post': 'create'})),
    
    # 활동 및 리더보드 통합 API (AI-Arcade)
    path('activity/leaderboard/', activity_view.LeaderboardView.as_view(), name='leaderboard'),
    path('activity/progress/', activity_view.UserProgressView.as_view(), name='user_progress'),
    path('activity/submit/', activity_view.SubmitProblemView.as_view(), name='submit_problem'),
    path('activity/preview/', activity_view.AvatarPreviewView.as_view(), name='avatar_preview'), # [수정일: 2026-02-06] 추가

    # 인증 관련
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', SessionCheckView.as_view(), name='session_check'),
    
    # AI 평가 관련
    path('ai-evaluate/', AIEvaluationView.as_view(), name='ai_evaluate'),
    path('ai-proxy/', AIProxyView.as_view(), name='ai_proxy'),
    path('ai-bughunt-evaluate/', BugHuntEvaluationView.as_view(), name='bughunt_evaluate'),

    # 코드 실행 샌드박스 API
    path('execute-code/', CodeExecutionView.as_view(), name='execute_code'),
    path('verify-behavior/', BehaviorVerificationView.as_view(), name='verify_behavior'),
    # 관리 및 기록 조회 API
    path('management/overall-progress/', OverallProgressView.as_view(), name='overall_progress'),
    path('management/user-answers/', UserAnswersView.as_view(), name='user_answers_all'),
    path('management/user-answers/<str:practice_id>/', UserAnswersView.as_view(), name='user_answers_practice'),
    path('management/user-answers/<str:practice_id>/<int:user_id>/', UserAnswersView.as_view(), name='user_answers_detail'),

    path('pseudocode/execute/', execute_python_code, name='pseudocode_execute'),
]
