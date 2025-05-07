"""
用户应用测试模块
包含所有用户相关的测试：模型测试、视图测试、API测试和权限测试
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.users.models import EmailVerification
from utils.api.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly, IsAdminOrStaffUser

User = get_user_model()


# ==================== 模型测试 ====================

class UserModelTest(TestCase):
    """用户模型测试"""

    def setUp(self):
        """测试前创建用户"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            bio='测试用户简介'
        )

    def test_user_creation(self):
        """测试用户创建"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.bio, '测试用户简介')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_user_str_method(self):
        """测试用户字符串表示"""
        self.assertEqual(str(self.user), 'testuser')


class EmailVerificationModelTest(TestCase):
    """邮箱验证模型测试"""

    def setUp(self):
        """测试前创建用户和验证记录"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

        # 创建有效的验证记录
        self.valid_verification = EmailVerification.objects.create(
            user=self.user,
            token=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(days=1)
        )

        # 创建过期的验证记录
        self.expired_verification = EmailVerification.objects.create(
            user=self.user,
            token=uuid.uuid4(),
            expires_at=timezone.now() - timedelta(days=1)
        )

        # 创建已验证的记录
        self.verified_verification = EmailVerification.objects.create(
            user=self.user,
            token=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(days=1),
            verified=True
        )

    def test_email_verification_creation(self):
        """测试邮箱验证记录创建"""
        self.assertEqual(self.valid_verification.user, self.user)
        self.assertFalse(self.valid_verification.verified)
        self.assertTrue(self.valid_verification.expires_at > timezone.now())

    def test_is_valid_method(self):
        """测试验证有效性检查方法"""
        # 有效的验证记录
        self.assertTrue(self.valid_verification.is_valid())

        # 过期的验证记录
        self.assertFalse(self.expired_verification.is_valid())

        # 已验证的记录
        self.assertFalse(self.verified_verification.is_valid())

    def test_email_verification_str_method(self):
        """测试邮箱验证字符串表示"""
        expected_str = f"{self.user.username} - {self.valid_verification.token}"
        self.assertEqual(str(self.valid_verification), expected_str)


# ==================== 视图测试 ====================

class RegisterViewTest(TestCase):
    """用户注册视图测试"""

    def setUp(self):
        """测试前准备"""
        self.client = Client()
        self.register_url = reverse('users:register')
        self.register_done_url = reverse('users:register_done')

    def test_register_page_loads(self):
        """测试注册页面加载"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_form_submission(self):
        """测试注册表单提交"""
        # 注意：由于实际注册会发送邮件，这里只测试表单提交
        # 实际应用中应该使用mock来模拟邮件发送
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'securepassword123',
            'password2': 'securepassword123',
        }
        response = self.client.post(self.register_url, data)

        # 检查是否重定向到注册完成页面
        # 注意：如果邮件发送失败，这个测试可能会失败
        self.assertRedirects(response, self.register_done_url)

        # 检查用户是否创建但未激活
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        self.assertFalse(user.is_active)


class LoginViewTest(TestCase):
    """用户登录视图测试"""

    def setUp(self):
        """测试前创建用户"""
        self.client = Client()
        self.login_url = reverse('users:login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

    def test_login_page_loads(self):
        """测试登录页面加载"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_successful(self):
        """测试登录成功"""
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data)

        # 检查是否登录成功并重定向到首页
        self.assertRedirects(response, '/')

        # 检查用户是否已登录
        # 使用session检查而不是检查context
        self.assertTrue('_auth_user_id' in self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

    def test_login_failed(self):
        """测试登录失败"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)

        # 检查是否留在登录页面
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

        # 检查是否有错误消息
        # 注意：实际错误消息可能不同，这里只检查是否有错误信息
        self.assertTrue(len(response.context['form'].errors) > 0)


class ProfileViewTest(TestCase):
    """用户个人信息视图测试"""

    def setUp(self):
        """测试前创建用户"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            bio='测试用户简介'
        )
        self.profile_url = reverse('users:profile', kwargs={'username': 'testuser'})
        self.profile_edit_url = reverse('users:profile_edit')

    def test_profile_page_loads(self):
        """测试个人信息页面加载"""
        # 登录用户
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertEqual(response.context['profile_user'], self.user)

    def test_profile_edit_page_loads(self):
        """测试个人信息编辑页面加载"""
        # 登录用户
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(self.profile_edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile_edit.html')

    def test_profile_update(self):
        """测试个人信息更新"""
        # 登录用户
        self.client.login(username='testuser', password='testpassword')

        # 获取当前用户信息以确认表单字段
        response = self.client.get(self.profile_edit_url)
        form = response.context['form']

        # 准备表单数据，包含所有必要的字段
        data = {
            'username': 'testuser',  # 可能需要包含用户名
            'email': 'test@example.com',  # 可能需要包含邮箱
            'bio': '更新后的个人简介',
            'first_name': '测试',
            'last_name': '用户'
        }

        # 添加表单中的其他必要字段
        for field_name in form.fields:
            if field_name not in data and field_name != 'password':
                data[field_name] = getattr(self.user, field_name, '')

        response = self.client.post(self.profile_edit_url, data)

        # 实际实现是重定向到个人信息页面
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)

        # 检查个人信息是否更新
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, '更新后的个人简介')
        self.assertEqual(self.user.first_name, '测试')
        self.assertEqual(self.user.last_name, '用户')


class EmailVerificationTest(TestCase):
    """邮箱验证测试"""

    def setUp(self):
        """测试前创建用户和验证记录"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_active=False  # 未激活用户
        )

        # 创建有效的验证记录
        self.verification = EmailVerification.objects.create(
            user=self.user,
            token=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(days=1)
        )

        self.verify_url = reverse('users:verify_email', kwargs={'token': self.verification.token})

    def test_email_verification_success(self):
        """测试邮箱验证成功"""
        response = self.client.get(self.verify_url)

        # 检查是否重定向到文章列表页面
        self.assertRedirects(response, reverse('articles:article_list'))

        # 检查用户是否已激活
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

        # 检查验证记录是否已标记为已验证
        self.verification.refresh_from_db()
        self.assertTrue(self.verification.verified)

    def test_email_verification_invalid_token(self):
        """测试无效的验证令牌"""
        invalid_url = reverse('users:verify_email', kwargs={'token': uuid.uuid4()})
        response = self.client.get(invalid_url)

        # 检查是否重定向到登录页面
        self.assertRedirects(response, reverse('users:login'))

        # 检查用户是否仍未激活
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


# ==================== API测试 ====================

class UserAPITest(TestCase):
    """用户API测试"""

    def setUp(self):
        """测试前创建用户和客户端"""
        self.client = APIClient()

        # 创建普通用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            bio='测试用户简介'
        )

        # 创建管理员用户
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )

        # API端点
        self.user_list_url = '/api/v1/users/'
        self.user_detail_url = f'/api/v1/users/{self.user.id}/'
        self.me_url = '/api/v1/users/me/'
        self.update_profile_url = '/api/v1/users/update_profile/'
        self.token_url = '/api/v1/token/'

    def test_user_list_authenticated(self):
        """测试已认证用户获取用户列表"""
        # 登录用户
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # 两个用户

    def test_user_list_unauthenticated(self):
        """测试未认证用户获取用户列表"""
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_detail_authenticated(self):
        """测试已认证用户获取用户详情"""
        # 登录用户
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['bio'], '测试用户简介')

    def test_user_detail_unauthenticated(self):
        """测试未认证用户获取用户详情"""
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_create(self):
        """测试创建用户"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password_confirm': 'newpassword123',
            'bio': '新用户简介'
        }

        response = self.client.post(self.user_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 检查用户是否创建
        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'newuser@example.com')
        self.assertEqual(new_user.bio, '新用户简介')

    def test_user_create_password_mismatch(self):
        """测试创建用户时密码不匹配"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password_confirm': 'differentpassword',
            'bio': '新用户简介'
        }

        response = self.client.post(self.user_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_me_endpoint(self):
        """测试获取当前用户信息"""
        # 登录用户
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_update_profile(self):
        """测试更新用户个人信息"""
        # 登录用户
        self.client.force_authenticate(user=self.user)

        data = {
            'bio': '更新后的个人简介',
            'first_name': '测试',
            'last_name': '用户'
        }

        response = self.client.patch(self.update_profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 检查个人信息是否更新
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, '更新后的个人简介')
        self.assertEqual(self.user.first_name, '测试')
        self.assertEqual(self.user.last_name, '用户')

    def test_token_obtain(self):
        """测试获取JWT令牌"""
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }

        response = self.client.post(self.token_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


# ==================== 权限测试 ====================

class MockObject:
    """模拟对象，用于测试权限"""
    def __init__(self, user):
        self.author = user
        self.user = user


class MockView(APIView):
    """模拟视图，用于测试权限"""
    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        return Response(status=status.HTTP_201_CREATED)

    def put(self, request):
        return Response(status=status.HTTP_200_OK)

    def delete(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class IsOwnerOrReadOnlyTest(TestCase):
    """测试IsOwnerOrReadOnly权限类"""

    def setUp(self):
        """测试前创建用户和请求工厂"""
        self.factory = APIRequestFactory()
        self.view = MockView.as_view()

        # 创建用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

        # 创建另一个用户
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword'
        )

        # 创建权限类实例
        self.permission = IsOwnerOrReadOnly()

        # 创建模拟对象
        self.user_object = MockObject(self.user)
        self.other_object = MockObject(self.other_user)

    def test_read_permissions(self):
        """测试读取权限"""
        # 创建GET请求
        request = self.factory.get('/')
        request.user = self.user

        # 测试对自己的对象
        self.assertTrue(self.permission.has_object_permission(request, MockView(), self.user_object))

        # 测试对他人的对象
        self.assertTrue(self.permission.has_object_permission(request, MockView(), self.other_object))

    def test_write_permissions_owner(self):
        """测试所有者的写入权限"""
        # 创建POST请求
        request = self.factory.post('/')
        request.user = self.user

        # 测试对自己的对象
        self.assertTrue(self.permission.has_object_permission(request, MockView(), self.user_object))

    def test_write_permissions_non_owner(self):
        """测试非所有者的写入权限"""
        # 创建POST请求
        request = self.factory.post('/')
        request.user = self.user

        # 测试对他人的对象
        self.assertFalse(self.permission.has_object_permission(request, MockView(), self.other_object))


class IsAdminOrReadOnlyTest(TestCase):
    """测试IsAdminOrReadOnly权限类"""

    def setUp(self):
        """测试前创建用户和请求工厂"""
        self.factory = APIRequestFactory()
        self.view = MockView.as_view()

        # 创建普通用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

        # 创建管理员用户
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )

        # 创建权限类实例
        self.permission = IsAdminOrReadOnly()

    def test_read_permissions(self):
        """测试读取权限"""
        # 创建GET请求
        request = self.factory.get('/')

        # 测试普通用户
        request.user = self.user
        self.assertTrue(self.permission.has_permission(request, MockView()))

        # 测试管理员用户
        request.user = self.admin_user
        self.assertTrue(self.permission.has_permission(request, MockView()))

    def test_write_permissions_admin(self):
        """测试管理员的写入权限"""
        # 创建POST请求
        request = self.factory.post('/')
        request.user = self.admin_user

        self.assertTrue(self.permission.has_permission(request, MockView()))

    def test_write_permissions_non_admin(self):
        """测试非管理员的写入权限"""
        # 创建POST请求
        request = self.factory.post('/')
        request.user = self.user

        self.assertFalse(self.permission.has_permission(request, MockView()))


class IsAdminOrStaffUserTest(TestCase):
    """测试IsAdminOrStaffUser权限类"""

    def setUp(self):
        """测试前创建用户和请求工厂"""
        self.factory = APIRequestFactory()
        self.view = MockView.as_view()

        # 创建普通用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

        # 创建管理员用户
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )

        # 创建超级用户
        self.super_user = User.objects.create_user(
            username='superuser',
            email='super@example.com',
            password='superpassword',
            is_superuser=True
        )

        # 创建权限类实例
        self.permission = IsAdminOrStaffUser()

    def test_permissions_normal_user(self):
        """测试普通用户的权限"""
        request = self.factory.get('/')
        request.user = self.user

        self.assertFalse(self.permission.has_permission(request, MockView()))

    def test_permissions_admin_user(self):
        """测试管理员用户的权限"""
        request = self.factory.get('/')
        request.user = self.admin_user

        self.assertTrue(self.permission.has_permission(request, MockView()))

    def test_permissions_super_user(self):
        """测试超级用户的权限"""
        request = self.factory.get('/')
        request.user = self.super_user

        self.assertTrue(self.permission.has_permission(request, MockView()))
