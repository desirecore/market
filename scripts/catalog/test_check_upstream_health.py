#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Unit tests for the upstream health check, using local Git repositories."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


CHECKER_PATH = Path(__file__).with_name("check_upstream_health.py")
SPEC = importlib.util.spec_from_file_location("market_upstream_health", CHECKER_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


def sh(*args: str, cwd: Path) -> str:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class UpstreamHealthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.upstream = self.root / "upstream"
        self.upstream.mkdir()
        sh("git", "init", "--quiet", "-b", "main", cwd=self.upstream)
        for key, value in (("user.name", "t"), ("user.email", "t@example.com"),
                           ("uploadpack.allowFilter", "true"),
                           ("uploadpack.allowAnySHA1InWant", "true")):
            sh("git", "config", key, value, cwd=self.upstream)
        self.first = self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: A.\n---\n"})
        self.url = self.upstream.as_uri()
        self.catalog = self.root / "catalog"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def commit(self, files: dict[str, str]) -> str:
        for rel, text in files.items():
            path = self.upstream / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        sh("git", "add", "-A", cwd=self.upstream)
        sh("git", "commit", "--quiet", "-m", "c", cwd=self.upstream)
        return sh("git", "rev-parse", "HEAD", cwd=self.upstream)

    def entry(self, **source) -> Path:
        base = {"kind": "git", "repoUrl": self.url, "repoBranch": "main"}
        data = {"id": "demo", "source": {**base, **source}}
        children = data["source"].pop("children", None)
        if children is not None:
            data["children"] = children
        path = self.catalog / "skills" / "demo" / "entry.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def statuses(self, path: Path) -> dict[str, str]:
        return {i["status"]: i["detail"] for i in CHECKER.check_entry(path)["issues"]}

    def test_pinned_head_with_valid_path_is_ok(self) -> None:
        result = self.statuses(self.entry(ref=self.first, path="skills/alpha"))
        self.assertEqual(result, {"ok": ""})

    def test_missing_repository_is_gone(self) -> None:
        result = self.statuses(self.entry(repoUrl=(self.root / "missing").as_uri()))
        self.assertIn("gone", result)

    def test_missing_branch_is_bad_branch(self) -> None:
        result = self.statuses(self.entry(repoBranch="release", ref=self.first))
        self.assertIn("bad-branch", result)

    def test_moved_skill_is_bad_path(self) -> None:
        result = self.statuses(self.entry(ref=self.first, path="alpha"))
        self.assertIn("bad-path", result)

    def test_newer_head_is_outdated(self) -> None:
        self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated.\n---\n"})
        result = self.statuses(self.entry(ref=self.first, path="skills/alpha"))
        self.assertIn("outdated", result)
        self.assertNotIn("bad-ref", result)

    def test_unrelated_feed_refresh_does_not_offer_a_skill_update(self) -> None:
        self.commit({"data/latest.json": '{"updated": true}', "README.md": "Updated website.\n"})
        self.assertEqual(self.statuses(self.entry(ref=self.first, path="skills/alpha")), {"ok": ""})

    def test_root_license_change_still_needs_review_for_a_subtree(self) -> None:
        self.commit({"LICENSE": "New licensing terms.\n"})
        self.assertIn("outdated", self.statuses(self.entry(ref=self.first, path="skills/alpha")))

    def test_unfetchable_ref_is_bad_ref(self) -> None:
        result = self.statuses(self.entry(ref="0" * 40, path="skills/alpha"))
        self.assertIn("bad-ref", result)

    def test_unpinned_entry_is_reported(self) -> None:
        result = self.statuses(self.entry(path="skills/alpha"))
        self.assertIn("unpinned", result)

    def test_branch_suffix_is_not_the_requested_branch(self) -> None:
        sh("git", "branch", "-m", "changeset-release/main", cwd=self.upstream)
        self.assertIn("bad-branch", self.statuses(self.entry(ref=self.first, path="skills/alpha")))

    def test_exact_branch_ignores_another_main_suffix(self) -> None:
        sh("git", "branch", "changeset-release/main", cwd=self.upstream)
        head = self.commit({"README.md": "New content.\n"})
        self.assertEqual(self.statuses(self.entry(ref=head, path="skills/alpha")), {"ok": ""})

    def test_identical_tree_does_not_offer_an_update(self) -> None:
        sh("git", "commit", "--quiet", "--allow-empty", "-m", "merge metadata", cwd=self.upstream)
        self.assertEqual(self.statuses(self.entry(ref=self.first, path="skills/alpha")), {"ok": ""})

    def test_moved_upstream_path_does_not_break_valid_pin(self) -> None:
        (self.upstream / "skills/alpha/SKILL.md").unlink()
        self.commit({"skills/beta/SKILL.md": "---\nname: beta\ndescription: B.\n---\n"})
        result = self.statuses(self.entry(ref=self.first, path="skills/alpha"))
        self.assertIn("upstream-path-change", result)
        self.assertNotIn("bad-path", result)
        self.assertIn("bad-path", self.statuses(self.entry(path="skills/alpha")))

    def test_lowercase_reference_is_not_a_skill(self) -> None:
        head = self.commit({"skills/beta/skill.md": "Reference documentation.\n"})
        self.assertIn("bad-path", self.statuses(self.entry(ref=head, path="skills/beta")))

    def test_fetch_network_error_is_unknown(self) -> None:
        self.commit({"README.md": "New content.\n"})
        real_git = CHECKER.git

        def failing_fetch(*args, **kwargs):
            if args[0] == "fetch":
                return subprocess.CompletedProcess(args, 128, "", "Connection reset by peer")
            return real_git(*args, **kwargs)

        with patch.object(CHECKER, "git", side_effect=failing_fetch):
            result = self.statuses(self.entry(ref=self.first, path="skills/alpha"))
        self.assertIn("unreachable", result)
        self.assertNotIn("bad-ref", result)

    def test_internal_child_is_not_offered(self) -> None:
        head = self.commit({"skills/mono/SKILL.md": "---\nname: dws\nmetadata:\n  internal: true\n---\n"})
        result = self.statuses(self.entry(ref=head, children=[{"id": "alpha", "path": "skills/alpha"}]))
        self.assertEqual(result, {"ok": ""})

    def test_summary_keeps_unpinned_and_unknown_entries_visible(self) -> None:
        def results(status):
            return [{"id": "a", "issues": [{"status": status, "detail": ""}]}]

        self.assertEqual(CHECKER.summarize(results("unpinned")),
                         {"checked": 1, "broken": False, "actionable": True, "unknown": False})
        self.assertEqual(CHECKER.summarize(results("upstream-path-change"))["actionable"], True)
        self.assertEqual(CHECKER.summarize(results("unreachable")),
                         {"checked": 1, "broken": False, "actionable": False, "unknown": True})
        self.assertEqual(CHECKER.summarize(results("ok")),
                         {"checked": 1, "broken": False, "actionable": False, "unknown": False})

    def test_collection_reports_missing_and_new_children(self) -> None:
        head = self.commit({"skills/beta/SKILL.md": "---\nname: beta\ndescription: B.\n---\n"})
        children = [{"id": "alpha", "path": "skills/alpha"}, {"id": "gamma", "path": "skills/gamma"}]
        result = self.statuses(self.entry(ref=head, children=children))
        self.assertIn("gamma", result["bad-path"])
        self.assertEqual(result["new-skill"], "skills/beta")

    def test_markdown_groups_broken_entries_first(self) -> None:
        results = [
            {"id": "a", "kind": "skill", "url": "u", "issues": [{"status": "outdated", "detail": "x"}]},
            {"id": "b", "kind": "skill", "url": "u", "issues": [{"status": "gone", "detail": "y"}]},
        ]
        text = CHECKER.render_markdown(results)
        self.assertLess(text.index("Broken"), text.index("Updates available"))


if __name__ == "__main__":
    unittest.main()
