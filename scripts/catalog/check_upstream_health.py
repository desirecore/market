#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Report the upstream health of every external pointer in the catalog.

External entries (`skills/*/entry.json`, `agents/*/entry.json`,
`teams/*/entry.json`) keep their content upstream, so a deleted repository, a
rewritten branch or a moved skill directory silently breaks installation. This
script looks at each upstream and reports, without rewriting anything:

  gone        upstream repository or URL no longer exists (deleted, private, 404/410)
  bad-branch  source.repoBranch no longer exists upstream
  bad-ref     pinned source.ref can no longer be fetched (history rewritten)
  bad-path    source.path, the root SKILL.md, or a declared child path is missing at
              branch head
  unreachable network error other than "not found"; treated as unknown, not broken
  new-skill   branch head has collection children that `children` does not declare
              (same discovery rules as scripts/gen-collection-children.py)
  outdated    pinned source.ref is behind branch head; an update is available
  unpinned    entry follows a moving branch without source.ref
  ok          nothing to report

Path checks run against branch head: they answer "will this pointer still work
after the next ref bump", while `bad-ref` answers "does the pinned ref still
resolve". Only skills get path checks; agents and teams are AgentFS repositories.

Usage:
  uv run scripts/catalog/check_upstream_health.py                  # text table
  uv run scripts/catalog/check_upstream_health.py --format markdown
  uv run scripts/catalog/check_upstream_health.py --format json
  uv run scripts/catalog/check_upstream_health.py dingtalk-cli humanlayer-skills

Exit code: 1 when any entry is gone / bad-branch / bad-ref / bad-path, else 0.
Needs Git and network access.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
KINDS = ("skills", "agents", "teams")

BROKEN = ("gone", "bad-branch", "bad-ref", "bad-path")
ORDER = (*BROKEN, "unreachable", "new-skill", "outdated", "unpinned", "ok")

# Git asks for credentials when a public repository disappears; never prompt.
GIT_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
NOT_FOUND = re.compile(
    r"repository not found|authentication failed|could not read username|"
    r"not found|does not exist|does not appear to be a git repository",
    re.IGNORECASE,
)


def _load_generator():
    """Reuse the collection generator's discovery so both tools agree on children."""
    path = REPO_ROOT / "scripts" / "gen-collection-children.py"
    spec = importlib.util.spec_from_file_location("market_collection_generator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GENERATOR = _load_generator()


def git(*args: str, cwd: Path | None = None, timeout: int = 180) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                              env=GIT_ENV, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, 124, "", "timed out")


def last_line(text: str) -> str:
    lines = [line for line in text.strip().splitlines() if line.strip()]
    return lines[-1][:200] if lines else "no output"


def check_git(entry: dict, kind: str) -> list[tuple[str, str]]:
    source = entry["source"]
    url = source["repoUrl"]
    branch = source.get("repoBranch")
    ref = source.get("ref")
    issues: list[tuple[str, str]] = []

    query = ["--heads", url, branch] if branch else [url, "HEAD"]
    remote = git("ls-remote", *query, timeout=90)
    if remote.returncode != 0:
        detail = last_line(remote.stderr)
        return [("gone" if NOT_FOUND.search(remote.stderr) else "unreachable", detail)]
    heads = [line.split()[0] for line in remote.stdout.splitlines() if line.strip()]
    if branch and not heads:
        return [("bad-branch", f"branch '{branch}' not found upstream")]
    if not heads:
        return [("unreachable", "remote advertised no HEAD")]
    head = heads[0]

    with tempfile.TemporaryDirectory(prefix=f"health-{entry['id']}-") as tmp:
        repo = Path(tmp) / "repo"
        clone = ["clone", "--quiet", "--depth", "1", "--filter=blob:none", "--no-checkout"]
        if branch:
            clone += ["--single-branch", "-b", branch]
        cloned = git(*clone, url, str(repo), timeout=300)
        if cloned.returncode != 0:
            return [("unreachable", f"clone failed: {last_line(cloned.stderr)}")]

        if ref and ref != head:
            fetched = git("fetch", "--quiet", "--depth", "1", "origin", ref, cwd=repo, timeout=180)
            if fetched.returncode != 0:
                issues.append(("bad-ref", f"pinned {ref[:12]} is no longer fetchable"))

        if kind == "skills":
            issues += check_skill_paths(entry, repo)

    if ref and ref != head:
        issues.append(("outdated", f"{ref[:7]} -> {head[:7]}"))
    if not ref:
        issues.append(("unpinned", f"follows '{branch or 'HEAD'}' at {head[:7]}"))
    return issues


def check_skill_paths(entry: dict, repo: Path) -> list[tuple[str, str]]:
    # Materialise only SKILL.md files; the generator reads their frontmatter.
    git("sparse-checkout", "set", "--no-cone", "SKILL.md", cwd=repo)
    checkout = git("checkout", "--quiet", "HEAD", cwd=repo, timeout=300)
    if checkout.returncode != 0:
        return [("unreachable", f"checkout failed: {last_line(checkout.stderr)}")]

    skill_dirs = {p.parent.relative_to(repo).as_posix() for p in repo.rglob("SKILL.md")
                  if ".git" not in p.parts}
    skill_dirs = {"" if d == "." else d for d in skill_dirs}
    issues: list[tuple[str, str]] = []
    children = entry.get("children") or []

    if children:
        declared = {c["path"].strip("/") for c in children}
        for child in children:
            if child["path"].strip("/") not in skill_dirs:
                issues.append(("bad-path", f"child '{child['id']}' -> '{child['path']}' has no SKILL.md"))
        discovered = [c for c in GENERATOR.discover_children(repo) if c["path"] not in declared]
        declared_ids = {c["id"] for c in children}
        extra = [c["path"] for c in discovered if c["id"] not in declared_ids]
        if extra:
            shown = ", ".join(extra[:8]) + (f" (+{len(extra) - 8} more)" if len(extra) > 8 else "")
            issues.append(("new-skill", shown))
    else:
        path = (entry["source"].get("path") or "").strip("/")
        if path not in skill_dirs:
            where = f"source.path '{path}'" if path else "repository root"
            issues.append(("bad-path", f"{where} has no SKILL.md"))
    return issues


def check_http(entry: dict) -> list[tuple[str, str]]:
    url = entry["source"].get("url") or entry["source"].get("repoUrl")
    request = urllib.request.Request(url, headers={"User-Agent": "desirecore-market-health", "Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(request, timeout=30):
            return []
    except urllib.error.HTTPError as err:
        if err.code in (404, 410):
            return [("gone", f"HTTP {err.code}")]
        return [("unreachable", f"HTTP {err.code}")]
    except Exception as err:  # noqa: BLE001 - network errors are reported, not raised
        return [("unreachable", str(err)[:200])]


def check_entry(path: Path) -> dict:
    entry = json.loads(path.read_text(encoding="utf-8"))
    kind = path.parent.parent.name
    source = entry.get("source", {})
    issues = check_git(entry, kind) if source.get("kind") == "git" else check_http(entry)
    return {
        "id": entry["id"],
        "kind": kind.rstrip("s"),
        "url": source.get("repoUrl") or source.get("url"),
        "issues": [{"status": s, "detail": d} for s, d in (issues or [("ok", "")])],
    }


def worst(result: dict) -> int:
    return min(ORDER.index(i["status"]) for i in result["issues"])


def render_text(results: list[dict]) -> str:
    rows = []
    for r in sorted(results, key=lambda r: (worst(r), r["id"])):
        for issue in sorted(r["issues"], key=lambda i: ORDER.index(i["status"])):
            rows.append(f"{issue['status']:<11} {r['kind']:<6} {r['id']:<32} {issue['detail']}")
    return "\n".join(rows)


def render_markdown(results: list[dict]) -> str:
    counts = {s: 0 for s in ORDER}
    for r in results:
        counts[ORDER[worst(r)]] += 1
    summary = " · ".join(f"{s}: {n}" for s, n in counts.items() if n)
    out = [f"Checked {len(results)} external entries. {summary}", ""]
    sections = [
        ("Broken — installation fails", BROKEN),
        ("Unreachable — network error, status unknown", ("unreachable",)),
        ("Undeclared upstream skills", ("new-skill",)),
        ("Updates available", ("outdated",)),
        ("Unpinned", ("unpinned",)),
    ]
    for title, statuses in sections:
        rows = [(r, i) for r in results for i in r["issues"] if i["status"] in statuses]
        if not rows:
            continue
        out += [f"### {title} ({len(rows)})", "", "| Status | Entry | Detail |", "|---|---|---|"]
        for r, i in sorted(rows, key=lambda x: (ORDER.index(x[1]["status"]), x[0]["id"])):
            detail = i["detail"].replace("|", "\\|")
            out.append(f"| `{i['status']}` | [{r['kind']}/{r['id']}]({r['url']}) | {detail} |")
        out.append("")
    ok = sorted(r["id"] for r in results if worst(r) == ORDER.index("ok"))
    if ok:
        out += [f"<details><summary>OK ({len(ok)})</summary>", "", ", ".join(f"`{i}`" for i in ok), "", "</details>"]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ids", nargs="*", help="entry IDs to check (default: every external entry)")
    parser.add_argument("--format", choices=("text", "markdown", "json"), default="text")
    parser.add_argument("--jobs", type=int, default=8, help="parallel upstream checks")
    args = parser.parse_args(argv)

    paths = [p for kind in KINDS for p in sorted((REPO_ROOT / kind).glob("*/entry.json"))]
    if args.ids:
        paths = [p for p in paths if p.parent.name in set(args.ids)]
        missing = set(args.ids) - {p.parent.name for p in paths}
        if missing:
            print(f"unknown entry id(s): {', '.join(sorted(missing))}", file=sys.stderr)
            return 2

    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = list(pool.map(check_entry, paths))

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.format == "markdown":
        print(render_markdown(results))
    else:
        print(render_text(results))
    return 1 if any(i["status"] in BROKEN for r in results for i in r["issues"]) else 0


if __name__ == "__main__":
    sys.exit(main())
