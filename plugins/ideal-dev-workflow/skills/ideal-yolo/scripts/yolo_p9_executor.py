"""
YOLO P9 逐故事执行模块

负责 P9 阶段的逐故事执行逻辑，实现上下文隔离的原子化任务执行。

核心功能：
- 读取故事索引，识别待执行故事
- 检查依赖关系，确定可执行故事
- 为每个故事生成 Task Prompt
- 更新故事状态
- 合并所有故事结果
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from enum import Enum
import re
import yaml


class StoryStatus(Enum):
    """故事状态枚举"""
    PENDING = "pending"          # 待开始 (⏳)
    IN_PROGRESS = "in_progress"  # 进行中 (🔄)
    COMPLETED = "completed"      # 已完成 (✅)
    FAILED = "failed"            # 失败 (❌)


# 状态图标映射
STATUS_ICONS = {
    StoryStatus.PENDING: "⏳",
    StoryStatus.IN_PROGRESS: "🔄",
    StoryStatus.COMPLETED: "✅",
    StoryStatus.FAILED: "❌"
}

# 图标到状态的反向映射
ICON_TO_STATUS = {v: k for k, v in STATUS_ICONS.items()}


@dataclass
class StoryInfo:
    """故事信息数据类"""
    story_id: str
    title: str
    status: StoryStatus
    file_path: str
    depends_on: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'story_id': self.story_id,
            'title': self.title,
            'status': self.status.value,
            'status_icon': STATUS_ICONS.get(self.status, "⏳"),
            'file_path': self.file_path,
            'depends_on': self.depends_on
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryInfo':
        """从字典创建"""
        status_value = data.get('status', 'pending')
        try:
            status = StoryStatus(status_value)
        except ValueError:
            status = StoryStatus.PENDING

        return cls(
            story_id=data.get('story_id', ''),
            title=data.get('title', ''),
            status=status,
            file_path=data.get('file_path', ''),
            depends_on=data.get('depends_on', [])
        )


@dataclass
class StoryResult:
    """故事执行结果数据类"""
    story_id: str
    success: bool
    summary: str = ""
    output_files: List[str] = field(default_factory=list)
    key_changes: List[str] = field(default_factory=list)
    tests_passed: Optional[bool] = None
    error_message: Optional[str] = None
    token_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'story_id': self.story_id,
            'success': self.success,
            'summary': self.summary,
            'output_files': self.output_files,
            'key_changes': self.key_changes,
            'tests_passed': self.tests_passed,
            'error_message': self.error_message,
            'token_count': self.token_count
        }


@dataclass
class StoryIndex:
    """故事索引数据类"""
    requirement: str
    total_stories: int
    completed: int
    current: Optional[str]
    stories: List[StoryInfo] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'requirement': self.requirement,
            'total_stories': self.total_stories,
            'completed': self.completed,
            'current': self.current,
            'stories': [s.to_dict() for s in self.stories]
        }


def parse_stories_index(stories_dir: str) -> Optional[StoryIndex]:
    """
    解析 stories/index.md 文件

    Args:
        stories_dir: stories 目录路径

    Returns:
        StoryIndex: 解析后的故事索引，失败返回 None
    """
    index_path = Path(stories_dir) / "index.md"
    if not index_path.exists():
        return None

    content = index_path.read_text(encoding='utf-8')

    # 解析 YAML frontmatter
    frontmatter = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                pass

    # 解析故事列表
    stories = _parse_story_table(content)

    return StoryIndex(
        requirement=frontmatter.get('requirement', ''),
        total_stories=frontmatter.get('total_stories', len(stories)),
        completed=frontmatter.get('completed', 0),
        current=frontmatter.get('current'),
        stories=stories
    )


def _parse_story_table(content: str) -> List[StoryInfo]:
    """
    从 index.md 内容中解析故事表格

    Args:
        content: index.md 文件内容

    Returns:
        List[StoryInfo]: 故事信息列表
    """
    stories = []

    # 匹配表格行：| [001](001-xxx.md) | 标题 | 状态 | 依赖 |
    table_pattern = r'\|\s*\[(\d+)\]\(([^)]+)\)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]*)\s*\|'
    matches = re.findall(table_pattern, content)

    for match in matches:
        story_id = match[0]
        file_path = match[1]
        title = match[2].strip()
        status_str = match[3].strip()
        depends_str = match[4].strip()

        # 解析状态
        status = _parse_status(status_str)

        # 解析依赖
        depends_on = []
        if depends_str and depends_str != '-':
            depends_on = [d.strip() for d in depends_str.split(',') if d.strip()]

        stories.append(StoryInfo(
            story_id=story_id,
            title=title,
            status=status,
            file_path=file_path,
            depends_on=depends_on
        ))

    return stories


def _parse_status(status_str: str) -> StoryStatus:
    """
    解析状态字符串

    支持格式：
    - 图标格式：⏳ 待开始, 🔄 进行中, ✅ 已完成, ❌ 失败
    - 纯文本：pending, in_progress, completed, failed

    Args:
        status_str: 状态字符串

    Returns:
        StoryStatus: 状态枚举值
    """
    status_str = status_str.strip()

    # 检查图标
    for icon, status in ICON_TO_STATUS.items():
        if icon in status_str:
            return status

    # 检查文本
    status_lower = status_str.lower()
    if 'pending' in status_lower or '待开始' in status_str:
        return StoryStatus.PENDING
    elif 'progress' in status_lower or '进行中' in status_str:
        return StoryStatus.IN_PROGRESS
    elif 'completed' in status_lower or '完成' in status_str:
        return StoryStatus.COMPLETED
    elif 'failed' in status_lower or '失败' in status_str:
        return StoryStatus.FAILED

    return StoryStatus.PENDING


def get_pending_stories(stories_dir: str) -> List[StoryInfo]:
    """
    获取待执行故事列表

    返回所有状态为 pending 且依赖已满足的故事。

    Args:
        stories_dir: stories 目录路径

    Returns:
        List[StoryInfo]: 可执行的故事列表（按依赖顺序排序）
    """
    index = parse_stories_index(stories_dir)
    if not index:
        return []

    # 构建状态映射
    status_map = {s.story_id: s.status for s in index.stories}

    # 筛选待执行且依赖满足的故事
    pending_stories = []
    for story in index.stories:
        if story.status != StoryStatus.PENDING:
            continue

        # 检查依赖
        deps_satisfied = True
        for dep_id in story.depends_on:
            dep_status = status_map.get(dep_id, StoryStatus.PENDING)
            if dep_status != StoryStatus.COMPLETED:
                deps_satisfied = False
                break

        if deps_satisfied:
            pending_stories.append(story)

    return pending_stories


def get_next_executable_story(stories_dir: str) -> Optional[StoryInfo]:
    """
    获取下一个可执行的故事

    Args:
        stories_dir: stories 目录路径

    Returns:
        StoryInfo: 下一个可执行的故事，没有则返回 None
    """
    pending = get_pending_stories(stories_dir)
    return pending[0] if pending else None


def get_in_progress_story(stories_dir: str) -> Optional[StoryInfo]:
    """
    获取当前进行中的故事

    Args:
        stories_dir: stories 目录路径

    Returns:
        StoryInfo: 进行中的故事，没有则返回 None
    """
    index = parse_stories_index(stories_dir)
    if not index:
        return None

    for story in index.stories:
        if story.status == StoryStatus.IN_PROGRESS:
            return story

    return None


def update_story_status(stories_dir: str, story_id: str, status: StoryStatus) -> bool:
    """
    更新故事状态

    更新 stories/index.md 中指定故事的状态。

    Args:
        stories_dir: stories 目录路径
        story_id: 故事 ID
        status: 新状态

    Returns:
        bool: 更新是否成功
    """
    index_path = Path(stories_dir) / "index.md"
    if not index_path.exists():
        return False

    content = index_path.read_text(encoding='utf-8')

    # 获取状态图标和文本
    icon = STATUS_ICONS.get(status, "⏳")
    status_text = {
        StoryStatus.PENDING: "待开始",
        StoryStatus.IN_PROGRESS: "进行中",
        StoryStatus.COMPLETED: "已完成",
        StoryStatus.FAILED: "失败"
    }.get(status, "待开始")

    new_status_str = f"{icon} {status_text}"

    # 更新表格中的状态
    # 匹配：| [story_id](...) | 标题 | 旧状态 | 依赖 |
    pattern = rf'(\|\s*\[{story_id}\]\([^)]+\)\s*\|\s*[^|]+\|\s*)([^|]+)(\s*\|\s*[^|]*\s*\|)'
    replacement = rf'\1{new_status_str}\3'
    new_content = re.sub(pattern, replacement, content)

    if new_content == content:
        # 没有匹配到，可能格式不同
        return False

    # 更新 frontmatter 中的 current 和 completed
    if content.startswith('---'):
        parts = new_content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                frontmatter = {}

            # 更新 current
            if status == StoryStatus.IN_PROGRESS:
                frontmatter['current'] = story_id
            elif status == StoryStatus.COMPLETED or status == StoryStatus.FAILED:
                # 如果当前故事完成或失败，清空 current
                if frontmatter.get('current') == story_id:
                    frontmatter['current'] = None

            # 更新 completed 计数
            if status == StoryStatus.COMPLETED:
                # 重新计算已完成数量
                index = parse_stories_index(stories_dir)
                if index:
                    completed_count = sum(1 for s in index.stories
                                         if s.story_id == story_id or s.status == StoryStatus.COMPLETED)
                    frontmatter['completed'] = completed_count

            # 重新构建文件内容
            new_content = f"---\n{yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)}---{parts[2]}"

    # 写入文件
    index_path.write_text(new_content, encoding='utf-8')
    return True


def set_story_in_progress(stories_dir: str, story_id: str) -> bool:
    """
    将故事状态设置为进行中

    Args:
        stories_dir: stories 目录路径
        story_id: 故事 ID

    Returns:
        bool: 设置是否成功
    """
    return update_story_status(stories_dir, story_id, StoryStatus.IN_PROGRESS)


def set_story_completed(stories_dir: str, story_id: str) -> bool:
    """
    将故事状态设置为已完成

    Args:
        stories_dir: stories 目录路径
        story_id: 故事 ID

    Returns:
        bool: 设置是否成功
    """
    return update_story_status(stories_dir, story_id, StoryStatus.COMPLETED)


def set_story_failed(stories_dir: str, story_id: str) -> bool:
    """
    将故事状态设置为失败

    Args:
        stories_dir: stories 目录路径
        story_id: 故事 ID

    Returns:
        bool: 设置是否成功
    """
    return update_story_status(stories_dir, story_id, StoryStatus.FAILED)


def build_p9_story_context(story: StoryInfo, docs_dir: str) -> Dict[str, Any]:
    """
    构建 P9 故事执行的上下文

    Args:
        story: 故事信息
        docs_dir: 文档目录

    Returns:
        Dict: 上下文字典，用于 build_task_prompt
    """
    return {
        'story_id': story.story_id,
        'story_title': story.title,
        'story_file': f"stories/{story.file_path}",
        'docs_dir': docs_dir
    }


def merge_story_results(results: List[StoryResult]) -> Dict[str, Any]:
    """
    合并所有故事结果

    Args:
        results: 各故事的执行结果

    Returns:
        Dict: 合并后的结果摘要
    """
    if not results:
        return {
            'success': False,
            'total_stories': 0,
            'completed_stories': 0,
            'failed_stories': 0,
            'summary': '没有故事执行结果',
            'output_files': [],
            'key_changes': [],
            'total_tokens': 0
        }

    success_count = sum(1 for r in results if r.success)
    total_count = len(results)
    failed_count = total_count - success_count
    total_tokens = sum(r.token_count for r in results)

    # 合并输出文件和关键变更
    all_output_files = []
    all_key_changes = []
    for r in results:
        all_output_files.extend(r.output_files)
        all_key_changes.extend(r.key_changes)

    # 去重
    all_output_files = list(set(all_output_files))
    all_key_changes = all_key_changes[:10]  # 限制数量

    # 测试通过状态
    tests_passed = all(r.tests_passed for r in results if r.tests_passed is not None)

    return {
        'success': failed_count == 0,
        'total_stories': total_count,
        'completed_stories': success_count,
        'failed_stories': failed_count,
        'summary': f"完成 {success_count}/{total_count} 个故事",
        'output_files': all_output_files,
        'key_changes': all_key_changes,
        'tests_passed': tests_passed,
        'total_tokens': total_tokens,
        'failed_story_ids': [r.story_id for r in results if not r.success]
    }


def get_story_execution_summary(stories_dir: str) -> Dict[str, Any]:
    """
    获取故事执行摘要

    Args:
        stories_dir: stories 目录路径

    Returns:
        Dict: 执行摘要
    """
    index = parse_stories_index(stories_dir)
    if not index:
        return {
            'total_stories': 0,
            'completed': 0,
            'pending': 0,
            'in_progress': 0,
            'failed': 0,
            'current': None
        }

    status_counts = {
        StoryStatus.PENDING: 0,
        StoryStatus.IN_PROGRESS: 0,
        StoryStatus.COMPLETED: 0,
        StoryStatus.FAILED: 0
    }

    for story in index.stories:
        status_counts[story.status] = status_counts.get(story.status, 0) + 1

    return {
        'total_stories': index.total_stories,
        'completed': status_counts[StoryStatus.COMPLETED],
        'pending': status_counts[StoryStatus.PENDING],
        'in_progress': status_counts[StoryStatus.IN_PROGRESS],
        'failed': status_counts[StoryStatus.FAILED],
        'current': index.current,
        'stories': [s.to_dict() for s in index.stories]
    }


def check_all_stories_completed(stories_dir: str) -> bool:
    """
    检查所有故事是否已完成

    Args:
        stories_dir: stories 目录路径

    Returns:
        bool: 是否全部完成
    """
    index = parse_stories_index(stories_dir)
    if not index:
        return False

    for story in index.stories:
        if story.status != StoryStatus.COMPLETED:
            return False

    return True


def get_stories_for_p9_execution(stories_dir: str) -> Tuple[Optional[StoryInfo], List[StoryInfo]]:
    """
    获取 P9 执行所需的故事信息

    返回当前应该执行的故事和所有待执行故事。
    用于 P9 编排器决定执行顺序。

    Args:
        stories_dir: stories 目录路径

    Returns:
        Tuple[Optional[StoryInfo], List[StoryInfo]]:
            - 当前应执行的故事（可能是进行中或下一个待执行的）
            - 所有待执行故事列表
    """
    # 先检查是否有进行中的故事
    in_progress = get_in_progress_story(stories_dir)
    if in_progress:
        # 有进行中的故事，继续执行它
        pending = get_pending_stories(stories_dir)
        return in_progress, pending

    # 没有进行中的故事，获取下一个待执行的
    pending = get_pending_stories(stories_dir)
    if pending:
        return pending[0], pending

    # 没有待执行的故事
    return None, []


# ============== 导出 ==============

__all__ = [
    # 枚举
    'StoryStatus',
    # 数据类
    'StoryInfo',
    'StoryResult',
    'StoryIndex',
    # 常量
    'STATUS_ICONS',
    'ICON_TO_STATUS',
    # 核心函数
    'parse_stories_index',
    'get_pending_stories',
    'get_next_executable_story',
    'get_in_progress_story',
    'update_story_status',
    'set_story_in_progress',
    'set_story_completed',
    'set_story_failed',
    'build_p9_story_context',
    'merge_story_results',
    'get_story_execution_summary',
    'check_all_stories_completed',
    'get_stories_for_p9_execution',
]
