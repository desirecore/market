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
              the installed snapshot (source.ref, or branch head when unpinned)
  unreachable network error other than "not found"; treated as unknown, not broken
  stale-hold  a reviewed hold no longer applies (invalid file, pin or installed upstream
              content changed since review, or nothing left to hold); re-review it
  new-skill   branch head has collection children that `children` does not declare
              (same discovery rules as scripts/gen-collection-children.py)
  upstream-path-change  a declared path moved at branch head but the pin still works
  outdated    pinned content differs from branch head; review before updating
  unpinned    entry follows a moving branch without source.ref
  held        upstream-path-change / outdated finding covered by a reviewed hold
  ok          nothing to report

Path checks distinguish the installed snapshot from changes at branch head.
Only skills get path checks; agents and teams are AgentFS repositories.

Maintainers who review an upstream change and deliberately keep the current pin
record that decision next to entry.json in `upstream-health-hold.json`:

  {"statuses": ["upstream-path-change", "outdated"], "ref": "<source.ref>",
   "head": "<reviewed upstream commit>", "reviewedAt": "YYYY-MM-DD", "reason": "..."}

The listed findings are reported as `held` while source.ref still equals `ref`
and the installed content at branch head is unchanged since `head`. Broken,
unreachable, new-skill and unpinned findings can never be held.

Usage:
  uv run scripts/catalog/check_upstream_health.py                  # text table
  uv run scripts/catalog/check_upstream_health.py --format markdown
  uv run scripts/catalog/check_upstream_health.py --format json
  uv run scripts/catalog/check_upstream_health.py dingtalk-cli humanlayer-skills

Exit code: 1 when any entry is gone / bad-branch / bad-ref / bad-path, else 0
(held and stale-hold findings alone never fail the run).
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
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
KINDS = ("skills", "agents", "teams")

BROKEN = ("gone", "bad-branch", "bad-ref", "bad-path")
ACTIONABLE = (*BROKEN, "stale-hold", "upstream-path-change", "new-skill", "outdated", "unpinned")
ORDER = (*BROKEN, "unreachable", "stale-hold", "upstream-path-change", "new-skill", "outdated", "unpinned",
         "held", "ok")

# A reviewed decision to keep the current pin, next to entry.json.
HOLD_NAME = "upstream-health-hold.json"
HOLD_KEYS = ("statuses", "ref", "head", "reviewedAt", "reason")
HOLDABLE = ("upstream-path-change", "outdated")
SHA = re.compile(r"[0-9a-f]{40}")

# Git asks for credentials when a public repository disappears; never prompt.
GIT_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
NOT_FOUND = re.compile(
    r"repository not found|authentication failed|could not read username|"
    r"not found|does not exist|does not appear to be a git repository",
    re.IGNORECASE,
)
# A fetch-by-SHA failure that means the commit is gone, not a network problem.
MISSING_COMMIT = re.compile(r"not our ref|couldn't find remote ref|unadvertised object|not found", re.IGNORECASE)


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


def comparison_scope(entry: dict, kind: str) -> list[str]:
    """Pathspec for snapshot comparisons: only what an installation copies.

    A single-skill pointer installs only source.path, and a collection installs
    only its declared children, so upstream feeds, site builds, CLI sources and
    unrelated skills must not cause endless repins. Root licensing changes still
    need review. Undeclared upstream children are reported separately as
    `new-skill`. Agents, teams and root-level skills install the whole snapshot.
    """
    if kind != "skills":
        return []
    children = entry.get("children") or []
    path = (entry["source"].get("path") or "").strip("/")
    paths = sorted({c["path"].strip("/") for c in children}) if children else ([path] if path else [])
    if not paths:
        return []
    return ["--", *paths, ":(top,glob)LICENSE*", ":(top,glob)NOTICE*", ":(top,glob)COPYING*"]


def check_git(entry: dict, kind: str, hold: dict | None = None) -> tuple[list[tuple[str, str]], str | None]:
    """Return the findings and the upstream commit they were checked against."""
    source = entry["source"]
    url = source["repoUrl"]
    branch = source.get("repoBranch")
    ref = source.get("ref")
    issues: list[tuple[str, str]] = []

    advertised_ref = f"refs/heads/{branch}" if branch else "HEAD"
    query = ["--heads", url, advertised_ref] if branch else [url, "HEAD"]
    remote = git("ls-remote", *query, timeout=90)
    if remote.returncode != 0:
        detail = last_line(remote.stderr)
        return [("gone" if NOT_FOUND.search(remote.stderr) else "unreachable", detail)], None
    heads = [line.split()[0] for line in remote.stdout.splitlines()
             if len(line.split()) == 2 and line.split()[1] == advertised_ref]
    if branch and not heads:
        return [("bad-branch", f"branch '{branch}' not found upstream")], None
    if not heads:
        return [("unreachable", "remote advertised no HEAD")], None
    head = heads[0]

    with tempfile.TemporaryDirectory(prefix=f"health-{entry['id']}-") as tmp:
        repo = Path(tmp) / "repo"
        clone = ["clone", "--quiet", "--depth", "1", "--filter=blob:none", "--no-checkout"]
        if branch:
            clone += ["--single-branch", "-b", branch]
        cloned = git(*clone, url, str(repo), timeout=300)
        if cloned.returncode != 0:
            return [("unreachable", f"clone failed: {last_line(cloned.stderr)}")], head

        # The branch can advance between advertisement and clone. Inspect the
        # actual cloned snapshot throughout this check.
        cloned_head = git("rev-parse", "HEAD", cwd=repo)
        if cloned_head.returncode != 0:
            return [("unreachable", f"cannot resolve clone: {last_line(cloned_head.stderr)}")], head
        head = cloned_head.stdout.strip()

        if ref and ref != head:
            fetched = git("fetch", "--quiet", "--depth", "1", "origin", ref, cwd=repo, timeout=180)
            if fetched.returncode != 0:
                status = "bad-ref" if MISSING_COMMIT.search(fetched.stderr) else "unreachable"
                return [(status, f"cannot fetch pinned {ref[:12]}: {last_line(fetched.stderr)}")], head

        try:
            if kind == "skills":
                if ref and ref != head:
                    issues += check_skill_paths(entry, repo, ref, discover=False)
                    upstream = check_skill_paths(entry, repo, head)
                    issues += [("upstream-path-change" if status == "bad-path" else status, detail)
                               for status, detail in upstream
                               if status != "bad-path" or ("bad-path", detail) not in issues]
                else:
                    issues += check_skill_paths(entry, repo, head)
        except RuntimeError as err:
            return [("unreachable", str(err)[:300])], head

        if ref and ref != head:
            difference = git("diff", "--quiet", ref, head, *comparison_scope(entry, kind), cwd=repo)
            if difference.returncode == 1:
                issues.append(("outdated", f"{ref[:7]} -> {head[:7]}"))
            elif difference.returncode != 0:
                issues.append(("unreachable", f"cannot compare snapshots: {last_line(difference.stderr)}"))

        if hold:
            issues = apply_hold(issues, hold, entry, kind, repo, head)

    if not ref:
        issues.append(("unpinned", f"follows '{branch or 'HEAD'}' at {head[:7]}"))
    return issues, head


def check_skill_paths(entry: dict, repo: Path, revision: str = "HEAD", *,
                      discover: bool = True) -> list[tuple[str, str]]:
    skill_dirs = {Path(path).parent.as_posix() for path in GENERATOR.skill_paths(repo, revision)}
    skill_dirs = {"" if d == "." else d for d in skill_dirs}
    issues: list[tuple[str, str]] = []
    children = entry.get("children") or []

    if children:
        declared = {c["path"].strip("/") for c in children}
        for child in children:
            if child["path"].strip("/") not in skill_dirs:
                issues.append(("bad-path", f"child '{child['id']}' -> '{child['path']}' has no SKILL.md"))
        discovered = [c for c in GENERATOR.discover_children(repo, revision)
                      if c["path"] not in declared] if discover else []
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


def apply_hold(issues: list[tuple[str, str]], hold: dict, entry: dict, kind: str, repo: Path,
               head: str) -> list[tuple[str, str]]:
    """Report reviewed findings as `held` while the review still covers them.

    A hold covers one pinned ref and the installed scope at the reviewed
    upstream head. Once either moves, or nothing it lists is found any more,
    the findings are kept as they are and a `stale-hold` explains why.
    """
    if any(status == "unreachable" for status, _ in issues):
        return issues  # unknown state: the review can be neither applied nor judged stale
    ref, reviewed = entry["source"].get("ref"), hold["head"]
    if ref != hold["ref"]:
        pinned = ref[:7] if ref else "unpinned"
        return [*issues, ("stale-hold", f"pinned ref changed since review ({hold['ref'][:7]} -> {pinned})")]
    if reviewed not in (ref, head):
        fetched = git("fetch", "--quiet", "--depth", "1", "origin", reviewed, cwd=repo, timeout=180)
        if fetched.returncode != 0:
            status = "stale-hold" if MISSING_COMMIT.search(fetched.stderr) else "unreachable"
            return [*issues, (status, f"reviewed head {reviewed[:7]} cannot be fetched: "
                                      f"{last_line(fetched.stderr)}")]
    difference = git("diff", "--quiet", reviewed, head, *comparison_scope(entry, kind), cwd=repo)
    if difference.returncode == 1:
        return [*issues, ("stale-hold", f"upstream changed within the installed scope since {reviewed[:7]}")]
    if difference.returncode != 0:
        return [*issues, ("unreachable", f"cannot compare with reviewed head {reviewed[:7]}: "
                                         f"{last_line(difference.stderr)}")]
    note = f" — reviewed {hold['reviewedAt']}: {hold['reason']}"
    held = [("held", f"{status}: {detail}{note}") if status in hold["statuses"] else (status, detail)
            for status, detail in issues]
    if not any(status == "held" for status, _ in held):
        held.append(("stale-hold", f"no held finding remains ({', '.join(hold['statuses'])}); remove {HOLD_NAME}"))
    return held


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


def hold_errors(data: object) -> list[str]:
    """Explain why a reviewed hold is unusable; an empty list means it is valid."""
    if not isinstance(data, dict):
        return ["must be a JSON object"]
    errors = []
    missing = [key for key in HOLD_KEYS if key not in data]
    unknown = sorted(set(data) - set(HOLD_KEYS))
    if missing:
        errors.append(f"missing {', '.join(missing)}")
    if unknown:
        errors.append(f"unknown key(s) {', '.join(unknown)}")
    if "statuses" in data:
        statuses = data["statuses"]
        if not isinstance(statuses, list) or not statuses:
            errors.append("statuses must be a non-empty list")
        elif any(status not in HOLDABLE for status in statuses):
            errors.append(f"statuses may only list {' / '.join(HOLDABLE)}")
        elif len(set(statuses)) != len(statuses):
            errors.append("statuses must be unique")
    for key in ("ref", "head"):
        if key in data and not (isinstance(data[key], str) and SHA.fullmatch(data[key])):
            errors.append(f"{key} must be a full lowercase 40-hex commit SHA")
    if "reviewedAt" in data:
        try:
            reviewed = date.fromisoformat(data["reviewedAt"]).isoformat() == data["reviewedAt"]
        except (TypeError, ValueError):
            reviewed = False
        if not reviewed:
            errors.append("reviewedAt must be a YYYY-MM-DD date")
    if "reason" in data and not (isinstance(data["reason"], str) and data["reason"].strip()):
        errors.append("reason must be non-empty text")
    return errors


def load_hold(entry_path: Path) -> tuple[dict | None, list[str]]:
    """Read the reviewed hold next to entry.json.

    Returns (None, []) without a hold file, (hold, []) for a valid one and
    (None, errors) when a hold file exists but cannot be used.
    """
    path = entry_path.with_name(HOLD_NAME)
    if not path.exists():
        return None, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        return None, [f"unreadable JSON: {err}"]
    errors = hold_errors(data)
    return (None, errors) if errors else (data, [])


def check_entry(path: Path) -> dict:
    entry = json.loads(path.read_text(encoding="utf-8"))
    kind = path.parent.parent.name
    source = entry.get("source", {})
    hold, hold_problems = load_hold(path)
    if source.get("kind") == "git":
        issues, head = check_git(entry, kind, hold)
    else:
        issues, head = check_http(entry), None
    if hold_problems:
        issues = [*issues, ("stale-hold", f"invalid {HOLD_NAME}: {'; '.join(hold_problems)}")]
    elif hold and source.get("kind") != "git":
        issues = [*issues, ("stale-hold", "holds apply only to git entries")]
    return {
        "id": entry["id"],
        "kind": kind.rstrip("s"),
        "url": source.get("repoUrl") or source.get("url"),
        "ref": source.get("ref"),
        "head": head,
        "issues": [{"status": s, "detail": d} for s, d in (issues or [("ok", "")])],
    }


def worst(result: dict) -> int:
    return min(ORDER.index(i["status"]) for i in result["issues"])


# Every git pointer in the catalog is hosted on GitHub.
GITHUB_REPO = re.compile(r"https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?")


def compare_url(url: str | None, ref: str | None, head: str | None) -> str | None:
    """Upstream page showing what changed between the pinned ref and the checked head."""
    match = GITHUB_REPO.fullmatch(url or "")
    if not (match and ref and head):
        return None
    return f"https://github.com/{match[1]}/{match[2]}/compare/{ref}...{head}"


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
        ("Stale holds — re-review", ("stale-hold",)),
        ("Upstream path changes — pinned installation still resolves", ("upstream-path-change",)),
        ("Undeclared upstream skills", ("new-skill",)),
        ("Updates available", ("outdated",)),
        ("Unpinned", ("unpinned",)),
        ("Reviewed holds — not actionable", ("held",)),
    ]
    for title, statuses in sections:
        rows = [(r, i) for r in results for i in r["issues"] if i["status"] in statuses]
        if not rows:
            continue
        out += [f"### {title} ({len(rows)})", "", "| Status | Entry | Detail |", "|---|---|---|"]
        for r, i in sorted(rows, key=lambda x: (ORDER.index(x[1]["status"]), x[0]["id"])):
            detail = i["detail"].replace("|", "\\|")
            compare = compare_url(r["url"], r.get("ref"), r.get("head"))
            if i["status"] == "outdated" and compare:
                detail = f"[{r['ref'][:7]} → {r['head'][:7]}]({compare})"
            out.append(f"| `{i['status']}` | [{r['kind']}/{r['id']}]({r['url']}) | {detail} |")
        out.append("")
    ok = sorted(r["id"] for r in results if worst(r) == ORDER.index("ok"))
    if ok:
        out += [f"<details><summary>OK ({len(ok)})</summary>", "", ", ".join(f"`{i}`" for i in ok), "", "</details>"]
    return "\n".join(out)


def summarize(results: list[dict]) -> dict:
    statuses = {issue["status"] for result in results for issue in result["issues"]}
    return {
        "checked": len(results),
        "broken": bool(statuses.intersection(BROKEN)),
        "actionable": bool(statuses.intersection(ACTIONABLE)),
        "unknown": "unreachable" in statuses,
        "held": sum(issue["status"] == "held" for result in results for issue in result["issues"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ids", nargs="*", help="entry IDs to check (default: every external entry)")
    parser.add_argument("--format", choices=("text", "markdown", "json"), default="text")
    parser.add_argument("--jobs", type=int, default=8, help="parallel upstream checks")
    parser.add_argument("--summary-file", type=Path, help="write machine-readable workflow decisions")
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

    if args.summary_file:
        args.summary_file.write_text(json.dumps(summarize(results), indent=2) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.format == "markdown":
        print(render_markdown(results))
    else:
        print(render_text(results))
    return 1 if summarize(results)["broken"] else 0


if __name__ == "__main__":
    sys.exit(main())
