from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AccessLog(models.Model):
    """访问日志模型，记录用户的请求信息"""
    
    # 请求信息
    path = models.CharField(_("请求路径"), max_length=255)
    method = models.CharField(_("请求方法"), max_length=10)
    status_code = models.PositiveIntegerField(_("状态码"), null=True, blank=True)
    
    # 用户信息
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="access_logs",
        verbose_name=_("用户")
    )
    ip_address = models.GenericIPAddressField(_("IP地址"), null=True, blank=True)
    user_agent = models.TextField(_("用户代理"), blank=True)
    
    # 请求详情
    referer = models.URLField(_("来源页面"), max_length=255, blank=True)
    query_params = models.TextField(_("查询参数"), blank=True)
    
    # 性能指标
    response_time = models.FloatField(_("响应时间(ms)"), null=True, blank=True)
    
    # 时间信息
    timestamp = models.DateTimeField(_("访问时间"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("访问日志")
        verbose_name_plural = _("访问日志")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["user"]),
            models.Index(fields=["path"]),
            models.Index(fields=["status_code"]),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else "匿名用户"
        return f"{user_str} - {self.method} {self.path} - {self.status_code} - {self.timestamp}"
