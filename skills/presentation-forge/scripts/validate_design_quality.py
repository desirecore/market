#!/usr/bin/env python3
"""Run the pre-build Anti-AI-slop design gate for presentation sessions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


NOTE_MARKER = re.compile(r"(?:设计说明|讲者备注|演讲备注|配图建议|排版说明|speaker\s*notes?|design\s*notes?|prompt\s*:)", re.I)
HARD_EFFECT_KEYS = {"shadow": "default-shadow", "gradient": "default-gradient"}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def finding(code: str, severity: str, message: str, slide_number: int | None = None, element_ids: list[str] | None = None) -> dict[str, Any]:
    return {"code": code, "severity": severity, "slide_number": slide_number, "message": message, "element_ids": element_ids or []}


def iter_effects(value: Any, path: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}/{key}"
            disabled = child is None or child is False or (isinstance(child, str) and child.lower() in {"none", "off"})
            if key in HARD_EFFECT_KEYS and not disabled:
                yield HARD_EFFECT_KEYS[key], child_path
            yield from iter_effects(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_effects(child, f"{path}/{index}")


def iter_slide_text(value: Any, path: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"visual_slot", "prompt", "prompt_record", "asset_path", "design_exceptions"}:
                continue
            yield from iter_slide_text(child, f"{path}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_slide_text(child, f"{path}/{index}")
    elif isinstance(value, str):
        yield path, value


def area_ratio(bbox: list[float], width: float, height: float) -> float:
    return float(bbox[2]) * float(bbox[3]) / max(1.0, width * height)


def contains(outer: list[float], inner: list[float]) -> bool:
    margin = 2.0
    return (
        inner[0] >= outer[0] - margin and inner[1] >= outer[1] - margin
        and inner[0] + inner[2] <= outer[0] + outer[2] + margin
        and inner[1] + inner[3] <= outer[1] + outer[3] + margin
    )


def analyze_design(spec: dict[str, Any], scenes: list[dict[str, Any]]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for code, path in iter_effects(spec):
        findings.append(finding(code, "ERROR", f"禁止默认启用阴影或渐变：{path}"))
    for slide in spec.get("slides", []):
        number = int(slide.get("slide_number", 0)) or None
        cards = slide.get("cards") if isinstance(slide.get("cards"), list) else []
        if len(cards) > 4:
            findings.append(finding("meaningless-cardification", "WARN", f"同页出现 {len(cards)} 个卡片；应确认它们确有同级语义，或改用分区、流程、表格。", number))
        for path, text in iter_slide_text(slide):
            if NOTE_MARKER.search(text):
                findings.append(finding("design-notes-in-body", "ERROR", f"页面正文包含设计说明或讲者提示：{path}", number))
        visual = slide.get("visual_slot")
        if isinstance(visual, dict):
            bbox = visual.get("bbox_in")
            if isinstance(bbox, list) and len(bbox) == 4 and area_ratio([float(v) for v in bbox], 13.333333, 7.5) >= 0.85:
                findings.append(finding("full-slide-movable-image", "ERROR", "独立图片覆盖整页或近整页；可编辑模式禁止用可移动图片冒充页面背景。", number))

    for scene in scenes:
        number = int(scene.get("slide_number", 0)) or None
        canvas = scene.get("canvas", {})
        width, height = float(canvas.get("width", 1920)), float(canvas.get("height", 1080))
        elements = scene.get("elements", []) if isinstance(scene.get("elements"), list) else []
        rounded = [row for row in elements if str(row.get("geometry", "")).lower() in {"rounded_rectangle", "round_rect", "rounded-rectangle"}]
        if len(rounded) > 5:
            findings.append(finding("excessive-rounded-rectangles", "WARN", f"本页包含 {len(rounded)} 个圆角矩形；请减少容器层级或改用留白分组。", number, [str(row.get("id")) for row in rounded]))
        shapes = [row for row in elements if row.get("type") == "shape" and isinstance(row.get("bbox"), list)]
        texts = [row for row in elements if row.get("type") == "text" and isinstance(row.get("bbox"), list)]
        for row in elements:
            bbox = row.get("bbox")
            if row.get("type") == "image" and isinstance(bbox, list) and area_ratio(bbox, width, height) >= 0.85:
                findings.append(finding("full-slide-movable-image", "ERROR", "画布中存在覆盖整页或近整页的独立图片对象。", number, [str(row.get("id"))]))
            if row.get("type") == "shape" and isinstance(bbox, list):
                short, long = min(float(bbox[2]), float(bbox[3])), max(float(bbox[2]), float(bbox[3]))
                if short <= 18 and long / max(short, 1.0) >= 12:
                    findings.append(finding("unjustified-accent-strip", "WARN", "检测到窄边强调条；若它不是坐标轴、时间线或有语义的分隔线，请删除。", number, [str(row.get("id"))]))
        for shape in shapes:
            contained = [text for text in texts if contains(shape["bbox"], text["bbox"])]
            if contained:
                findings.append(finding("shape-with-overlay-textbox", "WARN", "形状上叠加了独立文本框；优先把文字写入形状本身，或使用无容器的排版分组。", number, [str(shape.get("id")), *[str(row.get("id")) for row in contained]]))
        for code, path in iter_effects(scene):
            findings.append(finding(code, "ERROR", f"禁止默认启用阴影或渐变：{path}", number))

    exceptions = spec.get("design_exceptions", []) if isinstance(spec.get("design_exceptions"), list) else []
    for item in findings:
        waiver = next((row for row in exceptions if row.get("code") == item["code"] and row.get("slide_number") in {None, item["slide_number"]} and str(row.get("reason", "")).strip()), None)
        if waiver:
            item["waived"] = True
            item["waiver_reason"] = waiver["reason"]
    active = [item for item in findings if not item.get("waived")]
    errors = [item for item in active if item["severity"] == "ERROR"]
    warnings = [item for item in active if item["severity"] == "WARN"]
    return {
        "schema_version": 1,
        "status": "FAIL" if errors else "WARN" if warnings else "PASS",
        "policy": "anti-ai-slop.v1",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "waived_count": len(findings) - len(active),
        "findings": findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session")
    parser.add_argument("--spec")
    parser.add_argument("--scene-dir")
    parser.add_argument("--out")
    parser.add_argument("--strict-warnings", action="store_true")
    args = parser.parse_args()
    session = Path(args.session).resolve() if args.session else None
    spec_path = Path(args.spec).resolve() if args.spec else None
    if not spec_path and session:
        native = session / "analysis" / "native_deck_spec.json"
        spec_path = native if native.is_file() else session / "prompts.json"
    if not spec_path or not spec_path.is_file():
        raise SystemExit("native deck spec is required")
    scene_dir = Path(args.scene_dir).resolve() if args.scene_dir else (session / "scenes" if session else None)
    scenes = [load(path) for path in sorted(scene_dir.glob("*.scene.json"))] if scene_dir and scene_dir.is_dir() else []
    report = analyze_design(load(spec_path), scenes)
    out = Path(args.out).resolve() if args.out else (session / "reports" / "design-quality.json" if session else None)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if report["status"] == "FAIL" or (args.strict_warnings and report["status"] == "WARN"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
