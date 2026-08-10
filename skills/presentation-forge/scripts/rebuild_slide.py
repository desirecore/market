#!/usr/bin/env python3
"""Prepare or commit a page-level rebuild while preserving other slide caches."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "commit"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--session", required=True)
        cmd.add_argument("--slide", type=int, required=True)
        cmd.add_argument("--variant", choices=("image", "editable"), required=True)
        if name == "commit":
            cmd.add_argument("--artifact", required=True, help="New page image or editable page artifact.")
    args = parser.parse_args()

    session = Path(args.session).resolve()
    scene_path = session / "scenes" / f"slide-{args.slide:03d}.scene.json"
    metadata_path = session / "metadata.json"
    if not scene_path.is_file() or not metadata_path.is_file():
        raise SystemExit("scene or metadata.json missing; run compile_scenes.py first")
    scene = load(scene_path)
    metadata = load(metadata_path)
    variants = metadata.setdefault("variants", {})
    variant = variants.setdefault(args.variant, {"status": "not_built", "artifact": None, "slides": {}})
    slides = variant.setdefault("slides", {})
    key = str(args.slide)
    state = slides.get(key, {})
    scene_hash = scene["dependencies"]["scene_hash"]
    cache_dir = session / "cache" / args.variant / f"slide-{args.slide:03d}"
    cache_dir.mkdir(parents=True, exist_ok=True)

    if args.command == "prepare":
        stale = state.get("scene_hash") != scene_hash or not state.get("artifact") or not (session / state.get("artifact", "")).exists()
        payload = {
            "slide": args.slide,
            "variant": args.variant,
            "scene": str(scene_path),
            "scene_hash": scene_hash,
            "status": "stale" if stale else "clean",
            "reason": "scene_or_artifact_changed" if stale else "cache_hit",
            "generation": scene.get("generation", {}),
            "elements": scene.get("elements", []) if args.variant == "editable" else [],
        }
        save(cache_dir / "rebuild-plan.json", payload)
        if args.variant == "image":
            save(cache_dir / "prompt.json", {
                "slide_number": args.slide,
                "scene_hash": scene_hash,
                "style_id": scene.get("style_id"),
                "layout_id": scene.get("layout_id"),
                **scene.get("generation", {}),
            })
        else:
            class_map = {"semantic_visual": "unresolved"}
            items = []
            for element in scene.get("elements", []):
                item = dict(element)
                item["class"] = class_map.get(item.pop("type", "unresolved"), element.get("type"))
                item["bbox_px"] = item.pop("bbox")
                item["slide"] = 1
                items.append(item)
            save(cache_dir / "visual_inventory.json", {
                "schema_version": 1,
                "source_slide_number": args.slide,
                "scene_hash": scene_hash,
                "slide_size_px": [scene["canvas"]["width"], scene["canvas"]["height"]],
                "font_face": metadata.get("environment", {}).get("selected_font"),
                "items": items,
            })
        if stale:
            slides[key] = {**state, "status": "stale", "scene_hash": scene_hash}
            variant["status"] = "partial_stale"
            save(metadata_path, metadata)
        print(json.dumps(payload, ensure_ascii=False))
        return

    artifact = Path(args.artifact).resolve()
    if not artifact.is_file():
        raise SystemExit(f"artifact not found: {artifact}")
    try:
        artifact_ref = str(artifact.relative_to(session))
    except ValueError:
        artifact_ref = str(artifact)
    slides[key] = {
        "status": "built",
        "scene_hash": scene_hash,
        "artifact": artifact_ref,
        "artifact_hash": sha256(artifact),
        "built_at": datetime.now(timezone.utc).isoformat(),
    }
    scene_count = len(list((session / "scenes").glob("*.scene.json")))
    built_count = sum(row.get("status") == "built" for row in slides.values())
    variant["status"] = "built" if scene_count and built_count == scene_count else "partial"
    save(metadata_path, metadata)
    payload = {"slide": args.slide, "variant": args.variant, **slides[key]}
    save(cache_dir / "build-state.json", payload)
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
