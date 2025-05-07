# Celery 异步任务使用指南

本模块提供了基于Celery的异步任务处理功能，可用于处理耗时操作，如邮件发送、数据生成和定时任务等。

## 1. 基本设置

Celery已配置使用Redis作为消息代理(Broker)和结果存储(Backend)。确保系统中安装并运行了Redis服务。

### 依赖项

- celery>=5.5.2
- redis>=6.0.0

## 2. 启动Celery

在开发环境中，需要通过以下方式启动Celery工作进程和Beat定时任务调度器：

```bash
# 启动Celery工作进程
cd blog/
celery -A utils.celery.app worker -l info

# 在另一个终端启动Celery Beat调度器
cd blog/
celery -A utils.celery.app beat -l info
```

在生产环境中，建议使用Supervisor或systemd来管理Celery进程。

## 3. 可用的任务

### 3.1 邮件发送

```python
from utils.celery.tasks import send_email_async

# 基本用法
send_email_async.delay(
    subject="测试邮件",
    message="这是一封测试邮件",
    recipient_list=["user@example.com"]
)

# 使用HTML内容
send_email_async.delay(
    subject="HTML测试邮件",
    message="这是一封测试邮件（纯文本版本）",
    recipient_list=["user@example.com"],
    html_message="<h1>这是一封测试邮件</h1><p>HTML版本</p>"
)
```

### 3.2 站点统计

```python
from utils.celery.tasks import generate_site_stats

# 手动触发站点统计生成
stats = generate_site_stats.delay()

# 获取任务结果
result = stats.get(timeout=30)  # 最多等待30秒
print(result)  # 打印站点统计数据
```

### 3.3 清理过期令牌

```python
from utils.celery.tasks import cleanup_expired_tokens

# 手动触发清理过期令牌
result = cleanup_expired_tokens.delay()
print(f"已清理 {result.get()} 个过期令牌")
```

### 3.4 处理文章浏览量

```python
from utils.celery.tasks import process_article_views

# 手动触发处理文章浏览量
result = process_article_views.delay()
print(f"已更新 {result.get()} 篇文章的浏览量")
```

## 4. 高级接口

为了简化常见操作，我们提供了高级处理接口：

```python
from utils.celery.handlers import (
    send_verification_email, 
    send_article_published_notification,
    send_comment_notification,
    send_reply_notification
)

# 发送验证邮件
send_verification_email(user, verification_token, site_url)

# 发送文章发布通知
send_article_published_notification(article)

# 发送评论通知
send_comment_notification(comment)

# 发送回复通知
send_reply_notification(reply)
```

## 5. 定时任务

已配置的定时任务：

| 任务名称 | 执行时间 | 功能 |
|--------|---------|-----|
| generate-site-stats-daily | 每天凌晨2:00 | 生成站点统计数据 |
| cleanup-expired-tokens-daily | 每天凌晨3:00 | 清理过期的验证令牌 |
| process-article-views-hourly | 每小时整点 | 处理文章浏览量数据 |

若要修改定时任务配置，请编辑 `utils/celery/schedule.py` 文件。

## 6. 任务监控

在开发环境中，可以通过Celery命令行查看任务执行情况。在生产环境中，建议使用Flower来监控Celery任务：

```bash
pip install flower
celery -A utils.celery.app flower
```

然后访问 <http://localhost:5555> 查看任务监控仪表板。

## 7. 故障排除

1. 确保Redis服务正在运行
2. 检查Celery工作进程是否启动
3. 查看Celery日志以获取详细错误信息
4. 确保任务函数能够单独运行（不依赖于Celery）
