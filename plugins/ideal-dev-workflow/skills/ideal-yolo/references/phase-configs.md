# YOLO 模式阶段配置表

本文档定义 YOLO 模式下 P3-P14 阶段的完整配置，包括阶段类型、模型选择、输入输出文件、返回预算和依赖关系。

## 配置总览

| 阶段 | 名称 | 类型 | 模型 | 返回预算 | 依赖 |
|------|------|------|------|----------|------|
| P3 | 技术方案 | execution | opus | 3K | P2 |
| P4 | 方案评审 | review | sonnet | 2K | P3 |
| P5 | 计划生成 | execution | opus | 3K | P4 |
| P6 | 计划评审 | review | sonnet | 2K | P5 |
| P7 | 测试用例 | execution | sonnet | 3K | P6 |
| P8 | 用例评审 | review | sonnet | 2K | P7 |
| P9 | 开发执行 | execution | opus | 3K/故事 | P8 |
| P10 | 代码评审 | review | sonnet | 2K | P9 |
| P11 | 测试执行 | execution | sonnet | 3K | P10 |
| P12 | 测试评审 | review | sonnet | 2K | P11 |
| P13 | 维基更新 | execution | sonnet | 3K | P12 |
| P14 | 维基评审 | review | sonnet | 2K | P13 |

---

## 详细配置

### P3: 技术方案

```yaml
phase: P3
name: 技术方案
type: execution
model: opus
description: 根据需求文档生成技术方案

input_files:
  - P1-需求文档.md
  - .claude/project-config.md

output_files:
  - P3-技术方案.md

allowed_tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash

return_budget: 3K
depends_on: P2

agent: architect
skill: ideal-dev-solution

return_format:
  success: boolean
  phase: string
  output_files: string[]
  summary: string          # 50-100字概述
  key_decisions: string[]  # 关键技术决策
  risks: string[]          # 风险列表
  metrics:
    files_created: number
    files_modified: number
  error_message: string | null
```

### P4: 方案评审

```yaml
phase: P4
name: 方案评审
type: review
model: sonnet
description: 评审技术方案的质量和可行性

input_files:
  - P3-技术方案.md
  - P1-需求文档.md

output_files:
  - yolo-logs/review-P4.log

allowed_tools:
  - Read
  - Write

return_budget: 2K
depends_on: P3

review_criteria:
  - 需求覆盖完整性
  - 技术选型合理性
  - 架构设计清晰度
  - 风险识别充分性
  - 实施可行性

return_format:
  success: boolean
  phase: string
  review_passed: boolean
  review_score: number      # 0-100
  review_comments: string[]
  review_suggestions: string[]
  summary: string
  error_message: string | null
```

### P5: 计划生成

```yaml
phase: P5
name: 计划生成
type: execution
model: opus
description: 根据技术方案生成编码计划和故事文件

input_files:
  - P3-技术方案.md
  - P1-需求文档.md

output_files:
  - P5-编码计划.md
  - stories/index.md
  - stories/0XX-*.md       # 故事文件

allowed_tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash

return_budget: 3K
depends_on: P4

agent: architect
skill: ideal-dev-plan

return_format:
  success: boolean
  phase: string
  output_files: string[]
  summary: string
  key_decisions: string[]
  story_count: number       # 故事数量
  risks: string[]
  metrics:
    files_created: number
    files_modified: number
  error_message: string | null
```

### P6: 计划评审

```yaml
phase: P6
name: 计划评审
type: review
model: sonnet
description: 评审编码计划的合理性和完整性

input_files:
  - P5-编码计划.md
  - stories/index.md

output_files:
  - yolo-logs/review-P6.log

allowed_tools:
  - Read
  - Write

return_budget: 2K
depends_on: P5

review_criteria:
  - 任务拆分合理性
  - 依赖关系正确性
  - 估算合理性
  - 故事文件完整性

return_format:
  success: boolean
  phase: string
  review_passed: boolean
  review_score: number
  review_comments: string[]
  review_suggestions: string[]
  summary: string
  error_message: string | null
```

### P7: 测试用例

```yaml
phase: P7
name: 测试用例
type: execution
model: sonnet
description: 根据技术方案和编码计划生成测试用例

input_files:
  - P3-技术方案.md
  - P5-编码计划.md
  - P1-需求文档.md

output_files:
  - P7-测试用例.md

allowed_tools:
  - Read
  - Write
  - Glob
  - Grep

return_budget: 3K
depends_on: P6

agent: qa
skill: ideal-test-case

return_format:
  success: boolean
  phase: string
  output_files: string[]
  summary: string
  test_count: number        # 测试用例数量
  coverage_areas: string[]  # 覆盖的功能区域
  risks: string[]
  metrics:
    files_created: number
    files_modified: number
  error_message: string | null
```

### P8: 用例评审

```yaml
phase: P8
name: 用例评审
type: review
model: sonnet
description: 评审测试用例的覆盖度和质量

input_files:
  - P7-测试用例.md
  - P3-技术方案.md

output_files:
  - yolo-logs/review-P8.log

allowed_tools:
  - Read
  - Write

return_budget: 2K
depends_on: P7

review_criteria:
  - 功能覆盖完整性
  - 边界条件覆盖
  - 异常场景覆盖
  - 用例可执行性

return_format:
  success: boolean
  phase: string
  review_passed: boolean
  review_score: number
  review_comments: string[]
  review_suggestions: string[]
  summary: string
  error_message: string | null
```

### P9: 开发执行

```yaml
phase: P9
name: 开发执行
type: execution
model: opus
description: 按故事逐个执行开发任务（上下文隔离）

# P9 特殊处理：逐故事执行
execution_mode: story_by_story
story_context_isolation: true

input_files:
  # 动态加载：只加载当前故事文件
  - stories/current.md      # 当前执行的故事
  - P3-技术方案.md          # 参考方案
  - P5-编码计划.md          # 参考计划

output_files:
  # 由故事决定具体输出
  - src/**/*.py             # 源代码
  - tests/**/*.py           # 测试代码

allowed_tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash

return_budget: 3K           # 每故事 3K
depends_on: P8

agent: dev
skill: ideal-dev-exec

return_format:
  success: boolean
  phase: string
  story_id: string          # 当前故事 ID
  output_files: string[]
  summary: string
  key_changes: string[]     # 关键代码变更
  tests_passed: boolean
  risks: string[]
  metrics:
    files_created: number
    files_modified: number
    lines_added: number
    lines_removed: number
  error_message: string | null
```

### P10: 代码评审

```yaml
phase: P10
name: 代码评审
type: review
model: sonnet
description: 评审代码质量和规范性

input_files:
  # 动态获取 git diff
  - git-diff                 # 当前变更
  - P3-技术方案.md           # 参考方案

output_files:
  - yolo-logs/review-P10.log

allowed_tools:
  - Read
  - Write
  - Bash                    # 用于 git 命令

return_budget: 2K
depends_on: P9

review_criteria:
  - 代码规范遵循
  - 设计模式使用
  - 错误处理完整性
  - 测试覆盖充分性
  - 安全性考虑

return_format:
  success: boolean
  phase: string
  review_passed: boolean
  review_score: number
  review_comments: string[]
  review_suggestions: string[]
  summary: string
  error_message: string | null
```

### P11: 测试执行

```yaml
phase: P11
name: 测试执行
type: execution
model: sonnet
description: 执行测试用例并生成测试报告

input_files:
  - P7-测试用例.md
  - stories/index.md        # 了解已实现的功能

output_files:
  - P11-测试报告.md

allowed_tools:
  - Read
  - Write
  - Bash                    # 用于执行测试命令

return_budget: 3K
depends_on: P10

agent: qa
skill: ideal-test-exec

return_format:
  success: boolean
  phase: string
  output_files: string[]
  summary: string
  test_results:
    total: number
    passed: number
    failed: number
    skipped: number
    pass_rate: number       # 百分比
  risks: string[]
  metrics:
    files_created: number
    files_modified: number
  error_message: string | null
```

### P12: 测试评审

```yaml
phase: P12
name: 测试评审
type: review
model: sonnet
description: 评审测试结果的充分性

input_files:
  - P11-测试报告.md
  - P7-测试用例.md

output_files:
  - yolo-logs/review-P12.log

allowed_tools:
  - Read
  - Write

return_budget: 2K
depends_on: P11

review_criteria:
  - 测试通过率达标（>= 80%）
  - 失败用例分析充分
  - 回归测试覆盖
  - 性能测试结果

return_format:
  success: boolean
  phase: string
  review_passed: boolean
  review_score: number
  review_comments: string[]
  review_suggestions: string[]
  summary: string
  error_message: string | null
```

### P13: 维基更新

```yaml
phase: P13
name: 维基更新
type: execution
model: sonnet
description: 更新项目维基文档

input_files:
  - P1-需求文档.md
  - P3-技术方案.md
  - P11-测试报告.md
  - stories/index.md

output_files:
  - Wiki/**/*.md            # 维基文档

allowed_tools:
  - Read
  - Write
  - Glob
  - Grep

return_budget: 3K
depends_on: P12

agent: tech-writer
skill: ideal-wiki

return_format:
  success: boolean
  phase: string
  output_files: string[]
  summary: string
  wiki_sections_updated: string[]
  risks: string[]
  metrics:
    files_created: number
    files_modified: number
  error_message: string | null
```

### P14: 维基评审

```yaml
phase: P14
name: 维基评审
type: review
model: sonnet
description: 评审维基文档的完整性和准确性

input_files:
  - Wiki/**/*.md

output_files:
  - yolo-logs/review-P14.log

allowed_tools:
  - Read
  - Write
  - Glob

return_budget: 2K
depends_on: P13

review_criteria:
  - 文档完整性
  - 内容准确性
  - 结构清晰度
  - 示例充分性

return_format:
  success: boolean
  phase: string
  review_passed: boolean
  review_score: number
  review_comments: string[]
  review_suggestions: string[]
  summary: string
  error_message: string | null
```

---

## 执行顺序

```
P3 (技术方案) → P4 (方案评审) → P5 (计划生成) → P6 (计划评审)
    → P7 (测试用例) → P8 (用例评审) → P9 (开发执行) → P10 (代码评审)
    → P11 (测试执行) → P12 (测试评审) → P13 (维基更新) → P14 (维基评审)
```

## 模型选择策略

| 阶段类型 | 模型 | 理由 |
|----------|------|------|
| 执行阶段（关键） | opus | P3/P5/P9 需要高质量输出 |
| 执行阶段（常规） | sonnet | P7/P11/P13 成本效益更优 |
| 评审阶段 | sonnet | 评审任务相对简单 |

## 上下文预算

- 编排器自身：~10K tokens
- 各阶段摘要累计：~30K tokens（执行阶段 6 × 3K + 评审阶段 6 × 2K）
- 缓冲：~10K tokens
- **总计：< 50K tokens**

## P9 特殊处理

P9 阶段是上下文压力最大的阶段，需要特殊处理：

1. **逐故事执行**：每个故事一个独立 Task
2. **上下文隔离**：每个 Task 只加载当前故事文件
3. **状态追踪**：通过 stories/index.md 追踪执行进度
4. **依赖检查**：执行前检查故事依赖是否满足

```
P9 执行流程：
├── 读取 stories/index.md
├── 识别 pending 状态的故事
├── 检查依赖关系
├── 对每个可执行故事：
│   ├── 调用 Task（只加载当前故事）
│   ├── 解析结果
│   ├── 更新故事状态
│   └── 熔断检查
└── 所有故事完成后进入 P10
```

---

*文档版本: v1.0*
*创建时间: 2026-03-01*
