from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.comments.models import Comment
from apps.articles.models import Article
from api.serializers.comment_serializers import CommentSerializer, CommentCreateSerializer
from api.permissions import IsOwnerOrReadOnly, IsAdminOrStaffUser


class CommentViewSet(viewsets.ModelViewSet):
    """
    评论API视图集
    
    list:
    获取评论列表
    
    retrieve:
    获取评论详情
    
    create:
    创建新评论
    
    update:
    更新评论（仅作者）
    
    partial_update:
    部分更新评论（仅作者）
    
    destroy:
    删除评论（仅作者或管理员）
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        """根据用户权限过滤评论"""
        user = self.request.user
        
        # 基本查询：已批准的评论
        queryset = Comment.objects.filter(is_approved=True)
        
        # 如果用户已登录，添加用户自己的未批准评论
        if user.is_authenticated:
            user_comments = Comment.objects.filter(author=user, is_approved=False)
            queryset = queryset | user_comments
        
        # 如果是管理员，显示所有评论
        if user.is_authenticated and user.is_staff:
            queryset = Comment.objects.all()
        
        # 文章过滤
        article_id = self.request.query_params.get('article')
        if article_id:
            queryset = queryset.filter(article_id=article_id)
        
        # 只显示顶级评论
        parent = self.request.query_params.get('parent')
        if parent is None:
            queryset = queryset.filter(parent=None)
        elif parent:
            queryset = queryset.filter(parent_id=parent)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer
    
    def perform_create(self, serializer):
        """创建评论时设置作者和审核状态"""
        # 管理员发布的评论自动批准
        is_approved = self.request.user.is_staff
        serializer.save(author=self.request.user, is_approved=is_approved)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrStaffUser])
    def approve(self, request, pk=None):
        """批准评论（仅管理员）"""
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        serializer = self.get_serializer(comment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrStaffUser])
    def reject(self, request, pk=None):
        """拒绝评论（仅管理员）"""
        comment = self.get_object()
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """获取待审核评论（仅管理员）"""
        if not request.user.is_staff:
            return Response({"detail": "您没有权限执行此操作"}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = Comment.objects.filter(is_approved=False)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
