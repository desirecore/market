#!/usr/bin/env python3
"""新版 Skill 的有界来源、许可与结构化元数据核验；不执行上游代码。"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from check_upstream_health import GENERATOR
from automated_review import REVIEWER, validate_record
MAX_FILE_BYTES = 1024 * 1024
MAX_CONTENT_BYTES = 50 * 1024 * 1024
MAX_FILES = 2000
DEPENDENCY_NAMES = {'package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock',
                    'pyproject.toml', 'poetry.lock', 'uv.lock', 'pipfile', 'pipfile.lock',
                    'cargo.toml', 'cargo.lock', 'go.mod', 'go.sum', 'gemfile', 'gemfile.lock',
                    'environment.yml', 'dockerfile', 'compose.yml', 'docker-compose.yml'}


class AuditBlocked(ValueError):
    """可解释的自动核验阻碍，不能因此补写成功回执。"""


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', *args], cwd=repo,
                            capture_output=True, timeout=180)
    if result.returncode:
        raise AuditBlocked('无法读取固定 Git 快照')
    return result.stdout


def safe_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or '\\' in value or value.startswith('-'):
        raise AuditBlocked('来源或许可路径不安全')
    return '' if str(path) == '.' else str(path)


def tree(repo: Path, ref: str, path: str = '') -> dict[str, tuple[str, str, int]]:
    records = git(repo, 'ls-tree', '-rlz', ref, '--', path or '.').split(b'\0')
    result = {}
    for record in records:
        if not record:
            continue
        meta, filename = record.split(b'\t', 1)
        mode, kind, oid, size = meta.decode().split()
        name = filename.decode('utf-8')
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise AuditBlocked('来源包含符号链接、子模块或不支持的节点')
        if int(size) > MAX_FILE_BYTES:
            raise AuditBlocked('单文件超过自动审核预算')
        result[name] = (mode, oid, int(size))
    if len(result) > MAX_FILES or sum(item[2] for item in result.values()) > MAX_CONTENT_BYTES:
        raise AuditBlocked('来源超过自动审核内容预算')
    return result


def blob(repo: Path, ref: str, path: str) -> bytes:
    path = safe_path(path)
    size = int(git(repo, 'cat-file', '-s', f'{ref}:{path}'))
    if size > MAX_FILE_BYTES:
        raise AuditBlocked('证据文件超过自动审核预算')
    return git(repo, 'show', f'{ref}:{path}')


def root_evidence(repo: Path, ref: str) -> dict[str, str]:
    # 只读根目录，避免整个上游仓库的无关文件消耗预算。
    result = {}
    for record in git(repo, 'ls-tree', '-z', ref).split(b'\0'):
        if not record:
            continue
        meta, name = record.split(b'\t', 1)
        path = name.decode()
        if not path.upper().startswith(('LICENSE', 'NOTICE', 'COPYING')):
            continue
        mode, kind, _ = meta.decode().split()
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise AuditBlocked('根许可或 Notice 不是普通文件')
        result[path] = hashlib.sha256(blob(repo, ref, path)).hexdigest()
    return result


def stable_frontmatter(fm: dict) -> dict:
    result = copy.deepcopy(fm)
    for key in ('version', 'updated_at'):
        result.pop(key, None)
    if isinstance(result.get('metadata'), dict):
        for key in ('version', 'updated_at'):
            result['metadata'].pop(key, None)
    return result


def dependency_file(path: str) -> bool:
    name = PurePosixPath(path).name.lower()
    return name in DEPENDENCY_NAMES or (name.startswith('requirements') and name.endswith('.txt'))



def dependency_identity(repo: Path, ref: str, path: str, record):
    if PurePosixPath(path).name.lower() == 'package.json':
        try:
            manifest = json.loads(blob(repo, ref, path))
        except (ValueError, UnicodeError) as error:
            raise AuditBlocked('package.json 无法可靠解析') from error
        if not isinstance(manifest, dict):
            raise AuditBlocked('package.json 不是对象')
        # 包版本的正常递增不是新增依赖；其余字段（尤其 dependencies/scripts/license）仍完整比较。
        manifest.pop('version', None)
        return record[0], hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    return record[:2]


def audit_snapshots(repo: Path, entry: dict, sidecar: dict, result: dict,
                    observed_at: str | None = None) -> tuple[dict, dict, dict]:
    old, new = result['ref'], result['head']
    if not all(re.fullmatch('[0-9a-f]{40}', ref) for ref in (old, new)):
        raise AuditBlocked('审核必须绑定完整 SHA')
    source = entry.get('source', {})
    content = sidecar.get('provenance', {}).get('content', {})
    if (source.get('kind') != 'git' or source.get('ref') != old or content.get('ref') != old
            or content.get('url') != source.get('repoUrl') or old == new):
        raise AuditBlocked('来源、provenance 与待审固定快照不一致')
    governance = sidecar.get('governance', {})
    compliance = governance.get('compliance', {})
    if (governance.get('availability') != 'installable'
            or governance.get('license', {}).get('state') != 'known'
            or compliance.get('reviewedRef') != old
            or not compliance.get('reviewedBy') or not compliance.get('reviewedAt')):
        raise AuditBlocked('旧快照缺少可继承的许可与准入证据')
    now = observed_at or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', now):
        raise AuditBlocked('审核时间格式不正确')
    paths = [safe_path(child['path']) for child in entry.get('children', [])]
    if not paths:
        paths = [safe_path(entry['source'].get('path', ''))]
    old_files, new_files = {}, {}
    for path in paths:
        old_files.update(tree(repo, old, path)); new_files.update(tree(repo, new, path))
    if not new_files or len(new_files) > MAX_FILES or sum(item[2] for item in new_files.values()) > MAX_CONTENT_BYTES:
        raise AuditBlocked('新快照为空或超过总预算')
    licenses = root_evidence(repo, old)
    if licenses != root_evidence(repo, new):
        raise AuditBlocked('根许可证或 Notice 有变化，需专项复核')
    # 安装范围内的嵌套许可同样影响再分发，不能只核对根许可证。
    def scoped_evidence(ref, files):
        return {path: hashlib.sha256(blob(repo, ref, path)).hexdigest()
                for path in files if PurePosixPath(path).name.upper().startswith(('LICENSE', 'NOTICE', 'COPYING'))}
    scoped_licenses = scoped_evidence(old, old_files)
    if scoped_licenses != scoped_evidence(new, new_files):
        raise AuditBlocked('安装范围内的许可证或 Notice 有变化，需专项复核')
    licenses.update(scoped_licenses)
    for path in {compliance.get('licenseEvidencePath'), compliance.get('noticePath'),
                 governance.get('license', {}).get('evidencePath')} - {None}:
        old_bytes, new_bytes = blob(repo, old, path), blob(repo, new, path)
        if not old_bytes or old_bytes != new_bytes:
            raise AuditBlocked('声明的许可证或 Notice 变化，需专项复核')
        licenses[path] = hashlib.sha256(new_bytes).hexdigest()
    if not licenses:
        raise AuditBlocked('缺少可重读的许可文件')
    # 依赖清单既检查安装范围，也检查根目录的工具/引擎前置条件。
    for ref, items in ((old, old_files), (new, new_files)):
        for record in git(repo, 'ls-tree', '-z', ref).split(b'\0'):
            if not record:
                continue
            meta, raw_path = record.split(b'\t', 1); path = raw_path.decode()
            if dependency_file(path):
                mode, kind, oid = meta.decode().split()
                if kind != 'blob' or mode not in ('100644', '100755'):
                    raise AuditBlocked('根依赖清单不是普通文件')
                items[path] = (mode, oid, 0)
    old_dependencies = {path: dependency_identity(repo, old, path, value) for path, value in old_files.items() if dependency_file(path)}
    new_dependencies = {path: dependency_identity(repo, new, path, value) for path, value in new_files.items() if dependency_file(path)}
    if old_dependencies != new_dependencies:
        raise AuditBlocked('依赖清单有变化，无法自动确认新的前置条件')
    versions = {}
    for path in paths:
        marker = f'{path}/SKILL.md' if path else 'SKILL.md'
        old_fm = GENERATOR.skill_frontmatter(repo, marker, old)
        new_fm = GENERATOR.skill_frontmatter(repo, marker, new)
        if not isinstance(old_fm, dict) or not isinstance(new_fm, dict):
            raise AuditBlocked('技能 frontmatter 必须是对象')
        if stable_frontmatter(old_fm) != stable_frontmatter(new_fm):
            raise AuditBlocked('名称、简介、依赖、兼容性或其他结构化声明有变化，需同步审核元数据和翻译')
        raw = new_fm.get('version')
        if raw is None and not entry.get('children'):
            details = new_fm.get('metadata')
            raw = details.get('version') if isinstance(details, dict) else None
        if raw is not None:
            if re.search(r'[-+]', str(raw)):
                raise AuditBlocked('预发布或不明确的版本需专项复核')
            version = GENERATOR.normalize_version(raw)
            if not version:
                raise AuditBlocked('上游版本格式无法可靠归一化')
            versions[path] = version
    updated, metadata = copy.deepcopy(entry), copy.deepcopy(sidecar)
    updated['source']['ref'] = new
    metadata['provenance']['content']['ref'] = new
    if updated.get('children'):
        # 新增/移除成员及翻译需要单独处理；不能把一个未审成员混入整包审核。
        discovered = {child['path'] for child in GENERATOR.discover_children(repo, new)}
        if discovered != set(paths):
            raise AuditBlocked('合集成员集合变化，需核对新增/移除成员及翻译')
        for child in updated['children']:
            if child['path'] in versions:
                version = versions[child['path']]
                previous = GENERATOR.normalize_version(child.get('version'))
                if previous and tuple(map(int, version.split('.'))) < tuple(map(int, previous.split('.'))):
                    raise AuditBlocked('拒绝自动回退合集成员版本')
                child['version'] = version
                for child_catalog in metadata.get('spec', {}).get('collection', {}).get('children', []):
                    if child_catalog.get('identity', {}).get('id') == child['id']:
                        child_catalog['release'] = {'state': 'known', 'version': child['version'], 'versionScheme': 'semver'}
    elif paths[0] in versions:
        version = versions[paths[0]]
        previous = GENERATOR.normalize_version(entry.get('latestVersion'))
        if previous and tuple(map(int, version.split('.'))) < tuple(map(int, previous.split('.'))):
            raise AuditBlocked('拒绝自动回退版本')
        updated['latestVersion'] = version
        if metadata.get('release', {}).get('version') != version:
            metadata['release'] = {'state': 'known', 'version': version, 'versionScheme': 'semver'}
            metadata.setdefault('timestamps', {})['releasePublishedAt'] = {'state': 'unknown'}
    compliance = metadata['governance']['compliance']
    compliance.update(reviewedRef=new, reviewedAt=now[:10], reviewedBy=REVIEWER)
    metadata.setdefault('timestamps', {})['reviewedAt'] = {'state': 'known', 'value': now[:10], 'precision': 'day'}
    for key in ('catalogUpdatedAt', 'upstreamObservedAt'):
        metadata['timestamps'][key] = {'state': 'known', 'value': now, 'precision': 'second'}
    report = {'schemaVersion': 1, 'reviewer': REVIEWER, 'reviewedAt': now,
              'source': {'url': entry['source']['repoUrl'], 'previousRef': old, 'ref': new, 'paths': sorted(paths)},
              'checks': {'immutableSnapshots': True, 'installedScopeBoundedFiles': True,
                         'licenseAndNoticeUnchanged': True, 'structuredPrerequisitesUnchanged': True,
                         'presentationMetadataUnchanged': True},
              'licenseEvidenceSha256': licenses, 'observedVersions': versions,
              'contentManifestSha256': hashlib.sha256(json.dumps(new_files, sort_keys=True).encode()).hexdigest(),
              'fileCount': len(new_files),
              'limitations': ['自动来源、许可和结构化元数据核验；不执行上游代码，不代表软件安全认证或真实运行验收。',
                              '未结构化表达的依赖与行为变化仍在 PR 差异中供复核，不据此扩大授权。']}
    errors = validate_record(metadata, report)
    if errors:
        raise AuditBlocked('; '.join(errors))
    return updated, metadata, report


def audit_update(entry: dict, sidecar: dict, result: dict) -> tuple[dict, dict, dict]:
    url = entry['source']['repoUrl']
    if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?', url):
        raise AuditBlocked('自动获取仅使用已登记的 GitHub HTTPS 来源')
    with tempfile.TemporaryDirectory(prefix='skill-audit-') as temporary:
        repo = Path(temporary)
        git(repo, 'init', '--quiet')
        git(repo, 'fetch', '--quiet', '--no-tags', '--depth=1', url, result['ref'], result['head'])
        return audit_snapshots(repo, entry, sidecar, result)
