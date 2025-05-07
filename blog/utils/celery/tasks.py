"""
Celery任务定义模块
提供通用的异步任务
"""

import time
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .app import app

logger = logging.getLogger(__name__)


@app.task
def send_email_async(
    subject, message, from_email=None, recipient_list=None, html_message=None
):
    """
    异步发送电子邮件任务

    Args:
        subject: 邮件主题
        message: 邮件内容（纯文本）
        from_email: 发件人邮箱，默认使用settings.DEFAULT_FROM_EMAIL
        recipient_list: 收件人列表
        html_message: 邮件HTML内容（可选）
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    if recipient_list is None:
        recipient_list = []

    logger.info(f"开始发送邮件: {subject} 到 {recipient_list}")
    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"邮件发送成功，返回码: {result}")
        return result
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        raise


@app.task
def generate_site_stats():
    """
    生成站点统计数据任务
    可以定期执行，收集站点数据如用户数、文章数、评论数等
    """
    from apps.users.models import User
    from apps.articles.models import Article
    from apps.comments.models import Comment

    logger.info("开始生成站点统计数据")
    start_time = time.time()

    # 收集数据
    stats = {
        "user_count": User.objects.count(),
        "active_user_count": User.objects.filter(is_active=True).count(),
        "article_count": Article.objects.count(),
        "published_article_count": Article.objects.filter(status="published").count(),
        "comment_count": Comment.objects.count(),
        "approved_comment_count": Comment.objects.filter(is_approved=True).count(),
        "timestamp": timezone.now().isoformat(),
    }

    # 这里可以将统计数据保存到数据库或缓存
    # 示例: cache.set('site_stats', stats, timeout=86400)  # 缓存24小时

    end_time = time.time()
    logger.info(f"站点统计数据生成完成，耗时: {end_time - start_time:.2f}秒")
    return stats


@app.task
def cleanup_expired_tokens():
    """
    清理过期令牌任务
    可以定期执行，清理数据库中的过期令牌
    """
    from apps.users.models import EmailVerification

    logger.info("开始清理过期令牌")
    start_time = time.time()

    # 删除已过期的邮箱验证令牌
    expired_tokens = EmailVerification.objects.filter(
        expiry_date__lt=timezone.now(), verified=False
    )
    count = expired_tokens.count()
    expired_tokens.delete()

    end_time = time.time()
    logger.info(
        f"清理过期令牌完成，已删除 {count} 个过期令牌，耗时: {end_time - start_time:.2f}秒"
    )
    return count


@app.task
def process_article_views():
    """
    处理文章浏览量任务
    可以定期将临时存储的浏览量数据更新到数据库
    """
    from apps.articles.models import Article
    from django.core.cache import cache

    logger.info("开始处理文章浏览量数据")
    start_time = time.time()

    # 获取所有文章ID
    article_ids = Article.objects.values_list("id", flat=True)
    updated_count = 0

    # 逐个处理每篇文章的缓存浏览量
    for article_id in article_ids:
        view_count_key = f"article_views_{article_id}"
        cached_views = cache.get(view_count_key)

        if cached_views:
            # 将缓存的浏览量更新到数据库
            article = Article.objects.get(id=article_id)
            article.views += cached_views
            article.save(update_fields=["views"])

            # 重置缓存
            cache.delete(view_count_key)
            updated_count += 1

    end_time = time.time()
    logger.info(
        f"文章浏览量处理完成，更新了 {updated_count} 篇文章，耗时: {end_time - start_time:.2f}秒"
    )
    return updated_count
