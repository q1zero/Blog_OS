from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('register/done/', views.register_done, name='register_done'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),

    # 搜索功能
    path('search/', views.search, name='search'),

    # 用户个人信息相关URL - 注意顺序，先匹配特定路径，再匹配通用路径
    path('profile/edit/', views.UserProfileEditView.as_view(), name='profile_edit'),
    path('profile/change-avatar/', views.change_avatar, name='change_avatar'),
    path('profile/change-password/', views.UserPasswordChangeView.as_view(), name='change_password'),
    path('profile/change-password/done/', views.password_change_done, name='password_change_done'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
]