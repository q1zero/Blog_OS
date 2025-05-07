"""
Celery任务处理器模块
提供高级接口，让其他应用可以方便地使用Celery任务
"""

from .tasks import send_email_async


def send_verification_email(user, verification_token, site_url):
    """
    发送验证邮件的高级接口

    Args:
        user: 用户对象
        verification_token: 验证令牌
        site_url: 站点基础URL
    """
    verify_url = f"{site_url}/users/verify-email/{verification_token}/"
    subject = "请验证您的邮箱"
    message = f"""
    您好 {user.username}，

    请点击以下链接验证您的邮箱:
    {verify_url}

    此链接将在24小时后过期。

    如果您没有注册我们的网站，请忽略此邮件。

    祝好,
    博客网站团队
    """
    html_message = f"""
    <p>您好 {user.username}，</p>
    <p>请点击以下链接验证您的邮箱:</p>
    <p><a href="{verify_url}">{verify_url}</a></p>
    <p>此链接将在24小时后过期。</p>
    <p>如果您没有注册我们的网站，请忽略此邮件。</p>
    <p>祝好,<br>博客网站团队</p>
    """

    # 异步发送邮件
    send_email_async.delay(
        subject=subject,
        message=message,
        recipient_list=[user.email],
        html_message=html_message,
    )


def send_article_published_notification(article):
    """
    当文章发布时，向作者发送通知

    Args:
        article: 文章对象
    """
    user = article.author
    subject = f"您的文章 '{article.title}' 已发布"
    message = f"""
    您好 {user.username}，

    您的文章 '{article.title}' 已成功发布。
    
    您可以通过以下链接查看文章:
    {article.get_absolute_url()}

    祝好,
    博客网站团队
    """
    html_message = f"""
    <p>您好 {user.username}，</p>
    <p>您的文章 <strong>'{article.title}'</strong> 已成功发布。</p>
    <p>您可以通过以下链接查看文章:</p>
    <p><a href="{article.get_absolute_url()}">{article.title}</a></p>
    <p>祝好,<br>博客网站团队</p>
    """

    # 异步发送邮件
    send_email_async.delay(
        subject=subject,
        message=message,
        recipient_list=[user.email],
        html_message=html_message,
    )


def send_comment_notification(comment):
    """
    当评论被发表时，向文章作者发送通知

    Args:
        comment: 评论对象
    """
    article = comment.article
    article_author = article.author
    comment_author = comment.author

    # 如果评论作者是文章作者自己，则不发送通知
    if article_author == comment_author:
        return

    subject = f"您的文章 '{article.title}' 收到了新评论"
    message = f"""
    您好 {article_author.username}，

    用户 {comment_author.username} 在您的文章 '{article.title}' 中发表了评论:

    "{comment.content}"
    
    您可以通过以下链接查看此评论:
    {article.get_absolute_url()}#comment-{comment.id}

    祝好,
    博客网站团队
    """
    html_message = f"""
    <p>您好 {article_author.username}，</p>
    <p>用户 <strong>{comment_author.username}</strong> 在您的文章 <strong>'{article.title}'</strong> 中发表了评论:</p>
    <blockquote>"{comment.content}"</blockquote>
    <p>您可以通过以下链接查看此评论:</p>
    <p><a href="{article.get_absolute_url()}#comment-{comment.id}">查看评论</a></p>
    <p>祝好,<br>博客网站团队</p>
    """

    # 异步发送邮件
    send_email_async.delay(
        subject=subject,
        message=message,
        recipient_list=[article_author.email],
        html_message=html_message,
    )


def send_reply_notification(reply):
    """
    当回复评论时，向原评论作者发送通知

    Args:
        reply: 回复评论对象
    """
    if not reply.parent:
        return

    parent_comment = reply.parent
    parent_author = parent_comment.author
    reply_author = reply.author
    article = reply.article

    # 如果回复作者是原评论作者自己，则不发送通知
    if parent_author == reply_author:
        return

    subject = f"您在文章 '{article.title}' 的评论收到了回复"
    message = f"""
    您好 {parent_author.username}，

    用户 {reply_author.username} 回复了您在文章 '{article.title}' 中的评论:

    您的评论: "{parent_comment.content}"
    回复内容: "{reply.content}"
    
    您可以通过以下链接查看此回复:
    {article.get_absolute_url()}#comment-{reply.id}

    祝好,
    博客网站团队
    """
    html_message = f"""
    <p>您好 {parent_author.username}，</p>
    <p>用户 <strong>{reply_author.username}</strong> 回复了您在文章 <strong>'{article.title}'</strong> 中的评论:</p>
    <p>您的评论: <blockquote>"{parent_comment.content}"</blockquote></p>
    <p>回复内容: <blockquote>"{reply.content}"</blockquote></p>
    <p>您可以通过以下链接查看此回复:</p>
    <p><a href="{article.get_absolute_url()}#comment-{reply.id}">查看回复</a></p>
    <p>祝好,<br>博客网站团队</p>
    """

    # 异步发送邮件
    send_email_async.delay(
        subject=subject,
        message=message,
        recipient_list=[parent_author.email],
        html_message=html_message,
    )
