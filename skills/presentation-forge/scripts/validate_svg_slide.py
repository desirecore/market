#!/usr/bin/env python3
"""Validate an SVG slide for portable, safe structural reuse."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
LENGTH_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", help="SVG file to validate.")
    parser.add_argument("--out", help="Optional JSON report path.")
    parser.add_argument("--min-font-size", type=float, default=16.0, help="Warn below this SVG font size.")
    parser.add_argument("--aspect-ratio", type=float, default=16 / 9, help="Expected slide aspect ratio.")
    parser.add_argument("--aspect-tolerance", type=float, default=0.03, help="Allowed ratio difference.")
    return parser.parse_args()


def number(value: str | None) -> float | None:
    if not value:
        return None
    match = LENGTH_RE.match(value)
    return float(match.group(1)) if match else None


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def main() -> None:
    args = parse_args()
    path = Path(args.svg)
    errors: list[str] = []
    warnings: list[str] = []
    facts: dict[str, object] = {"file": str(path)}

    if not path.is_file():
        raise SystemExit(f"SVG not found: {path}")
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise SystemExit(f"Invalid SVG XML: {exc}") from exc

    if local_name(root.tag) != "svg":
        errors.append("root element is not <svg>")

    width = number(root.get("width"))
    height = number(root.get("height"))
    viewbox = root.get("viewBox", "").replace(",", " ").split()
    if len(viewbox) == 4:
        try:
            width, height = float(viewbox[2]), float(viewbox[3])
        except ValueError:
            errors.append("viewBox contains non-numeric values")
    elif width is None or height is None:
        errors.append("SVG needs a numeric viewBox or width/height")

    if width and height:
        ratio = width / height
        facts.update({"width": width, "height": height, "aspect_ratio": ratio})
        if abs(ratio - args.aspect_ratio) > args.aspect_tolerance:
            warnings.append(f"aspect ratio {ratio:.4f} differs from expected {args.aspect_ratio:.4f}")

    counts: dict[str, int] = {}
    for element in root.iter():
        name = local_name(element.tag)
        counts[name] = counts.get(name, 0) + 1
        if name in {"script", "foreignObject"}:
            errors.append(f"forbidden <{name}> element")
        href = element.get("href") or element.get(XLINK_HREF)
        if href and not href.startswith(("#", "data:")):
            errors.append(f"external resource reference: {href}")
        if name == "text":
            font_size = number(element.get("font-size"))
            style = element.get("style", "")
            if font_size is None:
                match = re.search(r"font-size\s*:\s*([0-9]+(?:\.[0-9]+)?)", style)
                font_size = float(match.group(1)) if match else None
            if font_size is not None and font_size < args.min_font_size:
                warnings.append(f"text font-size {font_size:g} is below {args.min_font_size:g}")

    facts["elements"] = counts
    report = {
        "status": "FAIL" if errors else "PASS",
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "facts": facts,
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
