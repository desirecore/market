#!/usr/bin/env python3
"""
Quick validation script for skills.

Validates against DesireCore SKILL.md frontmatter schema.
Also accepts Claude Code basic format (name + description only).
"""

import sys
import re
import json
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / 'scripts' / 'i18n' / 'schema' / 'skill-frontmatter.schema.json'
CATEGORIES_PATH = REPO_ROOT / 'categories.json'


def load_market_schema():
    if not SCHEMA_PATH.is_file():
        return {}
    return json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))


SCHEMA = load_market_schema()
SCHEMA_PROPERTIES = SCHEMA.get('properties', {}) if isinstance(SCHEMA, dict) else {}
KNOWN_PROPERTIES = set(SCHEMA_PROPERTIES)
REQUIRED_PROPERTIES = set(SCHEMA.get('required', [])) if isinstance(SCHEMA, dict) else set()
VALID_TYPES = set(SCHEMA_PROPERTIES.get('type', {}).get('enum', []))
VALID_RISK_LEVELS = set(SCHEMA_PROPERTIES.get('risk_level', {}).get('enum', []))
VALID_STATUSES = set(SCHEMA_PROPERTIES.get('status', {}).get('enum', []))
VALID_CONTEXTS = {'default', 'fork'}
SEMVER_RE = re.compile(SCHEMA_PROPERTIES.get('version', {}).get('pattern', r'^\d+\.\d+\.\d+$'))
NAME_RE = re.compile(SCHEMA_PROPERTIES.get('name', {}).get('pattern', r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$'))
TAG_RE = re.compile(SCHEMA_PROPERTIES.get('tags', {}).get('items', {}).get('pattern', r'^[a-z0-9][a-z0-9-]*$'))
LOCALE_RE = re.compile(r'^[a-z]{2,3}(?:-[A-Z]{2})?$')


def load_category_ids():
    if not CATEGORIES_PATH.is_file():
        return set()
    data = json.loads(CATEGORIES_PATH.read_text(encoding='utf-8'))
    return set(data) if isinstance(data, dict) else set()


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
    is_basic_claude_skill = set(frontmatter).issubset({'name', 'description', 'license', 'compatibility'})
    required = {'name', 'description'} if is_basic_claude_skill else REQUIRED_PROPERTIES
    for field in sorted(required):
        if field not in frontmatter:
            errors.append(f"Missing required field: '{field}'")

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
        if not NAME_RE.match(n):
            errors.append("Name must be lowercase ASCII kebab-case, cannot start/end with hyphen, and cannot contain consecutive hyphens")
        if n != skill_path.name:
            errors.append(f"Name '{n}' must equal parent directory '{skill_path.name}'")

    # === version 格式检查 ===
    version = frontmatter.get('version')
    if version is not None and not SEMVER_RE.match(str(version)):
        errors.append(f"Version '{version}' is not valid semver")

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

    tags = frontmatter.get('tags')
    if tags is not None:
        if not isinstance(tags, list) or not all(isinstance(x, str) for x in tags):
            errors.append("tags must be a list of strings")
        else:
            duplicate_tags = sorted({x for x in tags if tags.count(x) > 1})
            if duplicate_tags:
                errors.append(f"tags must be unique; duplicates: {', '.join(duplicate_tags)}")
            invalid_tags = [x for x in tags if not TAG_RE.match(x)]
            if invalid_tags:
                errors.append(f"Invalid tag(s): {', '.join(invalid_tags)}")

    if not is_basic_claude_skill:
        metadata = frontmatter.get('metadata')
        if not isinstance(metadata, dict):
            errors.append("metadata must be an object")
        else:
            i18n = metadata.get('i18n')
            if not isinstance(i18n, dict):
                errors.append("metadata.i18n block missing")
            else:
                locales = i18n.get('locales')
                if not isinstance(locales, list) or not all(isinstance(x, str) and LOCALE_RE.match(x) for x in locales):
                    errors.append("metadata.i18n.locales must be a list of BCP-47 locale strings")
                    locale_set = set()
                else:
                    locale_set = set(locales)
                for key in ('default_locale', 'source_locale'):
                    value = i18n.get(key)
                    if not isinstance(value, str) or not LOCALE_RE.match(value):
                        errors.append(f"metadata.i18n.{key} must be a BCP-47 locale string")
                    elif value not in locale_set:
                        errors.append(f"metadata.i18n.{key} must be present in metadata.i18n.locales")
                for locale in sorted(locale_set):
                    payload = i18n.get(locale)
                    if not isinstance(payload, dict):
                        errors.append(f"metadata.i18n.{locale} block missing")
                        continue
                    for field in ('name', 'short_desc'):
                        if not isinstance(payload.get(field), str) or not payload.get(field).strip():
                            errors.append(f"metadata.i18n.{locale}.{field} is required")
                    body = payload.get('body')
                    if body is not None:
                        if not isinstance(body, str) or not body.startswith('./') or not body.endswith('.md'):
                            errors.append(f"metadata.i18n.{locale}.body must be a relative Markdown path starting with './'")
                        elif not (skill_path / body.removeprefix('./')).is_file():
                            errors.append(f"metadata.i18n.{locale}.body points to missing file: {body}")

    market = frontmatter.get('market')
    if isinstance(market, dict):
        category = market.get('category')
        category_ids = load_category_ids()
        if category_ids and category not in category_ids:
            errors.append(f"market.category '{category}' is not declared in categories.json")

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
