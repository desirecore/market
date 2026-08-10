#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STYLES_ROOT = ROOT / "styles"
REQUIRED_LAYOUTS = {
    "cover-hero",
    "content-structured",
    "process-flow",
    "comparison-two-zone",
    "data-callouts",
    "closing-action",
}
HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def iter_colors(value: object):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"background", "primary", "secondary", "text"}:
                values = child if isinstance(child, list) else [child]
                for item in values:
                    yield item
            yield from iter_colors(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_colors(child)


def main() -> None:
    catalog_path = STYLES_ROOT / "catalog.json"
    if not catalog_path.is_file():
        fail("missing styles/catalog.json")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if catalog.get("schema_version") != 1:
        fail("catalog schema_version must be 1")

    entries = catalog.get("styles")
    if not isinstance(entries, list) or not entries:
        fail("catalog styles must be a non-empty list")
    ids = [entry.get("id") for entry in entries]
    if len(ids) != len(set(ids)):
        fail("duplicate style ids in catalog")

    for entry in entries:
        style_id = entry.get("id")
        if not isinstance(style_id, str) or not re.fullmatch(r"[a-z0-9-]+", style_id):
            fail(f"invalid style id: {style_id!r}")
        style_dir = STYLES_ROOT / style_id
        style_md = style_dir / "STYLE.md"
        layouts_path = style_dir / "layouts.json"
        if not style_md.is_file() or not layouts_path.is_file():
            fail(f"{style_id}: STYLE.md or layouts.json missing")

        data = json.loads(layouts_path.read_text(encoding="utf-8"))
        required_top = {"schema_version", "style_id", "display_name", "global_prompt", "design_tokens", "layouts"}
        missing_top = required_top - data.keys()
        if missing_top:
            fail(f"{style_id}: missing top-level keys {sorted(missing_top)}")
        if data["schema_version"] != 1 or data["style_id"] != style_id:
            fail(f"{style_id}: schema_version or style_id mismatch")
        if data["display_name"] != entry.get("name"):
            fail(f"{style_id}: display name differs from catalog")

        layouts = data.get("layouts")
        if not isinstance(layouts, list):
            fail(f"{style_id}: layouts must be a list")
        layout_ids = [layout.get("id") for layout in layouts]
        if set(layout_ids) != REQUIRED_LAYOUTS or len(layout_ids) != len(REQUIRED_LAYOUTS):
            fail(f"{style_id}: layout ids must equal {sorted(REQUIRED_LAYOUTS)}")
        required_layout = {"id", "page_type", "summary", "content_capacity", "best_for", "avoid_for", "reuse_friendly", "composition"}
        for layout in layouts:
            missing_layout = required_layout - layout.keys()
            if missing_layout:
                fail(f"{style_id}/{layout.get('id')}: missing keys {sorted(missing_layout)}")

        for color in iter_colors(data.get("design_tokens")):
            if not isinstance(color, str) or not HEX_COLOR.fullmatch(color):
                fail(f"{style_id}: invalid color token {color!r}")

    print(f"Style library is valid: {len(entries)} styles, {len(entries) * len(REQUIRED_LAYOUTS)} layouts")


if __name__ == "__main__":
    main()
