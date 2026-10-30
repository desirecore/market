"""候选生成只推进来源事实，不冒用旧审核证据。"""
import copy
import unittest
from propose_upstream_updates import candidate


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.old, self.new = "a" * 40, "b" * 40
        self.entry = {"id": "sample", "latestVersion": "1.0.0", "source": {
            "kind": "git", "repoUrl": "https://github.com/example/sample.git", "ref": self.old}}
        self.sidecar = {"provenance": {"content": {
            "kind": "git", "url": self.entry["source"]["repoUrl"], "ref": self.old}},
            "governance": {"compliance": {"reviewedRef": self.old, "reviewedBy": "reviewer"}}}
        self.result = {"id": "sample", "kind": "skill", "url": self.entry["source"]["repoUrl"],
                       "ref": self.old, "head": self.new, "issues": [{"status": "outdated"}]}

    def test_same_version_content_change_is_proposed_without_fake_review(self):
        before = copy.deepcopy((self.entry, self.sidecar))
        entry, sidecar = candidate(self.entry, self.sidecar, self.result)
        self.assertEqual(entry["source"]["ref"], self.new)
        self.assertEqual(sidecar["provenance"]["content"]["ref"], self.new)
        self.assertEqual(sidecar["governance"], self.sidecar["governance"])
        self.assertEqual(entry["latestVersion"], "1.0.0")
        self.assertEqual((self.entry, self.sidecar), before)

    def test_bad_or_held_snapshots_are_not_proposed(self):
        for status in ("bad-path", "held", "stale-hold", "unreachable", "upstream-path-change"):
            with self.subTest(status=status):
                self.result["issues"] = [{"status": "outdated"}, {"status": status}]
                self.assertIsNone(candidate(self.entry, self.sidecar, self.result))

    def test_stale_report_or_untrusted_paths_are_not_proposed(self):
        for field, value in (("id", "../sample"), ("ref", "c" * 40), ("head", "main"),
                             ("url", "https://github.com/example/other.git"), ("kind", "agent")):
            with self.subTest(field=field):
                result = {**self.result, field: value}
                self.assertIsNone(candidate(self.entry, self.sidecar, result))

    def test_sidecar_must_agree_with_checked_snapshot(self):
        self.sidecar["provenance"]["content"]["ref"] = self.new
        self.assertIsNone(candidate(self.entry, self.sidecar, self.result))


if __name__ == "__main__":
    unittest.main()
