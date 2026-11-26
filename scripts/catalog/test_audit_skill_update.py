#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0", "jsonschema>=4.23,<5"]
# ///
"""真实本地 Git 快照的自动核验；不联网、不运行上游代码。"""
import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from audit_skill_update import (audit_snapshots, audit_update, AuditBlocked, REVIEWER,
                                 GENERATOR, frontmatter_identity, _text_sha256)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.repo = Path(self.tmp.name)
        self.run_git('init', '--quiet')
        self.run_git('config', 'user.name', 'test'); self.run_git('config', 'user.email', 'test@example.com')
        self.mit = (Path(__file__).resolve().parents[2] / 'LICENSE').read_text()
        self.write('LICENSE', self.mit)
        self.write('skills/sample/LICENSE', self.mit)
        self.write('skills/another/LICENSE', self.mit)
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
        self.write('skills/another/LICENSE', self.mit)
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
        entry_schema = json.loads((Path(__file__).resolve().parents[2] / 'schemas' / validator.SKILL_ENTRY_SCHEMA_NAME).read_text())
        entry_validators = {
            'skill': validator.ClientEntryValidator(entry_schema, format_checker=FormatChecker()),
        }
        report = validator.Report()
        validator.validate_sidecar(path, Draft7Validator(schema, format_checker=FormatChecker()), report, root, {'zh-CN','en-US'}, entry_validators)
        self.assertFalse(report.has_errors, report.issues)
        receipt['source']['ref'] = 'f' * 40
        audit_path.write_text(json.dumps(receipt))
        report = validator.Report()
        validator.validate_sidecar(path, Draft7Validator(schema, format_checker=FormatChecker()), report, root, {'zh-CN','en-US'}, entry_validators)
        self.assertTrue(any(issue.rule == 'automated-review-evidence' for issue in report.issues))


    def test_exclude_paths_skip_symlinks_and_cannot_hide_license(self):
        (self.repo/'skills/sample/evals').mkdir(parents=True)
        (self.repo/'skills/sample/evals/AGENTS.md').symlink_to('SKILL.md')
        with self.assertRaisesRegex(AuditBlocked, '符号链接'):
            self.audit()
        self.run_git('reset', '--hard', self.old); self.run_git('clean', '-fd')
        (self.repo/'skills/sample/evals').mkdir(parents=True)
        (self.repo/'skills/sample/evals/AGENTS.md').symlink_to('SKILL.md')
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        new = self.commit()
        review = {'schemaVersion': 1, 'excludePaths': ['skills/sample/evals/AGENTS.md']}
        audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z', special_review=review)
        review = {'schemaVersion': 1, 'excludePaths': ['skills/sample/evals/AGENTS.md', 'LICENSE']}
        with self.assertRaisesRegex(AuditBlocked, '排除列表'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z', special_review=review)

    def test_budget_exempt_allows_known_oversize_file(self):
        big = 'skills/sample/data/index.json'
        self.write(big, 'x' * (1024 * 1024 + 50))
        self.old = self.commit()
        self.entry['source']['ref'] = self.old
        self.metadata['provenance']['content']['ref'] = self.old
        self.metadata['governance']['compliance']['reviewedRef'] = self.old
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        new = self.commit()
        with self.assertRaisesRegex(AuditBlocked, '单文件超过'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z')
        review = {'schemaVersion': 1, 'budgetExemptPaths': [big]}
        audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z', special_review=review)

    def test_special_review_accepts_dependency_and_frontmatter_change(self):
        from audit_skill_update import dependency_identity, frontmatter_identity
        from check_upstream_health import GENERATOR
        self.write('package.json', json.dumps({'name':'humanizer','private':True,'license':'MIT'}))
        path = 'skills/sample/SKILL.md'
        self.write(path, (self.repo/path).read_text().replace('description: Fixture', 'description: Rewritten blurb'))
        new = self.commit()
        with self.assertRaisesRegex(AuditBlocked, '依赖清单'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z')
        ident = dependency_identity(self.repo, new, 'package.json', ('100644', 'unused', 0))
        fm = GENERATOR.skill_frontmatter(self.repo, path, new)
        review = {
            'schemaVersion': 1,
            'acceptedDependencyIdentities': {'package.json': ident[1]},
            'acceptedFrontmatterSha256': {'skills/sample': frontmatter_identity(fm)},
        }
        entry, metadata, report = audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z', special_review=review)
        self.assertEqual(metadata['governance']['compliance']['reviewedBy'], REVIEWER)
        self.assertEqual(report['specialReview']['reviewedBy'] if report.get('specialReview') else None, None)

    def test_special_review_accepts_new_collection_member(self):
        from audit_skill_update import frontmatter_identity
        from check_upstream_health import GENERATOR
        self.entry['children'] = [{'id': 'sample', 'path': 'skills/sample', 'version': '1.0.0', 'i18n': {'zh-CN': {'name': '示例'}}}]
        self.metadata['spec'] = {'collection': {'children': [{'identity': {'id':'sample'}, 'path':'skills/sample', 'release': {'state':'known','version':'1.0.0','versionScheme':'semver'}}]}}
        self.write('skills/another/LICENSE', self.mit)
        self.write('skills/another/SKILL.md', '---\nname: another\ndescription: New member\nversion: 0.1.0\n---\nBody\n')
        new = self.commit()
        fm = GENERATOR.skill_frontmatter(self.repo, 'skills/another/SKILL.md', new)
        discovered = [child['path'] for child in GENERATOR.discover_children(self.repo, new)]
        with self.assertRaisesRegex(AuditBlocked, '合集成员'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z')
        review = {
            'schemaVersion': 1,
            'acceptedCollectionPaths': discovered,
            'acceptedFrontmatterSha256': {'skills/another': frontmatter_identity(fm)},
        }
        entry, metadata, report = audit_snapshots(
            self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z', special_review=review)
        ids = [child['id'] for child in entry['children']]
        self.assertEqual(set(ids), {'sample', 'another'})
        another = next(child for child in entry['children'] if child['id'] == 'another')
        self.assertEqual(another['path'], 'skills/another')
        self.assertEqual(another['version'], '0.1.0')
        self.assertNotIn('i18n', another)
        sample = next(child for child in entry['children'] if child['id'] == 'sample')
        self.assertEqual(sample['i18n'], self.entry['children'][0]['i18n'])
        catalog_ids = [child['identity']['id'] for child in metadata['spec']['collection']['children']]
        self.assertEqual(set(catalog_ids), {'sample', 'another'})
        catalog_another = next(child for child in metadata['spec']['collection']['children'] if child['identity']['id'] == 'another')
        self.assertNotIn('i18n', catalog_another)
        self.assertEqual(catalog_another['release']['version'], '0.1.0')
        self.assertEqual(report['source']['paths'], sorted(['skills/sample', 'skills/another']))

    def test_special_review_rejects_wrong_collection_or_frontmatter_acceptance(self):
        from audit_skill_update import frontmatter_identity
        from check_upstream_health import GENERATOR
        self.entry['children'] = [{'id': 'sample', 'path': 'skills/sample', 'version': '1.0.0'}]
        self.metadata['spec'] = {'collection': {'children': [{'identity': {'id':'sample'}, 'path':'skills/sample'}]}}
        self.write('skills/another/LICENSE', self.mit)
        self.write('skills/another/SKILL.md', '---\nname: another\ndescription: New member\nversion: 0.1.0\n---\n')
        new = self.commit()
        fm = GENERATOR.skill_frontmatter(self.repo, 'skills/another/SKILL.md', new)
        discovered = [child['path'] for child in GENERATOR.discover_children(self.repo, new)]
        digest = frontmatter_identity(fm)
        cases = [
            {'schemaVersion': 1, 'acceptedCollectionPaths': ['skills/sample'], 'acceptedFrontmatterSha256': {'skills/another': digest}},
            {'schemaVersion': 1, 'acceptedCollectionPaths': discovered + ['skills/extra'], 'acceptedFrontmatterSha256': {'skills/another': digest}},
            {'schemaVersion': 1, 'acceptedCollectionPaths': discovered, 'acceptedFrontmatterSha256': {'skills/another': 'a' * 64}},
            {'schemaVersion': 1, 'acceptedCollectionPaths': discovered},
        ]
        for review in cases:
            with self.subTest(review=review):
                with self.assertRaisesRegex(AuditBlocked, '合集成员|结构化声明'):
                    audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z', special_review=review)

    def test_special_review_accepts_root_notice_change(self):
        from audit_skill_update import root_evidence
        self.write('NOTICE', 'old notice\n')
        self.write('skills/sample/README.md', 'old notice\n')
        self.old = self.commit()
        self.entry['source']['ref'] = self.old
        self.metadata['provenance']['content']['ref'] = self.old
        self.metadata['governance']['compliance']['reviewedRef'] = self.old
        self.write('NOTICE', 'new notice documenting a font license\n')
        self.write('skills/sample/README.md', 'new notice documenting a font license\n')
        new = self.commit()
        with self.assertRaisesRegex(AuditBlocked, '许可证|Notice'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z')
        digest = root_evidence(self.repo, new)['NOTICE']
        with self.assertRaisesRegex(AuditBlocked, '许可证|Notice'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z',
                            special_review={'schemaVersion': 1, 'acceptedRootEvidenceSha256': {'NOTICE': 'b' * 64}})
        _, _, report = audit_snapshots(
            self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z',
            special_review={'schemaVersion': 1, 'acceptedRootEvidenceSha256': {'NOTICE': digest}})
        self.assertEqual(report['licenseEvidenceSha256']['NOTICE'], digest)

    def test_deleted_root_license_is_not_accepted(self):
        (self.repo / 'LICENSE').unlink()
        new = self.commit()
        reviews = [
            {'schemaVersion': 1, 'acceptedRootEvidenceSha256': {}},
            {'schemaVersion': 1},
        ]
        for review in reviews:
            with self.subTest(review=review):
                with self.assertRaisesRegex(AuditBlocked, '许可证|Notice'):
                    audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z', special_review=review)


    def _scoped_notice_review(self, old, new, path, previous, current, **overrides):
        review = {
            'schemaVersion': 1,
            'reviewedBy': 'mashagua',
            'reviewedAt': '2026-11-22',
            'notes': 'Accept an additive nested NOTICE that retains prior attribution.',
            'acceptedScopedNotice': {
                'fromRef': old,
                'toRef': new,
                'files': [{'path': path, 'previousSha256': previous, 'sha256': current}],
            },
        }
        review.update(overrides)
        return review

    def test_special_review_accepts_additive_scoped_notice(self):
        import hashlib
        path = 'skills/sample/NOTICE'
        old_text = 'retained vendor attribution\n'
        new_text = old_text + 'appended Unicode-3.0 notice\n'
        self.write(path, old_text)
        self.old = self.commit()
        self.entry['source']['ref'] = self.old
        self.metadata['provenance']['content']['ref'] = self.old
        self.metadata['governance']['compliance']['reviewedRef'] = self.old
        self.write(path, new_text)
        new = self.commit()
        previous = hashlib.sha256(old_text.encode()).hexdigest()
        digest = hashlib.sha256(new_text.encode()).hexdigest()
        with self.assertRaisesRegex(AuditBlocked, '许可证|Notice'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z')
        _, _, report = audit_snapshots(
            self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z',
            special_review=self._scoped_notice_review(self.old, new, path, previous, digest))
        self.assertEqual(report['licenseEvidenceSha256'][path], digest)
        self.assertTrue(any('安装范围内的 Notice' in item for item in report['limitations']))

    def test_special_review_rejects_invalid_scoped_notice_changes(self):
        import hashlib
        path = 'skills/sample/NOTICE'
        old_text = 'retained vendor attribution\n'
        new_text = old_text + 'appended Unicode-3.0 notice\n'
        rewrite = 'completely replaced notice, attribution dropped\n'
        self.write(path, old_text)
        self.old = self.commit()
        self.entry['source']['ref'] = self.old
        self.metadata['provenance']['content']['ref'] = self.old
        self.metadata['governance']['compliance']['reviewedRef'] = self.old
        previous = hashlib.sha256(old_text.encode()).hexdigest()

        # Rewrite that drops existing attribution, even with matching hashes.
        self.write(path, rewrite)
        rewritten = self.commit()
        rewrite_digest = hashlib.sha256(rewrite.encode()).hexdigest()
        with self.assertRaisesRegex(AuditBlocked, '未保留原有声明'):
            audit_snapshots(
                self.repo, self.entry, self.metadata, {'ref': self.old, 'head': rewritten}, '2026-10-31T01:02:03Z',
                special_review=self._scoped_notice_review(self.old, rewritten, path, previous, rewrite_digest))

        self.run_git('reset', '--hard', self.old); self.run_git('clean', '-fd')
        self.write(path, new_text)
        new = self.commit()
        digest = hashlib.sha256(new_text.encode()).hexdigest()
        valid = self._scoped_notice_review(self.old, new, path, previous, digest)
        cases = [
            ('哈希不匹配', self._scoped_notice_review(self.old, new, path, previous, 'ab' * 32)),
            ('哈希不匹配', self._scoped_notice_review(self.old, new, path, 'cd' * 32, digest)),
            ('未绑定当前固定快照', self._scoped_notice_review('a' * 40, new, path, previous, digest)),
            ('未绑定当前固定快照', self._scoped_notice_review(self.old, 'b' * 40, path, previous, digest)),
            ('必须包含审核人、日期和理由', {**valid, 'reviewedBy': '  '}),
            ('必须包含审核人、日期和理由', {k: v for k, v in valid.items() if k != 'notes'}),
            ('与实际变更文件不一致', {**valid, 'acceptedScopedNotice': {
                'fromRef': self.old, 'toRef': new,
                'files': [
                    {'path': path, 'previousSha256': previous, 'sha256': digest},
                    {'path': 'skills/sample/extra/NOTICE', 'previousSha256': previous, 'sha256': digest},
                ],
            }}),
            ('路径不安全', {**valid, 'acceptedScopedNotice': {
                'fromRef': self.old, 'toRef': new,
                'files': [{'path': 'skills/*/NOTICE', 'previousSha256': previous, 'sha256': digest}],
            }}),
            ('路径不安全', {**valid, 'acceptedScopedNotice': {
                'fromRef': self.old, 'toRef': new,
                'files': [{'path': '../NOTICE', 'previousSha256': previous, 'sha256': digest}],
            }}),
        ]
        for pattern, review in cases:
            with self.subTest(pattern=pattern):
                with self.assertRaisesRegex(AuditBlocked, pattern):
                    audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
                                    '2026-10-31T01:02:03Z', special_review=review)

    def test_special_review_cannot_accept_scoped_license_or_notice_deletion(self):
        import hashlib
        license_path = 'skills/sample/vendor/LICENSE'
        notice_path = 'skills/sample/NOTICE'
        old_license = 'old vendor terms\n'
        new_license = 'new vendor terms\n'
        old_notice = 'retained vendor attribution\n'
        new_notice = old_notice + 'appended note\n'
        self.write(license_path, old_license)
        self.write(notice_path, old_notice)
        self.old = self.commit()
        self.entry['source']['ref'] = self.old
        self.metadata['provenance']['content']['ref'] = self.old
        self.metadata['governance']['compliance']['reviewedRef'] = self.old

        self.write(license_path, new_license)
        new = self.commit()
        review = self._scoped_notice_review(
            self.old, new, license_path,
            hashlib.sha256(old_license.encode()).hexdigest(),
            hashlib.sha256(new_license.encode()).hexdigest())
        with self.assertRaisesRegex(AuditBlocked, '许可证|Notice|不能用于接受嵌套许可证'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
                            '2026-10-31T01:02:03Z', special_review=review)

        self.run_git('reset', '--hard', self.old); self.run_git('clean', '-fd')
        (self.repo / notice_path).unlink()
        deleted = self.commit()
        previous = hashlib.sha256(old_notice.encode()).hexdigest()
        with self.assertRaisesRegex(AuditBlocked, '许可证|Notice'):
            audit_snapshots(
                self.repo, self.entry, self.metadata, {'ref': self.old, 'head': deleted}, '2026-10-31T01:02:03Z',
                special_review=self._scoped_notice_review(self.old, deleted, notice_path, previous, previous))

        self.run_git('reset', '--hard', self.old); self.run_git('clean', '-fd')
        (self.repo / notice_path).unlink()
        self.write('skills/sample/docs/NOTICE', new_notice)
        renamed = self.commit()
        with self.assertRaisesRegex(AuditBlocked, '许可证|Notice'):
            audit_snapshots(
                self.repo, self.entry, self.metadata, {'ref': self.old, 'head': renamed}, '2026-10-31T01:02:03Z',
                special_review=self._scoped_notice_review(
                    self.old, renamed, 'skills/sample/docs/NOTICE',
                    hashlib.sha256(old_notice.encode()).hexdigest(),
                    hashlib.sha256(new_notice.encode()).hexdigest()))

    def test_exclude_paths_still_cannot_hide_scoped_notice(self):
        path = 'skills/sample/NOTICE'
        self.write(path, 'old notice\n')
        self.old = self.commit()
        self.entry['source']['ref'] = self.old
        self.metadata['provenance']['content']['ref'] = self.old
        self.metadata['governance']['compliance']['reviewedRef'] = self.old
        self.write(path, 'old notice\nappended\n')
        new = self.commit()
        review = {'schemaVersion': 1, 'excludePaths': [path], 'reviewedBy': 'mashagua',
                  'reviewedAt': '2026-11-22', 'notes': 'should not hide NOTICE'}
        with self.assertRaisesRegex(AuditBlocked, '排除列表'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
                            '2026-10-31T01:02:03Z', special_review=review)

    def test_symlink_scoped_notice_is_blocked_even_with_review(self):
        path = 'skills/sample/NOTICE'
        self.write(path, 'retained vendor attribution\n')
        self.old = self.commit()
        self.entry['source']['ref'] = self.old
        self.metadata['provenance']['content']['ref'] = self.old
        self.metadata['governance']['compliance']['reviewedRef'] = self.old
        (self.repo / path).unlink()
        (self.repo / path).symlink_to('SKILL.md')
        new = self.commit()
        review = self._scoped_notice_review(self.old, new, path, 'ab' * 32, 'cd' * 32)
        with self.assertRaisesRegex(AuditBlocked, '符号链接'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
                            '2026-10-31T01:02:03Z', special_review=review)

    def test_special_review_rejects_partial_or_new_file_scoped_notice(self):
        import hashlib
        first = 'skills/sample/NOTICE'
        second = 'skills/sample/docs/NOTICE'
        old_first = 'retained first attribution\n'
        new_first = old_first + 'appended first\n'
        old_second = 'retained second attribution\n'
        new_second = old_second + 'appended second\n'
        self.write(first, old_first)
        self.write(second, old_second)
        self.old = self.commit()
        self.entry['source']['ref'] = self.old
        self.metadata['provenance']['content']['ref'] = self.old
        self.metadata['governance']['compliance']['reviewedRef'] = self.old
        self.write(first, new_first)
        self.write(second, new_second)
        new = self.commit()
        review = self._scoped_notice_review(
            self.old, new, first,
            hashlib.sha256(old_first.encode()).hexdigest(),
            hashlib.sha256(new_first.encode()).hexdigest())
        with self.assertRaisesRegex(AuditBlocked, '与实际变更文件不一致'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
                            '2026-10-31T01:02:03Z', special_review=review)

        self.run_git('reset', '--hard', self.old); self.run_git('clean', '-fd')
        created = 'skills/sample/vendor/NOTICE'
        created_text = 'brand new notice\n'
        self.write(created, created_text)
        created_ref = self.commit()
        with self.assertRaisesRegex(AuditBlocked, '许可证|Notice'):
            audit_snapshots(
                self.repo, self.entry, self.metadata, {'ref': self.old, 'head': created_ref}, '2026-10-31T01:02:03Z',
                special_review=self._scoped_notice_review(
                    self.old, created_ref, created,
                    hashlib.sha256(b'').hexdigest(),
                    hashlib.sha256(created_text.encode()).hexdigest()))

    def test_special_review_rejects_prepended_scoped_notice(self):
        import hashlib
        path = 'skills/sample/NOTICE'
        old_text = 'retained vendor attribution\n'
        prepended = 'new preface\n' + old_text
        self.write(path, old_text)
        self.old = self.commit()
        self.entry['source']['ref'] = self.old
        self.metadata['provenance']['content']['ref'] = self.old
        self.metadata['governance']['compliance']['reviewedRef'] = self.old
        self.write(path, prepended)
        new = self.commit()
        with self.assertRaisesRegex(AuditBlocked, '未保留原有声明'):
            audit_snapshots(
                self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z',
                special_review=self._scoped_notice_review(
                    self.old, new, path,
                    hashlib.sha256(old_text.encode()).hexdigest(),
                    hashlib.sha256(prepended.encode()).hexdigest()))


    def _rebind_old(self, sha):
        self.old = sha
        self.entry['source']['ref'] = sha
        self.metadata['provenance']['content']['ref'] = sha
        self.metadata['governance']['compliance']['reviewedRef'] = sha

    def _client_attach_review(self, new, scopes, notice_sha, **overrides):
        review = {
            'schemaVersion': 1,
            'reviewedBy': 'mashagua',
            'reviewedAt': '2026-11-27',
            'notes': 'Install-copy readback of verified client root-notice attach for this pin.',
            'acceptedClientAttachedNotices': {
                'sourceRef': new,
                'clientCommit': '28128a15b3abd76e1529b983ca8a921bdfe9ff30',
                'clientTree': 'e8c1321e6a098eb905f4646b2027bc7b2259ca6b',
                'observedAt': '2026-11-26T16:04:23Z',
                'noticeRootPath': 'LICENSE',
                'noticeSha256': notice_sha,
                'scopes': [
                    {'path': path, 'attached': [
                        {'name': 'LICENSE', 'sourceName': 'LICENSE', 'sha256': notice_sha},
                    ]}
                    for path in scopes
                ],
            },
        }
        accepted = overrides.pop('acceptedClientAttachedNotices', None)
        review.update(overrides)
        if accepted is not None:
            merged = dict(review['acceptedClientAttachedNotices'])
            merged.update(accepted)
            review['acceptedClientAttachedNotices'] = merged
        return review


    def test_root_licenses_directory_is_not_a_broken_license_file(self):
        """A normal licenses/ directory plus an unchanged MIT LICENSE must pass (old and new pins)."""
        self.write('licenses/thirdparty-MIT.txt', 'Permission is hereby granted, MIT third-party text.\n')
        self._rebind_old(self.commit())
        # Unchanged directory already present on the admitted old pin should not block a script change.
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        entry, metadata, report = self.audit()
        self.assertEqual(entry['source']['ref'], metadata['governance']['compliance']['reviewedRef'])
        self.assertTrue(report['checks']['licenseAndNoticeUnchanged'])
        self.assertIn('LICENSE', report['licenseEvidenceSha256'])
        self.assertIn('licenses/thirdparty-MIT.txt', report['licenseEvidenceSha256'])

    def test_root_license_symlink_or_nonregular_still_blocked(self):
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        (self.repo / 'LICENSE').unlink()
        (self.repo / 'LICENSE').symlink_to('skills/sample/SKILL.md')
        with self.assertRaisesRegex(AuditBlocked, '根许可或 Notice 不是普通文件'):
            self.audit()
        self.run_git('reset', '--hard', self.old)
        self.run_git('clean', '-fd')
        self.write('licenses/thirdparty-MIT.txt', 'MIT third-party text\n')
        self._rebind_old(self.commit())
        (self.repo / 'licenses' / 'alias').symlink_to('thirdparty-MIT.txt')
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        with self.assertRaisesRegex(AuditBlocked, '根许可或 Notice 不是普通文件'):
            self.audit()

    def test_root_license_file_content_change_still_detected(self):
        self.write('licenses/thirdparty-MIT.txt', 'MIT third-party text\n')
        self._rebind_old(self.commit())
        self.write('LICENSE', 'different terms, no longer the admitted MIT text\n')
        with self.assertRaisesRegex(AuditBlocked, '许可证|Notice'):
            self.audit()

    def test_root_license_directory_changes_are_not_claimed_unchanged(self):
        from audit_skill_update import license_directory_manifest_sha256, root_license_directory_files
        self.write('licenses/ghidra-12.1.4.txt', 'Ghidra license text\n')
        self._rebind_old(self.commit())
        (self.repo / 'licenses' / 'ghidra-12.1.4.txt').unlink()
        self.write('licenses/ghidra-12.2.txt', 'Ghidra license text\n')
        self.write('licenses/microsoft-uf2-MIT.txt', 'UF2 MIT notice\n')
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        new = self.commit()
        with self.assertRaisesRegex(AuditBlocked, '根许可目录内的第三方许可文本有变化'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z')
        digest = license_directory_manifest_sha256(root_license_directory_files(self.repo, new)['licenses'])
        with self.assertRaisesRegex(AuditBlocked, '根许可目录专项复核必须包含审核人、日期和理由'):
            audit_snapshots(
                self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z',
                special_review={'schemaVersion': 1, 'acceptedRootLicenseDirectoryManifestSha256': {'licenses': digest}})
        with self.assertRaisesRegex(AuditBlocked, '根许可目录内的第三方许可文本有变化'):
            audit_snapshots(
                self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z',
                special_review={
                    'schemaVersion': 1,
                    'reviewedBy': 'mashagua',
                    'reviewedAt': '2026-11-22',
                    'notes': 'wrong digest must not pass',
                    'acceptedRootLicenseDirectoryManifestSha256': {'licenses': 'b' * 64},
                })
        entry, metadata, report = audit_snapshots(
            self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z',
            special_review={
                'schemaVersion': 1,
                'reviewedBy': 'mashagua',
                'reviewedAt': '2026-11-22',
                'notes': 'Reviewed ghidra 12.1.4 to 12.2 rename with identical text and the added UF2 MIT notice.',
                'acceptedRootLicenseDirectoryManifestSha256': {'licenses': digest},
            })
        self.assertEqual(report['licenseEvidenceSha256']['licenses/ghidra-12.2.txt'],
                         __import__('hashlib').sha256(b'Ghidra license text\n').hexdigest())
        self.assertNotIn('licenses/ghidra-12.1.4.txt', report['licenseEvidenceSha256'])
        self.assertIn('licenses/microsoft-uf2-MIT.txt', report['licenseEvidenceSha256'])
        self.assertTrue(any('许可目录' in item for item in report['limitations']))
        self.assertEqual(metadata['governance']['compliance']['reviewedRef'], entry['source']['ref'])

    def test_deleted_root_license_directory_is_not_accepted(self):
        self.write('licenses/thirdparty-MIT.txt', 'MIT third-party text\n')
        self._rebind_old(self.commit())
        (self.repo / 'licenses' / 'thirdparty-MIT.txt').unlink()
        (self.repo / 'licenses').rmdir()
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        with self.assertRaisesRegex(AuditBlocked, '根许可目录被删除'):
            self.audit()

    def test_scoped_notice_append_still_works_with_licenses_directory(self):
        import hashlib
        self.write('licenses/thirdparty-MIT.txt', 'MIT third-party text\n')
        path = 'skills/sample/NOTICE'
        old_text = 'retained vendor attribution\n'
        new_text = old_text + 'appended Unicode-3.0 notice\n'
        self.write(path, old_text)
        self._rebind_old(self.commit())
        self.write(path, new_text)
        new = self.commit()
        previous = hashlib.sha256(old_text.encode()).hexdigest()
        digest = hashlib.sha256(new_text.encode()).hexdigest()
        _, _, report = audit_snapshots(
            self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z',
            special_review=self._scoped_notice_review(self.old, new, path, previous, digest))
        self.assertEqual(report['licenseEvidenceSha256'][path], digest)
        self.assertIn('licenses/thirdparty-MIT.txt', report['licenseEvidenceSha256'])
        self.assertTrue(any('安装范围内的 Notice' in item for item in report['limitations']))


    def test_client_attached_notices_accepts_bound_install_readback(self):
        from jsonschema import Draft7Validator
        schema = json.loads((Path(__file__).resolve().parents[2] / 'schemas' / 'special-review.v1.schema.json').read_text())
        (self.repo / 'skills/sample/LICENSE').unlink()
        self._rebind_old(self.commit())
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        notice_sha = hashlib.sha256((self.repo / 'LICENSE').read_bytes()).hexdigest()
        new = self.commit()
        review = self._client_attach_review(new, ['skills/sample'], notice_sha)
        Draft7Validator(schema).validate(review)
        entry, metadata, report = audit_snapshots(
            self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z',
            special_review=review)
        self.assertEqual(metadata['governance']['compliance']['reviewedRef'], new)
        self.assertEqual(report['source']['ref'], new)
        self.assertEqual(report['source']['previousRef'], self.old)
        self.assertTrue(any('安装副本携带了完整根通知' in item for item in report['limitations']))

    def test_client_attached_notices_rejects_mismatched_bindings(self):
        (self.repo / 'skills/sample/LICENSE').unlink()
        self._rebind_old(self.commit())
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        notice_sha = hashlib.sha256((self.repo / 'LICENSE').read_bytes()).hexdigest()
        new = self.commit()
        valid = self._client_attach_review(new, ['skills/sample'], notice_sha)
        cases = [
            ('未绑定当前固定快照', {'acceptedClientAttachedNotices': {'sourceRef': self.old}}),
            ('未绑定当前固定快照', {'acceptedClientAttachedNotices': {'sourceRef': 'a' * 40}}),
            ('不在已核验实现清单中', {'acceptedClientAttachedNotices': {'clientCommit': 'a' * 40}}),
            ('客户端提交无效', {'acceptedClientAttachedNotices': {'clientCommit': '28128a15'}}),
            ('客户端 tree 与已核验实现不一致', {'acceptedClientAttachedNotices': {'clientTree': 'a' * 40}}),
            ('根通知哈希与当前快照不一致', {'acceptedClientAttachedNotices': {'noticeSha256': 'b' * 64}}),
            ('缺少子项安装回读', {'acceptedClientAttachedNotices': {'scopes': []}}),
            ('必须包含审核人、日期和理由', {'notes': ''}),
            ('必须包含审核人、日期和理由', {'reviewedBy': ''}),
        ]
        for message, overrides in cases:
            with self.subTest(overrides=overrides):
                review = self._client_attach_review(new, ['skills/sample'], notice_sha, **overrides)
                with self.assertRaisesRegex(AuditBlocked, message):
                    audit_snapshots(self.repo, self.entry, self.metadata,
                                    {'ref': self.old, 'head': new}, '2026-10-31T01:02:03Z',
                                    special_review=review)

    def test_client_attached_notices_rejects_missing_child_readback(self):
        self.write('skills/another/SKILL.md', '---\nname: another\ndescription: Fixture\nversion: 1.0.0\n---\n')
        (self.repo / 'skills/sample/LICENSE').unlink()
        (self.repo / 'skills/another/LICENSE').unlink()
        self.entry['children'] = [
            {'id': 'sample', 'path': 'skills/sample', 'version': '1.0.0'},
            {'id': 'another', 'path': 'skills/another', 'version': '1.0.0'},
        ]
        self.metadata['spec'] = {'collection': {'children': [
            {'identity': {'id': 'sample'}, 'path': 'skills/sample',
             'release': {'state': 'known', 'version': '1.0.0', 'versionScheme': 'semver'}},
            {'identity': {'id': 'another'}, 'path': 'skills/another',
             'release': {'state': 'known', 'version': '1.0.0', 'versionScheme': 'semver'}},
        ]}}
        self._rebind_old(self.commit())
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        notice_sha = hashlib.sha256((self.repo / 'LICENSE').read_bytes()).hexdigest()
        new = self.commit()
        complete = self._client_attach_review(new, ['skills/sample', 'skills/another'], notice_sha)
        audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
                        '2026-10-31T01:02:03Z', special_review=complete)
        partial = self._client_attach_review(new, ['skills/sample'], notice_sha)
        with self.assertRaisesRegex(AuditBlocked, '缺少子项安装回读|与安装范围不一致'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
                            '2026-10-31T01:02:03Z', special_review=partial)

    def test_client_attached_notices_cannot_excuse_incomplete_mit(self):
        self.write('LICENSE', 'License: MIT\n')
        (self.repo / 'skills/sample/LICENSE').unlink()
        self._rebind_old(self.commit())
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        notice_sha = hashlib.sha256((self.repo / 'LICENSE').read_bytes()).hexdigest()
        new = self.commit()
        review = self._client_attach_review(new, ['skills/sample'], notice_sha)
        with self.assertRaisesRegex(AuditBlocked, '不完整的 MIT 声明|完整版权|pin-bound-license-exception'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
                            '2026-10-31T01:02:03Z', special_review=review)

    def test_notes_without_client_attached_evidence_do_not_pass(self):
        (self.repo / 'skills/sample/LICENSE').unlink()
        self._rebind_old(self.commit())
        self.write('skills/sample/scripts/tool.py', 'print("new fixture")\n')
        with self.assertRaisesRegex(AuditBlocked, 'Installed notices|安装通知'):
            audit_snapshots(
                self.repo, self.entry, self.metadata, {'ref': self.old, 'head': self.commit()},
                '2026-10-31T01:02:03Z',
                special_review={
                    'schemaVersion': 1,
                    'reviewedBy': 'mashagua',
                    'reviewedAt': '2026-11-27',
                    'notes': 'The client will attach the root LICENSE later.',
                })

    def test_disallows_non_github_fetch_targets(self):
        self.entry['source']['repoUrl'] = 'file:///private/source'
        with self.assertRaisesRegex(AuditBlocked, 'HTTPS'): audit_update(self.entry, self.metadata, {})

    def _collection_description_fixture(self, new_description, short_descs, catalog=True):
        self.entry = {
            'id': 'collection',
            'latestVersion': '1.0.0',
            'source': {'kind': 'git', 'repoUrl': 'https://github.com/example/sample.git', 'ref': self.old},
            'children': [{
                'id': 'sample',
                'path': 'skills/sample',
                'version': '1.0.0',
                'i18n': {
                    'zh-CN': {'shortDesc': '旧的中文简介：在单个长会话中统筹子 Agent。'},
                    'en-US': {'shortDesc': 'Acts as a chief of staff in one long session, co-ordinating subagents toward a long-running goal.'},
                },
            }],
        }
        self.metadata['identity'] = {'kind': 'skill', 'id': 'collection'}
        self.metadata['provenance']['content'] = {'kind': 'git', 'url': self.entry['source']['repoUrl'], 'ref': self.old}
        self.metadata['spec'] = {'collection': {'children': [{
            'identity': {'kind': 'skill', 'id': 'sample', 'parentId': 'collection'},
            'path': 'skills/sample',
            'presentation': {'defaultLocale': 'en-US', 'i18n': {
                'en-US': {'name': 'sample', 'summary': self.entry['children'][0]['i18n']['en-US']['shortDesc']},
                'zh-CN': {'name': 'sample', 'summary': self.entry['children'][0]['i18n']['zh-CN']['shortDesc']},
            }, 'tags': []},
            'release': {'state': 'unknown'},
        }]}} if catalog else {'collection': {'children': [{'identity': {'id': 'sample'}, 'path': 'skills/sample'}]}}
        old_text = (self.repo / 'skills/sample/SKILL.md').read_text()
        self.write('skills/sample/SKILL.md', old_text.replace('description: Fixture', f'description: {new_description}'))
        self.entry['children'][0]['i18n']['en-US']['shortDesc'] = short_descs['en-US']
        self.entry['children'][0]['i18n']['zh-CN']['shortDesc'] = short_descs['zh-CN']
        if catalog:
            i18n = self.metadata['spec']['collection']['children'][0]['presentation']['i18n']
            i18n['en-US']['summary'] = short_descs['en-US']
            i18n['zh-CN']['summary'] = short_descs['zh-CN']
        new = self.commit()
        return new, GENERATOR.skill_frontmatter(self.repo, 'skills/sample/SKILL.md', new)

    def _description_review(self, new, fm, short_descs, **overrides):
        from audit_skill_update import frontmatter_identity, _text_sha256
        accepted = {
            'fromRef': self.old,
            'toRef': new,
            'files': [{
                'path': 'skills/sample',
                'oldDescription': 'Fixture',
                'newDescription': fm['description'],
                'newFrontmatterSha256': frontmatter_identity(fm),
                'locales': {
                    locale: {
                        'shortDesc': text,
                        'sha256': _text_sha256(text),
                        'previousShortDesc': {
                            'en-US': 'Acts as a chief of staff in one long session, co-ordinating subagents toward a long-running goal.',
                            'zh-CN': '旧的中文简介：在单个长会话中统筹子 Agent。',
                        }[locale],
                    }
                    for locale, text in short_descs.items()
                },
            }],
        }
        accepted.update(overrides)
        return {
            'schemaVersion': 1,
            'reviewedBy': 'mashagua',
            'reviewedAt': '2026-11-27',
            'notes': 'Reviewed bilingual listing copy against the new upstream description for this pin.',
            'acceptedFrontmatterSha256': {'skills/sample': frontmatter_identity(fm)},
            'acceptedDescriptionAndLocales': accepted,
        }

    def test_description_and_locales_accepts_updated_short_desc(self):
        new_description = 'Delegate the work to fresh subagents and remember what it taught you in a dated wiki, so the next session picks up the thread.'
        short_descs = {
            'en-US': 'Delegates work to fresh-context background subagents and records dated knowledge in an agreed wiki for later sessions.',
            'zh-CN': '将工作委派给新上下文后台子 Agent，并把有日期的知识写入约定 wiki，供后续会话续接。',
        }
        new, fm = self._collection_description_fixture(new_description, short_descs)
        entry, metadata, report = audit_snapshots(
            self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
            '2026-10-31T01:02:03Z', special_review=self._description_review(new, fm, short_descs))
        self.assertEqual(entry['source']['ref'], new)
        self.assertEqual(metadata['governance']['compliance']['reviewedRef'], new)
        self.assertTrue(any('双语简介' in item or '简介' in item for item in report['limitations']))

    def test_description_and_locales_rejects_mismatched_bindings(self):
        new_description = 'Delegate the work to fresh subagents and remember what it taught you in a dated wiki, so the next session picks up the thread.'
        short_descs = {
            'en-US': 'Delegates work to fresh-context background subagents and records dated knowledge in an agreed wiki for later sessions.',
            'zh-CN': '将工作委派给新上下文后台子 Agent，并把有日期的知识写入约定 wiki，供后续会话续接。',
        }
        new, fm = self._collection_description_fixture(new_description, short_descs)
        review = self._description_review(new, fm, short_descs)
        variants = [
            ('未绑定当前固定快照', {'toRef': self.old}),
            ('未绑定当前固定快照', {'fromRef': new}),
            ('路径与上游简介变化范围不一致', {'files': [{**review['acceptedDescriptionAndLocales']['files'][0], 'path': 'skills/missing'}]}),
        ]
        for message, override in variants:
            with self.subTest(message):
                broken = self._description_review(new, fm, short_descs, **override)
                with self.assertRaisesRegex(AuditBlocked, message):
                    audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
                                    '2026-10-31T01:02:03Z', special_review=broken)

    def test_description_and_locales_rejects_stale_or_unmatched_short_desc(self):
        new_description = 'Delegate the work to fresh subagents and remember what it taught you in a dated wiki, so the next session picks up the thread.'
        stale = {
            'en-US': 'Acts as a chief of staff in one long session, co-ordinating subagents toward a long-running goal.',
            'zh-CN': '将工作委派给新上下文后台子 Agent，并把有日期的知识写入约定 wiki，供后续会话续接。',
        }
        new, fm = self._collection_description_fixture(new_description, stale)
        with self.assertRaisesRegex(AuditBlocked, '未相对原先文案更新|未实际更新以匹配上游简介'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
                            '2026-10-31T01:02:03Z', special_review=self._description_review(new, fm, stale))
        self.run_git('reset', '--hard', self.old)
        self.run_git('clean', '-fd')
        unmatched = {
            'en-US': 'A completely unrelated listing about typography and typographic color palettes.',
            'zh-CN': '将工作委派给新上下文后台子 Agent，并把有日期的知识写入约定 wiki，供后续会话续接。',
        }
        new, fm = self._collection_description_fixture(new_description, unmatched)
        with self.assertRaisesRegex(AuditBlocked, '未实际更新以匹配上游简介'):
            audit_snapshots(self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
                            '2026-10-31T01:02:03Z', special_review=self._description_review(new, fm, unmatched))

    def test_notes_without_description_locale_evidence_do_not_pass(self):
        new_description = 'Delegate the work to fresh subagents and remember what it taught you in a dated wiki, so the next session picks up the thread.'
        short_descs = {
            'en-US': 'Delegates work to fresh-context background subagents and records dated knowledge in an agreed wiki for later sessions.',
            'zh-CN': '将工作委派给新上下文后台子 Agent，并把有日期的知识写入约定 wiki，供后续会话续接。',
        }
        new, fm = self._collection_description_fixture(new_description, short_descs)
        from audit_skill_update import frontmatter_identity
        with self.assertRaisesRegex(AuditBlocked, 'description-and-locales|简介|manual_review|安装通知|元数据'):
            audit_snapshots(
                self.repo, self.entry, self.metadata, {'ref': self.old, 'head': new},
                '2026-10-31T01:02:03Z',
                special_review={
                    'schemaVersion': 1,
                    'reviewedBy': 'mashagua',
                    'reviewedAt': '2026-11-27',
                    'notes': 'The bilingual shortDesc was reviewed.',
                    'acceptedFrontmatterSha256': {'skills/sample': frontmatter_identity(fm)},
                })



if __name__ == '__main__': unittest.main()
