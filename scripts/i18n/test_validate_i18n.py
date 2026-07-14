#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Unit tests for market validation policies."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
