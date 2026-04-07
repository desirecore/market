# Jina Reader — Default Token-Optimization Layer

[Jina Reader](https://jina.ai/reader) is a free public service that renders any URL server-side and returns clean Markdown. In this skill's three-layer architecture, **Jina is Layer 2: the default extractor for heavy/JS-rendered pages**, not just a fallback.

---

## Positioning in the three-layer model

```
L1 WebFetch            ── simple public static pages (docs, Wikipedia, HN)
    │
    │ WebFetch empty/truncated/garbled
    ▼
L2 Jina Reader         ── DEFAULT for JS-heavy SPAs, long articles, Medium, Twitter
    │                     Strips nav/ads automatically, saves 50-80% tokens
    │
    │ Login required, or Jina also fails
    ▼
L3 CDP Browser         ── user's logged-in Chrome (小红书/B站/微博/飞书/Twitter)
```

**Key insight**: Don't wait for WebFetch to fail before trying Jina. For any URL you expect to be JS-heavy (any major SPA, Medium, Dev.to, long-form articles), go straight to Jina for the token savings.

---

## Basic Usage (no API key)

```bash
curl -sL "https://r.jina.ai/https://example.com/article"
```

The original URL goes after `r.jina.ai/`. The response is plain Markdown — pipe to a file or read directly.

---

## When to use each layer

| Scenario | Primary choice | Why |
|----------|---------------|-----|
| Wikipedia, MDN, official docs | L1 WebFetch | Static clean HTML, fastest |
| GitHub README (public) | L1 WebFetch | Simple markup |
| Medium articles | **L2 Jina** | Member walls + heavy JS |
| Dev.to, Hashnode | **L2 Jina** | JS-rendered |
| Substack, Ghost blogs | **L2 Jina** | Partial JS rendering |
| News sites with lazy-load | **L2 Jina** | Scroll-triggered content |
| Twitter/X public threads | **L2 Jina** first, L3 CDP if truncated | Sometimes works |
| 公众号 (mp.weixin.qq.com) | **L2 Jina** | Clean Markdown extraction |
| LinkedIn articles | L3 CDP | Hard login wall |
| 小红书, B站, 微博, 飞书 | L3 CDP | 登录强制 |

---

## Token savings example

Raw HTML of a long Medium article: ~150 KB, ~50,000 tokens
Same article via Jina Reader: ~20 KB, ~7,000 tokens

**86% reduction**, with cleaner structure and no ads/nav cruft.

---

## Advanced Endpoints (optional)

If you need more than basic content extraction, Jina also offers:

- **Search**: `https://s.jina.ai/<query>` — returns top 5 results as Markdown
- **Embeddings**: `https://api.jina.ai/v1/embeddings` (requires free API key)
- **Reranker**: `https://api.jina.ai/v1/rerank` (requires free API key)

For DesireCore, prefer the built-in `WebSearch` tool over `s.jina.ai` for consistency.

---

## Rate Limits

- **Free tier**: ~20 requests/minute, no authentication needed
- **With free API key**: higher limits, fewer throttles
  ```bash
  curl -sL "https://r.jina.ai/https://example.com" \
       -H "Authorization: Bearer YOUR_KEY"
  ```
- Get a free key at [jina.ai](https://jina.ai) — stored in env var `JINA_API_KEY` if available

---

## Usage tips

### Cache your own results
Jina itself doesn't cache for you. If you call the same URL repeatedly in a session, save the Markdown to a temp file:

```bash
curl -sL "https://r.jina.ai/$URL" > /tmp/jina-cache.md
```

### Handle very long articles
Jina returns the full article in one response. For articles > 50K chars, pipe through `head` or extract specific sections with Python/awk before feeding back to the model context.

### Combine with CDP
When you use L3 CDP to fetch a login-gated page, you can pipe the resulting HTML through Jina for clean Markdown instead of parsing with BeautifulSoup:

```python
html = fetch_with_cdp(url)  # from references/cdp-browser.md
# Now convert via Jina (note: Jina fetches the URL itself, not your HTML)
# So this only works if the content is already visible without login:
import subprocess
md = subprocess.run(["curl", "-sL", f"https://r.jina.ai/{url}"],
                    capture_output=True, text=True).stdout
```

For truly login-gated content, you must parse the HTML directly (BeautifulSoup) since Jina can't log in on your behalf.

---

## Failure Mode

If Jina Reader returns garbage or error:
1. **Hard login wall** → escalate to L3 CDP browser
2. **Geographically restricted** → tell the user, suggest VPN or manual access
3. **Cloudflare challenge** → try L3 CDP (user's browser passes challenges naturally)
4. **404 / gone** → confirm the URL is correct

In all cases, tell the user explicitly which URL failed and what you tried.
