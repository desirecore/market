# DesireCore 内置环境管理底座

DesireCore 内置了完整的开发环境管理基础设施。`python-runtime` 和 `nodejs-runtime` 两个 skill 共用本文档作为事实源。

## 一、内置工具二进制

### Hatch（Python 项目与版本管理器，v1.16.5）

| 平台 | 手动下载（存在时优先） | 随包（默认） |
|------|------------------------|--------------|
| macOS / Linux | `${DESIRECORE_ROOT}/runtime/hatch/hatch` | 应用目录下 `static/toolchains/<平台>-<架构>/hatch/hatch` |
| Windows | `$env:DESIRECORE_ROOT\runtime\hatch\hatch.exe` | 应用目录下 `static\toolchains\win32-x64\hatch\hatch.exe` |

应用目录在 macOS 是 `<App>.app/Contents`，其他平台是安装目录。`runtime/hatch/` 下只有手动下载 Hatch 后才有二进制。Windows ARM64 随包的 `hatch-universal.exe` 是安装器，不能当 CLI 调用。

**Hatch 分发**：`${DESIRECORE_ROOT}/runtime/hatch/bootstrap/<Hatch 版本>-<平台>-<架构>/`（客户端 10.0.183 起），客户端启动后从随包归档解包。随包的 `hatch` 只是 PyApp 引导程序，直接调用时用 `PYAPP_INSTALL_DIR_HATCH` 指向这里，否则任何命令（包括 `--version`）第一次运行都要联网下载约 45MB，并解压到用户目录。

**Python 版本安装目录**：`${DESIRECORE_ROOT}/runtime/hatch/local/<版本>/python/bin/python3`（macOS/Linux），Windows 为 `python\python.exe`，pip 在旁边的 `Scripts\`。安装时必须带 `--private --dir=<这个 local 目录>`，否则 Hatch 装到用户数据目录并改写 `.zshrc`、`.zprofile`。

**内置 Python 已在 PATH 上**：服务把一个版本的可执行文件目录追加到进程 PATH 末尾，Bash 等工具都会继承，所以通常直接用 `python3`、`pip3`。系统已有 Python 时系统版本优先，要用内置版本就写绝对路径。

### Volta（Node.js 工具链管理器，v2.0.2）

| 平台 | 手动下载（存在时优先） | 随包（默认） |
|------|------------------------|--------------|
| macOS / Linux | `${DESIRECORE_ROOT}/runtime/volta/volta` | 应用目录下 `static/toolchains/<平台>-<架构>/volta/volta` |
| Windows | `$env:DESIRECORE_ROOT\runtime\volta\volta.exe` | 应用目录下 `static\toolchains\win32-<架构>\volta\volta.exe` |

应用目录在 macOS 是 `<App>.app/Contents`，其他平台是安装目录。`runtime/volta/` 只有手动下载 Volta 后才有二进制。

**Volta Home**：`${VOLTA_HOME:-${DESIRECORE_ROOT}/runtime/volta-home}`（启动 DesireCore 前显式设置的 `VOLTA_HOME` 优先）。

**Node.js 安装目录**：`<Volta Home>/tools/image/node/<version>/`，可执行文件在其下的 `bin/`（Windows 没有 `bin` 这一层），包管理器在 `tools/image/{packages,pnpm,yarn,npm}/`。

**内置 Node 已在 PATH 上**：服务把一个版本的可执行文件目录追加到进程 PATH 末尾，Bash 等工具都会继承，所以通常直接用 `node`、`npm`。系统已有 Node 时系统版本优先，要用内置版本就写绝对路径。

**不要使用 `<Volta Home>/bin`**：这里的入口是 Volta shim，未导出 `VOLTA_HOME` 时看的是 `~/.volta`，拿不到 DesireCore 的 Node：报 `Node is not available`，系统有 Node 时则透传到系统版本。放在 PATH 上还会卡住超过 30 秒。

### 优先级规则

`runtime/` 下的二进制优先于 `static/`。随包二进制可用时不会下载，只有它不可用时，`POST /hatch/install`、`POST /volta/install` 才写入 `runtime/`。

## 二、关键环境变量

| 变量 | 作用 | 默认/示例 |
|------|------|----------|
| `PYAPP_INSTALL_DIR_HATCH` | Hatch 分发目录 | `${DESIRECORE_ROOT}/runtime/hatch/bootstrap/<Hatch 版本>-<平台>-<架构>` |
| `HATCH_PYTHON_CUSTOM_SOURCE_<NAME>` | 覆盖某个 Python 版本的下载地址（完整归档 URL，加号写成 `%2B`，路径里必须有 `/python-build-standalone/releases/download/`） | `<NAME>` 是大写的版本名，点换成下划线，如 `3_12` |
| `VOLTA_HOME` | Volta 工作目录 | `${DESIRECORE_ROOT}/runtime/volta-home` |
| `VOLTA_FEATURE_PNPM` | 启用 pnpm 管理 | `1` |

DesireCore 只在自己调用 Hatch / Volta 时设置这些变量，不会传给 Bash 等工具；直接调用绝对路径 CLI 时需手动 export。

客户端还会设置 `HATCH_HOME`，但 Hatch 1.16.5 不读这个变量，也没有 `HATCH_PYTHON_MIRROR_URL`，这两个都不用设。Python 的安装目录靠 `--dir` 指定。

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
| GET | `/hatch/status` | 实际执行一次 `hatch --version`，Hatch 分发还没解包完时会先等它；返回 `{ installed, version }` |
| POST | `/hatch/install` | 随包 Hatch 可用时直接返回成功，否则下载并安装到 `runtime/hatch/`（同步返回成功/失败） |
| GET | `/volta/status` | 检查 Volta 是否就绪 |
| POST | `/volta/install` | 随包 Volta 可用时直接返回成功，否则下载并安装到 `runtime/volta/` |

### Python 版本管理

| 方法 | 路径 | 请求体 / 返回 |
|------|------|--------------|
| GET | `/python/installed` | 返回已安装版本列表（`["3.11", "3.12"]`） |
| GET | `/python/available` | 返回可安装版本 `{ source, versions: [{ name, version }] }`（Hatch 内置清单，不联网；Hatch 不可用时回落到兜底清单） |
| POST | `/python/install` | `{ "version": "3.12" }`（填上面的 `name`）→ `{ "taskId": "uuid" }`，订阅 `runtime:terminal` 流；首启导入进行中返回 409 |
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
| POST | `/pkg/{tool}/install` | `{ "version": "9.15.9" }`（必须是完整版本号，否则返回 400）→ `{ "taskId": "uuid" }` |
| POST | `/pkg/{tool}/remove` | `{ "version": "9.0.0" }` → `{ "taskId": "uuid" }` |

## 四、Socket.IO 实时输出契约

耗时操作（`*/install`、`*/remove`）立即返回 `{ taskId }`，真正的执行延迟 100ms 启动，期间通过 Socket.IO 推送：

| 事件 | Payload | 触发时机 |
|------|---------|----------|
| `runtime:terminal` | `{ taskId, data }` | 每行 stdout/stderr 输出 + 操作开始/结束的状态行 |
| `runtime:complete` | `{ taskId, success }` | 任务结束（成功 / 失败 / 异常） |

**前端订阅时序**：先 HTTP POST 拿 taskId → 再连 Socket.IO 监听该 taskId → 服务端 100ms 后开工。Skill 在无 Socket.IO 客户端时收不到日志：优先用绝对路径 CLI 同步执行；拿不到 CLI 路径时仍可走异步 HTTP API，再轮询对应的 `installed` 接口确认结果：安装时等目标版本出现，移除时等它消失。任务失败时轮询不会收到信号，所以要设上限。

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

`GET /api/runtime/environment` 返回结构（详见主仓库 `packages/agent-service/src/context/environment-detection.ts`）：

```ts
type ToolDetection = {
  available: boolean
  status?: 'available' | 'not_found' | 'detection_failed'  // detection_failed 只表示本次没有结论，不能据此建议安装
  failureCode?: string
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
    brew: ToolDetection
    gh: ToolDetection
    cuaDriver: ToolDetection
  }
  toolkits?: unknown[]  // 命令行工具套件（如 FFmpeg）的检测结果
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

| 模块 | 文件（主仓库） |
|------|----------------|
| 工具检测 | `packages/agent-service/src/context/environment-detection.ts` |
| 工具链管理（Hatch/Volta + 版本安装） | `packages/agent-service/src/session/runtime-manager.ts` |
| 内置运行时进 PATH | `packages/agent-service/src/session/managed-runtime-path.ts` |
| HTTP 路由 | `packages/agent-service/src/routes/runtime-env-routes.ts` |
| 端口文件 | `${DESIRECORE_ROOT}/agent-service.port`，DesireCore 启动时写入 |
