"""Independent bounded static findings, never upstream execution or admission receipts.

A finding is evidence about exact Git objects, not proof of a completed pipeline.
License-delivery checks intentionally fail closed on unrecognized grants.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import PurePosixPath

STATE = {'blocked': '阻断 / blocked', 'manual_review': '人工待审 / manual review',
         'not_checked': '未检查 / not checked', 'info': '说明 / information',
         'passed': '静态通过 / static pass'}
ORIGIN = {'pre_existing': '历史遗留 / pre-existing', 'introduced': '本次引入 / introduced',
          'changed': '本次变化 / changed', 'unchanged': '未变化 / unchanged',
          'unknown': '未确认 / unknown'}


def mit_grant(data):
    text = ' '.join(data.decode('utf-8', errors='replace').lower().split())
    return all(part in text for part in (
        'copyright', 'permission is hereby granted, free of charge',
        'to deal in the software without restriction',
        'the above copyright notice and this permission notice',
        'shall be included in all copies', 'the software is provided "as is"'))


def normalized(data):
    return re.sub(rb'\s+', b' ', data).strip()


def inspect_snapshots(repo, entry, metadata, result, special_review=None):
    # Lazy import avoids a circular module import; helpers only read bounded blobs.
    from audit_skill_update import git, blob, safe_path, GENERATOR, MAX_FILE_BYTES, MAX_FILES
    old, new = result['ref'], result['head']
    review = special_review or {}
    rows = []
    def add(path, gate, state, origin, reason, repair, evidence=None):
        rows.append(dict(id=entry['id'], path=path or '.', oldRef=old, newRef=new,
                         gate=gate, state=state, origin=origin, reason=reason,
                         repair=repair, evidence=evidence or {},
                         sourceUrl=entry['source']['repoUrl'].removesuffix('.git') + '/compare/' + old + '...' + new))
    def files(ref):
        found = {}
        for record in git(repo, 'ls-tree', '-rz', ref).split(b'\0'):
            if record:
                meta, path = record.split(b'\t', 1)
                mode, kind, oid = meta.decode().split()
                found[path.decode()] = (mode, kind, oid)
        if len(found) > 20000:
            raise ValueError('独立诊断仓库文件数超预算 / diagnostic tree exceeds budget')
        return found
    trees = {ref: files(ref) for ref in (old, new)}
    def read(ref, path):
        record = trees[ref].get(path)
        if not record or record[0] not in ('100644', '100755') or record[1] != 'blob':
            return b''
        if int(git(repo, 'cat-file', '-s', record[2])) > MAX_FILE_BYTES:
            return b''
        return blob(repo, ref, path)
    scopes = [safe_path(c['path']) for c in entry.get('children', [])]
    if not scopes:
        scopes = [safe_path(entry['source'].get('path', ''))]
    declared_scopes = set(scopes)
    discovered_children = GENERATOR.discover_children(repo, new) if entry.get('children') else []
    if discovered_children:
        scopes = sorted(set(scopes) | {safe_path(c['path']) for c in discovered_children})
    gov = metadata.get('governance', {})
    license_info = gov.get('license', {})
    evidence_path = safe_path(license_info.get('evidencePath') or gov.get('compliance', {}).get('licenseEvidencePath') or '')
    license_value = license_info.get('value')
    grants = {ref: read(ref, evidence_path) for ref in (old, new)}
    if license_value == 'MIT' and not mit_grant(grants[new]):
        add(evidence_path, 'pin-bound-license-exception', 'manual_review',
            'pre_existing' if not mit_grant(grants[old]) else 'introduced',
            'MIT 声明不是完整版权及许可通知；旧 pin 人工例外不得因字节未变而扩展到新 pin。 / An MIT declaration is not the full notice; an old-pin exception does not authorize a new pin even when bytes match.',
            '取得完整主许可通知，或由维护者明确审核并授权精确新 pin；不得由更新器改写 reviewedRef 冒充授权。 / Obtain the complete project notice or explicit human authorization for the exact new pin; never manufacture authorization by rebinding reviewedRef.',
            {'declaredLicense': license_value, 'evidencePath': evidence_path,
             'oldSha256': hashlib.sha256(grants[old]).hexdigest(), 'newSha256': hashlib.sha256(grants[new]).hexdigest()})
    for scope in scopes:
        def delivered(ref):
            grant = grants[ref]
            if not grant:
                return False, []
            # Only direct scope notice/readme/skill files qualify automatically.
            # A third-party vendor LICENSE cannot stand in for the main grant.
            candidates = []
            for path in trees[ref]:
                parent = str(PurePosixPath(path).parent)
                parent = '' if parent == '.' else parent
                name = PurePosixPath(path).name.upper()
                if parent == scope and (name.startswith(('LICENSE', 'COPYING', 'README', 'NOTICE')) or name == 'SKILL.MD'):
                    candidates.append(path)
            if len(candidates) > MAX_FILES:
                raise ValueError('许可候选超预算 / notice candidates exceed budget')
            exact = [p for p in candidates if normalized(grant) in normalized(read(ref, p))]
            return bool(exact) and (license_value != 'MIT' or mit_grant(grant)), exact
        old_ok, old_paths = delivered(old)
        new_ok, new_paths = delivered(new)
        if not new_ok:
            add(scope, 'installed-project-notice', 'blocked', 'pre_existing' if not old_ok else 'introduced',
                '未证明所选安装目录携带主项目完整通知；仓库根证据或 vendor 许可不等于安装交付。 / Complete project notice delivery is unverified in the selected directory; root evidence or a vendor license is not installed delivery.',
                '在不改变资源/选择/交付方式的前提下，由上游在原目录携带通知，或另行批准客户端确定性携带、摘要及锁记录方案并真实安装回读。嵌套或非标准等效通知可人工复核；不要伪造 LICENSE。 / Preserve scope/resources/delivery; upstream may include notices in-place, or separately authorize deterministic client notice staging with digest/lock and installation readback. Nonstandard or nested equivalents need human review; do not invent a LICENSE.',
                {'declaredLicense': license_value, 'requiredNoticePath': evidence_path,
                 'requiredNoticeSha256': hashlib.sha256(grants[new]).hexdigest(),
                 'requiredNoticeInsideScope': not scope or evidence_path.startswith(scope + '/'),
                 'oldDeliveredPaths': old_paths, 'newDeliveredPaths': new_paths,
                 'proof': 'bounded static scan of direct notice/README/SKILL files; not runtime acceptance'})
    declared_notice = gov.get('compliance', {}).get('noticePath')
    notice_paths = {p for p in trees[new] if '/' not in p and PurePosixPath(p).name.upper().startswith('NOTICE')}
    if declared_notice:
        notice_paths.add(safe_path(declared_notice))
    for notice in sorted(notice_paths):
        for scope in scopes:
            def notice_delivered(ref):
                required = read(ref, notice)
                if not required:
                    return False
                for path in trees[ref]:
                    parent = str(PurePosixPath(path).parent)
                    parent = '' if parent == '.' else parent
                    name = PurePosixPath(path).name.upper()
                    if parent == scope and (name.startswith(('LICENSE','COPYING','NOTICE','README')) or name == 'SKILL.MD'):
                        if normalized(required) in normalized(read(ref, path)):
                            return True
                return False
            if not notice_delivered(new):
                add(scope, 'installed-notice-delivery', 'blocked' if notice == declared_notice else 'manual_review',
                    'pre_existing' if not notice_delivered(old) else 'introduced',
                    '声明的 NOTICE 或仓库根 NOTICE 未证明随所选目录交付；未声明的根 NOTICE 适用性需保守人工确认。 / A declared or root NOTICE is not proven delivered with the selected directory; applicability of an undeclared root NOTICE requires conservative human review.',
                    '确认适用范围并保留完整通知；不能以根文件存在替代真实安装副本携带。 / Establish applicability and preserve complete notices; root-file existence is not installed delivery.',
                    {'requiredNoticePath':notice,'requiredNoticeSha256':hashlib.sha256(read(new,notice)).hexdigest(),
                     'declaredByCompliance':notice == declared_notice})
    # Use the exact parser used by collection discovery, not a hand-written YAML substitute.
    def fm_at(ref, path):
        try:
            raw = read(ref, path)
            fm = GENERATOR.parse_frontmatter_text(raw.decode('utf-8')) if raw else None
            return fm if isinstance(fm, dict) and fm else None
        except (ValueError, RuntimeError, OSError):
            return None
    markers = {ref: {p for p in trees[ref] if p.endswith('/SKILL.md') or p == 'SKILL.md'} for ref in (old, new)}
    if entry.get('children'):
        if len(markers[new]) > MAX_FILES:
            raise ValueError('SKILL 数量超预算 / SKILL marker budget exceeded')
        parsed = {ref: {p for p in markers[ref] if fm_at(ref, p)} for ref in (old, new)}
        discovered = {c['path'] for c in discovered_children}
        declared = declared_scopes
        accepted_members = set(review.get('acceptedCollectionPaths') or []) == discovered
        physical_added, physical_removed = sorted(markers[new] - markers[old]), sorted(markers[old] - markers[new])
        rediscovered = sorted((parsed[new] - parsed[old]) & markers[old])
        add('.', 'collection-inventory', 'info', 'changed' if physical_added or physical_removed or rediscovered else 'unchanged',
            f'市场登记 {len(declared)}；新 pin 可发现 {len(discovered)}；物理 SKILL {len(markers[old])}→{len(markers[new])}，新增 {len(physical_added)}、删除 {len(physical_removed)}。同路径恢复解析：{rediscovered}。不把恢复解析称为新增文件；未推断移动。 / Declared {len(declared)}; discoverable {len(discovered)}; physical SKILL files {len(markers[old])}→{len(markers[new])}, added {len(physical_added)}, removed {len(physical_removed)}. Rediscovered at existing paths: {rediscovered}. Rediscovery is not a new physical file; moves are not inferred.',
            '核对精确子项及双语派生目录；保留旧失败回执。 / Review exact children and bilingual derived metadata; preserve failed evidence.',
            {'physicalAdded': physical_added, 'physicalRemoved': physical_removed, 'rediscovered': rediscovered,
             'undeclared': sorted(discovered-declared), 'missing': sorted(declared-discovered)})
        for path in sorted(discovered ^ declared):
            marker = path + '/SKILL.md'
            add(path, 'collection-members', 'info' if accepted_members else 'blocked', 'pre_existing' if marker in markers[old] else 'introduced',
                '登记与解析集合不一致；文件原已存在。 / Declared/discovered mismatch; file already existed.' if marker in markers[old] else '登记与解析集合不一致；本次新增物理文件。 / Declared/discovered mismatch; physical file is newly added.',
                '逐项审核后同步 children 及两种语言，不把缺项自动准入。 / Review each item and synchronize children and both locales; never auto-admit missing members.')
        for path in sorted(markers[new]):
            if fm_at(new, path) is None:
                add(path, 'frontmatter-parse', 'blocked', 'pre_existing' if fm_at(old, path) is None and path in markers[old] else 'introduced',
                    'SKILL frontmatter 无法可靠解析。 / SKILL frontmatter cannot be parsed reliably.',
                    '修正 YAML 后重新发现；这不证明技能是新增加的。 / Fix YAML and rediscover; this does not prove a new skill was added.')
    # Descriptions are semantic, not automatic translations. Unchanged historical
    # English fallbacks are visible but not newly invented failures.
    for scope in scopes:
        marker = (scope + '/' if scope else '') + 'SKILL.md'
        before, after = fm_at(old, marker), fm_at(new, marker)
        if before and after and before.get('description') != after.get('description'):
            from audit_skill_update import frontmatter_identity
            accepted = review.get('acceptedFrontmatterSha256', {}).get(scope) == frontmatter_identity(after)
            has_locale_copy = bool(entry.get('i18n')) or any(c.get('path') == scope and any(v.get('shortDesc') for v in c.get('i18n', {}).values()) for c in entry.get('children', []))
            add(marker, 'description-and-locales', 'manual_review' if has_locale_copy or not accepted else 'info', 'changed',
                '上游简介变化；旧双语及派生简介不得默认为仍然准确。 / Upstream description changed; old bilingual and derived summaries require review.',
                '人工复核中英文及 entry/catalog 镜像；不能自动翻译或仅改 pin。 / Review both locales and entry/catalog mirrors; do not merely bump the pin or invent translations.',
                {'oldDescription': before.get('description'), 'newDescription': after.get('description')})
    children = {c['id']: c for c in entry.get('children', [])}
    for child in metadata.get('spec', {}).get('collection', {}).get('children', []):
        item = children.get(child.get('identity', {}).get('id'))
        if not item:
            continue
        for locale, text in item.get('i18n', {}).items():
            mirror = child.get('presentation', {}).get('i18n', {}).get(locale, {})
            if text.get('shortDesc') is not None and text['shortDesc'] != mirror.get('summary'):
                add(item['path'], 'derived-locales', 'blocked', 'pre_existing',
                    f'{locale} 的 entry 与 catalog 简介不一致。 / {locale} entry/catalog summaries differ.',
                    '同步实际审核后的派生文案。 / Synchronize reviewed derived copy.')
    for item in children.values():
        locales = item.get('i18n', {})
        zh = locales.get('zh-CN', {}).get('shortDesc')
        en = locales.get('en-US', {}).get('shortDesc')
        if zh and en and zh == en:
            add(item['path'], 'translation-fallback', 'info', 'pre_existing',
                '中英简介相同，属于已有英文回退，未声称已翻译。 / Identical summaries are an existing English fallback, not a claimed translation.',
                '需要时人工翻译；不要把历史回退误报成本次新增。 / Translate when needed; do not mislabel historical fallback as newly introduced.')
    # A plugin's explicit version is authoritative only for that plugin, not for
    # every unrelated number or every child skill version.
    for path in ('.claude-plugin/plugin.json', '.codex-plugin/plugin.json'):
        if path not in trees[new]:
            continue
        try:
            before = json.loads(read(old, path) or b'{}').get('version')
            after = json.loads(read(new, path)).get('version')
        except (ValueError, AttributeError):
            add(path, 'declared-version', 'manual_review', 'unknown', '插件清单无法可靠解析。 / Plugin manifest is not reliably parseable.', '人工核实版本来源。 / Verify the version source manually.')
            continue
        if not isinstance(after, str) or not re.fullmatch(r'\d+\.\d+\.\d+', after):
            continue
        # A root plugin version does not define the version of a selected subtree.
        root_fm = fm_at(new, 'SKILL.md') or {}
        root_metadata = root_fm.get('metadata') if isinstance(root_fm.get('metadata'), dict) else {}
        canonical_skill_version = GENERATOR.normalize_version(root_fm.get('version') or root_metadata.get('version'))
        if canonical_skill_version != after and not entry.get('children') and not entry['source'].get('path') and entry.get('latestVersion') and entry['latestVersion'] != after:
            add(path, 'declared-version', 'manual_review', 'changed' if before != after else 'pre_existing',
                f'登记版本 {entry["latestVersion"]} 与插件明确版本 {after} 不一致。 / Registered version {entry["latestVersion"]} differs from explicit plugin version {after}.',
                '审核并同步 entry/release，不以任意数字猜版本。 / Review and synchronize entry/release; never infer versions from arbitrary numbers.')
        if before and before != after:
            for container_name, container in (('entry', entry), ('catalog', metadata)):
                def walk(value, keys=()):
                    if isinstance(value, dict):
                        for key, child in value.items():
                            yield from walk(child, (*keys, key))
                    elif isinstance(value, list):
                        for index, child in enumerate(value):
                            yield from walk(child, (*keys, str(index)))
                    elif isinstance(value, str) and any(k in keys for k in ('description', 'shortDesc', 'summary')):
                        yield keys, value
                for keys, text in walk(container):
                    if re.search(r'(?<![\d.])v?' + re.escape(str(before)) + r'(?![\d.])', text):
                        add(container_name + '/' + '/'.join(keys), 'version-copy', 'manual_review', 'changed',
                            f'文案仍含明确旧插件版本 {before}，目标为 {after}；语义需人工确认。 / Copy still mentions explicit old plugin version {before}; target is {after}; semantic review is required.',
                            '核实其确为版本叙述后同步双语；不替换普通数字。 / Update both locales only after confirming this is a version claim; do not replace arbitrary numbers.',
                            {'versionSource':path,'oldVersion':before,'newVersion':after})
    # Complete Git-object manifests, not GitHub's capped comparison file list.
    def installed(ref):
        return {p: record for p, record in trees[ref].items()
                if any(not scope or p == scope or p.startswith(scope + '/') for scope in scopes)}
    old_installed, new_installed = installed(old), installed(new)
    changed_paths = sorted(p for p in old_installed.keys() | new_installed.keys()
                           if old_installed.get(p) != new_installed.get(p))
    if changed_paths:
        sensitive = [p for p in changed_paths if re.search(r'(auth|cookie|permission|credential|secret|env|config|http|network)', PurePosixPath(p).name, re.I)
                     and (PurePosixPath(p).suffix.lower() in ('.py','.js','.ts','.sh','.json') or PurePosixPath(p).name.startswith('.env'))]
        add('.', 'installed-content-delta', 'info', 'changed',
            f'直接比较完整 Git 对象：安装范围 {len(changed_paths)} 个路径变化；不是 GitHub 截断的 compare 列表，也不是行为审核通过。 / Complete Git-object comparison: {len(changed_paths)} installed paths changed; not a truncated GitHub compare list or a behavioral approval.',
            '按最终 SHA 复审实际指令/代码差异；现有自动合并行为审核门禁保持不变。 / Review actual instructions/code at the final SHA; existing behavioral merge clearance is unchanged.',
            {'changedPaths':changed_paths, 'physicalAdded':sorted(new_installed.keys()-old_installed.keys()),
             'physicalRemoved':sorted(old_installed.keys()-new_installed.keys()),
             'modeChanges':[p for p in changed_paths if p in old_installed and p in new_installed and old_installed[p][0]!=new_installed[p][0]],
             'comparisonComplete':True})
        if sensitive:
            add('.', 'authorization-config-network-review', 'manual_review', 'changed',
                '授权/凭据/配置/网络相关命名的实现文件发生变化；依赖哈希或普通元数据校验不能确认行为边界。这是保守人工复核提示，不是已证实漏洞。 / Implementation paths related by name to authorization, credentials, configuration or networking changed. Dependency hashes or metadata checks cannot establish behavioral bounds. This is a conservative review requirement, not a confirmed vulnerability.',
                '逐项检查凭据来源/保存、用户同意、网络端点与授权降级；另行记录真实最终 SHA 行为审核，不以依赖专项说明代替。 / Review credential access/storage, user consent, endpoints and authorization fallback; record genuine final-SHA behavioral review, not a dependency-only exception.',
                {'changedPaths':sensitive})
    # Root tooling is reported separately from installed runtime dependencies.
    old_package, new_package = read(old, 'package.json'), read(new, 'package.json')
    if old_package != new_package and new_package:
        try:
            a, b = json.loads(old_package or b'{}'), json.loads(new_package)
            for category in ('dependencies', 'devDependencies', 'optionalDependencies', 'peerDependencies'):
                if a.get(category, {}) != b.get(category, {}):
                    add('package.json#' + category, 'dependency-context', 'info', 'changed',
                        f'根清单 {category} 变化；不据此推断所选技能的运行时需求。 / Root manifest {category} changed; this alone does not establish installed-skill runtime requirements.',
                        '依赖门禁仍按精确对象审核；区分开发工具和实际运行依赖。 / Retain exact-object dependency review; distinguish development tools from runtime requirements.',
                        {'old': a.get(category, {}), 'new': b.get(category, {}), 'rootInsideSelectedScope': '' in scopes})
        except (ValueError, AttributeError):
            pass  # The core dependency parser blocks malformed manifests.
    deduplicated = {}
    for row in rows:
        key = (row['id'], row['path'], row['gate'], row['state'], row['reason'])
        if key not in deduplicated:
            deduplicated[key] = row
        elif row.get('evidence') != deduplicated[key].get('evidence'):
            deduplicated[key].setdefault('additionalEvidence', []).append(row['evidence'])
    return list(deduplicated.values())


def render_findings(rows):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', '<br>')
    out = ['| 技能/路径 / Skill/path | 精确旧→新 pin / Exact pins | 门槛 / Gate | 状态/来源 / State/origin | 原因及证据 / Reason/evidence | 修法 / Repair |', '|---|---|---|---|---|---|']
    for row in rows:
        evidence = json.dumps(row.get('evidence', {}), ensure_ascii=False, sort_keys=True)
        out.append('| ' + ' | '.join(cell(v) for v in (
            ('[' + row['id'] + '/' + row['path'] + '](' + row['sourceUrl'] + ')') if row.get('sourceUrl') else row['id'] + '/' + row['path'], row['oldRef'] + ' → ' + row['newRef'], row['gate'],
            STATE.get(row['state'], row['state']) + '; ' + ORIGIN.get(row['origin'], row['origin']),
            row['reason'] + (' ' + evidence if evidence != '{}' else ''), row['repair'])) + ' |')
    return '\n'.join(out)
