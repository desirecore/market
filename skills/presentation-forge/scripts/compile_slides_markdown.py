#!/usr/bin/env python3
"""Compile slides.md into a native editable spec, scenes, and an optional editor canvas."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from style_presets import resolve_style

try:
    import yaml as _yaml
except ModuleNotFoundError:  # Keep the editor bridge usable with the system Python.
    _yaml = None


ROOT = Path(__file__).resolve().parents[1]
CANVAS = {"width": 1920, "height": 1080, "unit": "px"}
LAYOUT_TO_ARCHETYPE = {
    "cover": "cover", "cover-left": "cover",
    "content": "content-structured", "cards": "content-structured", "columns": "content-structured",
    "timeline": "process-flow", "process": "process-flow",
    "comparison": "comparison-two-zone",
    "data": "data-callouts", "metrics": "data-callouts",
    "table": "table", "architecture": "architecture",
    "closing": "closing-action", "action": "closing-action",
}
ARCHETYPE_TO_LAYOUT = {
    "cover": "cover", "content-structured": "content", "process-flow": "timeline",
    "comparison-two-zone": "comparison", "data-callouts": "metrics", "table": "table",
    "architecture": "architecture", "closing-action": "closing",
}
DIRECTIVE = re.compile(r'^::(?P<name>[\w-]+)\{(?P<attrs>.*)}\s*$')
ATTR = re.compile(r'([\w-]+)\s*=\s*"([^"]*)"')


def yaml_load(text: str) -> dict[str, Any]:
    if _yaml is not None:
        value = _yaml.safe_load(text) or {}
        if not isinstance(value, dict):
            raise ValueError("slides.md frontmatter must be a mapping")
        return value
    result: dict[str, Any] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"unsupported frontmatter line without PyYAML: {raw}")
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        result[key.strip()] = value
    return result


def yaml_dump(value: dict[str, Any]) -> str:
    if _yaml is not None:
        return _yaml.safe_dump(value, allow_unicode=True, sort_keys=False).strip()
    rows = []
    for key, item in value.items():
        rendered = json.dumps(item, ensure_ascii=False) if isinstance(item, str) else str(item).lower() if isinstance(item, bool) else str(item)
        rows.append(f"{key}: {rendered}")
    return "\n".join(rows)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("slides.md frontmatter is not closed")
    value = yaml_load(text[4:end])
    return value, text[end + 5:]


def split_slides(body: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?m)^---\s*$", body) if part.strip()]


def directive_attrs(line: str, name: str) -> dict[str, str] | None:
    match = DIRECTIVE.match(line.strip())
    if not match or match.group("name") != name:
        return None
    return {key: value for key, value in ATTR.findall(match.group("attrs"))}


def parse_sections(lines: list[str]) -> tuple[list[dict[str, Any]], list[str], list[list[str]]]:
    sections: list[dict[str, Any]] = []
    bullets: list[str] = []
    table_rows: list[list[str]] = []
    current: dict[str, Any] | None = None
    for raw in lines:
        line = raw.strip()
        if line.startswith("## "):
            current = {"title": line[3:].strip(), "body_lines": [], "points": []}
            sections.append(current)
        elif re.match(r"^[-*+]\s+", line):
            value = re.sub(r"^[-*+]\s+", "", line).strip()
            (current["points"] if current else bullets).append(value)
        elif line.startswith("|") and line.endswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells):
                table_rows.append(cells)
        elif line and not line.startswith("::") and current:
            current["body_lines"].append(line)
    for section in sections:
        section["body"] = "\n".join(section.pop("body_lines")).strip()
    return sections, bullets, table_rows


def infer_layout(index: int, count: int, explicit: str | None) -> str:
    if explicit:
        if explicit not in LAYOUT_TO_ARCHETYPE:
            raise ValueError(f"unsupported Markdown layout: {explicit}")
        return explicit
    if index == 0:
        return "cover"
    return "closing" if index == count - 1 else "content"


def parse_slide(block: str, index: int, count: int) -> dict[str, Any]:
    lines = block.splitlines()
    title = next((line[2:].strip() for line in lines if line.startswith("# ")), "")
    if not title:
        raise ValueError(f"slide {index + 1} is missing a '# ' title")
    quote = "\n".join(line[1:].strip() for line in lines if line.startswith(">" )).strip()
    layout_value: str | None = None
    visual: dict[str, str] | None = None
    for line in lines:
        attrs = directive_attrs(line, "layout")
        if attrs is not None:
            layout_value = attrs.get("type")
        visual_attrs = directive_attrs(line, "visual")
        if visual_attrs is not None:
            visual = visual_attrs
    layout = infer_layout(index, count, layout_value)
    archetype = LAYOUT_TO_ARCHETYPE[layout]
    sections, bullets, table_rows = parse_sections(lines)
    row: dict[str, Any] = {"slide_number": index + 1, "archetype": archetype, "title": title}
    if quote:
        row["subtitle" if archetype == "cover" else "key_message"] = quote

    if archetype == "content-structured":
        cards = [{"title": item["title"], "body": item["body"] or "\n".join(item["points"])} for item in sections]
        if not cards:
            cards = [{"title": item, "body": ""} for item in bullets]
        if not 2 <= len(cards) <= 6:
            raise ValueError(f"slide {index + 1} content layout requires 2-6 '##' sections or bullets")
        row["cards"] = cards
    elif archetype == "process-flow":
        steps = [{"title": item["title"], "body": item["body"] or "\n".join(item["points"])} for item in sections]
        if not 3 <= len(steps) <= 5:
            raise ValueError(f"slide {index + 1} timeline layout requires 3-5 '##' steps")
        row["steps"] = steps
    elif archetype == "comparison-two-zone":
        if len(sections) != 2:
            raise ValueError(f"slide {index + 1} comparison layout requires exactly two '##' sections")
        for key, item in zip(("left", "right"), sections):
            points = item["points"] or ([item["body"]] if item["body"] else [])
            row[key] = {"title": item["title"], "points": points}
    elif archetype == "data-callouts":
        metrics = [{"value": item["title"], "label": item["body"] or "\n".join(item["points"])} for item in sections]
        if not 2 <= len(metrics) <= 5:
            raise ValueError(f"slide {index + 1} metrics layout requires 2-5 '##' sections")
        row["metrics"] = metrics
    elif archetype == "table":
        if len(table_rows) < 2:
            raise ValueError(f"slide {index + 1} table layout requires a Markdown table")
        row["headers"], row["rows"] = table_rows[0], table_rows[1:]
        row["column_types"] = ["text"] * len(row["headers"])
    elif archetype == "architecture":
        layers = [{"title": item["title"], "body": item["body"] or "\n".join(item["points"])} for item in sections]
        if not layers:
            raise ValueError(f"slide {index + 1} architecture layout requires '##' layers")
        row["layers"] = layers
    elif archetype == "closing-action":
        actions = bullets or [item["title"] for item in sections]
        if actions:
            row["actions"] = actions[:5]

    if visual and visual.get("asset"):
        backend = visual.get("backend", "provided")
        row["visual_slot"] = {
            "backend": backend,
            "source_type": "imagegen_asset" if backend == "image-2" else "provided_asset",
            "status": visual.get("status", "generated"),
            "asset_path": visual["asset"],
            "prompt_record": visual.get("prompt"),
        }
    return row


def parse_markdown(text: str, metadata: dict[str, Any] | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    frontmatter, body = split_frontmatter(text)
    blocks = split_slides(body)
    if not blocks:
        raise ValueError("slides.md contains no slides")
    metadata = metadata or {}
    style_id = str(frontmatter.get("style") or metadata.get("style_id") or "consulting-blue-white")
    requested_variant = frontmatter.get("variant") or metadata.get("style_variant")
    style, variant = resolve_style(style_id, None if requested_variant in {None, "", "default", "待确认"} else str(requested_variant))
    policy = str(frontmatter.get("visualAssetPolicy") or metadata.get("visual_asset_policy") or "native-only")
    slides = [parse_slide(block, index, len(blocks)) for index, block in enumerate(blocks)]
    spec = {
        "schema_version": 1,
        "title": str(frontmatter.get("title") or slides[0]["title"]),
        "style_id": style["id"],
        "style_variant": variant["id"],
        "typography_profile": style.get("typography_profile"),
        "table_profile": style.get("table_profile"),
        "visual_asset_policy": policy,
        "slides": slides,
    }
    return frontmatter, spec


def render_markdown(spec: dict[str, Any], existing_frontmatter: dict[str, Any] | None = None) -> str:
    fm = dict(existing_frontmatter or {})
    fm.update({
        "title": spec.get("title"), "style": spec.get("style_id"),
        "variant": spec.get("style_variant"), "ratio": fm.get("ratio", "16:9"),
        "fontCN": fm.get("fontCN", "微软雅黑"),
        "visualAssetPolicy": spec.get("visual_asset_policy", "native-only"),
    })
    parts = ["---\n" + yaml_dump(fm) + "\n---"]
    for row in spec.get("slides", []):
        lines = [f"# {row.get('title', '')}"]
        message = row.get("subtitle") or row.get("key_message")
        if message:
            lines.extend(["", f"> {message}"])
        lines.extend(["", f'::layout{{type="{ARCHETYPE_TO_LAYOUT.get(str(row.get("archetype")), "content")}"}}'])
        archetype = row.get("archetype")
        collection = {
            "content-structured": ("cards", "title", "body"),
            "process-flow": ("steps", "title", "body"),
            "data-callouts": ("metrics", "value", "label"),
            "architecture": ("layers", "title", "body"),
        }.get(str(archetype))
        if collection:
            key, title_key, body_key = collection
            for item in row.get(key, []):
                lines.extend(["", f"## {item.get(title_key, '')}"])
                if item.get(body_key):
                    lines.extend(["", str(item[body_key])])
        elif archetype == "comparison-two-zone":
            for key in ("left", "right"):
                item = row.get(key, {})
                lines.extend(["", f"## {item.get('title', '')}"])
                lines.extend(["", *[f"- {value}" for value in item.get("points", [])]])
        elif archetype == "table":
            headers = [str(value) for value in row.get("headers", [])]
            lines.extend(["", "| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"])
            lines.extend("| " + " | ".join(str(value) for value in values) + " |" for values in row.get("rows", []))
        elif archetype == "closing-action":
            lines.extend(["", *[f"- {value}" for value in row.get("actions", [])]])
        visual = row.get("visual_slot")
        if isinstance(visual, dict) and visual.get("asset_path"):
            attrs = [f'asset="{visual["asset_path"]}"', f'backend="{visual.get("backend", "provided")}"', f'status="{visual.get("status", "generated")}"']
            if visual.get("prompt_record"):
                attrs.append(f'prompt="{visual["prompt_record"]}"')
            lines.extend(["", "::visual{" + " ".join(attrs) + "}"])
        parts.append("\n".join(lines).rstrip())
    return "\n\n---\n\n".join(parts) + "\n"


def write_plan(session: Path, spec: dict[str, Any]) -> None:
    lines = [
        "---", f"title: {spec['title']}", "delivery_type: editable-pptx",
        f"style_id: {spec['style_id']}", f"style_variant: {spec['style_variant']}",
        f"typography_profile: {spec.get('typography_profile')}", f"table_profile: {spec.get('table_profile')}",
        f"visual_asset_policy: {spec.get('visual_asset_policy')}", "---", "", "# 逐页计划", "",
    ]
    for row in spec["slides"]:
        lines.extend([
            f"## {row['slide_number']}. [{row['archetype']}] {row['title']}", "",
            f"布局：{ARCHETYPE_TO_LAYOUT.get(row['archetype'], 'content')}", "",
            f"页面目标：{row.get('key_message') or row.get('subtitle') or row['title']}", "",
            "事实边界：沿用用户提供内容；禁止补造案例、参数、准确率或收益数据。", "",
        ])
    (session / "slides_plan.md").write_text("\n".join(lines), encoding="utf-8")


def write_prompts(session: Path, spec: dict[str, Any]) -> None:
    metadata = load_json(session / "metadata.json")
    prompts = {
        "schema_version": 1, "session_id": metadata.get("session_id"), "delivery_type": "editable-pptx",
        "style_id": spec["style_id"], "style_variant": spec["style_variant"],
        "typography_profile": spec.get("typography_profile"), "table_profile": spec.get("table_profile"),
        "visual_asset_policy": spec.get("visual_asset_policy"),
        "slides": [{
            "slide_number": row["slide_number"], "page_type": row["archetype"],
            "style_id": row.get("style_id") or spec["style_id"], "style_variant": row.get("style_variant") or spec["style_variant"],
            "layout_id": ARCHETYPE_TO_LAYOUT.get(row["archetype"], "content"),
            "layout_intent": "由 slides.md 结构化组件确定",
            "prompt": "Markdown-first 原生可编辑页面；不生成整页图片。", "reference_images": [],
            "asset_reference_images": [], "status": "planned", "output_image": None,
            "qa": {"status": "pending", "notes": []},
        } for row in spec["slides"]],
    }
    save_json(session / "prompts.json", prompts)


def write_scenes(session: Path, spec: dict[str, Any]) -> None:
    scenes_dir = session / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    expected: set[Path] = set()
    for row in spec["slides"]:
        number = int(row["slide_number"])
        path = scenes_dir / f"slide-{number:03d}.scene.json"
        expected.add(path)
        old = load_json(path) if path.is_file() else {}
        content = {"title": row["title"], "message": row.get("key_message") or row.get("subtitle") or "", "facts": []}
        scene = {
            "schema_version": 2, "slide_id": f"slide-{number:03d}", "slide_number": number,
            "revision": int(old.get("revision", 1)), "page_type": row["archetype"],
            "style_id": row.get("style_id") or spec["style_id"], "style_variant": row.get("style_variant") or spec["style_variant"],
            "layout_id": ARCHETYPE_TO_LAYOUT.get(row["archetype"]),
            "typography_profile": spec.get("typography_profile"), "table_profile": spec.get("table_profile"),
            "visual_asset_policy": spec.get("visual_asset_policy"), "canvas": CANVAS, "content": content,
            "generation": {"prompt": "", "reference_images": [], "asset_reference_images": []},
            "elements": old.get("elements", []),
            "dependencies": {"scene_hash": "", "prompt_hash": canonical_hash(""), "asset_hashes": old.get("dependencies", {}).get("asset_hashes", [])},
        }
        hashable = dict(scene); hashable.pop("revision", None)
        hashable["dependencies"] = {"prompt_hash": scene["dependencies"]["prompt_hash"], "asset_hashes": scene["dependencies"]["asset_hashes"]}
        next_hash = canonical_hash(hashable)
        if old and old.get("dependencies", {}).get("scene_hash") != next_hash:
            scene["revision"] += 1
        scene["dependencies"]["scene_hash"] = next_hash
        save_json(path, scene)
    for path in scenes_dir.glob("slide-*.scene.json"):
        if path not in expected:
            path.unlink()


def run_checked(*args: str) -> dict[str, Any]:
    result = subprocess.run([sys.executable, *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{result.stdout}\n{result.stderr}")
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True)
    parser.add_argument("--source", help="Default: <session>/slides.md")
    parser.add_argument("--build-preview", action="store_true", help="Build cache/editable/preview.pptx and sync its native objects to scenes.")
    parser.add_argument("--render-canvas", action="store_true", help="Export manifest and write reports/editor-canvas.html; implies --build-preview.")
    args = parser.parse_args()
    session = Path(args.session).resolve()
    source = Path(args.source).resolve() if args.source else session / "slides.md"
    if not source.is_file():
        raise SystemExit(f"missing Markdown source: {source}")
    metadata_path = session / "metadata.json"
    metadata = load_json(metadata_path)
    frontmatter, spec = parse_markdown(source.read_text(encoding="utf-8"), metadata)
    spec_path = session / "analysis" / "native_deck_spec.json"
    save_json(spec_path, spec)
    write_plan(session, spec)
    write_prompts(session, spec)
    write_scenes(session, spec)
    metadata.update({
        "authoring_mode": "markdown-canvas", "content_source": "slides.md", "style_id": spec["style_id"],
        "style_variant": spec["style_variant"], "typography_profile": spec.get("typography_profile"),
        "table_profile": spec.get("table_profile"), "visual_asset_policy": spec.get("visual_asset_policy"),
        "markdown_source_hash": hashlib.sha256(source.read_bytes()).hexdigest(), "status": "canvas_editing",
    })
    save_json(metadata_path, metadata)
    result: dict[str, Any] = {"status": "PASS", "source": str(source), "slide_count": len(spec["slides"]), "spec": str(spec_path)}
    if args.build_preview or args.render_canvas:
        preview = session / "cache" / "editable" / "preview.pptx"
        build = run_checked("scripts/build_native_editable_deck.py", "--spec", str(spec_path), "--session", str(session), "--out-pptx", str(preview), "--report", str(session / "reports" / "markdown-preview-build.json"))
        sync = run_checked("scripts/sync_canvas_scene.py", "--session", str(session), "--pptx", str(preview))
        result.update({"preview": str(preview), "preview_build": build["status"], "scene_sync": sync["status"]})
    if args.render_canvas:
        manifest = run_checked("scripts/editor_bridge.py", "export", "--session", str(session))
        canvas = session / "reports" / "editor-canvas.html"
        rendered = run_checked("scripts/render_editor_canvas.py", "--manifest", str(session / "reports" / "editor-manifest.json"), "--out", str(canvas))
        result.update({"manifest_slide_count": manifest["slide_count"], "canvas": str(canvas), "canvas_status": rendered["status"]})
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
