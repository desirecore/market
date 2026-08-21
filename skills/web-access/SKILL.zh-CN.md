<!-- locale: zh-CN -->

# web-access 技能

## L0：一句话摘要

联网访问工具包——搜索公开页面、Jina 优化抓取、内置受管浏览器完成登录态访问与交互，以及用户点名时接管他自己的 Chrome。

## L1：概述与使用场景

### 能力描述

web-access 是一个**流程型技能（Procedural Skill）**，提供四层互补的联网访问能力：

- **L1**（WebSearch + WebFetch）：公开页面，轻量
- **L2**（Jina Reader）：JS 渲染的重页面，默认节省 Token
- **L3**（内置受管浏览器，v3.0 能力面补全）：到达、操作并**读取**登录态/交互站点——每个任务独立 BrowserSpace 隔离、零 Python 依赖、每次动作都有可审计回执。批量取文（`page.extract-text`）、判别式等待（`page.wait`）、代码模式（`BrowserScript`）都在本层内闭环

- **L3-external**（用户自己的 Chrome，经 CDP + Python Playwright 接管）：**用户点名要用他自己那个浏览器时走这条**——他的登录态、他的窗口、他能全程看着并随时接管

关于 L3-external 的一段历史：v3.0 曾把它整个删掉，理由是「它存在的每一条技术理由（无批量取文通道、evaluate 不可用、截图必须串行 activate）都已被内置浏览器覆盖」。那个技术判断没错，**作为「内置浏览器不够用时的兜底」它确实不再需要**。但删除时顺带丢掉了一个完全不同的用例：用户想用**他自己那个**浏览器。这跟能力够不够无关，内置浏览器替代不了，所以 v3.2 把它作为一条**由用户意图触发**的平级选择恢复回来——注意它不再是 fallback，判据见下方「两个浏览器，按用户意图选」。

### v3.0：内置受管浏览器（默认隐藏，激活后才暴露）

调用 `Skill('web-access')` 加载本技能时，以下 9 个工具被注入到当前会话，让 LLM 直接驱动内置浏览器：

| 工具 | 用途 |
|------|------|
| BrowserManage | 建/销隔离 BrowserSpace、启动会话、管理标签页 |
| BrowserSnapshot | `semantic` / `text` / `accessibility` / `visual` 四种快照——读页面的主通道 |
| BrowserAct | 一次调用一个受管动作：导航、输入、取文、等待、元素操作、截图…… |
| BrowserScript | **代码模式**：一段异步 JS 连续下发浏览器命令，消除逐动作往返（信任级别等同 Bash） |
| BrowserImport | 从用户 Chrome/Edge/Firefox/Safari 配置导入 Cookie（需人工审批；**还需 Host 授予 `browser.import.*`，普通 `create_space` 会话拿不到**） |
| BrowserShare | 把 Space/Session 委派给其他 Agent（隔离 / 快照 / 写时复制 / 实时共享） |
| SitePatternRead / SitePatternWrite | 按域名累积"站点经验"（AgentFS 三层） |
| LocalBookmarks | 检索本地 Chrome 书签 / 历史 |

> **重要**：未调用 Skill('web-access') 之前，这些工具**不会**出现在 LLM 的 tools 列表里——默认对话不消耗其 token。详见 [references/browser-tools.md](references/browser-tools.md)。
>
> **v2.1 已移除**：`BrowserListTabs` / `BrowserNavigate` / `BrowserEval` / `BrowserClick` / `BrowserScreenshot` / `BrowserScroll` / `BrowserSetFiles` / `BrowserCloseTab` 及其背后的 cdp-proxy 已停用，调用会返回「该旧 BrowserXxx/cdp-proxy 入口已停用」。本版要求客户端 v10.0.98+；`page.extract-text` / `page.element` / `page.wait` / 内联 wait 块 / 跨源 iframe 快照需 v10.0.112+，`BrowserScript` 需包含 S17/S18 的更新版本。

### 使用场景

- 用户需要搜索当前信息或研究特定主题
- 用户需要抓取公开网页内容或技术文档
- 用户需要访问登录态站点（小红书、B站、微博、飞书、Twitter 等）并**读出正文**
- 用户需要在登录态下调站内接口取数（列表、评论、订单等）
- 用户需要对比产品、聚合新闻或调查 API/库版本

### 核心价值

- **分层递进**：从轻量搜索到重度 JS 渲染到登录态访问，按需选择；用户点名时还可直接用他自己的浏览器
- **Token 优化**：Jina Reader 默认减少 50-80% Token 消耗；`page.extract-text` 的 maxBytes/cursor 分页让登录态长文也可控
- **登录态复用**：Host 授予 `browser.import.*` 时用 BrowserImport 把 Cookie 导入隔离 Space，不必重新登录
- **默认零外部依赖**：内置浏览器不要求 Python/Playwright，也不要求用户手工启动调试 Chrome（L3-external 需要，且仅在用户点名时才用）

## L2：详细规范

## Output Rule

When you complete a research task, you **MUST** cite all source URLs in your response. Distinguish between:
- **Quoted facts**: directly from a fetched page → cite the URL
- **Inferences**: your synthesis or analysis → mark as "(分析/推断)"

If any fetch fails, explicitly tell the user which URL failed and which fallback you used.

## Prerequisites: Chrome CDP Setup（仅 L3-external 需要）

**只有走 L3-external（用户点名要用他自己的浏览器）时才需要这一步。** 内置浏览器零前置条件。

### One-time setup

让用户带远程调试端口启动 Chrome：

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

启动后：
1. 用户在这个 Chrome 里手工登录需要的站点
2. 这个 Chrome 窗口保持开着
3. 验证调试端点：`curl -s http://localhost:9222/json/version` 应返回 JSON

### 每次操作前先验就绪

```bash
curl -s http://localhost:9222/json/version | python3 -c "import sys,json; d=json.load(sys.stdin); print('CDP ready:', d.get('Browser'))"
```

失败就告诉用户：「请先启动 Chrome 并开启远程调试端口（见 web-access 技能的 Prerequisites 部分）」，
**然后等他**——不要因为内置浏览器也能做就擅自改用内置的。

⚠️ 用 CDP attach 时**绝不能调 `browser.close()`**，那会关掉用户自己的 Chrome；只关你开的 page。
完整配方见 [references/cdp-browser.md](references/cdp-browser.md)。

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
  │     └─→ BrowserManage(create_space/start_session) → BrowserAct(tab.navigate)
  │         → BrowserAct(page.extract-text)          ← 正文直接读出，支持 maxBytes/cursor 分页
  │         要登录态：仅在已授予 browser.import.* 时用 BrowserImport
  │
  ├─ "Pull data from the site's API in a logged-in context"
  │     └─→ fetch.browser 配方：BrowserAct(page.evaluate) 里跑 fetch（带该 origin 的 Cookie）
  │
  ├─ "API documentation / GitHub / npm package info"
  │     └─→ Prefer official API endpoints over scraping HTML:
  │          - GitHub: gh api repos/owner/name
  │          - npm:    curl https://registry.npmjs.org/<pkg>
  │          - PyPI:   curl https://pypi.org/pypi/<pkg>/json
  │
  └─ "Real-time interactive task" (click, fill form, scroll, screenshot)
        ├─→ **用户点名「我本机的 / 我自己的 / 外部的浏览器」** → L3-external：
        │     先验 CDP 就绪（见 Prerequisites），再 python3 playwright.connect_over_cdp()
        │     没就绪就给启动命令并等他，不要擅自改用内置浏览器
        └─→ **其余情况（默认）**：内置受管浏览器 (BrowserManage → BrowserAct → BrowserSnapshot —
             see references/browser-tools.md, no Python needed)
```

### 两个浏览器，按用户意图选，不按能力难度选

DesireCore 能驱动**两个**浏览器，它们是平级的选项：

| | L3 内置受管浏览器 | L3-external 用户自己的浏览器 |
|---|---|---|
| 是什么 | 应用内的浏览器实例（`Browser*` 工具族） | 用户机器上装的 Chrome，经 CDP + Python Playwright 接管 |
| 登录态 | 独立隔离；需 Host 授予 `browser.import.*` 才能用 `BrowserImport` 导 Cookie | **就是用户本人的登录态**，无需导入 |
| 用户能看到吗 | Agent 开的标签页默认离屏，需展示到工作台 | **就在用户自己的窗口里**，他能全程看着、随时接管 |
| 前置条件 | 无 | 用户需先带 `--remote-debugging-port=9222` 启动 Chrome（见 Prerequisites） |
| 默认 | ✅ 是 | 用户点名时 |

**选层判据是用户意图，不是技术难度。** v3.0 把这一层当作「内置浏览器不够用时的兜底」删掉过，
那个技术判断本身没错（取文、evaluate、截图这些内置浏览器现在都能做），但它顺带删掉的是一个
**完全不同的用例**：用户想用**他自己那个**浏览器。那跟能力够不够无关——他的登录态在他自己的
Chrome 里，他想亲眼看着操作、随时接管。这个需求内置浏览器替代不了。

**用户点名了就按点名的来：**

- 说「我本机的 / 我自己的 / 外部浏览器 / 我的 Chrome」→ 走 **L3-external**。先按
  Prerequisites 验 CDP 就绪；没就绪就告诉他启动命令并等他，**不要因为「内置浏览器也能做」
  就擅自改用内置的**
- 说「内置浏览器」或没点名 → 走 **L3 内置浏览器**（默认，零前置条件）
- 拿不准他指哪个 → 问一句，别猜

⚠️ 无论走哪条，都要让用户能分辨你实际用了哪个。不要用「本地浏览器」「本机的受管浏览器」
「已启动本地浏览器」这种两边都像的说法——用户要的和你给的不是一回事时，措辞必须让他一眼看出来。

### 分层策略总结

| Layer | Use case | Primary tool | Token cost |
|-------|----------|--------------|------------|
| L1 | Public, static | `WebFetch` | Low |
| L2 | JS-heavy, long articles, token savings | `Bash curl r.jina.ai` | **Lowest** (Markdown pre-cleaned) |
| **L3** | **登录态导航、交互与取文 (PRIMARY)** | **内置受管浏览器（BrowserManage / BrowserAct / BrowserSnapshot / BrowserScript）** | Medium |
| L3-external | **用户点名要用他自己的浏览器**；或需要他本人的登录态而 `BrowserImport` 不可用 | `Bash + Python Playwright connect_over_cdp`（见 references/cdp-browser.md） | Medium |

**Default priority**: L1 for simple public pages → L2 for heavy → **L3 for login-gated（含正文与站内接口取数）**。

> L3-external 不在这条默认排序里，因为它不由「能力够不够」决定，而由**用户点名**决定：
> 用户要他自己那个浏览器时直接走它，哪怕内置浏览器也做得到。判据见上方
> 「两个浏览器，按用户意图选」。

## Supported Sites Matrix

| Site | Recommended Layer | Notes |
|------|-------------------|-------|
| Wikipedia, MDN, official docs | L1 WebFetch | Static, clean HTML |
| GitHub README, issues, PRs | `gh api` (best) → L1 WebFetch | Prefer API |
| Hacker News, Reddit | L1 WebFetch | Public content |
| Medium, Dev.to | L2 Jina Reader | JS-rendered, member gates |
| Twitter/X | L3（或 L2 Jina with `x.com`） | Login required for full thread |
| 小红书 (xiaohongshu.com) | L3 内置浏览器 + BrowserImport | 强制登录；正文走 page.extract-text |
| B站 (bilibili.com) | L3 内置浏览器 + BrowserImport | 视频描述/评论需登录 |
| 微博 (weibo.com) | L3 内置浏览器 + BrowserImport | 长微博需登录 |
| 知乎 (zhihu.com) | L3 内置浏览器 + BrowserImport | 长文+评论需登录 |
| 飞书文档 (feishu.cn) | L3 内置浏览器 + BrowserImport | 必须登录 |
| 公众号 (mp.weixin.qq.com) | L2 Jina Reader | 通常公开，Jina 处理更干净 |
| LinkedIn | L3 内置浏览器 + BrowserImport | 登录墙 |

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

### Layer 2: Jina Reader（重页默认）

Jina Reader (`r.jina.ai`) 免费公共代理，服务端渲染页面并返回干净 Markdown。WebFetch 输出乱码/截断时的默认升级路径，JS 重页面的首选抓取器。

```bash
curl -sL "https://r.jina.ai/https://example.com/article"
```

Why Jina is the default token-saver:
- Strips nav/footer/ads automatically
- Handles JS-rendered SPAs
- Returns 50-80% fewer tokens than raw HTML
- No API key needed for basic use (~20 req/min)

See [references/jina-reader.md](references/jina-reader.md) for advanced endpoints and rate limits.

### Layer 3: 内置受管浏览器（登录态与交互）

完整命令面、能力档位与边界条件见 [references/browser-tools.md](references/browser-tools.md)。这里的循环是：

1. `BrowserManage(create_space)` → `BrowserManage(start_session)` 拿 sessionId + 首个 tab
2. 需要登录态 → `BrowserImport`（仅当 Host 已授予 `browser.import.*`；没有这层授权就无法复用用户 Cookie，告诉用户并按无登录态继续或放弃）
3. `BrowserAct(tab.navigate)` 到达页面
4. `BrowserSnapshot(semantic)` 拿可交互元素 `ref`（跨源 iframe 的元素也在同一棵树里，ref 全局连续编号）
5. 交互用 `input.*`（拟真轨迹）或 `page.element`（表单批量写）；等结果用 `page.wait` 或内联 wait 块
6. 取正文用 `BrowserSnapshot(text)` 或 `BrowserAct(page.extract-text)`；取接口数据用 fetch.browser 配方
7. 任务收尾 `BrowserManage(close_session)`

多动作连续编排（导航→快照→点击→等待→取文）可用 `BrowserScript` 一段脚本完成，省去逐动作 IPC 往返。

## L3 速查（v3.0）

### 读页面：按需求选通道

| 你要什么 | 用什么 | 说明 |
|----------|--------|------|
| 可交互元素 + `ref` / `loc=` 句柄 | `BrowserSnapshot({ mode: 'semantic' })` | 按钮/输入框/链接 + 每行 `[ref=eN]` 与（能产出时）`[loc=...]` 稳定选择器；跨源 iframe 元素同树 |
| 页面正文 | `BrowserSnapshot({ mode: 'text' })` 或 `BrowserAct({ action: 'page.extract-text' })` | markdown/text 两种格式；超 maxBytes 截断并给 nextCursor 续读（cursor 分页），不报错 |
| 辅助功能树 | `BrowserSnapshot({ mode: 'accessibility' })` | 尊重 `depth`（默认 50 上限 100）与 maxBytes 预算，超出截断+翻页，不再整体报错 |
| 页面长什么样 | `BrowserSnapshot({ mode: 'visual' })` 或 `BrowserAct({ action: 'page.screenshot' })` | 像素直接进结果（视觉模型当场看）；支持 `clip={x,y,width,height,scale}` 元素级裁剪放大（scale 最大 4）与 `captureBeyondViewport` 整页截图 |

### 命令面速览

`BrowserAct` 的 `action` 按用途分组（完整枚举见工具 schema）：

- **tab.***：`navigate` / `back` / `forward` / `reload` / `activate` / `close`
- **input.***：`move` / `click` / `double-click` / `drag` / `wheel` / `touch` / `pinch` / `key` / `text` —— 走输入拟真（#1808：UA/UA-CH 身份一致 + 真实轨迹），反检测站点的交互首选
- **page.element**（判别式 op × selector，九 op）：写类 `fill` / `select-option` / `check` / `uncheck` / `scroll-into-view`；读类 `get-attribute` / `bounding-box` / `count` / `all-inner-texts`。selector 说 `loc=` 方言或快照 `ref`（配 snapshotId）。`fill` 拒绝 `input[type=password]`
- **page.wait**（判别式 until，九种）：轮询型 `load` / `domcontentloaded` / `networkidle` / `selector` / `url` / `timeout` 超时返回 `waited:false`；事件型 `request` / `response` / `download` 超时抛错。默认 10s、上限 60s
- **内联 wait 块**：`tab.navigate` / `input.click` / `input.key` / `page.element{op:"fill"}` 的 `params.wait`（形态与 page.wait 同构）——一条回执完成「动作→等结果」，等待器先于动作注册，无跨 IPC 竞态
- **page.evaluate**：`{ expression, awaitPromise }`，返回值原样过界（超预算截断并标 `truncated`，不抛错）；能力档 `browser.page.evaluate` 走人工闸门（allow-all 模式免卡片）
- **page.extract-text / page.screenshot / page.wait**：见上表与 fetch.browser 配方

`loc=` 选择器方言（S7/S9）：`e<序号>`（须配签发该 ref 的快照 snapshotId）、`loc=css:` / `loc=role:` / `loc=text:` / `loc=testid:`、裸 CSS，可叠 `internal:nth/last/scope/filter`。未知前缀显式报错，绝不静默降级。

### 交互通道选用：input.* vs page.element

- **反检测站点（小红书/微博/B站等）一律优先 `input.*`**：走 #1808 的输入行为拟真（坐标派发、拟真轨迹、可视化可审计），配套身份一致性层让 UA/UA-CH 不带 Electron/Headless 痕迹
- **`page.element` 写类适用于表单批量填充等站点不检测的场景**：一次调用完成 fill/select-option/check，比逐元素 input.click+input.text 快得多
- **红线**：`page.element` 刻意不含 click——指针动作必须走 `input.*`，用 JS 直调 `el.click()` 会绕开全部拟真投入，属于明确禁止的回退

### fetch.browser 配方：带登录态取接口数据

登录态下取站内接口（列表、评论、订单等 JSON）的正解：在**页面上下文**里跑 `fetch`——自动带该 origin 的 Cookie，同 origin、受 Grant origins 约束，走 `page.evaluate` 已有闸门。这是 `BrowserAct({ action: 'page.evaluate' })` 的封装用法：

```yaml
BrowserAct:
  action: page.evaluate
  params:
    expression: |
      fetch('/api/v1/comments?page=1&size=20', {
        headers: { accept: 'application/json' }
      }).then(r => r.text())
    awaitPromise: true        # 默认 true；表达式返回 Promise 时等它 settle
```

要点：
- 先 `tab.navigate` 到该站任意页面（建立 origin 与 Cookie），再发 fetch；路径写相对路径，天然同 origin
- 返回值原样过界；大 JSON 用 `.text()` 拿原文自己截取，或分页多次取
- 只能访问当前 tab origin（Grant origins 约束）；跨站接口请先导航过去
- `page.evaluate` 属人工闸门能力：非 allow-all 模式会弹审批卡，向用户说明用途即可

### 推荐流程（小红书示例）

```
1. BrowserManage({ action: 'create_space', name: 'xhs-note', persistence: 'ephemeral' })
2. BrowserManage({ action: 'start_session', spaceId, capabilities: [...] })
   ← 显式列表是做减法；要滚动就把 browser.input.pointer.wheel 列进去，
     要取文就带 browser.observe.snapshot
3. 复用登录态：仅在 Host 已授予 browser.import.* 时走
   BrowserImport({ action: 'discover' → 'create_plan' → 'dry_run' → 'apply' })。
   没有这层授权就无法复用用户 Cookie——如实告诉用户，按无登录态继续或放弃。
4. BrowserAct({ action: 'tab.navigate', params: { url: 'https://www.xiaohongshu.com/explore/abc123' } })
5. BrowserSnapshot({ mode: 'semantic' })        ← 拿交互元素 ref（跨源 iframe 同树）
6. BrowserAct({ action: 'page.extract-text', params: { format: 'markdown' } })
   ← 正文直接读出；太长就传上一页返回的 nextCursor 续读
7. 需要确认渲染效果 → BrowserSnapshot({ mode: 'visual' })（像素直接可看）
8. SitePatternRead({ domain: 'xiaohongshu.com' })  ← 读累积经验
9. 任务结束 → BrowserManage({ action: 'close_session', sessionId })
10. 如发现新陷阱 → SitePatternWrite({ domain, scope: 'agent', mode: 'merge', content })
```

## 站点经验积累

任务结束如果发现新的反爬陷阱、有效选择器、平台特征，调用：

```
SitePatternWrite({
  domain: "xiaohongshu.com",
  scope: "agent",     // agent=共享（受 Git 管理，发布给其他用户）；user=私有
  mode: "merge",      // merge 追加，replace 覆盖
  content: "## 已知陷阱\n- 2026-08: ...",
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

## Common Workflows

Read [references/workflows.md](references/workflows.md) for detailed templates:
- 技术文档查询 (Tech docs lookup)
- 竞品对比研究 (Competitor research)
- 新闻聚合与时间线 (News aggregation)
- API/库版本调查 (Library version investigation)

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

- ❌ **Using WebFetch on obviously heavy sites** — Medium, Twitter, 小红书 will waste tokens or fail. Jump straight to L2/L3.
- ❌ **Fetching one URL at a time when you need 5** — batch in a single message.
- ❌ **Trusting a single source** — cross-check ≥ 2 sources for non-trivial claims.
- ❌ **Fetching the search result page itself** — WebSearch already returns snippets; fetch the actual articles.
- ❌ **Ignoring the cache** — WebFetch caches 15 min, reuse freely.
- ❌ **Scraping when an API exists** — GitHub, npm, PyPI, Wikipedia all have JSON APIs; 登录态站内接口走 fetch.browser 配方.
- ❌ **Forgetting the year in time-sensitive queries** — "best AI models" returns 2023 results; "best AI models 2026" returns current.
- ❌ **Hardcoding login credentials in scripts** — 登录态只能来自 BrowserImport 导入的 Cookie.
- ❌ **Citing only after the fact** — collect URLs as you fetch, not from memory afterwards.
- ❌ **(v3.0) 在反检测站点用 page.element 批量交互** — 它是 JS 直调，绕开拟真轨迹；反检测站点一律 `input.*`，`page.element` 只用于不检测场景的表单批量填充。
- ❌ **(v3.0) 用截图靠"看图读字"取正文** — `page.extract-text` / `BrowserSnapshot(text)` 直接给 markdown/text，带分页预算；截图留给版面确认与验证码这类必须看图的场合。
- ❌ **(v3.0) 逐动作往返还能忍时不换 BrowserScript** — 导航→快照→点击→等待→取文五连用一段脚本完成；但记住 BrowserScript 信任级别等同 Bash，脚本源码要过一次人工审批。
- ❌ **(v3.0) 任务结束发现新陷阱却不写 site-pattern** — 下次同 Agent 再做相同任务会重复踩坑。任何"花了 2+ 步才搞清楚的细节"都值得 `SitePatternWrite(scope='agent', mode='merge')`。
- ❌ **(v3.0) 把含 cookie / 手机号的内容写到 scope='agent'** — 这层会被 Git 提交、可能发布到市场。SitePatternWrite 会自动降级，但你不该故意往 agent 层写敏感信息。

## Example Interaction

**User**: "帮我抓一下这条小红书笔记的内容：https://www.xiaohongshu.com/explore/abc123"

**Agent workflow**:
```
1. 识别 → 小红书是 L3 登录态站点
2. BrowserManage(create_space + start_session)
   需要登录态 → 已授予 browser.import.* 就走 BrowserImport 四步；
   没授予 → 告诉用户无法复用登录态，按公开可见部分继续
3. BrowserAct(tab.navigate → 笔记 URL)
4. BrowserAct(page.extract-text, format: markdown)
   ← 正文直接读出；超预算就按 nextCursor 续读
5. 返回给用户时：
   - 引用原 URL
   - 引用正文事实，标注来源链接
6. 告知用户：「已通过内置浏览器抓取，原链接：[xhs](url)」
7. BrowserManage(close_session)
```
