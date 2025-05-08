"""
GitHub回调URL配置
"""
from django.urls import path
from . import github_auth

urlpatterns = [
    path('', github_auth.github_callback, name='github_callback'),
]
