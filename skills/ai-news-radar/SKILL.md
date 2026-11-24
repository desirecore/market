---
name: ai-news-radar
description: Generate AI daily-brief JSON with a complete MIT Python package. Requires Python 3.11+, dependencies and feed
  access; optional mail/API sources need separate authorization.
version: 2026.11.24
license: MIT
type: hybrid
risk_level: medium
disable-model-invocation: true
tags:
- ai-news
- rss
- learnprompt
compatibility: Python 3.11+, requirements.txt, authorized feed access, and a private writable output directory outside this
  skill. Optional email/API integrations require separate authorization and may incur service fees.
metadata:
  author: LearnPrompt; DesireCore local packaging
  updated_at: '2026-11-24'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
    - en-US
    - zh-CN
    en-US:
      name: AI News Radar
      short_desc: Generate AI daily-brief JSON with a complete MIT Python package. Requires Python 3.11+, dependencies and
        feed access; optional mail/API sources need separate authorization.
      description: Optional local MIT edition based on LearnPrompt/ai-news-radar@689395109cc962a27c369bdd6fa50d1e090eb319.
        Includes generation scripts, feed example, glossary, source-analysis helper, referenced docs and reader assets. Outputs
        belong outside the installed skill; external services and optional credentials are separately configured.
      body: ./SKILL.md
      translated_by: ai:grok-bot
      translated_at: '2026-11-24'
      source_hash: sha256:870dccded1b7c11b
    zh-CN:
      name: AI 资讯雷达
      short_desc: 完整 MIT 本地包生成 AI 日报 JSON。需 Python 3.11+、依赖和信源访问；可选邮件/API 集成须独立授权。
      description: 基于 LearnPrompt/ai-news-radar@689395109cc962a27c369bdd6fa50d1e090eb319 的可选 MIT 本地版，包含生成脚本、信源示例、词表、分析工具、引用文档和阅读器资源。运行结果须写入安装目录之外；外部服务与可选凭据需单独配置。
      body: ./SKILL.zh-CN.md
      translated_by: ai:grok-bot
      translated_at: '2026-11-24'
      source_hash: sha256:870dccded1b7c11b
market:
  icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16"
    height="16" rx="2" stroke="#2563EB" stroke-width="1.7"/><path d="M8 8h5m-5 4h8m-8 4h5" stroke="#2563EB" stroke-width="1.7"
    stroke-linecap="round"/><circle cx="17" cy="8" r="1.5" fill="#2563EB"/></svg>
  category: productivity
  maintainer:
    name: mashagua
    url: https://github.com/mashagua
    verified: true
  channel: latest
---

# AI News Radar

## Scope and provenance

Generate AI daily-brief JSON from the complete local Python package, review public source quality, and optionally inspect the bundled reader assets. Read [package notes](README.md), [provenance and license](UPSTREAM.md), and [source intake](references/source-intake.md). This is a maintained MIT local edition based only on LearnPrompt/ai-news-radar commit `689395109cc962a27c369bdd6fa50d1e090eb319`; package version `2026.11.24` is not an upstream release. It is optional marketplace content, not an automatically installed builtin.

## Prerequisites and boundaries

Require Python 3.11+, `uv` or an equivalent private Python environment, the pinned packages in [requirements.txt](requirements.txt), and access to the user's selected public feeds. Dependency downloads and normal generation require network access; upstream websites can fail, change terms, or rate-limit requests. Report source failures honestly. Do not claim a live feed, authenticated service, deployment, or email test passed merely because installation or the offline fixture passed.

Keep the installed directory read-only. Use [the safe launcher](scripts/run_daily_brief.py), which requires an absolute output directory outside the skill and suppresses bytecode writes. The unchanged [upstream generator](scripts/update_news.py) defaults to a relative output path; do not run its default command inside the skill. Never write a virtual environment, private OPML, generated data, logs, tokens, cookies, or email bodies into the installed skill or public repository.

## Prepare a private run

Set `SKILL_DIR` to the absolute installed directory, then choose a private working directory outside it. The following creates a fresh temporary working directory; use a private persistent directory instead when retention is wanted.

```bash
RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ai-news-radar.XXXXXX")"
export SKILL_DIR RUN_DIR
cp "$SKILL_DIR/feeds/follow.example.opml" "$RUN_DIR/follow.opml"
uv run --with-requirements "$SKILL_DIR/requirements.txt" python -B "$SKILL_DIR/scripts/update_news.py" --help
```

Ask which sources the user wants. Edit only the private OPML copy, using the bundled [example OPML](feeds/follow.example.opml); do not collect credentials in chat. The supplied OPML is a public example, not the user's subscription list.

## Generate the daily brief

```bash
uv run --with-requirements "$SKILL_DIR/requirements.txt" python -B "$SKILL_DIR/scripts/run_daily_brief.py" --output-dir "$RUN_DIR/data" --window-hours 24 --rss-opml "$RUN_DIR/follow.opml"
```

Read the generated daily brief, latest 24-hour items, and source-status JSON in the chosen output directory. Those are generated outputs, not missing bundled resources. Empty history is supported; large upstream historical archives and translation caches are deliberately not shipped. [AI relevance](scripts/ai_relevance.py) and the optional [translation glossary](translation-glossary.txt) are included. The offline smoke test is fixture-based and does not establish current public-feed availability.

## Review a candidate source

Follow [source intake](references/source-intake.md) and [product method](references/v2-method.md). Prefer official RSS/Atom or public generated feeds over fragile scraping. [The overlap helper](scripts/evaluate_source_overlap.py) is included; use the generated archive in the private output directory as its baseline and save the advisory report outside the skill. A low overlap score is not proof of source quality or permission to scrape.

## Optional local reader

The [reader page](index.html), [reader code](assets/app.js), and [styles](assets/styles.css) are bundled with their local static dependencies. To preview, copy the page and assets into a private working site, generate its data there, and serve only that directory. Never start a server rooted in the installed skill or publish private outputs automatically. Reader screenshots and historical datasets are not runtime dependencies. The reader includes the classic view and web manifest; its optional GSAP animation script comes from jsDelivr under its separate terms and needs network access. For optional persona commentary, [the scorer](scripts/persona_score.py) and [persona definitions](personas/README.md) are included: use explicit private data and bundled persona directories. Set `PERSONA_ENABLED=0` for rules-only scoring; do not enable a paid DeepSeek API run without separate authorization and private credentials. The daily generator does not automatically run the scorer.

## Optional private integrations

Email, X, cookie-based sources and paid APIs are optional, separately authorized integrations, not bundled accounts or free service entitlements. Keep email disabled unless the user explicitly authorizes it (`EMAIL_DIGEST_ENABLED=1`); leave publication disabled. Use private host/vault configuration for credentials, never chat, history-token reuse, public files or logs. Obtain confirmation before any publication, email sending, account change, or charge. This skill's default task is read-only collection, not sending mail. Stop before an unavailable or unauthorized integration; do not fabricate success.

## Reference material and validation

The upstream [project guide](references/upstream-project-readme.md), [English guide](references/upstream-project-readme.en.md), [skill guide](references/upstream-skill-readme.md), [handoff notes](docs/GPT_HANDOFF.md), [source coverage](docs/SOURCE_COVERAGE.md), [roadmap](docs/ROADMAP.md), and [product brief](docs/V2_PRODUCT_BRIEF.md) are included as reference material. Their upstream development tests, external skill-creator tools, hosted site, GitHub Actions and publication workflows are not installed or invoked by this edition. Do not run upstream workflow/deployment instructions without a separate user request. Retain the verbatim [MIT license](LICENSE) and LearnPrompt attribution when redistributing.
