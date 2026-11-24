---
name: pixelfx
description: Optional local MIT package of the pixelfx skill for making pixel-art
  effects. The effect library and Node tools stay in the same MIT repo and must be
  checked out separately. gallery/fonts is not covered by the repo MIT license and
  is not in this package. Optional pch CLI install uses a remote script and needs
  operator review.
version: 2026.11.24
license: MIT
type: hybrid
risk_level: high
tags:
- pixel-art
- vfx
- gamedev
- sprites
compatibility: Requires a separate checkout of the pixelfx library and Node tools;
  optional pch install is a remote script that must be reviewed before use.
metadata:
  author: patch-gg; DesireCore local packaging
  updated_at: '2026-11-24'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
    - en-US
    - zh-CN
    en-US:
      name: pixelfx
      short_desc: Optional local MIT package of the pixelfx skill for making pixel-art
        effects. The effect library and Node tools stay in the same MIT repo and must
        be checked out separately. gallery/fonts is not covered by the repo MIT license
        and is not in this package. Optional pch CLI install uses a remote script
        and needs operator review.
      description: Market-local packaging of patch-gg/pixelfx@5294518ce7c72e48b6100a744596e0acf57f2826
        path skills/pixelfx, with the upstream MIT LICENSE and NOTICE.md placed in
        the installed tree (the installer copies only this content directory). The
        effect library is not vendored here. Package version 2026.11.24.
      body: ./SKILL.md
      translated_by: human
      translated_at: '2026-11-24'
      source_hash: sha256:a6719a3de00a827d
    zh-CN:
      name: pixelfx
      short_desc: 用 pixelfx 制作像素特效的可选 MIT 本地技能包。特效库和 Node 工具在同一 MIT 仓库中，需另行检出。gallery/fonts
        不受仓库 MIT 许可覆盖，也不在本包内。可选 pch CLI 通过远程脚本安装，需操作者自行审核。
      description: 基于 patch-gg/pixelfx@5294518ce7c72e48b6100a744596e0acf57f2826 路径
        skills/pixelfx 的市场本地包装，把上游 MIT LICENSE 与 NOTICE.md 放进安装产物（安装器只复制本内容目录）。特效库不在本包中。包版本
        2026.11.24。
      body: ./SKILL.zh-CN.md
      translated_by: human
      translated_at: '2026-11-24'
      source_hash: sha256:a6719a3de00a827d
market:
  icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0
    0 24 24" fill="none"><rect x="4" y="4" width="6" height="6" stroke="#2563EB" stroke-width="1.7"/><rect
    x="14" y="4" width="6" height="6" stroke="#2563EB" stroke-width="1.7"/><rect x="4"
    y="14" width="6" height="6" stroke="#2563EB" stroke-width="1.7"/><rect x="14"
    y="14" width="6" height="6" stroke="#2563EB" stroke-width="1.7"/></svg>
  category: creative
  maintainer:
    name: mashagua
    url: https://github.com/mashagua
    verified: true
  channel: latest
---
# pixelfx

## Scope and provenance

This optional local package contains the pixelfx Agent Skill, the upstream MIT [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md). See [UPSTREAM.md](UPSTREAM.md) for the pinned commit and file hashes.

The effect library, Node tools and other repository code are **not** in this package; check them out separately from the same MIT pin if you need them. `gallery/fonts` is outside the repository MIT license and is not included.

The optional pch CLI is installed by a remote script only if you choose to run it; review that script yourself. This package does not run remote scripts.

Follow the verbatim upstream skill at [references/upstream-skill.md](references/upstream-skill.md) for how to use the library after you have it locally.

## Prerequisites and risks

- A runtime that can load this skill
- A separate checkout of the pixelfx library and Node tools from pin `5294518ce7c72e48b6100a744596e0acf57f2826` when you need to build effects
- Operator review before any `curl | sh` or similar pch install
