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
NS = {"a": A_NS}
CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx")
    parser.add_argument("--font", help="Require this exact East Asian typeface.")
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
                    nodes = run.xpath("./a:rPr/a:ea", namespaces=NS)
                    face = nodes[0].get("typeface") if nodes else None
                    if not face or (args.font and face != args.font):
                        errors.append({"part": name, "text": text, "east_asian_typeface": face})
            elif name.startswith("ppt/theme/theme") and name.endswith(".xml"):
                root = etree.fromstring(package.read(name))
                nodes = root.xpath(".//a:fontScheme/a:majorFont/a:ea | .//a:fontScheme/a:minorFont/a:ea", namespaces=NS)
                theme_nodes += len(nodes)
                for node in nodes:
                    face = node.get("typeface")
                    if not face or (args.font and face != args.font):
                        errors.append({"part": name, "theme_node": etree.QName(node).localname, "east_asian_typeface": face})
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
