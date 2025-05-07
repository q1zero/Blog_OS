"""
Celery应用配置模块
"""

import os
from celery import Celery

# 设置Django默认设置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 创建Celery应用
app = Celery("blog")

# 使用Django的settings.py配置Celery
app.config_from_object("django.conf:settings", namespace="CELERY")

# 自动发现所有应用中的tasks.py文件
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """用于调试的任务"""
    print(f"Request: {self.request!r}")
