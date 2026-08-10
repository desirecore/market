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
    args = parser.parse_args()

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
        "slides": [],
    }
    metadata = {
        "schema_version": 2,
        "session_id": session_id,
        "title": args.title,
        "delivery_type": args.delivery_type,
        "style_id": args.style_id,
        "current_revision": None,
        "editability_confirmed": True,
        "status": "planning",
        "route": None,
        "route_status": "pending",
        "route_report": None,
        "outline_approval": "pending",
        "smoke_slide": None,
        "smoke_approval": "pending",
        "final_qa": "pending",
        "quality_gate_report": None,
        "variants": {
            "image": {"status": "not_built", "artifact": None, "slides": {}},
            "editable": {"status": "not_built", "artifact": None, "slides": {}},
        },
        "environment": {"preflight_report": None, "status": "pending"},
    }

    (session / "slides_plan.md").write_text(plan, encoding="utf-8")
    (session / "prompts.json").write_text(json.dumps(prompts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (session / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"session_id": session_id, "path": str(session)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
