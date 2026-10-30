#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""自动核验上游候选并提交 PR；不能确认的事项保留为有明确原因的草稿。"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from audit_skill_update import audit_update, AuditBlocked

ROOT = Path(__file__).resolve().parents[2]
SHA = re.compile(r"[0-9a-f]{40}")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def candidate(entry: dict, metadata: dict, result: dict) -> tuple[dict, dict] | None:
    """只接受检查时与当前目录仍一致、没有路径/可用性错误的 Skill。"""
    source = entry.get("source", {})
    statuses = {issue["status"] for issue in result.get("issues", [])}
    if (result.get("kind") != "skill" or not SLUG.fullmatch(result.get("id", ""))
            or entry.get("id") != result["id"] or source.get("kind") != "git"
            or source.get("repoUrl") != result.get("url")
            or source.get("ref") != result.get("ref")
            or not SHA.fullmatch(result.get("ref") or "")
            or not SHA.fullmatch(result.get("head") or "")
            or result["ref"] == result["head"]
            or "outdated" not in statuses or statuses - {"outdated", "new-skill"}):
        return None
    content = metadata.get("provenance", {}).get("content", {})
    if (content.get("kind") != "git" or content.get("url") != source["repoUrl"]
            or content.get("ref") != source["ref"]):
        return None
    updated, sidecar = copy.deepcopy(entry), copy.deepcopy(metadata)
    updated["source"]["ref"] = result["head"]
    sidecar["provenance"]["content"]["ref"] = result["head"]
    # 候选基线不猜测版本、许可或审核成功；只有真实自动核验通过后才补写机器记录。
    # 自动核验受阻时保留旧审核回执，既有 installable-evidence 校验会阻止发布。
    return updated, sidecar



def prepare_proposal(entry: dict, metadata: dict, result: dict):
    proposed = candidate(entry, metadata, result)
    if proposed is None:
        return None, None, '不符合固定来源候选条件'
    try:
        updated, sidecar, audit = audit_update(entry, metadata, result)
        return (updated, sidecar), audit, None
    except (AuditBlocked, OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        # 保留旧审核证据；失败必须可见，不能改成机器审核已通过。
        return proposed, None, str(error)[:400]


def coverage(results: list[dict], root: Path = ROOT) -> list[dict]:
    checked = {item['id']: item for item in results if item.get('kind') == 'skill'}
    rows = []
    for folder in sorted((root / 'skills').iterdir()):
        pointer = folder / 'entry.json'
        if pointer.is_file():
            entry = json.loads(pointer.read_text())
            kind = entry.get('source', {}).get('kind', 'unknown')
            result = checked.get(entry['id'])
            if (folder / 'upstream-health-hold.json').exists():
                status, reason = 'held', '保留已登记的 hold 决策，需解除 hold 后再推进来源'
            elif kind != 'git':
                sidecar_path = folder / 'catalog-metadata.v1.json'
                governance = json.loads(sidecar_path.read_text()).get('governance', {}) if sidecar_path.is_file() else {}
                if governance.get('availability') != 'installable':
                    status, reason = 'governance-blocked', '当前仅收录或缺少准入证据；不能自动提升为可安装'
                else:
                    status, reason = 'requires-version-feed', 'ZIP/Web 需要可验证的新版发现地址及旧快照；不猜版本或审核成功'
            elif result is None:
                status, reason = 'not-checked', '本轮未包含此来源检查'
            else:
                statuses = {item['status'] for item in result['issues']}
                if statuses == {'ok'}:
                    status, reason = 'current', '检查的固定来源没有待处理变化'
                elif statuses <= {'outdated', 'new-skill'} and 'outdated' in statuses:
                    status, reason = 'queued', '等待有界自动审核预算'
                else:
                    status, reason = 'manual-review-required', ', '.join(sorted(statuses))
            rows.append({'id': entry['id'], 'sourceKind': kind, 'status': status, 'reason': reason})
            for child in entry.get('children', []):
                rows.append({'id': entry['id'] + '/' + child['id'], 'parentId': entry['id'], 'sourceKind': 'collection-child', 'status': status, 'reason': reason})
        elif (folder / 'SKILL.md').is_file():
            rows.append({'id': folder.name, 'sourceKind': 'market-content', 'status': 'market-release',
                         'reason': '内容随市场主仓发布；不另外复制或推测第三方最新来源'})
    return rows


def run(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def write_coverage(rows, destination):
    if destination is None:
        return
    parents = {row['id']: row for row in rows if not row.get('parentId')}
    for row in rows:
        if row.get('parentId'):
            parent = parents[row['parentId']]
            row.update(status=parent['status'], reason='随父合集核验：' + parent['reason'])
    destination.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    summary = ["| Skill | 来源 | 更新状态 | 说明 |", "|---|---|---|---|"]
    summary.extend(f"| {row['id']} | {row['sourceKind']} | {row['status']} | {row['reason'].replace('|', '/').replace(chr(10), ' ')} |" for row in rows)
    destination.with_suffix('.md').write_text("\n".join(summary) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--publish", action="store_true", help="显式创建 PR；默认只做来源核验并输出结果")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--coverage-file", type=Path, help="输出所有 Skill 的更新覆盖与阻碍")
    args = parser.parse_args()
    repository = os.environ.get("GITHUB_REPOSITORY", "desirecore/market")
    actor = os.environ.get("GITHUB_ACTOR", "")
    if args.publish and (repository != "desirecore/market" or not re.fullmatch(r"[A-Za-z0-9-]+", actor)):
        parser.error("发布仅限官方仓库，且必须有触发用户身份")
    if args.limit < 1:
        parser.error("limit 必须大于零")
    results = json.loads(args.results.read_text())
    rows = coverage(results, ROOT)
    by_id = {row["id"]: row for row in rows}
    try:
        open_heads = set()
        if args.publish:
            open_heads = {pr["headRefName"] for pr in json.loads(run("gh", "pr", "list", "--repo", repository, "--state", "open", "--limit", "1000", "--json", "headRefName"))}
        count = 0
        for result in results:
            item_id = result.get("id", "")
            if result.get("kind") != "skill" or not SLUG.fullmatch(item_id):
                continue
            folder = ROOT / "skills" / item_id
            entry_path, metadata_path = folder / "entry.json", folder / "catalog-metadata.v1.json"
            if not entry_path.is_file() or not metadata_path.is_file():
                if item_id in by_id:
                    by_id[item_id].update(status="manual-review-required", reason="缺少来源或 sidecar 契约")
                continue
            if (folder / "upstream-health-hold.json").exists():
                continue
            proposed = candidate(json.loads(entry_path.read_text()), json.loads(metadata_path.read_text()), result)
            if proposed is None:
                if item_id in by_id and by_id[item_id]['status'] == 'queued':
                    by_id[item_id].update(status="manual-review-required", reason="来源或 provenance 与检查快照不一致")
                continue
            branch = f"updates/{item_id}-{result['head'][:12]}"
            # 保留审核者已编辑的候选；已关闭候选也不在下一轮重新创建。
            if any(head.startswith(f"updates/{item_id}-") for head in open_heads):
                by_id[item_id].update(status="already-open", reason="保留已有 PR 和审核者修改")
                continue
            existing = json.loads(run("gh", "pr", "list", "--repo", repository, "--state", "all",
                                      "--head", branch, "--json", "number")) if args.publish else []
            if existing:
                by_id[item_id].update(status="already-proposed", reason="同一快照已有 PR 记录，不重复提交")
                continue
            if count >= args.limit:
                continue
            count += 1
            proposed, audit, reason = prepare_proposal(json.loads(entry_path.read_text()), json.loads(metadata_path.read_text()), result)
            if proposed is None:
                by_id[item_id].update(status="manual-review-required", reason=reason)
                continue
            by_id[item_id].update(status="audit-passed" if audit else "manual-review-required", reason=reason or "来源、许可与结构化元数据核验通过；不代表运行或安全认证")
            print(f"{item_id}: {by_id[item_id]['status']}: {by_id[item_id]['reason']}")
            if not args.publish:
                continue
            with tempfile.TemporaryDirectory(prefix="market-update-") as tmp:
                checkout = Path(tmp) / "checkout"
                run("git", "worktree", "add", "--detach", str(checkout), "HEAD")
                try:
                    run("git", "switch", "-c", branch, cwd=checkout)
                    for path, data in zip((entry_path, metadata_path), proposed):
                        (checkout / path.relative_to(ROOT)).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
                    paths = [f"skills/{item_id}/entry.json", f"skills/{item_id}/catalog-metadata.v1.json"]
                    if audit:
                        audit_path = f"skills/{item_id}/upstream-audit.v1.json"
                        (checkout / audit_path).write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
                        try:
                            # 只运行受审仓库自己的元数据校验，不运行上游代码。
                            run("uv", "run", "--quiet", "scripts/catalog/validate_catalog_metadata.py", "--require-complete", cwd=checkout)
                            run("uv", "run", "--quiet", "scripts/i18n/validate-i18n.py", f"skills/{item_id}", cwd=checkout)
                            run("uv", "run", "--quiet", "scripts/i18n/translate.py", "--check", f"skills/{item_id}", cwd=checkout)
                            if proposed[0].get('children'):
                                run("uv", "run", "--quiet", "scripts/gen-collection-children.py", "--check", item_id, cwd=checkout)
                        except subprocess.CalledProcessError as error:
                            print(error.stdout or error.stderr or '目录校验失败')
                            audit, reason = None, '目录或本地化元数据校验未通过；保持草稿，不能发布'
                            by_id[item_id].update(status="manual-review-required", reason=reason)
                            fallback = candidate(json.loads(entry_path.read_text()), json.loads(metadata_path.read_text()), result)
                            for path, data in zip((entry_path, metadata_path), fallback):
                                (checkout / path.relative_to(ROOT)).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
                            # 如果已有旧审计文件，不把它误称为本次通过记录。
                            (checkout / audit_path).write_text(json.dumps({'schemaVersion': 1, 'status': 'blocked', 'ref': result['head'], 'reason': reason}, ensure_ascii=False, indent=2) + "\n")
                        paths.append(audit_path)

                    run("git", "add", "--", *paths, cwd=checkout)
                    run("git", "-c", f"user.name={actor}", "-c", f"user.email={actor}@users.noreply.github.com",
                        "commit", "-m", f"chore(market): 提议更新 {item_id} 上游快照", cwd=checkout)
                    run("git", "push", "origin", f"HEAD:refs/heads/{branch}", cwd=checkout)
                    body = Path(tmp) / "body.md"
                    findings = json.dumps(audit, ensure_ascii=False, indent=2) if audit else reason
                    body.write_text(
                        f"`{item_id}` 上游快照：`{result['ref']}` → `{result['head']}`\n\n"
                        + ("自动来源、许可与结构化元数据核验通过；审核身份和记录明确标为机器。已运行目录与本条目元数据校验。\n"
                           if audit else "自动核验未通过，保留旧审核回执与草稿，不能据此发布新版。\n")
                        + "不执行上游代码，不代表软件安全认证或真实运行验收，不自动合并。非结构化依赖和行为变化仍需结合 PR 差异复核。\n\n"
                        + "Automated source/license/metadata verification, not a security certification or runtime acceptance. No auto-merge.\n\n"
                        + "```json\n" + str(findings) + "\n```\n", encoding="utf-8")
                    command = ["gh", "pr", "create", "--repo", repository, "--base", "main", "--head", branch,
                               "--title", f"chore(market): 更新 {item_id} 上游快照", "--body-file", str(body)]
                    if not audit:
                        command.append("--draft")
                    run(*command, cwd=checkout)

                except subprocess.CalledProcessError:
                    by_id[item_id].update(status="publish-failed", reason="本地校验、提交、推送或 PR API 失败；未宣称已发布")
                    raise
                finally:
                    run("git", "worktree", "remove", "--force", str(checkout))
    finally:
        write_coverage(rows, args.coverage_file)


if __name__ == "__main__":
    main()
