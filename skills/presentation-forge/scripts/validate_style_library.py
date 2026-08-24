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
    profiles_path = STYLES_ROOT / "typography-profiles.json"
    if not catalog_path.is_file():
        fail("missing styles/catalog.json")
    if not profiles_path.is_file():
        fail("missing styles/typography-profiles.json")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
    if catalog.get("schema_version") != 2:
        fail("catalog schema_version must be 2")

    entries = catalog.get("styles")
    if not isinstance(entries, list) or not entries:
        fail("catalog styles must be a non-empty list")
    ids = [entry.get("id") for entry in entries]
    if len(ids) != len(set(ids)):
        fail("duplicate style ids in catalog")

    typography_profiles = {row.get("id"): row for row in profiles.get("typography_profiles", [])}
    table_profiles = {row.get("id"): row for row in profiles.get("table_profiles", [])}
    if profiles.get("schema_version") != 1 or not typography_profiles or not table_profiles:
        fail("typography profile catalog must contain typography_profiles and table_profiles")
    required_tokens = {"hero", "section_title", "page_title", "subtitle", "minor_title", "body", "label", "caption", "table"}
    for profile_id, profile in typography_profiles.items():
        if not isinstance(profile_id, str) or not re.fullmatch(r"[a-z0-9-]+", profile_id):
            fail(f"invalid typography profile id: {profile_id!r}")
        missing_tokens = required_tokens - set(profile.get("tokens", {}))
        if missing_tokens:
            fail(f"{profile_id}: missing typography tokens {sorted(missing_tokens)}")
        grid = profile.get("font_size_grid")
        if not isinstance(grid, (int, float)) or grid <= 0:
            fail(f"{profile_id}: font_size_grid must be positive")

    for entry in entries:
        style_id = entry.get("id")
        if not isinstance(style_id, str) or not re.fullmatch(r"[a-z0-9-]+", style_id):
            fail(f"invalid style id: {style_id!r}")
        if entry.get("typography_profile") not in typography_profiles:
            fail(f"{style_id}: unknown typography_profile {entry.get('typography_profile')!r}")
        if entry.get("table_profile") not in table_profiles:
            fail(f"{style_id}: unknown table_profile {entry.get('table_profile')!r}")
        variants = entry.get("variants")
        if not isinstance(variants, list) or len(variants) < 3:
            fail(f"{style_id}: at least three visual variants are required")
        variant_ids = [variant.get("id") for variant in variants]
        if len(variant_ids) != len(set(variant_ids)):
            fail(f"{style_id}: duplicate variant ids")
        if entry.get("default_variant") not in variant_ids:
            fail(f"{style_id}: default_variant must reference a variant")
        for variant in variants:
            variant_id = variant.get("id")
            if not isinstance(variant_id, str) or not re.fullmatch(r"[a-z0-9-]+", variant_id):
                fail(f"{style_id}: invalid variant id {variant_id!r}")
            if not isinstance(variant.get("name"), str) or not variant["name"].strip():
                fail(f"{style_id}/{variant_id}: name is required")
            for color in iter_colors(variant.get("design_tokens")):
                if not isinstance(color, str) or not HEX_COLOR.fullmatch(color):
                    fail(f"{style_id}/{variant_id}: invalid color token {color!r}")
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

    preset_count = sum(len(entry.get("variants", [])) for entry in entries)
    print(f"Style library is valid: {len(entries)} families, {preset_count} presets, {len(entries) * len(REQUIRED_LAYOUTS)} layouts")


if __name__ == "__main__":
    main()
