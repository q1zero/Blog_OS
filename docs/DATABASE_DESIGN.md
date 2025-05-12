# 数据库设计文档

## 目录
1. [用户系统 (users app)](#用户系统-users-app)
2. [文章系统 (articles app)](#文章系统-articles-app)
3. [评论系统 (comments app)](#评论系统-comments-app)
4. [工具 / 其它 (utils app)](#工具--其它-utils-app)
5. [设计要点 & 说明](#设计要点--说明)
6. [实体关系图](#实体关系图)

---

## 用户系统 (users app)

### 1. `users_user`
| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | PK, AutoField | 主键 |
| username | varchar(150) | 唯一，登录名 (Django 默认) |
| first_name / last_name | varchar(150) | 姓名 (Django 默认) |
| email | varchar(254) | 邮箱 (Django 默认) |
| is_staff / is_active | bool | 管理员 / 启用 (Django 默认) |
| date_joined | datetime | 注册时间 (Django 默认) |
| bio | text, NULL | 个人简介 |
| avatar | varchar | 头像文件路径，NULL，默认 `avatars/test.jpg` |

> Django `AbstractUser` 其余字段不赘述。

关联关系：
* **1 - N** ：与 `articles_article`（author）
* **1 - N** ：与 `comments_comment`（author）
* **1 - N** ：与 `articles_like`、`articles_favorite`
* **1 - N** ：与 `users_emailverification`

---

### 2. `users_emailverification`
| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | PK |
| user_id | FK -> users_user | 外键，用户 |
| token | uuid, unique | 校验 Token |
| created_at | datetime | 创建时间 |
| expires_at | datetime | 过期时间 |
| verified | bool | 是否已验证 |

---

## 文章系统 (articles app)

### 3. `articles_category`
| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | PK |
| name | varchar(100) | 分类名称 |
| slug | slug, unique | 别名，用于 URL |
| description | text | 描述，可空 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

索引 / 约束： `ordering = ['-created_at']`

---

### 4. `articles_tag`
| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | PK |
| name | varchar(50) | 标签名称 |
| slug | slug | 别名，可空 (save 时若空将回写 id) |
| created_at | datetime |
| updated_at | datetime |

---

### 5. `articles_article`
| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | PK |
| title | varchar(200) | 标题 |
| slug | slug, unique | 别名，若空以 id 回写 |
| content | longtext | 正文 |
| author_id | FK -> users_user | 作者 |
| category_id | FK -> articles_category, NULL | 分类 |
| status | varchar(10) | 草稿 / 已发布 (`draft` / `published`) |
| visibility | varchar(10) | 公开 / 私密 (`public` / `private`) |
| published_at | datetime, NULL | 发布时间 (发布时自动填充) |
| views_count | int | 浏览量 |
| created_at | datetime |
| updated_at | datetime |

多对多：`tags` -> `articles_tag` (Django 自动创建中间表 `articles_article_tags`)

索引：
* `(author_id, status)` `author_status_idx`
* `(status, visibility)` `status_visibility_idx`

---

### 6. `articles_like`
| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | PK |
| user_id | FK -> users_user |
| article_id | FK -> articles_article |
| created_at | datetime |

唯一约束：`unique_together (user_id, article_id)`，同一用户对同一文章只能点赞一次。

---

### 7. `articles_favorite`
| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | PK |
| user_id | FK -> users_user |
| article_id | FK -> articles_article |
| created_at | datetime |

唯一约束：`unique_together (user_id, article_id)`，同一用户对同一文章只能收藏一次。

---

## 评论系统 (comments app)

### 8. `comments_comment`
| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | PK |
| content | text | 评论内容 |
| author_id | FK -> users_user | 评论者 |
| article_id | FK -> articles_article | 所属文章 |
| parent_id | FK -> comments_comment, NULL | 父评论 (用于嵌套) |
| is_approved | bool | 是否审核通过 |
| created_at | datetime |
| updated_at | datetime |

索引： `(article_id, is_approved)` `article_approved_idx`

---

## 工具 / 其它 (utils app)

### 9. `utils_sensitiveword`
| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | PK |
| word | varchar(100), unique | 敏感词条目 |
| created_at | datetime |

---

## 设计要点 & 说明

> 下列注释进一步解释各核心表的设计意图、约束原因及使用情景，帮助阅读者快速把握数据模型思想。

### `users_user`
- 基于 Django `AbstractUser` 扩展，保持与 Django 生态的兼容性。
- 通过 `avatar` 使用 `ImageField` 方便未来对接云存储或本地媒体目录。
- 业务层以 **用户名或邮箱** 作为登录凭证时，表结构无需改动。

### `users_emailverification`
- 采用 `UUIDField` 作为 `token`，天然唯一难以预测，提升安全性。
- 过期逻辑通过 `expires_at` 与 `verified` 组合判断，避免冗余定时删除。
- 与用户 **级联删除** (`on_delete=CASCADE`)；用户注销时验证记录自动清理。

### `articles_category` / `articles_tag`
- `slug` 字段为 SEO-friendly URL 设计，若未显式填写则由模型 `save()` 自动回写主键。
- 通过排序 `ordering = ['-created_at']` 保证后台列表默认最新在前。

### `articles_article`
- `status` 与 `visibility` 多枚举组合，配合联合索引快速过滤「已发布公开」等常用场景。
- `views_count` 改为 **正整数** 并带索引，既可做排行榜，又避免负值。
- `ManyToManyField(tags)` 使用 Django 默认中间表，若需额外字段（权重等）可拆自定义模型。

### `articles_like` / `articles_favorite`
- 纯映射表，不额外存储冗余计数；可在 `Article` 上通过聚合实时或缓存统计。
- 通过 `unique_together` 保证用户维度操作幂等，避免重复点赞 / 收藏。

### `comments_comment`
- `parent_id` 递归外键实现多层嵌套；如需限制深度可在业务逻辑层控制。
- `is_approved` 支持后台审核流，联合索引 `(article_id, is_approved)` 兼顾按文章分页与审核过滤。

### `utils_sensitiveword`
- 用于内容安全过滤，建议在管理后台提供批量导入 / 导出功能。
- 可考虑在应用启动时缓存至内存或 Redis，降低查询延迟。

---

## 实体关系图

项目根目录已包含 ER 图：
* `docs/Blog_ER.png` — 图片版
* `docs/database_er_diagram.puml` — PlantUML 源码

如需更新请同时修改本文件与 UML 文件。

---

> 2025-05-12 更新
