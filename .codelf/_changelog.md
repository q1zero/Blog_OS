## 2025-05-06 16:50

### 19. 数据库查询性能优化

**Change Type**: enhancement, performance

> **Purpose**: 优化数据库查询性能，减少数据库查询次数，提高响应速度
> **Detailed Description**:
>
> 1. 使用 select_related 和 prefetch_related 优化多个视图，减少数据库查询次数
>    * 在文章列表视图中预加载作者和分类数据
>    * 在文章详情视图中预加载作者、分类、标签和评论数据
>    * 在评论审核视图中预加载作者和文章数据
> 2. 为模型添加数据库索引，提高查询速度
>    * 为文章模型添加单字段索引（author、category、status、visibility等）
>    * 为文章模型添加复合索引（author+status、status+visibility）
>    * 为评论模型添加单字段索引（author、article、parent等）
>    * 为评论模型添加复合索引（article+is_approved）
> 3. 实施查询缓存，减少频繁访问的数据库查询
>    * 配置LocMemCache内存缓存后端
>    * 为首页和文章列表视图添加缓存装饰器
>    * 设置15分钟的缓存过期时间
> 4. 其他优化措施
>    * 限制评论查询结果数量
>    * 所有列表视图使用分页
>    * 使用会话控制文章浏览量重复计数
> **Reason for Change**: 提高网站性能，减轻数据库负载，改善用户体验
> **Impact Scope**: 影响文章和评论模块的模型和视图，以及全局缓存配置
> **API Changes**: 无
> **Configuration Changes**: 在settings.py中添加了缓存配置
> **Performance Impact**: 显著减少数据库查询次数，提高页面加载速度

   ```text
   root
   - blog/apps/articles
     - models.py              // update 添加数据库索引和复合索引
     - views.py               // update 使用select_related和prefetch_related优化查询，添加缓存装饰器
     - migrations/            // add 添加索引的数据库迁移文件
   - blog/apps/comments
     - models.py              // update 添加数据库索引和复合索引
     - views.py               // update 使用select_related优化评论查询
     - migrations/            // add 添加索引的数据库迁移文件
   - blog/config
     - settings.py            // update 添加缓存配置
   - README.md                // update 添加数据库查询优化文档
   ```

## 2025-05-08 15:30

### 18. 添加文章浏览量计数功能和优化响应式布局

**Change Type**: feature, enhancement

> **Purpose**: 跟踪文章浏览量并优化文章和评论的响应式布局
> **Detailed Description**:
>
> 1. 在文章模型中添加浏览量字段和增加浏览量的方法
> 2. 在文章详情视图中实现浏览量计数逻辑
>    * 使用会话(session)避免刷新页面重复计数
>    * 设置30分钟的会话过期时间，同一访问者在此期间内重复浏览不会增加计数
> 3. 在文章详情页面显示浏览量信息
> 4. 增强CSS样式，优化文章和评论的响应式布局
>    * 新增评论样式，包括嵌套评论布局和回复表单样式
>    * 完善文章互动部分的样式和响应式支持
>    * 添加多个媒体查询断点，优化不同设备上的显示效果
>    * 优化删除评论弹窗、通知提示等交互元素的样式
> **Reason for Change**: 增加功能完整性，跟踪文章受欢迎程度；提升用户体验，优化不同设备上的显示效果
> **Impact Scope**: 影响文章模型、视图和模板文件，以及CSS样式文件
> **API Changes**: 无
> **Configuration Changes**: 无
> **Performance Impact**: 每次查看文章详情页会增加一次数据库操作（检查和更新浏览量）

   ```text
   root
   - blog/apps/articles
     - models.py              // update 添加浏览量字段和增加浏览量的方法
     - views.py               // update 实现浏览量计数逻辑
     - migrations/            // add 数据库迁移文件
   - blog/templates/articles
     - detail.html            // update 显示文章浏览量信息
   - blog/static/css
     - style.css              // refact 增强响应式布局样式，添加评论样式和媒体查询
   ```

## 2025-05-06 10:21

### 17. 实现评论敏感词过滤功能

**Change Type**: feature

> **Purpose**: 自动检测评论内容中的敏感词，并根据检测结果自动审核或标记为待审核。
> **Detailed Description**:
>
> 1. 在 `utils` 应用中创建 `SensitiveWord` 模型，用于存储敏感词列表。
> 2. 在 Django Admin 后台注册 `SensitiveWord` 模型，方便管理员添加和管理敏感词。
> 3. 修改评论提交视图 (`apps/comments/views.py`) 的逻辑：
>     * 在评论保存前，检查评论内容是否包含数据库中定义的任何敏感词。
>     * 如果不包含敏感词，评论的 `is_approved` 状态设为 `True`，并提示用户"评论已成功提交！"。
>     * 如果包含敏感词，评论的 `is_approved` 状态设为 `False`，并提示用户"评论已提交，检测到可能包含敏感内容，将进行审核。"。
>     * 包含敏感词的评论会出现在管理员的评论审核列表中。
> **Reason for Change**: 自动管理评论内容，减少不当言论的展示，提高社区管理效率。
> **Impact Scope**: 影响评论系统模块和 `utils` 模块。
> **API Changes**: 无。
> **Configuration Changes**: 需要在 `settings.py` 的 `INSTALLED_APPS` 中添加 `utils`。
> **Performance Impact**: 评论提交时会增加一次数据库查询（获取敏感词列表）和字符串匹配操作。如果敏感词数量巨大，可能需要进一步优化。

   ```text
   root
   - blog/utils                 // add 新增 utils 应用
     - __init__.py           // add
     - models.py             // add 添加 SensitiveWord 模型
     - admin.py              // add 注册 SensitiveWord 模型到 Admin
     - migrations/           // add 模型迁移文件
   - blog/apps/comments
     - views.py              // refact 修改评论提交逻辑，添加敏感词检测和自动审核
   - blog/config
     - settings.py           // refact 在 INSTALLED_APPS 中添加 utils
   ```

## 2025-05-03 16:30

### 17. 实现RESTful API接口

**Change Type**: feature

> **Purpose**: 实现符合RESTful风格的API接口，支持版本控制和Swagger文档
> **Detailed Description**:
>
> 1. 创建API应用，实现用户、文章、评论等资源的RESTful接口
> 2. 使用DRF实现API视图和序列化器
> 3. 实现API版本控制，使用URL路径方式（/api/v1/...）
> 4. 集成Swagger文档，提供API自动文档
> 5. 实现JWT认证和权限控制
> **Reason for Change**: 提供标准化的API接口，方便前端和移动端集成
> **Impact Scope**: 新增API应用和接口，不影响现有功能
> **API Changes**: 新增 `/api/v1/` 路径下的所有API接口
> **Configuration Changes**: 在settings.py中添加了API应用和DRF配置
> **Performance Impact**: 无明显性能影响

   ```text
   root
   - blog/api                 // add 新增API应用
     - serializers/          // add API序列化器
       - user_serializers.py // add 用户序列化器
       - article_serializers.py // add 文章序列化器
       - comment_serializers.py // add 评论序列化器
     - views/               // add API视图
       - user_views.py      // add 用户API视图
       - article_views.py   // add 文章API视图
       - comment_views.py   // add 评论API视图
     - permissions.py       // add 自定义权限类
     - urls.py              // add API URL配置
   - blog/config/settings.py // update 更新DRF配置
   - blog/config/urls.py     // update 添加API URL
   - requirements.txt        // update 添加drf-yasg依赖
   ```

## 2025-05-01 16:30

### 16. 实现访问日志记录功能

**Change Type**: feature

> **Purpose**: 实现全站访问日志记录功能，记录用户请求信息并提供管理界面
> **Detailed Description**:
>
> 1. 创建访问日志模型，记录请求路径、方法、状态码、用户信息、IP地址等
> 2. 实现访问日志中间件，自动记录所有HTTP请求
> 3. 添加日志仪表盘页面，显示访问统计和详细记录
> 4. 配置日志记录系统，支持控制台和文件日志
> 5. 添加管理界面，方便管理员查看日志
> **Reason for Change**: 提供系统访问监控和分析功能，帮助管理员了解网站流量和用户行为
> **Impact Scope**: 影响全站，添加新的日志应用和中间件
> **API Changes**: 新增 `/logs/dashboard/` URL用于日志仪表盘
> **Configuration Changes**: 在settings.py中添加了日志配置和中间件
> **Performance Impact**: 由于每个请求都会记录日志，可能会对性能有轻微影响

   ```text
   root
   - blog/apps/logs            // add 新增日志应用
     - models.py              // add 访问日志模型
     - middleware.py          // add 访问日志中间件
     - views.py               // add 日志仪表盘视图
     - urls.py                // add 日志URL配置
     - admin.py               // add 日志管理界面
     - apps.py                // add 应用配置
   - blog/templates/logs
     - dashboard.html         // add 日志仪表盘模板
   - blog/config
     - settings.py            // refact 添加日志应用和中间件配置
     - urls.py                // refact 添加日志URL路由
   - blog/logs                // add 日志文件目录
   ```

## 2025-05-01 14:15

### 15. 添加用户视图下的搜索功能

**Change Type**: feature

> **Purpose**: 在用户视图下添加搜索功能，允许用户搜索作者或文章
> **Detailed Description**:
>
> 1. 在用户视图中添加搜索功能，支持按作者名称、个人简介搜索用户
> 2. 支持按文章标题、内容搜索文章
> 3. 搜索结果分为作者和文章两部分，分别显示
> 4. 支持按搜索类型（全部、作者、文章）筛选结果
> 5. 搜索结果支持分页显示
> **Reason for Change**: 提升用户体验，方便用户快速查找感兴趣的作者和文章
> **Impact Scope**: 影响用户模块，添加新的视图、URL和模板
> **API Changes**: 新增 `/users/search/` URL用于搜索功能
> **Configuration Changes**: 无
> **Performance Impact**: 无明显性能影响

   ```text
   root
   - blog/apps/users
     - views.py               // refact 添加搜索视图函数
     - urls.py                // refact 添加搜索URL路由
   - blog/templates/users
     - search_results.html    // add 搜索结果页面模板
   ```

## 2025-05-01 01:53

### 14. 为管理员添加全局文章编辑和删除功能

**Change Type**: feature

> **Purpose**: 允许管理员对所有已发布公开文章进行编辑和删除操作
> **Detailed Description**:
>
> 1. 在文章列表和详情页面为管理员添加编辑和删除按钮
> 2. 修改视图函数，确保管理员有权限编辑和删除所有文章
> 3. 在文章列表中添加删除确认弹窗，并通过AJAX请求实现删除功能
> 4. 确保编辑页面显示当前文章的内容，而不是之前的内容
> **Reason for Change**: 满足管理员管理所有文章的需求
> **Impact Scope**: 影响文章管理模块，更新视图、模板和交互逻辑
> **API Changes**: 无
> **Configuration Changes**: 无
> **Performance Impact**: 无明显性能影响

   ```text
   root
   - blog/apps/articles
     - views.py               // refact 更新视图函数，允许管理员编辑和删除所有文章
   - blog/templates/articles
     - list.html              // refact 添加编辑和删除按钮，添加删除确认弹窗
     - detail.html            // refact 添加编辑和删除按钮
     - article_form.html      // refact 确保编辑页面显示当前文章内容
   ```

## 2025-05-01 01:35

### 13. 添加评论审核功能

**Change Type**: feature

> **Purpose**: 为管理员添加评论审核功能，允许查看和管理待审核与已通过的评论
> **Detailed Description**:
>
> 1. 在评论应用中添加`review_comments`视图，显示所有评论，分为待审核和已通过两个栏目
> 2. 创建评论审核页面模板，包含两个选项卡分别显示待审核和已通过的评论
> 3. 为管理员在导航栏添加"审核评论"链接
> 4. 支持管理员通过或拒绝评论，拒绝的评论将被删除
> **Reason for Change**: 满足管理员管理评论的需求，确保评论内容符合平台规范
> **Impact Scope**: 影响评论系统模块，新增视图、URL和模板
> **API Changes**: 新增`/comments/review/` URL用于评论审核
> **Configuration Changes**: 无
> **Performance Impact**: 无明显性能影响

   ```text
   root
   - blog/apps/comments
     - views.py               // refact 添加评论审核视图
     - urls.py                // refact 添加评论审核URL模式
   - blog/templates/comments
     - review_comments.html   // add 评论审核页面模板
   - blog/templates/base
     - base.html              // refact 在导航栏添加审核评论链接
   ```

## {datetime: YYYY-MM-DD HH:mm:ss}

### 2025-05-01 01:23

### 12. 更新我的文章视图和状态显示

**Change Type**: feature

> **Purpose**: 改进我的文章视图，分别显示已发布和草稿文章，并在预览中显示状态
> **Detailed Description**:
>
> 1. 将`my_articles`视图拆分为`my_published_articles`和`my_draft_articles`，分别显示已发布文章（包括公开和私密）和草稿文章
> 2. 更新导航栏，将"我的文章"改为下拉菜单，包含"已发布"和"草稿箱"选项
> 3. 在文章列表预览的右下角添加状态标签，显示公开/私密和草稿/已发布状态（使用中文展示）
> **Reason for Change**: 满足用户需求，分别管理已发布和草稿文章，并直观显示文章状态
> **Impact Scope**: 影响文章管理模块，新增视图和URL，更新前端展示
> **API Changes**: 将`/articles/my/`拆分为`/articles/my/published/`和`/articles/my/drafts/`
> **Configuration Changes**: 无
> **Performance Impact**: 无明显性能影响

   ```text
   root
   - blog/apps/articles
     - views.py               // refact 更新我的文章视图，拆分为已发布和草稿视图
     - urls.py                // refact 更新URL模式，引用新的视图名称
   - blog/templates/base
     - base.html              // refact 更新导航栏，添加下拉菜单
   - blog/templates/articles
     - list.html              // refact 添加状态标签，显示公开/私密和草稿/已发布
   ```

### 2025-05-01 01:07

### 11. 添加我的文章视图和草稿发布功能

**Change Type**: feature

> **Purpose**: 允许用户查看自己的所有文章，包括草稿和私密文章，并支持草稿一键发布
> **Detailed Description**:
>
> 1. 添加`my_articles`视图，显示当前用户的所有文章，不论状态和可见性
> 2. 修改`article_detail`视图，允许作者查看自己的未发布或私密文章
> 3. 添加`publish_article`视图，支持用户将草稿文章一键发布
> **Reason for Change**: 满足用户需求，允许用户管理自己的所有文章，并方便地将草稿发布
> **Impact Scope**: 影响文章管理模块，新增视图和URL
> **API Changes**: 新增`/articles/my/`和`/articles/publish/<slug>/`URL
> **Configuration Changes**: 无
> **Performance Impact**: 无明显性能影响

   ```text
   root
   - blog/apps/articles
     - views.py               // refact 添加我的文章视图和草稿发布功能
   ```

### 2025-04-30 15:33

### 4. 调整文章详情页和评论系统UI

**Change Type**: improvement

> **Purpose**: 优化文章详情页面和评论系统的交互体验
> **Detailed Description**:
>
> 1. 将编辑/删除文章的按钮移到文章元数据行
> 2. 将点赞和收藏按钮移到文章内容末尾
> 3. 修改点赞按钮样式，与收藏按钮统一为浅色背景样式
> 4. 将评论提交后的等待审核信息改为使用JS弹窗提示，替代浏览器的alert提示
> 5. 将删除文章和评论的确认页面改为JS弹窗确认，通过AJAX请求处理删除操作
> **Reason for Change**: 提升用户界面的一致性和交互体验，使用更现代的UI交互方式
> **Impact Scope**: 影响文章详情页面和评论系统的显示与交互逻辑
> **API Changes**: 无
> **Configuration Changes**: 无
> **Performance Impact**: 无明显性能影响，但改善了用户体验

   ```text
   root
   - blog/templates/articles
     - detail.html           // refact 调整文章详情页UI布局和交互
   - blog/templates/comments
     - comment.html          // refact 更新评论组件，添加JS确认弹窗和提示
   ```

### 2025-04-30 14:45:00

### 3. 修复文章预览中Markdown格式符号显示问题

**Change Type**: improvement

> **Purpose**: 优化文章预览效果，去除Markdown格式符号
> **Detailed Description**: 创建自定义Django模板过滤器`plain_text_preview`，将Markdown文本转换为纯文本预览；修改文章列表和首页模板，使用该过滤器替代原有的truncatewords过滤器
> **Reason for Change**: 原先的truncatewords过滤器无法处理Markdown格式符号，导致文章预览显示原始Markdown文本
> **Impact Scope**: 影响文章列表和首页的文章预览显示
> **API Changes**: 无
> **Configuration Changes**: 将utils应用添加到INSTALLED_APPS配置
> **Performance Impact**: 无明显性能影响

   ```text
   root
   - blog/utils/templatetags      // add 自定义模板标签和过滤器目录
     - __init__.py               // add 包初始化文件
     - markdown_filters.py       // add Markdown文本处理过滤器
   - blog/templates/articles     // refact 修改文章模板
     - home.html                 // refact 更新首页模板使用自定义过滤器
     - list.html                 // refact 更新文章列表模板使用自定义过滤器
   - blog/config/settings.py     // refact 添加utils应用到INSTALLED_APPS
   ```

### 2025-04-27 16:33:00

### 1. 初始化 .codelf 目录并更新 attention.md 和 project.md

**Change Type**: docs

> **Purpose**: 使用 .codelf 进行项目文档管理并填充最初的项目文档
> **Detailed Description**: 初始化 .codelf 目录，添加 attention.md、project.md、_changelog.md 模板文件；更新 attention.md 中的框架语言最佳实践与可重用组件目录结构；更新 project.md 中项目基本信息、依赖、项目结构等。
> **Reason for Change**: 为后续项目开发提供统一文档规范与目录结构
> **Impact Scope**: 无
> **API Changes**: 无
> **Configuration Changes**: 无
> **Performance Impact**: 无

   ```text
   root
   - .codelf               // add 项目文档目录
   - .codelf/attention.md  // refact 更新框架语言最佳实践与可重用组件结构
   - .codelf/project.md    // refact 填充项目基本信息与项目结构
   - .codelf/_changelog.md // add 模板文件
   ```

**Change Type**: {type: feature/fix/improvement/refactor/docs/test/build}

> **Purpose**: {function purpose}
> **Detailed Description**: {function detailed description}
> **Reason for Change**: {why this change is needed}
> **Impact Scope**: {other modules or functions that may be affected by this change}
> **API Changes**: {if there are API changes, detail the old and new APIs}
> **Configuration Changes**: {changes to environment variables, config files, etc.}
> **Performance Impact**: {impact of the change on system performance}

   ```text
   root
   - pkg    // {type: add/del/refact/-} {The role of a folder}
    - utils // {type: add/del/refact} {The function of the file}
   - xxx    // {type: add/del/refact} {The function of the file}
   ```

## 修改记录

### 2025-04-30: 优化文章预览功能

* 修复文章预览中Markdown格式符号显示问题：
  * 创建自定义模板过滤器`plain_text_preview`，去除Markdown格式符号
  * 过滤器可以处理各种Markdown元素（标题、加粗、链接等）
  * 在首页和文章列表页使用该过滤器，提供更好的阅读体验
  
* 技术实现细节：
  * 使用正则表达式处理各种Markdown格式
  * 将utils应用添加到INSTALLED_APPS配置
  * 在模板中加载自定义过滤器
  
* 代码实现位置：

* 修复文章预览中Markdown格式符号显示问题：
  * 创建自定义模板过滤器`plain_text_preview`，去除Markdown格式符号
  * 过滤器可以处理各种Markdown元素（标题、加粗、链接等）
  * 在首页和文章列表页使用该过滤器，提供更好的阅读体验

* 技术实现细节：
  * 使用正则表达式处理各种Markdown格式
  * 将utils应用添加到INSTALLED_APPS配置
  * 在模板中加载自定义过滤器

* 代码实现位置：

  ```text
  blog/utils/templatetags/markdown_filters.py  // 自定义过滤器实现
  blog/templates/articles/home.html           // 更新首页模板
  blog/templates/articles/list.html           // 更新列表页模板
  blog/config/settings.py                     // 更新应用配置
  ```

### 2025-04-29: 实现CI/CD工作流

* 配置GitHub Actions工作流：
  * 检测pr，并进行代码检查、测试和自动审阅

## 修改记录

### 2025-04-30 15:18

* 添加:
  * 文章创建和编辑功能
    * 创建表单模板和视图
    * 添加表单验证
    * 支持Markdown编辑器
    * 自动生成文章 slug
  * 文章删除功能
    * 添加删除确认页面
    * 权限控制（只有作者可删除）
  * 文章点赞和收藏功能
    * 创建 Like 和 Favorite 模型
    * 实现 AJAX 点赞和收藏功能
    * 显示点赞和收藏数量
  * 评论系统
    * 创建评论模型（支持嵌套回复）
    * 实现评论提交和删除功能
    * 添加评论审核机制
    * AJAX 评论交互

* 修复:
  * 修复文章详情页标签显示问题
  * 改进文章列表页分页功能

* 变更:
  * 更新导航栏布局，添加创建文章按钮
  * 改进用户界面，添加 Bootstrap Icons 支持

### 2025-04-30 15:49

* 添加:
  * 基础项目结构
  * 用户管理模块
    * 自定义用户模型
    * 用户认证（注册、登录、登出）
  * 文章管理模块
    * 文章、分类和标签模型
    * 文章列表和详情页
    * 首页布局和最新文章展示

### 2025-04-30 15:33

### 5. 修复回复评论无法删除的问题

**Change Type**: fix

> **Purpose**: 修复回复评论无法删除的问题
> **Detailed Description**:
>
> 1. 在评论模板（comment.html）中为回复评论添加了删除确认弹窗
> 2. 确保回复评论的删除按钮能正确触发删除确认弹窗
> 3. 保持与主评论删除功能一致的用户体验
> **Reason for Change**: 原先模板中只为主评论添加了删除确认弹窗，忽略了回复评论的删除弹窗
> **Impact Scope**: 影响评论系统的删除功能
> **API Changes**: 无
> **Configuration Changes**: 无
> **Performance Impact**: 无性能影响

   ```text
   root
   - blog/templates/comments
     - comment.html          // fix 为回复评论添加删除确认弹窗
   ```

### 2025-04-30 15:45

### 6. 改进文章界面与交互体验

**Change Type**: improvement

> **Purpose**: 改进首页文章预览、标签输入方式和别名处理
> **Detailed Description**:
>
> 1. 在首页文章预览的卡片底部显示文章的点赞数和收藏数
> 2. 将创建/编辑文章页面的标签选择器改为可交互的标签输入框
>    * 引入Tagify.js库实现标签输入交互
>    * 支持输入标签并按回车确认添加
>    * 可以创建多个标签，用逗号分隔
> 3. 优化文章别名(slug)处理
>    * 别名字段可以留空
>    * 如果用户未提供别名，自动使用数据库中的文章ID作为默认值
> **Reason for Change**: 提升用户使用体验，简化标签输入操作，预览更多文章信息
> **Impact Scope**: 影响首页文章显示和文章创建/编辑功能
> **API Changes**: 无
> **Configuration Changes**: 无
> **Performance Impact**: 无

   ```text
   root
   - blog/templates/articles
     - home.html             // refact 在文章预览卡片底部添加点赞和收藏计数
     - article_form.html     // refact 将标签选择器改为标签输入框
   - blog/apps/articles
     - views.py              // refact 支持标签输入处理和文章ID作为默认别名
   ```

### 2025-04-30 16:08

### 7. 修复中文标签无法显示的问题

**Change Type**: fix

> **Purpose**: 修复使用中文标签导致页面报错的问题
> **Detailed Description**:
>
> 1. 修改Tag模型，使其slug字段自动使用数据库ID，无需手动指定
> 2. 修改文章标签URL配置，使用tag_id替代tag_slug作为URL参数
> 3. 更新所有相关模板，将标签链接从使用tag.slug改为使用tag.id
> 4. 修改Article模型，优化slug字段处理，自动使用ID作为默认值
> 5. 从ArticleForm中移除slug字段，完全使用自动生成的ID作为slug
> **Reason for Change**: 解决中文标签引起的NoReverseMatch错误，URL模式只支持英文字母、数字等字符，不支持中文字符
> **Impact Scope**: 影响标签系统和文章URL生成机制
> **API Changes**: 标签URL从 `/articles/tag/<slug>/` 改为 `/articles/tag/<id>/`
> **Configuration Changes**: 无
> **Performance Impact**: 无

   ```text
   root
   - blog/apps/articles
     - models.py            // refact 修改Tag和Article模型，自动使用ID作为slug
     - views.py             // refact 修改视图函数，使用tag_id参数
     - urls.py              // refact 修改URL模式，使用int类型的tag_id
   - blog/templates/articles
     - home.html            // refact 更新标签链接，使用tag.id
     - list.html            // refact 更新标签链接，使用tag.id
     - detail.html          // refact 更新标签链接，使用tag.id
   ```

### 2025-04-30 16:12

### 8. 移除文章创建表单中的slug输入框

**Change Type**: improvement

> **Purpose**: 统一使用数据库ID作为文章slug，简化用户操作
> **Detailed Description**:
>
> 1. 删除文章创建/编辑表单中的slug输入框
> 2. 移除从标题自动生成slug的JavaScript逻辑
> 3. 确保所有文章统一使用数据库ID作为slug
> **Reason for Change**: 为避免用户设置不合规的slug值，同时简化用户操作，统一使用数据库ID作为slug，保持系统一致性
> **Impact Scope**: 影响文章创建和编辑页面的表单字段
> **API Changes**: 无
> **Configuration Changes**: 无
> **Performance Impact**: 无

   ```text
   root
   - blog/templates/articles
     - article_form.html     // refact 移除slug输入框及相关生成逻辑
   ```

### 2025-04-30 16:14

### 9. 在文章列表页添加点赞和收藏数量显示

**Change Type**: improvement

> **Purpose**: 在文章列表页展示文章获得的点赞和收藏数量
> **Detailed Description**:
>
> 1. 在文章列表页的每篇文章预览卡片底部添加点赞和收藏数量显示
> 2. 布局及样式与首页保持一致，使用图标和计数器组合展示
> **Reason for Change**: 提升用户体验，使文章列表页与首页展示风格保持一致，为读者提供更丰富的信息
> **Impact Scope**: 影响文章列表页的预览卡片显示
> **API Changes**: 无
> **Configuration Changes**: 无
> **Performance Impact**: 无

   ```text
   root
   - blog/templates/articles
     - list.html             // refact 在文章列表页添加点赞和收藏数量显示
   ```

### 2025-04-30 16:17

### 10. 隐藏文章数量为0的标签

**Change Type**: improvement

> **Purpose**: 在标签云中自动隐藏没有关联文章的标签
> **Detailed Description**:
>
> 1. 修改home、article_list、article_create和article_update视图函数
> 2. 使用Django ORM的annotate和filter功能来筛选有效标签
> 3. 只显示至少关联了一篇文章的标签
> **Reason for Change**: 提高标签云的有效性，减少无用标签的显示，避免用户点击空标签导致的不良体验
> **Impact Scope**: 影响首页、文章列表页和文章表单页的标签云显示
> **API Changes**: 无
> **Configuration Changes**: 无
> **Performance Impact**: 稍微提高查询效率，减少标签云中显示的标签数量

   ```text
   root
   - blog/apps/articles
     - views.py               // refact 筛选有效标签，隐藏空标签
   ```

# 变更日志

## 2025-04-30

* 更新自动合并PR功能，使用自定义令牌CUSTOM_GITHUB_TOKEN替代默认的GITHUB_TOKEN
* 使用仓库环境变量CUSTOM_GITHUB_TOKEN获取权限进行合并操作
* 只有非草稿状态的PR才会被自动合并

## 2025-05-06 15:40

### 19. 添加用户收藏夹功能

**Change Type**: feature, enhancement

> **Purpose**: 实现用户收藏夹功能，使用户可以查看和管理所有收藏的文章
> **Detailed Description**:
>
> 1. 新增收藏夹功能，允许用户在一个集中的页面查看和管理所有收藏的文章
> 2. 实现了以下主要功能：
>    * 新增`my_favorites`视图，获取用户收藏的所有文章并显示
>    * 创建`favorites.html`模板，美观展示收藏的文章列表
>    * 在导航栏的"我的文章"下拉菜单中添加"我的收藏夹"入口
>    * 支持在收藏夹页面直接取消收藏，并提供平滑的动画过渡效果
>    * 提供空收藏夹的友好提示和引导用户浏览文章
>    * 添加收藏小贴士，指导用户如何使用收藏功能
> 3. 优化URL结构，添加`/articles/my/favorites/`路径
> **Reason for Change**: 提升用户体验，方便用户管理和访问喜欢的文章内容
> **Impact Scope**: 影响文章管理模块，添加新的视图、URL和模板
> **API Changes**: 新增`/articles/my/favorites/` URL用于访问收藏夹
> **Configuration Changes**: 无
> **Performance Impact**: 无明显性能影响，采用了数据库优化查询方式（select_related和prefetch_related）

   ```text
   root
   - blog/apps/articles
     - views.py               // refact 添加my_favorites视图函数
     - urls.py                // refact 添加my_favorites URL路由
   - blog/templates/articles
     - favorites.html         // add 新增收藏夹页面模板
   - blog/templates/base
     - base.html              // refact 在导航栏添加收藏夹入口
   ```

## 2025-05-06 16:21

### 19. 实现文章和评论模块的单元测试

**Change Type**: test

> **Purpose**: 为文章管理模块和评论系统模块编写单元测试，确保代码质量和稳定性
> **Detailed Description**:
>
> 1. 为文章模块实现了三个测试类：
>    * ArticleModelTest：测试文章模型创建、字符串表示、URL、发布时间和浏览量增加等功能
>    * ArticleViewTest：测试文章列表、详情、创建、更新和删除等视图功能
>    * LikeFavoriteTest：测试点赞和收藏功能，包括点赞切换、收藏切换、多用户点赞和收藏夹功能
> 2. 为评论模块实现了两个测试类：
>    * CommentModelTest：测试评论模型创建、字符串表示、嵌套评论创建、评论排序和审核状态等功能
>    * CommentViewTest：测试评论提交、评论回复、评论删除和权限控制等功能
> 3. 每个测试类至少包含5个测试任务，共计26个测试任务
> **Reason for Change**: 满足项目阶段四的开发任务，提高代码质量和稳定性
> **Impact Scope**: 影响文章和评论模块的测试文件
> **API Changes**: 无
> **Configuration Changes**: 无
> **Performance Impact**: 无

   ```text
   root
   - blog/apps/articles
     - tests.py              // update 实现文章模块的单元测试
   - blog/apps/comments
     - tests.py              // update 实现评论模块的单元测试
   ```

## 2025-05-07 17:23:37

### 20. 实现Celery异步任务功能

**Change Type**: feature, enhancement

> **Purpose**: 使用Celery和Redis实现异步任务处理，优化系统性能和用户体验
> **Detailed Description**:
>
> 1. 实现Celery异步任务框架：
>    * 创建Celery应用实例配置文件 (`utils/celery/app.py`)
>    * 实现常用异步任务 (`utils/celery/tasks.py`)：邮件发送、站点统计、数据清理、浏览量处理
>    * 配置定时任务计划 (`utils/celery/schedule.py`)
>    * 提供高级任务处理接口 (`utils/celery/handlers.py`)
>    * 创建详细使用文档 (`utils/celery/README.md`)
> 2. 在Django配置中集成Celery：
>    * 配置Redis作为消息代理(Broker)和结果存储(Backend)
>    * 在settings.py中添加Celery配置
>    * 创建Celery初始化模块，在WSGI/ASGI加载时初始化
> 3. 优化现有功能：
>    * 将用户注册中的验证邮件发送改为异步处理，提高注册性能
>    * 实现文章和评论通知的异步发送
>    * 设置定时任务：站点统计生成(每天2点)、过期令牌清理(每天3点)、文章浏览量处理(每小时)
> **Reason for Change**: 提高系统性能，优化用户体验，解决同步处理耗时操作（如邮件发送）导致的响应延迟问题
> **Impact Scope**: 影响系统配置、用户注册流程和邮件发送功能
> **API Changes**: 无API变更，为内部实现优化
> **Configuration Changes**: 添加Celery和Redis相关配置到settings.py
> **Performance Impact**: 显著提高系统响应速度，特别是涉及邮件发送的操作

   ```text
   root
   - blog/utils/celery/                 // add 新增Celery异步任务模块
     - __init__.py                     // add 包初始化文件
     - app.py                          // add Celery应用实例配置
     - tasks.py                        // add 异步任务定义
     - schedule.py                     // add 定时任务配置
     - handlers.py                     // add 任务处理器和高级接口
     - README.md                       // add 使用说明文档
   - blog/config
     - settings.py                     // refact 添加Celery配置
     - celery_init.py                  // add Celery初始化模块
     - wsgi.py                         // refact 引入Celery初始化
   - blog/apps/users
     - utils.py                        // refact 修改邮件发送为异步处理
   - pyproject.toml                    // refact 添加celery和redis依赖
   ```
