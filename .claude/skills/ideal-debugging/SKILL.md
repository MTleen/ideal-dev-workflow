---
name: ideal-debugging
description: Use when encountering bugs, test failures, or unexpected behavior. Implements systematic debugging with root cause analysis before any fixes.
agents: [debug]
---

# ideal-debugging（系统化调试）

## Overview

系统化调试 skill，实现根因分析驱动的 bug 修复流程。

**不在 15 阶段中** - 任何阶段遇到 bug 时独立调用。

## Agents

| Agent | 角色 | 用途 |
|-------|------|------|
| debug | 调试工程师 | 根因分析、TDD 修复 |

```markdown
Task(
    subagent_type: "debug",
    prompt: "执行系统化调试：根因调查 → 模式分析 → 假设测试 → TDD 修复",
    model: "opus"
)
```

## HARD GATE

```
╔══════════════════════════════════════════════════════════════════╗
║  NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST             ║
╚══════════════════════════════════════════════════════════════════╝
```

**在完成 Phase 1 之前，禁止提出任何修复方案。**

## When to Use

- 测试失败（单元测试、集成测试、E2E 测试）
- 运行时错误、意外行为、性能问题
- 任何需要调试的场景

## Trigger Points

| 触发场景 | 调用方式 |
|----------|----------|
| ideal-dev-exec 批次执行中失败 | 自动调用 |
| P11 测试执行发现 bug | 自动调用 |
| 任何阶段发现 bug | 手动调用 |

---

## Phase 1: Root Cause Investigation（必须完成）

**在提出任何修复前，必须完成此阶段。**

### 1.1 仔细阅读错误消息

- 完整阅读错误消息和堆栈跟踪
- 识别错误类型（TypeError, ReferenceError, AssertionError 等）
- 定位错误发生位置（文件、行号、函数）

### 1.2 一致地复现

- 确定复现步骤，多次执行确认稳定性
- 记录复现条件（输入、状态、环境）
- 确认是否随机/间歇性

### 1.3 检查最近变更

```bash
git log --oneline -10
git diff HEAD~5..HEAD
git log -p -- path/to/file  # 特定文件变更
```

### 1.4 收集证据

- 检查相关日志、数据库状态、API 请求/响应
- 检查并发情况

### 1.5 追踪数据流

- 从输入到输出的完整路径
- 识别数据转换点、状态变更点、边界条件

**Phase 1 输出**：根因假设 + 证据支持 + 置信度（1-10）

---

## Phase 2: Pattern Analysis

- 找到代码库中类似功能的正确实现
- 对比成功和失败场景的差异
- 理解依赖组件的状态和配置

---

## Phase 3: Hypothesis and Testing

**一次只测试一个假设。**

```
假设: {单一、具体的根因假设}
预期: 如果假设正确，修改 {X} 应该解决问题
```

- 编写最小复现测试，确认测试失败（验证假设）
- 如果失败，形成新假设；如果成功，进入 Phase 4
- **如果不知道原因，明确说"不知道"，而不是猜测**

---

## Phase 4: Implementation (TDD)

### 4.1 创建失败测试用例

```
测试名称: test_{bug_description}
测试目的: 复现 bug 并验证修复
预期失败: {failure_reason}
```

### 4.2 实现单一修复

**原则**：最小修改、单一目的、不重构（除非是根因）

### 4.3 验证修复

运行新测试 → 运行相关测试 → 运行完整测试套件

### 4.4 如果修复无效

**返回 Phase 1**，重新调查。

---

## Red Flags: 3+ 次失败后质疑架构

| 红旗 | 说明 |
|------|------|
| 共享状态耦合 | 每次修复在不同地方揭示新的共享状态问题 |
| 大规模重构 | 修复需要"大规模重构"才能工作 |
| 症状转移 | 每次修复在其他地方产生新症状 |
| 循环依赖 | 修复 A 导致 B 失败，修复 B 导致 A 失败 |

遇到红旗时：停止调试，报告架构问题，等待架构决策。

---

## Output

**不落盘** - 调试过程只在执行时输出，不创建文档。

```markdown
## 调试报告
### 问题：{问题描述}
### 根因：{根因分析结果}
### 修复：{修复内容}
### 验证：{验证结果}
```

---

## Quality Checklist

**Phase 1 完成**：
- [ ] 完整阅读错误消息
- [ ] 成功复现问题
- [ ] 检查了最近变更
- [ ] 收集了相关证据
- [ ] 形成了根因假设

**Phase 4 完成**：
- [ ] 创建了失败测试用例
- [ ] 实现了最小修复
- [ ] 新测试通过 + 相关测试通过 + 完整测试套件通过
