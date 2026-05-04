#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["ruamel.yaml>=0.18"]
# ///
"""One-shot migration: convert legacy SKILL.md frontmatter to i18n format.

For each skill directory:
  1. Read SKILL.md frontmatter (legacy format with Chinese top-level name).
  2. Move legacy `name` -> metadata.i18n.<source>.name (default source: zh-CN).
  3. Move legacy `market.short_desc` -> metadata.i18n.<source>.short_desc.
  4. Set top-level `name` to the directory name (ASCII slug).
  5. Add metadata.i18n.{default_locale=en-US, source_locale=<src>, locales=[src]}.
  6. Move existing body to SKILL.<source>.md (with `<!-- locale: <src> -->` header).
  7. Replace root SKILL.md body with a translation-pending placeholder.
  8. Compute source_hash for the source locale.

DOES NOT TRANSLATE — translate.py (the CI script) fills in the en-US body & i18n block
afterwards. After migration, the skill is structurally valid but only has source_locale
content; en-US locale is added by translate.py on the next CI run.

Usage:
  scripts/i18n/migrate.py --dry-run                # preview, default
  scripts/i18n/migrate.py --apply                  # write changes
  scripts/i18n/migrate.py --apply skills/web-access  # one skill
  scripts/i18n/migrate.py --apply --source zh-CN   # set source locale (default zh-CN)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from io import StringIO
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString, FoldedScalarString

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCALE = "en-US"
PLACEHOLDER_BODY = (
    "<!-- TRANSLATION PENDING: this body will be auto-translated from "
    "metadata.i18n.<source_locale>.body by scripts/i18n/translate.py on the next CI run. -->\n"
    "\n"
    "# {dir_name}\n"
    "\n"
    "_Translation pending. See `{source_body}` for the source-language version._\n"
)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def make_yaml() -> YAML:
    y = YAML()
    y.indent(mapping=2, sequence=4, offset=2)
    y.width = 4096
    y.preserve_quotes = True
    return y


def load_frontmatter(text: str) -> tuple[Any, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("File is missing YAML frontmatter")
    yaml_text, body = m.group(1), m.group(2)
    yaml = make_yaml()
    fm = yaml.load(yaml_text)
    return fm, body


def dump_frontmatter(fm: Any, body: str) -> str:
    yaml = make_yaml()
    buf = StringIO()
    yaml.dump(fm, buf)
    return f"---\n{buf.getvalue()}---\n\n{body.lstrip()}"


def source_hash(body: str, i18n_strings: dict[str, str]) -> str:
    h = hashlib.sha256()
    h.update(body.encode("utf-8"))
    h.update(b"\x00")
    h.update(json.dumps(i18n_strings, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    return f"sha256:{h.hexdigest()[:16]}"


def migrate_skill(skill_dir: Path, source_locale: str, default_locale: str, apply: bool) -> dict[str, Any]:
    """Return a dict describing the planned changes for this skill."""
    rel = skill_dir.relative_to(REPO_ROOT).as_posix()
    skill_md = skill_dir / "SKILL.md"
    plan: dict[str, Any] = {"skill": rel, "actions": [], "errors": []}

    if not skill_md.is_file():
        plan["errors"].append("SKILL.md not found")
        return plan

    text = skill_md.read_text(encoding="utf-8")
    try:
        fm, body = load_frontmatter(text)
    except ValueError as e:
        plan["errors"].append(str(e))
        return plan

    # Already migrated?
    metadata = fm.get("metadata") or {}
    if isinstance(metadata, dict) and "i18n" in metadata and isinstance(metadata.get("i18n"), dict):
        plan["actions"].append("already migrated, skipping")
        return plan

    legacy_name = fm.get("name", "").strip()
    legacy_short_desc = ""
    market = fm.get("market")
    if isinstance(market, dict):
        legacy_short_desc = (market.get("short_desc") or "").strip()
        # Remove short_desc from market — it has migrated.
        if "short_desc" in market:
            market.pop("short_desc", None)

    legacy_description = fm.get("description", "")

    # New top-level name = directory name
    new_name = skill_dir.name
    fm["name"] = new_name

    # Build metadata.i18n
    if not isinstance(metadata, dict):
        metadata = {}
        fm["metadata"] = metadata

    i18n_block: dict[str, Any] = {
        "default_locale": default_locale,
        "source_locale": source_locale,
        "locales": [source_locale],
    }

    # Source body file
    source_body_filename = f"SKILL.{source_locale}.md"
    source_body_path = skill_dir / source_body_filename
    source_body_text = f"<!-- locale: {source_locale} -->\n\n{body.lstrip()}"

    # Source locale strings
    src_strings = {
        "name": legacy_name or new_name,
        "short_desc": legacy_short_desc or legacy_name or new_name,
    }
    if legacy_description:
        src_strings["description"] = (
            legacy_description if isinstance(legacy_description, str) else str(legacy_description)
        )

    src_hash = source_hash(body, src_strings)

    src_block: dict[str, Any] = {
        "name": src_strings["name"],
        "short_desc": src_strings["short_desc"],
    }
    if "description" in src_strings:
        # Use folded style for long descriptions to keep frontmatter readable
        desc = src_strings["description"]
        src_block["description"] = FoldedScalarString(desc) if "\n" in desc or len(desc) > 80 else desc
    src_block["body"] = f"./{source_body_filename}"
    src_block["source_hash"] = src_hash
    src_block["translated_by"] = "human"

    i18n_block[source_locale] = src_block
    metadata["i18n"] = i18n_block

    # Plan actions
    plan["actions"].append(f"rename top-level name '{legacy_name}' -> '{new_name}'")
    plan["actions"].append(f"add metadata.i18n.{source_locale} (name, short_desc, description, body, source_hash)")
    plan["actions"].append(f"create {source_body_filename} ({len(body)} chars)")
    placeholder = PLACEHOLDER_BODY.format(dir_name=new_name, source_body=source_body_filename)
    plan["actions"].append(f"replace root SKILL.md body with translation-pending placeholder ({len(placeholder)} chars)")
    if legacy_short_desc:
        plan["actions"].append("remove market.short_desc (migrated to i18n)")

    if apply:
        # Write source body file
        source_body_path.write_text(source_body_text, encoding="utf-8")
        # Write new root SKILL.md (frontmatter + placeholder body)
        new_root = dump_frontmatter(fm, placeholder)
        skill_md.write_text(new_root, encoding="utf-8")
        plan["written"] = [
            source_body_path.relative_to(REPO_ROOT).as_posix(),
            skill_md.relative_to(REPO_ROOT).as_posix(),
        ]

    return plan


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Skill directories to migrate (default: all under skills/)")
    parser.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only (default)")
    parser.add_argument("--source", default="zh-CN", help="Source locale (default: zh-CN)")
    parser.add_argument("--default", dest="default_locale", default=DEFAULT_LOCALE,
                        help=f"Default locale (default: {DEFAULT_LOCALE})")
    args = parser.parse_args(argv)

    apply = args.apply and not args.dry_run

    if args.paths:
        targets = [Path(p).resolve() for p in args.paths]
    else:
        targets = sorted((REPO_ROOT / "skills").iterdir())
        targets = [t for t in targets if t.is_dir() and (t / "SKILL.md").is_file()]

    plans: list[dict[str, Any]] = []
    for skill_dir in targets:
        if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
            continue
        plans.append(migrate_skill(skill_dir, args.source, args.default_locale, apply))

    print(f"\n{'APPLIED' if apply else 'DRY-RUN'} migration plan ({len(plans)} skills):\n")
    for p in plans:
        if p.get("errors"):
            print(f"  ✗ {p['skill']}: ERRORS: {p['errors']}")
        else:
            print(f"  • {p['skill']}: {len(p['actions'])} action(s)")
            for a in p["actions"]:
                print(f"      - {a}")
    print()
    if not apply:
        print("Re-run with --apply to write changes.")
    else:
        print("Migration complete. Run scripts/i18n/validate-i18n.py to verify.")
    return 1 if any(p.get("errors") for p in plans) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
