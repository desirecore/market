---
name: stickman-video-director
description: 火柴人视频导演技能的可选 MIT 本地包，收录脚本、字体、许可证、风格样板和目录。B 模式配乐音频、B6 风格锁定参考视频、B6 绘制底板，以及已批准的
  B8 参考/回放包不随包分发；需按固定 URL 与 SHA-256 清单按需下载。下载脚本不会自动运行，也不会执行下载的文件。本地代码引擎渲染器需要 Node.js
  20+ 和已声明的 npm 依赖。
version: 2026.11.24
license: MIT
type: hybrid
risk_level: high
tags:
- animation
- video
- stickman
- youtube
compatibility: Node.js 20+ and declared npm packages are required for the local Code
  Engine renderer. Some B-mode scripts need Python. Large audio/video libraries are
  fetched on demand only.
metadata:
  author: kaomei; DesireCore local packaging
  updated_at: '2026-11-24'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
    - en-US
    - zh-CN
    en-US:
      name: Stickman Video Director
      short_desc: Optional local MIT package of the stickman video director skill,
        with scripts, fonts, licenses, style boards and catalogs. B-mode soundtrack
        audio, B6 style-lock reference videos, the B6 paint kit and the approved B8
        reference/replay packs are not shipped; fetch them on demand from pin-fixed
        URLs with SHA-256 checks. The fetch script is never run automatically and
        does not execute downloads. Node.js 20+ and the declared npm packages are
        required for the local Code Engine renderer.
      description: Market-local packaging of kaomei/stickman-video-director@10287822ba47579321068da1b93801face9160dd
        path skills/directing-stickman-videos, with the repository-root MIT LICENSE
        copied into the installed content directory. Package version 2026.11.24. On-demand
        asset groups and exclusion reasons are recorded in UPSTREAM.md and references/fetch-manifest.json.
      body: ./SKILL.md
      translated_by: human
      translated_at: '2026-11-24'
      source_hash: sha256:4270a91d21e53ac2
    zh-CN:
      name: 火柴人视频导演
      short_desc: 火柴人视频导演技能的可选 MIT 本地包，收录脚本、字体、许可证、风格样板和目录。B 模式配乐音频、B6 风格锁定参考视频、B6
        绘制底板，以及已批准的 B8 参考/回放包不随包分发；需按固定 URL 与 SHA-256 清单按需下载。下载脚本不会自动运行，也不会执行下载的文件。本地代码引擎渲染器需要
        Node.js 20+ 和已声明的 npm 依赖。
      description: 基于 kaomei/stickman-video-director@10287822ba47579321068da1b93801face9160dd
        路径 skills/directing-stickman-videos 的市场本地包装，并把仓库根目录 MIT LICENSE 放入安装内容目录。包版本
        2026.11.24。按需资源分组与排除理由见 UPSTREAM.md 和 references/fetch-manifest.json。
      body: ./SKILL.zh-CN.md
      translated_by: human
      translated_at: '2026-11-24'
      source_hash: sha256:4270a91d21e53ac2
market:
  icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0
    0 24 24" fill="none"><circle cx="12" cy="5" r="2" stroke="#2563EB" stroke-width="1.7"/><path
    d="M12 7v6M9 10h6M12 13l-3 6M12 13l3 6" stroke="#2563EB" stroke-width="1.7" stroke-linecap="round"/></svg>
  category: media
  maintainer:
    name: mashagua
    url: https://github.com/mashagua
    verified: true
  channel: latest
---

# Stickman Video Director

## Scope and provenance

This optional local MIT package contains the stickman video director skill, its scripts and references, fonts and OFL licenses, the audio-library catalog and license evidence, style boards that fit this slim snapshot, and [LICENSE](LICENSE) in the installed tree. See [UPSTREAM.md](UPSTREAM.md) and [references/market-packaging.md](references/market-packaging.md).

The verbatim upstream skill text is at [references/upstream-skill.md](references/upstream-skill.md). The catalog slug is `stickman-video-director`; the upstream frontmatter name was `directing-stickman-videos`.

## On-demand assets (explicit trigger only)

The following groups are necessary for the named B-mode work but are not installed with the package:

- `required-for-B-audio` — soundtrack binaries under `assets/b-audio-library/audio/`
- `required-before-B6` — B6 style-lock reference videos, including the Eiffel V44 standard, under `assets/b6/reference/`
- `required-for-B6-paint` — default paint-kit plates under `assets/b6/paint/`
- `required-before-B8` — approved B8 visual references and the portable replay pack under `assets/b8/`

Fetch them only by running [scripts/fetch-optional-assets.py](scripts/fetch-optional-assets.py) with [references/fetch-manifest.json](references/fetch-manifest.json). The script uses pin-fixed `raw.githubusercontent.com` URLs, verifies SHA-256, does not execute downloads, and is not started by install. Write the files to an absolute directory **outside** this skill, then copy or symlink the `assets/` tree back.

README demos, skill examples, public showcases, B5 local baselines and B6 Hong Kong work-in-progress example productions are excluded and remain at the pinned commit.

## Prerequisites

- Node.js 20 or newer, then install the declared packages in `package.json` (`@napi-rs/canvas`, `sharp`) in a private environment when you use the local Code Engine renderer
- Python 3 for some B-mode helper scripts, including packages listed in `scripts/requirements-b8.txt` when you use that workflow
- Configured generation tools as described by the upstream skill; this package does not bundle paid APIs or auto-run untrusted remote code
- A DesireCore-compatible client
