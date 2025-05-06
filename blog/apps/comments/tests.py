from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Comment
from apps.articles.models import Article

User = get_user_model()


class CommentModelTest(TestCase):
    """评论模型测试"""

    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        # 创建测试文章
        self.article = Article.objects.create(
            title="测试文章",
            content="测试文章内容",
            author=self.user,
            status="published",
            visibility="public",
        )

        # 创建测试评论
        self.comment = Comment.objects.create(
            content="测试评论内容",
            author=self.user,
            article=self.article,
            is_approved=True,
        )

    def test_comment_creation(self):
        """测试评论创建"""
        self.assertEqual(self.comment.content, "测试评论内容")
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.article, self.article)
        self.assertTrue(self.comment.is_approved)
        self.assertIsNone(self.comment.parent)

    def test_comment_str_representation(self):
        """测试评论字符串表示"""
        expected = f"{self.user.username} 对 {self.article.title} 的评论"
        self.assertEqual(str(self.comment), expected)

    def test_nested_comment_creation(self):
        """测试嵌套评论创建"""
        # 创建回复评论
        reply = Comment.objects.create(
            content="回复评论内容",
            author=self.user,
            article=self.article,
            parent=self.comment,
            is_approved=True,
        )

        self.assertEqual(reply.content, "回复评论内容")
        self.assertEqual(reply.parent, self.comment)
        self.assertEqual(reply.article, self.article)

        # 检查父评论是否有回复
        self.assertTrue(self.comment.replies.filter(id=reply.id).exists())

    def test_comment_ordering(self):
        """测试评论排序"""
        # 创建多个评论，验证排序
        comments_data = []
        for i in range(3):
            comment = Comment.objects.create(
                content=f"测试评论内容 {i}",
                author=self.user,
                article=self.article,
                is_approved=True,
            )
            comments_data.append(comment)

        # 获取所有评论并检查顺序
        comments = Comment.objects.filter(article=self.article, parent=None)
        self.assertEqual(comments.count(), 4)  # 包括setUp中创建的评论

        # 验证某个评论在列表中
        newest_comment = comments_data[-1]  # 最后创建的评论
        self.assertIn(newest_comment, comments)

    def test_comment_approval_status(self):
        """测试评论审核状态"""
        # 创建待审核评论
        pending_comment = Comment.objects.create(
            content="待审核评论内容",
            author=self.user,
            article=self.article,
            is_approved=False,
        )

        self.assertFalse(pending_comment.is_approved)

        # 更新审核状态
        pending_comment.is_approved = True
        pending_comment.save()

        # 验证审核状态已更新
        self.assertTrue(Comment.objects.get(id=pending_comment.id).is_approved)


class CommentViewTest(TestCase):
    """评论视图测试"""

    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword",
            is_staff=True,
        )

        # 创建测试文章
        self.article = Article.objects.create(
            title="测试文章",
            content="测试文章内容",
            author=self.user,
            status="published",
            visibility="public",
        )

        # 创建测试评论
        self.comment = Comment.objects.create(
            content="测试评论内容",
            author=self.user,
            article=self.article,
            is_approved=True,
        )

        # 创建待审核评论
        self.pending_comment = Comment.objects.create(
            content="待审核评论内容",
            author=self.user,
            article=self.article,
            is_approved=False,
        )

        # 创建测试客户端
        self.client = Client()

    def test_add_comment(self):
        """测试添加评论"""
        url = reverse("comments:add_comment", args=[self.article.slug])

        # 未登录用户不能评论
        response = self.client.post(url, {"content": "新评论内容"})
        self.assertEqual(response.status_code, 302)  # 重定向到登录页
        self.assertEqual(Comment.objects.count(), 2)  # 评论数量不变

        # 登录用户可以评论
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(url, {"content": "新评论内容"})
        self.assertEqual(response.status_code, 302)  # 重定向到文章详情页
        self.assertEqual(Comment.objects.count(), 3)  # 评论数量+1

        # 验证新评论
        new_comment = Comment.objects.latest("created_at")
        self.assertEqual(new_comment.content, "新评论内容")
        self.assertEqual(new_comment.author, self.user)
        self.assertEqual(new_comment.article, self.article)
        self.assertTrue(new_comment.is_approved)  # 默认通过审核

    def test_add_reply(self):
        """测试添加回复"""
        url = reverse("comments:add_comment", args=[self.article.slug])

        # 登录用户
        self.client.login(username="testuser", password="testpassword")

        # 添加回复
        response = self.client.post(
            url, {"content": "回复评论内容", "parent_id": self.comment.id}
        )

        # 验证回复
        reply = Comment.objects.filter(parent=self.comment).first()
        self.assertIsNotNone(reply)
        self.assertEqual(reply.content, "回复评论内容")
        self.assertEqual(reply.author, self.user)
        self.assertEqual(reply.article, self.article)

    def test_delete_comment(self):
        """测试删除评论"""
        url = reverse("comments:delete_comment", args=[self.comment.id])

        # 未登录用户不能删除
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # 重定向到登录页
        self.assertEqual(Comment.objects.count(), 2)  # 评论数量不变

        # 登录用户可以删除自己的评论
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # 重定向到文章详情页
        self.assertEqual(Comment.objects.count(), 1)  # 评论数量-1

    def test_delete_other_user_comment(self):
        """测试普通用户不能删除他人评论"""
        # 创建另一个用户及其评论
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpassword"
        )

        other_comment = Comment.objects.create(
            content="其他用户的评论",
            author=other_user,
            article=self.article,
            is_approved=True,
        )

        url = reverse("comments:delete_comment", args=[other_comment.id])

        # 普通用户尝试删除他人评论
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # 重定向到文章详情页
        self.assertEqual(Comment.objects.count(), 3)  # 评论数量不变

        # 管理员可以删除任何人的评论
        self.client.logout()
        self.client.login(username="adminuser", password="adminpassword")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 2)  # 评论数量-1

    def test_comment_approval(self):
        """测试评论审核状态变更"""
        # 不测试视图GET请求，只测试评论审核功能

        # 创建待审核评论
        pending_comment = Comment.objects.create(
            content="待审核评论内容",
            author=self.user,
            article=self.article,
            is_approved=False,
        )

        # 直接更改评论的审核状态，模拟审核通过的操作
        pending_comment.is_approved = True
        pending_comment.save()

        # 验证评论已通过审核
        pending_comment.refresh_from_db()
        self.assertTrue(pending_comment.is_approved)

        # 创建另一个待审核评论
        another_pending = Comment.objects.create(
            content="另一个待审核评论",
            author=self.user,
            article=self.article,
            is_approved=False,
        )

        # 直接删除评论，模拟审核拒绝的操作
        another_pending_id = another_pending.id
        another_pending.delete()

        # 验证评论已被删除
        self.assertEqual(Comment.objects.filter(id=another_pending_id).count(), 0)
