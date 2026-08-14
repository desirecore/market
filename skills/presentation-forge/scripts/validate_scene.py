#!/usr/bin/env python3
"""Validate scene files without external jsonschema dependencies."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ALLOWED_TYPES = {"text", "shape", "line", "connector", "image", "chart", "table", "group", "layout_native", "line_native", "connector_native", "semantic_visual", "imagegen_asset", "provided_asset", "unresolved"}
ALLOWED_CAPABILITIES = {"text", "geometry", "style", "rotation", "z-order", "asset"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        scene = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"invalid JSON: {exc}"]
    required = {"schema_version", "slide_id", "slide_number", "revision", "page_type", "canvas", "content", "elements", "dependencies"}
    if missing := required - scene.keys():
        errors.append(f"missing keys: {sorted(missing)}")
    if scene.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    if not re.fullmatch(r"slide-\d{3}", str(scene.get("slide_id", ""))):
        errors.append("slide_id must match slide-001")
    canvas = scene.get("canvas", {})
    if not all(isinstance(canvas.get(k), int) and canvas[k] > 0 for k in ("width", "height")):
        errors.append("canvas width and height must be positive integers")
    seen: set[str] = set()
    for idx, element in enumerate(scene.get("elements", [])):
        element_id = element.get("id")
        if not element_id or element_id in seen:
            errors.append(f"element {idx}: missing or duplicate id")
        seen.add(element_id)
        if element.get("type") not in ALLOWED_TYPES:
            errors.append(f"element {element_id}: unsupported type {element.get('type')}")
        bbox = element.get("bbox")
        if not isinstance(bbox, list) or len(bbox) != 4 or not all(isinstance(v, (int, float)) for v in bbox):
            errors.append(f"element {element_id}: bbox must contain four numbers")
        elif bbox[2] <= 0 or bbox[3] <= 0:
            errors.append(f"element {element_id}: bbox width and height must be positive")
        elif bbox[0] < 0 or bbox[1] < 0 or bbox[0] + bbox[2] > canvas.get("width", 0) + 0.1 or bbox[1] + bbox[3] > canvas.get("height", 0) + 0.1:
            errors.append(f"element {element_id}: bbox must remain inside canvas")
        capabilities = element.get("capabilities", [])
        if not isinstance(capabilities, list) or any(value not in ALLOWED_CAPABILITIES for value in capabilities):
            errors.append(f"element {element_id}: invalid capabilities")
        if not isinstance(element.get("editable"), bool):
            errors.append(f"element {element_id}: editable must be boolean")
        if not isinstance(element.get("z_index"), int) or element.get("z_index", -1) < 0:
            errors.append(f"element {element_id}: z_index must be a non-negative integer")
        if not isinstance(element.get("rotation", 0), (int, float)):
            errors.append(f"element {element_id}: rotation must be numeric")
    deps = scene.get("dependencies", {})
    if not all(key in deps for key in ("scene_hash", "prompt_hash", "asset_hashes")):
        errors.append("dependencies must include scene_hash, prompt_hash and asset_hashes")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Scene JSON file or session/scenes directory.")
    parser.add_argument("--out")
    args = parser.parse_args()
    target = Path(args.path)
    paths = [target] if target.is_file() else sorted(target.glob("*.scene.json"))
    if not paths:
        raise SystemExit(f"no scene files found: {target}")
    results = {str(path): validate(path) for path in paths}
    report = {"status": "FAIL" if any(results.values()) else "PASS", "scene_count": len(paths), "results": results}
    if args.out:
        out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if report["status"] == "FAIL":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
