"""
YOLO 审计日志模块

负责记录完整的执行过程，包括阶段执行、评审结果和错误信息。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pathlib import Path


class LogType(Enum):
    """日志类型枚举"""
    PHASE = "phase"       # 阶段执行日志
    REVIEW = "review"     # 评审日志
    ERROR = "error"       # 错误日志
    SYSTEM = "system"     # 系统日志


class LogStatus(Enum):
    """日志状态枚举"""
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"
    PENDING = "pending"


@dataclass
class AuditLogEntry:
    """审计日志条目"""
    phase: str
    phase_name: str
    log_type: LogType
    status: str  # success, failure, skipped

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: int = 0  # 秒

    skill_used: Optional[str] = None
    agent_used: Optional[str] = None
    token_count: int = 0

    output_files: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

    # 评审专用字段
    review_passed: Optional[bool] = None
    review_comments: List[str] = field(default_factory=list)
    review_suggestions: List[str] = field(default_factory=list)
    review_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'phase': self.phase,
            'phase_name': self.phase_name,
            'log_type': self.log_type.value,
            'status': self.status,
            'start_time': _format_dt(self.start_time),
            'end_time': _format_dt(self.end_time),
            'duration': self.duration,
            'skill_used': self.skill_used,
            'agent_used': self.agent_used,
            'token_count': self.token_count,
            'output_files': self.output_files,
            'error_message': self.error_message,
            'review_passed': self.review_passed,
            'review_comments': self.review_comments,
            'review_suggestions': self.review_suggestions,
            'review_score': self.review_score
        }


def _format_dt(value: Optional[datetime]) -> Optional[str]:
    """格式化日期时间"""
    if value is None:
        return None
    return value.isoformat()


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    """解析日期时间"""
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def write_audit_log(log_dir: str, entry: AuditLogEntry) -> Path:
    """
    写入审计日志到 Markdown 文件

    Args:
        log_dir: 日志目录
        entry: 日志条目

    Returns:
        Path: 生成的日志文件路径
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # 确定日志文件名
    if entry.log_type == LogType.REVIEW:
        filename = f"review-{entry.phase}.log"
    elif entry.log_type == LogType.ERROR:
        filename = f"error-{entry.phase}.log"
    else:
        filename = f"phase-{entry.phase}.log"

    log_file = log_path / filename

    # 计算 duration
    if entry.start_time and entry.end_time:
        entry.duration = int((entry.end_time - entry.start_time).total_seconds())

    # 生成 Markdown 内容
    content = f"""# YOLO 执行日志 - {entry.phase_name}

## 执行信息
- 阶段编号: {entry.phase}
- 日志类型: {entry.log_type.value}
- 开始时间: {entry.start_time.isoformat() if entry.start_time else 'N/A'}
- 结束时间: {entry.end_time.isoformat() if entry.end_time else 'N/A'}
- 执行耗时: {entry.duration} 秒
- Token 消耗: {entry.token_count}

## 执行过程
- 使用 Skill: {entry.skill_used or 'N/A'}
- 使用 Agent: {entry.agent_used or 'N/A'}

## 输出
- 状态: {entry.status}
- 输出文件: {', '.join(entry.output_files) or '无'}
"""

    # 评审专用内容
    if entry.log_type == LogType.REVIEW:
        review_status = '通过 ✅' if entry.review_passed else '不通过 ❌'
        content += f"""
## 评审结果
- 是否通过: {review_status}
- 评审得分: {entry.review_score:.1f}%
- 评审意见:
{chr(10).join(f'  - {c}' for c in entry.review_comments) if entry.review_comments else '  - 无'}
- 修改建议:
{chr(10).join(f'  - {s}' for s in entry.review_suggestions) if entry.review_suggestions else '  - 无'}
"""

    # 错误信息
    if entry.log_type == LogType.ERROR and entry.error_message:
        content += f"""
## 错误信息
```
{entry.error_message}
```
"""

    log_file.write_text(content, encoding='utf-8')
    return log_file


def generate_summary_log(
    log_dir: str,
    completed_phases: List[str],
    total_token_count: int = 0,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> Path:
    """
    生成 YOLO 执行摘要

    Args:
        log_dir: 日志目录
        completed_phases: 已完成的阶段列表
        total_token_count: 总 Token 消耗
        start_time: 开始时间
        end_time: 结束时间

    Returns:
        Path: 生成的摘要文件路径
    """
    log_path = Path(log_dir)
    summary_file = log_path / "summary.log"

    # 计算总耗时
    total_duration = 0
    if start_time and end_time:
        total_duration = int((end_time - start_time).total_seconds())

    # 统计各阶段状态
    phase_stats = []
    for phase in completed_phases:
        phase_log = log_path / f"phase-{phase}.log"
        review_log = log_path / f"review-{phase}.log"

        phase_status = "✅" if phase_log.exists() else "❌"
        review_status = "✅" if review_log.exists() else "❌"

        phase_stats.append({
            'phase': phase,
            'phase_status': phase_status,
            'review_status': review_status
        })

    content = f"""# YOLO 模式执行摘要

## 执行概览
- 开始时间: {start_time.isoformat() if start_time else 'N/A'}
- 结束时间: {end_time.isoformat() if end_time else 'N/A'}
- 总执行耗时: {total_duration} 秒
- 已完成阶段: {', '.join(completed_phases) or '无'}
- 总阶段数: {len(completed_phases)}
- 总 Token 消耗: {total_token_count}

## 阶段详情

| 阶段 | 执行状态 | 评审状态 |
|------|----------|----------|
"""

    for stat in phase_stats:
        content += f"| {stat['phase']} | {stat['phase_status']} | {stat['review_status']} |\n"

    content += f"""
## 生成时间
{datetime.now().isoformat()}
"""

    summary_file.write_text(content, encoding='utf-8')
    return summary_file


def create_phase_log_entry(
    phase: str,
    phase_name: str,
    skill_used: Optional[str] = None,
    agent_used: Optional[str] = None,
    output_files: Optional[List[str]] = None,
    token_count: int = 0
) -> AuditLogEntry:
    """
    创建阶段执行日志条目

    Args:
        phase: 阶段编号
        phase_name: 阶段名称
        skill_used: 使用的 Skill
        agent_used: 使用的 Agent
        output_files: 输出文件列表
        token_count: Token 消耗

    Returns:
        AuditLogEntry: 日志条目
    """
    return AuditLogEntry(
        phase=phase,
        phase_name=phase_name,
        log_type=LogType.PHASE,
        status=LogStatus.PENDING.value,
        skill_used=skill_used,
        agent_used=agent_used,
        output_files=output_files or [],
        token_count=token_count,
        start_time=datetime.now()
    )


def create_review_log_entry(
    phase: str,
    phase_name: str,
    review_passed: bool,
    review_score: float = 0.0,
    review_comments: Optional[List[str]] = None,
    review_suggestions: Optional[List[str]] = None,
    token_count: int = 0
) -> AuditLogEntry:
    """
    创建评审日志条目

    Args:
        phase: 阶段编号
        phase_name: 阶段名称
        review_passed: 评审是否通过
        review_score: 评审得分
        review_comments: 评审意见
        review_suggestions: 修改建议
        token_count: Token 消耗

    Returns:
        AuditLogEntry: 日志条目
    """
    return AuditLogEntry(
        phase=phase,
        phase_name=phase_name,
        log_type=LogType.REVIEW,
        status=LogStatus.SUCCESS.value if review_passed else LogStatus.FAILURE.value,
        review_passed=review_passed,
        review_score=review_score,
        review_comments=review_comments or [],
        review_suggestions=review_suggestions or [],
        token_count=token_count,
        start_time=datetime.now(),
        end_time=datetime.now()
    )


def create_error_log_entry(
    phase: str,
    phase_name: str,
    error_message: str,
    skill_used: Optional[str] = None
) -> AuditLogEntry:
    """
    创建错误日志条目

    Args:
        phase: 阶段编号
        phase_name: 阶段名称
        error_message: 错误信息
        skill_used: 使用的 Skill

    Returns:
        AuditLogEntry: 日志条目
    """
    return AuditLogEntry(
        phase=phase,
        phase_name=phase_name,
        log_type=LogType.ERROR,
        status=LogStatus.FAILURE.value,
        error_message=error_message,
        skill_used=skill_used,
        start_time=datetime.now(),
        end_time=datetime.now()
    )


def finalize_log_entry(entry: AuditLogEntry, status: str = "success") -> AuditLogEntry:
    """
    完成日志条目（设置结束时间和状态）

    Args:
        entry: 日志条目
        status: 最终状态

    Returns:
        AuditLogEntry: 更新后的日志条目
    """
    entry.end_time = datetime.now()
    entry.status = status

    if entry.start_time and entry.end_time:
        entry.duration = int((entry.end_time - entry.start_time).total_seconds())

    return entry


def get_phase_name(phase: str) -> str:
    """
    获取阶段名称

    Args:
        phase: 阶段编号

    Returns:
        str: 阶段名称
    """
    phase_names = {
        'P1': '需求编写',
        'P2': '需求评审',
        'P3': '技术方案',
        'P4': '方案评审',
        'P5': '计划生成',
        'P6': '计划评审',
        'P7': '测试用例',
        'P8': '用例评审',
        'P9': '开发执行',
        'P10': '代码评审',
        'P11': '测试执行',
        'P12': '测试评审',
        'P13': '维基更新',
        'P14': '维基评审',
        'P15': '成果提交',
    }
    return phase_names.get(phase, f'阶段 {phase}')
