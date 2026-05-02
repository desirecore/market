# pyenv（L4 社区方案）

仅在以下情况启用：
1. 用户明确要求 pyenv（"用 pyenv 装"）
2. 项目根目录已有 `.python-version` 文件
3. L1 (HTTP API) / L2 (Hatch CLI) / L3 (系统包管理器) 全部失败

如条件不满足，**不要**主动建议 pyenv——优先 DesireCore Hatch。

## 安装 pyenv

### macOS / Linux

```bash
curl https://pyenv.run | bash

# zsh
cat >> ~/.zshrc <<'EOF'
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
EOF

# bash
cat >> ~/.bashrc <<'EOF'
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
EOF

exec "$SHELL"
```

#### 编译依赖

| 平台 | 命令 |
|------|------|
| macOS | `brew install openssl readline sqlite3 xz zlib tcl-tk` |
| Ubuntu/Debian | `sudo apt install build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev` |
| Fedora/RHEL | `sudo dnf install gcc make zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel` |

### Windows（pyenv-win）

```powershell
pip install pyenv-win --target "$HOME\.pyenv"
# 或
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; & "./install-pyenv-win.ps1"
```

环境变量：
```powershell
[System.Environment]::SetEnvironmentVariable('PYENV', "$HOME\.pyenv\pyenv-win", 'User')
[System.Environment]::SetEnvironmentVariable('PYENV_HOME', "$HOME\.pyenv\pyenv-win", 'User')
# 然后把 %PYENV%\bin 和 %PYENV%\shims 加入 PATH
```

## 使用 pyenv

```bash
# 列出可装版本
pyenv install --list | grep "^  3\."

# 安装
pyenv install 3.12.4
pyenv install 3.11.9

# 全局默认
pyenv global 3.12.4

# 项目级（生成 .python-version）
pyenv local 3.11.9

# 已装版本
pyenv versions

# 当前激活
pyenv version

# 卸载
pyenv uninstall 3.10.14
```

## 镜像加速

```bash
export PYTHON_BUILD_MIRROR_URL="https://npmmirror.com/mirrors/python/"
pyenv install 3.12.4
```

## pyenv 常见问题

| 现象 | 排查 |
|------|------|
| `pyenv: command not found` | shell 配置未加载，`exec "$SHELL"` 或重启终端 |
| 编译时 `ModuleNotFoundError: _ssl` | 缺 `libssl-dev` / `openssl`，按上方编译依赖安装 |
| macOS Big Sur 编译失败 | `LDFLAGS="-L$(brew --prefix openssl)/lib" CPPFLAGS="-I$(brew --prefix openssl)/include" pyenv install 3.12.4` |
| Windows pyenv 切换无效 | 检查 PATH 中 `%PYENV%\shims` 是否在系统 Python 之前 |
