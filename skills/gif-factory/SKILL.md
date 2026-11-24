---
name: gif-factory
description: GIF 工厂技能及其五个配套技能的可选 MIT 本地包，用于表情包、光栅卡、动态海报、动态签名、电影片头、文章封面配色、动态绘本及相关风格。收录脚本、字体、模板、参考说明、100
  张色卡和 LICENSE。示例成片和预览图库仍留在固定上游版本，不随包分发。常用表情包导出需要自行准备 Python 3 与 Pillow；仅在可选 MP4 预览时需要
  FFmpeg。本包不附带生图模型或付费服务。
version: 2026.11.24
license: MIT
type: hybrid
risk_level: medium
tags:
- gif
- sticker
- animation
- media
compatibility: Python 3 and Pillow are required for common sticker export. FFmpeg
  is optional, only for MP4 previews. No generative model or paid service is bundled.
metadata:
  author: WoYun520; DesireCore local packaging
  updated_at: '2026-11-24'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
    - en-US
    - zh-CN
    en-US:
      name: GIF Factory
      short_desc: Optional local MIT package of the GIF factory skill and five companions
        for stickers, lenticular cards, motion posters, signatures, film titles, article-cover
        palettes, storybooks and related styles. Scripts, fonts, templates, references,
        the 100 color cards and LICENSE are included. Example renders and preview
        catalogs stay at the pinned upstream and are not shipped. Python 3 and Pillow
        are required for common sticker export; FFmpeg is needed only for optional
        MP4 previews. No generative models or paid services are bundled.
      description: Market-local packaging of WoYun520/gif-factory@e89003a4a6ca4fd0e9e39c8859851b58c82bc368.
        The installer copies only the skill content directory. Package version 2026.11.24.
        See UPSTREAM.md for the same-pin per-file manifest and exclusion reasons.
      body: ./SKILL.md
      translated_by: human
      translated_at: '2026-11-24'
      source_hash: sha256:89725857c8394bfa
    zh-CN:
      name: GIF 工厂
      short_desc: GIF 工厂技能及其五个配套技能的可选 MIT 本地包，用于表情包、光栅卡、动态海报、动态签名、电影片头、文章封面配色、动态绘本及相关风格。收录脚本、字体、模板、参考说明、100
        张色卡和 LICENSE。示例成片和预览图库仍留在固定上游版本，不随包分发。常用表情包导出需要自行准备 Python 3 与 Pillow；仅在可选
        MP4 预览时需要 FFmpeg。本包不附带生图模型或付费服务。
      description: 基于 WoYun520/gif-factory@e89003a4a6ca4fd0e9e39c8859851b58c82bc368
        的市场本地包装。安装器只复制技能内容目录。包版本 2026.11.24。同 pin 的逐文件清单与排除理由见 UPSTREAM.md。
      body: ./SKILL.zh-CN.md
      translated_by: human
      translated_at: '2026-11-24'
      source_hash: sha256:89725857c8394bfa
market:
  icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0
    0 24 24" fill="none"><rect x="4" y="5" width="16" height="14" rx="2" stroke="#2563EB"
    stroke-width="1.7"/><path d="M8 12h2l1.5-2 2 4 1.5-2H16" stroke="#2563EB" stroke-width="1.7"
    stroke-linecap="round" stroke-linejoin="round"/></svg>
  category: media
  maintainer:
    name: mashagua
    url: https://github.com/mashagua
    verified: true
  channel: latest
---

# GIF Factory

## Scope and provenance

This optional local MIT package contains the GIF factory skill, its five companion skills, scripts, fonts, templates, references, the 100 article-cover color cards, paper-mechanism visual references, and [LICENSE](LICENSE) in the installed tree. See [UPSTREAM.md](UPSTREAM.md) and [references/market-packaging.md](references/market-packaging.md).

The verbatim upstream skill text is at [references/upstream-skill.md](references/upstream-skill.md). The catalog slug is `gif-factory`; the upstream frontmatter name was `pixel-gif-sticker-pack`.

Example renders, `GALLERY.md`, `docs/` previews, and rendered style-catalog / english-title / signature / film-title previews are **not** in this package. They remain at the pinned upstream commit `e89003a4a6ca4fd0e9e39c8859851b58c82bc368`.

## Prerequisites

- Python 3 and Pillow in a private environment for common sticker export (`export_pack.py` and related scripts)
- FFmpeg only if you use `--preview` to write an MP4
- A DesireCore-compatible client
- The optional external `lemo-opuscar` skill is not bundled; install it separately if you follow that paper-mechanism workflow
- This package does not bundle a generative model or a paid service
