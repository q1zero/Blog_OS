## 2025-05-06 10:21

### 15. 实现评论敏感词过滤功能

**Change Type**: feature

> **Purpose**: 自动检测评论内容中的敏感词，并根据检测结果自动审核或标记为待审核。
> **Detailed Description**:
>
> 1. 在 `utils` 应用中创建 `SensitiveWord` 模型，用于存储敏感词列表。
> 2. 在 Django Admin 后台注册 `SensitiveWord` 模型，方便管理员添加和管理敏感词。
> 3. 修改评论提交视图 (`apps/comments/views.py`) 的逻辑：
>     * 在评论保存前，检查评论内容是否包含数据库中定义的任何敏感词。
>     * 如果不包含敏感词，评论的 `is_approved` 状态设为 `True`，并提示用户“评论已成功提交！”。
>     * 如果包含敏感词，评论的 `is_approved` 状态设为 `False`，并提示用户“评论已提交，检测到可能包含敏感内容，将进行审核。”。
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
> 3. 为管理员在导航栏添加“审核评论”链接
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
> 2. 更新导航栏，将“我的文章”改为下拉菜单，包含“已发布”和“草稿箱”选项
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
