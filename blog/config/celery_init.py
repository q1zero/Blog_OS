"""
Celery初始化配置，用于在Django项目启动时初始化Celery
在Django的wsgi.py和asgi.py中引用此文件
"""

from utils.celery.app import app as celery_app

__all__ = ["celery_app"]
