"""
YOLO 阶段编排模块

负责按顺序调度和执行 P3-P14 阶段，管理阶段间的上下文传递。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from enum import Enum
from pathlib import Path
import sys

# 添加同级目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from yolo_state import (
    YoloStatus,
    YoloModeConfig,
    load_yolo_state,
    save_yolo_state,
    update_phase_status,
    add_audit_log
)
from yolo_logger import (
    LogType,
    AuditLogEntry,
    write_audit_log,
    create_phase_log_entry,
    create_review_log_entry,
    finalize_log_entry,
    get_phase_name
)


class PhaseType(Enum):
    """阶段类型"""
    EXECUTION = "execution"  # 执行阶段
    REVIEW = "review"        # 评审阶段


@dataclass
class PhaseConfig:
    """阶段配置"""
    phase: str
    phase_name: str
    phase_type: PhaseType
    skill_name: Optional[str] = None
    agent_name: Optional[str] = None
    depends_on: Optional[str] = None  # 依赖的前一阶段
    max_retries: int = 3
    timeout_seconds: int = 600  # 10 分钟

    def to_dict(self) -> Dict[str, Any]:
        return {
            'phase': self.phase,
            'phase_name': self.phase_name,
            'phase_type': self.phase_type.value,
            'skill_name': self.skill_name,
            'agent_name': self.agent_name,
            'depends_on': self.depends_on,
            'max_retries': self.max_retries,
            'timeout_seconds': self.timeout_seconds
        }


@dataclass
class ExecutionContext:
    """执行上下文"""
    iteration_name: str
    docs_dir: str
    log_dir: str
    state_file: str
    current_phase: str
    completed_phases: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'iteration_name': self.iteration_name,
            'docs_dir': self.docs_dir,
            'log_dir': self.log_dir,
            'state_file': self.state_file,
            'current_phase': self.current_phase,
            'completed_phases': self.completed_phases,
            'variables': self.variables
        }


@dataclass
class PhaseResult:
    """阶段执行结果"""
    phase: str
    success: bool
    output_files: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    review_passed: Optional[bool] = None
    review_score: float = 0.0
    retry_count: int = 0
    duration: int = 0
    token_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'phase': self.phase,
            'success': self.success,
            'output_files': self.output_files,
            'error_message': self.error_message,
            'review_passed': self.review_passed,
            'review_score': self.review_score,
            'retry_count': self.retry_count,
            'duration': self.duration,
            'token_count': self.token_count
        }


# 默认阶段编排配置
DEFAULT_PHASE_CONFIGS: Dict[str, PhaseConfig] = {
    # 执行阶段
    'P3': PhaseConfig(
        phase='P3',
        phase_name='技术方案',
        phase_type=PhaseType.EXECUTION,
        skill_name='ideal-dev-solution',
        agent_name='architect',
        max_retries=3
    ),
    'P5': PhaseConfig(
        phase='P5',
        phase_name='计划生成',
        phase_type=PhaseType.EXECUTION,
        skill_name='ideal-dev-plan',
        agent_name='architect',
        depends_on='P4',
        max_retries=3
    ),
    'P7': PhaseConfig(
        phase='P7',
        phase_name='测试用例',
        phase_type=PhaseType.EXECUTION,
        skill_name='ideal-test-case',
        agent_name='qa',
        depends_on='P6',
        max_retries=3
    ),
    'P9': PhaseConfig(
        phase='P9',
        phase_name='开发执行',
        phase_type=PhaseType.EXECUTION,
        skill_name='ideal-dev-exec',
        agent_name='dev',
        depends_on='P8',
        max_retries=3
    ),
    'P11': PhaseConfig(
        phase='P11',
        phase_name='测试执行',
        phase_type=PhaseType.EXECUTION,
        skill_name='ideal-test-exec',
        agent_name='qa',
        depends_on='P10',
        max_retries=3
    ),
    'P13': PhaseConfig(
        phase='P13',
        phase_name='维基更新',
        phase_type=PhaseType.EXECUTION,
        skill_name='ideal-wiki',
        agent_name='tech-writer',
        depends_on='P12',
        max_retries=3
    ),
    # 评审阶段
    'P4': PhaseConfig(
        phase='P4',
        phase_name='方案评审',
        phase_type=PhaseType.REVIEW,
        depends_on='P3',
        max_retries=3
    ),
    'P6': PhaseConfig(
        phase='P6',
        phase_name='计划评审',
        phase_type=PhaseType.REVIEW,
        depends_on='P5',
        max_retries=3
    ),
    'P8': PhaseConfig(
        phase='P8',
        phase_name='用例评审',
        phase_type=PhaseType.REVIEW,
        depends_on='P7',
        max_retries=3
    ),
    'P10': PhaseConfig(
        phase='P10',
        phase_name='代码评审',
        phase_type=PhaseType.REVIEW,
        depends_on='P9',
        max_retries=3
    ),
    'P12': PhaseConfig(
        phase='P12',
        phase_name='测试评审',
        phase_type=PhaseType.REVIEW,
        depends_on='P11',
        max_retries=3
    ),
    'P14': PhaseConfig(
        phase='P14',
        phase_name='维基评审',
        phase_type=PhaseType.REVIEW,
        depends_on='P13',
        max_retries=3
    ),
}

# YOLO 模式执行顺序
YOLO_EXECUTION_ORDER = ['P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11', 'P12', 'P13', 'P14']


def get_phase_config(phase: str) -> Optional[PhaseConfig]:
    """
    获取阶段配置

    Args:
        phase: 阶段编号

    Returns:
        PhaseConfig: 阶段配置，不存在返回 None
    """
    return DEFAULT_PHASE_CONFIGS.get(phase)


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


def can_execute_phase(ctx: ExecutionContext, phase: str) -> bool:
    """
    检查是否可以执行指定阶段

    Args:
        ctx: 执行上下文
        phase: 阶段编号

    Returns:
        bool: 是否可以执行
    """
    config = get_phase_config(phase)
    if config is None:
        return False

    # 检查依赖
    if config.depends_on and config.depends_on not in ctx.completed_phases:
        return False

    return True


def execute_phase(
    ctx: ExecutionContext,
    phase: str,
    executor: Optional[Callable[[ExecutionContext, PhaseConfig], PhaseResult]] = None
) -> PhaseResult:
    """
    执行单个阶段

    Args:
        ctx: 执行上下文
        phase: 阶段编号
        executor: 自定义执行函数（用于测试或自定义逻辑）

    Returns:
        PhaseResult: 执行结果
    """
    config = get_phase_config(phase)
    if config is None:
        return PhaseResult(
            phase=phase,
            success=False,
            error_message=f"未找到阶段配置: {phase}"
        )

    # 检查依赖
    if not can_execute_phase(ctx, phase):
        return PhaseResult(
            phase=phase,
            success=False,
            error_message=f"依赖阶段未完成: {config.depends_on}"
        )

    # 创建日志条目
    log_entry = create_phase_log_entry(
        phase=phase,
        phase_name=config.phase_name,
        skill_used=config.skill_name,
        agent_used=config.agent_name
    )

    try:
        if executor:
            # 使用自定义执行器
            result = executor(ctx, config)
        else:
            # 默认执行逻辑（实际调用由外部实现）
            result = PhaseResult(
                phase=phase,
                success=True,
                output_files=[]
            )

        # 完成日志
        finalize_log_entry(log_entry, "success" if result.success else "failure")
        log_entry.output_files = result.output_files
        log_entry.token_count = result.token_count

    except Exception as e:
        result = PhaseResult(
            phase=phase,
            success=False,
            error_message=str(e)
        )
        finalize_log_entry(log_entry, "failure")
        log_entry.error_message = str(e)

    # 写入日志
    write_audit_log(ctx.log_dir, log_entry)

    # 更新状态
    if result.success:
        update_phase_status(ctx.state_file, phase, completed=True)
        add_audit_log(ctx.state_file, phase, f"phase-{phase}.log", "success")

    return result


def execute_chain(
    ctx: ExecutionContext,
    start_phase: str = 'P3',
    end_phase: str = 'P14',
    executor: Optional[Callable[[ExecutionContext, PhaseConfig], PhaseResult]] = None,
    reviewer: Optional[Callable[[ExecutionContext, str], PhaseResult]] = None
) -> List[PhaseResult]:
    """
    执行阶段链

    Args:
        ctx: 执行上下文
        start_phase: 起始阶段
        end_phase: 结束阶段
        executor: 自定义执行函数
        reviewer: 自定义评审函数

    Returns:
        List[PhaseResult]: 所有阶段的执行结果
    """
    results = []

    # 确定执行范围
    try:
        start_index = YOLO_EXECUTION_ORDER.index(start_phase)
        end_index = YOLO_EXECUTION_ORDER.index(end_phase)
        phases_to_execute = YOLO_EXECUTION_ORDER[start_index:end_index + 1]
    except ValueError:
        return [PhaseResult(phase=start_phase, success=False, error_message="无效的阶段范围")]

    for phase in phases_to_execute:
        # 检查是否可以继续
        if results and not results[-1].success:
            # 前一阶段失败，停止执行
            break

        # 执行阶段
        result = execute_phase(ctx, phase, executor)
        results.append(result)

        if result.success:
            ctx.completed_phases.append(phase)
            ctx.current_phase = phase

    return results


def create_execution_context(
    iteration_name: str,
    docs_dir: str,
    state_file: str
) -> ExecutionContext:
    """
    创建执行上下文

    Args:
        iteration_name: 迭代名称
        docs_dir: 文档目录
        state_file: 状态文件路径

    Returns:
        ExecutionContext: 执行上下文
    """
    log_dir = str(Path(docs_dir) / 'yolo-logs')

    return ExecutionContext(
        iteration_name=iteration_name,
        docs_dir=docs_dir,
        log_dir=log_dir,
        state_file=state_file,
        current_phase='P3',
        completed_phases=[],
        variables={}
    )


def get_execution_summary(results: List[PhaseResult]) -> Dict[str, Any]:
    """
    获取执行摘要

    Args:
        results: 执行结果列表

    Returns:
        Dict: 执行摘要
    """
    total = len(results)
    success = sum(1 for r in results if r.success)
    failed = total - success

    return {
        'total_phases': total,
        'success_count': success,
        'failed_count': failed,
        'success_rate': (success / total * 100) if total > 0 else 0,
        'phases': [r.to_dict() for r in results]
    }
