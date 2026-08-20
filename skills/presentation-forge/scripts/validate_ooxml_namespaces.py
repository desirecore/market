#!/usr/bin/env python3
"""Validate namespace prefixes referenced by OOXML compatibility attributes."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from lxml import etree


MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
PREFIX_LIST_ATTRIBUTES = {"Requires", "Ignorable"}
QNAME_LIST_ATTRIBUTES = {"PreserveAttributes", "PreserveElements", "ProcessContent"}


def attribute_local_name(name: str) -> str:
    return etree.QName(name).localname if name.startswith("{") else name


def referenced_prefixes(element: etree._Element) -> set[str]:
    prefixes: set[str] = set()
    for name, value in element.attrib.items():
        local = attribute_local_name(name)
        if local in PREFIX_LIST_ATTRIBUTES:
            prefixes.update(token for token in value.split() if token)
        elif local in QNAME_LIST_ATTRIBUTES:
            prefixes.update(token.split(":", 1)[0] for token in value.split() if ":" in token)
    return prefixes


def validate_package(pptx: Path) -> dict[str, object]:
    errors: list[dict[str, object]] = []
    checked_parts = 0
    checked_references = 0
    if not zipfile.is_zipfile(pptx):
        return {"status": "FAIL", "pptx": str(pptx), "checked_parts": 0, "checked_references": 0, "errors": [{"code": "not_zip_package"}]}
    with zipfile.ZipFile(pptx) as package:
        for name in package.namelist():
            if not name.endswith((".xml", ".rels", ".vml")):
                continue
            checked_parts += 1
            try:
                root = etree.fromstring(package.read(name))
            except etree.XMLSyntaxError as exc:
                errors.append({"code": "xml_parse_error", "part": name, "message": str(exc)})
                continue
            tree = root.getroottree()
            for element in root.iter():
                prefixes = referenced_prefixes(element)
                checked_references += len(prefixes)
                for prefix in sorted(prefixes):
                    if prefix not in element.nsmap:
                        errors.append({
                            "code": "compatibility_prefix_undeclared",
                            "part": name,
                            "path": tree.getpath(element),
                            "prefix": prefix,
                        })
    return {
        "status": "FAIL" if errors else "PASS",
        "pptx": str(pptx),
        "checked_parts": checked_parts,
        "checked_references": checked_references,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx")
    parser.add_argument("--out")
    args = parser.parse_args()
    report = validate_package(Path(args.pptx).resolve())
    if args.out:
        out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if report["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
