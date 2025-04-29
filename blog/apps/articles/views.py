from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import markdown
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify

from .models import Article, Category, Tag

# Create your views here.


def article_list(request, category_slug=None, tag_slug=None):
    """文章列表视图，支持分类和标签过滤"""
    articles = Article.objects.filter(status="published", visibility="public")

    category = None
    tag = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(category=category)

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
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
    categories = Category.objects.all()
    tags = Tag.objects.all()

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


def article_detail(request, article_slug):
    """文章详情视图"""
    article = get_object_or_404(
        Article, slug=article_slug, status="published", visibility="public"
    )

    # 使用Markdown渲染文章内容
    md = markdown.Markdown(
        extensions=[
            "markdown.extensions.extra",
            "markdown.extensions.codehilite",
            TocExtension(slugify=slugify),
        ]
    )
    article.content = md.convert(article.content)

    # 为文章添加目录属性
    article.toc = md.toc if hasattr(md, "toc") else ""

    # 获取相关文章（同一分类或有共同标签的文章）
    if article.category:
        related_articles = Article.objects.filter(
            category=article.category, status="published", visibility="public"
        ).exclude(id=article.id)[:5]
    else:
        # 如果没有分类，尝试通过标签获取相关文章
        related_articles = (
            Article.objects.filter(
                tags__in=article.tags.all(), status="published", visibility="public"
            )
            .exclude(id=article.id)
            .distinct()[:5]
        )

    return render(
        request,
        "articles/detail.html",
        {
            "article": article,
            "related_articles": related_articles,
        },
    )


def home(request):
    """首页视图，展示最新发布的文章"""
    # 获取已发布且公开的文章，按发布时间排序
    latest_articles = Article.objects.filter(
        status="published", visibility="public"
    ).order_by("-published_at")[:8]  # 显示最新的8篇文章

    # 获取所有分类和标签，用于侧边栏
    categories = Category.objects.all()
    tags = Tag.objects.all()

    return render(
        request,
        "articles/home.html",
        {
            "latest_articles": latest_articles,
            "categories": categories,
            "tags": tags,
        },
    )
