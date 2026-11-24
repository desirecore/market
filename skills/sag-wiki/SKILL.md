---
name: sag-wiki
description: Optional local MIT package of the SAG CLI skill for setup, semantic search,
  indexed folders, ignore rules and MCP configuration. Requires the separately licensed
  @zleap-ai/sag CLI; this package is only the skill files plus the upstream root LICENSE,
  not the full SAG Wiki app.
version: 2026.11.24
license: MIT
type: procedural
risk_level: medium
tags:
- knowledge-base
- search
- cli
- mcp
compatibility: Requires the separately licensed @zleap-ai/sag CLI and a runtime that
  can load this skill.
metadata:
  author: Zleap-AI; DesireCore local packaging
  updated_at: '2026-11-24'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
    - en-US
    - zh-CN
    en-US:
      name: SAG Wiki Skill
      short_desc: Optional local MIT package of the SAG CLI skill for setup, semantic
        search, indexed folders, ignore rules and MCP configuration. Requires the
        separately licensed @zleap-ai/sag CLI; this package is only the skill files
        plus the upstream root LICENSE, not the full SAG Wiki app.
      description: Independently maintained market packaging of Zleap-AI/SAG-Wiki@b6940ac834b3b1ec651c0b49dc1b0c45d4d74c4a
        path cli/skills/sag. The real DesireCore installer copies only the skill content
        directory and does not pull a parent LICENSE, so this package places the upstream
        MIT LICENSE in the installed tree. Package version 2026.11.24.
      body: ./SKILL.md
      translated_by: human
      translated_at: '2026-11-24'
      source_hash: sha256:b25843cf983c7653
    zh-CN:
      name: SAG Wiki 技能
      short_desc: SAG CLI 技能的可选 MIT 本地包，用于安装配置、语义检索、索引目录、忽略规则和 MCP。需另行安装并运行独立许可的 @zleap-ai/sag
        CLI；本包只含技能文件和上游根 LICENSE，不含完整 SAG Wiki 应用。
      description: 基于 Zleap-AI/SAG-Wiki@b6940ac834b3b1ec651c0b49dc1b0c45d4d74c4a 路径
        cli/skills/sag 的市场本地包装。真实 DesireCore 安装器只复制技能内容目录，不会自动带上父目录 LICENSE，因此本包把上游
        MIT LICENSE 放进安装产物。包版本 2026.11.24。
      body: ./SKILL.zh-CN.md
      translated_by: human
      translated_at: '2026-11-24'
      source_hash: sha256:b25843cf983c7653
market:
  icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0
    0 24 24" fill="none"><path d="M5 5h14v14H5z" stroke="#2563EB" stroke-width="1.7"
    stroke-linejoin="round"/><path d="M8 9h8M8 12h8M8 15h5" stroke="#2563EB" stroke-width="1.7"
    stroke-linecap="round"/></svg>
  category: productivity
  maintainer:
    name: mashagua
    url: https://github.com/mashagua
    verified: true
  channel: latest
---
# SAG Wiki Skill

## Scope and provenance

This is an optional local MIT edition of the upstream Agent Skill at `cli/skills/sag`. Read [UPSTREAM.md](UPSTREAM.md) for the pinned commit, per-file hashes and the reason the root LICENSE is copied into this package. The catalog directory is `sag-wiki`; the upstream frontmatter name was `sag`.

Install and run the separately licensed `@zleap-ai/sag` CLI yourself. This package does not include the SAG Wiki application, demo videos or third-party binaries from the rest of the repository.

The verbatim upstream skill text is at [references/upstream-skill.md](references/upstream-skill.md). Follow those setup, search, ignore-rule and MCP instructions after the CLI is installed.

## Prerequisites

- A supported Agent runtime that can load this skill
- The `@zleap-ai/sag` CLI, installed and licensed separately
- Any MCP or folder-index configuration described in the upstream skill references
