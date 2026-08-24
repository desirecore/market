---
name: web-access
description: >-
  Use this skill whenever the user needs to access information from the internet
  — searching for current information, fetching public web pages, browsing
  login-gated sites (微博/小红书/B站/飞书/Twitter), comparing products,
  researching topics, gathering documentation, or summarizing news.
  This skill orchestrates four complementary layers: (1) WebSearch + WebFetch
  for public pages, (2) Jina Reader as the default token-optimization layer for
  heavy/JS-rendered pages, and (3) the governed built-in browser (isolated
  BrowserSpace + Cookie import + bulk text extraction + waits + code mode) to
  reach, interact with, and read login-gated sites, and (4) the user's own Chrome over CDP when they ask for it by name. Always cite source URLs.
  Use when 用户提到 联网搜索、上网查、
  查资料、抓取网页、研究、调研、最新资讯、文档查询、对比、竞品、技术文档、
  新闻、网址、URL、找一下、搜一下、查一下、小红书、B站、微博、飞书、Twitter、
  推特、X、知乎、公众号、已登录、登录状态。
license: Complete terms in LICENSE.txt
version: 3.2.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - web
  - search
  - fetch
  - research
  - browsing
  - browser
  - cdp
provides:
  tools:
    - BrowserManage
    - BrowserSnapshot
    - BrowserAct
    - BrowserScript
    - BrowserImport
    - BrowserShare
    - SitePatternRead
    - SitePatternWrite
    - LocalBookmarks
metadata:
  author: desirecore
  updated_at: '2026-08-21'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 联网访问
      short_desc: 联网搜索、网页抓取、内置受管浏览器登录态访问与取文、研究调研工作流
      description: 联网访问工具包——搜索公开页面、Jina 优化抓取、内置受管浏览器完成登录态访问与取文，以及用户点名时接管他自己的 Chrome。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:4d3bc4221b2d6b09
      translated_by: human
    en-US:
      name: Web Access
      short_desc: Web search, page fetching, logged-in access via the governed built-in browser, research workflows
      description: A web-access toolkit — search public pages, fetch heavy pages via Jina Reader, reach and read logged-in sites through the governed built-in browser, and drive the user's own Chrome over CDP on request.
      body: ./SKILL.md
      source_hash: sha256:4d3bc4221b2d6b09
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="wa-a" x1="2" y1="2" x2="20"
    y2="20" gradientUnits="userSpaceOnUse"><stop stop-color="#007AFF"/><stop
    offset="1" stop-color="#34C759"/></linearGradient></defs><circle cx="10"
    cy="10" r="8" fill="url(#wa-a)" fill-opacity="0.1" stroke="url(#wa-a)"
    stroke-width="1.5"/><ellipse cx="10" cy="10" rx="3.5" ry="8"
    stroke="url(#wa-a)" stroke-width="1"
    stroke-opacity="0.35"/><path d="M2 10h16" stroke="url(#wa-a)"
    stroke-width="1" stroke-opacity="0.35"/><path d="M10 2v16"
    stroke="url(#wa-a)" stroke-width="1" stroke-opacity="0.35"/><circle cx="18.5"
    cy="18.5" r="2.5" stroke="#34C759" stroke-width="1.5" fill="#34C759"
    fill-opacity="0.12"/><path d="M20.5 20.5l2 2" stroke="#34C759"
    stroke-width="1.8" stroke-linecap="round"/></svg>
  category: research
  required_client_version: 10.0.98
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# web-access skill

## L0: One-line Summary

A web-access toolkit — search public pages, optimize fetches via Jina Reader, reach/interact with/read login-gated sites through the governed built-in browser, and drive the user's own Chrome over CDP when they ask for it by name.

## L1: Overview & Use Cases

### Capability

web-access is a **procedural skill** that provides four complementary layers of web access:

- **L1** (WebSearch + WebFetch): public, static pages
- **L2** (Jina Reader): JS-rendered heavy pages, saving tokens by default
- **L3** (governed built-in browser, capability surface completed in v3.0): reach, *interact with*, and **read** logged-in / interactive sites — isolated BrowserSpace per task, zero Python dependency, every action carries a signed receipt. Bulk text extraction (`page.extract-text`), discriminated waits (`page.wait`), and code mode (`BrowserScript`) all close the loop inside this layer

- **L3-external** (the user's own Chrome, attached via CDP + Python Playwright): **take this route when the user names their own browser** — their login state, their window, visible to them the whole time and theirs to take over at any moment

A note of history on L3-external: v3.0 deleted it outright, on the grounds that "every technical reason it existed for (no bulk text channel, evaluate unusable, screenshots must activate-serialize) is now covered by the built-in browser". That technical judgement was correct — **as a fallback for when the built-in browser isn't enough, it genuinely isn't needed any more**. But the deletion took with it a completely different use case: the user wanting *their own* browser. That has nothing to do with capability, and the built-in browser cannot stand in for it, so v3.2 restores it as a peer option **triggered by user intent**. Note it is no longer a fallback; see "Two browsers — pick by user intent" below.

### v3.0: governed built-in browser (default-hidden, exposed only after Skill activation)

When you call `Skill('web-access')`, the following 9 tools are injected into the current session so the LLM can drive the built-in browser directly:

| Tool | Purpose |
|------|---------|
| BrowserManage | Create/destroy isolated BrowserSpace, start sessions, manage tabs |
| BrowserSnapshot | `semantic` / `text` / `accessibility` / `visual` snapshots — the primary way to read a page |
| BrowserAct | One governed action per call: navigate, input, extract text, wait, element ops, screenshot, … |
| BrowserScript | **Code mode**: one async JS script issues browser commands back-to-back, eliminating per-action round trips (trust level equals Bash) |
| BrowserImport | Import Cookies from the user's Chrome/Edge/Firefox/Safari profile (human-approved; **needs `browser.import.*` granted by the Host — not available to a plain `create_space` session**) |
| BrowserShare | Delegate a Space/Session to another Agent (isolated / snapshot / copy-on-write / live) |
| SitePatternRead / SitePatternWrite | Per-domain "site experience" (AgentFS three-layer) |
| LocalBookmarks | Search local Chrome bookmarks / history |

> **Important**: before `Skill('web-access')` is called, none of these tools appear in the LLM tools list — default conversations don't pay their token cost. See [references/browser-tools.md](references/browser-tools.md).
>
> **Removed in v2.1**: `BrowserListTabs` / `BrowserNavigate` / `BrowserEval` / `BrowserClick` / `BrowserScreenshot` / `BrowserScroll` / `BrowserSetFiles` / `BrowserCloseTab` and the cdp-proxy behind them are retired. Calling them now returns "该旧 BrowserXxx/cdp-proxy 入口已停用". Requires client v10.0.98+; `page.extract-text` / `page.element` / `page.wait` / inline wait blocks / cross-origin iframe snapshots need v10.0.112+, and `BrowserScript` needs a build containing S17/S18.

### Use Cases

- The user needs to search for current information or research a specific topic
- The user needs to fetch public web content or technical documentation
- The user needs to access logged-in sites (Xiaohongshu, Bilibili, Weibo, Feishu, Twitter, etc.) and **read the body text**
- The user needs to pull data from a site's own API in a logged-in context (lists, comments, orders, …)
- The user needs to compare products, aggregate news, or investigate API/library versions

### Core Value

- **Layered progression**: from lightweight search to heavy JS rendering to logged-in access — pick on demand; plus the user's own browser whenever they name it
- **Token optimization**: Jina Reader cuts token usage by 50–80% by default; `page.extract-text`'s maxBytes/cursor paging keeps even long logged-in articles under control
- **Logged-in session reuse**: where the Host has granted `browser.import.*`, BrowserImport brings the user's Cookies into an isolated Space — no re-login required
- **Zero external dependencies by default**: the built-in browser needs no Python/Playwright install and no manually launched debug Chrome (L3-external does, and only when the user asks for it)

## L2: Detailed Specification

## Output Rule

When you complete a research task, you **MUST** cite all source URLs in your response. Distinguish between:
- **Quoted facts**: directly from a fetched page → cite the URL
- **Inferences**: your synthesis or analysis → mark as "(analysis/inference)"

If any fetch fails, explicitly tell the user which URL failed and which fallback you used.

## Prerequisites: Chrome CDP Setup (L3-external only)

**Only needed when taking the L3-external route** (the user named their own browser). The built-in
browser has no prerequisites.

### One-time setup

Have the user launch Chrome with remote debugging enabled:

**macOS**:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="${DESIRECORE_ROOT}/chrome-profile"
```

**Linux**:
```bash
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="${DESIRECORE_ROOT}/chrome-profile"
```

**Windows (PowerShell)**:
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="$env:USERPROFILE\.desirecore\chrome-profile"
```

After launch:
1. The user logs in manually to the sites they need
2. That Chrome window stays open
3. Verify the debug endpoint: `curl -s http://localhost:9222/json/version` should return JSON

### Verify readiness before every operation

```bash
curl -s http://localhost:9222/json/version | python3 -c "import sys,json; d=json.load(sys.stdin); print('CDP ready:', d.get('Browser'))"
```

If it fails, tell the user: "请先启动 Chrome 并开启远程调试端口（见 web-access 技能的 Prerequisites 部分）"
— **then wait for them.** Don't switch to the built-in browser just because it could also do the job.

⚠️ When attached over CDP, **never call `browser.close()`** — that would close the user's own Chrome.
Only close the page you opened. Full recipes in [references/cdp-browser.md](references/cdp-browser.md).

---

## Tool Selection Decision Tree

```
User intent
  │
  ├─ "Search for information about X" (no specific URL)
  │     └─→ WebSearch → pick top 3-5 results → fetch each (see next branches)
  │
  ├─ "Read this public page" (static HTML, docs, news)
  │     └─→ WebFetch(url) directly
  │
  ├─ "Read this heavy-JS page" (SPA, React/Vue sites, Medium, etc.)
  │     └─→ Bash: curl -sL "https://r.jina.ai/<original-url>"
  │          (Jina Reader = default for JS-rendered content, saves tokens)
  │
  ├─ "Read this login-gated page" (Xiaohongshu/Bilibili/Weibo/Feishu/Twitter/Zhihu/WeChat)
  │     └─→ BrowserManage(create_space/start_session) → BrowserAct(tab.navigate)
  │         → BrowserAct(page.extract-text)          ← body text read out directly, maxBytes/cursor paging
  │         Logged in? BrowserImport only if browser.import.* was granted
  │
  ├─ "Pull data from the site's API in a logged-in context"
  │     └─→ fetch.browser recipe: run fetch inside BrowserAct(page.evaluate) with that origin's cookies
  │
  ├─ "API documentation / GitHub / npm package info"
  │     └─→ Prefer official API endpoints over scraping HTML:
  │          - GitHub: gh api repos/owner/name
  │          - npm:    curl https://registry.npmjs.org/<pkg>
  │          - PyPI:   curl https://pypi.org/pypi/<pkg>/json
  │
  └─ "Real-time interactive task" (click, fill form, scroll, screenshot)
        ├─→ **User named "my own / my machine's / the external browser"** → L3-external:
        │     verify CDP is ready (see Prerequisites), then python3 playwright.connect_over_cdp()
        │     If it isn't ready, give them the launch command and wait — don't quietly switch to the built-in one
        └─→ **Otherwise (default)**: built-in browser (BrowserManage → BrowserAct → BrowserSnapshot —
             see references/browser-tools.md, no Python needed)
```

### Two browsers — pick by user intent, not by difficulty

DesireCore can drive **two** browsers. They are peer options:

| | L3 built-in governed browser | L3-external — the user's own browser |
|---|---|---|
| What it is | A browser instance inside the app (the `Browser*` tools) | The Chrome installed on the user's machine, attached via CDP + Python Playwright |
| Login state | Isolated; needs `browser.import.*` granted by the Host before `BrowserImport` can pull cookies | **Literally the user's own session** — nothing to import |
| Can the user see it | Agent tabs are offscreen by default; must be presented to the workbench | **It's their own window** — visible throughout, theirs to take over |
| Prerequisite | None | User must launch Chrome with `--remote-debugging-port=9222` (see Prerequisites) |
| Default | ✅ yes | When the user names it |

> The login-state row is easy to misread as "the built-in browser can't reuse the user's login
> state" — that isn't what it says. Precisely: it **can't reuse it directly**. `Browser*` cannot see
> the windows or tabs of the user's external browser and cannot read its live session; but once the
> Host grants `browser.import.*`, `BrowserImport` can carry that login state into an isolated Space
> **by importing cookies**. The distinction is "take over that live session" (not possible) versus
> "import a copy of the cookies" (possible, once authorized). Only without that grant is the login
> state genuinely unreusable — and then you say so plainly.

**The layer is chosen by user intent, not by technical difficulty.** v3.0 deleted this layer as
"a fallback for when the built-in browser isn't enough" — and as a fallback, it really isn't needed
any more. But that deletion also removed a **different** use case: the user wanting *their own*
browser. That has nothing to do with capability — their login state lives in their Chrome, and they
want to watch it happen and take over when they choose. The built-in browser cannot stand in for that.

**If the user named one, use the one they named:**

- "my own / my machine's / the external browser / my Chrome" → **L3-external**. Verify CDP readiness
  per Prerequisites first; if it isn't ready, give them the launch command and wait. **Do not switch
  to the built-in browser just because it could also do the job**
- "the built-in browser", or nothing named → **L3 built-in** (default, no prerequisites)
- Genuinely unclear which they mean → ask, don't guess

⚠️ Either way, the user must be able to tell which one you actually used. Never use wording that fits
both — "the local browser", "the managed browser on your machine", "your local browser is now open".
When what they asked for and what you're giving differ, the wording has to make that visible.

### Layer strategy summary

| Layer | Use case | Primary tool | Token cost |
|-------|----------|--------------|------------|
| L1 | Public, static | `WebFetch` | Low |
| L2 | JS-heavy, long articles, token savings | `Bash curl r.jina.ai` | **Lowest** (Markdown pre-cleaned) |
| **L3** | **Login-gated navigation, interaction & extraction (PRIMARY)** | **built-in browser (BrowserManage / BrowserAct / BrowserSnapshot / BrowserScript)** | Medium |
| L3-external | **User named their own browser**; or their personal login state is needed and `BrowserImport` is unavailable | `Bash + Python Playwright connect_over_cdp` (see references/cdp-browser.md) | Medium |

**Default priority**: L1 for simple public pages → L2 for heavy → **L3 for login-gated (body text and in-site API data included)**.


> L3-external is deliberately absent from this ordering: it isn't chosen by "is the layer capable
> enough" but by **the user naming it**. When the user wants their own browser, go there directly —
> even if the built-in browser could do the job. See "Two browsers — pick by user intent" above.
## Supported Sites Matrix

| Site | Recommended Layer | Notes |
|------|-------------------|-------|
| Wikipedia, MDN, official docs | L1 WebFetch | Static, clean HTML |
| GitHub README, issues, PRs | `gh api` (best) → L1 WebFetch | Prefer API |
| Hacker News, Reddit | L1 WebFetch | Public content |
| Medium, Dev.to | L2 Jina Reader | JS-rendered, member gates |
| Twitter/X | L3 (or L2 Jina with `x.com`) | Login required for full thread |
| Xiaohongshu (xiaohongshu.com) | L3 built-in browser + BrowserImport | Login required; body text via page.extract-text |
| Bilibili (bilibili.com) | L3 built-in browser + BrowserImport | Login needed for video desc/comments |
| Weibo (weibo.com) | L3 built-in browser + BrowserImport | Long posts require login |
| Zhihu (zhihu.com) | L3 built-in browser + BrowserImport | Long articles + comments require login |
| Feishu Docs (feishu.cn) | L3 built-in browser + BrowserImport | Login required |
| WeChat Official Accounts (mp.weixin.qq.com) | L2 Jina Reader | Usually public, Jina cleans better |
| LinkedIn | L3 built-in browser + BrowserImport | Login wall |

## Tool Reference

### Layer 1: WebSearch + WebFetch

**WebSearch** — discover URLs for an unknown topic:
```
WebSearch(query="latest typescript 5.5 features 2026", max_results=5)
```

Tips:
- Include the year for time-sensitive topics
- Use `allowed_domains` / `blocked_domains` to constrain

**WebFetch** — extract clean Markdown from a known URL:
```
WebFetch(url="https://example.com/article")
```

Tips:
- Results cached for 15 min
- Returns cleaned Markdown with title + URL + body
- If body < 200 chars or looks garbled → escalate to Layer 2 (Jina) or Layer 3 (built-in browser)

### Layer 2: Jina Reader (default for heavy pages)

Jina Reader (`r.jina.ai`) is a free public proxy that renders pages server-side and returns clean Markdown. Use it as the **default** for any page where WebFetch produces garbled or truncated output, and as the **preferred** extractor for JS-heavy SPAs.

```bash
curl -sL "https://r.jina.ai/https://example.com/article"
```

Why Jina is the default token-saver:
- Strips nav/footer/ads automatically
- Handles JS-rendered SPAs
- Returns 50-80% fewer tokens than raw HTML
- No API key needed for basic use (~20 req/min)

See [references/jina-reader.md](references/jina-reader.md) for advanced endpoints and rate limits.

### Layer 3: built-in browser (login-gated access)

The full command surface, capability tiers, and boundaries are in [references/browser-tools.md](references/browser-tools.md). The loop:

1. `BrowserManage(create_space)` → `BrowserManage(start_session)` for a sessionId + first tab
2. Need login state → `BrowserImport` (only if the Host granted `browser.import.*`; without that grant the user's Cookies cannot be reused — tell the user and continue without login or abort)
3. `BrowserAct(tab.navigate)` to reach the page
4. `BrowserSnapshot(semantic)` for interactive-element `ref` handles (cross-origin iframe elements are in the same tree with globally sequential refs)
5. Interact via `input.*` (humanized trajectories) or `page.element` (bulk form writes); wait for results via `page.wait` or inline wait blocks
6. Read body text via `BrowserSnapshot(text)` or `BrowserAct(page.extract-text)`; pull API data via the fetch.browser recipe
7. `BrowserManage(close_session)` when done

Multi-step sequences (navigate→snapshot→click→wait→extract) can be done in one `BrowserScript` run, skipping the per-action IPC round trips.

## L3 Cheatsheet (v3.0)

### Reading a page: pick the channel by need

| You need | Use | Note |
|----------|-----|------|
| Interactive elements + `ref` / `loc=` handles | `BrowserSnapshot({ mode: 'semantic' })` | Buttons/inputs/links + per-line `[ref=eN]` and (when producible) `[loc=...]` stable selectors; cross-origin iframes in the same tree |
| Article body text | `BrowserSnapshot({ mode: 'text' })` or `BrowserAct({ action: 'page.extract-text' })` | markdown/text formats; beyond maxBytes it truncates and hands back a nextCursor for paging — no error |
| Accessibility tree | `BrowserSnapshot({ mode: 'accessibility' })` | Respects `depth` (default 50, max 100) and the maxBytes budget — truncates + pages instead of failing wholesale |
| What the page looks like | `BrowserSnapshot({ mode: 'visual' })` or `BrowserAct({ action: 'page.screenshot' })` | Pixels land directly in the result (vision models read them in place); `clip={x,y,width,height,scale}` for element-level crops (scale up to 4) and `captureBeyondViewport` for full-page capture |

### Command surface at a glance

`BrowserAct` actions grouped by purpose (full enum in the tool schema):

- **tab.***: `navigate` / `back` / `forward` / `reload` / `activate` / `close`
- **input.***: `move` / `click` / `double-click` / `drag` / `wheel` / `touch` / `pinch` / `key` / `text` — humanized input (#1808: consistent UA/UA-CH identity + real trajectories); the preferred interaction channel on anti-bot sites
- **page.element** (discriminated op × selector, nine ops): write ops `fill` / `select-option` / `check` / `uncheck` / `scroll-into-view`; read ops `get-attribute` / `bounding-box` / `count` / `all-inner-texts`. Selectors speak the `loc=` dialect or a snapshot `ref` (with snapshotId). `fill` refuses `input[type=password]`
- **page.wait** (discriminated until, nine values): poll-type `load` / `domcontentloaded` / `networkidle` / `selector` / `url` / `timeout` return `waited:false` on timeout; event-type `request` / `response` / `download` throw on timeout. Default 10s, max 60s
- **Inline wait blocks**: `params.wait` (isomorphic to page.wait params) on `tab.navigate` / `input.click` / `input.key` / `page.element{op:"fill"}` — one receipt completes "act→wait for result", the waiter registers before the action, no cross-IPC race
- **page.evaluate**: `{ expression, awaitPromise }`, return values cross as-is (over-budget results truncate with a `truncated` flag, never throw); capability `browser.page.evaluate` sits behind the human gate (allow-all mode skips the card)
- **page.extract-text / page.screenshot / page.wait**: see the table above and the fetch.browser recipe

`loc=` selector dialect (S7/S9): `e<N>` (must carry the snapshotId of the snapshot that issued the ref), `loc=css:` / `loc=role:` / `loc=text:` / `loc=testid:`, bare CSS, composable with `internal:nth/last/scope/filter`. Unknown prefixes fail explicitly — never silently degrade to CSS.

### Choosing the interaction channel: input.* vs page.element

- **On anti-bot sites (Xiaohongshu/Weibo/Bilibili etc.) always prefer `input.*`**: it rides the #1808 humanized input pipeline (coordinate dispatch, humanized trajectories, auditable visualization) plus the identity layer that keeps UA/UA-CH free of Electron/Headless tells
- **`page.element` write ops fit bulk form filling on sites that don't detect automation**: one call fills/selects/checks, far faster than per-element input.click + input.text
- **Red line**: `page.element` deliberately has no click — pointer actions must go through `input.*`; invoking `el.click()` via JS bypasses the entire humanization investment and is an explicitly forbidden fallback

### The fetch.browser recipe: pull API data with login state

The right way to pull a site's own API (lists, comments, orders, any JSON) in a logged-in context: run `fetch` **in the page context** — it carries that origin's cookies automatically, stays same-origin, is bounded by Grant origins, and rides the existing `page.evaluate` gate. It is a wrapper usage of `BrowserAct({ action: 'page.evaluate' })`:

```yaml
BrowserAct:
  action: page.evaluate
  params:
    expression: |
      fetch('/api/v1/comments?page=1&size=20', {
        headers: { accept: 'application/json' }
      }).then(r => r.text())
    awaitPromise: true        # default true; waits for the returned Promise to settle
```

Notes:
- `tab.navigate` to any page on the site first (establishes the origin and cookies), then fire the fetch; use a relative path so it is same-origin by construction
- Return values cross as-is; for large JSON take `.text()` and slice it yourself, or page through multiple calls
- Only the current tab's origin is reachable (Grant origins constraint); for another site's API, navigate there first
- `page.evaluate` is a human-gated capability: outside allow-all mode an approval card appears — explain the purpose to the user

### Recommended flow (Xiaohongshu example)

```
1. BrowserManage({ action: 'create_space', name: 'xhs-note', persistence: 'ephemeral' })
2. BrowserManage({ action: 'start_session', spaceId, capabilities: [...] })
   ← an explicit list *narrows* the lease; include browser.input.pointer.wheel to scroll
     and browser.observe.snapshot to extract text
3. Reuse the login: only when the Host granted browser.import.*,
   BrowserImport({ action: 'discover' → 'create_plan' → 'dry_run' → 'apply' }).
   Without that grant the user's cookies cannot be reused — say so, then continue
   as logged-out or abort.
4. BrowserAct({ action: 'tab.navigate', params: { url: 'https://www.xiaohongshu.com/explore/abc123' } })
5. BrowserSnapshot({ mode: 'semantic' })        ← interaction refs (cross-origin iframes in the same tree)
6. BrowserAct({ action: 'page.extract-text', params: { format: 'markdown' } })
   ← body text read out directly; if too long, pass back the returned nextCursor to continue
7. Need to confirm rendering → BrowserSnapshot({ mode: 'visual' }) (pixels readable in place)
8. SitePatternRead({ domain: 'xiaohongshu.com' })  ← read accumulated experience
9. At task end → BrowserManage({ action: 'close_session', sessionId })
10. If you find a new pitfall → SitePatternWrite({ domain, scope: 'agent', mode: 'merge', content })
```

## Site Experience Accumulation

When the task ends and you've discovered new anti-bot pitfalls, effective selectors, or platform quirks, call:

```
SitePatternWrite({
  domain: "xiaohongshu.com",
  scope: "agent",     // agent=shared (Git-tracked, can be published); user=private
  mode: "merge",      // merge appends; replace overwrites
  content: "## Known pitfalls\n- 2026-08: ...",
  confidence: "medium"
})
```

Reads use a three-layer priority order:

```
SitePatternRead({ domain: "xiaohongshu.com" })
  → users/<userId>/agents/<agentId>/memory/site-patterns/   (user-private)
  → agents/<agentId>/memory/site-patterns/                  (agent-shared, Git)
  → defaults/global-skills/web-access/references/site-patterns/  (global baseline, read-only)
```

Content containing cookies / tokens / phone numbers / emails will **automatically downgrade scope='user'** and notify you.

## Common Workflows

Read [references/workflows.md](references/workflows.md) for detailed templates:
- Tech docs lookup
- Competitor research
- News aggregation & timelines
- API/library version investigation

Read [references/jina-reader.md](references/jina-reader.md) for Jina Reader positioning, rate limits, and advanced endpoints.

Read [references/browser-tools.md](references/browser-tools.md) for the full built-in browser command surface, capability tiers, and known boundaries.

## Quick Workflow: Multi-Source Research

```
1. WebSearch(query) → 5 candidate URLs
2. Skim titles + snippets → pick 3 most relevant
3. Classify each URL by layer (L1 / L2 / L3)
4. Fetch all in parallel (single message, multiple tool calls)
5. If any fetch returns < 200 chars or garbled → retry via next layer
6. Synthesize: contradictions? consensus? outliers?
7. Report with inline [source](url) citations + a Sources list at the end
```

## Anti-Patterns (Avoid)

- ❌ **Using WebFetch on obviously heavy sites** — Medium, Twitter, Xiaohongshu will waste tokens or fail. Jump straight to L2/L3.
- ❌ **Fetching one URL at a time when you need 5** — batch in a single message.
- ❌ **Trusting a single source** — cross-check ≥ 2 sources for non-trivial claims.
- ❌ **Fetching the search result page itself** — WebSearch already returns snippets; fetch the actual articles.
- ❌ **Ignoring the cache** — WebFetch caches 15 min, reuse freely.
- ❌ **Scraping when an API exists** — GitHub, npm, PyPI, Wikipedia all have JSON APIs; a logged-in site's own API goes through the fetch.browser recipe.
- ❌ **Forgetting the year in time-sensitive queries** — "best AI models" returns 2023 results; "best AI models 2026" returns current.
- ❌ **Hardcoding login credentials in scripts** — login state can only come from Cookies imported via BrowserImport.
- ❌ **Citing only after the fact** — collect URLs as you fetch, not from memory afterwards.
- ❌ **(v3.0) Using page.element for bulk interaction on anti-bot sites** — it is a direct JS call that bypasses humanized trajectories; on anti-bot sites always use `input.*`; keep `page.element` for bulk form filling where the site doesn't detect automation.
- ❌ **(v3.0) Reading body text from screenshots** — `page.extract-text` / `BrowserSnapshot(text)` hand you markdown/text with paged budgets; save screenshots for layout confirmation and CAPTCHAs where you truly must look.
- ❌ **(v3.0) Tolerating per-action round trips when BrowserScript would do** — navigate→snapshot→click→wait→extract runs as one script; remember BrowserScript's trust level equals Bash and the script source passes one human approval.
- ❌ **(v3.0) Discovering new pitfalls and not writing a site-pattern** — next time the same Agent runs the task, it'll repeat the same mistakes. Anything that took 2+ steps to figure out is worth `SitePatternWrite(scope='agent', mode='merge')`.
- ❌ **(v3.0) Writing cookies / phone numbers to scope='agent'** — that layer is Git-tracked and may be published to the marketplace. SitePatternWrite auto-downgrades, but don't deliberately write secrets to the agent layer.

## Example Interaction

**User**: "Grab the contents of this Xiaohongshu note for me: https://www.xiaohongshu.com/explore/abc123"

**Agent workflow**:
```
1. Recognize → Xiaohongshu is an L3 logged-in site
2. BrowserManage(create_space + start_session)
   Need login state → if browser.import.* was granted, run the BrowserImport four steps;
   otherwise tell the user the login cannot be reused and continue with the public part
3. BrowserAct(tab.navigate → the note URL)
4. BrowserAct(page.extract-text, format: markdown)
   ← body text read out directly; page with nextCursor if over budget
5. When returning to the user:
   - Cite the original URL
   - Quote facts from the extracted text with source links
6. Tell the user: "Fetched via the built-in browser, original link: [xhs](url)"
7. BrowserManage(close_session)
```
