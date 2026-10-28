#!/usr/bin/env python3
"""Run Office XML scripts with the client's prepared Python dependencies.

Each installed skill carries this launcher so it works without another Office
skill. The bootstrap uses only the standard library, including on Python 3.9;
the target requires Python 3.10+ and prefers the runtime's prepared interpreter.
No packages are installed and target failures are never reported as success.

    python "<skill-dir>/scripts/with-deps.py" office/unpack.py input.pptx unpacked/
"""

import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
# scripts -> skill -> skills -> the effective DesireCore data root
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_PYLIBS = os.path.join(_ROOT, "runtime-deps", "python-libs")
_BUNDLED = os.path.join(
    _ROOT,
    "runtime-deps",
    "python-runtime",
    "python.exe" if os.name == "nt" else os.path.join("bin", "python3"),
)


def _current_python_supported():
    if sys.version_info[:2] >= (3, 10):
        return True
    sys.stderr.write(
        "with-deps.py: Office XML scripts require Python 3.10+. "
        "Prepare the managed Python runtime in DesireCore and retry.\n"
    )
    return False


def main():
    arguments = list(sys.argv[1:])
    current_python = bool(arguments and arguments[0] == "--current-python")
    if current_python:
        arguments.pop(0)
    if not arguments:
        sys.stderr.write("usage: with-deps.py [--current-python] <script.py> [args...]\n")
        return 2

    argument = arguments[0]
    target = argument if os.path.isabs(argument) else os.path.join(_HERE, argument)
    if not os.path.isfile(target):
        sys.stderr.write("with-deps.py: target not found: " + target + "\n")
        return 2

    interpreter = sys.executable
    if not current_python and os.path.isfile(_BUNDLED):
        if os.path.realpath(_BUNDLED) != os.path.realpath(sys.executable):
            interpreter = _BUNDLED
    if interpreter == sys.executable and not _current_python_supported():
        return 1

    environment = dict(os.environ)
    if os.path.isdir(_PYLIBS):
        existing = environment.get("PYTHONPATH")
        environment["PYTHONPATH"] = _PYLIBS + (os.pathsep + existing if existing else "")
    # Running a skill must not change its installed content digest through .pyc.
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    arguments = ["-B", target, *arguments[1:]]
    try:
        return subprocess.run([interpreter, *arguments], env=environment).returncode
    except OSError as error:
        if interpreter == sys.executable:
            sys.stderr.write("with-deps.py: could not start Python: " + str(error) + "\n")
            return 126
        # Fall back only when the process could not start. A target's nonzero
        # exit or signal must never replay an edit that may have already run.
        sys.stderr.write("with-deps.py: managed Python could not start; trying current Python.\n")
        if not _current_python_supported():
            return 1
        try:
            return subprocess.run([sys.executable, *arguments], env=environment).returncode
        except OSError as fallback_error:
            sys.stderr.write("with-deps.py: could not start Python: " + str(fallback_error) + "\n")
            return 126


if __name__ == "__main__":
    raise SystemExit(main())
