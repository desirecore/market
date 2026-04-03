#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> --path <path> [--format basic|desirecore]

Examples:
    init_skill.py my-new-skill --path ~/.desirecore/skills
    init_skill.py my-api-helper --path ~/.desirecore/skills --format basic
"""

import sys
import argparse
import re
from pathlib import Path
from datetime import date


# ==================== DesireCore 完整格式模板 ====================

DESIRECORE_TEMPLATE = """\
---
name: {skill_name}
description: >-
  [TODO: 完整描述技能用途。必须包含 "Use when" 触发提示，
  帮助 AI 判断何时使用该技能。]
version: 1.0.0
type: procedural
risk_level: low
status: enabled
tags:
  - [TODO: 添加标签]
metadata:
  author: user
  updated_at: '{today}'
---

# {skill_title}

## L0：一句话摘要

[TODO: 用一句话描述这个技能做什么]

## L1：概述与使用场景

### 能力描述

[TODO: 详细描述技能的核心能力]

### 使用场景

- [TODO: 场景 1]
- [TODO: 场景 2]

### 核心价值

- [TODO: 价值 1]

## L2：详细规范

### 具体操作步骤

[TODO: 按步骤描述执行流程]

### 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| [TODO] | [TODO] |
"""


# ==================== Claude Code 基础格式模板 ====================

BASIC_TEMPLATE = """\
---
name: {skill_name}
description: [TODO: Complete and informative explanation of what the skill does and when to use it. Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it.]
---

# {skill_title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## [TODO: Replace with first main section]

[TODO: Add content here]

## Resources

This skill includes example resource directories:

### scripts/
Executable code for tasks that require deterministic reliability.

### references/
Documentation and reference material loaded into context as needed.

### assets/
Files used within the output (templates, images, fonts, etc.).

---

**Delete any unneeded directories.** Not every skill requires all three.
"""


EXAMPLE_SCRIPT = '''\
#!/usr/bin/env python3
"""
Example helper script for {skill_name}

Replace with actual implementation or delete if not needed.
"""

def main():
    print("Example script for {skill_name}")
    # TODO: Add actual script logic

if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """\
# Reference Documentation for {skill_title}

Replace with actual reference content or delete if not needed.

Reference docs are ideal for:
- API documentation
- Detailed workflow guides
- Database schemas
- Content too lengthy for main SKILL.md
"""

EXAMPLE_ASSET = """\
This is a placeholder for asset files.
Replace with actual assets (templates, images, fonts, etc.) or delete if not needed.

Asset files are NOT loaded into context — they are used within the output.
"""


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


def validate_skill_name(name):
    """Validate skill name format (kebab-case)."""
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', name) and not re.match(r'^[a-z0-9]$', name):
        return False, "Name must be kebab-case (lowercase letters, digits, hyphens)"
    if '--' in name:
        return False, "Name cannot contain consecutive hyphens"
    if len(name) > 64:
        return False, f"Name too long ({len(name)} chars, max 64)"
    return True, ""


def init_skill(skill_name, path, fmt='desirecore'):
    """Initialize a new skill directory with template SKILL.md."""
    skill_dir = Path(path).resolve() / skill_name

    if skill_dir.exists():
        print(f"❌ Error: Skill directory already exists: {skill_dir}")
        return None

    # Create skill directory
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"✅ Created skill directory: {skill_dir}")
    except Exception as e:
        print(f"❌ Error creating directory: {e}")
        return None

    # Create SKILL.md from template
    skill_title = title_case_skill_name(skill_name)
    template = DESIRECORE_TEMPLATE if fmt == 'desirecore' else BASIC_TEMPLATE
    skill_content = template.format(
        skill_name=skill_name,
        skill_title=skill_title,
        today=date.today().isoformat(),
    )

    skill_md_path = skill_dir / 'SKILL.md'
    try:
        skill_md_path.write_text(skill_content)
        print(f"✅ Created SKILL.md ({fmt} format)")
    except Exception as e:
        print(f"❌ Error creating SKILL.md: {e}")
        return None

    # Create resource directories with example files
    try:
        scripts_dir = skill_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        example_script = scripts_dir / 'example.py'
        example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
        example_script.chmod(0o755)
        print("✅ Created scripts/example.py")

        references_dir = skill_dir / 'references'
        references_dir.mkdir(exist_ok=True)
        example_ref = references_dir / 'api_reference.md'
        example_ref.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
        print("✅ Created references/api_reference.md")

        assets_dir = skill_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        example_asset = assets_dir / 'example_asset.txt'
        example_asset.write_text(EXAMPLE_ASSET)
        print("✅ Created assets/example_asset.txt")
    except Exception as e:
        print(f"❌ Error creating resource directories: {e}")
        return None

    print(f"\n✅ Skill '{skill_name}' initialized at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md — complete TODO items and update description")
    print("2. Customize or delete example files in scripts/, references/, assets/")
    print("3. Run quick_validate.py to check the skill structure")

    return skill_dir


def main():
    parser = argparse.ArgumentParser(
        description='Initialize a new skill from template',
        epilog='Examples:\n'
               '  init_skill.py my-new-skill --path ~/.desirecore/skills\n'
               '  init_skill.py my-api-helper --path ~/.desirecore/skills --format basic',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('skill_name', help='Skill name (kebab-case, max 64 chars)')
    parser.add_argument('--path', required=True, help='Parent directory for the skill')
    parser.add_argument(
        '--format', choices=['desirecore', 'basic'], default='desirecore',
        help='Template format: desirecore (full, default) or basic (Claude Code compatible)',
    )
    args = parser.parse_args()

    # Validate name
    valid, msg = validate_skill_name(args.skill_name)
    if not valid:
        print(f"❌ Invalid skill name: {msg}")
        sys.exit(1)

    print(f"🚀 Initializing skill: {args.skill_name}")
    print(f"   Location: {args.path}")
    print(f"   Format:   {args.format}")
    print()

    result = init_skill(args.skill_name, args.path, args.format)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
