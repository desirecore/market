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

    def test_accepts_valid_listing_only_pointer(self) -> None:
        report = self.validate(require_complete=True)
        self.assertFalse(report.has_errors, report.issues)
        self.assertEqual(1, report.stats["sidecars"])
        self.assertEqual(1, report.stats["publishableSkills"])

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
