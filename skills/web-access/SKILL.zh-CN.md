<!-- locale: zh-CN -->

# web-access 技能

## L0：一句话摘要

四层联网访问工具包——搜索公开页面、Jina 优化抓取、BrowserXxx 内置工具家族（v2.0）、Python Playwright CDP 兜底。

## L1：概述与使用场景

### 能力描述

web-access 是一个**流程型技能（Procedural Skill）**，提供四层互补的联网访问能力：

- **L1**（WebSearch + WebFetch）：公开页面，轻量
- **L2**（Jina Reader）：JS 渲染的重页面，默认节省 Token
- **L3-fast**（BrowserXxx 内置工具家族，**v2.0 新增**）：登录态站点首选——零 Python 依赖、内置 cdp-proxy 子进程、支持 CDP 真实鼠标事件
- **L3-fallback**（Chrome CDP + Python Playwright）：复杂自动化场景兜底（长等待、特殊 race condition 等）

### v2.0 新增：BrowserXxx 工具家族（默认隐藏，激活后才暴露）

调用 `Skill('web-access')` 加载本技能时，以下 11 个工具被注入到当前会话，让 LLM 直接驱动浏览器：

| 工具 | 用途 |
|------|------|
| BrowserListTabs / BrowserNavigate / BrowserCloseTab | tab 管理 |
| BrowserEval | 执行 JS 提取数据 |
| BrowserClick (`mode: js \| real-mouse`) | 点击元素，real-mouse 反爬更强 |
| BrowserScreenshot / BrowserScroll | 截图、滚动触发懒加载 |
| BrowserSetFiles | 上传本地文件（需用户确认） |
| SitePatternRead / SitePatternWrite | 按域名累积"站点经验"（AgentFS 三层） |
| LocalBookmarks | 检索本地 Chrome 书签 / 历史 |

> **重要**：未调用 Skill('web-access') 之前，这些工具**不会**出现在 LLM 的 tools 列表里——默认对话不消耗其 token。详见 [references/browser-tools.md](references/browser-tools.md)。

### 使用场景

- 用户需要搜索当前信息或研究特定主题
- 用户需要抓取公开网页内容或技术文档
- 用户需要访问登录态站点（小红书、B站、微博、飞书、Twitter 等）
- 用户需要对比产品、聚合新闻或调查 API/库版本

### 核心价值

- **四层递进**：从轻量搜索到重度 JS 渲染到登录态访问，按需选择
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
        ├─→ **Default: BrowserXxx tools** (BrowserNavigate / BrowserEval / BrowserClick / BrowserScreenshot —
        │     see references/browser-tools.md, no Python needed)
        └─→ Fallback: CDP + Python Playwright (references/cdp-browser.md) when BrowserXxx is insufficient
            (e.g., complex race conditions, multi-event waits, long-running in-browser scripts)
```

### 四层策略总结

| Layer | Use case | Primary tool | Token cost |
|-------|----------|--------------|------------|
| L1 | Public, static | `WebFetch` | Low |
| L2 | JS-heavy, long articles, token savings | `Bash curl r.jina.ai` | **Lowest** (Markdown pre-cleaned) |
| **L3-fast** | **Login-gated, interactive (PRIMARY)** | **BrowserXxx 工具家族** | Medium |
| L3-fallback | 复杂自动化（race / long-wait / 自定义脚本） | `Bash + Python Playwright CDP` | Medium |

**Default priority**: L1 for simple public pages → L2 for heavy → **L3-fast for login-gated** → L3-fallback only when BrowserXxx 不够用。

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

## L3-fast: BrowserXxx 工具速查（v2.0 推荐）

**只在你调用 `Skill('web-access')` 加载本技能后，下面这组工具才会出现在 tools[] 里。**

| 工具 | 一行示例 |
|------|---------|
| `BrowserListTabs()` | 列出所有打开 tab |
| `BrowserNavigate({ url })` | 在新 tab 打开 URL |
| `BrowserNavigate({ target, url })` | 在指定 tab 跳转 |
| `BrowserEval({ target, expression })` | 在 tab 内跑 JS，提取结构化数据 |
| `BrowserClick({ target, selector, mode: 'real-mouse' })` | 反爬严格站点用真实鼠标事件 |
| `BrowserScreenshot({ target })` | 写入 ${DESIRECORE_ROOT}/screenshots/ |
| `BrowserScroll({ target, direction: 'bottom' })` | 触发懒加载 |
| `BrowserSetFiles({ target, selector, files })` | 上传本地文件（**需用户确认**） |
| `BrowserCloseTab({ target })` | 任务收尾清理临时 tab |

完整 API 与边界条件见 [references/browser-tools.md](references/browser-tools.md)。

### 推荐流程（小红书示例）

```
1. BrowserListTabs() → 看是否已有登录态 tab
2. 没有 → BrowserNavigate({ url: "https://www.xiaohongshu.com/explore/abc123" })
3. BrowserEval({ target, expression: "(...)JSON.stringify({title, content})" })
4. SitePatternRead({ domain: "xiaohongshu.com" })  ← 读累积经验
5. 任务结束 → BrowserCloseTab({ target })
6. 如发现新陷阱 → SitePatternWrite({ domain, scope: "agent", mode: "merge", content })
```

---

## 站点经验积累（v2.0 新增）

任务结束如果发现新的反爬陷阱、有效选择器、平台特征，调用：

```
SitePatternWrite({
  domain: "xiaohongshu.com",
  scope: "agent",     // agent=共享（受 Git 管理，发布给其他用户）；user=私有
  mode: "merge",      // merge 追加，replace 覆盖
  content: "## 已知陷阱\n- 2026-05: ...",
  confidence: "medium"
})
```

读取走三层优先级：

```
SitePatternRead({ domain: "xiaohongshu.com" })
  → users/<userId>/agents/<agentId>/memory/site-patterns/   (用户私有)
  → agents/<agentId>/memory/site-patterns/                  (Agent 共享, Git)
  → defaults/global-skills/web-access/references/site-patterns/  (全局基线，只读)
```

含 cookie / token / 手机号 / 邮箱时 SitePatternWrite **自动降级 scope='user'** 并提示。

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
- ❌ **(v2.0) 在能用 BrowserXxx 时仍写 Python heredoc** — 慢、依赖 Python+Playwright 安装、上下文体积大。优先 L3-fast；只在 BrowserXxx 不够（race / 长等待 / 自定义脚本）时才回退。
- ❌ **(v2.0) 任务结束发现新陷阱却不写 site-pattern** — 下次同 Agent 再做相同任务会重复踩坑。任何"花了 2+ 步才搞清楚的细节"都值得 `SitePatternWrite(scope='agent', mode='merge')`。
- ❌ **(v2.0) 把含 cookie / 手机号的内容写到 scope='agent'** — 这层会被 Git 提交、可能发布到市场。SitePatternWrite 会自动降级，但你不该故意往 agent 层写敏感信息。

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
