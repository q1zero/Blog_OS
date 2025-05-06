from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限：对象所有者可以编辑，其他用户只读
    """
    
    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写入权限只允许对象的所有者
        # 假设对象有一个author或user属性
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    自定义权限：管理员可以编辑，其他用户只读
    """
    
    def has_permission(self, request, view):
        # 读取权限允许任何请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写入权限只允许管理员
        return request.user and request.user.is_staff


class IsAdminOrStaffUser(permissions.BasePermission):
    """
    自定义权限：只允许管理员或工作人员
    """
    
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)
