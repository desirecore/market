---
name: netease-skills
description: >-
  Use this skill when the user needs to reference the NetEase skills upstream.
  The upstream currently has no declared license, so this market entry is a
  source pointer only and does not vendor upstream code.
version: 1.0.0
type: procedural
risk_level: medium
status: enabled
tags:
  - netease
  - music
  - external-skill
  - source-pointer
license: Upstream license not declared
metadata:
  author: NetEase upstream, source pointer packaged for DesireCore Market
  updated_at: '2026-06-27'
  upstream:
    type: git
    url: https://github.com/NetEase/skills
    license: not-declared
    redistribution: source-pointer-only
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 网易云音乐 Skills 入口
      short_desc: 网易 Skills 上游来源指针
      description: 指向未声明 license 的 NetEase Skills 上游；本仓库不复制其源码。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: NetEase Skills
      short_desc: Source pointer for the NetEase skills upstream
      description: Points to the unlicensed NetEase skills upstream without vendoring source code.
      body: ./SKILL.md
      translated_by: human
market:
  category: media
  maintainer:
    name: DesireCore Community
    verified: false
  channel: latest
---

# NetEase Skills

Use this entry only as a pointer to the upstream project.

Canonical upstream: https://github.com/NetEase/skills

License: not declared upstream. Do not copy or redistribute upstream code in
this repository unless maintainers obtain permission or upstream adds a
compatible license.

## Sync

`scripts/vendor/sync-external-skills.mjs` tracks upstream metadata only.
