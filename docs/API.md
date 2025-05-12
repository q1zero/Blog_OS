# 博客系统 RESTful API 文档

> 本文档基于项目运行时在 `http://127.0.0.1:8000/api/swagger/` 自动生成的 **Swagger** 文档整理而来，仅供离线阅读与接口快速查阅。如需查看可交互的在线文档，请访问开发环境中的 Swagger UI。

## 基础信息

- 基础 URL（Base URL）：`/api/v1/`
- 统一响应格式：JSON
- 字符编码：UTF-8
- 版本：v1

## 认证与授权

本项目采用 [JSON Web Token](https://jwt.io/)（JWT）进行认证，基于 `djangorestframework-simplejwt`。

| 接口 | 方法 | 描述 |
| ---- | ---- | ---- |
| `/api/v1/token/` | POST | 获取 **access** 和 **refresh** token |
| `/api/v1/token/refresh/` | POST | 使用 **refresh** token 刷新 **access** token |
| `/api/v1/token/verify/` | POST | 校验 **access / refresh** token 是否有效 |

请求示例（`/token/`）：
```json
{
  "username": "demo",
  "password": "your_password"
}
```

成功响应：
```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>"
}
```

> 获得 token 后，需在后续请求 Header 中加入：
>
> `Authorization: Bearer <jwt_access_token>`

---

## 资源说明

### 1. 用户（Users）

| 路径 | 方法 | 权限 | 描述 |
| ---- | ---- | ---- | ---- |
| `/users/` | GET | 公开 | 获取用户列表 |
| `/users/` | POST | 匿名 | 创建用户 |
| `/users/{id}/` | GET | 公开 | 获取用户详情 |
| `/users/{id}/` | PUT/PATCH | 仅本人 / 管理员 | 更新用户信息 |
| `/users/{id}/` | DELETE | 管理员 | 删除用户 |
| `/users/me/` | GET | 已登录 | 获取当前登录用户信息 |
| `/users/update_profile/` | PUT/PATCH | 已登录 | 更新当前登录用户信息 |

#### 数据结构

```json
{
  "id": 1,
  "username": "demo",
  "email": "demo@example.com",
  "first_name": "Demo",
  "last_name": "User",
  "bio": "自我介绍...",
  "avatar": "/media/avatars/demo.png",
  "date_joined": "2024-01-01T12:00:00Z",
  "is_active": true
}
```

---

### 2. 文章（Articles）

| 路径 | 方法 | 权限 | 描述 |
| ---- | ---- | ---- | ---- |
| `/articles/` | GET | 公开 | 获取文章列表（支持搜索 / 排序 / 过滤） |
| `/articles/` | POST | 已登录 | 创建文章 |
| `/articles/{slug}/` | GET | 公开 | 获取文章详情 |
| `/articles/{slug}/` | PUT/PATCH | 作者 / 管理员 | 更新文章 |
| `/articles/{slug}/` | DELETE | 作者 / 管理员 | 删除文章 |
| `/articles/my_articles/` | GET | 已登录 | 获取当前用户的文章，可用 `status` 过滤 `draft` / `published` |

查询参数：

- `search`: 模糊搜索 `title`, `content`
- `ordering`: 排序字段，如 `published_at`, `-views`
- `category`: 分类 `slug`
- `tag`: 标签 `slug`
- `author`: 作者 `id`

---

### 3. 分类（Categories）

| 路径 | 方法 | 权限 | 描述 |
| ---- | ---- | ---- | ---- |
| `/categories/` | GET | 公开 | 获取分类列表 |
| `/categories/` | POST | 管理员 | 创建分类 |
| `/categories/{slug}/` | GET | 公开 | 获取分类详情 |
| `/categories/{slug}/` | PUT/PATCH | 管理员 | 更新分类 |
| `/categories/{slug}/` | DELETE | 管理员 | 删除分类 |

---

### 4. 标签（Tags）

| 路径 | 方法 | 权限 | 描述 |
| ---- | ---- | ---- | ---- |
| `/tags/` | GET | 公开 | 获取标签列表 |
| `/tags/` | POST | 管理员 | 创建标签 |
| `/tags/{slug}/` | GET | 公开 | 获取标签详情 |
| `/tags/{slug}/` | PUT/PATCH | 管理员 | 更新标签 |
| `/tags/{slug}/` | DELETE | 管理员 | 删除标签 |

---

### 5. 评论（Comments）

| 路径 | 方法 | 权限 | 描述 |
| ---- | ---- | ---- | ---- |
| `/comments/` | GET | 公开 | 获取评论列表（支持文章 / 父评论过滤） |
| `/comments/` | POST | 已登录 | 创建评论（`article`, `content`, 可选 `parent`） |
| `/comments/{id}/` | GET | 公开 | 获取评论详情 |
| `/comments/{id}/` | PUT/PATCH | 作者 | 更新评论 |
| `/comments/{id}/` | DELETE | 作者 / 管理员 | 删除评论 |
| `/comments/{id}/approve/` | POST | 管理员 | 批准评论 |
| `/comments/pending/` | GET | 管理员 | 待审核评论列表 |

查询参数：

- `article`: 文章 ID
- `parent`: 上级评论 ID（空=仅顶级评论）

---

## 公共错误结构

所有错误响应遵循以下 JSON 结构：

```json
{
  "detail": "错误信息描述"
}
```

若字段验证失败，将返回字段-错误键值对：

```json
{
  "username": ["用户名已存在"],
  "password": ["密码过短"]
}
```

---

## Swagger & ReDoc

- Swagger UI：`/api/swagger/`
- ReDoc：`/api/redoc/`
- 原始 OpenAPI JSON：`/api/swagger.json`

---

> **提示**：若接口或字段与实际返回不符，请以在线 Swagger 文档为准。此离线文档可能因代码变更而滞后。
