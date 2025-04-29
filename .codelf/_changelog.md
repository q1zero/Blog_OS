## {datetime: YYYY-MM-DD HH:mm:ss}

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

### 2. {function simple description}

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

### 3. {function simple description}

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

### 2025-04-28: 实现文章管理模块（阶段一）

- 创建文章模型、分类模型和标签模型，包含以下功能：
  - 文章可以设置状态（草稿/已发布）和可见性（公开/私密）
  - 文章支持分类和标签，实现多对多关系
  - 实现文章的创建时间、更新时间和发布时间记录
  
- 实现基础的文章列表和详情视图：
  - 支持通过分类和标签过滤文章
  - 实现分页显示
  - 整合Markdown渲染支持
  - 添加目录生成功能
  - 提供相关文章推荐功能
  
- 创建文章相关的模板：
  - 文章列表页面，支持分类和标签过滤
  - 文章详情页面，支持Markdown渲染和代码高亮
  - 添加响应式设计支持

- 设置管理后台：
  - 为文章、分类和标签配置管理界面
  - 添加筛选、搜索和排序功能
  
- 配置项目设置：
  - 注册文章和评论应用
  - 配置静态文件和媒体文件路径
  - 设置模板目录

### 2025-04-29: 实现博客首页功能

- 添加首页视图功能：
  - 创建home视图函数，获取最新发布的文章
  - 按发布时间降序排列文章
  - 限制显示8篇最新文章
  
- 创建首页模板：
  - 设计网格布局，展示最新文章卡片
  - 添加欢迎信息和网站介绍
  - 显示文章标题、发布时间、分类和标签
  - 添加文章摘要和"阅读全文"按钮
  - 保留侧边栏显示分类和标签云
  
- 配置URL路由：
  - 将首页视图设置为网站根URL的响应视图
  - 保持原有的文章相关URL结构
  
- 更新项目文档：
  - 更新项目结构说明
  - 添加首页功能描述
  - 更新URL结构文档

### 2025-04-29: 实现用户管理模块功能（开发者A）

- 实现自定义用户模型：
  - 继承 AbstractUser，添加自定义字段
  - 配置 AUTH_USER_MODEL 设置
  - 实现用户角色逻辑

- 添加用户认证功能：
  - 实现用户注册视图和模板
  - 实现用户登录/登出功能
  - 集成 djangorestframework-simplejwt 实现 JWT 认证

- 配置 Django Admin 界面：
  - 为自定义用户模型设置管理界面
  - 添加用户管理功能（创建、编辑、删除用户）
  - 添加过滤和搜索功能

- 定义用户相关URL：
  - 设置用户注册、登录、登出URL
  - 配置用户个人资料URL
  - 集成到项目主URL配置
  
- 代码实现详情：

  ```text
  apps/users/models.py     // 自定义User模型定义
  apps/users/forms.py      // 用户注册和登录表单
  apps/users/views.py      // 用户注册、登录、登出视图
  apps/users/urls.py       // 用户相关URL配置
  apps/users/admin.py      // 用户管理后台配置
  templates/users/         // 用户相关模板（注册、登录等）
  config/settings.py       // AUTH_USER_MODEL和认证配置
  config/urls.py           // 主URL配置更新
  ```

### 2025-04-29 17:33:36

### 2. 实现用户管理模块功能

**Change Type**: feature

> **Purpose**: 实现博客系统的用户认证和管理功能
> **Detailed Description**: 创建自定义用户模型继承AbstractUser；实现用户注册、登录、登出功能；集成JWT认证；配置Django Admin后台管理；设置用户相关URL路由
> **Reason for Change**: 为博客系统提供必要的用户管理基础设施
> **Impact Scope**: 影响文章模块中的作者关联
> **API Changes**: 添加用户注册、登录API端点
> **Configuration Changes**: 配置AUTH_USER_MODEL和JWT设置
> **Performance Impact**: 无明显性能影响

   ```text
   root
   - blog/apps/users             // add 用户管理模块
     - models.py                 // add 自定义User模型
     - forms.py                  // add 用户表单
     - views.py                  // add 用户视图
     - urls.py                   // add 用户URL配置
     - admin.py                  // add 用户管理后台
   - blog/templates/users        // add 用户模板目录
     - register.html            // add 注册模板
     - login.html               // add 登录模板
     - profile.html             // add 个人资料模板
   - blog/config/settings.py     // refact 更新AUTH_USER_MODEL和JWT配置
   - blog/config/urls.py         // refact 更新主URL配置
   ```
