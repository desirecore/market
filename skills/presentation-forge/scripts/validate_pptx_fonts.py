#!/usr/bin/env python3
"""Validate explicit East Asian font declarations in a PPTX package."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

from lxml import etree


A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"a": A_NS, "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
ROLE = re.compile(r"\[pf-role=([a-z0-9_-]+)]", re.I)
HEADING_ROLES = {"hero", "section_title", "section-title", "title", "page_title", "page-title", "subtitle", "header", "minor_title", "minor-title"}


def run_role(run) -> str | None:
    shape = next(iter(run.xpath("ancestor::p:sp[1]", namespaces=NS)), None)
    if shape is None:
        return None
    names = shape.xpath("./p:nvSpPr/p:cNvPr/@name", namespaces=NS)
    match = ROLE.search(names[0] if names else "")
    return match.group(1).lower() if match else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx")
    parser.add_argument("--font", help="Require this exact East Asian typeface.")
    parser.add_argument("--heading-font", help="Expected East Asian font for heading roles and the major theme font.")
    parser.add_argument("--body-font", help="Expected East Asian font for body roles and the minor theme font.")
    parser.add_argument("--latin-font", help="Require this Latin and complex-script typeface on checked CJK runs.")
    parser.add_argument("--out")
    args = parser.parse_args()
    pptx = Path(args.pptx)
    errors: list[dict[str, object]] = []
    checked_runs = 0
    theme_nodes = 0
    with zipfile.ZipFile(pptx) as package:
        for name in package.namelist():
            if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
                root = etree.fromstring(package.read(name))
                for run in root.xpath(".//a:r", namespaces=NS):
                    text = "".join(run.xpath("./a:t/text()", namespaces=NS))
                    if not CJK.search(text):
                        continue
                    checked_runs += 1
                    role = run_role(run)
                    expected_ea = args.font or (args.heading_font if role in HEADING_ROLES else args.body_font)
                    ea_nodes = run.xpath("./a:rPr/a:ea", namespaces=NS)
                    ea_face = ea_nodes[0].get("typeface") if ea_nodes else None
                    if not ea_face or (expected_ea and ea_face != expected_ea):
                        errors.append({"part": name, "text": text, "role": role, "east_asian_typeface": ea_face, "expected": expected_ea})
                    for tag in ("latin", "cs"):
                        nodes = run.xpath(f"./a:rPr/a:{tag}", namespaces=NS)
                        face = nodes[0].get("typeface") if nodes else None
                        if not face or (args.latin_font and face != args.latin_font):
                            errors.append({"part": name, "text": text, "role": role, "font_slot": tag, "typeface": face, "expected": args.latin_font})
            elif name.startswith("ppt/theme/theme") and name.endswith(".xml"):
                root = etree.fromstring(package.read(name))
                for branch, expected in (("majorFont", args.font or args.heading_font), ("minorFont", args.font or args.body_font)):
                    nodes = root.xpath(f".//a:fontScheme/a:{branch}/a:ea", namespaces=NS)
                    theme_nodes += len(nodes)
                    for node in nodes:
                        face = node.get("typeface")
                        if not face or (expected and face != expected):
                            errors.append({"part": name, "theme_node": branch, "east_asian_typeface": face, "expected": expected})
    if checked_runs == 0:
        errors.append({"type": "no_cjk_runs_found"})
    if theme_nodes < 2:
        errors.append({"type": "missing_major_or_minor_theme_east_asian_font", "count": theme_nodes})
    report = {"status": "FAIL" if errors else "PASS", "pptx": str(pptx), "checked_cjk_runs": checked_runs, "theme_east_asian_nodes": theme_nodes, "errors": errors}
    if args.out:
        out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
