---
name: wecom-cli
description: >-
  Use this skill when the user needs to work with the WeCom CLI upstream project
  or Enterprise WeChat automation assets. This entry records the canonical
  MIT-licensed upstream and sync workflow.
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - wecom
  - enterprise-wechat
  - cli
  - external-skill
license: MIT
metadata:
  author: WeCom upstream, packaged for DesireCore Market
  updated_at: '2026-06-27'
  upstream:
    type: git
    url: https://github.com/WecomTeam/wecom-cli
    license: MIT
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 企业微信 CLI
      short_desc: 企业微信 CLI 上游入口
      description: 指向 MIT 授权的企业微信 CLI 上游项目，并记录同步方式。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: WeCom CLI
      short_desc: Upstream entry for WeCom CLI
      description: Points to the MIT-licensed WeCom CLI upstream and documents the sync workflow.
      body: ./SKILL.md
      translated_by: human
market:
  category: communication
  maintainer:
    name: DesireCore Community
    verified: false
  channel: latest
---

# WeCom CLI

Use this skill when a user asks to work with WeCom / Enterprise WeChat CLI
automation.

Canonical upstream: https://github.com/WecomTeam/wecom-cli

License: MIT. Enterprise messaging and organization operations are high impact;
confirm credentials and mutation intent before executing upstream commands.

## Sync

This market entry is tracked by `scripts/vendor/sync-external-skills.mjs`.
