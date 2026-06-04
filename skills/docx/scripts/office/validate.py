"""
Command line tool to validate Office document XML files against XSD schemas and tracked changes.

Usage:
    python validate.py <path> [--original <original_file>] [--auto-repair] [--author NAME]

The first argument can be either:
- An unpacked directory containing the Office document XML files
- A packed Office file (.docx/.pptx/.xlsx) which will be unpacked to a temp directory

Auto-repair fixes:
- paraId/durableId values that exceed OOXML limits
- Missing xml:space="preserve" on w:t elements with whitespace
"""

import argparse
import atexit
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

# 复用客户端预装的共享 Python 依赖（defusedxml 等）：office → scripts → docx → skills → <ROOT>
_deps = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "runtime-deps", "python-libs")
if os.path.isdir(_deps):
    sys.path.insert(0, _deps)

try:
    from validators import DOCXSchemaValidator, PPTXSchemaValidator, RedliningValidator
    _VALIDATORS_AVAILABLE = True
except ImportError:
    # validators 依赖 lxml（编译型扩展，未随客户端预装）。缺失时优雅降级：
    # 提示安装并以成功退出，而非崩溃——避免阻塞依赖本脚本的上层流程。
    _VALIDATORS_AVAILABLE = False


def main():
    if not _VALIDATORS_AVAILABLE:
        print(
            "Warning: lxml 未安装，已跳过 XSD 完整校验。如需完整校验请安装 lxml：pip install lxml",
            file=sys.stderr,
        )
        return 0

    parser = argparse.ArgumentParser(description="Validate Office document XML files")
    parser.add_argument(
        "path",
        help="Path to unpacked directory or packed Office file (.docx/.pptx/.xlsx)",
    )
    parser.add_argument(
        "--original",
        required=False,
        default=None,
        help="Path to original file (.docx/.pptx/.xlsx). If omitted, all XSD errors are reported and redlining validation is skipped.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--auto-repair",
        action="store_true",
        help="Automatically repair common issues (hex IDs, whitespace preservation)",
    )
    parser.add_argument(
        "--author",
        default="Claude",
        help="Author name for redlining validation (default: Claude)",
    )
    args = parser.parse_args()

    path = Path(args.path)
    assert path.exists(), f"Error: {path} does not exist"

    original_file = None
    if args.original:
        original_file = Path(args.original)
        assert original_file.is_file(), f"Error: {original_file} is not a file"
        assert original_file.suffix.lower() in [".docx", ".pptx", ".xlsx"], (
            f"Error: {original_file} must be a .docx, .pptx, or .xlsx file"
        )

    file_extension = (original_file or path).suffix.lower()
    assert file_extension in [".docx", ".pptx", ".xlsx"], (
        f"Error: Cannot determine file type from {path}. Use --original or provide a .docx/.pptx/.xlsx file."
    )

    if path.is_file() and path.suffix.lower() in [".docx", ".pptx", ".xlsx"]:
        temp_dir = tempfile.mkdtemp()
        # 解包目录在进程退出时清理（含 sys.exit），避免每次校验泄漏 /tmp 目录
        atexit.register(shutil.rmtree, temp_dir, ignore_errors=True)
        with zipfile.ZipFile(path, "r") as zf:
            zf.extractall(temp_dir)
        unpacked_dir = Path(temp_dir)
    else:
        assert path.is_dir(), f"Error: {path} is not a directory or Office file"
        unpacked_dir = path

    match file_extension:
        case ".docx":
            validators = [
                DOCXSchemaValidator(unpacked_dir, original_file, verbose=args.verbose),
            ]
            if original_file:
                validators.append(
                    RedliningValidator(unpacked_dir, original_file, verbose=args.verbose, author=args.author)  
                )
        case ".pptx":
            validators = [
                PPTXSchemaValidator(unpacked_dir, original_file, verbose=args.verbose),
            ]
        case _:
            print(f"Error: Validation not supported for file type {file_extension}")
            sys.exit(1)

    if args.auto_repair:
        total_repairs = sum(v.repair() for v in validators)
        if total_repairs:
            print(f"Auto-repaired {total_repairs} issue(s)")

    success = all(v.validate() for v in validators)

    if success:
        print("All validations PASSED!")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
