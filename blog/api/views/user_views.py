from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.users.models import User
from api.serializers.user_serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from api.permissions import IsOwnerOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    """
    用户API视图集
    
    list:
    获取用户列表
    
    retrieve:
    获取用户详情
    
    create:
    创建新用户
    
    update:
    更新用户信息
    
    partial_update:
    部分更新用户信息
    
    destroy:
    删除用户
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """根据操作选择权限"""
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前登录用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """更新当前登录用户信息"""
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
