#!/usr/bin/env python3
"""Render PPTX to PDF through a tested PowerPoint or isolated LibreOffice backend."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path


POWERPOINT_APP = Path("/Applications/Microsoft PowerPoint.app")


def powerpoint_available() -> bool:
    return platform.system() == "Darwin" and POWERPOINT_APP.exists() and shutil.which("osascript") is not None


def libreoffice_path() -> str | None:
    return shutil.which("soffice") or shutil.which("libreoffice")


def valid_pdf(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size <= 100:
        return False
    data = path.read_bytes()
    return data.startswith(b"%PDF-") and b"%%EOF" in data[-2048:]


def run_powerpoint(source: Path, output: Path) -> dict[str, object]:
    script = r'''
on run argv
    set sourcePath to item 1 of argv
    set outputPath to item 2 of argv
    set openedDeck to missing value
    try
        with timeout of 180 seconds
            tell application "Microsoft PowerPoint"
                activate
                open POSIX file sourcePath
                delay 1
                set openedDeck to active presentation
                save openedDeck in POSIX file outputPath as save as PDF
                delay 1
                close openedDeck saving no
            end tell
        end timeout
    on error errorMessage number errorNumber
        try
            if openedDeck is not missing value then
                tell application "Microsoft PowerPoint" to close openedDeck saving no
            end if
        end try
        error errorMessage number errorNumber
    end try
end run
'''
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    try:
        result = subprocess.run(
            ["osascript", "-", str(source), str(output)],
            input=script,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=210,
        )
        return {"backend": "powerpoint-macos", "fidelity": "target", "returncode": result.returncode, "stdout": result.stdout[-2000:], "stderr": result.stderr[-2000:], "output_exists": output.is_file(), "output_size": output.stat().st_size if output.is_file() else 0, "valid_pdf": valid_pdf(output)}
    except subprocess.TimeoutExpired as exc:
        return {"backend": "powerpoint-macos", "fidelity": "target", "returncode": 124, "stdout": (exc.stdout or "")[-2000:], "stderr": "PowerPoint automation timed out", "output_exists": output.is_file(), "output_size": output.stat().st_size if output.is_file() else 0, "valid_pdf": valid_pdf(output)}


def run_libreoffice(source: Path, output: Path) -> dict[str, object]:
    executable = libreoffice_path()
    if not executable:
        return {"backend": "libreoffice", "fidelity": "approximate", "returncode": 127, "stderr": "soffice/libreoffice not found", "output_exists": False, "output_size": 0}
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with tempfile.TemporaryDirectory(prefix="codex-ppt-lo-profile-") as profile:
        env = os.environ.copy()
        env.setdefault("SAL_USE_VCLPLUGIN", "svp")
        cache_dir = Path(profile) / "cache"
        cache_dir.mkdir()
        env["XDG_CACHE_HOME"] = str(cache_dir)
        try:
            result = subprocess.run(
                [executable, f"-env:UserInstallation={Path(profile).as_uri()}", "--headless", "--convert-to", "pdf", "--outdir", str(output.parent), str(source)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=180,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            return {"backend": "libreoffice", "fidelity": "approximate", "returncode": 124, "stdout": (exc.stdout or "")[-2000:], "stderr": "LibreOffice conversion timed out", "output_exists": False, "output_size": 0, "valid_pdf": False}
    generated = output.parent / source.with_suffix(".pdf").name
    if generated.is_file() and generated != output:
        generated.replace(output)
    return {"backend": "libreoffice", "fidelity": "approximate", "returncode": result.returncode, "stdout": result.stdout[-2000:], "stderr": result.stderr[-2000:], "output_exists": output.is_file(), "output_size": output.stat().st_size if output.is_file() else 0, "valid_pdf": valid_pdf(output)}


def succeeded(attempt: dict[str, object]) -> bool:
    return attempt.get("returncode") == 0 and attempt.get("output_exists") is True and attempt.get("valid_pdf") is True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--backend", choices=("auto", "powerpoint", "libreoffice"), default="auto")
    parser.add_argument("--allow-approximate", action="store_true", help="Allow LibreOffice output to pass instead of remaining QA-only.")
    parser.add_argument("--report")
    args = parser.parse_args()
    source = Path(args.input).resolve()
    if not source.is_file():
        raise SystemExit(f"input PPTX not found: {source}")
    output = Path(args.out_dir).resolve() / source.with_suffix(".pdf").name
    attempts: list[dict[str, object]] = []
    if args.backend in {"auto", "powerpoint"}:
        if powerpoint_available():
            attempts.append(run_powerpoint(source, output))
        else:
            attempts.append({"backend": "powerpoint-macos", "fidelity": "target", "returncode": 127, "stderr": "PowerPoint automation unavailable", "output_exists": False, "output_size": 0})
    if not any(succeeded(row) for row in attempts) and args.backend in {"auto", "libreoffice"}:
        attempts.append(run_libreoffice(source, output))
    selected = next((row for row in attempts if succeeded(row)), None)
    status = "FAIL"
    if selected:
        status = "PASS" if selected["fidelity"] == "target" else "APPROXIMATE"
    report = {"status": status, "input": str(source), "output": str(output) if selected else None, "selected_backend": selected["backend"] if selected else None, "attempts": attempts}
    if args.report:
        report_path = Path(args.report); report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if status == "FAIL" or (status == "APPROXIMATE" and not args.allow_approximate):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
