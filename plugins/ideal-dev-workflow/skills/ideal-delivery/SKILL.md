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

## Sub-Iteration Detection（Step 0 前必须执行）

**在执行任何步骤前，必须判断当前迭代是否为子迭代。**

### 检测方法

```
1. 读取当前迭代的 流程状态.md
2. 检查 frontmatter 中是否存在 parent 字段
3. 如存在 → is_sub_iteration = true
4. 如不存在 → is_sub_iteration = false
```

### 行为差异总览

| 步骤 | 父迭代 | 子迭代 |
|------|--------|--------|
| Step 3: 检查开发环境 | 切换到主仓库 | **保持在 worktree 中** |
| Step 4-5: 提交/创建 PR | 执行 | **跳过**（commit 到共享分支，不做单独 PR） |
| Step 6: 合并后清理 | 执行 | **禁止执行**（worktree/branch 属于父迭代） |
| Step 7: 本地归档 | 执行 | 执行（路径基于父迭代目录） |
| Step 7.3: 更新父迭代状态 | 不需要 | **必须执行** |
| Step 8: 输出摘要 | 执行 | 执行（标注"子迭代"） |

> **⚠️ 核心规则**：子迭代 **绝对不能** 删除 worktree 或 feature branch。多个子迭代共享同一个父 worktree，只有父迭代 P15 完成后才能清理。

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

**父迭代**：必须在主仓库操作，不能在 worktree 中创建 PR：

```bash
git worktree list
pwd | grep worktree  # 如在 worktree 中，切换到主仓库
```

**子迭代**：保持在 worktree 中，仅提交代码到共享分支：

```bash
git status  # 检查未提交变更
git add -A && git commit -m "feat: 子迭代{X}-{名称} 开发完成"
# 不 push，不创建 PR
```

→ **子迭代提交后直接跳到 Step 7**。

### Step 4: 提交代码变更（仅父迭代）

```bash
git status  # 检查未提交变更
git add -A && git commit -m "feat: {需求名称} 开发完成"
git push origin {feature-branch}
```

### Step 5: 创建 Pull Request（仅父迭代）

**禁止直接合并到主分支，必须通过 PR**：

```bash
gh pr create --title "feat: {需求名称}" --body "变更概述、变更内容、检查清单"
```

**暂停等待用户合并 PR**，合并后告诉我"已合并"。

### Step 6: 合并后清理（仅父迭代）

> ⚠️ **子迭代绝对不能执行此步骤**。检查 `is_sub_iteration`，如为 true 则跳过。

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
# 父迭代
mv "docs/迭代/YYYY-MM-DD-[进行中]-{需求名称}" \
   "docs/迭代/YYYY-MM-DD-[已完成]-{需求名称}"

# 子迭代（路径在父迭代目录下）
mv "docs/迭代/YYYY-MM-DD-[状态]-{父需求名称}/YYYY-MM-DD-[进行中]-子迭代{X}-{名称}" \
   "docs/迭代/YYYY-MM-DD-[状态]-{父需求名称}/YYYY-MM-DD-[已完成]-子迭代{X}-{名称}"
```

**7.3 更新父迭代状态（仅子迭代，必须执行）**：

子迭代完成后，**必须**更新父迭代的 `流程状态.md`：

```
1. 从当前 流程状态.md 的 parent.path 获取父迭代目录路径
2. 读取父迭代的 流程状态.md
3. 在 sub_iterations 列表中找到当前子迭代（匹配 id）
4. 更新该子迭代的 status 为 "已完成"，添加 completed_at
5. 更新父迭代的 updated_at 为当前时间
6. 写回父迭代的 流程状态.md
```

父迭代 frontmatter 修改示例：

```yaml
# 修改前
sub_iterations:
  - id: X
    name: {名称}
    status: 待启动

# 修改后
sub_iterations:
  - id: X
    name: {名称}
    status: 已完成
    current_phase: P15
    completed_at: {YYYY-MM-DD}
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

### 父迭代

- [ ] 远程仓库已检测
- [ ] 项目配置已读取
- [ ] 已切换到主仓库
- [ ] 所有代码变更已提交
- [ ] Pull Request 已创建并合并
- [ ] Feature 分支已删除
- [ ] Worktree 已删除（如适用）
- [ ] 流程状态文件已更新
- [ ] 迭代目录已重命名

### 子迭代

- [ ] 远程仓库已检测
- [ ] 代码已提交到共享 worktree 分支
- [ ] **未删除** worktree 或 feature branch
- [ ] 流程状态文件已更新（当前迭代）
- [ ] 迭代目录已重命名（在父迭代目录下）
- [ ] **父迭代的 sub_iterations 状态已同步更新**
- [ ] 父迭代的 updated_at 已更新

---

## Red Flags - 立即停止

- "直接合并到 main 吧，更快"
- "worktree 不用删"（父迭代）
- "代码应该都提交了"（未验证 git status）
- "状态更新不重要"
- "目录名不用改"
- **"子迭代完成后删 worktree"**（子迭代绝对不能删共享 worktree）
- **"父迭代的 sub_iterations 不用更新"**（必须同步）

---

## Troubleshooting

详见 `references/troubleshooting.md`。
