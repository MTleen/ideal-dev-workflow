"""
YOLO 中断恢复模块

负责检测执行中断、验证状态完整性并从中断点恢复执行。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import sys

# 添加同级目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from yolo_state import (
    load_yolo_state,
    save_yolo_state,
    set_yolo_status,
    YoloStatus,
    YoloModeConfig
)
from yolo_circuit import clear_circuit, CircuitBreakerType
from yolo_orchestrator import YOLO_EXECUTION_ORDER, get_phase_config


class InterruptType(Enum):
    """中断类型枚举"""
    API_LIMIT = "api_limit"           # API 调用限制
    NETWORK_ERROR = "network_error"   # 网络连接中断
    PROCESS_KILLED = "process_killed" # 进程异常终止
    RESOURCE_EXHAUSTED = "resource_exhausted"  # 系统资源不足
    UNKNOWN = "unknown"               # 未知原因


class RecoveryStatus(Enum):
    """恢复状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class InterruptInfo:
    """中断信息"""
    detected: bool
    interrupt_type: Optional[InterruptType] = None
    detected_at: Optional[datetime] = None
    last_successful_phase: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'detected': self.detected,
            'interrupt_type': self.interrupt_type.value if self.interrupt_type else None,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'last_successful_phase': self.last_successful_phase,
            'message': self.message
        }


@dataclass
class ValidationResult:
    """状态验证结果"""
    valid: bool
    missing_phases: List[str] = field(default_factory=list)
    incomplete_outputs: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'valid': self.valid,
            'missing_phases': self.missing_phases,
            'incomplete_outputs': self.incomplete_outputs,
            'warnings': self.warnings
        }


@dataclass
class RecoveryResult:
    """恢复结果"""
    success: bool
    status: RecoveryStatus
    resumed_from_phase: Optional[str] = None
    message: str = ""
    recovery_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'status': self.status.value,
            'resumed_from_phase': self.resumed_from_phase,
            'message': self.message,
            'recovery_time': self.recovery_time.isoformat() if self.recovery_time else None
        }


# 中断检测阈值
INTERRUPT_DETECTION_THRESHOLD = timedelta(minutes=10)  # 10 分钟未更新视为中断


def detect_interrupt(state_file: str) -> InterruptInfo:
    """
    检测执行中断

    Args:
        state_file: 流程状态文件路径

    Returns:
        InterruptInfo: 中断信息
    """
    config = load_yolo_state(state_file)

    # 如果未启用或已完成，不算中断
    if not config.enabled:
        return InterruptInfo(detected=False, message="YOLO 模式未启用")

    if config.status == YoloStatus.COMPLETED:
        return InterruptInfo(detected=False, message="YOLO 模式已完成")

    # 如果状态是暂停或错误，可能是主动中断
    if config.status in [YoloStatus.PAUSED, YoloStatus.ERROR]:
        return InterruptInfo(
            detected=True,
            interrupt_type=InterruptType.PROCESS_KILLED,
            detected_at=datetime.now(),
            last_successful_phase=config.completed_phases[-1] if config.completed_phases else None,
            message=f"YOLO 模式处于 {config.status.value} 状态"
        )

    # 检查最后更新时间
    if config.last_update:
        time_since_update = datetime.now() - config.last_update

        if time_since_update > INTERRUPT_DETECTION_THRESHOLD:
            # 根据时间判断中断类型
            if time_since_update > timedelta(hours=5):
                interrupt_type = InterruptType.API_LIMIT
            elif time_since_update > timedelta(hours=1):
                interrupt_type = InterruptType.NETWORK_ERROR
            else:
                interrupt_type = InterruptType.UNKNOWN

            return InterruptInfo(
                detected=True,
                interrupt_type=interrupt_type,
                detected_at=datetime.now(),
                last_successful_phase=config.completed_phases[-1] if config.completed_phases else None,
                message=f"超过 {time_since_update} 未更新状态"
            )

    # 正在执行中，不算中断
    if config.status == YoloStatus.IN_PROGRESS:
        return InterruptInfo(detected=False, message="YOLO 模式正在执行中")

    return InterruptInfo(detected=False)


def validate_state(state_file: str, docs_dir: str) -> ValidationResult:
    """
    验证状态完整性

    Args:
        state_file: 流程状态文件路径
        docs_dir: 文档目录路径

    Returns:
        ValidationResult: 验证结果
    """
    config = load_yolo_state(state_file)
    result = ValidationResult(valid=True)

    # 检查已完成阶段的输出文件
    expected_files = {
        'P3': 'P3-技术方案.md',
        'P5': 'P5-编码计划.md',
        'P7': 'P7-测试用例.md',
        'P11': 'P11-测试报告.md',
        'P13': 'Wiki/',  # Wiki 目录
    }

    docs_path = Path(docs_dir)

    for phase in config.completed_phases:
        # 执行阶段检查输出文件
        if phase in expected_files:
            expected = expected_files[phase]
            file_path = docs_path / expected

            if not file_path.exists():
                result.incomplete_outputs.append(f"{phase}: 缺少 {expected}")
                result.valid = False

    # 检查阶段顺序完整性
    if config.completed_phases:
        for i, phase in enumerate(config.completed_phases):
            if phase in YOLO_EXECUTION_ORDER:
                phase_index = YOLO_EXECUTION_ORDER.index(phase)
                # 检查前面的阶段是否都完成了
                for prev_phase in YOLO_EXECUTION_ORDER[:phase_index]:
                    if prev_phase not in config.completed_phases:
                        result.missing_phases.append(prev_phase)
                        result.warnings.append(f"阶段 {prev_phase} 应在 {phase} 之前完成")

    # 如果有缺失阶段但状态显示已完成，可能是状态不一致
    if result.missing_phases and config.status == YoloStatus.COMPLETED:
        result.valid = False

    return result


def get_resume_phase(state_file: str) -> Optional[str]:
    """
    获取应该恢复执行的阶段

    Args:
        state_file: 流程状态文件路径

    Returns:
        str: 应该执行的阶段编号
    """
    config = load_yolo_state(state_file)

    # 如果有当前阶段且未完成，从当前阶段继续
    if config.current_phase and config.current_phase not in config.completed_phases:
        return config.current_phase

    # 否则找下一个未完成的阶段
    for phase in YOLO_EXECUTION_ORDER:
        if phase not in config.completed_phases:
            return phase

    # 所有阶段都完成了
    return None


def resume_execution(state_file: str, docs_dir: str) -> RecoveryResult:
    """
    恢复执行

    Args:
        state_file: 流程状态文件路径
        docs_dir: 文档目录路径

    Returns:
        RecoveryResult: 恢复结果
    """
    # 检测中断
    interrupt_info = detect_interrupt(state_file)

    if not interrupt_info.detected:
        return RecoveryResult(
            success=False,
            status=RecoveryStatus.FAILED,
            message="未检测到中断状态"
        )

    # 验证状态
    validation = validate_state(state_file, docs_dir)

    if not validation.valid:
        return RecoveryResult(
            success=False,
            status=RecoveryStatus.FAILED,
            message=f"状态验证失败: {validation.incomplete_outputs}"
        )

    # 获取恢复点
    resume_phase = get_resume_phase(state_file)

    if resume_phase is None:
        return RecoveryResult(
            success=False,
            status=RecoveryStatus.FAILED,
            message="所有阶段已完成，无需恢复"
        )

    # 清除熔断状态
    clear_circuit(state_file)

    # 设置状态为进行中
    set_yolo_status(state_file, YoloStatus.IN_PROGRESS)

    # 记录恢复事件
    config = load_yolo_state(state_file)
    config.current_phase = resume_phase
    save_yolo_state(state_file, config)

    return RecoveryResult(
        success=True,
        status=RecoveryStatus.IN_PROGRESS,
        resumed_from_phase=resume_phase,
        message=f"已从阶段 {resume_phase} 恢复执行",
        recovery_time=datetime.now()
    )


def generate_recovery_report(
    state_file: str,
    docs_dir: str,
    output_dir: str
) -> Path:
    """
    生成恢复报告

    Args:
        state_file: 流程状态文件路径
        docs_dir: 文档目录路径
        output_dir: 输出目录路径

    Returns:
        Path: 报告文件路径
    """
    interrupt_info = detect_interrupt(state_file)
    validation = validate_state(state_file, docs_dir)
    resume_phase = get_resume_phase(state_file)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report_file = output_path / "recovery-report.md"

    content = f"""# YOLO 中断恢复报告

## 中断检测

- 检测到中断: {'是' if interrupt_info.detected else '否'}
- 中断类型: {interrupt_info.interrupt_type.value if interrupt_info.interrupt_type else 'N/A'}
- 检测时间: {interrupt_info.detected_at.isoformat() if interrupt_info.detected_at else 'N/A'}
- 最后成功阶段: {interrupt_info.last_successful_phase or 'N/A'}
- 消息: {interrupt_info.message or 'N/A'}

## 状态验证

- 验证通过: {'是' if validation.valid else '否'}
- 缺失阶段: {', '.join(validation.missing_phases) or '无'}
- 不完整输出: {', '.join(validation.incomplete_outputs) or '无'}
- 警告: {len(validation.warnings)} 条

## 恢复建议

"""

    if interrupt_info.detected:
        content += f"""
1. 恢复起始阶段: {resume_phase or '已完成'}
2. 使用 `resume_yolo` 命令恢复执行
3. 或手动执行以下命令：
   - 调用 `ideal-yolo` skill
   - 从阶段 {resume_phase} 开始执行

"""
    else:
        content += "\n当前未检测到中断，无需恢复。\n"

    content += f"""
---
报告生成时间: {datetime.now().isoformat()}
"""

    report_file.write_text(content, encoding='utf-8')
    return report_file


def check_recovery_conditions(state_file: str) -> Dict[str, Any]:
    """
    检查恢复条件是否满足

    Args:
        state_file: 流程状态文件路径

    Returns:
        Dict: 检查结果
    """
    config = load_yolo_state(state_file)

    conditions = {
        'can_recover': True,
        'reasons': [],
        'recommendations': []
    }

    # 检查是否启用
    if not config.enabled:
        conditions['can_recover'] = False
        conditions['reasons'].append("YOLO 模式未启用")
        conditions['recommendations'].append("先启用 YOLO 模式")

    # 检查熔断状态
    if config.circuit_breaker.triggered:
        conditions['reasons'].append(f"熔断器已触发: {config.circuit_breaker.reason}")
        conditions['recommendations'].append("解决熔断原因后使用 clear_circuit")

    # 检查是否已完成
    if config.status == YoloStatus.COMPLETED:
        conditions['can_recover'] = False
        conditions['reasons'].append("YOLO 模式已完成")
        conditions['recommendations'].append("无需恢复")

    return conditions
