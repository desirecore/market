#!/usr/bin/env python3
"""Download pin-fixed optional assets and verify SHA-256.

This script only performs HTTP GET of URLs listed in the manifest and compares
each file to the recorded SHA-256 digest. It never executes downloaded files,
never runs remote scripts, and never starts a download unless you invoke it
explicitly with --manifest and --dest.

Example:
  python3 scripts/fetch-optional-assets.py \\
    --manifest references/fetch-manifest.json \\
    --dest /absolute/path/outside-the-skill \\
    --group required-for-B-audio
"""
from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import sys
import urllib.request
from pathlib import Path

CHUNK = 1024 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            data = fh.read(CHUNK)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "desirecore-market-fetch-optional-assets/1"})
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp, tmp.open("wb") as out:
        while True:
            data = resp.read(CHUNK)
            if not data:
                break
            out.write(data)
    tmp.replace(dest)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Fetch pin-fixed optional assets and verify SHA-256. Does not execute downloads.")
    p.add_argument("--manifest", required=True, type=Path, help="Path to references/fetch-manifest.json")
    p.add_argument("--dest", required=True, type=Path, help="Absolute directory outside the skill; files are written at dest/<upstream path>")
    p.add_argument("--group", action="append", dest="groups", help="Limit to one or more manifest groups. Repeatable. Default: all groups.")
    p.add_argument("--dry-run", action="store_true", help="Print planned downloads without writing files.")
    args = p.parse_args(argv)

    manifest_path = args.manifest.resolve()
    if not manifest_path.is_file():
        print(f"manifest not found: {manifest_path}", file=sys.stderr)
        return 2
    dest = args.dest
    if not dest.is_absolute():
        print("--dest must be an absolute path", file=sys.stderr)
        return 2
    # Refuse to write into the skill directory that contains this script by default.
    skill_root = Path(__file__).resolve().parent.parent
    try:
        dest.resolve().relative_to(skill_root)
        print("--dest must be outside this skill directory; copy or symlink verified files in afterwards.", file=sys.stderr)
        return 2
    except ValueError:
        pass

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = data.get("files") or []
    if args.groups:
        wanted = set(args.groups)
        files = [f for f in files if f.get("group") in wanted]
        missing = wanted - {f.get("group") for f in data.get("files") or []}
        if missing:
            print(f"unknown group(s): {sorted(missing)}", file=sys.stderr)
            return 2
    if not files:
        print("no files selected", file=sys.stderr)
        return 2

    errors = 0
    for item in files:
        rel = item["path"]
        url = item["url"]
        expect = item["sha256"].lower()
        target = dest / rel
        print(f"{item.get('group','')}  {rel}  {item.get('bytes',0)} bytes")
        if args.dry_run:
            print(f"  dry-run {url}")
            continue
        if target.is_file() and sha256_file(target) == expect:
            print("  already present and hash matches")
            continue
        try:
            download(url, target)
        except Exception as exc:
            print(f"  DOWNLOAD FAILED {url}: {exc}", file=sys.stderr)
            errors += 1
            continue
        got = sha256_file(target)
        if got != expect:
            print(f"  HASH MISMATCH expected {expect} got {got}", file=sys.stderr)
            errors += 1
            try:
                target.unlink()
            except OSError:
                pass
        else:
            print("  ok")
    if errors:
        print(f"{errors} file(s) failed", file=sys.stderr)
        return 1
    print("all selected files verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
