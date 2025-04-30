from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from .models import User


def is_admin(user):
    """
    检查用户是否为管理员
    
    Args:
        user: 用户对象
    
    Returns:
        bool: 如果用户是管理员返回True，否则返回False
    """
    return user.is_authenticated and user.is_staff


def is_owner(user, obj):
    """
    检查用户是否为对象的所有者
    
    Args:
        user: 用户对象
        obj: 需要检查所有权的对象，必须有user或author属性
    
    Returns:
        bool: 如果用户是对象的所有者返回True，否则返回False
    """
    if not user.is_authenticated:
        return False
    
    # 检查对象是否有user属性
    if hasattr(obj, 'user'):
        return obj.user == user
    
    # 检查对象是否有author属性
    if hasattr(obj, 'author'):
        return obj.author == user
    
    return False


def create_user_group(name, permissions_list=None):
    """
    创建用户组并分配权限
    
    Args:
        name: 组名
        permissions_list: 权限列表，格式为[(app_label, model, codename), ...]
    
    Returns:
        Group: 创建的用户组
    """
    group, created = Group.objects.get_or_create(name=name)
    
    if permissions_list:
        for app_label, model, codename in permissions_list:
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            permission = Permission.objects.get(content_type=content_type, codename=codename)
            group.permissions.add(permission)
    
    return group


def setup_basic_groups():
    """
    设置基本的用户组和权限
    """
    # 编辑者组 - 可以创建、编辑和删除自己的文章
    editor_permissions = [
        ('articles', 'article', 'add_article'),
        ('articles', 'article', 'change_article'),
        ('articles', 'article', 'delete_article'),
        ('articles', 'article', 'view_article'),
    ]
    create_user_group('Editors', editor_permissions)
    
    # 评论者组 - 可以添加评论
    commenter_permissions = [
        ('comments', 'comment', 'add_comment'),
        ('comments', 'comment', 'change_comment'),  # 修改自己的评论
        ('comments', 'comment', 'delete_comment'),  # 删除自己的评论
        ('comments', 'comment', 'view_comment'),
    ]
    create_user_group('Commenters', commenter_permissions)


def assign_user_to_group(user, group_name):
    """
    将用户分配到指定的组
    
    Args:
        user: 用户对象
        group_name: 组名
    
    Returns:
        bool: 如果分配成功返回True，否则返回False
    """
    try:
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        return True
    except Group.DoesNotExist:
        return False
