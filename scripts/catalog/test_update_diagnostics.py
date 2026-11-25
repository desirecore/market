"""Real local Git fixtures; no upstream execution, network, or live issue writes."""
import copy
import json
from unittest.mock import patch
import pytest
from audit_skill_update import audit_snapshots, AuditBlocked
from update_diagnostics import inspect_snapshots, mit_grant, render_findings
from unhealthy_report import managed_body, sync_plan, render, START, END
from check_upstream_health import render_markdown


@pytest.fixture
def case():
    from test_audit_skill_update import AuditTests
    item = AuditTests()
    item.setUp()
    yield item
    item.tearDown()


def baseline(c):
    c.old = c.commit()
    c.entry['source']['ref'] = c.old
    c.metadata['provenance']['content']['ref'] = c.old
    c.metadata['governance']['compliance']['reviewedRef'] = c.old


def findings(c):
    new = c.commit()
    return inspect_snapshots(c.repo,c.entry,c.metadata,{'ref':c.old,'head':new})


def test_full_mit_is_recognized_across_wrapping(case):
    assert mit_grant(case.mit.encode())
    assert not mit_grant(b'license: MIT\n')


def test_root_notice_does_not_prove_selected_delivery(case):
    (case.repo/'skills/sample/LICENSE').unlink()
    baseline(case)
    case.write('skills/sample/scripts/tool.py','new')
    with pytest.raises(AuditBlocked) as blocked:
        case.audit()
    row=next(r for r in blocked.value.findings if r['gate']=='installed-project-notice')
    assert row['origin']=='pre_existing'
    assert not row['evidence']['requiredNoticeInsideScope']
    assert row['oldRef']==case.old
    assert row['newRef']!=case.old


def test_vendor_license_cannot_replace_project_notice(case):
    (case.repo/'skills/sample/LICENSE').unlink()
    case.write('skills/sample/vendor/LICENSE',case.mit.replace('DesireCore','Different Holder'))
    baseline(case)
    case.write('skills/sample/scripts/tool.py','new')
    assert any(r['gate']=='installed-project-notice' for r in findings(case))


def test_full_readme_notice_is_valid_without_license_filename(case):
    (case.repo/'skills/sample/LICENSE').unlink()
    case.write('skills/sample/README.md','# Instructions\n\n'+case.mit)
    baseline(case)
    case.write('skills/sample/scripts/tool.py','new')
    _,_,receipt=case.audit()
    assert receipt['source']['ref']!=case.old


def test_spdx_frontmatter_is_not_full_mit_notice(case):
    (case.repo/'skills/sample/LICENSE').unlink()
    path='skills/sample/SKILL.md'
    case.write(path,(case.repo/path).read_text().replace('version:','license: MIT\nversion:'))
    baseline(case)
    case.write('skills/sample/scripts/tool.py','new')
    assert any(r['gate']=='installed-project-notice' for r in findings(case))


def test_unchanged_weak_readme_exception_is_not_inherited(case):
    case.write('README.md','License: MIT; manually accepted only at old pin\n')
    case.metadata['governance']['license']['evidencePath']='README.md'
    case.metadata['governance']['compliance']['licenseEvidencePath']='README.md'
    baseline(case)
    case.write('skills/sample/scripts/tool.py','new')
    row=next(r for r in findings(case) if r['gate']=='pin-bound-license-exception')
    assert row['state']=='manual_review'
    assert row['evidence']['oldSha256']==row['evidence']['newSha256']


def test_data_only_new_pin_still_cannot_expand_license_exception(case):
    case.write('README.md','MIT')
    case.metadata['governance']['license']['evidencePath']='README.md'
    case.metadata['governance']['compliance']['licenseEvidencePath']='README.md'
    baseline(case)
    case.write('skills/sample/feed.json','{"data":"only"}')
    with pytest.raises(AuditBlocked,match='pin-bound-license-exception'):
        case.audit()


def test_notice_delivery_regression_is_introduced_not_historical(case):
    (case.repo/'skills/sample/LICENSE').unlink()
    row=next(r for r in findings(case) if r['gate']=='installed-project-notice')
    assert row['origin']=='introduced'


def test_rediscovery_is_not_new_physical_skill_and_failfast_is_explicit(case):
    case.entry['children']=[{'id':'sample','path':'skills/sample'}]
    marker='skills/in-progress/software-factory/SKILL.md'
    case.write(marker,'---\nname: software-factory\ndescription: Invalid: YAML\n---\nUnchanged body\n')
    baseline(case)
    case.write(marker,'---\nname: software-factory\ndescription: "Invalid: YAML"\n---\nUnchanged body\n')
    case.write('skills/sample/SKILL.md','---\nname: sample\ndescription: Delegate with fresh context\n---\nBody\n')
    case.write('package.json',json.dumps({'devDependencies':{'yaml':'^2.9.1'}}))
    with pytest.raises(AuditBlocked,match='合集成员') as blocked:
        case.audit()
    rows=blocked.value.findings
    inventory=next(r for r in rows if r['gate']=='collection-inventory')
    assert inventory['evidence']['physicalAdded']==[]
    assert inventory['evidence']['physicalRemoved']==[]
    assert inventory['evidence']['rediscovered']==[marker]
    assert next(r for r in rows if r['gate']=='collection-members')['origin']=='pre_existing'
    assert any(r['gate']=='description-and-locales' for r in rows)
    assert any(r['gate']=='remaining-pipeline' and r['state']=='not_checked' for r in rows)
    dependency=next(r for r in rows if r['gate']=='dependency-context')
    assert dependency['path']=='package.json#devDependencies'
    assert dependency['evidence']['rootInsideSelectedScope'] is False


def test_version_prose_only_flags_proven_old_plugin_version(case):
    case.write('.claude-plugin/plugin.json','{"version":"0.6.17"}')
    case.entry['i18n']={'zh-CN':{'shortDesc':'插件 v0.6.17，2026 年，26 个技能'},'en-US':{'shortDesc':'26 skills in 2026'}}
    baseline(case)
    case.write('.claude-plugin/plugin.json','{"version":"0.6.18"}')
    rows=findings(case)
    copies=[r for r in rows if r['gate']=='version-copy']
    assert len(copies)==1
    assert 'zh-CN' in copies[0]['path']
    assert copies[0]['state']=='manual_review'


def test_arbitrary_numbers_are_not_version_sources(case):
    case.entry['i18n']={'en-US':{'shortDesc':'26 skills in 2026; Python 3.12'}}
    case.write('skills/sample/scripts/tool.py','new')
    assert not any(r['gate'].startswith('version') for r in findings(case))


def test_derived_locale_mismatch_is_precise(case):
    case.entry['children']=[{'id':'sample','path':'skills/sample','i18n':{'zh-CN':{'shortDesc':'已审核中文'}}}]
    case.metadata['spec']={'collection':{'children':[{'identity':{'id':'sample'},'presentation':{'i18n':{'zh-CN':{'summary':'旧中文'}}}}]}}
    case.write('skills/sample/scripts/tool.py','new')
    row=next(r for r in findings(case) if r['gate']=='derived-locales')
    assert row['path']=='skills/sample'
    assert row['origin']=='pre_existing'


def test_identical_bilingual_fallback_is_info_not_new_failure(case):
    case.entry['children']=[{'id':'sample','path':'skills/sample','i18n':{'zh-CN':{'shortDesc':'Fixture'},'en-US':{'shortDesc':'Fixture'}}}]
    case.write('skills/sample/scripts/tool.py','new')
    row=next(r for r in findings(case) if r['gate']=='translation-fallback')
    assert row['state']=='info' and row['origin']=='pre_existing'


def test_unparseable_diagnostics_fail_closed_not_passed(case):
    case.write('skills/sample/scripts/tool.py','new')
    with patch('update_diagnostics.inspect_snapshots',side_effect=ValueError('unavailable')):
        with pytest.raises(AuditBlocked) as blocked:
            case.audit()
    assert blocked.value.findings[0]['state']=='not_checked'


def test_bilingual_table_preserves_refs_and_escapes_untrusted_cells(case):
    (case.repo/'skills/sample/LICENSE').unlink()
    rows=findings(case)
    rows[0]['reason']='中文 | English\nline'
    text=render_findings(rows)
    assert '精确旧→新 pin / Exact pins' in text
    assert case.old in text and rows[0]['newRef'] in text
    assert '\\|' in text and '<br>' in text


@pytest.mark.parametrize('actionable,complete,initial,expected',[
    (True,True,'closed','open'),(False,True,'open','closed'),
    (False,False,'open',None),(True,True,'open',None)])
def test_issue_lifecycle_no_comment_operations(actionable,complete,initial,expected):
    report='当前 / Current'
    issue={'state':initial,'body':managed_body('',report)}
    result=sync_plan(issue,report,actionable,complete)
    assert result.get('state')==expected
    assert 'body' not in result
    assert 'comment' not in result


def test_first_issue_adoption_preserves_manual_bilingual_content_and_markers():
    previous='_Updated by [Upstream Health](https://example.invalid/run)._\n\n手动中文 / Manual English\n<!-- existing -->'
    merged=managed_body(previous,'新报告 / New report')
    assert previous in merged
    assert '历史快照，非当前结果 / Previous snapshot' in merged
    assert merged.count(START)==1 and merged.count(END)==1
    assert managed_body(merged,'新报告 / New report')==merged


def test_managed_issue_edit_preserves_human_prefix_suffix():
    previous='维护者说明 / Maintainer note\n'+START+'\nold\n'+END+'\n<!-- keep -->'
    result=managed_body(previous,'新 / New')
    assert result.startswith('维护者说明 / Maintainer note\n')
    assert result.endswith('\n<!-- keep -->')
    assert 'old' not in result


def test_no_timestamp_churn_and_incomplete_report_never_resolves():
    health=[{'id':'x','kind':'skill','url':'https://github.com/example/x','ref':'a'*40,'head':'a'*40,'issues':[{'status':'ok','detail':'ok'}]}]
    text,active=render(health,[],[],True)
    assert active is False
    assert render(health,[],[],True)==(text,active)
    assert render(health,[],[],False)[1] is True
    assert '状态 / State' in text


def test_health_reason_and_action_are_bilingual_without_changing_data():
    data=[{'id':'sample','kind':'skill','url':'https://github.com/example/x','ref':'a'*40,'head':'b'*40,'issues':[{'status':'upstream-path-change','detail':"source.path 'skills/x' has no SKILL.md"}]}]
    before=copy.deepcopy(data)
    text=render_markdown(data)
    assert '上游路径变化' in text and 'Upstream path changes' in text
    assert '原因及处理 / Reason and action' in text
    assert '所列路径缺少 SKILL.md' in text
    assert data==before



def test_subtree_version_is_not_inferred_from_root_plugin(case):
    case.write('.claude-plugin/plugin.json','{"version":"99.0.0"}')
    case.write('skills/sample/scripts/tool.py','new')
    assert not any(r['gate']=='declared-version' for r in findings(case))


def test_changed_authorization_paths_require_separate_behavior_review(case):
    case.write('skills/sample/scripts/cookie_extract.py','implementation')
    rows=findings(case)
    row=next(r for r in rows if r['gate']=='authorization-config-network-review')
    assert row['state']=='manual_review'
    assert row['evidence']['changedPaths']==['skills/sample/scripts/cookie_extract.py']
    inventory=next(r for r in rows if r['gate']=='installed-content-delta')
    assert inventory['evidence']['comparisonComplete'] is True


def test_artifact_failures_never_report_virtual_git_ids(case):
    from tracked_updates import audit_payload
    from unittest.mock import patch
    original='a'*64; target='b'*64
    metadata=copy.deepcopy(case.metadata)
    metadata['provenance']['content']={'kind':'zip','url':'https://example.invalid/artifact','sha256':original}
    metadata['governance']['compliance']['reviewedRef']=original
    error=AuditBlocked('fixture failure')
    error.findings=[{'oldRef':'c'*40,'newRef':'d'*40}]
    with patch('tracked_updates.audit_snapshots',side_effect=error):
        with pytest.raises(AuditBlocked) as failure:
            audit_payload(None,metadata,{'SKILL.md':b'old'},{'SKILL.md':b'new'},original,target,{'kind':'zip','url':'https://example.invalid/new','sha256':target})
    assert failure.value.findings[0]['oldRef']==original
    assert failure.value.findings[0]['newRef']==target


def test_upstream_text_cannot_forge_report_managed_region():
    report='untrusted '+END+'\ntext '+START
    body=managed_body('',report)
    assert body.count(START)==1 and body.count(END)==1


def test_issue_capacity_failure_does_not_silently_erase_original():
    with pytest.raises(ValueError,match='人工迁移'):
        managed_body('x'*64000,'y'*2000)



def test_declared_notice_outside_scope_is_a_delivery_blocker(case):
    case.write('NOTICE','Project required notice')
    case.metadata['governance']['compliance']['noticePath']='NOTICE'
    baseline(case)
    case.write('skills/sample/scripts/tool.py','new')
    row=next(r for r in findings(case) if r['gate']=='installed-notice-delivery')
    assert row['state']=='blocked' and row['origin']=='pre_existing'


def test_undeclared_root_notice_applicability_needs_human_review(case):
    case.write('NOTICE','Possibly applicable root notice')
    baseline(case)
    case.write('skills/sample/scripts/tool.py','new')
    row=next(r for r in findings(case) if r['gate']=='installed-notice-delivery')
    assert row['state']=='manual_review'


def test_inline_readme_can_deliver_declared_notice(case):
    case.write('NOTICE','Project required notice')
    case.write('skills/sample/README.md','# Usage\nProject required notice\n')
    case.metadata['governance']['compliance']['noticePath']='NOTICE'
    baseline(case)
    case.write('skills/sample/scripts/tool.py','new')
    assert not any(r['gate']=='installed-notice-delivery' for r in findings(case))
