from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _

from .models import User


class UserRegisterForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(
        label=_("邮箱"),
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'})
    )
    username = forms.CharField(
        label=_("用户名"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    password1 = forms.CharField(
        label=_("密码"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )
    password2 = forms.CharField(
        label=_("确认密码"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入密码'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        """验证用户名是否已被使用"""
        username = self.cleaned_data.get('username')
        print(f"Validating username: {username}")

        # 检查用户名是否存在
        if User.objects.filter(username=username).exists():
            # 检查是否有激活用户
            active_users = User.objects.filter(username=username, is_active=True)
            if active_users.exists():
                print(f"Active user with username '{username}' exists")
                raise forms.ValidationError(_('该用户名已被使用。'))

        return username

    def clean_email(self):
        """验证邮箱是否已被使用"""
        email = self.cleaned_data.get('email')
        print(f"Validating email: {email}")

        if User.objects.filter(email=email).exists():
            # 检查该邮箱关联的用户
            users = User.objects.filter(email=email)
            print(f"发现{users.count()}个使用相同邮箱的用户")

            # 检查是否有激活用户
            active_users = users.filter(is_active=True)
            if active_users.exists():
                print(f"Active user with email '{email}' exists")
                raise forms.ValidationError(_('该邮箱已被注册。'))

        return email


class UserLoginForm(AuthenticationForm):
    """用户登录表单"""
    username = forms.CharField(
        label=_("用户名"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    password = forms.CharField(
        label=_("密码"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )


class UserProfileForm(forms.ModelForm):
    """用户个人信息编辑表单"""
    first_name = forms.CharField(
        label=_("名"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label=_("姓"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label=_("邮箱"),
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    bio = forms.CharField(
        label=_("个人简介"),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio']


class UserAvatarForm(forms.ModelForm):
    """用户头像上传表单"""
    avatar = forms.ImageField(
        label=_("头像"),
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['avatar']