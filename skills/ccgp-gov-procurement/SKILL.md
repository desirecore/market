---
name: ccgp-gov-procurement
description: >-
  中国政府采购网招标公告查询——输入企业名称（或简称），搜索该企业参与的采购公告，返回公告列表（标题/链接/日期）并可深度提取详情字段（项目编号/采购人/代理机构/更正内容/联系人）。Use when 用户提到"查招投标"、"政府采购"、"采购公告"、"中标公告"、"招标信息"、"ccgp"、"企业中标"。
version: 1.0.0
type: procedural
risk_level: medium
status: enabled
tags:
  - due-diligence
  - procurement
  - government
  - bidding
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
      name: 政府采购网招标查询
      short_desc: 输入企业名称（建议简称），返回采购公告列表与详情字段
      description: >-
        中国政府采购网招标公告查询——输入企业名称（或简称），搜索该企业参与的采购公告，返回公告列表（标题/链接/日期）并可深度提取详情字段（项目编号/采购人/代理机构/更正内容/联系人）。Use when 用户提到"查招投标"、"政府采购"、"采购公告"、"中标公告"、"招标信息"、"ccgp"、"企业中标"。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:b5c84bd5f84eeb34
      translated_by: human
    en-US:
      name: CCGP Procurement Search
      short_desc: Search China Government Procurement announcements by company name
      description: >-
        China Government Procurement (ccgp.gov.cn) announcement search — input a company name (short name recommended) and return procurement announcements (title / link / date), with optional deep extraction of detail fields (project number / purchaser / agency / corrections / contacts). Use when the user asks about tenders, procurement announcements, winning bids, or ccgp.
      body: ./SKILL.md
      source_hash: sha256:b5c84bd5f84eeb34
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><rect x="5" y="4" width="14" height="17" rx="2.5" stroke="#5856D6" stroke-width="1.6"/><path d="M8.5 9.5h7M8.5 13h7M8.5 16.5h4" stroke="#5856D6" stroke-width="1.6" stroke-linecap="round"/></svg>
  category: business
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.115
---

# CCGP Government Procurement Search

## L0: One-Sentence Summary

Input a company name (short name recommended, e.g. "华为" instead of the full legal name), search ccgp.gov.cn via Kimi WebBridge browser automation, and return a structured list of procurement announcements.

## L1: Overview

- **Data source**: China Government Procurement search (`search.ccgp.gov.cn`)
- **Auth**: none (public search)
- **Invocation**: Kimi WebBridge browser automation (navigate + evaluate)
- **Prerequisites**: Kimi WebBridge daemon running (`127.0.0.1:10086`) + browser extension connected
- **Key advantage**: a browser session naturally avoids the IP throttling applied to direct curl calls

## L2: Procedure

### 1. Check the WebBridge daemon

```bash
curl -s -X POST "http://127.0.0.1:10086/command" \
  -H "Content-Type: application/json" \
  -d '{"action":"list_tabs","session":"ccgp-query"}' --max-time 10
```

If unreachable, start the daemon:

```bash
~/.kimi-webbridge/bin/kimi-webbridge.exe start
```

### 2. Navigate to the search results page

**Windows approach** (write JSON to a temp file to avoid encoding issues):

Write `C:\tmp\ccgp-nav.json`:

```json
{
  "action": "navigate",
  "args": {
    "url": "https://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=1&bidSort=0&pinMu=0&bidType=0&dbselect=bidx&kw={company-short-name-URL-encoded}",
    "newTab": true,
    "group_title": "政府采购网查询"
  },
  "session": "ccgp-query"
}
```

```bash
curl.exe -s -X POST "http://127.0.0.1:10086/command" \
  -H "Content-Type: application/json" \
  --data-binary "@C:\tmp\ccgp-nav.json" --max-time 30
```

Wait 5 seconds before continuing.

### 3. Extract the announcement list

Write `C:\tmp\ccgp-extract.json`:

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var txt=document.body.innerText||'';var total=(txt.match(/共找到\\s*(\\d+)\\s*条/)||[])[1]||'?';var items=[];document.querySelectorAll('a').forEach(function(a){var t=(a.innerText||'').replace(/\\s+/g,' ').trim();if(t.includes('{company-keyword}')&&t.length>10){var li=a.closest('li')||a.closest('div');var date='';if(li){var m=(li.innerText||'').match(/\\d{4}[-:]\\d{2}[-:]\\d{2}/);if(m)date=m[0];}items.push({title:t.slice(0,80),href:(a.href||'').slice(0,100),date:date});}});return JSON.stringify({total:total,count:items.length,items:items.slice(0,10)});})()"
  },
  "session": "ccgp-query"
}
```

```bash
curl.exe -s -X POST "http://127.0.0.1:10086/command" \
  -H "Content-Type: application/json" \
  --data-binary "@C:\tmp\ccgp-extract.json" --max-time 40
```

### 4. Deep extraction from detail pages (optional)

Navigate to each announcement's detail page and extract structured fields:

```json
{
  "action": "navigate",
  "args": { "url": "{announcement-detail-URL}" },
  "session": "ccgp-query"
}
```

Wait 5 seconds, then extract:

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var txt=document.body.innerText||'';var lines=txt.split('\\n').map(function(s){return s.trim();}).filter(function(s){return s.length>0;});var fields={};for(var i=0;i<lines.length-1;i++){var l=lines[i];var n=lines[i+1];if(/采购人|采购代理|项目名称|项目编号|采购方式|中标|金额|供应商|地址|联系人|电话|公告日期|品目|更正/.test(l)&&n.length<200){fields[l]=n;}}return JSON.stringify({title:document.title,url:location.href.slice(0,80),fields:fields});})()"
  },
  "session": "ccgp-query"
}
```

### 5. Normalized mapping

```json
{
  "query_status": "success",
  "source": "ccgp",
  "company_name": "{company name}",
  "total_found": 2,
  "announcements": [
    {
      "event_type": "招投标公告",
      "event_title": "乌兰察布职业学院物业服务（华为校区）采购更正公告（第一次）",
      "event_date": "2026-08-25",
      "source_url": "http://www.ccgp.gov.cn/cggg/dfgg/gzgg/...",
      "project_number": "WSZC-G-F-260032",
      "purchaser": "乌兰察布职业学院",
      "agency": "乌兰察布市公共资源交易中心",
      "contact": "栗春雨 0474-8305228",
      "correction": "投标截止时间 2026-09-02 → 2026-09-10"
    }
  ],
  "timestamp": "2026-08-31T21:00:00+08:00"
}
```

### 6. Pagination (optional)

If `total` > 10, change `page_index=2` in the URL and repeat steps 2-3. Keep ≥5-second intervals.

### 7. Close the session

```json
{
  "action": "close_session",
  "session": "ccgp-query"
}
```

## Known Limitations

- **Default time window is about one week**: results may be 0 — add `start_time` and `end_time` to the URL (e.g. `start_time=2026:01:01&end_time=2026:08:31`) or click the page's time filter
- **Title-keyword search**: matching happens on announcement titles, not a supplier dimension — full legal names rarely hit; use the short name
- **Polite pacing**: even browser sessions should keep ≥5 s between requests; do not hammer pagination
- **HTML coupling**: redesigns may break selectors — if extraction is empty, fall back to reading `document.body.innerText`

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| navigate fails | daemon down / extension disconnected | restart via `kimi-webbridge.exe start` |
| "频繁访问" (frequent-access) | IP throttling | browser sessions usually avoid it; wait 60 s and retry |
| Empty extraction | 0 results / selectors broken | check the keyword; fall back to `evaluate` reading `body.innerText` |
| Empty detail fields | async content not loaded | retry after 5 s |
