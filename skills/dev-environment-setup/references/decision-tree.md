# 环境管理四级降级决策树

`python-runtime` 与 `nodejs-runtime` 在执行任何安装/版本切换前必须按本决策树选择路径。

## 总体流程

```
                         ┌──────────────────┐
                         │  执行 probe 脚本 │
                         └─────────┬────────┘
                                   ▼
                  ┌─────────────────────────────┐
                  │ desirecore_api 字段非空？    │
                  └────────┬───────────────┬─────┘
                       是 │               │ 否
                          ▼               ▼
                ┌──────────────────┐  ┌──────────────────┐
                │ L1：HTTP API 路径 │  │ hatch_path /      │
                └────────┬─────────┘  │ volta_path 非空？ │
                         │            └────────┬──┬──────┘
                  失败/超时              是   │  │ 否
                         ▼                    ▼  ▼
                ┌──────────────────┐  ┌──────────────────┐
                │ L2：DesireCore CLI │  │ L3：系统包管理器 │
                └────────┬─────────┘  └────────┬─────────┘
                         │                     │
                  二进制损坏 / 安装失败          失败/不可用
                         ▼                     ▼
                ┌─────────────────────────────────────────┐
                │ L4：社区方案（pyenv / nvm / fnm / conda）│
                └─────────────────────────────────────────┘
```

## L1：DesireCore HTTP API（最高优先级）

**触发条件**

- `${DESIRECORE_ROOT}/agent-service.port` 文件存在且可读
- `curl -sk --max-time 0.5 https://127.0.0.1:${PORT}/api/runtime/environment` 返回 2xx
- 当前会话能订阅 Socket.IO（DesireCore 内部 Agent 默认满足）

**典型操作**

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port)
BASE="https://127.0.0.1:${PORT}/api/runtime"

# 1. 拉取快照
curl -sk "${BASE}/environment"

# 2. 触发安装（异步）
curl -sk -X POST "${BASE}/python/install" \
  -H "Content-Type: application/json" \
  -d '{"version":"3.12"}'

# 3. 订阅 runtime:terminal / runtime:complete 事件展示日志
```

**判定失败的信号**

- HTTP 状态码 ≥ 500 或 502（远端镜像不可用，详见 runtime-env-routes.ts 130/162 行）
- `runtime:complete` 事件 `success: false`
- Socket.IO 连接断开后超过 30 秒未收到 `runtime:complete`

**切换提示**：API 失败立即降级到 L2 CLI，不要重试同一接口（可能是镜像被墙）。

## L2：DesireCore 内置 CLI（绝对路径）

**触发条件**

- API 不可达或失败
- probe 脚本中 `hatch_path` / `volta_path` 字段非空（即二进制存在）

**典型操作（macOS / Linux）**

```bash
HATCH=${DESIRECORE_ROOT}/runtime/hatch/hatch
VOLTA=${DESIRECORE_ROOT}/runtime/volta/volta

export HATCH_HOME=${DESIRECORE_ROOT}/runtime/hatch
export VOLTA_HOME=${DESIRECORE_ROOT}/runtime/volta

"$HATCH" python install 3.12
"$VOLTA" install node@22
```

**典型操作（Windows PowerShell）**

```powershell
$Hatch = "$env:USERPROFILE\.desirecore\runtime\hatch\hatch.exe"
$Volta = "$env:USERPROFILE\.desirecore\runtime\volta\volta.exe"

$env:HATCH_HOME = "$env:USERPROFILE\.desirecore\runtime\hatch"
$env:VOLTA_HOME = "$env:USERPROFILE\.desirecore\runtime\volta"

& $Hatch python install 3.12
& $Volta install node@22
```

**判定失败的信号**

- exit code ≠ 0
- stderr 包含 `network`、`timeout`、`ENOTFOUND`、`failed to fetch`
- 可执行文件被反病毒软件隔离（macOS Gatekeeper / Windows Defender）

**切换提示**：失败后才考虑 L3，不要在 L2 内重试。

## L3：系统包管理器

**触发条件**：DesireCore 二进制全部缺失，或用户明确要求"系统级"安装。

| 平台 | Python | Node.js |
|------|--------|---------|
| macOS | `brew install python3` | `brew install node` |
| Debian/Ubuntu | `sudo apt install python3 python3-pip python3-venv` | NodeSource 仓库或 `sudo apt install nodejs npm` |
| Fedora/RHEL | `sudo dnf install python3 python3-pip` | `sudo dnf install nodejs` |
| Arch | `sudo pacman -S python python-pip` | `sudo pacman -S nodejs npm` |
| Windows | `winget install Python.Python.3` | `winget install OpenJS.NodeJS.LTS` |

**判定失败的信号**

- `command not found`（包管理器自身缺失，如 `brew` 未装）
- PEP 668 报错（Linux 新版发行版 `pip install` 全局被拒）→ 见 python-runtime troubleshooting
- 权限被拒（缺少 sudo / 非管理员）

**切换提示**：仅在系统包管理器都失败、并且用户明确希望安装时升级到 L4。

## L4：社区方案

仅在以下情况启用：

1. 用户明确指定（"我要 pyenv"、"用 nvm 装"）
2. L1–L3 全部失败
3. 项目已经使用社区方案（存在 `.python-version` / `.nvmrc` 文件）

| 工具 | 用途 | 文档 |
|------|------|------|
| pyenv / pyenv-win | Python 多版本 | python-runtime/references/pyenv-fallback.md |
| nvm / nvm-windows | Node.js 多版本（shell 脚本） | nodejs-runtime/references/nvm-fallback.md |
| fnm | Rust 实现的 nvm 替代 | nodejs-runtime/references/nvm-fallback.md |
| conda / miniconda | 数据科学场景 | python-runtime/references/virtualenv.md |

## 何时跳过决策树

skill 直接执行用户原话——不要走决策树——的情况：

- 用户明示路径："用 brew 装 python"、"在 .venv 里 pip install xxx"
- 用户在 skill 之外手工修改了环境（识别到 `.python-version`、`.nvmrc`、`package.json#volta`）
- skill 上下文已经存在激活的虚拟环境（`$VIRTUAL_ENV` 非空）

## 每次升级版本后

无论走哪条路径，**安装/移除完成后立即调用**：

```bash
# L1 模式
curl -sk -X POST "${BASE}/environment/refresh"

# L2/L3/L4 模式（强制 probe 输出最新结果）
bash <skill>/scripts/probe-{python,node}.sh
```

避免后续判断基于陈旧缓存。
