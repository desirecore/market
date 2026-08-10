#!/usr/bin/env python3
"""Snapshot, list, and non-destructively roll back a deck session."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


TRACKED_ROOT_FILES = ("metadata.json", "slides_plan.md", "prompts.json", "visual_inventory.json", "asset_manifest.json", "asset_anchors.json", "layout_rules.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def next_revision(versions: Path) -> str:
    values = [int(p.name[1:]) for p in versions.glob("r[0-9][0-9][0-9][0-9]") if p.is_dir()]
    return f"r{(max(values, default=0) + 1):04d}"


def tracked_files(session: Path) -> list[Path]:
    files = [session / name for name in TRACKED_ROOT_FILES if (session / name).is_file()]
    files.extend(sorted((session / "scenes").glob("*.scene.json")))
    return files


def snapshot(session: Path, reason: str, source_revision: str | None = None) -> str:
    versions = session / "versions"; versions.mkdir(parents=True, exist_ok=True)
    revision = next_revision(versions)
    target = versions / revision; target.mkdir()
    records = []
    for source in tracked_files(session):
        rel = source.relative_to(session)
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        records.append({"path": str(rel), "sha256": sha256(source), "size": source.stat().st_size})
    manifest = {
        "revision": revision,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "source_revision": source_revision,
        "files": records,
    }
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metadata_path = session / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["current_revision"] = revision
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return revision


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    snap = sub.add_parser("snapshot"); snap.add_argument("--session", required=True); snap.add_argument("--reason", required=True)
    listing = sub.add_parser("list"); listing.add_argument("--session", required=True)
    rollback = sub.add_parser("rollback"); rollback.add_argument("--session", required=True); rollback.add_argument("--revision", required=True)
    args = parser.parse_args()
    session = Path(args.session).resolve(); versions = session / "versions"
    if args.command == "snapshot":
        print(json.dumps({"revision": snapshot(session, args.reason)}, ensure_ascii=False)); return
    if args.command == "list":
        rows = [json.loads((p / "manifest.json").read_text(encoding="utf-8")) for p in sorted(versions.glob("r[0-9][0-9][0-9][0-9]")) if (p / "manifest.json").is_file()]
        print(json.dumps(rows, ensure_ascii=False)); return
    target = versions / args.revision
    manifest_path = target / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"revision not found: {args.revision}")
    before = snapshot(session, f"automatic snapshot before rollback to {args.revision}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target_paths = {row["path"] for row in manifest["files"]}
    for current in tracked_files(session):
        if str(current.relative_to(session)) not in target_paths:
            current.unlink()
    for row in manifest["files"]:
        source = target / row["path"]
        destination = session / row["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    new_revision = snapshot(session, f"rollback to {args.revision}", source_revision=args.revision)
    print(json.dumps({"status": "rolled_back", "target": args.revision, "safety_snapshot": before, "current_revision": new_revision}, ensure_ascii=False))


if __name__ == "__main__":
    main()
