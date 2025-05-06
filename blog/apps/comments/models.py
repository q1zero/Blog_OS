from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Comment(models.Model):
    """评论模型"""

    content = models.TextField(_("评论内容"))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("作者"),
        db_index=True,
    )
    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("文章"),
        db_index=True,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name=_("父评论"),
        db_index=True,
    )
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)
    is_approved = models.BooleanField(_("是否审核通过"), default=False, db_index=True)

    class Meta:
        verbose_name = _("评论")
        verbose_name_plural = _("评论")
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["article", "is_approved"], name="article_approved_idx"
            ),
        ]

    def __str__(self):
        return f"{self.author.username} 对 {self.article.title} 的评论"
