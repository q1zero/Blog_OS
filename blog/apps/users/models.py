import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone


class User(AbstractUser):
    """
    自定义用户模型，继承自AbstractUser

    默认字段包括：
    - username: 用户名
    - first_name: 名
    - last_name: 姓
    - email: 邮箱
    - is_staff: 是否为管理员
    - is_active: 是否激活
    - date_joined: 注册日期
    """
    # 自定义字段
    bio = models.TextField(_('个人简介'), blank=True,null=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', blank=True, null=True)

    # 如果需要更复杂的角色管理，可以添加自定义角色字段
    # 例如：is_editor, is_vip等

    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')

    def __str__(self):
        return self.username


class EmailVerification(models.Model):
    """邮箱验证模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('邮箱验证')
        verbose_name_plural = _('邮箱验证')

    def __str__(self):
        return f"{self.user.username} - {self.token}"

    def is_valid(self):
        """检查验证链接是否有效"""
        return not self.verified and self.expires_at > timezone.now()

