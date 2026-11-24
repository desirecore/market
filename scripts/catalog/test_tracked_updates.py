"""Offline security/contract tests. Network and publication never run in this suite."""
import copy
import io
import json
import stat
import subprocess
import zipfile
from pathlib import Path
from unittest.mock import patch
import pytest
import tracked_updates as t
import merge_verified_updates as m
from audit_skill_update import git
from automated_review import validate_record


def archive(files):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        for path,data in files:
            z.writestr(path,data)
    return out.getvalue()


def unz(data,**kw):
    return t.unpack({'kind':'zip','sha256':t.digest(data),**kw},data)


@pytest.mark.parametrize('url',[
    'http://clawhub.ai/x','https://127.0.0.1/x','https://clawhub.ai.evil.invalid/x',
    'https://user:password@clawhub.ai/x','https://clawhub.ai:8080/x','file:///tmp/x',
    'https://clawhub.ai/x#fragment',
])
def test_untrusted_urls_rejected(url):
    with pytest.raises(t.AuditBlocked): t.allowed_url(url)


@pytest.mark.parametrize('path',['../x','/x','a/../x','a\\b','.git/config','.github/workflows/x.yml','a//x','C:/escape','folder/NUL.txt','folder/end.','folder/end '])
def test_zip_paths_rejected(path):
    with pytest.raises(t.AuditBlocked):unz(archive([('SKILL.md','x'),(path,'x')]))


def test_zip_layout_hash_and_missing_marker():
    data=archive([('pkg/SKILL.md','body'),('pkg/LICENSE','MIT fixture')])
    assert set(unz(data,path='pkg'))=={'SKILL.md','LICENSE'}
    with pytest.raises(t.AuditBlocked): unz(data)
    with pytest.raises(t.AuditBlocked): t.unpack({'kind':'zip','sha256':'0'*64},data)


def test_duplicate_and_case_collision_blocked():
    with pytest.raises(t.AuditBlocked):unz(archive([('SKILL.md','x'),('skill.md','y')]))


def test_zip_symlink_and_executable_rejected():
    for mode in (stat.S_IFLNK|0o777,stat.S_IFREG|0o755):
        item=zipfile.ZipInfo('SKILL.md');item.external_attr=mode<<16
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as z:z.writestr(item,'body')
        with pytest.raises(t.AuditBlocked):unz(out.getvalue())


def test_oversized_zip_rejected():
    with pytest.raises(t.AuditBlocked):unz(archive([('SKILL.md',b'x'*(t.MAX_FILE+1))]))


def test_registry_version_and_owner_are_verified_not_license_inferred():
    track={'adapter':'clawhub','slug':'sample','owner':'owner'}
    meta={'skill':{'slug':'sample'},'owner':{'handle':'owner'},'latestVersion':{'version':'1.2.3'},'license':'MIT-0'}
    with patch.object(t,'json_url',return_value=meta):
        result=t.discover(track,{'kind':'zip'})
    assert 'version=1.2.3' in result['repoUrl']
    assert 'license' not in result
    meta['owner']['handle']='different'
    with patch.object(t,'json_url',return_value=meta),pytest.raises(t.AuditBlocked):t.discover(track,{})


def test_github_file_uses_resolved_commit_not_branch_url():
    track={'adapter':'github-file','repo':'example/project','branch':'main','path':'SKILL.md'}
    with patch.object(t,'json_url',return_value={'sha':'a'*40}):result=t.discover(track,{'kind':'web'})
    assert '/'+('a'*40)+'/' in result['repoUrl']
    with patch.object(t,'json_url',return_value={'sha':'main'}),pytest.raises(t.AuditBlocked):t.discover(track,{})


def test_release_requires_unique_asset():
    track={'adapter':'github-release','repo':'example/project','asset':'skill.zip'}
    meta={'tag_name':'v1.0.0','assets':[{'name':'other.zip','browser_download_url':'https://example.invalid/x'}]}
    with patch.object(t,'json_url',return_value=meta),pytest.raises(t.AuditBlocked):t.discover(track,{})


def metadata(ref='a'*64,kind='zip'):
    content={'kind':kind,'url':'https://github.com/example/project/releases/download/v1/skill.zip',
             ('ref' if kind=='git' else 'sha256'):ref}
    return {'identity':{'kind':'skill','id':'sample'},'provenance':{'content':content},
            'governance':{'availability':'installable','license':{'state':'known','value':'MIT','evidencePath':'LICENSE'},
                          'compliance':{'licenseEvidencePath':'LICENSE','reviewedRef':ref,'reviewedBy':'previous-human','reviewedAt':'2026-11-01'}}}


def payload():
    return {'SKILL.md':b'---\nname: sample\ndescription: Sample fixture\n---\nInstructions\n',
            'LICENSE':b'MIT fixture, previously reviewed\n','scripts/tool.py':b'print("fixture")\n'}


def test_artifact_receipt_binds_real_digest_and_fresh_audit():
    before=payload();after={**before,'scripts/tool.py':b'print("changed")\n'}
    new={'kind':'zip','url':'https://github.com/example/project/releases/download/v2/skill.zip','sha256':'b'*64}
    updated,record=t.audit_payload(None,metadata(),before,after,'a'*64,'b'*64,new)
    assert not record['identicalInstalledPayload']
    assert record['source']['ref']=='b'*64
    assert updated['governance']['compliance']['reviewedRef']=='b'*64
    assert validate_record(updated,record)==[]
    broken=copy.deepcopy(record);broken['source']['previousRef']='a'*40
    assert validate_record(updated,broken)
    broken=copy.deepcopy(record);broken['checks']['licenseAndNoticeUnchanged']=False
    assert validate_record(updated,broken)


@pytest.mark.parametrize('change',[{'LICENSE':b'new terms'},{'NOTICE':b'new obligation'},
                                   {'requirements.txt':b'new-package==1.0\n'},
                                   {'SKILL.md':b'---\nname: sample\ndescription: new API required\n---\n'}])
def test_artifact_delta_cannot_invent_admission(change):
    before=payload();after={**before,**change}
    with pytest.raises(t.AuditBlocked):t.audit_payload(None,metadata(),before,after,'a'*64,'b'*64,
        {'kind':'zip','url':'https://clawhub.ai/download?v=2','sha256':'b'*64})


def test_listing_only_not_promoted():
    meta=metadata();meta['governance']['availability']='listing-only'
    with pytest.raises(t.AuditBlocked):t.audit_payload(None,meta,payload(),payload(),'a'*64,'b'*64,
        {'kind':'zip','url':'https://clawhub.ai/download?v=2','sha256':'b'*64})


def check(name,state='success',status='completed'):
    return {'id':1,'name':name,'status':status,'conclusion':state,
            'app':{'slug':'github-advanced-security' if name=='CodeQL' else 'github-actions'}}


def test_merge_requires_all_exact_head_checks_and_trusted_apps():
    good=[check('validate'),check('translate'),check('CodeQL')]
    required=['validate','translate','CodeQL']
    assert m.checks_pass(good,[],required)
    assert not m.checks_pass(good[:2],[],required)
    assert not m.checks_pass(good+[check('Analyze (python)','failure')],[],required)
    assert not m.checks_pass(good+[check('Copilot',None,'in_progress')],[],required)
    assert not m.checks_pass(good,[{'state':'pending'}],required)
    bad=copy.deepcopy(good);bad[0]['app']['slug']='another-app'
    assert not m.checks_pass(bad,[],required)


def test_labels_do_not_authorize_merge():
    fake={'state':'open','draft':False,'labels':[{'name':'automerge'}],
          'user':{'login':'other'},'base':{'ref':'main','repo':{'full_name':m.REPO}},
          'head':{'repo':{'full_name':m.REPO}}}
    assert not m.trusted_pr(fake)
    fake['user']['login']='mashagua';assert m.trusted_pr(fake)
    fake['head']['repo']['full_name']='someone/fork';assert not m.trusted_pr(fake)


def test_receipt_or_unsafe_patch_cannot_authorize_merge(tmp_path):
    (tmp_path/'skills'/'sample').mkdir(parents=True)
    pr={'state':'open','draft':False,'user':{'login':'mashagua'},'number':1,
        'base':{'ref':'main','repo':{'full_name':m.REPO}},
        'head':{'ref':'tracked-updates/sample-123','sha':'a'*40,'repo':{'full_name':m.REPO}}}
    with patch.object(m,'discover_target',return_value={}),patch.object(m,'plan',return_value=({}, {'identicalInstalledPayload':False})),pytest.raises(t.AuditBlocked):
        m.assess(tmp_path,pr,{'tracking':{'sample':{}}})
    with patch.object(m,'discover_target',return_value={}),patch.object(m,'plan',return_value=({}, {'identicalInstalledPayload':True})),patch.object(m,'pages',return_value=[{'filename':'.github/workflows/evil.yml','status':'added'}]),pytest.raises(t.AuditBlocked):
        m.assess(tmp_path,pr,{'tracking':{'sample':{}}})


def test_publisher_requires_actual_human_not_environment_name():
    with patch.object(t,'gh',return_value='github-actions[bot]'),pytest.raises(t.AuditBlocked):t.check_identity()
    with patch.object(t,'gh',return_value='mashagua'):t.check_identity()


def test_workflow_privileged_path_never_checks_out_candidate():
    root=Path(__file__).resolve().parents[2]
    workflow=(root/'.github/workflows/merge-verified-updates.yml').read_text()
    assert 'ref: main' in workflow and 'persist-credentials: false' in workflow
    assert 'pull_request_target:' not in workflow and 'head_sha' not in workflow
    code=(root/'scripts/catalog/merge_verified_updates.py').read_text()
    assert "'sha='+pr['head']['sha']" in code and '--admin' not in code


def test_server_must_enforce_up_to_date_exact_base():
    assert not m.strict_updates_required([])
    rule={'type':'required_status_checks','parameters':{'strict_required_status_checks_policy':True,
        'required_status_checks':[{'context':'validate'},{'context':'translate'}]}}
    assert m.strict_updates_required([rule])
    rule['parameters']['strict_required_status_checks_policy']=False
    assert not m.strict_updates_required([rule])


def local_fixture(tmp_path):
    source=tmp_path/'source';source.mkdir();git(source,'init','--quiet')
    for p,b in payload().items():
        f=source/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
    def commit():
        git(source,'add','--all')
        git(source,'-c','user.name=fixture','-c','user.email=fixture@example.invalid',
            '-c','commit.gpgsign=false','commit','--quiet','--allow-empty','-m','fixture')
        return git(source,'rev-parse','HEAD').decode().strip()
    old=commit()
    root=tmp_path/'market';folder=root/'skills'/'sample';folder.mkdir(parents=True)
    mapping={}
    for p,b in payload().items():
        f=folder/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
        mapping[p]={'upstream':p,'upstreamSha256':t.digest(b),'installedSha256':t.digest(b),'installedMode':'100644'}
    meta=metadata(old,'git');meta['provenance']['content']['url']='https://github.com/example/project.git'
    (folder/'catalog-metadata.v1.json').write_text(json.dumps(meta))
    track={'adapter':'local-git','repoUrl':meta['provenance']['content']['url'],'ref':old,'branch':'main','files':mapping}
    def fetch_local(repo,*args):
        if args[0]=='fetch':args=(*args[:4],str(source),*args[5:])
        return git(repo,*args)
    return source,root,track,meta,commit,fetch_local


def test_local_upstream_change_preserves_unmodified_market_wrapper(tmp_path):
    source,root,track,meta,commit,fetch_local=local_fixture(tmp_path)
    folder=root/'skills'/'sample';wrapper=folder/'wrapper.md';wrapper.write_text('market-only wrapper')
    track['files']['wrapper.md']={'installedSha256':t.digest(wrapper.read_bytes()),'installedMode':'100644'}
    (source/'scripts/tool.py').write_text('print("new upstream")\n');head=commit()
    with patch.object(t,'git',side_effect=fetch_local):
        changes,updated,report,next_track=t.local_plan(root,'sample',track,meta,{'ref':head})
    assert 'skills/sample/scripts/tool.py' in changes
    assert 'skills/sample/wrapper.md' not in changes
    assert wrapper.read_text()=='market-only wrapper'
    assert next_track['ref']==head and updated['governance']['compliance']['reviewedRef']==head
    assert not report['identicalInstalledPayload']


def test_local_patch_conflict_blocks_without_overwrite(tmp_path):
    source,root,track,meta,commit,fetch_local=local_fixture(tmp_path)
    file=root/'skills/sample/scripts/tool.py';file.write_text('market patch')
    track['files']['scripts/tool.py']['installedSha256']=t.digest(file.read_bytes())
    (source/'scripts/tool.py').write_text('upstream also changed');head=commit()
    with patch.object(t,'git',side_effect=fetch_local),pytest.raises(t.AuditBlocked,match='patched file'):
        t.local_plan(root,'sample',track,meta,{'ref':head})
    assert file.read_text()=='market patch'


def test_new_upstream_notice_outside_mapping_is_not_ignored(tmp_path):
    source,root,track,meta,commit,fetch_local=local_fixture(tmp_path)
    (source/'NOTICE').write_text('new obligation');head=commit()
    with patch.object(t,'git',side_effect=fetch_local),pytest.raises(t.AuditBlocked,match='root license/notice'):
        t.local_plan(root,'sample',track,meta,{'ref':head})


def test_local_unmapped_file_blocks(tmp_path):
    source,root,track,meta,commit,fetch_local=local_fixture(tmp_path)
    (root/'skills/sample/new-wrapper.md').write_text('unmapped')
    head=commit()
    with pytest.raises(t.AuditBlocked,match='inventory'):
        t.local_plan(root,'sample',track,meta,{'ref':head})


def test_artifact_old_provenance_cannot_be_rebound():
    meta=metadata();meta['provenance']['content']['sha256']='c'*64
    with pytest.raises(t.AuditBlocked,match='old provenance'):
        t.audit_payload(None,meta,payload(),payload(),'a'*64,'b'*64,
            {'kind':'zip','url':'https://clawhub.ai/download?v=2','sha256':'b'*64})


def test_candidate_cannot_self_authorize_with_same_path_json(tmp_path):
    (tmp_path/'skills'/'sample').mkdir(parents=True)
    pr={'state':'open','draft':False,'user':{'login':'mashagua'},'number':1,
        'base':{'ref':'main','repo':{'full_name':m.REPO}},
        'head':{'ref':'tracked-updates/sample-123','sha':'a'*40,'repo':{'full_name':m.REPO}}}
    expected={'skills/sample/upstream-audit.v1.json':t.encoded({'checks':{'licenseAndNoticeUnchanged':False}})}
    with patch.object(m,'discover_target',return_value={}),patch.object(m,'plan',return_value=(expected,{'identicalInstalledPayload':True})),patch.object(m,'pages',return_value=[{'filename':next(iter(expected)),'status':'modified'}]),patch.object(m,'read_json',return_value={'checks':{'licenseAndNoticeUnchanged':True}}),pytest.raises(t.AuditBlocked,match='differs from fresh'):
        m.assess(tmp_path,pr,{'tracking':{'sample':{}}})


def test_unicode_aliases_in_zip_are_not_silently_overwritten():
    with pytest.raises(t.AuditBlocked):
        unz(archive([('SKILL.md','body'),('é.md','one'),('e\u0301.md','two')]))


@pytest.mark.parametrize('branch,expected',[(None,'HEAD'),('master','refs/heads/master')])
def test_git_merge_gate_tracks_default_head_when_branch_not_declared(tmp_path,branch,expected):
    folder=tmp_path/'skills/sample';folder.mkdir(parents=True)
    source={'kind':'git','repoUrl':'https://github.com/example/project.git','ref':'a'*40}
    if branch:source['repoBranch']=branch
    (folder/'entry.json').write_text(json.dumps({'id':'sample','source':source}))
    (folder/'catalog-metadata.v1.json').write_text(json.dumps(metadata('a'*40,'git')))
    class Result:stdout='b'*40+'\tHEAD\n'
    with patch.object(m.subprocess,'run',return_value=Result()) as run, \
         patch.object(m,'audit_update',side_effect=t.AuditBlocked('stop after branch resolution')), \
         pytest.raises(t.AuditBlocked,match='branch resolution'):
        m.git_plan(tmp_path,'sample','b'*40)
    assert run.call_args.args[0][-1]==expected


def review_fixture():
    pr={'user':{'login':'mashagua'},'head':{'sha':'b'*40}}
    review={'user':{'login':'maintainer','type':'User'},'state':'APPROVED','commit_id':'b'*40,
            'body':'Inspected installed delta; no licensing, permission, dependency or scope expansion.\nmarket-reviewed-no-expansion: '+'b'*40}
    return pr,review


def test_changed_payload_requires_real_exact_head_maintainer_attestation():
    pr,review=review_fixture()
    with patch.object(m,'api',return_value={'permission':'write'}):assert m.reviewed_no_expansion(pr,[review])
    with patch.object(m,'api',return_value={'permission':'read'}):assert not m.reviewed_no_expansion(pr,[review])


@pytest.mark.parametrize('field,value',[
    ('commit_id','a'*40),('body','market-reviewed-no-expansion: '+'a'*40),
    ('state','COMMENTED'),('user',{'login':'mashagua','type':'User'}),
    ('user',{'login':'maintainer','type':'Bot'}),
])
def test_stale_fake_bot_or_self_review_cannot_authorize(field,value):
    pr,review=review_fixture();review[field]=value
    with patch.object(m,'api') as api:
        assert not m.reviewed_no_expansion(pr,[review]);api.assert_not_called()


def test_dismissed_or_requested_changes_invalidate_clearance():
    pr,review=review_fixture()
    for state in ('DISMISSED','CHANGES_REQUESTED'):
        with patch.object(m,'api') as api:
            assert not m.reviewed_no_expansion(pr,[review,{**review,'state':state}]);api.assert_not_called()


def test_status_reruns_use_latest_context_not_obsolete_failure():
    statuses=[{'id':2,'context':'external-ci','state':'success'},
              {'id':1,'context':'external-ci','state':'failure'}]
    assert m.checks_pass([check('validate')],statuses,['validate'])
    statuses.append({'id':3,'context':'external-ci','state':'pending'})
    assert not m.checks_pass([check('validate')],statuses,['validate'])


def test_workflow_rerun_replaces_obsolete_cancelled_run_only():
    runs=[{'id':1,'workflow_id':9,'status':'completed','conclusion':'cancelled'},
          {'id':2,'workflow_id':9,'status':'completed','conclusion':'success'}]
    assert m.workflow_runs_pass(runs)
    assert not m.workflow_runs_pass(runs+[{'id':3,'workflow_id':9,'status':'queued','conclusion':None}])
    assert not m.workflow_runs_pass(runs+[{'id':4,'workflow_id':10,'status':'completed','conclusion':'failure'}])
    assert not m.workflow_runs_pass([])


@pytest.mark.parametrize('path,before,after,expected', [
    ('SKILL.md', b'---\nname: demo\nversion: 1.0.0\n---\nKeep instructions.\n', b'---\nname: demo\nversion: 1.0.1\n---\nKeep instructions.\n', True),
    ('skills/demo/SKILL.md', b'---\nversion: "1.0.0"\n---\nBody\n', b'---\nversion: "1.0.1"\n---\nBody\n', True),
    ('SKILL.md', b'---\nversion: 1.0.0\n---\nOld', b'---\nversion: 1.0.1\n---\nNew', False),
    ('SKILL.md', b'---\nversion: 1.0.0\nrequiredClientVersion: 2.0.0\n---\nBody', b'---\nversion: 1.0.1\nrequiredClientVersion: 3.0.0\n---\nBody', False),
    ('SKILL.md', b'---\nversion: 1.0.0\nversion: 1.0.0\n---\nBody', b'---\nversion: 1.0.1\nversion: 1.0.0\n---\nBody', False),
    ('SKILL.md', b'---\nversion: unknown\n---\nBody', b'---\nversion: latest\n---\nBody', False),
    ('script.py', b'version: 1.0.0', b'version: 1.0.1', False),
    ('README.md', b'---\nversion: 1.0.0\n---\nBody', b'---\nversion: 1.0.1\n---\nBody', False),
])
def test_only_proven_top_level_skill_version_change_is_automatic(path, before, after, expected):
    assert t.version_only_change(before, after, path) is expected


def test_absent_inapplicable_language_jobs_do_not_block_but_present_failures_do():
    # Registry-only pointer diffs may never schedule CodeQL or all language jobs.
    mandatory=['validate','translate','wait-for-copilot-review']
    baseline=[check(name) for name in mandatory]
    assert m.checks_pass(baseline, [], mandatory)
    assert not m.checks_pass(baseline + [{**check('CodeQL'), 'conclusion':'failure'}], [], mandatory)
    assert not m.checks_pass(baseline + [{**check('Analyze (python)'), 'conclusion':'failure'}], [], mandatory)
    assert not m.checks_pass(baseline + [{**check('CodeQL'), 'status':'in_progress'}], [], mandatory)
