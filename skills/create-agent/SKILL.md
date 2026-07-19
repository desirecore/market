---
name: create-agent
description: >-
  通过多轮对话收集需求，调用 ManageAgent 内置工具创建新的 AgentFS v2 智能体，支持自定义 persona 和 principles。Use when 用户要求创建新智能体、培养某领域助手、或快速基于模板生成可治理 Agent。
version: 2.5.1
type: meta
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - agent
  - creation
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
      name: 创建智能体
      short_desc: 通过自然语言对话收集需求，一键创建专业化数字智能体
      description: >-
        通过多轮对话收集需求，调用 ManageAgent 内置工具创建新的 AgentFS v2 智能体，支持自定义 persona 和 principles。Use when 用户要求创建新智能体、培养某领域助手、或快速基于模板生成可治理 Agent。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:a119427bed3bcd72
      translated_by: human
    en-US:
      name: Create Agent
      short_desc: Collect requirements through natural-language conversation and create a specialized digital Agent in one step
      description: >-
        Collect requirements through multi-turn conversation and call the ManageAgent builtin tool to create a new AgentFS v2 Agent, with customizable persona and principles. Use when the user asks to create a new Agent, raise a domain assistant, or quickly produce a governable Agent from a template.
      body: ./SKILL.md
      source_hash: sha256:a119427bed3bcd72
      translated_by: ai:claude-fable-5
      translated_at: '2026-07-19'
market:
  icon: >-
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0
    24 24" fill="none"><defs><linearGradient id="ca-a" x1="2" y1="7" x2="16"
    y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#34C759"/><stop
    offset="1" stop-color="#007AFF"/></linearGradient></defs><circle cx="9"
    cy="7" r="4" fill="url(#ca-a)" fill-opacity="0.15" stroke="url(#ca-a)"
    stroke-width="1.5"/><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"
    fill="url(#ca-a)" fill-opacity="0.1" stroke="url(#ca-a)"
    stroke-width="1.5"/><circle cx="19" cy="11" r="4" fill="#34C759"
    fill-opacity="0.15"/><line x1="19" y1="8.5" x2="19" y2="13.5"
    stroke="#34C759" stroke-width="2" stroke-linecap="round"/><line x1="16.5"
    y1="11" x2="21.5" y2="11" stroke="#34C759" stroke-width="2"
    stroke-linecap="round"/></svg>
  category: productivity
  maintainer:
    name: DesireCore Official
    verified: true
  compatible_agents: []
  channel: latest
  required_client_version: 10.0.90
---

# create-agent skill

## L0: One-Sentence Summary

Collect requirements through natural-language conversation and call the ManageAgent builtin tool to create a specialized digital Agent.

## L1: Overview

Meta-skill: gather requirements over multi-turn conversation → generate persona/principles → land via `ManageAgent(action='create')`. Use it to raise a domain specialist for the user (legal advisor, financial analyst, etc.). Its value is what the tool can't give: domain-tailored persona/principles generation + a pre-create preview confirmation.

## L2: Detailed Spec

Flow: intent recognition → requirement gathering → content generation → user confirmation → creation → receipt.

### Stage 1: Intent Recognition

Trigger (any): user explicitly says "create an Agent / make me an assistant"; describes a domain-specific need the current Agent lacks; asks "can you raise a …". Confirm intent, then move to requirement gathering.

### Stage 2: Requirement Gathering

- Required: `name`, `role` (core responsibility), `target_users`, `domain` (specialty).
- Optional: `style` (communication tone), `boundaries` (red lines), `language` (default Chinese) — defaults derived from the domain template.
- Strategy: prefer inferring from the user's natural description; only ask for missing required fields; at most 2 questions per turn.

### Stage 3: Content Generation

Organize persona and principles as structured fields (do not emit raw markdown; present field-by-field). Leave uncollected fields empty for the system to fill with defaults:

- **persona**: L0 one-sentence core identity; L1 `role` / `personality` (array of trait tags) / `communication_style`; L2 specialty, values, decision preferences (free-form).
- **principles**: L0 one-sentence top principle; L1 `must_do` / `must_not` (safety red lines) / `priority`; L2 governance principles, escalation rules (free-form).

**Domain matching reference** (recommend personality and red lines by domain):

| Domain | Recommended personality | Default must_not |
| --- | --- | --- |
| Legal / contract | Professional, rigorous, prudent | No litigation representation; not a substitute for formal legal advice |
| Finance / accounting / investment | Precise, analytical, conservative | No investment advice; no real transactions |
| Code / development / architecture | Logical, pragmatic, direct | No direct production access; no credential storage |
| General / other | Friendly, helpful | Standard safety norms |

### Stage 4: User Confirmation

Present the preview in natural language / tables (name, description, persona, principles; **no raw markdown source**), e.g.:

> About to create "Legal Advisor Assistant" — focused on contract review and legal risk assessment.
> **Persona**: digital legal advisor; professional, rigorous, prudent; uses legal terms accurately with plain-language explanations.
> **Principles**: user interest first, not a substitute for formal legal advice; must — cite statutes / mark uncertainty / recommend consulting a lawyer; must not — litigation representation / leaking consultations; priority: user safety > accuracy > efficiency.
> Confirm creation? (Confirm / Modify / Cancel)

If the user picks "Modify": ask which field → re-collect that field → update the preview → show and confirm again.

### Stage 5: Create via ManageAgent

Structured call (persona/principles also accept markdown strings; unprovided fields are auto-filled):

```
ManageAgent({
  "action": "create",
  "name": "Legal Advisor Assistant",
  "description": "A digital Agent focused on contract review and legal risk assessment",
  "persona": { "L0": "…", "L1": { "role": "…", "personality": ["professional","rigorous","prudent"], "communication_style": "…" } },
  "principles": { "L0": "…", "L1": { "must_do": ["…"], "must_not": ["…"], "priority": "user safety > accuracy > efficiency" } }
})
```

- Minimal create needs only `{ "action": "create", "name": "My Assistant" }` (everything else auto-generated).
- Optional `id` (kebab-case slug; `core` / `desirecore` are reserved core identifiers and cannot be used, including when the slug auto-generated from `name` collides), `config.llm` (llm delta only; sensitive fields like mcp_servers are rejected and must be adjusted via the UI after creation).
- The Agent is registered and usable immediately; the returned ID works directly with ManageTeam / Delegate. If the tool errors (already exists / reserved identifier / non-whitelisted config field, etc.), explain the reason and retry after adjusting per the hint.

### Stage 6: Receipt

Present in a user-friendly way (no internal paths / technical details): confirm success and suggest next steps — start chatting, add skills, adjust persona or rules.

### Background and Constraints

- AgentFS structure, troubleshooting, and protected paths: see `_agentfs-background.md` and `_protected-paths.yaml`.
- Always create via `ManageAgent`; never use curl / HTTP or write AgentFS directories directly. Requires client ≥ 10.0.90.
