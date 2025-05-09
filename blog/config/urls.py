"""
URL configuration for blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.articles import views as article_views
from .views import health_check

urlpatterns = [
    # 健康检查路由，用于部署环境监测
    path("health/", health_check, name="health_check"),
    # 也添加根路径的健康检查，但是使用额外的URL模式
    path(".well-known/health/", health_check, name="root_health_check"),
    # 恢复首页原来的视图
    path("", article_views.home, name="home"),
    path("admin/", admin.site.urls),
    path("articles/", include("apps.articles.urls", namespace="articles")),
    path("users/", include("apps.users.urls", namespace="users")),
    path("comments/", include("apps.comments.urls", namespace="comments")),
    path("logs/", include("utils.logs.urls", namespace="logs")),
    # API URLs
    path("api/", include("utils.api.urls")),
    # GitHub认证URLs
    path("github/", include("utils.github_auth.urls", namespace="github_auth")),
    # 添加对GitHub回调的处理
    path("accounts/github/callback", include("utils.github_auth.urls_callback")),
    # django-allauth URLs
    path("accounts/", include("allauth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
