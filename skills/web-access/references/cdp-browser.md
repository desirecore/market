# CDP Browser Access — Login-Gated Sites Manual

Detailed recipes for accessing sites through the user-approved external Chromium browser, via Chrome DevTools Protocol (CDP) + Python Playwright.

**Precondition**: `BrowserExternalProbe` has returned `ready` for the exact browser the user requested, that browser is running with its DesireCore-isolated profile, and the user has manually logged in to the target sites. Never infer readiness from a failed/successful `curl`; see the main SKILL.md status table.

The probe distinguishes these cases before Playwright is involved:

- requested browser not installed (`browser_not_installed`)
- browser installed but debug port closed (`debug_port_closed`)
- multiple browsers installed with no ready endpoint (`browser_choice_required`)
- a different browser owns the port (`browser_mismatch`)
- a non-CDP service owns the port (`invalid_cdp_endpoint`)
- desktop host cannot be inspected (`host_unavailable`)

Only `ready` permits `connect_over_cdp`. An alternative browser is a suggestion requiring user approval, never an automatic fallback.

---

## Why CDP attach, not headless

| Approach | Login state | Anti-bot | Speed | Cost |
|----------|-------------|----------|-------|------|
| Headless Playwright (new context) | ❌ Empty cookies | ❌ Flagged as bot | Slow cold start | Re-login pain |
| `playwright.chromium.launch(headless=False)` | ❌ Fresh profile | ⚠ Sometimes flagged | Slow | Same |
| **CDP attach (`connect_over_cdp`)** | ✅ Cookies from the DesireCore-isolated external profile where the user logged in manually | ✅ Looks human | Instant | Zero friction |

**Rule**: Attach only when the user named the external browser or explicitly accepted this route after
you explained why. BrowserImport being unavailable does not itself authorize switching to the user's
external browser.

---

## Core Template

Every CDP script follows this shape. `PROBE_PORT` must be the numeric `port` from the latest `ready`
`BrowserExternalProbe` result; never silently fall back to 9222 after probing another port.

```python
from playwright.sync_api import sync_playwright

PROBE_PORT: int | None = None  # Assign the exact BrowserExternalProbe ready result port.

def cdp_url(port: int | None) -> str:
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("invalid CDP port")
    return f"http://127.0.0.1:{port}"

def fetch_with_cdp(url: str, cdp_port: int, wait_selector: str | None = None) -> str:
    """Attach to the user-approved external Chromium profile, fetch URL, return HTML."""
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url(cdp_port))
        # contexts[0] is the DesireCore-isolated external profile where the user logged in manually.
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
            # DO NOT call browser.close() — that would close the user's external browser!

if __name__ == "__main__":
    if PROBE_PORT is None:
        raise RuntimeError(
            "Run BrowserExternalProbe first and assign the port from its ready result to PROBE_PORT."
        )
    html = fetch_with_cdp("https://example.com", PROBE_PORT)
    print(html[:1000])
```

**Critical**: Never call `browser.close()` when using CDP attach — you'd kill the user's external browser. Only close the page you opened.

---

## Site Recipes

### 小红书 (xiaohongshu.com)

```python
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

NOTE_URL = "https://www.xiaohongshu.com/explore/XXXXXXXX"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(cdp_url(PROBE_PORT))
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
    browser = p.chromium.connect_over_cdp(cdp_url(PROBE_PORT))
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

**Tip**: When the user did not require a specific browser, the [公开 API](https://api.bilibili.com/x/web-interface/view?bvid=XXXX) often returns JSON without needing CDP. Try it first. For an explicit external-browser request, ask before replacing that route with the API.

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

**Note**: Weibo uses React + heavy obfuscation. If the user did not require a specific browser and selectors fail, Jina can clean the page. For an explicit external-browser request, ask before changing the execution route:

```python
html = fetch_with_cdp(WEIBO_URL, PROBE_PORT)
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

When no browser was specified, try Jina first and fall back to the built-in browser if content is truncated. For an explicit external-browser request, do not replace that route without user approval.

### 飞书文档 (feishu.cn / larksuite.com)

```python
DOC_URL = "https://xxx.feishu.cn/docs/xxx"

# Feishu uses heavy virtualization — must scroll to load all content.
# Recipe:

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(cdp_url(PROBE_PORT))
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

When no browser was specified and selectors are unreliable, dump the full page HTML and let Jina do
the cleaning. For an explicit external-browser request, ask before replacing that route:

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

### `connect_over_cdp` fails after a `ready` probe

Do not guess that the browser is merely closed. Call `BrowserExternalProbe` again:

- `debug_port_closed` → show its current `launchCommand` and wait for the user
- `browser_mismatch` → report the actual/requested products and ask the user to correct or approve the change
- `browser_not_installed` → report that exact installation fact; alternatives require explicit approval
- `invalid_cdp_endpoint` → tell the user the port is not a valid CDP endpoint
- still `ready` → report the Playwright attach failure separately; do not switch to the built-in browser

### `browser.contexts[0]` is empty

The approved external Chromium browser is running but no windows are open. Ask the user to open at least one tab and navigate anywhere.

### Playwright not installed

First ensure the isolated venv exists, then run the import-only check with **that venv's interpreter**.
Do not generate or execute the attach script until this succeeds.

#### Unix-like hosts

```bash
test -x "<DESIRECORE_HOME>/runtime/external-browser-playwright/bin/python" || \
  python3 -m venv "<DESIRECORE_HOME>/runtime/external-browser-playwright"
if ! "<DESIRECORE_HOME>/runtime/external-browser-playwright/bin/python" -c 'import playwright'; then
  "<DESIRECORE_HOME>/runtime/external-browser-playwright/bin/python" -m pip install 'playwright==1.55.0' beautifulsoup4
fi
"<DESIRECORE_HOME>/runtime/external-browser-playwright/bin/python" -c 'import playwright' || {
  echo 'Playwright is still unavailable in the isolated venv' >&2
  exit 1
}
# No need for `playwright install` — we're attaching to an existing browser, not downloading one
```

#### Windows hosts

Use the `PowerShell` tool. Resolve `<DESIRECORE_HOME>` from the current DesireCore instance; do not
guess another instance's directory. The only permitted system/bootstrap `python.exe` use is running
`-m venv` when the isolated venv is missing. Never use the `Bash` tool, bare `python`, bare `pip`,
`pip --user`, or a global interpreter for any Playwright import, install, re-check, or attach step;
all of those steps must use the venv's `Scripts\python.exe`.

```powershell
$venv = Join-Path '<DESIRECORE_HOME>' 'runtime\external-browser-playwright'
$python = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    $bootstrapPython = (Get-Command python.exe -ErrorAction Stop).Source
    & $bootstrapPython -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw 'Failed to create the isolated Playwright venv.' }
}
& $python -c "import playwright"
if ($LASTEXITCODE -ne 0) {
    # Explain the missing dependency and obtain any required install approval first.
    & $python -m pip install 'playwright==1.55.0' beautifulsoup4
    if ($LASTEXITCODE -ne 0) { throw 'Failed to install Playwright in the isolated venv.' }
    & $python -c "import playwright"
    if ($LASTEXITCODE -ne 0) { throw 'Playwright is still unavailable in the isolated venv.' }
}
# Do NOT run `playwright install`; CDP attach uses the already-running external browser.
```

To run an attach script on Windows, do not send a Bash heredoc to PowerShell. Use a native
PowerShell here-string and explicit UTF-8 write:

```powershell
$scriptPath = Join-Path $env:TEMP ("desirecore-external-cdp-{0}.py" -f [guid]::NewGuid().ToString('N'))
$script = @'
# Paste the reviewed Python attach script here.
'@
try {
    [IO.File]::WriteAllText($scriptPath, $script, (New-Object Text.UTF8Encoding($false)))
    & $python $scriptPath
    if ($LASTEXITCODE -ne 0) { throw "Playwright attach failed with exit code $LASTEXITCODE." }
} finally {
    Remove-Item -LiteralPath $scriptPath -ErrorAction SilentlyContinue
}
```

Keep the environment isolated to DesireCore; do not install Playwright globally. A missing Playwright
dependency does not change a `ready` browser/CDP result and never authorizes fallback to BrowserManage.

### Site detects automation

Despite CDP attach, some sites (Cloudflare-protected, Instagram) may still detect automation. If the
user explicitly requested their external browser, ask before changing routes. Otherwise, options are:
1. Use Jina Reader instead (`curl -sL https://r.jina.ai/<url>`) — often succeeds where Playwright fails
2. Ask the user to manually copy the visible content
3. Use the site's public API if available

### Content is truncated

The page uses virtualization or lazy loading. Apply Pattern 1 (scroll to bottom) before calling `page.content()`.

### `page.wait_for_selector` times out

The selector is stale — the site updated its DOM. Dump `page.content()[:5000]` and inspect manually.
Only fall back to Jina Reader when no browser was specified; for an explicit external-browser request,
ask before changing the execution route.

---

## Security Notes

- **Never log or print cookies** from `context.cookies()` even during debugging
- **Never extract and store** the user's session tokens to files
- **Never use the CDP session** to perform writes (post, comment, like) unless the user explicitly requested it
- `${DESIRECORE_ROOT}/browser/external-profiles/<browser-id>` contains the manually established isolated login state — treat it as sensitive
- If the user asks to "log in automatically", refuse and explain they must log in manually in the approved external browser window; the skill only reads already-authenticated sessions

---

## When NOT to use CDP

- **Public static sites** → use L1 `WebFetch`, it's faster
- **Heavy SPAs without login walls** → use L2 Jina Reader, it's cheaper on tokens
- **You need thousands of pages** → CDP is not built for scale; look into proper scrapers

CDP is specifically the "right tool" for: **small number of pages + login required + human-like behavior needed**.
