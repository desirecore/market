#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.23,<5", "pyyaml>=6.0"]
# ///
"""Validate Market ``catalog-metadata.v1.json`` sidecars.

The sidecar is deliberately discovered at one fixed path next to a legacy
``agent.json``, ``SKILL.md`` or ``entry.json``.  It supplements the legacy
file; it never selects an arbitrary metadata path and never declares the
trusted catalog provider identity.

Agents, Teams and Skills are the three catalog item kinds.  A Team listing has
no inline form: it is always ``teams/<id>/entry.json``, a git fork pointer whose
installation forks the team repository and whose update is a ``git pull``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft7Validator, FormatChecker, ValidationError, validators


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "catalog-metadata.v1.schema.json"
AGENT_ENTRY_SCHEMA_NAME = "market-agent-entry.client.schema.json"
TEAM_ENTRY_SCHEMA_NAME = "market-team-entry.client.schema.json"
# Catalog roots that may hold a sidecar, in listing order.
CATALOG_ROOTS = ("agents", "teams", "skills")
ALLOWED_SIDECAR_LOCATIONS = ", ".join(f"{name}/<id>/" for name in CATALOG_ROOTS)
# Team display facts are mirrored in entry.json and the sidecar; neither file may
# declare one the other omits, otherwise the two disagree on what is even known.
TEAM_DISPLAY_FIELDS = (
    "supervisorName",
    "supervisorAgentId",
    "memberCount",
    "memberNames",
    "requiredSkills",
)
SIDECAR_NAME = "catalog-metadata.v1.json"
EXPECTED_SCHEMA_REF = "../../schemas/catalog-metadata.v1.schema.json"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FULL_GIT_REF_RE = re.compile(r"^[a-fA-F0-9]{40}(?:[a-fA-F0-9]{24})?$")
CONTAINER_DIGEST_RE = re.compile(r"^sha256:[a-fA-F0-9]{64}$")


def _client_pattern(validator, pattern, instance, schema):
    # The exported client patterns use ECMAScript ASCII \d; Python's default
    # Unicode \d would admit version strings that the client rejects.
    if validator.is_type(instance, "string") and re.search(pattern, instance, re.ASCII) is None:
        yield ValidationError(f"{instance!r} does not match {pattern!r}")


# The extension is about client pattern semantics; it is shared by every pointer kind.
ClientEntryValidator = validators.extend(Draft7Validator, {"pattern": _client_pattern})


@dataclass(frozen=True)
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
    stats: dict[str, int] = field(default_factory=dict)

    def add(self, path: str, rule: str, message: str, severity: str = "error") -> None:
        self.issues.append(Issue(path, rule, message, severity))

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == "error" for issue in self.issues)


@dataclass(frozen=True)
class LegacyItem:
    kind: str
    item_id: str
    source_type: str
    data: dict[str, Any]
    i18n: dict[str, dict[str, Any]]
    default_locale: str | None
    version: str | None
    category: str | None
    tags: list[str] | None


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(path: Path, report: Report, root: Path, rule: str) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.add(_rel(path, root), rule, f"cannot read JSON object: {exc}")
        return None
    if not isinstance(value, dict):
        report.add(_rel(path, root), rule, "JSON root must be an object")
        return None
    return value


def _read_skill_frontmatter(path: Path, report: Report, root: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        report.add(_rel(path, root), "legacy-read", f"cannot read SKILL.md: {exc}")
        return None
    match = FRONTMATTER_RE.match(text)
    if not match:
        report.add(_rel(path, root), "legacy-read", "SKILL.md has no YAML frontmatter")
        return None
    try:
        value = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        report.add(_rel(path, root), "legacy-read", f"cannot parse YAML frontmatter: {exc}")
        return None
    if not isinstance(value, dict):
        report.add(_rel(path, root), "legacy-read", "SKILL.md frontmatter must be a mapping")
        return None
    return value


def _legacy_i18n(raw: Any, *, short_key: str) -> tuple[dict[str, dict[str, Any]], str | None]:
    if not isinstance(raw, dict):
        return {}, None
    default_locale = raw.get("defaultLocale") or raw.get("default_locale")
    locales_value = raw.get("locales")
    if isinstance(locales_value, dict):
        candidates = locales_value.items()
    else:
        candidates = (
            (key, value)
            for key, value in raw.items()
            if re.fullmatch(r"[a-z]{2,3}(?:-[A-Z]{2})?", str(key))
        )
    locales: dict[str, dict[str, Any]] = {}
    for locale, payload in candidates:
        if not isinstance(payload, dict):
            continue
        normalized: dict[str, Any] = {}
        if isinstance(payload.get("name"), str):
            normalized["name"] = payload["name"]
        summary = payload.get(short_key)
        if isinstance(summary, str):
            normalized["summary"] = summary
        description = payload.get("description") or payload.get("fullDesc")
        if isinstance(description, str):
            normalized["description"] = description
        locales[str(locale)] = normalized
    return locales, default_locale if isinstance(default_locale, str) else None


def _report_entry_schema_errors(
    report: Report,
    legacy_path: Path,
    root: Path,
    validator,
    rule: str,
    data: dict[str, Any],
) -> bool:
    """Validate a raw pointer against the exported client contract.

    Returns True when the pointer is already invalid for the client, in which case
    no sidecar comparison is meaningful: a sidecar must never make an entry.json the
    client rejects look acceptable.
    """
    errors = list(validator.iter_errors(data))
    for error in errors:
        report.add(_rel(legacy_path, root), rule, f"{_json_path(error)}: {error.message}")
    return bool(errors)


def _load_team_pointer(
    sidecar: Path,
    parent: Path,
    report: Report,
    root: Path,
    team_entry_validator,
) -> LegacyItem | None:
    """Load ``teams/<id>/entry.json``.

    A Team listing is a fork pointer and has no inline form: the team body
    (team.json / members.json / shared/) lives in the forked repository, so the
    catalog only ever carries entry.json plus the sidecar.
    """
    pointer_path = parent / "entry.json"
    inline_path = parent / "team.json"
    if inline_path.is_file():
        report.add(
            _rel(inline_path, root),
            "fixed-sidecar-path",
            "team listings are fork pointers; team.json belongs in the forked team repository",
        )
        return None
    if not pointer_path.is_file():
        report.add(
            _rel(sidecar, root),
            "fixed-sidecar-path",
            "team sidecar must be next to a legacy entry.json",
        )
        return None
    data = _read_json(pointer_path, report, root, "legacy-read")
    if data is None:
        return None
    if _report_entry_schema_errors(report, pointer_path, root, team_entry_validator, "team-entry-schema", data):
        return None
    if data.get("id") != parent.name:
        report.add(_rel(pointer_path, root), "legacy-consistency", "entry.id must equal the catalog directory slug")
    i18n, default_locale = _legacy_i18n(data.get("i18n"), short_key="shortDesc")
    return LegacyItem(
        kind="team",
        item_id=parent.name,
        source_type="pointer",
        data=data,
        i18n=i18n,
        default_locale=default_locale,
        # A Team pointer carries no installed version; the catalog registers latestVersion.
        version=data.get("latestVersion"),
        category=data.get("category") if isinstance(data.get("category"), str) else None,
        tags=data.get("tags") if isinstance(data.get("tags"), list) else None,
    )


def load_legacy(sidecar: Path, report: Report, root: Path, entry_validators: dict[str, Any]) -> LegacyItem | None:
    parent = sidecar.parent
    root_kind = parent.parent.name
    if root_kind == "agents":
        inline_path = parent / "agent.json"
        pointer_path = parent / "entry.json"
        if inline_path.is_file() == pointer_path.is_file():
            report.add(
                _rel(sidecar, root),
                "fixed-sidecar-path",
                "agent sidecar must be next to exactly one legacy agent.json or entry.json",
            )
            return None
        is_pointer = pointer_path.is_file()
        legacy_path = pointer_path if is_pointer else inline_path
        data = _read_json(legacy_path, report, root, "legacy-read")
        if data is None:
            return None
        if is_pointer and _report_entry_schema_errors(
            report, legacy_path, root, entry_validators["agent"], "agent-entry-schema", data
        ):
            return None
        if is_pointer and data.get("id") != parent.name:
            report.add(_rel(legacy_path, root), "legacy-consistency", "entry.id must equal the catalog directory slug")
        # The pointer ID is a listing slug, not the upstream AgentFS UUID.
        # Client indexing reads latestVersion for pointers and version for inline metadata.
        version = data.get("latestVersion") if is_pointer else (
            str(data["version"]) if data.get("version") is not None else None
        )
        i18n, default_locale = _legacy_i18n(data.get("i18n"), short_key="shortDesc")
        return LegacyItem(
            kind="agent",
            item_id=parent.name,
            source_type="pointer" if is_pointer else "agent",
            data=data,
            i18n=i18n,
            default_locale=default_locale,
            version=version,
            category=data.get("category") if isinstance(data.get("category"), str) else None,
            tags=data.get("tags") if isinstance(data.get("tags"), list) else None,
        )

    if root_kind == "teams":
        return _load_team_pointer(sidecar, parent, report, root, entry_validators["team"])

    if root_kind != "skills":
        report.add(
            _rel(sidecar, root),
            "fixed-sidecar-path",
            f"{SIDECAR_NAME} is only allowed at {ALLOWED_SIDECAR_LOCATIONS}",
        )
        return None

    pointer_path = parent / "entry.json"
    builtin_path = parent / "SKILL.md"
    if pointer_path.is_file() == builtin_path.is_file():
        report.add(
            _rel(sidecar, root),
            "fixed-sidecar-path",
            "skill sidecar must be next to exactly one legacy entry.json or SKILL.md",
        )
        return None

    if pointer_path.is_file():
        data = _read_json(pointer_path, report, root, "legacy-read")
        if data is None:
            return None
        i18n, default_locale = _legacy_i18n(data.get("i18n"), short_key="shortDesc")
        return LegacyItem(
            kind="skill",
            item_id=parent.name,
            source_type="pointer",
            data=data,
            i18n=i18n,
            default_locale=default_locale,
            version=str(data["version"]) if data.get("version") is not None else None,
            category=data.get("category") if isinstance(data.get("category"), str) else None,
            tags=data.get("tags") if isinstance(data.get("tags"), list) else None,
        )

    data = _read_skill_frontmatter(builtin_path, report, root)
    if data is None:
        return None
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    i18n_raw = metadata.get("i18n") if isinstance(metadata, dict) else None
    i18n, default_locale = _legacy_i18n(i18n_raw, short_key="short_desc")
    market = data.get("market") if isinstance(data.get("market"), dict) else {}
    tags = data.get("tags") if isinstance(data.get("tags"), list) else None
    return LegacyItem(
        kind="skill",
        item_id=parent.name,
        source_type="builtin",
        data=data,
        i18n=i18n,
        default_locale=default_locale,
        version=str(data["version"]) if data.get("version") is not None else None,
        category=(market.get("category") if isinstance(market.get("category"), str) else None),
        tags=tags,
    )


def _json_path(error: Any) -> str:
    parts = [str(part) for part in error.absolute_path]
    return ".".join(parts) if parts else "$"


def _compare(report: Report, path: str, field: str, sidecar: Any, legacy: Any) -> None:
    if legacy is not None and sidecar != legacy:
        report.add(path, "legacy-consistency", f"{field} differs from the legacy value")


def _known_timestamp_value(value: Any) -> str | None:
    if isinstance(value, dict) and value.get("state") == "known" and isinstance(value.get("value"), str):
        return value["value"]
    return None


def _content_is_immutable(content: Any) -> bool:
    if not isinstance(content, dict):
        return False
    kind = content.get("kind")
    ref = content.get("ref")
    digest = content.get("sha256")
    if kind == "git":
        return isinstance(ref, str) and FULL_GIT_REF_RE.fullmatch(ref) is not None
    if kind == "container":
        return isinstance(ref, str) and CONTAINER_DIGEST_RE.fullmatch(ref) is not None
    if kind in {"web", "zip", "release", "package"}:
        return isinstance(digest, str) and re.fullmatch(r"[a-fA-F0-9]{64}", digest) is not None
    return False


def _validate_i18n(
    report: Report,
    rel: str,
    sidecar: dict[str, Any],
    legacy: LegacyItem,
    supported_locales: set[str],
) -> None:
    presentation = sidecar.get("presentation")
    if not isinstance(presentation, dict):
        return
    default_locale = presentation.get("defaultLocale")
    i18n = presentation.get("i18n")
    if not isinstance(i18n, dict):
        return
    if default_locale not in i18n:
        report.add(rel, "i18n", "presentation.defaultLocale must exist in presentation.i18n")
    missing = sorted(supported_locales - set(i18n))
    if missing:
        report.add(rel, "i18n", f"presentation.i18n is missing Market locales {missing}")
    if legacy.default_locale is not None:
        _compare(report, rel, "presentation.defaultLocale", default_locale, legacy.default_locale)

    for locale, legacy_payload in legacy.i18n.items():
        payload = i18n.get(locale)
        if not isinstance(payload, dict):
            report.add(rel, "legacy-consistency", f"presentation.i18n.{locale} is missing")
            continue
        for key in ("name", "summary", "description"):
            if key in legacy_payload:
                _compare(
                    report,
                    rel,
                    f"presentation.i18n.{locale}.{key}",
                    payload.get(key),
                    legacy_payload[key],
                )

    payloads = [
        (locale, value.get("name"), value.get("summary"))
        for locale, value in sorted(i18n.items())
        if isinstance(value, dict)
    ]
    if len(payloads) > 1 and len({(name, summary) for _, name, summary in payloads}) == 1:
        report.add(
            rel,
            "i18n-freshness",
            "all locale name/summary payloads are identical; translation requires explicit review",
            severity="warning",
        )


def _validate_content_consistency(
    report: Report,
    rel: str,
    sidecar: dict[str, Any],
    legacy: LegacyItem,
) -> None:
    if legacy.source_type != "pointer":
        return
    provenance = sidecar.get("provenance")
    content = provenance.get("content") if isinstance(provenance, dict) else None
    source = legacy.data.get("source")
    if not isinstance(content, dict) or not isinstance(source, dict):
        return
    mapping = {
        "kind": "kind",
        "url": "repoUrl",
        "path": "path",
        "ref": "ref",
        "sha256": "sha256",
    }
    for sidecar_key, legacy_key in mapping.items():
        legacy_value = source.get(legacy_key)
        if legacy.kind in {"agent", "team"}:
            declared_value = content.get(sidecar_key)
            # A sidecar must describe the exact pointer that the client installs,
            # not add a different subdirectory or pin that entry.json never uses.
            if sidecar_key in {"path", "ref"}:
                declared_value = None if declared_value == "" else declared_value
                legacy_value = None if legacy_value == "" else legacy_value
            if declared_value != legacy_value:
                label = "Agent" if legacy.kind == "agent" else "Team"
                report.add(rel, "legacy-consistency", f"provenance.content.{sidecar_key} differs from the {label} pointer")
        elif legacy_value is not None:
            _compare(
                report,
                rel,
                f"provenance.content.{sidecar_key}",
                content.get(sidecar_key),
                legacy_value,
            )


def _validate_governance_consistency(
    report: Report,
    rel: str,
    sidecar: dict[str, Any],
    legacy: LegacyItem,
) -> None:
    governance = sidecar.get("governance")
    if not isinstance(governance, dict):
        return
    legacy_governance = legacy.data
    if legacy.source_type == "builtin":
        market = legacy.data.get("market")
        legacy_governance = market if isinstance(market, dict) else {}

    for field in ("stewardship", "redistribution"):
        if legacy_governance.get(field) is not None and governance.get(field) is not None:
            _compare(report, rel, f"governance.{field}", governance.get(field), legacy_governance[field])

    license_value = legacy.data.get("license")
    license_fact = governance.get("license")
    if license_value is not None and isinstance(license_fact, dict):
        if license_fact.get("state") != "known":
            report.add(
                rel,
                "legacy-license-unverified",
                "legacy license text has no sidecar evidence and remains unknown",
                severity="warning",
            )
        else:
            _compare(report, rel, "governance.license.value", license_fact.get("value"), license_value)

    legacy_maintainer = legacy_governance.get("maintainer")
    maintainer_field = "upstreamMaintainer" if legacy.source_type == "pointer" else "listingMaintainer"
    sidecar_maintainer = governance.get(maintainer_field)
    if isinstance(legacy_maintainer, dict) and isinstance(sidecar_maintainer, dict):
        for field in ("name", "url", "verified"):
            if legacy_maintainer.get(field) is not None:
                _compare(
                    report,
                    rel,
                    f"governance.{maintainer_field}.{field}",
                    sidecar_maintainer.get(field),
                    legacy_maintainer[field],
                )


def _validate_license_evidence(
    report: Report,
    rel: str,
    sidecar: dict[str, Any],
    legacy: LegacyItem,
    item_dir: Path,
) -> None:
    """Make ``evidencePath`` a checkable claim rather than a well-formed string.

    The schema only constrains the shape, not what the path is relative to, and the
    two readings disagree exactly where it matters:

    * vendored content (builtin Skills, inline Agents) ships inside this repository,
      so the evidence file must be present here and is checked directly;
    * a pointer distributes nothing, so its evidence can only live in the upstream
      snapshot. This validator cannot read that offline, so an unpinned pointer is
      flagged instead: the claim is about whatever HEAD happens to be and nobody can
      check it. That stays a warning, because an installable pointer is already
      required to be pinned by ``installable-evidence`` — this branch is only ever
      reached by a listing-only entry, which is explicitly allowed to be unpinned and
      installs nothing on the strength of the claim.
    """
    governance = sidecar.get("governance")
    if not isinstance(governance, dict):
        return
    license_fact = governance.get("license")
    compliance = governance.get("compliance")
    candidates: list[tuple[str, Any]] = []
    if isinstance(license_fact, dict):
        candidates.append(("license.evidencePath", license_fact.get("evidencePath")))
    if isinstance(compliance, dict):
        for key in ("licenseEvidencePath", "noticePath"):
            candidates.append((f"compliance.{key}", compliance.get(key)))

    pinned = _content_is_immutable((sidecar.get("provenance") or {}).get("content"))
    for field, value in candidates:
        if not isinstance(value, str) or not value:
            continue
        if legacy.source_type == "pointer":
            if not pinned:
                report.add(
                    rel,
                    "license-evidence",
                    f"{field} names evidence inside the upstream snapshot but provenance.content is not "
                    "pinned to an immutable ref or digest, so the claim is about a moving target and "
                    "cannot be checked",
                    severity="warning",
                )
        elif not (item_dir / value).is_file():
            report.add(
                rel,
                "license-evidence",
                f"{field} {value!r} does not exist in the catalog item directory",
            )


def _validate_team_spec(report: Report, rel: str, sidecar: dict[str, Any], legacy: LegacyItem) -> None:
    """Keep the sidecar Team facts identical to the entry.json Team facts.

    The comparison is symmetric on purpose: a sidecar must not synthesize a
    supervisor, member count or required-Skill list that the pointer never
    declared, and it must not drop one the pointer did declare.
    """
    spec = sidecar.get("spec")
    if not isinstance(spec, dict):
        return
    for field in TEAM_DISPLAY_FIELDS:
        if spec.get(field) != legacy.data.get(field):
            report.add(rel, "legacy-consistency", f"spec.{field} differs from the Team pointer")


def _validate_collection(
    report: Report,
    rel: str,
    sidecar: dict[str, Any],
    legacy: LegacyItem,
    supported_locales: set[str],
) -> None:
    legacy_children = legacy.data.get("children")
    spec = sidecar.get("spec")
    collection = spec.get("collection") if isinstance(spec, dict) else None
    sidecar_children = collection.get("children") if isinstance(collection, dict) else None

    if isinstance(legacy_children, list) != isinstance(sidecar_children, list):
        report.add(rel, "collection-identity", "sidecar collection presence must match legacy children")
        return
    if not isinstance(legacy_children, list) or not isinstance(sidecar_children, list):
        return

    _compare(report, rel, "spec.collection.role", collection.get("role"), "parent")
    _compare(report, rel, "spec.collection.childCount", collection.get("childCount"), len(legacy_children))

    identities = [child.get("identity") for child in sidecar_children if isinstance(child, dict)]
    ids = [identity.get("id") for identity in identities if isinstance(identity, dict)]
    paths = [child.get("path") for child in sidecar_children if isinstance(child, dict)]
    if len(ids) != len(set(ids)):
        report.add(rel, "collection-identity", "collection child IDs must be unique")
    if len(paths) != len(set(paths)):
        report.add(rel, "collection-identity", "collection child paths must be unique")

    if len(sidecar_children) != len(legacy_children):
        report.add(
            rel,
            "collection-identity",
            f"sidecar declares {len(sidecar_children)} children but legacy declares {len(legacy_children)}",
        )
        return

    identical_locale_children: list[str] = []
    for index, (child, legacy_child) in enumerate(zip(sidecar_children, legacy_children)):
        if not isinstance(child, dict) or not isinstance(legacy_child, dict):
            continue
        identity = child.get("identity")
        if not isinstance(identity, dict):
            continue
        _compare(
            report,
            rel,
            f"spec.collection.children[{index}].identity.id",
            identity.get("id"),
            legacy_child.get("id"),
        )
        _compare(
            report,
            rel,
            f"spec.collection.children[{index}].identity.parentId",
            identity.get("parentId"),
            legacy.item_id,
        )
        _compare(
            report,
            rel,
            f"spec.collection.children[{index}].path",
            child.get("path"),
            legacy_child.get("path"),
        )
        presentation = child.get("presentation")
        child_i18n = presentation.get("i18n") if isinstance(presentation, dict) else None
        if isinstance(child_i18n, dict):
            missing_locales = sorted(supported_locales - set(child_i18n))
            if missing_locales:
                report.add(
                    rel,
                    "i18n",
                    f"collection child {identity.get('id')!r} is missing Market locales {missing_locales}",
                )
            locale_payloads = [
                (payload.get("name"), payload.get("summary"))
                for payload in child_i18n.values()
                if isinstance(payload, dict)
            ]
            if len(locale_payloads) > 1 and len(set(locale_payloads)) == 1:
                identical_locale_children.append(str(identity.get("id")))

            legacy_child_i18n = legacy_child.get("i18n")
            if isinstance(legacy_child_i18n, dict):
                for locale, legacy_payload in legacy_child_i18n.items():
                    payload = child_i18n.get(locale)
                    if not isinstance(payload, dict) or not isinstance(legacy_payload, dict):
                        report.add(
                            rel,
                            "legacy-consistency",
                            f"collection child {identity.get('id')!r} is missing legacy locale {locale!r}",
                        )
                        continue
                    if legacy_payload.get("shortDesc") is not None:
                        _compare(
                            report,
                            rel,
                            f"spec.collection.children[{index}].presentation.i18n.{locale}.summary",
                            payload.get("summary"),
                            legacy_payload.get("shortDesc"),
                        )
                    if legacy_child.get("name") is not None:
                        _compare(
                            report,
                            rel,
                            f"spec.collection.children[{index}].presentation.i18n.{locale}.name",
                            payload.get("name"),
                            legacy_child.get("name"),
                        )
        legacy_version = legacy_child.get("version")
        release = child.get("release")
        if legacy_version is not None and isinstance(release, dict):
            if release.get("state") != "known":
                report.add(
                    rel,
                    "legacy-consistency",
                    f"spec.collection.children[{index}].release must preserve legacy version",
                )
            else:
                _compare(
                    report,
                    rel,
                    f"spec.collection.children[{index}].release.version",
                    release.get("version"),
                    str(legacy_version),
                )
        if legacy_version is None and isinstance(release, dict) and release.get("state") == "known":
            report.add(
                rel,
                "collection-version",
                f"child {identity.get('id')!r} has no legacy/upstream version; sidecar must not synthesize one",
            )

    if identical_locale_children:
        preview = ", ".join(identical_locale_children[:5])
        suffix = "" if len(identical_locale_children) <= 5 else ", …"
        report.add(
            rel,
            "i18n-freshness",
            f"{len(identical_locale_children)} collection child locale payload(s) are identical "
            f"({preview}{suffix}); translation requires explicit review",
            severity="warning",
        )


def validate_sidecar(
    sidecar_path: Path,
    validator: Draft7Validator,
    report: Report,
    root: Path,
    supported_locales: set[str],
    entry_validators: dict[str, Any],
) -> None:
    rel = _rel(sidecar_path, root)
    sidecar = _read_json(sidecar_path, report, root, "catalog-schema")
    if sidecar is None:
        return
    for error in sorted(validator.iter_errors(sidecar), key=lambda item: list(item.absolute_path)):
        report.add(rel, "catalog-schema", f"{_json_path(error)}: {error.message}")
    if any(issue.path == rel and issue.rule == "catalog-schema" for issue in report.issues):
        return

    legacy = load_legacy(sidecar_path, report, root, entry_validators)
    if legacy is None:
        return
    identity = sidecar["identity"]
    _compare(report, rel, "identity.kind", identity.get("kind"), legacy.kind)
    _compare(report, rel, "identity.id", identity.get("id"), legacy.item_id)
    if identity.get("parentId") is not None:
        report.add(rel, "collection-identity", "top-level Market sidecar identity must not declare parentId")
    if sidecar.get("$schema") not in (None, EXPECTED_SCHEMA_REF):
        report.add(rel, "fixed-sidecar-path", f"$schema must be {EXPECTED_SCHEMA_REF!r}")

    presentation = sidecar.get("presentation", {})
    _compare(report, rel, "presentation.category", presentation.get("category"), legacy.category)
    if legacy.tags is not None:
        _compare(report, rel, "presentation.tags", presentation.get("tags"), legacy.tags)
    _validate_i18n(report, rel, sidecar, legacy, supported_locales)

    release = sidecar.get("release")
    spec = sidecar.get("spec")
    system_agent = (
        legacy.kind == "agent"
        and isinstance(spec, dict)
        and spec.get("installPolicy") == "system"
        and spec.get("updatePolicy") == "repository"
    )
    if system_agent:
        if isinstance(release, dict) and release.get("state") != "unknown":
            report.add(rel, "agent-policy", "system Agent metadata revision must not be exposed as a content release")
        release_published_at = sidecar.get("timestamps", {}).get("releasePublishedAt")
        if isinstance(release_published_at, dict) and release_published_at.get("state") != "unknown":
            report.add(
                rel,
                "agent-policy",
                "system Agent metadata revision must not be exposed as a content release timestamp",
            )
    elif legacy.version is not None and isinstance(release, dict):
        if release.get("state") != "known":
            report.add(rel, "legacy-consistency", "release must preserve the legacy version")
        else:
            _compare(report, rel, "release.version", release.get("version"), legacy.version)

    if legacy.kind == "agent" and legacy.source_type == "pointer":
        for field in ("installPolicy", "updatePolicy"):
            # Ordinary pointers default to market/market in the client. A sidecar
            # cannot turn an omitted pair into a system/repository listing.
            _compare(report, rel, f"spec.{field}", spec.get(field, "market"), legacy.data.get(field, "market"))
        _compare(
            report, rel, "compatibility.requiredClientVersion",
            sidecar["compatibility"].get("requiredClientVersion"), legacy.data.get("requiredClientVersion"),
        )

    if legacy.kind == "team":
        # Teams are always fork-installed and git-pull-updated, so there is no
        # policy pair to reconcile; the display facts and the client floor are.
        _validate_team_spec(report, rel, sidecar, legacy)
        # Symmetric on purpose: the upgrade gate is enforced from entry.json, which is
        # what the client reads. A floor that exists only in the sidecar would let a
        # listing look version-gated while the client still offers it for install.
        if sidecar["compatibility"].get("requiredClientVersion") != legacy.data.get("requiredClientVersion"):
            report.add(rel, "legacy-consistency", "compatibility.requiredClientVersion differs from the Team pointer")

    _validate_content_consistency(report, rel, sidecar, legacy)
    _validate_governance_consistency(report, rel, sidecar, legacy)
    _validate_license_evidence(report, rel, sidecar, legacy, sidecar_path.parent)
    _validate_collection(report, rel, sidecar, legacy, supported_locales)

    governance = sidecar.get("governance")
    provenance = sidecar.get("provenance")
    timestamps = sidecar.get("timestamps")
    if isinstance(governance, dict) and governance.get("availability") == "installable":
        content = provenance.get("content") if isinstance(provenance, dict) else None
        license_fact = governance.get("license")
        reviewed_at = timestamps.get("reviewedAt") if isinstance(timestamps, dict) else None
        compliance = governance.get("compliance")
        maintainer = governance.get("listingMaintainer")

        # Builtin Skills are already delivered by the trusted Market bootstrap.
        # Missing governance evidence must remain visible, but it must not silently
        # disable their existing installation path. A Market-installed Agent still
        # uses the strict evidence gate below; a system Agent is schema-locked to
        # listing-only and therefore never enters this installable branch.
        if legacy.source_type == "builtin":
            if not isinstance(license_fact, dict) or license_fact.get("state") != "known" or not license_fact.get("evidencePath"):
                report.add(
                    rel,
                    "missing-license-evidence",
                    "installable builtin content has no verified per-item license evidence",
                    severity="warning",
                )
            if _known_timestamp_value(reviewed_at) is None or not isinstance(compliance, dict):
                report.add(
                    rel,
                    "missing-review-evidence",
                    "installable builtin content has no ref-bound governance review",
                    severity="warning",
                )
            if not isinstance(maintainer, dict) or maintainer.get("verified") is not True:
                report.add(
                    rel,
                    "missing-maintainer-evidence",
                    "installable builtin content has no verified listing maintainer",
                    severity="warning",
                )
            if governance.get("stewardship") != "official" and not isinstance(content, dict):
                report.add(
                    rel,
                    "missing-content-evidence",
                    "vendored builtin content has no explicit upstream content provenance",
                    severity="warning",
                )
            return

        if legacy.kind in {"agent", "team"} and legacy.source_type == "pointer":
            if not _content_is_immutable(legacy.data.get("source")):
                label = "Agent" if legacy.kind == "agent" else "Team"
                report.add(
                    rel, "installable-evidence",
                    f"installable {label} entry.source must itself declare an immutable ref or SHA-256 digest",
                )

        if not _content_is_immutable(content):
            report.add(rel, "installable-evidence", "installable content must have an immutable ref or SHA-256 digest")
        if not isinstance(license_fact, dict) or license_fact.get("state") != "known":
            report.add(rel, "installable-evidence", "installable content must have a known license")
        if _known_timestamp_value(reviewed_at) is None:
            report.add(rel, "installable-evidence", "installable content must have a known reviewedAt timestamp")
        if not isinstance(compliance, dict):
            report.add(rel, "installable-evidence", "installable content must include compliance evidence")
        else:
            content_ref = None
            if isinstance(content, dict):
                content_ref = content.get("ref") or content.get("sha256")
            if content_ref is not None and compliance.get("reviewedRef") != content_ref:
                report.add(rel, "installable-evidence", "compliance.reviewedRef must match the immutable content ref/digest")
            if compliance.get("reviewedAt") != _known_timestamp_value(reviewed_at):
                report.add(rel, "installable-evidence", "compliance.reviewedAt must equal timestamps.reviewedAt")


def _discover_sidecars(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob(SIDECAR_NAME) if ".git" not in path.parts)


def _load_supported_locales(root: Path, report: Report) -> set[str]:
    manifest = _read_json(root / "manifest.json", report, root, "market-stats")
    if manifest is None:
        return set()
    locales = manifest.get("supportedLocales")
    if not isinstance(locales, list) or not all(isinstance(locale, str) for locale in locales):
        report.add("manifest.json", "market-stats", "supportedLocales must be a list of strings")
        return set()
    return set(locales)


def _validate_stats(root: Path, report: Report, sidecars: Iterable[Path]) -> None:
    agent_count = sum(1 for _ in (root / "agents").glob("*/agent.json")) + sum(
        1 for _ in (root / "agents").glob("*/entry.json")
    )
    # A Team has no inline form, so entry.json alone is the publishable unit.
    team_count = sum(1 for _ in (root / "teams").glob("*/entry.json"))
    builtin_count = sum(1 for _ in (root / "skills").glob("*/SKILL.md"))
    pointer_count = sum(1 for _ in (root / "skills").glob("*/entry.json"))
    collection_count = 0
    child_count = 0
    for entry_path in (root / "skills").glob("*/entry.json"):
        try:
            entry = json.loads(entry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        children = entry.get("children") if isinstance(entry, dict) else None
        if isinstance(children, list):
            collection_count += 1
            child_count += len(children)
    sidecar_list = list(sidecars)
    report.stats = {
        "agents": agent_count,
        "teams": team_count,
        "builtinSkills": builtin_count,
        "pointerSkills": pointer_count,
        "publishableSkills": builtin_count + pointer_count,
        "collections": collection_count,
        "collectionChildren": child_count,
        "sidecars": len(sidecar_list),
    }

    manifest = _read_json(root / "manifest.json", report, root, "market-stats")
    stats = manifest.get("stats") if isinstance(manifest, dict) else None
    if not isinstance(stats, dict):
        report.add("manifest.json", "market-stats", "stats must be an object")
        return
    if stats.get("totalAgents") != agent_count:
        report.add("manifest.json", "market-stats", f"stats.totalAgents must be {agent_count}")
    if stats.get("totalSkills") != builtin_count + pointer_count:
        report.add("manifest.json", "market-stats", f"stats.totalSkills must be {builtin_count + pointer_count}")
    # The client stats schema keeps totalTeams optional so a catalog with no teams
    # stays valid; once a team exists, or the key is declared at all, it must be exact.
    declared_teams = stats.get("totalTeams")
    if (team_count > 0 or declared_teams is not None) and declared_teams != team_count:
        report.add("manifest.json", "market-stats", f"stats.totalTeams must be {team_count}")


def validate_repository(root: Path = REPO_ROOT, *, require_complete: bool = False) -> Report:
    root = root.resolve()
    report = Report()
    schema_path = root / "schemas" / "catalog-metadata.v1.schema.json"
    schema = _read_json(schema_path, report, root, "catalog-schema")
    if schema is None:
        return report
    try:
        Draft7Validator.check_schema(schema)
    except Exception as exc:  # jsonschema raises several SchemaError subclasses
        report.add(_rel(schema_path, root), "catalog-schema", f"invalid JSON Schema: {exc}")
        return report
    entry_validators: dict[str, Any] = {}
    for kind, schema_name, rule in (
        ("agent", AGENT_ENTRY_SCHEMA_NAME, "agent-entry-schema"),
        ("team", TEAM_ENTRY_SCHEMA_NAME, "team-entry-schema"),
    ):
        entry_schema = _read_json(root / "schemas" / schema_name, report, root, rule)
        if entry_schema is None:
            return report
        try:
            ClientEntryValidator.check_schema(entry_schema)
        except Exception as exc:
            report.add(f"schemas/{schema_name}", rule, f"invalid JSON Schema: {exc}")
            return report
        entry_validators[kind] = ClientEntryValidator(entry_schema, format_checker=FormatChecker())
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    sidecars = _discover_sidecars(root)
    supported_locales = _load_supported_locales(root, report)

    catalog_roots = {root / name for name in CATALOG_ROOTS}
    for sidecar in sidecars:
        if sidecar.parent.parent not in catalog_roots:
            report.add(
                _rel(sidecar, root),
                "fixed-sidecar-path",
                f"{SIDECAR_NAME} is only allowed at {ALLOWED_SIDECAR_LOCATIONS}",
            )
            continue
        validate_sidecar(sidecar, validator, report, root, supported_locales, entry_validators)

    _validate_stats(root, report, sidecars)
    if require_complete:
        expected = (
            report.stats.get("agents", 0)
            + report.stats.get("teams", 0)
            + report.stats.get("publishableSkills", 0)
        )
        actual = report.stats.get("sidecars", 0)
        if actual != expected:
            report.add(
                ".",
                "sidecar-coverage",
                f"complete migration requires {expected} sidecars, found {actual}",
            )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit stable machine-readable JSON")
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="require one sidecar for every publishable top-level Agent, Team and Skill",
    )
    args = parser.parse_args(argv)
    report = validate_repository(require_complete=args.require_complete)
    if args.json:
        json.dump(
            {"stats": report.stats, "issues": [issue.to_dict() for issue in report.issues]},
            sys.stdout,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        sys.stdout.write("\n")
    else:
        for issue in report.issues:
            marker = "ERROR" if issue.severity == "error" else "WARN "
            print(f"[{marker}] {issue.path} :: {issue.rule} :: {issue.message}")
        summary = ", ".join(f"{key}={value}" for key, value in report.stats.items())
        if report.issues:
            errors = sum(issue.severity == "error" for issue in report.issues)
            warnings = sum(issue.severity == "warning" for issue in report.issues)
            print(f"\n{errors} error(s), {warnings} warning(s). {summary}")
        else:
            print(f"OK: catalog metadata valid. {summary}")
    return 1 if report.has_errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
