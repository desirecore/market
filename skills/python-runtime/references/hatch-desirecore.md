# DesireCore 内置 Hatch（L1 / L2 主路径）

DesireCore 内置 [Hatch](https://hatch.pypa.io/) v1.16.5。Hatch 二进制随应用打包于 `static/hatch/`，运行时位于 `~/.desirecore/runtime/hatch/`，**用户无需单独安装**。

> 与系统 Python 完全隔离：Hatch 安装的 Python 位于 `~/.desirecore/runtime/hatch/local/<version>/`，不修改系统 PATH。

## L1：通过 HTTP API 操作（推荐，DesireCore 应用内）

### 探测 API 可用性

```bash
PORT_FILE="$HOME/.desirecore/agent-service.port"
[ -r "$PORT_FILE" ] || { echo "API 不可用，降级到 L2"; exit 1; }
PORT=$(cat "$PORT_FILE")
BASE="https://127.0.0.1:${PORT}/api/runtime"

curl -sk --max-time 0.5 "${BASE}/environment" >/dev/null \
  || { echo "API 超时，降级到 L2"; exit 1; }
```

### 检查 Hatch 状态 / 安装

```bash
# 状态：runtime/static 任一存在即 ready
curl -sk "${BASE}/hatch/status"

# 若未就绪，触发自动下载
curl -sk -X POST "${BASE}/hatch/install"
```

### Python 版本管理

```bash
# 已安装版本
curl -sk "${BASE}/python/installed"
# → ["3.11", "3.12"]

# 可安装版本（来自 Hatch python show）
curl -sk "${BASE}/python/available"

# 安装（异步，立即返回 taskId）
curl -sk -X POST "${BASE}/python/install" \
  -H "Content-Type: application/json" \
  -d '{"version":"3.12"}'
# → { "taskId": "uuid" }

# 移除
curl -sk -X POST "${BASE}/python/remove" \
  -H "Content-Type: application/json" \
  -d '{"version":"3.10"}'
```

### 订阅实时输出

DesireCore 内部 Agent 默认连了 Socket.IO；外部脚本若未连，则 100ms 后任务静默执行。要看进度：

- 监听事件 `runtime:terminal`，payload `{ taskId, data }`，按 taskId 过滤
- 任务结束事件 `runtime:complete`，payload `{ taskId, success }`

### 强制刷新缓存

```bash
curl -sk -X POST "${BASE}/environment/refresh"
```

## L2：直接调用 Hatch CLI 绝对路径

### macOS / Linux

```bash
HATCH=~/.desirecore/runtime/hatch/hatch
export HATCH_HOME=~/.desirecore/runtime/hatch
# export HATCH_PYTHON_MIRROR_URL=...   # 中国大陆加速可选

# 列出版本表
"$HATCH" python show
# ┌──────────┬─────────┐
# │ Name     │ Version │
# ├──────────┼─────────┤
# │ 3.10     │ 3.10.16 │
# │ 3.11     │ 3.11.11 │
# │ 3.12     │ 3.12.8  │
# │ 3.13     │ 3.13.1  │
# │ pypy3.10 │ 7.3.17  │
# └──────────┴─────────┘

# 安装
"$HATCH" python install 3.12
"$HATCH" python install 3.12 3.11 3.10   # 批量

# 已装版本（直接读目录最稳）
ls ~/.desirecore/runtime/hatch/local/

# 移除
"$HATCH" python remove 3.11
```

### Windows PowerShell

```powershell
$Hatch = "$env:USERPROFILE\.desirecore\runtime\hatch\hatch.exe"
$env:HATCH_HOME = "$env:USERPROFILE\.desirecore\runtime\hatch"

& $Hatch python show
& $Hatch python install 3.12
```

### 使用 Hatch 安装的 Python

```bash
# 直接用绝对路径
~/.desirecore/runtime/hatch/local/3.12/python/bin/python3 --version

# 创建项目级虚拟环境（venv 推荐）
~/.desirecore/runtime/hatch/local/3.12/python/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows：`%USERPROFILE%\.desirecore\runtime\hatch\local\3.12\python\python.exe`。

## 可视化管理

DesireCore 应用 → 资源管理器（侧边栏文件夹图标）→ 计算资源 → **运行环境** Tab，GUI 安装 / 删除 Python 版本。

## Hatch vs pyenv

| 维度 | Hatch（DesireCore 内置） | pyenv（社区） |
|------|--------------------------|---------------|
| 安装方式 | 随应用自动内置 | 用户手动安装 |
| Python 存放 | `~/.desirecore/runtime/hatch/local/` | `~/.pyenv/versions/` |
| 版本切换 | 绝对路径 / venv | shell PATH (`pyenv global/local`) |
| 系统影响 | 完全隔离 | 修改 shell 启动脚本 |
| GUI | DesireCore 运行环境 Tab | 无 |
| 镜像加速 | `HATCH_PYTHON_MIRROR_URL` 环境变量 | `PYTHON_BUILD_MIRROR_URL` |
| 适用 | 技能执行环境（强隔离） | 系统级日常开发 |

**结论**：DesireCore 应用内、有 Hatch 时永远首选 Hatch；外部脚本/独立项目可考虑 pyenv。

## 故障排查（Hatch 专属）

| 现象 | 排查 |
|------|------|
| `~/.desirecore/runtime/hatch/hatch: not found` | 二进制未释放。先 `POST /api/runtime/hatch/install` 触发下载 |
| Hatch 安装 Python 时网络超时 | 设置 `HATCH_PYTHON_MIRROR_URL` 镜像 |
| 多版本共存路径混乱 | Hatch 永远绝对路径调用，**不要**写入 PATH |
| macOS Gatekeeper 阻止运行 | `xattr -d com.apple.quarantine ~/.desirecore/runtime/hatch/hatch` |
