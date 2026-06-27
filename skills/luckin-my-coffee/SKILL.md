---
name: luckin-my-coffee
description: >-
  Use this skill when the user needs to work with the packaged Luckin Coffee
  my-coffee skill distribution. This entry records the CDN package source and
  sync workflow.
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - luckin
  - coffee
  - ordering
  - external-skill
license: Packaged distribution; verify package terms before redistribution
metadata:
  author: Luckin Coffee upstream, packaged pointer for DesireCore Market
  updated_at: '2026-06-27'
  upstream:
    type: zip
    url: https://unpkg.luckincoffeecdn.com/@luckin/my-coffee-skill@latest/dist/my-coffee-skill.zip
    license: packaged-distribution
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 瑞幸咖啡 My Coffee Skill
      short_desc: 瑞幸咖啡打包 Skill 分发入口
      description: 指向瑞幸咖啡 my-coffee skill ZIP 分发包，并记录同步方式。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: Luckin My Coffee Skill
      short_desc: Packaged entry for Luckin Coffee my-coffee skill
      description: Points to the Luckin Coffee my-coffee skill ZIP distribution and documents the sync workflow.
      body: ./SKILL.md
      translated_by: human
market:
  category: productivity
  maintainer:
    name: DesireCore Community
    verified: false
  channel: latest
---

# Luckin My Coffee Skill

Use this skill when a user asks to work with Luckin Coffee ordering or
my-coffee skill assets.

Canonical package:
https://unpkg.luckincoffeecdn.com/@luckin/my-coffee-skill@latest/dist/my-coffee-skill.zip

License: packaged distribution. Verify package terms before redistributing
package contents. Ordering operations can create purchases; require explicit
confirmation before placing orders.

## Sync

This market entry is tracked by `scripts/vendor/sync-external-skills.mjs`.
