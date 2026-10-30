#!/usr/bin/env python3
"""把健康检查中确定过时的 Skill 指针提交为待审核草稿；绝不更新审核回执。"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

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
    # reviewedRef / reviewedAt / reviewedBy、版本、翻译与许可均须人工核验，不能伪造。
    # 旧审核回执与新 ref 不匹配时，既有 installable-evidence 校验会阻止发布。
    return updated, sidecar


def run(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--publish", action="store_true", help="显式创建远端草稿 PR；默认仅列候选")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    repository = os.environ.get("GITHUB_REPOSITORY", "desirecore/market")
    actor = os.environ.get("GITHUB_ACTOR", "")
    if args.publish and (repository != "desirecore/market" or not re.fullmatch(r"[A-Za-z0-9-]+", actor)):
        parser.error("发布仅限官方仓库，且必须有触发用户身份")
    if args.limit < 1:
        parser.error("limit 必须大于零")
    open_heads = set()
    if args.publish:
        open_heads = {pr["headRefName"] for pr in json.loads(run("gh", "pr", "list", "--repo", repository, "--state", "open", "--limit", "1000", "--json", "headRefName"))}
    count = 0
    for result in json.loads(args.results.read_text()):
        item_id = result.get("id", "")
        if result.get("kind") != "skill" or not SLUG.fullmatch(item_id):
            continue
        folder = ROOT / "skills" / item_id
        entry_path, metadata_path = folder / "entry.json", folder / "catalog-metadata.v1.json"
        if not entry_path.is_file() or not metadata_path.is_file() or (folder / "upstream-health-hold.json").exists():
            continue
        proposed = candidate(json.loads(entry_path.read_text()), json.loads(metadata_path.read_text()), result)
        if proposed is None:
            continue
        print(f"{item_id}: {result['ref']} -> {result['head']}")
        if not args.publish:
            continue
        branch = f"updates/{item_id}-{result['head'][:12]}"
        # 保留审核者已编辑的候选；已关闭候选也不在下一轮重新创建。
        if any(head.startswith(f"updates/{item_id}-") for head in open_heads):
            continue
        existing = json.loads(run("gh", "pr", "list", "--repo", repository, "--state", "all",
                                  "--head", branch, "--json", "number"))
        if existing:
            continue
        with tempfile.TemporaryDirectory(prefix="market-update-") as tmp:
            checkout = Path(tmp) / "checkout"
            run("git", "worktree", "add", "--detach", str(checkout), "HEAD")
            try:
                run("git", "switch", "-c", branch, cwd=checkout)
                for path, data in zip((entry_path, metadata_path), proposed):
                    (checkout / path.relative_to(ROOT)).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
                run("git", "add", "--", f"skills/{item_id}/entry.json", f"skills/{item_id}/catalog-metadata.v1.json", cwd=checkout)
                run("git", "-c", f"user.name={actor}", "-c", f"user.email={actor}@users.noreply.github.com",
                    "commit", "-m", f"chore(market): 提议更新 {item_id} 上游快照", cwd=checkout)
                run("git", "push", "origin", f"HEAD:refs/heads/{branch}", cwd=checkout)
                body = Path(tmp) / "body.md"
                body.write_text(
                    f"每日检查发现 `{item_id}` 的已安装范围有上游变化。\n\n"
                    f"旧快照：`{result['ref']}`\n新候选：`{result['head']}`\n\n"
                    "这是未审核草稿。仅调整来源指针，保留旧审核回执，不声明新版本已获审核。"
                    "固定来源与 reviewedRef 不一致导致的校验失败是发布阻碍，审核者必须完成以下事项后再转为 Ready：\n\n"
                    "- [ ] 审查来源差异、许可证、依赖和兼容性\n"
                    "- [ ] 核对版本和中英文简介；合集重新生成 children 并审查新增项\n"
                    "- [ ] 用真实审核者、日期和新 reviewedRef 更新审核证据\n"
                    "- [ ] 运行目录、翻译和安装相关验收\n\n"
                    "Daily upstream update candidate; no automatic merge or fabricated review evidence.\n",
                    encoding="utf-8")
                run("gh", "pr", "create", "--repo", repository, "--base", "main", "--head", branch,
                    "--draft", "--title", f"chore(market): 审核 {item_id} 上游更新", "--body-file", str(body), cwd=checkout)
            finally:
                run("git", "worktree", "remove", "--force", str(checkout))
        count += 1
        if count >= args.limit:
            break


if __name__ == "__main__":
    main()
