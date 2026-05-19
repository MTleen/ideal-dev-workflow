# 工作类型定义

本文档定义所有预设的工作类型。

> 探测规则见 `detection-rules.md`

---

## 预设工作类型

| 工作类型 | 标识符 | 典型特征 |
|----------|--------|----------|
| 软件开发 | `software-dev` | src/, package.json, go.mod, pom.xml |
| 文档撰写 | `doc-writing` | docs/, *.md（无代码特征） |
| 汇报材料 | `presentation` | slides/, *.pptx, 汇报关键词 |
| 论文撰写 | `paper-writing` | *.tex, 论文模板, 参考文献 |
| 专利申请 | `patent-filing` | 专利模板, 权利要求书 |
| 调研报告 | `research-report` | 调研目录, 问卷, 分析报告 |
| 项目申请书 | `project-proposal` | NSFC模板, 可行性报告 |
| 投标文件 | `bid-document` | 招标文件, 投标书模板 |
| 标书解析 | `bid-analysis` | 招标文件待分析 |

---

## 未知工作类型处理

当预设类型都不匹配时：

1. **询问用户描述**：
   ```
   未识别到预设的工作类型。请描述您的工作类型：
   - 这是什么类型的工作？
   - 主要产出是什么？
   - 需要什么样的验证方式？
   ```

2. **生成工作类型标识符**：
   - 基于用户描述生成合适的标识符（如 `video-production`、`data-analysis` 等）
   - **不使用 `custom` 作为标识符** - 是什么工作类型就用什么标识符

3. **直接记录到配置**：
   ```yaml
   work_type: video-production  # 直接使用实际的工作类型标识符
   ```

---

## 各 Skill 如何使用 work_type

`work_type` 记录在 `project-config.md` 中，各 Skill 读取后选择对应的指令文件：

| Skill | work_type 影响 |
|-------|----------------|
| ideal-requirement | 选择需求模板（software-feature.md / doc-requirement.md / presentation-requirement.md） |
| ideal-dev-solution | 选择方案模板（solution.md / doc-outline.md / ppt-outline.md） |
| ideal-dev-plan | 选择计划模板 |
| ideal-test-case | 选择生成测试用例还是评审标准 |
| ideal-test-exec | 选择运行测试脚本还是 LLM 角色模拟 |
| ideal-wiki | 选择文档格式化方式 |

```
各 Skill 读取 project-config.md 获取 work_type

if work_type 是预设类型:
    读取 instructions/{work_type}.md
else:
    Skill 根据 work_type 名称自行处理（可能需要 LLM 生成指导）
```

---

## 扩展指南

### 新增预设工作类型

1. 在本文件"预设工作类型"表格中添加新行
2. 创建 `instructions/{type-id}.md` 指导文件
3. 在 `detection-rules.md` 探测规则中添加特征检测
4. 更新 CLAUDE.md 或相关文档
