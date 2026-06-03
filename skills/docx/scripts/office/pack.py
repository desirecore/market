"""Pack a directory into a DOCX, PPTX, or XLSX file.

Validates with auto-repair, condenses XML formatting, and creates the Office file.

Usage:
    python pack.py <input_directory> <output_file> [--original <file>] [--validate true|false]

Examples:
    python pack.py unpacked/ output.docx --original input.docx
    python pack.py unpacked/ output.pptx --validate false
"""

import argparse
import os
import sys
import shutil
import tempfile
import zipfile
from pathlib import Path

# 复用客户端预装的共享 Python 依赖（defusedxml 等）：office → scripts → docx → skills → <ROOT>
_deps = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "runtime-deps", "python-libs")
if os.path.isdir(_deps):
    sys.path.insert(0, _deps)

import defusedxml.minidom

try:
    from validators import DOCXSchemaValidator, PPTXSchemaValidator, RedliningValidator
    _VALIDATORS_AVAILABLE = True
except ImportError as _e:
    # validators 依赖 lxml（编译型扩展，未随客户端预装）。缺失时优雅降级：
    # 跳过 XSD 完整校验而非崩溃——打包/编辑本身不需要 lxml。
    _VALIDATORS_AVAILABLE = False
    _VALIDATORS_IMPORT_ERROR = _e

def pack(
    input_directory: str,
    output_file: str,
    original_file: str | None = None,
    validate: bool = True,
    infer_author_func=None,
) -> tuple[None, str]:
    input_dir = Path(input_directory)
    output_path = Path(output_file)
    suffix = output_path.suffix.lower()

    if not input_dir.is_dir():
        return None, f"Error: {input_dir} is not a directory"

    if suffix not in {".docx", ".pptx", ".xlsx"}:
        return None, f"Error: {output_file} must be a .docx, .pptx, or .xlsx file"

    if validate and original_file:
        if not _VALIDATORS_AVAILABLE:
            print(
                "Warning: lxml 未安装，已跳过 XSD 完整校验（文件仍正常打包）。"
                "如需完整校验请安装 lxml：pip install lxml",
                file=sys.stderr,
            )
        else:
            original_path = Path(original_file)
            if original_path.exists():
                success, output = _run_validation(
                    input_dir, original_path, suffix, infer_author_func
                )
                if output:
                    print(output)
                if not success:
                    return None, f"Error: Validation failed for {input_dir}"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_content_dir = Path(temp_dir) / "content"
        shutil.copytree(input_dir, temp_content_dir)

        for pattern in ["*.xml", "*.rels"]:
            for xml_file in temp_content_dir.rglob(pattern):
                _condense_xml(xml_file)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in temp_content_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(temp_content_dir))

    return None, f"Successfully packed {input_dir} to {output_file}"


def _run_validation(
    unpacked_dir: Path,
    original_file: Path,
    suffix: str,
    infer_author_func=None,
) -> tuple[bool, str | None]:
    output_lines = []
    validators = []

    if suffix == ".docx":
        author = "Claude"
        if infer_author_func:
            try:
                author = infer_author_func(unpacked_dir, original_file)
            except ValueError as e:
                print(f"Warning: {e} Using default author 'Claude'.", file=sys.stderr)

        validators = [
            DOCXSchemaValidator(unpacked_dir, original_file),
            RedliningValidator(unpacked_dir, original_file, author=author),
        ]
    elif suffix == ".pptx":
        validators = [PPTXSchemaValidator(unpacked_dir, original_file)]

    if not validators:
        return True, None

    total_repairs = sum(v.repair() for v in validators)
    if total_repairs:
        output_lines.append(f"Auto-repaired {total_repairs} issue(s)")

    success = all(v.validate() for v in validators)

    if success:
        output_lines.append("All validations PASSED!")

    return success, "\n".join(output_lines) if output_lines else None


def _condense_xml(xml_file: Path) -> None:
    try:
        with open(xml_file, encoding="utf-8") as f:
            dom = defusedxml.minidom.parse(f)

        for element in dom.getElementsByTagName("*"):
            if element.tagName.endswith(":t"):
                continue

            for child in list(element.childNodes):
                if (
                    child.nodeType == child.TEXT_NODE
                    and child.nodeValue
                    and child.nodeValue.strip() == ""
                ) or child.nodeType == child.COMMENT_NODE:
                    element.removeChild(child)

        xml_file.write_bytes(dom.toxml(encoding="UTF-8"))
    except Exception as e:
        print(f"ERROR: Failed to parse {xml_file.name}: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pack a directory into a DOCX, PPTX, or XLSX file"
    )
    parser.add_argument("input_directory", help="Unpacked Office document directory")
    parser.add_argument("output_file", help="Output Office file (.docx/.pptx/.xlsx)")
    parser.add_argument(
        "--original",
        help="Original file for validation comparison",
    )
    parser.add_argument(
        "--validate",
        type=lambda x: x.lower() == "true",
        default=True,
        metavar="true|false",
        help="Run validation with auto-repair (default: true)",
    )
    args = parser.parse_args()

    _, message = pack(
        args.input_directory,
        args.output_file,
        original_file=args.original,
        validate=args.validate,
    )
    print(message)

    if "Error" in message:
        sys.exit(1)
