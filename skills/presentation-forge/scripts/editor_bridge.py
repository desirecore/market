#!/usr/bin/env python3
"""Export an editor manifest or apply optimistic-concurrency patches to a deck session."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from revision_session import snapshot
from style_presets import flattened_presets, resolve_style


PROTECTED_KEYS = {
    "schema_version", "slide_number", "backend", "source_type", "status",
    "asset_path", "prompt_record", "visual_asset_policy", "style_id", "style_variant",
    "typography_profile", "table_profile", "archetype",
}
ELEMENT_CHANGE_KEYS = {"bbox", "text", "style", "rotation", "z_index"}
STYLE_KEYS = {"fill", "line", "line_width_pt", "font_size_pt", "font_family", "font_color", "bold", "align", "vertical_align", "line_spacing"}


def validate_style_changes(style: dict) -> None:
    if set(style) - STYLE_KEYS:
        raise ValueError("unsupported style field")
    for key in ("fill", "line", "font_color"):
        if key in style and (not isinstance(style[key], str) or not re.fullmatch(r"[A-Fa-f0-9]{6}", style[key])):
            raise ValueError(f"{key} must be a six-digit hex color")
    if "font_size_pt" in style and (not isinstance(style["font_size_pt"], (int, float)) or not 1 <= float(style["font_size_pt"]) <= 200):
        raise ValueError("font_size_pt must be between 1 and 200")
    if "line_width_pt" in style and (not isinstance(style["line_width_pt"], (int, float)) or not 0 <= float(style["line_width_pt"]) <= 50):
        raise ValueError("line_width_pt must be between 0 and 50")
    if "line_spacing" in style and (not isinstance(style["line_spacing"], (int, float)) or not 0.5 <= float(style["line_spacing"]) <= 5):
        raise ValueError("line_spacing must be between 0.5 and 5")
    if "font_family" in style and (not isinstance(style["font_family"], str) or not style["font_family"].strip()):
        raise ValueError("font_family must be a non-empty string")
    if "bold" in style and not isinstance(style["bold"], bool):
        raise ValueError("bold must be boolean")
    if "align" in style and style["align"] not in {"left", "center", "right", "justify"}:
        raise ValueError("invalid text alignment")
    if "vertical_align" in style and style["vertical_align"] not in {"top", "middle", "bottom"}:
        raise ValueError("invalid vertical alignment")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def pointer_unescape(value: str) -> str:
    return value.replace("~1", "/").replace("~0", "~")


def editable_paths(value: object, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in PROTECTED_KEYS:
                continue
            child_prefix = f"{prefix}/{pointer_escape(str(key))}"
            paths.extend(editable_paths(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(editable_paths(child, f"{prefix}/{index}"))
    elif prefix:
        paths.append(prefix)
    return paths


def source_document(session: Path) -> tuple[str, Path, dict]:
    native = session / "analysis" / "native_deck_spec.json"
    if native.is_file():
        return "native-editable-deck", native, load(native)
    raise ValueError("editor bridge v1 requires analysis/native_deck_spec.json")


def thumbnail_for(session: Path, slide_number: int) -> str | None:
    names = (f"slide-{slide_number:03d}.png", f"slide-{slide_number}.png")
    for folder in ("render", "generated", "final"):
        for name in names:
            path = session / folder / name
            if path.is_file():
                return str(path.relative_to(session))
    return None


def current_style(document: dict) -> dict:
    style, variant = resolve_style(str(document.get("style_id") or "consulting-blue-white"), document.get("style_variant"))
    return {
        "style_id": style["id"], "variant_id": variant["id"],
        "family_name": style["name"], "name": variant["name"],
    }


def build_manifest(session: Path) -> dict:
    metadata = load(session / "metadata.json")
    document_kind, document_path, document = source_document(session)
    allowed = set(editable_paths(document))
    slides = []
    canvas_state = []
    for index, slide in enumerate(document.get("slides", [])):
        number = int(slide["slide_number"])
        prefix = f"/slides/{index}/"
        scene_path = session / "scenes" / f"slide-{number:03d}.scene.json"
        scene = load(scene_path) if scene_path.is_file() else {"canvas": {"width": 1920, "height": 1080, "unit": "px"}, "elements": []}
        canvas_state.append({"slide_number": number, "revision": scene.get("revision"), "elements": scene.get("elements", [])})
        slides.append({
            "slide_number": number,
            "title": slide.get("title", ""),
            "archetype": slide.get("archetype"),
            "style": {
                "style_id": slide.get("style_id") or document.get("style_id"),
                "variant_id": slide.get("style_variant") or document.get("style_variant") or resolve_style(str(document.get("style_id") or "consulting-blue-white"), None)[1]["id"],
            },
            "scene": f"scenes/slide-{number:03d}.scene.json",
            "thumbnail": thumbnail_for(session, number),
            "editable_paths": sorted(path for path in allowed if path.startswith(prefix)),
            "canvas": scene.get("canvas"),
            "elements": scene.get("elements", []),
        })
    validate_slide_contract(session, document, slides)
    return {
        "schema_version": 3,
        "protocol": "presentation-forge-editor.v3",
        "session_id": metadata.get("session_id"),
        "base_revision": metadata.get("current_revision"),
        "route": metadata.get("route"),
        "workflow": {
            "mode": metadata.get("editor_workflow_mode", "direct-build"),
            "style_selection_status": metadata.get("style_selection_status", "auto-selected"),
            "export_approval": metadata.get("editor_export_approval", "auto-proceed"),
            "final_pptx_ready": metadata.get("editor_export_approval") in {"approved", "auto-proceed"},
        },
        "document_kind": document_kind,
        "editable_document": str(document_path.relative_to(session)),
        "document_sha256": canonical_hash(document),
        "canvas_sha256": canonical_hash(canvas_state),
        "global_editable_paths": sorted(path for path in allowed if not path.startswith("/slides/")),
        "current_style": current_style(document),
        "style_catalog": flattened_presets(),
        "slides": slides,
        "slide_count": len(slides),
        "capabilities": {
            "replace_scalar": True,
            "element_canvas": True,
            "move_resize": True,
            "text_edit": True,
            "style_edit": True,
            "rotation": True,
            "z_order": True,
            "page_level_invalidation": True,
            "optimistic_concurrency": True,
            "revision_rollback": True,
            "deck_style_switch": True,
            "slide_variant_switch": True,
            "style_switch_modes": ["replace-theme", "preserve-layout"],
            "explicit_export_approval": metadata.get("editor_workflow_mode") == "canvas-first",
            "asset_replace": False,
            "direct_ooxml_edit": False,
        },
        "events": "reports/editor-events.jsonl",
    }


def validate_slide_contract(session: Path, document: dict, slides: list[dict]) -> None:
    document_numbers = [int(row["slide_number"]) for row in document.get("slides", [])]
    manifest_numbers = [int(row["slide_number"]) for row in slides]
    scene_numbers = sorted(int(path.stem.split("-")[1].split(".")[0]) for path in (session / "scenes").glob("slide-*.scene.json"))
    expected = list(range(1, len(document_numbers) + 1))
    if document_numbers != expected:
        raise ValueError(f"canvas slide contract failed: non-contiguous document slides {document_numbers}")
    if manifest_numbers != document_numbers:
        raise ValueError(f"canvas slide contract failed: manifest {manifest_numbers} != document {document_numbers}")
    if scene_numbers != document_numbers:
        raise ValueError(f"canvas slide contract failed: scenes {scene_numbers} != document {document_numbers}")


def export_manifest(session: Path, out: Path | None = None) -> dict:
    manifest = build_manifest(session)
    target = out or session / "reports" / "editor-manifest.json"
    save(target, manifest)
    metadata_path = session / "metadata.json"
    metadata = load(metadata_path)
    previous_editor = metadata.get("editor") if isinstance(metadata.get("editor"), dict) else {}
    metadata["editor"] = {
        "protocol": manifest["protocol"],
        "manifest": str(target.relative_to(session)) if target.is_relative_to(session) else str(target),
        "status": "editing" if metadata.get("editor_workflow_mode") == "canvas-first" and metadata.get("editor_export_approval") != "approved" else previous_editor.get("status", "ready"),
    }
    save(metadata_path, metadata)
    return manifest


def resolve_pointer(document: object, pointer: str) -> tuple[object, str | int]:
    if not pointer.startswith("/"):
        raise ValueError(f"invalid JSON pointer: {pointer}")
    parts = [pointer_unescape(part) for part in pointer[1:].split("/")]
    current = document
    for part in parts[:-1]:
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            current = current[part]
        else:
            raise ValueError(f"pointer traverses scalar: {pointer}")
    key: str | int = int(parts[-1]) if isinstance(current, list) else parts[-1]
    return current, key


def replace_value(document: dict, pointer: str, value: object) -> None:
    parent, key = resolve_pointer(document, pointer)
    old = parent[key]  # type: ignore[index]
    if isinstance(old, bool) != isinstance(value, bool):
        raise ValueError(f"type mismatch at {pointer}")
    if old is not None and value is not None and not isinstance(value, type(old)):
        if not (isinstance(old, (int, float)) and isinstance(value, (int, float)) and not isinstance(value, bool)):
            raise ValueError(f"type mismatch at {pointer}")
    parent[key] = value  # type: ignore[index]


def refresh_scene_hash(scene: dict) -> None:
    hashable = dict(scene)
    hashable.pop("revision", None)
    dependencies = dict(scene.get("dependencies", {}))
    dependencies.pop("scene_hash", None)
    hashable["dependencies"] = dependencies
    scene.setdefault("dependencies", {})["scene_hash"] = canonical_hash(hashable)


def clear_scene_style_overrides(scene: dict, mode: str) -> None:
    if mode == "replace-theme":
        scene["elements"] = []
        return
    for element in scene.get("elements", []):
        element["style"] = {}


def update_frontmatter(text: str, values: dict[str, str]) -> str:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return text
    frontmatter, body = text[4:].split("\n---\n", 1)
    lines = frontmatter.splitlines()
    found: set[str] = set()
    for index, line in enumerate(lines):
        key = line.split(":", 1)[0].strip() if ":" in line else ""
        if key in values:
            lines[index] = f"{key}: {values[key]}"
            found.add(key)
    for key, value in values.items():
        if key not in found:
            lines.append(f"{key}: {value}")
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def sync_scenes(session: Path, document: dict, changed_slides: set[int]) -> None:
    by_number = {int(slide["slide_number"]): slide for slide in document.get("slides", [])}
    for number in sorted(changed_slides):
        scene_path = session / "scenes" / f"slide-{number:03d}.scene.json"
        if not scene_path.is_file() or number not in by_number:
            continue
        slide = by_number[number]
        scene = load(scene_path)
        scene["revision"] = int(scene.get("revision", 1)) + 1
        scene["page_type"] = slide.get("archetype", scene.get("page_type", "other"))
        scene.setdefault("content", {})["title"] = slide.get("title", "")
        scene["content"]["message"] = slide.get("key_message") or slide.get("subtitle") or ""
        for element in scene.get("elements", []):
            binding = element.get("source_binding")
            if not isinstance(binding, dict) or binding.get("document") != "analysis/native_deck_spec.json" or "text" not in element:
                continue
            try:
                parent, key = resolve_pointer(document, str(binding["path"]))
                value = parent[key]  # type: ignore[index]
            except (KeyError, IndexError, TypeError, ValueError):
                continue
            if isinstance(value, (str, int, float)):
                element["text"] = str(value)
        refresh_scene_hash(scene)
        save(scene_path, scene)


def invalidate_slides(metadata: dict, changed_slides: set[int]) -> None:
    variant = metadata.setdefault("variants", {}).setdefault("editable", {"status": "not_built", "artifact": None, "slides": {}})
    slides = variant.setdefault("slides", {})
    for number in changed_slides:
        previous = slides.get(str(number), {})
        slides[str(number)] = {**previous, "status": "stale", "reason": "editor_patch"}
    if changed_slides:
        variant["status"] = "partial_stale"


def append_event(session: Path, event: dict) -> None:
    path = session / "reports" / "editor-events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def apply_patch(session: Path, patch_path: Path) -> dict:
    patch = load(patch_path)
    if patch.get("schema_version") not in {1, 2, 3}:
        raise ValueError("unsupported editor patch schema_version")
    metadata_path = session / "metadata.json"
    metadata = load(metadata_path)
    current_revision = metadata.get("current_revision")
    if patch.get("base_revision") != current_revision:
        raise ValueError(f"revision conflict: expected {current_revision!r}, got {patch.get('base_revision')!r}")
    _, document_path, document = source_document(session)
    current_hash = canonical_hash(document)
    if patch.get("document_sha256") != current_hash:
        raise ValueError("document hash conflict")
    current_manifest = build_manifest(session)
    if patch.get("schema_version") in {2, 3} and patch.get("canvas_sha256") != current_manifest.get("canvas_sha256"):
        raise ValueError("canvas hash conflict")
    allowed = set(editable_paths(document))
    prompts_path = session / "prompts.json"
    prompts = load(prompts_path) if prompts_path.is_file() else {}
    plan_path = session / "slides_plan.md"
    plan_text = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else ""
    deck_style_change: dict | None = None
    changed_slides: set[int] = set()
    changed_scene_docs: dict[int, tuple[Path, dict]] = {}
    for operation in patch.get("operations", []):
        if operation.get("op") == "apply-style":
            scope = operation.get("scope")
            mode = operation.get("mode")
            if scope not in {"deck", "slide"} or mode not in {"replace-theme", "preserve-layout"}:
                raise ValueError("invalid style scope or mode")
            target_style, target_variant = resolve_style(str(operation.get("style_id") or document.get("style_id")), operation.get("variant_id"))
            if scope == "slide" and target_style["id"] != document.get("style_id"):
                raise ValueError("slide style switch must remain inside the current deck style family")
            target_numbers = [int(row["slide_number"]) for row in document.get("slides", [])] if scope == "deck" else [int(operation.get("slide_number", 0))]
            if not target_numbers or any(number < 1 for number in target_numbers):
                raise ValueError("style operation targets no valid slides")
            by_number = {int(row["slide_number"]): row for row in document.get("slides", [])}
            if any(number not in by_number for number in target_numbers):
                raise ValueError("style operation targets an unknown slide")
            if scope == "deck":
                document["style_id"] = target_style["id"]
                document["style_variant"] = target_variant["id"]
                document["typography_profile"] = target_style["typography_profile"]
                document["table_profile"] = target_style["table_profile"]
                for row in document.get("slides", []):
                    row.pop("style_id", None); row.pop("style_variant", None)
                prompts["style_id"] = target_style["id"]
                prompts["style_variant"] = target_variant["id"]
                prompts["typography_profile"] = target_style["typography_profile"]
                prompts["table_profile"] = target_style["table_profile"]
                plan_text = update_frontmatter(plan_text, {
                    "style_id": target_style["id"], "style_variant": target_variant["id"],
                    "typography_profile": target_style["typography_profile"], "table_profile": target_style["table_profile"],
                })
                deck_style_change = {"style_id": target_style["id"], "style_variant": target_variant["id"], "typography_profile": target_style["typography_profile"], "table_profile": target_style["table_profile"]}
            else:
                row = by_number[target_numbers[0]]
                row["style_id"] = target_style["id"]
                row["style_variant"] = target_variant["id"]
            for prompt_row in prompts.get("slides", []):
                if int(prompt_row.get("slide_number", 0)) in target_numbers:
                    prompt_row["style_id"] = target_style["id"]
                    prompt_row["style_variant"] = target_variant["id"]
            for number in target_numbers:
                scene_path = session / "scenes" / f"slide-{number:03d}.scene.json"
                if not scene_path.is_file():
                    raise ValueError(f"scene not found for slide {number}")
                scene = changed_scene_docs.get(number, (scene_path, load(scene_path)))[1]
                scene["style_id"] = target_style["id"]
                scene["style_variant"] = target_variant["id"]
                scene["typography_profile"] = target_style["typography_profile"]
                scene["table_profile"] = target_style["table_profile"]
                clear_scene_style_overrides(scene, str(mode))
                changed_scene_docs[number] = (scene_path, scene)
                changed_slides.add(number)
            continue
        if operation.get("op") == "update-element":
            number = int(operation.get("slide_number", 0))
            scene_path = session / "scenes" / f"slide-{number:03d}.scene.json"
            if not scene_path.is_file():
                raise ValueError(f"scene not found for slide {number}")
            scene = changed_scene_docs.get(number, (scene_path, load(scene_path)))[1]
            element = next((row for row in scene.get("elements", []) if row.get("id") == operation.get("element_id")), None)
            if element is None:
                raise ValueError(f"element not found: {operation.get('element_id')}")
            if element.get("locked") or not element.get("editable"):
                raise ValueError(f"element is locked: {operation.get('element_id')}")
            changes = operation.get("changes")
            if not isinstance(changes, dict) or not changes or set(changes) - ELEMENT_CHANGE_KEYS:
                raise ValueError("invalid element changes")
            capabilities = set(element.get("capabilities", []))
            if "bbox" in changes:
                if "geometry" not in capabilities:
                    raise ValueError("element geometry is not editable")
                bbox = changes["bbox"]
                canvas = scene.get("canvas", {})
                if not isinstance(bbox, list) or len(bbox) != 4 or not all(isinstance(value, (int, float)) for value in bbox):
                    raise ValueError("bbox must contain four numbers")
                if bbox[2] <= 0 or bbox[3] <= 0 or bbox[0] < 0 or bbox[1] < 0 or bbox[0] + bbox[2] > canvas.get("width", 0) or bbox[1] + bbox[3] > canvas.get("height", 0):
                    raise ValueError("bbox must remain inside canvas")
                element["bbox"] = bbox
            if "text" in changes:
                if "text" not in capabilities or not isinstance(changes["text"], str):
                    raise ValueError("element text is not editable")
                element["text"] = changes["text"]
                binding = element.get("source_binding")
                if isinstance(binding, dict) and binding.get("document") == "analysis/native_deck_spec.json":
                    replace_value(document, str(binding["path"]), changes["text"])
            if "style" in changes:
                if "style" not in capabilities or not isinstance(changes["style"], dict) or set(changes["style"]) - STYLE_KEYS:
                    raise ValueError("element style is not editable")
                validate_style_changes(changes["style"])
                element.setdefault("style", {}).update(changes["style"])
            if "rotation" in changes:
                if "rotation" not in capabilities or not isinstance(changes["rotation"], (int, float)) or not -360 <= float(changes["rotation"]) <= 360:
                    raise ValueError("element rotation is not editable")
                element["rotation"] = float(changes["rotation"])
            if "z_index" in changes:
                if "z-order" not in capabilities or not isinstance(changes["z_index"], int) or not 0 <= changes["z_index"] <= 10000:
                    raise ValueError("element z-order is not editable")
                element["z_index"] = changes["z_index"]
            changed_scene_docs[number] = (scene_path, scene)
            changed_slides.add(number)
            continue
        if operation.get("op") != "replace":
            raise ValueError("unsupported editor operation")
        pointer = operation.get("path")
        if pointer not in allowed:
            raise ValueError(f"path is not editable: {pointer}")
        parts = pointer.split("/")
        if len(parts) > 3 and parts[1] == "slides":
            index = int(parts[2])
            changed_slides.add(int(document["slides"][index]["slide_number"]))
        elif pointer == "/title":
            changed_slides.update(int(slide["slide_number"]) for slide in document.get("slides", []))
        if pointer.endswith("/title") and (not isinstance(operation.get("value"), str) or not operation.get("value").strip()):
            raise ValueError(f"title cannot be empty: {pointer}")
        replace_value(document, pointer, operation.get("value"))
    if not patch.get("operations"):
        raise ValueError("patch has no operations")
    revision = snapshot(session, f"editor patch {patch.get('request_id', '')}".strip())
    save(document_path, document)
    if prompts_path.is_file():
        save(prompts_path, prompts)
    if plan_path.is_file():
        plan_path.write_text(plan_text, encoding="utf-8")
    for _, (scene_path, scene) in changed_scene_docs.items():
        scene["revision"] = int(scene.get("revision", 1)) + 1
        refresh_scene_hash(scene)
        save(scene_path, scene)
    sync_scenes(session, document, changed_slides)
    metadata = load(metadata_path)
    if deck_style_change:
        metadata.update(deck_style_change)
        metadata["style_selection_status"] = "confirmed"
    invalidate_slides(metadata, changed_slides)
    metadata.setdefault("editor", {})["status"] = "rebuild_required" if changed_slides else "ready"
    save(metadata_path, metadata)
    event = {
        "event": "editor.patch.applied",
        "request_id": patch.get("request_id"),
        "revision": revision,
        "changed_slides": sorted(changed_slides),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    append_event(session, event)
    manifest = export_manifest(session)
    return {"status": "applied", **event, "manifest": manifest}


def approve_export(session: Path) -> dict:
    metadata_path = session / "metadata.json"
    metadata = load(metadata_path)
    if metadata.get("editor_workflow_mode") != "canvas-first":
        raise ValueError("export approval is only used by canvas-first sessions")
    if metadata.get("style_selection_status") != "confirmed":
        raise ValueError("select and confirm a style before exporting PPTX")
    revision = snapshot(session, "canvas export approved")
    metadata = load(metadata_path)
    metadata["editor_export_approval"] = "approved"
    metadata.setdefault("editor", {})["status"] = "export_approved"
    save(metadata_path, metadata)
    event = {
        "event": "editor.export.approved",
        "revision": revision,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    append_event(session, event)
    return {"status": "approved", **event}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export_cmd = sub.add_parser("export")
    export_cmd.add_argument("--session", required=True)
    export_cmd.add_argument("--out")
    apply_cmd = sub.add_parser("apply")
    apply_cmd.add_argument("--session", required=True)
    apply_cmd.add_argument("--patch", required=True)
    approve_cmd = sub.add_parser("approve-export")
    approve_cmd.add_argument("--session", required=True)
    args = parser.parse_args()
    session = Path(args.session).resolve()
    try:
        if args.command == "export":
            result = export_manifest(session, Path(args.out).resolve() if args.out else None)
        elif args.command == "approve-export":
            result = approve_export(session)
        else:
            result = apply_patch(session, Path(args.patch).resolve())
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(2)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
