---
name: Python 运行时管理
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
version: 1.0.1
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
  short_desc: Python 安装、多版本与虚拟环境（DesireCore Hatch 优先）
  category: development
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# python-runtime 技能

## L0：一句话摘要

**何时使用**：用户需要 安装 Python / 升级 Python / 切换 Python 多版本 / 配置
pip / 创建虚拟环境（venv / pipx / conda）/ 排查 `python: command not found`、
`pip: command not found`、PEP 668 "externally-managed"、SSL 证书、import 失败、
PATH 异常 等 Python 运行时问题，或其他 skill（docx / pdf / xlsx / pptx）报告
"Python 不可用" 时。

**怎么做**：优先使用 DesireCore 内置 Hatch，按四级降级（HTTP API → Hatch CLI →
系统包管理器 brew/apt/dnf/winget → 社区方案 pyenv）执行。

## L1：概述与使用场景

### 能力描述

procedural skill。每次执行 Python 环境操作前，先运行 `scripts/probe-python.sh` 取 JSON 快照，再按 `references/decision-tree`（→ `../dev-environment-setup/references/decision-tree.md`）四级降级选择路径。

### 使用场景

- "python not found" / "pip not found"
- 用户要求安装/升级 Python
- 用户要求多版本管理（3.10/3.11/3.12 切换）
- 创建/激活/调试虚拟环境（venv/pipx/conda）
- "externally-managed-environment"（PEP 668）报错
- import 失败、PATH 问题、SSL 证书错误
- 其他 skill（docx/pdf/xlsx/pptx）报告 Python 不可用

### 核心价值

- **DesireCore 优先**：Hatch + HTTP API 作为强制 L1/L2，避免污染系统 Python
- **JSON 决策**：probe 脚本输出结构化数据，Claude 可直接解析
- **跨平台一致**：macOS / Linux / Windows 统一 4 级降级

## L2：详细规范

### 第一步：环境探测（必须）

```bash
bash skills/python-runtime/scripts/probe-python.sh > /tmp/py-probe.json
cat /tmp/py-probe.json | jq .
```

输出字段含义见 `../dev-environment-setup/references/probe-snapshot.md`。

### 第二步：选择执行路径

按 `../dev-environment-setup/references/decision-tree.md` 判断：

| 条件 | 路径 |
|------|------|
| `desirecore_api` 非空 | **L1** HTTP API |
| `desirecore_api` 空，`hatch_path` 非空 | **L2** Hatch CLI |
| 上述都不满足 | **L3** 系统包管理器（brew/apt/dnf/winget） |
| L1–L3 全部失败或用户明示 | **L4** 社区方案（pyenv） |

### 第三步：执行（仅展示主路径，详见各 references）

#### L1：HTTP API（→ `references/hatch-desirecore.md`）

```bash
PORT=$(cat ~/.desirecore/agent-service.port)
BASE="https://127.0.0.1:${PORT}/api/runtime"

# 列出可装版本
curl -sk "${BASE}/python/available"

# 触发安装（异步，订阅 runtime:terminal 看进度）
curl -sk -X POST "${BASE}/python/install" \
  -H "Content-Type: application/json" \
  -d '{"version":"3.12"}'

# 安装完成后强制刷新缓存
curl -sk -X POST "${BASE}/environment/refresh"
```

#### L2：Hatch CLI 绝对路径（→ `references/hatch-desirecore.md`）

```bash
HATCH=~/.desirecore/runtime/hatch/hatch
export HATCH_HOME=~/.desirecore/runtime/hatch

"$HATCH" python install 3.12
"$HATCH" python show           # 列出已安装/可装版本

# 直接使用 Hatch 安装的 Python
~/.desirecore/runtime/hatch/local/3.12/python/bin/python3 -m venv .venv
```

Windows：`%USERPROFILE%\.desirecore\runtime\hatch\hatch.exe`。

#### L3：系统包管理器

| 平台 | 命令 |
|------|------|
| macOS | `brew install python3` |
| Debian/Ubuntu | `sudo apt install python3 python3-pip python3-venv` |
| Fedora/RHEL | `sudo dnf install python3 python3-pip` |
| Arch | `sudo pacman -S python python-pip` |
| Windows | `winget install Python.Python.3` |

#### L4：pyenv（→ `references/pyenv-fallback.md`）

仅在用户明示或上述失败时启用。

### 第四步：虚拟环境

虚拟环境策略详见 `references/virtualenv.md`：
- venv（推荐，标准库）
- pipx（全局 CLI 工具如 black/ruff/markitdown）
- conda / miniconda（数据科学场景）

### 第五步：故障排查

报错时按 `references/troubleshooting.md` 查表：
- "python: command not found" / "pip: command not found"
- PEP 668 "externally-managed-environment"
- SSL/TLS 证书错误
- import 失败（包名 vs import 名差异）
- macOS xcrun / Xcode CLI 缺失
- Windows PowerShell 执行策略阻止脚本
- 代理环境配置

## 重要约束

1. **绝不 `sudo pip install`**：始终用虚拟环境或 `pipx`。
2. **修改了环境后必须刷新**：L1 调 `POST /api/runtime/environment/refresh`；L2/L3/L4 重新跑 probe。
3. **跨 skill 协作**：`docx` / `pdf` / `xlsx` / `pptx` 报"Python 不可用"时，进入 L1/L2 安装；办公依赖速查见 `../dev-environment-setup/references/office-deps.md`。
4. **不污染系统 Python**：项目级别一律使用 venv，全局 CLI 用 pipx。

## 引用关系

- 决策树：`../dev-environment-setup/references/decision-tree.md`
- DesireCore 底座：`../dev-environment-setup/references/desirecore-runtime.md`
- 探测协议：`../dev-environment-setup/references/probe-snapshot.md`
- 办公依赖：`../dev-environment-setup/references/office-deps.md`
- 系统工具：`../dev-environment-setup/references/system-tools.md`
