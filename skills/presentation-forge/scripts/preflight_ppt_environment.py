#!/usr/bin/env python3
"""Inspect fonts, build dependencies, and PPT rendering backends before production."""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_FONTS = ("Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", "Arial Unicode MS")


def font_families() -> set[str]:
    fc_list = shutil.which("fc-list")
    if fc_list:
        result = subprocess.run([fc_list, ":", "family"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
        if result.returncode == 0:
            return {name.strip().lower() for line in result.stdout.splitlines() for name in line.split(",") if name.strip()}
    roots = [Path("/System/Library/Fonts"), Path("/Library/Fonts"), Path.home() / "Library/Fonts", Path("/usr/share/fonts")]
    return {path.stem.lower() for root in roots if root.exists() for path in root.rglob("*") if path.suffix.lower() in {".ttf", ".otf", ".ttc"}}


def contains_font(available: set[str], requested: str) -> bool:
    needle = requested.lower().replace(" ", "")
    return any(needle in value.replace(" ", "") or value.replace(" ", "") in needle for value in available)


def render_backends() -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    if platform.system() == "Darwin":
        app = Path("/Applications/Microsoft PowerPoint.app")
        if app.exists():
            found.append({"id": "powerpoint-macos", "path": str(app), "fidelity": "target"})
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path and not any(row["path"] == path for row in found):
            found.append({"id": "libreoffice", "path": path, "fidelity": "approximate"})
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True)
    parser.add_argument("--target", choices=("image-pptx", "editable-pptx", "pdf"), required=True)
    parser.add_argument("--font", action="append", default=[])
    parser.add_argument("--strict-render", action="store_true", help="Fail when no rendering backend is available.")
    parser.add_argument("--render-backend", choices=("auto", "powerpoint", "libreoffice"), default="auto")
    parser.add_argument("--gui-validation-mode", choices=("final-only", "eager", "never"), help="Override session GUI validation policy.")
    parser.add_argument("--skip-render-probe", action="store_true", help="Only discover renderers; do not execute a Chinese smoke export.")
    parser.add_argument("--allow-approximate-render", action="store_true", help="Permit LibreOffice-only smoke export as WARN instead of BLOCKED.")
    args = parser.parse_args()
    session = Path(args.session).resolve(); metadata_path = session / "metadata.json"
    if not metadata_path.is_file():
        raise SystemExit(f"metadata.json missing: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    gui_validation_mode = args.gui_validation_mode or metadata.get("gui_validation_mode", "final-only")
    requested = tuple(args.font) or DEFAULT_FONTS
    available = font_families()
    fonts = [{"name": name, "available": contains_font(available, name)} for name in requested]
    selected_font = next((row["name"] for row in fonts if row["available"]), None)
    dependencies = {name: importlib.util.find_spec(module) is not None for name, module in {"Pillow": "PIL", "python-pptx": "pptx"}.items()}
    backends = render_backends()
    render_probe = None
    errors: list[str] = []; warnings: list[str] = []
    if not all(dependencies.values()):
        errors.append("missing Python build dependency")
    if not selected_font:
        errors.append("none of the requested CJK fonts is available")
    elif selected_font != requested[0]:
        warnings.append(f"font fallback selected: {selected_font}")
    require_backend_now = args.strict_render or gui_validation_mode == "eager"
    if not backends:
        message = "no PowerPoint or LibreOffice rendering backend found"
        if require_backend_now:
            errors.append(message)
        else:
            warnings.append(message)
    elif backends[0]["fidelity"] != "target" and args.target == "editable-pptx":
        warnings.append("LibreOffice render is approximate for Chinese PowerPoint font metrics")
    run_probe = gui_validation_mode == "eager" and not args.skip_render_probe
    if args.target in {"editable-pptx", "pdf"} and run_probe and all(dependencies.values()) and selected_font:
        reports_dir = session / "reports"; reports_dir.mkdir(parents=True, exist_ok=True)
        probe_dir = reports_dir / "render-probe"; probe_dir.mkdir(parents=True, exist_ok=True)
        inventory = {"slide_size_px": [1920, 1080], "font_face": selected_font, "items": [{"id": "probe_title", "class": "text", "text": "企业 AI 知识库 0123 ABC", "bbox_px": [120, 160, 1600, 120], "font_size": 36}]}
        (probe_dir / "inventory.json").write_text(json.dumps(inventory, ensure_ascii=False), encoding="utf-8")
        (probe_dir / "manifest.json").write_text("[]\n", encoding="utf-8")
        smoke_pptx = probe_dir / "font-render-smoke.pptx"
        build = subprocess.run([sys.executable, str(Path(__file__).with_name("build_semantic_deck.py")), "--inventory", str(probe_dir / "inventory.json"), "--manifest", str(probe_dir / "manifest.json"), "--out-pptx", str(smoke_pptx)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        render_report_path = reports_dir / "render-probe.json"
        if render_report_path.exists():
            render_report_path.unlink()
        render_cmd = [
            sys.executable, str(Path(__file__).with_name("render_pptx.py")),
            "--input", str(smoke_pptx), "--out-dir", str(probe_dir),
            "--backend", args.render_backend, "--validation-stage", "intermediate",
            "--gui-validation-mode", gui_validation_mode, "--report", str(render_report_path),
        ]
        if args.allow_approximate_render:
            render_cmd.append("--allow-approximate")
        probe_timed_out = False
        try:
            render = subprocess.run(render_cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=240) if build.returncode == 0 else None
        except subprocess.TimeoutExpired:
            render = None
            probe_timed_out = True
            errors.append("render probe timed out")
        if render_report_path.is_file():
            render_probe = json.loads(render_report_path.read_text(encoding="utf-8"))
        if build.returncode != 0:
            errors.append("Chinese font render probe PPTX build failed")
        elif not probe_timed_out and (render is None or render.returncode != 0):
            errors.append(f"requested render probe failed: {args.render_backend}")
        elif render_probe and render_probe.get("status") == "APPROXIMATE":
            warnings.append("render probe passed only through approximate LibreOffice output")
    probed_backend_id = render_probe.get("selected_backend") if render_probe else None
    selected_backend = next((row for row in backends if row["id"] == probed_backend_id), None)
    if selected_backend is None and backends:
        selected_backend = backends[0]
    status = "BLOCKED" if errors else "WARN" if warnings else "PASS"
    probe_state = "completed" if render_probe else "skipped" if args.skip_render_probe or gui_validation_mode == "never" else "deferred"
    report = {
        "schema_version": 1,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "target": args.target,
        "platform": {"system": platform.system(), "release": platform.release(), "python": platform.python_version()},
        "dependencies": dependencies,
        "fonts": fonts,
        "selected_font": selected_font,
        "render_backends": backends,
        "selected_render_backend": selected_backend,
        "gui_validation_mode": gui_validation_mode,
        "render_probe_state": probe_state,
        "render_probe": render_probe,
        "status": status,
        "errors": errors,
        "warnings": warnings,
    }
    out = session / "reports" / "preflight.json"; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metadata["environment"] = {
        "preflight_report": str(out.relative_to(session)),
        "status": status,
        "selected_font": selected_font,
        "render_backend": selected_backend["id"] if selected_backend else None,
        "render_probe": probe_state,
    }
    metadata["gui_validation_mode"] = gui_validation_mode
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if status == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
