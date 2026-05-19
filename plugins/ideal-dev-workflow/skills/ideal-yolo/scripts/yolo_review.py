"""
YOLO 自动评审模块

负责对各阶段输出进行自动评审，生成评审结果和修改建议。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pathlib import Path


class ReviewPhase(Enum):
    """评审阶段枚举"""
    P4 = "P4"   # 技术方案评审
    P6 = "P6"   # 计划评审
    P8 = "P8"   # 测试用例评审
    P10 = "P10"  # 代码评审
    P12 = "P12"  # 测试报告评审
    P14 = "P14"  # 维基文档评审


class ReviewStatus(Enum):
    """评审状态枚举"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ChecklistItem:
    """检查清单项"""
    id: str
    description: str
    required: bool = True
    passed: Optional[bool] = None
    comment: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'description': self.description,
            'required': self.required,
            'passed': self.passed,
            'comment': self.comment
        }


@dataclass
class ReviewStandard:
    """评审标准"""
    phase: ReviewPhase
    phase_name: str
    description: str
    checklist: List[ChecklistItem] = field(default_factory=list)
    min_pass_count: int = 1  # 最少需要通过的检查项数量

    def get_checklist_by_id(self, item_id: str) -> Optional[ChecklistItem]:
        """根据 ID 获取检查清单项"""
        for item in self.checklist:
            if item.id == item_id:
                return item
        return None


@dataclass
class ReviewResult:
    """评审结果"""
    phase: ReviewPhase
    status: ReviewStatus
    passed: bool
    score: float = 0.0  # 0-100
    comments: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    checklist_results: List[ChecklistItem] = field(default_factory=list)
    reviewed_at: datetime = field(default_factory=datetime.now)
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'phase': self.phase.value,
            'status': self.status.value,
            'passed': self.passed,
            'score': self.score,
            'comments': self.comments,
            'suggestions': self.suggestions,
            'checklist_results': [item.to_dict() for item in self.checklist_results],
            'reviewed_at': self.reviewed_at.isoformat(),
            'retry_count': self.retry_count
        }


# 预定义的评审标准
DEFAULT_REVIEW_STANDARDS: Dict[ReviewPhase, ReviewStandard] = {
    ReviewPhase.P4: ReviewStandard(
        phase=ReviewPhase.P4,
        phase_name="技术方案评审",
        description="评审技术方案的架构合理性、技术可行性和风险识别",
        checklist=[
            ChecklistItem("P4-001", "架构设计合理，模块划分清晰", required=True),
            ChecklistItem("P4-002", "技术选型有依据，符合项目需求", required=True),
            ChecklistItem("P4-003", "风险已识别并有应对措施", required=True),
            ChecklistItem("P4-004", "接口设计完整", required=False),
            ChecklistItem("P4-005", "性能考量已包含", required=False),
        ],
        min_pass_count=3
    ),
    ReviewPhase.P6: ReviewStandard(
        phase=ReviewPhase.P6,
        phase_name="计划评审",
        description="评审编码计划的任务完整性、依赖清晰度和估算合理性",
        checklist=[
            ChecklistItem("P6-001", "任务列表完整，覆盖所有需求", required=True),
            ChecklistItem("P6-002", "任务依赖关系清晰", required=True),
            ChecklistItem("P6-003", "时间估算合理", required=False),
            ChecklistItem("P6-004", "测试策略已定义", required=True),
            ChecklistItem("P6-005", "风险任务已识别", required=False),
        ],
        min_pass_count=3
    ),
    ReviewPhase.P8: ReviewStandard(
        phase=ReviewPhase.P8,
        phase_name="测试用例评审",
        description="评审测试用例的覆盖率和边界条件",
        checklist=[
            ChecklistItem("P8-001", "功能测试覆盖所有需求", required=True),
            ChecklistItem("P8-002", "边界条件测试覆盖", required=True),
            ChecklistItem("P8-003", "异常场景测试覆盖", required=True),
            ChecklistItem("P8-004", "测试用例可执行", required=True),
            ChecklistItem("P8-005", "测试数据准备完整", required=False),
        ],
        min_pass_count=4
    ),
    ReviewPhase.P10: ReviewStandard(
        phase=ReviewPhase.P10,
        phase_name="代码评审",
        description="评审代码的规范符合性、安全性和可维护性",
        checklist=[
            ChecklistItem("P10-001", "代码符合项目规范", required=True),
            ChecklistItem("P10-002", "无安全漏洞", required=True),
            ChecklistItem("P10-003", "代码可读可维护", required=True),
            ChecklistItem("P10-004", "单元测试覆盖核心逻辑", required=True),
            ChecklistItem("P10-005", "无冗余代码", required=False),
        ],
        min_pass_count=4
    ),
    ReviewPhase.P12: ReviewStandard(
        phase=ReviewPhase.P12,
        phase_name="测试报告评审",
        description="评审测试报告的通过率和缺陷修复情况",
        checklist=[
            ChecklistItem("P12-001", "测试通过率 ≥ 80%", required=True),
            ChecklistItem("P12-002", "关键缺陷已修复", required=True),
            ChecklistItem("P12-003", "测试报告完整", required=True),
            ChecklistItem("P12-004", "遗留问题已记录", required=False),
        ],
        min_pass_count=3
    ),
    ReviewPhase.P14: ReviewStandard(
        phase=ReviewPhase.P14,
        phase_name="维基文档评审",
        description="评审维基文档的完整性、准确性和可读性",
        checklist=[
            ChecklistItem("P14-001", "文档结构完整", required=True),
            ChecklistItem("P14-002", "内容准确无误", required=True),
            ChecklistItem("P14-003", "格式规范可读", required=True),
            ChecklistItem("P14-004", "示例代码可运行", required=False),
        ],
        min_pass_count=3
    ),
}


def get_review_standard(phase: ReviewPhase) -> ReviewStandard:
    """
    获取指定阶段的评审标准

    Args:
        phase: 评审阶段

    Returns:
        ReviewStandard: 评审标准对象
    """
    return DEFAULT_REVIEW_STANDARDS.get(phase, ReviewStandard(
        phase=phase,
        phase_name=f"{phase.value}评审",
        description="通用评审标准",
        checklist=[],
        min_pass_count=1
    ))


def apply_checklist(
    standard: ReviewStandard,
    checklist_results: List[Dict[str, Any]]
) -> List[ChecklistItem]:
    """
    应用检查清单结果

    Args:
        standard: 评审标准
        checklist_results: 检查清单结果列表，每项包含 id, passed, comment

    Returns:
        List[ChecklistItem]: 更新后的检查清单项列表
    """
    results = []
    results_map = {r['id']: r for r in checklist_results}

    for item in standard.checklist:
        result_item = ChecklistItem(
            id=item.id,
            description=item.description,
            required=item.required
        )

        if item.id in results_map:
            result_item.passed = results_map[item.id].get('passed', False)
            result_item.comment = results_map[item.id].get('comment')

        results.append(result_item)

    return results


def calculate_score(checklist_results: List[ChecklistItem]) -> float:
    """
    计算评审得分

    Args:
        checklist_results: 检查清单结果

    Returns:
        float: 评审得分 (0-100)
    """
    if not checklist_results:
        return 0.0

    passed_count = sum(1 for item in checklist_results if item.passed)
    total_count = len(checklist_results)

    return (passed_count / total_count) * 100


def check_review_passed(
    standard: ReviewStandard,
    checklist_results: List[ChecklistItem]
) -> bool:
    """
    检查评审是否通过

    Args:
        standard: 评审标准
        checklist_results: 检查清单结果

    Returns:
        bool: 评审是否通过
    """
    # 检查所有必填项是否通过
    required_passed = all(
        item.passed for item in checklist_results if item.required
    )

    # 检查通过数量是否达到最低要求
    passed_count = sum(1 for item in checklist_results if item.passed)

    return required_passed and passed_count >= standard.min_pass_count


def auto_review(
    phase: ReviewPhase,
    content: str,
    checklist_results: List[Dict[str, Any]],
    comments: Optional[List[str]] = None,
    suggestions: Optional[List[str]] = None,
    retry_count: int = 0
) -> ReviewResult:
    """
    执行自动评审

    Args:
        phase: 评审阶段
        content: 待评审内容
        checklist_results: 检查清单结果
        comments: 评审意见
        suggestions: 修改建议
        retry_count: 重试次数

    Returns:
        ReviewResult: 评审结果
    """
    standard = get_review_standard(phase)
    applied_checklist = apply_checklist(standard, checklist_results)
    score = calculate_score(applied_checklist)
    passed = check_review_passed(standard, applied_checklist)

    status = ReviewStatus.PASSED if passed else ReviewStatus.FAILED

    return ReviewResult(
        phase=phase,
        status=status,
        passed=passed,
        score=score,
        comments=comments or [],
        suggestions=suggestions or [],
        checklist_results=applied_checklist,
        reviewed_at=datetime.now(),
        retry_count=retry_count
    )


def generate_review_log(
    result: ReviewResult,
    output_dir: str,
    content_file: Optional[str] = None
) -> Path:
    """
    生成评审日志

    Args:
        result: 评审结果
        output_dir: 输出目录
        content_file: 被评审文件路径

    Returns:
        Path: 生成的日志文件路径
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    log_file = output_path / f"review-{result.phase.value}.log"

    # 构建日志内容
    content = f"""# YOLO 自动评审日志 - {result.phase.value}

## 评审信息
- 阶段: {result.phase.value} - {DEFAULT_REVIEW_STANDARDS.get(result.phase, ReviewStandard(result.phase, '', '')).phase_name}
- 评审时间: {result.reviewed_at.isoformat()}
- 评审结果: {'通过 ✅' if result.passed else '不通过 ❌'}
- 评审得分: {result.score:.1f}%
- 重试次数: {result.retry_count}

## 检查清单

| ID | 检查项 | 必填 | 结果 | 备注 |
|----|--------|------|------|------|
"""

    for item in result.checklist_results:
        status_icon = '✅' if item.passed else ('❌' if item.passed is False else '⏸️')
        required_icon = '🔴' if item.required else '🟡'
        comment = item.comment or '-'
        content += f"| {item.id} | {item.description} | {required_icon} | {status_icon} | {comment} |\n"

    if result.comments:
        content += "\n## 评审意见\n\n"
        for i, comment in enumerate(result.comments, 1):
            content += f"{i}. {comment}\n"

    if result.suggestions:
        content += "\n## 修改建议\n\n"
        for i, suggestion in enumerate(result.suggestions, 1):
            content += f"{i}. {suggestion}\n"

    if content_file:
        content += f"\n## 被评审文件\n\n{content_file}\n"

    log_file.write_text(content, encoding='utf-8')
    return log_file


def get_phase_review_phases() -> List[ReviewPhase]:
    """
    获取需要评审的阶段列表

    Returns:
        List[ReviewPhase]: 需要评审的阶段列表
    """
    return [
        ReviewPhase.P4,
        ReviewPhase.P6,
        ReviewPhase.P8,
        ReviewPhase.P10,
        ReviewPhase.P12,
        ReviewPhase.P14,
    ]


def is_review_phase(phase: str) -> bool:
    """
    检查指定阶段是否需要评审

    Args:
        phase: 阶段编号 (如 P4, P6)

    Returns:
        bool: 是否需要评审
    """
    try:
        return ReviewPhase(phase) in get_phase_review_phases()
    except ValueError:
        return False
