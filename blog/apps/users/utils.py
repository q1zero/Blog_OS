import datetime
import os
import uuid
from io import BytesIO
from PIL import Image
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import EmailVerification

# 导入Celery异步任务处理器
from utils.celery.handlers import (
    send_verification_email as send_verification_email_async,
)


def crop_and_resize_image(image_file, size=(300, 300), format="JPEG"):
    """
    裁剪并调整图片大小为正方形

    Args:
        image_file: 上传的图片文件
        size: 目标尺寸，默认为300x300
        format: 输出图片格式，默认为JPEG

    Returns:
        处理后的图片文件对象
    """
    # 检查是否为BytesIO对象并添加调试信息
    is_bytesio = isinstance(image_file, BytesIO)
    if is_bytesio:
        print(f"处理BytesIO对象，长度: {image_file.getbuffer().nbytes}字节")
    else:
        print(f"处理文件对象: {getattr(image_file, 'name', '未知名称')}")

    try:
        # 打开图片
        img = Image.open(image_file)

        # 确保图片是RGB模式（去除透明通道）
        if img.mode != "RGB":
            img = img.convert("RGB")

        # 获取原始尺寸
        width, height = img.size

        # 计算裁剪区域（居中裁剪为正方形）
        if width > height:
            # 宽图，裁剪左右两侧
            left = (width - height) // 2
            top = 0
            right = left + height
            bottom = height
        else:
            # 长图，裁剪上下两侧
            left = 0
            top = (height - width) // 2
            right = width
            bottom = top + width

        # 裁剪为正方形
        img = img.crop((left, top, right, bottom))

        # 调整大小（使用3=BICUBIC，兼容性更好）
        img = img.resize(size, 3)  # 3 是 BICUBIC 的值

        # 保存处理后的图片到内存中
        output = BytesIO()
        img.save(output, format=format, quality=95)
        output.seek(0)

        # 创建新的文件对象
        # 为文件名生成逻辑添加对BytesIO对象的支持
        if hasattr(image_file, "name"):
            # 如果有name属性，使用原始文件名
            filename = f"{os.path.splitext(image_file.name)[0]}.jpg"
            print(f"使用原始文件名: {filename}")
        else:
            # 对于没有name属性的对象（如BytesIO），生成一个默认文件名
            filename = f"image_{uuid.uuid4().hex[:8]}.jpg"
            print(f"为BytesIO对象生成随机文件名: {filename}")

        return InMemoryUploadedFile(
            output,
            "ImageField",
            filename,
            "image/jpeg",
            output.getbuffer().nbytes,
            None,
        )
    except Exception as e:
        print(f"图片处理失败: {e}")
        import traceback

        traceback.print_exc()

        # 更详细的错误信息
        if isinstance(image_file, BytesIO):
            print(f"BytesIO对象处理失败，返回原始对象")
        else:
            print(
                f"文件对象处理失败，返回原始对象: {getattr(image_file, 'name', '未知')}"
            )

        return image_file  # 如果处理失败，返回原始图片


def send_verification_email(user, request=None):
    """
    发送邮箱验证邮件（使用Celery异步处理）

    Args:
        user: 用户对象
        request: HTTP请求对象，用于构建完整URL

    Returns:
        bool: 发送成功返回True，否则返回False
    """
    try:
        print("\n===== 开始准备发送验证邮件 =====")
        print(
            f"Email settings: BACKEND={settings.EMAIL_BACKEND}, HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}"
        )
        print(f"FROM_EMAIL={settings.DEFAULT_FROM_EMAIL}, TO_EMAIL={user.email}")

        # 创建验证记录
        verification = EmailVerification.objects.create(
            user=user,
            expires_at=timezone.now() + datetime.timedelta(days=3),  # 3天有效期
        )
        print(f"Verification created: {verification.token}")

        # 构建站点URL
        if request:
            site_url = request.build_absolute_uri("/").rstrip("/")
        else:
            site_url = settings.SITE_URL

        print(f"Site URL: {site_url}")

        # 使用Celery异步发送邮件
        send_verification_email_async(user, verification.token, site_url)

        print("邮件发送任务已加入队列")
        print("===== 验证邮件准备完成 =====\n")

        return True
    except Exception as e:
        import traceback

        print(f"准备发送邮件失败: {e}")
        traceback.print_exc()
        print("===== 验证邮件发送失败 =====\n")
        return False
