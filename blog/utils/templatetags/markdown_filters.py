import re
from django import template
from django.utils.html import strip_tags
from django.utils.text import Truncator

register = template.Library()


@register.filter
def plain_text_preview(value, length=30):
    """
    将Markdown文本转换为纯文本预览，去除所有格式符号。
    例如：
    - "# 标题" 变成 "标题"
    - "**粗体**" 变成 "粗体"
    - "[链接](https://example.com)" 变成 "链接"
    """
    if not value:
        return ""

    # 移除链接
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)

    # 移除图片
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    # 移除标题符号
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)

    # 移除粗体、斜体
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)

    # 移除行内代码
    text = re.sub(r"`(.*?)`", r"\1", text)

    # 移除代码块
    text = re.sub(r"```[\s\S]*?```", "", text)

    # 移除引用
    text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)

    # 移除列表符号
    text = re.sub(r"^[\*\-+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)

    # 移除水平线
    text = re.sub(r"^-{3,}|^\*{3,}|^_{3,}", "", text, flags=re.MULTILINE)

    # 移除多余空格和空行
    text = re.sub(r"\n{2,}", "\n", text)
    text = text.strip()

    # 截断文本
    return Truncator(text).words(length, truncate=" ...")
