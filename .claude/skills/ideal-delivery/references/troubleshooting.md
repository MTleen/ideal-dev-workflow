# 交付故障恢复指南

## 检查清单

| 检查项 | 命令 | 判断 |
|--------|------|------|
| 代码是否已提交 | `git status` | working tree clean = 已提交 |
| PR 是否已创建 | `gh pr list --head {branch}` | 有输出 = 已创建 |
| PR 是否已合并 | `gh pr view {PR号}` | state: MERGED = 已合并 |
| 分支是否已删除 | `git branch -a \| grep {branch}` | 无输出 = 已删除 |
| 目录是否已重命名 | `ls docs/迭代/` | 无 [进行中] = 已归档 |

---

## PR 被拒绝或需要修改

```bash
# 1. 切换回 feature 分支
git checkout {feature-branch}

# 2. 修改代码后提交
git add -A
git commit -m "fix: 根据审查意见修改"
git push origin {feature-branch}

# 3. PR 会自动更新，等待重新审查
```

---

## 合并冲突

```bash
# 1. 确保在 feature 分支
git checkout {feature-branch}

# 2. 拉取最新的主分支并变基
git fetch origin {主分支名}
git rebase origin/{主分支名}

# 3. 解决冲突后继续变基
git rebase --continue

# 4. 强制推送
git push origin {feature-branch} --force-with-lease
```

---

## 中断恢复策略

根据检查结果确定当前阶段：

| 状态 | 从哪一步继续 |
|------|-------------|
| 代码未提交 | Step 4 |
| PR 未创建 | Step 5 |
| PR 未合并 | 等待用户合并后 Step 6 |
| 分支未删除 | Step 6 |
| 目录未重命名 | Step 7 |
