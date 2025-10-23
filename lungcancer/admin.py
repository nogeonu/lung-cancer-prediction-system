from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Patient, Notice, QnA, UserProfile

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'gender', 'age', 'prediction', 'prediction_probability', 'created_at']
    list_filter = ['gender', 'prediction', 'created_at']
    search_fields = ['id', 'age']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('gender', 'age')
        }),
        ('생활 습관', {
            'fields': ('smoking', 'alcohol_consuming')
        }),
        ('증상', {
            'fields': (
                'yellow_fingers', 'anxiety', 'peer_pressure', 
                'chronic_disease', 'fatigue', 'allergy', 
                'wheezing', 'coughing', 'shortness_of_breath', 
                'swallowing_difficulty', 'chest_pain'
            )
        }),
        ('예측 결과', {
            'fields': ('prediction', 'prediction_probability')
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_important', 'is_active', 'created_at']
    list_filter = ['is_important', 'is_active', 'created_at']
    search_fields = ['title', 'content']
    list_editable = ['is_important', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('공지사항 정보', {
            'fields': ('title', 'content', 'is_important', 'is_active')
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(QnA)
class QnAAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_answered', 'is_active', 'questioner_name', 'created_at']
    list_filter = ['category', 'is_answered', 'is_active', 'created_at']
    search_fields = ['question', 'answer', 'questioner_name', 'questioner_email']
    list_editable = ['is_answered', 'is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('질문 정보', {
            'fields': ('question', 'category', 'questioner_name', 'questioner_email')
        }),
        ('답변 정보', {
            'fields': ('answer', 'is_answered', 'is_active')
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # 기본 일괄 삭제 액션을 제거하고, 안전 삭제 액션을 추가한다
    actions = ['safe_delete_selected']

    def get_actions(self, request):
        actions = super().get_actions(request)
        # 기본 제공되는 delete_selected 액션 제거 (무결성 제약 이슈 방지)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def safe_delete_selected(self, request, queryset):
        """선택된 항목을 개별 삭제로 처리하여 FK 제약 오류를 회피한다."""
        from django.contrib import messages
        deleted = 0
        failed = 0
        for obj in queryset:
            try:
                obj.delete()
                deleted += 1
            except Exception:
                failed += 1
        if deleted:
            messages.success(request, f"{deleted}건 삭제 완료")
        if failed:
            messages.warning(request, f"{failed}건 삭제 실패 (관련 데이터 제약)")
    safe_delete_selected.short_description = '선택 항목 안전 삭제'


# UserProfile 인라인
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '프로필 정보'
    fields = ('first_name', 'last_name', 'email', 'phone')


# User 모델 확장
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('개인 정보', {'fields': ('first_name', 'last_name', 'email')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요한 날짜', {'fields': ('last_login', 'date_joined')}),
    )


# UserProfile 모델 등록
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'email', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'first_name', 'last_name', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('사용자 정보', {
            'fields': ('user',)
        }),
        ('개인 정보', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# 기존 User 모델 등록 해제 후 커스텀 모델로 재등록
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
