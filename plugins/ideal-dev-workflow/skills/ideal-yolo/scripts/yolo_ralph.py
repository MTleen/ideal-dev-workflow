"""
YOLO Ralph Loop 集成模块

负责生成执行提示、监控执行状态和管理 Ralph Loop 生命周期。
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 添加同级目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from yolo_state import load_yolo_state, YoloStatus
from yolo_orchestrator import get_phase_config, get_next_phase, YOLO_EXECUTION_ORDER


def generate_prompt(state_file: str, output_file: str) -> bool:
    """
    生成执行提示文件

    Args:
        state_file: 流程状态文件路径
        output_file: 输出 PROMPT.md 文件路径

    Returns:
        bool: 是否成功
    """
    config = load_yolo_state(state_file)

    # 获取当前阶段信息
    current_phase = config.current_phase or 'P3'
    phase_config = get_phase_config(current_phase)

    # 构建提示内容
    content = f"""# YOLO 模式执行提示

> 自动生成时间: {datetime.now().isoformat()}

## 当前状态

- YOLO 模式: {'启用' if config.enabled else '禁用'}
- 状态: {config.status.value}
- 当前阶段: {current_phase}
- 已完成阶段: {', '.join(config.completed_phases) or '无'}

## 当前任务

"""

    if phase_config:
        content += f"""
### 阶段: {phase_config.phase} - {phase_config.phase_name}

- 类型: {phase_config.phase_type.value}
- 使用的 Skill: {phase_config.skill_name or 'N/A'}
- 使用的 Agent: {phase_config.agent_name or 'N/A'}

**任务说明**:
请执行 {phase_config.phase} 阶段的任务，使用 {phase_config.skill_name or '相应的 Skill'}。

"""
    else:
        content += """
请继续执行当前阶段的任务。

"""

    # 添加下一阶段预览
    next_phase = get_next_phase(current_phase)
    if next_phase:
        next_config = get_phase_config(next_phase)
        if next_config:
            content += f"""
## 下一阶段预览

- {next_phase}: {next_config.phase_name}

"""

    # 添加熔断状态警告
    if config.circuit_breaker.triggered:
        content += f"""
## ⚠️ 熔断警告

熔断器已触发！原因: {config.circuit_breaker.reason or '未知'}

请检查错误日志并修复问题后，使用 resume_yolo 恢复执行。

"""

    # 添加完成信号说明
    content += """
## 完成信号

任务完成后，请更新流程状态文件中的阶段状态。
如果所有阶段完成，请将状态设置为 `completed`。

<!-- 完成标记: 在所有任务完成后添加 COMPLETED 标记 -->
<!-- COMPLETED -->

---
*此提示由 YOLO Ralph Loop 自动生成*
"""

    # 写入文件
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding='utf-8')

    return True


def get_execution_state(state_file: str) -> Dict[str, Any]:
    """
    获取执行状态快照

    Args:
        state_file: 流程状态文件路径

    Returns:
        Dict: 执行状态
    """
    config = load_yolo_state(state_file)

    return {
        'timestamp': datetime.now().isoformat(),
        'yolo_mode': {
            'enabled': config.enabled,
            'status': config.status.value,
            'current_phase': config.current_phase,
            'completed_phases': config.completed_phases,
        },
        'circuit_breaker': {
            'triggered': config.circuit_breaker.triggered,
            'reason': config.circuit_breaker.reason,
            'retry_count': config.circuit_breaker.retry_count,
        },
        'progress': {
            'total_phases': len(YOLO_EXECUTION_ORDER),
            'completed_count': len(config.completed_phases),
            'percentage': len(config.completed_phases) / len(YOLO_EXECUTION_ORDER) * 100 if YOLO_EXECUTION_ORDER else 0,
        }
    }


def save_state_snapshot(state_file: str, output_file: str) -> bool:
    """
    保存状态快照

    Args:
        state_file: 流程状态文件路径
        output_file: 输出快照文件路径

    Returns:
        bool: 是否成功
    """
    state = get_execution_state(state_file)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8')

    return True


def check_should_continue(state_file: str) -> Dict[str, Any]:
    """
    检查是否应该继续执行

    Args:
        state_file: 流程状态文件路径

    Returns:
        Dict: 检查结果
    """
    config = load_yolo_state(state_file)

    should_continue = True
    reason = None

    # 检查是否启用
    if not config.enabled:
        should_continue = False
        reason = "YOLO 模式未启用"

    # 检查状态
    elif config.status == YoloStatus.COMPLETED:
        should_continue = False
        reason = "YOLO 模式已完成"

    elif config.status == YoloStatus.ERROR:
        should_continue = False
        reason = "YOLO 模式处于错误状态"

    elif config.status == YoloStatus.PAUSED:
        should_continue = False
        reason = "YOLO 模式已暂停"

    # 检查熔断器
    elif config.circuit_breaker.triggered:
        should_continue = False
        reason = f"熔断器已触发: {config.circuit_breaker.reason}"

    return {
        'should_continue': should_continue,
        'reason': reason,
        'current_phase': config.current_phase,
        'status': config.status.value
    }


def send_exit_signal(log_dir: str) -> bool:
    """
    发送退出信号

    Args:
        log_dir: 日志目录路径

    Returns:
        bool: 是否成功
    """
    control_file = Path(log_dir) / '.ralph_control'
    control_file.parent.mkdir(parents=True, exist_ok=True)
    control_file.write_text('EXIT_SIGNAL\n', encoding='utf-8')

    return True


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='YOLO Ralph Loop 工具')
    parser.add_argument('--state-file', required=True, help='流程状态文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--log-dir', help='日志目录路径')

    subparsers = parser.add_subparsers(dest='action', help='操作')

    # generate_prompt
    subparsers.add_parser('generate_prompt', help='生成执行提示')

    # get_state
    subparsers.add_parser('get_state', help='获取执行状态')

    # save_snapshot
    subparsers.add_parser('save_snapshot', help='保存状态快照')

    # check_continue
    subparsers.add_parser('check_continue', help='检查是否应该继续')

    # send_exit
    parser_exit = subparsers.add_parser('send_exit', help='发送退出信号')
    parser_exit.add_argument('--log-dir', required=True, help='日志目录路径')

    args = parser.parse_args()

    if args.action == 'generate_prompt':
        success = generate_prompt(args.state_file, args.output)
        print(f"生成提示: {'成功' if success else '失败'}")
        sys.exit(0 if success else 1)

    elif args.action == 'get_state':
        state = get_execution_state(args.state_file)
        print(json.dumps(state, indent=2, ensure_ascii=False))
        sys.exit(0)

    elif args.action == 'save_snapshot':
        success = save_state_snapshot(args.state_file, args.output)
        print(f"保存快照: {'成功' if success else '失败'}")
        sys.exit(0 if success else 1)

    elif args.action == 'check_continue':
        result = check_should_continue(args.state_file)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result['should_continue'] else 1)

    elif args.action == 'send_exit':
        log_dir = args.log_dir or str(Path(args.output).parent)
        success = send_exit_signal(log_dir)
        print(f"发送退出信号: {'成功' if success else '失败'}")
        sys.exit(0 if success else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
