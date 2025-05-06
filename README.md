# Blog_OS

## 如何创建 GitHub 个人访问令牌（Personal Access Token）

1. 登录 GitHub 账户  
   - 打开 [GitHub](https://github.com) 并登录您的账户  
   - 点击右上角头像，选择 **Settings**

2. 进入开发者设置  
   - 滚动到页面底部，点击 **Developer settings**

3. 创建个人访问令牌  
   1. 在左侧菜单中选择 **Personal access tokens**  
   2. 点击 **Tokens (classic)**  
   3. 点击 **Generate new token**（生成新令牌）  
   4. 如有安全验证提示，请完成验证

4. 配置令牌信息  
   - **Note**：输入描述性名称，例如 `Blog_OS PR合并自动化`  
   - **过期时间**（Expiration）：选择合适的期限（建议 90 天）  
   - **Scopes**：勾选以下权限：  
     - `repo`（完整仓库访问权限）  
     - `workflow`（工作流权限）  
     - `read:org`（组织读取权限，仅在组织仓库时需勾选）  
   - 点击 **Generate token**  
   > **重要提示**：生成后请立即复制令牌，页面关闭后无法再次查看

---

## 将令牌添加到仓库密钥

1. 进入 Blog_OS 仓库设置  
2. 在左侧菜单点击 **Secrets and variables** → **Actions**  
3. 点击 **New repository secret**  
4. 填写密钥信息：  
   - **Name**：`CUSTOM_GITHUB_TOKEN`  
   - **Value**：粘贴刚才复制的个人访问令牌  
5. 点击 **Add secret**

完成上述步骤后，GitHub Actions 工作流即可使用此自定义令牌进行 PR 合并操作，确保拥有足够权限。

---

## 数据库查询性能优化文档

为了提高应用程序的性能，我们针对博客平台的数据库查询进行了一系列优化。以下详细介绍了实施的优化措施：

### 1. 使用 select_related 和 prefetch_related 减少查询次数

为了减少数据库查询的次数，我们在以下视图中使用了 `select_related` 和 `prefetch_related`：

#### 1.1 文章列表视图

```python
# 使用select_related加载author和category，减少数据库查询
articles = Article.objects.select_related('author', 'category').prefetch_related('tags').filter(
    status="published", 
    visibility="public"
)
```

#### 1.2 文章详情视图

```python
# 使用select_related预加载author和category，使用prefetch_related预加载tags和评论
article = get_object_or_404(
    Article.objects.select_related('author', 'category')
    .prefetch_related(
        'tags',
        'comments__author',  # 预加载评论及评论作者
        'comments__replies__author',  # 预加载评论回复及回复作者
    ),
    slug=article_slug
)
```

#### 1.3 评论审核视图

```python
# 使用select_related预加载评论相关的作者和文章数据
pending_comments = Comment.objects.select_related('author', 'article').filter(is_approved=False).order_by("-created_at")
```

### 2. 添加数据库索引

为了优化数据库查询性能，我们为模型的关键字段添加了数据库索引：

#### 2.1 文章模型索引

```python
# 为文章模型添加索引
author = models.ForeignKey(..., db_index=True)
category = models.ForeignKey(..., db_index=True)
status = models.CharField(..., db_index=True)
visibility = models.CharField(..., db_index=True)
created_at = models.DateTimeField(..., db_index=True)
published_at = models.DateTimeField(..., db_index=True)
views_count = models.PositiveIntegerField(..., db_index=True)

# 添加复合索引
class Meta:
    indexes = [
        models.Index(fields=["author", "status"], name="author_status_idx"),
        models.Index(fields=["status", "visibility"], name="status_visibility_idx"),
    ]
```

#### 2.2 评论模型索引

```python
# 为评论模型添加索引
author = models.ForeignKey(..., db_index=True)
article = models.ForeignKey(..., db_index=True)
parent = models.ForeignKey(..., db_index=True)
created_at = models.DateTimeField(..., db_index=True)
is_approved = models.BooleanField(..., db_index=True)

# 添加复合索引
class Meta:
    indexes = [
        models.Index(fields=["article", "is_approved"], name="article_approved_idx"),
    ]
```

### 3. 实施查询缓存

为了减少频繁访问的数据库查询，我们使用了Django的缓存框架：

#### 3.1 缓存配置

```python
# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# 缓存过期时间设置
CACHE_TTL = 60 * 15  # 15分钟
```

#### 3.2 视图缓存

```python
# 为首页和文章列表视图添加缓存装饰器
@cache_page(CACHE_TTL)
def article_list(request, category_slug=None, tag_id=None):
    # ...

@cache_page(CACHE_TTL)
def home(request):
    # ...
```

### 4. 其他优化建议

1. **限制查询结果数量**：对于不需要全部数据的查询，我们限制了返回结果的数量

   ```python
   approved_comments = Comment.objects.select_related('author', 'article').filter(is_approved=True).order_by("-created_at")[:50]
   ```

2. **使用分页**：所有列表视图都使用了分页，每页显示固定数量的结果

   ```python
   paginator = Paginator(articles, 10)  # 每页显示10篇文章
   ```

3. **使用会话控制重复计数**：避免文章浏览量的重复计数

   ```python
   session_key = f"viewed_article_{article.pk}"
   if not request.session.get(session_key, False):
       article.increase_views()
       request.session[session_key] = True
       request.session.set_expiry(1800)  # 30分钟内不重复计数
   ```

### 5. 优化效果

这些优化措施可以显著提高博客平台的性能表现：

1. **减少数据库查询次数**：使用 `select_related` 和 `prefetch_related` 可以减少多达数十次的数据库查询
2. **提高查询速度**：为经常查询的字段添加索引，可以使查询速度提高数倍
3. **减轻数据库负载**：通过缓存热门页面，可以减少数据库的负载
4. **改善用户体验**：页面加载更快，响应更迅速

以上优化措施在项目规模扩大、访问量增加时尤为重要。
