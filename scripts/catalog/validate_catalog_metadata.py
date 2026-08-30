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
from jsonschema import Draft7Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "catalog-metadata.v1.schema.json"
SIDECAR_NAME = "catalog-metadata.v1.json"
EXPECTED_SCHEMA_REF = "../../schemas/catalog-metadata.v1.schema.json"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FULL_GIT_REF_RE = re.compile(r"^[a-fA-F0-9]{40}(?:[a-fA-F0-9]{24})?$")
CONTAINER_DIGEST_RE = re.compile(r"^sha256:[a-fA-F0-9]{64}$")


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


def load_legacy(sidecar: Path, report: Report, root: Path) -> LegacyItem | None:
    parent = sidecar.parent
    root_kind = parent.parent.name
    if root_kind == "agents":
        legacy_path = parent / "agent.json"
        data = _read_json(legacy_path, report, root, "legacy-read")
        if data is None:
            return None
        i18n, default_locale = _legacy_i18n(data.get("i18n"), short_key="shortDesc")
        return LegacyItem(
            kind="agent",
            item_id=parent.name,
            source_type="agent",
            data=data,
            i18n=i18n,
            default_locale=default_locale,
            version=str(data["version"]) if data.get("version") is not None else None,
            category=data.get("category") if isinstance(data.get("category"), str) else None,
            tags=data.get("tags") if isinstance(data.get("tags"), list) else None,
        )

    if root_kind != "skills":
        report.add(
            _rel(sidecar, root),
            "fixed-sidecar-path",
            f"{SIDECAR_NAME} is only allowed at agents/<id>/ or skills/<id>/",
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
        if legacy_value is not None:
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
) -> None:
    rel = _rel(sidecar_path, root)
    sidecar = _read_json(sidecar_path, report, root, "catalog-schema")
    if sidecar is None:
        return
    for error in sorted(validator.iter_errors(sidecar), key=lambda item: list(item.absolute_path)):
        report.add(rel, "catalog-schema", f"{_json_path(error)}: {error.message}")
    if any(issue.path == rel and issue.rule == "catalog-schema" for issue in report.issues):
        return

    legacy = load_legacy(sidecar_path, report, root)
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
    if legacy.version is not None and isinstance(release, dict):
        if release.get("state") != "known":
            report.add(rel, "legacy-consistency", "release must preserve the legacy version")
        else:
            _compare(report, rel, "release.version", release.get("version"), legacy.version)

    _validate_content_consistency(report, rel, sidecar, legacy)
    _validate_governance_consistency(report, rel, sidecar, legacy)
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
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    sidecars = _discover_sidecars(root)
    supported_locales = _load_supported_locales(root, report)

    for sidecar in sidecars:
        if sidecar.parent.parent not in {root / "agents", root / "skills"}:
            report.add(
                _rel(sidecar, root),
                "fixed-sidecar-path",
                f"{SIDECAR_NAME} is only allowed at agents/<id>/ or skills/<id>/",
            )
            continue
        validate_sidecar(sidecar, validator, report, root, supported_locales)

    _validate_stats(root, report, sidecars)
    if require_complete:
        expected = report.stats.get("agents", 0) + report.stats.get("publishableSkills", 0)
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
        help="require one sidecar for every publishable top-level Agent and Skill",
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
