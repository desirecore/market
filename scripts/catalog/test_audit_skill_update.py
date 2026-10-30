#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0", "jsonschema>=4.23,<5"]
# ///
"""真实本地 Git 快照的自动核验；不联网、不运行上游代码。"""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from audit_skill_update import audit_snapshots, audit_update, AuditBlocked, REVIEWER


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.repo = Path(self.tmp.name)
        self.run_git('init', '--quiet')
        self.run_git('config', 'user.name', 'test'); self.run_git('config', 'user.email', 'test@example.com')
        self.write('LICENSE', 'MIT fixture; previously reviewed bytes\n')
        self.write('skills/sample/SKILL.md', '---\nname: sample\ndescription: Fixture\nversion: 1.0.0\n---\nOld instructions\n')
        self.write('skills/sample/scripts/tool.py', 'print("fixture")\n')
        self.old = self.commit()
        self.entry = {'id': 'sample', 'latestVersion': '1.0.0', 'source': {'kind': 'git',
            'repoUrl': 'https://github.com/example/sample.git', 'ref': self.old, 'path': 'skills/sample'}}
        self.metadata = {'identity': {'kind':'skill','id':'sample'}, 'provenance': {'content': {'kind': 'git', 'url': self.entry['source']['repoUrl'], 'ref': self.old, 'path': 'skills/sample'}},
            'release': {'state': 'known', 'version': '1.0.0', 'versionScheme': 'semver'},
            'timestamps': {'releasePublishedAt': {'state': 'known', 'value': '2026-10-01', 'precision': 'day'}},
            'governance': {'availability': 'installable', 'license': {'state': 'known', 'value': 'MIT', 'evidencePath': 'LICENSE'},
                'compliance': {'licenseEvidencePath': 'LICENSE', 'reviewedRef': self.old, 'reviewedAt': '2026-10-01',
                               'reviewedBy': 'previous-reviewer', 'upstreamEndorsed': False}}}

    def tearDown(self): self.tmp.cleanup()
    def run_git(self, *args):
        return subprocess.run(['git', *args], cwd=self.repo, check=True, capture_output=True, text=True).stdout.strip()
    def write(self, path, data):
        file = self.repo / path; file.parent.mkdir(parents=True, exist_ok=True); file.write_text(data)
    def commit(self):
        self.run_git('add', '-A'); self.run_git('commit', '--quiet', '-m', 'fixture')
        return self.run_git('rev-parse', 'HEAD')
    def audit(self):
        new = self.commit()
        return audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z')

    def test_same_version_scripts_change_has_truthful_new_receipt(self):
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        before = copy.deepcopy(self.metadata)
        entry, metadata, report = self.audit()
        self.assertEqual(entry['latestVersion'], '1.0.0')
        self.assertEqual(metadata['governance']['compliance']['reviewedRef'], entry['source']['ref'])
        self.assertEqual(metadata['governance']['compliance']['reviewedBy'], REVIEWER)
        self.assertEqual(metadata['timestamps']['reviewedAt']['value'], '2026-10-31')
        self.assertEqual(metadata['governance']['compliance']['upstreamEndorsed'], False)
        self.assertEqual(self.metadata, before)
        self.assertEqual(report['source']['ref'], entry['source']['ref'])
        self.assertTrue(report['checks']['licenseAndNoticeUnchanged'])
        self.assertEqual(len(report['contentManifestSha256']), 64)

    def test_version_is_from_upstream_and_release_date_not_invented(self):
        path = 'skills/sample/SKILL.md'; self.write(path, (self.repo/path).read_text().replace('1.0.0', '1.1.0'))
        entry, metadata, _ = self.audit()
        self.assertEqual(entry['latestVersion'], '1.1.0')
        self.assertEqual(metadata['release']['version'], '1.1.0')
        self.assertEqual(metadata['timestamps']['releasePublishedAt'], {'state': 'unknown'})

    def test_missing_upstream_version_is_not_invented(self):
        path = 'skills/sample/SKILL.md'; self.write(path, (self.repo/path).read_text().replace('version: 1.0.0\n', ''))
        entry, _, report = self.audit()
        self.assertEqual(entry['latestVersion'], '1.0.0')
        self.assertEqual(report['observedVersions'], {})

    def test_changed_license_or_new_notice_requires_review(self):
        for path, content in [('LICENSE', 'different terms'), ('NOTICE', 'new terms')]:
            with self.subTest(path=path):
                self.run_git('reset', '--hard', self.old)
                self.run_git('clean', '-fd')
                self.write(path, content)
                with self.assertRaisesRegex(AuditBlocked, '许可证|Notice'): self.audit()

    def test_nested_license_changes_require_review(self):
        self.write('skills/sample/vendor/LICENSE', 'new vendor terms')
        with self.assertRaisesRegex(AuditBlocked, '许可证|Notice'): self.audit()

    def test_collection_child_version_cannot_roll_back(self):
        self.entry['children'] = [{'id': 'sample', 'path': 'skills/sample', 'version': '1.0.0'}]
        self.metadata['spec'] = {'collection': {'children': [{'identity': {'id':'sample'}, 'path':'skills/sample'}]}}
        path = 'skills/sample/SKILL.md'
        self.write(path, (self.repo/path).read_text().replace('1.0.0', '0.9.0'))
        with self.assertRaisesRegex(AuditBlocked, '回退'): self.audit()

    def test_dependency_or_description_changes_are_not_auto_approved(self):
        self.write('requirements.txt', 'new-library==1.0\n')
        with self.assertRaisesRegex(AuditBlocked, '依赖清单'): self.audit()
        self.run_git('reset', '--hard', self.old); self.run_git('clean', '-fd')
        path = 'skills/sample/SKILL.md'; self.write(path, (self.repo/path).read_text().replace('description: Fixture', 'description: Needs another engine'))
        with self.assertRaisesRegex(AuditBlocked, '结构化声明'): self.audit()

    def test_symlink_and_version_rollback_are_blocked(self):
        (self.repo/'skills/sample/alias').symlink_to('SKILL.md')
        with self.assertRaisesRegex(AuditBlocked, '符号链接'): self.audit()
        self.run_git('reset', '--hard', self.old); self.run_git('clean', '-fd')
        path = 'skills/sample/SKILL.md'; self.write(path, (self.repo/path).read_text().replace('1.0.0', '0.9.0'))
        with self.assertRaisesRegex(AuditBlocked, '回退'): self.audit()

    def test_old_review_must_bind_the_old_pin(self):
        self.write('skills/sample/scripts/tool.py', 'new')
        self.metadata['governance']['compliance']['reviewedRef'] = 'a' * 40
        with self.assertRaisesRegex(AuditBlocked, '旧快照'): self.audit()

    def test_machine_receipt_rejects_tampered_checks_dates_and_bindings(self):
        from automated_review import validate_record
        self.write('skills/sample/scripts/tool.py', 'new fixture')
        _, metadata, receipt = self.audit()
        self.assertEqual(validate_record(metadata, receipt), [])
        wrong_scope = copy.deepcopy(receipt); wrong_scope['source']['paths'] = ['another/path']
        self.assertTrue(validate_record(metadata, wrong_scope))
        variants = []
        for field, value in [('reviewer','human'),('reviewedAt','2026-10-30T01:02:03Z'),('contentManifestSha256','bad')]:
            altered = copy.deepcopy(receipt); altered[field] = value; variants.append(altered)
        altered = copy.deepcopy(receipt); altered['source']['previousRef'] = None; variants.append(altered)
        altered = copy.deepcopy(receipt); altered['checks']['licenseAndNoticeUnchanged'] = False; variants.append(altered)
        for altered in variants:
            self.assertTrue(validate_record(metadata, altered))

    def test_collection_updates_child_versions_without_inventing_translations(self):
        self.entry['children'] = [{'id': 'sample', 'path': 'skills/sample', 'version': '1.0.0', 'i18n': {'zh-CN': {'name': '示例'}}}]
        self.metadata['spec'] = {'collection': {'children': [{'identity': {'id':'sample'}, 'path':'skills/sample', 'release': {'state':'known','version':'1.0.0','versionScheme':'semver'}}]}}
        path = 'skills/sample/SKILL.md'; self.write(path, (self.repo/path).read_text().replace('1.0.0', '1.1.0'))
        entry, metadata, _ = self.audit()
        self.assertEqual(entry['children'][0]['version'], '1.1.0')
        self.assertEqual(entry['children'][0]['i18n'], self.entry['children'][0]['i18n'])
        self.assertEqual(metadata['spec']['collection']['children'][0]['release']['version'], '1.1.0')
        self.write('skills/another/SKILL.md', '---\nname: another\ndescription: New member\n---\n')
        with self.assertRaisesRegex(AuditBlocked, '合集成员'): self.audit()

    def test_upstream_scripts_are_not_executed(self):
        sentinel = self.repo / 'should-not-exist'
        self.write('skills/sample/scripts/tool.py', f'from pathlib import Path; Path({str(sentinel)!r}).touch()')
        self.audit()
        self.assertFalse(sentinel.exists())

    def test_package_version_change_is_not_a_dependency_change(self):
        self.write('package.json', json.dumps({'name':'fixture','version':'1.0.0','dependencies':{'example':'1.0'}}))
        self.old = self.commit(); self.entry['source']['ref'] = self.old
        self.metadata['provenance']['content']['ref'] = self.old
        self.metadata['governance']['compliance']['reviewedRef'] = self.old
        self.write('package.json', json.dumps({'name':'fixture','version':'1.1.0','dependencies':{'example':'1.0'}}))
        self.audit()
        self.write('package.json', json.dumps({'name':'fixture','version':'1.1.0','dependencies':{'example':'2.0'}}))
        with self.assertRaisesRegex(AuditBlocked, '依赖清单'): self.audit()

    def test_generated_audit_metadata_passes_the_real_catalog_validator(self):
        from jsonschema import Draft7Validator, FormatChecker
        import validate_catalog_metadata as validator
        from test_validate_catalog_metadata import valid_entry, valid_sidecar
        entry = valid_entry(); metadata = valid_sidecar()
        entry['id'] = 'sample'; entry['source'] = copy.deepcopy(self.entry['source'])
        metadata['identity']['id'] = 'sample'
        metadata['provenance']['content'] = {'kind':'git','url':entry['source']['repoUrl'],'path':'skills/sample','ref':self.old}
        metadata['governance']['availability'] = 'installable'
        metadata['governance']['redistribution'] = entry['redistribution']
        metadata['governance']['license']['evidencePath'] = 'LICENSE'
        metadata['governance']['compliance'] = copy.deepcopy(self.metadata['governance']['compliance'])
        self.write('skills/sample/scripts/tool.py', 'new fixture')
        head = self.commit()
        updated, sidecar, receipt = audit_snapshots(self.repo, entry, metadata, {'ref':self.old,'head':head}, '2026-10-31T01:02:03Z')
        root = self.repo/'catalog'; folder = root/'skills/sample'; folder.mkdir(parents=True)
        (folder/'entry.json').write_text(json.dumps(updated))
        path = folder/'catalog-metadata.v1.json'; path.write_text(json.dumps(sidecar))
        audit_path = folder/'upstream-audit.v1.json'; audit_path.write_text(json.dumps(receipt))
        schema = json.loads((Path(__file__).resolve().parents[2]/'schemas/catalog-metadata.v1.schema.json').read_text())
        report = validator.Report()
        validator.validate_sidecar(path, Draft7Validator(schema, format_checker=FormatChecker()), report, root, {'zh-CN','en-US'}, {})
        self.assertFalse(report.has_errors, report.issues)
        receipt['source']['ref'] = 'f' * 40
        audit_path.write_text(json.dumps(receipt))
        report = validator.Report()
        validator.validate_sidecar(path, Draft7Validator(schema, format_checker=FormatChecker()), report, root, {'zh-CN','en-US'}, {})
        self.assertTrue(any(issue.rule == 'automated-review-evidence' for issue in report.issues))

    def test_disallows_non_github_fetch_targets(self):
        self.entry['source']['repoUrl'] = 'file:///private/source'
        with self.assertRaisesRegex(AuditBlocked, 'HTTPS'): audit_update(self.entry, self.metadata, {})


if __name__ == '__main__': unittest.main()
