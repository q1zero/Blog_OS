from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, UpdateView
from django.http import HttpResponseRedirect, Http404
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .forms import UserRegisterForm, UserLoginForm, UserProfileForm, UserAvatarForm
from .models import User, EmailVerification
from .utils import send_verification_email, crop_and_resize_image
from apps.articles.models import Article


def register(request):
    """用户注册视图"""
    if request.user.is_authenticated:
        return redirect('articles:article_list')

    if request.method == 'POST':
        try:
            print("\n===== 开始处理注册请求 =====")
            print(f"POST data: {request.POST}")

            # 预处理：检查用户名是否已存在
            username = request.POST.get('username')
            if User.objects.filter(username=username).exists():
                print(f"Username '{username}' already exists")
                # 如果用户名已存在，删除未激活的用户
                inactive_users = User.objects.filter(username=username, is_active=False)
                if inactive_users.exists():
                    for user in inactive_users:
                        print(f"Deleting inactive user: {user.username}")
                        user.delete()

            # 创建表单并验证
            form = UserRegisterForm(request.POST)
            is_valid = form.is_valid()
            print(f"Form is valid: {is_valid}")

            if not is_valid:
                print(f"Form errors: {form.errors}")
                return render(request, 'users/register.html', {'form': form})

            # 保存用户
            user = form.save(commit=False)
            user.is_active = False  # 默认设置为非激活状态，等待邮箱验证
            user.save()
            print(f"User created: {user.username}, {user.email}, active: {user.is_active}")

            # 发送验证邮件
            email_sent = send_verification_email(user, request)
            print(f"Email sent: {email_sent}")

            if email_sent:
                messages.success(
                    request,
                    _('注册成功！我们已向您的邮箱发送了验证链接，请点击链接激活您的账号。')
                )
                print("===== 注册成功，重定向到注册完成页面 =====\n")
                return redirect('users:register_done')
            else:
                # 如果邮件发送失败，删除用户
                user.delete()
                print(f"Deleted user due to email sending failure: {username}")
                messages.error(request, _('邮件发送失败，请重试。'))
        except Exception as e:
            print(f"Error during registration: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, _('注册过程中出现错误，请重试。'))
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


def register_done(request):
    """注册完成视图"""
    return render(request, 'users/register_done.html')


def verify_email(request, token):
    """邮箱验证视图"""
    try:
        verification = get_object_or_404(EmailVerification, token=token)

        # 检查验证是否有效
        if verification.is_valid():
            user = verification.user
            user.is_active = True
            user.save()

            verification.verified = True
            verification.save()

            # 自动登录用户
            login(request, user)

            messages.success(request, _('邮箱验证成功！您的账号已激活。'))
            return redirect('articles:article_list')
        else:
            if verification.verified:
                messages.error(request, _('此验证链接已被使用。'))
            else:
                messages.error(request, _('验证链接已过期。'))
            return redirect('users:resend_verification')

    except Http404:
        messages.error(request, _('无效的验证链接。'))
        return redirect('users:login')


def resend_verification(request):
    """重新发送验证邮件视图"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
            # 删除旧的验证记录
            user.email_verifications.filter(verified=False).delete()
            # 发送新的验证邮件
            send_verification_email(user, request)
            messages.success(request, _('验证邮件已重新发送，请检查您的邮箱。'))
            return redirect('users:login')
        except User.DoesNotExist:
            messages.error(request, _('没有找到与此邮箱关联的未激活账号。'))

    return render(request, 'users/resend_verification.html')


class UserLoginView(LoginView):
    """用户登录视图"""
    form_class = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """登录成功后的处理"""
        messages.success(self.request, _('登录成功！欢迎回来！'))
        return super().form_valid(form)


@login_required
def user_logout(request):
    """用户登出视图"""
    logout(request)
    messages.success(request, _('您已成功登出！'))
    return redirect('articles:article_list')


class UserProfileView(LoginRequiredMixin, DetailView):
    """用户个人信息展示视图"""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    """用户个人信息编辑视图"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, _('个人信息更新成功！'))
        return reverse('users:profile', kwargs={'username': self.request.user.username})


@login_required
def change_avatar(request):
    """更改用户头像，并裁剪为正方形"""
    if request.method == 'POST':
        form = UserAvatarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # 如果有新头像上传
            if 'avatar' in request.FILES:
                # 裁剪并调整图片大小
                print(f"Processing avatar image: {request.FILES['avatar'].name}")
                processed_image = crop_and_resize_image(request.FILES['avatar'])

                # 将处理后的图片设置为用户头像
                user = form.save(commit=False)
                user.avatar = processed_image
                user.save()

                print(f"Avatar updated successfully: {user.avatar.name}")
                messages.success(request, _('头像更新成功！'))
            else:
                form.save()
                messages.success(request, _('信息更新成功！'))

            return redirect('users:profile', username=request.user.username)
    else:
        form = UserAvatarForm(instance=request.user)

    return render(request, 'users/change_avatar.html', {'form': form})


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """用户密码修改视图"""
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:password_change_done')


@login_required
def password_change_done(request):
    """密码修改成功视图"""
    messages.success(request, _('密码修改成功！'))
    return redirect('users:profile', username=request.user.username)


def search(request):
    """搜索功能视图，支持搜索作者和文章"""
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')

    authors = []
    articles = []

    if query:
        # 根据搜索类型执行不同的查询
        if search_type == 'author' or search_type == 'all':
            # 搜索作者
            authors = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(bio__icontains=query)
            ).distinct()

        if search_type == 'article' or search_type == 'all':
            # 搜索文章（仅搜索已发布且公开的文章）
            articles = Article.objects.filter(
                Q(status='published', visibility='public') &
                (Q(title__icontains=query) |
                Q(content__icontains=query))
            ).distinct()

            # 如果用户已登录，也包括他们自己的私密文章
            if request.user.is_authenticated:
                user_private_articles = Article.objects.filter(
                    Q(status='published', visibility='private', author=request.user) &
                    (Q(title__icontains=query) |
                    Q(content__icontains=query))
                ).distinct()

                # 合并查询结果
                articles = (articles | user_private_articles).distinct()

    # 对作者结果进行分页
    authors_paginator = Paginator(authors, 10)  # 每页10个作者
    authors_page = request.GET.get('authors_page')
    try:
        paginated_authors = authors_paginator.page(authors_page)
    except PageNotAnInteger:
        paginated_authors = authors_paginator.page(1)
    except EmptyPage:
        paginated_authors = authors_paginator.page(authors_paginator.num_pages)

    # 对文章结果进行分页
    articles_paginator = Paginator(articles, 10)  # 每页10篇文章
    articles_page = request.GET.get('articles_page')
    try:
        paginated_articles = articles_paginator.page(articles_page)
    except PageNotAnInteger:
        paginated_articles = articles_paginator.page(1)
    except EmptyPage:
        paginated_articles = articles_paginator.page(articles_paginator.num_pages)

    context = {
        'query': query,
        'search_type': search_type,
        'authors': paginated_authors,
        'articles': paginated_articles,
    }

    return render(request, 'users/search_results.html', context)
