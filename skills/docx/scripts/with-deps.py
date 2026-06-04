#!/usr/bin/env python3
"""with-deps.py —— 跨平台 Python 启动器（无需 bash，对应已废弃的 with-deps.sh）

让 office 脚本复用客户端预装的共享依赖，免去运行时 pip install：
  - defusedxml：纯 Python，注入 PYTHONPATH（<ROOT>/runtime-deps/python-libs）
  - lxml：编译型扩展，绑定具体解释器 → 若存在受控 Python（<ROOT>/runtime-deps/
    python-runtime，已装 lxml），用它运行目标脚本，从而离线启用完整 XSD 校验；
    受控 Python 不存在 / 无法执行（如 macOS 公证拦截）→ 自动退回当前 Python
    （此时 lxml 缺失，校验会优雅降级跳过，不会崩）。

纯 Python 实现，在 Windows / macOS / Linux 上用同一条命令运行，不依赖 bash：

    python "<skill-dir>/scripts/with-deps.py" office/unpack.py document.docx unpacked/
    python "<skill-dir>/scripts/with-deps.py" office/validate.py doc.docx

目标脚本以 [解释器, 目标, *参数] 直接拉起 —— 等价于 `python <目标>`，因此脚本目录
会被 Python 自动加入 sys.path、__name__ == "__main__"、argv 与直接运行完全一致。
"""

import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))  # .../skills/docx/scripts
# scripts → docx → skills → <ROOT>
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_DEPS = os.path.join(_ROOT, "runtime-deps")
_PYLIBS = os.path.join(_DEPS, "python-libs")
_BUNDLED = os.path.join(
    _DEPS,
    "python-runtime",
    "python.exe" if os.name == "nt" else os.path.join("bin", "python3"),
)


def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write("usage: with-deps.py <script.py> [args...]\n")
        return 2

    # 目标脚本相对 scripts/ 解析（如 office/validate.py），也支持绝对路径
    arg = sys.argv[1]
    target = arg if os.path.isabs(arg) else os.path.join(_HERE, arg)
    if not os.path.isfile(target):
        sys.stderr.write(f"with-deps.py: target not found: {target}\n")
        return 2

    # 选解释器：有受控 Python（含 lxml）且当前不是它 → 用它；否则用当前/系统 Python
    interp = sys.executable
    if os.path.isfile(_BUNDLED) and os.path.realpath(_BUNDLED) != os.path.realpath(sys.executable):
        interp = _BUNDLED

    # 注入 defusedxml（os.pathsep 跨平台自动 ';' / ':'）
    env = dict(os.environ)
    if os.path.isdir(_PYLIBS):
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = _PYLIBS + (os.pathsep + existing if existing else "")

    cmd = [interp, target, *sys.argv[2:]]
    try:
        rc = subprocess.run(cmd, env=env).returncode
    except OSError:
        rc = 126  # 受控 Python 无法启动

    # 受控 Python 跑不了（rc<0=被信号杀，如 macOS Gatekeeper；126/127=无法执行）
    # → 退回系统 Python，让脚本在缺 lxml 时优雅降级，而不是把整条命令判为失败
    if interp != sys.executable and (rc < 0 or rc in (126, 127)):
        rc = subprocess.run([sys.executable, target, *sys.argv[2:]], env=env).returncode

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
