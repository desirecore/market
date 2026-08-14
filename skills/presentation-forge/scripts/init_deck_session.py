#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


DELIVERY_TYPES = ("image-pptx", "editable-pptx", "pdf", "png", "svg")
SESSION_DIRS = (
    "sources", "references", "analysis", "scenes", "versions", "cache/image", "cache/editable",
    "generated", "assets", "final", "render", "compare", "reports",
)
ROOT = Path(__file__).resolve().parents[1]


def available_style_ids() -> tuple[str, ...]:
    catalog_path = ROOT / "styles" / "catalog.json"
    if not catalog_path.is_file():
        return ()
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    return tuple(entry["id"] for entry in catalog.get("styles", []))


def style_policies(style_id: str | None) -> tuple[str | None, str | None, str | None]:
    if not style_id:
        return None, None, None
    catalog_path = ROOT / "styles" / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entry = next((row for row in catalog.get("styles", []) if row.get("id") == style_id), {})
    return entry.get("typography_profile"), entry.get("table_profile"), entry.get("default_variant")


def slugify(value: str) -> str:
    slug = re.sub(r"[^\w]+", "-", value.lower(), flags=re.UNICODE).replace("_", "-").strip("-")
    return slug[:48] or "deck"


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a session for a new PPT workflow.")
    parser.add_argument("--title", required=True, help="Presentation title.")
    parser.add_argument("--delivery-type", required=True, choices=DELIVERY_TYPES)
    parser.add_argument("--out-root", default="outputs", help="Parent directory for sessions.")
    parser.add_argument("--session-id", help="Explicit session id. Default: timestamp-title slug.")
    style_ids = available_style_ids()
    parser.add_argument("--style-id", choices=style_ids or None, help="Built-in style id from styles/catalog.json.")
    parser.add_argument("--visual-asset-policy", choices=("native-only", "native-image-assisted", "image-led-editable"), help="Image-2 usage policy for native editable decks.")
    parser.add_argument(
        "--editor-workflow-mode",
        choices=("direct-build", "canvas-first"),
        default="direct-build",
        help="canvas-first keeps editable previews in cache until the user explicitly approves PPTX export.",
    )
    parser.add_argument(
        "--outline-review-mode",
        choices=("continuous", "explicit"),
        default="continuous",
        help="continuous proceeds after writing the plan; explicit pauses until the user approves it.",
    )
    parser.add_argument(
        "--gui-validation-mode",
        choices=("final-only", "eager", "never"),
        default="final-only",
        help="Control when PowerPoint/GUI rendering may run. Default: final artifact only.",
    )
    args = parser.parse_args()
    typography_profile, table_profile, style_variant = style_policies(args.style_id)
    visual_asset_policy = args.visual_asset_policy or ("native-image-assisted" if args.delivery_type == "editable-pptx" else None)

    session_id = args.session_id or f"{datetime.now():%Y%m%d-%H%M%S}-{slugify(args.title)}"
    session = Path(args.out_root).expanduser().resolve() / session_id
    if session.exists():
        raise SystemExit(f"Session already exists: {session}")

    session.mkdir(parents=True)
    for name in SESSION_DIRS:
        (session / name).mkdir(parents=True)

    plan = f"""---
title: {args.title}
delivery_type: {args.delivery_type}
style_id: {args.style_id or '待确认'}
style_variant: {style_variant or '待确认'}
typography_profile: {typography_profile or '待确认'}
table_profile: {table_profile or '待确认'}
visual_asset_policy: {visual_asset_policy or '不适用'}
audience: 待确认
goal: 待确认
---

# 逐页计划

<!-- 按 references/planning-workflow.md 添加页面；此文件是内容 source of truth。 -->
"""
    prompts = {
        "schema_version": 1,
        "session_id": session_id,
        "delivery_type": args.delivery_type,
        "style_id": args.style_id,
        "style_variant": style_variant,
        "typography_profile": typography_profile,
        "table_profile": table_profile,
        "visual_asset_policy": visual_asset_policy,
        "slides": [],
    }
    metadata = {
        "schema_version": 4,
        "session_id": session_id,
        "title": args.title,
        "delivery_type": args.delivery_type,
        "style_id": args.style_id,
        "style_variant": style_variant,
        "typography_profile": typography_profile,
        "table_profile": table_profile,
        "visual_asset_policy": visual_asset_policy,
        "editor_workflow_mode": args.editor_workflow_mode,
        "style_selection_status": "pending" if args.editor_workflow_mode == "canvas-first" else "auto-selected",
        "editor_export_approval": "pending" if args.editor_workflow_mode == "canvas-first" else "auto-proceed",
        "current_revision": None,
        "editability_confirmed": True,
        "status": "planning",
        "route": None,
        "route_status": "pending",
        "route_report": None,
        "outline_review_mode": args.outline_review_mode,
        "outline_approval": "auto-proceed" if args.outline_review_mode == "continuous" else "pending",
        "gui_validation_mode": args.gui_validation_mode,
        "final_powerpoint_validation": "skipped" if args.gui_validation_mode == "never" else "pending",
        "smoke_slide": None,
        "smoke_approval": "pending",
        "final_qa": "pending",
        "quality_gate_report": None,
        "variants": {
            "image": {"status": "not_built", "artifact": None, "slides": {}},
            "editable": {"status": "not_built", "artifact": None, "slides": {}},
        },
        "environment": {"preflight_report": None, "status": "pending", "render_probe": "deferred" if args.gui_validation_mode == "final-only" else "pending"},
    }

    (session / "slides_plan.md").write_text(plan, encoding="utf-8")
    (session / "prompts.json").write_text(json.dumps(prompts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (session / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"session_id": session_id, "path": str(session)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
