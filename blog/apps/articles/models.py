from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings

# Create your models here.


class Category(models.Model):
    """文章分类模型"""

    name = models.CharField(_("分类名称"), max_length=100)
    slug = models.SlugField(_("分类别名"), max_length=100, unique=True)
    description = models.TextField(_("分类描述"), blank=True)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)

    class Meta:
        verbose_name = _("分类")
        verbose_name_plural = _("分类")
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.name)


class Tag(models.Model):
    """文章标签模型"""

    name = models.CharField(_("标签名称"), max_length=50)
    slug = models.SlugField(_("标签别名"), max_length=50, blank=True)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)

    class Meta:
        verbose_name = _("标签")
        verbose_name_plural = _("标签")
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        # 如果没有设置slug，使用ID
        if not self.slug and self.id:
            self.slug = str(self.id)
        super().save(*args, **kwargs)
        # 如果创建后仍然没有slug（第一次保存），再次保存以设置slug
        if not self.slug:
            self.slug = str(self.id)
            super().save(update_fields=["slug"])


class Article(models.Model):
    """文章模型"""

    STATUS_CHOICES = (
        ("draft", _("草稿")),
        ("published", _("已发布")),
    )
    VISIBILITY_CHOICES = (
        ("public", _("公开")),
        ("private", _("私密")),
    )

    title = models.CharField(_("标题"), max_length=200)
    slug = models.SlugField(_("别名"), max_length=200, unique=True, blank=True)
    content = models.TextField(_("内容"))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
        verbose_name=_("作者"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name=_("分类"),
    )
    tags = models.ManyToManyField(
        Tag, blank=True, related_name="articles", verbose_name=_("标签")
    )
    status = models.CharField(
        _("状态"), max_length=10, choices=STATUS_CHOICES, default="draft"
    )
    visibility = models.CharField(
        _("可见性"), max_length=10, choices=VISIBILITY_CHOICES, default="public"
    )
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)
    published_at = models.DateTimeField(_("发布时间"), null=True, blank=True)

    class Meta:
        verbose_name = _("文章")
        verbose_name_plural = _("文章")
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse("articles:article_detail", args=[self.slug])

    def save(self, *args, **kwargs):
        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()
        # 如果没有设置slug，使用ID
        if not self.slug and self.id:
            self.slug = str(self.id)
        super().save(*args, **kwargs)
        # 如果创建后仍然没有slug（第一次保存），再次保存以设置slug
        if not self.slug:
            self.slug = str(self.id)
            super().save(update_fields=["slug"])


class Like(models.Model):
    """文章点赞模型"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name=_("用户"),
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name=_("文章"),
    )
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)

    class Meta:
        verbose_name = _("点赞")
        verbose_name_plural = _("点赞")
        # 确保用户只能对一篇文章点赞一次
        unique_together = ("user", "article")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} 点赞了 {self.article.title}"


class Favorite(models.Model):
    """文章收藏模型"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name=_("用户"),
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name=_("文章"),
    )
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)

    class Meta:
        verbose_name = _("收藏")
        verbose_name_plural = _("收藏")
        # 确保用户只能收藏一篇文章一次
        unique_together = ("user", "article")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.article.title}"
