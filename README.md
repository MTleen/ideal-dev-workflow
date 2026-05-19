# ideal-dev-workflow

**15 阶段开发流程工作流 Marketplace** — 从需求到交付的完整开发链路

[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](https://github.com/MTleen/ideal-dev-workflow)
[![Skills](https://img.shields.io/badge/skills-14-green?style=flat-square)](./plugins/ideal-dev-workflow/skills)
[![Version](https://img.shields.io/badge/version-1.1.0-orange?style=flat-square)](./plugins/ideal-dev-workflow/.claude-plugin/plugin.json)

---

## 概览

ideal-dev-workflow 是一个 Claude Code Plugin Marketplace，提供 15 阶段严格有序的开发流程流水线，覆盖从需求编写到成果提交的完整链路。

包含 **1 个插件**、**14 个 Skill**。

## 快速开始

### 1. 添加 Marketplace

```bash
claude plugin marketplace add https://github.com/MTleen/ideal-dev-workflow
```

### 2. 安装插件

```bash
claude plugin install ideal-dev-workflow@ideal-dev-workflow
```

### 3. 调用 Skill

安装后 Skill 自动加载，通过斜杠命令调用：

```
/ideal-dev-workflow:ideal-init              # 项目初始化
/ideal-dev-workflow:ideal-requirement       # P1 需求编写
/ideal-dev-workflow:ideal-dev-solution      # P3 技术方案
/ideal-dev-workflow:ideal-dev-plan          # P5 编码计划
/ideal-dev-workflow:ideal-test-case         # P7 测试用例
/ideal-dev-workflow:ideal-dev-exec          # P9 开发执行
/ideal-dev-workflow:ideal-code-review       # P10 代码评审
/ideal-dev-workflow:ideal-test-exec         # P11 测试执行
/ideal-dev-workflow:ideal-wiki              # P13 维基更新
/ideal-dev-workflow:ideal-delivery          # P15 成果提交
/ideal-dev-workflow:ideal-flow-control      # 阶段流转控制
/ideal-dev-workflow:ideal-yolo              # YOLO 自动模式
/ideal-dev-workflow:ideal-debugging         # 系统调试
/ideal-dev-workflow:ideal-deep-research     # 深度调研
```

## 阶段流程

```
P1 需求编写 → P2 需求评审 → P3 技术方案 → P4 方案评审
→ P5 编码计划 → P6 计划评审 → P7 测试用例 → P8 用例评审
→ P9 开发执行 → P10 代码评审 → P11 测试执行 → P12 测试评审
→ P13 维基更新 → P14 维基评审 → P15 成果提交
```

偶数阶段（P2/P4/P6/P8/P10/P12/P14）为人工评审关卡。

## 插件清单

| 插件 | 版本 | 说明 | Skills |
|------|------|------|--------|
| [ideal-dev-workflow](./plugins/ideal-dev-workflow) | 1.1.0 | 15 阶段开发流程工作流 | 14 |

## Skill 列表

| Skill | 阶段 | 说明 |
|-------|------|------|
| ideal-init | — | 项目初始化与配置生成 |
| ideal-requirement | P1 | 需求文档编写（功能/Bug/重构） |
| ideal-dev-solution | P3 | 技术方案生成 |
| ideal-dev-plan | P5 | 编码计划与原子任务拆分 |
| ideal-test-case | P7 | 测试用例生成 |
| ideal-dev-exec | P9 | TDD 开发执行 |
| ideal-code-review | P10 | 两阶段代码评审（规格+质量） |
| ideal-test-exec | P11 | 测试执行与报告 |
| ideal-wiki | P13 | 维基文档生成 |
| ideal-delivery | P15 | 成果提交与交付 |
| ideal-flow-control | — | 阶段流转状态管理 |
| ideal-yolo | — | YOLO 自动模式（多视角评审） |
| ideal-debugging | — | 系统调试与根因分析 |
| ideal-deep-research | — | 企业级深度调研 |

## 目录结构

```
ideal-dev-workflow/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace 索引
├── plugins/
│   └── ideal-dev-workflow/       # 插件主体
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── skills/               # 14 个 Skill
│       ├── package.json
│       └── CHANGELOG.md
├── package.json
├── .gitignore
└── README.md
```

## License

MIT
