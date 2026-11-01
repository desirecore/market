# DesireCore 内置 Volta（L1 / L2 主路径）

DesireCore 内置 [Volta](https://volta.sh/) v2.0.2（Rust 实现的 Node.js 工具链管理器），**用户无需单独安装**。

| 内容 | 位置 |
|------|------|
| Volta Home（版本与工具数据） | `${VOLTA_HOME:-${DESIRECORE_ROOT}/runtime/volta-home}`：启动 DesireCore 前显式设置的 `VOLTA_HOME` 优先，否则是实例目录 |
| Volta 二进制（随包，默认） | 应用目录下的 `static/toolchains/<平台>-<架构>/volta/volta`（Windows 为 `volta.exe`）。应用目录在 macOS 是 `<App>.app/Contents`，其他平台是安装目录 |
| Volta 二进制（手动下载，存在时优先） | `${DESIRECORE_ROOT}/runtime/volta/volta`，只有随包二进制不可用、经 `POST /volta/install` 下载后才存在 |
| 内置 Node | `<Volta Home>/tools/image/node/<version>/bin/`（Windows 没有 `bin` 这一层） |

## 直接使用内置 Node（通常不需要安装）

DesireCore 把一个内置 Node 版本（推荐版本已安装就用它，否则取最高版本）的目录追加到服务进程 PATH 末尾，Bash 等工具都会继承，不改用户的 shell 配置。

- 系统没有 Node 时，直接运行 `node`、`npm`、`npx`。
- 系统已有 Node 时系统版本优先。要用内置版本，写绝对路径。版本清单见 `<env>` 块的 Managed runtimes 段，或列目录：

```bash
VOLTA_HOME="${VOLTA_HOME:-${DESIRECORE_ROOT}/runtime/volta-home}"
ls "$VOLTA_HOME/tools/image/node"

NODE_BIN="$VOLTA_HOME/tools/image/node/<version>/bin"
"$NODE_BIN/node" --version
PATH="$NODE_BIN:$PATH" npm --version      # npm 要从 PATH 找 node
```

> **不要使用 `<Volta Home>/bin`**。这里的 `node`、`npm` 等入口是 Volta shim，它按 `VOLTA_HOME` 选 Home。DesireCore 不导出这个变量，未导出时 shim 看的是 `~/.volta`（不存在还会新建），拿不到 DesireCore 的 Node：报 `Node is not available`，系统有 Node 时则透传到系统版本。这个目录放在 PATH 上还会卡住超过 30 秒。旧版升级的用户这里可能是断链，修好链接同样拿不到 DesireCore 的 Node，不需要修。

## L1：通过 HTTP API 操作（推荐，DesireCore 应用内）

### 探测 API 可用性

```bash
PORT_FILE="${DESIRECORE_ROOT}/agent-service.port"
[ -r "$PORT_FILE" ] || { echo "API 不可用，降级到 L2"; exit 1; }
PORT=$(cat "$PORT_FILE")
BASE="https://127.0.0.1:${PORT}/api/runtime"

curl -sk --max-time 0.5 "${BASE}/environment" >/dev/null \
  || { echo "API 超时，降级到 L2"; exit 1; }
```

### Volta 自身

```bash
curl -sk "${BASE}/volta/status"
curl -sk -X POST "${BASE}/volta/install"   # 随包 Volta 可用时直接返回成功，否则下载到 runtime/volta/
```

### Node.js 版本

```bash
# 已装版本
curl -sk "${BASE}/node/installed"

# 可装版本（远端 nodejs.org/dist 或 GitHub Releases）
curl -sk "${BASE}/node/available"
# ❗ 若返回 502，说明远端 / 镜像不可达，立即降级到 L2

# 安装（异步，立即返回 taskId）
curl -sk -X POST "${BASE}/node/install" \
  -H "Content-Type: application/json" \
  -d '{"version":"22"}'

# 移除
curl -sk -X POST "${BASE}/node/remove" \
  -H "Content-Type: application/json" \
  -d '{"version":"20.10.0"}'
```

### 包管理器（pnpm / yarn / npm）

```bash
TOOL="pnpm"   # 或 yarn / npm

curl -sk "${BASE}/pkg/${TOOL}/installed"
curl -sk "${BASE}/pkg/${TOOL}/available"

# 必须是完整版本号，latest、9 这类写法返回 400
curl -sk -X POST "${BASE}/pkg/${TOOL}/install" \
  -H "Content-Type: application/json" \
  -d '{"version":"9.15.9"}'

curl -sk -X POST "${BASE}/pkg/${TOOL}/remove" \
  -H "Content-Type: application/json" \
  -d '{"version":"9.0.0"}'
```

### 实时输出 / 缓存刷新

异步任务：监听 Socket.IO 事件 `runtime:terminal` / `runtime:complete`，按 taskId 过滤。没有 Socket.IO 客户端时，轮询 `GET ${BASE}/node/installed`（包管理器为 `GET ${BASE}/pkg/${TOOL}/installed`）直到出现目标版本。下载失败时轮询不会收到信号，所以要设上限；超时后看 `<Volta Home>/log/` 里最新的 `volta-error-*.log`。

```bash
curl -sk -X POST "${BASE}/environment/refresh"   # 安装结束后刷新
```

## L2：直接调用 Volta CLI 绝对路径

### macOS / Linux

```bash
# 二进制路径取自探测结果，为空时见下方「找不到 Volta 二进制」
VOLTA=$(bash skills/nodejs-runtime/scripts/probe-node.sh | jq -r .volta_path)

# 每次调用都要设置：DesireCore 只在自己调用 Volta 时设置它们，不传给 Bash
export VOLTA_HOME="${VOLTA_HOME:-${DESIRECORE_ROOT}/runtime/volta-home}"
export VOLTA_FEATURE_PNPM=1

# 下载到 Volta Home（与 DesireCore 自身的做法相同，不改默认版本）
"$VOLTA" fetch node@22                # 最新 22.x
"$VOLTA" fetch node@20.11.0           # 精确版本
"$VOLTA" fetch pnpm@latest
"$VOLTA" fetch yarn@latest
"$VOLTA" fetch npm@10

# 列表
"$VOLTA" list all
"$VOLTA" list node

# 项目级固定（写入 package.json#volta）
"$VOLTA" pin node@22 pnpm@9

# 运行：项目固定了版本时直接 run，否则显式传版本
"$VOLTA" run node --version
"$VOLTA" run --node 22 node --version
"$VOLTA" run --node 22 --pnpm 9 pnpm --version
```

`volta pin` 后 `package.json` 中会自动追加：
```json
"volta": {
  "node": "22.11.0",
  "pnpm": "9.5.0"
}
```

项目没有固定版本时，`"$VOLTA" run node` 报 `Node is not available`（提示 `first set a default version`），需要显式传 `--node`，或用 `"$VOLTA" install node@22` 把它设为这个 Home 的默认版本。

### 找不到 Volta 二进制

`probe-node.sh` 依次查找 `${DESIRECORE_ROOT}/runtime/volta/volta`、`$DESIRECORE_STATIC_DIR` 下的工具链、`<Volta Home>/bin/node` 的链接目标所在目录，以及默认安装位置（`/Applications/*.app/Contents/static`、`/opt/*/static`）。应用装在别处时 `volta_path` 为空（AppImage 每次启动的挂载路径都不同），这时走 L1，或按本文开头的表格到应用目录下找。

### Windows PowerShell

```powershell
# 手动下载过 Volta 时改用 "$env:DESIRECORE_ROOT\runtime\volta\volta.exe"
$Volta = "<安装目录>\static\toolchains\win32-x64\volta\volta.exe"   # ARM 为 win32-arm64
if (-not $env:VOLTA_HOME) { $env:VOLTA_HOME = "$env:DESIRECORE_ROOT\runtime\volta-home" }
$env:VOLTA_FEATURE_PNPM = "1"

& $Volta fetch node@22
& $Volta fetch pnpm@latest
& $Volta list all
```

### 移除

Volta 不支持 `volta uninstall node`，优先用 HTTP API，它会同时清理已下载的归档：

```bash
curl -sk -X POST "${BASE}/node/remove" -H "Content-Type: application/json" -d '{"version":"22.11.0"}'
```

或直接删目录：
```bash
rm -rf "${VOLTA_HOME:-${DESIRECORE_ROOT}/runtime/volta-home}/tools/image/node/<version>"
```

## 可视化管理

DesireCore 应用 → 资源管理器 → 计算资源 → **运行环境** Tab，GUI 安装/删除 Node.js 与包管理器。

## 按项目切换版本

`package.json` 中有 `volta` 字段时，`"$VOLTA" run <命令>` 按固定的版本运行，无需 `volta use`，也无需 `.nvmrc`。

`cd` 进目录自动切换要求 Volta shim 在 PATH 最前且已导出 `VOLTA_HOME`。DesireCore 的 PATH 上是固定的内置 Node，不是 shim，所以在这里只 `cd` 不会切换版本。

## Volta vs nvm

| 维度 | Volta（DesireCore 内置） | nvm（社区） |
|------|--------------------------|-------------|
| 安装方式 | 随 DesireCore 内置 | 用户手动 |
| 版本切换 | `volta run` 按 package.json 选择 | 手动 `nvm use` 或 `.nvmrc` |
| 包管理器 | 支持（pnpm/yarn/npm 都可固定版本） | 不支持 |
| Windows 原生 | ✅ | 需 nvm-windows（功能受限） |
| 速度 | 极快（Rust 实现） | 较慢（shell 脚本） |
| 系统 PATH | 不污染 | 修改 PATH |
| GUI | DesireCore 运行环境 Tab | 无 |
| 自定义下载源 | Volta Home 下的 `hooks.json` | 无内建支持 |

**结论**：DesireCore 应用内、有 Volta 时永远首选 Volta；外部脚本可考虑 nvm/fnm。

## 故障排查（Volta 专属）

| 现象 | 排查 |
|------|------|
| `volta: not found` | Volta 不在 PATH 上是正常的，用绝对路径调用，见「找不到 Volta 二进制」 |
| `Node is not available` | 调到了 `<Volta Home>/bin` 下的 shim，或 Volta 没带 `VOLTA_HOME`：改用 `tools/image/node/<version>/bin`，或同时设置 `VOLTA_HOME` 和 `VOLTA_FEATURE_PNPM`。`volta run` 在项目没有固定版本时也报这个错：传 `--node` |
| `node` 卡住超过 30 秒 | `<Volta Home>/bin` 在 PATH 上且未导出 `VOLTA_HOME`。把它从 PATH 去掉，需要时改加 `tools/image/node/<version>/bin` |
| `Could not download ...` | 网络或下载源问题，可以重试。Volta 2.0.2 没有镜像环境变量，自定义下载源用 `hooks.json`，否则降级到 L3 |
| pnpm 相关报错 | 检查 `VOLTA_FEATURE_PNPM=1` 是否设置 |
| Windows Defender 隔离 volta.exe | 信任应用安装目录下的 `static\toolchains\` |
| `cd` 进项目后版本未切换 | DesireCore 里符合预期，用 `"$VOLTA" run` 按 `package.json#volta` 运行 |
