# GitHub认证功能

这个模块提供了GitHub第三方登录功能，可以让用户使用GitHub账号直接登录Blog_OS应用，无需注册或输入密码。

## 功能

- GitHub一键登录，无需注册或输入密码
- 自动创建用户账号，关联GitHub身份
- GitHub应用配置管理
- 多环境支持（本地开发、Replit等）

## 使用方法

### 1. 自动配置回调URL（推荐）

运行以下命令自动检测环境并配置回调URL：

```bash
python -m utils.github_auth.setup_callback
```

这个脚本会：

1. 自动检测您的环境（本地开发、Replit等）
2. 生成所有可能的回调URL（包括HTTP和HTTPS两个版本）
3. 更新settings.py文件中的GITHUB_CALLBACK_URLS配置
4. 提示您在GitHub OAuth应用中添加这些回调URL

### 2. 在GitHub上创建OAuth应用

1. 登录GitHub
2. 进入Settings > Developer settings > OAuth Apps
3. 点击"New OAuth App"
4. 填写应用信息：
   - Application name: Blog_OS
   - Homepage URL: 您的应用主页URL（如 `https://blog-os-235.replit.app/`）
   - Authorization callback URL: 添加所有可能的回调URL，每行一个，例如：

     ```
     http://127.0.0.1:8000/accounts/github/callback
     http://localhost:8000/accounts/github/callback
     https://blog-os-235.replit.app/accounts/github/callback
     http://blog-os-235.replit.app/accounts/github/callback
     ```

   **注意**:
   - 从2023.11月起，GitHub OAuth应用支持在同一个输入框中添加多个回调URL（每行一个）
   - 必须完全匹配包括协议(http/https)、域名、路径和端口号
   - 对于同一域名，建议同时添加HTTP和HTTPS两个版本的回调URL
   - 必须添加所有可能的域名回调URL，包括本地测试域名和生产环境域名
   - 特别是在Replit环境中，回调URL一定要使用正确的Replit域名（如 `https://blog-os-235.replit.app/accounts/github/callback`）

### 3. 在settings.py中配置GitHub应用

在settings.py文件中添加以下配置：

```python
# GitHub认证配置
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'APP': {
            'client_id': '您从GitHub获取的Client ID',
            'secret': '您从GitHub获取的Client Secret',
            'key': '',
        },
        'SCOPE': ['user:email'],
        'VERIFIED_EMAIL': True,
    }
}

# 允许用户在没有电子邮件的情况下使用社交账号登录
SOCIALACCOUNT_EMAIL_REQUIRED = False

# GitHub OAuth配置
# 配置所有可能的回调URL
GITHUB_CALLBACK_URLS = [
    "http://127.0.0.1:8000/accounts/github/callback",
    "http://localhost:8000/accounts/github/callback",
    "https://blog-os-235.replit.app/accounts/github/callback",  # HTTPS版本
    "http://blog-os-235.replit.app/accounts/github/callback",   # HTTP版本
]

# 使用第一个URL作为默认回调URL
GITHUB_CALLBACK_URL = GITHUB_CALLBACK_URLS[0]
```

## 在Replit环境中使用

在Replit环境中使用GitHub登录时，需要特别注意以下几点：

1. **正确配置回调URL**：确保您在GitHub OAuth应用和settings.py中都添加了正确的Replit域名回调URL
2. **协议匹配**：必须确保回调URL的协议（HTTP/HTTPS）与认证请求中使用的协议完全匹配
   - 如果用户通过HTTP访问您的应用，则使用的回调URL也必须是HTTP版本
   - 如果用户通过HTTPS访问您的应用，则使用的回调URL也必须是HTTPS版本
   - 建议在GitHub OAuth应用设置中同时添加HTTP和HTTPS两个版本
3. **域名格式**：Replit域名格式通常是 `https://{repl-name}.{username}.repl.co` 或新版 `https://{repl-name}.replit.app`

如果您在Replit环境中遇到 `redirect_uri` 不匹配的错误：

1. 查看GitHub应用设置中的回调URL是否正确包含您的Replit域名（HTTP和HTTPS两个版本）
2. 确认settings.py中的GITHUB_CALLBACK_URLS包含正确的Replit域名（HTTP和HTTPS两个版本）
3. 检查授权URL中的redirect_uri参数与GitHub应用设置中的URL完全匹配（特别注意HTTP/HTTPS）
4. 运行 `setup_callback.py` 脚本更新配置

## 故障排除

### 1. redirect_uri不匹配错误

如果遇到以下错误：

```
Be careful!
The redirect_uri is not associated with this application.
The application might be misconfigured or could be trying to redirect you to a website you weren't expecting.
```

说明GitHub OAuth应用中配置的回调URL与实际请求中的回调URL不匹配。解决方法：

1. 登录GitHub，进入OAuth应用设置
2. 检查Authorization callback URL字段
3. 确认您添加了所有可能的回调URL，包括当前使用的域名
4. 特别注意检查协议（HTTP/HTTPS）是否匹配
   - 查看浏览器中GitHub授权URL，找到其中的redirect_uri参数
   - 确保该参数值（包括协议）与GitHub应用设置中的一个回调URL完全一致
5. 格式必须完全匹配，包括协议(http/https)、域名、路径和端口号
6. 保存设置后重新测试

### 2. 授权成功但登录失败

如果GitHub授权成功但无法完成登录，请检查：

1. 系统日志中的详细错误信息
2. GitHub用户信息API调用是否成功
3. 数据库中的用户创建和更新是否成功

## 流程说明

1. 用户点击"使用GitHub登录"按钮
2. 系统根据当前访问域名构建适当的回调URL（必须与GitHub应用设置匹配）
3. 用户被重定向到GitHub授权页面
4. 用户授权后，GitHub重定向回应用的回调URL
5. 系统验证授权码并获取访问令牌
6. 使用访问令牌获取用户信息
7. 创建或更新本地用户账户
8. 自动登录用户并重定向到首页

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
