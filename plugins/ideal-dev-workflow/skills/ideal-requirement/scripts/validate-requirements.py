#!/usr/bin/env python3
"""
Validate requirements document completeness.

Checks if all required fields are present in a requirements document.
"""

import sys
import re
from pathlib import Path


def validate_markdown(file_path: str) -> dict:
    """Validate a markdown requirements document."""
    path = Path(file_path)

    if not path.exists():
        return {"valid": False, "error": f"File not found: {file_path}"}

    content = path.read_text()

    # Required fields for different document types
    required_fields = {
        "software-feature": [
            "需求名称",
            "问题陈述",
            "目标概述",
            "功能清单",
            "验收标准"
        ],
        "bug-fix": [
            "需求名称",
            "Bug 标题",
            "前置条件",
            "复现流程",
            "期望行为",
            "实际行为"
        ],
        "refactoring": [
            "需求名称",
            "当前状态",
            "存在的问题",
            "重构目标",
            "方案概述"
        ]
    }

    # Detect document type from frontmatter or content
    doc_type = detect_document_type(content, file_path)

    if doc_type not in required_fields:
        return {
            "valid": False,
            "error": f"Unknown or missing document type. Expected one of: {list(required_fields.keys())}"
        }

    # Check for required fields
    missing_fields = []
    for field in required_fields[doc_type]:
        if field not in content:
            missing_fields.append(field)

    # Check for placeholders
    placeholders = re.findall(r'\[待补充\]|\[TODO\]|\[待填写\]', content, flags=re.IGNORECASE)

    result = {
        "valid": len(missing_fields) == 0,
        "document_type": doc_type,
        "file": str(path),
        "missing_fields": missing_fields,
        "placeholders_found": len(placeholders),
        "total_required": len(required_fields[doc_type]),
        "completed": len(required_fields[doc_type]) - len(missing_fields)
    }

    return result


def detect_document_type(content: str, file_path: str) -> str:
    """Detect document type from content or filename."""
    # Check frontmatter
    frontmatter_match = re.search(r'需求类型:\s*(\S+)', content)
    if frontmatter_match:
        return frontmatter_match.group(1)

    # Check filename
    if "bug-fix" in file_path.lower():
        return "bug-fix"
    elif "refactoring" in file_path.lower():
        return "refactoring"

    # Default to software-feature
    return "software-feature"


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-requirements.py <file.md>")
        sys.exit(1)

    file_path = sys.argv[1]
    result = validate_markdown(file_path)

    if not result["valid"]:
        print(f"❌ Validation failed for {result['document_type']}")
        print(f"Missing fields: {', '.join(result['missing_fields'])}")
        print(f"Completed: {result['completed']}/{result['total_required']}")
        if result['placeholders_found'] > 0:
            print(f"⚠️  Found {result['placeholders_found']} placeholders")
        sys.exit(1)
    else:
        print(f"✅ Validation passed for {result['document_type']}")
        print(f"All {result['total_required']} required fields present")
        sys.exit(0)


if __name__ == "__main__":
    main()
