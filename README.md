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
- `30` local built-in skills with `SKILL.md`
- `22` external skill entries with `entry.json`
- `52` publishable skills in total (`SKILL.md` + `entry.json`)

## Skill Sources

Local built-in skills are installable from this repository and must be listed in `builtin-skills.json`:

```text
configuring-compute, create-agent, dashscope-image-gen, delete-agent,
dev-environment-setup, discover-agent, docx, frontend-design, guizang-ppt,
image-to-image, mail-operations, manage-skills, manage-teams, markdown,
minimax-music-gen, minimax-video-gen, nodejs-runtime, pdf, pptx,
python-runtime, registering-services, s3-storage-operations, skill-creator,
tech-diagram, update-agent, using-services, web-access, workflow,
xiaomi-tts, xlsx
```

External entries are marketplace pointers to Git/Web/ZIP sources:

```text
agent-reach, ai-news-radar, amap-jsapi-skill, dingtalk-api, flyai-skill,
follow-builders, ian-xiaohei-illustrations, impeccable, khazix-skills,
larksuite-cli, luckin-my-coffee, mattpocock-skills, minimax-image-gen,
minimax-tts, mt-paotui-for-client, netease-skills, taste-skill, watchless,
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

# Translation freshness check
uv run scripts/i18n/translate.py --check

# Optional network check for entry.json source URLs
uv run scripts/i18n/validate-i18n.py --online
```

The validator checks market stats, category references, `builtin-skills.json`, `entry.json` structure, i18n completeness, and translation freshness. Human-locked translations (`translated_by: human`) must keep `source_hash` aligned after manual review.

Detailed i18n guidance is in [docs/I18N.md](docs/I18N.md).

## License

MIT License. See [LICENSE](LICENSE).
