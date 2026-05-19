#!/usr/bin/env python3
"""
Calculate risk level for a requirement based on impact and complexity.

Risk levels: LOW, MEDIUM, HIGH, CRITICAL
"""

import sys
import re
from pathlib import Path


def calculate_risk(file_path: str) -> dict:
    """Calculate risk level from requirements document."""
    path = Path(file_path)

    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    content = path.read_text()

    # Risk factors
    impact_score = assess_impact(content)
    complexity_score = assess_complexity(content)

    # Combined risk calculation
    total_score = (impact_score + complexity_score) / 2

    # Map to risk level
    if total_score >= 4.5:
        risk_level = "CRITICAL"
    elif total_score >= 3.5:
        risk_level = "HIGH"
    elif total_score >= 2.5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_level": risk_level,
        "impact_score": impact_score,
        "complexity_score": complexity_score,
        "total_score": total_score,
        "factors": {
            "affected_modules": count_modules(content),
            "integration_points": count_integrations(content),
            "team_size": extract_team_size(content),
            "estimated_days": extract_estimated_days(content)
        }
    }


def assess_impact(content: str) -> int:
    """Assess impact score (1-5)."""
    score = 1  # Base score

    # Number of affected modules
    module_count = count_modules(content)
    if module_count > 5:
        score += 2
    elif module_count > 2:
        score += 1

    # User impact
    if re.search(r'(核心|关键|重要|主要)', content):
        score += 1

    # Data impact
    if re.search(r'(数据迁移|数据同步|数据库)', content):
        score += 1

    return min(score, 5)


def assess_complexity(content: str) -> int:
    """Assess complexity score (1-5)."""
    score = 1  # Base score

    # Integration points
    integration_count = count_integrations(content)
    if integration_count > 5:
        score += 2
    elif integration_count > 2:
        score += 1

    # Technical complexity indicators
    complex_keywords = ['性能', '并发', '分布式', '异步', '缓存', '消息队列']
    keyword_count = sum(1 for kw in complex_keywords if kw in content)
    if keyword_count >= 3:
        score += 1

    # Estimated duration
    days = extract_estimated_days(content)
    if days and days > 10:
        score += 1
    elif days and days > 5:
        score += 0.5

    return min(score, 5)


def count_modules(content: str) -> int:
    """Count number of affected modules."""
    matches = re.findall(r'[模块|服务|系统][:：]\s*[^\n]+', content)
    return len(matches)


def count_integrations(content: str) -> int:
    """Count integration points."""
    # Count API mentions, interfaces, external dependencies
    patterns = [
        r'API',
        r'接口',
        r'集成',
        r'对接',
        r'第三方'
    ]
    return sum(len(re.findall(pattern, content)) for pattern in patterns)


def extract_team_size(content: str) -> int:
    """Extract team size from document."""
    match = re.search(r'团队[规模大小][:：]\s*(\d+)', content)
    if match:
        return int(match.group(1))
    return 3  # Default


def extract_estimated_days(content: str) -> int:
    """Extract estimated duration in days."""
    # Look for patterns like "预计 5 天" or "5人天"
    match = re.search(r'预计[工时]*[:：]\s*(\d+)\s*[天日]', content)
    if match:
        return int(match.group(1))

    # Look for story points or similar
    match = re.search(r'(\d+)\s*[点分]', content)
    if match:
        points = int(match.group(1))
        return points // 2  # Rough conversion

    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python calculate-risk.py <file.md>")
        sys.exit(1)

    file_path = sys.argv[1]
    result = calculate_risk(file_path)

    if "error" in result:
        print(f"❌ {result['error']}")
        sys.exit(1)

    print(f"Risk Level: {result['risk_level']}")
    print(f"Impact Score: {result['impact_score']}/5")
    print(f"Complexity Score: {result['complexity_score']}/5")
    print(f"Total Score: {result['total_score']:.1f}/5")
    print(f"\nFactors:")
    for key, value in result['factors'].items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
