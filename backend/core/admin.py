# 수정일: 2026-01-22
# 수정내용: Antigravity - 불필요한 모델 제거 및 현재 모델 구조에 맞춰 Admin 정리

from django.contrib import admin
from core.models import Common, UserProfile, UserDetail, Notice, DashboardLog, Practice

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
    verbose_name_plural = 'User Detail'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'email', 'create_date', 'use_yn')
    search_fields = ('id', 'user_name', 'email')
    inlines = (UserDetailInline,)

# 3. Notice (공지사항) Admin
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'open_date', 'create_date', 'use_yn')
    search_fields = ('title', 'contents')
    list_filter = ('use_yn',)

# 4. Dashboard (통계) Admin
@admin.register(DashboardLog)
class DashboardLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_name', 'event_count', 'create_date')
    search_fields = ('event_name',)

# 5. Practice (연습) Admin
@admin.register(Practice)
class PracticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'practice_name', 'practice_status', 'create_date', 'use_yn')
    search_fields = ('practice_name', 'practice_number')
