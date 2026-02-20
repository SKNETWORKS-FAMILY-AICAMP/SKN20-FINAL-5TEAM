# 수정내용: 코드 실행 샌드박스 및 라우팅 설정 정합성 수정 (Antigravity)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    UserProfileViewSet,
    DashboardLogViewSet,
    CommonViewSet,
    PracticeViewSet,
    PracticeDetailViewSet,
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
    activity_view,
    PseudocodeAgentView,
    JobPlannerParseView,
    JobPlannerAnalyzeView,
    JobPlannerCompanyAnalyzeView,
    JobPlannerAgentQuestionsView,
    JobPlannerAgentReportView,
    JobPlannerRecommendView
)
from core.views.pseudocode_execution import execute_python_code
from core.views import pseudocode_evaluation, youtube_recommendation
from core.views.architecture_view import ArchitectureEvaluationView, ArchitectureQuestionGeneratorView

router = DefaultRouter()
router.register(r'users', UserProfileViewSet, basename='users')
router.register(r'dashboard-logs', DashboardLogViewSet)
router.register(r'commons', CommonViewSet)
router.register(r'practices', PracticeViewSet)
router.register(r'practice-details', PracticeDetailViewSet, basename='practice-details')

urlpatterns = [
    path('', include(router.urls)),
    
    # 인증 및 사용자 관리 API
    path('user/profile/', UserProfileViewSet.as_view({'get': 'list', 'post': 'create'})),
    
    # 활동 및 리더보드 통합 API (AI-Arcade)
    path('activity/leaderboard/', activity_view.LeaderboardView.as_view(), name='leaderboard'),
    path('activity/progress/', activity_view.UserProgressView.as_view(), name='user_progress'),
    path('activity/solved-problems/', activity_view.UserSolvedProblemView.as_view(), name='solved_problems'),
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

    # Architecture Practice 평가 및 질문 생성 API [작성일: 2026-02-20]
    path('architecture/evaluate/', ArchitectureEvaluationView.as_view(), name='architecture_evaluate'),
    path('architecture/generate-questions/', ArchitectureQuestionGeneratorView.as_view(), name='architecture_questions'),

    # 코드 실행 샌드박스 API
    path('execute-code/', CodeExecutionView.as_view(), name='execute_code'),
    path('verify-behavior/', BehaviorVerificationView.as_view(), name='verify_behavior'),
    # 관리 및 기록 조회 API
    path('management/overall-progress/', OverallProgressView.as_view(), name='overall_progress'),
    path('management/user-answers/', UserAnswersView.as_view(), name='user_answers_all'),
    path('management/user-answers/<str:practice_id>/', UserAnswersView.as_view(), name='user_answers_practice'),
    path('management/user-answers/<str:practice_id>/<int:user_id>/', UserAnswersView.as_view(), name='user_answers_detail'),

    path('pseudocode/execute/', execute_python_code, name='pseudocode_execute'),
    path('pseudo-agent/', PseudocodeAgentView.as_view(), name='pseudo_agent'),
    path('pseudocode/evaluate-5d/', pseudocode_evaluation.evaluate_pseudocode_5d),
    path('youtube/recommendations', youtube_recommendation.get_youtube_recommendations),

    # Job Planner API
    path('job-planner/parse/', JobPlannerParseView.as_view(), name='job_planner_parse'),
    path('job-planner/analyze/', JobPlannerAnalyzeView.as_view(), name='job_planner_analyze'),
    path('job-planner/company-analyze/', JobPlannerCompanyAnalyzeView.as_view(), name='job_planner_company_analyze'),
    path('job-planner/agent-questions/', JobPlannerAgentQuestionsView.as_view(), name='job_planner_agent_questions'),
    path('job-planner/agent-report/', JobPlannerAgentReportView.as_view(), name='job_planner_agent_report'),
    path('job-planner/recommend/', JobPlannerRecommendView.as_view(), name='job_planner_recommend'),
]
