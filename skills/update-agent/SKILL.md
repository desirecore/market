---
name: update-agent
description: >-
  安全更新现有智能体的配置、人格、原则、技能与记忆，输出可审阅 diff 并在确认后应用与提交。Use when 用户要求修改 Agent
  行为、安装/卸载技能、调整配置、回滚变更或修订规则。
version: 3.1.2
type: meta
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - agent
  - update
  - meta
metadata:
  author: desirecore
  updated_at: '2026-07-19'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 更新智能体
      short_desc: 安全更新智能体配置、人格、规则与技能，支持 diff 预览与版本回滚
      description: >-
        安全更新现有智能体的配置、人格、原则、技能与记忆，输出可审阅 diff 并在确认后应用与提交。Use when 用户要求修改 Agent 行为、安装/卸载技能、调整配置、回滚变更或修订规则。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:ceab26ea93a41898
      translated_by: human
    en-US:
      name: Update Agent
      short_desc: Safely update Agent config, persona, principles, and skills, with diff preview and version rollback
      description: >-
        Safely update an existing Agent's config, persona, principles, skills, and memory, producing reviewable diffs that are applied and committed only after confirmation. Use when the user asks to modify Agent behavior, install/uninstall skills, adjust config, roll back changes, or revise rules.
      body: ./SKILL.md
      source_hash: sha256:ceab26ea93a41898
      translated_by: ai:claude-fable-5
      translated_at: '2026-07-19'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="ua-a" x1="2" y1="7" x2="14"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#AF52DE"/><stop
    offset="1" stop-color="#007AFF"/></linearGradient></defs><circle cx="9"
    cy="7" r="4" fill="url(#ua-a)" fill-opacity="0.15" stroke="url(#ua-a)"
    stroke-width="1.5"/><path d="M10 15H6a4 4 0 0 0-4 4v2" fill="url(#ua-a)"
    fill-opacity="0.1" stroke="url(#ua-a)" stroke-width="1.5"/><circle cx="18"
    cy="15" r="3" fill="#007AFF" fill-opacity="0.12" stroke="#007AFF"
    stroke-width="1.3"/><path d="m14.3
    16.53.92-.38m.01-2.3-.92-.38m1.5-1.24-.38-.92m0
    5.54-.38.92m2.3.01.38-.92m.3-4.84-.38-.92m1.24 1.5.92-.38m0 2.3.92.38"
    stroke="#AF52DE" stroke-width="1.3" stroke-linecap="round"/></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.90
---

# update-agent skill

## L0: One-Sentence Summary

Safely modify an Agent's configuration, persona, rules, and skills through natural-language conversation.

## L1: Overview

Meta-skill: recognize the edit intent → generate a reviewable diff → user confirmation → apply (structured fields via ManageAgent, free-form files via Read/Write) → receipt, with version rollback. Its value is what the tool can't give: diff preview confirmation, two-path orchestration, rollback; structured fields go through ManageAgent's whitelist + schema validation so invalid config never lands.

## L2: Detailed Spec

### Update Types and the Two Paths

Structured fields always go through `ManageAgent(action='update')` (whitelist + validation + merge semantics); free-form files (memory/skills/tools) are edited directly with Read/Write:

| User intent | Means | Target (risk) |
| --- | --- | --- |
| Rename (display name) | `ManageAgent(update, name=...)` | agent.json (med) |
| Change description | `ManageAgent(update, description=...)` | agent.json (low) |
| LLM config (model/temperature) | `ManageAgent(update, config={llm:{...}})` | agent.json (med) |
| Personality/style | `ManageAgent(update, persona=... or markdown)` | persona.md (med) |
| Behavior rules | `ManageAgent(update, principles=... or markdown)` | principles.md (high) |
| Install/uninstall skill | Read/Write | `skills/` (low/med) |
| Add memory | Read/Write | `memory/` (low) |
| Change tool config | Read/Write | `tools/` (high, watch protected paths) |

Flow: intent recognition → change analysis → diff generation → user confirmation → apply → receipt.

### Stage 1: Intent Recognition

Trigger (any): user says "modify/update/adjust your …", "from now on you should… / remember this rule…", "install/uninstall this skill…", or describes dissatisfaction with current behavior and wants change. Identify the update type and target scope.

### Stage 2: Change Analysis

Assess impact (which files/behaviors), dependencies, and conflicts, and set a risk level → matching confirmation strength:

- Low (non-core, e.g. memory entries): simple confirmation
- Medium (persona / ordinary principles): show diff, then confirm
- High (core principles / tool permissions): detailed explanation + diff + confirm
- Protected (touches a protected path): block, requires owner permission

### Stage 3: Diff Generation

Generate a before/after diff for the user (show only the actual change), e.g.:

```diff
# persona.md → ## Communication style
- friendly, easygoing, light humor
+ professional, rigorous, measured humor
```

### Stage 4: User Confirmation

Show the diff preview (affected file, risk level, impact note + diff) and ask the user to confirm "Apply / Cancel / Modify"; "Modify" enters fine-tuning then re-confirms. (The tool layer also enforces confirmation for updating other/core agents; see Stage 5.)

### Stage 5: Apply Changes

Do not call the HTTP API (unreachable under instance auth), do not operate git directly (the backend auto-commits). Split by target into two paths:

**Path A · Structured fields → ManageAgent (mandatory; never Write `agent.json` / `persona.md` / `principles.md` directly)**

Fields and constraints: `name` (1–50 chars), `description` (≤200), `config.llm` (shallow-merge delta, **config allows llm only**), `persona` / `principles` (structured object `{L0, L1:{...}, L2}` or markdown string). Calls:

```
ManageAgent(action='update', id='<agent-id>', name='New Name')
ManageAgent(action='update', id='<agent-id>', persona={ L1: { personality: ["professional","rigorous"] } })
ManageAgent(action='update', id='<agent-id>', principles='…full markdown…')
```

**Merge semantics**: structured persona/principles are **field-level merges** (omitted fields keep their original values — passing only `L1.personality` won't clear L0/role); a markdown string is a **full replacement** (whole-file rewrite); `config.llm` is a **shallow-merge delta**. The merged result is validated against the whole schema; invalid config never lands.

Key points:

- **Read before write**: first `ManageAgent(action='get', id)` to fetch current values, for diff generation and field-name checking. Structured field names are fixed: persona's `L1.role` / `personality` (string array) / `communication_style`; principles' `L1.must_do` / `must_not` (string arrays) / `priority`; plus top-level `L0` / `L2`.
- **Confirmation and boundaries**: updating self skips the extra confirmation; updating another agent triggers user confirmation (on top of this skill's diff confirmation); the core agent (`desirecore` / `core`) is refused.
- **config whitelist**: `config` accepts only `llm`; `mcp_servers` / `tool_permissions` / `version` / `id` etc. are rejected with the field named — such runtime config does not go through ManageAgent; tell the user it currently needs the corresponding mechanism.
- **Partial write failure**: the tool reports exactly which fields landed / which failed; retry only the failed fields, don't resend everything.
- **Rename in one call**: to change the display name, call `ManageAgent(action='update', id, name='Y')` directly (writes agent.json and refreshes the list); if the persona doc title should match, append a persona update in the same turn. **Never claim a rename happened without actually calling ManageAgent.**

**Path B · Free-form files → Read/Write** (`memory/` / `skills/` / `tools/`, root `${DESIRECORE_ROOT}/agents/<agentId>/`): Read current values, then Write/Edit, re-read after writing to confirm. Before editing, check `_protected-paths.yaml`; touching a protected path should be blocked with an owner-permission notice. After writing, the backend file watcher auto-commits — no manual git.

### Stage 6: Receipt

Present the change summary in a user-friendly way (no internal paths / technical details), and note the user can say "undo the last change" to roll back anytime.

### Version Rollback

Trigger: user says "undo / roll back / restore the previous settings". Flow:

1. In the Agent directory, `git log --oneline -10` for history and `git show <commit>:<file>` for the target version content; show it to the user to confirm.
2. After confirmation, write back by type: structured fields (persona/principles, agent.json name/description/llm) → `ManageAgent(action='update', ...)` (persona/principles as a markdown string, **full replacement** with the historical content); free-form files (memory/skills) → Write directly.
3. Show the diff to confirm the rollback.

(git is only for **reading** history; write-back always goes through the two paths above — never rewrite working-tree files with git commands.)

### Background and Error Handling

- AgentFS structure and protected paths: see `_agentfs-background.md` and `_protected-paths.yaml`.
- On tool errors: non-whitelisted config field / schema validation failure / core-agent refusal → fix per the tool's hint or inform the user; protected path → block with an owner-permission notice; rollback version not found → list available versions and ask the user to reselect.
