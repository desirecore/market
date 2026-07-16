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
  9. Skill/Agent counts and builtin skill index match the repository contents.
  10. Skill, Agent, and entry.json category references exist in categories.json.
  11. entry.json pointers have the required marketplace fields, valid inline SVG icons, and safe source URLs.
  12. Market Skills set `disable-model-invocation` to true or omit it; false is prohibited.

Exit codes:
  0 = pass
  1 = validation errors found
  2 = unexpected runtime error / missing dependencies

Usage:
  python3 scripts/i18n/validate-i18n.py            # validate everything under repo root
  python3 scripts/i18n/validate-i18n.py skills/web-access  # validate single skill
  python3 scripts/i18n/validate-i18n.py --online   # also check entry.json source URLs
  python3 scripts/i18n/validate-i18n.py --json     # machine-readable output
"""
from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
from xml.etree import ElementTree
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

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
SAFE_URL_PATTERN = re.compile(r"^https://")


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


def validate_model_invocation_policy(
    frontmatter: dict[str, Any],
    path: str,
    report: Report,
) -> None:
    """Reject market skills that request full-content system-prompt injection."""
    value = frontmatter.get("disable-model-invocation")
    if value is not None and value is not True:
        report.add(Issue(
            path,
            "model-invocation-policy",
            "disable-model-invocation must be true or omitted; automatic full-content injection is prohibited",
        ))


def validate_skill(
    skill_dir: Path,
    report: Report,
    declared_locales: set[str] | None = None,
    category_ids: set[str] | None = None,
) -> None:
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

    validate_model_invocation_policy(fm, f"{rel_dir}/SKILL.md", report)

    name = fm.get("name", "")
    description = fm.get("description", "")
    market = fm.get("market") or {}
    category = market.get("category") if isinstance(market, dict) else None
    if category is None:
        category = fm.get("category")

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

    if category_ids is not None:
        if not isinstance(category, str) or not category.strip():
            report.add(Issue(f"{rel_dir}/SKILL.md", "market-category", "market.category is missing"))
        elif category not in category_ids:
            report.add(Issue(
                f"{rel_dir}/SKILL.md", "market-category",
                f"category '{category}' is not declared in categories.json"
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


def load_json(path: Path, report: Report, rule: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        report.add(Issue(path.relative_to(REPO_ROOT).as_posix(), rule, "file not found"))
        return {}
    except json.JSONDecodeError as e:
        report.add(Issue(path.relative_to(REPO_ROOT).as_posix(), rule, f"JSON parse error: {e}"))
        return {}
    if not isinstance(value, dict):
        report.add(Issue(path.relative_to(REPO_ROOT).as_posix(), rule, "JSON root must be an object"))
        return {}
    return value


def validate_market_root(report: Report) -> tuple[set[str], set[str], dict[str, Any]]:
    """Validate manifest.json + categories.json. Returns locales, categories, manifest."""
    manifest_path = REPO_ROOT / "manifest.json"
    categories_path = REPO_ROOT / "categories.json"

    declared: set[str] = set()
    category_ids: set[str] = set()
    manifest: dict[str, Any] = {}
    if manifest_path.is_file():
        manifest = load_json(manifest_path, report, "rule-7")
        supported = manifest.get("supportedLocales") or []
        if not isinstance(supported, list) or not all(isinstance(x, str) and LOCALE_PATTERN.match(x) for x in supported):
            report.add(Issue("manifest.json", "rule-7", "supportedLocales must be a list of BCP-47 tags"))
        else:
            declared = set(supported)
        default = manifest.get("defaultLocale")
        if declared and default not in declared:
            report.add(Issue("manifest.json", "rule-7", f"defaultLocale '{default}' not in supportedLocales"))

    if categories_path.is_file() and declared:
        categories = load_json(categories_path, report, "rule-7")
        category_ids = set(categories)
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
    return declared, category_ids, manifest


def count_publishable_skills() -> tuple[list[str], list[str]]:
    skill_md_names = sorted(p.parent.name for p in (REPO_ROOT / "skills").glob("*/SKILL.md"))
    entry_names = sorted(p.parent.name for p in (REPO_ROOT / "skills").glob("*/entry.json"))
    return skill_md_names, entry_names


def validate_builtin_skills(report: Report, skill_md_names: list[str]) -> None:
    builtin_path = REPO_ROOT / "builtin-skills.json"
    builtin = load_json(builtin_path, report, "builtin-skills")
    skills = builtin.get("skills")
    if not isinstance(skills, list) or not all(isinstance(x, str) for x in skills):
        report.add(Issue("builtin-skills.json", "builtin-skills", "skills must be a list of strings"))
        return

    expected = sorted(skill_md_names)
    actual = list(skills)
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        order_issue = not missing and not extra
        parts = []
        if missing:
            parts.append(f"missing local SKILL.md skills {missing}")
        if extra:
            parts.append(f"contains non-local skills {extra}")
        if order_issue:
            parts.append("skills list is not sorted")
        report.add(Issue("builtin-skills.json", "builtin-skills", "; ".join(parts)))


def validate_agent_json(report: Report, agent_file: Path, category_ids: set[str]) -> None:
    rel = agent_file.relative_to(REPO_ROOT).as_posix()
    agent = load_json(agent_file, report, "agent-json")
    if not agent:
        return
    if agent.get("id") != agent_file.parent.name:
        report.add(Issue(rel, "agent-json", f"id must equal parent directory '{agent_file.parent.name}'"))
    category = agent.get("category")
    if not isinstance(category, str) or category not in category_ids:
        report.add(Issue(rel, "agent-json", f"category '{category}' is not declared in categories.json"))


def validate_entry_json(report: Report, entry_file: Path, category_ids: set[str], online: bool) -> None:
    rel = entry_file.relative_to(REPO_ROOT).as_posix()
    entry = load_json(entry_file, report, "entry-json")
    if not entry:
        return

    required = ("id", "name", "category", "icon", "maintainer", "stewardship", "license", "redistribution", "source")
    for key in required:
        if key not in entry:
            report.add(Issue(rel, "entry-json", f"missing required field '{key}'"))

    if entry.get("id") != entry_file.parent.name:
        report.add(Issue(rel, "entry-json", f"id must equal parent directory '{entry_file.parent.name}'"))

    category = entry.get("category")
    if not isinstance(category, str) or category not in category_ids:
        report.add(Issue(rel, "entry-json", f"category '{category}' is not declared in categories.json"))

    icon = entry.get("icon")
    if not isinstance(icon, str) or not icon.strip():
        report.add(Issue(rel, "entry-json", "icon must be a non-empty inline SVG string"))
    else:
        try:
            root = ElementTree.fromstring(icon)
            if root.tag != "{http://www.w3.org/2000/svg}svg":
                report.add(Issue(rel, "entry-json", "icon root element must be svg in the SVG namespace"))
            elif not root.get("viewBox"):
                report.add(Issue(rel, "entry-json", "icon SVG must declare a viewBox"))
        except ElementTree.ParseError as exc:
            report.add(Issue(rel, "entry-json", f"icon must be valid SVG XML: {exc}"))

    maintainer = entry.get("maintainer")
    if not isinstance(maintainer, dict) or not isinstance(maintainer.get("name"), str):
        report.add(Issue(rel, "entry-json", "maintainer.name is required"))

    tags = entry.get("tags")
    if tags is not None:
        if not isinstance(tags, list) or not all(isinstance(x, str) for x in tags):
            report.add(Issue(rel, "entry-json", "tags must be a list of strings"))
        elif len(tags) != len(set(tags)):
            report.add(Issue(rel, "entry-json", "tags must be unique"))

    source = entry.get("source")
    if not isinstance(source, dict):
        report.add(Issue(rel, "entry-json", "source must be an object"))
        return
    kind = source.get("kind")
    if kind not in {"git", "web", "zip"}:
        report.add(Issue(rel, "entry-json", f"source.kind '{kind}' must be one of git/web/zip"))
    repo_url = source.get("repoUrl")
    if not isinstance(repo_url, str) or not repo_url.strip():
        report.add(Issue(rel, "entry-json", "source.repoUrl is required"))
    elif not SAFE_URL_PATTERN.match(repo_url):
        report.add(Issue(rel, "entry-json", "source.repoUrl must use https://"))
    elif online:
        validate_url(report, rel, repo_url)


def validate_url(report: Report, path: str, url: str) -> None:
    context = ssl.create_default_context()
    for method in ("HEAD", "GET"):
        try:
            req = Request(url, method=method, headers={"User-Agent": "desirecore-market-validator/1.0"})
            with urlopen(req, timeout=12, context=context) as resp:
                if 200 <= resp.status < 400:
                    return
                report.add(Issue(path, "entry-online", f"{url} returned HTTP {resp.status}"))
                return
        except HTTPError as e:
            if method == "HEAD" and e.code in {403, 405}:
                continue
            report.add(Issue(path, "entry-online", f"{url} returned HTTP {e.code}"))
            return
        except (URLError, TimeoutError, OSError) as e:
            report.add(Issue(path, "entry-online", f"{url} is not reachable: {e}"))
            return


def validate_market_catalog(report: Report, manifest: dict[str, Any], category_ids: set[str], online: bool) -> None:
    agent_files = sorted((REPO_ROOT / "agents").glob("*/agent.json"))
    skill_md_names, entry_names = count_publishable_skills()

    stats = manifest.get("stats")
    if not isinstance(stats, dict):
        report.add(Issue("manifest.json", "market-stats", "stats must be an object"))
    else:
        expected_agents = len(agent_files)
        expected_skills = len(skill_md_names) + len(entry_names)
        if stats.get("totalAgents") != expected_agents:
            report.add(Issue(
                "manifest.json", "market-stats",
                f"stats.totalAgents is {stats.get('totalAgents')}, expected {expected_agents}"
            ))
        if stats.get("totalSkills") != expected_skills:
            report.add(Issue(
                "manifest.json", "market-stats",
                f"stats.totalSkills is {stats.get('totalSkills')}, expected {expected_skills}"
            ))

    features = manifest.get("features") or []
    if isinstance(features, list) and "verified-only" in features:
        for entry_file in sorted((REPO_ROOT / "skills").glob("*/entry.json")):
            entry = load_json(entry_file, report, "entry-json")
            maintainer = entry.get("maintainer") if isinstance(entry, dict) else None
            verified = maintainer.get("verified") if isinstance(maintainer, dict) else None
            if entry.get("stewardship") != "official" or verified is not True:
                report.add(Issue(
                    "manifest.json", "market-features",
                    "features includes 'verified-only' but the market contains non-official or unverified entry.json pointers"
                ))
                break

    validate_builtin_skills(report, skill_md_names)
    for agent_file in agent_files:
        validate_agent_json(report, agent_file, category_ids)
    for entry_file in sorted((REPO_ROOT / "skills").glob("*/entry.json")):
        validate_entry_json(report, entry_file, category_ids, online)


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
    parser.add_argument("--online", action="store_true", help="Check entry.json source URLs with HEAD/GET requests")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    report = Report()
    declared_locales, category_ids, manifest = validate_market_root(report)
    validate_market_catalog(report, manifest, category_ids, online=args.online)

    if args.paths:
        targets = [Path(p).resolve() for p in args.paths]
    else:
        targets = [REPO_ROOT / "skills"]

    for skill_dir in iter_skill_dirs(targets):
        validate_skill(
            skill_dir,
            report,
            declared_locales=declared_locales or None,
            category_ids=category_ids or None,
        )

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
