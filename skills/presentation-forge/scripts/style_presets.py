#!/usr/bin/env python3
"""Resolve presentation style families and their selectable visual variants."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_catalog() -> dict[str, Any]:
    value = json.loads((ROOT / "styles" / "catalog.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("styles/catalog.json must contain an object")
    return value


def resolve_style(style_id: str, variant_id: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    catalog = load_catalog()
    style = next((row for row in catalog.get("styles", []) if row.get("id") == style_id), None)
    if not style:
        raise ValueError(f"unknown style_id: {style_id}")
    variants = style.get("variants") or []
    resolved_variant_id = variant_id or style.get("default_variant")
    variant = next((row for row in variants if row.get("id") == resolved_variant_id), None)
    if not variant:
        raise ValueError(f"unknown style variant: {style_id}/{resolved_variant_id}")
    return style, variant


def merged_design_tokens(style_id: str, variant_id: str | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    style, variant = resolve_style(style_id, variant_id)
    layout_data = json.loads((ROOT / "styles" / style_id / "layouts.json").read_text(encoding="utf-8"))
    tokens = dict(layout_data.get("design_tokens", {}))
    tokens.update(variant.get("design_tokens", {}))
    return style, variant, tokens


def flattened_presets() -> list[dict[str, Any]]:
    presets: list[dict[str, Any]] = []
    for style in load_catalog().get("styles", []):
        for variant in style.get("variants", []):
            _, _, tokens = merged_design_tokens(str(style["id"]), str(variant["id"]))
            presets.append({
                "preset_id": f"{style['id']}--{variant['id']}",
                "style_id": style["id"],
                "variant_id": variant["id"],
                "family_name": style["name"],
                "name": variant["name"],
                "description": variant.get("description", ""),
                "best_for": style.get("best_for", []),
                "typography_profile": style.get("typography_profile"),
                "table_profile": style.get("table_profile"),
                "design_tokens": tokens,
            })
    return presets
