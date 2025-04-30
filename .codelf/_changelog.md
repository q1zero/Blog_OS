## {datetime: YYYY-MM-DD HH:mm:ss}

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

- 修复文章预览中Markdown格式符号显示问题：
  - 创建自定义模板过滤器`plain_text_preview`，去除Markdown格式符号
  - 过滤器可以处理各种Markdown元素（标题、加粗、链接等）
  - 在首页和文章列表页使用该过滤器，提供更好的阅读体验
  
- 技术实现细节：
  - 使用正则表达式处理各种Markdown格式
  - 将utils应用添加到INSTALLED_APPS配置
  - 在模板中加载自定义过滤器
  
- 代码实现位置：

  ```text
  blog/utils/templatetags/markdown_filters.py  // 自定义过滤器实现
  blog/templates/articles/home.html           // 更新首页模板
  blog/templates/articles/list.html           // 更新列表页模板
  blog/config/settings.py                     // 更新应用配置
  ```

### 2025-04-29: 实现CI/CD工作流

- 配置GitHub Actions工作流：
  - 检测pr，并进行代码检查、测试和自动审阅
