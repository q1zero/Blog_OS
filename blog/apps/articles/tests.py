from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Article, Category, Tag, Like, Favorite

User = get_user_model()


class ArticleModelTest(TestCase):
    """文章模型测试"""

    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        # 创建测试分类
        self.category = Category.objects.create(
            name="测试分类", slug="test-category", description="测试分类描述"
        )

        # 创建测试标签
        self.tag = Tag.objects.create(name="测试标签", slug="test-tag")

        # 创建测试文章
        self.article = Article.objects.create(
            title="测试文章",
            content="测试文章内容",
            author=self.user,
            category=self.category,
            status="published",
            visibility="public",
        )
        self.article.tags.add(self.tag)

    def test_article_creation(self):
        """测试文章创建"""
        self.assertEqual(self.article.title, "测试文章")
        self.assertEqual(self.article.content, "测试文章内容")
        self.assertEqual(self.article.author, self.user)
        self.assertEqual(self.article.category, self.category)
        self.assertEqual(self.article.status, "published")
        self.assertEqual(self.article.visibility, "public")
        self.assertTrue(self.article.tags.filter(id=self.tag.id).exists())

    def test_article_str_representation(self):
        """测试文章字符串表示"""
        self.assertEqual(str(self.article), "测试文章")

    def test_article_get_absolute_url(self):
        """测试文章的绝对URL"""
        self.assertEqual(
            self.article.get_absolute_url(),
            reverse("articles:article_detail", args=[self.article.slug]),
        )

    def test_article_published_at(self):
        """测试发布状态下的发布时间自动设置"""
        # 创建草稿状态文章
        draft_article = Article.objects.create(
            title="草稿文章",
            content="草稿文章内容",
            author=self.user,
            status="draft",
        )
        self.assertIsNone(draft_article.published_at)

        # 将文章状态改为已发布
        draft_article.status = "published"
        draft_article.save()
        self.assertIsNotNone(draft_article.published_at)

    def test_article_increase_views(self):
        """测试文章浏览量增加功能"""
        self.assertEqual(self.article.views_count, 0)

        # 增加浏览量
        self.article.increase_views()
        self.assertEqual(self.article.views_count, 1)

        # 再次增加浏览量
        self.article.increase_views()
        self.assertEqual(self.article.views_count, 2)


class ArticleViewTest(TestCase):
    """文章视图测试"""

    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        # 创建测试分类
        self.category = Category.objects.create(
            name="测试分类", slug="test-category", description="测试分类描述"
        )

        # 创建测试标签
        self.tag = Tag.objects.create(name="测试标签", slug="test-tag")

        # 创建测试文章（公开发布）
        self.public_article = Article.objects.create(
            title="公开文章",
            content="公开文章内容",
            author=self.user,
            category=self.category,
            status="published",
            visibility="public",
        )
        self.public_article.tags.add(self.tag)

        # 创建测试文章（私密发布）
        self.private_article = Article.objects.create(
            title="私密文章",
            content="私密文章内容",
            author=self.user,
            status="published",
            visibility="private",
        )

        # 创建测试文章（草稿状态）
        self.draft_article = Article.objects.create(
            title="草稿文章",
            content="草稿文章内容",
            author=self.user,
            status="draft",
            visibility="public",
        )

        # 创建测试客户端
        self.client = Client()

    def test_article_list_view(self):
        """测试文章列表视图"""
        url = reverse("articles:article_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "articles/list.html")
        self.assertContains(response, "公开文章")
        self.assertNotContains(response, "私密文章")
        self.assertNotContains(response, "草稿文章")

    def test_article_detail_view(self):
        """测试文章详情视图"""
        url = reverse("articles:article_detail", args=[self.public_article.slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "articles/detail.html")
        self.assertContains(response, "公开文章")
        self.assertContains(response, "公开文章内容")

    def test_article_detail_view_private(self):
        """测试私密文章详情视图访问限制"""
        url = reverse("articles:article_detail", args=[self.private_article.slug])

        # 未登录用户不能访问私密文章
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # 重定向到登录页

        # 文章作者可以访问自己的私密文章
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "私密文章")

    def test_article_create_view(self):
        """测试文章创建视图"""
        url = reverse("articles:article_create")

        # 未登录用户不能访问创建页面
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # 重定向到登录页

        # 登录用户可以访问创建页面
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "articles/article_form.html")

        # 测试创建文章
        article_data = {
            "title": "新文章",
            "content": "新文章内容",
            "category": self.category.id,
            "status": "published",
            "visibility": "public",
            "tags_input": "测试标签,新标签",
        }
        response = self.client.post(url, article_data)
        self.assertEqual(Article.objects.count(), 4)  # 原有3篇，新增1篇

        # 验证新创建的文章
        new_article = Article.objects.get(title="新文章")
        self.assertEqual(new_article.author, self.user)

    def test_article_update_view(self):
        """测试文章更新视图"""
        url = reverse("articles:article_update", args=[self.public_article.slug])

        # 未登录用户不能访问更新页面
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # 重定向到登录页

        # 登录用户可以访问更新页面
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "articles/article_form.html")

        # 测试更新文章
        update_data = {
            "title": "更新后的文章",
            "content": "更新后的内容",
            "category": self.category.id,
            "status": "published",
            "visibility": "private",
            "tags_input": "测试标签,更新标签",
        }
        response = self.client.post(url, update_data)

        # 验证更新后的文章
        self.public_article.refresh_from_db()
        self.assertEqual(self.public_article.title, "更新后的文章")
        self.assertEqual(self.public_article.content, "更新后的内容")
        self.assertEqual(self.public_article.visibility, "private")

    def test_article_delete_view(self):
        """测试文章删除视图"""
        url = reverse("articles:article_delete", args=[self.public_article.slug])

        # 未登录用户不能删除文章
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # 重定向到登录页
        self.assertEqual(Article.objects.count(), 3)  # 文章数量不变

        # 登录用户可以删除文章
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(url)
        self.assertEqual(Article.objects.count(), 2)  # 文章数量减1


class LikeFavoriteTest(TestCase):
    """点赞和收藏功能测试"""

    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        self.user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpassword"
        )

        # 创建测试文章
        self.article = Article.objects.create(
            title="测试文章",
            content="测试文章内容",
            author=self.user,
            status="published",
            visibility="public",
        )

        # 创建测试客户端
        self.client = Client()

    def test_toggle_like(self):
        """测试点赞切换功能"""
        url = reverse("articles:toggle_like", args=[self.article.slug])

        # 未登录用户不能点赞
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # 重定向到登录页
        self.assertEqual(Like.objects.count(), 0)

        # 登录用户可以点赞
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # 重定向到文章详情页
        self.assertEqual(Like.objects.count(), 1)

        # 再次点击取消点赞
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Like.objects.count(), 0)

    def test_toggle_favorite(self):
        """测试收藏切换功能"""
        url = reverse("articles:toggle_favorite", args=[self.article.slug])

        # 未登录用户不能收藏
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # 重定向到登录页
        self.assertEqual(Favorite.objects.count(), 0)

        # 登录用户可以收藏
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # 重定向到文章详情页
        self.assertEqual(Favorite.objects.count(), 1)

        # 再次点击取消收藏
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Favorite.objects.count(), 0)

    def test_user_can_like_multiple_articles(self):
        """测试用户可以点赞多篇文章"""
        # 创建另一篇文章
        article2 = Article.objects.create(
            title="测试文章2",
            content="测试文章内容2",
            author=self.user,
            status="published",
            visibility="public",
        )

        self.client.login(username="testuser", password="testpassword")

        # 点赞第一篇文章
        self.client.post(reverse("articles:toggle_like", args=[self.article.slug]))

        # 点赞第二篇文章
        self.client.post(reverse("articles:toggle_like", args=[article2.slug]))

        self.assertEqual(Like.objects.count(), 2)

    def test_multiple_users_can_like_same_article(self):
        """测试多用户可以点赞同一篇文章"""
        # 第一个用户点赞
        self.client.login(username="testuser", password="testpassword")
        self.client.post(reverse("articles:toggle_like", args=[self.article.slug]))

        # 第二个用户点赞
        self.client.logout()
        self.client.login(username="testuser2", password="testpassword")
        self.client.post(reverse("articles:toggle_like", args=[self.article.slug]))

        self.assertEqual(Like.objects.count(), 2)

    def test_my_favorites_view(self):
        """测试我的收藏夹视图"""
        url = reverse("articles:my_favorites")

        # 未登录用户不能访问收藏夹
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # 重定向到登录页

        # 登录用户可以访问收藏夹
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "articles/favorites.html")

        # 添加收藏并检查收藏夹
        Favorite.objects.create(user=self.user, article=self.article)
        response = self.client.get(url)
        self.assertContains(response, "测试文章")
