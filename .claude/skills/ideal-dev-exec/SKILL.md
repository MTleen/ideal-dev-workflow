---
name: ideal-dev-exec
description: Use when P8 test case review is completed and development execution is needed. Executes coding tasks following TDD principles with Git branch management.
agents: [implement, check, debug]
---

# ideal-dev-exec（P9 开发执行）

## 角色定位

Phase Skill — **执行协调者**。

职责：
1. 加载所需上下文（stories/ + P5 编码计划）
2. 调度子智能体按拓扑顺序执行任务
3. 将代码写入项目文件系统
4. 返回执行摘要

**不负责**：更新 flow state、验证前置条件、协调评审。

---

## 输入

| 来源 | 内容 |
|------|------|
| stories/ | 上下文隔离的故事文件和任务清单 |
| P5-编码计划.md | 任务依赖关系、验证清单 |
| project-config.md | Git 分支配置、测试/构建命令 |

## 输出

| 输出 | 位置 |
|------|------|
| 代码实现 | `src/` |
| 测试代码 | `tests/` |

---

## 子智能体调度

| 调用时机 | 子智能体 | 任务 |
|----------|----------|------|
| 代码实现 | `implement` | 按故事文件执行任务，遵循 TDD |
| 代码检查 | `check` | 规范合规审查 + 代码质量审查 |
| 调试支援 | `debug` | 根因分析、问题调试（失败时调用） |

### TDD 协议

详见 `references/tdd-protocol.md`。

### check 子智能体职责

**两阶段审查**：

```
Phase 1 — 规范合规审查
  ├─ 实现了计划中指定的功能？
  ├─ 没有添加计划外的功能？
  └─ 测试覆盖了计划中的验证标准？

Phase 2 — 代码质量审查
  ├─ 代码风格符合项目规范？
  ├─ 无明显性能问题？
  └─ 无安全隐患？

发现问题 → 自我修复 → 重新验证
```

---

## 执行流程

```
Step 1: 加载上下文
  ├─ 读取 stories/index.md
  ├─ 确定执行顺序（拓扑排序）
  └─ 读取 project-config.md

Step 2: 环境检查
  ├─ 读取 flow state 中的 worktree.path
  ├─ 验证当前目录是否为 worktree.path
  └─ 若不在正确的 worktree 中，终止并报告错误

Step 3: 验证干净基线
  └─ 运行测试套件，确认基线通过

Step 4: 按拓扑层级执行任务
  ├─ 第 1 层（无依赖）→ 并行执行
  ├─ 第 2 层 → 第 1 层完成后并行执行
  └─ 每批次：
      ├─ Task(implement)
      └─ Task(check) → 不通过 → Task(debug) → 修复后重审

Step 5: 最终验证
  ├─ 运行完整测试套件
  └─ 运行构建验证

Step 6: 返回摘要
```

---

## 质量检查清单

每批次完成后：
- [ ] implement 返回了实现报告
- [ ] check 通过了两阶段审查
- [ ] 测试套件全部通过

全部完成后：
- [ ] 所有任务已完成
- [ ] 代码已提交

---

## 返回格式

```markdown
## P9 开发执行 — 执行摘要

### 执行统计
- 总故事数：{N}，完成：{N}，跳过：{N}

### 批次执行记录
| 批次 | 故事 | 状态 | 耗时 |
|------|------|------|------|
| 1 | 001, 002 | ✅ 完成 | {X}min |

### 最终验证
- 测试套件：{通过/失败}
- 构建验证：{通过/失败}

### 产出文件
{列出所有修改/创建的文件}
```
