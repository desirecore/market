# 环境探测 JSON 协议

`probe.sh` / `probe.ps1` / `probe-python.sh` / `probe-node.sh` 输出统一 JSON。Skill 解析 JSON 后再决策，避免逐条 grep。

## 通用字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `platform` | `"darwin" \| "linux" \| "win32"` | 操作系统标识 |
| `arch` | `"arm64" \| "x64" \| ...` | CPU 架构 |
| `desirecore_api` | `string` | 探测到的 DesireCore agent-service URL，不可达时为 `""` |
| `desirecore_port_file` | `boolean` | `${DESIRECORE_ROOT}/agent-service.port` 是否存在（probe.sh / probe.ps1 输出原生 JSON boolean） |

## probe.sh / probe.ps1（父级 dev-environment-setup）

输出系统级总览：

```json
{
  "platform": "darwin",
  "arch": "arm64",
  "desirecore_api": "https://127.0.0.1:38291",
  "desirecore_port_file": true,
  "tools": {
    "python3": { "available": true, "path": "/opt/homebrew/bin/python3", "version": "3.12.4" },
    "pip3":    { "available": true, "path": "/opt/homebrew/bin/pip3",    "version": "24.0" },
    "node":    { "available": true, "path": "/opt/homebrew/bin/node",    "version": "22.4.1" },
    "npm":     { "available": true, "path": "/opt/homebrew/bin/npm",     "version": "10.8.1" },
    "docker":  { "available": false },
    "podman":  { "available": false },
    "git":     { "available": true, "path": "/usr/bin/git", "version": "2.43.0" }
  },
  "wsl": null
}
```

Windows 上 `wsl` 字段值类似 `{ "installed": true, "version": "2", "defaultDistro": "Ubuntu" }`。

## probe-python.sh（python-runtime 专用）

```json
{
  "platform": "darwin",
  "arch": "arm64",
  "desirecore_api": "https://127.0.0.1:38291",
  "system_python": { "path": "/opt/homebrew/bin/python3", "version": "3.12.4" },
  "system_pip": { "path": "/opt/homebrew/bin/pip3", "version": "24.0" },
  "hatch_path": "/Users/wangyi/.desirecore/runtime/hatch/hatch",
  "hatch_version": "1.16.5",
  "hatch_versions": ["3.11", "3.12"],
  "active_venv": "/Users/wangyi/proj/.venv",
  "pep668": false,
  "pyenv_path": "",
  "conda_path": ""
}
```

字段语义：
- `hatch_path` 空字符串表示二进制不存在
- `hatch_versions` 是 `${DESIRECORE_ROOT}/runtime/hatch/local/` 下的目录列表（即已通过 Hatch 安装的 Python 版本）
- `active_venv` 取自 `$VIRTUAL_ENV` 环境变量
- `pep668` 检测 `/usr/lib/python*/EXTERNALLY-MANAGED` 是否存在（Debian 12+/Ubuntu 23.04+ 启用）

## probe-node.sh（nodejs-runtime 专用）

```json
{
  "platform": "darwin",
  "arch": "arm64",
  "desirecore_api": "https://127.0.0.1:38291",
  "system_node": { "path": "/opt/homebrew/bin/node", "version": "22.4.1" },
  "system_npm":  { "path": "/opt/homebrew/bin/npm",  "version": "10.8.1" },
  "volta_path": "/Users/wangyi/.desirecore/runtime/volta/volta",
  "volta_version": "2.0.2",
  "volta_tools": {
    "node": ["22.4.1"],
    "pnpm": ["9.5.0"],
    "yarn": [],
    "npm":  []
  },
  "package_json_volta": null,
  "nvm_path": "",
  "fnm_path": "",
  "registry": "https://registry.npmmirror.com/",
  "proxy": ""
}
```

字段语义：
- `volta_tools` 来自 `<volta> list --format=plain`，按工具分类
- `package_json_volta` 若当前目录存在 `package.json` 且其中有 `"volta"` 字段，填入对象；否则 `null`
- `registry` / `proxy` 来自 `npm config get registry` / `npm config get https-proxy`

## 设计约定

1. **JSON 必合法**：缺字段也保留键并赋空字符串/`null`，避免 Claude 解析失败。
2. **不阻塞**：每个外部命令都加 `2>/dev/null`，失败用空值，不让脚本中途退出。
3. **超时控制**：HTTP 探测 0.5s 超时（curl `--max-time`/PowerShell `TimeoutSec`）；CLI 调用（`--version` 等）依赖工具自身实现，无显式 timeout 包装，正常情况通常 <5s 完成。
4. **跨平台**：`probe.sh` / `probe-python.sh` / `probe-node.sh` 共用 POSIX 子集；Windows 同等功能由 `probe.ps1` 提供（仅父级提供，python/nodejs 子 skill 可由 PowerShell 直接 invoke 父级或自行实现）。
5. **路径展开**：所有 `~` 在 JSON 中展开为绝对路径，避免下游解析歧义。

## 调用约定

```bash
SNAPSHOT=$(bash skills/python-runtime/scripts/probe-python.sh)
echo "$SNAPSHOT" | jq .

# 关键字段判定
HATCH=$(echo "$SNAPSHOT" | jq -r .hatch_path)
[ -n "$HATCH" ] && [ "$HATCH" != "null" ] && echo "Hatch 可用"
```

PowerShell 等价：

```powershell
$snapshot = & "$PWD\skills\dev-environment-setup\scripts\probe.ps1" | ConvertFrom-Json
if ($snapshot.tools.node.available) { ... }
```
