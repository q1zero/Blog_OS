from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

from apps.articles.models import Article
from .models import Comment
from django import forms

# Create your views here.


class CommentForm(forms.ModelForm):
    """评论表单"""

    parent_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": _("写下你的评论..."),
                    "class": "form-control",
                }
            ),
        }


@login_required
def add_comment(request, article_slug):
    """添加评论视图"""
    article = get_object_or_404(Article, slug=article_slug)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.article = article

            # 处理回复
            parent_id = form.cleaned_data.get("parent_id")
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent_comment

            # 自动审核通过普通评论，如果是管理员则直接通过
            if request.user.is_staff:
                comment.is_approved = True

            comment.save()

            messages.success(request, _("评论已提交，等待审核通过！"))

            # 处理AJAX请求
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {"status": "success", "message": _("评论已提交，等待审核通过！")}
                )

            return redirect("articles:article_detail", article_slug=article.slug)

        # 表单验证失败
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {"status": "error", "message": _("评论提交失败，请检查内容！")}
            )

    # GET请求或表单验证失败重定向到文章详情页
    return redirect("articles:article_detail", article_slug=article.slug)


@login_required
def delete_comment(request, comment_id):
    """删除评论视图"""
    comment = get_object_or_404(Comment, id=comment_id)

    # 检查权限：必须是评论作者或管理员
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, _("您没有权限删除此评论！"))
        return redirect("articles:article_detail", article_slug=comment.article.slug)

    if request.method == "POST":
        article_slug = comment.article.slug
        comment.delete()
        messages.success(request, _("评论已成功删除！"))

        # 处理AJAX请求
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "message": _("评论已成功删除！")})

        return redirect("articles:article_detail", article_slug=article_slug)

    # GET请求显示确认页面
    return render(request, "comments/comment_confirm_delete.html", {"comment": comment})


@login_required
def review_comments(request):
    """审核评论视图"""
    if not request.user.is_staff:
        messages.error(request, _("您没有权限访问此页面！"))
        return redirect("articles:home")

    pending_comments = Comment.objects.filter(is_approved=False).order_by('-created_at')
    approved_comments = Comment.objects.filter(is_approved=True).order_by('-created_at')

    if request.method == "POST":
        comment_id = request.POST.get('comment_id')
        action = request.POST.get('action')
        comment = get_object_or_404(Comment, id=comment_id)
        
        if action == 'approve':
            comment.is_approved = True
            comment.save()
            messages.success(request, _("评论已通过审核！"))
        elif action == 'reject':
            comment.delete()
            messages.success(request, _("评论已被拒绝并删除！"))

        return redirect("comments:review_comments")

    return render(request, "comments/review_comments.html", {
        "pending_comments": pending_comments,
        "approved_comments": approved_comments
    })
