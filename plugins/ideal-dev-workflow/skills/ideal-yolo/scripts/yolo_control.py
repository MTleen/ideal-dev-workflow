"""
YOLO 模式控制模块

负责管理 YOLO 模式的启用、禁用、切换和状态检查。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
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
    set_yolo_status,
    enable_yolo_mode,
    disable_yolo_mode,
    check_yolo_status as _check_yolo_status
)


class ModeTransition(Enum):
    """模式转换类型"""
    ENABLE = "enable"           # 启用 YOLO 模式
    DISABLE = "disable"         # 禁用 YOLO 模式
    PAUSE = "pause"             # 暂停
    RESUME = "resume"           # 恢复
    COMPLETE = "complete"       # 完成
    ERROR = "error"             # 错误
    RESET = "reset"             # 重置


@dataclass
class TransitionResult:
    """状态转换结果"""
    success: bool
    previous_status: YoloStatus
    new_status: YoloStatus
    message: str
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'previous_status': self.previous_status.value,
            'new_status': self.new_status.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }


# 有效的状态转换
VALID_TRANSITIONS: Dict[YoloStatus, List[YoloStatus]] = {
    YoloStatus.PENDING: [YoloStatus.IN_PROGRESS],
    YoloStatus.IN_PROGRESS: [YoloStatus.PAUSED, YoloStatus.COMPLETED, YoloStatus.ERROR],
    YoloStatus.PAUSED: [YoloStatus.IN_PROGRESS, YoloStatus.ERROR],
    YoloStatus.COMPLETED: [YoloStatus.PENDING],  # 重置
    YoloStatus.ERROR: [YoloStatus.PENDING, YoloStatus.IN_PROGRESS],  # 重试或恢复
}


def can_transition(current: YoloStatus, target: YoloStatus) -> bool:
    """
    检查是否可以从当前状态转换到目标状态

    Args:
        current: 当前状态
        target: 目标状态

    Returns:
        bool: 是否可以转换
    """
    if current == target:
        return True  # 相同状态允许

    valid_targets = VALID_TRANSITIONS.get(current, [])
    return target in valid_targets


def transition_status(file_path: str, target: YoloStatus) -> TransitionResult:
    """
    执行状态转换

    Args:
        file_path: 流程状态文件路径
        target: 目标状态

    Returns:
        TransitionResult: 转换结果
    """
    config = load_yolo_state(file_path)
    current = config.status

    if not can_transition(current, target):
        return TransitionResult(
            success=False,
            previous_status=current,
            new_status=current,
            message=f"无效的状态转换: {current.value} -> {target.value}",
            timestamp=datetime.now()
        )

    # 执行转换
    success = set_yolo_status(file_path, target)

    if success:
        return TransitionResult(
            success=True,
            previous_status=current,
            new_status=target,
            message=f"状态转换成功: {current.value} -> {target.value}",
            timestamp=datetime.now()
        )
    else:
        return TransitionResult(
            success=False,
            previous_status=current,
            new_status=current,
            message="状态保存失败",
            timestamp=datetime.now()
        )


def enable_yolo(file_path: str) -> TransitionResult:
    """
    启用 YOLO 模式

    Args:
        file_path: 流程状态文件路径

    Returns:
        TransitionResult: 转换结果
    """
    config = load_yolo_state(file_path)
    current = config.status

    # 如果已经是启用状态，返回成功
    if config.enabled and config.status == YoloStatus.IN_PROGRESS:
        return TransitionResult(
            success=True,
            previous_status=current,
            new_status=YoloStatus.IN_PROGRESS,
            message="YOLO 模式已启用",
            timestamp=datetime.now()
        )

    success = enable_yolo_mode(file_path)

    return TransitionResult(
        success=success,
        previous_status=current,
        new_status=YoloStatus.IN_PROGRESS if success else current,
        message="YOLO 模式启用成功" if success else "YOLO 模式启用失败",
        timestamp=datetime.now()
    )


def disable_yolo(file_path: str) -> TransitionResult:
    """
    禁用 YOLO 模式（降级到手动模式）

    Args:
        file_path: 流程状态文件路径

    Returns:
        TransitionResult: 转换结果
    """
    config = load_yolo_state(file_path)
    current = config.status

    success = disable_yolo_mode(file_path)

    return TransitionResult(
        success=success,
        previous_status=current,
        new_status=YoloStatus.PAUSED if success else current,
        message="YOLO 模式已禁用，切换到手动模式" if success else "禁用失败",
        timestamp=datetime.now()
    )


def pause_yolo(file_path: str) -> TransitionResult:
    """
    暂停 YOLO 模式

    Args:
        file_path: 流程状态文件路径

    Returns:
        TransitionResult: 转换结果
    """
    return transition_status(file_path, YoloStatus.PAUSED)


def resume_yolo(file_path: str) -> TransitionResult:
    """
    恢复 YOLO 模式

    Args:
        file_path: 流程状态文件路径

    Returns:
        TransitionResult: 转换结果
    """
    config = load_yolo_state(file_path)

    # 确保启用标志为 true
    if not config.enabled:
        return enable_yolo(file_path)

    return transition_status(file_path, YoloStatus.IN_PROGRESS)


def complete_yolo(file_path: str) -> TransitionResult:
    """
    完成 YOLO 模式执行

    Args:
        file_path: 流程状态文件路径

    Returns:
        TransitionResult: 转换结果
    """
    return transition_status(file_path, YoloStatus.COMPLETED)


def error_yolo(file_path: str, reason: str = "") -> TransitionResult:
    """
    将 YOLO 模式标记为错误状态

    Args:
        file_path: 流程状态文件路径
        reason: 错误原因

    Returns:
        TransitionResult: 转换结果
    """
    result = transition_status(file_path, YoloStatus.ERROR)

    if result.success:
        # 更新熔断器状态
        from yolo_state import YoloModeConfig, save_yolo_state
        config = load_yolo_state(file_path)
        config.circuit_breaker.triggered = True
        config.circuit_breaker.reason = reason
        config.circuit_breaker.triggered_at = datetime.now()
        save_yolo_state(file_path, config)

    return result


def reset_yolo(file_path: str) -> TransitionResult:
    """
    重置 YOLO 模式状态

    Args:
        file_path: 流程状态文件路径

    Returns:
        TransitionResult: 转换结果
    """
    config = load_yolo_state(file_path)
    current = config.status

    # 重置为初始状态
    config.enabled = False
    config.status = YoloStatus.PENDING
    config.start_time = None
    config.last_update = datetime.now()
    config.completed_phases = []
    config.current_phase = None
    config.current_attempt = 0
    config.circuit_breaker.triggered = False
    config.circuit_breaker.reason = None
    config.circuit_breaker.retry_count = 0
    config.circuit_breaker.triggered_at = None
    config.audit_logs = []

    success = save_yolo_state(file_path, config)

    return TransitionResult(
        success=success,
        previous_status=current,
        new_status=YoloStatus.PENDING if success else current,
        message="YOLO 模式已重置" if success else "重置失败",
        timestamp=datetime.now()
    )


def check_yolo_status(file_path: str) -> Dict[str, Any]:
    """
    检查 YOLO 模式状态

    Args:
        file_path: 流程状态文件路径

    Returns:
        Dict: 完整的状态信息
    """
    config = load_yolo_state(file_path)

    return {
        'enabled': config.enabled,
        'status': config.status.value,
        'start_time': config.start_time.isoformat() if config.start_time else None,
        'last_update': config.last_update.isoformat() if config.last_update else None,
        'current_phase': config.current_phase,
        'completed_phases': config.completed_phases,
        'current_attempt': config.current_attempt,
        'circuit_breaker': {
            'triggered': config.circuit_breaker.triggered,
            'reason': config.circuit_breaker.reason,
            'retry_count': config.circuit_breaker.retry_count,
            'triggered_at': config.circuit_breaker.triggered_at.isoformat() if config.circuit_breaker.triggered_at else None
        },
        'audit_logs_count': len(config.audit_logs),
        'can_resume': config.status in [YoloStatus.PAUSED, YoloStatus.ERROR],
        'is_active': config.enabled and config.status == YoloStatus.IN_PROGRESS
    }


def should_ask_yolo(file_path: str) -> bool:
    """
    检查是否应该询问用户是否启用 YOLO 模式

    在 P2 评审通过后调用此函数

    Args:
        file_path: 流程状态文件路径

    Returns:
        bool: 是否应该询问
    """
    config = load_yolo_state(file_path)

    # 如果已经启用或曾经启用，不再询问
    if config.enabled:
        return False

    # 如果状态不是 PENDING，不再询问
    if config.status != YoloStatus.PENDING:
        return False

    return True


def get_yolo_summary(file_path: str) -> str:
    """
    获取 YOLO 模式摘要文本

    Args:
        file_path: 流程状态文件路径

    Returns:
        str: 摘要文本
    """
    status = check_yolo_status(file_path)

    if not status['enabled']:
        return "YOLO 模式: 未启用"

    lines = [
        f"YOLO 模式: {status['status']}",
        f"当前阶段: {status['current_phase'] or '未开始'}",
        f"已完成阶段: {', '.join(status['completed_phases']) or '无'}",
    ]

    if status['circuit_breaker']['triggered']:
        lines.append(f"熔断状态: 已触发 ({status['circuit_breaker']['reason']})")

    return "\n".join(lines)
