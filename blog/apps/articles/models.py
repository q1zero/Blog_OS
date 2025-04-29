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
    slug = models.SlugField(_("标签别名"), max_length=50, unique=True)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)

    class Meta:
        verbose_name = _("标签")
        verbose_name_plural = _("标签")
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.name)


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
    slug = models.SlugField(_("别名"), max_length=200, unique=True)
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
        super().save(*args, **kwargs)
