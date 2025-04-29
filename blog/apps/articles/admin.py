from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Article, Category, Tag

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "status",
        "visibility",
        "created_at",
        "published_at",
    )
    list_filter = (
        "status",
        "visibility",
        "created_at",
        "published_at",
        "category",
        "tags",
    )
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    filter_horizontal = ("tags",)
    raw_id_fields = ("author",)
    fieldsets = (
        (None, {"fields": ("title", "slug", "author", "content")}),
        (_("分类和标签"), {"fields": ("category", "tags")}),
        (_("状态"), {"fields": ("status", "visibility", "published_at")}),
    )
