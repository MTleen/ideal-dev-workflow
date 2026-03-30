---
name: ideal-delivery
description: Use when P14 wiki review is completed, all development and testing work is finished, and the iteration needs to be finalized. Triggers when user requests to mark iteration complete, submit deliverables, or close the development cycle.
---

# ideal-delivery（P15 成果提交）

> **agents**: Utility skill — 不通过 Task 工具调度子代理，直接执行 git/PR 操作。

## Overview

完成迭代交付的最后一步：创建 PR、清理 worktree、本地归档、成果摘要。

**核心原则**：
- 迭代目录不被 git 跟踪，归档是纯本地操作
- 先提交代码，再创建 PR，PR 合并后本地归档

**违反以下规则 = 违反 skill 精神**：
- 直接合并到主分支（必须通过 PR，除非无远程仓库）
- 代码未提交就标记完成
- 跳过状态文件更新
- 忘记重命名迭代目录
- worktree 未清理

---

## When to Use

| 条件 | 说明 |
|------|------|
| P14 完成 | 维基评审通过 |
| 用户请求 | "标记完成"、"提交成果"、"归档" |

**不适用**：开发未完成 → 返回 P9，测试未通过 → 返回 P11

---

## Step-by-Step Process

### Step 0: 检测远程仓库

```bash
git remote -v
```

| 情况 | 流程 |
|------|------|
| 有远程仓库（GitHub/GitLab） | 完整 PR 流程（Step 1-8） |
| 无远程仓库 | 简化流程（本地 commit → 归档） |

### Step 1: 读取项目配置

必须先读取 `project-config.md` 获取主分支名和功能分支前缀。

### Step 2: 验证前置条件

找到进行中的迭代目录：
```bash
ls docs/迭代/ | grep "\[进行中\]"
```

如有多个进行中迭代，询问用户要完成哪一个。

### Step 3: 检查开发环境

**必须在主仓库操作，不能在 worktree 中创建 PR**：

```bash
git worktree list
pwd | grep worktree  # 如在 worktree 中，切换到主仓库
```

### Step 4: 提交代码变更

```bash
git status  # 检查未提交变更
git add -A && git commit -m "feat: {需求名称} 开发完成"
git push origin {feature-branch}
```

### Step 5: 创建 Pull Request

**禁止直接合并到主分支，必须通过 PR**：

```bash
gh pr create --title "feat: {需求名称}" --body "变更概述、变更内容、检查清单"
```

**暂停等待用户合并 PR**，合并后告诉我"已合并"。

### Step 6: 合并后清理

```bash
git checkout {主分支名} && git pull
git branch -d {feature-branch} && git push origin --delete {feature-branch}
git worktree remove {worktree路径}  # 如使用了 worktree
```

### Step 7: 本地归档

**7.1 更新流程状态文件**：

```yaml
---
current_phase: P15
status: completed
---
```

**7.2 重命名迭代目录**：

```
[进行中] → [已完成]
```

```bash
mv "docs/迭代/YYYY-MM-DD-[进行中]-{需求名称}" \
   "docs/迭代/YYYY-MM-DD-[已完成]-{需求名称}"
```

### Step 8: 输出成果摘要

```markdown
## 成果提交完成

### 迭代信息
- 需求名称：{名称}
- 开发周期：{开始日期} ~ {结束日期}
- Pull Request：{PR-URL}（已合并）

### 清理工作
- [x] Feature 分支已删除
- [x] Worktree 已删除（如适用）
- [x] 迭代目录已归档（本地）

✅ 迭代已完成，可进行上线部署。
```

---

## Quality Checklist

- [ ] 远程仓库已检测
- [ ] 项目配置已读取
- [ ] 已切换到主仓库
- [ ] 所有代码变更已提交
- [ ] Pull Request 已创建并合并
- [ ] Feature 分支已删除
- [ ] Worktree 已删除（如适用）
- [ ] 流程状态文件已更新
- [ ] 迭代目录已重命名

---

## Red Flags - 立即停止

- "直接合并到 main 吧，更快"
- "worktree 不用删"
- "代码应该都提交了"（未验证 git status）
- "状态更新不重要"
- "目录名不用改"

---

## Troubleshooting

详见 `references/troubleshooting.md`。
