#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""候选生成只推进来源事实，不冒用旧审核证据。"""
import copy
import unittest
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch
import propose_upstream_updates as proposer
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


    def exercise_publish(self, audited=True, validation_failure=False, publish_failure=False):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); folder = root / 'skills/sample'; folder.mkdir(parents=True)
            (folder/'entry.json').write_text(json.dumps(self.entry))
            (folder/'catalog-metadata.v1.json').write_text(json.dumps(self.sidecar))
            results = root/'results.json'; results.write_text(json.dumps([self.result]))
            updated, metadata = candidate(self.entry, self.sidecar, self.result)
            metadata['governance']['compliance'].update(reviewedRef=self.new, reviewedBy='automated:test')
            seen = {}
            def run(*args, cwd=None):
                if args[:3] == ('gh', 'pr', 'list'): return '[]'
                if args[:3] == ('git', 'worktree', 'add'):
                    shutil.copytree(root/'skills', Path(args[4])/'skills'); return ''
                if args[0] == 'uv' and validation_failure:
                    raise subprocess.CalledProcessError(1, args, output='catalog failure')
                if args[:3] == ('gh', 'pr', 'create'):
                    if publish_failure:
                        raise subprocess.CalledProcessError(1, args, stderr='API unavailable')
                    seen['draft'] = '--draft' in args
                    seen['metadata'] = json.loads((cwd/'skills/sample/catalog-metadata.v1.json').read_text())
                    seen['audit'] = json.loads((cwd/'skills/sample/upstream-audit.v1.json').read_text()) if (cwd/'skills/sample/upstream-audit.v1.json').exists() else None
                return ''
            with patch.object(proposer, 'ROOT', root), patch.object(proposer, 'run', side_effect=run), \
                 patch.object(proposer, 'audit_update', return_value=(updated, metadata, {'reviewer':'automated:test'}),
                              side_effect=None if audited else proposer.AuditBlocked('license changed')), \
                 patch.dict(os.environ, {'GITHUB_REPOSITORY':'desirecore/market', 'GITHUB_ACTOR':'example-user'}), \
                 patch('sys.argv', ['propose', str(results), '--publish', '--coverage-file', str(root/'coverage.json')]):
                if publish_failure:
                    with self.assertRaises(subprocess.CalledProcessError): proposer.main()
                else:
                    proposer.main()
            seen['coverage'] = json.loads((root/'coverage.json').read_text())
            return seen

    def test_successful_audit_and_validation_create_a_normal_pr(self):
        result = self.exercise_publish()
        self.assertFalse(result['draft'])
        self.assertEqual(result['metadata']['governance']['compliance']['reviewedRef'], self.new)
        self.assertEqual(result['audit']['reviewer'], 'automated:test')

    def test_audit_failure_keeps_old_review_and_draft(self):
        result = self.exercise_publish(audited=False)
        self.assertTrue(result['draft'])
        self.assertEqual(result['metadata']['governance']['compliance']['reviewedRef'], self.old)
        self.assertEqual(result['coverage'][0]['status'], 'manual-review-required')

    def test_validator_failure_cannot_publish_a_successful_audit(self):
        result = self.exercise_publish(validation_failure=True)
        self.assertTrue(result['draft'])
        self.assertEqual(result['metadata']['governance']['compliance']['reviewedRef'], self.old)
        self.assertEqual(result['audit']['status'], 'blocked')

    def test_publish_failure_still_writes_truthful_coverage(self):
        result = self.exercise_publish(publish_failure=True)
        self.assertEqual(result['coverage'][0]['status'], 'publish-failed')

    def test_coverage_includes_builtins_and_http_blockers(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for item in ['builtin', 'sample', 'archive']:
                folder = root/'skills'/item; folder.mkdir(parents=True)
                if item == 'builtin': (folder/'SKILL.md').write_text('fixture')
                else:
                    entry = copy.deepcopy(self.entry); entry['id'] = item
                    if item == 'archive': entry['source']['kind'] = 'zip'
                    (folder/'entry.json').write_text(json.dumps(entry))
            rows = {row['id']: row for row in proposer.coverage([self.result], root)}
            self.assertEqual(set(rows), {'builtin','sample','archive'})
            self.assertEqual(rows['builtin']['status'], 'market-release')
            self.assertEqual(rows['archive']['status'], 'governance-blocked')
            self.assertEqual(rows['sample']['status'], 'queued')


if __name__ == "__main__":
    unittest.main()
