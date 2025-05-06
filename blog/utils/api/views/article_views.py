from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils.text import slugify
from django.utils import timezone

from apps.articles.models import Article, Category, Tag
from utils.api.serializers.article_serializers import (
    ArticleListSerializer, ArticleDetailSerializer, ArticleCreateUpdateSerializer,
    CategorySerializer, TagSerializer
)
from utils.api.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    """
    分类API视图集
    
    list:
    获取分类列表
    
    retrieve:
    获取分类详情
    
    create:
    创建新分类（仅管理员）
    
    update:
    更新分类（仅管理员）
    
    partial_update:
    部分更新分类（仅管理员）
    
    destroy:
    删除分类（仅管理员）
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    
    def perform_create(self, serializer):
        """创建分类时自动生成slug"""
        if not serializer.validated_data.get('slug'):
            serializer.validated_data['slug'] = slugify(serializer.validated_data['name'])
        serializer.save()


class TagViewSet(viewsets.ModelViewSet):
    """
    标签API视图集
    
    list:
    获取标签列表
    
    retrieve:
    获取标签详情
    
    create:
    创建新标签（仅管理员）
    
    update:
    更新标签（仅管理员）
    
    partial_update:
    部分更新标签（仅管理员）
    
    destroy:
    删除标签（仅管理员）
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    
    def perform_create(self, serializer):
        """创建标签时自动生成slug"""
        if not serializer.validated_data.get('slug'):
            serializer.validated_data['slug'] = slugify(serializer.validated_data['name'])
        serializer.save()


class ArticleViewSet(viewsets.ModelViewSet):
    """
    文章API视图集
    
    list:
    获取文章列表
    
    retrieve:
    获取文章详情
    
    create:
    创建新文章
    
    update:
    更新文章
    
    partial_update:
    部分更新文章
    
    destroy:
    删除文章
    """
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'published_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """根据用户权限过滤文章"""
        user = self.request.user
        
        # 基本查询：已发布且公开的文章
        queryset = Article.objects.filter(status='published', visibility='public')
        
        # 如果用户已登录，添加用户自己的私密文章
        if user.is_authenticated:
            user_articles = Article.objects.filter(author=user)
            queryset = queryset | user_articles
        
        # 如果是管理员，显示所有文章
        if user.is_authenticated and user.is_staff:
            queryset = Article.objects.all()
        
        # 分类过滤
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # 标签过滤
        tag_slug = self.request.query_params.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # 作者过滤
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        # 状态过滤（仅对作者和管理员有效）
        status_filter = self.request.query_params.get('status')
        if status_filter and user.is_authenticated:
            if status_filter == 'draft' and (user.is_staff or queryset.filter(author=user).exists()):
                queryset = queryset.filter(Q(status='draft') & Q(author=user) | Q(status='draft') & Q(user.is_staff))
        
        return queryset.distinct()
    
    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateUpdateSerializer
        elif self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer
    
    def perform_create(self, serializer):
        """创建文章时设置作者和slug"""
        # 生成slug
        title = serializer.validated_data.get('title')
        slug = slugify(title)
        
        # 确保slug唯一
        if Article.objects.filter(slug=slug).exists():
            slug = f"{slug}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # 保存文章
        serializer.save(author=self.request.user, slug=slug)
    
    def perform_update(self, serializer):
        """更新文章时可能需要更新slug"""
        instance = self.get_object()
        title = serializer.validated_data.get('title')
        
        # 如果标题变了，更新slug
        if title and title != instance.title:
            slug = slugify(title)
            if Article.objects.filter(slug=slug).exclude(id=instance.id).exists():
                slug = f"{slug}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            serializer.save(slug=slug)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def my_articles(self, request):
        """获取当前用户的所有文章"""
        if not request.user.is_authenticated:
            return Response({"detail": "认证失败"}, status=status.HTTP_401_UNAUTHORIZED)
        
        queryset = Article.objects.filter(author=request.user)
        
        # 状态过滤
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
