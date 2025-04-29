from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from .forms import UserRegisterForm, UserLoginForm
from .models import User


def register(request):
    """用户注册视图"""
    if request.user.is_authenticated:
        return redirect('articles:article_list')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('注册成功！欢迎加入Blog_OS！'))
            return redirect('articles:article_list')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


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
