# DesireCore Market

DesireCore 官方市场仓库，存放官方维护的 Agent/Team/Skill 定义，以及经过整理的第三方 Skill 入口。

## Repository Shape

```
.
├── manifest.json          # Market metadata, supported locales, aggregate stats
├── categories.json        # Category registry and localized labels
├── builtin-skills.json    # Built-in local SKILL.md skills
├── agents/
│   ├── desirecore/
│   │   └── agent.json
│   └── <agent-listing>/
│       ├── agent.json
│       ├── catalog-metadata.v1.json
│       └── USAGE.md            # Optional usage notes (USAGE.<locale>.md for variants)
├── teams/
│   └── <team>/
│       └── entry.json
└── skills/
    ├── <local-skill>/
    │   ├── SKILL.md
    │   └── SKILL.<locale>.md
    └── <external-entry>/
        └── entry.json
```

The market currently contains:

- `2` Agents: `desirecore`, `dingtalk-workspace`
- `1` Team: `contract-review-team`
- `40` local built-in skills with `SKILL.md`
- `29` external skill entries with `entry.json`
- `69` publishable skills in total (`SKILL.md` + `entry.json`)

## Skill Sources

Local built-in skills are installable from this repository and must be listed in `builtin-skills.json`:

```text
baidu-poi-search, ccgp-gov-procurement, clone-agent, cnipa-patent-search, code-intelligence,
configuring-compute, create-agent, creditchina-query, dashscope-image-gen, delete-agent,
dev-environment-setup, discover-agent, docx, frontend-design, guizang-ppt,
image-to-image, mail-operations, manage-skills, manage-teams, markdown,
minimax-music-gen, minimax-video-gen, multi-source-sentiment, nodejs-runtime, pdf, pptx,
presentation-forge, python-runtime, registering-services, s3-storage-operations, skill-creator,
tech-diagram, tianyancha-risk, update-agent, using-services, web-access, workflow, workforce-optimization,
xiaomi-tts, xlsx
```

`builtin-skills.json#retired` lists old built-in Skill IDs that clients may safely retire during
startup. Clients only remove copies tracked in `skills.lock` as market/bundled content whose
`SKILL.md` hash still matches the installed record; manually installed or locally modified copies
are preserved. An ID must not appear in both `skills` and `retired`.

External entries are marketplace pointers to Git/Web/ZIP sources:

```text
agent-reach, ai-news-radar, amap-jsapi-skill, baoyu-skills, dingtalk-api,
dingtalk-cli, flyai-skill, follow-builders, humanizer, humanizer-zh,
ian-xiaohei-illustrations, impeccable, karpathy-guidelines, khazix-skills,
larksuite-cli, last30days, luckin-my-coffee, marketingskills,
mattpocock-skills, minimax-image-gen, minimax-tts, mt-paotui-for-client,
netease-skills, nuwa-skill, taste-skill, watch, watchless,
wechatpay-skills, wecom-cli
```

## Data Formats

### Local Skill (`skills/<id>/SKILL.md`)

Local skills use YAML frontmatter plus Markdown body. The top-level `name` must equal the directory slug. Display strings live in `metadata.i18n`.

```yaml
---
name: web-access
description: >-
  Use this skill when ...
version: 2.0.1
type: procedural
risk_level: low
status: enabled
metadata:
  author: desirecore
  updated_at: '2026-05-05'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales: [zh-CN, en-US]
    zh-CN:
      name: 联网访问
      short_desc: 联网搜索、网页抓取、登录态浏览器访问
      body: ./SKILL.zh-CN.md
      translated_by: human
    en-US:
      name: Web Access
      short_desc: Web search, page fetching, logged-in browser access
      body: ./SKILL.md
      source_hash: sha256:...
      translated_by: human
market:
  category: research
  channel: latest
  maintainer:
    name: DesireCore Official
    verified: true
---
```

### External Entry (`skills/<id>/entry.json`)

External entries point to upstream packages or repositories. They are counted in `manifest.stats.totalSkills` but are not included in `builtin-skills.json`.

```json
{
  "id": "example-skill",
  "name": "Example Skill",
  "category": "development",
  "icon": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\">...</svg>",
  "tags": ["example"],
  "maintainer": {
    "name": "Example",
    "verified": false,
    "account": "example",
    "url": "https://github.com/example/example-skill"
  },
  "stewardship": "community",
  "license": "MIT",
  "redistribution": "allowed",
  "source": {
    "kind": "git",
    "repoUrl": "https://github.com/example/example-skill.git",
    "repoBranch": "main"
  }
}
```

### Team Listing (`teams/<id>/entry.json`)

A Team is a group of Agents with a supervisor. It is published as a **fork pointer
only**: the team body (`team.json`, `members.json`, `shared/`) always stays in the
upstream team repository, and the catalog registers just "what it is and where to
fork it from". Installation forks that repository and installs the declared members;
updates are a `git pull` on the fork. Because both actions are Git actions,
`source.kind` must be `git` and `source.repoUrl` is required — `zip` and `web` cannot
express either one — and a Team deliberately has **no** `installPolicy` /
`updatePolicy` pair: it is always market-initiated fork plus repository-driven update.

`teams/<id>/` therefore holds exactly `entry.json` plus the sidecar. There is no
inline form; a `team.json` in the catalog is rejected.

```json
{
  "id": "example-team",
  "name": "Example Team",
  "category": "development",
  "tags": ["example"],
  "latestVersion": "0.1.0",
  "maintainer": {
    "name": "Example",
    "verified": false,
    "account": "example",
    "url": "https://github.com/example"
  },
  "stewardship": "community",
  "license": "MIT",
  "redistribution": "source-pointer-only",
  "source": {
    "kind": "git",
    "repoUrl": "https://github.com/example/example-team.git",
    "repoBranch": "main",
    "ref": "0123456789abcdef0123456789abcdef01234567"
  },
  "requiredClientVersion": "10.0.0",
  "avatar": { "t": "示", "bg": "linear-gradient(135deg, #5856D6, #3634A3)" },
  "supervisorName": "Example Supervisor",
  "supervisorAgentId": "example-lead",
  "memberCount": 3,
  "memberNames": ["Example Member One", "Example Member Two"]
}
```

A Team card is rendered from `avatar`, not from `icon`. The client's runtime
projection `marketTeamSchema` requires `avatar` and has no `icon` property at all —
the same is true of `marketAgentSchema`, while only `marketSkillSchema` exposes
`icon`. The entry contract inherits `icon` from the shared common properties, so it
is *accepted*, but it can never reach a card. The validator therefore requires `icon`
on Skill listings only, and warns when an Agent or Team listing declares one.

`redistribution` stays `source-pointer-only` for a Team even under a permissive
license: the market never ships the team body, it only points at the repository the
client forks. The license governs what a fork may do; `redistribution` describes how
the content is delivered, and for teams that is always "fetch from upstream".

`supervisorName`, `supervisorAgentId`, `memberCount`, `memberNames` and
`requiredSkills` are display metadata declared by the publisher. They may drift from
the upstream repository, so installation, permissions and member resolution must read
the forked `team.json` / `members.json` instead. Teams are counted in
`manifest.stats.totalTeams`, which the client keeps optional: a catalog with no teams
may omit it, and once the key is present it must be exact.

### Catalog metadata sidecar (`catalog-metadata.v1.json`)

The versioned catalog metadata contract is stored at one fixed path next to each
legacy item:

```text
agents/<id>/catalog-metadata.v1.json
teams/<id>/catalog-metadata.v1.json
skills/<id>/catalog-metadata.v1.json
```

Legacy `agent.json`, `SKILL.md`, and `entry.json` files remain the compatibility
surface for older clients. New clients merge the sidecar through a deterministic
adapter. Any field repeated in both files must have the same value; the validator
rejects drift rather than choosing one copy silently.

Agent listings support exactly one of `agents/<slug>/agent.json` (inline metadata)
or `agents/<slug>/entry.json` (an external pointer), alongside the sidecar. Missing
or simultaneous primary files are rejected. For a pointer, `entry.id` and sidecar
`identity.id` use the catalog directory slug and `identity.kind` is `agent`; the
upstream AgentFS `agent.json.id` remains its own UUID and must not be rewritten.

An agent listing may also carry an optional `USAGE.md` next to `agent.json`. The
client renders it as a separate "Usage" section on the agent detail page, kept
apart from `fullDesc` (which is persona text and also enters the agent's runtime
context). Localized variants use `USAGE.<locale>.md`, resolved through the same
fallback chain as the `i18n` block: requested locale, then `i18n.source_locale`,
then `i18n.default_locale`, then the unsuffixed file. Its scope is what a reader
needs *before* installing — prerequisites, authorization steps, capability and
safety boundaries — not full documentation; clients truncate overlong content.
Longer material belongs in a skill's `references/` directory, which the agent
loads on demand. Listings without the file are unaffected and render no section.
Relative image references do not render on the detail page, so keep `USAGE.md`
text-only. See ADR-143 in the DesireCore repository.

Agent pointers first pass the complete raw client contract in
[`schemas/market-agent-entry.client.schema.json`](schemas/market-agent-entry.client.schema.json),
exported from `marketAgentEntrySchema` in the DesireCore repository at commit
`18bbb86f62e1288b1f945209bed74ec72620a9d4`. The schema's `$comment` records the
source blob as well. Refresh this generated snapshot from the TypeScript export
when changing client compatibility; do not replace it with permissive sidecar
validation. Version fields keep their original types and the client's supported
format. Installation/update policies must either both be absent (effective
`market/market`) or form a complete supported pair; the sidecar must preserve
that effective pair.

Agent pointer `latestVersion` maps to sidecar `release.version`; optional
`requiredClientVersion`, `installPolicy`, and `updatePolicy` must agree with the
sidecar compatibility/spec fields. Pointer source fields must describe the same
artifact as `provenance.content`, and `maintainer` maps to `upstreamMaintainer`.
An installable Agent pointer must itself pin `source.ref` (Git) or `source.sha256`
(Web/ZIP); an immutable ref supplied only by the sidecar cannot pin a mutable
entry. Existing immutable-source, license, governance-review and complete-coverage
checks still apply. Agent pointers do not receive the built-in Skill exceptions.

Agent 目录必须在 `agent.json` 内联元数据和 `entry.json` 外部指针中二选一，并提供 sidecar。
Pointer 原始 JSON 先通过固定客户端提交导出的完整 Schema；版本类型与格式、来源路径和策略组合不能由 sidecar 掩盖。
Pointer 的目录 slug、`entry.id`、sidecar `identity.id` 必须一致；上游 AgentFS 的 UUID 不改写。
安装/更新策略双缺省时有效值仍是 `market/market`，sidecar 不得将其改成系统条目。
`latestVersion`、最低客户端版本和安装/更新策略须与 sidecar 对齐；来源必须是同一个制品。
可安装指针自身必须固定 Git ref 或 Web/ZIP 摘要，不能只在 sidecar 宣称不可变版本。
现有许可、治理审查、不可变来源和完整覆盖门禁继续有效，不适用内置 Skill 的宽松例外。

Team listings are pointer-only, so `teams/<slug>/` carries exactly `entry.json` plus
the sidecar; an inline `team.json` is rejected. Team pointers first pass the complete
raw client contract in
[`schemas/market-team-entry.client.schema.json`](schemas/market-team-entry.client.schema.json),
exported from `marketTeamEntrySchema` the same way as the Agent snapshot; its
`$comment` records the source commit and blob. `entry.id`, the directory slug and
sidecar `identity.id` must agree, `identity.kind` is `team`, and `latestVersion` maps
to `release.version`. `supervisorName`, `supervisorAgentId`, `memberCount`,
`memberNames`, `requiredSkills` and `requiredClientVersion` are compared symmetrically:
the sidecar may neither drop a fact the pointer declares nor invent one it omits,
because the client reads the pointer and a version gate that exists only in the
sidecar would not gate anything. Pointer source fields must describe the same
artifact as `provenance.content`, and an installable Team pointer must itself pin a
full-SHA `source.ref` — a tag is not a reproducible pin, because a tag can be moved
to a different commit after the listing is reviewed.

团队条目只有指针形态：`teams/<slug>/` 仅放 `entry.json` 与 sidecar，目录内出现 `team.json` 直接判非法。
Pointer 原始 JSON 先通过由 `marketTeamEntrySchema` 导出的完整客户端 Schema；
`source.kind` 恒为 `git` 且必须有 `repoUrl`，团队没有 `installPolicy` / `updatePolicy` 组合。
目录 slug、`entry.id`、sidecar `identity.id` 必须一致，`identity.kind` 为 `team`。
展示字段与最低客户端版本双向比对：sidecar 既不得丢弃指针声明的事实，也不得凭空补上指针没有的事实。
可安装团队指针自身必须固定完整 SHA 的 `source.ref`，tag 或分支不算可复现锁定。

The sidecar records source-owned presentation, release, timestamp, content
provenance, governance, compatibility, and type-specific facts. It deliberately
cannot declare `catalogSourceId`, catalog commit/path/trust, effective official
status, installation state, device state, health, URLs discovered at runtime, or
`syncedAt`. DesireCore injects trusted catalog provenance and runtime facts.

`license.evidencePath`, `compliance.licenseEvidencePath` and `compliance.noticePath`
resolve differently by item shape, because the schema constrains only the string
form. Vendored content (built-in Skills, inline Agents) ships inside this repository,
so the path is relative to the catalog item directory and the file must actually be
there — a missing file is an error. A pointer distributes nothing, so its evidence
can only be inside the upstream snapshot at the pinned revision; the validator cannot
read that offline, so it warns when such a claim is made against an unpinned pointer.
Pin `source.ref` to a full commit SHA and the claim becomes falsifiable by anyone who
fetches it.

Time facts are explicit `known`/`unknown` values. A known day uses
`YYYY-MM-DD` with `precision: "day"`; a known second uses an RFC 3339 UTC value
ending in `Z` with `precision: "second"`. Never use the current date, clone time,
or synchronization time to fill an unknown catalog or release timestamp.

Collection children stay in their parent's sidecar. Each child declares the
canonical `skill + parentId + id` identity and its own release fact; a collection
parent may have an unknown version, and a child version must not be inferred from
the parent.

The strict source schema is
[`schemas/catalog-metadata.v1.schema.json`](schemas/catalog-metadata.v1.schema.json).

## Categories

Valid category slugs are declared in `categories.json`:

```text
productivity, development, business, creative, design, media,
communication, research, data, management
```

## Validation

Run these checks before submitting changes:

```bash
# Full market + i18n validation
uv run scripts/i18n/validate-i18n.py

# Catalog sidecar validator unit tests and standalone validation
uv run scripts/catalog/test_validate_catalog_metadata.py
uv run scripts/catalog/test_collection_generator.py
uv run scripts/catalog/validate_catalog_metadata.py

# Translation freshness check
uv run scripts/i18n/translate.py --check

# Verify pinned collection children without changing entry.json (network required;
# mutable collections are reported and skipped because their output is not reproducible)
uv run scripts/gen-collection-children.py --check

# Optional network check for entry.json source URLs
uv run scripts/i18n/validate-i18n.py --online
```

The validators check market stats, category references, `builtin-skills.json`,
`entry.json` structure, sidecar schema and legacy consistency, immutable source
evidence, collection identity, i18n completeness, and translation freshness.
Human-locked translations (`translated_by: human`) must keep `source_hash`
aligned after manual review. During a data migration,
`scripts/catalog/validate_catalog_metadata.py --require-complete` additionally
requires one sidecar for every top-level Agent, Team and Skill.

Detailed i18n guidance is in [docs/I18N.md](docs/I18N.md).

## License

MIT License. See [LICENSE](LICENSE).
