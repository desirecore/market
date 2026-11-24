#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Discover configured ZIP/Web/local updates; default is read-only planning."""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from tracked_updates import (AuditBlocked, CONFIG, LOGIN, EMAIL, check_identity, discover_target,
                             digest, encoded, gh, load_config, plan)

ROOT = Path(__file__).resolve().parents[2]


def publish(root, item_id, target, changes, reason=None):
    branch = f'tracked-updates/{item_id}-{digest(encoded(target))[:12]}'
    open_heads = json.loads(gh('pr', 'list', '--repo', 'desirecore/market', '--state', 'open', '--limit', '1000', '--json', 'headRefName'))
    if any(p['headRefName'].startswith(f'tracked-updates/{item_id}-') for p in open_heads):
        return 'already-open'
    if json.loads(gh('pr', 'list', '--repo', 'desirecore/market', '--state', 'all', '--head', branch, '--json', 'number')):
        return 'already-proposed'
    check_identity()
    with tempfile.TemporaryDirectory(prefix='market-tracked-proposal-') as tmp:
        checkout = Path(tmp) / 'worktree'
        subprocess.run(['git', 'worktree', 'add', '--detach', str(checkout), 'HEAD'], cwd=root, check=True, capture_output=True)
        try:
            original = {relative: (checkout/relative).read_bytes() if (checkout/relative).exists() else None for relative in changes}
            for relative, data in changes.items():
                p = checkout / relative
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
            if reason is None:
                commands = [
                    ['uv','run','scripts/catalog/validate_catalog_metadata.py','--require-complete'],
                    ['uv','run','scripts/i18n/validate-i18n.py',f'skills/{item_id}'],
                    ['uv','run','scripts/i18n/translate.py','--check',f'skills/{item_id}'],
                ]
                for cmd in commands:
                    result = subprocess.run(cmd, cwd=checkout, capture_output=True)
                    if result.returncode:
                        # Restore only our own disposable files; never publish a failed admission.
                        for relative, baseline in original.items():
                            p = checkout / relative
                            if baseline is None:
                                p.unlink(missing_ok=True)
                            else:
                                p.write_bytes(baseline)
                        reason = 'generated proposal failed repository/i18n validation; unchanged admission retained'
                        path = f'docs/update-reviews/{item_id}.json'
                        changes = {path: encoded({'schemaVersion':1,'status':'blocked','id':item_id,'candidate':target,'reason':reason})}
                        p = checkout / path
                        p.parent.mkdir(parents=True, exist_ok=True)
                        p.write_bytes(changes[path])
                        break
            subprocess.run(['git','add','--',*changes], cwd=checkout, check=True)
            subprocess.run(['git','-c',f'user.name={LOGIN}','-c',f'user.email={EMAIL}',
                            'commit','-m',f'chore(market): review tracked {item_id} update'], cwd=checkout, check=True, capture_output=True)
            subprocess.run(['git','push','origin',f'HEAD:refs/heads/{branch}'], cwd=checkout, check=True, capture_output=True)
            body = Path(tmp) / 'body.md'
            body.write_text(f'Configured upstream update for `{item_id}`.\n\n'
                + ('Blocked: '+reason if reason else 'Pinned old/new payloads passed the existing license, prerequisite and metadata delta audit. This is not runtime/security certification.')
                + '\n\nMarket wrappers and patches are preserved. Content-changing updates require an exact-head human maintainer no-expansion review; identical installed payloads need no additional behavioral clearance. The separate trusted gate always reaudits bytes and checks.\n')
            args = ['pr','create','--repo','desirecore/market','--base','main','--head',branch,
                    '--title',f'chore(market): review {item_id} tracked upstream','--body-file',str(body)]
            if reason:
                args += ['--draft']
            return gh(*args)
        finally:
            # Remove only the disposable worktree created above, never a user's checkout.
            subprocess.run(['git','worktree','remove','--force',str(checkout)], cwd=root, check=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--limit', type=int, default=5)
    args=parser.parse_args()
    if args.limit < 1:
        parser.error('--limit must be positive')
    if args.publish:
        check_identity()
    cfg=load_config(ROOT)
    attempted=0
    for item_id, track in cfg['tracking'].items():
        if attempted >= args.limit:
            break
        target=None
        publication_attempted=False
        try:
            if (ROOT/'skills'/item_id/'upstream-health-hold.json').exists():
                print(item_id, 'held; not advancing')
                continue
            target=discover_target(ROOT,item_id,track)
            if track['adapter']=='local-git' and target['ref']==track['ref']:
                print(item_id,'current')
                continue
            result=plan(ROOT,item_id,cfg,target)
            if result is None:
                print(item_id,'current')
                continue
            changes,report=result
            print(item_id,'audited',report['source']['ref'])
            if args.publish:
                attempted+=1
                publication_attempted=True
                print(publish(ROOT,item_id,target,changes))
        except (AuditBlocked, ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
            reason=str(exc) if isinstance(exc,AuditBlocked) else 'discovery/fetch/validation failed: '+type(exc).__name__
            print(item_id,'BLOCKED:',reason)
            if args.publish and target is not None and not publication_attempted:
                attempted+=1
                path=f'docs/update-reviews/{item_id}.json'
                changes={path:encoded({'schemaVersion':1,'status':'blocked','id':item_id,'candidate':target,'reason':reason})}
                print(publish(ROOT,item_id,target,changes,reason))


if __name__=='__main__':
    main()
