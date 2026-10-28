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
                         {"checked": 1, "broken": False, "actionable": True, "unknown": False, "held": 0})
        self.assertEqual(CHECKER.summarize(results("upstream-path-change"))["actionable"], True)
        self.assertEqual(CHECKER.summarize(results("unreachable")),
                         {"checked": 1, "broken": False, "actionable": False, "unknown": True, "held": 0})
        self.assertEqual(CHECKER.summarize(results("ok")),
                         {"checked": 1, "broken": False, "actionable": False, "unknown": False, "held": 0})

    def hold(self, entry_path: Path, **fields) -> Path:
        head = sh("git", "rev-parse", "HEAD", cwd=self.upstream)
        data = {"statuses": ["outdated"], "ref": self.first, "head": head,
                "reviewedAt": "2026-10-01", "reason": "New layout cannot be installed as a subtree."}
        path = entry_path.parent / "upstream-health-hold.json"
        path.write_text(json.dumps({**data, **fields}), encoding="utf-8")
        return path

    def test_reviewed_hold_replaces_outdated_while_head_is_unchanged(self) -> None:
        head = self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated.\n---\n"})
        entry = self.entry(ref=self.first, path="skills/alpha")
        self.hold(entry)
        reviewed = "reviewed 2026-10-01: New layout cannot be installed as a subtree."
        self.assertEqual(self.statuses(entry), {"held": f"outdated: {self.first[:7]} -> {head[:7]} — {reviewed}"})

    def test_hold_survives_upstream_changes_outside_the_installed_scope(self) -> None:
        reviewed = self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated.\n---\n"})
        entry = self.entry(ref=self.first, path="skills/alpha")
        self.hold(entry, head=reviewed)
        self.commit({"README.md": "New website.\n"})
        self.assertEqual(set(self.statuses(entry)), {"held"})

    def test_in_scope_change_after_review_reraises_outdated(self) -> None:
        reviewed = self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated.\n---\n"})
        entry = self.entry(ref=self.first, path="skills/alpha")
        self.hold(entry, head=reviewed)
        self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated again.\n---\n"})
        result = self.statuses(entry)
        self.assertIn("outdated", result)
        self.assertNotIn("held", result)
        self.assertIn(f"since {reviewed[:7]}", result["stale-hold"])

    def test_unfetchable_reviewed_head_is_a_stale_hold(self) -> None:
        self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated.\n---\n"})
        entry = self.entry(ref=self.first, path="skills/alpha")
        self.hold(entry, head="f" * 40)
        result = self.statuses(entry)
        self.assertIn("outdated", result)
        self.assertIn("cannot be fetched", result["stale-hold"])

    def test_network_error_on_reviewed_head_is_unknown_not_stale(self) -> None:
        head = self.commit({"README.md": "Unrelated.\n"})
        self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated.\n---\n"})
        entry = self.entry(ref=self.first, path="skills/alpha")
        self.hold(entry, head=head)
        real_git = CHECKER.git

        def failing_fetch(*args, **kwargs):
            if args[0] == "fetch" and head in args:
                return subprocess.CompletedProcess(args, 128, "", "Connection reset by peer")
            return real_git(*args, **kwargs)

        with patch.object(CHECKER, "git", side_effect=failing_fetch):
            result = self.statuses(entry)
        self.assertIn("outdated", result)
        self.assertIn("unreachable", result)
        self.assertNotIn("stale-hold", result)

    def test_unknown_comparison_neither_applies_nor_stales_the_hold(self) -> None:
        self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated.\n---\n"})
        entry = self.entry(ref=self.first, path="skills/alpha")
        self.hold(entry)
        real_git = CHECKER.git

        def failing_diff(*args, **kwargs):
            if args[0] == "diff":
                return subprocess.CompletedProcess(args, 128, "", "fatal: unable to read tree")
            return real_git(*args, **kwargs)

        with patch.object(CHECKER, "git", side_effect=failing_diff):
            self.assertEqual(set(self.statuses(entry)), {"unreachable"})

    def test_changed_pin_makes_the_hold_stale(self) -> None:
        second = self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated.\n---\n"})
        self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated again.\n---\n"})
        entry = self.entry(ref=second, path="skills/alpha")
        self.hold(entry)
        result = self.statuses(entry)
        self.assertIn("outdated", result)
        self.assertIn("pinned ref changed", result["stale-hold"])

    def test_hold_without_a_remaining_finding_is_stale(self) -> None:
        entry = self.entry(ref=self.first, path="skills/alpha")
        self.hold(entry)
        result = self.statuses(entry)
        self.assertEqual(set(result), {"stale-hold"})
        self.assertIn("no held finding remains", result["stale-hold"])

    def test_hold_covers_upstream_path_change_and_reports_unlisted_findings(self) -> None:
        (self.upstream / "skills/alpha/SKILL.md").unlink()
        self.commit({"skills/beta/SKILL.md": "---\nname: beta\ndescription: B.\n---\n"})
        entry = self.entry(ref=self.first, path="skills/alpha")
        self.hold(entry, statuses=["upstream-path-change"])
        result = self.statuses(entry)
        self.assertTrue(result["held"].startswith("upstream-path-change: source.path 'skills/alpha' has no"))
        self.assertIn("outdated", result)
        self.assertNotIn("upstream-path-change", result)
        self.hold(entry, statuses=["upstream-path-change", "outdated"])
        issues = CHECKER.check_entry(entry)["issues"]
        self.assertEqual([i["status"] for i in issues], ["held", "held"])

    def test_hold_validation_rejects_unholdable_statuses_bad_shas_and_extra_keys(self) -> None:
        valid = {"statuses": ["upstream-path-change", "outdated"], "ref": "a" * 40, "head": "b" * 40,
                 "reviewedAt": "2026-10-01", "reason": "Kept after review."}
        self.assertEqual(CHECKER.hold_errors(valid), [])
        invalid = [{"statuses": [status]} for status in
                   (*CHECKER.BROKEN, "unreachable", "new-skill", "unpinned", "held", "stale-hold", "ok")]
        invalid += [{"statuses": []}, {"statuses": "outdated"}, {"statuses": ["outdated", "outdated"]},
                    {"ref": "A" * 40}, {"ref": "a" * 12}, {"head": "g" * 40}, {"head": None},
                    {"reviewedAt": "2026-13-01"}, {"reviewedAt": "18/10/2026"}, {"reason": " "}, {"reason": 1},
                    {"note": "extra"}]
        for fields in invalid:
            with self.subTest(fields=fields):
                self.assertTrue(CHECKER.hold_errors({**valid, **fields}))
        self.assertTrue(CHECKER.hold_errors({k: v for k, v in valid.items() if k != "reason"}))
        self.assertTrue(CHECKER.hold_errors(["outdated"]))

    def test_invalid_hold_file_is_stale_and_hides_nothing(self) -> None:
        self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated.\n---\n"})
        entry = self.entry(ref=self.first, path="skills/alpha")
        hold = self.hold(entry, statuses=["outdated", "gone"])
        result = self.statuses(entry)
        self.assertIn("outdated", result)
        self.assertIn("invalid", result["stale-hold"])
        hold.write_text("{", encoding="utf-8")
        self.assertIn("invalid", self.statuses(entry)["stale-hold"])

    def test_hold_on_a_non_git_entry_is_stale(self) -> None:
        entry = self.entry(kind="web", url="https://example.com/skill.zip")
        self.hold(entry)
        with patch.object(CHECKER, "check_http", return_value=[]):
            result = self.statuses(entry)
        self.assertEqual(set(result), {"stale-hold"})
        self.assertIn("git entries", result["stale-hold"])

    def test_held_alone_is_not_actionable_but_stale_hold_is(self) -> None:
        def results(*statuses):
            return [{"id": "a", "issues": [{"status": s, "detail": ""} for s in statuses]}]

        self.assertEqual(CHECKER.summarize(results("held", "held")),
                         {"checked": 1, "broken": False, "actionable": False, "unknown": False, "held": 2})
        self.assertEqual(CHECKER.summarize(results("stale-hold")),
                         {"checked": 1, "broken": False, "actionable": True, "unknown": False, "held": 0})

    def test_markdown_lists_reviewed_holds_separately(self) -> None:
        results = [
            {"id": "a", "kind": "skill", "url": "u", "issues": [{"status": "held", "detail": "outdated: x"}]},
            {"id": "b", "kind": "skill", "url": "u", "issues": [{"status": "stale-hold", "detail": "y"}]},
        ]
        text = CHECKER.render_markdown(results)
        self.assertIn("### Reviewed holds — not actionable (1)", text)
        self.assertLess(text.index("Stale holds — re-review"), text.index("Reviewed holds"))
        self.assertNotIn("OK (", text)

    def test_repository_hold_files_are_valid_and_match_the_pin(self) -> None:
        for kind in CHECKER.KINDS:
            for path in sorted((CHECKER.REPO_ROOT / kind).glob("*/upstream-health-hold.json")):
                with self.subTest(hold=f"{kind}/{path.parent.name}"):
                    entry_path = path.with_name("entry.json")
                    self.assertTrue(entry_path.is_file(), "a hold belongs next to an external entry.json")
                    hold, errors = CHECKER.load_hold(entry_path)
                    self.assertEqual(errors, [])
                    source = json.loads(entry_path.read_text(encoding="utf-8"))["source"]
                    self.assertEqual(source.get("kind"), "git")
                    self.assertEqual(source.get("ref"), hold["ref"],
                                     "bumping source.ref must update or remove the reviewed hold")

    def test_collection_ignores_changes_outside_declared_children(self) -> None:
        self.commit({"cmd/main.go": "package main\n", "README.md": "Release notes.\n"})
        children = [{"id": "alpha", "path": "skills/alpha"}]
        self.assertEqual(self.statuses(self.entry(ref=self.first, children=children)), {"ok": ""})

    def test_collection_child_change_is_outdated(self) -> None:
        self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated.\n---\n"})
        children = [{"id": "alpha", "path": "skills/alpha"}]
        self.assertIn("outdated", self.statuses(self.entry(ref=self.first, children=children)))

    def test_root_license_change_still_needs_review_for_a_collection(self) -> None:
        self.commit({"NOTICE": "New attribution.\n"})
        children = [{"id": "alpha", "path": "skills/alpha"}]
        self.assertIn("outdated", self.statuses(self.entry(ref=self.first, children=children)))

    def test_result_records_pinned_ref_and_checked_head(self) -> None:
        head = self.commit({"skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Updated.\n---\n"})
        result = CHECKER.check_entry(self.entry(ref=self.first, path="skills/alpha"))
        self.assertEqual((result["ref"], result["head"]), (self.first, head))

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

    def test_markdown_links_outdated_entry_to_upstream_compare(self) -> None:
        ref, head = "a19a171" + "0" * 33, "94f06c1" + "0" * 33
        results = [{"id": "a", "kind": "skill", "url": "https://github.com/o/r.git", "ref": ref, "head": head,
                    "issues": [{"status": "outdated", "detail": "a19a171 -> 94f06c1"}]}]
        self.assertIn(f"| [a19a171 → 94f06c1](https://github.com/o/r/compare/{ref}...{head}) |",
                      CHECKER.render_markdown(results))

    def test_compare_url_accepts_github_url_variants(self) -> None:
        ref, head = "a" * 40, "b" * 40
        for url in ("https://github.com/o/r.git", "https://github.com/o/r", "https://github.com/o/r/",
                    "https://github.com/o/r.git/"):
            with self.subTest(url=url):
                self.assertEqual(CHECKER.compare_url(url, ref, head),
                                 f"https://github.com/o/r/compare/{ref}...{head}")

    def test_markdown_keeps_plain_detail_without_compare_url(self) -> None:
        ref, head = "a" * 40, "b" * 40
        for url, pinned, checked in (("https://git.example.com/o/r.git", ref, head),
                                     ("https://github.com/o/r.git", None, head),
                                     ("https://github.com/o/r.git", ref, None),
                                     (None, ref, head)):
            with self.subTest(url=url, ref=pinned, head=checked):
                self.assertIsNone(CHECKER.compare_url(url, pinned, checked))
                results = [{"id": "a", "kind": "skill", "url": url, "ref": pinned, "head": checked,
                            "issues": [{"status": "outdated", "detail": "aaaaaaa -> bbbbbbb"}]}]
                text = CHECKER.render_markdown(results)
                self.assertIn("| aaaaaaa -> bbbbbbb |", text)
                self.assertNotIn("/compare/", text)

    def test_markdown_links_only_outdated_rows(self) -> None:
        results = [{"id": "a", "kind": "skill", "url": "https://github.com/o/r.git", "ref": "a" * 40,
                    "head": "b" * 40, "issues": [{"status": "outdated", "detail": "aaaaaaa -> bbbbbbb"},
                                                 {"status": "upstream-path-change", "detail": "x | y"}]}]
        text = CHECKER.render_markdown(results)
        self.assertEqual(text.count("/compare/"), 1)
        self.assertIn("| x \\| y |", text)


if __name__ == "__main__":
    unittest.main()
