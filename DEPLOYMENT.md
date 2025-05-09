# Blog_OS 部署指南

## 1. 概述

本文档旨在指导用户如何使用 Docker 和 Docker Compose 部署 Blog_OS 项目。

## 2. 先决条件

在部署之前，请确保您已安装以下软件：

*   Docker Engine
*   Docker Compose

## 3. 环境变量配置

您需要在项目根目录下创建一个名为 [.env](./.env:0) 的文件来存储环境变量。

以下是一个 [.env](./.env:0) 文件的示例，其中包含了在 [docker-compose.yml](./docker-compose.yml:0) 中使用的所有变量：

```env
MYSQL_DATABASE=your_db_name
MYSQL_USER=your_db_user
MYSQL_PASSWORD=your_db_password
MYSQL_ROOT_PASSWORD=your_db_root_password
# DJANGO_SETTINGS_MODULE 已经在 docker-compose.yml 中设置，通常不需要在 .env 中重复
# CELERY_BROKER_URL 和 CELERY_RESULT_BACKEND 也已经在 docker-compose.yml 中设置
```

**请记得将示例中的占位符（如 your_db_name）替换为您的实际值。**

## 4. 构建与运行

在项目根目录下执行以下命令来构建 Docker 镜像并启动所有服务：

```bash
docker-compose up --build -d
```

*   --build：此选项会在启动容器前重新构建镜像。
*   -d：此选项使容器在后台（detached mode）运行。

初次运行项目时，您可能需要执行数据库迁移。可以通过以下命令进入 web 容器并执行迁移：

```bash
docker-compose exec web python [blog/manage.py](blog/manage.py:0) migrate
```

如果您需要创建一个超级用户，可以执行：

```bash
docker-compose exec web python [blog/manage.py](blog/manage.py:0) createsuperuser
```

## 5. 访问应用

当所有服务成功启动后，您可以通过浏览器访问以下地址来查看应用程序：

[http://localhost:8000](http://localhost:8000)

## 6. 常用命令

以下是一些常用的 Docker Compose 命令：

*   **查看日志：**
    ```bash
    docker-compose logs -f
    # 或者查看特定服务的日志，例如 web 服务：
    docker-compose logs -f web
    ```
*   **停止服务：**
    ```bash
    docker-compose down
    ```
*   **重启服务：**
    ```bash
    docker-compose restart
    ```
*   **进入容器：**
    ```bash
    # 将 [service_name] 替换为您想要进入的服务名称，例如 web
    docker-compose exec [service_name] bash
    # 或者，如果 bash 不可用，可以尝试 sh
    docker-compose exec [service_name] sh
    ```

## 7. 注意事项

本项目的技术栈中包含 Elasticsearch，用于提供搜索功能。然而，为了简化初始部署，当前的 [docker-compose.yml](./docker-compose.yml:0) 配置文件中并未包含 Elasticsearch 服务。如果您需要使用搜索等完整功能，可能需要手动将 Elasticsearch 服务添加到 [docker-compose.yml](./docker-compose.yml:0) 文件中，并进行相应的配置。