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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--route", choices=("image-generation", "element-rebuild", "svg-redraw", "native-template-fill"))
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
    if route not in {"image-generation", "element-rebuild", "svg-redraw", "native-template-fill"}:
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

    if route == "image-generation":
        if metadata.get("outline_approval") not in {"approved", "confirmed", "waived"}:
            errors.append("outline_approval:not_approved")
        if metadata.get("smoke_approval") not in {"approved", "confirmed", "skipped", "waived"}:
            errors.append("smoke_approval:not_approved")
        images = sorted({*session.glob("generated/*.png"), *session.glob("final/*.png")})
        checks.append({"id": "final_images", "count": len(images)})
        if not images:
            errors.append("final_images:missing")
        if artifact.suffix.lower() == ".pptx" and images and pptx_slide_count(artifact) != len(images):
            errors.append("image_slide_count:mismatch")

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
        metadata["quality_gate_report"] = str(out.relative_to(session))
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if status == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
