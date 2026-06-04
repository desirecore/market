---
name: nodejs-runtime
description: >-
  Use this skill when the user needs to install, upgrade, or troubleshoot
  Node.js, npm, pnpm, yarn, and JavaScript/TypeScript runtime environments.
  Covers four-tier fallback strategy: (1) DesireCore HTTP API for in-app
  installation, (2) DesireCore built-in Volta CLI for Node.js + package
  manager version management, (3) system package managers
  (brew/apt/dnf/winget/NodeSource), (4) community nvm/fnm as last resort.
  Also covers global package management, npm registry/proxy configuration,
  EACCES permission errors, and PATH troubleshooting. Triggers include:
  "install node", "node not found", "npm not found", "npm EACCES", "pnpm",
  "yarn", "volta", "nvm", "fnm", "nodejs version", "package-lock", or any
  Node.js / npm runtime error. 使用场景：用户需要 安装 Node.js、安装 npm、
  pnpm、yarn、配置全局包、解决 EACCES、PATH 问题、镜像/代理配置。
version: 1.0.2
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - nodejs
  - npm
  - pnpm
  - yarn
  - volta
  - nvm
  - fnm
  - environment
metadata:
  author: desirecore
  updated_at: '2026-05-02'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: Node.js 运行时管理
      short_desc: Node.js / npm / pnpm / yarn 安装与多版本（DesireCore Volta 优先）
      description: >-
        Use this skill when the user needs to install, upgrade, or troubleshoot Node.js, npm, pnpm, yarn, and JavaScript/TypeScript runtime environments. Covers four-tier fallback strategy: (1) DesireCore HTTP API for in-app installation, (2) DesireCore built-in Volta CLI for Node.js + package manager version management, (3) system package managers (brew/apt/dnf/winget/NodeSource), (4) community nvm/fnm as last resort. Also covers global package management, npm registry/proxy configuration, EACCES permission errors, and PATH troubleshooting. Triggers include: "install node", "node not found", "npm not found", "npm EACCES", "pnpm", "yarn", "volta", "nvm", "fnm", "nodejs version", "package-lock", or any Node.js / npm runtime error. 使用场景：用户需要 安装 Node.js、安装 npm、 pnpm、yarn、配置全局包、解决 EACCES、PATH 问题、镜像/代理配置。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:2b8a00816c65d71c
      translated_by: human
    en-US:
      name: Node.js Runtime Management
      short_desc: Node.js / npm / pnpm / yarn install and multi-version (DesireCore Volta first)
      description: >-
        Use this skill when the user needs to install, upgrade, or troubleshoot Node.js, npm, pnpm, yarn, and JavaScript/TypeScript runtime environments. Covers four-tier fallback strategy: (1) DesireCore HTTP API for in-app installation, (2) DesireCore built-in Volta CLI for Node.js + package manager version management, (3) system package managers (brew/apt/dnf/winget/NodeSource), (4) community nvm/fnm as last resort. Also covers global package management, npm registry/proxy configuration, EACCES permission errors, and PATH troubleshooting. Triggers include: "install node", "node not found", "npm not found", "npm EACCES", "pnpm", "yarn", "volta", "nvm", "fnm", "nodejs version", "package-lock", or any Node.js / npm runtime error. Use cases: the user needs to install Node.js, install npm, pnpm, yarn, configure global packages, resolve EACCES, PATH issues, registry mirror / proxy configuration.
      body: ./SKILL.md
      source_hash: sha256:2b8a00816c65d71c
      translated_by: human
      translated_at: '2026-05-03'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="node-a" x1="3" y1="3" x2="21"
    y2="21" gradientUnits="userSpaceOnUse"><stop
    stop-color="#68A063"/><stop offset="1"
    stop-color="#3C873A"/></linearGradient></defs><rect x="3" y="3" width="18"
    height="18" rx="3" fill="url(#node-a)" fill-opacity="0.12"
    stroke="url(#node-a)" stroke-width="1.5"/><path d="M12 6.5L17 9.25v5.5L12
    17.5L7 14.75v-5.5z" stroke="url(#node-a)" stroke-width="1.4"
    stroke-linejoin="round" fill="none"/><path d="M12 11.5v3M10 12.5l2 1l2-1"
    stroke="url(#node-a)" stroke-width="1.4" stroke-linecap="round"
    fill="none"/></svg>
  category: development
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# nodejs-runtime Skill

## L0: One-line Summary

**When to use**: the user needs to install Node.js / upgrade Node / switch Node multi-version / install or configure
npm / pnpm / yarn / troubleshoot `node: command not found`, `npm: command not found`,
EACCES global install permission errors, node-gyp build failures, registry mirror / proxy issues, or other
Node.js runtime problems, or when other skills (pptx using pptxgenjs, etc.) report "Node.js unavailable".

**How**: prefer the DesireCore built-in Volta and follow a four-tier fallback (HTTP API → Volta CLI →
system package manager brew/apt/NodeSource/winget → community options nvm/fnm).

## L1: Overview and Use Cases

### Capability Description

Procedural skill. Before each Node.js environment operation, run `scripts/probe-node.sh` to obtain a JSON snapshot, then choose a path according to the four-tier fallback in `../dev-environment-setup/references/decision-tree.md`.

### Use Cases

- "node not found" / "npm not found"
- The user requests to install/upgrade Node.js
- Multi-version switching (based on `package.json#volta` or `.nvmrc`)
- Install/manage pnpm / yarn / npm
- "EACCES: permission denied" (npm global install permission error)
- Configure registry / proxy
- Other skills (pptx, etc.) report Node.js unavailable

### Core Value

- **DesireCore first**: Volta + HTTP API as L1/L2, avoiding pollution of the system Node
- **JSON-driven decisions**: the probe script outputs structured data that Claude can parse directly
- **package.json#volta compatible**: Volta automatically switches versions per project

## L2: Detailed Specification

### Step 1: Environment Probe (mandatory)

```bash
bash skills/nodejs-runtime/scripts/probe-node.sh > /tmp/node-probe.json
cat /tmp/node-probe.json | jq .
```

See `../dev-environment-setup/references/probe-snapshot.md` for field definitions.

### Step 2: Choose an Execution Path

| Condition | Path |
|------|------|
| `desirecore_api` non-empty | **L1** HTTP API |
| `desirecore_api` empty, `volta_path` non-empty | **L2** Volta CLI |
| Neither of the above | **L3** System package manager (brew / apt / NodeSource / winget) |
| L1–L3 all fail or user explicitly requests | **L4** Community options (nvm / fnm) |

### Step 3: Execute (only the main path is shown; see each reference for details)

#### L1: HTTP API (→ `references/volta-desirecore.md`)

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

#### L2: Volta CLI Absolute Path (→ `references/volta-desirecore.md`)

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

Windows: `%USERPROFILE%\.desirecore\runtime\volta\volta.exe`.

#### L3: System Package Manager

| Platform | Command |
|------|------|
| macOS | `brew install node` |
| Debian/Ubuntu | NodeSource: `curl -fsSL https://deb.nodesource.com/setup_22.x \| sudo -E bash - && sudo apt install nodejs` |
| Fedora/RHEL | `curl -fsSL https://rpm.nodesource.com/setup_22.x \| sudo bash - && sudo dnf install nodejs` |
| Arch | `sudo pacman -S nodejs npm` |
| Windows | `winget install OpenJS.NodeJS.LTS` |

#### L4: nvm / fnm (→ `references/nvm-fallback.md`)

Only enable when explicitly requested by the user or when the above fail.

### Step 4: Package Manager Strategy

See `references/package-managers.md` for details:
- pnpm (recommended, disk-efficient, strict dependencies)
- yarn (Berry / Classic)
- npm (default, ships with Node.js)
- Project-level `package.json#volta` automatic switching

### Step 5: Troubleshooting

See `references/troubleshooting.md` for details:
- npm EACCES permission errors (**do not use sudo npm**)
- registry / proxy configuration
- node-gyp build failures
- "node: command not found" when nvm is installed

## Important Constraints

1. **Never `sudo npm install -g`**: use a user-level prefix or Volta/nvm.
2. **Refresh after modifying the environment**: for L1, call `POST /api/runtime/environment/refresh`; for other paths, re-run the probe.
3. **Cross-skill collaboration**: when `pptx` and others need Node.js, install via this skill's main path; for npm package quick reference, see `../dev-environment-setup/references/office-deps.md`.
4. **Respect package.json#volta**: when this field is detected, prefer Volta — do not switch to nvm.

## References

- Decision tree: `../dev-environment-setup/references/decision-tree.md`
- DesireCore foundation: `../dev-environment-setup/references/desirecore-runtime.md`
- Probe protocol: `../dev-environment-setup/references/probe-snapshot.md`
- Office dependencies (npm packages): `../dev-environment-setup/references/office-deps.md`
