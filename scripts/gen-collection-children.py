#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Generate `children` for collection entries in skills/<id>/entry.json.

A collection entry points at an upstream repo that holds several sibling skills
(e.g. larksuite/cli has skills/lark-im, skills/lark-doc, ...). One market card
covers them all; the client lets the user tick which ones to install. That needs
a declared child list so the detail page renders without touching the network.

For each requested entry this script:
  1. clones the pinned ref (shallow, falling back to fetch-by-SHA);
  2. walks the tree for SKILL.md files, skipping test fixtures and vendored dirs;
  3. reads frontmatter name/description/version;
  4. writes `children` back into entry.json, leaving every other field untouched.

Usage:
  python3 scripts/gen-collection-children.py                 # all entries that already declare children
  python3 scripts/gen-collection-children.py larksuite-cli   # specific ids
  python3 scripts/gen-collection-children.py --check          # verify without writing
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

# Path segments that never hold a publishable skill: test fixtures for skill
# linters look exactly like real skills (larksuite/cli ships six of them under
# scripts/skill-format-check/tests/), so excluding them is not optional.
EXCLUDED_SEGMENTS = {
    ".git", "node_modules", "upstream", ".cache", "vendor", "internal",
    "test", "tests", "__tests__", "testdata", "test-data",
    "fixture", "fixtures", "__fixtures__",
    "example", "examples", "template", "templates",
}

# Descriptions run to several hundred characters upstream; the picker only has
# room for one line, so keep the first sentence.
MAX_SHORT_DESC = 160


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def clone_pinned(repo_url: str, branch: str, ref: str | None, dest: Path) -> None:
    """Clone at the pinned ref. Mirrors the client's cloneGitToTemp behaviour."""
    result = run(["git", "clone", "--quiet", "--single-branch", "-b", branch,
                  "--depth", "100", repo_url, str(dest)])
    if result.returncode != 0:
        raise RuntimeError(f"clone failed: {result.stderr.strip()[:300]}")

    if not ref:
        return

    if run(["git", "checkout", "--quiet", ref], cwd=dest).returncode == 0:
        return

    # Pinned commit fell outside the shallow window — fetch that object alone.
    # Both failures carry stderr: "cannot fetch pinned ref <sha>" alone cannot
    # tell a missing commit object from a permissions or network problem.
    fetched = run(["git", "fetch", "--quiet", "origin", ref, "--depth", "1"], cwd=dest)
    if fetched.returncode != 0:
        raise RuntimeError(f"cannot fetch pinned ref {ref}: {fetched.stderr.strip()[:300]}")

    checked_out = run(["git", "checkout", "--quiet", ref], cwd=dest)
    if checked_out.returncode != 0:
        raise RuntimeError(f"cannot check out pinned ref {ref}: {checked_out.stderr.strip()[:300]}")


def parse_frontmatter(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        return {}
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def first_sentence(text: str) -> str:
    flat = " ".join(str(text).split())
    match = re.search(r"^(.{1,%d}?[。.!?！？])\s" % MAX_SHORT_DESC, flat + " ")
    candidate = match.group(1) if match else flat
    if len(candidate) > MAX_SHORT_DESC:
        candidate = candidate[:MAX_SHORT_DESC].rstrip() + "…"
    return candidate


def normalize_version(raw) -> str | None:
    """Mirror the client's normalizeSemver: upstream writes `1.0` and `v1.2.3`."""
    if raw is None:
        return None
    core = str(raw).strip().lstrip("vV").split("-")[0].split("+")[0]
    match = re.match(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?$", core)
    if not match:
        return None
    major, minor, patch = match.groups()
    return f"{int(major)}.{int(minor or 0)}.{int(patch or 0)}"


def discover_children(repo_dir: Path) -> list[dict]:
    children: list[dict] = []
    seen: dict[str, str] = {}

    # Convention first: when the repo has a top-level skills/ directory, that is
    # the published set. Scanning the whole tree instead picks up decoys such as
    # larksuite/cli's internal/qualitygate/skillscan/testdata/skills/lark-demo,
    # which is a linter fixture, not a shippable skill.
    scan_root = repo_dir / "skills" if (repo_dir / "skills").is_dir() else repo_dir

    for skill_md in sorted(scan_root.rglob("SKILL.md")):
        rel = skill_md.relative_to(repo_dir)
        segments = [s.lower() for s in rel.parts[:-1]]
        if any(seg in EXCLUDED_SEGMENTS for seg in segments):
            continue
        if not segments:
            continue  # repo root itself is a single skill, not a collection

        child_id = rel.parts[-2]
        if not re.match(r"^[a-z0-9-]+$", child_id):
            print(f"  ! skipped {rel.parent}: directory name is not a valid skill id")
            continue
        if child_id in seen:
            print(f"  ! skipped {rel.parent}: id '{child_id}' already taken by {seen[child_id]}")
            continue
        seen[child_id] = str(rel.parent)

        fm = parse_frontmatter(skill_md)
        child: dict = {"id": child_id, "path": str(rel.parent)}
        name = fm.get("display_name") or fm.get("name")
        if name and str(name) != child_id:
            child["name"] = str(name)
        version = normalize_version(fm.get("version"))
        if version:
            child["version"] = version
        description = fm.get("description")
        if description:
            child["i18n"] = {
                "zh-CN": {"shortDesc": first_sentence(description)},
                "en-US": {"shortDesc": first_sentence(description)},
            }
        children.append(child)

    return children


def process(entry_id: str, *, check: bool = False) -> bool:
    entry_path = SKILLS_DIR / entry_id / "entry.json"
    if not entry_path.exists():
        print(f"{entry_id}: no entry.json")
        return False

    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    source = entry.get("source", {})
    if source.get("kind") != "git":
        print(f"{entry_id}: only git sources can be collections (kind={source.get('kind')})")
        return False
    if check and source.get("path") is not None:
        print(f"{entry_id}: stale — collection source.path must be omitted")
        return False
    if check and not source.get("ref"):
        print(
            f"{entry_id}: SKIP — source.ref is not pinned; "
            "a mutable source cannot have a deterministic generated-output check"
        )
        return True

    print(f"{entry_id}: cloning {source['repoUrl']} …")
    with tempfile.TemporaryDirectory(prefix=f"collection-{entry_id}-") as tmp:
        repo_dir = Path(tmp) / "repo"
        try:
            clone_pinned(source["repoUrl"], source.get("repoBranch", "main"), source.get("ref"), repo_dir)
        except RuntimeError as err:
            print(f"{entry_id}: {err}")
            return False
        children = discover_children(repo_dir)

    if not children:
        print(f"{entry_id}: no sub-skills found — not a collection?")
        return False

    if check:
        if entry.get("children") != children:
            print(
                f"{entry_id}: stale — declared children differ from the "
                f"{len(children)} children discovered at the pinned source"
            )
            return False
        print(f"{entry_id}: OK ({len(children)} children)")
        return True

    entry.pop("children", None)
    entry["children"] = children
    # source.path is mutually exclusive with children (the client rejects both).
    entry.get("source", {}).pop("path", None)
    entry_path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{entry_id}: wrote {len(children)} children")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare generated children with entry.json without writing files",
    )
    parser.add_argument("ids", nargs="*", help="collection entry IDs (default: every declared collection)")
    args = parser.parse_args(argv)

    ids = args.ids
    if not ids:
        ids = sorted(
            p.parent.name
            for p in SKILLS_DIR.glob("*/entry.json")
            if "children" in json.loads(p.read_text(encoding="utf-8"))
        )
        if not ids:
            print("no collection entries found; pass ids explicitly")
            return 1

    failed = [entry_id for entry_id in ids if not process(entry_id, check=args.check)]
    if failed:
        print(f"\nfailed: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
