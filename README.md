# Blog_OS

一个功能丰富的博客系统，基于 Django和 Docker构建。

**Demo 链接:** [https://blog-os-235.replit.app](https://blog-os-235.replit.app)
**GitHub 仓库:** [https://github.com/q1zero/Blog_OS](https://github.com/q1zero/Blog_OS)

## 主要功能

*   **文章管理:** 支持 Markdown语法的文章发布、编辑、删除功能。
*   **评论系统:** 用户可以对文章进行评论。
*   **用户认证:** 包括用户注册、登录、密码修改、头像更换等。
*   **GitHub 登录:** 支持通过 GitHub账号快捷登录。
*   **搜索功能:** 可以搜索文章。
*   **点赞与收藏:** 用户可以点赞和收藏喜欢的文章。
*   **API 接口:** 提供 RESTful API接口，使用 JWT进行认证，并提供 Swagger API文档。
*   **异步任务:** 使用 Celery和 Redis处理异步任务（例如邮件发送等）。
*   **访问日志:** 记录用户访问日志。
*   **后台管理:** 集成 Django Admin进行数据管理。
*   **调试工具:** 集成 Django Debug Toolbar方便开发调试。

## 技术栈

*   **后端:** Python 3.12+, Django 4.2.x
*   **API:** Django REST framework, djangorestframework-simplejwt (JWT 认证), drf-yasg (Swagger UI)
*   **数据库:** MySQL
*   **异步任务:** Celery, Redis
*   **用户认证:** django-allauth (包括 GitHub社交登录)
*   **内容处理:** Markdown, Pillow (图片处理)
*   **容器化:** Docker, Docker Compose
*   **其他:** python-decouple (环境变量管理), requests

## 安装与启动

### 1. 本地开发环境

**前提:**
*   Python >= 3.12
*   MySQL 数据库
*   Redis 服务
*   uv (或 pip) 用于安装依赖

**步骤:**

1.  **克隆仓库:**
    ```bash
    git clone https://github.com/q1zero/Blog_OS.git
    cd Blog_OS
    ```

2.  **创建并激活虚拟环境 (推荐):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate  # Windows
    ```

3.  **安装依赖:**
    项目使用 [pyproject.toml](pyproject.toml:0) 管理依赖。您可以使用 uv或 pip安装。
    ```bash
    uv pip install -r requirements.txt # (如果存在 requirements.txt, 通常由 poetry export 生成)
    # 或者根据 pyproject.toml 手动安装，或使用 poetry install (如果项目使用 Poetry 管理)
    # 鉴于 pyproject.toml 中列出了依赖，通常会有一个 requirements.txt 文件或使用如 Poetry/PDM 的工具。
    # 假设有一个 requirements.txt:
    # pip install -r requirements.txt
    ```
    *注意：根据 [pyproject.toml](pyproject.toml:0) 的结构，最佳实践是使用像 Poetry或 PDM这样的工具。如果没有，可以手动从 [pyproject.toml](pyproject.toml:0) 中提取依赖列表并安装。为简化，假设有 requirements.txt或者直接安装列出的主要依赖。*

4.  **配置环境变量:**
    创建 .env文件在项目根目录，并设置数据库连接等信息（参考 [blog/config/settings.py](blog/config/settings.py:102) 中的 DATABASES配置和 python-decouple的使用）。
    例如：
    ```env
    SECRET_KEY=your_secret_key
    DEBUG=True
    DB_NAME=blog_os
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=localhost
    DB_PORT=3306
    CELERY_BROKER_URL=redis://localhost:6379/0
    CELERY_RESULT_BACKEND=redis://localhost:6379/0
    # GitHub OAuth
    GITHUB_CLIENT_ID=your_github_client_id
    GITHUB_CLIENT_SECRET=your_github_client_secret
    # Email settings (if needed for local testing)
    EMAIL_HOST_USER=your_email
    EMAIL_HOST_PASSWORD=your_email_password
    ```

5.  **执行数据库迁移:**
    ```bash
    python blog/manage.py migrate
    ```

6.  **创建超级用户 (可选):**
    ```bash
    python blog/manage.py createsuperuser
    ```

7.  **启动开发服务器:**
    ```bash
    python blog/manage.py runserver
    ```
    访问 http://127.0.0.1:8000/

8.  **启动 Celery Worker (在另一个终端):**
    ```bash
    celery -A blog.config.celery_init worker -l info
    ```

9.  **启动 Celery Beat (在另一个终端, 如果有定时任务):**
    ```bash
    celery -A blog.config.celery_init beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    ```

### 2. 使用 Docker启动

**前提:**
*   Docker
*   Docker Compose

**步骤:**

1.  **克隆仓库:**
    ```bash
    git clone https://github.com/q1zero/Blog_OS.git
    cd Blog_OS
    ```

2.  **配置环境变量:**
    复制 .env.example (如果提供) 为 .env文件，或者直接创建 .env文件，并填写必要的环境变量。这些变量将被 [docker-compose.yml](docker-compose.yml:0) 使用。
    例如：
    ```env
    MYSQL_DATABASE=blog_os_docker
    MYSQL_USER=blog_user_docker
    MYSQL_PASSWORD=your_strong_password
    MYSQL_ROOT_PASSWORD=your_strong_root_password
    # SECRET_KEY, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET 等也应在此配置
    ```

3.  **构建并启动容器:**
    ```bash
    docker-compose up --build
    ```
    这将会启动 web服务、数据库 (db)、Redis以及 Celery的 worker和 beat服务。

4.  **执行数据库迁移 (在容器启动后, 可能需要在另一个终端执行):**
    ```bash
    docker-compose exec web python blog/manage.py migrate
    ```

5.  **创建超级用户 (可选):**
    ```bash
    docker-compose exec web python blog/manage.py createsuperuser
    ```
    访问 http://localhost:8000/

## 部署

*   **Replit:** 该项目已经配置为可以在 Replit上部署和运行。详情请参考项目中的 [replit.nix](replit.nix:0) 和 .replit文件，以及 [docs/REPLIT_DEPLOYMENT.md](docs/REPLIT_DEPLOYMENT.md:0) 文档。
*   **其他平台:** 关于通用的部署指南，请参考 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md:0) 文档。通常涉及配置 Web服务器 (如 Nginx或 Apache)、WSGI服务器 (如 Gunicorn或 uWSGI)、静态文件和媒体文件的处理，以及生产环境下的数据库和 Celery配置。

## 项目结构

```
Blog_OS/
├── blog/                     # Django 项目主目录
│   ├── apps/                 # 应用模块
│   │   ├── articles/         # 文章相关功能
│   │   ├── comments/         # 评论相关功能
│   │   └── users/            # 用户相关功能
│   ├── config/               # 项目配置 (settings.py, urls.py, wsgi.py, asgi.py, celery_init.py)
│   ├── logs/                 # 日志文件存放目录
│   ├── media/                # 用户上传的媒体文件
│   ├── static/               # 项目的静态文件 (CSS, JavaScript, 图片)
│   ├── templates/            # Django 模板文件
│   ├── utils/                # 公用程序和工具 (API 实现, Celery 任务, 日志记录等)
│   └── manage.py             # Django 命令行工具
├── docs/                     # 项目文档
├── .github/                  # GitHub Actions 等配置
├── .gitignore                # Git 忽略文件配置
├── docker-compose.yml        # Docker Compose 配置文件
├── Dockerfile                # Docker 镜像构建文件
├── pyproject.toml            # Python 项目元数据和依赖 (PEP 621)
├── README.md                 # 本文件
├── replit.nix                # Replit 环境配置 (Nix)
└── .replit                   # Replit 配置文件
```

## 贡献指南

(暂未提供，欢迎提出 Issue或 Pull Request)

## 许可证

(项目当前未指定明确的开源许可证。)
