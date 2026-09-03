---
name: tianyancha-risk
description: >-
  天眼查企业风险查询——输入企业名称，返回风险画像（自身风险/周边风险/历史风险/预警提醒，含分类统计与明细）。Use when 用户提到"查风险"、"企业风险"、"风险画像"、"司法风险"、"经营风险"、"开庭公告"、"裁判文书"、"被执行人"、"天眼查"。
version: 1.0.0
type: procedural
risk_level: low
status: enabled
tags:
  - due-diligence
  - risk
  - tianyancha
  - corporate
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
      name: 天眼查企业风险查询
      short_desc: 输入企业名称，返回自身/周边/历史/预警四类风险画像
      description: >-
        天眼查企业风险查询——输入企业名称，返回风险画像（自身风险/周边风险/历史风险/预警提醒，含分类统计与明细）。Use when 用户提到"查风险"、"企业风险"、"风险画像"、"司法风险"、"经营风险"、"开庭公告"、"裁判文书"、"被执行人"、"天眼查"。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:b58091c7ef9e968e
      translated_by: human
    en-US:
      name: Tianyancha Risk Query
      short_desc: Enterprise risk profile by company name — self/related/historical/warning risk
      description: >-
        Tianyancha enterprise risk query — input a company name and return a structured risk profile (self risk / related-party risk / historical risk / early warnings, with category counts and details). Use when the user asks about enterprise risk, judicial risk, litigation announcements, court rulings, dishonest debtors, or Tianyancha.
      body: ./SKILL.md
      source_hash: sha256:b58091c7ef9e968e
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 3l7 2.8v5.4c0 4.5-3 8-7 9.8-4-1.8-7-5.3-7-9.8V5.8L12 3Z" stroke="#FF9500" stroke-width="1.6" stroke-linejoin="round"/><path d="M12 8.5v4" stroke="#FF3B30" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="15.5" r="1" fill="#FF3B30"/></svg>
  category: business
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.115
---

# Tianyancha Risk Query

## L0: One-Sentence Summary

Input a company name, call the Tianyancha risk-info API, and return a structured risk profile (self / related-party / historical / warning, four categories).

## L1: Overview

- **Data source**: Tianyancha Open Platform `risk/riskInfo/2.0`
- **Auth**: Token (`Authorization` header, **without** the `Bearer` prefix)
- **Invocation**: HTTP GET (curl / HttpRequest tool)
- **Prerequisites**: a valid Token with the risk API enabled

## Credential Setup

This skill requires a Tianyancha Open Platform Token:

1. Register an enterprise account at the [Tianyancha Open Platform](https://open.tianyancha.com/)
2. Purchase/enable an API package (`risk/riskInfo/2.0` is authorized per package tier)
3. Export the token as the environment variable `TIANYANCHA_TOKEN`, or replace the `{TIANYANCHA_TOKEN}` placeholder below

## L2: Procedure

### 1. Build the request

```bash
curl -s --max-time 30 --ssl-no-revoke \
  "https://open.api.tianyancha.com/services/open/risk/riskInfo/2.0?keyword={company-name-URL-encoded}" \
  -H "Authorization: ${TIANYANCHA_TOKEN}"
```

**Parameters**:

| Param | Value | Notes |
|---|---|---|
| keyword | Company name (URL-encoded) | e.g. `华为技术有限公司` |
| Authorization | `{TIANYANCHA_TOKEN}` | **Token in header, no `Bearer` prefix** (adding one returns 300009) |

### 2. Interpret the response

- `error_code == 0` and `reason == "ok"`: success, extract `result.riskList[]`
- `error_code == 300009`: account error — wrong token or a `Bearer` prefix was added
- `error_code == 300005`: no permission for this API — the token does not cover it
- `error_code == 300008`: missing parameter — check keyword

### 3. Response structure

`result` contains:

- `riskLevel`: overall risk level
- `riskList[]`: four risk categories (each with name / count / type / list[])

| Category | type | Meaning |
|---|---|---|
| Self risk | 1 | The company's own judicial/business risks (court hearings / rulings / case filings / court announcements / judicial auctions) |
| Related-party risk | 2 | Risks of shareholders, executives, invested companies |
| Historical risk | 3 | Closed historical risks (historical filings / hearings / dishonest-debtor history) |
| Early warnings | 0 | Business-registration changes (investor / key-personnel / registered-capital / legal-representative changes, bankruptcy cases) |

Each category's `list[]` holds sub-items with `title` (e.g. "开庭公告") / `total` / `tag` (warning / high-risk / info) / `list[]` (top details with id / title / desc / riskCount).

### 4. Normalized mapping

```json
{
  "query_status": "success",
  "source": "tianyancha",
  "company_name": "{company name}",
  "risk_level": "{result.riskLevel}",
  "summary": {
    "self_risk_count": 3127,
    "related_risk_count": 1505,
    "history_risk_count": 9113,
    "warning_count": 815
  },
  "self_risks": [
    { "risk_type": "开庭公告", "count": 1501, "level": "警示", "title": "该公司起诉他人或公司的开庭公告", "detail_count": 1096 }
  ],
  "timestamp": "2026-08-31T21:00:00+08:00"
}
```

### 5. Due-diligence highlights

Prioritize as follows when composing the report:

1. **High-risk entries** (tag=高风险): e.g. "被执行人", "清算信息", "失信被执行人" — list as major risk items
2. **Large warning counts** (total > 100): e.g. 1,501 hearing announcements — list as judicial-activity indicators
3. **Change warnings**: recent investor / legal-representative / capital changes — list as business dynamics

## Known Limitations

- **Tiered token authorization**: APIs are authorized per package; unauthorized APIs return 300005 — full-dimension packages unlock business/shareholder/IP endpoints
- **QPS throttling**: rate limits depend on the package; keep ≥1 s between calls
- **Large responses**: big companies can return 98KB+ — extract summaries plus top-N details to keep context small

## Troubleshooting

| Code | Meaning | Fix |
|---|---|---|
| 0 | Success | — |
| 300005 | No permission for this API | Confirm the endpoint is covered by your package |
| 300008 | Missing parameter | Check the keyword parameter |
| 300009 | Account error | Wrong token / Bearer prefix / expired token — remove the prefix and retry; if still failing, update the token |
