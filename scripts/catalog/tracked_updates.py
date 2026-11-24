"""Pinned artifact/local tracking. Never execute upstream code or infer versions.

Policy is read from the trusted base checkout, never from a candidate PR.
A content hash identifies bytes; only audit_payload produces admission evidence.
"""
from __future__ import annotations
import copy
import hashlib
import io
import json
import re
import stat
import subprocess
import tempfile
import urllib.parse
import urllib.request
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from audit_skill_update import AuditBlocked, audit_snapshots, git, root_evidence, root_license_directory_files
from automated_review import validate_record

CONFIG = 'config/verified-updates.v1.json'
LOGIN = 'mashagua'
EMAIL = '993498039@qq.com'
MAX_BYTES = 50 * 1024 * 1024
MAX_FILE = 1024 * 1024
SHA40 = re.compile(r'[0-9a-f]{40}')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
REPO = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(value, empty=False):
    p = PurePosixPath(value)
    if (not isinstance(value, str) or '\\' in value or p.is_absolute() or '..' in p.parts
            or (not empty and (not value or str(p) == '.')) or str(p) != value):
        raise AuditBlocked('unsafe/non-canonical tracked path')
    if (any(ord(c) < 32 for c in value) or ':' in value
            or any(part.endswith((' ', '.')) or re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', part, re.I) for part in p.parts)):
        raise AuditBlocked('path is unsafe on a supported desktop platform')
    if any(part in ('.git', '.github') for part in p.parts):
        raise AuditBlocked('repository control path cannot be tracked content')
    return value


def allowed_url(url):
    p = urllib.parse.urlsplit(url)
    if (p.scheme != 'https' or p.username or p.password or p.port not in (None, 443)
            or p.fragment or not p.hostname):
        raise AuditBlocked('only credential-free HTTPS artifacts are supported')
    if p.hostname not in ('api.github.com', 'github.com', 'raw.githubusercontent.com',
                           'objects.githubusercontent.com', 'release-assets.githubusercontent.com',
                           'clawhub.ai', 'wry-manatee-359.convex.site'):
        raise AuditBlocked('artifact host is not a supported registry/release host')
    return url


class Redirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        allowed_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url):
    allowed_url(url)
    req = urllib.request.Request(url, headers={'User-Agent': 'market-verified-updates/1'})
    with urllib.request.build_opener(Redirects()).open(req, timeout=45) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise AuditBlocked('artifact download exceeds budget')
    return data


def json_url(url):
    return json.loads(fetch(url))


def gh(*args):
    return subprocess.run(['gh', *args], check=True, capture_output=True, text=True).stdout.strip()


def check_identity():
    if gh('api', 'user', '--jq', '.login') != LOGIN:
        raise AuditBlocked('publishing/merge requires the designated human maintainer; no bot fallback')


def load_config(root):
    cfg = json.loads((root / CONFIG).read_text())
    if cfg.get('schemaVersion') != 1 or cfg.get('autoMerge') != 'reviewed-or-identical-installed-payload':
        raise AuditBlocked('unsupported automation policy')
    required = cfg.get('requiredChecks')
    if (not isinstance(required, list) or not all(isinstance(x, str) for x in required)
            or not {'validate', 'translate', 'CodeQL'} <= set(required)):
        raise AuditBlocked('required exact-head checks cannot be omitted')
    if not isinstance(cfg.get('tracking'), dict):
        raise AuditBlocked('missing explicit tracking map')
    if any(not SLUG.fullmatch(k) for k in cfg['tracking']):
        raise AuditBlocked('invalid tracking id')
    return cfg


def discover(track, source):
    adapter = track.get('adapter')
    if adapter == 'clawhub':
        slug, owner = track['slug'], track['owner']
        if not SLUG.fullmatch(slug) or not re.fullmatch(r'[A-Za-z0-9_-]+', owner):
            raise AuditBlocked('invalid registry identity')
        meta = json_url(f'https://clawhub.ai/api/v1/skills/{slug}?ownerHandle={owner}')
        if meta.get('owner', {}).get('handle') != owner or meta.get('skill', {}).get('slug') != slug:
            raise AuditBlocked('registry owner changed or could not be verified')
        version = meta.get('latestVersion', {}).get('version')
        if not isinstance(version, str) or not re.fullmatch(r'\d+\.\d+\.\d+', version):
            raise AuditBlocked('registry lacks an explicit stable version')
        url = 'https://clawhub.ai/api/v1/download?' + urllib.parse.urlencode(
            {'slug': slug, 'version': version, 'ownerHandle': owner})
        # Version-specific endpoint, never an unpinned /latest download.
        return {'kind': 'zip', 'repoUrl': url, **({'path': source['path']} if source.get('path') else {})}
    if adapter in ('github-file', 'github-release'):
        repo = track['repo']
        if not REPO.fullmatch(repo):
            raise AuditBlocked('invalid GitHub repository')
        if adapter == 'github-file':
            ref = json_url(f'https://api.github.com/repos/{repo}/commits/' + urllib.parse.quote(track['branch'], safe=''))['sha']
            if not SHA40.fullmatch(ref):
                raise AuditBlocked('GitHub did not return an immutable commit')
            path = safe_path(track['path'])
            return {'kind': 'web', 'repoUrl': f'https://raw.githubusercontent.com/{repo}/{ref}/{path}'}
        release = json_url(f'https://api.github.com/repos/{repo}/releases/latest')
        if release.get('draft') or release.get('prerelease') or not release.get('tag_name'):
            raise AuditBlocked('release is not stable/published')
        assets = [a for a in release.get('assets', []) if a.get('name') == track['asset']]
        if len(assets) != 1 or not assets[0]['browser_download_url'].startswith(f'https://github.com/{repo}/releases/download/'):
            raise AuditBlocked('missing/ambiguous release asset')
        return {'kind': 'zip', 'repoUrl': assets[0]['browser_download_url'], **({'path': source['path']} if source.get('path') else {})}
    raise AuditBlocked('no supported discovery adapter; explicit tracking required')


class Payload(dict):
    modes = None


def unpack(source, data):
    if digest(data) != source['sha256']:
        raise AuditBlocked('download bytes do not match the immutable digest')
    if source['kind'] == 'web':
        if len(data) > MAX_FILE:
            raise AuditBlocked('web file exceeds ordinary audit budget')
        return {'SKILL.md': data}
    result, total, count = Payload(), 0, 0
    result.modes = {}
    folded = set()
    prefix = source.get('path', '')
    if prefix:
        safe_path(prefix)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for info in archive.infolist():
            count += 1
            if count > 2000 or info.flag_bits & 1:
                raise AuditBlocked('ZIP entry budget/encryption rejected')
            path = info.filename.rstrip('/')
            safe_path(path)
            mode = info.external_attr >> 16
            if mode & 0o111 and not info.is_dir():
                raise AuditBlocked('executable ZIP content requires manual review')
            if mode and stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise AuditBlocked('ZIP symlink/special file rejected')
            if info.is_dir():
                continue
            total += info.file_size
            if info.file_size > MAX_FILE or total > MAX_BYTES:
                raise AuditBlocked('ZIP expansion exceeds ordinary audit budget')
            key = unicodedata.normalize('NFC', path).casefold()
            if key in folded:
                raise AuditBlocked('duplicate/case-colliding ZIP path')
            folded.add(key)
            result.modes[path] = mode
            result[path] = archive.read(info)
    if prefix:
        modes = {p[len(prefix)+1:]: m for p, m in result.modes.items() if p.startswith(prefix + '/')}
        result = Payload({p[len(prefix)+1:]: b for p, b in result.items() if p.startswith(prefix + '/')})
        result.modes = modes
    if 'SKILL.md' not in result:
        raise AuditBlocked('selected artifact has no root SKILL.md')
    return result


def commit_payload(repo, files):
    for item in repo.iterdir():
        if item.name != '.git':
            import shutil
            shutil.rmtree(item) if item.is_dir() else item.unlink()
    for name, data in files.items():
        p = repo / safe_path(name)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    git(repo, 'add', '--all')
    git(repo, '-c', f'user.name={LOGIN}', '-c', f'user.email={EMAIL}',
        '-c', 'commit.gpgsign=false', 'commit', '--allow-empty', '--quiet', '-m', 'materialized audit snapshot')
    return git(repo, 'rev-parse', 'HEAD').decode().strip()


def audit_payload(entry, metadata, old_files, new_files, old_ref, new_ref, new_content):
    """Use the existing strict delta audit on materialized bytes, NOT a hash-only admission.

    Temporary Git IDs are transport identities only, replaced with the real
    artifact digest / upstream commit in the receipt. No upstream code runs.
    """
    if getattr(old_files, 'modes', None) != getattr(new_files, 'modes', None):
        raise AuditBlocked('artifact file permissions changed; manual review required')
    origin = metadata.get('provenance', {}).get('content', {})
    if (origin.get('ref') or origin.get('sha256')) != old_ref or origin.get('kind') != new_content.get('kind'):
        raise AuditBlocked('old provenance does not bind the real admitted snapshot')
    gov = metadata['governance']
    if (gov.get('availability') != 'installable' or gov.get('license', {}).get('state') != 'known'
            or gov.get('compliance', {}).get('reviewedRef') != old_ref or old_ref == new_ref):
        raise AuditBlocked('old snapshot lacks inheritable exact-pin admission')
    with tempfile.TemporaryDirectory(prefix='market-materialized-') as tmp:
        repo = Path(tmp)
        git(repo, 'init', '--quiet')
        a, b = commit_payload(repo, old_files), commit_payload(repo, new_files)
        virtual = {'id': metadata['identity']['id'], 'source': {'kind': 'git', 'repoUrl': new_content['url'], 'ref': a}}
        if entry and entry.get('latestVersion'):
            virtual['latestVersion'] = entry['latestVersion']
        sidecar = copy.deepcopy(metadata)
        sidecar['provenance']['content'] = {'kind': 'git', 'url': new_content['url'], 'ref': a}
        sidecar['governance']['compliance']['reviewedRef'] = a
        _, updated, report = audit_snapshots(repo, virtual, sidecar, {'ref': a, 'head': b})
    updated['provenance']['content'] = copy.deepcopy(new_content)
    updated['governance']['compliance']['reviewedRef'] = new_ref
    report['source'] = {'kind': new_content['kind'], 'url': new_content['url'], 'previousUrl': metadata['provenance']['content']['url'],
                        'previousRef': old_ref, 'ref': new_ref, 'paths': ['']}
    report['identicalInstalledPayload'] = old_files == new_files
    report['limitations'].append('Artifact/local bytes materialized solely for the existing delta audit; receipt pins refer to real upstream commits or SHA-256, not temporary Git commits. Upstream code was not executed.')
    problems = validate_record(updated, report)
    if problems:
        raise AuditBlocked('; '.join(problems))
    return updated, report


def source_blob(repo, ref, path):
    record = git(repo, 'ls-tree', '-z', ref, '--', path).rstrip(b'\0')
    if not record or b'\0' in record:
        raise AuditBlocked('mapped upstream file missing or ambiguous: ' + path)
    meta, name = record.split(b'\t', 1)
    mode, kind, oid = meta.decode().split()
    if name.decode() != path or kind != 'blob' or mode not in ('100644', '100755'):
        raise AuditBlocked('mapped upstream file is not regular: ' + path)
    if int(git(repo, 'cat-file', '-s', oid)) > MAX_FILE:
        raise AuditBlocked('mapped upstream file exceeds budget: ' + path)
    return git(repo, 'cat-file', 'blob', oid)


def local_plan(root, item_id, track, metadata, target=None):
    origin = metadata['provenance']['content']
    if origin.get('kind') != 'git' or origin['url'] != track['repoUrl'] or origin['ref'] != track['ref']:
        raise AuditBlocked('local map does not match admitted upstream pin')
    url = track['repoUrl']
    if not re.fullmatch(r'https://github\.com/[\w.-]+/[\w.-]+\.git', url):
        raise AuditBlocked('local tracking requires GitHub HTTPS provenance')
    head = (target or discover_target(root, item_id, track))['ref']
    if not SHA40.fullmatch(head):
        raise AuditBlocked('invalid upstream head')
    if head == track['ref']:
        return None
    old_files, new_files, next_track = {}, {}, copy.deepcopy(track)
    # Mapping covers every package file other than separately generated governance/i18n bookkeeping.
    folder = root / 'skills' / item_id
    actual = {str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file()}
    if any(p.is_symlink() for p in folder.rglob('*')):
        raise AuditBlocked('local symlink rejected')
    if actual != set(track['files']) | {'catalog-metadata.v1.json', 'upstream-audit.v1.json'} - ({'upstream-audit.v1.json'} if not (folder/'upstream-audit.v1.json').exists() else set()):
        raise AuditBlocked('local package file inventory changed; review mapping')
    with tempfile.TemporaryDirectory(prefix='market-local-source-') as tmp:
        repo = Path(tmp)
        git(repo, 'init', '--quiet')
        git(repo, 'fetch', '--quiet', '--no-tags', '--depth=1', url, track['ref'], head)
        if (root_evidence(repo, track['ref']) != root_evidence(repo, head)
                or root_license_directory_files(repo, track['ref']) != root_license_directory_files(repo, head)):
            raise AuditBlocked('upstream root license/notice changed, including files outside the local mapping')
        for local, mapping in track['files'].items():
            safe_path(local)
            current_path = folder / local
            mode = '100755' if current_path.stat().st_mode & 0o111 else '100644'
            if mode != mapping['installedMode']:
                raise AuditBlocked('market file permission changed; rebaseline mapping')
            current = current_path.read_bytes()
            if digest(current) != mapping['installedSha256']:
                raise AuditBlocked('market wrapper/patch changed; rebaseline mapping')
            old_files[local] = new_files[local] = current
            if mapping.get('upstream'):
                source_path = safe_path(mapping['upstream'])
                before = source_blob(repo, track['ref'], source_path)
                after = source_blob(repo, head, source_path)
                modes = [git(repo, 'ls-tree', ref, '--', source_path).decode().split()[0] for ref in (track['ref'], head)]
                if modes[0] != modes[1] or modes[0] not in ('100644', '100755'):
                    raise AuditBlocked('upstream changed file type/permissions')
                if len(after) > MAX_FILE or digest(before) != mapping['upstreamSha256']:
                    raise AuditBlocked('upstream mapping hash/budget changed')
                # Never silently overwrite a local derivative, including translations and wrappers.
                if digest(current) != digest(before) and before != after:
                    raise AuditBlocked('upstream changed a locally patched file: ' + local + '; manual three-way reconciliation required')
                if before != after:
                    new_files[local] = after
                    next_track['files'][local]['installedSha256'] = digest(after)
                next_track['files'][local]['upstreamSha256'] = digest(after)
    if sum(map(len, new_files.values())) > MAX_BYTES:
        raise AuditBlocked('local package exceeds total audit budget')
    content = {**origin, 'ref': head}
    updated, report = audit_payload(None, metadata, old_files, new_files, track['ref'], head, content)
    next_track['ref'] = head
    changes = {f'skills/{item_id}/{p}': b for p, b in new_files.items() if b != old_files[p]}
    return changes, updated, report, next_track


def discover_target(root, item_id, track):
    if track['adapter'] == 'local-git':
        url = track['repoUrl']
        if not re.fullmatch(r'https://github\.com/[\w.-]+/[\w.-]+\.git', url):
            raise AuditBlocked('unsupported upstream')
        text = subprocess.run(['git', 'ls-remote', url, 'refs/heads/' + track['branch']], check=True, capture_output=True, text=True).stdout.split()
        if not text or not SHA40.fullmatch(text[0]):
            raise AuditBlocked('missing immutable upstream branch head')
        return {'ref': text[0]}
    entry = json.loads((root / 'skills' / item_id / 'entry.json').read_text())
    return discover(track, entry['source'])


def plan(root, item_id, cfg, target=None):
    folder = root / 'skills' / item_id
    if not SLUG.fullmatch(item_id) or (folder / 'upstream-health-hold.json').exists():
        raise AuditBlocked('invalid id or tracked hold; manual handling required')
    metadata = json.loads((folder / 'catalog-metadata.v1.json').read_text())
    track = cfg['tracking'][item_id]
    if track['adapter'] == 'local-git':
        result = local_plan(root, item_id, track, metadata, target)
        if result is None:
            return None
        changes, updated, report, next_track = result
        next_config = copy.deepcopy(cfg)
        next_config['tracking'][item_id] = next_track
        changes[CONFIG] = encoded(next_config)
    else:
        entry = json.loads((folder / 'entry.json').read_text())
        old = entry['source']
        origin = metadata.get('provenance', {}).get('content', {})
        if origin.get('url') != (old.get('repoUrl') or old.get('url')) or origin.get('kind') != old.get('kind'):
            raise AuditBlocked('artifact pointer/provenance mismatch')
        new = copy.deepcopy(target) if target is not None else discover(track, old)
        # A source kind/path change is NOT an automatic update.
        if old['kind'] != new['kind'] or old.get('path', '') != new.get('path', ''):
            raise AuditBlocked('source type/install scope changed; manual review required')
        if old.get('path'):
            raise AuditBlocked('non-root artifact scope requires a reviewed layout adapter')
        new_bytes = fetch(new['repoUrl'])
        new['sha256'] = digest(new_bytes)
        if old == new:
            return None
        old_bytes = fetch(old.get('repoUrl') or old['url'])
        before, after = unpack(old, old_bytes), unpack(new, new_bytes)
        updated, report = audit_payload(entry, metadata, before, after, old['sha256'], new['sha256'],
                                        {'kind': new['kind'], 'url': new['repoUrl'], 'sha256': new['sha256']})
        if report.get('observedVersions', {}).get(''):
            entry['latestVersion'] = report['observedVersions']['']
        entry['source'] = new
        changes = {f'skills/{item_id}/entry.json': encoded(entry)}
    changes[f'skills/{item_id}/catalog-metadata.v1.json'] = encoded(updated)
    changes[f'skills/{item_id}/upstream-audit.v1.json'] = encoded(report)
    return changes, report


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()
