## Blog_OS

> 项目描述：一个基于 Django 的博客平台，提供用户管理、文章发布、评论交互等功能。
> 项目目的：搭建一个功能完善、易扩展的博客系统，支持用户认证、RESTful API 接口以及模板渲染。
> 项目状态：开发中
> 项目团队：
> * 开发者 A：负责用户管理模块和权限模块 (分支:710)
> * 开发者 B：负责文章管理模块和评论系统 (分支:zjy)
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
- .codelf            // 项目文档目录
    - attention.md
    - project.md
    - _changelog.md
- blog               // Django 项目主目录
    - manage.py      // Django 管理命令入口
    - apps           // 项目应用模块
        - users      // 用户管理模块
        - articles   // 文章管理模块
            - models.py      // 文章、分类和标签模型
            - views.py       // 文章列表、详情和首页视图
            - urls.py        // 文章URL配置
            - admin.py       // 管理后台配置
        - comments   // 评论系统模块
    - config         // 配置目录（settings, urls, wsgi, asgi）
    - utils          // 通用工具函数
    - templates      // 模板目录
        - base       // 基础模板
        - articles   // 文章相关模板
            - list.html      // 文章列表页
            - detail.html    // 文章详情页
            - home.html      // 首页模板
    - static         // 静态文件目录
        - css        // 样式文件目录
            - style.css      // 主要样式文件
- plan.md            // 项目开发计划
- pyproject.toml     // 依赖和项目配置
- README.md          // 项目说明文档
- uv.lock            // 依赖锁文件
```

## 模块说明

### 文章管理模块

文章管理模块提供了博客平台的核心功能，包括文章、分类和标签的管理。

**主要模型：**

1. **Article（文章）**
   - 基本信息：标题、内容、作者、创建时间、更新时间、发布时间
   - 状态管理：草稿/已发布状态，公开/私密可见性
   - 关联信息：分类（外键）、标签（多对多）

2. **Category（分类）**
   - 基本信息：名称、别名（slug）、描述、创建时间、更新时间

3. **Tag（标签）**
   - 基本信息：名称、别名（slug）、创建时间、更新时间

**主要功能：**

1. 网站首页展示（按发布时间展示最新的文章）
2. 文章列表展示（支持分类和标签过滤）
3. 文章详情展示（支持Markdown渲染和代码高亮）
4. 文章管理后台（支持文章、分类和标签的CRUD操作）

**URL结构：**

- `/` - 首页，显示最新文章
- `/articles/` - 文章列表
- `/articles/<slug>/` - 文章详情
- `/articles/category/<slug>/` - 按分类过滤文章
- `/articles/tag/<slug>/` - 按标签过滤文章