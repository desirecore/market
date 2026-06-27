---
name: dingtalk-api
description: >-
  Use this skill when the user needs to work with the DingTalk API skill entry
  published on ClawHub. This entry records the canonical MIT-0 source page and
  sync workflow.
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - dingtalk
  - collaboration
  - api
  - external-skill
license: MIT-0
metadata:
  author: ClawHub upstream, packaged for DesireCore Market
  updated_at: '2026-06-27'
  upstream:
    type: web
    url: https://clawhub.ai/ogenes/skills/dingtalk-api
    license: MIT-0
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 钉钉 API Skill
      short_desc: 钉钉 API Skill 上游入口
      description: 指向 MIT-0 授权的 ClawHub 钉钉 API Skill 页面，并记录同步方式。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: DingTalk API Skill
      short_desc: Upstream entry for the DingTalk API skill
      description: Points to the MIT-0 ClawHub DingTalk API skill page and documents the sync workflow.
      body: ./SKILL.md
      translated_by: human
market:
  category: communication
  maintainer:
    name: DesireCore Community
    verified: false
  channel: latest
---

# DingTalk API Skill

Use this skill when a user asks to work with DingTalk API skill assets.

Canonical upstream: https://clawhub.ai/ogenes/skills/dingtalk-api

License: MIT-0 according to the upstream listing. Confirm tenant, app
credentials, and mutation intent before executing write operations.

## Sync

This market entry is tracked by `scripts/vendor/sync-external-skills.mjs`.
