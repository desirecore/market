---
name: multi-source-sentiment
description: >-
  企业尽调舆情采集——通过抖音指数、抖音精选、WebSearch 三大数据源采集企业舆情，分析负面风险（诉讼/处罚/质量/高管/劳资），输出尽调舆情报告。Use when 用户提到"查舆情"、"企业舆情"、"负面新闻"、"舆论风险"、"尽调舆情"、"企业口碑"、"舆情分析"、"网络口碑"。
version: 1.0.0
type: procedural
risk_level: medium
status: enabled
tags:
  - due-diligence
  - sentiment
  - public-opinion
  - douyin
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
      name: 企业尽调舆情采集
      short_desc: 抖音指数+抖音精选+WebSearch 三渠道采集，输出尽调舆情报告
      description: >-
        企业尽调舆情采集——通过抖音指数、抖音精选、WebSearch 三大数据源采集企业舆情，分析负面风险（诉讼/处罚/质量/高管/劳资），输出尽调舆情报告。Use when 用户提到"查舆情"、"企业舆情"、"负面新闻"、"舆论风险"、"尽调舆情"、"企业口碑"、"舆情分析"、"网络口碑"。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:e102f3139e03fcd5
      translated_by: human
    en-US:
      name: Multi-Source Sentiment
      short_desc: Due-diligence sentiment via Douyin Index, Douyin Featured, and WebSearch
      description: >-
        Due-diligence sentiment collection — gather enterprise public opinion via three channels (Douyin Index, Douyin Featured, WebSearch), analyze negative risks (litigation / penalties / quality / executives / labor), and output a due-diligence sentiment report. Use when the user asks about enterprise sentiment, negative news, reputation risk, or public opinion.
      body: ./SKILL.md
      source_hash: sha256:e102f3139e03fcd5
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="2" fill="#FF2D55"/><path d="M12 7a5 5 0 0 1 5 5M12 3a9 9 0 0 1 9 9" stroke="#FF2D55" stroke-width="1.6" stroke-linecap="round"/><path d="M7 12a5 5 0 0 1 5-5M3 12a9 9 0 0 1 9-9" stroke="#FF9500" stroke-width="1.6" stroke-linecap="round"/></svg>
  category: research
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.115
---

# Multi-Source Sentiment (Due Diligence)

## L0: One-Sentence Summary

Input a company name, collect public opinion via Douyin Index (trend) + Douyin Featured (negative material) + WebSearch (web-wide news), and output a due-diligence sentiment report (negative-risk list / positive highlights / sentiment overview / overall judgment).

## L1: Overview

- **Purpose**: answer the core due-diligence questions — any negative publicity? litigation/penalty coverage? product-quality issues? executive misconduct? overall reputation?
- **Channel split**:

| Channel | Due-diligence use | Collection |
|---|---|---|
| **Douyin Index** | Quantified heat trend (is something fermenting recently?) | Kimi WebBridge visiting Oceanengine Trends |
| **Douyin Featured** | Concrete negative material (complaint/expose videos) | Kimi WebBridge searching Douyin |
| **WebSearch** | Web-wide negative news / court notices / penalties / complaints | DesireCore built-in WebSearch |

- **Prerequisites**: Kimi WebBridge daemon running (`127.0.0.1:10086`) + browser extension connected

## L2: Procedure

### Source 1: Douyin Index (heat trend)

#### Access Method

```
URL: https://trendinsight.oceanengine.com/arithmetic-index/analysis/keyword?keyword={company-short-name}&appName=aweme
Method: Kimi WebBridge opens the URL and extracts page content
Note: URL-parameterized access avoids captchas. Do not type into the search box.
```

#### Keyword Strategy

| Dimension | Keyword |
|---|---|
| Overall heat | `{short name}` |
| Negative heat | `{short name} 负面` |
| Complaint heat | `{short name} 投诉` |

#### Interpretation

- **Sudden spike** (MoM > 200%) → a negative event may be fermenting; investigate
- **Flat trend** → low reputation risk
- **Persistently high** → normal for famous companies; judge by content

### Source 2: Douyin Featured (negative material)

#### Access Method

```
URL: https://www.douyin.com/search/{company-short-name}?type=video
Method: Kimi WebBridge searches Douyin, extracts title / author / likes / comments
Note: search by short name (full names rarely hit); prioritize high-engagement videos.
```

#### Collected Fields

Collected fields: video title (negative signals: complaint / rights-protection / exposure / quality / scam / runaway), likes & comments (reach = impact), author (personal vent vs media report vs competitor smear), publish date (recent vs historical).

#### Signal Grading

| Signals | Risk |
|---|---|
| 投诉 / 维权 / 欺骗 / 诈骗 / 跑路 | 🔴 high |
| 质量 / 召回 / 不合格 / 假货 | 🔴 high |
| 欠薪 / 辞退 / 仲裁 | 🟡 medium |
| 吐槽 / 差评 / 不满 | 🟡 medium |
| positive / awards / innovation | 🟢 positive |

### Source 3: WebSearch (web-wide)

#### Search Keyword Groups

```python
# High priority (always)
search_queries_high = [
    "{company} 负面 OR 投诉 OR 维权 OR 欺骗 OR 跑路",
    "{company} 起诉 OR 法院 OR 被告 OR 被执行 OR 失信",
    "{company} 处罚 OR 违规 OR 罚款 OR 整改 OR 通报批评",
]

# Medium priority (recommended)
search_queries_mid = [
    "{company} 质量 OR 召回 OR 不合格 OR 安全事故",
    "{company} 老板 OR 法人 OR 总经理 丑闻 OR 被查 OR 被抓",
    "{company} 欠薪 OR 辞退 OR 劳动仲裁 OR 工伤",
]

# Low priority (positive control)
search_queries_low = [
    "{company} 获奖 OR 创新 OR 认定 OR 排名",
]
```

#### Collected Fields

Collected fields: title / source site / date / summary / URL. **Note**: distinguish the company as **plaintiff** (enforcement, not a negative signal) vs **defendant** (negative signal).

### Step 1: Run the three channels

1. **WebSearch** first (highest information density): run high/medium/low query groups and collect results
2. **Douyin Index**: check the heat trend for signs of recent fermentation
3. **Douyin Featured**: search videos and filter by negative signal words

### Step 2: LLM post-processing

| Step | Description |
|---|---|
| Sentiment classification | tag each item positive / neutral / negative |
| Risk grading | negative → high (defendant / penalty / runaway / safety accident) / medium (complaints / quality gripes / labor) / low (generic bad reviews) |
| Event merging | merge duplicate coverage of one event (keep the earliest) |
| Plaintiff/defendant split | litigation where the company is plaintiff is **not** a negative risk |
| Recency | mark "recent" (≤3 months) vs "historical" |

### Step 3: Output the report

```json
{
  "query_status": "success",
  "source": "multi-source-sentiment",
  "company_name": "{company}",
  "sentiment_overview": {
    "overall_assessment": "正面 | 中性偏正 | 中性 | 中性偏负 | 负面 | 高风险",
    "negative_ratio": "15%",
    "neutral_ratio": "60%",
    "positive_ratio": "25%",
    "trend": "稳定 | 近期发酵 | 持续负面"
  },
  "negative_risks": [
    {
      "risk_type": "诉讼报道(被告) | 行政处罚 | 产品质量 | 高管负面 | 劳资纠纷 | 消费者投诉 | 经营异常",
      "event_title": "……",
      "event_date": "YYYY-MM-DD",
      "recency": "近期 | 历史",
      "source_url": "https://……",
      "severity": "高 | 中 | 低",
      "summary": "1-2 sentence summary"
    }
  ],
  "controversies": [],
  "positive_highlights": [],
  "sentiment_summary": "3-5 sentence judgment: overall reputation, main negatives and severity, fermentation status, due-diligence advice",
  "data_sources_used": ["websearch", "douyin-index", "douyin-featured"],
  "collection_time": "ISO8601"
}
```

## Quality Standards

- **Authenticity**: all content must come from actual collection (WebSearch results / Douyin pages); never fabricate
- **Traceability**: every negative risk carries a source_url
- **Plaintiff/defendant**: litigation where the company is plaintiff goes to "litigation updates", not negative risks
- **Recency**: every negative item is marked recent (≤3 months) or historical
- **No absolute conclusions**: sentiment is one auxiliary signal; the report must note it should be combined with business-registration, judicial, and financial data

## Error Handling

| Scenario | Handling |
|---|---|
| Douyin Index unreachable | skip; supplement with WebSearch + Featured; note "heat data missing" in the report |
| Douyin search requires login | skip; WebSearch `{company} 抖音 负面` instead |
| WebSearch returns nothing | mark "no negative found" — a positive signal |
| Too many negatives | keep the top 10 by severity; count the rest |

## Known Limitations

- **Not real-time**: depends on search-engine indexing and Douyin pages; hour-to-day latency (7×24 monitoring requires commercial sentiment APIs)
- **LLM-based sentiment**: no dedicated sentiment model; ~85-90% accuracy, edge cases may misjudge
- **Douyin coverage**: WeChat/Weibo/Xiaohongshu content is only covered indirectly via WebSearch
- **Full vs short name**: WebSearch uses the full name (precision), Douyin the short name (recall); results may differ

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| WebBridge daemon unreachable | daemon down | `~/.kimi-webbridge/bin/kimi-webbridge.exe start` |
| Trends page blank | JS not rendered | wait 5 s, then evaluate innerText |
| Douyin search empty | login required / name mismatch | skip; supplement via WebSearch |
| WebSearch results all positive | weak negative keywords | use concrete terms (e.g. "被处罚" instead of "处罚") |
