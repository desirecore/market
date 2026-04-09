---
name: 开发环境配置
description: >-
  Use this skill when the user needs help setting up a development environment,
  installing Python, Node.js, or their package managers, managing multiple
  runtime versions, creating virtual environments, or troubleshooting
  environment-related issues. Triggers include: "install python", "install
  node", "setup environment", "virtual environment", "venv", "nvm", "pyenv",
  "pip not found", "python not found", "node not found", "npm not found",
  "PATH issues", "version manager", or any error message indicating a missing
  runtime or package manager. Also use when other skills (docx, pdf, xlsx,
  pptx) report that Python or Node.js is not available and the user needs
  guidance. Use when 用户提到 安装Python、安装Node、环境配置、虚拟环境、
  版本管理、PATH问题、pip找不到、python找不到。
version: 1.0.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: false
tags:
  - environment
  - python
  - nodejs
  - setup
  - troubleshooting
metadata:
  author: desirecore
  updated_at: '2026-04-08'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="env-a" x1="3" y1="3" x2="21"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#34C759"/><stop
    offset="1" stop-color="#007AFF"/></linearGradient></defs><rect x="3" y="3"
    width="18" height="18" rx="3" fill="url(#env-a)" fill-opacity="0.1"
    stroke="url(#env-a)" stroke-width="1.5"/><path d="M7 8l3 3-3 3"
    stroke="url(#env-a)" stroke-width="1.5" stroke-linecap="round"
    stroke-linejoin="round"/><path d="M13 16h4" stroke="url(#env-a)"
    stroke-width="1.5" stroke-linecap="round"/></svg>
  short_desc: Python / Node.js 环境安装、版本管理与问题排查
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# Environment Setup Guide

本技能提供 Python 和 Node.js 开发环境的完整安装、多版本管理、虚拟环境配置以及常见问题排查指南。

---

## 快速诊断

在进行任何安装之前，先运行以下命令检查当前环境状态：

```bash
echo "=== OS ===" && uname -a
echo "=== Python ===" && python3 --version 2>/dev/null || python --version 2>/dev/null || echo "NOT FOUND"
echo "=== pip ===" && pip3 --version 2>/dev/null || pip --version 2>/dev/null || echo "NOT FOUND"
echo "=== Node.js ===" && node --version 2>/dev/null || echo "NOT FOUND"
echo "=== npm ===" && npm --version 2>/dev/null || echo "NOT FOUND"
echo "=== PATH ===" && echo "$PATH" | tr ':' '\n'
```

根据输出结果，跳转到对应章节。

---

## Python 安装

### macOS

#### 方式 1：Homebrew（推荐）

```bash
# 安装 Homebrew（如果尚未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python 3
brew install python3

# 验证安装
python3 --version
pip3 --version
```

Homebrew 安装的 Python 位于 `/opt/homebrew/bin/python3`（Apple Silicon）或 `/usr/local/bin/python3`（Intel）。

#### 方式 2：官方安装包

1. 访问 https://www.python.org/downloads/
2. 下载最新的 macOS 安装包（.pkg）
3. 双击运行安装程序，按照向导完成安装
4. 安装完成后打开新终端窗口验证：

```bash
python3 --version
```

#### macOS 注意事项

- macOS 自带的 `/usr/bin/python3` 是 Apple 提供的精简版，缺少 `pip`，**不建议用于开发**
- 如果运行 `pip3` 提示 "No module named pip"，说明在使用系统自带 Python，请安装 Homebrew 或官方版本
- Xcode Command Line Tools 安装：`xcode-select --install`（部分 Python 包编译时需要）

### Windows

#### 方式 1：winget（推荐）

```powershell
winget install Python.Python.3
```

安装后**重启终端**，验证：

```powershell
python --version
pip --version
```

#### 方式 2：官方安装包

1. 访问 https://www.python.org/downloads/
2. 下载 Windows installer（.exe）
3. **务必勾选 "Add Python to PATH"**（安装界面底部的复选框）
4. 点击 "Install Now"
5. 安装完成后打开新的 CMD 或 PowerShell 验证

#### Windows 注意事项

- Windows 10/11 自带的 `python` 命令可能指向 Microsoft Store 的占位符，会弹出商店页面而非执行 Python。安装官方 Python 后此行为会被覆盖
- 如果安装后 `python` 仍指向 Store，在系统设置 > 应用 > 高级应用设置 > 应用执行别名中关闭 "python.exe" 和 "python3.exe" 的 Store 别名
- PowerShell 执行策略可能阻止脚本运行：`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
pip3 --version
```

### Linux (Fedora/RHEL/CentOS)

```bash
sudo dnf install python3 python3-pip
python3 --version
pip3 --version
```

### Linux (Arch)

```bash
sudo pacman -S python python-pip
python --version
pip --version
```

### Linux 注意事项

- 部分发行版（如 Debian 12+、Ubuntu 23.04+）启用了 PEP 668 "externally managed environment" 策略，`pip install` 全局安装会被拒绝。解决方法见下方"虚拟环境"章节，或使用 `pipx`
- 如果系统同时存在 Python 2 和 Python 3，确保使用 `python3` 和 `pip3` 而非 `python` 和 `pip`

---

## Python 多版本管理（Hatch — DesireCore 内置）

DesireCore 内置了 [Hatch](https://hatch.pypa.io/) v1.16.5 作为 Python 项目管理器和版本管理器。Hatch 二进制随应用打包在 `static/hatch/` 中，**无需用户单独安装**。

> **与系统 Python 的关系**：Hatch 管理的 Python 版本安装在 `~/.desirecore/runtime/hatch/local/` 中，与系统 Python 完全隔离，不会影响系统环境。

### 查看可安装的 Python 版本

```bash
# Hatch 二进制位置（DesireCore 自动管理，通常无需手动调用）
# macOS / Linux:
~/.desirecore/runtime/hatch/hatch python show

# 输出示例：
# ┌──────────┬─────────┐
# │ Name     │ Version │
# ├──────────┼─────────┤
# │ 3.8      │ 3.8.20  │
# │ 3.9      │ 3.9.21  │
# │ 3.10     │ 3.10.16 │
# │ 3.11     │ 3.11.11 │
# │ 3.12     │ 3.12.8  │
# │ 3.13     │ 3.13.1  │
# │ pypy3.10 │ 7.3.17  │
# └──────────┴─────────┘
```

### 安装 Python 版本

```bash
# 安装指定版本（下载到 ~/.desirecore/runtime/hatch/local/）
hatch python install 3.12
hatch python install 3.11

# 安装多个版本
hatch python install 3.12 3.11 3.10
```

### 查看已安装版本

```bash
# 查看 ~/.desirecore/runtime/hatch/local/ 下的目录
ls ~/.desirecore/runtime/hatch/local/
# 输出：3.11  3.12
```

### 移除 Python 版本

```bash
hatch python remove 3.11
```

### 使用 Hatch 管理的 Python

```bash
# 直接使用安装的 Python
~/.desirecore/runtime/hatch/local/3.12/python/bin/python3 --version

# 创建虚拟环境
~/.desirecore/runtime/hatch/local/3.12/python/bin/python3 -m venv .venv
source .venv/bin/activate
```

### 可视化管理

打开 DesireCore 应用 → 资源管理器（侧边栏文件夹图标）→ 计算资源 → **运行环境** Tab，可以可视化地查看、安装、删除 Python 版本。

### Hatch vs pyenv

| 特性 | Hatch (DesireCore 内置) | pyenv (社区) |
|------|------------------------|-------------|
| 安装方式 | 随 DesireCore 自动内置 | 需手动安装 |
| Python 存放位置 | `~/.desirecore/runtime/hatch/local/` | `~/.pyenv/versions/` |
| 版本切换 | 通过绝对路径或 venv | `pyenv global/local` |
| 系统影响 | 完全隔离 | 修改 shell PATH |
| GUI 管理 | DesireCore 运行环境 Tab | 无 |
| 适用场景 | DesireCore 技能执行环境 | 日常开发多版本管理 |

---

## Python 多版本管理（pyenv — 社区方案）

当需要在系统级别管理多个 Python 版本时，pyenv 是社区中最流行的方案。

### 安装 pyenv

#### macOS / Linux

```bash
# 安装 pyenv
curl https://pyenv.run | bash

# 添加到 shell 配置（zsh）
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# 添加到 shell 配置（bash）
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# 重新加载 shell
exec "$SHELL"
```

#### macOS 编译依赖

```bash
brew install openssl readline sqlite3 xz zlib tcl-tk
```

#### Ubuntu/Debian 编译依赖

```bash
sudo apt install build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev curl git \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
  libffi-dev liblzma-dev
```

#### Fedora/RHEL 编译依赖

```bash
sudo dnf install gcc make zlib-devel bzip2 bzip2-devel \
  readline-devel sqlite sqlite-devel openssl-devel tk-devel \
  libffi-devel xz-devel
```

#### Windows

Windows 上推荐使用 [pyenv-win](https://github.com/pyenv-win/pyenv-win)：

```powershell
# 通过 pip 安装
pip install pyenv-win --target "$HOME\.pyenv"

# 或通过 PowerShell 脚本安装
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

添加到环境变量（PowerShell profile）：

```powershell
[System.Environment]::SetEnvironmentVariable('PYENV', "$HOME\.pyenv\pyenv-win", 'User')
[System.Environment]::SetEnvironmentVariable('PYENV_HOME', "$HOME\.pyenv\pyenv-win", 'User')
# 将 %PYENV%\bin 和 %PYENV%\shims 添加到 PATH
```

### 使用 pyenv

```bash
# 查看可安装的版本
pyenv install --list | grep "^  3\."

# 安装指定版本
pyenv install 3.12.4
pyenv install 3.11.9

# 设置全局默认版本
pyenv global 3.12.4

# 设置当前目录（项目级别）的 Python 版本
pyenv local 3.11.9    # 创建 .python-version 文件

# 查看已安装的版本
pyenv versions

# 查看当前激活的版本
pyenv version

# 卸载版本
pyenv uninstall 3.10.14
```

---

## Python 虚拟环境

虚拟环境隔离项目依赖，避免全局污染。**强烈建议每个项目使用独立的虚拟环境。**

### venv（内置，推荐）

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
# macOS / Linux:
source .venv/bin/activate
# Windows CMD:
.venv\Scripts\activate.bat
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# 验证（应显示 .venv 中的 python）
which python    # macOS/Linux
where python    # Windows

# 安装依赖
pip install -r requirements.txt

# 退出虚拟环境
deactivate
```

### pipx（安装全局 CLI 工具）

当需要全局安装命令行工具（如 `black`、`ruff`、`markitdown`）但不想污染系统 Python 环境时：

```bash
# 安装 pipx
# macOS:
brew install pipx
pipx ensurepath

# Linux (Debian/Ubuntu):
sudo apt install pipx
pipx ensurepath

# Windows:
pip install --user pipx
pipx ensurepath

# 使用 pipx 安装工具
pipx install black
pipx install ruff
pipx install markitdown
```

### conda / miniconda

适用于数据科学和需要非 Python 依赖（如 BLAS、CUDA）的场景：

```bash
# 安装 miniconda（macOS / Linux）
curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-$(uname -s)-$(uname -m).sh -o miniconda.sh
bash miniconda.sh -b -p "$HOME/miniconda3"
eval "$("$HOME/miniconda3/bin/conda" shell.$(basename $SHELL) hook)"

# 创建环境
conda create -n myproject python=3.12
conda activate myproject

# 安装包
conda install numpy pandas scikit-learn
pip install some-pypi-only-package   # conda 没有的包用 pip

# 退出
conda deactivate
```

---

## Node.js 安装

### macOS

#### 方式 1：Homebrew

```bash
brew install node
node --version
npm --version
```

#### 方式 2：官方安装包

1. 访问 https://nodejs.org/
2. 下载 LTS 版本的 macOS 安装包（.pkg）
3. 运行安装程序

### Windows

#### 方式 1：winget

```powershell
winget install OpenJS.NodeJS.LTS
```

#### 方式 2：官方安装包

1. 访问 https://nodejs.org/
2. 下载 Windows LTS 安装包（.msi）
3. 运行安装程序（默认选项即可，会自动添加到 PATH）

### Linux (Debian/Ubuntu)

使用 NodeSource 官方仓库获取最新 LTS：

```bash
# 安装 Node.js 22.x LTS（根据需要替换版本号）
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

node --version
npm --version
```

或使用系统仓库（版本可能较旧）：

```bash
sudo apt install nodejs npm
```

### Linux (Fedora/RHEL)

```bash
curl -fsSL https://rpm.nodesource.com/setup_22.x | sudo bash -
sudo dnf install -y nodejs
```

### Linux (Arch)

```bash
sudo pacman -S nodejs npm
```

---

## Node.js 多版本管理（Volta — DesireCore 内置）

DesireCore 内置了 [Volta](https://volta.sh/) v2.0.2 作为 Node.js 工具链管理器。Volta 二进制随应用打包在 `static/volta/` 中，**无需用户单独安装**。

> **与系统 Node.js 的关系**：Volta 管理的 Node.js 和包管理器安装在 `~/.desirecore/runtime/volta/` 中，与系统 Node.js 完全隔离。

### 安装 Node.js 版本

```bash
# Volta 二进制位置（DesireCore 自动管理）
# 安装最新 LTS
volta install node@22

# 安装指定版本
volta install node@20.11.0

# 安装特定大版本的最新版
volta install node@18
```

### 安装包管理器

```bash
# 安装 pnpm
volta install pnpm@latest

# 安装 yarn
volta install yarn@latest

# 安装指定版本的 npm
volta install npm@10
```

### 查看已安装版本

```bash
# 查看已安装的 Node.js 版本
volta list node

# 查看已安装的所有工具
volta list all
```

### 固定项目版本

```bash
# 在项目目录下，固定 Node.js 和包管理器版本到 package.json
volta pin node@22
volta pin pnpm@9

# package.json 中会自动添加：
# "volta": {
#   "node": "22.x.x",
#   "pnpm": "9.x.x"
# }
```

### 版本自动切换

Volta 的核心优势：当你 `cd` 进入一个项目目录时，如果 `package.json` 中包含 `volta` 配置，Volta 会**自动切换**到指定版本，无需手动 `use`。

### 移除版本

```bash
# 移除 Node.js 版本
# 通过 DesireCore 运行环境 Tab 管理，或手动删除：
rm -rf ~/.desirecore/runtime/volta/tools/image/node/<version>
```

### 可视化管理

打开 DesireCore 应用 → 资源管理器 → 计算资源 → **运行环境** Tab，可以可视化地查看、安装、删除 Node.js 版本和包管理器。

### Volta vs nvm

| 特性 | Volta (DesireCore 内置) | nvm (社区) |
|------|------------------------|-----------|
| 安装方式 | 随 DesireCore 自动内置 | 需手动安装 |
| 版本切换 | 自动（基于 package.json） | 手动 `nvm use` 或 `.nvmrc` |
| 包管理器管理 | 支持（pnpm/yarn/npm） | 不支持 |
| Windows 支持 | 原生支持 | 需用 nvm-windows |
| 速度 | 极快（Rust 实现） | 较慢（shell 脚本） |
| 系统影响 | 完全隔离 | 修改 shell PATH |
| GUI 管理 | DesireCore 运行环境 Tab | 无 |
| 适用场景 | DesireCore 技能执行环境 | 日常开发多版本管理 |

---

## Node.js 多版本管理（nvm — 社区方案）

### 安装 nvm

#### macOS / Linux

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# 重新加载 shell 配置
source ~/.zshrc   # 或 source ~/.bashrc
```

#### Windows

Windows 上使用 [nvm-windows](https://github.com/coreybutler/nvm-windows)：

1. 从 https://github.com/coreybutler/nvm-windows/releases 下载安装包
2. 运行安装程序
3. 重启终端

### 使用 nvm

```bash
# 查看可安装的 LTS 版本
nvm ls-remote --lts

# 安装指定版本
nvm install 22     # 安装最新 22.x
nvm install 20     # 安装最新 20.x
nvm install --lts  # 安装最新 LTS

# 切换版本
nvm use 22
nvm use 20

# 设置默认版本
nvm alias default 22

# 查看已安装版本
nvm ls

# 在项目中固定版本（创建 .nvmrc 文件）
echo "22" > .nvmrc
nvm use   # 自动读取 .nvmrc
```

### 使用 fnm（社区替代品，Rust 实现）

[fnm](https://github.com/Schniz/fnm) 是用 Rust 编写的 Node.js 版本管理器，比 nvm 快得多：

```bash
# 安装 fnm
# macOS:
brew install fnm
# Linux:
curl -fsSL https://fnm.vercel.app/install | bash
# Windows:
winget install Schniz.fnm

# 添加到 shell（zsh）
echo 'eval "$(fnm env --use-on-cd --shell zsh)"' >> ~/.zshrc

# 添加到 shell（bash）
echo 'eval "$(fnm env --use-on-cd --shell bash)"' >> ~/.bashrc

# 使用方式与 nvm 类似
fnm install 22
fnm use 22
fnm default 22
fnm ls
```

---

## npm 全局包管理

```bash
# 查看全局安装的包
npm ls -g --depth=0

# 安装全局包
npm install -g pptxgenjs
npm install -g docx

# 查看全局包安装位置
npm root -g

# 如果全局安装报权限错误（Linux/macOS），不要用 sudo
# 而是更改 npm 全局目录：
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc  # 或 ~/.bashrc
source ~/.zshrc
```

---

## 常见问题排查

### "python: command not found" 或 "python3: command not found"

**原因**：Python 未安装或未添加到 PATH。

**排查步骤**：

```bash
# 1. 检查是否安装了 Python
which python3 2>/dev/null || which python 2>/dev/null
ls /usr/bin/python* /usr/local/bin/python* /opt/homebrew/bin/python* 2>/dev/null

# 2. 检查 PATH
echo "$PATH" | tr ':' '\n' | head -20

# 3. macOS：检查 Homebrew Python
brew list python 2>/dev/null && echo "Homebrew Python installed"

# 4. 如果已安装但找不到，添加到 PATH
# macOS (Apple Silicon):
export PATH="/opt/homebrew/bin:$PATH"
# macOS (Intel):
export PATH="/usr/local/bin:$PATH"
```

**解决方案**：按照上方"Python 安装"章节安装，或修复 PATH 配置。

### "pip: command not found"

**原因**：pip 未安装，或 Python 是系统自带的精简版。

```bash
# 尝试使用 python -m pip
python3 -m pip --version

# 如果也失败，手动安装 pip
curl -fsSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user
rm get-pip.py

# 确保 ~/.local/bin 在 PATH 中
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc  # 或 ~/.bashrc
source ~/.zshrc
```

### "externally-managed-environment" 错误（PEP 668）

**现象**：`pip install` 报错 "This environment is externally managed"。

**原因**：Debian 12+、Ubuntu 23.04+、Fedora 38+ 等新版发行版限制全局 pip 安装以保护系统 Python。

**解决方案（推荐优先级从高到低）**：

```bash
# 方案 1（推荐）：使用虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install package-name

# 方案 2：使用 pipx 安装 CLI 工具
pipx install package-name

# 方案 3：使用 --user 标志安装到用户目录
pip install --user package-name

# 方案 4（不推荐）：强制覆盖（可能破坏系统）
pip install --break-system-packages package-name
```

### "node: command not found"

**排查步骤**：

```bash
# 检查是否安装
which node 2>/dev/null
ls /usr/bin/node /usr/local/bin/node 2>/dev/null

# 检查 nvm 是否已安装但未加载
[ -s "$HOME/.nvm/nvm.sh" ] && echo "nvm installed but not loaded"

# 加载 nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
node --version
```

### npm 全局安装权限错误（EACCES）

**现象**：`npm install -g` 报 "EACCES: permission denied"。

**解决方案**（**不要使用 sudo npm**）：

```bash
# 更改 npm 全局安装目录到用户目录
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'

# 添加到 PATH
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc  # 或 ~/.bashrc
source ~/.zshrc

# 现在可以正常全局安装
npm install -g pptxgenjs
```

### SSL/TLS 证书错误

**现象**：pip 或 npm 报 SSL 证书验证失败。

```bash
# pip：升级 certifi
pip install --upgrade certifi

# 临时绕过（仅限调试，不要用于生产）
pip install --trusted-host pypi.org --trusted-host pypi.python.org package-name

# npm：检查代理设置
npm config get proxy
npm config get https-proxy
npm config delete proxy
npm config delete https-proxy
```

### Python 包安装后 import 失败

**常见原因和排查**：

```bash
# 1. 检查是否安装在正确的 Python 版本下
python3 -c "import sys; print(sys.executable)"
pip3 show package-name

# 2. 检查是否在虚拟环境中
echo "$VIRTUAL_ENV"

# 3. 检查包名与 import 名不一致
# 安装名 → import 名（常见差异）：
# Pillow → PIL
# python-dateutil → dateutil
# beautifulsoup4 → bs4
# scikit-learn → sklearn
# markitdown → markitdown
# pypdf → pypdf

# 4. 重新安装
pip install --force-reinstall package-name
```

### macOS "xcrun: error" 或编译失败

**现象**：安装需要 C 扩展的包（如 lxml、numpy）时编译失败。

```bash
# 安装 Xcode Command Line Tools
xcode-select --install

# 如果已安装但仍报错，重置
sudo xcode-select --reset

# 对于特定包，安装系统依赖
# lxml:
brew install libxml2 libxslt
# Pillow:
brew install libjpeg zlib
```

### Windows PowerShell 执行策略阻止脚本

**现象**：无法激活虚拟环境或运行 npm 脚本。

```powershell
# 查看当前策略
Get-ExecutionPolicy

# 设置为 RemoteSigned（推荐）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 代理环境下的配置

```bash
# pip 代理配置
pip install --proxy http://proxy:port package-name
# 或永久配置
pip config set global.proxy http://proxy:port

# npm 代理配置
npm config set proxy http://proxy:port
npm config set https-proxy http://proxy:port

# Git 代理（部分安装脚本需要 Git）
git config --global http.proxy http://proxy:port
git config --global https.proxy http://proxy:port
```

---

## 办公技能依赖速查

以下是 DesireCore 办公四件套技能所需的依赖汇总：

### DOCX（Word 文档处理）

```bash
# Python 包
pip install lxml defusedxml

# Node.js 包
npm install -g docx

# 系统工具
# pandoc — 文本提取
# LibreOffice — PDF 转换
```

### PDF（PDF 文档处理）

```bash
# Python 核心包
pip install pypdf pdfplumber Pillow

# Python 可选包
pip install reportlab    # PDF 创建
pip install pdf2image    # PDF 转图片（需要 poppler）
pip install pytesseract  # OCR（需要 tesseract）

# 系统工具
# poppler-utils — pdftotext, pdftoppm, pdfimages
# qpdf — 合并、拆分、解密
# tesseract — OCR 引擎
```

### XLSX（电子表格处理）

```bash
# Python 包
pip install openpyxl pandas

# 系统工具
# LibreOffice — 公式重算
```

### PPTX（演示文稿处理）

```bash
# Python 包
pip install "markitdown[pptx]" Pillow

# Node.js 包
npm install -g pptxgenjs

# 系统工具
# LibreOffice — PDF 转换
# poppler-utils — PDF 转图片
```

### 一键安装所有办公技能依赖

```bash
# Python 包（全部）
pip install lxml defusedxml pypdf pdfplumber Pillow reportlab openpyxl pandas "markitdown[pptx]"

# Node.js 包（全部）
npm install -g docx pptxgenjs
```

---

## 系统工具安装

### LibreOffice

办公技能用于文档格式转换和公式重算。

```bash
# macOS
brew install --cask libreoffice

# Ubuntu/Debian
sudo apt install libreoffice

# Fedora/RHEL
sudo dnf install libreoffice

# Windows
winget install TheDocumentFoundation.LibreOffice
```

### Poppler（PDF 工具集）

提供 `pdftotext`、`pdftoppm`、`pdfimages` 等命令。

```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt install poppler-utils

# Fedora/RHEL
sudo dnf install poppler-utils

# Windows（通过 conda 或手动下载）
conda install -c conda-forge poppler
```

### Pandoc（文档格式转换）

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt install pandoc

# Fedora/RHEL
sudo dnf install pandoc

# Windows
winget install JohnMacFarlane.Pandoc
```

### Tesseract（OCR 引擎）

```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt install tesseract-ocr

# Fedora/RHEL
sudo dnf install tesseract

# 安装中文语言包
# macOS:
brew install tesseract-lang
# Ubuntu/Debian:
sudo apt install tesseract-ocr-chi-sim tesseract-ocr-chi-tra
```

---

## 环境验证脚本

一键检查所有办公技能所需的环境是否就绪：

```bash
echo "=== Python ==="
python3 --version 2>/dev/null || echo "MISSING: python3"

echo "=== pip ==="
pip3 --version 2>/dev/null || echo "MISSING: pip3"

echo "=== Node.js ==="
node --version 2>/dev/null || echo "MISSING: node"

echo "=== npm ==="
npm --version 2>/dev/null || echo "MISSING: npm"

echo "=== Python Packages ==="
python3 -c "
packages = {
    'lxml': 'lxml',
    'defusedxml': 'defusedxml',
    'pypdf': 'pypdf',
    'pdfplumber': 'pdfplumber',
    'PIL': 'Pillow',
    'openpyxl': 'openpyxl',
    'pandas': 'pandas',
    'markitdown': 'markitdown',
    'reportlab': 'reportlab',
}
for mod, pkg in packages.items():
    try:
        __import__(mod)
        print(f'  OK: {pkg}')
    except ImportError:
        print(f'  MISSING: {pkg}')
" 2>/dev/null || echo "Cannot check packages (Python not available)"

echo "=== Node.js Global Packages ==="
for pkg in docx pptxgenjs; do
    node -e "require('$pkg')" 2>/dev/null && echo "  OK: $pkg" || echo "  MISSING: $pkg"
done

echo "=== System Tools ==="
for cmd in soffice pandoc pdftoppm pdftotext qpdf tesseract; do
    command -v "$cmd" >/dev/null 2>&1 && echo "  OK: $cmd" || echo "  MISSING: $cmd"
done
```

将上述脚本保存为 `check-env.sh`，运行 `bash check-env.sh` 即可查看完整的环境状态。
