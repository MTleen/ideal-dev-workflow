"""
YOLO Task 结果解析模块

负责解析 Task 返回的 JSON 摘要，验证格式和大小限制。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import re


@dataclass
class TaskResult:
    """Task 执行结果数据类"""
    success: bool
    phase: str
    output_files: List[str] = field(default_factory=list)
    summary: str = ""
    error_message: Optional[str] = None

    # 执行阶段专用字段
    key_decisions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    # 评审阶段专用字段
    review_passed: Optional[bool] = None
    review_score: float = 0.0
    review_comments: List[str] = field(default_factory=list)
    review_suggestions: List[str] = field(default_factory=list)

    # P9 专用字段
    story_id: Optional[str] = None
    key_changes: List[str] = field(default_factory=list)
    tests_passed: Optional[bool] = None

    # P11 专用字段
    test_results: Dict[str, Any] = field(default_factory=dict)

    # P13 专用字段
    wiki_sections_updated: List[str] = field(default_factory=list)

    # 元数据
    token_count: int = 0
    parsed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'success': self.success,
            'phase': self.phase,
            'output_files': self.output_files,
            'summary': self.summary,
            'error_message': self.error_message,
            'key_decisions': self.key_decisions,
            'risks': self.risks,
            'metrics': self.metrics,
            'token_count': self.token_count,
            'parsed_at': self.parsed_at.isoformat()
        }

        if self.review_passed is not None:
            result['review_passed'] = self.review_passed
            result['review_score'] = self.review_score
            result['review_comments'] = self.review_comments
            result['review_suggestions'] = self.review_suggestions

        if self.story_id:
            result['story_id'] = self.story_id
            result['key_changes'] = self.key_changes
            result['tests_passed'] = self.tests_passed

        if self.test_results:
            result['test_results'] = self.test_results

        if self.wiki_sections_updated:
            result['wiki_sections_updated'] = self.wiki_sections_updated

        return result

    def is_review(self) -> bool:
        """检查是否为评审结果"""
        return self.review_passed is not None

    def get_pass_rate(self) -> Optional[float]:
        """获取测试通过率（仅 P11）"""
        if self.test_results and 'pass_rate' in self.test_results:
            return self.test_results['pass_rate']
        return None


@dataclass
class ParseResult:
    """解析结果"""
    success: bool
    result: Optional[TaskResult] = None
    error: Optional[str] = None
    raw_output: str = ""
    token_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'result': self.result.to_dict() if self.result else None,
            'error': self.error,
            'token_count': self.token_count
        }


# 返回预算限制（tokens）
RETURN_BUDGET_LIMITS = {
    'P3': 3000, 'P4': 2000,
    'P5': 3000, 'P6': 2000,
    'P7': 3000, 'P8': 2000,
    'P9': 3000, 'P10': 2000,
    'P11': 3000, 'P12': 2000,
    'P13': 3000, 'P14': 2000,
}


def parse_task_result(phase: str, raw_output: str) -> ParseResult:
    """
    解析 Task 返回结果

    Args:
        phase: 阶段编号
        raw_output: Task 返回的原始输出

    Returns:
        ParseResult: 解析结果
    """
    if not raw_output:
        return ParseResult(
            success=False,
            error="Task 返回为空",
            raw_output=raw_output
        )

    # 提取 JSON
    json_data = extract_json_from_output(raw_output)
    if not json_data:
        return ParseResult(
            success=False,
            error="无法从输出中提取 JSON",
            raw_output=raw_output
        )

    try:
        # 估算 token 数量
        token_count = estimate_token_count(raw_output)

        # 验证返回大小
        budget_limit = RETURN_BUDGET_LIMITS.get(phase, 3000)
        if token_count > budget_limit * 1.5:  # 允许 50% 的容差
            # 截断处理
            json_data = truncate_result(json_data, budget_limit)

        # 构建结果对象
        result = build_task_result(phase, json_data)
        result.token_count = token_count

        return ParseResult(
            success=True,
            result=result,
            raw_output=raw_output,
            token_count=token_count
        )

    except Exception as e:
        return ParseResult(
            success=False,
            error=f"解析失败: {str(e)}",
            raw_output=raw_output
        )


def extract_json_from_output(output: str) -> Optional[Dict[str, Any]]:
    """
    从输出中提取 JSON

    支持：
    1. 纯 JSON 输出
    2. Markdown 代码块中的 JSON
    3. 文本中嵌入的 JSON

    Args:
        output: 原始输出

    Returns:
        Dict: 解析的 JSON 对象，失败返回 None
    """
    if not output:
        return None

    # 方法 1: 尝试直接解析整个输出
    try:
        return json.loads(output.strip())
    except json.JSONDecodeError:
        pass

    # 方法 2: 从 Markdown 代码块中提取
    code_block_pattern = r'```(?:json)?\s*\n([\s\S]*?)\n```'
    matches = re.findall(code_block_pattern, output)
    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue

    # 方法 3: 查找 JSON 对象模式
    json_pattern = r'\{[\s\S]*"success"\s*:\s*(?:true|false)[\s\S]*\}'
    matches = re.findall(json_pattern, output)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    # 方法 4: 从第一个 { 到最后一个 }
    start = output.find('{')
    end = output.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(output[start:end+1])
        except json.JSONDecodeError:
            pass

    return None


def build_task_result(phase: str, data: Dict[str, Any]) -> TaskResult:
    """
    构建 TaskResult 对象

    Args:
        phase: 阶段编号
        data: 解析的 JSON 数据

    Returns:
        TaskResult: 结果对象
    """
    result = TaskResult(
        success=data.get('success', False),
        phase=data.get('phase', phase),
        output_files=data.get('output_files', []),
        summary=data.get('summary', ''),
        error_message=data.get('error_message'),
        key_decisions=data.get('key_decisions', []),
        risks=data.get('risks', []),
        metrics=data.get('metrics', {}),
    )

    # 评审阶段字段
    if 'review_passed' in data:
        result.review_passed = data.get('review_passed')
        result.review_score = data.get('review_score', 0.0)
        result.review_comments = data.get('review_comments', [])
        result.review_suggestions = data.get('review_suggestions', [])

    # P9 专用字段
    if 'story_id' in data:
        result.story_id = data.get('story_id')
        result.key_changes = data.get('key_changes', [])
        result.tests_passed = data.get('tests_passed')

    # P11 专用字段
    if 'test_results' in data:
        result.test_results = data.get('test_results', {})

    # P13 专用字段
    if 'wiki_sections_updated' in data:
        result.wiki_sections_updated = data.get('wiki_sections_updated', [])

    return result


def estimate_token_count(text: str) -> int:
    """
    估算文本的 token 数量

    使用简单的启发式方法：
    - 英文: ~4 字符 = 1 token
    - 中文: ~2 字符 = 1 token

    Args:
        text: 输入文本

    Returns:
        int: 估算的 token 数量
    """
    if not text:
        return 0

    # 分离中文和非中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    non_chinese_chars = len(text) - chinese_chars

    # 估算
    chinese_tokens = chinese_chars / 2
    non_chinese_tokens = non_chinese_chars / 4

    return int(chinese_tokens + non_chinese_tokens)


def truncate_result(data: Dict[str, Any], budget: int) -> Dict[str, Any]:
    """
    截断结果以满足预算限制

    Args:
        data: 原始数据
        budget: token 预算

    Returns:
        Dict: 截断后的数据
    """
    result = data.copy()

    # 截断摘要
    if 'summary' in result and len(result['summary']) > 200:
        result['summary'] = result['summary'][:200] + '...'

    # 截断列表字段
    list_fields = ['key_decisions', 'risks', 'review_comments',
                   'review_suggestions', 'key_changes']
    for field in list_fields:
        if field in result and isinstance(result[field], list):
            result[field] = result[field][:3]  # 最多保留 3 条

    # 截断输出文件列表
    if 'output_files' in result and isinstance(result['output_files'], list):
        if len(result['output_files']) > 10:
            result['output_files'] = result['output_files'][:10]
            result['output_files'].append('... (truncated)')

    return result


def validate_result(result: TaskResult, phase: str) -> List[str]:
    """
    验证结果格式

    Args:
        result: Task 结果
        phase: 阶段编号

    Returns:
        List[str]: 验证错误列表，空列表表示验证通过
    """
    errors = []

    # 必填字段检查
    if result.phase != phase:
        errors.append(f"阶段编号不匹配: 期望 {phase}, 实际 {result.phase}")

    if not result.summary:
        errors.append("缺少 summary 字段")

    # 评审阶段检查
    if phase in ['P4', 'P6', 'P8', 'P10', 'P12', 'P14']:
        if result.review_passed is None:
            errors.append("评审阶段缺少 review_passed 字段")
        if result.review_score < 0 or result.review_score > 100:
            errors.append(f"评审得分无效: {result.review_score}")

    # 执行阶段检查
    if phase in ['P3', 'P5', 'P7', 'P9', 'P11', 'P13']:
        if not result.output_files:
            errors.append("执行阶段缺少 output_files 字段")

    # Token 预算检查
    budget = RETURN_BUDGET_LIMITS.get(phase, 3000)
    if result.token_count > budget * 1.5:
        errors.append(f"返回结果超出预算: {result.token_count} > {budget * 1.5}")

    return errors


def create_summary_for_orchestrator(result: TaskResult) -> str:
    """
    为编排器创建简洁的摘要

    Args:
        result: Task 结果

    Returns:
        str: 简洁摘要
    """
    lines = [f"[{result.phase}] ", ]

    if result.success:
        lines.append("SUCCESS")
    else:
        lines.append(f"FAILED: {result.error_message or 'Unknown error'}")

    if result.summary:
        lines.append(f" - {result.summary[:100]}")

    if result.is_review():
        review_status = "PASSED" if result.review_passed else "FAILED"
        lines.append(f" (Review: {review_status}, Score: {result.review_score})")

    return "".join(lines)


def create_error_result(phase: str, error_message: str) -> TaskResult:
    """
    创建错误结果

    Args:
        phase: 阶段编号
        error_message: 错误信息

    Returns:
        TaskResult: 错误结果对象
    """
    return TaskResult(
        success=False,
        phase=phase,
        error_message=error_message,
        summary=f"执行失败: {error_message}"
    )


def merge_p9_story_results(results: List[TaskResult]) -> TaskResult:
    """
    合并 P9 阶段多个故事的结果

    Args:
        results: 各故事的执行结果

    Returns:
        TaskResult: 合并后的结果
    """
    if not results:
        return create_error_result('P9', '没有故事执行结果')

    success_count = sum(1 for r in results if r.success)
    total_count = len(results)

    merged = TaskResult(
        success=all(r.success for r in results),
        phase='P9',
        summary=f"完成 {success_count}/{total_count} 个故事",
        output_files=[],
        key_decisions=[],
        risks=[],
        key_changes=[],
        tests_passed=all(r.tests_passed for r in results if r.tests_passed is not None),
        metrics={
            'stories_total': total_count,
            'stories_success': success_count,
            'stories_failed': total_count - success_count
        }
    )

    # 合并各故事的输出
    for r in results:
        merged.output_files.extend(r.output_files)
        merged.key_decisions.extend(r.key_decisions)
        merged.key_changes.extend(r.key_changes)
        merged.risks.extend(r.risks)

    # 去重和截断
    merged.output_files = list(set(merged.output_files))
    merged.key_decisions = merged.key_decisions[:5]
    merged.key_changes = merged.key_changes[:10]
    merged.risks = merged.risks[:5]

    return merged
