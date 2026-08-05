---
name: web-access
description: >-
  Use this skill whenever the user needs to access information from the internet
  — searching for current information, fetching public web pages, browsing
  login-gated sites (微博/小红书/B站/飞书/Twitter), comparing products,
  researching topics, gathering documentation, or summarizing news.
  This skill orchestrates four complementary layers: (1) WebSearch + WebFetch
  for public pages, (2) Jina Reader as the default token-optimization layer for
  heavy/JS-rendered pages, (3) the governed built-in browser (isolated
  BrowserSpace + Cookie import) to reach and interact with login-gated sites,
  and (4) Chrome DevTools Protocol via Python Playwright as the fallback for
  bulk text extraction and complex automation. Always cite source URLs.
  Use when 用户提到 联网搜索、上网查、
  查资料、抓取网页、研究、调研、最新资讯、文档查询、对比、竞品、技术文档、
  新闻、网址、URL、找一下、搜一下、查一下、小红书、B站、微博、飞书、Twitter、
  推特、X、知乎、公众号、已登录、登录状态。
license: Complete terms in LICENSE.txt
version: 2.1.1
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
  - cdp
  - playwright
provides:
  tools:
    - BrowserManage
    - BrowserSnapshot
    - BrowserAct
    - BrowserImport
    - BrowserShare
    - SitePatternRead
    - SitePatternWrite
    - LocalBookmarks
metadata:
  author: desirecore
  updated_at: '2026-08-06'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 联网访问
      short_desc: 联网搜索、网页抓取、内置受管浏览器登录态访问、研究调研工作流
      description: 四层联网访问工具包——搜索公开页面、Jina 优化抓取、内置受管浏览器登录态访问、Python Playwright CDP 兜底。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:ce46e1982de8cd65
      translated_by: human
    en-US:
      name: Web Access
      short_desc: Web search, page fetching, logged-in access via the governed built-in browser, research workflows
      description: A four-layer web-access toolkit — search public pages, fetch heavy pages via Jina Reader, reach logged-in sites through the governed built-in browser, and fall back to Chrome CDP.
      body: ./SKILL.md
      source_hash: sha256:ce46e1982de8cd65
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
    stroke="url(#wa-a)" stroke-width="1"
    stroke-opacity="0.35"/><circle cx="18.5" cy="18.5" r="2.5"
    stroke="#34C759" stroke-width="1.5" fill="#34C759"
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

A four-layer web-access toolkit — search public pages, optimize fetches via Jina Reader, reach login-gated sites through the governed built-in browser, and fall back to Chrome CDP.

## L1: Overview & Use Cases

### Capability

web-access is a **procedural skill** that provides four complementary layers of web access:

- **L1** (WebSearch + WebFetch): public, static pages
- **L2** (Jina Reader): JS-rendered heavy pages, saving tokens by default
- **L3-fast** (governed built-in browser — **rewritten in v2.1**): reach and *interact with* logged-in / interactive sites — isolated BrowserSpace per task, zero Python dependency, every action carries a signed receipt. **Reading long article text is still L2/L3-fallback's job** — see the extraction note below
- **L3-fallback** (Chrome CDP + Python Playwright): backup for complex automation (long waits, race conditions, custom in-browser scripts)

### v2.1 — governed built-in browser (default-hidden, exposed only after Skill activation)

When you call `Skill('web-access')`, the following 8 tools are injected into the current session so the LLM can drive the built-in browser directly:

| Tool | Purpose |
|------|---------|
| BrowserManage | Create/destroy isolated BrowserSpace, start sessions, manage tabs |
| BrowserSnapshot | `semantic` / `accessibility` / `visual` page snapshots — the primary way to read a page |
| BrowserAct | One governed action per call: navigate, click, type, scroll, screenshot, … |
| BrowserImport | Import Cookies from the user's Chrome/Edge/Firefox/Safari profile (human-approved; **needs `browser.import.*` granted by the Host — not available to a plain `create_space` session**) |
| BrowserShare | Delegate a Space/Session to another Agent (isolated / snapshot / copy-on-write / live) |
| SitePatternRead / SitePatternWrite | Per-domain "site experience" (AgentFS three-layer) |
| LocalBookmarks | Search local Chrome bookmarks / history |

> **Important**: before `Skill('web-access')` is called, none of these tools appear in the LLM tools list — default conversations don't pay their token cost. See [references/browser-tools.md](references/browser-tools.md).
>
> **Removed in v2.1**: `BrowserListTabs` / `BrowserNavigate` / `BrowserEval` / `BrowserClick` / `BrowserScreenshot` / `BrowserScroll` / `BrowserSetFiles` / `BrowserCloseTab` and the cdp-proxy behind them are retired. Calling them now returns "该旧 BrowserXxx/cdp-proxy 入口已停用". Requires client v10.0.98+.

### Use Cases

- The user needs to search for current information or research a specific topic
- The user needs to fetch public web content or technical documentation
- The user needs to access logged-in sites (Xiaohongshu, Bilibili, Weibo, Feishu, Twitter, etc.)
- The user needs to compare products, aggregate news, or investigate API/library versions

### Core Value

- **Four-layer progression**: from lightweight search to heavy JS rendering to logged-in access — pick on demand
- **Token optimization**: Jina Reader cuts token usage by 50–80% by default
- **Logged-in session reuse**: attach to the user's Chrome via CDP in the fallback layer, or — where the Host has granted `browser.import.*` — import their Cookies into an isolated Space via BrowserImport; either way, no re-login required

## L2: Detailed Specification

## Output Rule

When you complete a research task, you **MUST** cite all source URLs in your response. Distinguish between:
- **Quoted facts**: directly from a fetched page → cite the URL
- **Inferences**: your synthesis or analysis → mark as "(analysis/inference)"

If any fetch fails, explicitly tell the user which URL failed and which fallback you used.

---

## Prerequisites: Chrome CDP Setup (for login-gated sites)

**Required for the L3-fallback layer** (Python Playwright) — and, in practice, still the reliable way to reuse a login. The L3-fast built-in browser can skip it only when the Host has granted `browser.import.*` so that `BrowserImport` actually works; otherwise set this up.

### One-time setup

Launch a dedicated Chrome instance with remote debugging enabled:

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
1. Manually log in to the sites you need (Xiaohongshu, Bilibili, Weibo, Feishu, …)
2. Leave this Chrome window open in the background
3. Verify the debug endpoint: `curl -s http://localhost:9222/json/version` should return JSON

### Verify CDP is ready

Before any CDP operation, always run:
```bash
curl -s http://localhost:9222/json/version | python3 -c "import sys,json; d=json.load(sys.stdin); print('CDP ready:', d.get('Browser'))"
```

If the command fails, tell the user: "Please launch Chrome with the remote debugging port enabled (see the Prerequisites section of the web-access skill)."

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
  │     ├─→ Reach it: BrowserManage(create_space/start_session) → BrowserAct(tab.navigate)
  │     │              → tab.activate + page.screenshot to confirm you landed on the content
  │     │              (semantic snapshot has no body text). Logged-in? BrowserImport only if
  │     │              browser.import.* was granted — otherwise reuse the login via CDP below.
  │     └─→ Extract the text: verify CDP ready, then python3 playwright.connect_over_cdp()
  │                   → page.content() → Jina Reader / BeautifulSoup
  │
  ├─ "API documentation / GitHub / npm package info"
  │     └─→ Prefer official API endpoints over scraping HTML:
  │          - GitHub: gh api repos/owner/name
  │          - npm:    curl https://registry.npmjs.org/<pkg>
  │          - PyPI:   curl https://pypi.org/pypi/<pkg>/json
  │
  └─ "Real-time interactive task" (click, fill form, scroll, screenshot)
        ├─→ **Default: built-in browser** (BrowserManage → BrowserAct → BrowserSnapshot —
        │     see references/browser-tools.md, no Python needed)
        └─→ Fallback: CDP + Python Playwright (references/cdp-browser.md) when the built-in browser is insufficient
            (e.g., complex race conditions, multi-event waits, long-running in-browser scripts)
```

### Four-layer strategy summary

| Layer | Use case | Primary tool | Token cost |
|-------|----------|--------------|------------|
| L1 | Public, static | `WebFetch` | Low |
| L2 | JS-heavy, long articles, token savings | `Bash curl r.jina.ai` | **Lowest** (Markdown pre-cleaned) |
| **L3-fast** | **Login-gated navigation & interaction (PRIMARY)** | **built-in browser (BrowserManage / BrowserAct / BrowserSnapshot)** | Medium |
| L3-fallback | Complex automation (race / long-wait / custom scripts) | `Bash + Python Playwright CDP` | Medium |

**Default priority**: L1 for simple public pages → L2 for heavy → **L3-fast for login-gated** → L3-fallback only when the built-in browser is insufficient.

---

## Supported Sites Matrix

| Site | Recommended Layer | Notes |
|------|-------------------|-------|
| Wikipedia, MDN, official docs | L1 WebFetch | Static, clean HTML |
| GitHub README, issues, PRs | `gh api` (best) → L1 WebFetch | Prefer API |
| Hacker News, Reddit | L1 WebFetch | Public content |
| Medium, Dev.to | L2 Jina Reader | JS-rendered, member gates |
| Twitter/X | L3 CDP (or L2 Jina with `x.com`) | Login required for full thread |
| Xiaohongshu (xiaohongshu.com) | L3 CDP | Login required |
| Bilibili (bilibili.com) | L3 CDP | Login needed for video desc/comments |
| Weibo (weibo.com) | L3 CDP | Long posts require login |
| Zhihu (zhihu.com) | L3 CDP | Long articles + comments require login |
| Feishu Docs (feishu.cn) | L3 CDP | Login required |
| WeChat Official Accounts (mp.weixin.qq.com) | L2 Jina Reader | Usually public, Jina cleans better |
| LinkedIn | L3 CDP | Login wall |

---

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
- If body < 200 chars or looks garbled → escalate to Layer 2 (Jina) or Layer 3 (CDP)

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

### Layer 3: CDP Browser (login-gated access)

Use Python Playwright's `connect_over_cdp()` to attach to the user's running Chrome (which already has login cookies). **No re-login needed.**

**Minimal template**:
```bash
python3 << 'PY'
from playwright.sync_api import sync_playwright

TARGET_URL = "https://www.xiaohongshu.com/explore/..."

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]  # reuse user's default context (has cookies)
    page = context.new_page()
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)  # let lazy content load
    html = page.content()
    page.close()

# Print first 500 chars to verify
print(html[:500])
PY
```

**Extract text via BeautifulSoup** (no Jina round-trip):
```bash
python3 << 'PY'
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    page = browser.contexts[0].new_page()
    page.goto("https://www.bilibili.com/video/BV...", wait_until="networkidle")
    html = page.content()
    page.close()

soup = BeautifulSoup(html, "html.parser")
title = soup.select_one("h1.video-title")
desc = soup.select_one(".video-desc")
print("Title:", title.get_text(strip=True) if title else "N/A")
print("Desc:",  desc.get_text(strip=True)  if desc  else "N/A")
PY
```

See [references/cdp-browser.md](references/cdp-browser.md) for:
- Per-site selectors (Xiaohongshu / Bilibili / Weibo / Zhihu / Feishu)
- Scrolling & lazy-load patterns
- Screenshot & form-fill recipes
- Troubleshooting connection issues

---

## L3-fast: Built-in Browser Cheatsheet (v2.1)

**Only after you call `Skill('web-access')` will the following tools appear in `tools[]`.**

| Tool | One-line example |
|------|-----------------|
| `BrowserManage({ action: 'create_space', name, persistence: 'ephemeral' })` | One isolated Space per task |
| `BrowserManage({ action: 'start_session', spaceId, capabilities })` | Start a session, returns sessionId + first tab |
| `BrowserManage({ action: 'list_tabs' \| 'create_tab' \| 'close_session' })` | Tab / lifecycle management |
| `BrowserAct({ action: 'tab.navigate', params: { url } })` | Navigate the current tab |
| `BrowserSnapshot({ mode: 'semantic' })` | Read the page: interactive elements + `ref` handles |
| `BrowserAct({ action: 'input.click', params: { ref } })` | Click by snapshot `ref`, never by raw x/y |
| `BrowserAct({ action: 'input.text', params: { text } })` | Type into the focused element |
| `BrowserAct({ action: 'input.wheel', params: { x: 640, y: 400, deltaX: 0, deltaY: 720 } })` | Scroll to trigger lazy loading — `x`/`y` (or `ref`) is **required**, and the session needs `browser.input.pointer.wheel` |
| `BrowserAct({ action: 'tab.activate', params: { bounds } })` → `page.screenshot` | **activate first, then screenshot** |
| `BrowserImport({ action: 'discover' \| 'create_plan' \| 'dry_run' \| 'apply' \| 'rollback' \| 'list_plans' })` | Reuse the user's login cookies — those 6 are the **complete** action set; happy path is `discover → create_plan → dry_run → apply`. **Needs `browser.import.*`, which `create_space` does not grant** (see below) |

Full API and edge cases: see [references/browser-tools.md](references/browser-tools.md).

**How to read a page** — pick by what you need:

| You need | Use | Note |
|----------|-----|------|
| Interactive elements + `ref` handles | `BrowserSnapshot({ mode: 'semantic' })` | Buttons / inputs / links only — **no article text** |
| Article text on a small/simple page | `BrowserSnapshot({ mode: 'accessibility' })` | Returns StaticText nodes; fails with `BROWSER_RESULT_TOO_LARGE` on real content pages (2 MB result cap, and the `depth` argument is currently ignored by the host) |
| Article text on a real page | L2 Jina Reader (public) or L3-fallback Playwright (login-gated) | The built-in browser has no working bulk text-extraction channel yet |
| What the page looks like | `tab.activate` → `BrowserAct({ action: 'page.screenshot' })` | Full-page only; read it visually |

`page.evaluate` is **not** an extraction channel: it needs human approval per call and its string/object return values come back as `[REDACTED:browser-runtime-value]`.

### Recommended flow (Xiaohongshu example)

```
1. BrowserManage({ action: 'create_space', name: 'xhs-note', persistence: 'ephemeral' })
2. BrowserManage({ action: 'start_session', spaceId, capabilities: [...] })
   ← an explicit list *narrows* the lease; include browser.input.pointer.wheel if you will scroll
3. Reuse the login: L3-fallback Playwright against the user's own Chrome is the default path.
   BrowserImport({ action: 'discover' → 'create_plan' → 'dry_run' → 'apply' }) only works if the
   Host granted browser.import.* separately — create_space alone does not. If it is denied, fall back.
4. BrowserAct({ action: 'tab.navigate', params: { url: 'https://www.xiaohongshu.com/explore/abc123' } })
5. BrowserSnapshot({ mode: 'semantic' })   ← element refs for interaction (no body text)
   tab.activate + page.screenshot           ← confirm the note actually rendered
   → extract the note text via L3-fallback Playwright
6. SitePatternRead({ domain: 'xiaohongshu.com' })  ← read accumulated experience
7. At task end → BrowserManage({ action: 'close_session', sessionId })
8. If you find a new pitfall → SitePatternWrite({ domain, scope: 'agent', mode: 'merge', content })
```

---

## Site Experience Accumulation (v2.0)

When the task ends and you've discovered new anti-bot pitfalls, effective selectors, or platform quirks, call:

```
SitePatternWrite({
  domain: "xiaohongshu.com",
  scope: "agent",     // agent=shared (Git-tracked, can be published); user=private
  mode: "merge",      // merge appends; replace overwrites
  content: "## Known pitfalls\n- 2026-05: ...",
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

---

## Common Workflows

Read [references/workflows.md](references/workflows.md) for detailed templates:
- Tech docs lookup
- Competitor research
- News aggregation & timelines
- API/library version investigation

Read [references/cdp-browser.md](references/cdp-browser.md) for login-gated site recipes (Xiaohongshu / Bilibili / Weibo / Zhihu / Feishu).

Read [references/jina-reader.md](references/jina-reader.md) for Jina Reader positioning, rate limits, and advanced endpoints.

---

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

---

## Anti-Patterns (Avoid)

- ❌ **Using WebFetch on obviously heavy sites** — Medium, Twitter, Xiaohongshu will waste tokens or fail. Jump straight to L2/L3.
- ❌ **Launching headless Chrome instead of CDP attach** — loses user's login state, triggers anti-bot, slow cold start. Always use `connect_over_cdp()` to attach to the user's existing session.
- ❌ **Fetching one URL at a time when you need 5** — batch in a single message.
- ❌ **Trusting a single source** — cross-check ≥ 2 sources for non-trivial claims.
- ❌ **Fetching the search result page itself** — WebSearch already returns snippets; fetch the actual articles.
- ❌ **Ignoring the cache** — WebFetch caches 15 min, reuse freely.
- ❌ **Scraping when an API exists** — GitHub, npm, PyPI, Wikipedia all have JSON APIs.
- ❌ **Forgetting the year in time-sensitive queries** — "best AI models" returns 2023 results; "best AI models 2026" returns current.
- ❌ **Hardcoding login credentials in scripts** — always rely on the user's pre-logged CDP session.
- ❌ **Citing only after the fact** — collect URLs as you fetch, not from memory afterwards.
- ❌ **(v2.1) Writing Python heredoc when the built-in browser would do** — slow, requires Python+Playwright install, and bloats context. Prefer L3-fast; fall back to Python only when the built-in browser is insufficient (race / long-wait / custom scripts).
- ❌ **(v2.1) Calling `page.screenshot` before `tab.activate`** — tabs are parked off-screen at `(-10000,-10000,1x1)` and have no compositing surface, so the capture stalls until the 30s deadline **and the tab host is destroyed**; every later call then fails with `BROWSER_TAB_HOST_NOT_FOUND`. Always `tab.activate` with real bounds first.
- ❌ **(v2.1) Reaching for `page.evaluate` to read a page** — it needs human approval on every call, its string/object return values come back as `[REDACTED:browser-runtime-value]` (only number/boolean/null survive), and anti-debug sites stall it for tens of seconds. Read pages with `BrowserSnapshot` instead.
- ❌ **(v2.1) Discovering new pitfalls and not writing a site-pattern** — next time the same Agent runs the task, it'll repeat the same mistakes. Anything that took 2+ steps to figure out is worth `SitePatternWrite(scope='agent', mode='merge')`.
- ❌ **(v2.1) Writing cookies / phone numbers to scope='agent'** — that layer is Git-tracked and may be published to the marketplace. SitePatternWrite auto-downgrades, but don't deliberately write secrets to the agent layer.

---

## Example Interaction

**User**: "Grab the contents of this Xiaohongshu note for me: https://www.xiaohongshu.com/explore/abc123"

**Agent workflow**:
```
1. Recognize → Xiaohongshu is an L3 logged-in site
2. Check CDP: curl -s http://localhost:9222/json/version
   ├─ Failure → prompt the user to launch Chrome in debug mode, abort
   └─ Success → continue
3. Bash: python3 connect_over_cdp script → page.goto(url) → page.content()
4. BeautifulSoup extract h1 title, .note-content, .comments
5. When returning to the user:
   - Cite the original URL
   - If content is long, run it through Jina to save tokens
6. Tell the user: "Fetched via your logged-in session, original link: [xhs](url)"
```

---

## Installation Note

CDP features require Python + Playwright installed:

```bash
pip3 install playwright beautifulsoup4
python3 -m playwright install chromium  # only needed if user hasn't installed Chrome
```

If `playwright` is not installed when the user requests a login-gated site, run the install commands in Bash and explain you're setting up the browser automation dependency.
