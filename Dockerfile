# 基础镜像：使用 Python 3.12 slim 版本
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
# PYTHONUNBUFFERED=1 确保 Python 日志直接输出到终端，不进行缓存
ENV PYTHONUNBUFFERED 1
# PYTHONDONTWRITEBYTECODE=1 防止 Python 生成 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1

# 安装系统级依赖
# 更新 apt 包索引，安装编译工具和 MySQL 客户端开发库
# --no-install-recommends 避免安装不必要的推荐包
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libmysqlclient-dev \
    # 清理 apt 缓存，减少镜像体积
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制项目依赖文件
COPY requirements.txt .

# 安装 Python 依赖
# 首先使用 pip 安装 uv
RUN pip install --no-cache-dir uv
# 然后使用 uv 安装 requirements.txt 中的所有依赖
# --no-cache-dir 禁用缓存，减少镜像体积
RUN uv pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
# 将当前目录 (构建上下文的根目录) 下的所有文件复制到容器的 /app 目录
COPY . /app/

# 声明应用程序运行时使用的端口
# 这只是一个元数据声明，实际端口映射在 docker run 或 docker-compose.yml 中完成
EXPOSE 8000

# 默认启动命令
# 这里注释掉，因为 docker-compose.yml 中会为不同服务 (web, celery_worker, celery_beat) 指定不同的 command
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]