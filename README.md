# DesireCore Market

DesireCore 官方市场仓库，存放官方维护的 Agent/Skill 定义，以及经过整理的第三方 Skill 入口。

## Repository Shape

```
.
├── manifest.json          # Market metadata, supported locales, aggregate stats
├── categories.json        # Category registry and localized labels
├── builtin-skills.json    # Built-in local SKILL.md skills
├── agents/
│   └── desirecore/
│       └── agent.json
└── skills/
    ├── <local-skill>/
    │   ├── SKILL.md
    │   └── SKILL.<locale>.md
    └── <external-entry>/
        └── entry.json
```

The market currently contains:

- `1` Agent: `desirecore`
- `34` local built-in skills with `SKILL.md`
- `28` external skill entries with `entry.json`
- `62` publishable skills in total (`SKILL.md` + `entry.json`)

## Skill Sources

Local built-in skills are installable from this repository and must be listed in `builtin-skills.json`:

```text
code-intelligence, configuring-compute, create-agent, dashscope-image-gen, delete-agent,
dev-environment-setup, discover-agent, docx, frontend-design, guizang-ppt,
image-to-image, mail-operations, manage-skills, manage-teams, markdown,
minimax-music-gen, minimax-video-gen, nodejs-runtime, pdf, pptx,
presentation-forge, python-runtime, registering-services, s3-storage-operations, skill-creator,
tech-diagram, update-agent, using-services, web-access, workflow, workforce-optimization,
xiaomi-tts, xlsx
```

`builtin-skills.json#retired` lists old built-in Skill IDs that clients may safely retire during
startup. Clients only remove copies tracked in `skills.lock` as market/bundled content whose
`SKILL.md` hash still matches the installed record; manually installed or locally modified copies
are preserved. An ID must not appear in both `skills` and `retired`.

External entries are marketplace pointers to Git/Web/ZIP sources:

```text
agent-reach, ai-news-radar, amap-jsapi-skill, baoyu-skills, dingtalk-api,
flyai-skill, follow-builders, humanizer, humanizer-zh,
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

### Catalog metadata sidecar (`catalog-metadata.v1.json`)

The versioned catalog metadata contract is stored at one fixed path next to each
legacy item:

```text
agents/<id>/catalog-metadata.v1.json
skills/<id>/catalog-metadata.v1.json
```

Legacy `agent.json`, `SKILL.md`, and `entry.json` files remain the compatibility
surface for older clients. New clients merge the sidecar through a deterministic
adapter. Any field repeated in both files must have the same value; the validator
rejects drift rather than choosing one copy silently.

The sidecar records source-owned presentation, release, timestamp, content
provenance, governance, compatibility, and type-specific facts. It deliberately
cannot declare `catalogSourceId`, catalog commit/path/trust, effective official
status, installation state, device state, health, URLs discovered at runtime, or
`syncedAt`. DesireCore injects trusted catalog provenance and runtime facts.

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
requires one sidecar for every top-level Agent and Skill.

Detailed i18n guidance is in [docs/I18N.md](docs/I18N.md).

## License

MIT License. See [LICENSE](LICENSE).
