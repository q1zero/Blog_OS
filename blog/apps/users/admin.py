from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, EmailVerification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """自定义用户管理界面"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    actions = ['activate_users', 'deactivate_users']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('first_name', 'last_name', 'email', 'bio', 'avatar')}),
        (_('权限信息'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('重要日期'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    def activate_users(self, request, queryset):
        """激活选中的用户"""
        updated = queryset.update(is_active=True)
        self.message_user(request, _('成功激活 %d 个用户。') % updated)
    activate_users.short_description = _('激活选中的用户')

    def deactivate_users(self, request, queryset):
        """禁用选中的用户"""
        updated = queryset.update(is_active=False)
        self.message_user(request, _('成功禁用 %d 个用户。') % updated)
    deactivate_users.short_description = _('禁用选中的用户')


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """邮箱验证管理界面"""
    list_display = ('user', 'token', 'created_at', 'expires_at', 'verified')
    list_filter = ('verified', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('token', 'created_at')
    date_hierarchy = 'created_at'
