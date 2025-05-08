# GitHub认证功能

这个模块提供了GitHub第三方登录功能，可以让用户使用GitHub账号直接登录Blog_OS应用，无需注册或输入密码。

## 功能

- GitHub一键登录，无需注册或输入密码
- 自动创建用户账号，关联GitHub身份
- GitHub应用配置管理

## 使用方法

### 1. 在GitHub上创建OAuth应用

1. 登录GitHub
2. 进入Settings > Developer settings > OAuth Apps
3. 点击"New OAuth App"
4. 填写应用信息：
   - Application name: Blog_OS
   - Homepage URL: http://127.0.0.1:8000
   - Authorization callback URL: http://127.0.0.1:8000/github/callback/

   **注意**: 回调URL必须与代码中的redirect_uri完全匹配，包括末尾的斜杠。如果您修改了代码中的redirect_uri，也需要在GitHub上更新回调URL。

### 2. 配置settings.py

在settings.py文件中添加以下配置：

```python
# GitHub认证配置
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'APP': {
            'client_id': '您的GitHub客户端ID',
            'secret': '您的GitHub客户端密钥',
            'key': ''
        },
        'SCOPE': ['user:email'],
        'VERIFIED_EMAIL': True,
    }
}
```

### 3. 初始化GitHub应用配置

运行以下命令初始化GitHub应用配置：

```bash
python -m utils.github_auth.setup
```

### 4. 在模板中添加GitHub登录按钮

在登录模板中添加GitHub登录按钮：

```html
<div class="d-grid gap-2">
    <a href="{% url 'github_auth:login' %}" class="btn btn-dark">
        <i class="fab fa-github"></i> 使用GitHub登录
    </a>
</div>
```

## 管理工具

### 清理所有社交账号相关的对象

```bash
python -m utils.github_auth.cli --clean
```

### 创建GitHub应用配置

```bash
python -m utils.github_auth.cli --create
```

### 重置GitHub应用配置

```bash
python -m utils.github_auth.cli --reset
```

## 登录流程

1. 用户点击"GitHub登录"按钮
2. 系统重定向到GitHub授权页面
3. 用户授权应用访问其GitHub账号
4. GitHub重定向回应用，带有授权码
5. 应用自动创建用户账号并登录用户
6. 用户被重定向到首页，已登录状态

## 故障排除

### "The redirect_uri is not associated with this application"

如果您遇到这个错误，请检查以下几点：

1. 确保在GitHub上注册的OAuth应用程序的回调URL与代码中的redirect_uri完全匹配。

2. 尝试不同的回调URL格式：
   - 访问测试页面：`http://127.0.0.1:8000/github/test-urls/`
   - 点击不同的测试链接，看哪一个可以正常工作
   - 如果某个格式可以正常工作，请在GitHub上更新您的OAuth应用的回调URL为该格式

3. 检查URL编码问题：
   - 访问调试页面：`http://127.0.0.1:8000/github/debug/`
   - 查看原始重定向URI和编码后的重定向URI
   - 尝试使用不同的编码方式的测试链接

4. 修改代码中的redirect_uri：
   - 打开`utils/github_auth/github_auth.py`文件
   - 修改`redirect_uri`变量的值，使其与GitHub上注册的回调URL完全匹配
   - 重启Django开发服务器

5. 常见的回调URL格式问题：
   - 末尾的斜杠：`http://127.0.0.1:8000/github/callback/` vs `http://127.0.0.1:8000/github/callback`
   - 域名：`http://127.0.0.1:8000` vs `http://localhost:8000`
   - 协议：`http://` vs `https://`
   - 端口：`:8000` vs 无端口

### "OSError: [Errno 22] Invalid argument"

如果您遇到这个错误，这通常是因为URL编码问题。请尝试以下步骤：

1. 使用`localhost`而不是`127.0.0.1`作为回调URL的域名
2. 在GitHub上更新您的OAuth应用的回调URL为`http://localhost:8000/github/callback`
3. 修改`utils/github_auth/github_auth.py`文件中的`redirect_uri`变量，使其与GitHub上的回调URL匹配
4. 重启Django开发服务器

### 其他问题

如果您遇到其他问题，请尝试以下步骤：

1. 清理所有社交账号相关的对象：`python -m utils.github_auth.cli --clean`
2. 重新创建GitHub应用配置：`python -m utils.github_auth.cli --create`
3. 重启 Django 开发服务器
4. 清除浏览器缓存和 Cookie
