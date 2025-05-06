from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import AccessLog


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    """访问日志管理界面"""
    list_display = (
        "timestamp", 
        "user", 
        "method", 
        "path", 
        "status_code", 
        "ip_address", 
        "response_time"
    )
    list_filter = (
        "method", 
        "status_code", 
        "timestamp"
    )
    search_fields = (
        "path", 
        "user__username", 
        "ip_address"
    )
    readonly_fields = (
        "timestamp", 
        "user", 
        "method", 
        "path", 
        "status_code", 
        "ip_address", 
        "user_agent", 
        "referer", 
        "query_params", 
        "response_time"
    )
    date_hierarchy = "timestamp"
    
    fieldsets = (
        (_("请求信息"), {
            "fields": ("method", "path", "status_code", "query_params")
        }),
        (_("用户信息"), {
            "fields": ("user", "ip_address", "user_agent")
        }),
        (_("来源信息"), {
            "fields": ("referer",)
        }),
        (_("性能指标"), {
            "fields": ("response_time",)
        }),
        (_("时间信息"), {
            "fields": ("timestamp",)
        }),
    )
    
    def has_add_permission(self, request):
        """禁止手动添加日志"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改日志"""
        return False
