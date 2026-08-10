#!/usr/bin/env python3
"""Compile per-page scene files from slides_plan.md and prompts.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


HEADING = re.compile(r"^##\s+(\d+)\.\s+\[([^]]+)]\s+(.+?)\s*$")


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def parse_plan(path: Path) -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    current: dict[str, str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        match = HEADING.match(line)
        if match:
            number = int(match.group(1))
            current = {"page_type": match.group(2), "title": match.group(3), "layout_id": ""}
            result[number] = current
        elif current and (line.startswith("布局：") or line.startswith("布局:")):
            current["layout_id"] = line.split(":" if ":" in line else "：", 1)[1].strip()
    return result


def upgrade_metadata(path: Path, prompts: dict) -> dict:
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["schema_version"] = 2
    metadata.setdefault("current_revision", None)
    metadata.setdefault("style_id", prompts.get("style_id"))
    metadata.setdefault("variants", {
        "image": {"status": "not_built", "artifact": None, "slides": {}},
        "editable": {"status": "not_built", "artifact": None, "slides": {}},
    })
    metadata.setdefault("environment", {"preflight_report": None, "status": "pending"})
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True)
    parser.add_argument("--force", action="store_true", help="Replace existing scene content instead of preserving elements.")
    parser.add_argument("--emit-editable-inventory", action="store_true", help="Derive a full editable inventory under cache/editable/.")
    args = parser.parse_args()

    session = Path(args.session).resolve()
    prompts_path = session / "prompts.json"
    plan_path = session / "slides_plan.md"
    metadata_path = session / "metadata.json"
    for path in (prompts_path, plan_path, metadata_path):
        if not path.is_file():
            raise SystemExit(f"missing required session file: {path}")

    prompts = json.loads(prompts_path.read_text(encoding="utf-8"))
    metadata = upgrade_metadata(metadata_path, prompts)
    plan = parse_plan(plan_path)
    prompt_slides = {int(row["slide_number"]): row for row in prompts.get("slides", [])}
    numbers = sorted(set(plan) | set(prompt_slides))
    if not numbers:
        raise SystemExit("no slides found in slides_plan.md or prompts.json")

    scenes_dir = session / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    written = []
    compiled_scenes = []
    for number in numbers:
        info = plan.get(number, {})
        prompt = prompt_slides.get(number, {})
        scene_path = scenes_dir / f"slide-{number:03d}.scene.json"
        old = json.loads(scene_path.read_text(encoding="utf-8")) if scene_path.is_file() and not args.force else {}
        generation = {
            "prompt": prompt.get("prompt", old.get("generation", {}).get("prompt", "")),
            "reference_images": prompt.get("reference_images", old.get("generation", {}).get("reference_images", [])),
            "asset_reference_images": prompt.get("asset_reference_images", old.get("generation", {}).get("asset_reference_images", [])),
        }
        prompt_hash = canonical_hash(generation)
        scene = {
            "schema_version": 1,
            "slide_id": f"slide-{number:03d}",
            "slide_number": number,
            "revision": int(old.get("revision", 1)),
            "page_type": prompt.get("page_type") or info.get("page_type") or old.get("page_type", "other"),
            "style_id": prompt.get("style_id") or prompts.get("style_id") or metadata.get("style_id"),
            "layout_id": prompt.get("layout_id") or info.get("layout_id") or old.get("layout_id") or None,
            "canvas": old.get("canvas", {"width": 1920, "height": 1080}),
            "content": {
                "title": info.get("title") or old.get("content", {}).get("title", ""),
                "message": old.get("content", {}).get("message", ""),
                "facts": old.get("content", {}).get("facts", []),
            },
            "generation": generation,
            "elements": old.get("elements", []),
            "dependencies": {"scene_hash": "", "prompt_hash": prompt_hash, "asset_hashes": old.get("dependencies", {}).get("asset_hashes", [])},
        }
        hashable = dict(scene)
        hashable.pop("revision", None)
        hashable["dependencies"] = {"prompt_hash": prompt_hash, "asset_hashes": scene["dependencies"]["asset_hashes"]}
        next_hash = canonical_hash(hashable)
        previous_hash = old.get("dependencies", {}).get("scene_hash")
        if old and previous_hash != next_hash:
            scene["revision"] = int(old.get("revision", 1)) + 1
        scene["dependencies"]["scene_hash"] = next_hash
        scene_path.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(str(scene_path))
        compiled_scenes.append(scene)
    inventory_path = None
    if args.emit_editable_inventory:
        items = []
        for scene in compiled_scenes:
            for element in scene.get("elements", []):
                item = dict(element)
                element_type = item.pop("type", "unresolved")
                item["class"] = "unresolved" if element_type == "semantic_visual" else element_type
                item["bbox_px"] = item.pop("bbox")
                item["slide"] = scene["slide_number"]
                items.append(item)
        inventory = {
            "schema_version": 1,
            "source": "scene-derived",
            "slide_size_px": [compiled_scenes[0]["canvas"]["width"], compiled_scenes[0]["canvas"]["height"]],
            "font_face": metadata.get("environment", {}).get("selected_font"),
            "items": items,
        }
        inventory_path = session / "cache" / "editable" / "visual_inventory.json"
        inventory_path.parent.mkdir(parents=True, exist_ok=True)
        inventory_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"session": str(session), "scene_count": len(written), "scenes": written, "editable_inventory": str(inventory_path) if inventory_path else None}, ensure_ascii=False))


if __name__ == "__main__":
    main()
