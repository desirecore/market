#!/usr/bin/env python3
"""
Skill Packager & Installer

Supports two modes:
  - Package: Create a .skill file (ZIP) for Claude Code distribution
  - Install: Install directly to DesireCore via HTTP API

Usage:
    # Package as .skill file (Claude Code compatible)
    package_skill.py <path/to/skill-folder> [output-directory]

    # Install to DesireCore via API
    package_skill.py <path/to/skill-folder> --install [--scope global|agent] [--agent-id <id>]
"""

import sys
import os
import json
import zipfile
import argparse
import ssl
import urllib.request
import urllib.error
from pathlib import Path

# Import validate_skill from sibling script
_script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_script_dir))
from quick_validate import validate_skill


# ==================== Package Mode ====================

def package_skill(skill_path, output_dir=None):
    """Package a skill folder into a .skill file (ZIP format)."""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Validate before packaging
    print("🔍 Validating skill...")
    valid, errors, warnings = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed:")
        for e in errors:
            print(f"  ✗ {e}")
        return None
    if warnings:
        for w in warnings:
            print(f"  ⚠ {w}")
    print(f"✅ Validation passed\n")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    # Create .skill file (zip format)
    try:
        with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in skill_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(skill_path.parent)
                    zipf.write(file_path, arcname)
                    print(f"  Added: {arcname}")

        print(f"\n✅ Packaged to: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"❌ Error creating .skill file: {e}")
        return None


# ==================== Install Mode ====================

def read_agent_service_port():
    """Read Agent Service port from port file."""
    port_file = Path.home() / '.desirecore' / 'agent-service.port'
    if not port_file.exists():
        return None
    return port_file.read_text().strip()


def install_skill(skill_path, scope='global', agent_id=None):
    """Install a skill to DesireCore via HTTP API."""
    skill_path = Path(skill_path).resolve()
    skill_md = skill_path / 'SKILL.md'

    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Validate first
    print("🔍 Validating skill...")
    valid, errors, warnings = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed:")
        for e in errors:
            print(f"  ✗ {e}")
        return None
    if warnings:
        for w in warnings:
            print(f"  ⚠ {w}")
    print(f"✅ Validation passed\n")

    # Check Agent Service
    port = read_agent_service_port()
    if not port:
        print("❌ Error: Agent Service not running (port file not found)")
        print("\nFallback — install via file system:")
        if scope == 'agent' and agent_id:
            print(f"  cp -r {skill_path} ~/.desirecore/agents/{agent_id}/skills/")
        else:
            print(f"  cp -r {skill_path} ~/.desirecore/skills/")
        return None

    content = skill_md.read_text()
    skill_id = skill_path.name

    # Build API request
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    if scope == 'agent':
        if not agent_id:
            print("❌ Error: --agent-id is required for agent scope")
            return None
        url = f"https://127.0.0.1:{port}/api/agents/{agent_id}/skills"
        payload = {"id": skill_id, "fullContent": content}
    else:
        url = f"https://127.0.0.1:{port}/api/skills"
        payload = {"skillId": skill_id, "content": content}

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url, data=data, method='POST',
        headers={'Content-Type': 'application/json'},
    )

    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            result = json.loads(resp.read())
            print(f"✅ Installed '{skill_id}' ({scope} scope)")
            return result
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f"❌ API error ({e.code}): {body}")
        return None
    except urllib.error.URLError as e:
        print(f"❌ Connection error: {e.reason}")
        print("Is Agent Service running?")
        return None


# ==================== Main ====================

def main():
    parser = argparse.ArgumentParser(
        description='Package or install a skill',
        epilog='Examples:\n'
               '  package_skill.py my-skill/               # Package as .skill ZIP\n'
               '  package_skill.py my-skill/ ./dist         # Package to specific dir\n'
               '  package_skill.py my-skill/ --install      # Install via API (global)\n'
               '  package_skill.py my-skill/ --install --scope agent --agent-id abc123',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('skill_path', help='Path to skill folder')
    parser.add_argument('output_dir', nargs='?', default=None,
                        help='Output directory for .skill file (package mode only)')
    parser.add_argument('--install', action='store_true',
                        help='Install via DesireCore API instead of packaging')
    parser.add_argument('--scope', choices=['global', 'agent'], default='global',
                        help='Installation scope (default: global)')
    parser.add_argument('--agent-id',
                        help='Agent ID (required when --scope agent)')

    args = parser.parse_args()

    if args.install:
        print(f"📦 Installing skill: {args.skill_path} ({args.scope} scope)")
        print()
        result = install_skill(args.skill_path, args.scope, args.agent_id)
    else:
        print(f"📦 Packaging skill: {args.skill_path}")
        if args.output_dir:
            print(f"   Output: {args.output_dir}")
        print()
        result = package_skill(args.skill_path, args.output_dir)

    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
