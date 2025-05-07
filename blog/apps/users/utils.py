import datetime
import os
from io import BytesIO
from PIL import Image
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import EmailVerification


def crop_and_resize_image(image_file, size=(300, 300), format='JPEG'):
    """
    裁剪并调整图片大小为正方形

    Args:
        image_file: 上传的图片文件
        size: 目标尺寸，默认为300x300
        format: 输出图片格式，默认为JPEG

    Returns:
        处理后的图片文件对象
    """
    try:
        # 打开图片
        img = Image.open(image_file)

        # 确保图片是RGB模式（去除透明通道）
        if img.mode != 'RGB':
            img = img.convert('RGB')

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

        # 调整大小
        img = img.resize(size, Image.LANCZOS)

        # 保存处理后的图片到内存中
        output = BytesIO()
        img.save(output, format=format, quality=95)
        output.seek(0)

        # 创建新的文件对象
        return InMemoryUploadedFile(
            output,
            'ImageField',
            f"{os.path.splitext(image_file.name)[0]}.jpg",
            'image/jpeg',
            output.getbuffer().nbytes,
            None
        )
    except Exception as e:
        print(f"图片处理失败: {e}")
        import traceback
        traceback.print_exc()
        return image_file  # 如果处理失败，返回原始图片


def send_verification_email(user, request=None):
    """
    发送邮箱验证邮件

    Args:
        user: 用户对象
        request: HTTP请求对象，用于构建完整URL

    Returns:
        bool: 发送成功返回True，否则返回False
    """
    try:
        print("\n===== 开始发送验证邮件 =====")
        # 使用getattr避免属性不存在的错误
        print(f"Email settings: BACKEND={settings.EMAIL_BACKEND}, HOST={getattr(settings, 'EMAIL_HOST', 'N/A')}, PORT={getattr(settings, 'EMAIL_PORT', 'N/A')}")
        print(f"FROM_EMAIL={settings.DEFAULT_FROM_EMAIL}, TO_EMAIL={user.email}")

        # 创建验证记录
        verification = EmailVerification.objects.create(
            user=user,
            expires_at=timezone.now() + datetime.timedelta(days=3)  # 3天有效期
        )
        print(f"Verification created: {verification.token}")

        # 构建验证URL
        if request:
            verify_url = request.build_absolute_uri(
                reverse('users:verify_email', kwargs={'token': verification.token})
            )
        else:
            verify_url = f"{settings.SITE_URL}{reverse('users:verify_email', kwargs={'token': verification.token})}"

        print(f"Verification URL: {verify_url}")

        # 邮件内容
        subject = '【Blog_OS】请验证您的邮箱'
        message = """
您好，

感谢您注册Blog_OS！请点击以下链接验证您的邮箱：

{verify_url}

此链接有效期为3天。如果您没有注册Blog_OS账号，请忽略此邮件。

祝好，
Blog_OS团队
""".format(verify_url=verify_url)

        print("\n----- 邮件内容 -----")
        print(f"Subject: {subject}")
        print(f"Message: \n{message}")
        print("----- 邮件内容结束 -----\n")

        # 发送邮件
        print("Sending email...")
        # 创建HTML版本的邮件内容
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>邮箱验证</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4a6ee0; color: white; padding: 10px 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .button {{ display: inline-block; background-color: #4a6ee0; color: white; text-decoration: none; padding: 10px 20px; border-radius: 4px; }}
        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Blog_OS 邮箱验证</h2>
        </div>
        <div class="content">
            <p>您好，</p>
            <p>感谢您注册 Blog_OS！请点击下面的按钮验证您的邮箱：</p>
            <p style="text-align: center;">
                <a href="{verify_url}" class="button">验证邮箱</a>
            </p>
            <p>或者复制以下链接到浏览器地址栏：</p>
            <p>{verify_url}</p>
            <p>此链接有效期为3天。如果您没有注册 Blog_OS 账号，请忽略此邮件。</p>
        </div>
        <div class="footer">
            <p>祝好，<br>Blog_OS 团队</p>
        </div>
    </div>
</body>
</html>
"""

        # 使用EmailMultiAlternatives发送纯文本和HTML邮件
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_message, "text/html")
        # 在控制台后端模式下，邮件不会真正发送，而是打印到控制台
        if 'console' in settings.EMAIL_BACKEND.lower():
            print("\n[DEBUG] 使用控制台邮件后端，邮件将打印到控制台而非真正发送")
            email.send(fail_silently=True)
        else:
            email.send(fail_silently=False)
        print(f"邮件已成功发送到: {user.email}")
        print("===== 验证邮件发送成功 =====\n")
        return True
    except Exception as e:
        import traceback
        print(f"发送邮件失败: {e}")
        traceback.print_exc()
        print("===== 验证邮件发送失败 =====\n")
        return False
