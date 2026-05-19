"""
YOLO 模式状态管理模块

负责读写和持久化流程状态文件中的 YOLO 模式配置。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import yaml
from pathlib import Path


class YoloStatus(Enum):
    """YOLO 模式状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class CircuitBreakerState:
    """熔断器状态"""
    triggered: bool = False
    reason: Optional[str] = None
    retry_count: int = 0
    triggered_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'triggered': self.triggered,
            'reason': self.reason,
            'retry_count': self.retry_count,
            'triggered_at': _format_datetime(self.triggered_at)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CircuitBreakerState':
        """从字典创建"""
        return cls(
            triggered=data.get('triggered', False),
            reason=data.get('reason'),
            retry_count=data.get('retry_count', 0),
            triggered_at=_parse_datetime(data.get('triggered_at'))
        )


@dataclass
class AuditLogEntry:
    """审计日志条目"""
    phase: str
    log_file: str
    status: str
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'phase': self.phase,
            'log_file': self.log_file,
            'status': self.status,
            'created_at': _format_datetime(self.created_at)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditLogEntry':
        """从字典创建"""
        return cls(
            phase=data.get('phase', ''),
            log_file=data.get('log_file', ''),
            status=data.get('status', ''),
            created_at=_parse_datetime(data.get('created_at'))
        )


@dataclass
class YoloModeConfig:
    """YOLO 模式配置"""
    enabled: bool = False
    status: YoloStatus = YoloStatus.PENDING
    start_time: Optional[datetime] = None
    last_update: Optional[datetime] = None
    completed_phases: List[str] = field(default_factory=list)
    current_phase: Optional[str] = None
    current_attempt: int = 0
    circuit_breaker: CircuitBreakerState = field(default_factory=CircuitBreakerState)
    audit_logs: List[AuditLogEntry] = field(default_factory=list)

    def __post_init__(self):
        """初始化后处理"""
        if self.completed_phases is None:
            self.completed_phases = []
        if self.circuit_breaker is None:
            self.circuit_breaker = CircuitBreakerState()
        if self.audit_logs is None:
            self.audit_logs = []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'enabled': self.enabled,
            'status': self.status.value,
            'start_time': _format_datetime(self.start_time),
            'last_update': _format_datetime(self.last_update),
            'completed_phases': self.completed_phases,
            'current_phase': self.current_phase,
            'current_attempt': self.current_attempt,
            'circuit_breaker': self.circuit_breaker.to_dict(),
            'audit_logs': [log.to_dict() for log in self.audit_logs]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'YoloModeConfig':
        """从字典创建"""
        if not data:
            return cls()

        status_value = data.get('status', 'pending')
        try:
            status = YoloStatus(status_value)
        except ValueError:
            status = YoloStatus.PENDING

        circuit_breaker_data = data.get('circuit_breaker', {})
        audit_logs_data = data.get('audit_logs', [])

        return cls(
            enabled=data.get('enabled', False),
            status=status,
            start_time=_parse_datetime(data.get('start_time')),
            last_update=_parse_datetime(data.get('last_update')),
            completed_phases=data.get('completed_phases', []),
            current_phase=data.get('current_phase'),
            current_attempt=data.get('current_attempt', 0),
            circuit_breaker=CircuitBreakerState.from_dict(circuit_breaker_data),
            audit_logs=[AuditLogEntry.from_dict(log) for log in audit_logs_data]
        )


def _parse_datetime(value: Any) -> Optional[datetime]:
    """解析日期时间字符串"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    return None


def _format_datetime(value: Optional[datetime]) -> Optional[str]:
    """格式化日期时间为字符串"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat().replace('+00:00', 'Z')
    return None


def load_yolo_state(file_path: str) -> YoloModeConfig:
    """
    从流程状态文件加载 YOLO 模式配置

    Args:
        file_path: 流程状态文件路径

    Returns:
        YoloModeConfig: YOLO 模式配置对象
    """
    path = Path(file_path)
    if not path.exists():
        return YoloModeConfig()

    content = path.read_text(encoding='utf-8')

    # 解析 YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                if frontmatter is None:
                    return YoloModeConfig()
                yolo_data = frontmatter.get('yolo_mode', {})
                return YoloModeConfig.from_dict(yolo_data)
            except yaml.YAMLError:
                return YoloModeConfig()

    return YoloModeConfig()


def save_yolo_state(file_path: str, config: YoloModeConfig) -> bool:
    """
    保存 YOLO 模式配置到流程状态文件

    Args:
        file_path: 流程状态文件路径
        config: YOLO 模式配置对象

    Returns:
        bool: 保存是否成功
    """
    path = Path(file_path)

    if not path.exists():
        return False

    content = path.read_text(encoding='utf-8')

    # 更新 last_update
    config.last_update = datetime.now()

    # 构建 YOLO 模式 YAML
    yolo_yaml = {'yolo_mode': config.to_dict()}

    # 更新 frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                frontmatter = {}
            frontmatter.update(yolo_yaml)
            new_content = f"---\n{yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)}---\n{parts[2]}"
            path.write_text(new_content, encoding='utf-8')
            return True

    return False


def update_phase_status(file_path: str, phase: str, completed: bool = False) -> bool:
    """
    更新阶段完成状态

    Args:
        file_path: 流程状态文件路径
        phase: 阶段编号 (如 P3, P4)
        completed: 是否已完成

    Returns:
        bool: 更新是否成功
    """
    config = load_yolo_state(file_path)

    if completed:
        if phase not in config.completed_phases:
            config.completed_phases.append(phase)
    else:
        if phase in config.completed_phases:
            config.completed_phases.remove(phase)

    config.current_phase = phase
    return save_yolo_state(file_path, config)


def set_yolo_status(file_path: str, status: YoloStatus) -> bool:
    """
    设置 YOLO 模式状态

    Args:
        file_path: 流程状态文件路径
        status: YOLO 模式状态

    Returns:
        bool: 设置是否成功
    """
    config = load_yolo_state(file_path)
    config.status = status

    if status == YoloStatus.IN_PROGRESS and config.start_time is None:
        config.start_time = datetime.now()

    return save_yolo_state(file_path, config)


def enable_yolo_mode(file_path: str) -> bool:
    """
    启用 YOLO 模式

    Args:
        file_path: 流程状态文件路径

    Returns:
        bool: 启用是否成功
    """
    config = load_yolo_state(file_path)
    config.enabled = True
    config.status = YoloStatus.IN_PROGRESS
    config.start_time = datetime.now()
    return save_yolo_state(file_path, config)


def disable_yolo_mode(file_path: str) -> bool:
    """
    禁用 YOLO 模式

    Args:
        file_path: 流程状态文件路径

    Returns:
        bool: 禁用是否成功
    """
    config = load_yolo_state(file_path)
    config.enabled = False
    config.status = YoloStatus.PAUSED
    return save_yolo_state(file_path, config)


def check_yolo_status(file_path: str) -> Dict[str, Any]:
    """
    检查 YOLO 模式状态

    Args:
        file_path: 流程状态文件路径

    Returns:
        Dict: YOLO 模式状态信息
    """
    config = load_yolo_state(file_path)
    return {
        'enabled': config.enabled,
        'status': config.status.value,
        'current_phase': config.current_phase,
        'completed_phases': config.completed_phases,
        'circuit_breaker_triggered': config.circuit_breaker.triggered,
        'circuit_breaker_reason': config.circuit_breaker.reason
    }


def add_audit_log(file_path: str, phase: str, log_file: str, status: str) -> bool:
    """
    添加审计日志条目

    Args:
        file_path: 流程状态文件路径
        phase: 阶段编号
        log_file: 日志文件路径
        status: 执行状态

    Returns:
        bool: 添加是否成功
    """
    config = load_yolo_state(file_path)
    entry = AuditLogEntry(
        phase=phase,
        log_file=log_file,
        status=status,
        created_at=datetime.now()
    )
    config.audit_logs.append(entry)
    return save_yolo_state(file_path, config)
