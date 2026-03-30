---
name: ideal-code-review
description: Use for two-stage code review after batch execution. Reviews spec compliance first, then code quality. Called by ideal-dev-exec automatically.
agents: [check]
---

# ideal-code-review（代码审查）

## Overview

两阶段代码审查 skill，由 ideal-dev-exec 批次完成后自动调用。

1. **规范合规审查**（是否按计划实现）
2. **代码质量审查**（风格、性能、安全）

## Agents

| Agent | 角色 | 用途 |
|-------|------|------|
| check | 代码检查工程师 | 两阶段审查、自我修复、验证 |

```markdown
Task(
    subagent_type: "check",
    prompt: "执行两阶段代码审查：规范合规 + 代码质量",
    model: "opus"
)
```

## When to Use

**自动调用**：ideal-dev-exec 每批次完成后 / 最终验证后

**手动调用**：P10 代码评审、合并前验证、修复复杂 bug 后

## Output

| 输出 | 路径 |
|------|------|
| 审查报告 | `docs/迭代/{需求名称}/P9.1-代码审查.md` |

## HARD GATE

```
╔══════════════════════════════════════════════════════════════════╗
║  NO CODE QUALITY REVIEW BEFORE SPEC COMPLIANCE PASS           ║
╚══════════════════════════════════════════════════════════════════╝
```

**必须先通过规范合规审查，才能进行代码质量审查。**

## Ralph Loop

```
ideal-dev-exec 完成批次
    ↓
Task(check)
    ↓
Phase 1 规范合规
    ↓ (不合规) → check 子代理修复 → 重新审查
    ↓ (合规)
Phase 2 代码质量
    ↓ (有问题) → 能自修复? → check 修复 → 重新审查
    ↓           → 不能自修复 → Task(debug) → 重新审查
    ↓ (通过)
生成审查报告
```

## Phase 1: 规范合规审查

### 审查清单

```markdown
## 规范合规审查
- [ ] 实现了计划中指定的所有功能？
- [ ] 没有遗漏计划中的功能？
- [ ] 没有添加计划外的功能？
- [ ] 只修改了计划中指定的文件？
- [ ] 测试覆盖了计划中的验证标准？
- [ ] 接口签名符合计划？
```

### 不合规处理

```
记录不合规项 → 调用 check 子代理修复 → 重新审查
```

---

## Phase 2: 代码质量审查

**前置条件**：只有 Phase 1 通过后才进行。

### 审查清单

```markdown
## 代码质量审查

### 代码风格
- [ ] 命名清晰、一致？
- [ ] 代码格式符合项目规范？

### 可读性
- [ ] 逻辑清晰，易于理解？
- [ ] 函数/方法长度合理？

### 性能
- [ ] 无明显的性能问题？

### 安全
- [ ] 无安全隐患？
- [ ] 输入验证完整？

### 可维护性
- [ ] 代码重复度低？
- [ ] 依赖关系清晰？
```

### 问题分级

| 级别 | 说明 | 处理方式 |
|------|------|----------|
| Critical | 必须立即修复 | 阻断，立即修复 |
| Important | 应该修复 | 继续前修复 |
| Minor | 可选改进 | 记录，后续处理 |

---

## Review Report 格式

```markdown
# P9.1-代码审查

## 概述
| 项目 | 内容 |
|------|------|
| 需求名称 | {name} |
| 审查日期 | {date} |
| 审查范围 | Batch {n} / 全部 |

---

## 阶段一：规范合规审查

| 检查项 | 状态 |
|--------|------|
| 计划功能全部实现 | ✅ / ❌ |
| 无计划外功能 | ✅ / ❌ |
| 文件范围正确 | ✅ / ❌ |

**合规结论**: ✅ 通过 / ❌ 不合规

---

## 阶段二：代码质量审查

| 级别 | 问题描述 | 文件位置 | 状态 |
|------|----------|----------|------|
| Critical | {description} | {file}:{line} | 待修复 |

**质量结论**: ✅ 通过 / ❌ 需修复

---

## 审查结论

| 阶段 | 结果 |
|------|------|
| 规范合规 | ✅ 通过 |
| 代码质量 | ✅ 通过 |

**最终结论**: ✅ 审查通过
```

---

## Review Team 行为准则

详见 `references/feedback-principles.md`。

---

## Quality Checklist

**Phase 1 完成**：
- [ ] 检查了所有计划功能
- [ ] 验证了文件范围
- [ ] 确认了测试覆盖

**Phase 2 完成**：
- [ ] 检查了代码风格
- [ ] 评估了可读性
- [ ] 评估了性能
- [ ] 评估了安全
- [ ] 评估了可维护性

**报告完成**：
- [ ] 生成了审查报告
- [ ] 记录了所有问题

---

## References

- `references/feedback-principles.md` — Review Team 行为准则
- `references/templates/review-report-template.md` — 报告模板
