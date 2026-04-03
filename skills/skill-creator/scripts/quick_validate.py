#!/usr/bin/env python3
"""
Quick validation script for skills.

Validates against DesireCore SKILL.md frontmatter schema.
Also accepts Claude Code basic format (name + description only).
"""

import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


# DesireCore 已知的顶层字段集合
# 来源：lib/schemas/agent/skill-frontmatter.ts 的 properties 定义
# Schema 设置了 additionalProperties: true，所以未知字段只警告不报错
KNOWN_PROPERTIES = {
    # 核心字段
    'name', 'description', 'version', 'type', 'requires',
    'risk_level', 'status', 'tags', 'metadata',
    # 功能控制
    'disable-model-invocation', 'disable_model_invocation',
    'allowed-tools', 'user-invocable', 'argument-hint',
    'model', 'context', 'agent',
    # 高级字段
    'error_message', 'skill_package', 'input_schema', 'output_schema',
    'market', 'x_desirecore', 'json_output',
    # Claude Code 兼容字段
    'license', 'compatibility',
}

VALID_TYPES = {'procedural', 'conversational', 'meta'}
VALID_RISK_LEVELS = {'low', 'medium', 'high'}
VALID_STATUSES = {'enabled', 'disabled'}
VALID_CONTEXTS = {'default', 'fork'}
SEMVER_RE = re.compile(r'^\d+\.\d+\.\d+$')
KEBAB_RE = re.compile(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$')


def validate_skill(skill_path):
    """
    Validate a skill directory.

    Returns:
        (valid: bool, errors: list[str], warnings: list[str])
    """
    skill_path = Path(skill_path)
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, ["SKILL.md not found"], []

    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, ["No YAML frontmatter found (must start with ---)"], []

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, ["Invalid frontmatter format (missing closing ---)"], []

    try:
        frontmatter = yaml.safe_load(match.group(1))
        if not isinstance(frontmatter, dict):
            return False, ["Frontmatter must be a YAML dictionary"], []
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML: {e}"], []

    # === 必填字段 ===
    if 'description' not in frontmatter:
        errors.append("Missing required field: 'description'")

    # === description 质量检查 ===
    description = frontmatter.get('description', '')
    if isinstance(description, str):
        desc_stripped = description.strip()
        if desc_stripped and len(desc_stripped) < 10:
            warnings.append("Description is very short — include 'Use when' trigger hints")
        if len(desc_stripped) > 1024:
            errors.append(f"Description too long ({len(desc_stripped)} chars, max 1024)")
        if '<' in desc_stripped or '>' in desc_stripped:
            warnings.append("Description contains angle brackets (< or >) — may cause parsing issues")

    # === name 格式检查 ===
    name = frontmatter.get('name', '')
    if isinstance(name, str) and name.strip():
        n = name.strip()
        if len(n) > 64:
            errors.append(f"Name too long ({len(n)} chars, max 64)")
        # kebab-case 检查仅当 name 是英文时
        if re.match(r'^[a-z0-9-]+$', n):
            if not KEBAB_RE.match(n):
                warnings.append(f"Name '{n}' starts/ends with hyphen or has consecutive hyphens")

    # === version 格式检查 ===
    version = frontmatter.get('version')
    if version is not None and not SEMVER_RE.match(str(version)):
        warnings.append(f"Version '{version}' is not valid semver (expected x.y.z)")

    # === 枚举字段检查 ===
    skill_type = frontmatter.get('type')
    if skill_type is not None and skill_type not in VALID_TYPES:
        errors.append(f"Invalid type: '{skill_type}'. Must be one of: {', '.join(sorted(VALID_TYPES))}")

    risk = frontmatter.get('risk_level')
    if risk is not None and risk not in VALID_RISK_LEVELS:
        errors.append(f"Invalid risk_level: '{risk}'. Must be one of: {', '.join(sorted(VALID_RISK_LEVELS))}")

    status = frontmatter.get('status')
    if status is not None and status not in VALID_STATUSES:
        errors.append(f"Invalid status: '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}")

    context = frontmatter.get('context')
    if context is not None and context not in VALID_CONTEXTS:
        errors.append(f"Invalid context: '{context}'. Must be one of: {', '.join(sorted(VALID_CONTEXTS))}")

    # === 未知字段警告（不阻断） ===
    unknown = set(frontmatter.keys()) - KNOWN_PROPERTIES
    if unknown:
        warnings.append(f"Unknown fields (will be preserved): {', '.join(sorted(unknown))}")

    valid = len(errors) == 0
    return valid, errors, warnings


def main():
    if len(sys.argv) != 2:
        print("Usage: quick_validate.py <skill_directory>")
        print("\nValidates SKILL.md frontmatter against DesireCore schema.")
        print("Also accepts Claude Code basic format (name + description).")
        sys.exit(1)

    skill_path = sys.argv[1]
    valid, errors, warnings = validate_skill(skill_path)

    if valid and not warnings:
        print(f"✅ Skill is valid!")
    elif valid and warnings:
        print(f"✅ Skill is valid (with warnings):")
        for w in warnings:
            print(f"  ⚠ {w}")
    else:
        print(f"❌ Validation failed:")
        for e in errors:
            print(f"  ✗ {e}")
        if warnings:
            print(f"  Warnings:")
            for w in warnings:
                print(f"  ⚠ {w}")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
