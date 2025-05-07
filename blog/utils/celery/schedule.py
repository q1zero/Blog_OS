"""
Celery定时任务计划配置模块
"""
from celery.schedules import crontab

# 定时任务配置（将在settings.py中被引用）
CELERY_BEAT_SCHEDULE = {
    # 每天凌晨2点生成站点统计数据
    'generate-site-stats-daily': {
        'task': 'utils.celery.tasks.generate_site_stats',
        'schedule': crontab(hour=2, minute=0),
    },
    # 每天凌晨3点清理过期令牌
    'cleanup-expired-tokens-daily': {
        'task': 'utils.celery.tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=3, minute=0),
    },
    # 每小时处理一次文章浏览量
    'process-article-views-hourly': {
        'task': 'utils.celery.tasks.process_article_views',
        'schedule': crontab(minute=0),  # 每小时运行一次
    },
}