---
name: cnipa-patent-search
description: >-
  国家知识产权局专利检索——输入企业名称（作为申请人），返回专利列表（申请号/申请日/发明名称/专利类型/专利状态/主分类号/申请人/发明人/公开号/公开日/代理机构）。Use when 用户提到"查专利"、"知识产权"、"专利检索"、"专利申请"、"cnipa"、"pss-system"、"发明"、"实用新型"、"外观设计"、"专利状态"。
version: 1.0.0
type: procedural
risk_level: medium
status: enabled
tags:
  - due-diligence
  - patent
  - cnipa
  - intellectual-property
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
      name: 知识产权局专利检索
      short_desc: 登录态检索 pss-system，返回企业专利列表（申请号/类型/状态等）
      description: >-
        国家知识产权局专利检索——输入企业名称（作为申请人），返回专利列表（申请号/申请日/发明名称/专利类型/专利状态/主分类号/申请人/发明人/公开号/公开日/代理机构）。Use when 用户提到"查专利"、"知识产权"、"专利检索"、"专利申请"、"cnipa"、"pss-system"、"发明"、"实用新型"、"外观设计"、"专利状态"。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:08c8cb6ca63c6dd9
      translated_by: human
    en-US:
      name: CNIPA Patent Search
      short_desc: Logged-in pss-system patent search by applicant company name
      description: >-
        CNIPA patent search — input a company name (as applicant) and return a patent list (application number / date / title / type / status / main class / applicant / inventors / publication). Use when the user asks about patents, intellectual property, patent applications, cnipa, pss-system, inventions, utility models, or designs.
      body: ./SKILL.md
      source_hash: sha256:08c8cb6ca63c6dd9
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M9 18h6M10 21h4" stroke="#34C759" stroke-width="1.6" stroke-linecap="round"/><path d="M12 3a6.5 6.5 0 0 0-3.5 12c.6.45 1 1.15 1 1.9V18h5v-1.1c0-.75.4-1.45 1-1.9A6.5 6.5 0 0 0 12 3Z" stroke="#FFCC00" stroke-width="1.6" stroke-linejoin="round"/></svg>
  category: business
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.115
---

# CNIPA Patent Search

## L0: One-Sentence Summary

Input a company name, drive the CNIPA pss-system patent search via Kimi WebBridge browser automation, and return a structured patent list.

## L1: Overview

- **Data source**: CNIPA Patent Search and Analysis System (`pss-system.cponline.cnipa.gov.cn`)
- **Auth**: logged-in account (**registration required** — anonymous search redirects to login)
- **Invocation**: Kimi WebBridge browser automation (navigate + evaluate + CDP insertText)
- **Prerequisites**:
  - Kimi WebBridge daemon running
  - the user has **logged into pss-system** in the browser (login persists; log in once and reuse)

## Account Registration

pss-system requires real-name registration (phone + SMS):

1. Open `https://pss-system.cponline.cnipa.gov.cn/` in the browser
2. Click "注册" and complete real-name registration
3. Log in once — the browser keeps the session for later automation

## L2: Procedure

### 1. Check the WebBridge daemon

```bash
~/.kimi-webbridge/bin/kimi-webbridge.exe status
```

If down or disconnected, start it: `kimi-webbridge.exe start`.

### 2. Navigate to pss-system

Write `C:\tmp\cnipa-nav.json`:

```json
{
  "action": "navigate",
  "args": {
    "url": "https://pss-system.cponline.cnipa.gov.cn/",
    "newTab": true,
    "group_title": "专利检索"
  },
  "session": "cnipa-patent"
}
```

```bash
curl.exe -s -X POST "http://127.0.0.1:10086/command" \
  -H "Content-Type: application/json" \
  --data-binary "@C:\tmp\cnipa-nav.json" --max-time 30
```

Wait 5 seconds.

### 3. Confirm login, accept the disclaimer, enter search

Write `C:\tmp\cnipa-agree.json`:

```json
{
  "action": "evaluate",
  "args": {
    "code": "(async function(){var txt=document.body.innerText||'';var hasLogout=txt.includes('退出');if(txt.includes('免责声明')){var btns=document.querySelectorAll('button.el-button--primary');for(var b of btns){if((b.innerText||'').replace(/\\s+/g,'')==='同意'){b.click();break;}}await new Promise(function(r){setTimeout(r,4000);});}txt=document.body.innerText||'';return JSON.stringify({url:location.href.slice(0,80),isSearch:txt.includes('常规检索'),inputs:document.querySelectorAll('input').length,hasLogout:hasLogout});})()"
  },
  "session": "cnipa-patent"
}
```

**Login check**: if `hasLogout=false`, the user must log into pss-system in the browser first.

### 4. Focus the search box + CDP input

Write `C:\tmp\cnipa-focus.json`:

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){for(var i of document.querySelectorAll('input')){if((i.placeholder||'').includes('请输入关键词')){i.value='';i.dispatchEvent(new Event('input',{bubbles:true}));i.focus();return 'focused';}}return 'not-found';})()"
  },
  "session": "cnipa-patent"
}
```

Then write `C:\tmp\cnipa-insert.json` (CDP real input, Vue-compatible):

```json
{
  "action": "cdp",
  "args": {
    "method": "Input.insertText",
    "params": { "text": "{company name}" }
  },
  "session": "cnipa-patent"
}
```

### 5. Click search + wait for results

Write `C:\tmp\cnipa-click.json`:

```json
{
  "action": "evaluate",
  "args": {
    "code": "(async function(){var clicked=false;for(var el of document.querySelectorAll('div.btn')){if((el.innerText||'').replace(/\\s+/g,'')==='检索'){el.click();clicked=true;break;}}await new Promise(function(r){setTimeout(r,8000);});var tables=document.querySelectorAll('table').length;var rows=document.querySelectorAll('table tr').length;var hits=(document.body.innerText.match(/共[\\d,]+[条篇]/)||[])[0]||'';return JSON.stringify({clicked:clicked,url:location.href.slice(0,80),tables:tables,rows:rows,hits:hits});})()"
  },
  "session": "cnipa-patent"
}
```

### 6. Extract the result table

Write `C:\tmp\cnipa-table.json`:

```json
{
  "action": "evaluate",
  "args": {
    "code": "(function(){var table=document.querySelector('table');if(!table)return JSON.stringify({err:'no-table'});var headers=[];table.querySelectorAll('thead th').forEach(function(th){headers.push((th.innerText||'').trim())});var rows=[];table.querySelectorAll('tbody tr').forEach(function(tr){var cells=[];tr.querySelectorAll('td').forEach(function(td){cells.push((td.innerText||'').trim().slice(0,60))});rows.push(cells)});return JSON.stringify({headers:headers,rowCount:rows.length,rows:rows});})()"
  },
  "session": "cnipa-patent"
}
```

### 7. Normalized mapping

```json
{
  "query_status": "success",
  "source": "cnipa",
  "company_name": "{company name}",
  "total_found": 1,
  "patents": [
    {
      "patent_number": "202310104843.5",
      "application_date": "2023.01.16",
      "patent_name": "一种通信方法及装置",
      "patent_type": "发明",
      "patent_status": "实质审查的生效",
      "main_class_code": "H04W72/54",
      "applicant": "华为技术有限公司",
      "applicant_address": "广东省深圳市",
      "publication_number": "CN117834529A",
      "publication_date": "2024.04.05"
    }
  ],
  "timestamp": "2026-08-31T21:00:00+08:00"
}
```

### 8. Close the session

```json
{
  "action": "close_session",
  "session": "cnipa-patent"
}
```

## Known Limitations

- **Login required**: anonymous searches redirect to login or silently fail (unstable behavior); logged-in sessions return results reliably
- **Session persistence**: browser cookies keep the login valid for a long time, but re-login may be needed after long idle periods
- **Vue compatibility**: real input must go through CDP `Input.insertText` (not DOM setters), otherwise the Vue autocomplete ignores the text
- **Pagination**: when results exceed 10, click the pager and extract each page

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Search click redirects to login | not logged in | log into pss-system in the browser |
| Search click does nothing | Vue event not triggered | confirm CDP insertText was used; check the login state |
| Table empty | async results loading | retry extraction after 8 s |
| Stuck on the disclaimer | agree button not clicked | re-run the evaluate that clicks 同意 |
