# API 文档写作指南

## 概述

API 文档面向**前端开发者**和**第三方集成者**，目标是让开发者能够正确、高效地调用 API。

### 目标读者画像

| 读者类型 | 特点 | 需求 |
|----------|------|------|
| 前端开发者 | 集成 API 到前端应用 | 参数说明、响应格式、示例代码 |
| 第三方开发者 | 外部系统集成 | 认证方式、完整 API 参考 |
| 测试工程师 | 验证 API 正确性 | 请求/响应示例、边界情况 |

---

## 文档集结构

```
接口文档/
├── README.md          # API 概览
├── 认证授权.md        # 认证方式
├── endpoints/         # 按模块分类的接口
│   ├── 用户接口.md
│   ├── 订单接口.md
│   └── ...
└── 错误码.md          # 错误码表
```

---

## 各文档写作指南

### README.md（API 概览）

**目的**：作为 API 文档入口，提供全局视图和快速导航。

**必备内容**：
1. API 简介
2. 基础 URL 和版本
3. 认证概述
4. 接口分类导航
5. 快速示例

**示例结构**：
```markdown
# {项目名称} API 文档

## 概述

{项目} API 提供 RESTful 接口，支持 {主要功能}。

## 基础信息

| 项目 | 值 |
|------|-----|
| 基础 URL | `https://api.example.com/v1` |
| 协议 | HTTPS |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |

## 认证

所有 API 请求需要在 Header 中携带 Token：

```http
Authorization: Bearer <your-token>
```

详细说明请参考 [认证授权](认证授权.md)。

## 接口分类

| 分类 | 说明 | 文档 |
|------|------|------|
| 用户 | 用户注册、登录、信息管理 | [用户接口](endpoints/用户接口.md) |
| 订单 | 订单创建、查询、状态管理 | [订单接口](endpoints/订单接口.md) |

## 快速示例

### 获取用户信息

```bash
curl -X GET "https://api.example.com/v1/users/me" \
  -H "Authorization: Bearer <your-token>"
```

响应：

```json
{
  "code": 0,
  "data": {
    "id": "123",
    "name": "张三",
    "email": "zhangsan@example.com"
  }
}
```

## 版本说明

| 版本 | 状态 | 说明 |
|------|------|------|
| v1 | 当前 | 稳定版本 |
| v2-beta | 预览 | 即将发布 |

## 更新日志

详见 [GitHub Releases](...)。
```

---

### 认证授权.md

**目的**：详细说明 API 的认证和授权机制。

**必备内容**：
1. 支持的认证方式
2. 获取 Token 的方法
3. Token 使用方式
4. Token 刷新和过期

**示例结构**：
```markdown
# 认证授权

## 概述

{项目} API 使用 OAuth 2.0 进行认证。

## 认证方式

| 方式 | 适用场景 | 说明 |
|------|----------|------|
| Bearer Token | 服务端调用 | 长期有效的访问令牌 |
| OAuth 2.0 | 第三方应用 | 用户授权后获取 Token |

## 获取 Token

### 方式一：API Key（服务端）

```bash
curl -X POST "https://api.example.com/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "your-client-id",
    "client_secret": "your-client-secret"
  }'
```

响应：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 方式二：OAuth 2.0 授权码流程

```mermaid
sequenceDiagram
    participant 用户
    participant 应用
    participant 授权服务器
    participant API

    用户->>应用: 点击登录
    应用->>授权服务器: 重定向到授权页面
    用户->>授权服务器: 同意授权
    授权服务器->>应用: 返回授权码
    应用->>授权服务器: 用授权码换取 Token
    授权服务器->>应用: 返回 Token
    应用->>API: 使用 Token 调用 API
\```

## 使用 Token

在请求 Header 中添加：

```http
Authorization: Bearer <your-access-token>
```

## Token 刷新

Token 过期前可使用 Refresh Token 获取新的 Access Token：

```bash
curl -X POST "https://api.example.com/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your-refresh-token"
  }'
```

## 权限范围

| Scope | 说明 |
|-------|------|
| `user:read` | 读取用户信息 |
| `user:write` | 修改用户信息 |
| `order:read` | 读取订单 |
| `order:write` | 创建/修改订单 |
```

---

### endpoints/{模块}接口.md

**目的**：详细说明某个模块的所有 API 接口。

**每个接口必备内容**：
1. 接口名称和描述
2. 请求方法和路径
3. 请求参数（Query/Path/Body）
4. 请求头
5. 响应格式和示例
6. 错误码

**示例结构**：
```markdown
# 用户接口

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /users/me | 获取当前用户信息 |
| GET | /users/:id | 获取指定用户信息 |
| PUT | /users/:id | 更新用户信息 |
| DELETE | /users/:id | 删除用户 |

---

## 获取当前用户信息

获取当前认证用户的基本信息。

### 请求

```http
GET /users/me
```

### 请求头

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| Authorization | string | 是 | Bearer Token |

### 响应

#### 成功响应 (200)

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "usr_123456",
    "name": "张三",
    "email": "zhangsan@example.com",
    "avatar": "https://cdn.example.com/avatars/123.jpg",
    "created_at": "2026-01-15T08:30:00Z"
  }
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 用户唯一标识 |
| name | string | 用户名 |
| email | string | 邮箱地址 |
| avatar | string | 头像 URL |
| created_at | string | 创建时间（ISO 8601） |

#### 错误响应

| 状态码 | code | 说明 |
|--------|------|------|
| 401 | 40101 | Token 无效或已过期 |
| 403 | 40301 | 无权限访问 |

### 示例

```bash
curl -X GET "https://api.example.com/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

---

## 更新用户信息

更新当前用户的信息。

### 请求

```http
PUT /users/me
```

### 请求体

```json
{
  "name": "李四",
  "avatar": "https://cdn.example.com/avatars/new.jpg"
}
```

### 请求体字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 用户名（2-20 字符） |
| avatar | string | 否 | 头像 URL |

### 响应

#### 成功响应 (200)

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "usr_123456",
    "name": "李四",
    "email": "zhangsan@example.com",
    "avatar": "https://cdn.example.com/avatars/new.jpg",
    "updated_at": "2026-02-21T10:30:00Z"
  }
}
```
```

---

### 错误码.md

**目的**：汇总所有错误码，方便开发者快速定位问题。

**示例结构**：
```markdown
# 错误码

## 错误响应格式

所有错误响应遵循统一格式：

```json
{
  "code": 40001,
  "message": "参数错误",
  "details": [
    {
      "field": "email",
      "message": "邮箱格式不正确"
    }
  ]
}
```

## 错误码分类

| 范围 | 分类 |
|------|------|
| 400xx | 请求参数错误 |
| 401xx | 认证相关错误 |
| 403xx | 权限相关错误 |
| 404xx | 资源不存在 |
| 429xx | 请求频率限制 |
| 500xx | 服务器内部错误 |

## 详细错误码

### 400xx 请求参数错误

| code | message | 说明 |
|------|---------|------|
| 40001 | 参数错误 | 请求参数格式不正确 |
| 40002 | 缺少必填参数 | 缺少必要的请求参数 |
| 40003 | 参数值超出范围 | 参数值不在允许范围内 |

### 401xx 认证错误

| code | message | 说明 |
|------|---------|------|
| 40101 | 未授权 | 缺少认证信息 |
| 40102 | Token 无效 | Token 格式错误或已失效 |
| 40103 | Token 已过期 | Token 已超过有效期 |

### 403xx 权限错误

| code | message | 说明 |
|------|---------|------|
| 40301 | 无权限 | 没有访问该资源的权限 |
| 40302 | 账户已禁用 | 账户被管理员禁用 |

### 404xx 资源不存在

| code | message | 说明 |
|------|---------|------|
| 40401 | 资源不存在 | 请求的资源不存在 |
| 40402 | 用户不存在 | 指定的用户 ID 不存在 |

### 429xx 频率限制

| code | message | 说明 |
|------|---------|------|
| 42901 | 请求过于频繁 | 超出 API 调用频率限制 |

### 500xx 服务器错误

| code | message | 说明 |
|------|---------|------|
| 50001 | 服务器内部错误 | 未知的服务器错误 |
| 50002 | 服务暂时不可用 | 服务正在维护中 |

## 常见错误排查

### Token 无效 (40102)

**可能原因**：
1. Token 格式错误
2. Token 已被撤销
3. Token 签名验证失败

**解决方案**：
1. 检查 Token 格式是否正确
2. 重新获取 Token

### 请求过于频繁 (42901)

**可能原因**：
1. 短时间内发送大量请求
2. 并发请求超过限制

**解决方案**：
1. 降低请求频率
2. 实现请求队列
3. 联系管理员提升配额
```

---

## 质量检查清单

### README（概览）
- [ ] 基础 URL 和版本明确
- [ ] 认证概述清晰
- [ ] 接口分类导航完整
- [ ] 有快速示例

### 认证授权
- [ ] 认证方式说明完整
- [ ] Token 获取/使用/刷新流程清晰
- [ ] 权限范围列出

### 接口文档
- [ ] 每个接口有完整的请求/响应说明
- [ ] 参数表格包含类型、必填、说明
- [ ] 有可运行的示例代码
- [ ] 错误响应列出

### 错误码
- [ ] 错误码分类清晰
- [ ] 每个错误码有说明
- [ ] 常见错误有排查建议
