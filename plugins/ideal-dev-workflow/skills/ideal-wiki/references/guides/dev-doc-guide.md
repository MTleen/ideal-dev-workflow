# 开发文档写作指南

## 概述

开发文档面向**开发者**和**维护者**，目标是帮助开发者快速参与项目开发、理解系统架构、进行部署和维护。

### 目标读者画像

| 读者类型 | 特点 | 需求 |
|----------|------|------|
| 新开发者 | 刚加入项目 | 环境搭建、代码理解 |
| 维护者 | 长期维护项目 | 架构理解、故障排查 |
| 贡献者 | 外部贡献代码 | 贡献流程、代码规范 |

---

## 文档集结构

```
开发文档/
├── README.md          # 文档索引/首页
├── 架构设计.md        # 系统架构
├── 开发环境.md        # 环境配置
├── 代码结构.md        # 目录说明
├── 部署指南.md        # 部署步骤
└── 贡献指南.md        # 参与开发
```

---

## 各文档写作指南

### README.md（文档索引）

**目的**：作为开发文档入口，提供快速导航。

**示例结构**：
```markdown
# {项目名称} 开发文档

欢迎来到 {项目} 开发文档。

## 文档导航

| 文档 | 说明 |
|------|------|
| [架构设计](架构设计.md) | 系统架构和模块设计 |
| [开发环境](开发环境.md) | 环境配置和依赖安装 |
| [代码结构](代码结构.md) | 目录结构和模块说明 |
| [部署指南](部署指南.md) | 构建和部署步骤 |
| [贡献指南](贡献指南.md) | 如何参与开发 |

## 快速开始

```bash
# 克隆项目
git clone {repo_url}

# 安装依赖
{install_command}

# 启动开发服务
{dev_command}
```

详细步骤请参考 [开发环境](开发环境.md)。
```

---

### 架构设计.md

**目的**：说明系统的整体架构、核心模块和设计决策。

**必备内容**：
1. 系统架构图（使用 Mermaid）
2. 核心模块说明
3. 数据流/请求流程
4. 关键设计决策（如有）

**示例结构**：
```markdown
# 架构设计

## 系统架构

```mermaid
flowchart TB
    subgraph 用户层
        A[Web 客户端]
        B[移动端]
    end

    subgraph 应用层
        C[API 网关]
        D[业务服务]
    end

    subgraph 数据层
        E[(数据库)]
        F[(缓存)]
    end

    A --> C
    B --> C
    C --> D
    D --> E
    D --> F
\```

## 核心模块

| 模块 | 职责 | 技术栈 |
|------|------|--------|
| API 网关 | 请求路由、认证 | {tech} |
| 业务服务 | 核心业务逻辑 | {tech} |

## 请求流程

```mermaid
sequenceDiagram
    participant 用户
    participant 网关
    participant 服务
    participant 数据库

    用户->>网关: 发起请求
    网关->>网关: 验证 Token
    网关->>服务: 转发请求
    服务->>数据库: 查询数据
    数据库-->>服务: 返回结果
    服务-->>网关: 响应
    网关-->>用户: 返回数据
\```

## 设计决策

### {决策主题}

**背景**：{为什么需要做这个决策}

**选项**：
- 选项 A：{描述}
- 选项 B：{描述}

**决策**：选择 {选项}

**理由**：{为什么选择这个选项}
```

---

### 开发环境.md

**目的**：帮助新开发者快速搭建本地开发环境。

**必备内容**：
1. 系统要求
2. 必备工具和版本
3. 安装步骤
4. 验证方法
5. 常见问题

**示例结构**：
```markdown
# 开发环境

## 系统要求

| 项目 | 版本要求 |
|------|----------|
| 操作系统 | macOS 12+ / Ubuntu 20.04+ / Windows 10+ |
| Node.js | >= 18.0.0 |
| npm | >= 9.0.0 |

## 安装步骤

### 1. 克隆项目

```bash
git clone {repo_url}
cd {project_name}
```

### 2. 安装依赖

```bash
npm install
```

### 3. 配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入必要配置：

```bash
# 必填
DATABASE_URL=postgresql://...
API_KEY=your-api-key

# 可选
DEBUG=true
```

### 4. 初始化数据库

```bash
npm run db:init
```

### 5. 启动开发服务

```bash
npm run dev
```

**预期输出**：
```
Server running at http://localhost:3000
```

## 验证安装

访问 http://localhost:3000/health，应返回：

```json
{"status": "ok"}
```

## 常见问题

### 依赖安装失败

**原因**：网络问题或权限问题

**解决**：
```bash
# 使用国内镜像
npm config set registry https://registry.npmmirror.com

# 或使用 sudo（不推荐）
sudo npm install
```
```

---

### 代码结构.md

**目的**：说明项目的目录结构和各模块职责。

**示例结构**：
```markdown
# 代码结构

## 目录概览

```
{project_name}/
├── src/                    # 源代码
│   ├── modules/            # 业务模块
│   │   ├── user/           # 用户模块
│   │   └── order/          # 订单模块
│   ├── shared/             # 共享代码
│   │   ├── utils/          # 工具函数
│   │   └── types/          # 类型定义
│   └── index.ts            # 入口文件
├── tests/                  # 测试代码
├── docs/                   # 文档
├── scripts/                # 脚本文件
└── config/                 # 配置文件
```

## 核心目录说明

### src/modules/

业务模块目录，每个模块包含：

```
module/
├── controller.ts    # 控制器
├── service.ts       # 业务逻辑
├── repository.ts    # 数据访问
├── types.ts         # 类型定义
└── __tests__/       # 单元测试
```

### src/shared/

共享代码，可被多个模块使用：

| 目录 | 内容 |
|------|------|
| utils/ | 通用工具函数 |
| types/ | 共享类型定义 |
| middleware/ | 中间件 |

## 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件 | kebab-case | `user-service.ts` |
| 类 | PascalCase | `UserService` |
| 函数 | camelCase | `getUserById` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
```

---

### 部署指南.md

**目的**：说明如何构建、部署和运维项目。

**必备内容**：
1. 构建命令
2. 环境配置
3. 部署步骤
4. 健康检查
5. 回滚方案

**示例结构**：
```markdown
# 部署指南

## 构建产物

```bash
# 构建
npm run build

# 产物位置
ls dist/
```

## 环境配置

### 必需环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| NODE_ENV | 运行环境 | production |
| DATABASE_URL | 数据库连接 | postgresql://... |
| API_KEY | API 密钥 | sk-xxx |

### 可选环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| LOG_LEVEL | 日志级别 | info |
| PORT | 服务端口 | 3000 |

## 部署步骤

### Docker 部署

```bash
# 构建镜像
docker build -t {project}:latest .

# 运行容器
docker run -d \
  --name {project} \
  -p 3000:3000 \
  -e NODE_ENV=production \
  -e DATABASE_URL=... \
  {project}:latest
```

### Kubernetes 部署

```bash
# 应用配置
kubectl apply -f k8s/

# 检查状态
kubectl get pods -l app={project}
```

## 健康检查

```bash
# 健康检查端点
curl http://localhost:3000/health

# 预期响应
{"status": "ok", "version": "1.0.0"}
```

## 回滚方案

```bash
# Kubernetes 回滚
kubectl rollout undo deployment/{project}

# Docker 回滚
docker stop {project}
docker run -d --name {project} {project}:{previous_version}
```
```

---

### 贡献指南.md

**目的**：说明如何参与项目开发，包括代码规范、提交流程、PR 要求。

**示例结构**：
```markdown
# 贡献指南

感谢你考虑为 {项目} 做贡献！

## 开发流程

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 代码规范

### 提交消息

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关

### 代码风格

```bash
# 检查
npm run lint

# 自动修复
npm run lint:fix
```

## PR 要求

- [ ] 代码通过 Lint 检查
- [ ] 新功能有对应测试
- [ ] 文档已更新（如需要）
- [ ] 提交消息符合规范

## 问题反馈

- 使用 GitHub Issues
- 提供复现步骤
- 说明环境和版本
```

---

## 质量检查清单

### 架构设计
- [ ] 包含系统架构图（Mermaid）
- [ ] 核心模块职责明确
- [ ] 关键流程有说明

### 开发环境
- [ ] 系统要求明确
- [ ] 安装步骤可复现
- [ ] 包含验证方法

### 代码结构
- [ ] 目录结构清晰
- [ ] 命名规范明确
- [ ] 模块职责说明

### 部署指南
- [ ] 构建/部署步骤完整
- [ ] 环境变量说明
- [ ] 包含回滚方案

### 贡献指南
- [ ] 开发流程清晰
- [ ] 代码规范明确
- [ ] PR 要求列出
