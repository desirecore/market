#!/usr/bin/env python3
"""新版 Skill 的有界来源、许可与结构化元数据核验；不执行上游代码。"""
from __future__ import annotations

import copy
import fnmatch
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


def tree(repo: Path, ref: str, path: str = '', exclude_paths=(), budget_exempt_paths=()) -> dict[str, tuple[str, str, int]]:
    # Do not use ls-tree -l: in a partial clone it fetches every blob just to read
    # the size, including files we are about to exclude (multi-megabyte demos).
    records = git(repo, 'ls-tree', '-rz', ref, '--', path or '.').split(b'\0')
    result = {}
    for record in records:
        if not record:
            continue
        meta, filename = record.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()[:3]
        name = filename.decode('utf-8')
        if path_matches(name, exclude_paths):
            if protected_audit_path(name):
                raise AuditBlocked('排除列表不能用于许可、Notice 或依赖清单')
            continue
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise AuditBlocked('来源包含符号链接、子模块或不支持的节点')
        size = int(git(repo, 'cat-file', '-s', oid))
        if size > MAX_FILE_BYTES and not path_matches(name, budget_exempt_paths):
            raise AuditBlocked('单文件超过自动审核预算')
        result[name] = (mode, oid, size)
    if len(result) > MAX_FILES or sum(item[2] for item in result.values()) > MAX_CONTENT_BYTES:
        raise AuditBlocked('来源超过自动审核内容预算')
    return result


def blob(repo: Path, ref: str, path: str) -> bytes:
    path = safe_path(path)
    size = int(git(repo, 'cat-file', '-s', f'{ref}:{path}'))
    if size > MAX_FILE_BYTES:
        raise AuditBlocked('证据文件超过自动审核预算')
    return git(repo, 'show', f'{ref}:{path}')


LICENSE_NAME_PREFIXES = ('LICENSE', 'NOTICE', 'COPYING')


def root_evidence(repo: Path, ref: str) -> dict[str, str]:
    # 只读根目录的普通许可文件。名为 licenses/ 的目录不是损坏的 LICENSE 文件。
    result = {}
    for record in git(repo, 'ls-tree', '-z', ref).split(b'\0'):
        if not record:
            continue
        meta, name = record.split(b'\t', 1)
        path = name.decode()
        if not path.upper().startswith(LICENSE_NAME_PREFIXES):
            continue
        mode, kind, _ = meta.decode().split()
        if kind == 'tree' and mode == '040000':
            continue
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise AuditBlocked('根许可或 Notice 不是普通文件')
        result[path] = hashlib.sha256(blob(repo, ref, path)).hexdigest()
    return result


def root_license_directory_files(repo: Path, ref: str) -> dict[str, dict[str, str]]:
    """普通文件清单，按根上 LICENSE*/NOTICE*/COPYING* 目录分组。目录内的符号链接或子模块仍硬拦截。"""
    grouped: dict[str, dict[str, str]] = {}
    for record in git(repo, 'ls-tree', '-z', ref).split(b'\0'):
        if not record:
            continue
        meta, name = record.split(b'\t', 1)
        path = name.decode()
        if not path.upper().startswith(LICENSE_NAME_PREFIXES):
            continue
        mode, kind, _ = meta.decode().split()
        if kind != 'tree' or mode != '040000':
            continue
        files: dict[str, str] = {}
        for child in git(repo, 'ls-tree', '-rz', ref, '--', path).split(b'\0'):
            if not child:
                continue
            cmeta, cname = child.split(b'\t', 1)
            cpath = cname.decode()
            cmode, ckind, _ = cmeta.decode().split()
            if ckind != 'blob' or cmode not in ('100644', '100755'):
                raise AuditBlocked('根许可或 Notice 不是普通文件')
            files[cpath] = hashlib.sha256(blob(repo, ref, cpath)).hexdigest()
        grouped[path] = files
    return grouped


def license_directory_manifest_sha256(files: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


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




def path_matches(name: str, patterns: list[str] | tuple[str, ...] | None) -> bool:
    """Exact path, directory prefix, or fnmatch glob. Patterns are repo-relative."""
    for raw in patterns or ():
        pattern = raw[:-1] if raw.endswith('/') else raw
        if name == pattern or name.startswith(pattern + '/'):
            return True
        if fnmatch.fnmatch(name, raw) or fnmatch.fnmatch(name, pattern):
            return True
    return False


def protected_audit_path(path: str) -> bool:
    name = PurePosixPath(path).name.upper()
    return name.startswith(('LICENSE', 'NOTICE', 'COPYING')) or dependency_file(path)


def frontmatter_identity(fm: dict) -> str:
    return hashlib.sha256(json.dumps(stable_frontmatter(fm), sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def dependency_acceptance_key(identity: tuple) -> str:
    return identity[1]



def evidence_filename(path: str) -> str:
    return PurePosixPath(path).name.upper()


def is_notice_filename(path: str) -> bool:
    return evidence_filename(path).startswith('NOTICE')


def is_license_or_copying_filename(path: str) -> bool:
    return evidence_filename(path).startswith(('LICENSE', 'COPYING'))


def _sha256_hex(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r'[a-f0-9]{64}', value))


# Verified DesireCore client commits whose collection-child installer attaches
# root LICENSE/NOTICE/COPYING files after verifying the selected child tree.
# This is not a license exception. A later descendant tip is not accepted
# automatically; add a newly verified implementation commit explicitly.
CLIENT_COLLECTION_NOTICE_IMPLEMENTATIONS = {
    '28128a15b3abd76e1529b983ca8a921bdfe9ff30': 'e8c1321e6a098eb905f4646b2027bc7b2259ca6b',
}

# desirecore/desirecore#6429 (squashed into dev): the standalone Git-subdirectory
# path copies the exact catalog-evidenced notice and records it in the lock.
# This is source-implementation provenance, not a released-package or install receipt.
CLIENT_STANDALONE_NOTICE_IMPLEMENTATIONS = {
    '85fba4abf4c60c5704557b2c76568a3da3323967': '4e38063a01a6d8b9e7b7fc549bbc2716b7d45a81',
}

ROOT_NOTICE_NAME_PREFIXES = ('LICENSE', 'LICENCE', 'NOTICE', 'COPYING')


def is_root_notice_filename(name: str) -> bool:
    if not isinstance(name, str) or not name or name in ('.', '..'):
        return False
    if name != PurePosixPath(name).name or any(symbol in name for symbol in ('/', '\\', '\0')):
        return False
    upper = name.upper()
    return any(upper == prefix or upper.startswith(prefix + '.') or upper.startswith(prefix + '-')
               for prefix in ROOT_NOTICE_NAME_PREFIXES)


def root_regular_file_sha256(repo: Path, ref: str, path: str) -> str:
    path = safe_path(path)
    if path != PurePosixPath(path).name:
        raise AuditBlocked('客户端附加通知专项复核的根通知路径无效')
    for record in git(repo, 'ls-tree', '-z', ref, '--', path).split(b'\0'):
        if not record:
            continue
        meta, name = record.split(b'\t', 1)
        if name.decode() != path:
            continue
        mode, kind, _ = meta.decode().split()[:3]
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise AuditBlocked('根许可或 Notice 不是普通文件')
        return hashlib.sha256(blob(repo, ref, path)).hexdigest()
    raise AuditBlocked('客户端附加通知专项复核的根通知在当前快照中不存在')


def accept_client_attached_notices(review: dict, repo: Path, new: str, install_scopes: list[str],
                                  grant: bytes, license_value: str | None, *, is_collection: bool) -> set[str]:
    """Return install scopes proven by bound client attach + install readback.

    Absent field: empty set. Present but invalid: AuditBlocked. The acceptance is
    bound to the exact new pin and a verified client commit; it does not extend
    to a later pin and does not treat a future client change as delivery.
    """
    accepted = review.get('acceptedClientAttachedNotices')
    if not accepted:
        return set()
    if not isinstance(accepted, dict):
        raise AuditBlocked('客户端附加通知专项复核记录无效')
    if not all(isinstance(review.get(key), str) and review[key].strip()
               for key in ('reviewedBy', 'reviewedAt', 'notes')):
        raise AuditBlocked('客户端附加通知专项复核必须包含审核人、日期和理由')
    source_ref = accepted.get('sourceRef')
    client_commit = accepted.get('clientCommit')
    client_tree = accepted.get('clientTree')
    observed_at = accepted.get('observedAt')
    notice_path = accepted.get('noticeRootPath')
    notice_sha = accepted.get('noticeSha256')
    if not isinstance(source_ref, str) or not re.fullmatch(r'[0-9a-f]{40}', source_ref):
        raise AuditBlocked('客户端附加通知专项复核未绑定完整上游 pin')
    if source_ref != new:
        raise AuditBlocked('客户端附加通知专项复核未绑定当前固定快照')
    if not isinstance(client_commit, str) or not re.fullmatch(r'[0-9a-f]{40}', client_commit):
        raise AuditBlocked('客户端附加通知专项复核的客户端提交无效')
    implementations = (CLIENT_COLLECTION_NOTICE_IMPLEMENTATIONS if is_collection
                       else CLIENT_STANDALONE_NOTICE_IMPLEMENTATIONS)
    expected_tree = implementations.get(client_commit)
    if expected_tree is None:
        raise AuditBlocked('客户端附加通知专项复核的客户端提交不在已核验实现清单中（安装类型不匹配或提交未核验）')
    if not is_collection:
        if len(install_scopes) != 1 or not safe_path(install_scopes[0]):
            raise AuditBlocked('独立技能附加通知专项复核必须绑定单个 Git 子目录')
        if client_tree is None or observed_at is None:
            raise AuditBlocked('独立技能附加通知专项复核需要客户端 tree 和回读时间')
    if client_tree is not None and (not isinstance(client_tree, str)
                                    or not re.fullmatch(r'[0-9a-f]{40}', client_tree)
                                    or client_tree != expected_tree):
        raise AuditBlocked('客户端附加通知专项复核的客户端 tree 与已核验实现不一致')
    if observed_at is not None and not (isinstance(observed_at, str)
                                        and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', observed_at)):
        raise AuditBlocked('客户端附加通知专项复核的回读时间格式不正确')
    if not isinstance(notice_path, str) or not is_root_notice_filename(notice_path):
        raise AuditBlocked('客户端附加通知专项复核的根通知路径无效')
    if not _sha256_hex(notice_sha):
        raise AuditBlocked('客户端附加通知专项复核的根通知哈希无效')
    actual = root_regular_file_sha256(repo, new, notice_path)
    if actual != notice_sha:
        raise AuditBlocked('客户端附加通知专项复核的根通知哈希与当前快照不一致')
    if not grant or hashlib.sha256(grant).hexdigest() != notice_sha:
        raise AuditBlocked('客户端附加通知专项复核的根通知哈希与当前快照不一致')
    from update_diagnostics import mit_grant
    if license_value == 'MIT' and not mit_grant(grant):
        raise AuditBlocked('客户端附加通知专项复核不能用于不完整的 MIT 声明')

    scopes = accepted.get('scopes')
    if not isinstance(scopes, list) or not scopes:
        raise AuditBlocked('客户端附加通知专项复核缺少子项安装回读')
    required = {safe_path(scope) for scope in install_scopes}
    seen: set[str] = set()
    for item in scopes:
        if not isinstance(item, dict):
            raise AuditBlocked('客户端附加通知专项复核子项回读无效')
        raw_path = item.get('path')
        if not isinstance(raw_path, str) or any(symbol in raw_path for symbol in '*?[]'):
            raise AuditBlocked('客户端附加通知专项复核路径不安全')
        path = safe_path(raw_path)
        if path != raw_path:
            raise AuditBlocked('客户端附加通知专项复核路径不安全')
        if path in seen:
            raise AuditBlocked('客户端附加通知专项复核路径重复')
        seen.add(path)
        attached = item.get('attached')
        if not isinstance(attached, list) or not attached:
            raise AuditBlocked('客户端附加通知专项复核缺少子项安装回读')
        delivered = False
        names: set[str] = set()
        for record in attached:
            if not isinstance(record, dict):
                raise AuditBlocked('客户端附加通知专项复核子项回读无效')
            name, source_name, digest = record.get('name'), record.get('sourceName'), record.get('sha256')
            if not is_root_notice_filename(name) or not is_root_notice_filename(source_name):
                raise AuditBlocked('客户端附加通知专项复核的附带文件名无效')
            if not _sha256_hex(digest):
                raise AuditBlocked('客户端附加通知专项复核子项哈希无效')
            if name in names:
                raise AuditBlocked('客户端附加通知专项复核附带文件名重复')
            names.add(name)
            if source_name == notice_path and digest == notice_sha:
                delivered = True
        if not delivered:
            raise AuditBlocked('客户端附加通知专项复核未证明该子项安装副本携带完整根通知')
    if seen != required:
        raise AuditBlocked('客户端附加通知专项复核与安装范围不一致或缺少子项安装回读')
    return seen




LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9'-]{4,}")
CJK_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")


def _text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def _latin_stems(text: str) -> set[str]:
    tokens: set[str] = set()
    for match in LATIN_TOKEN.finditer(text or ''):
        for part in re.split(r"[-']", match.group(0).casefold()):
            if len(part) >= 5:
                tokens.add(part)
    stems = set(tokens)
    for token in tokens:
        for suffix in ('ing', 'ed', 'es', 's'):
            if len(token) > len(suffix) + 3 and token.endswith(suffix):
                stems.add(token[:-len(suffix)])
                if suffix == 'ing':
                    stems.add(token[:-3] + 'e')
    return stems


def short_desc_covers_new_description(short_desc: str, old_description: str, new_description: str,
                                      previous_short_desc: str = '') -> bool:
    """English/latin shortDesc must pick up distinctive new-description terms not already in the old listing."""
    new_only = _latin_stems(new_description) - _latin_stems(old_description)
    incremental = new_only - _latin_stems(previous_short_desc or '')
    target = incremental or new_only
    if not target:
        return True
    return bool(_latin_stems(short_desc) & target)


def _scope_locale_sources(entry: dict, sidecar: dict, scope: str) -> tuple[dict, dict | None]:
    for child in entry.get('children') or []:
        if safe_path(child.get('path') or '') == scope:
            catalog = None
            for item in sidecar.get('spec', {}).get('collection', {}).get('children', []):
                item_path = item.get('path')
                same_path = isinstance(item_path, str) and safe_path(item_path) == scope
                same_id = item.get('identity', {}).get('id') == child.get('id')
                if same_path or same_id:
                    catalog = item
                    break
            return child, catalog
    return {'id': entry.get('id'), 'path': scope, 'i18n': entry.get('i18n') or {}}, sidecar


def _has_locale_copy(entry: dict, scope: str) -> bool:
    """True only when this install scope already has listing shortDesc to review.

    Collection-root i18n is not a derived summary of every child; a new member
    without its own shortDesc is not treated as already having locale copy.
    """
    for child in entry.get('children') or []:
        if child.get('path') == scope:
            return any(isinstance(value, dict) and value.get('shortDesc')
                       for value in (child.get('i18n') or {}).values())
    if entry.get('children'):
        return False
    return any(isinstance(value, dict) and value.get('shortDesc')
               for value in (entry.get('i18n') or {}).values())


def description_changed_locale_scopes(repo: Path, entry: dict, old: str, new: str, install_scopes: list[str]) -> dict[str, tuple[dict, dict]]:
    changed: dict[str, tuple[dict, dict]] = {}
    for scope in install_scopes:
        marker = f'{scope}/SKILL.md' if scope else 'SKILL.md'
        before = GENERATOR.skill_frontmatter(repo, marker, old)
        after = GENERATOR.skill_frontmatter(repo, marker, new)
        if not isinstance(before, dict) or not isinstance(after, dict):
            continue
        if before.get('description') != after.get('description') and _has_locale_copy(entry, scope):
            changed[scope] = (before, after)
    return changed


def accept_description_and_locales(review: dict, entry: dict, sidecar: dict, repo: Path,
                                   old: str, new: str, install_scopes: list[str]) -> set[str]:
    """Return scopes whose listing shortDesc was reviewed against the new upstream description.

    Absent field: empty set. Present but invalid: AuditBlocked. The acceptance is
    bound to the exact old/new pins and reviewed listing text; it does not extend
    to a later pin and does not accept stale or unmatched shortDesc.
    """
    accepted = review.get('acceptedDescriptionAndLocales')
    if not accepted:
        return set()
    if not isinstance(accepted, dict):
        raise AuditBlocked('简介与双语专项复核记录无效')
    if not all(isinstance(review.get(key), str) and review[key].strip()
               for key in ('reviewedBy', 'reviewedAt', 'notes')):
        raise AuditBlocked('简介与双语专项复核必须包含审核人、日期和理由')
    from_ref, to_ref = accepted.get('fromRef'), accepted.get('toRef')
    if not isinstance(from_ref, str) or not re.fullmatch(r'[0-9a-f]{40}', from_ref):
        raise AuditBlocked('简介与双语专项复核未绑定完整旧 pin')
    if not isinstance(to_ref, str) or not re.fullmatch(r'[0-9a-f]{40}', to_ref):
        raise AuditBlocked('简介与双语专项复核未绑定完整新 pin')
    if from_ref != old or to_ref != new:
        raise AuditBlocked('简介与双语专项复核未绑定当前固定快照')
    required = description_changed_locale_scopes(repo, entry, old, new, install_scopes)
    files = accepted.get('files')
    if not isinstance(files, list) or not files:
        raise AuditBlocked('简介与双语专项复核缺少受影响路径')
    seen: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            raise AuditBlocked('简介与双语专项复核路径记录无效')
        raw_path = item.get('path')
        if not isinstance(raw_path, str) or any(symbol in raw_path for symbol in '*?[]'):
            raise AuditBlocked('简介与双语专项复核路径不安全')
        path = safe_path(raw_path)
        if path != raw_path:
            raise AuditBlocked('简介与双语专项复核路径不安全')
        if path in seen:
            raise AuditBlocked('简介与双语专项复核路径重复')
        seen.add(path)
        if path not in required:
            raise AuditBlocked('简介与双语专项复核路径与上游简介变化范围不一致')
        before, after = required[path]
        if item.get('oldDescription') != before.get('description'):
            raise AuditBlocked('简介与双语专项复核的旧简介与当前快照不一致')
        if item.get('newDescription') != after.get('description'):
            raise AuditBlocked('简介与双语专项复核的新简介与当前快照不一致')
        if item.get('newFrontmatterSha256') != frontmatter_identity(after):
            raise AuditBlocked('简介与双语专项复核的 frontmatter 哈希与当前快照不一致')
        locales = item.get('locales')
        if not isinstance(locales, dict) or not locales:
            raise AuditBlocked('简介与双语专项复核缺少语种文案')
        source, catalog = _scope_locale_sources(entry, sidecar, path)
        existing = {
            locale: (copy.get('shortDesc') if isinstance(copy, dict) else None)
            for locale, copy in (source.get('i18n') or {}).items()
        }
        existing = {locale: text for locale, text in existing.items() if isinstance(text, str) and text}
        if set(locales) != set(existing):
            raise AuditBlocked('简介与双语专项复核语种与条目现有简介不一致')
        english_text = None
        if isinstance(locales.get('en-US'), dict):
            english_text = locales['en-US'].get('shortDesc')
        for locale, record in locales.items():
            if not isinstance(locale, str) or not locale.strip() or not isinstance(record, dict):
                raise AuditBlocked('简介与双语专项复核语种记录无效')
            short_desc = record.get('shortDesc')
            previous = record.get('previousShortDesc')
            digest = record.get('sha256')
            if not isinstance(short_desc, str) or not short_desc.strip():
                raise AuditBlocked('简介与双语专项复核的简介文案为空')
            if not isinstance(previous, str):
                raise AuditBlocked('简介与双语专项复核缺少原先简介')
            if not _sha256_hex(digest) or digest != _text_sha256(short_desc):
                raise AuditBlocked('简介与双语专项复核的简介哈希与文案不一致')
            if existing.get(locale) != short_desc:
                raise AuditBlocked('简介与双语专项复核的简介与条目现有文案不一致')
            if catalog is not None:
                summary = ((catalog.get('presentation') or {}).get('i18n') or {}).get(locale, {})
                if not isinstance(summary, dict) or summary.get('summary') != short_desc:
                    raise AuditBlocked('简介与双语专项复核的 catalog 镜像与条目简介不一致')
            if previous.strip() and short_desc == previous:
                raise AuditBlocked('简介与双语专项复核的简介未相对原先文案更新')
            if short_desc == before.get('description'):
                raise AuditBlocked('简介与双语专项复核的简介仍是旧的上游简介')
            if CJK_RE.search(short_desc) or locale.lower().startswith('zh'):
                if not CJK_RE.search(short_desc):
                    raise AuditBlocked('简介与双语专项复核的中文简介不是中文')
                if short_desc in {before.get('description'), after.get('description'), english_text}:
                    raise AuditBlocked('简介与双语专项复核的中文简介未实际更新以匹配上游简介')
            elif not short_desc_covers_new_description(short_desc, before.get('description') or '', after.get('description') or '', previous):
                raise AuditBlocked('简介与双语专项复核的简介未实际更新以匹配上游简介')
    if seen != set(required):
        raise AuditBlocked('简介与双语专项复核与上游简介变化范围不一致或缺少路径')
    return seen


def accept_scoped_notice_changes(review: dict, repo: Path, old: str, new: str,
                                 old_map: dict[str, str], new_map: dict[str, str]) -> None:
    """Accept only exact, additive, in-place NOTICE edits bound to this snapshot pair.

    Nested LICENSE/COPYING changes, deletions, renames, new files, rewrites that
    drop existing text, symlinks, path escape, globs, hash or ref mismatches,
    and unexpected extra files remain rejected. Root LICENSE/NOTICE/COPYING stay
    on acceptedRootEvidenceSha256.
    """
    old_paths, new_paths = set(old_map), set(new_map)
    if any(is_license_or_copying_filename(path) and old_map.get(path) != new_map.get(path)
           for path in old_paths | new_paths):
        raise AuditBlocked('安装范围内的许可证或 Notice 有变化，需专项复核')
    if old_paths - new_paths or new_paths - old_paths:
        raise AuditBlocked('安装范围内的许可证或 Notice 有变化，需专项复核')
    changed = sorted(path for path in old_paths & new_paths if old_map[path] != new_map[path])
    if not changed or any(not is_notice_filename(path) for path in changed):
        raise AuditBlocked('安装范围内的许可证或 Notice 有变化，需专项复核')

    accepted = review.get('acceptedScopedNotice')
    if not isinstance(accepted, dict):
        raise AuditBlocked('安装范围内的许可证或 Notice 有变化，需专项复核')
    if not all(isinstance(review.get(key), str) and review[key].strip()
               for key in ('reviewedBy', 'reviewedAt', 'notes')):
        raise AuditBlocked('嵌套 Notice 专项复核必须包含审核人、日期和理由')
    if accepted.get('fromRef') != old or accepted.get('toRef') != new:
        raise AuditBlocked('嵌套 Notice 专项复核未绑定当前固定快照')

    files = accepted.get('files')
    if not isinstance(files, list) or not files:
        raise AuditBlocked('嵌套 Notice 专项复核文件列表无效')

    seen: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            raise AuditBlocked('嵌套 Notice 专项复核文件列表无效')
        raw_path = item.get('path')
        if not isinstance(raw_path, str) or any(symbol in raw_path for symbol in '*?[]'):
            raise AuditBlocked('嵌套 Notice 路径不安全')
        path = safe_path(raw_path)
        if path != raw_path or not path or is_license_or_copying_filename(path) or not is_notice_filename(path):
            raise AuditBlocked('专项复核不能用于接受嵌套许可证变更或根路径 Notice')
        if '/' not in path:
            raise AuditBlocked('专项复核不能用于接受嵌套许可证变更或根路径 Notice')
        if path in seen:
            raise AuditBlocked('嵌套 Notice 专项复核路径重复')
        seen.add(path)
        previous_digest, digest = item.get('previousSha256'), item.get('sha256')
        if not _sha256_hex(previous_digest) or not _sha256_hex(digest):
            raise AuditBlocked('嵌套 Notice 专项复核哈希无效')
        if path not in old_map or path not in new_map:
            raise AuditBlocked('嵌套 Notice 专项复核与实际变更文件不一致')
        old_bytes, new_bytes = blob(repo, old, path), blob(repo, new, path)
        if (old_map[path] != previous_digest or new_map[path] != digest
                or hashlib.sha256(old_bytes).hexdigest() != previous_digest
                or hashlib.sha256(new_bytes).hexdigest() != digest):
            raise AuditBlocked('嵌套 Notice 专项复核哈希不匹配')
        if not old_bytes or not new_bytes or new_bytes == old_bytes or not new_bytes.startswith(old_bytes):
            raise AuditBlocked('嵌套 Notice 变更未保留原有声明，不能作为附加 Notice 接受')
    if seen != set(changed):
        raise AuditBlocked('嵌套 Notice 专项复核与实际变更文件不一致')


def load_special_review(record) -> dict:
    if not record:
        return {}
    if not isinstance(record, dict) or record.get('schemaVersion') != 1:
        raise AuditBlocked('专项复核记录格式无效')
    return record


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


def _audit_snapshots(repo: Path, entry: dict, sidecar: dict, result: dict,
                    observed_at: str | None = None, special_review: dict | None = None) -> tuple[dict, dict, dict]:
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
    review = load_special_review(special_review)
    exclude_paths = review.get('excludePaths') or []
    budget_exempt_paths = review.get('budgetExemptPaths') or []
    if not isinstance(exclude_paths, list) or not isinstance(budget_exempt_paths, list):
        raise AuditBlocked('专项复核的排除或预算豁免列表无效')
    if any(not isinstance(item, str) or item != safe_path(item) for item in [*exclude_paths, *budget_exempt_paths]):
        raise AuditBlocked('专项复核路径不安全')
    if any(protected_audit_path(item) for item in exclude_paths):
        raise AuditBlocked('排除列表不能用于许可、Notice 或依赖清单')
    paths = [safe_path(child['path']) for child in entry.get('children', [])]
    if not paths:
        paths = [safe_path(entry['source'].get('path', ''))]
    old_member_paths = set(paths) if entry.get('children') else set()
    discovered_children = []
    if entry.get('children'):
        discovered_children = GENERATOR.discover_children(repo, new)
        discovered = {safe_path(child['path']) for child in discovered_children}
        if discovered != set(paths):
            accepted_paths = review.get('acceptedCollectionPaths') or []
            accepted = None
            if isinstance(accepted_paths, list) and all(isinstance(item, str) for item in accepted_paths):
                try:
                    accepted = {safe_path(item) for item in accepted_paths}
                except AuditBlocked:
                    accepted = None
            if accepted is None or len(accepted_paths) != len(accepted) or accepted != discovered:
                raise AuditBlocked('合集成员集合变化，需核对新增/移除成员及翻译')
            paths = [safe_path(child['path']) for child in discovered_children]
    old_files, new_files = {}, {}
    for path in paths:
        old_files.update(tree(repo, old, path, exclude_paths, budget_exempt_paths))
        new_files.update(tree(repo, new, path, exclude_paths, budget_exempt_paths))
    if not new_files or len(new_files) > MAX_FILES or sum(item[2] for item in new_files.values()) > MAX_CONTENT_BYTES:
        raise AuditBlocked('新快照为空或超过总预算')
    old_root = root_evidence(repo, old)
    new_root = root_evidence(repo, new)
    if review.get('acceptedClientAttachedNotices'):
        evidence_path = safe_path((sidecar.get('governance', {}).get('license') or {}).get('evidencePath')
                                  or sidecar.get('governance', {}).get('compliance', {}).get('licenseEvidencePath')
                                  or '')
        grant = blob(repo, new, evidence_path) if evidence_path else b''
        accept_client_attached_notices(
            review, repo, new, paths, grant,
            (sidecar.get('governance', {}).get('license') or {}).get('value'),
            is_collection=bool(entry.get('children')))
    if review.get('acceptedDescriptionAndLocales'):
        accept_description_and_locales(review, entry, sidecar, repo, old, new, paths)
    if old_root != new_root:
        accepted_root = review.get('acceptedRootEvidenceSha256') or {}
        if set(old_root) - set(new_root):
            raise AuditBlocked('根许可证或 Notice 有变化，需专项复核')
        expected_root = {
            path: digest
            for path, digest in new_root.items()
            if old_root.get(path) != digest
        }
        if (not isinstance(accepted_root, dict)
                or any(not isinstance(key, str) or not isinstance(value, str) for key, value in accepted_root.items())
                or accepted_root != expected_root):
            raise AuditBlocked('根许可证或 Notice 有变化，需专项复核')
    old_license_dirs = root_license_directory_files(repo, old)
    new_license_dirs = root_license_directory_files(repo, new)
    if set(old_license_dirs) - set(new_license_dirs):
        raise AuditBlocked('根许可目录被删除，需专项复核')
    expected_dir_manifests = {
        directory: license_directory_manifest_sha256(files)
        for directory, files in new_license_dirs.items()
        if old_license_dirs.get(directory) != files
    }
    if expected_dir_manifests:
        accepted_dirs = review.get('acceptedRootLicenseDirectoryManifestSha256') or {}
        if (not isinstance(accepted_dirs, dict)
                or any(not isinstance(key, str) or not isinstance(value, str) for key, value in accepted_dirs.items())
                or accepted_dirs != expected_dir_manifests):
            raise AuditBlocked('根许可目录内的第三方许可文本有变化，需专项复核')
        if not all(isinstance(review.get(key), str) and review[key].strip()
                   for key in ('reviewedBy', 'reviewedAt', 'notes')):
            raise AuditBlocked('根许可目录专项复核必须包含审核人、日期和理由')
    licenses = dict(new_root)
    for files in new_license_dirs.values():
        licenses.update(files)
    # 安装范围内的嵌套许可同样影响再分发，不能只核对根许可证。
    def scoped_evidence(ref, files):
        return {path: hashlib.sha256(blob(repo, ref, path)).hexdigest()
                for path in files if PurePosixPath(path).name.upper().startswith(('LICENSE', 'NOTICE', 'COPYING'))}
    scoped_licenses = scoped_evidence(old, old_files)
    new_scoped = scoped_evidence(new, new_files)
    if scoped_licenses != new_scoped:
        accept_scoped_notice_changes(review, repo, old, new, scoped_licenses, new_scoped)
    licenses.update(new_scoped)
    accepted_root = review.get('acceptedRootEvidenceSha256') or {}
    for path in {compliance.get('licenseEvidencePath'), compliance.get('noticePath'),
                 governance.get('license', {}).get('evidencePath')} - {None}:
        old_bytes, new_bytes = blob(repo, old, path), blob(repo, new, path)
        if not old_bytes or old_bytes != new_bytes:
            digest = hashlib.sha256(new_bytes).hexdigest() if new_bytes else None
            if (not old_bytes or not new_bytes or not isinstance(accepted_root, dict)
                    or accepted_root.get(path) != digest):
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
        accepted = review.get('acceptedDependencyIdentities') or {}
        if not isinstance(accepted, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in accepted.items()):
            raise AuditBlocked('依赖清单有变化，无法自动确认新的前置条件')
        if set(old_dependencies) - set(new_dependencies):
            raise AuditBlocked('依赖清单有变化，无法自动确认新的前置条件')
        expected = {
            path: dependency_acceptance_key(value)
            for path, value in new_dependencies.items()
            if path not in old_dependencies or dependency_acceptance_key(old_dependencies[path]) != dependency_acceptance_key(value)
        }
        if accepted != expected:
            raise AuditBlocked('依赖清单有变化，无法自动确认新的前置条件')
    versions = {}
    accepted_fm = review.get('acceptedFrontmatterSha256') or {}
    for path in paths:
        marker = f'{path}/SKILL.md' if path else 'SKILL.md'
        new_fm = GENERATOR.skill_frontmatter(repo, marker, new)
        if not isinstance(new_fm, dict):
            raise AuditBlocked('技能 frontmatter 必须是对象')
        is_new_member = bool(entry.get('children')) and path not in old_member_paths
        if is_new_member:
            if not isinstance(accepted_fm, dict) or accepted_fm.get(path) != frontmatter_identity(new_fm):
                raise AuditBlocked('名称、简介、依赖、兼容性或其他结构化声明有变化，需同步审核元数据和翻译')
        else:
            old_fm = GENERATOR.skill_frontmatter(repo, marker, old)
            if not isinstance(old_fm, dict):
                raise AuditBlocked('技能 frontmatter 必须是对象')
            if stable_frontmatter(old_fm) != stable_frontmatter(new_fm):
                if not isinstance(accepted_fm, dict) or accepted_fm.get(path) != frontmatter_identity(new_fm):
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
        # 新增/移除成员及翻译需要单独处理；接受后按发现结果重建成员列表，不为新成员编造翻译。
        if {child['path'] for child in updated['children']} != {child['path'] for child in discovered_children}:
            existing = {child['path']: child for child in updated['children']}
            catalog_existing = {
                child.get('identity', {}).get('id'): child
                for child in metadata.get('spec', {}).get('collection', {}).get('children', [])
            }
            rebuilt, rebuilt_catalog = [], []
            for discovered_child in discovered_children:
                path = discovered_child['path']
                if path in existing:
                    child = existing[path]
                    catalog_child = catalog_existing.get(child['id'])
                else:
                    child = {'id': discovered_child['id'], 'path': path}
                    catalog_child = {'identity': {'id': child['id']}, 'path': path}
                if path in versions:
                    version = versions[path]
                    previous = GENERATOR.normalize_version(child.get('version'))
                    if previous and tuple(map(int, version.split('.'))) < tuple(map(int, previous.split('.'))):
                        raise AuditBlocked('拒绝自动回退合集成员版本')
                    child['version'] = version
                    if catalog_child is not None:
                        catalog_child['release'] = {'state': 'known', 'version': version, 'versionScheme': 'semver'}
                rebuilt.append(child)
                if catalog_child is not None:
                    rebuilt_catalog.append(catalog_child)
            updated['children'] = rebuilt
            if metadata.get('spec', {}).get('collection') is not None:
                metadata['spec']['collection']['children'] = rebuilt_catalog
        else:
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
    if review:
        report['specialReview'] = {
            'reviewedBy': review.get('reviewedBy'),
            'reviewedAt': review.get('reviewedAt'),
            'excludePaths': list(exclude_paths),
            'budgetExemptPaths': list(budget_exempt_paths),
        }
        report['limitations'].append('依赖清单或结构化简介如有变化，已按专项复核记录中的接受哈希核对，不代表这些字段与旧快照逐字节相同。')
        if review.get('acceptedRootEvidenceSha256') or review.get('acceptedCollectionPaths'):
            report['limitations'].append('根许可证/Notice 或合集成员如有变化，已按专项复核记录中的接受哈希或路径集合核对，不代表与旧快照逐字节或成员集合相同。')
        if review.get('acceptedScopedNotice'):
            report['limitations'].append('安装范围内的 Notice 如有变化，已按专项复核记录中绑定的快照、路径和哈希核对，且新文件必须完整保留旧 Notice 字节；不代表与旧快照逐字节相同，也不接受嵌套许可证变更。')
        if review.get('acceptedRootLicenseDirectoryManifestSha256'):
            report['limitations'].append('根 licenses/ 等许可目录内的第三方许可文本如有变化，已按专项复核记录中的目录清单哈希核对，不代表与旧快照逐文件相同；不接受根 LICENSE/NOTICE/COPYING 文件被删除或改成非普通文件。')
        if review.get('acceptedClientAttachedNotices'):
            report['limitations'].append('所选安装目录在源树中仍可能没有完整通知；已按专项复核中绑定的上游 pin、已核验客户端提交和逐项安装回读哈希证明安装副本携带了完整根通知。该接受不是许可例外，不得自动延伸到新 pin，也不能把尚未回读的客户端附加写成已交付。')
        if review.get('acceptedDescriptionAndLocales'):
            report['limitations'].append('上游简介如有变化，已按专项复核中绑定的旧/新 pin、路径、frontmatter 哈希和已更新的双语简介核对；不代表自动翻译，也不得把旧简介或未匹配新简介的文案延伸到新 pin。')
        if exclude_paths:
            report['limitations'].append('excludePaths 只从本仓库的自动审核树遍历中省略路径；DesireCore 安装器在支持该字段前仍会从上游 pin 安装这些文件。')
    errors = validate_record(metadata, report)
    if errors:
        raise AuditBlocked('; '.join(errors))
    return updated, metadata, report


def audit_snapshots(repo: Path, entry: dict, sidecar: dict, result: dict,
                    observed_at: str | None = None, special_review: dict | None = None, candidate_view: dict | None = None):
    from update_diagnostics import inspect_snapshots, candidate_consistency
    if not all(isinstance(result.get(k), str) and re.fullmatch('[0-9a-f]{40}', result[k]) for k in ('ref', 'head')):
        return _audit_snapshots(repo, entry, sidecar, result, observed_at, special_review)
    findings = []
    try:
        findings = inspect_snapshots(repo, entry, sidecar, result, special_review)
        if candidate_view:
            candidate_rows, valid_source = candidate_consistency(entry, sidecar, result, candidate_view)
            findings.extend(candidate_rows)
            if valid_source:
                independent = inspect_snapshots(repo, candidate_view['entry'], candidate_view['metadata'], result)
                for row in independent:
                    row['basis'] = 'existing-pr-candidate@' + candidate_view['head']
                    if row['gate'] == 'description-and-locales':
                        row['reason'] = '上游简介曾变化；此行是当前 PR 文案的独立人工复核要求，不表示 main 的旧文案错误仍存在于已修订 PR。 / Upstream description changed; this is independent semantic review of the current candidate, not a claim that old main copy remains stale in a repaired PR.'
                findings.extend(independent)
    except (ValueError, TypeError, KeyError, AttributeError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        findings = [dict(id=entry.get('id', '?'), path='.', oldRef=result.get('ref', '?'),
                         newRef=result.get('head', '?'), gate='independent-static-diagnostics',
                         state='not_checked', origin='unknown', reason=str(error),
                         repair='静态诊断未完成，人工检查并重跑；不能假设通过。 / Complete diagnostics and rerun; never assume success.')]
    try:
        output = _audit_snapshots(repo, entry, sidecar, result, observed_at, special_review)
    except AuditBlocked as error:
        pipeline = dict(id=entry.get('id', '?'), path='.', oldRef=result.get('ref', '?'),
                        newRef=result.get('head', '?'), gate='actual-pipeline-failure', state='blocked',
                        origin='unknown', reason=str(error),
                        repair='修复实际失败门槛后重跑；其后流水线未完成，独立静态发现不代表后续检查已通过。 / Fix this gate and rerun; downstream pipeline stages did not complete. Independent findings are not downstream passes.')
        remaining = {**pipeline, 'gate': 'remaining-pipeline', 'state': 'not_checked',
                     'reason': '实际失败点之后的流水线未完成；独立静态检查不等于后续流水线通过。 / Pipeline stages after the actual failure did not complete; independent static findings are not downstream passes.'}
        error.findings = [pipeline, remaining, *findings]
        raise error
    blockers = [r for r in findings if r['state'] in ('blocked', 'manual_review', 'not_checked')]
    if blockers:
        error = AuditBlocked('安装通知、精确 pin 例外或元数据一致性需处理 / Installed notices, exact-pin exception or metadata consistency needs review: ' + '; '.join(r['gate'] + ': ' + r['path'] for r in blockers))
        error.findings = findings
        raise error
    return output


def audit_update(entry: dict, sidecar: dict, result: dict,
                 special_review: dict | None = None, candidate_view: dict | None = None) -> tuple[dict, dict, dict]:
    url = entry['source']['repoUrl']
    if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?', url):
        raise AuditBlocked('自动获取仅使用已登记的 GitHub HTTPS 来源')
    with tempfile.TemporaryDirectory(prefix='skill-audit-') as temporary:
        repo = Path(temporary)
        git(repo, 'init', '--quiet')
        git(repo, 'fetch', '--quiet', '--no-tags', '--depth=1', url, result['ref'], result['head'])
        return audit_snapshots(repo, entry, sidecar, result, special_review=special_review, candidate_view=candidate_view)
