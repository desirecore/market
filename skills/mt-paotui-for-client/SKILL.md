---
name: mt-paotui-for-client
description: >-
  Use this skill when the user needs to reference the Meituan Paotui client
  upstream. The upstream currently has no declared license, so this market entry
  is a source pointer only and does not vendor upstream code.
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - meituan
  - delivery
  - paotui
  - source-pointer
license: Upstream license not declared
metadata:
  author: Meituan upstream, source pointer packaged for DesireCore Market
  updated_at: '2026-06-27'
  upstream:
    type: git
    url: https://github.com/meituan/MT-Paotui-For-Client
    license: not-declared
    redistribution: source-pointer-only
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 美团跑腿客户端入口
      short_desc: 美团跑腿客户端上游来源指针
      description: 指向未声明 license 的美团跑腿客户端上游；本仓库不复制其源码。
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: Meituan Paotui Client
      short_desc: Source pointer for the Meituan Paotui client upstream
      description: Points to the unlicensed Meituan Paotui client upstream without vendoring source code.
      body: ./SKILL.md
      translated_by: human
market:
  category: business
  maintainer:
    name: DesireCore Community
    verified: false
  channel: latest
---

# Meituan Paotui Client

Use this entry only as a pointer to the upstream project.

Canonical upstream: https://github.com/meituan/MT-Paotui-For-Client

License: not declared upstream. Do not copy or redistribute upstream code in
this repository unless maintainers obtain permission or upstream adds a
compatible license.

## Sync

`scripts/vendor/sync-external-skills.mjs` tracks upstream metadata only.
