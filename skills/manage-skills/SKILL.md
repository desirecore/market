---
name: manage-skills
description: >-
  管理 Agent 的技能生命周期：通过 HTTP API 导入、安装、更新、删除技能，
  或通过 AgentFS 文件系统直接编写符合规范的 SKILL.md。Use when 用户要求
  安装技能、从 URL/Git 导入技能、编写新技能、或管理已有技能。
version: 1.0.2
type: meta
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - skill
  - import
  - management
  - meta
  - agentfs
metadata:
  author: desirecore
  updated_at: '2026-03-03'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 管理技能
      short_desc: 导入、编写、安装与管理 Agent 技能的完整工具箱
      description: >-
        管理 Agent 的技能生命周期：通过 HTTP API 导入、安装、更新、删除技能， 或通过 AgentFS 文件系统直接编写符合规范的 SKILL.md。Use when 用户要求 安装技能、从 URL/Git 导入技能、编写新技能、或管理已有技能。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:7f116cc5de352822
      translated_by: human
    en-US:
      name: Manage Skills
      short_desc: Complete toolbox for importing, authoring, installing, and managing Agent Skills
      description: >-
        Manage the Skill lifecycle of an Agent: import, install, update, and delete Skills via HTTP API, or directly author standards-compliant SKILL.md files via the AgentFS filesystem. Use when the user requests to install Skills, import Skills from URL/Git, author new Skills, or manage existing Skills.
      body: ./SKILL.md
      source_hash: sha256:7f116cc5de352822
      translated_by: ai:claude-opus-4-7
      translated_at: '2026-05-03'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="ms-a" x1="3" y1="3" x2="21"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#AF52DE"/><stop
    offset="1" stop-color="#007AFF"/></linearGradient></defs><rect x="3" y="3"
    width="18" height="18" rx="4" fill="url(#ms-a)"
    fill-opacity="0.12" stroke="url(#ms-a)"
    stroke-width="1.5"/><path d="M8 12h8M12 8v8" stroke="url(#ms-a)"
    stroke-width="2" stroke-linecap="round"/><circle cx="18" cy="6" r="3"
    fill="#34C759" fill-opacity="0.9"/><path d="M17 6h2M18 5v2"
    stroke="white" stroke-width="1.2" stroke-linecap="round"/></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
---

# manage-skills Skill

## L0: One-line Summary

Manage the full lifecycle of Skills—import, author, install, update, and delete.

## L1: Overview and Use Cases

### Capability

manage-skills is a **Meta-Skill** that gives DesireCore the ability to manage the Skill system. It covers five core operations:

1. **Import a Skill from a URL** — supply a remote SKILL.md URL, fetch the content, and create
2. **Bulk import from a Git repository** — clone a Git repo, scan all SKILL.md files, and selectively import
3. **Manage existing Skills via API** — list, read, update, delete, enable/disable Skills
4. **Author SKILL.md directly via AgentFS** — use the Write/Edit tools to create Skills on the filesystem
5. **Bulk operations and cross-Agent copying** — bulk enable/disable/delete, plus copy Skills to other Agents

### Use Cases

- The user wants to import community-shared Skills from platforms like GitHub
- The user wants to install a new Skill on an Agent to enhance its capabilities
- The user needs to author a custom Skill to teach the Agent a new workflow
- The user wants to bulk-manage existing Skills (enable/disable/delete)
- The user wants to copy one Agent's Skill to another Agent
- The user needs to view or edit the contents of a Skill

### Core Value

- **Self-extension**: an Agent can autonomously expand its capability boundary by importing or authoring Skills
- **Governable**: every Skill change goes through the API or filesystem operations and is traceable and auditable
- **Flexibility**: supports both API import and direct filesystem authoring to fit different scenarios

## L2: Detailed Specification

### 1. Import a Single Skill from a URL

For importing a single SKILL.md file (e.g. a GitHub raw link).

**Step 1: Fetch the remote content**

```bash
POST /api/skills/fetch-url
Content-Type: application/json

{
  "url": "https://raw.githubusercontent.com/user/repo/main/my-skill/SKILL.md"
}
```

**Success response** (`200 OK`):

```json
{
  "content": "---\nname: My Skill\ndescription: ...\n---\n\n# Skill content..."
}
```

**Security limits**:

- HTTPS URLs only
- 20MB file size limit
- 30-second request timeout

**Step 2: Create the Skill**

After a successful fetch, choose the creation endpoint based on scope:

**Create a global Skill** (visible to all Agents):

```bash
POST /api/skills
Content-Type: application/json

{
  "skillId": "my-skill",
  "content": "<content returned in the previous step>"
}
```

**Create an Agent-scoped Skill** (visible only to the specified Agent):

```bash
POST /api/agents/{agentId}/skills
Content-Type: application/json

{
  "id": "my-skill",
  "fullContent": "<content returned in the previous step>"
}
```

**Success response** (`201 Created`):

```json
{
  "success": true,
  "skill": { "id": "my-skill", "name": "My Skill", "description": "..." }
}
```

### 2. Bulk Import from a Git Repository

For importing a Git repository that contains multiple Skills.

**Step 1: Scan the repository**

```bash
POST /api/skills/fetch-git
Content-Type: application/json

{
  "url": "https://github.com/user/skill-collection.git"
}
```

**Success response** (`200 OK`):

```json
{
  "skills": [
    {
      "id": "data-analysis",
      "path": "data-analysis",
      "content": "---\nname: Data Analysis\n...",
      "sidecarFiles": [{ "name": "examples.md", "content": "..." }]
    },
    {
      "id": "report-writing",
      "path": "report-writing",
      "content": "---\nname: Report Writing\n..."
    }
  ]
}
```

The API automatically:

- Uses `--depth=1` shallow clone to reduce download size
- Recursively scans for SKILL.md files in directories
- Derives skillId from the directory name (falls back to a slug from the frontmatter name)
- Collects sidecar files in the same directory (e.g. examples.md, references/)
- Cleans up the temporary directory once finished

**Step 2: Import the chosen Skills one by one**

Show the scan results to the user and let them choose which Skills to import, then call the create API for each:

```bash
# Global Skill
POST /api/skills
{ "skillId": "data-analysis", "content": "<content>" }

# Or Agent-scoped Skill
POST /api/agents/{agentId}/skills
{ "id": "data-analysis", "fullContent": "<content>" }
```

**Handling sidecarFiles**: if the scan result contains sidecarFiles, after creating the Skill write them to the corresponding directory:

```bash
# Sidecar file path for a global Skill
~/.desirecore/skills/{skillId}/{filename}

# Sidecar file path for an Agent-scoped Skill
~/.desirecore/agents/{agentId}/skills/{skillId}/{filename}
```

### 3. Manage Existing Skills via API

#### List All Skills

```bash
GET /api/skills/list
GET /api/skills/list?agentId={agentId}
GET /api/skills/list?includeDisabled=true
```

Returns a Skill list covering all three scopes: project, agent, and global.

#### List Skills for a Specific Agent

```bash
GET /api/agents/{agentId}/skills
```

#### Read Skill Content

```bash
# Resolved automatically by scope priority
GET /api/skills/{skillId}/content
GET /api/skills/{skillId}/content?agentId={agentId}

# Read a specific Agent's Skill
GET /api/agents/{agentId}/skills/{skillId}
```

#### Update Skill Content

**Update a global Skill**:

```bash
PUT /api/skills/{skillId}/content
Content-Type: application/json

{
  "content": "---\nname: Updated Skill\n...\n---\n\n# New content..."
}
```

**Update an Agent-scoped Skill**:

```bash
PUT /api/agents/{agentId}/skills/{skillId}
Content-Type: application/json

{
  "content": "---\nname: Updated Skill\n...\n---\n\n# New content...",
  "bumpVersion": "minor"
}
```

`bumpVersion` accepts: `major` | `minor` | `patch`; when specified, the version number is auto-incremented. The system automatically updates `metadata.updated_at` whenever the content changes.

#### Delete a Skill

```bash
# Delete a global Skill
DELETE /api/skills/{skillId}

# Delete an Agent-scoped Skill
DELETE /api/agents/{agentId}/skills/{skillId}
```

#### Enable/Disable a Skill

```bash
# Global Skill
PATCH /api/skills/{skillId}/status
Content-Type: application/json
{ "enabled": false }

# Agent-scoped Skill
PATCH /api/agents/{agentId}/skills/{skillId}/status
Content-Type: application/json
{ "enabled": true }
```

#### Bulk Operations

```bash
POST /api/agents/{agentId}/skills/batch
Content-Type: application/json

{
  "action": "enable",
  "ids": ["skill-a", "skill-b", "skill-c"]
}
```

`action` accepts: `enable` | `disable` | `delete`

#### Copy a Skill to Another Agent

```bash
POST /api/agents/{targetAgentId}/skills/copy
Content-Type: application/json

{
  "sourceSkillId": "data-analysis",
  "sourceAgentId": "analyst",
  "targetSkillId": "data-analysis-v2"
}
```

Optional parameters:

- `sourceAgentId` — source Agent ID (required when copying from agent scope)
- `sourceSource` — source scope: `project` | `agent` | `global`
- `sourceWorkDir` — source project workDir (used when copying from project scope)
- `targetSkillId` — target Skill ID (defaults to sourceSkillId if omitted)

### 4. Author SKILL.md Directly via AgentFS

When you need to create a Skill from scratch or the API approach is not flexible enough, you can author SKILL.md directly on the filesystem.

#### Directory Structure

**Global Skill** (visible to all Agents):

```
~/.desirecore/skills/
└── my-new-skill/
    ├── SKILL.md          # required: skill definition file
    ├── examples/          # optional: example files
    ├── scripts/           # optional: helper scripts
    └── references/        # optional: reference material
```

**Agent-scoped Skill** (visible only to the specified Agent):

```
~/.desirecore/agents/{agentId}/
└── skills/
    └── my-new-skill/
        ├── SKILL.md
        └── ...
```

#### Full SKILL.md Format

```markdown
---
# === Required fields ===
description: >-
  Full description of the Skill's purpose. Should include a "Use when" trigger hint
  to help the AI decide when to use this Skill.

# === Recommended fields ===
name: Skill display name
version: 1.0.0
type: procedural
risk_level: low
status: enabled
tags:
  - tag1
  - tag2
metadata:
  author: your-name
  updated_at: '2026-03-03'

# === Optional fields ===
disable-model-invocation: true
requires:
  tools:
    - Bash
    - Read
  optional_tools:
    - Edit
---

# skill-id Skill

## L0: One-line Summary

Describe in one sentence what this Skill does.

## L1: Overview and Use Cases

### Capability

Detailed description of the Skill's core capability.

### Use Cases

- Scenario 1
- Scenario 2

### Core Value

- Value 1
- Value 2

## L2: Detailed Specification

### Concrete Steps

Describe the execution flow, API calls, and input/output formats stage by stage / step by step.

### Error Handling

| Error scenario | Handling |
| -------- | -------- |
| ...      | ...      |
```

#### Example: Create a Skill with the Write Tool

The following example shows how to create a global Skill with the Write tool:

```
Target path: ~/.desirecore/skills/daily-summary/SKILL.md
```

Content to write:

```markdown
---
name: Daily Summary
description: >-
  Aggregates today's conversation records and produces a structured daily work summary.
  Use when the user asks for a summary of today's work, generation of a daily report, or a recap of conversation content.
version: 1.0.0
type: procedural
risk_level: low
status: enabled
tags:
  - summary
  - daily
  - productivity
metadata:
  author: user
  updated_at: '2026-03-03'
---

# daily-summary Skill

## L0: One-line Summary

Aggregates today's conversation records and automatically produces a structured work summary.

## L1: Overview and Use Cases

### Capability

Extracts key information from conversation history, organizes it by project/topic, and produces a daily summary
covering completed items, to-dos, and important decisions.

### Use Cases

- The user asks for a summary at the end of a workday
- The user needs material for a daily or weekly report
- The user wants to recap a particular day's conversation and decisions

## L2: Detailed Specification

### Summary Structure

1. Items completed today
2. Items in progress
3. Important decisions and conclusions
4. Suggested to-dos for tomorrow
```

### 5. SKILL.md Format Reference

#### Frontmatter Field Table

| Field                       | Required     | Type     | Description                                               |
| -------------------------- | -------- | -------- | -------------------------------------------------- |
| `description`              | **Required** | string   | Skill purpose description; including a "Use when" trigger hint is recommended |
| `name`                     | Recommended     | string   | Skill display name                                       |
| `version`                  | Recommended     | string   | Semantic version (e.g. `1.0.0`)                           |
| `type`                     | Recommended     | enum     | `procedural` / `conversational` / `meta`           |
| `risk_level`               | Recommended     | enum     | `low` / `medium` / `high`                          |
| `status`                   | Recommended     | enum     | `enabled` / `disabled`                             |
| `tags`                     | Optional     | string[] | List of tags, used for search and categorization                           |
| `disable-model-invocation` | Optional     | boolean  | `true` = L0+L1 auto-injected into the system prompt; `false` = full L0+L1+L2 content injected; default `true` |
| `requires`                 | Optional     | object   | Dependency declaration: `tools`, `optional_tools`, `connections` |
| `metadata`                 | Optional     | object   | Meta information: `author`, `updated_at`                     |
| `market`                   | Optional     | object   | Market display metadata (only required for Skills published to the Market)             |

#### type Description

| Type             | Meaning                     | Examples                   |
| ---------------- | ------------------------ | ---------------------- |
| `procedural`     | Procedural; executed step by step       | Data analysis flow, approval flow |
| `conversational` | Conversational; completed through multi-turn dialogue | Requirements gathering, brainstorming     |
| `meta`           | Meta-Skill that manages other resources     | Creating Agents, managing Skills   |

#### Markdown Body Structure (L0 / L1 / L2)

| Tier | Content                                | Purpose               |
| ---- | ----------------------------------- | ------------------ |
| L0   | One-line summary                          | Quickly understand what the Skill does |
| L1   | Capability + Use Cases + Core Value      | Decide whether it applies       |
| L2   | Detailed specification: steps, APIs, formats, error handling | Concrete execution guide       |

### 6. Scope Notes

Skills exist at three scope levels, listed from highest priority to lowest:

| Priority | Scope     | Path                                     | Visibility           |
| ------ | ---------- | ---------------------------------------- | ------------------ |
| Highest   | Project | `.claude/skills/` (project root)           | All Agents in the current project |
| Medium     | Agent   | `~/.desirecore/agents/{agentId}/skills/` | Only that Agent         |
| Lowest    | Global  | `~/.desirecore/skills/`                  | All Agents         |

**Same-name override rule**: a Skill in a higher-priority scope overrides a same-named Skill in a lower-priority scope. For example, an Agent-scoped `data-analysis` Skill will shadow a global Skill of the same name.

### 7. Error Handling

| Error code | Scenario                          | Handling                               |
| ------ | ----------------------------- | -------------------------------------- |
| 400    | Missing required fields or invalid format        | Prompt the user to check the input and explain which field is problematic   |
| 400    | SKILL.md frontmatter validation failed | Show validation error details and guide the user to fix         |
| 404    | Skill does not exist                    | Note the Skill ID may be misspelled, list available Skills |
| 404    | No SKILL.md in the Git repo         | Note the repository's format does not match the Skill spec             |
| 409    | Skill already exists (write conflict)        | Suggest using PUT to update instead of POST to create        |
| 413    | Remote file exceeds 20MB             | Note the file is too large; suggest trimming the content         |
| 504    | URL fetch timeout                  | Note the network timed out; suggest checking the URL or retrying later  |
| 500    | Server internal error                | Tell the user to retry later                       |

### 8. Permission Notes

- It is recommended to use the `Bash` tool to call the Agent Service HTTP API via curl
- The API base address is already injected into the system prompt's "Local API" section; you can reference it directly
- For import and create operations, show the user a preview first and proceed only after confirmation
- Deletions require explicit user confirmation
- When authoring Skills via AgentFS, simply use the Write tool to create the file

### Background Knowledge

> AgentFS repository structure, troubleshooting tips, and protected paths are detailed in `_agentfs-background.md` and `_protected-paths.yaml`.

### Dependencies

- Agent Service HTTP API (Skills route group)
- The local API address declaration in the system prompt
- Write / Edit tools (for the AgentFS direct-authoring scenario)
