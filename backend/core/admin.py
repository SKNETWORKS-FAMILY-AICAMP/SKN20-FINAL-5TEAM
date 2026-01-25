# 수정일: 2026-01-25
# 수정내용: Antigravity - 모델 구조에 맞춰 관리자 화면 구성 최종 정리

from django.contrib import admin
from core.models import Common, UserProfile, UserDetail, DashboardLog, Practice, PracticeDetail

# 1. Common (공통 코드) Admin
@admin.register(Common)
class CommonAdmin(admin.ModelAdmin):
    list_display = ('id', 'top_code', 'code_id', 'code_name', 'order_number', 'use_yn')
    search_fields = ('top_code', 'code_name', 'code_id')
    list_filter = ('top_code', 'use_yn')
    list_editable = ('order_number', 'use_yn')

# 2. UserProfile (회원) Admin
class UserDetailInline(admin.StackedInline):
    model = UserDetail
    can_delete = False

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'email', 'create_date', 'use_yn')
    search_fields = ('id', 'user_name', 'email')
    inlines = (UserDetailInline,)

# 3. Dashboard (통계) Admin
@admin.register(DashboardLog)
class DashboardLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_name', 'event_count', 'create_date')
    search_fields = ('event_name',)

# 5. Practice (연습 과정) Admin
@admin.register(Practice)
class PracticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'unit_number', 'title', 'level', 'participant_count', 'display_order', 'is_active')
    list_filter = ('is_active', 'level')
    search_fields = ('title', 'subtitle')
    list_editable = ('display_order', 'is_active', 'participant_count')
    ordering = ('display_order', 'unit_number')

# 6. PracticeDetail (연습 상세 콘텐츠) Admin
@admin.register(PracticeDetail)
class PracticeDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'practice', 'detail_title', 'detail_type', 'display_order', 'is_active')
    list_filter = ('detail_type', 'is_active', 'practice')
    search_fields = ('detail_title', 'content_data')
    list_editable = ('display_order', 'is_active')
    ordering = ('practice', 'display_order')
