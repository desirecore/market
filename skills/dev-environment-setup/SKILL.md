---
name: dev-environment-setup
description: >-
  Use this skill as a router/index when the user faces a development
  environment question that spans multiple domains: containers
  (Docker/Podman), WSL2 on Windows, office-skill dependencies (DOCX/PDF/XLSX/
  PPTX), or system tools (LibreOffice/Poppler/Pandoc/Tesseract). For pure
  Python issues use python-runtime skill; for pure Node.js issues use
  nodejs-runtime skill. Triggers include: "setup environment", "PATH",
  "WSL", "WSL2", "docker not found", "podman", "container", "office
  dependency", "LibreOffice", "poppler", "pandoc", "tesseract", or any
  cross-cutting environment question. 使用场景：用户提到 环境配置、PATH、
  容器、Docker、Podman、WSL、WSL2、办公依赖、系统工具，或不确定属于 Python /
  Node.js 时的入口指引。
version: 2.0.4
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - environment
  - docker
  - container
  - wsl
  - office
  - system-tools
  - router
metadata:
  author: desirecore
  updated_at: '2026-06-09'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 开发环境综合配置
      short_desc: 开发环境综合入口（容器 / WSL / 办公依赖 / 系统工具）
      description: >-
        Use this skill as a router/index when the user faces a development environment question that spans multiple domains: containers (Docker/Podman), WSL2 on Windows, office-skill dependencies (DOCX/PDF/XLSX/ PPTX), or system tools (LibreOffice/Poppler/Pandoc/Tesseract). For pure Python issues use python-runtime skill; for pure Node.js issues use nodejs-runtime skill. Triggers include: "setup environment", "PATH", "WSL", "WSL2", "docker not found", "podman", "container", "office dependency", "LibreOffice", "poppler", "pandoc", "tesseract", or any cross-cutting environment question. 使用场景：用户提到 环境配置、PATH、 容器、Docker、Podman、WSL、WSL2、办公依赖、系统工具，或不确定属于 Python / Node.js 时的入口指引。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:748e754b5537ea01
      translated_by: human
    en-US:
      name: Dev Environment Setup
      short_desc: Unified dev environment entry (container / WSL / office deps / system tools)
      description: >-
        Use this skill as a router/index when the user faces a development environment question that spans multiple domains: containers (Docker/Podman), WSL2 on Windows, office-skill dependencies (DOCX/PDF/XLSX/ PPTX), or system tools (LibreOffice/Poppler/Pandoc/Tesseract). For pure Python issues use python-runtime skill; for pure Node.js issues use nodejs-runtime skill. Triggers include: "setup environment", "PATH", "WSL", "WSL2", "docker not found", "podman", "container", "office dependency", "LibreOffice", "poppler", "pandoc", "tesseract", or any cross-cutting environment question. Use when the user mentions environment setup, PATH, containers, Docker, Podman, WSL, WSL2, office dependencies, system tools, or needs an entry-point guide when uncertain whether the issue belongs to Python or Node.js.
      body: ./SKILL.md
      source_hash: sha256:748e754b5537ea01
      translated_by: human
      translated_at: '2026-06-09'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="env-a" x1="3" y1="3" x2="21"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#34C759"/><stop
    offset="1" stop-color="#007AFF"/></linearGradient></defs><rect x="3" y="3"
    width="18" height="18" rx="3" fill="url(#env-a)" fill-opacity="0.1"
    stroke="url(#env-a)" stroke-width="1.5"/><path d="M7 8l3 3-3 3"
    stroke="url(#env-a)" stroke-width="1.5" stroke-linecap="round"
    stroke-linejoin="round"/><path d="M13 16h4" stroke="url(#env-a)"
    stroke-width="1.5" stroke-linecap="round"/></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# dev-environment-setup Skill (v2.0.0 router)

## L0: One-line Summary

**When to use**: The user needs to

- Install / troubleshoot **Docker** or **Podman** containers ("docker not found", daemon startup, registry mirror, etc.)
- Configure **WSL2** (Linux Subsystem) on Windows
- One-shot install of **office skill dependencies** (Python packages + npm packages + system tools required by DOCX / PDF / XLSX / PPTX)
- Install **system tools**: LibreOffice / Poppler / Pandoc / Tesseract / qpdf / ImageMagick / Ghostscript / Git
- **Uncertain** whether the issue belongs to Python or Node.js, and a comprehensive diagnosis is needed first

**When not to use**: Use `python-runtime` for pure Python issues, and `nodejs-runtime` for pure Node.js issues.

**How to do it**: First run `scripts/probe.sh` (use `probe.ps1` on Windows) to obtain a system snapshot JSON,
and route to the corresponding references or sub-skill based on the result; this skill is also the source of truth
for DesireCore's built-in Hatch / Volta / HTTP API / Socket.IO integration (`references/desirecore-runtime.md`).

## L1: Routing Rules

Route directly to the corresponding skill or document by the keywords in the user's question:

| Keyword / Scenario | Path |
|--------------|------|
| python / pip / venv / pyenv / hatch / virtualenv / PEP 668 | `python-runtime` skill |
| node / npm / pnpm / yarn / volta / nvm / fnm / EACCES | `nodejs-runtime` skill |
| docker / podman / container / container daemon | `references/container.md` |
| WSL / WSL2 / Windows Linux Subsystem | `references/wsl.md` |
| DOCX / PDF / XLSX / PPTX dependencies / office skill dependencies | `references/office-deps.md` |
| LibreOffice / poppler / pandoc / tesseract / qpdf | `references/system-tools.md` |
| Unsure of category, want a quick diagnosis | First run `scripts/probe.sh` and inspect the JSON |
| DesireCore Hatch / Volta / HTTP API / Socket.IO | `references/desirecore-runtime.md` |
| User edited `.zshrc` / an env var / proxy / `setx`, but tools can't see it | `POST /api/runtime/environment/refresh` reloads the login environment (see `references/desirecore-runtime.md` §7, no app restart needed) |
| Four-tier fallback decision (API → CLI → package manager → community solution) | `references/decision-tree.md` |

## L2: Detailed Specification

### Step 1: Quick Diagnosis

```bash
bash skills/dev-environment-setup/scripts/probe.sh > /tmp/env-probe.json
cat /tmp/env-probe.json | jq .
```

For the meaning of output fields, see `references/probe-snapshot.md`. On Windows use `scripts/probe.ps1`.

### Step 2: Route by Result

- `desirecore_api` non-empty → take the HTTP API path (`references/desirecore-runtime.md`)
- `tools.python3.available = false` or `tools.node.available = false` → enter the corresponding sub-skill
- `tools.docker.available = false` and the user needs containers → `references/container.md`
- `wsl.installed = false` and Windows user → `references/wsl.md`

### Step 3: Execute the Sub-skill Decision Tree

Both `python-runtime` and `nodejs-runtime` have their own four-tier fallback (L1 API → L2 built-in CLI → L3 system package manager → L4 community solution), defined in the shared `references/decision-tree.md`.

### Step 4: Office Skill Dependencies

Quick lookup for the office quartet (DOCX / PDF / XLSX / PPTX) dependencies: `references/office-deps.md`. Includes one-shot install commands for Python packages, npm packages, and system tools.

### Step 5: System Tools

Installation and troubleshooting for LibreOffice / Poppler / Pandoc / Tesseract / qpdf / ImageMagick / Ghostscript: `references/system-tools.md`.

## DesireCore Built-in Environment Management Base

DesireCore embeds Hatch (Python) and Volta (Node.js), providing complete environment management via HTTP API + Socket.IO. This skill and the sub-skills (python/nodejs) all rely on:

| Document | Content |
|------|------|
| `references/desirecore-runtime.md` | Binary path table, HTTP API quick-reference, Socket.IO event contracts, `EnvironmentSnapshot` data structure |
| `references/decision-tree.md` | Four-tier fallback flowchart, concrete signals for failure detection, switch prompts |
| `references/probe-snapshot.md` | Probe script JSON output protocol |

## Important Constraints

1. **Do not write strong keywords like python / node / pip / npm into this skill's description**—those belong to their respective sub-skills, to avoid trigger conflicts.
2. **API first**: `scripts/probe.sh` first checks `${DESIRECORE_ROOT}/agent-service.port`; if it exists, recommend the HTTP API path.
3. **Cache coherence + env reload**: after any install/uninstall completes, call `POST /api/runtime/environment/refresh` to invalidate the cache before subsequent GETs; the same endpoint also reloads login environment variables (re-reads `.zshrc` / registry and precise-syncs into `process.env`), so when a user reports a freshly-changed env var that tools can't see, call it proactively too (no app restart; the returned `envDiff` confirms the changes).
4. **Cross-platform**: every command template provides both macOS / Linux and Windows (PowerShell) versions.

## Sub-skill and Document Manifest

```
skills/
├── python-runtime/        # Python environment (Hatch first)
├── nodejs-runtime/        # Node.js environment (Volta first)
└── dev-environment-setup/         # This skill (composite entry)
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

## Upgrade Notes (v1.x → v2.0.0)

- v1.x was a 1380-line all-in-one manual, now split.
- Python-related → `python-runtime`
- Node.js-related → `nodejs-runtime`
- Docker / WSL / office dependencies / system tools → this skill's `references/`
- DesireCore Hatch / Volta upgraded from "optional community solution" to mandatory L1/L2 primary path

Downstream skills (docx / pdf / xlsx / pptx) should rewrite "for Python environment issues, see dev-environment-setup" to "for Python environment issues, see python-runtime / for Node.js environment issues, see nodejs-runtime".
