---
name: wechatpay-skills
description: >-
  Use this skill when the user needs to work with the official WeChat Pay API v3
  skills upstream. This entry records the canonical MIT-licensed upstream and
  sync workflow.
version: 1.0.0
type: procedural
risk_level: critical
status: enabled
tags:
  - wechat-pay
  - payment
  - finance
  - external-skill
license: MIT
metadata:
  author: WeChat Pay upstream, packaged for DesireCore Market
  updated_at: '2026-06-27'
  upstream:
    type: git
    url: https://github.com/wechatpay-apiv3/wechatpay-skills
    license: MIT
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 微信支付 Skills
      short_desc: 微信支付 API v3 Skills 上游入口
      description: 指向 MIT 授权的微信支付 Skills 上游项目，并记录同步方式。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: WeChat Pay Skills
      short_desc: Upstream entry for WeChat Pay API v3 skills
      description: Points to the MIT-licensed WeChat Pay skills upstream and documents the sync workflow.
      body: ./SKILL.md
      translated_by: human
market:
  category: business
  maintainer:
    name: DesireCore Community
    verified: false
  channel: latest
---

# WeChat Pay Skills

Use this skill when a user asks to work with WeChat Pay API v3 skill assets.

Canonical upstream: https://github.com/wechatpay-apiv3/wechatpay-skills

License: MIT. Payment operations are critical risk; never proceed with live
payment, refund, or merchant mutation workflows without explicit confirmation
and properly scoped credentials.

## Sync

This market entry is tracked by `scripts/vendor/sync-external-skills.mjs`.
