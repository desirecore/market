"""自动来源审核回执的共享契约；生成与目录校验使用同一份绑定规则。"""
import re
from datetime import datetime
from pathlib import PurePosixPath

REVIEWER = 'automated:source-license-metadata-v1'
CHECKS = ('immutableSnapshots', 'installedScopeBoundedFiles', 'licenseAndNoticeUnchanged',
          'structuredPrerequisitesUnchanged', 'presentationMetadataUnchanged')


def validate_record(metadata: dict, record: dict) -> list[str]:
    errors = []
    if not isinstance(record, dict):
        return ['自动审核回执必须是对象']
    compliance = metadata.get('governance', {}).get('compliance', {})
    content = metadata.get('provenance', {}).get('content', {})
    if record.get('schemaVersion') != 1 or record.get('reviewer') != REVIEWER:
        errors.append('缺少受支持的机器审核身份/回执版本')
    if (metadata.get('identity', {}).get('kind') != 'skill' or content.get('kind') != 'git'
            or not isinstance(content.get('ref'), str) or not re.fullmatch('[0-9a-f]{40}', content['ref'])):
        errors.append('该机器审核契约仅适用于固定 Git Skill 来源')
    source = record.get('source', {})
    if not isinstance(source, dict) or source.get('url') != content.get('url') or source.get('ref') != content.get('ref'):
        errors.append('回执来源必须与当前 provenance 完全一致')
    elif not isinstance(source.get('previousRef'), str) or not re.fullmatch('[0-9a-f]{40}', source['previousRef']) or source.get('previousRef') == source.get('ref'):
        errors.append('回执必须绑定不同的旧、新固定快照')
    children = metadata.get('spec', {}).get('collection', {}).get('children', [])
    paths = [child.get('path') for child in children] if children else [content.get('path', '')]
    if not all(isinstance(path, str) for path in paths):
        errors.append('缺少受审核内容路径')
    else:
        expected_paths = sorted('' if str(PurePosixPath(path)) == '.' else str(PurePosixPath(path)) for path in paths)
        if not isinstance(source, dict) or source.get('paths') != expected_paths:
            errors.append('回执必须绑定当前 Skill 或合集成员的内容路径')
    reviewed = record.get('reviewedAt', '')
    try:
        datetime.strptime(reviewed, '%Y-%m-%dT%H:%M:%SZ')
    except (ValueError, TypeError):
        errors.append('自动审核时间无效')
    if not isinstance(reviewed, str) or reviewed[:10] != compliance.get('reviewedAt') or compliance.get('reviewedBy') != REVIEWER:
        errors.append('回执审核身份/日期与 compliance 不一致')
    checks = record.get('checks', {})
    if not isinstance(checks, dict) or any(checks.get(check) is not True for check in CHECKS):
        errors.append('自动审核必需检查未全部通过')
    evidence = record.get('licenseEvidenceSha256', {})
    if not isinstance(evidence, dict) or not evidence or any(not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value) for value in evidence.values()):
        errors.append('许可和 Notice 摘要证据无效')
    elif any(path not in evidence for path in [compliance.get('licenseEvidencePath'), compliance.get('noticePath')] if path):
        errors.append('缺少声明的许可或 Notice 文件摘要')
    if not isinstance(record.get('contentManifestSha256'), str) or not re.fullmatch('[0-9a-f]{64}', record['contentManifestSha256']):
        errors.append('缺少内容清单摘要')
    if type(record.get('fileCount')) is not int or record['fileCount'] < 1:
        errors.append('审核文件数量无效')
    if not isinstance(record.get('limitations'), list) or not record['limitations']:
        errors.append('必须披露自动核验的范围限制')
    return errors
