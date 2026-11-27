#!/usr/bin/env python3
"""Bilingual exact-evidence report and idempotent existing-issue lifecycle.

Only trusted default-branch workflows run this. Does not execute upstream code,
change admission receipts, create PRs, merge, or post issue comments.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from check_upstream_health import render_markdown, summarize
from update_diagnostics import render_findings

START = '<!-- market-upstream-health:begin -->'
END = '<!-- market-upstream-health:end -->'
TITLE = '上游健康与更新审核报告 / Upstream health and update audit report'
GUIDE = ('通过普通 PR 修正来源/路径、审核精确目标 pin 及安装通知；失败保持草稿，不重绑旧回执。网络未知或预算未覆盖不等于通过。\n\n'
         'Use normal PRs to fix sources/paths and review exact target pins and installed notices. Failures stay drafts; never rebind old receipts. Unknown network status or unreviewed budget overflow is not a pass.')


REPORT_HEADER_LABEL = '**报告生成时间（北京时间） / Report generated (Beijing time):** '


def report_header(generated_at, env):
    beijing = generated_at.astimezone(timezone(timedelta(hours=8)))
    stamp = beijing.strftime('%Y-%m-%d %H:%M:%S')
    header = f'{REPORT_HEADER_LABEL}{stamp} (UTC+08:00)'
    repo, run_id = env.get('GITHUB_REPOSITORY'), env.get('GITHUB_RUN_ID', '')
    if repo and run_id.isascii() and run_id.isdecimal():
        server = env.get('GITHUB_SERVER_URL', 'https://github.com').rstrip('/')
        run_url = f'{server}/{repo}/actions/runs/{run_id}'
        attempt = env.get('GITHUB_RUN_ATTEMPT', '')
        if attempt.isascii() and attempt.isdecimal():
            run_url += f'/attempts/{attempt}'
        header += f' · [本次运行 / Workflow run]({run_url})'
    return header


def render(results, coverage, tracked, complete=True, *, header=None):
    rows = []
    for item in [*coverage, *tracked]:
        if not item.get('parentId'):
            rows.extend(item.get('findings', []))
    out = [header, ''] if header else []
    out += [GUIDE, '', render_markdown(results), '', '## 更新审核结果 / Update audit results', '',
           '完整逐项证据见同次 Actions 的 audit-results 工件；本报告不代表运行验收。 / Complete per-item evidence is in the audit-results artifact of the same Actions run; this report is not runtime acceptance.', '',
           '| 技能 / Skill | 状态 / State | 精确旧→新 pin / Exact pins | 原因 / Reason |', '|---|---|---|---|']
    labels = {'audit-passed':'静态审核通过 / static audit passed', 'manual-review-required':'人工待审 / manual review',
              'queued':'预算内未轮到，未审核 / queued, not audited', 'already-open':'已有 PR，本轮未重审 / existing PR, not re-audited',
              'already-proposed':'同 pin 已提案，本轮未重审 / same pin already proposed, not re-audited',
              'publish-failed':'发布失败 / publishing failed', 'not-checked':'未检查 / not checked',
              'held':'已暂缓 / held', 'current':'来源无待处理更新 / source current'}
    for row in [r for r in coverage if not r.get('parentId') and r['status'] not in ('current','market-release')] + tracked:
        reason = str(row.get('reason', '')).split('\n')[0].replace('|', '\\|')
        out.append(f"| {row['id']} | {labels.get(row['status'], '需按原始详情复核 / see evidence: ' + row['status'])} | {row.get('oldRef', '未读取 / not read')} → {row.get('newRef', '未读取 / not read')} | {reason} |")
    if rows:
        out.extend(['', '## 精确失败与独立静态发现 / Exact failures and independent static findings', '', render_findings(rows)])
    if not complete:
        out.extend(['', '**本轮不完整，不能闭环为已解决。 / This run is incomplete; it cannot resolve the issue.**'])
    text = '\n'.join(out)
    # Keep the full structured report as an artifact; never silently claim that
    # omitted diagnostics passed or fabricate a shortened receipt.
    if len(text) > 42000:
        text = text[:41000].rsplit('\n', 1)[0] + '\n\n展示已截断，完整证据必须查看 audit-results 工件；不是检查通过。 / Display truncated; consult the complete audit-results artifact. This is not a pass.\n'
    pending = any(r['status'] not in ('current', 'market-release', 'audit-passed', 'held', 'governance-blocked', 'requires-version-feed')
                  for r in [*coverage, *tracked] if not r.get('parentId'))
    summary = summarize(results)
    actionable = not complete or pending or summary['actionable'] or summary['unknown']
    return text, bool(actionable)


def managed_body(previous, report):
    safe_report = report.replace(START, '&lt;!-- market-upstream-health:begin --&gt;').replace(END, '&lt;!-- market-upstream-health:end --&gt;')
    managed = START + '\n' + safe_report.strip() + '\n' + END
    if START in previous and END in previous:
        prefix, rest = previous.split(START, 1)
        _, suffix = rest.split(END, 1)
        return prefix + managed + suffix
    if previous.strip():
        # First adoption preserves the hand-translated issue as an explicitly
        # historical snapshot. Never silently erase human text or markers.
        archive = '\n\n<details><summary>历史快照，非当前结果 / Previous snapshot, not current results</summary>\n\n' + previous.strip() + '\n\n</details>\n'
        if len(managed + archive) > 65000:
            raise ValueError('保留现有正文会超出 issue 上限；需人工迁移 / issue preservation requires manual migration')
        return managed + archive
    return managed + '\n'


def without_generated_header(body):
    prefix, marker, managed = body.partition(START + '\n')
    header, newline, rest = managed.partition('\n')
    if marker and newline and header.startswith(REPORT_HEADER_LABEL) and END in rest:
        return prefix + marker + rest
    return None


def sync_plan(issue, report, actionable, complete):
    previous = issue.get('body') or ''
    body = managed_body(previous, report)
    edits = {}
    # The issue links to the run that generated the content it displays.
    # A report without a header still gets one on its first publish.
    if body != previous:
        previous_content = without_generated_header(previous)
        if previous_content is None or previous_content != without_generated_header(body):
            edits['body'] = body
    if actionable and issue['state'] == 'closed':
        edits['state'] = 'open'
    elif not actionable and complete and issue['state'] == 'open':
        edits['state'] = 'closed'
        edits['state_reason'] = 'completed'
    return edits


def gh(*args):
    return json.loads(subprocess.run(['gh', *args], check=True, capture_output=True, text=True).stdout or 'null')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results', type=Path, required=True)
    p.add_argument('--coverage', type=Path, required=True)
    p.add_argument('--tracked', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--complete', action='store_true')
    p.add_argument('--publish', action='store_true')
    a = p.parse_args()
    complete = a.complete and all(path.is_file() for path in (a.results, a.coverage, a.tracked))
    results, coverage, tracked = [json.loads(path.read_text()) if path.is_file() else [] for path in (a.results, a.coverage, a.tracked)]
    header = report_header(datetime.now(timezone.utc), os.environ)
    report, actionable = render(results, coverage, tracked, complete, header=header)
    a.output.write_text(report + '\n')
    if not a.publish:
        return
    repo = os.environ.get('GITHUB_REPOSITORY')
    if repo != 'desirecore/market':
        raise ValueError('仅官方仓库可同步 issue / only the official repository may sync issues')
    issues = gh('issue', 'list', '--repo', repo, '--label', 'upstream-health', '--state', 'all', '--limit', '100', '--json', 'number,title,body,state')
    compatible = [i for i in issues if START in (i.get('body') or '') or i['title'] in (TITLE, 'Upstream health report')]
    if len(compatible) > 1 or (issues and not compatible):
        raise ValueError('跟踪 issue 不唯一或无法识别，需人工确认 / tracking issue is ambiguous; manual review required')
    if compatible:
        issue = gh('api', 'repos/' + repo + '/issues/' + str(compatible[0]['number']))
        edits = sync_plan(issue, report, actionable, complete)
        if edits:
            # stdin JSON avoids shell interpolation; one edit, zero comments.
            subprocess.run(['gh', 'api', '--method', 'PATCH', 'repos/' + repo + '/issues/' + str(issue['number']), '--input', '-'], input=json.dumps(edits), text=True, check=True, capture_output=True)
    elif actionable:
        subprocess.run(['gh', 'issue', 'create', '--repo', repo, '--label', 'upstream-health', '--title', TITLE, '--body', managed_body('', report)], check=True, capture_output=True, text=True)


if __name__ == '__main__':
    main()
