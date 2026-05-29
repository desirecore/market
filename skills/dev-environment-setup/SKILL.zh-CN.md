<!-- locale: zh-CN -->

# dev-environment-setup 技能（v2.0.0 router）

## L0：一句话摘要

**何时使用**：用户需要

- 安装 / 排查 **Docker** 或 **Podman** 容器（"docker not found"、daemon 启动、镜像加速等）
- 在 Windows 上配置 **WSL2**（Linux 子系统）
- 一次性安装 **办公技能依赖**（DOCX / PDF / XLSX / PPTX 所需的 Python 包 + npm 包 + 系统工具）
- 安装 **系统工具**：LibreOffice / Poppler / Pandoc / Tesseract / qpdf / ImageMagick / Ghostscript / Git
- **不确定** 问题属于 Python 还是 Node.js，需要先做综合诊断

**何时不要用**：纯 Python 问题用 `python-runtime`，纯 Node.js 问题用 `nodejs-runtime`。

**怎么做**：先跑 `scripts/probe.sh`（Windows 用 `probe.ps1`）取系统快照 JSON，
按结果路由到对应 references 或子 skill；同时也是 DesireCore 内置 Hatch / Volta /
HTTP API / Socket.IO 集成的事实源（`references/desirecore-runtime.md`）。

## L1：路由规则

按用户问题的关键字直接转到对应 skill 或文档：

| 关键字 / 场景 | 路径 |
|--------------|------|
| python / pip / venv / pyenv / hatch / virtualenv / PEP 668 | `python-runtime` skill |
| node / npm / pnpm / yarn / volta / nvm / fnm / EACCES | `nodejs-runtime` skill |
| docker / podman / container / 容器守护进程 | `references/container.md` |
| WSL / WSL2 / Windows Linux 子系统 | `references/wsl.md` |
| DOCX / PDF / XLSX / PPTX 依赖 / 办公技能依赖 | `references/office-deps.md` |
| LibreOffice / poppler / pandoc / tesseract / qpdf | `references/system-tools.md` |
| 不确定属于哪类、想要快速诊断 | 先跑 `scripts/probe.sh` 看 JSON |
| DesireCore Hatch / Volta / HTTP API / Socket.IO | `references/desirecore-runtime.md` |
| 四级降级决策（API → CLI → 包管理器 → 社区方案） | `references/decision-tree.md` |

## L2：详细规范

### 第一步：快速诊断

```bash
bash skills/dev-environment-setup/scripts/probe.sh > /tmp/env-probe.json
cat /tmp/env-probe.json | jq .
```

输出字段含义：见 `references/probe-snapshot.md`。Windows 用 `scripts/probe.ps1`。

### 第二步：按结果路由

- `desirecore_api` 非空 → 走 HTTP API 路径（`references/desirecore-runtime.md`）
- `tools.python3.available = false` 或 `tools.node.available = false` → 进入对应子 skill
- `tools.docker.available = false` 且用户需容器 → `references/container.md`
- `wsl.installed = false` 且 Windows 用户 → `references/wsl.md`

### 第三步：执行子 skill 决策树

`python-runtime` 与 `nodejs-runtime` 都有自己的四级降级（L1 API → L2 内置 CLI → L3 系统包管理器 → L4 社区方案），定义在共享的 `references/decision-tree.md`。

### 第四步：办公技能依赖

办公四件套（DOCX / PDF / XLSX / PPTX）依赖速查：`references/office-deps.md`。包含 Python 包、npm 包、系统工具的一键安装命令。

### 第五步：系统工具

LibreOffice / Poppler / Pandoc / Tesseract / qpdf / ImageMagick / Ghostscript 安装与故障排查：`references/system-tools.md`。

## DesireCore 内置环境管理底座

DesireCore 内置 Hatch（Python）和 Volta（Node.js），通过 HTTP API + Socket.IO 提供完整的环境管理能力。本 skill 与子 skill（python/nodejs）都依赖：

| 文档 | 内容 |
|------|------|
| `references/desirecore-runtime.md` | 二进制路径表、HTTP API 速查、Socket.IO 事件契约、`EnvironmentSnapshot` 数据结构 |
| `references/decision-tree.md` | 四级降级流程图、判定失败的具体信号、切换提示 |
| `references/probe-snapshot.md` | 探测脚本 JSON 输出协议 |

## 重要约束

1. **不要把 python / node / pip / npm 强关键词写入本 skill description**——这些归属各自的子 skill，避免触发冲突。
2. **API 优先**：`scripts/probe.sh` 第一步检测 `${DESIRECORE_ROOT}/agent-service.port`；存在则推荐 HTTP API 路径。
3. **缓存协同**：任何安装/移除完成后，调 `POST /api/runtime/environment/refresh` 失效缓存，再发后续 GET。
4. **跨平台**：所有命令模板提供 macOS / Linux + Windows（PowerShell）双版本。

## 子 skill 与文档清单

```
skills/
├── python-runtime/        # Python 环境（Hatch 优先）
├── nodejs-runtime/        # Node.js 环境（Volta 优先）
└── dev-environment-setup/         # 本 skill（综合入口）
    ├── references/
    │   ├── desirecore-runtime.md
    │   ├── decision-tree.md
    │   ├── probe-snapshot.md
    │   ├── container.md
    │   ├── wsl.md
    │   ├── office-deps.md
    │   └── system-tools.md
    └── scripts/
        ├── probe.sh
        └── probe.ps1
```

## 升级说明（v1.x → v2.0.0）

- v1.x 是单文件 1380 行的全能手册，已拆分。
- Python 相关 → `python-runtime`
- Node.js 相关 → `nodejs-runtime`
- Docker / WSL / 办公依赖 / 系统工具 → 本 skill 的 `references/`
- DesireCore Hatch / Volta 从"可选社区方案"升级为强制 L1/L2 主路径

下游 skill（docx / pdf / xlsx / pptx）应将 "Python 环境问题请参考 dev-environment-setup" 改写为 "Python 环境问题请参考 python-runtime / Node.js 环境问题请参考 nodejs-runtime"。
