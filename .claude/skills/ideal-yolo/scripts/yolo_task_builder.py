"""
YOLO Task Prompt 构建模块

负责根据阶段配置构建 Task Prompt，实现上下文隔离的最小化输入。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum
import re


class PhaseType(Enum):
    """阶段类型"""
    EXECUTION = "execution"
    REVIEW = "review"


class ModelType(Enum):
    """模型类型"""
    OPUS = "opus"
    SONNET = "sonnet"


@dataclass
class PhaseConfig:
    """阶段配置数据类"""
    phase: str
    name: str
    phase_type: PhaseType
    model: ModelType
    description: str
    input_files: List[str]
    output_files: List[str]
    allowed_tools: List[str]
    return_budget: int  # tokens
    depends_on: str
    agent: Optional[str] = None
    skill: Optional[str] = None
    review_criteria: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'phase': self.phase,
            'name': self.name,
            'phase_type': self.phase_type.value,
            'model': self.model.value,
            'description': self.description,
            'input_files': self.input_files,
            'output_files': self.output_files,
            'allowed_tools': self.allowed_tools,
            'return_budget': self.return_budget,
            'depends_on': self.depends_on,
            'agent': self.agent,
            'skill': self.skill,
            'review_criteria': self.review_criteria
        }


# 阶段配置表（从 phase-configs.md 提取）
PHASE_CONFIGS: Dict[str, PhaseConfig] = {
    'P3': PhaseConfig(
        phase='P3',
        name='技术方案',
        phase_type=PhaseType.EXECUTION,
        model=ModelType.OPUS,
        description='根据需求文档生成技术方案',
        input_files=['P1-需求文档.md', '.claude/project-config.md'],
        output_files=['P3-技术方案.md'],
        allowed_tools=['Read', 'Write', 'Glob', 'Grep', 'Bash'],
        return_budget=3000,
        depends_on='P2',
        agent='architect',
        skill='ideal-dev-solution'
    ),
    'P4': PhaseConfig(
        phase='P4',
        name='方案评审',
        phase_type=PhaseType.REVIEW,
        model=ModelType.SONNET,
        description='评审技术方案的质量和可行性',
        input_files=['P3-技术方案.md', 'P1-需求文档.md'],
        output_files=['yolo-logs/review-P4.log'],
        allowed_tools=['Read', 'Write'],
        return_budget=2000,
        depends_on='P3',
        review_criteria=[
            '需求覆盖完整性',
            '技术选型合理性',
            '架构设计清晰度',
            '风险识别充分性',
            '实施可行性'
        ]
    ),
    'P5': PhaseConfig(
        phase='P5',
        name='计划生成',
        phase_type=PhaseType.EXECUTION,
        model=ModelType.OPUS,
        description='根据技术方案生成编码计划和故事文件',
        input_files=['P3-技术方案.md', 'P1-需求文档.md'],
        output_files=['P5-编码计划.md', 'stories/index.md', 'stories/0XX-*.md'],
        allowed_tools=['Read', 'Write', 'Glob', 'Grep', 'Bash'],
        return_budget=3000,
        depends_on='P4',
        agent='architect',
        skill='ideal-dev-plan'
    ),
    'P6': PhaseConfig(
        phase='P6',
        name='计划评审',
        phase_type=PhaseType.REVIEW,
        model=ModelType.SONNET,
        description='评审编码计划的合理性和完整性',
        input_files=['P5-编码计划.md', 'stories/index.md'],
        output_files=['yolo-logs/review-P6.log'],
        allowed_tools=['Read', 'Write'],
        return_budget=2000,
        depends_on='P5',
        review_criteria=[
            '任务拆分合理性',
            '依赖关系正确性',
            '估算合理性',
            '故事文件完整性'
        ]
    ),
    'P7': PhaseConfig(
        phase='P7',
        name='测试用例',
        phase_type=PhaseType.EXECUTION,
        model=ModelType.SONNET,
        description='根据技术方案和编码计划生成测试用例',
        input_files=['P3-技术方案.md', 'P5-编码计划.md', 'P1-需求文档.md'],
        output_files=['P7-测试用例.md'],
        allowed_tools=['Read', 'Write', 'Glob', 'Grep'],
        return_budget=3000,
        depends_on='P6',
        agent='qa',
        skill='ideal-test-case'
    ),
    'P8': PhaseConfig(
        phase='P8',
        name='用例评审',
        phase_type=PhaseType.REVIEW,
        model=ModelType.SONNET,
        description='评审测试用例的覆盖度和质量',
        input_files=['P7-测试用例.md', 'P3-技术方案.md'],
        output_files=['yolo-logs/review-P8.log'],
        allowed_tools=['Read', 'Write'],
        return_budget=2000,
        depends_on='P7',
        review_criteria=[
            '功能覆盖完整性',
            '边界条件覆盖',
            '异常场景覆盖',
            '用例可执行性'
        ]
    ),
    'P9': PhaseConfig(
        phase='P9',
        name='开发执行',
        phase_type=PhaseType.EXECUTION,
        model=ModelType.OPUS,
        description='按故事逐个执行开发任务（上下文隔离）',
        input_files=['stories/current.md', 'P3-技术方案.md', 'P5-编码计划.md'],
        output_files=['src/**/*.py', 'tests/**/*.py'],
        allowed_tools=['Read', 'Write', 'Edit', 'Glob', 'Grep', 'Bash'],
        return_budget=3000,
        depends_on='P8',
        agent='dev',
        skill='ideal-dev-exec'
    ),
    'P10': PhaseConfig(
        phase='P10',
        name='代码评审',
        phase_type=PhaseType.REVIEW,
        model=ModelType.SONNET,
        description='评审代码质量和规范性',
        input_files=['git-diff', 'P3-技术方案.md'],
        output_files=['yolo-logs/review-P10.log'],
        allowed_tools=['Read', 'Write', 'Bash'],
        return_budget=2000,
        depends_on='P9',
        review_criteria=[
            '代码规范遵循',
            '设计模式使用',
            '错误处理完整性',
            '测试覆盖充分性',
            '安全性考虑'
        ]
    ),
    'P11': PhaseConfig(
        phase='P11',
        name='测试执行',
        phase_type=PhaseType.EXECUTION,
        model=ModelType.SONNET,
        description='执行测试用例并生成测试报告',
        input_files=['P7-测试用例.md', 'stories/index.md'],
        output_files=['P11-测试报告.md'],
        allowed_tools=['Read', 'Write', 'Bash'],
        return_budget=3000,
        depends_on='P10',
        agent='qa',
        skill='ideal-test-exec'
    ),
    'P12': PhaseConfig(
        phase='P12',
        name='测试评审',
        phase_type=PhaseType.REVIEW,
        model=ModelType.SONNET,
        description='评审测试结果的充分性',
        input_files=['P11-测试报告.md', 'P7-测试用例.md'],
        output_files=['yolo-logs/review-P12.log'],
        allowed_tools=['Read', 'Write'],
        return_budget=2000,
        depends_on='P11',
        review_criteria=[
            '测试通过率达标（>= 80%）',
            '失败用例分析充分',
            '回归测试覆盖',
            '性能测试结果'
        ]
    ),
    'P13': PhaseConfig(
        phase='P13',
        name='维基更新',
        phase_type=PhaseType.EXECUTION,
        model=ModelType.SONNET,
        description='更新项目维基文档',
        input_files=['P1-需求文档.md', 'P3-技术方案.md', 'P11-测试报告.md', 'stories/index.md'],
        output_files=['Wiki/**/*.md'],
        allowed_tools=['Read', 'Write', 'Glob', 'Grep'],
        return_budget=3000,
        depends_on='P12',
        agent='tech-writer',
        skill='ideal-wiki'
    ),
    'P14': PhaseConfig(
        phase='P14',
        name='维基评审',
        phase_type=PhaseType.REVIEW,
        model=ModelType.SONNET,
        description='评审维基文档的完整性和准确性',
        input_files=['Wiki/**/*.md'],
        output_files=['yolo-logs/review-P14.log'],
        allowed_tools=['Read', 'Write', 'Glob'],
        return_budget=2000,
        depends_on='P13',
        review_criteria=[
            '文档完整性',
            '内容准确性',
            '结构清晰度',
            '示例充分性'
        ]
    ),
}

# YOLO 模式执行顺序
YOLO_EXECUTION_ORDER = ['P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11', 'P12', 'P13', 'P14']

# Agent 角色定义
AGENT_DEFINITIONS = {
    'architect': """你是一位资深的软件架构师。你的职责是：
1. 分析需求并设计技术方案
2. 评估技术选型的优劣
3. 制定实施计划和任务分解
4. 识别技术风险和应对策略

你的输出应该：
- 结构清晰、逻辑严谨
- 技术选型有理有据
- 风险识别全面
- 实施计划可执行""",

    'dev': """你是一位经验丰富的开发工程师。你的职责是：
1. 按照技术方案和编码计划实现功能
2. 编写高质量的代码
3. 编写单元测试
4. 遵循代码规范和最佳实践

你的输出应该：
- 代码简洁、可读性强
- 遵循 SOLID 原则
- 有充分的错误处理
- 测试覆盖充分""",

    'qa': """你是一位专业的测试工程师。你的职责是：
1. 设计全面的测试用例
2. 执行测试并记录结果
3. 分析测试覆盖率
4. 识别质量风险

你的输出应该：
- 测试用例覆盖全面
- 边界条件考虑充分
- 异常场景不遗漏
- 结果分析准确""",

    'tech-writer': """你是一位技术文档撰写专家。你的职责是：
1. 编写清晰的技术文档
2. 更新项目维基
3. 确保文档准确性
4. 维护文档结构

你的输出应该：
- 语言简洁明了
- 结构层次清晰
- 示例充分有效
- 易于理解和使用"""
}


def get_phase_config(phase: str) -> Optional[PhaseConfig]:
    """
    获取阶段配置

    Args:
        phase: 阶段编号 (P3-P14)

    Returns:
        PhaseConfig: 阶段配置，不存在返回 None
    """
    return PHASE_CONFIGS.get(phase)


def get_model_for_phase(phase: str) -> str:
    """
    获取阶段使用的模型

    Args:
        phase: 阶段编号

    Returns:
        str: 模型名称 (opus/sonnet)
    """
    config = get_phase_config(phase)
    if config:
        return config.model.value
    return 'sonnet'  # 默认使用 sonnet


def is_execution_phase(phase: str) -> bool:
    """
    检查是否为执行阶段

    Args:
        phase: 阶段编号

    Returns:
        bool: 是否为执行阶段
    """
    config = get_phase_config(phase)
    return config is not None and config.phase_type == PhaseType.EXECUTION


def is_review_phase(phase: str) -> bool:
    """
    检查是否为评审阶段

    Args:
        phase: 阶段编号

    Returns:
        bool: 是否为评审阶段
    """
    config = get_phase_config(phase)
    return config is not None and config.phase_type == PhaseType.REVIEW


def build_task_prompt(
    phase: str,
    docs_dir: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    构建 Task Prompt

    根据阶段配置生成包含最小上下文的 Task Prompt。

    Args:
        phase: 阶段编号 (P3-P14)
        docs_dir: 文档目录路径
        context: 额外上下文信息（如 story_id）

    Returns:
        str: 构建的 Task Prompt
    """
    config = get_phase_config(phase)
    if not config:
        raise ValueError(f"未知的阶段: {phase}")

    context = context or {}

    # 构建角色设定
    role_section = _build_role_section(config, context)

    # 构建输入文件列表
    input_section = _build_input_section(config, docs_dir, context)

    # 构建任务描述
    task_section = _build_task_section(config, context)

    # 构建输出要求
    output_section = _build_output_section(config)

    # 构建返回格式
    return_section = _build_return_format_section(config)

    # 构建上下文预算控制指令
    budget_section = _build_budget_control_section(config)

    prompt = f"""# YOLO 模式 Task - {config.name} ({phase})

{role_section}

{input_section}

{task_section}

{output_section}

{return_section}

{budget_section}
"""
    return prompt


def _build_role_section(config: PhaseConfig, context: Dict[str, Any]) -> str:
    """构建角色设定部分"""
    if config.agent and config.agent in AGENT_DEFINITIONS:
        agent_def = AGENT_DEFINITIONS[config.agent]
        return f"""## 角色身份

{agent_def}"""
    elif config.phase_type == PhaseType.REVIEW:
        return """## 角色身份

你是一位严谨的评审专家。你的职责是：
1. 根据评审标准评估交付物质量
2. 提供具体的改进建议
3. 确保交付物符合项目规范

你的评审应该：
- 客观公正
- 标准明确
- 建议可执行"""
    else:
        return f"""## 角色身份

你是 {config.name} 阶段的执行者。"""


def _build_input_section(config: PhaseConfig, docs_dir: str, context: Dict[str, Any]) -> str:
    """构建输入文件部分"""
    lines = ["## 输入文件\n", "请读取以下文件（不要读取其他文件）：\n"]

    # P9 特殊处理：只加载当前故事
    if config.phase == 'P9' and 'story_id' in context:
        story_id = context['story_id']
        lines.append(f"- stories/{story_id}.md  # 当前故事文件")
        lines.append(f"- P3-技术方案.md  # 技术方案参考")
        lines.append(f"- P5-编码计划.md  # 编码计划参考")
    else:
        for file_path in config.input_files:
            if file_path == 'git-diff':
                lines.append(f"- git-diff  # 使用 git diff 获取变更")
            elif file_path.endswith('**/*'):
                lines.append(f"- {file_path}  # 使用 Glob 匹配所有相关文件")
            else:
                lines.append(f"- {file_path}")

    return "\n".join(lines)


def _build_task_section(config: PhaseConfig, context: Dict[str, Any]) -> str:
    """构建任务描述部分"""
    lines = ["## 任务\n", config.description]

    if config.phase_type == PhaseType.REVIEW:
        lines.append("\n\n### 评审标准\n")
        for i, criteria in enumerate(config.review_criteria, 1):
            lines.append(f"{i}. {criteria}")

    # P9 特殊处理
    if config.phase == 'P9' and 'story_id' in context:
        lines.append(f"\n\n### 当前故事\n")
        lines.append(f"故事 ID: {context['story_id']}")
        if 'story_title' in context:
            lines.append(f"故事标题: {context['story_title']}")

    return "\n".join(lines)


def _build_output_section(config: PhaseConfig) -> str:
    """构建输出要求部分"""
    lines = ["## 输出\n", "请生成以下输出文件：\n"]

    for file_path in config.output_files:
        lines.append(f"- {file_path}")

    lines.append("\n### 允许使用的工具\n")
    lines.append(", ".join(config.allowed_tools))

    return "\n".join(lines)


def _build_return_format_section(config: PhaseConfig) -> str:
    """构建返回格式部分"""
    if config.phase_type == PhaseType.EXECUTION:
        return """## 返回格式

请在完成所有任务后，输出以下 JSON 格式的摘要：

```json
{
  "success": true,
  "phase": "阶段编号",
  "output_files": ["输出文件列表"],
  "summary": "执行摘要（50-100字）",
  "key_decisions": ["关键决策1", "关键决策2"],
  "risks": ["风险1", "风险2"],
  "metrics": {
    "files_created": 0,
    "files_modified": 0
  },
  "error_message": null
}
```

**重要**：
- summary 必须简洁，控制在 50-100 字
- key_decisions 最多 5 条
- risks 最多 3 条
- 整个 JSON 必须控制在 3K tokens 以内"""

    else:  # REVIEW 阶段
        return """## 返回格式

请在完成评审后，输出以下 JSON 格式的摘要：

```json
{
  "success": true,
  "phase": "阶段编号",
  "review_passed": true,
  "review_score": 85,
  "review_comments": ["评审意见1", "评审意见2"],
  "review_suggestions": ["改进建议1", "改进建议2"],
  "summary": "评审摘要（50-100字）",
  "error_message": null
}
```

**重要**：
- review_passed: 评审是否通过（总分 >= 70 为通过）
- review_score: 评审得分（0-100）
- review_comments: 最多 5 条
- review_suggestions: 最多 3 条
- 整个 JSON 必须控制在 2K tokens 以内"""


def _build_budget_control_section(config: PhaseConfig) -> str:
    """构建上下文预算控制指令"""
    return f"""## 上下文预算控制

**返回摘要预算**: {config.return_budget} tokens

为了确保主会话编排器上下文不溢出，请严格控制返回摘要的大小：
1. 只返回必要的信息
2. 使用简洁的语言
3. 避免在摘要中重复文档内容
4. 如有大量数据，请保存到文件中，摘要中只引用文件名"""


def build_p9_story_prompt(
    story_id: str,
    story_title: str,
    story_file: str,
    docs_dir: str
) -> str:
    """
    构建 P9 阶段单故事的 Task Prompt

    Args:
        story_id: 故事 ID (如 001)
        story_title: 故事标题
        story_file: 故事文件路径
        docs_dir: 文档目录

    Returns:
        str: Task Prompt
    """
    context = {
        'story_id': story_id,
        'story_title': story_title,
        'story_file': story_file
    }
    return build_task_prompt('P9', docs_dir, context)


def get_next_phase(current_phase: str) -> Optional[str]:
    """
    获取下一个阶段

    Args:
        current_phase: 当前阶段

    Returns:
        str: 下一个阶段编号，没有则返回 None
    """
    try:
        index = YOLO_EXECUTION_ORDER.index(current_phase)
        if index < len(YOLO_EXECUTION_ORDER) - 1:
            return YOLO_EXECUTION_ORDER[index + 1]
    except ValueError:
        pass
    return None


def get_all_phases() -> List[str]:
    """
    获取所有阶段列表

    Returns:
        List[str]: 阶段列表
    """
    return YOLO_EXECUTION_ORDER.copy()


def get_execution_phases() -> List[str]:
    """
    获取所有执行阶段

    Returns:
        List[str]: 执行阶段列表
    """
    return [p for p in YOLO_EXECUTION_ORDER if is_execution_phase(p)]


def get_review_phases() -> List[str]:
    """
    获取所有评审阶段

    Returns:
        List[str]: 评审阶段列表
    """
    return [p for p in YOLO_EXECUTION_ORDER if is_review_phase(p)]
