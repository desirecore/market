<!-- locale: zh-CN -->

# python-runtime 技能

## L0：一句话摘要

**何时使用**：用户需要 安装 Python / 升级 Python / 切换 Python 多版本 / 配置
pip / 创建虚拟环境（venv / pipx / conda）/ 排查 `python: command not found`、
`pip: command not found`、PEP 668 "externally-managed"、SSL 证书、import 失败、
PATH 异常 等 Python 运行时问题，或其他 skill（docx / pdf / xlsx / pptx）报告
"Python 不可用" 时。

**怎么做**：先确认 `python3` 是否已可用：DesireCore 把内置 Python 目录追加到了服务 PATH，通常不需要安装。
需要安装或切换版本时，优先使用 DesireCore 内置 Hatch，按四级降级（HTTP API → Hatch CLI →
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
| `system_python.path` 非空且版本够用 | 直接用这个解释器，pip 用 `"<system_python.path>" -m pip`，不需要安装 |
| 需要指定版本，且 `hatch_versions` 已列出 | 绝对路径 `${DESIRECORE_ROOT}/runtime/hatch/local/<version>/python/bin/python3`（→ `references/hatch-desirecore.md`） |
| `desirecore_api` 非空 | **L1** HTTP API |
| `desirecore_api` 空，`hatch_path` 非空 | **L2** Hatch CLI |
| 上述都不满足 | **L3** 系统包管理器（brew/apt/dnf/winget） |
| L1–L3 全部失败或用户明示 | **L4** 社区方案（pyenv） |

`system_python` 是 PATH 解析到的结果，可能就是 DesireCore 的内置 Python：一个内置版本追加在系统目录之后，系统有 `python3` 时系统版本优先。`<env>` 块的 Managed runtimes 段列出每个内置版本的绝对路径。

这个 bash 探测脚本在 Windows 上不查找 Hatch，`hatch_path` 恒为空。Windows 上降级到 L3 之前，先试 L2 里的 Windows 路径。

### 第三步：执行（仅展示主路径，详见各 references）

#### L1：HTTP API（→ `references/hatch-desirecore.md`）

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
BASE="https://127.0.0.1:${PORT}/api/runtime"

# 列出可装版本
curl -sk "${BASE}/python/available"

# 触发安装（异步，订阅 runtime:terminal 看进度）
# version 填上面列表里的 name，如 3.12，不是 3.12.12
curl -sk -X POST "${BASE}/python/install" \
  -H "Content-Type: application/json" \
  -d '{"version":"3.12"}'

# 安装完成后强制刷新缓存
curl -sk -X POST "${BASE}/environment/refresh"
```

#### L2：Hatch CLI 绝对路径（→ `references/hatch-desirecore.md`）

```bash
HATCH=$(jq -r .hatch_path /tmp/py-probe.json)
export PYAPP_INSTALL_DIR_HATCH=$(jq -r .hatch_bootstrap /tmp/py-probe.json)
LOCAL="${DESIRECORE_ROOT}/runtime/hatch/local"

"$HATCH" python install 3.12 --private --dir="$LOCAL"
"$HATCH" python show --dir "$LOCAL"    # 列出已安装/可装版本

# 直接使用 Hatch 安装的 Python
"$LOCAL/3.12/python/bin/python3" -m venv .venv
```

必须带 `--private --dir`：不带时 Hatch 装到它的用户数据目录，还会改 `.zshrc`、`.zprofile`，而 DesireCore 看不到这个 Python。每次调用都要设置 `PYAPP_INSTALL_DIR_HATCH`：DesireCore 只在自己调用时设置，不传给 Bash；不设时第一条 Hatch 命令会下载约 45MB 并解压到用户目录。二进制随包位于应用目录下的 `static/toolchains/<平台>-<架构>/hatch/hatch`；`runtime/hatch/hatch` 只有手动下载 Hatch 后才存在。

这些命令报 `ValueError: Unknown distribution source`，或 L1 安装一直等不到结果，说明首启导入留下的来源记录需要修复：见 `references/hatch-desirecore.md` 的「修复首启导入留下的来源记录」。

Windows：`<安装目录>\static\toolchains\win32-x64\hatch\hatch.exe`，`PYAPP_INSTALL_DIR_HATCH` 为 `$env:DESIRECORE_ROOT\runtime\hatch\bootstrap\<Hatch 版本>-win32-x64`。

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
5. **`hatch python install` 必须带 `--private --dir`**：否则会写用户的 shell 配置，还装到 DesireCore 看不到的地方。

## 引用关系

- 决策树：`../dev-environment-setup/references/decision-tree.md`
- DesireCore 底座：`../dev-environment-setup/references/desirecore-runtime.md`
- 探测协议：`../dev-environment-setup/references/probe-snapshot.md`
- 办公依赖：`../dev-environment-setup/references/office-deps.md`
- 系统工具：`../dev-environment-setup/references/system-tools.md`
