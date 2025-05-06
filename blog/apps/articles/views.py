from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import markdown
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import json
import uuid
import re
from django.db import models
from typing import Any, Optional, cast  # 添加类型提示导入

from .models import Article, Category, Tag, Like, Favorite
from django import forms

# Create your views here.


class ArticleForm(forms.ModelForm):
    """文章表单"""

    # 自定义标签字段，不直接使用模型中的多对多字段
    tags_input = forms.CharField(
        label=_("标签"),
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "输入标签，按回车添加，可添加多个标签",
            }
        ),
        help_text=_("输入标签名称并按回车确认，可添加多个标签"),
    )

    class Meta:
        model = Article
        fields = [
            "title",
            "content",
            "category",
            "status",
            "visibility",
        ]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 20}),
        }


def article_list(request, category_slug=None, tag_id=None):
    """文章列表视图，支持分类和标签过滤"""
    # 忽略类型检查器的Django ORM错误
    articles = Article.objects.filter(status="published", visibility="public")  # type: ignore

    category = None
    tag = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(category=category)

    if tag_id:
        tag = get_object_or_404(Tag, id=tag_id)
        articles = articles.filter(tags__in=[tag])

    # 分页
    paginator = Paginator(articles, 10)  # 每页显示10篇文章
    page = request.GET.get("page")
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # 如果page参数不是整数，显示第一页
        articles = paginator.page(1)
    except EmptyPage:
        # 如果page参数超出范围，显示最后一页
        articles = paginator.page(paginator.num_pages)

    # 获取所有分类和标签，用于侧边栏
    categories = Category.objects.all()  # type: ignore
    # 只获取至少关联了一篇文章的标签
    tags = Tag.objects.annotate(articles_count=models.Count("articles")).filter(  # type: ignore
        articles_count__gt=0
    )

    return render(
        request,
        "articles/list.html",
        {
            "articles": articles,
            "category": category,
            "tag": tag,
            "page": page,
            "categories": categories,
            "tags": tags,
        },
    )


@login_required
def my_published_articles(request):
    """显示当前用户的已发布文章，包括公开和私密"""
    # 获取当前用户的已发布文章，不论可见性
    articles = Article.objects.filter(author=request.user, status="published")  # type: ignore

    # 分页
    paginator = Paginator(articles, 10)  # 每页显示10篇文章
    page = request.GET.get("page")
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # 如果page参数不是整数，显示第一页
        articles = paginator.page(1)
    except EmptyPage:
        # 如果page参数超出范围，显示最后一页
        articles = paginator.page(paginator.num_pages)

    # 获取所有分类和标签，用于侧边栏
    categories = Category.objects.all()  # type: ignore
    # 只获取至少关联了一篇文章的标签
    tags = Tag.objects.annotate(articles_count=models.Count("articles")).filter(  # type: ignore
        articles_count__gt=0
    )

    return render(
        request,
        "articles/list.html",
        {
            "articles": articles,
            "page": page,
            "categories": categories,
            "tags": tags,
            "is_my_articles": True,  # 用于模板中区分是否是我的文章视图
            "view_type": "published",  # 用于区分是已发布文章视图
        },
    )


@login_required
def my_draft_articles(request):
    """显示当前用户的草稿文章"""
    # 获取当前用户的草稿文章
    articles = Article.objects.filter(author=request.user, status="draft")  # type: ignore

    # 分页
    paginator = Paginator(articles, 10)  # 每页显示10篇文章
    page = request.GET.get("page")
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # 如果page参数不是整数，显示第一页
        articles = paginator.page(1)
    except EmptyPage:
        # 如果page参数超出范围，显示最后一页
        articles = paginator.page(paginator.num_pages)

    # 获取所有分类和标签，用于侧边栏
    categories = Category.objects.all()  # type: ignore
    # 只获取至少关联了一篇文章的标签
    tags = Tag.objects.annotate(articles_count=models.Count("articles")).filter(  # type: ignore
        articles_count__gt=0
    )

    return render(
        request,
        "articles/list.html",
        {
            "articles": articles,
            "page": page,
            "categories": categories,
            "tags": tags,
            "is_my_articles": True,  # 用于模板中区分是否是我的文章视图
            "view_type": "draft",  # 用于区分是草稿文章视图
        },
    )


def generate_unique_slug(tag_name):
    """生成唯一的标签slug，确保中文标签也能有有效的slug"""
    # 尝试使用slugify处理
    tag_slug = slugify(tag_name)

    # 如果slugify后为空（例如纯中文标签），则使用随机字符串
    if not tag_slug:
        # 提取首字母或数字作为前缀
        prefix = "".join(re.findall(r"[a-zA-Z0-9]", tag_name))
        if not prefix:
            prefix = "tag"  # 如果没有提取到任何字母或数字，使用默认前缀

        # 添加随机字符串作为后缀
        random_suffix = str(uuid.uuid4())[:8]
        tag_slug = f"{prefix}-{random_suffix}"

    # 检查是否已存在相同的slug
    counter = 1
    original_slug = tag_slug
    while Tag.objects.filter(slug=tag_slug).exists():  # type: ignore
        # 如果已存在，添加数字后缀
        tag_slug = f"{original_slug}-{counter}"
        counter += 1

    return tag_slug


def article_detail(request, article_slug):
    """文章详情视图"""
    article = get_object_or_404(Article, slug=article_slug)

    # 检查是否是文章作者，如果不是，则只能查看已发布且公开的文章
    if article.author != request.user:
        if article.status != "published" or article.visibility != "public":
            messages.error(request, _("您无权查看此文章！"))
            return redirect("articles:article_list")

    # 增加文章浏览量
    # 使用session避免刷新页面重复增加浏览量
    session_key = f"viewed_article_{article.pk}"
    if not request.session.get(session_key, False):
        article.increase_views()
        # 设置session标记，使得在一段时间内不重复计数
        request.session[session_key] = True
        # 设置过期时间为30分钟
        request.session.set_expiry(1800)

    # 使用Markdown渲染文章内容
    md = markdown.Markdown(
        extensions=[
            "markdown.extensions.extra",
            "markdown.extensions.codehilite",
            TocExtension(slugify=slugify),
        ]
    )
    article.content = md.convert(article.content)

    # 为文章添加目录属性 - 使用类型忽略注解
    # 在Python中，动态添加的属性不会被类型检查器识别，使用setattr避免这个问题
    toc_value = ""
    if hasattr(md, "toc"):  # type: ignore
        toc_value = md.toc  # type: ignore
    setattr(article, "toc", toc_value)

    # 获取相关文章（同一分类或有共同标签的文章）
    if article.category:
        related_articles = Article.objects.filter(  # type: ignore
            category=article.category, status="published", visibility="public"
        ).exclude(pk=article.pk)[:5]
    else:
        # 如果没有分类，尝试通过标签获取相关文章
        related_articles = (
            Article.objects.filter(  # type: ignore
                tags__in=article.tags.all(), status="published", visibility="public"
            )
            .exclude(pk=article.pk)
            .distinct()[:5]
        )

    # 获取文章评论列表
    from apps.comments.models import Comment

    comments = Comment.objects.filter(  # type: ignore
        article=article, parent=None, is_approved=True
    ).select_related("author")

    # 为评论创建表单
    from apps.comments.views import CommentForm

    comment_form = CommentForm()

    # 检查当前用户是否已经点赞和收藏
    user_liked = False
    user_favorited = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, article=article).exists()  # type: ignore
        user_favorited = Favorite.objects.filter(  # type: ignore
            user=request.user, article=article
        ).exists()

    return render(
        request,
        "articles/detail.html",
        {
            "article": article,
            "related_articles": related_articles,
            "user_liked": user_liked,
            "user_favorited": user_favorited,
            "comments": comments,
            "comment_form": comment_form,
        },
    )


def home(request):
    """首页视图，展示最新发布的文章"""
    # 获取已发布且公开的文章，按发布时间排序
    latest_articles = Article.objects.filter(  # type: ignore
        status="published", visibility="public"
    ).order_by("-published_at")[:8]  # 显示最新的8篇文章

    # 获取所有分类和标签，用于侧边栏
    categories = Category.objects.all()  # type: ignore
    # 只获取至少关联了一篇文章的标签
    tags = Tag.objects.annotate(articles_count=models.Count("articles")).filter(  # type: ignore
        articles_count__gt=0
    )

    return render(
        request,
        "articles/home.html",
        {
            "latest_articles": latest_articles,
            "categories": categories,
            "tags": tags,
        },
    )


@login_required
def article_create(request):
    """文章创建视图，要求用户登录"""
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            # 自动关联当前登录用户为作者
            article.author = request.user
            article.save()

            # 处理标签输入
            tags_input = form.cleaned_data.get("tags_input", "")
            if tags_input:
                try:
                    # 尝试解析可能的JSON格式
                    tags_data = json.loads(tags_input)
                    # 如果是Tagify输出的格式，提取标签值
                    tag_names = [
                        tag.get("value", "").strip()
                        for tag in tags_data
                        if tag.get("value", "").strip()
                    ]
                except (json.JSONDecodeError, TypeError, AttributeError):
                    # 如果不是JSON或解析失败，按传统方式处理（逗号分隔）
                    tag_names = [t.strip() for t in tags_input.split(",") if t.strip()]

                # 为每个标签名称创建或获取标签实例
                for tag_name in tag_names:
                    # 获取或创建标签
                    tag, created = Tag.objects.get_or_create(name=tag_name)  # type: ignore

                    # 如果是新创建的标签，需要保存让其生成ID后自动设置slug
                    if created:
                        tag.save()

                    # 添加标签到文章
                    article.tags.add(tag)

            messages.success(request, _("文章创建成功！"))
            return redirect("articles:article_detail", article_slug=article.slug)
    else:
        form = ArticleForm()

    categories = Category.objects.all()  # type: ignore
    # 只获取至少关联了一篇文章的标签
    tags = Tag.objects.annotate(articles_count=models.Count("articles")).filter(  # type: ignore
        articles_count__gt=0
    )

    return render(
        request,
        "articles/article_form.html",
        {"form": form, "categories": categories, "tags": tags, "is_create": True},
    )


@login_required
def article_update(request, article_slug):
    """文章更新视图，要求用户登录"""
    # 获取文章，管理员可以编辑所有文章，普通用户只能编辑自己的文章
    if request.user.is_staff:
        article = get_object_or_404(Article, slug=article_slug)
    else:
        article = get_object_or_404(Article, slug=article_slug, author=request.user)

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            # 如果发布状态变更为已发布，设置发布时间
            if article.status == "published" and not article.published_at:
                article.published_at = timezone.now()
            article.save()

            # 处理标签输入
            tags_input = form.cleaned_data.get("tags_input", "")
            if tags_input:
                # 先清除现有标签
                article.tags.clear()

                try:
                    # 尝试解析可能的JSON格式
                    tags_data = json.loads(tags_input)
                    # 如果是Tagify输出的格式，提取标签值
                    tag_names = [
                        tag.get("value", "").strip()
                        for tag in tags_data
                        if tag.get("value", "").strip()
                    ]
                except (json.JSONDecodeError, TypeError, AttributeError):
                    # 如果不是JSON或解析失败，按传统方式处理（逗号分隔）
                    tag_names = [t.strip() for t in tags_input.split(",") if t.strip()]

                # 为每个标签名称创建或获取标签实例
                for tag_name in tag_names:
                    # 获取或创建标签
                    tag, created = Tag.objects.get_or_create(name=tag_name)  # type: ignore

                    # 如果是新创建的标签，需要保存让其生成ID后自动设置slug
                    if created:
                        tag.save()

                    # 添加标签到文章
                    article.tags.add(tag)

            messages.success(request, _("文章更新成功！"))
            return redirect("articles:article_detail", article_slug=article.slug)
    else:
        # 将现有标签格式化为简单的逗号分隔字符串，不使用JSON格式
        existing_tags = ", ".join([tag.name for tag in article.tags.all()])
        form = ArticleForm(instance=article, initial={"tags_input": existing_tags})

    categories = Category.objects.all()  # type: ignore
    # 只获取至少关联了一篇文章的标签
    tags = Tag.objects.annotate(articles_count=models.Count("articles")).filter(  # type: ignore
        articles_count__gt=0
    )

    return render(
        request,
        "articles/article_form.html",
        {
            "form": form,
            "article": article,
            "categories": categories,
            "tags": tags,
            "is_create": False,
        },
    )


@login_required
def article_delete(request, article_slug):
    """文章删除视图，要求用户登录"""
    # 获取文章，管理员可以删除所有文章，普通用户只能删除自己的文章
    if request.user.is_staff:
        article = get_object_or_404(Article, slug=article_slug)
    else:
        article = get_object_or_404(Article, slug=article_slug, author=request.user)

    if request.method == "POST":
        article.delete()
        messages.success(request, _("文章已成功删除！"))
        return redirect("articles:article_list")

    return render(request, "articles/article_confirm_delete.html", {"article": article})


@login_required
def toggle_like(request, article_slug):
    """切换文章点赞状态"""
    article = get_object_or_404(Article, slug=article_slug)
    user = request.user

    # 检查用户是否已经点赞过该文章
    like, created = Like.objects.get_or_create(user=user, article=article)  # type: ignore

    # 如果已经点赞，则取消点赞
    if not created:
        like.delete()
        action = "unlike"
        message = _("已取消点赞！")
    else:
        action = "like"
        message = _("点赞成功！")

    # 如果是AJAX请求，返回JSON响应
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        from django.http import JsonResponse

        likes_count = Like.objects.filter(article=article).count()  # type: ignore
        return JsonResponse(
            {
                "status": "success",
                "action": action,
                "message": message,
                "likes_count": likes_count,
            }
        )

    # 如果是普通请求，添加消息并重定向
    messages.success(request, message)
    return redirect("articles:article_detail", article_slug=article.slug)


@login_required
def toggle_favorite(request, article_slug):
    """切换文章收藏状态"""
    article = get_object_or_404(Article, slug=article_slug)
    user = request.user

    # 检查用户是否已经收藏过该文章
    favorite, created = Favorite.objects.get_or_create(user=user, article=article)  # type: ignore

    # 如果已经收藏，则取消收藏
    if not created:
        favorite.delete()
        action = "unfavorite"
        message = _("已取消收藏！")
    else:
        action = "favorite"
        message = _("收藏成功！")

    # 如果是AJAX请求，返回JSON响应
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        from django.http import JsonResponse

        favorites_count = Favorite.objects.filter(article=article).count()  # type: ignore
        return JsonResponse(
            {
                "status": "success",
                "action": action,
                "message": message,
                "favorites_count": favorites_count,
            }
        )

    # 如果是普通请求，添加消息并重定向
    messages.success(request, message)
    return redirect("articles:article_detail", article_slug=article.slug)


@login_required
def publish_article(request, article_slug):
    """发布草稿文章"""
    article = get_object_or_404(Article, slug=article_slug, author=request.user)

    if article.status == "draft":
        article.status = "published"
        if not article.published_at:
            article.published_at = timezone.now()
        article.save()
        messages.success(request, _("文章已成功发布！"))
    else:
        messages.info(request, _("文章已经是发布状态！"))

    return redirect("articles:article_detail", article_slug=article.slug)
