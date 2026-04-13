---
name: 联网访问
description: >-
  Use this skill whenever the user needs to access information from the internet
  — searching for current information, fetching public web pages, browsing
  login-gated sites (微博/小红书/B站/飞书/Twitter), comparing products,
  researching topics, gathering documentation, or summarizing news.
  This skill orchestrates three complementary layers: (1) WebSearch + WebFetch
  for public pages, (2) Jina Reader as the default token-optimization layer for
  heavy/JS-rendered pages, and (3) Chrome DevTools Protocol (CDP) via Python
  Playwright for login-gated sites that require the user's existing browser
  session. Always cite source URLs. Use when 用户提到 联网搜索、上网查、
  查资料、抓取网页、研究、调研、最新资讯、文档查询、对比、竞品、技术文档、
  新闻、网址、URL、找一下、搜一下、查一下、小红书、B站、微博、飞书、Twitter、
  推特、X、知乎、公众号、已登录、登录状态。
license: Complete terms in LICENSE.txt
version: 1.1.2
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
metadata:
  author: desirecore
  updated_at: '2026-04-13'
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
  short_desc: 联网搜索、网页抓取、登录态浏览器访问（CDP）、研究调研工作流
  category: research
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# web-access 技能

## L0：一句话摘要

三层联网访问工具包——搜索公开页面、Jina 优化抓取、CDP 登录态浏览器访问。

## L1：概述与使用场景

### 能力描述

web-access 是一个**流程型技能（Procedural Skill）**，提供三层互补的联网访问能力：Layer 1（WebSearch + WebFetch）用于公开页面；Layer 2（Jina Reader）用于 JS 渲染的重页面，默认节省 Token；Layer 3（Chrome CDP）用于需要登录态的站点（小红书/B站/微博/飞书/Twitter）。

### 使用场景

- 用户需要搜索当前信息或研究特定主题
- 用户需要抓取公开网页内容或技术文档
- 用户需要访问登录态站点（小红书、B站、微博、飞书、Twitter 等）
- 用户需要对比产品、聚合新闻或调查 API/库版本

### 核心价值

- **三层递进**：从轻量搜索到重度 JS 渲染到登录态访问，按需选择
- **Token 优化**：Jina Reader 默认减少 50-80% Token 消耗
- **登录态复用**：通过 CDP 连接用户已登录的 Chrome，无需重复登录

## L2：详细规范

## Output Rule

When you complete a research task, you **MUST** cite all source URLs in your response. Distinguish between:
- **Quoted facts**: directly from a fetched page → cite the URL
- **Inferences**: your synthesis or analysis → mark as "(分析/推断)"

If any fetch fails, explicitly tell the user which URL failed and which fallback you used.

---

## Prerequisites: Chrome CDP Setup (for login-gated sites)

**Only required when accessing sites that need the user's login session** (小红书/B站/微博/飞书/Twitter/知乎/公众号).

### One-time setup

Launch a dedicated Chrome instance with remote debugging enabled:

**macOS**:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.desirecore/chrome-profile"
```

**Linux**:
```bash
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.desirecore/chrome-profile"
```

**Windows (PowerShell)**:
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="$env:USERPROFILE\.desirecore\chrome-profile"
```

After launch:
1. Manually log in to the sites you need (小红书、B站、微博、飞书 …)
2. Leave this Chrome window open in the background
3. Verify the debug endpoint: `curl -s http://localhost:9222/json/version` should return JSON

### Verify CDP is ready

Before any CDP operation, always run:
```bash
curl -s http://localhost:9222/json/version | python3 -c "import sys,json; d=json.load(sys.stdin); print('CDP ready:', d.get('Browser'))"
```

If the command fails, tell the user: "请先启动 Chrome 并开启远程调试端口（见 web-access 技能的 Prerequisites 部分）。"

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
  ├─ "Read this login-gated page" (小红书/B站/微博/飞书/Twitter/知乎/公众号)
  │     └─→ 1. Verify CDP ready (curl http://localhost:9222/json/version)
  │          2. Bash: python3 script with playwright.connect_over_cdp()
  │          3. Extract content → feed to Jina Reader for clean Markdown
  │             (or use BeautifulSoup directly on the raw HTML)
  │
  ├─ "API documentation / GitHub / npm package info"
  │     └─→ Prefer official API endpoints over scraping HTML:
  │          - GitHub: gh api repos/owner/name
  │          - npm:    curl https://registry.npmjs.org/<pkg>
  │          - PyPI:   curl https://pypi.org/pypi/<pkg>/json
  │
  └─ "Real-time interactive task" (click, fill form, scroll, screenshot)
        └─→ CDP + Playwright (see references/cdp-browser.md)
```

### Three-layer strategy summary

| Layer | Use case | Primary tool | Token cost |
|-------|----------|--------------|------------|
| L1 | Public, static | `WebFetch` | Low |
| L2 | JS-heavy, long articles, token savings | `Bash curl r.jina.ai` | **Lowest** (Markdown pre-cleaned) |
| L3 | Login-gated, interactive | `Bash + Python Playwright CDP` | Medium (raw HTML, then clean via Jina or BS4) |

**Default priority**: L1 for simple public pages → L2 for anything heavy → L3 only when login is required.

---

## Supported Sites Matrix

| Site | Recommended Layer | Notes |
|------|-------------------|-------|
| Wikipedia, MDN, official docs | L1 WebFetch | Static, clean HTML |
| GitHub README, issues, PRs | `gh api` (best) → L1 WebFetch | Prefer API |
| Hacker News, Reddit | L1 WebFetch | Public content |
| Medium, Dev.to | L2 Jina Reader | JS-rendered, member gates |
| Twitter/X | L3 CDP (or L2 Jina with `x.com`) | Login required for full thread |
| 小红书 (xiaohongshu.com) | L3 CDP | 强制登录 |
| B站 (bilibili.com) | L3 CDP | 视频描述/评论需登录 |
| 微博 (weibo.com) | L3 CDP | 长微博需登录 |
| 知乎 (zhihu.com) | L3 CDP | 长文+评论需登录 |
| 飞书文档 (feishu.cn) | L3 CDP | 必须登录 |
| 公众号 (mp.weixin.qq.com) | L2 Jina Reader | 通常公开，Jina 处理更干净 |
| LinkedIn | L3 CDP | 登录墙 |

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
- Per-site selectors (小红书/B站/微博/知乎/飞书)
- Scrolling & lazy-load patterns
- Screenshot & form-fill recipes
- Troubleshooting connection issues

---

## Common Workflows

Read [references/workflows.md](references/workflows.md) for detailed templates:
- 技术文档查询 (Tech docs lookup)
- 竞品对比研究 (Competitor research)
- 新闻聚合与时间线 (News aggregation)
- API/库版本调查 (Library version investigation)

Read [references/cdp-browser.md](references/cdp-browser.md) for login-gated site recipes (小红书/B站/微博/知乎/飞书).

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

- ❌ **Using WebFetch on obviously heavy sites** — Medium, Twitter, 小红书 will waste tokens or fail. Jump straight to L2/L3.
- ❌ **Launching headless Chrome instead of CDP attach** — loses user's login state, triggers anti-bot, slow cold start. Always use `connect_over_cdp()` to attach to the user's existing session.
- ❌ **Fetching one URL at a time when you need 5** — batch in a single message.
- ❌ **Trusting a single source** — cross-check ≥ 2 sources for non-trivial claims.
- ❌ **Fetching the search result page itself** — WebSearch already returns snippets; fetch the actual articles.
- ❌ **Ignoring the cache** — WebFetch caches 15 min, reuse freely.
- ❌ **Scraping when an API exists** — GitHub, npm, PyPI, Wikipedia all have JSON APIs.
- ❌ **Forgetting the year in time-sensitive queries** — "best AI models" returns 2023 results; "best AI models 2026" returns current.
- ❌ **Hardcoding login credentials in scripts** — always rely on the user's pre-logged CDP session.
- ❌ **Citing only after the fact** — collect URLs as you fetch, not from memory afterwards.

---

## Example Interaction

**User**: "帮我抓一下这条小红书笔记的内容：https://www.xiaohongshu.com/explore/abc123"

**Agent workflow**:
```
1. 识别 → 小红书是 L3 登录态站点
2. 检查 CDP：curl -s http://localhost:9222/json/version
   ├─ 失败 → 提示用户启动 Chrome 调试模式，终止
   └─ 成功 → 继续
3. Bash: python3 connect_over_cdp 脚本 → page.goto(url) → page.content()
4. BeautifulSoup 提取 h1 title、.note-content、.comments
5. 返回给用户时：
   - 引用原 URL
   - 若内容很长，用 Jina 清洗一遍节省 token
6. 告知用户：「已通过你的登录态抓取，原链接：[xhs](url)」
```

---

## Installation Note

CDP features require Python + Playwright installed:

```bash
pip3 install playwright beautifulsoup4
python3 -m playwright install chromium  # only needed if user hasn't installed Chrome
```

If `playwright` is not installed when the user requests a login-gated site, run the install commands in Bash and explain you're setting up the browser automation dependency.
