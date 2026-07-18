---
name: create-agent
description: >-
  通过多轮对话收集需求，调用 ManageAgent 内置工具创建新的 AgentFS v2 智能体，支持自定义 persona 和 principles。Use when 用户要求创建新智能体、培养某领域助手、或快速基于模板生成可治理 Agent。
version: 2.5.0
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
  updated_at: '2026-07-18'
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
      source_hash: sha256:43425a25973ca933
      translated_by: human
    en-US:
      name: Create Agent
      short_desc: Collect requirements through natural-language conversation and create a specialized digital Agent in one step
      description: >-
        Collect requirements through multi-turn conversation and call the ManageAgent builtin tool to create a new AgentFS v2 Agent, with customizable persona and principles. Use when the user asks to create a new Agent, raise a domain assistant, or quickly produce a governable Agent from a template.
      body: ./SKILL.md
      source_hash: sha256:43425a25973ca933
      translated_by: ai:claude-fable-5
      translated_at: '2026-07-18'
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

## L1: Overview and Use Cases

### Capability Description

create-agent is a **Meta-Skill** that gives DesireCore the ability to create other Agents. It collects user requirements through multi-turn conversation, generates persona and principles content, and calls the `ManageAgent` builtin tool to complete the creation.

### Use Cases

- The user wants a digital assistant for a specialty domain (e.g. legal advisor, financial analyst)
- An enterprise needs to quickly deploy a customized business Agent
- A developer needs to quickly produce an Agent prototype from a template

### Core Value

- **Lower the barrier**: No programming knowledge required; create an Agent through conversation
- **Specialization**: Generate appropriate persona and principles based on a domain template
- **Governable**: The created repository conforms to the AgentFS v2 spec and supports version management

## L2: Detailed Specification

### Conversation Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   意图识别    │ ──→ │   需求收集    │ ──→ │   内容生成    │
└──────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ↓
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   回执生成    │ ←── │   工具创建   │ ←── │   用户确认    │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Stage 1: Intent Recognition

**Trigger conditions** (any one is sufficient):

- The user explicitly says "create an Agent" or "build me an assistant"
- The user describes needing professional help in some domain that the current Agent doesn't have
- The user asks "can you help me grow a..."

**Output**: Confirm the user's create intent and proceed to requirement collection.

### Stage 2: Requirement Collection

**Required information**:

| Field          | Description    | Example Probing Question                       |
| -------------- | -------------- | ---------------------------------------------- |
| `name`         | Agent name     | "What name would you like to give this Agent?" |
| `role`         | Core duty      | "What's its main responsibility?"              |
| `target_users` | Target users   | "Who will use this Agent?"                     |
| `domain`       | Specialty area | "What expertise does it need?"                 |

**Optional information**:

| Field        | Description           | Default                          |
| ------------ | --------------------- | -------------------------------- |
| `style`      | Communication style   | Determined by domain template    |
| `boundaries` | Off-limits / red lines| Determined by domain template    |
| `language`   | Primary language      | Chinese                          |

**Collection strategy**:

- Prefer to infer information from the user's natural description
- Only probe for required fields the user hasn't mentioned
- Ask at most 2 follow-up questions per turn

### Stage 3: Content Generation

Based on the collected requirements, assemble structured persona and principles data. **Do not output raw markdown**; instead, organize by field and present to the user.

**Persona fields** (all fields optional; missing ones are auto-filled by the system):

| Layer | Field                 | Description                                                  |
| ----- | --------------------- | ------------------------------------------------------------ |
| L0    | —                     | One-sentence core identity                                   |
| L1    | `role`                | Role positioning                                             |
| L1    | `personality`         | Personality trait tags                                       |
| L1    | `communication_style` | Communication style                                          |
| L2    | —                     | Specialty domain, core values, decision preferences (free-form) |

**Principles fields** (all also optional):

| Layer | Field      | Description                                  |
| ----- | ---------- | -------------------------------------------- |
| L0    | —          | One-sentence top-level principle             |
| L1    | `must_do`  | Things the Agent must do                     |
| L1    | `must_not` | Things the Agent must never do (safety red lines) |
| L1    | `priority` | Priority ordering                            |
| L2    | —          | Governance principles, escalation rules (free-form) |

**Domain matching reference**:

| Domain Keywords                  | Recommended personality          | Default must_not                                |
| -------------------------------- | -------------------------------- | ----------------------------------------------- |
| Legal, contract, legal affairs   | Professional, rigorous, prudent  | No litigation representation; not a substitute for formal legal advice |
| Finance, accounting, investment  | Precise, analytical, conservative | No investment advice; do not handle real transactions |
| Code, development, architecture  | Logical, pragmatic, direct       | No direct production access; do not store credentials |
| General / other                  | Friendly, helpful                | Standard safety norms                           |

### Stage 4: User Confirmation

When showing the preview to the user, present each field in natural language / table form. **Do not show raw markdown source**:

> About to create Agent:
>
> **Name**: Legal Advisor Assistant
> **Description**: A digital Agent focused on contract review and legal risk assessment
>
> ---
>
> **Persona**
>
> | Field                 | Content                                                                  |
> | --------------------- | ------------------------------------------------------------------------ |
> | Core identity         | You are Legal Advisor Assistant, focused on contract review and legal risk assessment |
> | Role positioning      | A digital legal advisor focused on contract review and legal risk assessment |
> | Personality           | Professional, rigorous, prudent                                          |
> | Communication style   | Use legal terminology accurately while also providing plain-language explanations |
>
> **Principles**
>
> | Field             | Content                                                              |
> | ----------------- | -------------------------------------------------------------------- |
> | Top principle     | User interest is the highest priority; not a substitute for formal legal advice |
> | Must do           | Cite statutes accurately, mark uncertainty, recommend consulting a professional lawyer |
> | Must not          | Provide litigation representation, substitute for formal legal advice, leak user consultations |
> | Priority          | User safety > Accuracy > Efficiency                                  |
>
> ---
>
> Confirm creation? (Confirm / Modify / Cancel)

**"Modify" branch handling**:

When the user chooses "Modify":

1. Ask the user which field to modify (e.g. "Which one do you want to modify?")
2. The user identifies the field to modify (e.g. "change personality to something more lively")
3. The Agent re-collects content for that field
4. Update the corresponding field in the preview
5. Show the full preview again → re-enter the confirmation flow

### Stage 5: Create via ManageAgent

**Tool call** (structured format):

```
ManageAgent({
  "action": "create",
  "name": "Legal Advisor Assistant",
  "description": "A digital Agent focused on contract review and legal risk assessment",
  "persona": {
    "L0": "You are Legal Advisor Assistant, a digital Agent focused on contract review and legal risk assessment.",
    "L1": {
      "role": "A digital legal advisor focused on contract review and legal risk assessment",
      "personality": ["Professional", "Rigorous", "Prudent"],
      "communication_style": "Use legal terminology accurately while also providing plain-language explanations"
    }
  },
  "principles": {
    "L0": "User interest is the highest priority; not a substitute for formal legal advice.",
    "L1": {
      "must_do": ["Cite statutes accurately", "Mark uncertainty", "Recommend consulting a professional lawyer"],
      "must_not": ["Provide litigation representation", "Substitute for formal legal advice", "Leak user consultations"],
      "priority": "User safety > Accuracy > Efficiency"
    }
  }
})
```

**Minimal create** (only `name`; the rest is auto-generated):

```
ManageAgent({ "action": "create", "name": "My Assistant" })
```

**Basic create** (`name` + `description`; `description` auto-fills persona L0):

```
ManageAgent({ "action": "create", "name": "Legal Advisor", "description": "Focused on contract review" })
```

Any unprovided fields are auto-filled with sensible defaults by the system. `persona` and `principles` also accept raw markdown strings (backward compatible).

**Optional parameters**:

- `id`: specify a kebab-case slug ID (e.g. "Legal Advisor" → "legal-advisor"). If not specified, the system auto-generates one from `name`. Note that `core` / `desirecore` are reserved core-agent identifiers and cannot be used (including when the slug auto-generated from `name` collides with them).
- `config`: an agent.json config delta. Only the `llm` field is allowed (model, temperature, etc.); sensitive fields such as `mcp_servers` / `tool_permissions` are rejected and must be adjusted via the settings UI after creation.

**Successful result**:

> Agent "Legal Advisor Assistant" created (ID: legal-advisor-assistant), registered and ready. It can be used directly with ManageTeam or Delegate.

The new Agent is registered online immediately after creation—no waiting or refresh needed; the returned ID can be used directly in subsequent ManageTeam / Delegate calls.

### Stage 6: Receipt Generation

**Receipt report**:

After successful creation, present the receipt in a user-friendly way (do not expose internal paths or technical details):

> Agent "Legal Advisor Assistant" has been created!
>
> **Next steps**:
>
> - Start a conversation right away
> - Add skills to make it more powerful
> - Adjust its personality or behavior rules

### Background Knowledge

> AgentFS repository structure, troubleshooting points, and protected paths are detailed in `_agentfs-background.md` and `_protected-paths.yaml`.

### Error Handling

| Error Scenario                              | Handling                                    |
| ------------------------------------------- | ------------------------------------------- |
| Missing `name` or invalid ID format         | Ask user to check input                     |
| Agent ID already exists                     | Suggest another name or an explicit `id`    |
| ID hits a reserved core-agent identifier    | Change the name or provide another `id`     |
| `config` contains non-whitelisted fields    | Retry with only the `llm` field             |

### Permission Requirements

- Always create via the `ManageAgent` builtin tool. **Never** call the local HTTP API, curl, or write AgentFS directories directly
- The `create` action is exempt from system approval, but this skill's conversation flow still requires showing the preview and getting user confirmation first (Stage 4)

### Dependencies

- `ManageAgent` builtin tool (client ≥ 10.0.90)
