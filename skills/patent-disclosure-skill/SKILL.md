---
name: patent-disclosure-skill
description: 中文专利技能的可选 MIT 本地包，用于交底、检索、阅读、专利地图和审查意见辅助。不是法律意见；申请事务仍需具备资质的专业人员。安装树和每个子技能都含上游
  LICENSE。包含可选 Python 工具，以及一个超过 1 MiB 的 vendored mermaid.min.js。
version: 2026.11.24
license: MIT
type: hybrid
risk_level: medium
tags:
- patent
- disclosure
- chinese
- skill-collection
compatibility: Not legal advice. Optional Python tools may require a private environment
  and declared packages.
metadata:
  author: handsomestWei; DesireCore local packaging
  updated_at: '2026-11-24'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
    - en-US
    - zh-CN
    en-US:
      name: Patent Disclosure Skills
      short_desc: Optional local MIT package of Chinese patent skills for disclosure,
        search, reading, mapping and office-action assistance. Not legal advice; filing
        still needs a qualified professional. Includes upstream LICENSE in the installed
        tree and in each child. Optional Python tools and a vendored mermaid.min.js
        over 1 MiB are included.
      description: Market-local packaging of handsomestWei/patent-disclosure-skill@491524bd36a3f9f8d2e35caa5b56368b67d88ced.
        The installer copies only the skill content directory, so LICENSE is placed
        here. Example renderings under docs/ are excluded. This is not legal advice.
        Package version 2026.11.24.
      body: ./SKILL.md
      translated_by: human
      translated_at: '2026-11-24'
      source_hash: sha256:fa2460a7f6df1bdc
    zh-CN:
      name: 专利交底技能合集
      short_desc: 中文专利技能的可选 MIT 本地包，用于交底、检索、阅读、专利地图和审查意见辅助。不是法律意见；申请事务仍需具备资质的专业人员。安装树和每个子技能都含上游
        LICENSE。包含可选 Python 工具，以及一个超过 1 MiB 的 vendored mermaid.min.js。
      description: 基于 handsomestWei/patent-disclosure-skill@491524bd36a3f9f8d2e35caa5b56368b67d88ced
        的市场本地包装。安装器只复制技能内容目录，因此把 LICENSE 放进本包。docs/ 下的效果例图已排除。本包不是法律意见。包版本 2026.11.24。
      body: ./SKILL.zh-CN.md
      translated_by: human
      translated_at: '2026-11-24'
      source_hash: sha256:fa2460a7f6df1bdc
market:
  icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0
    0 24 24" fill="none"><path d="M6 3.5h9l5 5V21H6z" stroke="#2563EB" stroke-width="1.7"
    stroke-linejoin="round"/><path d="M15 3.5V8h5M9 12h8M9 15h6M9 18h4" stroke="#2563EB"
    stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
  category: business
  maintainer:
    name: mashagua
    url: https://github.com/mashagua
    verified: true
  channel: latest
---

# Patent Disclosure Skills

## Scope and provenance

This optional local MIT package contains the collection's `skills/` tree, root helper scripts where present, and the upstream [LICENSE](LICENSE) at the package root and in each child. See [UPSTREAM.md](UPSTREAM.md).

This is not legal advice and does not replace a qualified patent professional. Optional Python tools and a vendored `mermaid.min.js` larger than 1 MiB are included because the skills use them.

Reviewed bilingual child summaries: [references/child-summaries.json](references/child-summaries.json).

| ID | Summary |
|---|---|
| `patent-application` | Filing documents: turn an existing disclosure into claims, specification, abstract and drawings; plan a parent case and divisionals and check them against the original disclosure. The four-document set needs a specified disclosure directory. Content disputes go to a question list; a confirmation-needed summary is required after delivery. Revisions to existing output are saved in a new timestamped directory. Must be explicitly triggered. |
| `patent-chart` | Claim chart: split independent claims into technical features, compare them cell by cell with prior art, products or standards, and attach evidence and strength notes. Used for invalidity comparison, preliminary FTO screening, infringement/EoU, SEP and patentability drafts. Must be invoked by name. Does not give legal opinions. |
| `patent-disclosure` | Chinese patent disclosure: mine patent points for inventions, utility models and designs, do lightweight novelty checks and drafting, and plan a protective 1+N portfolio. |
| `patent-docket` | From inventor or engineer materials, draft the disclosure and filing documents in one pass; gaps on the filing question list are revised at most three rounds. Ask for missing technical facts; do not invent them. Triggers include doing disclosure and filing together, drafting both from scratch, end-to-end work, writing the disclosure then the filing, revising from a list, joint review, docket, and /patent-docket. |
| `patent-exam-policy` | A policy brief for disclosures: compare recent CNIPA positions, explain the impact on disclosure drafting or the current draft, and note formal filing requirements. Skill evolution is a side path only; by default only the disclosure package is edited, and files are changed only when separately named. |
| `patent-map` | Patent map: from popularized interpretations already stored as Obsidian cases, open five map types when named. The terrain is laid out with bge-small-zh vectors. |
| `patent-oa` | Office-action assistance: Q&A and drafts for examination opinions; when the library is thin, guide case intake. Must be explicitly triggered. |
| `patent-reader` | Plain-language patent reading: turn a Chinese or overseas (US, EP, JP, KR, etc.) publication number or PDF into notes, graphs and an Obsidian intake. |
| `patent-search` | Bibliographic patent search: query China’s official publication notices by inventor, applicant, classification, title or abstract (keywords may also be generated from a single figure or claims); when the user names overseas search, use Google Patents for US, EP, JP, KR and similar patents. |

## Prerequisites

- Where a skill uses Python tools, install the declared packages in a private environment
- Human professional review for any filing or legal conclusion
