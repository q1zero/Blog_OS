## Blog_OS

> 项目描述：一个基于 Django 的博客平台，提供用户管理、文章发布、评论交互等功能。
> 项目目的：搭建一个功能完善、易扩展的博客系统，支持用户认证、RESTful API 接口以及模板渲染。
> 项目状态：开发中
> 项目团队：
>
> * 开发者 A：负责用户管理模块和权限模块 (分支:710)
> * 开发者 B：负责文章管理模块和评论系统模块 (分支:zjy)
>
> > 技术栈：Django 4.2.20, Python >=3.12, MySQL 8.0, djangorestframework 3.14.x, djangorestframework-simplejwt, Bootstrap 5

## 依赖

* Django==4.2.20：Web 框架
* djangorestframework>=3.14.0：RESTful API 支持
* djangorestframework-simplejwt>=5.0：JWT 认证
* markdown>=3.8：Markdown 渲染

## 开发环境

* Python 3.12+
* MySQL 8.0
* VS Code 或 PyCharm
* 虚拟环境管理（venv）
* 包管理器:uv (兼容pip,使用uv sync安装依赖,uv run运行项目)
* 工具：Black, isort, flake8, mypy, Sphinx

## 项目结构

```
root
- .gitignore         // Git 忽略文件
- .python-version    // Python 版本控制文件
- .venv              // 虚拟环境目录
- .github            // GitHub配置目录
    - workflows      // GitHub Actions工作流
        - pr-auto-review.yml        // PR自动审阅与合并
        - main-branch-pr-merge.yml  // Main分支PR合并自动化测试
        - main-branch-protection.yml // Main分支保护配置
    - PULL_REQUEST_TEMPLATE // PR模板目录
        - main_branch_pr.md // Main分支PR模板
    - pull_request_template.md // 默认PR模板
- .codelf            // 项目文档目录
    - attention.md
    - project.md
    - _changelog.md
- blog               // Django 项目主目录
    - manage.py      // Django 管理命令入口
    - apps           // 项目应用模块
        - users      // 用户管理模块
        - articles   // 文章管理模块
            - models.py      // 文章、分类、标签、点赞和收藏模型
            - views.py       // 文章列表、详情、创建、更新和删除视图
            - urls.py        // 文章URL配置
            - admin.py       // 管理后台配置
        - comments   // 评论系统模块
            - models.py      // 评论模型（支持嵌套回复）
            - views.py       // 评论提交和删除视图
            - urls.py        // 评论URL配置
            - admin.py       // 评论管理配置
    - config         // 配置目录（settings, urls, wsgi, asgi）
    - utils          // 通用工具函数
        - templatetags       // 自定义模板标签和过滤器
            - __init__.py    // 包初始化文件
            - markdown_filters.py // Markdown文本处理过滤器
    - templates      // 模板目录
        - base       // 基础模板
        - articles   // 文章相关模板
            - list.html      // 文章列表页
            - detail.html    // 文章详情页（优化布局，支持弹窗删除确认）
            - home.html      // 首页模板
            - article_form.html  // 文章创建和编辑表单
            - article_confirm_delete.html // 文章删除确认页面
        - comments   // 评论相关模板
            - comment.html   // 评论组件（支持嵌套，使用JS弹窗确认删除）
            - comment_confirm_delete.html // 评论删除确认页面
            - review_comments.html // 评论审核页面（管理员专用）
    - static         // 静态文件目录
        - css        // 样式文件目录
            - style.css      // 主要样式文件
- docs               // 项目文档目录
    - ci_cd_workflow.md // CI/CD工作流程文档
- plan.md            // 项目开发计划
- pyproject.toml     // 依赖和项目配置
- README.md          // 项目说明文档
- uv.lock            // 依赖锁文件
```

## 模块说明

### 用户管理模块

用户管理模块提供了博客平台的用户认证和管理功能，是系统的基础模块。

**主要模型：**

1. **User（用户）**
   * 基本信息：用户名、邮箱、密码、头像、个人简介
   * 角色管理：普通用户、管理员身份标识
   * 状态管理：账号激活状态、最后登录时间
   * 继承自AbstractUser，保留Django原生用户系统的所有功能

2. **EmailVerification（邮箱验证）**
   * 基本信息：UUID令牌、创建时间、过期时间、验证状态
   * 关联用户：外键关联到User模型
   * 验证逻辑：检查令牌是否有效、是否过期

**主要功能：**

1. 用户注册与认证
   * 支持用户名/邮箱注册
   * 邮箱验证功能，确保邮箱真实性
   * 验证链接过期处理和重新发送功能

2. 用户登录/登出管理
   * 使用Django原生会话认证
   * 集成JWT令牌认证支持API访问
   * 登录状态管理和记录

3. 用户个人资料管理
   * 个人资料展示页面
   * 个人信息编辑功能
   * 头像上传与裁剪功能（自动裁剪为正方形）
   * 密码修改功能

4. 用户激活与禁用管理
   * 管理员可以批量激活/禁用用户
   * 邮箱验证后自动激活账号

5. 用户权限管理
   * 基于角色的访问控制
   * 使用Django的权限系统进行管理

**URL结构：**

* `/users/register/` - 用户注册
* `/users/register/done/` - 注册完成页面
* `/users/verify-email/<token>/` - 邮箱验证
* `/users/resend-verification/` - 重新发送验证邮件
* `/users/login/` - 用户登录
* `/users/logout/` - 用户登出
* `/users/profile/<username>/` - 用户个人资料
* `/users/profile/edit/` - 编辑个人资料
* `/users/profile/change-avatar/` - 更换头像
* `/users/profile/change-password/` - 修改密码
* `/users/profile/change-password/done/` - 密码修改完成

### 文章管理模块

文章管理模块提供了博客平台的核心功能，包括文章、分类和标签的管理。

**主要模型：**

1. **Article（文章）**
   * 基本信息：标题、内容、作者、创建时间、更新时间、发布时间
   * 状态管理：草稿/已发布状态，公开/私密可见性
   * 关联信息：分类（外键）、标签（多对多）
   * 别名（slug）处理：支持自定义别名，或自动使用数据库ID作为默认值

2. **Category（分类）**
   * 基本信息：名称、别名（slug）、描述、创建时间、更新时间

3. **Tag（标签）**
   * 基本信息：名称、别名（slug）、创建时间、更新时间
   * 标签输入：支持通过标签输入框添加多个标签，逗号分隔或回车确认
   * 别名处理：自动使用数据库ID作为别名，支持中文标签名称

4. **Like（点赞）**
   * 关联信息：用户、文章、创建时间
   * 唯一性约束：用户只能对一篇文章点赞一次
   * 数据显示：在文章预览和详情页显示点赞数量

5. **Favorite（收藏）**
   * 关联信息：用户、文章、创建时间
   * 唯一性约束：用户只能收藏一篇文章一次
   * 数据显示：在文章预览和详情页显示收藏数量

**主要功能：**

1. 网站首页展示（按发布时间展示最新的文章）
   * 在文章预览卡片底部显示点赞数和收藏数
2. 文章列表展示（支持分类和标签过滤）
3. 文章详情展示（支持Markdown渲染和代码高亮）
4. 文章管理功能（支持创建、编辑和删除）
   * 编辑/删除文章按钮放置在文章元数据行，提升UI一致性
   * 删除文章采用JS弹窗确认，无需跳转确认页面
   * 创建/编辑表单支持标签输入框，通过回车或逗号分隔添加多个标签
   * 文章别名（slug）支持留空，自动使用数据库ID作为默认值
5. 文章状态和可见性控制（草稿/发布，公开/私密）
6. 文章点赞和收藏功能（支持AJAX交互）
   * 点赞/收藏按钮统一样式，放置在文章内容末尾
   * 点赞按钮使用浅色背景样式，与收藏按钮风格统一
7. 文章预览处理（去除Markdown格式符号，显示纯文本预览）
8. 我的文章视图
   * 显示当前用户的已发布文章（包括公开和私密），并标注状态
   * 提供草稿箱视图，专门显示草稿状态的文章
   * 在文章预览中显示状态标签（公开/私密，草稿/已发布）

**URL结构：**

* `/` - 首页，显示最新文章
* `/articles/` - 文章列表
* `/articles/<slug>/` - 文章详情
* `/articles/category/<slug>/` - 按分类过滤文章
* `/articles/tag/<id>/` - 按标签过滤文章（使用ID而非slug）
* `/articles/create/` - 创建新文章
* `/articles/update/<slug>/` - 更新文章
* `/articles/delete/<slug>/` - 删除文章
* `/articles/like/<slug>/` - 点赞文章
* `/articles/favorite/<slug>/` - 收藏文章
* `/articles/my/published/` - 我的已发布文章列表
* `/articles/my/drafts/` - 我的草稿箱
* `/articles/publish/<slug>/` - 发布草稿文章

### 评论系统模块

评论系统模块提供了用户互动的关键功能，支持对文章进行评论和回复。

**主要模型：**

1. **Comment（评论）**
   * 基本信息：内容、作者、文章、创建时间、更新时间
   * 审核状态：是否通过审核
   * 嵌套结构：父评论关联（自引用外键）

**主要功能：**

1. 评论提交功能（用户须登录）
   * 评论提交后的等待审核信息使用JS弹窗提示，替代浏览器原生alert
2. 嵌套回复功能（支持对评论进行回复）
3. 评论审核机制（管理员或自动审核）
4. 评论管理功能（作者和管理员可删除）
   * 删除评论采用JS弹窗确认，并通过AJAX处理删除请求
   * 支持主评论和回复评论的删除功能，保持一致的用户体验
5. AJAX评论交互（无需刷新页面）

**URL结构：**

* `/comments/<article_slug>/add/` - 添加评论
* `/comments/<comment_id>/delete/` - 删除评论
* `/comments/review/` - 审核评论（管理员专用）

### 工具模块

工具模块提供了整个博客平台的通用功能和辅助工具。

**主要组件：**

1. **模板标签和过滤器**
   * `markdown_filters.py`：处理Markdown文本的自定义过滤器
     * `plain_text_preview`：将Markdown文本转换为纯文本预览，去除所有格式符号
   * 应用场景：文章列表和首页的文章预览展示

## CI/CD 配置

项目使用GitHub Actions实现持续集成和部署，包含以下工作流程：

### Main分支PR合并自动化测试工作流

* **文件**: `.github/workflows/main-branch-pr-merge.yml`
* **用途**: 专门针对合并到main分支的PR进行基本测试和审批
* **触发条件**: 针对main分支的PR创建、更新和重新打开
* **主要步骤**:
  1. 验证PR内容与格式
  2. 代码检查与基本测试
  3. 基本集成测试（确保Django项目能启动）
  4. 测试结果报告
  5. 自动合并PR到main分支（非草稿状态）

详细的CI/CD流程说明请参考 `docs/ci_cd_workflow.md`

### CI特别说明

作为学习项目，本CI配置简化了部分测试流程：

* 不包含严格的安全检查
* 代码风格检查不会阻止流程
* 设计了数据库迁移容错机制
* 主要确保Django项目能够正常运行
* 智能依赖安装：
  * 自动检测pyproject.toml、requirements.txt等不同依赖文件
  * 针对不同情况采用合适的安装方式
  * 当找不到依赖文件时，直接安装基本依赖
  * 确保Django和MySQLClient正确安装
* 自动合并功能：
  * 使用GitHub仓库环境变量CUSTOM_GITHUB_TOKEN获取权限
  * 自动合并通过测试的非草稿PR
  * 合并后自动删除源分支