---
name: ideal-wiki
description: Use when P12 test review is completed and wiki documentation generation is needed. Creates high-quality wiki documentation based on project context.
agents: [tech-writer, dev, qa]
---

# ideal-wiki（P13 维基更新）

## 角色定位

Phase Skill — **执行协调者**。

职责：
1. 加载所需上下文（项目代码、配置、现有文档）
2. 调度子智能体设计大纲和撰写内容
3. 将文档写入文件系统
4. 返回执行摘要

**不负责**：更新 flow state、验证前置条件，协调评审。

---

## 输入

| 来源 | 内容 |
|------|------|
| 项目代码 | 核心代码文件和目录结构 |
| 项目配置 | package.json、技术栈信息 |
| 现有文档 | docs/ Wiki/ 等已有文档 |
| P1 需求文档 | 目标读者、功能模块 |

## 输出

| 文件 | 路径 |
|------|------|
| docs/Wiki/wiki-outline.md | 大纲文件 |
| docs/Wiki/wiki-improvements.md | 改进项追踪 |
| docs/Wiki/{类别}/ | 按读者群体划分的文档集 |

---

## 子智能体调度

| 调用时机 | 子智能体 | 任务 |
|----------|----------|------|
| 大纲设计 | `tech-writer` | 分析项目复杂度、规划文档结构 |
| 内容撰写 | `tech-writer` | 按大纲逐篇撰写，遵循正式技术风格 |
| 一致性审查 | `dev` | 检查文档与代码一致性 |
| 角色模拟审查 | `qa` | 模拟新用户和开发者视角 |

---

## 执行流程

```
Step 1: 加载上下文
  ├─ 分析项目代码结构和配置
  └─ 读取 P1 需求（确定目标读者）

Step 2: 大纲设计
  └─ Task(tech-writer) → 生成 docs/Wiki/wiki-outline.md
      └─ **暂停，等待用户确认大纲**

Step 3: 内容撰写（需大纲确认后）
  └─ Task(tech-writer) → 按确认的大纲逐篇撰写
      └─ **第一篇完成后，暂停等待用户确认风格**

Step 4: 质量审查
  ├─ Task(dev) → 内容一致性审查
  └─ Task(qa) → 角色模拟审查

Step 5: 写入产物
Step 6: 返回摘要
```

---

## 质量检查清单

- [ ] 所有文档使用 Mermaid（非 ASCII 图）
- [ ] 每篇文档有正确的 Frontmatter
- [ ] 内容使用正式技术风格（禁止模糊描述）
- [ ] 流程说明完整（前置 → 步骤 → 预期 → 异常）
- [ ] 代码示例可执行
- [ ] 目录结构符合在线文档标准

---

## 返回格式

```markdown
## P13 Wiki 文档 — 执行摘要

### 产物
- 大纲：docs/Wiki/wiki-outline.md
- 文档数：{N} 篇
- 文档集：{类别列表}

### 一致性检查
- 发现问题：{N} 个（P0/P1/P2 分布）

### 待处理
- {需要用户确认的事项}
```
