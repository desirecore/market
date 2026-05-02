# nvm / fnm（L4 社区方案）

仅在以下情况启用：
1. 用户明确要求 nvm / fnm
2. 项目根目录已有 `.nvmrc` 文件且不存在 `package.json#volta`
3. L1 (HTTP API) / L2 (Volta CLI) / L3 (系统包管理器) 全部失败

如条件不满足，**不要**主动建议 nvm——优先 DesireCore Volta。

## nvm（POSIX shell）

### 安装

```bash
# macOS / Linux
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

source ~/.zshrc   # 或 ~/.bashrc

# 验证
command -v nvm    # 应返回 "nvm"（函数）
```

`install.sh` 会自动追加加载片段到 `~/.zshrc` / `~/.bashrc`：
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
```

### 使用

```bash
# 列出可装 LTS
nvm ls-remote --lts

# 安装
nvm install 22       # 最新 22.x
nvm install --lts    # 最新 LTS
nvm install 20.10.0  # 精确版本

# 切换
nvm use 22
nvm use --lts

# 默认
nvm alias default 22

# 项目级（.nvmrc）
echo "22" > .nvmrc
nvm use   # 读取 .nvmrc

# 已装
nvm ls

# 卸载
nvm uninstall 18
```

### Windows（nvm-windows，独立项目）

```
https://github.com/coreybutler/nvm-windows/releases
```

下载安装包安装，重启终端。命令略有差异（无 `.nvmrc` 支持，需用 `nvm-windows-bridge` 之类的扩展）。

## fnm（Rust 实现，比 nvm 快）

### 安装

```bash
# macOS
brew install fnm

# Linux
curl -fsSL https://fnm.vercel.app/install | bash

# Windows
winget install Schniz.fnm
```

### 配置自动切换

```bash
# zsh
echo 'eval "$(fnm env --use-on-cd --shell zsh)"' >> ~/.zshrc

# bash
echo 'eval "$(fnm env --use-on-cd --shell bash)"' >> ~/.bashrc

# fish
fnm env --use-on-cd --shell fish | source
```

`--use-on-cd` 让 `cd` 进入有 `.nvmrc` 的目录时自动切换。

### 使用

```bash
fnm install 22
fnm install --lts
fnm use 22
fnm default 22
fnm ls
fnm uninstall 18
```

## .nvmrc / .node-version 约定

| 文件 | 工具支持 |
|------|----------|
| `.nvmrc` | nvm、fnm（默认） |
| `.node-version` | fnm（默认）、nodenv |
| `package.json#engines.node` | npm 安装时校验，不切换 |
| `package.json#volta` | Volta（自动切换） |

存在 `package.json#volta` 时**优先尊重**它，不要让用户改用 nvm。

## 镜像加速

```bash
# nvm
export NVM_NODEJS_ORG_MIRROR=https://npmmirror.com/mirrors/node/

# fnm
fnm install --node-dist-mirror https://npmmirror.com/mirrors/node/ 22
# 或全局
export FNM_NODE_DIST_MIRROR=https://npmmirror.com/mirrors/node/
```

## 故障排查

| 现象 | 排查 |
|------|------|
| `nvm: command not found` | shell 未 source nvm.sh，重启终端或 `source ~/.zshrc` |
| `nvm` 在脚本里失效 | nvm 是 shell function 不是命令；脚本里需先 `source ~/.nvm/nvm.sh` |
| `node: command not found`（nvm 已装） | 切换了 shell 但 nvm 没在新 shell 加载，添加加载片段 |
| nvm 编译 Node 时网络超时 | 设镜像 `NVM_NODEJS_ORG_MIRROR` |
| Windows nvm 切换无效 | 以管理员重新运行 nvm 安装包 |
