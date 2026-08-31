#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.23,<5", "pyyaml>=6.0"]
# ///
"""Unit tests for market validation policies."""

from __future__ import annotations

import importlib.util
import json
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


class EntryIconPolicyTests(unittest.TestCase):
    """`icon` is only required where the client actually renders one.

    `marketSkillSchema` exposes `icon`; `marketAgentSchema` and `marketTeamSchema`
    expose `avatar` and have no `icon` property at all, so an icon on those listings
    can never reach a card.
    """

    ICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M0 0h24v24H0z"/></svg>'

    def check(self, kind: str, *, icon: object = ..., source=None, source_kinds=None) -> list[object]:
        entry = {
            "id": "example",
            "name": "Example",
            "category": "development",
            "maintainer": {"name": "Example Maintainer", "verified": False},
            "stewardship": "community",
            "license": "MIT",
            "redistribution": "allowed",
            "source": source or {"kind": "git", "repoUrl": "https://example.com/example.git"},
        }
        if icon is not ...:
            entry["icon"] = icon
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry_dir = root / f"{kind}s" / "example"
            entry_dir.mkdir(parents=True)
            entry_file = entry_dir / "entry.json"
            entry_file.write_text(json.dumps(entry), encoding="utf-8")
            report = VALIDATOR.Report()
            with patch.object(VALIDATOR, "REPO_ROOT", root):
                VALIDATOR.validate_entry_json(
                    report, entry_file, {"development"}, False, kind,
                    source_kinds or frozenset({"git", "web", "zip"}),
                )
            return report.issues

    def test_skill_entry_still_requires_an_icon(self) -> None:
        messages = [issue.message for issue in self.check("skill")]
        self.assertTrue(any("missing required field 'icon'" in message for message in messages))

    def test_team_and_agent_entries_may_omit_the_icon(self) -> None:
        for kind in ("team", "agent"):
            with self.subTest(kind=kind):
                self.assertEqual([], self.check(kind))

    def test_icon_on_a_team_listing_is_flagged_but_not_fatal(self) -> None:
        issues = self.check("team", icon=self.ICON)
        self.assertEqual(1, len(issues))
        self.assertEqual("warning", issues[0].severity)
        self.assertIn("dead weight", issues[0].message)

    def test_a_declared_icon_is_still_validated_on_every_kind(self) -> None:
        for kind in ("skill", "team"):
            with self.subTest(kind=kind):
                errors = [i.message for i in self.check(kind, icon="not svg") if i.severity == "error"]
                self.assertTrue(any("valid SVG XML" in message for message in errors))

    def test_team_entry_rejects_non_git_sources(self) -> None:
        # Installing a team forks its repository and updating it is a git pull;
        # neither action can be expressed by a zip or a fetched web page.
        for source_kind in ("zip", "web"):
            with self.subTest(source_kind=source_kind):
                messages = [
                    issue.message
                    for issue in self.check(
                        "team",
                        source={"kind": source_kind, "repoUrl": "https://example.com/example.zip"},
                        source_kinds=frozenset({"git"}),
                    )
                    if issue.severity == "error"
                ]
                self.assertTrue(any("must be one of git" in message for message in messages), messages)

    def test_skill_entry_still_accepts_zip_and_web_sources(self) -> None:
        for source_kind in ("zip", "web"):
            with self.subTest(source_kind=source_kind):
                issues = self.check(
                    "skill",
                    icon=self.ICON,
                    source={"kind": source_kind, "repoUrl": "https://example.com/example.zip"},
                )
                self.assertEqual([], issues)


class PublishableTeamCatalogTests(unittest.TestCase):
    def test_counts_team_pointers_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "teams" / "pointer-team").mkdir(parents=True)
            (root / "teams" / "pointer-team" / "entry.json").write_text("{}")
            # A team is a fork pointer: a stray inline body is not a publishable unit.
            (root / "teams" / "inline-team").mkdir(parents=True)
            (root / "teams" / "inline-team" / "team.json").write_text("{}")

            with patch.object(VALIDATOR, "REPO_ROOT", root):
                teams = VALIDATOR.count_publishable_teams()

            self.assertEqual(["pointer-team"], teams)

    def test_returns_empty_without_a_teams_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(VALIDATOR, "REPO_ROOT", Path(tmp)):
                self.assertEqual([], VALIDATOR.count_publishable_teams())
class WorkforceClarificationDiscoveryTests(unittest.TestCase):
    """Guard the catalog-only entry text; actual model selection still needs runtime acceptance."""

    def test_clarify_only_requests_are_explicit_in_both_discovery_locales(self) -> None:
        import json
        import yaml

        directory = Path(__file__).resolve().parents[2] / "skills" / "workforce-optimization"
        raw = (directory / "SKILL.md").read_text(encoding="utf-8")
        metadata = yaml.safe_load(raw.split("---", 2)[1])
        locales = metadata["metadata"]["i18n"]
        catalog = json.loads((directory / "catalog-metadata.v1.json").read_text(encoding="utf-8"))
        # Keep the repository's on-demand-body policy; don't enable eager injection of all Skills.
        self.assertIs(metadata["disable-model-invocation"], True)
        self.assertIn("只澄清", metadata["description"][:180])
        self.assertIn("Skill", metadata["description"][:180])
        for locale, trigger in (("zh-CN", "暂不求解"), ("en-US", "clarify only")):
            description = locales[locale]["description"]
            self.assertIn(trigger, description)
            self.assertIn("DecisionWorkspace", description)
            self.assertIn("AskUserQuestion", description)
            self.assertEqual(description, catalog["presentation"]["i18n"][locale]["description"])
        self.assertIn("clarification works without a connected solver", metadata["compatibility"])
        self.assertIn("separately", metadata["compatibility"])
        self.assertIn("Generic AskUserQuestion may handle non-modeling setup", raw)
        chinese = (directory / "SKILL.zh-CN.md").read_text(encoding="utf-8")
        self.assertIn("普通 AskUserQuestion 只用于非建模设置选择", chinese)

    def test_ambiguous_answers_and_current_language_keep_their_boundaries(self) -> None:
        directory = Path(__file__).resolve().parents[2] / "skills" / "workforce-optimization"
        english = (directory / "SKILL.md").read_text(encoding="utf-8")
        chinese = (directory / "SKILL.zh-CN.md").read_text(encoding="utf-8")
        self.assertIn("only if raw_text uniquely determines", english)
        self.assertIn("keep the original answer and needs_input", english)
        self.assertIn("Do not add epistemic placeholders", english)
        self.assertIn("for Chinese use [中文澄清框架]", english)
        # 以下断言分别覆盖中文规范化、未知与语言入口。
        self.assertIn("仅在 raw_text 能唯一确定业务值及必要单位/统计窗口时", chinese)
        self.assertIn("仍有歧义时保留原答案和 needs_input", chinese)
        self.assertIn("不得把“目前不确定”“不知道”等知识缺口", chinese)
        self.assertIn("技能 metadata 默认语言不覆盖用户语言", chinese)
        for locale in ("", ".zh-CN"):
            framework = (directory / "references" / f"requirement-clarification-framework{locale}.md").read_text(encoding="utf-8")
            self.assertIn("needs_input", framework)
            self.assertIn("node.value", framework)


if __name__ == "__main__":
    unittest.main()
