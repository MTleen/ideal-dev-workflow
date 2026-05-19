# 流程状态规范

## 文件格式

### 文件位置

```
docs/迭代/{需求名称}/流程状态.md
```

### 文件结构

```markdown
---
requirement_name: {需求名称}
current_phase: P1-P15
status: pending|in_progress|completed|blocked|revision
worktree:
  branch: feature/<short-name>
  path: <repo_toplevel>/worktrees/<branch>
  created_at: {YYYY-MM-DD}
created_at: {YYYY-MM-DD}
updated_at: {YYYY-MM-DD}
---

# 流程状态

## 当前阶段

**P{n} - {阶段名称}** {状态图标} {状态文字}

## 阶段状态

### 规划阶段
| 阶段 | 状态 | 更新时间 |
|------|------|----------|
| P1 需求编写 | {状态} | {时间} |
| P2 需求评审 | {状态} | {时间} |
| P3 技术方案 | {状态} | {时间} |
| P4 方案评审 | {状态} | {时间} |

### 准备阶段
| 阶段 | 状态 | 更新时间 |
|------|------|----------|
| P5 计划生成 | {状态} | {时间} |
| P6 计划评审 | {状态} | {时间} |
| P7 测试用例 | {状态} | {时间} |
| P8 用例评审 | {状态} | {时间} |

### 执行阶段
| 阶段 | 状态 | 更新时间 |
|------|------|----------|
| P9 开发执行 | {状态} | {时间} |
| P10 代码评审 | {状态} | {时间} |
| P11 测试执行 | {状态} | {时间} |
| P12 测试评审 | {状态} | {时间} |

### 收尾阶段
| 阶段 | 状态 | 更新时间 |
|------|------|----------|
| P13 维基更新 | {状态} | {时间} |
| P14 维基评审 | {状态} | {时间} |
| P15 成果提交 | {状态} | {时间} |

---

## 状态说明

- ⏳ pending: 待执行
- 🔄 in_progress: 进行中
- ✅ completed: 已完成
- ❌ blocked: 已阻塞
- 🔙 revision: 需要修改

## 触发下一阶段

{说明下一阶段的触发条件}
```

## 状态值定义

### YAML 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `requirement_name` | string | 需求名称 |
| `current_phase` | string | 当前阶段（P1-P15） |
| `status` | enum | 当前状态 |
| `created_at` | date | 创建日期 |
| `updated_at` | date | 最后更新日期 |

### 状态枚举

| 状态值 | 说明 | 图标 |
|--------|------|------|
| `pending` | 待执行 | ⏳ |
| `in_progress` | 进行中 | 🔄 |
| `completed` | 已完成 | ✅ |
| `blocked` | 已阻塞 | ❌ |
| `revision` | 需要修改 | 🔙 |

## 阶段定义

### 15 阶段映射

| 阶段 | 名称 | 执行者 | 输入 | 输出 |
|------|------|--------|------|------|
| P1 | 需求编写 | Claude | 需求想法 | P1-需求文档.md |
| P2 | 需求评审 | 人工 | P1 文档 | 评审意见 |
| P3 | 技术方案 | Claude | P1 文档 | P3-技术方案.md |
| P4 | 方案评审 | 人工 | P3 文档 | 评审意见 |
| P5 | 计划生成 | Claude | P3 文档 | P5-编码计划.md |
| P6 | 计划评审 | 人工 | P5 文档 | 评审意见 |
| P7 | 测试用例 | Claude | P1+P5 文档 | P7-测试用例.md |
| P8 | 用例评审 | 人工 | P7 文档 | 评审意见 |
| P9 | 开发执行 | Claude | P5 文档 | 代码 + MR |
| P10 | 代码评审 | 人工 | MR | Approve |
| P11 | 测试执行 | Claude | P7 文档 | P11-测试报告.md |
| P12 | 测试评审 | 人工 | P11 文档 | 通过/修复 |
| P13 | 维基更新 | Claude | 代码+文档 | Wiki 文档 |
| P14 | 维基评审 | 人工 | Wiki 文档 | 发布许可 |
| P15 | 成果提交 | Claude | 全部通过 | 合并代码、删除 worktree、提交 PR、标记迭代完成 |

> 注：上线部署由 CI/CD 自动化完成，P15 成果提交后自动触发 CI/CD 流水线。

## 触发条件映射

| 当前阶段 | 触发条件 | 下一阶段 |
|----------|----------|----------|
| P1 | 文档生成完成 | P2 |
| P2 | 状态改为 completed | P3 |
| P3 | 文档生成完成 | P4 |
| P4 | 状态改为 completed | P5 |
| P5 | 文档生成完成 | P6 |
| P6 | 状态改为 completed | P7 |
| P7 | 文档生成完成 | P8 |
| P8 | 状态改为 completed | P9 |
| P9 | 代码完成 + MR 创建 | P10 |
| P10 | MR Approve | P11 |
| P11 | 报告生成完成 | P12 |
| P12 | 状态改为 completed | P13 |
| P13 | 文档生成完成 | P14 |
| P14 | 状态改为 completed | P15 |
| P15 | 成果提交完成 | 结束（自动触发 CI/CD） |

## P15 成果提交详细步骤

P15 成果提交阶段执行以下步骤：

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 合并代码 | 将开发分支代码合并到主分支 |
| 2 | 删除 worktree | 清理开发用的 git worktree（路径：`/repo_parent/repo_name-worktrees/<branch>`） |
| 3 | 提交 PR | 创建或更新 Pull Request |
| 4 | 标记迭代完成 | 将迭代目录名从 `[进行中]` 改为 `[完成]` |
| 5 | 更新引用 | 更新流程状态文件中的 `stories_dir` 路径 |

### Worktree 路径格式

```
<repo_toplevel>/worktrees/<branch>
```

其中：
- `repo_toplevel` = `git rev-parse --show-toplevel`（仓库根目录）
- `branch` = 功能分支名（`/` 替换为 `-`，即 `sanitized_branch`）
- `branch` = 功能分支名（`/` 替换为 `-`）

### 标记迭代完成规范

**目录命名约定**：
- 进行中：`docs/迭代/{日期}-[进行中]-{需求名}/`
- 已完成：`docs/迭代/{日期}-[完成]-{需求名}/`

**需要更新的文件**：
- `流程状态.md` 中的 `stories_dir` 路径
- 其他引用该路径的文档（如测试报告）

**Git 提交**：
```bash
git add -A
git commit -m "chore: 标记迭代为完成状态"
```
