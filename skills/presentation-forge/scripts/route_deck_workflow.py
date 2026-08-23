#!/usr/bin/env python3
"""Select exactly one PPT production route from a structured request."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROUTES = {
    "image-generation": "references/planning-workflow.md",
    "native-editable-deck": "references/native-editable-workflow.md",
    "element-rebuild": "references/semantic-replica-workflow.md",
    "svg-redraw": "SKILL.md#路径-csvg-拆解",
    "native-template-fill": "references/native-template-fill-workflow.md",
}
VALID_VALUES = {
    "delivery_type": {"image-pptx", "editable-pptx", "pdf", "png", "svg", "pptx", "unspecified"},
    "operation": {"create", "fill", "rebuild", "enhance"},
    "input_kind": {"topic", "document", "pptx-template", "pptx-finished", "slide-images", "mixed"},
    "editability": {"image", "editable", "unspecified"},
    "visual_asset_policy": {"native-only", "native-image-assisted", "image-led-editable"},
    "authoring_mode": {"slides-plan", "markdown-canvas"},
    "editor_workflow_mode": {"direct-build", "canvas-first"},
}

DEFAULT_VALUES = {
    "delivery_type": "unspecified",
    "operation": "create",
    "input_kind": "topic",
    "editability": "unspecified",
    "visual_asset_policy": "native-image-assisted",
    "authoring_mode": "markdown-canvas",
    "editor_workflow_mode": "canvas-first",
}


def truthy(value: object) -> bool:
    return value is True


def decide(request: dict[str, object]) -> dict[str, object]:
    delivery = str(request.get("delivery_type") or "unspecified")
    operation = str(request.get("operation") or "create")
    input_kind = str(request.get("input_kind") or "topic")
    editability = str(request.get("editability") or "unspecified")
    visual_asset_policy = str(request.get("visual_asset_policy") or "native-image-assisted")
    authoring_mode = str(request.get("authoring_mode") or "markdown-canvas")
    editor_workflow_mode = str(request.get("editor_workflow_mode") or "canvas-first")
    has_source_pptx = truthy(request.get("has_source_pptx")) or input_kind in {"pptx-template", "pptx-finished"}
    has_new_content = truthy(request.get("has_new_content"))
    has_reference_slides = truthy(request.get("has_reference_slides")) or input_kind == "slide-images"
    preserve_native = truthy(request.get("preserve_native_design"))
    template_fill = truthy(request.get("explicit_template_fill")) or operation == "fill"

    invalid_fields = {
        field: value
        for field, allowed in VALID_VALUES.items()
        if (value := str(request.get(field) or DEFAULT_VALUES[field])) not in allowed
    }
    if invalid_fields:
        return {
            "schema_version": 1,
            "status": "BLOCKED",
            "route": None,
            "authority": None,
            "reason_codes": ["invalid_request_value"],
            "missing_prerequisites": [],
            "blocking_question": None,
            "invalid_fields": invalid_fields,
        }

    reasons: list[str] = []
    missing: list[str] = []
    question = None
    route = None
    status = "PASS"

    if delivery == "pptx" or (delivery == "unspecified" and truthy(request.get("requests_pptx")) and editability == "unspecified"):
        status = "NEEDS_INPUT"
        reasons.append("pptx_editability_ambiguous")
        question = "需要图片型 PPTX，还是可在 PowerPoint 中逐字逐对象编辑的 PPTX？"
    elif operation == "enhance":
        status = "BLOCKED"
        reasons.append("native_enhancement_not_implemented")
        missing.append("notes/audio/animation enhancement route")
    elif template_fill or (has_source_pptx and preserve_native and has_new_content):
        route = "native-template-fill"
        reasons.append("raw_pptx_plus_native_fill_intent")
        if not has_source_pptx:
            missing.append("source_pptx")
        if not has_new_content:
            missing.append("new_content")
    elif delivery == "svg":
        route = "svg-redraw"
        reasons.append("svg_delivery_requested")
        if not has_reference_slides:
            missing.append("reference_slide_image")
    elif editability == "editable" or delivery == "editable-pptx":
        if operation == "create" and not has_reference_slides:
            route = "native-editable-deck"
            reasons.append("new_native_editable_deck_requested")
        else:
            route = "element-rebuild"
            reasons.append("reference_driven_object_editability_required")
            if not has_reference_slides:
                missing.append("reference_slide_image")
    elif editability == "image" or delivery in {"image-pptx", "pdf", "png"}:
        route = "image-generation"
        reasons.append("visual_delivery_without_object_editability")
    elif has_reference_slides and operation == "rebuild":
        status = "NEEDS_INPUT"
        reasons.append("rebuild_delivery_ambiguous")
        question = "重建后需要可编辑 PPTX，还是 SVG？"
    elif operation == "create" and input_kind in {"topic", "document", "mixed"} and delivery == "unspecified":
        route = "native-editable-deck"
        reasons.append("new_presentation_defaults_to_markdown_canvas")
    else:
        status = "NEEDS_INPUT"
        reasons.append("delivery_not_resolved")
        question = "最终需要图片型 PPTX、可编辑 PPTX，还是 SVG？"

    if missing:
        status = "BLOCKED"
    return {
        "schema_version": 1,
        "status": status,
        "route": route,
        "authority": ROUTES.get(route) if route else None,
        "reason_codes": reasons,
        "missing_prerequisites": missing,
        "blocking_question": question,
        "visual_asset_policy": visual_asset_policy if route == "native-editable-deck" else None,
        "authoring_mode": authoring_mode if route == "native-editable-deck" else None,
        "editor_workflow_mode": editor_workflow_mode if route == "native-editable-deck" else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, help="Structured request JSON.")
    parser.add_argument("--session", help="Optional initialized deck session to update.")
    parser.add_argument("--out", help="Decision report path; defaults to session/reports/route-decision.json.")
    args = parser.parse_args()

    request_path = Path(args.request).resolve()
    request = json.loads(request_path.read_text(encoding="utf-8"))
    result = decide(request)
    canonical = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    result["request_fingerprint"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    result["request"] = request

    session = Path(args.session).resolve() if args.session else None
    if args.out:
        out = Path(args.out).resolve()
    elif session:
        out = session / "reports" / "route-decision.json"
    else:
        out = request_path.with_name("route-decision.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if session:
        metadata_path = session / "metadata.json"
        if not metadata_path.is_file():
            raise SystemExit(f"metadata.json missing: {metadata_path}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["route"] = result["route"]
        metadata["route_status"] = result["status"]
        metadata["route_report"] = str(out.relative_to(session))
        if result.get("visual_asset_policy"):
            metadata["visual_asset_policy"] = result["visual_asset_policy"]
        if result.get("authoring_mode"):
            metadata["authoring_mode"] = result["authoring_mode"]
            metadata["content_source"] = "slides.md" if result["authoring_mode"] == "markdown-canvas" else "slides_plan.md"
        if result.get("editor_workflow_mode"):
            metadata["editor_workflow_mode"] = result["editor_workflow_mode"]
            metadata["style_selection_status"] = "pending" if result["editor_workflow_mode"] == "canvas-first" else "auto-selected"
            metadata["editor_export_approval"] = "pending" if result["editor_workflow_mode"] == "canvas-first" else "auto-proceed"
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False))
    if result["status"] == "BLOCKED":
        raise SystemExit(2)
    if result["status"] == "NEEDS_INPUT":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
