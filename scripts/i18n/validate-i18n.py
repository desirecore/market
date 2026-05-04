#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Validate DesireCore market i18n state.

Checks:
  1. SKILL.md frontmatter top-level `name` matches parent dir name and is spec-compliant.
  2. metadata.i18n.default_locale and source_locale are listed in metadata.i18n.locales.
  3. Each declared locale has metadata.i18n.<locale>.{name,short_desc}.
  4. metadata.i18n.<locale>.body, if present, points to an existing file; otherwise the
     fallback chain must terminate at a readable root SKILL.md.
  5. SKILL.<locale>.md, if it declares <!-- locale: ... -->, must match the filename locale.
  6. Frontmatter parses cleanly; heading count of locale body matches source body (+/- 0).
  7. categories.json's per-category i18n covers all locales declared in manifest.json.
  8. Top-level description is 1-1024 chars (spec); top-level name is 1-64 chars (spec).

Exit codes:
  0 = pass
  1 = validation errors found
  2 = unexpected runtime error / missing dependencies

Usage:
  python3 scripts/i18n/validate-i18n.py            # validate everything under repo root
  python3 scripts/i18n/validate-i18n.py skills/web-access  # validate single skill
  python3 scripts/i18n/validate-i18n.py --json     # machine-readable output
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError:
    sys.stderr.write("ERROR: PyYAML is required. Install with: pip install pyyaml\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]

NAME_PATTERN = re.compile(r"^(?!-)(?!.*--)[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
RESERVED_NAMES = {"anthropic", "claude"}
LOCALE_PATTERN = re.compile(r"^[a-z]{2,3}(?:-[A-Z]{2})?$")
LOCALE_HEADER_PATTERN = re.compile(r"^<!--\s*locale:\s*([a-zA-Z-]+)\s*-->")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+\S", re.MULTILINE)
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


@dataclass
class Issue:
    path: str
    rule: str
    message: str
    severity: str = "error"

    def to_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity,
        }


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)

    def add(self, issue: Issue) -> None:
        self.issues.append(issue)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str | None, str | None]:
    """Return (frontmatter_dict, body, error). All three Nones means file is empty."""
    if not text.strip():
        return None, None, "empty file"
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, None, "no YAML frontmatter (file must start with '---')"
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return None, None, f"YAML parse error: {e}"
    if not isinstance(fm, dict):
        return None, None, "frontmatter must be a YAML mapping"
    return fm, m.group(2), None


def heading_count(text: str) -> int:
    return len(HEADING_PATTERN.findall(text or ""))


def validate_skill(skill_dir: Path, report: Report, declared_locales: set[str] | None = None) -> None:
    """Validate one skill directory (must contain SKILL.md)."""
    rel_dir = skill_dir.relative_to(REPO_ROOT).as_posix()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        report.add(Issue(rel_dir, "structure", "SKILL.md not found"))
        return

    text = skill_md.read_text(encoding="utf-8")
    fm, body, err = parse_frontmatter(text)
    if err:
        report.add(Issue(f"{rel_dir}/SKILL.md", "rule-6", err))
        return
    assert fm is not None and body is not None

    name = fm.get("name", "")
    description = fm.get("description", "")

    # Rule 1: name spec-compliance + matches dir
    if not isinstance(name, str) or not NAME_PATTERN.match(name) or len(name) > 64 or name in RESERVED_NAMES:
        report.add(Issue(
            f"{rel_dir}/SKILL.md", "rule-1",
            f"name {name!r} is not spec-compliant (must be lowercase ASCII + hyphens, 1-64 chars, not 'anthropic'/'claude')"
        ))
    if name != skill_dir.name:
        report.add(Issue(
            f"{rel_dir}/SKILL.md", "rule-1",
            f"name '{name}' must equal parent dir name '{skill_dir.name}' (spec)"
        ))

    # Rule 8: description length
    if not isinstance(description, str) or not (1 <= len(description) <= 1024):
        report.add(Issue(
            f"{rel_dir}/SKILL.md", "rule-8",
            f"description must be 1-1024 chars (got {len(description) if isinstance(description, str) else 'non-string'})"
        ))

    # Rule 2/3/4: i18n block
    metadata = fm.get("metadata") or {}
    i18n = metadata.get("i18n") if isinstance(metadata, dict) else None
    if not isinstance(i18n, dict):
        report.add(Issue(f"{rel_dir}/SKILL.md", "rule-2", "metadata.i18n block missing"))
        return

    default_locale = i18n.get("default_locale")
    source_locale = i18n.get("source_locale")
    locales = i18n.get("locales") or []
    if not isinstance(locales, list) or not all(isinstance(x, str) for x in locales):
        report.add(Issue(f"{rel_dir}/SKILL.md", "rule-2", "metadata.i18n.locales must be a list of strings"))
        return
    locale_set = set(locales)

    for tag in ("default_locale", "source_locale"):
        val = i18n.get(tag)
        if not isinstance(val, str) or not LOCALE_PATTERN.match(val):
            report.add(Issue(f"{rel_dir}/SKILL.md", "rule-2", f"metadata.i18n.{tag} '{val!r}' is not a valid BCP-47 locale"))
        elif val not in locale_set:
            report.add(Issue(f"{rel_dir}/SKILL.md", "rule-2", f"metadata.i18n.{tag} '{val}' not present in metadata.i18n.locales"))

    if declared_locales is not None:
        missing = declared_locales - locale_set
        if missing:
            report.add(Issue(
                f"{rel_dir}/SKILL.md", "rule-7",
                f"manifest declares locales {sorted(declared_locales)} but skill is missing {sorted(missing)}",
                severity="error"
            ))

    # Rule 3: per-locale name/short_desc presence
    source_body_text: str | None = None
    for locale in locales:
        if not LOCALE_PATTERN.match(locale):
            report.add(Issue(f"{rel_dir}/SKILL.md", "rule-3", f"locale '{locale}' is not a valid BCP-47 tag"))
            continue
        payload = i18n.get(locale)
        if not isinstance(payload, dict):
            report.add(Issue(f"{rel_dir}/SKILL.md", "rule-3", f"metadata.i18n.{locale} block missing or not a mapping"))
            continue
        for required in ("name", "short_desc"):
            v = payload.get(required)
            if not isinstance(v, str) or not v.strip():
                report.add(Issue(
                    f"{rel_dir}/SKILL.md", "rule-3",
                    f"metadata.i18n.{locale}.{required} is missing or empty"
                ))

        # Rule 4: body file presence
        body_path_str = payload.get("body")
        body_text: str | None = None
        if body_path_str:
            if not isinstance(body_path_str, str) or not body_path_str.startswith("./"):
                report.add(Issue(
                    f"{rel_dir}/SKILL.md", "rule-4",
                    f"metadata.i18n.{locale}.body must be a relative path starting with './' (got {body_path_str!r})"
                ))
            else:
                body_file = (skill_dir / body_path_str.removeprefix("./")).resolve()
                if not body_file.is_file():
                    report.add(Issue(
                        f"{rel_dir}/SKILL.md", "rule-4",
                        f"metadata.i18n.{locale}.body points to missing file '{body_path_str}'"
                    ))
                else:
                    body_text = body_file.read_text(encoding="utf-8")
                    # Rule 5: locale header self-check (only when not the root SKILL.md)
                    if body_file.name != "SKILL.md":
                        first_line = body_text.splitlines()[0] if body_text else ""
                        m = LOCALE_HEADER_PATTERN.match(first_line)
                        if m and m.group(1) != locale:
                            report.add(Issue(
                                f"{rel_dir}/{body_file.name}", "rule-5",
                                f"file declares locale '{m.group(1)}' but is referenced as '{locale}'"
                            ))
        else:
            # Fallback to root SKILL.md body (default_locale must have a usable body)
            if locale == default_locale:
                body_text = body
            else:
                # OK to omit body for non-default locales (will fall back at runtime)
                pass

        if locale == source_locale:
            source_body_text = body_text or body  # source defaults to root if not specified

    # Rule 6: heading count consistency between source and other locales' bodies
    if source_body_text is not None:
        source_count = heading_count(source_body_text)
        for locale in locales:
            if locale == source_locale:
                continue
            payload = i18n.get(locale) or {}
            body_path_str = payload.get("body")
            if body_path_str:
                body_file = (skill_dir / body_path_str.removeprefix("./")).resolve()
                if body_file.is_file():
                    other_text = body_file.read_text(encoding="utf-8")
                    other_count = heading_count(other_text)
                    if other_count != source_count:
                        report.add(Issue(
                            f"{rel_dir}/{body_file.name}", "rule-6",
                            f"heading count {other_count} differs from source ({source_count})",
                            severity="warning",
                        ))


def validate_market_root(report: Report) -> set[str]:
    """Validate manifest.json + categories.json. Returns the declared locale set or empty."""
    manifest_path = REPO_ROOT / "manifest.json"
    categories_path = REPO_ROOT / "categories.json"

    declared: set[str] = set()
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            report.add(Issue("manifest.json", "rule-7", f"JSON parse error: {e}"))
            manifest = {}
        supported = manifest.get("supportedLocales") or []
        if not isinstance(supported, list) or not all(isinstance(x, str) and LOCALE_PATTERN.match(x) for x in supported):
            report.add(Issue("manifest.json", "rule-7", "supportedLocales must be a list of BCP-47 tags"))
        else:
            declared = set(supported)
        default = manifest.get("defaultLocale")
        if declared and default not in declared:
            report.add(Issue("manifest.json", "rule-7", f"defaultLocale '{default}' not in supportedLocales"))

    if categories_path.is_file() and declared:
        try:
            categories = json.loads(categories_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            report.add(Issue("categories.json", "rule-7", f"JSON parse error: {e}"))
            return declared
        for cat_id, cat in categories.items():
            i18n = cat.get("i18n") if isinstance(cat, dict) else None
            if not isinstance(i18n, dict):
                report.add(Issue("categories.json", "rule-7", f"category '{cat_id}' missing i18n block"))
                continue
            for locale in declared:
                payload = i18n.get(locale)
                if not isinstance(payload, dict) or not payload.get("label"):
                    report.add(Issue(
                        "categories.json", "rule-7",
                        f"category '{cat_id}' missing i18n.{locale}.label"
                    ))
    return declared


def iter_skill_dirs(targets: Iterable[Path]) -> Iterable[Path]:
    for t in targets:
        if t.is_file() and t.name == "SKILL.md":
            yield t.parent
        elif t.is_dir() and (t / "SKILL.md").is_file():
            yield t
        elif t.is_dir():
            for child in sorted(t.iterdir()):
                if child.is_dir() and (child / "SKILL.md").is_file():
                    yield child


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Skills or directories to validate (default: repo root)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    report = Report()
    declared_locales = validate_market_root(report)

    if args.paths:
        targets = [Path(p).resolve() for p in args.paths]
    else:
        targets = [REPO_ROOT / "skills"]

    for skill_dir in iter_skill_dirs(targets):
        validate_skill(skill_dir, report, declared_locales=declared_locales or None)

    if args.json:
        json.dump([i.to_dict() for i in report.issues], sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        if not report.issues:
            print("OK: no i18n issues found.")
        else:
            for issue in report.issues:
                marker = "ERROR" if issue.severity == "error" else "WARN "
                print(f"[{marker}] {issue.path} :: {issue.rule} :: {issue.message}")
            errors = sum(1 for i in report.issues if i.severity == "error")
            warns = sum(1 for i in report.issues if i.severity == "warning")
            print(f"\n{errors} error(s), {warns} warning(s).")

    return 1 if report.has_errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(130)
