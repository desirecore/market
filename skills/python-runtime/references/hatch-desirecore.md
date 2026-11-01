# DesireCore 内置 Hatch（L1 / L2 主路径）

DesireCore 内置 [Hatch](https://hatch.pypa.io/) v1.16.5，**用户无需单独安装**。

| 内容 | 位置 |
|------|------|
| Hatch 二进制（随包，默认） | 应用目录下的 `static/toolchains/<平台>-<架构>/hatch/hatch`（Windows 为 `hatch.exe`）。应用目录在 macOS 是 `<App>.app/Contents`，其他平台是安装目录 |
| Hatch 二进制（手动下载，存在时优先） | `${DESIRECORE_ROOT}/runtime/hatch/hatch`，只有随包二进制不可用、经 `POST /hatch/install` 下载后才存在 |
| Hatch 分发（客户端 10.0.183 起） | `${DESIRECORE_ROOT}/runtime/hatch/bootstrap/<Hatch 版本>-<平台>-<架构>/`，客户端启动后从随包归档解包 |
| 内置 Python | `${DESIRECORE_ROOT}/runtime/hatch/local/<版本>/python/bin/python3`（Windows 为 `python\python.exe`，pip 在旁边的 `Scripts\`） |

## 直接使用内置 Python（通常不需要安装）

客户端首次启动时导入一个内置 Python（目前是 3.13），可以直接用。DesireCore 把一个内置版本（推荐版本已安装就用它，否则取最高版本）的目录追加到服务进程 PATH 末尾，Bash 等工具都会继承，不改用户的 shell 配置。

- 系统没有 Python 时，直接运行 `python3`、`pip3`。
- 系统已有 Python 时系统版本优先（Windows 商店跳转存根、macOS 缺开发者工具时的 `/usr/bin` 工具 shim 不算，内置目录会排在它们前面）。要用内置版本，写绝对路径。版本清单见 `<env>` 块的 Managed runtimes 段，或列目录：

```bash
LOCAL="${DESIRECORE_ROOT}/runtime/hatch/local"
ls "$LOCAL"

"$LOCAL/<版本>/python/bin/python3" --version
"$LOCAL/<版本>/python/bin/python3" -m venv .venv
```

Windows：`$env:DESIRECORE_ROOT\runtime\hatch\local\<版本>\python\python.exe`。

只有需要另一个版本时才用下面的 L1 / L2 安装。

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

standalone 部署的接口要求实例令牌，Agent 没有，会返回 401，这时走 L2。桌面版的本机请求不需要令牌。

### 检查 Hatch 状态 / 安装

```bash
# 实际执行一次 hatch --version，解包还没完成时会先等它
curl -sk "${BASE}/hatch/status"
# → {"installed":true,"version":"1.16.5"}

# 随包 Hatch 可用时直接返回成功，否则下载到 runtime/hatch/
curl -sk -X POST "${BASE}/hatch/install"
```

### Python 版本管理

```bash
# 已安装版本
curl -sk "${BASE}/python/installed"
# → ["3.13"]

# 可安装版本（Hatch 内置清单，不联网；Hatch 不可用时回落到兜底清单）
curl -sk "${BASE}/python/available"
# → {"source":"live","versions":[{"name":"3.12","version":"3.12.12"}, ...]}

# 安装（异步，立即返回 taskId）。version 填上面的 name，如 3.12，不是 3.12.12
curl -sk -X POST "${BASE}/python/install" \
  -H "Content-Type: application/json" \
  -d '{"version":"3.12"}'
# → { "taskId": "uuid" }
# 首启导入还在进行时返回 409，稍后再试

# 移除
curl -sk -X POST "${BASE}/python/remove" \
  -H "Content-Type: application/json" \
  -d '{"version":"3.10"}'
```

### 实时输出 / 缓存刷新

DesireCore 内部界面连了 Socket.IO；在 Bash 里用 `curl` 调用时收不到输出，任务在 100ms 后静默执行。要看进度：

- 监听事件 `runtime:terminal`，payload `{ taskId, data }`，按 taskId 过滤
- 任务结束事件 `runtime:complete`，payload `{ taskId, success }`

没有 Socket.IO 客户端时，轮询 `GET ${BASE}/python/installed`：安装时等目标版本出现，移除时等它消失。任务失败时轮询不会收到信号，服务日志里也没有原因，所以要设上限；超时后改走 L2，CLI 会直接打印报错。

```bash
curl -sk -X POST "${BASE}/environment/refresh"   # 安装结束后刷新
```

## L2：直接调用 Hatch CLI 绝对路径

### macOS / Linux

```bash
SNAPSHOT=$(bash skills/python-runtime/scripts/probe-python.sh)

# 二进制路径取自探测结果，为空时见下方「找不到 Hatch 二进制」
HATCH=$(echo "$SNAPSHOT" | jq -r .hatch_path)

# 每次调用都要设置：DesireCore 只在自己调用 Hatch 时设置它，不传给 Bash
export PYAPP_INSTALL_DIR_HATCH=$(echo "$SNAPSHOT" | jq -r .hatch_bootstrap)

# 内置 Python 的目录，下面每条命令都要带上
LOCAL="${DESIRECORE_ROOT}/runtime/hatch/local"

# 列出版本表
"$HATCH" python show --dir "$LOCAL"
# Installed
# ┌──────┬─────────┐
# │ Name │ Version │
# ├──────┼─────────┤
# │ 3.13 │ 3.13.9  │
# └──────┴─────────┘
# Available
# ┌──────────┬─────────┐
# │ Name     │ Version │
# ├──────────┼─────────┤
# │ 3.11     │ 3.11.14 │
# │ 3.12     │ 3.12.12 │
# │ 3.14     │ 3.14.0  │
# └──────────┴─────────┘

# 安装
"$HATCH" python install 3.12 --private --dir="$LOCAL"
"$HATCH" python install 3.11 3.10 --private --dir="$LOCAL"   # 批量

# 已装版本（直接读目录最稳）
ls "$LOCAL"

# 移除
"$HATCH" python remove 3.11 --dir="$LOCAL"

# 查某个版本的路径
"$HATCH" python find 3.12 --dir "$LOCAL"
```

**`python install` 必须带 `--private --dir`。** 不带时 Hatch 装到用户数据目录（macOS 为 `~/Library/Application Support/hatch/pythons`），还会把它写进 `.zshrc`、`.zprofile` 等 shell 配置，而 DesireCore 看不到这个 Python。

**`PYAPP_INSTALL_DIR_HATCH` 指向客户端解包好的 Hatch 分发。** 随包的 `hatch` 只是 PyApp 引导程序，不带这个变量时，任何命令（包括 `--version`）第一次运行都要联网下载约 45MB 的分发，解压后在用户目录占约 160MB（macOS 为 `~/Library/Application Support/pyapp`、`~/Library/Caches/pyapp`）。探测结果里 `hatch_bootstrap` 为空，说明客户端早于 10.0.183，或者启动后的解包还没完成（`GET ${BASE}/hatch/status` 会等它完成）。

### 找不到 Hatch 二进制

`probe-python.sh` 依次查找 `${DESIRECORE_ROOT}/runtime/hatch/hatch`、`$DESIRECORE_STATIC_DIR` 下的工具链、`runtime/volta-home/bin/node` 的链接目标旁边的工具链，以及默认安装位置（`/Applications/*.app/Contents/static`、`/opt/*/static`）。应用装在别处时 `hatch_path` 为空（AppImage 每次启动的挂载路径都不同），这时走 L1，或按本文开头的表格到应用目录下找。

### Windows PowerShell

```powershell
# 手动下载过 Hatch 时改用 "$env:DESIRECORE_ROOT\runtime\hatch\hatch.exe"
$Hatch = "<安装目录>\static\toolchains\win32-x64\hatch\hatch.exe"
$env:PYAPP_INSTALL_DIR_HATCH = "$env:DESIRECORE_ROOT\runtime\hatch\bootstrap\<Hatch 版本>-win32-x64"
$Local = "$env:DESIRECORE_ROOT\runtime\hatch\local"

& $Hatch python show --dir "$Local"
& $Hatch python install 3.12 --private "--dir=$Local"
```

Windows ARM64 随包的 `hatch-universal.exe` 是安装器，不能当 CLI 调用，这个平台走 L3。

### 使用 Hatch 安装的 Python

```bash
# 直接用绝对路径
"$LOCAL/3.12/python/bin/python3" --version

# 创建项目级虚拟环境（venv 推荐）
"$LOCAL/3.12/python/bin/python3" -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows：`$env:DESIRECORE_ROOT\runtime\hatch\local\3.12\python\python.exe`，pip 在同级的 `Scripts\`。

## 可视化管理

DesireCore 应用 → 资源管理器（侧边栏文件夹图标）→ 计算资源 → **运行环境** Tab，GUI 安装 / 删除 Python 版本。

## Hatch vs pyenv

| 维度 | Hatch（DesireCore 内置） | pyenv（社区） |
|------|--------------------------|---------------|
| 安装方式 | 随应用自动内置 | 用户手动安装 |
| Python 存放 | `${DESIRECORE_ROOT}/runtime/hatch/local/` | `~/.pyenv/versions/` |
| 版本切换 | 绝对路径 / venv | shell PATH (`pyenv global/local`) |
| 系统影响 | 带 `--private` 时完全隔离 | 修改 shell 启动脚本 |
| GUI | DesireCore 运行环境 Tab | 无 |
| 自定义下载源 | `HATCH_PYTHON_CUSTOM_SOURCE_<NAME>` 环境变量 | `PYTHON_BUILD_MIRROR_URL` |
| 适用 | 技能执行环境（强隔离） | 系统级日常开发 |

**结论**：DesireCore 应用内、有 Hatch 时永远首选 Hatch；外部脚本/独立项目可考虑 pyenv。

## 故障排查（Hatch 专属）

| 现象 | 排查 |
|------|------|
| `${DESIRECORE_ROOT}/runtime/hatch/hatch: not found` | 这个文件只有手动下载后才存在，属于正常情况。用随包二进制，见「找不到 Hatch 二进制」 |
| `ValueError: Unknown distribution source: http://127.0.0.1:...` | 见下方「修复首启导入留下的来源记录」 |
| `python install` 成功但 `local/` 里没有这个版本，`.zshrc` 多了一段 `export PATH` | 没带 `--private --dir`。用正确的参数重新安装；`"$HATCH" python remove <版本>`（不带 `--dir`）移除装错的那份，再删掉 shell 配置里 `Created by userpath` 那段 |
| `hatch --version` 卡住很久 | 没带 `PYAPP_INSTALL_DIR_HATCH`，正在下载 Hatch 分发 |
| Hatch 安装 Python 时网络超时 | 可以重试。需要换下载源时设 `HATCH_PYTHON_CUSTOM_SOURCE_<NAME>`：完整归档 URL，加号写成 `%2B`，路径里必须有 `/python-build-standalone/releases/download/`，否则这个地址被记进 `hatch-dist.json` 后同样会报 `Unknown distribution source`；`<NAME>` 是大写的版本名，点换成下划线，如 `3_12`。`hatch python install --help` 里写的 `HATCH_PYTHON_SOURCE_<NAME>` 在 1.16.5 上不生效 |
| 多版本共存路径混乱 | Hatch 永远绝对路径调用，**不要**把版本目录手动写进 PATH |
| macOS Gatekeeper 阻止手动下载的二进制 | `xattr -d com.apple.quarantine "${DESIRECORE_ROOT}/runtime/hatch/hatch"` |

### 修复首启导入留下的来源记录

首次启动从随包归档导入 Python 时，下载地址是本机镜像，这个地址被记进了 `local/<版本>/hatch-dist.json`。Hatch 不认它，所以只要 `local/` 里有这样的版本，针对这个目录的 `python install`、`python remove`、`python show` 都会报 `ValueError: Unknown distribution source`，走 HTTP API 也一样（任务静默失败）。内置 Python 本身不受影响，可以继续用。

把记录改回官方地址就能恢复，归档内容与官方相同：

```bash
for f in "${DESIRECORE_ROOT}"/runtime/hatch/local/*/hatch-dist.json; do
  sed 's#http://127\.0\.0\.1:[0-9]*/runtime-mirror/python/#https://github.com/astral-sh/python-build-standalone/releases/download/#' "$f" > "$f.tmp" \
    && mv "$f.tmp" "$f"
done
```

PowerShell：

```powershell
Get-ChildItem "$env:DESIRECORE_ROOT\runtime\hatch\local\*\hatch-dist.json" | ForEach-Object {
  $text = (Get-Content -Raw $_.FullName) -replace 'http://127\.0\.0\.1:\d+/runtime-mirror/python/', 'https://github.com/astral-sh/python-build-standalone/releases/download/'
  [System.IO.File]::WriteAllText($_.FullName, $text)
}
```
