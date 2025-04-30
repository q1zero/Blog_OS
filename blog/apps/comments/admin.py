from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Comment

# Register your models here.


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "article", "content_preview", "created_at", "is_approved")
    list_filter = ("is_approved", "created_at")
    search_fields = ("content", "author__username", "article__title")
    actions = ["approve_comments", "disapprove_comments"]
    date_hierarchy = "created_at"

    def content_preview(self, obj):
        """显示评论内容预览"""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = _("评论内容预览")

    def approve_comments(self, request, queryset):
        """批量审核通过评论"""
        queryset.update(is_approved=True)

    approve_comments.short_description = _("审核通过选中的评论")

    def disapprove_comments(self, request, queryset):
        """批量取消审核通过评论"""
        queryset.update(is_approved=False)

    disapprove_comments.short_description = _("取消审核通过选中的评论")
