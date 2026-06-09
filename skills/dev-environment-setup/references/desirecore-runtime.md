# DesireCore 内置环境管理底座

DesireCore 内置了完整的开发环境管理基础设施。`python-runtime` 和 `nodejs-runtime` 两个 skill 共用本文档作为事实源。

## 一、内置工具二进制

### Hatch（Python 项目与版本管理器，v1.16.5）

| 平台 | 运行时绝对路径（用户安装版，优先） | 静态打包兜底 |
|------|----------------------------------|--------------|
| macOS / Linux | `${DESIRECORE_ROOT}/runtime/hatch/hatch` | 应用包内 `static/hatch/hatch` |
| Windows | `%USERPROFILE%\.desirecore\runtime\hatch\hatch.exe` | 应用包内 `static/hatch/hatch.exe` |

**Python 版本安装目录**：`${DESIRECORE_ROOT}/runtime/hatch/local/<版本>/python/bin/python3`（macOS/Linux），Windows 为 `python.exe`。

### Volta（Node.js 工具链管理器，v2.0.2）

| 平台 | 运行时绝对路径 | 静态打包兜底 |
|------|----------------|--------------|
| macOS / Linux | `${DESIRECORE_ROOT}/runtime/volta/volta` | 应用包内 `static/volta/volta` |
| Windows | `%USERPROFILE%\.desirecore\runtime\volta\volta.exe` | 应用包内 `static/volta/volta.exe` |

**Node.js 安装目录**：`${DESIRECORE_ROOT}/runtime/volta/tools/image/node/<version>/`，包管理器在 `tools/image/{packages,pnpm,yarn,npm}/`。

### 优先级规则

`runtime/` 目录优先于 `static/`。当用户更新过 Hatch/Volta 时，新版本写入 `runtime/`，DesireCore 优先调用之。

## 二、关键环境变量

| 变量 | 作用 | 默认/示例 |
|------|------|----------|
| `HATCH_HOME` | Hatch 工作目录 | `${DESIRECORE_ROOT}/runtime/hatch` |
| `HATCH_PYTHON_MIRROR_URL` | Python 下载镜像 | 加速节点（中国大陆） |
| `VOLTA_HOME` | Volta 工作目录 | `${DESIRECORE_ROOT}/runtime/volta` |
| `VOLTA_NODE_MIRROR` | Node.js 下载镜像 | `https://npmmirror.com/mirrors/node` |
| `VOLTA_FEATURE_PNPM` | 启用 pnpm 管理 | `1` |

DesireCore 在启动子进程时会自动注入这些变量；外部直接调用绝对路径 CLI 时需手动 export。

## 三、HTTP API 速查表

DesireCore agent-service 启动后将端口写入 `${DESIRECORE_ROOT}/agent-service.port`。全部接口走 **HTTPS + 自签名证书**（curl 需要 `-k`）。

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
BASE="https://127.0.0.1:${PORT}/api/runtime"
```

### 环境检测

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/environment` | 返回完整 `EnvironmentSnapshot`（platform/arch/tools/wsl） |
| POST | `/environment/refresh` | **重新加载登录环境变量**（重抓 `.zshrc` / 注册表并精确同步到 `process.env`）+ 清除进程级检测缓存并重新检测；返回 `EnvironmentSnapshot & { envDiff }`（详见第七节） |

### 工具链状态与安装

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/hatch/status` | 检查 Hatch 是否就绪（runtime/static 任一存在即可） |
| POST | `/hatch/install` | 下载并安装 Hatch 到 `runtime/hatch/`（同步返回成功/失败） |
| GET | `/volta/status` | 检查 Volta 是否就绪 |
| POST | `/volta/install` | 下载并安装 Volta 到 `runtime/volta/` |

### Python 版本管理

| 方法 | 路径 | 请求体 / 返回 |
|------|------|--------------|
| GET | `/python/installed` | 返回已安装版本列表（`["3.11", "3.12"]`） |
| GET | `/python/available` | 返回可安装版本（依赖 Hatch 元数据） |
| POST | `/python/install` | `{ "version": "3.12" }` → `{ "taskId": "uuid" }`，订阅 `runtime:terminal` 流 |
| POST | `/python/remove` | `{ "version": "3.11" }` → `{ "taskId": "uuid" }` |

### Node.js 版本管理

| 方法 | 路径 | 请求体 / 返回 |
|------|------|--------------|
| GET | `/node/installed` | 返回已安装版本 |
| GET | `/node/available` | 返回可安装版本（远端 nodejs.org/dist 或 GitHub Releases，2h 缓存）；网络失败返回 502 |
| POST | `/node/install` | `{ "version": "22" }` → `{ "taskId": "uuid" }` |
| POST | `/node/remove` | `{ "version": "22.11.0" }` → `{ "taskId": "uuid" }` |

### 包管理器（pnpm / yarn / npm）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/pkg/{tool}/installed` | tool ∈ {pnpm, yarn, npm} |
| GET | `/pkg/{tool}/available` | 失败返回 502 |
| POST | `/pkg/{tool}/install` | `{ "version": "9" }` → `{ "taskId": "uuid" }` |
| POST | `/pkg/{tool}/remove` | `{ "version": "9.0.0" }` → `{ "taskId": "uuid" }` |

## 四、Socket.IO 实时输出契约

耗时操作（`*/install`、`*/remove`）立即返回 `{ taskId }`，真正的执行延迟 100ms 启动，期间通过 Socket.IO 推送：

| 事件 | Payload | 触发时机 |
|------|---------|----------|
| `runtime:terminal` | `{ taskId, data }` | 每行 stdout/stderr 输出 + 操作开始/结束的状态行 |
| `runtime:complete` | `{ taskId, success }` | 任务结束（成功 / 失败 / 异常） |

**前端订阅时序**：先 HTTP POST 拿 taskId → 再连 Socket.IO 监听该 taskId → 服务端 100ms 后开工。Skill 在无 Socket.IO 客户端时不要走异步 HTTP API（无法收到日志），改用绝对路径 CLI 同步执行。

## 五、API 可用性探测

skill 必须先判定 API 是否可达，再决定走 HTTP 还是 CLI：

```bash
PORT_FILE="${DESIRECORE_ROOT}/agent-service.port"
if [ -r "$PORT_FILE" ]; then
  PORT=$(cat "$PORT_FILE")
  if curl -sk --max-time 0.5 "https://127.0.0.1:${PORT}/api/runtime/environment" >/dev/null 2>&1; then
    DESIRECORE_API="https://127.0.0.1:${PORT}"
  fi
fi
```

无 `agent-service.port` 文件、curl 超时（0.5s）、HTTP 非 2xx 一律视为不可达，立即降级到 CLI 路径。

## 六、EnvironmentSnapshot 数据结构

`GET /api/runtime/environment` 返回结构（详见 `lib/agent-service/environment-detection.ts`）：

```ts
type ToolDetection = {
  available: boolean
  command?: string   // 实际命令名（python3 / python）
  version?: string   // 提取后的版本号
  path?: string      // which/where 解析的绝对路径
}

type EnvironmentSnapshot = {
  platform: 'darwin' | 'win32' | 'linux'
  arch: string
  tools: {
    python: ToolDetection
    pip: ToolDetection
    node: ToolDetection
    npm: ToolDetection
    docker: ToolDetection
    podman: ToolDetection
    git: ToolDetection
  }
  wsl?: {
    installed: boolean
    version?: string
    defaultDistro?: string
  }
}
```

## 七、缓存失效 + 重新加载登录环境变量

`POST /api/runtime/environment/refresh` 按顺序做两件事：

1. **重新加载登录环境变量并精确同步到 `process.env`**：重新 fork 一个登录 shell（macOS/Linux：读最新 `.zshrc` / `.zprofile` / `.bashrc`）或重读 Windows 注册表（User + Machine），把用户最新 `export` / `setx` 的变量同步进 agent-service 主进程环境。删除采用可逆回退：用户在 rc 里删掉的变量，注入前不存在则移除、注入前是系统原值则回退到原值。受保护键（`HOME` / `USER` / `SHELL` / `DESIRECORE_*` 等）不受影响。
2. **清除运行时检测缓存并重新检测**，返回最新 `EnvironmentSnapshot`。

```bash
curl -sk -X POST "${DESIRECORE_API}/api/runtime/environment/refresh"
```

返回结构（在 `EnvironmentSnapshot` 基础上附带 `envDiff`）：

```ts
type EnvDiff = {
  added: string[]    // 本次新增的环境变量名
  removed: string[]  // 本次移除 / 回退的环境变量名
  changed: string[]  // 值发生变更的环境变量名
}
// 返回 = EnvironmentSnapshot & { envDiff: EnvDiff }
```

**何时主动调用此端点：**

- **触发了任何安装/移除操作后**（Python/Node 版本、包管理器）：失效检测缓存，否则后续 GET `/environment` 仍返回旧快照。
- **用户反馈「我改了 `.zshrc` / 某个环境变量 / 代理 / `export` 了新变量，但你（Agent）还是看不到」**：调此端点重新加载登录环境，用户**无需重启 App**。调用后**新执行**的 Bash / 脚本工具即可看到更新后的变量。可读取返回的 `envDiff.added` / `envDiff.removed` 向用户确认实际生效的变更。

**局限**：刷新仅更新主进程 `process.env` 及刷新**后**新 spawn 的子进程；已常驻运行的子进程（已启动的 MCP server、后台 `&` 进程）仍持旧 env，需重启该子进程才能生效。

## 八、参考源代码

| 模块 | 文件 | 行数（仓库 ~/Project/desirecore） |
|------|------|----------------------------------|
| 工具检测 | `lib/agent-service/environment-detection.ts` | 1–310 |
| 工具链管理（Hatch/Volta + 版本安装） | `lib/agent-service/runtime-manager.ts` | 1–1165 |
| HTTP 路由 | `lib/agent-service/routes/runtime-env-routes.ts` | 1–186 |
| 端口文件 | `${DESIRECORE_ROOT}/agent-service.port` | DesireCore 启动时写入 |
