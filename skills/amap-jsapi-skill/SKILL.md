---
name: amap-jsapi-skill
description: >-
  Use this skill when the user needs to work with the AMap JSAPI skill entry
  published on ClawHub. This entry records the canonical MIT-0 source page and
  sync workflow.
version: 1.0.0
type: procedural
risk_level: medium
status: enabled
tags:
  - amap
  - maps
  - lbs
  - external-skill
license: MIT-0
metadata:
  author: ClawHub upstream, packaged for DesireCore Market
  updated_at: '2026-06-27'
  upstream:
    type: web
    url: https://clawhub.ai/lbs-amap/skills/amap-jsapi-skill
    license: MIT-0
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 高德地图 JSAPI Skill
      short_desc: 高德地图 JSAPI Skill 上游入口
      description: 指向 MIT-0 授权的 ClawHub 高德地图 JSAPI Skill 页面，并记录同步方式。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: AMap JSAPI Skill
      short_desc: Upstream entry for the AMap JSAPI skill
      description: Points to the MIT-0 ClawHub AMap JSAPI skill page and documents the sync workflow.
      body: ./SKILL.md
      translated_by: human
market:
  category: productivity
  maintainer:
    name: DesireCore Community
    verified: false
  channel: latest
---

# AMap JSAPI Skill

Use this skill when a user asks to work with AMap / Gaode Maps JSAPI skill
assets.

Canonical upstream: https://clawhub.ai/lbs-amap/skills/amap-jsapi-skill

License: MIT-0 according to the upstream listing. Verify API key and platform
terms before making live calls.

## Sync

This market entry is tracked by `scripts/vendor/sync-external-skills.mjs`.
