# CDP Browser Access — Login-Gated Sites Manual

Detailed recipes for accessing sites that require the user's login session, via Chrome DevTools Protocol (CDP) + Python Playwright.

**Precondition**: Chrome is already running with `--remote-debugging-port=9222` and the user has manually logged in to the target sites. See the main SKILL.md `Prerequisites` section for the launch command.

---

## Why CDP attach, not headless

| Approach | Login state | Anti-bot | Speed | Cost |
|----------|-------------|----------|-------|------|
| Headless Playwright (new context) | ❌ Empty cookies | ❌ Flagged as bot | Slow cold start | Re-login pain |
| `playwright.chromium.launch(headless=False)` | ❌ Fresh profile | ⚠ Sometimes flagged | Slow | Same |
| **CDP attach (`connect_over_cdp`)** | ✅ User's real cookies | ✅ Looks human | Instant | Zero friction |

**Rule**: For any login-gated site, always attach to the user's running Chrome.

---

## Core Template

Every CDP script follows this shape:

```python
from playwright.sync_api import sync_playwright

def fetch_with_cdp(url: str, wait_selector: str | None = None) -> str:
    """Attach to user's Chrome via CDP, fetch URL, return HTML."""
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        # browser.contexts[0] is the user's default context (with cookies)
        context = browser.contexts[0]
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=10000)
            else:
                page.wait_for_timeout(2000)  # generic settle
            return page.content()
        finally:
            page.close()
            # DO NOT call browser.close() — that would close the user's Chrome!

if __name__ == "__main__":
    html = fetch_with_cdp("https://example.com")
    print(html[:1000])
```

**Critical**: Never call `browser.close()` when using CDP attach — you'd kill the user's Chrome. Only close the page you opened.

---

## Site Recipes

### 小红书 (xiaohongshu.com)

```python
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

NOTE_URL = "https://www.xiaohongshu.com/explore/XXXXXXXX"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    page = browser.contexts[0].new_page()
    page.goto(NOTE_URL, wait_until="domcontentloaded")
    page.wait_for_selector("#detail-title", timeout=10000)
    page.wait_for_timeout(1500)  # let images/comments load
    html = page.content()
    page.close()

soup = BeautifulSoup(html, "html.parser")
title = (soup.select_one("#detail-title") or {}).get_text(strip=True) if soup.select_one("#detail-title") else None
desc  = (soup.select_one("#detail-desc") or {}).get_text(" ", strip=True) if soup.select_one("#detail-desc") else None
author = soup.select_one(".author-wrapper .username")
print("Title:",  title)
print("Author:", author.get_text(strip=True) if author else None)
print("Desc:",   desc)
```

**Selectors** (may drift over time — update if they fail):
- Title: `#detail-title`
- Description: `#detail-desc`
- Author: `.author-wrapper .username`
- Images: `.swiper-slide img`
- Comments: `.parent-comment .content`

### B站 (bilibili.com)

```python
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

VIDEO_URL = "https://www.bilibili.com/video/BVxxxxxxxxx"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    page = browser.contexts[0].new_page()
    page.goto(VIDEO_URL, wait_until="networkidle")
    page.wait_for_timeout(2000)
    html = page.content()
    page.close()

soup = BeautifulSoup(html, "html.parser")
print("Title:", soup.select_one("h1.video-title").get_text(strip=True) if soup.select_one("h1.video-title") else None)
print("UP:",    soup.select_one(".up-name").get_text(strip=True) if soup.select_one(".up-name") else None)
print("Desc:",  soup.select_one(".desc-info-text").get_text(" ", strip=True) if soup.select_one(".desc-info-text") else None)
```

**Tip**: For B站 evaluations, the [公开 API](https://api.bilibili.com/x/web-interface/view?bvid=XXXX) often returns JSON without needing CDP. Try it first:

```bash
curl -s "https://api.bilibili.com/x/web-interface/view?bvid=BVxxxxxxxxx" | python3 -m json.tool
```

### 微博 (weibo.com)

```python
WEIBO_URL = "https://weibo.com/u/1234567890"  # or /detail/xxx

# Same CDP template
# Selectors:
#   .Feed_body_3R0rO .detail_wbtext_4CRf9    — post text
#   .ALink_default_2ibt1                      — user link
#   article[aria-label="微博"]                 — each feed item
```

**Note**: Weibo uses React + heavy obfuscation. Selectors change frequently. If selectors fail, pipe the HTML through Jina for clean Markdown:

```python
html = fetch_with_cdp(WEIBO_URL)
# Save to temp file, then:
import subprocess
result = subprocess.run(
    ["curl", "-sL", f"https://r.jina.ai/{WEIBO_URL}"],
    capture_output=True, text=True
)
print(result.stdout)
```

### 知乎 (zhihu.com)

```python
ANSWER_URL = "https://www.zhihu.com/question/123/answer/456"

# Selectors:
#   h1.QuestionHeader-title      — question title
#   .RichContent-inner            — answer body
#   .AuthorInfo-name              — author
```

Zhihu works with CDP but often also renders enough metadata server-side for Jina to work:

```bash
curl -sL "https://r.jina.ai/https://www.zhihu.com/question/123/answer/456"
```

Try Jina first, fall back to CDP if content is truncated.

### 飞书文档 (feishu.cn / larksuite.com)

```python
DOC_URL = "https://xxx.feishu.cn/docs/xxx"

# Feishu uses heavy virtualization — must scroll to load all content.
# Recipe:

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    page = browser.contexts[0].new_page()
    page.goto(DOC_URL, wait_until="domcontentloaded")
    page.wait_for_selector(".docs-render-unit", timeout=15000)

    # Scroll to bottom repeatedly to load lazy content
    last_height = 0
    for _ in range(20):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(800)
        h = page.evaluate("document.body.scrollHeight")
        if h == last_height:
            break
        last_height = h

    # Extract text
    text = page.evaluate("() => document.body.innerText")
    page.close()

print(text)
```

### Twitter / X

```python
TWEET_URL = "https://x.com/username/status/1234567890"

# Selectors:
#   article[data-testid="tweet"]         — tweet container
#   div[data-testid="tweetText"]          — tweet text
#   div[data-testid="User-Name"]          — author
#   a[href$="/analytics"]                 — view count anchor (next sibling has stats)
```

Twitter is aggressive with anti-bot. CDP attach usually works, but set a generous wait:

```python
page.goto(url, wait_until="networkidle", timeout=45000)
page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
```

---

## Common Patterns

### Pattern 1: Scroll to load lazy content

```python
def scroll_to_bottom(page, max_steps=30, pause_ms=800):
    last = 0
    for _ in range(max_steps):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(pause_ms)
        h = page.evaluate("document.body.scrollHeight")
        if h == last:
            return
        last = h
```

### Pattern 2: Screenshot a specific element

```python
element = page.locator("article").first
element.screenshot(path="/tmp/article.png")
```

### Pattern 3: Extract structured data via JavaScript

```python
data = page.evaluate("""() => {
    const items = document.querySelectorAll('.list-item');
    return Array.from(items).map(el => ({
        title: el.querySelector('.title')?.innerText,
        url:   el.querySelector('a')?.href,
    }));
}""")
print(data)
```

### Pattern 4: Fill a form and click

```python
page.fill("input[name=q]", "search query")
page.click("button[type=submit]")
page.wait_for_load_state("networkidle")
```

### Pattern 5: Clean HTML via Jina after extraction

When selectors are unreliable, dump the full page HTML and let Jina do the cleaning:

```python
html = page.content()
# Save to file, serve via local HTTP, or just pipe the original URL:
import subprocess
clean_md = subprocess.run(
    ["curl", "-sL", f"https://r.jina.ai/{url}"],
    capture_output=True, text=True
).stdout
print(clean_md)
```

---

## Troubleshooting

### `connect_over_cdp` fails with `ECONNREFUSED`

Chrome is not running with remote debugging. Tell the user:
> "请先用下面的命令启动 Chrome：
> `/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir=\"$HOME/.desirecore/chrome-profile\"`
> 然后手动登录需要抓取的网站，再让我继续。"

### `browser.contexts[0]` is empty

Chrome was launched but no windows are open. Ask the user to open at least one tab and navigate anywhere.

### Playwright not installed

```bash
pip3 install playwright beautifulsoup4
# No need for `playwright install` — we're attaching to existing Chrome, not downloading a new browser
```

### Site detects automation

Despite CDP attach, some sites (Cloudflare-protected, Instagram) may still detect automation. Options:
1. Use Jina Reader instead (`curl -sL https://r.jina.ai/<url>`) — often succeeds where Playwright fails
2. Ask the user to manually copy the visible content
3. Use the site's public API if available

### Content is truncated

The page uses virtualization or lazy loading. Apply Pattern 1 (scroll to bottom) before calling `page.content()`.

### `page.wait_for_selector` times out

The selector is stale — the site updated its DOM. Dump `page.content()[:5000]` and inspect manually, or fall back to Jina Reader.

---

## Security Notes

- **Never log or print cookies** from `context.cookies()` even during debugging
- **Never extract and store** the user's session tokens to files
- **Never use the CDP session** to perform writes (post, comment, like) unless the user explicitly requested it
- The `~/.desirecore/chrome-profile` directory contains the user's credentials — treat it as sensitive
- If the user asks to "log in automatically", refuse and explain they must log in manually in the Chrome window; the skill only reads already-authenticated sessions

---

## When NOT to use CDP

- **Public static sites** → use L1 `WebFetch`, it's faster
- **Heavy SPAs without login walls** → use L2 Jina Reader, it's cheaper on tokens
- **You need thousands of pages** → CDP is not built for scale; look into proper scrapers

CDP is specifically the "right tool" for: **small number of pages + login required + human-like behavior needed**.
