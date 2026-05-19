---
name: ideal-flow-control
description: "Use when managing workflow phase transitions and state control. This is the orchestration protocol — it defines how the main agent routes between phases, when to invoke phase skills, and how to coordinate the YOLO review team. Handle with care: state updates here drive the entire workflow."
---

> **主智能体（Claude Code 会话）职责：仅编排，不执行。所有阶段内的工作（读文件、做调研、写文档）全部由 Phase Skill 通过 sub-agent 完成。**

# ideal-flow-control（流程编排协议）

## 角色定位

**主智能体 = 编排器（Orchestrator）**，永远不直接执行工作。

### 主智能体只做三件事

1. **读取** `流程状态.md`，确定当前阶段
2. **调用** Phase Skill（作为 team lead 调度 sub-agent 完成所有工作）
3. **更新** `流程状态.md`，推进到下一阶段

### 主智能体绝对不做

- ❌ 读取项目文件（代码、文档）
- ❌ 做代码分析、架构设计、风险评估
- ❌ 写文档内容
- ❌ 做技术决策
- ❌ 验证构建结果

所有上述工作由 Phase Skill 内部 spawn 的 sub-agent 完成。

---

## 核心原则

### 两种执行模式

主智能体有两种执行模式，由流程状态.md 中的 `yolo_mode` 字段控制：

| 模式 | yolo_mode | 行为 |
|------|-----------|------|
| **手动模式** | `false` | 每次阶段完成后停下来，等待用户确认后再推进 |
| **自动循环模式** | `true` | 阶段完成后不停止，自动推进直到流程完成（P15）或熔断 |

### 手动模式行为（yolo_mode: false）

```
1. 读取 流程状态.md → current_phase
2. 判断阶段类型
   ┌─────────────────────────────────────┐
   │ 产物阶段（P1/P3/P5/P7/P9/P11/P13）  │
   │   → 调用 Phase Skill                 │
   │   → 等待 Skill 返回                  │
   │   → 验证产物文件存在                │
   │   → 更新 current_phase               │
   │   → ⏸ 停下来等待用户确认            │
   ├─────────────────────────────────────┤
   │ 评审阶段（P2/P4/P6/P8/P10/P12/P14） │
   │   → 展示摘要 → 询问 YOLO → 等确认   │
   ├─────────────────────────────────────┤
   │ 交付阶段（P15）                      │
   │   → 调用 ideal-delivery             │
   │   → ⏸ 停下来等待用户确认            │
   └─────────────────────────────────────┘
```

### 自动循环模式行为（yolo_mode: true）— 核心优化

**主智能体在 YOLO 模式下是"永不停歇的循环器"**。阶段完成后**立即回到起点**，不等待用户输入，直到流程终止。

```
YOLO 自动循环：

循环（永不停止，除非满足终止条件）：
  1. 读取 流程状态.md → current_phase, status, yolo_mode
  2. 检查终止条件（见下方）→ 满足则输出结果，停止循环
  3. 确定当前阶段 X = 第一个未完成的阶段
     （遍历 P1→P2→...→P15，查找第一个状态不为 completed/approved 的阶段）
     ⚠️ 序列完整性校验：X 序号 <= current_phase → 前置阶段被跳过，输出警告并停住
  4. 如果 X 是产物阶段（P1/P3/P5/P7/P9/P11/P13）：
       → 调用 Phase Skill（内部 spawn sub-agent 完成所有工作）
       → 等待 Skill 返回
       → 验证产物文件存在且非空
       → 更新 flow state：X > current_phase 时才推进 current_phase → X，状态设为 completed/approved
       → 立即回到循环起点（步骤 1）
  5. 如果 X 是评审阶段（P2/P4/P6/P8/P10/P12/P14）：
       → 调用 ideal-yolo 执行评审
       → 等待评审结果
       → 如果 "通过" → 更新为 approved（current_phase 不回退）→ 立即回到循环起点
       → 如果 "熔断" → 输出熔断报告 → 停止循环，等待人工介入
  6. 如果 X 是交付阶段（P15）：
       → 调用 ideal-delivery
       → 等待完成
       → 更新状态为 "已完成"
       → 输出流程完成摘要 → 停止循环
```

**步骤 3 的阶段序列完整性校验（新增）**：

| 场景 | 检测逻辑 | 处理方式 |
|------|----------|----------|
| X 序号 == current_phase + 1 | 正常，下一阶段 | 继续执行 |
| X 序号 <= current_phase | **前置阶段被跳过** | 输出警告：跳过了 P{current_phase} 之前的某些阶段，停止循环，等待人工确认 |

**终止条件**（满足任一即停止）：
- `status: 已完成` 或 `status: 已交付`
- P15 阶段已完成（current_phase = P15 且评审通过）
- `ideal-yolo` 返回熔断信号 → 停止循环，报告未解决问题

**关键原则**：YOLO 模式下，主智能体在每次阶段完成后**立即回到循环起点**，不输出"等待用户确认"之类的提示，不停下来。循环直到终止条件满足。

---

## 阶段类型定义

| 类型 | 阶段 | 主智能体行为 |
|------|------|-------------|
| **产物阶段** | P1, P3, P5, P7, P9, P11, P13 | 调用 Phase Skill，等待完成，更新 flow state |
| **评审阶段** | P2, P4, P6, P8, P10, P12, P14 | YOLO/人工评审处理 |
| **交付阶段** | P15 | 触发 ideal-delivery |

---

## Phase Skill 调用协议

### 阶段 → Skill 映射

| 阶段 | Phase Skill |
|------|-------------|
| P1 | `ideal-requirement` |
| P3 | `ideal-dev-solution` |
| P5 | `ideal-dev-plan` |
| P7 | `ideal-test-case` |
| P9 | `ideal-dev-exec` |
| P11 | `ideal-test-exec` |
| P13 | `ideal-wiki` |

### 主智能体调用流程（每次只推进一个阶段）

```
1. 读取 flow state → current_phase = X
2. 确定 Phase Skill 名称
3. 调用 Skill（Skill 内部 spawn sub-agent 完成所有工作）
4. 等待 Skill 返回执行摘要
5. 验证产物文件存在且非空
6. 更新 flow state：current_phase → X+1，status 更新
7. 继续循环
```

### Phase Skill 职责边界

Phase Skill 是 **team lead**，它负责：

| Phase Skill 负责 | Phase Skill 不负责 |
|------------------|-------------------|
| 读取 P1 等前置文档 | 更新 flow state |
| spawn sub-agent 调研和分析 | 验证前置条件 |
| spawn sub-agent 写文档 | 决定评审结果 |
| 写入产物文件 | 调度其他 Phase Skill |
| 返回执行摘要 | |

---

## 子迭代父状态同步协议

**关键规则**：当子迭代完成任何阶段（P1-P15），主智能体**必须**同步更新父迭代的 `流程状态.md`。

### 检测子迭代

```
1. 读取当前迭代的 流程状态.md
2. 检查 frontmatter 中是否存在 parent 字段
3. 如存在 → 当前是子迭代，需要执行父状态同步
4. 如不存在 → 当前是父迭代或独立迭代，无需同步
```

### 同步时机

| 事件 | 同步动作 |
|------|---------|
| 子迭代首次开始执行（P1） | 父迭代目录从 `[待启动]` 重命名为 `[进行中]`，更新所有子迭代的 `parent.path` |
| 子迭代任一阶段完成 | 更新父迭代 `sub_iterations` 中对应子迭代的 `current_phase` |
| 子迭代 P15 完成 | 额外更新 `status: 已完成` 和 `completed_at` |
| 所有子迭代 P15 完成 | 父迭代目录从 `[进行中]` 重命名为 `[已完成]` |

### 同步操作

```
1. 从子迭代 流程状态.md 的 parent.path 获取父迭代目录路径
2. 读取父迭代的 流程状态.md
3. 在 sub_iterations 列表中找到当前子迭代（匹配 id）
4. 更新该子迭代的 status 和 current_phase
5. 更新父迭代的 updated_at 为当前时间
6. 写回父迭代的 流程状态.md
```

### 父迭代 flow state 中的子迭代格式

```yaml
sub_iterations:
  - id: A
    name: 后端图谱API服务
    status: 已完成          # 待启动 | 进行中 | 已完成
    current_phase: P15      # 子迭代当前阶段
    completed_at: 2026-04-03  # 仅在已完成时有值
  - id: B
    name: 前端图谱渲染
    status: 进行中
    current_phase: P9
```

> **⚠️ 如果不执行父状态同步，会导致父迭代的子迭代列表永远显示"待启动"，无法正确追踪项目进度。**

Phase Skill 是 **team lead**，它负责：

| Phase Skill 负责 | Phase Skill 不负责 |
|------------------|-------------------|
| 读取 P1 等前置文档 | 更新 flow state |
| spawn sub-agent 调研和分析 | 验证前置条件 |
| spawn sub-agent 写文档 | 决定评审结果 |
| 写入产物文件 | 调度其他 Phase Skill |
| 返回执行摘要 | |

---

## Git Worktree 协议

### 基本原则

**整个迭代生命周期（P1 ~ P15）必须在独立的 Git Worktree 中执行**，禁止在 main 分支或 release 分支上直接进行任何迭代相关工作。

### Worktree 路径规范

```
<repo_toplevel>/worktrees/<branch>
```

| 组成部分 | 说明 |
|----------|------|
| `repo_parent` | 仓库父目录（`git rev-parse --show-toplevel` 的父目录） |
| `repo_name` | 仓库名称（不含 `.git` 后缀） |
| `branch` | 功能分支名（sanitized，`/` 替换为 `-`） |

**示例**：
- 仓库路径：`/Users/foo/projects/IdealClaw`
- 功能分支：`feature/mat5-multi-layer-memory`
- Worktree 路径：`/Users/foo/projects/IdealClaw/worktrees/feature-mat5-multi-layer-memory`

### 分支命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 功能分支 | `feature/<short-name>` | `feature/mat5-multi-layer-memory` |
| 修复分支 | `fix/<short-name>` | `fix/chat-api-timeout` |
| 重构分支 | `refactor/<short-name>` | `refactor/session-manager` |

> **short-name 规则**：需求 ID（如 MAT-5）+ 简短描述，不超过 50 字符

### 流程状态 Worktree 字段

在 `流程状态.md` 的 YAML frontmatter 中新增 `worktree` 字段：

```yaml
---
requirement_name: {需求名称}
current_phase: P5
status: in_progress
yolo_mode: false
worktree:
  branch: feature/mat5-multi-layer-memory
  path: /Users/foo/projects/IdealClaw/worktrees/feature-mat5-multi-layer-memory
  created_at: {YYYY-MM-DD}
created_at: {创建时间}
updated_at: {更新时间}
---
```

### Worktree 执行时机

```
[创建 worktree，分支名 feature/<short-name>]
    ↓
P1 需求编写 → P2 需求评审 → P3 技术方案 → P4 编码计划 → ... → P14 维基评审
    ↓
[P15 成果提交后删除 worktree]
```

**注意**：Worktree 在 **P1 开始前创建**，整个迭代生命周期（包含调研、文档编写、编码、测试）都在 worktree 中进行。

### 创建 Worktree

使用 git 命令创建 worktree：

```bash
# 计算 worktree 路径
REPO_PATH=$(git rev-parse --show-toplevel)
BRANCH="feature/mat5-multi-layer-memory"
SANITIZED_BRANCH=$(echo "$BRANCH" | sed 's/\//-/g')
WORKTREE_PATH="$REPO_PATH/worktrees/$SANITIZED_BRANCH"

# 创建 worktree（在仓库根目录下创建 worktrees/ 子目录）
mkdir -p "$REPO_PATH/worktrees"
git worktree add -b "$BRANCH" "$WORKTREE_PATH"
```

### 自动切换（关键）

**创建或识别到 worktree 后，必须立即切换进去**：

```
1. 检查当前是否在 worktree 中：
   pwd | grep worktrees
   git branch --show-current | grep -E '^feature/|^fix/|^refactor/'

2. 如不在 worktree 中，使用以下命令切换到 worktree 目录：
   cd /path/to/repo/worktrees/feature-{short-name}

3. 验证切换成功：
   pwd  # 确认路径包含 worktrees
   git branch --show-current  # 确认是 feature/xxx 分支
```

**重要**：切换到 worktree 后，后续所有操作都在 worktree 分支上执行，直到 P15 完成后才退出。**必须使用 `cd` 命令真正切换目录，而不仅仅是创建 worktree**。

### 子迭代 Worktree 继承（关键）

**子迭代不创建独立 worktree，直接继承父迭代的 worktree。**

```
1. 检测当前迭代是否为子迭代（parent 字段是否存在）
2. 如是子迭代：
   ├─ 从 parent.path 读取父迭代目录路径
   ├─ 从父迭代的 流程状态.md 读取 worktree 信息
   ├─ 切换到父 worktree 目录：cd {worktree.path}
   └─ 验证：pwd 包含 worktrees，分支正确
3. 如不是子迭代：
   └─ 按正常流程创建 worktree（见上方"创建 Worktree"）
```

**禁止操作**：
- ❌ 为子迭代创建独立 worktree
- ❌ 子迭代完成后删除 worktree
- ❌ 子迭代完成后删除 feature branch

### 质量检查清单（Worktree）

- [ ] P1 开始前已创建 worktree
- [ ] **已使用 `cd` 切换到 worktree 目录**
- [ ] 当前分支是 feature/fix/refactor 分支，不是 main/release
- [ ] `流程状态.md` 中已记录 worktree 路径
- [ ] P15 完成后已删除 worktree
- [ ] Worktree 删除后才能合并主分支

---

## 流程状态文件协议

**路径**：`docs/迭代/{需求名称}/流程状态.md`

**格式**：

独立迭代 / 父迭代：
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
created_at: {创建时间}
updated_at: {更新时间}
---
```

> **⚠️ `parent` 字段是区分父子迭代的唯一标识**。没有 `parent` 字段 = 父迭代/独立迭代；有 `parent` 字段 = 子迭代。所有依赖父子迭代判断的 skill 都通过此字段识别。

## 阶段状态

| 阶段 | 状态 | 更新时间 | 评审意见 |
|------|------|----------|----------|
| P1 需求编写 | ✅ completed | {时间} | - |
| P2 需求评审 | ⏳ pending | - | - |
```

**状态枚举**：

| 值 | 含义 |
|----|------|
| `pending` | 未开始 |
| `in_progress` | 进行中 |
| `completed` | 已完成 |
| `approved` | 评审通过 |
| `blocked` | 被阻塞 |

**阶段推进规则**：

| 当前阶段 | 前置条件 | 人工模式推进动作 | YOLO 模式推进动作 |
|----------|----------|------------------|------------------|
| P1 → P2 | P1 completed | 自动 | 自动 |
| P2 → P3 | P2 approved | 展示摘要 → 询问 YOLO → 人工确认"通过" | 自动调用 ideal-yolo |
| P3 → P4 | P3 completed | 自动 | 自动 |
| P4 → P5 | P4 approved | 人工说"通过" | 自动调用 ideal-yolo |
| P5 → P6 | P5 completed | 自动 | 自动 |
| P6 → P7 | P6 approved | 人工说"通过" | 自动调用 ideal-yolo |
| P7 → P8 | P7 completed | 自动 | 自动 |
| P8 → P9 | P8 approved | 人工说"通过" | 自动调用 ideal-yolo |
| P9 → P10 | P9 completed | 自动 | 自动 |
| P10 → P11 | P10 approved | 人工说"通过" | 自动调用 ideal-yolo |
| P11 → P12 | P11 completed | 自动 | 自动 |
| P12 → P13 | P12 approved | 人工说"通过" | 自动调用 ideal-yolo |
| P13 → P14 | P13 completed | 自动 | 自动 |
| P14 → P15 | P14 approved | 自动 | 自动，触发 ideal-delivery |

---

## 评审阶段处理

### YOLO 自动循环模式（`yolo_mode: true`）

YOLO 模式下，主智能体永不停止，直到流程完成或熔断：

1. **产物阶段完成 → 自动推进**：调用对应 Phase Skill，完成后立即更新 flow state 并进入下一阶段
2. **评审阶段**：自动调用 `ideal-yolo` 执行评审
   - `ideal-yolo` 返回"通过"→ 更新为 approved，立即推进到下一阶段
   - `ideal-yolo` 返回"熔断"→ 输出熔断报告，停止循环，等待人工介入
3. **P15 交付阶段**：调用 `ideal-delivery`，完成后更新状态为"已完成"，输出流程完成摘要

**熔断处理**：当评审返回熔断信号时，主智能体停止循环，输出完整的熔断报告（包括未解决的问题列表），等待人工处理。人工介入后，可选择：
- 修复问题后继续（保持 YOLO 模式）
- 切换回手动模式
- 中止流程

### 人工模式（默认，`yolo_mode: false`）

```
1. 产物阶段完成后 → 停下来，展示产物摘要
2. 评审阶段完成后：
   a) 展示评审摘要
   b) 询问是否进入 YOLO 模式（见下方选项）
   c) 等待用户响应：
      - "通过" / "ok" / "approved" → 更新为 approved，推进下一阶段（保持人工模式）
      - "YOLO" / "启用 YOLO" / "yolo" → yolo_mode 改为 true → 输出"YOLO 模式已启用，后续自动推进"，继续推进
      - "通过，YOLO" → 同时更新 approved + yolo_mode: true
      - 其他反馈 → 记录反馈，等待进一步指示
```

**YOLO 模式提示词（每次评审阶段必须展示）**：

```
评审摘要已生成。
请选择后续处理方式：
  1. [通过] — 继续下一阶段（保持手动模式）
  2. [通过，启用 YOLO] — 通过并启用 YOLO 模式，后续评审自动推进
  3. [启用 YOLO] — 不通过评审但启用 YOLO 模式，让 AI 自动迭代修复
  4. [其他反馈] — 提供具体修改意见
```

**切换到 YOLO 模式**：修改流程状态.md 中 `yolo_mode: false` → `yolo_mode: true`，后续所有评审阶段自动走 ideal-yolo，无需再次触发。

---

## 质量检查清单

### YOLO 模式下每次循环迭代必须验证

- [ ] flow state 文件格式正确（YAML frontmatter 有效）
- [ ] **阶段序列完整性：查找到的第一个未完成阶段序号 <= current_phase + 1**
- [ ] 当前阶段的前置条件已满足（completed/approved）
- [ ] 产物文件已写入正确路径
- [ ] 产物内容非空
- [ ] 时间戳已更新
- [ ] 流程状态.md 中状态字段正确反映当前阶段
- [ ] 熔断信号被正确识别并处理（停止循环，报告问题）
- [ ] 流程完成时输出完整执行摘要
- [ ] **当前在 worktree 中执行（pwd 包含 worktrees）**
- [ ] **如是子迭代，父迭代的 sub_iterations 状态已同步更新**

### 通用质量要求

- [ ] P2 评审阶段已展示 YOLO 模式选项提示
- [ ] 主智能体未直接执行任何阶段内工作（全部由 Skill 调度 sub-agent 完成）
- [ ] YOLO 模式下阶段完成后立即回到循环起点，不停下来等待用户
- [ ] P1 开始前已创建 worktree（路径格式：`<repo_toplevel>/worktrees/<branch>`）
- [ ] **已使用 `cd` 切换到 worktree 目录**
- [ ] 当前分支是 feature/fix/refactor 分支，不是 main/release
- [ ] `流程状态.md` 中已记录 worktree 路径
