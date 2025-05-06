from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from api.views.user_views import UserViewSet
from api.views.article_views import ArticleViewSet, CategoryViewSet, TagViewSet
from api.views.comment_views import CommentViewSet

# 创建Swagger文档视图
schema_view = get_schema_view(
    openapi.Info(
        title="博客API",
        default_version='v1',
        description="博客系统的RESTful API接口文档",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# 创建路由器
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'comments', CommentViewSet, basename='comment')

# API URL配置
urlpatterns = [
    # API版本v1
    path('v1/', include([
        # API根路由
        path('', include(router.urls)),
        
        # JWT认证
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
        
        # DRF认证
        path('auth/', include('rest_framework.urls')),
    ])),
    
    # Swagger文档
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
