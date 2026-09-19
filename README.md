# DesireCore Market

**English** | [简体中文](README.zh-CN.md)

The official, version-controlled catalog of **Agents, Teams, and Skills for DesireCore**.

Discover reusable assistants, coordinated agent teams, and task-specific skills in one place. This repository maintains catalog metadata, locally bundled skills, and curated pointers to upstream content, together with schemas and validation tools for consistent publication.

[Overview](#overview) · [Getting started](#getting-started) · [Repository layout](#repository-layout) · [Listing contracts](#listing-contracts) · [Localization](#localization) · [Contributing](#contributing) · [Validation](#validation) · [Security and trust](#security-and-trust) · [Related projects](#related-projects) · [License](#license)

## Overview

| Resource | Purpose | Where to explore |
| --- | --- | --- |
| **Agents** | Individual assistants with a defined role, capabilities, and configuration; published as inline metadata or an upstream pointer. | [`agents/`](agents/) |
| **Teams** | Groups of agents coordinated by a supervisor; published as pointers to repositories that the client forks. | [`teams/`](teams/) |
| **Skills** | Reusable task instructions and supporting resources; bundled locally or discovered through upstream Git, Web, or ZIP sources. | [`skills/`](skills/) |

The market is a **content catalog, not a standalone application or execution runtime**. A listing describes what a resource is, where it comes from, and the conditions under which it can be used. Installation and execution belong to a compatible DesireCore client and the resource's dependencies.

### Catalog sources of truth

| File | What it defines |
| --- | --- |
| [`manifest.json`](manifest.json) | Market identity, schema version, supported locales, default locale, and aggregate statistics. |
| [`categories.json`](categories.json) | Valid category IDs and their localized labels and descriptions. |
| [`builtin-skills.json`](builtin-skills.json) | Local built-in skill IDs and the retirement list. |
| `catalog-metadata.v1.json` beside each listing | Versioned presentation, release, provenance, governance, and compatibility facts. |

Use the manifest and actual catalog directories for the current inventory rather than maintaining a second list of counts in this README. `totalSkills` counts top-level local `SKILL.md` listings plus external `entry.json` listings, not every child inside a skill collection. `totalTeams` may be omitted for a catalog with no teams; when present, it must match the catalog exactly.

Categories cover productivity, development, business, creative work, design, media, communication, research, data, and management. Use the IDs in `categories.json` when publishing; display labels are not category IDs.

## Getting started

### Use the market in DesireCore

1. Open the market in a compatible DesireCore client and synchronize the official catalog.
2. Inspect the resource's description, source, release information, client requirements, license, and external dependencies before installation. Read any available usage notes.
3. Follow the client's installation flow when the listing is installable, then complete any required local setup or authorization. Keep credentials and private configuration outside this public repository.

**Listed does not necessarily mean installable.** Catalog metadata can describe listing-only resources; compatibility, governance, source reproducibility, or licensing requirements may prevent installation. Catalog synchronization also does not upgrade the desktop client or provision third-party services.

### Explore or contribute locally

For repository maintenance, use Git, Python **3.10 or newer**, and `uv`. The Python scripts declare their dependencies inline; `uv run` manages their execution environments.

```bash
git clone https://github.com/desirecore/market.git
cd market

# Validate market structure and skill localization.
uv run scripts/i18n/validate-i18n.py
```

Initial environment setup may download Python packages. The validation command above does not require model API credentials or fetch upstream content unless `--online` is supplied. See [Validation](#validation) for coverage checks, translation freshness, and focused commands.

Cloning this repository only downloads the catalog and bundled files; it does not install the DesireCore client, agents, teams, or external products.

## Repository layout

```text
.
├── README.md                         # English overview and contributor guide
├── README.zh-CN.md                   # Simplified Chinese counterpart
├── manifest.json                     # Market metadata, locales, and statistics
├── categories.json                   # Category registry
├── builtin-skills.json               # Built-in skills and retirement policy
├── agents/<id>/
│   ├── agent.json OR entry.json       # Exactly one primary listing file
│   ├── catalog-metadata.v1.json       # Versioned catalog metadata
│   └── USAGE[.<locale>].md            # Optional inline-agent usage notes
├── teams/<id>/
│   ├── entry.json                    # Upstream Git fork pointer only
│   └── catalog-metadata.v1.json
├── skills/<id>/
│   ├── SKILL.md OR entry.json         # Local skill or external source pointer
│   ├── catalog-metadata.v1.json
│   ├── SKILL.<locale>.md              # Localized body for a local skill
│   ├── references/                   # Optional supporting documentation
│   └── scripts/                      # Optional skill-specific helpers
├── schemas/                          # Catalog and exported client contracts
├── scripts/
│   ├── catalog/                      # Catalog validation and focused tests
│   ├── i18n/                         # Localization schema, validation, translation
│   └── gen-collection-children.py     # Upstream collection inventory generation
├── docs/                             # Authoring and application guides
├── .github/workflows/                # Validation, translation, and review automation
├── AGENTS.md / CLAUDE.md              # Equivalent repository contribution policies
├── LICENSE                           # License for repository-original content
└── THIRD_PARTY_NOTICES.md             # Third-party licensing qualifications
```

The tree illustrates supported shapes, not files required in every directory. Localized bodies, helper scripts, and references belong to local skills; external pointers keep their implementation upstream. A team directory contains `entry.json` and its sidecar, not an inline `team.json`.

## Listing contracts

Use the schemas and existing listings as implementation references. A shortened JSON example is not a substitute for the complete client contract.

### Local skills

A local skill lives at `skills/<id>/SKILL.md` and combines YAML frontmatter with a Markdown instruction body. Its top-level `name` must match the directory's lowercase ASCII slug; localized display names belong in `metadata.i18n`.

Only `SKILL.md` carries frontmatter. Localized `SKILL.<locale>.md` files contain the body, start with the corresponding locale comment, and are referenced by the i18n metadata. For example, `SKILL.zh-CN.md` starts with `<!-- locale: zh-CN -->`. Market skills must set `disable-model-invocation: true` or omit the field; `false` is rejected.

Register every local built-in skill in `builtin-skills.json.skills`, supply its sidecar, and use a valid market category. See the [frontmatter schema](scripts/i18n/schema/skill-frontmatter.schema.json), [Web Access example](skills/web-access/SKILL.md), and [i18n authoring guide](docs/I18N.md) (Chinese).

The `retired` list identifies former built-in skills that clients may retire at startup. Clients remove only market/bundled copies tracked in `skills.lock` whose `SKILL.md` hash still matches the installation record. Manually installed or locally modified copies are preserved. An ID must never appear in both `skills` and `retired`.

### External skills and collections

An external skill uses `skills/<id>/entry.json` to describe its upstream source, presentation, maintainer, category, license, and redistribution terms. Skill listings require an inline SVG `icon`. Supported source kinds are `git`, `web`, and `zip`; external listings count toward `manifest.stats.totalSkills` but do not belong in the built-in skill index.

A collection groups multiple upstream skills under one listing, with a declared `children` inventory for discovery. Keep the children's metadata in the parent's sidecar. Each child has its own `skill + parentId + id` identity and release fact; never infer a child's version from its parent, whose version may be unknown.

See the [Lark Suite CLI entry](skills/larksuite-cli/entry.json) and [sidecar](skills/larksuite-cli/catalog-metadata.v1.json). The [collection generator](scripts/gen-collection-children.py) derives children from upstream `SKILL.md` files; its `--check` mode verifies reproducible, pinned collections without rewriting entries.

### Agents

An agent directory must contain exactly one primary file: `agent.json` for inline metadata **or** `entry.json` for an external pointer, plus `catalog-metadata.v1.json`. Neither a missing primary file nor both files together is valid.

For pointers, the directory slug, `entry.id`, and sidecar `identity.id` must agree, and `identity.kind` is `agent`. The upstream AgentFS `agent.json.id` is a separate UUID and must not be rewritten to match the catalog slug.

The raw pointer must pass the [exported agent client schema](schemas/market-agent-entry.client.schema.json) before sidecar validation. Preserve version types and supported formats. `installPolicy` and `updatePolicy` must either both be absent, with effective values `market/market`, or form a complete supported pair. The sidecar must preserve that effective pair rather than reclassifying the resource as a system item.

`latestVersion` maps to `release.version`; client requirements, policies, and source fields must agree across the pointer and sidecar. `maintainer` maps to `upstreamMaintainer`. An installable pointer must itself pin a full Git commit in `source.ref`, or a Web/ZIP digest in `source.sha256`; a pin declared only in the sidecar is insufficient. Agent pointers do not receive the built-in skill exceptions to source, license, or review requirements.

An inline agent may include concise, text-only `USAGE.md` notes for prerequisites, authorization, and safety boundaries. Localized variants use `USAGE.<locale>.md`, resolved by requested locale → source locale → default locale → unsuffixed file. Usage is displayed separately from `fullDesc`, which also enters the agent's runtime context. Clients may truncate long notes; put extensive supporting material in skill `references/` instead. Relative images do not render in the usage section.

Examples: [inline DesireCore agent](agents/desirecore/agent.json) and [DingTalk Workspace pointer](agents/dingtalk-workspace/entry.json).

### Teams

A team is a supervisor-led group of agents, published **only as a Git fork pointer** at `teams/<id>/entry.json`, alongside its sidecar. The implementation (`team.json`, `members.json`, and `shared/`) stays upstream. Installation forks that repository and installs its declared members; subsequent updates use `git pull` on the fork.

Consequently, `source.kind` must be `git`, `source.repoUrl` is required, and an installable pointer must pin a full commit SHA in `source.ref`. Branches and tags are mutable and do not satisfy that pin. Teams have no `installPolicy` / `updatePolicy` pair, and `redistribution` remains `source-pointer-only` even when the upstream license is permissive.

The raw pointer must pass the [exported team client schema](schemas/market-team-entry.client.schema.json). The directory slug, `entry.id`, and sidecar `identity.id` must agree; `identity.kind` is `team`, and `latestVersion` maps to `release.version`. Source fields must describe the same artifact as `provenance.content`.

`supervisorName`, `supervisorAgentId`, `memberCount`, `memberNames`, `requiredSkills`, and `requiredClientVersion` must agree symmetrically with the sidecar: it may neither drop declared facts nor invent absent ones. Member and supervisor display metadata is not installation or permission authority; resolve those facts from the forked `team.json` and `members.json`.

Agent and team cards use `avatar`, not the skill-only `icon` presentation. An `icon` accepted by a shared entry contract still does not reach these cards, and the validator warns about it. See the [Contract Review Team entry](teams/contract-review-team/entry.json).

### Versioned catalog metadata

Every top-level listing must have `catalog-metadata.v1.json` at the fixed location beside its primary file. This **sidecar** supplements the legacy compatibility file; it does not replace `agent.json`, `entry.json`, or `SKILL.md`. New clients merge it through a deterministic adapter, and validators reject inconsistent duplicated fields.

The [catalog metadata schema](schemas/catalog-metadata.v1.schema.json) covers presentation, releases, explicit timestamp facts, content provenance, governance, compatibility, and type-specific metadata. Keep these boundaries intact:

- **Source facts versus runtime facts.** A sidecar cannot declare trusted catalog identity (`catalogSourceId`), catalog commit/path/trust, effective official status, installed state, device state, health, runtime-discovered URLs, or `syncedAt`. DesireCore supplies trusted catalog provenance and runtime observations.
- **Evidence paths follow the content.** `license.evidencePath`, `compliance.licenseEvidencePath`, and `compliance.noticePath` are relative to the item directory for vendored content, and the files must exist. For pointers they refer to the upstream snapshot; offline validation cannot fetch that evidence and warns about claims against unpinned sources.
- **Unknown is a valid fact.** Use explicit `known` / `unknown` states. A known day uses `YYYY-MM-DD` with `precision: "day"`; a known second uses an RFC 3339 UTC timestamp ending in `Z` with `precision: "second"`. Never fill an unknown release or catalog timestamp with the current date, clone time, or synchronization time.

The agent and team client schemas are generated compatibility snapshots. Their `$comment` records the upstream source commit and blob. Refresh them from the corresponding TypeScript exports when compatibility changes; do not weaken them or substitute sidecar-only validation.

## Localization

The market declares its languages in `manifest.json.supportedLocales`, currently `en-US` and `zh-CN`, with English as the default. Local skill display text lives in `metadata.i18n`; listing JSON and sidecars retain their own schema-defined i18n shapes rather than sharing interchangeable field names.

For skill bodies, resolve the requested locale, then the source locale, then the default locale. Keep the default body in `SKILL.md`, reference localized bodies explicitly, and keep heading structure aligned across languages. The [glossary](scripts/i18n/glossary.json) records shared terminology.

The [translation workflow](.github/workflows/i18n-translate.yml) translates eligible missing or stale skill locales using configured model credentials. Review its output for terminology, structure, and factual accuracy; automation is not a substitute for review. `translated_by: human` locks a translation against automatic replacement. After a source change, manually synchronize that translation and refresh `source_hash` only after review; never use a fabricated hash to silence a freshness failure.

Run `translate.py --check` to inspect freshness without calling a model API or rewriting translations. Backend configuration and the authoring workflow are documented in the [i18n guide](docs/I18N.md) (Chinese); the workflow and script are authoritative for current behavior. These two README files are maintained together manually and are not inputs to the skill translation pipeline.

## Contributing

Contributions can add reusable resources, improve existing listings, correct metadata, strengthen validation, or improve translations and documentation.

1. **Choose the right destination.** Agents, teams, and skills belong here; application entries belong in [DesireCore Registry](https://github.com/desirecore/registry). Read [AGENTS.md](AGENTS.md) or [CLAUDE.md](CLAUDE.md) before editing.
2. **Work from the current `main` branch.** Use a focused branch or isolated worktree. Select the correct listing shape, a stable public slug, and a valid category. Reuse existing examples without copying their identities, review status, or licensing claims.
3. **Publish a complete, consistent listing.** Keep the primary file and sidecar aligned; supply localization, provenance, license evidence, compatibility, and dependency disclosures. Update `builtin-skills.json` for local skills and `manifest.json` statistics when the inventory changes. Do not invent unknown dates or versions.
4. **Verify before publication.** Run the applicable checks below, review translations, and follow the private-token and public-information checks in the repository policy. Scan the working tree, including hidden files except `.git`, as well as new paths, branch names, commit messages, and proposed PR text. Keep confidential search tokens outside the repository.
5. **Open a pull request against `main`.** Explain the reusable use case, source and licensing decisions, compatibility impact, and validation performed. Use generic examples, keep both README languages synchronized when changing this guide, and wait for required checks and review before merging.

For catalog errors, broken pointers, or documentation issues, open an [issue](https://github.com/desirecore/market/issues) with the listing ID, relevant client version, expected behavior, and sanitized reproduction details. Report upstream implementation bugs to the upstream project when appropriate. Never include credentials, private customer data, or confidential incident evidence in a public issue.

## Validation

Run commands from the repository root. The scripts use their inline dependency declarations, so a separate application build or Node.js dependency installation is not required for catalog validation.

### Catalog and translation checks

```bash
# Market statistics, categories, built-in index, entries, sidecars, and skill i18n.
uv run scripts/i18n/validate-i18n.py

# Strict sidecar contracts and complete top-level listing coverage, as required by CI.
uv run scripts/catalog/validate_catalog_metadata.py --require-complete

# Missing or stale translations; no model API calls and no file changes.
uv run scripts/i18n/translate.py --check
```

The checks above do not fetch upstream source repositories. Package installation during environment setup may still require network access. A successful schema check is not proof of upstream license validity, external service availability, or successful installation in every client.

### Focused authoring and validator tests

```bash
# Limit skill-body validation and translation inspection to one existing skill.
uv run scripts/i18n/validate-i18n.py skills/web-access
uv run scripts/i18n/translate.py --check skills/web-access

# Run the relevant single-file suite when changing its validator or generator.
uv run scripts/i18n/test_validate_i18n.py
uv run scripts/catalog/test_validate_catalog_metadata.py
uv run scripts/catalog/test_collection_generator.py
```

Passing a skill path narrows skill-body validation, but market-level and sidecar checks still run. Choose the relevant test file for your change rather than treating every documentation edit as a reason to run all test suites.

### Network-dependent checks

```bash
# Compare declared children with pinned upstream collections without rewriting entries.
uv run scripts/gen-collection-children.py --check

# Optional source-URL availability checks in addition to normal validation.
uv run scripts/i18n/validate-i18n.py --online
```

Collection checking requires Git and network access. Mutable collections are reported and skipped because their generated inventory is not reproducible. Omitting `--check` runs the generator in write mode; review both the regenerated children and the corresponding sidecar facts before committing.

The [validation workflow](.github/workflows/i18n-validate.yml) is the source of truth for CI. It detects relevant paths and can skip catalog validation for documentation-only changes. A green skipped job is not evidence that Markdown links or bilingual documentation were checked; review those separately.

## Security and trust

**Official catalog hosting does not make every upstream resource DesireCore-authored, unrestricted, or ready to execute.** Review each resource's provenance, governance, availability, license, and compatibility rather than inferring trust from its directory or display name.

All contributions must be reusable, customer-neutral, and safe for public indexing. Keep tenant identities, private organization structures, customer-specific prompts, account mappings, credentials, and deployment details in private AgentFS homes, private repositories, or private runtime configuration. The same boundary applies to Git and GitHub metadata.

A connector or adapter does not bundle, license, install, pay for, or operate the third-party product it accesses. Disclose separately licensed, purchased, hosted, or deployed dependencies in discovery descriptions, compatibility information, localized text, and execution instructions. State operator prerequisites, applicable terms, relevant costs, readiness checks, and safe degraded behavior. When a required dependency is unavailable, stop before the external call and never fabricate success.

If confidential data is exposed, follow the incident-response policy in [AGENTS.md](AGENTS.md). Removing a current file or rewriting a branch does not by itself remove pull-request references, notifications, caches, or other copies.

## Related projects

| Project or guide | Responsibility |
| --- | --- |
| [DesireCore Registry](https://github.com/desirecore/registry) | Application catalog entries and authorized lifecycle metadata, separate from this Agent/Team/Skill catalog. |
| [DesireCore Control listing](https://github.com/desirecore/registry/tree/main/entries/desirecore-control) | Authoritative release source, checksum, compatibility requirements, and installation/uninstallation guide for Control. |
| [Control installation guide](docs/desirecore-control.md) | Using the native application from a compatible DesireCore client. |
| [Control implementation](https://github.com/desirecore-agent/desirecore-cdp-mcp) | Application source and releases. |

DesireCore Control is a native application for external agents. Its application listing belongs in Registry, not in a duplicate Skill or internal MCP service entry here. Installing Control does not register internal MCP tools, and publishing a catalog entry does not deploy a compatible desktop client or installation skill. Consult the authoritative listing and guide for current requirements rather than copying a release number into this overview.

## License

DesireCore-authored repository content is licensed under the [MIT License](LICENSE). **That license does not override the terms of bundled third-party content or external resources.**

Read [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), the resource's own license files, and its `license` / `redistribution` metadata. In particular, the notices identify the bundled `docx`, `pdf`, `pptx`, and `xlsx` skills as source-available reference implementations, not MIT-licensed open-source content; other bundled material may use Apache-2.0 or separate terms. External pointers remain governed by their upstream licenses.

A redistribution mode describes how content is delivered, not a replacement license. Verify the applicable upstream terms before redistribution or production use.
