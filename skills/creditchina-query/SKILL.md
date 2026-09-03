---
name: creditchina-query
description: >-
  信用中国企业信用信息查询——输入企业名称，自动通过图形验证码（ddddocr 本地 OCR 100ms），返回信用信息（行政处罚/失信被执行/行政许可）。Use when 用户提到"查信用"、"信用中国"、"行政处罚"、"失信企业"、"企业信用"、"失信被执行人"、"行政许可"、"creditchina"。
version: 1.0.0
type: procedural
risk_level: high
status: enabled
tags:
  - due-diligence
  - credit
  - creditchina
  - compliance
metadata:
  author: desirecore
  updated_at: '2026-09-03'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 信用中国查询
      short_desc: 浏览器自动化 + ddddocr 本地过验证码，返回企业信用信息
      description: >-
        信用中国企业信用信息查询——输入企业名称，自动通过图形验证码（ddddocr 本地 OCR 100ms），返回信用信息（行政处罚/失信被执行/行政许可）。Use when 用户提到"查信用"、"信用中国"、"行政处罚"、"失信企业"、"企业信用"、"失信被执行人"、"行政许可"、"creditchina"。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:ae28ca7a89d99438
      translated_by: human
    en-US:
      name: Credit China Query
      short_desc: Browser automation with local ddddocr captcha solving for enterprise credit records
      description: >-
        Credit China (creditchina.gov.cn) enterprise credit query — input a company name, automatically pass the graphic captcha (ddddocr local OCR, ~100 ms), and return credit records (administrative penalties / dishonest debtors / administrative licenses). Use when the user asks about enterprise credit, administrative penalties, dishonest-debtor lists, or creditchina.
      body: ./SKILL.md
      source_hash: sha256:ae28ca7a89d99438
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 4v16M8 20h8M4 8h16M6.5 8 4 13.5a3 3 0 0 0 5 0L6.5 8Zm11 0L15 13.5a3 3 0 0 0 5 0L17.5 8Z" stroke="#007AFF" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
  category: business
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.115
---

# Credit China Query

## L0: One-Sentence Summary

Input a company name, pass the graphic captcha automatically via Kimi WebBridge plus ddddocr local OCR, and return the enterprise's credit records.

## L1: Overview

- **Data source**: Credit China (`creditchina.gov.cn`, guided by NDRC)
- **Auth**: graphic captcha (solved locally by ddddocr, ~100 ms)
- **Invocation**: Kimi WebBridge + CDP screenshot + ddddocr Python OCR
- **Prerequisites**:
  - Kimi WebBridge daemon running
  - Python with `ddddocr` (`pip install ddddocr`)
  - Python with `Pillow` (`pip install pillow`)

## L2: Procedure

### 1. Navigate to the search page

Write `C:\tmp\cc-nav.json`:

```json
{
  "action": "navigate",
  "args": {
    "url": "https://www.creditchina.gov.cn/xinyongxinxi/?keyword={company-name-URL-encoded}&scenesVal=default&tableName=credit_xyzx_tyshxydm",
    "newTab": true,
    "group_title": "信用中国查询"
  },
  "session": "creditchina-query"
}
```

```bash
curl.exe -s -X POST "http://127.0.0.1:10086/command" \
  -H "Content-Type: application/json" \
  --data-binary "@C:\tmp\cc-nav.json" --max-time 30
```

Wait 6 seconds.

### 2. Confirm the captcha overlay

Write `C:\tmp\cc-check.json`:

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var v=document.getElementById('vcode');var i=document.getElementById('vcodeimg');return JSON.stringify({vcode:v?v.getBoundingClientRect().width>0:false,vimg:i?i.getBoundingClientRect().width>0:false});})()"
  },
  "session": "creditchina-query"
}
```

If `vcode=true` and `vimg=true`, the captcha overlay is visible — continue.

### 3. Get the captcha image coordinates

Write `C:\tmp\cc-coord.json`:

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var img=document.getElementById('vcodeimg');if(!img)return 'no-img';var r=img.getBoundingClientRect();return JSON.stringify({x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height),dpr:window.devicePixelRatio});})()"
  },
  "session": "creditchina-query"
}
```

Record `x` / `y` / `w` / `h`.

### 4. CDP screenshot of the captcha region

> **Note**: the WebBridge screenshot action fails intermittently on this site (HTTP 000/400) — **always use CDP `Page.captureScreenshot` with the clip parameter**.

Write `C:\tmp\cc-shot.json` (replace `{x}` / `{y}` / `{w}` / `{h}`):

```json
{
  "action": "cdp",
  "args": {
    "method": "Page.captureScreenshot",
    "params": {
      "format": "png",
      "clip": { "x": {x}, "y": {y}, "width": {w}, "height": {h}, "scale": 1 }
    }
  },
  "session": "creditchina-query"
}
```

```bash
curl.exe -s -X POST "http://127.0.0.1:10086/command" \
  -H "Content-Type: application/json" \
  --data-binary "@C:\tmp\cc-shot.json" --max-time 40 -o "C:/tmp/cc-cdp-resp.json"
```

Decode the base64 payload and save the image:

```python
import json, base64
d = json.load(open(r'C:\tmp\cc-cdp-resp.json', encoding='utf-8'))
b64 = d.get('data', {}).get('data', '')
open(r'C:\tmp\cc-captcha.png', 'wb').write(base64.b64decode(b64))
```

### 5. ddddocr recognition (~100 ms)

```python
import ddddocr, sys, time
sys.stdout.reconfigure(encoding='utf-8')
ocr = ddddocr.DdddOcr(show_ad=False)
t0 = time.time()
with open(r'C:\tmp\cc-captcha.png', 'rb') as f:
    code = ocr.classification(f.read())
print(f'验证码: {code} ({(time.time()-t0)*1000:.0f}ms)')
open(r'C:\tmp\cc-code.txt', 'w').write(code)
```

### 6. Fill and submit the captcha

Write `C:\tmp\cc-submit.json` (replace `{code}`):

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var inp=document.getElementById('vcode');if(!inp)return 'no-input';var s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;s.call(inp,'{code}');inp.dispatchEvent(new Event('input',{bubbles:true}));inp.dispatchEvent(new Event('change',{bubbles:true}));for(var el of document.querySelectorAll('button, a, input[type=button]')){if((el.innerText||el.value||'').trim()==='验证'){el.click();break;}}return 'submitted';})()"
  },
  "session": "creditchina-query"
}
```

Wait 5 seconds.

### 7. Check the verification result

Write `C:\tmp\cc-result.json`:

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var t=document.body.innerText||'';if(t.includes('验证码错误'))return '验证码错误';if(t.includes('失效'))return '验证码已失效';return JSON.stringify({hasResult:t.includes('共')||t.includes('条'),textSample:t.slice(0,500)});})()"
  },
  "session": "creditchina-query"
}
```

**Three outcomes**:

- `"验证码错误"` / `"验证码已失效"` → retry from step 3 (click 换一张 to refresh)
- `hasResult=true` with data → success, go to step 8
- `textSample` contains "很抱歉，没有找到您搜索的数据" → captcha passed but the keyword has no match — retry with the full name or a short name

### 8. Read the search results

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){return document.body.innerText.slice(0,1500);})()"
  },
  "session": "creditchina-query"
}
```

### 9. Normalized mapping

```json
{
  "query_status": "success",
  "source": "creditchina",
  "company_name": "{company name}",
  "captcha_solved": true,
  "search_result": "有结果 | 无匹配",
  "credit_info": [
    {
      "event_type": "行政处罚 | 行政许可 | 失信被执行 | 守信激励",
      "event_title": "...",
      "event_date": "...",
      "source_url": "...",
      "summary": "..."
    }
  ],
  "timestamp": "2026-08-31T21:00:00+08:00"
}
```

### 10. Close the session

```json
{
  "action": "close_session",
  "session": "creditchina-query"
}
```

## Retry Strategy

On captcha failure (wrong/expired), retry automatically up to 3 rounds:

1. Click 换一张 to refresh the captcha via `evaluate`
2. Wait 2 seconds for the new image
3. Repeat steps 3-6 (screenshot → recognize → submit)

After 3 failed rounds: ask the user to solve the captcha manually once in the browser, then resume — once verified, the browser remembers the state and subsequent queries skip the captcha.

## Known Limitations

- **Very short captcha TTL**: screenshot-to-submit must stay under ~15 s — **use ddddocr locally (~100 ms); cloud OCR (10-30 s round trips) always times out**
- **CDP screenshot required**: the WebBridge screenshot action fails intermittently here; use CDP `Page.captureScreenshot` with clip
- **Verification caching**: once passed, subsequent searches (navigating to new keyword URLs) return results without another captcha
- **CORS**: `fetch+FileReader` or `canvas.toDataURL` cannot capture the image (cross-origin taint) — CDP screenshots only
- **Keyword advice**: exact full names may return "no data" (the database only covers entities with credit records) — try the full name first, then the short name

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| 412 on direct HTTP | WAF blocks non-browser calls | always go through WebBridge |
| Captcha overlay missing | keyword param not triggered | check the keyword in the URL |
| Empty CDP screenshot | wrong coordinates / scrolled page | re-read `vcodeimg` bounding rect |
| ddddocr returns empty | broken image / recognition failure | refresh and retry; confirm screenshot bytes > 3000 |
| Wrong/expired captcha | misread / timeout | refresh (up to 3 rounds); fall back to manual |
| "没有找到您搜索的数据" | no credit records / keyword mismatch | retry with the short name |
