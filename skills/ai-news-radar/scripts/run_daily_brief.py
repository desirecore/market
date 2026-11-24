#!/usr/bin/env python3
"""Run the pinned generator with a required output directory outside this skill."""
from __future__ import annotations
import argparse
import runpy
import sys
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, help="Absolute private working/output directory, outside the installed skill")
    args, remaining = parser.parse_known_args()
    if any(arg == "--output-dir" or arg.startswith("--output-dir=") for arg in remaining):
        parser.error("supply --output-dir exactly once")
    output = Path(args.output_dir).expanduser()
    if not output.is_absolute():
        parser.error("--output-dir must be absolute")
    output = output.resolve()
    skill = Path(__file__).resolve().parents[1]
    if output == skill or skill in output.parents:
        parser.error("--output-dir must be outside the installed skill")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(skill / "scripts"))
    sys.argv = [str(skill / "scripts" / "update_news.py"), "--output-dir", str(output), *remaining]
    runpy.run_path(sys.argv[0], run_name="__main__")

if __name__ == "__main__":
    main()
