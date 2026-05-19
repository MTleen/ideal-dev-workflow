# P5-编码计划

> **For Claude:** REQUIRED SUB-SKILL: Use ideal-dev-exec to implement this plan task-by-task.

**Goal:** {一句话描述构建什么}

**Architecture:** {2-3 句关于方法}

**Tech Stack:** {关键技术/库}

---

## 概述

| 项目 | 内容 |
|------|------|
| 需求名称 | {requirement_name} |
| 技术方案 | P3-技术方案.md |
| 生成日期 | {date} |

---

## 模块总览

| 模块编号 | 模块名称 | 任务数 | 依赖 | 执行策略 | 预估时间 |
|----------|----------|--------|------|----------|----------|
| M1 | {name} | {count} | {deps} | parallel/sequential | {time} |

**总计**: {total_tasks} 个任务

**时间预估**: 串行 {serial_time} → 并行优化后 {parallel_time}

---

## 任务依赖图

```mermaid
flowchart TB
    subgraph Layer0[Layer 0 - 可并行]
        M1[M1: {模块名}]
        M2[M2: {模块名}]
    end

    subgraph Layer1[Layer 1]
        M3[M3: {模块名}]
    end

    M1 --> M3
    M2 --> M3
```

---

## 并行执行计划

| 批次 | 模块 | 说明 |
|------|------|------|
| Batch 1 | M1, M2 | 无依赖，可并行 |
| Batch 2 | M3 | 依赖 Batch 1 |

---

## 模块详情

### M1: {模块名称}

**目标**: {一句话描述}

**依赖**: 无 / M{x}, M{y}

**执行策略**: parallel / sequential

**文件范围**:
- 新增: `{file_path}`
- 修改: `{file_path}`

**任务列表**:

---

#### 任务 M1-T1: {任务名称}

**目标**: {一句话描述}

**Step 1: 编写失败测试**

```{language}
// {test_file_path}

{test_code}
```

**Step 2: 运行确认失败**

Run: `{test_command}`
Expected: FAIL with "{error_message}"

**Step 3: 实现最小代码**

```{language}
// {source_file_path}

{minimal_code}
```

**Step 4: 运行确认通过**

Run: `{test_command}`
Expected: PASS (0 failures)

**Step 5: 提交代码**

```bash
git add {files}
git commit -m "feat({scope}): {description}"
```

**验证标准**: {如何验证完成}

---

#### 任务 M1-T2: {任务名称}

**目标**: {一句话描述}

**Step 1: 编写失败测试**

```{language}
// {test_file_path}

{test_code}
```

**Step 2: 运行确认失败**

Run: `{test_command}`
Expected: FAIL

**Step 3: 实现最小代码**

```{language}
// {source_file_path}

{minimal_code}
```

**Step 4: 运行确认通过**

Run: `{test_command}`
Expected: PASS

**Step 5: 提交代码**

```bash
git add {files}
git commit -m "feat({scope}): {description}"
```

**验证标准**: {如何验证完成}

---

### M2: {模块名称}

{同上格式}

---

## 最终验证

**所有批次完成后必须验证**：

```bash
# 运行完整测试套件
{test_command}

# 预期：所有测试通过（exit 0）
```

**验证清单**：
- [ ] 所有测试通过（有输出证据）
- [ ] 所有任务已完成
- [ ] 代码已提交

---

## 验收标准

| 编号 | 标准 | 验证方式 |
|------|------|----------|
| AC-1 | {standard} | {method} |
| AC-2 | {standard} | {method} |

---

## 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| {risk} | {impact} | {mitigation} |

---

## 执行交接

计划已完成。选择执行方式：

**选项 1: Subagent-Driven (当前会话)**
- 每任务派遣子代理
- 任务间两阶段审查（规范合规 + 代码质量）
- 快速迭代

**选项 2: Parallel Session (独立会话)**
- 打开新会话
- 调用 ideal-dev-exec 批量执行
- 批次间检查点
