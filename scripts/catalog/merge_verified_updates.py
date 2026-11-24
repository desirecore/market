#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Trusted-base, fail-closed exact-head update merge gate. Labels/receipts are NOT authority.

Never checkout/import/run PR files. Recompute proposals from main plus independently
fetched upstream bytes, then compare the entire proposed diff. No admin bypass.
"""
from __future__ import annotations
import argparse
import base64
import copy
import json
import subprocess
import tempfile
from pathlib import Path
from audit_skill_update import AuditBlocked, audit_update, git, tree
from automated_review import validate_record
from tracked_updates import CONFIG, LOGIN, check_identity, discover_target, gh, load_config, plan

ROOT = Path(__file__).resolve().parents[2]
REPO = 'desirecore/market'


def api(path):
    return json.loads(gh('api',path))


def pages(path, field=None):
    result=json.loads(gh('api','--paginate','--slurp',path))
    return [item for page in result for item in (page[field] if field else page)]


def read_json(ref,path):
    obj=api(f'repos/{REPO}/contents/{path}?ref={ref}')
    if obj.get('encoding')!='base64':
        raise AuditBlocked('candidate metadata is not a bounded file')
    return json.loads(base64.b64decode(obj['content']))


def canonical(value):
    result=copy.deepcopy(value)
    if not isinstance(result,dict):
        return result
    if 'reviewedAt' in result:
        result['reviewedAt']='<audit-time>'
    if 'governance' in result:
        result['governance']['compliance']['reviewedAt']='<audit-day>'
    for key in ('reviewedAt','catalogUpdatedAt','upstreamObservedAt'):
        field=result.get('timestamps',{}).get(key)
        if isinstance(field,dict) and 'value' in field:
            field['value']='<audit-time>'
    return result


def checks_pass(checks, statuses, required):
    by_name={c['name']:c for c in sorted(checks,key=lambda c:c.get('id',0))}
    if not set(required)<=set(by_name):
        return False
    for name in required:
        app='github-advanced-security' if name=='CodeQL' else 'github-actions'
        if by_name[name].get('app',{}).get('slug')!=app:
            return False
    # Every applicable check/context, not only required names, must be finished and green.
    return (bool(checks) and all(c.get('status')=='completed' and c.get('conclusion')=='success' for c in by_name.values())
            and all(s.get('state')=='success' for s in statuses))


def trusted_pr(pr):
    return (pr.get('state')=='open' and not pr.get('draft') and not pr.get('merged')
            and pr.get('user',{}).get('login')==LOGIN and pr.get('base',{}).get('ref')=='main'
            and pr.get('base',{}).get('repo',{}).get('full_name')==REPO
            and pr.get('head',{}).get('repo',{}).get('full_name')==REPO)


def git_plan(root,item_id,head):
    folder=root/'skills'/item_id
    entry=json.loads((folder/'entry.json').read_text())
    metadata=json.loads((folder/'catalog-metadata.v1.json').read_text())
    source=entry['source']
    remote=subprocess.run(['git','ls-remote',source['repoUrl'],('refs/heads/'+source['repoBranch']) if source.get('repoBranch') else 'HEAD'],check=True,capture_output=True,text=True).stdout.split()
    if not remote or remote[0]!=head:
        raise AuditBlocked('upstream HEAD moved; a fresh proposal/audit is required')
    review_path=folder/'special-review.v1.json'
    review=json.loads(review_path.read_text()) if review_path.exists() else None
    if review and (review.get('excludePaths') or any(k.startswith('accepted') for k in review)):
        raise AuditBlocked('special exceptions require human review, not automatic merge')
    updated,sidecar,report=audit_update(entry,metadata,{'ref':source['ref'],'head':head},special_review=review)
    # Do not infer unchanged payload from the PR's own JSON. Read actual pinned trees.
    with tempfile.TemporaryDirectory(prefix='market-merge-delta-') as tmp:
        repo=Path(tmp)
        git(repo,'init','--quiet')
        git(repo,'fetch','--quiet','--no-tags','--depth=1',source['repoUrl'],source['ref'],head)
        paths=[c['path'] for c in entry.get('children',[])] or [source.get('path','')]
        budgets=(review or {}).get('budgetExemptPaths',[])
        if any(tree(repo,source['ref'],p,[],budgets)!=tree(repo,head,p,[],budgets) for p in paths):
            raise AuditBlocked('installed payload changed: manual behavioral/permission review required')
    return {f'skills/{item_id}/entry.json':updated,f'skills/{item_id}/catalog-metadata.v1.json':sidecar,
            f'skills/{item_id}/upstream-audit.v1.json':report}


def assess(root,pr,cfg):
    if not trusted_pr(pr):
        raise AuditBlocked('not a designated-maintainer same-repository update PR')
    branch=pr['head']['ref']
    prefix='tracked-updates/' if branch.startswith('tracked-updates/') else 'updates/'
    if not branch.startswith(prefix):
        raise AuditBlocked('not an update branch')
    # Bind id against trusted main's real IDs; never derive arbitrary filesystem paths.
    ids=[p.name for p in (root/'skills').iterdir() if p.is_dir()]
    matches=[i for i in ids if branch.startswith(prefix+i+'-')]
    if len(matches)!=1:
        raise AuditBlocked('ambiguous/unregistered update id')
    item_id=matches[0]
    if (root/'skills'/item_id/'upstream-health-hold.json').exists():
        raise AuditBlocked('held update')
    if prefix=='tracked-updates/':
        target=discover_target(root,item_id,cfg['tracking'][item_id])
        result=plan(root,item_id,cfg,target)
        if result is None or result[1].get('identicalInstalledPayload') is not True:
            raise AuditBlocked('installed payload changed or proposal stale; manual review required')
        expected={p:json.loads(b) if p.endswith('.json') else b for p,b in result[0].items()}
    else:
        proposed=read_json(pr['head']['sha'],f'skills/{item_id}/entry.json')
        expected=git_plan(root,item_id,proposed['source']['ref'])
    files=pages(f"repos/{REPO}/pulls/{pr['number']}/files?per_page=100")
    if len(files)!=len(expected) or {f['filename'] for f in files}!=set(expected) or any(f['status'] in ('removed','renamed') for f in files):
        raise AuditBlocked('candidate diff differs from independently regenerated scope')
    for path,value in expected.items():
        if canonical(read_json(pr['head']['sha'],path))!=canonical(value):
            raise AuditBlocked('candidate content differs from fresh trusted-base audit')
    metadata=read_json(pr['head']['sha'],f'skills/{item_id}/catalog-metadata.v1.json')
    report=read_json(pr['head']['sha'],f'skills/{item_id}/upstream-audit.v1.json')
    if validate_record(metadata,report):
        raise AuditBlocked('candidate receipt binding is invalid')
    return True


def strict_updates_required(rules):
    for rule in rules:
        params = rule.get('parameters') or {}
        names = {c.get('context') for c in params.get('required_status_checks', [])}
        if (rule.get('type') == 'required_status_checks'
                and params.get('strict_required_status_checks_policy') is True
                and {'validate', 'translate'} <= names):
            return True
    return False


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--merge',action='store_true')
    args=parser.parse_args()
    if args.merge:
        check_identity()
    cfg=load_config(ROOT)
    base=api(f'repos/{REPO}/branches/main')['commit']['sha']
    local=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
    if local!=base:
        raise AuditBlocked('trusted checkout is not current main; rerun on fresh main')
    for summary in pages(f'repos/{REPO}/pulls?state=open&base=main&per_page=100'):
        if not summary.get('head',{}).get('ref','').startswith(('updates/','tracked-updates/')):
            continue
        number=summary['number']
        try:
            pr=api(f'repos/{REPO}/pulls/{number}')
            if pr.get('mergeable') is not True or pr.get('mergeable_state')!='clean':
                raise AuditBlocked('not clean/up-to-date; protection/review/checks may block')
            comparison=api(f"repos/{REPO}/compare/{base}...{pr['head']['sha']}")
            if comparison.get('behind_by')!=0 or comparison.get('merge_base_commit',{}).get('sha')!=base:
                raise AuditBlocked('behind main; normal branch update and fresh checks required')
            assess(ROOT,pr,cfg)
            checks=pages(f"repos/{REPO}/commits/{pr['head']['sha']}/check-runs?filter=latest&per_page=100",'check_runs')
            statuses=pages(f"repos/{REPO}/commits/{pr['head']['sha']}/statuses?per_page=100")
            runs=pages(f"repos/{REPO}/actions/runs?head_sha={pr['head']['sha']}&per_page=100",'workflow_runs')
            if not runs or any(r.get('status')!='completed' or r.get('conclusion')!='success' for r in runs):
                raise AuditBlocked('exact-head workflow runs are unfinished/not successful')
            latest={}
            for review in pages(f'repos/{REPO}/pulls/{number}/reviews?per_page=100'):
                if review['state'] in ('APPROVED','CHANGES_REQUESTED','DISMISSED'):
                    latest[review['user']['login']]=review['state']
            if 'CHANGES_REQUESTED' in latest.values() or not checks_pass(checks,statuses,cfg['requiredChecks']):
                raise AuditBlocked('review or exact-head checks are incomplete/not successful')
            fresh=api(f'repos/{REPO}/pulls/{number}')
            if (not trusted_pr(fresh) or fresh.get('mergeable') is not True or fresh.get('mergeable_state')!='clean'
                    or fresh['head']['sha']!=pr['head']['sha']) or api(f'repos/{REPO}/branches/main')['commit']['sha']!=base:
                raise AuditBlocked('head/base moved; rerun audit for the new SHA')
            print(number,'eligible unchanged-payload update',pr['head']['sha'])
            if args.merge:
                # GitHub must atomically reject a behind-base merge if main moves after our final read.
                if not strict_updates_required(api(f'repos/{REPO}/rules/branches/main')):
                    raise AuditBlocked('strict server-side up-to-date/check rules required; no bypass')
                check_identity()
                result=json.loads(gh('api','--method','PUT',f'repos/{REPO}/pulls/{number}/merge',
                    '-f','merge_method=squash','-f','sha='+pr['head']['sha']))
                if not result.get('merged'):
                    raise AuditBlocked('GitHub protection rejected merge; no bypass')
                print(number,'merged',result['sha'])
                break  # main moved. Next run must recompute every remaining candidate.
        except (AuditBlocked,KeyError,ValueError,OSError,subprocess.SubprocessError) as exc:
            print(number,'held:',str(exc) if isinstance(exc,AuditBlocked) else type(exc).__name__)


if __name__=='__main__':
    main()
