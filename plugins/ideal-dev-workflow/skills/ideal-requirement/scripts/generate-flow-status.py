#!/usr/bin/env python3
"""
Generate flow status file for requirement tracking.

Creates or updates 流程状态.md with current phase and status.
"""

import sys
from datetime import datetime
from pathlib import Path


def generate_flow_status(output_dir: str, requirement_name: str, created_date: str, phase: str = "P1") -> str:
    """Generate flow status file content.

    Args:
        output_dir: Output directory path
        requirement_name: Name of the requirement
        created_date: Date when the requirement was created (YYYY-MM-DD format)
        phase: Current phase (default: P1)
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = f"""---
需求名称: {requirement_name}
创建日期: {created_date}
---

# 流程状态

## 当前状态

| 配置项 | 值 |
|--------|-----|
| current_phase | {phase} |
| phase_status | in_progress |

## 阶段详情

| 阶段 | 状态 | 开始时间 | 完成时间 |
|------|------|----------|----------|
| P1 需求编写 | 🔄 进行中 | {created_date} | - |
| P2 需求评审 | ⏳ 待开始 | - | - |
| P3 技术方案 | ⏳ 待开始 | - | - |
| P4 方案评审 | ⏳ 待开始 | - | - |
| P5 计划生成 | ⏳ 待开始 | - | - |
| P6 计划评审 | ⏳ 待开始 | - | - |
| P7 测试用例 | ⏳ 待开始 | - | - |
| P8 用例评审 | ⏳ 待开始 | - | - |
| P9 开发执行 | ⏳ 待开始 | - | - |
| P10 代码评审 | ⏳ 待开始 | - | - |
| P11 测试执行 | ⏳ 待开始 | - | - |
| P12 测试评审 | ⏳ 待开始 | - | - |
| P13 维基更新 | ⏳ 待开始 | - | - |
| P14 维基评审 | ⏳ 待开始 | - | - |

## 状态说明

| 状态 | 含义 |
|------|------|
| ⏳ 待开始 | 等待前置阶段完成 |
| 🔄 进行中 | 当前正在执行 |
| ✅ 已完成 | 阶段任务已完成 |
| ❌ 被阻塞 | 遇到问题需要处理 |
| 🔧 需修改 | 评审未通过，需要修改 |

## 下一步

当前正在 **P1 需求编写** 阶段。
完成需求文档后，通知评审人员查看 `P1-需求文档.md`。

---

*创建时间: {created_date}*
*最后更新: {timestamp}*
"""

    return content


def main():
    if len(sys.argv) < 4:
        print("Usage: python generate-flow-status.py <output_dir> <requirement_name> <created_date> [phase]")
        print("Example: python generate-flow-status.py docs/迭代/2026-02-22-用户登录 用户登录 2026-02-22 P1")
        sys.exit(1)

    output_dir = sys.argv[1]
    requirement_name = sys.argv[2]
    created_date = sys.argv[3]
    phase = sys.argv[4] if len(sys.argv) > 4 else "P1"

    output_path = Path(output_dir) / "流程状态.md"

    # Create directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate content
    content = generate_flow_status(output_dir, requirement_name, created_date, phase)

    # Write file
    output_path.write_text(content)

    print(f"✅ Generated: {output_path}")
    print(f"   Requirement: {requirement_name}")
    print(f"   Created Date: {created_date}")
    print(f"   Phase: {phase}")
    print(f"   Status: in_progress")


if __name__ == "__main__":
    main()
