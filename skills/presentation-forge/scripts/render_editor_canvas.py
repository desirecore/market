#!/usr/bin/env python3
"""Render the real multi-page editor UI from an editor manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    helper = Path(__file__).resolve().parents[1] / "assets" / "editor" / "render_editor_canvas.py"
    result = subprocess.run([sys.executable, str(helper), "--manifest", args.manifest, "--out", args.out], check=False)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
