<!-- locale: zh-CN -->

# nodejs-runtime 技能

## L0：一句话摘要

**何时使用**：用户需要 安装 Node.js / 升级 Node / 切换 Node 多版本 / 安装或配置
npm / pnpm / yarn / 排查 `node: command not found`、`npm: command not found`、
EACCES 全局安装权限错误、node-gyp 编译失败、registry 镜像 / proxy 问题 等
Node.js 运行时问题，或其他 skill（pptx 用 pptxgenjs 等）报告 "Node.js 不可用" 时。

**怎么做**：优先使用 DesireCore 内置 Volta，按四级降级（HTTP API → Volta CLI →
系统包管理器 brew/apt/NodeSource/winget → 社区方案 nvm/fnm）执行。

## L1：概述与使用场景

### 能力描述

procedural skill。每次执行 Node.js 环境操作前，先运行 `scripts/probe-node.sh` 取 JSON 快照，再按 `../dev-environment-setup/references/decision-tree.md` 四级降级选择路径。

### 使用场景

- "node not found" / "npm not found"
- 用户要求安装/升级 Node.js
- 多版本切换（基于 `package.json#volta` 或 `.nvmrc`）
- 安装/管理 pnpm / yarn / npm
- "EACCES: permission denied"（npm 全局安装权限错误）
- 配置 registry / proxy
- 其他 skill（pptx 等）报告 Node.js 不可用

### 核心价值

- **DesireCore 优先**：Volta + HTTP API 作为 L1/L2，避免污染系统 Node
- **JSON 决策**：probe 脚本输出结构化数据，Claude 可直接解析
- **package.json#volta 兼容**：Volta 自动按项目切换版本

## L2：详细规范

### 第一步：环境探测（必须）

```bash
bash skills/nodejs-runtime/scripts/probe-node.sh > /tmp/node-probe.json
cat /tmp/node-probe.json | jq .
```

字段含义见 `../dev-environment-setup/references/probe-snapshot.md`。

### 第二步：选择执行路径

| 条件 | 路径 |
|------|------|
| `desirecore_api` 非空 | **L1** HTTP API |
| `desirecore_api` 空，`volta_path` 非空 | **L2** Volta CLI |
| 上述都不满足 | **L3** 系统包管理器（brew / apt / NodeSource / winget） |
| L1–L3 全部失败或用户明示 | **L4** 社区方案（nvm / fnm） |

### 第三步：执行（仅展示主路径，详见各 references）

#### L1：HTTP API（→ `references/volta-desirecore.md`）

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
BASE="https://127.0.0.1:${PORT}/api/runtime"

# 列出可装版本
curl -sk "${BASE}/node/available"

# 触发安装（异步）
curl -sk -X POST "${BASE}/node/install" \
  -H "Content-Type: application/json" \
  -d '{"version":"22"}'

# 安装包管理器
curl -sk -X POST "${BASE}/pkg/pnpm/install" \
  -H "Content-Type: application/json" \
  -d '{"version":"latest"}'

# 完成后刷新缓存
curl -sk -X POST "${BASE}/environment/refresh"
```

#### L2：Volta CLI 绝对路径（→ `references/volta-desirecore.md`）

```bash
VOLTA=${DESIRECORE_ROOT}/runtime/volta/volta
export VOLTA_HOME=${DESIRECORE_ROOT}/runtime/volta
export VOLTA_FEATURE_PNPM=1

"$VOLTA" install node@22
"$VOLTA" install pnpm@latest
"$VOLTA" install yarn@latest
"$VOLTA" list all

# 项目级固定（修改 package.json#volta）
"$VOLTA" pin node@22 pnpm@9
```

Windows：`%USERPROFILE%\.desirecore\runtime\volta\volta.exe`。

#### L3：系统包管理器

| 平台 | 命令 |
|------|------|
| macOS | `brew install node` |
| Debian/Ubuntu | NodeSource：`curl -fsSL https://deb.nodesource.com/setup_22.x \| sudo -E bash - && sudo apt install nodejs` |
| Fedora/RHEL | `curl -fsSL https://rpm.nodesource.com/setup_22.x \| sudo bash - && sudo dnf install nodejs` |
| Arch | `sudo pacman -S nodejs npm` |
| Windows | `winget install OpenJS.NodeJS.LTS` |

#### L4：nvm / fnm（→ `references/nvm-fallback.md`）

仅在用户明示或上述失败时启用。

### 第四步：包管理器策略

详见 `references/package-managers.md`：
- pnpm（推荐，磁盘高效、严格依赖）
- yarn（Berry / Classic）
- npm（默认，Node.js 自带）
- 项目级 `package.json#volta` 自动切换

### 第五步：故障排查

详见 `references/troubleshooting.md`：
- npm EACCES 权限错误（**不要用 sudo npm**）
- registry / proxy 配置
- node-gyp 编译失败
- "node: command not found" 在 nvm 已装时

## 重要约束

1. **绝不 `sudo npm install -g`**：用户级 prefix 或 Volta/nvm。
2. **修改环境后必须刷新**：L1 调 `POST /api/runtime/environment/refresh`；其它路径重跑 probe。
3. **跨 skill 协作**：`pptx` 等需要 Node.js 时，按本 skill 主路径安装；npm 包速查见 `../dev-environment-setup/references/office-deps.md`。
4. **package.json#volta 必须尊重**：检测到该字段时优先 Volta，不要切到 nvm。

## 引用关系

- 决策树：`../dev-environment-setup/references/decision-tree.md`
- DesireCore 底座：`../dev-environment-setup/references/desirecore-runtime.md`
- 探测协议：`../dev-environment-setup/references/probe-snapshot.md`
- 办公依赖（npm 包）：`../dev-environment-setup/references/office-deps.md`
