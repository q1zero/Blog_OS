"""
GitHub认证URL配置
"""
from django.urls import path
from . import github_auth
from . import debug
from . import test_urls
from django.views.generic import TemplateView
from django.conf import settings

app_name = 'github_auth'

urlpatterns = [
    path('login/', github_auth.github_login, name='login'),
    path('callback/', github_auth.github_callback, name='callback'),
    path('callback', github_auth.github_callback, name='callback_no_slash'),  # 不带末尾斜杠的版本
    path('debug/', debug.debug_redirect_uri, name='debug'),
    path('test-urls/', test_urls.test_urls, name='test_urls'),
]
