from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import User


class UserRegistrationForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}),
        help_text=_("Required. Enter a valid email address."),
    )
    username = forms.CharField(
        label=_("Username"),
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'}),
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}),
        help_text=_("Your password must contain at least 8 characters."),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请确认密码'}),
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("A user with that email already exists."))
        return email


class UserLoginForm(AuthenticationForm):
    """用户登录表单"""
    username = forms.CharField(
        label=_("Username or Email"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名或邮箱'})
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )

    def clean_username(self):
        """允许用户使用邮箱或用户名登录"""
        username = self.cleaned_data.get('username')
        # 检查是否是邮箱格式
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                if user:
                    return user.username
            except User.DoesNotExist:
                pass
        return username
