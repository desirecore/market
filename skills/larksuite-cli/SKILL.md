---
name: larksuite-cli
description: >-
  Use this skill when the user needs to work with the Lark / Feishu CLI
  upstream project. This entry records the canonical MIT-licensed upstream and
  sync workflow.
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - lark
  - feishu
  - cli
  - external-skill
license: MIT
metadata:
  author: Lark Suite upstream, packaged for DesireCore Market
  updated_at: '2026-06-27'
  upstream:
    type: git
    url: https://github.com/larksuite/cli
    license: MIT
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 飞书 CLI
      short_desc: 飞书 / Lark CLI 上游入口
      description: 指向 MIT 授权的飞书 CLI 上游项目，并记录同步方式。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: Lark Suite CLI
      short_desc: Upstream entry for Lark / Feishu CLI
      description: Points to the MIT-licensed Lark Suite CLI upstream and documents the sync workflow.
      body: ./SKILL.md
      translated_by: human
market:
  category: communication
  maintainer:
    name: DesireCore Community
    verified: false
  channel: latest
---

# Lark Suite CLI

Use this skill when a user asks to work with Lark / Feishu CLI automation.

Canonical upstream: https://github.com/larksuite/cli

License: MIT. Confirm tenant, app credentials, and mutation intent before
running commands that affect Feishu resources.

## Sync

This market entry is tracked by `scripts/vendor/sync-external-skills.mjs`.
