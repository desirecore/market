# Python 故障排查

## "python: command not found" / "python3: command not found"

**原因**：未安装或未加入 PATH。

```bash
# 1. 找一下二进制
which python3 2>/dev/null; which python 2>/dev/null
ls /usr/bin/python* /usr/local/bin/python* /opt/homebrew/bin/python* 2>/dev/null

# 2. 查 PATH
echo "$PATH" | tr ':' '\n' | head -20

# 3. macOS：检查 Homebrew Python
brew list python 2>/dev/null && echo "Homebrew Python installed"

# 4. 修复 PATH
# Apple Silicon
export PATH="/opt/homebrew/bin:$PATH"
# Intel mac / Linux 常见
export PATH="/usr/local/bin:$PATH"
```

**根治**：按主 SKILL.md 决策树重新执行 L1–L3 安装路径。

## "pip: command not found"

```bash
# 用 module 模式调用
python3 -m pip --version

# 仍失败：手动 bootstrap
curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py --user
rm /tmp/get-pip.py

# 把 ~/.local/bin 加入 PATH（zsh / bash）
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## "externally-managed-environment"（PEP 668）

**触发系统**：Debian 12+、Ubuntu 23.04+、Fedora 38+、Arch（部分）。

**优先级从高到低**：

```bash
# 方案 1（推荐）：虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install package-name

# 方案 2：pipx 装 CLI 工具
pipx install package-name

# 方案 3：用户目录
pip install --user package-name

# 方案 4（不推荐，可能破坏系统）
pip install --break-system-packages package-name
```

## SSL / TLS 证书错误

```bash
# pip：升级 certifi
pip install --upgrade certifi

# 临时绕过（仅调试）
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org package-name

# 永久信任（不推荐）
pip config set global.trusted-host "pypi.org files.pythonhosted.org"
```

macOS 系统时间偏差也会导致 SSL 失败：`sudo sntp -sS time.apple.com`。

## import 失败

包名 ≠ import 名是最常见原因：

| 安装名 (pip install) | import 名 |
|----------------------|-----------|
| Pillow | PIL |
| python-dateutil | dateutil |
| beautifulsoup4 | bs4 |
| scikit-learn | sklearn |
| PyYAML | yaml |
| pytorch | torch |

```bash
# 1. 确认安装到了正确的 Python
python3 -c "import sys; print(sys.executable)"
pip3 show package-name

# 2. 是否在虚拟环境
echo "$VIRTUAL_ENV"

# 3. 强制重装
pip install --force-reinstall --no-cache-dir package-name
```

## macOS "xcrun: error" / 编译失败

安装 lxml / numpy / Pillow 等需要 C 扩展的包时：

```bash
# 安装 / 重置 Xcode CLI
xcode-select --install
sudo xcode-select --reset

# 包级依赖
brew install libxml2 libxslt    # lxml
brew install libjpeg zlib       # Pillow
brew install openssl readline   # cryptography 类
```

## Windows PowerShell 执行策略

```powershell
Get-ExecutionPolicy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

之后才能 `.\.venv\Scripts\Activate.ps1`。

## Windows Store 占位符

`python --version` 弹出 Store 页面：

1. 设置 → 应用 → 高级应用设置 → 应用执行别名
2. 关闭 `python.exe` / `python3.exe` 的 Store 别名
3. 重启终端

## 代理环境配置

```bash
# pip
pip install --proxy http://proxy:port package-name
pip config set global.proxy http://proxy:port

# 取消
pip config unset global.proxy

# 系统级（zsh / bash）
export http_proxy=http://proxy:port
export https_proxy=http://proxy:port
```

## EnvironmentSnapshot 信号速查

probe-python.sh 输出后，按字段快速判断：

| 字段 | 期望 | 失败原因 |
|------|------|----------|
| `system_python.version` | 非空且 ≥ 3.8 | 未装 Python 或版本太低 |
| `system_pip.version` | 非空 | pip 未装（macOS Apple 自带 Python 没有 pip） |
| `hatch_path` | 非空 | DesireCore Hatch 未释放，调 `POST /api/runtime/hatch/install` |
| `pep668: true` | — | 系统 Python 受保护，必须 venv/pipx |
| `active_venv` | 操作前为空，激活后非空 | venv 未生效，重新 `source .venv/bin/activate` |

## 重置整个 Python 环境（最后手段）

```bash
# 1. 退出所有虚拟环境
deactivate 2>/dev/null
conda deactivate 2>/dev/null

# 2. 删除可疑虚拟环境
rm -rf .venv venv

# 3. 重新探测
bash skills/python-runtime/scripts/probe-python.sh

# 4. 按主 SKILL.md 决策树重新安装
```
