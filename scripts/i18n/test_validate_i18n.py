#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Unit tests for market validation policies."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


VALIDATOR_PATH = Path(__file__).with_name("validate-i18n.py")
SPEC = importlib.util.spec_from_file_location("market_validate_i18n", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


class ModelInvocationPolicyTests(unittest.TestCase):
    def validate(self, frontmatter: dict[str, object]) -> list[object]:
        report = VALIDATOR.Report()
        VALIDATOR.validate_model_invocation_policy(
            frontmatter,
            "skills/example/SKILL.md",
            report,
        )
        return report.issues

    def test_allows_true(self) -> None:
        self.assertEqual([], self.validate({"disable-model-invocation": True}))

    def test_allows_omitted_field(self) -> None:
        self.assertEqual([], self.validate({}))

    def test_rejects_false(self) -> None:
        issues = self.validate({"disable-model-invocation": False})
        self.assertEqual(1, len(issues))
        self.assertEqual("model-invocation-policy", issues[0].rule)

    def test_rejects_non_boolean_value(self) -> None:
        issues = self.validate({"disable-model-invocation": "true"})
        self.assertEqual(1, len(issues))
        self.assertEqual("model-invocation-policy", issues[0].rule)


class BuiltinSkillManifestTests(unittest.TestCase):
    def validate(self, payload: dict[str, object], skills: list[str]) -> list[object]:
        report = VALIDATOR.Report()
        VALIDATOR.validate_builtin_manifest(report, payload, skills)
        return report.issues

    def test_allows_disjoint_sorted_retired_ids(self) -> None:
        self.assertEqual([], self.validate(
            {"skills": ["new-skill"], "retired": ["old-skill"]},
            ["new-skill"],
        ))

    def test_rejects_active_retired_overlap(self) -> None:
        issues = self.validate(
            {"skills": ["same-skill"], "retired": ["same-skill"]},
            ["same-skill"],
        )
        self.assertTrue(any("overlap" in issue.message for issue in issues))

    def test_rejects_unknown_fields_and_invalid_ids(self) -> None:
        issues = self.validate(
            {"skills": ["Invalid_ID"], "retired": [], "unknown": True},
            ["Invalid_ID"],
        )
        self.assertTrue(any("unknown top-level" in issue.message for issue in issues))
        self.assertTrue(any("invalid Skill IDs" in issue.message for issue in issues))

    def test_reports_unsorted_active_skills_once(self) -> None:
        issues = self.validate(
            {"skills": ["second-skill", "first-skill"], "retired": []},
            ["first-skill", "second-skill"],
        )
        sort_issues = [issue for issue in issues if "not sorted" in issue.message]
        self.assertEqual(1, len(sort_issues))


class PublishableAgentCatalogTests(unittest.TestCase):
    def test_counts_inline_and_pointer_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agents" / "inline-agent").mkdir(parents=True)
            (root / "agents" / "inline-agent" / "agent.json").write_text("{}")
            (root / "agents" / "pointer-agent").mkdir(parents=True)
            (root / "agents" / "pointer-agent" / "entry.json").write_text("{}")

            with patch.object(VALIDATOR, "REPO_ROOT", root):
                inline, pointers = VALIDATOR.count_publishable_agents()

            self.assertEqual(["inline-agent"], inline)
            self.assertEqual(["pointer-agent"], pointers)


if __name__ == "__main__":
    unittest.main()
