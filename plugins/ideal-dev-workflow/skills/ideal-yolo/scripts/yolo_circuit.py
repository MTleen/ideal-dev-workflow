"""
YOLO 熔断机制模块

负责检测异常情况并触发熔断，暂停执行等待用户介入。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pathlib import Path
import sys

# 添加同级目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from yolo_state import load_yolo_state, save_yolo_state, YoloModeConfig


class CircuitBreakerType(Enum):
    """熔断类型枚举"""
    REVIEW_FAILURE = "review_failure"        # 评审失败
    TEST_FAILURE = "test_failure"            # 测试失败
    REPEATED_ERROR = "repeated_error"        # 重复错误
    TIMEOUT = "timeout"                      # 超时
    MANUAL = "manual"                        # 手动触发


@dataclass
class CircuitCondition:
    """熔断条件"""
    condition_type: CircuitBreakerType
    threshold: int
    current_value: int
    description: str

    def is_triggered(self) -> bool:
        """检查是否触发熔断"""
        return self.current_value >= self.threshold

    def to_dict(self) -> Dict[str, Any]:
        return {
            'condition_type': self.condition_type.value,
            'threshold': self.threshold,
            'current_value': self.current_value,
            'description': self.description,
            'triggered': self.is_triggered()
        }


@dataclass
class CircuitBreakerReport:
    """熔断报告"""
    triggered: bool
    trigger_type: Optional[CircuitBreakerType] = None
    trigger_reason: Optional[str] = None
    trigger_time: Optional[datetime] = None
    conditions: List[CircuitCondition] = field(default_factory=list)
    recovery_suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'triggered': self.triggered,
            'trigger_type': self.trigger_type.value if self.trigger_type else None,
            'trigger_reason': self.trigger_reason,
            'trigger_time': self.trigger_time.isoformat() if self.trigger_time else None,
            'conditions': [c.to_dict() for c in self.conditions],
            'recovery_suggestions': self.recovery_suggestions
        }


# 默认熔断阈值配置
DEFAULT_CIRCUIT_THRESHOLDS = {
    CircuitBreakerType.REVIEW_FAILURE: 3,     # 连续 3 次评审失败
    CircuitBreakerType.TEST_FAILURE: 20,       # 测试通过率 < 80% (20% 失败率)
    CircuitBreakerType.REPEATED_ERROR: 5,     # 同一错误重复 5 次
}


class CircuitBreaker:
    """熔断器"""

    def __init__(
        self,
        thresholds: Optional[Dict[CircuitBreakerType, int]] = None
    ):
        """
        初始化熔断器

        Args:
            thresholds: 自定义阈值配置
        """
        self.thresholds = thresholds or DEFAULT_CIRCUIT_THRESHOLDS.copy()
        self._consecutive_review_failures = 0
        self._test_failure_rate = 0.0
        self._error_counts: Dict[str, int] = {}
        self._triggered = False
        self._trigger_type: Optional[CircuitBreakerType] = None
        self._trigger_reason: Optional[str] = None
        self._trigger_time: Optional[datetime] = None

    def reset(self):
        """重置熔断器状态"""
        self._consecutive_review_failures = 0
        self._test_failure_rate = 0.0
        self._error_counts = {}
        self._triggered = False
        self._trigger_type = None
        self._trigger_reason = None
        self._trigger_time = None

    def record_review_result(self, passed: bool):
        """
        记录评审结果

        Args:
            passed: 评审是否通过
        """
        if passed:
            self._consecutive_review_failures = 0
        else:
            self._consecutive_review_failures += 1

    def record_test_result(self, passed_count: int, total_count: int):
        """
        记录测试结果

        Args:
            passed_count: 通过的测试数
            total_count: 总测试数
        """
        if total_count > 0:
            self._test_failure_rate = (1 - passed_count / total_count) * 100

    def record_error(self, error_message: str):
        """
        记录错误

        Args:
            error_message: 错误信息
        """
        # 简化错误信息作为 key
        error_key = error_message[:100] if len(error_message) > 100 else error_message
        self._error_counts[error_key] = self._error_counts.get(error_key, 0) + 1

    def get_conditions(self) -> List[CircuitCondition]:
        """
        获取所有熔断条件状态

        Returns:
            List[CircuitCondition]: 熔断条件列表
        """
        conditions = []

        # 评审失败条件
        conditions.append(CircuitCondition(
            condition_type=CircuitBreakerType.REVIEW_FAILURE,
            threshold=self.thresholds.get(CircuitBreakerType.REVIEW_FAILURE, 3),
            current_value=self._consecutive_review_failures,
            description=f"连续评审失败次数: {self._consecutive_review_failures}"
        ))

        # 测试失败条件
        test_threshold = self.thresholds.get(CircuitBreakerType.TEST_FAILURE, 20)
        conditions.append(CircuitCondition(
            condition_type=CircuitBreakerType.TEST_FAILURE,
            threshold=test_threshold,
            current_value=int(self._test_failure_rate),
            description=f"测试失败率: {self._test_failure_rate:.1f}%"
        ))

        # 重复错误条件
        max_error_count = max(self._error_counts.values()) if self._error_counts else 0
        conditions.append(CircuitCondition(
            condition_type=CircuitBreakerType.REPEATED_ERROR,
            threshold=self.thresholds.get(CircuitBreakerType.REPEATED_ERROR, 5),
            current_value=max_error_count,
            description=f"最大重复错误次数: {max_error_count}"
        ))

        return conditions

    def check(self) -> CircuitBreakerReport:
        """
        检查是否应触发熔断

        Returns:
            CircuitBreakerReport: 熔断检查报告
        """
        if self._triggered:
            # 已经触发，返回现有报告
            return CircuitBreakerReport(
                triggered=True,
                trigger_type=self._trigger_type,
                trigger_reason=self._trigger_reason,
                trigger_time=self._trigger_time,
                conditions=self.get_conditions(),
                recovery_suggestions=self._get_recovery_suggestions()
            )

        conditions = self.get_conditions()

        for condition in conditions:
            if condition.is_triggered():
                self._triggered = True
                self._trigger_type = condition.condition_type
                self._trigger_reason = condition.description
                self._trigger_time = datetime.now()

                return CircuitBreakerReport(
                    triggered=True,
                    trigger_type=condition.condition_type,
                    trigger_reason=condition.description,
                    trigger_time=self._trigger_time,
                    conditions=conditions,
                    recovery_suggestions=self._get_recovery_suggestions()
                )

        return CircuitBreakerReport(
            triggered=False,
            conditions=conditions
        )

    def _get_recovery_suggestions(self) -> List[str]:
        """获取恢复建议"""
        suggestions = []

        if self._trigger_type == CircuitBreakerType.REVIEW_FAILURE:
            suggestions.append("检查评审标准是否过于严格")
            suggestions.append("手动审查最近的评审失败日志")
            suggestions.append("考虑调整技术方案或代码实现")

        elif self._trigger_type == CircuitBreakerType.TEST_FAILURE:
            suggestions.append("检查失败的测试用例")
            suggestions.append("修复核心功能缺陷")
            suggestions.append("考虑降低测试覆盖率要求")

        elif self._trigger_type == CircuitBreakerType.REPEATED_ERROR:
            suggestions.append("检查重复出现的错误")
            suggestions.append("可能存在系统性问题需要修复")
            suggestions.append("查看错误详情: " + (list(self._error_counts.keys())[0] if self._error_counts else "无"))

        suggestions.append("使用 resume_yolo 恢复执行")
        suggestions.append("使用 reset_yolo 重置状态")

        return suggestions

    def is_triggered(self) -> bool:
        """检查是否已触发熔断"""
        return self._triggered

    def get_max_error(self) -> Optional[str]:
        """获取出现次数最多的错误"""
        if not self._error_counts:
            return None
        return max(self._error_counts.items(), key=lambda x: x[1])[0]


def check_circuit(
    file_path: str,
    circuit_breaker: Optional[CircuitBreaker] = None
) -> CircuitBreakerReport:
    """
    检查是否应触发熔断

    Args:
        file_path: 流程状态文件路径
        circuit_breaker: 熔断器实例（可选）

    Returns:
        CircuitBreakerReport: 熔断检查报告
    """
    if circuit_breaker is None:
        circuit_breaker = CircuitBreaker()

    return circuit_breaker.check()


def trigger_circuit(
    file_path: str,
    reason: str,
    trigger_type: CircuitBreakerType = CircuitBreakerType.MANUAL
) -> bool:
    """
    手动触发熔断

    Args:
        file_path: 流程状态文件路径
        reason: 触发原因
        trigger_type: 触发类型

    Returns:
        bool: 是否成功
    """
    config = load_yolo_state(file_path)

    config.circuit_breaker.triggered = True
    config.circuit_breaker.reason = f"[{trigger_type.value}] {reason}"
    config.circuit_breaker.triggered_at = datetime.now()

    return save_yolo_state(file_path, config)


def clear_circuit(file_path: str) -> bool:
    """
    清除熔断状态

    Args:
        file_path: 流程状态文件路径

    Returns:
        bool: 是否成功
    """
    config = load_yolo_state(file_path)

    config.circuit_breaker.triggered = False
    config.circuit_breaker.reason = None
    config.circuit_breaker.triggered_at = None
    config.circuit_breaker.retry_count += 1

    return save_yolo_state(file_path, config)


def generate_circuit_report(
    report: CircuitBreakerReport,
    output_dir: str
) -> Path:
    """
    生成熔断报告文件

    Args:
        report: 熔断报告
        output_dir: 输出目录

    Returns:
        Path: 报告文件路径
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report_file = output_path / "circuit-breaker-report.md"

    content = f"""# YOLO 熔断报告

## 熔断状态
- 是否触发: {'是 🔴' if report.triggered else '否 🟢'}
- 触发类型: {report.trigger_type.value if report.trigger_type else 'N/A'}
- 触发原因: {report.trigger_reason or 'N/A'}
- 触发时间: {report.trigger_time.isoformat() if report.trigger_time else 'N/A'}

## 熔断条件检查

| 条件类型 | 阈值 | 当前值 | 状态 |
|----------|------|--------|------|
"""

    for condition in report.conditions:
        status = '🔴 触发' if condition.is_triggered() else '🟢 正常'
        content += f"| {condition.condition_type.value} | {condition.threshold} | {condition.current_value} | {status} |\n"

    if report.recovery_suggestions:
        content += "\n## 恢复建议\n\n"
        for i, suggestion in enumerate(report.recovery_suggestions, 1):
            content += f"{i}. {suggestion}\n"

    content += f"""
---
报告生成时间: {datetime.now().isoformat()}
"""

    report_file.write_text(content, encoding='utf-8')
    return report_file


def get_circuit_status(file_path: str) -> Dict[str, Any]:
    """
    获取熔断状态

    Args:
        file_path: 流程状态文件路径

    Returns:
        Dict: 熔断状态信息
    """
    config = load_yolo_state(file_path)

    return {
        'triggered': config.circuit_breaker.triggered,
        'reason': config.circuit_breaker.reason,
        'retry_count': config.circuit_breaker.retry_count,
        'triggered_at': config.circuit_breaker.triggered_at.isoformat() if config.circuit_breaker.triggered_at else None
    }
