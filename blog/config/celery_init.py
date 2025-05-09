import os

# 确保 DJANGO_SETTINGS_MODULE 环境变量在 Django 设置被访问前设置好
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 假设 blog.utils.celery.app 文件中定义了 Celery app 实例
# (根据上次的修复，此导入应该是 from blog.utils.celery.app import app as actual_celery_instance)
from utils.celery.app import app as actual_celery_instance

app = actual_celery_instance  # 将 Celery app 实例暴露为 'app'
celery_app = app  # 添加 celery_app 变量，以便被 wsgi.py 导入

# 从 Django 设置中加载 Celery 配置
app.config_from_object("django.conf:settings", namespace="CELERY")

# 自动发现 Django 应用中的任务
app.autodiscover_tasks()

__all__ = ("app", "celery_app")
