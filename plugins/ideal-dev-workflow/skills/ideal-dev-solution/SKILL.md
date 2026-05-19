---
name: ideal-dev-solution
description: Use when P2 requirement review is completed and technical solution generation is needed. Analyzes requirements and generates comprehensive technical design including architecture, tech stack, data models, and risk analysis.
agents: [general-purpose (x6 parallel)]
---

> **Phase Skill 角色**：Team Lead。主智能体调用本 Skill 后，本 Skill 全权负责：加载上下文 → spawn sub-agent 完成所有工作 → 写入产物文件 → 返回摘要。主智能体只等待本 Skill 返回。

# ideal-dev-solution（P3 技术方案生成）

## 职责边界

| 本 Skill 负责 | 本 Skill 不负责 |
|--------------|----------------|
| 读取 P1 需求文档 | 更新 flow state |
| 读取项目配置 | 验证前置条件 |
| spawn sub-agent 执行调研 | 决定评审结果 |
| spawn sub-agent 写 P3 文档 | 调度其他 Skill |
| 写入 `P3-技术方案.md` | |
| 返回执行摘要 | |

---

## 输入

| 来源 | 内容 |
|------|------|
| `docs/迭代/{需求名}/P1-需求文档.md` | 功能需求、验收标准、约束条件 |
| `CLAUDE.md` | 项目背景、技术栈 |
| `.claude/project-config.md` | 项目配置 |

## 输出

| 文件 | 路径 |
|------|------|
| `P3-技术方案.md` | `docs/迭代/{需求名称}/P3-技术方案.md` |

---

## 执行流程（全部由 sub-agent 完成）

> **强制要求**：阶段内所有工作必须通过 Agent 工具（`subagent_type: general-purpose`）并行调度。**主智能体不读取文件、不分析代码、不写文档**。所有工作由本 Skill 的 sub-agent 执行。

> **调研原则**（必须遵守）：
> 1. **必须使用 `ideal-deep-research` 进行详细调研** — 任何技术选型、功能方案必须先调研现有最佳实践，不能凭直觉设计
> 2. **必须避免重复造轮子** — 优先调研现有开源项目、SDK、框架是否可复用，引用调研报告作为方案依据

### Step 1: 加载上下文

Spawn 一个 sub-agent（`context-loader`）读取：

- `docs/迭代/{需求名}/P1-需求文档.md` 完整内容
- `CLAUDE.md` 项目背景和技术栈
- `.claude/project-config.md` 项目配置
- `docs/迭代/{需求名}/research/` 目录下的已有调研报告（如存在）

### Step 2: 详细调研（先于并行调研执行）

**使用 `ideal-deep-research` 进行技术调研**，调研内容包括：

| 调研方向 | 调研目的 |
|---------|---------|
| 竞品实现方案 | 业界如何实现类似功能，参考成熟方案 |
| 最新技术趋势 | 是否有更优的技术方案 |
| 开源项目复用 | 是否有可复用的开源项目/SDK |
| 踩坑记录 | 他人遇到的坑及解决方案 |

**调研报告输出路径**：`docs/迭代/{需求名}/research/P3-技术调研_{timestamp}.md`

> **重要**：技术选型、功能设计必须基于调研报告，禁止凭空设计。

### Step 3: 并行调研（6 个 sub-agent 同步执行）

| sub-agent | 任务 |
|-----------|------|
| `agent-requirements` | 功能分解、依赖关系、优先级排序 |
| `agent-architecture` | 系统架构、组件划分，输出 Mermaid 架构图 |
| `agent-tech-selection` | 候选技术评估（按功能满足度30%/团队熟悉度25%/社区活跃度15%/性能15%/学习成本10%/维护成本5%打分）、推荐方案 |
| `agent-data-model` | 核心数据模型，输出 Mermaid ER 图和数据流 |
| `agent-interface-design` | 内部/外部接口规范定义 |
| `agent-risk-analysis` | 风险矩阵（技术/性能/安全三维）+ 应对策略 |

**所有 6 个 sub-agent 并发执行，互不依赖。调研结果汇总到 Step 4。**

> **禁止重复造轮子检查**：每个 sub-agent 必须先检查 `research/` 目录是否有相关调研报告，复用已有结论。

### Step 4: 汇总与文档生成

Spawn 一个 sub-agent（`doc-writer`）：

- 整合 Step 1 和 Step 2 的所有结果
- 按以下结构填充 `P3-技术方案.md`：

| 章节 | 内容 |
|------|------|
| 一、方案概述 | 设计目标、核心原则 |
| 二、系统架构 | Mermaid 架构图、目录结构 |
| 三、功能模块设计 | 模块总览、详细设计 |
| 四、数据模型 | Mermaid ER 图、数据流 |
| 五、接口设计 | 内部接口、外部接口 |
| 六、风险分析与应对 | 风险项、应对策略 |
| 七、实施计划 | 阶段划分、依赖关系 |
| 八、参考资料 | 相关文档链接 |

- 写入文件到 `docs/迭代/{需求名称}/P3-技术方案.md`

### Step 5: 返回摘要

本 Skill 返回标准格式摘要给主智能体。

---

## 质量检查清单

- [ ] 架构图使用 Mermaid 格式（非 ASCII 图）
- [ ] 所有功能需求都有对应的技术方案
- [ ] 非功能需求（性能、安全等）有解决方案
- [ ] 技术选型有明确的打分和理由
- [ ] 风险分析覆盖技术/性能/安全三个维度
- [ ] 文档路径正确
- [ ] 所有工作由 sub-agent 完成（主智能体零直接操作）
- [ ] **必须使用 `ideal-deep-research` 进行过技术调研**
- [ ] **必须引用调研报告结论，不能凭空设计**
- [ ] **必须说明为何不直接复用现有开源项目/SDK**

---

## 返回格式

```markdown
## P3 技术方案 — 执行摘要

### 产物
- 调研报告：docs/迭代/{需求名称}/research/P3-技术调研_{timestamp}.md
- 技术方案：docs/迭代/{需求名称}/P3-技术方案.md

### 调研依据
- 已调研 {N} 个技术方向
- 引用开源项目/SDK：{列表}
- 决定自研的原因：{理由}

### 关键决策
1. {决策1} — {理由}（基于调研结论）
2. {决策2} — {理由}（基于调研结论）

### 风险提示
- {风险1}：{应对措施}
```
