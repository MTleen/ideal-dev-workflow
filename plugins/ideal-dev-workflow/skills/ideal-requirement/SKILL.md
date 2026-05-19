---
name: ideal-requirement
description: "Use when: (1) starting a new feature, bug fix, or refactoring task, (2) user mentions '需求', '需求文档', 'PRD', 'requirement', '需求编写', '需求收集', 'bug修复', '重构需求'."
agents: [pm, analyst]
---

# Ideal Requirement

通过交互式对话引导用户完善需求，生成符合正式学术风格的标准化需求文档。对于大型需求，自动识别并拆分为多个子迭代项。

## Agents

| Agent | 角色 | 用途 |
|-------|------|------|
| pm | 产品经理 | 需求梳理、苏格拉底式对话、文档编写 |
| analyst | 业务分析师 | 竞品分析、市场调研（可选） |

```markdown
Task(
    subagent_type: "pm",
    prompt: "执行需求收集，苏格拉底式对话引导用户",
    model: "opus"
)
```

## Workflow

```
进度：
- [ ] Step 0:   项目背景          ⚠️ REQUIRED
- [ ] Step 0.5: 迭代类型          ⚠️ REQUIRED
- [ ] Step 0.6: Worktree 检查      ⚠️ REQUIRED
- [ ] Step 1:   类型识别
- [ ] Step 2:   模板处理
- [ ] Step 3:   需求收集（苏格拉底式对话）
- [ ] Step 4:   确认摘要           ⚠️ REQUIRED
- [ ] Step 5:   子迭代拆分判断
- [ ] Step 6:   生成文档
- [ ] Step 7:   完成
```

---

## 0.6 Worktree 检查（必须）

**整个迭代必须在 Git Worktree 中执行**，P1 开始前就要完成 worktree 创建。

### 检查流程

```
1. 判断当前迭代是否为子迭代
   ├─ 检查父迭代的 流程状态.md 中 is_parent: true
   ├─ 检查当前需求名称是否匹配 sub_iterations 列表中的某一项
   └─ 如是子迭代 → 进入"子迭代 Worktree 继承"流程（见下方）

2. 检查当前是否在 worktree 中
   pwd | grep worktrees  # 或 git worktree list

3. 如不在 worktree 中：
   ├─ 读取 project-config.md 获取分支命名规范
   ├─ 生成分支名：feature/{short-name}
   ├─ 使用 git worktree add 创建 worktree
   └─ ★ 创建完成后立即切换到新 worktree 目录
```

### 子迭代 Worktree 继承

**子迭代不创建独立 worktree，直接使用父迭代的 worktree。**

```
1. 读取父迭代的 流程状态.md
2. 获取父 worktree 信息：branch, path
3. 检查父 worktree 是否存在：ls {path}
4. 切换到父 worktree：cd {path}
5. 验证：pwd, git branch --show-current
```

> **⚠️ 禁止为子迭代创建独立 worktree**。所有子迭代共享父迭代的 worktree 和 branch。

### 自动切换（关键）

**创建 worktree 后（或继承父 worktree 后）必须立即切换**，否则后续所有操作都在原分支执行：

```
切换成功后，立即执行：
  cd /path/to/repo/worktrees/feature-{short-name}

验证切换成功：
  pwd  # 确认路径包含 worktrees
  git branch --show-current  # 确认是 feature/xxx 分支
```

### 分支命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 功能分支 | `feature/<short-name>` | `feature/mat5-multi-layer-memory` |
| 修复分支 | `fix/<short-name>` | `fix/chat-api-timeout` |

> **short-name 规则**：需求 ID（如 MAT-5）+ 简短描述，不超过 50 字符

---

## The Iron Law

```
NO REQUIREMENT QUESTIONS WITHOUT READING PROJECT CONTEXT FIRST
```

**必须先读取 CLAUDE.md 或 README.md**，了解项目背景后再提问。

---

## 核心原则：需求文档聚焦"做什么"，不包含"怎么做"

**需求文档只回答：**
- 背景：现状是什么？为什么需要改变？
- 目标：重构后要达到什么效果？
- 范围：涉及哪些模块？不涉及哪些？
- 验收标准：怎么算完成？

**需求文档不包含（属于技术方案阶段）：**
- 技术选型、架构设计
- 实施步骤、依赖关系
- 接口变更、数据迁移
- 测试策略、详细设计
- 代码实现细节

---

## 0. 项目背景（必须）

读取优先级：CLAUDE.md → README.md → docs/项目状态.md

提取：项目目标、系统架构、当前阶段、已有模块、技术栈、团队规模。

如果无项目文件，在第一个问题中询问"请简要描述项目背景"。

---

## 0.5 迭代类型（必须）

**询问**：这是个人迭代还是项目迭代？

| 类型 | 说明 | 目录位置 |
|------|------|----------|
| 个人迭代 | 个人开发，不需要团队共享进度 | `docs/迭代/` |
| 项目迭代 | 团队协作，需要共享进度和文档 | `docs/项目迭代/` |

两种迭代目录都不被 Git 跟踪。

---

## 1. 类型识别

用户已指定类型 → 直接使用；未指定 → 通过对话识别：

| 类型 | 触发关键词 | 模板 |
|------|-----------|------|
| 软件功能 | 新功能、开发、实现 | `software-feature.md` |
| Bug修复 | Bug、缺陷、错误、修复 | `bug-fix.md` |
| 重构优化 | 重构、优化、改进 | `refactoring.md` |

---

## 2. 模板处理

1. 读取 `references/templates/{type}.md`
2. 扫描所有 `{placeholder}` 占位符
3. 按优先级排序提问（核心 → 主体 → 细节）

**必填字段**：

| 模板 | 必填字段 |
|------|----------|
| software-feature | title, problem_statement, goal, features, acceptance_functional |
| bug-fix | title, bug_title, preconditions, step_1, expected_behavior, actual_behavior |
| refactoring | title, current_state, problems, goals, acceptance_functional |

---

## 3. 需求收集（苏格拉底式对话）

调用 pm 子代理执行。

### 用户命令（随时可用）

| 命令 | 作用 |
|------|------|
| **跳过** | 跳过当前可选问题 |
| **直接生成** | 跳过剩余问题，进入确认 |
| **回到 XX** | 修改之前某个字段的回答 |
| **取消** | 结束流程（可选保存草稿） |

### 提问策略

- 一次只问一个问题
- 提供 2-4 个选项辅助
- 追问细节
- 记录答案
- 聚焦用户价值（每个功能都要回答"为谁解决什么问题"）

---

## 4. 确认摘要

展示：类型、标题、背景摘要、核心功能、验收标准

用户响应：
- "是"/"确认" → 进入拆分判断
- "修改 XX" → 返回收集阶段
- "继续" → 补充更多信息

---

## 5. 子迭代拆分判断

**建议拆分**（满足任一）：
- 涉及多个独立模块
- 工作量超过 2 人日
- 子任务之间有明确依赖关系
- 涉及多个技术栈层次

**不建议拆分**：单个组件（< 0.5 人日）、Bug 修复、简单样式调整

---

## 6. 生成文档

### 目录命名

#### 父迭代（单一需求）

```
docs/迭代/YYYY-MM-DD-[状态]-{需求名称}/
├── P1-需求文档.md
└── 流程状态.md
```

#### 拆分需求（父迭代 + 子迭代）

> **重要**：每个子迭代都是完整的 CCWorkflow 迭代（独立执行 P1-P15），因此命名规范与父迭代完全一致。

```
docs/迭代/YYYY-MM-DD-[状态]-{父需求名称}/
├── P1-需求文档.md              # 父迭代总览文档
├── 流程状态.md                 # 父迭代流程状态
├── YYYY-MM-DD-[状态]-子迭代A-{子迭代名称}/
│   ├── P1-需求文档.md
│   └── 流程状态.md
├── YYYY-MM-DD-[状态]-子迭代B-{子迭代名称}/
│   ├── P1-需求文档.md
│   └── 流程状态.md
└── YYYY-MM-DD-[状态]-子迭代C-{子迭代名称}/
    ├── P1-需求文档.md
    └── 流程状态.md
```

**命名规则**：
- 父迭代：`YYYY-MM-DD-[状态]-{需求名称}`
- 子迭代：`YYYY-MM-DD-[状态]-子迭代{A|B|C|...}-{简短名称}`
- 状态：`[待启动]` / `[进行中]` / `[已完成]` / `[已交付]`
- 每个子迭代独立执行完整 15 阶段流程（P1-P15）
- 子迭代文件夹内**不需要**包含父迭代的 `流程状态.md`

### 输出文件

| 文件 | 说明 |
|------|------|
| `P1-需求文档.md` | 填充模板 + 学术风格 |
| `流程状态.md` | current_phase: P1, status: in_progress, worktree 字段 |

**流程状态.md 必须包含 worktree 信息**：

父迭代：
```yaml
---
requirement_name: {需求名称}
current_phase: P1
status: in_progress
yolo_mode: false
is_parent: true
sub_iterations:
  - id: A
    name: {子迭代名称}
    status: 待启动
    current_phase: P1
worktree:
  branch: feature/{short-name}
  path: {repoRoot}/worktrees/feature-{short-name}
  created_at: {YYYY-MM-DD}
created_at: {创建时间}
updated_at: {更新时间}
---
```

子迭代（**必须**包含 parent 字段）：
```yaml
---
requirement_name: 子迭代{X}-{名称}
current_phase: P1
status: in_progress
yolo_mode: false
parent:
  name: {父需求名称}
  path: docs/迭代/{YYYY-MM-DD-[状态]-{父需求名称}}
worktree:
  branch: feature/{short-name}
  path: {repoRoot}/worktrees/feature-{short-name}
  created_at: {YYYY-MM-DD}
created_at: {创建时间}
updated_at: {更新时间}
---
```

> **⚠️ `parent` 字段是区分父子迭代的唯一标识**。没有 `parent` 字段 = 父迭代/独立迭代；有 `parent` 字段 = 子迭代。所有依赖父子迭代判断的 skill 都通过此字段识别。

### 生成流程

1. 读取 `references/templates/{type}.md`
2. 填充占位符，计算风险等级
3. 应用正式学术风格（见 `references/writing-style.md`）
4. 写入文件

---

## 7. 完成

输出文件位置和下一步提示（进入 P2 需求评审）。

---

## 示例

详见 `references/examples.md`。

---

## 错误处理

| 场景 | 处理 |
|------|------|
| 目录已存在 | 覆盖 / 修改 / 新名称 |
| 用户取消 | 保存草稿或直接结束 |
| 必填字段缺失 | 提示后用 `[待补充]` 占位 |

---

## Script Directory

| Script | 用途 |
|--------|------|
| `scripts/validate-requirements.py` | 验证需求文档完整性 |
| `scripts/calculate-risk.py` | 计算风险等级 |
| `scripts/generate-flow-status.py` | 生成流程状态文件 |

---

## References

| 文件 | 用途 |
|------|------|
| `references/templates/software-feature.md` | 软件功能需求模板 |
| `references/templates/bug-fix.md` | Bug 修复需求模板 |
| `references/templates/refactoring.md` | 重构优化需求模板 |
| `references/writing-style.md` | 正式学术风格指南 |
| `references/examples.md` | 示例 |
