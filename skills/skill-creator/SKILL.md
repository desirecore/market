---
name: skill-creator
description: >-
  引导用户创建和编辑符合规范的 SKILL.md 技能包。支持 DesireCore 完整格式
  （frontmatter 元数据 + L0/L1/L2 分层内容 + 脚本/参考/资产）和 Claude Code
  基础格式。Use when 用户要求创建新技能、更新已有技能、或将经验封装为可复用
  的技能包。
version: 1.0.3
type: meta
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - skill
  - creation
  - meta
  - template
  - authoring
metadata:
  author: desirecore
  updated_at: '2026-05-05'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 技能创建器
      short_desc: 引导创建符合规范的 SKILL.md 技能包，支持完整元数据与分层内容
      description: >-
        引导用户创建和编辑符合规范的 SKILL.md 技能包。支持 DesireCore 完整格式 （frontmatter 元数据 + L0/L1/L2 分层内容 + 脚本/参考/资产）和 Claude Code 基础格式。Use when 用户要求创建新技能、更新已有技能、或将经验封装为可复用 的技能包。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:fa0f3136371f236c
      translated_by: human
    en-US:
      name: Skill Creator
      short_desc: Guides creation of standards-compliant SKILL.md packages with complete metadata and layered content
      description: >-
        Guides users to create and edit standards-compliant SKILL.md skill packages. Supports the DesireCore full format (frontmatter metadata + L0/L1/L2 layered content + scripts/references/assets) and the Claude Code basic format. Use when the user requests to create a new Skill, update an existing Skill, or package experience into a reusable Skill bundle.
      body: ./SKILL.md
      source_hash: sha256:2e8b886dc0b77dd1
      translated_by: human
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="sc" x1="3" y1="3" x2="21"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#AF52DE"/><stop
    offset="1" stop-color="#34C759"/></linearGradient></defs><rect x="4" y="4"
    width="16" height="16" rx="3.5" fill="url(#sc)" fill-opacity="0.12"
    stroke="url(#sc)" stroke-width="1.5"/><path d="M8 8h8M8 12h5"
    stroke="url(#sc)" stroke-width="1.8" stroke-linecap="round"/><path d="M15
    14l2 2-2 2" stroke="#34C759" stroke-width="2" stroke-linecap="round"
    stroke-linejoin="round"/></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
---

# skill-creator Skill

## L0: One-line Summary

Guides users to package requirements, experience, and workflows into structured SKILL.md skill bundles.

## L1: Overview and Use Cases

### Capability

skill-creator is a **Meta-Skill** that gives an Agent the ability to create and edit Skills. Skills are modular, self-contained capability packages that, via SKILL.md, provide an Agent with domain knowledge, workflows, and tool integrations—turning the Agent from a general assistant into a domain expert.

### Use Cases

- The user wants to package a repeatedly executed workflow into a reusable Skill
- The user wants to create a new Skill to teach the Agent a new capability
- The user wants to update an existing Skill and improve its effectiveness
- The user has shared reference material that needs to be organized into a structured Skill bundle

### Core Value

- **Distill experience**: Solidify personal knowledge and workflows into reusable Skills
- **Self-extension**: Skills you create let the Agent's capabilities grow continuously
- **Standardization**: Generate standards-compliant SKILL.md files so the Skill system parses and distributes them correctly

## L2: Detailed Specification

### About Skills

Skills are modular, self-contained capability packages that provide an Agent with:

1. **Specialized workflows** — multi-step processes for a specific domain
2. **Tool integrations** — guidance for handling specific file formats or APIs
3. **Domain knowledge** — company conventions, business logic, specialized schemas
4. **Bundled resources** — scripts, reference docs, and asset files

### Core Principles

#### Conciseness First

The context window is a shared resource. A Skill shares the context window with the system prompt, conversation history, other Skill metadata, and the user request.

**Default assumption: the AI is already very capable.** Only add what the AI does not already know. For each piece of information, ask yourself: "Does the AI really need this explained?" "Is this paragraph worth its Token cost?"

Prefer concise examples over verbose explanations.

#### Set the Right Level of Latitude

Match instruction specificity to the task's fragility and variability:

- **High latitude (text guidance)**: when multiple approaches work and decisions depend on context
- **Medium latitude (pseudocode or parameterized scripts)**: when there is a preferred pattern but some variation is allowed
- **Low latitude (fixed scripts with few parameters)**: when the operation is fragile and error-prone, and consistency is critical

#### Progressive Disclosure

A Skill uses a three-tier loading system to manage context efficiently:

1. **Metadata (name + description)** — always in context (~100 words)
2. **SKILL.md body** — loaded when the Skill is triggered (<5k words)
3. **Bundled resources** — loaded by the Agent on demand (no limit; scripts can be executed directly without being read into context)

### Skill Structure

```
skill-name/
├── SKILL.md          (required: skill definition file)
├── scripts/          (optional: executable scripts)
├── references/       (optional: reference docs)
└── assets/           (optional: output asset files)
```

#### SKILL.md Format

A SKILL.md consists of two parts: **Frontmatter (YAML metadata)** and **Body (Markdown instructions)**.

##### Frontmatter Fields

**Required**:

| Field | Type | Description |
|------|------|------|
| `description` | string | Skill purpose description. **Must include a "Use when" trigger hint**—the AI uses this to decide when to invoke the Skill |

**Recommended**:

| Field | Type | Description | Default |
|------|------|------|--------|
| `name` | string | Skill display name | Directory name |
| `version` | string | Semantic version (e.g. `1.0.0`) | — |
| `type` | enum | `procedural` / `conversational` / `meta` | — |
| `risk_level` | enum | `low` / `medium` / `high` | — |
| `status` | enum | `enabled` / `disabled` | `enabled` |
| `tags` | string[] | List of tags | — |
| `metadata` | object | `author`, `updated_at` | — |

**Feature Controls**:

| Field | Type | Default | Description |
|------|------|------|------|
| `disable-model-invocation` | boolean | `true` | `false` = opt-in auto-injection of full SKILL.md content into the system prompt (auto-loaded); `true` (or omitted) = no auto-injection, only loaded when an Agent explicitly invokes the Skill tool (aligned with Claude Skills: disabled by default, opt-in) |
| `user-invocable` | boolean | `true` | `false` = does not appear in command completion; serves only as background knowledge |
| `allowed-tools` | string[] | — | Restricts the list of tools available at execution time |
| `requires` | object | — | Dependency declaration: `tools`, `optional_tools`, `connections` |

For the full field table (including market publishing, JSON output, fork execution, and other advanced fields), see [references/desirecore-format.md](references/desirecore-format.md).

> **Claude Code compatibility note**: Claude Code uses only `name` + `description` (plus optional `license`, `compatibility`). These fields are fully legal in DesireCore—the DesireCore format is a superset of Claude Code.

##### Body Structure

**Recommended L0/L1/L2 layering**:

```markdown
# skill-id Skill

## L0: One-line Summary
Describe in one sentence what this Skill does.

## L1: Overview and Use Cases
### Capability / ### Use Cases / ### Core Value

## L2: Detailed Specification
### Concrete steps / ### Error handling
```

Layered loading mechanism:
- **L0** (~50 chars): quickly understand what the Skill does
- **L1** (~300 chars): decide whether it applies to the current task
- **L2** (unlimited): the complete execution guide

> Layering is not mandatory. If the Skill content is short (<100 lines), you can skip layering—the parser will fall back to using the entire content. The unlayered Claude Code format also works in DesireCore.

#### Bundled Resources

##### Scripts (`scripts/`)

Executable code (Python/Bash, etc.) used for tasks that need deterministic reliability or are written repeatedly.

- **When to use**: the same code is written repeatedly, or deterministic reliability is needed
- **Examples**: `scripts/rotate_pdf.py` (PDF rotation), `scripts/fill_form.py` (form filling)
- **Advantages**: token-efficient, deterministic, can be executed directly without being read into context
- **Note**: scripts may still need to be read by the AI for environment adaptation

##### References (`references/`)

Documents and reference material loaded into context on demand.

- **When to use**: detailed documentation that the AI needs while working
- **Examples**: API docs, database schemas, domain knowledge, company policies
- **Best practice**: for large files (>10k words), provide grep search patterns in SKILL.md
- **Avoid duplication**: keep information in only one place—either SKILL.md or references

##### Assets (`assets/`)

Files that are not loaded into context but used in the output.

- **When to use**: files the Skill needs in the final output
- **Examples**: PPT templates, HTML scaffolds, logo images, font files
- **Advantage**: separates output assets from documentation

#### What Should Not Be Included

A Skill should contain only the files the AI needs to execute the task. **Do not** create README.md, INSTALLATION_GUIDE.md, CHANGELOG.md, or other ancillary documentation.

### Progressive Disclosure Patterns

Keep the SKILL.md body within 500 lines. When approaching the limit, split content into references.

**Pattern 1: High-level guide + reference files**

```markdown
# PDF Processing

## Quick start
[core code example]

## Advanced features
- **Form filling**: See [FORMS.md](FORMS.md)
- **API reference**: See [REFERENCE.md](REFERENCE.md)
```

**Pattern 2: Organized by domain**

```
bigquery-skill/
├── SKILL.md (overview)
└── references/
    ├── finance.md
    ├── sales.md
    └── product.md
```

When the user asks about sales metrics, the AI reads only sales.md.

**Pattern 3: Basic content + conditional advanced content**

```markdown
## Editing documents
For simple edits, modify the XML directly.
**For tracked changes**: See [REDLINING.md](REDLINING.md)
```

**Important**: avoid deep nested references—references should be linked only one level directly from SKILL.md. Long reference files (>100 lines) should include a table of contents at the top.

### Creation Workflow

1. Understand the Skill requirements with concrete examples
2. Plan reusable resources (scripts, references, assets)
3. Initialize the Skill (run init_skill.py)
4. Edit the Skill (implement resources, write SKILL.md)
5. Validate the Skill (run quick_validate.py)
6. Install the Skill
7. Iterate and refine

#### Step 1: Understand the Skill Requirements

Skip this step only when the Skill's usage pattern is already completely clear. Even when working on an existing Skill, this step still has value.

Use concrete examples to understand how the Skill will be used. For instance, when building an image-editor Skill:

- "What features should this Skill support? Editing, rotating, anything else?"
- "Can you give a few use cases?"
- "What action should trigger this Skill?"

Avoid asking too many questions at once—start with the most important and follow up as needed. End this step when you have a clear understanding of what features the Skill should support.

#### Step 2: Plan Resources

For each example, analyze:

1. Consider how to execute it from scratch
2. Identify which scripts, references, and assets would help when executing repeatedly

Example analysis:

- `pdf-editor` handles "rotate PDF" → the same code is written every time → `scripts/rotate_pdf.py`
- `frontend-webapp-builder` handles "create todo app" → boilerplate is written every time → `assets/hello-world/`
- `big-query` handles "how many users logged in today" → the schema is queried every time → `references/schema.md`

#### Step 3: Initialize

Use init_skill.py to create a template:

```bash
# DesireCore full format (default, recommended)
scripts/init_skill.py <skill-name> --path <output-directory>

# Claude Code basic format
scripts/init_skill.py <skill-name> --path <output-directory> --format basic
```

By default this generates the DesireCore format (with full frontmatter + L0/L1/L2 structure). `--format basic` generates the minimal Claude Code-compatible format.

After initialization, customize or delete the generated example files as needed.

#### Step 4: Edit the Skill

##### Learn the Design Patterns

Consult references based on the Skill's needs:

- **Multi-step workflows**: see [references/workflows.md](references/workflows.md)
- **Output format standards**: see [references/output-patterns.md](references/output-patterns.md)

##### Start from Resources

First implement the resource files identified in Step 2 (scripts/, references/, assets/). This step may need user input—e.g. brand assets require the user to supply a logo.

Any script you add must actually be run and tested to ensure it is bug-free and its output meets expectations. Unneeded example files should be deleted.

##### Write SKILL.md

**Frontmatter writing tips**:

- `description` is the most critical field—the AI uses it to decide when to trigger the Skill
- Include a "Use when" trigger hint and typical use cases in description
- Put all "when to use" information in description, not in the body (the body is loaded only after the Skill is triggered)

**Body writing tips**:

- Always use imperative/infinitive form
- L0 should be no longer than one sentence
- L1 is for deciding applicability and should not exceed 300 characters
- L2 holds the complete steps, API calls, and error handling

#### Step 5: Validate

```bash
scripts/quick_validate.py <path/to/skill-folder>
```

Validates SKILL.md format, the legality of frontmatter fields, and the directory structure.

#### Step 6: Install

**Option A: Install via API (recommended; requires the Agent Service to be running)**

```bash
PORT=$(cat ${DESIRECORE_ROOT}/agent-service.port 2>/dev/null)

# Install as a global Skill (visible to all Agents)
curl -k -X POST "https://127.0.0.1:${PORT}/api/skills" \
  -H "Content-Type: application/json" \
  -d "{\"skillId\": \"<skill-name>\", \"content\": \"$(cat path/to/SKILL.md | jq -Rsa .)\"}"

# Install as an Agent-scoped Skill (visible only to the specified Agent)
curl -k -X POST "https://127.0.0.1:${PORT}/api/agents/<agentId>/skills" \
  -H "Content-Type: application/json" \
  -d "{\"id\": \"<skill-name>\", \"fullContent\": \"$(cat path/to/SKILL.md | jq -Rsa .)\"}"
```

**Option B: Direct filesystem write**

```bash
# Global Skill
cp -r path/to/skill-name ${DESIRECORE_ROOT}/skills/

# Agent-scoped Skill
cp -r path/to/skill-name ${DESIRECORE_ROOT}/agents/<agentId>/skills/
```

**Option C: Package as a .skill file (Claude Code compatible)**

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Generates a `skill-name.skill` file (ZIP format) usable in Claude Code.

**After installation, you must report to the user**:
- The full path the Skill was installed to
- The installation scope (Global / Agent / Project)
- How to trigger this Skill in subsequent conversations

#### Step 7: Iterate

1. Use the Skill on real tasks
2. Observe shortcomings or inefficiencies
3. Decide how the SKILL.md or its resources need to change
4. Apply the changes and test again

### Scope Notes

Skills exist at three scope levels, listed from highest priority to lowest:

| Priority | Scope | Path | Visibility |
|--------|--------|------|---------|
| Highest | Project | `.claude/skills/` | All Agents in the current project |
| Medium | Agent | `${DESIRECORE_ROOT}/agents/{agentId}/skills/` | Only that Agent |
| Lowest | Global | `${DESIRECORE_ROOT}/skills/` | All Agents |

Skills with the same name override each other by priority—a higher-priority Skill shadows a lower-priority one with the same name.
