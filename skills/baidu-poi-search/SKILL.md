---
name: baidu-poi-search
description: >-
  百度地图企业 POI 搜索——输入企业名称，返回 POI 名称/地址/经纬度/分支机构。Use when 用户提到"查企业地址"、"查公司位置"、"POI搜索"、"企业地图"、"经纬度"、"查分支机构"、"百度地图"、"企业网点"、"周边企业"。
version: 1.0.0
type: procedural
risk_level: low
status: enabled
tags:
  - due-diligence
  - baidu-map
  - poi
  - geolocation
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
      name: 百度地图POI搜索
      short_desc: 输入企业名称，返回 POI 名称/地址/经纬度/分支机构
      description: >-
        百度地图企业 POI 搜索——输入企业名称，返回 POI 名称/地址/经纬度/分支机构。Use when 用户提到"查企业地址"、"查公司位置"、"POI搜索"、"企业地图"、"经纬度"、"查分支机构"、"百度地图"、"企业网点"、"周边企业"。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:24e98eab4d4e0f04
      translated_by: human
    en-US:
      name: Baidu Map POI Search
      short_desc: Enterprise POI lookup by company name — name, address, coordinates, branches
      description: >-
        Baidu Map enterprise POI search — input a company name and return POI name, address, latitude/longitude, and branch listings. Use when the user asks to look up a company address, location, POI, enterprise map, coordinates, branches, or nearby companies.
      body: ./SKILL.md
      source_hash: sha256:24e98eab4d4e0f04
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 21c4.97-4.36 7.5-8.1 7.5-11.5a7.5 7.5 0 1 0-15 0C4.5 12.9 7.03 16.64 12 21Z" stroke="#007AFF" stroke-width="1.6" stroke-linejoin="round"/><circle cx="12" cy="9.5" r="2.6" stroke="#34C759" stroke-width="1.6"/></svg>
  category: data
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.115
---

# Baidu Map POI Search

## L0: One-Sentence Summary

Input a company name, call the Baidu Map Place Search API, and return normalized POI data (name / address / coordinates / province & city).

## L1: Overview

- **Data source**: Baidu Map Open Platform Place Search API v2
- **Auth**: AK (free quota for individual developers)
- **Invocation**: HTTP GET (curl / HttpRequest tool)
- **Prerequisites**: no browser, no extra dependencies — pure REST API

## Credential Setup

This skill requires a Baidu Map AK (access key):

1. Register a developer account at the [Baidu Map Open Platform](https://lbsyun.baidu.com/)
2. Console → App Management → Create an app (enable the "Place Search" service; choose the empty-whitelist `0.0.0.0/0` AK type)
3. Export the AK as the environment variable `BAIDU_MAP_AK`, or replace the `{BAIDU_MAP_AK}` placeholder in the commands below

> If the local DesireCore service catalog already registers the Baidu Map service (endpoint `https://api.map.baidu.com`), prefer calling it through the catalog so credentials are managed centrally.

## L2: Procedure

### 1. Build the request

```bash
curl -s --max-time 15 --ssl-no-revoke \
  "https://api.map.baidu.com/place/v2/search?query={company-name-URL-encoded}&region={city-or-nationwide}&output=json&page_size=20&ak=${BAIDU_MAP_AK}"
```

**Parameters**:

| Param | Value | Notes |
|---|---|---|
| query | Company name (URL-encoded) | e.g. `华为技术有限公司` → `%E5%8D%8E%E4%B8%BA%E6%8A%80%E6%9C%AF%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8` |
| region | City name or `全国` (nationwide) | Scope; use nationwide when unsure |
| output | json | Fixed |
| page_size | 20 | Max 20 per page |
| ak | `{BAIDU_MAP_AK}` | Baidu Map AK (free for individual developers) |

### 2. Interpret the response

- `status == 0`: success, extract `results[]`
- `status != 0`: failure, check `message` (101 = AK missing, 200 = AK disabled, 302 = quota exceeded)

### 3. Normalized mapping

Map each entry in `results[]` to:

```json
{
  "source": "baidu-poi",
  "company_name": "{user input}",
  "poi_name": "{result.name}",
  "address": "{result.address}",
  "latitude": "{result.location.lat}",
  "longitude": "{result.location.lng}",
  "province": "{result.province}",
  "city": "{result.city}"
}
```

### 4. Homonym filtering (due-diligence scenario)

POI results may contain same-name noise (e.g. "南岗华为公司" is not "华为技术有限公司"). Filtering suggestion:

- Exact match: `result.name` equals the full company name → `match=exact`
- Partial match: `result.name` contains the full name or its short name → `match=partial`
- Otherwise → `match=related`, listed separately in due-diligence reports

### 5. Output format

```json
{
  "query_status": "success",
  "source": "baidu-poi",
  "total": 5,
  "results": [
    { "poi_name": "华为技术有限公司", "address": "广东省深圳市龙岗区...", "latitude": "22.656137", "longitude": "114.066131", "match": "exact" }
  ],
  "timestamp": "2026-08-31T21:00:00+08:00"
}
```

## Known Limitations

- Free quota: QPS (~3/s) and daily caps (~100 place-search calls/day) for individual developers, per console quota management
- POI ≠ registered business address: results are map annotations and may differ from the registered address (note the distinction in due diligence)
- Homonyms: short names of famous companies hit many non-target POIs — prefer the full company name

## Troubleshooting

| Code | Meaning | Fix |
|---|---|---|
| 0 | Success | — |
| 101 | AK param missing | Check the ak parameter |
| 200 | AK disabled | Check app status in the Baidu console |
| 201 | AK/SN check failed | This recipe uses an empty-whitelist `0.0.0.0/0` AK; no SN needed |
| 302 | Quota exceeded | Wait for the daily reset or upgrade the quota |
| 240 | API service invalid | The AK has not enabled "Place Search" — fix the app in the console |
