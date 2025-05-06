from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.core.exceptions import ValidationError

from apps.articles.models import Article
from apps.comments.models import Comment
from utils.models import SensitiveWord
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

    def clean_content(self):
        """检查评论内容是否包含敏感词"""
        content = self.cleaned_data.get("content")
        if content:
            try:
                # 从数据库获取所有敏感词
                sensitive_words = list(
                    SensitiveWord.objects.values_list("word", flat=True)
                )

                found_words = []
                for word in sensitive_words:
                    if word in content:
                        found_words.append(word)

                # if found_words: # 不再抛出错误
                #     raise ValidationError(
                #         _("评论包含敏感词。您的评论将需要审核。"),
                #         code="sensitive_word",
                #         params={"words": ", ".join(found_words)},
                #     )
            except SensitiveWord.DoesNotExist:
                pass
        return content


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
            content = form.cleaned_data.get("content")  # 获取内容用于检查

            # 处理回复
            parent_id = form.cleaned_data.get("parent_id")
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent_comment

            # -- 敏感词检查逻辑移到这里 --
            contains_sensitive = False
            if content:
                try:
                    sensitive_words = list(
                        SensitiveWord.objects.values_list("word", flat=True)
                    )
                    for word in sensitive_words:
                        if word in content:
                            contains_sensitive = True
                            break  # 找到一个就够了
                except SensitiveWord.DoesNotExist:
                    pass  # 如果模型不存在，则认为不包含敏感词

            # 根据是否包含敏感词设置审核状态
            if contains_sensitive:
                comment.is_approved = False
                success_message = _("评论已提交，检测到可能包含敏感内容，将进行审核。")
            else:
                comment.is_approved = True
                success_message = _("评论已成功提交！")
            # comment.is_approved = request.user.is_staff # 移除之前的逻辑

            comment.save()

            # 根据 is_approved 状态显示不同的成功消息 (已在上面设置)
            # if comment.is_approved:
            #     success_message = _("评论已成功提交！")
            # else:
            #     success_message = _("评论已提交，检测到可能包含敏感内容，将进行审核。")

            messages.success(request, success_message)

            # 处理AJAX请求
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success", "message": success_message})

            return redirect("articles:article_detail", article_slug=article.slug)

        # 表单验证失败
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # 提取表单错误信息返回给前端
            error_message = _("评论提交失败，请检查内容！")
            if form.errors:
                # 尝试获取 'content' 字段的错误，特别是敏感词错误
                content_errors = form.errors.get("content")
                if content_errors:
                    # 如果是 ValidationError 并且是我们定义的 'sensitive_word' code
                    if (
                        isinstance(content_errors.as_data()[0], ValidationError)
                        and content_errors.as_data()[0].code == "sensitive_word"
                    ):
                        error_message = (
                            content_errors.as_text()
                        )  # 使用 ValidationError 的消息
                    else:  # 其他 content 错误
                        error_message = (
                            f"{_('评论内容错误:')} {content_errors.as_text()}"
                        )
                else:  # 其他字段错误 (理论上只有content)
                    error_message = f"{_('评论提交失败:')} {form.errors.as_text()}"

            return JsonResponse(
                {
                    "status": "error",
                    "message": error_message,
                    "errors": form.errors.as_json(),
                }
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

    pending_comments = Comment.objects.filter(is_approved=False).order_by("-created_at")
    approved_comments = Comment.objects.filter(is_approved=True).order_by("-created_at")

    if request.method == "POST":
        comment_id = request.POST.get("comment_id")
        action = request.POST.get("action")
        comment = get_object_or_404(Comment, id=comment_id)

        if action == "approve":
            comment.is_approved = True
            comment.save()
            messages.success(request, _("评论已通过审核！"))
        elif action == "reject":
            comment.delete()
            messages.success(request, _("评论已被拒绝并删除！"))

        return redirect("comments:review_comments")

    return render(
        request,
        "comments/review_comments.html",
        {"pending_comments": pending_comments, "approved_comments": approved_comments},
    )
