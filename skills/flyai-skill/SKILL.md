---
name: flyai-skill
description: >-
  Use this skill when the user needs to discover or work with Alibaba FlyAI
  skill assets from the upstream flyai-skill project. This market entry points
  agents to the canonical MIT-licensed upstream and records the sync workflow.
version: 1.0.0
type: procedural
risk_level: medium
status: enabled
tags:
  - alibaba
  - flyai
  - travel
  - external-skill
license: MIT
metadata:
  author: Alibaba FlyAI upstream, packaged for DesireCore Market
  updated_at: '2026-06-27'
  upstream:
    type: git
    url: https://github.com/alibaba-flyai/flyai-skill
    license: MIT
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 飞猪 FlyAI Skill
      short_desc: 阿里 FlyAI / 飞猪相关 Skill 上游入口
      description: 指向 MIT 授权的 Alibaba FlyAI Skill 上游项目，并记录同步方式。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: FlyAI Skill
      short_desc: Upstream entry for Alibaba FlyAI skills
      description: Points to the MIT-licensed Alibaba FlyAI skill upstream and documents the sync workflow.
      body: ./SKILL.md
      translated_by: human
market:
  category: productivity
  maintainer:
    name: DesireCore Community
    verified: false
  channel: latest
---

# FlyAI Skill

Use this skill when a user asks to work with Alibaba FlyAI or Fliggy-related
skills from the upstream project.

Canonical upstream: https://github.com/alibaba-flyai/flyai-skill

License: MIT. Keep upstream license and attribution when vendoring files.

## Sync

This market entry is tracked by `scripts/vendor/sync-external-skills.mjs`.
Run the script to refresh upstream metadata and open a PR when upstream changes.
