# DesireCore 内置 Volta（L1 / L2 主路径）

DesireCore 内置 [Volta](https://volta.sh/) v2.0.2（Rust 实现的 Node.js 工具链管理器）。Volta 二进制随应用打包于 `static/volta/`，运行时位于 `${DESIRECORE_ROOT}/runtime/volta/`，**用户无需单独安装**。

> 与系统 Node.js 完全隔离：Volta 安装的工具位于 `${DESIRECORE_ROOT}/runtime/volta/tools/image/`，不修改系统 PATH。

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
curl -sk -X POST "${BASE}/volta/install"   # 自动下载到 runtime/
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

curl -sk -X POST "${BASE}/pkg/${TOOL}/install" \
  -H "Content-Type: application/json" \
  -d '{"version":"latest"}'

curl -sk -X POST "${BASE}/pkg/${TOOL}/remove" \
  -H "Content-Type: application/json" \
  -d '{"version":"9.0.0"}'
```

### 实时输出 / 缓存刷新

异步任务：监听 Socket.IO 事件 `runtime:terminal` / `runtime:complete`，按 taskId 过滤。

```bash
curl -sk -X POST "${BASE}/environment/refresh"   # 安装结束后刷新
```

## L2：直接调用 Volta CLI 绝对路径

### macOS / Linux

```bash
VOLTA=${DESIRECORE_ROOT}/runtime/volta/volta
export VOLTA_HOME=${DESIRECORE_ROOT}/runtime/volta
export VOLTA_FEATURE_PNPM=1
# export VOLTA_NODE_MIRROR=https://npmmirror.com/mirrors/node   # 中国大陆加速

# 安装
"$VOLTA" install node@22                # 最新 22.x
"$VOLTA" install node@20.11.0           # 精确版本
"$VOLTA" install pnpm@latest
"$VOLTA" install yarn@latest
"$VOLTA" install npm@10

# 列表
"$VOLTA" list all
"$VOLTA" list node

# 项目级固定（写入 package.json#volta）
"$VOLTA" pin node@22 pnpm@9
```

`volta pin` 后 `package.json` 中会自动追加：
```json
"volta": {
  "node": "22.11.0",
  "pnpm": "9.5.0"
}
```

后续 `cd` 进项目目录时 Volta 自动激活对应版本。

### Windows PowerShell

```powershell
$Volta = "$env:USERPROFILE\.desirecore\runtime\volta\volta.exe"
$env:VOLTA_HOME = "$env:USERPROFILE\.desirecore\runtime\volta"
$env:VOLTA_FEATURE_PNPM = "1"

& $Volta install node@22
& $Volta install pnpm@latest
& $Volta list all
```

### 移除

Volta 没有 `volta uninstall node`，直接删目录或用 HTTP API：

```bash
rm -rf ${DESIRECORE_ROOT}/runtime/volta/tools/image/node/<version>
```

或：
```bash
curl -sk -X POST "${BASE}/node/remove" -H "Content-Type: application/json" -d '{"version":"22.11.0"}'
```

## 可视化管理

DesireCore 应用 → 资源管理器 → 计算资源 → **运行环境** Tab，GUI 安装/删除 Node.js 与包管理器。

## 版本自动切换（核心优势）

只要 `package.json` 中有 `volta` 字段，Volta 会在 `cd` 进入目录时**自动激活**对应版本。无需手动 `volta use`，也无需 `.nvmrc`。

## Volta vs nvm

| 维度 | Volta（DesireCore 内置） | nvm（社区） |
|------|--------------------------|-------------|
| 安装方式 | 随 DesireCore 内置 | 用户手动 |
| 版本切换 | **自动**（基于 package.json） | 手动 `nvm use` 或 `.nvmrc` |
| 包管理器 | 支持（pnpm/yarn/npm 都可固定版本） | 不支持 |
| Windows 原生 | ✅ | 需 nvm-windows（功能受限） |
| 速度 | 极快（Rust 实现） | 较慢（shell 脚本） |
| 系统 PATH | 不污染 | 修改 PATH |
| GUI | DesireCore 运行环境 Tab | 无 |
| 镜像加速 | `VOLTA_NODE_MIRROR` | 无内建支持 |

**结论**：DesireCore 应用内、有 Volta 时永远首选 Volta；外部脚本可考虑 nvm/fnm。

## 故障排查（Volta 专属）

| 现象 | 排查 |
|------|------|
| `volta: not found` | 二进制未释放，调 `POST /api/runtime/volta/install` |
| `Volta error: Could not download node v22.x.x` | 网络或镜像问题，设 `VOLTA_NODE_MIRROR` |
| `volta install pnpm` 报错 | 检查 `VOLTA_FEATURE_PNPM=1` 是否设置 |
| Windows Defender 隔离 volta.exe | 信任 `~\.desirecore\runtime\volta\` 目录 |
| `cd` 进项目后版本未切换 | 确认 `package.json` 中 `volta` 字段且 PATH 中 Volta shim 在最前 |
