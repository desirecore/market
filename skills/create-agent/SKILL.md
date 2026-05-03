---
name: create-agent
description: >-
  通过多轮对话收集需求，调用 HTTP API 创建新的 AgentFS v2 智能体，支持自定义 persona 和 principles。Use when
  用户要求创建新智能体、培养某领域助手、或快速基于模板生成可治理 Agent。
version: 2.4.2
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
  updated_at: '2026-02-28'
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
        通过多轮对话收集需求，调用 HTTP API 创建新的 AgentFS v2 智能体，支持自定义 persona 和 principles。Use when 用户要求创建新智能体、培养某领域助手、或快速基于模板生成可治理 Agent。
      body: ./SKILL.zh-CN.md
      source_hash: sha256:cf21692224334fce
      translated_by: human
    en-US:
      name: Create Agent
      short_desc: Collect requirements through natural-language conversation and create a specialized digital Agent in one step
      description: >-
        Collect requirements through multi-turn conversation and call the HTTP API to create a new AgentFS v2 Agent, with customizable persona and principles. Use when the user asks to create a new Agent, raise a domain assistant, or quickly produce a governable Agent from a template.
      body: ./SKILL.md
      source_hash: sha256:cf21692224334fce
      translated_by: ai:claude-opus-4-7
      translated_at: '2026-05-03'
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
---

# create-agent skill

## L0: One-Sentence Summary

Collect requirements through natural-language conversation and call the HTTP API to create a specialized digital Agent.

## L1: Overview and Use Cases

### Capability Description

create-agent is a **Meta-Skill** that gives DesireCore the ability to create other Agents. It collects user requirements through multi-turn conversation, generates persona and principles content, and calls `POST /api/agents` to complete the creation.

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
│   回执生成    │ ←── │   API 创建   │ ←── │   用户确认    │
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

### Stage 5: Call API to Create

**API endpoint**: `POST /api/agents`

**Request body** (structured format):

```json
{
  "name": "法律顾问小助手",
  "description": "专注于合同审查和法律风险评估的数字智能体",
  "persona": {
    "L0": "你是法律顾问小助手，专注于合同审查和法律风险评估的数字智能体。",
    "L1": {
      "role": "专注于合同审查和法律风险评估的数字法律顾问",
      "personality": ["专业", "严谨", "审慎"],
      "communication_style": "准确使用法律术语，同时提供通俗解释"
    }
  },
  "principles": {
    "L0": "以用户利益为最高优先级，不替代正式法律意见。",
    "L1": {
      "must_do": ["准确引用法律条文", "标注不确定性", "建议咨询专业律师"],
      "must_not": ["提供诉讼代理", "替代正式法律意见", "泄露用户法律咨询内容"],
      "priority": "用户安全 > 准确性 > 效率"
    }
  }
}
```

**Minimal create** (only `name`; the rest is auto-generated):

```json
{ "name": "我的助手" }
```

**Basic create** (`name` + `description`; `description` auto-fills persona L0):

```json
{ "name": "法律顾问", "description": "专注合同审查" }
```

Any unprovided fields are auto-filled with sensible defaults by the system. `persona` and `principles` also accept raw markdown strings (backward compatible).

**Optional**: To specify a slug ID, generate a sensible kebab-case slug from `name` (e.g. "Legal Advisor" → "legal-advisor") and include `"id": "<slug>"` in the request body. If not specified, the system auto-generates one from `name`.

**Successful response** (`201 Created`):

```json
{
  "success": true,
  "agentId": "fa-lv-gu-wen-xiao-zhu-shou",
  "agent": {
    "id": "fa-lv-gu-wen-xiao-zhu-shou",
    "name": "法律顾问小助手",
    "description": "专注于合同审查和法律风险评估的数字智能体",
    "skillsCount": 0,
    "toolsCount": 0,
    "status": "offline"
  }
}
```

The `agent` field in the response contains the full info of the newly created Agent and can be used directly in the receipt.

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

| Error Code | Scenario                              | Handling                          |
| ---------- | ------------------------------------- | --------------------------------- |
| 400        | Missing `name` or invalid ID format   | Ask user to check input           |
| 409        | Agent ID already exists               | Suggest using another name        |
| 500        | Internal server error                 | Ask user to try again later       |

### Permission Requirements

- Prefer accessing the Agent Service HTTP API via the `Bash` tool with curl
- The API base URL is already injected into the "Local API" section of the system prompt; reference it directly
- Creation requires user confirmation

### Dependencies

- Agent Service HTTP API (`POST /api/agents`)
- The local API URL declaration in the system prompt
