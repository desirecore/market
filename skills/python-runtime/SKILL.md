---
name: python-runtime
description: >-
  Use this skill when the user needs to install, upgrade, or troubleshoot
  Python and pip environments. Covers four-tier fallback strategy: (1)
  DesireCore HTTP API for in-app installation, (2) DesireCore built-in Hatch
  CLI for Python version management, (3) system package managers
  (brew/apt/dnf/winget), (4) community pyenv as last resort. Also covers
  virtual environments (venv/pipx/conda), PEP 668 externally-managed errors,
  and import / PATH troubleshooting. Triggers include: "install python", "pip
  not found", "python not found", "PEP 668", "externally-managed", "venv",
  "virtualenv", "pipx", "conda", "miniconda", "pyenv", "hatch", "python
  version", "pip command not found", or any Python-related runtime error.
  使用场景：用户需要 安装 Python、安装 pip、配置虚拟环境、管理多版本、
  解决 PEP 668、import 失败、PATH 问题、SSL 证书错误等。
version: 1.0.3
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - python
  - pip
  - hatch
  - pyenv
  - venv
  - virtualenv
  - pipx
  - conda
  - environment
metadata:
  author: desirecore
  updated_at: '2026-05-02'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: Python 运行时管理
      short_desc: Python 安装、多版本与虚拟环境（DesireCore Hatch 优先）
      description: >-
        Use this skill when the user needs to install, upgrade, or troubleshoot Python and pip environments. Covers four-tier fallback strategy: (1) DesireCore HTTP API for in-app installation, (2) DesireCore built-in Hatch CLI for Python version management, (3) system package managers (brew/apt/dnf/winget), (4) community pyenv as last resort. Also covers virtual environments (venv/pipx/conda), PEP 668 externally-managed errors, and import / PATH troubleshooting. Triggers include: "install python", "pip not found", "python not found", "PEP 668", "externally-managed", "venv", "virtualenv", "pipx", "conda", "miniconda", "pyenv", "hatch", "python version", "pip command not found", or any Python-related runtime error. 使用场景：用户需要 安装 Python、安装 pip、配置虚拟环境、管理多版本、 解决 PEP 668、import 失败、PATH 问题、SSL 证书错误等。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:ea796e0282dc77af
      translated_by: human
    en-US:
      name: Python Runtime Management
      short_desc: Python install, multi-version, and virtual envs (DesireCore Hatch first)
      description: >-
        Use this skill when the user needs to install, upgrade, or troubleshoot Python and pip environments. Covers four-tier fallback strategy: (1) DesireCore HTTP API for in-app installation, (2) DesireCore built-in Hatch CLI for Python version management, (3) system package managers (brew/apt/dnf/winget), (4) community pyenv as last resort. Also covers virtual environments (venv/pipx/conda), PEP 668 externally-managed errors, and import / PATH troubleshooting. Triggers include: "install python", "pip not found", "python not found", "PEP 668", "externally-managed", "venv", "virtualenv", "pipx", "conda", "miniconda", "pyenv", "hatch", "python version", "pip command not found", or any Python-related runtime error. Use when the user needs to install Python, install pip, configure virtual environments, manage multiple versions, resolve PEP 668, import failures, PATH issues, SSL certificate errors, etc.
      body: ./SKILL.md
      source_hash: sha256:585a14843750b051
      translated_by: human
      translated_at: '2026-05-03'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="py-a" x1="3" y1="3" x2="21"
    y2="21" gradientUnits="userSpaceOnUse"><stop
    stop-color="#306998"/><stop offset="1"
    stop-color="#FFD43B"/></linearGradient></defs><rect x="3" y="3" width="18"
    height="18" rx="3" fill="url(#py-a)" fill-opacity="0.12"
    stroke="url(#py-a)" stroke-width="1.5"/><path d="M9 8.5h4.5a1.5 1.5 0 011.5
    1.5v3a1.5 1.5 0 01-1.5 1.5H9.5A1.5 1.5 0 008 16v.5" stroke="url(#py-a)"
    stroke-width="1.4" stroke-linecap="round" fill="none"/><path d="M15
    15.5h-4.5a1.5 1.5 0 01-1.5-1.5v-3a1.5 1.5 0 011.5-1.5H14.5A1.5 1.5 0 0016
    8v-.5" stroke="url(#py-a)" stroke-width="1.4" stroke-linecap="round"
    fill="none"/><circle cx="10.5" cy="10" r="0.6" fill="url(#py-a)"/><circle
    cx="13.5" cy="14" r="0.6" fill="url(#py-a)"/></svg>
  category: development
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# python-runtime Skill

## L0: One-line Summary

**When to use**: The user needs to install Python / upgrade Python / switch
between multiple Python versions / configure pip / create virtual environments
(venv / pipx / conda) / troubleshoot `python: command not found`,
`pip: command not found`, PEP 668 "externally-managed", SSL certificates,
import failures, PATH anomalies, and other Python runtime issues; or when
another skill (docx / pdf / xlsx / pptx) reports "Python unavailable".

**How to do it**: Prefer DesireCore's built-in Hatch, executing through the
four-tier fallback (HTTP API → Hatch CLI → system package manager
brew/apt/dnf/winget → community solution pyenv).

## L1: Overview and Use Cases

### Capability Description

Procedural skill. Before each Python environment operation, first run `scripts/probe-python.sh` to obtain a JSON snapshot, then follow `references/decision-tree` (→ `../dev-environment-setup/references/decision-tree.md`) to choose a path through the four-tier fallback.

### Use Cases

- "python not found" / "pip not found"
- The user requests to install/upgrade Python
- The user requests multi-version management (3.10/3.11/3.12 switching)
- Create/activate/debug virtual environments (venv/pipx/conda)
- "externally-managed-environment" (PEP 668) error
- import failures, PATH issues, SSL certificate errors
- Other skills (docx/pdf/xlsx/pptx) report Python unavailable

### Core Value

- **DesireCore first**: Hatch + HTTP API as mandatory L1/L2, avoiding pollution of system Python
- **JSON-driven decisions**: the probe script outputs structured data that Claude can parse directly
- **Cross-platform consistency**: macOS / Linux / Windows share a unified 4-tier fallback

## L2: Detailed Specification

### Step 1: Environment Probe (mandatory)

```bash
bash skills/python-runtime/scripts/probe-python.sh > /tmp/py-probe.json
cat /tmp/py-probe.json | jq .
```

For the meaning of output fields, see `../dev-environment-setup/references/probe-snapshot.md`.

### Step 2: Choose an Execution Path

Decide using `../dev-environment-setup/references/decision-tree.md`:

| Condition | Path |
|------|------|
| `desirecore_api` is non-empty | **L1** HTTP API |
| `desirecore_api` empty, `hatch_path` non-empty | **L2** Hatch CLI |
| Neither of the above | **L3** system package manager (brew/apt/dnf/winget) |
| L1–L3 all fail or user explicitly requests | **L4** community solution (pyenv) |

### Step 3: Execute (only the main path is shown; see references for details)

#### L1: HTTP API (→ `references/hatch-desirecore.md`)

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
BASE="https://127.0.0.1:${PORT}/api/runtime"

# List installable versions
curl -sk "${BASE}/python/available"

# Trigger install (asynchronous; subscribe to runtime:terminal for progress)
curl -sk -X POST "${BASE}/python/install" \
  -H "Content-Type: application/json" \
  -d '{"version":"3.12"}'

# Force-refresh the cache after install completes
curl -sk -X POST "${BASE}/environment/refresh"
```

#### L2: Hatch CLI absolute path (→ `references/hatch-desirecore.md`)

```bash
HATCH=${DESIRECORE_ROOT}/runtime/hatch/hatch
export HATCH_HOME=${DESIRECORE_ROOT}/runtime/hatch

"$HATCH" python install 3.12
"$HATCH" python show           # List installed/installable versions

# Use the Hatch-installed Python directly
${DESIRECORE_ROOT}/runtime/hatch/local/3.12/python/bin/python3 -m venv .venv
```

Windows: `%USERPROFILE%\.desirecore\runtime\hatch\hatch.exe`.

#### L3: System Package Manager

| Platform | Command |
|------|------|
| macOS | `brew install python3` |
| Debian/Ubuntu | `sudo apt install python3 python3-pip python3-venv` |
| Fedora/RHEL | `sudo dnf install python3 python3-pip` |
| Arch | `sudo pacman -S python python-pip` |
| Windows | `winget install Python.Python.3` |

#### L4: pyenv (→ `references/pyenv-fallback.md`)

Only enable when the user explicitly requests it or the above paths fail.

### Step 4: Virtual Environments

For virtual environment strategy, see `references/virtualenv.md`:
- venv (recommended, standard library)
- pipx (global CLI tools such as black/ruff/markitdown)
- conda / miniconda (data-science scenarios)

### Step 5: Troubleshooting

When errors occur, look up `references/troubleshooting.md`:
- "python: command not found" / "pip: command not found"
- PEP 668 "externally-managed-environment"
- SSL/TLS certificate errors
- import failures (package name vs. import name differences)
- macOS xcrun / Xcode CLI missing
- Windows PowerShell execution policy blocking scripts
- Proxy environment configuration

## Important Constraints

1. **Never `sudo pip install`**: always use a virtual environment or `pipx`.
2. **Refresh after modifying the environment**: for L1 call `POST /api/runtime/environment/refresh`; for L2/L3/L4 re-run probe.
3. **Cross-skill collaboration**: when `docx` / `pdf` / `xlsx` / `pptx` report "Python unavailable", fall into L1/L2 install; for office dependency lookup see `../dev-environment-setup/references/office-deps.md`.
4. **Do not pollute system Python**: at the project level always use venv; for global CLI use pipx.

## References

- Decision tree: `../dev-environment-setup/references/decision-tree.md`
- DesireCore base: `../dev-environment-setup/references/desirecore-runtime.md`
- Probe protocol: `../dev-environment-setup/references/probe-snapshot.md`
- Office dependencies: `../dev-environment-setup/references/office-deps.md`
- System tools: `../dev-environment-setup/references/system-tools.md`
