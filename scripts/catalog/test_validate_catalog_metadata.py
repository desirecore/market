#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.23,<5", "pyyaml>=6.0"]
# ///
"""Unit tests for the Market catalog metadata sidecar validator."""

from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


VALIDATOR_PATH = Path(__file__).with_name("validate_catalog_metadata.py")
SPEC = importlib.util.spec_from_file_location("market_catalog_metadata_validator", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)
SOURCE_SCHEMA = VALIDATOR_PATH.parents[2] / "schemas" / "catalog-metadata.v1.schema.json"


def unknown() -> dict[str, str]:
    return {"state": "unknown"}


def valid_entry() -> dict[str, object]:
    return {
        "id": "example-skill",
        "name": "Example Skill",
        "category": "development",
        "tags": ["example"],
        "i18n": {
            "zh-CN": {"name": "示例技能", "shortDesc": "中文简介"},
            "en-US": {"name": "Example Skill", "shortDesc": "English summary"},
        },
        "maintainer": {"name": "Example Maintainer", "verified": False},
        "stewardship": "community",
        "license": "MIT",
        "redistribution": "allowed",
        "source": {
            "kind": "git",
            "repoUrl": "https://example.com/example-skill.git",
            "repoBranch": "main",
            "ref": "a" * 40,
        },
    }


def valid_sidecar() -> dict[str, object]:
    return {
        "$schema": "../../schemas/catalog-metadata.v1.schema.json",
        "schemaVersion": 1,
        "identity": {"kind": "skill", "id": "example-skill"},
        "presentation": {
            "defaultLocale": "en-US",
            "i18n": {
                "zh-CN": {"name": "示例技能", "summary": "中文简介"},
                "en-US": {"name": "Example Skill", "summary": "English summary"},
            },
            "category": "development",
            "tags": ["example"],
        },
        "release": unknown(),
        "timestamps": {
            "catalogUpdatedAt": unknown(),
            "releasePublishedAt": unknown(),
            "reviewedAt": unknown(),
            "upstreamObservedAt": unknown(),
        },
        "provenance": {
            "content": {
                "kind": "git",
                "url": "https://example.com/example-skill.git",
                "ref": "a" * 40,
            }
        },
        "governance": {
            "stewardship": "community",
            "availability": "listing-only",
            "license": {"state": "known", "value": "MIT"},
            "redistribution": "allowed",
            "upstreamMaintainer": {"name": "Example Maintainer", "verified": False},
        },
        "compatibility": {"platforms": unknown()},
        "spec": {"kind": "skill", "riskLevel": "low"},
    }


class CatalogMetadataValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "schemas").mkdir()
        shutil.copyfile(SOURCE_SCHEMA, self.root / "schemas" / SOURCE_SCHEMA.name)
        (self.root / "agents").mkdir()
        (self.root / "skills" / "example-skill").mkdir(parents=True)
        self.write_json(
            self.root / "manifest.json",
            {
                "supportedLocales": ["zh-CN", "en-US"],
                "stats": {"totalAgents": 0, "totalSkills": 1},
            },
        )
        self.entry_path = self.root / "skills" / "example-skill" / "entry.json"
        self.sidecar_path = self.root / "skills" / "example-skill" / VALIDATOR.SIDECAR_NAME
        self.write_json(self.entry_path, valid_entry())
        self.write_json(self.sidecar_path, valid_sidecar())

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def write_json(path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def validate(self, *, require_complete: bool = False):
        return VALIDATOR.validate_repository(self.root, require_complete=require_complete)

    def rewrite_sidecar(self, mutate) -> None:
        payload = valid_sidecar()
        mutate(payload)
        self.write_json(self.sidecar_path, payload)

    def write_agent_case(self, install_policy: str | None, update_policy: str | None, availability: str) -> None:
        agent_dir = self.root / "agents" / "system-agent"
        agent_dir.mkdir()
        self.write_json(
            agent_dir / "agent.json",
            {
                "id": "system-agent",
                "category": "development",
                "i18n": {
                    "default_locale": "en-US",
                    "source_locale": "zh-CN",
                    "locales": ["zh-CN", "en-US"],
                    "zh-CN": {"name": "系统智能体", "shortDesc": "系统智能体简介"},
                    "en-US": {"name": "System Agent", "shortDesc": "System agent summary"},
                },
            },
        )
        sidecar = valid_sidecar()
        sidecar["identity"] = {"kind": "agent", "id": "system-agent"}
        sidecar["presentation"] = {
            "defaultLocale": "en-US",
            "i18n": {
                "zh-CN": {"name": "系统智能体", "summary": "系统智能体简介"},
                "en-US": {"name": "System Agent", "summary": "System agent summary"},
            },
            "category": "development",
            "tags": [],
        }
        sidecar["provenance"] = {}
        sidecar["governance"] = {
            "availability": availability,
            "license": unknown(),
            "redistribution": "verify-package-terms",
        }
        spec = {"kind": "agent"}
        if install_policy is not None:
            spec["installPolicy"] = install_policy
        if update_policy is not None:
            spec["updatePolicy"] = update_policy
        sidecar["spec"] = spec
        self.write_json(agent_dir / VALIDATOR.SIDECAR_NAME, sidecar)
        manifest = json.loads((self.root / "manifest.json").read_text(encoding="utf-8"))
        manifest["stats"]["totalAgents"] = 1
        self.write_json(self.root / "manifest.json", manifest)

    def write_agent_pointer_case(self, mutate_entry=None, mutate_sidecar=None) -> tuple[Path, Path]:
        agent_dir = self.root / "agents" / "example-agent"
        entry = valid_entry()
        entry.update(
            id="example-agent", name="Example Agent", latestVersion="1.2.3",
            requiredClientVersion="10.0.0", installPolicy="market", updatePolicy="market",
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M0 0h24v24H0z"/></svg>',
        )
        entry["i18n"] = {
            "zh-CN": {"name": "示例智能体", "shortDesc": "通用示例智能体"},
            "en-US": {"name": "Example Agent", "shortDesc": "General-purpose example agent"},
        }
        entry["source"]["repoUrl"] = "https://example.com/example-agent.git"
        sidecar = valid_sidecar()
        sidecar["identity"] = {"kind": "agent", "id": "example-agent"}
        sidecar["presentation"]["i18n"] = {
            locale: {"name": value["name"], "summary": value["shortDesc"]}
            for locale, value in entry["i18n"].items()
        }
        sidecar["release"] = {"state": "known", "version": "1.2.3", "versionScheme": "semver"}
        sidecar["provenance"]["content"]["url"] = entry["source"]["repoUrl"]
        sidecar["timestamps"]["reviewedAt"] = {"state": "known", "value": "2026-08-30", "precision": "day"}
        sidecar["governance"].update(
            availability="installable",
            compliance={"licenseEvidencePath": "LICENSE", "reviewedRef": "a" * 40,
                        "reviewedAt": "2026-08-30", "reviewedBy": "Example Reviewer", "upstreamEndorsed": False},
        )
        sidecar["governance"]["license"]["evidencePath"] = "LICENSE"
        sidecar["compatibility"]["requiredClientVersion"] = "10.0.0"
        sidecar["spec"] = {"kind": "agent", "installPolicy": "market", "updatePolicy": "market"}
        if mutate_entry:
            mutate_entry(entry)
        if mutate_sidecar:
            mutate_sidecar(sidecar)
        entry_path = agent_dir / "entry.json"
        sidecar_path = agent_dir / VALIDATOR.SIDECAR_NAME
        self.write_json(entry_path, entry)
        self.write_json(sidecar_path, sidecar)
        self.write_json(self.root / "manifest.json", {
            "supportedLocales": ["zh-CN", "en-US"], "stats": {"totalAgents": 1, "totalSkills": 1},
        })
        return entry_path, sidecar_path

    def test_accepts_complete_installable_agent_pointer_without_inline_agent(self) -> None:
        entry_path, _ = self.write_agent_pointer_case()
        report = self.validate(require_complete=True)
        self.assertFalse(report.has_errors, report.issues)
        self.assertFalse(entry_path.with_name("agent.json").exists())
        self.assertEqual(1, report.stats["agents"])
        self.assertEqual(2, report.stats["sidecars"])

    def test_listing_only_agent_pointer_allows_empty_root_path_and_unpinned_ref(self) -> None:
        def metadata_change(payload):
            payload["provenance"]["content"].pop("ref")
            payload["governance"]["availability"] = "listing-only"

        self.write_agent_pointer_case(
            lambda payload: payload["source"].update(path="", ref=""), metadata_change,
        )
        report = self.validate(require_complete=True)
        self.assertFalse(report.has_errors, report.issues)

    def test_accepts_agent_web_and_zip_pointers_with_matching_byte_digest(self) -> None:
        for kind in ("web", "zip"):
            with self.subTest(kind=kind):
                def entry_change(payload):
                    payload["source"] = {"kind": kind, "repoUrl": "https://example.com/agent.zip", "sha256": "b" * 64}

                def metadata_change(payload):
                    payload["provenance"]["content"] = {"kind": kind, "url": "https://example.com/agent.zip", "sha256": "b" * 64}
                    payload["governance"]["compliance"]["reviewedRef"] = "b" * 64

                self.write_agent_pointer_case(entry_change, metadata_change)
                report = self.validate(require_complete=True)
                self.assertFalse(report.has_errors, report.issues)

    def test_rejects_agent_pointer_sidecar_conflicts(self) -> None:
        mutations = {
            "identity": lambda p: p["identity"].update(id="other-agent"),
            "kind": lambda p: (p["identity"].update(kind="skill"), p.update(spec={"kind": "skill"})),
            "version": lambda p: p["release"].update(version="9.9.9"),
            "source-kind": lambda p: p["provenance"]["content"].update(kind="web"),
            "source-url": lambda p: p["provenance"]["content"].update(url="https://example.com/other.git"),
            "source-ref": lambda p: p["provenance"]["content"].update(ref="b" * 40),
            "source-path": lambda p: p["provenance"]["content"].update(path="another-agent"),
            "source-digest": lambda p: p["provenance"]["content"].update(sha256="b" * 64),
            "category": lambda p: p["presentation"].update(category="research"),
            "tags": lambda p: p["presentation"].update(tags=["other"]),
            "summary": lambda p: p["presentation"]["i18n"]["en-US"].update(summary="Different"),
            "license": lambda p: p["governance"]["license"].update(value="Apache-2.0"),
            "redistribution": lambda p: p["governance"].update(redistribution="source-pointer-only"),
            "stewardship": lambda p: p["governance"].update(stewardship="official"),
            "maintainer": lambda p: p["governance"]["upstreamMaintainer"].update(name="Other Maintainer"),
            "compatibility": lambda p: p["compatibility"].update(requiredClientVersion="9.0.0"),
            "policy": lambda p: (p.update(spec={"kind": "agent", "installPolicy": "system", "updatePolicy": "repository"}),
                                  p.update(release=unknown()), p["governance"].update(availability="listing-only")),
        }
        for name, mutation in mutations.items():
            with self.subTest(name=name):
                self.write_agent_pointer_case(mutate_sidecar=mutation)
                self.assertTrue(any(issue.rule == "legacy-consistency" for issue in self.validate().issues))

    def test_rejects_agent_pointer_entry_id_that_is_not_the_catalog_slug(self) -> None:
        self.write_agent_pointer_case(mutate_entry=lambda p: p.update(id="00000000-0000-4000-8000-000000000000"))
        self.assertTrue(any("entry.id" in issue.message for issue in self.validate().issues))

    def test_agent_pointer_must_keep_both_immutable_source_and_governance_evidence(self) -> None:
        cases = [
            (lambda p: p["source"].pop("ref"), None),
            (lambda p: p["source"].update(ref="main"),
             lambda p: (p["provenance"]["content"].update(ref="main"), p["governance"]["compliance"].update(reviewedRef="main"))),
            (None, lambda p: p["governance"].update(license=unknown())),
            (None, lambda p: p["governance"].pop("compliance")),
            (None, lambda p: p["timestamps"].update(reviewedAt=unknown())),
            (None, lambda p: p["governance"]["compliance"].update(reviewedRef="b" * 40)),
        ]
        for index, (entry_change, metadata_change) in enumerate(cases):
            with self.subTest(index=index):
                self.write_agent_pointer_case(entry_change, metadata_change)
                self.assertTrue(any(issue.rule == "installable-evidence" for issue in self.validate().issues))

    def test_agent_pointer_sidecar_does_not_allow_provider_or_runtime_fields(self) -> None:
        self.write_agent_pointer_case(mutate_sidecar=lambda p: p["identity"].update(catalogSourceId="market:official"))
        self.assertTrue(any(issue.rule == "catalog-schema" for issue in self.validate().issues))

    def test_agent_sidecar_rejects_missing_or_ambiguous_legacy_file(self) -> None:
        entry, sidecar = self.write_agent_pointer_case()
        entry.unlink()
        report = self.validate()
        self.assertTrue(any(issue.rule == "fixed-sidecar-path" and "agent.json or entry.json" in issue.message for issue in report.issues))
        self.write_agent_pointer_case()
        self.write_json(entry.with_name("agent.json"), {"id": "example-agent"})
        report = self.validate()
        self.assertTrue(any(issue.rule == "fixed-sidecar-path" and "exactly one" in issue.message for issue in report.issues))

    def test_agent_pointer_requires_sidecar_under_complete_coverage(self) -> None:
        _, sidecar = self.write_agent_pointer_case()
        sidecar.unlink()
        self.assertTrue(any(issue.rule == "sidecar-coverage" for issue in self.validate(require_complete=True).issues))

    def test_accepts_valid_listing_only_pointer(self) -> None:
        report = self.validate(require_complete=True)
        self.assertFalse(report.has_errors, report.issues)
        self.assertEqual(1, report.stats["sidecars"])
        self.assertEqual(1, report.stats["publishableSkills"])

    def test_accepts_system_repository_listing_only_agent_policy(self) -> None:
        self.write_agent_case("system", "repository", "listing-only")
        report = self.validate()
        self.assertFalse(report.has_errors, report.issues)

    def test_rejects_system_agent_content_release(self) -> None:
        self.write_agent_case("system", "repository", "listing-only")
        sidecar_path = self.root / "agents" / "system-agent" / VALIDATOR.SIDECAR_NAME
        payload = json.loads(sidecar_path.read_text(encoding="utf-8"))
        payload["release"] = {"state": "known", "version": "1.2.0", "versionScheme": "semver"}
        self.write_json(sidecar_path, payload)
        issues = self.validate().issues
        self.assertTrue(any(issue.rule in {"catalog-schema", "agent-policy"} for issue in issues))

    def test_rejects_system_agent_content_release_timestamp(self) -> None:
        self.write_agent_case("system", "repository", "listing-only")
        sidecar_path = self.root / "agents" / "system-agent" / VALIDATOR.SIDECAR_NAME
        payload = json.loads(sidecar_path.read_text(encoding="utf-8"))
        payload["timestamps"]["releasePublishedAt"] = {
            "state": "known",
            "value": "2026-08-13",
            "precision": "day",
        }
        self.write_json(sidecar_path, payload)
        issues = self.validate().issues
        self.assertTrue(any(issue.rule == "agent-policy" for issue in issues))

    def test_accepts_market_market_listing_only_agent_policy(self) -> None:
        self.write_agent_case("market", "market", "listing-only")
        report = self.validate()
        self.assertFalse(report.has_errors, report.issues)

    def test_rejects_invalid_agent_policy_combinations(self) -> None:
        cases = [
            ("system", "market", "listing-only"),
            ("system", "repository", "installable"),
            ("market", "repository", "listing-only"),
            ("system", None, "listing-only"),
            (None, "repository", "listing-only"),
        ]
        for index, (install_policy, update_policy, availability) in enumerate(cases):
            with self.subTest(
                installPolicy=install_policy,
                updatePolicy=update_policy,
                availability=availability,
            ):
                if index:
                    shutil.rmtree(self.root / "agents" / "system-agent")
                self.write_agent_case(install_policy, update_policy, availability)
                self.assertTrue(any(issue.rule == "catalog-schema" for issue in self.validate().issues))

    def test_market_agent_installable_still_requires_governance_evidence(self) -> None:
        self.write_agent_case("market", "market", "installable")
        issues = self.validate().issues
        evidence = [issue for issue in issues if issue.rule == "installable-evidence"]
        self.assertGreaterEqual(len(evidence), 4)

    def test_rejects_provider_identity_catalog_trust_and_runtime_fields(self) -> None:
        def mutate(payload):
            payload["identity"]["catalogSourceId"] = "market:official"
            payload["provenance"]["catalog"] = {"trust": "official"}
            payload["installStatus"] = "installed"

        self.rewrite_sidecar(mutate)
        issues = self.validate().issues
        schema_messages = [issue.message for issue in issues if issue.rule == "catalog-schema"]
        self.assertTrue(any("Additional properties" in message for message in schema_messages))

    def test_rejects_wrong_time_precision_and_non_utc_second(self) -> None:
        def mutate(payload):
            payload["timestamps"]["catalogUpdatedAt"] = {
                "state": "known",
                "value": "2026-08-30T12:00:00+08:00",
                "precision": "day",
            }

        self.rewrite_sidecar(mutate)
        self.assertTrue(any(issue.rule == "catalog-schema" for issue in self.validate().issues))

    def test_rejects_legacy_duplicate_mismatch(self) -> None:
        self.rewrite_sidecar(lambda payload: payload["presentation"].update(category="research"))
        issues = self.validate().issues
        self.assertTrue(any(issue.rule == "legacy-consistency" for issue in issues))

    def test_keeps_unverified_legacy_license_unknown_with_warning(self) -> None:
        def mutate(payload):
            payload["governance"]["license"] = unknown()

        self.rewrite_sidecar(mutate)
        report = self.validate()
        self.assertFalse(report.has_errors, report.issues)
        self.assertTrue(any(issue.rule == "legacy-license-unverified" for issue in report.issues))

    def test_rejects_installable_without_review_or_immutable_source(self) -> None:
        def mutate(payload):
            payload["governance"] = {
                "availability": "installable",
                "license": unknown(),
                "redistribution": "verify-package-terms",
            }
            payload["provenance"]["content"]["ref"] = "main"

        self.rewrite_sidecar(mutate)
        issues = self.validate().issues
        evidence = [issue.message for issue in issues if issue.rule == "installable-evidence"]
        self.assertTrue(any("immutable" in message for message in evidence))
        self.assertTrue(any("known license" in message for message in evidence))
        self.assertTrue(any("known reviewedAt" in message for message in evidence))
        self.assertTrue(any("compliance" in message for message in evidence))

    def test_allows_builtin_installation_with_stable_incomplete_governance_warnings(self) -> None:
        self.entry_path.unlink()
        skill_path = self.entry_path.with_name("SKILL.md")
        skill_path.write_text(
            """---
name: example-skill
description: Example builtin skill.
type: procedural
risk_level: low
tags: [example]
metadata:
  author: example
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales: [zh-CN, en-US]
    zh-CN:
      name: 示例技能
      short_desc: 中文简介
    en-US:
      name: Example Skill
      short_desc: English summary
market:
  category: development
---
Body.
""",
            encoding="utf-8",
        )

        def mutate(payload):
            payload["provenance"] = {}
            payload["governance"] = {
                "stewardship": "community",
                "availability": "installable",
                "license": unknown(),
                "redistribution": "verify-package-terms",
                "listingMaintainer": {"name": "Candidate", "verified": False},
            }
            payload["spec"] = {"kind": "skill", "riskLevel": "low", "skillType": "procedural"}

        self.rewrite_sidecar(mutate)
        report = self.validate()
        self.assertFalse(report.has_errors, report.issues)
        warning_rules = {issue.rule for issue in report.issues if issue.severity == "warning"}
        self.assertTrue(
            {
                "missing-license-evidence",
                "missing-review-evidence",
                "missing-maintainer-evidence",
                "missing-content-evidence",
            }.issubset(warning_rules)
        )

    def test_validates_collection_identity_and_does_not_invent_child_version(self) -> None:
        entry = valid_entry()
        entry["children"] = [
            {
                "id": "child-one",
                "path": "skills/child-one",
                "i18n": {
                    "zh-CN": {"shortDesc": "Same child summary"},
                    "en-US": {"shortDesc": "Same child summary"},
                },
            }
        ]
        self.write_json(self.entry_path, entry)

        def mutate(payload):
            child_presentation = copy.deepcopy(payload["presentation"])
            child_presentation["tags"] = []
            child_presentation["i18n"] = {
                "zh-CN": {"name": "child-one", "summary": "Same child summary"},
                "en-US": {"name": "child-one", "summary": "Same child summary"},
            }
            payload["spec"]["collection"] = {
                "role": "parent",
                "childCount": 1,
                "children": [
                    {
                        "identity": {
                            "kind": "skill",
                            "id": "child-one",
                            "parentId": "example-skill",
                        },
                        "path": "skills/child-one",
                        "presentation": child_presentation,
                        "release": unknown(),
                    }
                ]
            }

        self.rewrite_sidecar(mutate)
        report = self.validate()
        self.assertFalse(report.has_errors)
        self.assertTrue(any(issue.rule == "i18n-freshness" for issue in report.issues))

        def invent_version(payload):
            mutate(payload)
            payload["spec"]["collection"]["children"][0]["release"] = {
                "state": "known",
                "version": "1.0.0",
                "versionScheme": "semver",
            }

        self.rewrite_sidecar(invent_version)
        self.assertTrue(any(issue.rule == "collection-version" for issue in self.validate().issues))

    def test_marks_identical_locale_payloads_for_review_without_failing(self) -> None:
        def mutate(payload):
            payload["presentation"]["i18n"] = {
                "zh-CN": {"name": "Same", "summary": "Same summary"},
                "en-US": {"name": "Same", "summary": "Same summary"},
            }
            entry = valid_entry()
            entry["i18n"] = {
                "zh-CN": {"name": "Same", "shortDesc": "Same summary"},
                "en-US": {"name": "Same", "shortDesc": "Same summary"},
            }
            self.write_json(self.entry_path, entry)

        self.rewrite_sidecar(mutate)
        report = self.validate()
        self.assertFalse(report.has_errors, report.issues)
        self.assertTrue(any(issue.rule == "i18n-freshness" for issue in report.issues))

    def test_rejects_sidecar_outside_fixed_path(self) -> None:
        rogue = self.root / "metadata" / VALIDATOR.SIDECAR_NAME
        self.write_json(rogue, valid_sidecar())
        issues = self.validate().issues
        self.assertTrue(any(issue.path.startswith("metadata/") and issue.rule == "fixed-sidecar-path" for issue in issues))

    def test_reports_manifest_stats_and_optional_complete_coverage(self) -> None:
        manifest = {
            "supportedLocales": ["zh-CN", "en-US"],
            "stats": {"totalAgents": 1, "totalSkills": 99},
        }
        self.write_json(self.root / "manifest.json", manifest)
        issues = self.validate().issues
        self.assertEqual(2, sum(issue.rule == "market-stats" for issue in issues))

        self.sidecar_path.unlink()
        issues = self.validate(require_complete=True).issues
        self.assertTrue(any(issue.rule == "sidecar-coverage" for issue in issues))


if __name__ == "__main__":
    unittest.main()
