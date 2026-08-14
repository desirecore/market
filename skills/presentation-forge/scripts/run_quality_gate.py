#!/usr/bin/env python3
"""Run the single final quality gate for every supported PPT route."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from lxml import etree
from validate_ooxml_namespaces import validate_package


def read_json(path: Path, errors: list[str], code: str) -> dict[str, object] | None:
    if not path.is_file():
        errors.append(f"{code}:missing:{path}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{code}:invalid:{exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{code}:not_object:{path}")
        return None
    return value


def pptx_slide_count(path: Path) -> int:
    if not zipfile.is_zipfile(path):
        return 0
    with zipfile.ZipFile(path) as archive:
        root = etree.fromstring(archive.read("ppt/presentation.xml"))
    namespace = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
    return len(root.xpath("./p:sldIdLst/p:sldId", namespaces=namespace))


def status_is_pass(report: dict[str, object] | None) -> bool:
    return bool(report) and str(report.get("status", "")).upper() in {"PASS", "OK"}


def check_final_render(session: Path, artifact: Path, metadata: dict[str, object], errors: list[str], warnings: list[str], checks: list[dict[str, object]]) -> None:
    mode = str(metadata.get("gui_validation_mode") or "legacy")
    if mode == "legacy":
        return
    if mode == "never":
        warnings.append("final_render:skipped_by_policy")
        checks.append({"id": "final_powerpoint_render", "status": "SKIPPED", "mode": mode})
        return
    report = read_json(session / "reports" / "final-render.json", errors, "final_render")
    if not report:
        return
    status = str(report.get("status", "FAIL")).upper()
    checks.append({"id": "final_powerpoint_render", "status": status, "mode": mode, "backend": report.get("selected_backend")})
    if status != "PASS":
        errors.append(f"final_render:{status.lower()}")
    if report.get("validation_stage") != "final":
        errors.append("final_render:not_final_stage")
    if report.get("gui_validation_mode") != mode:
        errors.append("final_render:mode_mismatch")
    if report.get("selected_backend") != "powerpoint-macos":
        errors.append("final_render:not_target_powerpoint")
    try:
        rendered_input = Path(str(report.get("input"))).resolve()
    except (TypeError, ValueError):
        rendered_input = Path()
    if rendered_input != artifact:
        errors.append("final_render:artifact_mismatch")
    try:
        rendered_output = Path(str(report.get("output"))).resolve()
    except (TypeError, ValueError):
        rendered_output = Path()
    if not rendered_output.is_file() or not rendered_output.read_bytes().startswith(b"%PDF-"):
        errors.append("final_render:output_missing_or_invalid")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--route", choices=("image-generation", "native-editable-deck", "element-rebuild", "svg-redraw", "native-template-fill"))
    parser.add_argument("--out")
    args = parser.parse_args()

    session = Path(args.session).resolve()
    artifact = Path(args.artifact).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict[str, object]] = []

    metadata_path = session / "metadata.json"
    metadata = read_json(metadata_path, errors, "metadata") or {}
    decision = read_json(session / "reports" / "route-decision.json", errors, "route_decision")
    route = args.route or str(metadata.get("route") or (decision or {}).get("route") or "")
    if route not in {"image-generation", "native-editable-deck", "element-rebuild", "svg-redraw", "native-template-fill"}:
        errors.append(f"route:unsupported:{route or 'missing'}")
    if decision:
        if decision.get("status") != "PASS":
            errors.append(f"route_decision:not_pass:{decision.get('status')}")
        if decision.get("route") != route:
            errors.append("route_decision:mismatch")
    if metadata.get("route") != route:
        errors.append("metadata_route:mismatch")
    if not artifact.is_file():
        errors.append(f"artifact:missing:{artifact}")
    elif artifact.suffix.lower() == ".pptx":
        count = pptx_slide_count(artifact)
        checks.append({"id": "pptx_package", "slide_count": count})
        if count < 1:
            errors.append("artifact:invalid_pptx")
        namespace_report = validate_package(artifact)
        checks.append({
            "id": "ooxml_namespace_integrity",
            "status": namespace_report["status"],
            "checked_parts": namespace_report["checked_parts"],
            "checked_references": namespace_report["checked_references"],
        })
        if namespace_report["status"] != "PASS":
            for item in namespace_report["errors"]:
                errors.append(f"ooxml_namespace:{item.get('code')}:{item.get('part', '')}:{item.get('prefix', '')}")
        if route in {"native-editable-deck", "element-rebuild", "native-template-fill"} and metadata.get("typography_profile"):
            typography = read_json(session / "reports" / "typography-validation.json", errors, "typography_validation")
            if typography:
                typography_status = str(typography.get("status", "FAIL")).upper()
                checks.append({
                    "id": "typography_validation",
                    "status": typography_status,
                    "profile": typography.get("typography_profile"),
                    "table_profile": typography.get("table_profile"),
                })
                if typography.get("typography_profile") != metadata.get("typography_profile"):
                    errors.append("typography_validation:profile_mismatch")
                if typography.get("table_profile") != metadata.get("table_profile"):
                    errors.append("typography_validation:table_profile_mismatch")
                if typography_status in {"FAIL", "ERROR", "BLOCKED"}:
                    errors.append(f"typography_validation:{typography_status.lower()}")
                elif typography_status in {"WARN", "NOT_CHECKED"}:
                    warnings.append(f"typography_validation:{typography_status.lower()}")

    outline_mode = metadata.get("outline_review_mode", "legacy")
    outline_states = {"approved", "confirmed", "waived"}
    if outline_mode == "continuous":
        outline_states.add("auto-proceed")

    if route in {"image-generation", "native-editable-deck", "element-rebuild"}:
        design_quality = read_json(session / "reports" / "design-quality.json", errors, "design_quality")
        if design_quality:
            design_status = str(design_quality.get("status", "FAIL")).upper()
            checks.append({
                "id": "anti_ai_slop_design_gate",
                "status": design_status,
                "error_count": design_quality.get("error_count", 0),
                "warning_count": design_quality.get("warning_count", 0),
            })
            if design_status in {"FAIL", "ERROR", "BLOCKED"}:
                errors.append(f"design_quality:{design_status.lower()}")
            elif design_status == "WARN":
                warnings.append("design_quality:warn")

    if route == "image-generation":
        if metadata.get("outline_approval") not in outline_states:
            errors.append("outline_approval:not_approved")
        if metadata.get("smoke_approval") not in {"approved", "confirmed", "skipped", "waived"}:
            errors.append("smoke_approval:not_approved")
        images = sorted({*session.glob("generated/*.png"), *session.glob("final/*.png")})
        checks.append({"id": "final_images", "count": len(images)})
        if not images:
            errors.append("final_images:missing")
        if artifact.suffix.lower() == ".pptx" and images and pptx_slide_count(artifact) != len(images):
            errors.append("image_slide_count:mismatch")

    elif route == "native-editable-deck":
        if metadata.get("editor_workflow_mode") == "canvas-first":
            if metadata.get("style_selection_status") != "confirmed":
                errors.append("canvas_style:not_confirmed")
            if metadata.get("editor_export_approval") != "approved":
                errors.append("canvas_export:not_approved")
        if metadata.get("outline_approval") not in outline_states:
            errors.append("outline_approval:not_approved")
        spec = read_json(session / "analysis" / "native_deck_spec.json", errors, "native_deck_spec")
        editor_manifest = read_json(session / "reports" / "editor-manifest.json", errors, "editor_manifest") if metadata.get("editor_workflow_mode") == "canvas-first" else None
        build_report = read_json(session / "reports" / "native-editable-build.json", errors, "native_editable_build")
        visual_policy = str(metadata.get("visual_asset_policy") or "native-image-assisted")
        if spec and spec.get("visual_asset_policy") != visual_policy:
            errors.append("native_deck_spec:visual_asset_policy_mismatch")
        if spec and editor_manifest:
            spec_count = len(spec.get("slides", [])) if isinstance(spec.get("slides"), list) else 0
            manifest_slides = editor_manifest.get("slides", []) if isinstance(editor_manifest.get("slides"), list) else []
            manifest_count = int(editor_manifest.get("slide_count", len(manifest_slides)))
            artifact_count = pptx_slide_count(artifact)
            checks.append({"id": "canvas_slide_parity", "spec": spec_count, "manifest": manifest_count, "pptx": artifact_count})
            if not (spec_count == manifest_count == len(manifest_slides) == artifact_count):
                errors.append(f"canvas_slide_parity:mismatch:{spec_count}:{manifest_count}:{len(manifest_slides)}:{artifact_count}")
        if build_report:
            if not status_is_pass(build_report):
                errors.append("native_editable_build:not_pass")
            if build_report.get("visual_asset_policy") != visual_policy:
                errors.append("native_editable_build:visual_asset_policy_mismatch")
            if visual_policy == "image-led-editable" and int(build_report.get("image2_assets", 0)) < 1:
                errors.append("native_editable_build:image2_asset_required")
            checks.append({
                "id": "native_editable_objects",
                "native_text_objects": build_report.get("native_text_objects", 0),
                "native_shapes": build_report.get("native_shapes", 0),
                "native_tables": build_report.get("native_tables", 0),
                "office_charts": build_report.get("office_charts", 0),
                "image_objects": build_report.get("image_objects", 0),
                "image2_assets": build_report.get("image2_assets", 0),
            })
        font_report = read_json(session / "reports" / "font-validation.json", errors, "font_validation")
        if font_report and not status_is_pass(font_report):
            errors.append("font_validation:not_pass")
        editability = read_json(session / "reports" / "editability-audit.json", errors, "editability_audit")
        if editability:
            if str(editability.get("status", "PASS")).upper() not in {"PASS", "OK"}:
                errors.append("editability_audit:not_pass")
            if "deck_looks_image_only" in editability.get("deck_flags", []):
                errors.append("editability_audit:image_only")
        if isinstance(metadata.get("editor"), dict) and metadata["editor"].get("status") == "rebuild_required":
            errors.append("editor_canvas:changes_not_rebuilt")
        check_final_render(session, artifact, metadata, errors, warnings, checks)

    elif route == "element-rebuild":
        preflight = read_json(session / "reports" / "preflight.json", errors, "preflight")
        if preflight and preflight.get("status") == "BLOCKED":
            errors.append("preflight:blocked")
        elif preflight and preflight.get("status") == "WARN":
            warnings.append("preflight:warn")
        font_report = read_json(session / "reports" / "font-validation.json", errors, "font_validation")
        if font_report and not status_is_pass(font_report):
            errors.append("font_validation:not_pass")
        build_report = read_json(session / "reports" / "build_report.json", errors, "build_report")
        if build_report:
            if build_report.get("status") == "FAIL":
                errors.append("build_report:fail")
            error_count = ((build_report.get("layout_qa") or {}) if isinstance(build_report.get("layout_qa"), dict) else {}).get("error_count")
            if error_count not in {0, None}:
                errors.append(f"layout_qa:error_count:{error_count}")
        editability = read_json(session / "reports" / "editability-audit.json", errors, "editability_audit")
        if editability:
            if str(editability.get("status", "PASS")).upper() not in {"PASS", "OK"}:
                errors.append("editability_audit:not_pass")
            if "deck_looks_image_only" in editability.get("deck_flags", []):
                errors.append("editability_audit:image_only")
        semantic_report = session / "reports" / "semantic-validation.md"
        if not semantic_report.is_file():
            errors.append(f"semantic_validation:missing:{semantic_report}")
        elif "- Result status: PASS" not in semantic_report.read_text(encoding="utf-8"):
            errors.append("semantic_validation:not_pass")
        check_final_render(session, artifact, metadata, errors, warnings, checks)

    elif route == "svg-redraw":
        svgs = sorted(session.glob("final/*.svg"))
        checks.append({"id": "final_svg", "count": len(svgs)})
        if not svgs:
            errors.append("final_svg:missing")
        validation = read_json(session / "reports" / "svg-validation.json", errors, "svg_validation")
        if validation and not status_is_pass(validation):
            errors.append("svg_validation:not_pass")

    elif route == "native-template-fill":
        plan = read_json(session / "analysis" / "fill_plan.json", errors, "fill_plan")
        if plan and plan.get("status") != "confirmed":
            errors.append("fill_plan:not_confirmed")
        check_report = read_json(session / "analysis" / "check_report.json", errors, "fill_check")
        if check_report and int(check_report.get("error_count", 0)) != 0:
            errors.append(f"fill_check:error_count:{check_report.get('error_count')}")
        validation = read_json(session / "reports" / "native-template-validation.json", errors, "native_template_validation")
        if validation and not status_is_pass(validation):
            errors.append("native_template_validation:not_pass")
        check_final_render(session, artifact, metadata, errors, warnings, checks)

    status = "BLOCKED" if errors else "WARN" if warnings else "PASS"
    report = {
        "schema_version": 1,
        "status": status,
        "route": route,
        "artifact": str(artifact),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }
    out = Path(args.out).resolve() if args.out else session / "reports" / "quality-gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if metadata_path.is_file():
        metadata["final_qa"] = status.lower()
        if metadata.get("gui_validation_mode") == "never":
            metadata["final_powerpoint_validation"] = "skipped"
        elif any(check.get("id") == "final_powerpoint_render" and check.get("status") == "PASS" for check in checks):
            metadata["final_powerpoint_validation"] = "pass"
        elif metadata.get("gui_validation_mode") in {"final-only", "eager"}:
            metadata["final_powerpoint_validation"] = "blocked"
        metadata["quality_gate_report"] = str(out.relative_to(session))
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if status == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
