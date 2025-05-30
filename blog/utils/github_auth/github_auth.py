"""
GitHub认证工具
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.utils.http import urlencode
from django.http import HttpResponseRedirect
from django.core.files.base import ContentFile
import requests
import json
import os
import uuid
from io import BytesIO
from PIL import Image

from apps.users.utils import crop_and_resize_image


def github_login(request):
    """
    GitHub登录视图
    """
    try:
        # 检查配置
        if not hasattr(settings, "SOCIALACCOUNT_PROVIDERS"):
            raise Exception("SOCIALACCOUNT_PROVIDERS配置不存在")

        if "github" not in settings.SOCIALACCOUNT_PROVIDERS:
            raise Exception("GitHub配置不存在")

        if "APP" not in settings.SOCIALACCOUNT_PROVIDERS["github"]:
            raise Exception("GitHub APP配置不存在")

        # 构建GitHub登录URL
        github_config = settings.SOCIALACCOUNT_PROVIDERS["github"]
        app_config = github_config["APP"]

        client_id = app_config.get("client_id")
        if not client_id:
            raise Exception("GitHub client_id不存在或为空")

        # 获取当前请求的域名和协议
        scheme = request.scheme
        host = request.get_host()

        # 计算当前请求的回调URL，强制使用HTTPS
        # 即使当前请求是HTTP，也使用HTTPS版本的回调URL
        current_callback_url = f"https://{host}/accounts/github/callback"

        # 如果当前是在本地开发环境（127.0.0.1或localhost），则使用HTTP
        if host.startswith("127.0.0.1") or host.startswith("localhost"):
            current_callback_url = f"http://{host}/accounts/github/callback"

        # 获取配置中的回调URL
        if (
            hasattr(settings, "GITHUB_CALLBACK_URLS")
            and current_callback_url in settings.GITHUB_CALLBACK_URLS
        ):
            # 如果当前回调URL在配置的列表中，使用它
            callback_url = current_callback_url
            print(f"使用当前域名的回调URL（强制HTTPS）: {callback_url}")
        elif hasattr(settings, "GITHUB_CALLBACK_URL"):
            # 否则使用默认配置的回调URL
            callback_url = settings.GITHUB_CALLBACK_URL
            print(f"使用默认配置的回调URL: {callback_url}")
        else:
            # 如果没有配置，使用当前域名（可能不工作，但至少尝试）
            callback_url = current_callback_url
            print(
                f"警告：未在settings.py中找到GITHUB_CALLBACK_URL配置，尝试使用当前域名（强制HTTPS）: {callback_url}"
            )

        # 构建GitHub OAuth URL
        github_auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={callback_url}&scope=user:email"

        # 打印调试信息
        print(f"GitHub登录请求: {request.path}")
        print(f"Client ID: {client_id}")
        print(f"回调URL: {callback_url}")
        print(f"完整URL: {github_auth_url}")
        print(f"注意: 用户授权后将直接登录，无需原生登录")

        # 打印最终的URL
        print(f"最终的GitHub授权URL: {github_auth_url}")

        # 直接使用HttpResponseRedirect进行重定向
        # 这应该能解决重定向问题
        return HttpResponseRedirect(github_auth_url)
    except Exception as e:
        error_msg = f"GitHub登录错误: {str(e)}"
        print(error_msg)
        messages.error(request, error_msg)
        return redirect("users:login")


def github_callback(request):
    """
    GitHub登录回调视图 - 实现用户授权后直接登录
    """
    try:
        # 打印调试信息
        print(f"GitHub回调请求: {request.path}")
        print(f"请求参数: {request.GET}")

        # 检查错误
        error = request.GET.get("error")
        if error:
            error_description = request.GET.get("error_description", "")
            error_msg = f"GitHub授权错误: {error} - {error_description}"
            print(error_msg)
            messages.error(request, error_msg)
            return redirect("users:login")

        # 获取授权码
        code = request.GET.get("code")
        if not code:
            error_msg = "未收到GitHub授权码"
            print(error_msg)
            messages.error(request, error_msg)
            return redirect("users:login")

        # 打印成功信息
        print(f"成功收到GitHub授权码: {code}")

        # 使用授权码获取访问令牌和用户信息
        try:
            # 获取GitHub应用配置
            github_config = settings.SOCIALACCOUNT_PROVIDERS["github"]
            app_config = github_config["APP"]
            client_id = app_config.get("client_id")
            client_secret = app_config.get("secret")

            # 使用授权码获取访问令牌
            access_token = get_github_access_token(code, client_id, client_secret)
            if not access_token:
                raise Exception("无法获取GitHub访问令牌")

            # 使用访问令牌获取GitHub用户信息
            github_user = get_github_user_info(access_token)
            if not github_user:
                raise Exception("无法获取GitHub用户信息")

            # 打印GitHub用户信息
            print(f"GitHub用户信息: {github_user}")

            # 导入必要的模型和工具
            from django.contrib.auth import login, get_user_model, authenticate
            from django.contrib.auth.backends import ModelBackend

            # 获取用户模型
            User = get_user_model()

            # 使用GitHub用户ID作为唯一标识
            github_id = str(github_user.get("id"))
            username = f"github_{github_id}"

            # 获取GitHub用户的名称和邮箱
            name = github_user.get("name") or github_user.get("login") or username
            email = github_user.get("email") or f"{username}@github.com"

            # 检查用户是否已存在，如果不存在则创建
            try:
                user = User.objects.get(username=username)
                print(f"用户已存在: {username}")

                # 为已存在的用户更新GitHub头像
                try:
                    # 获取GitHub头像URL
                    avatar_url = github_user.get("avatar_url")
                    if avatar_url:
                        print(f"更新GitHub头像: {avatar_url}")
                        # 下载头像
                        avatar_response = requests.get(avatar_url)
                        if avatar_response.status_code == 200:
                            # 保存头像
                            avatar_content = avatar_response.content
                            # 使用PIL处理头像
                            img_io = BytesIO(avatar_content)
                            # 使用我们现有的裁剪和调整大小函数
                            processed_image = crop_and_resize_image(img_io)

                            # 如果用户已有自定义头像（不是默认头像），则不覆盖
                            if (
                                not user.avatar
                                or user.avatar.name == "avatars/test.jpg"
                            ):
                                # 随机文件名，避免冲突
                                image_name = (
                                    f"github_{github_id}_{uuid.uuid4().hex[:8]}.jpg"
                                )
                                # 设置用户头像
                                user.avatar.save(image_name, processed_image, save=True)
                                print(f"已更新GitHub头像: {image_name}")
                except Exception as e:
                    print(f"更新GitHub头像失败: {str(e)}")
            except User.DoesNotExist:
                # 创建新用户
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=None,  # 不设置密码，因为用户将使用GitHub登录
                )
                # 设置用户的名字
                user.first_name = name
                user.set_unusable_password()  # 设置为不可用的密码

                # 设置GitHub头像
                try:
                    # 获取GitHub头像URL
                    avatar_url = github_user.get("avatar_url")
                    if avatar_url:
                        print(f"下载GitHub头像: {avatar_url}")
                        # 下载头像
                        avatar_response = requests.get(avatar_url)
                        if avatar_response.status_code == 200:
                            # 保存头像
                            avatar_content = avatar_response.content
                            # 使用PIL处理头像
                            img_io = BytesIO(avatar_content)
                            # 使用我们现有的裁剪和调整大小函数
                            processed_image = crop_and_resize_image(img_io)

                            # 随机文件名，避免冲突
                            image_name = (
                                f"github_{github_id}_{uuid.uuid4().hex[:8]}.jpg"
                            )
                            # 设置用户头像
                            user.avatar.save(image_name, processed_image, save=False)
                            print(f"已设置GitHub头像: {image_name}")
                except Exception as e:
                    print(f"设置GitHub头像失败: {str(e)}")
                    # 如果设置头像失败，将使用默认头像

                user.save()
                print(f"创建新用户: {username}, 名称: {name}, 邮箱: {email}")

            # 登录用户，指定使用ModelBackend
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            # 设置成功消息
            success_msg = f"使用GitHub账号登录成功！欢迎回来，{name}"
            messages.success(request, success_msg)

            # 直接重定向到首页，而不是显示中间成功页面
            return redirect("home")

        except Exception as e:
            error_msg = f"GitHub登录处理错误: {str(e)}"
            print(error_msg)
            messages.error(request, error_msg)
            return redirect("users:login")
    except Exception as e:
        error_msg = f"GitHub回调错误: {str(e)}"
        print(error_msg)
        messages.error(request, error_msg)
        return redirect("users:login")


def get_github_user_info(access_token):
    """
    使用访问令牌获取GitHub用户信息
    """
    try:
        # 设置请求头
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/json",
        }

        # 发送请求获取用户信息
        response = requests.get("https://api.github.com/user", headers=headers)

        # 检查响应状态
        if response.status_code == 200:
            user_data = response.json()
            return user_data
        else:
            print(f"GitHub API请求失败: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"获取GitHub用户信息错误: {str(e)}")
        return None


def get_github_access_token(code, client_id, client_secret):
    """
    使用授权码获取GitHub访问令牌
    """
    try:
        # 设置请求参数
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
        }

        # 设置请求头
        headers = {
            "Accept": "application/json",
        }

        # 发送请求获取访问令牌
        response = requests.post(
            "https://github.com/login/oauth/access_token",
            params=params,
            headers=headers,
        )

        # 检查响应状态
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                return data["access_token"]
            else:
                print(f"GitHub访问令牌响应中没有access_token: {data}")
                return None
        else:
            print(f"GitHub访问令牌请求失败: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"获取GitHub访问令牌错误: {str(e)}")
        return None


def setup_github_app():
    """
    设置GitHub应用配置
    """
    try:
        # 获取Site对象
        site = Site.objects.get(id=settings.SITE_ID)
        print(f"Site: {site.domain}, {site.name}")

        # 检查是否已存在GitHub应用配置
        if SocialApp.objects.filter(provider="github").exists():
            print("已存在GitHub应用配置，跳过创建")
            return

        # 创建新的GitHub应用配置
        if (
            hasattr(settings, "SOCIALACCOUNT_PROVIDERS")
            and "github" in settings.SOCIALACCOUNT_PROVIDERS
        ):
            github_config = settings.SOCIALACCOUNT_PROVIDERS["github"]
            if "APP" in github_config:
                app_config = github_config["APP"]
                client_id = app_config.get("client_id", "")
                secret = app_config.get("secret", "")
                key = app_config.get("key", "")

                if client_id and secret:
                    github_app = SocialApp.objects.create(
                        provider="github",
                        name="GitHub",
                        client_id=client_id,
                        secret=secret,
                        key=key,
                    )
                    github_app.sites.add(site)
                    print(
                        f"已创建新的GitHub应用配置: ID={github_app.id}, Name={github_app.name}, Client ID={github_app.client_id}"
                    )
                    return True
                else:
                    print("Client ID或Secret为空，无法创建GitHub应用配置")
            else:
                print("settings中未找到GitHub APP配置")
        else:
            print("settings中未找到GitHub配置")
        return False
    except Exception as e:
        print(f"设置GitHub应用配置错误: {str(e)}")
        return False
