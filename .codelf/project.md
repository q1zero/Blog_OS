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
* mysqlclient>=2.2.0：MySQL 数据库驱动

## 开发环境

* Python 3.12+
* MySQL 8.0
* VS Code 或 PyCharm
* 虚拟环境管理（venv）
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
        - comments   // 评论系统模块
    - config         // 配置目录（settings, urls, wsgi, asgi）
    - utils          // 通用工具函数
- plan.md            // 项目开发计划
- pyproject.toml     // 依赖和项目配置
- README.md          // 项目说明文档
- uv.lock            // 依赖锁文件
```