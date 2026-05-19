---
需求名称: CC-Workflow 自动化工作流平台
关联方案: P3-技术方案.md
创建时间: 2026-02-18
当前阶段: P5
---

# P5-编码计划：CC-Workflow 自动化工作流平台

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans

**Goal:** 实现 CC-Workflow 自动化工作流平台的 7 个待开发 Skills，完成文档驱动的 15 阶段流程自动化系统。

**Architecture:** 采用 Superpowers 模式，每个 Skill 包含 SKILL.md（核心指令）、references/（模板和示例）、scripts/（辅助脚本）。系统通过 Markdown 文档管理流程状态，Claude Code 通过 skills 执行各阶段任务。

**Tech Stack:** Markdown, Claude Code Skills, Git, Obsidian, Gitea

---

## 模块总览

| 模块 | 任务数 | 优先级 | 说明 |
|------|--------|--------|------|
| M1: ideal-dev-solution | 6 | P0 | P3 技术方案生成 |
| M2: ideal-dev-plan | 6 | P0 | P5 编码计划生成 |
| M3: ideal-test-case | 6 | P0 | P7 测试用例生成 |
| M4: ideal-dev-exec | 7 | P0 | P9 开发执行 |
| M5: ideal-test-exec | 6 | P0 | P11 测试执行 |
| M6: ideal-wiki | 6 | P0 | P13 维基更新 |
| M7: ideal-flow-control | 6 | P1 | 流程状态管理 |

**总任务数：43 个原子任务**（含 7 个最佳实践调研任务）

---

## 最佳实践调研资源

每个模块开发前，需先调研以下资源的相似 skill：

### Superpowers Skills（主要参考）

| Skill | 用途 | 参考模块 |
|-------|------|----------|
| `brainstorming` | 苏格拉底式需求收集 | M1, M2, M3 |
| `writing-plans` | 编码计划生成 | M2 |
| `executing-plans` | 计划执行 | M4 |
| `subagent-driven-development` | 子代理开发 | M4 |
| `test-driven-development` | TDD 流程 | M4, M5 |
| `writing-skills` | Skill 编写规范 | 所有模块 |
| `verification-before-completion` | 完成验证 | 所有模块 |

**Superpowers GitHub**: https://github.com/obra/Superpowers

### Anthropic/Vercel 官方 Skills

| Skill | 用途 | 参考模块 |
|-------|------|----------|
| `doc-coauthoring` | 文档协作 | M1, M6 |
| `frontend-design` | 前端设计 | 代码生成参考 |
| `writing-plans` | 计划编写 | M2 |
| `systematic-debugging` | 系统化调试 | M5 |

### 调研方法

每个模块的第一个任务（Mx-0）为最佳实践调研任务，包含：

1. **读取相似 skill 的 SKILL.md**
   - 理解触发条件设计
   - 学习工作流结构
   - 提取可复用模式

2. **分析 skill 架构**
   - 目录结构
   - 模板设计
   - 脚本组织

3. **记录最佳实践**
   - 输出调研报告到 `references/research.md`
   - 标注可复用的模式
   - 标注需要定制的部分

---

## M1: ideal-dev-solution（P3 技术方案生成）

### 任务 M1-0: 最佳实践调研

**目标**：调研 Superpowers 和官方相似 skill 的最佳实践

**调研对象**：
- Superpowers `brainstorming` skill - 苏格拉底式对话收集需求
- Superpowers `writing-skills` skill - Skill 编写规范
- Anthropic `doc-coauthoring` skill - 文档协作模式

**步骤**：
1. [ ] 读取 Superpowers `brainstorming/SKILL.md`，理解工作流设计
2. [ ] 读取 Superpowers `writing-skills/SKILL.md`，学习 skill 编写规范
3. [ ] 搜索并阅读 Anthropic 官方文档相关 skill
4. [ ] 记录可复用的模式（触发条件、工作流、模板设计）
5. [ ] 输出调研报告 `references/research.md`

**验证标准**：
- 调研报告包含至少 3 个可复用模式
- 包含触发条件设计建议
- 包含工作流结构建议

---

### 任务 M1-1: 创建 Skill 目录结构

**目标**：建立 ideal-dev-solution skill 的基础目录结构

**步骤**：
1. [ ] 创建目录 `.claude/skills/ideal-dev-solution/`
2. [ ] 创建子目录 `references/templates/`
3. [ ] 创建子目录 `references/examples/`
4. [ ] 创建子目录 `scripts/`（预留）
5. [ ] 验证目录结构正确

**验证标准**：
```bash
ls -la .claude/skills/ideal-dev-solution/
# 应显示: SKILL.md(待创建), references/, scripts/
```

---

### 任务 M1-2: 编写技术方案模板

**目标**：创建 P3-技术方案.md 的标准模板

**步骤**：
1. [ ] 创建文件 `references/templates/solution-template.md`
2. [ ] 定义文档头部元数据（需求名称、关联需求、创建时间、当前阶段）
3. [ ] 定义章节结构：方案概述、系统架构、15阶段流程设计、Skills设计、数据模型、接口设计、风险分析、实施计划、参考资料
4. [ ] 添加占位符说明
5. [ ] 验证模板格式正确

**验证标准**：
- 模板包含所有必要章节
- 占位符格式统一（使用 `{placeholder}` 格式）
- Markdown 格式正确

---

### 任务 M1-3: 编写示例文档

**目标**：创建技术方案示例，供 skill 参考

**步骤**：
1. [ ] 创建文件 `references/examples/example-solution.md`
2. [ ] 基于当前项目的 P3-技术方案.md 作为示例
3. [ ] 确保示例涵盖所有章节
4. [ ] 添加注释说明各章节写作要点
5. [ ] 验证示例完整性

**验证标准**：
- 示例文档结构完整
- 包含架构图（ASCII 或 Mermaid）
- 包含技术选型表格

---

### 任务 M1-4: 编写 SKILL.md 核心指令

**目标**：编写 ideal-dev-solution 的核心 skill 文件

**步骤**：
1. [ ] 创建文件 `SKILL.md`
2. [ ] 定义 skill 描述和触发条件
3. [ ] 定义输入输出规范
4. [ ] 编写工作流程（读取需求 → 分析功能 → 设计架构 → 确定技术选型 → 生成方案）
5. [ ] 添加注意事项和最佳实践

**验证标准**：
- SKILL.md 格式符合 Superpowers 规范
- 包含清晰的触发条件
- 工作流程步骤明确

---

### 任务 M1-5: 集成测试

**目标**：验证 ideal-dev-solution skill 能正确生成技术方案

**步骤**：
1. [ ] 准备测试需求文档（使用现有的 P1-需求文档.md）
2. [ ] 调用 skill 生成技术方案
3. [ ] 验证输出文档包含所有必要章节
4. [ ] 验证技术选型合理
5. [ ] 记录问题和改进点

**验证标准**：
- 生成的技术方案格式正确
- 包含架构设计、技术选型、风险分析
- 文档路径正确（`docs/迭代/{需求名称}/P3-技术方案.md`）

---

## M2: ideal-dev-plan（P5 编码计划生成）

### 任务 M2-0: 最佳实践调研

**目标**：调研 Superpowers writing-plans skill 的最佳实践

**调研对象**：
- Superpowers `writing-plans` skill - 编码计划生成（核心参考）
- Superpowers `executing-plans` skill - 计划执行（理解计划格式要求）
- Superpowers `subagent-driven-development` skill - 子代理执行（理解任务粒度）

**步骤**：
1. [ ] 深度阅读 `writing-plans/SKILL.md`，理解计划生成流程
2. [ ] 分析计划模板格式（目标、架构、技术栈、任务分解）
3. [ ] 理解任务粒度控制（2-5 分钟原子任务）
4. [ ] 学习 TDD 任务组织方式
5. [ ] 输出调研报告 `references/research.md`

**验证标准**：
- 调研报告包含计划模板格式分析
- 包含任务粒度控制规范
- 包含 TDD 任务组织模式

---

### 任务 M2-1: 创建 Skill 目录结构

**目标**：建立 ideal-dev-plan skill 的基础目录结构

**步骤**：
1. [ ] 创建目录 `.claude/skills/ideal-dev-plan/`
2. [ ] 创建子目录 `references/templates/`
3. [ ] 创建子目录 `references/examples/`
4. [ ] 创建子目录 `scripts/`
5. [ ] 验证目录结构正确

**验证标准**：
```bash
ls -la .claude/skills/ideal-dev-plan/
# 应显示: SKILL.md(待创建), references/, scripts/
```

---

### 任务 M2-2: 编写编码计划模板

**目标**：创建 P5-编码计划.md 的标准模板

**步骤**：
1. [ ] 创建文件 `references/templates/plan-template.md`
2. [ ] 定义文档头部元数据
3. [ ] 定义模块总览表（模块名、任务数、优先级、说明）
4. [ ] 定义任务格式（目标、步骤、验证标准）
5. [ ] 添加 TDD 任务组织规范

**验证标准**：
- 任务格式包含：目标、步骤（TDD模式）、验证标准
- 每个任务粒度为 2-5 分钟
- 包含模块依赖关系

---

### 任务 M2-3: 编写示例文档

**目标**：创建编码计划示例

**步骤**：
1. [ ] 创建文件 `references/examples/example-plan.md`
2. [ ] 基于 Superpowers writing-plans 格式
3. [ ] 包含多模块、多任务的完整示例
4. [ ] 展示 TDD 任务分解方式
5. [ ] 验证示例完整性

**验证标准**：
- 示例包含至少 2 个模块
- 每个模块至少 3 个任务
- 任务步骤遵循 RED-GREEN-REFACTOR 模式

---

### 任务 M2-4: 编写 SKILL.md 核心指令

**目标**：编写 ideal-dev-plan 的核心 skill 文件

**步骤**：
1. [ ] 创建文件 `SKILL.md`
2. [ ] 定义 skill 描述和触发条件
3. [ ] 定义输入输出规范（输入：P3-技术方案.md，输出：P5-编码计划.md）
4. [ ] 编写任务分解流程（读取方案 → 识别模块 → 分解任务 → 组织 TDD 步骤）
5. [ ] 添加任务粒度控制规范

**验证标准**：
- 任务分解遵循 TDD 模式
- 每个任务包含验证标准
- 包含模块依赖处理逻辑

---

### 任务 M2-5: 集成测试

**目标**：验证 ideal-dev-plan skill 能正确生成编码计划

**步骤**：
1. [ ] 准备测试技术方案文档
2. [ ] 调用 skill 生成编码计划
3. [ ] 验证任务分解合理
4. [ ] 验证 TDD 步骤完整
5. [ ] 记录问题和改进点

**验证标准**：
- 生成的编码计划格式正确
- 任务粒度合理（2-5 分钟）
- 包含验证标准

---

## M3: ideal-test-case（P7 测试用例生成）

### 任务 M3-0: 最佳实践调研

**目标**：调研测试用例生成相关的最佳实践

**调研对象**：
- Superpowers `test-driven-development` skill - TDD 流程
- Superpowers `brainstorming` skill - 需求收集模式
- 业界测试用例编写规范

**步骤**：
1. [ ] 读取 `test-driven-development/SKILL.md`，理解测试优先原则
2. [ ] 分析验收标准提取方法
3. [ ] 调研测试用例分类方式（功能/边界/异常）
4. [ ] 学习测试覆盖率计算方法
5. [ ] 输出调研报告 `references/research.md`

**验证标准**：
- 调研报告包含测试用例格式规范
- 包含三种测试类型的定义
- 包含覆盖率计算方法

---

### 任务 M3-1: 创建 Skill 目录结构

**目标**：建立 ideal-test-case skill 的基础目录结构

**步骤**：
1. [ ] 创建目录 `.claude/skills/ideal-test-case/`
2. [ ] 创建子目录 `references/templates/`
3. [ ] 创建子目录 `references/examples/`
4. [ ] 创建子目录 `scripts/`
5. [ ] 验证目录结构正确

**验证标准**：
```bash
ls -la .claude/skills/ideal-test-case/
# 应显示: SKILL.md(待创建), references/, scripts/
```

---

### 任务 M3-2: 编写测试用例模板

**目标**：创建 P7-测试用例.md 的标准模板

**步骤**：
1. [ ] 创建文件 `references/templates/test-case-template.md`
2. [ ] 定义文档头部元数据
3. [ ] 定义测试用例格式（编号、名称、前置条件、步骤、预期结果、优先级）
4. [ ] 定义测试分类（功能测试、边界测试、异常测试）
5. [ ] 添加覆盖率统计模板

**验证标准**：
- 测试用例格式完整
- 包含三种测试类型分类
- 包含优先级定义（P0/P1/P2）

---

### 任务 M3-3: 编写示例文档

**目标**：创建测试用例示例

**步骤**：
1. [ ] 创建文件 `references/examples/example-test-case.md`
2. [ ] 包含功能测试用例示例
3. [ ] 包含边界条件测试用例示例
4. [ ] 包含异常场景测试用例示例
5. [ ] 验证示例完整性

**验证标准**：
- 示例涵盖三种测试类型
- 每个用例包含完整的步骤和预期结果
- 包含覆盖率统计示例

---

### 任务 M3-4: 编写 SKILL.md 核心指令

**目标**：编写 ideal-test-case 的核心 skill 文件

**步骤**：
1. [ ] 创建文件 `SKILL.md`
2. [ ] 定义 skill 描述和触发条件
3. [ ] 定义输入输出规范（输入：P1+P5 文档，输出：P7-测试用例.md）
4. [ ] 编写用例生成流程（提取功能点 → 生成功能用例 → 生成边界用例 → 生成异常用例）
5. [ ] 添加覆盖率保障规范

**验证标准**：
- 能从需求文档提取验收标准
- 能从编码计划识别测试点
- 包含三种测试类型的生成规则

---

### 任务 M3-5: 集成测试

**目标**：验证 ideal-test-case skill 能正确生成测试用例

**步骤**：
1. [ ] 准备测试需求文档和编码计划
2. [ ] 调用 skill 生成测试用例
3. [ ] 验证用例覆盖所有功能点
4. [ ] 验证包含边界和异常用例
5. [ ] 记录问题和改进点

**验证标准**：
- 测试用例覆盖需求中的所有验收标准
- 包含边界条件测试
- 包含异常场景测试

---

## M4: ideal-dev-exec（P9 开发执行）

### 任务 M4-0: 最佳实践调研

**目标**：调研开发执行相关的最佳实践

**调研对象**：
- Superpowers `executing-plans` skill - 计划执行（核心参考）
- Superpowers `subagent-driven-development` skill - 子代理驱动开发
- Superpowers `test-driven-development` skill - TDD 强制规则
- Superpowers `using-git-worktrees` skill - Git 分支管理
- Superpowers `finishing-a-development-branch` skill - 分支完成流程

**步骤**：
1. [ ] 深度阅读 `executing-plans/SKILL.md`，理解执行流程
2. [ ] 分析 `subagent-driven-development` 的任务派遣模式
3. [ ] 学习 TDD 强制规则（RED-GREEN-REFACTOR）
4. [ ] 理解 Git worktree 和分支管理策略
5. [ ] 输出调研报告 `references/research.md`

**验证标准**：
- 调研报告包含执行流程设计
- 包含 TDD 强制规则设计
- 包含 Git 分支管理策略

---

### 任务 M4-1: 创建 Skill 目录结构

**目标**：建立 ideal-dev-exec skill 的基础目录结构

**步骤**：
1. [ ] 创建目录 `.claude/skills/ideal-dev-exec/`
2. [ ] 创建子目录 `references/`
3. [ ] 创建子目录 `scripts/`
4. [ ] 验证目录结构正确

**验证标准**：
```bash
ls -la .claude/skills/ideal-dev-exec/
# 应显示: SKILL.md(待创建), references/, scripts/
```

---

### 任务 M4-2: 编写执行策略文档

**目标**：定义开发执行的标准策略

**步骤**：
1. [ ] 创建文件 `references/execution-strategy.md`
2. [ ] 定义 TDD 执行流程（RED-GREEN-REFACTOR）
3. [ ] 定义 Git 分支策略
4. [ ] 定义 MR 创建规范
5. [ ] 定义代码提交规范

**验证标准**：
- TDD 流程描述清晰
- 分支命名规范明确
- MR 模板完整

---

### 任务 M4-3: 编写 SKILL.md 核心指令

**目标**：编写 ideal-dev-exec 的核心 skill 文件

**步骤**：
1. [ ] 创建文件 `SKILL.md`
2. [ ] 定义 skill 描述和触发条件
3. [ ] 定义输入输出规范（输入：P5-编码计划.md，输出：代码 + MR）
4. [ ] 编写执行流程（读取计划 → 创建分支 → 逐任务执行 → 创建 MR）
5. [ ] 添加 TDD 强制检查规则

**验证标准**：
- 包含 TDD 强制规则（无测试不写代码）
- 包含分支管理逻辑
- 包含 MR 创建流程

---

### 任务 M4-4: 编写 Git 操作脚本

**目标**：创建辅助 Git 操作的脚本

**步骤**：
1. [ ] 创建文件 `scripts/git-helper.sh`
2. [ ] 实现分支创建函数
3. [ ] 实现提交信息生成函数
4. [ ] 实现 MR 创建函数（Gitea API）
5. [ ] 添加错误处理

**验证标准**：
```bash
./scripts/git-helper.sh create-branch "feature/test"
# 应成功创建并切换到新分支
```

---

### 任务 M4-5: 编写进度跟踪文档

**目标**：定义开发执行过程中的进度跟踪机制

**步骤**：
1. [ ] 创建文件 `references/progress-tracking.md`
2. [ ] 定义任务状态更新机制
3. [ ] 定义执行报告格式
4. [ ] 定义异常处理流程
5. [ ] 验证文档完整性

**验证标准**：
- 包含任务状态模板
- 包含执行报告模板
- 包含异常处理流程图

---

### 任务 M4-6: 集成测试

**目标**：验证 ideal-dev-exec skill 能正确执行开发任务

**步骤**：
1. [ ] 准备测试编码计划
2. [ ] 调用 skill 执行开发
3. [ ] 验证代码生成正确
4. [ ] 验证测试通过
5. [ ] 验证 MR 创建成功

**验证标准**：
- 代码符合 TDD 规范
- 测试通过
- MR 创建成功

---

## M5: ideal-test-exec（P11 测试执行）

### 任务 M5-0: 最佳实践调研

**目标**：调研测试执行相关的最佳实践

**调研对象**：
- Superpowers `test-driven-development` skill - 测试执行验证
- Superpowers `verification-before-completion` skill - 完成验证
- Superpowers `systematic-debugging` skill - 问题诊断

**步骤**：
1. [ ] 读取 `test-driven-development/SKILL.md` 的验证部分
2. [ ] 分析 `verification-before-completion` 的验证规则
3. [ ] 学习测试报告格式设计
4. [ ] 理解缺陷记录规范
5. [ ] 输出调研报告 `references/research.md`

**验证标准**：
- 调研报告包含测试执行流程
- 包含测试报告格式规范
- 包含缺陷记录模板

---

### 任务 M5-1: 创建 Skill 目录结构

**目标**：建立 ideal-test-exec skill 的基础目录结构

**步骤**：
1. [ ] 创建目录 `.claude/skills/ideal-test-exec/`
2. [ ] 创建子目录 `references/templates/`
3. [ ] 创建子目录 `scripts/`
4. [ ] 验证目录结构正确

**验证标准**：
```bash
ls -la .claude/skills/ideal-test-exec/
# 应显示: SKILL.md(待创建), references/, scripts/
```

---

### 任务 M5-2: 编写测试报告模板

**目标**：创建 P11-测试报告.md 的标准模板

**步骤**：
1. [ ] 创建文件 `references/templates/test-report-template.md`
2. [ ] 定义文档头部元数据
3. [ ] 定义测试执行汇总（总用例数、通过数、失败数、跳过数）
4. [ ] 定义用例执行结果表
5. [ ] 定义缺陷记录格式

**验证标准**：
- 包含测试汇总统计
- 包含用例执行结果表
- 包含缺陷记录模板

---

### 任务 M5-3: 编写 SKILL.md 核心指令

**目标**：编写 ideal-test-exec 的核心 skill 文件

**步骤**：
1. [ ] 创建文件 `SKILL.md`
2. [ ] 定义 skill 描述和触发条件
3. [ ] 定义输入输出规范（输入：P7-测试用例.md，输出：P11-测试报告.md）
4. [ ] 编写执行流程（读取用例 → 执行测试 → 收集结果 → 生成报告）
5. [ ] 添加手动测试指导

**验证标准**：
- 能解析测试用例文档
- 能指导手动测试执行
- 能生成标准化报告

---

### 任务 M5-4: 编写测试执行脚本

**目标**：创建辅助测试执行的脚本

**步骤**：
1. [ ] 创建文件 `scripts/test-runner.sh`
2. [ ] 实现自动化测试执行函数
3. [ ] 实现结果收集函数
4. [ ] 实现报告生成函数
5. [ ] 添加错误处理

**验证标准**：
```bash
./scripts/test-runner.sh run-all
# 应执行所有测试并输出结果
```

---

### 任务 M5-5: 集成测试

**目标**：验证 ideal-test-exec skill 能正确执行测试

**步骤**：
1. [ ] 准备测试用例文档
2. [ ] 调用 skill 执行测试
3. [ ] 验证测试报告生成正确
4. [ ] 验证缺陷记录完整
5. [ ] 记录问题和改进点

**验证标准**：
- 测试报告格式正确
- 包含所有用例的执行结果
- 缺陷记录完整

---

## M6: ideal-wiki（P13 维基更新）

### 任务 M6-0: 最佳实践调研

**目标**：调研文档生成相关的最佳实践

**调研对象**：
- Anthropic `doc-coauthoring` skill - 文档协作
- Superpowers `writing-skills` skill - 文档编写规范
- 业界 API 文档规范（OpenAPI/Swagger）

**步骤**：
1. [ ] 调研 `doc-coauthoring` 的工作流设计
2. [ ] 分析用户文档、开发文档、接口文档的结构规范
3. [ ] 学习从代码提取接口信息的方法
4. [ ] 调研文档质量检查规则
5. [ ] 输出调研报告 `references/research.md`

**验证标准**：
- 调研报告包含三种文档类型结构
- 包含代码分析提取方法
- 包含文档质量检查规则

---

### 任务 M6-1: 创建 Skill 目录结构

**目标**：建立 ideal-wiki skill 的基础目录结构

**步骤**：
1. [ ] 创建目录 `.claude/skills/ideal-wiki/`
2. [ ] 创建子目录 `references/templates/`
3. [ ] 创建子目录 `references/examples/`
4. [ ] 验证目录结构正确

**验证标准**：
```bash
ls -la .claude/skills/ideal-wiki/
# 应显示: SKILL.md(待创建), references/
```

---

### 任务 M6-2: 编写维基文档模板

**目标**：创建三种维基文档的标准模板

**步骤**：
1. [ ] 创建用户文档模板 `references/templates/user-doc-template.md`
2. [ ] 创建开发文档模板 `references/templates/dev-doc-template.md`
3. [ ] 创建接口文档模板 `references/templates/api-doc-template.md`
4. [ ] 定义各模板的章节结构
5. [ ] 验证模板格式正确

**验证标准**：
- 用户文档包含：功能介绍、使用指南、常见问题
- 开发文档包含：架构说明、环境配置、部署指南
- 接口文档包含：API 列表、请求/响应格式、错误码

---

### 任务 M6-3: 编写示例文档

**目标**：创建维基文档示例

**步骤**：
1. [ ] 创建用户文档示例 `references/examples/user-doc-example.md`
2. [ ] 创建开发文档示例 `references/examples/dev-doc-example.md`
3. [ ] 创建接口文档示例 `references/examples/api-doc-example.md`
4. [ ] 确保示例完整且可参考
5. [ ] 验证示例质量

**验证标准**：
- 示例文档结构完整
- 内容清晰易懂
- 格式规范

---

### 任务 M6-4: 编写 SKILL.md 核心指令

**目标**：编写 ideal-wiki 的核心 skill 文件

**步骤**：
1. [ ] 创建文件 `SKILL.md`
2. [ ] 定义 skill 描述和触发条件
3. [ ] 定义输入输出规范（输入：代码 + P1 文档，输出：Wiki 文档）
4. [ ] 编写文档生成流程（分析代码 → 生成用户文档 → 生成开发文档 → 生成接口文档）
5. [ ] 添加文档质量检查规则

**验证标准**：
- 能从代码提取接口信息
- 能从需求提取功能描述
- 包含文档质量检查规则

---

### 任务 M6-5: 集成测试

**目标**：验证 ideal-wiki skill 能正确生成维基文档

**步骤**：
1. [ ] 准备测试代码和需求文档
2. [ ] 调用 skill 生成维基文档
3. [ ] 验证用户文档生成正确
4. [ ] 验证开发文档生成正确
5. [ ] 验证接口文档生成正确

**验证标准**：
- 三种文档都已生成
- 文档路径正确（`docs/Wiki/{类型}/`）
- 文档内容完整

---

## M7: ideal-flow-control（流程状态管理）

### 任务 M7-0: 最佳实践调研

**目标**：调研流程控制相关的最佳实践

**调研对象**：
- Superpowers `using-superpowers` skill - Skill 导航和发现
- Superpowers `verification-before-completion` skill - 验证规则
- 状态机设计模式

**步骤**：
1. [ ] 分析 `using-superpowers` 的 skill 发现机制
2. [ ] 学习阶段前置条件验证方法
3. [ ] 调研状态机设计模式（状态定义、转换规则）
4. [ ] 理解触发条件映射设计
5. [ ] 输出调研报告 `references/research.md`

**验证标准**：
- 调研报告包含状态机设计
- 包含阶段转换规则
- 包含触发条件映射

---

### 任务 M7-1: 创建 Skill 目录结构

**目标**：建立 ideal-flow-control skill 的基础目录结构

**步骤**：
1. [ ] 创建目录 `.claude/skills/ideal-flow-control/`
2. [ ] 创建子目录 `references/`
3. [ ] 创建子目录 `scripts/`
4. [ ] 验证目录结构正确

**验证标准**：
```bash
ls -la .claude/skills/ideal-flow-control/
# 应显示: SKILL.md(待创建), references/, scripts/
```

---

### 任务 M7-2: 编写流程状态规范

**目标**：定义流程状态管理的标准规范

**步骤**：
1. [ ] 创建文件 `references/flow-state-spec.md`
2. [ ] 定义流程状态文件格式
3. [ ] 定义阶段状态值（pending/in_progress/completed/blocked/revision）
4. [ ] 定义阶段转换规则
5. [ ] 定义触发条件映射

**验证标准**：
- 状态值定义完整
- 阶段转换规则清晰
- 触发条件映射完整

---

### 任务 M7-3: 编写 SKILL.md 核心指令

**目标**：编写 ideal-flow-control 的核心 skill 文件

**步骤**：
1. [ ] 创建文件 `SKILL.md`
2. [ ] 定义 skill 描述和触发条件
3. [ ] 定义状态读取/更新规范
4. [ ] 编写阶段流转流程（读取状态 → 验证前置 → 调用 skill → 更新状态）
5. [ ] 添加状态验证规则

**验证标准**：
- 能正确解析流程状态文件
- 能验证阶段前置条件
- 能正确更新状态

---

### 任务 M7-4: 编写状态管理脚本

**目标**：创建辅助状态管理的脚本

**步骤**：
1. [ ] 创建文件 `scripts/flow-state.py`
2. [ ] 实现状态读取函数
3. [ ] 实现状态更新函数
4. [ ] 实现阶段验证函数
5. [ ] 添加错误处理

**验证标准**：
```bash
python scripts/flow-state.py get-current-phase "docs/迭代/测试需求/流程状态.md"
# 应返回当前阶段
```

---

### 任务 M7-5: 集成测试

**目标**：验证 ideal-flow-control skill 能正确管理流程状态

**步骤**：
1. [ ] 准备测试流程状态文件
2. [ ] 调用 skill 读取状态
3. [ ] 调用 skill 更新状态
4. [ ] 验证状态转换正确
5. [ ] 记录问题和改进点

**验证标准**：
- 能正确读取当前阶段
- 能正确更新状态
- 能验证前置条件

---

## 执行顺序建议

```
┌─────────────────────────────────────────────────────────────────┐
│                        执行顺序                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  批次 1: 基础 Skills（可并行）                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  M1: ideal-dev-solution  ─┐                             │    │
│  │  M2: ideal-dev-plan      ─┼─▶ 并行执行                   │    │
│  │  M7: ideal-flow-control  ─┘                             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  批次 2: 生成 Skills（依赖批次1）                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  M3: ideal-test-case   ─┐                               │    │
│  │  M6: ideal-wiki        ─┼─▶ 并行执行                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  批次 3: 执行 Skills（依赖批次2）                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  M4: ideal-dev-exec                                      │    │
│  │  M5: ideal-test-exec                                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 验证计划

### 完整流程验证

完成所有 Skills 开发后，选择"用户登录"功能进行完整流程验证：

| 步骤 | 阶段 | Skill | 预期输出 |
|------|------|-------|----------|
| 1 | P1 | ideal-requirement | 需求文档 |
| 2 | P2 | 人工评审 | 评审通过 |
| 3 | P3 | ideal-dev-solution | 技术方案 |
| 4 | P4 | 人工评审 | 评审通过 |
| 5 | P5 | ideal-dev-plan | 编码计划 |
| 6 | P6 | 人工评审 | 评审通过 |
| 7 | P7 | ideal-test-case | 测试用例 |
| 8 | P8 | 人工评审 | 评审通过 |
| 9 | P9 | ideal-dev-exec | 代码 + MR |
| 10 | P10 | 人工评审 | Approve |
| 11 | P11 | ideal-test-exec | 测试报告 |
| 12 | P12 | 人工评审 | 通过 |
| 13 | P13 | ideal-wiki | Wiki 文档 |
| 14 | P14 | 人工评审 | 发布许可 |
| 15 | P15 | CI/CD | 成果提交 |

### 验收标准

- [ ] 15 阶段流程完整跑通
- [ ] 各阶段文档格式规范
- [ ] 生成的代码通过测试
- [ ] 流程状态正确流转
- [ ] Wiki 文档完整生成

---

*文档版本: v1.0*
*创建时间: 2026-02-18*
*作者: Claude Code*
